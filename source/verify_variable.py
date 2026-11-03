"""Independently check a full wght/ital companion against its original statics.

Run with fontTools 4.68.0, uharfbuzz 0.57.0, freetype-py, numpy, scipy==1.16.3, skia-pathops==0.9.2 and brotli:
    python verify_variable.py --masters DIR --font VF.ttf --woff2 VF.woff2 --report proof.json

No construction helpers or generated build report are used as an oracle. All fourteen
endpoints check every source glyph's metrics/bounds/raster and every encoded character's
shaping, plus each available feature on a mixed corpus. Intermediate checks cover every original glyph, including unencoded feature targets,
with native raster topology and adjacent-static ink-envelope probes. Suspect images are saved.
They do not prove subjective quality or every possible intermediate string. Raster deltas
and <=1-unit format-rounding differences are recorded, never rounded out of the report.
MATH values are evaluated through GDEF VariationIndex data, not fontTools' static instancer.
See https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview and
https://learn.microsoft.com/en-us/typography/opentype/spec/math .
"""
from __future__ import annotations

import argparse
import ctypes
from collections import Counter
import hashlib
from functools import lru_cache
import io
import itertools
import importlib.metadata
import json
import math
import re
import struct
import zlib
from pathlib import Path
import sys

import numpy as np
from scipy import ndimage
import uharfbuzz as hb
import freetype
import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment
from fontTools.ttLib import TTFont
from fontTools.misc.roundTools import otRound
from fontTools.varLib.models import normalizeLocation, piecewiseLinearMap
from fontTools.varLib.varStore import VarStoreInstancer
from fontTools.varLib.mvar import MVAR_ENTRIES

WEIGHTS = (300, 400, 500, 600, 700, 800, 900)
STYLES = ('Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black')
TEXTS = (
    'office affine waffle tt Th ct st th attention sigmoid sigmoids gradient descent 28x28',
    'AVATAR THE The 0123456789 1st 2nd 11th 101st 50% 3−2 3×4 3±1 (3/4) ½ <= -> ...',
    'a\u0301 a\u0308 a\u0308\u0301 L\u0307 l\u0307 Å é Ā αβγξζς ΐΰ΅ θϑ φϕ πϖ ρϱ εϵ',
    'a\u00adb a\u200bb a\u2060b a\u200db a\u200cb',
    'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ абвгдеёжзийклмнопрстуфхцчшщъыьэюя аӑӓ',
)



def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tags(font, table):
    if table not in font or font[table].table.FeatureList is None:
        return set()
    return {r.FeatureTag for r in font[table].table.FeatureList.FeatureRecord}


@lru_cache(maxsize=64)
def shaping_font(data, location):
    font = hb.Font(hb.Face(data))
    if location:
        font.set_variations(dict(location))
    return font


def shape(font, text, features, location=None, preserve=False, language=None):
    f = shaping_font(font, tuple(sorted(location.items())) if location else ())
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    if language is not None:
        if not valid_language_tag(language):
            raise ValueError('language must be a nonempty ASCII hyphen-separated language tag')
        b.language = language
    if preserve:
        b.flags = hb.BufferFlags.PRESERVE_DEFAULT_IGNORABLES
    hb.shape(f, b, features)
    return [(i.codepoint, i.cluster, p.x_advance, p.y_advance, p.x_offset, p.y_offset)
            for i, p in zip(b.glyph_infos, b.glyph_positions)]


def native_glyph(face, glyph_id, ppem):
    """Use the real font loader, including composite metrics and gvar/HVAR."""
    face.load_glyph(glyph_id, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
    metric = (face.glyph.metrics.horiAdvance, face.glyph.metrics.horiBearingX)
    outline = face.glyph.outline
    box = outline.get_bbox() if outline.n_points else None
    box = None if box is None else (box.xMin, box.yMin, box.xMax, box.yMax)
    face.set_pixel_sizes(0, ppem)
    face.load_glyph(glyph_id, freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_NO_BITMAP)
    face.glyph.render(freetype.FT_RENDER_MODE_NORMAL)
    bitmap = face.glyph.bitmap
    array = np.array(bitmap.buffer, dtype=np.uint8).reshape(bitmap.rows, bitmap.pitch)[:, :bitmap.width].astype(float) / 255
    return metric, box, (array, face.glyph.bitmap_left, face.glyph.bitmap_top)


def raster_perimeter(array):
    # Native allocation boxes need not contain white padding. Count the outer
    # ink/background boundary too, not only differences within the array.
    padded = np.pad(array, 1)
    return float(np.abs(np.diff(padded, axis=0)).sum() + np.abs(np.diff(padded, axis=1)).sum())


def align_native(a, b):
    return align_native_many((a, b))


def align_native_many(records):
    left = min(x for arr, x, y in records); top = max(y for arr, x, y in records)
    right = max(x + arr.shape[1] for arr, x, y in records)
    bottom = min(y - arr.shape[0] for arr, x, y in records)
    result = []
    for arr, x, y in records:
        canvas = np.zeros((max(1, top-bottom), max(1, right-left)))
        canvas[top-y:top-y+arr.shape[0], x-left:x-left+arr.shape[1]] = arr
        result.append(canvas)
    return result


def dilate(mask):
    padded = np.pad(mask, 1)
    return np.logical_or.reduce([padded[y:y+mask.shape[0], x:x+mask.shape[1]] for y in range(3) for x in range(3)])


def topology(array):
    """Four-connected significant ink components and enclosed white regions."""
    black = np.pad(array > .5, 1)
    result = []
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)
    for is_ink, mask in ((True, black), (False, ~black)):
        labels, _ = ndimage.label(mask, structure=cross)
        sizes = np.bincount(labels.ravel())
        keep = set(np.flatnonzero(sizes >= 4)) - {0}
        if not is_ink:
            keep -= set(np.unique(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))))
        result.append(len(keep))
    return tuple(result)


def _path_curve_segments(path):
    pen = RecordingPen()
    path.draw(pen)
    segments = []
    current = start = None
    for command, args in pen.value:
        if command == 'moveTo':
            current = start = args[0]
        elif command == 'lineTo':
            segments.append((current, args[0]))
            current = args[0]
        elif command == 'qCurveTo':
            if args[-1] is None:
                if len(args) < 3:
                    raise ValueError('Degenerate all-off-curve contour')
                implied = tuple((a+b)/2 for a, b in zip(args[0], args[-2]))
                current = start = implied
                args = args[:-1] + (implied,)
            for control, end in decomposeQuadraticSegment(args):
                segments.append((current, control, end))
                current = end
        elif command == 'curveTo' and len(args) == 3:
            segments.append((current,) + args)
            current = args[-1]
        elif command == 'closePath':
            if current != start:
                segments.append((current, start))
            current = start
        else:
            raise ValueError(f'Unsupported filled contour command: {command}')
    return segments


def _curve_boundaries_separated(a, b, epsilon=1e-6):
    """Certify separation using Bezier convex hulls; uncertainty never passes."""
    pending = [(a, b, 0)]
    visits = 0
    while pending:
        a, b, depth = pending.pop()
        visits += 1
        ax, ay = zip(*a)
        bx, by = zip(*b)
        if (max(ax) < min(bx)-epsilon or max(bx) < min(ax)-epsilon or
                max(ay) < min(by)-epsilon or max(by) < min(ay)-epsilon):
            continue
        if depth >= 24 or visits >= 4096:
            return False
        def split(points):
            left, right = [points[0]], [points[-1]]
            while len(points) > 1:
                points = tuple(((x[0]+y[0])/2, (x[1]+y[1])/2) for x, y in zip(points, points[1:]))
                left.append(points[0])
                right.append(points[-1])
            return tuple(left), tuple(reversed(right))
        if max(max(ax)-min(ax), max(ay)-min(ay)) >= max(max(bx)-min(bx), max(by)-min(by)):
            left, right = split(a)
            pending.extend(((left, b, depth+1), (right, b, depth+1)))
        else:
            left, right = split(b)
            pending.extend(((a, left, depth+1), (a, right, depth+1)))
    return True


def filled_vector_topology(font, name, location=None):
    """Topology of actual nonzero fill, with conservative boundary ambiguity.

    This is only corroboration for pixel-connectivity flags. It proves neither
    source-equivalent curvature nor spacing, ink envelopes, or aesthetic quality.
    """
    try:
        glyphs = font.getGlyphSet(location=location)
        raw = pathops.Path()
        glyphs[name].draw(raw.getPen(glyphSet=glyphs))
        filled = pathops.simplify(raw)
        contours = list(filled.contours)
        areas = [abs(p.area) for p in contours]
        if any(not math.isfinite(a) or a <= 1e-6 for a in areas):
            raise ValueError('Degenerate or numerically ambiguous filled contour')
        parents = [None] * len(contours)
        curves = [_path_curve_segments(p) for p in contours]
        for boundary in curves:
            vertices = [tuple(segment[0]) for segment in boundary]
            if len(vertices) != len(set(vertices)):
                raise ValueError('Self-touching filled contour boundary')
        for i, a in enumerate(contours):
            containers = []
            for j, b in enumerate(contours):
                if i == j:
                    continue
                outside = abs(pathops.op(a, b, pathops.PathOp.DIFFERENCE).area)
                if outside <= 1e-6:
                    if areas[j] <= areas[i] + 1e-6:
                        raise ValueError('Duplicate or unresolved contour containment')
                    containers.append(j)
            if containers:
                parents[i] = min(containers, key=lambda j: areas[j])
        for i, a in enumerate(curves):
            for j in range(i+1, len(curves)):
                if not all(_curve_boundaries_separated(x, y) for x in a for y in curves[j]):
                    raise ValueError('Touching or insufficiently separated contour boundaries')
        def depth(i):
            return 0 if parents[i] is None else 1 + depth(parents[i])
        def branch(i):
            return tuple(sorted(branch(j) for j, parent in enumerate(parents) if parent == i))
        depths = [depth(i) for i in range(len(contours))]
        structure = tuple(sorted(branch(i) for i, parent in enumerate(parents) if parent is None))
        return {'status': 'resolved', 'components': sum(d % 2 == 0 for d in depths),
                'holes': sum(d % 2 == 1 for d in depths), 'structure': structure,
                'filled_area': abs(filled.area), 'glyph': name, 'location': location,
                'units_per_em': font['head'].unitsPerEm,
                'contours': [{'area': area, 'parent': parent, 'depth': d, 'branch': branch(index), 'bounds': list(p.bounds)}
                             for index, (p, area, parent, d) in enumerate(zip(contours, areas, parents, depths))],
                'method': 'Nonzero Skia fill; Boolean contour containment and Bezier convex-hull separation.',
                'numerical_bounds': {'area_epsilon_font_units_squared': 1e-6, 'boundary_margin_font_units': 1e-6,
                                     'maximum_subdivision_depth': 24, 'maximum_visits_per_curve_pair': 4096}}
    except Exception as error:
        return {'status': 'ambiguous', 'reason': str(error), 'method': 'No raster-sensitive exemption on ambiguous geometry.'}


def corroborate_raster_topology(fonts, names, locations):
    vectors = [filled_vector_topology(f, n, loc) for f, n, loc in zip(fonts, names, locations)]
    resolved = all(v['status'] == 'resolved' for v in vectors)
    same = resolved and all((v['components'], v['holes'], v['structure']) ==
                            (vectors[0]['components'], vectors[0]['holes'], vectors[0]['structure']) for v in vectors[1:])
    # A tiny surviving vector hole can still be a real collapsed counter.
    # Require matched filled-contour areas inside the adjacent reference range;
    # uncertainty or nonmonotone area stays flagged rather than being waived.
    area_ranges = []
    if same:
        ordered = [sorted(v['contours'], key=lambda c: (c['depth'], c['branch'], c['area'])) for v in vectors]
        for index, triple in enumerate(zip(*ordered)):
            areas = [c['area'] for c in triple]
            within = min(areas[0], areas[2])-1e-6 <= areas[1] <= max(areas[0], areas[2])+1e-6
            area_ranges.append({'contour_rank': index, 'areas': areas, 'within_reference_range': within})
    area_stable = same and all(r['within_reference_range'] for r in area_ranges)
    return {'raster_sensitive': area_stable, 'matching_vector_structure': same,
            'vectors': vectors, 'contour_area_ranges': area_ranges, 'area_range_epsilon_font_units_squared': 1e-6,
            'limit': 'Only matching separated fill topology with reference-bracketed contour areas corroborates raster sensitivity. Other curve fidelity, geometry, envelope, endpoint and layout checks remain independent.'}


def save_probe_png(arrays, path):
    """Unresampled native source/lower, variable, source/upper ink on white."""
    height = max(a.shape[0] for a in arrays) + 8
    width = sum(a.shape[1] for a in arrays) + 4 * (len(arrays) + 1)
    canvas = np.full((height, width, 3), 255, dtype=np.uint8)
    x = 4
    for a in arrays:
        ink = np.round(255 - a[:, :, None] * (255 - np.array([51, 36, 27]))).astype(np.uint8)
        canvas[4:4+a.shape[0], x:x+a.shape[1]] = ink
        x += a.shape[1] + 4
    def chunk(tag, data):
        return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff)
    raw = b''.join(b'\0' + row.tobytes() for row in canvas)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def normalized(font, location):
    loc = normalizeLocation(location, {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font['fvar'].axes})
    if 'avar' in font:
        loc = {tag: piecewiseLinearMap(value, font['avar'].segments[tag]) for tag, value in loc.items()}
    return loc


def math_signature(font, names, location=None):
    """Logical per-glyph MATH data, resolving every MathValueRecord recursively."""
    if 'MATH' not in font:
        return None
    store = getattr(font['GDEF'].table, 'VarStore', None) if 'GDEF' in font else None
    inst = VarStoreInstancer(store, font['fvar'].axes, normalized(font, location)) if location and store else None

    def walk(value):
        if value is None or isinstance(value, (str, int, float, bool)):
            return names.get(value, value) if isinstance(value, str) else value
        if isinstance(value, (list, tuple)):
            return [walk(x) for x in value]
        if hasattr(value, 'Value') and hasattr(value, 'DeviceTable'):
            delta = 0
            device = value.DeviceTable
            if device is not None:
                if device.DeltaFormat != 0x8000 or inst is None:
                    raise ValueError('MATH has an unresolved non-VariationIndex device or missing GDEF store')
                delta = inst[(device.StartSize << 16) | device.EndSize]
            return float(value.Value + delta)
        return {k: walk(v) for k, v in vars(value).items() if not k.startswith('_')}

    def covered(obj, coverage_name, records_name):
        if obj is None:
            return {}
        cov = getattr(obj, coverage_name)
        records = getattr(obj, records_name)
        return {names[g]: walk(record) for g, record in zip(cov.glyphs, records) if g in names}

    t = font['MATH'].table
    info = t.MathGlyphInfo
    result = {'constants': walk(t.MathConstants), 'italics': {}, 'topAccent': {}, 'extended': [], 'kern': {}}
    if info is not None:
        result['italics'] = covered(info.MathItalicsCorrectionInfo, 'Coverage', 'ItalicsCorrection')
        result['topAccent'] = covered(info.MathTopAccentAttachment, 'TopAccentCoverage', 'TopAccentAttachment')
        if info.ExtendedShapeCoverage:
            result['extended'] = sorted(names[g] for g in info.ExtendedShapeCoverage.glyphs if g in names)
        result['kern'] = covered(info.MathKernInfo, 'MathKernCoverage', 'MathKernInfoRecords')
    v = t.MathVariants
    result['variants'] = None
    if v is not None:
        result['variants'] = {'MinConnectorOverlap': v.MinConnectorOverlap,
                              'vertical': covered(v, 'VertGlyphCoverage', 'VertGlyphConstruction') if v.VertGlyphCoverage else {},
                              'horizontal': covered(v, 'HorizGlyphCoverage', 'HorizGlyphConstruction') if v.HorizGlyphCoverage else {}}
    return result


def numeric_diff(a, b, path=''):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return [] if abs(a-b) <= 1e-6 else [(path, a, b)]
    if type(a) is not type(b):
        return [(path, a, b)]
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return [(path + '.keys', sorted(a), sorted(b))]
        return [d for k in a for d in numeric_diff(a[k], b[k], path+'.'+k)]
    if isinstance(a, list):
        if len(a) != len(b):
            return [(path+'.length', len(a), len(b))]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in numeric_diff(x, y, path+f'[{i}]')]
    return [] if a == b else [(path, a, b)]


def valid_language_tag(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*', value) is not None


def load_corpus(path, required=False):
    """Load input-only registered feature cases; no expected answers are accepted."""
    if path is None:
        if required:
            raise ValueError('--require-corpus needs a nonempty --corpus file')
        return []
    document = json.loads(path.read_text())
    if not isinstance(document, dict) or set(document) - {'cases', 'provenance'}:
        raise ValueError('Corpus must contain cases and optional provenance only')
    cases = document.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('Corpus cases must be a nonempty list')
    seen = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError('A corpus case must be an input-field object')
        unknown = set(case) - {'id', 'module', 'text', 'features', 'preserve_default_ignorables', 'language'}
        if unknown:
            raise ValueError(f'Unsupported corpus case fields: {sorted(unknown)}')
        if 'language' in case and not valid_language_tag(case['language']):
            raise ValueError('Corpus language must be a nonempty ASCII hyphen-separated language tag')
        if any(not isinstance(case.get(k), str) or not case[k] for k in ('id', 'module', 'text')):
            raise ValueError('Each corpus case needs nonempty id, module and text strings')
        identity = (case['module'], case['id'])
        if identity in seen:
            raise ValueError(f'Duplicate corpus case: {identity}')
        seen.add(identity)
        features = case.get('features')
        if not isinstance(features, dict) or any(not isinstance(k, str) or len(k) != 4 or not k.isascii() or not k.isalnum() or not isinstance(v, int) or not 0 <= v <= 65535 for k, v in features.items()):
            raise ValueError('Corpus features must map four-character ASCII tags to unsigned integers')
        if not isinstance(case.get('preserve_default_ignorables', False), bool):
            raise ValueError('preserve_default_ignorables must be boolean')
    return cases


class EarlyFailure(Exception):
    def __init__(self, kind, detail):
        self.kind, self.detail = kind, detail
        super().__init__(kind)


class Audit:
    def __init__(self, fail_fast=False):
        self.fail_fast = fail_fast
        self.failures = Counter()
        self.samples = []
        self.details = []
        self.rounding = Counter()
        self.rounding_samples = []

    def check(self, condition, kind, detail):
        if not condition:
            self.failures[kind] += 1
            self.details.append({'kind': kind, 'detail': detail})
            if sum(x['kind'] == kind for x in self.samples) < 10:
                self.samples.append({'kind': kind, 'detail': detail})
            if self.fail_fast:
                raise EarlyFailure(kind, detail)

    def metric(self, got, want, kind, detail):
        delta = abs(got-want)
        self.check(math.isfinite(got) and delta <= 1, kind, dict(detail, got=got, want=want, delta=delta))
        if 0 < delta <= 1:
            self.rounding[kind] += 1
            if len(self.rounding_samples) < 30:
                self.rounding_samples.append(dict(detail, kind=kind, got=got, want=want, delta=delta))


def serialized_outline_headers(font, audit):
    """Derive default glyf resource needs and extrema without recalculating tables.

    maxp is an allocation profile: undersized capacities fail, while safe spare
    capacity is reported. head/hhea extrema describe decoded default outlines,
    including off-curve control points, not exact painted-curve extrema or every
    nondefault instance. Hint VM resource counts need execution to prove generally.
    """
    order = font.getGlyphOrder()
    glyf = font['glyf']
    active = set()

    @lru_cache(None)
    def counts(name):
        if name in active:
            raise ValueError(f'Composite glyph cycle: {name}')
        active.add(name)
        glyph = glyf[name]
        if glyph.isComposite():
            children = [counts(c.glyphName) for c in glyph.components]
            result = (sum(x[0] for x in children), sum(x[1] for x in children),
                      1 + max((x[2] for x in children), default=0))
        else:
            points = len(glyph.coordinates) if glyph.numberOfContours else 0
            contours = len(glyph.endPtsOfContours) if glyph.numberOfContours else 0
            audit.check(contours == glyph.numberOfContours, 'glyf-contour-count',
                        {'glyph': name, 'declared': glyph.numberOfContours, 'decoded': contours})
            result = (points, contours, 0)
        active.remove(name)
        return result

    needed = dict(numGlyphs=len(order), maxPoints=0, maxContours=0,
                  maxCompositePoints=0, maxCompositeContours=0,
                  maxComponentElements=0, maxComponentDepth=0, maxSizeOfInstructions=0)
    witnesses = {}
    boxes = []
    horizontal = []
    for name in order:
        glyph = glyf[name]
        points, contours, depth = counts(name)
        values = {'maxCompositePoints' if glyph.isComposite() else 'maxPoints': points,
                  'maxCompositeContours' if glyph.isComposite() else 'maxContours': contours,
                  'maxComponentDepth': depth,
                  'maxComponentElements': len(glyph.components) if glyph.isComposite() else 0,
                  'maxSizeOfInstructions': len(glyph.program.getBytecode()) if hasattr(glyph, 'program') else 0}
        for field, value in values.items():
            if value > needed[field]:
                needed[field] = value
                witnesses[field] = name
        if points:
            coordinates, _, _ = glyph.getCoordinates(glyf, round=otRound)
            xs, ys = zip(*coordinates)
            box = tuple(otRound(x) for x in (min(xs), min(ys), max(xs), max(ys)))
            actual = tuple(getattr(glyph, field) for field in ('xMin', 'yMin', 'xMax', 'yMax'))
            audit.check(actual == box, 'glyf-default-bounds', {'glyph': name, 'stored': actual, 'derived': box})
            boxes.append(box)
            advance, lsb = font['hmtx'][name]
            horizontal.append((lsb, advance - lsb - (box[2]-box[0]), lsb + box[2]-box[0]))
    audit.check(font['maxp'].tableVersion == 0x10000, 'maxp-version', font['maxp'].tableVersion)
    declared = {field: getattr(font['maxp'], field) for field in needed}
    for field, value in needed.items():
        valid = declared[field] == value if field == 'numGlyphs' else declared[field] >= value
        audit.check(valid, 'maxp-capacity', {'field': field, 'stored': declared[field], 'required': value, 'witness': witnesses.get(field)})
    if boxes:
        derived_head = (min(b[0] for b in boxes), min(b[1] for b in boxes),
                        max(b[2] for b in boxes), max(b[3] for b in boxes))
        actual_head = tuple(getattr(font['head'], field) for field in ('xMin', 'yMin', 'xMax', 'yMax'))
        audit.check(actual_head == derived_head, 'head-default-bounds', {'stored': actual_head, 'derived': derived_head})
    else:
        derived_head = None
    derived_hhea = {'advanceWidthMax': max((font['hmtx'][g][0] for g in order), default=0)}
    if horizontal:
        derived_hhea.update(minLeftSideBearing=min(x[0] for x in horizontal),
                            minRightSideBearing=min(x[1] for x in horizontal),
                            xMaxExtent=max(x[2] for x in horizontal))
    for field, value in derived_hhea.items():
        audit.check(getattr(font['hhea'], field) == value, 'hhea-default-extrema',
                    {'field': field, 'stored': getattr(font['hhea'], field), 'derived': value})
    audit.check(1 <= font['hhea'].numberOfHMetrics <= len(order), 'hhea-metric-count', font['hhea'].numberOfHMetrics)
    hint_programs = {tag: len(font[tag].program.getBytecode()) if tag in font else 0 for tag in ('fpgm', 'prep')}
    return {'maxp_declared': declared, 'maxp_required': needed, 'maxp_witnesses': witnesses,
            'nonempty_default_glyphs': len(boxes), 'derived_head_bounds': derived_head,
            'derived_hhea': derived_hhea, 'hint_table_bytes': hint_programs,
            'limits': 'No hint VM execution or nondefault-instance global extrema claim; safe maxp over-allocation is reported, not rejected.'}


def native_runtime_provenance():
    """Identify the library actually loaded by the caller; never select a backend."""
    result = {'version': list(freetype.version()), 'binding_module': str(Path(freetype.__file__).resolve())}
    try:
        library = freetype.raw._lib
        result['loader_name'] = str(library._name)
        candidate = Path(str(library._name))
        if not candidate.is_file():
            class DlInfo(ctypes.Structure):
                _fields_ = [('filename', ctypes.c_char_p), ('base', ctypes.c_void_p),
                            ('symbol', ctypes.c_char_p), ('address', ctypes.c_void_p)]
            dladdr = ctypes.CDLL(None).dladdr
            dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(DlInfo)]
            dladdr.restype = ctypes.c_int
            info = DlInfo()
            if not dladdr(ctypes.cast(library.FT_Init_FreeType, ctypes.c_void_p), ctypes.byref(info)) or not info.filename:
                raise OSError('Loaded FreeType library path could not be resolved')
            candidate = Path(info.filename.decode())
        candidate = candidate.resolve(strict=True)
        result.update(path=str(candidate), sha256=digest(candidate))
    except Exception as error:
        result.update(path=None, sha256=None, resolution_error=f'{type(error).__name__}: {error}')
    return result


def infer_shared_gid0(static_paths, vf_bytes, source_order, variable_order, source_cmaps):
    """Infer an actually shared structural missing-glyph slot, not a glyph-name alias."""
    occupied = set().union(*(set(cmap) for cmap in source_cmaps))
    missing = next(cp for cp in range(0x10FFFD, 0xFFFFF, -1) if cp not in occupied)
    evidence = []
    for weight, ital, static_path in static_paths:
        source_bytes = static_path.read_bytes()
        for preserve in (False, True):
            original = shape(source_bytes, chr(missing), {}, preserve=preserve)
            variable = shape(vf_bytes, chr(missing), {}, {'wght': weight, 'ital': ital}, preserve)
            evidence.append({'weight': weight, 'ital': ital, 'preserve': preserve,
                             'source_gids': [row[0] for row in original],
                             'variable_gids': [row[0] for row in variable]})
    shared = bool(source_order and variable_order and source_order[0] == variable_order[0]
                  and all(row['source_gids'] == [0] and row['variable_gids'] == [0] for row in evidence))
    return shared, missing, evidence


def structural_regression_cases(missing_codepoint):
    """Do not filter unencoded controls through cmap or hide a visible missing glyph."""
    return [(text, {}, preserve) for text in ('a\u200db', 'a\u200cb', chr(missing_codepoint))
            for preserve in (False, True)]


def verify(masters, path, woff2=None, ppem=160, fail_fast=False, suspect_dir=None, corpus=()):
    audit = Audit(fail_fast)
    static_paths = [(w, i, masters / f'TorchletteSans-{("Italic" if s == "Regular" else s+"Italic") if i else s}.ttf')
                    for w, s in zip(WEIGHTS, STYLES) for i in (0, 1)]
    before = {str(p): digest(p) for _, _, p in static_paths}
    vf_bytes = path.read_bytes()
    font_before = hashlib.sha256(vf_bytes).hexdigest()
    woff_before = digest(woff2) if woff2 else None
    vf = TTFont(io.BytesIO(vf_bytes), recalcTimestamp=False, recalcBBoxes=False)
    fonts = {(w, i): TTFont(p, recalcTimestamp=False) for w, i, p in static_paths}
    base = fonts[400, 0]
    order = base.getGlyphOrder()
    vo = vf.getGlyphOrder()
    header_consistency = serialized_outline_headers(vf, audit)
    n = len(order)
    audit.check(vo[:n] == order and len(vo) == 2*n, 'namespace', {'source': n, 'variable': len(vo)})
    if vo[:n] != order or len(vo) != 2*n:
        raise ValueError('Cannot align full glyph namespaces without inventing a mapping')
    italic_map = dict(zip(order, vo[n:]))
    axes = [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in vf['fvar'].axes]
    audit.check(axes == [('wght', 300, 400, 900), ('ital', 0, 0, 1)], 'axes', axes)
    expected_locations = {(w, i) for w in WEIGHTS for i in (0, 1)}
    actual_locations = {(x.coordinates.get('wght'), x.coordinates.get('ital')) for x in vf['fvar'].instances}
    audit.check(actual_locations == expected_locations and len(vf['fvar'].instances) == 14, 'instances', sorted(actual_locations))
    # OpenType HVAR specification: optional HVAR for TrueType, but head bit1
    # and default LSB=xMin are mandatory regardless of the metric mechanism.
    audit.check(bool(vf['head'].flags & 2), 'head-lsb-flag', vf['head'].flags)
    for name in vo:
        glyph = vf['glyf'][name]
        if glyph.numberOfContours and hasattr(glyph, 'xMin'):
            audit.check(vf['hmtx'][name][1] == glyph.xMin, 'default-lsb-xMin', {'glyph': name, 'lsb': vf['hmtx'][name][1], 'xMin': glyph.xMin})
    for t in ('fvar', 'gvar', 'STAT'):
        audit.check(t in vf, 'required-table', t)
    for t in ('GSUB', 'GPOS'):
        expected = set.union(*(tags(f, t) for f in fonts.values()))
        audit.check(tags(vf, t) >= expected, 'feature-loss', {'table': t, 'missing': sorted(expected-tags(vf, t))})
    audit.check(set(vf.getBestCmap()) == set(base.getBestCmap()), 'cmap-loss', 'Full Unicode coverage must survive')
    for name_id in (0, 13, 14):
        source = {x.toUnicode() for x in base['name'].names if x.nameID == name_id}
        actual = {x.toUnicode() for x in vf['name'].names if x.nameID == name_id}
        audit.check(source <= actual, 'license-metadata', name_id)
    if woff2:
        web = TTFont(woff2, recalcTimestamp=False, recalcBBoxes=False)
        audit.check(web.getGlyphOrder() == vo and web.getBestCmap() == vf.getBestCmap(), 'woff2-coverage', str(woff2))
        for field in set(vars(vf['head'])) | set(vars(web['head'])):
            if field in ('checkSumAdjustment', 'modified'):
                continue
            a, b = getattr(vf['head'], field, None), getattr(web['head'], field, None)
            if field == 'flags':
                a, b = a & ~0x0800, b & ~0x0800  # WOFF2 lossless-transform bit
            audit.check(a == b, 'woff2-head', {'field': field, 'source': a, 'decoded': b})
        for table in set(vf.keys()) | set(web.keys()):
            if table in ('GlyphOrder', 'head'):
                continue
            if table in vf and table in web and vf.getTableData(table) != web.getTableData(table):
                # WOFF2 may reserialize layout with different offset sharing. TTX
                # compares decoded values without treating byte packing as loss.
                a, b = io.BytesIO(), io.BytesIO()
                vf.saveXML(a, tables=[table])
                web.saveXML(b, tables=[table])
                equal = a.getvalue() == b.getvalue()
            else:
                equal = table in vf and table in web
            audit.check(equal, 'woff2-table', table)
    # Infer controls from their real static shaping behavior, not the builder report.
    shared = set()
    control_source = static_paths[0][2].read_bytes()
    for cp, name in base.getBestCmap().items():
        normal = shape(control_source, chr(cp), {})
        preserved = shape(control_source, chr(cp), {}, preserve=True)
        if normal != preserved and all(row[2] == 0 for row in normal):
            shared.add(name)
    shared_gid0, missing_cp, missing_evidence = infer_shared_gid0(
        static_paths, vf_bytes, order, vo, [f.getBestCmap() for f in fonts.values()])
    if shared_gid0:
        shared.add(order[0])
    rows, worst, raw_bearings = [], [], []
    for weight, ital, static_path in static_paths:
        reference = fonts[weight, ital]
        sb = static_path.read_bytes()
        location = {'wght': weight, 'ital': ital}
        mapping = {g: (g if not ital or g in shared else italic_map[g]) for g in order}
        reverse = {v: k for k, v in mapping.items()}
        audit.check(reference.getGlyphOrder() == order and set(reference.getBestCmap()) == set(base.getBestCmap()), 'master-repertoire', str(static_path))
        native_face = freetype.Face(str(path))
        source_face = freetype.Face(str(static_path))
        native_face.set_var_design_coords([weight, ital])
        endpoint = {'weight': weight, 'ital': ital, 'glyphs': 0, 'shaping_cases': 0, 'raster_l1_sum': 0.0, 'max_bound_delta': 0.0}
        for name in order:
            target = mapping[name]
            rm, rb, ri = native_glyph(source_face, reference.getGlyphID(name), ppem)
            vm, vb, vi = native_glyph(native_face, vf.getGlyphID(target), ppem)
            audit.metric(vm[0], rm[0], 'advance', dict(location, glyph=name))
            bearing_record = None
            if vm[1] != rm[1]:
                cboxes = []
                for face, table, glyph_name in ((source_face, reference, name), (native_face, vf, target)):
                    face.load_glyph(table.getGlyphID(glyph_name), freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
                    cb = face.glyph.outline.get_cbox()
                    cboxes.append((cb.xMin, cb.yMin, cb.xMax, cb.yMax))
                bearing_record = dict(location, glyph=name, source_bearing=rm[1], variable_bearing=vm[1], delta=vm[1]-rm[1], source_cbox=cboxes[0], variable_cbox=cboxes[1], source_exact_bbox=rb, variable_exact_bbox=vb)
                raw_bearings.append(bearing_record)
            audit.check((rb is None) == (vb is None), 'empty-outline', dict(location, glyph=name))
            if rb is not None and vb is not None:
                delta = max(abs(x-y) for x, y in zip(rb, vb))
                endpoint['max_bound_delta'] = max(endpoint['max_bound_delta'], delta)
                audit.check(delta <= 1, 'bounds', dict(location, glyph=name, delta=delta, source_bounds=rb, variable_bounds=vb))
                a, b = align_native(ri, vi)
                difference = float(np.abs(a-b).sum())
                ink = max(float(a.sum()), float(b.sum()))
                perimeter = raster_perimeter(a)
                limit = max(.75, perimeter*ppem/reference['head'].unitsPerEm*1.25)
                audit.check(difference <= limit, 'raster', dict(location, glyph=name, delta_pixels=difference, ink_pixels=ink, limit_pixels=limit))
                endpoint['raster_l1_sum'] += difference
                if bearing_record is not None:
                    bearing_record.update(actual_frame_within_bounds=delta <= 1 and difference <= limit, ink_delta_pixels=difference, ink_limit_pixels=limit)
                worst.append({'weight': weight, 'ital': ital, 'glyph': name, 'delta_pixels': difference, 'ink_pixels': ink, 'limit_pixels': limit})
            endpoint['glyphs'] += 1
        feature_sets = [{}, {'ss01': 1, 'ss02': 1, 'ss16': 1}, {'onum': 1, 'lnum': 1}, {'onum': 1, 'tnum': 1, 'ss16': 1}, {'smcp': 1, 'c2sc': 1}, {'mark': 1, 'mkmk': 1}]
        feature_sets += [{tag: 1} for tag in sorted(tags(reference, 'GSUB') | tags(reference, 'GPOS'))]
        cases = [(chr(cp), {}, preserve) for cp in reference.getBestCmap() for preserve in (False, True)]
        cases += [(''.join(c for c in text if ord(c) in reference.getBestCmap()), features, False) for text in TEXTS for features in feature_sets]
        cases += structural_regression_cases(missing_cp)
        builtins_count = len(cases)
        for case in corpus:
            missing_tags = set(case['features']) - (tags(reference, 'GSUB') | tags(reference, 'GPOS'))
            audit.check(not missing_tags, 'corpus-source-feature-missing', dict(location, case_id=case['id'], module=case['module'], missing=sorted(missing_tags)))
            cases.append((case['text'], case['features'], case.get('preserve_default_ignorables', False)))
        endpoint['registered_corpus_cases'] = len(corpus)
        for case_index, (text, features, preserve) in enumerate(cases):
            context = {} if case_index < builtins_count else {'case_id': corpus[case_index-builtins_count]['id'], 'module': corpus[case_index-builtins_count]['module']}
            language = None if case_index < builtins_count else corpus[case_index-builtins_count].get('language')
            if language is not None:
                context['language'] = language
            a = shape(sb, text, features, preserve=preserve, language=language)
            b = shape(vf_bytes, text, features, location, preserve, language=language)
            an = [(reference.getGlyphName(row[0]), *row[1:]) for row in a]
            bn = [(('space' if vo[row[0]] == 'space' and row[2] == 0 else reverse.get(vo[row[0]], 'FOREIGN:'+vo[row[0]])), *row[1:]) for row in b]
            audit.check(len(an) == len(bn), 'shaping-length', dict(location, **context, text=text, features=features))
            for left, right in zip(an, bn):
                audit.check(left[:2] == right[:2], 'shaping-glyph', dict(location, **context, text=text, features=features, want=left, got=right))
                for k in range(2, 6):
                    audit.metric(right[k], left[k], 'shaping-position', dict(location, **context, text=text, features=features, field=k))
            endpoint['shaping_cases'] += 1
        mvar = vf['MVAR'].table if 'MVAR' in vf else None
        records = {r.ValueTag: r.VarIdx for r in mvar.ValueRecord} if mvar else {}
        mvar_inst = VarStoreInstancer(mvar.VarStore, vf['fvar'].axes, normalized(vf, location)) if mvar else None
        for tag, (table, attribute) in MVAR_ENTRIES.items():
            if table in vf and table in reference and hasattr(vf[table], attribute) and hasattr(reference[table], attribute):
                got = getattr(vf[table], attribute) + (mvar_inst[records[tag]] if tag in records else 0)
                audit.metric(got, getattr(reference[table], attribute), 'MVAR-metric', dict(location, field=tag))
        original_math = math_signature(reference, {g: g for g in order})
        variable_math = math_signature(vf, reverse, location)
        differences = numeric_diff(original_math, variable_math)
        audit.check(not differences, 'MATH', {'location': location, 'differences': differences[:10]})
        endpoint['MATH_present'] = original_math is not None
        rows.append(endpoint)
        print(json.dumps({'endpoint': location, 'complete_glyphs': endpoint['glyphs'], 'failures_so_far': dict(audit.failures)}), flush=True)
    intermediate = []
    intermediate_details = []
    for weight, ital in itertools.product((350, 450, 550, 650, 750, 850), (0, 1)):
        intermediate_face = freetype.Face(str(path))
        intermediate_face.set_var_design_coords([weight, ital])
        mapping = {g: (g if not ital or g in shared else italic_map[g]) for g in order}
        for name, target in mapping.items():
            intermediate_face.load_glyph(vf.getGlyphID(target), freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
            ob = intermediate_face.glyph.outline.get_bbox() if intermediate_face.glyph.outline.n_points else None
            b = (ob.xMin, ob.yMin, ob.xMax, ob.yMax) if ob else None
            width = intermediate_face.glyph.metrics.horiAdvance
            audit.check(math.isfinite(width) and abs(width) < 100000, 'intermediate-metric', {'weight': weight, 'ital': ital, 'glyph': name, 'width': width})
            audit.check(b is None or all(math.isfinite(v) and abs(v) < 100000 for v in b), 'intermediate-bounds', {'weight': weight, 'ital': ital, 'glyph': name, 'bounds': b})
        # Critical raster topology compared with its two adjacent real statics.
        lo, hi = max(w for w in WEIGHTS if w < weight), min(w for w in WEIGHTS if w > weight)
        adjacent_paths = [next(p for w, i, p in static_paths if (w, i) == (value, ital)) for value in (lo, hi)]
        adjacent_faces = [freetype.Face(str(p)) for p in adjacent_paths]
        for name in order:
            if name not in mapping:
                continue
            records = [native_glyph(adjacent_faces[0], fonts[lo, ital].getGlyphID(name), 96)[2],
                       native_glyph(intermediate_face, vf.getGlyphID(mapping[name]), 96)[2],
                       native_glyph(adjacent_faces[1], fonts[hi, ital].getGlyphID(name), 96)[2]]
            bitmaps = align_native_many(records)
            failures_before = sum(audit.failures.values())
            topo = [topology(a) for a in bitmaps]
            # A contour correspondence error can retain a counter while sending
            # ink far outside two very similar adjacent static designs. Derive
            # a spatial budget from the actual endpoint ink displacement.
            masks = [a > .5 for a in bitmaps]
            endpoint_a, endpoint_b = masks[0], masks[2]
            if endpoint_a.any() and endpoint_b.any():
                da = ndimage.distance_transform_cdt(~endpoint_a, metric='chessboard')
                db = ndimage.distance_transform_cdt(~endpoint_b, metric='chessboard')
                radius = max(int(da[endpoint_b].max()), int(db[endpoint_a].max()))
            else:
                radius = 0
            envelope = ndimage.maximum_filter(endpoint_a | endpoint_b, size=2*(radius+2)+1)
            outside = float(bitmaps[1][~envelope].sum())
            limit = max(1.0, float(bitmaps[1].sum()) * .005)
            audit.check(outside <= limit, 'intermediate-ink-envelope', {'weight': weight, 'ital': ital, 'glyph': name, 'outside_pixels': outside, 'limit_pixels': limit, 'endpoint_distance_pixels': radius})
            detail = {'weight': weight, 'ital': ital, 'glyph': name, 'topology': topo, 'outside_pixels': outside, 'endpoint_distance_pixels': radius}
            # Component and hole expectations are independent. For example,
            # endpoints may differ in holes while agreeing on one ink component;
            # a newly detached second component is still a regression candidate.
            raster_parts = [label for index, label in ((0, 'components'), (1, 'holes'))
                            if not min(topo[0][index], topo[2][index]) <= topo[1][index] <= max(topo[0][index], topo[2][index])]
            vector_check = None
            if raster_parts:
                vector_check = corroborate_raster_topology(
                    (fonts[lo, ital], vf, fonts[hi, ital]), (name, mapping[name], name),
                    (None, {'wght': weight, 'ital': ital}, None))
                detail['vector_corroboration'] = vector_check
                detail['raster_ppem'] = 96
                for label in raster_parts:
                    audit.check(vector_check['raster_sensitive'], 'intermediate-counter',
                                {'weight': weight, 'ital': ital, 'glyph': name, 'part': label,
                                 'topology': topo, 'vector_corroboration': vector_check})
            area = [float(a.sum()) for a in bitmaps]
            audit.check(not (area[0] == 0 and area[2] == 0 and area[1] > 0), 'intermediate-unexpected-ink', {'weight': weight, 'ital': ital, 'glyph': name})
            audit.check(not (area[0] > 0 and area[2] > 0 and area[1] == 0), 'intermediate-missing-ink', {'weight': weight, 'ital': ital, 'glyph': name})
            detail['ink_area'] = area
            detail['flags'] = []
            if outside > limit:
                detail['flags'].append('reference-ink-envelope')
            for index, label in ((0, 'components'), (1, 'holes')):
                if not min(topo[0][index], topo[2][index]) <= topo[1][index] <= max(topo[0][index], topo[2][index]):
                    detail['flags'].append(label+'-outside-adjacent-reference-range')
            if area[0] == 0 and area[2] == 0 and area[1] > 0:
                detail['flags'].append('unexpected-ink')
            if area[0] > 0 and area[2] > 0 and area[1] == 0:
                detail['flags'].append('missing-ink')
            detail['suspect'] = sum(audit.failures.values()) > failures_before
            detail['classification'] = ('requires-explicit-review' if detail['suspect'] else
                                        'raster-sensitive-vector-topology-agrees' if vector_check and vector_check['raster_sensitive'] else 'no-heuristic-flag')
            if (detail['suspect'] or raster_parts) and suspect_dir:
                png = suspect_dir / f'{ital}-{weight}-{order.index(name)}.png'
                save_probe_png(bitmaps, png)
                detail['native_png'] = str(png)
            intermediate_details.append(detail)
        intermediate.append({'weight': weight, 'ital': ital, 'glyphs_checked': len(order)})
        print(json.dumps({'intermediate': [weight, ital], 'complete_glyphs': len(order), 'failures_so_far': dict(audit.failures)}), flush=True)
    branch_checks = []
    for value in (0, .49, .5, 1):
        ital = int(value >= .5)
        source = fonts[400, ital]
        source_bytes = next(p.read_bytes() for w, i, p in static_paths if (w, i) == (400, ital))
        mapping = {g: (g if not ital or g in shared else italic_map[g]) for g in order}
        reverse = {v: k for k, v in mapping.items()}
        a = shape(source_bytes, 'ag office sigmoid a\u00adb a\u200bb a\u2060b', {'ss16': 1})
        b = shape(vf_bytes, 'ag office sigmoid a\u00adb a\u200bb a\u2060b', {'ss16': 1}, {'wght': 400, 'ital': value})
        expected = [(source.getGlyphName(row[0]), row[1]) for row in a]
        got = [(('space' if vo[row[0]] == 'space' and row[2] == 0 else reverse.get(vo[row[0]], 'FOREIGN:'+vo[row[0]])), row[1]) for row in b]
        audit.check(expected == got, 'italic-branch', {'ital': value, 'expected': expected, 'got': got})
        branch_checks.append({'ital': value, 'expected_style': 'Italic' if ital else 'Roman', 'passed': expected == got})
    for record in raw_bearings:
        if record['source_exact_bbox'] is None and record['variable_exact_bbox'] is None:
            record['actual_frame_within_bounds'] = True
        prerequisites_pass = not any(audit.failures[k] for k in ('head-lsb-flag', 'default-lsb-xMin', 'shaping-length', 'shaping-glyph', 'shaping-position', 'advance'))
        record['classification'] = 'representation-supported-under-stated-checks' if record.get('actual_frame_within_bounds') and prerequisites_pass else 'unresolved-with-candidate-failures'
    after = {str(p): digest(p) for _, _, p in static_paths}
    audit.check(digest(path) == font_before and (not woff2 or digest(woff2) == woff_before), 'candidate-mutation', 'Variable input changed during verification')
    audit.check(before == after, 'static-mutation', 'Input master hashes changed')
    return {'font': str(path), 'sha256': digest(path), 'masters_sha256': before, 'statics_unchanged': before == after,
            'header_consistency': header_consistency, 'italic_branch_checks': branch_checks, 'axes': axes, 'endpoint_results': rows, 'intermediates': intermediate, 'intermediate_shape_probes': intermediate_details, 'corpus_characters_not_in_static_cmap': sorted({ord(c) for text in TEXTS for c in text if ord(c) not in base.getBestCmap()}), 'shared_controls_inferred': sorted(shared), 'structural_gid0': {'shared': shared_gid0, 'missing_codepoint': missing_cp, 'endpoint_evidence': missing_evidence}, 'freetype_native_backend': native_runtime_provenance(),
            'raster_ppem': ppem, 'raster_worst_absolute': sorted(worst, key=lambda x: x['delta_pixels'], reverse=True)[:30],
            'raw_control_bearing_deltas': raw_bearings, 'rounding_within_one_unit': dict(audit.rounding), 'rounding_samples': audit.rounding_samples,
            'failure_counts': dict(audit.failures), 'failure_samples': audit.samples, 'failure_details': audit.details,
            'limits': ['Every endpoint glyph rasterized at one stated size; this is numerical outline evidence, not a visual quality judgment.',
                       'Every original intermediate glyph receives native topology and reference-envelope probes. Pixel connectivity is corroborated only by matching separated filled-vector containment structures and reference-bracketed contour areas; unresolved geometry remains flagged. Raw raster flags and vector evidence remain in the report. No glyph-name allowlist or curve-fidelity clearance.',
                       'One-unit advance/position rounding is allowed and explicitly counted; raster budget models one-unit boundary movement. Every raw bearing/CBox delta is separately preserved; representation support requires actual exact-bbox/raster checks, normative defaults and layout checks, never glyph-name exceptions.',
                       'MATH values resolve VariationIndex records, but this alone does not certify a math layout engine.',
                       'Normative references: https://learn.microsoft.com/en-us/typography/opentype/spec/hvar and https://freetype.org/freetype2/docs/reference/ft2-outline_processing.html']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--masters', type=Path, required=True)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--woff2', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--ppem', type=int, default=160)
    parser.add_argument('--corpus', type=Path, help='Input-only registered feature/guard corpus JSON')
    parser.add_argument('--require-corpus', action='store_true', help='Refuse a missing or empty registered corpus; use for final full-module gates')
    parser.add_argument('--suspect-dir', type=Path, help='Native suspect PNGs; default beside the report')
    parser.add_argument('--fail-fast', action='store_true', help='Stop on the first failure; successful runs still execute all checks.')
    args = parser.parse_args()
    protected = {args.font.resolve(), Path(__file__).resolve()}
    protected.update(p.resolve() for p in args.masters.glob('*.ttf'))
    if args.woff2:
        protected.add(args.woff2.resolve())
    if args.corpus:
        protected.add(args.corpus.resolve())
    if args.report.resolve() in protected:
        parser.error('The report must not overwrite an input font, static master or verifier source')
    if not 8 <= args.ppem <= 512:
        parser.error('--ppem must be between 8 and 512')
    try:
        corpus = load_corpus(args.corpus, args.require_corpus)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    corpus_hash = digest(args.corpus) if args.corpus else None
    source_hash = digest(__file__)
    try:
        result = verify(args.masters, args.font, args.woff2, args.ppem, args.fail_fast, args.suspect_dir or args.report.parent / (args.report.stem+'-suspects'), corpus)
    except EarlyFailure as exc:
        result = {'failure_counts': {exc.kind: 1}, 'failure_samples': [{'kind': exc.kind, 'detail': exc.detail}], 'stopped_early': True}
    except Exception as exc:
        result = {'failure_counts': {'verifier-error': 1}, 'error': f'{type(exc).__name__}: {exc}'}
    result['registered_corpus'] = {'path': str(args.corpus) if args.corpus else None, 'sha256': corpus_hash, 'cases': len(corpus), 'modules': dict(Counter(c['module'] for c in corpus)), 'languages': dict(Counter(c.get('language', '<guessed>') for c in corpus)), 'required': args.require_corpus, 'scope': 'Provided registered inputs compared with original statics at every endpoint; built-in TEXTS alone are not exhaustive module coverage.'}
    if args.corpus and digest(args.corpus) != corpus_hash:
        result['failure_counts']['corpus-mutation'] = 1
    result['verifier_source_sha256'] = source_hash
    result['tool_versions'] = {name: importlib.metadata.version(name) for name in ('fonttools', 'uharfbuzz', 'freetype-py', 'numpy', 'scipy', 'skia-pathops')}
    result['freetype_runtime'] = freetype.version()
    result['freetype_native_backend'] = native_runtime_provenance()
    if result['freetype_native_backend'].get('resolution_error'):
        result['failure_counts']['native-runtime-provenance'] = 1
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'report': str(args.report), 'failures': result['failure_counts']}, indent=2))
    return 1 if result['failure_counts'] else 0


if __name__ == '__main__':
    sys.exit(main())

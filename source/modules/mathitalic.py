"""Mathematical italic Latin and Greek from matched, real Torchlette Italic fonts.

Geometry prototype: 112 explicit Unicode characters; no external font substitution,
new Greek design, MATH-table metrics or dtls/ssty ownership. A complete hash-bound
MATHITALIC_REFERENCE_MANIFEST and matching MATHITALIC_SOURCE_EPOCH are required.
References are built normally without this module. Only their selected outlines and
advances enter the target; original target layout is never imported or replaced.
"""
import hashlib
import io
import json
import os
import unicodedata
from array import array
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates

CODEPOINTS = tuple(cp for cp in range(0x1D434, 0x1D468) if cp != 0x1D455) + (0x210E, 0x1D6A4, 0x1D6A5) + tuple(range(0x1D6E2, 0x1D71C))
MAPPING = {}
for _cp in CODEPOINTS:
    _decomp = unicodedata.decomposition(chr(_cp)).split()
    if len(_decomp) != 2 or _decomp[0] != '<font>':
        raise ValueError(f'Unexpected Unicode math-italic decomposition: U+{_cp:04X}')
    MAPPING[_cp] = int(_decomp[1], 16)  # one level: retain Greek variant identity


def glyph_name(cp):
    return f'u{cp:05X}' if cp > 0xFFFF else f'uni{cp:04X}'


def read_reference(manifest_path, epoch, weight, upem):
    """Read each font once; retain the manifest's expected hash through final checks."""
    path = Path(manifest_path).resolve()
    raw = path.read_bytes()
    doc = json.loads(raw)
    if doc.get('schema') != 1 or not epoch or doc.get('source_epoch') != epoch:
        raise ValueError('mathitalic: missing/mismatched source epoch or manifest schema')
    style = 'Italic' if weight == 400 else {300: 'LightItalic', 500: 'MediumItalic', 600: 'SemiBoldItalic', 700: 'BoldItalic', 800: 'ExtraBoldItalic', 900: 'BlackItalic'}[weight]
    record = doc['styles'][style]
    font_path = Path(record['path']).resolve()
    data = font_path.read_bytes()
    expected = record['sha256']
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f'mathitalic: reference hash mismatch: {font_path}')
    font = TTFont(io.BytesIO(data), recalcBBoxes=False, recalcTimestamp=False)
    if font['head'].unitsPerEm != upem or font['OS/2'].usWeightClass != weight or not font['OS/2'].fsSelection & 1:
        raise ValueError('mathitalic: reference UPEM/weight/italic identity mismatch')
    missing = sorted({source for source in MAPPING.values() if source not in font.getBestCmap()})
    if missing:
        raise ValueError('mathitalic: missing actual source mappings: ' + ', '.join(f'U+{cp:04X}' for cp in missing))
    if any(cp in font.getBestCmap() for cp in CODEPOINTS):
        raise ValueError('mathitalic: references must be built without this module')
    return font, (path, raw, font_path, expected)


def reference_stable(binding):
    manifest_path, raw, font_path, expected = binding
    if manifest_path.read_bytes() != raw or hashlib.sha256(font_path.read_bytes()).hexdigest() != expected:
        raise ValueError('mathitalic: reference inputs changed during use')


def rendered_origin(font, name, visiting=None):
    """TrueType phantom origin, including the last recursive USE_MY_METRICS owner."""
    visiting = set() if visiting is None else visiting
    if name in visiting:
        raise ValueError(f'mathitalic: recursive composite {name}')
    visiting.add(name)
    glyph = font['glyf'][name]
    value = getattr(glyph, 'xMin', 0) - font['hmtx'][name][1]
    if glyph.isComposite():
        for component in glyph.components:
            if not hasattr(component, 'x'):
                raise ValueError(f'mathitalic: point-matched composite {name} unsupported')
            if component.flags & 0x0200:
                _, matrix = component.getComponentInfo()
                if tuple(matrix[:4]) != (1, 0, 0, 1):
                    raise ValueError(f'mathitalic: transformed USE_MY_METRICS requires a native-reviewed rule: {name}')
                if font['hmtx'][name][0] != font['hmtx'][component.glyphName][0]:
                    raise ValueError(f'mathitalic: inconsistent USE_MY_METRICS advance: {name}')
                value = rendered_origin(font, component.glyphName, visiting)
    visiting.remove(name)
    return value


def import_outline(font, name, target_shear, shear_centre):
    """Flatten exact quadratic points; rebase actual paint origin, never fit/redraw."""
    source = font['glyf'][name]
    coords, ends, flags = source.getCoordinates(font['glyf'])
    if not len(coords):
        raise ValueError(f'mathitalic: empty source outline {name}')
    origin = rendered_origin(font, name)
    out = Glyph()
    out.numberOfContours = len(ends)
    out.coordinates = GlyphCoordinates([(x - origin - target_shear * (y - shear_centre), y) for x, y in coords])
    out.endPtsOfContours = list(ends)
    out.flags = array('B', flags)
    from fontTools.ttLib.tables.ttProgram import Program
    out.program = Program()
    # No source hint program, component namespace, layout or global table is imported.
    return out, font['hmtx'][name][0]


def glyphs(ctx):
    manifest = os.environ.get('MATHITALIC_REFERENCE_MANIFEST')
    if not manifest:
        raise ValueError('mathitalic: MATHITALIC_REFERENCE_MANIFEST is required; no fallback')
    font, binding = read_reference(manifest, os.environ.get('MATHITALIC_SOURCE_EPOCH'), ctx.WEIGHT_CLASS, ctx.font['head'].unitsPerEm)
    cmap = font.getBestCmap()
    target_cmap = ctx.font.getBestCmap()
    order = set(ctx.font.getGlyphOrder())
    collisions = [glyph_name(cp) for cp in CODEPOINTS if cp in target_cmap or glyph_name(cp) in order]
    if collisions:
        raise ValueError(f'mathitalic: target collisions {collisions}')
    prepared = [(cp, import_outline(font, cmap[source], ctx.ITALIC_K, ctx.ITALIC_YC)) for cp, source in MAPPING.items()]
    reference_stable(binding)
    if not any(t.isUnicode() and t.format == 12 for t in ctx.font['cmap'].tables):
        for platform, encoding in ((3, 10), (0, 4)):
            table = cmap_format_12(12)
            table.platformID, table.platEncID, table.language = platform, encoding, 0
            table.cmap = dict(target_cmap)
            ctx.font['cmap'].tables.append(table)
    for cp, (glyph, advance) in prepared:
        name = glyph_name(cp)
        ctx.glyf[name] = glyph
        glyph.recalcBounds(ctx.glyf)
        ctx.hmtx[name] = (advance, glyph.xMin)
        if name not in ctx.font.getGlyphOrder():
            ctx.font.setGlyphOrder(ctx.font.getGlyphOrder() + [name])
        ctx.GDEF_CLASS[name] = 1
        ctx.map(cp, name)
    ctx.mathitalic_sources = {glyph_name(cp): cmap[source] for cp, source in MAPPING.items()}
    ctx.log(f'{len(prepared)} actual italic Latin/Greek shapes; source epoch {os.environ["MATHITALIC_SOURCE_EPOCH"]}; no MATH-table or fallback claim')
    reference_stable(binding)

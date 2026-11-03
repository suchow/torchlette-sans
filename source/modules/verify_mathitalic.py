"""Check the explicit math-italic repertoire and its bound original italic source.

CLI: FONT STYLE full|subset [--reference-manifest FILE] [--source-epoch HASH]
     [--original MATCHED_TARGET_BASELINE] [--proof JSON]
This checks geometry/coverage only. The full and new normal subset policy both retain all112;
--original must be a matched same-mode/same-policy baseline, never a full font
used as a subset oracle. Real MATH metrics, dtls/ssty and MathML consumer
ownership are separate gates; no claim is made merely because the cmap is present.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import unicodedata

from fontTools.ttLib import TTFont
import uharfbuzz as hb


def mapping():
    cps = [x for x in range(0x1D434, 0x1D468) if x != 0x1D455] + [0x210E, 0x1D6A4, 0x1D6A5] + list(range(0x1D6E2, 0x1D71C))
    return {cp: int(unicodedata.decomposition(chr(cp)).split()[1], 16) for cp in cps}


def name(cp):
    return f'u{cp:05X}' if cp > 0xFFFF else f'uni{cp:04X}'


def shape(data, text):
    font = hb.Font(hb.Face(data))
    font.scale = (font.face.upem, font.face.upem)
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(font, b, {'kern': False, 'liga': False})
    return [(i.codepoint, i.cluster, p.x_advance, p.y_advance, p.x_offset, p.y_offset) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def outline(font, glyph):
    g = font['glyf'][glyph]
    coords, ends, flags = g.getCoordinates(font['glyf'])
    return list(coords), list(ends), bytes(flags), font['hmtx'][glyph]


def verify(args):
    data = Path(args.font).read_bytes()
    font = TTFont(io.BytesIO(data), recalcBBoxes=False, recalcTimestamp=False)
    cmap, order = font.getBestCmap(), font.getGlyphOrder()
    expected = mapping()
    checks = []
    def check(label, value):
        checks.append({'check': label, 'passed': bool(value)})
    check('exact 112-character contract', len(expected) == 112)
    check('unassigned h slot is absent', 0x1D455 not in cmap)
    classes = font['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in font else {}
    for cp in expected:
        n = name(cp)
        check(f'U+{cp:04X} exact cmap name', cmap.get(cp) == n)
        if cmap.get(cp) != n:
            continue
        g = font['glyf'][n]
        check(f'{n} nonempty base glyph', g.numberOfContours > 0 and classes.get(n) == 1)
        check(f'{n} positive advance', font['hmtx'][n][0] > 0)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format in (12, 13):
                check(f'{n} cmap {table.platformID}/{table.platEncID}', table.cmap.get(cp) == n)
        seq = shape(data, chr(cp))
        check(f'{n} actual direct shaping, no fallback/GID0', len(seq) == 1 and seq[0][0] != 0 and order[seq[0][0]] == n)
    manifest_path = args.reference_manifest or os.environ.get('MATHITALIC_REFERENCE_MANIFEST')
    epoch = args.source_epoch or os.environ.get('MATHITALIC_SOURCE_EPOCH')
    source_record = None
    if manifest_path:
        raw = Path(manifest_path).read_bytes()
        doc = json.loads(raw)
        check('bound reference schema/epoch', doc.get('schema') == 1 and bool(epoch) and doc.get('source_epoch') == epoch)
        w = font['OS/2'].usWeightClass
        style = 'Italic' if w == 400 else {300: 'LightItalic', 500: 'MediumItalic', 600: 'SemiBoldItalic', 700: 'BoldItalic', 800: 'ExtraBoldItalic', 900: 'BlackItalic'}[w]
        source_record = doc['styles'][style]
        sdata = Path(source_record['path']).read_bytes()
        check('reference immutable hash', hashlib.sha256(sdata).hexdigest() == source_record['sha256'])
        src = TTFont(io.BytesIO(sdata), recalcBBoxes=False, recalcTimestamp=False)
        check('reference italic/weight/UPEM', src['OS/2'].usWeightClass == w and bool(src['OS/2'].fsSelection & 1) and src['head'].unitsPerEm == font['head'].unitsPerEm)
        sf, vf = hb.Font(hb.Face(sdata)), hb.Font(hb.Face(data))
        sf.scale = vf.scale = (font['head'].unitsPerEm,) * 2
        for cp, scp in expected.items():
            sn = src.getBestCmap().get(scp)
            check(f'U+{scp:04X} real source exists', sn is not None)
            if sn is None or cp not in cmap:
                continue
            old_gid, new_gid = src.getGlyphID(sn), font.getGlyphID(cmap[cp])
            check(f'{name(cp)} actual source advance', sf.get_glyph_h_advance(old_gid) == vf.get_glyph_h_advance(new_gid))
            a, b = sf.get_glyph_extents(old_gid), vf.get_glyph_extents(new_gid)
            check(f'{name(cp)} source extent within integer unit', a is not None and b is not None and all(abs(x-y) <= 1 for x, y in zip(a, b)))
        check('source/manifest stable after use', Path(manifest_path).read_bytes() == raw and hashlib.sha256(Path(source_record['path']).read_bytes()).hexdigest() == source_record['sha256'])
    if args.original:
        original_data = Path(args.original).read_bytes()
        original = TTFont(io.BytesIO(original_data), recalcBBoxes=False, recalcTimestamp=False)
        check('only declared new glyph names', set(order) - set(original.getGlyphOrder()) == {name(cp) for cp in expected})
        check('all old glyph names retained', set(original.getGlyphOrder()) <= set(order))
        for n in original.getGlyphOrder():
            check(f'original {n} exact geometry/metrics', n in font['glyf'] and outline(original, n) == outline(font, n))
        check('all original cmap entries unchanged', all(cmap.get(cp) == n for cp, n in original.getBestCmap().items()))
        # This finite corpus is deliberately not described as exhaustive GSUB/GPOS preservation.
        for text in ['Torchlette', 'fi fl ffi ffl', 'x + y = 2', 'office affinity', 'αβγ Θϑϕϰ', 'x\u0301\u0304', 'Q O A I l 1']:
            old = shape(original_data, text)
            new = shape(data, text)
            a = [(original.getGlyphOrder()[s[0]], *s[1:]) for s in old]
            b = [(order[s[0]], *s[1:]) for s in new]
            check(f'original named positions {text!r}', a == b)
    check('input font stable after use', Path(args.font).read_bytes() == data)
    report = {'font': str(Path(args.font).resolve()), 'sha256': hashlib.sha256(data).hexdigest(), 'style': args.style, 'mode': args.mode, 'checks': checks, 'passed': sum(x['passed'] for x in checks), 'failed': sum(not x['passed'] for x in checks), 'source_record': source_record, 'limits': ['geometry/coverage prototype, not MATH or browser acceptance', 'named positions finite corpus, not exhaustive layout preservation', 'native FreeType curves/raster and negative controls are separate recorded checks']}
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('font')
    p.add_argument('style')
    p.add_argument('mode', choices=['full', 'subset'])
    p.add_argument('--reference-manifest')
    p.add_argument('--source-epoch')
    p.add_argument('--original')
    p.add_argument('--proof')
    a = p.parse_args()
    try:
        report = verify(a)
    except (KeyError, ValueError, OSError) as e:
        report = {'failed': 1, 'error': str(e)}
    if a.proof:
        Path(a.proof).write_text(json.dumps(report, indent=2) + '\n')
    print(f'verify_mathitalic {a.style} {a.mode}: {report.get("passed",0)} passed, {report["failed"]} failed')
    for row in report.get('checks', []):
        if not row['passed']:
            print('FAIL', row['check'])
    if 'error' in report:
        print('FAIL', report['error'])
    raise SystemExit(bool(report['failed']))


if __name__ == '__main__':
    main()

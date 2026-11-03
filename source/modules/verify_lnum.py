"""Check the lnum module by shaping with HarfBuzz.

    verify_lnum.py <font.ttf> <style> full|subset

1. The font has an lnum feature.
2. Each figure 0-9 (and the ss08 seven): onum gives d.osf; onum + lnum d.pnum; onum + pnum +
   lnum d.pnum; onum + tnum + lnum d, at the tabular advance; lnum alone and tnum + lnum d;
   pnum + lnum d.pnum.
3. lnum cancels onum and keeps its spacing: under every combination of liga ss01 ss02 ss08
   ss16 zero onum pnum tnum smcp (those the font under test keeps), a test text with figures,
   ordinals, percent, times, minus, ratios and a fraction shapes with lnum on exactly as with
   onum off (plus pnum when onum was on without tnum): the same glyphs at the same advances,
   and no old-style glyph (a name with .osf, .tosf or .of) appears.
4. Sanity of 3: with onum on and lnum off the text does take old-style glyphs.
"""
import itertools
import os
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept   # noqa: E402

path, style, mode = sys.argv[1], sys.argv[2], sys.argv[3]
tt = TTFont(path); order = tt.getGlyphOrder()
font = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
fails, checks = [], 0
DIG = 'zero one two three four five six seven eight nine'.split()


def ok(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


def shape(text, feats):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(font, b, feats)
    return [(order[i.codepoint], p.x_advance) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def old(name): return any(s in name.split('.')[1:] for s in ('osf', 'tosf', 'of'))


# 1. the feature
tags = {r.FeatureTag for r in tt['GSUB'].table.FeatureList.FeatureRecord}
ok('lnum' in tags, 'no lnum feature')

# 2. the figures, one by one
CASES = [({'onum': 1}, '.osf', 'p'), ({'onum': 1, 'lnum': 1}, '.pnum', 'p'),
         ({'onum': 1, 'pnum': 1, 'lnum': 1}, '.pnum', 'p'), ({'onum': 1, 'tnum': 1, 'lnum': 1}, '', 't'),
         ({'lnum': 1}, '', 't'), ({'tnum': 1, 'lnum': 1}, '', 't'), ({'pnum': 1, 'lnum': 1}, '.pnum', 'p'),
         ({'onum': 1, 'pnum': 1, 'tnum': 1, 'lnum': 1}, '.pnum', 'p')]
tab_w = shape('0', {})[0][1]
for feats, suf, spacing in CASES:
    if not kept(*feats): continue
    got = shape('0123456789', feats)
    ok([g for g, _ in got] == [d + suf for d in DIG], f'{feats}: {[g for g, _ in got]}, not *{suf}')
    if spacing == 't':
        ok(all(w == tab_w for _, w in got), f'{feats}: advances {[w for _, w in got]} not all tabular {tab_w}')
    if kept('ss08'):
        s7 = shape('7', dict(feats, ss08=1))[0][0]
        want = {'.osf': 'seven.osf.ss08', '.pnum': 'seven.pnum.ss08', '': 'seven.ss08'}[suf]
        ok(s7 == want, f'{feats} + ss08: {s7}, not {want}')

# 3. lnum cancels onum under every combination
TEXT = '1969 7 1st 2nd 3rd 4th 10:30 50% 97.2% 28x28 3−2 3×4 3±1 3≈4 (3/4) 0 ½ 2048'
F = [t for t in ('liga', 'ss01', 'ss02', 'ss08', 'ss16', 'zero', 'onum', 'pnum', 'tnum', 'smcp')
     if t in tags and kept(t)]
saw_old = False
combos = 0
for bits in itertools.product([0, 1], repeat=len(F)):
    fd = dict(zip(F, bits))
    if not fd.get('onum'): continue
    combos += 1
    with_lnum = shape(TEXT, dict(fd, lnum=1))
    ref = dict(fd, onum=0)
    if not fd.get('tnum'): ref['pnum'] = 1
    want = shape(TEXT, ref)
    on = sorted(t for t, v in fd.items() if v)
    ok(with_lnum == want, f'{on} + lnum: {[g for g, _ in with_lnum]} != {[g for g, _ in want]}')
    bad = sorted({g for g, _ in with_lnum if old(g)})
    ok(not bad, f'{on} + lnum: old-style glyphs {bad}')
    if not fd.get('smcp'):
        saw_old |= any(old(g) for g, _ in shape(TEXT, fd))
ok(saw_old, 'onum never made an old-style glyph: the test text tests nothing')

print(f'lnum {style} {mode}: {checks} checks ({combos} feature combinations over {" ".join(F)}), {len(fails)} failures')
for f in fails[:20]: print('  FAIL', f)
sys.exit(1 if fails else 0)

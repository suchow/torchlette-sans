"""Checks of the fleurons module: the ornaments (U+E900-E915, U+E920-E925), the drafts
(U+E930-E938), the families (round 3: twelve Lissajous figures at U+E940-E94B and the 27
positions of the three-disc Tower of Hanoi at U+E950-E96A), the round 4 options (eight Bayes
nets at U+E970-E977, three Playfair charts at U+E978-E97A, two Turing tapes at U+E97B-E97C;
since round 5 superseded by Jordan's picks at U+E909, U+E90E and U+E911, and kept until they are
dropped) and the printers' marks ❦ ❧ ☙ ☞ ☜ ⁂ ※.

    verify_fleurons.py FONT STYLE full|subset

1. Coverage: every code point maps to its own glyph (uniXXXX) with ink and a positive
   advance, and shapes to it under HarfBuzz alone and between letters, with no features and
   with the app's (ss01 ss02 ss16 onum pnum). In the web subset a code point may be absent only
   while the Makefile's UNICODES leaves it out; then the glyph must be gone too.
2. Layout (where ornm is kept): with ornm, bullet takes alternate n (1 ... 35) to the nth
   ornament and the letters a-z, A-I become the ornaments in order (the drafts, the
   families and the options are left out); without it, nothing changes.
3. Clearance (not the drafts; the families and options too): each glyph's contour count is the one drawn at Regular (EXPECTED below), so no
   counter closes up or stroke fuses with its neighbour in any style; and if the Regular of the
   same build (or subset) lies beside FONT, the counts match it too.
4. Clean outlines (the visual gate's mechanical half): outline_check.py finds no spur, no
   segment under 4 units and no kink above 10 degrees in any of these glyphs (in a draft, a
   problem is printed as a note and does not fail).
5. Italic styles: each ornament stands upright: its outline is the same weight's upright
   outline moved sideways (after the shift of their boxes the two outlines differ in under 4%
   of the area, or by under 2 units on average, the area between them over the outline's
   length: rounding to the grid and the cleanup move points by a unit or so, which is more
   than 4% of a thin, long drawing such as the Hanoi positions or a Lissajous figure at Light,
   while a leaning drawing would be tens of units off; the boxes agree within 6), when that
   upright font lies beside FONT. ⁂, ※ and the draft FL18 are built from the italic's own
   letters and signs, so they are left out (FL9's P and Q are drawn, since round 3).
6. Sizes: the fleurons stand within the font's vertical metrics (win ascent and descent).
"""
import os
import re
import sys

import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import outline_check as OC          # noqa: E402
from webfeatures import kept        # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH); glyf = f['glyf']; cmap = f.getBestCmap(); hmtx = f['hmtx']; os2 = f['OS/2']
face = hb.Face(hb.Blob.from_file_path(PATH)); hbfont = hb.Font(face)
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
ITALIC = STYLE.endswith('Italic')
fails = 0; checks = 0

ORN = [0xE900 + i for i in range(0x16)] + [0xE920 + i for i in range(6)]
DRAFTS = [0xE930 + i for i in range(9)]
FAMILIES = [0xE940 + i for i in range(12)] + [0xE950 + i for i in range(27)]
OPTIONS = [0xE970 + i for i in range(13)]      # round 4's Bayes nets, Playfair charts, Turing tapes (superseded in round 5)
MARKS = [0x2766, 0x2767, 0x2619, 0x261E, 0x261C, 0x2042, 0x203B]
ORNM = ORN + MARKS                   # the ornm order
ALL = ORN + DRAFTS + FAMILIES + OPTIONS + MARKS
NAME = {cp: f'uni{cp:04X}' for cp in ALL}
# contour counts as drawn at Regular (python verify_fleurons.py FONT Regular full --print)
EXPECTED = {'uniE900': 1, 'uniE901': 3, 'uniE902': 5, 'uniE903': 8, 'uniE904': 1, 'uniE905': 9, 'uniE906': 2,
            'uniE907': 3, 'uniE908': 2, 'uniE909': 5, 'uniE90A': 3, 'uniE90B': 8, 'uniE90C': 8, 'uniE90D': 1,
            'uniE90E': 6, 'uniE90F': 1, 'uniE910': 7, 'uniE911': 9, 'uniE912': 1, 'uniE913': 8, 'uniE914': 2,
            'uniE915': 2, 'uniE920': 2, 'uniE921': 2, 'uniE922': 9, 'uniE923': 1, 'uniE924': 1, 'uniE925': 1,
            'uniE940': 3, 'uniE941': 4, 'uniE942': 9, 'uniE943': 9, 'uniE944': 9, 'uniE945': 9, 'uniE946': 19,
            'uniE947': 19, 'uniE948': 24, 'uniE949': 33, 'uniE94A': 33, 'uniE94B': 15, 'uniE950': 1,
            'uniE951': 1, 'uniE952': 1, 'uniE953': 1, 'uniE954': 1, 'uniE955': 1, 'uniE956': 1, 'uniE957': 1,
            'uniE958': 1, 'uniE959': 1, 'uniE95A': 1, 'uniE95B': 1, 'uniE95C': 1, 'uniE95D': 1, 'uniE95E': 1,
            'uniE95F': 1, 'uniE960': 1, 'uniE961': 1, 'uniE962': 1, 'uniE963': 1, 'uniE964': 1, 'uniE965': 1,
            'uniE966': 1, 'uniE967': 1, 'uniE968': 1, 'uniE969': 1, 'uniE96A': 1, 'uniE970': 3, 'uniE971': 6,
            'uniE972': 4, 'uniE973': 5, 'uniE974': 7, 'uniE975': 5, 'uniE976': 7, 'uniE977': 5, 'uniE978': 4,
            'uniE979': 3, 'uniE97A': 6, 'uniE97B': 9, 'uniE97C': 9, 'uni2766': 3, 'uni2767': 3, 'uni2619': 3,
            'uni261E': 7, 'uni261C': 7, 'uni2042': 3, 'uni203B': 5}


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('[verify_fleurons FAIL]', *msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(hbfont, b, feats or {})
    return [hbfont.get_glyph_name(i.codepoint) for i in b.glyph_infos]


def web_ranges():
    mk = open(os.path.join(os.path.dirname(HERE), 'Makefile')).read()
    line = re.search(r'^UNICODES := (.*)$', mk, re.M).group(1)
    out = []
    for part in line.split(','):
        a, _, b = part.strip()[2:].partition('-')
        out.append((int(a, 16), int(b or a, 16)))
    return out


def in_web(cp): return any(a <= cp <= b for a, b in web_ranges())


def outline(gl, n):
    p = pathops.Path(); gl[n].draw(p.getPen(), gl); p.simplify(); return p


def perimeter(gl, n):
    """The length of a glyph's outline, along its points (on- and off-curve)."""
    c, ends, _ = gl[n].getCoordinates(gl); s0 = 0; L = 0.0
    for e in ends:
        pts = list(c[s0:e + 1]); s0 = e + 1
        L += sum(((pts[i][0] - pts[i - 1][0]) ** 2 + (pts[i][1] - pts[i - 1][1]) ** 2) ** 0.5 for i in range(len(pts)))
    return L


def shifted(p, dx):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (1, 0, 0, 1, dx, 0))); return q


present = []
# 1. coverage
for cp in ALL:
    n = NAME[cp]
    if MODE == 'subset' and not in_web(cp):
        check(cp not in cmap or cmap[cp] == n, f'U+{cp:04X} outside UNICODES but mapped to {cmap.get(cp)}')
        continue
    check(cmap.get(cp) == n, f'U+{cp:04X} maps to {cmap.get(cp)}, not {n}')
    if cmap.get(cp) != n: continue
    present.append(cp)
    g = glyf[n]
    check(g.numberOfContours > 0, f'{n} has no ink'); check(hmtx[n][0] > 0, f'{n} has no advance')
    for feats in (None, APP):
        check(shape(chr(cp), feats) == [n], f'U+{cp:04X} alone shapes to {shape(chr(cp), feats)} ({feats})')
        s = shape('x' + chr(cp) + 'x', feats)
        check(len(s) == 3 and s[1] == n, f'U+{cp:04X} between letters shapes to {s} ({feats})')

# 2. ornm
if kept('ornm') and MODE == 'full':
    letters = [chr(ord('a') + i) for i in range(26)] + [chr(ord('A') + i) for i in range(26)]
    for i, cp in enumerate(ORNM):
        check(shape('•', {'ornm': i + 1}) == [NAME[cp]], f'ornm={i + 1} on bullet gives {shape(chr(0x2022), {"ornm": i + 1})}, not {NAME[cp]}')
        check(shape(letters[i], {'ornm': 1}) == [NAME[cp]], f'ornm on {letters[i]} gives {shape(letters[i], {"ornm": 1})}')
    check(shape('a•', {}) == ['a', 'bullet'], f'without ornm a and bullet change: {shape("a" + chr(0x2022))}')

# 3. clearance
base = 'web-subset-' if os.path.basename(PATH).startswith('web-subset-') else 'TorchletteSans-'
weight = (STYLE[:-len('Italic')] if ITALIC else STYLE) or 'Regular'
reg_path = os.path.join(os.path.dirname(PATH), base + 'Regular.ttf')
reg = TTFont(reg_path)['glyf'] if os.path.exists(reg_path) and os.path.abspath(reg_path) != os.path.abspath(PATH) else None
counts = {}
for cp in present:
    if cp in DRAFTS: continue        # the drafts (a mesh, a traced head) are not held to it
    n = NAME[cp]; k = glyf[n].numberOfContours; counts[n] = k
    if n in EXPECTED: check(k == EXPECTED[n], f'{n}: {k} contours, {EXPECTED[n]} drawn at Regular (a counter closed or two strokes fused)')
    if reg is not None and n in reg.glyphs:
        check(k == reg[n].numberOfContours, f'{n}: {k} contours, the Regular beside it has {reg[n].numberOfContours}')
if '--print' in sys.argv: print('EXPECTED =', counts)

# 4. clean outlines
for cp in present:
    n = NAME[cp]
    for b in OC.check(glyf[n], glyf):
        kind = b.split()[0]
        m = re.search(r'\(([\d.]+) deg\)', b)
        if kind == 'kink' and m and float(m.group(1)) <= 10: continue
        if cp in DRAFTS: print(f'[verify_fleurons note] draft {n}: {b}'); continue
        check(False, f'{n}: {b}')

# 5. upright in the italics
if ITALIC:
    up_path = os.path.join(os.path.dirname(PATH), base + weight + '.ttf')
    if os.path.exists(up_path):
        up = TTFont(up_path)['glyf']
        for cp in present:
            n = NAME[cp]
            if cp in (0x2042, 0x203B, 0xE934): continue   # built from the italic's own letters and signs
            ga, gb = glyf[n], up[n]
            pa, pb = outline(glyf, n), outline(up, n)
            # the area between them. Skia's boolean ops can misfire where two edges coincide exactly
            # (XOR reported 13% for FL9 in ExtraBold Italic, where the true figure is 0.25%), so the
            # smallest of XOR and the two one-way differences, each at the shift and at shifts of a
            # hundredth of a unit, is taken: a misfire rarely survives all six, and a leaning
            # drawing is tens of units off in every one of them
            xa = None
            for e in (0.0, 0.01, -0.01):
                q = shifted(pa, gb.xMin - ga.xMin + e)
                for v in (abs(pathops.op(q, pb, pathops.PathOp.XOR).area),
                          abs(pathops.op(q, pb, pathops.PathOp.DIFFERENCE).area) + abs(pathops.op(pb, q, pathops.PathOp.DIFFERENCE).area)):
                    xa = v if xa is None else min(xa, v)
            frac = xa / max(1.0, abs(pb.area))
            disp = xa / max(1.0, perimeter(up, n))      # the mean distance between the two outlines
            check((frac < (0.05 if cp in DRAFTS else 0.04) or disp < 2.0) and abs((ga.xMax - ga.xMin) - (gb.xMax - gb.xMin)) <= 6
                  and abs(ga.yMin - gb.yMin) <= 6 and abs(ga.yMax - gb.yMax) <= 6,
                  f'{n} is not the upright drawing shifted in {STYLE} (they differ in {frac:.1%} of the area, {disp:.2f} units on average)')

# 6. metrics
for cp in present:
    g = glyf[NAME[cp]]
    check(g.yMax <= os2.usWinAscent and -g.yMin <= os2.usWinDescent, f'{NAME[cp]} leaves the win metrics ({g.yMin}..{g.yMax})')

print(f'verify_fleurons {os.path.basename(PATH)} {STYLE} {MODE}: {checks} checks, {fails} failures ({len(present)} glyphs)')
sys.exit(1 if fails else 0)

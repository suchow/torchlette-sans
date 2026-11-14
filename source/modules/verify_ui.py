"""Checks of the ui module: ✓ ✗ ■ □ ▶ ● ○ ★, ①-⑳ and ⌘ ⌥ ⇧ ⏎ ⌫.

    verify_ui.py FONT STYLE full|subset

1. Coverage: each of the 33 characters shapes under HarfBuzz, alone and between letters, with
   no features and with the app's (ss01 ss02 ss16 onum pnum), to its own glyph with ink. In
   the web subset the circled numbers may be absent while the Makefile's UNICODES leaves them
   out; ✓ ✗ ★, the geometric shapes and the keyboard symbols must be there.
2. Shapes: ■ and □ are cap-height squares on the baseline, ● and ○ circles of the cap height
   with the round letters' overshoot, ▶ an equilateral triangle 1.12 cap heights tall centred
   on the capitals, ★ one contour as wide as the cap height; □ and ○ are hollow at the centre
   and their stroke is H's crossbar within 2; ✓ and ✗ are cap-height marks whose stroke is X's
   diagonal within 3 (one contour each; ✓'s lowest point left of its highest).
3. Circled numbers (the rule in ui.py's docstring): the figures' stem FS is 0.82 of H's stem at
   Regular's stem, 0.64 at Black's, linear between, and the ring's stroke 0.8 of FS. All twenty
   are square (within 3), 1.08 cap heights tall plus the ring stroke's excess over 0.0837 cap
   heights, centred on the capitals; at mid-height the outermost spans are the ring at 0.8 FS
   (within 2) with ink between; the figures keep 0.02 of the ring inside its inner circle; ①'s
   stem at mid-height is FS within 3, so the ring is 0.75 to 0.85 of it; ①'s figure is 0.62 of
   the inner diameter tall (within 0.015); ⑪'s figures are 0.95 of ①'s height down to 0.87 at
   Black's stem in an upright style (0.78 in an italic), at most 0.97, and their stems 0.90 of
   ①'s less 0.12 at Black's stem (within 0.05); ⑦'s figure has Torchlette's crossbar (a span
   near mid-height wider than 0.45 of the figure).
4. Keyboard (the same capped stroke): ⌘ is a cap-height square with six contours (the
   outline, the square's counter, four loops); ⌥ is a cap height wide and 0.62 of one tall,
   one span at mid-height and two at the top; ⇧ is cap height tall and 0.8 wide, hollow (two
   strokes across the shaft, two across the head at their slope); ⏎ is cap height tall with a
   riser at the top right; ⌫ is cap height tall, 1.42 wide and shows three spans at mid-height
   (point, cross, side).
5. Italic styles: ■ ● ⌘ ① keep square bounds (the pictures stand upright) while ①'s figure
   leans with the slant (its stem moves 0.1587 of the rise between two heights, within 10).
6. Nothing leaves the typo or win vertical metrics (the issue-33 shapes included).
7. Issue 33's shapes: each of ▲ △ ▼ ▽ ◀ ◁ ▷ ▴ ▵ ▾ ▿ ◂ ◃ ▹ ◆ ☆ ▪ ▫ ◦ ◯ ◌ is mapped, inked, a base
   (GDEF 1), shapes between letters and is not kerned beside A V 7; ◀ ◂ are ▶ ▸ mirrored, ▲ ▴
   are ▶ ▸ turned a quarter and ▼ ▾ ▲ ▴ turned over about ▶ ▸'s centre (outlines equal within
   about a unit, by the area they do not share), with ▶ ▸'s advance or each other's and their
   left sidebearing; each white shape's outer contour is its black one's (☆ ★'s, ▫ ▪'s, ◦ the
   bullet's, ◆ is ◇'s), two contours, the stroke the crossbar up to half the inradius (△ ▵ ▫);
   ☆'s stroke is the crossbar up to 0.09 of the cap height and 0.15 of the rest (within 2), at
   least 0.6 of △'s, its inner star at least a third of ★'s width; ◦'s ring the crossbar up to
   0.28 of the bullet's diameter and half the rest, at most a third of it (within 3), the
   counter at least a third across; in full mode, with the other six weights of the slant
   beside the font, ☆'s and ◦'s ink grows at every step from Light to Black, their contour
   counts equal;
   ▪ is 0.62 cap heights square on 235; ◯ is 1.125 of ○ on the capitals in the crossbar; ◌ is
   twelve equal round dots at 30 degrees on one radius, 0.93 of the x-height across, top 480.
"""
import math
import os
import sys

import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']; os2 = f['OS/2']
face = hb.Face(hb.Blob.from_file_path(PATH)); hbfont = hb.Font(face)
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
ITALIC = STYLE.endswith('Italic'); K = 0.1587
fails = 0; checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('[verify_ui FAIL]', *msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(hbfont, b, feats or {})
    return [hbfont.get_glyph_name(i.codepoint) for i in b.glyph_infos]


def path(g):
    p = pathops.Path(); gs[g].draw(p.getPen(glyphSet=gs)); return p


def spans(p, y=None, x=None):
    r = pathops.Path(); pen = r.getPen()
    box = (-5000, y - 0.25, 5000, y + 0.25) if y is not None else (x - 0.25, -5000, x + 0.25, 5000)
    pen.moveTo((box[0], box[1])); pen.lineTo((box[2], box[1])); pen.lineTo((box[2], box[3])); pen.lineTo((box[0], box[3])); pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION); i, j = (0, 2) if y is not None else (1, 3)
    return sorted((c.bounds[i], c.bounds[j]) for c in q.contours)


def width(s): return s[1] - s[0]
def mid(s): return (s[0] + s[1]) / 2
def near(a, b, tol): return abs(a - b) <= tol


CHARS = {0x2713: '✓', 0x2717: '✗', 0x25A0: '■', 0x25A1: '□', 0x25B6: '▶', 0x25CF: '●', 0x25CB: '○', 0x2605: '★',
         0x2318: '⌘', 0x2325: '⌥', 0x21E7: '⇧', 0x23CE: '⏎', 0x232B: '⌫'}
CHARS.update({0x2460 + i: chr(0x2460 + i) for i in range(20)})
MAY_MISS = {0x2460 + i for i in range(20)} if MODE == 'subset' else set()

# ---- 1. coverage ---------------------------------------------------------------------------
present = {}
for u, ch in sorted(CHARS.items()):
    if u not in cmap:
        check(u in MAY_MISS, f'U+{u:04X} {ch} unmapped')
        continue
    g = cmap[u]; present[u] = g
    check(path(g).bounds is not None and hmtx[g][0] > 0, f'{g}: no ink or no advance')
    for feats in (None, APP):
        check(shape(ch, feats) == [g], f'{ch} shapes to {shape(ch, feats)}, not [{g}] (features {feats})')
        names = shape('a' + ch + 'b', feats)
        check(len(names) == 3 and names[1] == g, f'a{ch}b shapes to {names} (features {feats})')
missing = sorted(set(CHARS) - set(present))
print(f'coverage: {len(present)} of {len(CHARS)} characters mapped and shaping' + (f'; not in the web subset: {[hex(u) for u in missing]}' if missing else ''))

# ---- the font's own measures ---------------------------------------------------------------
H = path('H'); Hb = H.bounds; CAP = Hb[3]; CC = CAP / 2
US = width(spans(H, x=(Hb[0] + Hb[2]) / 2)[0])                           # the crossbar
X = path('X')
if ITALIC:                                                                 # measured upright, as the module measured it
    q = pathops.Path(); X.draw(TransformPen(q.getPen(), (1, 0, -K, 1, K * 252, 0))); X = q
s1, s2 = spans(X, y=CAP * 0.14)[0], spans(X, y=CAP * 0.28)[0]
DS = width(s1) * math.sin(math.atan2(CAP * 0.14, abs(mid(s2) - mid(s1))))   # X's diagonal across its stroke
KS = min(US, 0.15 * CAP)                                                   # the keyboard symbols' stroke
HS = width(spans(H, y=CAP * 0.25)[0])                                      # H's stem (a shear keeps its width across)
TW = (HS - 0.0936 * CAP) / ((0.2397 - 0.0936) * CAP)                       # 0 at Regular's stem, 1 at Black's
FS = (0.82 - 0.18 * TW) * HS                                               # the circled figures' stem
RS = 0.8 * FS                                                              # and their ring's stroke
RING = 1.08 * CAP + max(0.0, RS - 0.0837 * CAP)                            # the ring's diameter


def square(g, tol, what):
    b = path(g).bounds
    check(near(b[2] - b[0], b[3] - b[1], tol), f'{what}: bounds {b[2] - b[0]:.0f} by {b[3] - b[1]:.0f}, not square')
    return b


# ---- 2. shapes -----------------------------------------------------------------------------
if 0x25A0 in present:
    b = square(present[0x25A0], 1, '■'); check(near(b[1], 0, 1) and near(b[3], CAP, 1), f'■: {b[1]:.0f}..{b[3]:.0f}')
if 0x25A1 in present:
    b = square(present[0x25A1], 1, '□'); sp = spans(path(present[0x25A1]), y=CC)
    check(len(sp) == 2 and all(near(width(s), US, 2) for s in sp), f'□: spans {sp} against the crossbar {US:.0f}')
if 0x25CF in present:
    b = square(present[0x25CF], 2, '●'); check(near(b[3] - b[1], CAP + 18, 4), f'●: {b[3] - b[1]:.0f} tall')
if 0x25CB in present:
    b = square(present[0x25CB], 2, '○'); sp = spans(path(present[0x25CB]), y=CC)
    check(len(sp) == 2 and all(near(width(s), US, 2) for s in sp), f'○: spans {sp} against the crossbar {US:.0f}')
if 0x25B6 in present:
    b = path(present[0x25B6]).bounds
    check(near(b[3] - b[1], 1.12 * CAP, 4) and near(b[2] - b[0], (b[3] - b[1]) * math.sqrt(3) / 2, 4), f'▶: {b[2] - b[0]:.0f} by {b[3] - b[1]:.0f}')
    check(near((b[1] + b[3]) / 2, CC, 2), f'▶: centre {(b[1] + b[3]) / 2:.0f}')
if 0x2605 in present:
    p = path(present[0x2605]); b = p.bounds
    check(near(b[2] - b[0], CAP, 3) and len(list(p.contours)) == 1 and near((b[1] + b[3]) / 2, CC, 3), f'★: {b}, {len(list(p.contours))} contours')
for u, what in ((0x2713, '✓'), (0x2717, '✗')):
    if u not in present: continue
    p = path(present[u]); b = p.bounds
    check(near(b[3], CAP, 3), f'{what}: top {b[3]:.0f}')
    check(len(list(p.contours)) == 1, f'{what}: {len(list(p.contours))} contours')
    if u == 0x2713:
        check(near(b[1], -12, 3), f'✓: bottom {b[1]:.0f}')
        sp = spans(p, y=CAP * 0.75)
        check(len(sp) == 1 and near(width(sp[0]) * math.sin(math.radians(58)), DS, 4), f'✓: stroke {sp} against X\'s diagonal {DS:.0f}')
    else:
        check(near(b[1], 0, 2), f'✗: bottom {b[1]:.0f}')
        sp = spans(p, y=CAP * 0.1); check(len(sp) == 2 and near(width(sp[0]), width(sp[1]), 2), f'✗: spans {sp}')
        check(len(spans(p, y=CC)) == 1, '✗: no crossing at mid-height')
print(f'shapes: cap height {CAP:.0f}, crossbar {US:.0f}, diagonal {DS:.0f}')

# ---- 3. circled numbers ----------------------------------------------------------------------
def circle(cx, cy, r):
    k = 0.5523 * r; p = pathops.Path(); pen = p.getPen()
    pen.moveTo((cx + r, cy)); pen.curveTo((cx + r, cy + k), (cx + k, cy + r), (cx, cy + r)); pen.curveTo((cx - k, cy + r), (cx - r, cy + k), (cx - r, cy))
    pen.curveTo((cx - r, cy - k), (cx - k, cy - r), (cx, cy - r)); pen.curveTo((cx + k, cy - r), (cx + r, cy - k), (cx + r, cy)); pen.closePath()
    return p


one_h = None
for n in (1,) + tuple(range(2, 21)):
    u = 0x2460 + n - 1
    if u not in present: continue
    g = present[u]; what = chr(u); p = path(g); b = square(g, 3, what)
    check(near(b[3] - b[1], RING, 3) and near((b[1] + b[3]) / 2, CC, 2), f'{what}: {b[1]:.0f}..{b[3]:.0f} against a {RING:.0f} ring on {CC:.0f}')
    sp = spans(p, y=CC)
    check(len(sp) >= 3 and near(width(sp[0]), RS, 2) and near(width(sp[-1]), RS, 2), f'{what}: ring spans {sp[:1]} {sp[-1:]} against {RS:.1f}')
    cx, cy, R = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, (b[2] - b[0]) / 2
    rw = width(sp[0]) if sp else RS; RIN = R - rw                       # the ring as drawn
    # the figure(s): the ink left when the ring (a little thickened) is taken away
    annulus = pathops.op(circle(cx, cy, R + 2), circle(cx, cy, RIN - 2), pathops.PathOp.DIFFERENCE)
    fig = pathops.op(p, annulus, pathops.PathOp.DIFFERENCE); fb = fig.bounds
    check(fb is not None and fb[2] > fb[0], f'{what}: no figure inside the ring')
    if not fb or fb[2] <= fb[0]: continue
    out = pathops.op(fig, circle(cx, cy, RIN - 0.02 * 2 * R), pathops.PathOp.DIFFERENCE).bounds
    check(not out or out[2] - out[0] <= 0.5 or out[3] - out[1] <= 0.5, f'{what}: figure within {0.02 * 2 * R:.0f} of the ring (ink out to {out})')
    if n == 1:
        inner_sp = sp[1:-1]; one_h = fb[3] - fb[1]; stem = width(inner_sp[0]) if len(inner_sp) == 1 else 0
        check(len(inner_sp) == 1 and near(stem, FS, 3), f'①: figure stem {inner_sp} against {FS:.1f}')
        check(stem and 0.75 <= rw / stem <= 0.85, f'①: ring {rw:.1f} is {rw / max(stem, 1):.2f} of the figure stem {stem:.1f}, expected 0.8')
        check(near(one_h / (2 * RIN), 0.62, 0.015), f'①: figure {one_h:.0f} tall, {one_h / (2 * RIN):.3f} of the inner diameter {2 * RIN:.0f}, expected 0.62')
        print(f'circled numbers: figure stem {stem:.1f} (H {HS:.1f}), ring {width(sp[0]):.1f} = {width(sp[0]) / max(stem, 1):.2f} of it, '
              f'figure {one_h / (2 * RIN):.3f} of the inner diameter')
    if n == 11 and one_h:
        h = fb[3] - fb[1]; lo = 0.78 if ITALIC else 0.95 - 0.08 * TW
        check(lo - 0.01 <= h / one_h <= 0.97, f'⑪: figures {h:.0f} tall, {h / one_h:.2f} of ①\'s {one_h:.0f}, expected {lo:.2f} to 0.97')
        st = [width(s) for s in sp[1:-1]]; pv = 0.90 - 0.12 * TW
        check(len(st) == 2 and all(near(w / FS, pv, 0.05) for w in st), f'⑪: figure stems {st} against ①\'s {FS:.1f}, expected {pv:.2f} of it')
        print(f'circled numbers: ⑪ at {h / one_h:.2f} of ①\'s height, its stems {[round(w / FS, 2) for w in st]} of ①\'s')
    if n == 7:
        wide = max((width(s) for y in range(-40, 70, 10) for s in spans(p, y=CC + y)[1:-1]), default=0)
        check(wide > 0.45 * (fb[2] - fb[0]), f'⑦: no crossbar near mid-height (widest figure span {wide:.0f} of a {fb[2] - fb[0]:.0f} figure)')
print('circled numbers: rings on the capitals, figures inside')

# ---- 4. keyboard -----------------------------------------------------------------------------
if 0x2318 in present:
    p = path(present[0x2318]); b = square(present[0x2318], 3, '⌘')
    check(near(b[3] - b[1], CAP, 3) and near((b[1] + b[3]) / 2, CC, 2), f'⌘: {b[1]:.0f}..{b[3]:.0f} against the cap height on {CC:.0f}')
    check(len(list(p.contours)) == 6, f'⌘: {len(list(p.contours))} contours, expected 6')
    sp = spans(p, y=CC); check(len(sp) == 2 and all(near(width(s), KS, 2) for s in sp), f'⌘: spans {sp} at mid-height against {KS:.0f}')
if 0x2325 in present:
    p = path(present[0x2325]); b = p.bounds
    check(near(b[2] - b[0], CAP, 3) and near(b[3] - b[1], 0.62 * CAP, 3), f'⌥: {b[2] - b[0]:.0f} by {b[3] - b[1]:.0f}')
    check(len(spans(p, y=CC)) == 1 and len(spans(p, y=b[3] - KS / 2)) == 2, f'⌥: spans {spans(p, y=CC)} / {spans(p, y=b[3] - KS / 2)}')
if 0x21E7 in present:
    p = path(present[0x21E7]); b = p.bounds
    check(near(b[3] - b[1], CAP, 2) and near(b[2] - b[0], 0.8 * CAP, 3), f'⇧: {b[2] - b[0]:.0f} by {b[3] - b[1]:.0f}')
    slope = KS / math.sin(math.atan2(CAP / 2, 0.4 * CAP))                 # the head's side across a scanline
    y_head = (CAP / 2 + KS + CAP - KS / math.sin(math.atan2(0.4 * CAP, CAP / 2))) / 2   # midway up the head's counter
    for y, w in ((CAP * 0.25, KS), (y_head, slope)):
        sp = spans(p, y=y); check(len(sp) == 2 and near(width(sp[0]), w, 3) and near(width(sp[1]), w, 3), f'⇧: spans {sp} at y={y:.0f}, expected two of {w:.0f}')
if 0x23CE in present:
    p = path(present[0x23CE]); b = p.bounds
    check(near(b[3], CAP, 2) and near(b[1], 0, 3), f'⏎: {b[1]:.0f}..{b[3]:.0f}')
    sp = spans(p, y=CAP - 10); check(len(sp) == 1 and near(width(sp[0]), KS, 2) and sp[0][1] > b[2] - 2, f'⏎: riser {sp}')
if 0x232B in present:
    p = path(present[0x232B]); b = p.bounds
    check(near(b[3] - b[1], CAP, 2) and near(b[2] - b[0], 1.42 * CAP, 4), f'⌫: {b[2] - b[0]:.0f} by {b[3] - b[1]:.0f}')
    sp = spans(p, y=CC); check(len(sp) == 3, f'⌫: {len(sp)} spans at mid-height, expected point, cross and side')
print('keyboard: ⌘ ⌥ ⇧ ⏎ ⌫ as designed')

# ---- 5. italic -------------------------------------------------------------------------------
if ITALIC and 0x2460 in present:
    p = path(present[0x2460])
    lo, hi = spans(p, y=CC - 90), spans(p, y=CC - 10)                   # both through the one's stem, above its foot and under its flag
    if len(lo) >= 3 and len(hi) >= 3:
        check(near(mid(hi[1]) - mid(lo[1]), K * 80, 6), f'①: figure stem shift {mid(hi[1]) - mid(lo[1]):.0f} over 80, expected {K * 80:.0f}')
    else: check(False, f'①: spans {lo} / {hi}')
    print('italic: the pictures stand upright, the figures lean')

# ---- 7. more geometric shapes (issue 33) -----------------------------------------------------------
def T(p, m):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q


def xor_area(a, b):
    """The area two outlines do not share (by a fine scanline count; 0 when they are equal)."""
    q = pathops.op(a, b, pathops.PathOp.XOR); bb = q.bounds
    if not bb or bb[2] - bb[0] < 0.5: return 0.0
    tot = 0.0
    for i in range(int(bb[1]), int(bb[3]) + 1, 2):
        tot += 2 * sum(width(s) for s in spans(q, y=i + 0.5))
    return tot


def outer(p):
    """p's outer contour filled (the contour with the widest bounds)."""
    cs = sorted(p.contours, key=lambda c: -(c.bounds[2] - c.bounds[0]) * (c.bounds[3] - c.bounds[1]))
    q = pathops.Path(); cs[0].draw(q.getPen()); return pathops.op(q, q, pathops.PathOp.UNION)


def same(a, b, what):                                                    # equal within about a unit along the outline
    b0 = a.bounds; per = 2 * ((b0[2] - b0[0]) + (b0[3] - b0[1]))
    d = xor_area(a, b); check(d <= 1.5 * per, f'{what}: outlines differ by {d:.0f} square units (allowed {1.5 * per:.0f})')


def centred(p):                                                          # p with its box centred on the origin
    b = p.bounds; return T(p, (1, 0, 0, 1, -(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2))


NEW33 = {0x25B2: '▲', 0x25B3: '△', 0x25BC: '▼', 0x25BD: '▽', 0x25C0: '◀', 0x25C1: '◁', 0x25B7: '▷',
         0x25B4: '▴', 0x25B5: '▵', 0x25BE: '▾', 0x25BF: '▿', 0x25C2: '◂', 0x25C3: '◃', 0x25B9: '▹',
         0x25C6: '◆', 0x2606: '☆', 0x25AA: '▪', 0x25AB: '▫', 0x25E6: '◦', 0x25EF: '◯', 0x25CC: '◌'}
gdef = f['GDEF'].table.GlyphClassDef.classDefs
for u, ch in NEW33.items():
    if u not in cmap: check(False, f'U+{u:04X} {ch} unmapped'); continue
    g = cmap[u]; check(path(g).bounds is not None and hmtx[g][0] > 0, f'{g}: no ink or no advance')
    check(gdef.get(g) == 1, f'{g}: GDEF class {gdef.get(g)}, not 1 (base)')
    for feats in (None, APP):
        names = shape('a' + ch + 'b', feats); check(len(names) == 3 and names[1] == g, f'a{ch}b shapes to {names} (features {feats})')
    b = hb.Buffer(); b.add_str('AV' + ch + 'VA7' + ch + '7'); b.guess_segment_properties(); hb.shape(hbfont, b, {})
    check(all(p.x_advance == hmtx[hbfont.get_glyph_name(i.codepoint)][0] and p.x_offset == 0 for i, p in zip(b.glyph_infos, b.glyph_positions)
              if i.codepoint == f.getGlyphID(g)), f'{ch}: kerned or moved beside A V 7')
G = {u: cmap.get(u) for u in list(NEW33) + [0x25B6, 0x25B8, 0x25A0, 0x25A1, 0x25CB, 0x2605, 0x25C7, 0x2022]}
have = lambda *us: all(G.get(u) for u in us)
adv = lambda u: hmtx[G[u]][0]
P = lambda u: path(G[u])
inr_tri = lambda u: (P(u).bounds[2] - P(u).bounds[0]) / (2 * math.sqrt(3))   # ▲ ▼: the width is the side


def stroke_of(u):                                                        # a white shape's stroke: the lowest span on its vertical centre line
    p = P(u); b = p.bounds; sp = spans(p, x=(b[0] + b[2]) / 2); return width(sp[0]) if sp else 0


for big in (True, False):
    r_, l_, u_, d_ = (0x25B6, 0x25C0, 0x25B2, 0x25BC) if big else (0x25B8, 0x25C2, 0x25B4, 0x25BE)
    wr, wl, wu, wd = (0x25B7, 0x25C1, 0x25B3, 0x25BD) if big else (0x25B9, 0x25C3, 0x25B5, 0x25BF)
    if not have(r_, l_, u_, d_, wr, wl, wu, wd): continue
    rb, ub = P(r_).bounds, P(u_).bounds; cy = (rb[1] + rb[3]) / 2
    same(centred(P(l_)), centred(T(P(r_), (-1, 0, 0, 1, 0, 0))), f'{NEW33[l_]} against ▶/▸ mirrored')
    same(P(d_), T(P(u_), (1, 0, 0, -1, 0, 2 * cy)), f'{NEW33[d_]} against {NEW33[u_]} turned over')
    same(centred(P(u_)), centred(T(P(r_), (0, 1, -1, 0, 0, 0))), f'{NEW33[u_]} against ▶/▸ turned a quarter')
    check(near((ub[1] + ub[3]) / 2, cy, 1), f'{NEW33[u_]}: centred at {(ub[1] + ub[3]) / 2:.0f}, ▶/▸ at {cy:.0f}')
    check(adv(l_) == adv(r_) and adv(wl) == adv(r_) and adv(wr) == adv(r_), f'◀ ◁ ▷: advances {adv(l_)} {adv(wl)} {adv(wr)} against {adv(r_)}')
    check(adv(d_) == adv(u_) == adv(wu) == adv(wd), f'▲ ▼ △ ▽ advances {adv(u_)} {adv(d_)} {adv(wu)} {adv(wd)}')
    check(all(near(hmtx[G[v]][1], hmtx[G[r_]][1], 1) for v in (l_, u_, d_)), f'{NEW33[u_]} {NEW33[d_]} {NEW33[l_]}: left sidebearings against {hmtx[G[r_]][1]}')
    sw = min(US, 0.5 * inr_tri(u_))
    for b_, w_ in ((r_, wr), (l_, wl), (u_, wu), (d_, wd)):
        same(outer(P(w_)), P(b_), f'{NEW33[w_]}\'s outline against {chr(b_)}')
        check(len(list(P(w_).contours)) == 2, f'{NEW33[w_]}: {len(list(P(w_).contours))} contours, expected 2')
    s = stroke_of(wu); check(near(s, sw, 2), f'{NEW33[wu]}: stroke {s:.1f} against {sw:.1f} (the crossbar {US:.0f} up to half the inradius)')
    if big: check(near(ub[1], CC - (ub[3] - ub[1]) / 2, 1) and near(ub[3] - ub[1], (rb[3] - rb[1]) * math.sqrt(3) / 2, 3), f'▲: {ub}')
if have(0x25C6, 0x25C7):
    same(P(0x25C6), outer(P(0x25C7)), '◆ against ◇\'s outline'); check(adv(0x25C6) == adv(0x25C7), f'◆: advance {adv(0x25C6)}, ◇ {adv(0x25C7)}')
if have(0x2606, 0x2605):
    same(outer(P(0x2606)), P(0x2605), '☆\'s outline against ★'); check(adv(0x2606) == adv(0x2605), f'☆: advance {adv(0x2606)}, ★ {adv(0x2605)}')
    check(len(list(P(0x2606).contours)) == 2, f'☆: {len(list(P(0x2606).contours))} contours')
    sb_ = P(0x2605).bounds; R5 = (sb_[2] - sb_[0]) / (2 * math.sin(math.radians(72)))
    tip, vx = (0, R5), (0.382 * R5 * math.cos(math.radians(126)), 0.382 * R5 * math.sin(math.radians(126)))
    s_inr = abs(tip[0] * vx[1] - tip[1] * vx[0]) / math.hypot(vx[0] - tip[0], vx[1] - tip[1])   # the centre to an edge's line
    sk = 0.09 * CAP; want = min(US if US <= sk else sk + 0.15 * (US - sk), 0.8 * s_inr)
    sp = spans(P(0x2606), x=(sb_[0] + sb_[2]) / 2)                       # the lowest span: the stroke at the bottom inner corner,
    st = width(sp[0]) * s_inr / (0.382 * R5) if sp else 0                # along the corner's ray, at sin = s_inr / r off the edges
    check(near(st, want, 2), f'☆: stroke {st:.1f} against {want:.1f} (the crossbar {US:.0f} up to {sk:.0f}, 0.15 of the rest)')
    if have(0x25B3):
        check(st >= 0.6 * stroke_of(0x25B3), f'☆: stroke {st:.1f} under 0.6 of △\'s {stroke_of(0x25B3):.1f}')
    inner = sorted(P(0x2606).contours, key=lambda c: (c.bounds[2] - c.bounds[0]))[0].bounds
    check(inner[2] - inner[0] >= 0.33 * (sb_[2] - sb_[0]), f'☆: inner star {inner} under a third of ★\'s width')
if have(0x25AA, 0x25AB, 0x25A0):
    b = P(0x25AA).bounds
    check(near(b[2] - b[0], 0.62 * CAP, 1) and near(b[3] - b[1], 0.62 * CAP, 1) and near((b[1] + b[3]) / 2, 235, 1), f'▪: {b}, expected 0.62 of the cap height on 235')
    same(outer(P(0x25AB)), P(0x25AA), '▫\'s outline against ▪'); check(adv(0x25AA) == adv(0x25AB), '▪ ▫ advances')
    s = stroke_of(0x25AB); check(near(s, min(US, 0.155 * CAP), 2), f'▫: stroke {s:.1f} against {min(US, 0.155 * CAP):.1f}')
if have(0x25E6, 0x2022):
    same(outer(P(0x25E6)), P(0x2022), '◦\'s outline against •'); check(adv(0x25E6) == adv(0x2022), f'◦: advance {adv(0x25E6)}, • {adv(0x2022)}')
    b = P(0x2022).bounds; sp = spans(P(0x25E6), y=(b[1] + b[3]) / 2); bd = min(b[2] - b[0], b[3] - b[1]); bk = 0.28 * bd
    bs = min(US if US <= bk else bk + 0.5 * (US - bk), bd / 3)           # the crossbar, half its growth past 0.28 of the bullet
    check(len(sp) == 2 and all(near(width(s), bs, 3) for s in sp), f'◦: spans {sp} against {bs:.1f}')
    check(len(sp) == 2 and sp[1][0] - sp[0][1] >= bd / 3 - 2, f'◦: counter {sp[1][0] - sp[0][1] if len(sp) == 2 else 0:.0f} under a third of the bullet {bd:.0f}')
if have(0x25EF, 0x25CB):
    b, bo = P(0x25EF).bounds, P(0x25CB).bounds
    check(near(b[3] - b[1], 1.125 * (bo[3] - bo[1]), 3) and near((b[1] + b[3]) / 2, CC, 2), f'◯: {b} against ○ {bo}')
    sp = spans(P(0x25EF), y=CC); check(len(sp) == 2 and all(near(width(s), US, 2) for s in sp), f'◯: spans {sp} against {US:.0f}')
if have(0x25CC):
    cs = list(P(0x25CC).contours); b = P(0x25CC).bounds; cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    check(len(cs) == 12, f'◌: {len(cs)} dots, expected 12')
    ds = [c.bounds for c in cs]                                          # within 2: the reslant's rounding
    dw = [d[2] - d[0] for d in ds]; dh = [d[3] - d[1] for d in ds]
    check(max(dw) - min(dw) <= 2 and max(dh) - min(dh) <= 2 and max(abs(w - h) for w, h in zip(dw, dh)) <= 2, f'◌: dots {sorted(set(map(round, dw)))} by {sorted(set(map(round, dh)))}')
    rr = sorted(math.hypot((d[0] + d[2]) / 2 - cx, (d[1] + d[3]) / 2 - cy) for d in ds)
    an = sorted(math.degrees(math.atan2((d[1] + d[3]) / 2 - cy, (d[0] + d[2]) / 2 - cx)) % 360 for d in ds)
    check(rr[-1] - rr[0] <= 2 and all(near((an[(i + 1) % 12] - an[i]) % 360, 30, 0.6) for i in range(12)), f'◌: dot radii {rr[0]:.1f}..{rr[-1]:.1f}, angles {[round(a) for a in an]}')
    check(near(b[3], 480, 2) and near(b[3] - b[1], 0.93 * 470, 2), f'◌: {b}, expected 0.93 of the x-height with its top at 480')
# across the seven weights of this slant (full mode, when they are beside this font): ☆ and ◦
# gain ink at every step, and keep their contour count (the variable font interpolates them)
if MODE == 'full':
    d_ = os.path.dirname(os.path.abspath(PATH))
    W7 = ['Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']
    sibs = [os.path.join(d_, f'TorchletteSans-{({"Regular": "Italic"}.get(w, w + "Italic") if ITALIC else w)}.ttf') for w in W7]
    if all(os.path.exists(q) for q in sibs):
        fs7 = [TTFont(q, lazy=True) for q in sibs]
        for u in (0x2606, 0x25E6):
            g = cmap.get(u)
            if not g or not all(g in f_.getGlyphOrder() for f_ in fs7): check(False, f'U+{u:04X}: missing in a weight'); continue
            areas = []
            for f_ in fs7:
                gs_ = f_.getGlyphSet(); q = pathops.Path(); gs_[g].draw(q.getPen(glyphSet=gs_)); q.simplify(); areas.append(abs(q.area))
            check(all(a < b_ for a, b_ in zip(areas, areas[1:])), f'{chr(u)}: ink across the weights {[round(a) for a in areas]}, not growing at every step')
            counts = [f_['glyf'][g].numberOfContours for f_ in fs7]
            check(len(set(counts)) == 1, f'{chr(u)}: contours across the weights {counts}')
        print('issue 33 shapes: ☆ and ◦ ink and contours compared across the seven weights')
print('issue 33 shapes: triangles, ◆ ☆ ▪ ▫ ◦ ◯ ◌ as designed')

# ---- 6. metrics --------------------------------------------------------------------------------
present.update({u: cmap[u] for u in NEW33 if u in cmap})
for u, g in present.items():
    b = path(g).bounds
    check(b[3] <= os2.sTypoAscender and b[1] >= os2.sTypoDescender and b[3] <= os2.usWinAscent and b[1] >= -os2.usWinDescent,
          f'{g}: bounds {b} leave the vertical metrics')
print('metrics: all within typo and win')

if fails: sys.exit(1)
print(f'[verify_ui OK] {STYLE} {MODE}: {checks} checks passed.')

"""HarfBuzz and outline check of the currency module.

    verify_currency.py FONT STYLE full|subset

1. Coverage: each of ₿ ₪ ₾ ₨ shapes to its own glyph (uniXXXX), with ink, a positive
   advance, GDEF class 1 (base), inside the hhea ascender and descender. The web subset
   keeps them all (U+20A0-20CF).
2. Composition, on the outlines unslanted (an italic's are sheared back about y = 252, as
   the build draws them), each against the glyphs it is made from:
   - ₿ is on the figure width (the zero's advance, as $ and €), three contours, its ink
     from the $'s bottom to its top (within 2); above cap height and below the baseline,
     two strokes each the $'s stroke wide (within 3), standing at the same places above
     and below (within 1.5), the left one flush with the B's stem; the B between them is
     as tall as the B.
   - ₪ is two contours from the baseline to cap height, wider than the figure width; at
     mid-height four stems of one width (within 2), each at least 0.9 of the ₽'s stem
     (which is the H's: so it cannot drift light again), and three counters of one width
     (within 3: an italic's reslant rounds), at least as wide as €'s bars are apart (less
     2); its bars at least 0.9 of the ₽'s bowl top; its ink no narrower than the H's.
   - ₾ is one contour, from the baseline to the $'s top (within 2), narrower than the O
     (ink and advance); its bowl between 0.95 and 1.3 of €'s ink width (1.02 where the
     strokes fit, wider in the heavy weights), its sides €'s side weight (within 4), a bar
     along the baseline as wide as the bowl (within 2); above cap height two strokes the $'s
     stroke wide, centred on the bowl (within 2), which run down inside it to its middle
     with white beside each at least 0.3 of €'s bar gap.
   - ₨ is R and s exactly, the s moved in: advance under R + s typed, the outline R and the
     s at (advance less the s's), the contours R's and s's (they do not touch).
   On the full font, with the other weights of the same slant beside it, each glyph has
   the same number of contours at every weight (for the variable font).
3. Like Mulish's currency signs, they have no small capitals or case forms and are not
   kerned: smcp and case leave them alone, and ₿0 ₪1 ₾7 ₨1 A₿ get no kerning.
"""
import os
import sys

import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept  # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
ITALIC = 'Italic' in STYLE
K, YC = (0.1587 if ITALIC else 0.0), 252

tt = TTFont(PATH)
GO = tt.getGlyphOrder(); HAVE = set(GO)
GS = tt.getGlyphSet(); HMTX = tt['hmtx'].metrics
GDEF = tt['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in tt else {}
HB = hb.Font(hb.Face(hb.Blob.from_file_path(PATH)))
fails, checks = [], 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties()
    hb.shape(HB, b, feats or {})
    return [(GO[i.codepoint], p.x_advance) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def outline(g, dx=0):
    """g's outline, unslanted, moved by dx."""
    p = pathops.Path()
    GS[g].draw(TransformPen(p.getPen(glyphSet=GS), (1, 0, -K, 1, K * YC + dx, 0)))
    p.simplify()
    return p


def area(p): return abs(p.area)
def ncont(p): return len(list(p.contours))
def W(g): return HMTX[g][0]


def hspans(p, y):
    box = pathops.Path(); pen = box.getPen()
    pen.moveTo((-3000, y - 0.5)); pen.lineTo((5000, y - 0.5)); pen.lineTo((5000, y + 0.5)); pen.lineTo((-3000, y + 0.5)); pen.closePath()
    return sorted((c.bounds[0], c.bounds[2]) for c in pathops.op(p, box, pathops.PathOp.INTERSECTION).contours)


def vspans(p, x):
    box = pathops.Path(); pen = box.getPen()
    pen.moveTo((x - 0.5, -3000)); pen.lineTo((x + 0.5, -3000)); pen.lineTo((x + 0.5, 5000)); pen.lineTo((x - 0.5, 5000)); pen.closePath()
    return sorted((c.bounds[1], c.bounds[3]) for c in pathops.op(p, box, pathops.PathOp.INTERSECTION).contours)


def union(*ps):
    out = ps[0]
    for q in ps[1:]: out = pathops.op(out, q, pathops.PathOp.UNION)
    return out


NAMES = {0x20BF: 'uni20BF', 0x20AA: 'uni20AA', 0x20BE: 'uni20BE', 0x20A8: 'uni20A8'}

# ---- 1. coverage ---------------------------------------------------------------------
asc, desc = tt['hhea'].ascent, tt['hhea'].descent
ok = {}
for cp, name in NAMES.items():
    s = shape(chr(cp))
    good = len(s) == 1 and s[0][0] == name
    check(good, f'U+{cp:04X} shapes to {s}, want {name}')
    if not good: continue
    p = outline(name); b = p.bounds
    fine = area(p) > 0 and W(name) > 0 and b[1] >= desc and b[3] <= asc
    check(fine, f'{name}: ink {b}, advance {W(name)}, outside {desc}..{asc} or empty')
    check(GDEF.get(name) == 1, f'{name}: GDEF class {GDEF.get(name)}, want 1')
    ok[name] = fine

def have(*gs): return all(g in HAVE and ok.get(g, True) for g in gs)

# ---- 2. composition ------------------------------------------------------------------
cap = outline('H').bounds[3]
dl = outline('dollar'); db = dl.bounds
d_stroke = (lambda s: s[1] - s[0])(hspans(dl, (cap + db[3]) / 2)[0])
FIG = W('zero')
eu = outline('Euro'); eb = eu.bounds
ebars = vspans(eu, eb[0] + 0.08 * (eb[2] - eb[0]))
e_gap = ebars[1][0] - ebars[0][1] if len(ebars) == 2 else None
check(e_gap is not None, f'Euro: bars {ebars}, want two')
e_side = (lambda s_: s_[0][1] - s_[0][0])(hspans(eu, cap / 2))
rp = outline('uni20BD'); rpb = rp.bounds
r_stem = (lambda s_: s_[1] - s_[0])(hspans(rp, 0.12 * cap)[0])
r_top = (lambda v: v[1] - v[0])(vspans(rp, rpb[0] + 0.45 * (rpb[2] - rpb[0]))[-1])

if have('uni20BF'):
    n = 'uni20BF'; p = outline(n); b = p.bounds
    check(W(n) == FIG, f'{n}: advance {W(n)}, want the figure width {FIG}')
    check(ncont(p) == 3, f'{n}: {ncont(p)} contours, want 3')
    check(abs(b[3] - db[3]) <= 2 and abs(b[1] - db[1]) <= 2, f'{n}: ink {b[1]:.0f}..{b[3]:.0f}, the $ {db[1]:.0f}..{db[3]:.0f}')
    up, dn = hspans(p, (cap + db[3]) / 2), hspans(p, db[1] / 2)
    check(len(up) == 2 and len(dn) == 2, f'{n}: strokes above {up}, below {dn}, want two each')
    if len(up) == 2 and len(dn) == 2:
        for a, c in up + dn:
            check(abs((c - a) - d_stroke) <= 3, f'{n}: a stroke {c - a:.0f} wide, the $\'s {d_stroke:.0f}')
        for (a, c), (a2, c2) in zip(up, dn):
            check(abs(a - a2) <= 1.5 and abs(c - c2) <= 1.5, f'{n}: strokes above {up} and below {dn} not aligned')
        stem = hspans(p, 0.25 * cap)[0]
        check(abs(up[0][1] - stem[1]) <= 1.5, f'{n}: the left stroke {up[0]} not flush with the stem {stem}')
    # the B runs from the baseline to cap height: wide there, and only the strokes beyond
    wide = lambda y: max((c - a for a, c in hspans(p, y)), default=0)
    check(wide(2) > 2.5 * d_stroke and wide(cap - 2) > 2.5 * d_stroke and wide(cap + 3) < 1.5 * d_stroke
          and wide(-3) < 1.5 * d_stroke, f'{n}: the B is not from the baseline to cap height {cap:.0f}')

if have('uni20AA') and e_gap:
    n = 'uni20AA'; p = outline(n); b = p.bounds; hb_ = outline('H').bounds
    check(ncont(p) == 2, f'{n}: {ncont(p)} contours, want 2 (two hooks)')
    check(abs(b[1]) <= 1 and abs(b[3] - cap) <= 1, f'{n}: ink {b[1]:.0f}..{b[3]:.0f}, want 0..{cap:.0f}')
    check((b[2] - b[0]) >= (hb_[2] - hb_[0]) - 3, f'{n}: ink {b[2] - b[0]:.0f} wide, narrower than the H\'s {hb_[2] - hb_[0]:.0f}')
    check(W(n) > FIG, f'{n}: advance {W(n)}, not wider than the figure width {FIG}')
    sp = hspans(p, cap / 2)
    check(len(sp) == 4, f'{n}: {len(sp)} stems at mid-height, want 4')
    if len(sp) == 4:
        ws = [c - a for a, c in sp]; gs_ = [sp[i + 1][0] - sp[i][1] for i in range(3)]
        check(max(ws) - min(ws) <= 2, f'{n}: stems {ws} uneven')
        check(min(ws) >= 0.9 * r_stem, f'{n}: stems {ws}, under 0.9 of the ₽\'s {r_stem:.0f}: lighter than its kin')
        check(max(gs_) - min(gs_) <= 3, f'{n}: counters {gs_} uneven')
        check(min(gs_) >= e_gap - 2, f'{n}: counters {gs_}, tighter than €\'s bar gap {e_gap:.0f}')
    tops = vspans(p, (b[0] + b[2]) / 2)                     # the bottom bar and the top bar, in the middle
    check(len(tops) == 2 and min(c - a for a, c in tops) >= 0.9 * r_top,
          f'{n}: bars {tops}, under 0.9 of the ₽\'s bowl top {r_top:.0f}')

if have('uni20BE') and e_gap:
    n = 'uni20BE'; p = outline(n); b = p.bounds; ob = outline('O').bounds
    check(ncont(p) == 1, f'{n}: {ncont(p)} contours, want 1')
    check(abs(b[1]) <= 1 and abs(b[3] - db[3]) <= 2, f'{n}: ink {b[1]:.0f}..{b[3]:.0f}, want 0..{db[3]:.0f}')
    check(W(n) < W('O') and b[2] - b[0] < ob[2] - ob[0], f'{n}: advance {W(n)}, ink {b[2] - b[0]:.0f}, not narrower than the O ({W("O")}, {ob[2] - ob[0]:.0f})')
    mid = hspans(p, cap / 2 + 15)                            # just above the bowl's middle: side, stroke, stroke, side
    check(len(mid) == 4, f'{n}: at mid-height {mid}, want the bowl\'s two sides and the two strokes between')
    if len(mid) == 4:
        bw = mid[3][1] - mid[0][0]
        ratio = bw / (eb[2] - eb[0])
        check(0.95 <= ratio <= 1.3, f'{n}: bowl {bw:.0f} wide, {ratio:.2f} of €\'s ink {eb[2] - eb[0]:.0f}, want 0.95..1.3')
        check(abs((mid[0][1] - mid[0][0]) - e_side) <= 4, f'{n}: bowl side {mid[0]}, €\'s side {e_side:.0f}')
        bar = hspans(p, 3)
        check(len(bar) == 1 and abs(bar[0][0] - mid[0][0]) <= 2 and abs(bar[0][1] - mid[3][1]) <= 2,
              f'{n}: baseline bar {bar}, the bowl {mid[0][0]:.0f}..{mid[3][1]:.0f}')
        check(min(mid[1][0] - mid[0][1], mid[3][0] - mid[2][1]) >= 0.3 * e_gap,
              f'{n}: inside the bowl {mid}, want white beside each stroke >= {0.3 * e_gap:.0f}')
        up = hspans(p, (cap + db[3]) / 2)
        check(len(up) == 2 and all(abs((c - a) - d_stroke) <= 3 for a, c in up), f'{n}: strokes above {up}, want two {d_stroke:.0f} wide')
        check(len(up) == 2 and all(abs(u[0] - m[0]) <= 1.5 and abs(u[1] - m[1]) <= 1.5 for u, m in zip(up, mid[1:3])),
              f'{n}: strokes above {up} and inside the bowl {mid[1:3]} not one pair of uprights')
        check(abs((mid[1][0] + mid[2][1]) / 2 - (mid[0][0] + mid[3][1]) / 2) <= 2, f'{n}: strokes {mid[1:3]} not centred on the bowl')

if have('uni20A8'):
    n = 'uni20A8'; p = outline(n); dx = W(n) - W('s')
    check(W(n) < W('R') + W('s'), f'{n}: advance {W(n)}, not under R + s ({W("R") + W("s")})')
    d = area(pathops.op(p, union(outline('R'), outline('s', dx)), pathops.PathOp.XOR)) / max(area(p), 1)
    check(d < 0.01, f'{n}: not R and s at {dx} ({d:.3%} differs)')
    check(ncont(p) == ncont(outline('R')) + ncont(outline('s')), f'{n}: R and s touch ({ncont(p)} contours)')

# the same contours at every weight of this slant (the variable font interpolates them)
if MODE == 'full':
    d = os.path.dirname(os.path.abspath(PATH))
    W7 = ['Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']
    sibs = [({'Regular': 'Italic'}.get(w, w + 'Italic') if ITALIC else w) for w in W7]
    paths = [os.path.join(d, f'TorchletteSans-{s}.ttf') for s in sibs]
    if all(os.path.exists(q) for q in paths):
        fonts = [TTFont(q, lazy=True) for q in paths]
        for g in NAMES.values():
            counts = [f['glyf'][g].numberOfContours if g in f.getGlyphOrder() else None for f in fonts]
            check(len(set(counts)) == 1, f'{g}: contours across the {"italic" if ITALIC else "upright"} weights {counts}')

# ---- 3. no forms, no kerning, as their kin -------------------------------------------
for feat in ('smcp', 'case'):
    if not kept(feat): continue
    for cp, name in NAMES.items():
        if not have(name): continue
        s = shape(chr(cp), {feat: 1})
        check(len(s) == 1 and s[0][0] == name, f'{feat} U+{cp:04X}: {s}, want {name} (its kin have no {feat} form)')
for text in ('₿0', '₪1', '₾7', '₨1', 'A₿', '1₪'):
    if not all(have(NAMES[ord(ch)]) for ch in text if ord(ch) in NAMES): continue
    s = shape(text)
    check(len(s) == 2 and s[0][1] == W(s[0][0]), f'{text!r}: kerned ({s}); Mulish\'s currency signs are not')

print(f'currency {STYLE} {MODE}: {checks - len(fails)}/{checks} checks passed')
for f in fails[:40]:
    print('  FAIL', f)
sys.exit(1 if fails else 0)

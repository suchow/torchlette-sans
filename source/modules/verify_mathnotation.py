"""Checks of the mathnotation module.

    verify_mathnotation.py FONT STYLE full|subset

1. Coverage: every character of the module shapes under HarfBuzz, alone and between letters,
   to its own glyph with ink and a positive advance. In the web subset a character outside
   the Makefile's UNICODES ranges may be absent; every one inside them must be there; the
   full font has them all.
2. Cmap: every Unicode subtable that maps a code point of the module maps it to the same glyph,
   and the best one keeps the whole (3,1) format 4 mapping.
3. ML1 accents (mark): ŷ θ̂ x̄ μ̃ ẋ ẍ and the five accents on every Greek letter the font has,
   on ℓ and on the letterlike capitals: the mark is moved by GPOS, its ink centre sits over
   the base's ink centre at the mark's height (allowing the italic's slant) within 22% of the
   base's ink width, and its ink clears the base's top. After a capital the mark is a .case form.
4. ML4 ccmp: ⫫ + U+0338 and ⊥ + U+0338 become one slashed glyph.
5. ML9 calt: in "king : man ∷ queen : woman" and "a:b∷c:d" both colons become U+2236; a colon
   in a line without ∷ stays a colon.
6. SH4 calt + kern: in ⟨ψ|φ⟩ the bar is bar.braket.mathnotation, which lies within the angle
   brackets' height; ⟨q and k⟩ are kerned closer than unkerned, and the ink gap of ⟨q is within
   30 units of the gap of (q.
7. Shapes: relations and operators sit in the 600-unit cell, but ⊘ ⊛ ⊖ have ⊕'s advance (720) and are as wide and tall as
   ⊕ (within 12: the shipped ⊕ comes out 10 narrower in Black); ≺ mirrors ≻ (uprights); the 29 script characters, including ℒ, use fixed normal-script Noto Sans
   Math outlines at one H-cap/714 scale, with donor-scaled advances and base glyph class.
   Donor-affine versus saved bounds are diagnostics, not equality claims across the ordinary
   rounding/G1/once-italic finishing stages. Those stages are checked separately.
   the double-struck capitals show at least four strokes on a scanline through their stems;
   each double-struck glyph has the contour count of its design (symbols.doublestruck after
   Noto Sans Math: one per counter of a doubled stroke, crescent and letter, so a counter that
   pinched shut or split at some weight shows); and every double-struck glyph is thin strokes only (all its ink lies within a thin stroke
   tv of its edge, so a counter filled in solid shows): no more than 0.25 tv² of its ink lies
   further than 1.15 tv (+ 4 units) from its edge, tv the width of 𝕀's strokes at
   mid-height. The depth is measured on a 4-unit raster of the outline (its own scanlines
   and distance transform, no path operations: skia-pathops' contour ordering is what fails).
8. Nothing leaves the typo or win vertical metrics.
"""
import os
import hashlib
import io
import re
import sys

import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from webfeatures import kept  # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']; os2 = f['OS/2']
order = set(f.getGlyphOrder())
face = hb.Face(hb.Blob.from_file_path(PATH)); hbfont = hb.Font(face)
ITALIC = STYLE.endswith('Italic'); K = 0.1587 if ITALIC else 0.0
fails = 0; checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('[verify_mathnotation FAIL]', *msg)


def run(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(hbfont, b, feats or {})
    return [hbfont.get_glyph_name(i.codepoint) for i in b.glyph_infos], b.glyph_positions


def shape(text, feats=None): return run(text, feats)[0]


def bounds(g):
    p = BoundsPen(gs); gs[g].draw(p); return p.bounds


def path(g):
    p = pathops.Path(); gs[g].draw(p.getPen(glyphSet=gs)); return p


def hspans(p, y):
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((-3000, y - 0.5)); pen.lineTo((5000, y - 0.5)); pen.lineTo((5000, y + 0.5)); pen.lineTo((-3000, y + 0.5)); pen.closePath()
    return sorted((c.bounds[0], c.bounds[2]) for c in pathops.op(p, r, pathops.PathOp.INTERSECTION).contours)


# the web subset's ranges, from the Makefile
mk = open(os.path.join(os.path.dirname(HERE), 'Makefile')).read()
ranges = []
for part in re.search(r'^UNICODES := (.*)$', mk, re.M).group(1).split(','):
    a, _, b = part.strip()[2:].partition('-')
    ranges.append((int(a, 16), int(b or a, 16)))
in_web = lambda u: any(a <= u <= b for a, b in ranges)

OPS = [0x225C, 0x225D, 0x2250, 0x2259, 0x2AEB, 0x2298, 0x229B, 0x2296, 0x229E, 0x229F, 0x22A0, 0x22A1, 0x22C8,
       0x227A, 0x227B, 0x227C, 0x227D, 0x2AAF, 0x2AB0, 0x2236, 0x2237, 0x25C9]
SCRIPT = [0x1D49C, 0x212C, 0x1D49E, 0x1D49F, 0x2130, 0x2131, 0x1D4A2, 0x210B, 0x2110, 0x1D4A5, 0x1D4A6, 0x2112, 0x2133,
          0x1D4A9, 0x1D4AA, 0x1D4AB, 0x1D4AC, 0x211B, 0x1D4AE, 0x1D4AF, 0x1D4B0, 0x1D4B1, 0x1D4B2, 0x1D4B3,
          0x1D4B4, 0x1D4B5, 0x212F, 0x210A, 0x2134]
DS = [0x1D538, 0x1D539, 0x1D53B, 0x1D53D, 0x1D53E, 0x1D540, 0x1D541, 0x1D542, 0x1D543, 0x1D544, 0x1D546,
      0x1D54A, 0x1D54B, 0x1D54C, 0x1D54D, 0x1D54E, 0x1D54F, 0x1D550, 0x1D7D8] + list(range(0x1D7DA, 0x1D7E2))
ALL = OPS + SCRIPT + DS
# the contours of each double-struck glyph's design: its outline, and one per counter
DS_CONTOURS = dict(zip(DS, [3, 6, 4, 2, 3, 2, 2, 3, 2, 3, 4, 3, 2, 2, 2, 3, 2, 2, 4, 2, 3, 3, 3, 4, 2, 7, 4]))

# 1. coverage
for u in ALL:
    if MODE == 'subset' and not in_web(u):
        continue
    ch = chr(u)
    if u not in cmap:
        check(False, f'U+{u:04X} {ch} not in the cmap'); continue
    g = cmap[u]
    for text in (ch, f'x{ch}y'):
        names = shape(text)
        check(g in names, f'U+{u:04X} {text!r} shapes to {names}, not {g}')
    b = bounds(g)
    check(b is not None and b[2] > b[0], f'{g} has no ink')
    check(hmtx[g][0] > 0, f'{g} has no advance')

# 2. cmap consistency
mapped = {u for u in ALL if u in cmap}
for t in f['cmap'].tables:
    if not t.isUnicode(): continue
    for u in mapped:
        if u in t.cmap: check(t.cmap[u] == cmap[u], f'cmap ({t.platformID},{t.platEncID}) maps U+{u:04X} to {t.cmap[u]}, best to {cmap[u]}')
f4 = next((t for t in f['cmap'].tables if (t.platformID, t.platEncID, t.format) == (3, 1, 4)), None)
if f4: check(all(cmap.get(u) == g for u, g in f4.cmap.items()), 'the best cmap lost part of the (3,1) format 4 mapping')

# 3. accents
MARKS = '̂̃̄̇̈'
bases = ''.join(ch for ch in 'yxθμ' if ord(ch) in cmap) + ''.join(chr(u) for u in list(range(0x3B1, 0x3CA)) + list(range(0x391, 0x3AA)) + [0x3D1, 0x3D5, 0x3F5, 0x3D6, 0x2113, 0x2112, 0x210B, 0x1D49F, 0x1D4A9, 0x1D53C]
                    if u in cmap and u != 0x3A2)
if kept('mark', 'ccmp'):
    nacc = 0
    for bch in bases:
        if MODE == 'subset' and not in_web(ord(bch)): continue
        for m in MARKS:
            names, pos = run(bch + m)
            if len(names) != 2: continue                  # composed to a precomposed letter
            nacc += 1
            bb, mb = bounds(names[0]), bounds(names[1])
            if mb is None: check(False, f'{bch}+U+{ord(m):04X}: empty mark {names[1]}'); continue
            moved = pos[1].x_offset != 0 or pos[1].y_offset != 0
            check(moved, f'{bch}+U+{ord(m):04X} {names}: mark not positioned')
            mx = pos[0].x_advance + pos[1].x_offset + (mb[0] + mb[2]) / 2
            my = pos[1].y_offset + (mb[1] + mb[3]) / 2
            bc = (bb[0] + bb[2]) / 2 + K * (my - (bb[1] + bb[3]) / 2)
            if bch in 'ιζξλ': continue                  # the anchor stands over the x-height part, not the ink box
            if 'SCRIPT' in __import__('unicodedata').name(bch, ''):
                # a script capital's box holds its swashes: the mark must stand over the ink of its upper part
                pb = path(names[0]); ys = [bb[3] - 0.35 * (bb[3] - bb[1]) + i * 10 for i in range(int(0.35 * (bb[3] - bb[1]) / 10))]
                xs = [x for y in ys for sp in hspans(pb, y) for x in sp]
                check(xs and min(xs) - 40 <= mx - K * (my - bb[3]) <= max(xs) + 40, f'{bch}+U+{ord(m):04X}: mark centre {mx:.0f} not over the upper ink')
                continue
            check(abs(mx - bc) <= 0.22 * (bb[2] - bb[0]) + 8, f'{bch}+U+{ord(m):04X}: mark centre {mx:.0f} off the base axis {bc:.0f}')
            check(pos[1].y_offset + mb[1] >= bb[3] - 30, f'{bch}+U+{ord(m):04X}: mark bottom {pos[1].y_offset + mb[1]} into the base (top {bb[3]})')
            import unicodedata
            if unicodedata.category(bch) == 'Lu' or 'CAPITAL' in unicodedata.name(bch, ''):
                check(names[1].endswith('.case'), f'{bch}+U+{ord(m):04X}: capital takes {names[1]}, not a .case mark')
    check(nacc >= 20, f'only {nacc} accent pairs tested')

# 4. ccmp negation
if kept('ccmp'):
    for t, want in (('⫫̸', 'uni2AEB.not.mathnotation'), ('⊥̸', 'uni22A5.not.mathnotation')):
        if MODE == 'subset' and not all(in_web(ord(ch)) for ch in t): continue
        if ord(t[0]) not in cmap: continue
        check(shape(t) == [want], f'{t!r} shapes to {shape(t)}, not {want}')

# 5. ratio colon
if kept('calt') and (MODE == 'full' or in_web(0x2237)):
    n = shape('king : man ∷ queen : woman')
    check(n.count('uni2236') == 2 and 'colon' not in n, f'analogy colons: {n}')
    n = shape('a:b∷c:d')
    check(n.count('uni2236') == 2, f'a:b∷c:d colons: {n}')
    check('colon' in shape('ratio: a : b') and 'uni2236' not in shape('ratio: a : b'), 'a colon without ∷ changed')

# 6. bra-ket
if kept('calt'):
    n = shape('⟨ψ|φ⟩' if 0x3C8 in cmap else '⟨a|b⟩')
    check('bar.braket.mathnotation' in n, f'⟨ψ|φ⟩ shapes to {n}')
    bb, br = bounds('bar.braket.mathnotation'), bounds('uni27E8')
    check(bb[1] >= br[1] - 1 and bb[3] <= br[3] + 1, f'bar.braket {bb} outside the bracket {br}')
    check('bar' in shape('a|b'), 'a plain | changed')
if kept('kern'):
    for t in ('⟨q', 'k⟩'):
        _, pos = run(t)
        _, pos0 = run(t, {'kern': False})
        check(pos[0].x_advance < pos0[0].x_advance, f'{t!r} not kerned ({pos[0].x_advance} vs {pos0[0].x_advance})')
    def gap(a, b):
        names, pos = run(a + b)
        pa, pb = path(names[0]), path(names[1]); gs_ = []
        for y in range(0, 700, 12):
            sa, sb = hspans(pa, y), hspans(pb, y)
            if sa and sb: gs_.append(pos[0].x_advance - sa[-1][1] + sb[0][0])
        return min(gs_)
    check(abs(gap('⟨', 'q') - gap('(', 'q')) <= 30, f'⟨q gap {gap(chr(0x27E8), "q")} vs (q {gap("(", "q")}')

# 7. shapes
H = path('H'); Hb = H.bounds; CH = Hb[3]
def g_of(u): return cmap.get(u)
for u in (0x225C, 0x225D, 0x2250, 0x2259, 0x2AEB, 0x227A, 0x227B, 0x227C, 0x227D, 0x2AAF, 0x2AB0):
    g = g_of(u)
    if g: check(hmtx[g][0] == 600, f'U+{u:04X} advance {hmtx[g][0]}, not 600')
for u in (0x2298, 0x229B, 0x2296):                          # ⊘ ⊛ ⊖ share ⊕'s ring and advance
    g = g_of(u)
    if g and g_of(0x2295): check(hmtx[g][0] == hmtx[g_of(0x2295)][0], f'U+{u:04X} advance {hmtx[g][0]}, ⊕ {hmtx[g_of(0x2295)][0]}')
if g_of(0x2295):
    ob = bounds(g_of(0x2295))
    for u in (0x2298, 0x229B, 0x2296):
        g = g_of(u)
        if g:
            b = bounds(g)
            check(all(abs(a - c) <= 12 for a, c in zip(b, ob)), f'U+{u:04X} bounds {b} vs ⊕ {ob}')
if g_of(0x227A) and g_of(0x227B) and not ITALIC:            # a sheared pair is no mirror image
    a, b = bounds(g_of(0x227A)), bounds(g_of(0x227B))
    check(abs(a[0] - (600 - b[2])) <= 2 and abs(a[1] - b[1]) <= 1, f'≺ {a} does not mirror ≻ {b}')
# Fixed donor script ownership: no custom pen, stroke-width, weight-growth or
# contour-count laws. Ordinary finishing changes geometry; raw affine bounds below
# are diagnostics only, without an invented saved-outline tolerance or PASS claim.
SCRIPT_DONOR_SHA256 = '3f495fe933c06786e4d5f6d86b8ee70b6753a68ee3b9d87528726de0f6e2c47d'
check(len(SCRIPT) == 29 and len(set(SCRIPT)) == 29 and 0x2112 in SCRIPT,
      'fixed script repertoire must contain all 29 characters, including ℒ')
donor_resource = os.path.join(os.path.dirname(HERE), 'notosansmath', 'NotoSansMath-Regular.ttf')
with open(donor_resource, 'rb') as donor_file:
    donor_bytes = donor_file.read()
check(hashlib.sha256(donor_bytes).hexdigest() == SCRIPT_DONOR_SHA256, 'fixed script donor hash mismatch')
if hashlib.sha256(donor_bytes).hexdigest() == SCRIPT_DONOR_SHA256:
    with TTFont(io.BytesIO(donor_bytes), recalcTimestamp=False) as donor:
        donor_cmap = donor.getBestCmap()
        check(donor['OS/2'].sCapHeight == 714, 'fixed script donor cap height is not 714')
        check(all(u in donor_cmap for u in SCRIPT), 'fixed donor lacks a script codepoint')
        scale = CH / 714
        glyph_classes = (getattr(f['GDEF'].table, 'GlyphClassDef', None) if 'GDEF' in f else None)
        classes = glyph_classes.classDefs if glyph_classes is not None else {}
        for u in SCRIPT:
            g = g_of(u)
            if not g or u not in donor_cmap:
                continue  # The existing full/subset coverage policy above still applies.
            advance = round(donor['hmtx'][donor_cmap[u]][0] * scale)
            check(hmtx[g][0] == advance, f'{chr(u)}: advance {hmtx[g][0]}, donor-scaled {advance}')
            check(classes.get(g) == 1, f'{chr(u)}: GDEF class {classes.get(g)}, expected base class 1')
            pen = BoundsPen(donor.getGlyphSet())
            donor.getGlyphSet()[donor_cmap[u]].draw(TransformPen(
                pen, (scale, 0, K * scale, scale, -K * 252, 0)))
            print(f'script diagnostic U+{u:04X}: donor affine bounds {pen.bounds}; saved {bounds(g)}; '
                  'ordinary grid/G1/once-italic phase differences are not asserted here')
for u in DS:
    g = g_of(u)
    if not g: continue
    p = path(g); b = p.bounds
    most = max(len(hspans(p, y)) for y in (b[3] * 0.3, b[3] * 0.5, b[3] * 0.7))
    check(most >= 2, f'{chr(u)}: at most {most} strokes on a scanline (no doubled stroke)')
    n = f['glyf'][g].numberOfContours
    check(n == DS_CONTOURS[u], f'{chr(u)}: {n} contours, not {DS_CONTOURS[u]} (a counter closed or split)')
class _Polys(BasePen):
    """A glyph's contours as polygons (curves cut into 8 lines each)."""
    def __init__(self, glyphset): super().__init__(glyphset); self.polys = []
    def _moveTo(self, p): self.polys.append([p])
    def _lineTo(self, p): self.polys[-1].append(p)
    def _qCurveToOne(self, p1, p2):
        p0 = self.polys[-1][-1]
        self.polys[-1].extend(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                               (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / 8 for i in range(1, 9)))
    def _curveToOne(self, p1, p2, p3):
        p0 = self.polys[-1][-1]
        self.polys[-1].extend(tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d
                                    for a, b, c, d in zip(p0, p1, p2, p3)) for t in (i / 8 for i in range(1, 9)))


def _edt1(f):
    """Squared distance transform of one row (Felzenszwalb and Huttenlocher)."""
    n = len(f); d = [0.0] * n; v = [0] * n; z = [0.0] * (n + 1); k = 0; z[0], z[1] = -1e20, 1e20
    for q in range(1, n):
        while True:
            s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k])
            if s > z[k]: break
            k -= 1
        k += 1; v[k] = q; z[k] = s; z[k + 1] = 1e20
    k = 0
    for q in range(n):
        while z[k + 1] < q: k += 1
        d[q] = (q - v[k]) ** 2 + f[v[k]]
    return d


def deep_ink(g, r, res=4):
    """The area of g's ink (nonzero fill, sampled every res units) further than r from its edge."""
    pen = _Polys(gs); gs[g].draw(pen)
    edges = [(p[i - 1], p[i]) for p in pen.polys for i in range(len(p)) if p[i - 1][1] != p[i][1]]
    b = bounds(g); x0, y0 = b[0] - 2 * res, b[1] - 2 * res
    nx, ny = int((b[2] - x0) / res) + 3, int((b[3] - y0) / res) + 3
    inf = 1e20; grid = []
    for j in range(ny):
        y = y0 + (j + 0.5) * res
        xs = sorted((a[0] + (y - a[1]) * (c[0] - a[0]) / (c[1] - a[1]), 1 if c[1] > a[1] else -1)
                    for a, c in edges if min(a[1], c[1]) <= y < max(a[1], c[1]))
        row = [0.0] * nx; w = 0; i = 0
        for col in range(nx):
            x = x0 + (col + 0.5) * res
            while i < len(xs) and xs[i][0] <= x: w += xs[i][1]; i += 1
            if w: row[col] = inf
        grid.append(row)
    rows = [_edt1(row) for row in grid]                                    # across, then down
    deep = 0
    for col in range(nx):
        for d in _edt1([rows[j][col] for j in range(ny)]):
            if d * res * res > r * r: deep += 1
    return deep * res * res


if g_of(0x1D540):
    pI = path(g_of(0x1D540)); bI = pI.bounds
    tv = sorted(s[1] - s[0] for s in hspans(pI, (bI[1] + bI[3]) / 2))[0]
    for u in DS:
        g = g_of(u)
        if not g: continue
        deep = deep_ink(g, 1.15 * tv + 4)
        check(deep < 0.25 * tv * tv, f'{chr(u)}: {deep:.0f} u2 of ink more than 1.15 x {tv:.0f} from its edge (a counter filled in?)')

# 8. vertical metrics
hhea = f['hhea']
for u in ALL:
    g = g_of(u)
    if not g: continue
    b = bounds(g)
    check(b[3] <= max(os2.usWinAscent, hhea.ascent) and b[1] >= -max(os2.usWinDescent, -hhea.descent),
          f'{g} {b} outside the win/hhea metrics')

print(f'verify_mathnotation {STYLE} {MODE}: {checks} checks, {fails} failures')
sys.exit(1 if fails else 0)

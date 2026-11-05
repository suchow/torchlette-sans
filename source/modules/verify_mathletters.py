"""Checks of the mathletters module: ℙ ℍ 𝔼 𝟙 ℏ ∥ ∖ ⟂ ⟦ ⟧ ⋆ and the format 12 cmap.

    verify_mathletters.py FONT STYLE full|subset

1. Coverage: each of the eleven characters shapes under HarfBuzz, alone and between letters,
   with no features and with the app's (ss01 ss02 ss16 onum pnum), to its own glyph with ink.
   In the web subset 𝔼 and 𝟙 (outside the BMP) may be absent while the Makefile's UNICODES
   leaves them out; every BMP character must be there.
2. Cmap: the full font has a (3,10) format 12 subtable that maps every code point of the (3,1)
   format 4 subtable to the same glyph and maps U+1D53C and U+1D7D9; a subset that keeps them
   has a format 12 subtable too.
3. Double-struck (symbols.doublestruck, after Noto Sans Math): on a scanline through the
   stem, ℙ 𝔼 𝟙 show two hairlines of one width (within 3) with a counter of at least 0.9 x
   67/53 of a hairline between them (Noto's gap), ℍ four; the hairline is ℝ's (uni211D,
   when the symbols module is present) within 3, and between 0.33 and 0.62 of H's stem. ℙ ℍ
   𝔼 stand on the baseline at the cap height, 𝟙 at the one's; every doubled stroke is
   closed at its ends (ℙ's stem is one span at the baseline, ℍ's two stems two spans at both
   ends, 𝔼 closed by its arms, 𝟙 by its foot); none is narrower than its plain letter nor
   more than 1.45 times as wide; each has its design's contour count (ℙ 4, ℍ 3, 𝔼 2, 𝟙 2).
4. ℏ is an h plus a bar: the ink beyond the h's is a bar at least 0.6 of h's ink width,
   centred on the stem (where the bar crosses it) within 40, slanted (taller than two
   crossbars, shorter than half the ascender). When the font has the math italic h (U+210E),
   mathglyphs rebuilds ℏ on it, as math fonts draw ℏ (Latin Modern, STIX: an italic h with a
   slanted bar), so that h is the reference, aligned on its foot; that ℏ has a left
   sidebearing of at least 35 (iℏ collided) and an advance no narrower than ℎ's. Without
   U+210E, ℏ is mathletters' upright h with the bar and h's advance. ℒ belongs to mathnotation's fixed Noto Sans Math script repertoire.
5. Operators: ∥ is two bars of |'s width (within 2) and height; ∖ leans like the backslash;
   ⟂ has the up tack's bar on the baseline and its stem centred in 600; ⟦ has two stems and
   ⟧ mirrors it; ⋆ is one contour centred on the math axis within 6.
6. Italic styles: ℙ's stem moves right between heights 100 and 600 by the italic's slant
   (0.1587 of the rise, within 10): the letters lean, like the other math glyphs.
7. Nothing leaves the typo or win vertical metrics.
"""
import sys

import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']; glyf = f['glyf']; os2 = f['OS/2']
face = hb.Face(hb.Blob.from_file_path(PATH)); hbfont = hb.Font(face)
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
ITALIC = STYLE.endswith('Italic'); K = 0.1587
fails = 0; checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('[verify_mathletters FAIL]', *msg)


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


def bounds(g): return path(g).bounds
def width(s): return s[1] - s[0]
def mid(s): return (s[0] + s[1]) / 2


CHARS = {0x2119: 'ℙ', 0x210D: 'ℍ', 0x1D53C: '𝔼', 0x1D7D9: '𝟙', 0x210F: 'ℏ', 0x2225: '∥', 0x2216: '∖',
         0x27C2: '⟂', 0x27E6: '⟦', 0x27E7: '⟧', 0x22C6: '⋆'}
MAY_MISS = {0x1D53C, 0x1D7D9} if MODE == 'subset' else set()

# ---- 1. coverage -------------------------------------------------------------------------
present = {}
for u, ch in CHARS.items():
    if u not in cmap:
        check(u in MAY_MISS, f'U+{u:04X} {ch} unmapped')
        if u in MAY_MISS: print(f'  (U+{u:04X} {ch} not in the web subset; outside the Makefile UNICODES)')
        continue
    g = cmap[u]; present[u] = g
    check(bounds(g) is not None and hmtx[g][0] > 0, f'{g}: no ink or no advance')
    for feats in (None, APP):
        check(shape(ch, feats) == [g], f'{ch} shapes to {shape(ch, feats)}, not [{g}] (features {feats})')
        names = shape('a' + ch + 'b', feats)
        check(len(names) == 3 and names[1] == g, f'a{ch}b shapes to {names} (features {feats})')
print(f'coverage: {len(present)} of {len(CHARS)} characters mapped and shaping')

# ---- 2. cmap ------------------------------------------------------------------------------
tables = {(t.platformID, t.platEncID, t.format): t for t in f['cmap'].tables}
if MODE == 'full' or 0x1D53C in present:
    t12 = tables.get((3, 10, 12))
    check(t12 is not None, 'no (3,10) format 12 cmap subtable')
    if t12 is not None:
        t4 = tables.get((3, 1, 4))
        if t4 is not None:
            bad = [u for u, g in t4.cmap.items() if t12.cmap.get(u) != g]
            check(not bad, f'format 12 subtable disagrees with format 4 at {[hex(u) for u in bad[:10]]}')
        for u in (0x1D53C, 0x1D7D9):
            if u in present: check(t12.cmap.get(u) == present[u], f'format 12 subtable lacks U+{u:04X}')
    print('cmap: format 12 subtable present and consistent with format 4')

# ---- 3. double-struck ------------------------------------------------------------------------
CAP = bounds('H')[3]
minus = path('minus'); BAR = width(spans(minus, x=300)[0])
ds_ref = width(spans(path(cmap[0x211D]), y=CAP * 0.15)[0]) if 0x211D in cmap else None


STEM = width(spans(path('H'), y=CAP * 0.25)[0])
CONTOURS = {0x2119: 4, 0x210D: 3, 0x1D53C: 2, 0x1D7D9: 2}


def doubled(g, y, n_strokes, what):
    sp = spans(path(g), y=y)
    check(len(sp) >= n_strokes, f'{what}: {len(sp)} spans at y={y:.0f}, expected {n_strokes}')
    if len(sp) < 2: return
    a, b = sp[0], sp[1]
    check(abs(width(a) - width(b)) <= 3, f'{what}: strokes {width(a):.1f} and {width(b):.1f} differ')
    gap = b[0] - a[1]
    check(gap >= 0.9 * width(a) * 67 / 53, f'{what}: counter {gap:.1f} too narrow for hairlines {width(a):.1f}')
    check(0.33 * STEM <= width(a) <= 0.62 * STEM, f'{what}: hairline {width(a):.1f} against the stem {STEM:.1f}')
    if ds_ref is not None: check(abs(width(a) - ds_ref) <= 3, f'{what}: stroke {width(a):.1f} differs from ℝ\'s {ds_ref:.1f}')
    if n_strokes == 4 and len(sp) >= 4:
        check(abs(width(sp[2]) - width(a)) <= 3 and abs(width(sp[3]) - width(a)) <= 3, f'{what}: right stem strokes differ')


for u, plain, y_frac in ((0x2119, 'P', 0.15), (0x210D, 'H', 0.15), (0x1D53C, 'E', 0.3), (0x1D7D9, 'one', 0.5)):
    if u not in present: continue
    g = present[u]; b = bounds(g); pb = bounds(plain)
    doubled(g, CAP * y_frac, 4 if u == 0x210D else 2, CHARS[u])
    check(abs(b[1]) <= 2 and abs(b[3] - pb[3]) <= 2, f'{CHARS[u]}: bounds {b[1]:.0f}..{b[3]:.0f}, plain {pb[1]:.0f}..{pb[3]:.0f}')
    w, pw = b[2] - b[0], pb[2] - pb[0]
    # in the italic a hairline foot leans out less than the plain letter's heavier one
    check(pw - 2 - (0.03 * pw if ITALIC else 0) <= w <= 1.45 * pw + 2, f'{CHARS[u]}: width {w:.0f} against {plain}\'s {pw:.0f}')
    check(hmtx[g][0] >= hmtx[plain][0], f'{CHARS[u]}: advance {hmtx[g][0]} under {plain}\'s {hmtx[plain][0]}')
    n = f['glyf'][g].numberOfContours
    check(n == CONTOURS[u], f'{CHARS[u]}: {n} contours, not {CONTOURS[u]} (a counter closed or split)')
if 0x2119 in present:
    check(len(spans(path(present[0x2119]), y=6)) == 1, 'ℙ: stem not closed at the baseline')
if 0x210D in present:
    check(len(spans(path(present[0x210D]), y=6)) == 2 and len(spans(path(present[0x210D]), y=CAP - 6)) == 2, 'ℍ: stems not closed at both ends')
if 0x1D53C in present:
    sp = spans(path(present[0x1D53C]), y=6); check(len(sp) == 1, f'𝔼: bottom arm does not close the stem ({len(sp)} spans)')
    sp = spans(path(present[0x1D53C]), y=CAP - 6); check(len(sp) == 1, f'𝔼: top arm does not close the stem ({len(sp)} spans)')
if 0x1D7D9 in present:
    sp = spans(path(present[0x1D7D9]), y=6); check(len(sp) == 1, f'𝟙: foot does not close the stem ({len(sp)} spans)')
print(f'double-struck: hairlines against the stem {STEM:.1f}' + (f' and ℝ\'s {ds_ref:.1f}' if ds_ref else ''))

# ---- 4. ℏ (script ℒ is verified by mathnotation) -----------------------------------------------
if 0x210F in present:
    ref = cmap.get(0x210E) or 'h'
    hb_ = path(present[0x210F]); h = path(ref)
    if ref != 'h':                                            # align ℎ on ℏ by the stem's foot
        dx = spans(hb_, y=8)[0][0] - spans(h, y=8)[0][0]
        q = pathops.Path(); from fontTools.pens.transformPen import TransformPen
        path(ref).draw(TransformPen(q.getPen(), (1, 0, 0, 1, dx, 0))); h = q
    hbb = h.bounds
    fat = pathops.Path(h); fat.stroke(6, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4); fat.convertConicsToQuads(); fat.simplify()
    fat = pathops.op(h, fat, pathops.PathOp.UNION)                  # h grown by 3, so the italic's rounding slivers go
    bar = pathops.op(hb_, fat, pathops.PathOp.DIFFERENCE); bb = bar.bounds
    check(bb is not None, 'ℏ: no bar beyond h')
    if bb:
        stem = spans(h, y=hbb[3] * 0.85 if ref == 'h' else mid((bb[1], bb[3])))[0]
        hw = width(path('h').bounds[0::2])                       # the upright h's ink width
        check(bb[2] - bb[0] >= 0.6 * hw, f'ℏ: bar {bb[2] - bb[0]:.0f} wide against h\'s {hw:.0f}')
        check(abs(mid((bb[0], bb[2])) - mid(stem)) <= 40 + (K * 300 if ITALIC else 0), f'ℏ: bar centred at {mid((bb[0], bb[2])):.0f}, stem at {mid(stem):.0f}')
        Hb_ = path('H').bounds; H_BAR = width(spans(path('H'), x=(Hb_[0] + Hb_[2]) / 2)[0])
        check(2 * H_BAR < bb[3] - bb[1] < 0.5 * hbb[3], f'ℏ: bar {bb[1]:.0f}..{bb[3]:.0f} not slanted as expected (crossbar {H_BAR:.0f})')
        check(bb[3] <= hbb[3] - 5, f'ℏ: bar reaches {bb[3]:.0f}, above the ascender {hbb[3]:.0f}')
        if ref == 'h':
            check(hmtx[present[0x210F]][0] == hmtx['h'][0], 'ℏ: advance differs from h')
        else:
            check(hmtx[present[0x210F]][1] >= 35, f'ℏ: left sidebearing {hmtx[present[0x210F]][1]}')
            check(hmtx[present[0x210F]][0] >= hmtx[ref][0], f'ℏ: advance {hmtx[present[0x210F]][0]}, ℎ {hmtx[ref][0]}')
    print(f'ℏ: {ref} with a slanted bar')

# ---- 5. operators -----------------------------------------------------------------------------
if 0x2225 in present:
    p = path(present[0x2225]); bw = width(spans(path('bar'), y=300)[0]); sp = spans(p, y=300); bb = p.bounds; barb = bounds('bar')
    check(len(sp) == 2 and all(abs(width(s) - bw) <= 2 for s in sp), f'∥: spans {sp} against |\'s width {bw:.0f}')
    check(len(sp) == 2 and sp[1][0] - sp[0][1] >= 50, f'∥: gap {sp[1][0] - sp[0][1] if len(sp) == 2 else None}')
    check(abs(bb[1] - barb[1]) <= 1 and abs(bb[3] - barb[3]) <= 1, f'∥: height {bb[1]:.0f}..{bb[3]:.0f} against |\'s {barb[1]:.0f}..{barb[3]:.0f}')
if 0x2216 in present:
    p = path(present[0x2216]); lo, hi = spans(p, y=100), spans(p, y=600)
    check(len(lo) == 1 and len(hi) == 1 and mid(hi[0]) < mid(lo[0]), f'∖: not a backslash ({lo}, {hi})')
if 0x27C2 in present:
    p = path(present[0x27C2]); base = spans(p, y=BAR / 2); stem = spans(p, y=300)
    lean = K * (BAR / 2 - 252) if ITALIC else 0
    check(len(base) == 1 and abs(base[0][0] - 70 - lean) <= 2 and abs(base[0][1] - 530 - lean) <= 2, f'⟂: bar {base}')
    check(len(stem) == 1 and abs(mid(stem[0]) - 300 - (K * (300 - 252) if ITALIC else 0)) <= 3, f'⟂: stem {stem}')
    check(hmtx[present[0x27C2]][0] == 600, '⟂: advance not 600')
if 0x27E6 in present and 0x27E7 in present:
    l, r = path(present[0x27E6]), path(present[0x27E7]); adv = hmtx[present[0x27E6]][0]
    sl, sr = spans(l, y=300), spans(r, y=300)
    check(len(sl) == 2 and abs(width(sl[0]) - width(sl[1])) <= 2, f'⟦: spans {sl}')
    check(len(spans(l, y=CAP - 10)) == 1, '⟦: top arm missing')
    if ITALIC:
        check(len(sr) == 2, f'⟧: spans {sr}')
    else:
        check(len(sr) == 2 and all(abs((adv - b_) - a_[0]) <= 1.5 and abs((adv - a_s) - a_[1]) <= 1.5 for a_, (a_s, b_) in zip(sl, sr[::-1])),
              f'⟧ does not mirror ⟦: {sl} vs {sr} in {adv}')
    check(hmtx[present[0x27E7]][0] == adv, '⟧: advance differs from ⟦')
if 0x22C6 in present:
    p = path(present[0x22C6]); b = p.bounds
    axis = mid(spans(minus, x=300)[0])
    check(abs((b[1] + b[3]) / 2 - axis) <= 6, f'⋆: centre {(b[1] + b[3]) / 2:.0f} off the axis {axis:.0f}')
    check(len(list(p.contours)) == 1 and 0.45 * 600 <= b[2] - b[0] <= 0.8 * 600, f'⋆: {len(list(p.contours))} contours, {b[2] - b[0]:.0f} wide')
print('operators: ∥ ∖ ⟂ ⟦ ⟧ ⋆ as designed')

# ---- 6. italic lean ----------------------------------------------------------------------------
if ITALIC and 0x2119 in present:
    p = path(present[0x2119]); lo, hi = spans(p, y=100)[0], spans(p, y=600)[0]
    check(abs((lo[0] - hi[0]) + K * 500) <= 10, f'ℙ: stem shift {hi[0] - lo[0]:.0f} over 500, expected {K * 500:.0f}')
    print('italic: the letters lean with the slant')

# ---- 7. metrics --------------------------------------------------------------------------------
for u, g in present.items():
    b = bounds(g)
    check(b[3] <= os2.sTypoAscender and b[1] >= os2.sTypoDescender and b[3] <= os2.usWinAscent and b[1] >= -os2.usWinDescent,
          f'{g}: bounds {b} leave the vertical metrics')
print('metrics: all within typo and win')

if fails: sys.exit(1)
print(f'[verify_mathletters OK] {STYLE} {MODE}: {checks} checks passed.')

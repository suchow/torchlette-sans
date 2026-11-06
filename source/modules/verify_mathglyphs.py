"""Check the mathglyphs module.

    verify_mathglyphs.py <font.ttf> <style> full|subset

1. ∬ ∭ ∮ ∯ ⋃ ⋂ ℵ and U+20D7 are mapped to uni222C uni222D uni222E uni222F uni22C3
   uni22C2 uni2135 uni20D7 (math_table refers to these names), have ink, and shape
   with HarfBuzz to themselves; U+20D7 is a zero-advance mark (GDEF class 3).
2. ∬ and ∭ are ∫ repeated: their advances are ∫'s plus one and two equal pitches, and
   their ink is as tall as ∫'s; ∮ has ∫'s advance; ⋃ and ⋂ span ∑'s height.
3. ∞ is at least 1.45 x-heights wide and centred on the math axis (the minus's centre)
   within 3 units; ⊕ ⊗ ⊙ are at least 1.2 x-heights across. ∪ ∩ are at least 1.15
   x-heights wide and 1.25 tall (TeX's: 1.26 x 1.40). ss14 (where the font keeps it) maps
   + − = ≤ × ⋅ ∈ to *.ss14.mathglyphs, at least 1.18 times as wide, on the same centre,
   + with the same stem; without ss14 they stay the text forms.
4. U+005E is a low hat: its visible ink starts at least 60 above the x-height, is at
   most 200 tall, 0.55 to 0.70 x-heights wide (TeX's is 0.62) and centred in its advance.
5. The accents asciicircum dotaccent uni02C9 macron dieresis uni20D7 and hat.w1..w5.mathglyphs
   (in the subset once math_table's MATH table lists them) end with an inkless
   contour: two points, no area, under the visible ink by the module's gap, inside its
   horizontal extent.
6. ′ and ″ are slanted wedges (wider at the top than at the foot, the centreline moving
   right by over 60 from foot to top), ″ is two of them; the
   ssty feature (where the font keeps it) maps ′ ″ ‴ to *.ssty.mathglyphs, whose ink
   starts below y 200.
7. ν's left stroke is near upright (its outer edge moves under 0.25 x-heights from
   x-height to foot, v's 40 more). γ is one contour with no counter: its arms apart
   somewhere between 0.4 and 0.9 x-heights, and below the baseline one upright stroke
   (its centre moves under 25) that thickens from a neck toward its end.
8. ℏ (when present) has a left sidebearing of at least 35; ∏'s stems are heavier than n's.
9. A relation + U+0338 shapes to symbols' precomposed negation, which ss14 grows where it
   grows the base; ss14's → ↦ ↔ are 1000, 1000, 1100 wide; U+0338's ink is left of 0.
10. ⨀ ⨁ ⨂ ⨄ ⨆ ∐ ⋀ ⋁ span most of ∑'s height and (where MATH is kept) have a 1430 display
   variant; → ↔ ⟶ ⇌ ↦ ⇒ ⟹ ↓ ⇕ have stretchy constructions with at most 20 variants
   (Chrome reads no more).
"""
import os
import sys

import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept   # noqa: E402

path, style, mode = sys.argv[1], sys.argv[2], sys.argv[3]
tt = TTFont(path); order = tt.getGlyphOrder(); cmap = tt.getBestCmap(); gs = tt.getGlyphSet()
glyf, hmtx = tt['glyf'], tt['hmtx']
hfont = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
fails, checks = [], 0
GAP = {'asciicircum': 90, 'dotaccent': 75, 'uni02C9': 80, 'macron': 80, 'dieresis': 75, 'uni20D7': 70}
GAP.update({f'hat.w{i}.mathglyphs': 90 for i in range(1, 6)})
XH = tt['OS/2'].sxHeight
K = 0.1587 if 'Italic' in style else 0.0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


def P(name):
    p = pathops.Path(); gs[name].draw(p.getPen(glyphSet=gs)); return p


def unslant(p):
    """The outline with the italic's lean taken out (about y 252), so stems can be measured upright."""
    if not K: return p
    q = pathops.Path()
    from fontTools.pens.transformPen import TransformPen
    p.draw(TransformPen(q.getPen(), (1, 0, -K, 1, K * 252, 0)))
    return q


def spans(p, y):
    b = p.bounds
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((b[0] - 10, y)); pen.lineTo((b[2] + 10, y)); pen.lineTo((b[2] + 10, y + 0.5)); pen.lineTo((b[0] - 10, y + 0.5)); pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION)
    return sorted((c.bounds[0], c.bounds[2]) for c in q.contours)


def visible(name):
    """Bounds of a glyph's contours that have area (the inkless contour left out)."""
    g = glyf[name]; coords, ends, _ = g.getCoordinates(glyf)
    xs, ys, s0 = [], [], 0
    for e in ends:
        pts = list(coords[s0:e + 1]); s0 = e + 1
        if len(pts) > 2:
            xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(hfont, b, feats or {})
    return [order[i.codepoint] for i in b.glyph_infos]


# 1. the new code points
NEW = {0x222C: 'uni222C', 0x222D: 'uni222D', 0x222E: 'uni222E', 0x222F: 'uni222F', 0x22C3: 'uni22C3',
       0x22C2: 'uni22C2', 0x2135: 'uni2135', 0x20D7: 'uni20D7'}
classes = tt['GDEF'].table.GlyphClassDef.classDefs
for cp, n in NEW.items():
    ok(cmap.get(cp) == n, f'U+{cp:04X} maps to {cmap.get(cp)}, not {n}')
    if n not in order: continue
    ok(glyf[n].numberOfContours > 0, f'{n} has no outline')
    ok(shape(chr(cp)) == [n], f'U+{cp:04X} shapes to {shape(chr(cp))}')
    ok(classes.get(n) == (3 if cp == 0x20D7 else 1), f'{n} GDEF class {classes.get(n)}')
ok(hmtx['uni20D7'][0] == 0, 'U+20D7 has an advance')

# 2. the integrals and the n-ary set operators
wi = hmtx['integral'][0]; p1 = hmtx['uni222C'][0] - wi; p2 = hmtx['uni222D'][0] - hmtx['uni222C'][0]
ok(p1 > 100 and p1 == p2, f'integral pitches {p1} {p2}')
ok(hmtx['uni222E'][0] == wi and hmtx['uni222F'][0] == wi + p1, 'contour integral advances')
ib = P('integral').bounds
for n in ('uni222C', 'uni222D', 'uni222E', 'uni222F'):
    b = P(n).bounds
    ok(abs(b[1] - ib[1]) <= 1 and abs(b[3] - ib[3]) <= 1, f'{n} height {b[1]}..{b[3]}, integral {ib[1]}..{ib[3]}')
sb = P('summation').bounds
for n in ('uni22C3', 'uni22C2'):
    b = P(n).bounds
    ok(abs(b[1] - sb[1]) <= 2 and abs(b[3] - sb[3]) <= 2, f'{n} height {b[1]}..{b[3]}, summation {sb[1]}..{sb[3]}')

# 3. infinity and the circled operators
mb = P('minus').bounds; axis = (mb[1] + mb[3]) / 2
b = P(cmap[0x221E]).bounds
ok(b[2] - b[0] >= 1.45 * XH, f'∞ is {b[2] - b[0]:.0f} wide')
ok(abs((b[1] + b[3]) / 2 - axis) <= 3, f'∞ centre {(b[1] + b[3]) / 2:.0f}, axis {axis:.1f}')
for cp in (0x2295, 0x2297, 0x2299):
    b = P(cmap[cp]).bounds
    ok(b[3] - b[1] >= 1.2 * XH, f'U+{cp:04X} is {b[3] - b[1]:.0f} across')

# 3b. ∪ ∩ at TeX's size; ss14's larger operators
for n in ('uni222A', 'uni2229'):
    b = P(n).bounds
    ok(b[2] - b[0] >= 1.15 * XH and b[3] - b[1] >= 1.25 * XH, f'{n} ink {b[2] - b[0]:.0f}x{b[3] - b[1]:.0f}')
if kept('ss14'):
    for ch, n in (('+', 'plus'), ('−', 'minus'), ('=', 'equal'), ('≤', 'lessequal'), ('×', 'multiply'), ('⋅', 'uni22C5'), ('∈', 'uni2208')):
        got = shape(ch, {'ss14': True})
        ok(got == [n + '.ss14.mathglyphs'], f'ss14 {ch}: {got}')
        ok(shape(ch) == [n], f'ss14 applies by default to {ch}')
        if got == [n + '.ss14.mathglyphs']:
            a, b = P(n).bounds, P(got[0]).bounds
            ok(b[2] - b[0] >= 1.18 * (a[2] - a[0]), f'{got[0]} is {b[2] - b[0]:.0f} wide, {n} {a[2] - a[0]:.0f}')
            ok(abs((a[1] + a[3]) / 2 - (b[1] + b[3]) / 2) <= 3, f'{got[0]} moved off its centre')
    pv = spans(unslant(P('plus.ss14.mathglyphs')), (P('plus').bounds[1] + P('plus').bounds[3]) / 2 + 100)
    pv0 = spans(unslant(P('plus')), (P('plus').bounds[1] + P('plus').bounds[3]) / 2 + 100)
    ok(abs((pv[0][1] - pv[0][0]) - (pv0[0][1] - pv0[0][0])) <= 4, f'ss14 + stem {pv} vs + {pv0}')

# 4. the hat
vb = visible('asciicircum')
ok(vb[1] >= XH + 60 and vb[3] - vb[1] <= 200, f'^ visible ink {vb}')
ok(0.55 * XH <= vb[2] - vb[0] <= 0.70 * XH, f'^ is {vb[2] - vb[0]:.0f} wide (TeX: 0.62 x-heights)')
ok(abs((vb[0] + vb[2]) / 2 - hmtx['asciicircum'][0] / 2) <= 3 + (K * 600 if K else 0), '^ is not centred in its advance')

# 5. the inkless contours
for n, gap in GAP.items():
    if n not in order and mode == 'subset' and n.endswith('.mathglyphs'):
        continue                     # kept in the subset only once math_table's MATH lists it
    ok(n in order, f'{n} missing')
    if n not in order: continue
    g = glyf[n]
    if g.isComposite():
        ok(False, f'{n} is a composite'); continue
    coords, ends, _ = g.getCoordinates(glyf)
    last = list(coords[(ends[-2] + 1 if len(ends) > 1 else 0):ends[-1] + 1])
    ok(len(last) == 2 and last[0][1] == last[1][1] and abs(last[0][0] - last[1][0]) <= 1, f'{n}: last contour {last}')
    v = visible(n)
    ok(abs((v[1] - last[0][1]) - gap) <= 2, f'{n}: inkless contour {v[1] - last[0][1]} under the ink, not {gap}')
    ok(v[0] <= last[0][0] <= v[2], f'{n}: inkless contour outside the ink')

# 6. primes
m = unslant(P('minute')); mb_ = m.bounds
top = spans(m, mb_[3] - 15); foot = spans(m, mb_[1] + 15)
ok(len(top) == 1 and len(foot) == 1 and (top[0][1] - top[0][0]) > 1.5 * (foot[0][1] - foot[0][0]), f'′ is not a wedge: {top} {foot}')
ok((top[0][0] + top[0][1]) / 2 > (foot[0][0] + foot[0][1]) / 2 + 60, '′ does not slant')   # its centreline
ok(len(spans(unslant(P('second')), (mb_[1] + mb_[3]) / 2)) == 2, '″ is not two primes')
if kept('ssty'):
    for ch, n in (('′', 'minute'), ('″', 'second'), ('‴', 'uni2034')):
        got = shape(ch, {'ssty': True})
        ok(got == [n + '.ssty.mathglyphs'], f'ssty {ch}: {got}')
        if n + '.ssty.mathglyphs' in order:
            ok(P(n + '.ssty.mathglyphs').bounds[1] < 200, f'{n}.ssty starts at {P(n + ".ssty.mathglyphs").bounds[1]}')
    ok(shape('′') == ['minute'], 'ssty applies by default')

# 7. nu and gamma
def lean(name):
    """How far the left stroke's outer edge moves right from the x-height to the foot (in heavy
    weights the two strokes of ν merge low down, so a span's centre is not the stroke's)."""
    p = unslant(P(name)); lo, hi = spans(p, 0.15 * XH)[0], spans(p, 0.85 * XH)[0]
    return lo[0] - hi[0]
ok(lean('nu') < 0.25 * XH and lean('v') > lean('nu') + 40, f'ν left stroke moves {lean("nu"):.0f}, v {lean("v"):.0f}')
g_ = unslant(P('gamma')); gb_ = g_.bounds
ok(len(list(g_.contours)) == 1, f'γ has {len(list(g_.contours))} contours (a counter in its descender?)')
ok(all(len(spans(g_, y)) == 1 for y in range(round(gb_[1]) + 10, -20, 20)), 'γ descender is not one open stroke')
mid_d = [(lambda s: (s[0][0] + s[0][1]) / 2)(spans(g_, y)) for y in (-40, round(gb_[1]) + 60)]
ok(abs(mid_d[0] - mid_d[1]) < 25, f'γ descender is not upright: centre {mid_d[0]:.0f} -> {mid_d[1]:.0f}')
wd = lambda y: (lambda s: s[0][1] - s[0][0])(spans(g_, y))
neck = min(wd(gb_[1] * f) for f in (0.25, 0.35, 0.45, 0.55))
end = max(wd(gb_[1] * f) for f in (0.70, 0.78, 0.86, 0.94))
ok(end > neck, f'γ descender does not thicken toward its end: neck {neck:.0f}, end {end:.0f}')
arms = max(len(spans(g_, f * XH)) for f in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9))
ok(arms >= 2, 'γ has no open V above its join')

# 8. hbar, product
if 'uni210F' in order:
    ok(hmtx['uni210F'][1] >= 35, f'ℏ left sidebearing {hmtx["uni210F"][1]}')
n_st = spans(unslant(P('n')), 250)[0]; p_st = spans(unslant(P('product')), 300)[0]
ok(p_st[1] - p_st[0] > 1.04 * (n_st[1] - n_st[0]), f'∏ stem {p_st[1] - p_st[0]:.0f}, n {n_st[1] - n_st[0]:.0f}')

# 9. negated relations: base + U+0338 reaches symbols' precomposed glyph (HarfBuzz recomposes),
# which ss14 grows where its base grows; U+0338 itself sits left of its origin, over the glyph
# before it; ss14's arrows are about TeX's 1 em
if 0x2270 in cmap:
    for base, neg in (('≤', '≰'), ('≡', '≢'), ('⊆', '⊈'), ('≺', '⊀'), ('∣', '∤'), ('∼', '≁'), ('→', '↛')):
        ok(shape(base + '̸') == [cmap[ord(neg)]], f'{base}+U+0338 shapes to {shape(base + chr(0x338))}')
    if kept('ss14'):
        for ch in '≰≱≢⊈⊀':
            ok(shape(ch, {'ss14': True}) == [cmap[ord(ch)] + '.ss14.mathglyphs'], f'ss14 {ch}: {shape(ch, {"ss14": True})}')
        for ch, w in (('→', 1000), ('↦', 1000), ('↔', 1100)):
            got = shape(ch, {'ss14': True})
            ok(got == [cmap[ord(ch)] + '.ss14.mathglyphs'] and hmtx[got[0]][0] == w, f'ss14 {ch}: {got}')
if 'uni0338' in order:
    b = P('uni0338').bounds
    ok(b[2] < 0 and b[0] > -650, f'U+0338 ink {b[0]:.0f}..{b[2]:.0f}, not over the glyph before it')

# 10. the n-ary operators drawn here span ∑'s height, and MATH (where kept) gives each a display form
for cp in (0x2A00, 0x2A01, 0x2A02, 0x2A04, 0x2A06, 0x2210, 0x22C0, 0x22C1):
    n = cmap.get(cp)
    ok(n is not None, f'U+{cp:04X} missing')
    if not n: continue
    b = P(n).bounds
    ok(b[1] >= sb[1] - 2 and b[3] <= sb[3] + 2 and b[3] - b[1] >= 0.78 * (sb[3] - sb[1]), f'{n} ink {b[1]:.0f}..{b[3]:.0f}')
if 'MATH' in tt:
    mvar = tt['MATH'].table.MathVariants
    vc = dict(zip(mvar.VertGlyphCoverage.glyphs, mvar.VertGlyphConstruction))
    hc = dict(zip(mvar.HorizGlyphCoverage.glyphs, mvar.HorizGlyphConstruction))
    for cp in (0x2A00, 0x2A01, 0x2A02, 0x2A04, 0x2A06, 0x2210, 0x22C0, 0x22C1):
        n = cmap.get(cp); recs = vc[n].MathGlyphVariantRecord if n in vc else []
        ok([r.AdvanceMeasurement for r in recs] == [885, 1430], f'{n} display variants {[r.AdvanceMeasurement for r in recs]}')
    for cp, table in ((0x2192, hc), (0x2194, hc), (0x27F6, hc), (0x21CC, hc), (0x21A6, hc), (0x21D2, hc), (0x27F9, hc), (0x2193, vc), (0x21D5, vc)):
        n = cmap.get(cp); c_ = table.get(n)
        ok(c_ is not None and c_.GlyphAssembly is not None and 1 < c_.VariantCount <= 20,
           f'U+{cp:04X} {n}: no stretchy construction')

print(f'verify_mathglyphs {style} {mode}: {checks - len(fails)} of {checks} checks passed')
for f in fails: print('FAIL', f)
sys.exit(1 if fails else 0)

"""Check the sigmoid module by shaping with HarfBuzz.

    verify_sigmoid.py <font.ttf> <style> full|subset

With the app's features (ss01 ss02 ss16 onum pnum):
1. "sigmoid" and "sigmoids" (alone, in a sentence, before punctuation) take i.sigmoid for the
   first i only; the s, the second i and every other glyph are the plain ones.
2. Capitalised and longer words are untouched: Sigmoid, SIGMOID, sigmoidal, logsigmoid,
   sigmoidsigmoid, sigma, sigmas, isigmoid; and with ss16 off, "sigmoid" is plain.
3. The ink gaps in "sigmoid" between the s and the sigmoid i and between the i and the g
   (the narrowest horizontal gap at any height) are the approved k2 values, within 3 units.
4. The glyph's outline has no kinks, tiny segments or spurs (outline_check.py's test).
"""
import math
import os
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

path, style, mode = sys.argv[1], sys.argv[2], sys.argv[3]
APP = {'ss01': True, 'ss02': True, 'ss16': True, 'onum': True, 'pnum': True}
GAPS = {'Regular': (111, 142), 'SemiBold': (87, 115), 'Bold': (68, 91)}   # ligature lab 2, round 5, k2
TOL = 3
TOL_ITALIC = 8   # the italic's neighbours (its own s and g) move the gaps 3-5 units from the upright's
fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


tt = TTFont(path); order = tt.getGlyphOrder()
font = hb.Font(hb.Face(hb.Blob.from_file_path(path)))


def shape(text, feats=APP):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(font, b, feats)
    return [order[i.codepoint] for i in b.glyph_infos], b.glyph_positions


def clusters(text, feats=APP):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(font, b, feats)
    return [i.cluster for i in b.glyph_infos]


def plain(text): return shape(text, {k: v for k, v in APP.items() if k != 'ss16'})[0]


ok('i.sigmoid' in order, 'no glyph i.sigmoid')

# 1. the word and its plural, in context
for text, word_at in (('sigmoid', 0), ('sigmoids', 0), ('the sigmoid function', 4), ('sigmoids, and', 0),
                      ('(sigmoid)', 1), ('sigmoid.', 0), ('a sigmoid; two sigmoids', 2)):
    got, cl = shape(text)[0], clusters(text)
    firsts = {k + 1 for k in range(len(text)) if text.startswith('sigmoid', k)}
    seconds = {k + 5 for k in range(len(text)) if text.startswith('sigmoid', k)}
    ok(sorted(c for g, c in zip(got, cl) if g == 'i.sigmoid') == sorted(firsts), f'{text!r}: i.sigmoid at {[c for g, c in zip(got, cl) if g == "i.sigmoid"]}, want {sorted(firsts)}')
    ok(all(g == 'i' for g, c in zip(got, cl) if c in seconds), f'{text!r}: second i changed: {got}')
    ok(all(g == 's' for g, c in zip(got, cl) if c in {f - 1 for f in firsts}), f'{text!r}: the s changed: {got}')
    # everything outside the words is as the font shapes it without the module's rule: compare with
    # the same text where the words are hidden behind a capital S (which the rule ignores)
    other = text.replace('sigmoid', 'Sigmoid')
    og, ocl = shape(other)[0], clusters(other)
    ok([g for g, c in zip(got, cl) if c not in firsts | {f - 1 for f in firsts}] == [g for g, c in zip(og, ocl) if c not in firsts | {f - 1 for f in firsts}],
       f'{text!r}: glyphs outside the first s and i differ from the unaffected text')

# 2. negatives
for text in ('Sigmoid', 'SIGMOID', 'sigmoidal', 'logsigmoid', 'sigmoidsigmoid', 'sigma', 'sigmas', 'isigmoid', 'Sigmoids'):
    got = shape(text)[0]
    ok('i.sigmoid' not in got, f'{text!r} took i.sigmoid: {got}')
ok('i.sigmoid' not in plain('sigmoid'), 'sigmoid changes with ss16 off')
# the rest of ss16 still works next to it
ok(shape('gradient sigmoid')[0][0] == 'g_r_a_d_i_e_n_t.ss11' if 'g_r_a_d_i_e_n_t.ss11' in order else True,
   'gradient logotype lost next to sigmoid')

# 3. ink gaps in "sigmoid"
gs = tt.getGlyphSet()


def spans(name, dx, y):
    rec = DecomposingRecordingPen(gs); gs[name].draw(rec)
    from fontTools.pens.basePen import BasePen
    xs = []

    class Cut(BasePen):                                 # crossings of the outline with the line at y
        def _moveTo(s, p): s.p0 = s.cur = p
        def _lineTo(s, p): s._seg([s.cur, p]); s.cur = p
        def _curveToOne(s, a, b, c): s._seg([s.cur, a, b, c]); s.cur = c
        def _qCurveToOne(s, a, b):
            p0 = s.cur; s._seg([p0, (p0[0] + 2 / 3 * (a[0] - p0[0]), p0[1] + 2 / 3 * (a[1] - p0[1])),
                                (b[0] + 2 / 3 * (a[0] - b[0]), b[1] + 2 / 3 * (a[1] - b[1])), b]); s.cur = b
        def _closePath(s):
            if s.cur != s.p0: s._seg([s.cur, s.p0])
        def _seg(s, P):
            n = 40 if len(P) == 4 else 1
            def at(t):
                if len(P) == 2: return (P[0][0] + t * (P[1][0] - P[0][0]), P[0][1] + t * (P[1][1] - P[0][1]))
                return tuple((1 - t) ** 3 * P[0][k] + 3 * (1 - t) ** 2 * t * P[1][k] + 3 * (1 - t) * t * t * P[2][k] + t ** 3 * P[3][k] for k in (0, 1))
            q = at(0)
            for i in range(1, n + 1):
                r = at(i / n)
                if (q[1] - y) * (r[1] - y) < 0: xs.append(q[0] + (y - q[1]) * (r[0] - q[0]) / (r[1] - q[1]) + dx)
                q = r
    rec.replay(Cut(gs))
    return sorted(xs)


names, pos = shape('sigmoid')
x, origin = 0, []
for p in pos: origin.append(x); x += p.x_advance


def gap(i, j):
    best = math.inf
    for y in range(-240, 760, 3):
        a, b = spans(names[i], origin[i], y + 0.5), spans(names[j], origin[j], y + 0.5)
        if a and b: best = min(best, min(b) - max(a))
    return best


if names[1] == 'i.sigmoid':
    g1, g2 = gap(0, 1), gap(1, 2)
    ok(g1 > 0 and g2 > 0, f'ink overlap in sigmoid: {g1:.0f}, {g2:.0f}')
    # The gaps are horizontal, so an italic is held to its weight's values; but its s and g
    # bring their own edges (Mulish Italic redraws the s), so it gets TOL_ITALIC.
    weight = style.replace('Italic', '') or 'Regular'
    tol = TOL if weight == style else TOL_ITALIC
    if weight in GAPS:
        w1, w2 = GAPS[weight]
        ok(abs(g1 - w1) <= tol, f's to i gap {g1:.0f}, want {w1}')
        ok(abs(g2 - w2) <= tol, f'i to g gap {g2:.0f}, want {w2}')
        print(f'{style} {mode}: ink gaps s-i {g1:.0f} (k2 {w1}), i-g {g2:.0f} (k2 {w2})')
    else:   # no approved k2 value: the gaps must sit between the neighbouring styles'
        lo, hi = {'Light': (GAPS['Regular'], None), 'Medium': (GAPS['SemiBold'], GAPS['Regular']),
                  'ExtraBold': (None, GAPS['Bold']), 'Black': (None, GAPS['Bold'])}[weight]
        for g, k, what in ((g1, 0, 's to i'), (g2, 1, 'i to g')):
            ok((lo is None or g > lo[k] - tol) and (hi is None or g < hi[k] + tol),
               f'{what} gap {g:.0f} outside {lo and lo[k]}..{hi and hi[k]}')
        print(f'{style} {mode}: ink gaps s-i {g1:.0f}, i-g {g2:.0f} (no k2 value; checked between neighbours)')

# 4. the outline
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import outline_check                                      # noqa: E402
if 'i.sigmoid' in order:
    probs = outline_check.check(tt['glyf']['i.sigmoid'], tt['glyf'])
    ok(not probs, f'i.sigmoid outline: {probs}')

for f in fails: print('FAIL', f)
print(f'verify_sigmoid {style} {mode}: {checks} checks, {len(fails)} failures')
sys.exit(1 if fails else 0)

"""sigmoid: the first i of "sigmoid" drawn as a small sigmoid curve (ligature lab 2, sigI3e2, spacing k2).

In the lowercase words "sigmoid" and "sigmoids" the first i becomes `i.sigmoid`: the i's own
stem, run as one rising stroke with a short level foot on the baseline, a gentle rise and a
short level top at the i's height (the stroke is the i's stem width throughout), with the i's
dot over the top. The s and the second i stay plain. Approved by Jordan, 1 Nov 2026
(font-preview/sigmoid-i-round4.html, then round 5, step k2).

Construction, per style, from this style's own i:
- foot and top run T = 58 * (1 + 0.625 * (SV - 1)) units (58 in Regular, about 72 in SemiBold,
  87 in Bold: the heavier stroke eats the tails, so they grow with the stem ratio SV);
- the rise is one cubic 124 units across with level handles (0.58 of that width) at each end,
  so it leaves the foot and meets the top tangentially; the two edges are that curve moved
  up-and-left and down-and-right by half a stroke, the sideways shift solved so the stroke is
  the stem's width where it is thinnest;
- the dot is the i's own dot, centred over the middle of the top run;
- spacing: the lab's sidebearings (70 - T/4 each side), less k2's 20 units per side in
  Regular, scaled with the glyph's advance in the heavier styles (21 SemiBold, 23 Bold).

Layout: one front lookup pair in ss16 (the Torchlette prose ligatures, which the app turns on),
placed right after the ss16 front block so it sees plain letters and the live @S16_WORD class,
with ss16's whole-word guards: no word letter before "sigmoid"/"sigmoids" and none after.
"Sigmoid", "SIGMOID", "sigmoidal", "logsigmoid" and "sigma" are untouched. Nothing is
registered as a new tag; ss16 gains two lookups (SIGMOID_WORD, SIGMOID_WORDS), which call a third
(SIGMOID_I). No existing glyph, advance or cmap entry changes. `i.sigmoid` is declared as ss16
proposal 217 (a new id after the lab's 125-216) with ctx.ss16_owner, so verify_ss16.py counts its
lesson-prose changes as a kept proposal's.
"""
import math

import pathops

GLYPH = 'i.sigmoid'
RISE, HANDLE, TAIL, TAIL_K = 124, 0.58, 58, 0.625     # sigI3e2
K2 = 20                                                # k2: units off each side (Regular)


def _sigmoid_stroke(ctx, T, C, Wt, ylo, yhi):
    """The rising stroke, foot to top, as a closed path; returns it and the top's right end."""
    h = Wt / 2
    yb, yt = ylo + h, yhi - h
    xa, xb = T, T + C
    x1 = xb + T

    def middle(dx, dy):
        a, b = (xa + dx, yb + dy), (xb + dx, yt + dy)
        return [a, (a[0] + C * HANDLE, a[1]), (b[0] - C * HANDLE, b[1]), b]

    def bez(P, t):
        return tuple((1 - t) ** 3 * P[0][k] + 3 * (1 - t) ** 2 * t * P[1][k]
                     + 3 * (1 - t) * t * t * P[2][k] + t ** 3 * P[3][k] for k in (0, 1))

    def thinnest(sx):
        U = [bez(middle(-sx, h), i / 120) for i in range(121)]
        L = [bez(middle(sx, -h), i / 30) for i in range(31)]
        return min(min(math.dist(p, u) for u in U) for p in L)

    lo, hi = -0.8 * Wt, 0.8 * Wt
    for _ in range(28):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if thinnest(m) < Wt else (lo, m)
    sx = (lo + hi) / 2
    low, up = middle(sx, -h), middle(-sx, h)
    q = pathops.Path(); pen = q.getPen()
    pen.moveTo((0, yb - h)); pen.lineTo(low[0]); pen.curveTo(*low[1:])
    pen.lineTo((x1, yt - h)); pen.lineTo((x1, yt + h))
    pen.lineTo(up[3]); pen.curveTo(up[2], up[1], up[0])
    pen.lineTo((0, yb + h)); pen.closePath()
    q.simplify()
    return q, x1


def glyphs(ctx):
    if GLYPH in ctx.font.getGlyphOrder():
        raise SystemExit(f'sigmoid: the font already has {GLYPH}')
    stem_path = ctx.path_of('dotlessi')
    s0, s1 = ctx.hspans(stem_path, 300)[0]
    Wt, top = s1 - s0, stem_path.bounds[3]
    dot = ctx.clip(ctx.path_of('i'), (-100, 560, 600, 2000))
    db = dot.bounds; dcx = (db[0] + db[2]) / 2
    T = TAIL * (1 + TAIL_K * (ctx.SV - 1))
    stroke, x1 = _sigmoid_stroke(ctx, T, RISE, Wt, 0, top)
    body = ctx.union(stroke, ctx.mv(dot, (x1 - T / 2) - dcx, 0))
    lsb = 70 - T * 0.25
    adv = round(x1 + 2 * lsb)                          # the e2 glyph's advance
    d = K2 * adv / 351                                 # k2, scaled with the advance (351 in Regular)
    ctx.add(GLYPH, ctx.mv(body, lsb - d), adv - 2 * d)
    ctx.GDEF_CLASS[GLYPH] = 1
    ctx.ss16_owner(217, [GLYPH])
    ctx.log(f'{GLYPH}: tails {T:.0f}, stem {Wt:.0f}, advance {adv} - 2 x {d:.1f} = {ctx.W(GLYPH)}')


def features(ctx):
    cm = ctx.font.getBestCmap()
    s = [cm[ord(c)] for c in 'sigmoid']
    rules = []
    for word in (s, s + [cm[ord('s')]]):
        marked = ' '.join(g + "'" for g in word)
        sub = ' '.join([word[0] + "'", word[1] + "' lookup SIGMOID_I"] + [g + "'" for g in word[2:]])
        rules.append(f"  ignore sub @S16_WORD {marked};\n  ignore sub {marked} @S16_WORD;\n  sub {sub};")
    ctx.gsub(f"lookup SIGMOID_I {{ sub {s[1]} by {GLYPH}; }} SIGMOID_I;\n"
             f"lookup SIGMOID_WORD {{\n{rules[0]}\n}} SIGMOID_WORD;\n"
             f"lookup SIGMOID_WORDS {{\n{rules[1]}\n}} SIGMOID_WORDS;\n"
             "feature ss16 { lookup SIGMOID_WORDS; lookup SIGMOID_WORD; } ss16;\n",
             after='ss16_front')

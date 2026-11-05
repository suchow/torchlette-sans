"""mathglyphs: the glyphs lesson math needs that the font lacked or drew as text.

Everything is drawn from Torchlette Sans's own outlines at each weight, except ℵ, which
is Noto Sans Math's aleph (Copyright 2022 The Noto Project Authors, SIL Open Font
License 1.1, no Reserved Font Name; `../notosansmath/NotoSansMath-Regular.ttf`) scaled
to the capital height and brought to each weight's stem by offsetting its outline.

New code points
- ∬ ∭ (U+222C, U+222D): the font's ∫ repeated at a pitch of 0.66 of its ink width.
- ∮ ∯ (U+222E, U+222F): ∫ and ∬ with a ring (an oval for ∯) on the integral's centre,
  drawn with the operators' bar and kept round in the italic.
- ⋃ ⋂ (U+22C3, U+22C2): the n-ary union and intersection at the text size of ∑ and ∏
  (ink -180..705), stems of ∏'s (new) weight, a half circle at the closed end.
  math_table refers to uni222C uni222D uni222E uni222F uni22C3 by these names for the
  display sizes.
- ℵ (U+2135): see above; 705 high, sidebearings 50.
- U+20D7 combining right arrow above (KaTeX's \\vec): a short arrow, zero advance, ink
  centred on 0 like the font's other combining marks, the head drawn like arrowright's.
  It is outside the Makefile's web ranges: the Makefile adds U+20D7.

Changed glyphs (GLYPH_OVERRIDE; why each changes)
- asciicircum: KaTeX writes \\hat as U+005E, and Chrome draws the cmap glyph of U+005E
  itself over any base narrower than its ink (MathML stretchy accents fall back to the
  MATH variants only when the base is wider). Mulish's caret (ink 142..628) made v̂ and
  ŷ diamonds and ı̂ an arrow. It is now a low hat over x-height letters, as in Latin
  Modern, Times or Verdana. Its size is TeX's hat's in proportion to the x-height (0.62
  x-heights wide, 0.37 tall): ink 290 wide from 560, 0.85 of the bar's weight, advance
  460 (Chrome sets \\hat as a non-stretchy accent from this cmap glyph, and a wider
  advance than the base widens î). hat.w1..w5.mathglyphs (380..820 wide, the bar's
  weight) are the stretch sizes math_table lists after it.
- dotaccent (U+02D9, \\dot), uni02C9 (U+02C9, \\bar), macron, dieresis (\\ddot),
  asciicircum, uni20D7: Chrome stacks an accent with its ink touching the base's ink
  (q̇'s dot disappears into the q). Each carries, in `post`, an inkless contour (two
  coincident-line points, no area) a fixed gap under its visible ink, so the stacked
  accent clears the base by that gap whatever the base's height. dotaccent is redrawn as
  a round dot of the i's dot size (it was a composite of uni0307, which is unchanged);
  macron and dieresis are decomposed (their marks are unchanged).
- minute, second (U+2032, U+2033): Mulish's are copies of the straight quote. They are
  now slanted wedges in the proportion of Latin Modern's prime to the x-height
  (base 440..745). symbols builds ‴ ⁗ ‵ ‶ ‷ from minute and second, and greek's
  numeral signs and ʹ (U+02B9) are composites of minute, so all follow.
- ssty (feature registered here): minute, second and uni2034 to script primes
  (*.ssty.mathglyphs) designed to be set as superscripts: low in the glyph (bottom at
  y 100), so that at the script size (68%) on the superscript shift (400) the prime
  starts at the x-height and rises to about the ascender, as TeX's prime does. Chrome
  does not turn ssty on by itself: the app's CSS must set font-feature-settings "ssty"
  on script children (msup/msubsup), and web_features.txt must keep ssty.
- product (U+220F): stems and bar heavier (x1.15 at Regular, easing to x1.05 at
  Black, and the stems never lighter than 1.08 n stems: Mulish's Black ∏ is lighter
  than its n), so the text-size ∏ is as dark as ∑.
- uni222A uni2229 (∪ ∩; in `features`, after symbols made them): 1.26 times the
  symbols module's, their stroke kept, so they are TeX's size (1.2 x-heights wide, 1.3
  tall; they were the size of a lowercase letter).
- infinity (U+221E; in `features`, after symbols has built ∝ from the old one): 1.42x
  the old one, its stroke brought back to the old weight, centred on the math axis,
  advance 840 (ink about 740 x 380, the proportion of STIX Two Math's and Noto Sans
  Math's ∞ to the x-height).
- uni2295 uni2297 uni2299 (⊕ ⊗ ⊙; in `features`, after symbols made them): the ring
  grows from 460 to 600 across (Latin Modern's ⊙ is 1.6 x-heights), advance 720; the
  dot of ⊙ grows with it.
- uni22EF uni22EE uni22F1 (⋯ ⋮ ⋱; in `features`, after symbols made them at the
  ellipsis's pitch, 0.13 em between dots, period-sized): TeX's \cdots in proportion to
  the x-height, dots 1.25 times periodcentered (120) on the math axis, 185 apart and
  92 outside;
  ⋮ steps 0.9 of that upward and sits on the baseline, ⋱ steps the same diagonally.
- uni210F (ℏ; in `features`, after mathletters and mathitalic): the math italic h
  (uni210E) with mathletters' slanted bar (30 degrees, 0.72 of h's ink width, centred on
  the stem midway between the arch and the ascender, the crossbar's weight), as Latin
  Modern's and STIX's ℏ is an italic h with a slanted bar; shifted to a left sidebearing
  of at least 40 (iℏ collided). verify_mathletters checks it against uni210E.
- nu, gamma: redrawn so that ν and γ (and, through mathitalic's references, 𝜈 and 𝛾)
  do not read as v and y: ν's right arm is a curve and its vertex sits left of centre;
  γ has the standard open form of Noto Sans, Latin Modern and STIX: a left arm that
  starts at a terminal, curls over at the x-height and swoops down, and a straight right
  arm meet at the baseline, and an upright descender drops
  from the join and thickens to a round end (y's tail continues its right arm).

Feature ss14 (registered here): the math forms of the binary operators and relations,
*.ss14.mathglyphs, 1.22 times as wide as the text forms, on the same centre with the same stroke
(⋅ grows whole): + − = ≠ < > ≤ ≥ ± ∓ × ÷ ≈ ≡ ∼ ≃ ≅ ∝ ∈ ∉ ∋ ⊂ ⊃ ⊆ ⊇ ≪ ≫ ≺ ≻ ∧ ∨ ⋅. TeX's
and STIX's operators are 1.26 to 1.5 x-heights wide, Mulish's 1.05: right for prose, small
beside math letters. Chrome turns no feature on in MathML by itself, so the app's CSS sets
font-feature-settings "ss14" on math (and "ssty", "ss14" on script children), and
web_features.txt must keep ss14. Prose keeps the text forms.

Code points remapped: none. Lookups: MATHGLYPHS_SSTY (GSUB ssty), MATHGLYPHS_SS14 (GSUB ss14).
"""
import math
import os

import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from array import array

GLYPH_OVERRIDE = {
    'asciicircum', 'dotaccent', 'uni02C9', 'macron', 'dieresis', 'minute', 'second', 'product',
    'uni02B9',  # ʹ: composite of minute; its hmtx advance is synced in post (USE_MY_METRICS)
    'infinity', 'uni2295', 'uni2297', 'uni2299', 'uni210F', 'nu', 'gamma', 'uni222A', 'uni2229',
    'uni22EF', 'uni22EE', 'uni22F1',
}

HERE = os.path.dirname(os.path.abspath(__file__))
NOTO_MATH = os.path.join(HERE, '..', 'notosansmath', 'NotoSansMath-Regular.ttf')

# The accents' inkless contour sits this far under their visible ink (units).
ACCENT_GAP = {'asciicircum': 90, 'dotaccent': 75, 'uni02C9': 80, 'macron': 80, 'dieresis': 75, 'uni20D7': 70}
ACCENT_GAP.update({f'hat.w{i}.mathglyphs': 90 for i in range(1, 6)})
HAT_W = (290, 380, 470, 560, 680, 820)     # ink widths of ^ and of hat.w1..w5.mathglyphs
HAT_RISE0, HAT_ADV = 136, 460              # ^ (TeX's hat: 0.62 x-heights wide, 0.37 tall)
INT_PITCH = 0.66          # ∬ ∭: pitch of the repeated ∫ over its ink width
SSTY_SHIFT = 400          # the superscript shift the script primes are drawn for
SSTY_SCALE = 0.68         # and the script size (MATH ScriptPercentScaleDown)
CUP_SCALE = 1.26          # ∪ ∩: their text forms grown to TeX's proportion of the x-height
DOTS_GAP = 185            # ⋯ ⋮ ⋱: the space between dots (TeX's \cdotp pitch less a dot, x-height scaled)
DOTS_SCALE = 1.25         # ⋯ ⋮ ⋱: their dots against periodcentered (TeX's 0.11 em dot, x-height scaled)
OP_SCALE = 1.22           # ss14's math operators, against the text forms
# ss14: (glyph, keep the stroke) for the binary operators and relations math sets larger
SS14_OPS = [(n, True) for n in (
    'plus', 'minus', 'equal', 'notequal', 'less', 'greater', 'lessequal', 'greaterequal',
    'plusminus', 'uni2213', 'multiply', 'divide', 'approxequal', 'uni2261', 'uni223C', 'uni2243',
    'uni2245', 'uni221D', 'uni2208', 'uni2209', 'uni220B', 'uni2282', 'uni2283', 'uni2286',
    'uni2287', 'uni226A', 'uni226B', 'uni227A', 'uni227B', 'uni2227', 'uni2228')] + [('uni22C5', False)]


def hat_rise(ink):
    return 128 + 0.08 * (ink - 360)


def _ellipse_round(ctx, cx, cy, rx, ry):
    """An ellipse that comes out with upright axes in the italic (see build.py's dot)."""
    if not ctx.ITALIC: return ctx.ellipse(cx, cy, rx, ry)
    K, YC = ctx.ITALIC_K, ctx.ITALIC_YC
    return ctx.transformed(ctx.ellipse(cx + K * (cy - YC), cy, rx, ry), (1, 0, -K, 1, K * YC, 0))


def _ring(ctx, cx, cy, rx, ry, w):
    return ctx.diff(_ellipse_round(ctx, cx, cy, rx, ry), _ellipse_round(ctx, cx, cy, rx - w, ry - w))


def _offset(p, t):
    """p grown (t > 0) or shrunk (t < 0) by |t| on every side."""
    if abs(t) < 0.5: return p
    s = pathops.Path(p)
    s.stroke(2 * abs(t), pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    return pathops.op(p, s, pathops.PathOp.UNION if t > 0 else pathops.PathOp.DIFFERENCE)


def _stem(ctx, name='n', y=250):
    s = ctx.hspans(ctx.path_of(name), y)[0]
    return s[1] - s[0]


def glyphs(ctx):
    c = ctx
    rect, poly, union, diff, clip, band = c.rect, c.poly, c.union, c.diff, c.clip, c.band
    path_of, transformed, mv, mirror, W = c.path_of, c.transformed, c.mv, c.mirror, c.W
    A, BAR, SM = c.LIN_AXIS, c.BAR, c.SM
    order = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()
    made = ctx.made = []
    NSTEM = _stem(c)

    def put(cp, name, path, adv, cls=1):
        assert name not in order, name
        assert cp is None or cp not in cmap, f'U+{cp:04X} already mapped to {cmap.get(cp)}'
        c.add(name, path, adv)
        c.GDEF_CLASS[name] = cls
        if cp is not None: c.map(cp, name)
        made.append(name)

    def replace(name, path, adv):
        assert name in GLYPH_OVERRIDE
        c.add(name, path, adv)

    # ---- the product: heavier stems and bar -----------------------------------------
    pr = path_of('product'); pb = pr.bounds
    st = c.hspans(pr, 300)                      # [(left stem), (right stem)]
    bar_y = c.vspans(pr, (pb[0] + pb[2]) / 2)[-1]
    f = 1.15 - 0.10 * min(1.0, max(0.0, (c.SV - 1.0) / 1.47))
    ls, rs = st[0], st[-1]
    sw = max((ls[1] - ls[0]) * f, NSTEM * 1.08)     # never lighter than n (Mulish's Black ∏ is)
    bh = (bar_y[1] - bar_y[0]) * f
    prod = union(rect(ls[0], pb[1], ls[0] + sw, pb[3]), rect(rs[1] - sw, pb[1], rs[1], pb[3]),
                 rect(ls[0], pb[3] - bh, rs[1], pb[3]))
    replace('product', prod, W('product'))
    PSTEM, PBAR = sw, bh

    # ---- integrals ------------------------------------------------------------------
    I = path_of('integral'); ib = I.bounds; iw = ib[2] - ib[0]
    pitch = round(INT_PITCH * iw)
    yc = (ib[1] + ib[3]) / 2
    sp = c.hspans(I, yc); scx = (sp[0][0] + sp[0][1]) / 2
    put(0x222C, 'uni222C', union(I, mv(I, pitch)), W('integral') + pitch)
    put(0x222D, 'uni222D', union(I, mv(I, pitch), mv(I, 2 * pitch)), W('integral') + 2 * pitch)
    R = round(0.50 * iw); RW = BAR * 1.0
    put(0x222E, 'uni222E', union(I, _ring(c, scx, yc, R, R, RW)), W('integral'))
    put(0x222F, 'uni222F', union(I, mv(I, pitch), _ring(c, scx + pitch / 2, yc, R + pitch / 2, R, RW)),
        W('integral') + pitch)

    # ---- n-ary union and intersection -------------------------------------------------
    sb = path_of('summation').bounds
    top, bot = sb[3], sb[1]
    x0, x1 = 80, 520; r = (x1 - x0) / 2; cx = (x0 + x1) / 2; ycu = bot + r
    outer = union(_half(c, cx, ycu, r, r), rect(x0, ycu - 1, x1, top))
    inner = union(_half(c, cx, ycu, r - PSTEM, r - PBAR), rect(x0 + PSTEM, ycu - 1, x1 - PSTEM, top + 10))
    cup = diff(outer, inner)
    put(0x22C3, 'uni22C3', cup, 600)
    put(0x22C2, 'uni22C2', transformed(cup, (1, 0, 0, -1, 0, top + bot)), 600)

    # ---- aleph, from Noto Sans Math -------------------------------------------------
    nm = TTFont(NOTO_MATH); ngs = nm.getGlyphSet(); ncm = nm.getBestCmap()
    al = pathops.Path(); ngs[ncm[0x2135]].draw(al.getPen(glyphSet=ngs))
    nl = pathops.Path(); ngs[ncm[0x6C]].draw(nl.getPen(glyphSet=ngs))
    ab = al.bounds
    s = 705 / (ab[3] - max(ab[1], 0))
    al = transformed(al, (s, 0, 0, s, 0, 0))
    lsp = c.hspans(nl, 300)[0]; nstem = (lsp[1] - lsp[0]) * s
    al = _offset(al, (NSTEM * 1.08 - nstem) / 2)
    ab = al.bounds
    al = mv(al, 50 - ab[0])
    put(0x2135, 'uni2135', al, round(ab[2] - ab[0] + 100))

    # ---- combining right arrow above (\vec) -------------------------------------------
    t = BAR * 0.86; L = 400; ya = 640; tip = L / 2
    wing_l, wing_h = 118 + 20 * (SM - 1), 82 + 12 * (SM - 1)
    head = c.stroke_line([(tip - wing_l, ya + wing_h), (tip, ya), (tip - wing_l, ya - wing_h)], t * 1.08, 20)
    head = clip(head, (-1000, -1000, tip, 2000))
    shaft = rect(-L / 2, ya - t / 2, tip - t * 0.8, ya + t / 2)
    put(0x20D7, 'uni20D7', union(head, shaft), 0, cls=3)

    # ---- the hat, and wider hats for math_table's stretchy list -----------------------
    def hat_path(cx, ink, rise, w=BAR):
        x0, x1, yb = cx - ink / 2, cx + ink / 2, 560
        k = 40 * rise / (ink / 2)
        p = c.stroke_line([(x0 - 40, yb - k), (cx, yb + rise), (x1 + 40, yb - k)], w, 60)
        return clip(p, (x0, yb, x1, 2000))
    adv = HAT_ADV
    replace('asciicircum', hat_path(adv / 2, HAT_W[0], HAT_RISE0, BAR * 0.85), adv)
    for i, ink in enumerate(HAT_W[1:], 1):
        put(None, f'hat.w{i}.mathglyphs', hat_path(ink / 2 + 20, ink, hat_rise(ink)), ink + 40)

    # ---- the dot above: the i's dot ------------------------------------------------------
    ib_i = path_of('i'); top_parts = clip(ib_i, (-200, 520, 800, 1200)).bounds
    rdot = (top_parts[2] - top_parts[0]) / 2
    replace('dotaccent', c.dot(W('dotaccent') / 2, 622, rdot), W('dotaccent'))
    for n in ('macron', 'dieresis'):
        replace(n, path_of(n), W(n))       # decomposed (the marks they used stay)

    # ---- primes ------------------------------------------------------------------------
    def wedge(xt, ybot, ytop, wt, wb, slant):
        xb = xt - (ytop - ybot) * slant
        return poly([(xt - wt / 2, ytop), (xt + wt / 2, ytop), (xb + wb / 2, ybot), (xb - wb / 2, ybot)])
    slant = math.tan(math.radians(17))
    pw_t = NSTEM * 1.30; pw_b = NSTEM * 0.50
    pbot, ptop = 440, 745
    ink_w = pw_t / 2 + (ptop - pbot) * slant + pw_b / 2
    lsb = 55
    xt = lsb + ink_w - pw_t / 2
    one = wedge(xt, pbot, ptop, pw_t, pw_b, slant)
    pitch_p = round(ink_w * 0.62 + 50)
    adv1 = round(ink_w + 2 * lsb)
    replace('minute', one, adv1)
    replace('second', union(one, mv(one, pitch_p)), adv1 + pitch_p)

    # script primes: drawn for a superscript at SSTY_SCALE on a shift of SSTY_SHIFT
    k = 1 / SSTY_SCALE
    fb, ft = (470 - SSTY_SHIFT) * k + 10, (470 - SSTY_SHIFT) * k + 330 * k
    sw_t, sw_b = NSTEM * 1.45, NSTEM * 0.60
    s_ink = sw_t / 2 + (ft - fb) * slant + sw_b / 2
    s_lsb = 50
    sxt = s_lsb + s_ink - sw_t / 2
    sone = wedge(sxt, fb, ft, sw_t, sw_b, slant)
    s_pitch = round(s_ink * 0.55 + 45)
    s_adv = round(s_ink + s_lsb + 25)
    put(None, 'minute.ssty.mathglyphs', sone, s_adv)
    put(None, 'second.ssty.mathglyphs', union(sone, mv(sone, s_pitch)), s_adv + s_pitch)
    put(None, 'uni2034.ssty.mathglyphs', union(sone, mv(sone, s_pitch), mv(sone, 2 * s_pitch)), s_adv + 2 * s_pitch)

    _greek(c, NSTEM)

    c.log(f'product stem {PSTEM:.0f} bar {PBAR:.0f}; integral pitch {pitch}; aleph stem {NSTEM * 1.04:.0f}; '
          f'prime ink {ink_w:.0f}x{ptop - pbot}; script prime {s_ink:.0f}x{ft - fb:.0f} at {fb:.0f}')


def _curve(pts, w):
    """A cubic centreline (p0, c1, c2, p3) stroked w wide, ends cut square."""
    p = pathops.Path(); pen = p.getPen(); pen.moveTo(pts[0]); pen.curveTo(*pts[1:]); pen.endPath()
    p.stroke(w, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4); p.simplify()
    return p


def _greek(c, NSTEM):
    """ν with a near-upright left stroke and a curved right arm; γ with an open, straight descender."""
    XH = 470
    nu = c.path_of('nu'); b = nu.bounds; w = b[2] - b[0]; x0 = b[0]
    tl = NSTEM * 1.0                       # the left stroke, a stem
    tr = NSTEM * 0.86                      # the right arm
    top_l = x0 + tl / 2 + 4
    bot_l = x0 + 0.25 * w
    left = c.band((top_l, XH + 40), (bot_l, -40), tl)
    xr = b[2] - tr / 2
    right = _curve([(bot_l + 0.1 * tl, 0), (bot_l + 0.55 * (xr - bot_l), 10), (xr, 0.38 * XH), (xr, XH + 40)], tr)
    nu_new = c.clip(c.union(left, right), (-100, 0, 1000, XH))
    c.add('nu', nu_new, c.W('nu'))

    # γ: a curled left arm and a straight right arm meeting at the baseline, and
    # from their meeting an open descender that thickens to a round end (Noto Sans,
    # Latin Modern, STIX). y's tail continues its right arm; γ's drops straight down.
    g = c.path_of('gamma'); gb = g.bounds; x0, x1, yd = gb[0], gb[2], gb[1]; w = x1 - x0
    tl, tr = NSTEM * 1.0, NSTEM * 0.84
    vx, yv = x0 + 0.55 * w, 20
    yt = XH - tl / 2                                # the curl's centreline top: ink to the x-height
    right = c.band((x1 - tr * 0.55, XH + 60), (vx, yv - 40), tr)
    # the left arm: a terminal at 0.8 x-height rising to a curl, then a swoop to the join
    xa = x0 + tl / 2 + max(0.14 * w, 0.75 * tl)     # the curl's top (wider in heavy weights)
    curl = _curve([(x0 + tl / 2, min(0.80 * XH, yt - 0.6 * tl)), (x0 + tl / 2, yt), (xa - 0.4 * (xa - x0 - tl / 2), yt),
                   (xa, yt)], tl)
    swoop = _curve([(xa, yt), (xa + 0.14 * w, yt), (vx - 0.10 * w, 0.45 * XH), (vx, yv - 40)], tl)
    arms = c.clip(c.union(curl, swoop, right), (-100, yv, 1000, XH))
    sp = c.hspans(arms, yv + 2); L, Rr = sp[0][0], sp[-1][1]
    tt, tb = NSTEM * 0.62, NSTEM * 1.08         # the descender's neck and its end
    ry = tb * 0.62; yb = yd + ry; yn = yv - min(70, 0.3 * (yv - yd))
    tail = c.union(c.poly([(L, yv + 2), (Rr, yv + 2), (vx + tt / 2, yn), (vx + tb / 2, yb),
                           (vx - tb / 2, yb), (vx - tt / 2, yn)]), c.ellipse(vx, yb, tb / 2, ry))
    yj = yv
    c.add('gamma', c.union(arms, tail), c.W('gamma'))
    c.log(f'nu: left stroke {top_l:.0f}->{bot_l:.0f}; gamma: join {yj} at x {vx:.0f}, descender {tt:.0f}->{tb:.0f}')


def _half(c, cx, cy, rx, ry):
    """The lower half of an ellipse (y <= cy)."""
    return c.clip(c.ellipse(cx, cy, rx, ry), (cx - rx - 10, cy - ry - 10, cx + rx + 10, cy))


def features(ctx):
    c = ctx
    path_of, mv, W, union, diff, rect, band = c.path_of, c.mv, c.W, c.union, c.diff, c.rect, c.band
    A, BAR = c.LIN_AXIS, c.BAR

    # ---- infinity: larger, the same stroke --------------------------------------------
    inf = path_of('infinity'); b = inf.bounds
    cx0, cy0 = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    vs = c.vspans(inf, b[0] + (b[2] - b[0]) * 0.20)      # through the left loop
    w0 = min(s1 - s0 for s0, s1 in vs)
    sc = 1.42
    big = c.transformed(inf, (sc, 0, 0, sc, -sc * cx0, -sc * cy0))
    big = _offset(big, -(sc - 1) * w0 / 2 * 0.80)
    bb = big.bounds
    adv = 840
    big = mv(big, adv / 2 - (bb[0] + bb[2]) / 2, A - (bb[1] + bb[3]) / 2)
    c.add('infinity', big, adv)

    # ---- circled operators: a larger ring ----------------------------------------------
    TH, TV = BAR, BAR * 1.1
    VB = BAR * 1.15
    RR = 300; adv = 720; cx = adv / 2
    ring = diff(c.ellipse(cx, A, RR, RR), c.ellipse(cx, A, RR - TV, RR - TH))
    plus = union(ring, rect(cx - RR + 5, A - BAR / 2, cx + RR - 5, A + BAR / 2), rect(cx - VB / 2, A - RR + 5, cx + VB / 2, A + RR - 5))
    c.add('uni2295', plus, adv)
    dg = (RR - 10) / math.sqrt(2)
    c.add('uni2297', union(ring, band((cx - dg, A - dg), (cx + dg, A + dg), BAR), band((cx - dg, A + dg), (cx + dg, A - dg), BAR)), adv)
    pc = path_of('periodcentered'); pb = pc.bounds; s = 1.2
    pcs = c.transformed(pc, (s, 0, 0, s, cx - s * (pb[0] + pb[2]) / 2, A - s * (pb[1] + pb[3]) / 2))
    c.add('uni2299', union(ring, pcs), adv)

    # ---- ∪ ∩: TeX's size, the same stroke ------------------------------------------------
    for n in ('uni222A', 'uni2229'):
        p = path_of(n); b = p.bounds
        st = min(s1 - s0 for s0, s1 in c.hspans(p, (b[1] + b[3]) / 2))
        lsb = c.hmtx[n][1]
        q = _grow(c, p, CUP_SCALE, st)
        qb = q.bounds
        c.add(n, mv(q, lsb - qb[0]), round(qb[2] - qb[0] + 2 * lsb))

    # ---- ⋯ ⋮ ⋱: TeX's spacing (symbols drew them at the ellipsis's tight pitch) ---------------
    # TeX's \cdots is three \cdotp, each 0.278 em wide with a 0.11 em dot centred, on the
    # math axis. Scaled to the x-height (470 here, 431 in Latin Modern): dots 1.25 times
    # the period's (about 120 units), 185 between them and half that outside.
    pc = path_of('periodcentered'); pb = pc.bounds
    pc = c.transformed(pc, (DOTS_SCALE, 0, 0, DOTS_SCALE, 0, 0)); pb = pc.bounds; d = pb[2] - pb[0]
    def dot(x, y): return mv(pc, x - (pb[0] + pb[2]) / 2, y - (pb[1] + pb[3]) / 2)
    gap, sb = DOTS_GAP, DOTS_GAP / 2
    step = d + gap
    c.add('uni22EF', union(*[dot(sb + d / 2 + k * step, A) for k in range(3)]), round(2 * sb + d + 2 * step))
    vstep = 0.9 * step                   # ⋮ from the baseline up, centred on the axis
    c.add('uni22EE', union(*[dot(sb + d / 2, A + (k - 1) * vstep) for k in range(3)]), round(2 * sb + d))
    c.add('uni22F1', union(*[dot(sb + d / 2 + k * step, A + (1 - k) * vstep) for k in range(3)]),
          round(2 * sb + d + 2 * step))

    # ---- ss14: the math forms of the operators and relations, larger ------------------------
    subs = []
    for n, keep in SS14_OPS:
        if n not in c.font.getGlyphOrder(): continue
        p = path_of(n); b = p.bounds
        sb = min(c.hmtx[n][1], W(n) - b[2])
        q = _grow(c, p, OP_SCALE, BAR if keep else 0)
        qb = q.bounds
        alt = f'{n}.ss14.mathglyphs'
        c.add(alt, mv(q, sb - qb[0]), round(qb[2] - qb[0] + 2 * sb))
        c.GDEF_CLASS[alt] = c.GDEF_CLASS.get(n, 1)
        subs.append(f'  sub {n} by {alt};')

    # ---- hbar: the math italic h with mathletters' bar ------------------------------------
    if 'uni210E' in c.font.getGlyphOrder() and 'uni210F' in c.font.getGlyphOrder():
        _hbar(c)
    else:
        c.log('no uni210E/uni210F: hbar left alone')

    c.gsub("""
lookup MATHGLYPHS_SSTY {
  sub minute by minute.ssty.mathglyphs;
  sub second by second.ssty.mathglyphs;
  sub uni2034 by uni2034.ssty.mathglyphs;
} MATHGLYPHS_SSTY;
feature ssty { lookup MATHGLYPHS_SSTY; } ssty;
lookup MATHGLYPHS_SS14 {
""" + '\n'.join(subs) + """
} MATHGLYPHS_SS14;
feature ss14 { featureNames { name "Math operators"; }; lookup MATHGLYPHS_SS14; } ss14;
""")


def _grow(c, p, s, stroke):
    """p grown about its ink centre so that its ink is s times as wide, its strokes (stroke
    wide) kept at that width: scaled by (s w - stroke) / (w - stroke), then thinned."""
    b = p.bounds; cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    w = b[2] - b[0]
    s = (s * w - stroke) / (w - stroke)
    q = c.transformed(p, (s, 0, 0, s, cx - s * cx, cy - s * cy))
    return _offset(q, -(s - 1) * stroke / 2) if stroke else q


def _hbar(c):
    """ℏ: the math italic h (uni210E) with mathletters' slanted bar across its ascender, as
    Latin Modern's and STIX's ℏ: the bar rises to the right at ML_HBAR_DEG (30), spans 0.72
    of the upright h's ink width centred on the stem, and crosses it midway between the arch
    and the ascender, at the crossbar's weight."""
    h = c.path_of('uni210E'); hb = h.bounds
    H = c.path_of('H'); Hb = H.bounds
    bth = min(s1 - s0 for s0, s1 in c.vspans(H, (Hb[0] + Hb[2]) / 2))     # H's crossbar
    up = c.path_of('h').bounds
    arch_top = 470
    yc = (arch_top + hb[3]) / 2
    deg = c.P('ML_HBAR_DEG', 30); tg = math.tan(math.radians(deg))
    half = 0.72 * (up[2] - up[0]) / 2
    t = bth / math.cos(math.radians(deg))
    yc = min(yc, hb[3] - 10 - half * tg - t / 2)
    stem = c.hspans(h, yc)[0]; xc = (stem[0] + stem[1]) / 2
    bar = c.poly([(xc - half, yc - half * tg - t / 2), (xc + half, yc + half * tg - t / 2),
                  (xc + half, yc + half * tg + t / 2), (xc - half, yc - half * tg + t / 2)])
    hbar = c.union(h, bar)
    hb2 = hbar.bounds
    adv_h, lsb_h = c.hmtx['uni210E']
    dx = max(lsb_h, 40) - hb2[0]             # a left sidebearing of at least 40 (iℏ collided)
    adv = round(max(adv_h + dx, hb2[2] + dx + (adv_h - hb[2])))
    c.add('uni210F', c.mv(hbar, dx), adv)
    c.log(f'hbar: bar {2 * half:.0f} at {deg} degrees, {bth:.0f} thick, centre ({xc:.0f}, {yc:.0f}), shifted {dx:.0f}, advance {adv}')


def post(ctx):
    """The accents' inkless contours: two points on one spot, no area, a gap under the ink."""
    glyf = ctx.font['glyf']
    for name, gap in ACCENT_GAP.items():
        g = glyf[name]
        if g.isComposite():
            continue
        coords = list(g.coordinates); flags = list(g.flags); ends = list(g.endPtsOfContours)
        xs = [p[0] for p in coords]; ys = [p[1] for p in coords]
        x = round((min(xs) + max(xs)) / 2); y = round(min(ys) - gap)
        coords += [(x, y), (x + 1, y)]; flags += [1, 1]; ends.append(len(coords) - 1)
        g.coordinates = GlyphCoordinates(coords); g.flags = array('B', flags)
        g.endPtsOfContours = ends; g.numberOfContours = len(ends)
        g.recalcBounds(glyf)
        ctx.hmtx[name] = (ctx.hmtx[name][0], g.xMin)

    # Composites that take their metrics from a component (USE_MY_METRICS, e.g. ʹ U+02B9
    # from minute) keep a stale hmtx advance once this module redraws the component, so
    # HarfBuzz (hmtx) and FreeType (the flag) disagree. Copy the component's advance to
    # the parent so every consumer sees the same width.
    for name in ctx.font.getGlyphOrder():
        g = glyf[name]
        if not g.isComposite():
            continue
        for comp in g.components:
            if comp.flags & 0x0200 and comp.glyphName in ctx.hmtx.metrics:
                ctx.hmtx[name] = (ctx.hmtx[comp.glyphName][0], ctx.hmtx[name][1])
                break

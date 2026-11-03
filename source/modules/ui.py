"""ui: the interface symbols ✓ ✗ ■ □ ▶ ● ○ ★, the circled numbers ①-⑳ and the keyboard
symbols ⌘ ⌥ ⇧ ⏎ ⌫, drawn in Torchlette's strokes at every weight.

Strokes. Two measures of this style's capitals are the monoline weights: H's crossbar (59 at
Regular, 103 at Bold, 139 at Black) for every outlined shape (□ ○, ⌘ ⌥ ⇧ ⏎ ⌫), and X's
diagonal across its stroke (63 at Regular, 114 at Bold) for the two marks drawn as strokes,
✓ and ✗, since Torchlette's diagonals carry the stems' weight. The keyboard symbols, whose
counters are small, take the crossbar only up to 0.15 of the cap height (106: ExtraBold's 121
and Black's 139 are capped, Bold's 103 is not), as a heavier ⌘ is four dots and a square. The
circled numbers' rings follow their figures instead (below). The filled shapes have no stroke.

Sizes. The shapes stand on the baseline at the cap height, as Noto Sans Math sets them (its ■
and ● are cap height, its ▶ an equilateral triangle 1.13 cap heights tall, since a triangle
looks smaller than its box): ■ □ a cap-height square; ● ○ a circle of the cap height with
O's overshoot; ▶ the equilateral triangle, centred on the capitals; ★ a regular pentagram
(inner radius 0.382 of the outer, as Noto Sans Math's) as wide as the cap height, its box
centred on the capitals. ✓: the long arm rises at 58 degrees to the cap height from a vertex
whose mitred point is 12 under the baseline, the short arm comes in at 45 degrees from 0.36
of the height; ✗: two strokes crossing, cap height tall and 0.8 of that wide (Noto Sans
Symbols2's ✗ is 562 by 736), their ends cut flat at the baseline and cap height as X's are.
The keyboard symbols are cap height tall: ⌘ a square 0.27 of the height on its centre lines
with a loop at each corner tangent to both sides run on, the loops filling the rest (Noto
Sans Symbols2's proportions); ⌥ a cap height wide and 0.62 of one tall, centred on the
capitals: a bar from the left to 0.38 of the width, a diagonal down to 0.62, a bar to the
right, and a bar over the right third; ⇧ an outline arrow 0.8 cap heights wide, the head's
base at half height, the shaft 0.48 of the width; ⏎ a chevron head of the shipped arrows'
angle whose lower barb rests on the baseline, its shaft running right into a riser up to the
cap height; ⌫ a pentagon 1.42 cap heights wide whose point reaches 0.44 of the height in, an
× of 0.46 of the height centred in the box (smaller if it would come within 16 of the frame). ⌘ ⌥ ⌫ ✗ follow Noto Sans Symbols2 (Copyright
2022 The Noto Project Authors, https://github.com/notofonts/symbols, SIL Open Font License
1.1; google/fonts ofl/notosanssymbols2/NotoSansSymbols2-Regular.ttf, version 2.008, commit
7b6724ac), ⇧ ⏎ ✓ ★ and the geometric shapes Noto Sans Math (ofl/notosansmath, version
3.000, commit dbd1ab6e), the circled numbers Noto Sans Symbols (ofl/notosanssymbols, version
2.003, commit caa8c837): proportions measured, no outline copied.

Circled numbers ①-⑳ (U+2460-2473): a ring holding Torchlette's own small-cap figures
(`one.sc` ... `zero.sc`: the crossed 7, the redrawn 2), its weight set by theirs, as in Noto
Sans Symbols, whose ring is 0.83-0.90 of its figures' stem at every weight (Jordan chose this
balance over a ring equal to the stem and a hairline ring, Nov 2026). The figures' stem is
0.82 of H's stem at Regular, falling linearly in the stem to 0.64 at Black (Noto's figures:
0.82 and 0.64 of its H), and the ring's stroke is 0.8 of that (Regular: figure stem 54, ring
43; Black: 108 and 87). The ring is 1.08 cap heights across, plus its stroke's excess over 59
(Noto's rings widen towards Black too), centred on the capitals. One figure's flat height is
0.62 of the ring's inner diameter (Noto: 0.58-0.66), the figure scaled and its outline offset
in or out until its stem is the figures' stem; it is centred in the ring. Two figures stand at
0.95 of one figure's height, condensed (Noto condenses its two-figure numbers too) with a gap
of 0.05 of the ring, until the widest pairs, leaned in an italic, stay 0.025 of the ring inside
its inner circle; their height is lowered only when even 0.75 of it in width does not fit
(upright: 0.95 to SemiBold, 0.91 at Bold, 0.88 at Black; the italics, whose pairs lean, 0.90
at Light to 0.80 at Black). The pairs' horizontals are offset to
0.95 of one figure's and their verticals widened sideways (an offset in a frame stretched
vertically) to 0.90 of its stem, both 0.12 less at Black's stem, as Noto's two-figure stems
fall from 0.98 of its single figures' at Regular to 0.8 at Black.

Italics. These are pictures, not letters, so they do not lean: in an italic style every
glyph here is drawn where the reslant will put it and sheared back (as build.py's `dot` keeps
dots round), and comes out upright in the slanted font; only the figures inside the circled
numbers lean, as Mulish Italic's figures do. Advances and sidebearings are the same in both
frames.

Nothing existing is changed. No layout features. Glyph names: uni2713, uni2717, uni25A0,
uni25A1, uni25B6, uni25CF, uni25CB, uni2605, uni2460 ... uni2473, uni2318, uni2325, uni21E7,
uni23CE, uni232B. Code points outside the Makefile's web subset ranges: the circled numbers,
U+2460-2473 (the Makefile names ★ ✓ ✗, U+2605, U+2713 and U+2717, which the app's interface
shows). Knobs (environment): UI_RING, the circled numbers' ring in cap heights (1.08); UI_CN_Q, the
ring's stroke against the figures' stem (0.8); UI_CN_FSK and UI_CN_FSK_BK, the figures' stem
against H's at Regular and at Black (0.82, 0.64); UI_CN_FIGH, one figure's height against the
inner diameter (0.62); UI_CN_PAIRH, two figures' height against one's (0.95); UI_CN_GAP and
UI_CN_MARGIN, the pairs' gap and margin in rings (0.05, 0.025); UI_CN_KXMIN, the narrowest
pair (0.75 of its height scale).
"""
import math

import pathops

DIGITS = 'zero one two three four five six seven eight nine'.split()


def inset(pts, d):
    """A simple polygon's outline moved inward by d with mitred corners, whatever its
    orientation: each edge's line is offset and consecutive lines intersected; an edge too
    short for the offset (one whose offset runs backwards) is dropped and its neighbours meet
    instead, so a heavy stroke swallows a small notch rather than folding the outline."""
    n = len(pts)
    if sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)) < 0: pts = pts[::-1]
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]; L = math.hypot(x1 - x0, y1 - y0)
        u = ((x1 - x0) / L, (y1 - y0) / L); nrm = (-u[1], u[0])                  # the left normal: inward for CCW
        lines.append(((x0 + d * nrm[0], y0 + d * nrm[1]), u))

    def meet(a, b):
        (px, py), (ux, uy) = a; (qx, qy), (vx, vy) = b
        den = ux * vy - uy * vx
        t = ((qx - px) * vy - (qy - py) * vx) / den
        return (px + t * ux, py + t * uy)
    while True:
        m = len(lines)
        verts = [meet(lines[i - 1], lines[i]) for i in range(m)]            # vertex i starts edge i
        bad = [i for i in range(m) if (verts[(i + 1) % m][0] - verts[i][0]) * lines[i][1][0]
               + (verts[(i + 1) % m][1] - verts[i][1]) * lines[i][1][1] < 0]
        if not bad or m <= 3: return verts
        del lines[bad[0]]


def glyphs(ctx):
    c = ctx
    rect, poly, union, diff, clip, band = c.rect, c.poly, c.union, c.diff, c.clip, c.band
    ellipse, transformed, path_of, W, mv = c.ellipse, c.transformed, c.path_of, c.W, c.mv
    hspans, vspans = c.hspans, c.vspans
    K, YC = c.ITALIC_K, c.ITALIC_YC
    order = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()
    made = ctx.made = []
    width = lambda s: s[1] - s[0]
    mid = lambda s: (s[0] + s[1]) / 2

    hp = path_of('H'); Hb = hp.bounds; CH = Hb[3]; CC = CH / 2
    US = width(vspans(hp, (Hb[0] + Hb[2]) / 2)[0])                 # the crossbar: the outlines' stroke
    xp = path_of('X'); s1, s2 = hspans(xp, CH * 0.14)[0], hspans(xp, CH * 0.28)[0]
    DS = width(s1) * math.sin(math.atan2(CH * 0.14, abs(mid(s2) - mid(s1))))   # X's diagonal across its stroke
    KS = min(US, 0.15 * CH)                                        # the keyboard symbols' stroke: capped past Bold
    ctx.log(f'strokes: outlines {US:.1f} (H crossbar), keyboard {KS:.1f}, marks {DS:.1f} (X diagonal); cap height {CH:.0f}')

    def upright(p, cy=CC):
        """p where the reslant will put a shape centred at height cy, sheared back, so it stands
        upright in the italic; p itself in an upright style."""
        if not K: return p
        return transformed(mv(p, K * (cy - YC)), (1, 0, -K, 1, K * YC, 0))

    def put(cp, path, adv, name=None):
        name = name or f'uni{cp:04X}'
        assert name not in order, name
        assert cp not in cmap, f'U+{cp:04X} already mapped to {cmap[cp]}'
        c.add(name, path, adv); c.GDEF_CLASS[name] = 1
        ctx.map(cp, name); made.append(name)

    def fit(p, lsb, rsb=None):
        b = p.bounds; p = mv(p, lsb - b[0])
        return p, round((b[2] - b[0]) + lsb + (lsb if rsb is None else rsb))

    def place(cp, p, lsb, cy=CC):
        q, adv = fit(p, lsb); put(cp, upright(q, cy), adv)

    def pentagram(cx, cy, R, r):
        return poly([(cx + (R if i % 2 == 0 else r) * math.cos(math.radians(90 + 36 * i)),
                      cy + (R if i % 2 == 0 else r) * math.sin(math.radians(90 + 36 * i))) for i in range(10)])

    # ---- marks ------------------------------------------------------------------------------
    deep = 12                                                      # the vertex's point under the baseline
    xl = (CH + deep) / math.tan(math.radians(58)); s = 0.36 * CH
    pts = [(-s, -deep + s), (0, -deep), (xl, CH)]
    for _ in range(4):                                             # the stroke's mitre and caps fitted to the box
        tick = c.stroke_line(pts, DS, limit=4); b = tick.bounds
        k = (CH + deep) / (b[3] - b[1])
        pts = [(x * k, -deep + (y - b[1]) * k) for x, y in pts]
    place(0x2713, tick, 55)
    w = 0.8 * CH; dx = 60 * w / CH                                 # the strokes cut flat at the baseline and cap height, as X's
    place(0x2717, clip(union(band((-dx, -60), (w + dx, CH + 60), DS), band((-dx, CH + 60), (w + dx, -60), DS)), (-1000, 0, 1000, CH)), 55)

    # ---- geometric shapes ---------------------------------------------------------------------
    sq = rect(0, 0, CH, CH)
    place(0x25A0, sq, 60)
    place(0x25A1, diff(sq, rect(US, US, CH - US, CH - US)), 60)
    side = 1.12 * CH; tall = side * math.sqrt(3) / 2
    place(0x25B6, poly([(0, CC - side / 2), (tall, CC), (0, CC + side / 2)]), 60)
    over = 9; R = CH / 2 + over
    place(0x25CF, ellipse(R, CC, R, R), 60)
    place(0x25CB, diff(ellipse(R, CC, R, R), ellipse(R, CC, R - US, R - US)), 60)
    R5 = CH / (2 * math.sin(math.radians(72)))
    place(0x2605, pentagram(R5, CC - R5 * (1 - math.cos(math.radians(36))) / 2, R5, 0.382 * R5), 60)

    # ---- circled numbers ------------------------------------------------------------------------
    # The figures' vertical stem FS follows H's stem (FSK of it at Regular, FSK_BK at Black,
    # linear in the stem between); the ring is Q of FS. The ring is 1.08 cap heights across plus
    # its stroke's excess over Regular's crossbar. A single figure's flat height is FIGH of the
    # ring's inner diameter: the small-cap figure scaled, its outline offset in or out to reach
    # FS. Two figures stand PAIRH of that height, condensed (no narrower than KXMIN of their
    # height scale) until the pair, leaned in an italic, keeps MARGIN of the ring inside the inner
    # circle, the height lowered only if that fails; their horizontals are offset to PH of the
    # singles' and their verticals widened sideways to PV of FS (PV, PH: 0.90, 0.95 at Regular's
    # stem, 0.12 less at Black's, as Noto Sans Symbols' two-figure stems fall from 0.98 to 0.8).
    Q = c.P('UI_CN_Q', 0.8); FIGH = c.P('UI_CN_FIGH', 0.62); PAIRH = c.P('UI_CN_PAIRH', 0.95)
    FSK = c.P('UI_CN_FSK', 0.82); FSK_BK = c.P('UI_CN_FSK_BK', 0.64)
    GAPK = c.P('UI_CN_GAP', 0.05); KXMIN = c.P('UI_CN_KXMIN', 0.75); MARGK = c.P('UI_CN_MARGIN', 0.025)
    HS = width(hspans(hp, CH * 0.25)[0])                               # H's stem
    tw = (HS - 0.0936 * CH) / ((0.2397 - 0.0936) * CH)                 # 0 at Regular's stem (66 of 705), 1 at Black's (169)
    FS = (FSK + (FSK_BK - FSK) * tw) * HS; RS = Q * FS
    PV, PH = 0.90 - 0.12 * tw, 0.95 - 0.12 * tw
    figs = {d: path_of(DIGITS[d] + '.sc').bounds for d in range(10)}
    sc_h = figs[1][3]
    sv = width(hspans(path_of('one.sc'), 0.45 * sc_h)[0])              # the figures' stems, unscaled: the 1's
    xm = figs[7][0] + 0.4 * (figs[7][2] - figs[7][0]); sh = width(vspans(path_of('seven.sc'), xm)[-1])   # and the 7's top bar
    D = c.P('UI_RING', 1.08) * CH + max(0.0, RS - 0.0837 * CH); RR = D / 2; RIN = RR - RS; cx = 60 + RR
    Ht = FIGH * 2 * RIN
    e1 = (FS - Ht * sv / sc_h) / (2 * (1 - sv / sc_h)); k1 = (Ht - 2 * e1) / sc_h   # scale and offset: height Ht, stem FS
    ring = upright(diff(ellipse(cx, CC, RR, RR), ellipse(cx, CC, RIN, RIN)))

    def offset(p, e):
        """p's outline moved out by e (in if e < 0), mitred."""
        if abs(e) <= 0.05: return p
        q = pathops.Path(); p.draw(q.getPen())
        q.stroke(2 * abs(e), pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
        return union(p, q) if e > 0 else diff(p, q)

    def widen(p, e, m=16):
        """p widened sideways by e on each side: offset in a frame stretched m times vertically,
        so the vertical growth is e / m."""
        if e <= 0.05: return p
        return transformed(offset(transformed(p, (1, 0, 0, m, 0, 0)), e), (1, 0, 0, 1 / m, 0, 0))
    figure = lambda d, kx, ky: transformed(path_of(DIGITS[d] + '.sc'), (kx, 0, 0, ky, 0, 0))
    gap = GAPK * D; single_hz = k1 * sh + 2 * e1

    def pair_e(kx, ky):                                                # the pair's offset and sideways widening
        ep = (PH * single_hz - ky * sh) / 2
        return ep, max(0.0, (PV * FS - (kx * sv + 2 * ep)) / 2)

    def pair(n, kx, ky):                                               # two figures, centred on the origin
        ep, eh = pair_e(kx, ky)
        a, b_ = (widen(offset(figure(d, kx, ky), ep), eh) for d in (n // 10, n % 10))
        b_ = mv(b_, a.bounds[2] + gap - b_.bounds[0])
        p = union(a, b_); pb = p.bounds
        return mv(p, -(pb[0] + pb[2]) / 2, -ky * sc_h / 2)
    hole = diff(rect(-3000, -3000, 6000, 6000), ellipse(0, 0, RIN - MARGK * D, RIN - MARGK * D))
    widest = sorted(range(10, 21), key=lambda n: -sum(figs[d][2] - figs[d][0] for d in (n // 10, n % 10)))

    def fits(kx, ky, ns=widest[:3]):
        for n in ns:
            p = pair(n, kx, ky)
            if K: p = transformed(p, (1, 0, K, 1, 0, 0))               # as the reslant will set it
            bb = pathops.op(p, hole, pathops.PathOp.INTERSECTION).bounds
            if bb and bb[2] - bb[0] > 0.5 and bb[3] - bb[1] > 0.5: return False
        return True
    ky = PAIRH * k1
    while True:
        lo, hi = KXMIN * ky, 0.95 * ky
        if fits(lo, ky):
            if fits(hi, ky): kx = hi
            else:
                for _ in range(14):
                    m = (lo + hi) / 2; lo, hi = (m, hi) if fits(m, ky) else (lo, m)
                kx = lo
            if fits(kx, ky, range(10, 21)): break
        ky *= 0.985
    ep, eh = pair_e(kx, ky)
    for n in range(1, 21):
        if n < 10:
            f = offset(figure(n, k1, k1), e1); b = f.bounds
            f = mv(f, cx - (b[0] + b[2]) / 2, CC - k1 * sc_h / 2)
        else:
            f = mv(pair(n, kx, ky), cx, CC)
        put(0x2460 + n - 1, union(ring, f), round(D + 120))
    ctx.log(f'circled numbers: ring {D:.0f} stroke {RS:.1f} ({Q} of the figure stem {FS:.1f}); one figure at {k1:.3f} '
            f'{e1:+.1f}, {Ht:.0f} tall ({FIGH} of the inner {2 * RIN:.0f}); two at {ky:.3f} by {kx:.3f} {ep:+.1f}, '
            f'widened {eh:.1f}: stems {kx * sv + 2 * ep + 2 * eh:.1f} and {ky * sh + 2 * ep:.1f} (one: {FS:.1f} and {single_hz:.1f}), '
            f'{(ky * sc_h + 2 * ep) / Ht:.2f} of its height')

    # ---- keyboard (stroke KS) ---------------------------------------------------------------------
    T = CH; sq_s = 0.27 * T; r = (T - sq_s - KS) / 4; ck = T / 2
    parts = [diff(rect(ck - sq_s / 2 - KS / 2, CC - sq_s / 2 - KS / 2, ck + sq_s / 2 + KS / 2, CC + sq_s / 2 + KS / 2),
                  rect(ck - sq_s / 2 + KS / 2, CC - sq_s / 2 + KS / 2, ck + sq_s / 2 - KS / 2, CC + sq_s / 2 - KS / 2))]
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner = (ck + sx * sq_s / 2, CC + sy * sq_s / 2)
            lc = (corner[0] + sx * r, corner[1] + sy * r)
            parts.append(diff(ellipse(lc[0], lc[1], r + KS / 2, r + KS / 2), ellipse(lc[0], lc[1], r - KS / 2, r - KS / 2)))
            parts.append(rect(corner[0] - KS / 2, min(corner[1], corner[1] + sy * r), corner[0] + KS / 2, max(corner[1], corner[1] + sy * r)))
            parts.append(rect(min(corner[0], corner[0] + sx * r), corner[1] - KS / 2, max(corner[0], corner[0] + sx * r), corner[1] + KS / 2))
    place(0x2318, union(*parts), 50)

    Wo, Ho = CH, 0.62 * CH; y0, y1 = CC - Ho / 2 + KS / 2, CC + Ho / 2 - KS / 2
    opt = union(c.stroke_line([(0, y1), (0.38 * Wo, y1), (0.62 * Wo, y0), (Wo, y0)], KS, limit=4),
                rect(0.66 * Wo, y1 - KS / 2, Wo, y1 + KS / 2))
    place(0x2325, opt, 50)

    Wa = 0.8 * CH; ws = 0.48 * Wa; yh = 0.5 * CH
    outer = [(Wa / 2, CH), (0, yh), (Wa / 2 - ws / 2, yh), (Wa / 2 - ws / 2, 0), (Wa / 2 + ws / 2, 0), (Wa / 2 + ws / 2, yh), (Wa, yh)]
    place(0x21E7, diff(poly(outer), poly(inset(outer, KS))), 55)

    reach, half = 220 * CH / 705, 176.5 * CH / 705                 # the shipped arrowhead's wings
    head = c.stroke_line([(reach, 2 * half), (0, half), (reach, 0)], KS, limit=4)
    lift = -head.bounds[1]; head = mv(head, 0, lift); ys = half + lift   # the lower barb's cap on the baseline
    xv = 0.8 * CH
    place(0x23CE, union(head, rect(KS / 2, ys - KS / 2, xv, ys + KS / 2), rect(xv - KS, ys - KS / 2, xv, CH)), 50)

    Wd, xk = 1.42 * CH, 0.44 * CH
    outer = [(0, CC), (xk, 0), (Wd, 0), (Wd, CH), (xk, CH)]
    h = min(0.23 * CH, CC - KS - 0.64 * KS - 16); cxx = (xk + Wd) / 2 - 0.02 * CH
    bs = union(diff(poly(outer), poly(inset(outer, KS))),
               band((cxx - h, CC - h), (cxx + h, CC + h), 0.9 * KS), band((cxx - h, CC + h), (cxx + h, CC - h), 0.9 * KS))
    place(0x232B, bs, 50)
    ctx.log(f'{len(made)} glyphs')

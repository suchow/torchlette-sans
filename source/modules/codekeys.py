"""codekeys: the code-and-keyboard lane of the technical repertoire (font-preview/
technical-repertoire.html, items CP1 CP2 CP3 SH1 SH2 SC1 SC3 ML6 LG4 LG6).

Glyphs, drawn at every weight from this style's own measures:

- CP1, alternates (no default glyph changes): `I.serif.codekeys`, the capital I with
  flat serifs top and bottom (IBM Plex Sans's and Verdana's answer to I/l/1), in ss17 and,
  next to l, 1 or |, in ss16 (proposal 301); `l.tail.codekeys`, the l whose stem
  turns right into a short tail at the baseline (Fira Sans's, Atkinson Hyperlegible's), in
  ss18; `v.spur.codekeys`, a v with an entry spur on its left arm at the x-height, the mark
  that tells italic v from Greek nu (UTR #25 notes the pair is "not very distinct"; upsilon is
  already round-bottomed here), in ss19. The serif and spur take the H crossbar's thickness;
  the tail is the stem's own stroke bent on a quarter circle.
  I.serif is spaced so that beside a stem it lets in as much light as the plain I: its
  serif tips take a sidebearing smaller than the I's own (the SPACE_CLIP rule in glyphs()).
  Beside l, the ll ligature and | that leaves nothing to kern; beside 1 the serif meets the
  figure's foot first, so no kerning is added there either.
- CP3, keyboard symbols in the ui module's rules (cap height tall, the H crossbar as stroke,
  capped at 0.15 cap height; pictures, so they stay upright in the italics): ⎋ U+238B a
  cap-height ring broken at the upper left with an arrow leaving through the break, ⇥ U+21E5
  the shipped chevron arrow running into a bar, ⌃ U+2303 an up chevron at the top of the cap
  height, ␣ U+2423 an open box under the x-height on the baseline, ⇪ U+21EA ui's outline ⇧
  over an outline bar, ⌦ U+2326 ui's ⌫ mirrored. Proportions measured on Noto Sans Symbols2
  (SIL OFL 1.1, google/fonts ofl/notosanssymbols2, version 2.008); no outline copied. `inset`
  is ui.py's helper, repeated here because modules cannot import each other.
- SH1, U+2581-2588 ▁▂▃▄▅▆▇█: ss16's spark bars (122) drawn again as encoded glyphs, the
  same 90-unit bar in a 130-unit cell on the baseline, eighths of the tallest spark bar (608).
  They are separate glyphs, not cmap entries for `spark.N`, so typed block elements never
  show an ss16 glyph with ss16 off. Like the spark bars, they lean in an italic.
- SC1, ♭ ♮ ♯ U+266D-266F and ♩ ♪ ♫ U+2669-266B, monoline in the stems' weight with the
  accidentals' slanted bars heavier, as music engraving sets them (proportions from Noto
  Music, SIL OFL 1.1, ofl/notomusic; no outline copied). `sharp.note.codekeys` and
  `flat.note.codekeys` are the forms ss16 puts after a note letter (tighter left side).
- LG4, `uni25B8` ▸ (Knuth's mark for a recommended exercise: ui's ▶ at 0.6 of its size,
  centred at half the x-height) and the rating badge `rate.*.codekeys`: an outline pill in
  the crossbar's half weight around small-cap letters and small-cap figures.
- LG6, ⤙ U+2919 leftwards arrow-tail, the encoded form closest to Peirce's claw −<: the
  minus's bar running into the shipped arrowhead turned to open rightwards. A heritage glyph
  for the specimen book; no rule makes it from -<.
- CP2: `uni2254.ss02.codekeys`, `uni21A6.ss02.codekeys` (and ⊢ ⊨ when present): copies, made in
  the features phase, of the symbols module's ≔ ↦ as ligature outputs, classed and given
  carets by otfeatures.
- SH2, ML6: `*.ein.codekeys` (copies of the small capitals, the tuple space and the shipped
  arrow, for einops patterns) and `g.argop.codekeys`, `g.lse.codekeys`, `m.lse.codekeys`
  (the letter with a thin space after it, for operator names).

Layout:

- ss02 (CP2), placed after build.py's ss02 (after='main'), so `->` is already an arrow:
  != → ≠ (not in !==), := → ≔ (not in ::= or :==); <- → ← is left to ss16's proposal 102,
  which already makes it with the guard x<-1 needs (in ss02 too it would take the rule from
  ss16, whose check expects ss16 to make it); and,
  space-guarded ` ~> ` → ⇝ (U+21DD, always supplied by this module in the native
  arrow/wave style). When the font has the target signs, also space-guarded
  ` |- ` → ⊢, ` |= ` → ⊨, ` |-> ` → ↦ (the turnstile module draws ⊢ and ⊨).
  In the app these never reach code: code is set in
  the editor and in `code`/`pre` in the monospace face (web/src/styles/app.css), which has
  none of these features.
- ss16 proposals (ids 301-306, above sigmoid's 217): 301 I.serif beside l, 1 or |; 302 F# C#
  ... (capital A-G, a sharp, then no letter) → F♯, and Bb Eb → B♭ E♭ (not Ab, Db, Gb, Cb, Fb:
  ab, database, gigabit; and not after a figure and a space, where Eb is a unit); 303 einops
  patterns, two or more single-letter axes before -> (or →), set in small capitals with tuple
  spaces and the arrow, parenthesised groups included (b c h w -> b (h w) c), when every
  axis letter stands alone between spaces, brackets or quotes (an axis at the very edge of a
  text run stays as typed); 304 the unit
  space before bit(s), nat(s), Sh after a figure (no glyph: build.py's `space.unit`); 305
  argmax, argmin as arg max, arg min with a thin space (1/6 em, amsmath's \\argmax) and
  logsumexp with hair spaces, whole words only (softmax already has ss16's logotype, 86);
  306 [M20], [HM45] and, after ▸ and an exercise number, [20] as a rating badge.
- ss17, ss18, ss19: the CP1 alternates above (tags taken by this module).

Nothing existing is changed. Code points outside the Makefile's web subset ranges:
U+2423 (Control Pictures), U+2581-2588 (Block Elements), U+2669-266F (Miscellaneous
Symbols).
"""
import math
from copy import deepcopy

import pathops

TAGS = {'I': 'ss17', 'l': 'ss18', 'v': 'ss19'}
ID_I, ID_NOTE, ID_EIN, ID_BITS, ID_OP, ID_RATE = 301, 302, 303, 304, 305, 306
LETTERS = 'abcdefghijklmnopqrstuvwxyz'
DIG = 'zero one two three four five six seven eight nine'.split()


def inset(pts, d):
    """ui.py's: a simple polygon's outline moved inward by d with mitred corners."""
    n = len(pts)
    if sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)) < 0: pts = pts[::-1]
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]; L = math.hypot(x1 - x0, y1 - y0)
        u = ((x1 - x0) / L, (y1 - y0) / L); nrm = (-u[1], u[0])
        lines.append(((x0 + d * nrm[0], y0 + d * nrm[1]), u))

    def meet(a, b):
        (px, py), (ux, uy) = a; (qx, qy), (vx, vy) = b
        t = ((qx - px) * vy - (qy - py) * vx) / (ux * vy - uy * vx)
        return (px + t * ux, py + t * uy)
    while True:
        m = len(lines)
        verts = [meet(lines[i - 1], lines[i]) for i in range(m)]
        bad = [i for i in range(m) if (verts[(i + 1) % m][0] - verts[i][0]) * lines[i][1][0]
               + (verts[(i + 1) % m][1] - verts[i][1]) * lines[i][1][1] < 0]
        if not bad or m <= 3: return verts
        del lines[bad[0]]


def blob(pts):
    """A closed path of cubic segments: pts = [start, (c1, c2, end), ...]."""
    p = pathops.Path(); pen = p.getPen(); pen.moveTo(pts[0])
    for c1, c2, e in pts[1:]: pen.curveTo(c1, c2, e)
    pen.closePath(); return p


def _squiggle_arrow(c):
    """U+21DD: native arrowhead, axis and weight, with a smooth wave shaft.

    Run in features(), after all modules' glyph constructors: symbols may supply
    U+223C. Without it, the upper native approx-sign wave is the same source.
    The uniform cubic B-spline has a fixed control structure and horizontal
    ends. Only its centreline is fitted; stroke thickness stays BAR throughout.
    Normal integer encoding and the existing final italic stage still apply.
    """
    arrow = c.path_of('arrowright')
    cmap = c.font.getBestCmap()
    if 0x223C in cmap:
        native_wave = c.path_of(cmap[0x223C])
    else:
        waves = []
        for contour in c.path_of('approxequal').contours:
            part = pathops.Path(); contour.draw(part.getPen()); waves.append(part)
        native_wave = max(waves, key=lambda part: part.bounds[1])
    amplitude = max(1.0, (native_wave.bounds[3] - native_wave.bounds[1] - c.BAR) / 2)
    control = [(-60, 0), (0, 0), (60, 0), (120, 2), (200, 0),
               (280, -2), (340, 0), (400, 0), (460, 0)]
    curve = pathops.Path(); pen = curve.getPen()
    def mix(*terms):
        return tuple(sum(weight * point[axis] for weight, point in terms) for axis in (0, 1))
    for i in range(len(control) - 3):
        a, b, d, e = control[i:i + 4]
        start = mix((1/6, a), (4/6, b), (1/6, d))
        if i == 0: pen.moveTo(start)
        pen.curveTo(mix((2/3, b), (1/3, d)), mix((1/3, b), (2/3, d)),
                    mix((1/6, b), (4/6, d), (1/6, e)))
    pen.endPath()
    head_start = min(330, 380 - 35 * c.SM - 10)  # build.py's native arrow-head cut
    bounds = curve.bounds
    sx = (head_start + c.BAR - arrow.bounds[0]) / (bounds[2] - bounds[0])
    sy = 2 * amplitude / (bounds[3] - bounds[1])
    shaft = c.transformed(curve, (sx, 0, 0, sy, arrow.bounds[0] - sx * bounds[0], c.LIN_AXIS))
    shaft.stroke(c.BAR, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    shaft.convertConicsToQuads()
    head = c.clip(arrow, (head_start, -1000, 2000, 2000))
    return c.union(shaft, head)


def glyphs(ctx):
    c = ctx
    rect, poly, union, diff, clip, band = c.rect, c.poly, c.union, c.diff, c.clip, c.band
    ellipse, transformed, path_of, W, mv, mirror = c.ellipse, c.transformed, c.path_of, c.W, c.mv, c.mirror
    hspans, vspans, stroke_line = c.hspans, c.vspans, c.stroke_line
    K, YC = c.ITALIC_K, c.ITALIC_YC
    order = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()
    made = ctx.made = []
    width = lambda s: s[1] - s[0]
    mid = lambda s: (s[0] + s[1]) / 2

    hp = path_of('H'); Hb = hp.bounds; CH = Hb[3]; CC = CH / 2
    US = width(vspans(hp, (Hb[0] + Hb[2]) / 2)[0])                # H's crossbar
    KS = min(US, 0.15 * CH)                                        # ui's keyboard stroke
    XH = c.XH; A, BAR, SM = c.LIN_AXIS, c.BAR, c.SM
    lp = path_of('l'); LST = hspans(lp, 300)[0]; LW = width(LST)   # the l's stem
    ctx.log(f'cap {CH:.0f}, crossbar {US:.1f}, keyboard stroke {KS:.1f}, l stem {LW:.1f}')

    def upright(p, cy=CC):
        if not K: return p
        return transformed(mv(p, K * (cy - YC)), (1, 0, -K, 1, K * YC, 0))

    def put(name, path, adv, cp=None, base=True):
        assert name not in order, name
        if cp is not None: assert cp not in cmap, f'U+{cp:04X} already mapped to {cmap[cp]}'
        c.add(name, path, adv)
        if base: c.GDEF_CLASS[name] = 1                        # else otfeatures classes it (a ligature: 2, with carets)
        if cp is not None: ctx.map(cp, name)
        made.append(name); return name

    def fit(p, lsb, rsb=None):
        b = p.bounds; p = mv(p, lsb - b[0])
        return p, round((b[2] - b[0]) + lsb + (lsb if rsb is None else rsb))

    def place(cp, p, lsb, cy=CC, keep_upright=True, name=None, rsb=None):
        q, adv = fit(p, lsb, rsb)
        return put(name or f'uni{cp:04X}', upright(q, cy) if keep_upright else q, adv, cp)

    # ---- CP1: alternates ------------------------------------------------------------------
    ip = path_of('I'); Ib = ip.bounds; IST = hspans(ip, CC)[0]; IW = width(IST)
    sl = round(0.17 * CH + 0.35 * IW)                              # each serif's reach past the stem
    st = US * 0.92
    lsb_I = Ib[0]; x0 = IST[0] - sl
    I_serif = union(ip, rect(x0, 0, IST[1] + sl, st), rect(x0, CH - st, IST[1] + sl, CH))
    # The serif tips' sidebearing, so that the I.serif sits beside a stem (H, l, |) as the
    # plain I does. The light between two shapes is the mean over the cap height of each
    # row's gap, a row counting only up to SPACE_CLIP times the plain stem-to-stem gap RI
    # (white deeper than that does not read as more space). With the serifs filling a
    # fraction phi of the rows, phi * t + (1 - phi) * SPACE_CLIP * RI = RI gives the tip gap t.
    # SPACE_CLIP is IBM Plex Sans's: 1.044 makes its serifed I beside H equal H beside H.
    SPACE_CLIP = 1.044
    RI = 2 * lsb_I; phi = 2 * st / CH
    tip = RI * (1 - (1 - phi) * SPACE_CLIP) / phi - lsb_I
    I_serif = mv(I_serif, tip - x0)
    put('I.serif.codekeys', I_serif, round(2 * tip + IW + 2 * sl))
    ctx.log(f'I.serif: serif reach {sl}, tip sidebearing {tip:.0f} (plain I {lsb_I:.0f})')

    lb = lp.bounds; R = 0.20 * CH + 0.5 * LW                       # tail radius to the stroke's centre
    xc = mid(LST); cx, cy = xc + R, -9 + R + LW / 2               # outer edge 9 under the baseline, as o's overshoot
    hor = LW * 0.86                                                # the tail thins a little as it turns level
    ring = diff(ellipse(cx, cy, R + LW / 2, R + LW / 2), ellipse(cx, cy + (LW - hor) / 2, R - LW / 2, R - hor / 2 - (LW - hor) / 2))
    arc = clip(ring, (xc - LW, -50, cx, cy))
    tip = cx + 0.30 * R
    l_tail = union(clip(lp, (-500, cy - 0.5, 2000, 2000)), arc, rect(cx - 1, -9, tip, -9 + hor))
    put('l.tail.codekeys', l_tail, W('l') + (tip - lb[2]) + 10)

    vp = path_of('v'); vb = vp.bounds; VL = hspans(vp, XH - 2)[0]
    sp = round(0.9 * width(VL) + 50)                               # the spur's reach left of the arm
    v_spur = mv(union(vp, clip(union(rect(VL[0] - sp, XH - US * 0.9, mid(VL), XH)), (-500, 0, 2000, XH))), sp)
    put('v.spur.codekeys', v_spur, W('v') + sp)

    # ---- CP3: keyboard (ui's rules) -------------------------------------------------------------
    reach, half = 220 * CH / 705, 176.5 * CH / 705                 # the shipped arrowhead's wings at cap scale
    def chev(tip, ang):
        """An open chevron pointing along angle ang (degrees), its tip at tip, stroke KS."""
        a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
        p1 = (tip[0] - reach * ux + half * nx, tip[1] - reach * uy + half * ny)
        p2 = (tip[0] - reach * ux - half * nx, tip[1] - reach * uy - half * ny)
        return stroke_line([p1, tip, p2], KS, limit=4)

    # ⎋: the ring opening and arrow share one upper-left diagonal axis.
    Rr = CH / 2; rc = (Rr, CC)
    axis, gap_half = 135, 42.5
    ux, uy = math.cos(math.radians(axis)), math.sin(math.radians(axis))
    ring = diff(ellipse(rc[0], rc[1], Rr, Rr), ellipse(rc[0], rc[1], Rr - KS, Rr - KS))
    def gap_ray(angle, radius):
        return (rc[0] + radius * math.cos(math.radians(angle)),
                rc[1] + radius * math.sin(math.radians(angle)))
    gap = poly([rc, gap_ray(axis - gap_half, 2 * Rr),
                gap_ray(axis, 3 * Rr), gap_ray(axis + gap_half, 2 * Rr)])
    ring = diff(ring, gap)
    tipe = (rc[0] + math.sqrt(2) * 0.80 * Rr * ux, rc[1] + math.sqrt(2) * 0.80 * Rr * uy)
    shaft_start = (rc[0] - math.sqrt(2) * 0.12 * Rr * ux, rc[1] - math.sqrt(2) * 0.12 * Rr * uy)
    shaft_end = (tipe[0] - KS * 0.5 * ux, tipe[1] - KS * 0.5 * uy)
    esc = union(ring, chev(tipe, axis), stroke_line([shaft_start, shaft_end], KS))
    place(0x238B, esc, 50)

    # ⇥: the arrow runs into a bar
    Wt = 0.95 * CH; xbar = Wt - KS / 2
    tab = union(rect(0, CC - KS / 2, xbar - KS * 0.7, CC + KS / 2), chev((xbar - KS * 0.75, CC), 0),
                rect(xbar - KS / 2, CC - 1.25 * half, xbar + KS / 2, CC + 1.25 * half))
    place(0x21E5, tab, 50)

    # ⌃: an up chevron at the top of the cap height
    wc, hc = 0.36 * CH, 0.30 * CH
    ctl = stroke_line([(-wc, CH - hc), (0, CH - KS * 0.75), (wc, CH - hc)], KS, limit=4)
    ctl = clip(ctl, (-2000, -100, 2000, CH))
    place(0x2303, ctl, 70)

    # ␣: an open box on the baseline
    wb, hb, yb = 0.9 * CH, 0.27 * CH, -0.06 * CH
    spc = union(rect(0, yb, wb, yb + KS), rect(0, yb, KS, yb + hb), rect(wb - KS, yb, wb, yb + hb))
    place(0x2423, spc, 55)

    # ⇪: ui's outline ⇧ over an outline bar
    Wa = 0.8 * CH; ws = 0.48 * Wa
    hbar = 2 * KS + 0.07 * CH; gapb = 0.09 * CH; y_a = hbar + gapb; yh = y_a + 0.5 * (CH - y_a)
    outer = [(Wa / 2, CH), (0, yh), (Wa / 2 - ws / 2, yh), (Wa / 2 - ws / 2, y_a), (Wa / 2 + ws / 2, y_a), (Wa / 2 + ws / 2, yh), (Wa, yh)]
    bx0, bx1 = Wa / 2 - ws / 2, Wa / 2 + ws / 2
    caps = union(diff(poly(outer), poly(inset(outer, KS))), diff(rect(bx0, 0, bx1, hbar), rect(bx0 + KS, KS, bx1 - KS, hbar - KS)))
    place(0x21EA, caps, 55)

    # ⌦: ui's ⌫ mirrored
    Wd, xk = 1.42 * CH, 0.44 * CH
    outer = [(0, CC), (xk, 0), (Wd, 0), (Wd, CH), (xk, CH)]
    h = min(0.23 * CH, CC - KS - 0.64 * KS - 16); cxx = (xk + Wd) / 2 - 0.02 * CH
    bs = union(diff(poly(outer), poly(inset(outer, KS))),
               band((cxx - h, CC - h), (cxx + h, CC + h), 0.9 * KS), band((cxx - h, CC + h), (cxx + h, CC - h), 0.9 * KS))
    place(0x2326, mirror(bs, Wd / 2), 50)

    # ---- SH1: block elements as the spark bars ------------------------------------------------------
    for i in range(1, 9):
        put(f'uni{0x2580 + i:04X}', rect(20, 0, 110, round(608 * i / 8)), 130, 0x2580 + i)

    # ---- SC1: music ---------------------------------------------------------------------------------
    MS = min(LW * 0.78, 52 + 0.3 * LW)                             # the accidentals' thin verticals, held back in the heavy weights
    MB = min(LW * 1.25, 66 + 0.6 * LW)                             # their slanted bars, heavier as engraved
    GROW = 0.9 * (MS - 51.5)                                       # the signs widen as the strokes grow, so the counters stay open
    slope = 0.36                                                   # the bars' rise across the sign
    def sbar(x0, x1, y):                                           # a slanted bar centred at height y over x0..x1
        xm = (x0 + x1) / 2
        return poly([(x0, y - MB / 2 + slope * (x0 - xm)), (x1, y - MB / 2 + slope * (x1 - xm)),
                     (x1, y + MB / 2 + slope * (x1 - xm)), (x0, y + MB / 2 + slope * (x0 - xm))])
    # ♯: two verticals (the right one higher), two heavy bars rising to the right
    ws_ = 0.56 * CH + 1.5 * GROW; v1, v2 = 0.30 * ws_, 0.70 * ws_
    sharp = union(rect(v1 - MS / 2, -0.17 * CH, v1 + MS / 2, 1.05 * CH), rect(v2 - MS / 2, -0.10 * CH, v2 + MS / 2, 1.12 * CH),
                  sbar(0, ws_, 0.30 * CH), sbar(0, ws_, 0.68 * CH))
    place(0x266F, sharp, 45, keep_upright=False)
    put('sharp.note.codekeys', mv(fit(sharp, 45)[0], -30), fit(sharp, 45)[1] - 40)
    # ♮: the left vertical from the top down to the lower bar, the right from the upper bar to the bottom
    wn = 0.42 * CH + GROW; n1, n2 = MS / 2, wn - MS / 2
    lo_y, hi_y = 0.22 * CH, 0.66 * CH
    nat = union(rect(n1 - MS / 2, lo_y - slope * wn / 2, n1 + MS / 2, 1.08 * CH),
                rect(n2 - MS / 2, -0.32 * CH, n2 + MS / 2, hi_y + slope * wn / 2),
                sbar(0, wn, lo_y), sbar(0, wn, hi_y))
    place(0x266E, nat, 55, keep_upright=False)
    # ♭: a stem to above the cap height, a bowl that swells right and closes to a point at its foot
    fs = MS * 1.1; bw = 0.40 * CH; top_b = 0.56 * CH
    kx = 1 + 1.6 * GROW / (0.2 * CH)                               # the bowl widens with the weight
    xs_ = fs; X = lambda f_: xs_ + (f_ - 0.08) * CH * kx; T_ = min(MB * 0.95, 0.13 * CH + 0.2 * LW); t_ = MS * 0.8; Cq = CH
    outer_b = blob([(xs_ - 1, 0.02 * Cq), ((xs_ + 0.14 * Cq, 0.10 * Cq), (X(0.30), 0.22 * Cq), (X(0.30), 0.37 * Cq)),
                    ((X(0.30), 0.49 * Cq), (X(0.25), 0.57 * Cq), (X(0.17), 0.57 * Cq)),
                    ((X(0.11), 0.57 * Cq), (xs_ + 0.07 * Cq, 0.53 * Cq), (xs_ - 8, 0.44 * Cq))])   # into the stem at a clear angle, as b's bowl
    xr_ = X(0.30) - T_; xt_ = min(X(0.165), xr_ - 0.04 * CH)        # the counter's right side and the top of its curve
    inner_b = blob([(xs_ - 2, 0.14 * Cq), ((xs_ + 0.10 * Cq, 0.19 * Cq), (X(0.30) - T_, 0.27 * Cq), (X(0.30) - T_, 0.37 * Cq)),
                    ((xr_, 0.47 * Cq - t_ / 2), ((xr_ + xt_) / 2 + 4, 0.57 * Cq - t_), (xt_, 0.57 * Cq - t_)),
                    ((min(X(0.10), xt_ - 10), 0.57 * Cq - t_), (xs_ + 0.08 * Cq, 0.47 * Cq), (xs_ - 10, 0.37 * Cq))])
    flat = union(rect(0, -0.0 * CH, fs, 1.12 * CH), diff(outer_b, inner_b))
    flat = clip(flat, (-1, -1, 2000, 2000))
    place(0x266D, flat, 55, keep_upright=False)
    put('flat.note.codekeys', mv(fit(flat, 55)[0], -35), fit(flat, 55)[1] - 45)
    # notes: a filled head leaning up at 20 degrees, a stem on its right
    hw, hh, ang = 0.215 * CH, 0.15 * CH, math.radians(20)
    def head(cx, cy):
        e = ellipse(0, 0, hw, hh); co, si = math.cos(ang), math.sin(ang)
        return transformed(e, (co, si, -si, co, cx, cy))
    NS = MS * 0.95; stem_top = 1.10 * CH
    def note(cx, top=stem_top):
        hd = head(cx, hh); xs = hd.bounds[2]                         # the stem's right edge on the head's rightmost point, where its side is vertical
        t_ = math.atan2(-hh * math.sin(ang), hw * math.cos(ang))     # the parameter of the head's rightmost point
        ty = hw * math.cos(t_) * math.sin(ang) + hh * math.sin(t_) * math.cos(ang)
        return union(hd, rect(xs - NS, hh + ty - 1, xs, top)), xs
    q, xs = note(hw + 10)
    place(0x2669, q, 40, keep_upright=False)
    # ♪: a flag that leaves the stem top and curls down and out
    FW = MB * 1.6; T0 = stem_top
    flag_o = blob([(xs - NS / 2, T0), ((xs + 0.02 * CH, T0 - 0.12 * CH), (xs + 0.33 * CH, T0 - 0.22 * CH), (xs + 0.31 * CH, T0 - 0.47 * CH)),
                   ((xs + 0.30 * CH, T0 - 0.58 * CH), (xs + 0.27 * CH, T0 - 0.65 * CH), (xs + 0.23 * CH, T0 - 0.71 * CH)),
                   ((xs + 0.25 * CH, T0 - 0.62 * CH), (xs + 0.25 * CH, T0 - 0.53 * CH), (xs + 0.21 * CH, T0 - 0.45 * CH)),
                   ((xs + 0.15 * CH, T0 - 0.34 * CH), (xs + 0.02 * CH, T0 - FW * 1.1), (xs - NS / 2, T0 - FW))])
    place(0x266A, union(q, flag_o), 40, keep_upright=False)
    # ♫: two notes, their stems joined by a heavy beam rising to the right
    q1, xs1 = note(hw + 10, stem_top - 0.06 * CH)
    dx2 = 0.62 * CH
    q2, xs2 = note(hw + 10 + dx2, stem_top + 0.06 * CH)
    BW = MB * 1.35
    beam = poly([(xs1 - NS, stem_top - 0.06 * CH - BW), (xs2, stem_top + 0.06 * CH - BW), (xs2, stem_top + 0.06 * CH), (xs1 - NS, stem_top - 0.06 * CH)])
    place(0x266B, union(q1, q2, beam), 40, keep_upright=False)

    # ---- LG4: ▸ and the rating badge -------------------------------------------------------------------
    side = 0.62 * 1.12 * CH; tall = side * math.sqrt(3) / 2; ty = XH / 2
    place(0x25B8, poly([(0, ty - side / 2), (tall, ty), (0, ty + side / 2)]), 70, cy=ty)
    SC_H = c.SC_H; PS = max(28, 0.42 * US); PB0, PB1 = -0.08 * CH - PS, SC_H + 0.08 * CH + PS; PR = (PB1 - PB0) / 2
    def rail(adv): return union(rect(0, PB0, adv, PB0 + PS), rect(0, PB1 - PS, adv, PB1))
    def rrect(x0, y0, x1, y1, r):                                  # a pill: a rectangle with round ends
        return union(rect(x0 + r, y0, x1 - r, y1), ellipse(x0 + r, (y0 + y1) / 2, r, (y1 - y0) / 2), ellipse(x1 - r, (y0 + y1) / 2, r, (y1 - y0) / 2))
    cap_w = PR + 30
    outer = rrect(30, PB0, 3000, PB1, PR); inner = rrect(30 + PS, PB0 + PS, 3000, PB1 - PS, PR - PS)
    put('rate.start.codekeys', clip(diff(outer, inner), (0, PB0 - 5, cap_w + 40, PB1 + 5)), cap_w + 40)
    outer = rrect(-3000, PB0, PR + 40, PB1, PR); inner = rrect(-3000, PB0 + PS, PR + 40 - PS, PB1 - PS, PR - PS)
    put('rate.end.codekeys', clip(diff(outer, inner), (-1, PB0 - 5, PR + 40 + 5, PB1 + 5)), PR + 70)
    for n in ['M', 'H'] + DIG:
        src = n + '.sc'; a = W(src)
        # Leave the rail/advance grid intact; scale every letter and figure by
        # the same factor about its cell centre, giving air above, below and
        # between characters without a weight- or rating-specific exception.
        scale = 0.80
        lettering = transformed(path_of(src), (scale, 0, 0, scale,
                                                (1 - scale) * a / 2,
                                                (1 - scale) * SC_H / 2))
        put(f'{n}.rate.codekeys', union(lettering, rail(a)), a)

    # ---- LG6: ⤙, Peirce's claw ---------------------------------------------------------------------------
    L_, H_ = 220, 176.5
    hd = poly([(-L_, -H_), (0, -13 * SM), (0, 13 * SM), (-L_, H_), (-L_ - 35 * SM, H_ - 38 * SM), (-80 * SM, 0), (-L_ - 35 * SM, -(H_ - 38 * SM))])
    xe = 420                                                       # the shaft's end, where the fork opens
    claw = union(rect(0, A - BAR / 2, xe + 10 * SM, A + BAR / 2), mv(mirror(hd, 0), xe, A))
    place(0x2919, claw, 60, keep_upright=False)

    # ---- SH2, ML6: the pattern and operator-name forms ------------------------------------------------------
    for ch in LETTERS:
        src = ch.upper() + '.sc'
        put(f'{ch}.ein.codekeys', path_of(src), W(src))
    put('space.ein.codekeys', pathops.Path(), 110)
    put('arrow.ein.codekeys', path_of('arrowright'), W('arrowright'), base=False)
    put('parenleft.ein.codekeys', path_of('parenleft'), W('parenleft'))
    put('parenright.ein.codekeys', path_of('parenright'), W('parenright'))
    put('g.argop.codekeys', path_of('g'), W('g') + 167)          # amsmath's \, : 3 mu, 1/6 em
    put('g.lse.codekeys', path_of('g'), W('g') + 83)
    put('m.lse.codekeys', path_of('m'), W('m') + 83)

    ctx.ss16_owner(ID_I, ['I.serif.codekeys'])
    ctx.ss16_owner(ID_NOTE, ['sharp.note.codekeys', 'flat.note.codekeys'])
    ctx.ss16_owner(ID_EIN, [f'{ch}.ein.codekeys' for ch in LETTERS] + ['space.ein.codekeys', 'arrow.ein.codekeys', 'parenleft.ein.codekeys', 'parenright.ein.codekeys'])
    ctx.ss16_owner(ID_OP, ['g.argop.codekeys', 'g.lse.codekeys', 'm.lse.codekeys'])
    ctx.ss16_owner(ID_RATE, ['rate.start.codekeys', 'rate.end.codekeys'] + [f'{n}.rate.codekeys' for n in ['M', 'H'] + DIG])
    ctx.log(f'{len(made)} glyphs')


def features(ctx):
    c = ctx; J = ' '.join
    have = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()

    # U+21DD is an encoded symbol as well as the prose-only ~> output. Add it
    # here, after all glyph phases, so the native U+223C wave is available.
    if 0x21DD not in cmap:
        c.add('uni21DD', _squiggle_arrow(c), c.W('arrowright'))
        c.GDEF_CLASS['uni21DD'] = 1
        c.map(0x21DD, 'uni21DD')
        ctx.made.append('uni21DD')
        cmap = c.font.getBestCmap()

    # ---- CP2: ss02, after build.py's ss02 (-> is an arrow by now) ----------------------------------------
    def lig(cp):
        """A copy of another module's sign (symbols' ≔ ↦, the turnstiles) as the output of an ss02
        ligature, made here, once every module's glyphs exist, and left unclassed so that
        otfeatures classes it as a ligature and gives it carets; the encoded glyph keeps its
        own class."""
        src = cmap[cp]; name = f'uni{cp:04X}.ss02.codekeys'
        if cp == 0x21DD:
            # This new symbol was just encoded above. Reinterpreting its quadratic
            # path drops implied points; later grid/polish steps can then change
            # the filled shape differently. Keep its complete encoded geometry.
            # Leave the clone unclassed: otfeatures infers its ligature class and
            # carets from the substitution, while the encoded sign stays a base.
            order = list(c.font.getGlyphOrder())
            assert name not in order, name
            c.glyf[name] = deepcopy(c.glyf[src])
            c.hmtx[name] = tuple(c.hmtx[src])
            c.font.setGlyphOrder(order + [name])
        else:
            c.add(name, c.path_of(src), c.W(src))
        return name
    rules = ['  ignore sub exclam\' equal\' equal;', '  ignore sub equal exclam\' equal\';', "  sub exclam' equal' by notequal;",
             "  ignore sub colon colon' equal';", "  ignore sub colon' equal' equal;"]
    if 0x2254 in cmap: rules.append(f"  sub colon' equal' by {lig(0x2254)};")   # symbols draws ≔
    turn = [(0x21DD, "space asciitilde' greater' space"), (0x21A6, "space bar' arrowright' space"), (0x22A2, "space bar' hyphen' space"), (0x22A8, "space bar' equal' space")]
    ctx.turnstiles = []
    for cp, ctxt in turn:
        if cp in cmap:
            rules.append(f'  sub {ctxt} by {lig(cp)};'); ctx.turnstiles.append(cp)
    ctx.log('ss02 turnstile rules for', [f'U+{cp:04X}' for cp in ctx.turnstiles] or 'none (no ⊢ ⊨ glyphs in this build)')
    ctx.gsub('lookup CODEKEYS_SS02 {\n' + '\n'.join(rules) + '\n} CODEKEYS_SS02;\nfeature ss02 { lookup CODEKEYS_SS02; } ss02;\n', after='main')

    # ---- CP1: ss17-19 alternates --------------------------------------------------------------------------
    ctx.gsub(f"feature {TAGS['I']} {{ featureNames {{ name \"Capital I with serifs\"; }}; sub I by I.serif.codekeys; }} {TAGS['I']};\n"
             f"feature {TAGS['l']} {{ featureNames {{ name \"l with a tail\"; }}; sub l by l.tail.codekeys; }} {TAGS['l']};\n"
             f"feature {TAGS['v']} {{ featureNames {{ name \"v with a spur (not nu)\"; }}; sub v by v.spur.codekeys; }} {TAGS['v']};\n", after='ss16')

    # ---- ss16 front: whole-word operator names (305), on plain letters ----------------------------------------
    front = []
    for word, pos, glyph in (('argmax', [2], ['g.argop.codekeys']), ('argmin', [2], ['g.argop.codekeys']),
                             ('logsumexp', [2, 5], ['g.lse.codekeys', 'm.lse.codekeys'])):
        s = list(word); marked = J(x + "'" for x in s)
        for p, g in zip(pos, glyph):
            front.append(f'lookup CODEKEYS_OP_{word}_{p} {{ sub {s[p]} by {g}; }} CODEKEYS_OP_{word}_{p};')
        marks = [x + "'" for x in s]
        for p in pos: marks[p] += f' lookup CODEKEYS_OP_{word}_{p}'
        front.append(f'lookup CODEKEYS_OP_{word} {{\n  ignore sub [@S16_WORD period] {marked};\n  ignore sub {marked} @S16_WORD;\n  sub {J(marks)};\n}} CODEKEYS_OP_{word};')
        front.append(f'feature ss16 {{ lookup CODEKEYS_OP_{word}; }} ss16;')
    ctx.gsub('\n'.join(front) + '\n', after='ss16_front')

    # ---- ss16 tail ----------------------------------------------------------------------------------------------
    D, WD, LET = '@S16_D', '@S16_WD', '@S16_LET'
    t = []
    # 301: the serifed I beside l, 1, | or another I
    NB = '[l l_l l.tail.codekeys one one.pnum one.osf one.tosf bar]'
    t.append(f'lookup CODEKEYS_I {{\n  sub {NB} I\' by I.serif.codekeys;\n  sub I\' {NB} by I.serif.codekeys;\n}} CODEKEYS_I;')
    # 302: note names
    t.append('lookup CODEKEYS_NOTE {\n'
             '  ignore sub @S16_WORD [A B C D E F G] numbersign\';\n'
             '  ignore sub [A B C D E F G] numbersign\' [@S16_LET numbersign underscore];\n'
             '  sub [A B C D E F G] numbersign\' by sharp.note.codekeys;\n'
             f'  ignore sub {D} space [B E] b\';\n'
             '  ignore sub @S16_WORD [B E] b\';\n'
             '  ignore sub [B E] b\' [@S16_LET underscore];\n'
             '  sub [B E] b\' by flat.note.codekeys;\n} CODEKEYS_NOTE;')
    # 303: einops patterns. The arrow is the anchor: two or more single-letter axes (or a
    # parenthesised group) before it, a single letter or a group after it, each letter standing
    # alone (a space, bracket or quote on both sides). From the arrow the marking runs leftwards
    # (a reverse chain, whose backtrack still sees the plain text) and rightwards. An axis at
    # the very start or end of a text run has no context glyph to show it stands alone and is
    # left as typed (so the pattern is marked only in part); a letter of a longer word is never marked.
    LC = '[' + J(LETTERS) + ']'; EL = '[' + J(f'{ch}.ein.codekeys' for ch in LETTERS) + ']'
    OPEN = '[space parenleft quotesingle quotedbl quoteleft quoteright quotedblleft quotedblright]'
    CLOSE = '[space parenright quotesingle quotedbl quoteright quotedblright comma period]'
    t.append(f'@CODEKEYS_LC = {LC};\n@CODEKEYS_EL = {EL};')
    anchor = []
    for ar in ("hyphen' greater'", "arrowright'"):
        for right in (f'@CODEKEYS_LC {CLOSE}', 'parenleft @CODEKEYS_LC'):
            for left in (f'{OPEN} @CODEKEYS_LC space @CODEKEYS_LC space', f'{OPEN} @CODEKEYS_LC space @CODEKEYS_LC parenright space',
                         'parenright space @CODEKEYS_LC space'):
                anchor.append(f'  sub {left} {ar} space {right} by arrow.ein.codekeys;')
    t.append('lookup CODEKEYS_EIN1 {\n' + '\n'.join(anchor) + '\n} CODEKEYS_EIN1;')
    TOK = '[@CODEKEYS_EL parenleft.ein.codekeys arrow.ein.codekeys]'
    t.append('lookup CODEKEYS_EIN2 {\n'
             f'  rsub {OPEN} @CODEKEYS_LC space\' {TOK} by space.ein.codekeys;\n'
             f'  rsub parenright space\' {TOK} by space.ein.codekeys;\n'
             '  rsub parenright\' [space.ein.codekeys arrow.ein.codekeys] by parenright.ein.codekeys;\n'
             f'  rsub {OPEN} @CODEKEYS_LC\' [space.ein.codekeys parenright.ein.codekeys] by @CODEKEYS_EL;\n'
             '  rsub parenleft\' @CODEKEYS_EL by parenleft.ein.codekeys;\n'
             '} CODEKEYS_EIN2;')
    t.append('lookup CODEKEYS_EIN3 {\n'
             f'  sub [arrow.ein.codekeys @CODEKEYS_EL parenleft.ein.codekeys parenright.ein.codekeys] space\' @CODEKEYS_LC {CLOSE} by space.ein.codekeys;\n'
             '  sub [arrow.ein.codekeys @CODEKEYS_EL parenright.ein.codekeys] space\' parenleft @CODEKEYS_LC by space.ein.codekeys;\n'
             f'  sub [space.ein.codekeys parenleft.ein.codekeys] @CODEKEYS_LC\' {CLOSE} by @CODEKEYS_EL;\n'
             '  sub space.ein.codekeys parenleft\' @CODEKEYS_LC by parenleft.ein.codekeys;\n'
             '  sub @CODEKEYS_EL parenright\' by parenright.ein.codekeys;\n'
             '} CODEKEYS_EIN3;')
    # 304: information units after a figure
    units = ['b i t s', 'n a t s', 'b i t', 'n a t', 'S h']
    t.append('lookup CODEKEYS_BITS {\n' + '\n'.join(r for u in units for r in (f"  ignore sub {D} space' {u} [{WD} hyphen];", f"  sub {D} space' {u} by space.unit;")) + '\n} CODEKEYS_BITS;')
    # 306: exercise ratings
    RD = '[' + J(f'{d}.rate.codekeys' for d in DIG) + ']'
    t.append(f'@CODEKEYS_RATE_DST = [' + J(f'{d}.rate.codekeys' for d in DIG for n in c.FORMS[d]) + '];\n@CODEKEYS_RD = ' + RD + ';')
    r1 = [f'  ignore sub @S16_WORD bracketleft\';',
          f"  sub bracketleft' M {D} {D} bracketright by rate.start.codekeys;",
          f"  sub bracketleft' H M {D} {D} bracketright by rate.start.codekeys;"]
    for n in range(1, 4):
        r1.append(f"  sub uni25B8 space {J([D] * n)} period space bracketleft' {D} {D} bracketright by rate.start.codekeys;")
    r1.append(f"  sub uni25B8 space bracketleft' {D} {D} bracketright by rate.start.codekeys;")
    t.append('lookup CODEKEYS_RATE1 {\n' + '\n'.join(r1) + '\n} CODEKEYS_RATE1;')
    t.append('lookup CODEKEYS_RATE2 {\n'
             '  sub rate.start.codekeys M\' by M.rate.codekeys;\n  sub rate.start.codekeys H\' by H.rate.codekeys;\n  sub H.rate.codekeys M\' by M.rate.codekeys;\n'
             '  sub [rate.start.codekeys M.rate.codekeys @CODEKEYS_RD] @S16_DSRC\' by @CODEKEYS_RATE_DST;\n'
             '  sub @CODEKEYS_RD bracketright\' by rate.end.codekeys;\n} CODEKEYS_RATE2;')
    names = ['CODEKEYS_I', 'CODEKEYS_NOTE', 'CODEKEYS_EIN1', 'CODEKEYS_EIN2', 'CODEKEYS_EIN3', 'CODEKEYS_BITS', 'CODEKEYS_RATE1', 'CODEKEYS_RATE2']
    t.append('feature ss16 {\n' + ''.join(f'  lookup {n};\n' for n in names) + '} ss16;')
    ctx.gsub('\n'.join(t) + '\n')

"""symbols: arrows, the mathematical operators prose and lessons use, double-struck
capitals, and the Unicode spaces and joiners.

Everything here is drawn from Torchlette Sans's own parts, at each weight:

- Arrows take the head of the shipped -> arrow (`arrowright`: an open chevron whose
  wings run back 220 units and out 176.5 from the shaft, the shaft the minus's bar),
  rotated or mirrored; the double arrows take build.py's `dbl_head` / `dbl_shafts`
  (the bars of =). U+2192 is mapped to the existing `arrowright` (it had a glyph
  but no cmap entry). Harpoons (↼ ↽ ⇀ ⇁ ↿ ↾ ⇃ ⇂, and ⇌ ⇋ stacked at the bars of =) take
  one half of that head, unmoved, with the shaft run on to the tip and cut along the
  barb's outer edge (see `harpoon`); the paired arrows ⇄ ⇆ (and ⇅ ⇵, the pair turned)
  stand far enough apart that the heads, which grow with the weight, stay clear.
  ⬑ (U+2B11) stands ↑'s head and shaft on the left end of a run just above the baseline,
  in IBM Plex Sans's proportions (see `tip_up`).
- Operators sit on the math axis (`LIN_AXIS`, the minus's centre, 286.5) with the
  minus's bar (`BAR`) as their stroke; relations and the binary operators that
  stand between operands take the 600-unit cell of + = < (ink about 60..540).
  Glyph-like symbols come from the letters: the for-all is the A turned, the
  exists the E reversed, the nabla the increment (U+2206) turned.
- Double-struck capitals ℝ ℕ ℤ ℚ ℂ after Noto Sans Math's design, drawn from R N Z Q C
  (see `doublestruck` at the end of this file, which draws the whole double-struck set:
  mathletters and mathnotation take their letters and figures from it).
- Negated relations (see `negations`): ≮ ≯ ≰ ≱ ≢ ≁ ≄ ≆ ≇ ≉ ⊀ ⊁ ⋠ ⋡ ⊄ ⊅ ⊈ ⊉ ∌ ⊊ ⊋ ∤ ∦ ⋢ ⋣
  ⋪ ⋫ ⋬ ⋭ ⊮ ⊯ ↚ ↛ ↮ ⇍ ⇏ ⇎, each its base with ∉'s slash, so that KaTeX's \\not and \\n...
  commands (precomposed, or base + U+0338, which HarfBuzz recomposes) reach one glyph; and
  the bases the font lacked, ⊏ ⊐ ⊑ ⊒ ⊲ ⊳ ⊴ ⊵ ⊩ ⊫.
- Spaces: narrow no-break (the thin space's width), en and em, the en and em quads
  (as wide as the en and em spaces), the three-, four- and six-per-em spaces and the
  medium mathematical space (4/18 em); the word joiner, the zero width no-break space
  and the zero width non-joiner and joiner are empty zero-width glyphs (HarfBuzz hides
  these default-ignorables whether or not the font maps them, and they keep their effect
  on ligatures; mapped, they show nothing where an application draws the font's glyph);
  the non-breaking hyphen is a copy of the hyphen (a
  copy, so ss16's hyphen rules, which make minus signs and arrows, leave it alone).

Nothing existing is changed: no glyph outline, advance, cmap entry or lookup of
build.py's. No layout features. The double-struck letters are Lu, so build.py adds
them to ss16's word letters (as it does any module letter).

Code points outside the Makefile's web subset ranges: U+2308-230B (floor and
ceiling), U+27F0-27FF (long arrows: U+27F5/27F6 already exist and are dropped
today), U+2934/2935 (curved arrows).
"""
import math

import pathops

# Private proposal helper: explicit construction primitives, not an auto-loaded module.
import importlib.util as _join_import
from pathlib import Path as _JoinPath
_join_spec = _join_import.spec_from_file_location('_ds_join_proposal', _JoinPath(__file__).with_name('_ds_join_proposal.py'))
_join_geometry = _join_import.module_from_spec(_join_spec)
_join_spec.loader.exec_module(_join_geometry)


def glyphs(ctx):
    c = ctx
    A, BAR, SM, SV = c.LIN_AXIS, c.BAR, c.SM, c.SV
    rect, poly, union, diff, clip, band = c.rect, c.poly, c.union, c.diff, c.clip, c.band
    ellipse, transformed, path_of, W = c.ellipse, c.transformed, c.path_of, c.W
    mv, mirror = c.mv, c.mirror
    order = set(c.font.getGlyphOrder())
    cmap = c.font.getBestCmap()
    made = ctx.made = []
    VB = BAR * 1.15            # a vertical stroke of the operators (letters' stems are heavier than their bars)

    def put(cp, path, adv, name=None):
        name = name or f'uni{cp:04X}'
        assert name not in order, name
        assert cp is None or cp not in cmap, f'U+{cp:04X} already mapped to {cmap.get(cp)}'
        c.add(name, path, adv)
        c.GDEF_CLASS[name] = 1
        if cp is not None: ctx.map(cp, name)
        made.append(name)
        return name

    def rot(p, deg, cx, cy):
        a = math.radians(deg); co, si = math.cos(a), math.sin(a)
        return transformed(p, (co, si, -si, co, cx - co * cx + si * cy, cy - si * cx - co * cy))

    def flipv(p, axis): return transformed(p, (1, 0, 0, -1, 0, 2 * axis))

    def fit(p, lsb=60, rsb=None, adv=None):
        """Shift p so its ink starts at lsb; return (path, advance)."""
        b = p.bounds; p = mv(p, lsb - b[0])
        if adv is None: adv = (b[2] - b[0]) + lsb + (lsb if rsb is None else rsb)
        return p, adv

    def vcentre(p, y=None):
        b = p.bounds; return mv(p, 0, (A if y is None else y) - (b[1] + b[3]) / 2)

    def centre(p, adv):
        b = p.bounds; return mv(p, (adv - b[0] - b[2]) / 2)

    # ---- arrows --------------------------------------------------------------------
    # The head of arrowright, tip at the origin pointing along +x (see build.py's
    # "arrow for ->"): s scales the wings' reach and keeps their stroke. The wings' stroke
    # and the notch where the shaft ends (80 SM behind the tip) grow with the weight, so a
    # head shortened to s keeps the inner edge of its wings as long as Regular's: its reach
    # grows by the 45 (SM - 1) units the notch and the wing ends move back (and never past
    # the full head). Without that, a head at s = 0.6 or 0.7 in Black has its back corners
    # in front of the notch and fills in as a solid blob (the old paired and circle arrows).
    def reach(s): return s if s >= 1 else min(1.0, max(s, s + 45 * (SM - 1) / 220))

    def head(tip, deg, s=1.0):
        s = reach(s); L, Hh = 220 * s, 176.5 * s
        pts = [(-L, -Hh), (0, -13 * SM), (0, 13 * SM), (-L, Hh), (-L - 35 * SM, Hh - 38 * SM), (-80 * SM, 0),
               (-L - 35 * SM, -(Hh - 38 * SM))]
        return mv(rot(poly(pts), deg, 0, 0), *tip)

    def arrow(p0, p1, s=1.0, both=False):
        """A shaft from p0 to p1 with the head at p1 (and at p0 when both)."""
        d = (p1[0] - p0[0], p1[1] - p0[1]); n = math.hypot(*d); u = (d[0] / n, d[1] / n)
        deg = math.degrees(math.atan2(d[1], d[0])); k = 80 * SM
        a = (p0[0] + u[0] * k, p0[1] + u[1] * k) if both else p0
        b = (p1[0] - u[0] * k, p1[1] - u[1] * k)
        out = union(band(a, b, BAR), head(p1, deg, s))
        if both: out = union(out, head(p0, deg + 180, s))
        return out

    def harpoon(p0, p1, side, s=1.0):
        """A shaft from p0 to p1 with one barb at p1: side +1 puts the barb on the left of the
        direction of travel (above a rightward shaft), -1 on the right.

        The barb is the matching half of arrowright's head, unmoved: its outer edge runs from
        13 SM off the centre line at the tip back to the wing's end. The shaft runs on to the
        tip (a harpoon has no other wing to hide its end in), and its end is cut along the
        barb's outer edge, so shaft and barb make one outline with a single point at the tip:
        the shaft's far edge meets a short flat that rises into the barb's outer edge. (The
        old harpoon clipped the head at the centre line and stopped the shaft at the head's
        notch, 80 SM short: the barb hung half a stroke off the shaft and the shaft's near
        half poked out under it.)"""
        d = (p1[0] - p0[0], p1[1] - p0[1]); n = math.hypot(*d)
        deg = math.degrees(math.atan2(d[1], d[0]))
        s = reach(s); L, Hh, t, b = 220 * s, 176.5 * s, 13 * SM, BAR / 2
        barb = poly([(0, 0), (0, t), (-L, Hh), (-L - 35 * SM, Hh - 38 * SM), (-80 * SM, 0)])
        xc = -(b - t) * L / (Hh - t)                    # where the barb's outer edge crosses the shaft's near edge
        shaft = poly([(-n, -b), (0, -b), (0, t), (xc, b), (-n, b)])
        h = union(shaft, barb)
        if side < 0: h = flipv(h, 0)
        return mv(rot(h, deg, 0, 0), *p1)

    def arc(cx, cy, r, a0, a1):
        """An open circular arc (degrees, a0 to a1, either way) as a pathops path."""
        p = pathops.Path(); pen = p.getPen()
        n = max(1, math.ceil(abs(a1 - a0) / 90)); da = math.radians((a1 - a0) / n)
        t = math.radians(a0); k = 4 / 3 * math.tan(da / 4)
        pen.moveTo((cx + r * math.cos(t), cy + r * math.sin(t)))
        for _ in range(n):
            t1 = t + da
            p1 = (cx + r * (math.cos(t) - k * math.sin(t)), cy + r * (math.sin(t) + k * math.cos(t)))
            p2 = (cx + r * (math.cos(t1) + k * math.sin(t1)), cy + r * (math.sin(t1) - k * math.cos(t1)))
            pen.curveTo(p1, p2, (cx + r * math.cos(t1), cy + r * math.sin(t1)))
            t = t1
        pen.endPath()
        return p

    def stroked(p, w=None):
        p.stroke(w or BAR, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4); p.simplify(); return p

    def arc_arrow(cx, cy, r, a0, a1, s=0.7):
        """An arc of the shaft's weight from a0 round to a1 (degrees), run on straight along its
        tangent at a1 into the head.

        The arc ends where the head's wings end, so the stroke leaves the head between the
        wings, centred, and turns only behind them; under the head it is a straight shaft
        that stops at the notch, as a straight arrow's does. (The old arc ran on under the
        head to its notch and the head pointed along the tangent there: the arc curved away
        under the inner wing, which lay along it, while the outer wing stood off the
        stroke.)"""
        sgn = 1 if a1 > a0 else -1; t = math.radians(a1)
        end = (cx + r * math.cos(t), cy + r * math.sin(t))
        u = (-math.sin(t) * sgn, math.cos(t) * sgn)
        L = 220 * reach(s) + 35 * SM                    # tip to the ends of the wings
        tip = (end[0] + u[0] * L, end[1] + u[1] * L)
        notch = (tip[0] - u[0] * 80 * SM, tip[1] - u[1] * 80 * SM)
        shaft = union(stroked(arc(cx, cy, r, a0, a1)), band(end, notch, BAR))
        return union(shaft, head(tip, math.degrees(math.atan2(u[1], u[0])), s))

    def head_back(r, s=0.7):
        """The angle (degrees) on a circle of radius r that the straight run under a head at s takes up."""
        return math.degrees((220 * reach(s) + 35 * SM - 80 * SM) / r)

    ctx.map(0x2192, 'arrowright')                                   # it had a glyph and no cmap entry
    AR = path_of('arrowright')                                     # ink 60..600, adv 660
    ARB = path_of('arrowboth')                                     # ink 60..780, adv 840
    DR, DB = path_of('arrowdblright'), path_of('arrowdblboth')     # 60..627 / 73..727

    def vert(p, deg):
        b = p.bounds; q = rot(p, deg, (b[0] + b[2]) / 2, A)
        return fit(q)
    put(0x2191, *vert(AR, 90))
    put(0x2193, *vert(AR, -90))
    put(0x2195, *vert(ARB, 90))
    put(0x21D1, *vert(DR, 90))
    put(0x21D3, *vert(DR, -90))
    put(0x21D5, *vert(DB, 90))
    put(0x21D0, mirror(DR, 350), 700)
    # diagonals: the -> arrow turned 45 degrees about its middle, set on the axis
    for cp, deg in ((0x2197, 45), (0x2196, 135), (0x2199, 225), (0x2198, 315)):
        q = rot(AR, deg, 330, A); b = q.bounds; q = mv(q, 0, A - (b[1] + b[3]) / 2)
        put(cp, *fit(q))
    # maps-to: a bar across the tail, the shaft's weight, three quarters of the head's height
    def tailbar(x): return rect(x, A - 140, x + VB, A + 140)
    put(0x21A6, union(arrow((60 + VB / 2, A), (600, A)), tailbar(60)), 660)
    put(0x21A4, mirror(path_of('uni21A6'), 330), 660)
    put(0x27FC, union(arrow((60 + VB / 2, A), (940, A)), tailbar(60)), 1000)
    # hooked arrows: the tail turns back over the shaft in a half circle
    def hooked():
        r = 100; xh = 60 + r + BAR / 2
        hook = clip(diff(ellipse(xh, A + r, r + BAR / 2, r + BAR / 2), ellipse(xh, A + r, r - BAR / 2, r - BAR / 2)),
                    (0, -500, xh, 1500))
        return union(hook, arrow((xh - 1, A), (640, A)))
    put(0x21AA, hooked(), 700)
    put(0x21A9, mirror(path_of('uni21AA'), 350), 700)
    # leftwards arrow with tip upwards (the app's reply link): ↑'s head and shaft on a
    # stem that rises from the left end of a run of the same bar. IBM Plex Sans's ⬑ sets the
    # proportions, measured and redrawn (no outline taken): the run's centre line 167 above
    # the baseline, the tip at 634 (0.9 of the cap height), the run ending 508 to the right
    # of the stem's centre, a sharp corner. The head is the -> head at full reach, as deep as
    # Plex's (255 from tip to wing ends) and narrower by the font's own wing angle.
    def tip_up(yc=167, tip=634, run=508):
        xs = 60 + 176.5                                  # the left wing's outer point at the lsb
        stem = rect(xs - BAR / 2, yc - BAR / 2, xs + BAR / 2, tip - 80 * SM)
        foot = rect(xs - BAR / 2, yc - BAR / 2, xs + run, yc + BAR / 2)
        return union(stem, foot, head((xs, tip), 90)), xs + run + 60
    put(0x2B11, *tip_up())
    # long arrows: the 1000-unit cell of U+27F5/27F6
    put(0x27F7, arrow((60, A), (940, A), both=True), 1000)
    put(0x27F9, union(c.dbl_shafts(60, 813), c.dbl_head(953)), 1000)
    put(0x27F8, mirror(path_of('uni27F9'), 500), 1000)
    put(0x27FA, union(c.dbl_head(953), mirror(c.dbl_head(953), 500), c.dbl_shafts(187, 813)), 1000)
    # paired arrows: two -> at 0.6 reach, one over the other, 112 above and below the axis
    # or further apart, so that each arrow stays 0.8 of a bar clear of the other (the heads'
    # inner wings grow with the weight and reach towards the other shaft and head).
    PS = 0.6
    def one(y, right): return arrow((60, y), (600, y), s=PS) if right else arrow((600, y), (60, y), s=PS)
    def apart(p, q, gap):
        """Whether paths p and q are at least gap apart (q grown by gap, mitred, misses p)."""
        g = pathops.Path(); q.draw(g.getPen()); g.stroke(2 * gap, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
        return abs(diff(p, union(q, g)).area - p.area) < 1
    PD = 112
    while not apart(one(A + PD, True), one(A - PD, False), 0.8 * BAR): PD += 2
    ctx.paired_gap = PD
    def pair(top_right, bottom_right):
        """Upper and lower arrows on the axis, each pointing right when its flag is true."""
        return union(one(A + PD, top_right), one(A - PD, bottom_right))
    put(0x21C4, pair(True, False), 660)
    put(0x21C6, pair(False, True), 660)
    # their vertical forms: the pair turned a quarter anticlockwise (up on the left, down on the right)
    def quarter(p):
        b = p.bounds; return fit(rot(p, 90, (b[0] + b[2]) / 2, A))
    put(0x21C5, *quarter(path_of('uni21C4')))
    put(0x21F5, *quarter(path_of('uni21C6')))
    # harpoons: the -> cell, shaft on the axis, the barb the matching half of the -> head
    def hp(right, side): return harpoon((60, A), (600, A), side) if right else harpoon((600, A), (60, A), side)
    put(0x21C0, hp(True, 1), 660)                  # rightwards, barb up
    put(0x21C1, hp(True, -1), 660)                 # rightwards, barb down
    put(0x21BC, hp(False, -1), 660)                # leftwards, barb up (on the right of travel)
    put(0x21BD, hp(False, 1), 660)                 # leftwards, barb down
    # upwards and downwards: the rightward harpoons turned a quarter (the vertical arrows' construction)
    def vh(right_barb_down, deg):
        return vert(path_of('uni21C1' if right_barb_down else 'uni21C0'), deg)
    put(0x21BE, *vh(True, 90))                     # upwards, barb right
    put(0x21BF, *vh(False, 90))                    # upwards, barb left
    put(0x21C2, *vh(False, -90))                   # downwards, barb right
    put(0x21C3, *vh(True, -90))                    # downwards, barb left
    # harpoon pairs: shafts at the bars of = about the axis, the barbs outside (upper barb up,
    # lower barb down), as Noto Sans Math, STIX Two Math and DejaVu Sans stack them
    HD = c.EQ_D
    put(0x21CC, union(harpoon((60, A + HD), (600, A + HD), 1), harpoon((600, A - HD), (60, A - HD), 1)), 660)
    put(0x21CB, union(harpoon((600, A + HD), (60, A + HD), -1), harpoon((60, A - HD), (600, A - HD), -1)), 660)
    # circle arrows: an open circle of the shaft's weight, open at the top; the clockwise
    # arrow's stroke ends at the upper left and runs on into the head, pointing up and to the
    # right (the anticlockwise arrow is its mirror), as Noto Sans Math and Apple Symbols draw
    # them. The circle, not the ink, is centred: across the advance, and on the middle of the
    # capitals' height, a little under the middle of the line box, so it sits centred in a button.
    R0, AE, GAP = 225, 170, 110       # radius; where the clockwise stroke ends; the open angle from there round to its start
    CY = path_of('H').bounds[3] / 2
    q = arc_arrow(0, CY, R0, AE - GAP, AE - 360)                # clockwise from the gap's right edge round to AE
    b = q.bounds; half = max(-b[0], b[2]) + 60
    put(0x21BB, mv(q, half), 2 * half)
    put(0x21BA, mv(mirror(q, 0), half), 2 * half)
    # semicircle arrows over the top: anticlockwise ends at the left pointing down, the arc cut
    # short by the head's straight run so the tip stays where the half circle would end
    q = arc_arrow(330, A - 120, 240, 0, 180 - head_back(240))
    put(0x21B6, *fit(q))
    put(0x21B7, *fit(mirror(q, 330)))
    # right then curving up / down
    def curl(up):
        r = 150; y0 = A - 150; xc = 400
        p = pathops.Path(); pen = p.getPen()
        pen.moveTo((60, y0)); pen.lineTo((xc, y0))
        k = 0.5523 * r
        pen.curveTo((xc + k, y0), (xc + r, y0 + r - k), (xc + r, y0 + r)); pen.lineTo((xc + r, A + 270 - 80 * SM))
        pen.endPath()
        q = union(stroked(p), head((xc + r, A + 270), 90))
        return q if up else flipv(q, A)
    put(0x2934, *fit(curl(True)))
    put(0x2935, *fit(curl(False)))

    # ---- operators -------------------------------------------------------------------
    TH = BAR                         # horizontal stroke of curves
    TV = BAR * 1.1                   # vertical stroke of curves
    def half_ring(cx, cy, rx, ry, keep):
        ring = diff(ellipse(cx, cy, rx, ry), ellipse(cx, cy, rx - TV, ry - TH))
        return clip(ring, keep)
    def subset_shape(x0, x1, yc, h):
        """The open-right curve of the subset sign: a half circle and two arms."""
        cx = x0 + h
        return union(half_ring(cx, yc, h, h, (-1000, -1000, cx, 2000)),
                     rect(cx - 1, yc + h - TH, x1, yc + h), rect(cx - 1, yc - h, x1, yc - h + TH))
    H = 228                                          # half height of the set signs: 58.5..514.5
    X0, X1 = 70, 530
    sub_ = subset_shape(X0, X1, A, H)
    put(0x2282, sub_, 600)
    put(0x2283, mirror(sub_, 300), 600)
    # subset-or-equal: the same curve over a bar, the stack set like <= (0..535)
    gap = 70
    hq = (535 - BAR - gap) / 2
    subeq = union(subset_shape(X0, X1, BAR + gap + hq, hq), rect(X0, 0, X1, BAR))
    put(0x2286, subeq, 600)
    put(0x2287, mirror(subeq, 300), 600)
    # element of: the subset curve with a bar through the middle
    elem = union(subset_shape(X0, X1, A, H), rect(X0 + 5, A - BAR / 2, X1 - 40, A + BAR / 2))
    put(0x2208, elem, 600)
    put(0x220B, mirror(elem, 300), 600)
    slash = band((300 - 150, A - 300), (300 + 150, A + 300), BAR)
    put(0x2209, union(elem, slash), 600)
    # cup and cap: two upright strokes and a half circle, 40..533 like the set signs
    def cup():
        r = 225; cx = 300; yb = A - 246.5; yc = yb + r
        return union(half_ring(cx, yc, r, r, (-1000, -1000, 2000, yc)),
                     rect(cx - r, yc - 1, cx - r + TV, A + 246.5), rect(cx + r - TV, yc - 1, cx + r, A + 246.5))
    put(0x222A, cup(), 600)
    put(0x2229, flipv(cup(), A), 600)
    # and / or: a wedge of the bar's weight, flat on the line
    def wedge():
        top, bot, hw = A + 246.5, A - 246.5, 215
        s = (hw / (top - bot))
        q = stroked_line([(300 - hw - 60 * s, bot - 60), (300, top - BAR * 0.9), (300 + hw + 60 * s, bot - 60)], BAR * 1.08)
        return clip(q, (0, bot, 600, top + 50))
    def stroked_line(pts, w):
        return c.stroke_line(pts, w, limit=4)
    wd = vcentre(wedge())
    put(0x2227, wd, 600)
    put(0x2228, flipv(wd, A), 600)
    # identical to: three bars of =
    EQ_T = c.EQ_T; step = 0.8 * 2 * c.EQ_D
    put(0x2261, union(*[rect(53, A + k * step - EQ_T / 2, 547, A + k * step + EQ_T / 2) for k in (-1, 0, 1)]), 600)
    # the tilde operator and its relatives, from the waves of the approx sign
    ax = path_of('approxequal'); waves = []
    for cont in ax.contours:
        q = pathops.Path(); cont.draw(q.getPen()); waves.append(q)
    waves.sort(key=lambda q: q.bounds[1])
    wave = waves[1]; wb = wave.bounds
    def wave_at(y): return mv(wave, 300 - (wb[0] + wb[2]) / 2, y - (wb[1] + wb[3]) / 2)
    put(0x223C, wave_at(A), 600)
    lo, hi = c.EQ_C - c.EQ_D, c.EQ_C + c.EQ_D
    put(0x2243, vcentre(union(wave_at(hi + 12), rect(53, lo - EQ_T / 2, 547, lo + EQ_T / 2))), 600)
    put(0x2245, vcentre(union(wave_at(A + step + 12), *[rect(53, A + k * step - EQ_T / 2, 547, A + k * step + EQ_T / 2) for k in (-1, 0)])), 600)
    # much less / greater: two chevrons of the < sign's weight, narrower
    lt = path_of('less'); lb = lt.bounds
    def chev(x, w, d):
        hh = (lb[3] - lb[1]) / 2 - 20
        pts = [(x + w, A + hh), (x, A), (x + w, A - hh)] if d < 0 else [(x, A + hh), (x + w, A), (x, A - hh)]
        q = stroked_line([(pts[0][0] + (20 if d < 0 else -20), pts[0][1] + 40 * hh / w / 2), pts[1],
                          (pts[2][0] + (20 if d < 0 else -20), pts[2][1] - 40 * hh / w / 2)], BAR * 1.08)
        return clip(q, (-100, A - hh, 1100, A + hh))
    gg = 125 + BAR
    put(0x226A, centre(union(chev(60, 270, -1), chev(60 + gg, 270, -1)), 600), 600)
    put(0x226B, centre(union(chev(60, 270, 1), chev(60 + gg, 270, 1)), 600), 600)
    # proportional to: the infinity sign with its right loop opened
    inf = path_of('infinity'); ib = inf.bounds
    cut = ib[0] + (ib[2] - ib[0]) * 0.80
    prop = clip(inf, (ib[0] - 10, ib[1] - 10, cut, ib[3] + 10))
    put(0x221D, *fit(prop, 53, adv=600))
    # floor and ceiling: the square brackets with one arm
    bl = path_of('bracketleft'); bb = bl.bounds
    stem_r = c.hspans(bl, 300)[0][1]
    arm = c.vspans(bl, bb[2] - 5)                    # bottom and top arms
    ab, at = arm[0], arm[-1]
    lfloor = union(rect(bb[0], ab[0], stem_r, at[1]), rect(bb[0], ab[0], bb[2], ab[1]))
    lceil = union(rect(bb[0], ab[0], stem_r, at[1]), rect(bb[0], at[0], bb[2], at[1]))
    wbr = W('bracketleft')
    put(0x230A, lfloor, wbr); put(0x2308, lceil, wbr)
    put(0x230B, mirror(lfloor, wbr / 2), wbr); put(0x2309, mirror(lceil, wbr / 2), wbr)
    # up tack / down tack
    tack_h = 650
    down = union(rect(70, 0, 530, BAR), rect(300 - VB / 2, 0, 300 + VB / 2, tack_h))
    put(0x22A5, down, 600)
    put(0x22A4, flipv(down, tack_h / 2), 600)
    # angle
    ang = union(rect(70, 0, 530, BAR), clip(band((60, BAR / 2 - 10), (60 + 520 * 0.82, BAR / 2 + 520), BAR * 1.08), (70, 0, 1000, 600)))
    put(0x2220, ang, 600)
    # circled operators: a ring of the operators' weight, 70..530
    RR = 230
    ring = diff(ellipse(300, A, RR, RR), ellipse(300, A, RR - TV, RR - TH))
    put(0x2295, union(ring, rect(300 - RR + 5, A - BAR / 2, 300 + RR - 5, A + BAR / 2), rect(300 - VB / 2, A - RR + 5, 300 + VB / 2, A + RR - 5)), 600)
    dg = (RR - 10) / math.sqrt(2)
    put(0x2297, union(ring, band((300 - dg, A - dg), (300 + dg, A + dg), BAR), band((300 - dg, A + dg), (300 + dg, A - dg), BAR)), 600)
    pc = path_of('periodcentered'); pb = pc.bounds; dot_r = (pb[2] - pb[0]) / 2
    def dot(x, y): return mv(pc, x - (pb[0] + pb[2]) / 2, y - (pb[1] + pb[3]) / 2)
    put(0x2299, union(ring, dot(300, A)), 600)
    # ring operator and dot operator: narrower, between operands
    r2 = 95
    put(0x2218, diff(ellipse(205, A, r2, r2), ellipse(205, A, r2 - TV * 0.9, r2 - TH * 0.9)), 410)
    # the dot operator (\cdot): 1.1 times the period's dot, so that ss14's math form (mathglyphs,
    # 1.22 times this) is about 128 units across, TeX's \cdotp to the x-height; the period stays
    DOTOP = 1.1
    put(0x22C5, transformed(dot(165 + (DOTOP - 1) * dot_r, A), (DOTOP, 0, 0, DOTOP, (1 - DOTOP) * (165 + (DOTOP - 1) * dot_r), (1 - DOTOP) * A)),
        330 + 2 * (DOTOP - 1) * dot_r)
    # asterisk operator: the asterisk on the axis
    ast = path_of('asterisk'); asb = ast.bounds
    put(0x2217, centre(mv(ast, 0, A - (asb[1] + asb[3]) / 2), 600), 600)
    # dots: the ellipsis's spacing, centred dots
    el = c.hspans(path_of('ellipsis'), 45); pitch = el[1][0] - el[0][0]
    put(0x22EF, union(*[dot(60 + dot_r + k * pitch, A) for k in range(3)]), 120 + 2 * dot_r + 2 * pitch)
    vp = 0.72 * pitch
    put(0x22EE, union(*[dot(60 + dot_r, A + (k - 1) * vp) for k in range(3)]), 120 + 2 * dot_r)
    d45 = vp / math.sqrt(2) * 1.25
    put(0x22F1, union(*[dot(60 + dot_r + k * d45, A + (1 - k) * d45) for k in range(3)]), 120 + 2 * dot_r + 2 * d45)
    # therefore / because: three dots in a triangle on the line, x-height tall
    tri = [(0, 0), (vp, 0), (vp / 2, vp * 0.92)]
    def triangle(pts): return union(*[dot(60 + dot_r + x, dot_r + 2 + y) for x, y in pts])
    tw = 120 + 2 * dot_r + vp
    put(0x2234, triangle(tri), tw)
    put(0x2235, flipv(triangle(tri), (2 * dot_r + 4 + vp * 0.92) / 2), tw)
    # colon equals / equals colon
    col = path_of('colon'); cb = col.bounds
    colA = mv(col, 60 - cb[0], A - (cb[1] + cb[3]) / 2)
    eqp = path_of('equal'); eb = eqp.bounds
    cw = cb[2] - cb[0]
    put(0x2254, union(colA, mv(eqp, 60 + cw + 60 - eb[0])), 60 + cw + 60 + (eb[2] - eb[0]) + 53)
    put(0x2255, union(mv(eqp, 53 - eb[0]), mv(colA, 53 + (eb[2] - eb[0]) + 60 - 60)), 53 + (eb[2] - eb[0]) + 60 + cw + 60)
    # minus-or-plus: the plus-minus turned over
    pm = path_of('plusminus'); pmb = pm.bounds
    put(0x2213, flipv(pm, (pmb[1] + pmb[3]) / 2), W('plusminus'))
    # bars: divides (|'s stroke with a relation's room) and the double bar
    bar = path_of('bar'); bab = bar.bounds; bw = bab[2] - bab[0]
    put(0x2223, mv(bar, 130 - bab[0]), 260 + bw)
    put(0x2016, union(mv(bar, 96 - bab[0]), mv(bar, 96 + bw + 72 - bab[0])), 192 + 2 * bw + 72)
    # for all: the A turned; exists: the E reversed; nabla: the increment turned
    a_ = path_of('A'); ab_ = a_.bounds
    put(0x2200, rot(a_, 180, (ab_[0] + ab_[2]) / 2, (ab_[1] + ab_[3]) / 2), W('A'))
    e_ = path_of('E'); eb_ = e_.bounds
    ex = mirror(e_, W('E') / 2)
    exb = ex.bounds; ex, exw = fit(ex, W('E') - eb_[2], eb_[0])
    put(0x2203, ex, exw)
    cx_ = (exb[0] + exb[2]) / 2
    put(0x2204, union(path_of('uni2203'), band((cx_ - 170, -60), (cx_ + 170, 765), BAR)), exw)
    de = path_of('uni2206'); deb = de.bounds
    put(0x2207, rot(de, 180, (deb[0] + deb[2]) / 2, (deb[1] + deb[3]) / 2), W('uni2206'))
    # primes: the minute's stroke, repeated at the second's pitch, and reversed
    mn = path_of('minute'); mb = mn.bounds; pp = c.hspans(path_of('second'), 600); ppitch = pp[1][0] - pp[0][0]
    put(0x2034, union(*[mv(mn, k * ppitch) for k in range(3)]), W('second') + ppitch)
    put(0x2057, union(*[mv(mn, k * ppitch) for k in range(4)]), W('second') + 2 * ppitch)
    rv = mirror(mn, (mb[0] + mb[2]) / 2)
    put(0x2035, rv, W('minute'))
    put(0x2036, union(*[mv(rv, k * ppitch) for k in range(2)]), W('second'))
    put(0x2037, union(*[mv(rv, k * ppitch) for k in range(3)]), W('second') + ppitch)

    negations(c, put)

    # ---- double-struck capitals (see doublestruck below) ------------------------------
    ds = doublestruck(c, ['R', 'N', 'Z', 'C', 'Q'])
    for cp, name, base in ((0x211D, 'uni211D', 'R'), (0x2115, 'uni2115', 'N'), (0x2124, 'uni2124', 'Z'), (0x2102, 'uni2102', 'C'), (0x211A, 'uni211A', 'Q')):
        put(cp, ds[base][0], round(ds[base][1]), name)

    # ---- spaces and joiners ----------------------------------------------------------
    empty = pathops.Path()
    put(0x202F, empty, W('uni2009'))          # narrow no-break space: the thin space's width
    put(0x2002, empty, 500)                   # en space
    put(0x2003, empty, 1000)                  # em space
    put(0x2000, empty, 500)                   # en quad: the en space (its canonical equivalent)
    put(0x2001, empty, 1000)                  # em quad: the em space
    put(0x2004, empty, 333)                   # three-per-em space
    put(0x2005, empty, 250)                   # four-per-em space
    put(0x2006, empty, 167)                   # six-per-em space
    put(0x205F, empty, 222)                   # medium mathematical space: 4/18 em
    put(0x2060, empty, 0)                     # word joiner
    put(0xFEFF, empty, 0)                     # zero width no-break space (byte order mark)
    put(0x200C, empty, 0)                     # zero width non-joiner (between f and i, still no fi)
    put(0x200D, empty, 0)                     # zero width joiner
    put(0x2011, path_of('hyphen'), W('hyphen'))   # non-breaking hyphen: the hyphen, outside its GSUB rules
    ctx.log(f'{len(made)} glyphs; U+2192 -> arrowright; paired arrows {ctx.paired_gap} off the axis')


# ---- negated relations and their missing bases ----------------------------------------
# KaTeX writes \not\le, \nleq, \nsubseteq, \nprec ... as precomposed code points (≰ U+2270)
# or as the base followed by U+0338. A font that has the base and U+0338 but not the
# precomposed glyph gets the pair from HarfBuzz's decomposition, and Mulish's U+0338 was
# drawn for letters, so the slash landed on the next character. HarfBuzz recomposes base +
# U+0338 into any of these glyphs the font has, so both spellings now reach them.
#
# Each is its base with the slash of ∉ (the bar's weight, rising two units for one across),
# reaching NEG_OVER past the base's ink above and below and at least as far as ≠'s slash;
# ∤ ∦ and the negated arrows take a short slash across the middle, ⊊ ⊋ a short one across
# the lower bar only, ≆ one across its two bars, ⊮ ⊯ the slash of the logic module's ⊬ ⊭.
# The bases the font lacked are drawn here first, on the set signs' conventions: ⊏ ⊐ ⊑ ⊒
# (the subset signs squared), ⊲ ⊳ ⊴ ⊵ (a triangle outline of the bar's weight), ⊩ ⊫ (⊢ ⊨
# with a second stem).
NEG_OVER = 70
NEG_CLEAR = 0.15     # ≆: the least gap between its slash and its wave, in bars
# ↚ ↛ ⇎ ⋠: where the slash crosses an arrowhead or ≼'s curved arms it leaves slivers of
# counter, a few units across, that open in some weights and not in others (↚: a pinhole in
# Bold, another elsewhere in ExtraBold; ⇎: one in Light, two in Regular). The variable font
# cannot interpolate a hole that comes and goes, so these fill every hole under a bar's
# square that the base itself does not have.
NEG_FILL = {0x219A, 0x219B, 0x21CE, 0x22E0}
# ⋠: past the slash, ≼'s lower arm and the bar under it run on to their right ends, where
# they all but meet: between them is a sliver of white, closed by the slash at its left and
# open at its right through a mouth 18 units wide in Bold Italic, 9 in ExtraBold Italic and
# 2.5 in Black Italic. Tapering through a pixel's width at text sizes, it rasterizes as a
# counter or two depending on the weight, which the variable font cannot interpolate (its
# ExtraBold-Black intermediates broke the sliver into two counters). Where an italic's mouth
# is narrower than NEG_CHANNEL units, the sliver's right two thirds and its mouth are opened
# to that width along their centre line: a channel like the lighter weights', open at both
# rasterized ends, in ExtraBold Italic and Black Italic alike. (Sealing the mouth instead
# changes the outline's structure from Bold Italic's, and its intermediates fall apart.)
# The uprights' intermediates keep one counter; they stay as drawn.
NEG_CHANNEL = {0x22E0: 16}
NEGATIONS = (    # code point, base, kind
    (0x226E, 'less', 'tall'), (0x226F, 'greater', 'tall'), (0x2270, 'lessequal', 'tall'),
    (0x2271, 'greaterequal', 'tall'), (0x2262, 'uni2261', 'tall'), (0x2241, 'uni223C', 'tall'),
    (0x2244, 'uni2243', 'tall'), (0x2247, 'uni2245', 'tall'), (0x2249, 'approxequal', 'tall'),
    (0x2246, 'uni2245', 'bars'), (0x2280, 'uni227A', 'tall'), (0x2281, 'uni227B', 'tall'),
    (0x22E0, 'uni227C', 'tall'), (0x22E1, 'uni227D', 'tall'), (0x2284, 'uni2282', 'tall'),
    (0x2285, 'uni2283', 'tall'), (0x2288, 'uni2286', 'tall'), (0x2289, 'uni2287', 'tall'),
    (0x220C, 'uni220B', 'tall'), (0x228A, 'uni2286', 'low'), (0x228B, 'uni2287', 'low'),
    (0x2224, 'uni2223', 'short'), (0x2226, 'uni2225', 'short'),
    (0x22E2, 'uni2291', 'tall'), (0x22E3, 'uni2292', 'tall'),
    (0x22EA, 'uni22B2', 'tall'), (0x22EB, 'uni22B3', 'tall'), (0x22EC, 'uni22B4', 'tall'), (0x22ED, 'uni22B5', 'tall'),
    (0x22AE, 'uni22A9', 'tack'), (0x22AF, 'uni22AB', 'tack'),
    (0x219A, 'arrowleft', 'short'), (0x219B, 'arrowright', 'short'), (0x21AE, 'arrowboth', 'short'),
    (0x21CD, 'uni21D0', 'short'), (0x21CF, 'arrowdblright', 'short'), (0x21CE, 'arrowdblboth', 'short'),
)


def negations(c, put):
    A, BAR = c.LIN_AXIS, c.BAR
    rect, poly, union, diff, band, mirror, path_of = c.rect, c.poly, c.union, c.diff, c.band, c.mirror, c.path_of
    VB, TH, TV = BAR * 1.15, BAR, BAR * 1.1
    have = lambda n: n in c.font.getGlyphOrder()

    # ⊏ ⊐ ⊑ ⊒: the subset signs' frame (X0..X1, half height 228, the stack of ⊆) squared
    def sq(x0, x1, yc, h):
        return union(rect(x0, yc - h, x0 + TV, yc + h), rect(x0, yc + h - TH, x1, yc + h), rect(x0, yc - h, x1, yc - h + TH))
    X0, X1, H, gap = 70, 530, 228, 70
    hq = (535 - BAR - gap) / 2
    put(0x228F, sq(X0, X1, A, H), 600); put(0x2290, mirror(sq(X0, X1, A, H), 300), 600)
    sqe = union(sq(X0, X1, BAR + gap + hq, hq), rect(X0, 0, X1, BAR))
    put(0x2291, sqe, 600); put(0x2292, mirror(sqe, 300), 600)

    # ⊲ ⊳ ⊴ ⊵: a triangle outline, the stroke t measured square to each side (its inner
    # triangle is the outer one shrunk about the incentre by the inradius less t)
    def triangle(pts, t):
        (ax, ay), (bx, by), (cx, cy) = pts
        la, lb, lc = math.dist(pts[1], pts[2]), math.dist(pts[0], pts[2]), math.dist(pts[0], pts[1])
        s = la + lb + lc
        ix, iy = (la * ax + lb * bx + lc * cx) / s, (la * ay + lb * by + lc * cy) / s
        area = abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2
        k = (2 * area / s - t) / (2 * area / s)
        return diff(poly(pts), poly([(ix + k * (x - ix), iy + k * (y - iy)) for x, y in pts]))
    TT = min(BAR, 70 + 0.4 * (BAR - 70))      # heavy weights' triangles keep a counter
    def tri(yc, h): return triangle([(X1, yc + h), (X0 + 10, yc), (X1, yc - h)], TT)
    put(0x22B2, tri(A, H), 600); put(0x22B3, mirror(tri(A, H), 300), 600)
    trie = union(tri(BAR + gap + hq, hq), rect(X0, 0, X1, BAR))
    put(0x22B4, trie, 600); put(0x22B5, mirror(trie, 300), 600)

    # ⊩ ⊫: ⊢ ⊨ (the logic module's: stem 70..70+VB on 0..2A, bars to 530) with a second stem
    yt, g2 = 2 * A, 0.9 * VB
    s2 = 70 + VB + g2
    stems = union(rect(70, 0, 70 + VB, yt), rect(s2, 0, s2 + VB, yt))
    put(0x22A9, union(stems, rect(s2, A - BAR / 2, 530, A + BAR / 2)), 600)
    put(0x22AB, union(stems, *[rect(s2, A + d - c.EQ_T / 2, 530, A + d + c.EQ_T / 2) for d in (c.EQ_D, -c.EQ_D)]), 600)

    ne = path_of('notequal').bounds
    made = []
    for cp, base, kind in NEGATIONS:
        if not have(base) or cp in c.font.getBestCmap():
            continue
        p = path_of(base); b = p.bounds; cx = (b[0] + b[2]) / 2
        if kind == 'tall':          # past the ink by NEG_OVER, and at least ≠'s slash
            y0, y1 = min(b[1] - NEG_OVER, ne[1]), max(b[3] + NEG_OVER, ne[3])
        elif kind == 'short':       # across the middle, past the ink by 50 each side
            dxh = max(100, (b[2] - b[0]) / 2 + 50) if base in ('uni2223', 'uni2225') else 100
            y0, y1 = A - max(200, 1.2 * dxh), A + max(200, 1.2 * dxh)
        elif kind == 'low':         # ⊊ ⊋: the lower bar only
            y0, y1 = -75, BAR + 75; cx += 25 if base == 'uni2286' else -25
        elif kind == 'bars':        # ≆: the two bars under the wave, clear of the wave
            # The bars come within 85 units of the wave in Light and 32 in Black, so a
            # NEG_OVER overshoot would join the slash to the wave from Medium on. Shorten both
            # ends alike until the slash clears the wave by NEG_CLEAR bars at every weight:
            # one topology in every weight, which the variable font can interpolate.
            v = c.vspans(p, cx)
            wave = c.transformed(c.clip(p, (-1000, (v[1][1] + v[2][0]) / 2, 2000, 3000)),
                                 (1, 0, 0, 1, 0, -NEG_CLEAR * BAR))
            over = NEG_OVER
            while over > 0 and pathops.op(band((cx - (v[1][1] - v[0][0] + 2 * over) / 4, v[0][0] - over),
                                               (cx + (v[1][1] - v[0][0] + 2 * over) / 4, v[1][1] + over), BAR),
                                          wave, pathops.PathOp.INTERSECTION).area > 0:
                over -= 1
            y0, y1 = v[0][0] - over, v[1][1] + over
        if kind == 'tack':          # ⊮ ⊯: the slash of ⊬ ⊭, right of the stems, across the bars
            sw, slope = min(BAR * 0.86, 80.0), 212.0 / yt
            xc = (s2 + VB + 530) / 2 + 10
            s = band((xc - slope * A, 0), (xc + slope * A, yt), sw)
        else:
            d = dxh if kind == 'short' else (y1 - y0) / 4
            s = band((cx - d, y0), (cx + d, y1), BAR)
        u = union(p, s)
        if cp in NEG_FILL:
            u = _fill_slivers(u, p, BAR * BAR)
        if cp in NEG_CHANNEL and c.ITALIC:
            u = _open_channel(u, NEG_CHANNEL[cp], c.log)
        made.append(put(cp, u, c.W(base)))
    c.log(f'negations: {len(made)} precomposed, bases ⊏ ⊐ ⊑ ⊒ ⊲ ⊳ ⊴ ⊵ ⊩ ⊫')


def _fill_slivers(path, base, limit):
    """path less its holes smaller than limit (square units) that are not base's counters."""
    def holes(p):
        cs = list(p.contours)
        if len(cs) < 2:
            return []
        outer = max(cs, key=lambda q: abs(q.area)).clockwise
        return [q for q in cs if q.clockwise != outer]
    counters = pathops.Path()
    for q in holes(base):
        counters.addPath(q)
    small = [(q.bounds, q.area) for q in holes(path) if abs(q.area) < limit
             and pathops.op(q, counters, pathops.PathOp.INTERSECTION).area < 0.5 * abs(q.area)]
    if not small:
        return path
    out = pathops.Path()
    for q in path.contours:
        if (q.bounds, q.area) not in small:
            out.addPath(q)
    return out


def _holes(p):
    cs = list(p.contours)
    if len(cs) < 2:
        return []
    outer = max(cs, key=lambda q: abs(q.area)).clockwise
    return [q for q in cs if q.clockwise != outer]


def _offset(p, g):
    """p grown by g (g > 0) or shrunk by -g, with round joins."""
    s = pathops.Path(); p.draw(s.getPen())
    s.stroke(2 * abs(g), pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    return pathops.op(p, s, pathops.PathOp.UNION if g > 0 else pathops.PathOp.DIFFERENCE)


def _open_channel(path, width, log):
    """path with a pocket of white whose mouth is narrower than width opened into a channel
    width units wide: a band of that width is cut along the pocket's centre line from a
    third of the way in, out through the mouth and 40 units past it. Where the pocket is
    already wider the band cuts nothing."""
    h0, g = len(_holes(path)), 0.25
    while g < width / 2 and len(_holes(_offset(path, g))) == h0:
        g += 0.25
    if g >= width / 2:
        return path
    mouth, g = 2 * g, g + 0.5
    extra = pathops.op(_offset(_offset(path, g), -g), path, pathops.PathOp.DIFFERENCE)
    for q in extra.contours:
        seal = pathops.Path(); seal.addPath(q)
        sealed = pathops.op(path, seal, pathops.PathOp.UNION)
        if len(_holes(sealed)) == h0 + 1:
            break
    else:
        return path
    pocket = None
    for q in _holes(sealed):
        h = pathops.Path(); h.addPath(q)
        if pathops.op(_offset(h, 1), seal, pathops.PathOp.INTERSECTION).area > 0:
            pocket = h
    if pocket is None:
        return path
    x0, y0, x1, y1 = pocket.bounds
    mids = []
    for i in range(41):
        x = x0 + (x1 - x0) * i / 40
        r = pathops.Path(); pen = r.getPen()
        pen.moveTo((x, y0 - 1)); pen.lineTo((x + 0.1, y0 - 1)); pen.lineTo((x + 0.1, y1 + 1)); pen.lineTo((x, y1 + 1)); pen.closePath()
        cut = pathops.op(r, pocket, pathops.PathOp.INTERSECTION)
        if cut.area > 0:
            mids.append((x, (cut.bounds[1] + cut.bounds[3]) / 2))
    (ax, ay), (bx, by) = mids[-4], mids[-1]
    run = math.hypot(bx - ax, by - ay)
    mids.append((bx + (bx - ax) / run * 40, by + (by - ay) / run * 40))
    line = pathops.Path(); pen = line.getPen()
    pen.moveTo(mids[len(mids) // 3])
    for m in mids[len(mids) // 3 + 1:]:
        pen.lineTo(m)
    pen.endPath()
    line.stroke(width, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    line.convertConicsToQuads()
    out = pathops.op(path, line, pathops.PathOp.DIFFERENCE)
    log(f'negations: opened a {mouth:g}-unit mouth into a {width}-unit channel')
    return out


# ---- double-struck letters and figures ----------------------------------------------
# The double-struck set follows Noto Sans Math's (Copyright 2022 The Noto Project Authors,
# https://github.com/notofonts/math, SIL Open Font License 1.1, no Reserved Font Name;
# NotoSansMath-Regular.ttf version 3.000): its design, not its outlines. Noto draws every
# stroke of a double-struck letter as one hairline, 53 units against its capitals' 90-unit
# stem; a doubled stroke is two hairlines 67 apart (a band 173 wide) closed at both ends; a
# round stroke is doubled by a straight upright inline, the crescent between it and the
# outer curve 197 deep at its widest. Which strokes double is Noto's for every letter and
# figure (the thick strokes of a calligraphic capital): A's right and V's and X's falling
# diagonals, M's left diagonal and right stem, W's two falling strokes, N's and Z's and 2's
# and 7's diagonal, the stems of B D E F H I J K L P R T U 1 4 5, K's and R's leg, Y's left
# arm and stem, G's spur; by an upright inline the left side of C G O Q S 0 6 8, the right
# side of O Q 0 3 8 9 and of every bowl (B D P R 5 6 9), and S's lower right. The letters themselves are Torchlette's: positions, widths, heights and
# slopes are measured from this style's capital or lining figure, and the curved hairlines
# are Mulish's own lightest master (wght 200, the type designer's hairline drawing of the
# same letter) set in the letter's ink box and offset to the hairline weight, so G's bar and
# spur, J's descent, M's upright stems, Q's tail, R's leg, 1's foot and 7's bar are
# Torchlette's. ℝ keeps round 1's approved leg (along R's own leg) and ℚ round 1's tail
# (one hairline along Q's tail axis, from the ring's stroke to the tail's end face).
#
# The weight rule. With s the capital stem of this style (66 in Regular) and u = s / 66:
#     t = DS_T * (u if u <= 1 else u ** DS_TEXP)      the hairline (DS_T 38.9 = 66 * 53/90)
#     g = DS_G * t                                     the gap inside a doubled stroke (67/53)
#     D = 2 t + g, DR = D * 197/173                    a doubled stroke, a crescent's depth
# so Regular's hairline stands to its stem as Noto's does to Noto's, Light scales with the
# stem, and above Regular the hairline grows as the square root (Bold 53, Noto's own; Black
# 62), since a doubled stroke 3.26 hairlines wide must still fit inside the letter. The gap
# is a fixed share of the hairline, so it never closes: every counter of a doubled stroke
# is an explicit band g wide (or a crescent at least g deep), and the contours a letter has
# are the same at every weight. A doubled straight stroke is centred on the capital's own
# stroke (the letter widens by (D - s) / 2 there, Noto's 0-12 %); a thin stroke on the
# letter's edge keeps the capital's outer edge; rings and crescents keep the outer curve.
#
# Alignment rules (round 3). Where a hairline meets a doubled band at the cap line or the
# baseline it meets it corner to corner: M's right diagonal (at the capital's slope) and W's
# second stroke arrive exactly at the band's top-left corner, and W's second stroke leaves
# the first band's foot at its right corner. Inlines that read as one upright share one x
# (B's two bowls). The 1's flag runs, at its own slope, into the doubled stem's top-left
# corner. J's hook reaches as far past the doubled stem's middle as J's past its stem's. The
# side inline of 6 and 9 runs through the bowl, and the bowl's hairline ends on it. The 2's
# doubling lies inside the bend and runs into the bowl, the 2 keeping its ink width.
# Knobs (environment): DS_T, DS_G, DS_TEXP, DS_CLOSE, DS69_K.
NOTO_STEM, NOTO_T, NOTO_G, NOTO_D, NOTO_DR = 90.0, 53.0, 67.0, 173.0, 197.0


_MASTERS = {}


def _master(c):
    """Mulish's default master (wght 200), unslanted in the italic, as build.py unslants its
    source: glyph paths and its capital stem and bar."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.transformPen import TransformPen
    key = (c.VAR, c.ITALIC_K)
    if key not in _MASTERS:
        f = TTFont(c.VAR); gs = f.getGlyphSet(); K, YC = c.ITALIC_K, c.ITALIC_YC
        def path(n):
            q = pathops.Path(); gs[n].draw(TransformPen(q.getPen(glyphSet=gs), (1, 0, -K, 1, K * YC, 0)))
            q.simplify(); return q
        h = path('H'); hb = h.bounds
        stem = (lambda s: s[0][1] - s[0][0])(c.hspans(h, hb[3] * 0.25))
        bar = (lambda s: s[0][1] - s[0][0])(c.vspans(h, (hb[0] + hb[2]) / 2))
        _MASTERS[key] = {'path': path, 'stem': stem, 'bar': bar}
    return _MASTERS[key]


def doublestruck(c, which=None):
    """{base glyph: (path, advance)} for the double-struck form of each base in `which` (all
    36 when None: the capitals A-Z by their names and the lining figures zero ... nine),
    drawn from this style's capitals and figures with c's helpers (path_of, rect, poly,
    union, diff, clip, transformed, mv, hspans, vspans, W, P, VAR, ITALIC_K, ITALIC_YC).
    Sets c.ds_strokes to this style's hairline, gap, doubled stroke and crescent depth."""
    rect, poly, union, diff, clip, transformed, mv = c.rect, c.poly, c.union, c.diff, c.clip, c.transformed, c.mv
    hspans, vspans, path_of, W = c.hspans, c.vspans, c.path_of, c.W
    width = lambda s: s[1] - s[0]
    mid = lambda s: (s[0] + s[1]) / 2

    hp = path_of('H'); CH = hp.bounds[3]
    s_v = width(hspans(hp, CH * 0.25)[0])                 # the capitals' stem
    u = s_v / 66.0                                         # the stem against Regular's
    t = c.P('DS_T', 66.0 * NOTO_T / NOTO_STEM) * (u if u <= 1 else u ** c.P('DS_TEXP', 0.5))
    g = c.P('DS_G', NOTO_G / NOTO_T) * t
    D = 2 * t + g
    DR = D * NOTO_DR / NOTO_D
    c.ds_strokes = {'t': t, 'g': g, 'D': D, 'DR': DR, 'stem': s_v}
    BIG = 3000

    # ---- geometry helpers ------------------------------------------------------------
    def stroke_open(pts, w):
        """An open polyline stroked w wide: butt ends, mitred joins."""
        q = pathops.Path(); pen = q.getPen(); pen.moveTo(pts[0])
        for p_ in pts[1:]: pen.lineTo(p_)
        pen.endPath()
        q.stroke(w, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 20)
        q.simplify(); return q

    def ext(p0, p1, L=BIG):
        """The segment p0-p1 run on L each way."""
        d = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); ux, uy = (p1[0] - p0[0]) / d, (p1[1] - p0[1]) / d
        return [(p0[0] - ux * L, p0[1] - uy * L), (p1[0] + ux * L, p1[1] + uy * L)]

    def offset_line(p0, p1, dist, towards):
        """The line p0-p1 moved dist perpendicular to itself, towards the point `towards`."""
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
        if (towards[0] - p0[0]) * nx + (towards[1] - p0[1]) * ny < 0: nx, ny = -nx, -ny
        return (p0[0] + nx * dist, p0[1] + ny * dist), (p1[0] + nx * dist, p1[1] + ny * dist)

    def half(p0, p1, towards):
        """The side of the line p0-p1 that holds `towards`, as a big polygon."""
        a, b = offset_line(p0, p1, 0, towards)
        a2, b2 = offset_line(p0, p1, 2 * BIG, towards)
        e = ext(a, b); e2 = ext(a2, b2)
        return poly([e[0], e[1], e2[1], e2[0]])

    def eroded(p, tx, ty):
        k = tx / ty
        q = transformed(p, (1, 0, 0, k, 0, 0))
        s = pathops.Path(q); s.stroke(2 * tx, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        s.convertConicsToQuads(); s.simplify()
        return transformed(diff(q, s), (1, 0, 0, 1 / k, 0, 0))

    def ring(F):
        """The hairline along the inside of a filled shape's boundary."""
        return diff(F, eroded(F, t, t))

    def contours(p):
        cs = []
        for cont in p.contours:
            q = pathops.Path(); cont.draw(q.getPen()); cs.append(q)
        return sorted(cs, key=lambda q: -(q.bounds[2] - q.bounds[0]) * (q.bounds[3] - q.bounds[1]))

    def outer_fill(p):
        q = contours(p)[0]; q2 = pathops.Path(q); q2.simplify(); return q2

    def dilated(p, tx, ty):
        """p grown by tx across and ty up and down, its corners kept sharp (mitred)."""
        k = tx / ty
        q = transformed(p, (1, 0, 0, k, 0, 0))
        s = pathops.Path(q); s.stroke(2 * tx, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
        s.convertConicsToQuads(); s.simplify()
        return transformed(union(q, s), (1, 0, 0, 1 / k, 0, 0))

    master = _master(c)

    def fit(q, box):
        qb = q.bounds; kx, ky = (box[2] - box[0]) / (qb[2] - qb[0]), (box[3] - box[1]) / (qb[3] - qb[1])
        return transformed(q, (kx, 0, 0, ky, box[0] - qb[0] * kx, box[1] - qb[1] * ky)), kx, ky

    def median(ws):
        ws = sorted(ws); return ws[len(ws) // 2] if ws else None

    def light(p, base, box=None):
        """Mulish's lightest master of the glyph (wght 200: its designer's hairline drawing of
        the same letter), set in this letter's ink box and offset so that its upright strokes
        (the median across rows at 0.3-0.7 of its height) and its level strokes (down columns
        at 0.3-0.7 of its width) are t."""
        box = box or p.bounds
        q, kx, ky = fit(master['path'](base), box)
        qb = q.bounds; Wd, Hh = qb[2] - qb[0], qb[3] - qb[1]
        sv = median([width(s_) for f_ in (0.3, 0.4, 0.5, 0.6, 0.7) for s_ in hspans(q, qb[1] + f_ * Hh)]) or t
        sh = median([width(s_) for f_ in (0.3, 0.4, 0.5, 0.6, 0.7) for s_ in vspans(q, qb[0] + f_ * Wd)]) or t
        dx, dy = (t - sv) / 2, (t - sh) / 2
        if dx > 0.25 and dy > 0.25: q = dilated(q, dx, dy)
        elif dx < -0.25 and dy < -0.25: q = eroded(q, -dx, -dy)
        elif max(abs(dx), abs(dy)) > 0.25:
            # one grows and one shrinks: shrink by a all round, then grow by (dx + a, dy + a),
            # a chosen so the smaller growth is a quarter of the larger
            m = 0.25 * max(abs(dx), abs(dy)); a = max(m - dx, m - dy)
            q = dilated(eroded(q, a, a), dx + a, dy + a)
        return fit(q, box)[0]

    def inline(L, x, y_in, x_probe=None):
        """An upright hairline at x..x+t from the hairline of L below y_in to the one above it
        (each joined halfway into its depth)."""
        sp = vspans(L, (x + t / 2) if x_probe is None else x_probe)
        lo = max((s for s in sp if s[1] <= y_in), key=lambda s: s[1])
        hi = min((s for s in sp if s[0] >= y_in), key=lambda s: s[0])
        return rect(x, mid(lo), x + t, mid(hi))

    def vband(xc, y0, y1, closed=(True, True)):
        """A doubled upright stroke D wide centred on xc from y0 to y1: (ink, counter)."""
        return rect(xc - D / 2, y0, xc + D / 2, y1), rect(xc - D / 2 + t, y0 + (t if closed[0] else -50), xc + D / 2 - t, y1 - (t if closed[1] else -50))

    def dband(pts, y0, y1):
        """A doubled stroke D wide on the centre polyline pts (run on past y0 and y1, cut level
        there): (ink, counter), the counter closed t inside both cuts."""
        return (clip(stroke_open(pts, D), (-BIG, y0, BIG, y1)),
                clip(stroke_open(pts, D - 2 * t), (-BIG, y0 + t, BIG, y1 - t)))

    def thin(pts, y0=-BIG, y1=BIG):
        return clip(stroke_open(pts, t), (-BIG, y0, BIG, y1))

    def edge_thin(p0, p1, inside):
        """A hairline t wide whose outer edge is the line p0-p1, on the side of `inside`."""
        a, b = offset_line(p0, p1, t / 2, inside)
        return stroke_open(ext(a, b), t)

    def to_corner(e, Q):
        """The line e (two points) moved level, keeping its slope, to run through Q: a hairline
        whose left edge is e then arrives exactly at the band corner Q."""
        (xa, ya), (xb, yb) = e; s_ = (xb - xa) / (yb - ya); x0 = Q[0] - (Q[1] - ya) * s_
        return (x0, ya), (x0 + (yb - ya) * s_, yb)

    def corner_thin(P, Q):
        """The left edge (points at y 0 and CH) of a hairline whose right edge leaves the
        baseline corner P of one band and whose left edge arrives at the cap-line corner Q of
        another: the two strokes meet corner to corner at both ends."""
        s_ = (Q[0] - P[0]) / CH
        for _ in range(8):
            x0 = P[0] - t * math.hypot(1, s_); s_ = (Q[0] - x0) / CH
        return (x0, 0), (Q[0], CH)

    def band_edge_x(cl, y, side):
        """The x at height y of a band D wide on the centre line cl: its right (+1) or left (-1) edge."""
        (xa, ya), (xb, yb) = cl; s_ = (xb - xa) / (yb - ya)
        return xa + (y - ya) * s_ + side * (D / 2) * math.hypot(1, s_)

    def centre_line(p, y_a, y_b, idx):
        """The centre line of the idx-th stroke of p crossing heights y_a and y_b."""
        sa, sb = hspans(p, y_a)[idx], hspans(p, y_b)[idx]
        return (mid(sa), y_a), (mid(sb), y_b)

    def heights(p, n, lo, hi):
        """The lowest and highest heights between lo and hi (shares of CH) where p's ink is n spans."""
        ys = [y for y in (CH * lo + k * 5 for k in range(int(CH * (hi - lo) / 5) + 1)) if len(hspans(p, y)) == n]
        if len(ys) < 2: raise ValueError(f'double-struck: no two heights with {n} spans in {lo}..{hi}')
        a, b_ = ys[0], ys[-1]; m = (b_ - a) * 0.1
        return a + m, b_ - m

    def edge_pts(p, y_a, y_b, idx, side):
        sa, sb = hspans(p, y_a)[idx], hspans(p, y_b)[idx]
        return (sa[side], y_a), (sb[side], y_b)

    def stem_x(p, lo, hi, idx=0):
        """The centre of p's idx-th upright stroke, read at the height between lo and hi (shares
        of p's height) where that stroke is narrowest (clear of arms, bars and bowls)."""
        b = p.bounds; Hh = b[3] - b[1]
        best = min((hspans(p, b[1] + Hh * (lo + (hi - lo) * k / 20)) for k in range(21)),
                   key=lambda sp: width(sp[idx]) if len(sp) > abs(idx) - (idx < 0) else 1e9)
        return mid(best[idx])

    def extreme_x(p, side, y_lo, y_hi, n=24):
        """The leftmost (side -1) or rightmost (+1) ink of p between two heights, and its height."""
        best = None
        for i in range(n + 1):
            y = y_lo + (y_hi - y_lo) * i / n
            s = hspans(p, y)
            if not s: continue
            x = s[0][0] if side < 0 else s[-1][1]
            if best is None or (x < best[0] if side < 0 else x > best[0]): best = (x, y)
        return best

    out = {}
    join_roles = {}
    side_rails = {}

    def finish(base, ink, counters=(), box=None):
        g_ = diff(ink, union(*counters)) if counters else ink
        if box: g_ = clip(g_, box)
        if base in join_roles:
            role, bar = join_roles[base]
            if role in ('side-left', 'side-right'):
                g_, _join_record = _join_geometry.side_rail_bridge(g_, t, bar, role == 'side-left', *side_rails[base])
            elif role == 'two-rails':
                g_, _join_record = _join_geometry.two_rail_bridge(g_, t, *bar)
            else:
                g_, _join_record = _join_geometry.role_bridges(g_, role, t, bar=bar)
        pb = path_of(base).bounds; gb = g_.bounds
        g_ = mv(g_, pb[0] - gb[0])
        out[base] = (g_, W(base) + (gb[2] - gb[0]) - (pb[2] - pb[0]))

    # ---- letters ---------------------------------------------------------------------
    def dA():
        p = path_of('A'); b = p.bounds
        ya, yb = heights(p, 2, 0.0, 0.3)
        eL = edge_pts(p, ya, yb, 0, 0)
        cR = centre_line(p, ya, yb, -1)
        bar = vspans(p, (b[0] + b[2]) / 2)[0]
        inside = ((b[0] + b[2]) / 2, CH * 0.3)
        left = edge_thin(*eL, inside)
        band, cnt = dband(ext(*cR), 0, CH)
        xbar = thin([(b[0] - 100, mid(bar)), (b[2] + 100, mid(bar))])
        hull = half(*eL, inside)
        a, b2 = offset_line(*eL, t, inside)
        cnt = pathops.op(cnt, half(a, b2, inside), pathops.PathOp.INTERSECTION)
        ink = pathops.op(union(left, band, xbar), hull, pathops.PathOp.INTERSECTION)
        hullR = half(*offset_line(*cR, D / 2, (BIG, b[1])), inside)
        ink = pathops.op(ink, hullR, pathops.PathOp.INTERSECTION)
        finish('A', ink, [cnt], (-BIG, 0, BIG, CH))

    def dV():
        p = path_of('V'); b = p.bounds
        ya, yb = heights(p, 2, 0.45, 1.0)
        eR = edge_pts(p, ya, yb, -1, 1)
        cL = centre_line(p, ya, yb, 0)
        inside = ((b[0] + b[2]) / 2, CH * 0.7)
        right = edge_thin(*eR, inside)
        band, cnt = dband(ext(*cL), 0, CH)
        a, b2 = offset_line(*eR, t, inside)
        cnt = pathops.op(cnt, half(a, b2, inside), pathops.PathOp.INTERSECTION)
        ink = pathops.op(union(right, band), half(*eR, inside), pathops.PathOp.INTERSECTION)
        finish('V', ink, [cnt], (-BIG, 0, BIG, CH))

    def stems_H():
        p = path_of('H'); b = p.bounds
        bar = vspans(p, (b[0] + b[2]) / 2)[0]
        return p, b, stem_x(p, 0.05, 0.45), stem_x(p, 0.05, 0.45, -1), bar

    def dH():
        p, b, xl, xr, bar = stems_H()
        (i1, c1), (i2, c2) = vband(xl, 0, CH), vband(xr, 0, CH)
        finish('H', union(i1, i2, rect(xl, mid(bar) - t / 2, xr, mid(bar) + t / 2)), [c1, c2])

    def dI():
        p = path_of('I'); xc = stem_x(p, 0.2, 0.8)
        i1, c1 = vband(xc, 0, CH); finish('I', i1, [c1])

    def dEFL(base):
        p = path_of(base); b = p.bounds
        xs = stem_x(p, 0.05, 0.95); st = [s for s in hspans(p, CH * 0.5) if s[0] <= xs <= s[1]][0]
        i1, c1 = vband(xs, 0, CH)
        parts = [i1]
        sw = min(width(hspans(p, CH * k / 20)[0]) for k in range(1, 20))
        arms = [s for s in vspans(p, st[0] + sw + 20)]
        for a in arms:
            xe = hspans(p, mid(a))[0][1]
            if a[0] < 1: y0, y1 = 0, t
            elif a[1] > CH - 1: y0, y1 = CH - t, CH
            else: y0, y1 = mid(a) - t / 2, mid(a) + t / 2
            parts.append(rect(xs, y0, xe, y1))
        finish(base, union(*parts), [c1])

    def dT():
        p = path_of('T'); b = p.bounds
        xs = stem_x(p, 0.05, 0.8)
        i1, c1 = vband(xs, 0, CH)
        finish('T', union(i1, rect(b[0], CH - t, b[2], CH)), [c1])

    def dN():
        p = path_of('N'); b = p.bounds; x0, x1 = b[0], b[2]
        y1, y2 = heights(p, 3, 0.1, 0.9)
        cD = centre_line(p, y1, y2, 1)
        band, cnt = dband(ext(*cD), 0, CH)
        cnt = clip(cnt, (x0 + t, -BIG, x1 - t, BIG))
        ink = union(rect(x0, 0, x0 + t, CH), rect(x1 - t, 0, x1, CH), clip(band, (x0, 0, x1, CH)))
        finish('N', ink, [cnt])

    def dZ():
        p = path_of('Z'); b = p.bounds; x0, x1 = b[0], b[2]
        top = hspans(p, CH - 1)[0]; bot = hspans(p, 1)[0]
        cD = centre_line(p, CH * 0.35, CH * 0.65, 0)
        band, cnt = dband(ext(*cD), 0, CH)
        ink = union(rect(top[0], CH - t, top[1], CH), rect(bot[0], 0, bot[1], t), clip(band, (x0, 0, x1, CH)))
        cnt = clip(cnt, (x0 + t, -BIG, x1 - t, BIG))
        finish('Z', ink, [cnt])

    def dX():
        p = path_of('X'); b = p.bounds
        ya, yb = CH * 0.12, CH * 0.88
        # '\' from top-left to bottom-right: the left stroke at the top, the right at the bottom
        cB = ((mid(hspans(p, yb)[0]), yb), (mid(hspans(p, ya)[-1]), ya))
        cF = ((mid(hspans(p, ya)[0]), ya), (mid(hspans(p, yb)[-1]), yb))
        band, cnt = dband(ext(*cB), 0, CH)
        finish('X', union(band, thin(ext(*cF), 0, CH)), [cnt], (-BIG, 0, BIG, CH))

    def dY():
        p = path_of('Y'); b = p.bounds
        xs = stem_x(p, 0.02, 0.3)
        ya, yb = heights(p, 2, 0.6, 1.0)
        cL = centre_line(p, ya, yb, 0)
        eR = edge_pts(p, ya, yb, -1, 1)
        # the arm's and the stem's centre lines meet at J
        (xa, ya_), (xb, yb_) = cL; m = (xb - xa) / (yb_ - ya_)
        yJ = ya_ + (xs - xa) / m; J = (xs, yJ)
        top = (xa + m * (CH + 400 - ya_), CH + 400)
        pts = [top, J, (xs, -400)]
        band = clip(stroke_open(pts, D), (-BIG, 0, BIG, CH)); cnt = clip(stroke_open(pts, D - 2 * t), (-BIG, t, BIG, CH - t))
        right = clip(edge_thin(*eR, (xs, CH * 0.6)), (xs, yJ - D / 2, BIG, CH))
        finish('Y', union(band, right), [cnt], (-BIG, 0, BIG, CH))

    def dK():
        p = path_of('K'); b = p.bounds
        xs = stem_x(p, 0.02, 0.98)
        i1, c1 = vband(xs, 0, CH)
        ya, yb = heights(p, 2, 0.6, 1.0)
        eA = edge_pts(p, ya, yb, -1, 0)             # the arm's upper-left edge
        cLg = centre_line(p, CH * 0.06, CH * 0.2, -1)
        inside = (b[2], 0)
        arm = clip(edge_thin(*eA, inside), (xs, 0, BIG, CH))
        leg, lc = dband(ext(*cLg), 0, CH)
        below_arm = half(*eA, inside)
        leg = pathops.op(clip(leg, (xs, -BIG, BIG, BIG)), below_arm, pathops.PathOp.INTERSECTION)
        a, b2 = offset_line(*eA, t, inside)
        lc = pathops.op(clip(lc, (xs + D / 2, -BIG, BIG, BIG)), half(a, b2, inside), pathops.PathOp.INTERSECTION)
        finish('K', union(i1, arm, leg), [c1, lc], (-BIG, 0, BIG, CH))

    def dM():
        p = path_of('M'); b = p.bounds; x0, x1 = b[0], b[2]
        xr = stem_x(p, 0.3, 0.7, -1)
        i1, c1 = vband(xr, 0, CH)
        ya, yb = heights(p, 4, 0.2, 1.0)
        cD = centre_line(p, ya, yb, 1)             # the left diagonal
        eR = edge_pts(p, ya, yb, 2, 0)              # the right diagonal's upper-left edge
        band, cnt = dband(ext(*cD), 0, CH)
        band = clip(band, (x0, -BIG, BIG, BIG))
        cnt = clip(cnt, (x0 + t, -BIG, BIG, BIG))
        inside = (x1, 0)
        # Constrain both ends of the thin ascending stroke. Its right edge leaves the
        # left doubled diagonal's baseline corner; its left edge reaches the upright's
        # cap corner. Translation alone satisfies only the latter and cuts the doubled
        # diagonal above its foot, increasingly far up as the weight grows.
        eR = corner_thin((band_edge_x(cD, 0, +1), 0), (xr - D / 2, CH))
        rdiag = pathops.op(edge_thin(*eR, inside), clip(half(*eR, inside), (-BIG, 0, xr, CH)), pathops.PathOp.INTERSECTION)
        finish('M', union(rect(x0, 0, x0 + t, CH), band, rdiag, i1), [c1, cnt], (-BIG, 0, BIG, CH))

    def dW():
        p = path_of('W'); b = p.bounds
        ya, yb = heights(p, 4, 0.2, 1.0)
        sp_a, sp_b = hspans(p, ya), hspans(p, yb)
        c1 = ((mid(sp_a[0]), ya), (mid(sp_b[0]), yb))
        c2 = ((mid(sp_a[1]), ya), (mid(sp_b[1]), yb))
        c3 = ((mid(sp_a[2]), ya), (mid(sp_b[2]), yb))
        e4 = ((sp_a[3][1], ya), (sp_b[3][1], yb))
        b1, k1 = dband(ext(*c1), 0, CH)
        b3, k3 = dband(ext(*c3), 0, CH)
        # the second stroke meets both bands corner to corner: its right edge leaves the first
        # band's foot at its right corner, its left edge arrives at the third band's top-left
        # corner, so it neither crosses a band nor cuts into a band's counter
        e2 = corner_thin((band_edge_x(c1, 0, +1), 0), (band_edge_x(c3, CH, -1), CH))
        w2 = t * math.hypot(1, (e2[1][0] - e2[0][0]) / CH)
        c2 = ((e2[0][0] + w2 / 2, 0), (e2[1][0] + w2 / 2, CH))
        s2 = thin(ext(*c2), 0, CH)
        s4 = edge_thin(*e4, (b[0], CH / 2))
        # each counter stays clear of the hairline that meets its band at a vertex
        r2 = offset_line(*c2, t / 2, (b[0], 0)); l2 = offset_line(*c2, t / 2, (b[2], 0))
        k1 = pathops.op(k1, half(*r2, (b[0], 0)), pathops.PathOp.INTERSECTION)
        k3 = pathops.op(k3, half(*l2, (b[2], 0)), pathops.PathOp.INTERSECTION)
        a, b2 = offset_line(*e4, t, (b[0], CH / 2))
        k3 = pathops.op(k3, half(a, b2, (b[0], CH / 2)), pathops.PathOp.INTERSECTION)
        ink = pathops.op(union(b1, s2, b3, s4), half(*e4, (b[0], CH / 2)), pathops.PathOp.INTERSECTION)
        finish('W', ink, [k1, k3], (-BIG, 0, BIG, CH))

    # ---- round letters --------------------------------------------------------------
    def dO(base='O'):
        p = path_of(base); F = outer_fill(p); b = F.bounds; ym = (b[1] + b[3]) / 2
        L = ring(F)
        xl = extreme_x(F, -1, b[1], b[3])[0]; xr = extreme_x(F, 1, b[1], b[3])[0]
        finish(base, union(L, inline(L, xl + DR - t, ym), inline(L, xr - DR, ym)))

    def bowl_letter(base, F, stem_x, bowls, extra=(), aligned=False):
        """The ring, the doubled stem and an inline DR inside each bowl's right extreme. With
        `aligned` (stacked bowls, B) the inlines share one x, so they read as one upright: the
        wider bowl's, but no further right than keeps the narrower bowl's gap at least g."""
        L = ring(F)
        i1, c1 = vband(stem_x, 0, CH)
        parts = [L, i1, *extra]
        xs_ = [extreme_x(F, 1, y_lo + 0.2 * (y_hi - y_lo), y_hi - 0.2 * (y_hi - y_lo))[0] - DR for y_lo, y_hi in bowls]
        if aligned:
            xa = min(max(xs_), min(xs_) + (DR - 2 * t - g)); xs_ = [xa] * len(xs_)
        for (y_lo, y_hi), x in zip(bowls, xs_):
            ym = (y_lo + y_hi) / 2
            parts.append(inline(union(L, *extra), x, ym))
        return parts, c1

    def dD():
        p = path_of('D'); F = outer_fill(p)
        xs = stem_x(p, 0.2, 0.8)
        parts, c1 = bowl_letter('D', F, xs, [(0, CH)])
        finish('D', union(*parts), [c1])

    def dP():
        p = path_of('P'); F = outer_fill(p)
        xs = stem_x(p, 0.02, 0.98)
        cnt = contours(p)[1].bounds
        parts, c1 = bowl_letter('P', F, xs, [(cnt[1], CH)])
        finish('P', union(*parts), [c1])

    def dB():
        p = path_of('B'); F = outer_fill(p); b = p.bounds
        xs = stem_x(p, 0.05, 0.95)
        cs = sorted((q.bounds for q in contours(p)[1:]), key=lambda bb: bb[1])  # lower, upper counter
        ybar = ((cs[0][3] + cs[1][1]) / 2)
        join_roles['B'] = ('B', ybar)
        notch = hspans(F, ybar)[-1][1]
        bar = rect(xs, ybar - t / 2, notch, ybar + t / 2)
        parts, c1 = bowl_letter('B', F, xs, [(0, ybar), (ybar, CH)], extra=(clip(bar, F.bounds),), aligned=True)
        finish('B', pathops.op(union(*parts), union(F, rect(xs - D / 2, 0, xs + D / 2, CH)), pathops.PathOp.INTERSECTION), [c1])

    def dR():
        p = path_of('R'); b = p.bounds; F = outer_fill(p)
        xs = stem_x(p, 0.02, 0.4); s_r = width([s for s in hspans(p, CH * 0.2) if s[0] <= xs <= s[1]][0])
        cnt = contours(p)[1].bounds                     # the bowl's counter
        ybar = cnt[1] - t                               # the bar's underside
        body = union(clip(F, (-BIG, ybar, BIG, BIG)), clip(F, (-BIG, -BIG, b[0] + s_r, BIG)))
        cLg = centre_line(p, CH * 0.06, CH * 0.2, -1)
        leg, lc = dband(ext(*cLg), 0, CH)
        leg = clip(leg, (-BIG, -BIG, BIG, ybar + t))
        lc = clip(lc, (-BIG, -BIG, BIG, ybar))
        parts, c1 = bowl_letter('R', body, xs, [(cnt[1], CH)])
        finish('R', union(*parts, leg), [c1, lc])

    def dQ():
        p = path_of('Q'); o = path_of('O'); F = outer_fill(o); ob = F.bounds; ym = (ob[1] + ob[3]) / 2
        L = ring(F)
        xl = extreme_x(F, -1, ob[1], ob[3])[0]; xr = extreme_x(F, 1, ob[1], ob[3])[0]
        cx, cy = (ob[0] + ob[2]) / 2, ym
        # round 1's tail: one hairline along Q's tail axis (its end face's normal), from the
        # middle of the ring's stroke to the end face
        tail = contours(diff(p, o))[0]
        segs = []
        cur = None
        for v, pts in tail.segments:
            if v == 'moveTo': cur = start = pts[0]
            elif v in ('closePath', 'endPath'):
                if cur != start: segs.append((cur, start)); cur = start
            else: segs.append((cur, pts[-1])); cur = pts[-1]
        far = max(segs, key=lambda s: math.dist(((s[0][0] + s[1][0]) / 2, (s[0][1] + s[1][1]) / 2), (cx, cy)))
        end = ((far[0][0] + far[1][0]) / 2, (far[0][1] + far[1][1]) / 2)
        ax = (far[1][1] - far[0][1], far[0][0] - far[1][0]); n_ = math.hypot(*ax); ax = (ax[0] / n_, ax[1] / n_)
        if ax[0] * (end[0] - cx) + ax[1] * (end[1] - cy) < 0: ax = (-ax[0], -ax[1])
        # walk in from the end along the axis to the ring's hairline, then halfway into it
        start = None
        for i in range(1, 400):
            q = (end[0] - ax[0] * i * 2, end[1] - ax[1] * i * 2)
            if L.contains(q):
                j = i
                while L.contains((end[0] - ax[0] * j * 2, end[1] - ax[1] * j * 2)): j += 1
                start = (end[0] - ax[0] * (i + j) , end[1] - ax[1] * (i + j)); break
        tl = stroke_open([start, end], t)
        # level the end with Q's tail's lowest point
        dy = p.bounds[1] - tl.bounds[1]
        tl = stroke_open([start, (end[0] + ax[0] * dy / ax[1], end[1] + dy)], t)
        finish('Q', union(L, tl, inline(L, xl + DR - t, ym), inline(L, xr - DR, ym)))

    def dC():
        p = path_of('C'); L = light(p, 'C'); b = L.bounds; ym = (b[1] + b[3]) / 2
        xl = extreme_x(L, -1, b[1], b[3])[0]
        finish('C', union(L, inline(L, xl + DR - t, ym)))

    def dG():
        p = path_of('G'); L = light(p, 'G'); b = L.bounds; ym = (b[1] + b[3]) / 2
        xl = extreme_x(L, -1, b[1], b[3])[0]
        # G's bar: the first stroke standing free of the bowl, probed in from the right
        bar = next(s for f in (0.2, 0.25, 0.3, 0.35, 0.4) for s in vspans(p, b[2] - (b[2] - b[0]) * f)
                   if s[0] > b[1] + 50 and s[1] < b[3] - 50)
        xr = hspans(L, mid(bar) - 60)[-1][1]
        sp = inline(L, xr - D, bar[0] - 5)
        finish('G', union(L, inline(L, xl + DR - t, ym), sp))

    def dU():
        p = path_of('U'); L = light(p, 'U'); b = L.bounds
        xl = b[0]
        cap = rect(xl, CH - t, xl + D, CH)
        sp = vspans(L, xl + D - t / 2)
        lo = max((s for s in sp if s[1] < CH * 0.5), key=lambda s: s[1])
        finish('U', union(L, cap, rect(xl + D - t, mid(lo), xl + D, CH)), box=(-BIG, -BIG, BIG, CH))

    def dJ():
        # the hook reaches as far left of the doubled stem's middle as J's hook reaches left
        # of its stem's middle: the hairline J is set (D - s) / 2 wider, to the left
        p = path_of('J'); pb_ = p.bounds; st_ = hspans(p, CH * 0.6)[-1]
        L = light(p, 'J', (pb_[0] - (D - width(st_)) / 2, pb_[1], pb_[2], pb_[3])); b = L.bounds
        xr = hspans(L, CH * 0.6)[-1][1]
        cap = rect(xr - D, CH - t, xr, CH)
        sp = vspans(L, xr - D + t / 2)
        lo = max((s for s in sp if s[1] < CH * 0.3), key=lambda s: s[1])
        finish('J', union(L, cap, rect(xr - D, mid(lo), xr - D + t, CH)), box=(-BIG, -BIG, BIG, CH))

    def dS():
        p = path_of('S'); L = light(p, 'S'); b = L.bounds; Hh = b[3] - b[1]
        yu = b[1] + 0.73 * Hh; yl = b[1] + 0.27 * Hh
        xl = extreme_x(L, -1, b[1] + 0.55 * Hh, b[3] - 0.1 * Hh)[0]
        xr = extreme_x(L, 1, b[1] + 0.1 * Hh, b[1] + 0.45 * Hh)[0]
        finish('S', union(L, inline(L, xl + DR - t, yu), inline(L, xr - DR, yl)))

    # ---- figures ----------------------------------------------------------------------
    def dzero(): dO('zero')

    def done():
        p = path_of('one'); b = p.bounds; top = b[3]
        xs = stem_x(p, 0.2, 0.6); st = [s for s in hspans(p, top * 0.4) if s[0] <= xs <= s[1]][0]
        i1, c1 = vband(xs, 0, top)
        foot = vspans(p, b[0] + 5)[0]                  # the foot, left of the stem
        footp = rect(b[0], 0, b[2], t)
        # the flag: its centre line from the tip to where it meets the stem
        sp_lo = [s for s in vspans(p, st[0] - 30) if s[0] > foot[1] + 10]
        sp_hi = [s for s in vspans(p, st[0] - 90) if s[0] > foot[1] + 10]
        f0 = (st[0] - 90, mid(sp_hi[0])); f1 = (st[0] - 30, mid(sp_lo[0]))
        dx, dy = f1[0] - f0[0], f1[1] - f0[1]
        # the flag's tip: its leftmost ink above the foot
        tipx = min(s_[0] for y in [top * f for f in (0.6, 0.65, 0.7, 0.75, 0.8)] for s_ in hspans(p, y))
        # at the flag's own slope, its upper edge runs into the doubled stem's top-left corner
        # (xs - D / 2, top), so the flag and the stem's cap meet in one corner
        k_ = dy / dx; cx_, cy_ = xs - D / 2, top - (t / 2) * math.hypot(1, k_)
        yat = lambda x: cy_ + (x - cx_) * k_
        a0 = (tipx, yat(tipx)); a1 = (xs, yat(xs))
        flag = stroke_open([a0, a1], t)
        finish('one', union(i1, footp, flag), [c1], (-BIG, 0, BIG, top))

    def dtwo():
        """Parallel inner rail: original base left edge to analytic bowl-stroke centre.
        Its one new white counter meets the bowl through an exact source-jet bridge.
        The old local hard-band dilation and one-unit entrance walk are not used.
        """
        p = path_of('two'); pb = p.bounds
        factory = lambda x: light(p, 'two', (x, pb[1], pb[2], pb[3]))
        ink, attachment = _join_geometry.attached_two(
            factory, pb, t, g, hspans, vspans, rect, union, clip)
        join_roles['two'] = ('two-rails', (attachment['sourceHairline'], attachment['copy']))
        finish('two', ink)

    def dthree():
        """One inline through both bowls, as Noto's: DR inside the lower bowl's right extreme,
        but at least 1.5 t inside the end of the middle bar, so it crosses the bar whole."""
        p = path_of('three'); L = light(p, 'three'); b = L.bounds; Hh = b[3] - b[1]
        xr = extreme_x(L, 1, b[1] + 0.1 * Hh, b[1] + 0.4 * Hh)[0]
        ym = vspans(L, b[0] + 0.5 * (b[2] - b[0]))
        ym = [s_ for s_ in ym if b[1] + 0.3 * Hh < mid(s_) < b[1] + 0.7 * Hh][0]
        bar_end = hspans(L, mid(ym))[-1][1]
        x = min(xr - DR, bar_end - 1.5 * t)
        sp = vspans(L, x + t / 2)
        finish('three', union(L, rect(x, mid(sp[0]), x + t, mid(sp[-1]))))

    def dfive():
        p = path_of('five'); L = light(p, 'five'); b = L.bounds; Hh = b[3] - b[1]
        xl = hspans(L, b[1] + 0.85 * Hh)[0][0]
        x = xl + D - t
        sp = vspans(L, x + t / 2)
        stem = rect(x, mid(sp[-2]), x + t, mid(sp[-1]))
        xr = extreme_x(L, 1, b[1] + 0.1 * Hh, b[1] + 0.5 * Hh)[0]
        bowl_mid = b[1] + 0.3 * Hh
        finish('five', union(L, stem, inline(L, xr - DR, bowl_mid)))

    def closed_up(L):
        """L with the narrow wedge where a bowl meets the side filled (a closing by DS_CLOSE t, 0.5),
        so no sliver of a counter opens there at some weights and not others."""
        r = c.P('DS_CLOSE', 0.5) * t
        return eroded(dilated(L, r, r), r, r)

    def bowl_depth(L, cnt_box):
        """A 6's or 9's crescent depth: DR, but at most DS69_K (0.38) of its bowl's counter
        width (the bowl does not grow with the weight; DR does), so at heavy weights the
        inlines stay near the edge instead of walking in towards the bowl's middle; and never
        less than D, a straight doubled stroke, so the crescent's gap stays at least g.
        Binds from about Medium up; Light and Regular keep DR."""
        cw = cnt_box[2] - cnt_box[0]
        return max(D, min(DR, c.P('DS69_K', 0.38) * cw))

    def bowl_ends_on_inline(L, side, x_in, left):
        """L without the stretch of the bowl's hairline that crosses between the side and the
        side's inline: everything of L on the side's side of the inline, over the height of
        the two crescents, that is more than t in from the outer edge (so the side is
        exactly a hairline there, with no step where the cut ends). The bowl then ends on the inline, as Noto's does,
        and the crescent between side and inline runs whole from end to end."""
        holes = contours(union(L, side))[1:]
        holes = [h for h in holes if (h.bounds[2] <= x_in + 1 if left else h.bounds[0] >= x_in - 1)]
        holes = sorted(holes, key=lambda h: -(h.bounds[2] - h.bounds[0]) * (h.bounds[3] - h.bounds[1]))[:2]
        if len(holes) < 2: return L
        lo, hi = sorted(holes, key=lambda h: h.bounds[1])
        y0, y1 = lo.bounds[1], hi.bounds[3]                       # the whole crescent, so the side is t throughout
        Fo = contours(union(L, side))[0]; Fo.simplify()
        strip = rect(-BIG, y0, x_in, y1) if left else rect(x_in, y0, BIG, y1)
        cut = pathops.op(eroded(Fo, t, t), strip, pathops.PathOp.INTERSECTION)
        side_rails['six' if left else 'nine'] = (L, cut)
        return diff(L, cut)

    def outer_full(L):
        """L with its outer edge's hairline at least t deep everywhere (the italic masters' hairline
        6 and 9 run thin along their curves)."""
        Fo = pathops.Path(contours(L)[0]); Fo.simplify()
        return union(L, diff(Fo, eroded(Fo, t, t)))

    def dsix():
        """Noto's 6: the side doubled by one inline from the hook down through the bowl to its
        foot, the bowl's hairline ending on that inline, and the bowl's right side by its own
        inline."""
        p = path_of('six'); L = outer_full(closed_up(light(p, 'six'))); b = L.bounds
        cnt = contours(p)[1].bounds; cb = contours(L)[1].bounds
        dr = bowl_depth(L, cb)
        xl = extreme_x(L, -1, b[1], b[3])[0]
        xr = extreme_x(L, 1, cnt[1], cnt[3])[0]
        x = xl + dr - t; sp = vspans(L, x + t / 2)
        side = rect(x, mid(sp[0]), x + t, mid(sp[-1]))
        L2 = bowl_ends_on_inline(L, side, x, True)
        join_roles['six'] = ('side-left', x)
        finish('six', union(L2, side, inline(L, xr - dr, (cnt[1] + cnt[3]) / 2)))

    def dnine():
        """The 6 turned: the side doubled by one inline from the tail up through the bowl to
        its top, the bowl's hairline ending on it, the bowl's left side by its own inline."""
        p = path_of('nine'); L = outer_full(closed_up(light(p, 'nine'))); b = L.bounds
        cnt = contours(p)[1].bounds; cb = contours(L)[1].bounds
        dr = bowl_depth(L, cb)
        xr = extreme_x(L, 1, b[1], b[3])[0]
        xl = extreme_x(L, -1, cnt[1], cnt[3])[0]
        x = xr - dr; sp = vspans(L, x + t / 2)
        side = rect(x, mid(sp[0]), x + t, mid(sp[-1]))
        L2 = bowl_ends_on_inline(L, side, x + t, False)
        join_roles['nine'] = ('side-right', x + t)
        finish('nine', union(L2, side, inline(L, xl + dr - t, (cnt[1] + cnt[3]) / 2)))

    def dseven():
        p = path_of('seven'); b = p.bounds; top = b[3]
        cD = centre_line(p, top * 0.15, top * 0.3, 0)
        band, cnt = dband(ext(*cD), 0, top)
        # the crossbar: probed in the part of it that stands free left of the diagonal (the
        # diagonal's left edge run up from below the bar), so a heavy diagonal never swallows it
        dl = edge_pts(p, top * 0.15, top * 0.3, 0, 0); kx = (dl[1][0] - dl[0][0]) / (dl[1][1] - dl[0][1])
        dleft = lambda y: dl[0][0] + kx * (y - dl[0][1])
        y_tb = min(s_[0] for s_ in vspans(p, (b[0] + b[2]) / 2) if s_[1] > top - 1)   # the top bar's underside
        rows = [y for y in (top * (0.3 + 0.01 * k) for k in range(56)) if y < y_tb - 10 and hspans(p, y)[0][0] < dleft(y) - 20]
        mbar = []
        if rows:
            yb = rows[len(rows) // 2]; xl0 = hspans(p, yb)[0][0]
            mbar = [s for s in vspans(p, (xl0 + dleft(yb)) / 2) if s[0] <= yb <= s[1] and s[1] < top - 80]
        parts = [rect(b[0], top - t, b[2], top), clip(band, (-BIG, 0, b[2], top))]
        if mbar:
            m = mbar[-1]; xs_ = hspans(p, mid(m))
            parts.append(rect(xs_[0][0], mid(m) - t / 2, xs_[-1][1], mid(m) + t / 2))
        finish('seven', union(*parts), [clip(cnt, (-BIG, -BIG, b[2] - t, BIG))])

    def dfour():
        p = path_of('four'); b = p.bounds; top = b[3]
        xs = stem_x(p, 0.02, 0.2)
        i1, c1 = vband(xs, 0, top)
        bar = vspans(p, b[0] + 10)[0]
        barp = rect(b[0], bar[0], b[2], bar[0] + t)
        dg = edge_pts(p, top * 0.5, top * 0.7, 0, 0)
        diag = clip(edge_thin(*dg, (b[2], 0)), (b[0], bar[0], xs, top))
        finish('four', union(i1, barp, diag), [c1], (-BIG, 0, BIG, top))

    def deight():
        p = path_of('eight'); L = light(p, 'eight'); b = L.bounds
        cs = sorted((q.bounds for q in contours(L)[1:]), key=lambda bb: bb[1])
        parts = [L]
        for cb in cs[-2:] if len(cs) >= 2 else []:
            ym = (cb[1] + cb[3]) / 2
            xl = extreme_x(L, -1, cb[1], cb[3])[0]; xr = extreme_x(L, 1, cb[1], cb[3])[0]
            parts += [inline(L, xl + DR - t, ym), inline(L, xr - DR, ym)]
        finish('eight', union(*parts))

    table = {'A': dA, 'B': dB, 'C': dC, 'D': dD, 'E': lambda: dEFL('E'), 'F': lambda: dEFL('F'), 'G': dG, 'H': dH,
             'I': dI, 'J': dJ, 'K': dK, 'L': lambda: dEFL('L'), 'M': dM, 'N': dN, 'O': dO, 'P': dP, 'Q': dQ, 'R': dR,
             'S': dS, 'T': dT, 'U': dU, 'V': dV, 'W': dW, 'X': dX, 'Y': dY, 'Z': dZ,
             'zero': dzero, 'one': done, 'two': dtwo, 'three': dthree, 'four': dfour, 'five': dfive, 'six': dsix,
             'seven': dseven, 'eight': deight, 'nine': dnine}
    for k in (which or table):
        table[k]()
    return out


def doublestruck_lowercase(c, which=('b', 'c', 'd', 'h', 'i', 'j', 'l', 'm', 'n', 'o', 'p', 'q', 'u', 'v', 'w', 'x', 'y', 'z')):
    """Eighteen lowercase forms using style contours, fitted light-master c and j outlines, and lowercase stem measurements.

    The capital/digit builder and its ds_strokes record are independent of this path.
    Bowls use hairline rings with straight inlines; straight stems use closed doubled bands.
    """
    width = lambda span: span[1] - span[0]
    mid = lambda span: (span[0] + span[1]) / 2
    median = lambda values: sorted(values)[len(values) // 2]
    rect, union, diff = c.rect, c.union, c.diff
    intersect = lambda a, b: pathops.op(a, b, pathops.PathOp.INTERSECTION)
    paths = {base: c.path_of(base) for base in ('b', 'c', 'd', 'h', 'i', 'j', 'l', 'm', 'n', 'o', 'p', 'q', 'u', 'v', 'w', 'x', 'y', 'z')}
    # Straight ascender rows avoid both the bowl and the shoulder join.
    stems = []
    for base in ('b', 'd'):
        p = paths[base]
        for frac in (0.70, 0.80, 0.90):
            y = c.XH + frac * (p.bounds[3] - c.XH)
            spans = c.hspans(p, y)
            if len(spans) != 1:
                raise ValueError(f'double-struck lowercase {base}: ambiguous ascender at {y}')
            stems.append(width(spans[0]))
    stem = median(stems)
    if stem <= 0:
        raise ValueError('double-struck lowercase: nonpositive stem')
    # The median Regular b/d ascender measure is 66 units (b=66, d=65).
    u = stem / 66.0
    t = (66.0 * NOTO_T / NOTO_STEM) * (u if u <= 1 else u ** 0.5)
    gap = t * NOTO_G / NOTO_T
    doubled = 2 * t + gap
    depth = doubled * NOTO_DR / NOTO_D

    def contours(p):
        result = []
        for contour in p.contours:
            q = pathops.Path(); contour.draw(q.getPen()); result.append(q)
        return sorted(result, key=lambda q: -(q.bounds[2] - q.bounds[0]) * (q.bounds[3] - q.bounds[1]))

    def eroded(p, amount):
        stroke = pathops.Path(p)
        stroke.stroke(2 * amount, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        stroke.convertConicsToQuads(); stroke.simplify()
        return diff(p, stroke)

    def ring(p):
        return diff(p, eroded(p, t))

    def rail(outline, x, y):
        spans = c.vspans(outline, x + t / 2)
        below = [s for s in spans if s[1] < y]
        above = [s for s in spans if s[0] > y]
        if not below or not above:
            raise ValueError(f'double-struck lowercase: no bowl edges for rail at {(x, y)}')
        lo, hi = max(below, key=lambda s: s[1]), min(above, key=lambda s: s[0])
        r = rect(x, mid(lo), x + t, mid(hi))
        for edge in (lo, hi):
            end = c.clip(r, (-3000, edge[0], 3000, edge[1]))
            if not intersect(end, outline).area:
                raise ValueError('double-struck lowercase: rail does not overlap both bowl edges')
        return r

    out = {}
    for base in which:
        if base not in paths:
            raise ValueError(f'double-struck lowercase: unsupported {base}')
        p = paths[base]; bounds = p.bounds
        if base == 'y':
            from fontTools.pens.basePen import BasePen

            class TailPen(BasePen):
                def __init__(self):
                    super().__init__(None)
                    self.segments = []
                    self.point = self.start = None

                def _moveTo(self, point):
                    self.point = self.start = point

                def _lineTo(self, point):
                    self.segments.append(('L', self.point, point)); self.point = point

                def _qCurveToOne(self, control, point):
                    self.segments.append(('Q', self.point, control, point)); self.point = point

                def _curveToOne(self, a, b, point):
                    raise ValueError('double-struck lowercase y: expected quadratic descender')

                def _closePath(self):
                    if self.point != self.start:
                        self._lineTo(self.start)

            canonical = pathops.Path(p); canonical.simplify(fix_winding=True)
            pen = TailPen(); canonical.draw(pen)
            segs = pen.segments; chains = []
            for j, seg in enumerate(segs):
                if seg[0] != 'Q' or segs[(j - 1) % len(segs)][0] == 'Q':
                    continue
                chain = []; k = j
                while segs[k % len(segs)][0] == 'Q':
                    chain.append(segs[k % len(segs)]); k += 1
                    if k - j > len(segs):
                        raise ValueError('double-struck lowercase y: cyclic curve chain')
                chains.append(chain)
            if sorted(len(chain) for chain in chains) != [3, 4] or len(list(canonical.contours)) != 1:
                raise ValueError('double-struck lowercase y: unexpected descender chains')
            outer = next(chain for chain in chains if len(chain) == 4)
            if outer[0][1][1] > outer[-1][-1][1]:
                outer = [('Q', q[-1], q[2], q[1]) for q in reversed(outer)]
            tail_tip, attachment = outer[0][1], outer[-1][-1]
            if abs(tail_tip[1] - bounds[1]) > .1 or attachment[1] >= 0 or bounds[1] >= 0:
                raise ValueError('double-struck lowercase y: invalid outer descender roles')
            continuations = []
            for seg in segs:
                if seg[0] != 'L': continue
                if math.dist(seg[1], attachment) < .01: continuations.append(seg[-1])
                elif math.dist(seg[-1], attachment) < .01: continuations.append(seg[1])
            if len(continuations) != 1 or abs(continuations[0][1] - bounds[3]) > .1:
                raise ValueError('double-struck lowercase y: missing right terminal edge')
            right_tip = continuations[0]
            boundary = pathops.Path(); bp = boundary.getPen(); bp.moveTo(tail_tip)
            for q in outer: bp.qCurveTo(q[2], q[-1])
            bp.lineTo(right_tip); bp.endPath()
            # Only this outside boundary is stroked. Intersecting the
            # source selects its inward half without eroding concave junctions.
            stroke = pathops.Path(boundary)
            stroke.stroke(2 * t, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
            stroke.convertConicsToQuads(); stroke.simplify()
            hairline = intersect(stroke, p)
            if len(list(hairline.contours)) != 1:
                raise ValueError('double-struck lowercase y: discontinuous right hairline')
            # Verify that the source supplies the inward thickness along every
            # extracted quadratic, not merely at its bounding box.
            for j, q in enumerate(outer):
                a, control, b = q[1:]
                for u in (.25, .5, .75):
                    v = 1 - u
                    pt = (v*v*a[0] + 2*v*u*control[0] + u*u*b[0],
                          v*v*a[1] + 2*v*u*control[1] + u*u*b[1])
                    tangent = (2*(v*(control[0]-a[0])+u*(b[0]-control[0])),
                               2*(v*(control[1]-a[1])+u*(b[1]-control[1])))
                    length = math.hypot(*tangent)
                    if length <= 0:
                        raise ValueError('double-struck lowercase y: degenerate tail tangent')
                    nx, ny = -tangent[1]/length, tangent[0]/length
                    if not any(p.contains((pt[0]+sign*t*nx, pt[1]+sign*t*ny)) for sign in (-1, 1)):
                        raise ValueError(f'double-struck lowercase y: exhausted source tail thickness at curve {j}')
            height = bounds[3]
            upper_join = max(seg[1][1] for seg in segs if seg[0] == 'L' and 0 < seg[1][1] < height)
            ys = [upper_join + f*(height-upper_join) for f in (.25, .5, .75)]
            rows = [c.hspans(p,y) for y in ys]
            if any(len(row) != 2 for row in rows):
                raise ValueError('double-struck lowercase y: ambiguous upper arms')
            right_slope = (right_tip[0] - attachment[0]) / (right_tip[1] - attachment[1])
            if any(width(row[-1]) / math.hypot(1, right_slope) < t for row in rows):
                raise ValueError('double-struck lowercase y: exhausted right-arm thickness')
            k = (mid(rows[-1][0])-mid(rows[0][0]))/(ys[-1]-ys[0])
            xzero = mid(rows[0][0])-k*ys[0]
            if k >= 0 or abs(xzero+k*ys[1]-mid(rows[1][0])) > 1:
                raise ValueError('double-struck lowercase y: invalid left diagonal')
            def diagonal(normal_width, y0, y1):
                xa, xb = xzero+k*y0, xzero+k*y1
                dx = normal_width*math.hypot(1,k)/2
                q = pathops.Path(); qp=q.getPen(); qp.moveTo((xa-dx,y0)); qp.lineTo((xa+dx,y0))
                qp.lineTo((xb+dx,y1)); qp.lineTo((xb-dx,y1)); qp.closePath(); return q
            band = diagonal(doubled,0,height)
            slot = diagonal(gap,t,height-t)
            if not intersect(band,hairline).area:
                raise ValueError('double-struck lowercase y: disconnected arm/descender junction')
            ink = union(band,hairline)
            if not slot.area or abs(diff(slot,ink).area) > .01:
                raise ValueError('double-struck lowercase y: unenclosed left slot')
            result = diff(ink,slot)
            if len(list(result.contours)) != 2 or not intersect(diff(band,slot),diff(hairline,slot)).area:
                raise ValueError('double-struck lowercase y: slot or junction is not closed')
        elif base == 'x':
            from fontTools.pens.recordingPen import RecordingPen
            p = pathops.Path(p); p.simplify(fix_winding=True)
            if any(abs(p.bounds[j] - bounds[j]) > .1 for j in (1, 3)):
                raise ValueError('double-struck lowercase x: canonical vertical bounds changed')
            record = RecordingPen(); p.draw(record)
            vertices = []
            for verb, points in record.value:
                if verb in ('moveTo', 'lineTo'):
                    vertices.append(points[0])
                elif verb != 'closePath':
                    raise ValueError('double-struck lowercase x: expected straight source')
            if len(vertices) != 12 or len(list(p.contours)) != 1 or bounds[1] != 0:
                raise ValueError('double-struck lowercase x: unexpected source polygon')
            height = bounds[3]
            feet = sorted(pt for pt in vertices if abs(pt[1]) < .01)
            heads = sorted(pt for pt in vertices if abs(pt[1] - height) < .01)
            crossing = [pt for pt in vertices if .01 < pt[1] < height - .01]
            if len(feet) != 4 or len(heads) != 4 or len(crossing) != 4:
                raise ValueError('double-struck lowercase x: invalid terminal/crossing roles')
            centre = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            descending = (centre(heads[0], heads[1]), centre(feet[2], feet[3]))
            rising = (centre(feet[0], feet[1]), centre(heads[2], heads[3]))
            low, high = min(pt[1] for pt in crossing), max(pt[1] for pt in crossing)
            if not 0 < low < high < height:
                raise ValueError('double-struck lowercase x: invalid crossing interval')
            def slope(line):
                return (line[1][0] - line[0][0]) / (line[1][1] - line[0][1])
            if slope(descending) >= 0 or slope(rising) <= 0:
                raise ValueError('double-struck lowercase x: invalid diagonal directions')
            residual = 0
            for j, line in enumerate((descending, rising)):
                a, b = line
                for upper in (False, True):
                    ys = [high + f * (height - high) if upper else f * low for f in (.25, .5, .75)]
                    for y in ys:
                        spans = c.hspans(p, y)
                        if len(spans) != 2:
                            raise ValueError('double-struck lowercase x: ambiguous source limbs')
                        idx = (0 if upper else 1) if j == 0 else (1 if upper else 0)
                        pt = (mid(spans[idx]), y)
                        distance = abs((b[0] - a[0]) * (pt[1] - a[1])
                                       - (b[1] - a[1]) * (pt[0] - a[0])) / math.dist(a, b)
                        residual = max(residual, distance)
            # Thin-slice offsets reach 2.5282 units; one-unit strip measurements
            # reach 2.5473. The 3.25-unit bound includes a rounding allowance.
            if residual > 3.25:
                raise ValueError(f'double-struck lowercase x: optical limb residual {residual:.4f} exceeds 3.25')
            def diagonal(line, normal_width, y0, y1):
                k = slope(line); a = line[0]
                x0 = a[0] + (y0 - a[1]) * k
                x1 = a[0] + (y1 - a[1]) * k
                dx = normal_width * math.hypot(1, k) / 2
                q = pathops.Path(); pen = q.getPen()
                pen.moveTo((x0 - dx, y0)); pen.lineTo((x0 + dx, y0))
                pen.lineTo((x1 + dx, y1)); pen.lineTo((x1 - dx, y1)); pen.closePath()
                return q
            band = diagonal(descending, doubled, 0, height)
            hairline = diagonal(rising, t, 0, height)
            slot = diagonal(descending, gap, t, height - t)
            ink = union(band, hairline)
            if not slot.area or abs(diff(slot, ink).area) > .01:
                raise ValueError('double-struck lowercase x: unenclosed continuous slot')
            result = diff(ink, slot)
            remaining_band = diff(band, slot)
            for j, region in enumerate(((0, low), (high, height))):
                arm = c.clip(hairline, (-3000, region[0], 5000, region[1]))
                if not diff(arm, slot).area:
                    raise ValueError(f'double-struck lowercase x: missing rising arm {j}')
            for j, region in enumerate(((0, high), (low, height))):
                arm = c.clip(hairline, (-3000, region[0], 5000, region[1]))
                if not intersect(diff(arm, slot), remaining_band).area:
                    raise ValueError(f'double-struck lowercase x: detached rising arm {j}')
            if len(list(result.contours)) != 2:
                raise ValueError('double-struck lowercase x: expected one closed crossing slot')
        elif base == 'z':
            from fontTools.pens.recordingPen import RecordingPen
            p = pathops.Path(p); p.simplify(fix_winding=True)
            if any(abs(p.bounds[j] - bounds[j]) > .1 for j in (1, 3)):
                raise ValueError('double-struck lowercase z: canonical vertical bounds changed')
            record = RecordingPen(); p.draw(record)
            vertices = []
            for verb, points in record.value:
                if verb in ('moveTo', 'lineTo'):
                    vertices.append(points[0])
                elif verb != 'closePath':
                    raise ValueError('double-struck lowercase z: expected straight polygon')
            if len(vertices) != 10 or len(list(p.contours)) != 1 or bounds[1] != 0:
                raise ValueError('double-struck lowercase z: unexpected source polygon')
            height = bounds[3]
            edges = list(zip(vertices, vertices[1:] + vertices[:1]))
            horizontal = [(a, b) for a, b in edges if abs(a[1] - b[1]) < .01]
            top_edges = [(a, b) for a, b in horizontal if abs(a[1] - height) < .1]
            bottom_edges = [(a, b) for a, b in horizontal if abs(a[1]) < .1]
            inner_edges = [(a, b) for a, b in horizontal if .1 < a[1] < height - .1]
            if len(top_edges) != 1 or len(bottom_edges) != 1 or len(inner_edges) != 2:
                raise ValueError('double-struck lowercase z: ambiguous terminal roles')
            top_span = sorted(point[0] for point in top_edges[0])
            bottom_span = sorted(point[0] for point in bottom_edges[0])
            low, high = sorted(edge[0][1] for edge in inner_edges)
            if low <= 0 or high >= height or low >= high:
                raise ValueError('double-struck lowercase z: invalid clear body interval')
            ys = [low + f * (high - low) for f in (.25, .5, .75)]
            rows = [c.hspans(p, y) for y in ys]
            if any(len(row) != 1 for row in rows):
                raise ValueError('double-struck lowercase z: ambiguous diagonal')
            k = (mid(rows[-1][0]) - mid(rows[0][0])) / (ys[-1] - ys[0])
            xzero = mid(rows[0][0]) - k * ys[0]
            if k <= 0 or abs(mid(rows[1][0]) - (xzero + k * ys[1])) > 1:
                raise ValueError('double-struck lowercase z: invalid rising diagonal')
            def diagonal(normal_width, y0, y1):
                dx = normal_width * math.hypot(1, k) / 2
                xa, xb = xzero + k * y0, xzero + k * y1
                q = pathops.Path(); pen = q.getPen()
                pen.moveTo((xa - dx, y0)); pen.lineTo((xa + dx, y0))
                pen.lineTo((xb + dx, y1)); pen.lineTo((xb - dx, y1)); pen.closePath()
                return q
            band = c.clip(diagonal(doubled, 0, height), (bounds[0], 0, bounds[2], height))
            top = rect(top_span[0], height - t, top_span[1], height)
            bottom = rect(bottom_span[0], 0, bottom_span[1], t)
            if not intersect(band, top).area or not intersect(band, bottom).area:
                raise ValueError('double-struck lowercase z: disconnected terminal')
            slot = c.clip(diagonal(gap, t, height - t),
                          (bounds[0] + t, t, bounds[2] - t, height - t))
            ink = union(band, top, bottom)
            if not slot.area or abs(diff(slot, ink).area) > .01:
                raise ValueError('double-struck lowercase z: unenclosed diagonal slot')
            result = diff(ink, slot)
            if len(list(result.contours)) != 2:
                raise ValueError('double-struck lowercase z: expected one closed slot')
        elif base in ('v', 'w'):
            from fontTools.pens.recordingPen import RecordingPen
            # Source heavy italics contain crossing diagonal ledges. Measure the
            # same filled outline as the final overlap cleanup, without changing
            # the source path or its bounds/advance contract.
            p = pathops.Path(p)
            p.simplify(fix_winding=True)
            if abs(p.bounds[1] - bounds[1]) > .1 or abs(p.bounds[3] - bounds[3]) > .1:
                raise ValueError(f'double-struck lowercase {base}: canonical vertical bounds changed')
            record = RecordingPen(); p.draw(record)
            vertices = []
            for verb, points in record.value:
                if verb in ('moveTo', 'lineTo'):
                    vertices.append(points[0])
                elif verb != 'closePath':
                    raise ValueError(f'double-struck lowercase {base}: expected straight source polygon')
            expected = 6 if base == 'v' else 12
            if len(vertices) != expected + 1 or len(list(p.contours)) != 1:
                raise ValueError(f'double-struck lowercase {base}: unexpected source polygon')
            height = bounds[3]
            # Boolean canonicalization may rotate or reverse the contour. Anchor
            # the role order at the left baseline corner, then the left terminal.
            feet = [j for j, point in enumerate(vertices) if abs(point[1]) <= .1]
            if not feet:
                raise ValueError(f'double-struck lowercase {base}: missing baseline corner')
            start = min(feet, key=lambda j: vertices[j][0])
            vertices = vertices[start:] + vertices[:start]
            if abs(vertices[1][1] - height) > .1:
                vertices = vertices[:1] + list(reversed(vertices[1:]))
            count = 2 if base == 'v' else 4
            terminal_indices = (1, 2, 4, 5) if base == 'v' else (1, 2, 4, 5, 7, 8)
            baseline_indices = (0, 6) if base == 'v' else (0, 9, 10, 12)
            if (any(abs(vertices[j][1] - height) > .1 for j in terminal_indices)
                    or any(abs(vertices[j][1]) > .1 for j in baseline_indices)):
                raise ValueError(f'double-struck lowercase {base}: unexpected terminal roles')
            lower = vertices[3][1] if base == 'v' else max(vertices[3][1], vertices[6][1])
            upper = height if base == 'v' else vertices[11][1]
            if upper <= lower:
                raise ValueError(f'double-struck lowercase {base}: no separated diagonal interval')
            ys = [lower + (upper - lower) * f for f in (.25, .5, .75)]
            rows = [sorted(c.hspans(p, y)) for y in ys]
            if bounds[1] != 0 or any(len(row) != count for row in rows):
                raise ValueError(f'double-struck lowercase {base}: invalid diagonal geometry')
            def line_x(line, y):
                a, b = line
                return a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            centres = [((mid(rows[0][j]), ys[0]), (mid(rows[-1][j]), ys[-1])) for j in range(count)]
            for j, line in enumerate(centres):
                if abs(line_x(line, ys[1]) - mid(rows[1][j])) > 1:
                    raise ValueError(f'double-struck lowercase {base}: diagonal {j} is not linear')
            for j, line in enumerate(centres):
                direction = line[1][0] - line[0][0]
                if (direction >= 0 if j % 2 == 0 else direction <= 0):
                    raise ValueError(f'double-struck lowercase {base}: diagonal {j} has wrong slope')
            def polygon(points):
                q = pathops.Path(); pen = q.getPen(); pen.moveTo(points[0])
                for pt in points[1:]: pen.lineTo(pt)
                pen.closePath(); return q
            def slope(line):
                return (line[1][0] - line[0][0]) / (line[1][1] - line[0][1])
            def strip(line, normal_width, y0=0, y1=None):
                y1 = height if y1 is None else y1
                dx = normal_width * math.hypot(1, slope(line)) / 2
                a, b = line_x(line, y0), line_x(line, y1)
                return polygon([(a - dx, y0), (a + dx, y0), (b + dx, y1), (b - dx, y1)])
            def side(line, left):
                a, b = line_x(line, -3000), line_x(line, 3000)
                edge = -5000 if left else 5000
                return polygon([(edge, -3000), (a, -3000), (b, 3000), (edge, 3000)])
            def shifted(line, dx):
                return tuple((pt[0] + dx, pt[1]) for pt in line)
            doubled_lines = [centres[0]] + ([centres[2]] if base == 'w' else [])
            bands = [strip(line, doubled) for line in doubled_lines]
            slots = [strip(line, gap, t, height - t) for line in doubled_lines]
            # Preserve the source's right outside edge; measure its actual slope.
            edge = ((rows[0][-1][1], ys[0]), (rows[-1][-1][1], ys[-1]))
            dx = t * math.hypot(1, slope(edge))
            right_thin = strip(shifted(edge, -dx / 2), t)
            slots[-1] = intersect(slots[-1], side(shifted(edge, -dx), True))
            parts = bands + [right_thin]
            if base == 'w':
                # Join the source-derived doubled bands corner to corner. The
                # terminal height is this lowercase w's own central terminal.
                end0 = line_x(doubled_lines[0], 0) + doubled / 2 * math.hypot(1, slope(doubled_lines[0]))
                end1 = line_x(doubled_lines[1], height) - doubled / 2 * math.hypot(1, slope(doubled_lines[1]))
                k = slope(centres[1])
                wd = t * math.hypot(1, k)
                x0 = end0 - wd
                top = x0 + k * height
                shift = top - end1
                # Preserve the source ascending angle and translate the entire
                # right pair to meet the middle hairline.
                bands[1] = c.mv(bands[1], shift)
                slots[1] = c.mv(slots[1], shift)
                edge = shifted(edge, shift)
                right_thin = c.mv(right_thin, shift)
                thin_edge = ((x0, 0), (top, height))
                if abs(slope(thin_edge) - k) > 1e-9:
                    raise ValueError('double-struck lowercase w: middle source slope changed')
                middle = strip(shifted(thin_edge, wd / 2), t)
                parts = bands + [right_thin, middle]
                slots[0] = intersect(slots[0], side(thin_edge, True))
                slots[1] = intersect(slots[1], side(shifted(thin_edge, wd), False))
            if not intersect(bands[-1], right_thin).area:
                raise ValueError(f'double-struck lowercase {base}: detached right hairline')
            if base == 'w' and any(not intersect(band, middle).area for band in bands):
                raise ValueError('double-struck lowercase w: detached middle hairline')
            ink = intersect(union(*parts), side(edge, True))
            for j, slot in enumerate(slots):
                if not slot.area or not intersect(slot, ink).area:
                    raise ValueError(f'double-struck lowercase {base}: empty diagonal slot {j}')
            result = diff(ink, union(*slots))
            if len(list(result.contours)) != len(slots) + 1:
                raise ValueError(f'double-struck lowercase {base}: diagonal slots or joins are not closed')
        elif base == 'u':
            from fontTools.pens.basePen import BasePen

            class LowerPen(BasePen):
                def __init__(self):
                    super().__init__(None)
                    self.segments = []
                    self.point = None

                def _moveTo(self, point):
                    self.point = point

                def _lineTo(self, point):
                    self.segments.append(('L', self.point, point)); self.point = point

                def _qCurveToOne(self, control, point):
                    self.segments.append(('Q', self.point, control, point)); self.point = point

                def _curveToOne(self, a, b, point):
                    raise ValueError('double-struck lowercase u: expected quadratic source')

                def _closePath(self):
                    pass

            pen = LowerPen(); p.draw(pen)
            segments = pen.segments
            chains = []
            nseg = len(segments)
            for i in range(nseg):
                chain = [segments[(i + j) % nseg] for j in range(4)]
                before, after = segments[(i - 1) % nseg], segments[(i + 4) % nseg]
                if (all(q[0] == 'Q' for q in chain) and before[0] == after[0] == 'L'):
                    if chain[0][1][0] > chain[-1][-1][0]:
                        chain = [('Q', q[-1], q[2], q[1]) for q in reversed(chain)]
                    if any(q[1][0] > q[2][0] + 2 or q[2][0] > q[-1][0] + 2 for q in chain):
                        raise ValueError('double-struck lowercase u: nonmonotone lower arch')
                    chains.append(chain)
            if len(chains) != 2:
                raise ValueError('double-struck lowercase u: expected two lower quadratic arches')
            chains.sort(key=lambda chain: min(pt[1] for q in chain for pt in q[1:]))
            outer_chain, inner_chain = chains
            bottom = min(pt[1] for q in outer_chain for pt in q[1:])
            inside_bottom = min(pt[1] for q in inner_chain for pt in q[1:])
            if abs(bottom - bounds[1]) > .1 or inside_bottom <= bottom:
                raise ValueError('double-struck lowercase u: invalid lower arch roles')
            straight = max(inner_chain[0][1][1], inner_chain[-1][-1][1])
            rows = [sorted(c.hspans(p, straight + f * (bounds[3] - straight))) for f in (.3, .5, .7)]
            if any(len(row) != 2 for row in rows):
                raise ValueError('double-struck lowercase u: ambiguous upper stems')
            left, right = [median([mid(row[j]) for row in rows]) for j in range(2)]
            if right - left <= doubled + t:
                raise ValueError('double-struck lowercase u: lower counter clearance exhausted')
            xleft, xright = left - doubled / 2, right - doubled / 2 + t
            # Fit the two actual source boundaries independently. The exterior
            # retains its overshoot; the explicit interior reserves a hairline.
            def lower_profile(chain, inset):
                a, b = chain[0][1], chain[-1][-1]
                low = min(pt[1] for q in chain for pt in q[1:])
                high = max(a[1], b[1])
                target_low = bottom + inset
                target_high = max(outer_chain[0][1][1], outer_chain[-1][-1][1])
                if high <= low or target_high <= target_low:
                    raise ValueError('double-struck lowercase u: invalid lower profile height')
                sx = (xright - xleft - inset) / (b[0] - a[0])
                sy = (target_high - target_low) / (high - low)
                def fitpoint(pt):
                    return (xleft + inset + sx * (pt[0] - a[0]), target_low + sy * (pt[1] - low))
                q = pathops.Path(); qp = q.getPen()
                start = fitpoint(a); end = fitpoint(b)
                qp.moveTo((start[0], bounds[3])); qp.lineTo(start)
                for seg in chain:
                    qp.qCurveTo(fitpoint(seg[2]), fitpoint(seg[-1]))
                qp.lineTo((end[0], bounds[3])); qp.closePath()
                return q
            exterior = lower_profile(outer_chain, 0)
            interior = lower_profile(inner_chain, t)
            bowl = diff(exterior, interior)
            if not bowl.area:
                raise ValueError('double-struck lowercase u: empty lower connection')
            rails = []
            for j, x in enumerate((xleft, left + doubled / 2 - t)):
                r = intersect(rect(x, bottom, x + t, bounds[3]), exterior)
                if not intersect(r, bowl).area:
                    raise ValueError(f'double-struck lowercase u: disconnected left rail {j}')
                rails.append(r)
            left_stem = union(*rails, rect(xleft, bounds[3] - t, left + doubled / 2, bounds[3]))
            right_stem = diff(rect(right - doubled / 2, 0, right + doubled / 2, bounds[3]),
                              rect(right - gap / 2, t, right + gap / 2, bounds[3] - t))
            if not intersect(bowl, right_stem).area:
                raise ValueError('double-struck lowercase u: disconnected right stem')
            result = union(bowl, left_stem, right_stem)
            if len(list(result.contours)) != 3:
                raise ValueError('double-struck lowercase u: expected two closed slots')
        elif base in ('h', 'm', 'n'):
            from fontTools.pens.basePen import BasePen

            class ShoulderPen(BasePen):
                def __init__(self):
                    super().__init__(None)
                    self.segments = []
                    self.point = None

                def _moveTo(self, point):
                    self.point = point

                def _lineTo(self, point):
                    self.segments.append(('L', self.point, point))
                    self.point = point

                def _qCurveToOne(self, control, point):
                    self.segments.append(('Q', self.point, control, point))
                    self.point = point

                def _curveToOne(self, a, b, point):
                    raise ValueError(f'double-struck lowercase {base}: expected quadratic shoulders')

                def _closePath(self):
                    pass

            pen = ShoulderPen()
            p.draw(pen)
            segments = pen.segments
            arches = []
            for i in range(1, len(segments) - 4):
                chain = segments[i:i + 4]
                before, after = segments[i - 1], segments[i + 4]
                if (before[0] != 'L' or after[0] != 'L'
                        or any(s[0] != 'Q' for s in chain)
                        or abs(before[1][1]) > 1 or abs(after[-1][1]) > 1):
                    continue
                # The counter arch connects two baseline-reaching inner edges.
                # Italic rounding can leave these edges about 1.3 units off vertical.
                if max(abs(s[1][0] - s[-1][0]) for s in (before, after)) > 2:
                    raise ValueError(f'double-struck lowercase {base}: nonvertical counter edge')
                if chain[0][1][0] > chain[-1][-1][0]:
                    chain = [('Q', s[-1], s[2], s[1]) for s in reversed(chain)]
                if any(s[1][0] > s[2][0] + 2 or s[2][0] > s[-1][0] + 2 for s in chain):
                    raise ValueError(f'double-struck lowercase {base}: nonmonotone shoulder')
                arches.append(chain)
            arches.sort(key=lambda chain: chain[0][1][0])
            if len(arches) != (2 if base == 'm' else 1):
                raise ValueError(f'double-struck lowercase {base}: unexpected counter arches')
            low = min(point[1] for chain in arches for point in (chain[0][1], chain[-1][-1]))
            rows = [sorted(c.hspans(p, low * f)) for f in (0.3, 0.5, 0.7)]
            count = len(arches) + 1
            if any(len(row) != count for row in rows):
                raise ValueError(f'double-struck lowercase {base}: ambiguous lower stems')
            centres = [median([mid(row[j]) for row in rows]) for j in range(count)]
            parts, receivers = [], []
            # Explicit fitted copies retain the actual counter's quadratic profile.
            # Each arch has its own endpoint heights; no global splice row is used.
            for j, chain in enumerate(arches):
                x0, x1 = chain[0][1][0], chain[-1][-1][0]
                y0 = min(chain[0][1][1], chain[-1][-1][1])
                yt = max(point[1] for s in chain for point in s[1:])
                # Each source shoulder has its own outer crown, including m's
                # two arches. Ascender lines are excluded from this measure.
                crown = max(point[1] for s in segments if s[0] == 'Q'
                            for point in s[1:] if x0 <= point[0] <= x1)
                left, right = centres[j], centres[j + 1]
                if right - left <= doubled + t or yt <= y0 or crown - t <= y0:
                    raise ValueError(f'double-struck lowercase {base} arch {j}: shoulder clearance exhausted')
                splice = y0 - t

                def profile(inset):
                    edge_left = left + doubled / 2 - t + inset
                    edge_right = right + doubled / 2 - inset
                    sx = (edge_right - edge_left) / (x1 - x0)
                    sy = (crown - inset - y0) / (yt - y0)
                    def fitpoint(point):
                        return (edge_left + sx * (point[0] - x0), y0 + sy * (point[1] - y0))
                    q = pathops.Path(); qp = q.getPen()
                    start = fitpoint(chain[0][1]); end = fitpoint(chain[-1][-1])
                    qp.moveTo((start[0], splice))
                    qp.lineTo(start)
                    for s in chain:
                        qp.qCurveTo(fitpoint(s[2]), fitpoint(s[-1]))
                    qp.lineTo((end[0], splice))
                    qp.closePath()
                    return q

                outside = profile(0)
                shoulder = diff(outside, profile(t))
                if not shoulder.area:
                    raise ValueError(f'double-struck lowercase {base} arch {j}: empty shoulder')
                parts.append(shoulder)
                # Continue the receiving stem only inside this shoulder's outer
                # silhouette. Both rails follow the curve across their full width;
                # a rectangular top cap would protrude beside the descending arch.
                silhouette = union(outside, rect(left, 0, right + doubled / 2, splice))
                rails = []
                for k, x in enumerate((right - doubled / 2, right + doubled / 2 - t)):
                    r = intersect(rect(x, 0, x + t, crown), silhouette)
                    if not intersect(r, shoulder).area:
                        raise ValueError(f'double-struck lowercase {base} arch {j}: disconnected receiving rail {k}')
                    rails.append(r)
                receiver = union(*rails, rect(right - doubled / 2, 0, right + doubled / 2, t))
                receivers.append(receiver)
            shoulders = tuple(parts)
            first = centres[0]
            first_top = bounds[3] if base == 'h' else c.XH
            first_band = diff(rect(first - doubled / 2, 0, first + doubled / 2, first_top),
                              rect(first - gap / 2, t, first + gap / 2, first_top - t))
            bands = [first_band] + receivers
            for j, shoulder in enumerate(shoulders):
                for k in (j, j + 1):
                    if not intersect(shoulder, bands[k]).area:
                        raise ValueError(f'double-struck lowercase {base} arch {j}: disconnected stem {k}')
            result = union(*parts, *bands)
        elif base in ('i', 'j', 'l'):
            cs = contours(p)
            stem_path = min(cs, key=lambda q: q.bounds[1])
            sb = stem_path.bounds
            rows = c.hspans(stem_path, (sb[1] + sb[3]) / 2)
            if len(rows) != 1:
                raise ValueError(f'double-struck lowercase {base}: ambiguous stem')
            xc = mid(rows[0])
            if base == 'j':
                # Follow the capital-J construction with j's own hook and dot.
                master_body = min(contours(_master(c)['path']('j')), key=lambda q: q.bounds[1])
                target = (sb[0] - (doubled - width(rows[0])) / 2, sb[1], sb[2], sb[3])
                def fit_body(q):
                    qb = q.bounds
                    sx = (target[2] - target[0]) / (qb[2] - qb[0])
                    sy = (target[3] - target[1]) / (qb[3] - qb[1])
                    return c.transformed(q, (sx, 0, 0, sy, target[0] - sx * qb[0], target[1] - sy * qb[1]))
                body = fit_body(master_body)
                straight_y = c.XH / 2
                spans = c.hspans(body, straight_y)
                if len(spans) != 1:
                    raise ValueError('double-struck lowercase j: ambiguous hairline stem')
                delta = (t - width(spans[0])) / 2
                if delta < 0:
                    body = eroded(body, -delta)
                elif delta > 0:
                    stroke = pathops.Path(body)
                    stroke.stroke(2 * delta, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
                    stroke.convertConicsToQuads(); stroke.simplify()
                    body = union(body, stroke)
                body = fit_body(body)
                xr = c.hspans(body, straight_y)[-1][1]
                rail_x = xr - doubled
                hook_spans = [v for v in c.vspans(body, rail_x + t / 2) if v[1] < 0]
                if not hook_spans:
                    raise ValueError('double-struck lowercase j: rail misses hook')
                hook = max(hook_spans, key=lambda v: v[1])
                j_rail = rect(rail_x, mid(hook), rail_x + t, sb[3])
                if not intersect(j_rail, body).area:
                    raise ValueError('double-struck lowercase j: rail has no hook overlap')
                result = union(body, j_rail, rect(rail_x, sb[3] - t, xr, sb[3]))
                slot_spans = c.hspans(result, straight_y)
                if len(slot_spans) != 2 or slot_spans[1][0] - slot_spans[0][1] <= 0:
                    raise ValueError('double-struck lowercase j: slot is not open')
            else:
                result = diff(rect(xc - doubled / 2, sb[1], xc + doubled / 2, sb[3]),
                              rect(xc - gap / 2, sb[1] + t, xc + gap / 2, sb[3] - t))
            if base in ('i', 'j'):
                if len(cs) != 2:
                    raise ValueError(f'double-struck lowercase {base}: expected stem and dot')
                dot = max(cs, key=lambda q: q.bounds[1]); db = dot.bounds
                dx, dy = (db[0] + db[2]) / 2, (db[1] + db[3]) / 2
                # Noto's dot/stem envelope ratio is 176/173. Grow the source dot
                # around its own centre so its opening follows the stem gap.
                diameter = max(db[2] - db[0], db[3] - db[1], doubled * 176 / 173)
                inside = diameter - 2 * t
                if inside < gap or dy - diameter / 2 <= sb[3] + t:
                    raise ValueError(f'double-struck lowercase {base}: dot clearance exhausted')
                def dot_profile(size):
                    sx, sy = size / (db[2] - db[0]), size / (db[3] - db[1])
                    return c.transformed(dot, (sx, 0, 0, sy, dx - sx * dx, dy - sy * dy))
                result = union(result, diff(dot_profile(diameter), dot_profile(inside)))
        elif base == 'c':
            # Fit the designer's lightest c, preserving its open terminals.
            q = _master(c)['path']('c'); qb = q.bounds
            sx, sy = (bounds[2] - bounds[0]) / (qb[2] - qb[0]), (bounds[3] - bounds[1]) / (qb[3] - qb[1])
            q = c.transformed(q, (sx, 0, 0, sy, bounds[0] - sx * qb[0], bounds[1] - sy * qb[1]))
            # Offset a filled contour to the measured lowercase hairline thickness.
            ym = (bounds[1] + bounds[3]) / 2
            spans = c.hspans(q, ym)
            if len(spans) != 1:
                raise ValueError('double-struck lowercase c: ambiguous left stroke')
            delta = (t - width(spans[0])) / 2
            if delta < 0:
                q = eroded(q, -delta)
            elif delta > 0:
                stroke = pathops.Path(q)
                stroke.stroke(2 * delta, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
                stroke.convertConicsToQuads(); stroke.simplify(); q = union(q, stroke)
            qb = q.bounds
            sx, sy = (bounds[2] - bounds[0]) / (qb[2] - qb[0]), (bounds[3] - bounds[1]) / (qb[3] - qb[1])
            outline = c.transformed(q, (sx, 0, 0, sy, bounds[0] - sx * qb[0], bounds[1] - sy * qb[1]))
            x = bounds[0] + depth - t
            if x + t >= bounds[2]:
                raise ValueError('double-struck lowercase c: rail exceeds ink width')
            result = union(outline, rail(outline, x, ym))
        else:
            cs = contours(p)
            if len(cs) != 2:
                raise ValueError(f'double-struck lowercase {base}: expected one counter')
            outer, counter = cs
            cb = counter.bounds; ym = (cb[1] + cb[3]) / 2
            parts = []; cuts = []
            if base == 'o':
                outline = ring(outer); parts = [outline]
                xl, xr = bounds[0] + depth - t, bounds[2] - depth
                if xr - (xl + t) <= t:
                    raise ValueError('double-struck lowercase o: insufficient centre clearance')
                parts.extend((rail(outline, xl, ym), rail(outline, xr, ym)))
            else:
                left = base in ('b', 'p')
                if base in ('b', 'd'):
                    sample_y = c.XH + 0.8 * (bounds[3] - c.XH)
                    y0, y1 = 0, bounds[3]
                else:
                    sample_y = bounds[1] * 0.7
                    y0, y1 = bounds[1], c.XH
                spans = c.hspans(p, sample_y)
                if len(spans) != 1:
                    raise ValueError(f'double-struck lowercase {base}: ambiguous straight stem')
                xc = mid(spans[0])
                # The remote half contains only the bowl, clear of the ascender
                # or descender. Read its actual vertical extrema before fitting
                # the source counter's smooth profile to a separate bowl.
                split = (cb[0] + cb[2]) / 2
                remote = c.clip(outer, (split, -3000, 3000, 3000) if left
                                else (-3000, -3000, split, 3000))
                if not remote.area:
                    raise ValueError(f'double-struck lowercase {base}: missing remote bowl')
                bowl_bottom, bowl_top = remote.bounds[1], remote.bounds[3]
                bowl_left, bowl_right = (xc, bounds[2]) if left else (bounds[0], xc)
                if bowl_right <= bowl_left or cb[2] <= cb[0] or cb[3] <= cb[1]:
                    raise ValueError(f'double-struck lowercase {base}: invalid bowl profile')
                # This prototype preserves the source counter's curve profile,
                # not the original outer bowl: its stem-side half is concealed
                # by the doubled band. No concave stem corner is eroded.
                sx = (bowl_right - bowl_left) / (cb[2] - cb[0])
                sy = (bowl_top - bowl_bottom) / (cb[3] - cb[1])
                bowl = c.transformed(counter, (sx, 0, 0, sy,
                                     bowl_left - sx * cb[0], bowl_bottom - sy * cb[1]))
                # A source counter has hole winding; the fitted bowl is now a
                # filled outer shape before erosion and needs outer winding.
                if bowl.clockwise != outer.clockwise:
                    bowl.reverse()
                # Define the opening explicitly: stroke erosion can leave a
                # filled middle for these fitted counter profiles.
                bb = bowl.bounds
                bw, bh = bb[2] - bb[0], bb[3] - bb[1]
                if min(bw, bh) <= 2 * t:
                    raise ValueError(f'double-struck lowercase {base}: no inset opening')
                ix, iy = (bw - 2 * t) / bw, (bh - 2 * t) / bh
                inner = c.transformed(bowl, (ix, 0, 0, iy,
                                      bb[0] + t - ix * bb[0], bb[1] + t - iy * bb[1]))
                outline = diff(bowl, inner)
                parts = [outline]
                band = rect(xc - doubled / 2, y0, xc + doubled / 2, y1)
                cut = rect(xc - gap / 2, y0 + t, xc + gap / 2, y1 - t)
                x = bounds[2] - depth if left else bounds[0] + depth - t
                clearance = x - (xc + doubled / 2) if left else (xc - doubled / 2) - (x + t)
                if clearance <= t:
                    raise ValueError(f'double-struck lowercase {base}: insufficient bowl clearance')
                if not intersect(band, outline).area:
                    raise ValueError(f'double-struck lowercase {base}: stem does not overlap bowl')
                parts.extend((band, rail(outline, x, ym))); cuts.append(cut)
            result = diff(union(*parts), union(*cuts)) if cuts else union(*parts)
        rb = result.bounds
        if abs(rb[1] - bounds[1]) > 0.1 or (base not in ('i', 'j') and abs(rb[3] - bounds[3]) > 0.1):
            raise ValueError(f'double-struck lowercase {base}: vertical bounds changed')
        result = c.mv(result, bounds[0] - rb[0])
        out[base] = (result, c.W(base) + (rb[2] - rb[0]) - (bounds[2] - bounds[0]))
    return out

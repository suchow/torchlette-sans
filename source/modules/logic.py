"""logic: turnstiles, modal operators, proof and editorial marks, APL heritage
glyphs, and the white trapezium (`LG1`-`LG3`, `CP4`, `CP5`).

Every glyph is constructed directly in TrueType quadratic outlines from
Torchlette Sans's own parametric stroke measures (`LIN_AXIS`, `BAR`, `SM`,
`EQ_D`, `EQ_T`, cap height `CH`, x-height `XH`, and stem widths), with fixed
contour counts, point counts, and on-curve/off-curve flag sequences across all
fourteen static styles so variable-font (`gvar`) interpolation stays exact:

- `LG1` turnstiles (`⊢` U+22A2, `⊣` U+22A3, `⊧` U+22A7, `⊨` U+22A8, `⊬` U+22AC,
  `⊭` U+22AD): built on the 600-unit operator cell centered vertically on
  `LIN_AXIS` (286.5), with horizontal stroke `BAR` and vertical stem `1.15 * BAR`
  matching `symbols.py` (`⊤` `uni22A4`, `=` `equal`). `⊨` spans `70..530` with
  `equal`'s bar separation; `⊧` pairs a slightly taller axis-centered stem with
  compact double bars (`125..475`) to distinguish model satisfaction from
  semantic entailment. `⊬` and `⊭` carry a flat-capped diagonal negation slash
  across the horizontal arm(s) with analytical line-line intersections so Heavy
  and Black weights keep wide-open counters.
- `LG2` modal operators (`◇` U+25C7, `◻` U+25FB, and unencoded `uni25A1.math.logic`
  for `□` U+25A1): hollow x-height-scale operators centered on `LIN_AXIS` and
  counter-sheared upright in italic styles (matching `ui.py`'s geometric shapes).
  `ui.py`'s cap-height `uni25A1` (`□`) is left untouched; `ss09` ("Modal necessity
  box") substitutes `uni25A1 -> uni25A1.math.logic` unconditionally, and a
  guarded `calt` lookup (`LOGIC_MODAL_CALT`) activates `uni25A1.math.logic`
  automatically beside turnstiles, modal operators, quantifiers, logical
  connectives, and parenthesized modal formulas while leaving standalone `□`,
  `a□b`, and UI checkboxes (`□ Item`) as `uni25A1`.
- `LG3` proof, caution, contradiction, and editorial marks:
  - `∎` (U+220E, Halmos tombstone): solid vertical rectangle (`0..670`) on the
    baseline, upright in italic.
  - `☡` (U+2621, Caution Sign / Bourbaki-Knuth dangerous bend): bare reverse-turn bend standing `0..CH`, with horizontal terminal legs,
    analytical quadratic turns, and the operator BAR stroke; counter-sheared
    upright in italic. No enclosing road-sign diamond is encoded in U+2621.
  - `↯` (U+21AF, downwards zigzag arrow): crisp reductio lightning arrow with
    strictly parallel 1:2 downward-left legs, horizontal middle step, and
    `symbols.py`'s open chevron head.
  - `⁎` (U+204E, low asterisk): Torchlette's own asterisk centred at `LIN_AXIS - XH/2 - 16`,
    retaining its drawing and advance while separating it from U+2217.
  - `‣` (U+2023, triangular bullet): compact right-pointing solid triangle on
    `LIN_AXIS`, upright in italic.
  - `⌑` (U+2311, square lozenge / Kissen): concave-sided pillow square on
    `LIN_AXIS`, upright in italic.
- `CP4` APL heritage glyphs (`⍳` U+2373, `⍴` U+2374, `⍉` U+2349, `⌽` U+233D):
  `⍳` at x-height with smooth bottom right hook; `⍴` from `p`'s descender to
  x-height overshoot with continuous loop arch; `⍉` and `⌽` on the axis-centered
  ring with projecting backslash (`120°`) and vertical stile (`90°`), built as
  three analytical `_implied_arc` contours (outer silhouette + two D-counters,
  28 points) scaling smoothly with `SV` across `300..900`.
- `CP5` flowchart shape (`⏢` U+23E2, white trapezium): right hollow trapezium
  centered on `LIN_AXIS` with mitered inner contour (`inset`), upright in italic.

Reference provenance (proportions measured for comparative scale only; no
outlines or control points copied):
- Knuth's `manfnt.mf` (`char 127`, "Dangerous bend sign", public domain / Knuth
  TeX distribution) for the signboard-and-reverse-turn topology of `☡`.
- Noto Sans Math v3.000 and Noto Sans Symbols 2 v2.008 (Copyright The Noto
  Project Authors, SIL Open Font License 1.1) and STIX Two Math (Copyright STI
  Pub Companies, SIL Open Font License 1.1) for comparative Unicode metrics of
  turnstiles, `⌑`, `⍳`, `⍴`, `⍉`, `⌽`, and `⏢`.

Feature tags added: `ss09` ("Modal necessity box"); contextual lookup added to
`calt` (`LOGIC_MODAL_CALT`).
Glyph names added: `uni22A2`, `uni22A3`, `uni22A7`, `uni22A8`, `uni22AC`,
`uni22AD`, `uni25C7`, `uni25FB`, `uni25A1.math.logic`, `uni220E`, `uni2621`,
`uni21AF`, `uni204E`, `uni2023`, `uni2311`, `uni2373`, `uni2374`, `uni2349`,
`uni233D`, `uni23E2`.
Code points outside the Makefile's current `UNICODES` web-subset list: `U+2621`
(`☡`).
"""
from array import array
import math

from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates


def _signed_area(pts):
    n = len(pts)
    return sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))


def _meet(a, b):
    """Intersection of two directed lines ((px, py), (ux, uy))."""
    (px, py), (ux, uy) = a
    (qx, qy), (vx, vy) = b
    den = ux * vy - uy * vx
    t = ((qx - px) * vy - (qy - py) * vx) / den
    return (px + t * ux, py + t * uy)


def _inset_poly(pts, d):
    """Offset a simple polygon inward by perpendicular distance d."""
    n = len(pts)
    if _signed_area([(x, y, True) for x, y in pts]) < 0:
        pts = pts[::-1]
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        lines.append(((x0 + d * nx, y0 + d * ny), (ux, uy)))
    return [_meet(lines[i - 1], lines[i]) for i in range(n)]


def _quad_arc(cx, cy, rx, ry, a0_deg, a1_deg, n_segs, include_start=True, include_end=True):
    """Exact-tangent quadratic Bezier approximation of an elliptical arc.
    Returns [(x, y, on_curve), ...] with fixed point count for fixed n_segs."""
    pts = []
    a0 = math.radians(a0_deg)
    da = math.radians(a1_deg - a0_deg) / n_segs
    sec = 1.0 / math.cos(da / 2.0)
    if include_start:
        pts.append((cx + rx * math.cos(a0), cy + ry * math.sin(a0), True))
    for k in range(n_segs):
        t0 = a0 + k * da
        t1 = t0 + da
        tm = 0.5 * (t0 + t1)
        pts.append((cx + rx * sec * math.cos(tm), cy + ry * sec * math.sin(tm), False))
        if k < n_segs - 1 or include_end:
            pts.append((cx + rx * math.cos(t1), cy + ry * math.sin(t1), True))
    return pts


def _implied_arc(cx, cy, r, a0_deg, a1_deg, n_segs):
    """Circular arc with TrueType implied on-curve midpoints between consecutive
    off-curve tangent controls: guarantees 0.0-degree tangent continuity across
    internal joins after integer rounding and italic shearing."""
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    da = (a1 - a0) / n_segs
    sec = 1.0 / math.cos(da / 2.0)
    pts = [(cx + r * math.cos(a0), cy + r * math.sin(a0), True)]
    for k in range(n_segs):
        tm = a0 + (k + 0.5) * da
        pts.append((cx + r * sec * math.cos(tm), cy + r * sec * math.sin(tm), False))
    pts.append((cx + r * math.cos(a1), cy + r * math.sin(a1), True))
    return pts


def _on_pts(coords):
    return [(x, y, True) for x, y in coords]


def _slash_x(y, xc, yc, slope_dx_dy):
    return xc + (y - yc) * slope_dx_dy


def _circled_bar(cx, cy, r_out, r_in, half_len, half_w, angle_deg):
    """Analytical 3-contour circled bar/backslash (1 outer CW + 2 inner CCW D-holes)
    using _implied_arc for 0.0-degree tangent continuity and constant 28-point
    topology across all weights and italics."""
    th = math.radians(angle_deg)
    ux, uy = math.cos(th), math.sin(th)          # bar axis (+u = upper/top-left end)
    nx, ny = -uy, ux                             # left normal to +u

    def to_world(u_coord, n_coord, on=True):
        return (cx + u_coord * ux + n_coord * nx, cy + u_coord * uy + n_coord * ny, on)

    phi_out = math.degrees(math.asin(half_w / r_out))
    u_out = math.sqrt(r_out * r_out - half_w * half_w)

    outer = [
        to_world(u_out, half_w),
        to_world(half_len, half_w),
        to_world(half_len, -half_w),
    ]
    arc_neg = _implied_arc(0.0, 0.0, r_out, -phi_out, -(180.0 - phi_out), 4)
    outer.extend(to_world(u_c, n_c, on) for u_c, n_c, on in arc_neg)
    outer.extend([
        to_world(-half_len, -half_w),
        to_world(-half_len, half_w),
    ])
    arc_pos = _implied_arc(0.0, 0.0, r_out, -(180.0 + phi_out), -(360.0 - phi_out), 4)
    outer.extend(to_world(u_c, n_c, on) for u_c, n_c, on in arc_pos[:-1])

    phi_in = math.degrees(math.asin(half_w / r_in))
    hole_neg_local = _implied_arc(0.0, 0.0, r_in, -phi_in, -(180.0 - phi_in), 4)
    hole_pos_local = _implied_arc(0.0, 0.0, r_in, phi_in, 180.0 - phi_in, 4)
    hole_neg = [to_world(u_c, n_c, on) for u_c, n_c, on in hole_neg_local]
    hole_pos = [to_world(u_c, n_c, on) for u_c, n_c, on in hole_pos_local]
    return [(outer, False), (hole_neg, True), (hole_pos, True)]


def glyphs(ctx):
    c = ctx
    font = c.font
    glyf, hmtx = font['glyf'], font['hmtx']
    order = set(font.getGlyphOrder())
    cmap = font.getBestCmap()
    made = ctx.made = []

    A = c.LIN_AXIS                       # 286.5
    BAR = c.BAR                          # 43 (Light), 53 (Regular), 84 (Bold), 110 (Black)
    VB = BAR * 1.15                      # operator vertical stem
    SM = c.SM
    EQ_D = c.EQ_D
    EQ_T = c.EQ_T
    K = c.ITALIC_K

    hp = c.path_of('H')
    CH = hp.bounds[3]                    # 705
    xp = c.path_of('x')
    XH = 470.0                           # canonical flat x-height zone
    XH_INK = xp.bounds[3]

    def put_tt(cp, contours, adv, name=None, upright_cy=None):
        name = name or f'uni{cp:04X}'
        assert name not in order, f'{name} already exists in glyph order'
        assert cp is None or cp not in cmap, f'U+{cp:04X} already mapped to {cmap.get(cp)}'

        all_xy = []
        all_flags = []
        ends = []
        for raw_pts, is_hole in contours:
            pts = list(raw_pts)
            if upright_cy is not None and K:
                pts = [(x + K * (upright_cy - y), y, on) for x, y, on in pts]
            pts = [(int(round(x)), int(round(y)), bool(on)) for x, y, on in pts]
            area = _signed_area(pts)
            # In TrueType (y-up), clockwise outer contours have negative signed area;
            # counter-clockwise inner hole contours have positive signed area.
            if (not is_hole and area > 0) or (is_hole and area < 0):
                pts = [pts[0]] + pts[1:][::-1]
            for x, y, on in pts:
                all_xy.append((x, y))
                all_flags.append(1 if on else 0)
            ends.append(len(all_xy) - 1)

        g = Glyph()
        g.numberOfContours = len(contours)
        g.coordinates = GlyphCoordinates(all_xy)
        g.flags = array('B', all_flags)
        g.endPtsOfContours = ends
        g.program = ttProgram.Program()
        g.recalcBounds(glyf)

        glyf[name] = g
        hmtx[name] = (int(round(adv)), getattr(g, 'xMin', 0))
        if name not in font.getGlyphOrder():
            font.setGlyphOrder(font.getGlyphOrder() + [name])
        order.add(name)
        c.GDEF_CLASS[name] = 1
        if cp is not None:
            ctx.map(cp, name)
        made.append(name)
        return name

    # =========================================================================
    # LG1 — Turnstiles: ⊢ (U+22A2), ⊣ (U+22A3), ⊧ (U+22A7), ⊨ (U+22A8),
    #                   ⊬ (U+22AC), ⊭ (U+22AD)
    # =========================================================================
    y_bot = 0.0
    y_top = 2.0 * A                      # 573: sits on baseline AND centers on LIN_AXIS
    x0, x1 = 70.0, 530.0

    # ⊢ U+22A2 RIGHT TACK (1 contour, 8 points)
    sx1 = x0 + VB
    bh0, bh1 = A - BAR / 2.0, A + BAR / 2.0
    right_tack = _on_pts([
        (x0, y_bot), (x0, y_top), (sx1, y_top), (sx1, bh1),
        (x1, bh1), (x1, bh0), (sx1, bh0), (sx1, y_bot),
    ])
    put_tt(0x22A2, [(right_tack, False)], 600)

    # ⊣ U+22A3 LEFT TACK (mirror of ⊢ about x = 300; 1 contour, 8 points)
    left_tack = [(600.0 - x, y, on) for x, y, on in right_tack]
    put_tt(0x22A3, [(left_tack, False)], 600)

    # ⊨ U+22A8 TRUE (full width 70..530, equal's bar spacing; 1 contour, 12 points)
    hi0, hi1 = A + EQ_D - EQ_T / 2.0, A + EQ_D + EQ_T / 2.0
    lo0, lo1 = A - EQ_D - EQ_T / 2.0, A - EQ_D + EQ_T / 2.0
    true_tack = _on_pts([
        (x0, y_bot), (x0, y_top), (sx1, y_top),
        (sx1, hi1), (x1, hi1), (x1, hi0), (sx1, hi0),
        (sx1, lo1), (x1, lo1), (x1, lo0), (sx1, lo0),
        (sx1, y_bot),
    ])
    put_tt(0x22A8, [(true_tack, False)], 600)

    # ⊧ U+22A7 MODELS (taller axis-centered stem -33..606, compact bars 125..475; 1 contour, 12 points)
    mx0, mx1 = 125.0, 475.0
    msx1 = mx0 + VB
    my_bot, my_top = A - 319.5, A + 319.5    # -33..606, centered on A = 286.5
    md = 0.86 * EQ_D
    mt = EQ_T * 0.94
    mhi0, mhi1 = A + md - mt / 2.0, A + md + mt / 2.0
    mlo0, mlo1 = A - md - mt / 2.0, A - md + mt / 2.0
    models_tack = _on_pts([
        (mx0, my_bot), (mx0, my_top), (msx1, my_top),
        (msx1, mhi1), (mx1, mhi1), (mx1, mhi0), (msx1, mhi0),
        (msx1, mlo1), (mx1, mlo1), (mx1, mlo0), (msx1, mlo0),
        (msx1, my_bot),
    ])
    put_tt(0x22A7, [(models_tack, False)], 600)

    # Negated turnstiles ⊬ (U+22AC) and ⊭ (U+22AD):
    # Flat-capped diagonal slash crossing the horizontal bar(s) cleanly to the right of the stem.
    nx1 = 555.0
    vb_neg = min(VB, 104.0)
    nsx1 = x0 + vb_neg
    nbh0, nbh1 = A - min(BAR, 94.0) / 2.0, A + min(BAR, 94.0) / 2.0
    eq_t_neg = min(EQ_T, 84.0)
    nhi0, nhi1 = A + EQ_D - eq_t_neg / 2.0, A + EQ_D + eq_t_neg / 2.0
    nlo0, nlo1 = A - EQ_D - eq_t_neg / 2.0, A - EQ_D + eq_t_neg / 2.0
    sw = min(BAR * 0.86, 80.0)           # perpendicular slash thickness
    slope = 212.0 / (y_top - y_bot)      # dx / dy (~0.370 => ~70 deg from horizontal)
    shw = 0.5 * sw * math.hypot(1.0, slope)   # horizontal half-width along a constant-y cut
    sxc = 342.0 + max(0.0, vb_neg - 61.0) * 0.25

    # ⊬ U+22AC DOES NOT PROVE (1 contour, 16 points)
    not_prove = _on_pts([
        (x0, y_bot), (x0, y_top), (nsx1, y_top),
        (nsx1, nbh1),
        (_slash_x(nbh1, sxc, A, slope) - shw, nbh1),
        (_slash_x(y_top, sxc, A, slope) - shw, y_top),
        (_slash_x(y_top, sxc, A, slope) + shw, y_top),
        (_slash_x(nbh1, sxc, A, slope) + shw, nbh1),
        (nx1, nbh1), (nx1, nbh0),
        (_slash_x(nbh0, sxc, A, slope) + shw, nbh0),
        (_slash_x(y_bot, sxc, A, slope) + shw, y_bot),
        (_slash_x(y_bot, sxc, A, slope) - shw, y_bot),
        (_slash_x(nbh0, sxc, A, slope) - shw, nbh0),
        (nsx1, nbh0),
        (nsx1, y_bot),
    ])
    put_tt(0x22AC, [(not_prove, False)], 600)

    # ⊭ U+22AD NOT TRUE (2 contours: 20-pt outer CW + 4-pt inner trapezoidal hole CCW = 24 points)
    not_true_outer = _on_pts([
        (x0, y_bot), (x0, y_top), (nsx1, y_top),
        (nsx1, nhi1),
        (_slash_x(nhi1, sxc, A, slope) - shw, nhi1),
        (_slash_x(y_top, sxc, A, slope) - shw, y_top),
        (_slash_x(y_top, sxc, A, slope) + shw, y_top),
        (_slash_x(nhi1, sxc, A, slope) + shw, nhi1),
        (nx1, nhi1), (nx1, nhi0),
        (_slash_x(nhi0, sxc, A, slope) + shw, nhi0),
        (_slash_x(nlo1, sxc, A, slope) + shw, nlo1),
        (nx1, nlo1), (nx1, nlo0),
        (_slash_x(nlo0, sxc, A, slope) + shw, nlo0),
        (_slash_x(y_bot, sxc, A, slope) + shw, y_bot),
        (_slash_x(y_bot, sxc, A, slope) - shw, y_bot),
        (_slash_x(nlo0, sxc, A, slope) - shw, nlo0),
        (nsx1, nlo0),
        (nsx1, y_bot),
    ])
    not_true_hole = _on_pts([
        (nsx1, nlo1),
        (_slash_x(nlo1, sxc, A, slope) - shw, nlo1),
        (_slash_x(nhi0, sxc, A, slope) - shw, nhi0),
        (nsx1, nhi0),
    ])
    put_tt(0x22AD, [(not_true_outer, False), (not_true_hole, True)], 600)

    # =========================================================================
    # LG2 — Modal Box & Diamond: ◻ (U+25FB), uni25A1.math.logic, ◇ (U+25C7)
    # =========================================================================
    t_modal = min(BAR, 98.0)
    box_s = XH                           # 470 x 470 modal necessity box
    bx0, bx1 = 65.0, 65.0 + box_s        # centered on 600-unit operator cell
    by0, by1 = A - box_s / 2.0, A + box_s / 2.0
    modal_outer = _on_pts([(bx0, by0), (bx0, by1), (bx1, by1), (bx1, by0)])
    modal_inner = _on_pts([
        (bx0 + t_modal, by0 + t_modal),
        (bx1 - t_modal, by0 + t_modal),
        (bx1 - t_modal, by1 - t_modal),
        (bx0 + t_modal, by1 - t_modal),
    ])
    put_tt(0x25FB, [(modal_outer, False), (modal_inner, True)], 600, upright_cy=A)
    put_tt(None, [(modal_outer, False), (modal_inner, True)], 600,
           name='uni25A1.math.logic', upright_cy=A)

    # ◇ U+25C7 WHITE DIAMOND (rotated hollow operator centered on LIN_AXIS; 2 contours, 8 points)
    r_dia = 275.0                        # optical balance against 470 square (side ~389)
    dcx = 325.0                          # lsb = rsb = 50, adv = 650
    r_dia_in = r_dia - (t_modal * 0.96) * math.sqrt(2.0)
    dia_outer = _on_pts([(dcx, A + r_dia), (dcx + r_dia, A), (dcx, A - r_dia), (dcx - r_dia, A)])
    dia_inner = _on_pts([(dcx, A + r_dia_in), (dcx - r_dia_in, A), (dcx, A - r_dia_in), (dcx + r_dia_in, A)])
    put_tt(0x25C7, [(dia_outer, False), (dia_inner, True)], 650, upright_cy=A)

    # =========================================================================
    # LG3 — End of Proof, Bourbaki/Knuth Dangerous Bend, Zigzag Arrow & Marks
    # =========================================================================
    # ∎ U+220E END OF PROOF (Halmos tombstone: solid vertical rectangle on baseline; 1 contour, 4 points)
    tomb_h = 670.0
    tomb_w = 436.0                       # ~0.65 * tomb_h
    tx0 = 62.0
    tomb = _on_pts([(tx0, 0.0), (tx0, tomb_h), (tx0 + tomb_w, tomb_h), (tx0 + tomb_w, 0.0)])
    put_tt(0x220E, [(tomb, False)], 560, upright_cy=tomb_h / 2.0)

    # ☡ U+2621 CAUTION SIGN / BOURBAKI-KNUTH DANGEROUS BEND
    # Bare caution bend 0..CH, using the existing analytical bend construction.
    # One CW bend contour; the separate enclosing diamond is deliberately absent.
    db_lsb = 55.0
    db_cx = db_lsb + CH / 2.0            # 407.5
    db_cy = CH / 2.0                     # 352.5
    db_adv = round(CH + 2.0 * db_lsb)    # 815

    def rounded_diamond(cx, cy, r_sharp, rc):
        # Vertices at top, right, bottom, left; each 90-deg vertex rounded by a tangent quadratic
        # whose off-curve control sits at the sharp vertex and on-curve tangencies sit at +-rc in x & y.
        return [
            (cx - rc, cy + r_sharp - rc, True), (cx, cy + r_sharp, False), (cx + rc, cy + r_sharp - rc, True),
            (cx + r_sharp - rc, cy + rc, True), (cx + r_sharp, cy, False), (cx + r_sharp - rc, cy - rc, True),
            (cx + rc, cy - r_sharp + rc, True), (cx, cy - r_sharp, False), (cx - rc, cy - r_sharp + rc, True),
            (cx - r_sharp + rc, cy - rc, True), (cx - r_sharp, cy, False), (cx - r_sharp + rc, cy + rc, True),
        ]

    rc_out = 40.0
    r_sharp_out = CH / 2.0 + rc_out / 2.0        # midpoint hits 0 and CH (705) exactly
    t_sign = min(max(36.0, BAR * 0.72), 56.0)
    r_sharp_in = r_sharp_out - t_sign * math.sqrt(2.0)
    rc_in = 18.0
    sign_outer = rounded_diamond(db_cx, db_cy, r_sharp_out, rc_out)
    sign_hole = rounded_diamond(db_cx, db_cy, r_sharp_in, rc_in)

    # Knuth S-bend highway stripe (matching manfnt.mf char 127 proportions:
    # ~20.5-deg middle reverse diagonal + long top-left and bottom-right highway legs)
    w_road = BAR
    ux_c = 150.0
    r_turn = 125.0
    uy_c = (CH - w_road) / 2.0 - r_turn
    hw_r = 0.5 * w_road
    d_half = math.hypot(ux_c, uy_c)
    phi_c = math.atan2(uy_c, ux_c)
    theta_mid = phi_c - math.asin(r_turn / d_half)       # ~20.46 deg (Knuth's atan2(3, 8) = 20.56 deg)
    a0_r = math.degrees(theta_mid) - 90.0                # ~-69.54 deg on C_R
    alpha_leg = 0.0                                      # crisp nearly-horizontal highway entry/exit bar
    a1_r = (180.0 - alpha_leg) - 90.0                    # +85.0 deg on C_R
    leg_len = 350.0                                      # extends to dx = -106.4, aligning over left bend
    u_leg = (math.cos(math.radians(180.0 - alpha_leg)), math.sin(math.radians(180.0 - alpha_leg)))
    n_leg = (math.cos(math.radians(a1_r)), math.sin(math.radians(a1_r)))   # right-hand normal (+0.19, +0.98)

    cr_x, cr_y = db_cx + ux_c, db_cy + uy_c
    cl_x, cl_y = db_cx - ux_c, db_cy - uy_c

    # Top centerline exit point from C_R(a1_r) along +u_leg, and its 180-deg symmetric bottom entry
    top_tan = (cr_x + r_turn * n_leg[0], cr_y + r_turn * n_leg[1])
    tip_top = (top_tan[0] + leg_len * u_leg[0], top_tan[1] + leg_len * u_leg[1])
    tip_bot = (2.0 * db_cx - tip_top[0], 2.0 * db_cy - tip_top[1])

    # Trace half 1: from Tip_bot (right-hand side of centerline) -> C_L inner arc (259 -> 102.03)
    # -> C_R outer arc (-77.97 -> +79.0) -> Tip_top (right-hand side of centerline).
    half1 = [(tip_bot[0] + hw_r * n_leg[0], tip_bot[1] + hw_r * n_leg[1], True)]
    half1.extend(_implied_arc(cl_x, cl_y, r_turn - hw_r, a1_r + 180.0, a0_r + 180.0, 2))
    half1.extend(_implied_arc(cr_x, cr_y, r_turn + hw_r, a0_r, a1_r, 3))
    half1.append((tip_top[0] + hw_r * n_leg[0], tip_top[1] + hw_r * n_leg[1], True))
    # Half 2 is the exact 180-degree rotation of half1 about (db_cx, db_cy)
    half2 = [(2.0 * db_cx - x, 2.0 * db_cy - y, on) for x, y, on in half1]
    sbend = half1 + half2

    put_tt(0x2621, [(sbend, False)], db_adv, upright_cy=db_cy)

    # ↯ U+21AF DOWNWARDS ZIGZAG ARROW (1 contour, 14 on-curve points)
    # Strictly parallel 1:2 downward-left legs (shared unit vector (ux2, uy2))
    # joined by a horizontal middle step, with smooth weight scaling across 300..900.
    ux2, uy2 = -1.0 / math.sqrt(5.0), -2.0 / math.sqrt(5.0)
    nx2, ny2 = -uy2, ux2                 # +n2 = pos side (right side of downward shaft)
    p0 = (320.0, 695.0)
    L_top = 352.0
    p1 = (p0[0] + L_top * ux2, p0[1] + L_top * uy2)
    L_mid = 240.0
    p2 = (p1[0] + L_mid, p1[1])
    L_bot = (-122.0 - p2[1]) / uy2
    p3 = (p2[0] + L_bot * ux2, p2[1] + L_bot * uy2)
    wz = 0.88 * BAR
    hw_z = 0.5 * wz

    def seg_lines(pa, pb, hw):
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        # n_pos = left normal (for downward vector, points +x = right side of glyph)
        nx, ny = -uy, ux
        return (((pa[0] + hw * nx, pa[1] + hw * ny), (ux, uy)),
                ((pa[0] - hw * nx, pa[1] - hw * ny), (ux, uy)))

    l0_pos, l0_neg = seg_lines(p0, p1, hw_z)
    l1_pos, l1_neg = seg_lines(p1, p2, hw_z)
    l2_pos, l2_neg = seg_lines(p2, p3, hw_z)

    top_line = ((0.0, p0[1]), (1.0, 0.0))
    z_top_pos = _meet(top_line, l0_pos)
    z_top_neg = _meet(top_line, l0_neg)
    z_k1_pos = _meet(l0_pos, l1_pos)
    z_k1_neg = _meet(l0_neg, l1_neg)
    z_k2_pos = _meet(l1_pos, l2_pos)
    z_k2_neg = _meet(l1_neg, l2_neg)

    # Chevron head at p3 along shared (ux2, uy2) direction (matching symbols.py head())
    hs = 0.88 + 0.08 * (SM - 1.0)
    sm_h = wz / 53.0
    hL, hH = 220.0 * hs, 176.5 * hs
    notch_x = -80.0 * sm_h
    back_x = -hL - 35.0 * sm_h
    back_y = hH - 38.0 * sm_h
    nose_y = 13.0 * sm_h
    tw = hw_z / back_y
    join_x = notch_x + tw * (back_x - notch_x)

    def h_pt(lx, ly):
        return (p3[0] + lx * ux2 + ly * nx2, p3[1] + lx * uy2 + ly * ny2)

    zig_raw = _on_pts([
        z_top_neg, z_top_pos,
        z_k1_pos, z_k2_pos,
        h_pt(join_x, hw_z),
        h_pt(back_x, back_y),
        h_pt(-hL, hH),
        h_pt(0.0, nose_y),
        h_pt(0.0, -nose_y),
        h_pt(-hL, -hH),
        h_pt(back_x, -back_y),
        h_pt(join_x, -hw_z),
        z_k2_neg, z_k1_neg,
    ])
    zx_min = min(x for x, _, _ in zig_raw)
    zx_max = max(x for x, _, _ in zig_raw)
    z_lsb = 55.0
    zig_pts = [(x + (z_lsb - zx_min), y, on) for x, y, on in zig_raw]
    put_tt(0x21AF, [(zig_pts, False)], (zx_max - zx_min) + 2.0 * z_lsb)

    # ⁎ U+204E LOW ASTERISK (Torchlette's own asterisk lowered to the baseline zone; shape retained)
    g_ast = glyf['asterisk']
    ast_coords, ast_ends, ast_flags = g_ast.getCoordinates(glyf)
    low_center = A - XH / 2.0 - 16.0   # low baseline-zone centre, distinct from the math-axis star
    dy_ast = (g_ast.yMin + g_ast.yMax) / 2.0 - low_center
    s0 = 0
    ast_contours = []
    for e in ast_ends:
        pts = [(ast_coords[i][0], ast_coords[i][1] - dy_ast, bool(ast_flags[i] & 1))
               for i in range(s0, e + 1)]
        s0 = e + 1
        ast_contours.append((pts, False))
    put_tt(0x204E, ast_contours, c.W('asterisk'))

    # ‣ U+2023 TRIANGULAR BULLET (compact right-pointing solid triangle on LIN_AXIS; 1 contour, 3 points)
    tb_h = 300.0
    tb_w = 264.0
    tb_x0 = 93.0
    tri_bullet = _on_pts([
        (tb_x0, A - tb_h / 2.0),
        (tb_x0, A + tb_h / 2.0),
        (tb_x0 + tb_w, A),
    ])
    put_tt(0x2023, [(tri_bullet, False)], 450, upright_cy=A)

    # ⌑ U+2311 SQUARE LOZENGE / KISSEN (concave-sided pillow square on LIN_AXIS; 2 contours, 16 points)
    k_cx = 280.0
    r_kout = 215.0
    d_kout = 146.0
    t_kissen = min(BAR * 0.85, 76.0)
    r_kin = r_kout - t_kissen * 1.32
    d_kin = d_kout - t_kissen * 1.05
    kissen_outer = [
        (k_cx - r_kout, A + r_kout, True), (k_cx, A + d_kout, False),
        (k_cx + r_kout, A + r_kout, True), (k_cx + d_kout, A, False),
        (k_cx + r_kout, A - r_kout, True), (k_cx, A - d_kout, False),
        (k_cx - r_kout, A - r_kout, True), (k_cx - d_kout, A, False),
    ]
    kissen_inner = [
        (k_cx - r_kin, A + r_kin, True), (k_cx, A + d_kin, False),
        (k_cx + r_kin, A + r_kin, True), (k_cx + d_kin, A, False),
        (k_cx + r_kin, A - r_kin, True), (k_cx, A - d_kin, False),
        (k_cx - r_kin, A - r_kin, True), (k_cx - d_kin, A, False),
    ]
    put_tt(0x2311, [(kissen_outer, False), (kissen_inner, True)], 560, upright_cy=A)

    # =========================================================================
    # CP4 — APL Heritage Glyphs: ⍳ (U+2373), ⍴ (U+2374), ⍉ (U+2349), ⌽ (U+233D)
    # =========================================================================
    i_spans = c.hspans(c.path_of('i'), 250)
    stem_lc = i_spans[0][1] - i_spans[0][0]
    s_iota = min(stem_lc, 142.0)
    s_iota_bot = min(BAR * 1.08, 108.0)

    # ⍳ U+2373 APL FUNCTIONAL SYMBOL IOTA (x-height stem with smooth bottom right hook; 1 contour, 13 points)
    ix0 = 74.0
    ix1 = ix0 + s_iota
    iy_top = round(XH_INK)
    iy_bot = -8.0
    r_in_iota = 54.0
    r_out_iota = r_in_iota + s_iota_bot
    ix_end = ix1 + r_in_iota + 42.0
    iota_pts = [
        (ix0, iy_top, True),
        (ix1, iy_top, True),
    ]
    # Inner 90-deg curve from (ix1, iy_bot + s_iota_bot + r_in_iota) to (ix1 + r_in_iota, iy_bot + s_iota_bot)
    iota_pts.extend(_quad_arc(ix1 + r_in_iota, iy_bot + s_iota_bot + r_in_iota,
                              r_in_iota, r_in_iota, 180.0, 270.0, 2,
                              include_start=True, include_end=True))
    iota_pts.extend([
        (ix_end, iy_bot + s_iota_bot, True),
        (ix_end, iy_bot, True),
    ])
    # Outer 90-deg curve from (ix0 + r_out_iota, iy_bot) to (ix0, iy_bot + r_out_iota)
    iota_pts.extend(_quad_arc(ix0 + r_out_iota, iy_bot + r_out_iota,
                              r_out_iota, r_out_iota, 270.0, 180.0, 2,
                              include_start=True, include_end=True))
    put_tt(0x2373, [(iota_pts, False)], round(ix_end + 52.0))

    # ⍴ U+2374 APL FUNCTIONAL SYMBOL RHO (descender stem arching smoothly over bowl; 2 contours, 30 points)
    p_path = c.path_of('p')
    y_desc = p_path.bounds[1]            # -236
    rx0 = 74.0
    sv_rho = min(stem_lc, 138.0)
    sh_rho = min(BAR * 1.06, 106.0)
    ry_top = round(XH_INK) + 9.0         # ~480..486 (bowl overshoot)
    ry_bot = 0.0                         # clean horizontal lower bar flush on baseline
    rcy = 0.5 * (ry_top + ry_bot)
    r_ry = 0.5 * (ry_top - ry_bot)       # ~240..243
    rx_max = rx0 + 486.0 + max(0.0, sv_rho - 66.0) * 0.45
    rcx = 0.5 * (rx0 + rx_max)
    r_rx = 0.5 * (rx_max - rx0)

    # Outer contour: straight left stem from y_desc up to (rx0, rcy), smooth 270-deg arch
    # (180 -> 90 -> 0 -> -90) to (rcx, 0), horizontal baseline join to (rx0 + sv_rho, 0), down stem.
    rho_outer = [(rx0, y_desc, True)]
    rho_outer.extend(_quad_arc(rcx, rcy, r_rx, r_ry, 180.0, 90.0, 2, include_start=True, include_end=False))
    rho_outer.extend(_quad_arc(rcx, rcy, r_rx, r_ry, 90.0, 0.0, 2, include_start=True, include_end=False))
    rho_outer.extend(_quad_arc(rcx, rcy, r_rx, r_ry, 0.0, -90.0, 2, include_start=True, include_end=True))
    rho_outer.extend([
        (rx0 + sv_rho, ry_bot, True),
        (rx0 + sv_rho, y_desc, True),
    ])

    # Matching D-arch counter with uniform loop thickness and crisp baseline/stem corner (14 points)
    in_x0 = rx0 + sv_rho
    in_x1 = rx_max - sv_rho * 0.96
    in_cx = 0.5 * (in_x0 + in_x1)
    in_rx = 0.5 * (in_x1 - in_x0)
    in_y0 = sh_rho
    in_y1 = ry_top - sh_rho
    in_cy = 0.5 * (in_y0 + in_y1)
    in_ry = 0.5 * (in_y1 - in_y0)
    rho_hole = [(in_x0, in_y0, True)]
    rho_hole.extend(_quad_arc(in_cx, in_cy, in_rx, in_ry, 180.0, 90.0, 2, include_start=True, include_end=False))
    rho_hole.extend(_quad_arc(in_cx, in_cy, in_rx, in_ry, 90.0, 0.0, 2, include_start=True, include_end=False))
    rho_hole.extend(_quad_arc(in_cx, in_cy, in_rx, in_ry, 0.0, -90.0, 2, include_start=True, include_end=True))
    put_tt(0x2374, [(rho_outer, False), (rho_hole, True)], round(rx_max + 56.0))

    # ⌽ U+233D APL CIRCLE STILE & ⍉ U+2349 APL CIRCLE BACKSLASH (3 contours, 28 points each)
    # Smooth affine SV progression across 300..900 matching ⍳, ⍴, O, and □ without clamps.
    apl_lsb = 75.0
    apl_rout = 245.0 + 22.0 * (c.SV - 1.0)
    t_ring = 56.0 + 59.0 * (c.SV - 1.0)
    apl_rin = apl_rout - t_ring
    hw_bar = 0.5 * (53.5 + 53.0 * (c.SV - 1.0))
    apl_cx = apl_lsb + apl_rout
    apl_adv = round(2.0 * apl_cx)

    put_tt(0x233D, _circled_bar(apl_cx, A, apl_rout, apl_rin, apl_rout + 98.0, hw_bar, 90.0), apl_adv)
    put_tt(0x2349, _circled_bar(apl_cx, A, apl_rout, apl_rin, apl_rout + 108.0, hw_bar, 120.0), apl_adv)

    # =========================================================================
    # CP5 — White Trapezium: ⏢ (U+23E2, White Trapezium)
    # =========================================================================
    trap_h = 540.0
    trap_w_bot = 760.0
    trap_w_top = 480.0
    trap_lsb = 55.0
    trap_cx = trap_lsb + trap_w_bot / 2.0        # 435, adv = 870
    ty0, ty1 = A - trap_h / 2.0, A + trap_h / 2.0
    trap_outer_xy = [
        (trap_cx - trap_w_bot / 2.0, ty0),
        (trap_lsb, ty1),
        (trap_lsb + trap_w_top, ty1),
        (trap_cx + trap_w_bot / 2.0, ty0),
    ]
    t_trap = min(BAR, 94.0)
    trap_inner_xy = _inset_poly(trap_outer_xy, t_trap)
    put_tt(0x23E2, [(_on_pts(trap_outer_xy), False), (_on_pts(trap_inner_xy), True)],
           round(trap_w_bot + 2.0 * trap_lsb), upright_cy=A)

    ctx.log(f'{len(made)} glyphs ({len(made) - 1} encoded + uni25A1.math.logic)')


def features(ctx):
    order = set(ctx.font.getGlyphOrder())
    if 'uni25A1' not in order or 'uni25A1.math.logic' not in order:
        ctx.log('uni25A1 absent (ui module off); skipping ss09/calt modal-box substitution')
        return

    # Stylistic Set ss09: explicit toggle for modal necessity box on U+25A1
    fea = [
        'lookup LOGIC_MODAL_BOX {',
        '  sub uni25A1 by uni25A1.math.logic;',
        '} LOGIC_MODAL_BOX;',
        'feature ss09 {',
        '  featureNames { name "Modal necessity box"; };',
        '  lookup LOGIC_MODAL_BOX;',
        '} ss09;',
    ]

    # Guarded contextual substitution in calt: converts U+25A1 to uni25A1.math.logic
    # automatically in unambiguous modal/logical operator contexts while leaving
    # standalone '□', 'a□b', and UI checkboxes ('□ Item') untouched.
    pre_candidates = [
        'uni22A2', 'uni22A3', 'uni22A7', 'uni22A8', 'uni22AC', 'uni22AD',
        'uni25C7', 'uni25FB', 'uni25A1.math.logic',
        'logicalnot', 'uni2200', 'uni2203', 'uni2204', 'uni2227', 'uni2228',
        'arrowright', 'arrowboth', 'arrowdblright', 'arrowdblboth',
        'uni27F6', 'uni27F7', 'uni27F9', 'uni27FA',
    ]
    post_candidates = [
        'uni25C7', 'uni25FB', 'uni25A1',
        'logicalnot', 'uni2200', 'uni2203', 'uni2204',
    ]
    prop_candidates = [
        *(chr(c) for c in range(ord('A'), ord('Z') + 1)),
        *(chr(c) for c in range(ord('a'), ord('z') + 1)),
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
        'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma',
        'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
        'Phi', 'Psi', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Omega',
    ]
    pre = [g for g in pre_candidates if g in order]
    post = [g for g in post_candidates if g in order]
    props = [g for g in prop_candidates if g in order]

    rules = []
    if pre:
        fea.append(f"@LOGIC_PRE = [{' '.join(pre)}];")
        rules.append('  sub @LOGIC_PRE uni25A1\' lookup LOGIC_MODAL_BOX;')
        if 'space' in order:
            rules.append('  sub @LOGIC_PRE space uni25A1\' lookup LOGIC_MODAL_BOX;')
    if post:
        fea.append(f"@LOGIC_POST = [{' '.join(post)}];")
        rules.append('  sub uni25A1\' lookup LOGIC_MODAL_BOX @LOGIC_POST;')
    if 'parenleft' in order and props:
        fea.append(f"@LOGIC_PROP = [{' '.join(props)}];")
        # □(p ...) and (□p ...), leaving UI '(□)' and '[□]' untouched
        rules.append('  sub uni25A1\' lookup LOGIC_MODAL_BOX parenleft [@LOGIC_PROP @LOGIC_PRE];'
                     if pre else '  sub uni25A1\' lookup LOGIC_MODAL_BOX parenleft @LOGIC_PROP;')
        rules.append('  sub parenleft uni25A1\' lookup LOGIC_MODAL_BOX [@LOGIC_PROP @LOGIC_POST parenleft];'
                     if post else '  sub parenleft uni25A1\' lookup LOGIC_MODAL_BOX [@LOGIC_PROP parenleft];')
        conn_candidates = [
            'uni22A2', 'uni22A3', 'uni22A7', 'uni22A8', 'uni22AC', 'uni22AD',
            'uni2227', 'uni2228', 'arrowright', 'arrowboth', 'arrowdblright', 'arrowdblboth',
            'uni27F6', 'uni27F7', 'uni27F9', 'uni27FA',
        ]
        conns = [g for g in conn_candidates if g in order]
        if conns:
            fea.append(f"@LOGIC_CONN = [{' '.join(conns)}];")
            rules.append('  sub uni25A1\' lookup LOGIC_MODAL_BOX @LOGIC_PROP @LOGIC_CONN;')
            if 'space' in order:
                rules.append('  sub uni25A1\' lookup LOGIC_MODAL_BOX @LOGIC_PROP space @LOGIC_CONN;')

    if rules:
        fea.extend([
            'lookup LOGIC_MODAL_CALT {',
            *rules,
            '} LOGIC_MODAL_CALT;',
            'feature calt {',
            '  lookup LOGIC_MODAL_CALT;',
            '} calt;',
        ])

    ctx.gsub('\n'.join(fea), after='alternates')
    ctx.log(f'ss09 ("Modal necessity box") + calt ({len(rules)} modal-context rules)')

"""math_table: OpenType MATH table, stretchy delimiters, radicals, display operators and math accents.

Builds a complete OpenType MATH table (version 1.0) for MathML Core rendering across all
14 upright and italic styles, overriding `radical` (for seamless vinculum overhang and
monoline valley matching its size variants) and, in post, lengthening the long arrows
⟵ ⟶ ⟷ ⟸ ⟹ ⟺ ⟼ by 450 units (TeX's are half again ⇒; they were 1000 beside a 700 ⇒), and
adding four standard horizontal math code points (U+0305 combining overline, U+203E
overline, U+23DE top curly bracket, U+23DF bottom curly bracket).

Every glyph but the tall radicals and display integrals stays inside -320..1120; the
radicals.size6..size20 (1545..4540) need meta.py's usWinAscent/Descent 2540/2060. Every assembly part stands on
y = 0 (as Latin Modern's and STIX's do).

glyphs    Encoded additions (uni0305, uni203E, uni23DE, uni23DF), monoline flat-cut `radical`
          override, and unencoded size variants and GlyphAssembly parts (all named *.math_table,
          with identical contour counts, point counts and starting-point order across all 14
          styles for variable-font interpolation):
          - Vertical delimiters: ( ) [ ] { } | ∣ ‖ ⌊ ⌋ ⌈ ⌉ ⟨ ⟩ / \\ (size0..size5, 965..1430),
            with side bearings that grow with the size, plus assemblies whose long connectors
            make every height above the largest variant. ( ) [ ] { } | ∣ ‖ ⌊ ⌋ ⌈ ⌉ ⟨ ⟩
            declare height / 0.85 (TeX's \\delimiterfactor rule). The grown braces are drawn
            (curled ends thinning to a terminal, a pointed cusp); the text brace is Mulish's.
          - Radicals: base `radical` (800) + radical.size0..size20 (938..4540), leaning further
            out as they grow (fully slanted, as TeX's), and radical.{bot,ext,top} past 4540:
            a 1115 check slanted to 900 under a vertical pole.
          - Display operators: summation.dsp, product.dsp, bigcup.dsp, bigcap.dsp (1430, the
            whole envelope, 0.67 as wide as tall, strokes 1.3-1.5 rule thicknesses), and the
            display integrals ∫ ∬ ∭ ∮ ∯ by assembly at DisplayOperatorMinHeight 2300 (TeX's
            2.2 em display integral): Mulish's hooks, enlarged, on a stem leaning toward its
            ends; ∮ ∯ with a ring part. ∬ ∭ ∮ ∯ ⋃ ⋂ are drawn by `mathglyphs`; their MATH
            entries are made only when it has made the base glyph.
          - Horizontal stretchy accents, rules, arrows and curly brackets:
            hat.size0..size6 (+ flat), tilde.size0..size6 (+ flat) (both with an inkless
            contour 90 under the ink, in post), full-bleed hbar.size0..size6
            (+ hbar.ext), and dense (4%) ladders of arrow{right,left,both} and of the drawn
            {overbrace,underbrace} (0.5 em deep, stroke 1.75 rules) with assemblies past them.
          Vertical stretchy variants, radicals and horizontal stretch operators are counter-sheared
          in italic styles so stacked assembly parts and radicals stand upright with zero step.

features  GSUB `dtls` (dotless i/j under math accents) and `flac` (flattened capital accents),
          all lookups prefixed with `MATH_TABLE_`.

post      Lengthens the long arrows, then populates `font['MATH']` (`MathConstants`,
          `MathGlyphInfo`, `MathVariants`) with all coverages strictly sorted by glyph ID,
          ^ ̂ grow through mathglyphs' hat.w1..w5 then hat.size3..size6,
          AccentBaseHeight = OS/2.sxHeight (470), FlattenedAccentBaseHeight = OS/2.sCapHeight - 1
          (704), script placement tuned to Torchlette's long ascenders and descenders
          (SuperscriptBaselineDropMax 340, SubscriptBaselineDropMin -45, SubscriptShiftDown 165),
          damped heavy-weight gaps, and identical canonical glyph/uint16 structure across all 14
          styles.
"""
import math
import os
from array import array
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.varLib.instancer import instantiateVariableFont

# radical: redrawn in glyphs; the long arrows (build.py's and symbols'): shafts lengthened in post
GLYPH_OVERRIDE = {'radical', 'uni27F5', 'uni27F6', 'uni27F7', 'uni27F8', 'uni27F9', 'uni27FA', 'uni27FC'}

_UPRIGHT_MULISH_CACHE = {}


def _upright_mulish_instance(here_dir, src_w):
    """Instantiate upright Mulish[wght].ttf at src_w so both Upright and Italic styles
    share identical 41-point brace and 28-point integral source topology across weights."""
    key = (here_dir, float(src_w))
    if key not in _UPRIGHT_MULISH_CACHE:
        vf_path = os.path.join(here_dir, 'mulish', 'Mulish[wght].ttf')
        _UPRIGHT_MULISH_CACHE[key] = instantiateVariableFont(TTFont(vf_path), {'wght': float(src_w)}, inplace=False)
    return _UPRIGHT_MULISH_CACHE[key]


# --- low-level interpolatable TrueType contour helpers ----------------------------

def _make_glyph(contours, glyf_table):
    """Build a simple TrueType Glyph directly from clockwise [(x, y, on_curve), ...]
    contours, preserving exact point count, flags and start-point order across all styles."""
    g = Glyph()
    g.numberOfContours = len(contours)
    pts, flags, ends = [], [], []
    k = -1
    for c in contours:
        for x, y, on in c:
            pts.append((float(x), float(y)))
            flags.append(1 if on else 0)
            k += 1
        ends.append(k)
    g.coordinates = GlyphCoordinates(pts)
    g.flags = array('B', flags)
    g.endPtsOfContours = ends
    from fontTools.ttLib.tables import ttProgram
    pr = ttProgram.Program()
    pr.fromBytecode(b'')
    g.program = pr
    g.recalcBounds(glyf_table)
    return g


def _counter_shear(contours, k, yc):
    if not k:
        return contours
    return [[(x - k * (y - yc), y, on) for x, y, on in c] for c in contours]


def _mirror_x(contours, cx):
    """Mirror clockwise contours across x = cx while keeping clockwise winding and c[0] on-curve."""
    out = []
    for c in contours:
        rev = [c[0]] + list(reversed(c[1:]))
        out.append([(2.0 * cx - x, y, on) for x, y, on in rev])
    return out


def _mirror_y(contours, cy):
    """Mirror clockwise contours across y = cy while keeping clockwise winding and c[0] on-curve."""
    out = []
    for c in contours:
        rev = [c[0]] + list(reversed(c[1:]))
        out.append([(x, 2.0 * cy - y, on) for x, y, on in rev])
    return out


def _rect_cw(x0, y0, x1, y1):
    return [(x0, y0, 1), (x0, y1, 1), (x1, y1, 1), (x1, y0, 1)]


def _eval_q(a, b, c, t):
    u = 1.0 - t
    return (u * u * a[0] + 2.0 * u * t * b[0] + t * t * c[0],
            u * u * a[1] + 2.0 * u * t * b[1] + t * t * c[1])


# --- Mulish cut-and-extend shapes (braces, horizontal braces, integrals) ----------

def _untwist_mulish_brace(coords, flags):
    """Resolve Mulish braceleft's tiny 4-unit inner-cusp self-crossing ([27..30]) analytically
    via exact de Casteljau subdivision, yielding 41 clean clockwise points across all weights."""
    assert len(coords) == 40, f'expected 40 raw Mulish braceleft points, got {len(coords)}'
    p26, p27, p28, p29, p30, p31 = [coords[i] for i in range(26, 32)]
    A0 = (0.5 * (p26[0] + p27[0]), 0.5 * (p26[1] + p27[1]))
    A1, A2 = p27, p28
    B0, B1 = p29, p30
    B2 = (0.5 * (p30[0] + p31[0]), 0.5 * (p30[1] + p31[1]))

    def x_at_y(P0, P1, P2, y_t):
        lo, hi = 0.0, 1.0
        asc = P0[1] < P2[1]
        for _ in range(44):
            mid = 0.5 * (lo + hi)
            if (_eval_q(P0, P1, P2, mid)[1] < y_t) == asc:
                lo = mid
            else:
                hi = mid
        t = 0.5 * (lo + hi)
        return _eval_q(P0, P1, P2, t)[0], t

    lo, hi = min(p28[1], p29[1]), max(p28[1], p29[1])
    for _ in range(44):
        ym = 0.5 * (lo + hi)
        if x_at_y(A0, A1, A2, ym)[0] < x_at_y(B0, B1, B2, ym)[0]:
            lo = ym
        else:
            hi = ym
    yc = 0.5 * (lo + hi)
    xa, ta = x_at_y(A0, A1, A2, yc)
    xb, tb = x_at_y(B0, B1, B2, yc)
    Ca = ((1.0 - ta) * A0[0] + ta * A1[0], (1.0 - ta) * A0[1] + ta * A1[1])
    Cb = ((1.0 - tb) * B1[0] + tb * B2[0], (1.0 - tb) * B1[1] + tb * B2[1])
    return (
        [(float(coords[i][0]), float(coords[i][1]), int(flags[i] & 1)) for i in range(27)]
        + [(A0[0], A0[1], 1), (Ca[0], Ca[1], 0), (0.5 * (xa + xb), yc, 1), (Cb[0], Cb[1], 0), (B2[0], B2[1], 1)]
        + [(float(coords[i][0]), float(coords[i][1]), int(flags[i] & 1)) for i in range(31, 40)]
    )


def _brace_cut_extend_cw(pts41, y0, y1, cusp_y_scale=1.0):
    """Cut-and-extend Mulish's 41-point untwisted `braceleft` along its two straight vertical
    stem runs ([3..4]/[34..35] and [13..14]/[23..24]) to span y0..y1."""
    y_bot_raw = pts41[0][1]
    y_top_raw = pts41[18][1]
    ym_raw = pts41[29][1]
    ym = 0.5 * (y0 + y1)
    dy_bot = y0 - y_bot_raw
    dy_top = y1 - y_top_raw
    out = []
    for i, (x, y, on) in enumerate(pts41):
        if i <= 3 or i >= 35:
            yn = y + dy_bot
        elif 14 <= i <= 23:
            yn = y + dy_top
        else:
            yn = ym + cusp_y_scale * (y - ym_raw)
        out.append((x, yn, on))
    return out


def _brace_asm_parts_from_mulish(pts41):
    """Cut Mulish's 41-point `braceleft` into 4 vertical assembly parts:
    bot (0..550, End=360), ext (0..500), mid (0..800, Start=220, End=220), top (0..550, Start=360)."""
    x0 = pts41[3][0]
    x1 = pts41[23][0]
    y_bot_raw = pts41[0][1]
    y_top_raw = pts41[18][1]
    ym_raw = pts41[29][1]

    dy_bot = 0.0 - y_bot_raw
    bot = (
        [(x, y + dy_bot, on) for x, y, on in pts41[0:4]]
        + [(x0, 550.0, 1), (x1, 550.0, 1)]
        + [(x, y + dy_bot, on) for x, y, on in pts41[35:41]]
    )

    dy_top = 550.0 - y_top_raw
    top = (
        [(x0, 0.0, 1)]
        + [(x, y + dy_top, on) for x, y, on in pts41[14:24]]
        + [(x1, 0.0, 1)]
    )

    cy_s = 1.16
    mid = (
        [(x0, 0.0, 1)]
        + [(x, 400.0 + cy_s * (y - ym_raw), on) for x, y, on in pts41[4:14]]
        + [(x0, 800.0, 1), (x1, 800.0, 1)]
        + [(x, 400.0 + cy_s * (y - ym_raw), on) for x, y, on in pts41[24:35]]
        + [(x1, 0.0, 1)]
    )

    ext = _rect_cw(x0, 0.0, x1, 500.0)
    return bot, ext, mid, top


def _rotate_brace_to_over_under(vert_cw, y0_vert, x_tip_raw, r_sc, y_over_bot=540.0, y_under_top=-18.0):
    """Map a clockwise vertical `braceleft` contour (spanning y0_vert..y0_vert+W) by a 90-deg
    clockwise rotation (det = +r_sc > 0, preserving clockwise winding) to a full-bleed 0..W
    horizontal `overbrace` contour, and reflect vertically to a clockwise `underbrace` contour."""
    over = [(y - y0_vert, y_over_bot + r_sc * (x_tip_raw - x), on) for x, y, on in vert_cw]
    rev = [over[0]] + list(reversed(over[1:]))
    under = [(X, y_under_top - (Y - y_over_bot), on) for X, Y, on in rev]
    return over, under


def _integral_sculpt_from_mulish(coords, flags, xc_out, bar, y0, y1, fh, fv):
    """Cut-and-extend Mulish's 28-point upright `integral`, softening heavy-weight stem thickness
    gracefully while sculpting wider curved hooks (fh) and taller hook arches (fv)."""
    assert len(coords) == 28, f'expected 28 Mulish integral points, got {len(coords)}'
    x0_raw = float(coords[10][0])
    x1_raw = float(coords[24][0])
    w_raw = x1_raw - x0_raw
    y_bot_raw = float(coords[0][1])
    y_top_raw = float(coords[14][1])

    # Smooth analytic stem softening: ~60.5u in Regular (vs 65.8u), ~136.7u in Black (vs 163.1u)
    w_new = 0.42 * w_raw + 0.62 * bar
    x0_new = xc_out - 0.5 * w_new
    x1_new = xc_out + 0.5 * w_new
    fh_eff = fh + 0.26 * ((w_raw - 65.8) / 97.3)

    def map_x(x):
        if x <= x0_raw:
            return x0_new + fh_eff * (x - x0_raw)
        if x >= x1_raw:
            return x1_new + fh_eff * (x - x1_raw)
        return x0_new + (x - x0_raw) * (w_new / w_raw)

    pts = [(float(coords[i][0]), float(coords[i][1]), int(flags[i] & 1)) for i in range(28)]
    full = []
    for i, (x, y, on) in enumerate(pts):
        xn = map_x(x)
        if i <= 10 or i >= 25:
            yn = y0 + fv * (y - y_bot_raw)
        else:
            yn = y1 - fv * (y_top_raw - y)
        full.append((xn, yn, on))

    # Assembly parts sharing the exact same sculpted Mulish hooks:
    # bot (0..620, End=340), ext (0..500, Start=500, End=500), top (0..620, Start=340)
    bot = (
        [(map_x(x), fv * (y - y_bot_raw), on) for x, y, on in pts[0:11]]
        + [(x0_new, 620.0, 1), (x1_new, 620.0, 1)]
        + [(map_x(x), fv * (y - y_bot_raw), on) for x, y, on in pts[25:28]]
    )
    top = (
        [(x0_new, 0.0, 1)]
        + [(map_x(x), 620.0 - fv * (y_top_raw - y), on) for x, y, on in pts[11:25]]
        + [(x1_new, 0.0, 1)]
    )
    ext = _rect_cw(x0_new, 0.0, x1_new, 500.0)
    return full, bot, ext, top


# --- parametric shapes ------------------------------------------------------------


def _integral_smooth_cw(xc, y0, y1, w_mid, w_end, slope=0.18, hook_r=None, sweep=200.0, n=72):
    """A display integral drawn whole, as TeX's is: one slanted stroke from a bottom hook
    curling left to a top hook curling right (point-symmetric about its middle), swelling to
    w_mid at the middle and tapering to w_end at the flat-cut terminals. Each side is a
    quadratic B-spline (consecutive off-curve points), so the outline has no corners but
    the four at the terminals and no straight connector anywhere."""
    H = y1 - y0
    ym = 0.5 * (y0 + y1)
    r = hook_r if hook_r is not None else 0.055 * H
    a = 2.0 * r                                   # vertical room above the stem for the hook
    dy = 0.5 * H - a
    dx = slope * dy
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln                      # stem direction, upward
    nx, ny = uy, -ux                               # its right normal
    # top half of the centre line: stem from the middle to P_t, then the hook arc
    pts = []
    m = 24
    for i in range(m + 1):
        t = i / m
        pts.append((xc + t * dx, ym + t * dy))
    cx, cy = xc + dx + r * nx, ym + dy + r * ny    # hook centre, right of the stem's top
    th0 = math.atan2(-ny, -nx)                     # angle of P_t seen from the centre
    k = 30
    for i in range(1, k + 1):
        th = th0 - math.radians(sweep) * i / k     # clockwise: over the top and down the right
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    bottom = [(2 * xc - x, 2 * ym - y) for x, y in reversed(pts[1:])]
    line = bottom + pts
    # arclength parameter
    L = [0.0]
    for (xa, ya), (xb, yb) in zip(line, line[1:]):
        L.append(L[-1] + math.hypot(xb - xa, yb - ya))
    tot = L[-1]
    N = len(line)
    right, left = [], []
    for i, (x, y) in enumerate(line):
        xa, ya = line[max(0, i - 1)]
        xb, yb = line[min(N - 1, i + 1)]
        tx, ty = xb - xa, yb - ya
        tl = math.hypot(tx, ty)
        tx, ty = tx / tl, ty / tl
        u = L[i] / tot
        w = w_end + (w_mid - w_end) * (1.0 - abs(2.0 * u - 1.0) ** 2.4)
        right.append((x + 0.5 * w * ty, y - 0.5 * w * tx))
        left.append((x - 0.5 * w * ty, y + 0.5 * w * tx))
    cw = ([(left[0][0], left[0][1], 1)] + [(x, y, 0) for x, y in left[1:-1]] + [(left[-1][0], left[-1][1], 1)]
          + [(right[-1][0], right[-1][1], 1)] + [(x, y, 0) for x, y in reversed(right[1:-1])]
          + [(right[0][0], right[0][1], 1)])
    area = sum(xa * yb - xb * ya for (xa, ya, _), (xb, yb, _) in zip(cw, cw[1:] + cw[:1]))
    if area > 0:                                   # make it clockwise
        cw = [cw[0]] + list(reversed(cw[1:]))
    return cw

def _paren_left_cw(x_out, w_mid, x_tip_L, w_tip, y0, y1):
    """Continuous full-height bowed left parenthesis matching Mulish's 16-point Bezier profile."""
    ym = 0.5 * (y0 + y1)
    hh = 0.5 * (y1 - y0)
    x_in = x_out + w_mid
    x_tip_R = x_tip_L + w_tip
    dx_o = x_tip_L - x_out
    dx_i = x_tip_R - x_in
    return [
        (x_tip_L, y0, 1),
        (x_out + 0.655 * dx_o, ym - 0.832 * hh, 0),
        (x_out + 0.207 * dx_o, ym - 0.508 * hh, 0),
        (x_out, ym - 0.178 * hh, 0),
        (x_out, ym, 1),
        (x_out, ym + 0.178 * hh, 0),
        (x_out + 0.207 * dx_o, ym + 0.508 * hh, 0),
        (x_out + 0.655 * dx_o, ym + 0.832 * hh, 0),
        (x_tip_L, y1, 1),
        (x_tip_R, y1, 1),
        (x_in + 0.510 * dx_i, ym + 0.748 * hh, 0),
        (x_in, ym + 0.251 * hh, 0),
        (x_in, ym, 1),
        (x_in, ym - 0.251 * hh, 0),
        (x_in + 0.510 * dx_i, ym - 0.748 * hh, 0),
        (x_tip_R, y0, 1),
    ]


def _paren_top_cw(x_out, w_mid, x_tip_L, w_tip, y_bot, y_join, y_top):
    """Upper cap of left parenthesis (y_join..y_top) continuing straight stem (y_bot..y_join)."""
    hh = y_top - y_join
    x_in = x_out + w_mid
    x_tip_R = x_tip_L + w_tip
    dx_o = x_tip_L - x_out
    dx_i = x_tip_R - x_in
    return [
        (x_out, y_bot, 1),
        (x_out, y_join, 1),
        (x_out, y_join + 0.178 * hh, 0),
        (x_out + 0.207 * dx_o, y_join + 0.508 * hh, 0),
        (x_out + 0.655 * dx_o, y_join + 0.832 * hh, 0),
        (x_tip_L, y_top, 1),
        (x_tip_R, y_top, 1),
        (x_in + 0.510 * dx_i, y_join + 0.748 * hh, 0),
        (x_in, y_join + 0.251 * hh, 0),
        (x_in, y_join, 1),
        (x_in, y_bot, 1),
    ]


def _bracket_left_cw(x0, x1, x_arm, y0, y1, arm_h):
    """Clockwise left square bracket [."""
    return [
        (x0, y0, 1),
        (x0, y1, 1),
        (x_arm, y1, 1),
        (x_arm, y1 - arm_h, 1),
        (x1, y1 - arm_h, 1),
        (x1, y0 + arm_h, 1),
        (x_arm, y0 + arm_h, 1),
        (x_arm, y0, 1),
    ]


def _lceil_cw(x0, x1, x_arm, y0, y1, arm_h):
    """Clockwise left ceiling (top arm only); also used for bracketleft.top."""
    return [
        (x0, y0, 1),
        (x0, y1, 1),
        (x_arm, y1, 1),
        (x_arm, y1 - arm_h, 1),
        (x1, y1 - arm_h, 1),
        (x1, y0, 1),
    ]


def _lfloor_cw(x0, x1, x_arm, y0, y1, arm_h):
    """Clockwise left floor (bottom arm only); also used for bracketleft.bot."""
    return [
        (x0, y0, 1),
        (x0, y1, 1),
        (x1, y1, 1),
        (x1, y0 + arm_h, 1),
        (x_arm, y0 + arm_h, 1),
        (x_arm, y0, 1),
    ]


def _langle_cw(x_apex, x_tip, y0, y1, stroke_w):
    """Clockwise left angle bracket ⟨ with flat horizontal ends and crisp apex."""
    ym = 0.5 * (y0 + y1)
    hh = 0.5 * (y1 - y0)
    dx = x_tip - x_apex
    hypot = math.hypot(dx, hh)
    wx = stroke_w * hypot / hh
    return [
        (x_tip, y0, 1),
        (x_apex, ym, 1),
        (x_tip, y1, 1),
        (x_tip + wx, y1, 1),
        (x_apex + wx, ym, 1),
        (x_tip + wx, y0, 1),
    ]


def _rad_top_x(H):
    """x of the upstroke's outer top corner for a surd H units tall: the base (800) and the
    938 variant keep their 2026-11-04 drawing; taller surds lean further out, as TeX's do,
    so a grown surd reads as a larger check rather than a steeper one."""
    x = 562.0 + 0.04 * (H - 938.0) + 0.16 * max(0.0, min(H, RAD_LEAN_H) - 938.0)
    return (x + RAD_TALL_LEAN * max(0.0, min(H, 3090.0) - RAD_LEAN_H)
            + RAD_TALL_LEAN2 * max(0.0, H - 3090.0))


# Past 1430 the surd leans 0.108 more per unit of height up to 3090 (180 more: an upstroke
# slope of 0.17 there, 0.25 at 1430), then 0.05 (252 more at 4540, slope 0.13). Chrome
# sizes every msqrt by the widest variant's advance (its intrinsic inline size cannot know
# the target height), so a surd that grew rightward would leave a gap after every radicand:
# the extra lean hangs left of the origin instead (the tick reaches -220 at 4540, inside
# the thick space after =) and no advance exceeds radical.size5's 702.
RAD_LEAN_H = 1430.0
RAD_TALL_LEAN = 180.0 / (3090.0 - 1430.0)
RAD_TALL_LEAN2 = 0.05
RAD_TALL_HANG = 1.0


def _radical_monoline_cw(y0, y1, r_th, overhang=38.0):
    """9-point clockwise monoline sans-serif radical surd from y0 to y1:
    - parallel-sided upstroke (1.05 R) and downstroke (0.96 R) matching Mulish / Noto Sans Math;
    - compact flat foot (0.98 R) with inner valley apex ~1.2 R above y0 even in Black;
    - flat horizontal top cut at y1 (no hanging elbow) with advance 38u inside x_top_R so
      Chrome's centre-on-top vinculum rule joins cleanly with zero white sliver and zero tooth."""
    H = y1 - y0
    w_up = max(46.0, 1.05 * r_th)
    w_down = max(42.0, 0.96 * r_th)
    w_foot = max(40.0, 0.98 * r_th)
    ledge_h = max(38.0, 0.94 * r_th)

    y_ledge = y0 + min(390.0, 0.41 * H)
    x_ledge_L = 32.0
    x_ledge_R = 146.0 + 0.32 * r_th
    x_foot_L = 305.0
    x_foot_R = x_foot_L + w_foot
    x_top_L = _rad_top_x(H)
    x_top_R = x_top_L + w_up
    adv = round(x_top_R - overhang)

    # Exact intersection of parallel inner edges:
    s_dn = (x_foot_L - (x_ledge_R - w_down)) / (y_ledge - y0)
    s_up = (x_top_R - x_foot_R) / H
    dy_val = (w_down + w_up - w_foot) / (s_dn + s_up)
    y_val_in = y0 + dy_val
    x_val_in = (x_foot_R - w_up) + s_up * dy_val
    x_ledge_in_bot = x_foot_L - s_dn * (y_ledge - ledge_h - y0)

    cw = [
        (x_ledge_L, y_ledge - ledge_h, 1),
        (x_ledge_L, y_ledge, 1),
        (x_ledge_R, y_ledge, 1),
        (x_val_in, y_val_in, 1),
        (x_top_L, y1, 1),
        (x_top_R, y1, 1),
        (x_foot_R, y0, 1),
        (x_foot_L, y0, 1),
        (x_ledge_in_bot, y_ledge - ledge_h, 1),
    ]
    return cw, adv


RAD_ASM_BOT = 1430.0   # the bottom part is the 1430 variant's full height, drawn at -315..1115 (Chrome
                       # places assembly parts by their ink, as it does Latin Modern's, which stand on y = 0)
RAD_ASM_JOIN = 1220.0  # where its slanted upstroke turns vertical (End connector 1430 - 1220 - 10)
RAD_ASM_EXT, RAD_ASM_TOP = 300.0, 260.0   # short pole parts: Chrome overlaps every joint equally, so with
                                          # the 200 connector these make every height from 1480 up


def _radical_asm_parts(r_th):
    """Three-part vertical GlyphAssembly for radicals taller than radical.size5 (1430):
    bot (1430, drawn at -315..1115: the 1430 variant's own check, its upstroke slanted to 1220
    and only then turning vertical, End=200), ext (300) and a flat-cut top (260, Start=220).
    A tall surd is TeX's shape: the largest check under a vertical pole, which used to be a
    small hook under a long pole. The pole stands upright, so the advance overhangs it by
    10 units only (the slanted variants' 38 would put it into the radicand)."""
    w_up = max(46.0, 1.05 * r_th)
    w_down = max(42.0, 0.96 * r_th)
    w_foot = max(40.0, 0.98 * r_th)
    ledge_h = max(38.0, 0.94 * r_th)

    # the stem stands where the 1430 variant's upstroke reaches y = RAD_ASM_JOIN
    x_foot_L = 305.0
    x_foot_R = x_foot_L + w_foot
    x_top_L_1430 = _rad_top_x(RAD_ASM_BOT)
    s_up0 = (x_top_L_1430 + w_up - x_foot_R) / RAD_ASM_BOT
    x_stem_R = x_foot_R + s_up0 * RAD_ASM_JOIN
    x_stem_L = x_stem_R - w_up
    adv = round(x_stem_R - 10.0)   # the pole is upright: a 38-unit overhang would put it into the radicand

    y_ledge = 390.0
    x_ledge_L = 32.0
    x_ledge_R = 146.0 + 0.32 * r_th

    s_dn = (x_foot_L - (x_ledge_R - w_down)) / y_ledge
    s_up = s_up0
    y_join_L = (x_stem_L - (x_foot_R - w_up)) / s_up
    dy_val = (w_down + w_up - w_foot) / (s_dn + s_up)
    y_val_in = dy_val
    x_val_in = (x_foot_R - w_up) + s_up * dy_val
    y_join_R = (x_stem_R - x_foot_R) / s_up
    x_ledge_in_bot = x_foot_L - s_dn * (y_ledge - ledge_h)

    bot = [
        (x_ledge_L, y_ledge - ledge_h, 1),
        (x_ledge_L, y_ledge, 1),
        (x_ledge_R, y_ledge, 1),
        (x_val_in, y_val_in, 1),
        (x_stem_L, y_join_L, 1),
        (x_stem_L, RAD_ASM_BOT, 1),
        (x_stem_R, RAD_ASM_BOT, 1),
        (x_stem_R, y_join_R, 1),
        (x_foot_R, 0.0, 1),
        (x_foot_L, 0.0, 1),
        (x_ledge_in_bot, y_ledge - ledge_h, 1),
    ]
    ext = _rect_cw(x_stem_L, 0.0, x_stem_R, RAD_ASM_EXT)
    top = _rect_cw(x_stem_L, 0.0, x_stem_R, RAD_ASM_TOP)
    bot = [(x, y - 315.0, on) for x, y, on in bot]
    return bot, ext, top, adv


DSP_Y0, DSP_Y1 = -315.0, 1115.0   # display ∑ ∏ ⋃: the whole vertical-metrics envelope (1430)


def _summation_dsp_cw(y0, y1, x_L, x_R, x_apex_L, diag_w, bar_h, bevel):
    """Display-size sans-serif summation ∑ in Torchlette Sans's 13-point geometry (top and
    bottom bars, two diagonals meeting at a short vertical apex). diag_w is the diagonals'
    horizontal thickness; the inner edge of the lower diagonal is the outer edge's exact
    parallel, so the stroke keeps one weight from corner to apex."""
    ym = 0.5 * (y0 + y1)
    x_apex_R = x_apex_L + diag_w
    y_ap = 0.30 * bar_h
    slope = (x_apex_L - x_L) / (ym - (y0 + bevel))
    x_in_L = x_L + diag_w + slope * (bar_h - bevel)
    cw = [
        (x_L, y0, 1),
        (x_L, y0 + bevel, 1),
        (x_apex_L, ym, 1),
        (x_L, y1 - bevel, 1),
        (x_L, y1, 1),
        (x_R, y1, 1),
        (x_R, y1 - bar_h, 1),
        (x_in_L, y1 - bar_h, 1),
        (x_apex_R, ym + y_ap, 1),
        (x_apex_R, ym - y_ap, 1),
        (x_in_L, y0 + bar_h, 1),
        (x_R, y0 + bar_h, 1),
        (x_R, y0, 1),
    ]
    return cw


def _product_dsp_cw(y0, y1, x_L, x_R, stem_w, bar_h):
    """Display-size sans-serif product ∏ in Torchlette Sans's 8-point geometry."""
    return [
        (x_L, y0, 1),
        (x_L, y1, 1),
        (x_R, y1, 1),
        (x_R, y0, 1),
        (x_R - stem_w, y0, 1),
        (x_R - stem_w, y1 - bar_h, 1),
        (x_L + stem_w, y1 - bar_h, 1),
        (x_L + stem_w, y0, 1),
    ]


def _bigcup_dsp_cw(y0, y1, x_L, x_R, stem_w, bowl_th):
    """Display-size n-ary union ⋃: two upright stems joined by a round bowl (quadratic
    quarter arcs); the bowl's bottom is bowl_th thick, its sides stem_w."""
    xc = 0.5 * (x_L + x_R)
    r_o = 0.5 * (x_R - x_L)
    yb = y0 + r_o                       # where the stems turn into the bowl
    xi_L, xi_R = x_L + stem_w, x_R - stem_w
    r_i = 0.5 * (xi_R - xi_L)
    k = 0.4142                          # tan(22.5 deg): two quadratics per quarter
    c = 0.7071
    yi_b = y0 + bowl_th                 # inner bowl bottom
    ry_i = yb - yi_b                    # inner bowl's vertical radius
    return [
        # outer: up the left stem from the bowl, across the top, down the right stem, round the bowl
        (x_L, yb, 1),
        (x_L, y1, 1),
        (xi_L, y1, 1),
        (xi_L, yb, 1),
        (xi_L, yb - k * ry_i, 0),
        (xc - c * r_i, yb - c * ry_i, 1),
        (xc - k * r_i, yi_b, 0),
        (xc, yi_b, 1),
        (xc + k * r_i, yi_b, 0),
        (xc + c * r_i, yb - c * ry_i, 1),
        (xi_R, yb - k * ry_i, 0),
        (xi_R, yb, 1),
        (xi_R, y1, 1),
        (x_R, y1, 1),
        (x_R, yb, 1),
        (x_R, yb - k * r_o, 0),
        (xc + c * r_o, yb - c * r_o, 1),
        (xc + k * r_o, y0, 0),
        (xc, y0, 1),
        (xc - k * r_o, y0, 0),
        (xc - c * r_o, yb - c * r_o, 1),
        (x_L, yb - k * r_o, 0),
    ]


def _brace_hook_cw(xs, w, wt, hdx, hh, y0, y_cut):
    """Bottom hook of a left curly brace: the stem (centre xs, thickness w) runs down from the
    flat cut y_cut and curls right into a horizontal terminal wt thick ending hdx right of xs."""
    return [
        (xs + hdx, y0, 1),
        (xs - 0.5 * w, y0, 0),
        (xs - 0.5 * w, y0 + hh, 1),
        (xs - 0.5 * w, y_cut, 1),
        (xs + 0.5 * w, y_cut, 1),
        (xs + 0.5 * w, y0 + hh, 1),
        (xs + 0.5 * w, y0 + wt, 0),
        (xs + hdx, y0 + wt, 1),
    ]


def _brace_cusp_cw(xs, w, cdx, ch, tip_w, ym, y_lo, y_hi):
    """Middle of a left curly brace: the stem from y_lo to y_hi bends left on both sides into
    a cusp pointing left at (xs - cdx, ym); tip_w is the cusp's horizontal depth."""
    xl, xr = xs - 0.5 * w, xs + 0.5 * w
    tip, tip_r = xs - cdx, xs - cdx + tip_w
    return [
        (xl, y_lo, 1),
        (xl, ym - ch, 1),
        (xl, ym - 0.35 * ch, 0),
        (tip, ym, 1),
        (xl, ym + 0.35 * ch, 0),
        (xl, ym + ch, 1),
        (xl, y_hi, 1),
        (xr, y_hi, 1),
        (xr, ym + ch, 1),
        (xr, ym + 0.20 * ch, 0),
        (tip_r, ym, 1),
        (xr, ym - 0.20 * ch, 0),
        (xr, ym - ch, 1),
        (xr, y_lo, 1),
    ]


def _brace_full_cw(xs, w, wt, hdx, hh, cdx, ch, tip_w, y0, y1):
    """A whole left curly brace from y0 to y1 as one contour: bottom hook, lower stem, cusp
    at the middle, upper stem, top hook (the hooks curl right, the cusp points left)."""
    ym = 0.5 * (y0 + y1)
    xl, xr = xs - 0.5 * w, xs + 0.5 * w
    tip, tip_r = xs - cdx, xs - cdx + tip_w
    return [
        (xs + hdx, y0, 1),
        (xl, y0, 0),
        (xl, y0 + hh, 1),
        (xl, ym - ch, 1),
        (xl, ym - 0.35 * ch, 0),
        (tip, ym, 1),
        (xl, ym + 0.35 * ch, 0),
        (xl, ym + ch, 1),
        (xl, y1 - hh, 1),
        (xl, y1, 0),
        (xs + hdx, y1, 1),
        (xs + hdx, y1 - wt, 1),
        (xr, y1 - wt, 0),
        (xr, y1 - hh, 1),
        (xr, ym + ch, 1),
        (xr, ym + 0.20 * ch, 0),
        (tip_r, ym, 1),
        (xr, ym - 0.20 * ch, 0),
        (xr, ym - ch, 1),
        (xr, y0 + hh, 1),
        (xr, y0 + wt, 0),
        (xs + hdx, y0 + wt, 1),
    ]


def _arc(cx, cy, rx, ry, t0, t1, n):
    """n quadratic arcs along the ellipse from parameter t0 to t1 (start point excluded)."""
    out = []
    for i in range(n):
        ta = t0 + (t1 - t0) * i / n
        tb = t0 + (t1 - t0) * (i + 1) / n
        h, tm = 0.5 * (tb - ta), 0.5 * (ta + tb)
        out.append((cx + rx * math.cos(tm) / math.cos(h), cy + ry * math.sin(tm) / math.cos(h), 0))
        out.append((cx + rx * math.cos(tb), cy + ry * math.sin(tb), 1))
    return out


def _stems_through_ring(stems, H, cx, cy, rx, ry, th):
    """Upright stems [(xl, xr), ...] from 0 to H crossed by an elliptical ring of thickness th,
    as already-merged, non-overlapping contours (one outline plus the ring's holes): the
    build's overlap removal would otherwise redraw the glyph with a point structure that
    differs between weights, which the variable font cannot interpolate."""
    rxi, ryi = rx - th, ry - th

    def t_of(x, r):
        return math.acos(max(-1.0, min(1.0, (x - cx) / r)))

    out = []
    (a1, b1), (a2, b2) = stems[0], stems[-1]
    tA1 = t_of(a1, rx)
    c = [(a1, 0.0, 1), (a1, cy - ry * math.sin(tA1), 1)]
    c += _arc(cx, cy, rx, ry, -tA1, tA1 - 2.0 * math.pi, 6)
    for k, (a, b) in enumerate(stems):
        if k > 0:
            c += _arc(cx, cy, rx, ry, t_of(stems[k - 1][1], rx), t_of(a, rx), 2)
        c += [(a, H, 1), (b, H, 1), (b, cy + ry * math.sin(t_of(b, rx)), 1)]
    tB2 = t_of(b2, rx)
    c += _arc(cx, cy, rx, ry, tB2, -tB2, 6)
    for k in range(len(stems) - 1, -1, -1):
        a, b = stems[k]
        c += [(b, 0.0, 1), (a, 0.0, 1)]
        if k > 0:
            c += [(a, cy - ry * math.sin(t_of(a, rx)), 1)]
            c += _arc(cx, cy, rx, ry, -t_of(a, rx), -t_of(stems[k - 1][1], rx), 2)
            c += [(stems[k - 1][1], cy - ry * math.sin(t_of(stems[k - 1][1], rx)), 1)][:0]
    # the last loop leaves the walk at the previous stem's right edge on the ring; drop
    # duplicate on-curve points (consecutive identical) and the closing repeat
    clean = []
    for pt in c:
        if clean and abs(clean[-1][0] - pt[0]) < 1e-6 and abs(clean[-1][1] - pt[1]) < 1e-6:
            continue
        clean.append(pt)
    if abs(clean[-1][0] - clean[0][0]) < 1e-6 and abs(clean[-1][1] - clean[0][1]) < 1e-6:
        clean.pop()
    out.append(clean)
    # holes (counter-clockwise): left of the first stem, right of the last, between stems
    tl = t_of(a1, rxi)
    out.append([(a1, cy + ryi * math.sin(tl), 1)] + _arc(cx, cy, rxi, ryi, tl, 2.0 * math.pi - tl, 4)[:-1]
               + [(a1, cy - ryi * math.sin(tl), 1)])
    tr = t_of(b2, rxi)
    out.append([(b2, cy - ryi * math.sin(tr), 1)] + _arc(cx, cy, rxi, ryi, -tr, tr, 4)[:-1]
               + [(b2, cy + ryi * math.sin(tr), 1)])
    for k in range(len(stems) - 1):
        bl, ar = stems[k][1], stems[k + 1][0]
        tb, ta = t_of(bl, rxi), t_of(ar, rxi)
        hole = [(bl, cy + ryi * math.sin(tb), 1), (bl, cy - ryi * math.sin(tb), 1)]
        hole += _arc(cx, cy, rxi, ryi, -tb, -ta, 2)
        hole += [(ar, cy + ryi * math.sin(ta), 1)]
        hole += _arc(cx, cy, rxi, ryi, ta, tb, 2)[:-1]
        out.append(hole)
    return out


def _ellipse_cw(cx, cy, rx, ry, ccw=False):
    """An ellipse of eight quadratic arcs (clockwise; counter-clockwise for a hole)."""
    k, c = 0.4142, 0.7071
    pts = [
        (cx - rx, cy, 1), (cx - rx, cy + k * ry, 0), (cx - c * rx, cy + c * ry, 1), (cx - k * rx, cy + ry, 0),
        (cx, cy + ry, 1), (cx + k * rx, cy + ry, 0), (cx + c * rx, cy + c * ry, 1), (cx + rx, cy + k * ry, 0),
        (cx + rx, cy, 1), (cx + rx, cy - k * ry, 0), (cx + c * rx, cy - c * ry, 1), (cx + k * rx, cy - ry, 0),
        (cx, cy - ry, 1), (cx - k * rx, cy - ry, 0), (cx - c * rx, cy - c * ry, 1), (cx - rx, cy - k * ry, 0),
    ]
    if ccw:
        pts = [pts[0]] + list(reversed(pts[1:]))
    return pts


def _integral_display_parts(coords, flags, xc, bar, fh, fv, lean, part_h, conn):
    """Display integral assembly parts cut from Mulish's 28-point `integral`: its hooks, larger
    by fh (across) and fv (up), on a stem that leans like TeX's: the bottom part's hook sits
    `lean` units left of the stem and the top part's `lean` units right, each joined to the
    vertical connector (the top `conn` units of the bottom part, the bottom `conn` of the top
    part) by a quadratic whose tangent meets the leaned hook's. Returns bot, ext, top."""
    full, bot0, ext, top0 = _integral_sculpt_from_mulish(coords, flags, xc, bar, -315.0, 1115.0, fh, fv)
    x0, x1 = ext[0][0], ext[2][0]
    yc_b = part_h - conn                     # bottom part: vertical from yc_b up to part_h
    # bot0 = hook pts[0..10] + (x0,620),(x1,620) + pts[25..27]
    hook_b = bot0[0:11]
    tail_b = bot0[13:]
    y10, y25 = hook_b[-1][1], tail_b[0][1]
    yl = min(y10, y25)
    s = 2.0 * lean / (yc_b - yl)             # tangent slope of the joining quadratic at the hook

    def lean_b(p):
        x, y, on = p
        return (x - lean - s * (yl - y) if y < yl else x - lean, y, on)

    bot = ([lean_b(p) for p in hook_b]
           + [(x0, 0.5 * (y10 + yc_b), 0), (x0, yc_b, 1), (x0, part_h, 1), (x1, part_h, 1), (x1, yc_b, 1),
              (x1, 0.5 * (y25 + yc_b), 0)]
           + [lean_b(p) for p in tail_b])
    # top0 = (x0,0) + pts[11..24] + (x1,0), hooks drawn from 0 up to 620
    dy = part_h - 620.0
    hook_t = [(x, y + dy, on) for x, y, on in top0[1:-1]]
    y11, y24 = hook_t[0][1], hook_t[-1][1]
    yh = max(y11, y24)
    yc_t = conn
    s_t = 2.0 * lean / (yh - yc_t)

    def lean_t(p):
        x, y, on = p
        return (x + lean + s_t * (y - yh) if y > yh else x + lean, y, on)

    top = ([(x0, 0.0, 1), (x0, yc_t, 1), (x0, 0.5 * (yc_t + y11), 0)]
           + [lean_t(p) for p in hook_t]
           + [(x1, 0.5 * (yc_t + y24), 0), (x1, yc_t, 1), (x1, 0.0, 1)])
    return bot, ext, top


def _hat_cw(adv, ink_w, y_bot, rise, th):
    """Clockwise math circumflex/wide-hat roof centered in adv."""
    xc = 0.5 * adv
    x0 = xc - 0.5 * ink_w
    x1 = xc + 0.5 * ink_w
    end_h = max(34.0, 0.84 * th)
    return [
        (x0, y_bot, 1),
        (x0, y_bot + end_h, 1),
        (xc, y_bot + rise + th, 1),
        (x1, y_bot + end_h, 1),
        (x1, y_bot, 1),
        (xc, y_bot + rise, 1),
    ]


def _tilde_cw(adv, ink_w, y_mid, amp, th):
    """Smooth G1-continuous clockwise S-wave tilde centered in adv."""
    x0 = 0.5 * (adv - ink_w)
    x1 = x0 + ink_w
    ht = 0.5 * th
    x_crest = x0 + 0.29 * ink_w
    x_trough = x0 + 0.71 * ink_w
    y_hi = y_mid + amp
    y_lo = y_mid - amp
    return [
        (x0, y_mid - 0.15 * amp - ht, 1),
        (x0, y_mid - 0.15 * amp + ht, 1),
        (x0 + 0.15 * ink_w, y_hi + ht, 0),
        (x_crest, y_hi + ht, 1),
        (x_crest + 0.14 * ink_w, y_hi + ht, 0),
        (x_trough - 0.14 * ink_w, y_lo + ht, 0),
        (x_trough, y_lo + ht, 1),
        (x1 - 0.15 * ink_w, y_lo + ht, 0),
        (x1, y_mid + 0.15 * amp + ht, 1),
        (x1, y_mid + 0.15 * amp - ht, 1),
        (x1 - 0.15 * ink_w, y_lo - ht, 0),
        (x_trough, y_lo - ht, 1),
        (x_trough - 0.14 * ink_w, y_lo - ht, 0),
        (x_crest + 0.14 * ink_w, y_hi - ht, 0),
        (x_crest, y_hi - ht, 1),
        (x0 + 0.15 * ink_w, y_hi - ht, 0),
    ]


def _arrow_rhead_cw(x_shaft_L, x_tip, ym, bar, sm):
    """Clockwise right arrow head + left shaft matching build.py's arrowright."""
    y0, y1 = ym - 0.5 * bar, ym + 0.5 * bar
    x_wing = x_tip - 220.0
    x_back = x_wing - 35.0 * sm
    x_notch = x_tip - 80.0 * sm
    wy_in = 176.5 - 38.0 * sm
    t = (0.5 * bar) / wy_in
    x_join = x_notch + t * (x_back - x_notch)
    return [
        (x_shaft_L, y0, 1),
        (x_shaft_L, y1, 1),
        (x_join, y1, 1),
        (x_back, ym + wy_in, 1),
        (x_wing, ym + 176.5, 1),
        (x_tip, ym + 13.0 * sm, 1),
        (x_tip, ym - 13.0 * sm, 1),
        (x_wing, ym - 176.5, 1),
        (x_back, ym - wy_in, 1),
        (x_join, y0, 1),
    ]


def _arrow_both_cw(x_L, x_R, ym, bar, sm):
    """16-point clockwise double-headed arrow matching build.py's arrowboth."""
    y0, y1 = ym - 0.5 * bar, ym + 0.5 * bar
    wy_in = 176.5 - 38.0 * sm
    t = (0.5 * bar) / wy_in
    r_wing = x_R - 220.0
    r_back = r_wing - 35.0 * sm
    r_notch = x_R - 80.0 * sm
    r_join = r_notch + t * (r_back - r_notch)
    l_wing = x_L + 220.0
    l_back = l_wing + 35.0 * sm
    l_notch = x_L + 80.0 * sm
    l_join = l_notch + t * (l_back - l_notch)
    return [
        (x_L, ym - 13.0 * sm, 1),
        (x_L, ym + 13.0 * sm, 1),
        (l_wing, ym + 176.5, 1),
        (l_back, ym + wy_in, 1),
        (l_join, y1, 1),
        (r_join, y1, 1),
        (r_back, ym + wy_in, 1),
        (r_wing, ym + 176.5, 1),
        (x_R, ym + 13.0 * sm, 1),
        (x_R, ym - 13.0 * sm, 1),
        (r_wing, ym - 176.5, 1),
        (r_back, ym - wy_in, 1),
        (r_join, y0, 1),
        (l_join, y0, 1),
        (l_back, ym - wy_in, 1),
        (l_wing, ym - 176.5, 1),
    ]


# --- Phase 1: glyphs --------------------------------------------------------------

# Six vertical discrete steps strictly > base (885..899) and strictly inside [-315, 1115]
VERT_SIZES = [
    (0, -205.0, 760.0),    # H = 965
    (1, -230.0, 830.0),    # H = 1060
    (2, -252.0, 903.0),    # H = 1155
    (3, -274.0, 976.0),    # H = 1250
    (4, -295.0, 1045.0),   # H = 1340
    (5, -315.0, 1115.0),   # H = 1430
]

ANG_SIZES = [
    (0, -180.0, 705.0),    # H = 885  (base uni27E8/27E9 is 705)
    (1, -215.0, 780.0),    # H = 995
    (2, -245.0, 860.0),    # H = 1105
    (3, -270.0, 945.0),    # H = 1215
    (4, -295.0, 1030.0),   # H = 1325
    (5, -315.0, 1115.0),   # H = 1430
]

SLASH_SIZES = [
    (0, -195.0, 735.0),    # H = 930  (base slash/backslash is 800)
    (1, -220.0, 810.0),    # H = 1030
    (2, -245.0, 885.0),    # H = 1130
    (3, -270.0, 960.0),    # H = 1230
    (4, -293.0, 1037.0),   # H = 1330
    (5, -315.0, 1115.0),   # H = 1430
]

# The encoded `radical` is the smallest surd MathML can use: Chrome and Firefox take the base
# glyph whenever it already covers the target (base ink height + gap + rule), never a smaller
# variant, and MathML Core hangs all of the surd's excess below the base (no TeX rule-11
# split). An x-height base needs 480 + 100 + 53 = 633, so a 938 base surd dropped its foot to
# -328 (below the g/p descenders at -243) and its tick onto the baseline. At 800 the foot of
# sqrt(n) sits at -167 (TeX's Computer Modern: about -190) and the tick ledge at +120..+161.
RAD_BASE = (-180.0, 620.0)  # H = 800
RAD_SIZES = [
    (0, -180.0, 758.0),    # H = 938 (the base radical before 2026-11-04)
    (1, -215.0, 820.0),    # H = 1035
    (2, -245.0, 890.0),    # H = 1135
    (3, -270.0, 965.0),    # H = 1235
    (4, -295.0, 1040.0),   # H = 1335
    (5, -315.0, 1115.0),   # H = 1430
]
# Tall surds stay slanted, as TeX's do (its largest is a 3 em check leaning 1 em), instead of a
# check under a vertical pole: 8% steps from 1430 to 4540 (lean: RAD_TALL_LEAN), centred near the
# math axis (a radical in a script-size fraction around a \dfrac, M068, needs 3900), which needs
# usWinAscent/Descent 2540/2060 (meta.py; USE_TYPO_METRICS keeps line spacing on typo/hhea).
# The pole assembly is left for anything taller.
RAD_TALL_H = (1545, 1670, 1800, 1945, 2100, 2270, 2450, 2645, 2860, 3090, 3335, 3600, 3890, 4200, 4540)
RAD_TALL_MID = 240.0
RAD_SIZES += [(6 + i, RAD_TALL_MID - h / 2.0, RAD_TALL_MID + h / 2.0) for i, h in enumerate(RAD_TALL_H)]

BRC_HOOK_PART = 560.0   # brace assembly end part: 260 of hook, 300 of straight stem
BRC_MID_PART = 1100.0   # brace assembly middle part: 520 of cusp, 290 of stem each side
BRC_CONN = 290.0        # long connectors: assemblies of every height from 1640 up

# display integrals (assembly only; the parts are shared by ∫ ∬ ∭ ∮ ∯)
INT_ADV = 860.0     # advance of one integral's parts, stem centred at INT_ADV / 2
INT_PART = 760.0    # bot / top part height
INT_CONN = 260.0    # their straight connector
INT_LEAN = 115.0    # hook offset from the stem, left at the bottom, right at the top
INT_FH, INT_FV = 1.55, 1.55
INT_MID = 900.0     # ∮'s middle part: ring INT_RING_RY tall each way about its middle (connectors 260)
INT_RING_RX, INT_RING_RY = 225.0, 190.0
INT_MID_CONN = 0.5 * INT_MID - INT_RING_RY
INT_SEP = 440.0

# horizontal curly brackets
HB_OVER_BOT, HB_UNDER_TOP = 560.0, -25.0
HB_CUSP = 230.0
HB_HOOK = 230.0
HB_END_PART = 460.0   # 230 of hook, 230 of straight rule (End / Start connector 200)
HB_MID_PART = 860.0   # 460 of cusp, 200 of rule each side     # stem spacing of ∬ ∭

ACCENT_GAP = 90         # the wide hats' and tildes' inkless contour sits this far under their ink
OVERLINE_GAP = 70       # and the overline bars'
DISPLAY_OP_MIN = 2300
INT_DSP2_IC = 205     # its italic correction, the assembly's (INT_LEAN + 90)
INT_SM_Y0 = 240.0 - 0.5 * DISPLAY_OP_MIN   # the whole display integrals, centred near the math axis   # TeX's display integral is 2.2 em at an x-height of 0.43 (2.4 em at Torchlette's 0.47); ∑ ∏ ⋃ ⋂ stop at their 1430 variant

HBAR_ADV = (440, 720, 1080, 1540, 2080, 2720, 3460)
# Horizontal stretchy glyphs grow by a dense ladder of size variants (4% steps), not by
# assembly: Chrome paints horizontal assemblies wrongly (the parts land short of the
# box and the arrowhead or the brace's ends go missing; Latin Modern shows the same), and it
# paints a size variant at the variant's own width, so coarse steps overshot the box.
OVERBRACE_ADV = tuple(round(720 * 1.04 ** k) for k in range(0, 63))       # 720 .. 8000
ARROW_ADV = tuple(round(700 * 1.04 ** k) for k in range(0, 56))           # 700 .. 6000
ARROWBOTH_ADV = tuple(round(880 * 1.04 ** k) for k in range(0, 50))       # 880 .. 5900


def glyphs(ctx):
    font, glyf, hmtx = ctx.font, ctx.glyf, ctx.hmtx
    k_it = ctx.ITALIC_K if ctx.ITALIC else 0.0
    yc_it = ctx.ITALIC_YC
    bar = float(ctx.BAR)
    axis = float(ctx.LIN_AXIS)
    sm, sv = float(ctx.SM), float(ctx.SV)
    r_th = float(round(bar))

    # Upright Mulish source at ctx.SRC_W for cut-and-extended braces & integrals
    up_mul = _upright_mulish_instance(ctx.HERE, ctx.SRC_W)
    up_glyf = up_mul['glyf']
    up_hmtx = up_mul['hmtx']

    gb_raw = up_glyf['braceleft']
    brc_pts41 = _untwist_mulish_brace(list(gb_raw.coordinates), list(gb_raw.flags))
    brc_adv0 = up_hmtx['braceleft'][0]
    brc_x0 = brc_pts41[3][0]
    brc_x1 = brc_pts41[23][0]
    brc_x_tip = brc_pts41[18][0]

    gi_raw = up_glyf['integral']
    int_coords = list(gi_raw.coordinates)
    int_flags = list(gi_raw.flags)

    # Measure weight-authentic stem & terminal metrics from upright-frame base glyphs
    p_par = ctx.path_of('parenleft')
    par_sp = ctx.hspans(p_par, 263)[0]
    par_x_out = par_sp[0]
    par_w_mid = par_sp[1] - par_sp[0]
    par_adv0 = ctx.W('parenleft')

    p_brk = ctx.path_of('bracketleft')
    brk_b = p_brk.bounds
    brk_sp = ctx.hspans(p_brk, 263)[0]
    brk_x0, brk_x1 = brk_sp[0], brk_sp[1]
    brk_x_arm = brk_b[2]
    brk_arm_h = ctx.vspans(p_brk, brk_x_arm - 5.0)[-1]
    brk_arm_th = brk_arm_h[1] - brk_arm_h[0]
    brk_adv0 = ctx.W('bracketleft')

    p_bar = ctx.path_of('bar')
    bar_b = p_bar.bounds
    bar_x0, bar_x1 = bar_b[0], bar_b[2]
    bar_w = bar_x1 - bar_x0
    bar_adv = ctx.W('bar')

    div_x0 = 130.0
    div_adv = round(260.0 + bar_w)
    dbl_x0 = 96.0
    dbl_gap = 72.0
    dbl_adv = round(192.0 + 2.0 * bar_w + dbl_gap)

    p_sl = ctx.path_of('slash')
    sl_sp = ctx.hspans(p_sl, 287)[0]
    sl_wx = sl_sp[1] - sl_sp[0]

    p_sum = ctx.path_of('summation')
    sum_diag_w = ctx.hspans(p_sum, 263)[0][1] - ctx.hspans(p_sum, 263)[0][0]
    sum_bar_h = max(44.0, bar * 1.12)

    p_prd = ctx.path_of('product')
    prd_sp = ctx.hspans(p_prd, 287)[0]
    prd_stem_w = prd_sp[1] - prd_sp[0]

    p_int = ctx.path_of('integral')
    int_sp = ctx.hspans(p_int, 287)[0]
    int_xc = 0.5 * (int_sp[0] + int_sp[1])

    added = []
    order = list(font.getGlyphOrder())
    order_set = set(order)
    cmap_before = font.getBestCmap()

    def emit(base_name, contours, adv, upright=True):
        name = f'{base_name}.math_table'
        assert name not in order_set, f'duplicate math_table glyph {name}'
        cs = _counter_shear(contours, k_it, yc_it) if upright else contours
        g = _make_glyph(cs, glyf)
        glyf[name] = g
        hmtx[name] = (int(round(adv)), getattr(g, 'xMin', 0))
        order.append(name)
        order_set.add(name)
        ctx.GDEF_CLASS[name] = 1
        added.append(name)
        return name

    def emit_encoded(name, cp, contours, adv, gdef_cls=1, upright=True):
        assert name not in order_set, f'duplicate encoded glyph {name}'
        assert cp not in cmap_before, f'U+{cp:04X} already mapped to {cmap_before[cp]}'
        cs = _counter_shear(contours, k_it, yc_it) if upright else contours
        g = _make_glyph(cs, glyf)
        glyf[name] = g
        hmtx[name] = (int(round(adv)), getattr(g, 'xMin', 0))
        order.append(name)
        order_set.add(name)
        ctx.GDEF_CLASS[name] = gdef_cls
        return (cp, name)

    # 0. Override base `radical` (RAD_BASE, H = 800) with monoline flat-cut + 38u overhang
    rad0_cw, rad0_adv = _radical_monoline_cw(*RAD_BASE, r_th)
    rad0_cs = _counter_shear([rad0_cw], k_it, yc_it)
    g_rad0 = _make_glyph(rad0_cs, glyf)
    glyf['radical'] = g_rad0
    hmtx['radical'] = (int(round(rad0_adv)), getattr(g_rad0, 'xMin', 0))

    # Side bearings of the grown delimiters. The text ( [ { keep Mulish's spacing, but a size
    # variant would otherwise keep their 29-unit (paren) and 7-unit (bracket) inner bearing
    # and touch the operand; TeX's (Latin Modern's) grown fences keep 57..120 inside and
    # 100..280 outside. pad_o is added outside and pad_i inside, both growing with the size.
    def pad_o(idx):
        return 8.0 + 6.0 * idx

    def pad_i(idx):
        return 14.0 + 6.0 * idx

    # 1. Parentheses ( ) — continuous Mulish-profile bow on .size0..size5, plus deep
    # 800-unit curved caps on .bot/.top so assembled parens (> 1430) stay gracefully bowed.
    par_dx_sizes = (142.0, 168.0, 194.0, 218.0, 242.0, 266.0)
    for idx, y0, y1 in VERT_SIZES:
        s = (y1 - y0) / 885.0
        dx_o = par_dx_sizes[idx] + 10.0 * (sv - 1.0)
        w_mid_k = par_w_mid * (1.0 + 0.05 * (s - 1.0))
        w_tip_k = max(44.0, 0.80 * w_mid_k)
        adv_k = par_adv0 + round(par_dx_sizes[idx] - 116.0) + round(pad_o(idx) + pad_i(idx))
        cw_l = _paren_left_cw(par_x_out + pad_o(idx), w_mid_k, par_x_out + pad_o(idx) + dx_o, w_tip_k, y0, y1)
        emit(f'parenleft.size{idx}', [cw_l], adv_k)
        emit(f'parenright.size{idx}', _mirror_x([cw_l], 0.5 * adv_k), adv_k)

    par_dx_asm = 278.0 + 12.0 * (sv - 1.0)
    par_w_mid_asm = par_w_mid * 1.06
    par_w_tip_asm = max(44.0, 0.78 * par_w_mid_asm)
    par_pad_o, par_pad_i = pad_o(6), pad_i(6)
    par_adv_asm = par_adv0 + 162 + round(par_pad_o + par_pad_i)
    par_xo_asm = par_x_out + par_pad_o
    # caps 1000 tall: 600 of curve on 400 of straight stem, so the assembly's connectors
    # (380) let it make every height from 1620 up, just past the largest variant
    par_top_cw = _paren_top_cw(par_xo_asm, par_w_mid_asm, par_xo_asm + par_dx_asm, par_w_tip_asm, 0.0, 400.0, 1000.0)
    par_bot_cw = _mirror_y([par_top_cw], 500.0)[0]
    par_ext_cw = _rect_cw(par_xo_asm, 0.0, par_xo_asm + par_w_mid_asm, 500.0)
    emit('parenleft.bot', [par_bot_cw], par_adv_asm)
    emit('parenleft.ext', [par_ext_cw], par_adv_asm)
    emit('parenleft.top', [par_top_cw], par_adv_asm)
    emit('parenright.bot', _mirror_x([par_bot_cw], 0.5 * par_adv_asm), par_adv_asm)
    emit('parenright.ext', _mirror_x([par_ext_cw], 0.5 * par_adv_asm), par_adv_asm)
    emit('parenright.top', _mirror_x([par_top_cw], 0.5 * par_adv_asm), par_adv_asm)

    # 2. Square brackets [ ] and Floor / Ceiling ⌊ ⌋ ⌈ ⌉
    for idx, y0, y1 in VERT_SIZES:
        s = (y1 - y0) / 885.0
        arm_dx = round(18.0 * (s - 1.0))
        po, pi = round(pad_o(idx) * 0.6), round(pad_i(idx) + 10.0)
        adv_k = brk_adv0 + arm_dx + po + pi
        x_arm_k = brk_x_arm + arm_dx + po
        bl_cw = _bracket_left_cw(brk_x0 + po, brk_x1 + po, x_arm_k, y0, y1, brk_arm_th)
        lc_cw = _lceil_cw(brk_x0 + po, brk_x1 + po, x_arm_k, y0, y1, brk_arm_th)
        lf_cw = _lfloor_cw(brk_x0 + po, brk_x1 + po, x_arm_k, y0, y1, brk_arm_th)
        emit(f'bracketleft.size{idx}', [bl_cw], adv_k)
        emit(f'bracketright.size{idx}', _mirror_x([bl_cw], 0.5 * adv_k), adv_k)
        emit(f'lceil.size{idx}', [lc_cw], adv_k)
        emit(f'rceil.size{idx}', _mirror_x([lc_cw], 0.5 * adv_k), adv_k)
        emit(f'lfloor.size{idx}', [lf_cw], adv_k)
        emit(f'rfloor.size{idx}', _mirror_x([lf_cw], 0.5 * adv_k), adv_k)

    bpo, bpi = round(pad_o(6) * 0.6), round(pad_i(6) + 10.0)
    brk_adv_asm = brk_adv0 + 10 + bpo + bpi
    brk_top_cw = _lceil_cw(brk_x0 + bpo, brk_x1 + bpo, brk_x_arm + 10.0 + bpo, 0.0, 600.0, brk_arm_th)
    brk_bot_cw = _lfloor_cw(brk_x0 + bpo, brk_x1 + bpo, brk_x_arm + 10.0 + bpo, 0.0, 600.0, brk_arm_th)
    brk_ext_cw = _rect_cw(brk_x0 + bpo, 0.0, brk_x1 + bpo, 500.0)
    emit('bracketleft.bot', [brk_bot_cw], brk_adv_asm)
    emit('bracketleft.ext', [brk_ext_cw], brk_adv_asm)
    emit('bracketleft.top', [brk_top_cw], brk_adv_asm)
    emit('bracketright.bot', _mirror_x([brk_bot_cw], 0.5 * brk_adv_asm), brk_adv_asm)
    emit('bracketright.ext', _mirror_x([brk_ext_cw], 0.5 * brk_adv_asm), brk_adv_asm)
    emit('bracketright.top', _mirror_x([brk_top_cw], 0.5 * brk_adv_asm), brk_adv_asm)

    # 3. Curly braces { }: drawn, not cut from Mulish. Mulish's text brace has small hooks and
    # a small cusp; cut and extended to 1.4 em and beyond (cases, \left\{) it read as a
    # square bracket with a nub. The grown braces are TeX's shape in Torchlette's stroke: the
    # ends curl over a quarter of the height (capped), the stem thins to a horizontal
    # terminal, and the middle bends into a pointed cusp. Stem and cusp depth come from
    # Mulish's brace so size0 continues the text brace.
    brc_w = brc_x1 - brc_x0
    brc_xs = 0.5 * (brc_x0 + brc_x1)
    brc_hdx = brc_x_tip - brc_xs
    brc_cdx = brc_xs - min(p[0] for p in brc_pts41)
    brc_wt = max(30.0, 0.62 * brc_w)
    brc_tipw = 1.25 * brc_w

    def brace_cw(y0, y1, extra=0.0):
        H = y1 - y0
        hh = min(300.0, 0.20 * H)
        ch = min(330.0, 0.22 * H)
        hdx = brc_hdx + extra
        cdx = brc_cdx + extra
        return _brace_full_cw(brc_xs + extra, brc_w, brc_wt, hdx, hh, cdx, ch, brc_tipw, y0, y1)

    for idx, y0, y1 in VERT_SIZES:
        ex = 6.0 * idx
        adv_b = brc_adv0 + round(2 * ex + pad_o(idx) * 0.5 + pad_i(idx) * 0.5)
        cw_b = [(x + pad_o(idx) * 0.5, y, on) for x, y, on in brace_cw(y0, y1, ex)]
        emit(f'braceleft.size{idx}', [cw_b], adv_b)
        emit(f'braceright.size{idx}', _mirror_x([cw_b], 0.5 * adv_b), adv_b)

    # assembly: bot (hook + stem, 0..BRC_HOOK_PART, End = BRC_CONN), ext (0..500),
    # mid (cusp, 0..BRC_MID_PART, Start = End = BRC_CONN), top (mirror of bot)
    ex6 = 6.0 * 6
    bxs = brc_xs + ex6 + pad_o(6) * 0.5
    adv_ba = brc_adv0 + round(2 * ex6 + pad_o(6) * 0.5 + pad_i(6) * 0.5)
    b_bot = _brace_hook_cw(bxs, brc_w, brc_wt, brc_hdx + ex6, 260.0, 0.0, BRC_HOOK_PART)
    b_top = _mirror_y([b_bot], 0.5 * BRC_HOOK_PART)[0]
    b_mid = _brace_cusp_cw(bxs, brc_w, brc_cdx + ex6, 260.0, brc_tipw, 0.5 * BRC_MID_PART, 0.0, BRC_MID_PART)
    b_ext = _rect_cw(bxs - 0.5 * brc_w, 0.0, bxs + 0.5 * brc_w, 500.0)
    emit('braceleft.bot', [b_bot], adv_ba)
    emit('braceleft.ext', [b_ext], adv_ba)
    emit('braceleft.mid', [b_mid], adv_ba)
    emit('braceleft.top', [b_top], adv_ba)
    emit('braceright.bot', _mirror_x([b_bot], 0.5 * adv_ba), adv_ba)
    emit('braceright.ext', _mirror_x([b_ext], 0.5 * adv_ba), adv_ba)
    emit('braceright.mid', _mirror_x([b_mid], 0.5 * adv_ba), adv_ba)
    emit('braceright.top', _mirror_x([b_top], 0.5 * adv_ba), adv_ba)

    # 4. Vertical bars: | (bar), ∣ (divides), ‖ (dblbar)
    for idx, y0, y1 in VERT_SIZES:
        emit(f'bar.size{idx}', [_rect_cw(bar_x0, y0, bar_x1, y1)], bar_adv)
        emit(f'divides.size{idx}', [_rect_cw(div_x0, y0, div_x0 + bar_w, y1)], div_adv)
        emit(f'dblbar.size{idx}', [
            _rect_cw(dbl_x0, y0, dbl_x0 + bar_w, y1),
            _rect_cw(dbl_x0 + bar_w + dbl_gap, y0, dbl_x0 + 2.0 * bar_w + dbl_gap, y1),
        ], dbl_adv)

    emit('bar.bot', [_rect_cw(bar_x0, 0.0, bar_x1, 600.0)], bar_adv)
    emit('bar.ext', [_rect_cw(bar_x0, 0.0, bar_x1, 600.0)], bar_adv)
    emit('divides.bot', [_rect_cw(div_x0, 0.0, div_x0 + bar_w, 600.0)], div_adv)
    emit('divides.ext', [_rect_cw(div_x0, 0.0, div_x0 + bar_w, 600.0)], div_adv)
    dbl_part = [
        _rect_cw(dbl_x0, 0.0, dbl_x0 + bar_w, 600.0),
        _rect_cw(dbl_x0 + bar_w + dbl_gap, 0.0, dbl_x0 + 2.0 * bar_w + dbl_gap, 600.0),
    ]
    emit('dblbar.bot', dbl_part, dbl_adv)
    emit('dblbar.ext', dbl_part, dbl_adv)

    # 4b. Chrome sets a vertical glyph assembly in a box as wide as the mo's widest variant
    # and centres the assembly's ink width in it, but draws each part from its own origin:
    # a part's left sidebearing shifts the ink off centre by that much (the round-3 parts,
    # lsb 79..341, put \left( \frac{p}{q} \right) against the ( and away from the )). So
    # every assembly's parts start their union ink at x = 0; the advances stay, and the
    # gaps on both sides of an assembled fence come out equal.
    for fam in (('parenleft', 'bot', 'ext', 'top'), ('parenright', 'bot', 'ext', 'top'),
                ('bracketleft', 'bot', 'ext', 'top'), ('bracketright', 'bot', 'ext', 'top'),
                ('braceleft', 'bot', 'ext', 'mid', 'top'), ('braceright', 'bot', 'ext', 'mid', 'top'),
                ('bar', 'bot', 'ext'), ('divides', 'bot', 'ext'), ('dblbar', 'bot', 'ext')):
        names = [f'{fam[0]}.{p}.math_table' for p in fam[1:]]
        for n in names:
            glyf[n].recalcBounds(glyf)
        m = min(glyf[n].xMin for n in names)
        for n in names:
            gp = glyf[n]
            gp.coordinates.translate((-m, 0))
            gp.recalcBounds(glyf)
            hmtx[n] = (hmtx[n][0], gp.xMin)

    # 5. Angle brackets ⟨ ⟩ and Slashes / \
    ang_w = max(44.0, bar * 1.05)
    for idx, y0, y1 in ANG_SIZES:
        H = y1 - y0
        span = 185.0 + 0.14 * (H - 885.0)
        x_ap = 64.0
        cw_la = _langle_cw(x_ap, x_ap + span, y0, y1, ang_w)
        adv_la = round(max(p[0] for p in cw_la) + 56.0)
        emit(f'langle.size{idx}', [cw_la], adv_la)
        emit(f'rangle.size{idx}', _mirror_x([cw_la], 0.5 * adv_la), adv_la)

    for idx, y0, y1 in SLASH_SIZES:
        H = y1 - y0
        sl_span = 260.0 + 0.24 * (H - 800.0)
        sl_cw = [
            (28.0, y0, 1),
            (28.0 + sl_span, y1, 1),
            (28.0 + sl_span + sl_wx, y1, 1),
            (28.0 + sl_wx, y0, 1),
        ]
        adv_sl = round(28.0 + sl_span + sl_wx + 28.0)
        emit(f'slash.size{idx}', [sl_cw], adv_sl)
        emit(f'backslash.size{idx}', _mirror_x([sl_cw], 0.5 * adv_sl), adv_sl)

    # 6. Radicals √ (size0..size5 + 3-part assembly; base `radical` at 800 comes first)
    for idx, y0, y1 in RAD_SIZES:
        # the vinculum overlaps the flat top by 14 (38 on the base surd): a grown surd's top
        # stands beside the radicand's tallest glyphs (the 1 of 1 - v^2/c^2) and must clear them
        rcw, radv = _radical_monoline_cw(y0, y1, r_th, overhang=14.0)
        hang = round(RAD_TALL_HANG * (_rad_top_x(y1 - y0) - _rad_top_x(RAD_LEAN_H)))
        if hang > 0:
            rcw = [(x - hang, y, on) for x, y, on in rcw]
            radv -= hang
        emit(f'radical.size{idx}', [rcw], radv)

    r_bot, r_ext, r_top, r_adv_asm = _radical_asm_parts(r_th)
    emit('radical.bot', [r_bot], r_adv_asm)
    emit('radical.ext', [r_ext], r_adv_asm)
    emit('radical.top', [r_top], r_adv_asm)

    # 7. Display operators. TeX's display ∑ and ∏ are 1.4 em and about as wide as tall, with
    # strokes heavier than the text forms; Torchlette's are the whole 1430-unit vertical
    # envelope (usWinAscent/Descent bound every glyph), 0.67 as wide as tall, with strokes
    # 1.3-1.5 rule thicknesses. ∫ ∬ ∭ ∮ ∯ grow past the envelope by assembly (DisplayOperator-
    # MinHeight 2000, as TeX's 2.2 em display integral): Mulish's hooks, enlarged, on a stem
    # that leans like TeX's toward its ends.
    dsp_h = DSP_Y1 - DSP_Y0
    sum_t = 1.38 * bar
    sum_xL, sum_xR = 60.0, 1020.0
    sum_xap = sum_xL + 0.54 * (sum_xR - sum_xL)
    sum_bar = 1.32 * bar
    sum_bevel = 0.9 * sum_bar
    sum_slope = (sum_xap - sum_xL) / (0.5 * dsp_h - sum_bevel)
    sum_dw = sum_t * math.sqrt(1.0 + sum_slope * sum_slope)
    emit('summation.dsp', [_summation_dsp_cw(DSP_Y0, DSP_Y1, sum_xL, sum_xR, sum_xap, sum_dw, sum_bar, sum_bevel)], 1080)

    emit('product.dsp', [_product_dsp_cw(DSP_Y0, DSP_Y1, 60.0, 1040.0, 1.48 * bar, 1.30 * bar)], 1100)

    cup_cw = _bigcup_dsp_cw(DSP_Y0, DSP_Y1, 70.0, 950.0, 1.36 * bar, 1.30 * bar)
    emit('bigcup.dsp', [cup_cw], 1020)
    emit('bigcap.dsp', _mirror_y([cup_cw], 0.5 * (DSP_Y0 + DSP_Y1)), 1020)

    int_s1, _, _, _ = _integral_sculpt_from_mulish(
        int_coords, int_flags, int_xc + 24.0, bar, -250.0, 915.0, fh=1.18, fv=1.12
    )
    int_dsp, _, _, _ = _integral_sculpt_from_mulish(
        int_coords, int_flags, int_xc + 44.0, bar, -315.0, 1115.0, fh=1.34, fv=1.24
    )
    emit('integral.size1', [int_s1], 650)
    emit('integral.dsp', [int_dsp], 710)
    int_bot, int_ext, int_top = _integral_display_parts(
        int_coords, int_flags, INT_ADV / 2.0, bar, INT_FH, INT_FV, INT_LEAN, INT_PART, INT_CONN)
    emit('integral.bot', [int_bot], INT_ADV)
    emit('integral.ext', [int_ext], INT_ADV)
    emit('integral.top', [int_top], INT_ADV)
    # Display integrals drawn whole at DisplayOperatorMinHeight (2300), smooth and swelling as
    # TeX's are, so a display ∫ ∬ ∭ never shows the assembly's straight connector; the
    # assembly is left for taller stretches and for ∮ ∯ (their ring cannot cross a curve
    # without overlaps the build would redraw differently per weight).
    w_int = 0.42 * (float(int_coords[24][0]) - float(int_coords[10][0])) + 0.62 * bar
    int_sm = _integral_smooth_cw(INT_ADV / 2.0, INT_SM_Y0, INT_SM_Y0 + DISPLAY_OP_MIN, 1.30 * w_int, 0.80 * w_int)
    emit('integral.dsp2', [int_sm], INT_ADV)
    for n_st, nm in ((2, 'dblint'), (3, 'tplint')):
        emit(f'{nm}.dsp2', [[(x + i * INT_SEP, y, on) for x, y, on in int_sm] for i in range(n_st)],
             INT_ADV + (n_st - 1) * INT_SEP)

    # ∮'s middle: the stem through a ring; the ring is as heavy as the stem's thinner rule
    x0e, x1e = int_ext[0][0], int_ext[2][0]
    xce = 0.5 * (x0e + x1e)
    ring_th = 0.95 * bar
    emit('integral.mid', _stems_through_ring([(x0e, x1e)], INT_MID, xce, 0.5 * INT_MID,
                                             INT_RING_RX, INT_RING_RY, ring_th), INT_ADV)
    # ∬ ∭ ∯: the same parts side by side, INT_SEP apart (∯'s ring spans both stems)
    for n_st, nm in ((2, 'dblint'), (3, 'tplint')):
        adv_n = INT_ADV + (n_st - 1) * INT_SEP
        for part, cs in (('bot', int_bot), ('ext', int_ext), ('top', int_top)):
            emit(f'{nm}.{part}', [[(x + i * INT_SEP, y, on) for x, y, on in cs] for i in range(n_st)], adv_n)
    adv2 = INT_ADV + INT_SEP
    xc2 = xce + 0.5 * INT_SEP
    rx2 = INT_RING_RX + 0.5 * INT_SEP
    emit('dblint.mid', _stems_through_ring([(x0e, x1e), (x0e + INT_SEP, x1e + INT_SEP)], INT_MID, xc2, 0.5 * INT_MID,
                                           rx2, INT_RING_RY, ring_th), adv2)

    # 8. Horizontal wide accents (hat, tilde), full-bleed overbars, stretchy arrows & curly brackets
    hat_th = max(43.0, bar * 1.00)
    for idx, (adv_h, ink_w, rise) in enumerate([
        (340, 270.0, 120.0),
        (680, 600.0, 144.0),
        (1060, 980.0, 158.0),
        (1520, 1440.0, 172.0),
        (2060, 1980.0, 184.0),
        (2700, 2620.0, 194.0),
        (3440, 3360.0, 204.0),
    ]):
        emit(f'hat.size{idx}', [_hat_cw(adv_h, ink_w, 525.0, rise, hat_th)], adv_h)
    emit('hat.flat', [_hat_cw(400, 330.0, 525.0, 90.0, hat_th * 0.94)], 400)

    tld_th = max(41.0, bar * 0.96)
    for idx, (adv_t, ink_w, amp) in enumerate([
        (380, 310.0, 44.0),
        (700, 620.0, 48.0),
        (1080, 1000.0, 52.0),
        (1540, 1460.0, 56.0),
        (2080, 2000.0, 60.0),
        (2720, 2640.0, 64.0),
        (3460, 3380.0, 68.0),
    ]):
        emit(f'tilde.size{idx}', [_tilde_cw(adv_t, ink_w, 625.0, amp, tld_th)], adv_t)
    emit('tilde.flat', [_tilde_cw(420, 350.0, 605.0, 30.0, tld_th * 0.94)], 420)

    # Full-bleed horizontal overbars (0..W so Chrome's ink-width stretcher matches AdvanceMeasurement)
    for idx, w_hb in enumerate(HBAR_ADV):
        emit(f'hbar.size{idx}', [_rect_cw(0.0, 600.0, float(w_hb), 600.0 + r_th)], w_hb)
    emit('hbar.ext', [_rect_cw(0.0, 600.0, 600.0, 600.0 + r_th)], 600)

    # Stretchy arrows: a 4% ladder (see OVERBRACE_ADV), each drawn like the base arrow
    for k_i, w_ar in enumerate(ARROW_ADV, start=1):
        rcw = _arrow_rhead_cw(40.0, float(w_ar) - 40.0, axis, bar, sm)
        emit(f'arrowright.size{k_i}', [rcw], w_ar)
        emit(f'arrowleft.size{k_i}', _mirror_x([rcw], 0.5 * float(w_ar)), w_ar)
    for k_i, w_ab in enumerate(ARROWBOTH_ADV, start=1):
        emit(f'arrowboth.size{k_i}', [_arrow_both_cw(40.0, float(w_ab) - 40.0, axis, bar, sm)], w_ab)
    # head parts 700 wide with 400 of shaft before the head (connector 380)
    ar_rhead = _arrow_rhead_cw(0.0, 660.0, axis, bar, sm)
    ar_lhead = _mirror_x([ar_rhead], 350.0)[0]
    ar_ext = _rect_cw(0.0, axis - 0.5 * bar, 500.0, axis + 0.5 * bar)
    emit('arrow.lhead', [ar_lhead], 700)
    emit('arrow.ext', [ar_ext], 500)
    emit('arrow.rhead', [ar_rhead], 700)

    # Horizontal curly brackets (U+23DE overbrace, U+23DF underbrace, .size1..5, 5-part assembly):
    # the drawn brace of section 3 turned on its side, about 0.5 em deep with a stroke of
    # 1.75 rules, as TeX's \overbrace and \underbrace look beside the formula (0.28 em read
    # light and flat under 1 + 2 + ... + n, M091).
    hb_w = 1.75 * bar
    hb_wt = 0.62 * hb_w
    hb_tipw = 1.3 * hb_w
    hb_xs = 0.0
    hb_hdx, hb_cdx = 205.0, 225.0
    hb_tip = hb_xs + hb_hdx

    def hbrace_vert(L):
        hh = min(HB_HOOK, 0.22 * L)
        ch = min(HB_CUSP, 0.24 * L)
        return _brace_full_cw(hb_xs, hb_w, hb_wt, hb_hdx, hh, hb_cdx, ch, hb_tipw, 0.0, float(L))

    ov0_cw, un0_cw = _rotate_brace_to_over_under(hbrace_vert(OVERBRACE_ADV[0]), 0.0, hb_tip, 1.0,
                                                 y_over_bot=HB_OVER_BOT, y_under_top=HB_UNDER_TOP)
    for k_i, w_ob in enumerate(OVERBRACE_ADV[1:], start=1):
        ov_k, un_k = _rotate_brace_to_over_under(hbrace_vert(w_ob), 0.0, hb_tip, 1.0,
                                                 y_over_bot=HB_OVER_BOT, y_under_top=HB_UNDER_TOP)
        emit(f'overbrace.size{k_i}', [ov_k], w_ob)
        emit(f'underbrace.size{k_i}', [un_k], w_ob)

    hb_left = _brace_hook_cw(hb_xs, hb_w, hb_wt, hb_hdx, HB_HOOK, 0.0, HB_END_PART)
    hb_right = _mirror_y([hb_left], 0.5 * HB_END_PART)[0]
    hb_mid = _brace_cusp_cw(hb_xs, hb_w, hb_cdx, HB_CUSP, hb_tipw, 0.5 * HB_MID_PART, 0.0, HB_MID_PART)
    hb_ext = _rect_cw(hb_xs - 0.5 * hb_w, 0.0, hb_xs + 0.5 * hb_w, 500.0)
    for nm, cw, adv_p in (('left', hb_left, HB_END_PART), ('ext', hb_ext, 500), ('mid', hb_mid, HB_MID_PART),
                          ('right', hb_right, HB_END_PART)):
        ov_p, un_p = _rotate_brace_to_over_under(cw, 0.0, hb_tip, 1.0, y_over_bot=HB_OVER_BOT, y_under_top=HB_UNDER_TOP)
        emit(f'overbrace.{nm}', [ov_p], adv_p)
        emit(f'underbrace.{nm}', [un_p], adv_p)

    # 9. Four standard encoded horizontal math characters (U+0305, U+203E, U+23DE, U+23DF)
    new_maps = [
        emit_encoded('uni0305', 0x0305, [_rect_cw(-220.0, 600.0, 220.0, 600.0 + r_th)], 0, gdef_cls=3),
        emit_encoded('uni203E', 0x203E, [_rect_cw(0.0, 745.0, 500.0, 745.0 + r_th)], 500, gdef_cls=1),
        emit_encoded('uni23DE', 0x23DE, [ov0_cw], OVERBRACE_ADV[0], gdef_cls=1),
        emit_encoded('uni23DF', 0x23DF, [un0_cw], OVERBRACE_ADV[0], gdef_cls=1),
    ]

    font.setGlyphOrder(order)
    for cp, gname in new_maps:
        ctx.map(cp, gname)

    ctx.math_added = added
    ctx.log(f'overrode radical, mapped 4 math chars, added {len(added)} .math_table glyphs')


# --- Phase 2: features ------------------------------------------------------------

def features(ctx):
    order = set(ctx.font.getGlyphOrder())
    dtls_rules = []
    if 'i' in order and 'dotlessi' in order:
        dtls_rules.append('  sub i by dotlessi;')
    if 'j' in order and 'uni0237' in order:
        dtls_rules.append('  sub j by uni0237;')
    if 'u1D456' in order and 'u1D6A4' in order:
        dtls_rules.append('  sub u1D456 by u1D6A4;')
    if 'u1D457' in order and 'u1D6A5' in order:
        dtls_rules.append('  sub u1D457 by u1D6A5;')

    flac_pairs = [
        ('circumflex', 'hat.flat.math_table'),
        ('uni0302', 'hat.flat.math_table'),
        ('hat.size0.math_table', 'hat.flat.math_table'),
        ('tilde', 'tilde.flat.math_table'),
        ('tildecomb', 'tilde.flat.math_table'),
        ('tilde.size0.math_table', 'tilde.flat.math_table'),
    ]
    flac_rules = [f'  sub {src} by {dst};' for src, dst in flac_pairs if src in order and dst in order]

    fea = []
    if dtls_rules:
        fea.append('lookup MATH_TABLE_DTLS {\n' + '\n'.join(dtls_rules) + '\n} MATH_TABLE_DTLS;')
        fea.append('feature dtls { lookup MATH_TABLE_DTLS; } dtls;')
    if flac_rules:
        fea.append('lookup MATH_TABLE_FLAC {\n' + '\n'.join(flac_rules) + '\n} MATH_TABLE_FLAC;')
        fea.append('feature flac { lookup MATH_TABLE_FLAC; } flac;')
    if fea:
        ctx.gsub('\n'.join(fea), after='main')


# --- Phase 3: post (OpenType MATH table) ------------------------------------------

def _mvr(val):
    r = ot.MathValueRecord()
    r.Value = int(round(val))
    r.DeviceTable = None
    return r


def _cov(glyphs, gid_fn):
    c = ot.Coverage()
    c.glyphs = sorted(set(glyphs), key=gid_fn)
    return c


def _vrec(glyph, adv):
    r = ot.MathGlyphVariantRecord()
    r.VariantGlyph = glyph
    r.AdvanceMeasurement = int(round(adv))
    return r


def _prec(glyph, start_c, end_c, full_adv, flags=0):
    p = ot.GlyphPartRecord()
    p.glyph = glyph
    p.StartConnectorLength = int(round(start_c))
    p.EndConnectorLength = int(round(end_c))
    p.FullAdvance = int(round(full_adv))
    p.PartFlags = int(flags)
    return p


def _mk_side(heights, kerns):
    mk = ot.MathKern()
    mk.HeightCount = len(heights)
    mk.CorrectionHeight = [_mvr(h) for h in heights]
    mk.KernValue = [_mvr(v) for v in kerns]
    return mk


def _gpos_top_anchors(font):
    """Extract class-0 top BaseAnchor X coordinates from Mulish's mark-to-base GPOS."""
    out = {}
    if 'GPOS' not in font:
        return out
    for lk in font['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable:
            if lk.LookupType == 9:
                st = st.ExtSubTable
            if getattr(st, 'LookupType', lk.LookupType) != 4:
                continue
            marks = [(g, mr.Class, mr.MarkAnchor.YCoordinate)
                     for g, mr in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord) if mr.MarkAnchor]
            top_cls = {c for g, c, y in marks if ('0302' in g or '0307' in g or '0308' in g) and y > 400}
            if not top_cls:
                continue
            c0 = min(top_cls)
            for g, rec in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                if g not in out and c0 < len(rec.BaseAnchor) and rec.BaseAnchor[c0] is not None:
                    out[g] = rec.BaseAnchor[c0].XCoordinate
    return out


LONG_ARROWS = (0x27F5, 0x27F6, 0x27F7, 0x27F8, 0x27F9, 0x27FA, 0x27FC)
LONG_ARROW_EXTRA = 450


def _lengthen_long_arrows(font, cmap, log):
    """TeX's \\longrightarrow and \\implies are 1.46 em, about half again ⇒ (1.0 em); the
    symbols module draws ⟵ ⟶ ⟷ ⟸ ⟹ ⟺ ⟼ in a 1000-unit cell (ink 893), which beside
    Torchlette's 0.7 em ⇒ still reads as ⇒ (M087 M097). Lengthen their shafts by
    LONG_ARROW_EXTRA: every point right of the cell's middle moves right, so the heads, the
    tail bar and the shafts' ends keep their drawing (the shafts are straight there, upright
    and italic alike, and no point lies near the middle). Runs in post, before hinting."""
    glyf, hmtx = font['glyf'], font['hmtx']
    done = []
    for cp in LONG_ARROWS:
        g = cmap.get(cp)
        if not g or g not in glyf:
            continue
        gl = glyf[g]
        if gl.isComposite() or gl.numberOfContours <= 0:
            continue
        adv, lsb = hmtx[g]
        mid = 0.5 * adv
        coords = gl.coordinates
        near = [x for x, y in coords if abs(x - mid) < 60]
        assert not near, f'{g}: points near the middle of the shaft {near}'
        gl.coordinates = GlyphCoordinates([(x + LONG_ARROW_EXTRA if x > mid else x, y) for x, y in coords])
        gl.recalcBounds(glyf)
        hmtx[g] = (adv + LONG_ARROW_EXTRA, lsb)
        done.append(g)
    log(f'lengthened {len(done)} long arrows by {LONG_ARROW_EXTRA}')


def post(ctx):
    font = ctx.font
    glyf, hmtx = font['glyf'], font['hmtx']
    gs = font.getGlyphSet()
    order_set = set(font.getGlyphOrder())
    gid = font.getGlyphID
    cmap = font.getBestCmap()

    R = int(round(ctx.BAR))
    axis = int(round(ctx.LIN_AXIS))
    k_it = float(ctx.ITALIC_K) if ctx.ITALIC else 0.0
    xh_os2 = int(font['OS/2'].sxHeight)
    cap_os2 = int(font['OS/2'].sCapHeight)

    def gbounds(name):
        g = glyf[name]
        if g.numberOfContours == 0 and not g.isComposite():
            return None
        g.recalcBounds(glyf)
        if getattr(g, 'xMax', None) is None:
            bp = BoundsPen(gs)
            gs[name].draw(bp)
            return bp.bounds
        return (g.xMin, g.yMin, g.xMax, g.yMax)

    _lengthen_long_arrows(font, cmap, ctx.log)

    # The wide hats and tildes get mathglyphs' inkless contour (two points on one spot, no
    # area) 90 units under their ink: Chrome stacks an accent with its ink touching the base's,
    # so the gap has to be in the glyph.
    gaps = {f'{p}.size{i}.math_table': ACCENT_GAP for p in ('hat', 'tilde') for i in range(7)}
    # \overline is <mover accent> with U+203E: its bar sits on the base the same way, so
    # its inkless contour sets TeX's overline clearance (3 rule thicknesses above the ink)
    gaps.update({g: OVERLINE_GAP for g in ['uni203E', 'uni0305'] + [f'hbar.size{i}.math_table' for i in range(len(HBAR_ADV))]})
    for name, gap in gaps.items():
        if name not in order_set:
            continue
        g = glyf[name]
        coords = list(g.coordinates); flags = list(g.flags); ends = list(g.endPtsOfContours)
        xs = [p[0] for p in coords]; ys = [p[1] for p in coords]
        x = round((min(xs) + max(xs)) / 2); y = round(min(ys) - gap)
        coords += [(x, y), (x + 1, y)]; flags += [1, 1]; ends.append(len(coords) - 1)
        g.coordinates = GlyphCoordinates(coords); g.flags = array('B', flags)
        g.endPtsOfContours = ends; g.numberOfContours = len(ends)
        g.recalcBounds(glyf)
        hmtx[name] = (hmtx[name][0], g.xMin)

    # 1. MathConstants (all 56 OpenType MATH constants; Upright == Italic at every weight)
    mc = ot.MathConstants()
    mc.ScriptPercentScaleDown = 68
    mc.ScriptScriptPercentScaleDown = 53
    mc.DelimitedSubFormulaMinHeight = 1320
    mc.DisplayOperatorMinHeight = DISPLAY_OP_MIN

    dR = R - 53
    dR_pos = max(0, dR)
    mvr_vals = {
        'MathLeading': 150,
        'AxisHeight': axis,
        'AccentBaseHeight': xh_os2,
        'FlattenedAccentBaseHeight': cap_os2 - 1,
        'SubscriptShiftDown': 165,
        'SubscriptTopMax': 380,
        # Chrome and Firefox drop a subscript to (base ink descent + this) and raise a
        # superscript to (base ink ascent - SuperscriptBaselineDropMax), for a letter as for a
        # box. TeX does that only for boxes; on a single letter it keeps sub1/sup1. With
        # Torchlette's long ascenders (750) and descenders (243), 140 and 70 dropped y_i, g_mu
        # and beta_1 far below and floated b^2, d^2, f^2, )^2 an x-height above a^2. These
        # values make a descender letter's subscript and an ascender letter's or closing
        # fence's superscript sit where a plain letter's do, and let only taller things (grown
        # fences, stacked fractions) push scripts out, as TeX's boxes do.
        'SubscriptBaselineDropMin': -45,
        'SuperscriptShiftUp': 400,
        'SuperscriptShiftUpCramped': 300,
        'SuperscriptBottomMin': 135,
        'SuperscriptBaselineDropMax': 340,
        'SubSuperscriptGapMin': 155 + round(0.45 * dR_pos),
        'SuperscriptBottomMaxWithSubscript': 380,
        'SpaceAfterScript': 45,
        'UpperLimitGapMin': 95 + round(0.35 * dR_pos),
        'UpperLimitBaselineRiseMin': 260,
        'LowerLimitGapMin': 95 + round(0.35 * dR_pos),
        'LowerLimitBaselineDropMin': 600,
        'StackTopShiftUp': 480 + round(0.45 * dR),
        'StackTopDisplayStyleShiftUp': 665 + round(0.65 * dR),
        'StackBottomShiftDown': 345 + round(0.45 * dR),
        'StackBottomDisplayStyleShiftDown': 645 + round(0.65 * dR),
        'StackGapMin': 165 + round(0.50 * dR_pos),
        'StackDisplayStyleGapMin': 315 + round(0.75 * dR_pos),
        'StretchStackTopShiftUp': 175,
        'StretchStackBottomShiftDown': 540,
        'StretchStackGapAboveMin': 85 + round(0.35 * dR_pos),
        'StretchStackGapBelowMin': 95 + round(0.35 * dR_pos),
        'FractionNumeratorShiftUp': 460 + round(0.45 * dR),
        'FractionNumeratorDisplayStyleShiftUp': 665 + round(0.65 * dR),
        'FractionDenominatorShiftDown': 345 + round(0.45 * dR),
        'FractionDenominatorDisplayStyleShiftDown': 645 + round(0.65 * dR),
        'FractionNumeratorGapMin': 72 + round(0.35 * dR_pos),
        'FractionNumDisplayStyleGapMin': 148 + round(0.45 * dR_pos),
        'FractionRuleThickness': R,
        'FractionDenominatorGapMin': 72 + round(0.35 * dR_pos),
        'FractionDenomDisplayStyleGapMin': 148 + round(0.45 * dR_pos),
        'SkewedFractionHorizontalGap': 320,
        'SkewedFractionVerticalGap': 66 + round(0.30 * dR_pos),
        'OverbarVerticalGap': 138 + round(0.40 * dR_pos),
        'OverbarRuleThickness': R,
        'OverbarExtraAscender': R,
        'UnderbarVerticalGap': 138 + round(0.40 * dR_pos),
        'UnderbarRuleThickness': R,
        'UnderbarExtraDescender': R,
        'RadicalVerticalGap': 62 + round(0.45 * dR_pos),
        'RadicalDisplayStyleVerticalGap': 150 + round(0.45 * dR_pos),
        'RadicalRuleThickness': R,
        'RadicalExtraAscender': R,
        'RadicalKernBeforeDegree': 250,
        'RadicalKernAfterDegree': -390,
    }
    for k, v in mvr_vals.items():
        setattr(mc, k, _mvr(v))
    mc.RadicalDegreeBottomRaisePercent = 60

    # 2. MathVariants (VertGlyphConstruction & HorizGlyphConstruction)
    # Every AdvanceMeasurement and connector length is a plain style-invariant uint16.
    STD_ADV = (965, 1060, 1155, 1250, 1340, 1430)
    ANG_ADV = (885, 995, 1105, 1215, 1325, 1430)
    SLASH_ADV = (930, 1030, 1130, 1230, 1330, 1430)
    RAD_STEP_ADV = (938, 1035, 1135, 1235, 1335, 1430) + RAD_TALL_H

    def std_sizes(base_g, prefix, base_adv=885, advs=STD_ADV, shortfall=True):
        # TeX lets a \left/\right delimiter fall short of the formula (TeX: up to 1 - 0.901; here 1 - 0.85, since Torchlette's text fences are 0.885 em against TeX's 1.0 and its descenders longer)
        # (\delimiterfactor 901); MathML Core has no such rule and takes the first variant whose
        # AdvanceMeasurement covers the target. So fences declare their real height / 0.85:
        # \left( around x or a small fraction stays the text-size paren, as in TeX, instead of
        # jumping one size up (M049 M058 M072). Only variant choice changes; the glyphs, their
        # ink and the assemblies (exact FullAdvance) are drawn at their real sizes.
        f = (1.0 / 0.85) if shortfall else 1.0
        return [_vrec(base_g, base_adv * f)] + [_vrec(f'{prefix}.size{i}.math_table', advs[i] * f) for i in range(len(advs))]

    def asm3(prefix, bot_end=360, bot_full=600, ext_full=500, top_start=360, top_full=600, ic=0):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(ic)
        a.PartRecords = [
            _prec(f'{prefix}.bot.math_table', 0, bot_end, bot_full, 0),
            _prec(f'{prefix}.ext.math_table', ext_full, ext_full, ext_full, 1),
            _prec(f'{prefix}.top.math_table', top_start, 0, top_full, 0),
        ]
        a.PartCount = len(a.PartRecords)
        return a

    def int_asm(prefix, ring):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(INT_LEAN + 90)
        parts = [_prec(f'{prefix}.bot.math_table', 0, INT_CONN, INT_PART, 0)]
        if ring:
            parts += [_prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
                      _prec(f'{prefix}.mid.math_table', INT_MID_CONN, INT_MID_CONN, INT_MID, 0),
                      _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1)]
        else:
            parts += [_prec(f'{prefix}.ext.math_table', 500, 500, 500, 1)]
        parts += [_prec(f'{prefix}.top.math_table', INT_CONN, 0, INT_PART, 0)]
        a.PartRecords = parts
        a.PartCount = len(parts)
        return a

    def asm_bar(prefix):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(0)
        a.PartRecords = [
            _prec(f'{prefix}.bot.math_table', 0, 600, 600, 0),
            _prec(f'{prefix}.ext.math_table', 600, 600, 600, 1),
        ]
        a.PartCount = 2
        return a

    def asm_brace(prefix):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(0)
        a.PartRecords = [
            _prec(f'{prefix}.bot.math_table', 0, BRC_CONN, BRC_HOOK_PART, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.mid.math_table', BRC_CONN, BRC_CONN, BRC_MID_PART, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.top.math_table', BRC_CONN, 0, BRC_HOOK_PART, 0),
        ]
        a.PartCount = 5
        return a

    def asm_horiz_brace(prefix):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(0)
        a.PartRecords = [
            _prec(f'{prefix}.left.math_table', 0, 200, HB_END_PART, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.mid.math_table', 200, 200, HB_MID_PART, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.right.math_table', 200, 0, HB_END_PART, 0),
        ]
        a.PartCount = 5
        return a

    def asm_floor(brk_prefix):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(0)
        a.PartRecords = [
            _prec(f'{brk_prefix}.bot.math_table', 0, 360, 600, 0),
            _prec(f'{brk_prefix}.ext.math_table', 500, 500, 500, 1),
        ]
        a.PartCount = 2
        return a

    def asm_ceil(brk_prefix):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(0)
        a.PartRecords = [
            _prec(f'{brk_prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{brk_prefix}.top.math_table', 360, 0, 600, 0),
        ]
        a.PartCount = 2
        return a

    rad_h = round(RAD_BASE[1] - RAD_BASE[0])
    rad_vars = [_vrec('radical', rad_h)] + [_vrec(f'radical.size{i}.math_table', RAD_STEP_ADV[i]) for i in range(len(RAD_STEP_ADV))]

    vert_specs = {
        'parenleft': (std_sizes('parenleft', 'parenleft'), asm3('parenleft', bot_end=380, bot_full=1000, ext_full=500, top_start=380, top_full=1000)),
        'parenright': (std_sizes('parenright', 'parenright'), asm3('parenright', bot_end=380, bot_full=1000, ext_full=500, top_start=380, top_full=1000)),
        'bracketleft': (std_sizes('bracketleft', 'bracketleft'), asm3('bracketleft')),
        'bracketright': (std_sizes('bracketright', 'bracketright'), asm3('bracketright')),
        'braceleft': (std_sizes('braceleft', 'braceleft'), asm_brace('braceleft')),
        'braceright': (std_sizes('braceright', 'braceright'), asm_brace('braceright')),
        'bar': (std_sizes('bar', 'bar', base_adv=899), asm_bar('bar')),
        'uni2223': (std_sizes('uni2223', 'divides', base_adv=899), asm_bar('divides')),
        'uni2016': (std_sizes('uni2016', 'dblbar', base_adv=899), asm_bar('dblbar')),
        'uni2308': (std_sizes('uni2308', 'lceil'), asm_ceil('bracketleft')),
        'uni2309': (std_sizes('uni2309', 'rceil'), asm_ceil('bracketright')),
        'uni230A': (std_sizes('uni230A', 'lfloor'), asm_floor('bracketleft')),
        'uni230B': (std_sizes('uni230B', 'rfloor'), asm_floor('bracketright')),
        'uni27E8': (std_sizes('uni27E8', 'langle', base_adv=705, advs=ANG_ADV), None),
        'uni27E9': (std_sizes('uni27E9', 'rangle', base_adv=705, advs=ANG_ADV), None),
        'slash': (std_sizes('slash', 'slash', base_adv=800, advs=SLASH_ADV, shortfall=False), None),
        'backslash': (std_sizes('backslash', 'backslash', base_adv=800, advs=SLASH_ADV, shortfall=False), None),
        'radical': (rad_vars, asm3('radical', bot_end=RAD_ASM_BOT - RAD_ASM_JOIN - 10, bot_full=RAD_ASM_BOT,
                                   ext_full=RAD_ASM_EXT, top_start=RAD_ASM_TOP - 40, top_full=RAD_ASM_TOP)),
        'summation': ([_vrec('summation', 885), _vrec('summation.dsp.math_table', DSP_Y1 - DSP_Y0)], None),
        'product': ([_vrec('product', 885), _vrec('product.dsp.math_table', DSP_Y1 - DSP_Y0)], None),
        'integral': ([_vrec('integral', 905),
                      _vrec('integral.size1.math_table', 1165),
                      _vrec('integral.dsp.math_table', 1430),
                      _vrec('integral.dsp2.math_table', DISPLAY_OP_MIN)],
                     int_asm('integral', False)),
    }
    # ∬ ∭ ∮ ∯ ⋃ are drawn by another module (mathglyphs, after this one in name order but
    # before this post phase); their display forms are added only when the base glyph is there.
    for cp, nm, ring in ((0x222C, 'dblint', False), (0x222D, 'tplint', False),
                         (0x222E, 'integral', True), (0x222F, 'dblint', True)):
        g = cmap.get(cp)
        if g and g in order_set and g not in vert_specs:
            whole = [] if ring else [_vrec(f'{nm}.dsp2.math_table', DISPLAY_OP_MIN)]
            # 905 as for ∫ (their ink is ∫'s height): a fixed MATH field, the same in every
            # style, since the variable builder needs MATH identical across masters
            vert_specs[g] = ([_vrec(g, 905)] + whole, int_asm(nm, ring))
    for cp, nm in ((0x22C3, 'bigcup'), (0x22C2, 'bigcap')):
        g = cmap.get(cp)
        if g and g in order_set and g not in vert_specs:
            vert_specs[g] = ([_vrec(g, 885), _vrec(f'{nm}.dsp.math_table', DSP_Y1 - DSP_Y0)], None)
    if cmap.get(0x2225) and cmap[0x2225] not in vert_specs:
        vert_specs[cmap[0x2225]] = (std_sizes(cmap[0x2225], 'dblbar', base_adv=899), asm_bar('dblbar'))
    if cmap.get(0x2215) and cmap[0x2215] not in vert_specs:
        vert_specs[cmap[0x2215]] = ([_vrec(cmap[0x2215], 800)] + [_vrec(f'slash.size{i}.math_table', SLASH_ADV[i]) for i in range(len(SLASH_ADV))], None)

    HAT_ADV = (340, 680, 1060, 1520, 2060, 2700, 3440)
    TILDE_ADV = (380, 700, 1080, 1540, 2080, 2720, 3460)
    hat_vars = [_vrec(f'hat.size{i}.math_table', HAT_ADV[i]) for i in range(len(HAT_ADV))]
    tilde_vars = [_vrec(f'tilde.size{i}.math_table', TILDE_ADV[i]) for i in range(len(TILDE_ADV))]
    hbar_vars_full = [_vrec(f'hbar.size{i}.math_table', HBAR_ADV[i]) for i in range(len(HBAR_ADV))]
    hbar_vars_from_0305 = [_vrec('uni0305', 440)] + [_vrec(f'hbar.size{i}.math_table', HBAR_ADV[i]) for i in range(1, len(HBAR_ADV))]
    hbar_vars_from_203E = [_vrec('uni203E', 500)] + [_vrec(f'hbar.size{i}.math_table', HBAR_ADV[i]) for i in range(1, len(HBAR_ADV))]

    hbar_asm = ot.GlyphAssembly()
    hbar_asm.ItalicsCorrection = _mvr(0)
    hbar_asm.PartRecords = [
        _prec('hbar.size0.math_table', 0, 380, HBAR_ADV[0], 0),
        _prec('hbar.ext.math_table', 600, 600, 600, 1),
    ]
    hbar_asm.PartCount = 2

    def arrow_asm(left_h, right_h):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(0)
        parts = []
        if left_h:
            parts.append(_prec('arrow.lhead.math_table', 0, 380, 700, 0))
        parts.append(_prec('arrow.ext.math_table', 500, 500, 500, 1))
        if right_h:
            parts.append(_prec('arrow.rhead.math_table', 380, 0, 700, 0))
        a.PartRecords = parts
        a.PartCount = len(parts)
        return a

    ar_r_vars = [_vrec('arrowright', 660)] + [_vrec(f'arrowright.size{k}.math_table', w) for k, w in enumerate(ARROW_ADV, 1)]
    ar_l_vars = [_vrec('arrowleft', 660)] + [_vrec(f'arrowleft.size{k}.math_table', w) for k, w in enumerate(ARROW_ADV, 1)]
    ar_b_vars = [_vrec('arrowboth', 840)] + [_vrec(f'arrowboth.size{k}.math_table', w) for k, w in enumerate(ARROWBOTH_ADV, 1)]

    ov_vars = [_vrec('uni23DE', OVERBRACE_ADV[0])] + [_vrec(f'overbrace.size{k}.math_table', w) for k, w in enumerate(OVERBRACE_ADV[1:], 1)]
    un_vars = [_vrec('uni23DF', OVERBRACE_ADV[0])] + [_vrec(f'underbrace.size{k}.math_table', w) for k, w in enumerate(OVERBRACE_ADV[1:], 1)]

    # ^ grows through mathglyphs' hats (ink 440..820, the text ^'s roof) before this module's
    # wide hats; AdvanceMeasurement is each glyph's advance.
    hat_w = [f'hat.w{i}.mathglyphs' for i in range(1, 6) if f'hat.w{i}.mathglyphs' in order_set]
    hat_vars = ([_vrec(g, hmtx[g][0]) for g in hat_w]
                + [_vrec(f'hat.size{i}.math_table', HAT_ADV[i]) for i in range(3, len(HAT_ADV))])
    horiz_specs = {
        'asciicircum': (hat_vars, None),
        'circumflex': (hat_vars, None),
        'uni0302': (hat_vars, None),
        'asciitilde': (tilde_vars, None),
        'tilde': (tilde_vars, None),
        'tildecomb': (tilde_vars, None),
        'macron': (hbar_vars_full, hbar_asm),
        'uni0304': (hbar_vars_full, hbar_asm),
        'uni0305': (hbar_vars_from_0305, hbar_asm),
        'uni203E': (hbar_vars_from_203E, hbar_asm),
        'arrowright': (ar_r_vars, arrow_asm(False, True)),
        'arrowleft': (ar_l_vars, arrow_asm(True, False)),
        'arrowboth': (ar_b_vars, arrow_asm(True, True)),
        'uni23DE': (ov_vars, asm_horiz_brace('overbrace')),
        'uni23DF': (un_vars, asm_horiz_brace('underbrace')),
    }

    v_keys = sorted((g for g in vert_specs if g in order_set), key=gid)
    h_keys = sorted((g for g in horiz_specs if g in order_set), key=gid)

    mv = ot.MathVariants()
    mv.MinConnectorOverlap = 50
    mv.VertGlyphCoverage = _cov(v_keys, gid)
    mv.VertGlyphCount = len(v_keys)
    mv.VertGlyphConstruction = []
    for g in v_keys:
        recs, asm = vert_specs[g]
        c = ot.MathGlyphConstruction()
        c.GlyphAssembly = asm
        c.MathGlyphVariantRecord = recs
        c.VariantCount = len(recs)
        mv.VertGlyphConstruction.append(c)

    mv.HorizGlyphCoverage = _cov(h_keys, gid)
    mv.HorizGlyphCount = len(h_keys)
    mv.HorizGlyphConstruction = []
    for g in h_keys:
        recs, asm = horiz_specs[g]
        c = ot.MathGlyphConstruction()
        c.GlyphAssembly = asm
        c.MathGlyphVariantRecord = recs
        c.VariantCount = len(recs)
        mv.HorizGlyphConstruction.append(c)

    # 3. MathGlyphInfo (identical canonical coverages across all 14 styles)
    ext_glyphs = set(v_keys)
    for g in v_keys:
        recs, asm = vert_specs[g]
        for r in recs:
            ext_glyphs.add(r.VariantGlyph)
        if asm:
            for p in asm.PartRecords:
                ext_glyphs.add(p.glyph)

    # 3b. MathItalicsCorrectionInfo: canonical set of letters + integrals across all 14 styles
    ic_map = {}
    letter_cps = (list(range(0x0041, 0x005B)) + list(range(0x0061, 0x007B))
                  + [0x0131, 0x0237]
                  + list(range(0x0391, 0x03AA)) + list(range(0x03B1, 0x03CA))
                  + [0x03D1, 0x03D5, 0x03D6, 0x03F0, 0x03F1, 0x03F5]
                  + [0x2102, 0x210D, 0x210F, 0x2112, 0x2115, 0x2119, 0x211A, 0x211D, 0x2124, 0x1D53C])
    for cp in letter_cps:
        g = cmap.get(cp)
        if not g or g not in order_set:
            continue
        b = gbounds(g)
        if not b:
            continue
        overhang = b[2] - hmtx[g][0]
        if ctx.ITALIC:
            ic_map[g] = max(16, int(round(overhang + 34)))
        else:
            ic_map[g] = max(0, int(round(overhang + (12 if overhang > 0 else 0))))

    for g, base_ic_up, base_ic_it in [
        ('integral', 165, 210),
        ('integral.size1.math_table', 195, 195),
        ('integral.dsp.math_table', 235, 235),
        ('integral.dsp2.math_table', INT_DSP2_IC, INT_DSP2_IC),
        ('dblint.dsp2.math_table', INT_DSP2_IC, INT_DSP2_IC),
        ('tplint.dsp2.math_table', INT_DSP2_IC, INT_DSP2_IC),
    ]:
        if g in order_set:
            ic_map[g] = base_ic_it if ctx.ITALIC else base_ic_up

    # Mathematical italic alphabet (112 targets): always italic correction regardless of ctx.ITALIC
    math_italic_glyphs = (
        [f'u1D4{i:02X}' for i in range(0x34, 0x55)] +
        [f'u1D4{i:02X}' for i in range(0x56, 0x68)] +
        ['uni210E', 'u1D6A4', 'u1D6A5'] +
        [f'u1D6{i:02X}' for i in range(0xE2, 0x100)] +
        [f'u1D7{i:02X}' for i in range(0x00, 0x1C)]
    )
    for g in math_italic_glyphs:
        if g in order_set and g not in ic_map:
            b = gbounds(g)
            if b:
                overhang = b[2] - hmtx[g][0]
                ic_map[g] = max(16, int(round(overhang + 34)))

    ic_keys = sorted(ic_map, key=gid)
    mic = ot.MathItalicsCorrectionInfo()
    mic.Coverage = _cov(ic_keys, gid)
    mic.ItalicsCorrectionCount = len(ic_keys)
    mic.ItalicsCorrection = [_mvr(ic_map[g]) for g in ic_keys]

    # 3c. MathTopAccentAttachment: canonical set of base letters + accent marks/variants
    gpos_anc = _gpos_top_anchors(font)
    att_map = {}
    for cp in letter_cps + list(range(0x00C0, 0x0250)):
        g = cmap.get(cp)
        if not g or g not in order_set or g in att_map:
            continue
        b = gbounds(g)
        if not b:
            continue
        if g == 'f':
            att_map[g] = int(round(0.5 * (b[0] + b[2]) + (38 if ctx.ITALIC else 24)))
        elif g in gpos_anc:
            att_map[g] = int(round(gpos_anc[g] + k_it * 50.0))
        else:
            att_map[g] = int(round(0.5 * (b[0] + b[2]) + k_it * 55.0))

    k_math = float(ctx.ITALIC_K) if ctx.ITALIC else 0.1587
    for g in math_italic_glyphs:
        if g in order_set and g not in att_map:
            b = gbounds(g)
            if b:
                mid_x = 0.5 * (b[0] + b[2])
                if g == 'u1D453':  # math italic f
                    att_map[g] = int(round(mid_x + 38))
                else:
                    att_map[g] = int(round(mid_x + k_math * 55.0))

    accent_names = (
        [
            'asciicircum', 'circumflex', 'uni0302',
            'asciitilde', 'tilde', 'tildecomb',
            'macron', 'uni0304', 'uni0305', 'uni203E',
            'dotaccent', 'uni0307', 'dieresis', 'uni0308',
            'acute', 'acutecomb', 'grave', 'gravecomb',
            'breve', 'uni0306', 'caron', 'uni030C', 'ring', 'uni030A',
            'hat.flat.math_table', 'tilde.flat.math_table',
        ]
        + [f'hat.size{i}.math_table' for i in range(len(HAT_ADV))]
        + [f'tilde.size{i}.math_table' for i in range(len(TILDE_ADV))]
        + [f'hbar.size{i}.math_table' for i in range(len(HBAR_ADV))]
    )

    for g in accent_names:
        if g in order_set:
            b = gbounds(g)
            if b:
                att_map[g] = int(round(0.5 * (b[0] + b[2])))

    # mathglyphs' hats: centred in their advance (their inkless contour is added after this
    # phase); its vector arrow U+20D7 is a zero-width mark drawn left of 0, attached at 0.
    for g in hat_w:
        att_map[g] = int(round(hmtx[g][0] / 2.0))
    if 'uni20D7' in order_set:
        att_map['uni20D7'] = 0

    att_keys = sorted(att_map, key=gid)
    mta = ot.MathTopAccentAttachment()
    mta.TopAccentCoverage = _cov(att_keys, gid)
    mta.TopAccentAttachmentCount = len(att_keys)
    mta.TopAccentAttachment = [_mvr(att_map[g]) for g in att_keys]

    # 3d. MathKernInfo: corner kerns on A, F, L, P, T, V, W, Y (identical coverage across all 14 styles)
    kern_specs = {}
    br_k = -75 if ctx.ITALIC else -60
    tr_k = -45 if ctx.ITALIC else -55
    for g in ('F', 'P', 'T', 'V', 'W', 'Y'):
        if g in order_set:
            kern_specs[g] = (None, _mk_side([250], [br_k, 0]))
    for g in ('A', 'L'):
        if g in order_set:
            kern_specs[g] = (_mk_side([460], [0, tr_k]), None)

    mk_keys = sorted(kern_specs, key=gid)
    mki = ot.MathKernInfo()
    mki.MathKernCoverage = _cov(mk_keys, gid)
    mki.MathKernCount = len(mk_keys)
    mki.MathKernInfoRecords = []
    for g in mk_keys:
        tr, br = kern_specs[g]
        rec = ot.MathKernInfoRecord()
        rec.TopRightMathKern = tr
        rec.TopLeftMathKern = None
        rec.BottomRightMathKern = br
        rec.BottomLeftMathKern = None
        mki.MathKernInfoRecords.append(rec)

    mgi = ot.MathGlyphInfo()
    mgi.MathItalicsCorrectionInfo = mic
    mgi.MathTopAccentAttachment = mta
    mgi.ExtendedShapeCoverage = _cov(ext_glyphs, gid)
    mgi.MathKernInfo = mki

    math_tbl = newTable('MATH')
    math_tbl.table = ot.MATH()
    math_tbl.table.Version = 0x00010000
    math_tbl.table.MathConstants = mc
    math_tbl.table.MathGlyphInfo = mgi
    math_tbl.table.MathVariants = mv
    font['MATH'] = math_tbl

    # GSUB 'math' script record routing: inherit all DFLT features (including dtls)
    if 'GSUB' in font:
        gsub = font['GSUB'].table
        if hasattr(gsub, 'ScriptList') and gsub.ScriptList and hasattr(gsub.ScriptList, 'ScriptRecord'):
            if not any(sr.ScriptTag == 'math' for sr in gsub.ScriptList.ScriptRecord):
                import copy
                dflt = next((sr for sr in gsub.ScriptList.ScriptRecord if sr.ScriptTag == 'DFLT'), None)
                if dflt:
                    math_sr = ot.ScriptRecord()
                    math_sr.ScriptTag = 'math'
                    math_sr.Script = copy.deepcopy(dflt.Script)
                    gsub.ScriptList.ScriptRecord.append(math_sr)
                    gsub.ScriptList.ScriptRecord.sort(key=lambda sr: sr.ScriptTag)
                    gsub.ScriptList.ScriptCount = len(gsub.ScriptList.ScriptRecord)

    ctx.log(f'MATH v1.0: Rule={R}, Axis={axis}, ABH={xh_os2}, FABH={cap_os2 - 1}, '
            f'vert={len(v_keys)}, horiz={len(h_keys)}, italCorr={len(ic_keys)}, topAcc={len(att_keys)}')

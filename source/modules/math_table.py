"""math_table: OpenType MATH table, stretchy delimiters, radicals, display operators and math accents.

Builds a complete OpenType MATH table (version 1.0) for MathML Core rendering across all
14 upright and italic styles, overriding only `radical` (for seamless vinculum overhang and
monoline valley matching its size variants) and adding four standard horizontal math code points
(U+0305 combining overline, U+203E overline, U+23DE top curly bracket, U+23DF bottom curly bracket):

glyphs    Encoded additions (uni0305, uni203E, uni23DE, uni23DF), monoline flat-cut `radical`
          override, and unencoded size variants and GlyphAssembly parts (all named *.math_table,
          with identical contour counts, point counts and starting-point order across all 14
          styles for variable-font interpolation):
          - Vertical delimiters: ( ) [ ] { } | ∣ ‖ ⌊ ⌋ ⌈ ⌉ ⟨ ⟩ / \\ (discrete size0..size5
            variants strictly inside the -315..1115 vertical metrics envelope with zero dead
            steps, plus multi-part GlyphAssembly parts for arbitrary matrix/tall heights).
            Curly braces are cut-and-extended directly from Mulish's upright `braceleft` so
            they preserve Mulish's exact hook radius, straight terminal and 73–85u pointed cusp.
          - Radicals: base `radical` (938) + radical.size1..size5.math_table (1035..1430) and
            radical.{bot,ext,top}.math_table, drawn with parallel-sided monoline strokes, a
            compact flat-foot valley, and a flat horizontal top cut overhanging advance width by
            38 units (zero hanging elbow tooth under Chrome's centre-on-top rule painter).
          - Display operators: summation.dsp.math_table (1400), product.dsp.math_table (1400),
            and Mulish-sculpted integral.{size1,dsp,bot,ext,top}.math_table (1165, 1430 + 3-part
            assembly) paired with DisplayOperatorMinHeight = 1400.
          - Horizontal stretchy accents, rules, arrows and curly brackets:
            hat.size0..size6.math_table (+ flat), tilde.size0..size6.math_table (+ flat),
            full-bleed hbar.size0..size6.math_table (+ hbar.ext), arrow{right,left,both}.size1..5
            (+ arrow.{lhead,ext,rhead}), and Mulish-rotated {overbrace,underbrace}.size1..5
            (+ 5-part {overbrace,underbrace}.{left,ext,mid,right}).
          Vertical stretchy variants, radicals and horizontal stretch operators are counter-sheared
          in italic styles so stacked assembly parts and radicals stand upright with zero step.

features  GSUB `dtls` (dotless i/j under math accents) and `flac` (flattened capital accents),
          all lookups prefixed with `MATH_TABLE_`.

post      Populates `font['MATH']` (`MathConstants`, `MathGlyphInfo`, `MathVariants`) with
          all coverages strictly sorted by glyph ID, AccentBaseHeight = OS/2.sxHeight (470),
          FlattenedAccentBaseHeight = OS/2.sCapHeight - 1 (704), damped heavy-weight gaps,
          and identical canonical glyph/uint16 structure across all 14 styles.
"""
import math
import os
from array import array
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.varLib.instancer import instantiateVariableFont

GLYPH_OVERRIDE = {'radical'}

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


def _radical_monoline_cw(y0, y1, r_th):
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
    x_top_L = 562.0 + 0.04 * (H - 938.0)
    x_top_R = x_top_L + w_up
    adv = round(x_top_R - 38.0)

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


def _radical_asm_parts(r_th):
    """Three-part vertical GlyphAssembly for arbitrary-height radicals:
    bot (0..900, vertical right stem on 500..900, End=380), ext (0..500), and
    plain flat-cut top stem (0..520, Start=420) overhanging advance by 38 units."""
    w_up = max(46.0, 1.05 * r_th)
    w_down = max(42.0, 0.96 * r_th)
    w_foot = max(40.0, 0.98 * r_th)
    ledge_h = max(38.0, 0.94 * r_th)

    x_stem_L = 568.0
    x_stem_R = x_stem_L + w_up
    adv = round(x_stem_R - 38.0)

    y_ledge = 375.0
    x_ledge_L = 32.0
    x_ledge_R = 146.0 + 0.32 * r_th
    x_foot_L = 305.0
    x_foot_R = x_foot_L + w_foot
    y_join_L = 500.0

    s_dn = (x_foot_L - (x_ledge_R - w_down)) / y_ledge
    s_up = (x_stem_L - (x_foot_R - w_up)) / y_join_L
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
        (x_stem_L, 900.0, 1),
        (x_stem_R, 900.0, 1),
        (x_stem_R, y_join_R, 1),
        (x_foot_R, 0.0, 1),
        (x_foot_L, 0.0, 1),
        (x_ledge_in_bot, y_ledge - ledge_h, 1),
    ]
    ext = _rect_cw(x_stem_L, 0.0, x_stem_R, 500.0)
    top = _rect_cw(x_stem_L, 0.0, x_stem_R, 520.0)
    return bot, ext, top, adv


def _summation_dsp_cw(y0, y1, bar_h, diag_w):
    """Display-size sans-serif summation ∑ matching Torchlette Sans's 13-point geometry."""
    ym = 0.5 * (y0 + y1)
    x_L, x_R = 56.0, 844.0
    x_apex_L = 470.0
    x_apex_R = x_apex_L + diag_w
    y_ap = 26.0
    x_in_L = x_L + 1.45 * diag_w
    bevel = max(48.0, 0.85 * bar_h)
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
    return cw, 900


def _product_dsp_cw(y0, y1, stem_w, bar_h):
    """Display-size sans-serif product ∏ matching Torchlette Sans's 8-point geometry."""
    x_L, x_R = 60.0, 860.0
    cw = [
        (x_L, y0, 1),
        (x_L, y1, 1),
        (x_R, y1, 1),
        (x_R, y0, 1),
        (x_R - stem_w, y0, 1),
        (x_R - stem_w, y1 - bar_h, 1),
        (x_L + stem_w, y1 - bar_h, 1),
        (x_L + stem_w, y0, 1),
    ]
    return cw, 920


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

RAD_SIZES = [
    (1, -215.0, 820.0),    # H = 1035 (base radical is 938: -180..758)
    (2, -245.0, 890.0),    # H = 1135
    (3, -270.0, 965.0),    # H = 1235
    (4, -295.0, 1040.0),   # H = 1335
    (5, -315.0, 1115.0),   # H = 1430
]

HBAR_ADV = (440, 720, 1080, 1540, 2080, 2720, 3460)
ARROW_SINGLE_ADV = (980, 1340, 1780, 2320, 2980)
ARROW_BOTH_ADV = (1080, 1420, 1840, 2360, 3000)
OVERBRACE_ADV = (720, 1020, 1380, 1820, 2360, 3020)


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

    # 0. Override base `radical` (-180..758, H = 938) with monoline flat-cut + 38u overhang
    rad0_cw, rad0_adv = _radical_monoline_cw(-180.0, 758.0, r_th)
    rad0_cs = _counter_shear([rad0_cw], k_it, yc_it)
    g_rad0 = _make_glyph(rad0_cs, glyf)
    glyf['radical'] = g_rad0
    hmtx['radical'] = (int(round(rad0_adv)), getattr(g_rad0, 'xMin', 0))

    # 1. Parentheses ( ) — continuous Mulish-profile bow on .size0..size5, plus deep
    # 800-unit curved caps on .bot/.top so assembled parens (> 1430) stay gracefully bowed.
    par_dx_sizes = (142.0, 168.0, 194.0, 218.0, 242.0, 266.0)
    for idx, y0, y1 in VERT_SIZES:
        s = (y1 - y0) / 885.0
        dx_o = par_dx_sizes[idx] + 10.0 * (sv - 1.0)
        w_mid_k = par_w_mid * (1.0 + 0.05 * (s - 1.0))
        w_tip_k = max(44.0, 0.80 * w_mid_k)
        adv_k = par_adv0 + round(par_dx_sizes[idx] - 116.0)
        cw_l = _paren_left_cw(par_x_out, w_mid_k, par_x_out + dx_o, w_tip_k, y0, y1)
        emit(f'parenleft.size{idx}', [cw_l], adv_k)
        emit(f'parenright.size{idx}', _mirror_x([cw_l], 0.5 * adv_k), adv_k)

    par_dx_asm = 278.0 + 12.0 * (sv - 1.0)
    par_w_mid_asm = par_w_mid * 1.06
    par_w_tip_asm = max(44.0, 0.78 * par_w_mid_asm)
    par_adv_asm = par_adv0 + 162
    par_top_cw = _paren_top_cw(par_x_out, par_w_mid_asm, par_x_out + par_dx_asm, par_w_tip_asm, -200.0, -120.0, 680.0)
    par_bot_cw = _mirror_y([par_top_cw], 240.0)[0]
    par_ext_cw = _rect_cw(par_x_out, 0.0, par_x_out + par_w_mid_asm, 500.0)
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
        adv_k = brk_adv0 + arm_dx
        x_arm_k = brk_x_arm + arm_dx
        bl_cw = _bracket_left_cw(brk_x0, brk_x1, x_arm_k, y0, y1, brk_arm_th)
        lc_cw = _lceil_cw(brk_x0, brk_x1, x_arm_k, y0, y1, brk_arm_th)
        lf_cw = _lfloor_cw(brk_x0, brk_x1, x_arm_k, y0, y1, brk_arm_th)
        emit(f'bracketleft.size{idx}', [bl_cw], adv_k)
        emit(f'bracketright.size{idx}', _mirror_x([bl_cw], 0.5 * adv_k), adv_k)
        emit(f'lceil.size{idx}', [lc_cw], adv_k)
        emit(f'rceil.size{idx}', _mirror_x([lc_cw], 0.5 * adv_k), adv_k)
        emit(f'lfloor.size{idx}', [lf_cw], adv_k)
        emit(f'rfloor.size{idx}', _mirror_x([lf_cw], 0.5 * adv_k), adv_k)

    brk_adv_asm = brk_adv0 + 10
    brk_top_cw = _lceil_cw(brk_x0, brk_x1, brk_x_arm + 10.0, 0.0, 600.0, brk_arm_th)
    brk_bot_cw = _lfloor_cw(brk_x0, brk_x1, brk_x_arm + 10.0, 0.0, 600.0, brk_arm_th)
    brk_ext_cw = _rect_cw(brk_x0, 0.0, brk_x1, 500.0)
    emit('bracketleft.bot', [brk_bot_cw], brk_adv_asm)
    emit('bracketleft.ext', [brk_ext_cw], brk_adv_asm)
    emit('bracketleft.top', [brk_top_cw], brk_adv_asm)
    emit('bracketright.bot', _mirror_x([brk_bot_cw], 0.5 * brk_adv_asm), brk_adv_asm)
    emit('bracketright.ext', _mirror_x([brk_ext_cw], 0.5 * brk_adv_asm), brk_adv_asm)
    emit('bracketright.top', _mirror_x([brk_top_cw], 0.5 * brk_adv_asm), brk_adv_asm)

    # 3. Curly braces { } — cut-and-extended directly from Mulish's `braceleft`
    for idx, y0, y1 in VERT_SIZES:
        cy_s = 1.0 + 0.22 * ((y1 - y0 - 885.0) / (1430.0 - 885.0))
        brc_cw = _brace_cut_extend_cw(brc_pts41, y0, y1, cusp_y_scale=cy_s)
        emit(f'braceleft.size{idx}', [brc_cw], brc_adv0)
        emit(f'braceright.size{idx}', _mirror_x([brc_cw], 0.5 * brc_adv0), brc_adv0)

    brc_bot_cw, brc_ext_cw, brc_mid_cw, brc_top_cw = _brace_asm_parts_from_mulish(brc_pts41)
    emit('braceleft.bot', [brc_bot_cw], brc_adv0)
    emit('braceleft.ext', [brc_ext_cw], brc_adv0)
    emit('braceleft.mid', [brc_mid_cw], brc_adv0)
    emit('braceleft.top', [brc_top_cw], brc_adv0)
    emit('braceright.bot', _mirror_x([brc_bot_cw], 0.5 * brc_adv0), brc_adv0)
    emit('braceright.ext', _mirror_x([brc_ext_cw], 0.5 * brc_adv0), brc_adv0)
    emit('braceright.mid', _mirror_x([brc_mid_cw], 0.5 * brc_adv0), brc_adv0)
    emit('braceright.top', _mirror_x([brc_top_cw], 0.5 * brc_adv0), brc_adv0)

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

    # 6. Radicals √ (size1..size5 + 3-part assembly; base `radical` at 938 is step 0)
    for idx, y0, y1 in RAD_SIZES:
        rcw, radv = _radical_monoline_cw(y0, y1, r_th)
        emit(f'radical.size{idx}', [rcw], radv)

    r_bot, r_ext, r_top, r_adv_asm = _radical_asm_parts(r_th)
    emit('radical.bot', [r_bot], r_adv_asm)
    emit('radical.ext', [r_ext], r_adv_asm)
    emit('radical.top', [r_top], r_adv_asm)

    # 7. Display operators: ∑, ∏, ∫ (cohesive compact display triad at 1400..1430)
    sum_cw, sum_adv = _summation_dsp_cw(-300.0, 1100.0, sum_bar_h * 1.12, sum_diag_w * 1.10)
    emit('summation.dsp', [sum_cw], sum_adv)

    prd_cw, prd_adv = _product_dsp_cw(-300.0, 1100.0, prd_stem_w * 1.10, sum_bar_h * 1.12)
    emit('product.dsp', [prd_cw], prd_adv)

    int_s1, _, _, _ = _integral_sculpt_from_mulish(
        int_coords, int_flags, int_xc + 24.0, bar, -250.0, 915.0, fh=1.18, fv=1.12
    )
    int_dsp, int_bot, int_ext, int_top = _integral_sculpt_from_mulish(
        int_coords, int_flags, int_xc + 44.0, bar, -315.0, 1115.0, fh=1.34, fv=1.24
    )
    emit('integral.size1', [int_s1], 650)
    emit('integral.dsp', [int_dsp], 710)
    emit('integral.bot', [int_bot], 710)
    emit('integral.ext', [int_ext], 710)
    emit('integral.top', [int_top], 710)

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

    # Discrete stretchy arrow ladders (.size1..size5) + 2/3-part assembly parts
    for k_i, w_ar in enumerate(ARROW_SINGLE_ADV, start=1):
        rcw = _arrow_rhead_cw(40.0, float(w_ar) - 40.0, axis, bar, sm)
        lcw = _mirror_x([rcw], 0.5 * float(w_ar))[0]
        emit(f'arrowright.size{k_i}', [rcw], w_ar)
        emit(f'arrowleft.size{k_i}', [lcw], w_ar)
    for k_i, w_ab in enumerate(ARROW_BOTH_ADV, start=1):
        bcw = _arrow_both_cw(40.0, float(w_ab) - 40.0, axis, bar, sm)
        emit(f'arrowboth.size{k_i}', [bcw], w_ab)

    ar_rhead = _arrow_rhead_cw(0.0, 460.0, axis, bar, sm)
    ar_lhead = _mirror_x([ar_rhead], 250.0)[0]
    ar_ext = _rect_cw(0.0, axis - 0.5 * bar, 500.0, axis + 0.5 * bar)
    emit('arrow.lhead', [ar_lhead], 500)
    emit('arrow.ext', [ar_ext], 500)
    emit('arrow.rhead', [ar_rhead], 500)

    # Horizontal curly brackets (U+23DE overbrace & U+23DF underbrace + .size1..5 + 5-part assembly)
    r_sc = min(0.86, max(0.70, (bar / (brc_x1 - brc_x0)) ** 0.65))
    ov0_vert = _brace_cut_extend_cw(brc_pts41, 0.0, float(OVERBRACE_ADV[0]), cusp_y_scale=0.92)
    ov0_cw, un0_cw = _rotate_brace_to_over_under(ov0_vert, 0.0, brc_x_tip, r_sc)

    for k_i, w_ob in enumerate(OVERBRACE_ADV[1:], start=1):
        cy_h = min(1.22, 0.96 + 0.26 * ((w_ob - 720.0) / (3020.0 - 720.0)))
        vk = _brace_cut_extend_cw(brc_pts41, 0.0, float(w_ob), cusp_y_scale=cy_h)
        ov_k, un_k = _rotate_brace_to_over_under(vk, 0.0, brc_x_tip, r_sc)
        emit(f'overbrace.size{k_i}', [ov_k], w_ob)
        emit(f'underbrace.size{k_i}', [un_k], w_ob)

    ov_left, un_left = _rotate_brace_to_over_under(brc_bot_cw, 0.0, brc_x_tip, r_sc)
    ov_ext, un_ext = _rotate_brace_to_over_under(brc_ext_cw, 0.0, brc_x_tip, r_sc)
    ov_mid, un_mid = _rotate_brace_to_over_under(brc_mid_cw, 0.0, brc_x_tip, r_sc)
    ov_right, un_right = _rotate_brace_to_over_under(brc_top_cw, 0.0, brc_x_tip, r_sc)
    emit('overbrace.left', [ov_left], 550)
    emit('overbrace.ext', [ov_ext], 500)
    emit('overbrace.mid', [ov_mid], 800)
    emit('overbrace.right', [ov_right], 550)
    emit('underbrace.left', [un_left], 550)
    emit('underbrace.ext', [un_ext], 500)
    emit('underbrace.mid', [un_mid], 800)
    emit('underbrace.right', [un_right], 550)

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

    # 1. MathConstants (all 56 OpenType MATH constants; Upright == Italic at every weight)
    mc = ot.MathConstants()
    mc.ScriptPercentScaleDown = 68
    mc.ScriptScriptPercentScaleDown = 53
    mc.DelimitedSubFormulaMinHeight = 1320
    mc.DisplayOperatorMinHeight = 1400

    dR = R - 53
    dR_pos = max(0, dR)
    mvr_vals = {
        'MathLeading': 150,
        'AxisHeight': axis,
        'AccentBaseHeight': xh_os2,
        'FlattenedAccentBaseHeight': cap_os2 - 1,
        'SubscriptShiftDown': 195,
        'SubscriptTopMax': 380,
        'SubscriptBaselineDropMin': 140,
        'SuperscriptShiftUp': 400,
        'SuperscriptShiftUpCramped': 300,
        'SuperscriptBottomMin': 135,
        'SuperscriptBaselineDropMax': 70,
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
        'RadicalVerticalGap': 77 + round(0.45 * dR_pos),
        'RadicalDisplayStyleVerticalGap': 167 + round(0.45 * dR_pos),
        'RadicalRuleThickness': R,
        'RadicalExtraAscender': R,
        'RadicalKernBeforeDegree': 55,
        'RadicalKernAfterDegree': -415,
    }
    for k, v in mvr_vals.items():
        setattr(mc, k, _mvr(v))
    mc.RadicalDegreeBottomRaisePercent = 55

    # 2. MathVariants (VertGlyphConstruction & HorizGlyphConstruction)
    # Every AdvanceMeasurement and connector length is a plain style-invariant uint16.
    STD_ADV = (965, 1060, 1155, 1250, 1340, 1430)
    ANG_ADV = (885, 995, 1105, 1215, 1325, 1430)
    SLASH_ADV = (930, 1030, 1130, 1230, 1330, 1430)
    RAD_STEP_ADV = (1035, 1135, 1235, 1335, 1430)

    def std_sizes(base_g, prefix, base_adv=885, advs=STD_ADV):
        return [_vrec(base_g, base_adv)] + [_vrec(f'{prefix}.size{i}.math_table', advs[i]) for i in range(len(advs))]

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
            _prec(f'{prefix}.bot.math_table', 0, 360, 550, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.mid.math_table', 220, 220, 800, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.top.math_table', 360, 0, 550, 0),
        ]
        a.PartCount = 5
        return a

    def asm_horiz_brace(prefix):
        a = ot.GlyphAssembly()
        a.ItalicsCorrection = _mvr(0)
        a.PartRecords = [
            _prec(f'{prefix}.left.math_table', 0, 360, 550, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.mid.math_table', 220, 220, 800, 0),
            _prec(f'{prefix}.ext.math_table', 500, 500, 500, 1),
            _prec(f'{prefix}.right.math_table', 360, 0, 550, 0),
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

    rad_vars = [_vrec('radical', 938)] + [_vrec(f'radical.size{i}.math_table', RAD_STEP_ADV[i - 1]) for i in range(1, 6)]

    vert_specs = {
        'parenleft': (std_sizes('parenleft', 'parenleft'), asm3('parenleft', bot_end=80, bot_full=880, ext_full=500, top_start=80, top_full=880)),
        'parenright': (std_sizes('parenright', 'parenright'), asm3('parenright', bot_end=80, bot_full=880, ext_full=500, top_start=80, top_full=880)),
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
        'slash': (std_sizes('slash', 'slash', base_adv=800, advs=SLASH_ADV), None),
        'backslash': (std_sizes('backslash', 'backslash', base_adv=800, advs=SLASH_ADV), None),
        'radical': (rad_vars, asm3('radical', bot_end=380, bot_full=900, ext_full=500, top_start=420, top_full=520)),
        'summation': ([_vrec('summation', 885), _vrec('summation.dsp.math_table', 1400)], None),
        'product': ([_vrec('product', 885), _vrec('product.dsp.math_table', 1400)], None),
        'integral': ([_vrec('integral', 905),
                      _vrec('integral.size1.math_table', 1165),
                      _vrec('integral.dsp.math_table', 1430)],
                     asm3('integral', bot_end=340, bot_full=620, ext_full=500, top_start=340, top_full=620,
                          ic=135)),
    }
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
            parts.append(_prec('arrow.lhead.math_table', 0, 340, 500, 0))
        parts.append(_prec('arrow.ext.math_table', 500, 500, 500, 1))
        if right_h:
            parts.append(_prec('arrow.rhead.math_table', 340, 0, 500, 0))
        a.PartRecords = parts
        a.PartCount = len(parts)
        return a

    ar_r_vars = [_vrec('arrowright', 660)] + [_vrec(f'arrowright.size{k}.math_table', w) for k, w in enumerate(ARROW_SINGLE_ADV, 1)]
    ar_l_vars = [_vrec('arrowleft', 660)] + [_vrec(f'arrowleft.size{k}.math_table', w) for k, w in enumerate(ARROW_SINGLE_ADV, 1)]
    ar_b_vars = [_vrec('arrowboth', 840)] + [_vrec(f'arrowboth.size{k}.math_table', w) for k, w in enumerate(ARROW_BOTH_ADV, 1)]

    ov_vars = [_vrec('uni23DE', OVERBRACE_ADV[0])] + [_vrec(f'overbrace.size{k}.math_table', w) for k, w in enumerate(OVERBRACE_ADV[1:], 1)]
    un_vars = [_vrec('uni23DF', OVERBRACE_ADV[0])] + [_vrec(f'underbrace.size{k}.math_table', w) for k, w in enumerate(OVERBRACE_ADV[1:], 1)]

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

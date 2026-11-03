"""Module games (GM1..GM4, SC2): games, chess, dice, Go markers, and astronomical signs.

Adds 29 encoded symbols across five repertoire groups plus one unencoded optical
subscript glyph (30 glyphs total), upright in both roman and italic styles and
topology-locked across all 14 static instances (Light..Black, roman and italic)
as well as across continuous variable-font weight interpolation (300..900):

- GM1 Chess figurines (U+2654..265F: uni2654..uni265F, 12 glyphs):
  White and Black King, Queen, Rook, Bishop, Knight, and Pawn. Adapted from
  SIL OFL 1.1 Noto Sans Symbols 2 v2.008 Staunton contours, scaled to Torchlette
  Sans cap height (0..705 with subtle optical overshoot on curved pedestals and
  crowns), given proportional sidebearings for algebraic notation (2. Nf3 nc6).
  Per executive directive ("Please just use the v1 and move on, this is taking
  too long. Make it always regular, weight does nothing"), all 12 figurines are
  locked to the original v1 Regular master outlines across all weights and styles:
  weight does nothing, producing zero deltas between static masters and eliminating
  all intermediate-weight variable font counter crowding or topology flags.

- GM2 Draughts / checkers (U+26C0..26C3: uni26C0..uni26C3, 4 glyphs):
  White Man, White King, Black Man, and Black King drawn as wide 3D perspective
  cylindrical pucks with uniform stroke weights around both front and back arcs of
  the top-face rings, side walls, bottom rims, and King seam.

- GM3 Die faces 1..6 (U+2680..2685: uni2680..uni2685, 6 glyphs):
  Rounded-square cap-height die frames (704 x 706) with inward-balanced circular
  pips (d_diag = 138, dx6 = 130, dy6 = 158) whose boldness scales smoothly with SV
  (SV ** 0.44 on 1-pip, SV ** 0.38 on 2..6-pip) so pips hold their weight in Black.

- GM4 Go stone markers (U+2686..2689: uni2686..uni2689, 4 glyphs):
  Unicode 15.1 semantics harmonized 1:1 with ui.py's U+25CB / U+25CF outer stone
  geometry (R = 361, cy = 353, advance = 843, ring = 59 * SH), with pips scaling
  up smoothly toward heavy weights (SH ** 0.40..0.48) to balance the thick ring
  and solid fill.

- SC2 Astronomical signs (U+2609, U+263D, U+2641 + uni2609.subs.games, 4 glyphs):
  Solar circumpunct (U+2609, matching U+25CB outer ring with punchy central dot),
  its optical subscript uni2609.subs.games (-7..433, R = 220, thickened ring
  50 * SH ** 0.78 and bold dot 56 * SH ** 0.34 matching M's optical density across
  Light..Black), analytical pointed-horn First Quarter Moon (U+263D) with open
  crescent counter, and Earth / globus cruciger (U+2641) from SIL OFL 1.1 Noto
  Sans Symbols [wght] v2.003.

Features:
- GSUB subs, sinf (lookup GAMES_SUBS): uni2609 -> uni2609.subs.games.
- GSUB calt (lookup GAMES_SOLAR): contextual [M L R M.sc L.sc R.sc] uni2609' ->
  uni2609.subs.games for astrophysical notation (M_sun, L_sun, R_sun).
- GPOS kern (lookup GAMES_KERN): optical kerning for M/R before uni2609.subs.games.

OFL 1.1 attribution:
- Noto Sans Symbols 2 Regular, Version 2.008: Copyright 2022 The Noto Project
  Authors (https://github.com/notofonts/symbols), SIL Open Font License 1.1
  (no Reserved Font Name). Used for U+2654..265F master contours.
- Noto Sans Symbols [wght], Version 2.003: Copyright 2022 The Noto Project
  Authors (https://github.com/notofonts/symbols), SIL Open Font License 1.1
  (no Reserved Font Name). Used for U+2641 variable master endpoints.
"""
from array import array
import math
import os
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates

K_QUAD = math.sqrt(2.0) - 1.0  # 0.41421356237: exact 12-point TrueType circle constant

ENCODED_ORDER = (
    tuple(range(0x2654, 0x2660))  # GM1: chess figurines
    + tuple(range(0x26C0, 0x26C4))  # GM2: draughts / checkers
    + tuple(range(0x2680, 0x2686))  # GM3: die faces 1..6
    + tuple(range(0x2686, 0x268A))  # GM4: Go stone markers
    + (0x2609, 0x263D, 0x2641)      # SC2: Sun, Moon, Earth
)
SUB_SUN = "uni2609.subs.games"

# Weight tracking (all smooth analytical functions of SV and SH; zero weight conditionals).
RING = 59.0          # ui.py's U+25CB ring width in Regular; follows SH in every weight
SUB_RING = 50.0      # subscript sun ring width in Regular (matched optically to inferior digits / M)
SUB_RING_K = 0.78    # subscript sun ring tracks SH ** SUB_RING_K into Bold/Black
SUB_DOT = 56.0       # subscript sun dot radius in Regular
SUB_DOT_K = 0.34     # subscript sun dot tracks SH ** SUB_DOT_K, keeping >= 47u white annulus in Black
_DR_K = 0.55         # draughts: uniform stroke exponent across SV
_DIE_FRAME_K = 0.66  # dice: frame stroke exponent across SV
_DIE_PIP1_K = 0.44   # dice: 1-pip radius exponent across SV
_DIE_PIP_K = 0.38    # dice: 2..6-pip radius exponent across SV


def _wlerp(sv, v_light, v_reg, v_bold, v_black):
    """Smooth interpolation across Torchlette Sans stem scale SV (0.758..2.470) for Earth masters."""
    if sv <= 1.0:
        t = max(0.0, (sv - 0.758) / (1.0 - 0.758))
        return v_light + t * (v_reg - v_light)
    if sv <= 1.803:
        t = (sv - 1.0) / (1.803 - 1.0)
        return v_reg + t * (v_bold - v_reg)
    t = min(1.2, (sv - 1.803) / (2.470 - 1.803))
    return v_bold + t * (v_black - v_bold)


def _to_glyph(contours, dx=0):
    """Build a TrueType simple Glyph with exact contour endpoints, flags, and empty program."""
    g = Glyph()
    g.numberOfContours = len(contours)
    pts, flgs, ends = [], [], []
    k = -1
    for c in contours:
        for x, y, on in c:
            pts.append((int(round(x)) + dx, int(round(y))))
            flgs.append(1 if on else 0)
        k += len(c)
        ends.append(k)
    g.coordinates = GlyphCoordinates(pts)
    g.flags = array("B", flgs)
    g.endPtsOfContours = ends
    g.program = ttProgram.Program()
    return g


def _rev_contour(c):
    return [list(c[0])] + [list(p) for p in reversed(c[1:])]


def _shift_to_sb(contours, sb=48):
    xmin = min(round(p[0]) for c in contours for p in c)
    xmax = max(round(p[0]) for c in contours for p in c)
    dx = sb - xmin
    out = [[[round(p[0]) + dx, round(p[1]), p[2]] for p in c] for c in contours]
    return out, (xmax - xmin) + 2 * sb, 352.5


def _q_ellipse(cx, cy, rx, ry, cw=True):
    """12-point TrueType quadratic ellipse with 4 cardinal extrema and 0.0 deg kinks."""
    cx, cy = round(cx), round(cy)
    rx, ry = round(rx), round(ry)
    ax, ay = round(K_QUAD * rx), round(K_QUAD * ry)
    pts_cw = [
        [cx + rx, cy, True],
        [cx + rx, cy - ay, False],
        [cx + ax, cy - ry, False],
        [cx, cy - ry, True],
        [cx - ax, cy - ry, False],
        [cx - rx, cy - ay, False],
        [cx - rx, cy, True],
        [cx - rx, cy + ay, False],
        [cx - ax, cy + ry, False],
        [cx, cy + ry, True],
        [cx + ax, cy + ry, False],
        [cx + rx, cy + ay, False],
    ]
    return pts_cw if cw else _rev_contour(pts_cw)


def _q_round_rect(x0, y0, x1, y1, r, cw=True):
    """16-point TrueType quadratic rounded rectangle with 0.0 deg kinks."""
    x0, y0, x1, y1, r = round(x0), round(y0), round(x1), round(y1), round(r)
    a = round(K_QUAD * r)
    pts_cw = [
        [x0 + r, y1, True],
        [x1 - r, y1, True],
        [x1 - r + a, y1, False],
        [x1, y1 - r + a, False],
        [x1, y1 - r, True],
        [x1, y0 + r, True],
        [x1, y0 + r - a, False],
        [x1 - r + a, y0, False],
        [x1 - r, y0, True],
        [x0 + r, y0, True],
        [x0 + r - a, y0, False],
        [x0, y0 + r - a, False],
        [x0, y0 + r, True],
        [x0, y1 - r, True],
        [x0, y1 - r + a, False],
        [x0 + r - a, y1, False],
    ]
    return pts_cw if cw else _rev_contour(pts_cw)



def _q_cylinder_outer(cx, rx, ry, yc_bot, yc_top):
    """14-point CW outer silhouette of a 3D perspective cylindrical game disc."""
    cx, rx, ry = round(cx), round(rx), round(ry)
    yc_bot, yc_top = round(yc_bot), round(yc_top)
    ax, ay = round(K_QUAD * rx), round(K_QUAD * ry)
    return [
        [cx - rx, yc_bot, True],
        [cx - rx, yc_top, True],
        [cx - rx, yc_top + ay, False],
        [cx - ax, yc_top + ry, False],
        [cx, yc_top + ry, True],
        [cx + ax, yc_top + ry, False],
        [cx + rx, yc_top + ay, False],
        [cx + rx, yc_top, True],
        [cx + rx, yc_bot, True],
        [cx + rx, yc_bot - ay, False],
        [cx + ax, yc_bot - ry, False],
        [cx, yc_bot - ry, True],
        [cx - ax, yc_bot - ry, False],
        [cx - rx, yc_bot - ay, False],
    ]


def _ell_lower_arc(cx, yc, rx, ry, hw, left_to_right=True):
    """Exact implied-midpoint lower elliptical arc for |x - cx| <= hw (0.0 deg kinks)."""
    th = math.asin(min(0.995, hw / rx))
    dm = th / 4.0
    inv_c = 1.0 / math.cos(dm)

    def pt_off(a):
        return [round(cx + rx * math.sin(a) * inv_c), round(yc - ry * math.cos(a) * inv_c), False]

    pts = [
        [round(cx - hw), round(yc - ry * math.cos(th)), True],
        pt_off(-3.0 * dm),
        pt_off(-1.0 * dm),
        [round(cx), round(yc - ry), True],
        pt_off(1.0 * dm),
        pt_off(3.0 * dm),
        [round(cx + hw), round(yc - ry * math.cos(th)), True],
    ]
    return pts if left_to_right else [list(p) for p in reversed(pts)]


def _q_skirt_exact(cx, rx, ry, hw, yc_lo, yc_hi, cw=False):
    """14-point front skirt cutout bounded by exact parallel lower arcs of (rx, ry)."""
    bot = _ell_lower_arc(cx, yc_lo, rx, ry, hw, left_to_right=True)
    top = _ell_lower_arc(cx, yc_hi, rx, ry, hw, left_to_right=False)
    pts_ccw = [top[-1], *bot, *top[:-1]]
    return pts_ccw if not cw else _rev_contour(pts_ccw)


def _ell_arc_angles(cx, cy, rx, ry, a0, a1, n_quads):
    """Implied-midpoint quadratic spline from angle a0 to a1 on (cx + rx cos a, cy + ry sin a)."""
    da = (a1 - a0) / (2.0 * n_quads)
    inv_c = 1.0 / math.cos(da)
    pts = [[round(cx + rx * math.cos(a0)), round(cy + ry * math.sin(a0)), True]]
    for k in range(n_quads):
        am = a0 + (2 * k + 1) * da
        pts.append([round(cx + rx * math.cos(am) * inv_c), round(cy + ry * math.sin(am) * inv_c), False])
    pts.append([round(cx + rx * math.cos(a1)), round(cy + ry * math.sin(a1)), True])
    return pts


def _contour_area(c):
    n = len(c)
    return sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(n)) / 2.0


def _turn_deg(a, p, b):
    ux, uy = p[0] - a[0], p[1] - a[1]
    vx, vy = b[0] - p[0], b[1] - p[1]
    if (ux == 0 and uy == 0) or (vx == 0 and vy == 0):
        return 180.0
    return abs(math.degrees(math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)))



def _smooth_and_snap(c, master_c):
    """Restore G1 tangent collinearity on integer coordinates without changing point count."""
    n = len(c)
    out = [list(p) for p in c]
    for _ in range(12):
        for i in range(n):
            a, p, b = out[i - 1], out[i], out[(i + 1) % n]
            if not p[2] or (a[2] and b[2]):
                continue
            t = _turn_deg(a, p, b)
            mt = _turn_deg(master_c[i - 1], master_c[i], master_c[(i + 1) % n])
            if mt < 30.0 or (2.5 < t < 30.5):
                if not a[2] and not b[2]:
                    dx, dy = b[0] - a[0], b[1] - a[1]
                    L2 = dx * dx + dy * dy
                    if L2 > 1e-6:
                        r = max(0.2, min(0.8, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
                        p[0], p[1] = a[0] + r * dx, a[1] + r * dy
                else:
                    h, o = (b, a) if a[2] else (a, b)
                    dx, dy = p[0] - o[0], p[1] - o[1]
                    L = math.hypot(dx, dy)
                    rh = max(6.0, math.hypot(h[0] - p[0], h[1] - p[1]))
                    if L > 1e-6:
                        h[0], h[1] = p[0] + (dx / L) * rh, p[1] + (dy / L) * rh
    snapped = [[int(round(x)), int(round(y)), on] for x, y, on in out]
    for _ in range(14):
        fixed_any = False
        for i in range(n):
            a, p, b = snapped[i - 1], snapped[i], snapped[(i + 1) % n]
            if not p[2] or (a[2] and b[2]):
                continue
            t0 = _turn_deg(a, p, b)
            if 2.8 < t0 < 30.1:
                if not a[2] and not b[2]:
                    best_q = min(
                        [(p[0] + dx, p[1] + dy) for dx in range(-4, 5) for dy in range(-4, 5)],
                        key=lambda q: (
                            0 if _turn_deg(a, q, b) <= 2.7 else round(_turn_deg(a, q, b), 2),
                            math.hypot(q[0] - out[i][0], q[1] - out[i][1]),
                        ),
                    )
                    if _turn_deg(a, best_q, b) <= 2.7:
                        if list(best_q) != p[:2]:
                            snapped[i][0], snapped[i][1] = best_q
                            fixed_any = True
                    else:
                        bx_even = b[0] if (a[0] + b[0]) % 2 == 0 else b[0] + (1 if out[(i + 1) % n][0] >= b[0] else -1)
                        by_even = b[1] if (a[1] + b[1]) % 2 == 0 else b[1] + (1 if out[(i + 1) % n][1] >= b[1] else -1)
                        b[0], b[1] = bx_even, by_even
                        snapped[i][0], snapped[i][1] = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2
                        fixed_any = True
                else:
                    hi = (i + 1) % n if a[2] else (i - 1) % n
                    o = a if a[2] else b
                    h = snapped[hi]
                    other_on = snapped[(hi + 1) % n if a[2] else (hi - 1) % n]
                    other_far = snapped[(hi + 2) % n if a[2] else (hi - 2) % n]
                    best_pair = None
                    for pdx in (-1, 0, 1):
                        for pdy in (-1, 0, 1):
                            if abs(out[i][1]) < 0.5 and pdy != 0:
                                continue
                            qp = (p[0] + pdx, p[1] + pdy)
                            prev_o = snapped[(i - 2) % n if a[2] else (i + 2) % n]
                            po_pen = 0.0
                            if not prev_o[2]:
                                to_deg = _turn_deg(prev_o, o, qp) if a[2] else _turn_deg(qp, o, prev_o)
                                if 2.8 < to_deg < 30.0:
                                    po_pen = to_deg * 10.0
                            for hdx in range(-5, 6):
                                for hdy in range(-5, 6):
                                    qh = (h[0] + hdx, h[1] + hdy)
                                    if (
                                        math.hypot(qh[0] - qp[0], qh[1] - qp[1]) < 4.5
                                        or math.hypot(qh[0] - other_on[0], qh[1] - other_on[1]) < 4.5
                                    ):
                                        continue
                                    t1 = _turn_deg(o, qp, qh) if a[2] else _turn_deg(qh, qp, o)
                                    pen = po_pen + (0.0 if t1 <= 2.7 else t1 * 10.0)
                                    t2 = _turn_deg(qh, other_on, other_far) if a[2] else _turn_deg(other_far, other_on, qh)
                                    if 2.8 < t2 < 30.0:
                                        pen += t2 * 10.0
                                    score = (
                                        round(pen, 2),
                                        abs(pdx) + abs(pdy),
                                        math.hypot(qh[0] - out[hi][0], qh[1] - out[hi][1])
                                        + math.hypot(qp[0] - out[i][0], qp[1] - out[i][1]),
                                    )
                                    if best_pair is None or score < best_pair[0]:
                                        best_pair = (score, qp, qh)
                    if best_pair:
                        _, qp, qh = best_pair
                        if list(qp) != p[:2] or list(qh) != h[:2]:
                            snapped[i][0], snapped[i][1] = qp
                            snapped[hi][0], snapped[hi][1] = qh
                            fixed_any = True
        if not fixed_any:
            break
    return snapped



def _build_chess(cp, sv=1.0, sb=48, style=None):
    """V1 Staunton chess figurines (U+2654..265F) fixed to Regular outline across all weights."""
    contours, adv, yc = CHESS_V1_REGULAR[cp]
    return [[list(p) for p in c] for c in contours], adv, yc

def _build_checker(cp, sv):
    """Build 3D perspective draughts pucks with uniform stroke weight around all rings and walls."""
    sb = 52
    rx = 352
    cx = sb + rx
    adv = 2 * rx + 2 * sb  # 808
    is_king = cp in (0x26C1, 0x26C3)
    is_black = cp in (0x26C2, 0x26C3)
    ry = 138 if is_king else 148
    yc_bot = -6 + ry
    yc_top = (711 - ry) if is_king else (470 - ry)

    th = round(39.0 * (sv ** _DR_K))
    tv = round(29.0 * (sv ** _DR_K))
    contours = [_q_cylinder_outer(cx, rx, ry, yc_bot, yc_top)]

    if not is_black:
        # Outer top-face hole: front and back arcs both have exact vertical thickness tv
        # because the front skirt cutout below terminates right on the outer top ellipse!
        contours.append(_q_ellipse(cx, yc_top, rx - th, ry - tv, cw=False))
        rx_in = round(0.47 * rx)
        ry_in = round(0.47 * ry)
        th_in = round(35.0 * (sv ** 0.52))
        tv_in = round(25.0 * (sv ** 0.52))
        contours.append(_q_ellipse(cx, yc_top, rx_in, ry_in, cw=True))
        contours.append(_q_ellipse(cx, yc_top, rx_in - th_in, ry_in - tv_in, cw=False))

        hw = rx - th
        if not is_king:
            contours.append(_q_skirt_exact(cx, rx, ry, hw, yc_bot + tv, yc_top, cw=False))
        else:
            yc_mid = (yc_bot + tv + yc_top) / 2.0
            contours.append(_q_skirt_exact(cx, rx, ry, hw, yc_mid + 0.5 * tv, yc_top, cw=False))
            contours.append(_q_skirt_exact(cx, rx, ry, hw, yc_bot + tv, yc_mid - 0.5 * tv, cw=False))
    else:
        pad_x = round(48.0 * (sv ** 0.45))
        pad_y = round(32.0 * (sv ** 0.45))
        gw_x = round(38.0 * (sv ** -0.18))
        gw_y = round(25.0 * (sv ** -0.18))
        contours.append(_q_ellipse(cx, yc_top, rx - pad_x, ry - pad_y, cw=False))
        contours.append(_q_ellipse(cx, yc_top, rx - pad_x - gw_x, ry - pad_y - gw_y, cw=True))
        rx_c = round(0.36 * rx)
        ry_c = round(0.36 * ry)
        gw_cx = round(0.90 * gw_x)
        gw_cy = round(0.90 * gw_y)
        contours.append(_q_ellipse(cx, yc_top, rx_c, ry_c, cw=False))
        contours.append(_q_ellipse(cx, yc_top, rx_c - gw_cx, ry_c - gw_cy, cw=True))
        if is_king:
            hw = rx - pad_x
            yc_mid = (yc_bot + yc_top) / 2.0
            gh = round(28.0 * (sv ** -0.18))
            contours.append(_q_skirt_exact(cx, rx, ry, hw, yc_mid - 0.5 * gh, yc_mid + 0.5 * gh, cw=False))
    return contours, adv, 352.5 if is_king else 232.0


def _build_die(cp, sv):
    """Build cap-height die faces with inward-centered pips and strong heavy-weight presence."""
    sb, w = 56, 704
    x0, x1 = sb, sb + w
    y0, y1 = 0, 706
    cx, cy = 408, 353
    adv = w + 2 * sb  # 816
    tf = round(48.0 * (sv ** _DIE_FRAME_K))
    r_out = 58
    r_in = max(20, round(r_out - tf * 0.52))
    contours = [
        _q_round_rect(x0, y0, x1, y1, r_out, cw=True),
        _q_round_rect(x0 + tf, y0 + tf, x1 - tf, y1 - tf, r_in, cw=False),
    ]
    n_pips = cp - 0x2680 + 1
    rp = round(56.0 * (sv ** _DIE_PIP1_K)) if n_pips == 1 else round(47.0 * (sv ** _DIE_PIP_K))
    d_diag = 138
    dx6, dy6 = 130, 158
    pips = {
        1: [(cx, cy)],
        2: [(cx - d_diag, cy + d_diag), (cx + d_diag, cy - d_diag)],
        3: [(cx - d_diag, cy + d_diag), (cx, cy), (cx + d_diag, cy - d_diag)],
        4: [(cx - d_diag, cy + d_diag), (cx + d_diag, cy + d_diag),
            (cx - d_diag, cy - d_diag), (cx + d_diag, cy - d_diag)],
        5: [(cx - d_diag, cy + d_diag), (cx + d_diag, cy + d_diag), (cx, cy),
            (cx - d_diag, cy - d_diag), (cx + d_diag, cy - d_diag)],
        6: [(cx - dx6, cy + dy6), (cx + dx6, cy + dy6),
            (cx - dx6, cy),       (cx + dx6, cy),
            (cx - dx6, cy - dy6), (cx + dx6, cy - dy6)],
    }[n_pips]
    for px, py in pips:
        contours.append(_q_ellipse(px, py, rp, rp, cw=True))
    return contours, adv, 353.0


def _build_go(cp, sv, sh):
    """Build Go stone markers with pips scaled smoothly upward in heavy weights."""
    R = 361
    cx, cy, adv = 421, 353, 843
    rt = round(RING * sh)  # ui.py's U+25CB ring in every weight
    if cp == 0x2686:
        rd = round(61.0 * (sh ** 0.48))
        dx_p = round(112.0 - 12.0 * (sh - 1.0))
        return [
            _q_ellipse(cx, cy, R, R, cw=True),
            _q_ellipse(cx, cy, R - rt, R - rt, cw=False),
            _q_ellipse(cx + dx_p, cy, rd, rd, cw=True),
        ], adv, 353.0
    if cp == 0x2687:
        rd = round(56.0 * (sh ** 0.46))
        dx_p = round(116.0 - 9.0 * (sh - 1.0))
        return [
            _q_ellipse(cx, cy, R, R, cw=True),
            _q_ellipse(cx, cy, R - rt, R - rt, cw=False),
            _q_ellipse(cx - dx_p, cy, rd, rd, cw=True),
            _q_ellipse(cx + dx_p, cy, rd, rd, cw=True),
        ], adv, 353.0
    if cp == 0x2688:
        rd = round(66.0 * (sh ** 0.42))
        return [
            _q_ellipse(cx, cy, R, R, cw=True),
            _q_ellipse(cx + 124, cy, rd, rd, cw=False),
        ], adv, 353.0
    rd = round(61.0 * (sh ** 0.40))
    return [
        _q_ellipse(cx, cy, R, R, cw=True),
        _q_ellipse(cx - 128, cy, rd, rd, cw=False),
        _q_ellipse(cx + 128, cy, rd, rd, cw=False),
    ], adv, 353.0


def _build_sun(sv, sh, sub=False):
    """Build solar circumpunct U+2609 and optical subscript uni2609.subs.games."""
    if not sub:
        R = 361
        cx, cy, adv = 421, 353, 843
        rt = round(RING * sh)
        rd = round(64.0 * (sh ** 0.80))
        return [
            _q_ellipse(cx, cy, R, R, cw=True),
            _q_ellipse(cx, cy, R - rt, R - rt, cw=False),
            _q_ellipse(cx, cy, rd, rd, cw=True),
        ], adv, 353.0
    R, sb = 220, 26
    cx, cy = sb + R, 213
    adv = 2 * R + 2 * sb  # 492
    rt = round(SUB_RING * (sh ** SUB_RING_K))
    rd = round(SUB_DOT * (sh ** SUB_DOT_K))
    return [
        _q_ellipse(cx, cy, R, R, cw=True),
        _q_ellipse(cx, cy, R - rt, R - rt, cw=False),
        _q_ellipse(cx, cy, rd, rd, cw=True),
    ], adv, 213.0


def _build_moon(sv, sb=52):
    """Build First Quarter Moon (U+263D) with clean pointed crescent horns and open counter."""
    cy = 352.5
    rx_out, ry_out = 336.0, 358.5
    tw = 49.0 * (sv ** 0.72)
    belly = 2.0 * tw + 102.0 * (sv ** -0.45)

    a_out = math.radians(113.0)
    cx_out = 0.0
    x_horn = cx_out + rx_out * math.cos(a_out)
    y_horn_dy = ry_out * math.sin(a_out)
    x_belly_in = cx_out + rx_out - belly
    ry_in = 368.0
    sin_in = y_horn_dy / ry_in
    cos_in = math.sqrt(1.0 - sin_in * sin_in)
    rx_in = (x_belly_in - x_horn) / (1.0 - cos_in)
    cx_in = x_belly_in - rx_in
    a_in = math.asin(sin_in)

    p_bot_to_s = _ell_arc_angles(cx_out, cy, rx_out, ry_out, -a_out, -0.5 * math.pi, 1)
    p_s_to_e = _ell_arc_angles(cx_out, cy, rx_out, ry_out, -0.5 * math.pi, 0.0, 2)
    p_e_to_n = _ell_arc_angles(cx_out, cy, rx_out, ry_out, 0.0, 0.5 * math.pi, 2)
    p_n_to_top = _ell_arc_angles(cx_out, cy, rx_out, ry_out, 0.5 * math.pi, a_out, 1)
    p_top_to_mid = _ell_arc_angles(cx_in, cy, rx_in, ry_in, a_in, 0.0, 2)
    p_mid_to_bot = _ell_arc_angles(cx_in, cy, rx_in, ry_in, 0.0, -a_in, 2)
    c_outer_ccw = (
        p_bot_to_s[:-1] + p_s_to_e[:-1] + p_e_to_n[:-1] + p_n_to_top[:-1]
        + p_top_to_mid[:-1] + p_mid_to_bot[:-1]
    )
    c_outer = _rev_contour(c_outer_ccw)

    tw_out = tw
    tw_in = 0.92 * tw
    rx_c_out, ry_c_out = rx_out - tw_out, ry_out - tw_out
    rx_c_in, ry_c_in = rx_in + tw_in, ry_in + tw_in

    lo, hi = 0.0, a_out
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        ya = ry_c_out * math.sin(mid)
        if ya >= ry_c_in:
            hi = mid
            continue
        xo = cx_out + rx_c_out * math.cos(mid)
        xi = cx_in + rx_c_in * math.sqrt(max(0.0, 1.0 - (ya / ry_c_in) ** 2))
        if xo > xi:
            lo = mid
        else:
            hi = mid
    a_cout = 0.5 * (lo + hi)
    yc_tip = ry_c_out * math.sin(a_cout)
    a_cin = math.asin(min(1.0, yc_tip / ry_c_in))

    c_bot_to_e = _ell_arc_angles(cx_out, cy, rx_c_out, ry_c_out, -a_cout, 0.0, 2)
    c_e_to_top = _ell_arc_angles(cx_out, cy, rx_c_out, ry_c_out, 0.0, a_cout, 2)
    c_top_to_m = _ell_arc_angles(cx_in, cy, rx_c_in, ry_c_in, a_cin, 0.0, 2)
    c_m_to_bot = _ell_arc_angles(cx_in, cy, rx_c_in, ry_c_in, 0.0, -a_cin, 2)
    c_e_to_top[-1] = list(c_top_to_m[0])
    c_m_to_bot[-1] = list(c_bot_to_e[0])
    c_inner_ccw = c_bot_to_e[:-1] + c_e_to_top[:-1] + c_top_to_m[:-1] + c_m_to_bot[:-1]

    return _shift_to_sb([c_outer, c_inner_ccw], sb=sb)


def _build_ns1(pair, sv, sb=52):
    c_lo, c_hi = pair
    t = _wlerp(sv, 0.02, 0.26, 0.72, 1.0)
    interp = []
    for cl, ch in zip(c_lo, c_hi):
        c = [
            [cl[i][0] + t * (ch[i][0] - cl[i][0]), cl[i][1] + t * (ch[i][1] - cl[i][1]), cl[i][2]]
            for i in range(len(cl))
        ]
        interp.append(_smooth_and_snap(c, cl))
    return _shift_to_sb(interp, sb=sb)




def _build_all(sv, sh=None, style=None):
    sh = sv if sh is None else sh
    built = {}
    for cp in ENCODED_ORDER:
        name = f"uni{cp:04X}"
        if 0x2654 <= cp <= 0x265F:
            built[name] = (_build_chess(cp, 1.0), cp)
        elif 0x26C0 <= cp <= 0x26C3:
            built[name] = (_build_checker(cp, sv), cp)
        elif 0x2680 <= cp <= 0x2685:
            built[name] = (_build_die(cp, sv), cp)
        elif 0x2686 <= cp <= 0x2689:
            built[name] = (_build_go(cp, sv, sh), cp)
        elif cp == 0x2609:
            built[name] = (_build_sun(sv, sh, sub=False), cp)
        elif cp == 0x263D:
            built[name] = (_build_moon(sv), cp)
        elif cp == 0x2641:
            built[name] = (_build_ns1(EARTH_PAIR, sv), cp)
    built[SUB_SUN] = (_build_sun(sv, sh, sub=True), None)
    return built


def glyphs(ctx):
    built = _build_all(ctx.SV, ctx.SH)
    ctx._games_built = built
    order = list(ctx.font.getGlyphOrder())
    for name, ((contours, adv, _yc), _cp) in built.items():
        if name not in order:
            order.append(name)
        g = _to_glyph(contours)
        g.recalcBounds(ctx.glyf)
        ctx.glyf[name] = g
        ctx.hmtx[name] = (int(adv), int(g.xMin))
        ctx.GDEF_CLASS[name] = 1
    ctx.font.setGlyphOrder(order)
    for name, (_geom, cp) in built.items():
        if cp is not None:
            ctx.map(cp, name)
    ctx.log(f"{len(built)} glyphs ({len(ENCODED_ORDER)} encoded + {SUB_SUN})")


def features(ctx):
    solar_bases = [g for g in ("M", "L", "R", "M.sc", "L.sc", "R.sc") if g in ctx.glyf.glyphs]
    base_cls = " ".join(solar_bases)
    ctx.gsub(
        f"""
lookup GAMES_SUBS {{
    sub uni2609 by {SUB_SUN};
}} GAMES_SUBS;

lookup GAMES_SOLAR {{
    sub [{base_cls}] uni2609' lookup GAMES_SUBS;
}} GAMES_SOLAR;

feature subs {{ lookup GAMES_SUBS; }} subs;
feature sinf {{ lookup GAMES_SUBS; }} sinf;
feature calt {{ lookup GAMES_SOLAR; }} calt;
""",
        after="classes",
    )
    k_m = -36 if ctx.ITALIC else -42
    k_r = -14 if ctx.ITALIC else -16
    kern_lines = []
    if "M" in ctx.glyf.glyphs:
        kern_lines.append(f"    pos M {SUB_SUN} {k_m};")
    if "R" in ctx.glyf.glyphs:
        kern_lines.append(f"    pos R {SUB_SUN} {k_r};")
    if kern_lines:
        body = "\n".join(kern_lines)
        ctx.gpos(
            f"""
lookup GAMES_KERN {{
{body}
}} GAMES_KERN;

feature kern {{ lookup GAMES_KERN; }} kern;
""",
            after="smallcap_kern",
        )


def post(ctx):
    """Install finalized upright topology-locked TrueType glyphs after build.py's italic shear."""
    for name, ((contours, adv, yc), _cp) in ctx._games_built.items():
        dx = int(round(ctx.ITALIC_K * (yc - ctx.ITALIC_YC))) if ctx.ITALIC else 0
        g = _to_glyph(contours, dx=dx)
        g.recalcBounds(ctx.glyf)
        ctx.glyf[name] = g
        ctx.hmtx[name] = (int(adv), int(g.xMin))


# --- SIL OFL 1.1 cleaned master contour tables (v1 Staunton Chess Figurines U+2654..265F) ---
CHESS_V1_REGULAR = {9812: ([[[336, -18, True],
          [256, -15, True],
          [194, -9, True],
          [140, -4, False],
          [141, 23, True],
          [155, 220, True],
          [48, 332, False],
          [48, 422, True],
          [48, 483, False],
          [80, 519, True],
          [111, 555, False],
          [167, 555, True],
          [230, 555, False],
          [277, 508, True],
          [273, 572, True],
          [271, 608, False],
          [320, 616, True],
          [320, 670, True],
          [280, 670, True],
          [280, 693, True],
          [320, 693, True],
          [320, 729, True],
          [352, 729, True],
          [352, 693, True],
          [392, 693, True],
          [392, 670, True],
          [352, 670, True],
          [352, 616, True],
          [401, 608, False],
          [399, 570, True],
          [395, 508, True],
          [441, 555, False],
          [505, 555, True],
          [561, 555, False],
          [592, 519, True],
          [624, 483, False],
          [624, 422, True],
          [624, 380, False],
          [600, 332, True],
          [576, 283, False],
          [517, 220, True],
          [531, 23, True],
          [532, -2, False],
          [479, -11, True],
          [425, -20, False]],
         [[336, 408, True],
          [348, 444, False],
          [363, 468, True],
          [363, 560, True],
          [363, 591, False],
          [336, 591, True],
          [309, 591, False],
          [309, 560, True],
          [310, 469, True],
          [311, 447, False]],
         [[188, 239, True],
          [260, 254, False],
          [316, 254, True],
          [316, 285, True],
          [316, 327, False],
          [305, 368, True],
          [293, 408, False],
          [273, 441, True],
          [253, 474, False],
          [226, 494, True],
          [200, 514, False],
          [169, 514, True],
          [133, 514, False],
          [112, 488, True],
          [92, 463, False],
          [92, 417, True],
          [92, 380, False],
          [119, 331, True],
          [146, 282, False]],
         [[484, 239, True],
          [527, 284, False],
          [553, 332, True],
          [580, 380, False],
          [580, 417, True],
          [580, 461, False],
          [561, 487, True],
          [541, 514, False],
          [503, 514, True],
          [472, 514, False],
          [445, 494, True],
          [418, 474, False],
          [398, 441, True],
          [379, 408, False],
          [367, 368, True],
          [356, 328, False],
          [356, 288, True],
          [356, 254, True],
          [416, 249, True]],
         [[194, 150, True],
          [226, 158, True],
          [278, 164, True],
          [336, 166, True],
          [392, 164, True],
          [444, 158, True],
          [478, 150, True],
          [473, 206, True],
          [407, 218, True],
          [336, 223, True],
          [264, 218, True],
          [199, 206, True]],
         [[189, 66, True],
          [240, 83, False],
          [336, 83, True],
          [431, 83, False],
          [483, 66, True],
          [480, 119, True],
          [412, 138, False],
          [336, 140, True],
          [297, 141, False],
          [258, 133, True],
          [192, 119, True]],
         [[336, -3, True],
          [489, -3, False],
          [489, 25, True],
          [489, 43, False],
          [449, 47, True],
          [401, 53, True],
          [336, 55, True],
          [272, 54, True],
          [224, 47, True],
          [182, 42, False],
          [182, 25, True],
          [183, -3, False]]],
        672,
        352.5),
 9813: ([[[411, -18, True],
          [331, -15, True],
          [269, -9, True],
          [216, -4, False],
          [216, 23, True],
          [219, 228, True],
          [120, 500, True],
          [86, 499, False],
          [67, 518, True],
          [48, 537, False],
          [48, 567, True],
          [48, 594, False],
          [68, 613, True],
          [87, 631, False],
          [114, 631, True],
          [142, 631, False],
          [161, 612, True],
          [180, 593, False],
          [180, 565, True],
          [180, 550, False],
          [172, 534, True],
          [164, 518, False],
          [151, 510, True],
          [270, 318, True],
          [248, 579, True],
          [222, 579, False],
          [203, 598, True],
          [183, 618, False],
          [183, 645, True],
          [183, 672, False],
          [202, 692, True],
          [220, 711, False],
          [247, 711, True],
          [275, 711, False],
          [294, 693, True],
          [314, 674, False],
          [314, 646, True],
          [314, 624, False],
          [303, 608, True],
          [292, 591, False],
          [272, 584, True],
          [359, 338, True],
          [399, 612, True],
          [377, 616, False],
          [361, 634, True],
          [345, 651, False],
          [345, 677, True],
          [345, 705, False],
          [365, 724, True],
          [384, 742, False],
          [411, 742, True],
          [438, 742, False],
          [457, 724, True],
          [477, 705, False],
          [477, 677, True],
          [477, 651, False],
          [461, 634, True],
          [445, 616, False],
          [423, 612, True],
          [463, 338, True],
          [550, 584, True],
          [530, 591, False],
          [519, 608, True],
          [508, 624, False],
          [508, 646, True],
          [508, 674, False],
          [528, 693, True],
          [547, 711, False],
          [575, 711, True],
          [603, 711, False],
          [621, 692, True],
          [639, 672, False],
          [639, 645, True],
          [639, 618, False],
          [619, 598, True],
          [600, 579, False],
          [574, 579, True],
          [552, 318, True],
          [671, 510, True],
          [659, 518, False],
          [651, 534, True],
          [642, 550, False],
          [642, 565, True],
          [642, 593, False],
          [661, 612, True],
          [680, 631, False],
          [708, 631, True],
          [736, 631, False],
          [755, 613, True],
          [774, 594, False],
          [774, 567, True],
          [774, 537, False],
          [755, 518, True],
          [736, 499, False],
          [702, 500, True],
          [603, 228, True],
          [606, 23, True],
          [606, -2, False],
          [554, -11, True],
          [501, -20, False]],
         [[412, 641, True],
          [426, 641, False],
          [436, 651, True],
          [446, 662, False],
          [446, 678, True],
          [446, 692, False],
          [434, 703, True],
          [426, 711, False],
          [410, 711, True],
          [396, 711, False],
          [388, 703, True],
          [376, 692, False],
          [376, 678, True],
          [376, 662, False],
          [386, 651, True],
          [396, 641, False]],
         [[573, 609, True],
          [589, 609, False],
          [599, 620, True],
          [608, 630, False],
          [608, 646, True],
          [608, 660, False],
          [598, 670, True],
          [588, 680, False],
          [575, 680, True],
          [556, 680, False],
          [547, 669, True],
          [538, 659, False],
          [538, 644, True],
          [538, 629, False],
          [546, 621, True],
          [557, 609, False]],
         [[249, 609, True],
          [265, 609, False],
          [276, 621, True],
          [284, 629, False],
          [284, 644, True],
          [284, 659, False],
          [275, 669, True],
          [265, 680, False],
          [247, 680, True],
          [234, 680, False],
          [224, 670, True],
          [214, 660, False],
          [214, 646, True],
          [214, 630, False],
          [224, 620, True],
          [234, 609, False]],
         [[708, 530, True],
          [725, 530, False],
          [734, 540, True],
          [744, 551, False],
          [744, 566, True],
          [744, 581, False],
          [732, 592, True],
          [724, 600, False],
          [710, 600, True],
          [693, 600, False],
          [683, 590, True],
          [673, 580, False],
          [673, 564, True],
          [673, 550, False],
          [683, 540, True],
          [693, 530, False]],
         [[114, 530, True],
          [129, 530, False],
          [139, 540, True],
          [149, 550, False],
          [149, 564, True],
          [149, 580, False],
          [139, 590, True],
          [129, 600, False],
          [112, 600, True],
          [98, 600, False],
          [90, 592, True],
          [78, 581, False],
          [78, 566, True],
          [78, 551, False],
          [88, 540, True],
          [98, 530, False]],
         [[387, 258, True], [411, 258, True], [435, 258, True], [411, 530, True]],
         [[307, 251, True], [327, 254, True], [349, 256, True], [281, 479, True]],
         [[515, 251, True], [541, 479, True], [473, 256, True], [495, 254, True]],
         [[245, 237, True], [279, 246, True], [186, 408, True]],
         [[577, 237, True], [636, 408, True], [543, 246, True]],
         [[264, 180, True],
          [322, 199, False],
          [411, 199, True],
          [500, 199, False],
          [558, 180, True],
          [558, 212, True],
          [535, 220, False],
          [493, 226, True],
          [451, 231, False],
          [411, 231, True],
          [372, 231, False],
          [329, 226, True],
          [286, 220, False],
          [264, 212, True]],
         [[263, 122, True],
          [292, 132, False],
          [329, 136, True],
          [365, 141, False],
          [411, 141, True],
          [501, 141, False],
          [559, 122, True],
          [559, 154, True],
          [535, 162, False],
          [492, 167, True],
          [449, 173, False],
          [411, 173, True],
          [372, 173, False],
          [330, 167, True],
          [288, 162, False],
          [263, 154, True]],
         [[262, 66, True],
          [314, 83, False],
          [411, 83, True],
          [508, 83, False],
          [560, 66, True],
          [560, 96, True],
          [536, 104, False],
          [494, 109, True],
          [453, 115, False],
          [411, 115, True],
          [371, 115, False],
          [329, 109, True],
          [286, 104, False],
          [262, 96, True]],
         [[411, -3, True],
          [562, -3, False],
          [562, 25, True],
          [562, 43, False],
          [522, 47, True],
          [474, 53, True],
          [411, 55, True],
          [348, 54, True],
          [301, 47, True],
          [259, 42, False],
          [259, 25, True],
          [260, -3, False]]],
        822,
        352.5),
 9814: ([[[48, 0, True],
          [48, 88, True],
          [106, 88, True],
          [106, 154, True],
          [147, 154, True],
          [184, 220, True],
          [184, 514, True],
          [147, 580, True],
          [106, 580, True],
          [106, 696, True],
          [226, 696, True],
          [226, 668, True],
          [285, 668, True],
          [285, 692, True],
          [440, 692, True],
          [440, 668, True],
          [498, 668, True],
          [498, 696, True],
          [619, 696, True],
          [619, 580, True],
          [577, 580, True],
          [541, 514, True],
          [541, 220, True],
          [577, 154, True],
          [619, 154, True],
          [619, 88, True],
          [677, 88, True],
          [677, 0, True]],
         [[148, 607, True],
          [577, 607, True],
          [577, 664, True],
          [524, 664, True],
          [524, 636, True],
          [415, 636, True],
          [415, 660, True],
          [310, 660, True],
          [310, 636, True],
          [201, 636, True],
          [201, 664, True],
          [148, 664, True]],
         [[212, 541, True], [515, 541, True], [533, 575, True], [192, 575, True]],
         [[226, 225, True], [499, 225, True], [499, 509, True], [226, 509, True]],
         [[192, 159, True], [533, 159, True], [514, 193, True], [210, 193, True]],
         [[148, 93, True], [577, 93, True], [577, 127, True], [148, 127, True]],
         [[90, 27, True], [635, 27, True], [635, 61, True], [90, 61, True]]],
        725,
        352.5),
 9815: ([[[48, -25, True],
          [48, 46, True],
          [64, 60, False],
          [92, 69, True],
          [120, 78, False],
          [154, 78, True],
          [293, 78, True],
          [333, 91, True],
          [217, 109, False],
          [227, 148, True],
          [230, 160, True],
          [264, 247, True],
          [230, 268, False],
          [210, 308, True],
          [190, 348, False],
          [190, 394, True],
          [190, 457, False],
          [235, 514, True],
          [279, 572, False],
          [357, 616, True],
          [330, 631, False],
          [330, 663, True],
          [330, 685, False],
          [346, 701, True],
          [362, 717, False],
          [384, 717, True],
          [406, 717, False],
          [422, 701, True],
          [438, 685, False],
          [438, 663, True],
          [438, 631, False],
          [411, 616, True],
          [489, 572, False],
          [533, 514, True],
          [578, 457, False],
          [578, 394, True],
          [578, 348, False],
          [558, 308, True],
          [538, 268, False],
          [504, 247, True],
          [538, 160, True],
          [541, 148, True],
          [551, 109, False],
          [435, 91, True],
          [475, 78, True],
          [614, 78, True],
          [648, 78, False],
          [676, 69, True],
          [704, 60, False],
          [720, 46, True],
          [720, -25, True],
          [696, -25, True],
          [689, -3, False],
          [622, -3, True],
          [441, -3, True],
          [399, -3, False],
          [384, 20, True],
          [369, -3, False],
          [327, -3, True],
          [146, -3, True],
          [79, -3, False],
          [72, -25, True]],
         [[384, 635, True],
          [396, 635, False],
          [404, 643, True],
          [412, 651, False],
          [412, 663, True],
          [412, 674, False],
          [404, 682, True],
          [396, 690, False],
          [384, 690, True],
          [372, 690, False],
          [364, 682, True],
          [356, 674, False],
          [356, 663, True],
          [356, 651, False],
          [364, 643, True],
          [372, 635, False]],
         [[384, 256, True],
          [453, 256, False],
          [493, 293, True],
          [534, 330, False],
          [534, 395, True],
          [534, 455, False],
          [492, 510, True],
          [450, 565, False],
          [384, 598, True],
          [319, 565, False],
          [277, 510, True],
          [234, 455, False],
          [234, 395, True],
          [234, 330, False],
          [275, 293, True],
          [316, 256, False]],
         [[368, 283, True],
          [368, 455, True],
          [290, 455, True],
          [290, 486, True],
          [368, 486, True],
          [368, 563, True],
          [400, 563, True],
          [400, 486, True],
          [478, 486, True],
          [478, 455, True],
          [400, 455, True],
          [400, 283, True]],
         [[278, 187, True],
          [326, 197, True],
          [384, 200, True],
          [443, 197, True],
          [490, 187, True],
          [471, 234, True],
          [434, 228, True],
          [384, 227, True],
          [334, 228, True],
          [297, 234, True]],
         [[384, 124, True],
          [430, 125, True],
          [467, 131, True],
          [502, 136, False],
          [502, 148, True],
          [502, 160, False],
          [468, 166, True],
          [431, 171, True],
          [384, 172, True],
          [337, 171, True],
          [300, 166, True],
          [267, 161, False],
          [267, 148, True],
          [267, 135, False],
          [301, 131, True],
          [338, 125, True]],
         [[73, -2, True],
          [84, 10, False],
          [106, 16, True],
          [127, 22, False],
          [157, 22, True],
          [327, 22, True],
          [362, 22, False],
          [369, 42, True],
          [375, 61, False],
          [367, 100, True],
          [359, 50, False],
          [304, 50, True],
          [157, 50, True],
          [93, 50, False],
          [75, 27, True]],
         [[695, -2, True],
          [693, 27, True],
          [675, 50, False],
          [611, 50, True],
          [464, 50, True],
          [409, 50, False],
          [401, 100, True],
          [393, 61, False],
          [399, 42, True],
          [406, 22, False],
          [441, 22, True],
          [611, 22, True],
          [641, 22, False],
          [663, 16, True],
          [685, 10, False]]],
        768,
        352.5),
 9816: ([[[218, 0, True],
          [218, 47, False],
          [229, 87, True],
          [240, 128, False],
          [256, 147, True],
          [280, 176, True],
          [322, 220, True],
          [352, 251, False],
          [368, 268, True],
          [392, 294, False],
          [376, 324, True],
          [372, 320, False],
          [360, 306, True],
          [346, 290, False],
          [327, 286, True],
          [301, 280, True],
          [263, 276, True],
          [238, 255, True],
          [211, 222, True],
          [180, 185, False],
          [158, 185, True],
          [133, 184, False],
          [117, 190, True],
          [101, 196, False],
          [91, 211, True],
          [48, 280, True],
          [62, 312, True],
          [78, 355, True],
          [96, 398, True],
          [113, 426, True],
          [129, 451, False],
          [141, 489, True],
          [156, 535, True],
          [162, 553, False],
          [176, 567, True],
          [190, 580, False],
          [217, 594, True],
          [228, 622, False],
          [226, 653, True],
          [224, 684, True],
          [218, 714, True],
          [241, 714, True],
          [296, 714, False],
          [306, 647, True],
          [315, 676, True],
          [317, 710, True],
          [317, 727, True],
          [315, 742, True],
          [349, 742, True],
          [382, 742, False],
          [400, 697, True],
          [413, 663, False],
          [413, 626, True],
          [473, 610, False],
          [527, 565, True],
          [580, 521, False],
          [620, 452, True],
          [661, 383, False],
          [679, 294, True],
          [693, 227, False],
          [699, 156, True],
          [706, 85, False],
          [706, 9, True],
          [706, 0, True]],
         [[646, 52, True],
          [646, 78, True],
          [646, 206, False],
          [623, 300, True],
          [601, 393, False],
          [562, 455, True],
          [523, 518, False],
          [473, 555, True],
          [423, 591, False],
          [368, 607, True],
          [371, 641, True],
          [375, 680, False],
          [343, 697, True],
          [343, 666, False],
          [337, 642, True],
          [331, 618, False],
          [322, 607, True],
          [277, 612, True],
          [277, 640, False],
          [272, 652, True],
          [267, 665, False],
          [251, 678, True],
          [255, 641, True],
          [258, 613, False],
          [250, 590, True],
          [242, 566, False],
          [237, 563, True],
          [227, 557, True],
          [212, 544, True],
          [196, 530, False],
          [190, 512, True],
          [169, 454, True],
          [164, 441, False],
          [149, 417, True],
          [135, 394, True],
          [118, 354, True],
          [102, 313, True],
          [89, 287, True],
          [98, 270, True],
          [118, 237, True],
          [124, 226, False],
          [133, 225, True],
          [158, 223, True],
          [168, 222, False],
          [177, 229, True],
          [185, 235, False],
          [200, 253, True],
          [225, 282, True],
          [250, 307, True],
          [268, 310, True],
          [301, 317, True],
          [327, 324, True],
          [343, 329, False],
          [349, 340, True],
          [359, 358, True],
          [404, 358, True],
          [419, 306, True],
          [412, 272, True],
          [409, 259, False],
          [396, 244, True],
          [357, 200, True],
          [314, 154, False],
          [294, 123, True],
          [273, 93, False],
          [273, 54, True]],
         [[557, 65, True],
          [562, 124, True],
          [564, 192, True],
          [566, 291, False],
          [551, 354, True],
          [537, 415, False],
          [510, 456, True],
          [483, 497, False],
          [447, 533, True],
          [497, 508, False],
          [541, 446, True],
          [584, 384, False],
          [604, 282, True],
          [614, 231, False],
          [617, 176, True],
          [621, 65, True]],
         [[240, 478, True],
          [217, 478, False],
          [209, 490, True],
          [209, 505, False],
          [218, 511, True],
          [229, 518, False],
          [244, 517, True],
          [256, 516, True],
          [269, 513, True],
          [292, 499, True],
          [275, 498, False],
          [264, 488, True],
          [252, 478, False]],
         [[143, 270, True],
          [129, 277, True],
          [117, 291, True],
          [127, 335, False],
          [184, 335, True],
          [167, 319, False],
          [156, 301, True],
          [146, 284, False]]],
        754,
        352.5),
 9817: ([[[48, 0, True],
          [48, 35, True],
          [48, 109, False],
          [71, 171, True],
          [95, 232, False],
          [137, 277, True],
          [180, 321, False],
          [237, 340, True],
          [173, 382, False],
          [173, 447, True],
          [173, 497, False],
          [204, 534, True],
          [235, 571, False],
          [293, 589, True],
          [273, 596, False],
          [261, 612, True],
          [250, 628, False],
          [250, 650, True],
          [250, 679, False],
          [276, 696, True],
          [302, 713, False],
          [345, 713, True],
          [388, 713, False],
          [414, 696, True],
          [440, 679, False],
          [440, 650, True],
          [440, 628, False],
          [428, 612, True],
          [416, 595, False],
          [397, 589, True],
          [454, 571, False],
          [485, 534, True],
          [517, 497, False],
          [517, 447, True],
          [517, 382, False],
          [453, 340, True],
          [511, 321, False],
          [554, 277, True],
          [596, 232, False],
          [619, 171, True],
          [642, 109, False],
          [642, 35, True],
          [642, 0, True]],
         [[105, 52, True],
          [585, 52, True],
          [585, 113, False],
          [561, 167, True],
          [538, 220, False],
          [495, 260, True],
          [452, 301, False],
          [392, 319, True],
          [392, 355, True],
          [467, 389, False],
          [467, 449, True],
          [467, 536, False],
          [359, 573, True],
          [359, 602, True],
          [400, 619, False],
          [400, 650, True],
          [400, 665, False],
          [385, 676, True],
          [371, 687, False],
          [345, 687, True],
          [319, 687, False],
          [305, 676, True],
          [290, 665, False],
          [290, 650, True],
          [290, 619, False],
          [331, 602, True],
          [331, 573, True],
          [223, 536, False],
          [223, 449, True],
          [223, 389, False],
          [298, 355, True],
          [298, 319, True],
          [239, 301, False],
          [196, 260, True],
          [152, 220, False],
          [129, 167, True],
          [105, 113, False]]],
        690,
        352.5),
 9818: ([[[336, -18, True],
          [256, -16, True],
          [194, -10, True],
          [139, -5, False],
          [141, 23, True],
          [154, 219, True],
          [48, 332, False],
          [48, 422, True],
          [48, 483, False],
          [79, 519, True],
          [111, 555, False],
          [167, 555, True],
          [231, 555, False],
          [277, 509, True],
          [272, 572, True],
          [270, 609, False],
          [319, 616, True],
          [319, 669, True],
          [279, 669, True],
          [279, 694, True],
          [319, 694, True],
          [319, 730, True],
          [353, 730, True],
          [353, 694, True],
          [393, 694, True],
          [393, 669, True],
          [353, 669, True],
          [353, 616, True],
          [402, 609, False],
          [400, 572, True],
          [395, 509, True],
          [441, 555, False],
          [505, 555, True],
          [561, 555, False],
          [593, 519, True],
          [624, 483, False],
          [624, 422, True],
          [624, 332, False],
          [518, 219, True],
          [531, 23, True],
          [533, -5, False],
          [478, -10, True],
          [417, -16, True]],
         [[336, 409, True],
          [350, 447, False],
          [363, 468, True],
          [363, 560, True],
          [363, 591, False],
          [336, 591, True],
          [309, 591, False],
          [309, 560, True],
          [309, 468, True],
          [322, 447, False]],
         [[336, 434, True],
          [331, 454, True],
          [323, 475, True],
          [323, 544, True],
          [331, 563, True],
          [346, 567, False],
          [347, 559, True],
          [349, 544, True],
          [349, 475, True],
          [341, 454, True]],
         [[188, 239, True],
          [260, 254, False],
          [315, 254, True],
          [315, 285, True],
          [315, 327, False],
          [304, 368, True],
          [293, 408, False],
          [273, 441, True],
          [253, 474, False],
          [226, 494, True],
          [199, 514, False],
          [169, 514, True],
          [133, 514, False],
          [113, 488, True],
          [92, 463, False],
          [92, 417, True],
          [92, 380, False],
          [119, 331, True],
          [146, 282, False]],
         [[484, 239, True],
          [526, 282, False],
          [553, 331, True],
          [580, 380, False],
          [580, 417, True],
          [580, 463, False],
          [560, 488, True],
          [540, 514, False],
          [503, 514, True],
          [473, 514, False],
          [446, 494, True],
          [419, 474, False],
          [399, 441, True],
          [379, 408, False],
          [368, 368, True],
          [357, 327, False],
          [357, 285, True],
          [357, 254, True],
          [412, 254, False]],
         [[192, 270, True],
          [122, 351, False],
          [122, 408, True],
          [122, 442, False],
          [136, 463, True],
          [150, 483, False],
          [178, 483, True],
          [210, 483, False],
          [236, 454, True],
          [262, 424, False],
          [277, 379, True],
          [292, 334, False],
          [292, 283, True],
          [249, 278, True]],
         [[480, 270, True],
          [423, 278, True],
          [380, 283, True],
          [380, 334, False],
          [395, 379, True],
          [410, 424, False],
          [437, 454, True],
          [463, 483, False],
          [494, 483, True],
          [522, 483, False],
          [536, 463, True],
          [550, 442, False],
          [550, 408, True],
          [550, 351, False]],
         [[194, 144, True],
          [226, 152, True],
          [278, 158, True],
          [336, 161, True],
          [394, 158, True],
          [446, 152, True],
          [478, 144, True],
          [476, 171, True],
          [411, 183, True],
          [336, 188, True],
          [262, 183, True],
          [196, 171, True]],
         [[187, 70, True],
          [238, 87, False],
          [336, 87, True],
          [435, 87, False],
          [485, 70, True],
          [483, 95, True],
          [415, 108, True],
          [375, 116, False],
          [336, 116, True],
          [297, 116, False],
          [257, 108, True],
          [189, 95, True]]],
        672,
        352.5),
 9819: ([[[412, -18, True],
          [332, -16, True],
          [270, -10, True],
          [216, -5, False],
          [217, 23, True],
          [219, 231, True],
          [120, 499, True],
          [86, 499, False],
          [67, 518, True],
          [48, 537, False],
          [48, 567, True],
          [48, 595, False],
          [68, 614, True],
          [87, 632, False],
          [115, 632, True],
          [143, 632, False],
          [162, 613, True],
          [182, 594, False],
          [182, 565, True],
          [182, 550, False],
          [174, 534, True],
          [166, 517, False],
          [153, 510, True],
          [278, 297, True],
          [249, 578, True],
          [223, 578, False],
          [203, 598, True],
          [183, 617, False],
          [183, 645, True],
          [183, 672, False],
          [202, 692, True],
          [221, 712, False],
          [248, 712, True],
          [276, 712, False],
          [296, 693, True],
          [316, 674, False],
          [316, 646, True],
          [316, 624, False],
          [305, 607, True],
          [294, 591, False],
          [274, 583, True],
          [364, 308, True],
          [399, 611, True],
          [378, 615, False],
          [361, 633, True],
          [345, 651, False],
          [345, 677, True],
          [345, 705, False],
          [365, 724, True],
          [385, 743, False],
          [412, 743, True],
          [439, 743, False],
          [459, 724, True],
          [479, 705, False],
          [479, 677, True],
          [479, 651, False],
          [463, 633, True],
          [446, 615, False],
          [425, 611, True],
          [460, 308, True],
          [550, 583, True],
          [530, 591, False],
          [519, 607, True],
          [508, 624, False],
          [508, 646, True],
          [508, 674, False],
          [528, 693, True],
          [548, 712, False],
          [576, 712, True],
          [604, 712, False],
          [623, 692, True],
          [641, 672, False],
          [641, 645, True],
          [641, 617, False],
          [621, 598, True],
          [601, 578, False],
          [575, 578, True],
          [546, 297, True],
          [671, 510, True],
          [659, 517, False],
          [651, 533, True],
          [642, 550, False],
          [642, 565, True],
          [642, 594, False],
          [662, 613, True],
          [681, 632, False],
          [709, 632, True],
          [738, 632, False],
          [757, 613, True],
          [776, 595, False],
          [776, 567, True],
          [776, 537, False],
          [757, 518, True],
          [738, 499, False],
          [704, 499, True],
          [605, 231, True],
          [607, 23, True],
          [608, -3, False],
          [555, -12, True],
          [502, -21, False]],
         [[395, 659, True],
          [405, 659, False],
          [416, 671, True],
          [419, 674, False],
          [419, 683, True],
          [419, 694, False],
          [412, 701, True],
          [405, 708, False],
          [395, 708, True],
          [385, 708, False],
          [378, 701, True],
          [371, 694, False],
          [371, 683, True],
          [371, 674, False],
          [374, 671, True],
          [385, 659, False]],
         [[557, 628, True],
          [568, 628, False],
          [575, 636, True],
          [581, 643, False],
          [581, 652, True],
          [581, 663, False],
          [574, 670, True],
          [567, 677, False],
          [557, 677, True],
          [548, 677, False],
          [536, 666, True],
          [533, 663, False],
          [533, 652, True],
          [533, 643, False],
          [540, 636, True],
          [548, 628, False]],
         [[233, 628, True],
          [243, 628, False],
          [254, 640, True],
          [257, 643, False],
          [257, 652, True],
          [257, 663, False],
          [250, 670, True],
          [243, 677, False],
          [233, 677, True],
          [223, 677, False],
          [216, 670, True],
          [209, 663, False],
          [209, 652, True],
          [209, 643, False],
          [212, 640, True],
          [223, 628, False]],
         [[692, 550, True],
          [702, 550, False],
          [709, 557, True],
          [716, 564, False],
          [716, 574, True],
          [716, 585, False],
          [709, 592, True],
          [702, 599, False],
          [692, 599, True],
          [682, 599, False],
          [675, 592, True],
          [668, 585, False],
          [668, 574, True],
          [668, 564, False],
          [675, 557, True],
          [682, 550, False]],
         [[97, 550, True],
          [108, 550, False],
          [115, 557, True],
          [122, 564, False],
          [122, 574, True],
          [122, 584, False],
          [115, 591, True],
          [108, 598, False],
          [97, 598, True],
          [88, 598, False],
          [80, 591, True],
          [73, 585, False],
          [73, 574, True],
          [73, 564, False],
          [85, 553, True],
          [88, 550, False]],
         [[251, 168, True],
          [312, 193, False],
          [412, 188, True],
          [499, 183, True],
          [544, 181, False],
          [574, 168, True],
          [574, 186, True],
          [533, 195, True],
          [472, 202, True],
          [412, 205, True],
          [352, 202, True],
          [291, 195, True],
          [251, 186, True]],
         [[250, 110, True],
          [311, 135, False],
          [412, 130, True],
          [498, 125, True],
          [544, 122, False],
          [575, 110, True],
          [575, 128, True],
          [535, 137, True],
          [473, 144, True],
          [412, 147, True],
          [352, 144, True],
          [291, 137, True],
          [250, 128, True]],
         [[249, 54, True],
          [275, 65, False],
          [320, 67, True],
          [412, 72, True],
          [504, 67, True],
          [551, 65, False],
          [576, 54, True],
          [576, 70, True],
          [536, 79, True],
          [474, 86, True],
          [412, 89, True],
          [352, 86, True],
          [290, 79, True],
          [249, 70, True]]],
        824,
        352.5),
 9820: ([[[48, 0, True],
          [48, 89, True],
          [107, 89, True],
          [107, 155, True],
          [148, 155, True],
          [184, 220, True],
          [184, 514, True],
          [148, 579, True],
          [107, 579, True],
          [107, 697, True],
          [228, 697, True],
          [228, 669, True],
          [285, 669, True],
          [285, 693, True],
          [442, 693, True],
          [442, 669, True],
          [499, 669, True],
          [499, 697, True],
          [620, 697, True],
          [620, 579, True],
          [578, 579, True],
          [543, 514, True],
          [543, 220, True],
          [578, 155, True],
          [620, 155, True],
          [620, 89, True],
          [678, 89, True],
          [678, 0, True]],
         [[136, 602, True], [590, 602, True], [590, 622, True], [136, 622, True]],
         [[195, 546, True], [532, 546, True], [544, 566, True], [183, 566, True]],
         [[180, 164, True], [547, 164, True], [535, 184, True], [192, 184, True]],
         [[136, 98, True], [590, 98, True], [590, 118, True], [136, 118, True]],
         [[78, 32, True], [649, 32, True], [649, 52, True], [78, 52, True]]],
        726,
        352.5),
 9821: ([[[48, -26, True],
          [48, 47, True],
          [64, 61, False],
          [92, 70, True],
          [121, 79, False],
          [155, 79, True],
          [294, 79, True],
          [333, 91, True],
          [217, 108, False],
          [227, 148, True],
          [230, 160, True],
          [264, 247, True],
          [230, 268, False],
          [210, 308, True],
          [191, 348, False],
          [191, 394, True],
          [191, 457, False],
          [235, 515, True],
          [280, 573, False],
          [357, 616, True],
          [330, 631, False],
          [330, 663, True],
          [330, 686, False],
          [346, 702, True],
          [362, 718, False],
          [385, 718, True],
          [408, 718, False],
          [424, 702, True],
          [440, 686, False],
          [440, 663, True],
          [440, 631, False],
          [413, 616, True],
          [490, 573, False],
          [535, 515, True],
          [579, 457, False],
          [579, 394, True],
          [579, 348, False],
          [560, 308, True],
          [540, 268, False],
          [506, 247, True],
          [540, 160, True],
          [543, 148, True],
          [553, 108, False],
          [437, 91, True],
          [476, 79, True],
          [615, 79, True],
          [649, 79, False],
          [678, 70, True],
          [706, 61, False],
          [722, 47, True],
          [722, -26, True],
          [696, -26, True],
          [689, -4, False],
          [623, -4, True],
          [442, -4, True],
          [399, -4, False],
          [385, 19, True],
          [371, -4, False],
          [328, -4, True],
          [147, -4, True],
          [81, -4, False],
          [74, -26, True]],
         [[369, 283, True],
          [401, 283, True],
          [401, 455, True],
          [479, 455, True],
          [479, 486, True],
          [401, 486, True],
          [401, 563, True],
          [369, 563, True],
          [369, 486, True],
          [291, 486, True],
          [291, 455, True],
          [369, 455, True]],
         [[291, 187, True],
          [319, 196, False],
          [385, 196, True],
          [451, 196, False],
          [479, 187, True],
          [464, 223, True],
          [424, 217, True],
          [385, 215, True],
          [346, 217, True],
          [306, 223, True]],
         [[385, 132, True],
          [431, 133, True],
          [462, 136, True],
          [488, 139, False],
          [488, 148, True],
          [488, 157, False],
          [461, 161, True],
          [428, 165, True],
          [385, 166, True],
          [342, 165, True],
          [309, 161, True],
          [282, 157, False],
          [282, 148, True],
          [282, 139, False],
          [308, 136, True],
          [339, 133, True]]],
        770,
        352.5),
 9822: ([[[218, 0, True],
          [218, 48, False],
          [229, 88, True],
          [240, 128, False],
          [256, 148, True],
          [280, 176, True],
          [322, 220, True],
          [352, 252, False],
          [368, 269, True],
          [392, 294, False],
          [376, 323, True],
          [374, 320, False],
          [361, 305, True],
          [348, 289, False],
          [328, 285, True],
          [302, 280, True],
          [264, 275, True],
          [240, 254, True],
          [212, 221, True],
          [181, 184, False],
          [159, 184, True],
          [134, 183, False],
          [118, 189, True],
          [102, 195, False],
          [92, 211, True],
          [48, 280, True],
          [62, 312, True],
          [78, 356, True],
          [96, 399, True],
          [113, 426, True],
          [129, 452, False],
          [141, 489, True],
          [156, 535, True],
          [162, 554, False],
          [177, 567, True],
          [191, 580, False],
          [218, 595, True],
          [228, 623, False],
          [226, 653, True],
          [224, 684, True],
          [218, 715, True],
          [242, 715, True],
          [298, 715, False],
          [307, 647, True],
          [315, 676, True],
          [317, 710, True],
          [317, 727, True],
          [315, 743, True],
          [350, 743, True],
          [383, 743, False],
          [402, 697, True],
          [415, 663, False],
          [415, 627, True],
          [474, 611, False],
          [528, 566, True],
          [582, 521, False],
          [622, 452, True],
          [662, 384, False],
          [681, 294, True],
          [694, 228, False],
          [701, 156, True],
          [708, 85, False],
          [708, 9, True],
          [708, 0, True]],
         [[578, 65, True],
          [641, 65, True],
          [641, 140, False],
          [633, 212, True],
          [625, 284, False],
          [607, 344, True],
          [590, 404, False],
          [561, 444, True],
          [540, 475, False],
          [517, 498, True],
          [495, 522, False],
          [468, 533, True],
          [504, 497, False],
          [531, 455, True],
          [557, 414, False],
          [572, 353, True],
          [586, 290, False],
          [584, 192, True],
          [583, 124, True]],
         [[241, 478, True],
          [253, 478, False],
          [265, 488, True],
          [276, 498, False],
          [295, 501, True],
          [270, 513, True],
          [257, 516, True],
          [245, 517, True],
          [230, 518, False],
          [219, 511, True],
          [210, 505, False],
          [210, 488, True],
          [218, 478, False]],
         [[144, 270, True],
          [146, 284, False],
          [157, 302, True],
          [168, 319, False],
          [185, 335, True],
          [156, 337, False],
          [139, 324, True],
          [123, 311, False],
          [118, 291, True],
          [130, 277, True]]],
        756,
        352.5),
 9823: ([[[48, 0, True],
          [48, 35, True],
          [48, 109, False],
          [72, 171, True],
          [95, 233, False],
          [137, 277, True],
          [180, 322, False],
          [237, 340, True],
          [173, 381, False],
          [173, 447, True],
          [173, 497, False],
          [205, 534, True],
          [236, 571, False],
          [293, 589, True],
          [274, 596, False],
          [262, 612, True],
          [250, 628, False],
          [250, 650, True],
          [250, 680, False],
          [276, 697, True],
          [302, 714, False],
          [346, 714, True],
          [390, 714, False],
          [416, 697, True],
          [442, 680, False],
          [442, 650, True],
          [442, 628, False],
          [430, 612, True],
          [417, 595, False],
          [399, 589, True],
          [455, 571, False],
          [487, 534, True],
          [519, 497, False],
          [519, 447, True],
          [519, 381, False],
          [455, 340, True],
          [513, 322, False],
          [555, 277, True],
          [598, 233, False],
          [621, 171, True],
          [644, 109, False],
          [644, 35, True],
          [644, 0, True]],
         [[294, 609, True],
          [282, 618, False],
          [282, 646, True],
          [282, 676, False],
          [309, 693, True],
          [299, 693, False],
          [285, 679, True],
          [270, 665, False],
          [270, 645, True],
          [270, 632, False],
          [278, 621, True],
          [286, 610, False]],
         [[257, 374, True],
          [245, 392, False],
          [238, 410, True],
          [232, 426, False],
          [232, 453, True],
          [232, 518, False],
          [288, 553, True],
          [272, 552, False],
          [253, 538, True],
          [235, 524, False],
          [222, 502, True],
          [209, 479, False],
          [209, 452, True],
          [209, 425, False],
          [224, 403, True],
          [239, 381, False]],
         [[99, 59, True],
          [130, 59, True],
          [130, 72, True],
          [130, 152, False],
          [156, 202, True],
          [181, 251, False],
          [223, 282, True],
          [166, 263, False],
          [132, 208, True],
          [99, 153, False],
          [99, 81, True]]],
        692,
        352.5)}


EARTH_PAIR = ([[[282.19, -8.0, True], [220.55, -8.0, False], [168.77, 22.35, True], [116.99, 52.69, False], [86.29, 103.93, True], [55.59, 155.16, False], [55.59, 217.25, True], [55.59, 276.01, False], [83.23, 325.35, True], [110.87, 374.69, False], [158.15, 406.11, True], [205.43, 437.53, False], [263.25, 441.85, True], [263.25, 545.17, True], [130.18, 545.17, True], [130.18, 580.88, True], [263.25, 580.88, True], [263.25, 706.0, True], [301.41, 706.0, True], [301.41, 580.88, True], [432.76, 580.88, True], [432.76, 545.17, True], [301.41, 545.17, True], [301.41, 441.85, True], [360.31, 437.53, False], [407.42, 405.74, True], [454.52, 373.95, False], [482.16, 324.78, True], [509.8, 275.61, False], [509.8, 217.04, True], [509.8, 155.16, False], [479.11, 103.93, True], [448.41, 52.69, False], [396.67, 22.35, True], [344.94, -8.0, False]], [[282.7, 28.76, True], [335.12, 28.76, False], [378.06, 54.42, True], [420.99, 80.07, False], [446.28, 122.84, True], [471.56, 165.62, False], [471.56, 216.94, True], [471.56, 267.96, False], [446.28, 310.68, True], [420.99, 353.39, False], [378.06, 379.41, True], [335.12, 405.44, False], [282.26, 405.44, True], [230.63, 405.44, False], [187.69, 379.78, True], [144.76, 354.13, False], [118.93, 311.56, True], [93.1, 268.99, False], [93.1, 216.94, True], [93.1, 165.6, False], [118.74, 122.99, True], [144.39, 80.38, False], [187.34, 54.57, True], [230.28, 28.76, False]]], [[[282.39, -29.8, True], [216.93, -29.8, False], [161.88, 2.9, True], [106.83, 35.6, False], [73.58, 90.25, True], [40.33, 144.9, False], [40.33, 210.02, True], [40.33, 265.61, False], [63.22, 313.57, True], [86.12, 361.54, False], [126.45, 395.87, True], [166.78, 430.21, False], [218.02, 444.38, True], [218.02, 494.53, True], [101.38, 494.53, True], [101.38, 616.61, True], [218.02, 616.61, True], [218.02, 723.44, True], [347.73, 723.44, True], [347.73, 616.61, True], [456.74, 616.61, True], [456.74, 494.53, True], [347.73, 494.53, True], [347.73, 444.38, True], [400.06, 430.21, False], [439.85, 395.87, True], [479.63, 361.54, False], [502.53, 313.57, True], [525.42, 265.61, False], [525.42, 210.02, True], [525.42, 144.9, False], [492.17, 90.25, True], [458.92, 35.6, False], [403.98, 2.9, True], [349.03, -29.8, False]], [[282.67, 95.56, True], [314.61, 95.56, False], [341.36, 111.43, True], [368.11, 127.31, False], [384.08, 153.16, True], [400.06, 179.0, False], [400.06, 210.02, True], [400.06, 241.76, False], [384.16, 268.33, True], [368.27, 294.91, False], [341.65, 310.78, True], [315.03, 326.65, False], [282.33, 326.65, True], [251.32, 326.65, False], [224.75, 310.75, True], [198.17, 294.85, False], [181.93, 268.23, True], [165.69, 241.61, False], [165.69, 209.81, True], [165.69, 179.49, False], [181.59, 153.36, True], [197.48, 127.22, False], [224.1, 111.39, True], [250.72, 95.56, False]]])

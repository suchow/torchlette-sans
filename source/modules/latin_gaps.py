"""latin_gaps: Dutch ij, complete Pinyin repertoire, Latin case-mapping partners,
all precomposed vulgar fractions, and stacked nut fractions (`afrc`).

What this module adds across all 14 styles (upright and italic, Light to Black):

1. Dutch digraph partner:
   - `ij` (`U+0133`), matching `i_j.loclNLD` (`i` + `j` with round dots) and paired
     with existing `IJ` (`U+0132`) and `IJ.sc` (550-unit small cap) in `smcp`.

2. Complete Pinyin repertoire (all 24 lowercase + 24 uppercase toned vowels and
   550-unit small caps):
   - Single-mark caron vowels: `Ǐ` (`U+01CF`), `ǐ` (`U+01D0`, built on `dotlessi`
     so there is never a double dot), `Ǒ` (`U+01D1`), `ǒ` (`U+01D2`), `Ǔ` (`U+01D3`,
     paired with existing `ǔ` `U+01D4` and `uni01D4.sc`), plus 550-unit small caps
     `uni01CF.sc.latin_gaps` and `uni01D1.sc.latin_gaps`.
   - Double-diacritic `ü` + tone vowels: `Ǖ ǖ` (`U+01D5/01D6`), `Ǘ ǘ` (`U+01D7/01D8`),
     `Ǚ ǚ` (`U+01D9/01DA`), `Ǜ ǜ` (`U+01DB/01DC`) and their 550-unit small caps
     `uni01D5.sc.latin_gaps`, `uni01D7.sc.latin_gaps`, `uni01D9.sc.latin_gaps`,
     `uni01DB.sc.latin_gaps`, drawn with round `dot()` dieresis dots and optically
     proportioned tone marks that stay clear across Light..Black within `WIN_ASCENT`.

3. All remaining Latin `case_mapping` partners and `Ƒ`/`ƒ` small cap:
   - `Ǥ` (`U+01E4`, capital partner of `ǥ` `U+01E5`, wired to `uni01E5.sc` in `c2sc`)
   - `Ǩ` (`U+01E8`, capital partner of `ǩ` `U+01E9`, wired to `uni01E9.sc` in `c2sc`)
   - `Ȟ` (`U+021E`, capital partner of `ȟ` `U+021F`, wired to `uni021F.sc` in `c2sc`)
   - `ȩ` (`U+0229`, lowercase partner of `Ȩ` `U+0228`, wired to `uni0228.sc` in `smcp`)
   - `Ƒ` (`U+0191`, capital partner of `ƒ` `U+0192` `florin`) and 550-unit small cap
     `florin.sc.latin_gaps` wired into both `smcp` (for `florin`) and `c2sc` (for `uni0191`).

4. All 17 missing Unicode vulgar fractions (`U+2150..U+215F` and `U+2189`), completing
   all 20 Unicode fraction characters alongside `¼ ½ ¾` (`U+00BC..00BE`), using standard
   AGL production names (`onethird`, `twothirds`, `oneeighth`, `threeeighths`,
   `fiveeighths`, `seveneighths`) and `uniXXXX` names elsewhere.

5. OpenType `afrc` (Alternative / Stacked Nut Fractions):
   - Substitutes all 19 precomposed vulgar fractions (`¼ ½ ¾`, `⅐..⅞`, `↉`) to stacked
     nut forms, expands `⅟` (`U+215F`) before digits/subscripts, and shapes arbitrary
     1- to 4-digit `<numerator>/<denominator>` sequences (with `/` or `⁄`, across all
     lining, old-style, proportional, tabular and small-cap figure sets, while ignoring
     chained dates/paths like `1/2/3` or `2026/11/02`) into vertically stacked nut
     fractions centered over a horizontal vinculum bar, leaning along the 9-degree slant
     axis in italic styles.
"""
import math
from array import array
from collections import defaultdict
import pathops
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent, GlyphCoordinates
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

SUF = 'latin_gaps'
DIG = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
TABULAR = set(
    DIG
    + [d + '.tosf' for d in DIG]
    + [d + '.sc.tf' for d in DIG]
    + ['seven.ss08', 'seven.tosf.ss08', 'seven.sc.tf.ss08']
)

# Vulgar fractions to add: (codepoint, numerator_digits, denominator_digits_or_None)
VULGAR_ADD = [
    (0x2150, [1], [7]),       # ⅐ 1/7
    (0x2151, [1], [9]),       # ⅑ 1/9
    (0x2152, [1], [1, 0]),    # ⅒ 1/10
    (0x2153, [1], [3]),       # ⅓ 1/3  (onethird)
    (0x2154, [2], [3]),       # ⅔ 2/3  (twothirds)
    (0x2155, [1], [5]),       # ⅕ 1/5
    (0x2156, [2], [5]),       # ⅖ 2/5
    (0x2157, [3], [5]),       # ⅗ 3/5
    (0x2158, [4], [5]),       # ⅘ 4/5
    (0x2159, [1], [6]),       # ⅙ 1/6
    (0x215A, [5], [6]),       # ⅚ 5/6
    (0x215B, [1], [8]),       # ⅛ 1/8  (oneeighth)
    (0x215C, [3], [8]),       # ⅜ 3/8  (threeeighths)
    (0x215D, [5], [8]),       # ⅝ 5/8  (fiveeighths)
    (0x215E, [7], [8]),       # ⅞ 7/8  (seveneighths)
    (0x215F, [1], None),      # ⅟ 1/   (Fraction Numerator One)
    (0x2189, [0], [3]),       # ↉ 0/3
]

# Existing Mulish vulgar fractions for afrc mapping
VULGAR_EXISTING = [
    (0x00BC, 'onequarter', [1], [4]),
    (0x00BD, 'onehalf', [1], [2]),
    (0x00BE, 'threequarters', [3], [4]),
]


def _agl_name(cp):
    return UV2AGL.get(cp, f'uni{cp:04X}')


def _add_composite(ctx, name, parts, adv, cp=None):
    """Build a flat composite glyph (all component glyphs must be simple)."""
    glyf, hmtx = ctx.glyf, ctx.hmtx
    g = Glyph()
    g.numberOfContours = -1
    g.components = []
    for comp_name, dx, dy in parts:
        assert not glyf[comp_name].isComposite(), f'nested component {comp_name} in {name}'
        gc = GlyphComponent()
        gc.glyphName = comp_name
        gc.x = round(dx)
        gc.y = round(dy)
        gc.flags = 0x4
        g.components.append(gc)
    glyf[name] = g
    order = ctx.font.getGlyphOrder()
    if name not in order:
        ctx.font.setGlyphOrder(order + [name])
    g.recalcBounds(glyf)
    hmtx[name] = (round(adv), g.xMin)
    ctx.GDEF_CLASS[name] = 1
    if cp is not None:
        ctx.map(cp, name)
    return name


def _add_simple(ctx, name, path, adv, cp=None):
    ctx.add(name, path, round(adv))
    ctx.GDEF_CLASS[name] = 1
    if cp is not None:
        ctx.map(cp, name)
    return name


def _base_anchor_x(ctx, base_glyph, mark_cls):
    """Read Mulish's unslanted GPOS mark-to-base XCoordinate for (base_glyph, mark_cls)."""
    gpos = ctx.font['GPOS'].table
    for lk in gpos.LookupList.Lookup:
        for st in lk.SubTable:
            s = st.ExtSubTable if lk.LookupType == 9 else st
            if getattr(s, 'LookupType', lk.LookupType) != 4:
                continue
            if base_glyph in s.BaseCoverage.glyphs:
                rec = s.BaseArray.BaseRecord[s.BaseCoverage.glyphs.index(base_glyph)]
                anc = rec.BaseAnchor[mark_cls]
                if anc is not None:
                    return anc.XCoordinate
    b = ctx.path_of(base_glyph).bounds
    return round((b[0] + b[2]) / 2)


def _scale_about(ctx, path, sx, sy, cx, cy):
    return ctx.transformed(path, (sx, 0, 0, sy, cx - sx * cx, cy - sy * cy))


def _add_dieresis_tone(ctx, name, base_name, tone_mark, adv, is_upper, is_sc=False, cp=None):
    """Build base + dedicated unencoded dieresis+tone mark glyph as an unscaled 2-component
    composite so contour/point signatures stay 100% weight-invariant across all 14 styles."""
    base_p = ctx.path_of(base_name)
    _bx0, _by0, _bx1, by1 = base_p.bounds

    # Horizontal anchor matches Udieresis / udieresis / Uacute.sc
    if is_upper:
        cx = ctx.glyf['Udieresis'].components[1].x
        dier_src = ctx.path_of('uni0308.case')
    elif is_sc:
        cx = ctx.glyf['Uacute.sc'].components[1].x
        dier_src = ctx.path_of('uni0308')
    else:
        cx = ctx.glyf['udieresis'].components[1].x
        dier_src = ctx.path_of('uni0308')

    # Measure Mulish/build.py's rounded dieresis dot radius and half-separation
    contours = sorted([c.bounds for c in dier_src.contours], key=lambda b: b[0])
    c_left, c_right = contours[0], contours[-1]
    r_src = (c_left[3] - c_left[1]) / 2.0
    dx_src = ((c_right[0] + c_right[2]) - (c_left[0] + c_left[2])) / 4.0

    # Slightly compact round dots so stacked tone mark sits comfortably within WIN_ASCENT
    dot_scale = 0.84 if is_upper else 0.86
    r_dot = r_src * dot_scale
    dx_dot = dx_src * (0.96 if is_upper else 0.98)

    # Clear vertical air gap from base top to dot bottom, and dot top to tone bottom
    gap1 = round(44 - 4 * min(1.0, (ctx.SV - 1.0) / 1.5)) if is_upper else round(46 - 4 * min(1.0, (ctx.SV - 1.0) / 1.5))
    cy_dot = by1 + gap1 + r_dot
    dots_top = cy_dot + r_dot

    tg = ctx.glyf[tone_mark]
    t_coords = list(tg.coordinates)
    t_flags = list(tg.flags)
    t_ends = list(tg.endPtsOfContours)
    tx0 = min(x for x, _ in t_coords)
    tx1 = max(x for x, _ in t_coords)
    ty0 = min(y for _, y in t_coords)
    tcx = (tx0 + tx1) / 2.0

    is_macron = tone_mark.startswith('uni0304')
    if is_macron:
        sx, sy = 0.94, 0.84
        gap2 = round(42 - 4 * min(1.0, (ctx.SV - 1.0) / 1.5))
    else:
        sx = 0.88
        sy = 0.76 if is_upper else 0.75
        gap2 = round(40 - 4 * min(1.0, (ctx.SV - 1.0) / 1.5))

    scaled = [((x - tcx) * sx + tcx, (y - ty0) * sy + ty0) for x, y in t_coords]
    sx0 = min(x for x, _ in scaled)
    sx1 = max(x for x, _ in scaled)
    sy0 = min(y for _, y in scaled)
    if 'acute' in tone_mark or 'grave' in tone_mark:
        dx_tone = float(cx)
    else:
        dx_tone = cx - (sx0 + sx1) / 2.0
    dy_tone = (dots_top + gap2) - sy0
    tone_float = [(x + dx_tone, y + dy_tone) for x, y in scaled]

    mk_gn = f'{name}.mark' if name.endswith(f'.{SUF}') else f'{name}.mark.{SUF}'
    # Initial simple glyph for build.py's GDEF / hmtx passes; post() writes exact final points
    _add_simple(ctx, mk_gn, ctx.rect(round(cx - dx_dot - r_dot), round(cy_dot - r_dot),
                                     round(cx + dx_dot + r_dot), round(cy_dot + r_dot + 80)), adv)
    ctx.lg_dier_marks[mk_gn] = (
        tone_float,
        t_ends,
        t_flags,
        [(cx - dx_dot, cy_dot), (cx + dx_dot, cy_dot)],
        r_dot,
        name,
    )
    _add_composite(ctx, name, [(base_name, 0, 0), (mk_gn, 0, 0)], adv, cp=cp)


def _build_g_stroke(ctx):
    """Build Ǥ (U+01E4, uni01E4): G with horizontal crossbar across its lower right stem."""
    gp = ctx.path_of('G')
    gb = gp.bounds
    # Measure G's right throat at y where the vertical right leg stands below the chin
    # Chin underside is horizontal segment around y = 270..320; inner bottom is ~80..150.
    pts = list(ctx.glyf['G'].coordinates)
    # Find the horizontal chin underside: two consecutive points with equal y in [250, 340] and dx > 120
    chin_y = None
    chin_x_left = None
    inner_x = None
    inner_y_bot = None
    n_pts = len(pts)
    for idx in range(n_pts):
        x0, y0 = pts[idx]
        x1, y1 = pts[(idx + 1) % n_pts]
        if abs(y0 - y1) <= 1 and 250 <= y0 <= 345 and abs(x1 - x0) >= 120:
            if chin_y is None or y0 < chin_y:
                chin_y = y0
                chin_x_left = min(x0, x1)
                inner_x = max(x0, x1)
                # Find the vertical inner wall segment meeting (inner_x, chin_y) from below
                cand_ys = []
                for adj in ((idx - 1) % n_pts, (idx + 2) % n_pts):
                    xa, ya = pts[adj]
                    if abs(xa - inner_x) <= 3 and ya < chin_y - 20:
                        cand_ys.append(ya)
                inner_y_bot = max(cand_ys) if cand_ys else round(gb[3] * 0.14)
    if chin_y is None:
        chin_y = 309
        chin_x_left = 432
        inner_x = gb[2] - round(66 * ctx.SV)
        inner_y_bot = 90

    throat_h = max(80, chin_y - inner_y_bot)
    # Secondary crossbar thins gracefully in heavy weights (matching Mulish's uni01E5.sc and Hbar)
    bar_t = min(round(48 * (ctx.SH ** 0.58)), round(0.46 * throat_h))
    y_mid = (inner_y_bot + chin_y) / 2.0
    y0 = round(y_mid - bar_t / 2.0)
    y1 = y0 + bar_t

    overhang_r = 52
    inward_l = min(84, round((inner_x - chin_x_left) * 0.48))
    x0 = max(chin_x_left + 32, inner_x - inward_l)
    x1 = gb[2] + overhang_r

    bar = ctx.rect(x0, y0, x1, y1)
    return ctx.union(gp, bar), ctx.W('G') + overhang_r


def _build_f_hook(ctx, f_glyph, j_glyph, min_lsb):
    """Build F-with-hook (Ƒ or florin.sc) by joining F's stem seamlessly into J's descender hook."""
    fp = ctx.path_of(f_glyph)
    jp = ctx.path_of(j_glyph)
    fb = fp.bounds
    jb = jp.bounds
    y_probe = round(fb[3] * 0.22)  # below F's middle crossbar, inside J's straight vertical stem
    f_span = ctx.hspans(fp, y_probe)[0]
    j_span = ctx.hspans(jp, round(jb[3] * 0.65))[-1]

    f_w = f_span[1] - f_span[0]
    j_w = j_span[1] - j_span[0]
    if abs(f_w - j_w) > 0.25:
        jp = _scale_about(ctx, jp, f_w / j_w, 1.0, j_span[0], 0)
        j_span = (j_span[0], j_span[0] + f_w)

    dx_align = f_span[0] - j_span[0]
    y_cut_f = round(fb[3] * 0.14)
    y_cut_j = round(fb[3] * 0.30)

    f_top = ctx.clip(fp, (-1000, y_cut_f, 3000, 2000))
    j_bot = ctx.clip(ctx.mv(jp, dx_align, 0), (-1000, -1000, 3000, y_cut_j))
    joined = ctx.union(f_top, j_bot)

    jb_new = joined.bounds
    shift_x = max(0, min_lsb - round(jb_new[0]))
    if shift_x:
        joined = ctx.mv(joined, shift_x, 0)
    adv = ctx.W(f_glyph) + shift_x
    return joined, adv, shift_x


def _frac_kern_offsets(ctx):
    """Extract Mulish's exact GPOS kerning for <numr>+fraction and fraction+<dnom>."""
    # Reference from onehalf and onequarter in Mulish:
    # onehalf = [('one.dnom', 0, 282), ('fraction', x_frac, 0), ('two.dnom', x_den2, 0)]
    g_half = ctx.glyf['onehalf']
    g_quar = ctx.glyf['onequarter']
    y_num = g_half.components[0].y
    x_frac_default = g_half.components[1].x
    x_den_default = g_half.components[2].x
    x_den_four = g_quar.components[2].x

    # Read explicit GPOS pair kerning for seven.numr + fraction and fraction + *.dnom if present
    num_kern = {}
    den_kern = {}
    gpos = ctx.font['GPOS'].table
    for lk in gpos.LookupList.Lookup:
        for st in lk.SubTable:
            s = st.ExtSubTable if lk.LookupType == 9 else st
            if getattr(s, 'LookupType', lk.LookupType) != 2:
                continue
            if s.Format == 1:
                for a, ps in zip(s.Coverage.glyphs, s.PairSet):
                    for r in ps.PairValueRecord:
                        v = (getattr(r.Value1, 'XAdvance', 0) or 0) if r.Value1 else 0
                        if v and r.SecondGlyph == 'fraction' and a.endswith('.numr'):
                            num_kern.setdefault(a, v)
                        elif v and a == 'fraction' and r.SecondGlyph.endswith('.dnom'):
                            den_kern.setdefault(r.SecondGlyph, v)
    return y_num, x_frac_default, x_den_default, x_den_four, num_kern, den_kern



def _numerator_wght(src_w):
    """Smooth optical weight grading for fraction numerators (top / top-left half).
    Anchors at Regular (324) so Light and Regular keep exact source weight; above
    Regular, stroke growth eases to 0.85x so upper figures balance lower figures."""
    if src_w <= 324.0:
        return float(src_w)
    return 324.0 + 0.85 * (src_w - 324.0)


def _small_two_path_at_weight(ctx, f_w, w_val):
    """Construct Torchlette's small `two` outline (`build.py`'s `small_two`) for
    Mulish instance `f_w` at donor weight `w_val`, scaling strokes continuously."""
    gl_w = f_w['glyf']
    g_two = gl_w['two.dnom']
    g_two.recalcBounds(gl_w)
    g_one = gl_w['one.dnom']
    g_one.recalcBounds(gl_w)
    iw = g_two.xMax - g_two.xMin
    k = iw / 500.0
    s_boxes = ctx._slice(f_w, 'one.dnom', (-1000, 199.5, 3000, 200.5))
    stem_one_w = s_boxes[0][2] - s_boxes[0][0]
    wt = stem_one_w / ctx.stem_at('one')
    m_w = ctx.measure(f_w)
    sv_w = (m_w['t_r'] - m_w['t_l']) / (ctx.R['t_r'] - ctx.R['t_l'])
    side_w = 67.0 * sv_w
    hx_w = 0.0 if w_val <= 675.0 else 67.0 * (sv_w - 119.0 / 66.0)
    dw = ctx.FIG_GROW * hx_w * wt
    w_head = min(440.0 * k + 2.0 * (ctx.SIDE * wt - side_w * k), ctx.P('TWO_SMALL_MAX', 0.94) * iw)
    return ctx.two_fig(
        g_one.yMax,
        w_head,
        g_two.xMin + iw / 2.0 - 10.0 * k - dw * 0.35,
        iw,
        g_two.xMin + iw / 2.0,
        wt,
        dw=dw,
    )

def _normalize_two_dnom(dg):
    """Refit Torchlette's cu2qu-converted `two.dnom` onto a fixed 35-point implied-midpoint
    quadratic B-spline (`1, 0*14, 1*5, 1, 0*14`) so all 14 masters share identical topology."""
    raw_c = list(dg.coordinates)
    raw_f = list(dg.flags)
    n = len(raw_c)
    pts = [(tuple(raw_c[i]), bool(raw_f[i] & 1)) for i in range(n)]
    k0 = next(i for i, (_, on) in enumerate(pts) if on)
    pts = pts[k0:] + pts[:k0]
    segs = []
    i = 0
    while i < n:
        a, _ = pts[i]
        nx, non = pts[(i + 1) % n]
        if non:
            segs.append(('L', a, nx))
            i += 1
        else:
            ctl = nx
            j = i + 2
            while True:
                p2, on2 = pts[j % n]
                if on2:
                    segs.append(('Q', a, ctl, p2))
                    i = j
                    break
                mid = ((ctl[0] + p2[0]) / 2.0, (ctl[1] + p2[1]) / 2.0)
                segs.append(('Q', a, ctl, mid))
                a = mid
                ctl = p2
                j += 1
    m = len(segs)
    k_rot = next(
        idx for idx in range(m)
        if segs[idx][0] == 'Q' and segs[(idx - 1) % m][0] == 'L' and segs[(idx - 2) % m][0] == 'Q'
    )
    segs = segs[k_rot:] + segs[:k_rot]
    runs = []
    for sg in segs:
        if not runs or runs[-1][0][0] != sg[0]:
            runs.append([sg])
        else:
            runs[-1].append(sg)

    def _fit_qrun(qrun, k_cnt, dir_start=None, dir_end=None):
        pa = qrun[0][1]
        pc = qrun[-1][3]
        poly = []
        for idx_q, (_, qa, qb, qc) in enumerate(qrun):
            for step in range(0 if idx_q == 0 else 1, 49):
                t = step / 48.0
                u = 1.0 - t
                poly.append((u * u * qa[0] + 2 * u * t * qb[0] + t * t * qc[0],
                             u * u * qa[1] + 2 * u * t * qb[1] + t * t * qc[1]))
        cum = [0.0]
        for ip in range(1, len(poly)):
            cum.append(cum[-1] + math.dist(poly[ip - 1], poly[ip]))

        def _sample(frac):
            tgt = frac * cum[-1]
            lo, hi = 0, len(cum) - 1
            while lo + 1 < hi:
                md = (lo + hi) // 2
                if cum[md] <= tgt:
                    lo = md
                else:
                    hi = md
            sp = cum[hi] - cum[lo]
            tt = (tgt - cum[lo]) / sp if sp > 0 else 0.0
            return (poly[lo][0] + tt * (poly[hi][0] - poly[lo][0]),
                    poly[lo][1] + tt * (poly[hi][1] - poly[lo][1]))

        targets = []
        for kk in range(k_cnt):
            u = (kk + 0.5) / k_cnt
            ch = 0.5 - 0.5 * math.cos(math.pi * u)
            targets.append(_sample(0.55 * u + 0.45 * ch))
        q_ctrl = [list(p) for p in targets]
        for _ in range(150):
            for kk in range(k_cnt):
                if kk == 0:
                    qx = (targets[0][0] - 0.25 * pa[0] - 0.125 * q_ctrl[1][0]) / 0.625
                    qy = (targets[0][1] - 0.25 * pa[1] - 0.125 * q_ctrl[1][1]) / 0.625
                    if dir_start is not None:
                        pr = max(8.5, (qx - pa[0]) * dir_start[0] + (qy - pa[1]) * dir_start[1])
                        qx, qy = pa[0] + pr * dir_start[0], pa[1] + pr * dir_start[1]
                    q_ctrl[0] = [qx, qy]
                elif kk == k_cnt - 1:
                    qx = (targets[kk][0] - 0.25 * pc[0] - 0.125 * q_ctrl[kk - 1][0]) / 0.625
                    qy = (targets[kk][1] - 0.25 * pc[1] - 0.125 * q_ctrl[kk - 1][1]) / 0.625
                    if dir_end is not None:
                        pr = max(8.5, (qx - pc[0]) * dir_end[0] + (qy - pc[1]) * dir_end[1])
                        qx, qy = pc[0] + pr * dir_end[0], pc[1] + pr * dir_end[1]
                    q_ctrl[kk] = [qx, qy]
                else:
                    q_ctrl[kk][0] = (targets[kk][0] - 0.125 * (q_ctrl[kk - 1][0] + q_ctrl[kk + 1][0])) / 0.75
                    q_ctrl[kk][1] = (targets[kk][1] - 0.125 * (q_ctrl[kk - 1][1] + q_ctrl[kk + 1][1])) / 0.75
        return [(qx, qy) for qx, qy in q_ctrl]

    _, eo, notch = runs[1][0]
    l_out = math.dist(eo, notch)
    dir_end_0 = ((eo[0] - notch[0]) / l_out, (eo[1] - notch[1]) / l_out)
    _, foot_l, ei = runs[1][-1]
    l_in = math.dist(foot_l, ei)
    dir_start_2 = ((ei[0] - foot_l[0]) / l_in, (ei[1] - foot_l[1]) / l_in)
    q0 = _fit_qrun(runs[0], 14, dir_end=dir_end_0)
    q2 = _fit_qrun(runs[2], 14, dir_start=dir_start_2)
    out_pts = [runs[0][0][1]] + q0 + [x[1] for x in runs[1]] + [runs[2][0][1]] + q2
    out_flg = [1] + [0] * len(q0) + [1] * len(runs[1]) + [1] + [0] * len(q2)
    return out_pts, [len(out_pts) - 1], out_flg


def glyphs(ctx):
    ctx.lg_smcp = []          # (lower_glyph, sc_glyph)
    ctx.lg_c2sc = []          # (upper_glyph, sc_glyph)
    ctx.lg_kern = {}          # glyph -> (first_src_for_right_edge, second_src_for_left_edge)
    ctx.lg_dier_marks = {}    # mark_glyph -> (tone_float, ends, flags, dot_centers, r_dot, parent_glyph)
    ctx.lg_quad_figs = {}     # fig_glyph -> (sc_coords, ends, flags, dx, y_base)
    ctx.lg_vulg_names = []    # encoded vulgar fraction composite names

    # ---- 1. Dutch ij (U+0133) -----------------------------------------------------
    w_i = ctx.W('i')
    adv_ij = ctx.W('i_j.loclNLD') if 'i_j.loclNLD' in ctx.glyf.glyphs else (w_i + ctx.W('j'))
    _add_composite(ctx, 'ij', [('i', 0, 0), ('j', w_i, 0)], adv_ij, cp=0x0133)
    ctx.lg_smcp.append(('ij', 'IJ.sc'))
    ctx.lg_kern['ij'] = ('j', 'i')

    # ---- 2. Pinyin single-mark caron vowels + small caps --------------------------
    # Ǐ (U+01CF) and ǐ (U+01D0, built on dotlessi!) + uni01CF.sc.latin_gaps
    ic_up = ctx.glyf['Iacute'].components[1]
    _add_composite(ctx, 'uni01CF', [('I', 0, 0), ('uni030C.case', ic_up.x, ic_up.y)], ctx.W('I'), cp=0x01CF)
    ic_lo = ctx.glyf['iacute'].components[1]
    _add_composite(ctx, 'uni01D0', [('dotlessi', 0, 0), ('uni030C', ic_lo.x, ic_lo.y)], ctx.W('dotlessi'), cp=0x01D0)
    ic_sc = ctx.glyf['Iacute.sc'].components[1]
    sc_01cf = f'uni01CF.sc.{SUF}'
    _add_composite(ctx, sc_01cf, [('I.sc', 0, 0), ('uni030C', ic_sc.x, ic_sc.y)], ctx.W('I.sc'))
    ctx.lg_smcp.append(('uni01D0', sc_01cf))
    ctx.lg_c2sc.append(('uni01CF', sc_01cf))
    ctx.lg_kern['uni01CF'] = ('I', 'I')
    ctx.lg_kern['uni01D0'] = ('i', 'i')
    ctx.lg_kern[sc_01cf] = ('I.sc', 'I.sc')

    # Ǒ (U+01D1) and ǒ (U+01D2) + uni01D1.sc.latin_gaps
    oc_up = ctx.glyf['Oacute'].components[1]
    _add_composite(ctx, 'uni01D1', [('O', 0, 0), ('uni030C.case', oc_up.x, oc_up.y)], ctx.W('O'), cp=0x01D1)
    oc_lo = ctx.glyf['oacute'].components[1]
    _add_composite(ctx, 'uni01D2', [('o', 0, 0), ('uni030C', oc_lo.x, oc_lo.y)], ctx.W('o'), cp=0x01D2)
    oc_sc = ctx.glyf['Oacute.sc'].components[1]
    sc_01d1 = f'uni01D1.sc.{SUF}'
    _add_composite(ctx, sc_01d1, [('O.sc', 0, 0), ('uni030C', oc_sc.x, oc_sc.y)], ctx.W('O.sc'))
    ctx.lg_smcp.append(('uni01D2', sc_01d1))
    ctx.lg_c2sc.append(('uni01D1', sc_01d1))
    ctx.lg_kern['uni01D1'] = ('O', 'O')
    ctx.lg_kern['uni01D2'] = ('o', 'o')
    ctx.lg_kern[sc_01d1] = ('O.sc', 'O.sc')

    # Ǔ (U+01D3); lowercase ǔ (uni01D4) and uni01D4.sc already exist
    uc_up = ctx.glyf['Uacute'].components[1]
    _add_composite(ctx, 'uni01D3', [('U', 0, 0), ('uni030C.case', uc_up.x, uc_up.y)], ctx.W('U'), cp=0x01D3)
    ctx.lg_c2sc.append(('uni01D3', 'uni01D4.sc'))
    ctx.lg_kern['uni01D3'] = ('U', 'U')

    # ---- 2b. Pinyin double-diacritic ü + tone (U+01D5..U+01DC) + small caps -------
    tones = [
        (0x01D5, 0x01D6, 'uni0304.case', 'uni0304'),          # Ǖ ǖ macron
        (0x01D7, 0x01D8, 'acutecomb.case', 'acutecomb'),      # Ǘ ǘ acute
        (0x01D9, 0x01DA, 'uni030C.case', 'uni030C'),          # Ǚ ǚ caron
        (0x01DB, 0x01DC, 'gravecomb.case', 'gravecomb'),      # Ǜ ǜ grave
    ]
    for cp_up, cp_lo, mk_up, mk_lo in tones:
        gn_up = f'uni{cp_up:04X}'
        gn_lo = f'uni{cp_lo:04X}'
        gn_sc = f'{gn_up}.sc.{SUF}'
        _add_dieresis_tone(ctx, gn_up, 'U', mk_up, ctx.W('U'), is_upper=True, cp=cp_up)
        _add_dieresis_tone(ctx, gn_lo, 'u', mk_lo, ctx.W('u'), is_upper=False, cp=cp_lo)
        _add_dieresis_tone(ctx, gn_sc, 'U.sc', mk_lo, ctx.W('U.sc'), is_upper=False, is_sc=True)
        ctx.lg_smcp.append((gn_lo, gn_sc))
        ctx.lg_c2sc.append((gn_up, gn_sc))
        ctx.lg_kern[gn_up] = ('U', 'U')
        ctx.lg_kern[gn_lo] = ('u', 'u')
        ctx.lg_kern[gn_sc] = ('U.sc', 'U.sc')

    # ---- 3. Remaining Latin case_mapping partners + Ƒ/ƒ small cap -----------------
    # Ǥ (U+01E4, partner of ǥ U+01E5; uni01E5.sc already exists)
    gstroke_p, gstroke_adv = _build_g_stroke(ctx)
    _add_simple(ctx, 'uni01E4', gstroke_p, gstroke_adv, cp=0x01E4)
    ctx.lg_c2sc.append(('uni01E4', 'uni01E5.sc'))
    ctx.lg_kern['uni01E4'] = (None, 'G')   # right side has protruding crossbar; left side is G's bowl

    # Ǩ (U+01E8, partner of ǩ U+01E9; uni01E9.sc already exists)
    kx = _base_anchor_x(ctx, 'K', 0)
    _add_composite(ctx, 'uni01E8', [('K', 0, 0), ('uni030C.case', kx, 0)], ctx.W('K'), cp=0x01E8)
    ctx.lg_c2sc.append(('uni01E8', 'uni01E9.sc'))
    ctx.lg_kern['uni01E8'] = ('K', 'K')

    # Ȟ (U+021E, partner of ȟ U+021F; uni021F.sc already exists)
    hx = _base_anchor_x(ctx, 'H', 0)
    _add_composite(ctx, 'uni021E', [('H', 0, 0), ('uni030C.case', hx, 0)], ctx.W('H'), cp=0x021E)
    ctx.lg_c2sc.append(('uni021E', 'uni021F.sc'))
    ctx.lg_kern['uni021E'] = ('H', 'H')

    # ȩ (U+0229, partner of Ȩ U+0228; uni0228.sc already exists)
    ex = _base_anchor_x(ctx, 'e', 2)
    _add_composite(ctx, 'uni0229', [('e', 0, 0), ('uni0327', ex, 0)], ctx.W('e'), cp=0x0229)
    ctx.lg_smcp.append(('uni0229', 'uni0228.sc'))
    ctx.lg_kern['uni0229'] = ('e', 'e')

    # Ƒ (U+0191, partner of ƒ U+0192 florin) and 550-unit florin.sc.latin_gaps
    fhook_p, fhook_adv, fhook_dx = _build_f_hook(ctx, 'F', 'J', min_lsb=16)
    _add_simple(ctx, 'uni0191', fhook_p, fhook_adv, cp=0x0191)
    fsc_p, fsc_adv, fsc_dx = _build_f_hook(ctx, 'F.sc', 'J.sc', min_lsb=14)
    sc_florin = f'florin.sc.{SUF}'
    _add_simple(ctx, sc_florin, fsc_p, fsc_adv)
    ctx.lg_smcp.append(('florin', sc_florin))
    ctx.lg_c2sc.append(('uni0191', sc_florin))
    ctx.lg_kern['uni0191'] = ('F', None if fhook_dx > 0 else 'F')
    ctx.lg_kern[sc_florin] = ('F.sc', None if fsc_dx > 0 else 'F.sc')

    # ---- 4. All 17 missing vulgar fractions (U+2150..215F, U+2189) ----------------
    # Smooth optical weight grading for numerator figures (`w_num`) + slash breathing
    # room (`pad_num`) so heavy weights balance the top/left numerator with denominator.
    w_num = _numerator_wght(ctx.SRC_W)
    f_num = ctx.inst(w_num)
    gs_num = f_num.getGlyphSet()
    gl_num = f_num['glyf']

    y_num, x_frac_def, x_den_def, x_den_four, num_kern, den_kern = _frac_kern_offsets(ctx)
    w_dnom = ctx.W('one.dnom')
    w_frac = ctx.W('fraction')
    pad_num = round(4.0 * min(1.0, max(0.0, (ctx.SV - 1.0) / 1.47)))

    # The numerators the vulgar fractions use get a glyph (`<digit>.vnumr`); every digit's
    # numerator outline is kept in num_src_paths/num_src_quads for afrc's `.anumr` figures.
    vnumr_used = {DIG[num_ds[0]] for _cp, num_ds, _den in VULGAR_ADD}
    assert 'two' in vnumr_used     # the two's branch normalizes its glyph's outline
    num_src_paths = {}
    num_src_quads = {}
    for d in DIG:
        gn_vn = f'{d}.vnumr.{SUF}'
        lsb_ref = ctx.path_of(d + '.dnom').bounds[0]
        if d == 'two':
            if ctx.SRC_W <= 324.0:
                p_vn_raw = ctx.path_of('two.dnom')
            else:
                p_vn_raw = _small_two_path_at_weight(ctx, f_num, w_num)
            dx_vn = lsb_ref - p_vn_raw.bounds[0]
            p_vn = ctx.mv(p_vn_raw, dx_vn, 0)
            _add_simple(ctx, gn_vn, p_vn, w_dnom)
            g_vn = ctx.glyf[gn_vn]
            d_coords, d_ends, d_flags = _normalize_two_dnom(g_vn)
            q_pack = (d_coords, d_ends, d_flags)
            ctx.lg_quad_figs[gn_vn] = (d_coords, d_ends, d_flags, 0.0, 0.0)
            num_src_paths[d] = p_vn
            num_src_quads[d] = q_pack
        else:
            p_vn_raw = pathops.Path()
            gs_num[d + '.dnom'].draw(p_vn_raw.getPen(glyphSet=gs_num))
            dx_vn = lsb_ref - p_vn_raw.bounds[0]
            p_vn = ctx.mv(p_vn_raw, dx_vn, 0)
            dg_num = gl_num[d + '.dnom']
            q_pack = (
                [(x + dx_vn, y) for x, y in dg_num.coordinates],
                list(dg_num.endPtsOfContours),
                [int(f) & 1 for f in dg_num.flags],
            )
            if d in vnumr_used:
                _add_simple(ctx, gn_vn, p_vn, w_dnom)
                ctx.lg_quad_figs[gn_vn] = (q_pack[0], q_pack[1], q_pack[2], 0.0, 0.0)
            else:
                p_vn.simplify()      # as ctx.add does to a glyph's path: afrc's .anumr reads p_vn's bounds
            num_src_paths[d] = p_vn
            num_src_quads[d] = q_pack

    for cp, num_ds, den_ds in VULGAR_ADD:
        gn = _agl_name(cp)
        n0 = DIG[num_ds[0]]
        x_frac_base = (w_dnom + num_kern[n0 + '.numr']) if (n0 + '.numr') in num_kern else x_frac_def
        x_frac = x_frac_base + pad_num
        parts = [(f'{n0}.vnumr.{SUF}', 0, y_num), ('fraction', x_frac, 0)]
        if den_ds is None:
            # U+215F Fraction Numerator One: advance places following subscript right under slash
            adv = x_frac + w_frac
        else:
            d0 = DIG[den_ds[0]]
            if d0 == 'four' and x_frac_base == x_frac_def:
                x_den = x_den_four + pad_num
            elif (d0 + '.dnom') in den_kern:
                x_den = x_frac + w_frac + den_kern[d0 + '.dnom']
            else:
                x_den = x_frac + (x_den_def - x_frac_def)
            parts.append((d0 + '.dnom', x_den, 0))
            if len(den_ds) == 1:
                adv = x_den + w_dnom
            else:
                # ⅒ (1/10): tighten gap slightly between 1 and 0 in denominator
                d1 = DIG[den_ds[1]]
                tighten = round(34 - 18 * min(1.0, max(0.0, (ctx.SV - 1.0) / 1.5)))
                x_den1 = x_den + w_dnom - tighten
                parts.append((d1 + '.dnom', x_den1, 0))
                adv = x_den1 + w_dnom
        _add_composite(ctx, gn, parts, adv, cp=cp)
        ctx.lg_vulg_names.append(gn)

    # ---- 5. Stacked nut fractions (afrc) glyphs -----------------------------------
    # Optically scaled from Mulish's weight-compensated .dnom figures, centered on cap middle (352)
    y_bar_mid = 352
    d5_p = ctx.path_of('five.dnom')
    d5_b = d5_p.bounds
    # Measure horizontal stroke of .dnom figures via minus & SH so vinculum matches figure color
    bar_t = round(42 * (ctx.SM ** 0.82))
    bar_y0 = round(y_bar_mid - bar_t / 2.0)
    bar_y1 = bar_y0 + bar_t

    fig_sy = 0.85
    fig_sx = 0.87
    gap_v = round(45 - 4 * min(1.0, max(0.0, (ctx.SV - 1.0) / 1.5)))

    # Uniform cell width W_d for stacked digits (wide enough in Black with clean air)
    w_d = round(336 + 10 * min(1.0, max(0.0, (ctx.SV - 1.0) / 1.5)))
    pad_bar = 22
    sb_bar = 44
    ctx.afrc_wd = w_d
    ctx.afrc_pad = pad_bar
    ctx.afrc_sb = sb_bar

    ref_h = round(ctx.path_of('one.dnom').bounds[3] * fig_sy)
    y_num_base = bar_y1 + gap_v
    y_den_base = bar_y0 - gap_v - ref_h

    ctx.afrc_numr = []
    ctx.afrc_dnom = []
    k_sl = ctx.ITALIC_K if ctx.ITALIC else 0.0
    yc_sl = ctx.ITALIC_YC

    def _center_at_y(p_scaled, y_base):
        placed = ctx.mv(p_scaled, 0, y_base)
        if k_sl:
            slanted = ctx.transformed(placed, (1, 0, k_sl, 1, -k_sl * yc_sl, 0))
            bx0, by0, bx1, by1 = slanted.bounds
            want_cx = w_d / 2.0 + k_sl * ((by0 + by1) / 2.0 - yc_sl)
            dx = want_cx - (bx0 + bx1) / 2.0
        else:
            bx0, _by0, bx1, _by1 = placed.bounds
            dx = (w_d - (bx0 + bx1)) / 2.0
        return ctx.mv(placed, dx, 0), dx

    for d in DIG:
        gn_n = f'{d}.anumr.{SUF}'
        gn_d = f'{d}.adnom.{SUF}'

        # Numerator (`anumr`) uses optically weight-graded `w_num` donor
        src_p_n = num_src_paths[d]
        sb_n = src_p_n.bounds
        cx_n = (sb_n[0] + sb_n[2]) / 2.0
        sc_p_n = _scale_about(ctx, src_p_n, fig_sx, fig_sy, cx_n, 0.0)
        p_num, dx_num = _center_at_y(sc_p_n, y_num_base)
        _add_simple(ctx, gn_n, p_num, w_d)

        # Denominator (`adnom`) uses `SRC_W` `.dnom` donor
        dg_d = ctx.glyf[d + '.dnom']
        src_p_d = ctx.path_of(d + '.dnom')
        sb_d = src_p_d.bounds
        cx_d = (sb_d[0] + sb_d[2]) / 2.0
        sc_p_d = _scale_about(ctx, src_p_d, fig_sx, fig_sy, cx_d, 0.0)
        p_den, dx_den = _center_at_y(sc_p_d, y_den_base)
        _add_simple(ctx, gn_d, p_den, w_d)

        if d == 'two':
            d_coords, d_ends, d_flags = _normalize_two_dnom(dg_d)
            sc_d_coords = [((x - cx_d) * fig_sx + cx_d, y * fig_sy) for x, y in d_coords]
            ctx.lg_quad_figs[gn_d] = (sc_d_coords, d_ends, d_flags, dx_den, y_den_base)

            n_coords, n_ends, n_flags = num_src_quads[d]
            sc_n_coords = [((x - cx_n) * fig_sx + cx_n, y * fig_sy) for x, y in n_coords]
            ctx.lg_quad_figs[gn_n] = (sc_n_coords, n_ends, n_flags, dx_num, y_num_base)
        else:
            n_coords, n_ends, n_flags = num_src_quads[d]
            sc_n_coords = [((x - cx_n) * fig_sx + cx_n, y * fig_sy) for x, y in n_coords]
            ctx.lg_quad_figs[gn_n] = (sc_n_coords, n_ends, n_flags, dx_num, y_num_base)

            d_coords = [tuple(xy) for xy in dg_d.coordinates]
            d_ends = list(dg_d.endPtsOfContours)
            d_flags = [int(f) & 1 for f in dg_d.flags]
            sc_d_coords = [((x - cx_d) * fig_sx + cx_d, y * fig_sy) for x, y in d_coords]
            ctx.lg_quad_figs[gn_d] = (sc_d_coords, d_ends, d_flags, dx_den, y_den_base)

        ctx.afrc_numr.append(gn_n)
        ctx.afrc_dnom.append(gn_d)

    # Pair-encoded nut bars bar{m}{n}.afrc.latin_gaps for 1 <= m, n <= 4
    ctx.afrc_bars = {}
    ctx.afrc_wk = {}
    for k in range(1, 5):
        ctx.afrc_wk[k] = k * w_d + 2 * (pad_bar + sb_bar)
    for m in range(1, 5):
        for n in range(1, 5):
            k = max(m, n)
            wk = ctx.afrc_wk[k]
            bname = f'bar{m}{n}.afrc.{SUF}'
            _add_simple(ctx, bname, ctx.rect(sb_bar, bar_y0, wk - sb_bar, bar_y1), wk)
            ctx.afrc_bars[(m, n)] = bname

    # Precomposed nut-fraction forms for all 19 full vulgar fractions
    ctx.afrc_vulg_pairs = []
    all_vulg = VULGAR_EXISTING + [(cp, _agl_name(cp), nd, dd) for cp, nd, dd in VULGAR_ADD if dd is not None]
    for _cp, vname, nd, dd in all_vulg:
        m, n = len(nd), len(dd)
        k = max(m, n)
        wk = ctx.afrc_wk[k]
        bname = ctx.afrc_bars[(m, n)]
        dx_n0 = round((wk - m * w_d) / 2.0)
        dx_d0 = round((wk - n * w_d) / 2.0)
        comps = []
        for idx, digit in enumerate(nd):
            comps.append((ctx.afrc_numr[digit], dx_n0 + idx * w_d, 0))
        comps.append((bname, 0, 0))
        for idx, digit in enumerate(dd):
            comps.append((ctx.afrc_dnom[digit], dx_d0 + idx * w_d, 0))
        aname = f'{vname}.afrc.{SUF}'
        _add_composite(ctx, aname, comps, wk)
        ctx.afrc_vulg_pairs.append((vname, aname))

    ctx.log(
        f'added 36 encoded glyphs (ij, 13 Pinyin, 5 case partners, 17 vulgar fractions), '
        f'{len(ctx.lg_smcp)} smcp / {len(ctx.lg_c2sc)} c2sc mappings, and afrc stacked fractions'
    )


def features(ctx):
    J = ' '.join

    # ---- 1. Small caps (placed before 'main' so build.py hoists them to front) ----
    smcp_l = J(a for a, _ in ctx.lg_smcp)
    smcp_r = J(b for _, b in ctx.lg_smcp)
    c2sc_l = J(a for a, _ in ctx.lg_c2sc)
    c2sc_r = J(b for _, b in ctx.lg_c2sc)
    sc_fea = (
        f'lookup LATIN_GAPS_SMCP {{ sub [{smcp_l}] by [{smcp_r}]; }} LATIN_GAPS_SMCP;\n'
        f'lookup LATIN_GAPS_C2SC {{ sub [{c2sc_l}] by [{c2sc_r}]; }} LATIN_GAPS_C2SC;\n'
        f'feature smcp {{ lookup LATIN_GAPS_SMCP; }} smcp;\n'
        f'feature c2sc {{ lookup LATIN_GAPS_C2SC; }} c2sc;\n'
    )
    ctx.gsub(sc_fea, before='main')

    # ---- 2. OpenType afrc (GSUB + GPOS) -------------------------------------------
    # Build source->target figure lists covering all figure sets (incl. .numr/.dnom from U+2044)
    fig_src, fig_numr, fig_dnom = [], [], []
    suffixes = ['', '.pnum', '.tosf', '.osf', '.sc', '.sc.tf', '.numr', '.dnom']
    glyf_set = set(ctx.glyf.glyphs)
    for sfx in suffixes:
        for idx, d in enumerate(DIG):
            gn = d + sfx
            if gn in glyf_set:
                fig_src.append(gn)
                fig_numr.append(ctx.afrc_numr[idx])
                fig_dnom.append(ctx.afrc_dnom[idx])
    for sfx in ['', '.pnum', '.tosf', '.osf', '.sc', '.sc.tf']:
        gn7 = f'seven{sfx}.ss08'
        if gn7 in glyf_set:
            fig_src.append(gn7)
            fig_numr.append(ctx.afrc_numr[7])
            fig_dnom.append(ctx.afrc_dnom[7])

    sub_digits = [f'uni208{i}' for i in range(10) if f'uni208{i}' in glyf_set]
    slashes = [s for s in ('slash', 'slash.sc', 'fraction') if s in glyf_set]
    all_bars = [ctx.afrc_bars[(m, n)] for m in range(1, 5) for n in range(1, 5)]

    v_src = J(a for a, _ in ctx.afrc_vulg_pairs)
    v_dst = J(b for _, b in ctx.afrc_vulg_pairs)

    lines = [
        f'@LATIN_GAPS_AF_D = [{J(fig_src)}];',
        f'@LATIN_GAPS_AF_NUMR = [{J(ctx.afrc_numr)}];',
        f'@LATIN_GAPS_AF_DNOM = [{J(ctx.afrc_dnom)}];',
        f'@LATIN_GAPS_AF_SL = [{J(slashes)}];',
        f'@LATIN_GAPS_AF_BARS = [{J(all_bars)}];',
        f'lookup LATIN_GAPS_AFRC_VULG {{ sub [{v_src}] by [{v_dst}]; }} LATIN_GAPS_AFRC_VULG;',
        'lookup LATIN_GAPS_AFRC_EXP { sub uni215F by one fraction; } LATIN_GAPS_AFRC_EXP;',
    ]
    if len(sub_digits) == 10:
        lines.append(f'@LATIN_GAPS_AF_SUB = [{J(sub_digits)}];')
        lines.append(
            'lookup LATIN_GAPS_AFRC_N1 {\n'
            '  sub uni215F\' lookup LATIN_GAPS_AFRC_EXP [@LATIN_GAPS_AF_D @LATIN_GAPS_AF_SUB];\n'
            '} LATIN_GAPS_AFRC_N1;'
        )
        lines.append(
            f'lookup LATIN_GAPS_AFRC_SUBD {{\n'
            f'  sub [fraction @LATIN_GAPS_AF_D] @LATIN_GAPS_AF_SUB\' by [{J(DIG)}];\n'
            f'}} LATIN_GAPS_AFRC_SUBD;'
        )
    else:
        lines.append(
            'lookup LATIN_GAPS_AFRC_N1 {\n'
            '  sub uni215F\' lookup LATIN_GAPS_AFRC_EXP @LATIN_GAPS_AF_D;\n'
            '} LATIN_GAPS_AFRC_N1;'
        )

    # Single-sub helper lookups for each bar{m}{n} and digit conversion
    for m in range(1, 5):
        for n in range(1, 5):
            bname = ctx.afrc_bars[(m, n)]
            lines.append(
                f'lookup LATIN_GAPS_AFRC_B{m}{n} {{ sub @LATIN_GAPS_AF_SL by {bname}; }} LATIN_GAPS_AFRC_B{m}{n};'
            )
    lines.append(
        f'lookup LATIN_GAPS_AFRC_TON {{ sub [{J(fig_src)}] by [{J(fig_numr)}]; }} LATIN_GAPS_AFRC_TON;'
    )
    lines.append(
        f'lookup LATIN_GAPS_AFRC_TOD {{ sub [{J(fig_src)}] by [{J(fig_dnom)}]; }} LATIN_GAPS_AFRC_TOD;'
    )

    # Contextual bar selection (longest match first, ignoring chained slashes and >=5 digits)
    bar_rules = ['lookup LATIN_GAPS_AFRC_BAR {']
    for k in range(1, 5):
        seq = ' '.join(['@LATIN_GAPS_AF_D'] * k)
        bar_rules.append(f'  ignore sub @LATIN_GAPS_AF_SL {seq} @LATIN_GAPS_AF_SL\';')
        bar_rules.append(f'  ignore sub [@LATIN_GAPS_AF_SL @LATIN_GAPS_AF_BARS] {seq} @LATIN_GAPS_AF_SL\';')
        bar_rules.append(f'  ignore sub @LATIN_GAPS_AF_SL\' {seq} @LATIN_GAPS_AF_SL;')
    bar_rules.append('  ignore sub @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_SL\';')
    bar_rules.append('  ignore sub @LATIN_GAPS_AF_SL\' @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D;')
    for total_len in range(8, 1, -1):
        for m in range(4, 0, -1):
            n = total_len - m
            if 1 <= n <= 4:
                left = ' '.join(['@LATIN_GAPS_AF_D'] * m)
                right = ' '.join(['@LATIN_GAPS_AF_D'] * n)
                bar_rules.append(f'  sub {left} @LATIN_GAPS_AF_SL\' lookup LATIN_GAPS_AFRC_B{m}{n} {right};')
    bar_rules.append('} LATIN_GAPS_AFRC_BAR;')
    lines.extend(bar_rules)

    # Contextual digit conversion around the chosen bar
    lines.append(
        'lookup LATIN_GAPS_AFRC_NUM {\n'
        '  sub @LATIN_GAPS_AF_D\' lookup LATIN_GAPS_AFRC_TON @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_BARS;\n'
        '  sub @LATIN_GAPS_AF_D\' lookup LATIN_GAPS_AFRC_TON @LATIN_GAPS_AF_D @LATIN_GAPS_AF_D @LATIN_GAPS_AF_BARS;\n'
        '  sub @LATIN_GAPS_AF_D\' lookup LATIN_GAPS_AFRC_TON @LATIN_GAPS_AF_D @LATIN_GAPS_AF_BARS;\n'
        '  sub @LATIN_GAPS_AF_D\' lookup LATIN_GAPS_AFRC_TON @LATIN_GAPS_AF_BARS;\n'
        '} LATIN_GAPS_AFRC_NUM;'
    )
    lines.append(
        'lookup LATIN_GAPS_AFRC_DEN {\n'
        '  sub [@LATIN_GAPS_AF_BARS @LATIN_GAPS_AF_DNOM] @LATIN_GAPS_AF_D\' lookup LATIN_GAPS_AFRC_TOD;\n'
        '} LATIN_GAPS_AFRC_DEN;'
    )

    subd_call = ' lookup LATIN_GAPS_AFRC_SUBD;' if len(sub_digits) == 10 else ''
    lines.append(
        f'feature afrc {{\n'
        f'  lookup LATIN_GAPS_AFRC_VULG;\n'
        f'  lookup LATIN_GAPS_AFRC_N1;{subd_call}\n'
        f'  lookup LATIN_GAPS_AFRC_BAR;\n'
        f'  lookup LATIN_GAPS_AFRC_NUM;\n'
        f'  lookup LATIN_GAPS_AFRC_DEN;\n'
        f'}} afrc;'
    )
    ctx.gsub('\n'.join(lines) + '\n')

    # ---- GPOS positioning for dynamic afrc sequences ------------------------------
    w_d = ctx.afrc_wd
    gpos_lines = [
        f'@LATIN_GAPS_GP_NUMR = [{J(ctx.afrc_numr)}];',
        f'@LATIN_GAPS_GP_DNOM = [{J(ctx.afrc_dnom)}];',
    ]

    # Helper single-adjustment lookups by unique offset tuple
    pos_helpers = {}

    def helper_for(dx, dadv):
        key = (dx, dadv)
        if key not in pos_helpers:
            idx = len(pos_helpers) + 1
            lname = f'LATIN_GAPS_AFRC_SH{idx}'
            gpos_lines.append(
                f'lookup {lname} {{\n'
                f'  pos [@LATIN_GAPS_GP_NUMR @LATIN_GAPS_GP_DNOM] <{dx} 0 {dadv} 0>;\n'
                f'}} {lname};'
            )
            pos_helpers[key] = lname
        return pos_helpers[key]

    # Group bar{m}{n} by (m, K) for numerator shift and by (n, K) for denominator shift
    num_groups = defaultdict(list)
    den_groups = defaultdict(list)
    for m in range(1, 5):
        for n in range(1, 5):
            k = max(m, n)
            bname = ctx.afrc_bars[(m, n)]
            num_groups[(m, k)].append(bname)
            den_groups[(n, k)].append(bname)

    num_pos_rules = ['lookup LATIN_GAPS_AFRC_PNUM {']
    for (m, k), bnames in sorted(num_groups.items(), key=lambda kv: (-kv[0][0], kv[0][1])):
        wk = ctx.afrc_wk[k]
        dx_num = round((wk - m * w_d) / 2.0)
        hlp = helper_for(dx_num, 0)
        bcls = f'[{J(bnames)}]'
        for pos_idx in range(m):
            after_n = ' '.join(['@LATIN_GAPS_GP_NUMR'] * (m - 1 - pos_idx))
            before_n = ' '.join(['@LATIN_GAPS_GP_NUMR'] * pos_idx)
            left_ctx = (before_n + ' ') if before_n else ''
            right_ctx = (' ' + after_n + ' ' + bcls) if after_n else (' ' + bcls)
            num_pos_rules.append(f'  pos {left_ctx}@LATIN_GAPS_GP_NUMR\' lookup {hlp}{right_ctx};')
    num_pos_rules.append('} LATIN_GAPS_AFRC_PNUM;')

    bar_pos_rules = ['lookup LATIN_GAPS_AFRC_PBAR {']
    for m in range(1, 5):
        bnames = [ctx.afrc_bars[(m, n)] for n in range(1, 5)]
        shift = -m * w_d
        bar_pos_rules.append(f'  pos [{J(bnames)}] <{shift} 0 {shift} 0>;')
    bar_pos_rules.append('} LATIN_GAPS_AFRC_PBAR;')

    den_pos_rules = ['lookup LATIN_GAPS_AFRC_PDEN {']
    for (n, k), bnames in sorted(den_groups.items(), key=lambda kv: (-kv[0][0], kv[0][1])):
        wk = ctx.afrc_wk[k]
        dx_den = round((wk - n * w_d) / 2.0) - wk
        hlp_mid = helper_for(dx_den, 0)
        hlp_end = helper_for(dx_den, -n * w_d)
        bcls = f'[{J(bnames)}]'
        for pos_idx in range(n):
            before_d = ' '.join(['@LATIN_GAPS_GP_DNOM'] * pos_idx)
            left_ctx = bcls + (' ' + before_d if before_d else '')
            hlp = hlp_end if pos_idx == n - 1 else hlp_mid
            den_pos_rules.append(f'  pos {left_ctx} @LATIN_GAPS_GP_DNOM\' lookup {hlp};')
    den_pos_rules.append('} LATIN_GAPS_AFRC_PDEN;')

    gpos_lines.extend(num_pos_rules)
    gpos_lines.extend(bar_pos_rules)
    gpos_lines.extend(den_pos_rules)
    gpos_lines.append(
        'feature afrc {\n'
        '  lookup LATIN_GAPS_AFRC_PNUM;\n'
        '  lookup LATIN_GAPS_AFRC_PBAR;\n'
        '  lookup LATIN_GAPS_AFRC_PDEN;\n'
        '} afrc;'
    )
    ctx.gpos('\n'.join(gpos_lines) + '\n')


def _effective_kerning(gpos):
    """Precedence-aware effective pair kerning across all existing GPOS `kern` lookups."""
    idxs = sorted({
        i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern'
        for i in fr.Feature.LookupListIndex
    })
    tot = defaultdict(int)
    for i in idxs:
        lk = gpos.LookupList.Lookup[i]
        if lk.LookupType not in (2, 9):
            continue
        sts = [st.ExtSubTable if lk.LookupType == 9 else st for st in lk.SubTable]
        sts = [st for st in sts if st.Format in (1, 2) and hasattr(st, 'Coverage')]
        covsets = [set(st.Coverage.glyphs) for st in sts]
        lefts = set().union(*covsets) if covsets else set()
        for a in lefts:
            seen = set()
            for st, cs in zip(sts, covsets):
                if a not in cs:
                    continue
                if st.Format == 1:
                    for r in st.PairSet[st.Coverage.glyphs.index(a)].PairValueRecord:
                        if r.SecondGlyph not in seen:
                            seen.add(r.SecondGlyph)
                            v = (getattr(r.Value1, 'XAdvance', 0) or 0) if r.Value1 else 0
                            if v:
                                tot[(a, r.SecondGlyph)] += v
                else:
                    rec = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)]
                    for b, c in st.ClassDef2.classDefs.items():
                        if c and b not in seen:
                            v = (getattr(rec.Class2Record[c].Value1, 'XAdvance', 0) or 0) if rec.Class2Record[c].Value1 else 0
                            if v:
                                tot[(a, b)] += v
                    break
    return {k: v for k, v in tot.items() if v}


def _turn_deg(a, p, b):
    u = (p[0] - a[0], p[1] - a[1])
    v = (b[0] - p[0], b[1] - p[1])
    if u == (0, 0) or v == (0, 0):
        return 180.0
    return abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))


def _g1fix_inplace(g):
    """Restore smooth G1 tangents on integer coordinates without adding or deleting points."""
    c = [tuple(xy) for xy in g.coordinates]
    on = [bool(f & 1) for f in g.flags]
    s0 = 0
    for e in g.endPtsOfContours:
        idx = list(range(s0, e + 1))
        s0 = e + 1
        n = len(idx)
        if n < 3:
            continue
        for k in range(n):
            i, a, b = idx[k], idx[k - 1], idx[(k + 1) % n]
            if not on[i] or (on[a] and on[b]):
                continue
            t = _turn_deg(c[a], c[i], c[b])
            if not (0.3 < t < 15.0):
                continue
            if not on[a] and not on[b]:
                ax, ay = c[a]
                bx, by = c[b]
                l2 = (bx - ax) ** 2 + (by - ay) ** 2
                if l2 == 0:
                    continue
                r = ((c[i][0] - ax) * (bx - ax) + (c[i][1] - ay) * (by - ay)) / l2
                ideal = (ax + r * (bx - ax), ay + r * (by - ay))
                cands = [(round(ideal[0]) + dx, round(ideal[1]) + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
                q = min(cands, key=lambda q: (round(_turn_deg(c[a], q, c[b]), 2), math.dist(q, ideal)))
                if _turn_deg(c[a], q, c[b]) < t:
                    c[i] = q
            else:
                h, o = (b, a) if on[a] else (a, b)
                lo = math.dist(c[i], c[o])
                lh = math.dist(c[i], c[h])
                if lo == 0 or lh == 0:
                    continue
                d = ((c[i][0] - c[o][0]) / lo, (c[i][1] - c[o][1]) / lo)
                ideal = (c[i][0] + d[0] * lh, c[i][1] + d[1] * lh)
                cands = [(round(ideal[0]) + dx, round(ideal[1]) + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
                q = min(cands, key=lambda q: (round(_turn_deg(c[o], c[i], q), 2), math.dist(q, ideal)))
                if _turn_deg(c[o], c[i], q) < t:
                    c[h] = q
    g.coordinates = GlyphCoordinates(c)


def _finalize_deterministic_outlines(ctx):
    """Write weight-invariant quadratic contours across upright and italic masters."""
    glyf = ctx.glyf
    k_sl = ctx.ITALIC_K if ctx.ITALIC else 0.0
    yc_sl = ctx.ITALIC_YC

    # 1. Stacked dieresis + tone marks: exact tone polygon + two 8-point off-curve circles
    for mk_gn, (tone_float, t_ends, t_flags, dot_centers, r_dot, parent_gn) in ctx.lg_dier_marks.items():
        coords = [(round(x + k_sl * (y - yc_sl)), round(y)) for x, y in tone_float]
        flags = list(t_flags)
        ends = list(t_ends)
        a_dot = r_dot * (math.sqrt(2.0) - 1.0)
        ring = [
            (r_dot, -a_dot), (a_dot, -r_dot), (-a_dot, -r_dot), (-r_dot, -a_dot),
            (-r_dot, a_dot), (-a_dot, r_dot), (a_dot, r_dot), (r_dot, a_dot),
        ]
        for ccx, ccy in dot_centers:
            ccx_sl = ccx + k_sl * (ccy - yc_sl)
            for dx_r, dy_r in ring:
                coords.append((round(ccx_sl + dx_r), round(ccy + dy_r)))
                flags.append(0)
            ends.append(len(coords) - 1)
        mg = glyf[mk_gn]
        mg.coordinates = GlyphCoordinates(coords)
        mg.flags = array('B', flags)
        mg.endPtsOfContours = ends
        mg.numberOfContours = len(ends)
        mg.recalcBounds(glyf)
        ctx.hmtx[mk_gn] = (ctx.hmtx[mk_gn][0], mg.xMin)
        pg = glyf[parent_gn]
        pg.recalcBounds(glyf)
        ctx.hmtx[parent_gn] = (ctx.hmtx[parent_gn][0], pg.xMin)

    # 2. Stacked nut figures: exact scaled Mulish .dnom quadratics with non-deleting midpoint snap
    for gn, (sc_coords, d_ends, d_flags, dx, y_base) in ctx.lg_quad_figs.items():
        coords = [(round(x + dx + k_sl * (y + y_base - yc_sl)), round(y + y_base)) for x, y in sc_coords]
        flags = list(d_flags)
        ends = list(d_ends)
        s0 = 0
        for e in ends:
            m = e - s0 + 1
            if m >= 4:
                for i in range(m):
                    ii = s0 + i
                    ip = s0 + (i - 1) % m
                    inxt = s0 + (i + 1) % m
                    if flags[ii] == 1 and flags[ip] == 0 and flags[inxt] == 0:
                        xp, yp = coords[ip]
                        xn, yn = coords[inxt]
                        xi, yi = coords[ii]
                        if abs(xi - (xp + xn) / 2.0) <= 1.5 and abs(yi - (yp + yn) / 2.0) <= 1.5:
                            if (xp + xn) % 2 != 0:
                                xn += 1 if 2 * xi >= xp + xn else -1
                            if (yp + yn) % 2 != 0:
                                yn += 1 if 2 * yi >= yp + yn else -1
                            coords[inxt] = (xn, yn)
                            coords[ii] = ((xp + xn) // 2, (yp + yn) // 2)
            s0 = e + 1
        fg = glyf[gn]
        fg.coordinates = GlyphCoordinates(coords)
        fg.flags = array('B', flags)
        fg.endPtsOfContours = ends
        fg.numberOfContours = len(ends)
        _g1fix_inplace(fg)
        _g1fix_inplace(fg)
        fg.recalcBounds(glyf)
        ctx.hmtx[gn] = (ctx.hmtx[gn][0], fg.xMin)

    for vgn in ctx.lg_vulg_names:
        if vgn in glyf:
            cg = glyf[vgn]
            cg.recalcBounds(glyf)
            ctx.hmtx[vgn] = (ctx.hmtx[vgn][0], cg.xMin)

    for _vname, p_afrc in ctx.afrc_vulg_pairs:
        if p_afrc in glyf:
            cg = glyf[p_afrc]
            cg.recalcBounds(glyf)
            ctx.hmtx[p_afrc] = (ctx.hmtx[p_afrc][0], cg.xMin)

    # 3. Ǥ (uni01E4): splice 14-point crossbar deterministically onto cleaned 32-point G
    if 'uni01E4' in glyf and 'G' in glyf:
        gg = glyf['G']
        g_pts = [tuple(xy) for xy in gg.coordinates]
        g_flg = list(gg.flags)
        m_g = len(g_pts)
        c_pts, c_flg = [], []
        for i in range(m_g):
            if g_flg[i] == 1 and g_flg[(i - 1) % m_g] == 0 and g_flg[(i + 1) % m_g] == 0:
                xp, yp = g_pts[(i - 1) % m_g]
                xn, yn = g_pts[(i + 1) % m_g]
                xi, yi = g_pts[i]
                if abs(yn - yp) >= 80 and abs(xi - (xp + xn) / 2.0) <= 4.0 and abs(yi - (yp + yn) / 2.0) <= 4.0:
                    continue
            c_pts.append(g_pts[i])
            c_flg.append(g_flg[i])
        m_c = len(c_pts)
        k_hit = None
        for k in range(m_c):
            if all(c_flg[(k + j) % m_c] == 1 for j in range(6)):
                q1 = c_pts[(k + 1) % m_c]
                q2 = c_pts[(k + 2) % m_c]
                if abs(q1[1] - q2[1]) <= 1 and 250 <= q1[1] <= 345 and (q1[0] - q2[0]) >= 120:
                    k_hit = k
                    break
        assert k_hit is not None, f'uni01E4: could not locate 6-point chin corner run in G (len={m_c})'
        c_pts = c_pts[k_hit:] + c_pts[:k_hit]
        c_flg = c_flg[k_hit:] + c_flg[:k_hit]
        p0, p1, p2, p3, p4, p5 = c_pts[:6]
        throat_h = max(80, p1[1] - p0[1])
        bar_t = min(round(48 * (ctx.SH ** 0.58)), round(0.46 * throat_h))
        y0 = round((p0[1] + p1[1]) / 2.0 - bar_t / 2.0)
        y1 = y0 + bar_t
        inward_l = min(84, round((p1[0] - p2[0]) * 0.48))
        overhang_r = 52
        x_in_0 = round(p0[0] + (p1[0] - p0[0]) * (y0 - p0[1]) / (p1[1] - p0[1]))
        x_in_1 = round(p0[0] + (p1[0] - p0[0]) * (y1 - p0[1]) / (p1[1] - p0[1]))
        x_out_0 = round(p5[0] + (p4[0] - p5[0]) * (y0 - p5[1]) / (p4[1] - p5[1]))
        x_out_1 = round(p5[0] + (p4[0] - p5[0]) * (y1 - p5[1]) / (p4[1] - p5[1]))
        spliced = [
            p0,
            (x_in_0, y0), (x_in_0 - inward_l, y0), (x_in_1 - inward_l, y1), (x_in_1, y1),
            p1, p2, p3, p4,
            (x_out_1, y1), (x_out_1 + overhang_r, y1), (x_out_0 + overhang_r, y0), (x_out_0, y0),
            p5,
        ]
        ug = glyf['uni01E4']
        ug.coordinates = GlyphCoordinates(spliced + c_pts[6:])
        ug.flags = array('B', [1] * 14 + c_flg[6:])
        ug.endPtsOfContours = [14 + len(c_pts) - 6 - 1]
        ug.numberOfContours = 1
        ug.recalcBounds(glyf)
        ctx.hmtx['uni01E4'] = (ctx.hmtx['uni01E4'][0], ug.xMin)

    # 4. Canonical top-left start-point rotation on single-contour simple glyphs
    single_contour_names = ['uni0191', f'florin.sc.{SUF}'] + list(ctx.afrc_bars.values())
    for gn in single_contour_names:
        if gn not in glyf:
            continue
        sg = glyf[gn]
        if sg.isComposite() or sg.numberOfContours != 1:
            continue
        pts = [tuple(xy) for xy in sg.coordinates]
        flg = list(sg.flags)
        k0 = max(range(len(pts)), key=lambda i: (pts[i][1], -pts[i][0]))
        if k0:
            sg.coordinates = GlyphCoordinates(pts[k0:] + pts[:k0])
            sg.flags = array('B', flg[k0:] + flg[:k0])


def post(ctx):
    """Finalize weight-invariant quadratic outlines and emit LATIN_GAPS_KERN."""
    _finalize_deterministic_outlines(ctx)
    font = ctx.font
    gpos = font['GPOS'].table
    eff = _effective_kerning(gpos)

    by_first = defaultdict(list)
    by_second = defaultdict(list)
    for (a, b), v in eff.items():
        if a in TABULAR or b in TABULAR:
            continue
        by_first[a].append((b, v))
        by_second[b].append((a, v))

    new_pairs = {}
    new_set = set(ctx.lg_kern.keys())
    for g, (src_first, src_second) in ctx.lg_kern.items():
        if src_first:
            for b, v in by_first.get(src_first, ()):
                if b not in new_set:
                    new_pairs[(g, b)] = v
        if src_second:
            for a, v in by_second.get(src_second, ()):
                if a not in new_set:
                    new_pairs[(a, g)] = v

    for ga, (src_first_a, _) in ctx.lg_kern.items():
        if not src_first_a:
            continue
        for gb, (_, src_second_b) in ctx.lg_kern.items():
            if not src_second_b:
                continue
            v = eff.get((src_first_a, src_second_b), 0)
            if v:
                new_pairs[(ga, gb)] = v

    if not new_pairs:
        return

    fea_lines = [
        'languagesystem DFLT dflt; languagesystem latn dflt;',
        'lookup LATIN_GAPS_KERN {',
        '  lookupflag IgnoreMarks;',
    ]
    for (a, b), v in sorted(new_pairs.items()):
        fea_lines.append(f'  pos {a} {b} {v};')
    fea_lines.append('} LATIN_GAPS_KERN;')
    fea_lines.append('feature kern { lookup LATIN_GAPS_KERN; } kern;')

    tmp = TTFont()
    tmp.setGlyphOrder(font.getGlyphOrder())
    addOpenTypeFeaturesFromString(tmp, '\n'.join(fea_lines) + '\n', tables=['GPOS'])
    ctx._merge_table(gpos, tmp['GPOS'].table)
    ctx.log(f'kern: {len(new_pairs)} inherited pairs in LATIN_GAPS_KERN')

"""mathnotation: the notation lane of machine-learning prose: math accents on Latin and Greek
(ŷ θ̂ x̄ μ̃ ẋ ẍ), definition signs, independence, the rest of the circled operators, script
and double-struck letters, preference relations, the proportion sign, and the spacing of
angle brackets and bra-kets.

Except the existing-font script fallback, notation is drawn from Torchlette Sans's own parts at each weight, on the symbols
module's conventions: relations and binary operators take the 600-unit cell of + = <, sit
on the math axis (`LIN_AXIS`, the minus's centre) and use the minus's bar (`BAR`) as their
stroke, a vertical stroke 1.15 bars (`VB`).

Operators
- ML3 ≜ ≝ ≐ ≙ (U+225C, U+225D, U+2250, U+2259): Torchlette's = with a sign above it, the
  stack's top below the cap height: an open triangle (delta), "def" in the font's own d e f
  scaled to 0.36 and thickened back to 0.75 bar, the dot operator's dot, a wedge (the
  estimates sign). Noto Sans Math and STIX Two draw all four as = with the sign above.
- ML4 ⫫ (U+2AEB) two up tacks on one bar, the stems 2.2 strokes apart; Unicode has no
  negated form, so ⫫ + U+0338 and ⊥ + U+0338 become precomposed slashed forms through
  ccmp (`uni2AEB.not.mathnotation`, `uni22A5.not.mathnotation`).
- ML5 ⊘ ⊛ ⊖ (U+2298, U+229B, U+2296) on the ring of mathglyphs' ⊕ ⊗ ⊙ (radius 300,
  advance 720, strokes 1.1 and 1.0 bars) with a slash, the asterisk operator scaled inside,
  the minus's bar; the squared set ⊞ ⊟ ⊠ ⊡ (U+229E-22A1) on a square of the same strokes
  (half side 218, advance 600); the join
  ⋈ (U+22C8) two triangles meeting at their tips, the bar's weight.
- ML8 ≺ ≻ ≼ ≽ ⪯ ⪰ (U+227A-227D, U+2AAF-2AB0): < > with curved arms (each arm leaves the
  tip level and bends out to the end of the plain arm, as STIX Two's and Noto Sans Math's
  do); ≼ ≽ add a curved line parallel to the lower arm, ⪯ ⪰ the straight bar of ≤.
- ML9 ∷ (U+2237) four colon dots on the math axis, the ratio colon ∶ (U+2236) the colon
  centred on the axis; calt makes a colon a ratio colon next to a word that touches ∷ (a : b ∷ c : d,
  words of up to MN_ANALOGY_N letters, spaced or not), so both sides space alike.
- SH5 ◉ (U+25C9) the ui module's ○ with a disc inside (observed node), kept upright in
  the italic as ui keeps its circles.

Letters
- ML7 script capitals and legacy ℯ ℊ ℴ: complete existing Noto Sans Math Regular
  outlines, scaled uniformly to the current H cap height. Original donor advances,
  sidebearings and ink placement share that same global scale. The donor weight is fixed across styles. Italics receive the build's
  existing final oblique transform. No script skeleton is traced or stroked.
- ML10 double-struck capitals and figures 𝔸 𝔹 𝔻 𝔽 𝔾 𝕀 𝕁 𝕂 𝕃 𝕄 𝕆 𝕊 𝕋 𝕌 𝕍 𝕎 𝕏 𝕐 and
  𝟘 𝟚-𝟡 from the symbols module's `doublestruck` (read through mathletters' `ds_glyphs`),
  which draws the whole double-struck set, ℝ ℕ ℤ ℚ ℂ ℙ ℍ 𝔼 𝟙 too, after Noto Sans Math's
  design (one hairline per stroke; the thick strokes doubled as bands closed at both ends,
  round ones by a straight inline) from Torchlette's capitals and lining figures.

Layout
- ML1 mark: one mark-to-base lookup (before Mulish's own, so Mulish's mkmk stacks on it)
  with Mulish's above-mark classes and anchors for the bases Mulish and otfeatures leave
  without anchors: the Greek letters (the greek module's), ℓ ℏ ϑ ϕ ϵ ϖ ϱ, and the letterlike
  capitals of this module, mathletters and symbols. The anchor sits on the letter's optical
  axis (Mulish's rule, the middle of the ink in the top fifth; over the x-height part for an
  ascender letter; for a script capital the centroid of the ink at 0.3-0.8 of the cap height,
  moved along the script's slant) at Mulish's heights: 16 under a flat x-height top (454), 26 under an ascender,
  on the cap height for capitals, whose marks become Mulish's .case forms through ccmp as
  after a Latin capital. Accented text in the italic follows the reslant.
- ML4 ccmp: the slashed ⫫ and ⊥ above.
- ML9 calt: the ratio colon above.
- SH4 calt + kern: inside ⟨ ⟩ a | becomes `bar.braket.mathnotation`, the bar cut to the
  brackets' height (0 to the cap height) so ⟨ψ|φ⟩ reads as one bracket; kern: Mulish's ⟨ ⟩
  stand in a 600-unit cell with 217 units each side, so ⟨ and ⟩ are kerned against every
  Latin and Greek letter, the math letters and the bra-ket bar so the smallest ink gap
  (profiles measured every 12 units of height) is the one ( or ) leaves with Mulish's
  kerning. Figures are left out: kern.py forbids kerning the tabular default figures.
- LG5 kern: ⟦ ⟧ against the same letters, the same way.

Feature tags: extends GSUB ccmp and calt and GPOS mark and kern. Glyph names: standard
production names (uniXXXX, uXXXXX) for encoded glyphs; unencoded ones end in
`.mathnotation`. GDEF: every glyph added here is a base. Script donor glyphs replace existing script mappings in place.
Code points outside the Makefile's web subset ranges: U+2A00-2AFF (⫫ ⪯ ⪰) and the SMP
letters U+1D49C-1D4B5, U+1D538-1D550, U+1D7D8-1D7E1. Knobs (environment): MN_ANALOGY_N (12).
"""
import importlib.util
import math
import os
import sys
import unicodedata

import pathops

HERE = os.path.dirname(os.path.abspath(__file__))
SUF = 'mathnotation'

TOP_MARKS = ['uni0302', 'tildecomb', 'uni0304', 'uni0307', 'uni0308']   # the five math accents


def _sibling(name, alias):
    """Another module as the build loaded it (tsmod_<name>), else loaded from beside this file."""
    mod = sys.modules.get(f'tsmod_{name}')
    if mod is None:
        spec = importlib.util.spec_from_file_location(alias, os.path.join(HERE, f'{name}.py'))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------ glyphs
def glyphs(ctx):
    c = ctx
    order = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()
    made = ctx.made = []
    ctx.groups = {}

    def put(cp, path, adv, name=None, group=None):
        name = name or (f'u{cp:04X}' if cp and cp > 0xFFFF else f'uni{cp:04X}')
        assert name not in order, name
        assert cp is None or cp not in cmap, f'U+{cp:04X} already mapped to {cmap[cp]}'
        c.add(name, path, round(adv)); c.GDEF_CLASS[name] = 1
        if cp is not None: ctx.map(cp, name)
        made.append(name); order.add(name)
        if group: ctx.groups.setdefault(group, []).append(name)
        return name

    ctx.put = put
    if _format12(c): ctx.log('cmap: format 12 subtables (3,10) and (0,4) added, copies of the best cmap')
    _operators(c, put)
    _braket(c, put)
    _doublestruck(c, put)
    _script(c, put)
    ctx.log(f'{len(made)} glyphs')


def _format12(c):
    """Format 12 Unicode subtables, (3,10) and (0,4), copies of the best cmap, unless the font
    has them already (mathletters adds them when it runs, before this module)."""
    from fontTools.ttLib.tables._c_m_a_p import cmap_format_12
    cmap = c.font['cmap']
    if any(t.isUnicode() and t.format in (12, 13) for t in cmap.tables): return False
    best = dict(c.font.getBestCmap())
    for plat, enc in ((3, 10), (0, 4)):
        t = cmap_format_12(12); t.platformID = plat; t.platEncID = enc; t.language = 0; t.cmap = dict(best)
        cmap.tables.append(t)
    return True


def _operators(c, put):
    A, BAR = c.LIN_AXIS, c.BAR
    rect, poly, union, diff, clip, band = c.rect, c.poly, c.union, c.diff, c.clip, c.band
    ellipse, transformed, path_of, W, mv, mirror = c.ellipse, c.transformed, c.path_of, c.W, c.mv, c.mirror
    hspans, vspans = c.hspans, c.vspans
    VB = BAR * 1.15
    TH, TV = BAR, BAR * 1.1

    def flipv(p, axis): return transformed(p, (1, 0, 0, -1, 0, 2 * axis))

    def centre(p, adv=600):
        b = p.bounds; return mv(p, (adv - b[0] - b[2]) / 2)

    def stroked(p, w, cap=pathops.LineCap.BUTT_CAP, join=pathops.LineJoin.MITER_JOIN, limit=4):
        q = pathops.Path(p); q.stroke(w, cap, join, limit); q.convertConicsToQuads(); q.simplify()
        return q

    def cubic(p0, p1, p2, p3):
        q = pathops.Path(); pen = q.getPen(); pen.moveTo(p0); pen.curveTo(p1, p2, p3); pen.endPath(); return q

    def thicken(p, d):
        if d <= 0: return p
        s = pathops.Path(p); s.stroke(2 * d, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        s.convertConicsToQuads(); return union(p, s)

    eq = path_of('equal'); eb = eq.bounds                     # = : 53..547, its top bar's top at eb[3]
    top0 = eb[3] + 0.9 * BAR                                  # where a sign above = starts
    CAPH = path_of('H').bounds[3]

    # ---- ML3 definition signs: = with a sign above ------------------------------------------
    # delta-equal: an open triangle, its stroke 0.85 bar, as wide as the = is tall
    th3 = 0.85 * BAR; tw = 0.6 * (eb[2] - eb[0]); thh = min(tw * 0.82, CAPH - top0)
    tri_o = poly([(300 - tw / 2, top0), (300 + tw / 2, top0), (300, top0 + thh)])
    # the inner triangle: the outer one inset by th3 across each side
    k = math.hypot(tw / 2, thh); sinb = thh / k; cosb = (tw / 2) / k
    ix = th3 / sinb * (1 + cosb)                               # inset of the base corners along x
    tri_i = poly([(300 - tw / 2 + ix, top0 + th3), (300 + tw / 2 - ix, top0 + th3),
                  (300, top0 + thh - th3 / cosb)])
    put(0x225C, union(eq, diff(tri_o, tri_i)), 600)
    # "def" over equals: the font's d e f at 0.36, thickened back to 0.75 bar
    sc = 0.43; lstem = (lambda s: s[1] - s[0])(hspans(path_of('l'), 300)[0])
    word = []; x = 0
    for n in ('d', 'e', 'f'):
        p = transformed(path_of(n), (sc, 0, 0, sc, x, 0)); word.append(p); x += sc * W(n) - 6
    dw = thicken(union(*word), (0.75 * BAR - sc * lstem) / 2)
    db = dw.bounds
    dw = mv(dw, 300 - (db[0] + db[2]) / 2, top0 + 10 - db[1])
    put(0x225D, union(eq, dw), 600)
    # approaches the limit: the dot operator's dot over =
    pc = path_of('periodcentered'); pb = pc.bounds; dr = (pb[3] - pb[1]) / 2
    put(0x2250, union(eq, mv(pc, 300 - (pb[0] + pb[2]) / 2, top0 + 25 + dr - (pb[1] + pb[3]) / 2)), 600)
    # estimates: a wedge over =, the and-sign's angle, 0.85 bar
    wh = 0.7 * thh
    wedge = c.stroke_line([(300 - tw / 2, top0), (300, top0 + wh), (300 + tw / 2, top0)], th3, limit=8)
    put(0x2259, union(eq, clip(wedge, (0, top0, 600, 2000))), 600)

    # ---- ML4 independence -------------------------------------------------------------------
    tack_h = 650
    gap4 = 2.2 * VB                                           # between the stems: Noto's and STIX's ⫫ stand a third of the bar apart
    xs = (300 - gap4 / 2 - VB, 300 + gap4 / 2)
    dtack = union(rect(70, 0, 530, BAR), *[rect(x0, 0, x0 + VB, tack_h) for x0 in xs])
    put(0x2AEB, dtack, 600)
    slash = band((300 - 165, -40), (300 + 165, tack_h + 40), BAR)
    put(None, union(dtack, slash), 600, name=f'uni2AEB.not.{SUF}'); c.GDEF_CLASS[f'uni2AEB.not.{SUF}'] = 2
    put(None, union(path_of('uni22A5'), slash) if 'uni22A5' in c.font.getGlyphOrder()
        else union(rect(70, 0, 530, BAR), rect(300 - VB / 2, 0, 300 + VB / 2, tack_h), slash), 600, name=f'uni22A5.not.{SUF}')
    c.GDEF_CLASS[f'uni22A5.not.{SUF}'] = 2                   # ligatures of the sign and U+0338

    # ---- ML5 circled and squared operators -------------------------------------------------
    # the circled ones on mathglyphs' ring for ⊕ ⊗ ⊙ (radius 300, advance 720)
    RC, CX = 300, 360
    ring = diff(ellipse(CX, A, RC, RC), ellipse(CX, A, RC - TV, RC - TH))
    dg = (RC - 10) / math.sqrt(2)
    put(0x2298, union(ring, band((CX - dg, A - dg), (CX + dg, A + dg), BAR)), 720)
    put(0x2296, union(ring, rect(CX - RC + 5, A - BAR / 2, CX + RC - 5, A + BAR / 2)), 720)
    ast = path_of('asterisk'); ab = ast.bounds; s_a = 0.78 * 2 * (RC - TV) / (ab[2] - ab[0])
    a2 = transformed(ast, (s_a, 0, 0, s_a, 0, 0)); a2 = thicken(a2, (1 - s_a) * 18)
    a2b = a2.bounds
    put(0x229B, union(ring, mv(a2, CX - (a2b[0] + a2b[2]) / 2, A - (a2b[1] + a2b[3]) / 2)), 720)
    RR = 230                                                  # the squared set keeps the old size
    S = RR - 12                                               # the square's half side: optically as big as the ring
    sq = diff(rect(300 - S, A - S, 300 + S, A + S), rect(300 - S + TV, A - S + TH, 300 + S - TV, A + S - TH))
    put(0x229E, union(sq, rect(300 - S, A - BAR / 2, 300 + S, A + BAR / 2), rect(300 - VB / 2, A - S, 300 + VB / 2, A + S)), 600)
    put(0x229F, union(sq, rect(300 - S, A - BAR / 2, 300 + S, A + BAR / 2)), 600)
    inner = rect(300 - S + TV / 2, A - S + TH / 2, 300 + S - TV / 2, A + S - TH / 2)
    put(0x22A0, union(sq, clip(union(band((300 - S, A - S), (300 + S, A + S), BAR), band((300 - S, A + S), (300 + S, A - S), BAR)), inner.bounds)), 600)
    put(0x22A1, union(sq, mv(pc, 300 - (pb[0] + pb[2]) / 2, A - (pb[1] + pb[3]) / 2)), 600)
    # join: two triangles meeting at their tips, the outer sides upright, 0.95 bar
    hj = 210; xj0, xj1 = 70, 530
    bow = union(c.stroke_line([(xj0 + VB / 2, A - hj), (xj1 - VB / 2, A + hj)], BAR, limit=4),
                c.stroke_line([(xj0 + VB / 2, A + hj), (xj1 - VB / 2, A - hj)], BAR, limit=4))
    bow = clip(bow, (xj0, A - hj, xj1, A + hj))
    put(0x22C8, union(bow, rect(xj0, A - hj, xj0 + VB, A + hj), rect(xj1 - VB, A - hj, xj1, A + hj)), 600)

    # ---- ML8 preference relations: < with curved arms --------------------------------------
    lt = path_of('less'); lb = lt.bounds                      # 53..547, 35..539: the arms' ends cut upright
    t_arm = BAR * 1.02
    def prec(y_lo, y_hi, x0=lb[0], x1=lb[2]):
        """≺ between heights y_lo and y_hi: each arm's medial line leaves the tip level and
        bends out to the plain arm's end; the arms are cut upright at x1."""
        yc = (y_lo + y_hi) / 2; h = (y_hi - y_lo) / 2 - t_arm * 0.55
        L = x1 - x0
        # a circular arc, level at the tip, through the plain arm's end
        H = h * 1.08; R = (L * L + H * H) / (2 * H)
        def arm(sgn):
            q = pathops.Path(); pen = q.getPen(); n = 24
            a1 = math.asin(min(1.0, (L + 30) / R))
            for i in range(n + 1):
                t = a1 * i / n
                pt = (x0 + t_arm * 0.2 + R * math.sin(t), yc + sgn * R * (1 - math.cos(t)))
                pen.moveTo(pt) if i == 0 else pen.lineTo(pt)
            pen.endPath(); return q
        q = union(stroked(arm(1), t_arm, join=pathops.LineJoin.ROUND_JOIN), stroked(arm(-1), t_arm, join=pathops.LineJoin.ROUND_JOIN))
        return clip(q, (x0, y_lo - 50, x1, y_hi + 50)), arm(-1)
    pr, _ = prec(lb[1], lb[3])
    put(0x227A, pr, 600)
    put(0x227B, mirror(pr, 300), 600)
    le = path_of('lessequal'); leb = le.bounds               # ≤: chevron 112..535 over a bar 0..53
    chev_lo = min(y0 for y0, y1 in vspans(le, 540) if y0 > BAR + 5)
    pr2, low_arm = prec(chev_lo, leb[3])
    put(0x2AAF, union(pr2, rect(lb[0], 0, lb[2], BAR)), 600)
    put(0x2AB0, mirror(union(pr2, rect(lb[0], 0, lb[2], BAR)), 300), 600)
    # ≼: the lower arm's curve again under the sign, as far below it as ≤'s bar is below its
    # chevron, then the whole stack set on the baseline
    gap_le = chev_lo - BAR
    curve = clip(mv(stroked(low_arm, t_arm, join=pathops.LineJoin.ROUND_JOIN), 0, -(gap_le + t_arm)), (lb[0] + 2, -1000, lb[2], 2000))
    pr3 = union(pr2, curve); b3 = pr3.bounds
    pr3 = mv(pr3, 0, -b3[1])
    put(0x227C, pr3, 600)
    put(0x227D, mirror(pr3, 300), 600)

    # ---- ML9 proportion and ratio ---------------------------------------------------------
    col = path_of('colon'); cb = col.bounds
    colA = mv(col, 0, A - (cb[1] + cb[3]) / 2)
    cw = cb[2] - cb[0]
    lsb = 70
    put(0x2236, mv(colA, lsb - cb[0]), cw + 2 * lsb)
    pitch = cw + 0.9 * cw                                      # the dots' horizontal pitch: the vertical one is larger
    put(0x2237, union(mv(colA, lsb - cb[0]), mv(colA, lsb - cb[0] + pitch)), cw + pitch + 2 * lsb)

    # ---- SH5 observed node: ui's ○ with a disc ------------------------------------------------
    hp = path_of('H'); Hb = hp.bounds; CH = Hb[3]; CC = CH / 2
    US = (lambda s: s[1] - s[0])(vspans(hp, (Hb[0] + Hb[2]) / 2)[0])
    R = CH / 2 + 9; Rd = R - US - max(0.75 * US, 0.12 * R)
    eye = union(diff(ellipse(R, CC, R, R), ellipse(R, CC, R - US, R - US)), ellipse(R, CC, Rd, Rd))
    K, YC = c.ITALIC_K, c.ITALIC_YC
    if K: eye = transformed(mv(eye, K * (CC - YC)), (1, 0, -K, 1, K * YC, 0))
    put(0x25C9, mv(eye, 60), 2 * R + 120)


def _braket(c, put):
    """SH4: | cut to the angle brackets' height, for ⟨ψ|φ⟩."""
    br = c.path_of('uni27E8').bounds
    bar = c.path_of('bar')
    put(None, c.clip(bar, (-1000, br[1], 3000, br[3])), c.W('bar'), name=f'bar.braket.{SUF}')


DS_SET = [(0x1D538, 'A'), (0x1D539, 'B'), (0x1D53B, 'D'), (0x1D53D, 'F'), (0x1D53E, 'G'), (0x1D540, 'I'),
          (0x1D541, 'J'), (0x1D542, 'K'), (0x1D543, 'L'), (0x1D544, 'M'), (0x1D546, 'O'), (0x1D54A, 'S'),
          (0x1D54B, 'T'), (0x1D54C, 'U'), (0x1D54D, 'V'), (0x1D54E, 'W'), (0x1D54F, 'X'), (0x1D550, 'Y'),
          (0x1D7D8, 'zero'), (0x1D7DA, 'two'), (0x1D7DB, 'three'), (0x1D7DC, 'four'), (0x1D7DD, 'five'),
          (0x1D7DE, 'six'), (0x1D7DF, 'seven'), (0x1D7E0, 'eight'), (0x1D7E1, 'nine')]


def _doublestruck(c, put):
    """ML10: the double-struck capitals and figures, from the symbols module's `doublestruck`
    (read through mathletters' `ds_glyphs`), which draws the whole double-struck set."""
    ml = _sibling('mathletters', 'tsmod_mathletters_for_mathnotation')
    ds = ml.ds_glyphs(c, [base for _, base in DS_SET])
    for cp, base in DS_SET:
        put(cp, ds[base][0], round(ds[base][1]))
    s_ = c.ds_strokes
    c.log(f"double-struck: hairline {s_['t']:.1f}, gap {s_['g']:.1f}, doubled stroke {s_['D']:.1f}, crescent {s_['DR']:.1f}")


def _area(p):
    """The net area of a path (counters negative when wound as counters)."""
    from fontTools.pens.areaPen import AreaPen
    a = AreaPen(); p.draw(a); return a.value


def _level_heights(*paths, eps=2 ** -8):
    """The paths with their point heights grouped and each group made one height: the
    first height in the group that the first path has, else the lowest. Sorted heights
    join a group while each is within eps of the one before, so a group's total span (and
    a point's movement) can exceed eps; over the tested grid (every double-struck letter
    in the 14 named styles and at Mulish wght 300-900 in steps of 10) the largest was
    about 0.011 unit.

    The hollowing's counters touch the heights of the outline's extremes: a stroke's inner
    edge has its leftmost and rightmost points at the heights of the outer edge's, and the
    stroker and the stretch put them a float32 unit (2^-15 at 339) off. skia-pathops orders
    contours after every op and simplify (build.py's add() too) by testing each contour's
    on-curve points with SkPath::contains, and a point one unit below an on-curve vertex
    of the enclosing contour can read as outside (observed; the cause inside
    SkPath::contains is inferred, not read from Skia's source). The counter is then wound as
    an outer contour and filled (𝟞 in Bold and at wght 330, 360 and 680, its left side
    solid). At one height, or eps apart, the test is exact. eps, the gap between adjacent
    heights below which they join, is 2^-8 unit, 64 float32
    units or more below 1024, and far under the font's 1-unit grid. `_doublestruck` levels
    a letter's heights only when its ink comes out wrong, so the others keep their points."""
    from fontTools.pens.recordingPen import RecordingPen
    recs = []
    for p in paths:
        r = RecordingPen(); p.draw(r); recs.append(r.value)
    ys = lambda rec: {pt[1] for _, args in rec for pt in args if pt is not None}
    first = ys(recs[0]); level = {}
    group = []
    for y in sorted(set().union(*map(ys, recs))) + [math.inf]:
        if group and y - group[-1] > eps:
            rep = next((v for v in group if v in first), group[0])
            for v in group: level[v] = rep
            group = []
        group.append(y)
    out = []
    for rec in recs:
        q = pathops.Path(); pen = q.getPen()
        for op, args in rec:
            getattr(pen, op)(*[None if pt is None else (pt[0], level[pt[1]]) for pt in args])
        out.append(q)
    return out


def _spline(pts, closed=False):
    """A Catmull-Rom spline through pts as an open cubic path (closed: wrapped round)."""
    if closed: pts = list(pts[:-1]) if pts[0] == pts[-1] else list(pts)
    p = pathops.Path(); pen = p.getPen(); n = len(pts)
    P = (lambda i: pts[i % n]) if closed else (lambda i: pts[max(0, min(n - 1, i))])
    pen.moveTo(pts[0])
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        pen.curveTo((p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6),
                    (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6), p2)
    pen.endPath()
    return p


def _script(c, put):
    """Direct fixed-weight Noto Sans Math outlines; ordinary build stages apply once."""
    import hashlib
    from fontTools.ttLib import TTFont
    from fontTools.pens.transformPen import TransformPen
    resource = os.path.join(HERE, '..', 'notosansmath', 'NotoSansMath-Regular.ttf')
    with open(resource, 'rb') as source:
        if hashlib.sha256(source.read()).hexdigest() != '3f495fe933c06786e4d5f6d86b8ee70b6753a68ee3b9d87528726de0f6e2c47d':
            raise ValueError('script donor resource hash mismatch')
    with TTFont(resource, recalcTimestamp=False) as donor:
        cmap = donor.getBestCmap(); glyphs = donor.getGlyphSet()
        missing = [cp for cp in SCRIPT_CODEPOINTS if cp not in cmap]
        if missing: raise ValueError(f'script donor missing {missing}')
        cap = donor['OS/2'].sCapHeight
        if cap <= 0: raise ValueError('script donor lacks a positive cap height')
        scale = c.path_of('H').bounds[3] / cap
        mapped = c.font.getBestCmap()
        for cp in SCRIPT_CODEPOINTS:
            path = pathops.Path()
            glyphs[cmap[cp]].draw(TransformPen(path.getPen(), (scale, 0, 0, scale, 0, 0)))
            advance = donor['hmtx'][cmap[cp]][0] * scale
            if cp in mapped:
                name = mapped[cp]
                GLYPH_OVERRIDE.add(name)
                c.add(name, path, round(advance)); c.GDEF_CLASS[name] = 1
                c.map(cp, name)
                if name not in c.made: c.made.append(name)
            else:
                put(cp, path, advance)
    c.log('29 script glyphs: direct Noto Sans Math Regular outlines; fixed donor weight')


# ------------------------------------------------------------------------------ features
TOP, BOT, OVER = 0, 2, 5
AXIS_FIX = {}          # glyph -> share of the ink box for the above anchor's x, where the rule misreads


def _letters(ctx):
    """The cmap's letters this module gives anchors and kerning: Greek, the letterlike and
    mathematical alphanumeric letters, ı ȷ ℓ ℏ; base letters only (no precomposed ones)."""
    out = {}
    for u, g in sorted(ctx.font.getBestCmap().items()):
        ch = chr(u); cat = unicodedata.category(ch)
        if not cat.startswith('L') and not (0x1D7CE <= u <= 0x1D7FF): continue
        if unicodedata.decomposition(ch) and not unicodedata.decomposition(ch).startswith('<'): continue
        if 0x370 <= u <= 0x3FF or 0x2100 <= u <= 0x214F or 0x1D400 <= u <= 0x1D7FF or u in (0x131, 0x237):
            out.setdefault(g, u)
    return out


def _anchor_top(ctx, otf, n, u):
    """The above anchor for glyph n (code point u): Mulish's rules (see the docstring)."""
    p = ctx.path_of(n); b = p.bounds
    if b is None or b == (0, 0, 0, 0): return None
    geo = otf._geometric(ctx, n)
    if TOP not in geo: return None
    x, y = geo[TOP]
    ft = otf._flat_top(ctx, n, p)
    cat = unicodedata.category(chr(u))
    upper = cat == 'Lu' or (0x1D400 <= u <= 0x1D7FF and unicodedata.name(chr(u), '').find('CAPITAL') >= 0) \
        or unicodedata.name(chr(u), '').startswith('SCRIPT CAPITAL') or unicodedata.name(chr(u), '').startswith('DOUBLE-STRUCK CAPITAL') \
        or unicodedata.name(chr(u), '').startswith('BLACK-LETTER CAPITAL')
    digit = 0x1D7CE <= u <= 0x1D7FF
    if upper or digit:
        y = round(705 + max(0, ft - 714))
    elif ft > 560:                                            # an ascender: over the x-height part, 26 under the top
        xm = otf._band_mid(ctx, p, 0.8 * ctx.XH, ctx.XH + 10)
        if xm is not None: x = round(xm)
        y = round(ft - 26)
    if unicodedata.name(chr(u), '').startswith(('SCRIPT', 'MATHEMATICAL SCRIPT')):
        from fontTools.pens.statisticsPen import StatisticsPen
        sp = StatisticsPen(); ctx.clip(p, (-3000, 0.3 * 705, 5000, 0.8 * 705)).draw(sp)   # a swash or ball would pull a band's middle
        if sp.area: x = round(sp.meanX + 0.15 * (y - 0.55 * 705))   # the ink's centroid, along the script's slant to the anchor
    if n in AXIS_FIX: x = round(b[0] + AXIS_FIX[n] * (b[2] - b[0]))
    return (x, y), upper or digit


def features(ctx):
    J = ' '.join
    order = set(ctx.font.getGlyphOrder())
    otf = _sibling('otfeatures', 'tsmod_otfeatures_for_mathnotation')
    marks, bases, _ligs, _mk2 = otf._mark_data(ctx.font)

    # ---- GSUB ccmp: slashed ⫫ and ⊥ ----------------------------------------------------------
    nots = [(b, f'{b}.not.{SUF}') for b in ('uni2AEB', 'uni22A5') if b in order and f'{b}.not.{SUF}' in order]
    if 'uni0338' in order and nots:
        ctx.gsub('lookup MATHNOTATION_NOT {\n' + '\n'.join(f'  sub {a} uni0338 by {b};' for a, b in nots) +
                 '\n} MATHNOTATION_NOT;\nfeature ccmp { lookup MATHNOTATION_NOT; } ccmp;')

    # ---- GPOS mark: anchors for Greek and the math letters -----------------------------------
    letters = _letters(ctx)
    top_marks = {m: a for m, (cl, a) in marks.items() if cl == TOP}
    anchors, caps = {}, []
    for g, u in letters.items():
        if TOP in bases.get(g, {}): continue
        r = _anchor_top(ctx, otf, g, u)
        if r is None: continue
        anchors[g], is_cap = r
        if is_cap: caps.append(g)
    ctx.anchors = anchors
    lines = [f'markClass {m} <anchor {a[0]} {a[1]}> @MATHNOTATION_TOP;' for m, a in sorted(top_marks.items())]
    lines.append('lookup MATHNOTATION_MARK {')
    lines += [f'  pos base {g} <anchor {x} {y}> mark @MATHNOTATION_TOP;' for g, (x, y) in anchors.items()]
    lines.append('} MATHNOTATION_MARK;\nfeature mark { lookup MATHNOTATION_MARK; } mark;')
    ctx.gpos('\n'.join(lines), before='mulish')
    # the capitals take the .case marks, as Mulish's ccmp gives them after a Latin capital
    case = [(m, f'{m}.case') for m in sorted(top_marks) if f'{m}.case' in order]
    if caps and case:
        ctx.gsub(f"lookup MATHNOTATION_CASEMARK {{ sub [{J(caps)}] [{J(a for a, _ in case)}]' by [{J(b for _, b in case)}]; }} MATHNOTATION_CASEMARK;\n"
                 "feature ccmp { lookup MATHNOTATION_CASEMARK; } ccmp;")

    # ---- GSUB calt: the ratio colon beside ∷, the bra-ket bar ----------------------------------
    N = int(ctx.P('MN_ANALOGY_N', 12))
    word = sorted({g for u, g in ctx.font.getBestCmap().items() if unicodedata.category(chr(u))[0] in 'LN'})
    ctx.gsub(f'@MATHNOTATION_W = [{J(word)}];', after='classes')
    rules = []
    if 'uni2237' in order and 'uni2236' in order:
        for n in range(1, N + 1):
            w = ' '.join(['@MATHNOTATION_W'] * n)
            for s1 in ('', 'space '):
                for s2 in ('', 'space '):
                    rules.append(f"  sub colon' {s1}{w} {s2}uni2237 by uni2236;")
                    rules.append(f"  sub uni2237 {s1}{w} {s2}colon' by uni2236;")
        ctx.gsub('lookup MATHNOTATION_RATIO {\n  lookupflag IgnoreMarks;\n' + '\n'.join(rules) + '\n} MATHNOTATION_RATIO;\n'
                 'feature calt { lookup MATHNOTATION_RATIO; } calt;')
    bk = f'bar.braket.{SUF}'
    if bk in order and 'uni27E8' in order:
        inside = f'[@MATHNOTATION_W space comma]'
        rules = []
        for n in range(0, 9):
            w = ' '.join([inside] * n)
            rules.append(f"  sub uni27E8 {w} bar' by {bk};".replace('  ', ' ').replace('sub', '  sub', 1))
            rules.append(f"  sub bar' {w} uni27E9 by {bk};".replace('  ', ' ').replace('sub', '  sub', 1))
        ctx.gsub('lookup MATHNOTATION_BRAKET {\n  lookupflag IgnoreMarks;\n' + '\n'.join(rules) + '\n} MATHNOTATION_BRAKET;\n'
                 'feature calt { lookup MATHNOTATION_BRAKET; } calt;')

    # ---- GPOS kern: ⟨ ⟩ ⟦ ⟧ against letters, figures and the bra-ket bar -------------------------
    kg = sorted({g for u, g in ctx.font.getBestCmap().items() if 0x41 <= u <= 0x5A or 0x61 <= u <= 0x7A
                 or 0x391 <= u <= 0x3C9 or u in (0x3D1, 0x3D5, 0x3D6, 0x3F5, 0x2113, 0x131) or 0x2100 <= u <= 0x214F and unicodedata.category(chr(u))[0] == 'L'
                 or 0x1D400 <= u <= 0x1D7FF})
    pairs = _bracket_kerns(ctx, kg + ([bk] if bk in order else []))
    ctx.kerns = pairs
    if pairs:
        ctx.gpos('lookup MATHNOTATION_KERN {\n' + '\n'.join(f'  pos {a} {b} {v};' for (a, b), v in pairs.items()) +
                 '\n} MATHNOTATION_KERN;\nfeature kern { lookup MATHNOTATION_KERN; } kern;')
    ctx.log(f'mark: {len(anchors)} bases ({len(caps)} capitals with .case marks); kern: {len(pairs)} bracket pairs')


def _profile(ctx, n, side, ys):
    """The ink's leftmost (side 'L') or rightmost ('R') x at each height in ys (None where none)."""
    p = ctx.path_of(n); out = []
    for y in ys:
        s = ctx.hspans(p, y)
        out.append(None if not s else (s[0][0] if side == 'L' else s[-1][1]))
    return out


def _gap(ctx, left, right, ys):
    """The smallest ink gap between left and right set side by side (no kerning), over ys."""
    rl, lr = _profile(ctx, left, 'R', ys), _profile(ctx, right, 'L', ys)
    gaps = [ctx.W(left) - a + b for a, b in zip(rl, lr) if a is not None and b is not None]
    return min(gaps) if gaps else None


def _bracket_kerns(ctx, glyphs):
    """⟨ (⟦) before a glyph is kerned to leave the ink gap that ( ([) leaves before it with
    Mulish's kerning, ⟩ (⟧) after it as ) (]) does; pairs under 8 units are dropped."""
    ys = [y for y in range(-240, 760, 12)]
    out = {}
    for br, ref, before in (('uni27E8', 'parenleft', True), ('uni27E9', 'parenright', False),
                            ('uni27E6', 'bracketleft', True), ('uni27E7', 'bracketright', False)):
        if br not in ctx.font.getGlyphOrder(): continue
        for g in glyphs:
            if g in (br, ref): continue
            a, b = (br, g) if before else (g, br)
            ra, rb = (ref, g) if before else (g, ref)
            gb, gr = _gap(ctx, a, b, ys), _gap(ctx, ra, rb, ys)
            if gb is None or gr is None: continue
            k = round(gr + ctx.kern(ra, rb) - gb)
            if abs(k) >= 8: out[(a, b)] = k
    return out


# Direct existing-font script repertoire; complete donor outlines, never medial tracing.
SCRIPT_CODEPOINTS = (119964, 8492, 119966, 119967, 8496, 8497, 119970, 8459, 8464, 119973, 119974, 8466, 8499, 119977, 119978, 119979, 119980, 8475, 119982, 119983, 119984, 119985, 119986, 119987, 119988, 119989, 8495, 8458, 8500)

# Existing mapped glyphs are intentionally replaced, including mathletters' former ℒ.
GLYPH_OVERRIDE = {f'u{cp:04X}' if cp > 0xFFFF else f'uni{cp:04X}' for cp in SCRIPT_CODEPOINTS}

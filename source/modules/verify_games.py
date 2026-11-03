"""HarfBuzz and geometry check of the games module.

    verify_games.py FONT STYLE full|subset

1. Coverage & shaping: all 29 encoded code points (GM1 chess U+2654..265F, GM2
   draughts U+26C0..26C3, GM3 dice U+2680..2685, GM4 Go markers U+2686..2689,
   SC2 astronomy U+2609, U+263D, U+2641) map to uniXXXX and shape to [uniXXXX]
   alone, between letters, and in figurine algebraic notation, both plain and
   with the app's feature settings (ss01 ss02 ss16 onum pnum). In subset mode,
   code points outside Makefile's UNICODES may be omitted cleanly.
2. Solar subscript & contextual shaping: unencoded uni2609.subs.games exists
   with ink and positive advance, is reached from U+2609 under subs and sinf,
   and substitutes contextually after M, L, R (and M.sc, L.sc, R.sc) via calt
   while leaving standalone U+2609 and non-solar letters untouched. GPOS kern
   tightens M + uni2609.subs.games.
3. Geometry, semantics, and counter openness: zero outline_check.py problems on
   all 30 glyphs; baseline and cap-height alignment; uniform checker top-ring
   stroke thickness; 6-pip die vertical slices prove all 3 pips and frame walls
   remain distinct even in Black; Go marker horizontal slices verify Unicode
   15.1 dot-right and two-dot semantics; Moon has pointed horns and open counter;
   Earth keeps open interior counters across all weights; subscript Sun ring and
   dot match inferior optical density; all glyphs stay within OS/2 typo and win
   vertical metrics.
4. Upright-in-italics & 14-style topology lock: italic glyphs remain strictly
   upright (matching their roman partner's width and height to 0 units, shifted
   solely by optical horizontal centering) and every built style in the same
   directory has 100% identical contour endpoints and point flags across all 30
   glyphs.
"""
import os
import sys
import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import outline_check  # noqa: E402
from webfeatures import kept  # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH)
glyf = f["glyf"]
gs = f.getGlyphSet()
cmap = f.getBestCmap()
hmtx = f["hmtx"]
os2 = f["OS/2"]
gdef_cls = (
    f["GDEF"].table.GlyphClassDef.classDefs
    if "GDEF" in f and f["GDEF"].table.GlyphClassDef
    else {}
)
face = hb.Face(hb.Blob.from_file_path(PATH))
hbfont = hb.Font(face)

APP = {"ss01": 1, "ss02": 1, "ss16": 1, "onum": 1, "pnum": 1}
ITALIC = STYLE.endswith("Italic")
BASE_STYLE = "Regular" if STYLE == "Italic" else (STYLE[:-6] if ITALIC else STYLE)

CHESS = list(range(0x2654, 0x2660))
CHECKERS = list(range(0x26C0, 0x26C4))
DICE = list(range(0x2680, 0x2686))
GO = list(range(0x2686, 0x268A))
ASTRO = [0x2609, 0x263D, 0x2641]
ENCODED = CHESS + CHECKERS + DICE + GO + ASTRO
SUB_SUN = "uni2609.subs.games"
ALL_GLYPHS = [f"uni{cp:04X}" for cp in ENCODED] + [SUB_SUN]
MAY_MISS = set(ENCODED) if MODE == "subset" else set()

fails = 0
checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok:
        fails += 1
        print("[verify_games FAIL]", *msg)


def shape(text, feats=None):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(hbfont, b, feats or {})
    return [hbfont.get_glyph_name(i.codepoint) for i in b.glyph_infos]


def shape_adv(text, feats=None):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(hbfont, b, feats or {})
    return sum(p.x_advance for p in b.glyph_positions)


def path_of(g):
    p = pathops.Path()
    gs[g].draw(p.getPen(glyphSet=gs))
    return p


def spans(p, y=None, x=None):
    r = pathops.Path()
    pen = r.getPen()
    box = (
        (-5000, y - 0.25, 5000, y + 0.25)
        if y is not None
        else (x - 0.25, -5000, x + 0.25, 5000)
    )
    pen.moveTo((box[0], box[1]))
    pen.lineTo((box[2], box[1]))
    pen.lineTo((box[2], box[3]))
    pen.lineTo((box[0], box[3]))
    pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION)
    i, j = (0, 2) if y is not None else (1, 3)
    return sorted((c.bounds[i], c.bounds[j]) for c in q.contours)


# --- 1. Coverage & HarfBuzz shaping ------------------------------------------
present = {}
for cp in ENCODED:
    ch = chr(cp)
    exp = f"uni{cp:04X}"
    if cp not in cmap:
        check(cp in MAY_MISS, f"U+{cp:04X} {ch} missing from cmap in {MODE} mode")
        continue
    g = cmap[cp]
    present[cp] = g
    check(g == exp, f"U+{cp:04X} mapped to {g!r}, expected {exp!r}")
    check(path_of(g).bounds is not None and hmtx[g][0] > 0, f"{g}: empty outline or zero advance")
    check(gdef_cls.get(g) == 1, f"{g}: GDEF class {gdef_cls.get(g)!r}, expected 1")
    for feats in (None, APP):
        check(shape(ch, feats) == [g], f"{ch} shapes to {shape(ch, feats)}, expected [{g}] ({feats})")
        ctx_names = shape("a" + ch + "b", feats)
        check(len(ctx_names) == 3 and ctx_names[1] == g, f"a{ch}b -> {ctx_names} ({feats})")

# Figurine algebraic notation check when chess pieces are present
if all(cp in present for cp in CHESS):
    san = "2. \u2658f3 \u265Ec6 3. \u2657b5 \u265Bd7+"
    for feats in (None, APP):
        got = shape(san, feats)
        for cp in (0x2658, 0x265E, 0x2657, 0x265B):
            check(f"uni{cp:04X}" in got, f"SAN missing uni{cp:04X} in {got} ({feats})")

# Plain Latin sanity check (also runs when subset omits U+2600..26FF)
for txt in ("M", "L", "R", "10 MLR"):
    got = shape(txt, APP)
    check(".notdef" not in got, f"unexpected .notdef in {txt!r}: {got}")

if not present and MODE == "subset":
    print(f"verify_games ({STYLE}, subset): 0 games code points in UNICODES; {checks} base checks passed")
    sys.exit(1 if fails else 0)

# --- 2. Solar subscript & contextual calt / subs / sinf / kern ----------------
order = set(f.getGlyphOrder())
check(SUB_SUN in order, f"{SUB_SUN} missing from glyph order")
if SUB_SUN in order:
    check(SUB_SUN not in cmap.values(), f"{SUB_SUN} must remain unencoded")
    check(path_of(SUB_SUN).bounds is not None and hmtx[SUB_SUN][0] > 0, f"{SUB_SUN}: empty or zero advance")
    check(gdef_cls.get(SUB_SUN) == 1, f"{SUB_SUN}: GDEF class {gdef_cls.get(SUB_SUN)!r}, expected 1")

    for tag in ("subs", "sinf"):
        if kept(tag):
            check(shape("\u2609", {tag: 1}) == [SUB_SUN], f"{tag} on U+2609 -> {shape('\u2609', {tag: 1})}")
            check(
                shape("M\u2609", dict(APP, **{tag: 1})) == ["M", SUB_SUN],
                f"{tag}+APP on M\u2609 -> {shape('M\u2609', dict(APP, **{tag: 1}))}",
            )

    if kept("calt"):
        for base in ("M", "L", "R"):
            check(
                shape(base + "\u2609") == [base, SUB_SUN],
                f"calt {base}\u2609 -> {shape(base + '\u2609')}",
            )
            check(
                shape(base + "\u2609", APP) == [base, SUB_SUN],
                f"calt+APP {base}\u2609 -> {shape(base + '\u2609', APP)}",
            )
        if kept("c2sc") and "M.sc" in order:
            check(
                shape("M\u2609", {"c2sc": 1}) == ["M.sc", SUB_SUN],
                f"c2sc+calt M\u2609 -> {shape('M\u2609', {'c2sc': 1})}",
            )
        # Negative cases: standalone Sun, non-solar capital, reversed order, calt=0
        check(shape("\u2609") == ["uni2609"], f"standalone \u2609 changed: {shape('\u2609')}")
        check(shape("A\u2609") == ["A", "uni2609"], f"A\u2609 should not subscript: {shape('A\u2609')}")
        check(shape("\u2609M") == ["uni2609", "M"], f"\u2609M should not subscript: {shape('\u2609M')}")
        check(
            shape("M\u2609", {"calt": 0}) == ["M", "uni2609"],
            f"calt=0 M\u2609 -> {shape('M\u2609', {'calt': 0})}",
        )

    if kept("calt") and kept("kern"):
        raw_adv = hmtx["M"][0] + hmtx[SUB_SUN][0]
        kerned_adv = shape_adv("M\u2609")
        check(kerned_adv < raw_adv, f"expected negative kern on M\u2609: got {kerned_adv} vs raw {raw_adv}")

# --- 3. Geometry, outline_check, interior counters, and vertical metrics ------
typo_lo, typo_hi = os2.sTypoDescender, os2.sTypoAscender
win_lo, win_hi = -os2.usWinDescent, os2.usWinAscent

for gname in ALL_GLYPHS:
    if gname not in order:
        continue
    g = glyf[gname]
    g.recalcBounds(glyf)
    probs = outline_check.check(g, glyf)
    check(not probs, f"{gname}: outline_check problems: {probs}")
    check(
        g.yMin >= max(typo_lo, win_lo) and g.yMax <= min(typo_hi, win_hi),
        f"{gname}: vertical bounds {g.yMin}..{g.yMax} exceed metrics {max(typo_lo, win_lo)}..{min(typo_hi, win_hi)}",
    )
    check(g.xMin >= 15 and hmtx[gname][0] - g.xMax >= 15, f"{gname}: tight sidebearings ({g.xMin}, {hmtx[gname][0] - g.xMax})")

# Chess bounds & interior open counters / negative-space accents
for cp in CHESS:
    g = glyf[f"uni{cp:04X}"]
    check(-42 <= g.yMin <= 2, f"uni{cp:04X}: base yMin {g.yMin} off baseline")
    check(680 <= g.yMax <= 765, f"uni{cp:04X}: piece yMax {g.yMax}")
    check(g.numberOfContours >= 2, f"uni{cp:04X}: too few contours ({g.numberOfContours})")

# Checkers: Kings taller and more contours than Men, plus uniform front/back outer top-ring stroke
for man_cp, king_cp in ((0x26C0, 0x26C1), (0x26C2, 0x26C3)):
    gm, gk = glyf[f"uni{man_cp:04X}"], glyf[f"uni{king_cp:04X}"]
    check(450 <= gm.yMax <= 500, f"uni{man_cp:04X}: man yMax {gm.yMax}")
    check(700 <= gk.yMax <= 720, f"uni{king_cp:04X}: king yMax {gk.yMax}")
    check(gk.numberOfContours == gm.numberOfContours + 1, f"checker contours man={gm.numberOfContours} king={gk.numberOfContours}")
    check(abs((gm.xMax - gm.xMin) - 704) <= 2 and abs((gk.xMax - gk.xMin) - 704) <= 2, "checker width != 704")

for w_chk_cp, exp_spans in ((0x26C0, 5), (0x26C1, 6)):
    gn = f"uni{w_chk_cp:04X}"
    g = glyf[gn]
    vs = spans(path_of(gn), x=(g.xMin + g.xMax) / 2.0)
    check(len(vs) == exp_spans, f"{gn}: center vertical spans {vs} (expected {exp_spans})")
    if len(vs) == exp_spans:
        back_ring = vs[-1][1] - vs[-1][0]
        front_ring = vs[-4][1] - vs[-4][0]
        check(
            abs(front_ring - back_ring) <= 2.5,
            f"{gn}: uneven top-ring front ({front_ring:.1f}u) vs back ({back_ring:.1f}u) in {STYLE}",
        )

# Dice: square 704x706 frame, exact contour count 2+n, and 6-pip vertical openness
for idx, cp in enumerate(DICE, start=1):
    gn = f"uni{cp:04X}"
    g = glyf[gn]
    check(g.yMin == 0 and g.yMax == 706, f"{gn}: y bounds {g.yMin}..{g.yMax}")
    check(g.xMax - g.xMin == 704, f"{gn}: width {g.xMax - g.xMin}")
    check(g.numberOfContours == 2 + idx, f"{gn}: contours {g.numberOfContours}, expected {2 + idx}")

g6 = glyf["uni2685"]
cx6 = (g6.xMin + g6.xMax) / 2.0
col_spans = spans(path_of("uni2685"), x=cx6 - 130)
check(len(col_spans) == 5, f"uni2685 left pip column vertical spans {col_spans} (expected 5: 2 walls + 3 pips)")
if len(col_spans) == 5:
    min_gap = min(col_spans[i + 1][0] - col_spans[i][1] for i in range(4))
    check(min_gap >= 24, f"uni2685 vertical pip/wall gap too tight in {STYLE}: {min_gap:.1f}u")

# Go markers: harmonized 722x722 outer stone and Unicode 15.1 dot semantics
for cp in GO:
    gn = f"uni{cp:04X}"
    g = glyf[gn]
    check(g.xMax - g.xMin == 722 and g.yMax - g.yMin == 722, f"{gn}: stone size {g.xMax - g.xMin}x{g.yMax - g.yMin}")
    cx_go = (g.xMin + g.xMax) / 2.0
    hs = spans(path_of(gn), y=353)
    if cp == 0x2686:  # WHITE CIRCLE WITH DOT RIGHT: left ring, right-offset dot, right ring
        check(len(hs) == 3 and (hs[1][0] + hs[1][1]) / 2.0 > cx_go + 60, f"uni2686 spans {hs}")
    elif cp == 0x2687:  # WHITE CIRCLE WITH TWO DOTS: left ring, left dot, right dot, right ring
        check(len(hs) == 4, f"uni2687 spans {hs}")
    elif cp == 0x2688:  # BLACK CIRCLE WITH WHITE DOT RIGHT: 2 dark spans with hole on right
        check(len(hs) == 2 and (hs[0][1] + hs[1][0]) / 2.0 > cx_go + 60, f"uni2688 spans {hs}")
    elif cp == 0x2689:  # BLACK CIRCLE WITH TWO WHITE DOTS: 3 dark spans
        check(len(hs) == 3, f"uni2689 spans {hs}")

# Astronomical signs: Sun, subscript Sun, Moon, Earth
gsun = glyf["uni2609"]
check(gsun.xMax - gsun.xMin == 722 and gsun.yMax - gsun.yMin == 722, f"uni2609 size {gsun.xMax - gsun.xMin}x{gsun.yMax - gsun.yMin}")
hs_sun = spans(path_of("uni2609"), y=353)
check(len(hs_sun) == 3 and abs((hs_sun[1][0] + hs_sun[1][1]) / 2.0 - (gsun.xMin + gsun.xMax) / 2.0) <= 2, f"uni2609 spans {hs_sun}")

gsub_sun = glyf[SUB_SUN]
check(-8 <= gsub_sun.yMin <= 0 and 420 <= gsub_sun.yMax <= 435, f"{SUB_SUN} y bounds {gsub_sun.yMin}..{gsub_sun.yMax}")
hs_sub = spans(path_of(SUB_SUN), y=(gsub_sun.yMin + gsub_sun.yMax) / 2.0)
check(len(hs_sub) == 3, f"{SUB_SUN} spans {hs_sub}")
if len(hs_sub) == 3:
    sub_ring_w = hs_sub[0][1] - hs_sub[0][0]
    sub_dot_w = hs_sub[1][1] - hs_sub[1][0]
    sub_gap = hs_sub[1][0] - hs_sub[0][1]
    check(sub_ring_w >= 40 and sub_dot_w >= 100 and sub_gap >= 40, f"{SUB_SUN} ring={sub_ring_w:.1f} dot={sub_dot_w:.1f} gap={sub_gap:.1f}")
    if BASE_STYLE == "Black":
        check(sub_ring_w >= 92, f"{SUB_SUN} Black ring too light: {sub_ring_w:.1f}u")

gmoon = glyf["uni263D"]
check(gmoon.numberOfContours == 2 and 695 <= gmoon.yMax <= 735, f"uni263D contours={gmoon.numberOfContours} yMax={gmoon.yMax}")
check(len(spans(path_of("uni263D"), y=353)) == 2, f"uni263D mid-height spans {spans(path_of('uni263D'), y=353)}")
# Verify Moon horns come to clean points at xMin (no flat vertical cut wall):
m_coords, m_ends, _ = gmoon.getCoordinates(glyf)
m_outer = list(m_coords[: m_ends[0] + 1])
left_pts = [pt for pt in m_outer if pt[0] <= gmoon.xMin + 2]
check(
    len(left_pts) == 2 and abs(left_pts[0][1] - left_pts[1][1]) >= 600,
    f"uni263D horn tips not clean upper/lower points: {left_pts}",
)

gearth = glyf["uni2641"]
check(gearth.numberOfContours == 2 and 695 <= gearth.yMax <= 735, f"uni2641 contours={gearth.numberOfContours} yMax={gearth.yMax}")
check(len(spans(path_of("uni2641"), y=210)) == 2, f"uni2641 orb mid-spans {spans(path_of('uni2641'), y=210)}")

# --- 4. Upright-in-italics & cross-style 14-way topology compatibility -------
build_dir = os.path.dirname(os.path.abspath(PATH))
if MODE == "full":
    my_sigs = {gn: (tuple(glyf[gn].endPtsOfContours), bytes(glyf[gn].flags)) for gn in ALL_GLYPHS}
    siblings = sorted(
        fn for fn in os.listdir(build_dir)
        if fn.startswith("TorchletteSans-") and fn.endswith(".ttf")
    )
    for fn in siblings:
        sf = TTFont(os.path.join(build_dir, fn))
        sglyf = sf["glyf"]
        if not all(gn in sglyf.glyphs for gn in ALL_GLYPHS):
            continue
        for gn in ALL_GLYPHS:
            sig = (tuple(sglyf[gn].endPtsOfContours), bytes(sglyf[gn].flags))
            check(sig == my_sigs[gn], f"topology mismatch {gn} between {STYLE} and {fn}")

    if ITALIC:
        roman_style = "Regular" if STYLE == "Italic" else STYLE[:-6]
        roman_path = os.path.join(build_dir, f"TorchletteSans-{roman_style}.ttf")
        if os.path.exists(roman_path):
            rf = TTFont(roman_path)
            rglyf, rhmtx = rf["glyf"], rf["hmtx"]
            for gn in ALL_GLYPHS:
                ig, rg = glyf[gn], rglyf[gn]
                ig.recalcBounds(glyf)
                rg.recalcBounds(rglyf)
                check(
                    (ig.xMax - ig.xMin) == (rg.xMax - rg.xMin) and (ig.yMax - ig.yMin) == (rg.yMax - rg.yMin),
                    f"{gn}: italic bounds size {(ig.xMax - ig.xMin, ig.yMax - ig.yMin)} != roman {(rg.xMax - rg.xMin, rg.yMax - rg.yMin)}",
                )
                check(hmtx[gn][0] == rhmtx[gn][0], f"{gn}: italic advance {hmtx[gn][0]} != roman {rhmtx[gn][0]}")

print(f"verify_games ({STYLE}, {MODE}): {checks} checks passed, {fails} failed")
sys.exit(1 if fails else 0)

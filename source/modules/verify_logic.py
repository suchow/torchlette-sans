"""Verify the logic module (`LG1`-`LG3`, `CP4`, `CP5`) across full and web-subset fonts.

    python modules/verify_logic.py FONT STYLE [full|subset]

Checks:
1. Coverage, `GDEF` base class (1), non-empty bounds, positive advances, and
   HarfBuzz shaping (plain and app features) for all 19 encoded glyphs, plus
   presence of unencoded `uni25A1.math.logic` (subset mode allows `U+2621` `☡`
   to be absent when outside the Makefile's `UNICODES` list).
2. Modal necessity box (`LG2`): `ui.py`'s `□` (`U+25A1`, `uni25A1`) stays
   untouched in isolation (`□`), `a□b`, `(□)`, `[□]`, and UI checkboxes (`□ Item`);
   `ss09` ("Modal necessity box") substitutes `uni25A1 -> uni25A1.math.logic`
   and carries its `name`-table UI label; `calt` substitutes `uni25A1 ->
   uni25A1.math.logic` in unambiguous modal/logical formulas (`⊢ □P`, `⊨ □p`,
   `¬□P`, `◇□P`, `□◇P`, `□□P`, `□(P → Q)`, `(□P → □Q)`).
3. Geometry, math-axis alignment (`LIN_AXIS`), stroke/counter openness (including
   Heavy/Black weights), bare caution bend (`☡`), 3-contour
   APL circle-bar operators (`⌽`, `⍉`), and upright counter-shear in italic styles.
4. Vertical metrics line-box envelope (`hhea` / `OS/2`).
5. Cross-style variable-font (`gvar`) outline compatibility: every glyph added by
   `logic` has identical contour count, point count, and on-curve flag sequence
   across all built styles in the same directory.
"""
import os
import sys

from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
import pathops
import uharfbuzz as hb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept  # noqa: E402

FONT, STYLE = sys.argv[1], sys.argv[2]
MODE = sys.argv[3] if len(sys.argv) > 3 else ('subset' if os.environ.get('TS_WEB_SUBSET') == '1' else 'full')
ITALIC = 'Italic' in STYLE
APP = {'ss01': True, 'ss02': True, 'ss16': True, 'onum': True, 'pnum': True}

tt = TTFont(FONT)
cmap = tt.getBestCmap()
glyf = tt['glyf']
hmtx = tt['hmtx']
gs = tt.getGlyphSet()
order = set(tt.getGlyphOrder())
K = -math.tan(math.radians(tt['post'].italicAngle)) if 'math' in globals() else 0.0
import math  # noqa: E402
K = -math.tan(math.radians(tt['post'].italicAngle))

blob = hb.Blob.from_file_path(FONT)
hbf = hb.Font(hb.Face(blob))

fails = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def shape(text, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, features)
    return [hbf.get_glyph_name(i.codepoint) for i in buf.glyph_infos]


def path_of(g):
    p = pathops.Path()
    gs[g].draw(p.getPen())
    return p


def spans(p, y=None, x=None):
    r = pathops.Path()
    pen = r.getPen()
    box = (-5000, y - 0.25, 5000, y + 0.25) if y is not None else (x - 0.25, -5000, x + 0.25, 5000)
    pen.moveTo((box[0], box[1]))
    pen.lineTo((box[2], box[1]))
    pen.lineTo((box[2], box[3]))
    pen.lineTo((box[0], box[3]))
    pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION)
    i, j = (0, 2) if y is not None else (1, 3)
    return sorted((c.bounds[i], c.bounds[j]) for c in q.contours)


def near(a, b, tol):
    return abs(a - b) <= tol


CHARS = {
    # LG1 — Turnstiles
    0x22A2: '⊢', 0x22A3: '⊣', 0x22A7: '⊧', 0x22A8: '⊨', 0x22AC: '⊬', 0x22AD: '⊭',
    # LG2 — Modal operators
    0x25C7: '◇', 0x25FB: '◻',
    # LG3 — End of proof, dangerous bend, contradiction, editorial marks
    0x220E: '∎', 0x2621: '☡', 0x21AF: '↯', 0x204E: '⁎', 0x2023: '‣', 0x2311: '⌑',
    # CP4 — APL heritage
    0x2373: '⍳', 0x2374: '⍴', 0x2349: '⍉', 0x233D: '⌽',
    # CP5 — ISO 5807 flowchart trapezium
    0x23E2: '⏢',
}
MAY_MISS = {0x2621} if MODE == 'subset' else set()

# ---- 1. Coverage, GDEF, and default HarfBuzz shaping -----------------------
gdef_cls = tt['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in tt and tt['GDEF'].table.GlyphClassDef else {}
present = {}
for u, ch in sorted(CHARS.items()):
    if u not in cmap:
        check(u in MAY_MISS, f'U+{u:04X} {ch} unmapped in {MODE} mode')
        continue
    g = cmap[u]
    present[u] = g
    check(g == f'uni{u:04X}', f'U+{u:04X} mapped to {g}, expected uni{u:04X}')
    b = path_of(g).bounds
    check(b is not None and hmtx[g][0] > 0, f'{g}: empty bounds or non-positive advance')
    check(gdef_cls.get(g) == 1, f'{g}: GDEF class {gdef_cls.get(g)}, expected 1')
    for feats in (None, APP):
        check(shape(ch, feats) == [g], f'{ch} shapes to {shape(ch, feats)} under {feats}, expected [{g}]')
        seq = shape('a' + ch + 'b', feats)
        check(len(seq) == 3 and seq[1] == g, f'a{ch}b shapes to {seq} under {feats}')

if MODE == 'full' or ('uni25A1' in order and kept('calt')):
    check('uni25A1.math.logic' in order, 'uni25A1.math.logic missing from glyph order')
    if 'uni25A1.math.logic' in order:
        check(gdef_cls.get('uni25A1.math.logic') == 1, 'uni25A1.math.logic GDEF class != 1')

# ---- 2. Modal necessity box (`ss09` & `calt` + negative UI checks) ---------
if 'uni25A1' in order and 'uni25A1.math.logic' in order and 0x25A1 in cmap:
    # Negative guards: UI square stays cap-height uni25A1
    for neg, idx in (('□', 0), ('a□b', 1), ('□ Item', 0), ('(□)', 1), ('[□]', 1)):
        for feats in (None, APP):
            got = shape(neg, feats)
            check(got[idx] == 'uni25A1', f'negative {neg!r} under {feats} shaped to {got}, expected uni25A1 at {idx}')

    # Explicit ss09 toggle
    if kept('ss09'):
        for txt, idx in (('□', 0), ('□P', 0), ('a□b', 1)):
            got = shape(txt, {'ss09': True})
            check(got[idx] == 'uni25A1.math.logic', f'ss09 on {txt!r} -> {got}')
        gsub = tt['GSUB'].table
        ss09_recs = [r for r in gsub.FeatureList.FeatureRecord if r.FeatureTag == 'ss09']
        check(bool(ss09_recs), 'ss09 missing from GSUB FeatureList')
        if ss09_recs and ss09_recs[0].Feature.FeatureParams is not None:
            uid = ss09_recs[0].Feature.FeatureParams.UINameID
            label = tt['name'].getDebugName(uid)
            check(label == 'Modal necessity box', f'ss09 UI name {label!r}')
        else:
            check(False, 'ss09 missing FeatureParams UI label')

    # Contextual calt rules in logical/modal formulas
    if kept('calt'):
        modal_cases = [
            ('⊢ □P', ['uni25A1.math.logic']),
            ('⊨ □p', ['uni25A1.math.logic']),
            ('¬□P', ['uni25A1.math.logic']),
            ('◇□P', ['uni25A1.math.logic']),
            ('□◇P', ['uni25A1.math.logic']),
            ('□□P', ['uni25A1.math.logic', 'uni25A1.math.logic']),
            ('□(P)', ['uni25A1.math.logic']),
            ('(□P)', ['uni25A1.math.logic']),
        ]
        if 0x2192 in cmap:
            modal_cases.append(('□(P → Q) → (□P → □Q)', ['uni25A1.math.logic', 'uni25A1.math.logic', 'uni25A1.math.logic']))
            modal_cases.append(('□P → P', ['uni25A1.math.logic']))
        if 0x2194 in cmap:
            modal_cases.append(('and □P ↔ ¬◇¬P', ['uni25A1.math.logic']))
        for formula, want_boxes in modal_cases:
            for feats in (None, APP):
                got = shape(formula, feats)
                boxes = [g for g in got if g in ('uni25A1', 'uni25A1.math.logic')]
                check(boxes == want_boxes, f'calt modal {formula!r} under {feats}: got {got}')

# ---- 3. Geometry, math-axis alignment, counters, and italic uprightness ----
mb = path_of('minus').bounds
A = 0.5 * (mb[1] + mb[3])
BAR = mb[3] - mb[1]
CAP = path_of('H').bounds[3]
XH = path_of('x').bounds[3]
P_DESC = path_of('p').bounds[1]

# LG1: Turnstiles
for u in (0x22A2, 0x22A3, 0x22A7, 0x22A8, 0x22AC, 0x22AD):
    if u not in present:
        continue
    g = present[u]
    b = path_of(g).bounds
    check(hmtx[g][0] == 600, f'{g}: advance {hmtx[g][0]} != 600')
    check(near(0.5 * (b[1] + b[3]), A, 3.0), f'{g}: vertical center {0.5 * (b[1] + b[3]):.1f} vs axis {A:.1f}')

if 0x22A2 in present and 0x22A3 in present:
    check(glyf[present[0x22A2]].numberOfContours == 1, '⊢ contours != 1')
    check(glyf[present[0x22A3]].numberOfContours == 1, '⊣ contours != 1')

if 0x22A7 in present and 0x22A8 in present:
    b_mod = path_of(present[0x22A7]).bounds
    b_tru = path_of(present[0x22A8]).bounds
    check(glyf[present[0x22A7]].numberOfContours == 1, '⊧ contours != 1')
    check(glyf[present[0x22A8]].numberOfContours == 1, '⊨ contours != 1')
    if not ITALIC:
        check((b_mod[2] - b_mod[0]) < (b_tru[2] - b_tru[0]) - 60, f'⊧ width {b_mod[2]-b_mod[0]} not compact vs ⊨ {b_tru[2]-b_tru[0]}')
    check((b_mod[3] - b_mod[1]) > (b_tru[3] - b_tru[1]) + 40, '⊧ stem not taller than ⊨')

if 0x22AC in present:
    check(glyf[present[0x22AC]].numberOfContours == 1, '⊬ contours != 1')
if 0x22AD in present:
    check(glyf[present[0x22AD]].numberOfContours == 2, '⊭ contours != 2 (outer + enclosed counter)')
    sp_mid = spans(path_of(present[0x22AD]), y=A)
    check(len(sp_mid) == 2 and (sp_mid[1][0] - sp_mid[0][1]) >= 40, f'⊭ mid-axis spans {sp_mid}: counter pinched')

# LG2: Modal box & diamond (upright in italic!)
for gname in ([present[0x25FB]] if 0x25FB in present else []) + (['uni25A1.math.logic'] if 'uni25A1.math.logic' in order else []):
    b = path_of(gname).bounds
    check(glyf[gname].numberOfContours == 2, f'{gname}: contours != 2')
    check(hmtx[gname][0] == 600, f'{gname}: advance {hmtx[gname][0]} != 600')
    check(near(b[2] - b[0], 470, 3) and near(b[3] - b[1], 470, 3), f'{gname}: bounds {b} not 470x470 upright square')
    check(near(0.5 * (b[1] + b[3]), A, 2.5), f'{gname}: not centered on math axis')
    sp = spans(path_of(gname), y=A)
    check(len(sp) == 2 and (sp[1][0] - sp[0][1]) >= 240, f'{gname}: counter too narrow {sp}')

if 0x25C7 in present:
    g = present[0x25C7]
    b = path_of(g).bounds
    check(glyf[g].numberOfContours == 2, '◇: contours != 2')
    check(near(b[2] - b[0], b[3] - b[1], 3), f'◇: bounds {b} not symmetric upright diamond')
    check(near(0.5 * (b[1] + b[3]), A, 2.5), '◇: not centered on math axis')
    sp = spans(path_of(g), y=A)
    check(len(sp) == 2 and (sp[1][0] - sp[0][1]) >= 220, f'◇: counter too narrow {sp}')

# LG3: Tombstone, Dangerous Bend, Zigzag Arrow, Low Asterisk, Bullet, Kissen
if 0x220E in present:
    g = present[0x220E]
    b = path_of(g).bounds
    check(glyf[g].numberOfContours == 1 and len(glyf[g].coordinates) == 4, '∎: not 4-pt solid rectangle')
    check(near(b[1], 0, 1) and near(b[3], 670, 2) and near(b[2] - b[0], 436, 3), f'∎: bounds {b}')

if 0x2621 in present:
    g = present[0x2621]
    p_db = path_of(g)
    b = p_db.bounds
    # Selected bare bend, not a bend inside a separately enclosing road diamond.
    check(glyf[g].numberOfContours == 1, '☡: expected one bare, unframed contour')
    check(near(b[1], 0, 3) and near(b[3], CAP, 3), f'☡: vertical bounds {b} not baseline to cap height')
    mids = [spans(p_db, y=CAP * q) for q in (0.25, 0.5, 0.75)]
    check(all(len(v) == 1 for v in mids), f'☡: expected single unframed stroke at interior scans, got {mids}')
    if all(len(v) == 1 for v in mids):
        centers = [(v[0][0] + v[0][1]) / 2 for v in mids]
        check(centers[0] < centers[1] < centers[2], f'☡: diagonal does not travel from lower left toward upper right: {centers}')

if 0x21AF in present:
    g = present[0x21AF]
    b = path_of(g).bounds
    coords = list(glyf[g].coordinates)
    check(glyf[g].numberOfContours == 1 and len(coords) == 14,
          f'↯: contours {glyf[g].numberOfContours}, pts {len(coords)} != (1, 14)')
    check(b[1] <= -100 and b[3] >= 680, f'↯: vertical span {b[1]}..{b[3]}')
    if len(coords) == 14:
        # Downward-left edges: upper (1->2, 0->13) and lower (3->4, 12->11) must be parallel
        dl_angs = [
            math.degrees(math.atan2(coords[b_i][1] - coords[a_i][1], coords[b_i][0] - coords[a_i][0]))
            for a_i, b_i in ((1, 2), (0, 13), (3, 4), (12, 11))
        ]
        ang_spread = max(dl_angs) - min(dl_angs)
        check(ang_spread <= 0.5, f'↯: downward-left edges not parallel: {dl_angs} (spread {ang_spread:.2f}°)')

if 0x204E in present:
    g = present[0x204E]
    b = path_of(g).bounds
    check(glyf[g].numberOfContours == 1 and len(glyf[g].coordinates) == 15, '⁎: expected 15-pt 5-lobed asterisk')
    check(abs((b[1] + b[3]) / 2) <= XH / 4 and b[1] < 0 < b[3] and b[3] < 420,
          f'⁎: expected a baseline-straddling low asterisk, got {b}')
    if 0x2217 in cmap:
        mb_star = path_of(cmap[0x2217]).bounds
        check((mb_star[1] + mb_star[3] - b[1] - b[3]) / 2 >= XH / 3,
              f'⁎: insufficient vertical distinction from math asterisk: {b}, {mb_star}')
    check(hmtx[g][0] == hmtx['asterisk'][0], f'⁎: advance {hmtx[g][0]} != asterisk {hmtx["asterisk"][0]}')

if 0x2023 in present:
    g = present[0x2023]
    b = path_of(g).bounds
    check(glyf[g].numberOfContours == 1 and len(glyf[g].coordinates) == 3, '‣: expected 3-pt triangle')
    check(near(0.5 * (b[1] + b[3]), A, 2.5) and near(b[2] - b[0], 264, 3), f'‣: bounds {b}')

if 0x2311 in present:
    g = present[0x2311]
    p_k = path_of(g)
    b = p_k.bounds
    check(glyf[g].numberOfContours == 2 and len(glyf[g].coordinates) == 16, '⌑: expected 2 contours, 16 pts')
    check(near(0.5 * (b[1] + b[3]), A, 2.5) and near(b[2] - b[0], b[3] - b[1], 3), f'⌑: bounds {b}')
    sp = spans(p_k, y=A)
    check(len(sp) == 2 and (sp[1][1] - sp[0][0]) < (b[2] - b[0]) - 45, f'⌑: waist {sp} not concave relative to {b}')
    check(len(sp) == 2 and (sp[1][0] - sp[0][1]) >= 140, f'⌑: inner pillow counter too small {sp}')

# CP4: APL heritage (⍳, ⍴, ⍉, ⌽)
if 0x2373 in present:
    g = present[0x2373]
    b = path_of(g).bounds
    check(glyf[g].numberOfContours == 1, '⍳: contours != 1')
    check(near(b[3], XH, 6) and -14 <= b[1] <= -2, f'⍳: vertical bounds {b[1]}..{b[3]} vs XH {XH}')

if 0x2374 in present:
    g = present[0x2374]
    p_r = path_of(g)
    b = p_r.bounds
    check(glyf[g].numberOfContours == 2, '⍴: contours != 2')
    check(near(b[1], P_DESC, 4) and near(b[3], XH + 9, 6), f'⍴: vertical bounds {b[1]}..{b[3]} vs {P_DESC}..{XH+9}')
    sp = spans(p_r, y=0.5 * XH)
    check(len(sp) == 2 and (sp[1][0] - sp[0][1]) >= 180, f'⍴: bowl counter too narrow {sp}')

i_sp = spans(path_of('i'), y=250)
I_STEM = (i_sp[0][1] - i_sp[0][0]) if i_sp else BAR

for u in (0x233D, 0x2349):
    if u not in present:
        continue
    g = present[u]
    p_c = path_of(g)
    b = p_c.bounds
    check(glyf[g].numberOfContours == 3 and len(glyf[g].coordinates) == 28,
          f'{g}: expected 3 contours, 28 pts (outer + 2 D-counters), got ({glyf[g].numberOfContours}, {len(glyf[g].coordinates)})')
    check(near(0.5 * (b[1] + b[3]), A, 3.5), f'{g}: vertical center {0.5*(b[1]+b[3]):.1f} vs {A:.1f}')
    sp = spans(p_c, y=A)
    # Bold (~112u / ~103u) and Black (~69u perpendicular; ~59u horizontal across 30°-tilted ⍉)
    # carry full SV-scaled ring/bar weight while keeping both semicircular D-counters wide open.
    min_h_cntr = 62 if u == 0x233D else 54
    check(len(sp) == 3 and (sp[1][0] - sp[0][1]) >= min_h_cntr and (sp[2][0] - sp[1][1]) >= min_h_cntr,
          f'{g}: expected 3 horizontal spans (ring, bar, ring) with open counters >= {min_h_cntr}, got {sp}')
    if len(sp) == 3:
        ring_w = sp[0][1] - sp[0][0]
        min_ratio = 0.83 if I_STEM >= 110 else 0.78
        check(ring_w >= min_ratio * I_STEM,
              f'{g}: ring stroke {ring_w:.1f} too light relative to i stem {I_STEM:.1f}')

# CP5: ISO 5807 White Trapezium
if 0x23E2 in present:
    g = present[0x23E2]
    p_t = path_of(g)
    b = p_t.bounds
    check(glyf[g].numberOfContours == 2 and len(glyf[g].coordinates) == 8, '⏢: expected 2 contours, 8 pts')
    check(near(0.5 * (b[1] + b[3]), A, 2.5), f'⏢: not centered on axis {b}')
    sp_lo = spans(p_t, y=b[1] + 5)
    sp_hi = spans(p_t, y=b[3] - 5)
    check((sp_lo[-1][1] - sp_lo[0][0]) > (sp_hi[-1][1] - sp_hi[0][0]) + 220, '⏢: bottom not wider than top')
    sp_mid = spans(p_t, y=A)
    check(len(sp_mid) == 2 and (sp_mid[1][0] - sp_mid[0][1]) >= 380, f'⏢: counter {sp_mid}')
    # The selected right trapezium has an upright left side; one font unit is
    # the independently measured source encoding/reslant rounding budget.
    lefts = [min(x for x, y in glyf[g].coordinates if y == yy)
             for yy in (glyf[g].yMin, glyf[g].yMax)]
    check(abs(lefts[0] - lefts[1]) <= 1, f'⏢: left edge is not upright: {lefts}')

# ---- 4. Vertical metrics envelope ------------------------------------------
hh, os2 = tt['hhea'], tt['OS/2']
v_lo = max(hh.descent, -os2.usWinDescent, os2.sTypoDescender)
v_hi = min(hh.ascent, os2.usWinAscent, os2.sTypoAscender)
logic_glyphs = list(present.values()) + (['uni25A1.math.logic'] if 'uni25A1.math.logic' in order else [])
for g in logic_glyphs:
    b = path_of(g).bounds
    check(b is not None and v_lo <= b[1] and b[3] <= v_hi,
          f'{g}: ink {b} outside vertical line metrics {v_lo}..{v_hi}')

# ---- 5. Cross-style gvar point/contour compatibility -----------------------
if MODE == 'full':
    reg_path = os.path.join(os.path.dirname(os.path.abspath(FONT)), 'TorchletteSans-Regular.ttf')
    if os.path.exists(reg_path) and os.path.abspath(FONT) != reg_path:
        reg_tt = TTFont(reg_path)
        reg_glyf = reg_tt['glyf']
        for g in logic_glyphs:
            if g in reg_glyf:
                ga, gb = glyf[g], reg_glyf[g]
                check(ga.numberOfContours == gb.numberOfContours,
                      f'gvar {g}: {STYLE} contours {ga.numberOfContours} != Regular {gb.numberOfContours}')
                check(list(ga.endPtsOfContours) == list(gb.endPtsOfContours),
                      f'gvar {g}: {STYLE} endPts {ga.endPtsOfContours} != Regular {gb.endPtsOfContours}')
                check([int(f & 1) for f in ga.flags] == [int(f & 1) for f in gb.flags],
                      f'gvar {g}: {STYLE} on-curve flags differ from Regular')

print(f'logic {STYLE} {MODE}: {checks - len(fails)}/{checks} checks passed')
for f in fails[:40]:
    print('  FAIL:', f)
sys.exit(1 if fails else 0)

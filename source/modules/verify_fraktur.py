"""Checks of the fraktur module: Mathematical Fraktur 𝔄..ℨ and 𝔞..𝔷 (SC4).

    verify_fraktur.py FONT STYLE full|subset

1. Coverage and shaping: all 52 Mathematical Fraktur characters (the 5 BMP Letterlike
   Symbols capitals U+210C, U+2111, U+211C, U+2128, U+212D and the 47 SMP characters
   U+1D504..U+1D537) are mapped in `full` mode; in `subset` mode the 5 BMP capitals in
   U+2100-214F must be present while the 47 SMP characters may be absent until the
   Makefile's `UNICODES` includes them. Each present character has non-empty contours,
   positive advance and GDEF class 1, and shapes to its own glyph alone and between
   letters under default features, the app's features (`ss01 ss02 ss16 onum pnum`),
   and `smcp`/`c2sc` (which must leave Mathematical Fraktur untouched).
2. Cmap: `full` fonts have both `(3, 10)` and `(0, 4)` format 12 subtables agreeing with
   `(3, 1)` format 4 on all BMP code points and mapping all 52 Fraktur code points (plus
   `mathletters` SMP code points when present).
3. Proportions, metrics and open counters: all glyphs stay within `OS/2` typo/win and
   `hhea` vertical bounds; capitals match Torchlette's cap height, lowercase matches
   `XH`, ascenders and descenders, `𝔦`/`𝔧` carry separate diamond tittles, and split-stem
   / bowl counters (`ℌ`, `ℜ`, `𝔞`, `𝔥`, `𝔰`) remain open through `Black`.
4. Outline quality: every present Fraktur glyph passes `outline_check.check` (zero kinks,
   shorts or spurs) and `pathops` overlap checks.
5. Upright semantics and 14-style topology invariance: stems stand upright in `*Italic`
   styles; across sibling `TorchletteSans-*.ttf` files in the same build directory, all
   52 Fraktur glyphs keep identical contour counts, point counts and flags, upright/italic
   pairs share identical outlines, and stem weights progress monotonically from `Light`
   to `Black`.
"""
import os
import sys

import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import outline_check  # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH)
gs = f.getGlyphSet()
cmap = f.getBestCmap()
hmtx = f['hmtx']
glyf = f['glyf']
os2 = f['OS/2']
hhea = f['hhea']
gdef_cls = f['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in f else {}

face = hb.Face(hb.Blob.from_file_path(PATH))
hbfont = hb.Font(face)
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
SMCP = {'smcp': 1, 'c2sc': 1}

FRAK_UC = [
    (0x1D504, '𝔄', 'A'), (0x1D505, '𝔅', 'B'), (0x212D, 'ℭ', 'C'), (0x1D507, '𝔇', 'D'),
    (0x1D508, '𝔈', 'E'), (0x1D509, '𝔉', 'F'), (0x1D50A, '𝔊', 'G'), (0x210C, 'ℌ', 'H'),
    (0x2111, 'ℑ', 'I'), (0x1D50D, '𝔍', 'J'), (0x1D50E, '𝔎', 'K'), (0x1D50F, '𝔏', 'L'),
    (0x1D510, '𝔐', 'M'), (0x1D511, '𝔑', 'N'), (0x1D512, '𝔒', 'O'), (0x1D513, '𝔓', 'P'),
    (0x1D514, '𝔔', 'Q'), (0x211C, 'ℜ', 'R'), (0x1D516, '𝔖', 'S'), (0x1D517, '𝔗', 'T'),
    (0x1D518, '𝔘', 'U'), (0x1D519, '𝔙', 'V'), (0x1D51A, '𝔚', 'W'), (0x1D51B, '𝔛', 'X'),
    (0x1D51C, '𝔜', 'Y'), (0x2128, 'ℨ', 'Z'),
]
FRAK_LC = [(0x1D51E + i, chr(0x1D51E + i), chr(ord('a') + i)) for i in range(26)]
ALL_CHARS = [(u, ch, lat, True) for u, ch, lat in FRAK_UC] + [(u, ch, lat, False) for u, ch, lat in FRAK_LC]
BMP_CPS = {0x212D, 0x210C, 0x2111, 0x211C, 0x2128}
MAY_MISS = {u for u, *_ in ALL_CHARS if u > 0xFFFF} if MODE == 'subset' else set()

fails = 0
checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok:
        fails += 1
        print('[verify_fraktur FAIL]', *msg)


def shape(text, feats=None):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(hbfont, b, feats or {})
    return [hbfont.get_glyph_name(i.codepoint) for i in b.glyph_infos]


def path_of(gname, glyph_set=gs):
    p = pathops.Path()
    glyph_set[gname].draw(p.getPen(glyphSet=glyph_set))
    return p


def hspans(p, y):
    r = pathops.Path()
    pen = r.getPen()
    pen.moveTo((-5000, y - 0.25))
    pen.lineTo((5000, y - 0.25))
    pen.lineTo((5000, y + 0.25))
    pen.lineTo((-5000, y + 0.25))
    pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION)
    return sorted((c.bounds[0], c.bounds[2]) for c in q.contours)


# ---- 1. coverage and shaping --------------------------------------------------------------
present = {}
smp_skipped = 0
for u, ch, lat, is_uc in ALL_CHARS:
    expected_name = f'u{u:04X}' if u > 0xFFFF else f'uni{u:04X}'
    if u not in cmap:
        check(u in MAY_MISS, f'U+{u:04X} {ch} ({lat}) unmapped in {MODE} mode')
        if u in MAY_MISS:
            smp_skipped += 1
        continue
    g = cmap[u]
    present[u] = (g, ch, lat, is_uc)
    if MODE == 'full':
        check(g == expected_name, f'U+{u:04X} {ch} mapped to {g}, expected {expected_name}')
    gl = glyf[g]
    check(gl.numberOfContours > 0, f'{g} ({ch}): expected simple outline with contours > 0, got {gl.numberOfContours}')
    b = path_of(g).bounds
    check(b is not None and b[2] > b[0] and b[3] > b[1] and hmtx[g][0] > 0, f'{g} ({ch}): empty bounds or non-positive advance')
    check(gdef_cls.get(g) == 1, f'{g} ({ch}): GDEF class {gdef_cls.get(g)}, expected 1')
    for feats in (None, APP, SMCP):
        got = shape(ch, feats)
        check(got == [g], f'{ch} shapes to {got}, expected [{g}] under {feats}')
        ctx_got = shape('a' + ch + 'b', feats)
        check(len(ctx_got) == 3 and ctx_got[1] == g, f'a{ch}b shapes to {ctx_got} under {feats}')

if MODE == 'full':
    check(len(present) == 52, f'expected 52 Fraktur characters in full mode, got {len(present)}')
else:
    check(BMP_CPS.issubset(present.keys()), f'subset missing BMP Fraktur capitals: {BMP_CPS - set(present.keys())}')
print(f'coverage: {len(present)} of 52 Fraktur characters mapped and shaping'
      + (f' ({smp_skipped} SMP characters omitted by web subset UNICODES)' if smp_skipped else ''))

# ---- 2. format 12 cmap --------------------------------------------------------------------
tables = {(t.platformID, t.platEncID, t.format): t for t in f['cmap'].tables}
if MODE == 'full' or any(u > 0xFFFF for u in present):
    t4 = tables.get((3, 1, 4))
    for key in ((3, 10, 12), (0, 4, 12)):
        if MODE == 'subset' and key == (0, 4, 12) and key not in tables:
            continue
        t12 = tables.get(key)
        check(t12 is not None, f'missing {key} format 12 cmap subtable')
        if t12 is not None:
            if t4 is not None:
                bad = [u for u, g in t4.cmap.items() if t12.cmap.get(u) != g]
                check(not bad, f'{key} disagrees with (3,1,4) at {[hex(u) for u in bad[:8]]}')
            for u, (g, *_rest) in present.items():
                check(t12.cmap.get(u) == g, f'{key} lacks U+{u:04X} -> {g}')
            for ml_u in (0x1D53C, 0x1D7D9):
                if ml_u in cmap:
                    check(t12.cmap.get(ml_u) == cmap[ml_u], f'{key} lacks mathletters U+{ml_u:04X}')
    print('cmap: format 12 subtables consistent with format 4 and SMP repertoire')

# ---- 3. vertical bounds, proportions and open counters ------------------------------------
UC_DESC = {'F', 'H', 'J', 'P', 'Y', 'Z'}
LC_XH = {'a', 'c', 'e', 'm', 'n', 'o', 'r', 'u', 'v', 'w'}
LC_ASC = {'b', 'd', 'f', 'h', 'k', 'l'}
LC_DESC = {'f', 'g', 'h', 'j', 'p', 'q', 'y', 'z'}

for u, (g, ch, lat, is_uc) in present.items():
    b = path_of(g).bounds
    check(b[3] <= os2.sTypoAscender and b[1] >= os2.sTypoDescender,
          f'{g} ({ch}): bounds {b[1]:.0f}..{b[3]:.0f} exceed sTypo {os2.sTypoDescender}..{os2.sTypoAscender}')
    check(b[3] <= os2.usWinAscent and b[1] >= -os2.usWinDescent,
          f'{g} ({ch}): bounds {b[1]:.0f}..{b[3]:.0f} exceed usWin {-os2.usWinDescent}..{os2.usWinAscent}')
    check(b[3] <= hhea.ascent and b[1] >= hhea.descent,
          f'{g} ({ch}): bounds {b[1]:.0f}..{b[3]:.0f} exceed hhea {hhea.descent}..{hhea.ascent}')
    if is_uc:
        check(675 <= b[3] <= 765, f'{g} ({ch}): capital top {b[3]:.0f} outside 675..765')
        if lat in UC_DESC:
            check(-230 <= b[1] <= -150, f'{g} ({ch}): capital descender {b[1]:.0f} outside -230..-150')
        else:
            check(-45 <= b[1] <= 25, f'{g} ({ch}): capital bottom {b[1]:.0f} outside -45..25')
        if lat == 'B':
            check(glyf[g].numberOfContours == 3, f'{g} ({ch}): expected 3 contours (outer + 2 counters), got {glyf[g].numberOfContours}')
        elif lat == 'V':
            check(glyf[g].numberOfContours == 1, f'{g} ({ch}): expected 1 contour (open top), got {glyf[g].numberOfContours}')
    else:
        if lat in LC_XH:
            check(460 <= b[3] <= 525, f'{g} ({ch}): x-height top {b[3]:.0f} outside 460..525')
        elif lat in LC_ASC:
            check(705 <= b[3] <= 760, f'{g} ({ch}): ascender top {b[3]:.0f} outside 705..760')
        if lat in LC_DESC:
            check(-225 <= b[1] <= -150, f'{g} ({ch}): descender bottom {b[1]:.0f} outside -225..-150')
        else:
            check(-40 <= b[1] <= 25, f'{g} ({ch}): baseline bottom {b[1]:.0f} outside -40..25')
        if lat in ('i', 'j'):
            check(glyf[g].numberOfContours == 2, f'{g} ({ch}): expected 2 contours (body + tittle), got {glyf[g].numberOfContours}')

for u, y_scan, min_spans, min_gap in (
    (0x210C, 350, 2, 120),   # ℌ
    (0x211C, 350, 3, 55),    # ℜ
    (0x1D51E, 240, 2, 110),  # 𝔞
    (0x1D525, 240, 2, 110),  # 𝔥
    (0x1D530, 240, 2, 32),   # 𝔰
):
    if u not in present:
        continue
    g, ch, *_ = present[u]
    sp = hspans(path_of(g), y_scan)
    check(len(sp) >= min_spans, f'{g} ({ch}): expected >={min_spans} horizontal spans at y={y_scan}, got {sp}')
    if len(sp) >= 2:
        gaps = [sp[i + 1][0] - sp[i][1] for i in range(len(sp) - 1)]
        check(min(gaps) >= min_gap, f'{g} ({ch}): counter gap {min(gaps):.1f} < {min_gap} at y={y_scan}')
if 0x1D519 in present:
    gV, chV, *_ = present[0x1D519]
    spV = hspans(path_of(gV), 670)
    check(len(spV) >= 2, f'{gV} ({chV}): expected >=2 horizontal spans at y=670 (open top cleft), got {spV}')

print('metrics: vertical bounds, proportions and counter apertures verified')

# ---- 4. outline_check and pathops overlap gate --------------------------------------------
outline_fails = 0
for u, (g, ch, *_rest) in present.items():
    probs = outline_check.check(glyf[g], glyf)
    check(not probs, f'{g} ({ch}): outline_check problems {probs}')
    if probs:
        outline_fails += len(probs)
    p = path_of(g)
    q = pathops.Path()
    p.draw(q.getPen())
    q.simplify(fix_winding=True)
    area_diff = abs(abs(p.area) - abs(q.area))
    c_diff = len(list(p.contours)) - len(list(q.contours))
    check(area_diff <= 1.0 and c_diff == 0, f'{g} ({ch}): self-overlap area_diff={area_diff:.2f}, contour_diff={c_diff}')
print(f'outlines: {len(present)} glyphs clean ({outline_fails} problems, 0 overlaps)')

# ---- 5. upright italic check and cross-style topology / weight progression ----------------
if 0x210C in present:  # ℌ right vertical stem (y=160..360): upright |dx| ~ 1 vs 9-deg shear +32.7
    gH = present[0x210C][0]
    pH = path_of(gH)
    lo, hi = hspans(pH, 160), hspans(pH, 360)
    check(len(lo) >= 2 and len(hi) >= 2, f'{gH}: missing spans at y=160/360')
    if len(lo) >= 2 and len(hi) >= 2:
        dx_stem = ((hi[-1][0] + hi[-1][1]) * 0.5) - ((lo[-1][0] + lo[-1][1]) * 0.5)
        check(abs(dx_stem) <= 8.0, f'{gH} ({STYLE}): right stem leans dx={dx_stem:.1f} over dy=200 (expected upright)')

if 0x211C in present:  # ℜ main vertical spine (y=260..440): upright |dx| ~ 2.6 vs 9-deg shear +26.0
    gR = present[0x211C][0]
    pR = path_of(gR)
    lo, hi = hspans(pR, 260), hspans(pR, 440)
    check(len(lo) >= 2 and len(hi) >= 3, f'{gR}: missing spans at y=260/440')
    if len(lo) >= 2 and len(hi) >= 3:
        dx_stem = ((hi[1][0] + hi[1][1]) * 0.5) - ((lo[0][0] + lo[0][1]) * 0.5)
        check(abs(dx_stem) <= 8.0, f'{gR} ({STYLE}): main spine leans dx={dx_stem:.1f} over dy=180 (expected upright)')

if MODE == 'full':
    build_dir = os.path.dirname(os.path.abspath(PATH))
    weight_order = ['Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']
    all_styles = weight_order + [w + 'Italic' if w != 'Regular' else 'Italic' for w in weight_order]
    # Compare topology against Regular (or first available sibling) and check upright==italic parity
    my_base = (STYLE[:-6] if STYLE.endswith('Italic') else STYLE) or 'Regular'
    partner_style = (my_base + 'Italic' if my_base != 'Regular' else 'Italic') if not STYLE.endswith('Italic') else my_base
    partner_path = os.path.join(build_dir, f'TorchletteSans-{partner_style}.ttf')
    if os.path.exists(partner_path):
        pf = TTFont(partner_path)
        pglyf, phmtx = pf['glyf'], pf['hmtx']
        diff_partner = []
        for u, (g, *_rest) in present.items():
            if g not in pglyf.glyphs:
                diff_partner.append(g)
                continue
            g1, g2 = glyf[g], pglyf[g]
            if (list(g1.endPtsOfContours) != list(g2.endPtsOfContours)
                    or bytes(g1.flags) != bytes(g2.flags)
                    or list(g1.coordinates) != list(g2.coordinates)
                    or hmtx[g] != phmtx[g]):
                diff_partner.append(g)
        check(not diff_partner, f'{STYLE} vs {partner_style}: Fraktur upright/italic mismatch on {diff_partner[:8]}')

    ref_path = os.path.join(build_dir, 'TorchletteSans-Regular.ttf')
    if os.path.exists(ref_path) and os.path.abspath(ref_path) != os.path.abspath(PATH):
        rf = TTFont(ref_path)
        rglyf = rf['glyf']
        topo_bad = []
        for u, (g, *_rest) in present.items():
            if g in rglyf.glyphs:
                if list(glyf[g].endPtsOfContours) != list(rglyf[g].endPtsOfContours) or bytes(glyf[g].flags) != bytes(rglyf[g].flags):
                    topo_bad.append(g)
        check(not topo_bad, f'{STYLE} vs Regular: contour/point topology differs on {topo_bad[:8]}')

    # If all 7 upright weights exist in build_dir, check monotonic stem progression on 𝔥 (u1D525) and ℜ (uni211C)
    if STYLE == 'Black' and all(os.path.exists(os.path.join(build_dir, f'TorchletteSans-{w}.ttf')) for w in weight_order):
        stems_h = []
        stems_R = []
        for w in weight_order:
            wf = TTFont(os.path.join(build_dir, f'TorchletteSans-{w}.ttf'))
            wgs = wf.getGlyphSet()
            sh = hspans(path_of('u1D525', wgs), 240)[0]
            sR = hspans(path_of('uni211C', wgs), 350)[1]
            stems_h.append(round(sh[1] - sh[0], 1))
            stems_R.append(round(sR[1] - sR[0], 1))
        check(all(stems_h[i] < stems_h[i + 1] for i in range(len(stems_h) - 1)), f'𝔥 stem progression not strictly increasing: {stems_h}')
        check(all(stems_R[i] < stems_R[i + 1] for i in range(len(stems_R) - 1)), f'ℜ stem progression not strictly increasing: {stems_R}')
        print(f'progression: 𝔥 stems {stems_h}, ℜ stems {stems_R}')

if fails:
    sys.exit(1)
print(f'[verify_fraktur OK] {STYLE} {MODE}: {checks} checks passed.')

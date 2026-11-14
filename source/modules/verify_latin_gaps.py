"""HarfBuzz and outline check of the latin_gaps module.

    verify_latin_gaps.py FONT.ttf STYLE full|subset

Verifies across every style (upright and italic, Light through Black):
1. Dutch `Ĳ`/`ĳ` (`U+0132`/`U+0133`) presence, non-nested components, `smcp`/`c2sc` -> `IJ.sc` (height 550);
   every vulgar-fraction numerator (`<digit>.vnumr`) a component of some fraction.
2. Complete 48-character Pinyin repertoire (24 uppercase + 24 lowercase), dotless `ǐ` (`U+01D0`),
   stacked `ü` + tone (`U+01D5..U+01DC`) clear vertical separation and round dots within `usWinAscent`,
   and 550-unit `smcp`/`c2sc` small caps for all 48 Pinyin letters.
3. All Latin `case_mapping` pairs (`Ĳ/ĳ`, `Ǔ/ǔ`, `Ǥ/ǥ`, `Ǩ/ǩ`, `Ȟ/ȟ`, `Ȩ/ȩ`, `Ƒ/ƒ`), zero non-Greek
   `case_mapping` gaps in `cmap`, and 100% Latin `Ll`/`Lu` coverage in `smcp`/`c2sc`.
4. All 20 Unicode fraction characters (`U+00BC..00BE`, `U+2150..215F`, `U+2189`) on `full` (and on
   `subset` when `U+2150-218F` is included in `UNICODES`), checking AGL names and glyph structure.
5. OpenType `afrc` stacked nut fractions (when `kept('afrc')`), verifying vertical stacking
   (numerator above bar above denominator with positive air gaps), horizontal centering (along the
   9-degree slant axis in italic styles), multi-digit support (`1/2`, `7/16`, `22/7`, `12/34`, `355/113`),
   precomposed vulgar fraction mapping, `⅟` expansion (`⅟8`, `⅟₁₆`), compatibility with `onum`/`pnum`/`smcp`,
   and negative guards (`1/2/3`, `2026/11/02`, `12345/6`, and `afrc` off by default).
6. Kerning inheritance on new letters and small caps without touching tabular figures.
7. Variable-font contour/point/flag compatibility across all 7 upright weights and all 7 italic weights.
"""
import os
import sys
import unicodedata

import uharfbuzz as hb
from fontTools.agl import UV2AGL
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import outline_check  # noqa: E402
from webfeatures import kept  # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
ITALIC = 'Italic' in STYLE
ITALIC_K = 0.1587 if ITALIC else 0.0
ITALIC_YC = 252

tt = TTFont(PATH)
GO = tt.getGlyphOrder()
HAVE = set(GO)
GS = tt.getGlyphSet()
GLYF = tt['glyf']
HMTX = tt['hmtx'].metrics
CMAP = tt.getBestCmap()
HB = hb.Font(hb.Face(hb.Blob.from_file_path(PATH)))

fails, checks = [], 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def shape(text, feats=None, lang=None):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    if lang:
        b.language = hb.Language.from_string(lang)
    hb.shape(HB, b, feats or {})
    out, x = [], 0
    for info, pos in zip(b.glyph_infos, b.glyph_positions):
        g = GO[info.codepoint]
        out.append(dict(g=g, x=x + pos.x_offset, y=pos.y_offset, adv=pos.x_advance, dx=pos.x_offset))
        x += pos.x_advance
    return out


_bb = {}


def bounds(g):
    if g not in _bb:
        p = BoundsPen(GS)
        GS[g].draw(p)
        _bb[g] = p.bounds
    return _bb[g]


def ink(r):
    b = bounds(r['g'])
    return None if b is None else (b[0] + r['x'], b[1] + r['y'], b[2] + r['x'], b[3] + r['y'])


def unslanted_center_x(box):
    ymid = (box[1] + box[3]) / 2.0
    return (box[0] + box[2]) / 2.0 - ITALIC_K * (ymid - ITALIC_YC)


# ---- 1. No nested components & valid glyph names / GDEF -----------------------
for g in GO:
    gl = GLYF[g]
    if gl.isComposite():
        nested = [c.glyphName for c in gl.components if GLYF[c.glyphName].isComposite()]
        check(not nested, f'{g}: nested components {nested}')
# the vulgar fractions' numerators (`<digit>.vnumr`) exist only as their components: none is
# built that no fraction uses (6, 8 and 9 were, reached by nothing)
_components = {c.glyphName for g in GO if GLYF[g].isComposite() for c in GLYF[g].components}
_vnumr = [g for g in GO if '.vnumr.' in g]
check(all(g in _components for g in _vnumr), f'vulgar-fraction numerators no fraction uses: {[g for g in _vnumr if g not in _components]}')

# ---- 2. Dutch IJ / ij (U+0132 / U+0133) ---------------------------------------
check(CMAP.get(0x0132) == 'IJ', f'U+0132 mapped to {CMAP.get(0x0132)}')
check(CMAP.get(0x0133) == 'ij', f'U+0133 mapped to {CMAP.get(0x0133)}')
if 'ij' in HAVE:
    check(HMTX['ij'][0] == HMTX['i'][0] + HMTX['j'][0] or (
        'i_j.loclNLD' in HAVE and HMTX['ij'][0] == HMTX['i_j.loclNLD'][0]
    ), f'ij advance {HMTX["ij"][0]}')
    s_smcp = shape('\u0133', {'smcp': 1})
    s_c2sc = shape('\u0132', {'c2sc': 1})
    check([r['g'] for r in s_smcp] == ['IJ.sc'], f'ij smcp -> {[r["g"] for r in s_smcp]}')
    check([r['g'] for r in s_c2sc] == ['IJ.sc'], f'IJ c2sc -> {[r["g"] for r in s_c2sc]}')
    check(bounds('IJ.sc')[3] == 550, f'IJ.sc yMax {bounds("IJ.sc")[3]} != 550')

# ---- 3. Complete 48-codepoint Pinyin repertoire + small caps ------------------
PINYIN_PAIRS = [
    (0x0100, 0x0101), (0x00C1, 0x00E1), (0x01CD, 0x01CE), (0x00C0, 0x00E0),  # a
    (0x014C, 0x014D), (0x00D3, 0x00F3), (0x01D1, 0x01D2), (0x00D2, 0x00F2),  # o
    (0x0112, 0x0113), (0x00C9, 0x00E9), (0x011A, 0x011B), (0x00C8, 0x00E8),  # e
    (0x012A, 0x012B), (0x00CD, 0x00ED), (0x01CF, 0x01D0), (0x00CC, 0x00EC),  # i
    (0x016A, 0x016B), (0x00DA, 0x00FA), (0x01D3, 0x01D4), (0x00D9, 0x00F9),  # u
    (0x01D5, 0x01D6), (0x01D7, 0x01D8), (0x01D9, 0x01DA), (0x01DB, 0x01DC),  # ü
]
check(len(PINYIN_PAIRS) == 24, '24 Pinyin tone pairs expected')
for up_cp, lo_cp in PINYIN_PAIRS:
    check(up_cp in CMAP and lo_cp in CMAP, f'Pinyin pair U+{up_cp:04X}/U+{lo_cp:04X} missing from cmap')
    if up_cp in CMAP and lo_cp in CMAP:
        r_lo = shape(chr(lo_cp), {'smcp': 1})
        r_up = shape(chr(up_cp), {'c2sc': 1})
        check(len(r_lo) == 1 and r_lo[0]['g'] != CMAP[lo_cp], f'U+{lo_cp:04X} smcp unchanged: {r_lo}')
        check(len(r_up) == 1 and r_up[0]['g'] != CMAP[up_cp], f'U+{up_cp:04X} c2sc unchanged: {r_up}')
        check(r_lo[0]['g'] == r_up[0]['g'], f'Pinyin SC mismatch U+{up_cp:04X}/{lo_cp:04X}: {r_up[0]["g"]} vs {r_lo[0]["g"]}')

# ǐ (U+01D0) MUST use dotlessi (never i with dot -> 2 components or 2 contours total, never 3!)
if 'uni01D0' in HAVE:
    g_01d0 = GLYF['uni01D0']
    if g_01d0.isComposite():
        comp_names = [c.glyphName for c in g_01d0.components]
        check(comp_names[0] == 'dotlessi' and 'i' not in comp_names, f'uni01D0 components {comp_names} must use dotlessi')
    else:
        check(g_01d0.numberOfContours == 2, f'uni01D0 contour count {g_01d0.numberOfContours} (expected 2: stem + caron)')

# Double-diacritic ü + tone: check 4 separate contours (base + 2 round dots + 1 tone) & clear vertical gaps
win_asc = tt['OS/2'].usWinAscent
for cp in range(0x01D5, 0x01DD):
    gn = CMAP.get(cp)
    check(gn == f'uni{cp:04X}', f'U+{cp:04X} glyph name {gn}')
    if gn and gn in HAVE:
        g = GLYF[gn]
        if g.isComposite():
            check(all(not GLYF[c.glyphName].isComposite() for c in g.components), f'{gn}: nested composite')
        pts, ends, _flg = g.getCoordinates(GLYF)
        check(len(ends) == 4, f'{gn}: expected 4 non-overlapping contours, got {len(ends)}')
        b = bounds(gn)
        check(b[3] <= win_asc, f'{gn}: yMax {b[3]} exceeds usWinAscent {win_asc}')
        # Extract each contour's vertical span and check base < dots < tone with positive air gaps
        c_ys = []
        s = 0
        for e in ends:
            ys = [pts[k][1] for k in range(s, e + 1)]
            c_ys.append((min(ys), max(ys)))
            s = e + 1
        c_ys.sort()
        # c_ys[0] = base U/u, c_ys[1], c_ys[2] = two dieresis dots, c_ys[3] = tone mark
        if len(c_ys) == 4:
            base_top = c_ys[0][1]
            dots_bot = min(c_ys[1][0], c_ys[2][0])
            dots_top = max(c_ys[1][1], c_ys[2][1])
            tone_bot = c_ys[3][0]
            check(dots_bot - base_top >= 25, f'{gn}: dots too close to base ({dots_bot} vs {base_top})')
            check(tone_bot - dots_top >= 25, f'{gn}: tone mark too close to dots ({tone_bot} vs {dots_top})')

# ---- 4. Latin case_mapping completeness + 100% Latin smcp/c2sc ----------------
REQUIRED_PAIRS = [
    (0x0132, 0x0133, 'IJ', 'ij'),
    (0x0191, 0x0192, 'uni0191', 'florin'),
    (0x01D3, 0x01D4, 'uni01D3', 'uni01D4'),
    (0x01E4, 0x01E5, 'uni01E4', 'uni01E5'),
    (0x01E8, 0x01E9, 'uni01E8', 'uni01E9'),
    (0x021E, 0x021F, 'uni021E', 'uni021F'),
    (0x0228, 0x0229, 'uni0228', 'uni0229'),
]
for up_cp, lo_cp, up_gn, lo_gn in REQUIRED_PAIRS:
    check(CMAP.get(up_cp) == up_gn, f'U+{up_cp:04X} -> {CMAP.get(up_cp)}, want {up_gn}')
    check(CMAP.get(lo_cp) == lo_gn, f'U+{lo_cp:04X} -> {CMAP.get(lo_cp)}, want {lo_gn}')
    r_lo = shape(chr(lo_cp), {'smcp': 1})
    r_up = shape(chr(up_cp), {'c2sc': 1})
    check(len(r_lo) == 1 and r_lo[0]['g'] == r_up[0]['g'] and r_lo[0]['g'] not in (up_gn, lo_gn),
          f'SC pair U+{up_cp:04X}/U+{lo_cp:04X}: {r_up} vs {r_lo}')

# Check 550-unit small-cap height on florin.sc.latin_gaps and base small caps
if 'florin.sc.latin_gaps' in HAVE:
    fb_sc = bounds('florin.sc.latin_gaps')
    check(fb_sc[3] == 550 and fb_sc[1] < -100, f'florin.sc.latin_gaps bounds {fb_sc} (expected yMax=550, descender<-100)')

# Mirror FontBakery's exact case_mapping check on every non-Greek character in cmap
FB_EXCEPTIONS = {0x00B5, 0x03C0, 0x2126, 0x03BC, 0x03A9, 0x0394}
missing_case = []
for cp in sorted(CMAP):
    if cp in FB_EXCEPTIONS or 0x0370 <= cp <= 0x03FF:
        continue
    ch = chr(cp)
    if unicodedata.category(ch) not in ('Lu', 'Ll'):
        continue
    swapped = ch.swapcase()
    if len(swapped) == 1 and ord(swapped) != cp and ord(swapped) not in CMAP:
        missing_case.append(f'U+{cp:04X}->{ord(swapped):04X}')
check(not missing_case, f'non-Greek case_mapping gaps in cmap: {missing_case}')

# Every Latin Ll in cmap maps under smcp, and every Latin Lu in cmap maps under c2sc
unmapped_latin_ll, unmapped_latin_lu = [], []
for cp, gn in sorted(CMAP.items()):
    ch = chr(cp)
    name = unicodedata.name(ch, '')
    if 'LATIN' not in name:
        continue
    cat = unicodedata.category(ch)
    if cat == 'Ll':
        s = shape(ch, {'smcp': 1})
        if len(s) == 1 and s[0]['g'] == gn:
            unmapped_latin_ll.append(f'U+{cp:04X}({gn})')
    elif cat == 'Lu':
        s = shape(ch, {'c2sc': 1})
        if len(s) == 1 and s[0]['g'] == gn:
            unmapped_latin_lu.append(f'U+{cp:04X}({gn})')
check(not unmapped_latin_ll, f'unmapped Latin Ll in smcp: {unmapped_latin_ll}')
check(not unmapped_latin_lu, f'unmapped Latin Lu in c2sc: {unmapped_latin_lu}')

# ---- 5. All 20 Unicode fraction characters ------------------------------------
ALL_VULGAR = [0x00BC, 0x00BD, 0x00BE] + list(range(0x2150, 0x2160)) + [0x2189]
if MODE == 'full' or (0x2153 in CMAP):
    for cp in ALL_VULGAR:
        want_gn = UV2AGL.get(cp, f'uni{cp:04X}')
        got_gn = CMAP.get(cp)
        check(got_gn == want_gn, f'vulgar fraction U+{cp:04X}: got {got_gn}, want {want_gn}')
        if got_gn in HAVE:
            b = bounds(got_gn)
            check(b is not None and -20 <= b[1] <= 10 and 695 <= b[3] <= 725, f'{got_gn} bounds {b}')
            check(450 <= HMTX[got_gn][0] <= 1350, f'{got_gn} advance {HMTX[got_gn][0]}')
else:
    for cp in (0x00BC, 0x00BD, 0x00BE):
        check(CMAP.get(cp) == UV2AGL[cp], f'subset U+{cp:04X} missing')

# ---- 6. OpenType `afrc` (Alternative / Stacked Nut Fractions) -----------------
if kept('afrc'):
    AFRC_CASES = [
        '1/2', '1/3', '2/3', '3/4', '5/8', '7/8',
        '7/16', '1/10', '22/7', '12/34', '1/100', '355/113', '1024/768',
        '1\u20442', '7\u204416',
    ]
    for txt in AFRC_CASES:
        sep = '/' if '/' in txt else '\u2044'
        lhs, rhs = txt.split(sep)
        m, n = len(lhs), len(rhs)
        off = shape(txt, {})
        on = shape(txt, {'afrc': 1})
        check([r['g'] for r in off] != [r['g'] for r in on], f'afrc did not change {txt!r}')
        check(len(on) == m + 1 + n, f'afrc {txt!r}: glyph count {len(on)}, want {m + 1 + n}')
        if len(on) == m + 1 + n:
            num_boxes = [ink(r) for r in on[:m]]
            bar_box = ink(on[m])
            den_boxes = [ink(r) for r in on[m + 1:]]
            num_union = (min(b[0] for b in num_boxes), min(b[1] for b in num_boxes),
                         max(b[2] for b in num_boxes), max(b[3] for b in num_boxes))
            den_union = (min(b[0] for b in den_boxes), min(b[1] for b in den_boxes),
                         max(b[2] for b in den_boxes), max(b[3] for b in den_boxes))
            # Vertical stacking: numerator > bar > denominator with clear air gaps
            check(num_union[1] >= bar_box[3] + 25, f'afrc {txt!r}: num bottom {num_union[1]} vs bar top {bar_box[3]}')
            check(bar_box[1] >= den_union[3] + 25, f'afrc {txt!r}: bar bottom {bar_box[1]} vs den top {den_union[3]}')
            # Horizontal centering (along 9-degree slant axis in italic, vertical in upright)
            cx_num = unslanted_center_x(num_union)
            cx_bar = unslanted_center_x(bar_box)
            cx_den = unslanted_center_x(den_union)
            tol_n = 4 if m == 1 else 22
            tol_d = 4 if n == 1 else 22
            check(abs(cx_num - cx_bar) <= tol_n, f'afrc {txt!r}: num center {cx_num:.1f} vs bar center {cx_bar:.1f}')
            check(abs(cx_den - cx_bar) <= tol_d, f'afrc {txt!r}: den center {cx_den:.1f} vs bar center {cx_bar:.1f}')
            # Cell-block centering for multi-digit numerator and denominator
            cell_num_cx = (on[0]['x'] + on[m - 1]['x'] + HMTX[on[m - 1]['g']][0]) / 2.0
            cell_den_cx = (on[m + 1]['x'] + on[-1]['x'] + HMTX[on[-1]['g']][0]) / 2.0
            bar_cell_cx = HMTX[on[m]['g']][0] / 2.0
            check(abs(cell_num_cx - bar_cell_cx) <= 2, f'afrc {txt!r}: num cell {cell_num_cx} vs {bar_cell_cx}')
            check(abs(cell_den_cx - bar_cell_cx) <= 2, f'afrc {txt!r}: den cell {cell_den_cx} vs {bar_cell_cx}')
            # Bar spans at least as wide as numerator and denominator ink
            bar_len = bar_box[2] - bar_box[0]
            check(bar_len >= (num_union[2] - num_union[0]) - 2 and bar_len >= (den_union[2] - den_union[0]) - 2,
                  f'afrc {txt!r}: bar length {bar_len} narrower than digits')
            # Total advance equals nut bar's nominal advance
            tot_adv = sum(r['adv'] for r in on)
            check(tot_adv == HMTX[on[m]['g']][0], f'afrc {txt!r}: total advance {tot_adv} != bar width {HMTX[on[m]["g"]][0]}')

    # Works identically when combined with app figure features (onum, pnum, smcp, ss08)
    for extra in ({'onum': 1, 'pnum': 1}, {'pnum': 1}, {'tnum': 1}, {'smcp': 1}, {'ss08': 1}):
        fdict = dict(extra, afrc=1)
        check([r['g'] for r in shape('7/16', fdict)] == [r['g'] for r in shape('7/16', {'afrc': 1})],
              f'afrc + {extra} failed on 7/16')

    # Precomposed vulgar fractions under afrc
    vulg_to_test = [0x00BC, 0x00BD, 0x00BE] + ([c for c in range(0x2150, 0x215F)] + [0x2189] if 0x2153 in CMAP else [])
    for cp in vulg_to_test:
        r = shape(chr(cp), {'afrc': 1})
        check(len(r) == 1 and r[0]['g'].endswith('.afrc.latin_gaps'), f'U+{cp:04X} afrc -> {r}')
    if 0x215F in CMAP:
        for s_in in ('\u215F8', '\u215F\u2081\u2086'):
            r = shape(s_in, {'afrc': 1})
            check(any('.afrc.latin_gaps' in x['g'] for x in r), f'{s_in!r} afrc did not form nut fraction: {r}')

    # Negative guards: chained slashes / dates / >=5-digit numbers stay unstacked, and afrc is off by default
    for non_frac in ('1/2/3', '2026/11/02', '12345/6', '1/12345'):
        r = shape(non_frac, {'afrc': 1})
        check(not any('.latin_gaps' in x['g'] for x in r), f'afrc stacked non-fraction {non_frac!r}: {[x["g"] for x in r]}')
    check(not any('.afrc.latin_gaps' in x['g'] for x in shape('1/2 3/4 7/16 \u00BD', {})), 'afrc active by default')

# ---- 7. Kerning inheritance & tabular non-interference ------------------------
for txt, ref_txt, must_neg in (
    ('T\u01D2', 'To', True),
    ('V\u01DA', 'Vu', True),
    ('T\u01E4', 'TG', True),
    ('\u0191.', 'F.', True),
    ('\u0133\u2019', 'j\u2019', False),
    ('/\u0133', '/i', False),
):
    r_new = shape(txt, {})
    r_ref = shape(ref_txt, {})
    k_new = r_new[0]['adv'] - HMTX[r_new[0]['g']][0]
    k_ref = r_ref[0]['adv'] - HMTX[r_ref[0]['g']][0]
    check(k_new == k_ref and (not must_neg or k_new < 0),
          f'kerning {txt!r}: got {k_new}, ref {ref_txt!r} {k_ref}')

# Tabular figures stay unkerned next to new glyphs
for t_txt in ('1\u01331', '7\u01E47', '4\u01DA4'):
    r_t = shape(t_txt, {'tnum': 1})
    check(r_t[0]['adv'] == HMTX[r_t[0]['g']][0] and r_t[2]['adv'] == HMTX[r_t[2]['g']][0],
          f'tabular figure kerned in {t_txt!r}: {r_t}')

# ---- 8. Cross-weight contour / point-count invariance (variable-font ready) ----
if MODE == 'full':
    bdir = os.path.dirname(os.path.abspath(PATH))
    sib_styles = (
        ['LightItalic', 'Italic', 'MediumItalic', 'SemiBoldItalic', 'BoldItalic', 'ExtraBoldItalic', 'BlackItalic']
        if ITALIC else
        ['Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']
    )
    sib_paths = [os.path.join(bdir, f'TorchletteSans-{s}.ttf') for s in sib_styles]
    if all(os.path.exists(p) for p in sib_paths):
        sib_fonts = [TTFont(p, lazy=True) for p in sib_paths]
        sib_glyfs = [f['glyf'] for f in sib_fonts]
        owned_glyphs = sorted(
            {'ij', 'uni01E4', 'uni01E8', 'uni021E', 'uni0229', 'uni0191'}
            | {f'uni{cp:04X}' for cp in range(0x01CF, 0x01DD) if cp != 0x01D4}
            | {UV2AGL.get(cp, f'uni{cp:04X}') for cp in list(range(0x2150, 0x2160)) + [0x2189]}
            | {gn for gn in GO if '.latin_gaps' in gn}
        )
        for gn in owned_glyphs:
            sigs = set()
            no_xform = True
            for gl in sib_glyfs:
                g = gl[gn]
                if g.isComposite():
                    if any(c.flags & 0x00C8 for c in g.components):
                        no_xform = False
                    sigs.add(('comp', tuple(c.glyphName for c in g.components)))
                else:
                    sigs.add((g.numberOfContours, tuple(g.endPtsOfContours), tuple(int(f) & 1 for f in g.flags)))
            check(no_xform, f'{gn}: uses scaled/transformed composite component')
            check(len(sigs) == 1, f'{gn}: contour/point drift across {"italic" if ITALIC else "upright"} weights: {sigs}')
        for f in sib_fonts:
            f.close()

# ---- 9. Outline quality (outline_check.py) on all module simple glyphs ---------
OWNED_CANDIDATES = sorted(
    {'ij', 'uni01E4', 'uni01E8', 'uni021E', 'uni0229', 'uni0191'}
    | {f'uni{cp:04X}' for cp in range(0x01CF, 0x01DD) if cp != 0x01D4}
    | {UV2AGL.get(cp, f'uni{cp:04X}') for cp in list(range(0x2150, 0x2160)) + [0x2189]}
    | {gn for gn in GO if '.latin_gaps' in gn}
)
for gn in OWNED_CANDIDATES:
    if gn in HAVE:
        g_oc = GLYF[gn]
        if not g_oc.isComposite() and g_oc.numberOfContours > 0:
            probs = outline_check.check(g_oc, GLYF)
            check(not probs, f'{gn}: outline_check problems {probs}')

print(f'latin_gaps {STYLE} {MODE}: {checks - len(fails)}/{checks} checks passed')
for f in fails[:40]:
    print('  FAIL', f)
sys.exit(1 if fails else 0)

"""Check the cyrillic module: small caps, metrics, stems, slant, marks, and kerning.

    python verify_cyrillic.py FONT.ttf STYLE full|subset
"""
import os
import sys
import unicodedata

import pathops
import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import outline_check

FONT_PATH = sys.argv[1]
STYLE = sys.argv[2] if len(sys.argv) > 2 else 'Regular'
MODE = sys.argv[3] if len(sys.argv) > 3 else 'full'
ITALIC = 'Italic' in STYLE
SUF = '.sc.cyrillic'

font = TTFont(FONT_PATH)
cmap = font.getBestCmap()

if MODE == 'subset' and 0x0410 not in cmap:
    print(f'cyrillic {STYLE} subset: subset omits U+0400-04FF until Makefile UNICODES update (skipped)')
    sys.exit(0)

glyf = font['glyf']
hmtx = font['hmtx']
os2 = font['OS/2']
hhea = font['hhea']
gs = font.getGlyphSet()
order = font.getGlyphOrder()

hb_face = hb.Face(hb.Blob.from_file_path(FONT_PATH))
hb_font = hb.Font(hb_face)

fails = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)
        if len(fails) <= 25:
            print(f'[verify_cyrillic FAIL] {msg}')


def shape(text, feats=None, lang=None):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    if lang:
        b.language = lang
    hb.shape(hb_font, b, feats or {})
    out = []
    x = 0
    for info, pos in zip(b.glyph_infos, b.glyph_positions):
        out.append({
            'g': order[info.codepoint],
            'adv': pos.x_advance,
            'dx': pos.x_offset,
            'dy': pos.y_offset,
            'x': x + pos.x_offset,
            'y': pos.y_offset,
        })
        x += pos.x_advance
    return out


def bounds(name, dx=0, dy=0):
    bp = BoundsPen(gs)
    pen = TransformPen(bp, (1, 0, 0, 1, dx, dy)) if (dx or dy) else bp
    gs[name].draw(pen)
    return bp.bounds


def path_of(name):
    p = pathops.Path()
    gs[name].draw(p.getPen(glyphSet=gs))
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


# 1. Coverage & bicameral pairing
cyr_cps = sorted(u for u in cmap if 0x0400 <= u <= 0x052F)
if MODE == 'full':
    check(len(cyr_cps) == 236, f'expected 236 Cyrillic code points in full font, got {len(cyr_cps)}')
else:
    c04 = [u for u in cyr_cps if 0x0400 <= u <= 0x04FF]
    check(len(c04) == 220, f'expected 220 U+0400..04FF code points in subset, got {len(c04)}')

caps_u = [u for u in cyr_cps if unicodedata.category(chr(u)) == 'Lu']
lows_u = [u for u in cyr_cps if unicodedata.category(chr(u)) == 'Ll']
check(len(caps_u) == len(lows_u) and len(caps_u) >= 110, f'Lu/Ll count mismatch: {len(caps_u)} vs {len(lows_u)}')

# 2. smcp & c2sc GSUB coverage + default shaping isolation
for u in caps_u:
    ch_u = chr(u)
    ch_l = ch_u.lower()
    want = cmap[u] + SUF
    check(ord(ch_l) in cmap, f'missing lowercase for U+{u:04X}')
    r_smcp_l = shape(ch_l, {'smcp': 1})
    r_c2sc_l = shape(ch_l, {'c2sc': 1})
    r_both_l = shape(ch_l, {'smcp': 1, 'c2sc': 1})
    r_c2sc_u = shape(ch_u, {'c2sc': 1})
    r_smcp_u = shape(ch_u, {'smcp': 1})
    r_both_u = shape(ch_u, {'smcp': 1, 'c2sc': 1})
    check(len(r_smcp_l) == 1 and r_smcp_l[0]['g'] == want, f'smcp {ch_l} (U+{ord(ch_l):04X}): got {[x["g"] for x in r_smcp_l]}, want {want}')
    check(len(r_c2sc_u) == 1 and r_c2sc_u[0]['g'] == want, f'c2sc {ch_u} (U+{u:04X}): got {[x["g"] for x in r_c2sc_u]}, want {want}')
    check(len(r_both_l) == 1 and r_both_l[0]['g'] == want, f'smcp+c2sc {ch_l}: got {[x["g"] for x in r_both_l]}')
    check(len(r_both_u) == 1 and r_both_u[0]['g'] == want, f'smcp+c2sc {ch_u}: got {[x["g"] for x in r_both_u]}')
    check(r_c2sc_l[0]['g'] == cmap[ord(ch_l)], f'c2sc altered lowercase {ch_l}: {r_c2sc_l[0]["g"]}')
    check(r_smcp_u[0]['g'] == cmap[u], f'smcp altered capital {ch_u}: {r_smcp_u[0]["g"]}')

all_cyr_str = ''.join(chr(u) for u in cyr_cps)
for feats in ({}, {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}):
    shaped_def = shape(all_cyr_str, feats)
    check(not any('.cyrillic' in x['g'] for x in shaped_def), f'default shaping {feats} emitted a .cyrillic glyph')

if MODE == 'full':
    # Localized Bashkir ('ba') and Chuvash ('cv') small caps
    for lang, ch_l, ch_u, want in [
        ('ba', '\u0456', '\u0406', 'uni0406.loclBSH' + SUF),
        ('ba', '\u0493', '\u0492', 'uni0492.loclBSH' + SUF),
        ('cv', '\u0499', '\u0498', 'uni0498.loclCHU' + SUF),
        ('cv', '\u04AB', '\u04AA', 'uni04AA.loclCHU' + SUF),
    ]:
        check(shape(ch_l, {'smcp': 1}, lang)[0]['g'] == want, f'locl {lang} smcp {ch_l}: got {shape(ch_l, {"smcp": 1}, lang)[0]["g"]}, want {want}')
        check(shape(ch_u, {'c2sc': 1}, lang)[0]['g'] == want, f'locl {lang} c2sc {ch_u}: got {shape(ch_u, {"c2sc": 1}, lang)[0]["g"]}, want {want}')

# 3. GDEF, non-nested components, line metrics, heights, overshoots, and homograph parity
cd = font['GDEF'].table.GlyphClassDef.classDefs
lo_y = max(hhea.descent, -os2.usWinDescent, os2.sTypoDescender)
hi_y = min(hhea.ascent, os2.usWinAscent, os2.sTypoAscender)

cyr_sc_glyphs = [g for g in order if g.endswith('.cyrillic')]
check(len(cyr_sc_glyphs) >= 110, f'too few .cyrillic glyphs: {len(cyr_sc_glyphs)}')
for g in cyr_sc_glyphs:
    check(cd.get(g) == 1, f'GDEF class of {g} is {cd.get(g)}, want 1')
    check(hmtx[g][0] > 0, f'{g}: non-positive advance {hmtx[g][0]}')
    rg = glyf[g]
    if rg.isComposite():
        nested = [c.glyphName for c in rg.components if glyf[c.glyphName].isComposite()]
        check(not nested, f'{g} has nested components: {nested}')
    elif rg.numberOfContours > 0:
        bad_out = outline_check.check(rg, glyf)
        check(not bad_out, f'{g} outline_check problems: {bad_out}')
    b = bounds(g)
    check(b is not None and lo_y <= b[1] and b[3] <= hi_y, f'{g}: bounds {b} outside {lo_y}..{hi_y}')

FLAT_SC = 'АВГДЕЖИКЛМНПРТУХЦЧШЩЪЫЬЯІЈЂЉЊЋЏ'
ROUND_SC = 'ОСЭЮЄЅЗӨӘ'
DESC_SC = 'ДЦЩЈЂЏҚҢҪҬҲҶ'

for ch in FLAT_SC:
    if ord(ch) in cmap:
        b = bounds(cmap[ord(ch)] + SUF)
        check(548 <= b[3] <= 552, f'flat small cap {ch}: yMax {b[3]} not in 548..552')
for ch in ROUND_SC:
    if ord(ch) in cmap:
        b = bounds(cmap[ord(ch)] + SUF)
        check(553 <= b[3] <= 564, f'round small cap {ch}: yMax {b[3]} not in 553..564')
if 0x0424 in cmap:  # Ф
    b_phi = bounds(cmap[0x0424] + SUF)
    check(555 <= b_phi[3] <= 582, f'Ф small cap: yMax {b_phi[3]} not in 555..582')
for ch in DESC_SC:
    if ord(ch) in cmap:
        b = bounds(cmap[ord(ch)] + SUF)
        check(-170 <= b[1] <= -100, f'descending small cap {ch}: yMin {b[1]} not in -170..-100')

for ch, lat in [('А', 'A.sc'), ('В', 'B.sc'), ('Е', 'E.sc'), ('І', 'I.sc'), ('О', 'O.sc'),
                ('Р', 'P.sc'), ('С', 'C.sc'), ('Т', 'T.sc'), ('Х', 'X.sc')]:
    if ord(ch) in cmap and lat in glyf:
        sc = cmap[ord(ch)] + SUF
        check(hmtx[sc][0] == hmtx[lat][0], f'{ch}.sc advance {hmtx[sc][0]} != {lat} {hmtx[lat][0]}')
        bs, bl = bounds(sc), bounds(lat)
        check(all(abs(a - b) <= 1 for a, b in zip(bs, bl)), f'{ch}.sc bounds {bs} != {lat} {bl}')

# 4. Stem weight parity and italic slant parity against H.sc
h_spans = hspans(path_of('H.sc'), 140)
h_stem = h_spans[0][1] - h_spans[0][0]
for ch in ('П', 'Ш', 'Н'):
    sc = cmap[ord(ch)] + SUF
    sp = hspans(path_of(sc), 140)
    st_w = sp[0][1] - sp[0][0]
    check(abs(st_w - h_stem) <= max(3.0, 0.05 * h_stem), f'{ch}.sc stem {st_w:.1f} differs from H.sc {h_stem:.1f}')


def left_edge_slope(gname):
    p = path_of(gname)
    s_lo = hspans(p, 120)[0]
    s_hi = hspans(p, 430)[0]
    return (s_hi[0] - s_lo[0]) / (430 - 120)


h_slope = left_edge_slope('H.sc')
for ch in ('П', 'И', 'Ш', 'Н'):
    sc = cmap[ord(ch)] + SUF
    sl = left_edge_slope(sc)
    check(abs(sl - h_slope) <= 0.008, f'{ch}.sc slope {sl:.4f} differs from H.sc {h_slope:.4f}')
    if ITALIC:
        check(0.145 <= sl <= 0.175, f'italic {ch}.sc slope {sl:.4f} out of range')
    else:
        check(abs(sl) <= 0.005, f'upright {ch}.sc slope {sl:.4f} not vertical')

# 5. Precomposed accented small caps + combining acute (U+0301) attachment
ACC_CAPS = 'ЀЁЃЇЌЍЎЙҊӁӐӒӖӚӜӞӢӤӦӪӬӮӰӲӴӸ'
for ch in ACC_CAPS:
    if ord(ch) not in cmap:
        continue
    sc = cmap[ord(ch)] + SUF
    b = bounds(sc)
    check(680 <= b[3] <= hi_y, f'accented {ch}.sc yMax {b[3]} not in 680..{hi_y}')
    # Verify non-collision: empty horizontal band between base top (~558) and mark bottom (~590+)
    mid_band = hspans(path_of(sc), 576)
    check(len(mid_band) == 0, f'accented {ch}.sc mark collides with base at y=576: {mid_band}')

# Combining stress mark U+0301 on Russian & Ukrainian vowels (lowercase, uppercase, smcp, c2sc)
for ch_l in 'аеиоуыэюяіє':
    if ord(ch_l) not in cmap:
        continue
    ch_u = ch_l.upper()
    for txt, feats in [
        (ch_l + '\u0301', {}),
        (ch_u + '\u0301', {}),
        (ch_l + '\u0301', {'smcp': 1}),
        (ch_u + '\u0301', {'c2sc': 1}),
    ]:
        r = shape(txt, feats)
        check(len(r) == 2 and r[1]['adv'] == 0, f'mark {txt!r} {feats}: {r}')
        if len(r) == 2:
            bb = bounds(r[0]['g'], r[0]['dx'], r[0]['dy'])
            mb = bounds(r[1]['g'], r[1]['x'] - r[0]['x'], r[1]['dy'])
            slant_dx = h_slope * ((mb[1] + mb[3]) / 2 - bb[3]) if ITALIC else 0.0
            mx = (mb[0] + mb[2]) / 2 - slant_dx
            check(bb[0] - 45 <= mx <= bb[2] + 50, f'mark {txt!r} {feats}: unslanted mark mid {mx:.0f} off base {bb[0]}..{bb[2]}')
            check(bb[3] + 15 <= mb[1] <= bb[3] + 135, f'mark {txt!r} {feats}: mark bottom {mb[1]} vs base top {bb[3]}')
            check(mb[3] <= hi_y, f'mark {txt!r} {feats}: mark top {mb[3]} > {hi_y}')
    # smcp on lowercase + acute matches c2sc on uppercase + acute
    r_s = shape(ch_l + '\u0301', {'smcp': 1})
    r_c = shape(ch_u + '\u0301', {'c2sc': 1})
    check(
        [(x['g'], x['adv'], x['dx'], x['dy']) for x in r_s] == [(x['g'], x['adv'], x['dx'], x['dy']) for x in r_c],
        f'smcp vs c2sc mismatch on {ch_l}/{ch_u} + U+0301: {r_s} vs {r_c}',
    )

# 6. Small-cap kerning & cross-script Latin<->Cyrillic kerning
def kern_delta(pair, feats=None):
    f_on = dict(feats or {}, kern=1)
    f_off = dict(feats or {}, kern=0)
    on = shape(pair, f_on)
    off = shape(pair, f_off)
    return on[0]['adv'] - off[0]['adv']


for pair in ('ТА', 'АТ', 'ТО', 'ОТ', 'ТД', 'ВА', 'АУ', 'УО', 'ГД', 'ГА', 'ДТ', '«Т'):
    d = kern_delta(pair, {'smcp': 1, 'c2sc': 1})
    check(d < 0, f'Cyrillic small-cap pair {pair!r} not kerned ({d})')

for pair in ('то', 'та', 'ау', 'уо', 'гд'):
    d = kern_delta(pair, {'smcp': 1})
    check(d < 0, f'Cyrillic smcp lowercase pair {pair!r} not kerned ({d})')

# Cross-script Latin <-> Cyrillic pairs (full-size and small caps)
for pair in (
    'A\u0422',  # Latin A + Cyrillic Т
    '\u0422A',  # Cyrillic Т + Latin A
    'T\u043E',  # Latin T + Cyrillic о
    '\u0422o',  # Cyrillic Т + Latin o
    'V\u0410',  # Latin V + Cyrillic А
    'V\u0414',  # Latin V + Cyrillic Д
    'L\u0422',  # Latin L + Cyrillic Т
    '\u0413o',  # Cyrillic Г + Latin o
    '\u0423e',  # Cyrillic У + Latin e
):
    d = kern_delta(pair, {})
    check(d < 0, f'cross-script pair {pair!r} ({[ hex(ord(c)) for c in pair ]}) not kerned ({d})')

for pair in ('A\u0422', '\u0422A', 'V\u0414', 'L\u0422', '\u0413O'):
    d = kern_delta(pair, {'smcp': 1, 'c2sc': 1})
    check(d < 0, f'cross-script small-cap pair {pair!r} not kerned ({d})')

# Capitals against punctuation (CYRILLIC_PUNCT_KERN): Г and its accented forms as T, at
# least as tight as T (Г's arm reaches farther); У and its forms as Y on both sides; Ч, whose
# right side is a stem, stays 0, as H. does.
t_dot = kern_delta('T.')
for g in 'ГЃҐҒ':
    for p in '.,…»›:':
        d = kern_delta(g + p)
        tight = g != 'Ғ' or p in '.,…'               # Ғ's stroke stands out at mid-height
        check(d < 0 and (d <= kern_delta('T' + p) or not tight), f'{g}{p} kerned {d}, T{p} {kern_delta("T" + p)}')
for g in 'УЎӮӰӲ':
    for p in '.,…»':
        d = kern_delta(g + p)
        check(d < 0, f'{g}{p} not kerned ({d})')
    for p in '«‹':
        d = kern_delta(p + g)
        check(d < 0, f'{p}{g} not kerned ({d})')
check(kern_delta('Ч.') == 0 and kern_delta('«Г') == 0, f'Ч. {kern_delta("Ч.")}, «Г {kern_delta("«Г")}: should stay 0')

print(f'cyrillic {STYLE} {MODE}: {checks - len(fails)}/{checks} checks passed ({len(cyr_sc_glyphs)} .sc.cyrillic glyphs)')
sys.exit(1 if fails else 0)

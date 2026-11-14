"""Checks of the greek module: coverage, fit to Torchlette's metrics, small caps, kerning.

    MULISH_STATIC=... python verify_greek.py FONT.ttf STYLE full|subset

Coverage: every modern Greek letter, the tonos and dialytika forms, the seven
mathematical variants and the Greek punctuation are mapped. Fit: x-height letters top
out at the x-height, ascenders at d's height, descenders at p's depth, capitals at the
cap height; the stems of eta and Psi match n's and H's; omicron and the Latin-shaped
capitals have their Latin glyph's advance; every glyph stays inside the vertical
metrics and every lowercase advance is within [0.45, 1.45] of o's. Sigma rests on the
baseline while the summation sign keeps its descender. smcp and c2sc turn every Greek
letter into a small capital under HarfBuzz, and Commissioner's largest Greek kerning
pairs still kern.
"""
import os
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont

FONT_PATH = sys.argv[1]
STYLE = sys.argv[2] if len(sys.argv) > 2 else 'Regular'
MODE = sys.argv[3] if len(sys.argv) > 3 else 'full'

fails = []


def fail(msg):
    fails.append(msg)
    print(f'[verify_greek FAIL] {msg}')


font = TTFont(FONT_PATH)
cmap = font.getBestCmap()
glyf = font['glyf']
hmtx = font['hmtx']
os2 = font['OS/2']

hb_face = hb.Face(hb.Blob.from_file_path(FONT_PATH))
hb_font = hb.Font(hb_face)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties()
    hb.shape(hb_font, b, feats or {})
    return [hb_font.get_glyph_name(i.codepoint) for i in b.glyph_infos], b.glyph_positions


def bounds(name):
    g = glyf[name]
    if g.isComposite() or g.numberOfContours > 0:
        g.recalcBounds(glyf); return g.xMin, g.yMin, g.xMax, g.yMax
    return None


checks = 0

# 1. coverage
CAPS = list(range(0x0391, 0x03A2)) + list(range(0x03A3, 0x03AA))
LC = list(range(0x03B1, 0x03CA))
ACC_CAPS = [0x0386, 0x0388, 0x0389, 0x038A, 0x038C, 0x038E, 0x038F, 0x03AA, 0x03AB]
ACC_LC = [0x03AC, 0x03AD, 0x03AE, 0x03AF, 0x03CC, 0x03CD, 0x03CE, 0x03CA, 0x03CB, 0x0390, 0x03B0]
MATH = [0x03D1, 0x03D5, 0x03D6, 0x03F0, 0x03F1, 0x03F4, 0x03F5]
PUNCT = [0x037E, 0x0387, 0x0384, 0x0385, 0x0374, 0x0375]
ALL = CAPS + LC + ACC_CAPS + ACC_LC + MATH + PUNCT
missing = [f'U+{u:04X}' for u in ALL if u not in cmap]
if missing: fail(f'unmapped code points: {missing}')
checks += len(ALL)
print(f'coverage: {len(ALL)} code points mapped')

# 2. vertical bounds and advances
G = {u: cmap[u] for u in ALL if u in cmap}
for u, n in sorted(G.items()):
    adv, _ = hmtx[n]
    if adv <= 0: fail(f'{n}: advance {adv}')
    b = bounds(n)
    if b and (b[3] > os2.sTypoAscender or b[1] < os2.sTypoDescender or b[3] > os2.usWinAscent or b[1] < -os2.usWinDescent):
        fail(f'{n}: bounds {b} outside the vertical metrics')
    checks += 1
print(f'bounds: {len(G)} glyphs inside typo {os2.sTypoDescender}..{os2.sTypoAscender} and win -{os2.usWinDescent}..{os2.usWinAscent}')

o_adv = hmtx['o'][0]
for u in LC:
    adv = hmtx[cmap[u]][0]
    if not 0.45 * o_adv <= adv <= 1.45 * o_adv: fail(f'{cmap[u]}: advance {adv} outside [0.45, 1.45] of o ({o_adv})')
    checks += 1
print('advances: lowercase within [0.45, 1.45] of o')

# 3. fit to Torchlette's metrics
XH = os2.sxHeight; ASC = bounds('d')[3]; DESC = bounds('p')[1]; CAP = bounds('H')[3]
def within(name, lo, hi, idx, what):
    global checks
    v = bounds(name)[idx]
    if not lo <= v <= hi: fail(f'{name}: {what} {v} not in [{lo}, {hi}]')
    checks += 1
for ch in 'ικντσ': within(cmap[ord(ch)], XH - 8, XH + 14, 3, 'top')
for ch in 'αε': within(cmap[ord(ch)], XH + 1, XH + 18, 3, 'top (overshoot)')
for ch in 'βδθλ': within(cmap[ord(ch)], ASC - 8, ASC + 8, 3, 'ascender')
for ch in 'ηρφψβ': within(cmap[ord(ch)], DESC - 5, DESC + 5, 1, 'descender')
for ch in 'γχ': within(cmap[ord(ch)], DESC - 8, DESC + 10, 1, 'descender')
for ch in 'ΣΨΓΠΞΛ': within(cmap[ord(ch)], CAP - 3, CAP + 3, 3, 'cap height')
for ch in 'ΦΘ': within(cmap[ord(ch)], CAP - 2, CAP + 26, 3, 'cap height (overshoot)')
for ch in 'ΣΨΓΠΞΛ': within(cmap[ord(ch)], -3, 2, 1, 'baseline')
for ch in 'ΦΘ': within(cmap[ord(ch)], -26, 2, 1, 'baseline (overshoot)')
print(f'fit: x-height {XH}, ascender {ASC}, descender {DESC}, cap height {CAP}')

import pathops
def path(name):
    p = pathops.Path(); gs = font.getGlyphSet(); gs[name].draw(p.getPen(glyphSet=gs)); return p
def spans(p, y):
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((-5000, y - 0.25)); pen.lineTo((5000, y - 0.25)); pen.lineTo((5000, y + 0.25)); pen.lineTo((-5000, y + 0.25)); pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION)
    return sorted((c.bounds[0], c.bounds[2]) for c in q.contours)
def stem(name, y):
    s = spans(path(name), y); return s[0][1] - s[0][0]
n_stem = stem('n', XH / 2); eta_stem = stem(cmap[0x03B7], XH / 2)
if abs(eta_stem - n_stem) > 2.5: fail(f'eta stem {eta_stem:.1f} differs from n stem {n_stem:.1f}')
H_stem = stem('H', CAP * 0.2); psi_stem = stem(cmap[0x03A8], CAP * 0.1)
if abs(psi_stem - H_stem) > max(3.5, 0.05 * H_stem): fail(f'Psi stem {psi_stem:.1f} differs from H stem {H_stem:.1f}')
checks += 2
print(f'stems: eta {eta_stem:.1f} ~ n {n_stem:.1f}; Psi {psi_stem:.1f} ~ H {H_stem:.1f}')

for u, latin in {0x03BF: 'o', 0x0391: 'A', 0x0392: 'B', 0x0395: 'E', 0x0396: 'Z', 0x0397: 'H', 0x0399: 'I', 0x039A: 'K',
                 0x039C: 'M', 0x039D: 'N', 0x039F: 'O', 0x03A1: 'P', 0x03A4: 'T', 0x03A5: 'Y', 0x03A7: 'X', 0x0393: 'F', 0x03A0: 'H'}.items():
    if hmtx[cmap[u]][0] != hmtx[latin][0]: fail(f'{cmap[u]} advance {hmtx[cmap[u]][0]} differs from {latin} ({hmtx[latin][0]})')
    checks += 1
print('advances: omicron and the Latin-shaped capitals match their Latin glyphs')

# 4. Sigma on the baseline, summation descending
sig = bounds(cmap[0x03A3])
if sig[1] < -3: fail(f'Sigma descends to {sig[1]}')
if 'summation' in glyf.glyphs:
    sm = bounds('summation')
    if sm[1] > -150: fail(f'summation lost its descender: yMin {sm[1]}')
checks += 2
print(f'Sigma {sig[1]}..{sig[3]}; summation keeps its descender')

# 4b. the dialytika-tonos: two dots and a tonos that touch nothing, not much wider than
# the dieresis, and no wider than its advance (in an italic the slant moves it right)
dt = cmap.get(0x0385)
if dt:
    n_c = glyf[dt].numberOfContours if not glyf[dt].isComposite() else -1
    if n_c != 3: fail(f'{dt}: {n_c} contours, not two dots and a tonos apart')
    db, tb_ = bounds('uni0308'), bounds(dt)
    ratio = (tb_[2] - tb_[0]) / (db[2] - db[0])
    if not 1.0 < ratio < 1.6: fail(f'{dt}: {ratio:.2f} times the dieresis width')
    adv = hmtx[dt][0]
    if tb_[2] - tb_[0] > adv: fail(f'{dt}: ink {tb_[0]}..{tb_[2]} wider than its advance {adv}')
    checks += 3
    print(f'dialytika-tonos: 3 parts, {ratio:.2f} times the dieresis width')

# 5. small caps under HarfBuzz
def all_sc(text, feat, what):
    global checks
    names, _ = shape(text, {feat: 1})
    for ch, gn in zip(text, names):
        if not (gn.endswith('.sc') or gn.endswith('.sc.greek')): fail(f'{what} {ch} U+{ord(ch):04X} under {feat}: {gn}')
    checks += len(text)
all_sc('αβγδεζηθικλμνξοπρσςτυφχψω', 'smcp', 'lowercase')
all_sc('άέήίόύώϊϋΐΰ', 'smcp', 'accented lowercase')
all_sc('ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ', 'c2sc', 'capital')
all_sc('ΆΈΉΊΌΎΏΪΫ', 'c2sc', 'accented capital')
# the symbol forms take the small capital of their Unicode uppercase, as the plain letter
# does (issue 22); the micro sign keeps its form under smcp (a unit sign, not text)
for sym, plain, feat in (('ϑ', 'θ', 'smcp'), ('ϕ', 'φ', 'smcp'), ('ϖ', 'π', 'smcp'), ('ϰ', 'κ', 'smcp'),
                         ('ϱ', 'ρ', 'smcp'), ('ϵ', 'ε', 'smcp'), ('ϴ', 'Θ', 'c2sc')):
    got, want = shape(sym, {feat: 1})[0], shape(plain, {feat: 1})[0]
    if got != want: fail(f'{sym} U+{ord(sym):04X} under {feat}: {got}, not {plain}\'s small capital {want}')
    checks += 1
if 0x00B5 in cmap and shape('µ', {'smcp': 1})[0] != [cmap[0x00B5]]: fail(f'µ U+00B5 changes under smcp: {shape("µ", {"smcp": 1})[0]}')
checks += 1
names, _ = shape('αβγδεζηθικλμνξοπρσςτυφχψω')
if any(n.endswith('.sc') or n.endswith('.sc.greek') for n in names): fail('small caps appear without smcp')
checks += 1
print('small caps: smcp and c2sc cover every Greek letter and the symbol forms ϑ ϕ ϖ ϰ ϱ ϵ ϴ; µ stays')

# 6. kerning
for pair in ['ΤΑ', 'ΑΥ', 'Το', 'Γα', 'ΛΤ', 'Υο']:
    _, on = shape(pair, {'kern': 1}); _, off = shape(pair, {'kern': 0})
    d = on[0].x_advance - off[0].x_advance
    if d >= 0: fail(f'pair {pair} not kerned ({d})')
    checks += 1
print('kerning: Commissioner\'s large Greek pairs kern')

# 7. Latin against Greek, shaped as one run (issue 26): a Greek letter that is a Latin
# one kerns against Latin letters, on both sides, as its twin does; a Greek letter that
# is none kerns against the Latin twins as against their Greek twins (Yα as Υα)
def kern_of(pair):
    _, on = shape(pair, {'kern': 1}); _, off = shape(pair, {'kern': 0})
    return on[0].x_advance - off[0].x_advance
have = lambda s: all(ord(c) in cmap for c in s)
TWINS = {'Α': 'A', 'Β': 'B', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Ι': 'I', 'Κ': 'K', 'Μ': 'M', 'Ν': 'N', 'Ο': 'O', 'Ρ': 'P',
         'Τ': 'T', 'Υ': 'Y', 'Χ': 'X', 'Ϊ': 'Ï', 'Ϋ': 'Ÿ', 'ο': 'o'}
# (not à á â ...: Mulish leaves those a's unkerned and kern.py gives them a's kerning
# afterwards, against the Latin letters only; Τà is 0 where Tà kerns)
PARTNERS = 'AJLOTVWYacefjortvwxyÀÝéôý'
n_twin = nz_twin = 0
for gr, la in TWINS.items():
    for x in PARTNERS:
        for mixed, model in ((gr + x, la + x), (x + gr, x + la)):
            if not have(mixed + model): continue
            km, k0 = kern_of(mixed), kern_of(model)
            if km != k0: fail(f'{mixed} kerns {km}, its Latin model {model} {k0}')
            n_twin += 1; nz_twin += bool(k0)
            checks += 1
if nz_twin < n_twin // 4: fail(f'only {nz_twin} of {n_twin} twin models kern: the partners test too little')
GREEK_ONLY = 'αγδελπστυφχψωΓΔΘΛΞΠΣΦΨΩ'
n_gr = nz_gr = 0
for la, gr in (('A', 'Α'), ('T', 'Τ'), ('Y', 'Υ'), ('O', 'Ο'), ('P', 'Ρ'), ('o', 'ο'), ('X', 'Χ'), ('K', 'Κ')):
    for y in GREEK_ONLY:
        for mixed, model in ((la + y, gr + y), (y + la, y + gr)):
            if not have(mixed + model): continue
            km, k0 = kern_of(mixed), kern_of(model)
            if km != k0: fail(f'{mixed} kerns {km}, its Greek model {model} {k0}')
            n_gr += 1; nz_gr += bool(k0)
            checks += 1
for pair in ['AΥ', 'AΤ', 'ΑV', 'TΟ', 'Yα', 'Vο', 'Τo', 'Υa', 'Tα']:
    if have(pair) and kern_of(pair) >= 0: fail(f'mixed pair {pair} not kerned ({kern_of(pair)})')
    checks += 1
print(f'kerning, Latin and Greek: {n_twin} twin pairs as their Latin models ({nz_twin} kerned), '
      f'{n_gr} as their Greek models ({nz_gr} kerned); AΥ ΑV TΟ Yα Vο kern')

if fails: sys.exit(1)
print(f'[verify_greek OK] {STYLE} {MODE}: {checks} checks passed.')

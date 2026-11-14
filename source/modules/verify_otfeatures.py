"""HarfBuzz check of the otfeatures module: case, cpsp, zero, mark attachment on
build.py's glyphs, GDEF classes and carets, aalt and salt, mgrk, nalt and the grek script record.

    MULISH_STATIC=Mulish-<wght>.ttf verify_otfeatures.py FONT.ttf STYLE full|subset

Every check shapes real text (or reads the table a shaper reads) and has a negative
counterpart: with the feature off, text shapes as without the module. With
TS_WEB_SUBSET=1 the features web_features.txt leaves out (case, cpsp, aalt, salt,
mgrk, nalt, the stylistic sets but ss01, ss02 and ss16) are not checked.
"""
import os, sys
import unicodedata
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.pointInsidePen import PointInsidePen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept   # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
tt = TTFont(PATH)
GO = tt.getGlyphOrder()
GS = tt.getGlyphSet()
HB = hb.Font(hb.Face(hb.Blob.from_file_path(PATH)))
MUL = set(TTFont(os.environ['MULISH_STATIC'], lazy=True).getGlyphOrder()) if os.environ.get('MULISH_STATIC') else None
SUF = '.otfeatures'
fails, checks = [], 0


def check(ok, what):
    global checks
    checks += 1
    if not ok: fails.append(what)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(HB, b, feats or {})
    out, x = [], 0
    for i, p in zip(b.glyph_infos, b.glyph_positions):
        out.append(dict(g=GO[i.codepoint], x=x + p.x_offset, y=p.y_offset, adv=p.x_advance, dx=p.x_offset, cl=i.cluster))
        x += p.x_advance
    return out


_bb = {}
def bounds(g):
    if g not in _bb:
        p = BoundsPen(GS); GS[g].draw(p); _bb[g] = p.bounds
    return _bb[g]


def ink(r):
    b = bounds(r['g'])
    return None if b is None else (b[0] + r['x'], b[1] + r['y'], b[2] + r['x'], b[3] + r['y'])


def names(text, feats=None): return [r['g'] for r in shape(text, feats)]


# ---------------------------------------------------------------- case
if kept('case'):
    CASE = {'(': 'parenleft', ')': 'parenright', '[': 'bracketleft', ']': 'bracketright', '{': 'braceleft',
            '}': 'braceright', '\u2013': 'endash', '\u2014': 'emdash', '\u00ab': 'guillemotleft', '\u00bb': 'guillemotright',
            '\u2039': 'guilsinglleft', '\u203a': 'guilsinglright', '@': 'at', '\u00b7': 'periodcentered',
            '\u00a1': 'exclamdown', '\u00bf': 'questiondown'}
    for ch, src in CASE.items():
        t = f'H{ch}H'
        off, on = shape(t), shape(t, {'case': 1})
        check(off[1]['g'] == src, f'case off: {ch!r} -> {off[1]["g"]}')
        want = f'{src}.case{SUF}'
        check(on[1]['g'] == want, f'case on: {ch!r} -> {on[1]["g"]}, want {want}')
        if on[1]['g'] == want:
            b = bounds(want)
            check(abs((b[1] + b[3]) / 2 - 352.5) <= 1, f'case {want}: ink middle {(b[1] + b[3]) / 2} not on the cap middle')
            check(on[1]['adv'] == off[1]['adv'], f'case {want}: advance {on[1]["adv"]} != {off[1]["adv"]}')
    on = shape('A-Z', {'case': 1})
    check(on[1]['g'] == 'hyphen.case', f'case: hyphen -> {on[1]["g"]}')
    check(names('a-z (x)') == names('a-z (x)', {'case': 0}), 'case off changes text')
    proof = '(ABC) [XYZ] \u00abNASA\u00bb \u00a1HOLA! A\u2013Z'
    check(not any(SUF in g for g in names(proof)), 'default shaping uses a case form')
    check(sum(SUF in g for g in names(proof, {'case': 1})) == 8, f'case proof: {names(proof, {"case": 1})}')
    # ss16 still sees the plain punctuation (its shape tuples) with case on
    check(names('(28, 28)', {'ss16': 1, 'case': 1})[2:4] == names('(28, 28)', {'ss16': 1})[2:4], 'case changes ss16 shape tuples')

# ---------------------------------------------------------------- cpsp
if kept('cpsp'):
    off, on = shape('HAMBURG hamburg'), shape('HAMBURG hamburg', {'cpsp': 1})
    for a, b in zip(off, on):
        up = a['g'][0].isupper()
        check(b['adv'] - a['adv'] == (20 if up else 0) and b['dx'] - a['dx'] == (10 if up else 0),
              f'cpsp {a["g"]}: advance {a["adv"]}->{b["adv"]}, offset {a["dx"]}->{b["dx"]}')
    check([r['adv'] for r in shape('ABC')] == [r['adv'] for r in shape('ABC', {'cpsp': 0})], 'cpsp on by default')

# ---------------------------------------------------------------- zero
if kept('zero'):
    ZERO = [({}, 'zero'), ({'pnum': 1}, 'zero.pnum'), ({'onum': 1}, 'zero.osf'), ({'onum': 1, 'tnum': 1}, 'zero.tosf'),
            ({'onum': 1, 'pnum': 1}, 'zero.osf'), ({'smcp': 1}, 'zero.sc'), ({'smcp': 1, 'tnum': 1}, 'zero.sc.tf'),
            ({'sups': 1}, 'uni2070'), ({'subs': 1}, 'uni2080'), ({'sinf': 1}, 'uni2080'), ({'numr': 1}, 'zero.numr'),
            ({'dnom': 1}, 'zero.dnom'), ({'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}, 'zero.osf')]
    for feats, src in ZERO:
        if not kept(*feats): continue
        off = shape('101', feats); on = shape('101', dict(feats, zero=1))
        check(off[1]['g'] == src, f'zero off {feats}: {off[1]["g"]}, want {src}')
        want = f'{src}.zero{SUF}'
        check(on[1]['g'] == want, f'zero on {feats}: {on[1]["g"]}, want {want}')
        check([r['g'] for r in on[::2]] == [r['g'] for r in off[::2]], f'zero {feats} changed the 1s')
        check(on[1]['adv'] == off[1]['adv'] and on[2]['x'] == off[2]['x'], f'zero {feats}: spacing changed')
        if on[1]['g'] == want:
            b = bounds(src); c = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
            pa, pb = PointInsidePen(GS, c), PointInsidePen(GS, c)
            GS[src].draw(pa); GS[want].draw(pb)
            check(not pa.getResult() and pb.getResult(), f'zero {want}: no slash across the counter')
            # within a unit: an italic ring's extremes lie between its points, and the slashed
            # copy's re-approximated curves move them by a fraction
            bw, bs = bounds(want), bounds(src)
            check(all(abs(a - b) <= 1 for a, b in zip(bw, bs)), f'zero {want}: ink box {bw} != {bs} (slash outside the ring)')
    fr = names('10/20', {'frac': 1, 'zero': 1})
    if kept('frac'): check(fr[1].endswith('.zero' + SUF) and fr[-1].endswith('.zero' + SUF), f'zero in fractions: {fr}')
    check(names('0O 1Il 00A0', {'zero': 1}).count(f'zero.zero{SUF}') == 4 and 'O' in names('0O', {'zero': 1}), 'zero proof')
    check(not any(SUF in g for g in names('0O 1Il 00A0 0.5 \u2070', {'calt': 0})), 'shaping with calt off uses a slashed zero')

# ---------------------------------------------------------------- calt: the lone zero
# A zero is slashed by default only when it is the only digit of its number: no figure
# (of any form) touches it, and no . , U+2009 U+202F joins it to one. Each case is the
# text and the same text with Ø for every zero that must be slashed.
CALT = [('0 x0 (0) 0, 0.05 10 2026 100 0', 'Ø xØ (Ø) Ø, 0.05 10 2026 100 Ø'),
        ('row 0, x[0], 0x, O0, a0b, "0", 0.', 'row Ø, x[Ø], Øx, OØ, aØb, "Ø", Ø.'),
        ('0.5 5.0 1,000 0,5 1.0e-3 10\u2009000 0\u202f5 0.0 00', '0.5 5.0 1,000 0,5 1.0e-3 10\u2009000 0\u202f5 0.0 00'),
        ('(0, 0) 0-1 1-10 0th 0/1 10/20 0\u0301', '(Ø, Ø) Ø-1 1-10 Øth Ø/1 10/20 Ø\u0301'),
        ('x\u2070 10\u2070 x\u2080 1\u2080\u2080 \u2070', 'xØ 10\u2070 xØ 1\u2080\u2080 Ø')]
CALT_FEATS = [({}, 'zero'), ({'onum': 1}, 'zero.osf'), ({'onum': 1, 'tnum': 1}, 'zero.tosf'), ({'tnum': 1}, 'zero'),
              ({'pnum': 1}, 'zero.pnum'), ({'smcp': 1}, 'zero.sc'), ({'smcp': 1, 'tnum': 1}, 'zero.sc.tf'),
              ({'sups': 1}, 'uni2070'), ({'subs': 1}, 'uni2080'), ({'numr': 1}, 'zero.numr'), ({'dnom': 1}, 'zero.dnom'),
              ({'lnum': 1, 'onum': 1}, 'zero.pnum'), ({'lnum': 1, 'onum': 1, 'tnum': 1}, 'zero'), ({'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}, 'zero.osf')]


def zeros_of(text, feats):
    """The text with each zero (any form) that shaped to a slashed zero written Ø."""
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(HB, b, feats)
    by = {}
    for i in b.glyph_infos: by.setdefault(i.cluster, []).append(GO[i.codepoint])
    return ''.join('Ø' if ch in '0\u2070\u2080' and any(g.endswith('.zero' + SUF) for g in by.get(k, ())) else ch
                   for k, ch in enumerate(text)), by


if kept('calt'):
    for feats, form in CALT_FEATS:
        if not kept(*feats): continue
        for text, want in CALT:
            if feats and ('\u2070' in text or '\u2080' in text or '/' in text): continue  # the encoded ones are their own forms
            got, by = zeros_of(text, feats)
            check(got == want, f'calt {feats}: {text!r} -> {got!r}, want {want!r}')
        got, by = zeros_of('0 10', feats)
        check(by[0][0] == f'{form}.zero{SUF}' and by[3][0] == form, f'calt {feats}: lone zero {by[0]}, in 10 {by[3]}, want {form}(.zero{SUF})')
        check(zeros_of('0 10', dict(feats, calt=0))[0] == '0 10', f'calt off {feats}: a slashed zero')
        if kept('zero'):
            for text, want in CALT[:4]:
                got, _ = zeros_of(text, dict(feats, zero=1))
                check(got == text.replace('0', 'Ø'), f'calt + zero {feats}: {text!r} -> {got!r}')
    # every figure form counts as a digit: a zero beside a superior, an old-style or a small-cap figure stays plain
    check(zeros_of('0\u00b9', {})[0] == '0\u00b9' and zeros_of('\u20810', {})[0] == '\u20810', 'calt: superior/inferior neighbours')
    # spacing: the slashed zero keeps the plain zero's advance and kerning
    a, b = shape('(0)'), shape('(0)', {'calt': 0})
    check([r['adv'] for r in a] == [r['adv'] for r in b] and [r['x'] for r in a] == [r['x'] for r in b], f'calt: (0) spacing {a} vs {b}')

# ---------------------------------------------------------------- marks
# (text, features, base glyph, kind of each mark). top: above the base's ink, not
# floating, over its ink; bottom: below; over: centred on the base's ink.
TOPM = '\u0300\u0301\u0302\u0303\u0304\u0306\u0307\u0308\u030a\u030c'
MARKS = [('x\u0301', {'smcp': 1}, 'X.sc', 'top'), ('a\u0331', {'ss04': 1}, 'a.ss04', 'bottom'),
         ('Q\u0307', {'ss05': 1}, 'Q.ss05', 'top'), ('t\u0338', {'ss07': 1}, 't.ss07', 'over'),
         ('X\u0301', {'c2sc': 1}, 'X.sc', 'top'), ('x\u0323', {'smcp': 1}, 'X.sc', 'bottom'),
         ('x\u0327', {'smcp': 1}, 'X.sc', 'bottom'), ('x\u0331', {'smcp': 1}, 'X.sc', 'bottom'),
         ('x\u0338', {'smcp': 1}, 'X.sc', 'over'), ('v\u0331', {'smcp': 1}, 'V.sc', 'bottom'),
         ('y\u0301', {'ss06': 1}, None, None), ('y\u0302\u0301', {'ss06': 1}, None, None),
         ('t\u0324', {'ss07': 1}, 't.ss07', 'bottom'), ('t\u0301', {'ss07': 1}, 't.ss07', 'top'),
         ('1\u0304', {}, 'one', 'top'), ('1\u0331', {}, 'one', 'bottom'), ('7\u0338', {}, 'seven', 'over'),
         ('0\u0301', {'onum': 1, 'pnum': 1, 'calt': 0}, 'zero.osf', 'top'), ('0\u0301', {'onum': 1, 'pnum': 1}, f'zero.osf.zero{SUF}', 'top'), ('3\u0323', {'onum': 1}, 'three.osf', 'bottom'),
         ('5\u0302', {'smcp': 1}, 'five.sc', 'top'), ('0\u0301', {'zero': 1}, f'zero.zero{SUF}', 'top'),
         ('2\u0303', {'pnum': 1}, 'two.pnum', 'top')]
MARKS += [('x' + m, {'smcp': 1}, 'X.sc', 'top') for m in TOPM]
MARKS += [('4' + m, {'onum': 1, 'pnum': 1}, 'four.osf', 'top') for m in TOPM]
MARKS += [('8' + m, {}, 'eight', 'top') for m in TOPM]


def placed(base, mark, kind, what):
    b, m = ink(base), ink(mark)
    if not b or not m: return check(False, f'{what}: no ink')
    mx, my = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2
    check(mark['adv'] == 0, f'{what}: mark advance {mark["adv"]}')
    if kind == 'top':
        check(b[3] - 15 <= m[1] <= b[3] + 140, f'{what}: mark bottom {m[1]} vs base top {b[3]}')
        check(b[0] <= mx + 40 and mx - 40 <= b[2], f'{what}: mark middle {mx} off the base {b[0]}..{b[2]}')
    elif kind == 'bottom':
        check(b[1] - 260 <= m[3] <= b[1] + 30, f'{what}: mark top {m[3]} vs base bottom {b[1]}')
        check(b[0] <= mx <= b[2], f'{what}: mark middle {mx} off the base {b[0]}..{b[2]}')
    else:
        check(abs(mx - (b[0] + b[2]) / 2) <= 0.25 * (b[2] - b[0]) + 20 and abs(my - (b[1] + b[3]) / 2) <= 0.25 * (b[3] - b[1]),
              f'{what}: overlay middle ({mx:.0f}, {my:.0f}) off the base middle')


for text, feats, base, kind in MARKS:
    if not kept(*feats): continue
    r = shape(text, feats)
    what = f'mark {text!r} {feats}: {[x["g"] for x in r]}'
    if base is None or (len(r) == 1 and len(text) == 2 and base == 'X.sc'):   # composes (x dot above ...)
        check(len(r) <= 2, what); continue
    check(r[0]['g'] == base, f'{what}: base {r[0]["g"]}, want {base}')
    if len(r) < 2: check(False, f"{what}: composed"); continue
    placed(r[0], r[1], kind, what)
# stacked marks on a small cap: the second above the first
r = shape('x\u0301\u0304', {'smcp': 1})
check(len(r) == 3 and ink(r[2])[1] >= ink(r[1])[3] - 10 and ink(r[1])[1] >= ink(r[0])[3] - 15, f'stack x.sc: {r}')
r = shape('8\u0301\u0304')
check(len(r) == 3 and ink(r[2])[1] >= ink(r[1])[3] - 10, f'stack eight: {r}')
# lining figures take the capitals' .case marks; old-style and small-cap figures keep the lowercase ones
check(names('1\u0301')[1] == 'acutecomb.case' and names('1\u0301', {'onum': 1})[1] == 'acutecomb'
      and names('1\u0301', {'smcp': 1})[1] == 'acutecomb', 'figure marks: case forms')
# a mark after a ligature sits over its last letter
for text, feats, lig in (('ff\u0301', {}, 'f_f'), ('tt\u0324', {}, 't_t'), ('Th\u0301', {'ss01': 1}, 'T_h'), ('ft\u0324', {'ss16': 1}, 'f_t')):
    r = shape(text, feats)
    ok = r[0]['g'] == lig and len(r) == 2
    check(ok, f'ligature {text!r}: {[x["g"] for x in r]}')
    if ok:
        b, m = ink(r[0]), ink(r[1]); mx = (m[0] + m[2]) / 2
        check(mx > (b[0] + b[2]) / 2 and mx < b[2] + 20, f'ligature {lig} mark at {mx}, ink {b[0]}..{b[2]}')
        check(m[1] >= b[3] - 40 if text[-1] in '\u0301' else m[3] <= 15, f'ligature {lig}: mark {m} vs ink {b}')
# canonically equivalent: a precomposed small cap / alternate against base + mark, the
# precomposed one built by build.py from the same mark. The anchors are derived from
# the capitals' and the alternates' own, so the two should agree within a few units.
gp = tt['GPOS'].table


def base_anchor(glyph, cls_mark):
    for lk in gp.LookupList.Lookup:
        if lk.LookupType != 4: continue
        for st in lk.SubTable:
            if glyph in st.BaseCoverage.glyphs and cls_mark in st.MarkCoverage.glyphs:
                mr = st.MarkArray.MarkRecord[st.MarkCoverage.glyphs.index(cls_mark)]
                a = st.BaseArray.BaseRecord[st.BaseCoverage.glyphs.index(glyph)].BaseAnchor[mr.Class]
                if a: return (a.XCoordinate - mr.MarkAnchor.XCoordinate, a.YCoordinate - mr.MarkAnchor.YCoordinate)
    return None


# build.py sets these four from the lowercase composite's mark offsets, not the capital's
FROM_LOWER = {'uni01D4.sc', 'uni01E9.sc', 'uni021F.sc', 'uni1E97.sc'}
gl = tt['glyf']; agree = 0
for pre in [g for g in GO if (g.endswith('.sc') or g.endswith('.ss04') or g.endswith('.ss06') or g.endswith('.ss07'))
            and gl[g].isComposite() and len(gl[g].components) == 2]:
    base, mk = gl[pre].components
    if base.glyphName not in GO or mk.glyphName.endswith('.case'): continue
    if pre in FROM_LOWER or pre.startswith(('uni04', 'uni05')): continue   # Mulish sets its Cyrillic marks a few units off its Latin ones
    a = base_anchor(base.glyphName, mk.glyphName)
    if a is None: continue
    agree += 1
    check(abs(a[0] - mk.x) <= 8 and abs(a[1] - mk.y) <= 8, f'{pre}: {base.glyphName} + {mk.glyphName} at {a}, precomposed at ({mk.x}, {mk.y})')
check(agree >= 150, f'only {agree} precomposed small caps and alternates compared')

# letters Mulish left unanchored (issue 28): a combining acute, dot below or ogonek after
# them is moved by the mark feature (a nonzero offset), its anchor falls within the
# letter's ink from left to right, an above mark sits on the letter's top, a dot below
# under its foot (or its descender), and an ogonek hangs from its foot, joined to it.
NEW_TOP = 'ŋəɓɗħđðßƴǥƒƁƊĦƑƳǤẞ'
NEW_BOT = ('ŋəɓɗħđðßƴǥƒgøƁƊĦƑƳǤẞ' + 'αδεικλνοπστυωθΓΔΛΞΠΣΦΨΩΑΟ'
           + 'ГЖИКМНТУХЧЫгжикхчыэѳҠһәө')
NEW_OGON = 'bcdfhklmnprstvwxzBCDFGHKLMNPRSTVWXZ'
_mk_anchor = {}
for lk in gp.LookupList.Lookup:
    for st in lk.SubTable:
        if lk.LookupType == 9: st = st.ExtSubTable
        if getattr(st, 'LookupType', lk.LookupType) == 4 and hasattr(st, 'MarkCoverage'):
            for g, r in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord): _mk_anchor.setdefault(g, r.MarkAnchor.XCoordinate)
if kept('mark'):
    _cm = tt.getBestCmap()
    for chars, mark, kind in ((NEW_TOP, '́', 'top'), (NEW_BOT, '̣', 'bottom'), (NEW_OGON, '̨', 'ogonek')):
        for ch in chars:
            if ord(ch) not in _cm: continue
            r = shape(ch + mark)
            what = f'letter anchor {ch}{mark} ({kind}): {[x["g"] for x in r]}'
            if len(r) != 2: check(False, f'{what}: composed'); continue
            base, m = r
            check(m['dx'] != 0 or m['y'] != 0, f'{what}: mark not positioned')
            b, mi = ink(base), ink(m)
            ax = m['x'] + _mk_anchor.get(m['g'], 0)
            check(b[0] <= ax <= b[2], f'{what}: mark anchor x {ax} outside the ink {b[0]}..{b[2]}')
            if kind == 'ogonek':
                check(mi[1] < 0 <= mi[3] and b[0] <= (mi[0] + mi[2]) / 2 <= b[2] + 40,
                      f'{what}: ogonek {mi} not hung from the foot of {b}')
                def inside(x, y):
                    pen = PointInsidePen(GS, (x - base['x'], y - base['y'])); GS[base['g']].draw(pen); return pen.getResult()
                check(any(inside(ax, y) for y in (2, 8, 15)), f'{what}: the ogonek\'s anchor ({ax}, 0) is not on the letter\'s foot')
            elif kind == 'top':
                placed(base, m, kind, what)
                check(mi[1] >= b[3] - 5, f'{what}: mark bottom {mi[1]} below the letter top {b[3]}')
            else:                                       # on the baseline, or under a descender
                check(b[1] - 260 <= mi[3] <= -60 and b[0] <= (mi[0] + mi[2]) / 2 <= b[2],
                      f'{what}: dot {mi} not under the letter {b}')
                check(m['adv'] == 0, f'{what}: mark advance {m["adv"]}')

def subset_component_only(font):
    """Conservative glyf-only dependencies, never encoded/layout/caret consumers.

    Unknown glyph-addressing tables and unsupported profiles fail closed: they
    receive no component-class exemption. Class absence is allowed separately,
    only in the explicit normal static subset verification path.
    """
    if 'glyf' not in font or 'fvar' in font:
        return set()
    infrastructure = {'OS/2', 'STAT', 'cmap', 'cvt ', 'fpgm', 'gasp', 'glyf',
                      'head', 'hhea', 'hmtx', 'loca', 'maxp', 'meta', 'name',
                      'post', 'prep', 'DSIG'}
    consumers = {'GSUB', 'GPOS', 'MATH', 'BASE', 'JSTF', 'kern', 'GDEF'}
    if (set(font.keys()) - {'GlyphOrder'}) - infrastructure - consumers:
        return set()
    order = font.getGlyphOrder()
    names = set(order)
    def references(value):
        if isinstance(value, str):
            return {value} if value in names else set()
        result = set()
        if isinstance(value, dict):
            for key, child in value.items():
                result.update(references(key)); result.update(references(child))
        elif isinstance(value, (list, tuple)):
            for child in value:
                result.update(references(child))
        elif hasattr(value, '__dict__'):
            for key, child in vars(value).items():
                if key not in ('reader', 'font') and not key.startswith('_'):
                    result.update(references(child))
        return result
    # Glyph zero is a standalone missing-character fallback even without cmap.
    standalone = {order[0]}
    for table in font['cmap'].tables:
        standalone.update(getattr(table, 'cmap', {}).values())
        standalone.update(references(getattr(table, 'uvsDict', {})))
    for tag in consumers - {'GDEF'}:
        if tag in font:
            standalone.update(references(font[tag]))
    if 'GDEF' in font:
        gd = font['GDEF'].table
        known = {'Version', 'GlyphClassDef', 'AttachList', 'LigCaretList',
                 'MarkAttachClassDef', 'MarkGlyphSetsDef', 'VarStore'}
        if {k for k in vars(gd) if not k.startswith('_')} - known:
            return set()
        # GlyphClassDef itself is classification, not standalone reachability.
        for key in ('AttachList', 'LigCaretList', 'MarkAttachClassDef', 'MarkGlyphSetsDef'):
            standalone.update(references(getattr(gd, key, None)))
    dependencies = set()
    visiting, visited = set(), set()
    def descend(name):
        if name in visiting or name not in names:
            raise ValueError('Invalid composite dependency graph')
        if name in visited:
            return
        visiting.add(name)
        glyph = font['glyf'][name]
        if glyph.isComposite():
            for component in glyph.components:
                dependencies.add(component.glyphName)
                descend(component.glyphName)
        visiting.remove(name); visited.add(name)
    try:
        for name in standalone:
            descend(name)
    except ValueError:
        return set()
    return dependencies - standalone


# ---------------------------------------------------------------- GDEF
gd = tt['GDEF'].table; cd = gd.GlyphClassDef.classDefs
component_only = subset_component_only(tt) if MODE == 'subset' and os.environ.get('TS_WEB_SUBSET') == '1' else set()
def omitted_component_class(g):
    return g in component_only and cd.get(g) is None
carets = {g: [c.Coordinate for c in lg.CaretValue] for g, lg in zip(gd.LigCaretList.Coverage.glyphs, gd.LigCaretList.LigGlyph)}
ligs = {}
for lk in tt['GSUB'].table.LookupList.Lookup:
    for st in lk.SubTable:
        if lk.LookupType == 7: st = st.ExtSubTable
        if getattr(st, 'LookupType', lk.LookupType) == 4 and hasattr(st, 'ligatures'):
            for first, ls in st.ligatures.items():
                for l in ls: ligs.setdefault(l.LigGlyph, []).append([first] + l.Component)
# Classify encoded combining marks from Unicode semantics, not glyph names.
encoded_categories = {}
for table in tt['cmap'].tables:
    if table.isUnicode():
        for cp, g in getattr(table, 'cmap', {}).items():
            encoded_categories.setdefault(g, set()).add(unicodedata.category(chr(cp)))
encoded_marks = {g for g, categories in encoded_categories.items() if categories <= {'Mn', 'Me'}}
# nalt's ⑩-⑳ are ligature outputs but encoded characters of their own: bases, no carets
NALT_OUT = {g for u, g in tt.getBestCmap().items() if 0x2469 <= u <= 0x2473}
def expected_new_class(g):
    return 1 if g in NALT_OUT else 2 if g in ligs else 3 if g in encoded_marks else 1
if MUL is not None:
    new = [g for g in GO if g not in MUL]
    check(len(new) > 500, f'only {len(new)} glyphs beyond Mulish')
    check(all(cd.get(g) == expected_new_class(g) or omitted_component_class(g) for g in new), f'incorrect new glyph classes: {[g for g in new if cd.get(g) != expected_new_class(g) and not omitted_component_class(g)][:10]}')
    for g in new:
        if g in NALT_OUT:
            check(cd.get(g) == 1 and not carets.get(g), f'GDEF {g}: class {cd.get(g)}, carets {carets.get(g)}; nalt\'s circled number is a base')
        elif g in ligs:
            check(cd.get(g) == 2, f'GDEF {g}: class {cd.get(g)}, a ligature')
            c = carets.get(g, [])
            n = len(g.split('.')[0].split('_')) if '_' in g else None
            check(len(c) >= 1 and (n is None or len(c) == n - 1), f'GDEF {g}: carets {c}')
            check(c == sorted(set(c)) and all(0 < x < tt['hmtx'][g][0] for x in c), f'GDEF {g}: carets {c} not increasing inside the advance')
        else:
            check(cd.get(g) == expected_new_class(g) or omitted_component_class(g), f'GDEF {g}: class {cd.get(g)}, expected {expected_new_class(g)}')
if os.environ.get('MULISH_STATIC'):            # Mulish's own carets (fi, fl) as Mulish has them
    _ml = TTFont(os.environ['MULISH_STATIC'])['GDEF'].table.LigCaretList
    for g, lg in zip(_ml.Coverage.glyphs, _ml.LigGlyph):
        if g in GO: check(carets.get(g) == [c.Coordinate for c in lg.CaretValue], f'{g} carets {carets.get(g)} changed')
check(all(cd.get(g) == 3 for g in ('acutecomb', 'uni0338', 'dotbelowcomb')), 'marks lost their class')
unclassed = [g for g in GO if g != '.notdef' and g not in cd and not omitted_component_class(g)]
check(not unclassed, f'GDEF: {len(unclassed)} glyphs without a class: {unclassed[:10]}')
check(all(cd.get(g) == 3 for g in encoded_marks), f'GDEF: combining marks not class 3: {[g for g in encoded_marks if cd.get(g) != 3][:10]}')
_cmap = tt.getBestCmap()
check(all(cd.get(_cmap[ord(c)]) == 1 for c in 'БВДəðŋß ' if ord(c) in _cmap), 'GDEF: Б В Д ə ð ŋ ß space are not bases')
# carets follow the letters: office's ffi has two, between the letters
r = shape('office')
check(r[1]['g'] == 'f_f_i' and len(carets.get('f_f_i', [])) == 2, f'office: {[x["g"] for x in r]}')

# ---------------------------------------------------------------- frac
if kept('frac'):
    F = {'frac': 1}
    def fr(t): return ' '.join(names(t, F))
    for text, want in (('1/2', 'one.numr fraction two.dnom'),
                       ('10/31', 'one.numr zero.numr fraction three.dnom one.dnom'),
                       ('7 1/2', 'seven space one.numr fraction two.dnom'),
                       ('3 3/4', 'three space three.numr fraction four.dnom'),
                       ('1⁄2', 'one.numr fraction two.dnom'),
                       ('7', 'seven'), ('7 and 8', 'seven space a n d space eight'),
                       ('and/or', 'a n d slash o r'), ('x/2', 'x slash two'), ('2/', 'two slash')):
        check(fr(text) == want, f'frac {text!r}: {fr(text)}, expected {want}')
    for text, feats in (('7 1/2', {'onum': 1}), ('7 1/2', {'tnum': 1})):
        g = names(text, dict(F, **feats))
        check(not g[0].endswith(('.numr', '.dnom')) and g[2:] == ['one.numr', 'fraction', 'two.dnom'], f'frac {text!r} {feats}: {g}')

# ---------------------------------------------------------------- dlig
if kept('dlig'):
    check(names('The other', {'dlig': 1})[:3] == ['T_h', 'e', 'space'] and 't_h' in names('The other', {'dlig': 1}),
          f"dlig: The other -> {names('The other', {'dlig': 1})}")
    check(names('The other') == names('The other', {'dlig': 0}) and 'T_h' not in names('The other'), 'dlig: Th without dlig')
    check(names('The other', {'dlig': 1, 'smcp': 1}) == names('The other', {'smcp': 1}), 'dlig: a ligature under smcp')

# ---------------------------------------------------------------- locl
def names_lang(text, lang, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); b.language = lang
    hb.shape(HB, b, feats or {}); return [GO[i.codepoint] for i in b.glyph_infos]
if kept('locl'):
    for lang in ('ro', 'mo'):
        got = names_lang('ŞşŢţ', lang)
        check(got == ['uni0218', 'uni0219', 'uni021A', 'uni021B'], f'locl {lang}: ŞşŢţ -> {got}')
    check(names_lang('ŞşŢţ', 'en') == ['Scedilla', 'scedilla', 'uni0162', 'uni0163'], 'locl en: Ş ş Ţ ţ changed')
    tr = names_lang('fi i', 'tr')
    check('i.loclTRK' in tr, f'locl tr: fi i -> {tr}')
    for lang in ('az', 'crh', 'kk', 'tt'):
        got = names_lang('fi i', lang)
        check(got == tr, f'locl {lang}: fi i -> {got}, Turkish {tr}')
    check('i.loclTRK' not in names_lang('fi i', 'en'), 'locl en: dotted i form outside Turkic')

# ---------------------------------------------------------------- grek
# GSUB and GPOS have a script record for Greek with DFLT's features, and Greek text
# shapes under it as under DFLT (script Zyyy, which HarfBuzz shapes with DFLT).
def langsys(ls):
    return None if ls is None else (ls.ReqFeatureIndex, list(ls.FeatureIndex))
for tag in ('GSUB', 'GPOS'):
    recs = {sr.ScriptTag: sr.Script for sr in tt[tag].table.ScriptList.ScriptRecord}
    check('grek' in recs, f'grek: {tag} has no grek script record ({sorted(recs)})')
    if 'grek' in recs and 'DFLT' in recs:
        g, d = recs['grek'], recs['DFLT']
        check(langsys(g.DefaultLangSys) == langsys(d.DefaultLangSys)
              and [(r.LangSysTag, langsys(r.LangSys)) for r in g.LangSysRecord] == [(r.LangSysTag, langsys(r.LangSys)) for r in d.LangSysRecord],
              f'grek: {tag} grek features differ from DFLT\'s')
GREEK = 'ΑΒΓΔ Σοφία, ΤΑΥ; Ψυχή (ΩΜΕΓΑ) άλφα ΆΈΪ ξ ζ ς μ'


def shape_script(text, script, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); b.script = script
    hb.shape(HB, b, feats or {})
    return [(GO[i.codepoint], p.x_advance, p.x_offset, p.y_offset) for i, p in zip(b.glyph_infos, b.glyph_positions)]


for feats in ({}, {'smcp': 1}, {'c2sc': 1}, {'case': 1}, {'kern': 0}, {'mgrk': 1}):
    if not kept(*feats): continue
    gr = shape_script(GREEK, 'Grek', feats)
    check(gr == shape_script(GREEK, 'Zyyy', feats), f'grek {feats}: Greek shapes otherwise under grek than under DFLT')
for tag, key in (('smcp', 0), ('c2sc', 0), ('kern', 1)):     # the features reach Greek under grek
    if kept(tag):
        check([x[key] for x in shape_script(GREEK, 'Grek', {tag: 1 - key})] != [x[key] for x in shape_script(GREEK, 'Grek', {tag: key})],
              f'grek: {tag} does not change Greek text')

# ---------------------------------------------------------------- mgrk
# Σ Π Δ Ω μ to ∑ ∏ ∆ Ω µ, one single substitution; no other glyph changes.
if kept('mgrk'):
    _cm = tt.getBestCmap()
    MG = [(_cm.get(a), _cm.get(b)) for a, b in ((0x03A3, 0x2211), (0x03A0, 0x220F), (0x0394, 0x2206))]
    gsub = tt['GSUB'].table
    li = sorted({i for fr in gsub.FeatureList.FeatureRecord if fr.FeatureTag == 'mgrk' for i in fr.Feature.LookupListIndex})
    check(len(li) == 1 and gsub.LookupList.Lookup[li[0]].LookupType == 1, f'mgrk: lookups {li}, want one single substitution')

    def gnames(text, script, feats=None): return [x[0] for x in shape_script(text, script, feats)]
    for script in ('Grek', 'Zyyy', 'Latn'):
        on, off = gnames('ΣΠΔ', script, {'mgrk': 1}), gnames('ΣΠΔ', script)
        check(on == [b for _, b in MG], f'mgrk {script}: ΣΠΔ -> {on}, want {[b for _, b in MG]}')
        check(off == [a for a, _ in MG] and off == gnames('ΣΠΔ', script, {'mgrk': 0}), f'mgrk off {script}: ΣΠΔ -> {off}')
    allg = ''.join(chr(u) for u in range(0x0370, 0x0400) if u in _cm)
    a0, a1 = names(allg), names(allg, {'mgrk': 1})
    diff = sorted({(a, b) for a, b in zip(a0, a1) if a != b})
    check(len(a0) == len(a1) and diff == sorted(MG), f'mgrk: the Greek block changes {diff}')

# ---------------------------------------------------------------- nalt
# A whole number from 1 to 20 to its circled form (① to ⑳); 10-20 are one glyph, not
# ①⓪ or ①①; longer numbers and numbers joined by a decimal point stay; off, nothing changes.
if kept('nalt'):
    _cm = tt.getBestCmap()
    C = {n: _cm.get(0x2460 + n - 1) for n in range(1, 21)}
    check(all(C.values()), f'nalt: circled numbers missing from the cmap: {[n for n, g in C.items() if not g]}')
    gsub = tt['GSUB'].table
    check(any(fr.FeatureTag == 'nalt' for fr in gsub.FeatureList.FeatureRecord), 'nalt: no nalt feature')
    want = [C[1], 'space', C[5], 'space', C[10], 'space', C[20]]
    for feats in ({'nalt': 1}, {'nalt': 1, 'onum': 1}, {'nalt': 1, 'pnum': 1, 'zero': 1}, {'nalt': 1, 'smcp': 1}):
        if not kept(*feats): continue
        got = names('1 5 10 20', feats)
        check(got == want, f'nalt {feats}: 1 5 10 20 -> {got}, want {want}')
    got = names(' '.join(str(n) for n in range(1, 21)), {'nalt': 1})
    check(got[::2] == [C[n] for n in range(1, 21)], f'nalt: 1 to 20 -> {got[::2]}')
    check(names('(3) [12]', {'nalt': 1}) == ['parenleft', C[3], 'parenright', 'space', 'bracketleft', C[12], 'bracketright'], 'nalt: (3) [12]')
    for t in ('21', '25', '100', '0', '1.5', '2026', '1,2', '120', '201'):
        check(names(t, {'nalt': 1}) == names(t), f'nalt: {t} -> {names(t, {"nalt": 1})}, want it unchanged')
    for t in ('1 5 10 20', '12 x 7', 'H1 ①'):
        check(names(t) == names(t, {'nalt': 0}) and not any(g in C.values() for g in names(t.replace('①', ''))), f'nalt off: {t} -> {names(t)}')
    r = shape('10', {'nalt': 1})
    check(len(r) == 1 and r[0]['adv'] == tt['hmtx'][C[10]][0], f'nalt: 10 -> {r}')

# ---------------------------------------------------------------- aalt / salt
if kept('aalt', 'salt'):
    gsub = tt['GSUB'].table


    def feat_lookups(tag):
        return sorted({i for fr in gsub.FeatureList.FeatureRecord if fr.FeatureTag == tag for i in fr.Feature.LookupListIndex})


    for tag in ('aalt', 'salt'):
        li = feat_lookups(tag)
        check(len(li) == 1 and gsub.LookupList.Lookup[li[0]].LookupType == 3, f'{tag}: lookups {li}')
    alts = {}
    for i in feat_lookups('aalt'):
        for st in gsub.LookupList.Lookup[i].SubTable:
            for k, v in (getattr(st, 'alternates', None) or {k: [v] for k, v in (getattr(st, 'mapping', None) or {}).items()}).items():
                alts.setdefault(k, []).extend(v)
    for g, must in (('a', ['ordfeminine', 'a.ss04', 'A.sc']), ('Q', ['Q.ss05', 'Q.sc']), ('seven', ['seven.ss08', 'seven.tosf', 'seven.sc', 'uni2077']),
                    ('zero', [f'zero.zero{SUF}', 'zero.tosf', 'zero.sc']), ('parenleft', [f'parenleft.case{SUF}', 'parenleft.sc']),
                    ('hyphen', ['hyphen.case']), ('y', ['y.ss06']), ('t', ['t.ss07']), ('one', ['uni00B9', 'one.pnum'])):
        check(all(m in alts.get(g, []) for m in must), f'aalt {g}: {alts.get(g)}')
    check(not any(x.endswith(('.keep', '.out', '.vec', '.rn')) or x.startswith(('spark', 'pbar')) for v in alts.values() for x in v), 'aalt lists internal glyphs')
    check(names('a', {'aalt': 1}) == ['ordfeminine'], f'aalt=1 a: {names("a", {"aalt": 1})}')   # Mulish's first alternate stays first
    i = alts['a'].index('a.ss04') + 1 if 'a.ss04' in alts.get('a', []) else 1
    check(names('a', {'aalt': i}) == ['a.ss04'], f'aalt={i} a: {names("a", {"aalt": i})}')
    for t in ('aQ7(0)', 'office'):                    # one substitution per glyph, never a chain
        a1 = names(t, {'aalt': 1, 'liga': 0}); base = names(t, {'liga': 0})
        check(all(x == y or x in alts.get(y, []) for x, y in zip(a1, base)), f'aalt chains: {t} -> {a1}')
    s1 = names('a Q y t 7 b H', {'salt': 1})
    check(s1 == ['a.ss04', 'space', 'Q.ss05', 'space', 'y.ss06', 'space', 't.ss07', 'space', 'seven.ss08', 'space', 'b', 'space', 'H'], f'salt: {s1}')
    check(names('a Q y t 7') == ['a', 'space', 'Q', 'space', 'y', 'space', 't', 'space', 'seven'], 'salt or aalt on by default')

# ---------------------------------------------------------------- defaults and line box
cm = tt.getBestCmap()
allc = ''.join(chr(u) for u in sorted(cm) if u > 32)
for feats in ({}, {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}):
    r = shape(allc, feats)                         # (calt's lone zeros are the only ones)
    check(not any(SUF in x['g'] and not x['g'].endswith('.zero' + SUF) for x in r), f'default shaping {feats} uses a module glyph')
    r = shape(allc, dict(feats, calt=0))
    check(not any(SUF in x['g'] for x in r), f'shaping {feats} with calt off uses a module glyph')
# The module's glyphs stay inside hhea, typo and win metrics. Mark stacks on the new
# bases stay inside the win metrics (what Windows clips to) and, for single marks,
# inside hhea/typo; a lining figure's two stacked marks reach as high as the same
# stack on a capital (Mulish's own: H + acute + macron, and its precomposed glyphs).
hh, os2 = tt['hhea'], tt['OS/2']
lo, hi = max(hh.descent, -os2.usWinDescent, os2.sTypoDescender), min(hh.ascent, os2.usWinAscent, os2.sTypoAscender)
wlo, whi = -os2.usWinDescent, os2.usWinAscent
for g in GO:
    if SUF in g:
        b = bounds(g)
        check(b and lo <= b[1] and b[3] <= hi, f'{g}: ink {b} outside the line metrics {lo}..{hi}')
def top_of(text, feats=None): return max(ink(x)[3] for x in shape(text, feats) if ink(x))
for text, feats in (('x\u0301', {'smcp': 1}), ('8\u0301', {}), ('4\u0302', {'onum': 1}), ('1\u0331', {}),
                    ('Q\u0307', {'ss05': 1}), ('ff\u0301', {}), ('(\u00c9)', {'case': 1}), ('x\u0301\u0304', {'smcp': 1})):
    if not kept(*feats): continue
    for x in shape(text, feats):
        b = ink(x)
        check(not b or (lo <= b[1] and b[3] <= hi), f'{text!r} {feats}: {x["g"]} ink {b} outside {lo}..{hi}')
for text, feats in (('8\u0301\u0304', {}), ('4\u0302\u0301', {'onum': 1}), ('a\u0304\u0301', {'ss04': 1})):
    if not kept(*feats): continue
    t = top_of(text, feats)
    check(t <= whi and t <= max(top_of('H\u0301\u0304'), top_of('\u01fa')), f'{text!r} {feats}: top {t} above the capitals\' stacks / win ascent {whi}')

print(f'otfeatures {STYLE} {MODE}: {checks - len(fails)}/{checks} checks passed')
for f in fails[:40]: print('  FAIL', f)
sys.exit(1 if fails else 0)

"""HarfBuzz check of Torchlette Sans's OpenType features.

    python verify.py FONT [ss04 ss05 ss06 ss07]

Shapes a test string under every combination of the features below (and the extra
stylistic sets named on the command line) and checks the glyphs each one selects;
then checks that Mulish's own features (frac, subs, sups, ordn, case, locl) behave
exactly as they do in the unmodified wght-324 instance (build/Mulish-324.ttf, or
MULISH_STATIC). FONT is a .ttf with glyph names. Prints the failure counts.
With TS_WEB_SUBSET=1 (the web subset) the features web_features.txt leaves out are
not checked.
"""
import itertools, os, uharfbuzz as hb
from fontTools.ttLib import TTFont
import sys
from webfeatures import kept
HERE = os.path.dirname(os.path.abspath(__file__))
P = sys.argv[1]
EXTRA = [t for t in sys.argv[2:] if kept(t)]   # extra stylistic sets to include
def mk(path):
    face = hb.Face(hb.Blob.from_file_path(path)); return hb.Font(face)
FT, FM = mk(P), mk(os.environ.get('MULISH_STATIC', os.path.join(HERE, 'build', 'Mulish-324.ttf')))
def shape(font, text, feats, lang=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties()
    if lang: b.language = lang
    hb.shape(font, b, feats)
    return [font.get_glyph_name(i.codepoint) for i in b.glyph_infos]
ALL_F = ['liga', 'ss01', 'ss02', 'ss03', 'onum', 'pnum', 'tnum', 'smcp', 'c2sc', 'ss08']
F = [t for t in ALL_F if kept(t)] + EXTRA
TEXT = 'off offi offl attn The the first x 28x28 -> <= >= ... 1969 7 MNIST Quite by (3/4) & 97.2%! “q” Å ö'
DIG = 'zero one two three four five six seven eight nine'.split()
fails = 0; n = 0
def expect_fig(fd):
    c = ''
    if fd['c2sc'] or fd['smcp']: return '.sc.tf' if fd['tnum'] else '.sc'   # small-cap figures, tabular under tnum
    if fd['onum']: c = '.osf'          # lining -> .tosf (Mulish) -> .osf (ours); .osf stays
    if fd['tnum']: c = {'.osf': '.tosf', '.pnum': ''}.get(c, c)
    if fd['pnum']: c = {'.tosf': '.osf', '': '.pnum'}.get(c, c)
    return c
for bits in itertools.product([0, 1], repeat=len(F)):
    fd = dict(zip(F, bits)); g = shape(FT, TEXT, fd); n += 1
    for t in ALL_F: fd.setdefault(t, 0)   # a feature the subset drops is off
    lc_sc = fd['smcp']; uc_sc = fd['c2sc']
    exp = {
        'liga': fd['liga'] and not lc_sc,                       # small caps come first, so no f ligatures
        'ss01': fd['ss01'] and not lc_sc and not uc_sc,         # Th only when both letters stay as they are
        'ss03': fd['ss03'] and not lc_sc,
        'ss02': fd['ss02'],
    }
    got = {
        'liga': any(x in g for x in ('f_f', 'f_f_i', 'f_f_l', 't_t', 't_t.ss07')),
        'ss01': 'T_h' in g, 'ss03': 't_h' in g or 't_h.ss07' in g,
        'ss02': all(x in g for x in ('arrowright', 'lessequal', 'greaterequal', 'ellipsis')) and ('multiply' in g or 'multiply.sc' in g),
    }
    for k in exp:
        if bool(exp[k]) != got[k]: fails += 1; print('FAIL', k, fd, g)
    # figures
    figs = [x for x in g if x.split('.')[0] in DIG]
    want = expect_fig(fd)
    exp_figs = [x.split('.')[0] + want + ('.ss08' if x.startswith('seven') and fd['ss08'] else '') for x in figs]
    if figs != exp_figs: fails += 1; print('FAIL figs', fd, figs)
    # small caps
    if ('M.sc' in g) != bool(uc_sc): fails += 1; print('FAIL c2sc', fd)
    if ('X.sc' in g) != bool(lc_sc): fails += 1; print('FAIL smcp', fd)   # the lone "x" (the one in 28x28 becomes multiply under ss02)
    if fd['ss02']:
        m = shape(FT, '28x28', fd)
        if m[2] != ('multiply.sc' if (fd['smcp'] or fd['c2sc']) else 'multiply'): fails += 1; print('FAIL 28x28', fd, m)
    if 'c_t' in g: fails += 1
    sc_on = bool(fd['smcp'] or fd['c2sc'])
    if sc_on and fd['tnum']:
        b = hb.Buffer(); b.add_str('1170 9'); b.guess_segment_properties(); hb.shape(FT, b, fd)
        ws = {p.x_advance for i, p in zip(b.glyph_infos, b.glyph_positions) if FT.get_glyph_name(i.codepoint) != 'space'}
        if len(ws) != 1: fails += 1; print('FAIL tnum widths', fd, ws)
    fr = shape(FT, '1/2', dict(fd, frac=1))
    if kept('frac') and fr != ['one.numr', 'fraction', 'two.dnom']: fails += 1; print('FAIL frac', fd, fr)
    for sym in ('parenleft', 'slash', 'ampersand', 'percent', 'exclam', 'quotedblleft'):
        if ((sym + '.sc') in g) != sc_on or (sym in g) == sc_on: fails += 1; print('FAIL sym', sym, fd)
    if ('Aring.sc' in g) != bool(fd['c2sc']) or ('odieresis.sc' in g) or (('Odieresis.sc' in g) != bool(fd['smcp'])):
        fails += 1; print('FAIL accents', fd, [x for x in g if 'ring' in x or 'dieresis' in x])
    if EXTRA:
        for tag, glyph, blocked in (('ss04', 'a.ss04', lc_sc), ('ss05', 'Q.ss05', uc_sc), ('ss06', 'y.ss06', lc_sc)):
            if (glyph in g) != bool(fd[tag] and not blocked): fails += 1; print('FAIL', tag, fd)
        t7 = any(x in g for x in ('t.ss07', 't_t.ss07', 't_h.ss07'))
        if t7 != bool(fd['ss07'] and not lc_sc): fails += 1; print('FAIL ss07', fd)
        if fd['ss07'] and any(x in g for x in ('t', 't_t', 't_h')): fails += 1; print('FAIL ss07 leftovers', fd, g)
    if 'c_t' in shape(FT, 'act predict', fd): fails += 1; print('FAIL c_t')
f = TTFont(P)
print('combos', n, 'fails', fails)
print('c_t in glyph order:', 'c_t' in f.getGlyphOrder(), '| s_t:', 's_t' in f.getGlyphOrder())
tags = [r.FeatureTag for r in f['GSUB'].table.FeatureList.FeatureRecord]
print('dlig present:', 'dlig' in tags, '| FeatureList sorted:', tags == sorted(tags))
print('28x28 onum+ss02:', shape(FT, '28x28', {'onum': 1, 'ss02': 1}))
print('28x28 onum+tnum+ss02:', shape(FT, '28x28', {'onum': 1, 'tnum': 1, 'ss02': 1}))
print('figures pnum:', shape(FT, '1907', {'pnum': 1}), 'tnum:', shape(FT, '1907', {'tnum': 1}), 'onum:', shape(FT, '1907', {'onum': 1}), 'onum+tnum:', shape(FT, '1907', {'onum': 1, 'tnum': 1}))
print('MNIST all-small-caps:', shape(FT, 'MNIST 3', {'smcp': 1, 'c2sc': 1}))
print('office smcp:', shape(FT, 'office', {'smcp': 1}))
# Mulish's own features must behave exactly as before for text without our triggers
tests = [('1/2 3/4', {'frac': 1}), ('2 13 2026', {'subs': 1, 'sups': 1}), ('2 13', {'sups': 1}), ('2 13', {'subs': 1}), ('2 13', {'sinf': 1}), ('No. 1a', {'ordn': 1}),
         ('fi fl', {}), ('İ i', {}), ('ÄÖ', {'case': 1}), ('ijs', {}), ('Ł·L', {})]
for t, fe in tests:
    if not kept(*fe): continue
    for lang in (None, 'tr', 'nl', 'ca'):
        a = shape(FT, t, fe, lang); b = shape(FM, t, fe, lang)
        if a != b: print('DIFF from Mulish', t, fe, lang, a, b); fails += 1
print('Mulish-feature regression fails:', fails)
cm = TTFont(P).getBestCmap()
import unicodedata
for feat, cat in (('smcp', 'Ll'), ('c2sc', 'Lu')):
    miss = [chr(u) for u, n in sorted(cm.items()) if unicodedata.category(chr(u)) in (cat, 'Lt') and shape(FT, chr(u), {feat: 1}) == shape(FT, chr(u), {})]
    print(feat, 'leaves', len(miss), 'letters unmapped:', ' '.join(miss))
if EXTRA:
    for t, fe in [('Ångström, Čapek, Dvořák', {'smcp': 1, 'c2sc': 1}), ('(3/4) 97.2%!', {'smcp': 1}), ('áäâ', {'ss04': 1}), ('ýÿ', {'ss06': 1}), ('ťţ', {'ss07': 1})]:
        print(t, fe, shape(FT, t, fe))
sys.exit(1 if fails else 0)

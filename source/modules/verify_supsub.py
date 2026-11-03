"""HarfBuzz check of the supsub module: superscript and subscript letters and signs.

    verify_supsub.py FONT STYLE full|subset

1. Encoded forms: every promised code point maps to its glyph and shapes to it (not
   .notdef), in the full font and in the web subset (the subset only keeps them when
   the Makefile's UNICODES covers U+1D2C-1D6A, U+1D9C-1DBF and U+2C7C-2C7D).
2. sups, subs, sinf: a-z, the capitals with a superscript form, + - U+2212 = ( )
   and the figures go to the right forms; Mulish's fi and fl split back into two
   letters; letters stay out of liga, ss01, ss02, ss16 under the features; the app's
   own settings (ss01 ss02 ss16 onum pnum) are unchanged outside them.
3. Negative cases: no feature, no change; capitals without a superscript form and
   all capitals under subs stay; small caps win over sups; subs wins over sups.
4. Geometry: superiors stand on the superior figures' baseline and inferiors on the
   inferior figures' (below the baseline: build.py's SUB_DROP), the lowercase reaches
   0.6 of the x-height, the stems match the superior 1's within 3 units, and no new
   glyph leaves the win vertical metrics (clipping) or, measured from its own
   baseline, reaches beyond the font's own tallest and deepest letters. Superiors also
   stay inside the hhea and typo metrics (the line box); inferiors with descenders
   hang below it unless meta.py's INFERIOR_DESCENT is on, and then they must not.

With TS_WEB_SUBSET=1 the features web_features.txt leaves out (sups, subs, sinf in
the web subset) are not checked; the glyphs and code points still are.
"""
import os, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
import pathops
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept   # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
# meta.py's INFERIOR_DESCENT (the line box grows to hold the lowered inferiors), read from
# the module so this check follows the switch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
INFERIOR_DESCENT = getattr(__import__('meta'), 'INFERIOR_DESCENT', None) is not None
f = TTFont(PATH); gs = f.getGlyphSet(); cmap = f.getBestCmap(); order = set(f.getGlyphOrder())
face = hb.Face(hb.Blob.from_file_path(PATH)); font = hb.Font(face)
fails = 0; checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('FAIL', *msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(font, b, feats or {})
    return [font.get_glyph_name(i.codepoint) for i in b.glyph_infos]


SUP_LC = dict(zip('abcdefghijklmnopqrstuvwxyz', 'ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖ?ʳˢᵗᵘᵛʷˣʸᶻ'))
SUP_UC = dict(zip('ABDEGHIJKLMNOPRTUVW', 'ᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ'))
SUB_LC = dict(zip('abcdefghijklmnopqrstuvwxyz', 'ₐ???ₑ??ₕᵢⱼₖₗₘₙₒₚ?ᵣₛₜᵤᵥ?ₓ??'))
SIGNS = {'+': ('⁺', '₊'), '-': ('⁻', '₋'), '−': ('⁻', '₋'), '=': ('⁼', '₌'), '(': ('⁽', '₍'), ')': ('⁾', '₎')}
FIGS = '0123456789'
SUP_FIG, SUB_FIG = '⁰¹²³⁴⁵⁶⁷⁸⁹', '₀₁₂₃₄₅₆₇₈₉'
uname = lambda ch: f'uni{ord(ch):04X}'

# 1. encoded forms
encoded = [c for c in SUP_LC.values() if c != '?'] + list(SUP_UC.values()) + [c for c in SUB_LC.values() if c != '?'] \
    + ['ₔ'] + [s for p in SIGNS.values() for s in p]
encoded = sorted(set(encoded))
for ch in encoded:
    g = cmap.get(ord(ch))
    check(g == uname(ch), f'cmap U+{ord(ch):04X} {ch}: {g}')
    check(shape(ch) == [uname(ch)], f'shape {ch}: {shape(ch)}')
for ch in SUP_FIG + SUB_FIG:
    check(cmap.get(ord(ch)) not in (None, '.notdef'), f'figure {ch} missing')
print(f'encoded: {len(encoded)} code points checked')


def sup_glyph(c):
    if c in SUP_LC: return 'q.sups.supsub' if SUP_LC[c] == '?' else uname(SUP_LC[c])
    if c in SUP_UC: return uname(SUP_UC[c])
    if c in SIGNS: return uname(SIGNS[c][0])
    if c in FIGS: return cmap[ord(SUP_FIG[int(c)])]
    return None


def sub_glyph(c):
    if c in SUB_LC: return f'{c}.subs.supsub' if SUB_LC[c] == '?' else uname(SUB_LC[c])
    if c in SIGNS: return uname(SIGNS[c][1])
    if c in FIGS: return cmap[ord(SUB_FIG[int(c)])]
    return None


# 2. the features
LC, UC = 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
for base_feats in ({}, APP):
    for tag, fn in (('sups', sup_glyph), ('subs', sub_glyph), ('sinf', sub_glyph)):
        if not kept(tag): continue
        for text in (LC, '+-−=()', FIGS, 'the office fifty flow attn -> x2', UC):
            got = shape(text, dict(base_feats, **{tag: 1}))
            plain = shape(text, base_feats)
            want = [fn(c) or p for c, p in zip(text, plain)] if len(plain) == len(text) else None
            if want is None:      # the plain run ligates: compare letter by letter instead
                want = [fn(c) or shape(c, base_feats)[0] for c in text]
            check(got == want, tag, base_feats, repr(text), got, want)
# Mulish's fi / fl (on by default) split back into two forms
for tag, fn in (('sups', sup_glyph), ('subs', sub_glyph), ('sinf', sub_glyph)):
    if not kept(tag): continue
    for t in ('fi', 'fl', 'ﬁ', 'ﬂ'):
        exp = [fn(c) for c in ('fi' if t in 'fiﬁ' else 'fl')]
        check(shape(t, {tag: 1}) == exp, tag, t, shape(t, {tag: 1}))
# the lesson examples, as features
if kept('sups'):
    ex = shape('x', {}) + shape('-1', {'sups': 1})
    check(ex == ['x', 'uni207B', 'uni00B9'], 'x^-1', ex)
    check(shape('T', {'sups': 1}) == ['uni1D40'], 'W^T', shape('T', {'sups': 1}))
if kept('subs'):
    check(shape('(ij)', {'subs': 1}) == ['uni208D', 'uni1D62', 'uni2C7C', 'uni208E'], 'x_(ij)', shape('(ij)', {'subs': 1}))
on = [t for t in ('sups', 'subs', 'sinf') if kept(t)]
print(f'features: {" ".join(on)} checked, plain and with ss01 ss02 ss16 onum pnum' if on else
      'features: sups, subs and sinf are not in the web subset; not checked')

# 3. negative cases
ours = {g for g in order if g.endswith('.supsub')} | {uname(c) for c in encoded}
for feats in ({}, APP, {'liga': 1, 'ss03': 1, 'ss08': 1}, {'smcp': 1}, {'c2sc': 1}):
    for text in (LC, UC, '+-=() 0123456789 the office -> x2 1st', 'Hamburgefontsiv'):
        got = shape(text, feats)
        check(not (set(got) & ours), 'stray form without sups/subs', feats, text, got)
for c in 'CFQSXYZ' if kept('sups') else '':
    check(shape(c, {'sups': 1}) == shape(c), 'capital without a superscript form changed', c, shape(c, {'sups': 1}))
for c in UC if kept('subs', 'sinf') else '':
    check(shape(c, {'subs': 1}) == shape(c) and shape(c, {'sinf': 1}) == shape(c), 'capital changed under subs', c)
if kept('smcp', 'sups'):
    sc = shape('ab', {'smcp': 1, 'sups': 1})
    check(sc == shape('ab', {'smcp': 1}), 'smcp should win over sups', sc)
if kept('subs', 'sups'):
    both = shape('ax2', {'subs': 1, 'sups': 1})
    check(both == ['uni2090', 'uni2093', cmap[ord('₂')]], 'subs should win over sups', both)
print('negative cases checked')

# 4. geometry and vertical clipping
def bounds(n):
    p = BoundsPen(gs); gs[n].draw(p); return p.bounds
def stem(n, y):
    p = pathops.Path(); gs[n].draw(p.getPen(glyphSet=gs))
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((-3000, y - .5)); pen.lineTo((5000, y - .5)); pen.lineTo((5000, y + .5)); pen.lineTo((-3000, y + .5)); pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION)
    s = sorted((c.bounds[0], c.bounds[2]) for c in q.contours)
    return s[0][1] - s[0][0]
sup_base = bounds('uni00B9')[1]; sub_base = bounds(cmap[ord('₁')])[1]
fig_stem = stem('uni00B9', sup_base + 218)
os2, hhea = f['OS/2'], f['hhea']
top_lim = min(hhea.ascent, os2.sTypoAscender, os2.usWinAscent)
bot_lim = max(hhea.descent, os2.sTypoDescender, -os2.usWinDescent)
# Round 15: the inferiors hang SUB_DROP below the baseline, so one with a descender
# (ⱼ ₚ, the g q y forms, ₍ ₎) goes deeper than the font's descent unless the line box
# grows (meta.py's INFERIOR_DESCENT). The win descent (clipping) binds them either way.
win_bot = -os2.usWinDescent
let_top = max(bounds(g)[3] for g in 'bdfhklt' + 'ABHT')
let_bot = min(bounds(g)[1] for g in 'gjpqy')
xh = round(0.6 * bounds('x')[3])
inferiors = {sub_glyph(c) for c in LC + ''.join(SIGNS)} | {uname(c) for c in 'ₔ'}
ext = [1e9, -1e9]
for n in sorted(ours):
    b = bounds(n)
    if b is None: check(False, 'empty glyph', n); continue
    ext = [min(ext[0], b[1]), max(ext[1], b[3])]
    base = sub_base if n in inferiors else 0
    lo = win_bot if n in inferiors and not INFERIOR_DESCENT else bot_lim
    check(b[3] <= top_lim and b[1] >= lo, 'outside the vertical metrics', n, b, (lo, top_lim))
    check(b[3] - base <= let_top and b[1] - base >= let_bot, 'beyond the full-size letters', n, b, base, (let_bot, let_top))
    check(f['hmtx'][n][0] > 0, 'zero advance', n)
for c in LC + 'ABDHOTW':
    sb = bounds(c)
    for g, base in ((sup_glyph(c), sup_base), (sub_glyph(c), sub_base)):
        if g is None or (g not in order and not kept('sups', 'subs', 'sinf')): continue   # an unencoded form the subset drops
        b = bounds(g)        # top and bottom at 0.6 of the full-size letter's, on the figures' baseline
        check(abs(b[1] - base - 0.6 * sb[1]) <= 3 and abs(b[3] - base - 0.6 * sb[3]) <= 3,
              'vertical position', c, g, (b[1] - base, b[3] - base), (0.6 * sb[1], 0.6 * sb[3]))
for c in 'nhlmu':
    for g, base in ((sup_glyph(c), sup_base), (sub_glyph(c), sub_base)):
        if g not in order and not kept('sups', 'subs', 'sinf'): continue
        s = stem(g, base + 100)
        check(abs(s - fig_stem) <= 3, 'stem', g, round(s, 1), round(fig_stem, 1))
for c in 'HT':
    b = bounds(sup_glyph(c)); fb = bounds('uni00B9')
    check(abs(b[3] - fb[3]) <= 2 and abs(b[1] - fb[1]) <= 1, 'cap height', c, b, fb)
print(f'geometry: superiors on {sup_base}, inferiors on {sub_base}, x-height {xh}, figure stem {fig_stem:.1f}; '
      f'new ink {ext[0]:.0f}..{ext[1]:.0f} within letters {let_bot:.0f}..{let_top:.0f} and metrics {bot_lim}..{top_lim}')
print(f'supsub {STYLE} {MODE}: {checks} checks, {fails} fails')
sys.exit(1 if fails else 0)

"""Check the kern module by shaping with HarfBuzz.

    verify_kern.py <font.ttf> <style> full|subset

1. Every pair of build.py's small-cap kerning (the SC_KERN lookup's records) shapes to
   its written value; with the module's unmasking lookup taken out of `kern`, more
   than 2,000 of them shape to something else (the masking the module fixes).
2. Tabular figures: no pair with a tabular figure (default figures, .tosf, .sc.tf,
   their ss08 sevens) moves, against any glyph the kerning touches; tnum text keeps
   every figure at its advance and every column the same width.
3. Ligatures and new glyphs kern like their outer letters in real text with the app's
   features (ss01 ss02 ss16 onum pnum): "Tft" as T f, "(The" as ( T, "fy." as y . ...
   and the word marks add nothing on their built-in side.
4. Proportional figures are kerned (7. 1' '4 under onum pnum, under pnum, under smcp),
   tabular ones in the same text are not.

Pair checks shape glyph pairs directly: a copy of the font, without GSUB, maps a
private-use code point to every glyph, so HarfBuzz applies GPOS exactly as it
would to those glyphs in text.
"""
import io
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont

path, style, mode = sys.argv[1], sys.argv[2], sys.argv[3]
APP = {'ss01': True, 'ss02': True, 'ss16': True, 'onum': True, 'pnum': True}
DIG = 'zero one two three four five six seven eight nine'.split()
TABULAR = (DIG + [d + '.tosf' for d in DIG] + [d + '.sc.tf' for d in DIG]
           + ['seven.ss08', 'seven.tosf.ss08', 'seven.sc.tf.ss08'])
fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


tt = TTFont(path)
order = tt.getGlyphOrder(); have = set(order); hm = tt['hmtx']
gpos = tt['GPOS'].table


def xa(v): return (getattr(v, 'XAdvance', 0) or 0) if v else 0


def subtables(lk): return [s.ExtSubTable if lk.LookupType == 9 else s for s in lk.SubTable]


def nominal(lk):
    out = {}
    for st in subtables(lk):
        if st.Format == 1:
            for a, ps in zip(st.Coverage.glyphs, st.PairSet):
                for r in ps.PairValueRecord: out.setdefault((a, r.SecondGlyph), xa(r.Value1))
        else:
            c2 = {}
            for g, c in st.ClassDef2.classDefs.items():
                if c: c2.setdefault(c, []).append(g)
            for a in st.Coverage.glyphs:
                rec = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)]
                for c, gs in c2.items():
                    for b in gs: out.setdefault((a, b), xa(rec.Class2Record[c].Value1))
    return {k: v for k, v in out.items() if v}


kern_idx = sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex})
nom = {i: nominal(gpos.LookupList.Lookup[i]) for i in kern_idx}
sc_i = max((i for i in kern_idx if nom[i]), key=lambda i: sum(a.endswith('.sc') for a, _ in nom[i]))
sc_nom = nom[sc_i]
unmask_i = [i for i in kern_idx if i != sc_i and nom[i] and set(nom[i]) <= set(sc_nom)]
ok(len(unmask_i) == 1, f'unmasking lookup not found ({unmask_i})')


def pua_face(drop_lookups=()):
    """The font without GSUB, every glyph on a private-use code point; optionally with
    some lookups dropped from kern."""
    f = TTFont(path)
    del f['GSUB']
    for t in f['cmap'].tables:
        if t.isUnicode():
            for j, g in enumerate(order): t.cmap[0xE000 + j] = g
    if drop_lookups:
        for fr in f['GPOS'].table.FeatureList.FeatureRecord:
            if fr.FeatureTag == 'kern':
                fr.Feature.LookupListIndex = [i for i in fr.Feature.LookupListIndex if i not in drop_lookups]
                fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    b = io.BytesIO(); f.save(b)
    return hb.Font(hb.Face(b.getvalue()))


GID = {g: j for j, g in enumerate(order)}


def pair_kern(font, a, b):
    buf = hb.Buffer(); buf.add_codepoints([0xE000 + GID[a], 0xE000 + GID[b]]); buf.guess_segment_properties()
    hb.shape(font, buf, {})
    return buf.glyph_positions[0].x_advance - hm[a][0]


pua = pua_face()

# 1. small-cap kerning applies as written
bad = [(a, b, v, pair_kern(pua, a, b)) for (a, b), v in sc_nom.items() if pair_kern(pua, a, b) != v]
ok(not bad, f'{len(bad)} small-cap pairs do not shape to their value, e.g. {bad[:4]}')
if unmask_i:
    pua0 = pua_face(drop_lookups=unmask_i)
    hidden = sum(pair_kern(pua0, a, b) != v for (a, b), v in sc_nom.items())
    ok(hidden > 2000, f'without the unmasking lookup only {hidden} small-cap pairs change (expected > 2000)')
    print(f'small-cap pairs: {len(sc_nom)} shape as written; {hidden} of them need the unmasking lookup')
for t, a, b in (('dt', 'D.sc', 'T.sc'), ('ov', 'O.sc', 'V.sc'), ('dj', 'D.sc', 'J.sc')):
    ok(pair_kern(pua, a, b) == sc_nom.get((a, b)) and sc_nom.get((a, b), 0) < 0, f'{a} {b}: {pair_kern(pua, a, b)} vs {sc_nom.get((a, b))}')

# 2. tabular figures are never kerned
touched = sorted({g for i in kern_idx for k in nom[i] for g in k} | set(order[:0]))
tabs = [t for t in TABULAR if t in have]
moved = [(t, g) for t in tabs for g in touched if pair_kern(pua, t, g) or pair_kern(pua, g, t)]
ok(not moved, f'tabular figure pairs kerned: {moved[:6]}')
print(f'tabular: {len(tabs)} figures x {len(touched)} kerned glyphs, both orders: {len(moved)} pairs move')

blob = hb.Blob.from_file_path(path); real = hb.Font(hb.Face(blob))


def shape(text, feats):
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(real, buf, feats)
    return [(order[i.codepoint], p.x_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


for feats in ({'tnum': True}, {'onum': True, 'tnum': True}, dict(APP, tnum=True, pnum=False), {'smcp': True, 'tnum': True}):
    run = shape("(1.7)/4,7' 11-74% 7. 1’ ‘4 7: [71]", feats)
    figs = [(n, a) for n, a in run if n in TABULAR]
    ok(figs and all(a == hm[n][0] for n, a in figs), f'tnum {feats}: figure advance changed {figs}')
    nb = [(run[i - 1][0], run[i - 1][1]) for i in range(1, len(run)) if run[i][0] in TABULAR]
    ok(all(a == hm[n][0] for n, a in nb), f'tnum {feats}: glyph before a figure kerned {nb}')
    widths = {sum(a for _, a in shape(s, feats)) for s in ('1111.11', '7777.77', '4444.44', '1471.07')}
    ok(len(widths) == 1, f'tnum {feats}: columns differ {widths}')

# 3. ligatures kern like their letters (real text, app features)


def boundary(text, a, b, feats=APP):
    run = shape(text, feats)
    for i in range(len(run) - 1):
        if run[i][0] == a and run[i + 1][0] == b: return run[i][1] - hm[a][0]
    return None


SAME = [  # text, glyphs formed, the letters whose pair kerning it must equal
    ('Tft', ('T', 'f_t'), ('T', 'f')), ('Yff', ('Y', 'f_f'), ('Y', 'f')), ('(The', ('parenleft', 'T_h'), ('parenleft', 'T')),
    ('“The', ('quotedblleft', 'T_h'), ('quotedblleft', 'T')), ('fy.', ('f_y', 'period'), ('y', 'period')),
    ('tw.', ('t_w', 'period'), ('w', 'period')), ('Tfu', ('T', 'f_u'), ('T', 'f')),
    ('network,', ('n_e_t_w_o_r_k.ss11', 'comma'), ('k', 'comma')), ('(Torchlette)', ('parenleft', 'T_o_r_c_h_l_e_t_t_e.ss11'), ('parenleft', 'T')),
    ('Tá', ('T', 'aacute'), ('T', 'a')), ('Vå', ('V', 'aring'), ('V', 'a')), ('Wä', ('W', 'adieresis'), ('W', 'a')),
]
for text, (a, b), (x, y) in SAME:
    if not {a, b, x, y} <= have: continue
    got, want = boundary(text, a, b), pair_kern(pua, x, y)
    ok(got is not None, f'{text!r}: {a} {b} not formed')
    ok(got == want and want != 0, f'{text!r}: {a} {b} kern {got}, letters {x} {y} {want}')
BUILT_IN = [('vector', 'v.vec', 'e'), ('residual', 'i', 'd_u_a_l.arch'), ('length', 'n', 'g_t.w200'), ('length', 'g_t.w200', 'h'),
            ('backward', 'b.backc', 'a'), ('forward', 'r', 'd.fwdb'), ('output', 'u', 't.out'), ('outputs', 'u', 't_s.out')]
for text, a, b in BUILT_IN:
    got = boundary(text, a, b)
    ok(got == 0, f'{text!r}: built-in side {a} {b} kerned {got}')
EDGE = [('gradient.', 'g_r_a_d_i_e_n_t.ss11', 'period'), ('gradients,', 'g_r_a_d_i_e_n_t_s.ss11', 'comma'),
        ('output.', 't.out', 'period'), ('forward.', 'd.fwdb', 'period')]
for text, a, b in EDGE:
    got = boundary(text, a, b)
    ok(got is not None and -60 <= got < 0, f'{text!r}: arrow end {a} {b} kern {got} (expected -60..-1)')

# 4. proportional figures are kerned; the same text in tabular figures is not
FIG = [("7.", APP, 'seven.osf', 'period'), ("7,", APP, 'seven.osf', 'comma'), ("7,", {'pnum': True}, 'seven.pnum', 'comma'), ("1’", APP, 'one.osf', 'quoteright'),
       ("‘4", APP, 'quoteleft', 'four.osf'), ("7.", {'pnum': True}, 'seven.pnum', 'period'),
       ("‘4", {'pnum': True}, 'quoteleft', 'four.pnum'), ("1997.", {'smcp': True, 'pnum': True}, 'seven.sc', 'period')]
for text, feats, a, b in FIG:
    got = boundary(text, a, b, feats)
    # the old-style 7 is short; in Bold its gap to the period stays under the module's 10-unit floor
    # and in Black the open-top 4's model value after the heavier quote (-25 Regular, -15 Bold and
    # ExtraBold) falls under it too
    weight = style.replace('Italic', '') or 'Regular'       # the italics share their weight's exceptions
    lim = 0 if (a == 'seven.osf' and weight in ('Bold', 'ExtraBold', 'Black')) or \
        (a, b, weight) == ('quoteleft', 'four.pnum', 'Black') else -1
    ok(got is not None and got <= lim, f'{text!r} {feats}: {a} {b} kern {got} (expected <= {lim})')
    tf = dict(feats, tnum=True); tf.pop('pnum', None)
    run = shape(text, tf)
    ok(all(adv == hm[n][0] for n, adv in run), f'{text!r} tnum: kerned {run}')

# 5. with the symbols and supsub modules built in: relations and arrows, superiors
cmap = tt.getBestCmap()
if 0x2192 in cmap and 'T' in have:
    got = boundary('T→', 'T', cmap[0x2192], {})
    ok(got is not None and got < 0, f'T + arrow: {got} (expected < 0)')
    got = boundary('x=7', 'equal', 'seven', {})
    ok(got == 0, f'x=7 in tabular figures: = 7 kerned {got}')
for t, (a, b), (x, y) in (('ᵀʸ', (0x1D40, 0x02B8), ('T', 'y')), ('⁽ʲ', (0x207D, 0x02B2), ('parenleft', 'j'))):
    if a in cmap and b in cmap:
        got, want = boundary(t, cmap[a], cmap[b], {}), pair_kern(pua, x, y)
        ok(got is not None and want and abs(got - 0.6 * want) <= 1, f'{t!r}: superiors kern {got}, letters {want}')

print(f'kern ({style}, {mode}): {checks} checks, {len(fails)} failures')
for f in fails: print('  FAIL', f)
sys.exit(1 if fails else 0)

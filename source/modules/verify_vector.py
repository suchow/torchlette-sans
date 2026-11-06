"""Check the vector module by reading GSUB and shaping with HarfBuzz.

    verify_vector.py <font.ttf> <style> full|subset

1. Every form exists in this style: the words v_e_c_t_o_r.vNN and v_e_c_t_o_r_s.vNN and the
   placeholders v.vec.vNN, for the ten ids; the words are GDEF ligatures, the placeholders bases.
2. The rand feature lists them: one alternate rule, v.vec from [v.vec v.vec.v01 ... v.vec.v25]
   (the default first, then the ids in order), and a ligature rule for each placeholder with
   e c t o r and e c t o r s. No other feature outputs them.
3. Shaping with the app's features (ss01 ss02 ss16 onum pnum): "rand" N selects form N in
   "vector", "vectors" and in context (1 the default v.vec e c t o r); the advance before the
   word ("(" before v) is within 40 units of the default's for every form: each kerns like the
   v on the left, corrected where its arrow changes that edge.
4. The ss16 word guards hold for every form: Vector, VECTOR, vectorize, eigenvector(s),
   vectorss, vector2, vec get none of them; with ss16 off, "vector" is plain letters.
5. With rand at its default (as browsers apply it), forty "vector"s take a mix of forms, the
   default among them.
6. Each word has the contours of its letters (vector 8, vectors 9; v06 one more, its free
   arrow): the arrow grows out of a letter and touches no other.
"""
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont

path, style, mode = sys.argv[1], sys.argv[2], sys.argv[3]
IDS = ('v01', 'v02', 'v06', 'v13', 'v15', 'v16', 'v18', 'v20', 'v23', 'v25')
APP = {'ss01': True, 'ss02': True, 'ss16': True, 'onum': True, 'pnum': True}
DEFAULT = 'v.vec'
def word(i, plural): return f"v_e_c_t_o_r{'_s' if plural else ''}.{i}"
def marker(i): return f'{DEFAULT}.{i}'
MINE = {word(i, p) for i in IDS for p in (False, True)} | {marker(i) for i in IDS}

fails, checks = [], 0
def ok(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)

tt = TTFont(path); order = tt.getGlyphOrder(); have = set(order)
font = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
def shape(text, feats):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(font, b, feats)
    return [order[i.codepoint] for i in b.glyph_infos], [p.x_advance for p in b.glyph_positions]

# 1. the glyphs
missing = sorted(MINE - have)
ok(not missing, f'missing glyphs: {missing}')
cls = tt['GDEF'].table.GlyphClassDef.classDefs
for g in sorted(MINE & have):
    want = 1 if g.startswith(DEFAULT + '.') else 2
    ok(cls.get(g) == want, f'{g}: GDEF class {cls.get(g)}, not {want}')

# 2. the rand lookups, and no other feature reaching the forms
gsub = tt['GSUB'].table; lookups = gsub.LookupList.Lookup
def subtables(i):
    lk = lookups[i]
    for st in lk.SubTable:
        yield (st.ExtSubTable.LookupType, st.ExtSubTable) if lk.LookupType == 7 else (lk.LookupType, st)
def outputs(i):
    out = set()
    for t, st in subtables(i):
        if t == 1: out |= set(st.mapping.values())
        elif t == 2: out |= {g for seq in st.mapping.values() for g in seq}
        elif t == 3: out |= {g for alts in st.alternates.values() for g in alts}
        elif t == 4: out |= {l.LigGlyph for ls in st.ligatures.values() for l in ls}
    return out
rand = sorted({i for r in gsub.FeatureList.FeatureRecord if r.FeatureTag == 'rand' for i in r.Feature.LookupListIndex})
ok(bool(rand), 'no rand feature')
alts, ligs = {}, {}
for i in rand:
    for t, st in subtables(i):
        if t == 3: alts.update(st.alternates)
        elif t == 4:
            for first, ls in st.ligatures.items():
                for l in ls: ligs[(first,) + tuple(l.Component)] = l.LigGlyph
ok(alts == {DEFAULT: [DEFAULT] + [marker(i) for i in IDS]}, f'rand alternates {alts}')
want_ligs = {(marker(i),) + tuple('ector') + (('s',) if p else ()): word(i, p) for i in IDS for p in (False, True)}
ok(ligs == want_ligs, f'rand ligatures differ: {sorted(set(ligs.items()) ^ set(want_ligs.items()))[:6]}')
for r in gsub.FeatureList.FeatureRecord:
    if r.FeatureTag == 'rand': continue
    leak = set().union(*[outputs(i) for i in r.Feature.LookupListIndex]) & MINE
    ok(not leak, f'{r.FeatureTag} outputs {sorted(leak)}')

# 3. each form on request
for n, form in enumerate(('default',) + IDS, 1):
    feats = dict(APP, rand=n)
    for text, pre, plural in (('vector', [], False), ('vectors', [], True), ('a vector of', ['a', 'space'], False),
                              ('(vectors)', ['parenleft'], True), ('the vector.', ['t', 'h', 'e', 'space'], False)):
        got = shape(text, feats)[0]
        mid = [DEFAULT] + list('ectors' if plural else 'ector') if n == 1 else [word(form, plural)]
        ok(got[:len(pre) + len(mid)] == pre + mid, f'{text!r} with rand {n}: {got}')
    # every form kerns like the v on its left, plus the kern module's edge correction where an
    # arrow changes that edge (v02's overhangs it; a heavy v06's rides beside the paren's top)
    adv, base = shape('(vector', feats)[1][0], shape('(vector', dict(APP, rand=1))[1][0]
    ok(abs(adv - base) <= 40, f'rand {n}: "(" before {form} advances {adv}, the default {base}')

# 4. the word guards, for every form and at random
for text in ('Vector', 'VECTOR', 'vectorize', 'vectorized', 'eigenvector', 'eigenvectors', 'vectorss', 'vector2', 'vec'):
    for n in [None] + list(range(1, 12)):
        feats = APP if n is None else dict(APP, rand=n)
        got = set(shape(text, feats)[0])
        ok(not got & (MINE | {DEFAULT}), f'{text!r} rand {n}: {sorted(got)}')
ok(shape('vector', {'ss01': True})[0] == list('vector'), f'ss16 off: {shape("vector", {"ss01": True})[0]}')

# 5. at random
got = shape(' '.join(['vector'] * 40), APP)[0]
forms = [g for g in got if g == DEFAULT or g in MINE]
kinds = {g.split('.')[-1] if g != DEFAULT else 'default' for g in forms}
ok(len(forms) == 40 and len(kinds) >= 6 and 'default' in kinds, f'forty vectors at random: {len(forms)} marks, forms {sorted(kinds)}')

# 6. contours
gl = tt['glyf']
for i in IDS:
    for p in (False, True):
        g = word(i, p)
        if g in have:
            n = gl[g].numberOfContours
            want = (9 if p else 8) + (1 if i == 'v06' else 0)       # v06's arrow rides free above the v
            ok(n == want, f'{g}: {n} contours, not {want} (an arrow touches a letter?)')

print(f'vector {style} ({mode}): {checks} checks, {len(fails)} failures; forty at random took {sorted(kinds)}')
for f in fails: print('FAIL', f)
sys.exit(1 if fails else 0)

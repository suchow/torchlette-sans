"""kern: kerning for the glyphs Mulish's and build.py's kerning leave out, and the
small-cap pairs an earlier subtable hides.

What it adds (all GPOS, feature `kern`, no new glyphs, outlines, advances or tags):

1. KERN_SC_UNMASK. build.py's SC_KERN lookup is one feature-file lookup whose class
   pairs feaLib splits into several format-2 subtables. A format-2 subtable that
   covers the left glyph applies even when it has no value for the right one, so
   2,244 pairs per style (O.sc, D.sc, Oslash.sc ... before T.sc, V.sc, J.sc, the
   quotes, period ...) came out 0. This module rebuilds SC_KERN's rules exactly as
   build.py writes them, compiles them the way build.py does to see which pairs the
   split hides, and adds those pairs (intended value minus what applies) in a lookup
   of its own. post() checks the result against the compiled font and stops the
   build if any pair is still hidden (so a change to SC_KERN in build.py cannot
   silently undo this).

2. KERN_NEW_L / KERN_NEW_R. Glyphs with no kerning of their own (the liga and ss16
   ligatures and logotypes, the ss04-ss07 alternates, a few small caps and Mulish's
   own unkerned accented a's) kern like the letter their outer side shows: the
   left side like the first letter, the right side like the last (INHERIT below).
   The value is that letter's kerning (Mulish's, or the small caps' intended one),
   plus a correction, measured on the outlines, where the glyph's edge differs from
   the letter's (the arrow of "gradient", the curl of "backward", the two-storey
   a); corrections under MIN_K units are dropped. A side built into the glyph (the
   word marks carry the kerning of their known neighbour) gets no pairs.

3. KERN_FIG. The proportional figures (lining .pnum, old-style .osf, small-cap .sc)
   kerned with one another and with the punctuation that meets figures (period,
   comma, colon, parentheses, brackets, quotes, slash, percent, hyphen, en dash, and
   ss16's range dash, ratio colons and old-style percent). Mulish kerns no figures,
   so these values come from the optical model only (see `_model`), calibrated on
   Mulish's own capital-punctuation kerning (r about 0.89) and applied at a lower
   gain, rounded to 5 units, nothing under MIN_K. Tabular figures (the default
   figures, .tosf, .sc.tf and their ss08 sevens) are in no pair, so tnum columns
   keep their advances.

4. Relations and arrows (< = >, and every glyph mapped to a math symbol named for an
   arrow or relation, the symbols module's included) against the proportional figures
   and letters, by the same model at a lower gain (GAIN_OPS), an accented letter
   taking its letter's value. Part of KERN_FIG.

5. KERN_SUPSUB. Superiors with superiors and inferiors with inferiors (the supsub
   module's letters and signs, found by their `.sups.supsub`/`.subs.supsub` names or
   their <super>/<sub> decomposition) take their full-size letters' kerning times the
   superiors' scale (the superior 1's height over the 1's, 0.6); under 5 units dropped.

Sections 4 and 5 use glyphs other modules add in their glyphs phase, which runs
for every module before any features phase, so module order does not matter.

Placement: all lookups go after the small-cap kerning (the default). GPOS values
add up across lookups, and every pair here is one that no earlier lookup gives a
value (or, for the unmasking, the difference to what it gives), so the order
does not change any result.

Extending: a new glyph that should kern like an existing one goes in INHERIT
(glyph -> (left-side base, right-side base); None for a side that is built in);
INHERIT_BY_CODEPOINT does the same by code point for glyphs other modules add
(for example Greek capitals that share Latin shapes). An entry applies only when
the glyph exists, has no kerning yet, and no other module's GPOS text names it.
"""
import math
import unicodedata
from collections import defaultdict

from fontTools.pens.basePen import BasePen

# --- tuning -------------------------------------------------------------------
STEP = 10                 # profile rows every STEP units
Y0, Y1 = -300, 900
DEPTH = 80                # gap rows count up to DEPTH beyond the pair's closest row
BLUR, BLUR_R = 0.5, 200   # vertical spread of each edge: +BLUR units per unit, up to BLUR_R
GAIN_FIG = 0.25           # figure model gain (the fit on Mulish's capital pairs is 0.24-0.30)
GAIN_EDGE = 0.25          # edge-correction gain for inherited kerning
GAIN_OPS = 0.15           # relations and arrows: math spacing is meant to stay open, so a lower gain
MIN_K = 10                # smaller model values are dropped
MAX_K = 60                # and larger ones capped
ROUND = 5

# --- inheritance --------------------------------------------------------------
# glyph -> (base whose left-side kerning it takes, base whose right-side kerning it takes)
INHERIT = {
    # liga, ss01, ss03
    'f_f': ('f', 'f'), 'f_f_i': ('f', 'i'), 'f_f_l': ('f', 'l'), 't_t': ('t', 't'),
    'T_h': ('T', 'h'), 't_h': ('t', 'h'),
    # ss16 joins
    'f_b': ('f', 'b'), 'f_h': ('f', 'h'), 'f_k': ('f', 'k'), 'f_j': ('f', 'j'), 'f_t': ('f', 't'),
    'f_f_t': ('f', 't'), 't_f': ('t', 'f'), 'f_y': ('f', 'y'), 't_w': ('t', 'w'), 'r_y': ('r', 'y'),
    'r_w': ('r', 'w'), 'l_l': ('l', 'l'), 'r.rn': ('r', 'r'), 'c.cl': ('c', 'c'), 'T_T.dlig': ('T', 'T'),
    't_p': ('t', 'p'), 'x_t': ('x', 't'), 'f_u': ('f', 'u'), 'r_v': ('r', 'v'),
    # ss16 logotypes (whole words)
    'T_o_r_c_h_l_e_t_t_e.ss11': ('T', 'e'), 'n_e_t_w_o_r_k.ss11': ('n', 'k'),
    'g_r_a_d_i_e_n_t.ss11': ('g', 't'), 'g_r_a_d_i_e_n_t_s.ss11': ('g', 's'),
    's_o_f_t_m_a_x.ss11': ('s', 'x'), 'P_y_t_h_o_n.ss11': ('P', 'n'),
    # ss16 word marks: the side next to the known neighbour is built in
    'v.vec': ('v', None), 'g_t.w200': (None, None), 'd_u_a_l.arch': (None, 'l'),
    'b.backc': ('b', None), 'd.fwdb': (None, 'd'), 't.out': (None, 't'), 't_s.out': (None, 's'),
    # ss16 punctuation forms
    'hyphen.case': ('hyphen', 'hyphen'), 'endash.range': ('endash', 'endash'),
    'colon.lf': ('colon', 'colon'), 'colon.of': ('colon', 'colon'),
    # Mulish leaves these unkerned (Ta, Tá: -76, 0)
    'aacute': ('a', 'a'), 'abreve': ('a', 'a'), 'uni01CE': ('a', 'a'), 'acircumflex': ('a', 'a'),
    'uni0201': ('a', 'a'), 'adieresis': ('a', 'a'), 'uni0227': ('a', 'a'), 'agrave': ('a', 'a'),
    'uni0203': ('a', 'a'), 'amacron': ('a', 'a'), 'aring': ('a', 'a'), 'aringacute': ('a', 'a'),
    'atilde': ('a', 'a'), 'uni01CD': ('A', 'A'), 'uni0226': ('A', 'A'), 'IJ': ('I', 'J'),
    # small caps with no pairs
    'IJ.sc': ('I.sc', 'J.sc'), 'uni01CD.sc': ('A.sc', 'A.sc'), 'uni0226.sc': ('A.sc', 'A.sc'),
    'germandbls.sc': ('S.sc', 'S.sc'), 'uni01D4.sc': ('U.sc', 'U.sc'), 'uni01E9.sc': ('K.sc', 'K.sc'),
    'uni021F.sc': ('H.sc', 'H.sc'), 'uni1E97.sc': ('T.sc', 'T.sc'), 'uni01E5.sc': ('G.sc', 'G.sc'),
}
ALT_SUFFIXES = ('.ss04', '.ss05', '.ss06', '.ss07')   # X.ss0N kerns like X (when X has kerning)
# code point -> base glyph, for glyphs other modules add (Greek capitals drawn as Latin)
INHERIT_BY_CODEPOINT = {
    0x0391: 'A', 0x0392: 'B', 0x0395: 'E', 0x0396: 'Z', 0x0397: 'H', 0x0399: 'I', 0x039A: 'K',
    0x039C: 'M', 0x039D: 'N', 0x039F: 'O', 0x03A1: 'P', 0x03A4: 'T', 0x03A5: 'Y', 0x03A7: 'X',
}

# --- figures ------------------------------------------------------------------
DIG = 'zero one two three four five six seven eight nine'.split()
FIG_PUNCT = ('period comma colon semicolon parenleft parenright bracketleft bracketright quoteleft quoteright '
             'quotedblleft quotedblright quotesingle quotedbl slash percent hyphen endash endash.range').split()
FIG_SETS = (   # (name, figures, punctuation they meet, reference glyph)
    ('lining', [d + '.pnum' for d in DIG] + ['seven.pnum.ss08'], FIG_PUNCT + ['colon.lf'], 'H'),
    ('oldstyle', [d + '.osf' for d in DIG] + ['seven.osf.ss08'], FIG_PUNCT + ['colon.of', 'percent.osf'], 'H'),
    ('smallcap', [d + '.sc' for d in DIG] + ['seven.sc.ss08'],
     'period comma colon semicolon parenleft.sc parenright.sc bracketleft.sc bracketright.sc quoteleft.sc '
     'quoteright.sc quotedblleft.sc quotedblright.sc quotesingle.sc quotedbl.sc slash.sc percent.sc hyphen.sc '
     'endash.sc'.split(), 'H.sc'),
)
TABULAR = (DIG + [d + '.tosf' for d in DIG] + [d + '.sc.tf' for d in DIG]
           + ['seven.ss08', 'seven.tosf.ss08', 'seven.sc.tf.ss08'])

# letters and punctuation the edge corrections are measured against (others use their
# base letter: an accented letter its letter, a small cap its letter's small cap)
CORE_PUNCT = ('period comma colon semicolon parenleft parenright bracketleft bracketright braceleft braceright '
              'quoteleft quoteright quotedblleft quotedblright quotesingle quotedbl hyphen endash emdash slash '
              'backslash question exclam guillemotleft guillemotright quotesinglbase quotedblbase asterisk '
              'underscore ampersand').split()


# ============================================================================
# kerning as it applies: a precedence-aware walk of GPOS pair lookups
def _xa(v): return (getattr(v, 'XAdvance', 0) or 0) if v else 0


def _subtables(lk):
    return [st.ExtSubTable if lk.LookupType == 9 else st for st in lk.SubTable]


def lookup_pairs(lk):
    """(effective {(a, b): v}, nominal {(a, b): v}) of one pair-adjustment lookup.
    Effective: HarfBuzz's rule, the first subtable that covers a and matches b applies
    (format 2 always matches, with class 0 for an unlisted b). Nominal: each pair's
    first explicit record."""
    sts = [st for st in _subtables(lk) if st.Format in (1, 2) and hasattr(st, 'Coverage')]
    nominal, eff = {}, {}
    for st in sts:
        if st.Format == 1:
            for a, ps in zip(st.Coverage.glyphs, st.PairSet):
                for r in ps.PairValueRecord:
                    nominal.setdefault((a, r.SecondGlyph), _xa(r.Value1))
        else:
            c2 = defaultdict(list)
            for g, c in st.ClassDef2.classDefs.items():
                if c: c2[c].append(g)
            for a in st.Coverage.glyphs:
                rec = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)]
                for c, gs_ in c2.items():
                    v = _xa(rec.Class2Record[c].Value1)
                    for b in gs_:
                        nominal.setdefault((a, b), v)
    covsets = [set(st.Coverage.glyphs) for st in sts]
    lefts = set().union(*covsets) if covsets else set()
    for a in lefts:
        seen = set()
        for st, cs in zip(sts, covsets):
            if a not in cs: continue
            if st.Format == 1:
                for r in st.PairSet[st.Coverage.glyphs.index(a)].PairValueRecord:
                    if r.SecondGlyph not in seen:
                        seen.add(r.SecondGlyph); eff[a, r.SecondGlyph] = _xa(r.Value1)
            else:
                rec = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)]
                for b, c in st.ClassDef2.classDefs.items():
                    if c and b not in seen:
                        eff[a, b] = _xa(rec.Class2Record[c].Value1)
                break
    return ({k: v for k, v in eff.items() if v}, {k: v for k, v in nominal.items() if v})


def kern_lookup_indices(gpos):
    return sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern'
                   for i in fr.Feature.LookupListIndex})


def effective_kerning(gpos):
    tot = defaultdict(int)
    for i in kern_lookup_indices(gpos):
        lk = gpos.LookupList.Lookup[i]
        if lk.LookupType not in (2, 9): continue
        for k, v in lookup_pairs(lk)[0].items(): tot[k] += v
    return {k: v for k, v in tot.items() if v}


# ============================================================================
# ink profiles and the optical model
class _Seg(BasePen):
    def __init__(self):
        super().__init__(None); self.segs = []; self.cur = self.start = None
    def _moveTo(self, p): self.start = self.cur = p
    def _lineTo(self, p): self.segs.append((self.cur, p)); self.cur = p
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur
        for i in range(1, 13):
            t = i / 12; m = 1 - t
            q = tuple(m ** 3 * p0[k] + 3 * m * m * t * p1[k] + 3 * m * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1))
            self.segs.append((self.cur, q)); self.cur = q
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur
        for i in range(1, 11):
            t = i / 10; m = 1 - t
            q = tuple(m * m * p0[k] + 2 * m * t * p1[k] + t * t * p2[k] for k in (0, 1))
            self.segs.append((self.cur, q)); self.cur = q
    def _closePath(self):
        if self.cur is not None and self.cur != self.start: self.segs.append((self.cur, self.start))
        self.cur = self.start
    _endPath = _closePath


NROWS = (Y1 - Y0) // STEP + 1
INF = 1e9


class Model:
    """Each glyph's edges row by row (white from the advance edge to the ink, blurred
    vertically), and the pair measure: the mean white between two edges over the rows
    where both have ink, each row counted up to DEPTH beyond the closest one. A pair's
    model kern is the double difference of that measure against a straight reference
    glyph, -gain * (G(a,b) - G(a,ref) - G(ref,b) + G(ref,ref)), so a glyph's own
    sidebearings, which its spacing already sets, cancel out."""
    def __init__(self, ctx):
        self.ctx = ctx; self.cache = {}; self.gcache = {}

    def edges(self, n):
        if n in self.cache: return self.cache[n]
        pen = _Seg(); self.ctx.path_of(n).draw(pen)
        lo = [None] * NROWS; hi = [None] * NROWS
        for (x0, y0), (x1, y1) in pen.segs:
            if y0 == y1: continue
            a, b = min(y0, y1), max(y0, y1)
            for k in range(max(0, math.ceil((a - Y0 - 0.5) / STEP)), min(NROWS - 1, math.floor((b - Y0 - 0.5) / STEP)) + 1):
                y = Y0 + k * STEP + 0.5
                if not (a <= y < b): continue
                x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                lo[k] = x if lo[k] is None else min(lo[k], x)
                hi[k] = x if hi[k] is None else max(hi[k], x)
        w = self.ctx.W(n)
        R = [INF if h is None else w - h for h in hi]
        L = [INF if l is None else l for l in lo]
        out = (self._blur(R), self._blur(L))
        self.cache[n] = out
        return out

    @staticmethod
    def _blur(A):
        out = list(A); r = BLUR_R // STEP
        for i, v in enumerate(A):
            if v >= INF: continue
            for s in range(1, r + 1):
                pen = v + BLUR * s * STEP
                for j in (i - s, i + s):
                    if 0 <= j < NROWS and pen < out[j]: out[j] = pen
        return out

    def G(self, a, b):
        key = (a, b)
        if key in self.gcache: return self.gcache[key]
        R = self.edges(a)[0]; L = self.edges(b)[1]
        g = [r + l for r, l in zip(R, L) if r < INF / 2 and l < INF / 2]
        if not g: v = None
        else:
            m = min(g) + DEPTH; v = sum(min(x, m) for x in g) / len(g)
        self.gcache[key] = v
        return v

    def dd(self, a, b, ref):
        vals = (self.G(a, b), self.G(a, ref), self.G(ref, b), self.G(ref, ref))
        if any(v is None for v in vals): return 0.0
        return vals[0] - vals[1] - vals[2] + vals[3]


def _round(k, cap=MAX_K):
    if abs(k) < MIN_K: return 0
    k = max(-cap, min(cap, k))
    return int(ROUND * round(k / ROUND))


# ============================================================================
# the small-cap kerning as build.py writes it (round 13), and what its compile hides
def sc_kern_rules(ctx):
    """build.py's SC_KERN rules, in its order: (glyph pairs, class pairs), each a list of
    (lefts, rights, value). Mirrors build.py's round 13 loop exactly."""
    glyf = ctx.glyf; font = ctx.font
    src = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ') | {c for _, c, _ in ctx.SC_ACC} | set(ctx.DIGITS) | set(ctx.SC_SYMBOLS)
    rev = {g: u for u, g in font.getBestCmap().items()}
    def mp(g):
        if g in src and g + '.sc' in glyf.glyphs: return g + '.sc', True
        if g + '.sc' not in glyf.glyphs and g in rev and unicodedata.category(chr(rev[g]))[0] in 'PS': return g, False
        return None
    scale = ctx.SC_SCALE * ctx.SC_K
    def v_(x): return round((x or 0) * scale)
    gp, cp = [], []
    scg = ctx.sc_font['GPOS'].table
    for i in sorted({i for fr in scg.FeatureList.FeatureRecord if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex}):
        lk = scg.LookupList.Lookup[i]
        for st in lk.SubTable:
            if lk.LookupType == 9: st = st.ExtSubTable
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for a, ps in zip(cov, st.PairSet):
                    ma = mp(a)
                    if not ma: continue
                    for rec in ps.PairValueRecord:
                        mb = mp(rec.SecondGlyph); v = v_(_xa(rec.Value1))
                        if mb and (ma[1] or mb[1]) and v: gp.append(([ma[0]], [mb[0]], v))
            else:
                c1 = {}
                for g in cov: c1.setdefault(st.ClassDef1.classDefs.get(g, 0), []).append(g)
                c2 = {}
                for g, c in st.ClassDef2.classDefs.items(): c2.setdefault(c, []).append(g)
                split = lambda gs_: [[m[0] for m in map(mp, sorted(gs_)) if m and m[1] == k] for k in (True, False)]
                c1s = {c: split(g) for c, g in c1.items()}; c2s = {c: split(g) for c, g in c2.items() if c}
                for k1, (s1, p1) in sorted(c1s.items()):
                    for k2, (s2, p2) in sorted(c2s.items()):
                        r = st.Class1Record[k1].Class2Record[k2]
                        v = v_(_xa(r.Value1))
                        if not v: continue
                        for L, R in ((s1, s2), (s1, p2), (p1, s2)):
                            if L and R: cp.append((L, R, v))
    return gp, cp


def sc_kern_fea(gp, cp):
    return ('languagesystem DFLT dflt; languagesystem latn dflt;\nlookup SC_KERN {\n  lookupflag IgnoreMarks;\n'
            + ''.join(f'  pos {L[0]} {R[0]} {v};\n' for L, R, v in gp) + '  subtable;\n'
            + ''.join(f'  pos [{" ".join(L)}] [{" ".join(R)}] {v};\n' for L, R, v in cp)
            + '} SC_KERN;\nfeature kern { lookup SC_KERN; } kern;\n')


def sc_kern_intended(gp, cp):
    """What the rules say: glyph pairs first, then class pairs, the first rule for a
    pair wins (feaLib keeps the first of duplicate pairs)."""
    out = {}
    for L, R, v in gp + cp:
        for a in L:
            for b in R:
                out.setdefault((a, b), v)
    return out


def compile_gpos(ctx, fea):
    from fontTools.ttLib import TTFont, newTable
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    t = TTFont()
    t.setGlyphOrder(ctx.font.getGlyphOrder())
    if 'GDEF' in ctx.font: t['GDEF'] = ctx.font['GDEF']
    addOpenTypeFeaturesFromString(t, fea, tables=['GPOS'])
    return t['GPOS'].table


# ============================================================================
# writing pairs as one conflict-free class-kerning subtable per lookup
def pairs_fea(name, pairs):
    """{(a, b): v} -> feature text for lookup `name`: lefts with the same row share a
    class, rights with the same column share a class, every class disjoint, so feaLib
    writes one format-2 subtable."""
    rows = defaultdict(dict)
    for (a, b), v in pairs.items():
        if v: rows[a][b] = v
    lcls = defaultdict(list)
    for a, r in rows.items(): lcls[tuple(sorted(r.items()))].append(a)
    lkeys = sorted(lcls, key=lambda k: sorted(lcls[k])[0])
    col = defaultdict(list)
    for i, k in enumerate(lkeys):
        for b, v in k: col[b].append((i, v))
    rcls = defaultdict(list)
    for b, c in col.items(): rcls[tuple(c)].append(b)
    rkeys = sorted(rcls, key=lambda k: sorted(rcls[k])[0])
    out = []
    for i, k in enumerate(lkeys): out.append(f'@{name}_L{i} = [{" ".join(sorted(lcls[k]))}];')
    for j, k in enumerate(rkeys): out.append(f'@{name}_R{j} = [{" ".join(sorted(rcls[k]))}];')
    out.append(f'lookup {name} {{\n  lookupflag IgnoreMarks;')
    for j, k in enumerate(rkeys):
        for i, v in k:
            out.append(f'  pos @{name}_L{i} @{name}_R{j} {v};')
    out.append(f'}} {name};\nfeature kern {{ lookup {name}; }} kern;\n')
    return '\n'.join(out), len(lkeys), len(rkeys)


# ============================================================================
def _kerned_glyphs(eff):
    return {a for a, _ in eff} | {b for _, b in eff}


def _other_module_gpos_names(ctx):
    names = set()
    for _, mod, text in ctx.MODULE_GPOS:
        if mod == ctx.module: continue
        names.update(text.replace('[', ' ').replace(']', ' ').replace(';', ' ').split())
    return names


def features(ctx):
    font, glyf = ctx.font, ctx.glyf
    have = set(font.getGlyphOrder())
    model = Model(ctx)

    # 1. the small-cap kerning as intended, and the pairs its compile hides
    gp, cp = sc_kern_rules(ctx)
    sck = sc_kern_intended(gp, cp)
    sc_eff, _ = lookup_pairs(compile_gpos(ctx, sc_kern_fea(gp, cp)).LookupList.Lookup[0])
    unmask = {k: v - sc_eff.get(k, 0) for k, v in sck.items() if sc_eff.get(k, 0) != v}
    ctx.sc_intended = sck

    # the kerning every base glyph has: Mulish's (as it applies) and the small caps' (as intended)
    base = dict(effective_kerning(font['GPOS'].table))
    for k, v in sck.items(): base[k] = base.get(k, 0) + v
    kerned = _kerned_glyphs(base)
    by_left, by_right = defaultdict(dict), defaultdict(dict)
    for (a, b), v in base.items():
        by_left[a][b] = v; by_right[b][a] = v

    # 2. glyphs that inherit a base's kerning
    taken = _other_module_gpos_names(ctx)
    inherit = {g: s for g, s in INHERIT.items() if g in have}
    for g in sorted(have):
        for suf in ALT_SUFFIXES:
            if g.endswith(suf) and g not in inherit:
                b = g[:-len(suf)]
                if b in have: inherit[g] = (b, b)
    cmap = font.getBestCmap()
    for u, b in INHERIT_BY_CODEPOINT.items():
        if u in cmap and cmap[u] != b and b in have: inherit.setdefault(cmap[u], (b, b))
    inherit = {g: s for g, s in inherit.items() if g not in kerned and g not in taken}

    def resolve(g, side):
        """The kerned glyph whose `side` kerning g takes (following chains), or None."""
        seen = set()
        while g in inherit and g not in seen:
            seen.add(g); g = inherit[g][side]
            if g is None: return None
        return g if g in kerned else None

    new = sorted(inherit)
    LB = {g: resolve(g, 0) for g in new}            # left side's base
    RB = {g: resolve(g, 1) for g in new}            # right side's base

    rev = {g: u for u, g in cmap.items()}
    core = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') & have
    core |= {c + '.sc' for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c + '.sc' in have}
    core |= {p for p in CORE_PUNCT if p in have}
    def proxy(x):
        """The glyph whose outline stands for x in edge corrections, or None."""
        if x in core: return x
        if x in inherit:
            return None
        stem, dot, suf = x.partition('.')
        if suf == 'sc' and stem in rev:
            dec = unicodedata.decomposition(chr(rev[stem])).split()
            if dec and not dec[0].startswith('<'):
                c = chr(int(dec[0], 16))
                if c + '.sc' in core: return c + '.sc'
        if x in rev:
            dec = unicodedata.decomposition(chr(rev[x])).split()
            if dec and not dec[0].startswith('<'):
                c = chr(int(dec[0], 16))
                if c in core: return c
        return None

    # edge corrections: how much the glyph's edge differs from its base's, against each core glyph
    def corr_right(g, b):        # g on the left: its right edge against core glyph x on the right
        out = {}
        for x in core:
            d = -GAIN_EDGE * ((model.G(g, x) - model.G(g, 'H')) - (model.G(b, x) - model.G(b, 'H'))) \
                if None not in (model.G(g, x), model.G(g, 'H'), model.G(b, x), model.G(b, 'H')) else 0
            d = _round(d)
            if d: out[x] = d
        return out
    def corr_left(g, b):         # g on the right: its left edge against core glyph x on the left
        out = {}
        for x in core:
            d = -GAIN_EDGE * ((model.G(x, g) - model.G('H', g)) - (model.G(x, b) - model.G('H', b))) \
                if None not in (model.G(x, g), model.G('H', g), model.G(x, b), model.G('H', b)) else 0
            d = _round(d)
            if d: out[x] = d
        return out
    CR = {g: corr_right(g, RB[g]) for g in new if RB[g]}
    CL = {g: corr_left(g, LB[g]) for g in new if LB[g]}

    universe = sorted(have)
    newset = set(new)
    tab = set(TABULAR)
    pairs_l, pairs_r = {}, {}
    # new glyph on the left
    for g in new:
        b = RB[g]
        if not b: continue
        row = dict(by_left.get(b, {}))
        cr = CR[g]
        for x in universe:
            if x in tab: continue
            if x in newset:
                lb = LB[x]
                if not lb: continue
                v = base.get((b, lb), 0) + cr.get(proxy(lb) or '', 0) + CL[x].get(proxy(b) or '', 0)
            else:
                v = row.get(x, 0) + cr.get(proxy(x) or '', 0)
            if v: pairs_l[g, x] = v
    # new glyph on the right, an existing glyph on the left
    for g in new:
        b = LB[g]
        if not b: continue
        col = by_right.get(b, {})
        cl = CL[g]
        for x in universe:
            if x in newset or x in tab: continue
            v = col.get(x, 0) + cl.get(proxy(x) or '', 0)
            if v: pairs_r[x, g] = v

    # 3. figures
    pairs_f = {}
    fig_log = {}
    for name, figs, punct, ref in FIG_SETS:
        figs = [f for f in figs if f in have]; punct = [p for p in punct if p in have]
        n0 = len(pairs_f)
        for a in figs:
            for b in figs + punct:
                k = _round(-GAIN_FIG * model.dd(a, b, ref))
                if k: pairs_f[a, b] = k
        for a in punct:
            for b in figs:
                k = _round(-GAIN_FIG * model.dd(a, b, ref))
                if k: pairs_f[a, b] = k
        fig_log[name] = len(pairs_f) - n0
    # a pair the figure model sets wins over an inherited one (ss16's range dash, colons)
    for k in pairs_f:
        pairs_l.pop(k, None); pairs_r.pop(k, None)
    figs_new_left = {k: v for k, v in pairs_f.items() if k[0] in newset}
    figs_new_right = {k: v for k, v in pairs_f.items() if k[0] not in newset and k[1] in newset}
    pairs_l.update(figs_new_left); pairs_r.update(figs_new_right)
    pairs_f = {k: v for k, v in pairs_f.items() if k not in figs_new_left and k not in figs_new_right}

    # 4. relations and arrows (Mulish's < = > and every module's) against proportional
    # figures and letters, by the same model; an accented letter takes its letter's value
    ops = sorted({g for u, g in cmap.items() if _is_relation(u)} - newset - tab)
    letters = [c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' if c in have]
    partners = letters + [f for _, figs, _, _ in FIG_SETS[:2] for f in figs if f in have]
    same = defaultdict(list)                     # letter -> it and the glyphs that stand for it
    for x in universe:
        if x in newset or x in tab: continue
        p = x if x in letters else (proxy(x) if x not in core else None)
        if p in letters: same[p].append(x)
    pairs_o = {}
    for op in ops:
        for x in partners:
            for (a, b) in ((op, x), (x, op)):
                k = _round(-GAIN_OPS * model.dd(a, b, 'H'))
                if not k: continue
                for y in same.get(x, [x]):
                    key = (op, y) if a == op else (y, op)
                    if not base.get(key) and key not in pairs_f: pairs_o[key] = k
    pairs_f.update(pairs_o)

    # 5. superiors and inferiors (supsub's letters and signs, Mulish's figures) with their
    # own kind: their letters' kerning at their scale
    sups = _supsub_bases(ctx, have, cmap)
    sscale = (lambda a, b: (a[3] - a[1]) / (b[3] - b[1]))(ctx.path_of('uni00B9').bounds, ctx.path_of('one').bounds) \
        if {'uni00B9', 'one'} <= have else 0.6
    pairs_s = {}
    for kind in ('sup', 'sub'):
        gl = [(g, b) for g, (k, b) in sups.items() if k == kind]
        for g1, b1 in gl:
            for g2, b2 in gl:
                v = round(sscale * base.get((b1, b2), 0))
                if abs(v) >= ROUND and not base.get((g1, g2)): pairs_s[g1, g2] = v

    assert not any(a in tab or b in tab for a, b in list(pairs_l) + list(pairs_r) + list(pairs_f)), 'tabular figure kerned'
    assert not set(pairs_s) & (set(pairs_l) | set(pairs_r) | set(pairs_f))
    for (a, b) in list(pairs_l) + list(pairs_r) + list(pairs_f):
        assert base.get((a, b), 0) == 0, ('pair already kerned', a, b)

    ctx.added = {'unmask': unmask, 'new_l': pairs_l, 'new_r': pairs_r, 'fig': pairs_f, 'supsub': pairs_s}
    for nm, pr in (('KERN_SC_UNMASK', unmask), ('KERN_NEW_L', pairs_l), ('KERN_NEW_R', pairs_r), ('KERN_FIG', pairs_f),
                   ('KERN_SUPSUB', pairs_s)):
        if not pr: continue
        text, nl, nr = pairs_fea(nm, pr)
        ctx.gpos(text)
        ctx.log(f'{nm}: {len(pr)} pairs, {nl} x {nr} classes')
    ctx.log(f'{len(new)} glyphs inherit kerning; figure pairs {fig_log}; {len(ops)} relations and arrows, '
            f'{len(pairs_o)} pairs; {len(sups)} superiors and inferiors, {len(pairs_s)} pairs (x{sscale:.2f})')


RELATION_WORDS = ('ARROW', 'EQUAL', 'LESS-THAN', 'GREATER-THAN', 'IDENTICAL', 'TILDE OPERATOR', 'ALMOST',
                  'ASYMPTOTICALLY', 'PROPORTIONAL', 'ELEMENT OF', 'CONTAINS AS MEMBER', 'SUBSET', 'SUPERSET',
                  'PRECEDES', 'SUCCEEDS', 'PARALLEL', 'PERPENDICULAR', 'MAPS TO')


def _is_relation(u):
    """A relation or arrow: < = > and the mathematical symbols named for one."""
    ch = chr(u)
    if ch in '<=>': return True
    if unicodedata.category(ch) != 'Sm' and not (0x2190 <= u <= 0x21FF or 0x27F0 <= u <= 0x27FF or 0x2900 <= u <= 0x297F):
        return False
    if unicodedata.category(ch) not in ('Sm', 'So'): return False
    name = unicodedata.name(ch, '')
    if 'MODIFIER' in name or 'SUPERSCRIPT' in name or 'SUBSCRIPT' in name: return False
    return any(w in name for w in RELATION_WORDS)


def _supsub_bases(ctx, have, cmap):
    """superior/inferior glyph -> ('sup' | 'sub', the full-size glyph it is drawn from)."""
    out = {}
    for g in have:
        for suf, kind in (('.sups.supsub', 'sup'), ('.subs.supsub', 'sub')):
            if g.endswith(suf) and g[:-len(suf)] in have: out[g] = (kind, g[:-len(suf)])
    for u, g in cmap.items():
        dec = unicodedata.decomposition(chr(u)).split()
        if len(dec) == 2 and dec[0] in ('<super>', '<sub>'):
            b = cmap.get(int(dec[1], 16))
            if b and b in have: out[g] = ('sup' if dec[0] == '<super>' else 'sub', b)
    return out


def post(ctx):
    """The small-cap pairs must all apply now, and nothing tabular may be kerned."""
    gpos = ctx.font['GPOS'].table
    eff = effective_kerning(gpos)
    bad = [(a, b, v, eff.get((a, b), 0)) for (a, b), v in ctx.sc_intended.items() if eff.get((a, b), 0) != v
           and (a, b) not in ctx.added['new_l'] and (a, b) not in ctx.added['new_r']]
    # a small-cap pair Mulish also kerns adds up; only the SC_KERN part is checked
    if bad:
        raise SystemExit(f'kern: {len(bad)} small-cap pairs still do not apply as written, e.g. {bad[:5]}')
    tab = set(TABULAR)
    hit = [k for k in eff if k[0] in tab or k[1] in tab]
    if hit: raise SystemExit(f'kern: tabular figures kerned: {hit[:5]}')
    ctx.log(f'effective kern pairs: {len(eff)}; small-cap pairs all apply ({len(ctx.sc_intended)})')

"""greek: the Greek alphabet (U+0370-03FF) for Torchlette Sans, fitted from Commissioner.

Sources and licenses. The Greek letters are imported, not drawn: the lowercase (but
omicron, mu and pi), the capitals Sigma, Phi and Psi and the small capitals of those
three come from Commissioner, by Kostas Bartsokas (Copyright 2019 The Commissioner
Project Authors, https://github.com/kosbarts/Commissioner), licensed under the SIL Open
Font License 1.1 with no Reserved Font Name; the variable font `../commissioner/
Commissioner[FLAR,VOLM,slnt,wght].ttf` is the file from google/fonts `ofl/commissioner/`
(its OFL.txt is beside it). The five mathematical variants ϑ ϕ ϖ ϱ ϵ, which
Commissioner lacks, come from Noto Sans (Copyright 2022 The Noto Project Authors,
https://github.com/notofonts/latin-greek-cyrillic), OFL 1.1, no Reserved Font Name:
`../notosans/NotoSans-GreekMathSubset[wght].ttf` is google/fonts `ofl/notosans/
NotoSans[wdth,wght].ttf` with wdth pinned to 100 and subset to those five glyphs and
the six Latin letters the fitting measures (README has the commands; its OFL.txt is
beside it). Nothing is named after either font.

What Torchlette Sans contributes. Delta, Omega, mu and pi are Mulish's own glyphs
(uni0394, uni03A9, uni03BC, pi), left as they are. The capitals that share a Latin
shape (Α Β Ε Ζ Η Ι Κ Μ Ν Ο Ρ Τ Υ Χ) and omicron are composites of the Latin glyphs, so
they are those glyphs. Gamma, Pi, Xi, Lambda and Theta are made from Torchlette's F,
H, E, A and O (an arm or a bar removed, a bar added), so they match the Latin
capitals exactly; their small capitals likewise from F.sc, H.sc, E.sc, A.sc, O.sc, and
Delta's and Omega's from the heavier Mulish instance build.py's small caps use. The
accents are Torchlette's own acutecomb and uni0308, placed where Commissioner places its
marks; the dialytika-tonos (uni0385) is built from them on the plan of Commissioner's
dieresistonos.narrow, the dots moved out where the broader acute would come closer to
one than Commissioner's tonos does.

Fitting (per style). Each imported glyph is scaled in x and y to Torchlette's metrics,
not traced: the x-height goes to XH (470), descenders to p's depth, ascenders to d's
height, capitals to 705 and small capitals to SC_H, by piecewise-linear vertical maps
whose knots sit where the letters are straight (40 under the baseline, the x-height),
with θ and λ scaled uniformly to the ascender and γ and χ, which have no baseline
feature, mapped affinely from x-height to descender. Horizontally one scale serves
every lowercase letter: the x-height scale times a factor that fits Commissioner's o
to Torchlette's o. The weight is not faked: the module instances the variable
reference at the wght where the fitted n stem equals Torchlette's n stem (and, for the
capitals and small capitals, where the fitted H stem equals H's and H.sc's), by
bisection, as build.py chooses its small-cap weight. Sidebearings are the reference's,
scaled, times the ratio by which Torchlette's o and n sidebearings differ from the
reference's. The kerning of Greek pairs is Commissioner's, read from its GPOS at the
chosen weight and scaled; nothing under 4 units.

Changes to the shared font: GLYPH_OVERRIDE Sigma and summation. Mulish's Sigma glyph
is the summation sign (it descends to -180) and summation is a composite of it;
summation is decomposed first, so it keeps that outline, and Sigma is redrawn on the
baseline for Greek text. No code point that Mulish maps is remapped.

Features: smcp and c2sc (GREEK_SMCP, GREEK_C2SC, placed before `main` like build.py's
own small-cap lookups, which build.py then moves to the front of GSUB); kern
(GREEK_KERN, GPOS, default placement). Glyph names: AGL names for the encoded glyphs
(alpha, sigma1, theta1, uni03F1 ...); unencoded ones end in `.greek`.

Knobs (environment): GREEK_KXO, the horizontal scale over the o fit (1.025); GREEK_SB,
a factor on every sidebearing (1.0); GREEK_THETA_BAR, Theta's bar as a share of its
counter (0.62).
"""
import math
import os

import pathops
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

GLYPH_OVERRIDE = {'Sigma', 'summation'}

HERE = os.path.dirname(os.path.abspath(__file__))
COMMISSIONER = os.path.join(HERE, '..', 'commissioner', 'Commissioner[FLAR,VOLM,slnt,wght].ttf')
NOTO = os.path.join(HERE, '..', 'notosans', 'NotoSans-GreekMathSubset[wght].ttf')

# Commissioner glyph -> Torchlette glyph, code point, vertical map
LOWER = [
    ('alpha', 'alpha', 0x03B1, 'body'), ('beta', 'beta', 0x03B2, 'asc'), ('gamma', 'gamma', 0x03B3, 'affine'),
    ('delta', 'delta', 0x03B4, 'asc'), ('epsilon', 'epsilon', 0x03B5, 'body'), ('zeta', 'zeta', 0x03B6, 'asc'),
    ('eta', 'eta', 0x03B7, 'body'), ('theta', 'theta', 0x03B8, 'tall'), ('iota', 'iota', 0x03B9, 'body'),
    ('kappa', 'kappa', 0x03BA, 'body'), ('lambda', 'lambda', 0x03BB, 'tall'), ('nu', 'nu', 0x03BD, 'body'),
    ('xi', 'xi', 0x03BE, 'asc'), ('rho', 'rho', 0x03C1, 'body'), ('uni03C2', 'sigma1', 0x03C2, 'body'),
    ('sigma', 'sigma', 0x03C3, 'body'), ('tau', 'tau', 0x03C4, 'body'), ('upsilon', 'upsilon', 0x03C5, 'body'),
    ('phi', 'phi', 0x03C6, 'body'), ('chi', 'chi', 0x03C7, 'affine'), ('psi', 'psi', 0x03C8, 'asc'),
    ('omega', 'omega', 0x03C9, 'body'),
]
MATH = [   # Noto glyph -> Torchlette glyph, code point, map
    ('uni03D1', 'theta1', 0x03D1, 'asc'), ('uni03D5', 'phi1', 0x03D5, 'asc'), ('uni03D6', 'omega1', 0x03D6, 'body'),
    ('uni03F1', 'uni03F1', 0x03F1, 'body'), ('uni03F5', 'uni03F5', 0x03F5, 'body'),
    ('uni03F0', 'uni03F0', 0x03F0, 'body'),
]
CAPS_REF = [('Sigma', 'Sigma', 0x03A3, 'H'), ('Phi', 'Phi', 0x03A6, 'O'), ('Psi', 'Psi', 0x03A8, 'H')]
CAPS_LATIN = [('Alpha', 'A', 0x0391), ('Beta', 'B', 0x0392), ('Epsilon', 'E', 0x0395), ('Zeta', 'Z', 0x0396),
              ('Eta', 'H', 0x0397), ('Iota', 'I', 0x0399), ('Kappa', 'K', 0x039A), ('Mu', 'M', 0x039C),
              ('Nu', 'N', 0x039D), ('Omicron', 'O', 0x039F), ('Rho', 'P', 0x03A1), ('Tau', 'T', 0x03A4),
              ('Upsilon', 'Y', 0x03A5), ('Chi', 'X', 0x03A7)]
# lowercase tonos and dialytika: Torchlette glyph, base, Commissioner composite (for the mark's place), code point
LC_TONOS = [('alphatonos', 'alpha', 'alphatonos', 0x03AC), ('epsilontonos', 'epsilon', 'epsilontonos', 0x03AD),
            ('etatonos', 'eta', 'etatonos', 0x03AE), ('iotatonos', 'iota', 'iotatonos', 0x03AF),
            ('omicrontonos', 'omicron', 'omicrontonos', 0x03CC), ('upsilontonos', 'upsilon', 'upsilontonos', 0x03CD),
            ('omegatonos', 'omega', 'omegatonos', 0x03CE)]
LC_DIER = [('iotadieresis', 'iota', 'iotadieresis', 0x03CA), ('upsilondieresis', 'upsilon', 'upsilondieresis', 0x03CB)]
LC_BOTH = [('iotadieresistonos', 'iota', 'iotadieresis', 0x0390), ('upsilondieresistonos', 'upsilon', 'upsilondieresis', 0x03B0)]
UC_TONOS = [('Alphatonos', 'Alpha', 0x0386), ('Epsilontonos', 'Epsilon', 0x0388), ('Etatonos', 'Eta', 0x0389),
            ('Iotatonos', 'Iota', 0x038A), ('Omicrontonos', 'Omicron', 0x038C), ('Upsilontonos', 'Upsilon', 0x038E),
            ('Omegatonos', 'uni03A9', 0x038F)]
# punctuation whose Commissioner kerning with Greek letters is kept (same names in both fonts)
KERN_PUNCT = ['period', 'comma', 'hyphen', 'colon', 'semicolon', 'quotesingle', 'quotedbl', 'parenleft', 'parenright',
              'slash', 'guillemotleft', 'guillemotright', 'quoteright', 'quoteleft', 'quotedblleft', 'quotedblright']
KERN_MIN = 4


# --- outline helpers --------------------------------------------------------------
def _contours(glyf, name):
    """A glyph's contours, composites decomposed, as lists of (x, y, on-curve)."""
    g = glyf[name]
    coords, ends, flags = g.getCoordinates(glyf)
    out, s = [], 0
    for e in ends:
        out.append([(coords[i][0], coords[i][1], bool(flags[i] & 1)) for i in range(s, e + 1)]); s = e + 1
    return out


def _draw(contours, fx, fy):
    """Quadratic contours, each point mapped through fx and fy, as a pathops path."""
    p = pathops.Path(); pen = p.getPen()
    for c in contours:
        pts = [(fx(x), fy(y), on) for x, y, on in c]
        if not pts: continue
        k = next((i for i, q in enumerate(pts) if q[2]), None)
        if k is None:                                   # all off-curve: start at an implied midpoint
            a, b = pts[-1], pts[0]
            pts = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, True)] + pts
            k = 0
        pts = pts[k:] + pts[:k]
        pen.moveTo(pts[0][:2]); offs = []
        for x, y, on in pts[1:] + [pts[0]]:
            if on:
                if offs: pen.qCurveTo(*offs, (x, y)); offs = []
                else: pen.lineTo((x, y))
            else: offs.append((x, y))
        if offs: pen.qCurveTo(*offs, pts[0][:2])
        pen.closePath()
    return p


def _glyph_path(glyf, name):
    return _draw(_contours(glyf, name), lambda x: x, lambda y: y)


def _spans(p, y=None, x=None):
    """Ink intervals of a path along a horizontal (y) or vertical (x) line, unrounded."""
    r = pathops.Path(); pen = r.getPen()
    if y is not None: box = (-5000, y - 0.25, 5000, y + 0.25)
    else: box = (x - 0.25, -5000, x + 0.25, 5000)
    pen.moveTo((box[0], box[1])); pen.lineTo((box[2], box[1])); pen.lineTo((box[2], box[3])); pen.lineTo((box[0], box[3])); pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION)
    i, j = (0, 2) if y is not None else (1, 3)
    return sorted((c.bounds[i], c.bounds[j]) for c in q.contours)


def _bounds(glyf, name):
    g = glyf[name]; g.recalcBounds(glyf); return g.xMin, g.yMin, g.xMax, g.yMax


def _vstem(p, b, left=True):
    """The x range of a full-height vertical stem at the left (or right) edge of a path
    with bounds b: the run of x where the ink is one span from bottom to top."""
    step = 1 if left else -1
    x = (b[0] if left else b[2]) + step * 2
    edge = x
    while b[0] < x < b[2]:
        sp = _spans(p, x=x)
        if len(sp) != 1 or sp[0][0] > b[1] + 2 or sp[0][1] < b[3] - 2: break
        edge = x; x += step
    return (b[0], edge) if left else (edge, b[2])


# --- the reference fonts ------------------------------------------------------------
class Ref:
    """A variable reference font, subset to the glyphs the module reads, instanced on demand."""

    def __init__(self, path, glyph_names, keep_kern):
        f = TTFont(path)
        self.cmap = f.getBestCmap()
        want = {g for g in glyph_names if g in f.getGlyphOrder()}
        opts = subset.Options()
        opts.layout_features = ['kern'] if keep_kern else []
        opts.name_IDs = ['*']; opts.notdef_outline = True; opts.hinting = False; opts.glyph_names = True
        opts.drop_tables += ['MVAR', 'STAT']
        sub = subset.Subsetter(options=opts); sub.populate(glyphs=want); sub.subset(f)
        self.vf = f
        self.axes = {a.axisTag: a for a in f['fvar'].axes}
        self._inst = {}

    def at(self, w):
        w = round(w, 1)
        if w not in self._inst:
            loc = {t: a.defaultValue for t, a in self.axes.items()}
            loc['wght'] = w
            self._inst[w] = instantiateVariableFont(self.vf, loc, inplace=False, updateFontNames=False)
        return self._inst[w]

    def has(self, name): return name in self.vf.getGlyphOrder()


class Fit:
    """One instance of a reference, with the metrics and maps that fit it to Torchlette."""

    def __init__(self, ctx, ref, w, XH, ASC_T, DESC_T, kxo):
        self.ref, self.w = ref, w
        f = ref.at(w); self.f = f; self.glyf = f['glyf']; self.hmtx = f['hmtx']
        c = ref.cmap
        self.names = {ch: c[ord(ch)] for ch in 'xdpnoHO' if ord(ch) in c}
        self.xh = _bounds(self.glyf, self.names['x'])[3]
        self.asc = _bounds(self.glyf, self.names['d'])[3]
        self.desc = _bounds(self.glyf, self.names['p'])[1]
        self.cap = _bounds(self.glyf, self.names['H'])[3]
        self.s = XH / self.xh
        ob = _bounds(self.glyf, self.names['o'])
        t_ob = _bounds(ctx.glyf, 'o')
        self.kx = kxo * (t_ob[2] - t_ob[0]) / ((ob[2] - ob[0]) * self.s)
        self.sx = self.s * self.kx
        # vertical maps (y in reference units -> Torchlette units)
        s = self.s; DK = -40.0
        kd = (DESC_T - DK) / (self.desc * s - DK)
        ka = (ASC_T - XH) / (self.asc * s - XH)
        st = ASC_T / self.asc
        a = (XH - DESC_T) / (self.xh - self.desc); b = XH - a * self.xh

        def body(y):
            y = y * s
            return DK + (y - DK) * kd if y < DK else y

        def asc(y):
            y0 = y * s
            return XH + (y0 - XH) * ka if y0 > XH else body(y)

        self.maps = {'body': body, 'asc': asc, 'tall': lambda y: y * st, 'affine': lambda y: a * y + b}

    def stem(self, name, y):
        sp = _spans(_glyph_path(self.glyf, name), y=y)
        return (sp[0][1] - sp[0][0]) if sp else 0

    def n_stem(self):
        return self.stem(self.names['n'], self.xh / 2) * self.sx

    def H_stem(self, scale):
        return self.stem(self.names['H'], self.cap * 0.2) * scale

    def side(self, name):
        """The reference glyph's sidebearings, unscaled."""
        b = _bounds(self.glyf, name); adv = self.hmtx[name][0]
        return b[0], adv - b[2]

    def place(self, name, ymap, sx, ksb, sy=None):
        """The glyph fitted: a path at its new left sidebearing, and its advance."""
        fy = ymap if callable(ymap) else (lambda y: y * sy)
        p = _draw(_contours(self.glyf, name), lambda x: x * sx, fy)
        l, r = self.side(name)
        b = p.bounds
        lsb, rsb = round(l * sx * ksb), round(r * sx * ksb)
        q = pathops.Path(); p.draw(TransformPen(q.getPen(), (1, 0, 0, 1, lsb - b[0], 0)))
        return q, lsb + (b[2] - b[0]) + rsb


def _clearance(a, b, hi=200.0):
    """The least distance between the ink of paths a and b (0 when they touch), to 1/4 unit."""
    def touches(d):
        g = pathops.Path(); a.draw(g.getPen())
        if d > 0:
            g.stroke(2 * d, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
            g.convertConicsToQuads()
            g = pathops.op(g, a, pathops.PathOp.UNION)
        return abs(pathops.op(g, b, pathops.PathOp.INTERSECTION).area) > 0.01
    if touches(0): return 0.0
    lo = 0.0
    if not touches(hi): return hi
    while hi - lo > 0.25:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if touches(mid) else (mid, hi)
    return lo


def _bisect(fn, lo, hi, n=9):
    """The w in [lo, hi] where fn(w) crosses 0 (fn increasing), to (hi - lo) / 2**n."""
    for _ in range(n):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if fn(mid) < 0 else (lo, mid)
    return round((lo + hi) / 2)


def _pair_kerning(font, names):
    """Horizontal pair kerning of the font's kern feature for pairs of `names`, by glyph."""
    gpos = font['GPOS'].table
    idx = sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex})
    out = {}
    names = set(names)
    for i in idx:
        lk = gpos.LookupList.Lookup[i]
        seen = {}
        for st in lk.SubTable:
            if lk.LookupType == 9: st = st.ExtSubTable
            if getattr(st, 'LookupType', 2) != 2: continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for g1, ps in zip(cov, st.PairSet):
                    if g1 not in names: continue
                    for rec in ps.PairValueRecord:
                        if rec.SecondGlyph in names and (g1, rec.SecondGlyph) not in seen:
                            seen[g1, rec.SecondGlyph] = getattr(rec.Value1, 'XAdvance', 0) or 0
            else:
                c1 = st.ClassDef1.classDefs; c2 = st.ClassDef2.classDefs
                by2 = {}
                for g, k in c2.items(): by2.setdefault(k, []).append(g)
                for g1 in cov:
                    if g1 not in names: continue
                    k1 = c1.get(g1, 0)
                    row = st.Class1Record[k1].Class2Record
                    for k2, rec in enumerate(row):
                        v = getattr(rec.Value1, 'XAdvance', 0) or 0
                        if not v: continue
                        g2s = by2.get(k2, []) if k2 else [g for g in names if g not in c2]
                        for g2 in g2s:
                            if g2 in names and (g1, g2) not in seen: seen[g1, g2] = v
        for k, v in seen.items(): out[k] = out.get(k, 0) + v
    return {k: v for k, v in out.items() if v}


# --- the module ---------------------------------------------------------------------
def glyphs(ctx):
    glyf, hmtx, font = ctx.glyf, ctx.hmtx, ctx.font
    XH = ctx.XH
    ASC_T = _bounds(glyf, 'd')[3]
    DESC_T = _bounds(glyf, 'p')[1]
    CAP_T = _bounds(glyf, 'H')[3]
    SC_H = ctx.SC_H
    KXO = ctx.P('GREEK_KXO', 1.025)
    SBF = ctx.P('GREEK_SB', 1.0)
    made = []

    def base(name, path, width):
        ctx.add(name, path, width); ctx.GDEF_CLASS[name] = 1; made.append(name)

    def composite(name, parts, width, cls=1):
        # a component that is itself a composite is replaced by its own components, so
        # no composite nests another (fontbakery's nested_components)
        flat = []
        for gn, dx, dy in parts:
            if glyf[gn].isComposite():
                flat += [(c.glyphName, c.x + dx, c.y + dy) for c in glyf[gn].components]
            else:
                flat.append((gn, dx, dy))
        g = Glyph(); g.numberOfContours = -1; g.components = []
        for gn, dx, dy in flat:
            c = GlyphComponent(); c.glyphName = gn; c.x = int(round(dx)); c.y = int(round(dy)); c.flags = 0x4
            g.components.append(c)
        glyf[name] = g; g.recalcBounds(glyf)
        hmtx[name] = (int(round(width)), g.xMin)
        if name not in font.getGlyphOrder(): font.setGlyphOrder(font.getGlyphOrder() + [name])
        ctx.GDEF_CLASS[name] = cls; made.append(name)

    # Torchlette's own measures
    def t_stem(name, y):
        sp = _spans(ctx.path_of(name), y=y); return sp[0][1] - sp[0][0]
    T_N = t_stem('n', XH / 2)
    T_H = t_stem('H', CAP_T * 0.2)
    T_HSC = t_stem('H.sc', SC_H * 0.2)
    ob, nb, Hb, Ob, Hscb = (_bounds(glyf, n) for n in ('o', 'n', 'H', 'O', 'H.sc'))

    # --- Commissioner, instanced where the fitted stems match -----------------------
    cm = TTFont(COMMISSIONER, lazy=True).getBestCmap()
    greek_ref = [g for u, g in cm.items() if 0x0370 <= u <= 0x03FF]
    latin_ref = [cm[ord(ch)] for ch in 'xdpnoHOAEIY' if ord(ch) in cm]
    punct_ref = [cm[u] for u in map(ord, '.,-:;\'"()/«»’‘“”') if u in cm]
    comm = Ref(COMMISSIONER, greek_ref + latin_ref + punct_ref + ['tonos', 'tonos.case', 'uni0308', 'uni0308.case',
                                                                  'dieresistonos', 'dieresistonos.narrow', 'minute', 'period', 'comma'], True)
    fit_of = lambda w: Fit(ctx, comm, w, XH, ASC_T, DESC_T, KXO)
    w_lc = _bisect(lambda w: fit_of(w).n_stem() - T_N, 100, 900)
    L = fit_of(w_lc)
    w_uc = _bisect(lambda w: fit_of(w).H_stem(CAP_T / fit_of(w).cap) - T_H, 100, 900)
    U = fit_of(w_uc)
    cap_scale = CAP_T / U.cap
    w_sc = _bisect(lambda w: fit_of(w).H_stem(SC_H / fit_of(w).cap) - T_HSC, 100, 900)
    S = fit_of(w_sc)
    sc_scale = SC_H / S.cap
    ctx.log(f'Commissioner wght {w_lc} (n stem {L.n_stem():.1f} for {T_N}), caps {w_uc} (H {U.H_stem(cap_scale):.1f} for {T_H}), '
            f'small caps {w_sc} (H {S.H_stem(sc_scale):.1f} for {T_HSC}); x-height scale {L.s:.4f}, x scale {L.sx:.4f}')
    ctx.greek_weights = {'lowercase': w_lc, 'capitals': w_uc, 'smallcaps': w_sc}

    # sidebearing factors: how Torchlette's o and n sidebearings relate to the fitted reference's
    ol, orr = L.side(L.names['o']); nl, nr = L.side(L.names['n'])
    ksb_lc = SBF * ((ob[0] / (ol * L.sx)) + (nb[0] / (nl * L.sx)) + ((hmtx['n'][0] - nb[2]) / (nr * L.sx))) / 3
    Hl, Hr = U.side(U.names['H']); Ol, Or = U.side(U.names['O'])
    ksb_uc = {'H': SBF * (Hb[0] / (Hl * cap_scale) + (hmtx['H'][0] - Hb[2]) / (Hr * cap_scale)) / 2,
              'O': SBF * (Ob[0] / (Ol * cap_scale) + (hmtx['O'][0] - Ob[2]) / (Or * cap_scale)) / 2}
    Hl_s, Hr_s = S.side(S.names['H'])
    ksb_sc = SBF * (Hscb[0] / (Hl_s * sc_scale) + (hmtx['H.sc'][0] - Hscb[2]) / (Hr_s * sc_scale)) / 2

    # --- lowercase from Commissioner --------------------------------------------------
    for src, name, uni, ymap in LOWER:
        p, adv = L.place(src, L.maps[ymap], L.sx, ksb_lc)
        base(name, p, adv); ctx.map(uni, name)
    composite('omicron', [('o', 0, 0)], hmtx['o'][0]); ctx.map(0x03BF, 'omicron')
    # mu (uni03BC) and pi are Mulish's, already mapped

    # --- the mathematical variants from Noto Sans --------------------------------------
    noto = Ref(NOTO, TTFont(NOTO, lazy=True).getGlyphOrder(), False)
    nfit = lambda w: Fit(ctx, noto, w, XH, ASC_T, DESC_T, KXO)
    w_math = _bisect(lambda w: nfit(w).n_stem() - T_N, 100, 900)
    N = nfit(w_math)
    nol, nor = N.side(N.names['o']); nnl, nnr = N.side(N.names['n'])
    ksb_math = SBF * ((ob[0] / (nol * N.sx)) + (nb[0] / (nnl * N.sx)) + ((hmtx['n'][0] - nb[2]) / (nnr * N.sx))) / 3
    ctx.log(f'Noto Sans wght {w_math} (n stem {N.n_stem():.1f} for {T_N}) for the five mathematical variants')
    ctx.greek_weights['math'] = w_math
    for src, name, uni, ymap in MATH:
        p, adv = N.place(src, N.maps[ymap], N.sx, ksb_math)
        base(name, p, adv); ctx.map(uni, name)

    # --- capitals ------------------------------------------------------------------
    # Mulish's Sigma is the summation sign; summation keeps that outline as its own glyph
    if glyf['summation'].isComposite():
        ctx.add('summation', ctx.path_of('summation'), hmtx['summation'][0])
    sum_path = ctx.path_of('summation')
    for src, name, uni, sbkey in CAPS_REF:
        p, adv = U.place(src, None, cap_scale, ksb_uc[sbkey], sy=cap_scale)
        if name == 'Sigma':
            # the glyph exists (Mulish's descending one): replace its outline and advance
            ctx.add('Sigma', p, adv)
            ctx.GDEF_CLASS['Sigma'] = 1
        else:
            base(name, p, adv)
        ctx.map(uni, name)
    assert _bounds(glyf, 'summation')[1] < -100, 'summation lost its descender'

    for name, latin, uni in CAPS_LATIN:
        composite(name, [(latin, 0, 0)], hmtx[latin][0]); ctx.map(uni, name)

    def gamma_from(F):
        """F with its lower arm removed."""
        p = ctx.path_of(F); b = _bounds(glyf, F)
        stem = _vstem(p, b)
        arms = _spans(p, x=stem[1] + 30)                  # the arms' y ranges beside the stem
        lower = arms[0]
        cut = ctx.rect(stem[1], lower[0] - 20, b[2] + 50, lower[1] + 20)
        return ctx.diff(p, cut), hmtx[F][0]

    def pi_from(H, T):
        """H without its crossbar, a bar over both stems as thick as T's."""
        p = ctx.path_of(H); b = _bounds(glyf, H)
        ls, rs = _vstem(p, b), _vstem(p, b, left=False)
        bar = _spans(p, x=(ls[1] + rs[0]) / 2)[0]
        tp = ctx.path_of(T); tb = _bounds(glyf, T)
        t = (lambda s: s[-1][1] - s[-1][0])(_spans(tp, x=tb[2] - 30))
        q = ctx.diff(p, ctx.rect(ls[1], bar[0] - 20, rs[0], bar[1] + 20))
        q = ctx.union(q, ctx.rect(ls[0], b[3] - t, rs[1], b[3]))
        return q, hmtx[H][0]

    def xi_from(E, width_k):
        """Three bars with E's arm thickness and middle-arm height; the outer ones width_k
        times E's ink width, the middle one inset as Commissioner insets its own."""
        p = ctx.path_of(E); b = _bounds(glyf, E)
        stem = _vstem(p, b)
        arms = _spans(p, x=stem[1] + 30)                  # bottom, middle, top
        bottom, mid, top = arms[0], arms[len(arms) // 2], arms[-1]
        w = (b[2] - b[0]) * width_k
        x0 = b[0]; x1 = x0 + w
        inset = w * XI_MID_INSET
        q = ctx.union(ctx.rect(x0, bottom[0], x1, bottom[1]), ctx.rect(x0, top[0], x1, top[1]),
                      ctx.rect(x0 + inset, mid[0], x1 - inset, mid[1]))
        return q, round(hmtx[E][0] + (w - (b[2] - b[0])))

    def lambda_from(A):
        """A without its crossbar: the outer contour's apex and feet, the legs' inner
        edges running straight from the feet to the counter's top (Mulish's A has a
        small ink trap where the crossbar meets each leg, which goes with the bar)."""
        cs = _contours(glyf, A)
        outer = max(cs, key=lambda c: max(x for x, y, on in c) - min(x for x, y, on in c))
        inner = min(cs, key=lambda c: max(x for x, y, on in c) - min(x for x, y, on in c))
        top = max(y for x, y, on in outer); base_y = min(y for x, y, on in outer)
        apex = sorted((x, y) for x, y, on in outer if y >= top - 2)
        feet = sorted(x for x, y, on in outer if y <= base_y + 2)
        ctop = max(y for x, y, on in inner)
        ctl = min(x for x, y, on in inner if y >= ctop - 2); ctr = max(x for x, y, on in inner if y >= ctop - 2)
        pts = [(feet[0], base_y)] + apex + [(feet[-1], base_y), (feet[-2], base_y), (ctr, ctop), (ctl, ctop), (feet[1], base_y)]
        return ctx.poly(pts), hmtx[A][0]

    def theta_from(O, share):
        """O with a floating bar through its middle, as thick as H's crossbar."""
        p = ctx.path_of(O); b = _bounds(glyf, O)
        ym = (b[1] + b[3]) / 2
        ring = _spans(p, y=ym)
        counter = (ring[0][1], ring[-1][0])
        hp = ctx.path_of('H'); hb = _bounds(glyf, 'H')
        ls, rs = _vstem(hp, hb), _vstem(hp, hb, left=False)
        bar = _spans(hp, x=(ls[1] + rs[0]) / 2)[0]; t = bar[1] - bar[0]
        half = (counter[1] - counter[0]) * share / 2; cx = (counter[0] + counter[1]) / 2
        return ctx.union(p, ctx.rect(cx - half, ym - t / 2, cx + half, ym + t / 2)), hmtx[O][0]

    # Commissioner's Xi: outer bars 1.26 of E's ink width, the middle bar inset 9% each side
    xb = _bounds(U.glyf, U.ref.cmap[0x039E]); eb = _bounds(U.glyf, U.ref.cmap[ord('E')])
    XI_K = (xb[2] - xb[0]) / (eb[2] - eb[0])
    xm = [s for s in _spans(_glyph_path(U.glyf, U.ref.cmap[0x039E]), y=(xb[1] + xb[3]) / 2)]
    XI_MID_INSET = (xm[0][0] - xb[0]) / (xb[2] - xb[0]) if xm else 0.09
    THETA_BAR = ctx.P('GREEK_THETA_BAR', 0.62)

    for name, uni, (fn, args) in [('Gamma', 0x0393, (gamma_from, ('F',))), ('Pi', 0x03A0, (pi_from, ('H', 'T'))),
                                  ('Xi', 0x039E, (xi_from, ('E', XI_K))), ('Lambda', 0x039B, (lambda_from, ('A',))),
                                  ('Theta', 0x0398, (theta_from, ('O', THETA_BAR))), ('uni03F4', 0x03F4, (theta_from, ('O', 1.05)))]:
        p, adv = fn(*args); base(name, p, adv); ctx.map(uni, name)

    # --- accents ---------------------------------------------------------------------
    ac = _bounds(glyf, 'acutecomb'); acx = (ac[0] + ac[2]) / 2
    di = _bounds(glyf, 'uni0308'); dix = (di[0] + di[2]) / 2
    tonos_ref = _bounds(comm.at(w_lc)['glyf'], 'tonos'); tonos_cx = (tonos_ref[0] + tonos_ref[2]) / 2
    dier_ref = _bounds(comm.at(w_lc)['glyf'], 'uni0308'); dier_cx = (dier_ref[0] + dier_ref[2]) / 2

    def mark_x(comp_name, mark_ref, mark_cx_ref, base_src):
        """Where Commissioner centres this mark over the base, in Torchlette units of the fitted base."""
        g = L.glyf[comp_name]
        off = next((c.x for c in g.components if c.glyphName == mark_ref), None) if g.isComposite() else None
        if off is None:                                   # not a composite: centre on the base's ink
            b = _bounds(L.glyf, base_src); cx_ref = (b[0] + b[2]) / 2
        else: cx_ref = mark_cx_ref + off
        return cx_ref

    def fitted_x(cx_ref, src, name):
        """A reference x over src, carried to the fitted glyph `name`."""
        b = _bounds(L.glyf, src); nb_ = _bounds(glyf, name)
        return nb_[0] + (cx_ref - b[0]) * L.sx

    # the dialytika-tonos (U+0385, spacing; the module adds no combining marks, so ΐ and
    # ΰ are composites of it): uni0308's two dots and a scaled acute, laid out as
    # Commissioner lays out its dieresistonos.narrow at the lowercase weight. Each part's
    # centre is carried over by the ratio of the two fonts' dieresis widths (x) and dot
    # heights (y), and the tonos is scaled to Commissioner's tonos/dot height ratio, so
    # the group widens and tightens with the weight as Commissioner's does.
    cg = comm.at(w_lc)['glyf']
    c_parts = sorted((_draw([c], lambda x: x, lambda y: y).bounds for c in _contours(cg, 'dieresistonos.narrow')),
                     key=lambda b: b[3] - b[1])
    assert len(c_parts) == 3, f'dieresistonos.narrow has {len(c_parts)} contours, not two dots and a tonos'
    c_tonos = c_parts[-1]; c_dots = sorted(c_parts[:2])            # the tonos is the tallest part
    c_di = _bounds(cg, 'uni0308')
    dpath = ctx.path_of('uni0308')
    left = ctx.clip(dpath, (-1000, -1000, dix, 2000)); right = ctx.clip(dpath, (dix, -1000, 2000, 2000))
    lb, rb = left.bounds, right.bounds
    kx = (di[2] - di[0]) / (c_di[2] - c_di[0])
    ky = (lb[3] - lb[1]) / (c_dots[0][3] - c_dots[0][1])
    c_cx = (c_dots[0][0] + c_dots[1][2]) / 2                       # the dots' midpoint, Commissioner
    c_y0 = c_dots[0][1]
    cx_of = lambda b: (b[0] + b[2]) / 2
    TK = (c_tonos[3] - c_tonos[1]) * ky / (ac[3] - ac[1])        # the acute at Commissioner's tonos/dot height ratio
    tpath = ctx.transformed(ctx.path_of('acutecomb'), (TK, 0, 0, TK, 0, 0)); tb = tpath.bounds
    t_dx = (cx_of(c_tonos) - c_cx) * kx - cx_of(tb)
    t_dy = lb[1] + (c_tonos[1] - c_y0) * ky - tb[1]
    tonos = ctx.transformed(tpath, (1, 0, 0, 1, t_dx, t_dy))
    dl = (cx_of(c_dots[0]) - c_cx) * kx - cx_of(lb); dr = (cx_of(c_dots[1]) - c_cx) * kx - cx_of(rb)
    # Torchlette's acute is broader than Commissioner's tonos, so carried over it can run
    # into a dot: each dot then moves out until it clears the tonos by Commissioner's
    # clearance (the least tonos-dot distance there), scaled.
    c_paths = sorted((_draw([c], lambda x: x, lambda y: y) for c in _contours(cg, 'dieresistonos.narrow')),
                     key=lambda q: q.bounds[3] - q.bounds[1])
    CLEAR = min(_clearance(c_paths[-1], q) for q in c_paths[:2]) * kx
    pushed = []
    for side, sgn in ((left, -1), (right, 1)):
        d0 = dl if sgn < 0 else dr
        at = lambda e: ctx.transformed(side, (1, 0, 0, 1, d0 + sgn * e, 0))
        e = 0.0
        if _clearance(tonos, at(0)) < CLEAR - 0.5:
            lo, hi = 0.0, 200.0
            while hi - lo > 0.5:
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if _clearance(tonos, at(mid)) < CLEAR - 0.5 else (lo, mid)
            e = hi
        pushed.append(e)
        if sgn < 0: dl = d0 - e
        else: dr = d0 + e
    parts = [ctx.transformed(left, (1, 0, 0, 1, dl, 0)), ctx.transformed(right, (1, 0, 0, 1, dr, 0)), tonos]
    dt0 = ctx.union(*parts); b0 = dt0.bounds
    DT_ADV = max(500, round(b0[2] - b0[0]) + 40)                   # spaced like acute (500), or wider in the heavy weights
    dt = ctx.transformed(dt0, (1, 0, 0, 1, DT_ADV / 2 - (b0[0] + b0[2]) / 2, 0))   # centred on its advance
    ctx.greek_dt = {'TK': round(TK, 3), 'width': round(b0[2] - b0[0]), 'dieresis': round(di[2] - di[0]),
                    'contours': len(list(dt.contours))}
    base('uni0385', dt, DT_ADV); ctx.map(0x0385, 'uni0385')
    dtx = DT_ADV / 2 - (b0[0] + b0[2]) / 2 + (dl + cx_of(lb) + dr + cx_of(rb)) / 2   # the dots' midpoint, where ΐ and ΰ centre it
    ctx.log(f'dialytika-tonos: tonos at {TK:.3f} of the acute, clearance {CLEAR:.0f} (dots pushed out {pushed[0]:.0f}, {pushed[1]:.0f}), '
            f'{b0[2] - b0[0]:.0f} wide over a {di[2] - di[0]:.0f} dieresis')

    for name, bname, comp, uni in LC_TONOS:
        base_src = {'alpha': 'alpha', 'epsilon': 'epsilon', 'eta': 'eta', 'iota': 'iota', 'omicron': 'o', 'upsilon': 'upsilon', 'omega': 'omega'}[bname]
        cx = fitted_x(mark_x(comp, 'tonos', tonos_cx, base_src), base_src, bname)
        composite(name, [(bname, 0, 0), ('acutecomb', cx - acx, 0)], hmtx[bname][0]); ctx.map(uni, name)
    for name, bname, comp, uni in LC_DIER:
        cx = fitted_x(mark_x(comp, 'uni0308', dier_cx, bname), bname, bname)
        composite(name, [(bname, 0, 0), ('uni0308', cx - dix, 0)], hmtx[bname][0]); ctx.map(uni, name)
    for name, bname, comp, uni in LC_BOTH:
        cx = fitted_x(mark_x(comp, 'uni0308', dier_cx, bname), bname, bname)
        composite(name, [(bname, 0, 0), ('uni0385', cx - dtx, 0)], hmtx[bname][0]); ctx.map(uni, name)

    # capital tonos: Torchlette's acute, its top at cap height, left of the letter by a
    # gap of Commissioner's (scaled); the letter moves right when the tonos would reach
    # further left than Commissioner lets it (a small overhang into the previous glyph)
    E_ref = U.glyf['Epsilontonos']
    e_base = next(c for c in E_ref.components if c.glyphName == 'E'); e_mark = next(c for c in E_ref.components if c.glyphName != 'E')
    tc_ref = _bounds(U.glyf, e_mark.glyphName); eb_ref = _bounds(U.glyf, 'E')
    GAP = ((eb_ref[0] + e_base.x) - (tc_ref[2] + e_mark.x)) * cap_scale
    OVER = (tc_ref[0] + e_mark.x) * cap_scale                      # the tonos's left edge, negative
    dy_cap = CAP_T - ac[3]
    for name, bname, uni in UC_TONOS:
        bp = ctx.path_of(bname)
        band = [s for y in (ac[1] + dy_cap + 5, (ac[1] + ac[3]) / 2 + dy_cap, ac[3] + dy_cap - 5) for s in _spans(bp, y=y)[:1]]
        left_ink = min(s[0] for s in band)
        t_right = left_ink - GAP; t_left = t_right - (ac[2] - ac[0])
        shift = max(0, OVER - t_left)
        t_left += shift
        composite(name, [(bname, shift, 0), ('acutecomb', t_left - ac[0], dy_cap)], hmtx[bname][0] + shift); ctx.map(uni, name)
    composite('Iotadieresis', [('Idieresis', 0, 0)], hmtx['Idieresis'][0]); ctx.map(0x03AA, 'Iotadieresis')
    composite('Upsilondieresis', [('Ydieresis', 0, 0)], hmtx['Ydieresis'][0]); ctx.map(0x03AB, 'Upsilondieresis')

    # spacing marks and punctuation
    composite('uni0384', [('acutecomb', 250 - acx, 0)], 500); ctx.map(0x0384, 'uni0384')          # tonos, spaced like acute
    composite('uni037E', [('semicolon', 0, 0)], hmtx['semicolon'][0]); ctx.map(0x037E, 'uni037E')  # Greek question mark
    composite('uni0387', [('periodcentered', 0, 0)], hmtx['periodcentered'][0]); ctx.map(0x0387, 'uni0387')  # ano teleia
    mb = _bounds(glyf, 'minute')
    composite('uni0374', [('minute', 0, 0)], hmtx['minute'][0]); ctx.map(0x0374, 'uni0374')        # numeral sign
    lo_ref = _bounds(U.glyf, 'uni0375')
    composite('uni0375', [('minute', 0, round(lo_ref[3] * cap_scale) - mb[3])], hmtx['minute'][0]); ctx.map(0x0375, 'uni0375')

    # --- small capitals --------------------------------------------------------------
    for src, name in (('uni0394', 'delta.sc.greek'), ('uni03A9', 'omega.sc.greek')):
        base(name, ctx.sc_path(src), round(ctx.sc_font['hmtx'][src][0] * ctx.SC_SCALE + 2 * ctx.SC_TRACK))
        ctx.sc_respace(name)
    for name, (fn, args) in [('gamma.sc.greek', (gamma_from, ('F.sc',))), ('pi.sc.greek', (pi_from, ('H.sc', 'T.sc'))),
                             ('xi.sc.greek', (xi_from, ('E.sc', XI_K))), ('lambda.sc.greek', (lambda_from, ('A.sc',))),
                             ('theta.sc.greek', (theta_from, ('O.sc', THETA_BAR)))]:
        p, adv = fn(*args); base(name, p, adv)
    for src, name, _, sbkey in CAPS_REF:
        p, adv = S.place(src, None, sc_scale, ksb_sc, sy=sc_scale)
        base(name.lower() + '.sc.greek', p, adv)
    # accented small capitals: the small cap with Torchlette's acute above it
    for sc_name, sc_base in (('alphatonos.sc.greek', 'A.sc'), ('epsilontonos.sc.greek', 'E.sc'), ('etatonos.sc.greek', 'H.sc'),
                             ('iotatonos.sc.greek', 'I.sc'), ('omicrontonos.sc.greek', 'O.sc'), ('upsilontonos.sc.greek', 'Y.sc'),
                             ('omegatonos.sc.greek', 'omega.sc.greek')):
        b = _bounds(glyf, sc_base)
        composite(sc_name, [(sc_base, 0, 0), ('acutecomb', (b[0] + b[2]) / 2 - acx, 0)], hmtx[sc_base][0])

    # --- kerning: Commissioner's Greek pairs at the lowercase weight, scaled ------------
    ref_to_t = {src: name for src, name, _, _ in LOWER}
    ref_to_t.update({'Sigma': 'Sigma', 'Phi': 'Phi', 'Psi': 'Psi', 'omicron': 'omicron', 'uni03BC': 'uni03BC', 'pi': 'pi',
                     'uni0394': 'uni0394', 'uni03A9': 'uni03A9', 'Gamma': 'Gamma', 'Pi': 'Pi', 'Xi': 'Xi', 'Lambda': 'Lambda', 'Theta': 'Theta'})
    ref_to_t.update({n: n for n, _, _ in CAPS_LATIN})
    ref_to_t.update({n: n for n in KERN_PUNCT if n in glyf.glyphs})
    pairs = _pair_kerning(L.f, set(ref_to_t))
    kern = {}
    for (a, b), v in pairs.items():
        ta, tb = ref_to_t[a], ref_to_t[b]
        if ta in KERN_PUNCT and tb in KERN_PUNCT: continue
        k = round(v * L.sx)
        if abs(k) >= KERN_MIN: kern[ta, tb] = k
    ctx.greek_kern = kern
    ctx.log(f'{len(made)} glyphs; {len(kern)} kerning pairs from Commissioner')


def features(ctx):
    smcp = {
        'alpha': 'A.sc', 'beta': 'B.sc', 'gamma': 'gamma.sc.greek', 'delta': 'delta.sc.greek', 'epsilon': 'E.sc', 'zeta': 'Z.sc',
        'eta': 'H.sc', 'theta': 'theta.sc.greek', 'iota': 'I.sc', 'kappa': 'K.sc', 'lambda': 'lambda.sc.greek', 'uni03BC': 'M.sc',
        'nu': 'N.sc', 'xi': 'xi.sc.greek', 'omicron': 'O.sc', 'pi': 'pi.sc.greek', 'rho': 'P.sc', 'sigma': 'sigma.sc.greek',
        'sigma1': 'sigma.sc.greek', 'tau': 'T.sc', 'upsilon': 'Y.sc', 'phi': 'phi.sc.greek', 'chi': 'X.sc', 'psi': 'psi.sc.greek',
        'omega': 'omega.sc.greek',
        'alphatonos': 'alphatonos.sc.greek', 'epsilontonos': 'epsilontonos.sc.greek', 'etatonos': 'etatonos.sc.greek',
        'iotatonos': 'iotatonos.sc.greek', 'omicrontonos': 'omicrontonos.sc.greek', 'upsilontonos': 'upsilontonos.sc.greek',
        'omegatonos': 'omegatonos.sc.greek', 'iotadieresis': 'Idieresis.sc', 'upsilondieresis': 'Ydieresis.sc',
        'iotadieresistonos': 'Idieresis.sc', 'upsilondieresistonos': 'Ydieresis.sc',
    }
    c2sc = {
        'Alpha': 'A.sc', 'Beta': 'B.sc', 'Gamma': 'gamma.sc.greek', 'uni0394': 'delta.sc.greek', 'Epsilon': 'E.sc', 'Zeta': 'Z.sc',
        'Eta': 'H.sc', 'Theta': 'theta.sc.greek', 'Iota': 'I.sc', 'Kappa': 'K.sc', 'Lambda': 'lambda.sc.greek', 'Mu': 'M.sc',
        'Nu': 'N.sc', 'Xi': 'xi.sc.greek', 'Omicron': 'O.sc', 'Pi': 'pi.sc.greek', 'Rho': 'P.sc', 'Sigma': 'sigma.sc.greek',
        'Tau': 'T.sc', 'Upsilon': 'Y.sc', 'Phi': 'phi.sc.greek', 'Chi': 'X.sc', 'Psi': 'psi.sc.greek', 'uni03A9': 'omega.sc.greek',
        'Alphatonos': 'alphatonos.sc.greek', 'Epsilontonos': 'epsilontonos.sc.greek', 'Etatonos': 'etatonos.sc.greek',
        'Iotatonos': 'iotatonos.sc.greek', 'Omicrontonos': 'omicrontonos.sc.greek', 'Upsilontonos': 'upsilontonos.sc.greek',
        'Omegatonos': 'omegatonos.sc.greek', 'Iotadieresis': 'Idieresis.sc', 'Upsilondieresis': 'Ydieresis.sc',
    }
    have = set(ctx.font.getGlyphOrder())
    missing = [g for m in (smcp, c2sc) for pair in m.items() for g in pair if g not in have]
    if missing: raise SystemExit(f'greek: small-cap feature names glyphs the font lacks: {sorted(set(missing))}')
    rules = lambda m: ''.join(f'    sub {a} by {b};\n' for a, b in m.items())
    ctx.gsub(f'feature smcp {{\n  lookup GREEK_SMCP {{\n{rules(smcp)}  }} GREEK_SMCP;\n}} smcp;\n\n'
             f'feature c2sc {{\n  lookup GREEK_C2SC {{\n{rules(c2sc)}  }} GREEK_C2SC;\n}} c2sc;\n', before='main')
    kern = getattr(ctx, 'greek_kern', {})
    if kern:
        lines = ''.join(f'    pos {a} {b} {v};\n' for (a, b), v in sorted(kern.items()))
        ctx.gpos(f'feature kern {{\n  lookup GREEK_KERN {{\n{lines}  }} GREEK_KERN;\n}} kern;\n')

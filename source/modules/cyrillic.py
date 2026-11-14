"""cyrillic: Cyrillic small capitals, mark anchors, small-cap kerning, and cross-script kerning.

Mulish ships 236 Cyrillic code points (118 bicameral uppercase/lowercase pairs across
U+0400..U+04FF and U+0510..U+052F) plus localized Bashkir (`BSH `) and Chuvash (`CHU `)
forms, with zero Cyrillic small capitals (`smcp` / `c2sc`), missing `mark` base anchors
on 87 Cyrillic letters (including Russian `Ю`, `ю`, `Я`, `я` and Ukrainian `є`), and
zero cross-script Latin<->Cyrillic letter kerning (`A` + `Т` = 0).

What this module adds (owned glyphs suffixed `.cyrillic`, lookups/classes prefixed `CYRILLIC_`):

1. `glyphs(ctx)`:
   Builds 122 weight-compensated 550-unit small capitals (`<cap>.sc.cyrillic` for all
   118 `cmap` Cyrillic capitals and 4 distinct Bashkir/Chuvash `locl` capitals):
   - Capitals that alias a single Latin capital (`А`, `В`, `Е`, `О`, `С`, `Т`, etc.)
     reference Torchlette's finished `<lat>.sc` (inheriting `ROUND_UC` widening on
     `О`, `С`, `Ԛ` and exact stem/sidebearing parity).
   - Native simple and overlay-stroke capitals (`Б`, `Г`, `Д`, `Ж`, `И`, `К`, `Л`,
     `П`, `У`, `Ф`, `Ц`, `Ч`, `Ш`, `Щ`, `Ъ`, `Ы`, `Ь`, `Э`, `Ю`, `Я`, `Ђ`, `Ћ`, `Љ`,
     `Њ`, `Џ`, `Ұ`, `Ӿ`, etc.) are drawn from `ctx.sc_font` (`SC_WGHT`) at `SC_SCALE`
     (`SC_H = 550`) with `round_dots=True` and `ctx.sc_respace`.
   - `Ҋ` (`uni048A`, whose Mulish capital bakes in a `.case` breve contour) strips the
     baked-in `.case` breve and attaches Torchlette's lowercase `brevecombcy` raised by
     `SC_H - XH`, matching `Й` (`uni0419.sc.cyrillic`) in weight and height.
   - Precomposed accented capitals (`Ё`, `Й`, `Ї`, `Ў`, `Ѓ`, `Ќ`, `Ѐ`, `Ѝ`, `Ӣ`, `Ӯ`,
     `Ӑ`, `Ӓ`, `Ӗ`, `Ӛ`, `Ӝ`, `Ӟ`, `Ӥ`, `Ӧ`, `Ӫ`, `Ӭ`, `Ӱ`, `Ӳ`, `Ӵ`, `Ӹ`, `Ҿ`, etc.)
     are built as flat (depth-1, non-nested) composites of the small-cap base and the
     lowercase mark raised by `SC_H - XH` (with `build.py`'s `mark_anchor_x` italic
     offset correction).
   - Every added glyph gets `GDEF` class 1 (base glyph).

2. `features(ctx)`:
   - `GSUB` (`before='main'`, moved to the front of `GSUB` by `build.py`):
     `CYRILLIC_SMCP` (lowercase + `locl` lowercase -> `.sc.cyrillic`),
     `CYRILLIC_C2SC` (uppercase + `locl` uppercase -> `.sc.cyrillic`), and
     `CYRILLIC_C2SC_MARK` (reverts `.case` combining marks applied by `ccmp` after
     capitals back to lowercase marks on `.sc.cyrillic` bases, so `А́` under `c2sc`
     matches `а́` under `smcp`).
   - `GPOS` `mark` (`before='mulish'`):
     `CYRILLIC_MARK` attaches Mulish's 6 combining mark classes (`@CYRILLIC_M0`..`M5`)
     to all 122 `.sc.cyrillic` bases and to the 87 Cyrillic `cmap` letters Mulish left
     out of its `mark` table (`Ю`, `ю`, `Я`, `я`, `є`, etc.).
   - `GPOS` `kern`:
     `CYRILLIC_SC_KERN` carries `sc_font`'s Cyrillic capital kerning (`SC_SCALE * SC_K`)
     onto `.sc.cyrillic` pairs (with `.sc.cyrillic`, Latin `.sc`, `.sc` symbols, and
     plain punctuation) in a single conflict-free Format-2 subtable (zero masked pairs).
     `CYRILLIC_CROSS_KERN` bridges Mulish's separate Latin and Cyrillic kerning classes
     across script boundaries (`A`+`Т`, `Т`+`A`, `V`+`Д`, `T`+`о`, `Г`+`o`, etc.) in a
     single conflict-free Format-2 subtable without touching tabular figures. The Latin
     letters are those in Mulish's classes up to U+036F and in Latin Extended Additional
     (U+1E00-1EFF: the Vietnamese ụ ủ ứ ọ ẹ ...).
     `CYRILLIC_PUNCT_KERN` kerns Г Ѓ Ґ Ғ (right side, as T) and У Ў Ӯ Ӱ Ӳ (both sides,
     as Y) against the punctuation their Latin model kerns with (Г. Г, Г» У. «У ...),
     scaled by the open space beside each mark (see `_build_punct_kern`).

3. `post(ctx)`:
   Verifies against the compiled `GPOS` table that zero kerning pairs in
   `CYRILLIC_SC_KERN` or `CYRILLIC_CROSS_KERN` are masked.
"""
from array import array
from collections import defaultdict
import math
import unicodedata

from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent, GlyphCoordinates

SUF = '.sc.cyrillic'

LOCL_PAIRS = [
    # (lowercase_locl, uppercase_locl, target_cap_stem)
    ('uni0456.loclBSH', 'uni0406.loclBSH', 'uni0406.loclBSH'),
    ('uni0493.loclBSH', 'uni0492.loclBSH', 'uni0492.loclBSH'),
    ('uni0499.loclBSH', 'uni0498.loclBSH', 'uni0498'),
    ('uni04AB.loclBSH', 'uni04AA.loclBSH', 'uni04AA'),
    ('uni0499.loclCHU', 'uni0498.loclCHU', 'uni0498.loclCHU'),
    ('uni04AB.loclCHU', 'uni04AA.loclCHU', 'uni04AA.loclCHU'),
]

DIGITS = 'zero one two three four five six seven eight nine'.split()
TABULAR = set(
    DIGITS
    + [d + '.tosf' for d in DIGITS]
    + [d + '.sc.tf' for d in DIGITS]
    + ['seven.ss08', 'seven.tosf.ss08', 'seven.sc.tf.ss08']
)


def _is_cyr_codepoint(u):
    return 0x0400 <= u <= 0x052F


def _is_cyr_glyph(g):
    stem = g.split('.')[0]
    return stem.startswith(('uni04', 'uni05')) or g.endswith('.cyrillic')


def _make_composite(ctx, name, parts, width):
    """Build a flat (depth-1, never nested) composite glyph and register it in glyf/hmtx."""
    glyf, hmtx, font = ctx.glyf, ctx.hmtx, ctx.font
    flat = []
    for gn, dx, dy in parts:
        sub = glyf[gn]
        if sub.isComposite():
            for c in sub.components:
                flat.append((c.glyphName, dx + c.x, dy + c.y))
        else:
            flat.append((gn, dx, dy))
    new = Glyph()
    new.numberOfContours = -1
    new.components = []
    for gn, x, y in flat:
        gc = GlyphComponent()
        gc.glyphName, gc.x, gc.y, gc.flags = gn, int(round(x)), int(round(y)), 0x4
        new.components.append(gc)
    glyf[name] = new
    if name not in font.getGlyphOrder():
        font.setGlyphOrder(font.getGlyphOrder() + [name])
    new.recalcBounds(glyf)
    hmtx[name] = (int(round(width)), getattr(new, 'xMin', 0))


# ================================================================ phase 1: glyphs
def glyphs(ctx):
    glyf, font = ctx.glyf, ctx.font
    cmap = font.getBestCmap()

    pairs = []  # (low_glyph, cap_glyph, sc_glyph)
    caps_to_build = []
    for u, cap in sorted(cmap.items()):
        if not (_is_cyr_codepoint(u) and unicodedata.category(chr(u)) == 'Lu'):
            continue
        low_ch = chr(u).lower()
        low = cmap.get(ord(low_ch)) if len(low_ch) == 1 else None
        if low == cap:
            low = None
        sc = cap + SUF
        pairs.append((low, cap, sc))
        caps_to_build.append(cap)

    for low_l, cap_l, stem in LOCL_PAIRS:
        if low_l in glyf.glyphs and cap_l in glyf.glyphs:
            sc = stem + SUF
            pairs.append((low_l, cap_l, sc))
            if stem not in caps_to_build:
                caps_to_build.append(stem)

    made = []

    def register(sc_name):
        ctx.GDEF_CLASS[sc_name] = 1
        made.append(sc_name)

    # Pass 1: Latin-sc single-component aliases, simple outlines, and overlay-stroke capitals
    deferred_cyr_alias = []
    deferred_mark_comp = []
    for cap in caps_to_build:
        sc = cap + SUF
        g = glyf[cap]
        if g.isComposite() and len(g.components) == 1 and g.components[0].y == 0:
            tgt = g.components[0].glyphName
            if tgt + '.sc' in glyf.glyphs:
                _make_composite(ctx, sc, [(tgt + '.sc', 0, 0)], ctx.W(tgt + '.sc'))
                register(sc)
            else:
                deferred_cyr_alias.append((cap, tgt))
        elif g.isComposite() and not any('0335' in c.glyphName for c in g.components[1:]):
            deferred_mark_comp.append(cap)
        elif cap == 'uni048A':
            # Mulish's U+048A (Ҋ) bakes in a .case breve contour above y=720; strip that
            # contour here and attach Torchlette's lowercase brevecombcy in Pass 4 so Ҋ.sc
            # matches Й.sc in breve height and stroke weight.
            p = ctx.clip(ctx.sc_path(cap, round_dots=True), (-1000, -1000, 4000, ctx.SC_H + 15))
            ctx.add(sc, p, ctx.sc_font['hmtx'][cap][0] * ctx.SC_SCALE + 2 * ctx.SC_TRACK)
            ctx.sc_respace(sc)
            register(sc)
        else:
            ctx.add(sc, ctx.sc_path(cap, round_dots=True), ctx.sc_font['hmtx'][cap][0] * ctx.SC_SCALE + 2 * ctx.SC_TRACK)
            ctx.sc_respace(sc)
            register(sc)

    # Pass 2: Cyrillic-to-Cyrillic single-component aliases (e.g. U+0472 Ѳ -> U+04E8 Ө)
    for cap, tgt in deferred_cyr_alias:
        sc = cap + SUF
        tgt_sc = tgt + SUF
        _make_composite(ctx, sc, [(tgt_sc, 0, 0)], ctx.W(tgt_sc))
        register(sc)

    # Pass 3: Base + combining-mark composites (top marks raised by SC_H - XH, bottom marks at 0)
    for cap in deferred_mark_comp:
        sc = cap + SUF
        g = glyf[cap]
        b0 = g.components[0].glyphName
        b_sc = (b0 + SUF) if (b0 + SUF) in glyf.glyphs else (b0 + '.sc')
        cx0, cx1 = ctx.ink(b0)
        sx0, sx1 = ctx.ink(b_sc)
        comps = []
        ok = True
        for c in g.components[1:]:
            m = c.glyphName.split('.case')[0]
            if m not in glyf.glyphs:
                ok = False
                break
            mg = glyf[m]
            mg.recalcBounds(glyf)
            if mg.yMin >= 300:
                dy = ctx.SC_H - ctx.XH
            elif mg.yMax <= 60:
                dy = 0
            else:
                ok = False
                break
            x_sc = round((sx0 + sx1) / 2 + (c.x - (cx0 + cx1) / 2) * ctx.SC_SCALE)
            if ctx.ITALIC:
                x_sc = round(
                    (sx0 + sx1) / 2
                    + (c.x + ctx.mark_anchor_x(c.glyphName) - (cx0 + cx1) / 2) * ctx.SC_SCALE
                    - ctx.mark_anchor_x(m)
                )
            comps.append((m, x_sc, dy + round(c.y * ctx.SC_SCALE)))
        if ok:
            _make_composite(ctx, sc, [(b_sc, 0, 0)] + comps, ctx.W(b_sc))
        else:
            ctx.add(sc, ctx.sc_path(cap, round_dots=True), ctx.sc_font['hmtx'][cap][0] * ctx.SC_SCALE + 2 * ctx.SC_TRACK)
            ctx.sc_respace(sc)
        register(sc)

    # Pass 4: Attach lowercase brevecombcy to uni048A.sc.cyrillic matching uni0419.sc.cyrillic
    if 'uni048A' + SUF in glyf.glyphs and 'uni0419' + SUF in glyf.glyphs and glyf['uni0419' + SUF].isComposite():
        j_sc = 'uni048A' + SUF
        i_sc = 'uni0418' + SUF
        mc = glyf['uni0419' + SUF].components[-1]
        dx = mc.x + round(ctx.ink(j_sc)[0] - ctx.ink(i_sc)[0])
        dy = mc.y
        merged = ctx.union(ctx.path_of(j_sc), ctx.path_of(mc.glyphName, dx=dx, dy=dy))
        ctx.add(j_sc, merged, ctx.W(j_sc))

    ctx.cyr_pairs = pairs
    ctx.cyr_sc_glyphs = made
    ctx.log(f'{len(made)} small-cap glyphs built ({len(pairs)} bicameral/locl pairs)')


# ================================================================ GPOS mark helpers
TOP, TOPR, BOT, OGON, ASC, OVER = 0, 1, 2, 3, 4, 5


def _mark_data(font):
    marks, bases, mk2 = {}, {}, {}
    if 'GPOS' not in font:
        return marks, bases, mk2
    for lk in font['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable:
            t = lk.LookupType
            if t == 9:
                st = st.ExtSubTable
                t = st.LookupType
            if t == 4:
                for g, r in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord):
                    marks[g] = (r.Class, (r.MarkAnchor.XCoordinate, r.MarkAnchor.YCoordinate))
                for g, r in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                    bases[g] = {c: (a.XCoordinate, a.YCoordinate) for c, a in enumerate(r.BaseAnchor) if a}
            elif t == 6:
                for g, r in zip(st.Mark2Coverage.glyphs, st.Mark2Array.Mark2Record):
                    a = r.Mark2Anchor[0]
                    if a:
                        mk2[g] = (a.XCoordinate, a.YCoordinate)
    return marks, bases, mk2


def _onpts(ctx, n):
    c, _, fl = ctx.glyf[n].getCoordinates(ctx.glyf)
    return [(tuple(q), bool(f & 1)) for q, f in zip(c, fl)]


def _band_mid(ctx, p, y0, y1):
    b = ctx.clip(p, (-3000, y0, 5000, y1)).bounds
    return None if b is None or b == (0, 0, 0, 0) else (b[0] + b[2]) / 2


def _flat_top(ctx, n, p):
    x0, y0, x1, y1 = p.bounds
    top = [on for (q, on) in _onpts(ctx, n) if abs(q[1] - y1) < 0.5] if not ctx.glyf[n].isComposite() else [True, True]
    rnd = (not all(top)) or len(top) < 2
    return y1 - (round(0.013 * (y1 - min(y0, 0))) if rnd else 0)


def _geometric_anchors(ctx, n, is_cap=False):
    p = ctx.path_of(n)
    x0, y0, x1, y1 = p.bounds
    h = y1 - min(y0, 0)
    ft = _flat_top(ctx, n, p)
    # Capitals take .case marks (anchor y=705 -> ft); lowercase & small caps take plain marks (anchor y=454 -> ft - 16)
    top_y = ft if is_cap else ft - 16
    out = {TOP: (_band_mid(ctx, p, y1 - 0.2 * h, y1 + 1), top_y)}
    yb = 0 if y0 > -30 else y0
    out[BOT] = (_band_mid(ctx, p, y0 - 1, y0 + 0.2 * h), yb)
    out[OVER] = (_band_mid(ctx, p, ft / 2 - 0.1 * h, ft / 2 + 0.1 * h), ft / 2)
    return {c: (round(a[0]), round(a[1])) for c, a in out.items() if a[0] is not None}


def _from_capital_anchors(ctx, sc, cap, mbases):
    cx0, cx1 = ctx.ink(cap)
    sx0, sx1 = ctx.ink(sc)
    S = ctx.SC_SCALE
    out = {}
    for c, (x, y) in mbases[cap].items():
        x2 = round((sx0 + sx1) / 2 + (x - (cx0 + cx1) / 2) * S)
        if c == TOP:
            y2 = 454 + (ctx.SC_H - ctx.XH) + round((y - 705) * S)
        elif c == TOPR:
            y2 = ctx.SC_H + round((y - 705) * S)
        else:
            y2 = round(y * S)
        out[c] = (x2, y2)
    for c, a in _geometric_anchors(ctx, sc, is_cap=False).items():
        out.setdefault(c, a)
    return out


def _stack_delta(ctx, mbases, marks, mk2):
    d = {TOP: [], BOT: []}
    for n, anc in mbases.items():
        g = ctx.glyf[n]
        if not g.isComposite() or len(g.components) != 2:
            continue
        m = g.components[1]
        if m.glyphName not in mk2 or m.glyphName not in marks:
            continue
        cls = marks[m.glyphName][0]
        k = TOP if cls in (TOP, TOPR) else BOT if cls in (BOT, OGON) else None
        if k is None or k not in anc:
            continue
        d[k].append(anc[k][1] - (m.y + mk2[m.glyphName][1]))
    med = lambda v: sorted(v)[len(v) // 2] if v else 0
    return {k: med(v) for k, v in d.items()}


def _build_mark_fea(ctx):
    marks, mbases, mk2 = _mark_data(ctx.font)
    if not marks:
        return ''
    delta = _stack_delta(ctx, mbases, marks, mk2)
    cmap = ctx.font.getBestCmap()

    # Learn exact offsets from our precomposed .sc.cyrillic composites
    learned = {}
    for sc in ctx.cyr_sc_glyphs:
        g = ctx.glyf[sc]
        if not g.isComposite() or len(g.components) != 2:
            continue
        b, m = g.components
        if m.glyphName not in marks or m.glyphName.endswith('.case'):
            continue
        c, (mx, my) = marks[m.glyphName]
        learned.setdefault(b.glyphName, {}).setdefault(c, []).append((m.x + mx, m.y + my))
    med = lambda v: sorted(v)[len(v) // 2]

    resolved = {}

    def resolve_sc(sc):
        if sc in resolved:
            return resolved[sc]
        cap = sc[:-len(SUF)]
        g = ctx.glyf[sc]
        if g.isComposite() and len(g.components) == 1:
            b0 = g.components[0].glyphName
            if b0.endswith('.sc') and b0[:-3] in mbases:
                r = _from_capital_anchors(ctx, sc, b0[:-3], mbases)
            elif b0 in resolved or b0.endswith(SUF):
                r = dict(resolve_sc(b0))
            else:
                r = _geometric_anchors(ctx, sc, is_cap=False)
        elif g.isComposite() and len(g.components) > 1 and all(c.glyphName in marks for c in g.components[1:]):
            b0 = g.components[0].glyphName
            if b0.endswith(SUF):
                ba = dict(resolve_sc(b0))
            elif b0.endswith('.sc') and b0[:-3] in mbases:
                ba = _from_capital_anchors(ctx, b0, b0[:-3], mbases)
            else:
                ba = _geometric_anchors(ctx, b0, is_cap=False)
            if b0 in learned:
                for c, pts in learned[b0].items():
                    ba[c] = (med([p[0] for p in pts]), med([p[1] for p in pts]))
            r = {c: (x + g.components[0].x, y + g.components[0].y) for c, (x, y) in ba.items()}
            for m in g.components[1:]:
                cls = marks[m.glyphName][0]
                k = TOP if cls in (TOP, TOPR) else BOT if cls in (BOT, OGON) else None
                if k is not None and m.glyphName in mk2:
                    r[k] = (m.x + mk2[m.glyphName][0], m.y + mk2[m.glyphName][1] + delta[k])
        elif cap == 'uni048A':
            # Base И with tail + unioned brevecombcy: raise TOP above the breve
            ba = _from_capital_anchors(ctx, sc, 'uni0418', mbases) if 'uni0418' in mbases else _geometric_anchors(ctx, sc, is_cap=False)
            r = dict(ba)
            if 'brevecombcy' in mk2 and 'uni0419' + SUF in ctx.glyf and ctx.glyf['uni0419' + SUF].isComposite():
                mc = ctx.glyf['uni0419' + SUF].components[-1]
                r[TOP] = (ba[TOP][0], mc.y + mk2['brevecombcy'][1] + delta[TOP])
        elif cap in mbases:
            r = _from_capital_anchors(ctx, sc, cap, mbases)
        else:
            r = _geometric_anchors(ctx, sc, is_cap=False)
        if sc in learned:
            r = dict(r)
            for c, pts in learned[sc].items():
                r[c] = (med([p[0] for p in pts]), med([p[1] for p in pts]))
        resolved[sc] = r
        return r

    bases_out = {}
    for sc in ctx.cyr_sc_glyphs:
        bases_out[sc] = resolve_sc(sc)

    # Also supply anchors for Cyrillic cmap letters Mulish omitted (e.g. Ю, ю, Я, я, є)
    for u, g in sorted(cmap.items()):
        if not _is_cyr_codepoint(u) or g in mbases or g in bases_out:
            continue
        cat = unicodedata.category(chr(u))
        if cat in ('Lu', 'Ll'):
            bases_out[g] = _geometric_anchors(ctx, g, is_cap=(cat == 'Lu'))

    classes = sorted({c for c, _ in marks.values()})
    lines = [f'markClass {m} <anchor {a[0]} {a[1]}> @CYRILLIC_M{c};' for m, (c, a) in marks.items()]
    lines.append('lookup CYRILLIC_MARK {')
    for g, a in bases_out.items():
        body = ' '.join(f'<anchor {a[c][0]} {a[c][1]}> mark @CYRILLIC_M{c}' for c in classes if c in a)
        if body:
            lines.append(f'  pos base {g} {body};')
    lines.append('} CYRILLIC_MARK;')
    lines.append('feature mark { lookup CYRILLIC_MARK; } mark;\n')
    ctx.cyr_mark_bases = len(bases_out)
    return '\n'.join(lines)


# ================================================================ GPOS kern helpers
def _xa(v):
    return (getattr(v, 'XAdvance', 0) or 0) if v else 0


def _subtables(lk):
    return [s.ExtSubTable if lk.LookupType == 9 else s for s in lk.SubTable]


def _lookup_pairs(lk):
    eff, seen = {}, set()
    for st in _subtables(lk):
        if st.Format == 1:
            for a, ps in zip(st.Coverage.glyphs, st.PairSet):
                for r in ps.PairValueRecord:
                    k = (a, r.SecondGlyph)
                    if k not in seen:
                        seen.add(k)
                        v = _xa(r.Value1)
                        if v:
                            eff[k] = v
        elif st.Format == 2:
            cov = st.Coverage.glyphs
            c2 = defaultdict(list)
            for g, c in st.ClassDef2.classDefs.items():
                if c:
                    c2[c].append(g)
            all_r = [g for gs in c2.values() for g in gs]
            for a in cov:
                rec = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)].Class2Record
                for c, gs in c2.items():
                    v = _xa(rec[c].Value1)
                    if v:
                        for b in gs:
                            if (a, b) not in seen:
                                eff[a, b] = v
                for b in all_r:
                    seen.add((a, b))
    return eff


def _effective_kerning(gpos):
    idxs = sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex})
    total = {}
    for i in idxs:
        for k, v in _lookup_pairs(gpos.LookupList.Lookup[i]).items():
            total[k] = total.get(k, 0) + v
    return {k: v for k, v in total.items() if v}


def _pairs_fea(name, pairs):
    """Compile {(a, b): v} into one single conflict-free Format-2 subtable."""
    pairs = {k: v for k, v in pairs.items() if v}
    if not pairs:
        return ''
    rows = defaultdict(dict)
    for (a, b), v in pairs.items():
        rows[a][b] = v
    lcls = defaultdict(list)
    for a, r in rows.items():
        lcls[tuple(sorted(r.items()))].append(a)
    lkeys = sorted(lcls)
    cols = defaultdict(dict)
    for i, k in enumerate(lkeys):
        for b, v in k:
            cols[b][i] = v
    rcls = defaultdict(list)
    for b, c in cols.items():
        rcls[tuple(sorted(c.items()))].append(b)
    rkeys = sorted(rcls)
    out = []
    for i, k in enumerate(lkeys):
        out.append(f'@{name}_L{i} = [{" ".join(sorted(lcls[k]))}];')
    for j, k in enumerate(rkeys):
        out.append(f'@{name}_R{j} = [{" ".join(sorted(rcls[k]))}];')
    out.append(f'lookup {name} {{\n  lookupflag IgnoreMarks;')
    for j, k in enumerate(rkeys):
        for i, v in k:
            out.append(f'  pos @{name}_L{i} @{name}_R{j} {v};')
    out.append(f'}} {name};\nfeature kern {{ lookup {name}; }} kern;\n')
    return '\n'.join(out)


def _find_format2(gpos):
    for i in sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex}):
        for st in _subtables(gpos.LookupList.Lookup[i]):
            if st.Format == 2:
                return st
    return None


def _alias_bridges(glyf, order, st2):
    """Bridge Mulish's Format-2 C1 and C2 classes between Cyrillic and Latin via 1-component aliases."""
    c1_of = {g: st2.ClassDef1.classDefs.get(g, 0) for g in st2.Coverage.glyphs}
    c2_of = {g: c for g, c in st2.ClassDef2.classDefs.items() if c != 0}
    c1_c2l, c1_l2c, c2_c2l, c2_l2c = {}, {}, {}, {}
    for g in order:
        if not _is_cyr_glyph(g):
            continue
        rg = glyf[g]
        if rg.isComposite() and len(rg.components) == 1:
            comp = rg.components[0]
            lat = comp.glyphName
            if not _is_cyr_glyph(lat) and comp.y == 0 and abs(comp.x) <= 8:
                if g in c1_of and lat in c1_of:
                    c1_c2l.setdefault(c1_of[g], c1_of[lat])
                    c1_l2c.setdefault(c1_of[lat], c1_of[g])
                if g in c2_of and lat in c2_of:
                    c2_c2l.setdefault(c2_of[g], c2_of[lat])
                    c2_l2c.setdefault(c2_of[lat], c2_of[g])
    # Cyrillic У (uni0423) has the upper V/Y diagonal arms of Y (uni04AE -> Y)
    if 'uni0423' in c1_of and 'Y' in c1_of:
        c1_c2l.setdefault(c1_of['uni0423'], c1_of['Y'])
    if 'uni0423' in c2_of and 'Y' in c2_of:
        c2_c2l.setdefault(c2_of['uni0423'], c2_of['Y'])
    return c1_of, c2_of, c1_c2l, c1_l2c, c2_c2l, c2_l2c


def _mat(st2, i, j):
    if i is None or j is None or j == 0:
        return 0
    return _xa(st2.Class1Record[i].Class2Record[j].Value1)


def _build_sc_kern(ctx):
    """Build CYRILLIC_SC_KERN for all pairs involving at least one .sc.cyrillic glyph."""
    glyf, font, sc_font = ctx.glyf, ctx.font, ctx.sc_font
    have = set(font.getGlyphOrder())
    rev = {g: u for u, g in font.getBestCmap().items()}
    lat_sc_src = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ') | {c for _, c, _ in ctx.SC_ACC}
    sym_sc_src = set(ctx.SC_SYMBOLS)
    cyr_cap_to_sc = {sc[:-len(SUF)]: sc for sc in ctx.cyr_sc_glyphs}
    for _, cap_l, sc in ctx.cyr_pairs:
        cyr_cap_to_sc.setdefault(cap_l, sc)

    def map_sc(g):
        """Return (mapped_glyph, kind) where kind in ('cyr_sc', 'lat_sc', 'punct') or None."""
        if g in cyr_cap_to_sc and cyr_cap_to_sc[g] in have:
            return cyr_cap_to_sc[g], 'cyr_sc'
        if g in lat_sc_src and g + '.sc' in have:
            return g + '.sc', 'lat_sc'
        if g in sym_sc_src and g + '.sc' in have:
            return g + '.sc', 'punct'
        if g + '.sc' not in have and g in rev and unicodedata.category(chr(rev[g]))[0] in 'PS':
            return g, 'punct'
        return None

    scale = lambda v: round((v or 0) * ctx.SC_SCALE * ctx.SC_K)
    scg = sc_font['GPOS'].table
    raw = _effective_kerning(scg)
    out = {}

    # 1. Direct sc_font pairs involving Cyrillic capitals (with Cyrillic capitals, .sc symbols, or plain punct)
    for (a, b), v in raw.items():
        ma, mb = map_sc(a), map_sc(b)
        if not ma or not mb:
            continue
        if ma[0] in TABULAR or mb[0] in TABULAR:
            continue
        if ma[1] == 'cyr_sc' or mb[1] == 'cyr_sc':
            sv = scale(v)
            if sv:
                out[ma[0], mb[0]] = sv

    # 2. Cross-script small-cap pairs (.sc.cyrillic <-> Latin .sc) via sc_font's Format-2 class bridge
    st2 = _find_format2(scg)
    if st2 is not None:
        c1_of, c2_of, c1_c2l, c1_l2c, c2_c2l, c2_l2c = _alias_bridges(
            sc_font['glyf'], sc_font.getGlyphOrder(), st2
        )
        cyr_srcs = [g for g in cyr_cap_to_sc if g in c1_of or g in c2_of]
        lat_srcs = [g for g in sorted(lat_sc_src) if (g + '.sc' in have) and (g in c1_of or g in c2_of)]
        for c_src in cyr_srcs:
            c_sc = cyr_cap_to_sc[c_src]
            for l_src in lat_srcs:
                l_sc = l_src + '.sc'
                if (c_sc, l_sc) not in out and c_src in c1_of and l_src in c2_of:
                    ca, cb = c1_of[c_src], c2_of[l_src]
                    v = _mat(st2, ca, c2_l2c.get(cb)) or _mat(st2, c1_c2l.get(ca), cb)
                    sv = scale(v)
                    if sv:
                        out[c_sc, l_sc] = sv
                if (l_sc, c_sc) not in out and l_src in c1_of and c_src in c2_of:
                    ca, cb = c1_of[l_src], c2_of[c_src]
                    v = _mat(st2, ca, c2_c2l.get(cb)) or _mat(st2, c1_l2c.get(ca), cb)
                    sv = scale(v)
                    if sv:
                        out[l_sc, c_sc] = sv

    return out


def _build_cross_kern(ctx):
    """Build CYRILLIC_CROSS_KERN for full-size Latin<->Cyrillic letter pairs Mulish left at 0."""
    glyf, font = ctx.glyf, ctx.font
    gpos = font['GPOS'].table
    existing = _effective_kerning(gpos)
    st2 = _find_format2(gpos)
    if st2 is None:
        return {}

    order = font.getGlyphOrder()
    rev = {g: u for u, g in font.getBestCmap().items()}
    kerned = {a for a, _ in existing} | {b for _, b in existing}

    def is_lat_letter(g):
        if g in TABULAR or _is_cyr_glyph(g) or g not in kerned:
            return False
        if '.' in g:  # skip .ss04/.ss06/ligatures/etc. so kern.py's inheritance stays untouched
            return False
        u = rev.get(g)
        # Latin Extended Additional too: Mulish puts ụ ủ ứ ọ ẹ ỵ Ụ Ọ Ạ ... in their letter's
        # classes, and they kerned as their letter does against Latin only (uТ -74, ụТ 0
        # through v0.5.10, issue 13)
        return bool(u and unicodedata.category(chr(u)).startswith('L') and (u < 0x0370 or 0x1E00 <= u <= 0x1EFF))

    def is_cyr_letter(g):
        if g in TABULAR or g.endswith(SUF) or not _is_cyr_glyph(g) or g not in kerned:
            return False
        if g.endswith(('.ss04', '.ss06')):
            return False
        return True

    c1_of, c2_of, c1_c2l, c1_l2c, c2_c2l, c2_l2c = _alias_bridges(glyf, order, st2)
    cyr_l = [g for g in order if is_cyr_letter(g) and g in c1_of]
    cyr_r = [g for g in order if is_cyr_letter(g) and g in c2_of]
    lat_l = [g for g in order if is_lat_letter(g) and g in c1_of]
    lat_r = [g for g in order if is_lat_letter(g) and g in c2_of]

    out = {}
    for a in cyr_l:
        ca = c1_of[a]
        for b in lat_r:
            if (a, b) in existing:
                continue
            cb = c2_of[b]
            v = _mat(st2, ca, c2_l2c.get(cb)) or _mat(st2, c1_c2l.get(ca), cb)
            if v:
                out[a, b] = v
    for a in lat_l:
        ca = c1_of[a]
        for b in cyr_r:
            if (a, b) in existing:
                continue
            cb = c2_of[b]
            v = _mat(st2, ca, c2_c2l.get(cb)) or _mat(st2, c1_l2c.get(ca), cb)
            if v:
                out[a, b] = v
    return out


# Cyrillic capitals whose open side has the shape of a Latin capital's, for the
# punctuation kerning Mulish gives the Latin capital and not the Cyrillic: the right side
# of Г Ѓ Ґ Ғ is T's (an arm over open space), and both sides of У Ў Ӯ Ӱ Ӳ are Y's (the arms
# over open space, the foot under them). Ч is not here: its right side is a full-height
# stem, which takes no kerning against a period in Mulish's Latin (H.) or in the reference
# faces (IBM Plex Sans, PT Sans, Arial, SF: Ч. 0).
PUNCT_RIGHT = {'uni0413': 'T', 'uni0403': 'T', 'uni0490': 'T', 'uni0492': 'T',
               'uni0423': 'Y', 'uni040E': 'Y', 'uni04EE': 'Y', 'uni04F0': 'Y', 'uni04F2': 'Y'}
PUNCT_LEFT = {'uni0423': 'Y', 'uni040E': 'Y', 'uni04EE': 'Y', 'uni04F0': 'Y', 'uni04F2': 'Y'}
PUNCT_RATIO = (0.0, 1.5)   # less room than the Latin model, less kerning; never over 1.5 times
PUNCT_PAD = 60


def _build_punct_kern(ctx):
    """CYRILLIC_PUNCT_KERN: Г, У and their accented forms against the punctuation their Latin
    model (T, Y) kerns with, for the pairs Mulish leaves at 0 (Г. Г, Г» У. У, «У ...).

    A positive value (T” T) T?: the arm's end meets the mark) is taken as it is. A negative
    one is scaled by how much more open space the Cyrillic letter has beside that mark than
    the Latin one: the distance from the letter's ink to its advance edge (right side) or
    origin (left side), measured across the punctuation mark's own height range (60 units
    more each way), Cyrillic
    over Latin, at most 1.5 (PUNCT_RATIO): Ғ's stroke, which stands out to the right at
    mid-height, takes less kerning against a dash or a guillemet than Г does. Г's arm reaches farther from its stem than T's half
    bar, so Г. is about 1.45 times T. (IBM Plex Sans gives 1.5, PT Sans 1.07, Arial 1.1);
    У's foot leaves a little more room than Y's stem (1.17 times Y.)."""
    font = ctx.font
    have = set(font.getGlyphOrder())
    rev = {g: u for u, g in font.getBestCmap().items()}
    existing = _effective_kerning(font['GPOS'].table)

    def is_punct(g):
        u = rev.get(g)
        return u is not None and unicodedata.category(chr(u))[0] == 'P'

    def ink(g):
        b = ctx.path_of(g).bounds
        return b if b and b[3] > b[1] else None

    def open_side(g, y0, y1, right):
        b = ctx.clip(ctx.path_of(g), (-4000, y0, 8000, y1)).bounds
        if not b or b[2] <= b[0]: return None
        return ctx.W(g) - b[2] if right else b[0]

    def value(cyr, lat, mark, v, right):
        if v >= 0: return v
        m = ink(mark)
        if not m: return v
        # the mark's height range, and PUNCT_PAD more above and below: a stroke that ends
        # just over a dash still counts as beside it
        y0, y1 = m[1] - PUNCT_PAD, m[3] + PUNCT_PAD
        oc, ol = open_side(cyr, y0, y1, right), open_side(lat, y0, y1, right)
        if oc is None or ol is None or ol <= 0: return v
        r = min(max(oc / ol, PUNCT_RATIO[0]), PUNCT_RATIO[1])
        return round(v * r)

    out = {}
    for cyr, lat in PUNCT_RIGHT.items():
        if cyr not in have or lat not in have: continue
        for (a, b), v in existing.items():
            if a == lat and is_punct(b) and (cyr, b) not in existing:
                k = value(cyr, lat, b, v, True)
                if k: out[cyr, b] = k
    for cyr, lat in PUNCT_LEFT.items():
        if cyr not in have or lat not in have: continue
        for (a, b), v in existing.items():
            if b == lat and is_punct(a) and (a, cyr) not in existing:
                k = value(cyr, lat, a, v, False)
                if k: out[a, cyr] = k
    return out


# ================================================================ phase 2: features
def features(ctx):
    have = set(ctx.font.getGlyphOrder())

    smcp_map = {low: sc for low, _, sc in ctx.cyr_pairs if low and low in have and sc in have}
    c2sc_map = {cap: sc for _, cap, sc in ctx.cyr_pairs if cap and cap in have and sc in have}

    # Combining marks that Mulish's ccmp promotes to .case after capitals: revert them
    # after .sc.cyrillic bases so c2sc on 'А\u0301' matches smcp on 'а\u0301'.
    mcase_pairs = [
        (g, g[:-5])
        for g in ctx.font.getGlyphOrder()
        if g.endswith('.case') and g[:-5] in have and ctx.is_mark(g) and ctx.is_mark(g[:-5])
    ]
    marks_dict, _, _ = _mark_data(ctx.font)
    top_marks = [
        m for m in ctx.font.getGlyphOrder()
        if m in marks_dict and marks_dict[m][0] in (TOP, TOPR) and not m.endswith('.case')
    ]

    J = ' '.join
    smcp_srcs = sorted(smcp_map)
    smcp_dsts = [smcp_map[g] for g in smcp_srcs]
    c2sc_srcs = sorted(c2sc_map)
    c2sc_dsts = [c2sc_map[g] for g in c2sc_srcs]
    sc_all = sorted(set(ctx.cyr_sc_glyphs))

    gsub_lines = [
        f'@CYRILLIC_LC = [{J(smcp_srcs)}];',
        f'@CYRILLIC_SC_FROM_LC = [{J(smcp_dsts)}];',
        f'@CYRILLIC_UC = [{J(c2sc_srcs)}];',
        f'@CYRILLIC_SC_FROM_UC = [{J(c2sc_dsts)}];',
        f'@CYRILLIC_SC = [{J(sc_all)}];',
        'lookup CYRILLIC_SMCP { sub @CYRILLIC_LC by @CYRILLIC_SC_FROM_LC; } CYRILLIC_SMCP;',
        'lookup CYRILLIC_C2SC { sub @CYRILLIC_UC by @CYRILLIC_SC_FROM_UC; } CYRILLIC_C2SC;',
    ]
    c2sc_extra = ''
    if mcase_pairs:
        mc_src = [a for a, _ in mcase_pairs]
        mc_dst = [b for _, b in mcase_pairs]
        gsub_lines.extend([
            f'@CYRILLIC_MCASE = [{J(mc_src)}];',
            f'@CYRILLIC_MLC = [{J(mc_dst)}];',
            'lookup CYRILLIC_C2SC_UNCASE { sub @CYRILLIC_MCASE by @CYRILLIC_MLC; } CYRILLIC_C2SC_UNCASE;',
            'lookup CYRILLIC_C2SC_MARK { sub @CYRILLIC_SC @CYRILLIC_MCASE\' lookup CYRILLIC_C2SC_UNCASE; } CYRILLIC_C2SC_MARK;',
        ])
        c2sc_extra = ' lookup CYRILLIC_C2SC_MARK;'
    # Soft-dotted Ukrainian і (uni0456) and Serbian/Macedonian ј (uni0458): drop dot under top marks
    if top_marks and {'uni0456', 'uni0456.loclBSH', 'uni0458', 'uni0237'} <= have:
        gsub_lines.extend([
            f'@CYRILLIC_TOPMARKS = [{J(top_marks)}];',
            'lookup CYRILLIC_SOFTDOT_SUB { sub uni0456 by uni0456.loclBSH; sub uni0458 by uni0237; } CYRILLIC_SOFTDOT_SUB;',
            'lookup CYRILLIC_SOFTDOT { sub [uni0456 uni0458]\' lookup CYRILLIC_SOFTDOT_SUB @CYRILLIC_TOPMARKS; } CYRILLIC_SOFTDOT;',
            'feature ccmp { lookup CYRILLIC_SOFTDOT; } ccmp;',
        ])
    gsub_lines.extend([
        'feature smcp { lookup CYRILLIC_SMCP; } smcp;',
        f'feature c2sc {{ lookup CYRILLIC_C2SC;{c2sc_extra} }} c2sc;',
    ])
    ctx.gsub('\n'.join(gsub_lines), before='main')

    mark_fea = _build_mark_fea(ctx)
    if mark_fea:
        ctx.gpos(mark_fea, before='mulish')

    sc_kern = _build_sc_kern(ctx)
    cross_kern = _build_cross_kern(ctx)
    punct_kern = _build_punct_kern(ctx)
    ctx.cyr_sc_kern = sc_kern
    ctx.cyr_cross_kern = cross_kern
    ctx.cyr_punct_kern = punct_kern

    kern_fea = (_pairs_fea('CYRILLIC_SC_KERN', sc_kern) + _pairs_fea('CYRILLIC_CROSS_KERN', cross_kern)
                + _pairs_fea('CYRILLIC_PUNCT_KERN', punct_kern))
    if kern_fea:
        ctx.gpos(kern_fea)

    ctx.log(
        f'smcp: {len(smcp_map)}, c2sc: {len(c2sc_map)}, mark bases: {getattr(ctx, "cyr_mark_bases", 0)}, '
        f'sc_kern: {len(sc_kern)} pairs, cross_kern: {len(cross_kern)} pairs, punct_kern: {len(punct_kern)} pairs '
        f'({" ".join(f"{a}+{b}={v}" for (a, b), v in sorted(punct_kern.items()) if b == "period" or a == "guillemotleft")})'
    )


# ================================================================ phase 3: post
def _attach_locl_sc(font):
    """Ensure cyrl BSH and CHU locl features also localize small caps after smcp/c2sc."""
    from fontTools.ttLib.tables import otTables

    have = set(font.getGlyphOrder())
    lang_maps = {
        'BSH ': {
            'uni0406' + SUF: 'uni0406.loclBSH' + SUF,
            'uni0492' + SUF: 'uni0492.loclBSH' + SUF,
        },
        'CHU ': {
            'uni0498' + SUF: 'uni0498.loclCHU' + SUF,
            'uni04AA' + SUF: 'uni04AA.loclCHU' + SUF,
        },
    }
    gsub = font['GSUB'].table
    for sr in gsub.ScriptList.ScriptRecord:
        if sr.ScriptTag != 'cyrl':
            continue
        for lr in sr.Script.LangSysRecord:
            mp = {a: b for a, b in lang_maps.get(lr.LangSysTag, {}).items() if a in have and b in have}
            if not mp:
                continue
            for fi in lr.LangSys.FeatureIndex:
                fr = gsub.FeatureList.FeatureRecord[fi]
                if fr.FeatureTag == 'locl':
                    st = otTables.SingleSubst()
                    st.mapping = mp
                    lk = otTables.Lookup()
                    lk.LookupType = 1
                    lk.LookupFlag = 0
                    lk.SubTable = [st]
                    lk.SubTableCount = 1
                    new_idx = len(gsub.LookupList.Lookup)
                    gsub.LookupList.Lookup.append(lk)
                    gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
                    fr.Feature.LookupListIndex.append(new_idx)
                    fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
                    break


def _unkink_cyr(font):
    """Smooth residual rounding kinks (3..15 deg) in .cyrillic simple glyphs across all 14 styles."""
    glyf, hmtx = font['glyf'], font['hmtx']

    def turn(a, p, b):
        u, v = (p[0] - a[0], p[1] - a[1]), (b[0] - p[0], b[1] - p[1])
        if u == (0, 0) or v == (0, 0):
            return 180.0
        return abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))

    for name in font.getGlyphOrder():
        if not name.endswith('.cyrillic'):
            continue
        g = glyf[name]
        if g.isComposite() or g.numberOfContours <= 0:
            continue
        for _ in range(3):
            c = [tuple(xy) for xy in g.coordinates]
            on = [bool(f & 1) for f in g.flags]
            s0, moved, out_c = 0, 0, []
            for e in g.endPtsOfContours:
                pts = list(zip(c[s0:e + 1], on[s0:e + 1]))
                s0 = e + 1
                k = 0
                while k < len(pts) and len(pts) > 5:
                    n = len(pts)
                    p0, o0 = pts[k - 1]
                    p1, o1 = pts[k]
                    p2, o2 = pts[(k + 1) % n]
                    p3, o3 = pts[(k + 2) % n]
                    if (
                        o1 and o2 and (not o0 or not o3)
                        and math.dist(p1, p2) <= 5.5
                        and 3.0 < max(turn(p0, p1, p2) if not o0 else 0, turn(p1, p2, p3) if not o3 else 0) < 20.0
                    ):
                        pts[k] = ((round((p1[0] + p2[0]) / 2), round((p1[1] + p2[1]) / 2)), True)
                        del pts[(k + 1) % n]
                        moved += 1
                        break
                    pm, om = pts[k - 2]
                    if (
                        om and not o0 and o1 and not o2 and o3
                        and 3.0 < turn(p0, p1, p2) < 15.0
                        and math.dist(pm, p3) < 40.0
                        and turn(pm, p1, p3) < 12.0
                    ):
                        # Collapse 2-segment micro-spline (on-off-on-off-on) into one quadratic keeping tangent at p3
                        pts[k] = (p2, False)
                        del pts[(k + 1) % n]
                        del pts[(k - 1) % len(pts)]
                        moved += 1
                        break
                    k += 1
                n = len(pts)
                for k in range(n):
                    p1, o1 = pts[k]
                    p0, o0 = pts[k - 1]
                    p2, o2 = pts[(k + 1) % n]
                    if not o1 or (o0 and o2):
                        continue
                    if not 2.8 < turn(p0, p1, p2) < 15.0:
                        continue
                    if not o0 and not o2:
                        ax, ay = p0
                        bx, by = p2
                        l2 = (bx - ax) ** 2 + (by - ay) ** 2
                        if not l2:
                            continue
                        r = ((p1[0] - ax) * (bx - ax) + (p1[1] - ay) * (by - ay)) / l2
                        ix, iy = ax + r * (bx - ax), ay + r * (by - ay)
                        cands = [
                            (round(ix) + dx, round(iy) + dy)
                            for dx in range(-3, 4)
                            for dy in range(-3, 4)
                            if math.dist((round(ix) + dx, round(iy) + dy), p0) >= 2
                            and math.dist((round(ix) + dx, round(iy) + dy), p2) >= 2
                        ]
                        if cands:
                            q = min(cands, key=lambda q: (turn(p0, q, p2) >= 2.5, math.dist(q, (ix, iy)), turn(p0, q, p2)))
                            if turn(p0, q, p2) < 2.5:
                                pts[k] = (q, True)
                                moved += 1
                    else:
                        hi, oi = ((k + 1) % n, k - 1) if o0 else (k - 1, (k + 1) % n)
                        ph, po = pts[hi][0], pts[oi][0]
                        lo, lh = math.dist(p1, po), math.dist(p1, ph)
                        if lo > 0 and lh > 0:
                            ux, uy = (p1[0] - po[0]) / lo, (p1[1] - po[1]) / lo
                            ix, iy = p1[0] + ux * lh, p1[1] + uy * lh
                            cands = [
                                (round(ix) + dx, round(iy) + dy)
                                for dx in range(-2, 3)
                                for dy in range(-2, 3)
                                if math.dist((round(ix) + dx, round(iy) + dy), p1) >= 2
                            ]
                            if cands:
                                q = min(cands, key=lambda q: (turn(po, p1, q) >= 2.5, math.dist(q, (ix, iy)), turn(po, p1, q)))
                                if turn(po, p1, q) < 2.5:
                                    pts[hi] = (q, False)
                                    moved += 1
                out_c.append(pts)
            if not moved:
                break
            g.coordinates = GlyphCoordinates([xy for pts in out_c for xy, _ in pts])
            g.flags = array('B', [1 if o else 0 for pts in out_c for _, o in pts])
            ends, acc = [], -1
            for pts in out_c:
                acc += len(pts)
                ends.append(acc)
            g.endPtsOfContours = ends
            g.numberOfContours = len(out_c)
            g.recalcBounds(glyf)
            hmtx[name] = (hmtx[name][0], g.xMin)


def post(ctx):
    _unkink_cyr(ctx.font)
    _attach_locl_sc(ctx.font)
    eff = _effective_kerning(ctx.font['GPOS'].table)
    bad_sc = [(k, v, eff.get(k, 0)) for k, v in ctx.cyr_sc_kern.items() if eff.get(k, 0) != v]
    if bad_sc:
        raise SystemExit(f'cyrillic: {len(bad_sc)} CYRILLIC_SC_KERN pairs masked or altered, e.g. {bad_sc[:5]}')
    bad_cx = [(k, v, eff.get(k, 0)) for k, v in ctx.cyr_cross_kern.items() if eff.get(k, 0) != v]
    if bad_cx:
        raise SystemExit(f'cyrillic: {len(bad_cx)} CYRILLIC_CROSS_KERN pairs masked or altered, e.g. {bad_cx[:5]}')
    bad_px = [(k, v, eff.get(k, 0)) for k, v in ctx.cyr_punct_kern.items() if eff.get(k, 0) != v]
    if bad_px:
        raise SystemExit(f'cyrillic: {len(bad_px)} CYRILLIC_PUNCT_KERN pairs masked or altered, e.g. {bad_px[:5]}')

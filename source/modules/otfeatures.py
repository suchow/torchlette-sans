"""otfeatures: case forms and capital spacing, the slashed zero, mark attachment for
build.py's glyphs, their GDEF classes and ligature carets, and aalt / salt.

Feature tags: extends GSUB case, ccmp and aalt and GPOS mark; adds GSUB zero and salt
and GPOS cpsp. The new ones and case and aalt are off by default. The default-on
additions (mark, and ccmp's one lookup) touch only a combining mark after a glyph that
had no anchors (a small cap, an alternate, a figure, a ligature), which was left
unpositioned before; text without such a sequence shapes exactly as before.

- case: ( ) [ ] { } - – — « » ‹ › @ · ¡ ¿ centred on the capitals (their ink box's
  middle on the cap height's, 352.5). The hyphen takes build.py's hyphen.case (ss16's
  cap hyphen); the rest are new glyphs `<name>.case.otfeatures`, the default glyph
  moved up, same advance. Its lookup runs last (after ss16), so ss16's rules still
  see the plain punctuation.
- cpsp: 10 units more on each side of every capital (and the case forms).
- zero: a slashed zero for every zero form (lining, pnum, onum, tabular onum, small
  cap, tabular small cap, superior, inferior, numerator, denominator):
  `<zero form>.zero.otfeatures`. The slash is a straight stroke in the zero's own
  side thickness (0.8 of it) at the solidus's slant (less in a narrow counter),
  ending inside the ring. Runs
  last, after every figure feature.
- mark: one mark-to-base and one mark-to-ligature lookup (before Mulish's own, so
  mark-to-base comes before mkmk) with Mulish's mark classes and mark anchors, for
  the bases Mulish has no anchors for: the small caps, the ss04-ss07 alternates and
  their accented forms, ss16's letter alternates, every figure form, the slashed
  zeros, and (mark-to-ligature) the letter ligatures. Anchors follow Mulish's
  conventions (see anchors_for below); where build.py drew a precomposed form of the
  base (Á.sc, á.ss04 ...), its mark offset is the anchor, so base + mark matches it.
- ccmp: a top mark right after a lining figure becomes its .case form, as Mulish's
  ccmp does after a capital (old-style and small-cap figures keep the lowercase marks).
- GDEF: every glyph build.py and this module add (and any other module's glyph
  left without one) gets a glyph class (ligature for
  every ligature substitution's output, base otherwise) and each ligature without
  carets a caret between each pair of its characters.
- aalt: one alternate lookup with every glyph's single alternates from Mulish's
  aalt, ss04-ss08, case, zero, smcp, c2sc, the figure features, sups, subs, sinf,
  numr, dnom, ordn and the ss15/ss16/cvNN letter and sign alternates (not the
  internal pieces: protected glyphs, spark, progress-bar and tag parts, and the
  word marks' and spacing pieces that only make sense inside their words). It
  replaces Mulish's two aalt lookups, whose alternates come first in it.
- salt: one alternate lookup with the ss04-ss08 alternates.

Copies of the kerning: each new case form and slashed zero is added to every pair
positioning subtable wherever its source glyph is, so it kerns as the source does.

No existing glyph outline or advance changes.
"""
import math, re, unicodedata

CAP_MID = 705 / 2
CASE_SRC = ['parenleft', 'parenright', 'bracketleft', 'bracketright', 'braceleft', 'braceright',
            'endash', 'emdash', 'guillemotleft', 'guillemotright', 'guilsinglleft', 'guilsinglright',
            'at', 'periodcentered', 'exclamdown', 'questiondown']
ZERO_SRC = ['zero', 'zero.pnum', 'zero.osf', 'zero.tosf', 'zero.sc', 'zero.sc.tf',
            'uni2070', 'uni2080', 'zero.numr', 'zero.dnom']
CPSP = 10
SLASH_K = 0.8
SUF = 'otfeatures'


def case_name(n): return f'{n}.case.{SUF}'
def zero_name(n): return f'{n}.zero.{SUF}'


# ---------------------------------------------------------------- glyphs
def _slant(ctx):
    """The solidus's slant (dx per dy), from the middle of its stroke at two heights."""
    p = ctx.path_of('slash'); b = p.bounds
    ya, yb = b[1] + 0.25 * (b[3] - b[1]), b[1] + 0.75 * (b[3] - b[1])
    xa, xb = ctx.mid(ctx.hspans(p, ya)[0]), ctx.mid(ctx.hspans(p, yb)[0])
    return (xb - xa) / (yb - ya)


def _slashed(ctx, z):
    """The zero with a straight stroke across its counter, 0.8 of its side's thickness,
    at the solidus's slant, ending in the ring."""
    p = ctx.path_of(z)
    contours = []
    for c in p.contours:
        q = ctx.pathops.Path(); c.draw(q.getPen()); contours.append(q)
    area = lambda q: (q.bounds[2] - q.bounds[0]) * (q.bounds[3] - q.bounds[1])
    contours.sort(key=area)
    hole = contours[-2]                                  # the counter
    x0, y0, x1, y1 = p.bounds
    cx, cy, h = (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0
    side = ctx.hspans(p, cy)[0]
    hb = hole.bounds; hx, hy = (hb[0] + hb[2]) / 2, (hb[1] + hb[3]) / 2
    cw, ch = hb[2] - hb[0], hb[3] - hb[1]
    # In a narrow counter (the small, superior and inferior zeros of the heavy styles)
    # the slash is no steeper than the counter's diagonal allows, so it ends in the
    # counter's top and bottom curves rather than running along its sides, and no
    # thicker than half the counter, so it leaves no slivers.
    t = min(SLASH_K * (side[1] - side[0]), 0.5 * cw)
    k, dy = min(_slant(ctx), 0.85 * cw / ch), h / 2 + 40
    bar = ctx.band((cx - k * dy, cy - dy), (cx + k * dy, cy + dy), t)
    # cut at the counter grown a little into the ring, so the slash's ends are hidden in
    # the ring and its sides meet the counter's edge at a clean, steep corner
    e = 0.4 * (side[1] - side[0])
    sx, sy = 1 + 2 * e / (hb[2] - hb[0]), 1 + 2 * e / (hb[3] - hb[1])
    grown = ctx.transformed(hole, (sx, 0, 0, sy, hx - sx * hx, hy - sy * hy))
    cut = ctx.pathops.op(bar, grown, ctx.pathops.PathOp.INTERSECTION)
    return ctx.union(p, cut)


def glyphs(ctx):
    ctx.case_pairs = [('hyphen', 'hyphen.case')]
    for n in CASE_SRC:
        b = ctx.path_of(n).bounds
        dy = round(CAP_MID - (b[1] + b[3]) / 2)
        ctx.add(case_name(n), ctx.path_of(n, 0, dy), ctx.W(n))
        ctx.case_pairs.append((n, case_name(n)))
    ctx.zero_pairs = []
    for z in ZERO_SRC:
        if z not in ctx.glyf.glyphs: continue
        ctx.add(zero_name(z), _slashed(ctx, z), ctx.W(z))
        ctx.zero_pairs.append((z, zero_name(z)))
    ctx.log(f'{len(ctx.case_pairs) - 1} case forms, {len(ctx.zero_pairs)} slashed zeros')


# ---------------------------------------------------------------- anchors
# Mulish's mark-to-base lookup has six mark classes: 0 above (lowercase marks anchored
# at 454, the .case marks at 705), 1 above right (horn, the d/l/t caron), 2 below (y 0),
# 3 ogonek, 4 the short stroke on an ascender, 5 the stroke overlays (Ħ Ł Đ, U+0337/8).
# Its bases put the above anchor 16 units under the x-height (454) and at the cap
# height (705, for the .case marks the capitals get from ccmp), over the middle of the
# ink near the top; the below anchor on the baseline under the middle of the ink there.
TOP, TOPR, BOT, OGON, ASC, OVER = range(6)


def _mark_data(font):
    gpos = font['GPOS'].table
    idx = sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag in ('mark', 'mkmk')
                  for i in fr.Feature.LookupListIndex})
    marks, bases, ligs, mk2 = {}, {}, set(), {}
    for i in idx:
        lk = gpos.LookupList.Lookup[i]
        for st in lk.SubTable:
            if lk.LookupType == 9: st = st.ExtSubTable
            t = st.LookupType if hasattr(st, 'LookupType') else lk.LookupType
            if lk.LookupType == 4 or t == 4:
                assert not marks or st.ClassCount == 6, 'one six-class mark-to-base subtable expected'
                for g, r in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord):
                    marks[g] = (r.Class, (r.MarkAnchor.XCoordinate, r.MarkAnchor.YCoordinate))
                for g, r in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                    bases[g] = {c: (a.XCoordinate, a.YCoordinate) for c, a in enumerate(r.BaseAnchor) if a}
            elif lk.LookupType == 5:
                ligs.update(st.LigatureCoverage.glyphs)
            elif lk.LookupType == 6:
                for g, r in zip(st.Mark2Coverage.glyphs, st.Mark2Array.Mark2Record):
                    a = r.Mark2Anchor[0]
                    if a: mk2[g] = (a.XCoordinate, a.YCoordinate)
    return marks, bases, ligs, mk2


def _onpts(ctx, n):
    c, _, fl = ctx.glyf[n].getCoordinates(ctx.glyf)
    return [(tuple(q), bool(f & 1)) for q, f in zip(c, fl)]


def _band_mid(ctx, p, y0, y1):
    b = ctx.clip(p, (-3000, y0, 5000, y1)).bounds
    return None if b is None or b == (0, 0, 0, 0) else (b[0] + b[2]) / 2


def _local_top(ctx, p, x, half=30):
    b = ctx.clip(p, (x - half, -3000, x + half, 5000)).bounds
    return None if not b or b == (0, 0, 0, 0) else b[3]


def _flat_top(ctx, n, p):
    """The glyph's top less its overshoot: a round top (a curve extreme at the top) is
    taken to overshoot by 1.3% of the glyph's height, as Mulish's o (480 on 470) does."""
    x0, y0, x1, y1 = p.bounds
    top = [on for (q, on) in _onpts(ctx, n) if abs(q[1] - y1) < 0.5] if not ctx.glyf[n].isComposite() else [True, True]
    rnd = (not all(top)) or len(top) < 2
    return y1 - (round(0.013 * (y1 - min(y0, 0))) if rnd else 0)


def _geometric(ctx, n):
    """Anchors from the outline, Mulish's way: above at the flat top less 16 (for the
    lowercase marks) or at the flat top (lining figures, which take the .case marks as
    the capitals do), over the middle of the top fifth's ink; below on the baseline (or
    the bottom, for a figure that descends) under the middle of the bottom fifth's ink;
    the overlay at half height. Heights are from the glyph's own baseline: the line,
    or for an inferior figure (and its slashed zero) build.py's SUB_DROP below it."""
    p = ctx.path_of(n)
    x0, y0, x1, y1 = p.bounds
    bl = -ctx.SUB_DROP if n.split('.')[0] in {f'uni{u:04X}' for u in range(0x2080, 0x208F)} else 0
    h = y1 - min(y0, bl); ft = _flat_top(ctx, n, p)
    out = {TOP: (_band_mid(ctx, p, y1 - 0.2 * h, y1 + 1), ft if LINING_RE.match(n) else ft - 16)}
    yb = bl if y0 > bl - 30 else y0
    out[BOT] = (_band_mid(ctx, p, y0 - 1, y0 + 0.2 * h), yb)
    mid = (ft + bl) / 2
    out[OVER] = (_band_mid(ctx, p, mid - 0.1 * h, mid + 0.1 * h), mid)
    return {c: (round(a[0]), round(a[1])) for c, a in out.items() if a[0] is not None}


def _bands(ctx, p):
    x0, y0, x1, y1 = p.bounds; h = y1 - y0
    return {'top': _band_mid(ctx, p, y1 - 0.2 * h, y1 + 1), 'bot': _band_mid(ctx, p, y0 - 1, y0 + 0.2 * h),
            'mid': _band_mid(ctx, p, (y0 + y1) / 2 - 0.1 * h, (y0 + y1) / 2 + 0.1 * h)}


def _from_source(ctx, n, src, A):
    """An alternate's anchors: its source's, each moved by the change in the middle of
    the ink in its zone (top for the above marks, bottom for below, middle for the
    overlays), and an above anchor raised by as much as the ink above it rose."""
    pn, ps = ctx.path_of(n), ctx.path_of(src)
    bn, bs = _bands(ctx, pn), _bands(ctx, ps)
    zone = {TOP: 'top', TOPR: 'top', ASC: 'top', BOT: 'bot', OGON: 'bot', OVER: 'mid'}
    out = {}
    for c, (x, y) in A[src].items():
        z = zone[c]
        dx = (bn[z] - bs[z]) if bn[z] is not None and bs[z] is not None else 0
        x2 = round(x + dx)
        if c == TOP:
            tn, ts = _local_top(ctx, pn, x2), _local_top(ctx, ps, x)
            if tn is not None and ts is not None and tn > ts: y += round(tn - ts)
        out[c] = (x2, y)
    for c, a in _geometric(ctx, n).items(): out.setdefault(c, a)
    return out


def _from_capital(ctx, sc, cap, A):
    """A small cap's anchors: the capital's, mapped as build.py maps the capitals' marks
    onto the small caps (x about the ink middle times SC_SCALE); above marks are the
    lowercase ones, set SC_H - XH higher than on the x-height."""
    cx0, cx1 = ctx.ink(cap); sx0, sx1 = ctx.ink(sc)
    S = ctx.SC_SCALE; out = {}
    for c, (x, y) in A[cap].items():
        x2 = round((sx0 + sx1) / 2 + (x - (cx0 + cx1) / 2) * S)
        if c == TOP: y2 = 454 + (ctx.SC_H - ctx.XH) + round((y - 705) * S)
        elif c == TOPR: y2 = ctx.SC_H + round((y - 705) * S)
        else: y2 = round(y * S)
        out[c] = (x2, y2)
    for c, a in _geometric(ctx, sc).items(): out.setdefault(c, a)
    return out


def _stack_delta(ctx, A, marks, mk2):
    """How far Mulish sets a precomposed glyph's anchor beyond its mark's mark-to-mark
    anchor (the median over its own composites), above and below."""
    d = {TOP: [], BOT: []}
    for n, anc in A.items():
        g = ctx.glyf[n]
        if not g.isComposite() or len(g.components) != 2: continue
        m = g.components[1]
        if m.glyphName not in mk2 or m.glyphName not in marks: continue
        cls = marks[m.glyphName][0]
        k = TOP if cls in (TOP, TOPR) else BOT if cls in (BOT, OGON) else None
        if k is None or k not in anc: continue
        d[k].append(anc[k][1] - (m.y + mk2[m.glyphName][1]))
    med = lambda v: sorted(v)[len(v) // 2] if v else 0
    return {k: med(v) for k, v in d.items()}


def _composite(ctx, n, A, marks, mk2, delta, resolve):
    g = ctx.glyf[n]
    base = g.components[0]
    ba = resolve(base.glyphName)
    if ba is None: return None
    out = {c: (x + base.x, y + base.y) for c, (x, y) in ba.items()}
    for m in g.components[1:]:
        if m.glyphName not in marks: return None
        cls = marks[m.glyphName][0]
        k = TOP if cls in (TOP, TOPR) else BOT if cls in (BOT, OGON) else None
        if k is None or m.glyphName not in mk2: continue
        out[k] = (m.x + mk2[m.glyphName][0], m.y + mk2[m.glyphName][1] + delta[k])
    return out


LINING_RE = re.compile(r'^(zero|one|two|three|four|five|six|seven|eight|nine)(\.pnum)?(\.ss08)?(\.zero\.otfeatures)?$')
FIG_RE = re.compile(r'^(zero|one|two|three|four|five|six|seven|eight|nine)(\.(pnum|osf|tosf|sc|tf|ss08))*$')


def anchors_for(ctx):
    font = ctx.font
    marks, mbases, mligs, mk2 = _mark_data(font)
    A = dict(mbases)
    delta = _stack_delta(ctx, A, marks, mk2)
    order = font.getGlyphOrder()
    rev = {}
    for t in font['cmap'].tables:
        if t.isUnicode():
            for u, g in t.cmap.items(): rev.setdefault(g, u)
    new = [g for g in order if g not in ctx.mulish_glyphs]
    figs = [g for g in order if FIG_RE.match(g) and g not in A]
    zeros = [b for _, b in ctx.zero_pairs]
    want = []
    for g in new + figs:
        if g in A or g in want: continue
        stem = g.split('.')[0]
        letter = stem in rev and unicodedata.category(chr(rev[stem])).startswith('L')
        if g.endswith('.sc'):
            if FIG_RE.match(g) or letter: want.append(g)
        elif FIG_RE.match(g) or g in zeros: want.append(g)
        elif re.search(r'\.ss0[4-7]$', g) and '_' not in stem: want.append(g)
        elif g in ('r.rn', 'c.cl', 'v.vec', 'b.backc', 'd.fwdb', 't.out'): want.append(g)
    # build.py's precomposed forms of these bases (the small caps' and alternates'
    # accented composites: the base and one mark) say where it put each mark class;
    # those placements win, so a base + mark sequence matches its precomposed glyph.
    learned = {}
    for n in order:
        g = ctx.glyf[n]
        if not g.isComposite() or len(g.components) != 2: continue
        b, m = g.components
        if b.glyphName not in want or m.glyphName not in marks or m.glyphName.endswith('.case'): continue
        c, (mx, my) = marks[m.glyphName]
        learned.setdefault(b.glyphName, {}).setdefault(c, []).append((m.x + mx, m.y + my))
    med = lambda v: sorted(v)[len(v) // 2]
    ctx.learned = sum(len(v) for v in learned.values())
    cache = {}

    def resolve(n):
        if n in A: return A[n]
        if n in cache: return cache[n]
        cache[n] = None
        g = ctx.glyf[n]
        stem = n.split('.')[0]
        r = None
        if g.isComposite() and len(g.components) > 1 and all(c.glyphName in marks for c in g.components[1:]):
            r = _composite(ctx, n, A, marks, mk2, delta, resolve)
        elif g.isComposite() and len(g.components) > 1:
            r = _geometric(ctx, n)
        elif n.endswith('.sc') and not FIG_RE.match(n):
            u = rev.get(stem)
            cap = stem if (u and unicodedata.category(chr(u)) == 'Lu' and stem in A) else None
            r = _from_capital(ctx, n, cap, A) if cap else _geometric(ctx, n)
        elif FIG_RE.match(n) or n in zeros or '.zero.' in n:
            r = _geometric(ctx, n)
        elif stem in A:
            r = _from_source(ctx, n, stem, A)
        else:
            r = _geometric(ctx, n)
        if n in learned:
            r = dict(r or {})
            for c, pts in learned[n].items(): r[c] = (med([p[0] for p in pts]), med([p[1] for p in pts]))
        cache[n] = r
        return r

    out = {g: a for g in want if (a := resolve(g))}
    # ligatures: one component per letter of the name, each with that letter's anchors
    # where the letter sits in the ligature (see _fit); an above anchor is raised as far
    # as the ligature's ink above it rose.
    ligs = {}; ctx.lig_fit = {}
    for g in new:
        stem = g.split('.')[0]
        if '_' not in stem or g in mligs: continue
        parts = stem.split('_')
        if not all(p in A for p in parts): continue
        fit = _fit(ctx, g, parts); ctx.lig_fit[g] = fit
        pg = ctx.path_of(g); comps = []
        for p, x in fit:
            ca = {}
            for c, (ax, ay) in A[p].items():
                ax2 = round(x + ax)
                if c == TOP:
                    tn, ts = _local_top(ctx, pg, ax2), _local_top(ctx, ctx.path_of(p), ax)
                    if tn is not None and ts is not None and tn > ts: ay += round(tn - ts)
                ca[c] = (ax2, ay)
            comps.append(ca)
        ligs[g] = comps
    return marks, out, ligs


def _fit(ctx, g, parts):
    """Where each letter of a ligature sits in it: [(letter, x offset)]. Starting from
    Mulish's kerned setting scaled to the ligature's advance, each letter in turn is
    slid (within 120 units, never left of the previous letter's middle) to where its
    outline covers most of the ligature's ink and leaves least of its own uncovered."""
    op, I, D = ctx.pathops.op, ctx.pathops.PathOp.INTERSECTION, ctx.pathops.PathOp.DIFFERENCE
    items, total = ctx.setting(parts)
    k = ctx.W(g) / total if total else 1
    lig = ctx.path_of(g); out = []; floor = -1e9

    def score(p, dx):
        q = ctx.path_of(p, dx)
        return op(q, lig, I).area - 0.5 * op(q, lig, D).area
    for (p, x), part in zip(items, parts):
        x0 = x * k
        cands = [x0 + d for d in range(-120, 121, 10) if x0 + d >= floor]
        best = max(cands or [x0], key=lambda dx: score(part, dx))
        best = max((best + d for d in range(-8, 9, 2) if best + d >= floor), key=lambda dx: score(part, dx), default=best)
        out.append((part, round(best)))
        b = ctx.path_of(part).bounds
        floor = best + (b[0] + b[2]) / 2
    return out


def _anchor(a): return f'<anchor {a[0]} {a[1]}>'


def _mark_fea(marks, bases, ligs):
    classes = sorted({c for c, _ in marks.values()})
    lines = [f'markClass {m} {_anchor(a)} @OTFEATURES_M{c};' for m, (c, a) in marks.items()]
    lines.append('lookup OTFEATURES_MARK {')
    for g, a in bases.items():
        body = ' '.join(f'{_anchor(a[c])} mark @OTFEATURES_M{c}' for c in classes if c in a)
        if body: lines.append(f'  pos base {g} {body};')
    lines.append('} OTFEATURES_MARK;')
    if ligs:
        lines.append('lookup OTFEATURES_MARKLIG {')
        for g, comps in ligs.items():
            parts = []
            for ca in comps:
                body = ' '.join(f'{_anchor(ca[c])} mark @OTFEATURES_M{c}' for c in classes if c in ca)
                parts.append(body or '<anchor NULL>')
            lines.append(f'  pos ligature {g} ' + ' ligComponent '.join(parts) + ';')
        lines.append('} OTFEATURES_MARKLIG;')
    lines.append('feature mark { lookup OTFEATURES_MARK;' + (' lookup OTFEATURES_MARKLIG;' if ligs else '') + ' } mark;')
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------- features
def features(ctx):
    from fontTools.ttLib import TTFont
    ctx.mulish_glyphs = set(TTFont(ctx.SRC, lazy=True).getGlyphOrder())
    J = ' '.join
    ctx.gsub(f"lookup OTFEATURES_CASE {{ sub [{J(a for a, _ in ctx.case_pairs)}] by [{J(b for _, b in ctx.case_pairs)}]; }} OTFEATURES_CASE;\n"
             f"feature case {{ lookup OTFEATURES_CASE; }} case;")
    ctx.gsub(f"lookup OTFEATURES_ZERO {{ sub [{J(a for a, _ in ctx.zero_pairs)}] by [{J(b for _, b in ctx.zero_pairs)}]; }} OTFEATURES_ZERO;\n"
             f"feature zero {{ lookup OTFEATURES_ZERO; }} zero;")
    # lining figures take the capitals' .case marks (Mulish's ccmp gives them to the
    # capitals only): a top mark right after one becomes its .case form. Runs last, on
    # the figures' final forms (old-style and small-cap figures keep the lowercase marks).
    gs0 = ctx.font['GSUB'].table
    mcase = {a: b for a, bs in _singles(gs0, _feature_lookups(gs0, 'case')) for b in bs if ctx.is_mark(a) and ctx.is_mark(b)}
    lining = [g for g in ctx.font.getGlyphOrder() if LINING_RE.match(g)]
    ctx.fig_case = mcase
    ctx.gsub(f"lookup OTFEATURES_FIGMARK {{ sub [{J(lining)}] [{J(mcase)}]' by [{J(mcase.values())}]; }} OTFEATURES_FIGMARK;\n"
             f"feature ccmp {{ lookup OTFEATURES_FIGMARK; }} ccmp;")
    marks, bases, ligs = anchors_for(ctx)
    ctx.mark_bases, ctx.mark_ligs = bases, ligs
    ctx.gpos(_mark_fea(marks, bases, ligs), before='mulish')
    caps = []
    for t in ctx.font['cmap'].tables:
        if t.isUnicode():
            for u, g in sorted(t.cmap.items()):
                if unicodedata.category(chr(u)) == 'Lu' and g not in caps: caps.append(g)
    caps += ['Q.ss05'] + [b for _, b in ctx.case_pairs]
    ctx.cpsp_glyphs = caps
    ctx.gpos(f"lookup OTFEATURES_CPSP {{ pos [{J(caps)}] <{CPSP} 0 {2 * CPSP} 0>; }} OTFEATURES_CPSP;\n"
             f"feature cpsp {{ lookup OTFEATURES_CPSP; }} cpsp;")
    ctx.log(f'mark: {len(bases)} bases ({ctx.learned} anchors from precomposed glyphs), {len(ligs)} ligatures; cpsp: {len(caps)} glyphs')


# ---------------------------------------------------------------- post
AALT_FROM = ['ss04', 'ss05', 'ss06', 'ss07', 'ss08', 'case', 'zero', 'smcp', 'c2sc', 'onum', 'pnum', 'tnum',
             'sups', 'subs', 'sinf', 'numr', 'dnom', 'ordn', 'ss01', 'ss02', 'ss03', 'ss15', 'ss16'] + [f'cv{i:02d}' for i in range(1, 100)]
SALT_FROM = ['ss04', 'ss05', 'ss06', 'ss07', 'ss08']
INTERNAL = re.compile(r'(\.keep$|^spark|^pbar|^tag\.|\.tag$|^space\.|\.(vec|out|backc|fwdb|rn|cl)$)')


def _singles(table, idxs):
    """Single and alternate substitutions of these lookups and of the lookups their
    contextual rules call, in order: [(glyph, [alternates])]."""
    out, seen = [], set()

    def visit(i):
        if i in seen: return
        seen.add(i)
        lk = table.LookupList.Lookup[i]
        for st in lk.SubTable:
            t = lk.LookupType
            if t == 7: st = st.ExtSubTable; t = st.LookupType
            if t == 1: out.extend((a, [b]) for a, b in st.mapping.items())
            elif t == 3: out.extend((a, list(b)) for a, b in st.alternates.items())
            elif t in (5, 6):
                for obj in _walk(st):
                    if type(obj).__name__ in ('SubstLookupRecord', 'LookupRecord'): visit(obj.LookupListIndex)
    for i in idxs: visit(i)
    return out


def _walk(obj, seen=None):
    seen = seen if seen is not None else set()
    if id(obj) in seen: return
    seen.add(id(obj)); yield obj
    if isinstance(obj, list):
        for x in obj: yield from _walk(x, seen)
    elif hasattr(obj, '__dict__') and type(obj).__module__.startswith('fontTools.ttLib.tables.otTables'):
        for v in vars(obj).values():
            if isinstance(v, list) or hasattr(v, '__dict__'): yield from _walk(v, seen)


def _feature_lookups(table, tag):
    return sorted({i for fr in table.FeatureList.FeatureRecord if fr.FeatureTag == tag for i in fr.Feature.LookupListIndex})


def _alternates(table, tags, first=()):
    alts = {}
    for a, bs in first:
        for b in bs:
            if b != a and b not in alts.setdefault(a, []): alts[a].append(b)
    for tag in tags:
        for a, bs in _singles(table, _feature_lookups(table, tag)):
            if INTERNAL.search(a): continue
            for b in bs:
                if b == a or INTERNAL.search(b): continue
                if b not in alts.setdefault(a, []): alts[a].append(b)
    return {a: bs for a, bs in alts.items() if bs}


def _copy_kerning(ctx, pairs):
    """Add each new glyph to every pair-positioning subtable wherever its source is."""
    from fontTools.ttLib.tables import otTables as ot
    import copy, bisect
    font = ctx.font; gid = font.getGlyphID
    src_of = {}
    for a, b in pairs: src_of.setdefault(a, []).append(b)
    gpos = font['GPOS'].table; n = 0

    def cov_insert(cov, g):
        ids = [gid(x) for x in cov.glyphs]
        k = bisect.bisect_left(ids, gid(g)); cov.glyphs.insert(k, g); return k
    for lk in gpos.LookupList.Lookup:
        for st in lk.SubTable:
            if lk.LookupType == 9: st = st.ExtSubTable
            if type(st).__name__ != 'PairPos': continue
            if st.Format == 1:
                for ps in st.PairSet:
                    recs = ps.PairValueRecord; added = False
                    for r in list(recs):
                        for b in src_of.get(r.SecondGlyph, ()):
                            r2 = copy.deepcopy(r); r2.SecondGlyph = b; recs.append(r2); added = True; n += 1
                    if added:
                        recs.sort(key=lambda r: gid(r.SecondGlyph)); ps.PairValueCount = len(recs)
                for a, bs in src_of.items():
                    if a not in st.Coverage.glyphs: continue
                    srcps = st.PairSet[st.Coverage.glyphs.index(a)]
                    for b in bs:
                        if b in st.Coverage.glyphs: continue
                        k = cov_insert(st.Coverage, b); st.PairSet.insert(k, copy.deepcopy(srcps)); n += 1
                st.PairSetCount = len(st.PairSet)
            else:
                cd1, cd2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                for a, bs in src_of.items():
                    for b in bs:
                        if a in st.Coverage.glyphs and b not in st.Coverage.glyphs:
                            cov_insert(st.Coverage, b)
                            if a in cd1: cd1[b] = cd1[a]
                            n += 1
                        if a in cd2: cd2[b] = cd2[a]; n += 1
    return n


def _ligatures(table):
    """Every ligature substitution: {ligature: [component sequences]}."""
    out = {}
    for lk in table.LookupList.Lookup:
        for st in lk.SubTable:
            t = lk.LookupType
            if t == 7: st = st.ExtSubTable; t = st.LookupType
            if t != 4: continue
            for first, ls in st.ligatures.items():
                for l in ls: out.setdefault(l.LigGlyph, []).append([first] + list(l.Component))
    return out


def post(ctx):
    from fontTools.ttLib import TTFont
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    from fontTools.otlLib.builder import buildLigCaretList
    font = ctx.font; gsub = font['GSUB'].table
    # kerning for the new glyphs
    nk = _copy_kerning(ctx, ctx.case_pairs[1:] + ctx.zero_pairs)
    # GDEF: classes and carets
    cd = ctx.GDEF_CLASS
    ligdefs = _ligatures(gsub)
    new = [g for g in font.getGlyphOrder() if g not in ctx.mulish_glyphs]
    for g in new:                                     # a class another module set stays
        if g not in cd: cd[g] = 2 if g in ligdefs else 1
    alt_src = {}
    for a, bs in _singles(gsub, range(len(gsub.LookupList.Lookup))):
        for b in bs: alt_src.setdefault(b, a)

    def chars(g, depth=0):
        """The characters a ligature stands for: its components', expanded."""
        if depth > 6: return [g]
        if g in ligdefs:
            seqs = [sum((chars(c, depth + 1) for c in s), []) for s in ligdefs[g]]
            return max(seqs, key=len)
        if g in alt_src and g not in ctx.mulish_glyphs: return chars(alt_src[g], depth + 1)
        return [g]
    gd = font['GDEF'].table
    carets = {}
    if gd.LigCaretList:
        for g, lg in zip(gd.LigCaretList.Coverage.glyphs, gd.LigCaretList.LigGlyph):
            carets[g] = [c.Coordinate for c in lg.CaretValue]
    ncar = 0
    for g in new:
        if g not in ligdefs or g in carets: continue   # carets another module set stay
        cs = chars(g)
        if len(cs) < 2: continue
        fit = ctx.lig_fit.get(g)
        if fit and len(fit) == len(cs):
            ink = [ctx.path_of(p).bounds for p, _ in fit]
            cx = [round((fit[i - 1][1] + ink[i - 1][2] + fit[i][1] + ink[i][0]) / 2) for i in range(1, len(fit))]
        else:
            items, total = ctx.setting(cs)
            k = ctx.W(g) / total if total else 1
            cx = [round(x * k) for _, x in items[1:]]
        lo, out = 0, []
        for c in cx:                                  # inside the advance and increasing
            c = min(max(c, lo + 1), ctx.W(g) - 1); out.append(c); lo = c
        carets[g] = out; ncar += 1
    gd.LigCaretList = buildLigCaretList(carets, {}, font.getReverseGlyphMap())
    # aalt and salt: one alternate lookup each
    first = _singles(gsub, _feature_lookups(gsub, 'aalt'))
    aalt = _alternates(gsub, AALT_FROM, first)
    salt = _alternates(gsub, SALT_FROM)
    J = ' '.join
    fea = ('languagesystem DFLT dflt; languagesystem latn dflt;\n'
           'lookup OTFEATURES_AALT {\n' + ''.join(f'  sub {a} from [{J(bs)}];\n' for a, bs in aalt.items()) + '} OTFEATURES_AALT;\n'
           'lookup OTFEATURES_SALT {\n' + ''.join(f'  sub {a} from [{J(bs)}];\n' for a, bs in salt.items()) + '} OTFEATURES_SALT;\n'
           'feature xalt { lookup OTFEATURES_AALT; } xalt;\nfeature salt { lookup OTFEATURES_SALT; } salt;\n')
    tmp = TTFont(); tmp.setGlyphOrder(font.getGlyphOrder())
    addOpenTypeFeaturesFromString(tmp, fea, tables=['GSUB'])
    for fr in tmp['GSUB'].table.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'xalt': fr.FeatureTag = 'aalt'
    added = ctx._merge_table(gsub, tmp['GSUB'].table)
    aalt_i = added[0]
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'aalt':
            fr.Feature.LookupListIndex = [aalt_i]; fr.Feature.LookupCount = 1
    ctx.log(f'GDEF: {len(new)} glyphs classed ({sum(1 for g in new if cd[g] == 2)} ligatures, {ncar} with carets); '
            f'aalt {len(aalt)} glyphs, salt {len(salt)}; {nk} kerning entries copied')

"""punctuation: twelve punctuation marks and three letterlike symbols, each made from
the marks and letters it is a form of, at each weight.

What it adds (all fourteen styles; the drawing runs on the unslanted outlines, so an
italic's marks lean with its letters once build.py reslants it, the mirrored ones
included):

- ⸺ ⸻ (U+2E3A, U+2E3B, two- and three-em dash): two and three em dashes end to end,
  one bar with no gap (bridged at the joints, which in an italic meet within a fraction
  of a unit), advances twice and three times the em dash's.
- ⁓ (U+2053, swung dash): the tilde stretched sideways to the em dash's width less the
  tilde's own sidebearings, centred on the em dash's height; its strokes keep the
  tilde's vertical thickness.
- ‛ ‟ (U+201B, U+201F, high-reversed-9 quotation marks): ’ and ” mirrored about the
  middle of their advance (so their sidebearings swap).
- ‱ (U+2031, per ten thousand): ‰ with its last ring repeated at the step between its
  two lower rings; the advance grows by that step.
- ‽ (U+203D, interrobang): the ?'s hook with the !'s tapered stem standing over the dot
  (the two dots are one), from the ?'s foot up to the top of the arc, cut flush with it.
  The hook opens around the stem: its left terminal moves out until the white beside the
  stem is IB_SIDE of the ?'s aperture, and its bowl moves right until the counter is
  IB_OPEN of it, so the counter stays open in Black; the advance grows by the moves
  (Regular 506 against the ?'s 442, Black 680 against 478).
- ‧ (U+2027, hyphenation point): the middle dot, centred on the hyphen's height, with
  half its sidebearings.
- ‼ ⁇ (U+203C, U+2047): two ! and two ?, the gap between them GAP_DBL of the gap two
  typed marks have, but not under DBL_MIN of the lowercase stem (Black's ! is so wide at
  the top that 0.75 of its typed gap all but closed it), nor over the typed gap.
- ⸮ (U+2E2E, reversed question mark): the ? mirrored about the middle of its advance, its
  dot drawn again round (build.py's `dot`), so it stays a circle in the italic.
- ⁑ (U+2051, two asterisks aligned vertically): two equal asterisks in a compact stack
  within the line, the lower one on the baseline, the upper one's top at the cap height, the
  lower one's top arm reaching up between the upper one's legs with DAST_GAP of the arm's
  width between them at the closest (as STIX Two stacks them, not the asterisk over the low
  asterisk ⁎, which would hang 0.17 em under the baseline). Each is the asterisk scaled by
  the largest k that fits, at most DAST_MAX (0.85 from Light to SemiBold, 0.80 at Bold, 0.72
  at Black; the italics 0.85 to 0.75), its outline offset out by DAST_WT of what the scaling
  took from the arm's width; sidebearings the asterisk's times k.
- ℃ ℉ (U+2103, U+2109): the degree sign followed by C or F, the letter moved in until
  the closest white between the ring and the letter, across the ring's height, is
  TUCK of what it is in °C or °F typed (unkerned).
- ℗ (U+2117, sound recording copyright): the ring of © with a P, the P made as Mulish
  makes the R of ®: scaled and its outline offset so that it is as tall as that R and
  its stem as wide, standing where the R stands.

Forms, where their models have them: small capitals (smcp and c2sc) of ‼ ⁇ ‽ ⸮ ‛ ‟ ‱
⸺ ⸻, made in the same way from the small capitals of ! ? ’ ” ‰ and the em dash; case
forms (case) of ⸺ ⸻ ‧ from those of the em dash and middle dot. Every glyph gets GDEF
class 1 (base). Kerning comes from the kern module's INHERIT table (‛ ‟ as ’ ”, ‼ ⁇ ‽ as
! ? ?, the dashes as the em dash, ℃ ℉ as the degree sign on the left and C or F on the
right); this module adds none.

Nothing existing is changed. U+2E2E, U+2E3A and U+2E3B are outside the Makefile's
older web subset ranges and are listed there; the others are in U+2000-206F and
U+2100-214F.
"""
import pathops
from fontTools.agl import UV2AGL

GAP_DBL = 0.75        # ‼ ⁇: the gap between the two marks, of the gap two typed marks have,
DBL_MIN = 0.5         # but no less than this much of the lowercase stem (nor more than typed)
TUCK = 0.5            # ℃ ℉: the white between ring and letter, of what °C / °F have unkerned
IB_SIDE = 0.3         # ‽: the white between the hook's left terminal and the stem, of the ?'s aperture
IB_OPEN = 0.65        # ‽: the counter between the stem and the bowl, of the ?'s aperture
NARROW = 0.5          # ‧: its sidebearings, of the middle dot's
DAST_GAP = 0.8        # ⁑: the closest white between the two asterisks, of the asterisk's arm width
DAST_WT = 0.6         # ⁑: of the arm width the scaling takes away, how much the outline offset gives back
DAST_MAX = 0.85       # ⁑: the asterisks' largest scale (the light weights would fit them larger, nested deep)


def _name(cp):
    return UV2AGL.get(cp, f'uni{cp:04X}')


def _contours(p):
    """The contours of p, each as a path."""
    out = []
    for c in p.contours:
        q = pathops.Path(); c.draw(q.getPen()); out.append(q)
    return out


def _join(paths):
    q = pathops.Path(); pen = q.getPen()
    for p in paths: p.draw(pen)
    return q


def glyphs(ctx):
    c = ctx
    path_of, W, mv, mirror, union, diff, transformed = c.path_of, c.W, c.mv, c.mirror, c.union, c.diff, c.transformed
    hspans, vspans, rect = c.hspans, c.vspans, c.rect
    order = set(c.font.getGlyphOrder())
    cmap = c.font.getBestCmap()
    made = ctx.pu_made = []
    ctx.pu_sc, ctx.pu_case = [], []            # (base glyph, small cap / case form)

    def put(name, path, adv, cp=None):
        assert name not in order, name
        assert cp is None or cp not in cmap, f'U+{cp:04X} already mapped to {cmap.get(cp)}'
        c.add(name, path, adv)
        c.GDEF_CLASS[name] = 1
        if cp is not None: c.map(cp, name)
        made.append(name)
        return name

    def forms(cp, build, models):
        """The glyph of cp built from models['']; its small cap from models['sc'] and its case
        form from models['case'], when those exist. build(names) -> (path, advance)."""
        base = _name(cp)
        put(base, *build(models['']), cp=cp)
        for suf, pairs in (('sc', ctx.pu_sc), ('case', ctx.pu_case)):
            src = models.get(suf)
            if src and all(s in order for s in src):
                pairs.append((base, put(f'{base}.{suf}', *build(src))))

    # ---- dashes ----------------------------------------------------------------------------
    def dashes(n):
        def build(src):
            d = src[0]; p = path_of(d); b = p.bounds
            # the copies meet edge to edge (an italic's within a fraction of a unit): a 4-unit
            # bridge at each joint makes them one bar at every weight
            joints = [rect(i * W(d) - 2, b[1], i * W(d) + 2, b[3]) for i in range(1, n)]
            return union(*[mv(p, i * W(d)) for i in range(n)], *joints), n * W(d)
        return build
    for cp, n in ((0x2E3A, 2), (0x2E3B, 3)):
        forms(cp, dashes(n), {'': ['emdash'], 'sc': ['emdash.sc'], 'case': ['emdash.case.otfeatures']})

    def swung(src):
        t, d = src
        p = path_of(t); b = p.bounds; lsb, rsb = b[0], W(t) - b[2]
        e = path_of(d).bounds; yc = (e[1] + e[3]) / 2
        k = (W(d) - lsb - rsb) / (b[2] - b[0])
        p = transformed(p, (k, 0, 0, 1, lsb - k * b[0], yc - (b[1] + b[3]) / 2))
        return p, W(d)
    forms(0x2053, swung, {'': ['asciitilde', 'emdash']})

    # ---- quotation marks and the reversed question mark: mirrored --------------------------
    def mirrored(src):
        s = src[0]; return mirror(path_of(s), W(s) / 2), W(s)

    def mirrored_dot(src):
        """Mirrored, and its round dot (the lowest contour) drawn again as a dot: in an italic
        the dot is a circle sheared back by the reslant, and mirrored it would lean the
        wrong way and come out an oval."""
        s = src[0]; cs = _contours(path_of(s))
        d = min(cs, key=lambda q: q.bounds[1]); b = d.bounds
        rest = mirror(_join([q for q in cs if q is not d]), W(s) / 2)
        return union(rest, c.dot(W(s) - (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, (b[3] - b[1]) / 2)), W(s)
    forms(0x201B, mirrored, {'': ['quoteright'], 'sc': ['quoteright.sc']})
    forms(0x201F, mirrored, {'': ['quotedblright'], 'sc': ['quotedblright.sc']})
    forms(0x2E2E, mirrored_dot, {'': ['question'], 'sc': ['question.sc']})

    # ---- doubled marks ---------------------------------------------------------------------
    lstem = (lambda sp: sp[1] - sp[0])(hspans(path_of('l'), 200)[0])     # the lowercase stem
    def doubled(src):
        s = src[0]; p = path_of(s); b = p.bounds
        typed = (W(s) - b[2]) + b[0]                       # two typed: right then left sidebearing
        gap = min(typed, max(GAP_DBL * typed, DBL_MIN * lstem))
        step = round(W(s) - (typed - gap))
        return union(p, mv(p, step)), step + W(s)
    forms(0x203C, doubled, {'': ['exclam'], 'sc': ['exclam.sc']})
    forms(0x2047, doubled, {'': ['question'], 'sc': ['question.sc']})

    # ---- interrobang -----------------------------------------------------------------------
    # The ?'s hook with the !'s own tapered stem standing over the dot (the two dots are one).
    # The stem runs from the ?'s foot up to the hook's top and is cut to the arc's outer edge,
    # so its top is flush with the arc. The hook is opened around it: its left terminal moves
    # out until the white between terminal and stem is IB_SIDE of the ?'s aperture (the white
    # beside the terminal's tip), and its bowl moves right until the counter between stem and
    # bowl is IB_OPEN of that aperture. The moves are a horizontal map of the hook's points:
    # the terminal and the bowl move whole (their strokes keep their thickness); the arc
    # between is stretched (a horizontal stroke, it keeps its thickness too); the bowl's move
    # fades out down to the foot, so the hook's tail still runs into the stem at the foot. The
    # advance grows by the two moves; the heavy weights, whose ! is wide at the top, open most.
    def interrobang(src):
        q, e = src
        qcs = _contours(path_of(q))
        hook = max(qcs, key=lambda k: k.bounds[3]); qdot = min(qcs, key=lambda k: k.bounds[1])
        hb, db = hook.bounds, qdot.bounds
        cx = (db[0] + db[2]) / 2                                 # the stem stands over the dot
        fa = hspans(hook, hb[1] + 1)[0][0]                       # the left of the ?'s foot
        # the left terminal: its tip (the lowest ink left of the foot, in the hook's upper part)
        # and its free rows up to where it meets the arc
        tips = [v[0][0] for v in (vspans(hook, x) for x in range(int(hb[0]) + 1, int(fa))) if v]
        tb = min(t for t in tips if t > hb[1] + (hb[3] - hb[1]) / 3)
        rows, y = [], tb + 2
        while True:
            sp = hspans(hook, y)
            if len(sp) < 2 or sp[0][1] > cx: break
            rows.append((y, sp[0][1], sp[1][0])); y += 2
        ap = rows[0][2] - rows[0][1]                             # the ?'s aperture
        low = [r for r in rows if r[0] < (rows[0][0] + rows[-1][0]) / 2]   # the terminal's lower half
        term_r = min(max(r[1] for r in low), fa - 1)
        yr = max(range(int(hb[1]) + 2, int(hb[3]) - 2, 2), key=lambda y: hspans(hook, y)[-1][1])
        inner = max(hspans(hook, yr)[-1][0], fa + 1)             # the bowl's inner edge, at its widest
        ecs = _contours(path_of(e)); st = max(ecs, key=lambda k: k.bounds[3]); sb = st.bounds
        k = (hb[3] + 40 - hb[1]) / (sb[3] - sb[1])               # run up past the arc, cut below
        stem0 = transformed(st, (1, 0, 0, k, cx - (sb[0] + sb[2]) / 2, hb[1] - k * sb[1]))

        def build(dl, dr):
            def f(pt):
                x, y = pt
                if x <= term_r: return (x - dl, y)
                if x < fa: return (x - dl * (fa - x) / (fa - term_r), y)
                up = min(1, max(0, (y - hb[1]) / (yr - hb[1])))
                return (x + dr * up * min(1, (x - fa) / (inner - fa)), y)
            h = [k_ for k_ in _contours(path_of(q, fn=f)) if k_.bounds[3] > db[3] + 1][0]
            s0 = stem0.bounds
            xs = [s0[0] - 2 + i * (s0[2] - s0[0] + 4) / 40 for i in range(41)]
            tops = [max((v[1] for v in vspans(h, x)), default=hb[1]) for x in xs]
            under = c.poly([(xs[0], hb[1] - 10)] + list(zip(xs, tops)) + [(xs[-1], hb[1] - 10)])
            return union(h, pathops.op(stem0, under, pathops.PathOp.INTERSECTION), qdot)

        def side(out):                                           # white between terminal and stem
            return min((s[1][0] - s[0][1]) if len(s) >= 2 else 0 for s in (hspans(out, r[0]) for r in low))

        def counter(out):
            hs = [k_ for k_ in _contours(out) if k_.bounds[1] > db[3] + 1 and k_.bounds[3] < hb[3] - 1]
            return (hs[0].bounds[2] - hs[0].bounds[0]) if len(hs) == 1 else 0
        dl = 0
        while side(build(dl, 0)) < IB_SIDE * ap:
            dl += 2; assert dl < 300, (q, 'terminal')
        dr = 0
        while counter(out := build(dl, dr)) < IB_OPEN * ap:
            dr += 2; assert dr < 400, (q, 'counter')
        return mv(out, dl), W(q) + dl + dr
    forms(0x203D, interrobang, {'': ['question', 'exclam'], 'sc': ['question.sc', 'exclam.sc']})

    # ---- per ten thousand ------------------------------------------------------------------
    def per_ten_thousand(src):
        s = src[0]; p = path_of(s); cs = _contours(p)
        # the rings: an outer contour and the counter inside it; the slash is the tallest contour
        slash = max(cs, key=lambda q: q.bounds[3] - q.bounds[1])
        outers = [q for q in cs if q is not slash and not any(
            o is not q and o is not slash and o.bounds[0] < q.bounds[0] and o.bounds[2] > q.bounds[2]
            and o.bounds[1] < q.bounds[1] and o.bounds[3] > q.bounds[3] for o in cs)]
        lower = sorted((q for q in outers if q.bounds[1] < p.bounds[1] + 1), key=lambda q: q.bounds[0])
        assert len(outers) == 3 and len(lower) == 2, (s, [q.bounds for q in outers])
        step = lower[1].bounds[0] - lower[0].bounds[0]
        lb = lower[1].bounds
        ring = _join([q for q in cs if q is not slash and q.bounds[0] >= lb[0] and q.bounds[2] <= lb[2]
                      and q.bounds[1] >= lb[1] and q.bounds[3] <= lb[3]])
        return union(p, mv(ring, step)), W(s) + step
    forms(0x2031, per_ten_thousand, {'': ['perthousand'], 'sc': ['perthousand.sc']})

    # ---- hyphenation point -----------------------------------------------------------------
    def hyph_point(src):
        d, h = src
        p = path_of(d); b = p.bounds; hb = path_of(h).bounds
        p = mv(p, -NARROW * b[0], (hb[1] + hb[3]) / 2 - (b[1] + b[3]) / 2)
        return p, W(d) - (1 - NARROW) * (b[0] + W(d) - b[2])
    forms(0x2027, hyph_point, {'': ['periodcentered', 'hyphen'], 'case': ['periodcentered.case.otfeatures', 'hyphen.case']})

    # ---- two asterisks ---------------------------------------------------------------------
    # Two equal asterisks stacked within the line: the lower one on the baseline, the upper one's
    # top at the cap height, the lower one's top arm reaching up between the upper one's legs
    # with DAST_GAP of the arm's width between them at the closest. Both are the asterisk scaled
    # by k, the outline then offset out by DAST_WT of what the scaling took from half the arm's
    # width, so the smaller arms look as heavy as the asterisk's (a smaller figure needs relatively
    # heavier strokes, as small capitals do); k is the largest that fits the pair in the cap
    # height, but no more than DAST_MAX (where k is capped the gap is wider than DAST_GAP).
    # Sidebearings are the asterisk's times k.
    ch = path_of('H').bounds[3]

    def dilate(p, e):
        q = pathops.Path(); p.draw(q.getPen())
        q.stroke(2 * e, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
        return union(p, q)

    def two_asterisks(src):
        s = src[0]; p = path_of(s); b = p.bounds
        arm = (lambda sp: sp[1] - sp[0])(hspans(p, b[3] - 0.15 * (b[3] - b[1]))[0])   # the top arm, near its end
        gap = DAST_GAP * arm

        def stack(k):
            one = dilate(transformed(p, (k, 0, 0, k, 0, 0)), DAST_WT * (1 - k) * arm / 2); ob = one.bounds
            one = mv(one, k * b[0] - ob[0], -ob[1])                # on the baseline, the left sidebearing scaled
            near_ = dilate(one, gap)                               # the white the upper one keeps from it
            lo, hi = 0.0, 2 * (ob[3] - ob[1])                      # the upper one's rise: touching, clear
            while hi - lo > 0.25:
                m = (lo + hi) / 2
                if not list(pathops.op(near_, mv(one, 0, m), pathops.PathOp.INTERSECTION).contours): hi = m
                else: lo = m
            return one, hi
        lo, hi = 0.5, DAST_MAX + 0.002
        while hi - lo > 0.002:                                     # the largest k whose pair fits the cap height
            k = (lo + hi) / 2; one, rise = stack(k)
            if rise + one.bounds[3] <= ch: lo = k
            else: hi = k
        lo = min(lo, DAST_MAX)
        one, rise = stack(lo); rise += ch - (rise + one.bounds[3])  # the top exactly at the cap height (the gap opens if k is capped)
        ob = one.bounds
        ctx.pu_dast = (lo, arm, gap)
        return _join([one, mv(one, 0, rise)]), ob[2] + lo * (W(s) - b[2])
    forms(0x2051, two_asterisks, {'': ['asterisk']})

    # ---- degree Celsius and Fahrenheit -----------------------------------------------------
    def degree_letter(src):
        deg, L = src
        r = path_of('degree'); rb = r.bounds; lp = path_of(L)
        ys = [rb[1] + (rb[3] - rb[1]) * i / 24 for i in range(1, 24)]

        def white(dx):
            """The narrowest white between the ring and the letter (moved by dx), across the ring's height."""
            best = None
            for y in ys:
                a, bb = hspans(r, y), hspans(lp, y)
                if a and bb:
                    w = bb[0][0] + dx - a[-1][1]
                    best = w if best is None else min(best, w)
            return best
        w0 = white(W(deg))                                       # as typed, unkerned
        dx = W(deg) - (1 - TUCK) * w0
        return union(r, mv(lp, dx)), dx + W(L)
    forms(0x2103, degree_letter, {'': ['degree', 'C']})
    forms(0x2109, degree_letter, {'': ['degree', 'F']})

    # ---- sound recording copyright ---------------------------------------------------------
    def phonogram(src):
        cr, rg, R, P = src
        def ring_and_rest(n):
            cs = sorted(_contours(path_of(n)), key=lambda q: -(q.bounds[2] - q.bounds[0]) * (q.bounds[3] - q.bounds[1]))
            return _join(cs[:2]), _join(cs[2:])
        ring, _ = ring_and_rest(cr)
        _, r_in = ring_and_rest(rg)
        rb = r_in.bounds; Rp = path_of(R); Rb = Rp.bounds
        row = lambda b: b[1] + 0.2 * (b[3] - b[1])          # through the stems, below the bowls
        stem = hspans(Rp, row(Rb))[0]; stem_in = hspans(r_in, row(rb))[0]
        sw, sw_in = stem[1] - stem[0], stem_in[1] - stem_in[0]
        # scale k and outline offset e with k R + 2e = the inner R's height and k stem + 2e = its stem
        k = ((rb[3] - rb[1]) - sw_in) / ((Rb[3] - Rb[1]) - sw)
        e = (sw_in - k * sw) / 2
        p = transformed(path_of(P), (k, 0, 0, k, 0, 0))
        if abs(e) > 0.05:
            q = pathops.Path(); p.draw(q.getPen())
            q.stroke(2 * abs(e), pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
            p = union(p, q) if e > 0 else diff(p, q)
        pb = p.bounds
        ps = hspans(p, row(pb))[0]
        p = mv(p, stem_in[0] - ps[0], rb[1] - pb[1])
        return union(ring, p), W(cr)
    forms(0x2117, phonogram, {'': ['copyright', 'registered', 'R', 'P']})

    ctx.log(f'{len(made)} glyphs: {" ".join(made)}')


def features(ctx):
    J = ' '.join
    sc, case = ctx.pu_sc, ctx.pu_case
    fea = ''
    if sc:
        fea += (f'lookup PUNCTUATION_SC {{ sub [{J(a for a, _ in sc)}] by [{J(b for _, b in sc)}]; }} PUNCTUATION_SC;\n'
                f'feature smcp {{ lookup PUNCTUATION_SC; }} smcp;\n'
                f'feature c2sc {{ lookup PUNCTUATION_SC; }} c2sc;\n')
    if case:
        fea += (f'lookup PUNCTUATION_CASE {{ sub [{J(a for a, _ in case)}] by [{J(b for _, b in case)}]; }} PUNCTUATION_CASE;\n'
                f'feature case {{ lookup PUNCTUATION_CASE; }} case;\n')
    if fea: ctx.gsub(fea, before='main')

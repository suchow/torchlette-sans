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
- ‽ (U+203D, interrobang): the ? with the stem of a ! set on its dot (the two dots are
  one): a straight stem of the ?'s own stem width, from where the ?'s stem ends above the
  dot up into the arc, stopping just inside the arc's outer edge; in the heavy weights
  its right side moves in until the hook's counter is IB_COUNTER of its width; the ?'s
  advance.
- ‧ (U+2027, hyphenation point): the middle dot, centred on the hyphen's height, with
  half its sidebearings.
- ‼ ⁇ (U+203C, U+2047): two ! and two ?, the gap between them GAP_DBL of the gap two
  typed marks have, but not under DBL_MIN of the lowercase stem (Black's ! is so wide at
  the top that 0.75 of its typed gap all but closed it), nor over the typed gap.
- ⸮ (U+2E2E, reversed question mark): the ? mirrored about the middle of its advance, its
  dot drawn again round (build.py's `dot`), so it stays a circle in the italic.
- ⁑ (U+2051, two asterisks aligned vertically): the asterisk over the low asterisk ⁎
  (U+204E), the asterisk's advance.
- ℃ ℉ (U+2103, U+2109): the degree sign followed by C or F, the letter moved in until
  the closest white between the ring and the letter, across the ring's height, is
  TUCK of what it is in °C or °F typed (unkerned).
- ℗ (U+2117, sound recording copyright): the ring of © with a P, the P made as Mulish
  makes the R of ®: scaled and its outline offset so that it is as tall as that R and
  its stem as wide, standing where the R stands.

Forms, where their models have them: small capitals (smcp and c2sc) of ‼ ⁇ ‽ ⸮ ‛ ‟ ‱
⸺ ⸻, made in the same way from the small capitals of ! ? ’ ” ‰ and the em dash; case
forms (case) of ⸺ ⸻ ‧ from those of the em dash and middle dot. Every glyph gets GDEF
class 1 (base). Kerning comes from the kern module's INHERIT table (‛ ‟ as ‘ “, ‼ ⁇ as
! ?, the dashes as the em dash, ℃ ℉ as the degree sign on the left and C or F on the
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
IB_COUNTER = 0.4     # ‽: the hook's counter, at least this much of the stem's width
NARROW = 0.5          # ‧: its sidebearings, of the middle dot's


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
    # The ! stands on the ?'s dot: a straight stem of the ?'s own stem width, centred on the
    # ?'s stem where it ends above the dot, run up into the arc and stopped below the arc's
    # outer edge, so it neither shows above the arc nor fills the hook (the !'s own stem,
    # which widens upwards, filled the hook of Black's ? and stood out above its terminal).
    def interrobang(src):
        q = src[0]; p = path_of(q)
        hook = max(_contours(p), key=lambda c: c.bounds[3])
        y0 = hook.bounds[1]                                     # where the ?'s stem ends, above the dot
        a, b = hspans(p, y0 + 1)[0]                              # its foot, so the stem's sides run on from it
        top = min(vspans(p, x)[-1][1] for x in (a + 0.5, (a + b) / 2, b - 0.5)) - 1

        def with_stem(r):
            out = union(p, rect(a, y0, r, top))
            holes = [c for c in _contours(out) if c.bounds[1] > y0 and c.bounds[3] < hook.bounds[3] - 1]
            return out, (holes[0].bounds[2] - holes[0].bounds[0]) if holes else 0
        # In the heavy weights the hook comes back close to the stem; the stem's right side
        # moves in (never past the middle of the foot) until the counter left between them is
        # IB_COUNTER of the stem's width (Black's would be a 25-unit slit, its small cap's shut).
        r = b
        out, cw = with_stem(r)
        while cw < IB_COUNTER * (r - a) and r - 1 > (a + b) / 2:
            r -= 1; out, cw = with_stem(r)
        return out, W(q)
    forms(0x203D, interrobang, {'': ['question'], 'sc': ['question.sc']})

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
    forms(0x2051, lambda src: (union(path_of(src[0]), path_of(src[1])), W(src[0])), {'': ['asterisk', 'uni204E']})

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

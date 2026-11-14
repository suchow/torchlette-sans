"""currency: four currency signs, ₿ ₪ ₾ ₨, drawn at each weight from the letters, figures and
currency signs they are kin to.

Mulish's own currency signs ($ ¢ £ ¥ € ₹ ₽ ₺ ₩ ₫ ₦ ₴ ₸ ₱) are all on the tabular figure
width (the zero's advance), have no proportional, old-style or small-cap forms, are not
kerned, and draw their extra strokes thinner than the letters: the $'s stroke, which runs
115 units past cap height and the baseline, and the bars of € ₽ ₩ ₹. The new signs follow
them; ₪ ₾ ₨ are too wide for the figure width and have their own (below).

What it adds (all fourteen styles; the drawing runs on the unslanted outlines, so an
italic's signs lean with its letters once build.py reslants it):

- ₿ (U+20BF, bitcoin sign): the B with two short strokes above it and two below, in the $'s
  stroke weight and reaching as far above cap height and below the baseline as the $'s
  stroke. The left pair stands over the stem (flush with its right side), the right pair
  as far from it as the two bars of € are apart; above and below, the strokes are aligned.
  Where the B is wider than the ink of ₽ (the heavy weights) a slice of its flat bars just
  right of the stem is taken out, so the stems and bowls keep their weight. On the figure
  width, centred.
- ₪ (U+20AA, new sheqel sign): two interlocked square hooks: a left stem with a top bar and
  an inner right stem that stops short of the baseline, and turned round inside it a right
  stem with a bottom bar and an inner left stem that stops short of the top (SH_END of the
  cap height from the bar it does not reach). Square corners, as the font's Π and ₸ have.
  Its four stems are the ₽'s stem (which is the H's), its bars the ₽'s bowl top, as heavy
  as its neighbours in every weight; the three counters equal, as wide as leaves the ink
  the H's, or as €'s bars are apart where that is wider (from Bold on), so the heavy
  weights' ₪ grows wider rather than lighter (Black's ink 880, as SF's heavy ₪ is wide).
  Its own width (ink plus the n's left sidebearing on each side), wider than the figure width.
- ₾ (U+20BE, lari sign): a round bowl with its lower right quarter taken away, standing on a
  bar along the baseline as wide as the bowl and as deep as its bottom stroke, which it
  carries on; two strokes in the $'s stroke weight, as far apart as the bars of €, rise
  from the bowl's middle, where its right side ends, through its top to the height of the
  $'s stroke. The bowl is the O narrowed to LA_BOWL of €'s ink width (the O's own width made
  the sign the biggest of its kin), its outer and inner outlines narrowed apart so that its
  sides keep €'s side weight and its top and bottom the O's; it is a rounder cap-height
  zero (the zero's own ring read as a C, and with the strokes as the cedi sign ₵). Where
  the two strokes would not fit inside it with LA_CLEAR of €'s bar gap beside each (from
  Bold on, as the $'s stroke grows) the bowl is widened until they do: strokes stopped at
  its top instead read as a crowned C. The O's sidebearings.
- ₨ (U+20A8, rupee sign): R and s set close as one sign, the s moved in until the
  narrowest white between them, over the s's height, is RS_TUCK of what it is in Rs typed
  (unkerned); its advance R's plus s's less that.

Every glyph gets GDEF class 1 (base); none has small capitals or case forms, nor kerning
(their kin have none). Nothing existing is changed. U+20A0-20CF is in the Makefile's web
subset ranges.
"""
from fontTools.agl import UV2AGL

LA_BOWL = 1.02        # ₾: its bowl this much of €'s ink width
LA_CLEAR = 0.4        # ₾: the white beside each stroke inside the bowl, at least this much of €'s bar gap
SH_END = 0.30         # ₪: an inner stem stops this much of the cap height from the far side
RS_TUCK = 0.5         # ₨: the white between R and s, of what Rs typed has unkerned


def _name(cp):
    return UV2AGL.get(cp, f'uni{cp:04X}')


def glyphs(ctx):
    c = ctx
    path_of, W, mv, union, diff, clip, rect = c.path_of, c.W, c.mv, c.union, c.diff, c.clip, c.rect
    hspans, vspans = c.hspans, c.vspans
    order = set(c.font.getGlyphOrder())
    cmap = c.font.getBestCmap()
    made = ctx.cu_made = []

    def put(cp, path, adv):
        name = _name(cp)
        assert name not in order, name
        assert cp not in cmap, f'U+{cp:04X} already mapped to {cmap.get(cp)}'
        c.add(name, path, adv)
        c.GDEF_CLASS[name] = 1
        c.map(cp, name)
        made.append(name)

    # ---- the kin's measures -------------------------------------------------------------
    FIG = W('zero')                                         # the figure width, all the signs' advance
    cap = path_of('H').bounds[3]
    db = path_of('dollar').bounds
    d_top, d_bot = db[3], db[1]                              # the $'s stroke, above and below
    a, b = hspans(path_of('dollar'), (cap + d_top) / 2)[0]
    stroke = b - a                                           # its weight
    eu = path_of('Euro'); eb = eu.bounds
    bars = vspans(eu, eb[0] + 0.08 * (eb[2] - eb[0]))       # the two bars of €, left of the bowl
    assert len(bars) == 2, ('Euro bars', bars)
    bar = sum(q - p for p, q in bars) / 2                    # the currency signs' bar weight
    gap = bars[1][0] - bars[0][1]                            # and how far apart €'s bars are
    hb_ = path_of('H').bounds
    stem = (lambda s: s[1] - s[0])(hspans(path_of('H'), 0.3 * cap)[0])

    # ---- ₿ ------------------------------------------------------------------------------
    B = path_of('B'); bb = B.bounds
    s0, s1 = hspans(B, 0.25 * cap)[0]                        # the stem
    target = path_of('uni20BD').bounds; target = target[2] - target[0]
    cut = round((bb[2] - bb[0]) - target)          # whole units, so the reslant gives back the B's own points
    if cut > 0:
        # take a slice of width cut out of the flat bars just right of the stem
        x0 = round(s1) + 2
        flat = vspans(B, x0)
        assert len(flat) == 3 and all(abs(p[0] - q[0]) < 0.5 and abs(p[1] - q[1]) < 0.5
                                       for p, q in zip(flat, vspans(B, x0 + cut + 1))), ('B not flat', flat)
        B = union(clip(B, (-1000, -1000, x0, 2000)), mv(clip(B, (x0 + cut, -1000, 3000, 2000)), -cut))
        bb = B.bounds
    dx = round((FIG - (bb[2] - bb[0])) / 2 - bb[0])
    B = mv(B, dx); s1 += dx
    v = vspans(B, s1 + 1)                                    # the top and bottom bars, by the stem
    bot_t, top_t = v[0][1] - v[0][0], v[-1][1] - v[-1][0]
    ticks = []                                               # each runs half into its bar
    for xl in (s1 - stroke, s1 + gap):
        ticks += [rect(xl, cap - top_t / 2, xl + stroke, d_top), rect(xl, d_bot, xl + stroke, bot_t / 2)]
    put(0x20BF, union(B, *ticks), FIG)

    # ---- ₪ ------------------------------------------------------------------------------
    s = stem                                                 # the ₽'s stem, which is the H's
    rb_ = path_of('uni20BD').bounds
    t = (lambda v: v[1] - v[0])(vspans(path_of('uni20BD'), rb_[0] + 0.45 * (rb_[2] - rb_[0]))[-1])   # ₽'s bowl top
    k = round(max(gap, (hb_[2] - hb_[0] - 4 * s) / 3))       # counters: the H's width, or €'s bar gap if wider
    ink = 4 * s + 3 * k
    sb = path_of('n').bounds[0]
    xs = [sb + i * (s + k) for i in range(4)]
    end = SH_END * cap
    hook_a = union(rect(xs[0], 0, xs[0] + s, cap), rect(xs[0], cap - t, xs[2] + s, cap), rect(xs[2], end, xs[2] + s, cap))
    hook_b = union(rect(xs[3], 0, xs[3] + s, cap), rect(xs[1], 0, xs[3] + s, t), rect(xs[1], 0, xs[1] + s, cap - end))
    put(0x20AA, union(hook_a, hook_b), ink + 2 * sb)

    # ---- ₾ ------------------------------------------------------------------------------
    O = path_of('O'); ob = O.bounds
    side = (lambda s_: s_[0][1] - s_[0][0])(hspans(eu, cap / 2))    # €'s bowl, at its side
    cs = sorted(O.contours, key=lambda q: q.bounds[2] - q.bounds[0])
    inner, outer = cs[0], cs[-1]
    ox = (ob[0] + ob[2]) / 2
    span = 2 * stroke + gap                                  # the two strokes, which run down into the bowl
    bw = round(max(LA_BOWL * (eb[2] - eb[0]),                # the bowl: €'s width, or wider where the
                   span + 2 * LA_CLEAR * gap + 2 * side))    # strokes would not fit inside it otherwise
    ib = inner.bounds
    sx = lambda p_, w0, w1: c.transformed(p_, (w1 / w0, 0, 0, 1, ox - ox * w1 / w0, 0))
    Z = diff(sx(outer, ob[2] - ob[0], bw), sx(inner, ib[2] - ib[0], bw - 2 * side))
    zb = Z.bounds
    cx, cy = round((zb[0] + zb[2]) / 2), (zb[1] + zb[3]) / 2
    ring = clip(diff(Z, rect(cx, -1000, 3000, cy)), (-1000, 0, 3000, 2000))
    base = vspans(Z, cx - 1)[0][1]                           # the top of the bowl's bottom stroke: the bar
    lari = union(ring, rect(zb[0], 0, zb[2], base),          # carries the ring's bottom on, no step
                 rect(cx - gap / 2 - stroke, cy, cx - gap / 2, d_top), rect(cx + gap / 2, cy, cx + gap / 2 + stroke, d_top))
    lsb = ob[0]
    lari = mv(lari, round(lsb - zb[0]))
    put(0x20BE, lari, round(bw + 2 * lsb))

    # ---- ₨ ------------------------------------------------------------------------------
    R, S = path_of('R'), path_of('s'); sbb = S.bounds
    ys = [sbb[1] + (sbb[3] - sbb[1]) * i / 24 for i in range(1, 24)]

    def white(off):
        best = None
        for y in ys:
            p, q = hspans(R, y), hspans(S, y)
            if p and q:
                w = q[0][0] + off - p[-1][1]
                best = w if best is None else min(best, w)
        return best
    w0 = white(W('R'))
    off = round(W('R') - (1 - RS_TUCK) * w0)
    put(0x20A8, union(R, mv(S, off)), off + W('s'))

    ctx.log(f'{len(made)} glyphs: {" ".join(made)}')

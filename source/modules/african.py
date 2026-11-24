"""african: the letters of African orthographies that Mulish lacks (issue 34), 38 letters in 19
case pairs, drawn at each weight from the letters, hooks, tails and bars Mulish already has, but
for Ɣ ɣ Ʋ ʋ, which are Noto Sans's, fitted.

What it adds (all fourteen styles; the drawing runs on the unslanted outlines, so an italic's
letters lean with its letters once build.py reslants it, the turned and mirrored ones too):

- Ɔ ɔ (U+0186, U+0254): C and c turned (not mirrored), so the sidebearings swap.
- Ǝ (U+018E): E mirrored. ǝ (U+01DD): Mulish's ə (U+0259), which is e turned.
- Ɛ ɛ (U+0190, U+025B): Mulish's own Cyrillic З з mirrored (Mulish's weights, its c's
  terminals).
- Ʒ ʒ (U+01B7, U+0292): Mulish's Cyrillic Ӡ ӡ (U+04E0, U+04E1), the same letters.
- Ʇ (U+A7B1): T turned. ʇ (U+0287): t turned about the middle of the x-height, so its hook is at
  the x-height, its bar on the baseline and its top below it, as the turned t is drawn.
- Ɖ (U+0189): Đ. ɖ (U+0256): d whose stem runs on below the baseline into ŋ's tail turned to the
  right.
- Ɲ ɲ (U+019D, U+0272): N and n with Ŋ's and ŋ's tail (which turns left) under the left stem; the
  ink starts where J's and j's tails start.
- ƙ ƭ (U+0199, U+01AD): k and t with ɓ's hooked ascender on the stem. ƥ (U+01A5): p whose stem
  runs up into ɓ's ascender and hook.
- Ƥ (U+01A4): P with Ɓ's hook, moved over as Ɓ's B is. Ƭ (U+01AC): T whose bar ends on the left
  in Ɓ's hook, its outer edge where the bar ended.
- Ƙ (U+0198): K whose upper arm ends in ɓ's hook (as ƙ's stem does), KH_F times as large, its
  stroke thinned back to the arm's weight, its stem turned to the arm's slope, slid along the
  arm until its top is the O's overshoot above the cap height: the arm curls over to the right
  and down, unmistakably not K's at text size (Ƴ's flatter arm-end, used before, was not).
- Ʋ ʋ Ɣ ɣ (U+01B2, U+028B, U+0194, U+0263): not drawn here but Noto Sans's, fitted (BORROW):
  Noto's outline mapped vertically by the line through its x-height or cap height and the
  bottom of its y (ɣ), o (ʋ) or O (Ɣ Ʋ) onto Torchlette's, so the descender and overshoot are
  Torchlette's, and horizontally by Torchlette's v, u, V or U width over Noto's. Of Noto's
  static weights (NOTO_W) the one whose fitted stroke (the left arm across it for Ɣ ɣ, against
  v's or V's; the left stem for Ʋ ʋ, against u's or U's) is nearest is taken, and the rest of
  the difference made up by offsetting the outline evenly, half each side (at most 6 units),
  its height then put back. Sidebearings are the model's. Ɣ's loop hangs below the baseline, as
  Noto draws it. Noto Sans (Copyright 2022 The Noto Project Authors,
  https://github.com/notofonts/latin-greek-cyrillic) is licensed under the SIL Open Font
  License 1.1 with no Reserved Font Name; the files are `../notosans/NotoSans-AfricanSubset-
  <weight>.ttf` (README has their source), its OFL.txt beside them. Nothing is named after it.
- Ɩ ɩ (U+0196, U+0269): I and ı whose stem ends in t's foot (scaled to I's stem).
- Ʊ (U+01B1): Ω upside down, its feet on top at the cap height. ʊ (U+028A): the small capital Ʊ
  scaled to the x-height and to UPS_W of o's width, its strokes thickened back to the
  lowercase's (the stems to n's, the bottom to o's).
- Ƀ ƀ Ɨ ɨ Ʉ ʉ (U+0243, U+0180, U+0197, U+0268, U+0244, U+0289): the barred letters, their bars
  measured on Mulish's: Ƀ's crosses the stem at the middle of the lower bowl with Đ's weight
  and overhang (into the counter no more than BAR_B of its width); ƀ's is ħ's; Ɨ's and Ʉ's are
  Đ's, at its height, past each stem by Đ's overhang; ɨ's and ʉ's are đ's weight across the
  middle of the x-height, past the stem by đ's overhang (BAR_I, BAR_LC of it).
- Ƿ ƿ (U+01F7, U+01BF): wynn: P and p, the top of the bowl kept, its right side running down
  in a curve into a straight stroke (of the bowl's side weight) that meets the stem at WY_MEET
  of the cap height (Ƿ) or TT_DEPTH of the x-height (ƿ).
- Ꞌ ꞌ (U+A78B, U+A78C): saltillo: ꞌ is the straight quote; Ꞌ the quote lengthened from the cap
  height down to SALT_L of it (Noto Sans's Ꞌ is about 0.7 of its cap height), so 1.6 to 1.8
  times as long as ꞌ, its width and taper kept; ı's sidebearings, as letters.
- ǀ ǁ ǂ ǃ (U+01C0–01C3): uncased click letters, with stems measured from l, text
  sidebearings, and a dot on ǃ. Small-cap forms use I.sc's stem and H.sc's height;
  both smcp and c2sc select them. The default forms remain in ordinary capital text.
- Ɵ ɵ (U+019F, U+0275): O and o with a bar across the counter. Ʌ ʌ
  (U+0245, U+028C): V and v turned, with sidebearings exchanged.
- Ɠ ɠ (U+0193, U+0260): G and single-storey g with a right-facing hook on
  the upper right. The hook comes from ɓ and is fitted to each outline.

Small capitals: each pair has one, which smcp gives for the lowercase and c2sc for the capital
(<capital>.sc.african), drawn by the same rule from the small capitals of the models (C.sc,
Ɓ's uni0181.sc, Eng.sc ...) or, where build.py has none (З Ӡ Ω Đ, and ɓ for Ƙ's hook), from
build.py's sc_path, the heavier instance at small-cap size, as build.py draws its own. (Ɖ.sc is
D.sc with the bar measured on sc_path('Dcroat'), the same outline as build.py's Dcroat.sc,
which since issue 50 puts the heavier instance's bar across D.sc's stem in the same way.)

Every glyph gets GDEF class 1 (base). Kerning (post): each letter kerns on each side as the
letter whose side it has (KERN), its small capital as the models' small capitals: the letter is
put into its models' classes and pair sets in the finished GPOS's kern lookups (a few bytes;
the same pairs as a list would be some 16,000 per style, about 10 KB of the web font), and
AFRICAN_KERN, after all the others, sets right any pair that would then differ from the copy.
Mark attachment comes from the otfeatures module (DRAWN_ON, MIRRORED, OWN_SHAPE). ccmp: the
capitals take the .case marks above, as Mulish's Latin capitals do (AFRICAN_CASEMARK, with
Mulish's own mapping); ɨ, soft-dotted, takes its dotless form uni0268.dotless.african before a
mark above, by Mulish's own rule for i and j (AFRICAN_SOFTDOT). Nothing existing is changed but
the kern lookups' classes and pair sets, which gain the new letters. U+0180-024F and
U+0250-02FF are in the Makefile's web subset ranges; U+A78B, U+A78C and U+A7B1 are listed there.
"""
import math
import os
import pathops
from collections import defaultdict
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

SUF = 'african'
UPS_W = 1.06          # ʊ: its ink this much of the o's ink width
TT_DEPTH = 0.12       # ƿ: where the diagonal meets the stem, of the x-height above the baseline
WY_MEET = 0.30        # Ƿ: where the diagonal meets the stem, of the cap height
KH_F = 1.25           # Ƙ: the hook's size, of ɓ's (its stroke thinned back to the arm's weight)
SALT_L = 0.70         # Ꞌ: its length, of the cap height (ꞌ is the straight quote, about 0.39 of it)
BAR_UC = 1.0          # Ɨ Ʉ: the bar beyond each stem, of Đ's bar beyond its stem on the left
BAR_LC = 0.6          # ʉ: the bar beyond each stem, of đ's bar beyond its stem
BAR_B = 0.30         # Ƀ: the bar runs into the lower counter no further than this much of its width
BAR_I = 1.0           # ɨ: the bar beyond each side of the stem, of đ's

# Ɣ ɣ Ʋ ʋ come from Noto Sans: one static file per weight, upright (the italics are slanted by
# build.py, as all the module's letters are), vendored in ../notosans (README, "Greek sources").
HERE = os.path.dirname(os.path.abspath(__file__))
NOTO = os.path.join(HERE, '..', 'notosans', 'NotoSans-AfricanSubset-{w}.ttf')
NOTO_W = ('ExtraLight', 'Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black')
# (letter, model, kind of stroke the weight is matched on, vertical knots: (Noto letter, its
# bound) -> (Torchlette glyph, its bound); the bounds: 1 bottom, 3 top)
BORROW = {
    0x0263: ('v', 'arm', (('x', 3), ('y', 1))),
    0x028B: ('u', 'stem', (('x', 3), ('o', 1))),
    0x0194: ('V', 'arm', (('H', 3), ('O', 1))),
    0x01B2: ('U', 'stem', (('H', 3), ('O', 1))),
}


def _name(cp):
    return UV2AGL.get(cp, f'uni{cp:04X}')


_NOTO = {}


def _noto_path(w, ch):
    """Noto Sans's glyph for the character ch at weight w (one of NOTO_W), as a path."""
    if w not in _NOTO:
        f = TTFont(NOTO.format(w=w))
        _NOTO[w] = (f.getGlyphSet(), f.getBestCmap())
    gs, cm = _NOTO[w]
    p = pathops.Path(); gs[cm[ord(ch)]].draw(p.getPen(glyphSet=gs))
    return p


def _drop_slivers(g):
    """Drop the contours a union leaves with no area (a two-point spur where outlines met)."""
    from array import array
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    if g.isComposite() or g.numberOfContours <= 0: return
    pts, fl, keep, s0 = list(g.coordinates), list(g.flags), [], 0
    for e in g.endPtsOfContours:
        c = pts[s0:e + 1]
        a = sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(len(c))) / 2
        if len(c) >= 3 and abs(a) > 4: keep.append((s0, e))
        s0 = e + 1
    if len(keep) == len(g.endPtsOfContours): return
    co, fo, ends = [], [], []
    for a, e in keep:
        co += pts[a:e + 1]; fo += fl[a:e + 1]; ends.append(len(co) - 1)
    g.coordinates = GlyphCoordinates(co); g.flags = array('B', fo); g.endPtsOfContours = ends
    g.numberOfContours = len(ends)


def glyphs(ctx):
    c = ctx
    P, W, mv, union, clip, rect = c.path_of, c.W, c.mv, c.union, c.clip, c.rect
    hs, vs, tf = c.hspans, c.vspans, c.transformed
    order = set(c.font.getGlyphOrder())
    cmap = c.font.getBestCmap()
    c.af_made, c.af_smcp, c.af_c2sc = [], [], []
    BIG = 4000

    def put(name, path, adv, cp=None):
        assert name not in order, name
        if cp is not None: assert cp not in cmap, f'U+{cp:04X} already mapped to {cmap.get(cp)}'
        c.add(name, path, round(adv))
        _drop_slivers(c.glyf[name])
        c.GDEF_CLASS[name] = 1
        if cp is not None: c.map(cp, name)
        c.af_made.append(name)
        return name

    def bounds(p): return p.bounds

    def sb(name):
        b = P(name).bounds
        return b[0], W(name) - b[2]

    def fit(p, lsb, rsb):
        """p moved by whole units so its ink starts at lsb; the advance leaves rsb after it."""
        b = p.bounds
        dx = round(lsb - b[0])
        return mv(p, dx), round(b[2] + dx + rsb)

    def rot(p, x2, y2):
        """p turned 180 degrees about (x2/2, y2/2)."""
        return tf(p, (-1, 0, 0, -1, x2, y2))

    def mir(p, x2):
        """p mirrored about x = x2/2."""
        return tf(p, (-1, 0, 0, 1, x2, 0))

    def scale(p, sx, sy, cx=0, cy=0):
        return tf(p, (sx, 0, 0, sy, cx - sx * cx, cy - sy * cy))

    def stem(name, y=None):
        """The left stem: the first ink span at height y, or, with no y, the narrowest first
        span of the rows (from 0.15 to 0.85 of the height) that have more than one."""
        q = P(name)
        if y is not None: return hs(q, y)[0]
        b = q.bounds; best = None
        for i in range(15, 86, 2):
            sp = hs(q, b[1] + (b[3] - b[1]) * i / 100)
            if len(sp) >= 2 and (best is None or sp[0][1] - sp[0][0] < best[1] - best[0] - 0.5): best = sp[0]
        if best is None:                                       # one span in every row (t): the narrowest
            for i in range(15, 86, 2):
                sp = hs(q, b[1] + (b[3] - b[1]) * i / 100)
                if sp and (best is None or sp[0][1] - sp[0][0] < best[1] - best[0] - 0.5): best = sp[0]
        return best

    def sc_from(src, path):
        """A small cap drawn from the heavier instance's src outline (path), tracked like the letters."""
        return path, c.sc_font['hmtx'][src][0] * c.SC_SCALE + 2 * c.SC_TRACK

    def put_sc(name, path, adv):
        put(name, path, adv)
        c.sc_respace(name)
        return name

    def pair(cap_cp, low_cp, sc_name):
        cap, low = _name(cap_cp), _name(low_cp)
        if sc_name:
            c.af_c2sc.append((cap, sc_name))
            c.af_smcp.append((low, sc_name))

    xh = P('x').bounds[3]
    o_top = P('o').bounds[3]

    # ---- Ɔ ɔ: C and c turned ------------------------------------------------------------
    def turned(src):
        b = P(src).bounds
        p = rot(P(src), W(src), round(b[1] + b[3]))
        return p, W(src)
    put(_name(0x0186), *turned('C'), cp=0x0186)
    put(_name(0x0254), *turned('c'), cp=0x0254)
    put(f'{_name(0x0186)}.sc.{SUF}', *turned('C.sc'))
    pair(0x0186, 0x0254, f'{_name(0x0186)}.sc.{SUF}')

    # ---- Ǝ ǝ: E mirrored; ǝ is the schwa ---------------------------------------------------
    put(_name(0x018E), mir(P('E'), W('E')), W('E'), cp=0x018E)
    put(_name(0x01DD), P('uni0259'), W('uni0259'), cp=0x01DD)
    put(f'{_name(0x018E)}.sc.{SUF}', mir(P('E.sc'), W('E.sc')), W('E.sc'))
    pair(0x018E, 0x01DD, f'{_name(0x018E)}.sc.{SUF}')

    # ---- Ɛ ɛ: Mulish's Cyrillic З з mirrored -----------------------------------------------
    put(_name(0x0190), mir(P('uni0417'), W('uni0417')), W('uni0417'), cp=0x0190)
    put(_name(0x025B), mir(P('uni0437'), W('uni0437')), W('uni0437'), cp=0x025B)
    p, a = sc_from('uni0417', c.sc_path('uni0417'))
    put_sc(f'{_name(0x0190)}.sc.{SUF}', mir(p, a), a)
    pair(0x0190, 0x025B, f'{_name(0x0190)}.sc.{SUF}')

    # ---- Ʒ ʒ: Mulish's Cyrillic Ӡ ӡ ---------------------------------------------------------
    put(_name(0x01B7), P('uni04E0'), W('uni04E0'), cp=0x01B7)
    put(_name(0x0292), P('uni04E1'), W('uni04E1'), cp=0x0292)
    put_sc(f'{_name(0x01B7)}.sc.{SUF}', *sc_from('uni04E0', c.sc_path('uni04E0')))
    pair(0x01B7, 0x0292, f'{_name(0x01B7)}.sc.{SUF}')

    # ---- Ʇ ʇ: T and t turned; ʇ about the middle of the x-height --------------------------
    put(_name(0xA7B1), *turned('T'), cp=0xA7B1)
    put(f'{_name(0xA7B1)}.sc.{SUF}', *turned('T.sc'))
    tb = P('t').bounds
    xt = vs(P('t'), round(tb[2]) - 3)[-1][1]                # the top of t's crossbar at its right end
    put(_name(0x0287), rot(P('t'), W('t'), round(xt)), W('t'), cp=0x0287)
    pair(0xA7B1, 0x0287, f'{_name(0xA7B1)}.sc.{SUF}')

    # ---- Ɖ ɖ: Ɖ is Đ ------------------------------------------------------------------------
    put(_name(0x0189), P('Dcroat'), W('Dcroat'), cp=0x0189)

    # tails: ŋ's (n's right stem down into a tail turned left) and Ŋ's
    def tail(src, x0=None, x1=None):
        """The tail of src below the baseline, its stem carried a few units above it."""
        p = P(src)
        t0, t1 = hs(p, -2)[-1]
        return union(clip(p, (-BIG, -BIG, BIG, 0)), rect(t0, -4, t1, 6))
    n_r = hs(P('eng'), -2)[-1]
    eng_tail = tail('eng')
    d_s = hs(P('d'), 600)[0]
    dt = union(P('d'), mv(mir(eng_tail, round(n_r[0] + n_r[1])), round(d_s[0] - n_r[0])))
    db = dt.bounds
    adv = max(W('d'), round(db[2] + 0.5 * (W('d') - P('d').bounds[2])))
    put(_name(0x0256), dt, adv, cp=0x0256)
    pair(0x0189, 0x0256, f'{_name(0x0189)}.sc.{SUF}')

    # ---- Ɲ ɲ: N and n with Ŋ's and ŋ's tail under the left stem -----------------------------
    def left_tail(src, tsrc, y):
        """src with tsrc's tail under its left stem (the first span at y)."""
        s0, s1 = hs(P(src), y)[0]
        r0, r1 = hs(P(tsrc), -2)[-1]
        return union(P(src), mv(tail(tsrc), round(s0 - r0)))
    jl = P('j').bounds[0]
    p = left_tail('n', 'eng', 0.3 * xh)
    put(_name(0x0272), *fit(p, jl, sb('n')[1]), cp=0x0272)
    p = left_tail('N', 'Eng', 0.2 * P('N').bounds[3])
    put(_name(0x019D), *fit(p, P('J').bounds[0], sb('N')[1]), cp=0x019D)
    p = left_tail('N.sc', 'Eng.sc', 0.2 * P('N.sc').bounds[3])
    put(f'{_name(0x019D)}.sc.{SUF}', *fit(p, P('J.sc').bounds[0], sb('N.sc')[1]))
    pair(0x019D, 0x0272, f'{_name(0x019D)}.sc.{SUF}')

    # ---- hooks ------------------------------------------------------------------------------
    def asc_hook(src, bowl_top=None):
        """ɓ's hook: its outline above where its stem stops being straight (the hook may begin
        low: in Black the stem bends from just above the bowl), with 40 units of the straight
        stem below; the stem's span and the height where the hook begins. src: a glyph name
        or a path (whose bowl's top is bowl_top)."""
        p = P(src) if isinstance(src, str) else src
        y = (o_top if bowl_top is None else bowl_top) + 12
        s = hs(p, y)[0]
        while y < 900:
            q = hs(p, y + 2)
            if len(q) != 1 or abs(q[0][0] - s[0]) > 0.5 or abs(q[0][1] - s[1]) > 0.5: break
            y += 2
        piece = union(clip(p, (-BIG, y, BIG, BIG)), clip(p, (s[0] - 1, y - 40, s[1] + 1, y + 1)))
        return piece, s, y
    hk, hk_s, hk_y = asc_hook('uni0253')

    def hooked(src, piece, ps, py, dy=0):
        """src with its left stem ending in piece (ps: the piece's stem span, py: where its hook
        begins), the piece moved up by dy."""
        t = P(src)
        s0, s1 = stem(src)
        dx = round(s0 - ps[0])
        return union(clip(t, (-BIG, -BIG, BIG, py + dy - 20)), mv(piece, dx, dy))
    # ƙ ƭ: k and t with ɓ's hook on the stem
    p = hooked('k', hk, hk_s, hk_y)
    put(_name(0x0199), p, max(W('k'), round(p.bounds[2] + sb('k')[1])), cp=0x0199)
    p = hooked('t', hk, hk_s, hk_y)
    put(_name(0x01AD), p, max(W('t'), round(p.bounds[2] + sb('t')[1])), cp=0x01AD)
    # ƥ: p with ɓ's stem and hook above the x-height
    ps0, ps1 = stem('p')
    up = clip(P('uni0253'), (-BIG, o_top + 10, hk_s[1] + 1, hk_y + 1))
    p = union(P('p'), mv(union(up, clip(P('uni0253'), (-BIG, hk_y, BIG, BIG))), round(ps0 - hk_s[0])),
              rect(ps0, xh - 20, ps1, o_top + 15))
    put(_name(0x01A5), p, W('p'), cp=0x01A5)

    # Ɓ's hook (left of the stem, at the cap height)
    for src, base, sfx in (('uni0181', 'B', ''), ('uni0181.sc', 'B.sc', '.sc')):
        q = P(src)
        s0, s1 = stem(src, 0.3 * q.bounds[3])
        hb = clip(q, (-BIG, -BIG, s0 - 2, BIG)).bounds         # the hook, left of the stem
        piece = clip(q, (-BIG, hb[1] - 10, s1, BIG))            # the hook and the stem beside it
        # Ƥ: P moved over as Ɓ's B is, with Ɓ's hook
        Pn = 'P' + sfx
        d_ = round(s0 - stem(Pn, 0.3 * P(Pn).bounds[3])[0])
        pp = union(mv(P(Pn), d_), piece)
        nm = _name(0x01A4) + (f'.sc.{SUF}' if sfx else '')
        put(nm, pp, W(Pn) + d_, *(() if sfx else (0x01A4,)))
        # Ƭ: T's bar ending on the left in Ɓ's hook, the hook's outer edge where the bar ended
        Tn = 'T' + sfx
        tb_ = P(Tn).bounds
        hook_only = clip(q, (-BIG, hb[1] - 10, s0, BIG))
        xa = round(tb_[0] + (s0 - hb[0]))                        # where the hook meets the bar
        pt = union(clip(P(Tn), (xa - 4, -BIG, BIG, BIG)), mv(hook_only, round(xa - s0)))
        nm = _name(0x01AC) + (f'.sc.{SUF}' if sfx else '')
        put(nm, pt, W(Tn), *(() if sfx else (0x01AC,)))
    pair(0x01A4, 0x01A5, f'{_name(0x01A4)}.sc.{SUF}')
    pair(0x01AC, 0x01AD, f'{_name(0x01AC)}.sc.{SUF}')

    # Ɠ ɠ: ɓ's hook points right already. Find the rightmost upper shoulder;
    # a fixed-height slice can intersect only the left side of G.
    def right_hook(base, piece, hook_y, top, height, stem_model=None):
        q = P(base)
        samples = [(y, s[-1]) for y in (height * i / 100 for i in range(65, 91, 2))
                   if (s := hs(q, y))]
        join_y, (a, b) = max(samples, key=lambda item: item[1][1])
        if stem_model:
            # G's shoulder span can include most of its bowl at heavy weights.
            # Its hook takes a capital stem's width, independently of that span.
            m0, m1 = hs(P(stem_model), height * 0.5)[0]
            a = b - (m1 - m0)
        # Fit both edges at a splice inside the extracted straight stem. Matching
        # only the right edge left a width discontinuity in ɠ.
        splice = hook_y - 20
        h0, h1 = hs(piece, splice)[0]
        sx = (b - a) / (h1 - h0)
        dy = round(top - piece.bounds[3])
        hook = tf(clip(piece, (-BIG, splice, BIG, BIG)),
                  (sx, 0, 0, 1, a - sx * h0, dy))
        if stem_model:
            # A low hook splice must not project below the shoulder as a spur.
            hook = clip(hook, (-BIG, join_y, BIG, BIG))
        # Overlap the fitted splice and shoulder by two units at each end.
        x0, x1 = a, b
        assert x1 > x0, f'{base}: hook stem misses the shoulder'
        hook_bottom = max(join_y, splice + dy) if stem_model else splice + dy
        y0, y1 = sorted((join_y, hook_bottom))
        bridge = rect(x0, y0 - 2, x1, y1 + 2)
        assert abs(pathops.op(bridge, q, pathops.PathOp.INTERSECTION).area) > 0, f'{base}: bridge misses shoulder'
        assert abs(pathops.op(bridge, hook, pathops.PathOp.INTERSECTION).area) > 0, f'{base}: bridge misses hook'
        p = union(q, hook, bridge)
        return fit(p, *sb(base))

    put(_name(0x0193), *right_hook('G', hk, hk_y, P('H').bounds[3] * 1.12,
                                  P('H').bounds[3], 'H'), cp=0x0193)
    put(_name(0x0260), *right_hook('g', hk, hk_y, P('H').bounds[3], xh), cp=0x0260)
    sc_hook, _, sc_y = asc_hook(c.sc_path('uni0253'), P('O.sc').bounds[3])
    sc_h = P('H.sc').bounds[3]
    put(f'{_name(0x0193)}.sc.{SUF}',
        *right_hook('G.sc', sc_hook, sc_y, sc_h * 1.12, sc_h, 'H.sc'))
    pair(0x0193, 0x0260, f'{_name(0x0193)}.sc.{SUF}')

    # ---- Ɣ ɣ Ʋ ʋ: Noto Sans's letters, fitted -----------------------------------------------
    # Each is Noto's outline mapped onto Torchlette's: vertically by the line through two knots
    # (x-height or cap height, and the bottom of y, o or O, so the descender and overshoot are
    # Torchlette's), horizontally by the ratio of the model letters' widths (v u V U, Torchlette's
    # to Noto's at that weight). The weight is Noto's whose fitted stroke (the left arm, across
    # it, or the left stem) comes nearest the model's; the rest of the difference is taken up by
    # offsetting the outline evenly (half each side), its height then put back (so the strokes
    # across change by under 2%). Sidebearings: the model's.
    c.af_noto = {}

    def stroke_of(p, kind, H):
        """The weight of p's left stem at half of H, or of its left arm across it (between 0.55
        and 0.75 of H)."""
        if kind == 'stem':
            s = hs(p, 0.5 * H)[0]
            return s[1] - s[0]
        a, b = hs(p, 0.55 * H)[0], hs(p, 0.75 * H)[0]
        dx, dy = (b[0] + b[1] - a[0] - a[1]) / 2, 0.2 * H
        return (a[1] - a[0]) * dy / math.hypot(dx, dy)

    def offset(p, d):
        """p made d units heavier (lighter, d < 0) on every side."""
        if abs(d) < 0.25: return p
        s = pathops.Path(); p.draw(s.getPen())
        s.stroke(2 * abs(d), pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 12)   # the corners kept sharp
        return union(p, s) if d > 0 else c.diff(p, s)

    def borrow(cp, sfx=''):
        model, kind, ((n1, i1), (n0, i0)) = BORROW[cp]
        q = P(model + sfx); qb = q.bounds
        y1t, y0t = P(n1 + sfx).bounds[i1], P(n0 + sfx).bounds[i0]
        H = y1t
        want = stroke_of(q, kind, H)
        best = None
        for w in NOTO_W:
            nb = _noto_path(w, model).bounds
            y1n, y0n = _noto_path(w, n1).bounds[i1], _noto_path(w, n0).bounds[i0]
            a = (y1t - y0t) / (y1n - y0n)
            sx = (qb[2] - qb[0]) / (nb[2] - nb[0])
            p = tf(_noto_path(w, chr(cp)), (sx, 0, 0, a, 0, y1t - a * y1n))
            got = stroke_of(p, kind, H)
            if best is None or abs(got - want) < abs(best[2] - want): best = (w, p, got, sx, a)
        w, p, got, sx, a = best
        y0, y1 = p.bounds[1], p.bounds[3]
        p = offset(p, (want - got) / 2)
        z0, z1 = p.bounds[1], p.bounds[3]                     # the offset moved top and bottom: put them back
        k_ = (y1 - y0) / (z1 - z0)
        p = tf(p, (1, 0, 0, k_, 0, y0 - k_ * z0))
        name = _name(cp) + (f'.sc.{SUF}' if sfx else '')
        c.af_noto[name] = dict(weight=w, noto=round(got, 1), model=round(want, 1), fitted=round(stroke_of(p, kind, H), 1),
                               sx=round(sx, 4), sy=round(a, 4))
        c.log(f'{name}: Noto Sans {w}, stroke {got:.1f} offset to {want:.1f} ({model + sfx}); x {sx:.3f}, y {a:.3f}')
        return put(name, *fit(p, *sb(model + sfx)), *(() if sfx else (cp,)))

    borrow(0x01B2); borrow(0x01B2, '.sc'); borrow(0x028B)
    pair(0x01B2, 0x028B, f'{_name(0x01B2)}.sc.{SUF}')

    # Ƙ: K's upper arm ending in ɓ's hook, turned to the K's arm and as heavy
    def arm(p, y0, y1):
        a, b = hs(p, y0)[-1], hs(p, y1)[-1]
        ca, cb = (a[0] + a[1]) / 2, (b[0] + b[1]) / 2
        ang = math.atan2(cb - ca, y1 - y0)                    # from the vertical, positive leaning right
        perp = (a[1] - a[0]) * math.cos(ang)
        return (ca, y0), ang, perp
    for kn, sfx in (('K', ''), ('K.sc', '.sc')):
        K_ = P(kn); H_ = K_.bounds[3]
        (kc, ky), ka, kw = arm(K_, 0.70 * H_, 0.80 * H_)
        # ɓ's hook (the small cap's from the heavier instance at small-cap size, as build.py
        # draws its small capitals), its straight stem run on downwards
        bq = P('uni0253') if not sfx else c.sc_path('uni0253')
        bo = P('o').bounds[3] if not sfx else c.sc_path('o').bounds[3]
        piece, (s0, s1), hy = asc_hook(bq, bo)
        d_ = (s1 - s0) * (KH_F - 1) / KH_F / 2                # the hook KH_F times ɓ's, its stroke thinned
        c.log(f'Ƙ{sfx}: ɓ hook from {hy:.0f}, bowl top {bo:.0f}, stem {s0:.1f}-{s1:.1f}, thinned {d_:.1f}')
        # back to the arm's weight; the stem run on below by a rect just into the thinned piece's
        # straight stem (higher, its straight edge would stand off the curve where it begins)
        piece = union(offset(piece, -d_), rect(s0 + d_, hy - 400, s1 - d_, hy - 40 + d_ + 6))
        k_ = kw / (s1 - s0) * KH_F
        th = ka                                               # the stem turned to the arm's slope
        co, si = math.cos(th) * k_, math.sin(th) * k_
        sx, sy = (s0 + s1) / 2, hy
        piece = tf(piece, (co, -si, si, co, 0, 0))             # clockwise
        px, py = co * sx + si * sy, -si * sx + co * sy
        piece = mv(piece, kc - px, ky - py)
        # slide along K's arm until its top is the overshoot above the cap height
        top_want = H_ + (P('O' + sfx).bounds[3] - P('H' + sfx).bounds[3])
        t_ = (top_want - piece.bounds[3]) / math.cos(ka)
        piece = mv(piece, t_ * math.sin(ka), t_ * math.cos(ka))
        yj = ky + t_ * math.cos(ka)                           # where the hook's straight stem began
        cut = yj - 0.06 * H_ * (1 + math.cos(ka))
        piece = clip(piece, (-BIG, cut - 1, BIG, BIG))
        ks1 = stem(kn)[1]
        pk = union(clip(K_, (-BIG, -BIG, BIG, cut)), clip(K_, (-BIG, -BIG, ks1 + 2, BIG)), piece)
        nm = _name(0x0198) + (f'.sc.{SUF}' if sfx else '')
        # the hook ends a T's bar's sidebearing from the advance (K's leg reaches past its own,
        # in Black by 46 units): the right side kerns as X's, whose top reaches out too (K's
        # kerning, -31 to -37 against T, would run T's bar into the hook)
        adv = max(W(kn), round(pk.bounds[2] + sb('T' + sfx)[1]))
        put(nm, pk, adv, *(() if sfx else (0x0198,)))
    pair(0x0198, 0x0199, f'{_name(0x0198)}.sc.{SUF}')

    # ---- bars ------------------------------------------------------------------------------
    def bar_of(q, x_probe, y_stem, left=True):
        """A bar's bottom, top, and how far it runs past the stem on the left and on the right."""
        y0, y1 = [s for s in vs(q, x_probe)][0 if left else -1]
        y_stem = y1 + 40 if y_stem is None else y_stem
        s0, s1 = hs(q, y_stem)[0] if left else hs(q, y_stem)[-1]
        sp = [s for s in hs(q, (y0 + y1) / 2) if s[0] <= s0 + 1 and s[1] >= s1 - 1][0]
        return y0, y1, s0 - sp[0], sp[1] - s1
    # đ: the lowercase bar; Đ: the capital's (the small caps': Đ of the heavier instance at
    # small-cap size, as build.py draws the small caps)
    dcb = bar_of(P('dcroat'), P('dcroat').bounds[2] - 5, 300, left=False)
    hbb = bar_of(P('hbar'), P('hbar').bounds[0] + 5, 300)
    for Dp, sfx in ((P('Dcroat'), ''), (c.sc_path('Dcroat'), '.sc')):
        y0, y1, el, er = bar_of(Dp, Dp.bounds[0] + 5, None)
        y0, y1 = round(y0), round(y1)
        t_ = y1 - y0
        # Ɖ.sc: D.sc with the bar
        if sfx:
            s0, s1 = stem('D.sc', y1 + 40)
            put(f'{_name(0x0189)}.sc.{SUF}', union(P('D.sc'), rect(round(s0 - el), y0, round(s1 + er), y1)), W('D.sc'))
        # Ƀ: through the stem at the middle of the lower bowl
        Bn = 'B' + sfx
        bb = P(Bn).bounds
        s0, s1 = stem(Bn, 0.25 * bb[3])
        mid = vs(P(Bn), s1 + 20)                               # the B's three bars beside the stem
        yc = (mid[0][1] + mid[1][0]) / 2
        cw = hs(P(Bn), yc)[-1][0] - s1 if len(hs(P(Bn), yc)) > 1 else 0   # the lower counter's width there
        er_b = min(er, BAR_B * cw)
        p = union(P(Bn), rect(round(s0 - el), round(yc - t_ / 2), round(s1 + er_b), round(yc - t_ / 2) + t_))
        nm = _name(0x0243) + (f'.sc.{SUF}' if sfx else '')
        put(nm, p, W(Bn), *(() if sfx else (0x0243,)))
        # Ɨ: I with the bar at Đ's height, as far past the stem on each side as Đ's on the left
        In = 'I' + sfx
        s0, s1 = stem(In, 100)
        e = round(BAR_UC * el)
        p = union(P(In), rect(s0 - e, y0, s1 + e, y1))
        nm = _name(0x0197) + (f'.sc.{SUF}' if sfx else '')
        l_, r_ = sb(In)
        put(nm, *fit(p, max(l_ - e, 0.35 * l_), max(r_ - e, 0.35 * r_)), *(() if sfx else (0x0197,)))
        # Ʉ: U with the bar across, past both stems
        Un = 'U' + sfx
        a0, a1 = hs(P(Un), y1 + 20)[0][0], hs(P(Un), y1 + 20)[-1][1]
        p = union(P(Un), rect(round(a0 - e), y0, round(a1 + e), y1))
        l_, r_ = sb(Un)
        nm = _name(0x0244) + (f'.sc.{SUF}' if sfx else '')
        put(nm, *fit(p, max(l_ - e, 0.35 * l_), max(r_ - e, 0.35 * r_)), *(() if sfx else (0x0244,)))
    pair(0x0243, 0x0180, f'{_name(0x0243)}.sc.{SUF}')
    pair(0x0197, 0x0268, f'{_name(0x0197)}.sc.{SUF}')
    pair(0x0244, 0x0289, f'{_name(0x0244)}.sc.{SUF}')
    # ƀ: b with ħ's bar
    y0, y1, el, er = hbb
    s0, s1 = stem('b', 600)
    put(_name(0x0180), union(P('b'), rect(s0 - el, y0, s1 + er, y1)), W('b'), cp=0x0180)
    # ɨ ʉ: đ's bar weight, across the middle of the x-height
    y0, y1, el, er = dcb
    t_ = y1 - y0
    yb = round(xh / 2 - t_ / 2)
    s0, s1 = stem('i', 200)
    e = round(BAR_I * er)
    p = union(P('i'), rect(s0 - e, yb, s1 + e, yb + t_))
    l_, r_ = sb('i')
    put(_name(0x0268), *fit(p, l_ - e, r_ - e), cp=0x0268)
    # ɨ is soft-dotted: under a mark above it loses its dot (ccmp, as Mulish's i and j do)
    put(f'{_name(0x0268)}.dotless.{SUF}', clip(P(_name(0x0268)), (-BIG, -BIG, BIG, P('dotlessi').bounds[3] + 1)),
        W(_name(0x0268)))
    a0, a1 = hs(P('u'), 300)[0][0], hs(P('u'), 300)[-1][1]
    e = round(BAR_LC * er)
    p = union(P('u'), rect(a0 - e, yb, a1 + e, yb + t_))
    l_, r_ = sb('u')
    put(_name(0x0289), *fit(p, l_ - e, r_ - e), cp=0x0289)

    # Barred O: each bar joins the two sides of its own O, at the counter's
    # middle. Its weight follows the corresponding D with stroke.
    for base, cp, bar_src in (('O', 0x019F, P('Dcroat')),
                              ('O.sc', None, c.sc_path('Dcroat')),
                              ('o', 0x0275, P('dcroat'))):
        q = P(base); bb = q.bounds
        height = (bb[1] + bb[3]) / 2
        y0, y1, _, _ = bar_of(bar_src, bar_src.bounds[0] + 5, None) if base != 'o' else dcb
        thickness = y1 - y0
        spans = hs(q, height)
        p = union(q, rect(spans[0][0], height - thickness / 2,
                          spans[-1][1], height + thickness / 2))
        name = f'{_name(0x019F)}.sc.{SUF}' if base == 'O.sc' else _name(cp)
        put(name, p, W(base), *(() if cp is None else (cp,)))
    pair(0x019F, 0x0275, f'{_name(0x019F)}.sc.{SUF}')

    # Turn V through 180 degrees in its own advance, as for Ɔ.
    for base, cp in (('V', 0x0245), ('v', 0x028C), ('V.sc', None)):
        name = f'{_name(0x0245)}.sc.{SUF}' if cp is None else _name(cp)
        put(name, *turned(base), *(() if cp is None else (cp,)))
    pair(0x0245, 0x028C, f'{_name(0x0245)}.sc.{SUF}')

    # ---- Ɩ ɩ: a stem with t's foot ---------------------------------------------------------
    t = P('t')
    ts0, ts1 = hs(t, 300)[0]
    yf = 0
    while yf < 300:
        q = hs(t, yf)
        if q and abs(q[0][0] - ts0) < 0.5 and abs(q[0][1] - ts1) < 0.5: break
        yf += 2
    foot = clip(t, (-BIG, -BIG, BIG, yf + 30))
    i0, i1 = hs(P('dotlessi'), 200)[0]
    p = union(clip(mv(P('dotlessi'), round(ts0 - i0)), (-BIG, yf, BIG, BIG)), foot)
    put(_name(0x0269), *fit(p, sb('dotlessi')[0], sb('t')[1]), cp=0x0269)
    for In, sfx in (('I', ''), ('I.sc', '.sc')):
        s0, s1 = stem(In, 200)
        k_ = (s1 - s0) / (ts1 - ts0)
        f_ = mv(scale(foot, k_, k_, ts0, 0), round(s0 - ts0))
        p = union(clip(P(In), (-BIG, k_ * yf, BIG, BIG)), f_)
        nm = _name(0x0196) + (f'.sc.{SUF}' if sfx else '')
        put(nm, *fit(p, sb(In)[0], sb('t')[1]), *(() if sfx else (0x0196,)))
    pair(0x0196, 0x0269, f'{_name(0x0196)}.sc.{SUF}')

    # ---- Ɣ ɣ: Noto Sans's, fitted as Ʋ ʋ are -------------------------------------------------
    borrow(0x0263); borrow(0x0194); borrow(0x0194, '.sc')
    pair(0x0194, 0x0263, f'{_name(0x0194)}.sc.{SUF}')

    # ---- Ʊ ʊ: Ω turned upside down; ʊ from the small cap, narrowed and lowered -------------
    def flipped(p, top):
        b = p.bounds
        return tf(p, (1, 0, 0, -1, 0, round(top + b[1])))       # its feet's underside to `top`
    put(_name(0x01B1), flipped(P('uni03A9'), P('H').bounds[3]), W('uni03A9'), cp=0x01B1)
    p, a = sc_from('uni03A9', c.sc_path('uni03A9'))
    usc = flipped(p, c.SC_H)
    put_sc(f'{_name(0x01B1)}.sc.{SUF}', usc, a)
    pair(0x01B1, 0x028A, f'{_name(0x01B1)}.sc.{SUF}')
    # ʊ: the small cap scaled to the x-height and the o's width, its strokes thickened back
    q = P(f'{_name(0x01B1)}.sc.{SUF}'); qb = q.bounds
    cx = (qb[0] + qb[2]) / 2
    tv = (lambda s_: s_[1] - s_[0])(hs(q, (qb[1] + qb[3]) / 2 - 40)[0])   # its side at the middle
    th_ = (lambda s_: s_[1] - s_[0])(vs(q, cx)[0])                        # its bowl's bottom
    ob = P('o').bounds
    lv = (lambda s_: s_[1] - s_[0])(hs(P('n'), 200)[0])
    lh = (lambda s_: s_[1] - s_[0])(vs(P('o'), (ob[0] + ob[2]) / 2)[0])
    Wt, Ht = UPS_W * (ob[2] - ob[0]), xh - ob[1]
    sx = (Wt - lv) / (qb[2] - qb[0] - tv); sy = (Ht - lh) / (qb[3] - qb[1] - th_)
    dxv, dyv = lv - sx * tv, lh - sy * th_
    qs = scale(q, sx, sy, qb[0], qb[3])
    qs = union(qs, mv(qs, dxv, 0), mv(qs, 0, -dyv), mv(qs, dxv, -dyv))
    qs = mv(qs, 0, round(xh - qs.bounds[3]))
    put(_name(0x028A), *fit(qs, *sb('o')), cp=0x028A)

    # ---- Ƿ ƿ: wynn: p's stem and the top of its bowl, its right side running down into a
    # straight stroke to the stem ---------------------------------------------------------------

    def wynn(src, meet):
        q = P(src)
        s0, s1 = hs(q, 0.35 * P(src).bounds[3] if src[0] == 'P' else 200)[0]
        bb_ = q.bounds
        top = bb_[3]
        # the bowl's right side: where it is widest
        best = None
        for yy in range(int(0.3 * top), int(top), 4):
            sp = hs(q, yy)
            if len(sp) >= 2 and (best is None or sp[-1][1] > best[1][1]): best = (yy, sp[-1])
        ym, (r0, r1) = best
        w = r1 - r0
        keep = union(clip(q, (-BIG, ym, BIG, BIG)), clip(q, (-BIG, -BIG, s1, BIG)))
        xc = (r0 + r1) / 2
        E = (s0 + 0.5 * (s1 - s0), meet)
        pth = pathops.Path(); pen = pth.getPen()
        pen.moveTo((xc, ym + 2))
        pen.curveTo((xc, ym - 0.45 * (ym - meet)), (xc - 0.25 * (xc - E[0]), meet + 0.15 * (ym - meet)), E)
        pen.endPath()
        pth.stroke(w * 0.95, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        pth.simplify()
        return union(keep, pth)
    p = wynn('p', TT_DEPTH * xh)
    put(_name(0x01BF), p, W('p'), cp=0x01BF)
    p = wynn('P', WY_MEET * P('H').bounds[3])
    put(_name(0x01F7), p, W('P'), cp=0x01F7)
    p = wynn('P.sc', WY_MEET * P('H.sc').bounds[3])
    put(f'{_name(0x01F7)}.sc.{SUF}', p, W('P.sc'))
    pair(0x01F7, 0x01BF, f'{_name(0x01F7)}.sc.{SUF}')

    # ---- Ꞌ ꞌ: saltillo: the straight quote; the capital longer -----------------------------
    put(_name(0xA78C), *fit(P('quotesingle'), *sb('dotlessi')), cp=0xA78C)

    def long_quote(q, H):
        """The straight quote q lengthened from its top down to SALT_L of the cap height H."""
        qb = q.bounds
        return scale(q, 1, SALT_L * H / (qb[3] - qb[1]), 0, qb[3])
    put(_name(0xA78B), *fit(long_quote(P('quotesingle'), P('H').bounds[3]), *sb('dotlessi')), cp=0xA78B)
    put(f'{_name(0xA78B)}.sc.{SUF}', *fit(long_quote(P('quotesingle.sc'), P('H.sc').bounds[3]), *sb('I.sc')))
    pair(0xA78B, 0xA78C, f'{_name(0xA78B)}.sc.{SUF}')

    # Uncased clicks: the same construction at letter and small-cap height. The double
    # stem's gap grows with the stem, so it remains open in the heaviest weight.
    def clicks(stem_name, height, dot_name, sides):
        s0, s1 = hs(P(stem_name), height * 0.5)[0]
        t = s1 - s0
        left, right = sides
        bar = rect(0, 0, t, height)
        gap = max(45, 0.65 * t)
        double = union(bar, mv(bar, t + gap, 0))
        # Two short bars cross the stem, higher and closer than an equals sign.
        arm = max(60, 0.8 * t)
        thick = max(20, 0.70 * t)
        y1, y2 = height * 0.34, height * 0.63
        cross = union(bar, rect(-arm, y1 - thick / 2, t + arm, y1 + thick / 2),
                      rect(-arm, y2 - thick / 2, t + arm, y2 + thick / 2))
        dot = P(dot_name); db = dot.bounds
        dp = mv(dot, (t - (db[2] - db[0])) / 2 - db[0], -db[1])
        dot_top = db[3] - db[1]
        bang = union(rect(0, dot_top + max(55, 0.45 * t), t, height), dp)
        return [fit(p, left, right) for p in (bar, double, cross, bang)]

    full = clicks('l', P('H').bounds[3], 'period', sb('l'))
    small = clicks('I.sc', P('H.sc').bounds[3], 'period', sb('I.sc'))
    for cp, normal, sc in zip(range(0x01C0, 0x01C4), full, small):
        name = _name(cp)
        sc_name = f'{name}.sc.{SUF}'
        put(name, *normal, cp=cp)
        put(sc_name, *sc)
        c.af_smcp.append((name, sc_name))
        c.af_c2sc.append((name, sc_name))

    c.log(f'{len(c.af_made)} glyphs')


def features(ctx):
    J = ' '.join
    sm, cs = ctx.af_smcp, ctx.af_c2sc
    ctx.gsub(f'lookup AFRICAN_SMCP {{ sub [{J(a for a, _ in sm)}] by [{J(b for _, b in sm)}]; }} AFRICAN_SMCP;\n'
             f'lookup AFRICAN_C2SC {{ sub [{J(a for a, _ in cs)}] by [{J(b for _, b in cs)}]; }} AFRICAN_C2SC;\n'
             f'feature smcp {{ lookup AFRICAN_SMCP; }} smcp;\n'
             f'feature c2sc {{ lookup AFRICAN_C2SC; }} c2sc;\n', before='main')
    # the capitals take the .case marks, as Mulish's ccmp gives them after its Latin capitals
    caps = [g for cp, g in sorted(ctx.font.getBestCmap().items()) if cp in KERN and g in ctx.af_made
            and chr(cp).isupper() and cp not in (0xA78B,)]
    case = _case_marks(ctx.font)
    if caps and case:
        ctx.gsub(f"lookup AFRICAN_CASEMARK {{ sub [{J(caps)}] [{J(a for a, _ in case)}]' by [{J(b for _, b in case)}]; }} AFRICAN_CASEMARK;\n"
                 'feature ccmp { lookup AFRICAN_CASEMARK; } ccmp;\n', before='main')
    # ɨ drops its dot before a mark above (or a mark below, then one above): Mulish's own rule
    # for i and j, with its own classes of marks
    i, d = _name(0x0268), f'{_name(0x0268)}.dotless.{SUF}'
    rules = _soft_dot_contexts(ctx.font)
    if rules and d in set(ctx.font.getGlyphOrder()):
        ctx.gsub(f'lookup AFRICAN_SOFTDOT_SUB {{ sub {i} by {d}; }} AFRICAN_SOFTDOT_SUB;\n'
                 'lookup AFRICAN_SOFTDOT {\n'
                 + ''.join(f"  sub {i}' lookup AFRICAN_SOFTDOT_SUB {' '.join('[' + J(c) + ']' for c in la)};\n" for la in rules)
                 + '} AFRICAN_SOFTDOT;\n'
                 'feature ccmp { lookup AFRICAN_SOFTDOT; } ccmp;\n', before='main')


def _case_marks(font):
    """Mulish's ccmp mapping of the marks to their .case forms after a capital (the single
    substitution its rule with A in the backtrack calls), as (mark, mark.case) pairs."""
    lks = font['GSUB'].table.LookupList.Lookup
    for lk in lks:
        for st in lk.SubTable:
            st = getattr(st, 'ExtSubTable', st)
            if type(st).__name__ == 'ChainContextSubst' and st.Format == 3 and len(st.BacktrackCoverage) == 1 \
                    and 'A' in st.BacktrackCoverage[0].glyphs and len(st.InputCoverage) == 1 \
                    and 'acutecomb' in st.InputCoverage[0].glyphs and len(st.SubstLookupRecord) == 1:
                sub = lks[st.SubstLookupRecord[0].LookupListIndex]
                m = {}
                for s2 in sub.SubTable:
                    m.update(getattr(s2, 'ExtSubTable', s2).mapping)
                return sorted((a, b) for a, b in m.items() if b == a + '.case')
    return []


def _soft_dot_contexts(font):
    """The look-ahead classes of Mulish's ccmp rules that take i and j to their dotless forms
    (a mark above; a mark below, then one above), in Mulish's order."""
    out = []
    for lk in font['GSUB'].table.LookupList.Lookup:
        for st in lk.SubTable:
            st = getattr(st, 'ExtSubTable', st)
            if type(st).__name__ == 'ChainContextSubst' and st.Format == 3 and not st.BacktrackCoverage \
                    and len(st.InputCoverage) == 1 and st.InputCoverage[0].glyphs == ['i', 'j'] and st.LookAheadCoverage:
                out.append([c.glyphs for c in st.LookAheadCoverage])
    return out


# ---- kerning ---------------------------------------------------------------------------------
# Each letter takes, on each side, the kerning of the letter whose side it has there (None: no
# pairs on that side): (left side, right side), the left side's model where the letter comes
# second in a pair, the right side's where it comes first. The first model in a list that has
# kerning on that side is used. Small capitals take the small capitals of the capitals' models.
KERN = {
    0x0186: (['O'], ['O']),                 # Ɔ: round on the right as O; the open side as O's round
    0x0254: (['o'], ['o']),
    0x018E: (['Z'], ['H']),                 # Ǝ: the arms on the left (as Z's), the stem on the right
    0x01DD: (['uni0259', 'o'], ['uni0259', 'o']),
    0x0190: (['C'], ['C']),                 # Ɛ: C's round left and open right
    0x025B: (['c'], ['c']),
    0x0194: (['V'], ['V']), 0x0263: (['v'], ['v']),
    0x0196: (['I'], ['I']), 0x0269: (['i'], ['l']),
    0x01B1: (['U'], ['U']), 0x028A: (['u'], ['u']),
    0x01B2: (['U'], ['U']), 0x028B: (['u'], ['o']),
    0x01B7: (['uni04E0', 'Z'], ['uni04E0', 'Z']), 0x0292: (['uni04E1', 'z'], ['uni04E1', 'z']),
    0x0198: (['K'], ['X']), 0x0199: (['k'], ['k']),     # Ƙ: the hook out on the right, as X's arm
    0x01A4: (['uni0181', None], ['P']), 0x01A5: (['p'], ['p']),
    0x01AC: (['uni018A', None], ['T']), 0x01AD: (['t'], ['t']),
    0x019D: (['N'], ['N']), 0x0272: (['n'], ['n']),
    0x0243: (['Dcroat'], ['B']), 0x0180: (['hbar'], ['b']),
    0x0197: (['Dcroat'], ['Hbar']), 0x0268: (['hbar'], ['dcroat']),
    0x0244: (['U'], ['U']), 0x0289: (['u'], ['u']),
    0x019F: (['O'], ['O']), 0x0275: (['o'], ['o']),
    0x0245: (['A'], ['A']), 0x028C: ([None], [None]),
    0x0193: (['G'], [None]), 0x0260: (['g'], [None]),
    0x0189: (['Dcroat'], ['Dcroat']), 0x0256: (['d'], ['d']),
    0x01F7: (['P'], ['P']), 0x01BF: (['p'], ['p']),
    0xA78B: ([None], [None]), 0xA78C: ([None], [None]),
    0xA7B1: ([None], [None]), 0x0287: ([None], [None]),
}


def _effective_kerning(gpos):
    """Pair kerning as it applies: within a lookup the first subtable that covers the left glyph
    (format 1: and has the pair) decides; the kern feature's lookups add up."""
    idxs = sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern'
                   for i in fr.Feature.LookupListIndex})
    tot = defaultdict(int)
    for i in idxs:
        lk = gpos.LookupList.Lookup[i]
        if lk.LookupType not in (2, 9): continue
        sts = [st.ExtSubTable if lk.LookupType == 9 else st for st in lk.SubTable]
        sts = [st for st in sts if getattr(st, 'LookupType', 2) == 2 and st.Format in (1, 2)]
        covs = [set(st.Coverage.glyphs) for st in sts]
        for a in set().union(*covs) if covs else ():
            seen = set()
            for st, cs in zip(sts, covs):
                if a not in cs: continue
                if st.Format == 1:
                    for r in st.PairSet[st.Coverage.glyphs.index(a)].PairValueRecord:
                        if r.SecondGlyph not in seen:
                            seen.add(r.SecondGlyph)
                            v = (getattr(r.Value1, 'XAdvance', 0) or 0) if r.Value1 else 0
                            if v: tot[(a, r.SecondGlyph)] += v
                else:
                    rec = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)]
                    for b, k in st.ClassDef2.classDefs.items():
                        if k and b not in seen:
                            seen.add(b)
                            v = (getattr(rec.Class2Record[k].Value1, 'XAdvance', 0) or 0) if rec.Class2Record[k].Value1 else 0
                            if v: tot[(a, b)] += v
                    break
    return {k: v for k, v in tot.items() if v}


def post(ctx):
    """The letters' kerning, copied side by side from their models' (KERN): each letter goes into
    its models' classes and pair sets in the kern lookups (_into_classes), and AFRICAN_KERN, after
    every other kern lookup, sets right any pair that then differs from the copy. A pair already
    kerned is left alone."""
    gpos = ctx.font['GPOS'].table
    eff = _effective_kerning(gpos)
    firsts, seconds = defaultdict(list), defaultdict(list)
    for (a, b), v in eff.items():
        firsts[a].append((b, v)); seconds[b].append((a, v))
    have = set(ctx.font.getGlyphOrder())
    cmap = ctx.font.getBestCmap()
    side = {}                                       # glyph -> (model of its left side, of its right side)

    def pick(cands, table):
        for m in cands:
            if m is None: return None
            if m in have and table.get(m): return m
        return None
    for cp, (lc, rc) in KERN.items():
        g = cmap.get(cp)
        if not g: continue
        side[g] = (pick(lc, seconds), pick(rc, firsts))
        sc = dict(ctx.af_smcp + ctx.af_c2sc).get(g)
        if sc and sc not in side and cp in (c_ for c_ in KERN if chr(c_).isupper()):
            lsc = [m + '.sc' if m else None for m in lc]; rsc = [m + '.sc' if m else None for m in rc]
            side[sc] = (pick(lsc, seconds), pick(rsc, firsts))
    dl = f'{_name(0x0268)}.dotless.{SUF}'
    if dl in have and cmap.get(0x0268) in side: side[dl] = side[cmap[0x0268]]   # the dotless ɨ kerns as ɨ
    new = {}
    for g, (l_, r_) in side.items():
        if r_:
            for b, v in firsts[r_]:
                if b not in side: new[(g, b)] = v
        if l_:
            for a, v in seconds[l_]:
                if a not in side: new[(a, g)] = v
    for g, (_, r_) in side.items():
        for h, (l_, _) in side.items():
            if r_ and l_ and eff.get((r_, l_)): new[(g, h)] = eff[(r_, l_)]
    new = {k: v for k, v in new.items() if k not in eff}
    ctx.af_kern_pairs = new
    if not new: return
    _into_classes(ctx, gpos, side)
    # what that gives against what is meant (the pairs above, every other pair as it was): a
    # pair the classes miss or give twice (a model kerned by a lookup that kerns the letter
    # already) is set right in AFRICAN_KERN, after every other kern lookup
    got = _effective_kerning(gpos)
    want = dict(eff); want.update(new)
    fix = {k: want.get(k, 0) - got.get(k, 0) for k in set(got) | set(want) if want.get(k, 0) != got.get(k, 0)}
    if fix:
        fea = ['languagesystem DFLT dflt; languagesystem latn dflt;', 'lookup AFRICAN_KERN {', '  lookupflag IgnoreMarks;']
        fea += [f'  pos {a} {b} {v};' for (a, b), v in sorted(fix.items())]
        fea += ['} AFRICAN_KERN;', 'feature kern { lookup AFRICAN_KERN; } kern;']
        tmp = TTFont(); tmp.setGlyphOrder(ctx.font.getGlyphOrder())
        addOpenTypeFeaturesFromString(tmp, '\n'.join(fea) + '\n', tables=['GPOS'])
        ctx._merge_table(gpos, tmp['GPOS'].table)
    ctx.log(f'kern: {len(new)} pairs copied from the models, through their classes; {len(fix)} set right in AFRICAN_KERN')


def _into_classes(ctx, gpos, side):
    """Each letter put into its models' places in every kern subtable: as the first glyph where
    its right side's model is (the same class, or a copy of its pair set), as the second where
    its left side's model is (the same class, or a copy of each record), so it kerns as they do
    for a few bytes, not as thousands of pairs. A subtable that has the letter already is left
    alone."""
    from copy import deepcopy
    gid = ctx.font.getReverseGlyphMap()
    firsts = {g: r for g, (_, r) in side.items() if r}
    seconds = defaultdict(list)                     # model -> the letters whose left side it is
    for g, (l_, _) in side.items():
        if l_: seconds[l_].append(g)
    idxs = sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex})
    for i in idxs:
        lk = gpos.LookupList.Lookup[i]
        if lk.LookupType not in (2, 9): continue
        for st in lk.SubTable:
            st = st.ExtSubTable if lk.LookupType == 9 else st
            if getattr(st, 'LookupType', 2) != 2 or st.Format not in (1, 2): continue
            cov = list(st.Coverage.glyphs); covset = set(cov)
            add = sorted((g for g, m in firsts.items() if m in covset and g not in covset), key=gid.get)
            if st.Format == 1:
                # as the second glyph: a copy of each record that has the model second
                for ps in st.PairSet:
                    there = {r.SecondGlyph for r in ps.PairValueRecord}
                    extra = []
                    for r in ps.PairValueRecord:
                        for g in seconds.get(r.SecondGlyph, ()):
                            if g not in there:
                                r2 = deepcopy(r); r2.SecondGlyph = g; extra.append(r2)
                    if extra:
                        ps.PairValueRecord = sorted(ps.PairValueRecord + extra, key=lambda r: gid[r.SecondGlyph])
                        ps.PairValueCount = len(ps.PairValueRecord)
                # as the first: a copy of the model's pair set
                sets = dict(zip(cov, st.PairSet))
                for g in add: sets[g] = deepcopy(sets[firsts[g]])
                cov = sorted(sets, key=gid.get)
                st.PairSet = [sets[g] for g in cov]; st.PairSetCount = len(cov)
            else:
                c2 = st.ClassDef2.classDefs
                for m, gs in seconds.items():
                    if c2.get(m):
                        for g in gs:
                            if g not in c2: c2[g] = c2[m]
                c1 = st.ClassDef1.classDefs
                for g in add:
                    if c1.get(firsts[g]): c1[g] = c1[firsts[g]]
                cov = sorted(covset | set(add), key=gid.get)
            st.Coverage.glyphs = cov

"""vector: ten alternates of the "vector" word mark (ss16 proposal 171), chosen at random.

ss16 draws "vector" and "vectors" with the arrow of a maths vector on the v (`v.vec`, build.py's
proposal 171). This module adds ten more forms of the whole word, in which one stroke of the
word itself grows into the arrow, and lets the `rand` feature pick one for each occurrence.
Jordan chose them from the 25 in the vector-ligature lab (5 Nov 2026), ids from the lab:

  v01  the v's right arm runs on up and to the right into an arrowhead
  v02  the v's left arm runs on up and to the left into an arrowhead
  v06  a short arrow, as in \\vec{v}, rides just above the v
  v13  the t's stem rises past the ascender into an upward arrowhead
  v15  the top of the t's stem bends forward and runs over the rest of the word into an arrowhead
  v16  the top of the t's stem bends back and runs left over c and e into an arrowhead
  v18  the t's crossbar becomes a chevron below the stem's top, so the t is an upward arrow
       (the stem runs on above the head, which sits lower than the crossbar did)
  v20  the c's lower terminal runs on into an arrowhead, leaving along the c's own curve and
       pointing the way the curve is heading where they meet
  v23  the r's arm straightens into an arrow rising gently forward, up and to the right
  v25  the v's right arm rises and hooks forward, running over e and c into an arrowhead

Glyphs, per style, drawn from this style's own v, t, c, r and their measured strokes (so the
joins stay flush and the strokes keep the weight of the strokes they continue): the whole words
`v_e_c_t_o_r.vNN` and `v_e_c_t_o_r_s.vNN` (letters at the places Mulish's kerning puts them, as
the default `v.vec e c t o r` sits), and `v.vec.vNN`, a composite of `v.vec` that marks the
choice between the two lookups below. The italic is drawn unslanted, as every other step is,
and leans with the letters when build.py reslants it.

Layout: two lookups, placed right after ss16's front block (so they see `v.vec` and the plain
letters that follow it, and nothing that runs later can split the word):

  VECTOR_RAND  sub v.vec from [v.vec v.vec.v01 ... v.vec.v25];   (alternate, in rand)
  VECTOR_WORD  sub v.vec.vNN e c t o r [s] by v_e_c_t_o_r[_s].vNN;  (ligature, in rand)

Both are in `rand` only, so ss16 itself, its guards (no mark in Vector, eigenvector, vectorize
...) and everything verify_ss16.py checks are unchanged: `rand` acts only on a `v.vec` that ss16
has already made. The default form is the first alternate. HarfBuzz (Chrome, Firefox, Android)
applies `rand` by default and picks an alternate at random for each occurrence (a fixed seed per
shaped run, so a page renders the same every time); `font-feature-settings: "rand" N` selects
alternate N (1 the default, 2-11 v01 ... v25 in the order above) and `"rand" 0` turns it off.
Core Text (Safari) ignores `rand`, so Safari always shows the default.

No existing glyph, advance, cmap entry or lookup changes. The kern module kerns the words like
a v on the left and their last letter on the right (its INHERIT_BY_PATTERN).
"""
import math

import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

IDS = ('v01', 'v02', 'v06', 'v13', 'v15', 'v16', 'v18', 'v20', 'v23', 'v25')
ANG = math.radians(37)          # the font's own arrows (U+2192) open at about 37 degrees
DEFAULT = 'v.vec'


def word_glyph(id_, plural): return f"v_e_c_t_o_r{'_s' if plural else ''}.{id_}"
def marker_glyph(id_): return f'{DEFAULT}.{id_}'


# --- path helpers -------------------------------------------------------------------------
def poly(pts):
    p = pathops.Path(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath(); return p
def rect(x0, y0, x1, y1): return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
def union(*ps):
    ps = [q for q in ps if q is not None]; out = ps[0]
    for q in ps[1:]: out = pathops.op(out, q, pathops.PathOp.UNION)
    return out
def diff(a, b): return pathops.op(a, b, pathops.PathOp.DIFFERENCE)
def inter(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)
def clip(p, box): return inter(p, rect(*box))
def mv(p, dx, dy=0):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (1, 0, 0, 1, dx, dy))); return q
def unit(v): n = math.hypot(*v); return (v[0] / n, v[1] / n)
def add(a, b, s=1): return (a[0] + s * b[0], a[1] + s * b[1])
def rot(v, a): c, s = math.cos(a), math.sin(a); return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)
def nrm(d): return (-d[1], d[0])
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def halfplane(pt, d, R=6000):
    """Everything on the -d side of the line through pt perpendicular to d."""
    n = nrm(d); b = add(pt, d, -R)
    return poly([add(pt, n, R), add(pt, n, -R), add(b, n, -R), add(b, n, R)])
def points(p):
    rp = RecordingPen(); p.draw(rp)
    return [q for _, args in rp.value for q in args if q is not None]
def stroke(pts, w, limit=10):
    p = pathops.Path(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.endPath(); p.stroke(w, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, limit); p.simplify()
    return p
def band(q0, q1, w):
    n = nrm(unit((q1[0] - q0[0], q1[1] - q0[1]))); h = w / 2
    return poly([add(q0, n, h), add(q1, n, h), add(q1, n, -h), add(q0, n, -h)])


def head(tip, d, w, L, a=ANG, flat=0.45):
    """Chevron arrowhead, its centre lines meeting at `tip`, pointing along d: stroke w, arm
    length L (centre line), the point blunted to a flat about flat*w wide, as the font's own
    arrows are."""
    d = unit(d)
    b1, b2 = rot((-d[0], -d[1]), -a), rot((-d[0], -d[1]), a)
    p = stroke([add(tip, b1, L), tip, add(tip, b2, L)], w, 20); s = flat * w / (2 * math.tan(a))
    apex = max(dot(q, d) for q in points(p))
    return inter(p, halfplane(add((0, 0), d, apex - s), d))


def tip_for(d, w, a=ANG, flat=0.45):
    """How far past the centre-line tip the blunted point of a head of stroke w reaches."""
    return (w / 2) / math.sin(a) - flat * w / (2 * math.tan(a))


def notch(w, a=ANG):
    """How far behind its centre-line tip a head of stroke w has its inner corner: a shaft
    that ends there, however wide (up to the head's spread), hides its square end in the barbs."""
    return (w / 2) / math.sin(a)


def hfit(half, w, Lmax):
    """Longest arm (<= Lmax) whose level head stays within `half` of its axis."""
    return max(60, min(Lmax, (half - (w / 2) / math.cos(ANG)) / math.sin(ANG)))


def arrow(a, tip, w, L):
    """Straight shaft from a to the tip, plus its head."""
    return union(band(a, tip, w), head(tip, unit((tip[0] - a[0], tip[1] - a[1])), w, L))


def curve_band(fn, w_of, t0=0.0, t1=1.0, seg=60):
    """A variable-width stroke along a parametric centre line fn(t) -> (point, tangent). Each
    edge is a chain of cubics through samples of the exact offset curve, with the offset's own
    tangents as handles (cubic Hermite), so the edges are smooth curves."""
    def edge(t, s):
        pt, tg = fn(t); n = nrm(unit(tg)); h = s * w_of(t) / 2
        return (pt[0] + n[0] * h, pt[1] + n[1] * h)
    def deriv(t, s, e=1e-4):
        a, b = max(t0, t - e), min(t1, t + e)
        p, q = edge(a, s), edge(b, s)
        return ((q[0] - p[0]) / (b - a), (q[1] - p[1]) / (b - a))
    def knots(s):
        """Each edge its own pieces: one per `seg` units of its length and per 45 degrees
        it turns, so a tight inner edge is not cut into slivers that round to kinks."""
        pts = [edge(t0 + (t1 - t0) * i / 64, s) for i in range(65)]
        ln = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        ang = [math.atan2(*reversed(unit(deriv(t0 + (t1 - t0) * i / 64, s)))) for i in range(65)]
        turn = sum(abs((b - a + math.pi) % (2 * math.pi) - math.pi) for a, b in zip(ang, ang[1:]))
        n = max(1, math.ceil(ln / seg), math.ceil(turn / math.radians(45)))
        return [t0 + (t1 - t0) * i / n for i in range(n + 1)]
    p = pathops.Path(); pen = p.getPen()
    ts = knots(1)
    pen.moveTo(edge(ts[0], 1))
    for a, b in zip(ts, ts[1:]):
        h = (b - a) / 3; da, db = deriv(a, 1), deriv(b, 1)
        pa, pb = edge(a, 1), edge(b, 1)
        pen.curveTo(add(pa, da, h), add(pb, db, -h), pb)
    ts = knots(-1)
    pen.lineTo(edge(ts[-1], -1))
    for a, b in zip(ts[::-1], ts[-2::-1]):          # back along the other edge
        h = (a - b) / 3; da, db = deriv(a, -1), deriv(b, -1)
        pa, pb = edge(a, -1), edge(b, -1)
        pen.curveTo(add(pa, da, -h), add(pb, db, h), pb)
    pen.closePath()
    q = pathops.Path(); p.draw(q.getPen()); q.simplify(fix_winding=True)
    return q


def dilate(p, g):
    q = pathops.Path(); p.draw(q.getPen())
    q.stroke(2 * g, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4); q.convertConicsToQuads()
    return union(q, p)


def dist(a, b, cap=400.0):
    """The nearest distance between the ink of a and b (to a unit), up to cap."""
    def apart(g): return inter(dilate(a, g), b).area == 0
    if not apart(0.5): return 0.0
    if apart(cap): return cap
    lo, hi = 0.5, cap
    while hi - lo > 1:
        m = (lo + hi) / 2
        lo, hi = (m, hi) if apart(m) else (lo, m)
    return lo


def cubic(p0, p1, p2, p3):
    def f(t):
        u = 1 - t
        pt = (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
              u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])
        tg = (3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0]),
              3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1]))
        return pt, tg
    return f


def line_at_y(p, q, y):
    t = (y - p[1]) / (q[1] - p[1]); return (p[0] + t * (q[0] - p[0]), y)


# --- this style's letters ------------------------------------------------------------------
class Style:
    """The v, t, r and c of this style, measured on their on-curve points (Mulish's own
    structure, the same at every weight and in the italic: v 7, t 16, r 12, c 10 of them)."""
    def __init__(self, ctx):
        self.ctx = ctx
        cm = ctx.font.getBestCmap()
        self.g = {ch: cm[ord(ch)] for ch in 'vector' + 's'}
        def outline(n):
            """n's points as the finished font will have them: a glyph drawn as overlapping
            contours (the v, the r) is merged here the way build.py merges it after the modules
            run (add(): simplify, cubic to quadratic, tidy), so the indices are the final ones."""
            g = ctx.glyf[n]
            p = ctx.path_of(n); q = pathops.Path(); p.draw(q.getPen()); q.simplify(fix_winding=True)
            if abs(abs(p.area) - abs(q.area)) > 1 or len(list(q.contours)) < len(list(p.contours)):
                r = ctx.path_of(n); r.simplify()
                tt = TTGlyphPen(None); r.draw(Cu2QuPen(tt, 1.0, reverse_direction=True))
                g = ctx.tidy(tt.glyph(dropImpliedOnCurves=True))
            c, _, fl = g.getCoordinates(ctx.glyf)
            return [(tuple(q), bool(f & 1)) for q, f in zip(c, fl)]
        def on(n): return [q for q, o in outline(n) if o]
        full = outline
        want = {'v': 7, 't': 16, 'r': 12, 'c': 10}
        for ch, k in want.items():
            if len(on(self.g[ch])) != k:
                raise SystemExit(f'vector: {self.g[ch]} has {len(on(self.g[ch]))} on-curve points, not {k}; '
                                 'the measurements below read them by index')
        self.V = dict(zip('ABCDEFG', on(self.g['v'])))
        t = on(self.g['t'])
        self.xb = (t[3][1], t[4][1]); self.t_bar = (t[3][0], t[9][0])
        self.t_top = max(t[6][1], t[7][1])
        # the stems are measured on the outlines as drawn now, so a stroke grown out of one
        # meets its edges exactly (no step of a unit or two where they join)
        self.t_stem = ctx.hspans(self.path('t'), (self.xb[1] + self.t_top) / 2)[0]
        self.r_stem = ctx.hspans(self.path('r'), 150)[0]
        self.XBW = self.xb[1] - self.xb[0]
        self.STEM = self.t_stem[1] - self.t_stem[0]
        self.R = on(self.g['r']); self.c = on(self.g['c']); self.c_full = full(self.g['c'])
        V = self.V; E, F, G = V['E'], V['F'], V['G']
        th = math.atan2(F[0] - G[0], F[1] - G[1])
        self.ARM = (F[0] - E[0]) * math.cos(th)                 # the v's arm, square to it
        self.HL = 80 + 1.6 * self.XBW                          # head arm length
        # a head that takes the weight of a heavy stroke (a v arm, the r's arm, the c's
        # terminal) is drawn lighter past Regular's crossbar weight (52 units), growing as
        # its 0.65th power, so that in the heavy weights its barbs stay open and clear of the
        # letters around it; at Regular and lighter it is the stroke's own weight
        self.HK = min(1, (52 / self.XBW) ** 0.35)
        self.layout = {}
        for plural in (False, True):
            seq = [self.g[ch] for ch in ('vectors' if plural else 'vector')]
            items, adv = ctx.setting(seq)
            self.layout[plural] = (items, adv)
    def path(self, ch, dx=0, dy=0): return self.ctx.path_of(self.g[ch], dx, dy)


class Word:
    """The letters of vector(s) where the default sets them; letters can be replaced, the
    space after any letter opened, and strokes added."""
    def __init__(self, S, plural):
        self.S = S; self.plural = plural
        items, adv = S.layout[plural]
        self.chars = list('vectors' if plural else 'vector')
        self.x0 = [x for _, x in items]; self.adv0 = adv
        self.extra = [0] * len(items)        # space opened after letter i
        self.repl = {}; self.adds = []
    def x(self, i): return self.x0[i] + sum(self.extra[:i])
    def idx(self, ch): return self.chars.index(ch)
    def letter(self, i): return self.repl.get(i) or self.S.path(self.chars[i])
    def adv(self): return self.adv0 + sum(self.extra)
    def clear(self, i, extra_ink=(), share=1.0):
        """Open the space after letter i (drawn with extra_ink, in the word's coordinates)
        until its ink is as far from the letters after it as the plain letters i and i + 1
        are from each other (times share)."""
        after = union(*[mv(self.letter(k), self.x(k)) for k in range(i + 1, len(self.chars))])
        left = union(mv(self.letter(i), self.x(i)), *extra_ink)
        plain = share * dist(mv(self.S.path(self.chars[i]), self.x0[i]), mv(self.S.path(self.chars[i + 1]), self.x0[i + 1]))
        lo, hi = 0.0, 600.0
        if dist(left, after, plain + 1) >= plain: return 0
        for _ in range(14):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if dist(left, mv(after, m), plain + 1) < plain else (lo, m)
        self.extra[i] += math.ceil(hi)
        return math.ceil(hi)
    def build(self, rsb=40):
        p = union(*[mv(self.letter(i), self.x(i)) for i in range(len(self.chars))], *self.adds)
        adv = self.adv(); lsb = self.S.V['B'][0]
        sh = max(0, lsb - p.bounds[0]) if p.bounds[0] < lsb - 1 else 0     # ink before the v: keep the v's bearing
        p = mv(p, sh); adv += sh
        plain = union(*[self.S.path(ch, self.x(i)) for i, ch in enumerate(self.chars)])
        if p.bounds[2] > plain.bounds[2] + sh + 1: adv = max(adv, p.bounds[2] + rsb)
        return p, adv


# --- the strokes that grow ------------------------------------------------------------------
def v_arm(S, side, y_end):
    """The v's left or right arm, continued along its own edges up to y_end: the extension,
    the centre of its end, the arm's direction (upward) and its width."""
    V = S.V
    if side == 'R': inn, out = (V['D'], V['E']), (V['G'], V['F'])
    else: inn, out = (V['D'], V['C']), (V['A'], V['B'])
    y0 = 300
    d = unit(add(unit((inn[1][0] - inn[0][0], inn[1][1] - inn[0][1])), unit((out[1][0] - out[0][0], out[1][1] - out[0][1]))))
    a0, b0 = line_at_y(*inn, y0), line_at_y(*out, y0)
    end = ((line_at_y(*inn, y_end)[0] + line_at_y(*out, y_end)[0]) / 2, y_end)
    def cut(p, q):      # where edge p-q crosses the line through `end` square to d
        e = (q[0] - p[0], q[1] - p[1]); t = dot((end[0] - p[0], end[1] - p[1]), d) / dot(e, d)
        return (p[0] + t * e[0], p[1] + t * e[1])
    a1, b1 = cut(*inn), cut(*out)
    ext = poly([a0, b0, b1, a1] if side == 'R' else [b0, a0, a1, b1])
    return ext, end, d, S.ARM


def arm_arrow(S, side, ytop):
    """The v's arm grown into an arrow whose head peaks at ytop."""
    hw = S.ARM * 0.86 * S.HK; L = S.HL
    lo, hi = 400, ytop
    for _ in range(30):
        m = (lo + hi) / 2
        ext, end, d, w = v_arm(S, side, m)
        lo, hi = (m, hi) if head(end, d, hw, L).bounds[3] < ytop else (lo, m)
    ext, end, d, w = v_arm(S, side, lo)
    return union(inter(ext, halfplane(add(end, d, -notch(hw)), d)), head(end, d, hw, L))


def t_without_top(S, ycut): return clip(S.path('t'), (-100, -100, 1000, ycut))


def t_curl(S, d, r, x_tip_rel):
    """The top of the t's stem turns (d=+1 right, -1 left) in an even curve the stem's width,
    and runs on level to an arrowhead whose point is at x_tip_rel (the t's coordinates)."""
    s0, s1 = S.t_stem; w = s1 - s0; c = (s0 + s1) / 2
    hw = S.XBW * 0.85
    top = max(S.t_top + 8, 690); yc = top - hw / 2
    r = min(r, yc - S.xb[1] - 15 - w / 2 + hw / 2); y0 = yc - r; acx = c + d * r
    keep = clip(S.path('t'), (-100, -100, 1000, y0 + 0.5))
    a0, a1 = (math.pi, math.pi / 2) if d > 0 else (0, math.pi / 2)
    def f(t):
        a = a0 + (a1 - a0) * t
        return (acx + r * math.cos(a), y0 + r * math.sin(a)), (-math.sin(a) * (a1 - a0), math.cos(a) * (a1 - a0))
    turn = curve_band(f, lambda t: w + (hw - w) * (0.5 - 0.5 * math.cos(math.pi * t)))
    L = hfit(yc - 500, hw, S.HL * 0.8)
    tip = (x_tip_rel - d * tip_for((d, 0), hw), yc)
    shaft = band((acx - d * 1, yc), tip, hw)
    return union(keep, rect(s0, y0 - 40, s1, y0 + 1), turn, shaft, head(tip, (d, 0), hw, L))


VARIANTS = {}
def variant(id_):
    def deco(fn): VARIANTS[id_] = fn; return fn
    return deco


@variant('v01')
def v01(S, Wd):
    a = mv(arm_arrow(S, 'R', 745), Wd.x(0))
    Wd.adds.append(a); Wd.clear(0, [a], share=0.7)     # the head is over the e: a smaller gap reads as open


@variant('v02')
def v02(S, Wd):
    Wd.adds.append(mv(arm_arrow(S, 'L', 745), Wd.x(0)))


@variant('v06')
def v06(S, Wd):
    V = S.V; w = S.XBW * 0.85; y = 640; L = S.HL * 0.75
    tipx = V['F'][0] - 10
    Wd.adds.append(mv(arrow((V['B'][0] + 15, y), (tipx - tip_for((1, 0), w), y), w, L), Wd.x(0)))


@variant('v13')
def v13(S, Wd):
    it = Wd.idx('t'); w = S.t_stem[1] - S.t_stem[0]; hw = w * 0.82 * S.HK
    y = S.t_top - 50                           # the stem runs on from just under its slanted top
    s0, s1 = S.ctx.hspans(S.path('t'), y - 10)[0]
    tip = ((s0 + s1) / 2, 770 - tip_for((0, 1), hw))
    L = S.HL                                   # the barbs end well clear of the crossbar
    while head(tip, (0, 1), hw, L).bounds[1] < S.xb[1] + 0.6 * S.XBW and L > 60: L -= 4
    Wd.repl[it] = union(t_without_top(S, y + 10), rect(s0, y, s1, tip[1] - notch(hw)), head(tip, (0, 1), hw, L))


@variant('v15')
def v15(S, Wd):
    it = Wd.idx('t'); end = Wd.adv() - Wd.x(it) + (35 if Wd.plural else -15)
    Wd.repl[it] = t_curl(S, 1, S.STEM * 1.3 + 40, end)


@variant('v16')
def v16(S, Wd):
    it = Wd.idx('t'); ie = Wd.idx('e')
    Wd.repl[it] = t_curl(S, -1, S.STEM * 1.3 + 40, Wd.x(ie) + 40 - Wd.x(it))


@variant('v18')
def v18(S, Wd):
    it = Wd.idx('t'); s0, s1 = S.t_stem; xb0, xb1 = S.xb
    t = S.path('t')
    t = diff(t, rect(-100, xb0 - 0.5, s0 + 0.5, xb1 + 0.5)); t = diff(t, rect(s1 - 0.5, xb0 - 0.5, 1000, xb1 + 0.5))
    hw = S.XBW; c = (s0 + s1) / 2
    half = max(c - S.t_bar[0], S.t_bar[1] - c) - hw * 0.3
    L = 0.85 * half / math.sin(ANG)
    h = head((c, 0), (0, 1), hw, L)
    Wd.repl[it] = union(t, mv(h, 0, S.t_top - 115 - h.bounds[3]))    # the point 115 below the stem's top


def _tangent(full, k, forward):
    """Unit tangent of an outline at on-curve point k of a contour of (point, on) pairs:
    towards the next point (forward) or from the previous one."""
    n = len(full); p = full[k][0]
    q = full[(k + 1) % n][0] if forward else full[k - 1][0]
    v = (q[0] - p[0], q[1] - p[1]) if forward else (p[0] - q[0], p[1] - q[1])
    return unit(v)


@variant('v20')
def v20(S, Wd):
    ic = Wd.idx('c'); c = S.c
    p, q = c[8], c[9]                          # the lower terminal: inner, outer end of its cut
    full = S.c_full
    kp = next(i for i, (pt, on) in enumerate(full) if on and pt == p)
    kq = next(i for i, (pt, on) in enumerate(full) if on and pt == q)
    tp = _tangent(full, kp, forward=False)     # the inner edge arrives at p
    tq = _tangent(full, kq, forward=True)      # the outer edge leaves q (contour order)
    tq = (-tq[0], -tq[1]) if dot(tq, tp) < 0 else tq
    d = unit(add(tp, tq))                      # the way the stroke is heading at its end
    w = abs(dot((p[0] - q[0], p[1] - q[1]), nrm(d)))   # its width, square to that
    m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    hw = S.XBW * 0.95 * S.HK
    n = nrm(d); sgn = 1 if dot((p[0] - m[0], p[1] - m[1]), n) > 0 else -1
    body = S.path('c'); gmin = 0.55 * w
    def draw(ln, L):
        # each edge leaves its own end of the cut along its own tangent and runs into a
        # straight shaft along d, so the c's edges carry on without a corner
        end = add(m, d, ln)
        ep, eq = add(end, n, sgn * hw / 2), add(end, n, -sgn * hw / 2)
        k = min(ln, 140) * 0.45
        ext = pathops.Path(); pen = ext.getPen()
        pen.moveTo(q); pen.lineTo(p)
        pen.curveTo(add(p, tp, k), add(ep, d, -k * 0.6), ep)
        pen.lineTo(eq)
        pen.curveTo(add(eq, d, -k * 0.6), add(q, tq, k), q)
        pen.closePath()
        ext2 = pathops.Path(); ext.draw(ext2.getPen()); ext2.simplify(fix_winding=True)
        tip = add(end, d, tip_for(d, hw) * 0.3)
        return ext2, band(add(end, d, -2), tip, hw), head(tip, d, hw, L)
    # the longest head (barbs as long as the font's arrows', down to 0.7 of them), on the
    # shortest shaft (up to 160 units more than the lab's) that lets it keep its lower barb
    # above the baseline and its barbs clear of the c's own stroke
    base = 95 + 0.4 * w; pick = None
    for L in [S.HL * (1 - 0.1 * j) for j in range(4)]:
        for ln in [base + 10 * i for i in range(17)]:
            ext, shaft, h = draw(ln, L)
            if h.bounds[1] >= -12 and dist(h, body, gmin + 1) >= gmin:
                pick = (ln, L); break
        if pick: break
    if pick is None: raise SystemExit('vector: v20 found no head that fits')
    ext, shaft, h = draw(*pick)
    Wd.repl[ic] = union(body, ext, shaft, h)
    Wd.clear(ic)


@variant('v23')
def v23(S, Wd):
    ir = Wd.idx('r'); r = S.R; s0, s1 = S.r_stem
    stem = clip(S.path('r'), (-100, -100, s1, 1000))
    w = math.hypot(r[7][0] - r[8][0], r[7][1] - r[8][1]) * 0.95; L = S.HL * 0.85
    d = (math.cos(math.radians(36)), math.sin(math.radians(36)))
    # the arm's lower edge leaves the stem's right side where the old shoulder met it
    y_out = r[4][1] - 40
    p0 = (s1 - w / 2 / d[1] - 5, y_out - (w / 2) * d[0])
    tip = add(p0, d, (650 - p0[1]) / d[1] - tip_for(d, w) * 0.9)
    Wd.repl[ir] = union(stem, clip(band(add(p0, d, -30), add(tip, d, -notch(w * S.HK)), w), (s0 + 2, -100, 2000, 2000)), head(tip, d, w * S.HK, L))
    if Wd.plural: Wd.clear(ir)


@variant('v25')
def v25(S, Wd):
    ext, end, d, w = v_arm(S, 'R', 471); x0 = Wd.x(0)
    ic = Wd.idx('c'); tipx = Wd.x(ic) - x0 + S.c[3][0] - 20
    y = 660; hw = S.XBW; L = hfit(790 - y, hw, S.HL * 0.8)
    tip = (tipx - tip_for((1, 0), hw), y)
    p0 = end; p3 = (p0[0] + 260, y)
    arc = curve_band(cubic(p0, add(p0, d, 120), (p3[0] - 110, y), p3), lambda t: w + (S.XBW - w) * t * t * (3 - 2 * t))
    Wd.adds.append(mv(union(ext, arc, rect(p3[0] - 2, y - S.XBW / 2, tip[0], y + S.XBW / 2), head(tip, (1, 0), hw, L)), x0))


# --- build ------------------------------------------------------------------------------------
def glyphs(ctx):
    order = ctx.font.getGlyphOrder()
    if DEFAULT not in order: raise SystemExit(f'vector: no {DEFAULT} (build.py\'s ss16 proposal 171)')
    S = Style(ctx)
    for id_ in IDS:
        for plural in (False, True):
            Wd = Word(S, plural); VARIANTS[id_](S, Wd); p, adv = Wd.build()
            name = word_glyph(id_, plural)
            if name in order: raise SystemExit(f'vector: the font already has {name}')
            ctx.add(name, p, adv)
            ctx.GDEF_CLASS[name] = 2
        from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
        comp = GlyphComponent(); comp.glyphName, comp.x, comp.y, comp.flags = DEFAULT, 0, 0, 0x4   # ROUND_XY_TO_GRID
        g = Glyph(); g.numberOfContours = -1; g.components = [comp]; m = marker_glyph(id_)
        ctx.glyf[m] = g; g.recalcBounds(ctx.glyf)
        ctx.hmtx[m] = (ctx.W(DEFAULT), ctx.hmtx[DEFAULT][1])
        if m not in ctx.font.getGlyphOrder(): ctx.font.setGlyphOrder(ctx.font.getGlyphOrder() + [m])
        ctx.GDEF_CLASS[m] = 1
    ctx.log(f'{len(IDS)} forms of vector and vectors; advances '
            + ', '.join(f'{i} {ctx.W(word_glyph(i, False))}/{ctx.W(word_glyph(i, True))}' for i in IDS)
            + f' (default {round(S.layout[False][1])}/{round(S.layout[True][1])})')


def features(ctx):
    cm = ctx.font.getBestCmap()
    tail = [cm[ord(ch)] for ch in 'ector']
    alts = ' '.join([DEFAULT] + [marker_glyph(i) for i in IDS])
    ligs = ''.join(f"  sub {marker_glyph(i)} {' '.join(tail)} {cm[ord('s')]} by {word_glyph(i, True)};\n"
                   f"  sub {marker_glyph(i)} {' '.join(tail)} by {word_glyph(i, False)};\n" for i in IDS)
    ctx.gsub(f'lookup VECTOR_RAND {{\n  sub {DEFAULT} from [{alts}];\n}} VECTOR_RAND;\n'
             f'lookup VECTOR_WORD {{\n{ligs}}} VECTOR_WORD;\n'
             'feature rand { lookup VECTOR_RAND; lookup VECTOR_WORD; } rand;\n',
             after='ss16_front')

"""fleurons: printers' ornaments for Torchlette Sans (round 4), each started from an existing,
professionally drawn design under an OFL-compatible licence, a public-domain drawing or
public-domain data, or constructed, and refitted to Torchlette's stroke in every style.

Method. The icon sources (Tabler, Phosphor) are monoline drawings on a 24-unit grid
(Phosphor: 256): their centre lines are read from the published SVG path data, kept verbatim
below, placed at 36 font units per grid unit (the 18-unit live area is 648 units tall, centred
on the capitals' middle, y 352), and stroked here with round caps and joins at the ornaments'
stroke for the style: 58 at Regular (between the operators' bar, 53, and the stem, 66), in
proportion to the stem below Regular and as its square root above, so the counters survive in
Black (Light 44, Medium 64, SemiBold 68, Bold 78, ExtraBold 85, Black 91). The stroker offsets
each centre line by fitted cubics that are tangent-continuous at every joint, so the outlines
have no kinks of their own; where two strokes touch, `polish` (in the post phase, on the final
outlines) removes the few-unit segments and spikes the union leaves and makes smooth the points
whose tangents turn by less than 30 degrees. The Noto Sans Symbols 2 outlines are used as Noto
draws them (one weight; scaled, with shallow corners made smooth by the same pass). Torchlette's
own glyphs supply ⁂ and ※.

Sources (every glyph):

  code    glyph            source and licence
  U+E900  uniE900 neuron   original drawing (round 3) after Santiago Ramón y Cajal's drawings of
                           cortical pyramidal cells (c. 1899-1904; public domain): a filled
                           soma, tapering dendrites, the axon. Nothing traced. FL1.
  U+E901  logical neuron   Tabler Icons "logic-buffer" (MIT), terminals after McCulloch & Pitts
                           1943, Fig. 1; round 3 spaces the inputs for Black. FL2.
  U+E902  perceptron       Tabler "binary-tree-2" (MIT), turned, output stroke added. FL3.
  U+E903  network          Tabler "hierarchy-3" (MIT), turned.
  U+E904  sigmoid          Tabler "ease-in-out" (MIT).
  U+E905  Lissajous        constructed (round 3): the 3:2 figure, x = sin(3t + phase), y = sin 2t
                           (Lissajous 1857); the family is at U+E940-E94B.
  U+E906  AND gate         Tabler "logic-and" (MIT).
  U+E907  λ roundel        Tabler "circle" and "lambda" (MIT).
  U+E908  Galton bell      after Tabler "chart-histogram" (MIT), vertical axis removed, five
                           symmetric bars; round 3 seats a normal curve on the bars. FL4.
  U+E909  Bayes net        constructed (round 4) in Pearl's notation (Pearl 1988): Jordan's pick
                           in round 4, the plate (a parameter, its arrow into a plate with N in
                           the corner, the observed node inside); the same glyph as U+E975.
  U+E90A  eye              Tabler "eye" (MIT), pupil filled.
  U+E90B  Necker cube      Phosphor Icons "cube-transparent" (MIT), centre lines of the regular
                           weight; round 3 thins its stroke above Regular. FL7.
  U+E90C  Venn             constructed: three circles (Venn 1880), Tabler's stroke. FL6.
  U+E90D  Nightingale      constructed from Nightingale's 1858 monthly death rates, April 1854 to
                           March 1855 (public-domain data). FL11.
  U+E90E  Playfair         constructed (round 4) after Playfair's Commercial and Political Atlas
                           (1786): two series crossing over plain axes, the balance solid or
                           hatched; Jordan's pick in round 4, the bold hatches (as U+E97A). FL12.
  U+E90F  Feynman vertex   constructed (after Feynman 1949), Tabler's arrowheads mitred. FL14.
  U+E910  glider           Tabler "grid-3x3" (MIT) with five discs (Guy 1969; Raymond's hacker
                           emblem). FL15.
  U+E911  Turing tape      constructed tape with the digits 1 0 1 in its cells, after Tabler
                           "caret-down" (MIT) as the head: round 4's 1.5 em tape (U+E97B), with
                           round 5's smaller, squatter digits (TAPE5_DIGITS). FL16.
  U+E912  Tower of Hanoi   constructed (Lucas 1883): the starting position; all 27 positions
                           are at U+E950-E96A. FL17.
  U+E913  evidence bound   constructed (Ratcliff 1978): axes, dashed bounds, a walk. FL21.
  U+E914  forward/backward Tabler "arrows-right-left" (MIT), two unit discs added. FL22.
  U+E915  signal/noise     constructed (round 3): noise hills, a spike, a baseline. FL23.
  U+E940-E94B  Lissajous family  constructed: twelve figures a:b at two phases (see LISSAJOUS).
  U+E950-E96A  Hanoi family      constructed: the 27 positions of three discs on three pegs.
  U+E970-E97C  round 4 options   constructed, temporary: eight Bayes nets (U+E970-E977, after
                           Pearl 1988), three Playfair charts (U+E978-E97A, after Playfair 1786),
                           two Turing tapes (U+E97B-E97C). Superseded in round 5 by the picks at
                           U+E909, U+E90E and U+E911; kept, unchanged, until they are dropped.
  U+E920  vine left        Noto Sans Symbols 2 U+1F658 NORTH WEST POINTING VINE LEAF (OFL).
  U+E921  vine right       Noto Sans Symbols 2 U+1F65A NORTH EAST POINTING VINE LEAF (OFL).
  U+E922  quilt            Noto Sans Symbols 2 U+1F668 HOLLOW QUILT SQUARE ORNAMENT (OFL): the
                           border unit, set flush.
  U+E923-E925 swelled rules  constructed (the printers' swelled rule), 1, 2 and 3 ems, flush.
  U+2766 ❦ U+2767 ❧ U+2619 ☙  Noto Sans Symbols 2 floral hearts (OFL).
  U+261E ☞ U+261C ☜        Noto Sans Symbols 2 white pointing indexes (OFL).
  U+2042 ⁂                 three of Torchlette's own asterisks (Mulish, OFL).
  U+203B ※                 Torchlette's own × and four of its dots (Mulish, OFL).

Versions: Tabler Icons 3.35.0 (npm @tabler/icons), Phosphor Icons core 2.1.1 (npm @phosphor-icons/core), NotoSansSymbols2-Regular.ttf from
notofonts.github.io (fonts/NotoSansSymbols2/unhinted/ttf).

Licences. Tabler Icons: MIT License, Copyright (c) 2020-2025 Paweł Kuna. Phosphor Icons: MIT
License, Copyright (c) 2023 Phosphor Icons. MIT: "Permission is hereby granted, free of charge,
to any person obtaining a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so, subject to the
following conditions: The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT
WARRANTY OF ANY KIND, EXPRESS OR IMPLIED." Noto Sans Symbols 2:
SIL Open Font License 1.1, Copyright 2022 The Noto Project Authors
(https://github.com/notofonts/symbols). These notices must travel with the font (OFL.txt or the
README's credits). Lucide (ISC), used for FL12 in round 2, is no longer used: round 3 draws the
Playfair chart from scratch. Not used: The Noun Project (its icons are CC BY or paid, which an OFL font
cannot carry) and OpenMoji (CC BY-SA).

Drafts at U+E930-E938, kept out of ornm (from the repertoire's FL list): FL5 Darwin's tree
(round 3: redrawn after Notebook B, p. 36, 1837, not traced: three limbs, six living tips with
his cross stroke); FL8 duck-rabbit (traced from the 1892 Fliegende Blaetter printing; round 3
sets the lower ear lower so the two ears stay apart); FL9 Peirce's scroll (round 4: round 2's cuts, the circle touching the oval, with round 3's
monoline P and Q in the cuts' stroke); FL10 Llull's Figure A (round 3: simplified to the ring, nine principles and the
{9/4} star of chords); FL18 Hamilton's formula and FL19 the four alchemical elements, kept.

Round 3 helpers. `stroke_exact` strokes straight-line drawings as rectangles and discs (Skia's
union mishandled the Necker cube's coincident round joins at some strokes); `stroke_dense`
strokes curves that turn tighter than half the stroke (Lissajous figures, the spike, the
neuron's tapering dendrites) as a polygon union whose outline is refitted as smooth curves.
Elsewhere: FL13 Penrose node is the tensordiagram module's SH3; FL20's draughts man and gate are
GM2 and CP5 in the games lane, and the glider is U+E910.

Italics. The ornaments are pictures and stand upright in the italics: each is drawn where the
reslant will put it (offset by the slant at its centre height) and sheared back, as ui.py does.

Layout. ornm (OpenType ornaments): the bullet • takes every ornament as an alternate
(`font-variant-alternates: ornaments(n)` picks the nth), and with ornm on, the letters a-z then
A-I become the ornaments in the order of the table above (a = U+E900 ... ; the marks last).

Nothing existing is changed. Glyph names: uniE900 ... uniE915, uniE920 ... uniE925, uniE930 ...
uniE938, uniE940 ... uniE94B, uniE950 ... uniE96A, uniE970 ... uniE97C, uni2766, uni2767, uni2619, uni261E, uni261C,
uni2042, uni203B. The families and the round 4 options stay out of ornm until they are picked. Code points
outside the Makefile's web subset ranges: U+E900-E97C, U+2619, U+261C, U+261E, U+2766, U+2767 (U+2042 and
U+203B are inside U+2000-206F). ornm is not in web_features.txt.
"""
import math

import pathops
from fontTools.pens.basePen import BasePen
from fontTools.svgLib.path import parse_path

EPS = 1e-6
# ---- centerline representation -------------------------------------------------------
# A subpath is (segs, closed); a seg is a tuple of 2 (line) or 4 (cubic) points.

class _Collect(BasePen):
    """Collect drawing commands as subpaths of line and cubic segments."""
    def __init__(self, xf=None):
        super().__init__(None); self.subs = []; self.cur = None; self.start = None; self.segs = None
        self.xf = xf or (lambda p: p)
    def _moveTo(self, p):
        self._flush(False); p = self.xf(p); self.cur = self.start = p; self.segs = []
    def _lineTo(self, p):
        p = self.xf(p)
        if math.dist(p, self.cur) > EPS: self.segs.append((self.cur, p))
        self.cur = p
    def _curveToOne(self, a, b, c):
        a, b, c = self.xf(a), self.xf(b), self.xf(c)
        if max(math.dist(self.cur, q) for q in (a, b, c)) > EPS: self.segs.append((self.cur, a, b, c))
        self.cur = c
    def _closePath(self):
        if self.segs is not None and math.dist(self.cur, self.start) > 1e-3: self.segs.append((self.cur, self.start))
        self._flush(True)
    def _endPath(self): self._flush(False)
    def _flush(self, closed):
        if self.segs: self.subs.append((self.segs, closed))
        self.segs = None
    def done(self): self._flush(False); return self.subs


def svg_subpaths(d, xf=None):
    pen = _Collect(xf); parse_path(d, pen); return pen.done()


# ---- segment geometry ----------------------------------------------------------------
def pt(s, t):
    if len(s) == 2: return (s[0][0] + (s[1][0] - s[0][0]) * t, s[0][1] + (s[1][1] - s[0][1]) * t)
    u = 1 - t; a, b, c, d = s
    return (u**3 * a[0] + 3*u*u*t * b[0] + 3*u*t*t * c[0] + t**3 * d[0],
            u**3 * a[1] + 3*u*u*t * b[1] + 3*u*t*t * c[1] + t**3 * d[1])


def der(s, t):
    if len(s) == 2: return (s[1][0] - s[0][0], s[1][1] - s[0][1])
    u = 1 - t; a, b, c, d = s
    return (3*u*u*(b[0]-a[0]) + 6*u*t*(c[0]-b[0]) + 3*t*t*(d[0]-c[0]),
            3*u*u*(b[1]-a[1]) + 6*u*t*(c[1]-b[1]) + 3*t*t*(d[1]-c[1]))


def norm(v):
    L = math.hypot(*v); return (v[0] / L, v[1] / L) if L > EPS else None


def tan(s, t):
    """Unit tangent at t, robust at degenerate handles."""
    v = norm(der(s, t))
    if v: return v
    for dt in (1e-4, 1e-3, 1e-2):
        tt = min(1.0, t + dt) if t < 0.5 else max(0.0, t - dt)
        q, p = pt(s, tt), pt(s, t)
        v = norm((q[0] - p[0], q[1] - p[1]) if tt > t else (p[0] - q[0], p[1] - q[1]))
        if v: return v
    return norm((s[-1][0] - s[0][0], s[-1][1] - s[0][1])) or (1.0, 0.0)


def split(s, t):
    if len(s) == 2:
        m = pt(s, t); return (s[0], m), (m, s[1])
    a, b, c, d = s
    L = lambda p, q: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    ab, bc, cd = L(a, b), L(b, c), L(c, d); abc, bcd = L(ab, bc), L(bc, cd); m = L(abc, bcd)
    return (a, ab, abc, m), (m, bcd, cd, d)


def angle(u, v):
    return abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))


# ---- offsetting ------------------------------------------------------------------------
def _fit(A, ta, B, tb, samples):
    """Cubic from A (tangent ta) to B (tangent tb) through samples [(t, point)]: least
    squares for the two handle lengths."""
    m11 = m12 = m22 = r1 = r2 = 0.0
    for t, P in samples:
        u = 1 - t; b0, b1, b2, b3 = u**3, 3*u*u*t, 3*u*t*t, t**3
        base = (A[0] * (b0 + b1) + B[0] * (b2 + b3), A[1] * (b0 + b1) + B[1] * (b2 + b3))
        e = (P[0] - base[0], P[1] - base[1])
        g1 = (b1 * ta[0], b1 * ta[1]); g2 = (-b2 * tb[0], -b2 * tb[1])
        m11 += g1[0]**2 + g1[1]**2; m22 += g2[0]**2 + g2[1]**2; m12 += g1[0]*g2[0] + g1[1]*g2[1]
        r1 += g1[0]*e[0] + g1[1]*e[1]; r2 += g2[0]*e[0] + g2[1]*e[1]
    det = m11 * m22 - m12 * m12
    if abs(det) < 1e-9: L = math.dist(A, B) / 3; al = be = L
    else: al = (r1 * m22 - r2 * m12) / det; be = (m11 * r2 - m12 * r1) / det
    return (A, (A[0] + al * ta[0], A[1] + al * ta[1]), (B[0] - be * tb[0], B[1] - be * tb[1]), B), al, be


def offset_seg(s, d, ta=None, tb=None, tol=0.5, depth=0):
    """The offset of s by d (left of the direction), as a list of cubics/lines, G1 at
    the joins. ta/tb override the end tangents (to make a smooth joint exact)."""
    t0 = ta or tan(s, 0); t1 = tb or tan(s, 1)
    if len(s) == 2:
        n = (-t0[1] * d, t0[0] * d)
        return [((s[0][0] + n[0], s[0][1] + n[1]), (s[1][0] + n[0], s[1][1] + n[1]))]
    def off(t, tt=None):
        p = pt(s, t); v = tt or tan(s, t); return (p[0] - v[1] * d, p[1] + v[0] * d)
    A, B = off(0, t0), off(1, t1)
    samp = [(k / 12, off(k / 12)) for k in range(1, 12)]
    c, al, be = _fit(A, t0, B, t1, samp)
    if al > 0 and be > 0:       # the error: each true offset point's distance to the fitted curve
        dense = [pt(c, k / 60) for k in range(61)]
        err = max(min(math.dist(P, q) for q in dense) for _, P in samp)
    else: err = 1e9
    if err > tol and depth < 7:
        a, b = split(s, 0.5); tm = tan(s, 0.5)
        return offset_seg(a, d, t0, tm, tol, depth + 1) + offset_seg(b, d, tm, t1, tol, depth + 1)
    if al <= 0 or be <= 0:      # degenerate (inside a cusp): keep the polyline-ish shape
        L = math.dist(A, B) / 3; c = (A, (A[0] + L * t0[0], A[1] + L * t0[1]), (B[0] - L * t1[0], B[1] - L * t1[1]), B)
    return [c]


def arc_segs(c, r, a0, a1):
    """Cubic arc around c from angle a0 to a1 (radians, signed sweep)."""
    n = max(1, math.ceil(abs(a1 - a0) / (math.pi / 2) - 1e-9)); da = (a1 - a0) / n
    k = 4 / 3 * math.tan(da / 4); out = []; t = a0
    for _ in range(n):
        t1 = t + da
        p0 = (c[0] + r * math.cos(t), c[1] + r * math.sin(t)); p3 = (c[0] + r * math.cos(t1), c[1] + r * math.sin(t1))
        p1 = (p0[0] - k * r * math.sin(t), p0[1] + k * r * math.cos(t))
        p2 = (p3[0] + k * r * math.sin(t1), p3[1] - k * r * math.cos(t1))
        out.append((p0, p1, p2, p3)); t = t1
    return out


def rev(s): return tuple(reversed(s))


def _path_of(segs):
    p = pathops.Path(); pen = p.getPen(); pen.moveTo(segs[0][0])
    for s in segs:
        if len(s) == 2: pen.lineTo(s[1])
        else: pen.curveTo(s[1], s[2], s[3])
    pen.closePath(); return p


def prepare(segs, closed, corner=2.5):
    """(items, corners): items are (seg, ta, tb) with the tangents at a smooth joint
    averaged; corners[i] says whether the joint after item i is a corner."""
    n = len(segs)
    tin = [tan(s, 0) for s in segs]; tout = [tan(s, 1) for s in segs]
    ta, tb = list(tin), list(tout); corners = []
    for i in range(n):
        j = (i + 1) % n
        if j == 0 and not closed: corners.append(False); continue
        if angle(tout[i], tin[j]) < corner:
            m = norm((tout[i][0] + tin[j][0], tout[i][1] + tin[j][1])); tb[i] = ta[j] = m; corners.append(False)
        else: corners.append(True)
    return [(segs[i], ta[i], tb[i]) for i in range(n)], corners


def side(items, corners, d, closed, join='round'):
    """One side of the stroke (offset d, left of the direction), with round joins on the
    outer side of each corner and the offsets run through the joint on the inner side
    (the loop that leaves is removed by the final simplify)."""
    out = []; n = len(items)
    offs = [offset_seg(s, d, a, b) for s, a, b in items]
    for i in range(n):
        out += offs[i]
        if not corners[i] or (i == n - 1 and not closed): continue
        j = (i + 1) % n; J = items[i][0][-1]
        Pe, Ps = offs[i][-1][-1], offs[j][0][0]
        t1, t2 = items[i][2], items[j][1]
        turn = t1[0] * t2[1] - t1[1] * t2[0]
        if turn * d < 0 and join == 'miter':      # outer side, mitred: the offset lines meet
            u1, u2 = t1, t2
            den = u1[0] * u2[1] - u1[1] * u2[0]
            k = ((Ps[0] - Pe[0]) * u2[1] - (Ps[1] - Pe[1]) * u2[0]) / den
            M = (Pe[0] + k * u1[0], Pe[1] + k * u1[1])
            out += [(Pe, M), (M, Ps)]
        elif turn * d < 0:        # outer side: an arc about the joint
            a0 = math.atan2(Pe[1] - J[1], Pe[0] - J[0]); a1 = math.atan2(Ps[1] - J[1], Ps[0] - J[0])
            da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            out += arc_segs(J, abs(d), a0, a0 + da)
        else:
            out += [(Pe, J), (J, Ps)]
    return out


def stroke_sub(segs, closed, w, cap='round', join='round'):
    items, corners = prepare(segs, closed)
    d = w / 2
    L = side(items, corners, d, closed, join)
    R = [rev(x) for x in reversed(side(items, corners, -d, closed, join))]
    if closed:
        p = pathops.Path(); _path_of(L).draw(p.getPen())
        inner = _path_of(R)
        if abs(inner.area) > (0.8 * w) ** 2: inner.draw(p.getPen())   # a ring too small for a counter is a dot
        return p
    end, tend = items[-1][0][-1], items[-1][2]; start, tst = items[0][0][0], items[0][1]
    segs_ = list(L)
    if cap == 'round':
        a = math.atan2(tend[0], -tend[1])
        segs_ += arc_segs(end, d, a, a - math.pi) + R
        a = math.atan2(-tst[0], tst[1])
        segs_ += arc_segs(start, d, a, a - math.pi)
    else:
        segs_ += [(L[-1][-1], R[0][0])] + R + [(R[-1][-1], L[0][0])]
    p = _path_of(segs_)
    return p


def stroke(subs, w, cap='round', join='round'):
    """Outline of a list of subpaths stroked at width w (round joins at corners). A
    subpath shorter than a unit is a dot: a disc of the stroke's diameter."""
    parts = []
    for segs, closed in subs:
        if sum(math.dist(s[0], s[-1]) for s in segs) < 1:
            parts.append(circle(segs[0][0], w / 2)); continue
        parts.append(stroke_sub(segs, closed, w, cap, join))
    return union(parts)


def _shift(p, dx, dy):
    from fontTools.pens.transformPen import TransformPen
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (1, 0, 0, 1, dx, dy))); return q


def union(parts):
    """Union of filled paths. One simplify of all of them under nonzero winding (every
    simplified path has the same orientation convention); if Skia's solver gives up on a
    degenerate coincidence, the parts are merged one by one, a failing part nudged by a
    hundredth of a unit."""
    ps = []
    for q in parts:
        if q is None: continue
        q2 = pathops.Path(q); q2.simplify(fix_winding=True); ps.append(q2)
    out = pathops.Path()
    for q in ps: q.draw(out.getPen())
    try:
        out.simplify(fix_winding=True); return out
    except pathops.PathOpsError:
        pass
    out = pathops.Path()
    for q in ps:
        for k in range(6):
            try:
                out = pathops.op(out, _shift(q, 0.01 * k, 0.007 * k) if k else q, pathops.PathOp.UNION); break
            except pathops.PathOpsError:
                continue
        else:
            raise pathops.PathOpsError("union failed")
    return out


def diff(a, b): return pathops.op(a, b, pathops.PathOp.DIFFERENCE)
def inter(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)


def circle(c, r):
    segs = arc_segs(c, r, 0, 2 * math.pi); return _path_of(segs)


def ring(c, r, w):
    return diff(circle(c, r + w / 2), circle(c, r - w / 2))


def disc(c, r): return circle(c, r)


def capsule(a, b, w):
    return stroke([([(a, b)], False)], w)


# ---- outline polish ------------------------------------------------------------------------
def _turn(u, v):
    if u == (0, 0) or v == (0, 0): return 0.0
    return math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))


def polish(g, short=6, kink=None, spur_leg=15, grid=True, aggressive=False):
    """Clean a TrueType glyph where strokes met: the few-unit segments and spikes that a
    union leaves where two round ends or a round end and an edge touch are removed (their
    points merged), and every on-curve point next to a handle whose tangent turns by less
    than 30 degrees is made smooth: a point between two handles moves onto the line joining
    them, the handle of a curve that follows a straight segment onto that segment's line.
    With grid=False the points stay unrounded (for a source outline, smoothed before it is
    scaled). Returns the number of edits."""
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    from array import array
    if g.isComposite() or g.numberOfContours <= 0: return 0
    coords, ends, flags = g.coordinates, g.endPtsOfContours, g.flags
    cs, s0, edits = [], 0, 0
    for e in ends:
        raw = [[float(coords[i][0]), float(coords[i][1]), bool(flags[i] & 1), False] for i in range(s0, e + 1)]; s0 = e + 1
        c = []                                   # the implied on-curve points made explicit (marked)
        for i, p in enumerate(raw):
            c.append(p)
            q = raw[(i + 1) % len(raw)]
            if not p[2] and not q[2]: c.append([(p[0] + q[0]) / 2, (p[1] + q[1]) / 2, True, True])
        changed = True; guard = 0
        while changed and len(c) > 4 and guard < 5000:
            changed = False; guard += 1; n = len(c)
            # orientation for the convexity of a spur
            area = sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(n))
            orient = 1 if area > 0 else -1
            for i in range(n):
                p, q, r = c[i], c[(i + 1) % n], c[i - 1]
                if p[2] and q[2] and math.dist(p[:2], q[:2]) < short:            # a tiny line
                    m = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2, True, False]
                    c[i] = m; del c[(i + 1) % n]; changed = True; edits += 1; break
                t = c[(i + 2) % n]
                if p[2] and (aggressive or not p[3]) and not q[2] and t[2] and (aggressive or not t[3]) and math.dist(p[:2], t[:2]) < short:   # a tiny curve
                    m = [(p[0] + t[0]) / 2, (p[1] + t[1]) / 2, True, False]
                    for k in sorted([(i + 1) % n, (i + 2) % n], reverse=True): del c[k]
                    c[i if i < len(c) else 0] = m if i < len(c) else m
                    changed = True; edits += 1; break
                if not p[2]: continue
                tin = (p[0] - r[0], p[1] - r[1]); tout = (q[0] - p[0], q[1] - p[1])
                a = _turn(tin, tout)
                legs = min(math.dist(r[:2], p[:2]), math.dist(p[:2], q[:2]))
                if abs(a) > 150 and legs < spur_leg and a * orient > 0:          # a spike
                    del c[i]; changed = True; edits += 1; break
                if kink is None or (r[2] and q[2]) or not (kink[0] < abs(a) < kink[1]): continue
                if not r[2] and not q[2]:                                      # between two handles: onto their line
                    L2 = (q[0] - r[0]) ** 2 + (q[1] - r[1]) ** 2
                    t = max(0.05, min(0.95, ((p[0] - r[0]) * (q[0] - r[0]) + (p[1] - r[1]) * (q[1] - r[1])) / L2))
                    p[0], p[1] = r[0] + t * (q[0] - r[0]), r[1] + t * (q[1] - r[1])
                else:                                                           # a line runs into a curve
                    h, o = (q, r) if r[2] else (r, q)
                    d = norm((p[0] - o[0], p[1] - o[1])); L = math.dist(p[:2], h[:2])
                    h[0], h[1] = p[0] + d[0] * L, p[1] + d[1] * L
                changed = True; edits += 1        # the list keeps its length: carry on
        if len(c) <= 4:                          # a sliver left where two edges touched
            xs = [p[0] for p in c]; ys = [p[1] for p in c]
            if max(xs) - min(xs) < 8 or max(ys) - min(ys) < 8: edits += 1; continue
        out = []                                 # the implied points that are still implied go back
        for i, p in enumerate(c):
            a, b = c[i - 1], c[(i + 1) % len(c)]
            if p[2] and not a[2] and not b[2] and abs((a[0] + b[0]) / 2 - p[0]) < 0.51 and abs((a[1] + b[1]) / 2 - p[1]) < 0.51:
                continue
            out.append(p)
        cs.append(out)
    g.coordinates = GlyphCoordinates([((round(p[0]), round(p[1])) if grid else (p[0], p[1])) for c in cs for p in c])
    g.flags = array('B', [1 if p[2] else 0 for c in cs for p in c])
    g.endPtsOfContours = []; k = -1
    for c in cs: k += len(c); g.endPtsOfContours.append(k)
    g.numberOfContours = len(cs)
    return edits


# ---- shallow corners filleted ----------------------------------------------------------------
def _contours_of(path):
    """A pathops Path as closed contours of line and cubic segments (quadratics raised)."""
    out, cur, start, segs = [], None, None, None
    for verb, pts in path.segments:
        if segs is None and verb not in ('moveTo', 'closePath', 'endPath'):
            start = cur; segs = []                   # a contour that runs on from the last one's end
        if verb == 'moveTo':
            cur = start = pts[0]; segs = []
        elif verb == 'lineTo':
            if math.dist(cur, pts[0]) > EPS: segs.append((cur, pts[0]))
            cur = pts[0]
        elif verb == 'qCurveTo' and pts[-1] is None:      # a closed loop of handles only
            offs = list(pts[:-1]); n = len(offs)
            mids = [((offs[i][0] + offs[(i + 1) % n][0]) / 2, (offs[i][1] + offs[(i + 1) % n][1]) / 2) for i in range(n)]
            segs = []
            for i in range(n):
                a, c, b = mids[i - 1], offs[i], mids[i]
                segs.append((a, (a[0] + 2 / 3 * (c[0] - a[0]), a[1] + 2 / 3 * (c[1] - a[1])),
                             (b[0] + 2 / 3 * (c[0] - b[0]), b[1] + 2 / 3 * (c[1] - b[1])), b))
            start = cur = mids[-1]
        elif verb == 'qCurveTo':
            q = [cur] + list(pts)
            for i in range(1, len(q) - 1):           # a quadratic spline: implied on-curve points
                a = q[i - 1] if i == 1 else ((q[i - 1][0] + q[i][0]) / 2, (q[i - 1][1] + q[i][1]) / 2)
                b = q[i + 1] if i == len(q) - 2 else ((q[i][0] + q[i + 1][0]) / 2, (q[i][1] + q[i + 1][1]) / 2)
                c = q[i]
                segs.append((a, (a[0] + 2 / 3 * (c[0] - a[0]), a[1] + 2 / 3 * (c[1] - a[1])),
                             (b[0] + 2 / 3 * (c[0] - b[0]), b[1] + 2 / 3 * (c[1] - b[1])), b))
            cur = pts[-1]
        elif verb == 'curveTo':
            segs.append((cur,) + tuple(pts)); cur = pts[-1]
        elif verb in ('closePath', 'endPath'):
            if segs is not None:
                if math.dist(cur, start) > 1e-3: segs.append((cur, start))
                if segs: out.append(segs)
            segs = None
    return out


def _seg_len(s, n=12):
    return sum(math.dist(pt(s, k / n), pt(s, (k + 1) / n)) for k in range(n))


def _cut_end(s, d):
    """s shortened by about d at its end: (the remaining piece, the cut point's parameter)."""
    L = _seg_len(s); t = max(0.0, 1 - d / L)
    for _ in range(3):                                # refine t so the chord to the end is d
        q = pt(s, t); e = s[-1]; cur = math.dist(q, e)
        if cur < EPS: break
        t = max(0.0, min(1.0, 1 - (1 - t) * d / cur))
    return split(s, t)[0] if len(s) == 4 else (s[0], pt(s, t))


def _cut_start(s, d):
    r = tuple(reversed(s)); c = _cut_end(r, d); return tuple(reversed(c))


def _segs_path(contours):
    out = pathops.Path(); pen = out.getPen()
    for segs in contours:
        pen.moveTo(segs[0][0])
        for sg in segs:
            if len(sg) == 2: pen.lineTo(sg[1])
            else: pen.curveTo(sg[1], sg[2], sg[3])
        pen.closePath()
    return out


def regularize(contours, short=8.0, handle=4.0):
    """Outline pieces that would not survive rounding to the grid: a segment under `short`
    units is removed (its neighbours meet at its middle, their handles moved with their end
    points), and a cubic's handle under `handle` units on a longer segment is lengthened along
    its own direction, so that the rounded handle still points where the curve goes."""
    out = []
    for segs in contours:
        segs = [list(sg) for sg in segs]
        changed = True
        while changed and len(segs) > 2:
            changed = False
            for i, sg in enumerate(segs):
                if math.dist(sg[0], sg[-1]) < short and _seg_len(tuple(sg)) < short:
                    m = ((sg[0][0] + sg[-1][0]) / 2, (sg[0][1] + sg[-1][1]) / 2)
                    p, q = segs[i - 1], segs[(i + 1) % len(segs)]
                    dp = (m[0] - p[-1][0], m[1] - p[-1][1]); dq = (m[0] - q[0][0], m[1] - q[0][1])
                    p[-1] = m
                    if len(p) == 4: p[2] = (p[2][0] + dp[0], p[2][1] + dp[1])
                    q[0] = m
                    if len(q) == 4: q[1] = (q[1][0] + dq[0], q[1][1] + dq[1])
                    del segs[i]; changed = True; break
        for sg in segs:
            if len(sg) != 4: continue
            L = math.dist(sg[0], sg[3])
            if L < 2 * handle: continue
            hl = min(handle, L / 3)
            for h, o in ((1, 0), (2, 3)):
                v = (sg[h][0] - sg[o][0], sg[h][1] - sg[o][1]); n = math.hypot(*v)
                if 0 < n < hl:
                    sg[h] = (sg[o][0] + v[0] / n * hl, sg[o][1] + v[1] / n * hl)
        out.append([tuple(sg) for sg in segs])
    return out


def fillet(path, lo=2.0, hi=40.0, d=16.0):
    """Every corner of a filled outline where the tangent turns by more than lo and less than
    hi degrees (a shallow corner: where two strokes cross at a narrow angle, or an outline
    meets itself) and at least one side is curved is rounded off: each side is cut back by up
    to d units (a third of the shorter side at most) and a cubic tangent to both cut ends
    joins them, so the outline is smooth there. Sharper corners stay sharp. The outline is
    regularized first (see `regularize`)."""
    out = pathops.Path(); pen = out.getPen()
    for segs in regularize(_contours_of(path)):
        n = len(segs)
        joins = {}
        for i in range(n):
            a, b = segs[i], segs[(i + 1) % n]
            t1, t2 = tan(a, 1), tan(b, 0)
            th = angle(t1, t2)
            if not (lo < th < hi) or (len(a) == 2 and len(b) == 2): continue
            dd = min(d, _seg_len(a) / 3, _seg_len(b) / 3)
            if dd < 1.0: continue
            joins[i] = dd
        segs2 = list(segs)
        for i, dd in joins.items():
            segs2[i] = _cut_end(segs2[i], dd)
            j = (i + 1) % n; segs2[j] = _cut_start(segs2[j], dd)
        pen.moveTo(segs2[0][0])
        for i in range(n):
            s = segs2[i]
            if len(s) == 2: pen.lineTo(s[1])
            else: pen.curveTo(s[1], s[2], s[3])
            if i in joins:
                j = (i + 1) % n; A, B = s[-1], segs2[j][0]
                ta, tb = tan(s, 1), tan(segs2[j], 0); k = math.dist(A, B) * 0.5
                pen.curveTo((A[0] + ta[0] * k, A[1] + ta[1] * k), (B[0] - tb[0] * k, B[1] - tb[1] * k), B)
            elif math.dist(s[-1], segs2[(i + 1) % n][0]) > 1e-3:
                pen.lineTo(segs2[(i + 1) % n][0])
        pen.closePath()
    return out


# ---- the outline gate, and the best cleanup ------------------------------------------------
def outline_problems(g, kink_max=10.0):
    """outline_check.py's tests on one glyph (spur, segment under 4 units, kink: a turn of
    3 to 30 degrees at a point next to a handle), counting only kinks above kink_max."""
    coords, ends, flags = g.coordinates, g.endPtsOfContours, g.flags
    bad = []; s0 = 0
    for e in ends:
        c = [tuple(coords[i]) for i in range(s0, e + 1)]; f = [bool(flags[i] & 1) for i in range(s0, e + 1)]; s0 = e + 1
        n = len(c)
        if not any(f): continue
        k = f.index(True); c = c[k:] + c[:k]; f = f[k:] + f[:k]
        seg = []
        for i in range(n):
            if f[i]: seg.append([c[i], None])
            else:
                seg[-1][1] = c[i]
                if not f[(i + 1) % n]: seg.append([((c[i][0] + c[(i + 1) % n][0]) / 2, (c[i][1] + c[(i + 1) % n][1]) / 2), None])
        m = len(seg)
        orient = 1 if sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(n)) > 0 else -1
        for i in range(m):
            p, ctl = seg[i]; q = seg[(i + 1) % m][0]; pp, pctl = seg[i - 1]
            if math.dist(p, q) < 4: bad.append(('short', p))
            a_ = pctl if pctl is not None else pp; b_ = ctl if ctl is not None else q
            tin = (p[0] - a_[0], p[1] - a_[1]); tout = (b_[0] - p[0], b_[1] - p[1])
            if tin == (0, 0) or tout == (0, 0): continue
            a = abs(_turn(tin, tout)); legs = min(math.dist(pp, p), math.dist(p, q))
            convex = (tin[0] * tout[1] - tin[1] * tout[0]) * orient > 0
            if a > 150 and legs < 15 and convex: bad.append(('spur', p))
            elif (pctl is not None or ctl is not None) and kink_max < a < 30: bad.append(('kink', p))
    return bad


def _drop_specks(g, area=300):
    """Remove contours smaller than `area` square units: a speck of a counter left where an
    arrowhead nearly meets a ring, or a sliver where two edges touched (invisible at any size,
    and a closed-up counter for the clearance check)."""
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    from array import array
    coords, ends, flags = list(g.coordinates), g.endPtsOfContours, list(g.flags)
    keep_c, keep_f, new_ends, s0 = [], [], [], 0
    for e in ends:
        c = coords[s0:e + 1]; f = flags[s0:e + 1]; s0 = e + 1
        a = abs(sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(len(c)))) / 2
        if a < area and len(ends) > 1: continue
        keep_c += c; keep_f += f; new_ends.append(len(keep_c) - 1)
    if len(new_ends) != len(ends):
        g.coordinates = GlyphCoordinates(keep_c); g.flags = array('B', keep_f)
        g.endPtsOfContours = new_ends; g.numberOfContours = len(new_ends)


def unkink(g, maxmove=8.0):
    """The last resort for a kink or a short segment that survives `clean`: a segment under
    4 units long loses its end point (and the handle before it); two handles under 8 units
    apart become one at their midpoint; where a line runs into a curve at a kink, the handle
    moves onto the line (on the grid, so it stays there); an on-curve point between two
    off-curve points whose tangent turns by 3 to 30 degrees is dropped when the midpoint of
    its two handles lies within `maxmove` units of it; TrueType then implies an on-curve
    point at that midpoint, which is on the line between the handles and so cannot kink.
    Returns the number of points dropped."""
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    from array import array
    if g.isComposite() or g.numberOfContours <= 0: return 0
    coords, ends, flags = list(g.coordinates), g.endPtsOfContours, list(g.flags)
    keep_c, keep_f, new_ends, s0, dropped = [], [], [], 0, 0
    for e in ends:
        c = [tuple(coords[i]) for i in range(s0, e + 1)]; f = [flags[i] & 1 for i in range(s0, e + 1)]; s0 = e + 1
        changed = True; guard = 0
        while changed and len(c) > 6 and guard < 5000:
            changed = False; guard += 1
            for i in range(len(c)):                # a segment under 4 units: its end point goes
                if not f[i]: continue
                j = (i + 1) % len(c); k = (i + 2) % len(c)
                if f[j]: nxt = [j]
                elif f[k]: nxt = [j, k]
                else: continue
                if math.dist(c[i], c[nxt[-1]]) < 4:
                    for x in sorted(nxt, reverse=True): del c[x]; del f[x]
                    dropped += 1; changed = True; break
            if changed: continue
            for i in range(len(c)):                # two handles under 8 units apart (a short implied segment): one
                j = (i + 1) % len(c)
                if f[i] or f[j] or math.dist(c[i], c[j]) >= 8: continue
                c[i] = (round((c[i][0] + c[j][0]) / 2), round((c[i][1] + c[j][1]) / 2)); del c[j]; del f[j]
                dropped += 1; changed = True; break
            if changed: continue
            for i in range(len(c)):                # a line runs into a curve at a kink: the handle onto the line,
                if not f[i]: continue              # at a whole multiple of the line's smallest grid step
                n_ = len(c); p, q = c[i - 1], c[(i + 1) % n_]
                if f[i - 1] == f[(i + 1) % n_]: continue
                if f[i - 1]: line, hi = (c[i][0] - p[0], c[i][1] - p[1]), (i + 1) % n_
                else: line, hi = (q[0] - c[i][0], q[1] - c[i][1]), i - 1
                h = (c[hi][0] - c[i][0], c[hi][1] - c[i][1]); sgn = 1 if f[i - 1] else -1
                if not (3.0 < abs(_turn(line, (h[0] * sgn, h[1] * sgn))) < 30.0): continue
                gd = math.gcd(int(line[0]), int(line[1])) or 1; u = (line[0] / gd, line[1] / gd)
                k = round(math.hypot(*h) / math.hypot(*u))
                if k < 1 or k * math.hypot(*u) > 2 * math.hypot(*h) + 4: continue
                new_h = (c[i][0] + sgn * k * u[0], c[i][1] + sgn * k * u[1])
                if new_h == tuple(c[hi]): continue
                c[hi] = new_h; dropped += 1; changed = True; break
            if changed: continue
            for i in range(len(c)):
                a, b = c[i - 1], c[(i + 1) % len(c)]
                if not f[i] or f[i - 1] or f[(i + 1) % len(c)]: continue
                tin = (c[i][0] - a[0], c[i][1] - a[1]); tout = (b[0] - c[i][0], b[1] - c[i][1])
                if not (3.0 < abs(_turn(tin, tout)) < 30.0): continue
                if math.dist(c[i], ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)) > maxmove: continue
                del c[i]; del f[i]; dropped += 1; changed = True; break
        keep_c += c; keep_f += f; new_ends.append(len(keep_c) - 1)
    if dropped:
        g.coordinates = GlyphCoordinates(keep_c); g.flags = array('B', keep_f); g.endPtsOfContours = new_ends
    return dropped


def clean(g, rounds=6):
    """Specks dropped, then of the glyph as it is and of a few rounds of `polish` (cleanup alone, then with the
    shallow-corner smoothing, then also merging tiny curves into their implied neighbours),
    keep the outline with the fewest outline problems."""
    import copy
    _drop_specks(g)
    best = copy.deepcopy(g); score = len(outline_problems(best))
    cur = copy.deepcopy(g)
    for r in range(rounds):
        if score == 0: break
        polish(cur, kink=None if r % 2 == 0 else (3.0, 30.0), aggressive=r >= 2)
        sc = len(outline_problems(cur))
        if sc < score: best, score = copy.deepcopy(cur), sc
    g.coordinates, g.flags, g.endPtsOfContours, g.numberOfContours = best.coordinates, best.flags, best.endPtsOfContours, best.numberOfContours
    return score

# ---- the ornaments ---------------------------------------------------------------------
# Each design takes a Style and returns the ornament's filled outline (pathops.Path),
# upright, in font units, its ink centred on the capitals' middle (CY) unless noted.
# Icon coordinates are the sources' own 24-unit grid (y down), placed by grid().

CY = 352                      # half the cap height (705): the ornaments' centre line
UNIT = 36                     # font units per icon-grid unit: the 18-unit live area is 648 tall


class Style:
    """The stroke of one style. w: the ornaments' monoline stroke, 58 at Regular (between
    the operators' 53 and the stem's 66), in proportion to the stem below Regular and
    as the square root of it above, so the drawings keep their counters in Black (Light 44,
    Bold 78, Black 91)."""
    def __init__(self, sv, src=None, width=None, cmap=None):
        self.sv = sv; self.width = width; self.cmap = cmap
        self.g = sv if sv <= 1 else sv ** 0.5
        self.w = 58 * self.g
        self.src = src            # src(name): a glyph of the font being built, as a Path


def grid(cx=12, cy=12, s=UNIT, rot=0, X=0, Y=CY, mirror=False):
    """A map from an icon's grid (y down) to font units: (cx, cy) goes to (X, Y), rotated
    rot degrees clockwise on the page, scaled by s."""
    a = math.radians(rot); c, sn = math.cos(a), math.sin(a)
    def f(p):
        x, y = p[0] - cx, p[1] - cy
        if mirror: x = -x
        x, y = x * c - y * sn, x * sn + y * c          # clockwise on the page (y down)
        return (X + x * s, Y - y * s)
    return f


def sub(ds, f):
    """Subpaths of a list of SVG path strings under the map f."""
    out = []
    for d in ds: out += svg_subpaths(d, f)
    return out


def chev(tip, deg, L, w, half=45, join='round'):
    """An open arrowhead (Tabler's: two strokes at 45 degrees) with its tip at `tip`,
    pointing `deg` degrees (font frame, counterclockwise from +x). On a line, the tip is
    mitred (join='miter'), so that it stands clear of the line's edges."""
    a = math.radians(deg); pts = []
    for sg in (1, -1):
        b = a + math.pi - sg * math.radians(half)
        pts.append((tip[0] + L * math.cos(b), tip[1] + L * math.sin(b)))
    return stroke([([(pts[0], tip), (tip, pts[1])], False)], w, join=join)


def short(a, b, d):
    """The point d before b on the line from a to b."""
    L = math.dist(a, b); return (b[0] - (b[0] - a[0]) * d / L, b[1] - (b[1] - a[1]) * d / L)


def polyline(pts, w, closed=False):
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    if closed: segs.append((pts[-1], pts[0]))
    return stroke([(segs, closed)], w)


def smooth_pts(pts):
    """A C1 curve through pts (Catmull-Rom as cubics), as one subpath."""
    n = len(pts); segs = []
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[0]; p1, p2 = pts[i], pts[i + 1]; p3 = pts[i + 2] if i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segs.append((p1, c1, c2, p2))
    return segs


def xform(p, m):
    from fontTools.pens.transformPen import TransformPen
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q


def mv(p, dx, dy=0): return xform(p, (1, 0, 0, 1, dx, dy))


def centred(p, y=CY):
    b = p.bounds; return mv(p, 0, y - (b[1] + b[3]) / 2)


# ---- Tabler Icons (MIT, Paweł Kuna), v3.35.0, outline set -----------------------------
TABLER = {
    'logic-and': ['M22 12h-5', 'M2 9h5', 'M2 15h5', 'M9 5c6 0 8 3.5 8 7s-2 7 -8 7h-2v-14h2z'],
    'logic-buffer': ['M22 12h-5', 'M2 9h5', 'M2 15h5', 'M7 5l10 7l-10 7z'],
    'lambda': ['M6 20l6.5 -9', 'M19 20c-6 0 -6 -16 -12 -16'],
    'circle': ['M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0'],
    'infinity': ['M9.828 9.172a4 4 0 1 0 0 5.656a10 10 0 0 0 2.172 -2.828a10 10 0 0 1 2.172 -2.828'
                 'a4 4 0 1 1 0 5.656a10 10 0 0 1 -2.172 -2.828a10 10 0 0 0 -2.172 -2.828'],
    'ease-in-out': ['M3 20c8 0 10 -16 18 -16'],
    'eye': ['M10 12a2 2 0 1 0 4 0a2 2 0 0 0 -4 0',
            'M21 12c-2.4 4 -5.4 6 -9 6c-3.6 0 -6.6 -2 -9 -6c2.4 -4 5.4 -6 9 -6c3.6 0 6.6 2 9 6'],
    'chart-histogram': ['M3 3v18h18', 'M20 18v3', 'M16 16v5', 'M12 13v8', 'M8 16v5', 'M3 11c6 0 5 -5 9 -5s3 5 9 5'],
    'hierarchy-3': ['M12 5m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0', 'M8 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0',
                    'M12 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0', 'M20 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0',
                    'M4 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0', 'M16 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0',
                    'M5 17l2 -3', 'M9 10l2 -3', 'M13 7l2 3', 'M17 14l2 3', 'M15 14l-2 3', 'M9 14l2 3'],
    'binary-tree-2': ['M14 6a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z', 'M7 14a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z',
                      'M21 14a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z', 'M14 18a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z',
                      'M12 8v8', 'M6.316 12.496l4.368 -4.992', 'M17.684 12.496l-4.366 -4.99'],
    'topology-ring-2': ['M14 6a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z', 'M7 18a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z',
                        'M21 18a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z', 'M7 18h10', 'M18 16l-5 -8', 'M11 8l-5 8'],
    'arrows-right-left': ['M21 7l-18 0', 'M18 10l3 -3l-3 -3', 'M6 20l-3 -3l3 -3', 'M3 17l18 0'],
    'caret-down': ['M6 10l6 6l6 -6h-12'],
    'grid-3x3': ['M3 8h18', 'M3 16h18', 'M8 3v18', 'M16 3v18'],
    'activity': ['M3 12h4l3 8l4 -16l3 8h4'],
}

def T(name, f, w):
    return stroke(sub(TABLER[name], f), w)


# --- neural ------------------------------------------------------------------------------
def neuron(st):
    """FL1. A pyramidal cell as Cajal drew it: an original drawing after his drawings of the
    cortex (not a tracing). The soma is filled and broad; the dendrites leave it at the
    stroke's full width or more and taper to spindly tips at half of it, the apical dendrite
    rising with two oblique branches, the basal ones spreading to both sides and down; the
    axon descends straight, thin and even."""
    w = st.w; parts = []
    tip = max(0.4 * w, 20)
    for pts, k in CAJAL:
        parts.append(stroke_dense(seg_param(smooth_pts(pts)), 0, 1, 0.9 * k * w + 4, w1=tip, fit=NEURON_FIT[0], corner=NEURON_FIT[1]))
    parts.append(polyline([(0, 230), (0, -60)], max(0.5 * w, 24)))          # the axon
    s = 0.3 * w + 70                                                          # the soma: a rounded triangle, filled
    tri = [(-s * 1.25, 300 - s * 0.55), (s * 1.25, 300 - s * 0.55), (0, 300 + s * 1.5)]
    parts.append(_path_of([(tri[i], tri[(i + 1) % 3]) for i in range(3)]))
    parts.append(stroke([([(tri[i], tri[(i + 1) % 3]) for i in range(3)], True)], 0.9 * s))
    return fillet(union(parts), lo=2.0, hi=60.0, d=45.0)     # the junctions, rounded where shallow


def logical_neuron(st):
    """FL2. The McCulloch-Pitts neuron (1943, Fig. 1), drawn on Tabler's logic-buffer: the
    triangular cell body, an excitatory input ending in a bulb, an inhibitory one in a ring,
    each terminal just touching the body, and the axon. Round 3: the inputs are set wider
    apart (at 8 and 16 of the grid) and the ring's stroke grows only as fast as the bulb, so
    the two terminals no longer crowd each other and the body in Black."""
    w = st.w; f = grid()
    parts = [stroke(sub(['M22 12h-5', 'M7 5l10 7l-10 7z', 'M1.5 8.2h3', 'M1.5 15.8h2'], f), w)]
    wr = w if st.g <= 1 else 58 * st.g ** 0.6                                   # the ring's stroke
    r = max(1.25 * UNIT, 0.5 * wr + 26) / UNIT                                   # its counter stays open
    parts.append(circle(f((7 - 1.25, 8.2)), 1.25 * UNIT + 0.1 * w))              # excitatory: a bulb
    parts.append(stroke(sub([f'M{7 - 2 * r - 0.5} 15.8a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0'], f), wr))  # inhibitory: a ring
    return union(parts)


def perceptron(st):
    """FL3. A perceptron: three inputs converging on one unit and its output; Tabler's
    binary-tree-2 turned a quarter clockwise (the root on the right), the output stroke added."""
    w = st.w; f = grid(rot=90)
    p = T('binary-tree-2', f, w)
    o0 = f((12, 4)); o1 = f((12, 0.8))
    return union([p, stroke([([(o0, o1)], False)], w)])


def network(st):
    """A layered network: Tabler's hierarchy-3 turned a quarter counterclockwise, so its
    layers of one, two and three units read left to right."""
    return T('hierarchy-3', grid(rot=-90), st.w)


def sigmoid(st):
    """The logistic curve: Tabler's ease-in-out."""
    return T('ease-in-out', grid(), st.w)


def lissajous(st):
    """The Lissajous representative: 3:2 at its most open phase (U+E944's figure)."""
    return lissajous_fig(3, 2, 1.0)(st)


def and_gate(st):
    """The AND gate: Tabler's logic-and."""
    return T('logic-and', grid(), st.w)


def lambda_roundel(st):
    """λ in a ring: Tabler's circle, and Tabler's lambda at 0.6 of its size inside it."""
    w = st.w
    ring_ = T('circle', grid(), w)
    lam = T('lambda', grid(s=UNIT * 0.6, cx=12.5, cy=12), w)
    return union([ring_, lam])


def galton(st):
    """FL4. The bell over its histogram, as Galton's board piles its beads: five bars on a
    baseline (Tabler's chart-histogram, its vertical axis removed), and the bell seated on
    them: each bar rises to just under the curve (a gap of 0.4 of a stroke), and the curve's
    tails run out level, that same gap above the baseline."""
    w = st.w; f = grid(); base = 20.8; H = 13.4; s = 4.2
    gap = 0.4 * w + 10; need = (w + gap) / UNIT
    cy = lambda x: base - need - H * math.exp(-(x - 12) ** 2 / (2 * s * s))
    xs = [1.8 + 20.4 * k / 24 for k in range(25)]
    parts = [polyline([f((1.6, base)), f((22.4, base))], w),
             stroke([(smooth_pts([f((x, cy(x))) for x in xs]), False)], w)]
    for x in (4.4, 8.2, 12, 15.8, 19.6):
        parts.append(polyline([f((x, base)), f((x, cy(x) + need))], w))
    return union(parts)


def eye(st):
    """The eye: Tabler's eye, the pupil filled."""
    w = st.w; f = grid()
    return union([stroke(sub([TABLER['eye'][1]], f), w), circle(f((12, 12)), 2 * UNIT + w / 2 - 6)])


def necker(st):
    """FL7. The Necker cube (1832): Phosphor's cube-transparent, all twelve edges, its
    256-unit grid centre lines (the regular weight's outline inset by half its stroke).
    Round 3: above Regular the cube's stroke grows more slowly than the other ornaments'
    (to 0.84 of it in Black), so its small faces keep their counters open."""
    s = UNIT * 24 / 256; f = grid(cx=128, cy=128, s=s)
    w = st.w if st.g <= 1 else st.w * (1 - 0.16 * (st.g - 1) / (math.sqrt(163 / 66) - 1))
    hexa = [(40, 40), (160, 40), (216, 96), (216, 216), (96, 216), (40, 160)]
    subs = [([(f(hexa[i]), f(hexa[(i + 1) % 6])) for i in range(6)], True)]
    for a, b in [((160, 40), (160, 160)), ((40, 160), (160, 160)), ((160, 160), (216, 216)),
                 ((96, 96), (216, 96)), ((96, 96), (96, 216)), ((40, 40), (96, 96))]:
        subs.append(([(f(a), f(b))], False))
    return stroke_exact(subs, w)


# --- the history of the sciences ------------------------------------------------------
def venn(st):
    """FL6. Venn's three circles (1880): circles of 6 grid units on an equilateral triangle
    of side 5.2, drawn with Tabler's stroke."""
    w = st.w; f = grid(); r = 6 * UNIT; parts = []
    for ang in (90, 210, 330):
        c = (12 + 3.0 * math.cos(math.radians(ang)), 12.6 - 3.0 * math.sin(math.radians(ang)))
        parts.append(ring(f(c), r, w))
    return union(parts)


# Nightingale's "Diagram of the causes of mortality in the army in the East", April 1854 to
# March 1855 (Notes on Matters Affecting the Health ... of the British Army, 1858): the annual
# death rate per 1000 for each month, zymotic + wounds + other causes, from her table.
NIGHTINGALE = [8.4, 10.8, 7.2, 159.6, 340.8, 372.0, 298.8, 499.2, 721.2, 1173.5, 979.2, 561.7]


def rose(st):
    """FL11. Nightingale's rose: twelve wedges, one per month from April 1854, the area of
    each in proportion to that month's death rate (radius as its square root), filled, round
    a hub, white gaps between them as wide as a third of the stroke; the rose is then scaled
    to stand as tall as the capitals."""
    w = st.w; R = 360; hub = 46 + 0.3 * w; c = (0, CY)
    top = max(NIGHTINGALE); parts = [circle(c, hub)]
    for i, v in enumerate(NIGHTINGALE):
        r = max(hub + 40, R * math.sqrt(v / top))
        a0 = math.radians(90 - i * 30); a1 = math.radians(90 - (i + 1) * 30)   # clockwise from the top
        segs = [(c, (c[0] + r * math.cos(a0), c[1] + r * math.sin(a0)))] + arc_segs(c, r, a0, a1) + \
               [((c[0] + r * math.cos(a1), c[1] + r * math.sin(a1)), c)]
        parts.append(_path_of(segs))
    flower = union(parts)
    gap = max(16, 0.34 * w); cuts = []
    for i in range(12):
        a = math.radians(90 - i * 30); e = (c[0] + 420 * math.cos(a), c[1] + 420 * math.sin(a))
        n = (-math.sin(a) * gap / 2, math.cos(a) * gap / 2)
        cuts.append(_path_of([((c[0] + n[0], c[1] + n[1]), (e[0] + n[0], e[1] + n[1])),
                              ((e[0] + n[0], e[1] + n[1]), (e[0] - n[0], e[1] - n[1])),
                              ((e[0] - n[0], e[1] - n[1]), (c[0] - n[0], c[1] - n[1])),
                              ((c[0] - n[0], c[1] - n[1]), (c[0] + n[0], c[1] + n[1]))]))
    flower = union([diff(flower, union(cuts)), circle(c, hub)])
    b = flower.bounds; k = 690 / (b[3] - b[1])                  # the whole rose, cap height tall
    return xform(flower, (k, 0, 0, k, 0, CY - k * (b[1] + b[3]) / 2))


def feynman(st):
    """FL14. A Feynman vertex: two fermion lines meet, each with Tabler's arrowhead at its
    middle, and a photon leaves as a wave."""
    w = st.w; f = grid()
    V = f((12, 12)); A = f((3, 4.5)); B = f((3, 19.5))
    parts = [polyline([A, V], w), polyline([V, B], w)]
    for P, Q in ((A, V), (V, B)):
        m = ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2); a = math.degrees(math.atan2(Q[1] - P[1], Q[0] - P[0]))
        m = (m[0] + (Q[0] - P[0]) * 0.08, m[1] + (Q[1] - P[1]) * 0.08)
        parts.append(chev(m, a, 70 + 0.4 * w, w, join='miter'))
    # the photon: a sine of a period and a half, its amplitude kept low enough that its
    # crests stay rounder than the stroke (radius of curvature >= 0.8 w)
    P = 10 / 1.5 * UNIT; A = min(1.2 * UNIT, (P / (2 * math.pi)) ** 2 / (0.8 * w))
    pts = [(V[0] + P * k / 4, V[1] + A * math.sin(math.pi * k / 2)) for k in range(7)]   # zeros and crests
    parts.append(stroke([(smooth_pts(pts), False)], w))
    return union(parts)


def glider(st):
    """FL15. The glider (Guy, 1969), as Raymond's hacker emblem sets it: a 3x3 grid after
    Tabler's grid-3x3 (its lines moved to 8.5 and 15.5 and run from 2 to 22 so the nine cells
    are near equal, at 0.7 of the stroke) with five discs in its cells."""
    w = st.w; f = grid()
    parts = [stroke(sub(['M2 8.5h20', 'M2 15.5h20', 'M8.5 2v20', 'M15.5 2v20'], f), 0.7 * w)]
    for col, row in ((1, 0), (2, 1), (0, 2), (1, 2), (2, 2)):
        parts.append(circle(f((5.1 + 6.9 * col, 5.1 + 6.9 * row)), 1.55 * UNIT))
    return union(parts)

def hanoi(st):
    """FL17. The Tower of Hanoi's starting position, all three discs on the first peg (U+E950's
    drawing)."""
    return hanoi_state((0, 0, 0))(st)


def evidence(st):
    """FL21. Evidence to a bound (Ratcliff, 1978), as the diffusion model is plotted: the
    vertical axis, the time axis along the foot, the two bounds dashed, and a walk that
    starts on the axis midway between them, drifts up and ends with a dot on the upper
    bound."""
    w = st.w; f = grid(); parts = []
    parts.append(polyline([f((2.4, 2.6)), f((2.4, 21.2)), f((22.6, 21.2))], w))
    wb = 0.8 * w; a, b = f((5.4, 0))[0], f((22.6, 0))[0]
    gp = 1.6 * UNIT + wb; dash = (b - a - 3 * gp) / 4                # four dashes in every style
    for y in (5.0, 18.2):
        Y = f((0, y))[1]; parts.append(stroke(dashes((a, Y), (b, Y), dash, gp), wb))
    parts.append(polyline([f(p) for p in EVIDENCE_WALK], w))
    parts.append(circle(f(EVIDENCE_WALK[-1]), 0.85 * w + 14))
    return union(parts)


def fwd_bwd(st):
    """FL22. Forward and backward: Tabler's arrows-right-left, the forward pass through
    two units (discs on its upper arrow), the gradient returning below. Round 3: the third
    disc, which ran into the arrowhead, is gone, so the head reads as an arrow."""
    w = st.w; f = grid(); k = 0.3 * w
    parts = [stroke(sub(['M18 10l3 -3l-3 -3', 'M6 20l-3 -3l3 -3'], f), w),
             polyline([f((3, 7)), short(f((3, 7)), f((21, 7)), k)], w),
             polyline([f((21, 17)), short(f((21, 17)), f((3, 17)), k)], w)]
    for x in (7.5, 13.0): parts.append(circle(f((x, 7)), 0.95 * w + 18))
    return union(parts)


def signal_noise(st):
    """FL23. Signal in noise: one trace of low, uneven hills (the noise) with a tall, narrow
    spike in the middle (the signal), over a baseline. The spike's tip is rounded only a
    little, so the trace is drawn by `stroke_dense`."""
    w = st.w; f = grid()
    left = [f(p) for p in SIGNAL]; right = [f((24 - x, y)) for x, y in reversed(SIGNAL)]
    spike = [f((11.35, 9.0)), f((11.8, 4.0)), f((12, 3.0)), f((12.2, 4.0)), f((12.65, 9.0))]
    segs = smooth_pts(left) + smooth_pts([left[-1]] + spike + [right[0]]) + smooth_pts(right)
    return union([stroke_dense(seg_param(segs), 0, 1, w, fit=SIGNAL_FIT[0], corner=SIGNAL_FIT[1]), polyline([f((0.6, 20.6)), f((23.4, 20.6))], w)])


def rrect(x0, y0, x1, y1, r):
    """A filled rectangle with corners rounded to radius r."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    segs = [((x0 + r, y0), (x1 - r, y0))] + arc_segs((x1 - r, y0 + r), r, -math.pi / 2, 0) + \
           [((x1, y0 + r), (x1, y1 - r))] + arc_segs((x1 - r, y1 - r), r, 0, math.pi / 2) + \
           [((x1 - r, y1), (x0 + r, y1))] + arc_segs((x0 + r, y1 - r), r, math.pi / 2, math.pi) + \
           [((x0, y1 - r), (x0, y0 + r))] + arc_segs((x0 + r, y0 + r), r, math.pi, 1.5 * math.pi)
    return _path_of([s for s in segs if math.dist(s[0], s[-1]) > EPS])


def hermite(P, dP, t0, t1, n):
    """The parametric curve P on [t0, t1] as n cubics, each with the curve's own end tangents
    (handles a third of the step along P')."""
    segs = []
    for k in range(n):
        a = t0 + (t1 - t0) * k / n; b = t0 + (t1 - t0) * (k + 1) / n; h = (b - a) / 3
        pa, pb, da, db = P(a), P(b), dP(a), dP(b)
        segs.append((pa, (pa[0] + h * da[0], pa[1] + h * da[1]), (pb[0] - h * db[0], pb[1] - h * db[1]), pb))
    return segs


def dashes(a, b, dash, gap):
    """Centre lines of a dashed line from a to b: dashes of `dash` units (centre line) with
    `gap` units between them (centre to centre of the round ends), centred on the line."""
    L = math.dist(a, b); d = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    n = max(1, int((L + gap) // (dash + gap))); used = n * dash + (n - 1) * gap; s = (L - used) / 2; out = []
    for k in range(n):
        u = s + k * (dash + gap); v = u + dash
        out.append(([((a[0] + d[0] * u, a[1] + d[1] * u), (a[0] + d[0] * v, a[1] + d[1] * v))], False))
    return out


def ellipse_ring(c, rx, ry, w):
    """An elliptical ring: the ellipse with semi-axes rx, ry stroked at w."""
    return stroke(svg_subpaths(f'M{c[0] - rx} {c[1]}a{rx} {ry} 0 1 0 {2 * rx} 0a{rx} {ry} 0 1 0 {-2 * rx} 0z'), w)


CAJAL = [
    ([(0, 390), (6, 530), (-4, 680), (8, 800)], 1.15),                       # the apical dendrite
    ([(4, 580), (-80, 660), (-180, 700)], 0.8),                               # its oblique branches
    ([(2, 470), (90, 560), (190, 610)], 0.8),
    ([(-55, 330), (-190, 380), (-330, 470), (-430, 520)], 1.1),               # basal dendrites
    ([(-210, 390), (-290, 340), (-420, 330)], 0.75),
    ([(-60, 285), (-200, 250), (-350, 190), (-450, 170)], 1.1),
    ([(55, 335), (200, 380), (320, 450), (420, 470)], 1.1),
    ([(235, 398), (285, 330), (425, 300)], 0.75),
    ([(60, 280), (190, 230), (330, 150), (430, 110)], 1.1),
    ([(-60, 245), (-160, 170), (-280, 110), (-380, 90)], 1.0),
    ([(60, 240), (150, 150), (230, 40)], 1.0),
]


def lissajous_fig(a, b, k):
    """A Lissajous figure x = sin(a t + phase), y = sin(b t), the phase k of the way from
    degenerate to most open (see `lissajous_phase`), in a square 620 units on a side (670 for
    five lobes; centre lines), centred on the capitals' middle. Its turns at the edges of the square are tighter
    than half the stroke, so it is drawn by `stroke_dense`."""
    phase = lissajous_phase(a, b, k)
    def f(st):
        A = 310 if max(a, b) <= 4 else 335 if min(a, b) == 3 else 350
        P = lambda t: (A * math.sin(a * t + phase), CY + A * math.sin(b * t))
        return stroke_dense(P, 0, 2 * math.pi, lissajous_w(st, a, b))
    return f


def lissajous_w(st, a, b):
    """The figures' stroke, an oscilloscope's trace: 0.8 of the ornaments' stroke for figures
    of up to three lobes a side; finer for the denser ones (0.62 for four lobes, 0.55 for
    five), whose stroke also grows more slowly above Regular (as the 0.4 and 0.25 power of the
    weight's stem ratio) so that their strands stay apart in Black. All of them get heavier
    with the text."""
    n = max(a, b)
    if n <= 3: return 0.8 * st.w
    k, p = (0.62, 0.4) if n == 4 else (0.55, 0.25) if (a, b) in ((3, 5), (5, 3)) else (0.5, 0.1)
    return k * (st.w if st.g <= 1 else 58 * st.g ** p)


def arrowhead(tip, d, L, hw):
    """A filled arrowhead (a triangle) with its tip at `tip`, pointing along the unit vector d."""
    n = (-d[1], d[0]); b = (tip[0] - d[0] * L, tip[1] - d[1] * L)
    pts = [tip, (b[0] + n[0] * hw, b[1] + n[1] * hw), (b[0] - n[0] * hw, b[1] - n[1] * hw)]
    return _path_of([(pts[i], pts[(i + 1) % 3]) for i in range(3)])


PLAYFAIR_A = [(4.5, 7.8), (8, 9.0), (11.5, 11.6), (15, 14.6), (18, 16.0), (21, 16.4)]   # imports: rising, then flat


PLAYFAIR_B = [(4.5, 17.4), (8, 16.2), (11.5, 13.0), (15, 8.4), (18, 6.0), (21, 4.8)]     # exports: climbing past it


def hanoi_state(pegs):
    """FL17. A position of the Tower of Hanoi (Lucas, 1883) with three discs: pegs[i] is the
    peg (0, 1, 2) of disc i, largest first; on each peg the discs stack largest at the
    bottom, the lowest sitting on the base and each on the one below, a hairline apart. The
    pegs are a little over half the stroke, the base the full stroke; a disc is a bar with
    rounded corners, its thickness growing with the stroke and its width fixed."""
    def f(st):
        w = st.w; g = grid(); parts = []
        base = g((0, 20.8))[1]; top = g((0, 8.2))[1]
        parts.append(polyline([g((1.2, 20.8)), g((22.8, 20.8))], w))
        X = [g((x, 0))[0] for x in (4.2, 12, 19.8)]
        for x in X: parts.append(polyline([(x, base), (x, top)], 0.55 * w))
        t = 0.82 * w + 14; gp = max(11, 0.13 * w); half = (3.7 * UNIT, 2.75 * UNIT, 1.8 * UNIT)
        level = [0, 0, 0]
        for i, p in enumerate(pegs):                      # largest first: the stack grows upward
            y0 = base + w / 2 + gp + level[p] * (t + gp); level[p] += 1
            parts.append(rrect(X[p] - half[i], y0, X[p] + half[i], y0 + t, 0.32 * t))
        return union(parts)
    return f


EVIDENCE_WALK = [(2.4, 11.6), (4.4, 10.0), (6.2, 13.0), (8.4, 9.6), (10.2, 12.0), (12.6, 7.6), (14.4, 10.0), (17.0, 5.0)]


SIGNAL = [(1.0, 15.6), (2.6, 13.8), (4.2, 16.0), (5.8, 13.2), (7.4, 15.4), (8.8, 14.0), (10.4, 16.4)]


def stroke_exact(subs, w):
    """A stroke of straight-line subpaths with round caps and joins, built from simple pieces:
    a rectangle per segment and one disc per distinct vertex, unioned. Skia's union can lose
    or fill counters where several offset curves meet exactly at a joint (the Necker cube
    failed at some strokes); rectangles and de-duplicated discs avoid those coincidences."""
    parts, seen = [], set()
    for segs, closed in subs:
        for s in segs:
            a, b = s[0], s[-1]; L = math.dist(a, b)
            for q in (a, b):
                k = (round(q[0], 3), round(q[1], 3))
                if k not in seen: seen.add(k); parts.append(circle(q, w / 2))
            if L < EPS: continue
            n = (-(b[1] - a[1]) / L * w / 2, (b[0] - a[0]) / L * w / 2)
            parts.append(_path_of([((a[0] + n[0], a[1] + n[1]), (b[0] + n[0], b[1] + n[1])),
                                   ((b[0] + n[0], b[1] + n[1]), (b[0] - n[0], b[1] - n[1])),
                                   ((b[0] - n[0], b[1] - n[1]), (a[0] - n[0], a[1] - n[1])),
                                   ((a[0] - n[0], a[1] - n[1]), (a[0] + n[0], a[1] + n[1]))]))
    return union(parts)


def _poly(pts):
    return _path_of([(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))])


def stroke_dense(P, t0, t1, w, step=7.0, corner=32.0, fit=40.0, w1=None):
    """The stroke of a parametric curve P on [t0, t1] (closed when P(t0) == P(t1)) at width
    w, for curves that turn tighter than half the stroke (where offset curves have cusps):
    the curve is sampled every `step` units, each sample interval made a quadrilateral
    (neighbours sharing their edges; an open curve gets a disc at each end), and the union's outline (a polygon with the right counters) is
    refitted as smooth curves (Catmull-Rom) through points `fit` units apart, kept sharp only
    at its true corners (a turn of more than `corner` degrees over a few units, where strands
    cross). With w1, the width runs
    from w at t0 to w1 at t1 (by length: a tapered stroke)."""
    n = 4096; pts = [P(t0 + (t1 - t0) * k / n) for k in range(n + 1)]
    closed = math.dist(pts[0], pts[-1]) < 1e-6
    S = [pts[0]]
    for q in pts[1:-1] if closed else pts[1:]:
        if math.dist(q, S[-1]) >= step: S.append(q)
    h = w / 2; m = len(S); parts = []
    Lc = [0.0]
    for i in range(1, m): Lc.append(Lc[-1] + math.dist(S[i - 1], S[i]))
    H = [h if w1 is None else (w + (w1 - w) * Lc[i] / Lc[-1]) / 2 for i in range(m)]
    def nrm(i):                                    # the vertex normal: across the chord of its neighbours
        a = S[i - 1] if (closed or i > 0) else S[i]; b = S[(i + 1) % m] if (closed or i + 1 < m) else S[i]
        d = norm((b[0] - a[0], b[1] - a[1])) or (1.0, 0.0); return (-d[1] * H[i], d[0] * H[i])
    N = [nrm(i) for i in range(m)]
    for i in range(m if closed else m - 1):        # quadrilaterals sharing their edges exactly
        j = (i + 1) % m; a, b, na, nb = S[i], S[j], N[i], N[j]
        q = _poly([(a[0] + na[0], a[1] + na[1]), (b[0] + nb[0], b[1] + nb[1]), (b[0] - nb[0], b[1] - nb[1]), (a[0] - na[0], a[1] - na[1])])
        q.simplify(fix_winding=True); parts.append(q)
    if not closed:
        parts += [_poly([(c[0] + r * math.cos(2 * math.pi * k / 48), c[1] + r * math.sin(2 * math.pi * k / 48)) for k in range(48)])
                  for c, r in ((S[0], H[0]), (S[-1], H[-1]))]
    U = union(parts)
    out = pathops.Path(); pen = out.getPen()
    for segs in _contours_of(U):
        V = [s[0] for s in segs]                       # the polygon's vertices
        m = len(V)
        if m < 6: continue
        # true corners: the direction over +-6 units turns by more than `corner`
        def dirn(i, sgn):
            j = i; d = 0
            while d < 6 and abs(j - i) < m // 2: j += sgn; d = math.dist(V[i], V[j % m])
            q = V[j % m]; return (q[0] - V[i][0], q[1] - V[i][1]) if sgn > 0 else (V[i][0] - q[0], V[i][1] - q[1])
        corners = [i for i in range(m) if angle(norm(dirn(i, -1)) or (1, 0), norm(dirn(i, 1)) or (1, 0)) > corner]
        keep = []                                  # one per cluster: corners within 14 units are one corner
        for i in corners:
            if keep and math.dist(V[i], V[keep[-1]]) < 14: continue
            keep.append(i)
        if len(keep) > 1 and math.dist(V[keep[0]], V[keep[-1]]) < 14: keep.pop()
        if not keep:
            # a smooth loop: resample and close with Catmull-Rom
            Ls = [0.0]
            for i in range(1, m + 1): Ls.append(Ls[-1] + math.dist(V[i - 1], V[i % m]))
            k = max(8, round(Ls[-1] / fit)); R = []
            j = 0
            for s in range(k):
                target = Ls[-1] * s / k
                while Ls[j + 1] < target: j += 1
                u = (target - Ls[j]) / max(EPS, Ls[j + 1] - Ls[j]); a, b = V[j], V[(j + 1) % m]
                R.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            Rc = R + R[:3]
            sg = smooth_pts([R[-1]] + Rc)[1:len(R) + 1]
            pen.moveTo(sg[0][0])
            for s in sg: pen.curveTo(s[1], s[2], s[3])
            pen.closePath(); continue
        first = True
        for ci in range(len(keep)):
            i0, i1 = keep[ci], keep[(ci + 1) % len(keep)]
            run = [V[i0]]; j = i0
            while True:
                j = (j + 1) % m; run.append(V[j])
                if j == i1: break
            Ls = [0.0]
            for i in range(1, len(run)): Ls.append(Ls[-1] + math.dist(run[i - 1], run[i]))
            k = max(1, round(Ls[-1] / fit)); R = [run[0]]; j = 0
            for s in range(1, k):
                target = Ls[-1] * s / k
                while Ls[j + 1] < target: j += 1
                u = (target - Ls[j]) / max(EPS, Ls[j + 1] - Ls[j]); a, b = run[j], run[j + 1]
                R.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            R.append(run[-1])
            if first: pen.moveTo(R[0]); first = False
            if Ls[-1] < 2 * fit:                   # a short run: one cubic, its handles a third of it long
                A, B = run[0], run[-1]; d = Ls[-1] / 3
                ta = norm((run[min(len(run) - 1, 2)][0] - A[0], run[min(len(run) - 1, 2)][1] - A[1])) or (1.0, 0.0)
                tb = norm((B[0] - run[max(0, len(run) - 3)][0], B[1] - run[max(0, len(run) - 3)][1])) or (1.0, 0.0)
                if Ls[-1] < 1.2 * math.dist(A, B):
                    pen.curveTo((A[0] + ta[0] * d, A[1] + ta[1] * d), (B[0] - tb[0] * d, B[1] - tb[1] * d), B)
                else:
                    for s in run_curve(R): pen.curveTo(s[1], s[2], s[3])
            else:
                for s in run_curve(R): pen.curveTo(s[1], s[2], s[3])
        pen.closePath()
    out.simplify(fix_winding=False)               # the refit keeps each contour's direction
    return fillet(out, lo=2.0, hi=DENSE_FILLET[0], d=DENSE_FILLET[1]) if DENSE_FILLET else out   # where strands merge at a narrow angle: rounded


def mono_P(x, y0, H, w):
    """A monoline capital P, H tall (centre lines) from y0, its stem at x: the stem, and the
    bowl from the top to just under the middle, all in the stroke w."""
    bw = 0.62 * H; r = 0.27 * H; yt = y0 + H; ym = y0 + 0.44 * H
    segs = [((x, y0), (x, yt)), ((x, yt), (x + bw - r, yt))] + arc_segs((x + bw - r, yt - (yt - ym) / 2), (yt - ym) / 2, math.pi / 2, -math.pi / 2) + \
           [((x + bw - r, ym), (x, ym))]
    return stroke([(segs[:1], False), (segs[1:], False)], w)


def mono_Q(c, rx, ry, w):
    """A monoline capital Q: an oval ring and a tail crossing its lower right."""
    tail = [((c[0] + 0.2 * rx, c[1] - 0.4 * ry), (c[0] + 0.88 * rx, c[1] - 1.0 * ry))]
    return union([ellipse_ring(c, rx, ry, w), stroke([(tail, False)], w)])


DARWIN3 = {
    # limbs as centre lines in the icon grid (y down): the trunk from the root, three limbs
    # and their branches; 'live' tips end in Darwin's cross stroke, the others (extinct) bare
    'limbs': [
        [(5.6, 21.4), (6.0, 18.0), (7.0, 15.0)],                       # the trunk
        [(7.0, 15.0), (4.6, 11.8), (3.2, 8.6)],                         # left limb
        [(3.2, 8.6), (2.2, 6.4), (1.8, 3.8)],
        [(3.2, 8.6), (5.4, 7.2), (6.8, 5.6)],
        [(7.0, 15.0), (10.0, 11.6), (12.2, 8.6)],                       # middle limb
        [(12.2, 8.6), (11.8, 5.6), (12.0, 2.8)],
        [(12.2, 8.6), (15.4, 6.4), (18.0, 4.6)],
        [(7.0, 15.0), (11.4, 15.0), (15.6, 13.4)],                      # right limb
        [(15.6, 13.4), (18.6, 11.4), (21.2, 9.8)],
        [(15.6, 13.4), (18.8, 15.4), (21.6, 17.8)],
        [(4.6, 11.8), (2.8, 12.6), (1.4, 12.6)],                        # an extinct side branch
        [(11.4, 15.0), (12.8, 17.0), (13.2, 18.6)],                     # another
    ],
    'live': [(1.8, 3.8), (6.8, 5.6), (12.0, 2.8), (18.0, 4.6), (21.2, 9.8), (21.6, 17.8)],
}


def lissajous_phase(a, b, k):
    """The phase for x = sin(a t + phase), y = sin(b t) that is k of the way from a degenerate
    figure (one traced back on itself, open: a parabola, an S) to the most open one (k = 1,
    the symmetric figure, e.g. 1:2's figure eight): degenerate phases fall every pi/b,
    at pi/2 - a pi/(2b) + j pi/b."""
    return math.pi / 2 - a * math.pi / (2 * b) + k * math.pi / (2 * b)


def seg_param(segs):
    """A parameter t in [0, 1] over a chain of segments (each an equal share), as a function."""
    n = len(segs)
    def P(t):
        k = min(n - 1, int(t * n)); return pt(segs[k], t * n - k)
    return P


NEURON_FIT = (56, 32)   # the refit's point spacing and corner angle (chosen so every style's outline is clean)


SIGNAL_FIT = (48, 40)   # the refit's point spacing and corner angle (chosen so every style's outline is clean)


def run_curve(R):
    """The Catmull-Rom curve through R, its two end handles a third of the end spacing long
    (Catmull-Rom's own are a sixth, too short to keep their direction on the grid)."""
    sg = [list(x) for x in smooth_pts(R)]
    a, c1 = sg[0][0], sg[0][1]; sg[0][1] = (a[0] + 2 * (c1[0] - a[0]), a[1] + 2 * (c1[1] - a[1]))
    b, c2 = sg[-1][3], sg[-1][2]; sg[-1][2] = (b[0] + 2 * (c2[0] - b[0]), b[1] + 2 * (c2[1] - b[1]))
    return [tuple(x) for x in sg]


DENSE_FILLET = (50.0, 30.0)   # stroke_dense's own rounding of shallow corners: (largest turn, cut-back)




# ---- drafts: below the main set's bar at text size, for Jordan's decision ------------------
# Darwin, Notebook B, p. 36 (1837), the "I think" tree, traced as centre lines from the
# Cambridge University Library page (Wikimedia Commons, Darwin_tree.png, public domain); the
# coordinates are pixels of that scan cropped at (90, 150), y down. Only the main limbs are
# kept (the short side twigs, extinct lines without a cross stroke, are left out) so that the
# tree reads at text size; each branch tip that Darwin closed with a cross stroke (his living
# species) ends in one here.
DARWIN = {
    'trunk': [(147, 382), (150, 352), (170, 311), (166, 197), (159, 137), (155, 74)],
    'branches': [
        [(155, 74), (134, 34)], [(155, 74), (220, 58)],
        [(159, 137), (206, 94), (252, 90)],
        [(159, 137), (81, 159)], [(81, 159), (28, 150)], [(81, 159), (30, 196)],
        [(166, 197), (249, 178)], [(249, 178), (259, 153)], [(249, 178), (293, 197)],
        [(170, 311), (290, 292)], [(290, 292), (315, 252)],
        [(290, 292), (340, 323), (384, 398)],
        [(384, 398), (380, 450)], [(384, 398), (450, 407)],
    ],
    'tips': [(134, 34), (220, 58), (252, 90), (28, 150), (30, 196),
             (259, 153), (293, 197), (380, 450), (450, 407), (315, 252)],
}


def darwin(st):
    """FL5 (draft, round 3). Darwin's "I think" tree (Notebook B, p. 36, 1837), redrawn after
    it (not traced) so that it reads at text size: a trunk from a root ring, three limbs
    branching once or twice, smooth curves in the ornaments' stroke; the six living tips end
    in his cross stroke, and two short side branches stop bare (extinct)."""
    w = st.w; f = grid(); parts = []
    for limb in DARWIN3['limbs']:
        parts.append(stroke([(smooth_pts([f(p) for p in limb]), False)], w))
    h = 0.42 * w + 20                                   # half the cross stroke
    for limb in DARWIN3['limbs']:
        if limb[-1] not in DARWIN3['live']: continue
        a, e = f(limb[-2]), f(limb[-1]); d = norm((e[0] - a[0], e[1] - a[1])); n = (-d[1] * h, d[0] * h)
        parts.append(polyline([(e[0] + n[0], e[1] + n[1]), (e[0] - n[0], e[1] - n[1])], w))
    r = f(DARWIN3['limbs'][0][0]); R = 0.9 * UNIT + 0.2 * w
    parts.append(ring((r[0], r[1] - R - w / 2 + 6), R, w))   # the root's ring, hung from the trunk's foot
    return union(parts)


# The duck-rabbit, Fliegende Blätter, 23 October 1892, "Kaninchen und Ente" (Wikimedia
# Commons, Kaninchen_und_Ente.png, public domain), traced as centre lines: pixels of that scan,
# y down.
DUCKRABBIT = {
    'back': [(62, 352), (150, 302), (320, 345), (470, 395), (548, 414), (615, 372), (720, 350), (850, 356),
             (960, 410), (1040, 500), (1066, 575), (1045, 640), (1008, 690), (948, 745), (885, 792), (858, 850)],
    'upper': [(62, 352), (92, 374), (262, 404), (430, 424), (550, 424)],
    'lower': [(80, 436), (262, 448), (400, 444), (472, 438)],
    'chin': [(80, 436), (104, 490), (136, 526), (300, 560), (472, 602), (482, 650), (474, 722), (500, 842)],
    'eye': (786, 522),
}


def duck_rabbit(st):
    """FL8 (draft). Jastrow's duck-rabbit after its first printing (Fliegende Blätter, 1892),
    traced: the back of the head and the upper ear (the duck's upper bill), the two edges of
    the lower ear (the lower bill), the chin and neck, and the eye. Round 3: the lower ear and
    the start of the chin are set lower, by enough that a gap of half a stroke more than the
    stroke itself divides the two ears (the two halves of the bill) in every weight; the
    rest is round 2's tracing."""
    w = st.w; s = 0.86
    f = lambda p: ((p[0] - 62) * s, CY + (576 - p[1]) * s)
    D = DUCKRABBIT
    d = max(0.0, 1.5 * w - 38) / s                          # the drop, in scan pixels (the traced gap is 38 units)
    lower = [(x, y + d) for x, y in D['lower']]
    chin = [(x, y + d * k) for (x, y), k in zip(D['chin'], (1, 0.8, 0.5, 0.25, 0, 0, 0, 0))]
    parts = []
    for pts in (D['back'], D['upper'], lower, chin):
        parts.append(stroke([(smooth_pts([f(p) for p in pts]), False)], w))
    e = f(D['eye']); parts.append(ring(e, 34 + 0.25 * w, w)); parts.append(circle(e, 14 + 0.12 * w))
    return union(parts)


def peirce(st):
    """FL9 (draft, round 4). Peirce's scroll (existential graphs, c. 1896): an outer cut
    holding P and an inner cut holding Q, read "if P then Q". Round 4 joins round 2's cuts (the
    oval, and the circle set into its right end, touching it as the scroll's one line does)
    to round 3's letters, P and Q drawn in the ornaments' own monoline stroke, so the whole
    glyph has one weight and tracks the text's."""
    w = st.w; parts = []
    parts.append(stroke(svg_subpaths(f'M{-500} {CY}a500 320 0 1 0 1000 0a500 320 0 1 0 -1000 0z'), w))
    R = 240; C = (500 - R - 22, CY)                 # the circle's rim 22 units inside the oval's: they touch in every weight
    parts.append(ring(C, R, w))
    H = 240; parts.append(mono_P((-500 + C[0] - R) / 2 - 0.31 * H, CY - H / 2, H, w))   # centred between the cuts
    parts.append(mono_Q(C, 0.4 * H, H / 2, w))
    return union(parts)


def llull(st):
    """FL10 (draft, round 3). Llull's Figure A (Ars brevis, 1308), simplified: the ring, the
    nine principles B to K as discs on it, and of the 36 chords joining every pair only the
    nine of the star that joins each principle to the two it faces across the circle (the
    {9/4} enneagram), at half the stroke, the ring at 0.7 of it."""
    w = st.w; R = 330; c = (0, CY); parts = [ring(c, R, 0.7 * w)]
    pts = [(c[0] + R * math.sin(2 * math.pi * k / 9), c[1] + R * math.cos(2 * math.pi * k / 9)) for k in range(9)]
    parts.append(stroke_exact([([(pts[i], pts[(i + 4) % 9])], False) for i in range(9)], 0.5 * w))
    for p in pts: parts.append(circle(p, 0.6 * w + 18))
    return union(parts)


def hamilton(st):
    """FL18 (draft). Hamilton's formula as cut into Broom Bridge (16 October 1843),
    i² = j² = k² = ijk = −1, set from Torchlette's own letters, superior two, equals and minus,
    under a rule and over a rule, as a tail-piece."""
    w = st.w; x = 0; parts = []
    seq = 'i\u00b2 = j\u00b2 = k\u00b2 = ijk = \u22121'
    for ch in seq:
        n = 'space' if ch == ' ' else st.cmap[ord(ch)]
        if n != 'space': parts.append(mv(st.src(n), x, 0))
        x += st.width(n) * (0.55 if n == 'space' else 1)
    for y in (-90, 800):
        parts.append(polyline([(0, y), (x, y)], 0.6 * w))
    return union(parts)


def alchemy(kind):
    """FL19 (drafts). The alchemical elements as Unicode's Alchemical Symbols block draws them
    (U+1F701 air, U+1F702 fire, U+1F703 earth, U+1F704 water), a public-domain convention,
    constructed geometrically with no outline copied from any font: an equilateral triangle, apex up for fire and air, down for water and earth, air and
    earth crossed by a bar; drawn here in the ornaments' stroke, mitred."""
    def f(st):
        w = st.w; h = 640; a = h / math.sqrt(3)
        up = kind in ('fire', 'air')
        if up: pts = [(0, CY + h / 2), (a, CY - h / 2), (-a, CY - h / 2)]
        else: pts = [(0, CY - h / 2), (-a, CY + h / 2), (a, CY + h / 2)]
        parts = [stroke([([(pts[i], pts[(i + 1) % 3]) for i in range(3)], True)], w, join='miter')]
        if kind in ('air', 'earth'):
            y = CY + (-1 if up else 1) * h * 0.12
            parts.append(stroke([([((-a * 0.62 - w * 0.2, y), (a * 0.62 + w * 0.2, y))], False)], w, cap='butt'))
        return union(parts)
    return f

# ---- Noto Sans Symbols 2 (SIL OFL 1.1, Copyright 2022 The Noto Project Authors) -------
# NotoSansSymbols2-Regular.ttf from notofonts.github.io (fonts/NotoSansSymbols2/unhinted/ttf),
# 1000 units per em: each outline exactly as the font draws it, as SVG path data in font units
# (y up): code point -> (advance, (xMin, yMin, xMax, yMax), path).
NOTO = {
    0x2766: (784, (51, -138, 733, 686), 'M401 318 391 340 420 397Q427 410 431 421.5Q435 433 439 444Q376 465 327 508L289 542Q207 616 167 616Q105 616 105 556Q105 536 115 524Q125 512 139 512Q150 512 156.5 514.5Q163 517 173 524Q170 496 153.5 480Q137 464 109 464Q81 464 66 485.5Q51 507 51 536Q51 586 83 620Q115 654 173 654Q236 654 343 568Q337 588 337 616Q337 645 357.5 665.5Q378 686 413 686Q455 686 481 655Q507 624 507 576Q507 538 483 478Q497 471 521.5 466.5Q546 462 565 462Q604 462 622.5 478Q641 494 641 516Q641 534 626 544Q611 555 611 578Q611 603 628 619.5Q645 636 671 636Q698 636 715.5 615.5Q733 595 733 566Q733 542 714 509Q695 476 656 451Q616 426 559 426Q506 426 465 436Q448 392 401 318ZM455 492Q460 512 462.5 530Q465 548 465 564Q465 595 449.5 616.5Q434 638 409 638Q386 638 374.5 626Q363 614 363 594Q363 587 364 575.5Q365 564 367 550Q391 529 414 516ZM465 -138Q417 -138 363 -115.5Q309 -93 260 -53.5Q211 -14 177 38Q127 115 127 202Q127 260 144 307Q161 354 193.5 382Q226 410 273 410Q326 410 354 377.5Q382 345 385 274H401Q415 324 451 354Q487 384 539 384Q598 384 631.5 345Q665 306 665 240Q665 205 641.5 166Q618 127 558 88Q497 48 463 20.5Q429 -7 429 -44Q429 -68 449 -85Q469 -102 493 -102Q520 -102 535.5 -87.5Q551 -73 551 -50Q551 -31 533 2Q551 38 581 38Q629 38 629 -14Q629 -63 587 -100.5Q545 -138 465 -138Z'),
    0x2767: (926, (51, -67, 875, 615), 'M419 283 397 273 340 302Q327 309 315.5 313Q304 317 293 321Q272 258 229 209L195 171Q121 89 121 49Q121 -13 181 -13Q201 -13 213 -3Q225 7 225 21Q225 32 223 38.5Q221 45 213 55Q241 52 257 35.5Q273 19 273 -9Q273 -37 251.5 -52Q230 -67 201 -67Q151 -67 117 -35Q83 -3 83 55Q83 118 169 225Q150 219 121 219Q92 219 71.5 239.5Q51 260 51 295Q51 337 82 363Q113 389 161 389Q199 389 259 365Q266 379 270.5 403.5Q275 428 275 447Q275 486 259 504.5Q243 523 221 523Q204 523 193 508Q183 493 159 493Q134 493 117.5 510Q101 527 101 553Q101 580 121.5 597.5Q142 615 171 615Q195 615 228 596Q261 577 286 538Q311 498 311 441Q311 388 301 347Q345 330 419 283ZM245 337Q225 342 207 344.5Q189 347 173 347Q142 347 120.5 331.5Q99 316 99 291Q99 268 111 256.5Q123 245 143 245Q151 245 162 246Q173 247 187 249Q208 273 221 296ZM875 347Q875 299 852.5 245Q830 191 790.5 142Q751 93 699 59Q622 9 535 9Q477 9 430 26Q383 43 355 75.5Q327 108 327 155Q327 208 359.5 236Q392 264 463 267V283Q414 297 383.5 333Q353 369 353 421Q353 480 392 513.5Q431 547 497 547Q532 547 571 523.5Q610 500 649 440Q689 379 716.5 345Q744 311 781 311Q805 311 822 331Q839 351 839 375Q839 402 824.5 417.5Q810 433 787 433Q768 433 735 415Q699 433 699 463Q699 511 751 511Q801 511 838 469Q875 427 875 347Z'),
    0x2619: (926, (51, -67, 875, 615), 'M507 265 529 275 586 246Q599 239 610.5 235Q622 231 633 227Q654 290 697 339L731 377Q805 459 805 499Q805 561 745 561Q725 561 713 551Q701 541 701 527Q701 516 703.5 510Q706 504 713 493Q685 496 669 512.5Q653 529 653 557Q653 585 674.5 600Q696 615 725 615Q775 615 809 583Q843 551 843 493Q843 430 757 323Q777 329 805 329Q834 329 854.5 308.5Q875 288 875 253Q875 211 844 185Q813 159 765 159Q727 159 667 183Q660 169 655.5 144.5Q651 120 651 101Q651 62 667 43.5Q683 25 705 25Q723 25 733 40Q744 55 767 55Q792 55 808.5 38Q825 21 825 -5Q825 -32 804.5 -49.5Q784 -67 755 -67Q731 -67 698 -48Q665 -29 640 10Q615 50 615 107Q615 160 625 201Q581 218 507 265ZM681 211Q701 207 719 204Q737 201 753 201Q784 201 805.5 216.5Q827 232 827 257Q827 280 815 291.5Q803 303 783 303Q776 303 764.5 302Q753 301 739 299Q718 275 705 252ZM51 201Q51 249 73.5 303Q96 357 135.5 406.5Q175 456 227 489Q304 539 391 539Q449 539 496 522Q543 505 571 472.5Q599 440 599 393Q599 341 566.5 312.5Q534 284 463 281V265Q513 252 543 216Q573 180 573 127Q573 68 534 34.5Q495 1 429 1Q394 1 355 24.5Q316 48 277 108Q237 169 209.5 203Q182 237 145 237Q121 237 104 217Q87 197 87 173Q87 146 101.5 130.5Q116 115 139 115Q158 115 191 133Q227 115 227 85Q227 37 175 37Q126 37 88.5 79Q51 121 51 201Z'),
    0x261E: (1220, (37, -24, 1183, 585), 'M628 -24Q573 -24 512 -13.5Q451 -3 393 19.5Q335 42 289 76H216Q162 133 162 283Q162 321 169 358.5Q176 396 188 427Q200 458 215 475Q217 476 227.5 475Q238 474 250.5 473.5Q263 473 271 473Q289 473 301.5 475.5Q314 478 331 488Q348 498 376 520Q423 557 458 571Q493 585 538 585Q641 585 705 559Q738 546 763.5 538Q789 530 802 526Q820 522 834 511Q856 510 877.5 508Q899 506 921 504Q956 500 995.5 495.5Q1035 491 1066 487Q1128 480 1155.5 461Q1183 442 1183 406Q1183 337 1085 337Q1068 337 1036.5 338.5Q1005 340 973 340Q949 340 926 339Q903 338 881 336Q897 313 897 278Q897 233 854 214Q840 208 840 199Q840 191 845 179.5Q850 168 850 154Q850 102 801 85Q794 83 792.5 79.5Q791 76 791 65Q791 20 749.5 -2Q708 -24 628 -24ZM628 10H668Q656 14 639.5 20.5Q623 27 600 39Q570 55 546 74Q522 93 511 109Q508 117 508 129Q508 139 512 147.5Q516 156 521 162Q502 172 486.5 181Q471 190 463 197Q459 202 456 209.5Q453 217 452 227Q439 223 423.5 221Q408 219 391 219Q366 219 346 224V259Q354 257 367.5 256Q381 255 391 255Q412 255 429 257.5Q446 260 459 267Q474 293 504 296Q499 311 499 325Q499 351 515 369.5Q531 388 562 388Q573 388 584.5 385Q596 382 608 377Q612 382 616 388Q620 394 624 401Q590 410 578 422L605 446Q610 441 629 435.5Q648 430 674 425Q700 420 725 416.5Q750 413 765 413Q785 413 801.5 426Q818 439 818 467V477H817Q817 479 809 484Q801 489 793 491Q780 495 753 503.5Q726 512 691 526Q634 549 538 549Q499 549 469.5 537Q440 525 398 491Q369 468 349 456Q329 444 311.5 440.5Q294 437 271 437Q264 437 253 437.5Q242 438 233 439Q218 413 208 370Q198 327 198 283Q198 164 233 112H301Q338 81 390 58Q442 35 503 22.5Q564 10 628 10ZM120 43Q96 43 79.5 66Q63 89 54 125Q45 161 41 201.5Q37 242 37 276Q37 310 41 350.5Q45 391 54.5 427Q64 463 80 486.5Q96 510 120 510H195Q215 510 215 486V484Q209 491 200 491Q179 491 165 470.5Q151 450 143.5 417.5Q136 385 132.5 347.5Q129 310 129 276Q129 242 132.5 204Q136 166 144.5 133.5Q153 101 166.5 80.5Q180 60 200 60Q209 60 215 70V63Q215 55 210.5 49Q206 43 195 43ZM743 337Q748 355 767 364Q786 373 808 373Q822 373 830 372.5Q838 372 845 370Q875 372 909.5 374Q944 376 973 376Q1005 376 1037 374.5Q1069 373 1085 373Q1121 373 1134 381Q1147 389 1147 406Q1147 425 1128.5 434.5Q1110 444 1061 451Q1031 456 992.5 460Q954 464 916 468Q903 470 886.5 471Q870 472 853 473V468Q853 425 827.5 401Q802 377 767 377Q748 377 718 381Q688 385 659 392Q655 385 651 378Q647 371 642 364H643Q656 360 680 351.5Q704 343 743 337ZM778 222Q799 222 835 244Q852 255 856.5 260Q861 265 861 275Q861 293 857 309.5Q853 326 839 337Q834 338 829.5 338Q825 338 821 338Q793 338 782.5 327.5Q772 317 772 297Q723 302 692.5 311.5Q662 321 634 331Q615 337 596 347Q577 357 560 355Q552 354 543 348.5Q534 343 534 329Q534 323 536.5 315Q539 307 540 305Q554 294 583.5 277Q613 260 662 243Q691 233 725 227.5Q759 222 778 222ZM762 111Q785 111 801.5 120Q818 129 818 150Q818 162 815.5 173Q813 184 810 191Q798 186 783 186Q772 186 750 189Q728 192 703.5 197Q679 202 657 209Q623 220 591.5 235Q560 250 536 265Q523 270 514 270Q501 270 493 260Q485 250 485 237Q485 225 492 214Q502 207 524 195Q546 183 572.5 170.5Q599 158 621 149Q665 132 699.5 121.5Q734 111 762 111ZM724 34Q748 34 754.5 48.5Q761 63 761 74Q761 78 760 80H753Q712 80 675.5 94.5Q639 109 611 120Q599 125 584 132Q569 139 554 146Q544 136 542 121Q550 110 568 95.5Q586 81 606 70Q624 60 639.5 52Q655 44 674.5 39Q694 34 724 34Z'),
    0x261C: (1220, (37, -24, 1183, 585), 'M592 -24Q513 -24 471 -2Q429 20 429 65Q429 76 427.5 79.5Q426 83 419 85Q370 102 370 154Q370 168 375 179.5Q380 191 380 199Q380 208 366 214Q323 233 323 278Q323 313 339 336Q317 338 294 339Q271 340 247 340Q216 340 184 338.5Q152 337 135 337Q37 337 37 406Q37 442 65 461Q93 480 154 487Q185 491 225 495.5Q265 500 299 504Q321 506 342.5 508Q364 510 386 511Q400 522 418 526Q432 530 457 538Q482 546 515 559Q579 585 682 585Q727 585 762.5 571Q798 557 844 520Q873 498 889.5 488Q906 478 919 475.5Q932 473 949 473Q957 473 969.5 473.5Q982 474 993 475Q1004 476 1005 475Q1021 458 1032.5 427Q1044 396 1051 358.5Q1058 321 1058 283Q1058 133 1004 76H931Q886 42 827.5 19.5Q769 -3 708 -13.5Q647 -24 592 -24ZM552 10H592Q656 10 717 22.5Q778 35 830.5 58Q883 81 919 112H987Q1022 164 1022 283Q1022 327 1012 370Q1002 413 987 439Q978 438 967.5 437.5Q957 437 949 437Q927 437 909 440.5Q891 444 871.5 456Q852 468 822 491Q780 525 750.5 537Q721 549 682 549Q586 549 529 526Q495 512 468 503.5Q441 495 427 491Q419 489 411 484Q403 479 403 477H402V467Q402 439 418.5 426Q435 413 455 413Q470 413 495 416.5Q520 420 546 425Q572 430 591.5 435.5Q611 441 615 446L642 422Q630 410 596 401Q600 394 604 388Q608 382 612 377Q624 382 635.5 385Q647 388 658 388Q689 388 705 369.5Q721 351 721 325Q721 311 716 296Q746 293 761 267Q775 260 791.5 257.5Q808 255 829 255Q839 255 852.5 256Q866 257 874 259V224Q854 219 829 219Q812 219 797 221Q782 223 768 227Q767 217 764 209.5Q761 202 757 197Q749 190 733.5 181Q718 172 699 162Q704 156 708 147.5Q712 139 712 129Q712 117 709 109Q698 93 674 74Q650 55 620 39Q597 27 580.5 20.5Q564 14 552 10ZM1025 43Q1014 43 1009.5 49Q1005 55 1005 63V70Q1011 60 1020 60Q1040 60 1053.5 80.5Q1067 101 1075.5 133.5Q1084 166 1087.5 204Q1091 242 1091 276Q1091 310 1087.5 347.5Q1084 385 1076.5 417.5Q1069 450 1055 470.5Q1041 491 1020 491Q1011 491 1005 484V486Q1005 510 1025 510H1100Q1124 510 1140 486.5Q1156 463 1165.5 427Q1175 391 1179 350.5Q1183 310 1183 276Q1183 242 1179 201.5Q1175 161 1166 125Q1157 89 1140.5 66Q1124 43 1100 43ZM477 337Q516 343 540 351.5Q564 360 577 364H578Q574 371 569.5 378Q565 385 561 392Q532 385 502.5 381Q473 377 453 377Q419 377 393 401Q367 425 367 468V473Q350 472 334 471Q318 470 304 468Q267 464 228 460Q189 456 159 451Q110 444 91.5 434.5Q73 425 73 406Q73 389 86 381Q99 373 135 373Q152 373 183.5 374.5Q215 376 247 376Q276 376 310.5 374Q345 372 375 370Q382 372 390.5 372.5Q399 373 412 373Q434 373 453 364Q472 355 477 337ZM442 222Q462 222 495.5 227.5Q529 233 558 243Q607 260 636.5 277Q666 294 680 305Q681 307 683.5 315Q686 323 686 329Q686 343 677 348.5Q668 354 660 355Q644 357 624.5 347Q605 337 586 331Q558 321 527.5 311.5Q497 302 448 297Q448 317 438 327.5Q428 338 399 338Q395 338 390.5 338Q386 338 381 337Q367 326 363 309.5Q359 293 359 275Q359 265 364 260Q369 255 385 244Q421 222 442 222ZM458 111Q487 111 521 121.5Q555 132 599 149Q621 158 647.5 170.5Q674 183 696.5 195Q719 207 728 214Q735 225 735 237Q735 250 727.5 260Q720 270 706 270Q697 270 684 265Q660 250 629 235Q598 220 563 209Q542 202 517 197Q492 192 470.5 189Q449 186 437 186Q423 186 410 191Q407 184 404.5 173Q402 162 402 150Q402 129 418.5 120Q435 111 458 111ZM496 34Q527 34 546 39Q565 44 580.5 52Q596 60 614 70Q634 81 652 95.5Q670 110 678 121Q676 136 666 146Q651 139 636 132Q621 125 609 120Q581 109 544.5 94.5Q508 80 467 80H460Q459 78 459 74Q459 63 465.5 48.5Q472 34 496 34Z'),
    0x1F658: (981, (51, 43, 930, 648), 'M581 43Q543 43 502 66Q461 89 420.5 125.5Q380 162 340 204Q300 246 264 284Q231 270 197 260.5Q163 251 125 251Q89 251 70 268.5Q51 286 51 312Q51 344 71 372.5Q91 401 121.5 419Q152 437 183 437Q207 437 239.5 410Q272 383 310 343Q319 347 329 353Q352 376 383.5 412.5Q415 449 452 490Q489 531 529 567Q569 603 609.5 625.5Q650 648 687 648Q731 648 752.5 628Q774 608 774 579Q774 558 763.5 538.5Q753 519 740 506.5Q727 494 721 494Q715 494 715 498Q715 500 719 505Q723 510 723 523Q723 546 704.5 566.5Q686 587 648 587Q611 587 571 563Q531 539 494 503.5Q457 468 427.5 434Q398 400 381 379Q439 408 508 432.5Q577 457 669 457Q755 457 813 428.5Q871 400 900.5 356.5Q930 313 930 268Q930 234 918.5 207Q907 180 891.5 161Q876 142 862.5 132Q849 122 844 122Q838 122 838 127Q838 131 845 139Q852 147 858.5 162.5Q865 178 865 203Q865 255 835 297.5Q805 340 748.5 365.5Q692 391 614 391Q523 391 457 367.5Q391 344 334 317Q368 280 405 241.5Q442 203 479.5 170Q517 137 554.5 117Q592 97 627 97Q655 97 664.5 114Q674 131 674 147Q674 170 660.5 189.5Q647 209 626 221Q605 233 582 233Q573 233 568.5 231.5Q564 230 560 230Q558 230 558 232Q558 237 568.5 249.5Q579 262 586 266Q595 272 607.5 277.5Q620 283 636 283Q665 283 693 260.5Q721 238 721 193Q721 152 699 117.5Q677 83 644.5 63Q612 43 581 43ZM94 351Q94 331 112.5 316.5Q131 302 162 302Q181 302 199.5 305Q218 308 236 313Q204 344 177.5 364Q151 384 131 384Q116 384 105 373Q94 362 94 351Z'),
    0x1F65A: (981, (51, 43, 930, 648), 'M401 43Q370 43 337.5 63Q305 83 283 117.5Q261 152 261 193Q261 238 288.5 260.5Q316 283 345 283Q362 283 374.5 277.5Q387 272 395 266Q402 261 412.5 249Q423 237 423 232Q423 230 421 230Q418 230 413.5 231.5Q409 233 399 233Q376 233 355 221Q334 209 320.5 189.5Q307 170 307 147Q307 131 317 114Q327 97 355 97Q390 97 427.5 117Q465 137 502.5 170Q540 203 576.5 241.5Q613 280 647 317Q591 344 525 367.5Q459 391 368 391Q290 391 233.5 365.5Q177 340 146.5 297.5Q116 255 116 203Q116 178 123 162.5Q130 147 136.5 139Q143 131 143 127Q143 122 137 122Q133 122 119.5 132Q106 142 90 161Q74 180 62.5 207Q51 234 51 268Q51 313 80.5 356.5Q110 400 168.5 428.5Q227 457 313 457Q405 457 474 432.5Q543 408 601 379Q584 399 554.5 433.5Q525 468 488 503.5Q451 539 411 563Q371 587 334 587Q296 587 277 566.5Q258 546 258 523Q258 510 262 505Q266 500 266 498Q266 494 260 494Q254 494 241.5 506.5Q229 519 218.5 538.5Q208 558 208 579Q208 608 229.5 628Q251 648 295 648Q332 648 372.5 625Q413 602 453 566Q493 530 530 489.5Q567 449 598.5 412.5Q630 376 652 353Q663 347 672 343Q710 383 742.5 410Q775 437 799 437Q830 437 860 419Q890 401 910 372.5Q930 344 930 312Q930 286 911.5 268.5Q893 251 856 251Q818 251 784 260.5Q750 270 717 284Q681 246 641.5 204Q602 162 561 125.5Q520 89 479.5 66Q439 43 401 43ZM850 384Q830 384 803.5 364Q777 344 745 313Q763 308 781.5 305Q800 302 819 302Q851 302 869.5 316.5Q888 331 888 351Q888 362 876.5 373Q865 384 850 384Z'),
    0x1F668: (1020, (51, -102, 969, 815), 'M51 -102V-83Q159 -83 252 -35Q345 13 409 96Q472 179 490 282Q482 281 470 280Q458 279 444 277Q424 185 367.5 113.5Q311 42 228 1Q147 -39 51 -39V-20H52Q68 77 122 157.5Q176 238 255 290Q295 316 338.5 333Q382 350 429 358V362Q320 382 235 448Q150 514 100 609Q51 704 51 815H69Q69 711 115 619Q161 527 243 464Q327 400 428 381Q428 392 426.5 403Q425 414 423 427Q336 446 265 502.5Q194 559 154 641Q114 722 114 815H133Q228 797 308 742.5Q388 688 439 607Q490 526 505 431H511Q529 539 594.5 627Q660 715 759 765Q857 815 969 815V796Q861 796 766.5 748.5Q672 701 610 618Q546 533 530 431Q545 432 556.5 433.5Q568 435 575 436Q595 528 653 600Q711 672 793 712Q874 752 969 752V733H968Q951 636 898 556Q845 476 765 423Q725 397 681 380Q637 363 590 355V352Q699 332 786 267Q873 202 920 105Q968 8 968 -102H950Q950 3 904 94.5Q858 186 776 249Q692 313 591 332Q591 322 592.5 310.5Q594 299 596 286Q683 268 754 211Q825 154 865 72Q905 -9 905 -102H886Q790 -84 711.5 -29Q633 26 581 106Q529 186 514 282H509Q491 174 426 86Q361 -2 262 -52Q162 -102 51 -102ZM447 360Q454 361 465 362Q476 363 491 364Q491 469 445 560.5Q399 652 317 713Q233 775 133 796Q134 772 139 749Q228 728 298.5 671.5Q369 615 408 534Q447 453 447 361ZM510 367H514Q619 367 712.5 415Q806 463 869 547Q931 630 949 732Q939 732 927.5 730.5Q916 729 903 727Q883 635 826.5 563.5Q770 492 689 452Q608 412 514 412H507Q510 390 510 367ZM419 448Q403 517 364 574Q325 631 268.5 671.5Q212 712 143 728Q159 660 197.5 603Q236 546 293 506Q350 466 419 448ZM594 440Q666 456 725.5 496Q785 536 826 594.5Q867 653 883 723Q812 707 752.5 667Q693 627 652 569Q611 511 594 440ZM885 -82Q885 -71 883.5 -59.5Q882 -48 880 -35Q792 -14 722.5 43Q653 100 612 180Q572 259 572 352V353Q565 352 554 351Q543 350 528 349Q528 244 574.5 153Q621 62 702 0Q785 -63 885 -82ZM71 -19Q79 -19 90 -18Q101 -17 116 -15Q136 77 192.5 149Q249 221 331 261Q412 301 506 301H512Q509 324 509 346H506Q400 346 306.5 298Q213 250 151 167Q87 82 71 -19ZM136 -11Q208 5 267 45.5Q326 86 367 144.5Q408 203 424 273Q354 257 294.5 216.5Q235 176 194 117.5Q153 59 136 -11ZM876 -14Q860 54 821 111Q782 168 725.5 208Q669 248 600 265Q616 197 655 140Q694 83 751 43.5Q808 4 876 -14Z'),
}


def noto(cp):
    """A Noto Sans Symbols 2 outline as a Path, its shallow corners (tangents turning by 3 to
    35 degrees, which read as kinks when scaled and rounded) made smooth first by `polish`
    on the unrounded quadratic outline."""
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    tt = TTGlyphPen(None); parse_path(NOTO[cp][2], tt)
    g = tt.glyph(dropImpliedOnCurves=False)
    for _ in range(12):
        polish(g, kink=(3.0, 35.0), grid=False)
    p = pathops.Path(); g.draw(p.getPen(), None); return p


def hedera(cp):
    """❦ ❧ ☙ (U+2766, U+2767, U+2619): Noto Sans Symbols 2's floral hearts, at 0.86 of their
    size, centred on the capitals."""
    def f(st):
        return centred(xform(noto(cp), (0.86, 0, 0, 0.86, 0, 0)))
    return f


def manicule(cp):
    """☞ ☜ (U+261E, U+261C): Noto Sans Symbols 2's white right pointing index at 0.8 of its
    size, centred on the capitals; ☜ is ☞ mirrored (Noto draws them as mirror images, and the
    mirror keeps ☞'s clean rounding)."""
    def f(st):
        p = centred(xform(noto(0x261E), (0.8, 0, 0, 0.8, 0, 0)))
        if cp == 0x261C: p = xform(p, (-1, 0, 0, 1, 0, 0)); p.simplify(fix_winding=True)
        return p
    return f


def vine(cp):
    """Flankers: Noto Sans Symbols 2's vine leaves (U+1F658 north west, U+1F65A north east
    pointing) at 0.72 of their size, centred on the x-height."""
    def f(st):
        return centred(xform(noto(cp), (0.72, 0, 0, 0.72, 0, 0)), 260)
    return f


def quilt(st):
    """A border unit: Noto Sans Symbols 2's hollow quilt square (U+1F668), which tiles edge
    to edge; set without sidebearings, a line of them is a rule and a column a side."""
    return centred(noto(0x1F668))


def asterism(st):
    """⁂ (U+2042): three of Torchlette's own asterisks, at 0.78 of their size, in a triangle."""
    a = st.src('asterisk'); b = a.bounds; k = 0.78
    a = xform(a, (k, 0, 0, k, -k * (b[0] + b[2]) / 2, -k * (b[1] + b[3]) / 2))
    aw, ah = k * (b[2] - b[0]), k * (b[3] - b[1])
    parts = [mv(a, 0, 0.5 * ah * 0.92), mv(a, -0.56 * aw, -0.5 * ah * 0.92), mv(a, 0.56 * aw, -0.5 * ah * 0.92)]
    return centred(union(parts), 400)


def refmark(st):
    """※ (U+203B): Torchlette's own × at 1.25 of its size, a dot (the period's) in each of
    its four openings."""
    x = st.src('multiply'); b = x.bounds; k = 1.25
    x = xform(x, (k, 0, 0, k, -k * (b[0] + b[2]) / 2, -k * (b[1] + b[3]) / 2))
    r = (st.src('period').bounds[2] - st.src('period').bounds[0]) / 2 * 0.92
    R = k * (b[2] - b[0]) * 0.47
    parts = [x] + [circle((R * math.cos(math.radians(a)), R * math.sin(math.radians(a))), r) for a in (0, 90, 180, 270)]
    return centred(union(parts))


def swelled(L):
    """A swelled rule L units long: thickest (2.2 strokes) at its middle, thinning to a
    third of a stroke at its square-cut ends, on the minus sign's centre line."""
    def f(st):
        w = st.w; tmax, tmin = 2.2 * w, max(16, 0.34 * w)
        c = 0
        n = 24; top = []
        for k in range(n + 1):
            x = L * k / n; u = 2 * x / L - 1
            t = tmin + (tmax - tmin) * (1 - u * u) ** 1.6
            top.append((x, c + t / 2))
        bot = [(x, c - (y - c)) for x, y in reversed(top)]
        segs = smooth_pts(top) + [(top[-1], bot[0])] + smooth_pts(bot) + [(bot[-1], top[0])]
        p = _path_of(segs)
        m = st.src('minus').bounds if st.src else (0, 250, 0, 300)
        return mv(p, 0, (m[1] + m[3]) / 2)
    return f


# ---- round 4: options for Jordan to pick from ---------------------------------------------
# Bayes nets (R-bay), drawn in font units (y up, centred on CY), not on an icon grid: the
# nodes are much bigger than round 3's (a node's outer radius is given at Regular and grows by
# half the stroke's growth, so its counter stays open in Black), and every edge is a short
# shaft and a bold filled head whose tip stops short of the child.
def bn_node(c, R, filled, w):
    """A node of outer radius R at Regular: a ring in the stroke, or (observed) a disc."""
    o = R + (w - 58) / 2
    return circle(c, o) if filled else ring(c, o - w / 2, w)


def bn_edge(P, RP, Q, RQ, w, head=1.0, shaft=True):
    """An edge from the node at P to the node at Q (outer radii at Regular RP, RQ): a shaft in
    the stroke from P's ring and a filled head (length 0.5 w + 130, half as wide as it is long,
    times `head`) whose tip stops 0.25 w + 28 short of Q."""
    oP = RP + (w - 58) / 2; oQ = RQ + (w - 58) / 2
    D = math.dist(P, Q); d = ((Q[0] - P[0]) / D, (Q[1] - P[1]) / D)
    L = head * (0.5 * w + 130); hw = 0.5 * L; gap = 0.25 * w + 28
    tip = (Q[0] - d[0] * (oQ + gap), Q[1] - d[1] * (oQ + gap))
    s0 = (P[0] + d[0] * (oP - w / 2), P[1] + d[1] * (oP - w / 2)); e0 = (tip[0] - d[0] * (L - 4), tip[1] - d[1] * (L - 4))
    if not shaft:                                   # the head alone, midway between the rims
        m = ((oP - oQ) / 2 + D / 2 + L / 2) ; tip = (P[0] + d[0] * m, P[1] + d[1] * m)
        return arrowhead(tip, d, L, hw)
    parts = [arrowhead(tip, d, L, hw)]
    if (e0[0] - s0[0]) * d[0] + (e0[1] - s0[1]) * d[1] > 0: parts.append(polyline([s0, e0], w))
    return union(parts)


def bn(nodes, edges, head=1.0, extra=None, shafts=True):
    """A Bayes net: nodes {key: ((x, y), R, observed)}, edges [(parent, child)]; without
    shafts, each edge is its head alone, centred between the two nodes."""
    def f(st):
        w = st.w; parts = [bn_node(c, R, o, w) for c, R, o in nodes.values()]
        for a, b in edges:
            (P, RP, _), (Q, RQ, _) = nodes[a], nodes[b]
            parts.append(bn_edge(P, RP, Q, RQ, w, head, shafts))
        if extra: parts.append(extra(st))
        return union(parts)
    return f


def mono_N(x, y0, H, w):
    """A monoline capital N, H tall (centre lines), 0.7 H wide, from (x, y0)."""
    b = 0.7 * H
    return stroke([([((x, y0), (x, y0 + H)), ((x, y0 + H), (x + b, y0)), ((x + b, y0), (x + b, y0 + H))], False)], w)


def plate(x0, y0, x1, y1):
    """Plate notation's box: a rounded rectangle at 0.7 of the stroke with a monoline N (the
    repeat count) in its lower right corner."""
    def f(st):
        w = st.w; k = 0.7 * w; r = 70
        box = diff(rrect(x0 - k / 2, y0 - k / 2, x1 + k / 2, y1 + k / 2, r + k / 2), rrect(x0 + k / 2, y0 + k / 2, x1 - k / 2, y1 - k / 2, max(4, r - k / 2)))
        H = 150; return union([box, mono_N(x1 - 80 - 0.7 * H, y0 + 85, H, 0.62 * w)])
    return f


BAYES4 = {
    # (nodes {key: (centre, outer radius at Regular, observed)}, edges, head scale, extra, shafts);
    # the nodes fill the ornaments' height (y 28 to 676 at Regular)
    'chain2': ({'A': ((0, CY), 235, False), 'B': ((800, CY), 235, True)}, [('A', 'B')], 1.15, None, True),
    'chain3': ({'A': ((0, CY), 170, False), 'B': ((640, CY), 170, False), 'C': ((1280, CY), 170, False)},
               [('A', 'B'), ('B', 'C')], 1.1, None, True),
    'fork': ({'A': ((0, 526), 150, False), 'B': ((-560, 178), 150, True), 'C': ((560, 178), 150, True)},
             [('A', 'B'), ('A', 'C')], 1.25, None, True),
    'collider': ({'A': ((-560, 526), 150, False), 'B': ((560, 526), 150, False), 'C': ((0, 178), 150, True)},
                 [('A', 'C'), ('B', 'C')], 1.25, None, True),
    'diamond': ({'C': ((0, 536), 140, False), 'S': ((-560, CY), 140, False), 'R': ((560, CY), 140, False), 'W': ((0, 168), 140, True)},
                [('C', 'S'), ('C', 'R'), ('S', 'W'), ('R', 'W')], 0.95, None, True),
    'plate': ({'T': ((0, CY), 150, False), 'X': ((740, 380), 200, True)}, [('T', 'X')], 1.0, plate(250, 40, 1190, 664), True),
    'heads': ({'A': ((-560, 526), 150, False), 'B': ((560, 526), 150, False), 'C': ((0, 178), 150, True)},
              [('A', 'C'), ('B', 'C')], 1.6, None, False),
    'triangle': ({'A': ((0, 536), 140, False), 'B': ((-540, 168), 140, False), 'C': ((540, 168), 140, True)},
                 [('A', 'B'), ('A', 'C'), ('B', 'C')], 1.25, None, True),
}


# Playfair (FL12), round 4: between round 2's single line and round 3's full chart: the two
# series crossing over plain L-shaped axes (no ticks), and the balance between them either
# solid (inset from the series by a white gap, so the lines stay lines) or a few bold hatches.
def _curve_y(segs, X):
    """The y of a left-to-right curve (cubic segments) at x = X, or None outside it."""
    for s in segs:
        if s[0][0] <= X <= s[-1][0]:
            lo, hi = 0.0, 1.0
            for _ in range(40):
                m = (lo + hi) / 2
                if pt(s, m)[0] < X: lo = m
                else: hi = m
            return pt(s, lo)[1]
    return None


def playfair4(kind):
    """kind: 'fill' (both lobes solid), 'lobe' (only the right lobe, after the crossing,
    solid) or 'hatch' (three bold hatches in each lobe, at half the stroke, 2.1 grid units apart)."""
    def f(st):
        w = st.w; g = grid(); parts = [polyline([g((2.2, 3)), g((2.2, 20.6)), g((22.6, 20.6))], w)]
        A = smooth_pts([g(p) for p in PLAYFAIR_A]); B = smooth_pts([g(p) for p in PLAYFAIR_B])
        parts.append(stroke([(A, False), (B, False)], w))
        x0, x1 = A[0][0][0], A[-1][-1][0]
        cross = x0; sg = _curve_y(A, x0) > _curve_y(B, x0)
        while (_curve_y(A, cross) > _curve_y(B, cross)) == sg and cross < x1: cross += 1   # where they cross
        if kind == 'hatch':
            def ends(X, ww):                          # a hatch's ends, clear of both series by the same
                out = []                              # perpendicular distance (the series slant)
                for C in (A, B):
                    y = _curve_y(C, X); sl = (_curve_y(C, X + 3) - _curve_y(C, X - 3)) / 6
                    out.append((y, (ww / 2 + 0.25 * ww + 14) * math.sqrt(1 + sl * sl)))
                (y1, c1), (y2, c2) = sorted(out)
                return y1 + c1, y2 - c2
            wb = 58 * math.sqrt(163 / 66)             # Black's stroke: a hatch is kept only if it is long there
            for gx in (4.9, 7.0, 9.1, 15.3, 17.4, 19.5):
                X = g((gx, 0))[0]; lo, hi = ends(X, wb)
                if hi - lo < 70: continue
                lo, hi = ends(X, w); parts.append(polyline([(X, lo), (X, hi)], 0.5 * w))
            return union(parts)
        c = w / 2 + 0.22 * w + 16                     # the white gap between a series and the fill
        lobes = [(x0 + 4, cross - 2), (cross + 2, x1 - 4)] if kind == 'fill' else [(cross + 2, x1 - 4)]
        for a, b in lobes:
            n = 24; top, bot = [], []
            for i in range(n + 1):
                X = a + (b - a) * i / n; ya, yb = _curve_y(A, X), _curve_y(B, X)
                lo, hi = min(ya, yb) + c, max(ya, yb) - c
                if hi - lo > 6: top.append((X, hi)); bot.append((X, lo))
            parts.append(_poly(bot + top[::-1]))
        return union(parts)
    return f


# The Turing tape (FL16), round 4: wider, so the cells and the 1 0 1 in them read at text
# size: three whole cells and a stub of tape running off each end, the digits 0.4 of the cap
# height in the ornaments' stroke, the cell walls at half of it (so they do not read as 1s), the head (a filled triangle, after Tabler's
# caret-down) above the middle cell. `pitch` is the cell's width (centre lines).
# Round 5 (Jordan: "make the numbers smaller and squatter so that they fill up less of their
# box"): `digits` = (H, zero, flag, stem), the digits' height (centre lines), the 0's half-width,
# the 1's flag reach and its stem's offset from the cell's centre, the last three in units of H.
# Round 4's (286, 0.29, 0.3, 0.08) stays at U+E97B-E97C; TAPE5 is the redrawn digits at U+E911.
TAPE4_DIGITS = (286, 0.29, 0.3, 0.08)
TAPE5_DIGITS = (190, 0.39, 0.37, 0.09)


def tape4(pitch, digits=TAPE4_DIGITS):
    def f(st):
        w = st.w; parts = []
        yb, yt = 40, 486; stub = 0.42 * pitch; L = -1.5 * pitch - stub; R = 1.5 * pitch + stub
        parts.append(polyline([(L, yt), (R, yt)], w)); parts.append(polyline([(L, yb), (R, yb)], w))
        for k in range(4):
            x = (k - 1.5) * pitch; parts.append(polyline([(x, yb), (x, yt)], 0.5 * w))   # thin, so a wall is not read as a 1
        wd = w if st.g <= 1 else 58 * st.g ** 0.6                  # the digits' stroke, twice the walls'
        H, rz, rf, rs = digits; y0 = (yb + yt) / 2 - H / 2
        for k, d in enumerate((1, 0, 1)):
            x = (k - 1) * pitch
            if d:
                parts.append(stroke([([((x - rf * H + rs * H, y0 + 0.74 * H), (x + rs * H, y0 + H)), ((x + rs * H, y0 + H), (x + rs * H, y0))], False)], wd))
            else:
                parts.append(ellipse_ring((x, y0 + H / 2), rz * H, H / 2, wd))
        tip = yt + w / 2 + 0.3 * w + 34; hh = 150; hb = 128            # the head: tip, height, half-base
        tri = [(0, tip), (hb, tip + hh), (-hb, tip + hh)]
        parts.append(_poly(tri)); parts.append(polyline(tri, 0.5 * w, closed=True))
        return mv(union(parts), 0, CY - (yb + tip + hh) / 2 - 0)
    return f


# ---- the set ------------------------------------------------------------------------------
# (code point, glyph key, design, sidebearing). The ornaments are in the Private Use Area
# from U+E900 (fleurons) and U+E920 (printers' pieces); the printers' marks that Unicode
# encodes keep their code points. A sidebearing of None sets the glyph flush (no sidebearings).
SIDE = 70
# Round 5: Jordan's round 4 picks. U+E909 is the plate (also at U+E975), U+E90E the bold hatches
# (also at U+E97A), and U+E911 the 1.5 em tape (U+E97B's pitch) with round 5's smaller, squatter
# digits (TAPE5_DIGITS), which no option holds. The other options are superseded.
MAIN4 = {'bayes': 'plate', 'playfair': 'hatch', 'tape': 340}
ORNAMENTS = [
    (0xE900, 'neuron', neuron, SIDE),
    (0xE901, 'logicalneuron', logical_neuron, SIDE),
    (0xE902, 'perceptron', perceptron, SIDE),
    (0xE903, 'network', network, SIDE),
    (0xE904, 'sigmoid', sigmoid, SIDE),
    (0xE905, 'lissajous', lissajous, SIDE),
    (0xE906, 'andgate', and_gate, SIDE),
    (0xE907, 'lambdaroundel', lambda_roundel, SIDE),
    (0xE908, 'galton', galton, SIDE),
    (0xE909, 'bayesnet', lambda st: bn(*BAYES4[MAIN4['bayes']][:2], head=BAYES4[MAIN4['bayes']][2], extra=BAYES4[MAIN4['bayes']][3], shafts=BAYES4[MAIN4['bayes']][4])(st), SIDE),
    (0xE90A, 'eye', eye, SIDE),
    (0xE90B, 'necker', necker, SIDE),
    (0xE90C, 'venn', venn, SIDE),
    (0xE90D, 'nightingale', rose, SIDE),
    (0xE90E, 'playfair', lambda st: playfair4(MAIN4['playfair'])(st), SIDE),
    (0xE90F, 'feynman', feynman, SIDE),
    (0xE910, 'glider', glider, SIDE),
    (0xE911, 'turingtape', lambda st: tape4(MAIN4['tape'], TAPE5_DIGITS)(st), SIDE),
    (0xE912, 'hanoi', hanoi, SIDE),
    (0xE913, 'evidence', evidence, SIDE),
    (0xE914, 'forwardbackward', fwd_bwd, SIDE),
    (0xE915, 'signalnoise', signal_noise, SIDE),
    (0xE920, 'vineleft', vine(0x1F658), SIDE),
    (0xE921, 'vineright', vine(0x1F65A), SIDE),
    (0xE922, 'quilt', quilt, None),
    (0xE923, 'swelled1', swelled(1000), None),
    (0xE924, 'swelled2', swelled(2000), None),
    (0xE925, 'swelled3', swelled(3000), None),
]
DRAFTS = [
    (0xE930, 'darwintree', darwin, SIDE),
    (0xE931, 'duckrabbit', duck_rabbit, SIDE),
    (0xE932, 'peirce', peirce, SIDE),
    (0xE933, 'llull', llull, SIDE),
    (0xE934, 'hamilton', hamilton, SIDE),
    (0xE935, 'air', alchemy('air'), SIDE),
    (0xE936, 'fire', alchemy('fire'), SIDE),
    (0xE937, 'earth', alchemy('earth'), SIDE),
    (0xE938, 'water', alchemy('water'), SIDE),
]
# The families (round 3): every member its own glyph, after the drafts and out of ornm until
# Jordan's pick. Lissajous figures at U+E940-E94F, a:b the frequencies, k the phase (1 most open, 0.5
# halfway to degenerate: twisted, as if turning in depth; see lissajous_phase);
# the 27 positions of the three-disc Tower of Hanoi at U+E950-E96A, numbered in base 3 by the
# pegs of the large, middle and small disc (U+E950 + 9 L + 3 M + S).
LISSAJOUS = [(1, 2, 0.5), (1, 3, 0.75), (2, 3, 1.0), (2, 3, 0.75), (3, 2, 1.0), (3, 2, 0.6), (3, 4, 1.0), (4, 3, 0.85),
             (3, 5, 0.95), (5, 4, 1.0), (5, 4, 0.85), (5, 2, 0.7)]
FAMILIES = [(0xE940 + i, f'lissajous{a}{b}k{round(k * 100)}', lissajous_fig(a, b, k), SIDE)
            for i, (a, b, k) in enumerate(LISSAJOUS)] + \
           [(0xE950 + 9 * L + 3 * M + S, f'hanoi{L}{M}{S}', hanoi_state((L, M, S)), SIDE)
            for L in range(3) for M in range(3) for S in range(3)]
# Round 4 options (temporary, out of ornm; superseded in round 5 by MAIN4, kept until dropped):
# U+E970-E977 the Bayes nets, U+E978-E97A the Playfair charts, U+E97B-E97C the Turing tapes.
OPTIONS = [(0xE970 + i, f'bayes{k}', bn(*BAYES4[k][:2], head=BAYES4[k][2], extra=BAYES4[k][3], shafts=BAYES4[k][4]), SIDE)
           for i, k in enumerate(BAYES4)] + \
          [(0xE978 + i, f'playfair{k}', playfair4(k), SIDE) for i, k in enumerate(('fill', 'lobe', 'hatch'))] + \
          [(0xE97B + i, f'tape{p}', tape4(p), SIDE) for i, p in enumerate((340, 440))]
MARKS = [
    (0x2766, 'floralheart', hedera(0x2766), SIDE),
    (0x2767, 'floralheartrot', hedera(0x2767), SIDE),
    (0x2619, 'floralheartrev', hedera(0x2619), SIDE),
    (0x261E, 'indexright', manicule(0x261E), SIDE),
    (0x261C, 'indexleft', manicule(0x261C), SIDE),
    (0x2042, 'asterism', asterism, SIDE),
    (0x203B, 'refmark', refmark, SIDE),
]


# ---- the build hooks ------------------------------------------------------------------------
def _slots():
    return [(cp, f'uni{cp:04X}', key, fn, sb) for cp, key, fn, sb in ORNAMENTS + DRAFTS + FAMILIES + OPTIONS + MARKS]


def glyphs(ctx):
    c = ctx
    K, YC = c.ITALIC_K, c.ITALIC_YC
    order = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()
    st = Style(c.SV, src=lambda n: c.path_of(n), width=c.W, cmap=dict(cmap))
    ctx.log(f'stroke {st.w:.1f} (SV {c.SV:.3f})')
    made = ctx.made = []
    for cp, name, key, fn, sb in _slots():
        assert name not in order, name
        assert cp not in cmap, f'U+{cp:04X} already mapped to {cmap[cp]}'
        p = fn(st); p.simplify(); p = fillet(p); b = p.bounds
        if sb is None: p = mv(p, -b[0]); adv = round(b[2] - b[0])
        else: p = mv(p, sb - b[0]); adv = round(b[2] - b[0] + 2 * sb)
        if K:       # upright in the italic: where the reslant puts its centre, sheared back
            cy = (b[1] + b[3]) / 2
            p = xform(mv(p, K * (cy - YC)), (1, 0, -K, 1, K * YC, 0))
        c.add(name, p, adv); c.GDEF_CLASS[name] = 1
        ctx.map(cp, name); made.append(name)
    ctx.log(f'{len(made)} glyphs')


def features(ctx):
    names = [f'uni{cp:04X}' for cp, *_ in ORNAMENTS + MARKS]      # the drafts stay out of ornm
    letters = [chr(ord('a') + i) for i in range(26)] + [chr(ord('A') + i) for i in range(26)]
    pairs = '\n'.join(f'    sub {l} by {n};' for l, n in zip(letters, names))
    ctx.gsub(f"""
lookup FLEURONS_ORNM_BULLET {{
    sub bullet from [{' '.join(names)}];
}} FLEURONS_ORNM_BULLET;
lookup FLEURONS_ORNM_LETTERS {{
{pairs}
}} FLEURONS_ORNM_LETTERS;
feature ornm {{
    lookup FLEURONS_ORNM_BULLET;
    lookup FLEURONS_ORNM_LETTERS;
}} ornm;
""")


def post(ctx):
    """The outlines as shipped (reslanted, rounded to the grid): each is rounded to the grid
    first (the uprights arrive unrounded), then the best cleanup (`clean`) of it is kept; a
    glyph still with a kink or a short segment gets `unkink`; any that still has an outline problem is
    reported."""
    glyf, hmtx = ctx.glyf, ctx.hmtx; left = []
    for n in ctx.made:
        g = glyf[n]
        g.coordinates.toInt()        # judged as saved: an upright arrives unrounded
        if clean(g) and not (unkink(g) and not outline_problems(g)): left.append(n)
        g.recalcBounds(glyf); hmtx[n] = (hmtx[n][0], getattr(g, 'xMin', 0))
    ctx.log(f'outlines clean but {left}' if left else 'outlines clean')

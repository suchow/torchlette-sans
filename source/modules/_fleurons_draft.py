"""DRAFT (ignored by the build: _*.py). Fleuron drawings for a future modules/fleurons.py.
Concatenation of the scratch files base.py (helpers, Style), designs.py (fleurons), marks.py
(printers marks, truss border, swelled rules). Each drawing takes a Style (s.w stroke, s.r node
radius, s.stem) and returns (pathops.Path, advance), upright; see font-preview/fleurons.html."""
import math
import pathops

CAP, XH = 705, 471
CY = 352                      # vertical centre of the tall ornaments (half the cap height)

# lowercase stems of the seven weights (README table)
STEMS = {'Light': 50, 'Regular': 66, 'Medium': 79, 'SemiBold': 92, 'Bold': 119, 'ExtraBold': 141, 'Black': 163}


class Style:
    def __init__(self, weight):
        self.weight = weight
        self.stem = STEMS[weight]
        self.sv = self.stem / 66
        # the ornaments' stroke: 58 at Regular (between the operators' bar, 53, and the
        # stem, 66); proportional below Regular, growing as SV**0.7 above, so the
        # drawings keep their counters open in Black (Bold 88, Black 109)
        g = self.sv if self.sv <= 1 else self.sv ** 0.5
        self.g = g
        self.w = 58 * g          # Light 44, Regular 58, Bold 78, Black 91
        self.r = 50 * (g if g <= 1 else g ** 0.6)   # node dot: about the period's radius (47 at Regular)


# ---- path construction ----------------------------------------------------------
def _new():
    p = pathops.Path(); return p, p.getPen()


def line(a, b):
    p, pen = _new(); pen.moveTo(a); pen.lineTo(b); pen.endPath(); return p


def polyline(pts, closed=False):
    p, pen = _new(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath() if closed else pen.endPath()
    return p


def cubic(*segs):
    """cubic(p0, (c1, c2, p1), (c1, c2, p2), ...): an open chain of cubics."""
    p, pen = _new(); pen.moveTo(segs[0])
    for c1, c2, e in segs[1:]: pen.curveTo(c1, c2, e)
    pen.endPath(); return p


def smooth(pts, closed=False, t=1.0):
    """A C1 curve through pts (Catmull-Rom as cubics)."""
    n = len(pts)
    p, pen = _new(); pen.moveTo(pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[0]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 6, p1[1] + (p2[1] - p0[1]) * t / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 6, p2[1] - (p3[1] - p1[1]) * t / 6)
        pen.curveTo(c1, c2, p2)
    pen.closePath() if closed else pen.endPath()
    return p


def arc_pts(cx, cy, rx, ry, a0, a1, rot=0.0):
    """Cubic control points of an elliptical arc (degrees), as a list of segments."""
    n = max(1, math.ceil(abs(a1 - a0) / 90)); da = math.radians((a1 - a0) / n)
    k = 4 / 3 * math.tan(da / 4); cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    def T(x, y): return (cx + x * cr - y * sr, cy + x * sr + y * cr)
    t = math.radians(a0); start = T(rx * math.cos(t), ry * math.sin(t)); segs = []
    for _ in range(n):
        t1 = t + da
        c1 = T(rx * (math.cos(t) - k * math.sin(t)), ry * (math.sin(t) + k * math.cos(t)))
        c2 = T(rx * (math.cos(t1) + k * math.sin(t1)), ry * (math.sin(t1) - k * math.cos(t1)))
        segs.append((c1, c2, T(rx * math.cos(t1), ry * math.sin(t1)))); t = t1
    return start, segs


def arc(cx, cy, rx, ry, a0, a1, rot=0.0):
    s, segs = arc_pts(cx, cy, rx, ry, a0, a1, rot); return cubic(s, *segs)


def oval(cx, cy, rx, ry, rot=0.0):
    s, segs = arc_pts(cx, cy, rx, ry, 0, 360, rot)
    p, pen = _new(); pen.moveTo(s)
    for c1, c2, e in segs: pen.curveTo(c1, c2, e)
    pen.closePath(); return p


def fn_curve(f, x0, x1, n=24):
    return smooth([(x0 + (x1 - x0) * i / n, f(x0 + (x1 - x0) * i / n)) for i in range(n + 1)])


# ---- filled shapes ----------------------------------------------------------------
def S(path, w, cap='round', join='round'):
    """Stroke an open or closed path with a round (or butt) pen."""
    q = pathops.Path(path)
    q.stroke(w, pathops.LineCap.ROUND_CAP if cap == 'round' else pathops.LineCap.BUTT_CAP,
             pathops.LineJoin.ROUND_JOIN if join == 'round' else pathops.LineJoin.MITER_JOIN, 4)
    q.convertConicsToQuads(); q.simplify(); return q


def disc(cx, cy, r):
    return oval(cx, cy, r, r)


def ring(cx, cy, r, w):
    return S(oval(cx, cy, r, r), w)


def U(*ps):
    ps = [p for p in ps if p is not None]
    out = pathops.Path(ps[0])
    for q in ps[1:]: out = pathops.op(out, q, pathops.PathOp.UNION)
    out.simplify(); return out


def D(a, b): return pathops.op(a, b, pathops.PathOp.DIFFERENCE)
def I(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)


def box(x0, y0, x1, y1):
    return polyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True)


def xf(p, m):
    from fontTools.pens.transformPen import TransformPen
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q


def mv(p, dx, dy=0): return xf(p, (1, 0, 0, 1, dx, dy))
def mirror(p, axis): return xf(p, (-1, 0, 0, 1, 2 * axis, 0))
def rot(p, deg, cx, cy):
    a = math.radians(deg); c, s_ = math.cos(a), math.sin(a)
    return xf(p, (c, s_, -s_, c, cx - c * cx + s_ * cy, cy - s_ * cx - c * cy))


def towards(a, b, d):
    """The point d along the line from a towards b."""
    L = math.dist(a, b); return (a[0] + (b[0] - a[0]) * d / L, a[1] + (b[1] - a[1]) * d / L)


def chevron(tip, deg, L, half_angle, w):
    """An open arrowhead (two round-ended strokes) with its tip at `tip` pointing at `deg`."""
    a = math.radians(deg)
    pts = []
    for sgn in (1, -1):
        b = a + math.pi - sgn * math.radians(half_angle)
        pts.append((tip[0] + L * math.cos(b), tip[1] + L * math.sin(b)))
    return S(polyline([pts[0], tip, pts[1]]), w)


def fit(p, lsb=60, rsb=None):
    """Shift p so its ink starts at lsb; return (path, advance) with equal sidebearings."""
    b = p.bounds
    return mv(p, lsb - b[0]), (b[2] - b[0]) + lsb + (lsb if rsb is None else rsb)


def vcentre(p, y=CY):
    b = p.bounds; return mv(p, 0, y - (b[1] + b[3]) / 2)


import math


def closed_smooth_stroke(pts, w):
    return S(smooth(pts, closed=True), w)


def rbox(x0, y0, x1, y1, rr):
    p, pen = _new(); k = 0.5523 * rr
    pen.moveTo((x0 + rr, y0)); pen.lineTo((x1 - rr, y0)); pen.curveTo((x1 - rr + k, y0), (x1, y0 + rr - k), (x1, y0 + rr))
    pen.lineTo((x1, y1 - rr)); pen.curveTo((x1, y1 - rr + k), (x1 - rr + k, y1), (x1 - rr, y1)); pen.lineTo((x0 + rr, y1))
    pen.curveTo((x0 + rr - k, y1), (x0, y1 - rr + k), (x0, y1 - rr)); pen.lineTo((x0, y0 + rr))
    pen.curveTo((x0, y0 + rr - k), (x0 + rr - k, y0), (x0 + rr, y0)); pen.closePath(); return p


def bend(a, b, k):
    """A gently curved stroke path from a to b, bowed k units to the left of a->b."""
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); L = math.dist(a, b)
    n = (-(b[1] - a[1]) / L, (b[0] - a[0]) / L)
    c = (m[0] + n[0] * k, m[1] + n[1] * k)
    return cubic(a, ((a[0] + 2 * (c[0] - a[0]) / 3, a[1] + 2 * (c[1] - a[1]) / 3),
                     (b[0] + 2 * (c[0] - b[0]) / 3, b[1] + 2 * (c[1] - b[1]) / 3), b))


def polar(c, r, deg): return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


# ======================================================================================

def neuron(s):
    """A neuron: the soma, four dendrites that fork, the axon and three boutons."""
    w, r = s.w, s.r
    c = (300, CY); R = 98 + 0.2 * w
    parts = [disc(*c, R)]
    for ang, L1, L2, sp, k in ((100, 150, 115, 34, 14), (152, 165, 120, 32, -14), (208, 165, 120, 32, 14), (260, 150, 115, 34, -14)):
        p0 = polar(c, R - 15, ang); p1 = polar(c, R + L1, ang)
        parts.append(S(bend(p0, p1, k), w))
        for sg in (1, -1):
            parts.append(S(bend(p1, polar(p1, L2, ang + sg * sp), sg * 10), w))
    xe = 860
    parts.append(S(line(c, (xe, CY)), w))
    hill = polyline([polar(c, R, 52), (c[0] + R + 120, CY + w / 2), (c[0] + R + 120, CY - w / 2), polar(c, R, -52)], closed=True)
    parts.append(hill)
    for dy in (150, 0, -150):
        e = (xe + 170, CY + dy)
        parts.append(S(cubic((xe - 40, CY), ((xe + 50, CY), (xe + 70, CY + dy), e)), w))
        parts.append(disc(*e, r * 1.1))
    return fit(vcentre(U(*parts)))


def perceptron(s):
    """Three inputs converging on a node, and its output."""
    w, r = s.w, s.r
    nx, ny, R = 560, CY, 178
    parts = [ring(nx, ny, R, w)]
    for dy in (265, 0, -265):
        a = (90, ny + dy)
        parts.append(disc(a[0], a[1], r * 1.2))
        parts.append(S(line(a, towards((nx, ny), a, R)), w))
    h = 72 - 0.15 * (w - 58)
    sig = fn_curve(lambda x: ny + h * math.tanh((x - nx) / 36), nx - 100, nx + 100, 12)
    parts.append(S(sig, w * 0.9))
    parts.append(S(line((nx + R, ny), (nx + R + 200, ny)), w))
    parts.append(chevron((nx + R + 232, ny), 0, 100, 42, w))
    return fit(U(*parts))


def network(s):
    """A small fully connected network: 2, 3 and 2 nodes and their edges."""
    w, r = s.w, s.r
    cols = [[(90, CY - 165), (90, CY + 165)], [(470, CY - 300), (470, CY), (470, CY + 300)], [(850, CY - 165), (850, CY + 165)]]
    parts = []
    for A, B in zip(cols, cols[1:]):
        for a in A:
            for b in B: parts.append(S(line(a, b), w * 0.7))
    for col in cols:
        for p in col: parts.append(disc(*p, r * 1.5))
    return fit(U(*parts))


def sigmoid(s):
    """The logistic curve as a swash, with ball terminals."""
    w, r = s.w, s.r
    f = lambda x: 75 + 560 / (1 + math.exp(-(x - 560) / 95))
    c = fn_curve(f, 90, 1030, 20)
    return fit(U(S(c, w), disc(90, f(90), r * 1.35), disc(1030, f(1030), r * 1.35)))


def relu(s):
    """The ReLU hinge between two ball terminals."""
    w, r = s.w, s.r
    a, k, b = (80, 150), (520, 150), (900, 600)
    return fit(U(S(polyline([a, k, b]), w), disc(*a, r * 1.35), disc(*b, r * 1.35)))


def descent(s):
    """Gradient descent: elliptical contours and the iterates' path into the minimum."""
    w, r = s.w, s.r
    cx, cy, tilt = 560, CY, 20
    radii = (500, 310, 125); q = 0.56
    parts = [S(oval(cx, cy, rx, rx * q, tilt), w * 0.62) for rx in radii]
    def at(u, v):
        a = math.radians(tilt); return (cx + u * math.cos(a) - v * math.sin(a), cy + u * math.sin(a) + v * math.cos(a))
    def on(rx, u, sg): return at(u, sg * rx * q * math.sqrt(1 - (u / rx) ** 2))
    path = [on(500, -400, 1), on(310, -220, -1), on(125, -70, 1), at(0, 0)]
    parts.append(S(polyline(path), w))
    for p_ in path[:-1]: parts.append(disc(*p_, r * 1.1))
    parts.append(disc(*path[-1], r * 1.45))
    return fit(U(*parts))


def landscape(s):
    """A loss landscape: a local minimum, a ridge, the global minimum and the ball in it."""
    w, r = s.w, s.r
    pts = [(70, 560), (180, 330), (300, 265), (410, 330), (520, 430), (640, 300), (760, 130), (880, 115),
           (990, 260), (1100, 520)]
    c = smooth(pts)
    R = 70 + 0.3 * w
    bx = 860; by = 115 + w / 2 + R - 6
    return fit(U(S(c, w), disc(bx, by, R)))


def nabla(s):
    """The nabla with an inline: two nested triangles, point down."""
    w = s.w
    cx = 400; top, bot, hw = 690, 20, 380
    ang = math.atan2(top - bot, hw)
    def tri(d):                                 # the triangle inset by d (perpendicular)
        dx = d / math.tan(ang / 2)
        return polyline([(cx - hw + dx, top - d), (cx + hw - dx, top - d), (cx, bot + d / math.cos(math.pi / 2 - ang) )], closed=True)
    g = w * 0.5 + 0.6 * w * 0.5 + 62
    return fit(U(S(tri(0), w), S(tri(g), w * 0.6)))


def lissajous(s):
    """The 3:2 Lissajous figure."""
    w = s.w
    n = 72
    pts = [(560 + 470 * math.sin(3 * 2 * math.pi * i / n + math.pi / 2), CY + 340 * math.sin(2 * 2 * math.pi * i / n)) for i in range(n)]
    return fit(S(smooth(pts, closed=True), w))


def golden(s):
    """The golden rectangle: squares 8, 5, 3, 2 (and 1, 1) and the spiral through them."""
    w, r = s.w, s.r
    u = 86; H = 8 * u; W_ = 13 * u
    x0, y0 = 60, CY - H / 2
    thin = w * 0.55
    parts = [S(box(x0, y0, x0 + W_, y0 + H), thin)]
    # squares: 8 on the left, 5 top-right, 3 bottom-right, 2 bottom-left of the rest, 1, 1
    # cut lines
    cuts = [((x0 + 8 * u, y0), (x0 + 8 * u, y0 + H)),            # 8 | 5x8
            ((x0 + 8 * u, y0 + 3 * u), (x0 + 13 * u, y0 + 3 * u)),  # 5 above, 3x5 below
            ((x0 + 10 * u, y0), (x0 + 10 * u, y0 + 3 * u)),      # 3 on the right, 2x3 on the left
            ((x0 + 8 * u, y0 + 2 * u), (x0 + 10 * u, y0 + 2 * u)),  # 2 below? (2 at the bottom-left)
            ((x0 + 9 * u, y0 + 2 * u), (x0 + 9 * u, y0 + 3 * u))]
    for a, b in cuts: parts.append(S(line(a, b), thin))
    # the spiral: quarter arcs, each in its square
    arcs = [(x0 + 8 * u, y0, 8 * u, 90, 180),                 # big square: centre at its bottom-right corner
            (x0 + 8 * u, y0 + 3 * u, 5 * u, 0, 90),           # 5-square: centre at its bottom-left
            (x0 + 10 * u, y0 + 3 * u, 3 * u, -90, 0),         # 3-square: centre top-left
            (x0 + 10 * u, y0 + 2 * u, 2 * u, 180, 270),       # 2-square: centre top-right
            (x0 + 9 * u, y0 + 2 * u, 1 * u, 90, 180)]
    # one continuous path: 8 (180->90), 5 (90->0), 3 (0->-90), 2 (-90->-180), 1 (-180->-270)
    sweep = [(arcs[0], 180, 90), (arcs[1], 90, 0), (arcs[2], 0, -90), (arcs[3], -90, -180), (arcs[4], -180, -270)]
    segs = []; start = None
    for (cx, cy, R, _, _), a0, a1 in sweep:
        st, sg = arc_pts(cx, cy, R, R, a0, a1)
        if start is None: start = st
        segs += sg
    parts.append(S(cubic(start, *segs), w, cap='butt'))
    return fit(U(*parts))


def conv(s):
    """A 3x3 kernel framed on a 4x4 grid of pixels, projecting to one output."""
    w, r = s.w, s.r
    st = 160 + 30 * (s.g - 1); x0 = 90; y0 = CY - 1.5 * st
    dr = r * 0.78
    parts = []
    for i in range(4):
        for j in range(4):
            parts.append(disc(x0 + i * st, y0 + j * st, dr))
    m = st / 2; fw = w * 0.72
    fx0, fx1, fy0, fy1 = x0 - m, x0 + 2 * st + m, y0 + st - m, y0 + 3 * st + m
    parts.append(S(rbox(fx0, fy0, fx1, fy1, 40), fw))
    out = (x0 + 3 * st + 330, y0 + 2 * st)
    for c in ((fx1 - 12, fy1 - 12), (fx1 - 12, fy0 + 12)):
        parts.append(S(line(c, towards(out, c, r * 1.5)), w * 0.6))
    parts.append(disc(*out, r * 1.5))
    return fit(U(*parts))


def tensor(s):
    """A tensor: a cube in oblique projection, each visible face cut 3 x 3."""
    w = s.w
    L = 430; dx, dy = 285, 215; x0, y0 = 70, 20
    ew = w * 0.58
    def seg(a, b): return S(line(a, b), ew)
    F = [(x0, y0), (x0 + L, y0), (x0 + L, y0 + L), (x0, y0 + L)]
    T = [(x0, y0 + L), (x0 + L, y0 + L), (x0 + L + dx, y0 + L + dy), (x0 + dx, y0 + L + dy)]
    R_ = [(x0 + L, y0), (x0 + L + dx, y0 + dy), (x0 + L + dx, y0 + L + dy), (x0 + L, y0 + L)]
    outline = [(x0, y0), (x0 + L, y0), (x0 + L + dx, y0 + dy), (x0 + L + dx, y0 + L + dy), (x0 + dx, y0 + L + dy), (x0, y0 + L)]
    parts = [S(polyline(outline, closed=True), w), S(polyline([(x0, y0 + L), (x0 + L, y0 + L), (x0 + L + dx, y0 + L + dy)]), w),
             S(line((x0 + L, y0), (x0 + L, y0 + L)), w)]
    for k in (1, 2):
        f = k / 3
        parts.append(seg((x0 + L * f, y0), (x0 + L * f, y0 + L)))
        parts.append(seg((x0, y0 + L * f), (x0 + L, y0 + L * f)))
        parts.append(seg((x0 + L * f, y0 + L), (x0 + L * f + dx, y0 + L + dy)))
        parts.append(seg((x0 + dx * f, y0 + L + dy * f), (x0 + L + dx * f, y0 + L + dy * f)))
        parts.append(seg((x0 + L + dx * f, y0 + dy * f), (x0 + L + dx * f, y0 + L + dy * f)))
        parts.append(seg((x0 + L, y0 + L * f), (x0 + L + dx, y0 + dy + L * f)))
    return fit(vcentre(U(*parts)))


def tape(s):
    """A Turing machine: the tape's cells, ones and zeros, and the head over one cell."""
    w, r = s.w, s.r
    cw = 200; n = 5; x0 = 40; yb, yt = 40, 330
    parts = [S(line((x0, yb), (x0 + n * cw, yb)), w), S(line((x0, yt), (x0 + n * cw, yt)), w)]
    for i in range(1, n): parts.append(S(line((x0 + i * cw, yb), (x0 + i * cw, yt)), w * 0.8))
    cyc = (yb + yt) / 2
    for i, bit in enumerate([1, 0, 1, 1, 0]):
        cx = x0 + (i + 0.5) * cw
        if bit: parts.append(S(line((cx, cyc - 62), (cx, cyc + 62)), w))
        else: parts.append(disc(cx, cyc, s.r * 1.05))
    hx = x0 + 2.5 * cw
    head = polyline([(hx - 100, 640), (hx + 100, 640), (hx, 440)], closed=True)
    parts.append(U(S(head, w * 0.6), head))
    return fit(U(*parts))


def gate(s):
    """An AND gate with its two inputs and output."""
    w, r = s.w, s.r
    x0, xm, R = 280, 440, 230; cy = CY
    p, pen = _new()
    pen.moveTo((xm, cy - R)); pen.lineTo((x0, cy - R)); pen.lineTo((x0, cy + R)); pen.lineTo((xm, cy + R))
    st, segs = arc_pts(xm, cy, R, R, 90, -90)
    for c1, c2, e in segs: pen.curveTo(c1, c2, e)
    pen.closePath()
    parts = [S(p, w)]
    for dy in (115, -115):
        parts.append(S(line((80, cy + dy), (x0, cy + dy)), w)); parts.append(disc(80, cy + dy, r * 1.2))
    parts.append(S(line((xm + R, cy), (xm + R + 200, cy)), w)); parts.append(disc(xm + R + 200, cy, r * 1.2))
    return fit(U(*parts))


def lambda_ring(s):
    """Lambda in a circle."""
    w = s.w
    cx, cy, R = 400, CY, 372
    parts = [ring(cx, cy, R, w)]
    top = (cx - 62, cy + 222); bot = (cx + 158, cy - 225)
    parts.append(S(cubic((cx - 160, cy + 236), ((cx - 120, cy + 252), (cx - 82, cy + 250), top)), w))
    parts.append(S(line(top, bot), w))
    t = 0.45
    mid = (top[0] + (bot[0] - top[0]) * t, top[1] + (bot[1] - top[1]) * t)
    parts.append(S(line(mid, (cx - 150, cy - 225)), w))
    return fit(U(*parts))


def galton(s):
    """A Galton board's outcome: stacked balls under the bell curve."""
    w, r = s.w, s.r
    sig = 205; cx = 560; y0 = 30
    g = lambda x: y0 + 610 * math.exp(-((x - cx) / sig) ** 2 / 2)
    rr = 44 * s.g ** 0.2 if s.g > 1 else 44 * s.g ** 0.5
    pitch = 118
    parts = [S(fn_curve(g, 60, 1060, 24), w)]
    for k, n in zip(range(-3, 4), (1, 2, 3, 4, 3, 2, 1)):
        x = cx + k * 112
        for j in range(n):
            parts.append(disc(x, y0 + 44 + j * pitch, rr))
    return fit(U(*parts))


def bayes(s):
    """A Bayes net: three nodes, A pointing to B and C, B pointing to C."""
    w = s.w
    R = 118
    A, B, C = (450, 598), (150, 118), (750, 118)
    parts = [ring(*A, R, w), ring(*B, R, w), ring(*C, R, w)]
    for p0, p1 in ((A, B), (A, C), (B, C)):
        a = towards(p0, p1, R + w * 0.9); b = towards(p1, p0, R + w * 0.9)
        parts.append(S(line(a, b), w))
        deg = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        parts.append(chevron(b, deg, 76, 38, w))
    return fit(U(*parts))


def brain(s):
    """A brain in profile, facing left: the cerebrum with its sulci, the cerebellum, the stem."""
    w = s.w; t = w * 0.85
    out = [(70, 400), (130, 560), (290, 680), (500, 712), (720, 668), (880, 540), (935, 400), (885, 290),
           (720, 250), (560, 205), (390, 200), (270, 255), (230, 330), (160, 300), (90, 330)]
    parts = [closed_smooth_stroke(out, w)]
    # lateral fissure, central sulcus, two more
    parts.append(S(smooth([(255, 320), (420, 360), (600, 420)]), t))
    parts.append(S(smooth([(560, 705), (520, 590), (545, 480)]), t))
    parts.append(S(smooth([(300, 640), (300, 520), (380, 460)]), t))
    parts.append(S(smooth([(760, 640), (720, 520), (790, 420)]), t))
    parts.append(S(smooth([(390, 290), (520, 300), (640, 260)]), t))
    # cerebellum and the stem
    cb = [(700, 250), (840, 270), (905, 200), (850, 110), (720, 110), (650, 170)]
    parts.append(closed_smooth_stroke(cb, w))
    parts.append(S(smooth([(735, 210), (820, 200)]), t * 0.8))
    parts.append(S(smooth([(720, 160), (830, 150)]), t * 0.8))
    parts.append(S(smooth([(590, 210), (600, 100), (630, 0)]), w))
    return fit(vcentre(U(*parts)))


def eye(s):
    """An eye: the lids, iris and pupil, and five lashes."""
    w = s.w
    cx, cy, hw, hh = 560, CY - 40, 470, 250
    P0, P1, P2, P3 = (cx - hw, cy), (cx - hw * 0.55, cy + hh * 1.25), (cx + hw * 0.55, cy + hh * 1.25), (cx + hw, cy)
    p, pen = _new(); pen.moveTo(P0); pen.curveTo(P1, P2, P3)
    pen.curveTo((cx + hw * 0.55, cy - hh * 1.25), (cx - hw * 0.55, cy - hh * 1.25), P0); pen.closePath()
    parts = [S(p, w)]
    ri = 165
    parts.append(ring(cx, cy, ri, w))
    parts.append(disc(cx, cy, (ri - w / 2) * 0.55))
    for k in (-2, -1, 0, 1, 2):
        a = math.radians(90 - k * 26)
        t = 0.5 + k * 0.17
        bx = (1 - t) ** 3 * P0[0] + 3 * (1 - t) ** 2 * t * P1[0] + 3 * (1 - t) * t ** 2 * P2[0] + t ** 3 * P3[0]
        by = (1 - t) ** 3 * P0[1] + 3 * (1 - t) ** 2 * t * P1[1] + 3 * (1 - t) * t ** 2 * P2[1] + t ** 3 * P3[1]
        parts.append(S(line((bx, by), (bx + 120 * math.cos(a), by + 120 * math.sin(a))), w))
    return fit(vcentre(U(*parts)))


def necker(s):
    """The Necker cube: a wire cube, every edge drawn."""
    w = s.w
    L = 430; dx, dy = 250, 250; x0, y0 = 70, 0
    F = [(x0, y0), (x0 + L, y0), (x0 + L, y0 + L), (x0, y0 + L)]
    B = [(x + dx, y + dy) for x, y in F]
    parts = [S(polyline(F, closed=True), w), S(polyline(B, closed=True), w)]
    for a, b in zip(F, B): parts.append(S(line(a, b), w))
    return fit(vcentre(U(*parts)))


def owl(s):
    """The owl of Minerva on a branch: ear tufts, two eyes, the beak, the wings."""
    w = s.w
    cx = 420; hw = 270
    p, pen = _new()
    # left ear tip, down the left side, round the bottom, up to the right ear tip, a brow V back
    pen.moveTo((cx - hw + 25, 720))
    pen.curveTo((cx - hw - 10, 520), (cx - hw - 30, 330), (cx - hw + 5, 220))
    pen.curveTo((cx - hw + 45, 100), (cx - 120, 62), (cx, 62))
    pen.curveTo((cx + 120, 62), (cx + hw - 45, 100), (cx + hw - 5, 220))
    pen.curveTo((cx + hw + 30, 330), (cx + hw + 10, 520), (cx + hw - 25, 720))
    pen.curveTo((cx + 150, 650), (cx + 80, 615), (cx, 615))
    pen.curveTo((cx - 80, 615), (cx - 150, 650), (cx - hw + 25, 720))
    pen.closePath()
    parts = [S(p, w)]
    er = 100
    for sg in (1, -1):
        parts.append(ring(cx + sg * 112, 470, er, w))
        parts.append(disc(cx + sg * 112, 462, (er - w / 2) * 0.58))
        # a wing: a curve down the flank
        parts.append(S(smooth([(cx + sg * 175, 330), (cx + sg * 160, 220), (cx + sg * 95, 130)]), w * 0.85))
    beak = polyline([(cx - 36, 405), (cx + 36, 405), (cx, 320)], closed=True)
    parts.append(U(S(beak, w * 0.5), beak))
    parts.append(S(line((cx - hw - 120, 45), (cx + hw + 120, 45)), w))
    return fit(U(*parts))


# ---- printer's-flower-style pieces ---------------------------------------------------

def dinkus(s):
    """A section break: three nodes on a wave, an arch over the first pair and a hollow under the second."""
    w, r = s.w, s.r
    y = 300; xs = (80, 400, 720)
    parts = [S(arc(240, y, 160, 150, 0, 180), w), S(arc(560, y, 160, 150, 180, 360), w),
             disc(xs[0], y, r * 1.05), disc(xs[1], y, r * 1.35), disc(xs[2], y, r * 1.05)]
    return fit(U(*parts))


def flank_left(s):
    """Heading flanker, pointing right: three dendrites gather into a node beside the heading."""
    w, r = s.w, s.r
    y = CY - 60; node = (900, y); stem0 = (430, y)
    parts = [S(line(stem0, node), w)]
    for dy in (150, 0, -150):
        p1 = (190, y + dy)
        parts.append(S(cubic(stem0, ((330, y), (300, y + dy), p1)), w))
        parts.append(disc(p1[0] - 20, p1[1], r))
    parts.append(disc(*node, r * 1.6))
    return fit(U(*parts))


def flank_right(s):
    p, adv = flank_left(s)
    return mirror(p, adv / 2), adv


def tailpiece(s):
    """A tail-piece: a merge tree, four leaves to two to one."""
    w, r = s.w, s.r
    top, mid, low = 650, 370, 110
    L = [(90 + 240 * i, top) for i in range(4)]
    M = [(210, mid), (690, mid)]
    R_ = (450, low)
    parts = []
    for i, p in enumerate(L): parts.append(S(line(p, M[i // 2]), w))
    for p in M: parts.append(S(line(p, R_), w))
    for p in L: parts.append(disc(*p, r * 1.15))
    for p in M: parts.append(disc(*p, r * 1.3))
    parts.append(disc(*R_, r * 1.55))
    return fit(U(*parts))


FLEURONS = [
    ('neuron', 'Neuron', neuron),
    ('perceptron', 'Perceptron', perceptron),
    ('network', 'Layered network', network),
    ('sigmoid', 'Sigmoid swash', sigmoid),
    ('relu', 'ReLU hinge', relu),
    ('landscape', 'Loss landscape', landscape),
    ('lissajous', 'Lissajous figure', lissajous),
    ('golden', 'Golden rectangle', golden),
    ('conv', 'Convolution kernel', conv),
    ('tensor', 'Tensor cube', tensor),
    ('tape', 'Turing tape', tape),
    ('gate', 'AND gate', gate),
    ('lambda', 'Lambda roundel', lambda_ring),
    ('galton', 'Galton bell', galton),
    ('bayes', 'Bayes net', bayes),
    ('brain', 'Brain', brain),
    ('eye', 'Eye', eye),
    ('necker', 'Necker cube', necker),
    ('owl', 'Owl of Minerva', owl),
    ('dinkus', 'Node dinkus', dinkus),
    ('flank_left', 'Flanker, left', flank_left),
    ('flank_right', 'Flanker, right', flank_right),
    ('tailpiece', 'Merge-tree tail-piece', tailpiece),
]
import math


def flipv(p, axis): return xf(p, (1, 0, 0, -1, 0, 2 * axis))


# ---- hederas ------------------------------------------------------------------------
def _leaf(s, cx):
    """The ivy leaf, solid, point down at (cx, 0), notch at (cx, 455), with a white vein."""
    N, P = (cx, 455), (cx, 0)
    p, pen = _new(); pen.moveTo(N)
    pen.curveTo((cx - 25, 560), (cx - 165, 625), (cx - 270, 545))
    pen.curveTo((cx - 360, 470), (cx - 325, 285), (cx - 200, 170))
    pen.curveTo((cx - 120, 95), (cx - 40, 55), P)
    pen.curveTo((cx + 40, 55), (cx + 120, 95), (cx + 200, 170))
    pen.curveTo((cx + 325, 285), (cx + 360, 470), (cx + 270, 545))
    pen.curveTo((cx + 165, 625), (cx + 25, 560), N)
    pen.closePath()
    vein = S(cubic((cx, 400), ((cx + 8, 300), (cx + 6, 200), (cx, 105))), s.w * 0.36)
    return D(p, vein)


def hedera(s):
    """U+2766 floral heart: the leaf, a little turned, and its stem curling over the top."""
    w, r = s.w, s.r; cx = 330
    leaf = rot(_leaf(s, cx), -20, cx, 330)          # the point swings to the lower left
    n = (cx + 43, 447)                              # the notch, turned with the leaf
    stem = S(smooth([n, (cx + 62, 590), (cx + 140, 715), (cx + 260, 752), (cx + 340, 700), (cx + 335, 625), (cx + 270, 625)]), w)
    end = disc(cx + 270, 625, r * 1.1)
    p = xf(U(leaf, stem, end), (0.92, 0, 0, 0.92, 0, 0))
    return fit(vcentre(p, CY))


def hedera_rot(s):
    """U+2767 rotated floral heart bullet: the floral heart turned to point right."""
    p, _ = hedera(s); b = p.bounds
    q = rot(p, -90, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    return fit(vcentre(q, 300))


def hedera_rev(s):
    """U+2619 reversed rotated floral heart bullet: U+2767 mirrored, pointing left."""
    p, adv = hedera_rot(s)
    return mirror(p, adv / 2), adv


# ---- asterism, reference mark ---------------------------------------------------------
def _asterisk(cx, cy, a, w):
    return U(*[S(line((cx, cy), (cx + a * math.cos(math.radians(90 + 72 * k)), cy + a * math.sin(math.radians(90 + 72 * k)))), w, cap='butt')
               for k in range(5)])


def asterism(s):
    """U+2042 asterism: three five-spoked asterisks (the font's asterisk has five) in a triangle."""
    w = s.w * 0.82; a = 108; cx = 320
    p = U(_asterisk(cx, 590, a, w), _asterisk(cx - 128, 372, a, w), _asterisk(cx + 128, 372, a, w))
    return fit(p)


def refmark(s):
    """U+203B reference mark: a saltire with a dot in each quarter."""
    w, r = s.w, s.r; cx, cy = 340, 300; a = 215
    p = U(S(line((cx - a, cy - a), (cx + a, cy + a)), w), S(line((cx - a, cy + a), (cx + a, cy - a)), w),
          *[disc(cx + dx, cy + dy, r * 1.15) for dx, dy in ((0, 205), (0, -205), (205, 0), (-205, 0))])
    return fit(p)


# ---- manicules ------------------------------------------------------------------------
def manicule(s):
    """U+261E white right pointing index: cuff, the back of the hand, the index finger,
    three folded fingers and the thumb."""
    w = s.w
    parts = []
    parts.append(S(rbox_(60, 105, 190, 575, 28), w))
    # the back of the hand and the index finger, round its tip, back along its underside
    p, pen = _new()
    pen.moveTo((190, 525))
    pen.curveTo((280, 548), (350, 558), (430, 558))
    pen.lineTo((880, 558))
    st, segs = arc_pts(880, 492, 66, 66, 90, -90)
    for c1, c2, e in segs: pen.curveTo(c1, c2, e)
    pen.lineTo((520, 426))
    pen.endPath()
    parts.append(S(p, w))
    # folded fingers: three rounded ends stacked under the index finger
    for top, bot, xr in ((426, 320, 680), (320, 214, 648), (214, 108, 606)):
        rr = (top - bot) / 2
        q, qp = _new(); qp.moveTo((470, top)); qp.lineTo((xr - rr, top))
        st, segs = arc_pts(xr - rr, (top + bot) / 2, rr, rr, 90, -90)
        for c1, c2, e in segs: qp.curveTo(c1, c2, e)
        qp.lineTo((470, bot)); qp.endPath()
        parts.append(S(q, w))
    # palm: from the cuff's foot to the last finger
    parts.append(S(cubic((190, 150), ((280, 120), (380, 108), (470, 108))), w))
    # thumb: lies over the folded fingers' roots, its tip on the middle finger
    parts.append(S(smooth([(250, 470), (380, 432), (485, 365), (530, 320)]), w))
    return fit(vcentre(U(*parts), 345))


def manicule_left(s):
    """U+261C white left pointing index."""
    p, adv = manicule(s)
    return mirror(p, adv / 2), adv


def rbox_(x0, y0, x1, y1, rr):
    p, pen = _new(); k = 0.5523 * rr
    pen.moveTo((x0 + rr, y0)); pen.lineTo((x1 - rr, y0)); pen.curveTo((x1 - rr + k, y0), (x1, y0 + rr - k), (x1, y0 + rr))
    pen.lineTo((x1, y1 - rr)); pen.curveTo((x1, y1 - rr + k), (x1 - rr + k, y1), (x1 - rr, y1)); pen.lineTo((x0 + rr, y1))
    pen.curveTo((x0 + rr - k, y1), (x0, y1 - rr + k), (x0, y1 - rr)); pen.lineTo((x0, y0 + rr))
    pen.curveTo((x0, y0 + rr - k), (x0 + rr - k, y0), (x0 + rr, y0)); pen.closePath(); return p


MARKS = [
    ('hedera', 'Floral heart', hedera, 0x2766),
    ('hedera_rot', 'Rotated floral heart', hedera_rot, 0x2767),
    ('hedera_rev', 'Reversed rotated heart', hedera_rev, 0x2619),
    ('asterism', 'Asterism', asterism, 0x2042),
    ('refmark', 'Reference mark', refmark, 0x203B),
    ('manicule', 'Manicule, right', manicule, 0x261E),
    ('manicule_left', 'Manicule, left', manicule_left, 0x261C),
]


# ---- the truss border ----------------------------------------------------------------
# A Warren truss: two rails 300 apart joined by diagonals, a node at every joint. The
# horizontal unit is 500 wide (outer nodes at its edges, the inner node in the middle).
# The vertical unit is one line of `line-height: 1` (1000 units: the line box runs from
# -122.5 to 877.5 in this font) holding two periods. The corners hold the joint where
# both strips meet; rails sit at x 80 / 380 in a 630-wide side glyph and at y 127.5 /
# 427.5 in the top row, which puts all four corners and both strips on one phase.
YI, YO = 127.5, 427.5          # top row: inner and outer rails
XO, XI, AV = 80, 380, 630      # left side: outer and inner rails, advance
LB0, LB1 = -122.5, 877.5       # the line box at line-height 1
MIDLINE = (LB0 + LB1) / 2      # 377.5: flipping about it turns a top piece into a bottom one


def _truss_w(s): return s.w * 0.78, s.r * 1.05


def border_h(s):
    w, r = _truss_w(s)
    parts = [S(line((-100, YI), (600, YI)), w), S(line((-100, YO), (600, YO)), w),
             S(polyline([(-250, YI), (0, YO), (250, YI), (500, YO), (750, YI)]), w),
             disc(0, YO, r), disc(500, YO, r), disc(250, YI, r)]
    return I(U(*parts), box(0, -500, 500, 1500)), 500


def border_v(s):
    w, r = _truss_w(s)
    pts = []; y = LB0 - 1000
    while y < LB1 + 1000:
        pts.append((XO, y)); pts.append((XI, y + 250)); y += 500
    parts = [S(line((XO, -2000), (XO, 2500)), w), S(line((XI, -2000), (XI, 2500)), w), S(polyline(pts), w)]
    parts += [disc(*p, r) for p in pts]
    return I(U(*parts), box(0, LB0, AV, LB1)), AV


def border_corner(s):
    """Top-left corner."""
    w, r = _truss_w(s)
    hub, corner = (XI, YI), (XO, YO)
    parts = [S(polyline([(XO, LB0 - 300), (XO, YO), (AV + 100, YO)]), w),
             S(polyline([(XI, LB0 - 300), (XI, YI), (AV + 100, YI)]), w),
             S(line((XO, LB0), hub), w), S(line(hub, (AV, YO)), w), S(line(hub, corner), w),
             disc(*hub, r), disc(XO, LB0, r), disc(AV, YO, r), disc(*corner, r * 1.5)]
    return I(U(*parts), box(-200, LB0, AV, 1500)), AV


def rule_cap(s):
    """Left end of a truss rule: the truss closed off in a triangle."""
    w, r = _truss_w(s); A = 330; x0 = A - 250
    parts = [S(line((x0, YI), (A + 100, YI)), w), S(line((x0, YI), (A, YO)), w), S(line((A - 1, YO), (A + 100, YO)), w),
             disc(x0, YI, r * 1.3), disc(A, YO, r)]
    return I(U(*parts), box(-200, -500, A, 1500)), A


def border_set(s):
    """{name: (path, advance)} for the eight frame pieces and the rule's two caps."""
    h, ah = border_h(s); v, av = border_v(s); c, ac = border_corner(s); cap, acap = rule_cap(s)
    return {
        'border.h.top': (h, ah), 'border.h.bottom': (flipv(h, MIDLINE), ah),
        'border.v.left': (v, av), 'border.v.right': (mirror(v, av / 2), av),
        'border.tl': (c, ac), 'border.tr': (mirror(c, ac / 2), ac),
        'border.bl': (flipv(c, MIDLINE), ac), 'border.br': (flipv(mirror(c, ac / 2), MIDLINE), ac),
        'rule.left': (cap, acap), 'rule.right': (mirror(cap, acap / 2), acap),
    }


# ---- swelled rules ---------------------------------------------------------------------
def swelled(s, L, k=2.0, y=290, side=40):
    """A swelled rule L long: k x the stem thick at the centre, tapering to hairline points."""
    t = k * s.stem; x0 = side; x1 = side + L; xm = (x0 + x1) / 2
    p, pen = _new(); pen.moveTo((x0, y))
    pen.curveTo((x0 + L * 0.24, y), (xm - L * 0.2, y + t / 2), (xm, y + t / 2))
    pen.curveTo((xm + L * 0.2, y + t / 2), (x1 - L * 0.24, y), (x1, y))
    pen.curveTo((x1 - L * 0.24, y), (xm + L * 0.2, y - t / 2), (xm, y - t / 2))
    pen.curveTo((xm - L * 0.2, y - t / 2), (x0 + L * 0.24, y), (x0, y))
    pen.closePath()
    return p, L + 2 * side


RULES = [('swell.short', 'Swelled rule, short', 2000), ('swell.medium', 'Swelled rule, medium', 3500), ('swell.long', 'Swelled rule, long', 6000)]

"""Build one style of Torchlette Sans from Mulish (SIL OFL 1.1).

    python build.py SOURCE.ttf OUT.ttf [WGHT STYLE]

SOURCE.ttf is the static instance of mulish/Mulish[wght].ttf at WGHT (the Makefile
writes it to build/Mulish-324.ttf for Regular); for an italic STYLE ('Italic',
'BoldItalic' ...) it is the instance of mulish/Mulish-Italic[wght].ttf, which the build
unslants, works on as an upright and reslants at the end (see "italic" below). The
variable font itself is read again for the heavier small caps and for the
stem-preserving horizontal scaling; MULISH_VF overrides its path. Every number in this
file can be read as a design decision; the P(...) knobs can be overridden from the
environment for experiments.

What changes from Mulish:
round tittles and dots; wider round letters, narrower v w y z s; a lower x-height
with longer ascenders and descenders; an e crossbar at least 0.68 of the stem;
redrawn old-style figures; true small caps (.sc) drawn from a heavier Mulish instance; and these features:

liga  ff ffi ffl (Raleway-style staggered: the first f is shorter, its hook runs
      into the second stem) and tt (shared crossbar)
ss01  Th   (h tucked under the T bar)
ss02  -> as an arrow, <= >= as the signs, 28x28 as 28×28, ... as an ellipsis
ss03  th   (t crossbar runs into the h stem)
ss04-ss07  alternate a (two-storey), Q, y, t; ss08 alternate 7
onum  proportional old-style figures; with tnum, tabular old-style (Mulish's .tosf)
pnum, tnum  switch old-style figures between proportional and tabular
smcp, c2sc  small capitals A.sc ... Z.sc; c2sc also maps figures to small-cap figures
ss16  Torchlette prose ligatures: the 54 kept from the two ligature labs (fb fh fk fj ft fft tf fy tw
      ry rw ll tp xt fu rv, rn and cl spacing, TT, five word logotypes, word marks for backward,
      forward, output, vector, length and residual, range dash, minus,
      plus-minus, approx, ordinals, fractions, ratio colon, cap hyphen, arrows, old-style
      operators and percent, B×C×H×W, tuple and unit spaces, numero, matmul @, version tag,
      spark bars, progress bar); cv01-cv99 each turn on one of them (cvNN = lab id NN)
ss15  spark line instead of spark bars for {1,5,3,8}

Extensions live in modules/*.py, run at three hook points (glyphs, features, post);
modules/README.md is the contract.
"""
import math, os, sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.varLib.instancer import instantiateVariableFont

SRC, DST = sys.argv[1], sys.argv[2]
SRC_W = float(sys.argv[3]) if len(sys.argv) > 3 else 324.0   # the wght SOURCE.ttf was instanced at
STYLE = sys.argv[4] if len(sys.argv) > 4 else 'Regular'
# 'Italic', 'LightItalic' ... are built from the matching instance of Mulish Italic (see
# "italic" below); the weight is the name before Italic, Regular when there is none.
ITALIC = STYLE.endswith('Italic')
WEIGHT_NAME = (STYLE[:-len('Italic')] if ITALIC else STYLE) or 'Regular'
WEIGHT_CLASS = {'Light': 300, 'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700, 'ExtraBold': 800, 'Black': 900}[WEIGHT_NAME]
P = lambda k, d: float(os.environ.get(k, d))   # tuning knobs, overridable from the shell
font = TTFont(SRC)

# --- italic: the pipeline runs upright ----------------------------------------------
# Mulish Italic is Mulish leaning 9 degrees (ITALIC_K of x per unit of height), with a few
# letters, the figures and the marks corrected by hand; sheared back about y = ITALIC_YC,
# its stems stand exactly where the upright's do. An italic style unslants its source here
# (every outline, component offset and mark anchor), runs everything below as the upright
# does, and is reslanted just before the modules' post phase. A horizontal shear keeps
# every y and every horizontal span (stem widths, crossbars, advances, kerning), so each
# number in this file applies as it is, and the drawn figures, strokes and ligature joins
# lean with the letters once reslanted, as Mulish Italic's own figures and operators do.
# Only the round dots are made circles in the slanted frame (dot(), below), as Mulish
# Italic keeps its bullet and degree sign round.
ITALIC_K = P('ITALIC_K', 0.1587) if ITALIC else 0.0    # the l, I and H stems lean dx/dy 0.1587..0.1590 (9.0 degrees)
ITALIC_YC = P('ITALIC_YC', 252)                        # unslanted about this height, the stems match the upright's x within half a unit
def shear_font(f_, k, anchors=True):
    """Shear f_'s outlines by k per unit of height about y = ITALIC_YC: the simple glyphs'
    points (kept as floats), the composites' offsets and, with anchors, the GPOS mark
    anchors (both rounded, as the tables hold integers); hmtx's left bearings follow."""
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates as _GC
    gl, hm = f_['glyf'], f_['hmtx']
    names = f_.getGlyphOrder()
    for n in names:
        g = gl[n]
        if g.isComposite() or g.numberOfContours <= 0: continue
        g.coordinates = _GC([(x + k * (y - ITALIC_YC), y) for x, y in g.coordinates])
        g.recalcBounds(gl); hm[n] = (hm[n][0], g.xMin)
    for n in names:                    # a component at (dx, dy) raises its glyph by dy, so its offset leans by k * dy
        g = gl[n]
        if not g.isComposite(): continue
        for c in g.components: c.x = round(c.x + k * c.y)
        g.recalcBounds(gl); hm[n] = (hm[n][0], g.xMin)
    if not anchors or 'GPOS' not in f_: return
    def sh(a):
        if a is not None: a.XCoordinate = round(a.XCoordinate + k * (a.YCoordinate - ITALIC_YC))
    for lk in f_['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable:
            if lk.LookupType == 9: st = st.ExtSubTable
            t = getattr(st, 'LookupType', lk.LookupType)
            if t == 4:
                for rec in st.BaseArray.BaseRecord:
                    for a in rec.BaseAnchor: sh(a)
                for rec in st.MarkArray.MarkRecord: sh(rec.MarkAnchor)
            elif t == 5:
                for rec in st.LigatureArray.LigatureAttach:
                    for cr in rec.ComponentRecord:
                        for a in cr.LigatureAnchor: sh(a)
                for rec in st.MarkArray.MarkRecord: sh(rec.MarkAnchor)
            elif t == 6:
                for rec in st.Mark2Array.Mark2Record:
                    for a in rec.Mark2Anchor: sh(a)
                for rec in st.Mark1Array.MarkRecord: sh(rec.MarkAnchor)
if ITALIC: shear_font(font, -ITALIC_K)
glyf, hmtx = font['glyf'], font['hmtx']
gs = font.getGlyphSet()


def path_of(name, dx=0, dy=0, fn=None):
    """Outline of a glyph as a pathops Path, shifted, with an optional point map."""
    p = pathops.Path()
    pen = TransformPen(p.getPen(glyphSet=gs), (1, 0, 0, 1, dx, dy))
    if fn:
        from fontTools.pens.filterPen import FilterPen
        class Map(FilterPen):
            def moveTo(s, pt): s._outPen.moveTo(fn(pt))
            def lineTo(s, pt): s._outPen.lineTo(fn(pt))
            def qCurveTo(s, *pts): s._outPen.qCurveTo(*[fn(q) if q else q for q in pts])
            def curveTo(s, *pts): s._outPen.curveTo(*[fn(q) for q in pts])
        pen = Map(pen)
    gs[name].draw(pen)
    return p


def rect(x0, y0, x1, y1):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return p


def poly(pts):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath()
    return p


def union(*paths):
    out = paths[0]
    for q in paths[1:]: out = pathops.op(out, q, pathops.PathOp.UNION)
    return out


def clip(p, box):
    return pathops.op(p, rect(*box), pathops.PathOp.INTERSECTION)


def band(q0, q1, w):
    """A straight stroke of width w from q0 to q1, its ends cut square."""
    d = unit((q1[0] - q0[0], q1[1] - q0[1])); n = (-d[1] * w / 2, d[0] * w / 2)
    return poly([(q0[0] + n[0], q0[1] + n[1]), (q1[0] + n[0], q1[1] + n[1]), (q1[0] - n[0], q1[1] - n[1]), (q0[0] - n[0], q0[1] - n[1])])


def unit(v, L=1):
    n = math.hypot(*v); return (v[0] / n * L, v[1] / n * L)


def tidy(g):
    """Clean a glyph after rounding to the font grid: drop repeated points, handles that
    sit on or within 2 units of their on-curve point, on-curve points that lie on a straight line between
    their neighbours, and segments under 4 units (a 1-unit spur or a 3-unit step left
    where two shapes met), merging their ends."""
    if g.isComposite() or g.numberOfContours <= 0: return g
    coords, ends, flags = g.coordinates, g.endPtsOfContours, g.flags
    out, s0 = [], 0
    for e in ends:
        c = [(coords[i][0], coords[i][1], bool(flags[i] & 1)) for i in range(s0, e + 1)]; s0 = e + 1
        changed = True
        while changed and len(c) > 3:
            changed = False; n = len(c)
            for i in range(n):
                p, q = c[i], c[(i + 1) % n]
                if (p[0], p[1]) == (q[0], q[1]):                       # repeated point
                    del c[i if (q[2] and not p[2]) else (i + 1) % n]   # keep the on-curve one
                    changed = True; break
                r = c[i - 1]
                if p[2] and r[2] and q[2]:                             # on-curve on a straight line
                    ux, uy, vx, vy = p[0] - r[0], p[1] - r[1], q[0] - p[0], q[1] - p[1]
                    if ux * vx + uy * vy > 0 and abs(math.degrees(math.atan2(ux * vy - uy * vx, ux * vx + uy * vy))) < 0.75:
                        del c[i]; changed = True; break
                if p[2] and q[2] and math.dist(p[:2], q[:2]) < 4:       # tiny line: merge its ends
                    a, b = c[i - 1], c[(i + 2) % n]
                    # keep the end that stays on an axis with its other neighbour, so
                    # horizontal and vertical edges stay straight
                    keep_q = (q[0] == b[0] or q[1] == b[1]) and not (p[0] == a[0] or p[1] == a[1])
                    del c[i if keep_q else (i + 1) % n]; changed = True; break
                if p[2] != q[2] and math.dist(p[:2], q[:2]) < 2:       # a handle on top of its point
                    del c[i if not p[2] else (i + 1) % n]; changed = True; break
                if p[2] and not q[2]:                                  # tiny curve: make it a line
                    t = c[(i + 2) % n]
                    if t[2] and math.dist(p[:2], t[:2]) < 4:
                        del c[(i + 1) % n]; changed = True; break
        out.append(c)
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates as GC
    from array import array
    g.coordinates = GC([(x, y) for c in out for x, y, _ in c])
    g.flags = array('B', [1 if on else 0 for c in out for _, _, on in c])
    g.endPtsOfContours = []; k = -1
    for c in out: k += len(c); g.endPtsOfContours.append(k)
    g.numberOfContours = len(out)
    return g


def add(name, path, width):
    path.simplify()
    tt = TTGlyphPen(None)
    path.draw(Cu2QuPen(tt, 1.0, reverse_direction=True))
    g = tidy(tt.glyph(dropImpliedOnCurves=True)); g.recalcBounds(glyf)
    glyf[name] = g
    hmtx[name] = (int(round(width)), getattr(g, 'xMin', 0))
    font.setGlyphOrder(font.getGlyphOrder() + [name]) if name not in font.getGlyphOrder() else None


W = lambda n: hmtx[n][0]

def ellipse(cx, cy, rx, ry):
    """Closed ellipse from four cubic arcs."""
    k = 0.5523
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo((cx + rx, cy))
    pen.curveTo((cx + rx, cy + k*ry), (cx + k*rx, cy + ry), (cx, cy + ry))
    pen.curveTo((cx - k*rx, cy + ry), (cx - rx, cy + k*ry), (cx - rx, cy))
    pen.curveTo((cx - rx, cy - k*ry), (cx - k*rx, cy - ry), (cx, cy - ry))
    pen.curveTo((cx + k*rx, cy - ry), (cx + rx, cy - k*ry), (cx + rx, cy))
    pen.closePath()
    return p


def diff(a, b):
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE)


def transformed(p, m):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q


def dot(cx, cy, r):
    """A round dot of radius r at (cx, cy): a circle in the font as shipped. The italic is
    drawn here unslanted, so the circle is placed where the reslant will put it and
    sheared back, and comes out round rather than as a leaning oval."""
    if not ITALIC: return ellipse(cx, cy, r, r)
    return transformed(ellipse(cx + ITALIC_K * (cy - ITALIC_YC), cy, r, r), (1, 0, -ITALIC_K, 1, ITALIC_K * ITALIC_YC, 0))


def _distinct(vs, tol):
    """The sorted values vs with each one within tol of the previous kept value dropped."""
    out = []
    for v in vs:
        if not out or v - out[-1] > tol: out.append(v)
    return out


HERE = os.path.dirname(os.path.abspath(__file__))
VAR = os.environ.get('MULISH_VF', os.path.join(HERE, 'mulish', 'Mulish-Italic[wght].ttf' if ITALIC else 'Mulish[wght].ttf'))
_INST = {}
def instance(w):
    """A fresh static instance of variable Mulish at wght w, unslanted in the italic."""
    f_ = instantiateVariableFont(TTFont(VAR), {'wght': w})
    if ITALIC: shear_font(f_, -ITALIC_K, anchors=False)
    return f_
def inst(w):
    if w not in _INST: _INST[w] = instance(w)
    return _INST[w]

# --- weight: every drawn stroke follows the source instance's own strokes ----------
# The numbers below were designed on the wght-324 instance (Regular). Each heavier
# style measures the same features in its own source instance and in the 324 one:
# SV scales vertical strokes (the t stem: 66 at 324), SH horizontal strokes (the T
# bar: 58), SM the minus (53); positions tied to a glyph's geometry move with it.
def _slice(f_, n, box):
    p = pathops.Path(); g_ = f_.getGlyphSet(); g_[n].draw(p.getPen(glyphSet=g_))
    q = pathops.op(p, rect(*box), pathops.PathOp.INTERSECTION)
    return sorted(tuple(round(v) for v in c.bounds) for c in q.contours)
def measure(f_):
    hs = lambda n, y: [(b[0], b[2]) for b in _slice(f_, n, (-3000, y - 0.5, 5000, y + 0.5))]
    vs = lambda n, x: [(b[1], b[3]) for b in _slice(f_, n, (x - 0.5, -3000, x + 0.5, 5000))]
    m = {}
    m['t_l'], m['t_r'] = hs('t', 300)[0]                      # t stem
    m['tbar_lo'], m['tbar_hi'] = vs('t', m['t_r'] + 15)[-1]   # t crossbar
    m['f_l'] = hs('f', 300)[0][0]
    g_ = f_['glyf']['f']; g_.recalcBounds(f_['glyf']); m['f_x'] = g_.xMax
    g_ = f_['glyf']['T']; g_.recalcBounds(f_['glyf']); m['T_x'], m['T_top'] = g_.xMax, g_.yMax
    m['T_sr'] = hs('T', 300)[0][1]                            # T stem's right edge
    m['T_lo'] = vs('T', 50)[-1][0]                            # T bar's underside
    m['h_l'], m['h_r'] = hs('h', 600)[0]                      # h stem
    g_ = f_['glyf']['minus']; g_.recalcBounds(f_['glyf']); m['mn_lo'], m['mn_hi'] = g_.yMin, g_.yMax
    m['four_lo'], m['four_hi'] = vs('four', 200)[0]           # lining 4's crossbar
    m['four_osf_hi'] = vs('four.tosf', 200)[0][1]             # old-style 4's crossbar top
    m['five_lo'], m['five_top'] = vs('five.tosf', 250)[-1]    # old-style 5's top bar
    return m
M, R = measure(inst(SRC_W)), measure(inst(324))
SV = (M['t_r'] - M['t_l']) / (R['t_r'] - R['t_l'])
SH = (M['T_top'] - M['T_lo']) / (R['T_top'] - R['T_lo'])
SM = (M['mn_hi'] - M['mn_lo']) / (R['mn_hi'] - R['mn_lo'])
print(f'{STYLE}: source wght {SRC_W:g}; t stem {M["t_r"] - M["t_l"]} (x{SV:.3f}), T bar {M["T_top"] - M["T_lo"]} (x{SH:.3f}), minus {M["mn_hi"] - M["mn_lo"]} (x{SM:.3f})')



# --- round dots: every square dot becomes a circle ------------------------------
# A dot is any contour that is an axis-aligned square-ish rectangle, 40-130 units a
# side: tittles, period, colon, semicolon, ! ? and their inverted forms, middle dots,
# the dots of divide, and the dieresis / dot-above / dot-below marks (which the
# accented composites use, so those update through their components). Each circle's
# diameter is DOT_K * sqrt(w * h): the i dot (86 x 80) gets r = DOT_R.
DOT_R = P('DOT_R', 44)
DOT_K = 2 * DOT_R / math.sqrt(86 * 80)
def square_dots(name):
    g = glyf[name]
    if g.isComposite() or g.numberOfContours <= 0: return []
    coords, ends, flags = g.getCoordinates(glyf); out = []; s0 = 0
    for e in ends:
        idx = range(s0, e + 1); s0 = e + 1
        xs = sorted({coords[i][0] for i in idx}); ys = sorted({coords[i][1] for i in idx})
        if ITALIC: xs = _distinct(xs, 2.5)         # unslanted, a leaning dot's corners agree to a fraction of a unit
        if len(idx) == 4 and len(xs) == 2 and len(ys) == 2 and all(flags[i] & 1 for i in idx):
            w, h = xs[1] - xs[0], ys[1] - ys[0]
            if 40 * SV <= w <= 130 * SV and 40 * SV <= h <= 130 * SV and 0.75 <= w / h <= 1.33:
                out.append((xs[0], ys[0], xs[1], ys[1]))
    return out
ROUNDED = {}
for name in list(font.getGlyphOrder()):
    dots = square_dots(name)
    if not dots: continue
    body = path_of(name)
    for (x0, y0, x1, y1) in dots:
        body = diff(body, rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2))
    for (x0, y0, x1, y1) in dots:
        r = DOT_K * math.sqrt((x1 - x0) * (y1 - y0)) / 2
        body = union(body, dot((x0 + x1) / 2, (y0 + y1) / 2, r))
        ROUNDED.setdefault(name, []).append(round(r, 1))
    add(name, body, W(name))
print('rounded dots in', len(ROUNDED), 'glyphs; radii', sorted({r for v in ROUNDED.values() for r in v}))

# ===== Round 4: rounder, lower, and the figures Jordan asked for =================
import copy, unicodedata
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables import ttProgram
def EMPTY_PROGRAM():
    pr = ttProgram.Program(); pr.fromBytecode(b''); return pr
GDEF_CLASS = font['GDEF'].table.GlyphClassDef.classDefs
is_mark = lambda n: GDEF_CLASS.get(n) == 3

def side(f_, n):
    """Thickness of the left side of a bowl (outer contour's xMin to the counter's xMin)."""
    p = pathops.Path(); f_.getGlyphSet()[n].draw(p.getPen(glyphSet=f_.getGlyphSet()))
    cs = sorted((c.bounds for c in p.contours), key=lambda b: b[0])
    return cs[1][0] - cs[0][0]

XMAP = {}       # name -> (old xMin, old xMax, new xMin, new xMax), for anchors and composites
def xscale(name, s, ref, src_w=None, target=None):
    """Scale a glyph horizontally by s about its ink centre, keeping the thickness of its
    vertical strokes: x is first interpolated toward a lighter (s > 1) or heavier (s < 1)
    instance of variable Mulish by just the amount that the scaling then undoes; y is
    untouched, so horizontal strokes keep their thickness. Sidebearings stay as they were."""
    src_w = src_w or SRC_W
    wB = src_w - 100 if s > 1 else src_w + 100
    A, B = inst(src_w), inst(wB)
    r = side(B, ref) / side(A, ref)
    k = (1 / s - 1) / (r - 1)
    gA = A['glyf'][name]; ca, _, _ = gA.getCoordinates(A['glyf']); cb, _, _ = B['glyf'][name].getCoordinates(B['glyf'])
    xs = [pa[0] + k * (pb[0] - pa[0]) for pa, pb in zip(ca, cb)]
    cx = (min(xs) + max(xs)) / 2
    xs = [cx + s * (x - cx) for x in xs]
    dst = target or glyf
    old = dst[name] if name in dst.glyphs else gA
    old.recalcBounds(dst if name in dst.glyphs else A['glyf'])
    L = old.xMin; adv = (hmtx[name][0] if target is None else A['hmtx'][name][0]); R = adv - old.xMax
    shift = L - min(xs)
    g = copy.deepcopy(gA)
    g.coordinates = GlyphCoordinates([(round(x + shift), round(p[1])) for x, p in zip(xs, ca)])
    g.program = EMPTY_PROGRAM()
    g.recalcBounds(A['glyf'])
    return g, int(round(L + (g.xMax - g.xMin) + R)), (old.xMin, old.xMax, g.xMin, g.xMax)

def put(name, g, adv):
    glyf[name] = g; hmtx[name] = (adv, g.xMin)

# --- 1. round capitals ~10% wider, round lowercase ~5% wider; 3. v w y z 8% narrower
ROUND_UC = {n: P('ROUND_UC', 1.10) for n in 'O Q C G D'.split()}
ROUND_LC = {n: P('ROUND_LC', 1.05) for n in 'o c e b d p q'.split()}   # Mulish's g is single-storey
NARROW = {n: P('NARROW', 0.92) for n in 'v y z'.split()}
# Round 6: toward Avenir Book's widths (ink / cap height: a 0.562, s 0.511, w 0.980),
# at most about 2% wider. Mulish 324 has a 0.665 (its a is single-storey), s 0.549, w 1.132.
NARROW.update({'w': P('NARROW_W', 0.868), 's': P('NARROW_S', 0.942)})
# round 8: the single-storey a keeps Mulish's width (Jordan: the 0.840 squeeze was far too narrow)
DADV = {}
for table, ref in ((ROUND_UC, 'O'), (ROUND_LC, 'o'), (NARROW, 'o')):
    for n, s in table.items():
        oldadv = hmtx[n][0]
        g, adv, m = xscale(n, s, ref)
        put(n, g, adv); XMAP[n] = m; DADV[n] = adv - oldadv
# round 9: the old-style 0 a touch smaller (ZERO_K of its width here, of its height in
# the figure zone below), stems kept, centred in its 600-unit tabular cell
ZERO_K = P('ZERO_K', 0.93)
gz = glyf['zero.tosf']; gz.recalcBounds(glyf); zc = (gz.xMin + gz.xMax) / 2
g, adv, m = xscale('zero.tosf', ZERO_K, 'zero.tosf')
dz = round(zc - (g.xMin + g.xMax) / 2)
g.coordinates = GlyphCoordinates([(x + dz, y) for x, y in g.coordinates]); g.recalcBounds(glyf)
put('zero.tosf', g, 600)
# composites follow: marks move with the base's ink centre, later bases by its advance
for n in font.getGlyphOrder():
    g = glyf[n]
    if not g.isComposite() or g.components[0].glyphName not in XMAP: continue
    base = g.components[0].glyphName
    ox0, ox1, nx0, nx1 = XMAP[base]
    dc = (nx0 + nx1) / 2 - (ox0 + ox1) / 2
    for c in g.components[1:]:
        c.x += round(dc) if is_mark(c.glyphName) else DADV[base]
    if hmtx[n][0] == hmtx[base][0] - DADV[base] or n.startswith(base):
        hmtx[n] = (hmtx[n][0] + DADV[base], hmtx[n][1])
print('widened/narrowed:', {n: f'{DADV[n]:+d}' for n in DADV})

# --- 2. vertical proportions toward Avenir's -------------------------------------
# Avenir Book: x 0.468, ascender 0.756, cap 0.708 em (ascender / x = 1.62); p and g
# descend to -0.288 and -0.240. Mulish 324: x 0.501, ascender 0.736, cap 0.705 (1.47);
# p and g -0.216 and -0.223. The zones move rigidly, so stems and stroke thicknesses
# stay; only the straight stems and the bowls' sides between the zones get longer or
# shorter.
X0, XH = 500, int(P('XH', 470))       # x-height (flat tops; overshoots move with it)
XD = X0 - XH
AD = int(P('ASC_UP', 14))             # ascenders 736 -> 750
DD = int(P('DESC_DOWN', 20))          # descenders -219 -> -239 (they looked short against 750)
DOT_DY = int(P('DOT_DY', 0))          # i/j dots stay put: top 706, 44 under the ascender
def piecewise(knots):
    def f(y):
        for (a, fa), (b, fb) in zip(knots, knots[1:]):
            if a <= y <= b: return fa + (fb - fa) * (y - a) / (b - a)
        return y
    return f
X_ZONE = [(0, 0), (150, 150), (X0 - 140, X0 - 140 - XD), (X0 + 70, X0 + 70 - XD)]
YL = piecewise([(-3000, -3000 - DD), (-130, -130 - DD), (-40, -40)] + X_ZONE + [(650, 650 + AD), (3000, 3000 + AD)])
YT = piecewise([(-3000, -3000 - DD), (-130, -130 - DD), (-40, -40)] + X_ZONE + [(3000, 3000 - XD)])   # t: its top keeps its height over the x-height (Mulish +160; Avenir +132)
# Old-style figures (round 6): bodies about 1.15 x-height, as in Lato and Avenir Next,
# rather than x-height. Mulish's .tosf top 510 -> FIG_TOP; descenders grow in proportion.
FIG_TOP = int(P('FIG_TOP', 545))
FK = FIG_TOP / round(YL(510))                     # 545 / 480
FIG_DD = round(189 * (FK - 1))                    # -189 -> -215
Z_TOP = round(-9 + ZERO_K * (FIG_TOP + 9))       # the smaller 0's top
def YF4(y):   # the bar (y 0..54 in Mulish's .tosf 4) rises; the stem and its foot stay
    return YF(y + FOUR_UP) if -5 <= y <= M['four_osf_hi'] + 6 else YF(y)
def YF5(y):   # top bar and short stem come down so the top sits at FIVE_TOP; the bowl stays
    k = M['five_lo'] - 7                          # 440 at 324: just under the top bar
    if y <= 300: return YF(y)
    if y >= k: return y - (M['five_top'] - FIVE_TOP)
    a, b = YF(300), k - (M['five_top'] - FIVE_TOP)
    return a + (b - a) * (y - 300) / (k - 300)
YF0 = piecewise([(-3000, -3000), (0, 0), (150, 150), (360, 360 + Z_TOP - 510), (3000, 3000 + Z_TOP - 510)])
FOUR_UP = int(P('FOUR_UP', 35))                  # round 10: the 4's crossbar a touch higher
FIVE_TOP = int(P('FIVE_TOP', XH))                # round 10: the 5's top bar down to the x-height
YF4_ = None; YF5_ = None
YF = piecewise([(-3000, -3000 - FIG_DD), (-120, -120 - FIG_DD), (-40, -40), (0, 0), (150, 150),
                (360, 360 + FIG_TOP - 510), (3000, 3000 + FIG_TOP - 510)])
Y = YL
rev = {v: k for k, v in font.getBestCmap().items()}
def lowercase(n):
    base = n.split('.')[0]
    u = rev.get(base) or rev.get(n)
    return u is not None and unicodedata.category(chr(u)) == 'Ll'
YSET = [n for n in font.getGlyphOrder() if not glyf[n].isComposite() and glyf[n].numberOfContours > 0
        and (lowercase(n) or n in ('fi', 'fl', 'colon', 'semicolon') or n.endswith('.tosf'))
        and not n.endswith('.sc')]
TOPMARKS = [n for n in font.getGlyphOrder() if is_mark(n) and 'case' not in n and not glyf[n].isComposite()
            and glyf[n].numberOfContours > 0 and (glyf[n].recalcBounds(glyf) or glyf[n].yMin >= 450)]
for n in YSET:
    g = glyf[n]; c, ends, _ = g.getCoordinates(glyf); s0 = 0; out = list(c)
    fy = YF0 if n == 'zero.tosf' else YF4 if n == 'four.tosf' else YF5 if n == 'five.tosf' else YF if n.endswith('.tosf') else YT if n.split('.')[0] == 't' else YL
    for e in ends:
        idx = range(s0, e + 1); s0 = e + 1
        ys = [c[i][1] for i in idx]
        rigid = min(ys) >= X0 + 60 and max(ys) <= 760      # i/j dots: move whole
        for i in idx:
            out[i] = (c[i][0], c[i][1] + DOT_DY if rigid else round(fy(c[i][1])))
    g.coordinates = GlyphCoordinates(out)
    g.program = EMPTY_PROGRAM()
    g.recalcBounds(glyf); hmtx[n] = (hmtx[n][0], g.xMin)
for n in TOPMARKS:
    g = glyf[n]; c, _, _ = g.getCoordinates(glyf)
    g.coordinates = GlyphCoordinates([(p[0], p[1] - XD) for p in c]); g.recalcBounds(glyf)
font['OS/2'].sxHeight = XH
print(f'x-height {X0} -> {XH}, ascender 736 -> {736 + AD}, descender -219 -> {-219 - DD}: {len(YSET)} glyphs remapped, {len(TOPMARKS)} top marks lowered')

# GPOS anchors follow the outlines
def fix_anchor(a, glyph, mark=False):
    if a is None: return
    if glyph in XMAP:
        ox0, ox1, nx0, nx1 = XMAP[glyph]
        a.XCoordinate = round(nx0 + (a.XCoordinate - ox0) * (nx1 - nx0) / (ox1 - ox0))
    if glyph in YSET_S: a.YCoordinate = round(Y(a.YCoordinate))
    elif glyph in TOPSET: a.YCoordinate -= XD
YSET_S, TOPSET = set(YSET), set(TOPMARKS)
# composites built on lowercase bases count as lowercase for their anchors
for n in font.getGlyphOrder():
    g = glyf[n]
    if g.isComposite() and g.components[0].glyphName in YSET_S: YSET_S.add(n)
    if g.isComposite() and g.components[0].glyphName in XMAP and n not in XMAP:
        XMAP[n] = XMAP[g.components[0].glyphName]
for lk in font['GPOS'].table.LookupList.Lookup:
    for st in lk.SubTable:
        if lk.LookupType == 4:
            for gn, rec in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                for a in rec.BaseAnchor: fix_anchor(a, gn)
            for gn, rec in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord): fix_anchor(rec.MarkAnchor, gn)
        elif lk.LookupType == 6:
            for gn, rec in zip(st.Mark2Coverage.glyphs, st.Mark2Array.Mark2Record):
                for a in rec.Mark2Anchor: fix_anchor(a, gn)
            for gn, rec in zip(st.Mark1Coverage.glyphs, st.Mark1Array.MarkRecord): fix_anchor(rec.MarkAnchor, gn)
        elif lk.LookupType == 5:
            for gn, rec in zip(st.LigatureCoverage.glyphs, st.LigatureArray.LigatureAttach):
                for comp in rec.ComponentRecord:
                    for a in comp.LigatureAnchor: fix_anchor(a, gn)
            for gn, rec in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord): fix_anchor(rec.MarkAnchor, gn)

def hspans(p, y):
    """Ink of path p along the horizontal line at y, as sorted (x0, x1) intervals."""
    return sorted((c.bounds[0], c.bounds[2]) for c in clip(p, (-3000, y - 0.5, 5000, y + 0.5)).contours)
def vspans(p, x):
    return sorted((c.bounds[1], c.bounds[3]) for c in clip(p, (x - 0.5, -3000, x + 0.5, 5000)).contours)

# --- the e's crossbar: E_BAR of the stem, grown mostly down ------------------------
# Mulish's e bar barely thickens with weight (40 units at Regular, 61 at ExtraBold, 0.61
# and 0.43 of the stem), so at the heavy weights it was thinner than the e's own top
# stroke and pale beside the t bar. It becomes E_BAR times this style's lowercase stem
# (the t stem: 45 at Regular, 96 at ExtraBold, the ExtraBold e's top-stroke thickness),
# never thinner than it was. E_BAR_UP of the added thickness goes up into the eye (its
# floor is cut flat higher up), the rest down into the aperture (the bar's underside is
# moved down, its end following the end's own line, so the italic's leaning end stays
# straight). The accented e's are composites of e and follow; the ss16 ligatures and
# modules draw from e after this. ae, oe and schwa get the same bar on their e (schwa
# turned a half turn, so its bar grows mostly up). Jordan's variant E, 2026-11-06.
E_BAR, E_BAR_UP = P('E_BAR', 0.68), P('E_BAR_UP', 0.3)
LC_STEM = M['t_r'] - M['t_l']
E_BAR_T = round(E_BAR * LC_STEM)
def thicken_ebar(name, turned=False):
    """Bring the bar under the e-eye (the rightmost counter) of name to E_BAR_T units."""
    p = path_of(name); p.simplify()
    b = p.bounds; cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    turn = (-1, 0, 0, -1, 2 * cx, 2 * cy)        # a half turn about the ink centre, its own inverse
    if turned: p = transformed(p, turn)
    cs = list(p.contours)
    inside = lambda u, v: u is not v and v.bounds[0] <= u.bounds[0] and u.bounds[2] <= v.bounds[2] and v.bounds[1] <= u.bounds[1] and u.bounds[3] <= v.bounds[3]
    holes = [c for c in cs if any(inside(c, o) for o in cs)]
    eye = max(holes, key=lambda c: c.bounds[2])
    ex0, ey0, ex1, _ = eye.bounds
    bar = [s for s in vspans(p, (ex0 + ex1) / 2) if abs(s[1] - ey0) < 1.5]
    assert len(bar) == 1, (name, bar)
    lo, hi = bar[0]; cur = round(hi - lo)
    d = max(0, E_BAR_T - cur); up = round(d * E_BAR_UP); down = d - up
    if d:
        assert down < cur, (name, cur, down)
        x0 = ex0 - 20 * SV                       # into the bowl (or the a's or o's side) left of the eye
        r1, r2 = hspans(p, lo + 1)[-1][1], hspans(p, lo + min(15, cur - 2))[-1][1]
        k = (r2 - r1) / (min(15, cur - 2) - 1)   # the bar end's lean, dx per unit of height
        add_ = [poly([(x0, lo + 1), (r1, lo + 1), (r1 - k * (down + 1), lo - down), (x0, lo - down)])]
        if up:
            eyef = pathops.Path(); eye.draw(eyef.getPen()); eyef.simplify()
            add_.append(clip(eyef, (ex0 - 50, ey0 - 5, ex1 + 50, ey0 + up)))
        p = union(p, *add_)
        if turned: p = transformed(p, turn)
        add(name, p, W(name))
    E_BAR_LOG[name] = (cur, cur + d, up, down)
E_BAR_LOG = {}
for n in ('e', 'ae', 'oe'): thicken_ebar(n)
thicken_ebar('uni0259', turned=True)
print(f'e bars (stem {LC_STEM}, target {E_BAR_T}): ' + ', '.join(f'{n} {a} -> {b} (+{u} up, +{d_} down)' for n, (a, b, u, d_) in E_BAR_LOG.items()))

# --- figures: 2, 6, 7, 8, 9 in the old-style sets, 2 in lining --------------------
SIDE, CAP = 67 * SV, 56 * SH            # the rings' sides and caps (Mulish's o at 324: 67 and 55)
FT = round(YF(510))                       # old-style figure top (x-height plus overshoot)
# Past Bold (ExtraBold, Black) the rings' sides grow on into the small counters of the
# 2, 3 and 8; those figures widen by FIG_GROW times the growth of a side beyond Bold's,
# so their counters close at half the rate. Zero up to Bold, whose figures stay as drawn.
HX = 0 if SRC_W <= 675 else 67 * (SV - 119 / 66)
LEGACY = SRC_W in (324, 510, 675) and not ITALIC   # Regular, SemiBold, Bold: outlines kept byte for byte
FIG_GROW = P('FIG_GROW', 1.5)
FGW = FIG_GROW * HX
def ring(cx, y0, y1, w, side=SIDE, cap=CAP):
    rx, ry = w / 2, (y1 - y0) / 2; cy = y0 + ry
    return diff(ellipse(cx, cy, rx, ry), ellipse(cx, cy, rx - side, ry - cap)), (cx, cy, rx - side / 2, ry - cap / 2)
def ring_edges(cx, y0, y1, w, side=SIDE, cap=CAP):
    """The outer and inner ellipses of a ring, as (cx, cy, rx, ry)."""
    rx, ry = w / 2, (y1 - y0) / 2; cy = y0 + ry
    return (cx, cy, rx, ry), (cx, cy, rx - side, ry - cap)
def on_ring(e, deg):
    cx, cy, a, b = e; t = math.radians(deg)
    return (cx + a * math.cos(t), cy + b * math.sin(t)), (-a * math.sin(t), b * math.cos(t))

# Round 12: the strokes that leave a ring (the 2's neck, the 6's and 9's tails) are
# drawn edge by edge. Each edge starts on the ring's own outer or inner ellipse, along
# its tangent there, so the seam is smooth; the ring and stroke are one contour, with no
# overlap for the boolean operations to cut into steps and spurs.
def E_at(el, t): return (el[0] + el[2] * math.cos(t), el[1] + el[3] * math.sin(t))
def E_d(el, t): return (-el[2] * math.sin(t), el[3] * math.cos(t))
def arc_to(pen, el, t0, t1):
    """Elliptical arc from parameter t0 to t1 (radians) as cubics of at most 45 degrees,
    with an on-curve point at every extreme (each multiple of 90 degrees), so the
    glyph's control box is its ink box."""
    lo, hi = min(t0, t1), max(t0, t1)
    cuts = [k * math.pi / 2 for k in range(math.ceil(lo / (math.pi / 2)), math.floor(hi / (math.pi / 2)) + 1)
            if lo + 1e-6 < k * math.pi / 2 < hi - 1e-6]
    knots = [t0] + (cuts if t1 > t0 else cuts[::-1]) + [t1]
    for u0, u1 in zip(knots, knots[1:]):
        _arc_piece(pen, el, u0, u1)
def _arc_piece(pen, el, t0, t1):
    n = max(1, math.ceil(abs(t1 - t0) / (math.pi / 4)))
    for i in range(n):
        a, b = t0 + (t1 - t0) * i / n, t0 + (t1 - t0) * (i + 1) / n
        k = 4 / 3 * math.tan((b - a) / 4)
        pa, pb, da, db = E_at(el, a), E_at(el, b), E_d(el, a), E_d(el, b)
        pen.curveTo((pa[0] + k * da[0], pa[1] + k * da[1]), (pb[0] - k * db[0], pb[1] - k * db[1]), pb)
def bez(c, t):
    u = 1 - t
    return tuple(u**3 * c[0][k] + 3 * u * u * t * c[1][k] + 3 * u * t * t * c[2][k] + t**3 * c[3][k] for k in (0, 1))
def bez_split(c, t):
    """The part of cubic c from t to 1."""
    lerp = lambda p, q: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    a, b, d = lerp(c[0], c[1]), lerp(c[1], c[2]), lerp(c[2], c[3])
    ab, bd = lerp(a, b), lerp(b, d)
    return (lerp(ab, bd), bd, d, c[3])
def stroke_edges(outer, inner, deg, sign, end, end_dir, t0, t1, w1):
    """The two edges of a stroke leaving a ring at parameter angle deg (sign picks the
    direction along the ring) and ending square at `end`, w1 wide, heading along
    end_dir; returns the outer and inner edges as cubics."""
    t = math.radians(deg)
    ao, ai = E_at(outer, t), E_at(inner, t)
    do, di = unit(E_d(outer, t), sign * t0), unit(E_d(inner, t), sign * t0)
    d1 = unit(end_dir); nl = (-d1[1], d1[0])
    left = (do[0] * (ao[1] - ai[1]) - do[1] * (ao[0] - ai[0])) > 0     # the outer edge is left of travel
    h = w1 / 2 if left else -w1 / 2
    eo, ei = (end[0] + nl[0] * h, end[1] + nl[1] * h), (end[0] - nl[0] * h, end[1] - nl[1] * h)
    co = (ao, (ao[0] + do[0], ao[1] + do[1]), (eo[0] - d1[0] * t1, eo[1] - d1[1] * t1), eo)
    ci = (ai, (ai[0] + di[0], ai[1] + di[1]), (ei[0] - d1[0] * t1, ei[1] - d1[1] * t1), ei)
    return co, ci
def bowl_with_tail(outer, inner, deg, sign, end, end_dir, t0, t1, w1):
    """A closed ring with a stroke leaving it (the 6 and the 9): one outer contour that
    runs from the seam round the ring to the crotch, out along the stroke's inner edge,
    across its end and back along its outer edge; the counter is the inner ellipse."""
    co, ci = stroke_edges(outer, inner, deg, sign, end, end_dir, t0, t1, w1)
    f = lambda t: ((bez(ci, t)[0] - outer[0]) / outer[2]) ** 2 + ((bez(ci, t)[1] - outer[1]) / outer[3]) ** 2 - 1
    lo, hi = 0.0, 1.0                                # where the inner edge leaves the ring: the crotch
    for _ in range(60):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    x = bez(ci, hi); tj = math.radians(deg)
    tx = math.atan2((x[1] - outer[1]) / outer[3], (x[0] - outer[0]) / outer[2])
    while -sign * (tx - tj) <= 0: tx -= sign * 2 * math.pi     # round the ring, away from the stroke
    while -sign * (tx - tj) > 2 * math.pi: tx += sign * 2 * math.pi
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo(co[0]); arc_to(pen, outer, tj, tx)
    rest = bez_split(ci, hi); pen.curveTo(rest[1], rest[2], rest[3])
    pen.lineTo(co[3]); pen.curveTo(co[2], co[1], co[0]); pen.closePath()
    return diff(p, ellipse(*inner))

def six_fig(top=P('SIX_TOP', round(1.55 * XH)), bowl_top=None, w=P('SIX_W', 500), cx=300):
    # After Lato's and Avenir Next's old-style 6: a round bowl a little under the figure
    # height; the stroke leaves its upper left along the bowl and rises, almost
    # straight, to a terminal right of centre.
    # Round 9: the bowl stops at the x-height (as in Avenir Next and Lato), and the
    # stroke leaves the bowl's left side and climbs well clear of it, to 1.55 x-height
    # (Avenir Next 1.52, Lato 1.33), ending in a full-weight terminal.
    bowl_top = bowl_top or XH
    o, i = ring_edges(cx, -9, bowl_top, w)
    return bowl_with_tail(o, i, P('SIX_DEG', 162), -1, (cx + P('SIX_TX', 95), top - 31 * SV), (1, P('SIX_SLOPE', 1.3)), 200, 160, 62 * SV)

def nine_fig(bottom=P('NINE_BOT', round(-185 * FK)), w=P('NINE_W', 500), cx=300):
    # After Avenir Next's old-style 9: the bowl sits at the top of the figure (about 4/5
    # of its height); the tail leaves the bowl's right side heading down and curls left,
    # ending below the baseline left of centre.
    bowl_bot = FT - (XH + 9)                                     # the same bowl height as the 6's
    o, i = ring_edges(cx, bowl_bot, FT, w)
    return bowl_with_tail(o, i, 0, -1, (cx - P('NINE_TX', 120), bottom + 31 * SV), (-1, P('NINE_SLOPE', -0.35)), 180, 150, 62 * SV)

def eight_fig(top=P('EIGHT_TOP', round(628 * FK)), w=P('EIGHT_W', 458) + FGW, upper=P('EIGHT_UP', 0.76), cx=300, split=P('EIGHT_SPLIT', 0.5825)):
    # Smaller than Mulish's (which rises to 714), the upper bowl clearly smaller: two
    # rings whose waist strokes coincide, so the waist is one stroke thick.
    lo_top = round(-9 + (top + 9) * split)
    r1, _ = ring(cx, -9, lo_top, w)
    r2, _ = ring(cx, lo_top - CAP, top, w * upper)
    return union(r1, r2)

def mid2(p, q): return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
def bez_d(c, t):
    u = 1 - t
    return tuple(3 * u * u * (c[1][k] - c[0][k]) + 6 * u * t * (c[2][k] - c[1][k]) + 3 * t * t * (c[3][k] - c[2][k]) for k in (0, 1))
def fit_cubic(p0, d0, p3, d3, pts, rounds=6):
    """The cubic from p0 (leaving along d0) to p3 (arriving along d3) whose two handle
    lengths best fit pts in the least-squares sense (chord-length parameters, then
    refined by nearest-point reparametrization).
    Only the points between the two ends are fitted: a point past p3 along d3, or short
    of p0 along d0, lies beyond the curve's own span (the 2's outer neck edge, offset
    square to a diagonal that is cut horizontally, runs on down the diagonal past its
    end by half the stroke over tan(angle), 43 units in the Black superior 2), and
    fitting it pulls the end handle backwards into an S-bend: a notch where the bowl
    turns into the diagonal."""
    pts = [q for q in pts if (q[0] - p3[0]) * d3[0] + (q[1] - p3[1]) * d3[1] < 0
           and (q[0] - p0[0]) * d0[0] + (q[1] - p0[1]) * d0[1] > 0]
    poly_ = [p0] + pts + [p3]
    L = [0.0]
    for q0, q1 in zip(poly_, poly_[1:]): L.append(L[-1] + math.dist(q0, q1))
    ts = [l / L[-1] for l in L[1:-1]]
    for _ in range(rounds):
        # B(t) = A(t) + a * B1(t) d0 - b * B2(t) d3, linear in the handle lengths a and b
        s11 = s12 = s22 = r1 = r2 = 0.0
        for q, t in zip(pts, ts):
            u = 1 - t; b0, b1, b2, b3 = u**3, 3*u*u*t, 3*u*t*t, t**3
            base = ((b0 + b1) * p0[0] + (b2 + b3) * p3[0], (b0 + b1) * p0[1] + (b2 + b3) * p3[1])
            va, vb = (b1 * d0[0], b1 * d0[1]), (-b2 * d3[0], -b2 * d3[1])
            rx, ry = q[0] - base[0], q[1] - base[1]
            s11 += va[0]**2 + va[1]**2; s22 += vb[0]**2 + vb[1]**2; s12 += va[0]*vb[0] + va[1]*vb[1]
            r1 += va[0]*rx + va[1]*ry; r2 += vb[0]*rx + vb[1]*ry
        det = s11 * s22 - s12 * s12
        a_, b_ = (r1 * s22 - r2 * s12) / det, (s11 * r2 - s12 * r1) / det
        hmin = 0.15 * math.dist(p0, p3)                 # handles stay forward: no loop or spur at an end
        if b_ < hmin: b_ = hmin; a_ = max(hmin, (r1 - s12 * b_) / s11)
        elif a_ < hmin: a_ = hmin; b_ = max(hmin, (r2 - s12 * a_) / s22)
        c = (p0, (p0[0] + d0[0] * a_, p0[1] + d0[1] * a_), (p3[0] - d3[0] * b_, p3[1] - d3[1] * b_), p3)
        new = []
        for q, t in zip(pts, ts):                     # one Newton step toward the nearest point
            for _ in range(3):
                bp, bd = bez(c, t), bez_d(c, t)
                t = min(1, max(0, t + ((q[0] - bp[0]) * bd[0] + (q[1] - bp[1]) * bd[1]) / (bd[0]**2 + bd[1]**2)))
            new.append(t)
        ts = new
    return c

def two_fig(top, w, cx, base_w, bx, wt=1.0, dw=0):
    # Round 14 (Jordan: "like Josefin Sans, but pull back ever so slightly on how far
    # around the top part of the two curls inward"): a round head whose arc runs on past
    # its leftmost point and curls back in, ending in a radial cut at TWO_TERM degrees
    # (Josefin Sans curls to about 226); the neck leaves the head's right side nearly
    # upright and sweeps down, convex, to a straight diagonal that lands on the
    # baseline at the base's left end, so the foot's left end is the neck's own edge.
    # Head and neck are one contour, as in round 12. wt scales every stroke (for the
    # small-cap and superior 2s); bx centres the foot, base_w wide.
    head_h = round(w * P('TWO_HEAD', 1.0))
    w += dw                                   # past Bold: wider (FGW), not taller
    cap = CAP * wt
    o, i = ring_edges(cx, top - head_h, top, w, SIDE * wt, cap)
    x0 = bx - base_w / 2
    w1 = 64 * SV * wt
    # The neck's diagonal is the line from the foot's left end that touches the middle
    # of the head's stroke (as Josefin's spine is nearly straight); the neck leaves the
    # head TWO_BOW degrees before that tangent point, so it bows out a little, convex,
    # and never turns back on itself.
    m = (cx, o[1], (o[2] + i[2]) / 2, (o[3] + i[3]) / 2)
    def tangent(th):
        """For a diagonal at angle th: the parameter where the line from its end's middle
        touches m, the first such point below the head's right side, and that line's angle."""
        ls = (cap + w1 / 2) / math.sin(th)
        bm = (x0 + w1 / 2 / math.sin(th) + math.cos(th) * ls, math.sin(th) * ls)
        f = lambda t: (lambda q, v: v[0] * (q[1] - bm[1]) - v[1] * (q[0] - bm[0]))(E_at(m, t), E_d(m, t))
        hi = 0.0
        while f(hi - 0.01) * f(0.0) > 0:
            hi -= 0.01
            if hi < -2 * math.pi: return None    # the end lies inside the head: no tangent (a low head, as the Black Italic small-cap 2's)
        lo = hi - 0.01
        for _ in range(50):
            md = (lo + hi) / 2; lo, hi = (md, hi) if f(md) * f(lo) > 0 else (lo, md)
        q = E_at(m, hi)
        return hi, math.atan2(q[1] - bm[1], q[0] - bm[0])
    a_, b_ = math.radians(20), math.radians(80)                    # the angle that is its own tangent's
    for _ in range(50):
        md = (a_ + b_) / 2; tg = tangent(md)
        a_, b_ = (md, b_) if tg is None or tg[1] > md else (a_, md)   # no tangent: steeper, so the end leaves the head
    th = (a_ + b_) / 2; tg = tangent(th)
    if tg is None: th = b_; tg = tangent(th)
    if tg is None: raise SystemExit(f'two_fig: no neck diagonal touches the head (top {top}, width {w}, base {base_w})')
    hi = tg[0]
    d = (-math.cos(th), -math.sin(th))
    deg, term = math.degrees(hi) + P('TWO_BOW', 20), P('TWO_TERM', 215)
    tj, tt = math.radians(deg), math.radians(term)
    ao, ai = E_at(o, tj), E_at(i, tj)
    do, di = unit(E_d(o, tj)), unit(E_d(i, tj))
    do, di = (-do[0], -do[1]), (-di[0], -di[1])                     # clockwise, down the right side
    # the edges end in straight runs along the diagonal, through the foot to the baseline:
    # the inner edge at the base's left corner, the outer one w1 away across the stroke
    ls = (cap + w1 / 2) / math.sin(th)
    bi, bo = (x0, 0), (x0 + w1 / math.sin(th), 0)
    ei, eo = (bi[0] - d[0] * ls, bi[1] - d[1] * ls), (bo[0] - d[0] * ls, bo[1] - d[1] * ls)
    chord = math.dist(mid2(ao, ai), mid2(ei, eo))
    t0, t1 = P('TWO_T0', 0.30) * chord, P('TWO_T1', 0.40) * chord
    # The neck is drawn about its centre line, a cubic from the middle of the head's
    # stroke to the middle of the diagonal's end; each edge is the cubic, leaving the
    # ring along the ring's own tangent and ending along the diagonal, that best fits
    # the centre line offset by half the stroke (SIDE where it leaves the head, easing
    # to w1 on the diagonal), so the neck's weight stays even.
    w0 = math.dist(ao, ai)
    cm, bm = mid2(ao, ai), mid2(ei, eo)
    dm = unit(mid2(do, di))
    cc = (cm, (cm[0] + dm[0] * t0, cm[1] + dm[1] * t0), (bm[0] - d[0] * t1, bm[1] - d[1] * t1), bm)
    def edge(side, p0, d0, p3):
        pts = []
        for n in range(1, 40):
            t = n / 40; q = bez(cc, t); tg = unit(bez_d(cc, t)); hw = (w0 + (w1 - w0) * t) / 2
            pts.append((q[0] - side * tg[1] * hw, q[1] + side * tg[0] * hw))
        return fit_cubic(p0, d0, p3, d, pts)
    left = (do[0] * (ao[1] - ai[1]) - do[1] * (ao[0] - ai[0])) > 0      # is the outer edge left of travel?
    co = edge(1 if left else -1, ao, do, eo)
    ci = edge(-1 if left else 1, ai, di, ei)
    if wt == 1: TWO_LOG.append((top, round(math.degrees(th), 1), round(deg, 1), [round(min(math.dist(bez(ci, a / 40), bez(co, b / 200)) for b in range(201))) for a in range(0, 41, 4)]))
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo(E_at(o, tt)); arc_to(pen, o, tt, tj)
    pen.curveTo(co[1], co[2], co[3]); pen.lineTo(bo); pen.lineTo(bi); pen.lineTo(ci[3]); pen.curveTo(ci[2], ci[1], ci[0])
    ti = math.atan2(i[2] * math.sin(tt), i[3] * math.cos(tt))          # the inner end on the same radius: a radial cut
    while ti < tj: ti += 2 * math.pi
    arc_to(pen, i, tj, ti); pen.closePath()
    # the foot: cap thick, its left end cut along the neck's diagonal
    return union(p, poly([(x0, 0), (x0 + base_w, 0), (x0 + base_w, cap), (x0 + cap / math.tan(th), cap)]))
TWO_LOG = []

def sector(path, e, a0, a1, R=3000, n=48):
    """Keep the part of `path` seen from the ellipse centre between angles a0 and a1
    (degrees, counter-clockwise)."""
    cx, cy = e[0], e[1]
    pts = [(cx, cy)] + [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                         cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return pathops.op(path, poly(pts), pathops.PathOp.INTERSECTION)

def three_fig(bottom=-189 - FIG_DD, top=None, wl=P('THREE_WL', 456) + FGW, up=P('THREE_UP', 0.86), split=P('THREE_SPLIT', 0.54), cxl=300):
    # After Source Sans 3's old-style 3: a round top, a waist that runs in as a short
    # horizontal from the left, and a lower bowl larger and wider than the upper one.
    top = top or FT
    ywc = bottom + split * (top - bottom)              # centre line of the waist
    rl, el = ring(cxl, bottom, ywc + CAP / 2, wl)
    wu = wl * up
    cxu = cxl + wl / 2 - 22 - wu / 2
    ru, eu = ring(cxu, ywc - CAP / 2, top, wu)
    lower = sector(rl, el, P('THREE_LO_DEG', -150), 90)
    upper = sector(ru, eu, -90, P('THREE_UP_DEG', 150))
    xw = cxu - wu * P('THREE_WAIST', 0.28)
    waist = rect(xw, ywc - CAP / 2, cxu + 5, ywc + CAP / 2)
    return union(lower, upper, waist)

def seven_fig(beak=True, cross=False, src='seven.tosf'):
    p = path_of(src)
    g = glyf[src]; g.recalcBounds(glyf)
    top = g.yMax
    if beak:                       # a short downward serif at the left end of the bar
        p = union(p, rect(g.xMin, top - P('BEAK', 120), g.xMin + 60 * SV, top))
    if cross:
        p = union(p, crossbar(path_of(src), g.yMin, top, descends=src.endswith('tosf')))
    return p

def crossbar(p, ymin, top, descends=False):
    """Round 11: a bar across the 7's diagonal, CROSS_LEN of the top bar's length,
    centred on the diagonal, CROSS_THICK times as thick as the top bar. Round 12
    (Jordan: a little too low): its centre at CROSS_AT of the ink height, from the
    descender's end in the old-style figures and from the baseline in the lining and
    small-cap ones (y 132 -> 213 old-style, 352 -> 398 lining, 242 -> 273 small caps
    in Regular), but leaving at least the top bar's own thickness clear under it (which
    holds the Bold small cap a little lower)."""
    b = p.bounds
    bar_len = b[2] - b[0]                                  # the top bar spans the ink width
    # the top bar's thickness: from the top down to where the slice stops being full width
    t = 0
    while clip(p, (-1000, top - t - 3, 3000, top - t - 1)).bounds[0] <= b[0] + 1: t += 2
    y0 = ymin if descends else max(ymin, 0)
    th = t * P('CROSS_THICK', 1.10)
    yc = min(y0 + P('CROSS_AT', 0.565) * (top - y0), top - 2 * t - th / 2)
    sl = clip(p, (-1000, yc - 2, 3000, yc + 2)).bounds
    xc = (sl[0] + sl[2]) / 2
    # round 11b: longer (CROSS_LEN of the top bar), reaching further left than right as in
    # handwritten European 7s, and CROSS_THICK times the top bar's thickness so it reads
    # at text size; kept inside the top bar's span (the right end gives way first)
    L = bar_len * P('CROSS_LEN', 0.78)
    x0, x1 = xc - L * P('CROSS_LEFT', 0.60), xc + L * (1 - P('CROSS_LEFT', 0.60))
    x1 = min(x1, b[2]); x0 = max(x0, b[0])
    CROSS_LOG.append((round(yc), round(x0), round(x1), round(xc), t, round(th, 1), round(bar_len)))
    return rect(x0, yc - th / 2, x1, yc + th / 2)
CROSS_LOG = []

g4 = glyf['four']; c4, _, _ = g4.getCoordinates(glyf)
g4.coordinates = GlyphCoordinates([(x, y + FOUR_UP if M['four_lo'] - 8 <= y <= M['four_hi'] + 6 else y) for x, y in c4])
g4.program = EMPTY_PROGRAM(); g4.recalcBounds(glyf)
# round 12: Mulish's own figures that keep their outlines are drawn as overlapping
# contours; add() merges them into one outline
for n in ('three', 'four', 'five', 'six', 'nine', 'four.tosf', 'five.tosf'):
    add(n, path_of(n), W(n))
add('three.tosf', three_fig(), 600)
add('six.tosf', six_fig(), 600)
add('nine.tosf', nine_fig(), 600)
add('eight.tosf', eight_fig(), 600)
# round 11: the lining 8's bowls were nearly equal; same construction at cap height
add('eight', eight_fig(top=714, w=500 + FGW), 600)
add('two.tosf', two_fig(FT, P('TWO_W', 360), 290, P('TWO_BASE', 444), 296, dw=FGW), 600)
# round 10: the crossbarred 7 is the default; ss08 gives the plain one (old-style with its beak)
plain7, cross7 = seven_fig(beak=True), seven_fig(beak=False, cross=True)
add('seven.tosf.ss08', plain7, 600); add('seven.tosf', cross7, 600)
add('seven.ss08', path_of('seven'), W('seven'))
add('seven', seven_fig(beak=False, cross=True, src='seven.ss08'), 600)
add('two', two_fig(714 - 9, 440, 290, 500, 300, dw=FGW), 600)          # lining 2, same design at cap height
print('2 neck widths (old-style, lining):', TWO_LOG)

# --- dollar (U+0024): D01 continuous single through-bar ------------------------------
# Mulish's dollar has only disconnected exterior stub prongs at top and bottom, leaving
# the inner counters and diagonal spine empty. D01 draws a full continuous vertical
# through-bar from y = -115 to y = 820, centered on the S body center in unslanted space
# (cx = 310). The bar width follows the continuous source weight law (from 46 at Light
# to 58 at Regular to 127 at Black), overridable via DOLLAR_BAR_W.
# An explicit source-prong witness verifies the donor outline structure and fails if missing.
_pts_top = [p for p in glyf['dollar'].coordinates if p[1] >= 819]
if len(_pts_top) != 2:
    raise RuntimeError(
        f"Missing expected dollar top prong witness in donor font for style {STYLE}: "
        f"expected exactly 2 points at y >= 819, found {len(_pts_top)} ({_pts_top})"
    )
_xs_top = sorted(p[0] for p in _pts_top)
_w_src = _xs_top[1] - _xs_top[0]
if _w_src <= 0:
    raise RuntimeError(
        f"Invalid dollar top prong witness width in donor font for style {STYLE}: {_w_src}"
    )
DOLLAR_BAR_W = P('DOLLAR_BAR_W', _w_src)
DOLLAR_CX = P('DOLLAR_CX', (_xs_top[0] + _xs_top[1]) / 2.0)
_d_bar = rect(DOLLAR_CX - DOLLAR_BAR_W / 2.0, -115, DOLLAR_CX + DOLLAR_BAR_W / 2.0, 820)
add('dollar', union(path_of('dollar'), _d_bar), W('dollar'))

# --- staggered f: everything above the crossbar drops DROP units --------------
# Raleway's first f in f_f tops out at 701 against its f's 740: a 5.2% drop. 5.2% of
# Mulish's 740 is 39.
DROP = P('DROP', 40)
# Points above DROP_Y drop. DROP_Y is Y(560), or lower where the hook's curves start
# below it (in the heavier styles), so a curve never drops apart from its handles.
_fc, _fe, _ff = glyf['f'].getCoordinates(glyf); _fn = len(_fc)
_starts = [_fc[i][1] for i in range(_fn) if _ff[i] & 1 and Y(M['tbar_hi']) < _fc[i][1] <= Y(560)
           and any(not _ff[j] & 1 and _fc[j][1] > _fc[i][1] for j in ((i - 1) % _fn, (i + 1) % _fn))]
DROP_Y = min([Y(560)] + [y - 1 for y in _starts])
short = lambda pt: (pt[0], pt[1] - DROP) if pt[1] > DROP_Y else pt
DX_F = P('DX_F', 230) + (M['f_x'] - M['f_l']) - (R['f_x'] - R['f_l'])   # second stem starts where the short hook ends
ff = union(path_of('f', fn=short), path_of('f', DX_F))
add('f_f', ff, DX_F + W('f'))
add('f_f_i', union(path_of('f', fn=short), path_of('fi', DX_F)), DX_F + W('fi'))
add('f_f_l', union(path_of('f', fn=short), path_of('fl', DX_F)), DX_F + W('fl'))

# --- tt: one crossbar across both stems -----------------------------------------
TB0, TB1 = M['tbar_lo'], M['tbar_hi']        # the t crossbar: 449..501 at 324
add('t_t', union(path_of('t'), path_of('t', W('t') - 20), rect(150, Y(TB0), W('t') + 30, Y(TB1))), 2*W('t') - 20)

# --- Th: h tucked under the right half of the T bar -----------------------------
DX_H = P('DX_H', 490) + (M['T_sr'] - R['T_sr']) - (M['h_l'] - R['h_l'])   # the gap from the T stem to the h stem stays
# The T bar ends at 585. When the h moves further right than DX_H = 437, the bar is
# extended so that it still ends flush with the h stem's right edge (h stem: 82..148).
bar_end = max(M['T_x'], DX_H + M['h_r'])
add('T_h', union(path_of('T'), rect(M['T_x'] - 25, M['T_lo'], bar_end, M['T_top']),
                 clip(path_of('h', DX_H), (0, -50, 2000, M['T_top']))), DX_H + W('h'))

# --- th: the t crossbar runs on into the h stem ----------------------------------
DX_TH = W('t') - 30
add('t_h', union(path_of('t'), path_of('h', DX_TH), rect(150, Y(TB0), DX_TH + 100, Y(TB1))), DX_TH + W('h'))

# --- arrow for -> ------------------------------------------------------------------
y0, y1 = M['mn_lo'], M['mn_hi']                 # the minus stroke (260..313 at 324)
ym = (y0 + y1) / 2
arrow = union(rect(60, y0, 600 - 80 * SM, y1),
              poly([(380, ym - 176.5), (600, ym - 13 * SM), (600, ym + 13 * SM), (380, ym + 176.5),   # round 12: tip points in order (they crossed)
                    (380 - 35 * SM, ym + 176.5 - 38 * SM), (600 - 80 * SM, ym), (380 - 35 * SM, ym - 176.5 + 38 * SM)]))
add('arrowright', arrow, 660)

# --- proportional old-style figures (.osf) ----------------------------------------
# The .tosf outlines with natural sidebearings instead of the 600-unit tabular cell.
DIGITS = 'zero one two three four five six seven eight nine'.split()
SB = {'zero': (48, 48), 'one': (45, 45), 'two': (50, 45), 'three': (42, 48), 'four': (32, 40),
      'five': (50, 45), 'six': (50, 40), 'seven': (40, 30), 'eight': (48, 48), 'nine': (45, 48)}
def proportional(src, dst, d):
    g = glyf[src]; g.recalcBounds(glyf)
    lsb, rsb = SB[d]
    add(dst, path_of(src, lsb - g.xMin), lsb + (g.xMax - g.xMin) + rsb)
for d in DIGITS:
    proportional(d + '.tosf', d + '.osf', d)        # old-style proportional
    proportional(d, d + '.pnum', d)                 # lining proportional (Mulish has none)
proportional('seven.tosf.ss08', 'seven.osf.ss08', 'seven')
proportional('seven.ss08', 'seven.pnum.ss08', 'seven')

# --- small capitals (.sc) ---------------------------------------------------------
# The capitals of a heavier instance of variable Mulish, scaled by SC_SCALE. The
# weight is chosen so the scaled cap stem matches the 66-unit lowercase stem of this
# wght-324 instance (Mulish's T stem is 83 at wght 400, 88 at 450, 93 at 500).
SC_SCALE = P('SC_SCALE', round((XH + 80) / 705, 4))   # 550, 80 over the x-height: acronyms in prose read as capitals (Jordan, Nov 2026; was XH + 14)
SC_STEM = P('SC_STEM', 64) * SV   # target stem after scaling: 2 under the lowercase's 66, since
                              # the caps' diagonals (M, N) set darker than the lowercase at text size
SC_TRACK = P('SC_TRACK', 18)                    # extra sidebearing on each side
def cap_stem(w):
    inst = instance(w)
    c, _, _ = inst['glyf']['T'].getCoordinates(inst['glyf'])
    xs = sorted(p[0] for p in c if p[1] == 0)
    return inst, xs[-1] - xs[0]
lo, hi = SRC_W, min(1000, SRC_W + 376)          # 324..700 for Regular
for _ in range(9):                               # bisect on weight for stem * scale = 66
    mid = (lo + hi) / 2
    _, st = cap_stem(mid)
    lo, hi = (mid, hi) if st * SC_SCALE < SC_STEM else (lo, mid)
SC_WGHT = round((lo + hi) / 2)
sc_font, sc_stem = cap_stem(SC_WGHT)
sc_gs = sc_font.getGlyphSet()
print(f'small caps: wght {SC_WGHT}, cap stem {sc_stem:.1f} -> {sc_stem * SC_SCALE:.1f} at scale {SC_SCALE}, height {705 * SC_SCALE:.0f}')
for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    p = pathops.Path()
    sc_gs[ch].draw(TransformPen(p.getPen(glyphSet=sc_gs), (SC_SCALE, 0, 0, SC_SCALE, SC_TRACK, 0)))
    adv = sc_font['hmtx'][ch][0]
    if ch in ROUND_UC:               # rounder, like the capitals: same stem-keeping x scale
        g, adv, _ = xscale(ch, ROUND_UC[ch], 'O', src_w=SC_WGHT, target=sc_font['glyf'])
        p = pathops.Path()
        g.draw(TransformPen(p.getPen(), (SC_SCALE, 0, 0, SC_SCALE, SC_TRACK, 0)), sc_font['glyf'])
    add(ch + '.sc', p, adv * SC_SCALE + 2 * SC_TRACK)

# round 13: the letters' tracking, half constant and half in proportion to each side.
# A constant SC_TRACK on every side loosened the open sides most: T's 7-unit scaled
# sidebearings more than tripled while H's grew by a quarter, so T stood off from its
# neighbours (Jordan: "the T is too far from the HE"). Each side is now its scaled
# sidebearing times SC_K plus SC_TRACK_C, with SC_K chosen so that H keeps the
# sidebearings it had: straight sides are unchanged, and T, A, V, W, X, Y, the J's
# left and the L's right keep the capitals' proportions to H. Outlines only move.
SC_TRACK_C = P('SC_TRACK_C', 9)
_hb = glyf['H.sc']; _hb.recalcBounds(glyf)
SC_K = (_hb.xMin - SC_TRACK_C) / (_hb.xMin - SC_TRACK)
def sc_respace(name):
    g = glyf[name]; g.recalcBounds(glyf); adv = W(name)
    l, r = g.xMin, adv - g.xMax
    nl, nr = (round((s - SC_TRACK) * SC_K + SC_TRACK_C) for s in (l, r))
    g.coordinates.translate((nl - l, 0)); g.recalcBounds(glyf)
    hmtx[name] = (nl + (g.xMax - g.xMin) + nr, g.xMin)
for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': sc_respace(ch + '.sc')

# ===== Round 7: complete small caps: figures, punctuation, accented letters =========
from fontTools.pens.recordingPen import DecomposingRecordingPen
SC_H = round(705 * SC_SCALE)                         # small-cap height (A.sc top)
def sc_path(name, round_dots=True):
    """A glyph of the heavier instance, decomposed, its square dots made round (as in
    round 2-3), scaled to small-cap size and tracked like the letters."""
    rec = DecomposingRecordingPen(sc_gs); sc_gs[name].draw(rec)
    p = pathops.Path(); pen = TransformPen(p.getPen(), (SC_SCALE, 0, 0, SC_SCALE, SC_TRACK, 0))
    contour = []
    def flush():
        pts = [a[0] for op, a in contour if op in ('moveTo', 'lineTo')]
        ops = [op for op, a in contour]
        xs, ys = sorted({q[0] for q in pts}), sorted({q[1] for q in pts})
        if ITALIC: xs = _distinct(xs, 2.5)
        if (round_dots and set(ops) <= {'moveTo', 'lineTo', 'closePath'} and len(pts) == 4 and len(xs) == 2 and len(ys) == 2
                and 40 * SV <= xs[1] - xs[0] <= 140 * SV and 40 * SV <= ys[1] - ys[0] <= 140 * SV and 0.75 <= (xs[1] - xs[0]) / (ys[1] - ys[0]) <= 1.33):
            r = DOT_K * math.sqrt((xs[1] - xs[0]) * (ys[1] - ys[0])) / 2
            if ITALIC:                 # a circle once reslanted: drawn at small-cap size in this frame, not through the scaling pen
                dot(SC_SCALE * (xs[0] + xs[1]) / 2 + SC_TRACK, SC_SCALE * (ys[0] + ys[1]) / 2, SC_SCALE * r).draw(p.getPen())
            else:
                ellipse((xs[0] + xs[1]) / 2, (ys[0] + ys[1]) / 2, r, r).draw(pen)
        else:
            for op, a in contour: getattr(pen, op)(*a)
        contour.clear()
    for op, a in rec.value:
        contour.append((op, a))
        if op in ('closePath', 'endPath'): flush()
    return p
SC_EXTRA = []                                        # (lowercase-or-None, capital-or-source, sc name)

# figures: lining figures of the heavier instance at small-cap height, proportional
for d in DIGITS:
    p = sc_path(d)
    b = p.bounds; lsb, rsb = SB[d]
    p = transformed(p, (1, 0, 0, 1, lsb * SC_SCALE + SC_TRACK - b[0], 0))
    add(d + '.sc', p, (b[2] - b[0]) + (lsb + rsb) * SC_SCALE + 2 * SC_TRACK)

# Round 14: the small-cap 2 and the 2 that the superiors, inferiors, numerators and
# denominators share (two.dnom; two.numr, uni00B2, uni2082 and onehalf are composites of
# it) in the lining 2's design: the same proportions in each glyph's own ink box and
# advance, its top at its own 1's height (as the lining 2's is at the 1's), its strokes
# scaled by its 1's stem against the lining 1's.
def stem_at(n, y=200):
    b = clip(path_of(n), (-1000, y - 0.5, 3000, y + 0.5)).bounds; return b[2] - b[0]
def small_two(name, one):
    g = glyf[name]; g.recalcBounds(glyf); go = glyf[one]; go.recalcBounds(glyf)
    iw, k = g.xMax - g.xMin, (g.xMax - g.xMin) / 500
    wt = stem_at(one) / stem_at('one')
    # its strokes are not scaled down with it, so the head widens by the extra stroke
    # on each side (keeping the counter in proportion), up to P('TWO_SMALL_MAX') of the foot
    w = min(440 * k + 2 * SIDE * (wt - k), P('TWO_SMALL_MAX', 0.94) * iw)
    dw = FGW * wt                             # past Bold: the head widens, mostly leftward, so the neck keeps its run
    p = two_fig(go.yMax, w, g.xMin + iw / 2 - 10 * k - dw * 0.35, iw, g.xMin + iw / 2, wt, dw=dw)
    add(name, p, W(name))
small_two('two.sc', 'one.sc')
small_two('two.dnom', 'one.dnom')

# Round 15: the inferiors hang below the baseline (Jordan, Nov 2026: "drop it by just a
# hair less than a third of the x-height"). Mulish's inferior figures U+2080-2089 stood on
# the baseline, so x₁ read as a small 1 on the line; they drop by SUB_DROP, 0.31 of the
# x-height (146 at 470; a third would be 157). It is the one number for every inferior:
# supsub's inferior letters and signs stand on the inferior figures' baseline and
# otfeatures' slashed inferior zero is drawn from uni2080, so both follow. Italics drop
# along the slant, as Mulish Italic raises its superiors (the shift is made upright and
# reslanted with everything else).
SUB_DROP = round(P('SUB_DROP_K', 0.31) * XH)
for _u in range(0x2080, 0x208A):
    _g = glyf[font.getBestCmap()[_u]]
    if _g.isComposite():
        for _c in _g.components: _c.y -= SUB_DROP
    else:
        _g.coordinates = GlyphCoordinates([(x, y - SUB_DROP) for x, y in _g.coordinates])
    _g.recalcBounds(glyf)
print(f'inferior figures: lowered {SUB_DROP} ({SUB_DROP / XH:.3f} of the x-height {XH})')
add('seven.sc.ss08', path_of('seven.sc'), W('seven.sc'))
sc7 = path_of('seven.sc')
add('seven.sc', union(sc7, crossbar(sc7, sc7.bounds[1], sc7.bounds[3])), W('seven.sc'))

# punctuation and symbols drawn from the heavier instance, scaled like the letters
SC_PUNCT = 'exclam question exclamdown questiondown ampersand percent perthousand numbersign at slash backslash parenleft parenright bracketleft bracketright braceleft braceright multiply'.split()
for n in SC_PUNCT:
    add(n + '.sc', sc_path(n), sc_font['hmtx'][n][0] * SC_SCALE + 2 * SC_TRACK)
# dashes keep their weight and length, centred on the small-cap height instead
for n in ('hyphen', 'endash', 'emdash'):
    g = glyf[n]; g.recalcBounds(glyf)
    add(n + '.sc', path_of(n, 0, round(SC_H / 2 - (g.yMin + g.yMax) / 2)), W(n))
# quotes and apostrophe hang from the cap height; these hang from the small-cap height
for n in ('quotesingle', 'quotedbl', 'quoteleft', 'quoteright', 'quotedblleft', 'quotedblright'):
    add(n + '.sc', path_of(n, 0, SC_H - 705), W(n))
# round 7.1: tabular small-cap figures, all one width, each centred in it
SC_TF_W = round(max(W(d + '.sc') for d in DIGITS))
for d in DIGITS + ['seven.sc.ss08']:
    src = d if d.endswith('ss08') else d + '.sc'
    dst = 'seven.sc.tf.ss08' if d.endswith('ss08') else d + '.sc.tf'
    b = path_of(src).bounds
    add(dst, path_of(src, round((SC_TF_W - (b[2] - b[0])) / 2 - b[0])), SC_TF_W)
SC_SYMBOLS = SC_PUNCT + ['hyphen', 'endash', 'emdash', 'quotesingle', 'quotedbl', 'quoteleft', 'quoteright', 'quotedblleft', 'quotedblright']

# accented letters: composites of the .sc base and the lowercase-height marks, raised
# from the x-height to the small-cap height; overlays (Ł, Đ) and simple glyphs (Ø, Æ,
# Œ, Þ ...) are drawn from the heavier instance like the plain letters.
cmap_ = font.getBestCmap()
def ink(n):
    g = glyf[n]; g.recalcBounds(glyf); return g.xMin, g.xMax
SC_ACC = []                                          # (lowercase glyph or None, capital glyph, sc glyph)
def mark_anchor_x(name):
    """x of Mulish's mark anchor on a combining mark (0 when it has none): where the mark's
    origin sits against the anchor of the base it attaches to."""
    for lk in font['GPOS'].table.LookupList.Lookup:
        if lk.LookupType != 4: continue
        for st in lk.SubTable:
            if name in st.MarkCoverage.glyphs:
                return st.MarkArray.MarkRecord[st.MarkCoverage.glyphs.index(name)].MarkAnchor.XCoordinate
    return 0
for u in list(range(0xC0, 0x100)) + list(range(0x100, 0x250)) + list(range(0x1E00, 0x1F00)):   # Latin-1, Extended-A and -B, Extended Additional
    ch = chr(u)
    if not (ch.isupper() and unicodedata.category(ch) == 'Lu') or ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': continue
    if u == 0x1E9E: continue                         # capital sharp s: mapped to germandbls.sc below
    if 0x1C4 <= u <= 0x1CC: continue                 # DŽ LJ NJ digraphs: mapped to letter sequences below
    cap = cmap_.get(u)
    if not cap or cap + '.sc' in glyf.glyphs: continue
    low = cmap_.get(ord(ch.lower())) if len(ch.lower()) == 1 else None
    if low == cap: low = None
    g = glyf[cap]; name = cap + '.sc'; built = False
    if g.isComposite() and g.components[0].glyphName + '.sc' in glyf.glyphs:
        base = g.components[0].glyphName
        cx0, cx1 = ink(base); sx0, sx1 = ink(base + '.sc')
        comps = []
        for c in g.components[1:]:
            m = c.glyphName.split('.case')[0]
            if m not in glyf.glyphs: break
            mg = glyf[m]; mg.recalcBounds(glyf)
            if mg.yMin >= 300: dy = SC_H - XH          # top mark: from the x-height to the small-cap height
            elif mg.yMax <= 60: dy = 0                 # bottom mark (cedilla, ogonek, comma below)
            else: break                                # an overlay: draw the letter instead
            x_sc = round((sx0 + sx1) / 2 + (c.x - (cx0 + cx1) / 2) * SC_SCALE)
            if ITALIC:
                # Mulish Italic anchors its plain grave 35 units from its .case grave (its other
                # marks agree with their .case forms, as all the upright's do). The small cap takes
                # the plain mark, so it goes where the anchors put it, as base + mark does: the
                # capital's anchor (its offset plus the .case mark's anchor), scaled, less the
                # plain mark's own anchor.
                x_sc = round((sx0 + sx1) / 2 + (c.x + mark_anchor_x(c.glyphName) - (cx0 + cx1) / 2) * SC_SCALE - mark_anchor_x(m))
            comps.append((m, x_sc, dy + round(c.y * SC_SCALE)))
        else:
            from fontTools.ttLib.tables._g_l_y_f import GlyphComponent, Glyph
            new = Glyph(); new.numberOfContours = -1; new.components = []
            for gn, x, y in [(base + '.sc', 0, 0)] + comps:
                gc = GlyphComponent(); gc.glyphName, gc.x, gc.y, gc.flags = gn, x, y, 0x4
                new.components.append(gc)
            glyf[name] = new; hmtx[name] = (W(base + '.sc'), 0)
            if name not in font.getGlyphOrder(): font.setGlyphOrder(font.getGlyphOrder() + [name])
            new.recalcBounds(glyf); hmtx[name] = (W(base + '.sc'), new.xMin)
            built = True
    if not built:
        if cap not in sc_gs: continue
        add(name, sc_path(cap), sc_font['hmtx'][cap][0] * SC_SCALE + 2 * SC_TRACK); sc_respace(name)
    SC_ACC.append((low, cap, name))
# round 7.1: letters with no capital of their own. ß -> SS (its Unicode uppercase),
# dotless i -> I, kra -> K, and n-apostrophe -> apostrophe + N, as composites.
from fontTools.ttLib.tables._g_l_y_f import GlyphComponent, Glyph
def sc_composite(name, parts):
    new = Glyph(); new.numberOfContours = -1; new.components = []; x = 0
    for gn in parts:
        gc = GlyphComponent(); gc.glyphName, gc.x, gc.y, gc.flags = gn, x, 0, 0x4
        new.components.append(gc); x += W(gn)
    glyf[name] = new
    if name not in font.getGlyphOrder(): font.setGlyphOrder(font.getGlyphOrder() + [name])
    new.recalcBounds(glyf); hmtx[name] = (x, new.xMin)
sc_composite('germandbls.sc', ['S.sc', 'S.sc'])
sc_composite('napostrophe.sc', ['quoteright.sc', 'N.sc'])
# round 7.2: lowercase letters whose capital Mulish lacks (so the c2sc-driven loop
# above never saw them): build the small cap from the lowercase composite instead.
def sc_from_lower(low, base_sc):
    g = glyf[low]; base = g.components[0].glyphName
    lx0, lx1 = ink(base); sx0, sx1 = ink(base_sc)
    new = Glyph(); new.numberOfContours = -1; new.components = []
    gc = GlyphComponent(); gc.glyphName, gc.x, gc.y, gc.flags = base_sc, 0, 0, 0x4; new.components.append(gc)
    for c in g.components[1:]:
        m = c.glyphName.split('.case')[0]
        gc = GlyphComponent(); gc.glyphName = m; gc.flags = 0x4
        gc.x = round((sx0 + sx1) / 2 + (c.x - (lx0 + lx1) / 2)); gc.y = SC_H - XH
        new.components.append(gc)
    name = low + '.sc'; glyf[name] = new
    if name not in font.getGlyphOrder(): font.setGlyphOrder(font.getGlyphOrder() + [name])
    new.recalcBounds(glyf); hmtx[name] = (W(base_sc), new.xMin)
    return name
SC_LX_MORE = [(low, sc_from_lower(low, b)) for low, b in (('uni01D4', 'U.sc'), ('uni01E9', 'K.sc'), ('uni021F', 'H.sc'), ('uni1E97', 'T.sc')) if low in glyf.glyphs]
# g with stroke: a small-cap G with a bar across its right side
gb = path_of('G.sc').bounds
add('uni01E5.sc', union(path_of('G.sc'), rect(gb[2] - 120, round(SC_H * 0.22), gb[2] + 40, round(SC_H * 0.22) + 48 * SH)), W('G.sc') + 40)
SC_LX_MORE += [('uni01E5', 'uni01E5.sc'), ('uni0237', 'J.sc')]
SC_UX = [(n, 'germandbls.sc') for n in ('uni1E9E',) if n in glyf.glyphs]   # capital sharp s
SC_LX = [(n, s) for n, s in (('germandbls', 'germandbls.sc'), ('dotlessi', 'I.sc'), ('kgreenlandic', 'K.sc'), ('napostrophe', 'napostrophe.sc')) if n in glyf.glyphs] + SC_LX_MORE
print(f'small caps: {len(DIGITS)} figures, {len(SC_SYMBOLS)} punctuation and symbols, {len(SC_ACC)} accented letters (height {SC_H})')

# ===== Round 5: alternates as stylistic sets (all off by default) ===================
ALT_FEA = ''
def alt_composites(base, alt):
    """Accented forms of an alternate: clone each composite built on `base`, swap in
    `alt`, and move its marks by the change in the ink centre."""
    gb = glyf[base]; gb.recalcBounds(glyf); ga = glyf[alt]; ga.recalcBounds(glyf)
    dc = round((ga.xMin + ga.xMax) / 2 - (gb.xMin + gb.xMax) / 2)
    pairs = [(base, alt)]
    for n in list(font.getGlyphOrder()):
        g = glyf[n]
        if not g.isComposite() or g.components[0].glyphName != base or '.' in n: continue
        new = copy.deepcopy(g); new.components[0].glyphName = alt
        for c in new.components[1:]: c.x += dc
        name = n + '.' + alt.split('.')[1]
        glyf[name] = new; hmtx[name] = (hmtx[alt][0], hmtx[n][1])
        if name not in font.getGlyphOrder(): font.setGlyphOrder(font.getGlyphOrder() + [name])
        pairs.append((n, name))
    return pairs
def ss(tag, pairs):
    global ALT_FEA
    ALT_FEA += f"feature {tag} {{ sub [{' '.join(a for a, _ in pairs)}] by [{' '.join(b for _, b in pairs)}]; }} {tag};\n"

# ss04: Mulish's default a is already single-storey (like Futura's); the alternate is a
# two-storey a, as in Avenir. A bowl under an arch, both rings in Mulish's stroke.
# Heavier styles widen the letter by the growth of a stroke (DW), so the counters
# keep room, and set the bowl's top where the two counters stay equal in height.
DW = SIDE - 67
A_STEM_R = P('A_STEM_R', 448) + DW
cxa = P('A_ARCH_CX', 262) + DW / 2
arch, ea = ring(cxa, round(XH * 0.36), XH + 10, 2 * (A_STEM_R - cxa))
arch = sector(arch, ea, 0, P('A_ARCH_TERM', 152))
# The bowl is open on the right: its top runs straight into the stem as a horizontal,
# and its lower curve meets the stem near the baseline.
bcx, btop = P('A_BOWL_CX', 236) + DW / 2, round(XH * P('A_BOWL_H', 0.56) + (CAP - 56) / 2)
bowl, eb = ring(bcx, -9, btop, P('A_BOWL_W', 316) + DW)
bowl = sector(bowl, eb, 90, 340)
bar = rect(bcx - 2, btop - CAP, A_STEM_R - 30, btop)
stem = rect(A_STEM_R - 66 * SV, 0, A_STEM_R, ea[1] + 2)
add('a.ss04', union(arch, bowl, bar, stem), A_STEM_R + 46)
ss('ss04', alt_composites('a', 'a.ss04'))

# ss05: a Q whose straight tail crosses the bowl.
ob = path_of('O').bounds
qx0, qy0 = ob[0] + (ob[2] - ob[0]) * P('Q_START_X', 0.60), ob[1] + (ob[3] - ob[1]) * P('Q_START_Y', 0.30)
qx1, qy1 = ob[0] + (ob[2] - ob[0]) * P('Q_END_X', 1.02), P('Q_END_Y', -120)
tailq = band((qx0, qy0), (qx1, qy1), 62 * SV)
add('Q.ss05', union(path_of('O'), tailq), max(W('O'), round(qx1 + 20)))
ss('ss05', [('Q', 'Q.ss05')])

# ss06: a y whose right stroke runs straight on to the descender, with no hook.
vc, _, _ = glyf['v'].getCoordinates(glyf); vc = list(vc)
outer_top = max((p for p in vc if p[1] == max(q[1] for q in vc)), key=lambda p: p[0])
bottom_r = max((p for p in vc if p[1] == 0), key=lambda p: p[0])
slope = (outer_top[0] - bottom_r[0]) / (outer_top[1] - bottom_r[1])        # dx per dy
inner_x0 = min(p[0] for p in vc if p[1] > 0 and p[1] < 100 * SV and p[0] > (bottom_r[0] - 80 * SV))
thick = bottom_r[0] - (inner_x0 - slope * min(p[1] for p in vc if p[1] > 0))
DESC = -219 - DD
xo = bottom_r[0] + slope * DESC
add('y.ss06', union(path_of('v'), poly([(bottom_r[0], 0), (xo, DESC), (xo - thick, DESC), (bottom_r[0] - thick, 0)])), W('v'))
ss('ss06', alt_composites('y', 'y.ss06'))

# ss07: Mulish's t already has a slight slant at the top (21 units over the 66-unit stem);
# this one is cut steeply, rising to the right.
tc, _, _ = glyf['t'].getCoordinates(glyf)
t_top = max(p[1] for p in tc)
above = [p[0] for p in tc if p[1] > YL(TB1) + 5]   # the stem above the crossbar
stem_l = min(above); SW = max(above) - stem_l       # 106 and 66 at 324
SLANT = P('T_SLANT', 60) * SW / 66                  # the same angle at every weight
cut_y = lambda x: t_top - SLANT + (x - stem_l) * SLANT / SW
t_alt = union(path_of('t'), rect(stem_l, YL(TB0), stem_l + SW, t_top))
t_alt = pathops.op(t_alt, poly([(-200, -500), (2000, -500), (2000, cut_y(2000)), (-200, cut_y(-200))]), pathops.PathOp.INTERSECTION)
add('t.ss07', t_alt, W('t'))
add('t_t.ss07', union(path_of('t.ss07'), path_of('t.ss07', W('t') - 20), rect(150, YL(TB0), W('t') + 30, YL(TB1))), 2*W('t') - 20)
add('t_h.ss07', union(path_of('t.ss07'), path_of('h', DX_TH), rect(150, YL(TB0), DX_TH + 100, YL(TB1))), DX_TH + W('h'))
ss('ss07', alt_composites('t', 't.ss07') + [('t_t', 't_t.ss07'), ('t_h', 't_h.ss07')])
print('alternates: ss04 a (two-storey), ss05 Q, ss06 y, ss07 t')

print(f'7 crossbars (yc, x0, x1, diagonal centre, top-bar thickness, bar thickness, top-bar length):', CROSS_LOG)

# ===== Round 13: ss16, the Torchlette prose ligatures ===============================
# The proposals Jordan kept from the two ligature labs (ids 1-124, then 125-207), drawn here at
# every weight. Each one is assembled from this style's own outlines: the crossbars,
# arms, stems and terminals it joins are measured on the glyphs above, so the joins
# stay flush as the strokes grow, and its own strokes take the width of the strokes
# they continue. Letters are placed by Mulish's kerned spacing at this weight plus the
# lab's offset (the lab drew them on Regular, so each offset is the lab position less
# the kerned one there). All sit in ss16; ids up to 99 are also reachable alone through
# cvNN. Glyph names are the lab's, so its tests read the same.
S16 = {}                                   # lab id -> the glyphs it adds
def s16_add(id_, name, path, width, uni=None):
    add(name, path, width); S16.setdefault(id_, []).append(name)
    if uni:
        for t in font['cmap'].tables:
            if t.isUnicode(): t.cmap[uni] = name
def s16_raw(id_, name, draw, width):
    """A glyph written straight to TrueType points (the round-capped spark-line strokes)."""
    tt = TTGlyphPen(None); draw(tt)
    g = tidy(tt.glyph()); g.recalcBounds(glyf)
    glyf[name] = g; hmtx[name] = (int(round(width)), getattr(g, 'xMin', 0))
    if name not in font.getGlyphOrder(): font.setGlyphOrder(font.getGlyphOrder() + [name])
    S16.setdefault(id_, []).append(name)
def mid(s): return (s[0] + s[1]) / 2
def mv(p, dx, dy=0): return transformed(p, (1, 0, 0, 1, dx, dy))
def mirror(p, axis): return transformed(p, (-1, 0, 0, 1, 2 * axis, 0))
def oncurve(n):
    c, _, fl = glyf[n].getCoordinates(glyf)
    return [tuple(q) for q, f_ in zip(c, fl) if f_ & 1], [tuple(q) for q in c]
def stroke_line(pts, w, limit=40):
    p = pathops.Path(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.endPath()
    p.stroke(w, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, limit); p.simplify()
    return p
def rrect(x0, y0, x1, y1, r):
    """Rounded rectangle: one contour of lines and quarter arcs."""
    p = pathops.Path(); pen = p.getPen(); k = 0.5523 * r
    pen.moveTo((x0 + r, y0)); pen.lineTo((x1 - r, y0))
    pen.curveTo((x1 - r + k, y0), (x1, y0 + r - k), (x1, y0 + r)); pen.lineTo((x1, y1 - r))
    pen.curveTo((x1, y1 - r + k), (x1 - r + k, y1), (x1 - r, y1)); pen.lineTo((x0 + r, y1))
    pen.curveTo((x0 + r - k, y1), (x0, y1 - r + k), (x0, y1 - r)); pen.lineTo((x0, y0 + r))
    pen.curveTo((x0, y0 + r - k), (x0 + r - k, y0), (x0 + r, y0)); pen.closePath()
    return p

# Mulish's kerning (GPOS kern, pair adjustments), so a ligature's letters sit where
# shaping would put them.
_GPOS = font['GPOS'].table
KERN_LOOKUPS = [_GPOS.LookupList.Lookup[i] for i in sorted({i for fr in _GPOS.FeatureList.FeatureRecord
                if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex})]
def kern(a, b):
    total = 0
    for lk in KERN_LOOKUPS:
        for st in lk.SubTable:
            if lk.LookupType == 9: st = st.ExtSubTable
            cov = st.Coverage.glyphs
            if a not in cov: continue
            if st.Format == 1:
                rec = next((r for r in st.PairSet[cov.index(a)].PairValueRecord if r.SecondGlyph == b), None)
                if rec is None: continue
                v = rec.Value1
            else:
                v = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)].Class2Record[st.ClassDef2.classDefs.get(b, 0)].Value1
            total += (getattr(v, 'XAdvance', 0) or 0) if v else 0
            break
    return total
def setting(seq):
    """Glyphs set in a row with Mulish's kerning: [(glyph, x)], total advance."""
    out, x = [], 0
    for i, n in enumerate(seq):
        out.append((n, x)); x += W(n) + (kern(n, seq[i + 1]) if i + 1 < len(seq) else 0)
    return out, x
def kerned(a, b): return W(a) + kern(a, b)
def word_paths(items): return union(*[path_of(n, x) for n, x in items])

# --- what the joins meet, measured on this style's outlines -----------------------
_tp = path_of('t')
T_STEM = hspans(_tp, 300)[0]                               # t stem: 106..172 at Regular
XB0, XB1 = vspans(_tp, (_tp.bounds[0] + T_STEM[0]) / 2)[-1]   # t and f crossbar: 419..471
XBM, XBW = (XB0 + XB1) / 2, XB1 - XB0
TBAR_L, TBAR_R = hspans(_tp, XBM)[0][0], hspans(_tp, XBM)[-1][1]   # the crossbar's ends: 7, 319
def arm(n, y=XBM, k=0): return mid(hspans(path_of(n), y)[k])     # middle of the k-th stroke at y
# the f's hook: its top (an on-curve extreme) and its underside's highest point
_fon, _fall = oncurve('f')
F_TOP = max(y for x, y in _fon); F_PEAK = max(x for x, y in _fon if y == F_TOP)            # 754 at 264
X_IN, F_IN = max(((x, y) for x, y in _fon if F_PEAK < x < max(q[0] for q in _fall) and 550 < y < F_TOP - 20),
                 key=lambda q: q[1])                                                           # 697 at 272
# the r's arm at its terminal: top and underside extremes
_ron, _ = oncurve('r')
R_TOP = max(y for x, y in _ron); R_TX = max(x for x, y in _ron if y == R_TOP)                 # 480 at 300
R_WIN = 120 if SRC_W <= 675 else 120 * SH / (101 / 58)      # past Bold, the arm's underside sits lower in proportion
R_UX, R_UND = max(((x, y) for x, y in _ron if x > 200 and R_TOP - R_WIN < y < R_TOP - 20), key=lambda q: q[1])   # 422 at 293
print(f'ss16 measures: crossbar {XB0:g}..{XB1:g}, f hook top {F_TOP} at {F_PEAK}, underside {F_IN} at {X_IN}, '
      f'r arm {R_UND}..{R_TOP} at {R_UX}/{R_TX}')

def terminal_run(p, x_top, y_top, x_und, y_und, x_end, below=None, below_x=None):
    """Run a stroke that ends in a terminal on flat to x_end: the stroke's top edge
    leaves at its highest point (x_top, y_top) and its underside at its own highest
    point (x_und, y_und), both level there, so the joins stay smooth. Ink below the
    height `below` is cut at below_x."""
    ym = (y_top + y_und) / 2
    parts = [clip(p, (-500, below if below is not None else -500, x_und + 1, ym)), clip(p, (-500, ym, x_top + 1, 1000)),
             rect(x_top, ym, x_end, y_top), rect(x_und, y_und, x_end, ym + 1)]
    if below is not None: parts.append(clip(p, (-500, -500, below_x, below)))
    if not LEGACY:             # one cut through the kept region, so its inner edges split no curve (3-degree kinks)
        keep = union(*[rect(-500, below if below is not None else -500, x_und + 1, ym), rect(-500, ym, x_top + 1, 1000)]
                     + ([rect(-500, -500, below_x, below)] if below is not None else []))
        return union(pathops.op(p, keep, pathops.PathOp.INTERSECTION), *parts[2:4])
    return union(*parts)

# --- f, t, r and l families (lab G1) ---------------------------------------------
# 1-3: the f's hook flattens into a roof that lands on the next ascender; the f's
# crossbar stops under the roof's start, as in the lab.
def froof(nxt, off):
    dx = kerned('f', nxt) + off
    sr = hspans(path_of(nxt), F_TOP - 14)[0][1]            # the ascender stem's right edge near its top
    roof = terminal_run(path_of('f'), F_PEAK, F_TOP, X_IN, F_IN, dx + sr, below=600 if F_IN > 620 else F_IN - 40, below_x=F_PEAK + 1)   # Black's underside: 602
    return union(roof, path_of(nxt, dx)), dx + W(nxt)
for id_, n in ((1, 'b'), (2, 'h'), (3, 'k')):
    p, w = froof(n, -6); s16_add(id_, 'f_' + n, p, w)
# 4 fj: the f's crossbar runs on across the j stem, as in Mulish's fi
dx = kerned('f', 'j') - 8
s16_add(4, 'f_j', union(path_of('f'), rect(150, XB0, dx + hspans(path_of('j'), 300)[0][1], XB1), path_of('j', dx)), dx + W('j'))
# 5 ft, 6 fft, 7 tf: one crossbar through both letters
dx = kerned('f', 't') - 15
s16_add(5, 'f_t', union(path_of('f'), path_of('t', dx), rect(150, XB0, dx + 150, XB1)), dx + W('t'))
dx = kerned('f_f', 't') - 37
s16_add(6, 'f_f_t', union(path_of('f_f'), path_of('t', dx), rect(DX_F + 150, XB0, dx + 150, XB1)), dx + W('t'))
dx = kerned('t', 'f') - 33
s16_add(7, 't_f', union(path_of('t'), path_of('f', dx), rect(150, XB0, dx + 150, XB1)), dx + W('f'))
# 9 fy, 16 tw: the crossbar meets the left arm, flush with its top
dx = kerned('f', 'y')
s16_add(9, 'f_y', union(path_of('f'), path_of('y', dx), rect(150, XB0, dx + arm('y'), XB1)), dx + W('y'))
dx = kerned('t', 'w') - 16
s16_add(16, 't_w', union(path_of('t'), path_of('w', dx), rect(150, XB0, dx + arm('w'), XB1)), dx + W('w'))
# 22 ry, 23 rw: the r's arm runs level into the next letter's left arm, which is
# carried up along its own edges to the arm's top
def r_into(nxt, off):
    dx = kerned('r', nxt) + off
    q = path_of(nxt); top = q.bounds[3]
    (a0, a1), (b0, b1) = hspans(q, top - 20)[0], hspans(q, top - 60)[0]
    k0, k1, h = (a0 - b0) / 40, (a1 - b1) / 40, R_TOP - (top - 20)
    ext = poly([(dx + a0, top - 20), (dx + a1, top - 20), (dx + a1 + k1 * h, R_TOP), (dx + a0 + k0 * h, R_TOP)])
    return union(terminal_run(path_of('r'), R_TX, R_TOP, R_UX, R_UND, dx + mid((a0, a1))), path_of(nxt, dx), ext), dx + W(nxt)
p, w = r_into('y', -20); s16_add(22, 'r_y', p, w)
p, w = r_into('w', -22); s16_add(23, 'r_w', p, w)
# 24 ll: staggered like ff, the first l DROP shorter
_lp = path_of('l')
dx = kerned('l', 'l') - 25
s16_add(24, 'l_l', union(clip(_lp, (-500, -500, 1000, _lp.bounds[3] - DROP)), path_of('l', dx)), dx + W('l'))
# 25 rn, 26 cl: spacing alternates, 30 units more before n and l
s16_add(25, 'r.rn', path_of('r'), W('r') + 30)
s16_add(26, 'c.cl', path_of('c'), W('c') + 30)

# --- capitals and word logotypes (lab G2) -----------------------------------------
# 50 TT: two stems under one bar
dx = kerned('T', 'T') - 139
s16_add(50, 'T_T.dlig', union(path_of('T'), path_of('T', dx)), dx + W('T'))
_Tp = path_of('T'); T_LO = vspans(_Tp, 50)[-1][0]; T_TOP, T_XR = _Tp.bounds[3], _Tp.bounds[2]
# 81 Torchlette: selected T03-K120, a C2 left ribbon and a tighter T-o gap.
# The selected prototype uses fixed 120-unit extension, 35-unit drop and 120-unit
# T-o tightening in every weight. All letters after T move together; later gaps
# and the glyph/ss16 identity stay unchanged. The existing T supplies bar weight.
_TORCHLETTE_EXTENSION, _TORCHLETTE_DROP, _TORCHLETTE_KERN = 120.0, 35.0, 120
items, adv = setting('T o r c h l e t_t e'.split())
items = [(n, x if i == 0 else x - _TORCHLETTE_KERN) for i, (n, x) in enumerate(items)]
adv -= _TORCHLETTE_KERN
xh = dict(items)['h']
parts = [clip(path_of(n, x), (x - 100, -300, x + 1000, T_TOP)) if n == 'h' else path_of(n, x) for n, x in items]
# Native cubic ribbon, not an SVG transcription. At the old left edge its first
# two controls share the join's y: both slope and curvature agree with the flat
# bar. Its parallel upper boundary gives exactly the original vertical weight.
_left = _Tp.bounds[0]
_ribbon = pathops.Path(); _rp = _ribbon.getPen()
_rp.moveTo((_left, T_LO))
_rp.curveTo((_left - _TORCHLETTE_EXTENSION / 3, T_LO),
            (_left - 2 * _TORCHLETTE_EXTENSION / 3, T_LO),
            (_left - _TORCHLETTE_EXTENSION, T_LO - _TORCHLETTE_DROP))
_rp.lineTo((_left - _TORCHLETTE_EXTENSION, T_TOP - _TORCHLETTE_DROP))
_rp.curveTo((_left - 2 * _TORCHLETTE_EXTENSION / 3, T_TOP),
            (_left - _TORCHLETTE_EXTENSION / 3, T_TOP), (_left, T_TOP))
_rp.closePath()
s16_add(81, 'T_o_r_c_h_l_e_t_t_e.ss11', union(*parts, _ribbon,
        rect(T_XR - 5, T_LO, xh + hspans(path_of('h'), 600)[0][1], T_TOP)), adv)
# 84 network: the t's crossbar runs on into the top of the w's first arm
items, adv = setting('n e t w o r k'.split()); d = dict(items)
s16_add(84, 'n_e_t_w_o_r_k.ss11', union(word_paths(items), rect(d['t'] + TBAR_R - 19, XB0, d['w'] + arm('w'), XB1)), adv)
# 85 gradient: the last t's crossbar becomes an arrow, its head a chevron in the bar's weight
items, _ = setting('g r a d i e n t'.split()); xt = items[-1][1]
tip = xt + W('t') + 130
head = stroke_line([(tip - 125, XBM + 125), (tip, XBM), (tip - 125, XBM - 125)], XBW, limit=4)
s16_add(85, 'g_r_a_d_i_e_n_t.ss11', union(word_paths(items), rect(xt + TBAR_R - 19, XB0, tip - 20, XB1), head),
        tip + XBW * math.sqrt(0.5) + 33)
# 85 gradients: the t's foot runs level along the baseline into the bottom of the s, and
# the arrow, the singular's chevron in the s's top stroke's weight, leaves the top of the
# s level and stands as far past the s as the singular's stands past its t. The s loses
# both terminals; the t keeps its crossbar. Each cut is made at an on-curve extreme, where
# the edge is level, so the joins stay smooth, and the foot's top is eased down
# (quadratically, from where the stem's inner edge stops being straight) to the s's counter
# bottom, so the run has one weight. The s eased under a crossbar (_s) is outputs' (169).
items, _ = setting('g r a d i e n t s'.split()); xt, xs = items[-2][1], items[-1][1]
_sp, _son = path_of('s'), oncurve('s')[0]
S_TX = min(x for x, y in _son if y == max(q[1] for q in _son))                  # the s's top: 245 at Regular
S_T0 = vspans(_sp, S_TX)[-1][0]                                                 # the top of its counter: 427
_tg = vspans(_sp, _sp.bounds[2] - 30)                                           # near its right side: lower bowl, upper terminal
S_CUT = (_tg[-2][1] + _tg[-1][0]) / 2                                           # the gap between them
S_EASE = S_CUT - 40                                                             # the easing starts a little below the terminal
_k = (S_T0 - XB0) / (S_T0 - S_EASE) ** 2
_sp = path_of('s', fn=lambda q: (q[0], q[1] - _k * (q[1] - S_EASE) ** 2) if q[1] > S_EASE else q)
_s = clip(diff(_sp, rect(S_TX, S_CUT, 2000, 2000)), (-100, -400, 2000, XB1))
def _ext(on, pick, keep): return pick([q for q in on if keep(q)], key=lambda q: q[1])
_ton, _sp0 = oncurve('t')[0], path_of('s')
TF_OUT = _ext(_ton, min, lambda q: q[0] > T_STEM[1])                                          # the t's foot, underside: 248, -9
TF_IN = _ext(_ton, min, lambda q: T_STEM[1] + 20 < q[0] < _tp.bounds[2] - 20 and q[1] > TF_OUT[1] + 20)   # its top: 256, 48
TF_LIM = max(q[1] for q in _ton if q[0] > T_STEM[1] + 20 and q[1] < 300) + 60            # above the foot's terminal: 121
TF_YI = max(q[1] for q in _ton if abs(q[0] - T_STEM[1]) < 2 and TF_IN[1] < q[1] < 300)    # the stem's inner edge, straight above: 163
SB_OUT = _ext(_son, min, lambda q: True)                                                     # the s's bottom: 235, -9
SB_IN = _ext(_son, min, lambda q: abs(q[0] - SB_OUT[0]) < 60 and q[1] > SB_OUT[1] + 20)      # its counter's bottom: 237, 45
ST_OUT = _ext(_son, max, lambda q: True)                                                     # the s's top: 245, 480
ST_IN = _ext(_son, max, lambda q: abs(q[0] - ST_OUT[0]) < 60 and q[1] < ST_OUT[1] - 20)      # its counter's top: 246, 427
_bg, _bm = vspans(_sp0, _sp0.bounds[0] + 30), vspans(_sp0, SB_IN[0])
SB_CUT = min((_bg[0][1] + _bg[1][0]) / 2, (_bm[0][1] + _bm[1][0]) / 2)                       # above the lower terminal: 127
WT = ST_OUT[1] - ST_IN[1]                                                                    # the top stroke's weight: 53
_dd = TF_IN[1] - SB_IN[1]
def _lower(q, y0=TF_IN[1]):       # the foot's top eased down to the s's counter bottom, from where the stem's edge stops being straight
    if q[0] < T_STEM[1] - 1 or q[1] >= TF_YI or q[1] < TF_OUT[1] + 20: return q
    return (q[0], q[1] - _dd * min(1, (TF_YI - q[1]) / (TF_YI - y0)) ** 2)
TF_IN = (TF_IN[0], SB_IN[1])                                                                 # the foot's top, eased
def _main(q):                     # without the crumbs a cut leaves of a terminal (Black's lower one)
    cs = list(q.contours); big = max(abs(c.area) for c in cs)
    return union(*[c for c in cs if abs(c.area) > 0.05 * big])
# Each letter is cut along a slant from just outside its stroke's outer extreme to just outside
# its inner one, and the run and the shaft reach 3 units past the cut into the letter, so no
# edge of a join lies on an edge of the letter it meets but the level ones.
_tkeep = poly([(-500, -500), (TF_OUT[0] + 1, -500), (TF_OUT[0] + 1, TF_OUT[1] - 1), (TF_IN[0] + 1, TF_IN[1] + 1),
               (TF_IN[0] + 1, TF_LIM), (3000, TF_LIM), (3000, 3000), (-500, 3000)])
_skeep = pathops.op(poly([(SB_OUT[0] - 1, -500), (3000, -500), (3000, 3000), (-500, 3000), (-500, SB_CUT), (SB_IN[0] - 1, SB_CUT),
                          (SB_IN[0] - 1, SB_IN[1] + 1), (SB_OUT[0] - 1, SB_OUT[1] - 1)]),
                    poly([(-500, -500), (3000, -500), (3000, S_CUT), (ST_IN[0] + 1, S_CUT), (ST_IN[0] + 1, ST_IN[1] - 1),
                          (ST_OUT[0] + 1, ST_OUT[1] + 1), (ST_OUT[0] + 1, 3000), (-500, 3000)]), pathops.PathOp.INTERSECTION)
_tf = mv(_main(pathops.op(path_of('t', fn=_lower), _tkeep, pathops.PathOp.INTERSECTION)), xt)
_sf = mv(_main(pathops.op(_sp0, _skeep, pathops.PathOp.INTERSECTION)), xs)
_o0, _i0, _o1, _i1 = (xt + TF_OUT[0], TF_OUT[1]), (xt + TF_IN[0], TF_IN[1]), (xs + SB_OUT[0], SB_OUT[1]), (xs + SB_IN[0], SB_IN[1])
_run = pathops.Path(); _pen = _run.getPen(); _xo, _xi = (_o0[0] + _o1[0]) / 2, (_i0[0] + _i1[0]) / 2   # each edge level at both ends
_pen.moveTo((_o0[0] - 2, _o0[1])); _pen.curveTo((_xo, _o0[1]), (_xo, _o1[1]), (_o1[0] + 2, _o1[1])); _pen.lineTo((_i1[0] + 2, _i1[1]))
_pen.curveTo((_xi, _i1[1]), (_xi, _i0[1]), (_i0[0] - 2, _i0[1])); _pen.closePath()
tip = xs + _sp0.bounds[2] + W('t') + 130 - _tp.bounds[2]          # past the s as the singular's tip is past its t: 151 at Regular
_shaft = poly([(xs + ST_OUT[0] - 2, ST_OUT[1]), (tip - 20, ST_OUT[1]), (tip - 20, ST_IN[1]), (xs + ST_IN[0] - 2, ST_IN[1])])
head = stroke_line([(tip - 125, (ST_OUT[1] + ST_IN[1]) / 2 + 125), (tip, (ST_OUT[1] + ST_IN[1]) / 2), (tip - 125, (ST_OUT[1] + ST_IN[1]) / 2 - 125)], WT, limit=4)
_ts = union(_sf, _run, _tf, _shaft, head)
_area = lambda q: sum(abs(c.area) for c in q.contours)
assert _area(_ts) > _area(_sf) + _area(_tf), 'gradients: the t-s union lost a part'
s16_add(85, 'g_r_a_d_i_e_n_t_s.ss11', union(word_paths(items[:-2]), _ts), tip + WT * math.sqrt(0.5) + 33)
# 86 softmax: the t's crossbar runs into the top of the m's first stem
items, adv = setting('s o f t m a x'.split()); d = dict(items)
s16_add(86, 's_o_f_t_m_a_x.ss11', union(word_paths(items), rect(d['t'] + TBAR_R - 19, XB0, d['m'] + mid(hspans(path_of('m'), 300)[0]), XB1)), adv)
# 88 Python: the t's crossbar reaches back to the top of the y's right arm
items, adv = setting('P y t h o n'.split()); d = dict(items)
s16_add(88, 'P_y_t_h_o_n.ss11', union(word_paths(items), rect(d['y'] + arm('y', k=1), XB0, d['t'] + (TBAR_L + T_STEM[0]) / 2, XB1)), adv)

# --- numbers, signs and data glyphs (lab G3) ---------------------------------------
_mn = path_of('minus').bounds
BAR, LIN_AXIS = _mn[3] - _mn[1], (_mn[1] + _mn[3]) / 2       # the operators' bar (53) and axis (286.5)
OSF_AXIS = 245                                               # the old-style figures' middle
# 90 range dash: a shorter en dash with sidebearings; the protected hyphen and slash
_en = path_of('endash').bounds
s16_add(90, 'endash.range', rect(36, _en[1], 416, _en[3]), 452)
s16_add(90, 'hyphen.keep', path_of('hyphen'), W('hyphen'))
s16_add(98, 'slash.keep', path_of('slash'), W('slash'))
# 91 minus, 92 plus-minus, 93 approx, 114 times, for old-style figures
s16_add(91, 'minus.osf', rect(45, OSF_AXIS - BAR / 2, 435, OSF_AXIS + BAR / 2), 480)
_pm = vspans(path_of('plusminus'), 300); pm_gap = 41 * (_pm[1][0] - _pm[0][1]) / 70   # Mulish's own gap (70) closes as it gets heavier
_ps = hspans(path_of('plus'), 400)[0]
pm_c, pm_x, pm_h = 270, 243, (_ps[1] - _ps[0]) / 2               # the plus's vertical: 54 wide at Regular
pm_v = pm_c - (BAR + pm_gap)                                     # the vertical's half length (176 at Regular)
s16_add(92, 'plusminus.osf', union(rect(48, pm_c - BAR / 2, 438, pm_c + BAR / 2), rect(pm_x - pm_h, pm_c - pm_v, pm_x + pm_h, pm_c + pm_v),
                                   rect(48, 0, 438, BAR)), 486)
_ax = path_of('approxequal')
_waves = []
for c in _ax.contours:
    q = pathops.Path(); c.draw(q.getPen()); _waves.append(q)
_waves.sort(key=lambda q: q.bounds[1])
_as = vspans(_ax, 300); ax_in = 15 * (_as[1][0] - _as[0][1]) / 139      # each wave 15 closer at Regular, in proportion to the gap
ax = union(mv(_waves[0], 0, ax_in), mv(_waves[1], 0, -ax_in))
b = ax.bounds; acy = (b[1] + b[3]) / 2
ax = transformed(ax, (0.82, 0, 0, 1, 0, 0)); b = ax.bounds
ax = mv(ax, 45 - b[0], OSF_AXIS - acy)
s16_add(93, 'approxequal.osf', ax, ax.bounds[2] + 45)
def times(cx, cy, h, t=BAR):
    return union(band((cx - h, cy - h), (cx + h, cy + h), t), band((cx - h, cy + h), (cx + h, cy - h), t))
# its arms end in points that meet the figures only at their tips, so it takes more room
# than minus.osf's flat ends (45): TIMES_SB at every weight, as Source Sans and IBM Plex
# give their times signs about 1.4 times their plus's sidebearings
TIMES_SB = P('TIMES_SB', 62)
_mo = times(0, OSF_AXIS, 172); _mob = _mo.bounds
s16_add(114, 'multiply.osf', mv(_mo, TIMES_SB - _mob[0]), _mob[2] - _mob[0] + 2 * TIMES_SB)
# 115 a times sign centred on the capitals
_mb = path_of('multiply').bounds
s16_add(115, 'multiply.case', mv(path_of('multiply'), 0, 352 - (_mb[1] + _mb[3]) / 2), W('multiply'))
# 99 ratio colon: centred on the figures, a little tighter; 100 cap hyphen
_cb = path_of('colon').bounds; _cc = (_cb[1] + _cb[3]) / 2
s16_add(99, 'colon.lf', mv(path_of('colon'), -18, 352 - _cc), W('colon') - 36)
s16_add(99, 'colon.of', mv(path_of('colon'), -18, 255 - _cc), W('colon') - 36)
_hb = path_of('hyphen').bounds
s16_add(100, 'hyphen.case', mv(path_of('hyphen'), 0, 353.5 - (_hb[1] + _hb[3]) / 2), W('hyphen'))
# 102-105 arrows from the shipped -> arrow: its head, mirrored, doubled, on longer shafts
AR = path_of('arrowright')
HX = min(330, 380 - 35 * SM - 10)                       # the head starts right of its back corners
ahead = clip(AR, (HX, 0, 700, 600))
def shaft(x0, x1): return rect(x0, _mn[1], x1, _mn[3])
s16_add(102, 'arrowleft', mirror(AR, 330), 660, 0x2190)
s16_add(103, 'arrowboth', union(mirror(ahead, 330), shaft(100, 680), mv(ahead, 180)), 840, 0x2194)
s16_add(105, 'uni27F6', union(shaft(60, 840), mv(ahead, 340)), 1000, 0x27F6)
s16_add(105, 'uni27F5', mirror(union(shaft(60, 840), mv(ahead, 340)), 500), 1000, 0x27F5)
# 104 double arrows: shafts at the bars of =, a 45-degree chevron head with a 26-unit flat tip
_eq = vspans(path_of('equal'), 300); EQ_C, EQ_D, EQ_T = (_eq[0][0] + _eq[1][1]) / 2, (mid(_eq[1]) - mid(_eq[0])) / 2, _eq[0][1] - _eq[0][0]
def dbl_head(X, R=200, t=55 * EQ_T / 53):
    v, h, c = t * math.sqrt(2), t / math.sqrt(2), EQ_C
    return poly([(X - 13, c + 13), (X - R, c + R), (X - R - h, c + R - h), (X - v, c), (X - R - h, c - R + h), (X - R, c - R), (X - 13, c - 13)])
def dbl_shafts(x0, x1):
    return union(rect(x0, EQ_C - EQ_D - EQ_T / 2, x1, EQ_C - EQ_D + EQ_T / 2), rect(x0, EQ_C + EQ_D - EQ_T / 2, x1, EQ_C + EQ_D + EQ_T / 2))
s16_add(104, 'arrowdblright', union(dbl_shafts(60, 500), dbl_head(640)), 700, 0x21D2)
s16_add(104, 'arrowdblboth', union(mirror(dbl_head(740), 400), dbl_shafts(200, 600), dbl_head(740)), 800, 0x21D4)
# 96 ordinals: superior letters from a heavier Mulish scaled to the superior figures'
# x-height (282), the instance chosen so their stems match those figures' stems
SUP_XH = 282
SUP_STEM = (lambda s: s[1] - s[0])(hspans(path_of('uni00B9'), 500)[0])   # 56 at Regular
def n_stem(f_):
    g_ = f_.getGlyphSet(); q = pathops.Path(); g_['n'].draw(q.getPen(glyphSet=g_))
    return (lambda s: s[1] - s[0])(hspans(q, 200)[0])
lo, hi = (400 if SRC_W >= 324 else 200), 1000   # Light's superiors want a wght under 400
for _ in range(9):
    mid_w = (lo + hi) / 2; f_ = inst(mid_w)
    lo, hi = (mid_w, hi) if n_stem(f_) * SUP_XH / f_['OS/2'].sxHeight < SUP_STEM else (lo, mid_w)
SUPW = round((lo + hi) / 2); supf = inst(SUPW); sup_gs = supf.getGlyphSet(); SUPS = SUP_XH / supf['OS/2'].sxHeight
print(f'ss16 superior letters: Mulish wght {SUPW}, scale {SUPS:.3f}, stem {n_stem(supf) * SUPS:.1f} (superior figures {SUP_STEM:g})')
for ch in 'stndrh':
    for suffix, base in (('.ord', 330), ('.ord.osf', 238)):
        rec = DecomposingRecordingPen(sup_gs); sup_gs[ch].draw(rec)
        q = pathops.Path(); rec.replay(TransformPen(q.getPen(), (SUPS, 0, 0, SUPS, 12, base)))
        s16_add(96, ch + suffix, q, supf['hmtx'][ch][0] * SUPS + 24)
# 111 matmul @: the small-cap @ on the operator axis
_ab = path_of('at.sc').bounds
s16_add(111, 'at.op', mv(path_of('at.sc'), 0, LIN_AXIS - (_ab[1] + _ab[3]) / 2), W('at.sc'))
# 116 tuple space, 118 unit space; 117 old-style percent (the small-cap one, pulled in)
s16_add(116, 'space.tuple', pathops.Path(), 110)
s16_add(118, 'space.unit', pathops.Path(), 140)
s16_add(117, 'percent.osf', mv(path_of('percent.sc'), -22), W('percent.sc') - 44)
# 121 version tag: a pill-shaped band with the v and small-cap figures knocked out
TAG0, TAG1, TAGR = -110, 590, 130
def band_end(a): return clip(rrect(-2000, TAG0, a, TAG1, TAGR), (0, TAG0 - 10, a + 10, TAG1 + 10))
def band_start(x0, a): return clip(rrect(x0, TAG0, a + 2000, TAG1, TAGR), (-10, TAG0 - 10, a, TAG1 + 10))
_vb = path_of('v').bounds; v_adv = 120 + (_vb[2] - _vb[0]) + 11       # 590 at Regular
s16_add(121, 'tag.v', diff(band_start(30, v_adv), path_of('v', 120 - _vb[0])), v_adv)
for dg in DIGITS:
    s16_add(121, dg + '.tag', diff(rect(0, TAG0, W(dg + '.sc'), TAG1), path_of(dg + '.sc')), W(dg + '.sc'))
_pb = path_of('period').bounds
s16_add(121, 'period.tag', diff(rect(0, TAG0, 170, TAG1), path_of('period', 85 - (_pb[0] + _pb[2]) / 2)), 170)
s16_add(121, 'tag.end', band_end(150), 190)
# 122 spark bars: one bar per figure, 0-9 high
for k in range(10):
    s16_add(122, f'spark.{k}', rect(20, 0, 110, 50 + k * 62), 130)
for n, a in (('spark.start', 40), ('spark.sep', 0), ('spark.end', 40)):
    s16_add(122, n, pathops.Path(), a)
# 123 spark line: each figure a round-capped segment from the previous value; the
# stroke follows the stems (48 at Regular)
SL_W, SL_R = 110, 24 * SV
def SY(k): return 50 + k * 55
def capsule_raw(x0, y0, x1, y1, r):
    """A round-ended stroke written straight to TrueType points: the tangent points are
    rounded first and each quarter arc is one quadratic whose control lies along the
    rounded straight edge, so every join is smooth."""
    def draw(pen):
        R = lambda q: (round(q[0]), round(q[1]))
        if math.hypot(x1 - x0, y1 - y0) < 1:
            pen.qCurveTo(R((x0 + r, y0 - r)), R((x0 - r, y0 - r)), R((x0 - r, y0 + r)), R((x0 + r, y0 + r)), None); pen.closePath(); return
        a = math.atan2(y1 - y0, x1 - x0); ux, uy = math.cos(a), math.sin(a); nx, ny = uy, -ux
        T1, T2 = R((x0 - r * nx, y0 - r * ny)), R((x1 - r * nx, y1 - r * ny))
        T3, T4 = R((x1 + r * nx, y1 + r * ny)), R((x0 + r * nx, y0 + r * ny))
        def along(P_, Q_, d):
            L = math.dist(P_, Q_); return R((Q_[0] + (Q_[0] - P_[0]) / L * d, Q_[1] + (Q_[1] - P_[1]) / L * d))
        pen.moveTo(T1); pen.lineTo(T2); pen.qCurveTo(along(T1, T2, r), along(T4, T3, r), T3)
        pen.lineTo(T4); pen.qCurveTo(along(T3, T4, r), along(T2, T1, r), T1); pen.closePath()
    return draw
for k in range(10):
    s16_raw(123, f'sparkl.first.{k}', capsule_raw(0, SY(k), 0, SY(k), SL_R), 0)
    for q_ in range(10):
        s16_raw(123, f'sparkl.{q_}_{k}', capsule_raw(0, SY(q_), SL_W, SY(k), SL_R), SL_W)
for n, a in (('sparkl.start', 50), ('sparkl.sep', 0), ('sparkl.end', 50)):
    s16_add(123, n, pathops.Path(), a)
# 124 progress bar: = cells filled, - cells hollow (their rails follow the stems), round ends
PB0, PB1, PS, PR = 40, 440, 46 * SV, 200
s16_add(124, 'pbar.fill', rect(0, PB0, 110, PB1), 110)
s16_add(124, 'pbar.empty', union(rect(0, PB0, 110, PB0 + PS), rect(0, PB1 - PS, 110, PB1)), 110)
def pcap(left, filled, a=260):
    if left:
        outer = rrect(40, PB0, a + 2000, PB1, PR); inner = rrect(40 + PS, PB0 + PS, a + 2000, PB1 - PS, PR - PS)
        box = (0, PB0 - 10, a, PB1 + 10)
    else:
        outer = rrect(-2000, PB0, a - 40, PB1, PR); inner = rrect(-2000, PB0 + PS, a - 40 - PS, PB1 - PS, PR - PS)
        box = (0, PB0 - 10, a + 10, PB1 + 10)
    return clip(outer if filled else diff(outer, inner), box)
for n, l_, f_ in (('pbar.start.f', True, True), ('pbar.start.e', True, False), ('pbar.end.f', False, True), ('pbar.end.e', False, False)):
    s16_add(124, n, pcap(l_, f_), 260)

# --- round 2 of the lab (ids 125-215): the joins and word marks Jordan kept ---------
# A crossbar that ends flush on the next (or previous) letter, at the first x where
# that letter's ink covers the whole bar height.
def covers(p, x, y0, y1): return any(a <= y0 and b >= y1 for a, b in vspans(p, x))
def join_from_left(p, y0, y1):
    b = p.bounds; x = b[0]
    while x < b[2]:
        if covers(p, x, y0 + 2, y1 - 2): return x
        x += 2
    raise ValueError('no cover')
def join_from_right(p, y0, y1):
    b = p.bounds; x = b[2]
    while x > b[0]:
        if covers(p, x, y0 + 2, y1 - 2): return x
        x -= 2
    raise ValueError('no cover')
def chevron(tip, y, d=1, k=125, w=None):
    w = XBW if w is None else w
    return stroke_line([(tip - d * k, y + k), (tip, y), (tip - d * k, y - k)], w, limit=4)
def t_into(nxt, off=0, first='t'):
    """The crossbar of t (or f) runs right into the next letter."""
    dx = kerned(first, nxt) + off; q = path_of(nxt)
    x = join_from_left(q, XB0, XB1)
    x0 = TBAR_R - 19 if first == 't' else 150
    return union(path_of(first), path_of(nxt, dx), rect(x0, XB0, dx + x + 6, XB1)), dx + W(nxt), dx
def into_t(prev, off=0, nxt='t'):
    """The crossbar of the t runs back left into the letter before."""
    dx = kerned(prev, nxt) + off; q = path_of(prev)
    x = join_from_right(q, XB0, XB1)
    return union(path_of(prev), path_of(nxt, dx), rect(x - 6, XB0, dx + TBAR_L + 19, XB1)), dx + W(nxt), dx
# Where a bar's underside meets a curved or slanting edge, the inside corner is
# filleted: a circle of radius FIL touches the underside and the edge (found on the
# outline, so the arc leaves both along their own tangents), and the space between
# them and the arc is filled. side 'right': the edge is to the right of the corner.
FIL = XBW if SRC_W <= 675 else XBW * (101 / 58) / SH   # past Bold, Bold's radius: a larger one fills the x's crotch
def fillet(p, Y, x_ref, side, r=FIL):
    sg = 1 if side == 'right' else -1
    def edge(y):
        xs = [s_[0] for s_ in hspans(p, y) if s_[0] > x_ref] if sg > 0 else [s_[1] for s_ in hspans(p, y) if s_[1] < x_ref]
        return (min(xs) if sg > 0 else max(xs)) if xs else None
    pts = [(edge(y), y) for y in (Y - 0.5 - k * 0.5 for k in range(int(4 * r)))]
    pts = [q for q in pts if q[0] is not None]
    cy = Y - r
    def d(cx): return min((math.hypot(x - cx, y - cy), (x, y)) for x, y in pts)
    lo, hi = edge(cy) - sg * 3 * r, edge(cy)            # d(lo) > r > d(hi)
    for _ in range(40):
        m_ = (lo + hi) / 2
        lo, hi = (m_, hi) if d(m_)[0] > r else (lo, m_)
    cx = (lo + hi) / 2; tx, ty = d(cx)[1]
    inner = [(x + sg * 8, y) for x, y in pts if y >= ty][::8] + [(tx + sg * 8, ty)]   # just inside the edge
    # the patch as one contour: along the underside to just inside the edge, down it, to the
    # tangent point, and back up the arc (one cubic; no boolean touches the tangencies)
    a0 = math.atan2(ty - cy, tx - cx); a1 = math.pi / 2; h = 4 / 3 * math.tan((a1 - a0) / 4) * r
    q = pathops.Path(); pen = q.getPen()
    pen.moveTo((cx, Y)); pen.lineTo((inner[0][0], Y))
    for q_ in inner: pen.lineTo(q_)
    pen.lineTo((tx, ty))
    pen.curveTo((tx - h * math.sin(a0), ty + h * math.cos(a0)), (cx + h, Y), (cx, Y)); pen.closePath()
    return union(p, q)
# A word mark replaces one letter (or a few) inside a known word, so the kerning Mulish
# gives that letter with its neighbours there is built into the glyph.
def in_word(p, w, prev, first, nxt, last=None):
    kp = kern(prev, first) if prev else 0; kn = kern(last or first, nxt) if nxt else 0
    return mv(p, kp), w + kp + kn
# 125 tp: the t's crossbar runs into the top of the p's stem
p, w, dx = t_into('p', -20); p = fillet(p, XB0, dx + join_from_left(path_of('p'), XB0, XB1) - 8, 'right')
s16_add(125, 't_p', p, w)
# 137 xt: the crossbar reaches back to the x's upper right arm, flush with its top
p, w, _ = into_t('x', -20); p = fillet(p, XB0, join_from_right(path_of('x'), XB0, XB1) + 8, 'left')
s16_add(137, 'x_t', p, w)
# 145 fu: the f's crossbar meets the u's left stem, flush with its top (a square corner, as fy's)
dx = kerned('f', 'u') - 10
s16_add(145, 'f_u', union(path_of('f'), path_of('u', dx), rect(150, XB0, dx + join_from_left(path_of('u'), XB0, XB1) + 6, XB1)), dx + W('u'))
# 148 rv: the r's arm runs level into the v's left arm, as in ry
p, w = r_into('v', -20); dx = kerned('r', 'v') - 20
p = fillet(p, R_UND, dx + hspans(path_of('v'), R_UND - 4)[0][0] - 8, 'right')
s16_add(148, 'r_v', p, w)
# 171 vector(s): the v carries the arrow of a maths vector, under the ascender line
_vp = path_of('v'); VB = _vp.bounds; VY, VK, VW = 615, 80, XBW * 0.8
s16_add(171, 'v.vec', *in_word(union(_vp, rect(VB[0] + 30, VY - VW / 2, VB[2] - 40, VY + VW / 2), chevron(VB[2] - 20, VY, 1, VK, VW)), W('v'), None, 'v', 'e'))
# 200 length(s): the crossbar reaches back to the g's stem, only in this word
p, w, _ = into_t('g', -10); p = fillet(p, XB0, join_from_right(path_of('g'), XB0, XB1) + 8, 'left')
s16_add(200, 'g_t.w200', *in_word(p, w, 'n', 'g', 'h', 't'))
# 207 residual(s): an arch, the skip connection, over u and a from the d's stem to the l's.
# Each end rises straight out of its stem at the stem's own width and thins to the
# crossbar's weight at the crown (the lab's crown, 820 + half a crossbar), so it
# springs without a corner.
items_, adv = setting(['d', 'u', 'a', 'l']); dd_ = dict(items_)
_dp, _lp2 = path_of('d'), path_of('l', dd_['l'])
D_STEM = hspans(_dp, 700)[0]; L_STEM = hspans(_lp2, 700)[0]
AY = min(_dp.bounds[3], _lp2.bounds[3]); ARY = 820 - AY
def _arch(x0, x1, ry): return ellipse((x0 + x1) / 2, AY, (x1 - x0) / 2, ry)
arch = clip(diff(_arch(D_STEM[0], L_STEM[1], ARY + XBW / 2), _arch(D_STEM[1], L_STEM[0], ARY - XBW / 2)), (-100, AY - 1, 3000, 2000))
s16_add(207, 'd_u_a_l.arch', *in_word(union(word_paths(items_), arch), adv, 'i', 'd', None))
# 166c backward(s), 167b forward: the top of the b's (d's) stem turns back (forward) in an
# even curve, the stem's own width, and runs on level as the gradient's arrow. The b's
# arrow hangs before the word, so the glyph starts 30 units before the tip; the d's
# widens the d to 33 past it. Heavier styles lengthen the head so the chevron stays open.
def curl(n, d, r, L, k):
    p = path_of(n); b_ = p.bounds
    st = hspans(p, 640)[0 if d < 0 else -1]; w = st[1] - st[0]; c = mid(st)
    top = b_[3]; yc = top - w / 2; y0 = yc - r                     # centre line of the shaft; the turn starts at y0
    acx = c + d * r                                                # the turn's centre: (acx, y0)
    ring = diff(ellipse(acx, y0, r + w / 2, r + w / 2), ellipse(acx, y0, r - w / 2, r - w / 2))
    turn = clip(ring, (c - w, y0, acx, top + 5) if d > 0 else (acx, y0, c + w, top + 5))
    keep = clip(p, (-500, -500, 3000, y0 + 0.5))                  # the letter below the turn, whole
    tip = acx + d * L
    shaft = rect(min(acx, tip - d * 20) - (1 if d > 0 else 0), yc - w / 2, max(acx, tip - d * 20) + (1 if d < 0 else 0), yc + w / 2)
    body = union(keep, turn, shaft, chevron(tip, yc, d, k))
    if d < 0:
        sh = max(0, 30 - body.bounds[0]); return mv(body, sh), W(n) + sh
    return body, max(W(n), body.bounds[2] + 33)
for id_, n, d, nm, r, L, k, prev, nxt in ((166, 'b', -1, 'b.backc', 140, 185, 110, None, 'a'), (167, 'd', 1, 'd.fwdb', 95, 165, 100, 'r', None)):
    kk = k * (XBW / 52) ** 0.6
    p, w = curl(n, d, r, L + kk - k, kk); s16_add(id_, nm, *in_word(p, w, prev, n, nxt))
# 169 output(s): the last t's crossbar runs on as the gradient's arrow; in outputs it runs
# over the s, the s eased under it (_s, from 85 gradients)
tip = W('t') + 130
s16_add(169, 't.out', *in_word(union(path_of('t'), rect(TBAR_R - 19, XB0, tip - 20, XB1), chevron(tip, XBM)), tip + XBW * math.sqrt(0.5) + 33, 'u', 't', None))
xs = kerned('t', 's'); tip = xs + W('s') + 110
s16_add(169, 't_s.out', *in_word(union(path_of('t'), mv(_s, xs), rect(TBAR_R - 19, XB0, tip - 20, XB1), chevron(tip, XBM)), tip + XBW * math.sqrt(0.5) + 33, 'u', 't', None))
print(f'ss16: {sum(len(v) for v in S16.values())} glyphs for {len(S16)} proposals')

# --- ss16 features -----------------------------------------------------------------
# Every proposal keeps the lab's rule and its guards (word boundaries for the
# logotypes, the protected date and phone chains for the range dash, the
# fraction guards, the minus that never follows a word). The logotypes and TT run
# right after the small caps, before liga and ss01 (S16_FRONT, placed at the head of
# FEA), so they see plain letters; the rest run after every other feature (S16_FEA),
# where ss02 has made -> an arrow and 28x28 a times sign, onum has made the figures
# old-style and liga has made ff and tt. The spark line (123) shares its trigger with
# the spark bars (122), so it lives in ss15, which runs first and wins when on.
S16_LOOKUPS = {}                      # lab id -> its lookups, in order
S16_FEATURE = {}                      # lookup -> the feature it belongs to ('ss16' or 'ss15')
S16_FRONT, S16_TAIL = [], []
def s16_lookup(id_, name, body, front=False, feature='ss16'):
    (S16_FRONT if front else S16_TAIL).append(f'lookup {name} {{\n{body}\n}} {name};')
    if id_ is not None: S16_LOOKUPS.setdefault(id_, []).append(name)
    S16_FEATURE[name] = feature
J = ' '.join
def cls(xs): return '[' + J(xs) + ']'
cmap_s16 = font.getBestCmap()
_letters = {g for u, g in cmap_s16.items() if unicodedata.category(chr(u))[0] in 'LN' or chr(u) == '_'}
_wordish = lambda g: bool(g.split('.')[0]) and all(q in _letters for q in g.split('.')[0].split('_'))
S16_WORD = sorted(g for g in font.getGlyphOrder() if g != '.notdef' and (g in _letters or _wordish(g)))
S16_FRONT.append(f"@S16_WORD = {cls(S16_WORD)};\n@S16_WORDNOS = {cls(g for g in S16_WORD if g != 's')};")
# 50 TT, then the whole-word logotypes: never inside a longer word; a plural s is allowed
# (gradients has its own logotype)
s16_lookup(50, 'S16_50', '  sub T T by T_T.dlig;', front=True)
# 85 gradients: the plural logotype, tried first, so the singular's lookup sees it no more
s = [cmap_s16[ord(ch)] for ch in 'gradients']; marked = J(x + "'" for x in s)
S16_FRONT.append(f'lookup S16_LIG_85S {{ sub {J(s)} by g_r_a_d_i_e_n_t_s.ss11; }} S16_LIG_85S;')
s16_lookup(85, 'S16_85S', f"  ignore sub @S16_WORD {marked};\n  ignore sub {marked} @S16_WORD;\n"
           f"  sub {s[0]}' lookup S16_LIG_85S {J(x + chr(39) for x in s[1:])};", front=True)
for id_, word, g in ((81, 'Torchlette', 'T_o_r_c_h_l_e_t_t_e.ss11'), (84, 'network', 'n_e_t_w_o_r_k.ss11'),
                     (85, 'gradient', 'g_r_a_d_i_e_n_t.ss11'), (86, 'softmax', 's_o_f_t_m_a_x.ss11'),
                     (88, 'Python', 'P_y_t_h_o_n.ss11')):
    s = [cmap_s16[ord(ch)] for ch in word]; marked = J(x + "'" for x in s)
    S16_FRONT.append(f'lookup S16_LIG_{id_} {{ sub {J(s)} by {g}; }} S16_LIG_{id_};')
    s16_lookup(id_, f'S16_{id_}', f"  ignore sub @S16_WORD {marked};\n  ignore sub {marked} @S16_WORDNOS;\n"
               f"  ignore sub {marked} s @S16_WORD;\n  sub {s[0]}' lookup S16_LIG_{id_} {J(x + chr(39) for x in s[1:])};", front=True)
# 171 vector, 200 length, 207 residual: the same word guards (a plural s allowed), with
# the substitution on some of the word's letters only
# (166 backward and 169 output too; 169's plural, with its own glyph, goes first; 167
# forward takes no plural, since in forwards the arrow would run into the s)
for id_, word, pos, n, g, plural in ((171, 'vector', 0, 1, 'v.vec', True), (200, 'length', 3, 2, 'g_t.w200', True),
                                     (207, 'residual', 4, 4, 'd_u_a_l.arch', True), (166, 'backward', 0, 1, 'b.backc', True),
                                     (167, 'forward', 6, 1, 'd.fwdb', False), (169, 'outputs', 5, 2, 't_s.out', False),
                                     (169, 'output', 5, 1, 't.out', True)):
    s = [cmap_s16[ord(ch)] for ch in word]; marked = J(x + "'" for x in s); lk = f'S16_{id_}' + ('S' if word == 'outputs' else '')
    marks = [x + "'" for x in s]; marks[pos] += f' lookup S16_LIG_{lk[4:]}'
    S16_FRONT.append(f'lookup S16_LIG_{lk[4:]} {{ sub {J(s[pos:pos + n])} by {g}; }} S16_LIG_{lk[4:]};')
    right = (f"  ignore sub {marked} @S16_WORDNOS;\n  ignore sub {marked} s @S16_WORD;\n" if plural
             else f"  ignore sub {marked} @S16_WORD;\n")
    s16_lookup(id_, lk, f"  ignore sub @S16_WORD {marked};\n" + right + f"  sub {J(marks)};", front=True)

for id_, rule in ((1, 'sub f b by f_b;'), (2, 'sub f h by f_h;'), (3, 'sub f k by f_k;'), (4, 'sub f j by f_j;'),
                  (5, 'sub f t by f_t;'), (6, 'sub f_f t by f_f_t;'), (7, 'sub t f by t_f;'), (9, 'sub f y by f_y;'),
                  (16, 'sub t w by t_w;'), (22, 'sub r y by r_y;'), (23, 'sub r w by r_w;'), (24, 'sub l l by l_l;'),
                  (25, "sub r' n by r.rn;"), (26, "sub c' l by c.cl;")):
    s16_lookup(id_, f'S16_{id_:02d}', '  ' + rule)
# 125 tp, 137 xt, 145 fu, 148 rv: after the f and t pairs above, so ftp keeps ft, ffu
# its ff and tfu its tf
# (in output and outputs, tp joins the first t and 169's arrow ends the last)
for id_, rule in ((125, 'sub t p by t_p;'), (137, 'sub x t by x_t;'), (145, 'sub f u by f_u;'), (148, 'sub r v by r_v;')):
    s16_lookup(id_, f'S16_{id_}', '  ' + rule)

# numbers and signs
FIG = 'zero one two three four five six seven eight nine'.split()
SUPF = ['uni2070', 'uni00B9', 'uni00B2', 'uni00B3', 'uni2074', 'uni2075', 'uni2076', 'uni2077', 'uni2078', 'uni2079']
FORMS_L = {d: [d, d + '.pnum'] + ([d + '.ss08', d + '.pnum.ss08'] if d == 'seven' else []) for d in FIG}
FORMS_O = {d: [d + '.osf', d + '.tosf'] + ([d + '.osf.ss08', d + '.tosf.ss08'] if d == 'seven' else []) for d in FIG}
FORMS = {d: FORMS_L[d] + FORMS_O[d] for d in FIG}
A = S16_TAIL.append
A(f'@S16_DL = {cls(n for d in FIG for n in FORMS_L[d])};\n@S16_DO = {cls(n for d in FIG for n in FORMS_O[d])};\n@S16_D = [@S16_DL @S16_DO];')
A(f"@S16_LC = {cls('abcdefghijklmnopqrstuvwxyz')};\n@S16_UC = {cls('ABCDEFGHIJKLMNOPQRSTUVWXYZ')};\n"
  '@S16_LET = [@S16_LC @S16_UC];\n@S16_WD = [@S16_LET @S16_D underscore];')
A('@S16_DSRC = ' + cls(n for d in FIG for n in FORMS[d]) + ';')
A('@S16_NUMR_DST = ' + cls(d + '.numr' for d in FIG for n in FORMS[d]) + ';')
A('@S16_DNOM_DST = ' + cls(d + '.dnom' for d in FIG for n in FORMS[d]) + ';')
A('@S16_NUMR = ' + cls(d + '.numr' for d in FIG) + ';\n@S16_DNOM = ' + cls(d + '.dnom' for d in FIG) + ';')
A('@S16_TAG_DST = ' + cls(d + '.tag' for d in FIG for n in FORMS[d]) + ';\n@S16_TAGD = ' + cls(d + '.tag' for d in FIG) + ';')
A('@S16_SPARK_DST = ' + cls(f'spark.{FIG.index(d)}' for d in FIG for n in FORMS[d]) + ';')
A('@S16_SPARK = ' + cls(f'spark.{i}' for i in range(10)) + ';')
for i, d in enumerate(FIG):
    A(f'@S16_D{i} = {cls(FORMS[d])};')
    A(f'@S16_SLEND{i} = [sparkl.first.{i} ' + J(f'sparkl.{q}_{i}' for q in range(10)) + '];')
A('@S16_SLEND = [' + J(f'@S16_SLEND{i}' for i in range(10)) + '];')
A('@S16_SLFIRST_DST = ' + cls(f'sparkl.first.{FIG.index(d)}' for d in FIG for n in FORMS[d]) + ';')
D, DL, DO, LET, UC, LC, WD = '@S16_D', '@S16_DL', '@S16_DO', '@S16_LET', '@S16_UC', '@S16_LC', '@S16_WD'
# arrows (102-105); ss02 has already made -> an arrow
s16_lookup(103, 'S16_ARR_LONG', f'''  sub less' hyphen' hyphen' greater' by arrowboth;
  sub less' hyphen' arrowright' by arrowboth;
  sub less' arrowright' by arrowboth;
  sub less' hyphen' greater' by arrowboth;
  sub hyphen' arrowright' by uni27F6;
  sub hyphen' hyphen' greater' by uni27F6;
  sub less' hyphen' hyphen' by uni27F5;
  sub lessequal' greater' by arrowdblboth;
  sub less' equal' greater' by arrowdblboth;
  sub equal' greater' by arrowdblright;''')
S16_LOOKUPS[104] = S16_LOOKUPS[105] = ['S16_ARR_LONG']
s16_lookup(102, 'S16_ARR_LEFT', f"  ignore sub less' hyphen' {D};\n  sub less' hyphen' by arrowleft;")
# 90 ranges: protect date and phone chains first, then figure-hyphen-figure
rules = [f"  ignore sub {D} {D} {D} {D} hyphen' {D} {D} {D};", f"  sub {D} {D} {D} {D} hyphen' {D} {D} by hyphen.keep;"]
for n in range(1, 5):
    run = J([D] * n)
    rules.append(f"  sub {D} hyphen' {run} [hyphen hyphen.keep] {D} by hyphen.keep;")
    rules.append(f"  sub {D} [hyphen hyphen.keep] {run} hyphen' {D} by hyphen.keep;")
s16_lookup(90, 'S16_RANGE_KEEP', '\n'.join(rules))
s16_lookup(90, 'S16_RANGE', f"  sub {D} hyphen' {D} by endash.range;")
# 91 true minus: a hyphen before a figure that does not follow a word
s16_lookup(91, 'S16_MINUS', f'''  ignore sub [{WD} period parenright bracketright hyphen hyphen.keep endash.range plus slash] hyphen' {D};
  sub hyphen' {DO} by minus.osf;
  sub hyphen' {DL} by minus;
  sub minus' {DO} by minus.osf;''')
# 92 plus-minus; 93 approximately
s16_lookup(92, 'S16_PM', f"  sub plus' slash' hyphen' by plusminus;\n  sub plus' hyphen' [{D} space period] by plusminus;")
s16_lookup(93, 'S16_APPROX_EQ', "  sub asciitilde' equal' by approxequal;")
s16_lookup(93, 'S16_APPROX', f"  ignore sub {WD} asciitilde' {D};\n  sub asciitilde' {D} by approxequal;")
# 96 ordinals
s16_lookup(96, 'S16_ORD', f'''  ignore sub {D} s' t {LET};  ignore sub {D} n' d {LET};  ignore sub {D} r' d {LET};  ignore sub {D} t' h {LET};
  sub {DO} s' t by s.ord.osf;  sub {DO} n' d by n.ord.osf;  sub {DO} r' d by r.ord.osf;  sub {DO} t' h by t.ord.osf;
  sub {DL} s' t by s.ord;      sub {DL} n' d by n.ord;      sub {DL} r' d by r.ord;      sub {DL} t' h by t.ord;
  sub s.ord.osf t' by t.ord.osf;  sub [n.ord.osf r.ord.osf] d' by d.ord.osf;  sub t.ord.osf h' by h.ord.osf;
  sub s.ord t' by t.ord;  sub [n.ord r.ord] d' by d.ord;  sub t.ord h' by h.ord;
  ignore sub {LET} [n i j k] t' h;  ignore sub [n i j k] t' h {LET};
  sub [n i j k] t' h by t.ord;  sub t.ord h' by h.ord;''')
# Ordinal spacing. The superiors share one left bearing, so their distance from the
# figure before them follows that figure's right side at the superiors' height. The
# 1 and 4 (whose ink up there is a stem standing well in from the foot or bar below)
# and the tabular figures left them up to 280 units off, against 131 in "2nd". A pair
# adjustment in ss16 (GPOS) pulls the first superior in after any figure whose nearest
# ink is further from it than the 2's is in the old-style proportional "2nd" (the app's
# default figures), per suffix letter, so no ordinal sits looser than 2nd. Closer pairs
# (the round 0, 6, 9 and the overhanging 7) keep their spacing.
_ord_rows = {}
def ord_rows(n, right):
    """Ink edge of glyph n row by row, every 4 units: rightmost if right, else leftmost."""
    if (n, right) not in _ord_rows:
        p = path_of(n); b = p.bounds; rows = {}
        for y in range(int(b[1]) // 4 * 4, int(b[3]) + 1, 4):
            sp = hspans(p, y)
            if sp: rows[y] = max(q[1] for q in sp) if right else min(q[0] for q in sp)
        _ord_rows[n, right] = rows
    return _ord_rows[n, right]
def ord_pairs(fig, sup):
    """(dx, dy) from each row of fig's right edge to each row of sup's left edge, sup set after fig."""
    R, L = ord_rows(fig, True), ord_rows(sup, False)
    return [(x2 + W(fig) - x1, y2 - y1) for y1, x1 in R.items() for y2, x2 in L.items()]
def ord_gap(fig, sup):
    """Nearest ink between fig and the superior set after it."""
    return min(math.hypot(dx, dy) if dx > 0 else abs(dy) for dx, dy in ord_pairs(fig, sup))
def ord_need(fig, sup, T):
    """The advance change that brings the superior to nearest-ink distance T from fig."""
    return max(math.sqrt(T * T - dy * dy) - dx for dx, dy in ord_pairs(fig, sup) if abs(dy) < T)
# Round 14: the targets are pinned at the gaps the round-12 2 left in "2nd" (its
# ord_gap('two.osf', ...)), so the new 2's roomier top right does not loosen the other
# figures' ordinals; every figure, the 2 included, is still measured against them.
ORD_T = {'Regular': {'s': 124.05, 'n': 131.0, 'r': 130.0, 't': 119.19},
         'SemiBold': {'s': 119.01, 'n': 126.0, 'r': 125.0, 't': 114.49},
         'Bold': {'s': 114.37, 'n': 121.0, 'r': 121.0, 't': 109.26},
         'Light': {'s': 127.15, 'n': 134.08, 'r': 133.08, 't': 122.08},
         'Medium': {'s': 121.53, 'n': 128.5, 'r': 127.5, 't': 116.84},
         'ExtraBold': {'s': 110.59, 'n': 116.93, 'r': 117.74, 't': 105.0},
         'Black': {'s': 106.81, 'n': 112.85, 'r': 114.48, 't': 100.74}}[WEIGHT_NAME]   # the italic takes its weight's (the gaps are horizontal)
ORD_KERN = {}
for d in FIG:
    for figs, suffix in ((FORMS_O[d], '.ord.osf'), (FORMS_L[d], '.ord')):
        for fg in figs:
            for c in 'snrt':
                k = round(ord_need(fg, c + suffix, ORD_T[c]))
                if k <= -10: ORD_KERN[fg, c + suffix] = k       # under 10 units is not worth a pair
print('ss16 ordinals: target gaps', {c: round(t) for c, t in ORD_T.items()}, f'; {len(ORD_KERN)} figure-superior pairs pulled in')
# 97 vulgar fractions, standing alone
rules = [f"  ignore sub [{D} slash slash.keep fraction] @S16_D1' slash' [@S16_D2 @S16_D4]';", f"  ignore sub [{D} slash slash.keep fraction] @S16_D3' slash' @S16_D4';",
         f"  ignore sub @S16_D1' slash' [@S16_D2 @S16_D4]' [{D} slash slash.keep];", f"  ignore sub @S16_D3' slash' @S16_D4' [{D} slash slash.keep];",
         f"  ignore sub @S16_D1' slash' [@S16_D2 @S16_D4]' period {D};", f"  ignore sub @S16_D3' slash' @S16_D4' period {D};"]
for a_, b_, g in (('1', '2', 'onehalf'), ('1', '4', 'onequarter'), ('3', '4', 'threequarters')):
    rules.append(f"  sub @S16_D{a_}' slash' @S16_D{b_}' by {g};")
s16_lookup(97, 'S16_VULGAR', '\n'.join(rules))
# 98 diagonal fractions: dates, 3+ figure numerators, 4+ figure denominators, figures
# glued to letters and 0/1 stay as typed
rules = []
for n in range(1, 5):
    run = J([D] * n)
    rules.append(f"  sub {D} slash' {run} [slash slash.keep] by slash.keep;")
    rules.append(f"  sub [slash slash.keep] {run} slash' {D} by slash.keep;")
rules += [f"  sub {D} slash' {J([D] * n)} period {D} by slash.keep;" for n in range(1, 4)]
rules += [f"  sub {D} {D} {D} slash' {D} by slash.keep;", f"  sub {LET} {D} slash' {D} by slash.keep;", f"  sub {LET} {D} {D} slash' {D} by slash.keep;",
          f"  sub {D} slash' {D} {D} {D} {D} by slash.keep;"]
rules += [f"  ignore sub {D} @S16_D0 slash' {D};", f"  sub @S16_D0 slash' {D} by slash.keep;"]
s16_lookup(98, 'S16_FRAC_KEEP', '\n'.join(rules))
s16_lookup(98, 'S16_FRAC_SLASH', f"  sub {D} slash' {D} by fraction;")
s16_lookup(98, 'S16_FRAC_NUMR', "  rsub @S16_DSRC' [fraction @S16_NUMR] by @S16_NUMR_DST;")
s16_lookup(98, 'S16_FRAC_DNOM', "  sub [fraction @S16_DNOM] @S16_DSRC' by @S16_DNOM_DST;")
# 99 ratio colon, 100 cap hyphen
s16_lookup(99, 'S16_COLON', f"  sub {DL} colon' {DL} by colon.lf;\n  sub {DO} colon' {DO} by colon.of;")
s16_lookup(100, 'S16_CAPHY', f"  sub {UC} hyphen' [{UC} {D}] by hyphen.case;")
# 114 old-style operators: ×, −, ±, ≈ beside old-style figures (after ss02's 28x28 -> 28×28)
s16_lookup(114, 'S16_OSFOPS', f'''  sub {DO} [minus multiply plusminus approxequal]' {DO} by [minus.osf multiply.osf plusminus.osf approxequal.osf];
  sub {DO} space [minus multiply plusminus approxequal]' space {DO} by [minus.osf multiply.osf plusminus.osf approxequal.osf];
  sub [minus plusminus approxequal]' {DO} by [minus.osf plusminus.osf approxequal.osf];
  sub [plusminus approxequal]' space {DO} by [plusminus.osf approxequal.osf];''')
# 115 dimension-letter chains: B×C×H×W
s16_lookup(115, 'S16_BCHW', f'''  ignore sub {LET} {UC} x' {UC} x {UC};
  sub {UC} x' {UC} x {UC} by multiply.case;
  sub {UC} multiply.case {UC} x' {UC} by multiply.case;
  sub {UC} multiply' {UC} by multiply.case;''')
# 116 shape tuples: (28, 28) and [1, 28, 28] with a tight space
NUMCH = f'[{D} minus minus.osf period]'
rules = []
for n in range(1, 6):
    run = J([NUMCH] * n)
    rules.append(f"  sub [parenleft bracketleft] {run} comma space' [{D} minus minus.osf hyphen] by space.tuple;")
    rules.append(f"  sub space.tuple {run} comma space' [{D} minus minus.osf hyphen] by space.tuple;")
s16_lookup(116, 'S16_TUPLE', '\n'.join(rules))
# 117 percent after old-style figures; 118 figure, space, unit
s16_lookup(117, 'S16_PCT', f"  sub {DO} percent' by percent.osf;")
UNITS = sorted(['m s', 's', 'n s', 'H z', 'k H z', 'M H z', 'G H z', 'M B', 'G B', 'K B', 'k B', 'T B', 'p x', 'k g', 'f p s',
                'd B', 'm', 'c m', 'm m', 'k m', 'V', 'W', 'k W', 'm A', 'm g'], key=lambda u: -len(u.split()))
s16_lookup(118, 'S16_UNITS', '\n'.join(r for u in UNITS for r in (f"  ignore sub {D} space' {u} [{WD} hyphen];", f"  sub {D} space' {u} by space.unit;")))
# 120 numero: "No." before a figure
s16_lookup(120, 'S16_NUMERO', f"  ignore sub {LET} N' o' period';\n  sub N' o' period' space {D} by uni2116;\n  sub N' o' period' {D} by uni2116;")
# 111 matmul @ between spaces
s16_lookup(111, 'S16_ATOP', "  sub space at' space by at.op;")
# 121 version tag: v1.2.3
S16_TAIL.append('lookup S16_TAG_END { ' + J(f'sub {d}.tag by {d}.tag tag.end;' for d in FIG) + ' } S16_TAG_END;')
s16_lookup(121, 'S16_TAG1', f"  ignore sub {WD} v';\n  sub v' {D} period {D} by tag.v;  sub v' {D} {D} period {D} by tag.v;")
s16_lookup(121, 'S16_TAG2', f"  sub [tag.v @S16_TAGD period.tag] @S16_DSRC' by @S16_TAG_DST;\n  sub @S16_TAGD period' {D} by period.tag;")
s16_lookup(121, 'S16_TAG3', f"  ignore sub @S16_TAGD' [{D} @S16_TAGD period.tag];\n  sub @S16_TAGD' lookup S16_TAG_END;")
# 123 spark line (ss15) before 122 spark bars (ss16): {1,5,3,8}
s16_lookup(123, 'S16_SPARKL1', f"  sub braceleft' {D} comma {D} by sparkl.start;", feature='ss15')
rules = ["  sub sparkl.start @S16_DSRC' by @S16_SLFIRST_DST;", f"  sub @S16_SLEND comma' {D} by sparkl.sep;", "  sub @S16_SLEND braceright' by sparkl.end;"]
rules += [f"  sub @S16_SLEND{q} sparkl.sep @S16_D{d}' by sparkl.{q}_{d};" for q in range(10) for d in range(10)]
s16_lookup(123, 'S16_SPARKL2', '\n'.join(rules), feature='ss15')
s16_lookup(122, 'S16_SPARK1', f"  sub braceleft' {D} comma {D} by spark.start;")
s16_lookup(122, 'S16_SPARK2', f"  sub [spark.start spark.sep] @S16_DSRC' by @S16_SPARK_DST;\n  sub @S16_SPARK comma' {D} by spark.sep;\n  sub @S16_SPARK braceright' by spark.end;")
# 124 progress bar: [=====-----]
s16_lookup(124, 'S16_PBAR1', "  sub bracketleft' equal [equal hyphen] [equal hyphen] by pbar.start.f;\n  sub bracketleft' hyphen [equal hyphen] [equal hyphen] by pbar.start.e;")
s16_lookup(124, 'S16_PBAR2', '''  sub [pbar.start.f pbar.start.e pbar.fill pbar.empty] equal' by pbar.fill;
  sub [pbar.start.f pbar.start.e pbar.fill pbar.empty] hyphen' by pbar.empty;
  sub pbar.fill bracketright' by pbar.end.f;
  sub pbar.empty bracketright' by pbar.end.e;''')
# the protected hyphen and slash go back to the plain glyphs once every rule has run
s16_lookup(None, 'S16_KEEP_RESTORE', '  sub hyphen.keep by hyphen;\n  sub slash.keep by slash;')
S16_LOOKUPS[90].append('S16_KEEP_RESTORE'); S16_LOOKUPS[98].append('S16_KEEP_RESTORE')
S16_ACCEPTED = [1, 2, 3, 4, 5, 6, 7, 9, 16, 22, 23, 24, 25, 26, 50, 81, 84, 85, 86, 88, 90, 91, 92, 93, 96, 97, 98, 99,
                100, 102, 103, 104, 105, 111, 114, 115, 116, 117, 118, 120, 121, 122, 123, 124,
                125, 137, 145, 148, 166, 167, 169, 171, 200, 207]
assert sorted(S16_LOOKUPS) == S16_ACCEPTED, sorted(set(S16_ACCEPTED) ^ set(S16_LOOKUPS))
_ord = [l for l in S16_FEATURE]                     # definition order = lookup-list order
S16_TAIL.append('feature ss16 {\n  featureNames { name "Torchlette prose ligatures"; };\n'
                + ''.join(f'  lookup {l};\n' for l in _ord if S16_FEATURE[l] == 'ss16') + '} ss16;')
S16_TAIL.append('feature ss15 {\n' + ''.join(f'  lookup {l};\n' for l in _ord if S16_FEATURE[l] == 'ss15') + '} ss15;')
for id_ in S16_ACCEPTED:
    if id_ <= 99:
        S16_TAIL.append(f'feature cv{id_:02d} {{ ' + J(f'lookup {l};' for l in dict.fromkeys(S16_LOOKUPS[id_])) + f' }} cv{id_:02d};')
S16_FRONT = '\n'.join(S16_FRONT) + '\n'
S16_FEA = '\n'.join(S16_TAIL) + '\n'

# ===== modules: modules/*.py extend the font (the contract is modules/README.md) =====
# Each module file may define glyphs(ctx), features(ctx) and post(ctx); they run in
# sorted file-name order at three points: here, once every glyph above exists; just
# before the features are compiled; and just before the font is saved. MODULES (a
# comma list, or 'none') picks a subset. With no module files the font is unchanged.
import importlib.util, re
MODULE_DIR = os.path.join(HERE, 'modules')
GSUB_ANCHORS = ('classes', 'ss16_front', 'main', 'alternates', 'ss16')   # FEA's blocks, in compile order
GPOS_ANCHORS = ('mulish', 'ss16_ordinals', 'smallcap_kern')             # GPOS's lookup blocks, in order
SS16_OWNERS = {}                       # ss16 proposal id -> (module, the glyphs it adds), from ctx.ss16_owner
def write_ss16_owners():
    """The modules' ss16 declarations, as <PostScript name>.ss16.json beside DST, which
    verify_ss16.py finds for the full font and its web subset alike (the subset keeps the
    name); a build with none removes a stale file."""
    side = os.path.join(os.path.dirname(os.path.abspath(DST)), f"{font['name'].getDebugName(6)}.ss16.json")
    if not SS16_OWNERS:
        if os.path.exists(side): os.remove(side)
        return
    order = set(font.getGlyphOrder()); builtin = {g for v in S16.values() for g in v}; seen = {}
    for id_, (mod, gl) in sorted(SS16_OWNERS.items()):
        for g in gl:
            if g not in order: sys.exit(f'module {mod}: ss16_owner({id_}) names {g!r}, which the font does not have')
            if g in builtin: sys.exit(f'module {mod}: ss16_owner({id_}) names {g!r}, one of build.py\'s ss16 glyphs')
            if g in seen: sys.exit(f'module {mod}: ss16_owner({id_}) names {g!r}, already declared for {seen[g]}')
            seen[g] = id_
    import json
    with open(side, 'w') as fh:
        json.dump({str(i): {'module': m, 'glyphs': gl} for i, (m, gl) in sorted(SS16_OWNERS.items())}, fh, indent=1, sort_keys=True)
        fh.write('\n')
    print(f'modules: ss16 proposals {sorted(SS16_OWNERS)} declared in {side}')
MODULE_GSUB, MODULE_GPOS = [], []      # ((placement, anchor), module, text), in run order
OWNER = {}                             # glyph name -> the module that added it
def _module_names():
    have = sorted(f[:-3] for f in os.listdir(MODULE_DIR)
                  if f.endswith('.py') and not f.startswith(('verify_', '_'))) if os.path.isdir(MODULE_DIR) else []
    bad = [n for n in have if not re.fullmatch(r'[a-z][a-z0-9_]*', n)]
    if bad: sys.exit(f'modules: bad module file names {bad} (lowercase letters, digits and _, starting with a letter)')
    want = os.environ.get('MODULES', '').strip()
    if want == 'none': return []
    if not want: return have
    sel = {w.strip() for w in want.split(',') if w.strip()}
    if sel - set(have): sys.exit(f'MODULES: no module file in modules/ for {sorted(sel - set(have))}')
    return [n for n in have if n in sel]
def _placement(anchors, before, after):
    if before and after: raise ValueError('pass before= or after=, not both')
    where, anchor = ('before', before) if before else ('after', after or anchors[-1])
    if anchor not in anchors: raise ValueError(f'unknown anchor {anchor!r}; one of {anchors}')
    if (where, anchor) == ('before', 'classes'): raise ValueError("nothing goes before the language systems; use after='classes'")
    return where, anchor
class ModuleContext:
    """What a module's phase functions get. ctx.NAME reads build.py's global NAME (glyf,
    hmtx, font, add, path_of, SV, XH, STYLE ...); ctx.globals is that dict itself, for
    rebinding a global. Other attributes set on ctx persist across the module's phases."""
    def __init__(self, module): self.module = module; self.globals = globals()
    def __getattr__(self, k):
        try: return globals()[k]
        except KeyError: raise AttributeError(f'{k!r}: not an attribute of the context nor a global of build.py') from None
    def log(self, *a): print(f'[{self.module}]', *a)
    def ss16_owner(self, id_, glyphs):
        """Declare that ss16 proposal id_ (an int not used by build.py's) adds these glyphs;
        verify_ss16.py reads the declarations from <PostScript name>.ss16.json beside the font."""
        if type(id_) is not int: raise TypeError(f'ss16_owner: id {id_!r} must be an int')
        if id_ in S16_ACCEPTED: raise ValueError(f'ss16_owner: id {id_} is one of build.py\'s ss16 proposals')
        owner, have = SS16_OWNERS.setdefault(id_, (self.module, []))
        if owner != self.module: raise ValueError(f'ss16_owner: id {id_} is already declared by module {owner}')
        have.extend(g for g in ([glyphs] if isinstance(glyphs, str) else glyphs) if g not in have)
    def map(self, uni, glyph):
        """Map code point uni to glyph in every Unicode cmap subtable."""
        if glyph not in glyf.glyphs: raise KeyError(f'map U+{uni:04X}: no glyph {glyph!r}')
        if uni > 0xFFFF and not any(t.isUnicode() and t.format in (12, 13) for t in font['cmap'].tables):
            raise ValueError(f'U+{uni:04X} needs a format 12 cmap subtable, which the font does not have')
        for t in font['cmap'].tables:
            if t.isUnicode() and (uni <= 0xFFFF or t.format in (12, 13)): t.cmap[uni] = glyph
    def gsub(self, text, before=None, after=None):
        """Feature-file text (lookups, feature blocks, classes) compiled with build.py's own GSUB."""
        MODULE_GSUB.append((_placement(GSUB_ANCHORS, before, after), self.module, text.rstrip('\n') + '\n'))
    def gpos(self, text, before=None, after=None):
        """Feature-file text with positioning rules, compiled on its own (after FEA_HEAD's classes)."""
        MODULE_GPOS.append((_placement(GPOS_ANCHORS, before, after), self.module, text.rstrip('\n') + '\n'))
MODULES_RUN = []
for _n in _module_names():
    _spec = importlib.util.spec_from_file_location(f'tsmod_{_n}', os.path.join(MODULE_DIR, _n + '.py'))
    _m = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _m              # registered first, as import does (dataclasses, pickle, typing look it up)
    _spec.loader.exec_module(_m)
    MODULES_RUN.append((_n, _m, ModuleContext(_n)))
if MODULES_RUN: print('modules:', ', '.join(n for n, _, _ in MODULES_RUN))
def _glyph_sig(g):
    """A glyph's outline (points, flags, contours or components) and its hmtx entry, by value."""
    if g not in glyf.glyphs: return None
    o = glyf[g]
    if o.isComposite():
        shape = tuple((c.glyphName, c.x, c.y, c.flags, tuple(map(tuple, getattr(c, 'transform', ()))))
                      for c in o.components)
    elif o.numberOfContours > 0:
        shape = (tuple(map(tuple, o.coordinates)), bytes(o.flags), tuple(o.endPtsOfContours))
    else:
        shape = ()
    return shape, tuple(hmtx[g]) if g in hmtx.metrics else None
def _cmap_sig():
    """Every cmap subtable, keyed by (platformID, platEncID, format, language), with its full mapping."""
    return {(t.platformID, t.platEncID, t.format, getattr(t, 'language', 0)): dict(t.cmap) for t in font['cmap'].tables}
def _cmap_changes(before, after, allowed):
    """Code points mapped before whose mapping changed in any subtable (a removed subtable
    unmaps all of its code points), outside allowed; and the subtables added and removed.
    A new subtable may repeat a code point's existing mapping, and new code points are free."""
    prev = {}
    for mp in before.values():
        for u, g in mp.items(): prev.setdefault(u, set()).add(g)
    bad = set()
    for k in set(before) | set(after):
        b, a = before.get(k, {}), after.get(k, {})
        for u in set(b) | set(a):
            if b.get(u) == a.get(u) or u in allowed or u not in prev: continue
            if k not in before and prev[u] == {a.get(u)}: continue
            bad.add(u)
    # A client reads one Unicode subtable, the best it knows: fontTools and HarfBuzz prefer
    # (3,10), then (0,6), (0,4), (3,1), (0,3) ... So the best subtable after the phase, and
    # every Unicode subtable it added (one some client may prefer), must still map every
    # code point of the old best one to the same glyph (a format 4 table, those it can hold).
    order = [(3, 10), (0, 6), (0, 4), (3, 1), (0, 3), (0, 2), (0, 1), (0, 0)]
    def best(sig):
        ks = sorted((k for k in sig if k[:2] in order and k[2] != 14), key=lambda k: order.index(k[:2]))
        return ks[0] if ks else None
    old_best = before.get(best(before), {})
    for k in {best(after)} | {k for k in set(after) - set(before) if k[:2] in order and k[2] != 14}:
        if k is None: continue
        bad.update(u for u, g in old_best.items() if u not in allowed and (k[2] != 4 or u <= 0xFFFF) and after[k].get(u) != g)
    return sorted(bad), sorted(set(after) - set(before)), sorted(set(before) - set(after))
def run_modules(phase):
    for n, m, ctx in MODULES_RUN:
        fn = getattr(m, phase, None)
        if not callable(fn): continue
        # In any phase a module may add glyphs and change its own, but no other glyph
        # (build.py's or another module's) unless it lists it in GLYPH_OVERRIDE, and
        # no existing code point's mapping unless it lists it in CMAP_OVERRIDE.
        before_g = {g: _glyph_sig(g) for g in font.getGlyphOrder()}; before_c = _cmap_sig()
        fn(ctx)
        own = {g for g, o in OWNER.items() if o == n} | set(getattr(m, 'GLYPH_OVERRIDE', ()))
        hit = [g for g, s in before_g.items() if g not in own and _glyph_sig(g) != s]
        if hit: sys.exit(f'module {n} ({phase}) changed glyphs it does not own: '
                         f'{[(g, OWNER.get(g, "build.py")) for g in hit]} (list them in GLYPH_OVERRIDE)')
        for g in font.getGlyphOrder():
            if g not in OWNER and g not in before_g: OWNER[g] = n
        remapped, added_t, removed_t = _cmap_changes(before_c, _cmap_sig(), set(getattr(m, 'CMAP_OVERRIDE', ())))
        if remapped: sys.exit(f'module {n} ({phase}) remapped existing code points {[f"U+{u:04X}" for u in remapped[:20]]}'
                              + (f' and {len(remapped) - 20} more' if len(remapped) > 20 else '')
                              + (f' (cmap subtables added {added_t}, removed {removed_t})' if added_t or removed_t else '')
                              + ' (list them in CMAP_OVERRIDE)')
def module_fea(blocks):
    """build.py's GSUB blocks, in order, with each module's text before or after its anchor."""
    out = []
    for k, text in blocks:
        out += [t for p, _, t in MODULE_GSUB if p == ('before', k)] + [text] + [t for p, _, t in MODULE_GSUB if p == ('after', k)]
    return ''.join(out)
GLYPHS_BEFORE_MODULES = set(font.getGlyphOrder())
run_modules('glyphs')
# ss16's word-boundary classes again, now with the letters the modules added (a Greek
# alpha next to "gradient" keeps the logotype from forming). build.py's own glyphs
# keep the classes they had; with no module glyphs nothing changes.
_cmap_m = font.getBestCmap()
_letters_m = {g for u, g in _cmap_m.items() if unicodedata.category(chr(u))[0] in 'LN' or chr(u) == '_'}
_wordish_m = lambda g: bool(g.split('.')[0]) and all(q in _letters_m for q in g.split('.')[0].split('_'))
_word_new = {g for g in font.getGlyphOrder() if g not in GLYPHS_BEFORE_MODULES or (g in _letters_m and g not in _letters)}
_word_new = {g for g in _word_new if g != '.notdef' and (g in _letters_m or _wordish_m(g))} - set(S16_WORD)
if _word_new:
    _old_cls = f"@S16_WORD = {cls(S16_WORD)};\n@S16_WORDNOS = {cls(g for g in S16_WORD if g != 's')};"
    assert S16_FRONT.count(_old_cls) == 1
    S16_WORD = sorted(set(S16_WORD) | _word_new)
    S16_FRONT = S16_FRONT.replace(_old_cls, f"@S16_WORD = {cls(S16_WORD)};\n@S16_WORDNOS = {cls(g for g in S16_WORD if g != 's')};")
    print(f'modules: {len(_word_new)} glyphs join ss16\'s word letters')
# --- name: a modified font never ships under the original name -----------------
# Mulish's OFL.txt declares no Reserved Font Name; the new name is required anyway
# by good practice and keeps the two fonts apart in a user's font menu.
# The font version: the one line in VERSION beside this file, such as 0.504 for
# release v0.5.4 (name ID 5 'Version 0.504', head.fontRevision 0.504, the form
# fontbakery checks). Set it there once per release; the Makefile rebuilds on a change.
VERSION = open(os.path.join(HERE, 'VERSION')).read().strip()
assert len(VERSION) == 5 and VERSION[1] == '.' and VERSION.replace('.', '', 1).isdigit(), f'VERSION file: {VERSION!r} is not like 0.504'
COPYRIGHT = ('Copyright 2016 The Mulish Project Authors (https://github.com/googlefonts/mulish). '
             'Copyright 2026 The Torchlette Authors.')
LICENSE = ('This Font Software is licensed under the SIL Open Font License, Version 1.1. '
           'This license is available with a FAQ at: https://openfontlicense.org')
# Regular, Italic, Bold and Bold Italic form the style-linked family "Torchlette Sans";
# SemiBold and the other weights (Light, Medium, ExtraBold, Black), each with its italic,
# are their own legacy family (nameID 1/2) and join the typographic family by 16/17.
RIBBI = STYLE in ('Regular', 'Bold', 'Italic', 'BoldItalic')
STYLE_NAME = STYLE if not ITALIC else 'Italic' if WEIGHT_NAME == 'Regular' else f'{WEIGHT_NAME} Italic'   # 'Bold Italic'
NAMES = {
    0: COPYRIGHT,
    1: 'Torchlette Sans' if RIBBI else f'Torchlette Sans {WEIGHT_NAME}',
    2: STYLE_NAME if RIBBI else 'Italic' if ITALIC else 'Regular',
    3: f'{VERSION};NONE;TorchletteSans-{STYLE}',
    4: f'Torchlette Sans {STYLE_NAME}',
    5: f'Version {VERSION}',
    6: f'TorchletteSans-{STYLE}',
    8: 'The Torchlette Authors',
    9: 'Vernon Adams (Mulish); The Torchlette Authors',
    13: LICENSE,
    14: 'https://openfontlicense.org',
}
if not RIBBI: NAMES.update({16: 'Torchlette Sans', 17: STYLE_NAME})
nt = font['name']
for r in list(nt.names):                      # drop Mulish's family/designer records we replace
    if r.nameID in (1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14, 16, 17, 25): nt.removeNames(nameID=r.nameID)
for nid, text in NAMES.items():
    nt.setName(text, nid, 3, 1, 0x409)        # Windows, Unicode BMP, English (US), as in Mulish
font['head'].fontRevision = float(VERSION)
# Reproducible output: fixed timestamps rather than the time of the build.
font['head'].created = font['head'].modified = 3876249600   # 2026-10-31 00:00 UTC, seconds since 1904
font.recalcTimestamp = False
if 'OS/2' in font: font['OS/2'].achVendID = 'NONE'
# The instancer leaves usWeightClass at the source wght (324 for Regular) and the
# REGULAR bit set; give each style its nominal class and style bits.
os2 = font['OS/2']
os2.usWeightClass = WEIGHT_CLASS
os2.fsSelection = (os2.fsSelection & ~0b1100001) | {'Regular': 1 << 6, 'Bold': 1 << 5}.get(WEIGHT_NAME, 0) | (1 if ITALIC else 0)   # the others as SemiBold
font['head'].macStyle = (font['head'].macStyle & ~0b11) | (1 if WEIGHT_NAME == 'Bold' else 0) | (2 if ITALIC else 0)

SC_CLASSES = (
    f"@LACC = [{' '.join(l for l, c, s in SC_ACC if l)}];\n@SCACC_L = [{' '.join(s for l, c, s in SC_ACC if l)}];\n"
    f"@UACC = [{' '.join(c for l, c, s in SC_ACC)}];\n@SCACC_U = [{' '.join(s for l, c, s in SC_ACC)}];\n"
    f"@SYM = [{' '.join(n for n in SC_SYMBOLS if n != 'slash')}];\n@SCSYM = [{' '.join(n + '.sc' for n in SC_SYMBOLS if n != 'slash')}];\n"
    f"@LX = [{' '.join(a for a, b in SC_LX)}];\n@SCLX = [{' '.join(b for a, b in SC_LX)}];\n"
    f"@UX = [{' '.join(a for a, b in SC_UX)}];\n@SCUX = [{' '.join(b for a, b in SC_UX)}];\n")

# --- features: built in a scratch copy, then appended to the existing GSUB ------
# FEA_HEAD (language systems and classes), S16_FRONT, FEA_MAIN, ALT_FEA and S16_FEA
# are compiled in this order; modules' GSUB text goes before or after any of them.
FEA_HEAD = """
languagesystem DFLT dflt; languagesystem latn dflt;
@LNUM = [zero one two three four five six seven eight nine];
@TOSF = [zero.tosf one.tosf two.tosf three.tosf four.tosf five.tosf six.tosf seven.tosf eight.tosf nine.tosf];
@OSF = [zero.osf one.osf two.osf three.osf four.osf five.osf six.osf seven.osf eight.osf nine.osf];
@PNUM = [zero.pnum one.pnum two.pnum three.pnum four.pnum five.pnum six.pnum seven.pnum eight.pnum nine.pnum];
@SEVEN8 = [seven.ss08 seven.pnum.ss08 seven.tosf.ss08 seven.osf.ss08 seven.sc.ss08 seven.sc.tf.ss08];
@SCNUM = [zero.sc one.sc two.sc three.sc four.sc five.sc six.sc seven.sc eight.sc nine.sc];
@SCTF = [zero.sc.tf one.sc.tf two.sc.tf three.sc.tf four.sc.tf five.sc.tf six.sc.tf seven.sc.tf eight.sc.tf nine.sc.tf];
@D = [@LNUM @TOSF @OSF @PNUM @SEVEN8 @SCNUM @SCTF];
@LC = [a b c d e f g h i j k l m n o p q r s t u v w x y z];
@UC = [A B C D E F G H I J K L M N O P Q R S T U V W X Y Z];
@SC = [A.sc B.sc C.sc D.sc E.sc F.sc G.sc H.sc I.sc J.sc K.sc L.sc M.sc N.sc O.sc P.sc Q.sc R.sc S.sc T.sc U.sc V.sc W.sc X.sc Y.sc Z.sc];
""" + SC_CLASSES
FEA_MAIN = """
feature liga { sub f fi by f_f_i; sub f fl by f_f_l; sub f f i by f_f_i; sub f f l by f_f_l; sub f f by f_f; sub t t by t_t; } liga;
feature ss01 { sub T h by T_h; } ss01;
feature ss03 { sub t h by t_h; } ss03;
feature ss02 {
  sub [hyphen hyphen.sc] greater by arrowright; sub less equal by lessequal; sub greater equal by greaterequal;
  sub period period period by ellipsis; sub @SCNUM X.sc' @SCNUM by multiply.sc; sub @D [x X.sc]' @D by multiply;   # X.sc: smcp runs first
} ss02;
# Mulish's own onum lookup (digits -> .tosf) runs first; these lookups follow it in
# this order, so onum alone ends proportional, onum + tnum ends tabular, and an
# explicit pnum wins over tnum.
feature onum { sub @TOSF by @OSF; } onum;
feature tnum { sub @OSF by @TOSF; sub @PNUM by @LNUM; } tnum;
feature pnum { sub @TOSF by @OSF; sub @LNUM by @PNUM; } pnum;
feature ss08 { sub [seven seven.pnum seven.tosf seven.osf] by [seven.ss08 seven.pnum.ss08 seven.tosf.ss08 seven.osf.ss08]; } ss08;
# Small caps come in two parts. The letters and most symbols run first of all (moved
# to the front of the lookup list below), so ligatures can't form under them. Figures,
# the slash and the times sign run last, after Mulish's frac and after onum, pnum and
# tnum, so fractions still build, and tnum can then pick the tabular small-cap figures.
lookup SC_LC { sub @LC by @SC; sub @LACC by @SCACC_L; sub @LX by @SCLX; sub @SYM by @SCSYM; } SC_LC;
# the encoded fi/fl ligatures and the DŽ, LJ, NJ digraphs, as letter sequences;
# smcp takes the lowercase and titlecase forms, c2sc the capitals and titlecase forms
lookup SC_LIG { sub fi by F.sc I.sc; sub fl by F.sc L.sc;
  sub uni01C6 by D.sc Zcaron.sc; sub uni01C9 by L.sc J.sc; sub uni01CC by N.sc J.sc;
  sub uni01C5 by D.sc Zcaron.sc; sub uni01C8 by L.sc J.sc; sub uni01CB by N.sc J.sc; } SC_LIG;
lookup SC_UCLIG { sub uni01C4 by D.sc Zcaron.sc; sub uni01C7 by L.sc J.sc; sub uni01CA by N.sc J.sc;
  sub uni01C5 by D.sc Zcaron.sc; sub uni01C8 by L.sc J.sc; sub uni01CB by N.sc J.sc; } SC_UCLIG;
lookup SC_UC { sub @UC by @SC; sub @UACC by @SCACC_U; sub @UX by @SCUX; sub @SYM by @SCSYM; } SC_UC;
lookup SC_FIG { sub [@LNUM @TOSF @OSF @PNUM] by [@SCNUM @SCNUM @SCNUM @SCNUM]; sub [seven.ss08 seven.pnum.ss08 seven.tosf.ss08 seven.osf.ss08] by seven.sc.ss08; sub slash by slash.sc; sub multiply by multiply.sc; } SC_FIG;
lookup SC_TAB { sub @SCNUM by @SCTF; sub seven.sc.ss08 by seven.sc.tf.ss08; } SC_TAB;
feature smcp { lookup SC_LC; lookup SC_LIG; lookup SC_FIG; } smcp;
feature c2sc { lookup SC_UC; lookup SC_UCLIG; lookup SC_FIG; } c2sc;
feature tnum { lookup SC_TAB; } tnum;
"""
FEA = FEA_HEAD + S16_FRONT + FEA_MAIN
run_modules('features')
scratch = TTFont(SRC)
scratch.setGlyphOrder(font.getGlyphOrder()); font.getReverseGlyphMap(rebuild=True)
for n in font.getGlyphOrder():                # every glyph this script added or changed
    scratch['glyf'][n] = glyf[n]; scratch['hmtx'][n] = hmtx[n]
del scratch['GSUB']
addOpenTypeFeaturesFromString(scratch, module_fea([('classes', FEA_HEAD), ('ss16_front', S16_FRONT), ('main', FEA_MAIN), ('alternates', ALT_FEA), ('ss16', S16_FEA)]))
if MODULE_GSUB and 'GPOS' in scratch:
    sys.exit('modules: positioning rules in ctx.gsub() text; pass them to ctx.gpos()')
for r in scratch['name'].names:              # ss16's feature name (nameID 256 and up)
    if r.nameID >= 256 and font['name'].getName(r.nameID, r.platformID, r.platEncID, r.langID) is None:
        font['name'].setName(r.toUnicode(), r.nameID, r.platformID, r.platEncID, r.langID)
new = scratch['GSUB'].table
old = font['GSUB'].table
base = len(old.LookupList.Lookup)
def walk(obj, seen=None):
    seen = seen if seen is not None else set()
    if id(obj) in seen: return
    seen.add(id(obj)); yield obj
    if isinstance(obj, list):
        for x in obj: yield from walk(x, seen)
    elif hasattr(obj, '__dict__') and type(obj).__module__.startswith('fontTools.ttLib.tables.otTables'):
        for v in vars(obj).values():
            if isinstance(v, (list,)) or hasattr(v, '__dict__'): yield from walk(v, seen)
for lk in new.LookupList.Lookup:              # nested lookups inside contextual rules, at any depth
    for obj in walk(lk):                      # (feaLib writes chaining rules in format 1, 2 or 3)
        if type(obj).__name__ in ('SubstLookupRecord', 'LookupRecord'):
            obj.LookupListIndex += base
old.LookupList.Lookup.extend(new.LookupList.Lookup)
old.LookupList.LookupCount = len(old.LookupList.Lookup)
for fr in new.FeatureList.FeatureRecord:
    fr.Feature.LookupListIndex = [i + base for i in fr.Feature.LookupListIndex]
    fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
records = old.FeatureList.FeatureRecord
added = []
for fr in new.FeatureList.FeatureRecord:
    same = [r for r in records if r.FeatureTag == fr.FeatureTag]
    if same:                                   # shapers read one record per tag: extend Mulish's own
        for r in same:
            r.Feature.LookupListIndex = sorted(r.Feature.LookupListIndex + fr.Feature.LookupListIndex)
            r.Feature.LookupCount = len(r.Feature.LookupListIndex)
    else:
        added.append(fr)
merged = sorted(range(len(records) + len(added)),
                key=lambda i: (records + added)[i].FeatureTag)   # FeatureList must stay sorted by tag
remap = {old_i: new_i for new_i, old_i in enumerate(merged)}
old.FeatureList.FeatureRecord = [(records + added)[i] for i in merged]
old.FeatureList.FeatureCount = len(merged)
for sr in old.ScriptList.ScriptRecord:
    for ls in [sr.Script.DefaultLangSys] + [l.LangSys for l in sr.Script.LangSysRecord]:
        if not ls: continue
        ls.FeatureIndex = sorted([remap[i] for i in ls.FeatureIndex] + [remap[len(records) + j] for j in range(len(added))])
        ls.FeatureCount = len(ls.FeatureIndex)

# --- ss16's one positioning lookup: the ordinals' figure-superior pairs ------------
# compiled on the scratch copy and appended to Mulish's GPOS as ss16 and cv96
if 'GPOS' in scratch: del scratch['GPOS']
addOpenTypeFeaturesFromString(scratch, 'languagesystem DFLT dflt; languagesystem latn dflt;\nlookup S16_ORD_POS {\n'
    + ''.join(f'  pos {a} {b} {k};\n' for (a, b), k in sorted(ORD_KERN.items())) + '} S16_ORD_POS;\n'
    + 'feature ss16 { lookup S16_ORD_POS; } ss16;\nfeature cv96 { lookup S16_ORD_POS; } cv96;\n', tables=['GPOS'])
gnew, gold = scratch['GPOS'].table, font['GPOS'].table
gbase = len(gold.LookupList.Lookup)
GPOS_MULISH_N = gbase                         # Mulish's own GPOS lookups (the modules' 'mulish' block)
gold.LookupList.Lookup.extend(gnew.LookupList.Lookup); gold.LookupList.LookupCount = len(gold.LookupList.Lookup)
grecs = gold.FeatureList.FeatureRecord
assert not {r.FeatureTag for r in grecs} & {'ss16', 'cv96'}
for fr in gnew.FeatureList.FeatureRecord:
    fr.Feature.LookupListIndex = [i + gbase for i in fr.Feature.LookupListIndex]
gall = grecs + gnew.FeatureList.FeatureRecord
gmerged = sorted(range(len(gall)), key=lambda i: gall[i].FeatureTag)
gremap = {o: n for n, o in enumerate(gmerged)}
gold.FeatureList.FeatureRecord = [gall[i] for i in gmerged]; gold.FeatureList.FeatureCount = len(gall)
for sr in gold.ScriptList.ScriptRecord:
    for ls in [sr.Script.DefaultLangSys] + [l.LangSys for l in sr.Script.LangSysRecord]:
        if not ls: continue
        ls.FeatureIndex = sorted([gremap[i] for i in ls.FeatureIndex] + [gremap[len(grecs) + j] for j in range(len(gnew.FeatureList.FeatureRecord))])
        ls.FeatureCount = len(ls.FeatureIndex)

# --- round 13: small-cap kerning ---------------------------------------------------
# Mulish kerns its capitals; the small caps had no pairs at all (T.sc O.sc, A.sc V.sc
# set at full sidebearings). Each capital pair of the heavier instance the small caps
# are drawn from (its kerning, so it fits their weight) is carried over to the .sc
# glyphs, times SC_SCALE and SC_K, like the sidebearings: letters (accented ones in
# their base's class), figures and the small-cap punctuation with one another, and
# with the punctuation small caps leave as it is (period, comma, colon, guillemets ...).
# Pairs of two plain glyphs stay with Mulish's own lookup. Glyph pairs (Mulish's
# exceptions) come before the class pairs, as in Mulish.
SC_KERN_SRC = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ') | {c for _, c, _ in SC_ACC} | set(DIGITS) | set(SC_SYMBOLS)
_rev = {g: u for u, g in font.getBestCmap().items()}
def sc_kern_map(g):
    """(the glyph g stands for in small-cap text, whether it is a small cap) or None."""
    if g in SC_KERN_SRC and g + '.sc' in glyf.glyphs: return g + '.sc', True
    if g + '.sc' not in glyf.glyphs and g in _rev and unicodedata.category(chr(_rev[g]))[0] in 'PS': return g, False
    return None
_scg = sc_font['GPOS'].table
SC_KERN_PAIRS, SC_KERN_RULES, _fea_g, _fea_c = 0, 0, [], []
def _sc_v(x): return round((x or 0) * SC_SCALE * SC_K)
for _i in sorted({i for fr in _scg.FeatureList.FeatureRecord if fr.FeatureTag == 'kern' for i in fr.Feature.LookupListIndex}):
    _lk = _scg.LookupList.Lookup[_i]
    for st in _lk.SubTable:
        if _lk.LookupType == 9: st = st.ExtSubTable
        cov = st.Coverage.glyphs
        if st.Format == 1:
            for a, ps in zip(cov, st.PairSet):
                ma = sc_kern_map(a)
                if not ma: continue
                for rec in ps.PairValueRecord:
                    mb = sc_kern_map(rec.SecondGlyph); v = _sc_v(getattr(rec.Value1, 'XAdvance', 0) if rec.Value1 else 0)
                    if mb and (ma[1] or mb[1]) and v:
                        _fea_g.append(f'  pos {ma[0]} {mb[0]} {v};\n'); SC_KERN_PAIRS += 1; SC_KERN_RULES += 1
        else:
            c1 = {}
            for g in cov: c1.setdefault(st.ClassDef1.classDefs.get(g, 0), []).append(g)
            c2 = {}
            for g, c in st.ClassDef2.classDefs.items(): c2.setdefault(c, []).append(g)
            split = lambda gs: [[m[0] for m in map(sc_kern_map, sorted(gs)) if m and m[1] == k] for k in (True, False)]
            c1s = {c: split(gs) for c, gs in c1.items()}; c2s = {c: split(gs) for c, gs in c2.items() if c}
            for k1, (s1, p1) in sorted(c1s.items()):
                for k2, (s2, p2) in sorted(c2s.items()):
                    v = _sc_v(getattr(st.Class1Record[k1].Class2Record[k2].Value1, 'XAdvance', 0) if st.Class1Record[k1].Class2Record[k2].Value1 else 0)
                    if not v: continue
                    for L, R in ((s1, s2), (s1, p2), (p1, s2)):
                        if L and R:
                            _fea_c.append(f'  pos [{" ".join(L)}] [{" ".join(R)}] {v};\n'); SC_KERN_PAIRS += len(L) * len(R); SC_KERN_RULES += 1
if 'GPOS' in scratch: del scratch['GPOS']
addOpenTypeFeaturesFromString(scratch, 'languagesystem DFLT dflt; languagesystem latn dflt;\nlookup SC_KERN {\n  lookupflag IgnoreMarks;\n'
    + ''.join(_fea_g) + '  subtable;\n' + ''.join(_fea_c) + '} SC_KERN;\nfeature kern { lookup SC_KERN; } kern;\n', tables=['GPOS'])
gnew = scratch['GPOS'].table
gbase = len(gold.LookupList.Lookup)
gold.LookupList.Lookup.extend(gnew.LookupList.Lookup); gold.LookupList.LookupCount = len(gold.LookupList.Lookup)
for r in gold.FeatureList.FeatureRecord:      # one record per tag: extend Mulish's kern
    if r.FeatureTag == 'kern':
        r.Feature.LookupListIndex = sorted(r.Feature.LookupListIndex + [gbase + i for i in range(len(gnew.LookupList.Lookup))])
        r.Feature.LookupCount = len(r.Feature.LookupListIndex)
print(f'small-cap kerning: {SC_KERN_PAIRS} pairs in {SC_KERN_RULES} rules (x{SC_SCALE * SC_K:.3f}); sidebearing scale SC_K {SC_K:.3f} + {SC_TRACK_C:g}')

# --- modules' positioning: each ctx.gpos() text compiled on its own, merged into GPOS,
# then its lookups moved before or after the anchor block it named
_LOOKUP_RECORDS = ('SubstLookupRecord', 'PosLookupRecord', 'LookupRecord')
def _merge_table(old, new):
    """Append new's lookups to old (renumbering nested records) and its features: a tag old
    has gains the lookups, a new tag gets a record in every language system. Returns the
    indices of the appended lookups."""
    base = len(old.LookupList.Lookup)
    for lk in new.LookupList.Lookup:
        for obj in walk(lk):
            if type(obj).__name__ in _LOOKUP_RECORDS: obj.LookupListIndex += base
    old.LookupList.Lookup.extend(new.LookupList.Lookup); old.LookupList.LookupCount = len(old.LookupList.Lookup)
    records, added = old.FeatureList.FeatureRecord, []
    for fr in new.FeatureList.FeatureRecord:
        idx = [i + base for i in fr.Feature.LookupListIndex]
        same = [r for r in records if r.FeatureTag == fr.FeatureTag]
        for r in same:
            r.Feature.LookupListIndex = sorted(set(r.Feature.LookupListIndex + idx)); r.Feature.LookupCount = len(r.Feature.LookupListIndex)
        if not same:
            fr.Feature.LookupListIndex = idx; fr.Feature.LookupCount = len(idx); added.append(fr)
    allr = records + added
    merged = sorted(range(len(allr)), key=lambda i: allr[i].FeatureTag)
    remap = {o: n for n, o in enumerate(merged)}
    old.FeatureList.FeatureRecord = [allr[i] for i in merged]; old.FeatureList.FeatureCount = len(allr)
    for sr in old.ScriptList.ScriptRecord:
        for ls in [sr.Script.DefaultLangSys] + [l.LangSys for l in sr.Script.LangSysRecord]:
            if not ls: continue
            ls.FeatureIndex = sorted([remap[i] for i in ls.FeatureIndex] + [remap[len(records) + j] for j in range(len(added))])
            ls.FeatureCount = len(ls.FeatureIndex)
    return list(range(base, len(old.LookupList.Lookup)))
def _reorder_lookups(table, order):
    pos = {o: n for n, o in enumerate(order)}
    lks = table.LookupList.Lookup
    for lk in lks:
        for obj in walk(lk):
            if type(obj).__name__ in _LOOKUP_RECORDS: obj.LookupListIndex = pos[obj.LookupListIndex]
    table.LookupList.Lookup = [lks[i] for i in order]
    for r in table.FeatureList.FeatureRecord:
        r.Feature.LookupListIndex = sorted(pos[i] for i in r.Feature.LookupListIndex)
if MODULE_GPOS:
    _blocks = {'mulish': list(range(GPOS_MULISH_N)), 'ss16_ordinals': list(range(GPOS_MULISH_N, gbase)),
               'smallcap_kern': list(range(gbase, len(gold.LookupList.Lookup)))}
    _slots = {}
    for placement, mod, text in MODULE_GPOS:
        if 'GPOS' in scratch: del scratch['GPOS']
        addOpenTypeFeaturesFromString(scratch, FEA_HEAD + text, tables=['GPOS'])
        if 'GPOS' not in scratch: continue
        _slots.setdefault(placement, []).extend(_merge_table(gold, scratch['GPOS'].table))
    _order = [i for a in GPOS_ANCHORS for i in _slots.get(('before', a), []) + _blocks[a] + _slots.get(('after', a), [])]
    assert sorted(_order) == list(range(len(gold.LookupList.Lookup)))
    _reorder_lookups(gold, _order)
    print('modules: GPOS lookups', {f'{w} {a}': len(v) for (w, a), v in _slots.items()})

# --- small caps run first ------------------------------------------------------
# Lookups apply in LookupList order. Mulish's liga (fi, fl) and our ligatures come
# before smcp/c2sc in the list, so "office" in small caps would keep an fi ligature
# and "MNIST" next to a Th would miss. Move the smcp and c2sc lookups to the front
# and renumber every reference: feature records and nested lookup records alike.
lookups = old.LookupList.Lookup
def maps_figures(i):
    return any('zero' in (getattr(st, 'mapping', None) or {}) or 'slash' in (getattr(st, 'mapping', None) or {})
               for st in lookups[i].SubTable)
first = sorted({i for r in old.FeatureList.FeatureRecord if r.FeatureTag in ('smcp', 'c2sc')
                for i in r.Feature.LookupListIndex if not maps_figures(i)})   # SC_FIG stays late
order = first + [i for i in range(len(lookups)) if i not in first]
pos = {o: n for n, o in enumerate(order)}
for lk in lookups:
    for obj in walk(lk):
        if type(obj).__name__ in ('SubstLookupRecord', 'LookupRecord'):
            obj.LookupListIndex = pos[obj.LookupListIndex]
old.LookupList.Lookup = [lookups[i] for i in order]
for r in old.FeatureList.FeatureRecord:
    r.Feature.LookupListIndex = sorted(pos[i] for i in r.Feature.LookupListIndex)

# --- round 12: smooth points stay smooth after scaling and rounding ----------------
# Scaling (xscale, the small caps), the piecewise vertical remap (whose zone edges cut
# through curves) and rounding to the grid all nudge a smooth on-curve point off the
# line through its handles, leaving kinks of 3-10 degrees (and Mulish's own rounding
# leaves a few). Every simple glyph gets each such point (turn under 15 degrees) moved back: an on-curve
# point between two handles onto the line joining them, the handle of a curve that
# continues a straight segment onto that segment's line; then the nearest grid point
# with the smallest turn is kept.
def _turn(a, p, b):
    u, v = (p[0] - a[0], p[1] - a[1]), (b[0] - p[0], b[1] - p[1])
    if u == (0, 0) or v == (0, 0): return 180.0
    return abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))
def _best(ideal, fixed_turn):
    cands = [(round(ideal[0]) + dx, round(ideal[1]) + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    return min(cands, key=lambda q: (round(fixed_turn(q), 2), math.dist(q, ideal)))
def g1fix(g):
    c = [tuple(xy) for xy in g.coordinates]; on = [bool(f & 1) for f in g.flags]; s0 = 0; moved = 0
    for e in g.endPtsOfContours:
        idx = list(range(s0, e + 1)); s0 = e + 1; n = len(idx)
        if n < 3: continue
        for k in range(n):
            i, a, b = idx[k], idx[k - 1], idx[(k + 1) % n]
            if not on[i] or (on[a] and on[b]): continue
            t = _turn(c[a], c[i], c[b])
            if not 0.3 < t < 15: continue
            if not on[a] and not on[b]:            # on-curve between two handles
                ax, ay = c[a]; bx, by = c[b]; L2 = (bx - ax) ** 2 + (by - ay) ** 2
                r = ((c[i][0] - ax) * (bx - ax) + (c[i][1] - ay) * (by - ay)) / L2
                q = _best((ax + r * (bx - ax), ay + r * (by - ay)), lambda q: _turn(c[a], q, c[b]))
                if _turn(c[a], q, c[b]) < t: c[i] = q; moved += 1
            else:                                   # a straight segment running into a curve
                h, o = (b, a) if on[a] else (a, b)  # h: the handle, o: the far end of the line
                d = unit((c[i][0] - c[o][0], c[i][1] - c[o][1])); L = math.dist(c[i], c[h])
                q = _best((c[i][0] + d[0] * L, c[i][1] + d[1] * L), lambda q: _turn(c[o], c[i], q))
                if _turn(c[o], c[i], q) < t: c[h] = q; moved += 1
    g.coordinates = GlyphCoordinates(c)
    return moved
# --- round 12: no overlapping contours anywhere ----------------------------------
# Mulish draws many glyphs as overlapping contours (M, N, W, A, K ...), some of them
# self-intersecting, which leaves small unfilled holes in some rasterizers (the M's
# right diagonal at the cap line). Every simple glyph whose outline has overlaps is
# merged into one outline, as add() does for the glyphs drawn here.
OVERLAPS = []
for n in font.getGlyphOrder():
    g = glyf[n]
    if g.isComposite() or g.numberOfContours <= 0: continue
    p = path_of(n); q = pathops.Path(); p.draw(q.getPen())
    try: q.simplify(fix_winding=True)
    except pathops.PathOpsError: continue
    if abs(abs(p.area) - abs(q.area)) > 1 or len(list(q.contours)) < len(list(p.contours)):
        add(n, path_of(n), W(n)); OVERLAPS.append(n)
print(f'overlaps removed in {len(OVERLAPS)} glyphs')

G1_MOVED = 0
for n in font.getGlyphOrder():
    g = glyf[n]
    if g.isComposite() or g.numberOfContours <= 0: continue
    G1_MOVED += g1fix(g); tidy(g); G1_MOVED += g1fix(g); g.recalcBounds(glyf)
print('smooth points restored:', G1_MOVED)

# --- italic: back to the slant -------------------------------------------------------
# Every outline, component offset and mark anchor leans again (shear_font, at the top);
# the points are rounded to the grid and the smooth points restored once more, so the
# modules' post phase (metadata, hinting) and the saved font see the finished italic.
if ITALIC:
    shear_font(font, ITALIC_K)
    moved = 0
    for n in font.getGlyphOrder():
        g = glyf[n]
        if g.isComposite() or g.numberOfContours <= 0: continue
        g.coordinates.toInt(); moved += g1fix(g); tidy(g); g.recalcBounds(glyf); hmtx[n] = (hmtx[n][0], g.xMin)
    for n in font.getGlyphOrder():
        g = glyf[n]
        if g.isComposite(): g.recalcBounds(glyf); hmtx[n] = (hmtx[n][0], g.xMin)
    print(f'italic: reslanted {ITALIC_K:g} per unit about y {ITALIC_YC:g}; smooth points restored again: {moved}')

run_modules('post')
write_ss16_owners()
font['maxp'].numGlyphs = len(font.getGlyphOrder())
font.getReverseGlyphMap(rebuild=True)
font.save(DST)
print('wrote', DST)

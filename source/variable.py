"""Build a full-feature wght/ital variable companion from fourteen finished statics.

Input fonts are read only. Weight is continuous from Light (300) through Black
(900). Italic is the registered 0/1 style selector, implemented with required
FeatureVariations, retaining the genuine italic outlines and their own layout.

Run with the same fontTools version as Makefile; see README-variable.md.
"""
from __future__ import annotations

from collections import Counter

import argparse
import bisect
import copy
import hashlib
import io
import json
import math
import sys
import importlib.metadata
import pathops
from pathlib import Path
from typing import Sequence

from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor
from fontTools.merge import Merger
from fontTools.misc.bezierTools import calcQuadraticArcLength, solveCubic
from fontTools.misc.roundTools import otRound
from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.varLib import build as build_variable, _add_gvar as build_gvar
from fontTools.varLib.featureVars import (addFeatureVariations, buildConditionTable, buildFeatureVariations,
                                        buildFeatureVariationRecord, buildFeatureTableSubstitutionRecord)
from fontTools.varLib.models import normalizeValue, piecewiseLinearMap
from fontTools.varLib.varStore import OnlineVarStoreBuilder
from fontTools.varLib.builder import buildVarDevTable, buildVarData
from fontTools.varLib.mvar import MVAR_ENTRIES
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables.TupleVariation import TupleVariation

WEIGHTS = ((300, 'Light'), (400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'),
           (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black'))
SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
TIMESTAMP = 3876249600
# Exactly representable normalized master coordinates avoid endpoint rounding
# at weights such as 600 (a raw normalized 0.4 is not F2DOT14-exact).
WEIGHT_MAP = [(300, 300), (400, 400), (500, 462.5), (600, 525),
              (700, 650), (800, 775), (900, 900)]
# Removed only from private intermediates: point-referencing static instructions
# cannot survive exact curve subdivision. Full layout/features are not stripped.
STATIC_ONLY = ('STAT', 'DSIG', 'fpgm', 'prep', 'cvt ', 'cvar', 'hdmx', 'LTSH', 'VDMX')
LAYOUT_TABLES = ('GSUB', 'GPOS', 'GDEF', 'MATH', 'BASE', 'JSTF', 'kern', 'morx', 'kerx')
Point = tuple[float, float]
Quad = tuple[Point, Point, Point]


def default_ignorable(codepoint: int) -> bool:
    # Unicode 17 DerivedCoreProperties Default_Ignorable_Code_Point ranges.
    # Keeping these glyph IDs avoids marking invisible controls as intentionally
    # substituted, which would suppress HarfBuzz's default-ignorable handling.
    ranges = ((0xAD,0xAD),(0x34F,0x34F),(0x61C,0x61C),(0x115F,0x1160),
              (0x17B4,0x17B5),(0x180B,0x180F),(0x200B,0x200F),
              (0x202A,0x202E),(0x2060,0x206F),(0x3164,0x3164),
              (0xFE00,0xFE0F),(0xFEFF,0xFEFF),(0xFFA0,0xFFA0),
              (0xFFF0,0xFFF8),(0x1BCA0,0x1BCA3),(0x1D173,0x1D17A),
              (0xE0000,0xE0FFF))
    return any(lo <= codepoint <= hi for lo,hi in ranges)


def italic_style(style: str) -> str:
    return 'Italic' if style == 'Regular' else style + 'Italic'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def split(q: Quad, t: float) -> tuple[Quad, Quad]:
    a, b = lerp(q[0], q[1], t), lerp(q[1], q[2], t)
    c = lerp(a, b, t)
    return (q[0], a, c), (c, b, q[2])


def subquad(q: Quad, lo: float, hi: float) -> Quad:
    if hi < 1:
        q = split(q, hi)[0]
    if lo > 0:
        q = split(q, lo / hi)[1]
    return q


def length(q: Quad) -> float:
    return float(calcQuadraticArcLength(*q))


class ContourPen(BasePen):
    """Expand components/implied points into closed, exact quadratic segments."""
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.contours: list[list[Quad]] = []
        self.segments: list[Quad] = []
        self.start: Point | None = None

    def _moveTo(self, pt):
        self.start = tuple(pt)
        self.segments = []

    def _lineTo(self, pt):
        a = tuple(self._getCurrentPoint())
        b = tuple(pt)
        self.segments.append((a, lerp(a, b, .5), b))

    def _qCurveToOne(self, control, end):
        self.segments.append((tuple(self._getCurrentPoint()), tuple(control), tuple(end)))

    def _curveToOne(self, *args):
        raise ValueError('Cubic outlines are unsupported; supply the finished TrueType statics.')

    def _closePath(self):
        if self.start is not None and self._getCurrentPoint() != self.start:
            self._lineTo(self.start)
        if self.segments:
            self.contours.append(self.segments)
        self.segments = []
        self.start = None

    def _endPath(self):
        raise ValueError('An open contour cannot be made into a TrueType variation master.')


class RawGlyphSet:
    """Component expansion without glyph-wrapper sidebearing translations."""
    def __init__(self,font,leaves=None):
        self.font=font
        self.leaves=leaves or {}

    def __getitem__(self,name):
        owner=self
        class Glyph:
            def draw(self,pen):
                if name in owner.leaves:
                    for contour in owner.leaves[name]:
                        pen.moveTo(contour[0][0])
                        for _,control,end in contour:
                            pen.qCurveTo(control,end)
                        pen.closePath()
                else:
                    owner.font['glyf'][name].draw(pen,owner.font['glyf'])
        return Glyph()


def raw_contours(font,name,leaves=None):
    glyphs=RawGlyphSet(font,leaves)
    pen=ContourPen(glyphs)
    glyphs[name].draw(pen)
    return pen.contours


def contours(font: TTFont, name: str) -> list[list[Quad]]:
    source_contours=raw_contours(font,name)
    # Some statics contain self-touching contours: one boundary can traverse
    # both an outer and a counter, while another weight stores two contours.
    # Normalize the SAME nonzero filled shape before matching boundaries.
    # Treating that as a missing counter would deform intermediate outlines.
    path=pathops.Path()
    for contour in source_contours:
        path.moveTo(*contour[0][0])
        for _,control,end in contour:
            path.quadTo(*control,*end)
        path.close()
    if not source_contours:
        return []
    normalized=ContourPen(None)
    pathops.simplify(path).draw(normalized)
    cs=normalized.contours
    if cs and area(max(cs,key=lambda c:abs(area(c))))>0:
        cs=[reverse(c) for c in cs]
    return cs


def reverse(contour: list[Quad]) -> list[Quad]:
    return [(c, b, a) for a, b, c in reversed(contour)]


def area(contour: list[Quad]) -> float:
    # Exact integral x dy - y dx for each quadratic, through fixed Simpson nodes.
    total = 0.
    for a, b, c in contour:
        def integrand(t):
            x, y = lerp(lerp(a, b, t), lerp(b, c, t), t)
            dx = 2 * ((1-t)*(b[0]-a[0]) + t*(c[0]-b[0]))
            dy = 2 * ((1-t)*(b[1]-a[1]) + t*(c[1]-b[1]))
            return x*dy-y*dx
        total += (integrand(0)+4*integrand(.5)+integrand(1))/12
    return total


def anchor(contour: list[Quad], reference=None) -> list[Quad]:
    """Rotate to a geometric leftmost/bottommost point, independent of knots."""
    if reference is not None:
        ref_anchor=anchor(reference)[0][0]
        def bounds(c):
            points=[p for q in c for p in q]
            return tuple(min(p[k] for p in points) for k in (0,1))+tuple(max(p[k] for p in points) for k in (0,1))
        rb,cb=bounds(reference),bounds(contour)
        target=tuple(cb[k]+(ref_anchor[k]-rb[k])/(rb[k+2]-rb[k] or 1)*(cb[k+2]-cb[k]) for k in (0,1))
        near=[]
        for i,(a,b,c) in enumerate(contour):
            aa=tuple(a[k]-2*b[k]+c[k] for k in (0,1))
            bb=tuple(2*(b[k]-a[k]) for k in (0,1))
            cc=tuple(a[k]-target[k] for k in (0,1))
            dot=lambda x,y:sum(v*w for v,w in zip(x,y))
            roots=solveCubic(2*dot(aa,aa),3*dot(aa,bb),dot(bb,bb)+2*dot(aa,cc),dot(bb,cc))
            for t in [0.,1.]+[float(x) for x in roots if 0<x<1]:
                point=lerp(lerp(a,b,t),lerp(b,c,t),t)
                near.append((sum((x-y)**2 for x,y in zip(point,target)),i,t))
        _,i,t=min(near)
        if t>1-1e-10:
            i=(i+1)%len(contour);t=0.
        if t<1e-10:
            return contour[i:]+contour[:i]
        left,right=split(contour[i],t)
        return [right]+contour[i+1:]+contour[:i]+[left]
    candidates = []
    for i, q in enumerate(contour):
        ts = [0.]
        for axis in (0, 1):
            den = q[0][axis] - 2*q[1][axis] + q[2][axis]
            if den:
                t = (q[0][axis]-q[1][axis])/den
                if 0 < t < 1:
                    ts.append(t)
        for t in ts:
            pt = lerp(lerp(q[0], q[1], t), lerp(q[1], q[2], t), t)
            candidates.append((round(pt[0], 8), round(pt[1], 8), i, t))
    _, _, i, t = min(candidates)
    if t < 1e-12:
        return contour[i:] + contour[:i]
    left, right = split(contour[i], t)
    return [right] + contour[i+1:] + contour[:i] + [left]


def descriptor(c):
    points = [p for q in c for p in q]
    xs, ys = zip(*points)
    return ((min(xs)+max(xs))/2, (min(ys)+max(ys))/2, area(c), sum(length(q) for q in c))


def assignment(cost: list[list[float]]) -> list[int]:
    """Deterministic O(n^3) minimum-cost contour assignment (Hungarian method)."""
    n = len(cost)
    u, v, p, way = [0.]*(n+1), [0.]*(n+1), [0]*(n+1), [0]*(n+1)
    for i in range(1, n+1):
        p[0] = i
        j0 = 0
        mins, used = [math.inf]*(n+1), [False]*(n+1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], math.inf, 0
            for j in range(1, n+1):
                if not used[j]:
                    cur = cost[i0-1][j-1]-u[i0]-v[j]
                    if cur < mins[j]:
                        mins[j], way[j] = cur, j0
                    if mins[j] < delta:
                        delta, j1 = mins[j], j
            for j in range(n+1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    mins[j] -= delta
            j0 = j1
            if not p[j0]:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if not j0:
                break
    out = [0]*n
    for j in range(1, n+1):
        out[p[j]-1] = j-1
    return out


def match_contours(all_contours: list[list[list[Quad]]], upem: int):
    # A counter may open into the outside at a heavy weight. Reserve the
    # maximum number of contours of EACH winding, rather than forcing a hole
    # to become a filled outer contour. Absent members are zero-area contours.
    default = all_contours[min((i for i,c in enumerate(all_contours) if c),key=lambda i:abs(i-1))]
    sign = 1 if area(max(default,key=lambda c:abs(area(c)))) >= 0 else -1
    normalized=[]
    for cs in all_contours:
        if cs and area(max(cs,key=lambda c:abs(area(c))))*sign<0:
            cs=[reverse(c) for c in cs]
        normalized.append(cs)
    all_contours=normalized
    ref=[]
    for polarity in (-1,0,1):
        groups=[[c for c in cs if (1 if area(c)>1 else -1 if area(c)<-1 else 0)==polarity] for cs in all_contours]
        maximum=max(map(len,groups))
        pivot=min((i for i,c in enumerate(groups) if len(c)==maximum),key=lambda i:abs(i-1))
        ref.extend(groups[pivot])
    count=len(ref)
    rd=list(map(descriptor,ref))
    matched = []
    degenerates = 0
    for cs in all_contours:
        # Reversing every contour preserves fill; never reverse an isolated hole.
        if cs and ref:
            largest = max(cs, key=lambda c: abs(area(c)))
            largest_ref = max(ref, key=lambda c: abs(area(c)))
            if area(largest)*area(largest_ref)<0:
                cs = [reverse(c) for c in cs]
        ds = list(map(descriptor, cs))
        cost=[]
        for x,y,a,per in rd:
            row=[]
            for xx,yy,aa,pper in ds:
                row.append(((x-xx)**2+(y-yy)**2)/(upem*upem)+abs(a-aa)/(upem*upem)+
                           (1000 if a*aa<0 and abs(a)>1 and abs(aa)>1 else 0))
            row += [abs(a)/(upem*upem)+.001]*(count-len(ds))
            cost.append(row)
        chosen=assignment(cost)
        ordered=[]
        for i,j in enumerate(chosen):
            if j<len(cs):
                if rd[i][2]*ds[j][2]<0 and abs(rd[i][2])>1 and abs(ds[j][2])>1:
                    raise ValueError('Contour winding changes cannot be aligned without changing fill.')
                ordered.append(anchor(cs[j],ref[i]))
            else:
                # A zero-area contour preserves this master's exact filled shape;
                # it may open continuously into the real counter in another master.
                x,y,a,per=rd[i]
                if per>0 and abs(a)/(per*per)<.001:
                    # A missing thin boundary sliver collapses across its width,
                    # not along its length: point-collapse would pull a long
                    # edge through the glyph and create intermediate spikes.
                    points=[p for q in ref[i] for p in q]
                    axis=max((0,1),key=lambda k:max(p[k] for p in points)-min(p[k] for p in points))
                    lo=min(points,key=lambda p:p[axis]);hi=max(points,key=lambda p:p[axis])
                    direction=(hi[0]-lo[0],hi[1]-lo[1]);norm=sum(t*t for t in direction)
                    def project(p):
                        t=sum((p[k]-lo[k])*direction[k] for k in (0,1))/(norm or 1)
                        return (lo[0]+t*direction[0],lo[1]+t*direction[1])
                    ordered.append([tuple(project(p) for p in q) for q in ref[i]])
                else:
                    ordered.append([((x,y),(x,y),(x,y))])
                degenerates += 1
        matched.append(ordered)
    return matched, degenerates


def contours_path(cs):
    path=pathops.Path()
    for contour in cs:
        path.moveTo(*contour[0][0])
        for _,control,end in contour:
            path.quadTo(*control,*end)
        path.close()
    return path


def contour_bounds(contour):
    points=[p for q in contour for p in q]
    return tuple(min(p[k] for p in points) for k in (0,1))+tuple(max(p[k] for p in points) for k in (0,1))


def counter_transition_boundaries(all_contours):
    """Use exact filled-shape decompositions for genuine topology changes.

    Counter opening: a retraced bridge joins the hole to its geometrically
    containing outer. Component splitting: intersect with complementary half
    planes through the void, but only if both pieces are a single filled
    boundary in EVERY master. Both constructions preserve the source ink; the
    chosen class, complete affected set and per-master area errors are reported.
    """
    normalized=[]
    for cs in all_contours:
        if cs and area(max(cs,key=lambda c:abs(area(c))))>0:
            cs=[reverse(c) for c in cs]
        normalized.append(cs)
    counts=[(sum(area(c)<-1 for c in cs),sum(area(c)>1 for c in cs)) for cs in normalized]
    if len(set(counts))<=1:
        return all_contours,None
    if len({x[0] for x in counts})!=1:
        # A counter cutting right through a badge changes the outer-component
        # count. Split through the void instead of swapping an outer for a hole.
        for axis in (1,0):
            cuts=[]
            for cs in normalized:
                holes=[c for c in cs if area(c)>1]
                if holes:
                    bounds=contour_bounds(max(holes,key=lambda c:abs(area(c))))
                    cuts.append((bounds[axis]+bounds[axis+2])/2)
                else:
                    bounds=sorted((contour_bounds(c) for c in cs if area(c)<-1),key=lambda b:b[axis])
                    end=bounds[0][axis+2] if bounds else 0
                    gaps=[]
                    for bound in bounds[1:]:
                        if bound[axis]>end:
                            gaps.append((bound[axis]-end,(bound[axis]+end)/2))
                        end=max(end,bound[axis+2])
                    cuts.append(max(gaps)[1] if gaps else None)
            if any(cut is None for cut in cuts):
                continue
            result=[];errors=[];valid=True
            for cs,cut in zip(normalized,cuts):
                shape=contours_path(cs)
                points=[p for c in cs for q in c for p in q]
                lo=[min(p[k] for p in points)-100 for k in (0,1)]
                hi=[max(p[k] for p in points)+100 for k in (0,1)]
                parts=[]
                for side in (0,1):
                    a,b=lo.copy(),hi.copy()
                    if side==0:
                        b[axis]=cut
                    else:
                        a[axis]=cut
                    clip=pathops.Path();clip.moveTo(a[0],a[1]);clip.lineTo(b[0],a[1]);clip.lineTo(b[0],b[1]);clip.lineTo(a[0],b[1]);clip.close()
                    piece=pathops.op(shape,clip,pathops.PathOp.INTERSECTION)
                    pen=ContourPen(None);piece.draw(pen)
                    if len(pen.contours)!=1 or abs(area(pen.contours[0]))<=1:
                        valid=False;break
                    contour=pen.contours[0]
                    parts.append(reverse(contour) if area(contour)>0 else contour)
                if not valid:
                    break
                error=abs(sum(area(c) for c in parts)-sum(area(c) for c in cs))
                if error>max(.1,abs(sum(area(c) for c in cs))*1e-6):
                    valid=False;break
                errors.append(error);result.append(parts)
            if valid:
                return result,{'mode':'complementary_half_planes','axis':'xy'[axis],
                               'cuts':cuts,'source_topologies':counts,'area_errors':errors}
        # Other component transitions still use explicit zero-area slots and
        # must pass the complete intermediate glyph audit; never claim repair.
        return all_contours,None
    # This representation is for a single counter opening into one outer.
    # Existing independent counters in a multi-counter glyph must retain their
    # own correspondence; folding all of them into one path is not equivalent
    # interpolation merely because one additional small loop appears.
    if {tuple(x) for x in counts}!={(1,0),(1,1)}:
        return all_contours,None
    result=[];parents=[];errors=[]
    for cs in normalized:
        outers=[c for c in cs if area(c)<-1]
        original_paths=[contours_path([c]) for c in outers]
        holes=sorted((c for c in cs if area(c)>1),key=lambda c:(descriptor(c)[1],descriptor(c)[0]))
        owners=[]
        for hole in holes:
            hole_path=contours_path([hole])
            candidates=[]
            for oi,parent in enumerate(original_paths):
                outside=pathops.op(hole_path,parent,pathops.PathOp.DIFFERENCE).area
                if outside<=max(.0001,hole_path.area*1e-7):
                    candidates.append((parent.area,oi))
            if not candidates:
                raise ValueError('Opening counter has no geometrically containing outer boundary.')
            _,oi=min(candidates)
            out=outers[oi]
            _,i,j=min((sum((x-y)**2 for x,y in zip(q[0],r[0])),i,j)
                       for i,q in enumerate(out) for j,r in enumerate(hole))
            out=out[i:]+out[:i];h=hole[j:]+hole[:j]
            a,b=out[0][0],h[0][0]
            outers[oi]=out+[(a,lerp(a,b,.5),b)]+h+[(b,lerp(b,a,.5),a)]
            owners.append(oi)
        error=abs(sum(area(c) for c in outers)-sum(area(c) for c in cs))
        if error>max(.0001,abs(sum(area(c) for c in cs))*1e-9):
            raise ValueError('Counter bridge changed source signed area.')
        parents.append(owners);errors.append(error);result.append(outers)
    return result,{'mode':'contained_counter_bridges','source_topologies':counts,
                   'containing_outer_indices':parents,'area_errors':errors}


def arc_segments(contour):
    lengths=[length(q) for q in contour]
    cumul=[0.]
    for x in lengths:
        cumul.append(cumul[-1]+x)
    return lengths,cumul


def parameter(q, distance, full):
    if distance <= 1e-7:
        return 0.
    if full-distance <= 1e-7:
        return 1.
    lo,hi=0.,1.
    t=distance/full
    for _ in range(30):
        measured=length(split(q,t)[0])
        error=measured-distance
        if abs(error)<1e-7:
            return t
        if error<0:
            lo=t
        else:
            hi=t
        dx=2*((1-t)*(q[1][0]-q[0][0])+t*(q[2][0]-q[1][0]))
        dy=2*((1-t)*(q[1][1]-q[0][1])+t*(q[2][1]-q[1][1]))
        speed=math.hypot(dx,dy)
        candidate=t-error/speed if speed>1e-12 else (lo+hi)/2
        t=candidate if lo<candidate<hi else (lo+hi)/2
    return (lo+hi)/2


def subdivide_arcs(cs: list[list[Quad]]) -> list[list[Quad]]:
    """Shared arc-length knots; exact subdivision, not polygonal resampling."""
    measures=[arc_segments(c) for c in cs]
    knots={0.,1.}
    for _,cum in measures:
        if cum[-1]>1e-10:
            knots.update(x/cum[-1] for x in cum)
    knots=sorted(knots)
    # Only merge roundoff-equivalent knots, never a meaningful geometric span.
    knots=[x for i,x in enumerate(knots) if not i or x-knots[i-1]>1e-11]
    knots[-1]=1.
    result=[]
    for c,(lens,cum) in zip(cs,measures):
        if cum[-1]<1e-10:
            pt=c[0][0]
            result.append([(pt,pt,pt)]*(len(knots)-1))
            continue
        targets=[]
        for t in knots:
            x=t*cum[-1]
            j=bisect.bisect_left(cum,x)
            near=min([q for q in [j-1,j] if 0<=q<len(cum)],key=lambda q:abs(cum[q]-x))
            targets.append(cum[near] if abs(cum[near]-x)<1e-7 else x)
        quads=[]
        for a,b in zip(targets,targets[1:]):
            j=min(len(c)-1,max(0,bisect.bisect_right(cum,a+1e-9)-1))
            if b>cum[j+1]+1e-6:
                raise ValueError('Shared knot interval crossed an original quadratic boundary.')
            lo=parameter(c[j],max(0,a-cum[j]),lens[j])
            hi=parameter(c[j],min(lens[j],b-cum[j]),lens[j])
            quads.append(subquad(c[j],lo,hi))
        result.append(quads)
    return result


def hard_corners(contour):
    """Salient tangent discontinuities; ignore small integer-grid join noise."""
    result=[]
    for i,q in enumerate(contour):
        previous=contour[i-1]
        a=(previous[2][0]-previous[1][0],previous[2][1]-previous[1][1])
        b=(q[1][0]-q[0][0],q[1][1]-q[0][1])
        na,nb=math.hypot(*a),math.hypot(*b)
        if not na:
            a=(previous[2][0]-previous[0][0],previous[2][1]-previous[0][1]);na=math.hypot(*a)
        if not nb:
            b=(q[2][0]-q[0][0],q[2][1]-q[0][1]);nb=math.hypot(*b)
        if na*nb and (a[0]*b[0]+a[1]*b[1])/(na*nb)<math.cos(math.radians(15)):
            result.append(i)
    return result


def subdivide(cs: list[list[Quad]],audit=None) -> list[list[Quad]]:
    indices=[hard_corners(c) for c in cs]
    if not indices[0] or len(set(map(len,indices)))!=1:
        if audit is not None:
            audit['arc_aligned_contours']+=1
        return subdivide_arcs(cs)
    # Match actual corners BEFORE inserting arc-length knots. A single global
    # perimeter parameter can otherwise smear a straight end-face into a curve.
    def normalized_points(contour,ids):
        b=contour_bounds(contour)
        return [((contour[i][0][0]-b[0])/(b[2]-b[0] or 1),
                 (contour[i][0][1]-b[1])/(b[3]-b[1] or 1)) for i in ids]
    reference=normalized_points(cs[min(1,len(cs)-1)],indices[min(1,len(cs)-1)])
    aligned=[]
    for contour,ids in zip(cs,indices):
        points=normalized_points(contour,ids)
        shift=min(range(len(ids)),key=lambda j:sum((x-y)**2 for p,q in zip(reference,points[j:]+points[:j]) for x,y in zip(p,q)))
        aligned.append(ids[shift:]+ids[:shift])
    result=[[] for _ in cs]
    for k in range(len(reference)):
        spans=[]
        for contour,ids in zip(cs,aligned):
            a,b=ids[k],ids[(k+1)%len(ids)]
            spans.append(contour[a:b] if b>a else contour[a:]+contour[:b])
        for target,part in zip(result,subdivide_arcs(spans)):
            target.extend(part)
    if audit is not None:
        audit['corner_aligned_contours']+=1
    return result


def signature(font,name):
    g=font['glyf'][name]
    if g.isComposite():
        return ('components',tuple((c.glyphName, tuple(c.getComponentInfo()[1][:4])) for c in g.components))
    if g.numberOfContours<=0:
        return ('empty',)
    return (g.numberOfContours,tuple(g.endPtsOfContours),tuple(int(x)&1 for x in g.flags))


def canonicalize(fonts: Sequence[TTFont], only=None):
    order=fonts[0].getGlyphOrder()
    stats={'changed_glyphs':[],'topology_repairs':{},'degenerate_contours':0,'maximum_points':0,
           'corner_aligned_contours':0,'arc_aligned_contours':0,
           'corner_policy':'15-degree salient tangent changes, equal count across every master, cyclic geometric matching.'}
    for name in order:
        if only is not None and name not in only:
            continue
        # Identical point signatures alone cannot prove correspondence: boolean
        # constructors may permute equal-looking contours or rotate starts.
        # A shared composite graph with fixed linear transforms is different:
        # it inherits canonical leaf curves and interpolates only translations.
        if all(f['glyf'][name].isComposite() for f in fonts) and len({signature(f,name) for f in fonts})==1:
            continue
        cs=[contours(f,name) for f in fonts]
        if not any(cs):
            continue
        cs,repair=counter_transition_boundaries(cs)
        if repair:
            stats['topology_repairs'][name]=repair
        try:
            aligned,n=match_contours(cs,fonts[0]['head'].unitsPerEm)
        except ValueError as error:
            raise ValueError(f'{name}: {error}') from error
        stats['degenerate_contours']+=n
        final=[[] for _ in fonts]
        for i in range(len(aligned[0])):
            qs=subdivide([c[i] for c in aligned],audit=stats)
            for j,q in enumerate(qs):
                final[j].append(q)
        for f,contour_list in zip(fonts,final):
            old=f['glyf'][name]
            bounds=tuple(getattr(old,k,0) for k in ('xMin','yMin','xMax','yMax'))
            pen=TTGlyphPen(None)
            for c in contour_list:
                pen.moveTo(c[0][0])
                for _,control,end in c:
                    pen.qCurveTo(control,end)
                pen.closePath()
            g=pen.glyph(dropImpliedOnCurves=False)
            for k,v in zip(('xMin','yMin','xMax','yMax'),bounds):
                setattr(g,k,v)
            f['glyf'][name]=g
            stats['maximum_points']=max(stats['maximum_points'],len(g.coordinates))
        if len({signature(f,name) for f in fonts})!=1:
            raise ValueError(f'Canonicalization did not produce compatible topology: {name}')
        stats['changed_glyphs'].append(name)
    return stats


def rebase_source_origins(font):
    """Keep statics' actual rendered origins while normalizing variable origins.

    Static TrueType glyphs may have xMin != LSB. Their phantom origin is xMin-LSB,
    except that the last USE_MY_METRICS component supplies its own effective
    phantom origin (recursively, including its scale).
    Rebase each outline into that rendered coordinate frame. Composite offsets
    compensate for the rebasing of their children, so no child-origin shift is
    accidentally applied twice. Layout anchor values and advance widths retain
    their original, already-rendered-layout meaning.
    """
    glyf=font['glyf']
    shifts={}
    visiting=set()
    def origin(name):
        if name in shifts:
            return shifts[name]
        if name in visiting:
            raise ValueError(f'Recursive composite glyph: {name}')
        visiting.add(name)
        glyph=glyf[name]
        value=getattr(glyph,'xMin',0)-font['hmtx'][name][1]
        if glyph.isComposite():
            for component in glyph.components:
                if component.flags & 0x0200:
                    _,matrix=component.getComponentInfo()
                    value=matrix[0]*origin(component.glyphName)
        visiting.remove(name);shifts[name]=value
        return value
    for name in font.getGlyphOrder():
        origin(name)
    for name in font.getGlyphOrder():
        glyph=glyf[name];shift=shifts[name]
        if glyph.isComposite():
            for component in glyph.components:
                if not hasattr(component,'x'):
                    raise ValueError(f'Point-matched composite requires explicit origin conversion: {name}')
                _,(xx,xy,yx,yy,dx,dy)=component.getComponentInfo()
                child=shifts[component.glyphName]
                component.x=otRound(dx+xx*child-shift)
                component.y=otRound(dy+xy*child)
                # All private parent hmtx metrics are explicit; child metrics
                # must not override the parent's normalized phantom origin.
                component.flags &= ~0x0200
        elif glyph.numberOfContours>0 and shift:
            glyph.coordinates.translate((-shift,0))
        for attr in ('xMin','xMax'):
            if hasattr(glyph,attr):
                setattr(glyph,attr,getattr(glyph,attr)-shift)
    return {'rebased_glyphs':sum(bool(x) for x in shifts.values()),'source_origin_offsets':{n:d for n,d in shifts.items() if d}}


def normalize_variable_bearings(font):
    glyf=font['glyf']
    for name in font.getGlyphOrder():
        glyph=glyf[name]
        glyph.recalcBounds(glyf)
        width,_=font['hmtx'][name]
        font['hmtx'][name]=(width,getattr(glyph,'xMin',0))
    font['head'].flags |= 2


def filled_shape_difference(before,after):
    """Both directional differences: equal removed/added areas cannot cancel."""
    removed=pathops.op(before,after,pathops.PathOp.DIFFERENCE).area
    added=pathops.op(after,before,pathops.PathOp.DIFFERENCE).area
    return removed,added


def audit_source_composite_fill(font):
    """Prove a uniform leaf winding preserves every assembled source composite.

    Deliberate opposite-winding knockout is a valid input design, but cannot be
    silently turned into a union. Such input needs an explicit equivalent
    decomposition before this companion can be built, so fail with its glyph.
    """
    composites=[n for n in font.getGlyphOrder() if font['glyf'][n].isComposite()]
    leaves={n:contours(font,n) for n in font.getGlyphOrder() if not font['glyf'][n].isComposite()}
    rows=[]
    for name in composites:
        before=pathops.simplify(contours_path(raw_contours(font,name)))
        after=pathops.simplify(contours_path(raw_contours(font,name,leaves)))
        removed,added=filled_shape_difference(before,after)
        error=removed+added
        tolerance=max(.1,before.area*1e-6)
        if error>tolerance:
            raise ValueError(f'{name}: uniform leaf winding changes assembled source ink (removed {removed}, added {added} square font units); preserve deliberate knockout with an explicit equivalent source decomposition.')
        rows.append(error)
    return {'assembled_composites':len(composites),'maximum_area_error':max(rows,default=0),'difference_metric':'sum of both directional filled-shape differences',
            'numerical_area_bound':'max(0.1 square font unit, source filled area * 1e-6)',
            'deliberate_knockout_policy':'Explicit error; never silently filled.'}


def strip_static_hints(font):
    for tag in STATIC_ONLY:
        if tag in font:
            del font[tag]
    def reject_point_references(value):
        if isinstance(value,list):
            for item in value:
                reject_point_references(item)
        elif hasattr(value,'__dict__'):
            if type(value).__name__ in ('Anchor','CaretValue') and getattr(value,'Format',None)==2:
                raise ValueError('Point-index layout anchors/carets need conversion before outline canonicalization.')
            for key,item in vars(value).items():
                if key not in ('reader','font'):
                    reject_point_references(item)
    for tag in ('GDEF','GPOS'):
        if tag in font:
            reject_point_references(font[tag].table)
    for g in font['glyf'].glyphs.values():
        g.removeHinting()
    font.recalcBBoxes=False
    font.recalcTimestamp=False
    font['head'].created=font['head'].modified=TIMESTAMP


def _position_subtable(font, lookup_index, subtable_index):
    table=font['GPOS'].table.LookupList.Lookup[lookup_index].SubTable[subtable_index]
    while hasattr(table,'ExtSubTable'):
        table=table.ExtSubTable
    return table


def _anchor_row(font, key, create=False):
    li,si,glyph,ci=key
    sub=_position_subtable(font,li,si)
    if glyph not in sub.BaseCoverage.glyphs:
        if not create:
            return None
        pairs=list(zip(sub.BaseCoverage.glyphs,sub.BaseArray.BaseRecord))
        row=otTables.BaseRecord();row.BaseAnchor=[None]*sub.ClassCount
        pairs.append((glyph,row));pairs.sort(key=lambda p:font.getGlyphID(p[0]))
        sub.BaseCoverage.glyphs=[p[0] for p in pairs]
        sub.BaseArray.BaseRecord=[p[1] for p in pairs]
        sub.BaseArray.BaseCount=len(pairs)
    return sub.BaseArray.BaseRecord[sub.BaseCoverage.glyphs.index(glyph)].BaseAnchor


def prepare_sparse_anchors(fonts, locations):
    """Densify numeric anchor data; keep actual absence as explicit layout rules.

    None is not a zero anchor. Coordinate values may interpolate, but whether a
    mark attaches at all must retain each static master's behavior. The latter
    is represented by GPOS FeatureVariations, not fabricated origin anchors.
    """
    keys=set()
    for font in fonts:
        for li,lookup in enumerate(font['GPOS'].table.LookupList.Lookup):
            for si,_ in enumerate(lookup.SubTable):
                sub=_position_subtable(font,li,si)
                if hasattr(sub,'BaseArray'):
                    for glyph,row in zip(sub.BaseCoverage.glyphs,sub.BaseArray.BaseRecord):
                        keys.update((li,si,glyph,ci) for ci,_ in enumerate(row.BaseAnchor))
    cases=[]
    for key in sorted(keys):
        values=[]
        for font in fonts:
            row=_anchor_row(font,key)
            values.append(None if row is None else row[key[3]])
        if all(x is None for x in values) or all(x is not None for x in values):
            continue
        presence=[]
        for weight,_ in WEIGHTS:
            flags=[value is not None for loc,value in zip(locations,values) if loc[0]==weight]
            if len(set(flags))!=1:
                raise ValueError('Sparse anchor presence differs between duplicate style master grids.')
            presence.append(flags[0])
        for i,value in enumerate(values):
            if value is None:
                nearest=min((j for j,x in enumerate(values) if x is not None),
                            key=lambda j:(abs(locations[i][0]-locations[j][0]),locations[i][1]!=locations[j][1],j))
                row=_anchor_row(fonts[i],key,create=True)
                row[key[3]]=copy.deepcopy(values[nearest])
        cases.append({'key':key,'presence':presence})
    return cases


def normalized_weight(font, value):
    raw = normalizeValue(value, (300, 400, 900))
    return piecewiseLinearMap(raw, font['avar'].segments['wght']) if 'avar' in font else raw


def install_sparse_anchor_variations(font,cases):
    if not cases:
        return
    table=font['GPOS'].table
    if getattr(table,'FeatureVariations',None) is not None:
        raise ValueError('Existing GPOS FeatureVariations require explicit composition, not replacement.')
    lookups=table.LookupList.Lookup
    originals=copy.deepcopy(lookups)
    original_count=len(originals)
    default=tuple(c['presence'][1] for c in cases)
    patterns=[tuple(c['presence'][i] for c in cases) for i in range(len(WEIGHTS))]
    variants={}
    remapped_contexts=0
    seen_context_objects=set()
    def remap_context(value,indices):
        nonlocal remapped_contexts
        if isinstance(value,list) or hasattr(value,'__dict__'):
            if id(value) in seen_context_objects:
                return
            seen_context_objects.add(id(value))
        if isinstance(value,list):
            for item in value:
                remap_context(item,indices)
        elif hasattr(value,'__dict__'):
            if isinstance(value,otTables.PosLookupRecord):
                if value.LookupListIndex not in indices:
                    raise ValueError('Contextual positioning refers outside its original lookup group.')
                value.LookupListIndex=indices[value.LookupListIndex]
                remapped_contexts+=1
            for key,item in vars(value).items():
                if key not in ('reader','font') and not key.startswith('_'):
                    remap_context(item,indices)
    for pattern in sorted(set(patterns)):
        if pattern==default:
            group=lookups[:original_count]
            indices={i:i for i in range(original_count)}
        else:
            # Feature lookups execute in GLOBAL LookupList order, not the order
            # in a Feature's list. Cloning only a mark lookup after mkmk reverses
            # their execution and breaks stacked attachment. Clone every lookup
            # in the same relative order and redirect every active Feature.
            group=copy.deepcopy(originals)
            offset=len(lookups)
            indices={i:offset+i for i in range(original_count)}
            seen_context_objects.clear()
            for lookup in group:
                remap_context(lookup,indices)
            lookups.extend(group)
        for flag,case in zip(pattern,cases):
            if flag:
                continue
            li,si,glyph,ci=case['key']
            sub=group[li].SubTable[si]
            while hasattr(sub,'ExtSubTable'):
                sub=sub.ExtSubTable
            sub.BaseArray.BaseRecord[sub.BaseCoverage.glyphs.index(glyph)].BaseAnchor[ci]=None
        variants[pattern]=indices
    table.LookupList.LookupCount=len(lookups)
    records=[]
    start=0
    while start<len(patterns):
        end=start
        while end+1<len(patterns) and patterns[end+1]==patterns[start]:
            end+=1
        pattern=patterns[start]
        if pattern!=default:
            lo=300 if start==0 else (WEIGHTS[start-1][0]+WEIGHTS[start][0])/2
            hi=900 if end==len(patterns)-1 else (WEIGHTS[end][0]+WEIGHTS[end+1][0])/2
            subs=[]
            for fi,record in enumerate(table.FeatureList.FeatureRecord):
                old=record.Feature.LookupListIndex
                new=[variants[pattern].get(i,i) for i in old]
                if new!=old:
                    item=buildFeatureTableSubstitutionRecord(fi,new)
                    item.Feature.FeatureParams=copy.deepcopy(record.Feature.FeatureParams)
                    subs.append(item)
            records.append(buildFeatureVariationRecord(
                [buildConditionTable(0,normalized_weight(font,lo),normalized_weight(font,hi))],subs))
        start=end+1
    table.Version=0x00010001
    table.FeatureVariations=buildFeatureVariations(records)
    return {'original_lookups':original_count,'ordered_variant_groups':len(set(patterns))-1,
            'contextual_references_remapped':remapped_contexts,
            'policy':'Whole lookup groups and every Feature index redirected, preserving global execution order.'}


def stabilize_master_avar(font):
    """Map named masters exactly despite F2DOT14 input-knot quantization.

    OpenType permits equal successive output coordinates. A single-cell flat
    interval around a nonrepresentable input master gives every consumer the
    same exact dyadic node, before or after normalized-coordinate quantization.
    fvar/named user coordinates are unchanged; intervals are ~0.03 CSS weight.
    """
    mapping=font['avar'].segments['wght']
    intervals=[]
    for weight,_ in WEIGHTS:
        raw=normalizeValue(weight,(300,400,900))
        target=normalizeValue(piecewiseLinearMap(weight,dict(WEIGHT_MAP)),(300,400,900))
        lo=math.floor(raw*16384)/16384
        hi=math.ceil(raw*16384)/16384
        for value in list(mapping):
            if lo<value<hi:
                del mapping[value]
        mapping[lo]=mapping[hi]=target
        if lo!=hi:
            intervals.append({'master':weight,'normalized_input':[lo,hi],'normalized_output':target,
                              'CSS_bounds':[400+lo*500,400+hi*500],'CSS_width':(hi-lo)*500})
    keys=sorted(mapping)
    if any(a>=b for a,b in zip(keys,keys[1:])) or any(mapping[a]>mapping[b] for a,b in zip(keys,keys[1:])) or any(mapping[x]!=x for x in (-1,0,1)):
        raise ValueError('Invalid monotone master avar mapping.')
    return intervals


def recalculate_derived_metadata(font):
    font['maxp'].recalc(font)
    font['hhea'].recalc(font)
    for attr in ('maxTwilightPoints','maxStorage','maxFunctionDefs','maxInstructionDefs','maxStackElements','maxSizeOfInstructions'):
        setattr(font['maxp'],attr,0)
    font['maxp'].maxZones=1
    if not font['head'].flags & 2:
        raise ValueError('Variable glyphs must have LSB equal to xMin.')
    return {'maxp':{k:getattr(font['maxp'],k) for k in ('numGlyphs','maxPoints','maxContours','maxCompositePoints','maxCompositeContours','maxComponentElements','maxComponentDepth')},
            'head_bbox':[getattr(font['head'],k) for k in ('xMin','yMin','xMax','yMax')],
            'hhea':{k:getattr(font['hhea'],k) for k in ('advanceWidthMax','minLeftSideBearing','minRightSideBearing','xMaxExtent')}}


def math_hat_plan(model):
    """An exact local tensor basis for the complete two-axis source grid.

    Hierarchical global supports can require fractional deltas even for integer
    masters, which ItemVariationStore cannot encode exactly. Local hat supports
    vanish at all other named weight nodes; their endpoint differences and style
    interactions are integers, so every supplied MathValueRecord is reproduced.
    """
    keys=[(loc.get('wght',0.),loc.get('ital',0.)) for loc in model.origLocations]
    weights=sorted({w for w,i in keys});italics=sorted({i for w,i in keys})
    if italics!=[0.,1.] or 0. not in weights or len(set(keys))!=len(keys) or set(keys)!={(w,i) for w in weights for i in italics}:
        raise ValueError('Exact MATH interpolation requires a complete wght/ital source grid.')
    if any(value*16384!=round(value*16384) for value in weights):
        raise ValueError('Exact MATH interpolation needs F2DOT14-representable weight supports.')
    index={key:i for i,key in enumerate(keys)}
    ordered=[(w,0.) for w in weights if w!=0.]+[(0.,1.)]+[(w,1.) for w in weights if w!=0.]
    supports=[]
    for w,i in ordered:
        support={}
        if w:
            j=weights.index(w)
            support['wght']=(weights[max(0,j-1)],w,weights[min(len(weights)-1,j+1)])
        if i:
            support['ital']=(0.,1.,1.)
        supports.append(support)
    def deltas(values):
        base=values[index[0.,0.]]
        result=[]
        for w,i in ordered:
            value=values[index[w,i]]-base
            if w and i:
                value=values[index[w,1.]]-values[index[w,0.]]-values[index[0.,1.]]+base
            result.append(value)
        return base,result
    return supports,deltas


def merge_math_variations(font, masters, model):
    """Preserve the complete static MATH contract using the existing GDEF store.

    All MathValueRecords (at any depth) can use VariationIndex device tables.
    Plain integer construction fields cannot; differing values are an error,
    never a reason to keep the default silently. Existing GPOS indexes retain
    both their outer/inner indexes and region identities.
    """
    present=['MATH' in f for f in masters]
    if not any(present):
        return {'present':False}
    if not all(present):
        raise ValueError('MATH must be present in every finished master.')
    builder=OnlineVarStoreBuilder([a.axisTag for a in font['fvar'].axes])
    supports,integer_deltas=math_hat_plan(model)
    builder.setSupports(supports)
    devices=[]
    paths=[]
    varying=[]
    def walk(values, target, path):
        first=values[0]
        if isinstance(first,otTables.MathValueRecord):
            if not all(isinstance(x,otTables.MathValueRecord) for x in values):
                raise ValueError(f'MATH structure differs at {path}.')
            if any(getattr(x,'DeviceTable',None) is not None for x in values):
                raise ValueError(f'Existing MATH device table requires explicit composition: {path}.')
            nums=[x.Value for x in values]
            paths.append(path)
            if len(set(nums))==1:
                target.Value=nums[0];target.DeviceTable=None
            else:
                base,deltas=integer_deltas(nums)
                index=builder.storeDeltas(deltas)
                target.Value=base;target.DeviceTable=buildVarDevTable(index)
                devices.append(target.DeviceTable);varying.append(path)
            return
        if first is None or isinstance(first,(int,float,str,bytes,bool)):
            if any(x!=first for x in values):
                raise ValueError(f'Non-variable MATH field differs at {path}: {values!r}')
            return
        if isinstance(first,list):
            if any(not isinstance(x,list) or len(x)!=len(first) for x in values):
                raise ValueError(f'MATH list structure differs at {path}.')
            for i in range(len(first)):
                walk([x[i] for x in values],target[i],f'{path}[{i}]')
            return
        keys=set(vars(first))
        if any(type(x) is not type(first) or set(vars(x))!=keys for x in values):
            raise ValueError(f'MATH object structure differs at {path}.')
        for key in sorted(keys):
            walk([getattr(x,key) for x in values],getattr(target,key),f'{path}.{key}')
    walk([f['MATH'].table for f in masters],font['MATH'].table,'MATH')
    if devices:
        extra=builder.finish()
        if 'GDEF' not in font:
            from fontTools.ttLib import newTable
            font['GDEF']=newTable('GDEF');font['GDEF'].table=otTables.GDEF()
        gdef=font['GDEF'].table
        existing=getattr(gdef,'VarStore',None)
        if existing is None:
            gdef.VarStore=extra
        else:
            if existing.VarRegionList.RegionAxisCount!=extra.VarRegionList.RegionAxisCount:
                raise ValueError('MATH and GPOS variation-store axis counts differ.')
            offset=len(existing.VarData)
            def region_key(region):
                return tuple((a.StartCoord,a.PeakCoord,a.EndCoord) for a in region.VarRegionAxis)
            indices={region_key(r):i for i,r in enumerate(existing.VarRegionList.Region)}
            remap={}
            for i,region in enumerate(extra.VarRegionList.Region):
                key=region_key(region)
                if key not in indices:
                    indices[key]=len(existing.VarRegionList.Region)
                    existing.VarRegionList.Region.append(region)
                remap[i]=indices[key]
            for data in extra.VarData:
                data.VarRegionIndex=[remap[i] for i in data.VarRegionIndex]
            existing.VarData.extend(extra.VarData)
            existing.VarDataCount=len(existing.VarData)
            existing.VarRegionList.RegionCount=len(existing.VarRegionList.Region)
            for device in devices:
                device.StartSize+=offset
        gdef.Version=max(getattr(gdef,'Version',0x00010000),0x00010003)
    return {'present':True,'interpolation':'Exact local piecewise-linear tensor hats; integer endpoint and style-interaction deltas.',
            'supports':supports,'math_value_records':len(paths),'varying_records':len(varying),
            'varying_paths':varying,'all_paths':paths,
            'plain_field_policy':'All non-MathValueRecord fields must be identical across masters.'}


def exact_phantom_variations(font, masters, model):
    """Use original integer phantom metrics, without changing outline deltas."""
    supports, coefficients = math_hat_plan(model)
    default = next(i for i, location in enumerate(model.origLocations) if not any(location.values()))
    glyphs = font.getGlyphOrder()
    for name in glyphs:
        originals = [master['glyf']._getCoordinatesAndControls(name, master['hmtx'].metrics)[0] for master in masters]
        count = len(originals[default])
        if any(len(c) != count for c in originals):
            raise ValueError(f'Phantom source topology differs: {name}')
        baseline = font['glyf']._getCoordinatesAndControls(name, font['hmtx'].metrics)[0][-4:]
        if list(baseline) != list(originals[default][-4:]):
            raise ValueError(f'Phantom default source differs: {name}')
        for variation in font['gvar'].variations[name]:
            variation.coordinates[-4:] = [(0, 0)] * 4
        terms = [[(0, 0)] * 4 for _ in supports]
        for point in range(4):
            for axis in (0, 1):
                values = [c[-4+point][axis] for c in originals]
                if any(int(value) != value for value in values):
                    raise ValueError(f'Noninteger original phantom metric: {name}')
                base, deltas = coefficients(values)
                for k, delta in enumerate(deltas):
                    value = list(terms[k][point]); value[axis] = delta
                    terms[k][point] = tuple(value)
        for support, phantoms in zip(supports, terms):
            if any(x or y for x, y in phantoms):
                font['gvar'].variations[name].append(TupleVariation(support, [None]*(count-4)+phantoms))
    return {'glyphs': len(glyphs), 'source_node_checks': len(glyphs)*len(masters),
            'policy': 'Exact integer local hats from original metric-owner phantoms; every nonphantom outline delta retained.'}


def logical_position_lookup(lookup):
    """Validate one GPOS lookup; remove only an explicit valid ExtensionPos shell."""
    classes = {1: otTables.SinglePos, 2: otTables.PairPos, 3: otTables.CursivePos,
               4: otTables.MarkBasePos, 5: otTables.MarkLigPos, 6: otTables.MarkMarkPos,
               7: otTables.ContextPos, 8: otTables.ChainContextPos}
    kind = lookup.LookupType
    if type(kind) is not int or kind not in (*classes, 9):
        raise ValueError('Unknown GPOS lookup type in logical positioning view.')
    if type(lookup.SubTableCount) is not int or lookup.SubTableCount != len(lookup.SubTable):
        raise ValueError('GPOS subtable count does not match ordered subtables.')
    effective = kind
    subtables = list(lookup.SubTable)
    if kind == 9:
        declared = []
        for sub in subtables:
            if type(sub) is not otTables.ExtensionPos:
                raise ValueError('Type-9 lookup requires ExtensionPos subtables.')
            if set(vars(sub)) != {'Format', 'ExtensionLookupType', 'ExtSubTable'}:
                raise ValueError('Unknown or missing ExtensionPos metadata; phase is unsupported.')
            if type(sub.Format) is not int or sub.Format != 1:
                raise ValueError('Only explicit ExtensionPos format 1 is supported.')
            target = sub.ExtensionLookupType
            if type(target) is not int or target not in classes:
                raise ValueError('Invalid or nested ExtensionPos effective lookup type.')
            if type(sub.ExtSubTable) is not classes[target]:
                raise ValueError('ExtensionPos declared type differs from actual underlying table.')
            declared.append(target)
        if not declared or len(set(declared)) != 1:
            raise ValueError('Mixed or empty ExtensionPos effective types are unsupported.')
        effective = declared[0]
        subtables = [sub.ExtSubTable for sub in subtables]
    elif any(type(sub) is not classes[kind] for sub in subtables):
        raise ValueError('Direct GPOS lookup type differs from actual subtable class.')
    result = copy.copy(lookup)
    result.LookupType = effective
    result.SubTable = subtables
    # All outer attributes, flags, mark-filter fields and ordered children remain.
    return result


def physical_position_path(root, path):
    """Resolve a logical anchor path to the same actual target object, without sorting."""
    if not isinstance(root, otTables.Lookup):
        return path
    view = logical_position_lookup(root)
    if root.LookupType != 9:
        return path
    if len(path) < 2 or path[0] != 'SubTable' or type(path[1]) is not int:
        raise ValueError('Logical anchor path does not identify an ordered positioning subtable.')
    if not 0 <= path[1] < len(view.SubTable):
        raise ValueError('Logical positioning subtable path is outside the lookup.')
    return path[:2] + ('ExtSubTable',) + path[2:]


def anchor_paths(value, path=()):
    """Logical source paths, before conditional lookup-group cloning."""
    if isinstance(value, otTables.Lookup):
        value = logical_position_lookup(value)
    if isinstance(value, otTables.Anchor):
        return {path: value}
    result = {}
    if isinstance(value, list):
        for i, child in enumerate(value):
            result.update(anchor_paths(child, path+(i,)))
    elif hasattr(value, '__dict__'):
        for key, child in vars(value).items():
            if key not in ('reader', 'font'):
                result.update(anchor_paths(child, path+(key,)))
    return result


def anchor_lookup_structure(value):
    """Retain coverage, class, contextual references and order; ignore only anchors."""
    if isinstance(value, otTables.Lookup):
        value = logical_position_lookup(value)
    if isinstance(value, otTables.Anchor):
        return 'Anchor'
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [anchor_lookup_structure(child) for child in value]
    if isinstance(value, dict):
        return {key: anchor_lookup_structure(child) for key, child in value.items()}
    return {key: anchor_lookup_structure(child) for key, child in vars(value).items()
            if key not in ('reader', 'font') and not key.startswith('_')}


def private_anchor_at(root, path):
    """Isolate a semantic anchor path even if compiled source objects shared offsets."""
    path = physical_position_path(root, path)
    parent = root
    for key in path:
        child = parent[key] if isinstance(key, int) else getattr(parent, key)
        child = copy.copy(child)
        if isinstance(key, int):
            parent[key] = child
        else:
            setattr(parent, key, child)
        parent = child
    return parent


def append_exact_store(font, extra):
    """Append without rewriting any existing region or variation index."""
    gdef = font['GDEF'].table
    existing = getattr(gdef, 'VarStore', None)
    offset = len(existing.VarData) if existing else 0
    if existing:
        if existing.VarRegionList.RegionAxisCount != extra.VarRegionList.RegionAxisCount:
            raise ValueError('Exact GPOS store axis order/count differs.')
        region_offset = len(existing.VarRegionList.Region)
        for data in extra.VarData:
            data.VarRegionIndex = [i+region_offset for i in data.VarRegionIndex]
        existing.VarRegionList.Region.extend(extra.VarRegionList.Region)
        existing.VarRegionList.RegionCount = len(existing.VarRegionList.Region)
        existing.VarData.extend(extra.VarData)
        existing.VarDataCount = len(existing.VarData)
    else:
        gdef.VarStore = extra
    gdef.Version = max(gdef.Version, 0x00010003)
    return offset


def exact_anchor_variations(font, masters, model, sparse_cases):
    """Store complete original Anchor grids before rounding/index dedup can erase them."""
    if 'GPOS' not in font:
        return {'present': False}
    target = font['GPOS'].table.LookupList.Lookup
    sources = [master['GPOS'].table.LookupList.Lookup for master in masters]
    if any(len(lookups) != len(target) for lookups in sources):
        raise ValueError('Original GPOS lookup lists differ before exact anchor merging.')
    supports, coefficients = math_hat_plan(model)
    store = OnlineVarStoreBuilder([axis.axisTag for axis in font['fvar'].axes])
    store.setSupports(supports)
    changes = []; skipped = []; vectors = []; coordinates = 0
    for li, lookup in enumerate(target):
        originals = [lookups[li] for lookups in sources]
        source_maps = [anchor_paths(value) for value in originals]
        targets = anchor_paths(lookup)
        if not targets:
            continue
        structure = anchor_lookup_structure(originals[0])
        if any(anchor_lookup_structure(value) != structure for value in originals[1:]):
            raise ValueError(f'Original GPOS anchor semantics differ in lookup {li}.')
        if anchor_lookup_structure(lookup) != structure:
            raise ValueError(f'GPOS anchor coverage/class/context topology changed in lookup {li}.')
        common = set(targets).intersection(*(set(values) for values in source_maps))
        sparse_paths = set()
        for case in sparse_cases:
            ci, si, glyph, anchor_class = case['key']
            if ci != li:
                continue
            sub = _position_subtable(masters[0], li, si)
            index = sub.BaseCoverage.glyphs.index(glyph)
            suffix = ('BaseArray', 'BaseRecord', index, 'BaseAnchor', anchor_class)
            sparse_paths.update(path for path in common if path[:2] == ('SubTable', si) and path[-len(suffix):] == suffix)
        for path in sorted(targets, key=repr):
            if path not in common or path in sparse_paths:
                skipped.append({'lookup': li, 'path': path, 'reason': 'Outside a complete original availability grid.'})
                continue
            anchor = private_anchor_at(lookup, path)
            devices = {}
            for coordinate, device_name in [('XCoordinate', 'XDeviceTable'), ('YCoordinate', 'YDeviceTable')]:
                values = [getattr(values[path], coordinate) for values in source_maps]
                if any(int(value) != value for value in values):
                    raise ValueError(f'Noninteger original Anchor grid in lookup {li}, {path}.')
                base, deltas = coefficients(values)
                setattr(anchor, coordinate, base)
                devices[device_name] = store.storeDeltas(deltas) if any(deltas) else None
                vectors.append([li, path, coordinate, values]); coordinates += 1
            anchor.Format = 3 if any(index is not None for index in devices.values()) else 1
            for name, index in devices.items():
                if anchor.Format == 3:
                    setattr(anchor, name, None)
                    if index is not None:
                        changes.append((anchor, name, index))
                elif hasattr(anchor, name):
                    delattr(anchor, name)
    if changes:
        offset = append_exact_store(font, store.finish())
        for anchor, name, index in changes:
            value = (((index >> 16)+offset) << 16) | (index & 65535)
            if value >> 16 >= 65536:
                raise ValueError('Exact GPOS store exceeds VariationIndex outer range.')
            setattr(anchor, name, buildVarDevTable(value))
    return {'present': True, 'complete_anchor_coordinates': coordinates,
            'varying_coordinates': len(changes), 'sparse_paths_skipped': skipped,
            'original_grid_sha256': hashlib.sha256(json.dumps(vectors, separators=(',', ':')).encode()).hexdigest(),
            'policy': 'Original integer Anchor grids before rounding/dedup; semantic paths before any conditional lookup cloning. Existing shared-store prefixes preserved.',
            'limits': 'Non-anchor ValueRecords and incomplete availability grids are unchanged.'}


def discrete_style_profiles(font, shared):
    """Preserve public binary ital selection for shared structural/control profiles."""
    threshold = .5
    before = threshold - 1/16384
    regions = ((before, threshold, 1.), (threshold, 1., 1.))
    changed = []
    for name, variations in font['gvar'].variations.items():
        if name not in shared:
            if any('ital' in v.axes and any(p is not None and any(p) for p in v.coordinates) for v in variations):
                raise ValueError(f'Unexpected style-dependent nonshared glyph requires review: {name}')
            continue
        expanded = []
        for variation in variations:
            if 'ital' not in variation.axes:
                expanded.append(variation)
                continue
            if variation.axes['ital'] != (0., 1., 1.):
                raise ValueError(f'Unexpected shared glyph style support: {name}, {variation.axes}')
            for support in regions:
                axes = dict(variation.axes); axes['ital'] = support
                expanded.append(TupleVariation(axes, copy.deepcopy(variation.coordinates)))
        font['gvar'].variations[name] = expanded
        changed.append({'name': name, 'old_tuples': len(variations), 'new_tuples': len(expanded)})
    axis = next(i for i, a in enumerate(font['fvar'].axes) if a.axisTag == 'ital')
    mvar_changes = []
    if 'MVAR' in font:
        store = font['MVAR'].table.VarStore
        original = list(store.VarRegionList.Region)
        result = list(original); expansion = {}
        for i, region in enumerate(original):
            triplet = region.VarRegionAxis[axis]
            if not triplet.PeakCoord:
                continue
            if (triplet.StartCoord, triplet.PeakCoord, triplet.EndCoord) != (0., 1., 1.):
                raise ValueError('Unexpected MVAR style support requires review.')
            first, second = copy.deepcopy(region), copy.deepcopy(region)
            for value, support in zip((first, second), regions):
                value.VarRegionAxis[axis].StartCoord, value.VarRegionAxis[axis].PeakCoord, value.VarRegionAxis[axis].EndCoord = support
            result[i] = first
            expansion[i] = (i, len(result)); result.append(second)
            mvar_changes.append(i)
        store.VarRegionList.Region = result
        store.VarRegionList.RegionCount = len(result)
        data = []
        for block in store.VarData:
            indices = [new for old in block.VarRegionIndex for new in expansion.get(old, (old,))]
            rows = [[delta for old, delta in zip(block.VarRegionIndex, row) for _ in expansion.get(old, (old,))] for row in block.Item]
            data.append(buildVarData(indices, rows, optimize=True))
        store.VarData = data; store.VarDataCount = len(data)
    # Unreviewed style-dependent shared-store/vertical participants must not be
    # silently changed by a global normalization map. Current GPOS is weight-only.
    for tag in ('GDEF', 'HVAR', 'VVAR'):
        if tag not in font:
            continue
        store = getattr(font[tag].table, 'VarStore', None)
        if store is None:
            continue
        active = set()
        for block in store.VarData:
            for column, index in enumerate(block.VarRegionIndex):
                if store.VarRegionList.Region[index].VarRegionAxis[axis].PeakCoord and any(row[column] for row in block.Item):
                    active.add(index)
        if active:
            raise ValueError(f'{tag} has active ital-dependent records requiring discrete-style integration: {sorted(active)}')
    if 'GPOS' in font:
        variations = getattr(font['GPOS'].table, 'FeatureVariations', None)
        if variations and any(condition.AxisIndex == axis for record in variations.FeatureVariationRecord for condition in record.ConditionSet.ConditionTable):
            raise ValueError('GPOS style-conditional availability requires explicit normalization review.')
    font['avar'].segments['ital'] = {-1.: -1., 0.: 0., before: 0., threshold: 1., 1.: 1.}
    return {'shared_profiles': changed, 'MVAR_expanded_regions': mvar_changes,
            'public_style_threshold': threshold, 'F2Dot14_before_threshold': before,
            'future_participant_policy': 'Active GDEF/MATH or vertical-store style regions fail loudly until explicitly integrated; no invented support.'}


def input_alias(a, b):
    a, b = Path(a), Path(b)
    return a.resolve() == b.resolve() or (a.exists() and b.exists() and a.samefile(b))


def check_input_outputs(outputs, inputs):
    outputs = [Path(p) for p in outputs if p is not None]
    if any(input_alias(p, q) for i, p in enumerate(outputs) for q in outputs[:i]):
        raise ValueError('Font, work and report outputs must be distinct files.')
    if any(input_alias(p, q) for p in outputs for q in inputs):
        raise ValueError('Output/report must never alias an input (including hardlinks).')


def recheck_inputs(hashes):
    for path, expected in hashes.items():
        if sha256(Path(path)) != expected:
            raise ValueError(f'Input changed during the build: {path}')


def complete_cmaps(font):
    # Include every subtable, including Unicode variation sequences (format 14).
    return sorted((t.platformID, t.platEncID, t.language, t.format,
                   sorted(getattr(t, 'cmap', {}).items()),
                   repr(sorted(getattr(t, 'uvsDict', {}).items())))
                  for t in font['cmap'].tables)


def auxiliary_geometry(manifest, manifest_sha256, paths, fonts, outputs):
    """Validate immutable snapshots; import only explicitly selected raw outlines.

    Declarations and point signatures are intake conditions, not proof that raw
    curves correspond or reproduce the original statics. Independent verification
    against --masters is still mandatory.
    """
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    def fields(obj, names, where):
        require(isinstance(obj, dict) and set(obj) == set(names),
                f'{where}: exact fields required: {names}')
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    manifest = Path(manifest).resolve()
    raw = manifest.read_bytes()
    require(isinstance(manifest_sha256, str) and len(manifest_sha256) == 64
            and all(c in '0123456789abcdef' for c in manifest_sha256),
            'Auxiliary manifest requires its lowercase SHA256 digest.')
    require(hashlib.sha256(raw).hexdigest() == manifest_sha256, 'Auxiliary manifest hash mismatch.')
    data = json.loads(raw, object_pairs_hook=unique_pairs)
    fields(data, ('schema', 'version', 'generator', 'source_mode', 'originals', 'auxiliaries', 'replacements'), 'manifest')
    require(data['schema'] == 'torchlette-auxiliary-geometry' and type(data['version']) is int
            and data['version'] == 1, 'Unsupported auxiliary manifest schema/version.')
    require(isinstance(data['source_mode'], str) and data['source_mode'].strip(), 'source_mode is required.')
    fields(data['generator'], ('source', 'config', 'commit'), 'generator')
    require(isinstance(data['generator']['commit'], str) and data['generator']['commit'].strip(), 'Generator commit is required.')
    hashes = {str(manifest): manifest_sha256}
    seen = [manifest]
    def file_record(record):
        fields(record, ('path', 'sha256'), 'file')
        require(isinstance(record['path'], str) and bool(record['path']) and
                isinstance(record['sha256'], str), 'Invalid file record.')
        path = (manifest.parent / record['path']).resolve()
        require(not any(input_alias(path, p) for p in seen), f'Auxiliary input alias: {path}')
        content = path.read_bytes()
        require(hashlib.sha256(content).hexdigest() == record['sha256'], f'Input hash mismatch: {path}')
        seen.append(path)
        hashes[str(path)] = record['sha256']
        return path, content
    for key in ('source', 'config'):
        file_record(data['generator'][key])
    expected = set(fonts)
    auxiliaries = {}
    for kind in ('originals', 'auxiliaries'):
        rows = data[kind]
        require(isinstance(rows, list) and len(rows) == 14, f'{kind}: fourteen fonts required.')
        locations = set()
        for row in rows:
            fields(row, ('weight', 'ital', 'file'), kind)
            require(type(row['weight']) is int and type(row['ital']) is int, 'Style coordinates must be integers.')
            loc = (row['weight'], row['ital'])
            require(loc in expected and loc not in locations, f'Unknown/duplicate {kind} style: {loc}')
            locations.add(loc)
            path, content = file_record(row['file'])
            if kind == 'originals':
                require(input_alias(path, paths[loc]), f'Manifest original does not identify --masters at {loc}')
                # The build already loaded immutable original bytes; require that
                # snapshot, not a later disk epoch, to match the pinned manifest.
                require(hashlib.sha256(content).hexdigest() == fonts[loc]._input_sha256,
                        f'Original snapshot differs from manifest at {loc}')
            else:
                auxiliaries[loc] = TTFont(io.BytesIO(content), recalcTimestamp=False, recalcBBoxes=False)
    check_input_outputs(outputs, seen)
    reference = fonts[400, 0]
    order = reference.getGlyphOrder()
    cmap = complete_cmaps(reference)
    upem = reference['head'].unitsPerEm
    selections = {}
    require(isinstance(data['replacements'], list) and data['replacements'], 'Explicit replacements required.')
    prohibited = {order[0]} | {g for cp, g in reference.getBestCmap().items() if default_ignorable(cp)}
    for row in data['replacements']:
        fields(row, ('glyph', 'ital', 'curve_provenance'), 'replacement')
        name, slants = row['glyph'], row['ital']
        require(isinstance(name, str) and name in order and name not in selections, 'Unknown/duplicate replacement glyph.')
        require(name not in prohibited, 'Shared structural/default-ignorable replacements require separate support.')
        require(isinstance(slants, list) and slants and all(type(i) is int and i in (0, 1) for i in slants)
                and len(set(slants)) == len(slants), 'Invalid/duplicate replacement styles.')
        require(isinstance(row['curve_provenance'], str) and row['curve_provenance'].strip(), 'Curve provenance is required.')
        selections[name] = set(slants)
    grids = {}
    faces = []
    parent_grids = {}
    for loc in sorted(expected):
        original, aux = fonts[loc], auxiliaries[loc]
        def style(f):
            return (f['OS/2'].usWeightClass, bool(f['OS/2'].fsSelection & 1),
                    bool(f['head'].macStyle & 2), f['name'].getDebugName(2))
        for label, f in [('original', original), ('auxiliary', aux)]:
            require(f.getGlyphOrder() == order and complete_cmaps(f) == cmap and f['head'].unitsPerEm == upem,
                    f'{label} glyph order/full cmap/UPEM differs at {loc}')
        require(style(original)[:3] == (loc[0], bool(loc[1]), bool(loc[1])), f'Original style mismatch at {loc}')
        require(style(original) == style(aux), f'Auxiliary style mismatch at {loc}')
        selected = {n for n, slants in selections.items() if loc[1] in slants}
        reverse = {}
        for name in order:
            g = original['glyf'][name]
            if g.isComposite():
                for component in g.components:
                    reverse.setdefault(component.glyphName, set()).add(name)
        parents = set()
        pending = list(selected)
        while pending:
            for name in reverse.get(pending.pop(), ()):
                if name not in parents:
                    parents.add(name)
                    pending.append(name)
        # Scope support guards to the selected dependency closure. Ordinary,
        # unrelated scaled-metric composites keep their existing canonicalizer.
        for name in sorted(parents):
            g = original['glyf'][name]
            parent_grids.setdefault((name, loc[1]), []).append(signature(original, name))
            for c in g.components:
                require(hasattr(c, 'x'), f'Unsupported affected point-matched parent: {name}')
                if c.flags & 0x200:
                    require(c.getComponentInfo()[1][:4] == (1, 0, 0, 1)
                            and original['hmtx'][name][0] == original['hmtx'][c.glyphName][0],
                            f'Unsupported affected metric-owner transform/advance: {name}')
        facts = {}
        for name in sorted(selected):
            require(not original['glyf'][name].isComposite(), f'Unsupported selected original composite: {name}')
            g = aux['glyf'][name]
            require(not g.isComposite() and g.numberOfContours > 0, f'Replacement must be a nonempty raw simple glyph: {name}')
            require(len(g.flags) > 0 and int(g.flags[0]) & 64, f'OVERLAP_SIMPLE missing: {name}')
            grids.setdefault((name, loc[1]), []).append(signature(aux, name))
            facts[name] = {'original_hmtx': list(original['hmtx'][name]),
                           'ignored_auxiliary_hmtx': list(aux['hmtx'][name])}
        differences = {}
        for tag in sorted((set(original.keys()) | set(aux.keys())) - {'GlyphOrder', 'glyf', 'loca'}):
            a = original.getTableData(tag) if tag in original else None
            b = aux.getTableData(tag) if tag in aux else None
            if a != b:
                differences[tag] = {'original': hashlib.sha256(a).hexdigest() if a is not None else None,
                                    'ignored_auxiliary': hashlib.sha256(b).hexdigest() if b is not None else None}
        faces.append({'weight': loc[0], 'ital': loc[1], 'selected': facts, 'affected_parents': sorted(parents),
                      'ignored_auxiliary_tables': differences})
    for key, signatures in {**grids, **{('parent:' + n, i): v for (n, i), v in parent_grids.items()}}.items():
        require(len(signatures) == 7 and all(s == signatures[0] for s in signatures), f'Incompatible selected/parent grid: {key}')
    recheck_inputs(hashes)
    return auxiliaries, selections, hashes, {'manifest': str(manifest), 'sha256': manifest_sha256,
        'source_mode': data['source_mode'], 'generator': data['generator'], 'replacements': data['replacements'],
        'faces': faces, 'input_sha256': hashes,
        'policy': 'Only selected raw contours imported; original metrics and layout retained. Signatures and provenance declarations are necessary, not sufficient; original-static endpoint/intermediate verification remains required.'}


def build(masters: Path, output: Path, work: Path, woff2: Path | None = None,
          auxiliary_manifest: Path | None = None, auxiliary_sha256: str | None = None,
          report_path: Path | None = None):
    if (auxiliary_manifest is None) != (auxiliary_sha256 is None):
        raise ValueError('Auxiliary manifest and SHA256 must be supplied together.')
    paths={}
    fonts={}
    input_hashes={}
    for weight,style in WEIGHTS:
        for ital,name in [(0,style),(1,italic_style(style))]:
            path=masters/f'TorchletteSans-{name}.ttf'
            if not path.is_file():
                raise ValueError(f'Missing finished static master: {path}')
            if path.resolve() in {output.resolve(), *( [woff2.resolve()] if woff2 else [])}:
                raise ValueError('Variable output must never overwrite a static input.')
            paths[weight,ital]=path
            raw=path.read_bytes()
            input_hashes[str(path)]=hashlib.sha256(raw).hexdigest()
            fonts[weight,ital]=TTFont(io.BytesIO(raw),recalcTimestamp=False,recalcBBoxes=False)
            fonts[weight,ital]._input_sha256=input_hashes[str(path)]
    if woff2 and woff2.resolve()==output.resolve():
        raise ValueError('TTF and WOFF2 outputs must be distinct files.')
    generated=[output,woff2,report_path,work/'TorchletteSans.designspace']
    generated += [work/f'{prefix}-{w}-{i}.ttf' for prefix in ('prepared','master') for w,_ in WEIGHTS for i in (0,1)]
    if any(input_alias(p,q) for k,p in enumerate(paths.values()) for q in list(paths.values())[:k]):
        raise ValueError('Static inputs must not alias each other.')
    check_input_outputs(generated,paths.values())
    auxiliaries={}; selections={}; auxiliary_report=None; auxiliary_hashes={}
    if auxiliary_manifest is not None:
        auxiliaries,selections,auxiliary_hashes,auxiliary_report=auxiliary_geometry(
            auxiliary_manifest,auxiliary_sha256,paths,fonts,generated)
    work.mkdir(parents=True,exist_ok=True)
    order=fonts[400,0].getGlyphOrder()
    cmap_mapping=fonts[400,0].getBestCmap()
    cmap=set(cmap_mapping)
    invisible={glyph for cp,glyph in fonts[400,0].getBestCmap().items() if default_ignorable(cp)}
    structural={order[0]}
    shared=invisible|structural
    for loc,f in fonts.items():
        if f.getGlyphOrder()!=order or f.getBestCmap()!=cmap_mapping or f['head'].unitsPerEm!=fonts[400,0]['head'].unitsPerEm:
            raise ValueError(f'Glyph order/cmap differs at {loc}; refusing to omit or invent glyphs.')
        strip_static_hints(f)
    report={'builder_source_sha256':SOURCE_SHA256,'python':sys.version,
            'tool_versions':{name:importlib.metadata.version(name) for name in ('fonttools','skia-pathops','brotli')},
            'outline_policy':'Normalize identical nonzero filled shapes, align reference anchors, subdivide quadratic curves exactly, round to integer TrueType points.',
            'input_sha256':input_hashes,'axes':{'wght':[300,400,900],'ital':[0,0,1]},
            'italic_policy':'Required discrete style branch at ital >=0.5; no synthetic oblique.',
            'hint_policy':'Variable companion unhinted; static hinted input files preserved.',
            'source_glyphs':len(order),'source_cmap':len(cmap),'canonicalization':{}}
    report['source_composite_fill']={f'{w}-{i}':audit_source_composite_fill(fonts[w,i]) for w,_ in WEIGHTS for i in (0,1)}
    report['origin_rebasing']={f'{w}-{i}':rebase_source_origins(fonts[w,i]) for w,_ in WEIGHTS for i in (0,1)}
    if auxiliary_report is not None:
        auxiliary_report['origin_rebasing']={}
        for loc,aux in auxiliaries.items():
            offsets={}
            for name,slants in selections.items():
                if loc[1] in slants:
                    # Selection validation permits only simple raw glyphs.
                    # Their own phantom origin is xMin-LSB; no auxiliary parent,
                    # metric owner, hint table or layout table participates.
                    g=copy.deepcopy(aux['glyf'][name])
                    shift=g.xMin-aux['hmtx'][name][1]
                    g.removeHinting()
                    if shift:
                        g.coordinates.translate((-shift,0))
                        g.xMin-=shift;g.xMax-=shift
                    fonts[loc]['glyf'][name]=g
                    offsets[name]=shift
            auxiliary_report['origin_rebasing'][f'{loc[0]}-{loc[1]}']={'selected_simple_origin_offsets':offsets}
        report['auxiliary_geometry']=auxiliary_report
    for ital in (0,1):
        report['canonicalization'][str(ital)]=canonicalize([fonts[w,ital] for w,_ in WEIGHTS], only=set(order)-{n for n,ss in selections.items() if ital in ss})
    original_meta=copy.deepcopy(fonts[400,0].get('meta'))
    merged=[]
    mapping=None
    for weight,style in WEIGHTS:
        files=[]
        for ital in (0,1):
            f=fonts[weight,ital]
            if 'meta' in f:
                del f['meta']
            if ital:
                f['cmap'].tables=[]
            path=work/f'prepared-{weight}-{ital}.ttf'
            f.save(path,reorderTables=True)
            files.append(path)
        m=Merger()
        combined=m.merge(files)
        if len(combined.getGlyphOrder())!=2*len(order):
            raise ValueError('Style merge changed the complete glyph count.')
        current_mapping=dict(zip(order,combined.getGlyphOrder()[len(order):]))
        if mapping is None:
            mapping=current_mapping
        elif mapping!=current_mapping:
            raise ValueError('Italic glyph namespace is inconsistent across weights.')
        for tag in LAYOUT_TABLES:
            if tag in fonts[weight,0] and tag not in combined:
                raise ValueError(f'Style merger cannot preserve {tag}; requires explicit table support.')
        if original_meta is not None:
            combined['meta']=copy.deepcopy(original_meta)
        if set(combined.getBestCmap())!=cmap:
            raise ValueError('Style merge lost Unicode coverage.')
        for ital in (0,1):
            f=copy.deepcopy(combined)
            if ital:
                for glyph in shared:
                    f['glyf'][glyph]=copy.deepcopy(f['glyf'][mapping[glyph]])
                    f['hmtx'][glyph]=f['hmtx'][mapping[glyph]]
            if 'MATH' in f:
                f['MATH'].table.MathConstants=copy.deepcopy(fonts[weight,ital]['MATH'].table.MathConstants)
            # Retain style-specific global metrics so varLib can make MVAR deltas.
            for tag,attr in sorted(set(MVAR_ENTRIES.values())):
                if tag in f and tag in fonts[weight,ital] and hasattr(fonts[weight,ital][tag],attr):
                    setattr(f[tag],attr,getattr(fonts[weight,ital][tag],attr))
            f['post'].italicAngle=fonts[weight,ital]['post'].italicAngle
            f.recalcTimestamp=False;f.recalcBBoxes=False
            f['head'].created=f['head'].modified=TIMESTAMP
            path=work/f'master-{weight}-{ital}.ttf';f.save(path,reorderTables=True)
            merged.append((weight,ital,path))
    sparse_fonts=[TTFont(path,recalcTimestamp=False,recalcBBoxes=False) for _,_,path in merged]
    report['shared_control_canonicalization']=canonicalize(sparse_fonts,only=shared)
    for font in sparse_fonts:
        normalize_variable_bearings(font)
    sparse_cases=prepare_sparse_anchors(sparse_fonts,[(w,i) for w,i,_ in merged])
    for font,(_,_,path) in zip(sparse_fonts,merged):
        font.save(path,reorderTables=True)
    report['sparse_anchor_availability']=sparse_cases
    ds=DesignSpaceDocument()
    for tag,name,minimum,default,maximum in [('wght','Weight',300,400,900),('ital','Italic',0,0,1)]:
        axis=AxisDescriptor();axis.tag=tag;axis.name=name;axis.minimum=minimum;axis.default=default;axis.maximum=maximum
        if tag=='wght':
            axis.map=WEIGHT_MAP
        ds.addAxis(axis)
    for weight,ital,path in merged:
        source=SourceDescriptor();source.path=str(path);source.name=f'{weight}-{ital}';source.location={'Weight':piecewiseLinearMap(weight,dict(WEIGHT_MAP)),'Italic':ital};source.copyInfo=source.copyLib=source.copyFeatures=(weight,ital)==(400,0);ds.addSource(source)
    for weight,style in WEIGHTS:
        for ital in (0,1):
            ins=InstanceDescriptor();file_style=italic_style(style) if ital else style;ins.name=('Italic' if style=='Regular' else style+' Italic') if ital else style;ins.familyName='Torchlette Sans Variable';ins.styleName=ins.name;ins.postScriptFontName='TorchletteSansVariable-'+file_style;ins.location={'Weight':piecewiseLinearMap(weight,dict(WEIGHT_MAP)),'Italic':ital};ds.addInstance(ins)
    ds.write(work/'TorchletteSans.designspace')
    vf,model,_=build_variable(ds,optimize=True,exclude=['HVAR','gvar'],drop_implied_oncurves=False)
    build_gvar(vf,model,sparse_fonts,tolerance=0,optimize=True)
    report['exact_phantom_metrics']=exact_phantom_variations(vf,sparse_fonts,model)
    report['exact_gpos_anchors']=exact_anchor_variations(vf,sparse_fonts,model,sparse_cases)
    missing_gvar=set(vf.getGlyphOrder())-set(vf['gvar'].variations)
    if missing_gvar:
        raise ValueError(f'Incompatible gvar masters were skipped: {sorted(missing_gvar)}')
    report['gvar_glyph_entries']=len(vf['gvar'].variations)
    report['gvar_precision']='Exact IUP compression (zero coordinate-error tolerance); integer tuple encoding remains independently checked.'
    report['avar_master_intervals']=stabilize_master_avar(vf)
    report['horizontal_metrics']={'policy':'Complete advance and bearing phantom metrics in gvar; optional HVAR omitted to preserve composite-origin deltas in rasterizers.'}
    if 'MATH' in vf:
        validation_font=copy.deepcopy(vf)
        validation_font['MATH']=copy.deepcopy(fonts[400,0]['MATH'])
        report['source_math_contract']=merge_math_variations(validation_font,list(fonts.values()),model)
    report['math_variations']=merge_math_variations(vf,sparse_fonts,model)
    report['sparse_anchor_lookup_policy']=install_sparse_anchor_variations(vf,sparse_cases)
    branch_mapping={g:target for g,target in mapping.items() if g not in shared}
    addFeatureVariations(vf,[([{'ital':(.5,1.)}],branch_mapping)],featureTag='rvrn')
    report['discrete_shared_style']=discrete_style_profiles(vf,shared)
    buildStatTable(vf,[{'tag':'wght','name':'Weight','ordering':0,'values':[{'value':w,'name':s,'flags':2 if w==400 else 0} for w,s in WEIGHTS]},
                       {'tag':'ital','name':'Italic','ordering':1,'values':[{'value':0,'name':'Roman','flags':2,'linkedValue':1},{'value':1,'name':'Italic'}]}])
    names={1:'Torchlette Sans Variable',2:'Regular',3:'1.000;TSAN;TorchletteSansVariable',4:'Torchlette Sans Variable',6:'TorchletteSansVariable',16:'Torchlette Sans Variable',17:'Regular',25:'TorchletteSansVariable'}
    for nid,value in names.items():
        vf['name'].removeNames(nameID=nid);vf['name'].setName(value,nid,3,1,0x409)
    vf['head'].created=vf['head'].modified=TIMESTAMP;vf['head'].macStyle=0;vf['head'].flags |= 2
    vf['OS/2'].usWeightClass=400;vf['OS/2'].fsSelection=(vf['OS/2'].fsSelection & ~0x21)|0x40
    vf['post'].italicAngle=0
    report['derived_metadata']=recalculate_derived_metadata(vf)
    vf.recalcTimestamp=False;vf.recalcBBoxes=False
    recheck_inputs({**input_hashes,**auxiliary_hashes})
    check_input_outputs(generated,[Path(p) for p in {**input_hashes,**auxiliary_hashes}])
    output.parent.mkdir(parents=True,exist_ok=True);vf.save(output,reorderTables=True)
    if woff2:
        vf.flavor='woff2';woff2.parent.mkdir(parents=True,exist_ok=True);vf.save(woff2,reorderTables=True)
    recheck_inputs({**input_hashes,**auxiliary_hashes})
    report.update({'output':str(output),'sha256':sha256(output),'glyphs':len(vf.getGlyphOrder()),
                   'italic_mapping':{g:(g if g in shared else target) for g,target in mapping.items()},
                   'shared_default_ignorables':sorted(invisible),'shared_structural_glyphs':sorted(structural),'tables':sorted(vf.keys()),'statics_unchanged':True,
                   'feature_tags':{t:sorted({r.FeatureTag for r in vf[t].table.FeatureList.FeatureRecord}) for t in ('GSUB','GPOS') if t in vf}})
    if woff2:
        report['woff2']={'path':str(woff2),'sha256':sha256(woff2)}
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--masters',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--work-dir',required=True,type=Path)
    parser.add_argument('--woff2',type=Path)
    parser.add_argument('--report',required=True,type=Path)
    parser.add_argument('--auxiliary-manifest',type=Path,help='Optional geometry-only manifest; --masters remain authoritative.')
    parser.add_argument('--auxiliary-sha256',help='Required SHA256 of the exact auxiliary manifest bytes.')
    args=parser.parse_args()
    if args.report.resolve() in {p.resolve() for p in args.masters.glob('TorchletteSans-*.ttf')}:
        parser.error('Report must never overwrite a static input.')
    if args.report.resolve() in {args.output.resolve(), *([args.woff2.resolve()] if args.woff2 else [])}:
        parser.error('Report and font outputs must be distinct files.')
    result=build(args.masters,args.output,args.work_dir,args.woff2,args.auxiliary_manifest,args.auxiliary_sha256,args.report)
    recheck_inputs({**result['input_sha256'],**result.get('auxiliary_geometry',{}).get('input_sha256',{})})
    check_input_outputs([args.report],[Path(p) for p in {**result['input_sha256'],**result.get('auxiliary_geometry',{}).get('input_sha256',{})}])
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('output','sha256','glyphs','source_glyphs','statics_unchanged')},indent=2))


if __name__=='__main__':
    main()

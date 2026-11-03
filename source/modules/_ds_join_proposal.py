# Source component: analytic_boundary.py
"""Exact source-boundary splice primitives; no sampling or font construction.

A rail is a line/quadratic/cubic Bezier, represented by its original controls.
Conversions and trims are exact polynomial operations. bridge() is the separately
reviewed three-cubic C2 jet construction; callers must still reject loops or ink
collisions after the complete proposed contour is assembled.
"""
from math import hypot

def lerp(a,b,t):return tuple((1-t)*x+t*y for x,y in zip(a,b))
def split(points,t):
    rows=[tuple(points)]
    while len(rows[-1])>1:rows.append(tuple(lerp(a,b,t) for a,b in zip(rows[-1],rows[-1][1:])))
    return tuple(row[0] for row in rows),tuple(row[-1] for row in rows[::-1])
def trim(points,lo,hi):
    if not 0<=lo<hi<=1:raise ValueError('empty or reversed source rail trim')
    left=split(points,hi)[0]
    return split(left,lo/hi)[1] if lo else left

def cubic(points):
    if len(points)==4:return tuple(points)
    a,b=points[0],points[-1]
    if len(points)==2:return a,lerp(a,b,1/3),lerp(a,b,2/3),b
    if len(points)==3:return a,lerp(a,points[1],2/3),lerp(b,points[1],2/3),b
    raise ValueError('unsupported rail degree')

def endpoint_jet(points,end,speed):
    """Geometric C2 jet at a source endpoint, with chosen nonzero speed.

    Source tangent and signed curvature are retained. Tangential acceleration is
    zero in the local constant-speed parameter; no curvature estimate from samples.
    """
    p=cubic(points)
    if end:
        at=p[3];d=tuple(3*(p[3][i]-p[2][i]) for i in (0,1));dd=tuple(6*(p[3][i]-2*p[2][i]+p[1][i]) for i in (0,1))
    else:
        at=p[0];d=tuple(3*(p[1][i]-p[0][i]) for i in (0,1));dd=tuple(6*(p[2][i]-2*p[1][i]+p[0][i]) for i in (0,1))
    norm=hypot(*d)
    if norm==0:raise ValueError('degenerate source endpoint tangent')
    tangent=tuple(x/norm for x in d);k=(d[0]*dd[1]-d[1]*dd[0])/(norm**3)
    return at,tuple(speed*x for x in tangent),(-tangent[1]*k*speed**2,tangent[0]*k*speed**2)


# Source component: c2_join.py
"""Analytic C2 bridge proposal. No path sampling, fitting, or font construction.

The endpoint jets use each retained source segment's parameter, rescaled to the
bridge's segment duration. Three cubic pieces are the minimum that can satisfy
both endpoint positions/first/second derivatives with C2 internal joins.
"""
def bridge(a, da, dda, b, db, ddb):
    def add(*vs): return tuple(map(sum, zip(*vs)))
    def mul(v,k): return tuple(x*k for x in v)
    p1=add(a,mul(da,1/3));p2=add(a,mul(da,2/3),mul(dda,1/6))
    r1=add(b,mul(db,-2/3),mul(ddb,1/6));r2=add(b,mul(db,-1/3))
    x=mul(add(mul(p2,7),mul(p1,-2),mul(r2,-1),mul(r1,2)),1/6)
    y=mul(add(r1,mul(x,4),mul(p2,-4),p1),1/2)
    q1=add(mul(x,2),mul(p2,-1));q2=add(mul(x,4),mul(p2,-4),p1)
    return [(a,p1,p2,x),(x,q1,q2,y),(y,r1,r2,b)]


# Source component: counter_bridge.py
"""Private counter-boundary construction. No font/glyph-specific coordinates.

Only explicitly supplied counter-contour regions are eligible. Outer contour and
all other rails remain exact. A source rail is never sampled into a replacement
polygon: exact Bezier trims and analytic endpoint jets feed three cubic pieces.
"""
from math import hypot,acos
from fontTools.misc.bezierTools import calcCubicArcLength
from fontTools.pens.basePen import decomposeQuadraticSegment
import pathops

def curves(path):
    cs=[];current=start=None
    for op,pts in path.segments:
        if op=='moveTo':cs.append([]);current=start=pts[0]
        elif op in ('closePath','endPath'):
            if current!=start:cs[-1].append(cubic((current,start)))
            current=start
        elif op=='lineTo':cs[-1].append(cubic((current,pts[0])));current=pts[0]
        elif op=='qCurveTo':
            for control,end in decomposeQuadraticSegment(pts):cs[-1].append(cubic((current,control,end)));current=end
        elif op=='curveTo':cs[-1].append(tuple([current,*pts]));current=pts[-1]
        else:raise ValueError('unsupported source rail '+op)
    return cs

def as_path(contours):
    out=pathops.Path();p=out.getPen()
    for c in contours:
        p.moveTo(c[0][0])
        for seg in c:p.curveTo(*seg[1:])
        p.closePath()
    return out

def length(c):return calcCubicArcLength(*c,tolerance=.001)
def at_length(c,d):
    if d<=0:return 0
    total=length(c)
    if d>=total:return 1
    lo,hi=0.,1.
    for _ in range(36):
        mid=(lo+hi)/2
        if length(trim(c,0,mid))<d:lo=mid
        else:hi=mid
    return (lo+hi)/2


def replace_corner(c,index,distance):
    # Put the construction junction between last and first, retaining orientation.
    r=c[index+1:]+c[:index+1];total=sum(map(length,r));distance=min(distance,total/8)
    i=0;d=distance
    while d>=length(r[i]):d-=length(r[i]);i+=1
    right=trim(r[i],at_length(r[i],d),1)
    j=len(r)-1;d=distance
    while d>=length(r[j]):d-=length(r[j]);j-=1
    left=trim(r[j],0,at_length(r[j],length(r[j])-d))
    if i>=j:raise ValueError('join consumes its counter contour')
    a,b=left[-1],right[0];speed=hypot(b[0]-a[0],b[1]-a[1])/2
    if speed==0:raise ValueError('coincident bridge ends')
    ja,jb=endpoint_jet(left,True,speed),endpoint_jet(right,False,speed)
    new=bridge(*ja,*jb)
    return [right,*r[i+1:j],left,*new],{'originalJunction':c[index][-1],'trimDistance':distance,'sourceLeft':left,'sourceRight':right,'bridge':new,'startJet':ja,'endJet':jb}



# Source component: semantic_bridge.py
"""Source-role selectors replacing the exploratory maximum-turn rule.

B: four bowl counters, on each side of its actual middle bar; the counter face
nearest that bar, rightmost end when the face is level. Stem counter is excluded
because it spans the middle bar. Two: the unique new white counter's bowl end.
69 binding is deliberately not supplied here until source-rail attribution is
unambiguous; do not fall back to maximum-turn selection in production.
"""
import pathops

def role_bridges(path,role,t,bar=None):
 cs=curves(path);orig=list(path.contours);areas=[abs(as_path([c]).area)for c in cs];outer=max(range(len(cs)),key=areas.__getitem__);edits={};records=[]
 if role=='two' and len(cs)!=2:raise ValueError('new two counter identity is not unique')
 for ci,c in enumerate(cs):
  if ci==outer:continue
  bounds=orig[ci].bounds
  if role=='B':
   if bounds[1]<bar<bounds[3]:continue
   if bounds[3]<=bar:index=max(range(len(c)),key=lambda i:(c[i][-1][1],c[i][-1][0]))
   elif bounds[1]>=bar:index=min(range(len(c)),key=lambda i:(c[i][-1][1],-c[i][-1][0]))
   else:raise ValueError('ambiguous B counter/bar side')
   distance=t
  elif role=='two':index=max(range(len(c)),key=lambda i:(c[i][-1][1],c[i][-1][0]));distance=t/2
  else:raise ValueError('unsupported or unresolved source role '+role)
  edits[ci],record=replace_corner(c,index,distance);record.update({'contour':ci,'role':role,'originalCounterBounds':bounds});records.append(record)
 if role=='B' and len(records)!=4:raise ValueError('B must have four distinct bowl counter/bar joints')
 out=pathops.Path()
 for ci,contour in enumerate(orig):
  if ci in edits:as_path([edits[ci]]).draw(out.getPen())
  else:contour.draw(out.getPen())
 return out,records


# Source component: two_attachment.py
"""Private analytic double-two construction, independent of serialized fonts.

Caller supplies the original source hairline factory. The inner parallel rail is
constrained to leave the original base's left edge and enter the bowl stroke's
centre. Polynomial ray intersections replace the old one-unit entrance walk.
"""
import math,pathops
from fontTools.misc.bezierTools import solveCubic

def point(c,t):
 while len(c)>1:c=[tuple((1-t)*a[i]+t*b[i]for i in(0,1))for a,b in zip(c,c[1:])]
 return c[0]
def ray_hits(path,origin,direction):
 def cross(p):return (p[0]-origin[0])*direction[1]-(p[1]-origin[1])*direction[0]
 hits=[]
 for ci,contour in enumerate(curves(path)):
  for si,c in enumerate(contour):
   v=[cross(p)for p in c];a=-v[0]+3*v[1]-3*v[2]+v[3];b=3*v[0]-6*v[1]+3*v[2];cc=3*(v[1]-v[0]);d=v[0]
   for t in solveCubic(a,b,cc,d):
    if isinstance(t,complex) or not 0<=t<=1:continue
    p=point(list(c),t);s=sum((p[i]-origin[i])*direction[i]for i in(0,1))
    hits.append({'distance':s,'point':p,'contour':ci,'segment':si,'parameter':t,'controls':c})
 return sorted(hits,key=lambda h:h['distance'])

def attached_two(factory,pb,t,g,hspans,vspans,rect,union,clip):
 def datum(x):
  L=factory(x);b=L.bounds;H=b[3];base=vspans(L,b[2]-.1*(b[2]-b[0]))[0]
  ya,yb=base[1]+.06*H,base[1]+.18*H
  a,b0=hspans(L,ya)[0],hspans(L,yb)[0];xa,xb=sum(a)/2,sum(b0)/2
  slope=(xb-xa)/(yb-ya);uy=1/math.hypot(1,slope);ux=slope*uy
  # Parallel rail normal separation t+g, with its left face at the old base edge.
  left_at_zero=xa-ya*slope-(t+g+t/2)/uy
  return L,base,(ux,uy),left_at_zero-pb[0]
 lo,hi=pb[0],(pb[0]+pb[2])/2
 dlo,dhi=datum(lo)[3],datum(hi)[3]
 if dlo*dhi>0:raise ValueError('parallel/base constraints have no source-width bracket')
 for _ in range(36):
  mid=(lo+hi)/2;dm=datum(mid)[3]
  if (dm>0)==(dlo>0):lo=mid;dlo=dm
  else:hi=mid
 x=(lo+hi)/2;L,base,direction,error=datum(x);ux,uy=direction
 foot=(pb[0]+t/(2*uy),0.)
 hits=[h for h in ray_hits(L,foot,direction)if h['point'][1]>base[1]+t]
 spans=[]
 for a,b in zip(hits,hits[1:]):
  middle=(a['distance']+b['distance'])/2;p=(foot[0]+ux*middle,foot[1]+uy*middle)
  if p[1]>pb[3]/2 and L.contains(p):spans.append((a,b,p))
 if len(spans)!=1:raise ValueError('bowl stroke centre has ambiguous analytic ray interval: '+str(len(spans)))
 enter,exit,centre=spans[0]
 q=pathops.Path();pen=q.getPen();pen.moveTo(foot);pen.lineTo(centre);pen.endPath();q.stroke(t,pathops.LineCap.BUTT_CAP,pathops.LineJoin.MITER_JOIN,20);q.simplify()
 copy=clip(q,(-3000,0,3000,pb[3]));ink=union(L,copy,rect(pb[0],0,pb[2],t))
 return ink,{'sourceHairline':L,'copy':copy,'xLeft':x,'widthConstraintResidual':error,'direction':direction,'baseFootCentre':foot,'bowlEnter':enter,'bowlExit':exit,'bowlCentre':centre,'rayHits':hits,'rawInkBounds':ink.bounds}


# Source component: side_rail_bridge.py
"""Named crescent-side Boolean junction, with no maximum-turn selection.

The source construction supplies the side inline. The completed exterior crescent is
identified by that inline (the source cut joins its two earlier pieces). Its
outer rail has exactly one certified nonparallel join. Float32 ULP bounds separate
roundoff-compatible tangent noise; ambiguity fails instead of changing branches.
This classification is construction policy, not a relaxed font acceptance gate.
"""
import math,pathops

def ulp32(x):
 if not x:return 2.0**-149
 return max(2.0**-149,2.0**(math.frexp(abs(x))[1]-24))
def tangent_interval(seg,end):
 a,b=(seg[-2],seg[-1]) if end else(seg[0],seg[1])
 d=(b[0]-a[0],b[1]-a[1]);e=tuple(4*(ulp32(a[i])+ulp32(b[i]))for i in(0,1))
 return d,e

def certified_turn(a,b):
 (ax,ay),(eax,eay)=tangent_interval(a,True);(bx,by),(ebx,eby)=tangent_interval(b,False)
 cross=ax*by-ay*bx;error=abs(ax)*eby+abs(by)*eax+eax*eby+abs(ay)*ebx+abs(bx)*eay+eay*ebx
 return abs(cross)>error,{'cross':cross,'roundoffCrossBound':error}

def rail_matches(point_,path):
 """Algebraic point-on-source-rail matches, with explicit F32 coordinate bounds.

 Solve the larger-range coordinate polynomial, then verify the other coordinate.
 This labels source provenance; it changes no font acceptance criterion.
 """
 matches=[]
 for ci,contour in enumerate(curves(path)):
  for si,c in enumerate(contour):
   axis=max((0,1),key=lambda a:max(p[a]for p in c)-min(p[a]for p in c));v=[p[axis]-point_[axis]for p in c]
   coefficients=(-v[0]+3*v[1]-3*v[2]+v[3],3*v[0]-6*v[1]+3*v[2],3*(v[1]-v[0]),v[0])
   for u in solveCubic(*coefficients):
    if isinstance(u,complex)or not 0<=u<=1:continue
    hit=point(list(c),u);distance=math.hypot(hit[0]-point_[0],hit[1]-point_[1]);bound=8*max(ulp32(x)for p in [*c,point_]for x in p)
    if distance<=bound:matches.append({'contour':ci,'segment':si,'parameter':u,'distance':distance,'coordinateBound':bound})
 return matches

def replace_transition(c,start,end,distance):
 """One connected transition arc, retaining every source vertex outside it."""
 if start==end:return replace_corner(c,start,distance)
 r=c[start+1:]+c[:start+1];n=(end-start)%len(c);span=sum(length(s)for s in r[:n]);total=sum(map(length,r));distance=min(distance,total/8)
 i=n;d=distance
 while d>=length(r[i]):d-=length(r[i]);i+=1
 right=trim(r[i],at_length(r[i],d),1)
 j=len(r)-1;d=distance
 while d>=length(r[j]):d-=length(r[j]);j-=1
 left=trim(r[j],0,at_length(r[j],length(r[j])-d))
 if i>=j:raise ValueError('source transition consumes counter contour')
 a,b=left[-1],right[0];speed=hypot(b[0]-a[0],b[1]-a[1])/2
 if not speed:raise ValueError('source transition ends coincide')
 ja,jb=endpoint_jet(left,True,speed),endpoint_jet(right,False,speed);new=bridge(*ja,*jb)
 return[right,*r[i+1:j],left,*new],{'originalJunction':c[end][-1],'originalTransitionStart':c[start][-1],'originalTransitionEnd':c[end][-1],'transitionArcLength':span,'removedSegments':r[:n],'trimDistance':distance,'sourceLeft':left,'sourceRight':right,'bridge':new,'startJet':ja,'endJet':jb}

def transition_arc(c,eligible,source_l,cut,t):
 ownership=[]
 for i in eligible:
  p=c[i][-1];a,b=rail_matches(p,source_l),rail_matches(p,cut);ownership.append({'index':i,'point':p,'L':a,'cut':b})
 switches=[r['index']for r in ownership if r['L']and r['cut']]
 if len(switches)!=1:raise ValueError('expected one source L/cut switch, found '+str(switches))
 switch=switches[0]
 # Keep inherited L junctions as explicit preservation obligations. They are
 # neither members of the Boolean replacement arc nor silently discarded data.
 inherited=[r for r in ownership if r['index']!=switch and r['L'] and not r['cut']]
 others=[r['index']for r in ownership if r['index']!=switch and r not in inherited]
 if any(not r['cut']or r['L']for r in ownership if r['index']in others):raise ValueError('unresolved additional source-rail ownership')
 def cut_only(s):
  mid=point(list(s),.5)
  return bool(rail_matches(mid,cut))and not rail_matches(mid,source_l)
 before=cut_only(c[switch]);after=cut_only(c[(switch+1)%len(c)])
 if before==after:raise ValueError('source switch has ambiguous incoming/outgoing rail ownership')
 if not others:return switch,switch,ownership
 if before:
  run=[];i=switch
  while cut_only(c[i]):
   run.append(i);i=(i-1)%len(c)
   if i==switch:raise ValueError('entire counter aliases cut rail')
  ordered=[i for i in reversed(run)if i in others]
  if set(ordered)!=set(others):raise ValueError('cut seams lie on disconnected transition arcs')
  start,end=ordered[0],switch
 else:
  run=[];i=(switch+1)%len(c)
  while cut_only(c[i]):
   run.append(i);i=(i+1)%len(c)
   if i==(switch+1)%len(c):raise ValueError('entire counter aliases cut rail')
  ordered=[i for i in run if i in others]
  if set(ordered)!=set(others):raise ValueError('cut seams lie on disconnected transition arcs')
  start,end=switch,ordered[-1]
 r=c[start+1:]+c[:start+1];extent=sum(length(s)for s in r[:(end-start)%len(c)])
 if extent>t:raise ValueError('source transition exceeds one hairline footprint; not one local join')
 return start,end,ownership


def side_rail_bridge(path,t,inline,left,source_l,cut):
 cs=curves(path);original=list(path.contours);outer=max(range(len(cs)),key=lambda i:abs(original[i].area));tol=4*ulp32(inline)
 candidates=[i for i,c in enumerate(original)if i!=outer and(c.bounds[2]<=inline+tol if left else c.bounds[0]>=inline-tol)]
 if len(candidates)!=1:raise ValueError('completed source must expose one continuous side crescent, found '+str(len(candidates)))
 target=candidates[0];c=cs[target];eligible=[];diagnostics=[]
 for i,a in enumerate(c):
  point=a[-1]
  # The crescent's top/bottom termination faces are intentional corners.
  y0,y1=original[target].bounds[1],original[target].bounds[3]
  if point[1]<=y0+4*ulp32(y0) or point[1]>=y1-4*ulp32(y1):continue
  if not(point[0]<inline-tol if left else point[0]>inline+tol):continue
  yes,why=certified_turn(a,c[(i+1)%len(c)]);diagnostics.append({'index':i,'point':point,'certified':yes,**why})
  if yes:eligible.append(i)
 if not eligible:raise ValueError('source crescent has no classified transition')
 start,end,ownership=transition_arc(c,eligible,source_l,cut,t)
 new,record=replace_transition(c,start,end,t/2)
 inherited=[]
 for own in ownership:
  if own['L'] and not own['cut']:
   i=own['index'];pair=[c[i],c[(i+1)%len(c)]]
   # Exact native polynomial controls, including original subdivision, must
   # remain adjacent after replacement. No angle threshold or cleanup waiver.
   hits=[j for j in range(len(new)) if new[j]==pair[0] and new[(j+1)%len(new)]==pair[1]]
   if len(hits)!=1:raise ValueError('replacement changes an inherited L polynomial/junction')
   inherited.append({'sourceOwnership':own,'nativeSegments':pair,'outputIndex':hits[0], 'startJet':endpoint_jet(pair[0],True,1),'endJet':endpoint_jet(pair[1],False,1)})
 record['inheritedLPreservation']=inherited;record['sourceOwnership']=ownership;record.update({'role':'continuous-left-side-crescent'if left else'continuous-right-side-crescent','counter':target,'sourceCounterBounds':original[target].bounds,'inline':inline,'cornerDiagnostics':diagnostics})
 out=pathops.Path()
 for i,contour in enumerate(original):
  if i==target:as_path([new]).draw(out.getPen())
  else:contour.draw(out.getPen())
 return out,record


def line_curve_cubic(left,right):
 """Analytic single cubic for a straight rail meeting a curved rail.

 First two controls are collinear with the straight rail: start curvature0.
 The end-tangent intersection fixes control2. End signed curvature solves the
 remaining start-handle length. Positive ordered handles ensure a nondegenerate
 convex control polygon. No samples, fit, weight-specific constants or cleanup
 tolerance changes. If the geometry is outside this class, fail explicitly.
 """
 A,u,dda=endpoint_jet(left,True,1);B,v,ddb=endpoint_jet(right,False,1)
 # The retained source rail must be structurally straight, not merely have low
 # endpoint curvature. Check all control offsets against a roundoff-only bound.
 chord=(left[-1][0]-left[0][0],left[-1][1]-left[0][1]);scale=math.hypot(*chord)
 for q in left[1:-1]:
  cross=(q[0]-left[0][0])*chord[1]-(q[1]-left[0][1])*chord[0]
  error=16*max(math.ulp(x)for p in left for x in p)*max(scale,1)
  if abs(cross)>error:raise ValueError('two bowl bridge does not start on its straight source rail')
 det=u[0]*v[1]-u[1]*v[0]
 if not det:raise ValueError('parallel tangent rays cannot define the bowl bridge')
 delta=(B[0]-A[0],B[1]-A[1]);l=(delta[0]*v[1]-delta[1]*v[0])/det;h=(u[0]*delta[1]-u[1]*delta[0])/det
 k=v[0]*ddb[1]-v[1]*ddb[0];alpha=l+1.5*k*h*h/(-det)
 if not(0<alpha<l and h>0):raise ValueError('line-to-bowl cubic has unordered or reversed tangent handles')
 C1=(A[0]+u[0]*alpha,A[1]+u[1]*alpha);C2=(A[0]+u[0]*l,A[1]+u[1]*l)
 return (A,C1,C2,B),{'alpha':alpha,'tangentIntersectionDistance':l,'endHandleDistance':h,'targetEndCurvature':k,'sourceStartTangent':u,'sourceEndTangent':v}

def two_rail_bridge(path,t,source_l,copy):
 cs=curves(path);original=list(path.contours)
 if len(cs)!=2:raise ValueError('two must expose exactly one new counter')
 outer=max(range(len(cs)),key=lambda i:abs(original[i].area));ci=1-outer;c=cs[ci];switches=[];details=[]
 for i,s in enumerate(c):
  p=s[-1]
  # Source baseline plate, not a bowl joint. Its corners remain intentional.
  if p[1]<=t+8*ulp32(t):continue
  a,b=rail_matches(p,source_l),rail_matches(p,copy)
  if a and b:switches.append(i);details.append({'index':i,'point':p,'L':a,'copy':b})
 if len(switches)!=1:raise ValueError('two bowl must have one source L/parallel-rail switch: '+str(switches))
 i=switches[0];fit=_stroke_derive(c,i,t)
 r=c[i+1:]+c[:i+1];j=fit['root']['segment'];u=fit['root']['u']
 left=trim(r[-1],0,fit['Aparameter']);right=trim(r[j],u,1)
 pieces=[right,*r[j+1:-1],left,fit['curve']]
 if pieces[1:-2]!=r[j+1:-1]:raise ValueError('stroke support changes an untouched native polynomial')
 counter=as_path([pieces]);clean=pathops.Path(counter);clean.simplify()
 outerPath=pathops.Path();original[outer].draw(outerPath.getPen())
 if len(list(clean.contours))!=1:raise ValueError('stroke support counter is not one closed simple region')
 if pathops.op(counter,outerPath,pathops.PathOp.DIFFERENCE).area!=0:raise ValueError('stroke support leaves original outer ink boundary')
 if fit['curve'][0][1]<=t:raise ValueError('stroke support enters original baseline plate')
 record={'originalJunction':c[i][-1],'sourceLeft':left,'sourceRight':right,'bridge':[fit['curve']],'sourceOwnership':details,'strokeSupport':fit,'retainedNativePieces':r[j+1:-1]}
 out=pathops.Path()
 for index,contour in enumerate(original):
  if index==ci:as_path([pieces]).draw(out.getPen())
  else:contour.draw(out.getPen())
 return out,[record]


import math
# Private stroke-support proposal: exact source polynomials; fixed physical law.
# FontTools' existing analytic cubic root utility isolates only degree<=3 signs.
from fontTools.misc.bezierTools import solveCubic as _stroke_solveCubic
class _StrokePoly:
 def __init__(self,values):
  self.c=list(values)
  while len(self.c)>1 and self.c[-1]==0:self.c.pop()
 def __call__(self,t):
  value=0.
  for a in reversed(self.c):value=value*t+a
  return value
 def deriv(self,n=1):
  p=self
  for unused in range(n):p=_StrokePoly([i*x for i,x in enumerate(p.c)][1:]or[0.])
  return p
 def __add__(self,other):
  if not isinstance(other,_StrokePoly):other=_StrokePoly([other])
  return _StrokePoly([(self.c[i]if i<len(self.c)else 0)+(other.c[i]if i<len(other.c)else 0)for i in range(max(len(self.c),len(other.c)))])
 __radd__=__add__
 def __neg__(self):return _StrokePoly([-x for x in self.c])
 def __sub__(self,other):return self+-other if isinstance(other,_StrokePoly)else self+(-other)
 def __rsub__(self,other):return -self+other
 def __mul__(self,other):
  if not isinstance(other,_StrokePoly):return _StrokePoly([other*x for x in self.c])
  out=[0.]*(len(self.c)+len(other.c)-1)
  for i,a in enumerate(self.c):
   for j,b in enumerate(other.c):out[i+j]+=a*b
  return _StrokePoly(out)
 __rmul__=__mul__
 def roots(self):
  if len(self.c)>4:raise ValueError('stroke sign polynomial exceeds analytic cubic degree')
  c=self.c+[0.]*(4-len(self.c));return _stroke_solveCubic(c[3],c[2],c[1],c[0])

def _stroke_polynomial(s,j):
 a,b,c,d=[p[j]for p in s];return _StrokePoly([a,3*(b-a),3*(a-2*b+c),-a+3*b-3*c+d])
def _stroke_eval_(s,u):return tuple(_stroke_polynomial(s,j)(u)for j in (0,1))
def _stroke_cross(a,b):return a[0]*b[1]-a[1]*b[0]
def _stroke_dot(a,b):return sum(x*y for x,y in zip(a,b))
def _stroke_geom(s,u):
 x,y=[_stroke_polynomial(s,j)for j in(0,1)];d=(x.deriv()(u),y.deriv()(u));dd=(x.deriv(2)(u),y.deriv(2)(u));v=math.hypot(*d)
 if not v:raise ValueError('zero original derivative')
 return tuple(a/v for a in d),_stroke_cross(d,dd)/v**3

def _stroke_root_intervals(s,u,J,t):
 x,y=[_stroke_polynomial(s,j)for j in(0,1)];dx,dy=x.deriv(),y.deriv();N=u[0]*(y-J[1])-u[1]*(x-J[0]);det=u[0]*dy-u[1]*dx;dp=u[0]*dx+u[1]*dy;cn=dx*y.deriv(2)-dy*x.deriv(2)
 polys={'det':det,'_stroke_dot':dp,'curvatureNumerator':cn,'lineSide':N};cuts=[0.,1.];critical=[]
 for label,p in polys.items():
  for z in p.roots():
   if abs(z.imag if isinstance(z,complex)else 0)<1e-9 and 0<float(z.real if isinstance(z,complex)else z)<1:
    q=float(z.real if isinstance(z,complex)else z);cuts.append(q);critical.append({'kind':label,'u':q,'residual':float(p(q))})
 cuts=sorted(set(cuts));roots=[];domains=[]
 def values(q):
  d=float(det(q));n=float(N(q));speed=math.hypot(float(dx(q)),float(dy(q)));h=n*speed/d if d else math.copysign(math.inf,n*d if d else -n);return h,d,float(dp(q)),float(cn(q))
 for lo,hi in zip(cuts,cuts[1:]):
  mid=(lo+hi)/2;hm,d,dpv,kv=values(mid)
  if not(d<0 and dpv<0 and kv<0 and hm>0):continue
  # On this analytic sign interval, dh/ds=1-h*k*_stroke_dot(u,v)/det>1.
  # At a boundary pole the one-sided h limit is positive infinity.
  hl=values(lo)[0];hh=values(hi)[0]
  if hl<0 or not math.isfinite(hl):hl=0 if abs(float(N(lo)))<1e-9 else hl
  if hh<0 or not math.isfinite(hh):hh=math.inf if abs(float(det(hi)))<1e-9 else hh
  domains.append({'lo':lo,'hi':hi,'hLo':hl,'hHi':hh,'signMid':{'det':d,'_stroke_dot':dpv,'curvatureNumerator':kv,'h':hm},'analyticDerivativeLowerBound':1})
  if not hl<=t<=hh:continue
  a,b=lo,hi
  for unused in range(80):
   q=(a+b)/2;h=values(q)[0]
   if h<t:a=q
   else:b=q
  q=(a+b)/2;h=values(q)[0]
  if abs(h-t)>1e-7:raise ValueError('physical root residual exceeds numeric solver bound')
  roots.append({'u':q,'h':h,'residual':h-t,'bracket':[a,b],'domain':[lo,hi]})
 return roots,domains,critical

def _stroke_derive(c,index,t):
 if not(math.isfinite(t) and t>0):raise ValueError('stroke thickness must be finite and positive')
 r=c[index+1:]+c[:index+1];J=c[index][-1];straight=r[-1];u,_=_stroke_geom(straight,1);roots=[];domains=[]
 # Only the forward original bowl before its first tangent pole is eligible.
 stop=False
 for j,s in enumerate(r[:-1]):
  rr,dd,cc=_stroke_root_intervals(s,u,J,t);domains.append({'segment':j,'domains':dd,'critical':cc});pole=[z['u']for z in cc if z['kind']=='det']
  cutoff=min(pole)if pole else 1.
  for root in rr:
   if root['u']<cutoff:roots.append({**root,'segment':j})
  # A native-piece endpoint may itself be the tangent pole.
  v,_=_stroke_geom(s,1)
  if pole or _stroke_cross(u,v)>=0:stop=True;break
 if len(roots)!=1:raise ValueError('physical support root count '+str(len(roots))+'; '+str(domains))
 root=roots[0];j,q=root['segment'],root['u'];B=_stroke_eval_(r[j],q);v,k=_stroke_geom(r[j],q);det=_stroke_cross(u,v);g=1.5*k*t*t/det;T=tuple(B[z]-t*v[z]for z in(0,1));A=tuple(T[z]-(t+g)*u[z]for z in(0,1));C1=tuple(A[z]+t*u[z]for z in(0,1));curve=(A,C1,T,B)
 if not g>0:raise ValueError('nonpositive curvature gap')
 d=tuple(straight[-1][z]-straight[0][z]for z in(0,1));ta=_stroke_dot(tuple(A[z]-straight[0][z]for z in(0,1)),d)/_stroke_dot(d,d);lineResidual=abs(_stroke_cross(tuple(A[z]-straight[0][z]for z in(0,1)),d))/math.hypot(*d)
 if not 0<ta<1:raise ValueError('support extends beyond original straight native piece')
 if lineResidual>1e-9:raise ValueError('support A not on original straight _stroke_polynomial')
 ja,ka=_stroke_geom(curve,0);jb,kb=_stroke_geom(curve,1)
 leftLength=math.hypot(J[0]-A[0],J[1]-A[1]);return {'root':root,'domains':domains,'Aparameter':ta,'lineResidual':lineResidual,'curve':curve,'t':t,'g':g,'nativeEndCurvature':k,'rootB':B,'support':{'straightDistance':leftLength,'straightInHairlines':leftLength/t,'bowlSegments':j,'bowlPartialParameter':q},'geometricJetResiduals':{'startTangent':max(abs(ja[z]-u[z])for z in(0,1)),'endTangent':max(abs(jb[z]-v[z])for z in(0,1)),'startCurvature':ka,'endCurvature':kb-k},'retainedIndices':list(range(j+1,len(r)-1)),'rootDomainMonotonicity':'Actual sign intervals k<0, det<0, _stroke_dot<0, h>0; dh/ds>1. All intervals before first pole enumerated.'}

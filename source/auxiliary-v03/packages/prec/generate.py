"""Source-parameter circular bands for the preference-or-equal design.
The shipped constructor approximates circular arcs with 24 line segments.
This companion keeps the same parameters using compatible quadratic arc bands.
It is bounded approximation and requires independent native source gates.
"""
from pathlib import Path
from copy import deepcopy
import argparse,ast,hashlib,importlib.util,json,math,subprocess,textwrap
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.cu2qu import curves_to_quadratic
p=argparse.ArgumentParser();p.add_argument('--masters',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
M=a.masters.resolve();OUT=a.out.resolve();src=a.repo/'source'
spec=importlib.util.spec_from_file_location('builder',src/'variable.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ns={'math':math,'pathops':pathops,'TransformPen':TransformPen}
for node in ast.parse((src/'build.py').read_text()).body:
 if isinstance(node,ast.FunctionDef)and node.name in['rect','poly','union','clip','transformed','mv','mirror','vspans']:
  exec(compile(ast.Module([node],type_ignores=[]),str(src/'build.py'),'exec'),ns)
raw=(src/'modules/mathnotation.py').read_text();block=textwrap.dedent(raw[raw.index("    lt = path_of('less');"):raw.index('    # ---- ML9')])
def getparams(w,ital):
 style=dict(b.WEIGHTS)[w];f=TTFont(M/f'TorchletteSans-{b.italic_style(style)if ital else style}.ttf');gl=f['glyf']
 if ital:
  for name in['less','lessequal','minus']:
   g=gl[name];g.coordinates=GlyphCoordinates([(x-.1587*(y-252),y)for x,y in g.coordinates]);g.recalcBounds(gl)
 def path_of(n):
  p=pathops.Path();gl[n].draw(p.getPen(),gl);return p
 def stroked(p,w,cap=pathops.LineCap.BUTT_CAP,join=pathops.LineJoin.MITER_JOIN,limit=4):
  q=pathops.Path(p);q.stroke(w,cap,join,limit);q.convertConicsToQuads();q.simplify();return q
 env=dict(ns);env.update(path_of=path_of,stroked=stroked,BAR=path_of('minus').bounds[3]-path_of('minus').bounds[1],put=lambda *args:None)
 exec(block,env)
 return env,f

def cubic_arc(cx,cy,r,sgn,a,z):
 # x=cx+r*sin(theta), y=cy-sgn*r*cos(theta)
 p=lambda t:(cx+r*math.sin(t),cy-sgn*r*math.cos(t))
 d=lambda t:(r*math.cos(t),sgn*r*math.sin(t))
 k=4/3*math.tan((z-a)/4);p0,p3=p(a),p(z);da,dz=d(a),d(z)
 return(p0,(p0[0]+k*da[0],p0[1]+k*da[1]),(p3[0]-k*dz[0],p3[1]-k*dz[1]),p3)

def shapes(env,ital):
 lb=env['lb'];ta=env['t_arm'];lo=env['chev_lo'];hi=env['leb'][3];yc=(lo+hi)/2;h=(hi-lo)/2-ta*.55;H=h*1.08;L=lb[2]-lb[0];R=(L*L+H*H)/(2*H);cx=lb[0]+ta*.2;baseline=-env['b3'][1]
 out=[]
 for sgn,shift in[(1,0),(-1,0),(-1,-(env['gap_le']+ta))]:
  cy=yc+sgn*R+shift+baseline;arcs=[]
  for r,direction in[(R+ta/2,1),(R-ta/2,-1)]:
   end=math.asin((lb[2]-cx)/r);angles=[end*i/8 for i in range(9)]
   if direction<0:angles.reverse()
   arcs.extend(cubic_arc(cx,cy,r,sgn,a,z)for a,z in zip(angles,angles[1:]))
  def tr(p):return(p[0]+(.1587*(p[1]-252)if ital else 0),p[1])
  # Keep arcs separate to insert explicit right and left cap lines.
  out.append([[tuple(tr(p)for p in c)for c in arcs[:8]],[tuple(tr(p)for p in c)for c in arcs[8:]]])
 return out
records=[];originals=[];auxiliaries=[]
for ital in[0,1]:
 params=[getparams(w,ital)for w,s in b.WEIGHTS];ss=[shapes(e,ital)for e,f in params];allquad=[[[None]*2 for _ in range(3)]for _ in range(7)]
 for arm in range(3):
  for side in range(2):
   for i in range(8):
    qs=curves_to_quadratic([ss[j][arm][side][i]for j in range(7)],[.35]*7)
    for j,q in enumerate(qs):
     if allquad[j][arm][side]is None:allquad[j][arm][side]=[]
     allquad[j][arm][side].append(q)
 for j,((w,style),(e,f))in enumerate(zip(b.WEIGHTS,params)):
  pen=TTGlyphPen(None)
  for arm in allquad[j]:
   pen.moveTo(arm[0][0][0])
   for q in arm[0]:pen.qCurveTo(*q[1:])
   pen.lineTo(arm[1][0][0])
   for q in arm[1]:pen.qCurveTo(*q[1:])
   pen.closePath()
  g=pen.glyph(dropImpliedOnCurves=False);cp=b.ContourPen(None);g.draw(cp,None);pen=TTGlyphPen(None)
  for contour in cp.contours:
   contour=b.reverse(contour)if b.area(contour)>0 else contour
   pen.moveTo(contour[0][0])
   for _,control,end in contour:pen.qCurveTo(control,end)
   pen.closePath()
  g=pen.glyph(dropImpliedOnCurves=False);g.flags[0]|=0x40
  style=b.italic_style(style)if ital else style
  original=(M/f'TorchletteSans-{style}.ttf').resolve();font=TTFont(original)
  glyph=deepcopy(g);font['glyf']['uni227C']=glyph;glyph.recalcBounds(font['glyf'])
  font['hmtx']['uni227C']=(font['hmtx']['uni227C'][0],glyph.xMin)
  font['head'].created=font['head'].modified=b.TIMESTAMP;font.recalcTimestamp=False
  out=OUT/f'TorchletteSans-{style}.ttf';font.save(out)
  originals.append({'weight':w,'ital':ital,'file':{'path':str(original),'sha256':H(original)}})
  auxiliaries.append({'weight':w,'ital':ital,'file':{'path':out.name,'sha256':H(out)}})
  records.append({'weight':w,'ital':ital,'quadratic_points':len(glyph.coordinates)})
sources={str(src/f):H(src/f)for f in['variable.py','build.py','modules/mathnotation.py']}
config={'glyph':'uni227C','source_sha256':sources,'construction':'Three circular arc bands, same preference source parameters from original less/lessequal/minus parts; 8 cubic sections per arc boundary; shared Cu2Qu max error0.35; original italic shear; consistent nonzero winding.','limitations':'Analytic arcs approximate the source 24-line stroke. Original-source native endpoint and intermediate gates are mandatory. No complete-family release acceptance inferred.','records':records}
config_path=OUT/'config.json';config_path.write_text(json.dumps(config,indent=2)+'\n')
source_path=OUT/'generate.py'
if source_path.resolve()!=Path(__file__).resolve():source_path.write_bytes(Path(__file__).read_bytes())
manifest={'schema':'torchlette-auxiliary-geometry','version':1,'source_mode':'Preference-or-equal source-parameter circular bands','generator':{'source':{'path':'generate.py','sha256':H(source_path)},'config':{'path':'config.json','sha256':H(config_path)},'commit':(a.repo/'SOURCE-REVISION.txt').read_text().strip()},'originals':originals,'auxiliaries':auxiliaries,'replacements':[{'glyph':'uni227C','ital':[0,1],'curve_provenance':'Upper preference arm, lower preference arm, parallel lower band; shared semantic arc section indices across seven weights.'}]}
p=OUT/'geometry.json';p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':H(p),'auxiliaries':len(auxiliaries)}))

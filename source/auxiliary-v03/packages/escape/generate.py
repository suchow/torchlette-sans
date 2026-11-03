"""Retain the Escape symbol source ring, chevron and shaft before Boolean union.
Corresponding cubic curves are converted jointly across all seven weights.
Native source endpoint and intermediate checks remain mandatory.
"""
from pathlib import Path
from copy import deepcopy
import argparse,ast,hashlib,importlib.util,json,math,subprocess,textwrap
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
p=argparse.ArgumentParser();p.add_argument('--masters',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
M=a.masters.resolve();OUT=a.out.resolve();src=a.repo/'source'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('builder',src/'variable.py');H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ns={'math':math,'pathops':pathops,'TransformPen':TransformPen}
for node in ast.parse((src/'build.py').read_text()).body:
 if isinstance(node,ast.FunctionDef)and node.name in['rect','poly','union','clip','transformed','mv','mirror','vspans']:
  exec(compile(ast.Module([node],type_ignores=[]),str(src/'build.py'),'exec'),ns)
originals=[];auxiliaries=[];records=[]
from fontTools.cu2qu import curves_to_quadratic
from fontTools.designspaceLib import DesignSpaceDocument,AxisDescriptor,SourceDescriptor
from fontTools.varLib import build
from fontTools.varLib.models import piecewiseLinearMap
from copy import deepcopy
sp=importlib.util.spec_from_file_location('fleurons',src/'modules/fleurons.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
for node in ast.parse((src/'build.py').read_text()).body:
 if isinstance(node,ast.FunctionDef)and node.name in['ellipse','diff','hspans','stroke_line']:
  exec(compile(ast.Module([node],type_ignores=[]),str(src/'build.py'),'exec'),ns)
raw=(src/'modules/codekeys.py').read_text();block=textwrap.dedent(raw[raw.index('    reach, half ='):raw.index('    # ⇥:')]);orig_union=ns['union']
for ital in[0,1]:
 families=[];refs=[]
 for w,style in b.WEIGHTS:
  f=TTFont(M/f'TorchletteSans-{b.italic_style(style)if ital else style}.ttf');refs.append(f);hf=deepcopy(f);g=hf['glyf']['H']
  if ital:g.coordinates=GlyphCoordinates([(x-.1587*(y-252),y)for x,y in g.coordinates]);g.recalcBounds(hf['glyf'])
  hp=pathops.Path();g.draw(hp.getPen(),hf['glyf']);Hb=hp.bounds;CH=Hb[3];CC=CH/2;US=ns['vspans'](hp,(Hb[0]+Hb[2])/2)[0];KS=min(US[1]-US[0],.15*CH);captured=[]
  def union(*parts):captured.extend(parts);return orig_union(*parts)
  env=dict(ns,CH=CH,CC=CC,KS=KS,union=union,place=lambda *args:None)
  exec(block,env);esc=env['esc'];dx=f['glyf']['uni238B'].xMin-esc.bounds[0];parts=[]
  assert len(captured)==3
  for part in captured:
   cs=m._contours_of(part);assert len(cs)==1
   parts.append([tuple((x+dx,y)for x,y in seg)for seg in cs[0]])
  families.append(parts)
 assert len({tuple((len(part),tuple(map(len,part)))for part in family)for family in families})==1,[[tuple(map(len,part))for part in family]for family in families]
 curves=[[[None]*len(part)for part in family]for family in families]
 for part in range(3):
  for i in range(len(families[0][part])):
   segs=[family[part][i]for family in families]
   if len(segs[0])==2:
    for j,seg in enumerate(segs):curves[j][part][i]=seg
   else:
    qs=curves_to_quadratic(segs,[.35]*7)
    for j,q in enumerate(qs):curves[j][part][i]=q
 for j,((w,style),f)in enumerate(zip(b.WEIGHTS,refs)):
  pen=TTGlyphPen(None)
  for part in curves[j]:
   pen.moveTo(part[0][0])
   for seg in part:
    if len(seg)==2:pen.lineTo(seg[-1])
    else:pen.qCurveTo(*seg[1:])
   pen.closePath()
  g=pen.glyph(dropImpliedOnCurves=False);cp=b.ContourPen(None);g.draw(cp,None);pen=TTGlyphPen(None)
  for c in cp.contours:
   c=b.reverse(c)if b.area(c)>0 else c;pen.moveTo(c[0][0])
   for _,control,end in c:pen.qCurveTo(control,end)
   pen.closePath()
  g=pen.glyph(dropImpliedOnCurves=False);g.flags[0]|=0x40
  style=b.italic_style(style)if ital else style
  original=(M/f'TorchletteSans-{style}.ttf').resolve();font=TTFont(original);glyph=deepcopy(g);font['glyf']['uni238B']=glyph;glyph.recalcBounds(font['glyf']);font['hmtx']['uni238B']=(font['hmtx']['uni238B'][0],glyph.xMin);font['head'].created=font['head'].modified=b.TIMESTAMP;font.recalcTimestamp=False;out=OUT/f'TorchletteSans-{style}.ttf';font.save(out)
  originals.append({'weight':w,'ital':ital,'file':{'path':str(original),'sha256':H(original)}});auxiliaries.append({'weight':w,'ital':ital,'file':{'path':out.name,'sha256':H(out)}});records.append({'weight':w,'ital':ital,'quadratic_points':len(glyph.coordinates)})
sources={str(src/f):H(src/f)for f in['variable.py','build.py','modules/codekeys.py','modules/fleurons.py']}
config={'glyph':'uni238B','source_sha256':sources,'construction':'Exact source CP3 Escape constructor and H measurements, preserving three pre-union source paths (ring, chevron, shaft). Corresponding cubic curves converted jointly across all seven weights with Cu2Qu max error0.35; source placement and consistent nonzero winding.','limitations':'Keeps separate source components instead of original final union/rounding/tidy. Original-source native endpoint and intermediate gates mandatory.','records':records}
config_path=OUT/'config.json';config_path.write_text(json.dumps(config,indent=2)+'\n');source_path=OUT/'generate.py'
if source_path.resolve()!=Path(__file__).resolve():source_path.write_bytes(Path(__file__).read_bytes())
manifest={'schema':'torchlette-auxiliary-geometry','version':1,'source_mode':'Escape retained ring, chevron and shaft source paths','generator':{'source':{'path':'generate.py','sha256':H(source_path)},'config':{'path':'config.json','sha256':H(config_path)},'commit':(a.repo/'SOURCE-REVISION.txt').read_text().strip()},'originals':originals,'auxiliaries':auxiliaries,'replacements':[{'glyph':'uni238B','ital':[0,1],'curve_provenance':'Ring, chevron, shaft in exact source constructor order; shared cubic section indices across all seven source weights.'}]}
p=OUT/'geometry.json';p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':H(p),'auxiliaries':len(auxiliaries)}))

"""Retain seven source Playfair hatch stroke paths with shared curve parameterization.
Each curved series uses the original offset fitter on two shared half-spans
per source cubic. This replaces adaptive per-weight subdivision and Boolean outline joins.
It is bounded approximation; native source endpoint/intermediate gates apply.
"""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,importlib.util,json,subprocess
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
p=argparse.ArgumentParser();p.add_argument('--masters',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
M=a.masters.resolve();OUT=a.out.resolve();src=a.repo/'fonts/torchlette-sans'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('builder',src/'variable.py');m=load('fleurons',src/'modules/fleurons.py');H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_hashes={str(src/f):H(src/f)for f in['variable.py','modules/fleurons.py']}
originals=[];auxiliaries=[];records=[]
from fontTools.cu2qu import curves_to_quadratic
from fontTools.designspaceLib import DesignSpaceDocument,AxisDescriptor,SourceDescriptor
from fontTools.varLib import build
from fontTools.varLib.models import piecewiseLinearMap
orig_stroke=m.stroke;orig_offset=m.offset_seg;captured=[]
def capture(subs,w,*args,**kw):captured.append((subs,w,args,kw));return orig_stroke(subs,w,*args,**kw)
def fixed_offset(s,d,ta=None,tb=None,tol=.5,depth=0):
 if len(s)==2:return orig_offset(s,d,ta,tb,tol,7)
 a,z=m.split(s,.5);tm=m.tan(s,.5)
 return orig_offset(a,d,ta,tm,tol,7)+orig_offset(z,d,tm,tb,tol,7)
m.stroke=capture
for ital in[0,1]:
 families=[];refs=[]
 for(w,style),stem in zip(b.WEIGHTS,[50,66,79,92,119,141,163]):
  f=TTFont(M/f'TorchletteSans-{b.italic_style(style)if ital else style}.ttf');refs.append(f);captured.clear();m.offset_seg=orig_offset;p=m.playfair4('hatch')(m.Style(stem/66));p.simplify();p=m.fillet(p);dx=f['glyf']['uniE90E'].xMin-p.bounds[0];m.offset_seg=fixed_offset;parts=[]
  for subs,ww,args,kw in captured:
   for segs,closed in subs:
    raw=m.stroke_sub(segs,closed,ww,*args,**kw);cs=m._contours_of(raw);assert len(cs)==1
    parts.append([tuple((x+dx,y)for x,y in seg)for seg in cs[0]])
  families.append(parts)
 assert len({tuple((len(part),tuple(map(len,part)))for part in family)for family in families})==1
 curves=[[[None]*len(part)for part in family]for family in families]
 for part in range(7):
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
  original=(M/f'TorchletteSans-{style}.ttf').resolve();font=TTFont(original)
  assert b.raw_contours(font,'uniE90E')==b.raw_contours(font,'uniE97A') and font['hmtx']['uniE90E']==font['hmtx']['uniE97A']
  for name in['uniE90E','uniE97A']:
   glyph=deepcopy(g);font['glyf'][name]=glyph;glyph.recalcBounds(font['glyf']);font['hmtx'][name]=(font['hmtx'][name][0],glyph.xMin)
  font['head'].created=font['head'].modified=b.TIMESTAMP;font.recalcTimestamp=False;out=OUT/f'TorchletteSans-{style}.ttf';font.save(out)
  originals.append({'weight':w,'ital':ital,'file':{'path':str(original),'sha256':H(original)}});auxiliaries.append({'weight':w,'ital':ital,'file':{'path':out.name,'sha256':H(out)}});records.append({'weight':w,'ital':ital,'quadratic_points':len(glyph.coordinates)})
sources={str(src/f):H(src/f)for f in['variable.py','modules/fleurons.py']}
assert sources==source_hashes,'Source files changed during geometry generation'
config={'glyphs':['uniE90E','uniE97A'],'stems':[50,66,79,92,119,141,163],'shared_source_cubic_split':0.5,'offset_fitter_terminal_depth':7,'collective_cu2qu_max_error':0.35,'source_sha256':sources,'construction':'Seven source Playfair hatch strokes: axes, two series, four hatches. Original centerlines and offset fitter; each original cubic split at t=0.5 with two fits shared across all weights. Collective Cu2Qu max error0.35; source placement; consistent nonzero winding.','limitations':'Fixed shared fitting approximates source adaptive fitting and post-union polish. Original-source native endpoint/intermediate gates mandatory.','records':records}
config_path=OUT/'config.json';config_path.write_text(json.dumps(config,indent=2)+'\n');source_path=OUT/'generate.py'
if source_path.resolve()!=Path(__file__).resolve():source_path.write_bytes(Path(__file__).read_bytes())
manifest={'schema':'torchlette-auxiliary-geometry','version':1,'source_mode':'Playfair hatch retained source stroke paths with shared fitting','generator':{'source':{'path':'generate.py','sha256':H(source_path)},'config':{'path':'config.json','sha256':H(config_path)},'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.repo,text=True).strip()},'originals':originals,'auxiliaries':auxiliaries,'replacements':[{'glyph':name,'ital':[0,1],'curve_provenance':'Axes, two series, four hatches: semantic source stroke order and shared centerline/offset half-span indices across all weights.'}for name in['uniE90E','uniE97A']]}
p=OUT/'geometry.json';p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':H(p),'auxiliaries':len(auxiliaries)}))

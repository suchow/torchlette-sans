from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
import json,hashlib,os
root=Path(__file__).resolve().parent;old=root/'aux';out=root/'aux-all-components';out.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((old/'geometry.json').read_text()); added=[('uni222C','integral',2),('uni222D','integral',3),('second','minute',2),('uni2034','minute',3),('uni2057','minute',4),('uni2036','uni2035',2),('uni2037','uni2035',3),('second.ssty.mathglyphs','minute.ssty.mathglyphs',2),('uni2034.ssty.mathglyphs','minute.ssty.mathglyphs',3)]
for a in m['auxiliaries']:
 p=(old/a['file']['path']).resolve(); f=TTFont(p,recalcBBoxes=False,recalcTimestamp=False)
 for name,source,count in added:
  if '.ssty.' in name: pitch=f['hmtx']['second.ssty.mathglyphs'][0]-f['hmtx']['minute.ssty.mathglyphs'][0]
  else: pitch=(f['hmtx'][name][0]-f['hmtx'][source][0])//(count-1)
  assert pitch>0
  pen=TTGlyphPen(None)
  for k in range(count):f['glyf'][source].draw(TransformPen(pen,(1,0,0,1,k*pitch,0)),f['glyf'])
  g=pen.glyph(dropImpliedOnCurves=False);g.flags[0]|=0x40;g.recalcBounds(f['glyf'])
  f['glyf'][name]=g
 f['maxp'].recalc(f);dest=out/p.name;f.save(dest,reorderTables=False);a['file']={'path':os.path.relpath(dest,out),'sha256':H(dest)}
for row in m['originals']:
 row['file']['path']=os.path.relpath((old/row['file']['path']).resolve(),out)
for name,source,count in added:m['replacements'].append({'glyph':name,'ital':[0,1],'curve_provenance':f'{count} independently repeated raw {source} contours at source-derived pitch; preserves overlapping nonzero winding'})
config=out/'config.json';config.write_text(json.dumps({'source_manifest':os.path.relpath(old/'geometry.json',out),'sha256':H(old/'geometry.json'),'method':'retain component paths independently for overlapping repeated marks and integrals'},indent=2)+'\n')
m['generator']={'source':{'path':os.path.relpath(Path(__file__).resolve(),out),'sha256':H(Path(__file__))},'config':{'path':os.path.relpath(config,out),'sha256':H(config)},'commit':'scratch-v04-component-correspondence'};m['source_mode']='preliminary source component geometry';p=out/'geometry.json';p.write_text(json.dumps(m,indent=2)+'\n');print(H(p))

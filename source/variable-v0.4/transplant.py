from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
import hashlib,json,copy,os
root=Path(__file__).resolve().parent; old=root/'v03'; auxdir=old/'source/auxiliary-v03/combined/auxiliaries'; out=root/'aux';out.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
oldm=json.loads((old/'source/auxiliary-v03/combined/geometry.json').read_text()); names=oldm['replacements']; rec=[]; orig=[]
styles=[(300,'Light'),(400,'Regular'),(500,'Medium'),(600,'SemiBold'),(700,'Bold'),(800,'ExtraBold'),(900,'Black')]
for w,s in styles:
 for i in (0,1):
  style=(('Italic' if s=='Regular' else s+'Italic') if i else s); name='TorchletteSans-'+style+'.ttf'
  p=root/'masters'/name; o=old/'fonts/ttf'/name; q=auxdir/name
  f=TTFont(p,recalcTimestamp=False,recalcBBoxes=False); original=TTFont(o,recalcTimestamp=False,recalcBBoxes=False); source=TTFont(q,recalcTimestamp=False,recalcBBoxes=False)
  for item in names:
   if i not in item['ital']:continue
   n=item['glyph']
   assert f['glyf'][n].compile(f['glyf'])==original['glyf'][n].compile(original['glyf']) and f['hmtx'][n]==original['hmtx'][n], (name,n,'changed original')
   idx=source.getGlyphID(n); locations=source['loca'].locations
   f['glyf'][n]=Glyph(source.reader['glyf'][locations[idx]:locations[idx+1]])
   f['hmtx'][n]=(f['hmtx'][n][0],source['hmtx'][n][1])
  f['maxp'].recalc(f);dest=out/name;f.save(dest,reorderTables=False)
  orig.append({'weight':w,'ital':i,'file':{'path':os.path.relpath(p,out),'sha256':H(p)}});rec.append({'weight':w,'ital':i,'file':{'path':os.path.relpath(dest,out),'sha256':H(dest)}})
config=out/'config.json';config.write_text(json.dumps({'old_manifest':os.path.relpath(old/'source/auxiliary-v03/combined/geometry.json',out),'sha256':H(old/'source/auxiliary-v03/combined/geometry.json'),'method':'transplant only selected raw outlines from old auxiliaries after verifying identical original outlines and metrics'},indent=2)+'\n')
m={'schema':'torchlette-auxiliary-geometry','version':1,'source_mode':'preliminary transplant from verified v0.3 auxiliary geometry','generator':{'source':{'path':os.path.relpath(Path(__file__).resolve(),out),'sha256':H(Path(__file__))},'config':{'path':os.path.relpath(config,out),'sha256':H(config)},'commit':'scratch-preflight-v04'},'originals':orig,'auxiliaries':rec,'replacements':names}; path=out/'geometry.json';path.write_text(json.dumps(m,indent=2)+'\n');print(H(path))

"""Reconstruct combined auxiliaries from packaged raw candidates, never a VF."""
from pathlib import Path
import argparse,hashlib,json,importlib.util,copy,os
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();assert not out.exists(),'Output must not already exist'
A=Path(__file__).resolve().parent;R=A.parents[1];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('builder',R/'source/variable.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);paths={};fonts={}
for w,s in b.WEIGHTS:
 for i in [0,1]:
  f=R/'fonts/ttf'/('TorchletteSans-'+(b.italic_style(s)if i else s)+'.ttf');paths[w,i]=f;fonts[w,i]=TTFont(f,recalcTimestamp=False,recalcBBoxes=False);fonts[w,i]._input_sha256=H(f)
selections={};replacement=[];packages=json.loads((A/'packages.json').read_text())['packages'];inputs={}
for row in packages:
 m=A/row['manifest'];assert H(m)==row['sha256'];aux,sel,hh,rr=b.auxiliary_geometry(m,H(m),paths,fonts,[]);inputs.update(hh)
 for n,ital in sel.items():assert n not in selections;selections[n]=(aux,ital)
 replacement.extend(json.loads(m.read_text())['replacements'])
assert len(selections)==10;out.mkdir(parents=True);rows=[]
for loc,p in paths.items():
 f=TTFont(p,recalcTimestamp=False,recalcBBoxes=False)
 for n,(aux,ital)in selections.items():
  if loc[1]not in ital:continue
  src=aux[loc];idx=src.getGlyphID(n);lo=src['loca'].locations;f['glyf'][n]=Glyph(src.reader['glyf'][lo[idx]:lo[idx+1]]);f['hmtx'][n]=(f['hmtx'][n][0],src['hmtx'][n][1])
 f['maxp'].recalc(f);dest=out/p.name;f.save(dest,reorderTables=False)
 expected=A/'combined/auxiliaries'/p.name;assert H(dest)==H(expected),('Combined bytes changed',p.name)
 rows.append({'weight':loc[0],'ital':loc[1],'file':{'path':p.name,'sha256':H(dest)}})
config={'source_package_inventory':os.path.relpath(A/'packages.json',out),'sha256':H(A/'packages.json'),'policy':'Preserve package selected LSB/frame and original advances; original masters supply target metrics.'};(out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
m={'schema':'torchlette-auxiliary-geometry','version':1,'source_mode':'Reconstructed portable package raw auxiliaries; byte-exact against packaged combined inputs','generator':{'source':{'path':os.path.relpath(__file__,out),'sha256':H(__file__)},'config':{'path':'config.json','sha256':H(out/'config.json')},'commit':(R/'SOURCE-REVISION.txt').read_text().strip()},'originals':[{'weight':w,'ital':i,'file':{'path':os.path.relpath(p,out),'sha256':H(p)}}for(w,i),p in paths.items()],'auxiliaries':rows,'replacements':replacement}
(out/'geometry.json').write_text(json.dumps(m,indent=2)+'\n');b.auxiliary_geometry(out/'geometry.json',H(out/'geometry.json'),paths,fonts,[])
for p,h in inputs.items():assert H(p)==h
print('Fourteen auxiliary bytes match packaged originals; no VF generated.',H(out/'geometry.json'))

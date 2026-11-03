"""Read-only intake + package/raw/imported-geometry validation. No VF build."""
from pathlib import Path
import hashlib,json,importlib.util,copy,argparse
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);args=p.parse_args()
A=Path(__file__).resolve().parent;R=A.parents[1];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('builder',R/'source/variable.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
from fontTools.ttLib import TTFont
paths={};fonts={}
for w,s in b.WEIGHTS:
 for i in [0,1]:
  f=R/'fonts/ttf'/('TorchletteSans-'+(b.italic_style(s)if i else s)+'.ttf');paths[w,i]=f;fonts[w,i]=TTFont(f,recalcBBoxes=False,recalcTimestamp=False);fonts[w,i]._input_sha256=H(f)
m=A/'combined/geometry.json';aux,selected,hashes,intake=b.auxiliary_geometry(m,H(m),paths,fonts,[]);package_sources={};inventory=json.loads((A/'packages.json').read_text());package_reports=[]
for row in inventory['packages']:
 mp=A/row['manifest'];assert H(mp)==row['sha256'];aa,ss,hh,rr=b.auxiliary_geometry(mp,H(mp),paths,fonts,[]);hashes.update(hh);package_reports.append(rr)
 for n,slants in ss.items():
  assert n not in package_sources;package_sources[n]=(aa,slants)
assert set(package_sources)==set(selected)and len(selected)==10

def raw(f,n):
 i=f.getGlyphID(n);loc=f['loca'].locations;return f.reader['glyf'][loc[i]:loc[i+1]]
def signature(g):return(g.numberOfContours,tuple(g.coordinates),tuple(g.flags),tuple(g.endPtsOfContours),getattr(g,'xMin',None),getattr(g,'xMax',None),getattr(g,'yMin',None),getattr(g,'yMax',None))
def imported(f,n):
 g=copy.deepcopy(f['glyf'][n]);shift=g.xMin-f['hmtx'][n][1];g.removeHinting()
 if shift:g.coordinates.translate((-shift,0));g.xMin-=shift;g.xMax-=shift
 return g,shift
rows=[]
for loc,f in aux.items():
 original=fonts[loc];chosen={n for n,sl in selected.items()if loc[1]in sl};assert f.getGlyphOrder()==original.getGlyphOrder()
 for n in original.getGlyphOrder():
  if n not in chosen:assert raw(f,n)==raw(original,n)and f['hmtx'][n]==original['hmtx'][n],(loc,n)
  assert f['hmtx'][n][0]==original['hmtx'][n][0]
 for n in sorted(chosen):
  pkg=package_sources[n][0][loc];g,shift=imported(f,n);pg,pshift=imported(pkg,n);assert signature(f['glyf'][n])==signature(pkg['glyf'][n]);assert f['glyf'][n].program.getBytecode()==pkg['glyf'][n].program.getBytecode();assert signature(g)==signature(pg)and shift==pshift
  assert f['hmtx'][n][1]==pkg['hmtx'][n][1]
  target=copy.deepcopy(original);metrics=copy.deepcopy(target['hmtx'].metrics);target['glyf'][n]=g;assert target['hmtx'].metrics==metrics
  rows.append({'weight':loc[0],'ital':loc[1],'glyph':n,'raw_exact':True,'post_rebase_exact':True,'shift':shift,'original_target_metrics_retained':True})
for file,h in hashes.items():assert H(file)==h
args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps({'scope':'Portable manifest intake and140raw/imported correspondence checks only; no VF build or source reconstruction','manifest_sha256':H(m),'builder_sha256':H(R/'source/variable.py'),'rows':rows,'all_nonselected_raw_glyf_metrics_exact':True,'all_original_advances_retained':True,'package_intake_count':len(package_reports),'combined_intake':intake,'input_hashes':hashes,'passed':True},indent=2)+'\n');print('PASS',len(rows),'selected glyph/style checks')

from pathlib import Path
from fontTools.ttLib import TTFont
import json,hashlib,copy
R=Path(__file__).parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((R/'geometry.json').read_text());c=json.loads((R/'config.json').read_text());proof=json.loads((R/'proof.json').read_text())
for p,h in proof['inputs'].items():assert H(p)==h
orig={(r['weight'],r['ital']):r['file'] for r in m['originals']}
rows=[]
def bytesglyph(f,n):
 i=f.getGlyphID(n);l=f['loca'].locations;return f.reader['glyf'][l[i]:l[i+1]]
def points(f,n):
 g=f['glyf'][n];return (g.numberOfContours,tuple(g.coordinates),tuple(g.flags),tuple(g.endPtsOfContours),g.program.getBytecode())
for row in m['auxiliaries']:
 loc=(row['weight'],row['ital']);p=R/row['file']['path'];assert H(p)==row['file']['sha256'];o=orig[loc];assert H(o['path'])==o['sha256'];a=TTFont(o['path'],recalcTimestamp=False,recalcBBoxes=False);z=TTFont(p,recalcTimestamp=False,recalcBBoxes=False);selected=set();sources={}
 for name,info in c['selections'].items():
  if loc[1]not in info['ital']:continue
  package=Path(info['package']);pm=json.loads((package/'geometry.json').read_text());r=next(r for r in pm['auxiliaries']if(r['weight'],r['ital'])==loc);pp=package/r['file']['path'];assert H(pp)==r['file']['sha256'];f=TTFont(pp,recalcTimestamp=False,recalcBBoxes=False);assert points(z,name)==points(f,name)
  def imported(font):
   g=copy.deepcopy(font['glyf'][name]);shift=g.xMin-font['hmtx'][name][1];g.removeHinting()
   if shift:g.coordinates.translate((-shift,0));g.xMin-=shift;g.xMax-=shift
   return (tuple(g.coordinates),tuple(g.flags),tuple(g.endPtsOfContours),g.xMin,g.xMax,g.yMin,g.yMax),shift
  actual,shift=imported(z);expected,package_shift=imported(f);assert actual==expected and shift==package_shift
  assert z['hmtx'][name]==(a['hmtx'][name][0],f['hmtx'][name][1])
  target=copy.deepcopy(a);target['glyf'][name]=copy.deepcopy(z['glyf'][name]);assert target['hmtx'].metrics==a['hmtx'].metrics
  selected.add(name);sources[name]={'file':str(pp),'sha256':H(pp),'combined_shift':shift,'package_shift':package_shift,'original_lsb':a['hmtx'][name][1],'auxiliary_lsb':z['hmtx'][name][1]}
 assert a.getGlyphOrder()==z.getGlyphOrder();assert all(a['hmtx'][n][0]==z['hmtx'][n][0] for n in a.getGlyphOrder())
 for n in a.getGlyphOrder():
  if n not in selected:assert bytesglyph(a,n)==bytesglyph(z,n) and a['hmtx'][n]==z['hmtx'][n],(loc,n)
 changes={t for t in a.keys() if t!='GlyphOrder' and a.getTableData(t)!=z.getTableData(t)};assert changes<={'glyf','loca','head','maxp','hmtx','hhea'}
 ma=a['maxp'].__dict__;mz=z['maxp'].__dict__;md={k:[ma.get(k),mz.get(k)]for k in set(ma)|set(mz)if ma.get(k)!=mz.get(k)};assert set(md)<={'maxPoints','maxContours','maxCompositePoints','maxCompositeContours','maxComponentElements','maxComponentDepth'}
 rows.append({'location':loc,'selected_count':len(selected),'nonselected_count':len(a.getGlyphOrder())-len(selected),'original_advances_and_nonselected_metrics_exact':True,'selected_importer_frame_matches_package':True,'target_metrics_retained_by_geometry_only_import':True,'selected_points_flags_endpoints_instructions_exact':True,'nonselected_raw_glyf_bytes_exact':True,'table_changes':sorted(changes),'maxp_changes':md,'source_packages':sources})
(R/'verification.json').write_text(json.dumps({'manifest_sha256':H(R/'geometry.json'),'rows':rows,'total_selected_checks':sum(x['selected_count']for x in rows),'passed':True},indent=2)+'\n')
print('Independent saved readback PASS',len(rows),'faces')

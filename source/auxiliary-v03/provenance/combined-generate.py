from pathlib import Path
import json,hashlib,copy,importlib.util,io
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
R=Path(__file__).parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def check(p,h):
 assert H(p)==h,('hash mismatch',str(p));return str(Path(p).resolve())
B=Path('/Users/jsuchow/Dropbox/Projects/torchlette/fonts/torchlette-sans/variable.py')
spec=importlib.util.spec_from_file_location('builder',B);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
roots=[Path('/tmp/torchlette-a20c8-component-aux')]+[Path('/tmp/torchlette-a20c8-vf-smallcases')/x for x in ['analytic-prec','raw-galton','raw-escape']]+[Path('/tmp/torchlette-a20c8-raw-hatch-final')]
M=Path('/tmp/torchlette-release-full22-normal/static');paths={};fonts={};inputs={str(B):H(B),str(Path(__file__)):H(__file__)}
for w,s in b.WEIGHTS:
 for i in (0,1):
  p=M/f'TorchletteSans-{b.italic_style(s) if i else s}.ttf';paths[w,i]=p;f=TTFont(p,recalcTimestamp=False,recalcBBoxes=False);f._input_sha256=H(p);fonts[w,i]=f;inputs[str(p)]=H(p)
packages=[];selections={};replacement=[]
for root in roots:
 mp=root/'geometry.json';seal=root/('sealed-proof.json' if (root/'sealed-proof.json').exists() else 'sealed-receipt.json');sd=read(seal);inputs[str(seal)]=H(seal)
 check(mp,sd.get('manifest_sha256',sd.get('manifest',{}).get('sha256')))
 if 'package_proof_sha256' in sd:
  pp=root/'package-proof.json';check(pp,sd['package_proof_sha256']);inputs[str(pp)]=H(pp)
  bound=read(pp)['files']
 else:bound=sd['files']
 for name,h in bound.items():
  p=Path(name) if Path(name).is_absolute() else root/name
  check(p,h);inputs[str(p)]=h
 aux,sel,hashes,report=b.auxiliary_geometry(mp,H(mp),paths,fonts,[]);inputs.update(hashes)
 for name,ital in sel.items():
  assert name not in selections,('duplicate',name)
  selections[name]=(len(packages),ital)
 replacement.extend(read(mp)['replacements']);packages.append({'root':str(root),'manifest':str(mp),'manifest_sha256':H(mp),'seal':str(seal),'seal_sha256':H(seal),'aux':aux,'intake':report})
assert len(selections)==10
config={'scope':'Geometry-only combined auxiliary proposal; no font constructors, VF generation or release acceptance. Existing saved-VF receipt gaps remain. Selected auxiliary LSB is copied from each source package to preserve importer rebasing; original masters remain target metric authority.','builder':{'path':str(B),'sha256':H(B)},'packages':[{k:v for k,v in p.items() if k not in ['aux','intake']}for p in packages],'selections':{n:{'package':packages[idx]['root'],'ital':sorted(ital)}for n,(idx,ital) in selections.items()}}
(R/'config.json').write_text(json.dumps(config,indent=2)+'\n')
def raw(f,n):
 idx=f.getGlyphID(n);lo=f['loca'].locations;return f.reader['glyf'][lo[idx]:lo[idx+1]]
def geom(g):return {'coords':[list(x)for x in g.coordinates],'flags':list(g.flags),'ends':list(g.endPtsOfContours),'contours':g.numberOfContours}
rows=[];arows=[]
for loc,src in paths.items():
 f=TTFont(src,recalcTimestamp=False,recalcBBoxes=False);original=TTFont(src,recalcTimestamp=False,recalcBBoxes=False);selected={n:idx for n,(idx,ital)in selections.items() if loc[1]in ital}
 for n,idx in selected.items():
  a=packages[idx]['aux'][loc];f['glyf'][n]=Glyph(raw(a,n));f['hmtx'][n]=(original['hmtx'][n][0],a['hmtx'][n][1])
 # Saving retains original metrics and tables. Geometry-dependent maxp maxima must cover replacements.
 f['maxp'].recalc(f)
 (R/'auxiliaries').mkdir(exist_ok=True);out=R/'auxiliaries'/src.name;assert not out.exists(),out;f.save(out,reorderTables=False)
 saved=TTFont(out,recalcTimestamp=False,recalcBBoxes=False)
 assert saved.getGlyphOrder()==original.getGlyphOrder()
 assert all(saved['hmtx'][n]==((original['hmtx'][n][0],packages[selected[n]]['aux'][loc]['hmtx'][n][1]) if n in selected else original['hmtx'][n]) for n in original.getGlyphOrder())
 selected_checks={n:geom(saved['glyf'][n])==geom(packages[idx]['aux'][loc]['glyf'][n])for n,idx in selected.items()};assert all(selected_checks.values())
 nonselected=[n for n in original.getGlyphOrder()if n not in selected]
 assert all(raw(saved,n)==raw(original,n)for n in nonselected),('nonselected bytes',loc)
 changed={tag for tag in original.keys()if tag!='GlyphOrder' and original.getTableData(tag)!=saved.getTableData(tag)}
 assert changed <= {'glyf','loca','head','maxp','hmtx','hhea'},(loc,changed)
 hd=copy.deepcopy(original['head'].__dict__);hs=copy.deepcopy(saved['head'].__dict__)
 for x in ['checkSumAdjustment','indexToLocFormat','xMin','xMax','yMin','yMax']:hd.pop(x,None);hs.pop(x,None)
 assert (hd.pop('flags') ^ hs.pop('flags')) & ~2 == 0, ('unexpected head flags',loc)
 assert hd==hs,('head metadata',loc)
 rows.append({'weight':loc[0],'ital':loc[1],'selected_exact':selected_checks,'nonselected_raw_glyf_exact_count':len(nonselected),'original_advances_and_nonselected_hmtx_exact':True,'selected_lsb_matches_package':True,'head_flags_before_after':[original['head'].flags,saved['head'].flags],'changed_tables':sorted(changed),'source_sha256':H(src),'output_sha256':H(out)})
 arows.append({'weight':loc[0],'ital':loc[1],'file':{'path':str(out.relative_to(R)),'sha256':H(out)}})
manifest={'schema':'torchlette-auxiliary-geometry','version':1,'source_mode':'Union of ten explicitly selected sealed raw-source auxiliary glyphs; original target layout and metrics authoritative; selected auxiliary LSB preserves source frame','generator':{'source':{'path':'generate.py','sha256':H(__file__)},'config':{'path':'config.json','sha256':H(R/'config.json')},'commit':'private-combination-of-sealed-packages'},'originals':[{'weight':w,'ital':i,'file':{'path':str(p.resolve()),'sha256':H(p)}}for (w,i),p in paths.items()],'auxiliaries':arows,'replacements':replacement}
mp=R/'geometry.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
aux,sel,hashes,report=b.auxiliary_geometry(mp,H(mp),paths,fonts,[])
for p,h in inputs.items():check(p,h)
proof={'scope':config['scope'],'manifest_sha256':H(mp),'inputs':inputs,'rows':rows,'actual_builder_intake':report,'limitations':['No constructor or variable-font build. No inherited saved-VF acceptance. Geometry-dependent glyf/loca/maxp/head serialization may change; original advances and nonselected metrics retained; selected auxiliary LSB preserves source-package importer frame. Actual builder retains original target metrics.']}
(R/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('PASS',len(rows),'faces',len(sel),'selections',H(mp))

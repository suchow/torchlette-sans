"""Rebind immutable shipped combined auxiliary inputs; does not generate fonts."""
from pathlib import Path
import hashlib,json,os
A=Path(__file__).resolve().parent;C=A/'combined';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();c=json.loads((C/'config.json').read_text())
assert H(C/c['builder'])==c['builder_sha256'];assert H(C/c['package_inventory'])==c['package_inventory_sha256']
for k in ['originals','auxiliaries']:
 assert len(c[k])==14
 for r in c[k]:
  assert not Path(r['file']['path']).is_absolute();assert H(C/r['file']['path'])==r['file']['sha256']
m={'schema':'torchlette-auxiliary-geometry','version':1,'source_mode':'Portable binding of ten sealed v2 raw-geometry replacements; original masters remain metric/layout authority','generator':{'source':{'path':'../prepare_manifest.py','sha256':H(__file__)},'config':{'path':'config.json','sha256':H(C/'config.json')},'commit':(A.parents[1]/'SOURCE-REVISION.txt').read_text().strip()},'originals':c['originals'],'auxiliaries':c['auxiliaries'],'replacements':c['replacements']}
(C/'geometry.json').write_text(json.dumps(m,indent=2)+'\n');(C/'geometry.sha256').write_text(H(C/'geometry.json')+'\n');print(H(C/'geometry.json'))

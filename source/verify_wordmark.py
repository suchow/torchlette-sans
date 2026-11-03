"""Focused T03-K120 constructor check. FONT STYLE --original MATCHED_FONT.
No claim on a full-family/VF, hinted raster or subjective design approval.
"""
from pathlib import Path
import argparse,json,hashlib,io
from fontTools.ttLib import TTFont
import uharfbuzz as hb
TARGET='T_o_r_c_h_l_e_t_t_e.ss11'
def sig(f,n):
 g=f['glyf'][n];c,e,flags=g.getCoordinates(f['glyf']);return list(c),list(e),bytes(flags),f['hmtx'][n]
def shape(raw,text,on):
 f=hb.Font(hb.Face(raw));f.scale=(f.face.upem,)*2;b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(f,b,{'ss16':int(on)})
 tt=TTFont(io.BytesIO(raw),recalcBBoxes=False);return[(tt.getGlyphOrder()[i.codepoint],i.cluster,p.x_advance,p.y_advance,p.x_offset,p.y_offset)for i,p in zip(b.glyph_infos,b.glyph_positions)]
def main():
 p=argparse.ArgumentParser();p.add_argument('font');p.add_argument('style');p.add_argument('--original',required=True);p.add_argument('--proof',required=True);a=p.parse_args();raw=Path(a.font).read_bytes();old=Path(a.original).read_bytes();f=TTFont(io.BytesIO(raw),recalcBBoxes=False);o=TTFont(io.BytesIO(old),recalcBBoxes=False);checks=[]
 def check(n,v):checks.append({'check':n,'passed':bool(v)})
 check('glyph order exact',f.getGlyphOrder()==o.getGlyphOrder());check('cmap exact',f.getBestCmap()==o.getBestCmap());check('named wordmark present',TARGET in f['glyf'])
 for n in o.getGlyphOrder():
  if n==TARGET:continue
  check('untargeted outline/metric '+n,n in f['glyf']and sig(o,n)==sig(f,n))
 check('advance tightens by exactly120',f['hmtx'][TARGET][0]==o['hmtx'][TARGET][0]-120)
 check('GSUB byte-equivalent routing',f.getTableData('GSUB')==o.getTableData('GSUB'))
 for text in ['Torchlette','Torchlette!', 'Torchlette Torchlette','xTorchlette','Torchlettex','torchlette','T o r c h l e t t e']:
  for on in [False,True]:
   x,y=shape(old,text,on),shape(raw,text,on)
   if any(r[0]==TARGET for r in x):
    check(f'wordmark names/clusters {text!r}/{on}',[(r[0],r[1])for r in x]==[(r[0],r[1])for r in y])
    check(f'wordmark120 advance {text!r}/{on}',len(x)==len(y)and all(b[2]==c[2]-(120 if b[0]==TARGET else 0)for b,c in zip(y,x)))
   else:check(f'feature off / boundary exact {text!r}/{on}',x==y)
 check('inputs stable',Path(a.font).read_bytes()==raw and Path(a.original).read_bytes()==old)
 report={'style':a.style,'candidate_sha256':hashlib.sha256(raw).hexdigest(),'original_sha256':hashlib.sha256(old).hexdigest(),'checks':checks,'passed':sum(r['passed']for r in checks),'failed':sum(not r['passed']for r in checks),'limits':['source cubicC2 proof and independent native transformed-wordmark shape/raster checks are separate','no all-context GPOS/GDEF/metadata identity claim; glyph-specific carets/anchors and geometry-derived fields need inspection']};Path(a.proof).write_text(json.dumps(report,indent=2)+'\n');print(report['passed'],report['failed']);raise SystemExit(bool(report['failed']))
if __name__=='__main__':main()

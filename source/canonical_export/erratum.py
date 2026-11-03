"""Private opt-in canonical-family erratum; see frozen POLICY.md. Not adopted."""
from pathlib import Path
from fractions import Fraction as Q
from dataclasses import dataclass, asdict
import copy, hashlib, io, json, sys
from types import SimpleNamespace
import core_exporter as core
import uharfbuzz as hb
import uharfbuzz._harfbuzz as native_runtime

SOURCE_SHA = '0a4e6f9fa86dbdde41cc935441469681a930c5a591063d6497738cb5eecdf906'
CORE_SHA = '25b836d0a9412ae6fd3e778782c8d35ad6b367872ff27ac7d3be7ad90f8ac061'
POLICY = 'canonical-source0a-MM-half-ties-cell-v1'
RUNTIME_SHA = 'bb5f9abe6f722ff11df22fe9d462fff53dd08c017358ed547c8ea0413f2b7737'
FIELDS = (('Mark1',43,0,'tildecomb.case.1',Q(151,2),76,75,705),
          ('Mark1',53,0,'uni0311.case.1',Q(151,2),76,75,705),
          ('Mark2',2,0,'gravecomb.1',Q(203,2),102,101,655),
          ('Mark2',11,0,'hookabovecomb.1',Q(157,2),79,78,655))
require = core.require

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'))
def hash_object(x): return core.digest(canonical(x).encode())
def nearest(q):
    q=Q(q);return (2*q.numerator+q.denominator)//(2*q.denominator)
def normalized(font,pins):
    """Independent serialized fixed-point oracle, vendored from saved audit."""
    result={}
    for axis in font['fvar'].axes:
        tag=axis.axisTag;u=nearest(Q(str(pins[tag]))*65536)
        lo,d,hi=[nearest(Q(str(x))*65536) for x in (axis.minValue,axis.defaultValue,axis.maxValue)]
        require(lo<=u<=hi,'Pin outside source axis')
        n=0 if u==d else nearest(Q((u-d)*65536,(hi-d) if u>d else d-lo))
        n=max(-65536,min(65536,n))
        points=[(nearest(Q(str(x))*65536),nearest(Q(str(y))*65536)) for x,y in sorted(font['avar'].segments[tag].items())]
        exact=[y for x,y in points if x==n]
        if exact:mapped=exact[0]
        else:
            left,right=next((a,b) for a,b in zip(points,points[1:]) if a[0]<n<b[0])
            ratio=nearest(Q((n-left[0])*65536,right[0]-left[0]));mapped=left[1]+nearest(Q(ratio*(right[1]-left[1]),65536))
        result[tag]=Q((max(-65536,min(65536,mapped))+2)>>2,16384)
    return result

def weight_cell(raw,font,weight):
    require(core.digest(raw)==SOURCE_SHA,'Erratum source SHA unsupported')
    require(core.digest(Path(core.__file__).read_bytes())==CORE_SHA,'Erratum core SHA unsupported')
    core.require_runtime();core.source_profile(font)
    require(core.digest(Path(native_runtime.__file__).read_bytes())==RUNTIME_SHA,'Erratum native runtime binary unsupported')
    weight=Q(str(weight));loc=normalized(font,{'wght':weight,'ital':Q(0)})
    native=hb.Font(hb.Face(raw));native.set_variations({'wght':float(weight),'ital':0.0})
    coords=dict(zip([a.axisTag for a in font['fvar'].axes],map(Q,native.get_var_coords_normalized())))
    require(loc['wght']==coords['wght'],'Independent/native weight coordinate mismatch')
    return {'rational_wght':str(loc['wght']),'native_wght':str(coords['wght']),
            'active':loc['wght']==Q(3,8),'user_weight':str(weight)}

def body(font,li=53):
    lookup=font['GPOS'].table.LookupList.Lookup[li]
    require(len(lookup.SubTable)==1,'Erratum lookup subtable priority changed')
    st=lookup.SubTable[0]
    if lookup.LookupType==9:
        require(st.ExtensionLookupType==6,'Erratum extension type changed');st=st.ExtSubTable
    else:require(lookup.LookupType==6,'Erratum lookup type changed')
    require(st.Format==1,'Erratum MarkMark format changed')
    return lookup,st

def decoded(o):
    if o is None or isinstance(o,(str,int,float,bool)):return o
    if isinstance(o,(list,tuple)):return [decoded(v) for v in o]
    if isinstance(o,dict):return {str(k):decoded(v) for k,v in o.items()}
    return {k:decoded(v) for k,v in vars(o).items() if not k.startswith('_')}

def gpos_tree(font):
    # toXML forces lazy decompilation before complete decoded comparison.
    font.saveXML(io.StringIO(),tables=['GPOS'])
    tree=decoded(font['GPOS'].table)
    for li,lookup in enumerate(font['GPOS'].table.LookupList.Lookup):
        if lookup.LookupType==9:
            row=tree['LookupList']['Lookup'][li]
            types={st.ExtensionLookupType for st in lookup.SubTable}
            require(len(types)==1,'Mixed extension types unsupported')
            row['LookupType']=next(iter(types));row['SubTable']=[decoded(st.ExtSubTable) for st in lookup.SubTable]
    return tree

def differences(a,b,path=()):
    if type(a)!=type(b):return [(path,a,b)]
    if isinstance(a,dict):
        if a.keys()!=b.keys():return [(path+('keys',),list(a),list(b))]
        return [d for k in a for d in differences(a[k],b[k],path+(k,))]
    if isinstance(a,list):
        if len(a)!=len(b):return [(path+('length',),len(a),len(b))]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,path+(i,))]
    return [] if a==b else [(path,a,b)]

def topology(font,li=53):
    lookup,st=body(font,li)
    require(lookup.LookupFlag==16 and lookup.MarkFilteringSet==3,'Erratum flags/filter changed')
    require(st.ClassCount==1 and len(st.Mark1Coverage.glyphs)==75 and len(st.Mark2Coverage.glyphs)==33,'Erratum coverage/class count changed')
    result={'flags':lookup.LookupFlag,'filter':lookup.MarkFilteringSet,'class_count':st.ClassCount,
            'mark1':list(st.Mark1Coverage.glyphs),'mark2':list(st.Mark2Coverage.glyphs),
            'classes':[r.Class for r in st.Mark1Array.MarkRecord],
            'mark1_nulls':[r.MarkAnchor is None for r in st.Mark1Array.MarkRecord],
            'mark2_nulls':[[a is None for a in r.Mark2Anchor] for r in st.Mark2Array.Mark2Record]}
    require(len(st.Mark1Array.MarkRecord)==75 and len(st.Mark2Array.Mark2Record)==33,'Erratum array lengths changed')
    return result

def anchors(font,li=53):
    _,st=body(font,li);out=[]
    for role,index,cls,name,half,old,new,y in FIELDS:
        cov=st.Mark1Coverage.glyphs if role=='Mark1' else st.Mark2Coverage.glyphs
        require(cov[index]==name,'Erratum semantic glyph/index changed')
        if role=='Mark1':
            rec=st.Mark1Array.MarkRecord[index];require(rec.Class==cls,'Erratum child class changed');a=rec.MarkAnchor
        else:a=st.Mark2Array.Mark2Record[index].Mark2Anchor[cls]
        require(a is not None,'Erratum anchor missing');out.append(a)
    return out

def source_value(font,a,loc):
    require(a.Format in (1,3),'Unsupported source anchor format')
    result=Q(a.XCoordinate);dev=getattr(a,'XDeviceTable',None)
    if dev is None:return result
    require(dev.DeltaFormat==0x8000,'Unsupported source ppem device')
    if (dev.StartSize,dev.EndSize)==(65535,65535):return result
    store=font['GDEF'].table.VarStore;data=store.VarData[dev.StartSize]
    axes=[x.axisTag for x in font['fvar'].axes]
    deltas=data.Item[dev.EndSize]
    require(len(deltas)==len(data.VarRegionIndex),'Source variation delta dimensions differ')
    # Analytic dependency proof precedes ALL scalar short circuits.
    for delta,ri in zip(deltas,data.VarRegionIndex):
        require(type(delta) is int and 0<=ri<len(store.VarRegionList.Region),'Invalid source delta/region')
        region=store.VarRegionList.Region[ri]
        require(len(region.VarRegionAxis)==len(axes),'Source region axis dimensions differ')
        for tag,r in zip(axes,region.VarRegionAxis):
            start,peak,end=[Q(str(v)) for v in (r.StartCoord,r.PeakCoord,r.EndCoord)]
            require(-1<=start<=peak<=end<=1 and not(start<0<end and peak!=0),'Unsupported source region support')
            if delta and tag=='ital':require(peak==0,'Source anchor depends on remaining italic')
    for delta,ri in zip(deltas,data.VarRegionIndex):
        if not delta:continue
        scalar=Q(1)
        for tag,r in zip(axes,store.VarRegionList.Region[ri].VarRegionAxis):
            start,peak,end=[Q(str(v)) for v in (r.StartCoord,r.PeakCoord,r.EndCoord)]
            if tag=='ital':require(peak==0,'Source anchor depends on remaining italic')
            if peak==0:continue
            x=loc[tag]
            if x==peak:continue
            if x<=start or x>=end:scalar=Q(0);break
            scalar*=((x-start)/(peak-start)) if x<peak else ((end-x)/(end-peak))
        result+=delta*scalar
    return result

def source_guard(raw):
    require(core.digest(raw)==SOURCE_SHA,'Erratum source SHA unsupported')
    font=core.load(raw);weight_cell(raw,font,650)
    require(topology(font,53)==topology(font,143),'Source alias topology differs')
    loc={'wght':Q(3,8),'ital':Q(0)}
    for li in (53,143):
        for a,field in zip(anchors(font,li),FIELDS):
            require(source_value(font,a,loc)==field[4],'Source half-tie preimage differs')
            # Guard Y remaining-axis dependency as well as X.
            proxy=copy.copy(a);proxy.XCoordinate=a.YCoordinate;proxy.XDeviceTable=getattr(a,'YDeviceTable',None)
            require(source_value(font,proxy,loc)==field[7],'Source Y preimage differs')
    return {'topology':topology(font),'glyph_order':font.getGlyphOrder()}

def validate_state(font,profile,state):
    require(font.getGlyphOrder()==profile['glyph_order'],'Erratum glyph order changed')
    require(topology(font)==profile['topology'],'Erratum complete topology changed')
    require(state in ('old','new'),'Unknown trusted anchor state')
    for a,field in zip(anchors(font),FIELDS):
        require(a.Format==1,'Erratum target anchor format changed')
        require(set(vars(a))=={'Format','XCoordinate','YCoordinate'},'Erratum target anchor payload changed')
        require(a.YCoordinate==field[7] and a.XCoordinate==field[5 if state=='old' else 6],
                'Erratum all-four '+state+' payload required; mixed/unknown/untrusted new rejects')

def apply_phase(raw,profile,action):
    """Atomic byte-level phase. Only 'apply' or trusted 'inherit' accepted.
    The caller must establish inherited receipt trust before requesting inherit.
    """
    require(action in ('apply','inherit'),'Invalid erratum phase action')
    font=core.load(raw);validate_state(font,profile,'old' if action=='apply' else 'new')
    before=gpos_tree(font)
    if action=='apply':
        # Deep-copy the complete mutable lookup owner chain; each logical anchor
        # is additionally copied independently to avoid aliases within MarkMark.
        root=font['GPOS'].table;root.LookupList=copy.copy(root.LookupList);root.LookupList.Lookup=list(root.LookupList.Lookup)
        root.LookupList.Lookup[53]=copy.deepcopy(root.LookupList.Lookup[53])
        _,st=body(font)
        for rec in st.Mark1Array.MarkRecord:rec.MarkAnchor=copy.deepcopy(rec.MarkAnchor)
        for rec in st.Mark2Array.Mark2Record:rec.Mark2Anchor=[copy.deepcopy(a) for a in rec.Mark2Anchor]
        for a,field in zip(anchors(font),FIELDS):a.XCoordinate=field[6]
        out=core.serialize(font)
    else:out=raw
    reopened=core.load(out);validate_state(reopened,profile,'new')
    changes=differences(before,gpos_tree(reopened))
    expected=[]
    if action=='apply':
        for role,index,cls,name,half,old,new,y in FIELDS:
            suffix=('Mark1Array','MarkRecord',index,'MarkAnchor','XCoordinate') if role=='Mark1' else ('Mark2Array','Mark2Record',index,'Mark2Anchor',cls,'XCoordinate')
            expected.append((('LookupList','Lookup',53,'SubTable',0)+suffix,old,new))
    require(changes==expected,'Erratum decoded GPOS changes exceed exact four fields')
    core.same_other_tables(core.load(raw),reopened,{'GPOS'})
    return out,{'action':action,'before_sha256':core.digest(raw),'after_sha256':core.digest(out),
                'GPOS_before':core.digest(core.load(raw).getTableData('GPOS')),
                'GPOS_after':core.digest(reopened.getTableData('GPOS')),
                'decoded_changes':[(list(p),a,b) for p,a,b in changes],
                'non_GPOS_raw_unchanged_except_head_checksum':True}

@dataclass(frozen=True)
class Receipt(core.Receipt):
    policy_id:str
    state_json:str
    state_sha256:str

class Exporter(core.Exporter):
    def __setattr__(self,name,value):
        if name in ('erratum_enabled','_erratum_enabled') and hasattr(self,'_erratum_enabled'):
            raise AttributeError('Constructor policy mode is immutable')
        super().__setattr__(name,value)

    @property
    def erratum_enabled(self):return self._erratum_enabled

    def __init__(self,raw,expected_sha,canonical_mm_erratum=False):
        require(type(canonical_mm_erratum) is bool,'Policy mode must be boolean')
        self._erratum_enabled=canonical_mm_erratum
        self.erratum_audit=[];self._ledger={}
        if canonical_mm_erratum:
            require(expected_sha==SOURCE_SHA and core.digest(raw)==SOURCE_SHA,'Erratum source unsupported')
            require(core.digest(Path(core.__file__).read_bytes())==CORE_SHA,'Erratum core unsupported')
        super().__init__(raw,expected_sha)
        self.profile=source_guard(raw) if canonical_mm_erratum else None

    def partial(self,axis,value,path,order):
        if not self.erratum_enabled:return super().partial(axis,value,path,order)
        value=core.coordinate(value,axis);path=Path(path)
        require(not path.exists() and not path.is_symlink(),'Output already exists')
        cell=weight_cell(self.raw,self.source(),value) if axis=='wght' else None
        mathpath=path.with_name('math-'+path.name)
        original,font=super().partial(axis,value,mathpath,order)
        raw=mathpath.read_bytes();status='deferred' if cell is None else ('applied' if cell['active'] else 'outside-cell')
        phase=None
        if status=='applied':raw,phase=apply_phase(raw,self.profile,'apply')
        # No-change paths retain literal core bytes.
        with path.open('xb') as f:f.write(raw)
        state={'policy':POLICY,'enabled':True,'source_sha256':self.sha,'status':status,
               'cell':cell,'partial_sha256':core.digest(raw),'partial_GPOS_sha256':core.digest(core.load(raw).getTableData('GPOS')),
               'runtime_binary_sha256':RUNTIME_SHA,'field_policy':[[str(v) if isinstance(v,Q) else v for v in field] for field in FIELDS],
               'topology_sha256':hash_object(self.profile['topology']),'math_baseline':str(mathpath),
               'math_baseline_sha256':original.partial_sha256,'phase':phase}
        state_json=canonical(state)
        receipt=Receipt(original.source_sha256,str(path.resolve()),core.digest(raw),original.first_axis,
                        original.first_value,original.remaining_axis,original.order,POLICY,state_json,hash_object(state))
        del self.receipts[original.partial_sha256]
        self.receipts[receipt.partial_sha256]=receipt;self._ledger[receipt.partial_sha256]=receipt
        self.erratum_audit.append(state)
        return receipt,core.load(raw)

    def complete(self,receipt,second_axis,value,path):
        if not self.erratum_enabled:
            require(not isinstance(receipt,Receipt),'Enabled receipt cannot enter disabled mode')
            return super().complete(receipt,second_axis,value,path)
        require(isinstance(receipt,Receipt) and receipt.policy_id==POLICY,'Erratum receipt mode/policy mismatch')
        require(self._ledger.get(receipt.partial_sha256) is receipt,'Erratum receipt not trusted by this exporter')
        state=json.loads(receipt.state_json)
        require(hash_object(state)==receipt.state_sha256,'Erratum receipt state changed')
        require(state['enabled'] is True and state['policy']==POLICY and state['source_sha256']==self.sha,'Erratum state mode/source mismatch')
        actual=Path(receipt.partial_path).read_bytes()
        require(core.digest(actual)==receipt.partial_sha256==state['partial_sha256'],'Actual corrected partial changed')
        require(core.digest(core.load(actual).getTableData('GPOS'))==state['partial_GPOS_sha256'],'Partial GPOS changed')
        if state['status']=='applied':validate_state(core.load(actual),self.profile,'new')
        pins={receipt.first_axis:Q(receipt.first_value),second_axis:core.coordinate(value,second_axis)}
        cell=weight_cell(self.raw,self.source(),pins['wght'])
        require((state['status']=='applied')==bool(state['cell'] and state['cell']['active']),'Partial application state inconsistent')
        path=Path(path);require(not path.exists() and not path.is_symlink(),'Output already exists')
        mathpath=path.with_name('math-'+path.name)
        super().complete(receipt,second_axis,value,mathpath)
        raw=mathpath.read_bytes();phase=None
        if state['status']=='applied':
            require(cell['active'],'Inherited active cell changed');raw,phase=apply_phase(raw,self.profile,'inherit')
        elif cell['active']:raw,phase=apply_phase(raw,self.profile,'apply')
        with path.open('xb') as f:f.write(raw)
        self.erratum_audit.append({'policy':POLICY,'cell':cell,'actual_partial':receipt.partial_path,
             'partial_sha256':receipt.partial_sha256,'math_baseline':str(mathpath),'math_baseline_sha256':core.digest(mathpath.read_bytes()),
             'phase':phase,'final_sha256':core.digest(raw),'status':'applied' if cell['active'] else 'outside-cell'})
        return core.load(raw)

"""Normal module CLI: FONT STYLE full|subset [--original MATCHED_FONT] [--proof JSON].

Standalone checks validate this font's contract, not historical source identity.
--original adds named-glyph/default-layout preservation against a matched build.
Subset feature retention follows --feature-policy (default ../web_features.txt).
"""
from pathlib import Path
import argparse,copy,io,json,sys
import pathops,uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.misc.xmlWriter import XMLWriter
from fontTools.ttLib.tables import otTables
CPS={0x25CB:'latent.graphnodes',0x25C9:'observed.graphnodes',0x25CF:'filled.graphnodes'}
APP={'ss01':1,'ss02':1,'ss16':1,'onum':1}

def xml(obj,font):
    s=io.StringIO();obj.toXML(XMLWriter(s),font);return s.getvalue()

# Frozen logical_position_lookup from signed6c7f002; no builder import/execution.
def logical_position_lookup(lookup):
    """Validate one GPOS lookup; remove only an explicit valid ExtensionPos shell."""
    classes = {1: otTables.SinglePos, 2: otTables.PairPos, 3: otTables.CursivePos,
               4: otTables.MarkBasePos, 5: otTables.MarkLigPos, 6: otTables.MarkMarkPos,
               7: otTables.ContextPos, 8: otTables.ChainContextPos}
    kind = lookup.LookupType
    if type(kind) is not int or kind not in (*classes, 9):
        raise ValueError('Unknown GPOS lookup type in logical positioning view.')
    if type(lookup.SubTableCount) is not int or lookup.SubTableCount != len(lookup.SubTable):
        raise ValueError('GPOS subtable count does not match ordered subtables.')
    effective = kind
    subtables = list(lookup.SubTable)
    if kind == 9:
        declared = []
        for sub in subtables:
            if type(sub) is not otTables.ExtensionPos:
                raise ValueError('Type-9 lookup requires ExtensionPos subtables.')
            if set(vars(sub)) != {'Format', 'ExtensionLookupType', 'ExtSubTable'}:
                raise ValueError('Unknown or missing ExtensionPos metadata; phase is unsupported.')
            if type(sub.Format) is not int or sub.Format != 1:
                raise ValueError('Only explicit ExtensionPos format 1 is supported.')
            target = sub.ExtensionLookupType
            if type(target) is not int or target not in classes:
                raise ValueError('Invalid or nested ExtensionPos effective lookup type.')
            if type(sub.ExtSubTable) is not classes[target]:
                raise ValueError('ExtensionPos declared type differs from actual underlying table.')
            declared.append(target)
        if not declared or len(set(declared)) != 1:
            raise ValueError('Mixed or empty ExtensionPos effective types are unsupported.')
        effective = declared[0]
        subtables = [sub.ExtSubTable for sub in subtables]
    elif any(type(sub) is not classes[kind] for sub in subtables):
        raise ValueError('Direct GPOS lookup type differs from actual subtable class.')
    result = copy.copy(lookup)
    result.LookupType = effective
    result.SubTable = subtables
    # All outer attributes, flags, mark-filter fields and ordered children remain.
    return result

def position_equal(original,candidate):
    """Preserve ordered logical tables; expand old class0 membership explicitly."""
    a,b=original,candidate;old=set(a.getGlyphOrder());ga,gb=a['GPOS'].table,b['GPOS'].table
    assert xml(ga.ScriptList,a)==xml(gb.ScriptList,b)
    assert xml(ga.FeatureList,a)==xml(gb.FeatureList,b)
    assert len(ga.LookupList.Lookup)==len(gb.LookupList.Lookup)
    for la,lb in zip(ga.LookupList.Lookup,gb.LookupList.Lookup):
        la,lb=logical_position_lookup(la),logical_position_lookup(lb)
        assert la.LookupType==lb.LookupType and la.LookupFlag==lb.LookupFlag
        assert getattr(la,'MarkFilteringSet',None)==getattr(lb,'MarkFilteringSet',None)
        assert len(la.SubTable)==len(lb.SubTable)
        for sa,sb in zip(la.SubTable,lb.SubTable):
            if type(sa) is otTables.PairPos and sa.Format==2:
                assert sb.Format==2 and sa.ValueFormat1==sb.ValueFormat1 and sa.ValueFormat2==sb.ValueFormat2
                ca,cb=set(sa.Coverage.glyphs),set(sb.Coverage.glyphs);assert ca==cb&old
                first,second={},{}
                for n in old:
                    if n in ca:first.setdefault(sa.ClassDef1.classDefs.get(n,0),set()).add(sb.ClassDef1.classDefs.get(n,0))
                    second.setdefault(sa.ClassDef2.classDefs.get(n,0),set()).add(sb.ClassDef2.classDefs.get(n,0))
                for x,xs in first.items():
                    for y,ys in second.items():
                        av=sa.Class1Record[x].Class2Record[y]
                        for xx in xs:
                            for yy in ys:
                                bv=sb.Class1Record[xx].Class2Record[yy]
                                for k in ['Value1','Value2']:
                                    va,vb=getattr(av,k),getattr(bv,k)
                                    assert (None if va is None else vars(va))==(None if vb is None else vars(vb))
            else:assert xml(sa,a)==xml(sb,b)
    return True

def old_gsub_equal(original,candidate,retained=True):
    """Named old feature graphs/routing; only cv82 and circle aalt additions project out."""
    a,b=original,candidate;ga,gb=a['GSUB'].table,b['GSUB'].table
    if getattr(ga,'FeatureVariations',None)is not None or getattr(gb,'FeatureVariations',None)is not None:
        raise ValueError('Variable GSUB routing is outside this static matched-font check.')
    assert ga.Version==gb.Version
    variants=set(CPS.values()) if retained else set();circles={a.getBestCmap()[cp]for cp in CPS}
    def keys(records):
        counts={};out=[]
        for r in records:
            n=counts.get(r.FeatureTag,0);counts[r.FeatureTag]=n+1;out.append((r.FeatureTag,n))
        return out
    ak,bk=keys(ga.FeatureList.FeatureRecord),keys(gb.FeatureList.FeatureRecord)
    assert [k for k in bk if k[0]!='cv82']==ak
    assert len([k for k in bk if k[0]=='cv82'])==int(retained)
    def name_value(font,index):
        values=sorted((n.platformID,n.platEncID,n.langID,bytes(n.string).hex())for n in font['name'].names if n.nameID==index)
        return ('name-records',values)if values else('unbound-nameID',index)
    types={1:otTables.SingleSubst,2:otTables.MultipleSubst,3:otTables.AlternateSubst,4:otTables.LigatureSubst,5:otTables.ContextSubst,6:otTables.ChainContextSubst,8:otTables.ReverseChainSingleSubst}
    name_fields={'FeatUILabelNameID','FeatUITooltipTextNameID','SampleTextNameID','UINameID','SubfamilyNameID'}
    def feature_terms(font,table,feature,project):
        cache={};lookups=table.LookupList.Lookup
        def freeze(value,trail):
            if value is None or isinstance(value,(str,int,float,bool)):return value
            if isinstance(value,(list,tuple)):return tuple(freeze(x,trail)for x in value)
            if isinstance(value,dict):return tuple(sorted((k,freeze(v,trail))for k,v in value.items()))
            if type(value)is otTables.SubstLookupRecord:
                return ('SubstLookupRecord',tuple((k,term(v,trail))if k=='LookupListIndex'else(k,freeze(v,trail))for k,v in sorted(vars(value).items())))
            attrs=vars(value).copy()
            if project and type(value)is otTables.SingleSubst:
                attrs['mapping']={src:dst for src,dst in value.mapping.items()if not(src in circles and dst in variants)}
            if project and type(value)is otTables.AlternateSubst:
                attrs['alternates']={src:kept for src,dsts in value.alternates.items()if(kept:=[dst for dst in dsts if not(src in circles and dst in variants)])}
            out=[]
            for k,v in sorted(attrs.items()):
                if k in name_fields:v=name_value(font,v)
                elif k=='FirstParamUILabelNameID'and getattr(value,'NumNamedParameters',0):v=tuple(name_value(font,v+i)for i in range(value.NumNamedParameters))
                else:v=freeze(v,trail)
                out.append((k,v))
            return(type(value).__name__,tuple(out))
        def term(index,trail=()):
            if index in trail:raise ValueError('Recursive GSUB lookup graph is not supported by this bounded static checker.')
            if index in cache:return cache[index]
            assert 0<=index<len(lookups);lk=lookups[index];kind=lk.LookupType;subs=list(lk.SubTable)
            assert lk.SubTableCount==len(subs)
            if kind==7:
                effective=[]
                for st in subs:
                    assert type(st)is otTables.ExtensionSubst and set(vars(st))=={'Format','ExtensionLookupType','ExtSubTable'}
                    assert st.Format==1 and st.ExtensionLookupType in types
                    assert type(st.ExtSubTable)is types[st.ExtensionLookupType];effective.append(st.ExtensionLookupType)
                assert effective and len(set(effective))==1;kind=effective[0];subs=[st.ExtSubTable for st in subs]
            else:assert kind in types and all(type(st)is types[kind]for st in subs)
            attrs=vars(lk).copy();attrs['LookupType']=kind;attrs['SubTable']=subs
            # A new aalt-only lookup may become empty after removing precisely the
            # three declared circle alternatives. Never drop other empty/context rules.
            empty=False
            if project and kind in[1,3]and lk.LookupFlag==0 and getattr(lk,'MarkFilteringSet',None)is None:
                mappings=[st.mapping if kind==1 else st.alternates for st in subs]
                actual=[(src,[dst]if kind==1 else dst)for mp in mappings for src,dst in mp.items()]
                empty=bool(actual)and all(src in circles and all(d in variants for d in dsts)for src,dsts in actual)
            value=None if empty else('Lookup',tuple((k,freeze(v,trail+(index,)))for k,v in sorted(attrs.items())))
            cache[index]=value;return value
        roots=[term(i)for i in feature.LookupListIndex];params=freeze(feature.FeatureParams,())
        return tuple(x for x in roots if x is not None),params
    bm={k:r for k,r in zip(bk,gb.FeatureList.FeatureRecord)};feature_count=0
    for k,r in zip(ak,ga.FeatureList.FeatureRecord):
        nr=bm[k];assert feature_terms(a,ga,r.Feature,False)==feature_terms(b,gb,nr.Feature,retained and k[0]=='aalt'),k;feature_count+=1
    def routes(table,featurekeys):
        def lang(ls):
            if ls is None:return None
            assert ls.FeatureCount==len(ls.FeatureIndex)
            return(ls.LookupOrder,None if ls.ReqFeatureIndex==65535 else featurekeys[ls.ReqFeatureIndex],tuple(featurekeys[i]for i in ls.FeatureIndex if featurekeys[i][0]!='cv82'))
        return tuple((r.ScriptTag,lang(r.Script.DefaultLangSys),tuple((x.LangSysTag,lang(x.LangSys))for x in r.Script.LangSysRecord))for r in table.ScriptList.ScriptRecord)
    assert routes(ga,ak)==routes(gb,bk)
    return {'old_features_compared':feature_count,'routing':'Ordered scripts/languages/required and optional old features exact','lookup_graphs':'Ordered per-feature expanded named lookup graphs and contextual references exact','allowed_projection':('Only cv82 feature/routing and aalt circle→three declared graphnodes variants' if retained else 'None; omitted policy requires unchanged old feature graphs/routing'),'limits':'Unreachable unbound lookup container ordering is not an all-text behavior claim; six actual app cases remain separately bounded.'}

def geometry(f,n):
    g=f['glyf'][n];coords,ends,flags=g.getCoordinates(f['glyf'])
    return list(coords),list(ends),list(flags)

def verify(path,style,mode,original=None,policy=None):
    f=TTFont(path,recalcBBoxes=False);o=TTFont(original,recalcBBoxes=False)if original else None
    order=f.getGlyphOrder();cmap=f.getBestCmap();gs=f.getGlyphSet();checks=[]
    def check(ok,msg):checks.append({'ok':bool(ok),'check':msg})
    def path_of(n):
        p=pathops.Path();gs[n].draw(p.getPen(glyphSet=gs));return p
    def shape(font,text,features):
        hf=hb.Font(hb.Face(Path(font.reader.file.name).read_bytes()));hb.ot_font_set_funcs(hf)
        b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(hf,b,features)
        return[(font.getGlyphName(g.codepoint),g.cluster,p.x_advance,p.y_advance,p.x_offset,p.y_offset)for g,p in zip(b.glyph_infos,b.glyph_positions)]
    tags=[r for r in f['GSUB'].table.FeatureList.FeatureRecord if r.FeatureTag=='cv82']
    retained=mode=='full'
    if mode=='subset':
        assert policy is not None,'subset mode requires an existing explicit/default feature-policy file'
        retained='cv82'in{line.split('#',1)[0].strip()for line in Path(policy).read_text().splitlines()}
    check(len(tags)==int(retained),'cv82 presence matches declared full/subset retention policy')
    if not retained:check(not(set(CPS.values())&set(order)),'omitted policy drops all graphnodes variants')
    check(len(order)==len(set(order))and f['maxp'].numGlyphs==len(order),'unique glyph order and maxp')
    check(all(cp in cmap for cp in CPS),'all three default UI circles encoded')
    if not all(cp in cmap for cp in CPS):return {'checks':checks,'baseline_compared':bool(o)}
    check(len({cmap[cp]for cp in CPS})==3,'default circles have distinct sources')
    mapping={}
    if tags:
        ft=tags[0].Feature;p=ft.FeatureParams
        check(p is not None and sorted(p.Character)==sorted(CPS),'cvParameters owns exactly the three circles')
        check(p is not None and f['name'].getDebugName(p.FeatUILabelNameID)=='Inline graphical-model nodes','cvParameters readable UI label')
        for idx in ft.LookupListIndex:
            lk=f['GSUB'].table.LookupList.Lookup[idx];check(lk.LookupType==1 and lk.LookupFlag==0,'cv82 plain single substitution')
            if lk.LookupType==1:
                for st in lk.SubTable:
                    check(not(set(mapping)&set(st.mapping)),'no duplicate cv82 source mapping');mapping.update(st.mapping)
        check(mapping=={cmap[cp]:n for cp,n in CPS.items()},'exact cv82 source-to-variant mapping')
    for cp,n in CPS.items():
        src=cmap[cp];text='x'+chr(cp)+'z';off=shape(f,text,dict(APP,cv82=0));default=shape(f,text,APP)
        check(src not in CPS.values(),'default cmap does not point at an opt-in variant')
        check(off==default and len(off)==3 and off[1][0]==src,'feature-off/default source circle and positions')
        check(all(x[0]!=order[0]for x in off),'default has no GID0')
        if o:check(off==shape(o,text,dict(APP,cv82=0)),f'U+{cp:04X} matched original named positions')
        if retained:check(n in order,'required opt-in variant present')
        if n not in order:continue
        on=shape(f,text,{'cv82':1})
        if retained:check(len(on)==3 and on[1][0]==n and all(x[0]!=order[0]for x in on),f'U+{cp:04X} actual opt-in native target')
        check(n not in cmap.values(),n+' unencoded')
        check(f['GDEF'].table.GlyphClassDef.classDefs.get(n)==1,n+' GDEF base')
        p=path_of(n);bounds=p.bounds;d=(o if o is not None else f)['OS/2'].sxHeight;minus=path_of(cmap[0x2212]).bounds;axis=(minus[1]+minus[3])/2
        check(abs((bounds[3]-bounds[1])-d)<=2,n+' x-height diameter')
        check(abs((bounds[3]+bounds[1])/2-axis)<=1,n+' math-axis centre')
        check(abs((bounds[2]-bounds[0])-d)<=2,n+' round upright picture')
        check(f['hmtx'][n][0]==d+120,n+' common advance')
        contours=list(pathops.simplify(p).contours)
        check(len(contours)=={'latent.graphnodes':2,'observed.graphnodes':3,'filled.graphnodes':1}[n],n+' actual filled boundaries')
        if n!='filled.graphnodes'and len(contours)>=2:
            boxes=sorted([c.bounds for c in contours],key=lambda b:(b[2]-b[0])*(b[3]-b[1]),reverse=True);hole=boxes[1]
            check(hole[2]-hole[0]>=.5*d,n+' nondegenerate counter')
            if n=='observed.graphnodes'and len(boxes)>=3:
                dot=boxes[2];gap=min(dot[0]-hole[0],hole[2]-dot[2],dot[1]-hole[1],hole[3]-dot[3]);check(gap>=.1*d-2,n+' open white annulus')
    if o:
        old=o.getGlyphOrder();check(all(n in order for n in old),'all original named glyphs retained')
        check(set(order)-set(old)==(set(CPS.values()) if retained else set()),'new glyph set matches declared graphnodes retention policy')
        check([(t.platformID,t.platEncID,t.format,getattr(t,'language',None),getattr(t,'cmap',None),getattr(t,'uvsDict',None))for t in f['cmap'].tables]==[(t.platformID,t.platEncID,t.format,getattr(t,'language',None),getattr(t,'cmap',None),getattr(t,'uvsDict',None))for t in o['cmap'].tables],'matched original all cmap subtables unchanged')
        check(all(n in order and geometry(f,n)==geometry(o,n)and f['hmtx'][n]==o['hmtx'][n]for n in old),'matched original decoded geometry/flags/hmtx exact')
        check(all(n in order and hasattr(f['glyf'][n],'program')and list(f['glyf'][n].program.getBytecode())==list(o['glyf'][n].program.getBytecode())for n in old if hasattr(o['glyf'][n],'program')),'matched original glyph programs exact')
        try:gsub_comparison=old_gsub_equal(o,f,retained);gsub_equal=True
        except (AssertionError,ValueError,IndexError,KeyError,AttributeError):gsub_comparison=None;gsub_equal=False
        check(gsub_equal,'matched original named GSUB feature graphs and script routing exact except declared additions')
        if 'GPOS'in o:
            try:position_equal(o,f);equal=True
            except (AssertionError,ValueError,IndexError,KeyError,AttributeError):equal=False
            check(equal,'matched original ordered logical GPOS/old-class0 pair values exact')
        if 'MATH'in o:check(xml(f['MATH'],f)==xml(o['MATH'],o),'matched original named MATH exact')
        for text in ['plain text','Il1','ά̄','x◉z ○ ●','loss != prev','[M20]']:
            check(shape(f,text,APP)==shape(o,text,APP),repr(text)+' matched original default/app named shaping')
    return {'candidate':str(path),'style':style,'mode':mode,'baseline':str(original)if original else None,'baseline_compared':bool(o),'cv82_retained_by_policy':retained,'checks':checks,'GSUB_original_comparison':gsub_comparison if o else None}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('font',type=Path);p.add_argument('style');p.add_argument('mode',choices=['full','subset']);p.add_argument('--original',type=Path);p.add_argument('--proof',type=Path);p.add_argument('--feature-policy',type=Path,default=Path(__file__).resolve().parent.parent/'web_features.txt');a=p.parse_args();r=verify(a.font,a.style,a.mode,a.original,a.feature_policy);r['passed']=sum(x['ok']for x in r['checks']);r['failed']=sum(not x['ok']for x in r['checks']);r['identity_limit']='Original UI/source preservation is assessed only when --original is supplied.'
    if a.proof:a.proof.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r));return bool(r['failed'])
if __name__=='__main__':sys.exit(main())

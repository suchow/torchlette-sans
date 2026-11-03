"""Source-aware auxiliary contours for five validated ornament constructions.

Keep semantic paths separate through source-bound clipping and quadratic matching.
This approximates post-union polish; authoritative endpoint/intermediate gates apply.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, subprocess
import freetype
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

p=argparse.ArgumentParser()
p.add_argument('--masters',type=Path,required=True)
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
b=load('builder',a.repo/'fonts/torchlette-sans/variable.py')
m=load('fleurons',a.repo/'fonts/torchlette-sans/modules/fleurons.py')
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
STEMS=[50,66,79,92,119,141,163]
constructors=[('uniE931','duck-rabbit',m.duck_rabbit),
              ('uniE97B','tape-340',m.tape4(340)),
              ('uniE97C','tape-440',m.tape4(440)),
              ('uniE978','playfair-fill',m.playfair4('fill')),
              ('uniE979','playfair-lobe',m.playfair4('lobe'))]
original_union,original_stroke=m.union,m.stroke
calls=[];split_paths={}
def capture(parts):
    calls.append(list(parts))
    return original_union(parts)
def separated_series(subs,w,cap='round',join='round'):
    result=original_stroke(subs,w,cap,join)
    if len(subs)==2:
        split_paths[id(result)]=[original_stroke([sub],w,cap,join)for sub in subs]
    return result
m.union=capture;m.stroke=separated_series
fonts={};paths={}
for weight,style in b.WEIGHTS:
    for ital in(0,1):
        file_style=b.italic_style(style)if ital else style
        path=(a.masters/f'TorchletteSans-{file_style}.ttf').resolve()
        paths[weight,ital]=path;fonts[weight,ital]=TTFont(path)
records=[]
for name,label,constructor in constructors:
    for ital in(0,1):
        groups_by_master=[]
        for (weight,_),stem in zip(b.WEIGHTS,STEMS):
            font=fonts[weight,ital];path=paths[weight,ital]
            calls.clear();split_paths.clear()
            raw=constructor(m.Style(stem/66))
            parts=calls[-1]
            union=original_union(parts)
            translation=(raw.bounds[0]-union.bounds[0],raw.bounds[1]-union.bounds[1])
            semantic=[]
            for part in parts:
                semantic.extend(split_paths.get(id(part),[part]))
            raw.simplify();polished=m.fillet(raw)
            face=freetype.Face(str(path))
            face.load_glyph(font.getGlyphID(name),freetype.FT_LOAD_NO_SCALE|freetype.FT_LOAD_NO_HINTING)
            box=face.glyph.outline.get_bbox();bbox=(box.xMin,box.yMin,box.xMax,box.yMax)
            clip=b.pathops.Path();clip.moveTo(bbox[0],bbox[1]);clip.lineTo(bbox[2],bbox[1]);clip.lineTo(bbox[2],bbox[3]);clip.lineTo(bbox[0],bbox[3]);clip.close()
            groups=[];areas=[]
            for index,part in enumerate(semantic):
                part.simplify(fix_winding=True);part=m.fillet(part)
                component=m.mv(part,translation[0]+font['glyf'][name].xMin-polished.bounds[0],translation[1])
                bounded=b.pathops.op(component,clip,b.pathops.PathOp.INTERSECTION)
                areas.append({'part_index':index,'unclipped_area':component.area,
                              'bounded_area':bounded.area,'removed_area':max(0,component.area-bounded.area)})
                pen=TTGlyphPen(None);bounded.draw(Cu2QuPen(pen,1.,reverse_direction=True))
                contour_pen=b.ContourPen(None);pen.glyph().draw(contour_pen,None)
                groups.append(contour_pen.contours)
            groups_by_master.append(groups)
            records.append({'glyph':name,'design':label,'weight':weight,'ital':ital,
                            'stem':stem,'translation':translation,'source_native_unscaled_bounds':bbox,
                            'semantic_part_count':len(groups),'parts':areas})
        count=len(groups_by_master[0]);assert all(len(g)==count for g in groups_by_master)
        aligned=[[]for _ in b.WEIGHTS]
        for group_index in range(count):
            groups=[g[group_index]for g in groups_by_master]
            if not any(groups):continue
            matched,_=b.match_contours(groups,1000)
            for contour in range(len(matched[0])):
                spans=b.subdivide([cs[contour]for cs in matched])
                for target,curves in zip(aligned,spans):target.append(curves)
        for (weight,_),curves in zip(b.WEIGHTS,aligned):
            font=fonts[weight,ital];pen=TTGlyphPen(None)
            for contour in curves:
                pen.moveTo(contour[0][0])
                for _,control,end in contour:pen.qCurveTo(control,end)
                pen.closePath()
            glyph=pen.glyph(dropImpliedOnCurves=False)
            glyph.flags[0]|=0x40
            font['glyf'][name]=glyph;glyph.recalcBounds(font['glyf'])
            # The importer ignores auxiliary metrics. Zero its auxiliary phantom
            # shift so these points retain their verified rendered coordinates.
            font['hmtx'][name]=(font['hmtx'][name][0],glyph.xMin)
        assert len({b.signature(fonts[w,ital],name)for w,_ in b.WEIGHTS})==1
originals=[];auxiliaries=[]
for weight,style in b.WEIGHTS:
    for ital in(0,1):
        font=fonts[weight,ital];file_style=b.italic_style(style)if ital else style
        font['head'].created=font['head'].modified=b.TIMESTAMP;font.recalcTimestamp=False
        out=a.out/f'TorchletteSans-{file_style}.ttf';font.save(out)
        originals.append({'weight':weight,'ital':ital,'file':{'path':str(paths[weight,ital]),'sha256':H(paths[weight,ital])}})
        auxiliaries.append({'weight':weight,'ital':ital,'file':{'path':out.name,'sha256':H(out)}})
config={'glyphs':[name for name,_,_ in constructors],'stems':STEMS,
        'source_sha256':{str(a.repo/'fonts/torchlette-sans'/file):H(a.repo/'fonts/torchlette-sans'/file)
                         for file in['variable.py','modules/fleurons.py']},
        'construction':'Ordered final source union operands; each Playfair curve-series subpath remains separate. Independent simplify/fillet; original native bounding rectangle; per-part shared quadratic subdivision.',
        'records':records,
        'limits':['Independent polish approximates the source post-union polish.','Native source bbox is a fixed construction constraint, not a fitted scale.','Hatched Playfair forms excluded: their remaining counter check fails.','Full variable-family merge and release checks remain required.']}
config_path=a.out/'config.json';config_path.write_text(json.dumps(config,indent=2)+'\n')
source_path=a.out/'generate.py'
if source_path.resolve()!=Path(__file__).resolve():source_path.write_bytes(Path(__file__).read_bytes())
manifest={'schema':'torchlette-auxiliary-geometry','version':1,
          'source_mode':'retained semantic ornament paths bounded by approved source outlines',
          'generator':{'source':{'path':'generate.py','sha256':H(source_path)},
                       'config':{'path':'config.json','sha256':H(config_path)},
                       'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.repo,text=True).strip()},
          'originals':originals,'auxiliaries':auxiliaries,
          'replacements':[{'glyph':name,'ital':[0,1],
                           'curve_provenance':label+': fixed source construction order; independent semantic-part correspondence across all seven weights.'}
                          for name,label,_ in constructors]}
path=a.out/'geometry.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'manifest':str(path),'sha256':H(path),'glyphs':config['glyphs'],'auxiliary_fonts':len(auxiliaries)}))

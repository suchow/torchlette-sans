#!/usr/bin/env python3
"""Frozen, native-size FreeType diagnostics; never a native Windows capture."""
import argparse
import ctypes as C
import hashlib
import json
import importlib.metadata
from pathlib import Path
import platform
import shutil
import sys

import freetype as ft
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw

STYLES = dict(zip(('Light','Regular','Medium','SemiBold','Bold','ExtraBold','Black'), (242,324,388,510,675,762,845)))
STYLES.update({('Italic' if s == 'Regular' else s+'Italic'): w for s,w in list(STYLES.items())})
SAMPLES = ('Il1 | Hhx nmw ft 0123456789', 'Ag Åé ñü 2 6 9 Q j y', 'gradients training output 28×28')
INK = (51,36,27)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def inventory(path):
    f = TTFont(path)
    programs = {}
    for n in f.getGlyphOrder():
        g = f['glyf'][n]  # force lazy glyph decompilation before reading instructions
        if hasattr(g, 'program'): programs[n] = len(g.program.getBytecode())
    return dict(sha256=sha(path), units_per_em=f['head'].unitsPerEm,
                glyphs=len(f.getGlyphOrder()), cmap=len(f.getBestCmap()),
                version=f['name'].getDebugName(5), family=f['name'].getDebugName(1), subfamily=f['name'].getDebugName(2),
                os2_weight=f['OS/2'].usWeightClass, italic_angle=f['post'].italicAngle,
                hint_tables={t: dict(bytes=len(f.getTableData(t)),sha256=hashlib.sha256(f.getTableData(t)).hexdigest()) for t in ('fpgm','prep','cvt ') if t in f},
                instructed_glyphs=sum(bool(n) for n in programs.values()), instruction_bytes=sum(programs.values()),
                gasp=f['gasp'].gaspRange if 'gasp' in f else {},
                maxp={k:getattr(f['maxp'],k,None) for k in ('maxSizeOfInstructions','maxStackElements','maxStorage','maxTwilightPoints')})


class Raster:
    def __init__(self, library):
        self.path=Path(library).resolve(); self.lib=C.CDLL(str(self.path)); self.h=ft.FT_Library()
        self.check(self.lib.FT_Init_FreeType(C.byref(self.h)))
        a,b,c=C.c_int(),C.c_int(),C.c_int()
        self.lib.FT_Library_Version(self.h,C.byref(a),C.byref(b),C.byref(c))
        self.version=[a.value,b.value,c.value]
        v=C.c_uint(35)
        self.check(self.lib.FT_Property_Set(self.h,b'truetype',b'interpreter-version',C.byref(v)))
        self.check(self.lib.FT_Property_Get(self.h,b'truetype',b'interpreter-version',C.byref(v)))
        if v.value != 35: raise RuntimeError('FreeType did not retain interpreter 35')
        self.filter_error=self.lib.FT_Library_SetLcdFilter(self.h,ft.FT_LCD_FILTER_DEFAULT)
        if self.filter_error: raise RuntimeError(f'LCD default filter unavailable ({self.filter_error}); cannot claim this renderer configuration')

    @staticmethod
    def check(err):
        if err: raise RuntimeError(f'FreeType error {err}')

    def render(self,path,text,size,hint,lcd):
        face=ft.FT_Face(); self.check(self.lib.FT_New_Face(self.h,str(path).encode(),0,C.byref(face)))
        try:
            self.check(self.lib.FT_Set_Pixel_Sizes(face,0,size))
            font=hb.Font(hb.Face(Path(path).read_bytes())); upem=font.face.upem; font.scale=(upem,upem)
            buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties()
            hb.shape(font,buf,{'kern':True,'liga':True,'ss16':True,'onum':True,'pnum':True})
            tt=TTFont(path); order=tt.getGlyphOrder(); metrics=tt['hmtx'].metrics
            image=Image.new('RGB',(max(360,size*len(text)),size*3),'white'); x=8.; baseline=size*2
            records=[]
            flags=ft.FT_LOAD_PEDANTIC|ft.FT_LOAD_NO_AUTOHINT|ft.FT_LOAD_NO_BITMAP|(ft.FT_LOAD_TARGET_LCD if lcd else ft.FT_LOAD_TARGET_NORMAL)
            if not hint: flags |= ft.FT_LOAD_NO_HINTING
            for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
                if info.codepoint == 0: raise RuntimeError(f'missing glyph in {path.name}: {text!r}')
                self.check(self.lib.FT_Load_Glyph(face,info.codepoint,flags))
                slot=face.contents.glyph.contents
                advance=slot.advance.x/64
                self.check(self.lib.FT_Render_Glyph(face.contents.glyph,ft.FT_RENDER_MODE_LCD if lcd else ft.FT_RENDER_MODE_NORMAL))
                slot=face.contents.glyph.contents; b=slot.bitmap; channels=3 if lcd else 1
                if b.pixel_mode != (ft.FT_PIXEL_MODE_LCD if lcd else ft.FT_PIXEL_MODE_GRAY):
                    if b.width and b.rows: raise RuntimeError(f'unexpected pixel mode {b.pixel_mode}')
                width=b.width//channels
                left=round(x+pos.x_offset*size/upem)+slot.bitmap_left
                top=round(baseline-pos.y_offset*size/upem)-slot.bitmap_top
                raw=C.string_at(b.buffer,abs(b.pitch)*b.rows) if b.rows else b''
                for row in range(b.rows):
                    offset=(row if b.pitch>=0 else b.rows-1-row)*abs(b.pitch)
                    for col in range(width):
                        coverage=[raw[offset+col*channels+k] for k in range(channels)]
                        if channels==1: coverage*=3
                        px=(left+col,top+row)
                        if not (0<=px[0]<image.width and 0<=px[1]<image.height):
                            if any(coverage): raise RuntimeError('ink clipped by diagnostic canvas')
                            continue
                        old=image.getpixel(px)
                        image.putpixel(px,tuple(round(old[k]*(1-coverage[k]/255)+INK[k]*coverage[k]/255) for k in range(3)))
                records.append(dict(gid=info.codepoint,advance=advance,bearing=[slot.bitmap_left,slot.bitmap_top],bitmap=[width,b.rows],raw_bitmap=[b.width,b.rows],pitch=b.pitch,pixel_mode=b.pixel_mode))
                # Preserve HB positioning adjustments, but use this raster mode's actual FT advance.
                x += advance+(pos.x_advance-metrics[order[info.codepoint]][0])*size/upem
            return image.crop((0,0,min(image.width,max(360,round(x)+16)),image.height)),records
        finally: self.lib.FT_Done_Face(face)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--full-dir',type=Path,required=True);p.add_argument('--web-dir',type=Path,required=True)
    p.add_argument('--reference-dir',type=Path,required=True,help='directory with original Mulish[wght].ttf and Mulish-Italic[wght].ttf')
    p.add_argument('--freetype-library',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--source-commit',required=True);p.add_argument('--sizes',default='12,14,16,18,20,24')
    args=p.parse_args(); args.out.mkdir(parents=True,exist_ok=False)
    inputs=args.out/'inputs';inputs.mkdir(); raster=Raster(args.freetype_library)
    report=dict(source_commit=args.source_commit,python=sys.version,platform=platform.platform(),
                dependencies={n:importlib.metadata.version(n) for n in ('freetype-py','fonttools','uharfbuzz','pillow','brotli')},
                freetype=dict(path=str(raster.path),sha256=sha(raster.path),version=raster.version,interpreter=35,lcd_filter='FT_LCD_FILTER_DEFAULT',filter_error=raster.filter_error),
                features={'kern':1,'liga':1,'ss16':1,'onum':1,'pnum':1},sizes=[int(x) for x in args.sizes.split(',')],styles={},
                limits=['FreeType simulation, not Windows, DirectWrite, or a native ClearType screenshot.',
                        'RGB stripe order; byte-coverage compositing on white, no Windows gamma/contrast tuning.',
                        'Bytecode inventory and successful rasterization do not establish visual quality. Inspect native-size PNGs.',
                        'Mulish references are instantiated original source fonts at matching design weight, without synthetic slant or bold.'])
    sources={str(raster.path):sha(raster.path)}
    overview_rows=[]
    def freeze(src,dst):
        before=sha(src);shutil.copyfile(src,dst)
        if sha(src)!=before or sha(dst)!=before: raise RuntimeError(f'input changed while freezing {src}')
        sources[str(src.resolve())]=before
        return dst
    refs={}
    for italic in (False,True):
        name='Mulish-Italic[wght].ttf' if italic else 'Mulish[wght].ttf'
        refs[italic]=freeze(args.reference_dir/name,inputs/name)
    if (args.reference_dir/'OFL.txt').exists(): freeze(args.reference_dir/'OFL.txt',inputs/'Mulish-OFL.txt')
    if (args.web_dir/'OFL.txt').exists(): freeze(args.web_dir/'OFL.txt',inputs/'Torchlette-OFL.txt')
    for style,weight in STYLES.items():
        full=freeze(args.full_dir/f'TorchletteSans-{style}.ttf',inputs/f'{style}-full.ttf')
        web=freeze(args.web_dir/f'TorchletteSans-{style}.woff2',inputs/f'{style}-web.woff2')
        decoded=inputs/f'{style}-web.ttf';f=TTFont(web);f.flavor=None;f.recalcTimestamp=False;f.save(decoded)
        ref=inputs/f'{style}-Mulish.ttf';reference=TTFont(refs['Italic' in style]);reference.recalcTimestamp=False
        instantiateVariableFont(reference,{'wght':weight},inplace=True).save(ref)
        inv={k:inventory(v) for k,v in [('full',full),('web',web),('reference',ref)]}
        inv['decoded_web_sha256']=sha(decoded)
        if not inv['full']['instruction_bytes']: raise RuntimeError(f'{style}: full font has no glyph bytecode')
        if inv['web']['instruction_bytes'] or inv['web']['hint_tables']: raise RuntimeError(f'{style}: expected unhinted app subset')
        rows=[];diagnostics=[]
        for size in report['sizes']:
            for lcd in (False,True):
                for text in SAMPLES:
                    pairs=[];rendered={}
                    for label,path,hint in [('full ON',full,True),('full OFF',full,False),('web ON',decoded,True),('web OFF',decoded,False),('Mulish ON',ref,True)]:
                        im,rec=raster.render(path,text,size,hint,lcd);rendered[label]=(im,rec)
                        panel=Image.new('RGB',(max(390,im.width),im.height+20),'white');ImageDraw.Draw(panel).text((4,2),f'{size}px {"LCD RGB" if lcd else "gray"} | {label}',fill=INK);panel.paste(im,(0,20));pairs.append(panel)
                    for prefix in ('full','web'):
                        a,ar=rendered[prefix+' ON'];b,br=rendered[prefix+' OFF'];w=max(a.width,b.width);canv=[]
                        for im in (a,b):
                            c=Image.new('RGB',(w,max(a.height,b.height)),'white');c.paste(im,(0,0));canv.append(c)
                        changed=sum(x!=y for x,y in zip(canv[0].getdata(),canv[1].getdata()))
                        diagnostics.append(dict(size=size,lcd=lcd,text=text,source=prefix,changed_pixels=changed,on=ar,off=br))
                    row=Image.new('RGB',(sum(x.width for x in pairs),max(x.height for x in pairs)),'white');x=0
                    for im in pairs:row.paste(im,(x,0));x+=im.width
                    rows.append(row)
                    if size==16 and not lcd and text==SAMPLES[0]:
                        selected=[pairs[i] for i in (0,1,4)]
                        overview=Image.new('RGB',(sum(im.width for im in selected),row.height+20),'white')
                        ImageDraw.Draw(overview).text((4,2),style,fill=INK);ox=0
                        for im in selected: overview.paste(im,(ox,20));ox+=im.width
                        overview_rows.append(overview)
        sheet=Image.new('RGB',(max(x.width for x in rows),sum(x.height for x in rows)+35),'white');ImageDraw.Draw(sheet).text((8,8),f'{style} | original size, no image scaling | FreeType {raster.version}, v35 | {weight=}',fill=INK);y=35
        for row in rows:sheet.paste(row,(0,y));y+=row.height
        if not any(d['changed_pixels'] for d in diagnostics if d['source']=='full'):
            raise RuntimeError(f'{style}: no measured hinting on/off effect in the diagnostic corpus')
        image_path=args.out/f'{style}.png';sheet.save(image_path)
        report['styles'][style]=dict(weight=weight,inventory=inv,diagnostics=diagnostics,image_sha256=sha(image_path))
    overview=Image.new('RGB',(max(im.width for im in overview_rows),sum(im.height for im in overview_rows)),'white');oy=0
    for im in overview_rows: overview.paste(im,(0,oy));oy+=im.height
    overview.save(args.out/'overview.png')
    report['overview_sha256']=sha(args.out/'overview.png')
    report['source_hashes']=sources
    report['sources_still_match']={path:sha(path)==digest for path,digest in sources.items()}
    if not all(report['sources_still_match'].values()): raise RuntimeError('source mutation; frozen inputs retained, repeat with a coherent epoch')
    (args.out/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    (args.out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>FreeType v35 diagnostic</title><h1>FreeType simulation, not native Windows</h1><p>Native pixel dimensions. Scroll horizontally; do not scale screenshots to assess hinting.</p>'+''.join(f'<h2>{s}</h2><a href="{s}.png"><img style="max-width:none" src="{s}.png" alt="{s} hinting comparisons"></a>' for s in STYLES))
    raster.lib.FT_Done_FreeType(raster.h)
    print(json.dumps(dict(styles=len(report['styles']),proof=str(args.out/'proof.json'),source_mutations=0)))


if __name__=='__main__':main()

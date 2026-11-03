"""Emit the current15 profile of three codekeys auxiliary glyphs from pinned sources."""
from pathlib import Path
import ast, math, copy, io, json, re, sys, hashlib, argparse, importlib.metadata, builtins, os
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.misc.bezierTools import splitCubicAtT
from fontTools.cu2qu.cu2qu import curves_to_quadratic
import pathops
WEIGHTS=((300,'Light'),(400,'Regular'),(500,'Medium'),(600,'SemiBold'),(700,'Bold'),(800,'ExtraBold'),(900,'Black'))
SELECTED=('uni238B','uni266D','flat.note.codekeys')
def require(ok,message):
 if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def unique_json(raw):
 def pairs(rows):
  out={}
  for k,v in rows:
   require(k not in out,f'Duplicate JSON key: {k}');out[k]=v
  return out
 return json.loads(raw,object_pairs_hook=pairs)
def exact(obj,keys,where):require(isinstance(obj,dict)and set(obj)==set(keys),f'{where}: unexpected/missing fields')
def alias(a,b):
 a,b=Path(a),Path(b)
 return a.resolve()==b.resolve()or(a.exists()and b.exists()and a.samefile(b))
def transform(conts,m):
 a,b,c,d,e,f=m;tp=lambda p:(a*p[0]+c*p[1]+e,b*p[0]+d*p[1]+f)
 return [[(s[0],)+tuple(tp(p)for p in s[1:])for s in cont]for cont in conts]
def polyline_miter(pts,w):
 def add(a,b):return(a[0]+b[0],a[1]+b[1])
 def sub(a,b):return(a[0]-b[0],a[1]-b[1])
 def mul(a,b):return(a[0]*b,a[1]*b)
 def unit(a):
  n=math.hypot(*a);return(a[0]/n,a[1]/n)if n else(0.,0.)
 def dot(a,b):return a[0]*b[0]+a[1]*b[1]
 h=w/2;n=len(pts);dirs=[unit(sub(pts[i+1],pts[i]))for i in range(n-1)]
 def side(sign):
  out=[]
  for i in range(n):
   if i==0:nn=(-dirs[0][1]*sign,dirs[0][0]*sign);out.append(add(pts[0],mul(nn,h)))
   elif i==n-1:nn=(-dirs[-1][1]*sign,dirs[-1][0]*sign);out.append(add(pts[-1],mul(nn,h)))
   else:
    a,b=dirs[i-1],dirs[i];na=(-a[1]*sign,a[0]*sign);nb=(-b[1]*sign,b[0]*sign);m=unit(add(na,nb));L=h/dot(m,na);out.append(add(pts[i],mul(m,L)))
  return out
 p=side(1)+side(-1)[::-1];return[('L',p[i],p[(i+1)%len(p)])for i in range(len(p))]
def assigned(node):
 if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):return{node.name}
 return {n.id for t in getattr(node,'targets',[])for n in ast.walk(t)if isinstance(n,ast.Name)}
def loads(node):
 needed={n.id for n in ast.walk(node)if isinstance(n,ast.Name)and isinstance(n.ctx,ast.Load)}
 needed-={n.arg for n in ast.walk(node)if isinstance(n,ast.arg)}
 if isinstance(node,ast.FunctionDef):
  local={n.id for n in ast.walk(node)if isinstance(n,ast.Name)and isinstance(n.ctx,ast.Store)}
  local|={n.arg for n in ast.walk(node)if isinstance(n,ast.arg)}
  local|={n.name for n in ast.walk(node)if isinstance(n,ast.FunctionDef)}
  needed-=local|{node.name}
 return needed

def source_slice(body,targets,provided):
 """Backward data dependencies, not source line spans or execution of build.py."""
 needed=set(targets)-set(provided)-set(vars(builtins));chosen=[]
 for node in reversed(body):
  names=assigned(node)
  if names&needed:
   require(isinstance(node,(ast.Assign,ast.FunctionDef)), 'Unsupported source statement')
   chosen.append(node);needed=(needed-names)|loads(node);needed-=set(provided)|set(vars(builtins))
 require(not needed,f'Unresolved source data dependencies: {sorted(needed)}')
 return list(reversed(chosen))
def execute_ast(nodes,filename,namespace):
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(filename),'exec'),namespace)

def original_values(font,italic,context):
 bt,kt,gd,source,donorraw,parameters,donor_path,source_weight=context
 env={'pathops':pathops,'math':math,'TransformPen':TransformPen}
 funcs={'ellipse','rect','poly','union','clip','diff','transformed','unit','stroke_line','hspans','vspans','mv'}
 selected=[n for n in bt.body if isinstance(n,ast.FunctionDef)and n.name in funcs]
 require({n.name for n in selected}==funcs,'Required build primitives changed')
 execute_ast(selected,source/'build.py',env)
 execute_ast([n for n in kt.body if isinstance(n,ast.FunctionDef)and n.name=='blob'],source/'modules/codekeys.py',env)
 params=parameters.copy();yenv={'P':lambda key,default:params.get(key,default),'ITALIC':italic}
 ynodes=source_slice(bt.body,{'YL','ITALIC_K','ITALIC_YC'},yenv)
 execute_ast(ynodes,source/'build.py',yenv);K=yenv['ITALIC_K'];YC=yenv['ITALIC_YC']
 df=TTFont(io.BytesIO(donorraw),recalcBBoxes=False,recalcTimestamp=False)
 for name in('H','l'):
  g=df['glyf'][name];require(not g.isComposite(),f'Unsupported donor component: {name}')
  xy=[(x-K*(y-YC),round(yenv['YL'](y))if name=='l'else y)for x,y in g.coordinates];g.coordinates=GlyphCoordinates(xy);g.recalcBounds(df['glyf'])
 gs=df.getGlyphSet()
 def path_of(name):
  p=pathops.Path();gs[name].draw(p.getPen(glyphSet=gs));return p
 env.update(path_of=path_of,K=K,YC=YC,donor=donor_path,source_weight=source_weight,W=lambda n:font['hmtx'][n][0],width=lambda z:z[1]-z[0],mid=lambda z:(z[0]+z[1])/2)
 targets={'CH','CC','US','KS','LW','MS','MB','GROW','fs','outer_b','inner_b','flat','rc','Rr','gap','tipe','d','esc','reach','half','fit'}
 selected=source_slice(gd.body,targets,env);execute_ast(selected,source/'modules/codekeys.py',env)
 return env

def segs(path):
    pen = RecordingPen()
    path.draw(pen)
    out = []
    here = start = None
    for op, args in pen.value:
        if op == 'moveTo':
            here = start = args[0]
        elif op == 'lineTo':
            out.append(('L', here, args[0]))
            here = args[0]
        elif op == 'curveTo':
            out.append(('C', here, *args))
            here = args[-1]
        elif op == 'closePath':
            if here != start:
                out.append(('L', here, start))
        else:
            raise ValueError(op)
    return out

def path(conts):
    p = pathops.Path()
    pen = p.getPen()
    for cont in conts:
        pen.moveTo(cont[0][1])
        for s in cont:
            if s[0] == 'L':
                pen.lineTo(s[2])
            else:
                pen.curveTo(*s[2:])
        pen.closePath()
    return p

def reverse(cont):
    return [(s[0],) + tuple(reversed(s[1:])) for s in reversed(cont)]

def clockwise(cont):
    pen = AreaPen(None)
    path([cont]).draw(pen)
    return reverse(cont) if pen.value > 0 else cont

def point(c, t):
    s = 1 - t
    return tuple((s ** 3 * c[0][a] + 3 * s * s * t * c[1][a] + 3 * s * t * t * c[2][a] + t ** 3 * c[3][a] for a in [0, 1]))

def sub(c, a, b):
    if a == 0 and b == 1:
        return c
    pieces = splitCubicAtT(*c, *([a, b] if 0 < a < b < 1 else [a] if a > 0 else [b]))
    return pieces[1] if a > 0 else pieces[0]

def root(c, fn):
    lo, hi = (0.0, 1.0)
    fl, fh = (fn(c[0]), fn(c[-1]))
    require(fl * fh <= 0, str((fl, fh)))
    for _ in range(64):
        mid = (lo + hi) / 2
        fm = fn(point(c, mid))
        if fl * fm <= 0:
            hi = mid
            fh = fm
        else:
            lo = mid
            fl = fm
    return (lo + hi) / 2

def clipped_bowl(curves, cut):
    cs = [s[1:] for s in curves if s[0] == 'C']
    require(len(cs) == 3, str('Analytic source precondition failed'))
    a = root(cs[0], lambda p: p[0] - cut)
    b = root(cs[-1], lambda p: p[0] - cut)
    return ([('C', *sub(cs[0], a, 1)), ('C', *cs[1]), ('C', *sub(cs[-1], 0, b))], {'first_t': a, 'last_t': b})

def construct(font, italic, context):
    e = original_values(font, italic, context)
    K = e['K']
    YC = e['YC']
    CH = e['CH']
    CC = e['CC']
    KS = e['KS']
    rc = e['rc']
    Rr = e['Rr']
    ellipse_code = None
    outer = [s[1:] for s in segs(e['ellipse'](*rc, Rr, Rr)) if s[0] == 'C']
    inner = [s[1:] for s in segs(e['ellipse'](*rc, Rr - KS, Rr - KS)) if s[0] == 'C']
    gap = segs(e['gap'])
    ray100 = gap[0][2]
    ray185 = gap[-2][2]

    def arc(cs):

        def rt(c, p):
            v = (p[0] - rc[0], p[1] - rc[1])
            return root(c, lambda q: (q[0] - rc[0]) * v[1] - (q[1] - rc[1]) * v[0])
        t185 = rt(cs[2], ray185)
        t100 = rt(cs[1], ray100)
        return ([('C', *sub(cs[2], t185, 1)), ('C', *cs[3]), ('C', *cs[0]), ('C', *sub(cs[1], 0, t100))], {'t185': t185, 't100': t100})
    oc, ocroots = arc(outer)
    ic, icroots = arc(inner)
    ir = reverse(ic)
    ring = oc + [('L', oc[-1][-1], ir[0][1])] + ir + [('L', ir[-1][-1], oc[0][1])]
    tip = e['tipe']
    a = math.radians(135)
    ux, uy = (math.cos(a), math.sin(a))
    nx, ny = (-uy, ux)
    reach = e['reach']
    half = e['half']
    p1 = (tip[0] - reach * ux + half * nx, tip[1] - reach * uy + half * ny)
    p2 = (tip[0] - reach * ux - half * nx, tip[1] - reach * uy - half * ny)
    chev = polyline_miter([p1, tip, p2], KS)
    shaft = polyline_miter([(rc[0] + 0.12 * Rr, rc[1] - 0.12 * Rr), (tip[0] + e['d'], tip[1] - e['d'])], KS)
    escdx = 50 - e['esc'].bounds[0]
    esc = [clockwise(c) for c in transform([ring, chev, shaft], (1, 0, -K, 1, escdx + K * CC, 0))]
    cut = e['fs'] - 0.5
    out, oroot = clipped_bowl(segs(e['outer_b']), cut)
    inc, iroot = clipped_bowl(segs(e['inner_b']), cut)
    inc = reverse(inc)
    bowl = out + [('L', out[-1][-1], inc[0][1])] + inc + [('L', inc[-1][-1], out[0][1])]
    stem = segs(e['rect'](0, 0, e['fs'], 1.12 * CH))
    fd = 55 - e['flat'].bounds[0]
    pre = [clockwise(stem), clockwise(bowl)]
    full = {'uni238B': {'contours': esc, 'analytic_source': e['transformed'](e['esc'], (1, 0, -K, 1, escdx + K * CC, 0)), 'roots': {'outer': ocroots, 'inner': icroots}, 'computed_advance': e['fit'](e['esc'], 50)[1]}, 'uni266D': {'contours': [clockwise(c) for c in transform(pre, (1, 0, 0, 1, fd, 0))], 'analytic_source': e['transformed'](e['flat'], (1, 0, 0, 1, fd, 0)), 'roots': {'outer': oroot, 'inner': iroot, 'cut_x': cut}, 'computed_advance': e['fit'](e['flat'], 55)[1]}, 'flat.note.codekeys': {'contours': [clockwise(c) for c in transform(pre, (1, 0, 0, 1, fd - 35, 0))], 'analytic_source': e['transformed'](e['flat'], (1, 0, 0, 1, fd - 35, 0)), 'roots': {'outer': oroot, 'inner': iroot, 'cut_x': cut}, 'computed_advance': e['fit'](e['flat'], 55)[1] - 45}}
    parameters = {k: e[k] for k in ['CH', 'CC', 'US', 'KS', 'LW', 'MS', 'MB', 'GROW', 'fs']}
    parameters.update(K=K, YC=YC, donor=e['donor'], source_weight=e['source_weight'])
    return (full, parameters)

def main():
 require(globals().get('_EXECUTED_RAW')is not None,'Use the hash-bound launcher, not direct execution.')
 parser=argparse.ArgumentParser(description=__doc__)
 for name in('source-root','masters','donors-manifest','config','out-dir'):parser.add_argument('--'+name,type=Path,required=True)
 parser.add_argument('--config-sha256',required=True);args=parser.parse_args()
 source=args.source_root.resolve();masters=args.masters.resolve();dest=args.out_dir.resolve()
 require(not args.out_dir.is_symlink(),'Output directory must not be a symlink.')
 require(not dest.exists(),'Output directory already exists; use a new empty path.')
 snapshots={};loaded={}
 def take(path,digest):
  path=Path(path).resolve();require(path.is_file(),f'Missing input: {path}')
  require(isinstance(digest,str)and len(digest)==64 and all(x in'0123456789abcdef'for x in digest),'Invalid SHA256')
  require(not any(alias(path,p)for p in snapshots),f'Input alias: {path}')
  raw=path.read_bytes();require(sha(raw)==digest,f'Hash mismatch: {path}')
  require(not path.is_relative_to(dest),'Output directory contains an input.')
  snapshots[str(path)]=digest;loaded[str(path)]=raw;return raw
 configraw=take(args.config,args.config_sha256);config=unique_json(configraw)
 require(globals().get('_BOOTSTRAP_SHA')==config.get('bootstrap_sha256'),'Bootstrap executed-source hash differs from config.')
 exact(config,('schema','version','source_files','originals','donor_manifest_sha256','params','modules','pins','source_commit','bootstrap_sha256'),'config')
 require(config['schema']=='torchlette-codekeys-cold-source'and type(config['version'])is int and config['version']==1,'Unsupported config schema')
 require(isinstance(config['source_commit'],str)and config['source_commit'],'Source commit required')
 require(isinstance(config['params'],dict)and all(isinstance(k,str)and type(v)in(int,float)and math.isfinite(v)for k,v in config['params'].items()),'Explicit numeric params required')
 require(config['modules']==['codekeys','cyrillic','fleurons','greek','kern','lnum','mathletters','mathnotation','meta','otfeatures','sigmoid','supsub','symbols','tensordiagram','ui'],'Explicit current15 module context required; defaults never changed.')
 require(config['pins']=={'fonttools':'4.68.0','skia-pathops':'0.9.2','brotli':'1.2.1'},'Unexpected generation pins')
 for package,version in config['pins'].items():require(importlib.metadata.version(package)==version,f'Tool version mismatch: {package}')
 exact(config['source_files'],('build.py','modules/codekeys.py','Makefile'),'source files')
 sourcebytes={name:take(source/name,digest)for name,digest in config['source_files'].items()}
 bt=ast.parse(sourcebytes['build.py']);kt=ast.parse(sourcebytes['modules/codekeys.py']);gd=next(n for n in kt.body if isinstance(n,ast.FunctionDef)and n.name=='glyphs')
 # The explicit context supports the default source knobs or declared actual
 # numeric overrides. Unknown keys cannot be silently ignored.
 known={call.args[0].value for call in ast.walk(bt)if isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='P'and call.args and isinstance(call.args[0],ast.Constant)}
 require(set(config['params'])<=known,'Unknown context parameter')
 donorraw=take(args.donors_manifest,config['donor_manifest_sha256']);donors=unique_json(donorraw)
 exact(donors,('schema','version','faces'),'donors');require(donors['schema']=='torchlette-donor-instances'and donors['version']==1,'Unexpected donor schema')
 require(isinstance(donors['faces'],list)and len(donors['faces'])==14,'Fourteen donors required')
 donorby={};make=sourcebytes['Makefile'].decode()
 for row in donors['faces']:
  exact(row,('weight','ital','source_weight','file'),'donor face');loc=(row['weight'],row['ital'])
  require(type(row['weight'])is int and type(row['ital'])is int and loc in{(w,i)for w,_ in WEIGHTS for i in(0,1)}and loc not in donorby,'Unknown/duplicate donor style')
  exact(row['file'],('path','sha256'),'donor file');path=(args.donors_manifest.resolve().parent/row['file']['path']).resolve();content=take(path,row['file']['sha256']);style=dict(WEIGHTS)[row['weight']]
  expected=int(re.search(r'^WGHT_'+re.escape(style)+r'\s*:=\s*(\d+)',make,re.M).group(1));require(row['source_weight']==expected,'Donor source weight differs from source Makefile')
  font=TTFont(io.BytesIO(content),recalcTimestamp=False,recalcBBoxes=False);require(bool(font['OS/2'].fsSelection&1)==bool(loc[1]),'Donor italic identity differs')
  donorby[loc]=(content,str(path),expected)
 expected_names={f'TorchletteSans-{("Italic"if s=="Regular"else s+"Italic")if i else s}.ttf'for _,s in WEIGHTS for i in(0,1)}
 require(set(config['originals'])==expected_names,'Original namespace requires all fourteen styles')
 originals={};analytic=[];sourcepaths={}
 for w,s in WEIGHTS:
  for i in(0,1):
   style=('Italic'if s=='Regular'else s+'Italic')if i else s;name=f'TorchletteSans-{style}.ttf';content=take(masters/name,config['originals'][name]);originals[w,i]=(name,content);sourcepaths[w,i]=masters/name
   font=TTFont(io.BytesIO(content),recalcTimestamp=False,recalcBBoxes=False);require(font['OS/2'].usWeightClass==w and bool(font['OS/2'].fsSelection&1)==bool(i),'Original style identity differs')
   d,path,sw=donorby[w,i];context=(bt,kt,gd,source,d,config['params'],path,sw);out,parameters=construct(font,bool(i),context)
   for glyph,info in out.items():
    rawpath=path_of_contours=globals()['path'](info['contours']);original=info['analytic_source'];removed=abs(pathops.op(original,rawpath,pathops.PathOp.DIFFERENCE).area);added=abs(pathops.op(rawpath,original,pathops.PathOp.DIFFERENCE).area)
    require(removed==0 and added==0,f'Analytic source fill changed: {style}/{glyph}: {removed}/{added}')
    require(info['computed_advance']==font['hmtx'][glyph][0],f'Source advance differs: {style}/{glyph}')
    analytic.append({'style':style,'weight':w,'ital':i,'name':glyph,'parameters':parameters,'logical_contours':info['contours'],'roots':info['roots'],'analytic_difference':{'removed_u2':removed,'added_u2':added},'source_advance':font['hmtx'][glyph][0],'computed_advance':info['computed_advance']})
 # Executed emitter bytes are supplied by the bootstrap after verification.
 emitter=Path(__file__).resolve();require(emitter.read_bytes()==_EXECUTED_RAW,'Executing source changed during startup')
 take(emitter,sha(_EXECUTED_RAW))
 # Retain the declared analytic-JSON -> conversion stage boundary. The original
 # converter receives list points, including its exact closing-point encoding;
 # bypassing this boundary changes TTGlyphPen list/tuple closing comparisons.
 analytic=unique_json(json.dumps(analytic))
 by={(r['style'],r['name']):r for r in analytic};styles=[('Italic'if s=='Regular'else s+'Italic')if i else s for i in(0,1)for _,s in WEIGHTS];converted={};conversion=[]
 for name in SELECTED:
  rows=[by[style,name]for style in styles];sigs=[[[seg[0]for seg in c]for c in r['logical_contours']]for r in rows];require(all(x==sigs[0]for x in sigs),'Logical source arc correspondence differs')
  for style,row in zip(styles,rows):converted[style,name]=copy.deepcopy(row['logical_contours'])
  for ci,contour in enumerate(rows[0]['logical_contours']):
   for si,segment in enumerate(contour):
    if segment[0]=='L':continue
    curves=[[tuple(p)for p in row['logical_contours'][ci][si][1:]]for row in rows];quads=curves_to_quadratic(curves,[.125]*14,all_quadratic=True);require(len({len(q)for q in quads})==1,'Joint conversion point mismatch')
    for style,q in zip(styles,quads):converted[style,name][ci][si]=('Q',*[tuple(x)for x in q])
    conversion.append({'glyph':name,'contour':ci,'segment':si,'joint_style_count':14,'declared_max_error_u':.125,'original_cubics':curves,'quadratic_results':quads})
 # All inputs validated before any generated path is created.
 dest.mkdir(parents=True,exist_ok=False);(dest/'fonts').mkdir();records=[];auxrows=[];origrows=[]
 def record(p):return{'path':str(p),'sha256':sha(p.read_bytes())}
 for(w,i),(filename,content)in originals.items():
  style=filename[len('TorchletteSans-'):-4];font=TTFont(io.BytesIO(content),recalcTimestamp=False,recalcBBoxes=False)
  for name in SELECTED:
   pen=TTGlyphPen(None)
   for contour in converted[style,name]:
    pen.moveTo(contour[0][1])
    for seg in contour:
     if seg[0]=='L':pen.lineTo(seg[2])
     else:pen.qCurveTo(*seg[2:])
    pen.closePath()
   glyph=pen.glyph(dropImpliedOnCurves=False);first=[tuple(x)for x in glyph.coordinates];params=by[style,name]['parameters'];K=params['K'];YC=params['YC']
   if K:glyph.coordinates=GlyphCoordinates([(x+K*(y-YC),y)for x,y in glyph.coordinates]);glyph.coordinates.toInt()
   glyph.recalcBounds(font['glyf']);glyph.flags[0]|=64;original=font['glyf'][name];original.recalcBounds(font['glyf']);advance,lsb=font['hmtx'][name];origin=original.xMin-lsb;metrics=(advance,glyph.xMin-origin)
   records.append({'style':style,'weight':w,'ital':i,'glyph':name,'source_hmtx':[advance,lsb],'candidate_hmtx':metrics,'source_declared_origin':origin,'candidate_declared_origin':glyph.xMin-metrics[1],'pre_reslant_integer_coordinates':first,'post_reslant_integer_coordinates':[tuple(x)for x in glyph.coordinates],'end_points':list(glyph.endPtsOfContours),'on_curve_flags':[x&1 for x in glyph.flags],'OVERLAP_SIMPLE':True,'additional_polish_points_moved':0})
   font['glyf'][name]=glyph;font['hmtx'][name]=metrics
  output=dest/'fonts'/filename;require(not any(alias(output,p)for p in snapshots),'Output aliases input');font.save(output,reorderTables=True)
  auxrows.append({'weight':w,'ital':i,'file':record(output)});origrows.append({'weight':w,'ital':i,'file':record(sourcepaths[w,i])})
 for p,digest in snapshots.items():require(sha(Path(p).read_bytes())==digest,f'Input changed during emission: {p}')
 manifest={'schema':'torchlette-auxiliary-geometry','version':1,'generator':{'source':{'path':str(emitter),'sha256':sha(_EXECUTED_RAW)},'config':record(args.config.resolve()),'commit':'Declared source working-tree lineage: '+config['source_commit']+'; executed emitter SHA256 '+sha(_EXECUTED_RAW)},'source_mode':'Cold codekeys source cubics / exact DeCasteljau / joint14 .125cu2qu / integer-reslant-integer / no extra polish','originals':origrows,'auxiliaries':auxrows,'replacements':[{'glyph':name,'ital':[0,1],'curve_provenance':'Pinned original source analytic cubic segments, exact clipping roots and joint14 conversion. source-stage-records.json records both integer stages.'}for name in SELECTED]}
 (dest/'auxiliary-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(dest/'analytic.json').write_text(json.dumps(analytic,indent=2)+'\n');(dest/'source-stage-records.json').write_text(json.dumps({'conversion':conversion,'records':records},indent=2)+'\n')
 proof={'scope':'Cold raw emitter only; no VF build, acceptance test, source default/module mutation or installation.','executed_bootstrap_sha256':_BOOTSTRAP_SHA,'executed_emitter_sha256':sha(_EXECUTED_RAW),'executed_path':str(emitter),'config_sha256':args.config_sha256,'inputs':snapshots,'modules':config['modules'],'params':config['params'],'environment':{k:os.environ.get(k)for k in('PYTHONHASHSEED','PYTHONPATH','PYTHONOPTIMIZE','PYTHONDONTWRITEBYTECODE')},'tools':{k:importlib.metadata.version(k)for k in config['pins']},'python':sys.version,'analytic_cases':len(analytic),'source_stage_records':len(records),'font_sha256':{r['file']['path']:r['file']['sha256']for r in auxrows},'manifest_sha256':sha((dest/'auxiliary-manifest.json').read_bytes())};(dest/'emission-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'output':str(dest),'fonts':14,'analytic_cases':len(analytic),'manifest_sha256':proof['manifest_sha256']}))

if __name__=='__main__':main()

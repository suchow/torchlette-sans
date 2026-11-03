"""Private API/CLI for the frozen canonical-family optional GPOS erratum."""
from pathlib import Path
from dataclasses import asdict
import argparse,json,sys
import erratum as e

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha256',required=True)
    p.add_argument('--wght',required=True);p.add_argument('--ital',required=True)
    p.add_argument('--order',choices=['wght,ital','ital,wght'],required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--canonical-mm-erratum',action='store_true',help='Opt in to exact-source, effective-cell versioned canonical-family correction; not general quantization')
    a=p.parse_args();source=a.source.resolve();raw=source.read_bytes()
    runner=e.Exporter(raw,a.source_sha256,a.canonical_mm_erratum)
    inputs=[source,Path(e.__file__),Path(e.core.__file__),Path(__file__),Path(__file__).with_name('POLICY.md'),Path(e.native_runtime.__file__),Path(sys.executable)]
    before={str(x):e.core.digest(x.read_bytes()) for x in inputs}
    root=a.out_dir.resolve();e.require(not root.exists() and not a.out_dir.is_symlink(),'Output root must be fresh')
    e.require(not source.is_relative_to(root),'Output root aliases source');root.mkdir(parents=True)
    pins={'wght':e.core.coordinate(a.wght,'wght'),'ital':e.core.coordinate(a.ital,'ital')};order=tuple(a.order.split(','))
    receipt,_=runner.partial(order[0],pins[order[0]],root/'partial.ttf',order)
    (root/'receipt.json').write_text(json.dumps(asdict(receipt),indent=2)+'\n')
    runner.complete(receipt,order[1],pins[order[1]],root/'final.ttf')
    e.require(e.core.digest(Path(receipt.partial_path).read_bytes())==receipt.partial_sha256,'Partial changed during export')
    after={str(x):e.core.digest(x.read_bytes()) for x in inputs};e.require(before==after,'Inputs drifted')
    proof={'status':'private experiment, not adopted or complete gate','policy_mode':a.canonical_mm_erratum,
      'policy':e.POLICY if a.canonical_mm_erratum else None,'inputs_before':before,'inputs_after':after,
      'pins':{k:str(v) for k,v in pins.items()},'receipt':asdict(receipt),
      'MATH_phase_only':{'audit':runner.audit,'aligned_partial_baselines':runner.partial_audit},
      'separate_optional_GPOS_phase':runner.erratum_audit,
      'partial_sha256':receipt.partial_sha256,'final_sha256':e.core.digest((root/'final.ttf').read_bytes()),
      'runtime':{'python':sys.version,'fonttools':e.core.PIN,'uharfbuzz':e.core.REPACKER_PIN,'harfbuzz':e.hb.version_string()}}
    (root/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'out':str(root),'final':proof['final_sha256']}))
if __name__=='__main__':main()

"""Hash-bound execution bootstrap. Only an explicit verified emitter is executed."""
import sys,hashlib,os
from pathlib import Path
if len(sys.argv)<4 or sys.argv[1]!='--emitter':raise ValueError('Use --emitter PATH SHA256 followed by emitter arguments.')
p=Path(sys.argv[2]).resolve();expected=sys.argv[3];raw=p.read_bytes()
if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Executed emitter source hash mismatch.')
# Third-party pins are checked by the emitter; source/helper code never imports
# from historical caches or ambient PYTHONPATH. These flags do not claim that -B
# alone prevents cache reads; all first-party code executes verified snapshots.
if sys.flags.optimize or os.environ.get('PYTHONPATH')or os.environ.get('PYTHONOPTIMIZE'):raise ValueError('Use a clean explicit Python context.')
sys.argv=[str(p),*sys.argv[4:]];sys.path=[x for x in sys.path if x not in('',str(p.parent))];sys.dont_write_bytecode=True
exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'_EXECUTED_RAW':raw,'_BOOTSTRAP_SHA':globals().get('_BOOTSTRAP_SHA')})

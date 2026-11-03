"""Explicit Make dependency metadata for math-italic geometry references.

Never constructs a font. Make calls normal build.py itself for every reference;
record-ref is the immediately following receipt step. Reuse requires matching
source/config/tool epoch AND recorded font/donor bytes, not a filename alone.
"""
import argparse
import ast
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import os
import shutil
from pathlib import Path
import sys
import tempfile

PINS = {'fonttools': '4.68.0', 'skia-pathops': '0.9.2', 'brotli': '1.2.1', 'ttfautohint-py': '0.6.1'}
WEIGHTS = {'LightItalic': 300, 'Italic': 400, 'MediumItalic': 500, 'SemiBoldItalic': 600, 'BoldItalic': 700, 'ExtraBoldItalic': 800, 'BlackItalic': 900}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value, protected=()):
    path = Path(path).resolve()
    for item in protected:
        item = Path(item)
        if path == item.resolve() or (path.exists() and item.exists() and path.samefile(item)):
            raise ValueError(f'Metadata output aliases an input: {path}')
    data = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    if path.exists() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def snapshot(root, modules):
    root = Path(root).resolve()
    modules = sorted(set(modules.split(',')))
    if not modules or 'mathitalic' in modules or 'greek' not in modules:
        raise ValueError('Reference selection must explicitly include Greek and exclude mathitalic.')
    for name in modules:
        if not name.isidentifier() or not (root / 'modules' / (name + '.py')).is_file():
            raise ValueError(f'Unknown reference module: {name}')
    paths = [p for p in root.iterdir() if p.is_file() and (p.suffix in ('.py', '.txt') or p.name == 'Makefile')]
    for folder in ['modules', 'mulish', 'commissioner', 'notosans', 'notosansmath']:
        paths.extend(p for p in (root / folder).glob('*') if p.is_file() and p.suffix in ('.py', '.ttf', '.txt'))
    files = {str(p.relative_to(root)): digest(p.read_bytes()) for p in sorted(set(paths))}
    env_names = {'LC_ALL', 'LANG', 'PYTHONHASHSEED', 'SOURCE_DATE_EPOCH'}
    for p in paths:
        if p.suffix != '.py':
            continue
        for node in ast.walk(ast.parse(p.read_bytes())):
            if not isinstance(node, ast.Call) or not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                continue
            fn = node.func
            if (isinstance(fn, ast.Name) and fn.id == 'P') or (isinstance(fn, ast.Attribute) and fn.attr == 'P') or (isinstance(fn, ast.Attribute) and fn.attr == 'get' and isinstance(fn.value, ast.Attribute) and fn.value.attr == 'environ'):
                env_names.add(node.args[0].value)
    # MODULES is explicitly canonicalized above; per-target/output paths are not geometry knobs.
    env_names -= {'MODULES', 'MATHITALIC_REFERENCE_MANIFEST', 'MATHITALIC_SOURCE_EPOCH'}
    config = {name: os.environ.get(name) for name in sorted(env_names)}
    external = {}
    for name in ['MULISH_VF']:
        if config.get(name):
            path = Path(config[name]).resolve()
            external[str(path)] = digest(path.read_bytes())
    executables = {}
    for name in ('uv', 'make'):
        found = shutil.which(name)
        if not found:
            raise ValueError(f'Required normal workflow tool is unavailable: {name}')
        resolved = Path(found).resolve()
        executables[name] = {'path': str(resolved), 'sha256': digest(resolved.read_bytes())}
    tools = {'executables': executables, 'python': sys.version, 'python_binary_sha256': digest(Path(sys.executable).resolve().read_bytes()), 'packages': {}}
    if sys.version_info[:2] != (3, 12):
        raise ValueError('Normal pinned Python 3.12 runtime required.')
    for name, pin in PINS.items():
        dist = importlib.metadata.distribution(name)
        if dist.version != pin:
            raise ValueError(f'Expected {name}=={pin}, found {dist.version}')
        package_files = {}
        for item in dist.files or []:
            path = Path(dist.locate_file(item))
            if path.is_file() and (path.suffix in ('.py', '.so', '.dylib') or path.name == 'METADATA'):
                package_files[str(item)] = digest(path.read_bytes())
        tools['packages'][name] = {'version': pin, 'file_hashes': package_files}
    payload = {'modules': modules, 'files': files, 'external_inputs': external, 'configuration': config, 'tools': tools}
    epoch = digest(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode())
    return {'schema': 1, 'source_root': str(root), 'source_epoch': epoch, 'payload': payload}


def inputs(path):
    record = json.loads(Path(path).read_bytes())
    if record.get('schema') != 1:
        raise ValueError('Unsupported inputs record.')
    actual = snapshot(record['source_root'], ','.join(record['payload']['modules']))
    if actual != record:
        raise ValueError('Reference source/resources/config/tool inputs changed.')
    return record


def mapping(root):
    path = Path(root) / 'modules/mathitalic.py'
    spec = importlib.util.spec_from_file_location('mathitalic_reference_contract', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.MAPPING


def reference(record, path, style):
    from fontTools.ttLib import TTFont
    path = Path(path).resolve()
    if style not in WEIGHTS or path.name != f'TorchletteSans-{style}.ttf' or path.parent.name != record['source_epoch']:
        raise ValueError('Reference path/style is outside the declared epoch cache.')
    raw = path.read_bytes()
    font = TTFont(io.BytesIO(raw), recalcBBoxes=False, recalcTimestamp=False)
    cmap = font.getBestCmap()
    if font['head'].unitsPerEm != 1000 or font['OS/2'].usWeightClass != WEIGHTS[style] or not font['OS/2'].fsSelection & 1:
        raise ValueError('Reference weight/style/UPEM mismatch.')
    required = mapping(record['source_root'])
    missing = sorted(set(required.values()) - set(cmap))
    if missing:
        raise ValueError(f'Reference lacks real source mappings: {missing}')
    if any(cp in cmap for cp in required):
        raise ValueError('Reference was not built with mathitalic excluded.')
    if path.read_bytes() != raw:
        raise ValueError('Reference changed while read.')
    return {'path': str(path), 'sha256': digest(raw), 'style': style, 'weight': WEIGHTS[style], 'upem': 1000}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    e = sub.add_parser('epoch'); e.add_argument('--root', required=True); e.add_argument('--modules', required=True); e.add_argument('--record', required=True)
    r = sub.add_parser('record-ref'); r.add_argument('--inputs', required=True); r.add_argument('--font', required=True); r.add_argument('--style', required=True); r.add_argument('--donor', required=True)
    m = sub.add_parser('manifest'); m.add_argument('--inputs', required=True); m.add_argument('--directory', required=True); m.add_argument('--styles', nargs='+', required=True); m.add_argument('--output', required=True)
    g = sub.add_parser('guard'); g.add_argument('--inputs', required=True); g.add_argument('--manifest', required=True); g.add_argument('--style', required=True)
    a = p.parse_args()
    if a.command == 'epoch':
        value = snapshot(a.root, a.modules)
        protected = [Path(a.root) / n for n in value['payload']['files']] + [Path(n) for n in value['payload']['external_inputs']]
        write(a.record, value, protected)
        print(value['source_epoch'])
        return
    record = inputs(a.inputs)
    protected = [Path(record['source_root']) / n for n in record['payload']['files']] + [Path(n) for n in record['payload']['external_inputs']]
    if a.command == 'record-ref':
        value = reference(record, a.font, a.style)
        donor = Path(a.donor).resolve()
        value.update(schema=1, source_epoch=record['source_epoch'], donor={'path': str(donor), 'sha256': digest(donor.read_bytes())})
        inputs(a.inputs)
        write(str(a.font) + '.reference.json', value, protected + [a.font, donor, a.inputs])
    elif a.command == 'manifest':
        directory = Path(a.directory).resolve()
        if directory.name != record['source_epoch'] or any(st not in WEIGHTS for st in a.styles):
            raise ValueError('Unknown epoch or selected reference style.')
        styles = {}
        receipt_inputs = []
        for receipt in directory.glob('*.ttf.reference.json'):
            saved = json.loads(receipt.read_bytes())
            if saved.get('schema') != 1 or saved.get('source_epoch') != record['source_epoch']:
                raise ValueError('Stale reference receipt.')
            checked = reference(record, saved['path'], saved['style'])
            if any(saved[k] != v for k, v in checked.items()) or digest(Path(saved['donor']['path']).read_bytes()) != saved['donor']['sha256']:
                raise ValueError('Reference/donor bytes differ from normal-build receipt.')
            receipt_inputs.extend([receipt, Path(saved['donor']['path'])])
            if saved['style'] in styles:
                raise ValueError('Duplicate reference style receipts.')
            styles[saved['style']] = {'path': checked['path'], 'sha256': checked['sha256']}
        if not set(a.styles) <= set(styles):
            raise ValueError('A required normal reference-build receipt is missing.')
        inputs(a.inputs)
        write(a.output, {'schema': 1, 'source_epoch': record['source_epoch'], 'styles': styles}, protected + [a.inputs] + receipt_inputs + [s['path'] for s in styles.values()])
    else:
        manifest = json.loads(Path(a.manifest).read_bytes())
        if manifest.get('schema') != 1 or manifest.get('source_epoch') != record['source_epoch']:
            raise ValueError('Candidate manifest epoch mismatch.')
        needed = 'Italic' if a.style in ('Regular', 'Italic') else a.style if a.style.endswith('Italic') else a.style + 'Italic'
        if needed not in manifest['styles']:
            raise ValueError('Candidate is missing its selected weight reference.')
        for style, item in manifest['styles'].items():
            receipt = json.loads(Path(item['path'] + '.reference.json').read_bytes())
            checked = reference(record, item['path'], style)
            if receipt.get('schema') != 1 or receipt.get('style') != style or receipt.get('path') != checked['path'] or item['sha256'] != checked['sha256'] or receipt['source_epoch'] != record['source_epoch'] or receipt['sha256'] != checked['sha256'] or digest(Path(receipt['donor']['path']).read_bytes()) != receipt['donor']['sha256']:
                raise ValueError('Candidate reference/donor binding mismatch.')
        inputs(a.inputs)


if __name__ == '__main__':
    main()

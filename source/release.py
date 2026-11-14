"""The release files: web fonts from the built .ttf, and the comparison with a release.

    python release.py woff2 FONT.ttf OUT.woff2
    python release.py compare BUILT_DIR RELEASE_DIR
    python release.py zip OUT.zip TOP PATH...

woff2 writes the whole font, every glyph and feature, as WOFF2, keeping the .ttf's
head.modified (so the same .ttf gives the same bytes on every build; up to v0.5.7 the
release web fonts carried the time they were written instead).

compare checks every file of RELEASE_DIR (ttf/, webfonts/, variable/) against the file
of the same path in BUILT_DIR: identical bytes, or else, table by table, the same
decoded tables but for head.modified and head.checkSumAdjustment, which it reports. It
exits nonzero on a missing file or any other difference.

zip writes the release download: each PATH (a file, or a folder and everything in it
but dot files such as .DS_Store) under the one folder TOP, as TOP/<name of PATH>/...
The entries are in sorted order and every one has the date ZIP_DATE and fixed
permissions (0644 for a file, 0755 for a folder), so the same files give the same
bytes on every run.
"""
import hashlib
import os
import sys
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont

HEAD_SKIP = ('modified', 'checkSumAdjustment')
# The date of every zip entry: 2026-10-31 00:00, the date that build.py and variable.py
# write into head.created and head.modified (3876249600 seconds since 1904).
ZIP_DATE = (2026, 10, 31, 0, 0, 0)


def woff2(src, dst):
    f = TTFont(src, recalcTimestamp=False)
    f.flavor = 'woff2'
    f.save(dst)


def table_diff(a, b):
    """Tables that differ between two fonts, and whether head differs only in HEAD_SKIP."""
    fa, fb = TTFont(a), TTFont(b)
    diff, head_only = [], []
    for tag in sorted(set(fa.keys()) | set(fb.keys())):
        if tag == 'GlyphOrder':
            if fa.getGlyphOrder() != fb.getGlyphOrder(): diff.append(tag)
            continue
        if tag not in fa or tag not in fb:
            diff.append(tag); continue
        if tag == 'head':
            ha, hb = vars(fa['head']), vars(fb['head'])
            keys = set(ha) | set(hb)
            if any(ha.get(k) != hb.get(k) for k in keys if k not in HEAD_SKIP):
                diff.append(tag)
            elif ha.get('modified') != hb.get('modified'):
                head_only.append(f"head.modified {ha.get('modified')} vs {hb.get('modified')}")
            continue
        if fa[tag].compile(fa) != fb[tag].compile(fb): diff.append(tag)
    return diff, head_only


def compare(built, release):
    built, release = Path(built), Path(release)
    bad = 0
    for rel in sorted(p for p in release.rglob('*') if p.is_file() and p.suffix in ('.ttf', '.woff2')):
        name = rel.relative_to(release)
        new = built / name
        if not new.exists():
            print(f'MISSING   {name}'); bad += 1; continue
        if new.read_bytes() == rel.read_bytes():
            print(f'identical {name}  sha256 {hashlib.sha256(rel.read_bytes()).hexdigest()[:16]}'); continue
        diff, head_only = table_diff(new, rel)
        if diff:
            print(f'DIFFERENT {name}: tables {" ".join(diff)}'); bad += 1
        else:
            print(f'same tables {name} ({"; ".join(head_only) or "serialization only"})')
    print('release compare:', 'FAILED' if bad else 'every file matches')
    return bad


def zip_release(out, top, paths):
    entries = {top + '/': None}
    for path in map(Path, paths):
        if path.is_dir():
            entries[f'{top}/{path.name}/'] = None
            for p in path.rglob('*'):
                rel = p.relative_to(path)
                if any(part.startswith('.') for part in rel.parts): continue
                entries[f'{top}/{path.name}/{rel.as_posix()}' + ('/' if p.is_dir() else '')] = None if p.is_dir() else p
        elif path.is_file():
            entries[f'{top}/{path.name}'] = path
        else:
            sys.exit(f'release.py zip: {path} is missing')
    tmp = Path(str(out) + '.tmp')
    with zipfile.ZipFile(tmp, 'w') as z:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, ZIP_DATE)
            info.create_system = 3                     # Unix, so that the permissions are read
            if entries[name] is None:
                info.external_attr = (0o40755 << 16) | 0x10
                z.writestr(info, b'', zipfile.ZIP_STORED)
            else:
                info.external_attr = 0o100644 << 16
                z.writestr(info, entries[name].read_bytes(), zipfile.ZIP_DEFLATED)
    os.replace(tmp, out)
    print(f'{out}: {len(entries)} entries')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'woff2' and len(sys.argv) == 4: woff2(sys.argv[2], sys.argv[3])
    elif cmd == 'compare' and len(sys.argv) == 4: sys.exit(1 if compare(sys.argv[2], sys.argv[3]) else 0)
    elif cmd == 'zip' and len(sys.argv) >= 5: zip_release(sys.argv[2], sys.argv[3], sys.argv[4:])
    else: sys.exit(__doc__)

"""The release files: web fonts from the built .ttf, and the comparison with a release.

    python release.py woff2 FONT.ttf OUT.woff2
    python release.py compare BUILT_DIR RELEASE_DIR

woff2 writes the whole font, every glyph and feature, as WOFF2, keeping the .ttf's
head.modified (so the same .ttf gives the same bytes on every build; up to v0.5.7 the
release web fonts carried the time they were written instead).

compare checks every file of RELEASE_DIR (ttf/, webfonts/, variable/) against the file
of the same path in BUILT_DIR: identical bytes, or else, table by table, the same
decoded tables but for head.modified and head.checkSumAdjustment, which it reports. It
exits nonzero on a missing file or any other difference.
"""
import hashlib
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

HEAD_SKIP = ('modified', 'checkSumAdjustment')


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


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'woff2' and len(sys.argv) == 4: woff2(sys.argv[2], sys.argv[3])
    elif cmd == 'compare' and len(sys.argv) == 4: sys.exit(1 if compare(sys.argv[2], sys.argv[3]) else 0)
    else: sys.exit(__doc__)

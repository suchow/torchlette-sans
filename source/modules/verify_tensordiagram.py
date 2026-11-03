"""Checks of the tensordiagram module: Penrose tensor-diagram glyphs (U+EE00-EE07, calt, ss20).

    verify_tensordiagram.py FONT STYLE full|subset

1. Coverage: the eight PUA characters are mapped, with ink and an advance, and every one of
   the module's 114 glyphs (105 drawn, 9 empty pending forms) exists. In the web subset they may all be absent (the Makefile's
   UNICODES leaves U+EE00-EE07 out and web_features.txt leaves ss20 out), but not some of them.
2. Default text is unchanged: the ASCII diagram strings, with no features and with the app's
   (ss01 ss02 ss16 onum pnum), shape to no glyph of the module; with ss20 on, near misses
   ("[-1, 2]", "a[i]", "x - y", "[--version]", an unclosed "[o-") stay text.
3. Shaping: each diagram, typed as ASCII under ss20 and as PUA with default features, shapes to
   the expected glyphs (legs attached, up/down legs merged, loop line under the loop).
4. Strokes: the wire is centred on the minus's centre (within 1) and as thick as the T bar
   (within 1); an up leg is as wide as the t stem (within 2; measured upright in an italic).
5. Seams: for each diagram, the positioned ink along the math axis is one unbroken span from
   the first leg to the last where the diagram is connected, and along the loop line one span
   from loop end to loop end; the wire overlaps each neighbour by 2 units (no antialiasing
   seam); the ring and box keep their counter where legs meet them.
   The loop hugs the node: the loop line's underside clears the ring node's top by 45 (within
   1), and the trace as a whole (the looped ring's bottom to the loop's top) is centred on the
   math axis (within 1); its axis is DROP below the minus's, and it stays inside the ascender
   and the descender.
6. Italic styles: the dot node stands upright (square bounds within 2) and the wire's two ends
   shift by the same amount (beyond the 2-unit overlap).
7. Nothing leaves the win vertical metrics.
"""
import sys

import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']; os2 = f['OS/2']
order = set(f.getGlyphOrder())
face = hb.Face(hb.Blob.from_file_path(PATH)); hbfont = hb.Font(face)
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
ITALIC = STYLE.endswith('Italic'); K = 0.1587; YC = 252
SUF = '.tensordiagram'
fails = 0; checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('[verify_tensordiagram FAIL]', *msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(hbfont, b, feats or {})
    return [(hbfont.get_glyph_name(i.codepoint), p.x_advance) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def names(text, feats=None): return [n for n, _ in shape(text, feats)]


def path(g, dx=0, unslant=False):
    p = pathops.Path()
    m = (1, 0, -K, 1, K * YC + dx, 0) if unslant else (1, 0, 0, 1, dx, 0)
    gs[g].draw(TransformPen(p.getPen(glyphSet=gs), m)); return p


def spans(p, y=None, x=None):
    r = pathops.Path(); pen = r.getPen()
    box = (-50000, y - 0.25, 50000, y + 0.25) if y is not None else (x - 0.25, -5000, x + 0.25, 5000)
    pen.moveTo((box[0], box[1])); pen.lineTo((box[2], box[1])); pen.lineTo((box[2], box[3])); pen.lineTo((box[0], box[3])); pen.closePath()
    q = pathops.op(p, r, pathops.PathOp.INTERSECTION); i, j = (0, 2) if y is not None else (1, 3)
    return sorted((c.bounds[i], c.bounds[j]) for c in q.contours)


def merged(sp, tol=0.6):
    out = []
    for a, b in sp:
        if out and a <= out[-1][1] + tol: out[-1] = (out[-1][0], max(out[-1][1], b))
        else: out.append((a, b))
    return out


def near(a, b, tol): return abs(a - b) <= tol


PUA = {'dot': 0xEE00, 'ring': 0xEE01, 'box': 0xEE02, 'wire': 0xEE03, 'up': 0xEE04, 'down': 0xEE05, 'lopen': 0xEE06, 'lclose': 0xEE07}
G = {k: f'uni{v:04X}' for k, v in PUA.items()}
LEGSETS = ['', 'l', 'r', 'u', 'd', 'lr', 'lu', 'ld', 'ru', 'rd', 'ud', 'lru', 'lrd', 'lud', 'rud', 'lrud']


def node(kind, legs='', trk=False):
    if not legs and not trk: return G[kind]
    return G[kind] + '.' + (legs or 'n') + ('t' if trk else '') + SUF


ALL = [node(k, l, t) for k in ('dot', 'ring', 'box') for l in LEGSETS for t in (False, True)]
ALL += [G['wire'], G['wire'] + '.t' + SUF, G['up'], G['down'], G['lopen'], G['lclose'], 'open' + SUF, 'close' + SUF, 'space' + SUF]
ALL += [G[k] + '.pend' + SUF for k in ('ring', 'dot', 'box', 'wire', 'lopen', 'lclose', 'up', 'down')] + ['space.pend' + SUF]

# ---- 1. coverage ---------------------------------------------------------------------------
mapped = [u for u in PUA.values() if u in cmap]
have = [g for g in ALL if g in order]
if MODE == 'subset' and not mapped:
    check(not have, f'subset: PUA unmapped but {len(have)} module glyphs kept')
    print(f'coverage: subset leaves the module out (U+EE00-EE07 not in UNICODES)')
    present = False
else:
    present = True
    check(len(mapped) == 8, f'only {len(mapped)} of 8 PUA characters mapped')
    check(len(have) == len(ALL), f'missing glyphs: {sorted(set(ALL) - set(have))[:8]}')
    for k, u in PUA.items():
        if u in cmap:
            g = cmap[u]; check(g == G[k], f'U+{u:04X} maps to {g}')
            check(path(g).bounds is not None and hmtx[g][0] > 0, f'{g}: no ink or advance')
    print(f'coverage: {len(mapped)} PUA characters, {len(have)} of {len(ALL)} glyphs')

DIAGRAMS = {   # ASCII, PUA string, expected glyphs between the brackets, connected along the axis?
    'scalar': ('[*]', 'dot', [node('dot')], True),
    'vector': ('[*-]', 'dot wire', [node('dot', 'r'), G['wire']], True),
    'matrix': ('[-*-]', 'wire dot wire', [G['wire'], node('dot', 'lr'), G['wire']], True),
    'order-3': ('[-*^-]', 'wire dot up wire', [G['wire'], node('dot', 'lru'), G['wire']], True),
    'order-4': ('[-o^_-]', 'wire ring up down wire', [G['wire'], node('ring', 'lrud'), G['wire']], True),
    'matmul': ('[-*-*-]', 'wire dot wire dot wire', [G['wire'], node('dot', 'lr'), G['wire'], node('dot', 'lr'), G['wire']], True),
    'matvec': ('[-*-*]', 'wire dot wire dot', [G['wire'], node('dot', 'lr'), G['wire'], node('dot', 'l')], True),
    'box': ('[-#-*-]', 'wire box wire dot wire', [G['wire'], node('box', 'lr'), G['wire'], node('dot', 'lr'), G['wire']], True),
    'ring': ('[-o-o-]', 'wire ring wire ring wire', [G['wire'], node('ring', 'lr'), G['wire'], node('ring', 'lr'), G['wire']], True),
    'trace': ('[(-*-)]', 'lopen wire dot wire lclose',
              [G['lopen'], G['wire'] + '.t' + SUF, node('dot', 'lr', True), G['wire'] + '.t' + SUF, G['lclose']], True),
    'trace AB': ('[(-*-*-)]', 'lopen wire dot wire dot wire lclose',
                 [G['lopen'], G['wire'] + '.t' + SUF, node('dot', 'lr', True), G['wire'] + '.t' + SUF, node('dot', 'lr', True),
                  G['wire'] + '.t' + SUF, G['lclose']], True),
    'tight trace': ('[(o)]', 'lopen ring lclose', [G['lopen'], node('ring', 'lr', True), G['lclose']], True),
    'outer product': ('[*- -*]', None, [node('dot', 'r'), G['wire'], 'space' + SUF, G['wire'], node('dot', 'l')], False),
}

# ---- 2. default text unchanged -----------------------------------------------------------------
mods = set(ALL)
for key, (asc, _, _, _) in DIAGRAMS.items():
    for feats in (None, APP):
        got = names('see ' + asc + ' here', feats)
        check(not (set(got) & mods), f'{asc} with features {feats} shapes to module glyphs {got}')
for text in ('[-1, 2]', 'a[i]', 'x - y', '(x)^2', 'f(o_o)', '[--version]', '[o-', '[-*- x]'):
    got = names(text, {'ss20': 1})
    check(not (set(got) & mods), f'{text!r} under ss20 shapes to module glyphs {got}')
print('default text: no module glyph without ss20 or PUA input')

if present:
    # ---- 3. shaping --------------------------------------------------------------------------------
    for key, (asc, pua, want, _) in DIAGRAMS.items():
        got = names(asc, {'ss20': 1})
        check(got == ['open' + SUF] + want + ['close' + SUF], f'{key}: {asc} under ss20 shapes to {got}')
        if pua:
            s = ''.join(chr(PUA[w]) for w in pua.split())
            check(names(s) == want, f'{key}: PUA shapes to {names(s)}, not {want}')
            check(names(s, APP) == want, f'{key}: PUA with the app features shapes to {names(s, APP)}')
    unclosed = names(chr(PUA['lopen']) + chr(PUA['wire']) + chr(PUA['dot']))
    check(not any(n.endswith('t' + SUF) for n in unclosed), f'an unclosed loop draws a loop line: {unclosed}')
    print(f'shaping: {len(DIAGRAMS)} diagrams as ASCII (ss20) and PUA (calt)')

    # ---- 4. strokes -------------------------------------------------------------------------------
    mb = path('minus').bounds; AX = (mb[1] + mb[3]) / 2
    T = path('T'); Tb = T.bounds; HS = Tb[3] - spans(T, x=Tb[0] + 50 + (K * (Tb[3] - YC) if ITALIC else 0))[-1][0]
    t = path('t', unslant=ITALIC); ts = spans(t, y=300)[0]; V = ts[1] - ts[0]
    wb = path(G['wire']).bounds
    check(near((wb[1] + wb[3]) / 2, AX, 1), f'wire centre {(wb[1] + wb[3]) / 2:.1f}, minus centre {AX:.1f}')
    check(near(wb[3] - wb[1], HS, 1), f'wire {wb[3] - wb[1]:.0f} thick, T bar {HS:.0f}')
    check(near(wb[2] - wb[0], hmtx[G['wire']][0] + 4, 1), f'wire ink {wb[2] - wb[0]:.0f} long: not its advance plus 2 at each end')
    up = path(G['up']); ub = up.bounds; leg = spans(up, y=ub[3] - 20)
    check(len(leg) == 1 and near(leg[0][1] - leg[0][0], V, 2), f'up leg {leg} against the t stem {V:.0f}')
    print(f'strokes: wire {wb[3] - wb[1]:.0f} on {AX:.1f} (T bar {HS:.0f}, minus centre {AX:.1f}); legs {V:.0f} (t stem)')

    _w = path(G['wire'] + '.t' + SUF).bounds; DROP = AX - (_w[1] + HS / 2)
    # ---- 5. seams ---------------------------------------------------------------------------------
    for key, (asc, _, want, connected) in DIAGRAMS.items():
        run = shape(asc, {'ss20': 1}); x = 0; ink = pathops.Path(); pen = ink.getPen()
        for g, adv in run:
            gs[g].draw(TransformPen(pen, (1, 0, 0, 1, x, 0))); x += adv
        ink.simplify()
        sp = merged(spans(ink, y=AX - DROP if 'trace' in key else AX))
        hollow = asc.count('o') + asc.count('#')                    # each hollow node's counter opens the axis once
        n = (1 if connected else 2) + hollow
        check(len(sp) == n, f'{key}: {len(sp)} spans on the axis, expected {n}: {sp}')
        if 'trace' in key:
            yt = path(G['lopen']).bounds[3] - HS / 2
            st = merged(spans(ink, y=yt))
            check(len(st) == 1, f'{key}: loop line broken: {st}')
    lb = path(G['lopen']).bounds; asc = path('l').bounds[3]; cap = path('H').bounds[3]
    rg = path(node('ring', 'lr', True)); ra = merged(spans(rg, y=AX - DROP))
    cut = merged(spans(rg, x=(ra[0][1] + ra[1][0]) / 2))
    rb, rt, under = cut[0][0], cut[1][1], cut[-1][0]; desc = path('p').bounds[1]
    check(len(cut) == 3, f'cut through the looped ring: {cut}')
    check(near(under - rt, 45, 1), f'loop line underside {under:.0f}, ring top {rt:.0f}: clearance {under - rt:.0f}, not 45')
    check(near((rb + lb[3]) / 2, AX, 1), f'trace {rb:.0f}..{lb[3]:.0f} centred on {(rb + lb[3]) / 2:.0f}, axis {AX:.0f}')
    check(lb[3] < asc and rb > desc, f'trace {rb:.0f}..{lb[3]:.0f} outside the ascender {asc:.0f} and descender {desc:.0f}')
    print(f'loop: trace {rb:.0f}..{lb[3]:.0f}, centre {(rb + lb[3]) / 2:.0f} on the axis {AX:.0f}, dropped {DROP:.0f}; clears the node by {under - rt:.0f}')
    for kind in ('ring', 'box'):
        p = path(node(kind, 'lr')); b = p.bounds
        sp = merged(spans(p, y=AX))
        check(len(sp) == 2, f'{node(kind, "lr")}: legs fill the counter ({sp})')
    print('seams: axis and loop line unbroken; ring and box counters open')

    # ---- 6. italic ------------------------------------------------------------------------------
    if ITALIC:
        db = path(G['dot']).bounds
        check(near(db[2] - db[0], db[3] - db[1], 2), f'dot {db[2] - db[0]:.0f} by {db[3] - db[1]:.0f}: not upright')
        check(near(wb[0] + 2, wb[2] - hmtx[G['wire']][0] - 2, 1), f'wire ends shift unequally: {wb[0]}, {wb[2] - hmtx[G["wire"]][0]}')

    # ---- 7. vertical metrics -----------------------------------------------------------------------
    for g in have:
        b = path(g).bounds
        if b: check(b[3] <= os2.usWinAscent and -b[1] <= os2.usWinDescent, f'{g}: {b} outside win metrics')

print(f'verify_tensordiagram {STYLE} {MODE}: {checks} checks, {fails} failed')
sys.exit(1 if fails else 0)

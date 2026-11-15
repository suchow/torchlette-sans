"""HarfBuzz and outline check of the african module.

    verify_african.py FONT STYLE full|subset

1. Coverage: each of the 38 letters shapes to its own glyph, with ink, a positive advance,
   GDEF class 1 (base), inside the win ascent and descent (1100 and 480: the meta module's);
   the lowest and highest points of them all are printed. The web subset keeps them all.
2. Construction, on the outlines unslanted (an italic's are sheared back about y = 252, as
   the build draws them), each against the glyphs it is made from:
   - the turned and mirrored letters are their models' outlines turned or mirrored, the
     copied ones their models' (Ɔ ɔ Ǝ Ɛ ɛ Ʇ ʇ Ʒ ʒ ǝ Ɖ): the ink differs by under 1.5% of
     the model's, after the bounding boxes are aligned (in an italic, the least over shifts
     of up to a unit across: the build rounds the slanted points);
   - heights: the flat-topped capitals end at the H's cap height, the round ones at the
     O's overshoot or Ƴ's (Ƙ), within 2; the x-height letters at the x or o, the ascenders
     with ɓ's hook (ƙ ƭ ƥ) at ɓ's top, ƀ at b's; the descenders no deeper than the deepest
     of p, y and j (ɲ ɖ ʒ ɣ ƥ ƿ ʇ), within 2;
   - stems: the stem of each letter made on another is that letter's, measured at a
     stated height, within 2 (Ƙ ƙ Ƥ ƥ Ɲ ɲ Ƀ ƀ Ɨ ɨ Ʉ ʉ Ɩ ɩ Ƿ ƿ ɖ);
   - bars: ƀ's is ħ's bar's weight; Ƀ Ɨ Ʉ Đ's; ɨ ʉ đ's, within 2;
   - counters: Ɣ ɣ have their loop (two contours), ɛ Ɛ Ɔ ɔ Ʊ ʊ Ʋ ʋ one contour.
   - Noto Sans's Ɣ ɣ Ʋ ʋ (and the small capitals Ɣ Ʋ): the weight of the left arm across it
     (Ɣ ɣ, between 0.55 and 0.75 of the height) or of the left stem (Ʋ ʋ, at half the height) is
     the model's (V v U u, V.sc U.sc), within 3; the sidebearings are the model's, within 1
     (2 in an italic: rounded after the slant, a round side's extreme moves on the unslanted
     outline); the loop's counter is open (at least LOOP_W of the arm's weight wide and LOOP_H high). Ɣ's
     loop hangs below the baseline (Noto's form), no deeper than y; Ʋ's and ʋ's curl overshoots
     the cap height or x-height by no more than OVER.
   On the full font, with the other weights of the same slant beside it, each glyph the
   module adds (the small capitals too) has the same number of contours at every weight.
3. Forms: smcp turns each lowercase letter and c2sc its capital into the same small capital,
   which is a glyph of its own with ink no taller than the small-cap H's (but for hooks and
   tails above and below it); the case partners are each other's (Unicode).
   ɨ before a mark above (or below, then above) is its dotless form, ɨ alone keeps its dot;
   the capitals take the .case acute and tilde (ccmp). Ɣ ɣ take the dot below under the loop.
4. Kerning, on the full font: a side made as its model's kerns as the model does
   (Tɔ as To, VƆ as VO, ƔA as VA, ƙo as ko, ƀo as bo, Ɲa as Na, Ʉ, as U, ...).
"""
import os
import sys

import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept  # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
ITALIC = 'Italic' in STYLE
K, YC = (0.1587 if ITALIC else 0.0), 252
WIN_ASCENT, WIN_DESCENT = 1100, 480
LOOP_W, LOOP_H, OVER = 0.25, 0.7, 16

tt = TTFont(PATH)
GO = tt.getGlyphOrder(); HAVE = set(GO)
GS = tt.getGlyphSet(); HMTX = tt['hmtx'].metrics
CMAP = tt.getBestCmap()
GDEF = tt['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in tt else {}
HB = hb.Font(hb.Face(hb.Blob.from_file_path(PATH)))
fails, checks = [], 0

PAIRS = [(0x0186, 0x0254), (0x018E, 0x01DD), (0x0190, 0x025B), (0x0194, 0x0263), (0x0196, 0x0269),
         (0x01B1, 0x028A), (0x01B2, 0x028B), (0x01B7, 0x0292), (0x0198, 0x0199), (0x01A4, 0x01A5),
         (0x01AC, 0x01AD), (0x019D, 0x0272), (0x0243, 0x0180), (0x01F7, 0x01BF), (0xA78B, 0xA78C),
         (0xA7B1, 0x0287), (0x0189, 0x0256), (0x0197, 0x0268), (0x0244, 0x0289)]
CPS = [c for p in PAIRS for c in p]


def check(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties()
    hb.shape(HB, b, feats or {})
    return [(GO[i.codepoint], p.x_advance) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def outline(g):
    p = pathops.Path()
    GS[g].draw(TransformPen(p.getPen(glyphSet=GS), (1, 0, -K, 1, K * YC, 0)))
    p.simplify()
    return p


def ncont(p): return len(list(p.contours))
def W(g): return HMTX[g][0]
def G(ch): return CMAP.get(ord(ch))


def hspans(p, y):
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((-3000, y - 0.5)); pen.lineTo((5000, y - 0.5)); pen.lineTo((5000, y + 0.5)); pen.lineTo((-3000, y + 0.5)); pen.closePath()
    return sorted((c.bounds[0], c.bounds[2]) for c in pathops.op(p, r, pathops.PathOp.INTERSECTION).contours)


def vspans(p, x):
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((x - 0.5, -3000)); pen.lineTo((x + 0.5, -3000)); pen.lineTo((x + 0.5, 5000)); pen.lineTo((x - 0.5, 5000)); pen.closePath()
    return sorted((c.bounds[1], c.bounds[3]) for c in pathops.op(p, r, pathops.PathOp.INTERSECTION).contours)


def moved(p, m):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q


def same(p, q):
    """The ink p and q do not share, after their boxes are aligned, of q's ink. In an italic the
    unslanted box ends at sheared-back points the build rounded after slanting, which a turned
    or mirrored outline has at other heights, so the boxes can be a unit out across: the
    least over horizontal shifts of up to a unit (a thin italic ʇ is 2.25% of t one unit out
    and 0.65% aligned, every point within a unit of t's turned)."""
    a, b = p.bounds, q.bounds
    best = None
    for dx in ((-1, -0.5, 0, 0.5, 1) if ITALIC else (0,)):
        r = moved(q, (1, 0, 0, 1, a[0] - b[0] + dx, a[1] - b[1]))
        d = abs(pathops.op(p, r, pathops.PathOp.XOR).area) / max(1, abs(r.area))
        best = d if best is None else min(best, d)
    return best


# ---- 1. coverage ----------------------------------------------------------------------
lo, hi = 0, 0
for cp in CPS:
    s = shape(chr(cp))
    g = s[0][0] if len(s) == 1 else None
    check(g is not None and g != '.notdef' and CMAP.get(cp) == g, f'U+{cp:04X} {chr(cp)}: shapes to {s}')
    if not g or g == '.notdef': continue
    p = outline(g); b = p.bounds
    check(abs(p.area) > 0, f'{g}: no ink')
    check(W(g) > 0, f'{g}: advance {W(g)}')
    check(GDEF.get(g) == 1, f'{g}: GDEF class {GDEF.get(g)}')
    gb = tt['glyf'][g]; gb.recalcBounds(tt['glyf'])
    check(gb.yMax <= WIN_ASCENT and gb.yMin >= -WIN_DESCENT, f'{g}: {gb.yMin}..{gb.yMax} outside the win metrics')
    lo, hi = min(lo, gb.yMin), max(hi, gb.yMax)

have = lambda ch: G(ch) in HAVE if G(ch) else False
if all(have(chr(c)) for c in CPS):
    # ---- 2. construction --------------------------------------------------------------
    def turned(g):
        b = outline(g).bounds
        return moved(outline(g), (-1, 0, 0, -1, b[0] + b[2], b[1] + b[3]))

    def mirrored(g):
        b = outline(g).bounds
        return moved(outline(g), (-1, 0, 0, 1, b[0] + b[2], 0))
    for ch, model in (('Ɔ', turned(G('C'))), ('ɔ', turned(G('c'))), ('Ǝ', mirrored(G('E'))), ('Ɛ', mirrored(G('З'))),
                      ('ɛ', mirrored(G('з'))), ('Ʇ', turned(G('T'))), ('ʇ', turned(G('t'))), ('Ʒ', outline(G('Ӡ'))),
                      ('ʒ', outline(G('ӡ'))), ('ǝ', outline(G('ə'))), ('Ɖ', outline(G('Đ'))), ('ꞌ', outline(G("'")))):
        d = same(outline(G(ch)), model)
        check(d < 0.015, f'{ch}: differs from its model by {d:.2%}')
    top = lambda ch: outline(G(ch)).bounds[3]
    bot = lambda ch: outline(G(ch)).bounds[1]
    cap, otop, xh, xo = top('H'), top('O'), top('x'), top('o')
    for ch in 'ƎƗɃƤƬƝƖǷƉ':
        check(abs(top(ch) - cap) <= 2, f'{ch}: top {top(ch):.0f}, cap height {cap:.0f}')
    for ch in 'ƆƐ':
        check(abs(top(ch) - otop) <= 2, f'{ch}: top {top(ch):.0f}, O {otop:.0f}')
    check(abs(top('Ʊ') - cap) <= 2, f'Ʊ: top {top("Ʊ"):.0f}, cap height {cap:.0f}')
    check(cap - 2 <= top('Ʋ') <= cap + OVER, f'Ʋ: top {top("Ʋ"):.0f}, cap height {cap:.0f}')
    check(xh - 2 <= top('ʋ') <= xh + OVER, f'ʋ: top {top("ʋ"):.0f}, x-height {xh:.0f}')
    check(bot('Ɣ') >= bot('y') - 2, f'Ɣ: bottom {bot("Ɣ"):.0f}, deeper than y ({bot("y"):.0f})')
    check(abs(top('Ƙ') - top('Ƴ')) <= 2, f'Ƙ: top {top("Ƙ"):.0f}, Ƴ {top("Ƴ"):.0f}')
    check(abs(top('Ɣ') - cap) <= 2 and abs(top('Ʇ') - cap) <= 2, f'Ɣ Ʇ: tops {top("Ɣ"):.0f} {top("Ʇ"):.0f}, cap {cap:.0f}')
    for ch in 'ɔɛɣɩʊɲɨʉ':
        check(min(abs(top(ch) - xh), abs(top(ch) - xo)) <= 2 or (ch == 'ɨ' and abs(top(ch) - top('i')) <= 2),
              f'{ch}: top {top(ch):.0f}, x-height {xh:.0f} / o {xo:.0f}')
    for ch in 'ƙƭƥ':
        check(abs(top(ch) - top('ɓ')) <= 2, f'{ch}: top {top(ch):.0f}, ɓ {top("ɓ"):.0f}')
    check(abs(top('ƀ') - top('b')) <= 2, f'ƀ: top {top("ƀ"):.0f}, b {top("b"):.0f}')
    deep = min(bot('p'), bot('y'), bot('j'))
    for ch in 'ɲɖʒɣƥƿʇ':
        check(bot(ch) >= deep - 2, f'{ch}: bottom {bot(ch):.0f}, deeper than p y j ({deep:.0f})')
    for ch in 'ƆƐƎƗɃƤƬƖǷƉƱƲƘɄ':
        check(bot(ch) >= -20, f'{ch}: bottom {bot(ch):.0f}, below the baseline')

    def stem(ch, y, last=False):
        s = hspans(outline(G(ch)), y)
        return (s[-1] if last else s[0]) if s else (0, 0)
    for ch, model, y, last in (('Ƙ', 'K', 0.2, False), ('ƙ', 'k', 0.2, False), ('Ƥ', 'P', 0.2, False), ('ƥ', 'p', -0.3, False),
                               ('Ɲ', 'N', 0.5, False), ('ɲ', 'n', 0.5, False), ('Ƀ', 'B', 0.65, False), ('ƀ', 'b', 1.5, False),
                               ('Ɨ', 'I', 0.2, False), ('ɨ', 'i', 0.2, False), ('Ʉ', 'U', 0.8, False), ('ʉ', 'u', 0.8, False),
                               ('Ʉ', 'U', 0.8, True), ('ʉ', 'u', 0.8, True), ('Ɩ', 'I', 0.6, False), ('ɩ', 'ı', 0.6, False),
                               ('Ƿ', 'P', 0.6, False), ('ƿ', 'p', -0.3, False), ('ɖ', 'd', 0.5, True), ('ɖ', 'd', 1.3, True)):
        hgt = cap if model.isupper() else xh
        a, b_ = stem(ch, y * hgt, last), stem(model, y * hgt, last)
        check(abs((a[1] - a[0]) - (b_[1] - b_[0])) <= 2,
              f'{ch}: stem {a[1] - a[0]:.0f} at {y * hgt:.0f}, {model} {b_[1] - b_[0]:.0f}')

    def bar(ch, x_from_left=True):
        p = outline(G(ch)); b = p.bounds
        v = vspans(p, b[0] + 4 if x_from_left else b[2] - 4)
        return v[0][1] - v[0][0] if v else 0
    hb_, Db, db = bar('ħ'), bar('Đ'), bar('đ', False)
    check(abs(bar('ƀ') - hb_) <= 2, f'ƀ: bar {bar("ƀ"):.0f}, ħ {hb_:.0f}')
    for ch in 'ɃƗɄ':
        check(abs(bar(ch) - Db) <= 2, f'{ch}: bar {bar(ch):.0f}, Đ {Db:.0f}')
    for ch in 'ɨʉ':
        check(abs(bar(ch) - db) <= 2, f'{ch}: bar {bar(ch):.0f}, đ {db:.0f}')
    for ch in 'Ɣɣ':
        check(ncont(outline(G(ch))) == 2, f'{ch}: {ncont(outline(G(ch)))} contours, want the loop (2)')
    for ch in 'ɛƐƆɔƱʊƲʋ':
        check(ncont(outline(G(ch))) == 1, f'{ch}: {ncont(outline(G(ch)))} contours, want 1')

    def stroke_of(p, kind, H):
        if kind == 'stem':
            s = hspans(p, 0.5 * H)[0]
            return s[1] - s[0]
        a, b = hspans(p, 0.55 * H)[0], hspans(p, 0.75 * H)[0]
        dx, dy = (b[0] + b[1] - a[0] - a[1]) / 2, 0.2 * H
        return (a[1] - a[0]) * dy / (dx * dx + dy * dy) ** 0.5

    def side(g):
        b = outline(g).bounds
        return b[0], W(g) - b[2]
    noto = [(G('ɣ'), G('v'), 'arm', xh), (G('Ɣ'), G('V'), 'arm', cap), (G('ʋ'), G('u'), 'stem', xh), (G('Ʋ'), G('U'), 'stem', cap)]
    if 'V.sc' in HAVE:
        sch = outline('H.sc').bounds[3]
        noto += [('uni0194.sc.african', 'V.sc', 'arm', sch), ('uni01B2.sc.african', 'U.sc', 'stem', sch)]
    for g, m, kind, H in noto:
        if g not in HAVE: check(False, f'{g}: missing'); continue
        a, b_ = stroke_of(outline(g), kind, H), stroke_of(outline(m), kind, H)
        check(abs(a - b_) <= 3, f'{g}: {kind} {a:.1f}, {m} {b_:.1f}')
        (l1, r1), (l2, r2) = side(g), side(m)
        tol = 2 if ITALIC else 1
        check(abs(l1 - l2) <= tol and abs(r1 - r2) <= tol, f'{g}: sidebearings {l1:.0f} {r1:.0f}, {m} {l2:.0f} {r2:.0f}')
        if kind == 'arm':
            cs = sorted(outline(g).contours, key=lambda c_: abs(c_.area))
            if len(cs) == 2:
                cb = cs[0].bounds
                check(cb[2] - cb[0] >= LOOP_W * b_ and cb[3] - cb[1] >= LOOP_H * b_,
                      f'{g}: the loop\'s counter {cb[2] - cb[0]:.0f} x {cb[3] - cb[1]:.0f}, arm {b_:.0f}')

    # ---- 3. forms ---------------------------------------------------------------------
    sc_h = outline('H.sc').bounds[3] if 'H.sc' in HAVE else None
    for up, low in PAIRS:
        U, L = chr(up), chr(low)
        check(L.upper() == U and U.lower() == L,
              f'{U} {L}: not case partners')
        if not (kept('smcp') and kept('c2sc')) or sc_h is None: continue
        a, b = shape(L, {'smcp': 1}), shape(U, {'c2sc': 1})
        check(len(a) == 1 and len(b) == 1 and a[0][0] == b[0][0] and a[0][0] not in (G(L), G(U)),
              f'{L} smcp {a}, {U} c2sc {b}: want one small capital')
        if len(a) == 1 and a[0][0] in HAVE:
            g = a[0][0]
            check(GDEF.get(g) == 1, f'{g}: GDEF class {GDEF.get(g)}')
            bb = outline(g).bounds
            if U not in 'ƘƲƝƔꞋ':
                check(bb[3] <= sc_h + 15, f'{g}: top {bb[3]:.0f}, above the small-cap height {sc_h:.0f}')

    # ---- 4. kerning --------------------------------------------------------------------
    def kern(text):
        s = shape(text)
        return s[0][1] - W(s[0][0]) if len(s) == 2 else None
    if MODE == 'full' and kept('kern'):
        for new, old in (('Tɔ', 'To'), ('VƆ', 'VO'), ('ƔA', 'VA'), ('ƙo', 'ko'), ('ƀo', 'bo'), ('Ɲa', 'Na'),
                         ('Ʉ,', 'U,'), ('ɣo', 'vo'), ('Ɛ.', 'C.'), ('Tɛ', 'Tc'), ('Ƭa', 'Ta'), ('ɖo', 'do'),
                         ('Ƀa', 'Ba'), ('AƐ', 'AC'), ('YƎ', 'YZ')):
            check(kern(new) == kern(old), f'{new!r} kerned {kern(new)}, {old!r} {kern(old)}')

# ɨ is soft-dotted: before a mark above (or a mark below, then one above) ccmp gives its
# dotless form, which keeps its advance and has no ink above the dotless i's top
if kept('ccmp') and 0x0268 in CMAP:
    for txt in ('\u0268\u0301', '\u0268\u0300', '\u0268\u0303', '\u0268\u0323\u0301'):
        g0 = shape(txt)[0][0]
        check(g0 != CMAP[0x0268] and W(g0) == W(CMAP[0x0268]) and outline(g0).bounds[3] <= outline('dotlessi').bounds[3] + 2,
              f'soft dot {txt!r}: {g0}')
    check(shape('\u0268')[0][0] == CMAP[0x0268], 'soft dot: ɨ alone keeps its dot')
# Ɣ ɣ take the dot below under their loop at every weight (a light weight's thin loop once
# left room for it beside the loop, outside the letter): its top below the loop's bottom
if kept('mark') and 'dotbelowcomb' in HAVE:
    for cp in (0x0194, 0x0263):
        if cp not in CMAP: continue
        b = hb.Buffer(); b.add_str(chr(cp) + '\u0323'); b.guess_segment_properties(); hb.shape(HB, b, {})
        gi, ps = b.glyph_infos, b.glyph_positions
        ok = len(gi) == 2 and GO[gi[1].codepoint] == 'dotbelowcomb'
        if ok:
            lb = outline(CMAP[cp]).bounds
            m = moved(outline('dotbelowcomb'), (1, 0, 0, 1, ps[0].x_advance + ps[1].x_offset - K * ps[1].y_offset, ps[1].y_offset)).bounds
            ok = m[3] < lb[1] and lb[0] <= (m[0] + m[2]) / 2 <= lb[2]
        check(ok, f'{chr(cp)}\u0323: the dot below is not under the loop')
# the capitals take the .case marks above, as Mulish's Latin capitals do (ccmp)
if kept('ccmp') and 'acutecomb.case' in HAVE:
    for cp in CPS:
        if cp in CMAP and chr(cp).isupper() and cp != 0xA78B:
            for mk, case in (('́', 'acutecomb.case'), ('̃', 'tildecomb.case')):
                if case in HAVE:
                    r = shape(chr(cp) + mk)
                    check(len(r) == 2 and r[1][0] == case, f'{chr(cp)}{mk}: {[g for g, _ in r]}, want {case}')

# the same contours at every weight of this slant (the variable font interpolates them)
if MODE == 'full':
    d = os.path.dirname(os.path.abspath(PATH))
    W7 = ['Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']
    sibs = [({'Regular': 'Italic'}.get(w, w + 'Italic') if ITALIC else w) for w in W7]
    paths = [os.path.join(d, f'TorchletteSans-{s}.ttf') for s in sibs]
    if all(os.path.exists(q) for q in paths):
        fonts = [TTFont(q, lazy=True) for q in paths]
        names = [CMAP[c] for c in CPS if c in CMAP] + [g for g in GO if g.endswith('.african')]
        for g in names:
            counts = [f['glyf'][g].numberOfContours if g in f.getGlyphOrder() else None for f in fonts]
            check(len(set(counts)) == 1, f'{g}: contours across the {"italic" if ITALIC else "upright"} weights {counts}')

print(f'african {STYLE} {MODE}: {checks - len(fails)}/{checks} checks passed; ink from {lo} to {hi}')
for f in fails[:40]:
    print('  FAIL', f)
sys.exit(1 if fails else 0)

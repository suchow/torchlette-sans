"""HarfBuzz and outline check of the punctuation module.

    verify_punctuation.py FONT STYLE full|subset

1. Coverage: each of ⸺ ⸻ ⁓ ‛ ‟ ‱ ‽ ‧ ‼ ⁇ ⸮ ⁑ ℃ ℉ ℗ shapes to its own glyph (AGL name, or
   uniXXXX), with ink, a positive advance, GDEF class 1 (base), inside the hhea ascender
   and descender. The web subset keeps them all (U+2000-206F and U+2100-214F, and the
   Makefile's U+2E2E, U+2E3A-2E3B).
2. Composition, on the outlines unslanted (an italic's are sheared back about y = 252, as
   the build draws them), each against the glyphs it is made from:
   - ⸺ ⸻ are one bar, two and three em dashes long: advance 2 and 3 em dashes, the em
     dash's height and thickness, one contour.
   - ⁓ is the em dash's advance, centred on its height (within 2), one contour, wider
     than the tilde.
   - ‛ ‟ ⸮ are ’ ” ? mirrored about the middle of the advance, the same advance: the
     outlines differ by under 3% of their area (the grid rounding of the reslant); ⸮'s dot
     is drawn round again, so its hook is compared, and its dot's size and place.
   - ‼ ⁇ are two ! or two ?: the first at 0, the second one advance less an overlap
     between 0 and the gap two typed marks have; the outline is the two marks exactly.
   - ‽ is three contours (the hook and stem, the counter, the dot), the ?'s height and dot,
     an advance from the ?'s to 1.6 times it; a stem over the dot from the foot to the
     top of the arc, as wide as the !'s stem at the same height where it meets the
     counter; the counter at least 0.2 of the ?'s advance wide.
   - ‱ holds the whole ‰ and two contours more (the ring), advance ‰'s plus the ring's
     step, the new ring a copy of the last.
   - ‧ is the middle dot, centred on the hyphen's height (within 1), its sidebearings
     at most 0.6 of the middle dot's.
   - ⁑ is * over ⁎ exactly, the asterisk's advance.
   - ℃ ℉ hold ° at its own place and C or F moved in, closer than typed (advance under
     ° + letter) and clear of the ring (no contour merged).
   - ℗ holds the ring of © exactly, the ©'s advance, and a P (two contours) inside the
     ring's inner circle, as tall as the R of ® (within 2) with its stem (within 3).
   On the full font, with the other weights of the same slant beside it, each glyph has
   the same number of contours at every weight (for the variable font).
3. Forms: under smcp and c2sc, ‼ ⁇ ‽ ⸮ ‛ ‟ ‱ ⸺ ⸻ become small capitals as tall as the
   small capitals of ! ? ’ ” ‰ and the em dash; under case, ⸺ ⸻ rise as the em dash does
   and ‧ as the hyphen (it stays on the hyphen's height). (Skipped on the web subset when it drops the feature.)
4. Kerning (KERN; it comes from the kern module's INHERIT table, not from this module):
   ‛ ‟ kern as ’ ” (their mirror images), ‼ ⁇ ‽ as ! ? ?, ⸺ ⸻ as the em dash, ℃ ℉ as ° on the left and C or F on
   the right: a pair the model kerns gets a value of the same sign. ⸺ ⸻ against T A V Y J
   kern exactly as the em dash, and under case as the em dash's case form.
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

tt = TTFont(PATH)
GO = tt.getGlyphOrder(); HAVE = set(GO)
GS = tt.getGlyphSet(); HMTX = tt['hmtx'].metrics
CMAP = tt.getBestCmap()
GDEF = tt['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in tt else {}
HB = hb.Font(hb.Face(hb.Blob.from_file_path(PATH)))
fails, checks = [], 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties()
    hb.shape(HB, b, feats or {})
    return [(GO[i.codepoint], p.x_advance) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def outline(g, dx=0):
    """g's outline, unslanted, moved by dx."""
    p = pathops.Path()
    GS[g].draw(TransformPen(p.getPen(glyphSet=GS), (1, 0, -K, 1, K * YC + dx, 0)))
    p.simplify()
    return p


def area(p): return abs(p.area)


def xor_frac(a, b):
    """The area where a and b differ, as a fraction of a's area."""
    return area(pathops.op(a, b, pathops.PathOp.XOR)) / max(area(a), 1)


def union(*ps):
    out = ps[0]
    for q in ps[1:]: out = pathops.op(out, q, pathops.PathOp.UNION)
    return out


def ncont(p): return len(list(p.contours))


def hspans(p, y):
    box = pathops.Path(); pen = box.getPen()
    pen.moveTo((-3000, y - 0.5)); pen.lineTo((5000, y - 0.5)); pen.lineTo((5000, y + 0.5)); pen.lineTo((-3000, y + 0.5)); pen.closePath()
    return sorted((c.bounds[0], c.bounds[2]) for c in pathops.op(p, box, pathops.PathOp.INTERSECTION).contours)


def W(g): return HMTX[g][0]


NAMES = {0x2E3A: 'uni2E3A', 0x2E3B: 'uni2E3B', 0x2053: 'uni2053', 0x201B: 'quotereversed', 0x201F: 'uni201F',
         0x2031: 'uni2031', 0x203D: 'uni203D', 0x2027: 'uni2027', 0x203C: 'exclamdbl', 0x2047: 'uni2047',
         0x2E2E: 'uni2E2E', 0x2051: 'uni2051', 0x2103: 'uni2103', 0x2109: 'uni2109', 0x2117: 'uni2117'}

# ---- 1. coverage ---------------------------------------------------------------------
asc, desc = tt['hhea'].ascent, tt['hhea'].descent
ok = {}
for cp, name in NAMES.items():
    s = shape(chr(cp))
    good = len(s) == 1 and s[0][0] == name
    check(good, f'U+{cp:04X} shapes to {s}, want {name}')
    if not good: continue
    p = outline(name); b = p.bounds
    fine = area(p) > 0 and W(name) > 0 and b[1] >= desc and b[3] <= asc
    check(fine, f'{name}: ink {b}, advance {W(name)}, outside {desc}..{asc} or empty')
    check(GDEF.get(name) == 1, f'{name}: GDEF class {GDEF.get(name)}, want 1')
    ok[name] = fine

def have(*gs): return all(g in HAVE and ok.get(g, True) for g in gs)

# ---- 2. composition ------------------------------------------------------------------
em = outline('emdash'); eb = em.bounds
for name, n in (('uni2E3A', 2), ('uni2E3B', 3)):
    if not have(name): continue
    p = outline(name); b = p.bounds
    check(W(name) == n * W('emdash'), f'{name}: advance {W(name)}, want {n} x {W("emdash")}')
    check(ncont(p) == 1 and abs(b[1] - eb[1]) <= 1 and abs(b[3] - eb[3]) <= 1, f'{name}: {ncont(p)} contours, ink {b} (em dash {eb})')
    check(abs((b[2] - b[0]) - (n * W('emdash') - (W('emdash') - (eb[2] - eb[0])))) <= 2, f'{name}: bar {b[2] - b[0]:.0f} long')

if have('uni2053'):
    p = outline('uni2053'); b = p.bounds; tb = outline('asciitilde').bounds
    check(W('uni2053') == W('emdash'), f'swung dash: advance {W("uni2053")}, want the em dash\'s {W("emdash")}')
    check(abs((b[1] + b[3]) / 2 - (eb[1] + eb[3]) / 2) <= 2, f'swung dash: centred at {(b[1] + b[3]) / 2:.0f}, em dash at {(eb[1] + eb[3]) / 2:.0f}')
    check(ncont(p) == 1 and b[2] - b[0] > 1.5 * (tb[2] - tb[0]), f'swung dash: {ncont(p)} contours, {b[2] - b[0]:.0f} wide (tilde {tb[2] - tb[0]:.0f})')

def mirrored(g, w):
    p = pathops.Path(); outline(g).draw(TransformPen(p.getPen(), (-1, 0, 0, 1, w, 0))); p.simplify(); return p

for name, src in (('quotereversed', 'quoteright'), ('uni201F', 'quotedblright'), ('uni2E2E', 'question')):
    for suf in ('', '.sc'):
        n, s = name + suf, src + suf
        if not (have(n) and s in HAVE): continue
        check(W(n) == W(s), f'{n}: advance {W(n)}, {s} {W(s)}')
        a, m = outline(n), mirrored(s, W(s))
        if name == 'uni2E2E':                       # the dot is drawn round again: compare the hooks, and the dot's size
            lo = lambda p: min(p.contours, key=lambda c: c.bounds[1])
            da, dm = lo(a).bounds, lo(m).bounds
            check(abs((da[3] - da[1]) - (dm[3] - dm[1])) <= 1.5 and abs((da[1] + da[3]) - (dm[1] + dm[3])) <= 3,
                  f'{n}: dot {da}, {s}\'s mirrored {dm}')
            hk = lambda p: max(p.contours, key=lambda c: c.bounds[3])
            a, m = hk(a), hk(m)
        d = xor_frac(a, m)
        check(d < 0.03, f'{n}: not {s} mirrored about the middle of its advance ({d:.3%} of the area differs)')

def doubled(name, src):
    if not (have(name) and src in HAVE): return
    sb = outline(src).bounds; typed = (W(src) - sb[2]) + sb[0]
    overlap = 2 * W(src) - W(name)
    check(-0.5 <= overlap <= typed + 0.5, f'{name}: advance {W(name)}, overlap {overlap} outside 0..{typed:.0f} (2 x {src} {W(src)})')
    step = W(name) - W(src)
    d = xor_frac(outline(name), union(outline(src), outline(src, step)))
    check(d < 0.01, f'{name}: not two {src} {step} apart ({d:.3%} differs)')
for suf in ('', '.sc'):
    doubled('exclamdbl' + suf, 'exclam' + suf)
    doubled('uni2047' + suf, 'question' + suf)

for suf in ('', '.sc'):
    n, q, e = 'uni203D' + suf, 'question' + suf, 'exclam' + suf
    if not (have(n) and q in HAVE and e in HAVE): continue
    p, qp = outline(n), outline(q); b, qb = p.bounds, qp.bounds
    check(W(q) <= W(n) <= 1.6 * W(q), f'{n}: advance {W(n)}, want from {q}\'s {W(q)} to 1.6 times it')
    check(abs(b[3] - qb[3]) <= 1 and abs(b[1] - qb[1]) <= 1, f'{n}: ink {b}, {q} {qb}')
    cs = sorted(p.contours, key=lambda c: c.bounds[1])
    qcs = sorted(qp.contours, key=lambda c: c.bounds[1])
    check(len(cs) == 3, f'{n}: {len(cs)} contours, want 3 (hook and stem, the counter, the dot)')
    if len(cs) != 3: continue
    dot, qdot, hook = cs[0].bounds, qcs[0].bounds, qcs[-1].bounds
    check(abs((dot[2] - dot[0]) - (qdot[2] - qdot[0])) <= 1 and abs((dot[3] - dot[1]) - (qdot[3] - qdot[1])) <= 1
          and abs(dot[1] - qdot[1]) <= 1, f'{n}: dot {dot}, {q}\'s {qdot}')
    dcx = (dot[0] + dot[2]) / 2
    # the !'s stem over the dot, from the foot to the top of the arc
    for t in (0.05, 0.3, 0.55, 0.75, 0.95):
        y = hook[1] + t * (hook[3] - hook[1])
        check(any(a_ <= dcx <= c_ for a_, c_ in hspans(p, y)), f'{n}: no stem over the dot (x {dcx:.0f}) at y {y:.0f}: {hspans(p, y)}')
    # the counter is open, and the stem beside it is the !'s, tapered as the ! is
    cb = min(cs[1:], key=lambda c: c.bounds[3] - c.bounds[1]).bounds     # the counter, inside the outer contour
    check(cb[1] > dot[3] and cb[2] - cb[0] >= 0.2 * W(q), f'{n}: counter {cb}, want at least {0.2 * W(q):.0f} wide')
    es = sorted(outline(e).contours, key=lambda c: c.bounds[1])[-1].bounds
    k = (hook[3] + 40 - hook[1]) / (es[3] - es[1])
    for y in (cb[1] + 0.4 * (cb[3] - cb[1]), cb[1] + 0.7 * (cb[3] - cb[1])):
        sp = [s_ for s_ in hspans(p, y) if s_[0] <= dcx <= s_[1]]
        ew = [c_ - a_ for a_, c_ in hspans(outline(e), es[1] + (y - hook[1]) / k)]
        check(sp and ew and abs((sp[0][1] - sp[0][0]) - ew[0]) <= 4,
              f'{n}: stem at y {y:.0f} {sp}, want the width of {e}\'s stem there ({ew})')

for suf in ('', '.sc'):
    n, s = 'uni2031' + suf, 'perthousand' + suf
    if not (have(n) and s in HAVE): continue
    p, sp = outline(n), outline(s); step = W(n) - W(s)
    check(ncont(p) == ncont(sp) + 2, f'{n}: {ncont(p)} contours, {s} {ncont(sp)} + 2')
    check(area(pathops.op(sp, p, pathops.PathOp.DIFFERENCE)) < 0.005 * area(sp), f'{n}: does not hold the whole {s}')
    lower = sorted((c for c in sp.contours if c.bounds[1] < sp.bounds[1] + 1), key=lambda c: c.bounds[0])
    check(len(lower) == 2 and abs(step - (lower[1].bounds[0] - lower[0].bounds[0])) <= 1,
          f'{n}: advance grows by {step}, not the step between {s}\'s lower rings')
    if len(lower) == 2:
        lb = lower[1].bounds; ring = pathops.Path()
        for c in sp.contours:
            cb = c.bounds
            if cb[0] >= lb[0] - 0.5 and cb[2] <= lb[2] + 0.5 and cb[1] >= lb[1] - 0.5 and cb[3] <= lb[3] + 0.5: c.draw(ring.getPen())
        moved = pathops.Path(); ring.draw(TransformPen(moved.getPen(), (1, 0, 0, 1, step, 0)))
        d = xor_frac(p, union(sp, moved))
        check(d < 0.01, f'{n}: the new ring is not the last ring of {s} moved {step} ({d:.3%} differs)')

for suf, h in (('', 'hyphen'), ('.case', 'hyphen.case')):
    n, d = 'uni2027' + suf, ('periodcentered' + ('.case.otfeatures' if suf else ''))
    if not (have(n) and d in HAVE and h in HAVE): continue
    b, db, hb_ = outline(n).bounds, outline(d).bounds, outline(h).bounds
    check(abs((b[2] - b[0]) - (db[2] - db[0])) <= 1 and abs((b[3] - b[1]) - (db[3] - db[1])) <= 1, f'{n}: dot {b}, {d} {db}')
    check(abs((b[1] + b[3]) / 2 - (hb_[1] + hb_[3]) / 2) <= 1, f'{n}: centred at {(b[1] + b[3]) / 2:.0f}, {h} at {(hb_[1] + hb_[3]) / 2:.0f}')
    check(b[0] <= 0.6 * db[0] + 1 and W(n) - b[2] <= 0.6 * (W(d) - db[2]) + 1, f'{n}: sidebearings {b[0]:.0f}/{W(n) - b[2]:.0f}, {d} {db[0]:.0f}/{W(d) - db[2]:.0f}')

if have('uni2051'):
    d = xor_frac(outline('uni2051'), union(outline('asterisk'), outline('uni204E')))
    check(d < 0.01 and W('uni2051') == W('asterisk'), f'uni2051: not * over the low asterisk ({d:.3%} differs, advance {W("uni2051")})')

for n, L in (('uni2103', 'C'), ('uni2109', 'F')):
    if not have(n): continue
    p, dg = outline(n), outline('degree'); dx = W(n) - W(L)
    check(W(n) < W('degree') + W(L), f'{n}: advance {W(n)}, not under ° + {L} ({W("degree") + W(L)})')
    d = xor_frac(p, union(dg, outline(L, dx)))
    check(d < 0.01, f'{n}: not ° and {L} at {dx} ({d:.3%} differs)')
    check(ncont(p) == ncont(dg) + ncont(outline(L)), f'{n}: ring and {L} touch ({ncont(p)} contours)')

if have('uni2117'):
    p, cp_ = outline('uni2117'), outline('copyright')
    check(W('uni2117') == W('copyright'), f'uni2117: advance {W("uni2117")}, copyright {W("copyright")}')
    cs = sorted(cp_.contours, key=lambda c: -(c.bounds[2] - c.bounds[0]) * (c.bounds[3] - c.bounds[1]))
    ring = pathops.Path(); [c.draw(ring.getPen()) for c in cs[:2]]; ring.simplify()
    check(area(pathops.op(ring, p, pathops.PathOp.DIFFERENCE)) < 0.005 * area(ring), 'uni2117: does not hold the ring of ©')
    inner = cs[1].bounds
    rest = pathops.op(p, ring, pathops.PathOp.DIFFERENCE); rb = rest.bounds
    check(ncont(rest) == 2 and rb[0] > inner[0] and rb[2] < inner[2] and rb[1] > inner[1] and rb[3] < inner[3],
          f'uni2117: P {rb} ({ncont(rest)} contours) not inside the inner circle {inner}')
    rg = outline('registered'); rcs = sorted(rg.contours, key=lambda c: -(c.bounds[2] - c.bounds[0]) * (c.bounds[3] - c.bounds[1]))
    R = pathops.Path(); [c.draw(R.getPen()) for c in rcs[2:]]; R.simplify(); Rb = R.bounds
    check(abs((rb[3] - rb[1]) - (Rb[3] - Rb[1])) <= 2, f'uni2117: P {rb[3] - rb[1]:.0f} tall, the R of ® {Rb[3] - Rb[1]:.0f}')
    ys = lambda b: b[1] + 0.2 * (b[3] - b[1])
    sp, sR = hspans(rest, ys(rb))[0], hspans(R, ys(Rb))[0]
    check(abs((sp[1] - sp[0]) - (sR[1] - sR[0])) <= 3, f'uni2117: P stem {sp[1] - sp[0]:.0f}, the R of ® {sR[1] - sR[0]:.0f}')

# the same contours at every weight of this slant (the variable font interpolates them)
if MODE == 'full':
    d = os.path.dirname(os.path.abspath(PATH))
    W7 = ['Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']
    sibs = [({'Regular': 'Italic'}.get(w, w + 'Italic') if ITALIC else w) for w in W7]
    paths = [os.path.join(d, f'TorchletteSans-{s}.ttf') for s in sibs]
    if all(os.path.exists(q) for q in paths):
        fonts = [TTFont(q, lazy=True) for q in paths]
        made = sorted(g for g in HAVE if g.split('.')[0] in NAMES.values())
        for g in made:
            counts = [f['glyf'][g].numberOfContours if g in f.getGlyphOrder() else None for f in fonts]
            check(len(set(counts)) == 1, f'{g}: contours across the {"italic" if ITALIC else "upright"} weights {counts}')

# ---- 3. small capitals and case forms ------------------------------------------------
def top(g): return outline(g).bounds[3]
SC = {0x203C: 'exclam', 0x2047: 'question', 0x203D: 'question', 0x2E2E: 'question', 0x201B: 'quoteright',
      0x201F: 'quotedblright', 0x2031: 'perthousand', 0x2E3A: 'emdash', 0x2E3B: 'emdash'}
for feat in ('smcp', 'c2sc'):
    if not kept(feat): continue
    for cp, model in SC.items():
        if not have(NAMES[cp]) or model + '.sc' not in HAVE: continue
        s = shape(chr(cp), {feat: 1})
        check(len(s) == 1 and s[0][0] == NAMES[cp] + '.sc' and abs(top(s[0][0]) - top(model + '.sc')) <= 2,
              f'{feat} U+{cp:04X}: {s}, want {NAMES[cp]}.sc as tall as {model}.sc')
if kept('case'):
    lift = lambda a, b: outline(b).bounds[1] - outline(a).bounds[1]
    for cp, model in ((0x2E3A, 'emdash'), (0x2E3B, 'emdash'), (0x2027, 'hyphen')):
        if not have(NAMES[cp]): continue
        m = shape({'emdash': '\u2014', 'hyphen': '-'}[model], {'case': 1})[0][0]
        s = shape(chr(cp), {'case': 1})
        check(len(s) == 1 and s[0][0] != NAMES[cp] and abs(lift(NAMES[cp], s[0][0]) - lift(model, m)) <= 1,
              f'case U+{cp:04X}: {s}, not raised as {model} -> {m}')

# ---- 4. kerning (from kern.INHERIT) --------------------------------------------------
def kern(text):
    s = shape(text)
    return s[0][1] - W(s[0][0]) if len(s) == 2 else None
KERN = [('A‛', 'A’'), ('‛A', '’A'), ('‟A', '”A'), ('A‟', 'A”'), ('‼J', '!J'), ('Y‼', 'Y!'),
        ('A⁇', 'A?'), ('Y‽', 'Y?'), ('‽T', '?T'), ('⸺T', '—T'), ('L⸺', 'L—'), ('⸻T', '—T'),
        ('A℃', 'A°'), ('℃A', 'CA'), ('A℉', 'A°'), ('℉A', 'FA')]
for new, ref in KERN:
    if not all(have(NAMES[ord(ch)]) for ch in new if ord(ch) in NAMES): continue
    kn, kr = kern(new), kern(ref)
    if not kr: continue
    check(kn is not None and kn != 0 and (kn > 0) == (kr > 0),
          f'KERN {new!r}: {kn}, want the sign of {ref!r} ({kr}) (needs the kern module\'s INHERIT entries)')

# the dashes' edges are the em dash's, so they kern exactly as it does, under case too (where
# the em dash's case form takes its kerning from otfeatures, after the kern module has run)
def kern_f(text, feats):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(HB, b, feats)
    gp = list(zip(b.glyph_infos, b.glyph_positions))
    return gp[0][1].x_advance - W(GO[gp[0][0].codepoint]) if len(gp) == 2 else None
for feats in ({},) + (({'case': 1},) if kept('case') else ()):
    for d in ('\u2E3A', '\u2E3B'):
        if not have(NAMES[ord(d)]): continue
        for x in 'TAVYJ':
            for new, ref in ((d + x, '\u2014' + x), (x + d, x + '\u2014')):
                kn, kr = kern_f(new, feats), kern_f(ref, feats)
                check(kn == kr, f'KERN {new!r} {feats}: {kn}, want the em dash\'s {ref!r} {kr}')

print(f'punctuation {STYLE} {MODE}: {checks - len(fails)}/{checks} checks passed')
for f in fails[:40]:
    print('  FAIL', f)
sys.exit(1 if fails else 0)

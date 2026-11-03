"""Checks of the codekeys module (CP1 CP2 CP3 SH1 SH2 SC1 SC3 ML6 LG4 LG6).

    verify_codekeys.py FONT STYLE full|subset

1. Coverage: ⎋ ⇥ ⌃ ␣ ⇪ ⌦, ▁-█, ♭ ♮ ♯ ♩ ♪ ♫, ▸ and ⤙ each shape to their own glyph with ink,
   alone and between letters, with no features and with the app's. In the web subset ␣,
   the block elements and the music signs may be absent while the Makefile's UNICODES
   leaves them out; the rest must be there.
2. Defaults unchanged: I, l and v shape to themselves with no features and with the app's
   (outside the ss16 contexts below).
3. CP1: ss17, ss18, ss19 give I.serif, l.tail, v.spur (full font only: the web subset
   drops those features); I.serif is wider than I with ink at the cap height and baseline
   beyond the stem; under ss16, I beside l, 1 or | takes the serifs, and It, In, I am, PII do not.
   I.serif is spaced like the plain I: beside l, the ll ligature, | (and H under ss17), on either
   side, the light between the shapes is the plain I's within 6 units (codekeys.py's SPACE_CLIP
   rule), and its serif tips sit inside the plain I's sidebearing.
4. CP2 (ss02): != := give ≠ ≔, space-guarded ~> gives ⇝ (also encoded at U+21DD),
   and <- gives ← through ss16's 102; !==, ::=, :==, x<-1,
   <--, <-> do not give them; with ss02 off nothing changes; ` |-> ` gives ↦ (and ` |- ` ⊢, ` |= ` ⊨ when the font has them).
5. CP3: the keyboard symbols are about cap height tall (⌃ and ␣ excepted), ⌦ is ⌫'s
   width; in an italic ⌦'s right side is vertical (the pictures stand upright).
6. SH1: ▁-█ are 130-unit cells with a bar from 20 to 110 on the baseline, i/8 of 608 tall.
7. SC1 (ss16): F# C# F#4 give the note sharp, Bb Eb the note flat; xF#, F#x, F##, #F, Ab,
   Db, Gb, 8 Eb, Hb and C++ do not; the MIDI lesson's "D E F# G A B C#" and "D–E–F#–G" fire.
8. SH2 (ss16): "b c h w -> b (h w) c" sets every axis letter in small capitals, the arrow
   and tuple spaces, with ss02 on or off; "x -> y", "f(x) -> y", "the cat -> dog" do not.
9. SC3: a figure, space, bit(s)/nat(s)/Sh takes the unit space; "3 bitsy" does not.
10. ML6: argmax, argmin, logsumexp take their operator spacing; torch.argmax, argmaxes,
    xargmax do not.
11. LG4: [M20], [HM45] and "▸ 12. [20]" become a badge (start, small caps and figures, end);
    "[20]", "a[M20]", "[M2]" and "[M200]" do not.
12. With ss16 off, none of the module's ss16 glyphs appears in any of the above.
"""
import os
import sys

import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import kept   # noqa: E402

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']; ORDER = f.getGlyphOrder()
hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(PATH)))
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
NO16 = dict(APP, ss16=0)
ITALIC = STYLE.endswith('Italic'); SUB = MODE == 'subset'
fails = 0; checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('[verify_codekeys FAIL]', *msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(hbfont, b, feats or {})
    return [ORDER[i.codepoint] for i in b.glyph_infos]


def path(g):
    p = pathops.Path(); gs[g].draw(p.getPen(glyphSet=gs)); return p


def spans(g, y):
    p = path(g); r = pathops.Path(); pen = r.getPen()
    pen.moveTo((-3000, y - 0.5)); pen.lineTo((5000, y - 0.5)); pen.lineTo((5000, y + 0.5)); pen.lineTo((-3000, y + 0.5)); pen.closePath()
    return sorted((c.bounds[0], c.bounds[2]) for c in pathops.op(p, r, pathops.PathOp.INTERSECTION).contours)


CH = f['OS/2'].sCapHeight
MAY_MISS = {0x2423} | set(range(0x2581, 0x2589)) | set(range(0x2669, 0x2670))
CPS = [0x238B, 0x21E5, 0x2303, 0x2423, 0x21EA, 0x2326] + list(range(0x2581, 0x2589)) + [0x266D, 0x266E, 0x266F, 0x2669, 0x266A, 0x266B, 0x25B8, 0x2919, 0x21DD]

# 1. coverage
present = set()
for cp in CPS:
    if cp not in cmap:
        check(SUB and cp in MAY_MISS, f'U+{cp:04X} not in the cmap')
        if SUB and cp in MAY_MISS: print(f'  (U+{cp:04X} {chr(cp)} not in the web subset; outside the Makefile UNICODES)')
        continue
    g = cmap[cp]; present.add(cp)
    check(path(g).bounds[2] > path(g).bounds[0], f'U+{cp:04X} {g} has no ink')
    for feats in ({}, APP):
        check(shape(chr(cp), feats) == [g], f'U+{cp:04X} alone under {feats}: {shape(chr(cp), feats)}')
        check(shape('a' + chr(cp) + 'n', feats)[1] == g, f'U+{cp:04X} between letters under {feats}')

# 2. defaults
for ch in 'Ilv':
    for feats in ({}, APP):
        check(shape(ch, feats) == [ch], f'{ch} under {feats}: {shape(ch, feats)}')

# 3. CP1
if kept('ss17', 'ss18', 'ss19'):
    for ch, tag, g in (('I', 'ss17', 'I.serif.codekeys'), ('l', 'ss18', 'l.tail.codekeys'), ('v', 'ss19', 'v.spur.codekeys')):
        check(shape(ch, {tag: 1}) == [g], f'{tag}: {shape(ch, {tag: 1})}')
if 'I.serif.codekeys' in ORDER:
    stem = spans('I', CH / 2)[0]
    for y in (10, CH - 10):
        sp = spans('I.serif.codekeys', y)
        check(sp and sp[0][1] - sp[0][0] > 2.2 * (stem[1] - stem[0]), f'I.serif at {y}: {sp} against stem {stem}')
    check(hmtx['I.serif.codekeys'][0] > hmtx['I'][0], 'I.serif no wider than I')
for t, want in (('Il', ['I.serif.codekeys', None]), ('lI', [None, 'I.serif.codekeys']), ('I1', ['I.serif.codekeys', None]),
                ('|I|', [None, 'I.serif.codekeys', None])):
    got = shape(t, APP)
    check(all(w is None or w == g for w, g in zip(want, got)) and len(got) == len(want), f'ss16 I: {t!r} -> {got}')
for t in ('It', 'In', 'I am', 'Ia', 'AI', 'PII', 'II'):
    check('I.serif.codekeys' not in shape(t, APP), f'ss16 I fires in {t!r}')
# I.serif's spacing (codekeys.py's SPACE_CLIP rule): beside a stem (H, l, the ll ligature, |),
# on either side, the light between the shapes, as shaped with the app's features and kern,
# matches the plain I's within 6 units. The light is the mean over the cap height of each
# row's gap, a row counting up to 1.044 times the plain pair's stem gap. The serif tips sit
# closer than the plain I's stem sidebearing, which is what keeps "Illinois" even.
if 'I.serif.codekeys' in ORDER:
    YS = [CH * (i + .5) / 80 for i in range(80)]
    def edges(g):
        out = []
        for y in YS:
            sp = spans(g, y); out.append((sp[0][0], sp[-1][1]) if sp else None)
        return out
    EDGE = {}
    def pair(text, feats):
        b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(hbfont, b, feats)
        gl = [ORDER[i.codepoint] for i in b.glyph_infos]; adv = b.glyph_positions[0].x_advance
        if len(gl) != 2: return gl, None
        for g in gl: EDGE.setdefault(g, edges(g))
        return gl, [adv + q[0] - r[1] for r, q in zip(EDGE[gl[0]], EDGE[gl[1]]) if r and q]
    def light(gaps, stem): return sum(min(x, 1.044 * stem) for x in gaps) / len(gaps)
    PLAIN = dict(APP, ss16=0, kern=1)
    lsb_I = hmtx['I'][1]; ink = spans('I.serif.codekeys', 10)[0]
    tips = (hmtx['I.serif.codekeys'][1], hmtx['I.serif.codekeys'][0] - hmtx['I.serif.codekeys'][1] - (ink[1] - ink[0]))
    if not ITALIC: check(all(0.25 * lsb_I < s < lsb_I for s in tips), f'I.serif tip sidebearings {tips} against the plain I {lsb_I}')
    # ss16 makes the serifed I beside l, ll, |; ss17 (full font only) beside H
    cases = [(t, dict(APP, kern=1)) for t in ('Il', 'lI', 'Ill', 'I|', '|I')]
    if kept('ss17'): cases += [(t, dict(APP, ss17=1, kern=1)) for t in ('IH', 'HI')]
    for t, feats in cases:
        gl, g = pair(t, feats); _, ref = pair(t[:2], PLAIN)
        check(g is not None and 'I.serif.codekeys' in gl, f'{t!r} under {feats}: {gl}')
        if g is None: continue
        stem = ref[len(ref) // 2]; d = light(g, stem) - light(ref, stem)
        check(abs(d) <= 6, f'I.serif spacing {t!r}: light {light(g, stem):.1f} against the plain I {light(ref, stem):.1f}')
        print(f'  I.serif spacing {t!r} {"+".join(gl)}: light {light(g, stem):.1f}, plain I {light(ref, stem):.1f} ({d:+.1f})')

# 4. CP2
SS02 = {'ss02': 1}
check(cmap.get(0x2190) is None or cmap.get(0x2190) in shape('y <- x', APP), 'y <- x under the app features (ss16 102)')
for t, g in (('a != b', 'notequal'),) + ((('x := 3', 'uni2254.ss02.codekeys'),) if 0x2254 in cmap else ()):
    for feats in (SS02, APP):
        check(g in shape(t, feats), f'ss02 {t!r} under {feats}: {shape(t, feats)}')
    check(g not in shape(t, {}), f'{t!r} changes with ss02 off')
for t, g in (('a !== b', 'notequal'), ('x ::= y', 'uni2254.ss02.codekeys'), ('x :== y', 'uni2254.ss02.codekeys'), ('x<-1', cmap.get(0x2190)),
             ('a <-- b', cmap.get(0x2190)), ('a <-> b', cmap.get(0x2190))):
    check(g not in shape(t, APP), f'ss02 negative {t!r}: {shape(t, APP)}')
for cp, t in ((0x21A6, 'f |-> g'), (0x22A2, 'P |- Q'), (0x22A8, 'M |= P')):
    if cp in cmap: check(f'uni{cp:04X}.ss02.codekeys' in shape(t, SS02), f'ss02 {t!r}: {shape(t, SS02)}')
for cp, t in ((0x22A2, '|---|'), (0x22A8, 'x|=y'), (0x22A2, 'a|-b')):
    if cp in cmap: check(f'uni{cp:04X}.ss02.codekeys' not in shape(t, APP), f'ss02 turnstile negative {t!r}')

# CP2's wave arrow is a genuine encoded sign, not a missing-glyph alias.
# Its ligature needs a space on both sides; identifiers/near misses stay literal.
if 0x21DD in cmap:
    wave = cmap[0x21DD]
    check(path(wave).area > 0, 'U+21DD has no ink')
    check(shape('⇝', {}) == [wave] and wave in shape('a⇝b', APP), 'U+21DD does not shape directly')
    check(hmtx[wave][0] == hmtx['arrowright'][0], 'U+21DD should use the native arrow cell')
    if kept('ss02'):
        out = 'uni21DD.ss02.codekeys'
        check(out in shape('a ~> b', SS02), 'space-guarded ~> does not shape')
        check(out not in shape('a ~> b', dict(APP, ss02=0)), '~> shapes with ss02 off')
        check(path(out).area == path(wave).area and hmtx[out] == hmtx[wave], 'wave-arrow ligature differs from its encoded sign')
        for text in ('~> b', 'a ~>', 'a~>b', 'a ~>b', 'a~> b', 'a ~~> b', 'a ~>> b', 'a ~-> b', 'file_~>_name'):
            check(out not in shape(text, APP), f'wave-arrow negative {text!r}: {shape(text, APP)}')
else:
    check(False, 'font missing approved CP2 U+21DD')

# 5. CP3
for cp in (0x238B, 0x21E5, 0x21EA, 0x2326):
    if cp in cmap:
        b = path(cmap[cp]).bounds; check((0.5 if cp == 0x21E5 else 0.7) * CH < b[3] - b[1] < 1.1 * CH, f'U+{cp:04X} height {b[3] - b[1]:.0f}, cap {CH}')
if 0x2326 in cmap and 0x232B in cmap:
    w1, w2 = [path(cmap[c]).bounds for c in (0x2326, 0x232B)]
    check(abs((w1[2] - w1[0]) - (w2[2] - w2[0])) < 4, f'⌦ width {w1[2] - w1[0]:.0f} vs ⌫ {w2[2] - w2[0]:.0f}')
    r0, r1 = spans(cmap[0x2326], 0.15 * CH)[-1][1], spans(cmap[0x2326], 0.85 * CH)[-1][1]
    check(abs(r0 - r1) < 4, f'⌦ right side not vertical ({r0:.0f} vs {r1:.0f})')

# Escape's arrow and ring opening must be centred on the same upper-left
# diagonal, not just look aligned at one raster size. Reflection of the decoded
# filled glyph about that diagonal allows a small integer-encoding boundary area.
if 0x238B in cmap:
    esc = path(cmap[0x238B]); eb = esc.bounds
    centre_sum = eb[0] + CH  # cx + cy; the ring is one cap-height in diameter
    reflected = pathops.Path()
    esc.draw(TransformPen(reflected.getPen(), (0, -1, -1, 0, centre_sum, centre_sum)))
    asymmetry = abs(pathops.op(esc, reflected, pathops.PathOp.XOR).area)
    check(asymmetry <= 2 * CH, f'Escape arrow/opening diagonal asymmetry {asymmetry:.1f} square units')

# 6. SH1
for i in range(1, 9):
    cp = 0x2580 + i
    if cp not in cmap: continue
    b = path(cmap[cp]).bounds; want = round(608 * i / 8)
    check(hmtx[cmap[cp]][0] == 130 and abs(b[1]) < 1 and abs(b[3] - want) <= 1, f'U+{cp:04X}: advance {hmtx[cmap[cp]][0]}, bounds {b}')
    if not ITALIC: check(abs(b[0] - 20) <= 1 and abs(b[2] - 110) <= 1, f'U+{cp:04X} bar {b[0]}..{b[2]}')

# 7. SC1
SH, FL = 'sharp.note.codekeys', 'flat.note.codekeys'
for t, g in (('F#', SH), ('play C# now', SH), ('F#4', SH), ('(G#)', SH), ('Bb', FL), ('play Eb.', FL),
             ('for D major: D E F# G A B C#.', SH), ('walks up D–E–F#–G sometime', SH), ('every C# is 1', SH)):
    check(g in shape(t, APP), f'note {t!r}: {shape(t, APP)}')
    check(g not in shape(t, NO16), f'note {t!r} with ss16 off')
for t in ('xF#', 'F#x', 'F##', '#F', 'Ab', 'Db', 'Gb', '8 Eb', 'Hb', 'C++', 'Bbq', 'aBb', 'F#_1'):
    check(not {SH, FL} & set(shape(t, APP)), f'note negative {t!r}: {shape(t, APP)}')

# 8. SH2
pat = 'the pattern b c h w -> b (h w) c here'
for t in ('The pattern b c h w -> b (h w) c flattens it.', "'b (h w) c -> b h w c'"):
    got = shape(t, APP)
    check(sum(g.endswith('.ein.codekeys') and len(g) == 14 for g in got) == 8, f'einops in prose {t!r}: {got}')
for feats in (APP, dict(APP, ss02=0)):
    got = shape(pat, feats)
    check(got.count('arrow.ein.codekeys') == 1 and sum(g.endswith('.ein.codekeys') and len(g) == 14 for g in got) == 8
          and got.count('space.ein.codekeys') == 8, f'einops {feats}: {got}')
check(not any(g.endswith('.ein.codekeys') for g in shape(pat, NO16)), 'einops with ss16 off')
for t in ('x -> y', 'f(x) -> y', 'the cat -> dog', 'a -> b c', 'so cab b -> x', 'so b c -> cat'):
    check(not any(g.endswith('.ein.codekeys') for g in shape(t, APP)), f'einops negative {t!r}: {shape(t, APP)}')

# 9. SC3
for t in ('3.2 bits', '1 bit', '2 nats', '5 Sh'):
    check('space.unit' in shape(t, APP), f'units {t!r}: {shape(t, APP)}')
for t in ('3 bitsy', '3 natural', 'bits'):
    check('space.unit' not in shape(t, APP), f'units negative {t!r}')

# 10. ML6
for t, g in (('argmax', 'g.argop.codekeys'), ('the argmin of', 'g.argop.codekeys'), ('(argmax)', 'g.argop.codekeys'),
             ('logsumexp', 'm.lse.codekeys')):
    check(g in shape(t, APP), f'operator {t!r}: {shape(t, APP)}')
    check(g not in shape(t, NO16), f'operator {t!r} with ss16 off')
for t in ('torch.argmax', 'argmaxes', 'xargmax', 'argmax_idx', 'Argmax'):
    check(not {'g.argop.codekeys', 'g.lse.codekeys'} & set(shape(t, APP)), f'operator negative {t!r}: {shape(t, APP)}')

# 11. LG4
for t, n in (('[M20]', 3), ('[HM45]', 4), ('▸ 12. [20]', 2)):
    got = shape(t, APP)
    check(got.count('rate.start.codekeys') == 1 and got.count('rate.end.codekeys') == 1
          and sum(g.endswith('.rate.codekeys') for g in got) == n, f'rating {t!r}: {got}')
    check(not any('rate.' in g for g in shape(t, NO16)), f'rating {t!r} with ss16 off')
# Every rating cell has real vertical air between its lettering and the
# horizontal rails. Inspect decoded contours, including all digits, not a
# particular shaped rating. Rails are thin horizontal rectangles; the letter's
# outer contour spans more than 100 units in every family weight.
for g in ['M.rate.codekeys', 'H.rate.codekeys'] + [d + '.rate.codekeys' for d in 'zero one two three four five six seven eight nine'.split()]:
    if g not in ORDER:
        check(SUB and not kept('ss16'), f'missing rating cell {g}')
        continue
    contours = list(path(g).contours)
    lettering = [c.bounds for c in contours if c.bounds[3] - c.bounds[1] > 100]
    lower = [c.bounds[3] for c in contours if c.bounds[3] - c.bounds[1] < 100 and c.bounds[3] < 0]
    upper = [c.bounds[1] for c in contours if c.bounds[3] - c.bounds[1] < 100 and c.bounds[1] > 550]
    check(bool(lettering and lower and upper), f'{g}: missing separated lettering/rails')
    if lettering and lower and upper:
        bottom = min(c[1] for c in lettering) - max(lower)
        top = min(upper) - max(c[3] for c in lettering)
        check(min(bottom, top) >= 0.14 * CH, f'{g}: rating rail clearance {bottom:.1f}/{top:.1f}')
for t in ('[20]', 'see [20].', 'a[M20]', '[M2]', '[M200]', '13. [20]'):
    check(not any('rate.' in g for g in shape(t, APP)), f'rating negative {t!r}: {shape(t, APP)}')

print(f'verify_codekeys {STYLE} {MODE}: {checks} checks, {fails} failures ({len(present)} of {len(CPS)} code points present)')
sys.exit(1 if fails else 0)

"""HarfBuzz check of the symbols module: arrows, operators, double-struck capitals,
Unicode spaces and joiners.

    verify_symbols.py FONT STYLE full|subset

The cases come from Codex's acceptance corpus (rows ArrowCore, CommonMath,
DoubleStruck, Primes, long-arrows-subset, Greek-versus-math-Sigma (the sum only),
space-control-*, prose-versus-literal-contexts), shaped under the app's settings
(ss01 ss02 ss16 onum pnum) and with no features.

1. Coverage: every promised character shapes to one real glyph with ink (not
   .notdef, not a space), in the full font and in the web subset. The subset keeps
   them only when the Makefile's UNICODES covers U+2308-230B, U+27F0-27FF and
   U+2934-2935.
2. Identity: U+2192 is the -> arrow ss02 makes (`arrowright`); no two promised
   characters share an outline (distinct semantic forms); the sum U+2211 is still
   `summation`, descending below the baseline; | and the divides sign differ.
3. Geometry: binary operators and relations sit on the math axis (the minus's
   centre) within 6 units; relations take the 600-unit cell of = < > (but ∪ ∩ ⊙ ⊗ ⊕,
   which the mathglyphs module, when built, redraws at TeX's size); arrows of
   one direction family share the shaft weight (the minus's bar); no new glyph
   leaves the hhea, typo or win metrics or reaches past the font's tallest and
   deepest letters.
4. Spaces and joiners: shaped widths of A<space>B are A + B + the space's semantic
   width (thin 1/5 em, hair 1/10, narrow no-break = thin, figure = tabular figure,
   punctuation = period (within 5: Mulish's own U+2008 is 225, the period 222), en, em, no-break = space); ZWSP, ZWNJ, ZWJ, word joiner,
   BOM and soft hyphen add no advance and no ink.
5. Negative cases: the non-breaking hyphen stays a hyphen where ss16 turns - into a
   minus; ss02's -> <= >= and 28x28 still form; nothing here touches letters.
6. Double-struck ℝ ℕ ℤ ℚ ℂ (Noto Sans Math's design on Torchlette's capitals): each stands
   on the baseline at its capital's cap height, no narrower than the capital and at most
   30% wider. Every stroke is one hairline T, ℕ's stem: between 0.33 and 0.62 of H's stem
   (Noto's is 0.59 of its stem; above Regular the hairline grows as the root of the stem).
   On a scanline through the letter each doubled stroke (ℝ's stem, bowl and leg, ℕ's and
   ℤ's diagonal, ℚ's two sides, ℂ's left side) is two hairlines (within 3 units of T) with
   an open counter between of at least 0.9 x 67/53 T (Noto's gap, which never closes); the
   horizontals (ℤ's bars, ℝ's bars, the tops and bottoms of ℚ and ℂ) are hairlines too,
   within 25% of T and within 4 of each other; no span on these lines is under 0.75 T.
   Doubled strokes are closed at their ends (ℝ's stem and leg are one span each at the
   baseline); ℕ's stems are single. Each glyph has the contour count of its design (ℝ 5,
   ℕ 2, ℤ 2, ℚ 4, ℂ 2), at every weight.
7. Harpoons ↼ ↽ ↾ ↿ ⇀ ⇁ ⇂ ⇃ and the pairs ⇌ ⇋: each harpoon is one contour holding one
   shaft of the minus's weight (singles on the axis, the pairs' shafts at the bars of =,
   within 3 units). Turned so it points along +x with its barb above, the shaft runs on to
   the tip: along the shaft's far edge (2 units in) the ink is one interval that ends
   within 3 units of the tip, and 2 units behind the tip the ink reaches down to the far
   edge (within 3), so the barb's outer tip and the shaft's end are one point. The barb
   rises at least 100 units above the shaft on its own side and nothing hangs below the
   far edge. (The first harpoons failed this: the barb was half of the -> head cut at the
   centre line and the shaft stopped 80 SM short of the tip under it.)
8. Paired arrows ⇄ ⇆ ⇅ ⇵: two contours at least 0.6 of a bar apart, and each head opens:
   a scan across the head finds the two wings apart from the shaft (three spans), so no
   head fills in solid (the first pair did in Black, its 0.6-reach head shorter than the
   notch is deep).
9. Circle arrows ↻ ↺ and semicircle arrows ↶ ↷: each is one contour, ↺ is ↻ mirrored and ↷
   is ↶ mirrored. The open circle of ↻ ↺ is centred: across its advance (within 2 units,
   unslanted about 252 in an italic) and on half the cap height (within 3), where a scan
   finds the ring's two sides, each a bar wide (within 3). Each head is centred on the
   stroke: turned to some direction, scans across it find three spans (wing, shaft, wing)
   over at least 0.3 of the bar's width, the middle one a bar wide (within 4) and centred
   between the wings' outer edges (within 4). (The first circle arrows pointed the head along
   the tangent at the arc's end and let the arc curve on under it: the inner wing lay along
   the stroke and the outer one stood off it, so no direction gave a centred shaft.)
"""
import sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen

PATH, STYLE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
f = TTFont(PATH); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']
face = hb.Face(hb.Blob.from_file_path(PATH)); font = hb.Font(face)
APP = {'ss01': 1, 'ss02': 1, 'ss16': 1, 'onum': 1, 'pnum': 1}
fails = 0; checks = 0


def check(ok, *msg):
    global fails, checks
    checks += 1
    if not ok: fails += 1; print('FAIL', *msg)


def shape(text, feats=None):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(font, b, feats or {})
    return [(font.get_glyph_name(i.codepoint), p.x_advance) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def bounds(g):
    bp = BoundsPen(gs); gs[g].draw(bp); return bp.bounds


def outline(g):
    rp = RecordingPen(); gs[g].draw(rp); return tuple((op, tuple(tuple(q) if q else q for q in a)) for op, a in rp.value)


# ---- 1. coverage ------------------------------------------------------------------
ROWS = {
    'ArrowCore': '←↑→↓↔↕↖↗↘↙↦↤↩↪↶↷↺↻⇒⇐⇑⇓⇔⇕⇄⇆⇋⇌⟵⟶⟷⟸⟹⟺⤴⤵',
    'ScopeArrows': '⟼',
    'Harpoons': '↼↽↾↿⇀⇁⇂⇃⇅⇵',
    'CommonMath': '∈∉∀∃∄∇∂⋅∘∗⊙⊗⊕‖∣∼≃≅≡∝≪≫⊂⊆⊃⊇∪∩∧∨¬⊤⊥⌊⌋⌈⌉⋯⋮⋱≔≕∓±×÷−·∑∏∫√∞≈≠≤≥∅∆⟨⟩∠∴∵',
    'ScopeMath': '∋∙≡‰°',
    'DoubleStruck': 'ℝℕℤℚℂ',
    'Primes': '′″‴⁗‵‶‷',
    'long-arrows-subset': '←→↔⟵⟶⟷⟸⟹⟺',
}
promised = []
for row, text in ROWS.items():
    for feats in (None, APP):
        for ch in text:
            out = shape(ch, feats)
            ok = len(out) == 1 and out[0][0] != '.notdef' and out[0][1] > 0 and bounds(out[0][0]) is not None
            check(ok, f'{row}: U+{ord(ch):04X} {ch} -> {out} ({"app" if feats else "plain"})')
    promised += [ch for ch in text if ch not in promised]
print(f'coverage: {len(promised)} characters, plain and under {" ".join(APP)}')

# ---- 2. identity ------------------------------------------------------------------
check(shape('→') == shape('->', {'ss02': 1})[:1] and shape('→')[0][0] == 'arrowright',
      f'U+2192 {shape("→")} vs ss02 -> {shape("->", {"ss02": 1})}')
check(shape('a → b', APP)[2][0] == 'arrowright', f'U+2192 in prose under ss16: {shape("a → b", APP)}')
seen = {}
for ch in promised:
    g = cmap.get(ord(ch))
    if g is None: continue
    o = outline(g)
    check(o not in seen, f'{ch} U+{ord(ch):04X} ({g}) has the same outline as {seen.get(o)}')
    seen.setdefault(o, ch)
sg = cmap.get(0x2211)
check(sg == 'summation' and bounds(sg)[1] < -100, f'U+2211 should stay the descending summation: {sg} {sg and bounds(sg)}')
check(outline(cmap[0x2223]) != outline(cmap[0x7C]) or hmtx[cmap[0x2223]][0] != hmtx[cmap[0x7C]][0], 'divides is the bar')

# ---- 3. geometry ------------------------------------------------------------------
mb = bounds('minus'); AXIS = (mb[1] + mb[3]) / 2; BAR = mb[3] - mb[1]
ON_AXIS = '+−×÷=≠≈∼≃≅≡∝≪≫∈∉∋⊂⊃∪∩∧∨⊙⊗⊕∘⋅∗⋯→←↔↦↤⟵⟶⟷⟸⟹⟺⟼⇒⇐⇔⇄⇆⇋⇌⇅⇵↑↓↕⇑⇓⇕↖↗↘↙'
for ch in ON_AXIS:
    if ord(ch) not in cmap: continue
    b = bounds(cmap[ord(ch)]); c = (b[1] + b[3]) / 2
    check(abs(c - AXIS) <= 6, f'{ch} off the math axis: centre {c:.1f} vs {AXIS:.1f}')
REL = '=<>≤≥≠≈∼≃≅≡∝≪≫∈∉∋⊂⊃⊆⊇∪∩∧∨⊙⊗⊕⊤⊥∠∗'
cell = hmtx[cmap[ord('=')]][0]
MATHGLYPHS_SIZED = set('∪∩⊙⊗⊕') if 'uni22C3' in gs else set()   # mathglyphs redraws these larger (TeX's size)
for ch in REL:
    if ord(ch) not in cmap or ch in MATHGLYPHS_SIZED: continue
    check(hmtx[cmap[ord(ch)]][0] == cell, f'{ch} advance {hmtx[cmap[ord(ch)]][0]} != {cell}')
# shaft weight: horizontal arrows' ink across the shaft at a third of their length
from fontTools.pens.basePen import BasePen
class Flat(BasePen):
    """Outline as polygons (curves sampled), for crossing counts; with shear k the outline
    is unslanted first (x - k y), so an italic's strokes stand upright for the columns."""
    def __init__(s, k=0): super().__init__(gs); s.polys = []; s.cur = []; s.k = k
    def _pt(s, p): return (p[0] - s.k * p[1], p[1])
    def _moveTo(s, p): s.cur = [s._pt(p)]; s.polys.append(s.cur)
    def _lineTo(s, p): s.cur.append(s._pt(p))
    def _qCurveToOne(s, c, p):
        a = s.cur[-1]; c = s._pt(c); p = s._pt(p)
        for k in range(1, 17):
            t = k / 16; s.cur.append(((1-t)**2*a[0] + 2*(1-t)*t*c[0] + t*t*p[0], (1-t)**2*a[1] + 2*(1-t)*t*c[1] + t*t*p[1]))
    def _curveToOne(s, c1, c2, p):
        a = s.cur[-1]; c1 = s._pt(c1); c2 = s._pt(c2); p = s._pt(p)
        for k in range(1, 17):
            t = k / 16; u = 1 - t
            s.cur.append((u**3*a[0] + 3*u*u*t*c1[0] + 3*u*t*t*c2[0] + t**3*p[0], u**3*a[1] + 3*u*u*t*c1[1] + 3*u*t*t*c2[1] + t**3*p[1]))
def vspan(g, x, k=0):
    """Ink intervals of glyph g along the vertical line at x (nonzero winding)."""
    fp = Flat(k); gs[g].draw(fp); hits = []
    for poly in fp.polys:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if (a[0] <= x < b[0]) or (b[0] <= x < a[0]):
                y = a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]); hits.append((y, 1 if b[0] > a[0] else -1))
    hits.sort(); out = []; w = 0; y0 = None
    for y, d in hits:
        if w == 0: y0 = y
        w += d
        if w == 0: out.append((y0, y))
    return out
for ch in '→←↔⟵⟶⟷↦↤⟼↪↩':
    if ord(ch) not in cmap: continue
    g = cmap[ord(ch)]; b = bounds(g); x = b[0] + (b[2] - b[0]) * 0.5
    sp = [s for s in vspan(g, x) if s[0] <= AXIS <= s[1]]
    check(len(sp) == 1 and abs((sp[0][1] - sp[0][0]) - BAR) <= 2, f'{ch} shaft {sp} vs bar {BAR}')
# vertical extents
hh, os2 = f['hhea'], f['OS/2']
top_lim = min(hh.ascent, os2.sTypoAscender, os2.usWinAscent)
bot_lim = max(hh.descent, os2.sTypoDescender, -os2.usWinDescent)
letters = [cmap[u] for u in list(range(0x41, 0x5B)) + list(range(0x61, 0x7B)) + [0xC5, 0xC9] if u in cmap]
L_top = max(bounds(g)[3] for g in letters); L_bot = min(bounds(g)[1] for g in letters)
for ch in promised:
    if ord(ch) not in cmap: continue
    b = bounds(cmap[ord(ch)])
    check(bot_lim <= b[1] and b[3] <= top_lim, f'{ch} {b} outside the vertical metrics {bot_lim}..{top_lim}')
    check(L_bot - 2 <= b[1] and b[3] <= L_top + 2, f'{ch} {b} beyond the letters {L_bot}..{L_top}')
print(f'geometry: {len(ON_AXIS)} on the axis ({AXIS}), {len(REL)} in the {cell} cell, extents {L_bot}..{L_top}')

# ---- 4. spaces and joiners --------------------------------------------------------
adv = lambda t, feats=None: sum(a for _, a in shape(t, feats))
AB = adv('AB')
upem = face.upem
tab = shape('0', {'tnum': 1, 'lnum': 1})[0][1]
WANT = {0x2009: (upem / 5, 12), 0x200A: (upem / 10, 12), 0x202F: (shape(' ')[0][1], 0),
        0x2007: (tab, 0), 0x2008: (shape('.')[0][1], 5), 0x2002: (upem / 2, 0), 0x2003: (upem, 0),
        0x00A0: (shape(' ')[0][1], 0)}
for u, (w, tol) in WANT.items():
    for feats in (None, APP):
        got = adv(f'A{chr(u)}B', feats) - adv('AB', feats)
        out = shape(f'A{chr(u)}B', feats)
        check(abs(got - w) <= tol, f'U+{u:04X} width {got}, want {w}')
        check(bounds(out[1][0]) is None, f'U+{u:04X} has ink: {out}')
for u in (0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x00AD):
    for feats in (None, APP):
        out = shape(f'A{chr(u)}B', feats)
        got = sum(a for _, a in out) - adv('AB', feats)
        ink = [g for g, _ in out[1:-1] if bounds(g) is not None]
        check(got == 0 and not ink and out[0][0] == 'A' and out[-1][0] == 'B', f'U+{u:04X} not zero-width/ink-free: {out}')
print(f'spaces: {len(WANT)} widths, 6 zero-width controls')

# ---- 5. negative cases ---------------------------------------------------------------
nb = shape('x ‑1', APP); hy = shape('x -1', APP)
check(nb[2][0] != hy[2][0] and outline(nb[2][0]) == outline('hyphen'),
      f'U+2011 should stay a hyphen where ss16 makes a minus: {nb} vs {hy}')
pv = shape('output vector forward backward residual -> <= >= 28x28', APP)
names = [g for g, _ in pv]
for want in ('arrowright', 'lessequal', 'greaterequal'):
    check(want in names, f'prose-versus-literal: {want} missing from {names}')
check('.notdef' not in names and any(g.startswith('multiply') for g in names), f'prose-versus-literal: {names}')
check(shape('->') == [('hyphen', hmtx['hyphen'][0]), ('greater', hmtx['greater'][0])], f'-> without ss02: {shape("->")}')
check(shape('Σ∑')[1][0] == 'summation', 'sum after sigma')

# ---- 6. double-struck capitals -------------------------------------------------------
import math
K_IT = math.tan(math.radians(-f['post'].italicAngle))          # the italic's lean, 0 in an upright
def hspan(g, y):
    """Ink intervals of glyph g along the horizontal line at y (nonzero winding), the
    outline unslanted first."""
    fp = Flat(K_IT); gs[g].draw(fp); hits = []
    for poly in fp.polys:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                x = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]); hits.append((x, 1 if b[1] > a[1] else -1))
    hits.sort(); out = []; w = 0; x0 = None
    for x, d in hits:
        if w == 0: x0 = x
        w += d
        if w == 0: out.append((x0, x))
    return out
wid = lambda s: s[1] - s[0]
DS = {ch: cmap.get(ord(ch)) for ch in 'ℝℕℤℚℂ'}
DS_CONTOURS = {'ℝ': 5, 'ℕ': 2, 'ℤ': 2, 'ℚ': 4, 'ℂ': 2}
if all(DS.values()):
    H = bounds('H')[3]
    for ds, cap in zip('ℝℕℤℚℂ', 'RNZQC'):
        a, b = bounds(DS[ds]), bounds(cmap[ord(cap)])
        check(abs(a[1] - b[1]) <= 1 and abs(a[3] - b[3]) <= 1, f'{ds} {a} not on {cap}\'s baseline and cap height {b}')
        check((b[2] - b[0]) - 1 <= (a[2] - a[0]) <= 1.3 * (b[2] - b[0]), f'{ds} width {a[2] - a[0]} vs {cap} {b[2] - b[0]}')
        check(hmtx[cmap[ord(cap)]][0] - 1 <= hmtx[DS[ds]][0] <= 1.3 * hmtx[cmap[ord(cap)]][0], f'{ds} advance {hmtx[DS[ds]][0]} vs {cap} {hmtx[cmap[ord(cap)]][0]}')
        n = f['glyf'][DS[ds]].numberOfContours
        check(n == DS_CONTOURS[ds], f'{ds}: {n} contours, not {DS_CONTOURS[ds]} (a counter closed or split)')
    stem = wid(hspan(cmap[ord('H')], 0.25 * H)[0])
    N = hspan(DS['ℕ'], H / 2)
    check(len(N) == 4, f'ℕ at mid-height should be stem, two diagonal strokes, stem: {N}')
    T = wid(N[0]) if N else 0                                     # the hairline, from ℕ's left stem
    C_MIN = 0.9 * T * 67 / 53
    check(0.33 * stem <= T <= 0.62 * stem, f'hairline {T:.1f} vs the stem {stem:.1f}: not 0.33-0.62 of it')
    def pair(name, spans, i, what):
        """spans[i] and spans[i+1] are a doubled stroke: two hairlines, an open counter between."""
        if len(spans) <= i + 1: return
        s1, s2 = spans[i], spans[i + 1]
        check(abs(wid(s1) - wid(s2)) <= 3, f'{name} {what}: strokes {wid(s1):.1f} and {wid(s2):.1f} differ')
        check(s2[0] - s1[1] >= C_MIN, f'{name} {what}: counter {s2[0] - s1[1]:.1f} under {C_MIN:.0f}')
    def vert(name, span, what, tol=3):
        check(abs(wid(span) - T) <= tol, f'{name} {what}: {wid(span):.1f} is not the hairline {T:.1f}')
    if len(N) == 4:
        vert('ℕ', N[3], 'right stem'); pair('ℕ', N, 1, 'diagonal')
        check(0.9 * T <= wid(N[1]) <= 1.6 * T, f'ℕ diagonal stroke {wid(N[1]):.1f} vs hairline {T:.1f}')
    Z = hspan(DS['ℤ'], H / 2)
    check(len(Z) == 2, f'ℤ at mid-height should be the two diagonal strokes: {Z}')
    if len(Z) == 2: pair('ℤ', Z, 0, 'diagonal'); check(0.9 * T <= wid(Z[0]) <= 1.6 * T, f'ℤ diagonal stroke {wid(Z[0]):.1f} vs {T:.1f}')
    R = hspan(DS['ℝ'], 0.7 * H)
    check(len(R) == 4, f'ℝ through the bowl should be two stem strokes, the inline and the bowl: {R}')
    if len(R) == 4:
        for k, w in ((0, 'stem'), (1, 'stem'), (2, 'inline'), (3, 'bowl')): vert('ℝ', R[k], w, 4 if k == 3 else 3)
        pair('ℝ', R, 0, 'stem')
        check(R[3][0] - R[2][1] >= C_MIN, f'ℝ bowl crescent {R[3][0] - R[2][1]:.1f} under {C_MIN:.0f}')
        check(R[2][0] - R[1][1] >= C_MIN, f'ℝ bowl counter {R[2][0] - R[1][1]:.1f} under {C_MIN:.0f}')
    Rl = hspan(DS['ℝ'], 0.12 * H)
    check(len(Rl) == 4, f'ℝ near the baseline should be two stem strokes and two leg strokes: {Rl}')
    if len(Rl) == 4: pair('ℝ', Rl, 0, 'stem near the baseline'); pair('ℝ', Rl, 2, 'leg near the baseline')
    R0 = hspan(DS['ℝ'], 2)
    check(len(R0) == 2, f'ℝ at the baseline should be the closed stem and the closed leg: {R0}')
    qb = bounds(DS['ℚ']); ob = bounds('O'); cy = (ob[1] + ob[3]) / 2
    Q = hspan(DS['ℚ'], cy)
    check(len(Q) == 4, f'ℚ at mid-height should be outer, inline, inline, outer: {Q}')
    if len(Q) == 4:
        for k in range(4): vert('ℚ', Q[k], f'stroke {k + 1}')
        pair('ℚ', Q, 0, 'left side'); pair('ℚ', Q, 2, 'right side')
    cb_ = bounds(DS['ℂ']); cyc = (cb_[1] + cb_[3]) / 2
    Cc = hspan(DS['ℂ'], cyc)
    check(len(Cc) == 2, f'ℂ at mid-height should be the outer and inner left strokes: {Cc}')
    if len(Cc) == 2: vert('ℂ', Cc[0], 'outer', 6); vert('ℂ', Cc[1], 'inline'); pair('ℂ', Cc, 0, 'left side')
    # horizontals: hairlines too, alike everywhere
    zb = bounds(DS['ℤ']); zw = zb[2] - zb[0]; zb = (zb[0] - K_IT * H / 2, zb[1], zb[2] - K_IT * H / 2, zb[3])   # about mid-height, unslanted
    zc = [vspan(DS['ℤ'], zb[0] + 0.85 * zw, K_IT)[0], vspan(DS['ℤ'], zb[0] + 0.15 * zw, K_IT)[-1]]   # bottom bar right of the diagonal's foot, top bar left of its head
    rc = vspan(DS['ℝ'], R[1][1] + 0.5 * C_MIN if len(R) == 4 else bounds(DS['ℝ'])[0] + 250, K_IT)   # through the bowl's counter, clear of the leg's junction
    qc = vspan(DS['ℚ'], (Q[1][1] + Q[2][0]) / 2 if len(Q) == 4 else (ob[0] + ob[2]) / 2, K_IT); cc = vspan(DS['ℂ'], (Cc[1][1] + 120) if len(Cc) == 2 else (cb_[0] + cb_[2]) / 2, K_IT)
    hz = {'ℤ bottom bar': zc[0] if zc else None, 'ℤ top bar': zc[-1] if zc else None,
          'ℝ middle bar': rc[-2] if len(rc) >= 2 else None, 'ℝ top bar': rc[-1] if rc else None,
          'ℚ bottom': qc[0] if qc else None, 'ℚ top': qc[-1] if qc else None,
          'ℂ bottom': cc[0] if cc else None, 'ℂ top': cc[-1] if cc else None}
    ths = [wid(s) for s in hz.values() if s]
    TH = sorted(ths)[len(ths) // 2] if ths else 0
    check(0.75 * T <= TH <= 1.25 * T, f'horizontal stroke {TH:.1f} vs the hairline {T:.1f}')
    for k, s in hz.items():
        check(s is not None and abs(wid(s) - TH) <= 4, f'{k}: {s and wid(s):.1f} is not the horizontal hairline {TH:.1f}' if s else f'{k}: no ink')
    for name, spans in (('ℕ', N), ('ℤ', Z), ('ℝ', R), ('ℚ', Q), ('ℂ', Cc)):
        for s in spans: check(wid(s) >= 0.75 * T, f'{name}: span {s} is under the hairline ({wid(s):.1f} < 0.75 x {T:.1f})')
    print(f'double-struck: hairline {T:.1f} (H stem {stem:.1f}), horizontal {TH:.1f}, counters >= {C_MIN:.0f}')
else:
    check(False, f'double-struck letters unmapped: {DS}')

# ---- 7. harpoons ----------------------------------------------------------------------
def scan(polys, v, horizontal):
    """Ink intervals (nonzero winding) along y = v (horizontal) or x = v."""
    hits = []
    for poly in polys:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            pa, pb = (a[1], b[1]) if horizontal else (a[0], b[0])
            qa, qb = (a[0], b[0]) if horizontal else (a[1], b[1])
            if (pa <= v < pb) or (pb <= v < pa):
                hits.append((qa + (v - pa) * (qb - qa) / (pb - pa), 1 if pb > pa else -1))
    hits.sort(); out = []; w = 0; s0 = None
    for q, d in hits:
        if w == 0: s0 = q
        w += d
        if w == 0: out.append((s0, q))
    return out
HARPOONS = {0x21C0: [(0, 1)], 0x21C1: [(0, -1)], 0x21BC: [(180, -1)], 0x21BD: [(180, 1)],
            0x21BE: [(90, -1)], 0x21BF: [(90, 1)], 0x21C2: [(270, 1)], 0x21C3: [(270, -1)],
            0x21CC: [(0, 1), (180, 1)], 0x21CB: [(180, -1), (0, -1)]}       # top to bottom for the pairs
EQ = vspan(cmap[ord('=')], (bounds(cmap[ord('=')])[0] + bounds(cmap[ord('=')])[2]) / 2, K_IT)
EQ_MID = sorted((lo + hi) / 2 for lo, hi in EQ)
for u, shafts in HARPOONS.items():
    g = cmap.get(u); ch = chr(u)
    if g is None: check(False, f'{ch} U+{u:04X} unmapped'); continue
    vertical = shafts[0][0] in (90, 270)
    fp = Flat(K_IT); gs[g].draw(fp)                              # unslanted
    check(len(fp.polys) == len(shafts), f'{ch}: {len(fp.polys)} contours for {len(shafts)} harpoon(s) (each harpoon one outline)')
    if len(fp.polys) != len(shafts): continue
    cen = lambda poly: (sum(x for x, _ in poly) / len(poly), sum(y for _, y in poly) / len(poly))
    polys = sorted(fp.polys, key=lambda q: cen(q)[0] if vertical else -cen(q)[1])   # top to bottom (left to right)
    centres = []
    for poly, (deg, side) in zip(polys, shafts):
        a = math.radians(-deg); co, si = math.cos(a), math.sin(a)
        P = [[(x * co - y * si, (x * si + y * co) * side) for x, y in poly]]   # pointing along +x, barb above
        X = [x for x, _ in P[0]]; Y = [y for _, y in P[0]]; tip = max(X)
        sh = scan(P, min(X) + 10, False)                          # the bare shaft at the tail
        check(len(sh) == 1 and abs((sh[0][1] - sh[0][0]) - BAR) <= 3, f'{ch} ({deg} deg): the tail {sh} is not one shaft of the bar {BAR}')
        if len(sh) != 1: continue
        y_lo, y_hi = sh[0]
        yc = (y_lo + y_hi) / 2 * side; co2, si2 = math.cos(-a), math.sin(-a)
        centres.append((min(X) * co2 - yc * si2, min(X) * si2 + yc * co2)[0 if vertical else 1])
        far = scan(P, y_lo + 2, True)
        check(len(far) == 1 and far[0][1] >= tip - 3,
              f'{ch} ({deg} deg): along the shaft\'s far edge the ink is {[(round(p), round(q)) for p, q in far]}, the tip at {tip:.0f}: the shaft stops short of the tip')
        near_tip = scan(P, tip - 2, False)
        check(bool(near_tip) and near_tip[0][0] <= y_lo + 3,
              f'{ch} ({deg} deg): 2 units behind the tip the ink is {[(round(p), round(q)) for p, q in near_tip]}, the far edge at {y_lo:.0f}: the barb\'s tip is off the shaft')
        check(max(Y) >= y_hi + 100, f'{ch} ({deg} deg): barb top {max(Y):.0f}, only {max(Y) - y_hi:.0f} above the shaft')
        check(min(Y) >= y_lo - 2, f'{ch} ({deg} deg): ink {y_lo - min(Y):.0f} units below the shaft\'s far edge')
    if len(centres) != len(shafts) or vertical: continue
    want = [AXIS] if len(shafts) == 1 else sorted(EQ_MID, reverse=True)
    for c_, w_ in zip(centres, want):
        check(abs(c_ - w_) <= 3, f'{ch}: shaft centre {c_:.1f}, want {w_:.1f} ({"the axis" if len(shafts) == 1 else "a bar of ="})')
print(f'harpoons: {len(HARPOONS)} glyphs, the tip on the shaft\'s far edge')

# ---- 8. paired arrows ----------------------------------------------------------------
def dense(poly, step=4):
    out = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out
PAIRS = {0x21C4: ((0, 'top'), (180, 'bottom')), 0x21C6: ((180, 'top'), (0, 'bottom')),
         0x21C5: ((90, 'left'), (270, 'right')), 0x21F5: ((270, 'left'), (90, 'right'))}
for u, arrows in PAIRS.items():
    g = cmap.get(u); ch = chr(u)
    if g is None: check(False, f'{ch} U+{u:04X} unmapped'); continue
    fp = Flat(K_IT); gs[g].draw(fp)
    check(len(fp.polys) == 2, f'{ch}: {len(fp.polys)} contours, want the two arrows apart')
    if len(fp.polys) != 2: continue
    d = min(math.dist(p, q) for p in dense(fp.polys[0]) for q in dense(fp.polys[1]))
    check(d >= 0.6 * BAR, f'{ch}: the two arrows {d:.0f} apart, under 0.6 x {BAR}')
    for poly in fp.polys:
        heads = 0
        for deg, _ in arrows:
            a = math.radians(-deg); co, si = math.cos(a), math.sin(a)
            P = [[(x * co - y * si, x * si + y * co) for x, y in poly]]
            X = [x for x, _ in P[0]]; tip = max(X)
            tail = scan(P, min(X) + 80, False)                 # 80 in from this end: the bare shaft if it is the tail
            if not (len(tail) == 1 and tail[0][1] - tail[0][0] <= BAR + 3): continue   # this deg runs tip to tail
            heads += 1
            three = any(len(scan(P, tip - k, False)) == 3 for k in range(60, 400, 4))
            check(three, f'{ch} ({deg} deg): the head never opens into two wings beside the shaft (filled in)')
        check(heads == 1, f'{ch}: an arrow with {heads} heads found (one tail of bare shaft, one head)')
print(f'paired arrows: {len(PAIRS)} glyphs, apart and with open heads')

# ---- 9. circle and semicircle arrows -------------------------------------------------
def tip_flats(g, k=0):
    """The short straight segments of g's outline (unslanted by k): the flat tips of its heads."""
    rp = RecordingPen(); gs[g].draw(rp); out = []; cur = start = None
    for op, args in rp.value:
        pts = [(x - k * y, y) for x, y in args]
        if op == 'moveTo': cur = start = pts[0]
        elif op == 'lineTo':
            if 10 <= math.dist(cur, pts[0]) <= 4 * BAR: out.append((cur, pts[0]))
            cur = pts[0]
        elif op == 'closePath':
            if cur != start and 10 <= math.dist(cur, start) <= 4 * BAR: out.append((cur, start))
        elif pts: cur = pts[-1]
    return out
def centred_head(g, P, run):
    """Whether some flat tip of g, scanned across behind it, gives `run` units of scans that
    find a wing, a bar-wide shaft and a wing, the shaft centred between the wings' outer edges."""
    for p, q in tip_flats(g, K_IT):
        m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        for sgn in (1, -1):
            deg = math.atan2(sgn * (p[0] - q[0]), -sgn * (p[1] - q[1])); co, si = math.cos(-deg), math.sin(-deg)
            Q = [[(x * co - y * si, x * si + y * co) for x, y in poly] for poly in P]
            tip, yt = m[0] * co - m[1] * si, m[0] * si + m[1] * co; good = 0
            for k in range(20, 500, 2):
                sp = [s_ for s_ in scan(Q, tip - k, False) if abs((s_[0] + s_[1]) / 2 - yt) < 300]   # the head's, not the far side of the arc
                ok = (len(sp) == 3 and abs((sp[1][1] - sp[1][0]) - BAR) <= 4
                      and abs((sp[1][0] + sp[1][1]) / 2 - (sp[0][0] + sp[2][1]) / 2) <= 4)
                good = good + 2 if ok else 0
                if good >= run: return True
    return False
H_CAP = bounds('H')[3]
for cw, acw in ((0x21BB, 0x21BA), (0x21B6, 0x21B7)):
    if cw not in cmap or acw not in cmap: check(False, f'U+{cw:04X}/U+{acw:04X} unmapped'); continue
    ga, gb = cmap[cw], cmap[acw]; adv = hmtx[ga][0]
    ba, bb = bounds(ga), bounds(gb)
    check(K_IT or hmtx[gb][0] == adv and all(abs(p - q) <= 1 for p, q in zip(ba, (adv - bb[2], bb[1], adv - bb[0], bb[3]))),
          f'{chr(acw)} is not {chr(cw)} mirrored: {bb} vs {ba} (advance {adv})')
    for u in (cw, acw):
        ch = chr(u); fp = Flat(K_IT); gs[cmap[u]].draw(fp)
        check(len(fp.polys) == 1, f'{ch}: {len(fp.polys)} contours, want one')
        check(centred_head(cmap[u], fp.polys, round(0.3 * BAR)), f'{ch}: no direction finds the shaft centred between the head\'s wings')
        if u in (0x21B6, 0x21B7): continue
        # a chord 100 below the centre, clear of the head: the ring's two sides
        low = min(y for poly in fp.polys for _, y in poly); yc = H_CAP / 2 - 100
        ring = scan(fp.polys, yc, True)
        mid = hmtx[cmap[u]][0] / 2 - K_IT * 252                  # the advance's middle, unslanted like the outline
        if len(ring) != 2: check(False, f'{ch}: 100 under half the cap height the ring is {ring}, not two sides'); continue
        cx = (ring[0][0] + ring[1][1]) / 2
        check(abs(cx - mid) <= 2, f'{ch}: the circle\'s centre {cx:.1f} is off the advance\'s middle {mid:.1f}')
        bot = [q for q in scan(fp.polys, cx, False) if q[1] < yc]
        check(len(bot) == 1 and abs((bot[0][1] - bot[0][0]) - BAR) <= 3, f'{ch}: the ring\'s foot {bot} is not one bar ({BAR}) wide')
        ro = ((ring[1][1] - ring[0][0]) ** 2 / 4 + (yc - low) ** 2) / (2 * (yc - low))   # outer radius from the chord and the foot
        check(abs(low + ro - H_CAP / 2) <= 3, f'{ch}: the circle\'s centre at {low + ro:.1f}, not half the cap height {H_CAP / 2:.1f}')
print('circle arrows: centred circles, heads centred on the stroke')

print(f'verify_symbols {STYLE} {MODE}: {checks} checks, {fails} failures')
sys.exit(1 if fails else 0)

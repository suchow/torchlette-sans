"""kern_apos: the apostrophe fitted to the letters around it (person’s, don’t, we’ll).

Mulish spaces the apostrophe ’ (quoteright, also the closing single quote), the ASCII
' (quotesingle) and the modifier letter apostrophe ʼ (uni02BC) as free-standing
punctuation and kerns only a few letters to them (’s -29, ’d -39, n’ -19 in Regular).
Torchlette's lower x-height drops the letters further below the apostrophe, which hangs
from the cap height, so the white around it grows: in Regular the closest approach of
’ to s is 1.24 times the n-n gap (Mulish 1.14, Noto Sans 0.74) and of n to ’ 1.23 (Noto
0.60), and the s of person’s floats away from its word.

What it changes:

1. glyphs: ʼ (uni02BC) takes the sidebearings of ’ (Mulish gives it a modifier letter's
   114 and 113 units in Regular against ’'s 67 and 66, though it only ever stands
   inside a word); its outline and height are unchanged. GLYPH_OVERRIDE says so.
2. KERN_APOS (GPOS, feature `kern`, one lookup): for each apostrophe A and each letter
   x, the pairs (x, A) and (A, x) are tightened until the closest approach of the two
   outlines, as set (Mulish's kerning included, measured in the slanted frame in an
   italic), is TARGET times the closest approach of n to n in the same style. A pair
   already that tight is left alone (nothing is loosened); the pull is capped at
   MAX_PULL times the n-n gap (in practice the cap sets ’s, n’, e’, o’, ’d, ’e, ’o,
   which the closest-approach target alone would pull in further than looks right),
   rounded to ROUND units, and dropped under MIN_K. Accented letters (by canonical
   decomposition), kern's INHERIT glyphs (ligatures, ss16 forms) and the ss04-ss07
   alternates are fitted the same way on their own outlines, so an accent next to the
   apostrophe (café’s) limits its own pair. Values add to the kerning earlier lookups
   give, so the lookup's place among the kern lookups does not matter.

In Regular this moves ’s from -29 to -79 and n’ from -19 to -69 units; their closest
approaches go from 1.24 and 1.23 times the n-n gap to 0.99 and 0.99 (Italic: n’ 1.40 to
1.14, ’s 1.12 to 0.89; Noto Sans 0.60 and 0.74). The cap keeps them looser than Noto's,
in keeping with Mulish's open fit. Tuned by eye on a specimen beside Noto Sans and
Mulish at 16, 20 and 48 px.

Closest approach is the measure here because the apostrophe meets the next letter
corner to corner: what reads as the gap of ’s is the distance from the tail of the
apostrophe down to the shoulder of the s, which the row-by-row model in `kern` sees only
through its blur.

Requires `kern` (it reads kern's applied-kerning walk and its INHERIT table); the name
sorts after it, so kern's check that no other module names its inheriting glyphs has
run before this module's text exists.
"""
import math
import sys
import unicodedata
from collections import defaultdict

from fontTools.pens.basePen import BasePen

TARGET = 0.90     # closest approach of letter and apostrophe, as a multiple of the n-n one
MAX_PULL = 0.30   # never pull a pair in by more than this multiple of the n-n gap
ROUND = 5
MIN_K = 5
APOS = ('quoteright', 'quotesingle', 'uni02BC')
GLYPH_OVERRIDE = {'uni02BC'}   # its sidebearings (see glyphs()): an edit to the shared font
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


class _Pts(BasePen):
    """The outline as a dense polyline of points (curves flattened)."""
    def __init__(self):
        super().__init__(None); self.pts = []; self.cur = self.start = None
    def _seg(self, p):
        a = self.cur
        n = max(1, int(math.hypot(p[0] - a[0], p[1] - a[1]) // 6))
        for i in range(1, n + 1):
            self.pts.append((a[0] + (p[0] - a[0]) * i / n, a[1] + (p[1] - a[1]) * i / n))
        self.cur = p
    def _moveTo(self, p): self.start = self.cur = p; self.pts.append(p)
    def _lineTo(self, p): self._seg(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur
        for i in range(1, 17):
            t = i / 16; m = 1 - t
            self._seg(tuple(m ** 3 * p0[k] + 3 * m * m * t * p1[k] + 3 * m * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1)))
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur
        for i in range(1, 13):
            t = i / 12; m = 1 - t
            self._seg(tuple(m * m * p0[k] + 2 * m * t * p1[k] + t * t * p2[k] for k in (0, 1)))
    def _closePath(self):
        if self.cur is not None and self.start is not None and self.cur != self.start: self._seg(self.start)
        self.cur = self.start
    _endPath = _closePath


def glyphs(ctx):
    """The modifier letter apostrophe ʼ takes the sidebearings of ’. Mulish spaces it as a
    free-standing modifier (114 and 113 units in Regular against ’'s 67 and 66), but it
    only ever stands inside a word. Its outline and height are unchanged."""
    glyf, hmtx = ctx.glyf, ctx.hmtx
    if 'uni02BC' not in glyf.glyphs or 'quoteright' not in glyf.glyphs: return
    q, m = glyf['quoteright'], glyf['uni02BC']
    if m.isComposite() or q.isComposite(): return
    q.recalcBounds(glyf); m.recalcBounds(glyf)
    q_l = q.xMin; q_r = hmtx['quoteright'][0] - q.xMax
    old_l, old_r = m.xMin, hmtx['uni02BC'][0] - m.xMax
    dx = q_l - m.xMin
    m.coordinates.translate((dx, 0)); m.recalcBounds(glyf)
    adv = m.xMax + q_r
    hmtx['uni02BC'] = (adv, m.xMin)
    ctx.log(f'uni02BC: sidebearings {old_l}, {old_r} -> {m.xMin}, {adv - m.xMax}; advance {adv}')


def features(ctx):
    kern = sys.modules.get('tsmod_kern')
    if kern is None:
        raise SystemExit('kern_apos: needs the kern module (MODULES must include kern)')
    font = ctx.font
    have = set(font.getGlyphOrder())
    cmap = font.getBestCmap()
    k_slant, yc = ctx.ITALIC_K, ctx.ITALIC_YC
    pts_cache = {}

    def pts(g):
        """The outline's points in the final frame (reslanted in an italic)."""
        if g not in pts_cache:
            pen = _Pts(); ctx.path_of(g).draw(pen)
            pts_cache[g] = [(x + k_slant * (y - yc), y) for x, y in pen.pts]
        return pts_cache[g]

    # the kerning as it will apply before this lookup: Mulish's, the small caps', and
    # kern's inherited pairs (accented letters, ligatures) for the glyphs it adds
    base = dict(kern.effective_kerning(font['GPOS'].table))

    def need(a, b, kern0, target):
        """The extra kerning that sets b after a (advance plus kern0) with its closest
        approach exactly `target`: for each pair of outline points less than `target`
        apart vertically, the horizontal span they need is sqrt(target^2 - dy^2), so the
        answer is the largest shortfall over the facing points. Negative when the pair
        is looser than `target`; None when the outlines never come that close
        vertically."""
        A = pts(a); B = pts(b)
        if not A or not B: return None
        dx = ctx.W(a) + kern0
        ax = max(x for x, _ in A); bx = min(x for x, _ in B)
        A = [p for p in A if p[0] > ax - 2 * target]; B = [p for p in B if p[0] < bx + 2 * target]
        t2 = target * target; best = None
        for x0, y0 in A:
            for x1, y1 in B:
                dy = y1 - y0
                if dy * dy >= t2: continue
                k = math.sqrt(t2 - dy * dy) - (x1 + dx - x0)
                if best is None or k > best: best = k
        return best

    def closest(a, b, kern0):
        """Closest approach of b set after a, in units (for the log and the check)."""
        A = pts(a); B = pts(b); dx = ctx.W(a) + kern0
        return math.sqrt(min((x1 + dx - x0) ** 2 + (y1 - y0) ** 2 for x0, y0 in A for x1, y1 in B))

    nn = closest('n', 'n', base.get(('n', 'n'), 0))
    target = TARGET * nn
    cap = MAX_PULL * nn
    apos = [a for a in APOS if a in have]
    letters = [c for c in LETTERS if c in have]

    # letter -> it and the accented letters (by canonical decomposition); each is fitted
    # on its own outline (an accent can stand closer to the apostrophe than the letter),
    # starting from its letter's kerning when it has none of its own (kern's INHERIT)
    family = defaultdict(list)
    for c in letters: family[c].append(c)
    for u, g in sorted(cmap.items()):
        if g in letters or g not in have: continue
        dec = unicodedata.decomposition(chr(u)).split()
        if dec and not dec[0].startswith('<'):
            c = chr(int(dec[0], 16))
            while c not in letters:
                d2 = unicodedata.decomposition(c).split()
                if not d2 or d2[0].startswith('<'): break
                c = chr(int(d2[0], 16))
            if c in letters and g not in family[c]: family[c].append(g)

    # glyphs kern gives a letter's kerning (ligatures, ss16 forms, alternates): fitted
    # the same way on their own outlines, each side from the letter that side shows
    sides = {}                                          # glyph -> (left letter, right letter)
    for c in letters:
        for g in family[c]: sides[g] = (c, c)
    for g, (lb, rb) in kern.INHERIT.items():
        if g in have and g not in sides: sides[g] = (lb, rb)
    for g in sorted(have):
        for suf in kern.ALT_SUFFIXES:
            if g.endswith(suf) and g[:-len(suf)] in sides and g not in sides: sides[g] = sides[g[:-len(suf)]]
    for g, (lb, rb) in list(sides.items()):       # resolve chains to a letter
        lb = sides.get(lb, (lb, lb))[0] if lb not in letters else lb
        rb = sides.get(rb, (rb, rb))[1] if rb not in letters else rb
        sides[g] = (lb if lb in letters else None, rb if rb in letters else None)

    pairs = {}
    show = {}
    for a in apos:
        for g, (lb, rb) in sorted(sides.items()):
            todo = []
            if rb: todo.append((g, a, rb, a))
            if lb: todo.append((a, g, a, lb))
            for (l, r, lc, rc) in todo:
                k0 = base.get((l, r), base.get((lc, rc), 0))
                k = need(l, r, k0, target)
                if k is None or k >= 0: continue
                k = int(ROUND * round(max(k, -cap) / ROUND))
                if -k < MIN_K: continue
                pairs[l, r] = k
                if g in letters: show[l, r] = k
    ctx.apos_pairs = pairs
    ctx.apos_target = (TARGET, nn)
    if not pairs: return
    text, nl, nr = kern.pairs_fea('KERN_APOS', pairs)
    ctx.gpos(text)
    sample = ' '.join(f'{l}{r}:{v}' for (l, r), v in sorted(show.items()) if 'quoteright' in (l, r) and (l + r).replace('quoteright', '') in 'nsdltmrveoy')
    ctx.log(f'KERN_APOS: {len(pairs)} pairs, {nl} x {nr} classes; n-n gap {nn:.0f}, target {target:.0f}; {sample}')

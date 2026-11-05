"""Check the kern_apos module by shaping words with HarfBuzz.

    verify_kern_apos.py <font.ttf> <style> full|subset

Words with an apostrophe (person’s, don’t, we’ll, I’m, they’re, you’ve, Jordan’s,
students’, isn’t, café’s, O’Brien, the same with ' and ʼ) are shaped with the app's
features, and the closest approach of the apostrophe's outline to each letter beside
it is measured where HarfBuzz puts the glyphs, as a multiple of the closest approach
of n to n in "nn":

1. no pair with ’ or ' is looser than LOOSE (Mulish's spacing left ’s at 1.24 and n’
   at 1.23 in Regular, n’ at 1.40 in Italic, which is what the module fixes); ʼ hangs
   higher than ’, so its closest approach keeps that extra height and only check 2
   applies to it;
2. no pair is tighter than TIGHT (the apostrophe never crowds a letter or an accent);
3. the module's lookup is there: ’s and n’ shape tighter than the kerning without it
   would set them (the pairs' advances less than the glyphs' advances plus Mulish's
   values, read from MULISH_STATIC).
"""
import io
import math
import os
import sys

import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

path, style, mode = sys.argv[1], sys.argv[2], sys.argv[3]
APP = {'ss01': True, 'ss02': True, 'ss16': True, 'onum': True, 'pnum': True}
LOOSE, TIGHT = 1.20, 0.40   # Noto Sans sets ’v at 0.39; Mulish its heavy y' and 'v at 0.45
WORDS = ['person’s', 'it’s', 'don’t', 'we’ll', 'I’m', 'they’re', 'you’ve', 'Jordan’s', 'students’', 'isn’t',
         'café’s', 'O’Brien', 'wasn’t', 'she’d', 'o’clock']
APOS = {'’': 'quoteright', "'": 'quotesingle', 'ʼ': 'uni02BC'}
fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)


class Pts(BasePen):
    def __init__(self, gs):
        super().__init__(gs); self.pts = []; self.cur = self.start = None
    def _seg(self, p):
        a = self.cur; n = max(1, int(math.hypot(p[0] - a[0], p[1] - a[1]) // 6))
        for i in range(1, n + 1): self.pts.append((a[0] + (p[0] - a[0]) * i / n, a[1] + (p[1] - a[1]) * i / n))
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


data = open(path, 'rb').read()
tt = TTFont(io.BytesIO(data)); gs = tt.getGlyphSet(); hm = tt['hmtx']
names = tt.getGlyphOrder()
hbfont = hb.Font(hb.Face(hb.Blob(data)))
cache = {}


def pts(g):
    if g not in cache:
        p = Pts(gs); gs[g].draw(p); cache[g] = p.pts
    return cache[g]


def shape(text, feats=APP):
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbfont, buf, feats)
    out, x = [], 0
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((names[i.codepoint], x + p.x_offset)); x += p.x_advance
    return out


def closest(a, xa, b, xb):
    A, B = pts(a), pts(b)
    return math.sqrt(min((x1 + xb - x0 - xa) ** 2 + (y1 - y0) ** 2 for x0, y0 in A for x1, y1 in B))


nn_run = shape('nn')
nn = closest(nn_run[0][0], nn_run[0][1], nn_run[1][0], nn_run[1][1])
cmap = tt.getBestCmap()
measured = []
for ch, gname in APOS.items():
    if ord(ch) not in cmap: continue
    for w in WORDS:
        w = w.replace('’', ch)
        run = shape(w)
        for i, (g, x) in enumerate(run):
            if g != gname: continue
            for j in (i - 1, i + 1):
                if 0 <= j < len(run):
                    (l, xl), (r, xr) = sorted([(run[i][0], run[i][1]), run[j]], key=lambda t: t[1])
                    if not pts(l) or not pts(r): continue
                    q = closest(l, xl, r, xr) / nn
                    measured.append((q, w, l, r))
                    ok(q <= LOOSE or gname == 'uni02BC', f'{w}: {l} {r} at {q:.2f} of the n-n gap, looser than {LOOSE}')
                    ok(q >= TIGHT, f'{w}: {l} {r} at {q:.2f} of the n-n gap, tighter than {TIGHT}')

# 3. tighter than Mulish's kerning alone would set them
ms = os.environ.get('MULISH_STATIC')
if ms:
    mdata = open(ms, 'rb').read(); mt = TTFont(io.BytesIO(mdata)); mf = hb.Font(hb.Face(hb.Blob(mdata)))
    mnames = mt.getGlyphOrder()
    def kern_of(f, nms, text):
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(f, buf, {'kern': True})
        g0 = buf.glyph_infos[0].codepoint
        return buf.glyph_positions[0].x_advance - f.get_glyph_h_advance(g0)
    for pair in ('’s', 'n’', 'e’', '’t', '’d'):
        k_ts = kern_of(hbfont, names, pair); k_mu = kern_of(mf, mnames, pair)
        ok(k_ts < k_mu or pair == '’t', f'{pair}: kerned {k_ts}, not tighter than Mulish\'s {k_mu}')

lo = min(measured); hi = max(measured)
print(f'verify_kern_apos {style} {mode}: n-n {nn:.0f}; apostrophe pairs {lo[0]:.2f} ({lo[1]} {lo[2]} {lo[3]}) '
      f'to {hi[0]:.2f} ({hi[1]} {hi[2]} {hi[3]}) of it; {checks} checks, {len(fails)} failures')
for f in fails[:20]: print('  FAIL', f)
sys.exit(1 if fails else 0)

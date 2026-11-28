"""X-height Latin petite capitals, separate from the existing small capitals.

A-Z use the small-cap construction at XH/705, including heavier-donor stem
matching, round-cap width correction, and proportional sidebearings. Accents,
non-Latin letters, figures, and petite-cap kerning are outside this first slice.
"""
import pathops
from fontTools.pens.transformPen import TransformPen

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def draw(ctx, donor, weight, scale):
    """Draw all 26 forms from an unslanted donor using the build's cap recipe."""
    gs = donor.getGlyphSet()
    for ch in ALPHABET:
        p = pathops.Path()
        gs[ch].draw(TransformPen(p.getPen(glyphSet=gs),
                                (scale, 0, 0, scale, ctx.SC_TRACK, 0)))
        advance = donor['hmtx'][ch][0]
        if ch in ctx.ROUND_UC:
            g, advance, _ = ctx.xscale(ch, ctx.ROUND_UC[ch], 'O',
                                       src_w=weight, target=donor['glyf'])
            p = pathops.Path()
            g.draw(TransformPen(p.getPen(),
                               (scale, 0, 0, scale, ctx.SC_TRACK, 0)), donor['glyf'])
        ctx.add(ch + '.pc', p, advance * scale + 2 * ctx.SC_TRACK)
        ctx.GDEF_CLASS[ch + '.pc'] = 1
    h = ctx.glyf['H.pc']
    h.recalcBounds(ctx.glyf)
    spacing = (h.xMin - ctx.SC_TRACK_C) / (h.xMin - ctx.SC_TRACK)
    for ch in ALPHABET:
        name = ch + '.pc'
        g = ctx.glyf[name]
        g.recalcBounds(ctx.glyf)
        left, right = g.xMin, ctx.hmtx[name][0] - g.xMax
        nl, nr = (round((side - ctx.SC_TRACK) * spacing + ctx.SC_TRACK_C)
                  for side in (left, right))
        g.coordinates.translate((nl - left, 0))
        g.recalcBounds(ctx.glyf)
        ctx.hmtx[name] = (nl + g.xMax - g.xMin + nr, g.xMin)


def glyphs(ctx):
    if any(ch + '.pc' in ctx.font.getGlyphOrder() for ch in ALPHABET):
        raise ValueError('petite-capital glyph name collision')
    scale = ctx.XH / 705
    target = ctx.SC_STEM
    lo, hi = ctx.SRC_W, min(1000, ctx.SRC_W + 376)
    for _ in range(9):
        mid = (lo + hi) / 2
        _, stem = ctx.cap_stem(mid)
        lo, hi = (mid, hi) if stem * scale < target else (lo, mid)
    weight = round((lo + hi) / 2)
    donor, stem = ctx.cap_stem(weight)
    draw(ctx, donor, weight, scale)
    ctx.log(f'donor {weight}, stem {stem * scale:.1f}, height {ctx.XH}')


def features(ctx):
    lower = ' '.join(ALPHABET.lower())
    upper = ' '.join(ALPHABET)
    petite = ' '.join(ch + '.pc' for ch in ALPHABET)
    ctx.gsub(f'feature pcap {{ sub [{lower}] by [{petite}]; }} pcap;\n'
             f'feature c2pc {{ sub [{upper}] by [{petite}]; }} c2pc;\n',
             after='classes')

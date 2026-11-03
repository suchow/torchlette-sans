"""mathletters: the letterlike symbols of machine-learning prose, ℙ ℍ 𝔼 𝟙 ℒ ℏ, and the
operators ∥ ∖ ⟂ ⟦ ⟧ ⋆.

Double-struck ℙ ℍ 𝔼 𝟙 (U+2119, U+210D, U+1D53C, U+1D7D9) are the symbols module's
(`doublestruck` in symbols.py, which draws the whole double-struck set after Noto Sans
Math's design from Torchlette's capitals and figures): ℙ's stem and the right side of its
bowl doubled, ℍ's two stems, 𝔼's stem, 𝟙's stem; every other stroke one hairline, every
doubled stroke closed at both ends.

ℒ (U+2112) is supplied with the other script letters by mathnotation's direct Noto Sans Math fallback.

ℏ (U+210F) is Torchlette's h with a bar through the ascender at the crossbar's weight; the
bar's slope (30 degrees; Noto Sans Math's is 35 on a slanted h), its reach (0.72 of the
letter's ink width, centred on the stem) and its height (crossing the stem midway between the
arch and the ascender, where ħ's bar crosses; lower in Black, so its high end stays 10 under
the ascender) follow Noto Sans Math's ℏ. It differs from ħ
(U+0127) by the slant.

Operators, on the symbols module's conventions: ∥ (U+2225) two bars of | with a gap of 1.1
bars and a relation's sidebearings (130, as ∣ has); ∖ (U+2216) the backslash with 80 of room
each side (Noto Sans Math, STIX Two and DejaVu Sans all draw it the backslash's full height);
⟂ (U+27C2) the up tack's geometry on the baseline (Noto Sans Math and STIX Two draw ⟂ and ⊥
alike); ⟦ ⟧ (U+27E6-27E7) the square brackets with a second stem 1.3 stems inside (Noto's
gap), the arms run on; ⋆ (U+22C6) a regular pentagram (inner radius 0.382 of the outer) of
the asterisk's size on the math axis.

Cmap: 𝔼 and 𝟙 are outside the BMP, so before mapping them the module adds format 12
subtables, (3,10) and (0,4), that copy the whole best cmap, so every client still sees the
full repertoire (modules/README.md, "Avoiding collisions").

Nothing existing is changed. No layout features. Glyph names: uni2119, uni210D, u1D53C,
u1D7D9, uni210F, uni2225, uni2216, uni27C2, uni27E6, uni27E7, uni22C6. Code points
outside the Makefile's web subset ranges: U+1D53C and U+1D7D9. Knobs (environment):
ML_HBAR_DEG, ℏ's bar angle (30).
"""
import importlib.util
import math
import os
import sys

import pathops
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12

HERE = os.path.dirname(os.path.abspath(__file__))

def ds_glyphs(c, which):
    """The symbols module's double-struck forms of the bases in `which` for this style
    (symbols.py's `doublestruck`, from the module as loaded by the build, or symbols.py beside
    this file when symbols is not selected): {base: (path, advance)}."""
    mod = sys.modules.get('tsmod_symbols')
    if mod is None:
        spec = importlib.util.spec_from_file_location('tsmod_symbols_for_mathletters', os.path.join(HERE, 'symbols.py'))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        sys.modules['tsmod_symbols_for_mathletters'] = mod
    return mod.doublestruck(c, which)


def _format12(c):
    """Format 12 Unicode subtables, (3,10) and (0,4), each a copy of the best cmap, unless the
    font has one already."""
    cmap = c.font['cmap']
    if any(t.isUnicode() and t.format in (12, 13) for t in cmap.tables): return False
    best = dict(c.font.getBestCmap())
    for plat, enc in ((3, 10), (0, 4)):
        t = cmap_format_12(12); t.platformID = plat; t.platEncID = enc; t.language = 0; t.cmap = dict(best)
        cmap.tables.append(t)
    return True




def glyphs(ctx):
    c = ctx
    rect, poly, union, diff, clip, band = c.rect, c.poly, c.union, c.diff, c.clip, c.band
    ellipse, transformed, path_of, W, mv, mirror = c.ellipse, c.transformed, c.path_of, c.W, c.mv, c.mirror
    hspans, vspans = c.hspans, c.vspans
    A, BAR = c.LIN_AXIS, c.BAR
    VB = BAR * 1.15                                             # the operators' vertical stroke (symbols)
    order = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()
    made = ctx.made = []
    width = lambda s: s[1] - s[0]

    def put(cp, path, adv, name=None):
        name = name or (f'u{cp:04X}' if cp > 0xFFFF else f'uni{cp:04X}')
        assert name not in order, name
        assert cp not in cmap, f'U+{cp:04X} already mapped to {cmap[cp]}'
        c.add(name, path, adv); c.GDEF_CLASS[name] = 1
        ctx.map(cp, name); made.append(name)
        return name

    def fit(p, lsb, rsb=None):
        b = p.bounds; p = mv(p, lsb - b[0])
        return p, round((b[2] - b[0]) + lsb + (lsb if rsb is None else rsb))

    def contours(p):
        cs = []
        for cont in p.contours:
            q = pathops.Path(); cont.draw(q.getPen()); cs.append(q)
        return sorted(cs, key=lambda q: -(q.bounds[2] - q.bounds[0]) * (q.bounds[3] - q.bounds[1]))

    def eroded(p, tx, ty):
        """p shrunk by tx horizontally and ty vertically (a round pen in a frame stretched by tx/ty)."""
        k = tx / ty
        q = transformed(p, (1, 0, 0, k, 0, 0))
        s = pathops.Path(q); s.stroke(2 * tx, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        s.convertConicsToQuads(); s.simplify()
        return transformed(diff(q, s), (1, 0, 0, 1 / k, 0, 0))

    def hollowed(fat, tx, ty):
        return diff(fat, eroded(fat, tx, ty))


    hp = path_of('H'); Hb = hp.bounds; CH = Hb[3]
    H_STEM = width(hspans(hp, CH * 0.2)[0])
    H_BAR = width(vspans(hp, (Hb[0] + Hb[2]) / 2)[0])

    if _format12(c): ctx.log('cmap: format 12 subtables (3,10) and (0,4) added, copies of the best cmap')

    # ---- double-struck ℙ ℍ 𝔼 𝟙 (symbols.doublestruck) ----------------------------------
    ds = ds_glyphs(c, ['P', 'H', 'E', 'one'])
    s_ = c.ds_strokes
    ctx.log(f"double-struck hairline {s_['t']:.1f}, gap {s_['g']:.1f}, doubled stroke {s_['D']:.1f} (stem {s_['stem']:.1f})")
    for cp, name, base in ((0x2119, 'uni2119', 'P'), (0x210D, 'uni210D', 'H'), (0x1D53C, 'u1D53C', 'E'), (0x1D7D9, 'u1D7D9', 'one')):
        put(cp, ds[base][0], round(ds[base][1]), name)

    # ℒ is supplied by mathnotation's complete existing-font script fallback.

    # ---- ℏ: h with a slanted bar ---------------------------------------------------------
    hh = path_of('h'); hb = hh.bounds
    stem = hspans(hh, hb[3] * 0.85)[0]; xc = (stem[0] + stem[1]) / 2
    arch_top = max(y1 for y0, y1 in vspans(hh, hb[2] - 30))    # the arch's top at the right stem
    deg = c.P('ML_HBAR_DEG', 30); tg = math.tan(math.radians(deg))
    half = 0.72 * (hb[2] - hb[0]) / 2
    t = H_BAR / math.cos(math.radians(deg))                     # vertical thickness for the crossbar's weight across
    yc = min((arch_top + hb[3]) / 2, hb[3] - 10 - half * tg - t / 2)   # the bar's high end stays under the ascender (Black)
    barp = poly([(xc - half, yc - half * tg - t / 2), (xc + half, yc + half * tg - t / 2),
                 (xc + half, yc + half * tg + t / 2), (xc - half, yc - half * tg + t / 2)])
    put(0x210F, union(hh, barp), W('h'))

    # ---- operators ------------------------------------------------------------------------
    bar = path_of('bar'); bb = bar.bounds; bw = bb[2] - bb[0]; gap = 1.1 * bw
    put(0x2225, union(mv(bar, 130 - bb[0]), mv(bar, 130 + bw + gap - bb[0])), round(260 + 2 * bw + gap))
    put(0x2216, *fit(path_of('backslash'), 80))
    put(0x27C2, union(rect(70, 0, 530, BAR), rect(300 - VB / 2, 0, 300 + VB / 2, 650)), 600)
    bl = path_of('bracketleft'); blb = bl.bounds
    st = hspans(bl, 300)[0]; sw = width(st)
    arms = vspans(bl, st[1] + 10)                               # the arms, bottom and top, beside the stem
    bgap = 1.3 * sw; ext = sw + bgap
    dbl = union(bl, rect(st[1] + bgap, arms[0][0], st[1] + bgap + sw, arms[-1][1]),
                rect(st[1], arms[0][0], blb[2] + ext, arms[0][1]), rect(st[1], arms[-1][0], blb[2] + ext, arms[-1][1]))
    wb = round(W('bracketleft') + ext)
    put(0x27E6, dbl, wb)
    put(0x27E7, mirror(dbl, wb / 2), wb)
    ast = path_of('asterisk').bounds
    R = (ast[2] - ast[0]) / (2 * math.sin(math.radians(72))); r = 0.382 * R
    cy = A - R * (1 - math.cos(math.radians(36))) / 2           # the pentagram's box centred on the axis
    star = poly([(300 + (R if i % 2 == 0 else r) * math.cos(math.radians(90 + 36 * i)),
                  cy + (R if i % 2 == 0 else r) * math.sin(math.radians(90 + 36 * i))) for i in range(10)])
    put(0x22C6, *fit(star, 60))
    ctx.log(f'{len(made)} glyphs')

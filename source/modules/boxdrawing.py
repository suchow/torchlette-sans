"""Nineteen box-drawing characters in a joining cell 600 units wide and 1000 units high.

Cell edges are x=0/600 and y=-250/750; the junction is (300, 250).
Light strokes use the style's minus thickness (BAR); heavy strokes use twice BAR.
Double lines have two BAR strokes separated by a BAR white gap. Rounded corners
have a 150-unit centreline radius. The drawings remain upright in italic styles.
No existing glyphs, features, anchors, or metrics are changed.
"""
import pathops


ADVANCE = 600
BOTTOM, TOP = -250, 750
CX, CY = 300, 250
RADIUS = 150


def glyphs(ctx):
    t = float(ctx.BAR)
    if not 0 < t < RADIUS:
        raise ValueError(f'boxdrawing requires 0 < BAR < {RADIUS}, got {t}')
    order = set(ctx.font.getGlyphOrder())
    cmap = ctx.font.getBestCmap()

    def put(cp, p):
        name = f'uni{cp:04X}'
        if name in order or cp in cmap:
            raise ValueError(f'boxdrawing collision: U+{cp:04X} / {name}')
        # Cancel build.py's final shear exactly, including its y=252 pivot.
        k = ctx.ITALIC_K
        if k:
            p = ctx.transformed(p, (1, 0, -k, 1, k * ctx.ITALIC_YC, 0))
        ctx.add(name, p, ADVANCE)
        ctx.GDEF_CLASS[name] = 1
        ctx.map(cp, name)

    def junction(arms):
        # Trace a single perimeter. Every arm has the same thickness; neither
        # overlaps nor Boolean joins can introduce extra contours with weight.
        h = t / 2
        pts = [(CX - h, CY + h)]
        if 'U' in arms:
            pts += [(CX - h, TOP), (CX + h, TOP)]
        pts += [(CX + h, CY + h)]
        if 'R' in arms:
            pts += [(ADVANCE, CY + h), (ADVANCE, CY - h)]
        pts += [(CX + h, CY - h)]
        if 'D' in arms:
            pts += [(CX + h, BOTTOM), (CX - h, BOTTOM)]
        pts += [(CX - h, CY - h)]
        if 'L' in arms:
            pts += [(0, CY - h), (0, CY + h)]
        return ctx.poly(pts)

    for cp, arms in ((0x2500, 'LR'), (0x2502, 'UD'),
                     (0x250C, 'RD'), (0x2510, 'LD'),
                     (0x2514, 'RU'), (0x2518, 'LU'),
                     (0x251C, 'URD'), (0x2524, 'ULD'),
                     (0x252C, 'LRD'), (0x2534, 'LRU'),
                     (0x253C, 'LRUD')):
        put(cp, junction(arms))

    # Top-left rounded corner: right and down arms, tangent to a quarter circle.
    # Both edges use the same cubic circle approximation, with concentric radii.
    h, r = t / 2, RADIUS
    xc, yc = CX + r, CY - r
    outer, inner = r + h, r - h
    kappa = 4 * (2 ** 0.5 - 1) / 3
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo((CX - h, BOTTOM))
    pen.lineTo((CX - h, yc))
    pen.curveTo((xc - outer, yc + kappa * outer),
                (xc - kappa * outer, yc + outer), (xc, CY + h))
    pen.lineTo((ADVANCE, CY + h))
    pen.lineTo((ADVANCE, CY - h))
    pen.lineTo((xc, CY - h))
    pen.curveTo((xc - kappa * inner, yc + inner),
                (xc - inner, yc + kappa * inner), (CX + h, yc))
    pen.lineTo((CX + h, BOTTOM))
    pen.closePath()
    for cp, sx, sy in ((0x256D, 1, 1), (0x256E, -1, 1),
                       (0x256F, -1, -1), (0x2570, 1, -1)):
        put(cp, ctx.transformed(p, (sx, 0, 0, sy, CX * (1 - sx), CY * (1 - sy))))

    put(0x2501, ctx.rect(0, CY - t, ADVANCE, CY + t))
    put(0x2503, ctx.rect(CX - t, BOTTOM, CX + t, TOP))

    # Centreline separation 2t leaves a clear t between the two t-wide strokes.
    horizontal = pathops.Path()
    vertical = pathops.Path()
    for d in (-t, t):
        ctx.rect(0, CY + d - h, ADVANCE, CY + d + h).draw(horizontal.getPen())
        ctx.rect(CX + d - h, BOTTOM, CX + d + h, TOP).draw(vertical.getPen())
    put(0x2550, horizontal)
    put(0x2551, vertical)

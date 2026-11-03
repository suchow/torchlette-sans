"""Outline check of a built font: kinks, tiny segments and spurs.

    python outline_check.py FONT.ttf [REFERENCE.ttf] [--all]

For every simple glyph (or, with REFERENCE, only the glyphs whose outlines differ
from REFERENCE: the Mulish instance the font was built from; --all checks every
glyph even with REFERENCE) it walks each contour's
curve segments (on-curve points, explicit or implied between two off-curve points):

- kink: an on-curve point next to an off-curve point (a point meant to be smooth)
  where the tangent turns by more than 3 and less than 30 degrees;
- short: a segment whose ends are under 4 units apart;
- spur: a convex turn of more than 150 degrees next to a segment under 15 units (a
  small spike sticking out; long-legged acute corners such as the crotch of an M are drawn on purpose).

A problem that the same glyph of REFERENCE also has (same kind, as many) is Mulish's
own and is listed as inherited, not counted. Prints each failure and exits nonzero if
there are any.
"""
import math, sys
from fontTools.ttLib import TTFont

KINK, KINK_MAX, SHORT, SPUR, SPUR_LEG = 3.0, 30.0, 4.0, 150.0, 15.0

def segments(coords, flags):
    """The contour as on-curve points with the (off-curve) control between them."""
    n = len(coords); pts = [(tuple(coords[i]), bool(flags[i] & 1)) for i in range(n)]
    if not any(on for _, on in pts):
        return []
    k = next(i for i, (_, on) in enumerate(pts) if on)
    pts = pts[k:] + pts[:k]
    out = []                                # (on point, control after it or None)
    for i, (p, on) in enumerate(pts):
        nxt, non = pts[(i + 1) % n]
        if on:
            out.append([p, None])
        else:
            out[-1][1] = p
            if not non:                     # implied on-curve midpoint
                out.append([((p[0] + nxt[0]) / 2, (p[1] + nxt[1]) / 2), None])
    return out

def angle(u, v):
    a = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
    return abs(math.degrees(a))

def check(glyph, glyf):
    coords, ends, flags = glyph.getCoordinates(glyf)
    bad = []; s0 = 0
    for e in ends:
        c = list(coords[s0:e + 1]); f = list(flags[s0:e + 1]); s0 = e + 1
        seg = segments(c, f); m = len(seg)
        orient = 1 if sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(len(c))) > 0 else -1
        for i in range(m):
            p, ctl = seg[i]; q = seg[(i + 1) % m][0]
            prev_p, prev_ctl = seg[i - 1]
            if math.dist(p, q) < SHORT:
                bad.append(f'short {p}->{q} ({math.dist(p, q):.1f})')
            tin_from = prev_ctl if prev_ctl is not None else prev_p
            tout_to = ctl if ctl is not None else q
            tin = (p[0] - tin_from[0], p[1] - tin_from[1]); tout = (tout_to[0] - p[0], tout_to[1] - p[1])
            if tin == (0, 0) or tout == (0, 0): continue
            a = angle(tin, tout)
            smooth = prev_ctl is not None or ctl is not None
            legs = min(math.dist(prev_p, p), math.dist(p, q))
            convex = (tin[0] * tout[1] - tin[1] * tout[0]) * orient > 0
            if a > SPUR and legs < SPUR_LEG and convex: bad.append(f'spur at {p} ({a:.0f} deg)')
            elif smooth and KINK < a < KINK_MAX: bad.append(f'kink at {p} ({a:.1f} deg)')
    return bad

if __name__ == '__main__':
    ALL = '--all' in sys.argv; args = [a for a in sys.argv[1:] if a != '--all']
    font = TTFont(args[0]); glyf = font['glyf']
    ref = TTFont(args[1])['glyf'] if len(args) > 1 else None
    total = inherited = checked = 0
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.isComposite() or g.numberOfContours <= 0: continue
        own = []
        if ref is not None and name in ref.glyphs and not ref[name].isComposite():
            r = ref[name]
            if not ALL and r.numberOfContours == g.numberOfContours and list(r.getCoordinates(ref)[0]) == list(g.getCoordinates(glyf)[0]):
                continue                    # unchanged from Mulish
            own = [b.split()[0] for b in check(r, ref)] if r.numberOfContours > 0 else []
        checked += 1
        for b in check(g, glyf):
            kind = b.split()[0]
            if kind in own:
                own.remove(kind); inherited += 1; print(f'{name}: {b} (inherited from Mulish)')
            else:
                print(f'{name}: {b}'); total += 1
    print(f'{args[0]}: {checked} glyphs checked, {total} problems, {inherited} inherited from Mulish')
    sys.exit(1 if total else 0)

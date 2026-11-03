"""Superscript and subscript letters and signs (x⁻¹, xⁿ, Wᵀ, aᵢ, xᵢⱼ, eˣ, 10⁻³, h₀, x₍ᵢ₎).

Glyphs. Every form is made from Torchlette Sans's own glyph (its round dots, wider
round letters, lower x-height and longer extenders included), scaled to the
superior and inferior figures Mulish already has (uni00B9 ..., uni2080 ...): the
same scale (the superior 1's height over the lining 1's, 0.6), the same positions
(superiors stand on y 282, inferiors on the inferior figures' baseline, which build.py
drops SUB_DROP, 0.31 of the x-height, below the line) and the same weight. Scaling thins every stroke by that 0.6; the outline is then grown
point by point (each point moves out along the bisector of its two edges' normals,
FreeType's embolden, with separate horizontal and vertical amounts) until the
scaled lowercase stem equals the superior 1's stem and the scaled 0's top equals
the superior 0's, in each style. A piecewise vertical map before the growth keeps
baseline, x-height, cap height and extender lengths exactly at 0.6 of the full
size afterwards. Left sidebearings are 0.6 of the source's, the advance 0.6 of the
source's plus the growth, as the superior figures are spaced.
In the post phase (after build.py's overlap removal and smooth-point pass) this
module's own glyphs lose the few kinks the growth leaves where it meets a sharp
inner corner (the crotch of r and R, the tail of y).

Encoded (production names uniXXXX):
  superscript lowercase  ᵃ ᵇ ᶜ ᵈ ᵉ ᶠ ᵍ ʰ ⁱ ʲ ᵏ ˡ ᵐ ⁿ ᵒ ᵖ ʳ ˢ ᵗ ᵘ ᵛ ʷ ˣ ʸ ᶻ (all but q)
  superscript capitals   ᴬ ᴮ ᴰ ᴱ ᴳ ᴴ ᴵ ᴶ ᴷ ᴸ ᴹ ᴺ ᴼ ᴾ ᴿ ᵀ ᵁ ⱽ ᵂ
  superscript signs      ⁺ ⁻ ⁼ ⁽ ⁾
  subscript lowercase    ₐ ₑ ₒ ₓ ₔ ₕ ₖ ₗ ₘ ₙ ₚ ₛ ₜ ᵢ ⱼ ᵣ ᵤ ᵥ
  subscript signs        ₊ ₋ ₌ ₍ ₎
Unencoded (Unicode has no code point): q.sups.supsub and b c d f g q w y z
.subs.supsub, so sups and subs cover the whole lowercase alphabet. The figures
(¹ ² ³ ⁰ ⁴-⁹, ₀-₉) are Mulish's (build.py lowers ₀-₉) and are left alone here.

Features. sups, subs and sinf (Mulish's tags, extended) map a-z, the capitals that
have a superscript form (sups only), + - (hyphen and U+2212) = ( ) to these forms.
Mulish's figure lookups for the same tags are untouched. The lookups go right after
the classes block, ahead of build.py's liga, ss01, ss16 ..., so ligatures and
ss16's logotypes cannot form from letters that are being raised or lowered; Mulish's
own fi and fl (which run before any compiled lookup) are split back into two
superiors or inferiors. Subs comes before sups, so with both on, subs wins, as it
does for Mulish's figures. Small caps (smcp, c2sc) still run first and win.

Changes nothing that exists: no outline, advance, mapping or lookup of build.py's.
All new code points are in U+02B0-02FF, U+1D2C-1D6A, U+1D9C-1DBF, U+2070-209C and
U+2C7C-2C7D; the last three ranges (and part of the first) need the Makefile's
UNICODES to grow to reach the web font (see verify_supsub.py).
"""
import math

# code point -> source glyph, kind ('sup' or 'sub'), vertical frame ('lc' or 'uc')
SUP_LC = {'a': 0x1D43, 'b': 0x1D47, 'c': 0x1D9C, 'd': 0x1D48, 'e': 0x1D49, 'f': 0x1DA0, 'g': 0x1D4D,
          'h': 0x02B0, 'i': 0x2071, 'j': 0x02B2, 'k': 0x1D4F, 'l': 0x02E1, 'm': 0x1D50, 'n': 0x207F,
          'o': 0x1D52, 'p': 0x1D56, 'q': None, 'r': 0x02B3, 's': 0x02E2, 't': 0x1D57, 'u': 0x1D58,
          'v': 0x1D5B, 'w': 0x02B7, 'x': 0x02E3, 'y': 0x02B8, 'z': 0x1DBB}
SUP_UC = {'A': 0x1D2C, 'B': 0x1D2E, 'D': 0x1D30, 'E': 0x1D31, 'G': 0x1D33, 'H': 0x1D34, 'I': 0x1D35,
          'J': 0x1D36, 'K': 0x1D37, 'L': 0x1D38, 'M': 0x1D39, 'N': 0x1D3A, 'O': 0x1D3C, 'P': 0x1D3E,
          'R': 0x1D3F, 'T': 0x1D40, 'U': 0x1D41, 'V': 0x2C7D, 'W': 0x1D42}
SUP_SIGN = {'plus': 0x207A, 'minus': 0x207B, 'equal': 0x207C, 'parenleft': 0x207D, 'parenright': 0x207E}
SUB_LC = {'a': 0x2090, 'b': None, 'c': None, 'd': None, 'e': 0x2091, 'f': None, 'g': None, 'h': 0x2095,
          'i': 0x1D62, 'j': 0x2C7C, 'k': 0x2096, 'l': 0x2097, 'm': 0x2098, 'n': 0x2099, 'o': 0x2092,
          'p': 0x209A, 'q': None, 'r': 0x1D63, 's': 0x209B, 't': 0x209C, 'u': 0x1D64, 'v': 0x1D65,
          'w': None, 'x': 0x2093, 'y': None, 'z': None}
SUB_EXTRA = {'uni0259': 0x2094}          # ₔ, the schwa: encoded, not in the a-z feature map
SUB_SIGN = {'plus': 0x208A, 'minus': 0x208B, 'equal': 0x208C, 'parenleft': 0x208D, 'parenright': 0x208E}


def _name(src, kind, uni):
    if uni is not None: return f'uni{uni:04X}'
    return f'{src}.{kind}s.supsub'


def _contours(ctx, name):
    """The glyph's contours (composites decomposed) as lists of [x, y, on-curve]."""
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    rec = DecomposingRecordingPen(ctx.gs); ctx.gs[name].draw(rec)
    out, cur = [], None
    for op, args in rec.value:
        if op == 'moveTo': cur = [[*args[0], True]]
        elif op == 'lineTo': cur.append([*args[0], True])
        elif op == 'qCurveTo':
            pts = list(args)
            if pts[-1] is None: cur = (cur or []) + [[*q, False] for q in pts[:-1]]; continue
            cur += [[*q, False] for q in pts[:-1]] + [[*pts[-1], True]]
        elif op == 'curveTo': raise ValueError(f'{name}: cubic outline')
        elif op in ('closePath', 'endPath'):
            if len(cur) > 1 and cur[-1][:2] == cur[0][:2] and cur[-1][2] and cur[0][2]: cur.pop()
            out.append(cur); cur = None
    return out


def _embolden(contours, ex, ey):
    """Grow the outline outwards by ex horizontally and ey vertically: each point moves
    along the bisector of its two edges' normals (FreeType's FT_Outline_EmboldenXY)."""
    area = 0.0
    for c in contours:
        for i in range(len(c)):
            x0, y0 = c[i - 1][:2]; x1, y1 = c[i][:2]; area += x0 * y1 - x1 * y0
    sgn = 1 if area < 0 else -1          # clockwise outers (TrueType): outward = (-dy, dx)
    out = []
    for c in contours:
        n = len(c); new = []
        for i in range(n):
            p = c[i]
            j = (i - 1) % n
            while j != i and c[j][:2] == p[:2]: j = (j - 1) % n
            k = (i + 1) % n
            while k != i and c[k][:2] == p[:2]: k = (k + 1) % n
            a, b = c[j], c[k]
            def nrm(u, v):
                L = math.hypot(v[0] - u[0], v[1] - u[1]) or 1
                return (-(v[1] - u[1]) / L * sgn, (v[0] - u[0]) / L * sgn)
            n1, n2 = nrm(a, p), nrm(p, b)
            d = 1 + n1[0] * n2[0] + n1[1] * n2[1]
            d = max(d, 0.5)                   # miter limit: at most twice the offset at sharp corners
            sx, sy = (n1[0] + n2[0]) / d, (n1[1] + n2[1]) / d
            new.append([p[0] + sx * ex, p[1] + sy * ey, p[2]])
        # an on-curve point between two handles that were in line with it stays on
        # the line through the moved handles, at the same ratio
        for i in range(n):
            a, p, b = c[i - 1], c[i], c[(i + 1) % n]
            if not p[2] or a[2] or b[2]: continue
            ux, uy, vx, vy = p[0] - a[0], p[1] - a[1], b[0] - p[0], b[1] - p[1]
            lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
            if lu == 0 or lv == 0 or abs(ux * vy - uy * vx) > 0.02 * lu * lv or ux * vx + uy * vy <= 0: continue
            r = lu / (lu + lv); A, B = new[i - 1], new[(i + 1) % n]
            new[i][0], new[i][1] = A[0] + r * (B[0] - A[0]), A[1] + r * (B[1] - A[1])
        out.append(new)
    return out


def _path(ctx, contours):
    import pathops
    p = pathops.Path(); pen = p.getPen()
    for c in contours:
        # start at an on-curve point
        s = next((i for i, q in enumerate(c) if q[2]), None)
        if s is None:
            pen.qCurveTo(*[tuple(q[:2]) for q in c], None); continue
        c = c[s:] + c[:s]
        pen.moveTo(tuple(c[0][:2])); offs = []
        for q in c[1:] + [c[0]]:
            if q[2]:
                if offs: pen.qCurveTo(*offs, tuple(q[:2])); offs = []
                else: pen.lineTo(tuple(q[:2]))
            else: offs.append(tuple(q[:2]))
        pen.closePath()
    return p


def _unkink(ctx, g):
    """Where the growth folds a curve into a sharp inner corner (the crotch of r, the
    tail of y), the overlap removal leaves a short handle and an on-curve point that
    turns 15-30 degrees just past the corner, too much for build.py's smooth-point
    pass. Drop that handle and that point: the curve then starts at the corner."""
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    from array import array
    def turn(a, p, b):
        u, v = (p[0] - a[0], p[1] - a[1]), (b[0] - p[0], b[1] - p[1])
        if u == (0, 0) or v == (0, 0): return 180.0
        return abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))
    changed = True
    while changed:
        changed = False
        c = [tuple(q) for q in g.coordinates]; on = [bool(x & 1) for x in g.flags]; s0 = 0; cont = []
        for e in g.endPtsOfContours: cont.append(list(range(s0, e + 1))); s0 = e + 1
        for idx in cont:
            n = len(idx)
            for k in range(n):
                i, a, b = idx[k], idx[k - 1], idx[(k + 1) % n]
                if not on[i] or on[a] or on[b] or n < 6: continue
                if not 3 < turn(c[a], c[i], c[b]) < 30: continue
                short = min((a, b), key=lambda j: math.dist(c[i], c[j]))
                far = idx[k - 2] if short == a else idx[(k + 2) % n]
                if math.dist(c[i], c[short]) < 6 and on[far]:
                    drop = {i, short}; changed = True; break
            for k in range(n):                      # a curve running into a straight line:
                i, a, b = idx[k], idx[k - 1], idx[(k + 1) % n]   # its handle onto the line
                if not on[i] or on[a] == on[b]: continue
                h, o = (b, a) if on[a] else (a, b)
                t = turn(c[o], c[i], c[h]) if o == a else turn(c[h], c[i], c[o])
                if not 3 < t < 30: continue
                d = (c[i][0] - c[o][0], c[i][1] - c[o][1]); L = math.hypot(*d); r = math.dist(c[i], c[h])
                c[h] = (round(c[i][0] + d[0] / L * r), round(c[i][1] + d[1] / L * r))
                g.coordinates = GlyphCoordinates(c)
            if changed: break
        if changed:
            keep = [j for j in range(len(c)) if j not in drop]
            ends, m = [], -1
            for idx in cont:
                m += sum(1 for j in idx if j not in drop); ends.append(m)
            g.coordinates = GlyphCoordinates([c[j] for j in keep])
            g.flags = array('B', [1 if on[j] else 0 for j in keep]); g.endPtsOfContours = ends
    ctx.tidy(g); g.recalcBounds(ctx.glyf)


def post(ctx):
    # after build.py's overlap removal and smooth-point pass, which may leave a kink
    # where the growth met a sharp inner corner; only this module's glyphs are touched
    for src, name, kind, uni in ctx.made:
        g = ctx.glyf[name]; _unkink(ctx, g)
        ctx.hmtx[name] = (ctx.hmtx[name][0], g.xMin)


def glyphs(ctx):
    path_of, hspans, vspans = ctx.path_of, ctx.hspans, ctx.vspans
    b1, bone = path_of('uni00B9').bounds, path_of('one').bounds
    S = round((b1[3] - b1[1]) / (bone[3] - bone[1]), 4)                       # 0.6
    BASE = {'sup': round(b1[1]), 'sub': round(path_of('uni2081').bounds[1])}   # 282, -SUB_DROP
    stem = lambda n, y: (lambda s: s[1] - s[0])(hspans(path_of(n), y)[0])
    top = lambda n: (lambda s: s[1] - s[0])(vspans(path_of(n), (lambda b: (b[0] + b[2]) / 2)(path_of(n).bounds))[-1])
    EX = (ctx.SUP_STEM - S * stem('n', 200)) / 2                              # per side
    EY = (top('uni2070') - S * top('zero')) / 2
    ctx.log(f'{ctx.STYLE}: scale {S}, superiors on {BASE["sup"]}, inferiors on {BASE["sub"]}, '
            f'growth {EX:.1f} x {EY:.1f} per side (stem {S * stem("n", 200):.1f} -> {ctx.SUP_STEM:g}, '
            f'0 top {S * top("zero"):.1f} -> {top("uni2070"):g})')
    H = {'lc': ctx.XH, 'uc': 705}

    def make(src, name, kind, frame, uni):
        h = H[frame]
        def ymap(y):                       # baseline -> EY, frame top -> S*h - EY; slope S beyond
            if y <= 0: return EY + S * y
            if y >= h: return S * h - EY + S * (y - h)
            return EY + y * (S * h - 2 * EY) / h
        cs = [[[S * x + EX, ymap(y), on] for x, y, on in c] for c in _contours(ctx, src)]
        cs = _embolden(cs, EX, EY)
        cs = [[[x, y + BASE[kind], on] for x, y, on in c] for c in cs]
        ctx.add(name, _path(ctx, cs), S * ctx.W(src) + 2 * EX)
        ctx.GDEF_CLASS[name] = 1
        if uni is not None: ctx.map(uni, name)
        ctx.made.append((src, name, kind, uni))

    ctx.made = []
    for table, kind, frame in ((SUP_LC, 'sup', 'lc'), (SUP_UC, 'sup', 'uc'), (SUP_SIGN, 'sup', 'uc'),
                               (SUB_LC, 'sub', 'lc'), (SUB_EXTRA, 'sub', 'lc'), (SUB_SIGN, 'sub', 'uc')):
        for src, uni in table.items():
            make(src, _name(src, kind, uni), kind, frame, uni)
    ctx.log(f'{len(ctx.made)} glyphs, {sum(1 for m in ctx.made if m[3] is not None)} encoded')


def features(ctx):
    def maps(kind):
        m = {src: name for src, name, k, uni in ctx.made if k == kind and src in
             set(SUP_LC) | set(SUP_UC) | set(SUP_SIGN)}
        m['hyphen'] = m['minus']
        return m
    sup, sub = maps('sup'), maps('sub')
    def single(name, m): return f'lookup {name} {{\n' + ''.join(f'  sub {a} by {b};\n' for a, b in sorted(m.items())) + f'}} {name};\n'
    def split(name, m): return (f'lookup {name} {{\n  sub fi by {m["f"]} {m["i"]};\n  sub fl by {m["f"]} {m["l"]};\n}} {name};\n')
    ctx.gsub(split('SUPSUB_SUBS_FI', sub) + single('SUPSUB_SUBS', sub) +
             split('SUPSUB_SUPS_FI', sup) + single('SUPSUB_SUPS', sup) +
             'feature subs {\n  lookup SUPSUB_SUBS_FI;\n  lookup SUPSUB_SUBS;\n} subs;\n'
             'feature sinf {\n  lookup SUPSUB_SUBS_FI;\n  lookup SUPSUB_SUBS;\n} sinf;\n'
             'feature sups {\n  lookup SUPSUB_SUPS_FI;\n  lookup SUPSUB_SUPS;\n} sups;\n', after='classes')

"""tensordiagram: Penrose tensor-diagram glyphs that compose by typing, so lesson prose can
draw a tensor network inside a sentence (repertoire item SH3).

The notation. A tensor is a node with one leg per axis: a scalar has none, a vector one, a
matrix two, an order-3 tensor three. A contraction is a joined leg, so a matrix product is
two nodes sharing a leg; a trace (or any einsum that sums an index against itself) is a
loop. This is Penrose's graphical notation ("Applications of negative dimensional tensors",
1971: tensors as shapes, each index a line, upper indices as legs up and lower ones as legs
down, contraction as a joined line) in the horizontal form modern tensor-network notes use
(tensornetwork.org/diagrams: "shapes (usually filled or shaded)", "lines emanating from
these shapes", joined lines contract, a line joining two legs of one tensor is a trace,
identity is a plain line; Bridgeman and Chubb, "Hand-waving and interpretive dance",
arXiv:1603.03039, section 1: matrices as nodes with a left and a right leg, AB as two nodes
on one line, Tr(X) and Tr(AB) as a line leaving the right leg and running back over the top
to the left leg with rounded corners). Measured from Bridgeman and Chubb's table and
eq. 1.6, not copied: a joined leg is about 0.9 of a node, a free leg about 0.7, the trace
line runs about 0.3 of a node above the node's top and turns with a radius about 0.4 of its
rise. No outline is taken from any source; everything is drawn here from this style's own
strokes. Inline the loop is drawn tighter than that (see Sizes): a loop line 0.3 of a node
up lifts a trace to the cap height and past it, so it reads as sitting above the line; the
whole trace is also lowered so that it is centred on the math axis.

The glyphs (Private Use Area U+EE00-EE07, plus unencoded variants):

    U+EE00  dot node        a filled circle: the generic tensor
    U+EE01  ring node       an open circle, stroked like o
    U+EE02  box node        an open square: a special tensor (Penrose's boxes, a unitary)
    U+EE03  wire            a leg segment on the math axis, edge to edge: tiles seamlessly
    U+EE04  up leg          after a node: a leg up from it (Penrose's upper index)
    U+EE05  down leg        after a node: a leg down from it (a lower index)
    U+EE06  loop open       a line from the axis that turns up and runs right over the top
    U+EE07  loop close      its mirror image

Shaping (`calt`, so PUA text composes with default features; nothing else is touched): a
node followed by up and/or down legs becomes one glyph with those legs; a node next to a wire
or a loop end grows a stub to the glyph edge on that side, so `node wire node` is one
unbroken line; every node and wire between a loop open and a loop close takes a variant
with the loop's top line across its whole advance. 3 node shapes x 16 leg sets (left,
right, up, down) x with and without the loop line = 96 node glyphs; 114 glyphs in all.

ASCII triggers (`ss20`, "Tensor diagrams"; off by default, so default text is unchanged):
a diagram is written in square brackets, which vanish (each becomes a 40-unit space):

    [*]      scalar            *  dot node      o  ring node     #  box node
    [*-]     vector            -  leg / wire    ^  up leg        _  down leg (after a node)
    [-*-]    matrix            (  )  loop open and close
    [-*^-]   order-3 tensor    a space inside the brackets is a gap
    [-*-*-]  matrix product A B
    [-*-*]   matrix-vector product A v
    [(-*-)]  trace Tr A;  [(-*-*-)]  Tr(A B)

A bracket run converts only when it is a whole diagram: it opens with `[` and a trigger
character, holds only trigger characters, and is closed by `]`; anything else stays text
(`[-1, 2]`, `[--version]`, an unclosed `[o-`). This takes three passes through nine empty
pending glyphs (`*.pend.tensordiagram`, see `features`). ss20's lookups run before ss16 and
the figure features (after `classes`), so they see plain characters. The PUA block stays
clear of the fleurons' U+E000-E2FF. The nine node glyphs that TENSORDIAGRAM_UD forms (node
plus up and/or down leg) are GDEF ligatures.

Strokes. The horizontal strokes (legs, wires, the loop line, the tops of the ring and box)
take the font's horizontal stem, the T bar (58 at Regular, build.py's SH measure); the
vertical ones (up and down legs, the loop's turn, the sides of the ring and box) the
vertical stem, the t stem (66 at Regular, SV's), the contrast the letters themselves have.
Every horizontal leg is centred on the math axis (`LIN_AXIS`, the minus's centre).

Sizes (font units): the node is 480 across at Regular (the o's height with its overshoot),
centred on the axis, and grows by 0.8 of the stem's excess over Regular's, as o widens
(467 Light, 522 Bold, 558 Black), so the hollow nodes keep a counter; the dot is 0.96 of it,
the box 0.86 (filled and square shapes look larger); the ring and box are wider than tall by
their sides' extra weight, as o is, so their counters are round and square, and legs stop at
their outer edge. A 50-unit stub on each side of a node and a 300-unit wire make a free leg
350 (0.73 of a node) and a joined one 400 (0.83); up and down legs reach the ascender and the
descender less 30, symmetric about the axis. The loop line's underside clears the node's top
by 45 at every weight (a little under a pixel at 18 px), so the loop hugs the node, and the
whole trace (loop ends, wires and nodes between them) drops by DROP, half of what the loop adds
above the node ((45 + the T bar) / 2: 52 at Regular, 90 at Black), so that the ink from the
node's bottom to the loop's top is centred on the axis. A trace's top is then 578 at Regular
and 657 at Black, and its nodes sit DROP below the nodes of the diagrams beside it. (Round 2
kept the nodes on the axis, which put the top at 630 at Regular and 748 at Black, which read as sitting above the line.) The loop turns with a centre-line radius of 0.4 of its
rise.

Italics. Diagrams are pictures: in an italic style each glyph is drawn where the reslant
will put it and sheared back about the axis (as the ui module does), so it stands upright;
every glyph takes the same shift, so wires still tile. Every bar that meets a glyph edge runs 2
units past it, so neighbours overlap and renderers show no antialiasing seam at the join.

Limits: an up leg inside a loop meets the loop line. Nothing existing is changed. Feature tag
registered: ss20 (codekeys holds ss17-ss19). Lookups TENSORDIAGRAM_*, class names @TENSORDIAGRAM_*. Code points outside
the Makefile's web subset ranges: U+EE00-EE07; ss20 is not in web_features.txt.
"""
import itertools

PUA = {'dot': 0xEE00, 'ring': 0xEE01, 'box': 0xEE02, 'wire': 0xEE03, 'up': 0xEE04, 'down': 0xEE05,
       'lopen': 0xEE06, 'lclose': 0xEE07}
G = {k: f'uni{v:04X}' for k, v in PUA.items()}
SUF = '.tensordiagram'
NODES = ('dot', 'ring', 'box')
LEGSETS = [''.join(s) for n in range(5) for s in itertools.combinations('lrud', n)]   # '', 'l', ... 'lrud'

D = 480                      # node across
STUB = 50                    # a node glyph's side, where its horizontal legs start
WIRE = 300                   # the wire's advance
LOOP_CLEAR = 45              # clear space between the node's top and the loop line's underside
OPEN = 40                    # the vanishing brackets' advance
OVL = 2                      # bars that meet a glyph edge run this far past it, so abutting glyphs
                             # overlap and no antialiasing seam shows where they join


TRIG = 'o asterisk numbersign hyphen parenleft parenright asciicircum underscore space'.split()
TARG = [G[k] for k in ('ring', 'dot', 'box', 'wire', 'lopen', 'lclose', 'up', 'down')] + ['space' + SUF]
PEND = [t.replace(SUF, '') + '.pend' + SUF for t in TARG]


def node_name(kind, legs='', trk=False):
    if not legs and not trk: return G[kind]
    return G[kind] + '.' + (legs or 'n') + ('t' if trk else '') + SUF


def wire_name(trk=False): return G['wire'] + ('.t' + SUF if trk else '')


def glyphs(ctx):
    c = ctx
    rect, union, diff, clip, ellipse, mv, transformed = c.rect, c.union, c.diff, c.clip, c.ellipse, c.mv, c.transformed
    path_of, hspans, vspans = c.path_of, c.hspans, c.vspans
    K, YC, A = c.ITALIC_K, c.ITALIC_YC, c.LIN_AXIS
    order = set(c.font.getGlyphOrder()); cmap = c.font.getBestCmap()
    made = ctx.made = []

    t = path_of('t'); ts = hspans(t, 300)[0]; V = ts[1] - ts[0]           # vertical stem: t stem
    T = path_of('T'); Tb = T.bounds
    HS = Tb[3] - vspans(T, Tb[0] + 50)[-1][0]                                 # horizontal stem: T bar
    asc = path_of('l').bounds[3]; desc = path_of('p').bounds[1]
    ctx.dims = dict(V=V, HS=HS, A=A)

    def upright(p):
        if not K: return p
        return transformed(mv(p, K * (A - YC)), (1, 0, -K, 1, K * YC, 0))

    def put(name, p, adv, cp=None):
        assert name not in order, name
        if cp is not None: assert cp not in cmap, f'U+{cp:04X} already mapped'
        c.add(name, upright(p) if p is not None else c.rect(0, 0, 0, 0), adv)
        c.GDEF_CLASS[name] = 1
        if cp is not None: ctx.map(cp, name)
        made.append(name)

    hbar = lambda x0, x1, y=A: rect(x0, y - HS / 2, x1, y + HS / 2)
    vbar = lambda x, y0, y1: rect(x - V / 2, y0, x + V / 2, y1)

    # the nodes grow with the stroke as o does (Black's o is 0.8 of its extra stem wider than
    # Regular's), so the ring and the box keep a counter
    DN = D + 0.8 * (V - V / c.SV); RN = DN / 2; top = A + RN
    LV = min(asc - 30 - top, (A - RN) - (desc + 30)); YT = top + LOOP_CLEAR + HS / 2
    # a trace is centred on the axis as a whole: everything between and including the loop ends
    # drops by half of what the loop adds above the node, so the ink from the node's bottom to the
    # loop's top is centred on the axis (the nodes inside sit DROP below the diagrams beside them)
    DROP = (YT + HS / 2 - top) / 2
    ctx.dims.update(DN=DN, LV=LV, YT=YT, DROP=DROP)
    adv_n = round(DN + 2 * STUB); cx = adv_n / 2; bh = 0.43 * DN
    # the ring and the box are wider than tall by their sides' extra weight (V - HS), as o is,
    # so their counters come out round and square
    ex = (V - HS) / 2
    counters = {'dot': None, 'ring': ellipse(cx, A, RN - HS, RN - HS),
                'box': rect(cx - bh + HS, A - bh + HS, cx + bh - HS, A + bh - HS)}
    outlines = {'dot': ellipse(cx, A, 0.48 * DN, 0.48 * DN), 'ring': ellipse(cx, A, RN + ex, RN),
                'box': rect(cx - bh - ex, A - bh, cx + bh + ex, A + bh)}
    for kind in NODES:
        for legs in LEGSETS:
            for trk in (False, True):
                parts = [outlines[kind]]
                if 'l' in legs: parts.append(hbar(-OVL, cx))
                if 'r' in legs: parts.append(hbar(cx, adv_n + OVL))
                if 'u' in legs: parts.append(vbar(cx, A, top + LV))
                if 'd' in legs: parts.append(vbar(cx, A - RN - LV, A))
                p = union(*parts)
                if counters[kind] is not None: p = diff(p, counters[kind])     # legs stop at a hollow node's edge
                if trk: p = mv(union(p, hbar(-OVL, adv_n + OVL, YT)), 0, -DROP)
                name = node_name(kind, legs, trk)
                put(name, p, adv_n, PUA[kind] if name == G[kind] else None)
                if legs in ('u', 'd', 'ud') and not trk: c.GDEF_CLASS[name] = 2   # TENSORDIAGRAM_UD's ligatures

    put(wire_name(), hbar(-OVL, WIRE + OVL), WIRE, PUA['wire'])
    put(wire_name(True), mv(union(hbar(-OVL, WIRE + OVL), hbar(-OVL, WIRE + OVL, YT)), 0, -DROP), WIRE)
    m = 60                                                                    # the free modifiers' sides
    put(G['up'], vbar(m + V / 2, A, top + LV), round(2 * m + V), PUA['up'])
    put(G['down'], vbar(m + V / 2, A - RN - LV, A), round(2 * m + V), PUA['down'])

    # loop ends: a rounded rectangle's left side, clipped at the glyph's right edge
    rise = YT - A; rc = 0.4 * rise; xc = 40 + V / 2; adv_l = round(xc + rc + 60)
    outer = c.rrect(xc - V / 2, A - HS / 2, adv_l + 400, YT + HS / 2, rc + (V + HS) / 4)
    inner = c.rrect(xc + V / 2, A + HS / 2, adv_l + 400, YT - HS / 2, max(10, rc - (V + HS) / 4))
    lo = mv(clip(diff(outer, inner), (-100, -1000, adv_l + OVL, 2000)), 0, -DROP)
    put(G['lopen'], lo, adv_l, PUA['lopen'])
    put(G['lclose'], c.mirror(lo, adv_l / 2), adv_l, PUA['lclose'])

    put('open' + SUF, None, OPEN)
    put('close' + SUF, None, OPEN)
    put('space' + SUF, None, c.W('space'))
    for b in TARG:                                                            # ss20's pending forms (see features)
        put(b.replace(SUF, '') + '.pend' + SUF, None, c.W(b))
    ctx.log(f'strokes: vertical {V:.0f} (t stem), horizontal {HS:.0f} (T bar); axis {A}; node {DN:.0f}; legs {LV:.0f}; loop line {YT:.0f}; trace dropped {DROP:.0f}; {len(made)} glyphs')


def features(ctx):
    nodes0 = [node_name(k, l) for k in NODES for l in LEGSETS]
    base = [G[k] for k in NODES]
    trig, targ, pend = ' '.join(TRIG), ' '.join(TARG), ' '.join(PEND)
    # ss20 in three passes, so a bracket run converts only when it is closed: forward, an
    # opening bracket followed by trigger characters becomes `open`, and the characters after
    # it pending forms (empty placeholders), up to a closing bracket; backward, a pending form
    # followed by `close` or by a confirmed glyph is confirmed (the real glyph); forward again,
    # whatever is still pending, and an `open` not followed by a confirmed glyph, turn back into
    # the characters they were, so `[--version]` or an unclosed `[o-` stays text.
    ascii_ = f'''
lookup TENSORDIAGRAM_OPEN {{
  sub bracketleft' [o asterisk numbersign hyphen parenleft] [{trig} bracketright] by open{SUF};
}} TENSORDIAGRAM_OPEN;
lookup TENSORDIAGRAM_BODY {{
  sub [open{SUF} {pend}] [{trig}]' by [{pend}];
  sub [{pend}] bracketright' by close{SUF};
}} TENSORDIAGRAM_BODY;
lookup TENSORDIAGRAM_CONFIRM {{
  rsub [{pend}]' [close{SUF} {targ}] by [{targ}];
}} TENSORDIAGRAM_CONFIRM;
lookup TENSORDIAGRAM_REVERT {{
  ignore sub open{SUF}' [{targ}];
  sub open{SUF}' by bracketleft;
  sub [{pend}]' by [{trig}];
}} TENSORDIAGRAM_REVERT;
'''
    # node + up/down legs -> one glyph
    lig = []
    for k in NODES:
        n = G[k]
        lig += [f"  sub {n} {G['up']} {G['down']} by {node_name(k, 'ud')};",
                f"  sub {n} {G['down']} {G['up']} by {node_name(k, 'ud')};",
                f"  sub {n} {G['up']} by {node_name(k, 'u')};",
                f"  sub {n} {G['down']} by {node_name(k, 'd')};"]
    ud = ['', 'u', 'd', 'ud']
    srcR = [node_name(k, l) for k in NODES for l in ud]
    dstR = [node_name(k, 'r' + l) for k in NODES for l in ud]
    srcL = [node_name(k, r + l) for k in NODES for r in ('', 'r') for l in ud]
    dstL = [node_name(k, 'l' + r + l) for k in NODES for r in ('', 'r') for l in ud]
    trkable = nodes0 + [wire_name()]
    trked = [node_name(k, l, True) for k in NODES for l in LEGSETS] + [wire_name(True)]
    attach = f'''
@TENSORDIAGRAM_TRKABLE = [{' '.join(trkable)}];
@TENSORDIAGRAM_TRKED = [{' '.join(trked)}];
lookup TENSORDIAGRAM_UD {{
{chr(10).join(lig)}
}} TENSORDIAGRAM_UD;
lookup TENSORDIAGRAM_RIGHT {{
  sub [{' '.join(srcR)}]' [{G['wire']} {G['lclose']}] by [{' '.join(dstR)}];
}} TENSORDIAGRAM_RIGHT;
lookup TENSORDIAGRAM_LEFT {{
  sub [{G['wire']} {G['lopen']}] [{' '.join(srcL)}]' by [{' '.join(dstL)}];
}} TENSORDIAGRAM_LEFT;
lookup TENSORDIAGRAM_LOOP {{
  rsub @TENSORDIAGRAM_TRKABLE' [{G['lclose']} @TENSORDIAGRAM_TRKED] by @TENSORDIAGRAM_TRKED;
}} TENSORDIAGRAM_LOOP;
lookup TENSORDIAGRAM_UNLOOP {{
  ignore sub [{G['lopen']} @TENSORDIAGRAM_TRKED] @TENSORDIAGRAM_TRKED';
  sub @TENSORDIAGRAM_TRKED' by @TENSORDIAGRAM_TRKABLE;
}} TENSORDIAGRAM_UNLOOP;
'''
    names = ['TENSORDIAGRAM_UD', 'TENSORDIAGRAM_RIGHT', 'TENSORDIAGRAM_LEFT', 'TENSORDIAGRAM_LOOP', 'TENSORDIAGRAM_UNLOOP']
    refs = ''.join(f'  lookup {n};\n' for n in names)
    feas = (f'feature ss20 {{\n  featureNames {{ name "Tensor diagrams"; }};\n  lookup TENSORDIAGRAM_OPEN;\n  lookup TENSORDIAGRAM_BODY;\n  lookup TENSORDIAGRAM_CONFIRM;\n  lookup TENSORDIAGRAM_REVERT;\n{refs}}} ss20;\n'
            f'feature calt {{\n{refs}}} calt;\n')
    ctx.gsub(ascii_ + attach + feas, after='classes')

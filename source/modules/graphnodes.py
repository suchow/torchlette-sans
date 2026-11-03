"""Opt-in inline graphical-model nodes (SH5), proposed registered cv82.

Add three unencoded simple glyphs, not replacements for UI glyphs. The module
can draw in alphabetical glyph-phase order before mathnotation/ui: it uses
ctx.XH, LIN_AXIS and BAR and independent circle geometry. features() validates
all three existing cmap sources only AFTER all modules' glyph phases. Missing
sources fail, not silent partial coverage. post() rejects a colliding compiled
cv82 mapping/parameters. A final pending-source tag inventory is still required.

Diameter is XH, centred on LIN_AXIS, with 60-unit sidebearings and one common
advance. Ring weight follows the minus BAR, limited to XH/5 to retain its counter
at heavy weights; the observed disc grows with that ring stroke. Italic pictures
are counter-sheared about the math axis using the same frame convention as UI,
not resized copies of approved UI outlines. Feature off leaves those untouched.
Plates remain SVG. No cmap, source glyph or original layout override is declared.
"""
TAG = 'cv82'
VARIANTS = {0x25CB: 'latent.graphnodes', 0x25C9: 'observed.graphnodes',
            0x25CF: 'filled.graphnodes'}


def _sources(ctx):
    cmap = ctx.font.getBestCmap()
    missing = [f'U+{cp:04X}' for cp in VARIANTS if cp not in cmap
               or cmap[cp] not in ctx.font.getGlyphOrder()]
    if missing:
        raise ValueError('graphnodes requires ui and mathnotation glyph phases: ' + ', '.join(missing))
    if len({cmap[cp] for cp in VARIANTS}) != 3:
        raise ValueError('graphnodes needs three distinct source glyphs')
    return {cp: cmap[cp] for cp in VARIANTS}


def glyphs(ctx):
    if 'GSUB' in ctx.font and any(r.FeatureTag == TAG for r in ctx.font['GSUB'].table.FeatureList.FeatureRecord):
        raise ValueError('graphnodes tag already present: ' + TAG)
    if set(VARIANTS.values()) & set(ctx.font.getGlyphOrder()):
        raise ValueError('graphnodes glyph-name collision')
    d, axis = float(ctx.XH), float(ctx.LIN_AXIS)
    stroke = min(float(ctx.BAR), d / 5)
    if not (d > 0 and 0 < stroke < d / 2):
        raise ValueError('graphnodes invalid diameter/stroke')
    r, cx = d / 2, 60 + d / 2
    disc = 0.12 * d + 0.25 * stroke
    if r - stroke - disc < d / 10:
        raise ValueError('graphnodes observed node has insufficient white annulus')
    outer = ctx.ellipse(cx, axis, r, r)
    ring = ctx.diff(outer, ctx.ellipse(cx, axis, r - stroke, r - stroke))
    paths = [ring, ctx.union(ring, ctx.ellipse(cx, axis, disc, disc)), outer]
    for name, p in zip(VARIANTS.values(), paths):
        if ctx.ITALIC_K:
            k = ctx.ITALIC_K
            p = ctx.transformed(p, (1, 0, -k, 1, k * axis, 0))
        ctx.add(name, p, d + 120)
        ctx.GDEF_CLASS[name] = 1
    ctx.graphnodes_metrics = dict(diameter=d, axis=axis, stroke=stroke, disc=disc,
                                  advance=d + 120)


def features(ctx):
    sources = _sources(ctx)
    if not all(n in ctx.font.getGlyphOrder() for n in VARIANTS.values()):
        raise ValueError('graphnodes glyph phase did not complete')
    params = '\n'.join(f'    Character 0x{cp:04X};' for cp in VARIANTS)
    subs = '\n'.join(f'  sub {sources[cp]} by {name};' for cp, name in VARIANTS.items())
    ctx.gsub(f'''feature {TAG} {{
  cvParameters {{
    FeatUILabelNameID {{ name "Inline graphical-model nodes"; }};
{params}
  }};
{subs}
}} {TAG};''', after='ss16')


def post(ctx):
    """Fail closed on compiled tag collision; no table or outline edits here."""
    sources = _sources(ctx)
    if 'GSUB' not in ctx.font:
        raise ValueError('graphnodes GSUB missing')
    table = ctx.font['GSUB'].table
    records = [r for r in table.FeatureList.FeatureRecord if r.FeatureTag == TAG]
    if len(records) != 1:
        raise ValueError('graphnodes compiled tag collision/missing feature')
    feature = records[0].Feature
    p = feature.FeatureParams
    if p is None or sorted(p.Character) != sorted(VARIANTS):
        raise ValueError('graphnodes compiled cvParameters mismatch')
    mapping = {}
    for i in feature.LookupListIndex:
        lk = table.LookupList.Lookup[i]
        if lk.LookupType != 1 or lk.LookupFlag != 0:
            raise ValueError('graphnodes unexpected compiled lookup')
        for st in lk.SubTable:
            for old, new in st.mapping.items():
                if old in mapping:
                    raise ValueError('graphnodes duplicate mapping')
                mapping[old] = new
    if mapping != {sources[cp]: name for cp, name in VARIANTS.items()}:
        raise ValueError('graphnodes compiled mapping collision')

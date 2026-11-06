"""meta: the font's metadata and its .notdef.

Tables only, apart from one outline (.notdef, listed in GLYPH_OVERRIDE): no glyph advance, cmap entry or shaping rule
changes. In order of the phases:

glyphs    .notdef (build.py's, empty in Mulish) becomes a slashed box in this
          style's weight: the sides take H's stem, the top and bottom H's bar, the
          slash 0.6 of the stem; cap height tall, advance 500 as before. This edits a glyph
          of the shared font.
features  UI names (featureNames for ssNN, cvParameters FeatUILabelNameID for cvNN)
          for every ss and cv tag of build.py's feature text, and of modules that ran
          before this one, that lacks one (ss16 has its own). Tags of modules named
          after `meta` must name themselves. No lookups are added.
post      name: no Mac records; IDs 3 (unique ID with the vendor), 9, 10, 11, 12.
          OS/2: fsSelection (REGULAR for every upright non-bold style, so SemiBold
          too, as its legacy subfamily is Regular), achVendID, xAvgCharWidth and
          usMaxContext recomputed, Unicode ranges recomputed, PANOSE, fsType 0,
          usWinAscent/Descent with headroom; typo and hhea are kept (they set the
          app's line box).
          STAT: axes wght and ital; this font's own axis values only, as the spec's
          non-variable examples do (Regular 400 elidable linked to Bold 700, ital 0
          Roman elidable linked to 1). WEIGHTS names every standard weight, so a
          Light, Medium, ExtraBold or Black style needs no change here.
          GDEF: ligature carets for the letter ligatures (liga, ss01, ss03, ss07,
          ss16) that have none; glyph classes are left alone.
          meta: dlng Latn, slng from the cmap's scripts.
          Unreferenced name records of ID 256 and up are dropped.
          Last, ttfautohint, if ttfautohint-py is installed (see HINT_OPTIONS): it
          adds fpgm, cvt, prep, gasp and glyph programs and changes no outline; head
          flags get bit 3 (integer ppem), as hinted fonts need. Modules that run
          after this one must not change outlines in their own post phase.

Takes no feature tag. Adds no glyph.
"""
import re
import unicodedata

GLYPH_OVERRIDE = {'.notdef'}   # build.py's (Mulish's) empty .notdef gets an outline

VENDOR = 'TRLT'          # not in Microsoft's registered vendor list (checked 2026-11-01)
REPO = 'https://github.com/suchow/torchlette-sans'
DESIGNER = 'The Torchlette Authors; Vernon Adams (Mulish)'
DESCRIPTION = ('Torchlette Sans is the text face of torchlette, a modified version of Mulish '
               'with round dots, a lower x-height, old-style figures, true small capitals '
               'and the Torchlette prose ligatures.')
# usWinAscent/Descent, the same in every style: the tallest glyph (U+1E66, a stacked
# caron and dot) reaches 1044 in Regular, 1059 in Bold, 1065 in ExtraBold; the deepest
# (cedilla and comma-below capitals) -270, -277, -282. The headroom is for Greek with
# tonos and dialytika, superiors, arrows and Black. math_table's tall slanted radicals
# (up to 6000, centred at 240: -2760..3240) set the values now. USE_TYPO_METRICS is on, so
# browsers and apps space lines by the typo/hhea metrics, which this does not change.
WIN_ASCENT, WIN_DESCENT = 3260, 2780
# ttfautohint, when build.py's interpreter has the pinned ttfautohint-py (the Makefile's
# PY line); without it the font stays unhinted, as before. The epoch keeps head.modified.
HINT_OPTIONS = dict(no_info=True, windows_compatibility=True, fallback_script='latn', epoch=1793404800)
# the standard weight names (OpenType usWeightClass, Google's axis registry)
WEIGHTS = {100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium',
           600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black'}

FEATURE_LABELS = {
    'ss01': 'Th ligature', 'ss02': 'Arrows, comparison signs, times sign, ellipsis',
    'ss03': 'th ligature', 'ss04': 'Two-storey a', 'ss05': 'Q with a straight tail',
    'ss06': 'Straight-tailed y', 'ss07': 'Alternate t', 'ss08': 'Plain 7',
    'ss15': 'Spark line', 'ss16': 'Torchlette prose ligatures',
    'cv01': 'fb ligature', 'cv02': 'fh ligature', 'cv03': 'fk ligature', 'cv04': 'fj ligature',
    'cv05': 'ft ligature', 'cv06': 'fft ligature', 'cv07': 'tf ligature', 'cv09': 'fy ligature',
    'cv16': 'tw ligature', 'cv22': 'ry ligature', 'cv23': 'rw ligature', 'cv24': 'll ligature',
    'cv25': 'rn spacing', 'cv26': 'cl spacing', 'cv50': 'TT ligature',
    'cv81': 'Torchlette logotype', 'cv84': 'network logotype', 'cv85': 'gradient logotype',
    'cv86': 'softmax logotype', 'cv88': 'Python logotype', 'cv90': 'Range dash',
    'cv91': 'True minus', 'cv92': 'Plus-minus sign', 'cv93': 'Approximately equal sign',
    'cv96': 'Ordinals', 'cv97': 'Vulgar fractions', 'cv98': 'Diagonal fractions',
    'cv99': 'Ratio colon',
}
_BLOCK = re.compile(r'\bfeature\s+((?:ss|cv)\d\d)\s*\{(.*?)\}\s*\1\s*;', re.S)


# --- glyphs ---------------------------------------------------------------------
def glyphs(ctx):
    H = ctx.path_of('H')
    sl, sr = ctx.hspans(H, 200)[0]                   # H's left stem
    bar = ctx.vspans(H, ctx.W('H') / 2)              # H's crossbar
    bar = [s for s in bar if 200 < ctx.mid(s) < 500][0]
    stem, hbar = sr - sl, bar[1] - bar[0]
    x0, x1, y0, y1 = 40, 460, 0, 705
    box = ctx.diff(ctx.rect(x0, y0, x1, y1), ctx.rect(x0 + stem, y0 + hbar, x1 - stem, y1 - hbar))
    slash = ctx.clip(ctx.band((x0, y0), (x1, y1), 0.6 * stem), (x0, y0, x1, y1))   # thinner, so Bold keeps its counters
    ctx.add('.notdef', ctx.union(box, slash), 500)
    ctx.log(f'.notdef: slashed box, stem {stem:g}, bar {hbar:g}')


# --- features -------------------------------------------------------------------
def features(ctx):
    texts = [ctx.FEA_HEAD, ctx.S16_FRONT, ctx.FEA_MAIN, ctx.ALT_FEA, ctx.S16_FEA]
    texts += [t for _, _, t in ctx.MODULE_GSUB]
    have, named = set(), set()
    for t in texts:
        for tag, body in _BLOCK.findall(t):
            have.add(tag)
            if 'featureNames' in body or 'cvParameters' in body: named.add(tag)
    out = []
    for tag in sorted(have - named):
        label = FEATURE_LABELS.get(tag)
        if label is None:
            ctx.log(f'{tag}: no UI name (not in FEATURE_LABELS)'); continue
        if tag.startswith('ss'):
            out.append(f'feature {tag} {{ featureNames {{ name "{label}"; }}; }} {tag};')
        else:
            out.append(f'feature {tag} {{ cvParameters {{ FeatUILabelNameID {{ name "{label}"; }}; }}; }} {tag};')
    ctx.gsub('\n'.join(out))
    ctx.log(f'UI names for {len(out)} features')


# --- post -----------------------------------------------------------------------
def _referenced_name_ids(font):
    ids = set()
    if 'STAT' in font:
        st = font['STAT'].table
        ids.add(st.ElidedFallbackNameID)
        for a in st.DesignAxisRecord.Axis: ids.add(a.AxisNameID)
        for v in (st.AxisValueArray.AxisValue if st.AxisValueArray else []): ids.add(v.ValueNameID)
    if 'fvar' in font:
        for a in font['fvar'].axes: ids.add(a.axisNameID)
        for i in font['fvar'].instances: ids.update({i.subfamilyNameID, i.postscriptNameID})
    for tag in ('GSUB', 'GPOS'):
        if tag not in font: continue
        for fr in font[tag].table.FeatureList.FeatureRecord:
            p = fr.Feature.FeatureParams
            if p is None: continue
            for k in ('UINameID', 'FeatUILabelNameID', 'FeatUITooltipTextNameID', 'SampleTextNameID', 'SubfamilyNameID'):
                if getattr(p, k, 0): ids.add(getattr(p, k))
            if getattr(p, 'FirstParamUILabelNameID', 0):
                ids.update(range(p.FirstParamUILabelNameID, p.FirstParamUILabelNameID + p.NumNamedParameters))
    return ids


def _stat(ctx):
    from fontTools.otlLib.builder import buildStatTable
    font, style = ctx.font, ctx.STYLE
    wc = ctx.WEIGHT_CLASS
    w = {'value': wc, 'name': WEIGHTS[wc]}
    if wc == 400: w.update(flags=0x2, linkedValue=700)
    italic = 'Italic' in style
    i = {'value': 1, 'name': 'Italic'} if italic else {'value': 0, 'name': 'Roman', 'flags': 0x2, 'linkedValue': 1}
    if 'STAT' in font: del font['STAT']
    buildStatTable(font, [dict(tag='wght', name='Weight', ordering=0, values=[w]),
                          dict(tag='ital', name='Italic', ordering=1, values=[i])],
                   elidedFallbackName='Regular', macNames=False)


# PANOSE weight digit by usWeightClass (Light 3, Book 5, Medium 6, Demi 7, Bold 8, Heavy
# 9, Black 10), as Windows' font matching pairs them. The spec's ratio (cap height
# over the stem) runs light for this design (Regular 10.7, "Thin"), and is logged.
PANOSE_WEIGHT = {100: 2, 200: 3, 300: 3, 400: 5, 500: 6, 600: 7, 700: 8, 800: 9, 900: 10}


def _panose(ctx):
    """PANOSE Latin Text digits: sans (normal), weight by class, modern proportions, no
    contrast or stroke variation, straight arms, round contact letterforms (oblique
    contact in the italics), pointed apex at a standard midline, x-height measured (over
    cap height: >0.66 is large)."""
    os2 = ctx.font['OS/2']
    l, r = ctx.hspans(ctx.path_of('H'), 150)[0]
    rat = os2.sCapHeight / (r - l)
    xr = os2.sxHeight / os2.sCapHeight
    xheight = 2 if xr <= 0.5 else 3 if xr <= 0.66 else 4
    letterform = 9 if 'Italic' in ctx.STYLE else 2
    p = os2.panose; weight = PANOSE_WEIGHT[ctx.WEIGHT_CLASS]
    (p.bFamilyType, p.bSerifStyle, p.bWeight, p.bProportion, p.bContrast, p.bStrokeVariation,
     p.bArmStyle, p.bLetterForm, p.bMidline, p.bXHeight) = (2, 11, weight, 3, 2, 2, 2, letterform, 3, xheight)
    return rat, weight


def _carets(ctx):
    """Carets at the joins of letter ligatures: each component's share of the
    ligature's advance is its own advance's share of the components' sum."""
    from fontTools.ttLib.tables import otTables as ot
    font = ctx.font; hmtx = font['hmtx']; gdef = font['GDEF'].table
    cmap = font.getBestCmap(); letters = {g for u, g in cmap.items() if unicodedata.category(chr(u))[0] == 'L'}
    have = {}
    if gdef.LigCaretList:
        have = dict(zip(gdef.LigCaretList.Coverage.glyphs, gdef.LigCaretList.LigGlyph))
    new = {}
    for lk in font['GSUB'].table.LookupList.Lookup:
        for st in lk.SubTable:
            if lk.LookupType == 7: st = st.ExtSubTable
            if getattr(st, 'LookupType', lk.LookupType) != 4: continue
            for first, ligs in st.ligatures.items():
                for lg in ligs:
                    g = lg.LigGlyph
                    if g in have or g in new: continue
                    parts = [p.split('.')[0] for p in [first] + list(lg.Component)]
                    if len(parts) < 2 or not all(p in letters for p in parts): continue
                    ws = [hmtx[p][0] for p in parts]; adv = hmtx[g][0]; acc = 0; pos = []
                    for wd in ws[:-1]:
                        acc += wd; pos.append(round(adv * acc / sum(ws)))
                    new[g] = pos
    if not new: return 0
    allg = {**{g: [c.Coordinate for c in lg.CaretValue] for g, lg in have.items()}, **new}
    order = font.getReverseGlyphMap()
    names = sorted(allg, key=order.get)
    cl = ot.LigCaretList(); cl.Coverage = ot.Coverage(); cl.Coverage.glyphs = names; cl.LigGlyph = []
    for g in names:
        if g in have: cl.LigGlyph.append(have[g]); continue
        lg = ot.LigGlyph(); lg.CaretValue = []
        for x in allg[g]:
            cv = ot.CaretValue(); cv.Format = 1; cv.Coordinate = x; lg.CaretValue.append(cv)
        lg.CaretCount = len(lg.CaretValue); cl.LigGlyph.append(lg)
    cl.LigGlyphCount = len(cl.LigGlyph); gdef.LigCaretList = cl
    return len(new)


def _meta_table(ctx):
    from fontTools.ttLib import newTable
    scripts = set()
    for u in ctx.font.getBestCmap():
        n = unicodedata.name(chr(u), '')
        if unicodedata.category(chr(u))[0] != 'L': continue
        scripts.add('Latn' if n.startswith('LATIN') else 'Grek' if n.startswith('GREEK') else
                    'Cyrl' if n.startswith('CYRILLIC') else None)
    scripts.discard(None)
    m = newTable('meta'); m.data = {'dlng': 'Latn', 'slng': ','.join(s for s in ('Latn', 'Grek', 'Cyrl') if s in scripts)}
    ctx.font['meta'] = m
    return m.data['slng']


def _hint(ctx):
    try:
        import ttfautohint
    except ImportError:
        return 'not hinted (no ttfautohint-py)'
    import io
    from fontTools.ttLib import TTFont
    font = ctx.font; buf = io.BytesIO(); font.save(buf)
    h = TTFont(io.BytesIO(ttfautohint.ttfautohint(in_buffer=buf.getvalue(), **HINT_OPTIONS)))
    if h.getGlyphOrder() != font.getGlyphOrder(): raise SystemExit('meta: ttfautohint changed the glyph order')
    for t in ('fpgm', 'prep', 'cvt ', 'gasp'):
        font[t] = h[t]
    glyf, hg = font['glyf'], h['glyf']; n = 0
    for name in font.getGlyphOrder():
        g = hg[name]
        if hasattr(g, 'program'):
            glyf[name].program = g.program; n += bool(g.program.getBytecode())
    for k in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs', 'maxInstructionDefs',
              'maxStackElements', 'maxSizeOfInstructions'):
        setattr(font['maxp'], k, getattr(h['maxp'], k))
    font['head'].flags |= h['head'].flags & (1 << 4 | 1 << 2) | 1 << 3
    return f'hinted: {n} glyph programs, ttfautohint-py {ttfautohint.__version__}'


def post(ctx):
    from fontTools.otlLib.maxContextCalc import maxCtxFont
    font, style = ctx.font, ctx.STYLE
    nt, os2, head = font['name'], font['OS/2'], font['head']
    # name
    nt.names = [r for r in nt.names if r.platformID != 1]
    version = ctx.VERSION
    if nt.getDebugName(5) != f'Version {version}' or f'{head.fontRevision:.3f}' != version:
        raise SystemExit(f'meta: version mismatch: name 5 {nt.getDebugName(5)!r}, head {head.fontRevision}')
    for nid, text in ((3, f'{version};{VENDOR};TorchletteSans-{style}'), (9, DESIGNER), (10, DESCRIPTION),
                      (11, REPO), (12, REPO)):
        nt.removeNames(nameID=nid); nt.setName(text, nid, 3, 1, 0x409)
    # OS/2
    italic, bold = 'Italic' in style, style.startswith('Bold')
    sel = os2.fsSelection & ~0b1100001
    sel |= (1 << 0 if italic else 0) | (1 << 5 if bold else 0) | (1 << 6 if not (italic or bold) else 0)
    os2.fsSelection = sel | (1 << 7)                 # USE_TYPO_METRICS stays on
    head.macStyle = (head.macStyle & ~0b11) | (1 if bold else 0) | (2 if italic else 0)
    os2.achVendID = VENDOR
    os2.fsType = 0
    os2.recalcAvgCharWidth(font)
    os2.usMaxContext = maxCtxFont(font)
    os2.recalcUnicodeRanges(font)
    rat, pw = _panose(ctx)
    os2.usWinAscent, os2.usWinDescent = WIN_ASCENT, WIN_DESCENT
    glyf = font['glyf']; ymax = ymin = 0
    for n in font.getGlyphOrder():
        g = glyf[n]
        if g.numberOfContours: g.recalcBounds(glyf); ymax = max(ymax, g.yMax); ymin = min(ymin, g.yMin)
    if ymax > WIN_ASCENT or -ymin > WIN_DESCENT:
        raise SystemExit(f'meta: glyph bounds {ymin}..{ymax} exceed usWin {-WIN_DESCENT}..{WIN_ASCENT}; raise WIN_ASCENT/WIN_DESCENT in modules/meta.py')
    _stat(ctx)
    n_car = _carets(ctx)
    slng = _meta_table(ctx)
    used = _referenced_name_ids(font)
    stale = sorted({r.nameID for r in nt.names if r.nameID >= 256 and r.nameID not in used})
    for nid in stale: nt.removeNames(nameID=nid)
    hinted = _hint(ctx)
    ctx.log(f'fsSelection {os2.fsSelection:#06x}, xAvgCharWidth {os2.xAvgCharWidth}, usMaxContext {os2.usMaxContext}, '
            f'PANOSE weight {pw} (cap/stem {rat:.2f}), win {WIN_ASCENT}/{WIN_DESCENT} (glyphs {ymin}..{ymax}), '
            f'carets for {n_car} ligatures, slng {slng}, dropped names {stale}; {hinted}')

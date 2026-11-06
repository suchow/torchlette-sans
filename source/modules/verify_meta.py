"""Check the meta module: names, OS/2, STAT, .notdef, carets, vertical metrics.

    verify_meta.py FONT.ttf STYLE full|subset

HarfBuzz reads the names, the font extents and the glyphs a run shapes to (the
.notdef for unmapped text, the ligatures that carry carets); fontTools reads the
tables HarfBuzz has no API for (STAT, PANOSE, LigCaretList, FeatureParams). Exits
nonzero on any failure. In the web subset, xAvgCharWidth and usMaxContext are
pyftsubset's (stored unless it is asked to recompute) and are reported only. With
TS_WEB_SUBSET=1 the features web_features.txt leaves out are not checked.
"""
import os, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.otlLib.maxContextCalc import maxCtxFont
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfeatures import SUBSET, WEB_FEATURES, kept   # noqa: E402

path, style, kind = sys.argv[1], sys.argv[2], sys.argv[3]
VENDOR, REPO = 'TRLT', 'https://github.com/suchow/torchlette-sans'
WEIGHT = {'Thin': 100, 'ExtraLight': 200, 'Light': 300, 'Regular': 400, 'Medium': 500,
          'SemiBold': 600, 'Bold': 700, 'ExtraBold': 800, 'Black': 900}
APP_LINE_HEIGHT = 1.5                      # body text in web/src/styles/app.css

font = TTFont(path)
blob = hb.Blob.from_file_path(path); face = hb.Face(blob); hbf = hb.Font(face)
upm = face.upem
fails, checks = [], 0
def check(ok, what):
    global checks
    checks += 1
    if not ok: fails.append(what)

# --- names ----------------------------------------------------------------------
nt = font['name']
check(not [r for r in nt.names if r.platformID == 1], 'Mac name records present')
hbname = lambda i: face.get_name(i)
ribbi = style in ('Regular', 'Bold', 'Italic', 'BoldItalic')
italic = 'Italic' in style
weight = style.replace('Italic', '') or 'Regular'
style_name = style if not italic else 'Italic' if weight == 'Regular' else f'{weight} Italic'   # 'BoldItalic' is named 'Bold Italic'
check(hbname(1) == ('Torchlette Sans' if ribbi else f'Torchlette Sans {weight}'), f'name 1 {hbname(1)!r}')
check(hbname(2) == (style_name if ribbi else 'Italic' if italic else 'Regular'), f'name 2 {hbname(2)!r}')
check(hbname(4) == f'Torchlette Sans {style_name}' and hbname(6) == f'TorchletteSans-{style}', f'names 4/6 {hbname(4)!r} {hbname(6)!r}')
VERSION = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'VERSION')).read().strip()
check('%.3f' % font['head'].fontRevision == VERSION, f'head.fontRevision {font["head"].fontRevision} vs VERSION {VERSION}')
check(hbname(3) == f'{VERSION};{VENDOR};TorchletteSans-{style}', f'name 3 {hbname(3)!r}')
check(hbname(9) == 'The Torchlette Authors; Vernon Adams (Mulish)', f'name 9 {hbname(9)!r}')
check(bool(hbname(10)) and 'Mulish' in hbname(10), f'name 10 {hbname(10)!r}')
check(hbname(11) == REPO and hbname(12) == REPO, f'names 11/12 {hbname(11)!r} {hbname(12)!r}')
check(hbname(13) and 'Open Font License' in hbname(13) and hbname(14), 'license names')
if not ribbi: check(hbname(16) == 'Torchlette Sans' and hbname(17) == style_name, f'names 16/17 {hbname(16)!r} {hbname(17)!r}')
check(hbname(5) == 'Version %.3f' % font['head'].fontRevision, f'name 5 {hbname(5)!r} vs head {font["head"].fontRevision}')

# UI names of every ss and cv feature, read back through HarfBuzz
named, tags = 0, set()
for fr in font['GSUB'].table.FeatureList.FeatureRecord:
    tag = fr.FeatureTag
    if not (tag.startswith('ss') or tag.startswith('cv')) or not tag[2:].isdigit(): continue
    p = fr.Feature.FeatureParams
    nid = getattr(p, 'UINameID', None) if tag.startswith('ss') else getattr(p, 'FeatUILabelNameID', None)
    check(p is not None and nid and hbname(nid), f'{tag}: no UI name')
    named += 1; tags.add(tag)
if SUBSET:
    web = {t for t in WEB_FEATURES if t[:2] in ('ss', 'cv') and t[2:].isdigit()}
    check(tags == web, f'ss/cv feature records {sorted(tags)} != the web list {sorted(web)}')
else:
    check(named >= 38, f'only {named} ss/cv feature records')

# --- OS/2, head, PANOSE -----------------------------------------------------------
os2, head = font['OS/2'], font['head']
italic, bold = 'Italic' in style, style.startswith('Bold')
want_sel = (1 if italic else 0) | (1 << 5 if bold else 0) | (1 << 6 if not (italic or bold) else 0) | (1 << 7)
check(os2.fsSelection & 0b11100001 == want_sel, f'fsSelection {os2.fsSelection:#06x}, want bits {want_sel:#06x}')
check(head.macStyle & 0b11 == (1 if bold else 0) | (2 if italic else 0), f'macStyle {head.macStyle}')
wc = WEIGHT[style.replace('Italic', '') or 'Regular']
check(os2.usWeightClass == wc, f'usWeightClass {os2.usWeightClass}')
hw, hi = hbf.get_style_value(hb.StyleTag.WEIGHT), hbf.get_style_value(hb.StyleTag.ITALIC)   # from STAT
check(hw == wc and hi == (1 if italic else 0), f'HarfBuzz style values wght {hw} ital {hi}')
check(os2.achVendID == VENDOR and os2.fsType == 0, f'achVendID {os2.achVendID!r} fsType {os2.fsType}')
avg = round(sum(w for w, _ in font['hmtx'].metrics.values() if w) / sum(1 for w, _ in font['hmtx'].metrics.values() if w))
ctx = maxCtxFont(font)
if kind == 'full':
    check(os2.xAvgCharWidth == avg, f'xAvgCharWidth {os2.xAvgCharWidth}, average {avg}')
    check(os2.usMaxContext == ctx, f'usMaxContext {os2.usMaxContext}, computed {ctx}')
else:
    print(f'  subset: xAvgCharWidth {os2.xAvgCharWidth} (average {avg}), usMaxContext {os2.usMaxContext} (computed {ctx})')
pan = os2.panose
check((pan.bFamilyType, pan.bSerifStyle) == (2, 11) and 2 <= pan.bWeight <= 11, f'PANOSE {vars(pan)}')

# --- STAT -----------------------------------------------------------------------
st = font['STAT'].table
axes = [a.AxisTag for a in st.DesignAxisRecord.Axis]
check(axes == ['wght', 'ital'], f'STAT axes {axes}')
vals = {}
for v in st.AxisValueArray.AxisValue:
    vals.setdefault(axes[v.AxisIndex], []).append(v)
check(len(vals.get('wght', [])) == 1 and len(vals.get('ital', [])) == 1, 'STAT: one value per axis')
w, i = (vals.get('wght') or [None])[0], (vals.get('ital') or [None])[0]
if w is None or i is None: check(False, 'STAT: missing axis values'); w = i = None
if w is not None:
  check(w.Value == wc and hbname(w.ValueNameID) == (style.replace('Italic', '') or 'Regular'),
        f'STAT wght {w.Value} {hbname(w.ValueNameID)!r}')
  if wc == 400: check(w.Format == 3 and w.Flags & 2 and w.LinkedValue == 700, 'STAT Regular not elidable/linked to 700')
  else: check(not w.Flags & 2, 'STAT non-Regular weight elidable')
if i is None: pass
elif italic: check(i.Value == 1 and hbname(i.ValueNameID) == 'Italic', 'STAT ital')
else: check(i.Value == 0 and i.Flags & 2 and i.Format == 3 and i.LinkedValue == 1 and hbname(i.ValueNameID) == 'Roman', 'STAT ital Roman')
check(hbname(st.ElidedFallbackNameID) in ('Regular', 'Italic'), 'STAT elided fallback name')

# --- .notdef: unmapped text shows a drawn box -----------------------------------
buf = hb.Buffer(); buf.add_str('ก一'); buf.guess_segment_properties(); hb.shape(hbf, buf, {})
check([g.codepoint for g in buf.glyph_infos] == [0, 0], 'unmapped text did not shape to .notdef')
ext = hbf.get_glyph_extents(0)
check(ext.width > 300 and ext.height < -600, f'.notdef extents {ext}')
check(buf.glyph_positions[0].x_advance == 500, '.notdef advance')
g0 = font['glyf']['.notdef']; check(g0.numberOfContours >= 2, '.notdef contours')

# --- ligature carets on the ligatures shaping makes ------------------------------
gdef = font['GDEF'].table
carets = dict(zip(gdef.LigCaretList.Coverage.glyphs, gdef.LigCaretList.LigGlyph)) if gdef.LigCaretList else {}
for text, feats, lig, n in (('office', {}, 'f_f_i', 2), ('staff', {}, 'f_f', 1), ('putt', {}, 't_t', 1),
                            ('fi', {}, 'fi', 1), ('The', {'ss01': True}, 'T_h', 1), ('fb', {'ss16': True}, 'f_b', 1),
                            ('ft', {'cv05': True}, 'f_t', 1)):
    if not kept(*feats): continue
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hbf, buf, feats)
    names = [hbf.get_glyph_name(g.codepoint) for g in buf.glyph_infos]
    if lig not in names:
        check(False, f'{text} {feats}: no {lig} in {names}'); continue
    k = names.index(lig); adv = buf.glyph_positions[k].x_advance
    cs = [c.Coordinate for c in carets[lig].CaretValue] if lig in carets else []
    xs = [0] + cs + [adv]
    check(len(cs) == n and all(a < b for a, b in zip(xs, xs[1:])), f'{lig}: carets {cs} in advance {adv}')
# no carets on glyphs that are not ligatures (a ligature substitution's output counts:
# otfeatures gives carets to ss02's arrows, which ligate from -> and the like)
lig_out = set()
for lk in font['GSUB'].table.LookupList.Lookup:
    for st in lk.SubTable:
        st = st.ExtSubTable if lk.LookupType == 7 else st
        if getattr(st, 'LookupType', lk.LookupType) == 4:
            lig_out.update(l.LigGlyph for ls in st.ligatures.values() for l in ls)
check(not [g for g in carets if '_' not in g and g not in ('fi', 'fl') and g not in lig_out],
      'carets on non-ligatures')

# --- vertical metrics ------------------------------------------------------------
fe = hbf.get_font_extents('ltr')
hhea = font['hhea']
check(os2.fsSelection & (1 << 7), 'USE_TYPO_METRICS off')
check((os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) == (hhea.ascent, hhea.descent, hhea.lineGap)
      == (fe.ascender, fe.descender, fe.line_gap), f'typo/hhea/HarfBuzz extents differ {fe}')
top = bot = 0; who = ('', '')
for gid in range(face.glyph_count):
    e = hbf.get_glyph_extents(gid)
    if e is None or e.height == 0: continue
    if e.y_bearing > top: top, who = e.y_bearing, (hbf.get_glyph_name(gid), who[1])
    if e.y_bearing + e.height < bot: bot, who = e.y_bearing + e.height, (who[0], hbf.get_glyph_name(gid))
check(top <= os2.usWinAscent and -bot <= os2.usWinDescent, f'ink {bot}..{top} ({who}) outside win {os2.usWinAscent}/{os2.usWinDescent}')
half = (APP_LINE_HEIGHT * upm - (fe.ascender - fe.descender)) / 2   # half-leading of the app's line box
# MATH-table size variants and assembly parts (unencoded *.math_table / *.mathglyphs glyphs)
# only appear in stretched display math, which sets its own line box; the win metrics check
# above covers them. Every other glyph must fit the app's text line box.
ltop = lbot = 0
for gid in range(face.glyph_count):
    e = hbf.get_glyph_extents(gid)
    if e is None or e.height == 0: continue
    name = hbf.get_glyph_name(gid)
    # ⏜–⏡ (U+23DC–U+23E1) are over/under braces, brackets and parens that only occur
    # stacked above or below a formula in math; TeX-depth braces reach below the text box.
    if name.endswith(('.math_table', '.mathglyphs')) or name in ('uni23DC', 'uni23DD', 'uni23DE', 'uni23DF', 'uni23E0', 'uni23E1'): continue
    ltop = max(ltop, e.y_bearing); lbot = min(lbot, e.y_bearing + e.height)
check(ltop <= fe.ascender + half and lbot >= fe.descender - half, f'ink {lbot}..{ltop} outside the app line box')
gasp = font['gasp'].gaspRange if 'gasp' in font else {}
check(gasp.get(0xFFFF) == 0x0F, f'gasp {gasp}')
# hinting (ttfautohint, when the build had it): integer ppem, programs, and FreeType-free
# sanity through HarfBuzz: hinting must not change advances (hmtx is what shaping reads)
hinted = 'fpgm' in font
if hinted:
    check(head.flags & (1 << 3), 'hinted font without head flags bit 3 (integer ppem)')
    check('cvt ' in font and 'prep' in font, 'hinted font without cvt/prep')
    progs = sum(1 for n in font.getGlyphOrder() if getattr(font['glyf'][n], 'program', None) is not None
                and font['glyf'][n].program.getBytecode())
    check(progs > 500, f'only {progs} glyph programs')
print(f"  {'hinted' if hinted else 'unhinted'}")

# --- meta -----------------------------------------------------------------------
if kind == 'subset':
    print(f"  subset: meta table {'kept' if 'meta' in font else 'dropped by pyftsubset (no subset method)'}")
elif 'meta' in font:
    check(font['meta'].data.get('dlng') == 'Latn' and 'Latn' in font['meta'].data.get('slng', ''), f"meta {font['meta'].data}")
else:
    check(False, 'no meta table')

print(f'meta {style} {kind}: {checks - len(fails)}/{checks} checks; ink {bot}..{top}, win {os2.usWinAscent}/{os2.usWinDescent}, '
      f'line box {fe.descender - half:.0f}..{fe.ascender + half:.0f}; {named} named ss/cv features; {len(carets)} caret glyphs')
for f_ in fails: print('  FAIL', f_)
sys.exit(1 if fails else 0)

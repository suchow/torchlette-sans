"""Build the Torchlette Sans specimen page at /sans (web/public/sans/index.html + sans.css).

Run from source/: python3 specimen/build_sans.py <out-dir> [--version 0.5.13]
The output directory can also be supplied through SANS_OUT.

The inputs are specimen-v03.html, specimen.css, specimen-v03.css, and
hand-authored pieces in sans-src/, resolved relative to this script.
specimen-v03.html is a frozen generated snapshot used as input. Preserve its
line layout: the builder selects sections by line number. The script retains
the literary book and selected v0.3 reference pages. It omits explanatory decks,
contents, glyph-outline atlases, and the feature catalogue. It makes these web
adaptations:

  * sections are reordered (SECTION_ORDER): notation and machine-learning
    material first, then the book's typographic pages, then languages and
    ornaments;
  * "Mathematics in use" is replaced by a grid of ML formulas
    (sans-src/ml-formulas.html, hand-written MathML);
  * v0.3 feature rows show only the "on" form of each feature, and the
    Capitals kerning pair shows only the kerned line;
  * a fixed Download corner (version, font zip with the specimen PDF) sits top right,
    with a glow that appears once the page scrolls;
  * the page uses espresso ink, accent-yellow overscroll and a bottom line,
    the "Made with love on the Hudson" credit, and an ExtraBold cover title;
  * pt sizes become fluid CSS lengths; phone layouts use separate rules.

The default version comes from source/VERSION using the Makefile release-tag
convention. --version accepts an explicit release version for reproducing earlier
output. The version controls the label, release links, and font cache queries.
Copy the matching woff2 files into the output directory's fonts/ separately.
This script writes only index.html and sans.css and uses the Python standard library.
"""
import argparse
import os
import re
from pathlib import Path

# ---- source paths and release metadata --------------------------------------
SRC = Path(__file__).resolve().parent
HAND = SRC / 'sans-src'

parser = argparse.ArgumentParser(description='Build the Torchlette Sans web specimen HTML and CSS.')
parser.add_argument('out_dir', nargs='?', default=os.environ.get('SANS_OUT'),
                    help='existing output directory (or set SANS_OUT)')
parser.add_argument('--version', metavar='X.Y.Z',
                    help='release version override; defaults to source/VERSION')
args = parser.parse_args()
if not args.out_dir:
    parser.error('supply an output directory or set SANS_OUT')
OUT = Path(args.out_dir)
if not OUT.is_dir():
    parser.error(f'output directory does not exist: {OUT}')

if args.version is not None:
    if not re.fullmatch(r'[0-9]+\.[0-9]\.[0-9]+', args.version):
        parser.error('--version must have the form X.Y.Z with a single-digit minor version')
    FONT_VERSION = args.version
else:
    version_path = SRC.parent / 'VERSION'
    try:
        metadata = version_path.read_text().strip()
    except OSError as exc:
        parser.error(f'cannot read release metadata at {version_path}: {exc}')
    # Match source/Makefile RELEASE_TAG: 0.514 -> 0.5.14; 0.504 -> 0.5.4.
    match = re.fullmatch(r'([0-9]+)\.([0-9])0?([0-9]+)', metadata)
    if not match:
        parser.error(f'malformed release metadata in {version_path}: {metadata!r}')
    FONT_VERSION = '.'.join(match.groups())

CACHE_BUST = FONT_VERSION
RELEASE_URL = f'https://github.com/suchow/torchlette-sans/releases/download/v{FONT_VERSION}'
ZIP_URL = f'{RELEASE_URL}/TorchletteSans-v{FONT_VERSION}.zip'
PRELOAD_FACES = ['Regular', 'ExtraBold', 'Black']   # body text, title, cover Aa


def font_url(name):
    return f'fonts/TorchletteSans-{name}.woff2?v={CACHE_BUST}'


def replace_once(s, old, new):
    """str.replace that fails loudly if the source text has drifted."""
    assert s.count(old) == 1, f'expected exactly one match for {old[:60]!r}'
    return s.replace(old, new)


lines = (SRC / 'specimen-v03.html').read_text().split('\n')

def L(a, b=None):
    return '\n'.join(lines[a - 1:(b or a)])

# ---- pick sections -------------------------------------------------------
literary = L(12, 508)
# contents page and cover meta
literary = re.sub(r'<section class="page v03 contents-page".*?</section>\n', '', literary)
literary = re.sub(r'\s*<div class="cover-top lab">.*?</div>', '', literary)
literary = re.sub(r'\s*<ul class="cover-list lab">.*?</ul>', '', literary, flags=re.S)

V03_KEEP = [510, 511, 512, (513, 518), 524, 525, 526, 527, 528, 529, 530, 531, 532,
            536, 537, 538, 'ORN', 539, 540, 541, 546, 547]

def orn_plates():
    cps = []
    for n in range(519, 523):
        cps += re.findall(r'aria-label="uni([0-9A-F]{4,5})"', lines[n - 1])
    cells = ''.join(f'<span>&#x{c};</span>' for c in cps)
    return f'<section class="page v03" data-head="Ornaments"><div class="orn-plate">{cells}</div></section>'

parts = [literary]
for k in V03_KEEP:
    if k == 'ORN':
        parts.append(orn_plates())
    elif isinstance(k, tuple):
        parts.append(L(*k))
    else:
        parts.append(L(k))
body = '\n'.join(parts)

# ---- strip meta text -----------------------------------------------------
body = re.sub(r'<h2 class="chapter-title">.*?</h2>', '', body)
body = re.sub(r'<p class="deck">.*?</p>', '', body)
body = re.sub(r' data-(src|expect|title-src|v03-title)="[^"]*"', '', body)
body = re.sub(r'<!--.*?-->\n?', '', body)
body = re.sub(r'<div class="feature-row"><h3>(Negative guards|Literal guards)</h3>.*?</div></div></div></div>', '', body)
# feature-row headings become small labels
body = body.replace('<h3>', '<div class="lab fr-h">').replace('</h3>', '</div>')
# running heads -> visible small label at the top of each section
def head(m):
    cls, h = m.group(1), m.group(2)
    h = re.sub(r' / \d+$', '', h)
    lab = f'<div class="rh lab">{h}</div>' if h else ''
    return f'<section class="{cls}">{lab}'
body = re.sub(r'<section class="([^"]*)" data-head="([^"]*)">', head, body)
# the descriptive cover feature list etc. gone; the 'Proportions' metric svg: drop fixed size
body = body.replace('width="482pt" height="122pt"', '')

# ---- show only the "on" form ------------------------------------------------
# v0.3 feature rows pair an Off sample with an On sample; keep just the On one.
SAMPLE = r'<div class="spec-sample [^>]*>.*?</div>'
body = re.sub(rf'<div class="feature-pair"><div><div class="lab">Off</div>{SAMPLE}</div>'
              rf'<div><div class="lab">On</div>({SAMPLE})</div></div>',
              r'<div class="feature-pair one"><div>\1</div></div>', body)
# Capitals: the kerned line only
body = replace_once(body,
    '      <div><p class="cd nss nokern">PATAV., GEORG. FLOREN,</p><div class="lab">Kerning off</div></div>\n'
    '      <div><p class="cd nss">PATAV., GEORG. FLOREN,</p><div class="lab">Kerning on</div></div>',
    '      <div><p class="cd nss">PATAV., GEORG. FLOREN,</p><div class="lab">Kerning</div></div>')

# ---- unit conversion -----------------------------------------------------
def pt(m):
    v = float(m.group(1))
    a = abs(v)
    var = '--tpt' if a < 16 else ('--mpt' if a < 30 else '--dpt')
    return f'calc({m.group(1)} * var({var}))'

def conv_units(s):
    s = re.sub(r'(-?\d*\.?\d+)pt\b', pt, s)
    s = re.sub(r'(-?\d*\.?\d+)in\b', lambda m: f'{round(float(m.group(1)) * 96, 1)}px', s)
    return s

body = re.sub(r'style="([^"]*)"', lambda m: 'style="' + (m.group(1) if m.group(1).startswith('--s:') else conv_units(m.group(1))) + '"', body)

# wrap the wide Lovelace table so it can scroll on phones instead of the page
body = body.replace('<table class="ops">', '<div class="ops-scroll"><table class="ops">').replace(
    '</tbody>\n    </table>\n    <div class="lab">Inferior figures', '</tbody>\n    </table></div>\n    <div class="lab">Inferior figures')

# ---- sections: replace and reorder ---------------------------------------
sections = re.split(r'\n(?=<section )', body)

def heading(sec):
    m = re.match(r'<section class="[^"]*">(?:<div class="rh lab">([^<]*)</div>)?', sec)
    return m.group(1) or ''

# "Mathematics in use": hand-written ML formulas instead of the v0.3 samples
ML_HEAD = '<section class="page v03"><div class="rh lab">Mathematics in use</div>'
ml_grid = (HAND / 'ml-formulas.html').read_text().rstrip('\n')
sections = [ML_HEAD + ml_grid + '</section>\n' if heading(s) == 'Mathematics in use' else s
            for s in sections]

# Running heads in page order ('' = the untitled cover and epigraph pages,
# which keep their place). A head that names several sections keeps their order.
SECTION_ORDER = [
    '',
    'Distinctive forms',
    # notation and machine learning
    'Mathematics in use', 'Notation in ordinary text', 'Code, units and transforms',
    'Readable code alternatives', 'Nodes in a model', 'Notation for reasoning',
    'Contextual symbols', 'Letter joins and wordmarks', 'Mathematical alphabets',
    'Script, Fraktur and double-struck', 'Greek', 'Vertical mathematics', 'Mathematics',
    'Inferiors &amp; superiors', 'All the playing pieces',
    # ligatures and the book's typographic pages
    'Ligatures', 'Prose ligatures · ss16', 'Stylistic sets', 'Character set', 'Weights',
    'Italics', 'Roman &amp; italic', 'Display', 'Sizes', 'Text · 10 pt', 'Text · 12 pt',
    'Small capitals', 'Capitals', 'Figures', 'Tabular figures', 'Fractions',
    'Fractions and scripts', 'Signs', 'Signs, arrows and actions',
    # languages and ornaments
    'Cyrillic', 'Accents and language', 'Localized typography', 'Ornaments',
    'Ornament selections', 'Ornaments in composition', 'Small details, full vocabulary',
    'Choosing an alternate',
]
assert sorted(set(map(heading, sections))) == sorted(SECTION_ORDER), \
    set(map(heading, sections)) ^ set(SECTION_ORDER)
sections = [s for h in SECTION_ORDER for s in sections if heading(s) == h]
body = '\n'.join(sections)

# ---- CSS -----------------------------------------------------------------
css_src = (SRC / 'specimen.css').read_text() + '\n' + (SRC / 'specimen-v03.css').read_text()
css_src = re.sub(r'@page[^}]*}', '', css_src)
css_src = conv_units(css_src)

# site colours: accent-yellow overscroll and closing line
css_src = replace_once(css_src,
    'html, body { margin: 0; padding: 0; background: #fff; color: var(--ink); }\n',
    'html, body { margin: 0; padding: 0; background: #fff; color: var(--ink); }\n'
    '/* As on torchlette.com: the html background paints the overscroll region in the\n'
    ' * accent yellow, and a 2px accent line closes the page. */\n'
    'html { background: #eb6; }\n'
    'body { border-bottom: 2px solid #eb6; }\n')
# title at ExtraBold, as on the modules list
css_src = replace_once(css_src, '.cover-name { font-weight: 900;', '.cover-name { font-weight: 800;')
# the Download button (placed in .dl-corner below); inverts on hover
css_src = replace_once(css_src, '.cover-aa.it { bottom: 177.6px; }\n',
    '.cover-aa.it { bottom: 177.6px; }\n'
    '.cover-download { position: absolute; left: 86.4px; bottom: 96px; font-weight: 600; font-size: 20px; color: #fff; background: var(--ink); border: 1.5px solid var(--ink); padding: 10px 26px; border-radius: 999px; text-decoration: none; transition: background 120ms, color 120ms; }\n'
    '.cover-download:hover, .cover-download:focus-visible { background: #fff; color: var(--ink); }\n')

FACES = [(300, 'Light'), (400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'),
         (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')]
faces = []
for w, n in FACES:
    faces.append(f'@font-face{{font-family:"Torchlette Sans";font-weight:{w};font-style:normal;font-display:swap;src:url("{font_url(n)}") format("woff2");}}')
    itn = 'Italic' if n == 'Regular' else n + 'Italic'
    faces.append(f'@font-face{{font-family:"Torchlette Sans";font-weight:{w};font-style:italic;font-display:swap;src:url("{font_url(itn)}") format("woff2");}}')

WEB = r'''
/* ---- web adaptation ---------------------------------------------------- */
:root {
  --ink: #33241b; --ink2: #8a7f78; --rule: #dcdad8;
  --tpt: 1.3333px;                                   /* text sizes */
  --mpt: clamp(1.02px, calc(100vw / 380), 1.45px); /* 16-29 pt   */
  --dpt: clamp(0.62px, calc(100vw / 640), 1.5px);  /* display    */
}
html { -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }
body { background: #fff; overflow-x: hidden; }
main { max-width: 1000px; margin: 0 auto; padding: 0 max(clamp(16px, 5vw, 56px), env(safe-area-inset-right)) 0 max(clamp(16px, 5vw, 56px), env(safe-area-inset-left)); }
.page { width: auto; height: auto; overflow: visible; position: static; padding: clamp(64px, 11vw, 140px) 0 0; break-after: auto; }
.page:last-child { padding-bottom: clamp(72px, 12vw, 160px); }
.rh { position: static; display: block; margin-bottom: clamp(20px, 3vw, 34px); padding-bottom: 8px; border-bottom: 0.6px solid var(--rule); }
.cover { padding-top: clamp(48px, 9vw, 120px); }
.cover-name { margin: 0 0 clamp(36px, 7vw, 90px); }
.cover-aa, .cover-aa.it { position: static; margin: 0 0 18px; flex-wrap: wrap; gap: 0 4px; }
.cover-download { position: static; display: inline-block; margin-top: 12px; }
.epigraph { position: static; padding: clamp(24px, 6vw, 80px) 0 0; max-width: 34em; }
.epi-text { max-width: 15em; }
svg.metrics { width: 100%; height: auto; overflow: visible; }
.lab { font-size: 12px; }
.orn { color: var(--ink2); }
.ornament-glyph { font-size: calc(34 * var(--dpt) + 10px); }
.orn-plate { display: flex; flex-wrap: wrap; gap: 22px 0; font-size: calc(44 * var(--dpt) + 8px); line-height: 1.2; text-align: center; }
.orn-plate span { min-width: calc(76 * var(--dpt) + 20px); flex: 0 0 auto; padding: 0 6px; }
.ornament-selections { display: flex; flex-wrap: wrap; gap: 28px 0; }
.ornament-selection { min-width: calc(80 * var(--dpt) + 30px); padding: 0 8px; }
.spec-sample { hyphens: none; -webkit-hyphens: none; }
.feature-row .fr-h { font-size: 11px; margin-bottom: 6px; }
.feature-pair .lab { font-size: 10px; }
.charset dd, .gr-inv dd, .spec-sample, .glyphs, .keys, .cd, .set p, .gr-table, .scw-grid p, .joins { overflow-wrap: anywhere; }
.set p, .cd, .scw-grid p { white-space: normal; }
.native-grid math, .math-specimens math { font-size: calc(27 * var(--dpt) + 6px); }
math { overflow: visible; max-width: 100%; padding-block: 0.35em; }
/* Mathematics in use: a grid of machine-learning formulas */
.ml-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: calc(30 * var(--dpt) + 8px) calc(40 * var(--mpt)); }
.ml-eq { margin: 0; min-width: 0; border-top: 0.6px solid var(--rule); padding-top: 10px; }
.ml-eq .lab { display: block; margin-bottom: calc(10 * var(--dpt) + 6px); }
.ml-eq math { font-family: "Torchlette Sans", math; font-size: calc(10 * var(--dpt) + 11px); }
.ml-eq.wide { grid-column: 1 / -1; }
.ml-eq math { font-variant-numeric: lining-nums proportional-nums; }
.ml-eq mtd { padding: 0.12em 0; math-style: normal; }
.ml-eq mtd:first-child { text-align: right; }
.ml-eq mtd:last-child { text-align: left; }
@media (min-width: 1000px) { .ml-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 379px) { .ml-eq math { font-size: 15px; } }
@media (max-width: 339px) { .ml-eq math { font-size: 13.5px; } }
table.ops-wrap, .ops-scroll { overflow-x: auto; }
.wf { grid-template-columns: 64px 1fr; }

@media (max-width: 720px) {
  .dist-grid, .figs, .ligs, .lig.two, .boole-two, .tbl-two, .scw-grid, .feature-pair,
  .figs-more, .intro-grid { grid-template-columns: minmax(0, 1fr); }
  .dist-grid .span2, .lig.two { grid-column: auto; }
  .pair { grid-template-columns: minmax(0, 1fr); gap: 8px 0; }
  .s16-row, .charset, .gr-inv { grid-template-columns: minmax(0, 1fr); }
  .s16-row p { grid-column: 1; }
  .charset dt, .gr-inv dt { padding-top: 12px; }
  .cols2 { column-count: 1; }
  .set { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 4px 16px; }
  .set > .lab:first-child { grid-column: span 2; }
  .set.set-h > div:first-child { display: none; }
  .notation { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
  .notation .nt-head { grid-column: span 2; }
  .native-grid { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
  .book-head { grid-template-columns: 72px minmax(0, 1fr); }
  .joins { flex-wrap: wrap; gap: 4px 18px; justify-content: flex-start; }
  .marbles { font-size: calc(38 * var(--mpt)); }
  .eqn { position: static; display: block; text-align: right; }
  .ronde li { grid-template-columns: 18px minmax(0, 1fr) 64px; }
  .gr-table td { padding: 0 8px; }
  .alternate-row { flex-wrap: wrap; }
  .tp5 { font-size: 9px; }
  .tp5 br { display: none; }
  .wf { grid-template-columns: minmax(0, 1fr); gap: 4px 0; }
  .wf p { font-size: min(var(--s), 11.5vw); max-height: calc(min(var(--s), 11.5vw) * 1.3 * var(--n)); }
  table.ops { font-size: 13px; }
  table.num.big { font-size: calc(25 * var(--mpt)); }
  table.num.big th, table.num.big td { padding-right: 8px; }
  table.num th { font-size: 10px; }
  .love .eq { white-space: normal; font-size: 22px; }
}

.credit { text-align: center; font-size: 17px; padding: 0 16px 56px; color: var(--ink); }
.credit img { display: inline-block; vertical-align: -3px; }
.feature-pair.one { grid-template-columns: 1fr; }

/* Download, fixed top right; version and button share one baseline */
.dl-corner { position: fixed; top: calc(20px + env(safe-area-inset-top)); right: calc(24px + env(safe-area-inset-right)); z-index: 10; display: flex; align-items: baseline; gap: 12px; padding: 4px 4px 4px 12px; line-height: 1; isolation: isolate; }
/* a soft white oval behind the corner that fades out in every direction;
   a gradient, not a blur filter, so Safari has nothing to clip */
.dl-corner::before { content: ""; position: absolute; inset: -18px -24px -18px -48px; z-index: -1; background: radial-gradient(closest-side, #fff 62%, rgba(255,255,255,0.85) 75%, rgba(255,255,255,0) 100%); }
.dl-corner .ver { --ss: "ss01" 1, "ss02" 1; /* ss16 would set v0.5.1 as a filled badge */ font-weight: 500; font-size: 15px; line-height: 1; color: var(--ink2); font-variant-numeric: oldstyle-nums proportional-nums; }
.dl-corner .cover-download { position: static; display: inline-block; font-size: 15px; line-height: 1; padding: 8px 18px; margin: 0; }
@media (max-width: 720px) {
  .dl-corner { top: calc(12px + env(safe-area-inset-top)); right: calc(12px + env(safe-area-inset-right)); gap: 8px; }
  .dl-corner .ver, .dl-corner .cover-download { font-size: 14px; }
  .dl-corner .cover-download { padding: 7px 14px; }
  .cover { padding-top: calc(76px + env(safe-area-inset-top)); }
}
.ml-eq { --ss: "ss01" 1, "ss02" 1, "ss16" 0; --fx: "kern" 1, "calt" 0; } /* calt slashes a lone 0, which reads as the empty set in math */
.ml-eq math { overflow: visible; padding-block: 0.35em; }
.dl-corner::before { opacity: 0; transition: opacity 150ms; }
.dl-corner.dl-glow::before { opacity: 1; }
'''

css = '/* Torchlette Sans specimen: web edition of the v0.3 specimen book. */\n' + '\n'.join(faces) + '\n' + css_src + WEB
(OUT / 'sans.css').write_text(css)

# ---- HTML ------------------------------------------------------------------
preloads = '\n'.join(f'<link rel="preload" href="{font_url(n)}" as="font" type="font/woff2" crossorigin>'
                     for n in PRELOAD_FACES)
dl_corner = (f'<div class="dl-corner"><span class="ver">v{FONT_VERSION}</span>'
             f'<a class="cover-download" href="{ZIP_URL}" download>Download</a></div>')

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="format-detection" content="telephone=no">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Torchlette Sans</title>
{preloads}
<link rel="stylesheet" href="sans.css">
</head>
<body>
{dl_corner}
<main>
{body}
</main>
<footer class="credit">Made with <img src="/heart.png" alt="love" width="16" height="16"> on the Hudson</footer>
<script>
// The glow behind the Download corner is only needed once text scrolls under
// it; hiding it at the top keeps the overscroll colour clear of it.
(function () {{
  var c = document.querySelector('.dl-corner');
  if (!c) return;
  function update() {{ c.classList.toggle('dl-glow', window.scrollY > 4); }}
  window.addEventListener('scroll', update, {{ passive: true }});
  update();
}})();
</script>
</body>
</html>
'''
(OUT / 'index.html').write_text(page)
print(len(page), len(css))

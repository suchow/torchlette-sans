# Torchlette Sans

Torchlette Sans is the text face of the torchlette web app. It is a modified
version of [Mulish](https://github.com/googlefonts/mulish) and, like Mulish, is
licensed under the SIL Open Font License 1.1 (`OFL.txt`). Mulish's own license
is in `mulish/OFL.txt`; it declares no Reserved Font Name.

The font starts from Mulish and changes it: round dots, wider round letters, an e
whose crossbar is at least 0.68 of the stem at every weight, a lower x-height
with longer ascenders and descenders, redrawn old-style figures,
true small capitals, and ligatures and stylistic sets, among them ss16, the
Torchlette prose ligatures (54 kept from the two ligature labs, each up to lab id
99 also on its own as cvNN; the spark line is ss15). `build.py` lists every
feature at the top. Every weight has an italic, built the same way from Mulish
Italic (see "Italics" below).

The modules in `modules/` add to that (each plugs into the build, and its
docstring lists what it changes):

- `kern`: kerning for the glyphs Mulish's and `build.py`'s kerning leave out (the
  figure forms, the ligatures, the arrows and relations, the superiors and
  inferiors), and the small-cap pairs an earlier subtable hides.
- `kern_apos`: tightens apostrophe pairs (’s, n’t, ’ll, …) for ’ ' ʼ against every letter to 0.90 of the n–n gap, capped; gives ʼ the spacing of ’.
- `greek`: the Greek alphabet (U+0370-03FF), with small capitals and kerning. The
  letters are Commissioner's Greek, fitted to Torchlette's metrics and stems (see
  "Greek sources" below); the capitals that share a Latin shape are Torchlette's Latin
  capitals. It is part of the default build.
- `lnum`: the lnum feature, which maps every old-style figure back to the lining
  figure of the same spacing after onum, tnum and pnum have run, so
  `font-variant-numeric: lining-nums` overrides `oldstyle-nums` and keeps the spacing
  that `tabular-nums` or `proportional-nums` chose.
- `supsub`: superscript and subscript letters and signs, encoded (the modifier
  letters, U+1D2C-1DBF, U+2C7C-2C7D) and through sups, subs and sinf.
- `symbols`: arrows, the mathematical operators prose and lessons use (among them
  floor and ceiling brackets from U+2300-23FF), the double-struck capitals ℝ ℕ ℤ ℚ ℂ
  (the capitals drawn in the operators' thin strokes with their weight-bearing strokes
  doubled, as Noto Sans Math and DejaVu Sans draw them; `modules/symbols.py`,
  `doublestruck`), and the Unicode spaces and joiners.
- `otfeatures`: case forms of the punctuation (case), capital spacing (cpsp), a
  slashed zero (zero), mark attachment on `build.py`'s glyphs and on the letters
  Mulish left without anchors (ŋ, ə, ɓ, ɗ, g, and others, and the ogonek on
  consonants), GDEF classes and ligature carets, and aalt and salt; dlig (the Th and th
  ligatures of ss01 and ss03); mgrk (Σ Π Δ to the symbols ∑ ∏ ∆); nalt (the whole
  numbers 1 to 20 to the circled numbers ① to ⑳); a grek script record with DFLT's
  features; and fixes to Mulish's own layout: a GDEF class for every glyph, frac only around a
  slash between digits, and locl for Romanian and the Turkic languages Mulish left out.
  By default, calt also slashes a zero that is the only digit of its number: the
  zeros in `0`, `x[0]`, and `(0)` are slashed, and those in `10` and `0.05` are plain.

  Of the other registered features, these are not in the font: clig (there are no
  contextual ligatures beyond those of liga, calt and ss16), pcap and c2pc (petite
  capitals would be a new alphabet drawn at the x-height, with its accented forms,
  Cyrillic, marks and kerning), unic (it needs those x-height capitals too), and titl
  (no titling forms are drawn).
- `sigmoid`: the first i of "sigmoid" drawn as a small sigmoid curve, in ss16.
- `vector`: ten more forms of ss16's "vector"/"vectors" word mark, in each of which a stroke
  of the word grows into the arrow (Jordan's picks from the vector-ligature lab: v01 v02 v06
  v13 v15 v16 v18 v20 v23 v25). The `rand` feature, which browsers that shape with HarfBuzz
  apply by default, picks the default mark or one of the ten for each occurrence;
  `"rand" N` selects form N. Safari ignores rand and shows the default.
- `mathletters`: the letters and operators of ML notation beside the double-struck capitals: ℙ ℍ 𝔼 𝟙 in
  `symbols`' thin doubled strokes, the complete script alphabet from Noto Sans Math Regular, ℏ, ∥ ∖ ⟂ ⟦ ⟧ ⋆, and the format-12
  cmap that 𝔼 and 𝟙 (outside the BMP) need.
- `latin_gaps`: the Dutch ij, every Pinyin vowel with its tone, the long s ſ (small
  capitals give S), the Latin case partners Mulish left out (Ǥ Ǩ Ȟ ȩ Ƒ), the vulgar
  fractions ⅐ to ⅞ and ↉, and stacked fractions (afrc).
- `african`: the letters of African orthographies that Mulish lacks, 19 case pairs:
  Ɔ ɔ, Ɛ ɛ, Ǝ ǝ, Ɣ ɣ, Ɩ ɩ, Ʊ ʊ, Ʋ ʋ, Ʒ ʒ, Ƙ ƙ, Ƥ ƥ, Ƭ ƭ, Ɲ ɲ, Ɖ ɖ, Ƀ ƀ, Ɨ ɨ, Ʉ ʉ, Ƿ ƿ,
  Ʇ ʇ and Ꞌ ꞌ, with small capitals (smcp, c2sc), kerning (each side as the letter it is
  made from) and accents above and below (the anchors are `otfeatures`'). Ɣ ɣ Ʋ ʋ are Noto
  Sans's, fitted to each weight (see "Greek sources"); the others are drawn at each weight
  from Mulish's own letters, hooks, tails and bars.
- `logic`: the turnstiles ⊢ ⊣ ⊧ ⊨ ⊬ ⊭, the modal operators ◇ ◻ and the black diamond ◆,
  the marks ∎ ☡ ↯ ⁎ ‣ ⌑, the APL glyphs ⍳ ⍴ ⍉ ⌽, and the white trapezium ⏢; ss09, and
  calt beside logic, turn □ into the modal box.
- `currency`: the bitcoin, new shekel, lari, and rupee signs ₿ ₪ ₾ ₨, drawn at each weight
  from B, H, O, R, and s with the strokes and bars of $ and €. ₿ is on the figure width, as
  Mulish's currency signs are; ₪ ₾ ₨ have their own widths.
- `punctuation`: the two- and three-em dashes ⸺ ⸻, the swung dash ⁓, the reversed
  quotation marks ‛ ‟, the per ten thousand sign ‱, the interrobang ‽, the hyphenation
  point ‧, ‼ ⁇, the reversed question mark ⸮, the two asterisks ⁑, and ℃ ℉ ℗, with small
  capitals and case forms where the marks they are made from have them.
- `ui`: the interface symbols ✓ ✗ ■ □ ▶ ● ○ ★, the triangles ▲ △ ▼ ▽ ◀ ◁ ▷ and their small
  forms ▴ ▵ ▾ ▿ ◂ ◃ ▹, the shapes ☆ ▪ ▫ ◦ ◯, the dotted circle ◌ (it takes combining marks),
  the circled numbers ①–⑳ with Torchlette's small-cap figures, and the keyboard symbols
  ⌘ ⌥ ⇧ ⏎ ⌫.
- `tensordiagram`: Penrose tensor-diagram glyphs (U+EE00-EE07) that join up under calt,
  and ss20 ("Tensor diagrams"), which turns an ASCII diagram in square brackets
  (`[-*-]`, `[(-*-*-)]`) into them. ss20 has its own lookups for the brackets and shares
  calt's joining lookups, so it works whether calt is on (the default) or off.
- `meta`: the name table, OS/2 and STAT metadata, a drawn .notdef, feature names,
  ligature carets, and, when `ttfautohint-py` is installed (the Makefile pins it),
  ttfautohint hinting of the .ttf.

There are seven weights, each built from its own static instance of Mulish, and each
with an italic built from the same instance of Mulish Italic:

| Style     | usWeightClass | Mulish wght | lowercase stem | stem / Regular's |
|-----------|---------------|-------------|----------------|------------------|
| Light     | 300           | 242         | 50             | 0.76             |
| Regular   | 400           | 324         | 66             | 1.00             |
| Medium    | 500           | 388         | 79             | 1.20             |
| SemiBold  | 600           | 510         | 92             | 1.39             |
| Bold      | 700           | 675         | 119            | 1.80             |
| ExtraBold | 800           | 762         | 141            | 2.14             |
| Black     | 900           | 845         | 163            | 2.47             |

The stem ratios follow the median of text families' SemiBold and Bold
(Open Sans 1.41 / 1.83, Source Code Pro 1.41 / 1.79, Gill Sans 1.35 / 1.98,
Helvetica Neue Bold 1.67; Avenir's Heavy, often used as its bold, is 1.82 times
Avenir Book's 66-unit stem). Every stroke `build.py` draws (dots, crossbars, the
figures, the ligature joins, the alternates) is scaled from the source
instance's own measured stems, and the small capitals come from a heavier
instance whose stem, scaled down, matches the lowercase's (wght 342, 498, 631,
704, 842 and 946 from Light to ExtraBold). Black's come from wght 1000, Mulish's
heaviest, so they are a little lighter than its lowercase (cap stem 148 against 163).
Light, Medium, ExtraBold and Black continue the progression of the other three.

## Italics

Mulish Italic is Mulish leaning 9 degrees (0.1587 of x per unit of height), with a
few letters (c, e, s, the round capitals), the figures and the marks corrected by
hand, and its operators, crossbar ends and dots leaning with the letters. An italic
style (`Italic`, `LightItalic` ... `BlackItalic`) starts from the static instance of
`mulish/Mulish-Italic[wght].ttf` at its weight's wght. `build.py` unslants that
instance about y = 252 (where Mulish Italic's stems then stand exactly on the
upright's), runs every step above on it as on an upright, and reslants the result
before the modules' post phase. A horizontal shear keeps every height and every
horizontal span, so the stem and crossbar measurements, the vertical remap, the
small-cap and superior instances, the kerning and the ligature joins are the same code
with the same numbers; the drawn figures, crossbars, arrows and joins come out leaning
with the letters, as Mulish Italic's own figures and operators do, on Mulish Italic's
own letterforms and kerning. Only the round dots are drawn as circles in the slanted
frame, as Mulish Italic keeps its bullet and degree sign round. Mulish Italic's slant,
caret slope and italic angle are kept; the names, OS/2 and head style bits and the STAT
`ital` axis value (1, Italic, with the upright's Roman value linked to it) follow the
`meta` module's conventions. Regular, Italic, Bold and Bold Italic are the style-linked
family "Torchlette Sans"; each other weight is a legacy family of its own with a
Regular and an Italic.

## Box drawing

The `boxdrawing` module adds 19 light, rounded, heavy, and double line characters.
Each has a 600-unit advance in all fourteen styles. The cell spans x = 0..600
and y = -250..750, with its junction at (300, 250). Light strokes use the style's
minus thickness (`BAR`); heavy strokes use twice that thickness. Double lines
have two `BAR` strokes separated by a `BAR` white gap. Rounded corners have a
150-unit centreline radius. The drawings remain upright in italic styles.
The existing 130-unit spark-line blocks are unchanged.

Adjacent drawing cells require a 600-unit horizontal pitch, zero letter spacing,
and no justification or inserted spacing. Vertical joins require a 1000-unit
baseline pitch: use `line-height: 1` with this 1000-UPM font. The current font
metrics span 1255 units. A 1255-unit baseline pitch leaves 255-unit gaps between
vertical strokes.
Other line heights and terminal-imposed cell dimensions may also leave gaps or
overlaps. Use a dedicated drawing container with explicit spacing.

## Greek sources

The `greek` module imports its letters from two other OFL fonts, vendored here as
build inputs (the module's docstring says how each glyph is fitted):

- `commissioner/Commissioner[FLAR,VOLM,slnt,wght].ttf`: Commissioner by Kostas
  Bartsokas, Copyright 2019 The Commissioner Project Authors
  (https://github.com/kosbarts/Commissioner), SIL Open Font License 1.1
  (`commissioner/OFL.txt`, no Reserved Font Name), unchanged from
  [google/fonts](https://github.com/google/fonts/tree/main/ofl/commissioner)
  (version 1.001, commit ff73ff5e). The Greek lowercase (but omicron, mu and pi),
  the capitals Sigma, Phi and Psi, their small capitals and the Greek kerning come
  from it, each at the wght whose fitted stem matches Torchlette's.
- `notosans/NotoSans-GreekMathSubset[wght].ttf`: the six mathematical variants
  ϑ ϕ ϖ ϰ ϱ ϵ from Noto Sans, Copyright 2022 The Noto Project Authors
  (https://github.com/notofonts/latin-greek-cyrillic), SIL Open Font License 1.1
  (`notosans/OFL.txt`, no Reserved Font Name). It is
  [google/fonts](https://github.com/google/fonts/tree/main/ofl/notosans)
  `NotoSans[wdth,wght].ttf` (version 2.015, commit 2984c575) with its width axis
  pinned and subset to those six glyphs and the six Latin letters the fitting
  measures, with fontTools 4.68.0:

      fonttools varLib.instancer 'NotoSans[wdth,wght].ttf' wdth=100 -o step1.ttf
      pyftsubset step1.ttf --unicodes=U+03D1,U+03D5,U+03D6,U+03F0,U+03F1,U+03F5,U+0048,U+006E,U+006F,U+0070,U+0064,U+0078 \
        --layout-features='' --name-IDs='*' --glyph-names --notdef-outline --no-hinting \
        --output-file='notosans/NotoSans-GreekMathSubset[wght].ttf'

The replacement Noto subset is frozen at SHA256
`845b471cdafa811c6dca84159ac46f00aaec05f6b5338a2377a54d602e3985f4`.
The parent-to-subset commands above are documented provenance; this integration
preparation did not replay that derivation. The preserved width-pinned intermediate
has SHA256 `fb1bc89025e8f37048b2dcc2702a0dd86d86fd088fec32963b9451209d1ea9d2`.

The `african` module takes Ɣ ɣ Ʋ ʋ from Noto Sans too, from eight static weights
vendored here as build inputs (the module's docstring says how each is fitted):

- `notosans/NotoSans-AfricanSubset-<weight>.ttf`, for ExtraLight, Light, Regular, Medium,
  SemiBold, Bold, ExtraBold and Black: Noto Sans version 2.005 (name ID 0 "Copyright 2015
  Google LLC. All Rights Reserved."; its license file: Copyright 2018 The Noto Project
  Authors (github.com/googlei18n/noto-fonts)), SIL Open Font License 1.1 (name IDs 13
  and 14; `notosans/OFL.txt`, and `licenses/NotoSans-AfricanSubset-OFL.txt` in the
  release; no Reserved Font Name). Each is TeX Live 2025's
  `texmf-dist/fonts/truetype/google/noto/NotoSans-<weight>.ttf` (the `noto` package; its
  license is `texmf-dist/doc/fonts/noto/LICENSE_OFL.txt`) subset to those four letters
  and the nine Latin letters the fitting measures, with fontTools 4.68.0:

      pyftsubset NotoSans-<weight>.ttf --unicodes=U+0048,U+004F,U+0055,U+0056,U+006F,U+0075,U+0076,U+0078,U+0079,U+0194,U+01B2,U+0263,U+028B \
        --layout-features='' --name-IDs='*' --glyph-names --notdef-outline --no-hinting \
        --output-file='notosans/NotoSans-AfricanSubset-<weight>.ttf'

  The command was replayed on the TeX Live files: each vendored subset is its output byte
  for byte. SHA256 of each subset and of its parent:

  | weight     | subset                                                             | parent `NotoSans-<weight>.ttf`                                     |
  |------------|--------------------------------------------------------------------|--------------------------------------------------------------------|
  | ExtraLight | `fb8eb509353c7f31415c8bdc6227e43a9e8c863d283e69901cfd70f4d90c4616` | `a63efedb825a74ece7902ec1b26fcb991bf4a49d848ee76c23f5365620538ddd` |
  | Light      | `437bd2e96c765b7cfefba5e9e210b02d4fcec699555bf4821d58a433f21d1cf9` | `193cf399bcc7105760398f727e41952bebe4a4f8e2a8ea49f3181ec0fb4a2368` |
  | Regular    | `69debc1f8d60071a961aa2d2a99b05ecf71233a7ebe1ab652dc71f897b6887a9` | `9cb49a54e520423033f9727be2e53e4805a60656deb09c219740d8e5f3e033ac` |
  | Medium     | `a6fd9fdc09863b52e7b385d7b5d85a76b0d0c3897b7aad0ff2d2f3bbc2dc6d82` | `30ca1a9e9caae1ea676ba5fe3aec1b852c5f57c5455bc61742fcf3ed3a75053e` |
  | SemiBold   | `8c6c6223ae259731945f49c9735e2c77a92afb8a4ef4afe5120a3b03d7429b7e` | `b7296d4d83afb96e2ba11459c677cfec948eebe871c0b84e4851eec186816c30` |
  | Bold       | `5dc7e76f65ce595df9b0dd45f893cf8269387cc5b2723056b6535ce9e1dca11d` | `4439dc44113d49beb0abfdc0def48719deda6f163f3337122ea509c90eed1d0d` |
  | ExtraBold  | `f5f3e68bfa18155fe12eab7ea039083ff20df3580ec52662c527cff0646fee9c` | `b372de8c32a14452c6cdf94da6948e5cffff6f11e8453e42a71140e81687cdb1` |
  | Black      | `084454750ef9767020d6f77086819dec378518db5321e770070dd8b723b507fe` | `2059bc762f958866a4e58b7c202396af5c8557382a9e34dbbd82f978499a8b1b` |

Both fonts' own names stay out of Torchlette Sans; the OFL permits the derivation,
and the copyright notices above are the attribution it asks for.

## Double-struck lowercase

The initial lowercase set contains b, c, d, h, i, j, k, l, m, n, o, p, q, r, u, v, w, x, y, and z.
The b, d, o, p, and q outlines use each style's lowercase contours. The c outline
uses the lightest Mulish master fitted to the target style's ink bounds. Hairline weight is measured
from the straight ascenders of b and d. Bowls and doubled stems preserve the
original vertical bounds, including the p and q descenders. Noto Sans Math provides
the doubled-stroke placement reference. Capital and digit construction is unchanged.
The i and l stems are closed doubled bands. During construction, the i dot expands
around its source centre using Noto Sans Math's dot-to-stem proportion. The outline
includes a central opening. Its vertical extent may exceed the source dot's extent.

The j body follows the light-master hook construction used for capital J, fitted
to j's own descender bounds. Its added rail overlaps the measured hook stroke.
During construction, its hollow dot expands around j's source centre using the
same sizing rule as i.

The h, n, and m forms use doubled vertical bands joined by thin shoulders. Each
shoulder follows its own source counter-arch profile, fitted between the bands.
Separate inner and outer profiles define its thickness. Construction preserves
the source shoulder heights and h ascender.

The u form has two doubled stems. Its lower connection follows the source
lower-curve profiles. The left stem slot has a curved bottom; the right stem
retains a separate baseline foot. Construction preserves the source vertical bounds.

The v form doubles its descending left diagonal. The w form doubles its first
and third diagonals, counted from left to right. The other diagonals are hairlines.
Their construction uses measured source lines and the lowercase stroke dimensions.
The middle hairline of w preserves its source angle. The right-hand pair is
translated horizontally to join it.
The source baseline and terminal heights are preserved, including w's central terminal.

The z form has a doubled diagonal and hairline horizontal terminals. The diagonal
uses its measured source centreline and the lowercase stroke dimensions. The top
and bottom terminals retain their separate source lengths. The slot is closed
inside both terminals.

The x form doubles its descending diagonal and uses a hairline for the rising
diagonal. Straight centrelines connect the source terminal centres. They
approximate the source's small optical offsets near the crossing. The diagonal
slot continues through the crossing.

The y form doubles its upper-left diagonal. The right arm and curved descender
follow the outside edge of the source outline as a hairline. The diagonal slot
is closed above the baseline. At the junction, the doubled arm is trimmed to the
source right edge. Construction preserves the source descender depth.

The k form doubles its vertical stem and lower diagonal. Its upper arm is a
hairline following the source upper edge. The lower diagonal follows its measured
source centreline. Separate closed slots stop inside the stem and arm edges.
Construction preserves the source ascender and arm-terminal heights.

The r form has a doubled stem and a hairline shoulder. The shoulder follows the
source outside curve, including its crown and terminal. The stem stops at its
source top height, below the shoulder overshoot.

## Mathematical script sources

The script alphabet contains 52 letters imported from Noto Sans Math Regular at a
fixed donor weight across styles. The outlines are scaled uniformly to the capital
height. Legacy Letterlike Symbols mappings are included; unassigned holes in
Mathematical Alphanumeric Symbols remain unmapped. The ordinary italic transform
is applied once.

## Files

- `mulish/Mulish[wght].ttf` and `mulish/Mulish-Italic[wght].ttf`: the variable Mulish
  sources, upright and italic, unchanged from
  [google/fonts](https://github.com/google/fonts/tree/main/ofl/mulish) (version 3.603,
  commit 73086f05, "Mulish: Version 3.603 added"; `mulish/OFL.txt` is their license,
  the same file for both).
- `instance.py`: writes the static instance (wght 242 ... 845, upright or italic) that
  `build.py` starts from.
- `build.py`: makes one style of Torchlette Sans from that instance (and reads the
  variable font again for the small capitals and the stem measurements); for an italic
  style it unslants the instance first and reslants the result (see "Italics").
- `verify.py`: the HarfBuzz check of the OpenType features.
- `verify_ss16.py`: the HarfBuzz check of ss16, the prose ligatures: the ligature
  lab's trigger and negative cases for each of the 54, common English, and every
  line of lesson prose.
- `outline_check.py`: checks the outlines for kinks, tiny segments and spurs.
- `fontbakery_gate.py`: judges a fontbakery run from its exit status and report;
  `verify_fontbakery_gate.py` is its test.
- `modules/`: the modules (see above) and their checks, `modules/verify_<name>.py`.
- `commissioner/`, `notosans/`: the Greek and african modules' source fonts and their
  licenses (see "Greek sources").
- `web_features.txt`: the OpenType features the web font keeps; `webfeatures.py`
  reads it for the checks.
- `Makefile`: runs the steps with pinned tool versions.

## Build

Requires [uv](https://docs.astral.sh/uv/) and nothing else: the Makefile pins Python 3.12
and every tool (fontTools 4.68.0, skia-pathops 0.9.2, brotli 1.2.1, ttfautohint-py 0.6.1),
and this folder holds every input. From this folder of a fresh clone:

    make -j7 release

builds the release in `../fonts`, the files the GitHub releases carry:

- `ttf/TorchletteSans-<style>.ttf`, the fourteen styles (seven weights, upright and
  italic), each built from its own static instance of Mulish by `build.py` with the
  default modules (about 4 minutes for all fourteen with `-j7`);
- `webfonts/TorchletteSans-<style>.woff2`, the same fonts, whole, as WOFF2
  (`release.py woff2`, which keeps the .ttf's timestamp);
- `variable/TorchletteSans-Variable.ttf` and `.woff2`, the wght/ital variable font that
  `variable.py` makes from the fourteen .ttf (about 9 minutes), also under the name
  `TorchletteSansVariable`.

The build is deterministic: the same source gives the same bytes. `make -j7 check`
rebuilds the release from scratch in `build/release` and compares it with `../fonts`
(`release.py compare`): the .ttf and the variable font byte for byte, and the web fonts
byte for byte or, for those of v0.5.7 and before, which carried the time they were
written in `head.modified`, table by table. On the v0.5.7 tag every .ttf and both
variable fonts are byte-identical, and every web font has the same tables but for that
timestamp. The folders `auxiliary-v03/`, `canonical_export/` and `variable-v0.4/` are
the record of earlier variable-font work; the release build does not use them.

    make

writes `build/TorchletteSans-<style>.ttf` and the torchlette app's subset web fonts
`build/web/TorchletteSans-<style>.woff2` (`WEB_DIR`). The .ttf keeps
every feature and is hinted. The woff2 is unhinted and keeps only the code points
in the Makefile's `UNICODES` and the features in `web_features.txt`: what browsers
apply by default (kern, liga, clig, calt, rlig, ccmp, locl, mark, mkmk) and what
the app's CSS turns on (ss01, ss02, ss16, the figure features, smcp and c2sc), and rand
(the vector module's random word marks). The
other stylistic sets, the cvNN, case, cpsp, zero, aalt, salt, sups, subs, frac and
the rest are in the .ttf only. The tool versions are pinned, so each woff2 is
byte-identical on every build.

## Web specimen

`specimen/build_sans.py` uses the Python standard library to write `index.html`
and `sans.css` into an existing output directory. From `source/`, run:

    python3 specimen/build_sans.py /path/to/output

`SANS_OUT` can supply the output directory; the positional argument takes precedence.
The version label, release download link, and font cache queries use `VERSION`
with the Makefile release-tag convention: `0.514` becomes `0.5.14`.
Use `--version 0.5.13` to reproduce the earlier release metadata.

The builder reads `specimen-v03.html`, `specimen.css`, `specimen-v03.css`, and
`sans-src/ml-formulas.html` relative to its own directory. `specimen-v03.html` is
a frozen generated snapshot used as input. Preserve its line layout: the builder
selects sections by line number. Supply matching released WOFF2 files in the output
directory’s `fonts/` folder and `/heart.png` at the host site root. Font delivery
and PDF generation are separate steps.

## Check

    make verify

This shapes a test string under all 16,384 combinations of the font's features
with HarfBuzz, checks which glyphs each combination selects, and checks that
Mulish's own features (fractions, superscripts, locale forms) are unchanged from stock
Mulish (Mulish Italic for an italic style) at the same wght.
Then it runs `verify_ss16.py` and each module's `modules/verify_<name>.py`.
For each style it runs on the full font and on the web subset and exits nonzero on any failure.
On the web subset the checks skip the features `web_features.txt` leaves out; on the full
font every check runs.

`make verify` also runs `make fontbakery`, which checks the fourteen .ttf with fontbakery's
universal profile and writes `build/fontbakery.json` and `build/fontbakery.md`. It fails
if fontbakery stops with an error, if the report is incomplete, or on any FAIL but the open
checks listed, with their reasons, in `fontbakery_gate.py`; `verify_fontbakery_gate.py`
checks that the gate rejects broken runs.

CI (`.github/workflows/ci.yml`) has two jobs. The job `check` runs `make check` on an
Apple silicon Mac, the kind of machine the release is built on. The job `verify` runs
`make verify` on all fourteen styles and uploads the fontbakery report as an artifact.
To verify only some styles by hand, name them in `STYLES`. For example,
`make verify STYLES="Regular Italic Bold BoldItalic"` takes about a quarter of the time
that all fourteen take.

    uv run --no-project --with fonttools python outline_check.py build/TorchletteSans-Bold.ttf build/Mulish-675.ttf [--all]

reports kinks (a smooth point whose tangent turns 3-30 degrees), segments under
4 units and small spikes in the glyphs that differ from Mulish (or, with `--all`,
in every glyph).

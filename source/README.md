# Torchlette Sans

## v0.5.0 status

The v0.5.0 fonts were built from an r3 working-tree build of the torchlette repository, not from this directory, which is still the v0.4.0 source and does not reproduce them; the updated source will follow. The variable font has one known intermediate-weight flag: ⋠ (U+22E0) at weight 850 italic. Build inputs and verification are recorded in `provenance/v0.5/`.

Torchlette Sans is the text face of the torchlette web app. It is a modified
version of [Mulish](https://github.com/googlefonts/mulish) and, like Mulish, is
licensed under the SIL Open Font License 1.1 (`OFL.txt`). Mulish's own license
is in `mulish/OFL.txt`; it declares no Reserved Font Name.

The font starts from Mulish and changes it: round dots, wider round letters, a
lower x-height with longer ascenders and descenders, redrawn old-style figures,
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
  capitals. It is held back from the default build (the Makefile's `MODULES_OFF`)
  pending design review, so the shipped fonts have no Greek and browsers fall back to
  a system font.
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
  slashed zero (zero), mark attachment on `build.py`'s glyphs, GDEF classes and
  ligature carets, and aalt and salt.
- `sigmoid`: the first i of "sigmoid" drawn as a small sigmoid curve, in ss16.
- `mathletters`: the letters and operators of ML notation beside the double-struck capitals: ℙ ℍ 𝔼 𝟙 in
  `symbols`' thin doubled strokes, a script ℒ drawn with Torchlette's pen, ℏ, ∥ ∖ ⟂ ⟦ ⟧ ⋆, and the format-12
  cmap that 𝔼 and 𝟙 (outside the BMP) need.
- `ui`: the interface symbols ✓ ✗ ■ □ ▶ ● ○ ★, the circled numbers ①–⑳ with Torchlette's small-cap figures,
  and the keyboard symbols ⌘ ⌥ ⇧ ⏎ ⌫.
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

Both fonts' own names stay out of Torchlette Sans; the OFL permits the derivation,
and the copyright notices above are the attribution it asks for.

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
- `commissioner/`, `notosans/`: the Greek module's source fonts and their licenses
  (see "Greek sources").
- `web_features.txt`: the OpenType features the web font keeps; `webfeatures.py`
  reads it for the checks.
- `Makefile`: runs the steps with pinned tool versions.

## Build

Requires [uv](https://docs.astral.sh/uv/). From this folder:

    make

This writes `build/TorchletteSans-<style>.ttf` for the fourteen styles (seven weights,
upright and italic) and the subset web fonts
`../../web/public/fonts/TorchletteSans-<style>.woff2`. The .ttf keeps
every feature and is hinted. The woff2 is unhinted and keeps only the code points
in the Makefile's `UNICODES` and the features in `web_features.txt`: what browsers
apply by default (kern, liga, clig, calt, rlig, ccmp, locl, mark, mkmk) and what
the app's CSS turns on (ss01, ss02, ss16, the figure features, smcp and c2sc). The
other stylistic sets, the cvNN, case, cpsp, zero, aalt, salt, sups, subs, frac and
the rest are in the .ttf only. The tool versions are pinned, so each woff2 is
byte-identical on every build; `make check` rebuilds all fourteen from scratch and
compares.

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

CI (`.github/workflows/ci.yml`, job `fonts`) runs `make verify` on four styles, Regular,
Italic, Bold and BoldItalic (`make verify STYLES="Regular Italic Bold BoldItalic"`), which
takes about a quarter of the time all fourteen do, and uploads `build/fontbakery.md` when
the job fails. Run `make verify` on all fourteen before a change ships.

    uv run --no-project --with fonttools python outline_check.py build/TorchletteSans-Bold.ttf build/Mulish-675.ttf [--all]

reports kinks (a smooth point whose tangent turns 3-30 degrees), segments under
4 units and small spikes in the glyphs that differ from Mulish (or, with `--all`,
in every glyph).

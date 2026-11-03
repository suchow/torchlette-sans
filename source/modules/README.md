# Torchlette Sans modules

A module is one Python file, `modules/<name>.py`, that extends the font without
editing `build.py`. Several people can work on the font at once (kerning,
symbols, super- and subscripts, Greek, hinting ...), each in their own file.
With no module files, `build.py` writes the same bytes it did before modules
existed (`make check` says `identical` for every style).

## Files and names

- `modules/<name>.py` is a module. `<name>` is lowercase letters, digits and `_`,
  starting with a letter (`kern`, `greek`, `supsub`, `math_symbols`).
- `modules/verify_<name>.py` is that module's check (see "Verify" below). It is
  not a module.
- `modules/_*.py` are ignored by the build: use them for notes or scratch code.
  The build does not put `modules/` on `sys.path`, so a module cannot import them.
- This README.

Modules run in sorted file-name order (`greek` before `kern` before `supsub`),
each phase for all modules before the next phase. If your module must run after
another, say so in its docstring and pick the name accordingly; to order layout
lookups, use the placement arguments below instead of the file name.

## Phases

A module defines any of three functions. A missing one is skipped.

```python
def glyphs(ctx): ...     # add or change outlines, advances, cmap entries
def features(ctx): ...   # hand over feature-file text with ctx.gsub() / ctx.gpos()
def post(ctx): ...       # edit tables just before the font is saved
```

`build.py` imports every selected module once, right before the `glyphs` phase,
as its own Python module named `tsmod_<name>`, registered in `sys.modules`
before it runs, as `import` does (so `dataclasses`, `typing`, `pickle` and
`from __future__ import annotations` work; its top-level names never collide
with another module's or with `build.py`'s). Top-level code therefore runs at
that point too; keep it to imports and constants.

1. `glyphs`: after every glyph of `build.py` exists (outlines, small caps,
   alternates, the ss16 ligatures) and after `build.py` has written its own
   feature text (`FEA_HEAD`, `S16_FRONT`, `FEA_MAIN`, `ALT_FEA`, `S16_FEA` are all
   strings by now), and before the name table edits and any feature compilation.
   Glyphs added here go through `build.py`'s later passes like its own: the
   overlap removal and the smooth-point restoration run on every simple glyph
   after compilation, so draw with `add()` and overlapping shapes are fine.
2. `features`: after the name table and OS/2 edits, right before the GSUB
   compilation. Every module's text is collected first, then compiled (see
   "Layout" below).
3. `post`: after all layout work (GSUB and GPOS merged, the small-cap lookups
   moved to the front of GSUB, overlaps removed, smooth points restored), just
   before `maxp.numGlyphs` is set and the font is saved. Use it for table and
   metadata edits and hinting. A glyph added here skips the outline passes and
   cannot take part in the features.

## The context object

Every phase function gets the same `ctx` for that module.

- `ctx.module`: the module's name.
- `ctx.NAME` reads `build.py`'s global `NAME` at call time: anything `build.py`
  defines at top level. `ctx.globals` is that dict itself; assign through it to
  rebind a global (`ctx.globals['X'] = ...`), which you should rarely need.
- Any other attribute you set on `ctx` (`ctx.made = [...]`) stays for the module's
  later phases. Module-level variables work too.
- `ctx.map(codepoint, glyph)`: map a code point in every Unicode cmap subtable.
  The font has format 4 subtables only, so a code point above U+FFFF fails until
  some module adds a format 12 subtable.
- `ctx.gsub(text, before=None, after=None)` and `ctx.gpos(text, before=None,
  after=None)`: feature-file text (see "Layout").
- `ctx.ss16_owner(id, [glyphs])`: declare that ss16 proposal `id` (see "Extending
  ss16") adds these glyphs, so `verify_ss16.py` treats them as a kept proposal's.
- `ctx.log(*args)`: print with the module's name in front.

The `build.py` globals you are most likely to want (read `build.py` for the rest):

| Name | What it is |
|---|---|
| `font`, `glyf`, `hmtx`, `gs` | the font being built, its glyf and hmtx tables, its glyph set |
| `STYLE`, `SRC_W`, `WEIGHT_CLASS` | `'Regular'`/`'SemiBold'`/`'Bold'`/`'Italic'`/`'BoldItalic'` ..., the Mulish wght (324/510/675), 400/600/700 |
| `ITALIC`, `WEIGHT_NAME` | whether this is an italic style; the weight's name (`'Regular'` for `'Italic'`) |
| `ITALIC_K`, `ITALIC_YC`, `shear_font`, `dot` | the italic's slant (0 in an upright) and shear centre; the shear of a whole font; a round dot that stays a circle in the italic (see "Italics" below) |
| `P(key, default)` | a tuning knob, overridable from the environment |
| `path_of(name, dx, dy, fn)` | a glyph's outline as a `pathops.Path`, shifted or point-mapped |
| `rect`, `poly`, `ellipse`, `band`, `union`, `diff`, `transformed`, `unit` | shapes and boolean operations on paths |
| `mv(p, dx, dy=0)`, `mirror(p, axis)` | a path moved, or mirrored about the vertical line x = axis |
| `clip(p, (x0, y0, x1, y1))` | the part of a path inside a box (a dot cut off a letter, say) |
| `hspans(p, y)`, `vspans(p, x)` | the ink of a path along a horizontal (vertical) line, as sorted (start, end) intervals: stem widths and positions |
| `add(name, path, width)` | write a glyph (simplified, converted to quadratics, tidied) and append it to the glyph order |
| `s16_add`, `s16_raw` | ss16's own adders (they record the glyph under a lab id); modules should use `add` and `ctx.map` |
| `tidy(g)`, `W(name)`, `side(f, name)` | clean a glyph; a glyph's advance; its sidebearings |
| `SV`, `SH`, `SM` | this style's vertical stroke, horizontal stroke and minus thickness relative to Regular's (1.0 in Regular) |
| `SIDE`, `CAP` | this style's ring side and cap thickness (67 and 56 in Regular) |
| `M`, `R`, `measure(f)` | stroke measurements of this style's source instance and of the wght-324 one |
| `XH`, `X0`, `AD`, `DD`, `Y`, `YL` | the x-height (470), Mulish's (500), ascender rise, descender drop, the vertical remap of Mulish's y |
| `inst(w)` | an instance of variable Mulish at wght `w` (cached) |
| `GDEF_CLASS` | Mulish's GDEF glyph classes, a dict (1 base, 2 ligature, 3 mark, 4 component) |
| `DIGITS`, `FIG`, `FORMS_L`, `FORMS_O` | figure names and their lining and old-style forms |
| `SC_SCALE`, `SC_H`, `sc_font` | small-cap scale and height, the heavier instance they come from |

Mulish's own GPOS (kern, mark, mkmk ...) and GDEF are in `font` as they ship.

## Italics

An italic style (`ITALIC` true, `STYLE` `'Italic'`, `'LightItalic'` ...) is built from
Mulish Italic, which `build.py` unslants before anything is measured or drawn and
reslants again after the smooth-point pass, right before the `post` phase. So in the
`glyphs` and `features` phases the font is upright: measure and draw exactly as for an
upright style (axis-aligned bars, upright stems, `hspans` at a height), and your glyphs
lean with the letters once the font is reslanted, as Mulish Italic's own operators and
figures do. A shape that must stay round in the italic (a dot) is drawn with `dot(cx,
cy, r)`, which places it where the reslant will put it and shears it back. In `post` the
font is slanted and its points are rounded; a module that adds outlines there draws them
leaning itself (`shear_font` shows the transform: x moves by `ITALIC_K * (y -
ITALIC_YC)`). Kerning and advances are the same in both frames.

## Layout

### GSUB: `ctx.gsub(text, before=..., after=...)`

All GSUB text, `build.py`'s and every module's, compiles in one feaLib pass, in
this order of blocks:

| Anchor | Block | What is in it |
|---|---|---|
| `classes` | `FEA_HEAD` | `languagesystem DFLT dflt; languagesystem latn dflt;` and the classes `@LNUM @TOSF @OSF @PNUM @SEVEN8 @SCNUM @SCTF @D @LC @UC @SC @LACC @SCACC_L @UACC @SCACC_U @SYM @SCSYM @LX @SCLX @UX @SCUX` |
| `ss16_front` | `S16_FRONT` | the ss16 logotypes and TT, which must see plain letters |
| `main` | `FEA_MAIN` | liga, ss01, ss03, ss02, onum, tnum, pnum, ss08, and the small-cap lookups (smcp, c2sc) |
| `alternates` | `ALT_FEA` | ss04-ss07 |
| `ss16` | `S16_FEA` | the rest of ss16 and ss15, the `@S16_*` classes, the cv01-cv99 features |

`before='main'` puts your text right before that block, `after='ss16'` right
after it. The default is `after='ss16'`: last. `after='classes'` is the earliest
place (nothing can precede the language systems; `before='classes'` is an
error). Texts given to the same place keep module order, then call order.

Lookups take the order of the text. In the font's lookup list they come out as:
Mulish's own GSUB lookups first, then every lookup of the compiled text in text
order; then `build.py` moves the smcp and c2sc lookups that do not map figures
or the slash to the very front (so ligatures cannot form under small caps). That
move applies to module lookups too: a lookup you add to smcp or c2sc goes to the
front unless it maps `zero` or `slash`. A module cannot put a lookup ahead of
Mulish's own.

Rules for GSUB text:

- No `languagesystem` statements. Your features are registered for every script
  and language the font has (DFLT, cyrl, latn). A Greek feature works under
  HarfBuzz through DFLT.
- A `feature xxxx { ... } xxxx;` block for a tag that already exists adds your
  lookups to it (feaLib merges same-tag blocks; the result is merged with
  Mulish's record of that tag).
- Classes from an earlier block are visible: `FEA_HEAD`'s everywhere,
  `@S16_WORD` and `@S16_WORDNOS` from `after='ss16_front'` on, the other
  `@S16_*` classes only after `ss16`. Named lookups of `build.py` can be
  referenced from text placed after them.
- `featureNames` works here (the name records are copied into the font).
- Positioning rules are an error here; use `ctx.gpos()`.
- `table GDEF { ... }` has no effect (only GSUB is taken from the compile). Set a
  new glyph's class in `GDEF_CLASS` in the glyphs phase instead.

### Extending ss16

A module may add proposals to ss16, the Torchlette prose ligatures the app turns
on. Write the lookups with `ctx.gsub()` and register them in a `feature ss16 {
lookup ...; } ss16;` block; feaLib merges it with build.py's ss16. Placement
decides what the lookups see:

- `after='ss16_front'`: right after the logotypes and TT, before liga, ss01-ss03
  and the figure features, so the lookups see plain letters (as the logotypes
  do) and can use the word guards `@S16_WORD` / `@S16_WORDNOS` (`ignore sub
  @S16_WORD x' y' z';`). This is the place for whole-word replacements.
- `after='ss16'` (the default): after all of ss16, where liga has made ff and
  tt, ss02 has made `->` an arrow and onum the figures old-style; the `@S16_*`
  classes are all defined. This is the place for rules that depend on those.
- `after='main'`: after liga, ss01-ss03, ss02, onum/tnum/pnum and ss08, before
  ss04-ss07; `after='alternates'` (the same as `before='ss16'`): after those too,
  before the rest of ss16.

Within a feature, lookups run in lookup-list order, so ss16's lookups and yours
run in the order of the compiled text, whatever order the `feature ss16` block
names them in. A module does not get a cvNN unless it writes one.

Declare every glyph a proposal adds with `ctx.ss16_owner(id, [glyphs])` (in
any phase; once per id, or again from the same module to add glyphs). `id` is
an int that build.py's proposals (`S16_ACCEPTED`) and other modules do not use:
take the next free number above the labs' (sigmoid has 217) and say so in the
docstring. Keep it above 99: `verify_ss16.py` expects a `cvNN` feature for
every id up to 99. Before saving, build.py checks that each declared glyph
exists and is not build.py's or another proposal's, and writes the
declarations to `<PostScript name>.ss16.json` beside the output font
(`build/TorchletteSans-Regular.ss16.json`); a build with no declarations
removes that file. `verify_ss16.py FONT` reads the file from FONT's folder by
FONT's PostScript name, so the full font and the web subset that `make verify`
writes beside it both find it; it counts the glyphs as that proposal's in the
lesson-prose check and the "nothing appears with ss16 off" checks.

### GPOS: `ctx.gpos(text, before=..., after=...)`

Each `ctx.gpos()` text is compiled on its own, after `FEA_HEAD` (so its classes
are available, but nothing from other GPOS texts or from `S16_FEA`), once
`build.py`'s own GPOS work is done. Its lookups are appended to the font's GPOS,
its features merged (a tag the font has gains the lookups, a new tag gets a
record in every language system), and then its lookups move to the place named:

| Anchor | Block |
|---|---|
| `mulish` | Mulish's own GPOS lookups (its kern, mark, mkmk ...) |
| `ss16_ordinals` | `S16_ORD_POS`, the ordinals' figure-superior pairs (ss16, cv96) |
| `smallcap_kern` | `SC_KERN`, the small-cap kerning (kern) |

The default is `after='smallcap_kern'` (last); `before='mulish'` is first.
Lookup order matters for GPOS only within one glyph run's features (values add
up; a later lookup sees earlier adjustments), so most modules can keep the
default. `featureNames` in GPOS text is not supported.

## Avoiding collisions

- Glyph names: an encoded glyph takes its standard production name (`uni2208`,
  `alpha`, `uni00B9`), after checking that the font does not have it already. An
  unencoded glyph carries the module name as its last suffix: `alpha.sc.greek`,
  `one.sups.supsub`, `arrow.long.math`.
- Lookup names start with the module name in capitals: `KERN_PAIRS`,
  `GREEK_SC`, `SUPSUB_SUPS`. Class names too: `@GREEK_LC`.
- Feature tags: register the tag you take (a new `ssNN` or `cvNN`) in your
  module's docstring; ss01-ss08, ss15, ss16 and cv01-cv99 (ss16's) are taken, except the explicitly
  reassigned `cv82` for graphnodes' three circle alternatives. The retired tensor
  logotype and `cv48` remain forbidden.
  Existing tags can be extended: Mulish's GSUB aalt, calt, case, ccmp, dnom, frac,
  liga, locl, numr, onum, ordn, sinf, subs, sups and GPOS kern, mark, mkmk, and
  build.py's tnum, pnum, smcp, c2sc.
- Around every phase call the build compares each glyph by value (points, flags,
  contour ends or components, and its hmtx entry) and every cmap subtable (its
  platform, encoding, format and full mapping). It stops with an error naming the
  module when, in any phase, a module changes or removes a glyph it did not add
  (build.py's or another module's), or changes the mapping of a code point that
  was already mapped in any subtable, the non-preferred ones included. Removing a
  subtable counts as unmapping its code points; adding one is fine as long as it
  maps existing code points to the glyphs they already had (a format 12 copy of
  the BMP mapping, say). New code points are free. Because a client reads only
  the best Unicode subtable it knows ((3,10) first, then (0,6), (0,4), (3,1),
  (0,3) ...), the best subtable after a phase, and every Unicode subtable the
  phase added, must still map every code point of the previous best one to the
  same glyph: a format 12 table holding only a new non-BMP code point would hide
  the rest, so copy the whole mapping first, then `ctx.map` the new code point.
  `CMAP_OVERRIDE` covers a code
  point in every subtable; `ctx.map` writes all Unicode subtables. A module owns the glyphs it adds and may
  keep changing them in its later phases. To change other glyphs on purpose,
  list them in a module-level `GLYPH_OVERRIDE = {'a', ...}`; to remap code
  points, `CMAP_OVERRIDE = {0x2212, ...}`. Say why in the module docstring: it
  is an edit to the shared font. (TrueType instructions are not compared, so a
  hinting module can add them in `post`.)
- Code points ship in the web font only within the Makefile's `UNICODES` ranges;
  a module that adds code points outside them must say so (and the ranges have
  to grow in a separate change to the Makefile).
- ss16's word-boundary classes `@S16_WORD` and `@S16_WORDNOS` are recomputed
  after the glyphs phase: a glyph a module adds or maps to a letter or digit code
  point (Greek alpha) counts as a word letter, so "αgradientα" keeps its letters
  and forms no logotype. The other ss16 letter classes (`@S16_LC`, `@S16_UC`,
  `@S16_LET`, `@S16_WD`) are ASCII by design and do not grow.

## Choosing modules: MODULES

    make MODULES=kern,greek     # only these two
    make MODULES=none           # none: the font exactly as build.py alone makes it
    make                        # the explicit 22-module MODULES_DEFAULT release set

`MODULES_OFF` in the Makefile holds a module back from the default set without
deleting it: a module that is not ready to ship stays in `modules/`, out of the
shipped fonts and out of `make verify`, until it leaves the list. Naming it in
`MODULES` still builds it (`make ttf verify BUILD_DIR=/tmp/me/build MODULES=greek,kern`).
`MODULES_OFF` is currently empty; Greek and mathitalic are in `MODULES_DEFAULT`.
A new module file is not automatically added to that explicit release set.

`build.py` reads the environment variable `MODULES` (a comma list, `none`, or
empty for all) and stops on a name with no file. The Makefile passes it the
selection it has worked out (`MODULES`, or `MODULES_DEFAULT` minus `MODULES_OFF`) and
records it in `$(BUILD_DIR)/modules.txt`, so changing it rebuilds the fonts;
editing or adding a module file does too.

## Building without clobbering anyone

`make` normally writes `build/` and the committed web fonts in
`../../web/public/fonts`. When several people build at once, give each build
its own directory and leave the web fonts alone:

    make ttf    BUILD_DIR=/tmp/me/build MODULES=kern     # the fourteen .ttf only, no woff2
    make verify BUILD_DIR=/tmp/me/build MODULES=kern
    make        BUILD_DIR=/tmp/me/build WEB_DIR=/tmp/me/web MODULES=kern   # woff2 too, elsewhere

`make /tmp/me/build/TorchletteSans-Bold.ttf BUILD_DIR=/tmp/me/build` builds one
style. `BUILD_DIR` holds the Mulish instances, the .ttf, the verify subsets and `make
check`'s files. `WEB_DIR` is where `make` writes the woff2. `make check` always
compares with the committed woff2 in `../../web/public/fonts`, rebuilding in
`BUILD_DIR` (which it deletes first). Only write `../../web/public/fonts` when
the change is meant to ship.

## Verify

`make verify` runs, for every style, `verify.py` and `verify_ss16.py` and then,
for each selected module that has one, `modules/verify_<name>.py`, twice:

    MULISH_STATIC=<BUILD_DIR>/Mulish-<wght>.ttf  verify_<name>.py <font.ttf> <style> full
    MULISH_STATIC=<BUILD_DIR>/Mulish-<wght>.ttf  verify_<name>.py <subset.ttf> <style> subset

`full` is the built font; `subset` is its web subset (the shipped woff2's glyphs
and layout, kept as a .ttf with glyph names). `<style>` is Light, Regular, Medium,
SemiBold, Bold, ExtraBold or Black, or LightItalic, Italic ... BlackItalic;
`MULISH_STATIC` is stock Mulish (Mulish Italic for an italic) at the same wght, for
comparisons. The
interpreter has fonttools 4.68.0 and uharfbuzz 0.57.0. The script prints what it
checked and exits nonzero on any failure, which stops `make verify`.

## Before handing a module over

    make ttf verify BUILD_DIR=<yours> MODULES=<name>
    make ttf verify BUILD_DIR=<yours>                 # the explicit release default; include a new module explicitly if not yet selected
    uv run --no-project --with fonttools python outline_check.py <yours>/TorchletteSans-Bold.ttf <yours>/Mulish-675.ttf

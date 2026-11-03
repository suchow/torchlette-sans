# Variable companion

`variable.py` builds a full, unsubsetted TrueType/WOFF2 companion from the fourteen
finished Torchlette Sans static fonts. It reads those fonts without modifying them.
Build the statics with the intended module configuration first; a variable build
cannot acquire a feature or script absent from its inputs.

```sh
uv run --no-project --python 3.12 \
  --with fonttools==4.68.0 --with skia-pathops==0.9.2 --with brotli==1.2.1 \
  python fonts/torchlette-sans/variable.py \
  --masters /absolute/path/to/fourteen-statics \
  --output /absolute/scratch/TorchletteSans-Variable.ttf \
  --woff2 /absolute/scratch/TorchletteSans-Variable.woff2 \
  --work-dir /absolute/scratch/variable-work \
  --report /absolute/scratch/variable-build.json
```

The inputs are `TorchletteSans-Light.ttf`, `Regular`, `Medium`, `SemiBold`, `Bold`,
`ExtraBold`, and `Black`, plus `LightItalic`, `Italic`, `MediumItalic`,
`SemiBoldItalic`, `BoldItalic`, `ExtraBoldItalic`, and `BlackItalic` in the same
naming pattern. All fourteen must have identical glyph order, Unicode mapping,
and units per em. Keep the work directory private to this build. Outputs and
reports must not overwrite a static input.

The output has continuous `wght` from 300 to 900, default 400, and the registered
`ital` selector from 0 to 1, default 0. Fourteen named instances correspond to the
static styles. Set `ital` to 0 for Roman and 1 for italic. The selector switches to
genuine italic outlines at 0.5; it does not gradually slant Roman glyphs. Weight
interpolation works within either style. The monotonic `avar` map gives every
named weight an exactly representable variation coordinate while retaining the
usual user-facing weight numbers. Four narrow plateaus around unrepresentable
input coordinates are each about 0.03052 CSS weight units wide; their input
coordinates increase strictly and their outputs never decrease. This keeps named
weights exact in serialized consumers without changing named styles.

## Outlines and layout

Both complete style namespaces are retained. Required GSUB feature variations
select the italic namespace, preserving each style's own substitutions and
positioning rather than applying Roman kerning to italic outlines. Unicode
default-ignorable controls retain their original glyph IDs: their real italic
outlines and metrics vary directly, because substituting their IDs would interfere
with a shaper's default-ignorable handling. No encoded character or alternate is
dropped to obtain compatible masters. Static origin offsets are rebased into the
actual rendered coordinate frame, honoring the last `USE_MY_METRICS` component
recursively. Variable glyphs then satisfy `LSB = xMin` and
set the required `head` flag; no invisible bounding-box padding is added.
Control-box metrics can differ after exact subdivision even when painted curves
and placement agree, and those differences must be reported separately.

For every simple glyph, the builder first
normalizes its nonzero filled shape (so self-touching boundaries and separate
counters are represented consistently), then aligns contours to a shared
reference anchor and subdivides existing quadratic curves at shared arc-length knots.
Where corresponding hard corners exist in every master, subdivision preserves
those corner boundaries rather than matching a corner to the middle of a curve.
Matching point counts alone are not accepted as proof of correspondence.
If every master already has exactly the same raw curves and compatible point
signatures, the builder preserves those source outlines directly; unnecessary
subdivision can otherwise round away narrow openings. Each master retains its own
metrics. A matching signature with differing geometry still takes the normal path.
Compatible composite graphs inherit these canonical leaf outlines and vary their
placements, preserving fixed linear component transforms.
Subdivision preserves the original curves apart from TrueType integer rounding;
it does not approximate curves with polygons. Missing contours are represented by
zero-area contours, with winding preserved. Opening counters can instead use
exactly retraced boundary bridges, after testing actual geometric containment.
For the bounded case of one outer boundary and at most one counter per master,
spatial counter identities distinguish a counter closing into ink from an unrelated
counter opening to the exterior. Closing counters keep independent zero-area slots
when absent; opening counters use retraced bridges. Ambiguous containment or
multiple outer boundaries fall back to the established path. This classification
is a geometric heuristic, so the complete endpoint and intermediate gates remain
mandatory.
For a void that splits a glyph into separate components, complementary half-plane
intersections are used only if both pieces have one filled boundary in every
master. The report lists every such repair and its source-area preservation check;
selection is by topology rather than by glyph name. Endpoint and intermediate
visual checks are still necessary: compatible point counts alone do not establish good
interpolation.

Static point-referencing hint instructions are removed only from private copies.
The variable companion is therefore unhinted; the existing hinted statics remain
available unchanged. Horizontal advance widths and origin/bearing adjustments
use the complete phantom-point data in `gvar`. The optional `HVAR` table is
omitted so rasterizers use those composite-origin deltas consistently; advance widths and actual rendered origins are preserved. Raw static versus
variable control-box bearings can differ after curve subdivision; these
representation differences must not be confused with a painted-origin shift. Point-index GPOS anchors or GDEF carets are rejected until
explicitly converted, since changing outline point indices would invalidate them.
Coordinate-based anchors, carets, marks, kerning, and all existing feature tags
are retained. Where an anchor genuinely exists only at heavier weights, GPOS
feature variations preserve its presence or absence; a missing anchor is not
silently replaced with an origin anchor. Conditional lookup groups preserve the
original execution order, with feature and contextual lookup references remapped
together, so base-to-mark attachment still precedes mark-to-mark attachment.

GPOS anchor merging uses a strict logical view of direct positioning subtables and
valid format-1 `ExtensionPos` wrappers. It compares the same ordered coverage,
classes, context references, flags and mark-filter fields, and writes anchors
through their actual target paths. A wrapper with an incorrect declared type,
mixed or nested types, or unknown or missing metadata is rejected. This handles
fontTools changing extension packaging without treating a real layout change as
an equivalent representation. Table-fixture checks do not establish final-family
geometry or native-size visual acceptance.

When MATH is present, every master must provide it with compatible structure.
Every varying `MathValueRecord`, including nested kern and assembly records, uses
a VariationIndex in the shared GDEF variation store. Existing GPOS variation
indices remain intact. An integer local hat basis preserves source values at
named endpoints and piecewise-linear weight interpolation without rounding
fractional hierarchical deltas. MATH fields without a variation mechanism must be identical
across masters, including construction advances and connector lengths; differing
values produce an explicit error. Existing MATH device tables require explicit
composition and are rejected. This prevents a default-only MATH table from being
mistaken for a variable implementation. The pinned fontTools 4.68 instancer
supports MATH VariationIndex resolution, including partial-instance index remapping.
The independent checker evaluates the original variable store directly as a
separate oracle. Before publication, also verify serialized full and partial
instances in both axis orders; this is a separate integration check.
For a supported two-stage export that derives MATH values from the immutable full
source, see [MATH-aware saved-instance export](README-math-export.md). Generic
fontTools chains retain their independent rounding behavior.

## Optional auxiliary geometry input

Ordinary builds need only `--masters`. That path uses the ordinary canonicalizer;
precision, origin, discrete style, and default-ignorable handling are unchanged.
An optional second input can supply explicitly selected raw simple contours when
ordinary shape normalization cannot establish useful correspondence:

```sh
# Add these two arguments to the build command above:
--auxiliary-manifest /absolute/path/geometry.json \
--auxiliary-sha256 <lowercase-SHA256-of-exact-manifest-bytes>
```

For the three codekeys source-mode outputs and their scoped input contract, see
[Auxiliary codekeys geometry](README-auxiliary-codekeys.md).

`--masters` remains the authoritative polished fourteen-font reference. Auxiliary
advances, bearings, kerning, marks, global metrics, feature tables, names, and
other tables are not imported. The report records differing auxiliary table
hashes and ignored metrics. Only selected outlines are copied after normalization
into their own actual rendered frame. Original recursive `USE_MY_METRICS` origins
and original layout/advances remain in charge. Unselected outlines follow the
ordinary canonicalization path; selected raw contours bypass Boolean normalization
and subdivision, retaining their winding and `OVERLAP_SIMPLE` flag.

The manifest is UTF-8 JSON with these exact fields (unknown or duplicate fields
are errors):

| Field | Required value |
| --- | --- |
| `schema`, `version` | `"torchlette-auxiliary-geometry"`, integer `1` |
| `source_mode` | Nonempty description of the raw geometry source |
| `generator` | Object with `source`, `config` file records and nonempty `commit` lineage |
| `originals`, `auxiliaries` | Each exactly fourteen `{ "weight": 300, "ital": 0, "file": { "path": "...", "sha256": "..." } }` rows, one for every weight/style pair |
| `replacements` | Nonempty list of `{ "glyph": "name", "ital": [0, 1], "curve_provenance": "ordered contour/arc lineage" }` records; `[0]` or `[1]` selects only that style |

Every file record is exactly `{ "path": "relative-or-absolute-path", "sha256":
"lowercase-digest" }`. Relative paths resolve beside the manifest. `generator.source`
and `generator.config` are hashed provenance inputs, never executed. Original rows
must identify the exact `--masters` files. Every font is parsed from an immutable,
hash-verified byte snapshot. Original and auxiliary glyph order, all cmap subtables
(including variation sequences), units per em, and fourteen style identities must
match. Each selected style has a complete seven-weight grid of identical raw
contour endpoints and on/off-curve signatures; a provenance declaration is also
required. An overlap flag alone never selects a glyph or proves correspondence.

Initial support deliberately rejects empty/composite selected glyphs, shared
structural/default-ignorable slots, incompatible affected original parent graphs,
and affected point-matched or transformed/inconsistent metric-owner parents.
These restrictions apply to the selected dependency closure, not unrelated
ordinary composites or ignored auxiliary parents/layout. Parent outlines retain
original component order/transforms and origin compensation. Full auxiliary fonts
are required for namespace validation, but unselected auxiliary outlines are not
normalized or imported.

Keep work/output/report paths private. Existing symlink and hardlink aliases to
any input, or between generated files, reject. The manifest, generator inputs,
originals, and auxiliaries are rehashed against their initial expected digests
before output and again at completion; an input change fails the build. This is
input validation and geometry-only intake, not acceptance of an auxiliary source.
The independent checker must still use the original `--masters`, unchanged
endpoint/intermediate bounds and full feature corpus. Tiny intake fixtures do
not certify an actual family or authorize substituting auxiliary fonts as oracles.

## Verification and integration

Run the independent checker against the same static directory:

```sh
uv run --no-project --python 3.12 \
  --with fonttools==4.68.0 --with uharfbuzz==0.57.0 \
  --with freetype-py==2.5.1 --with numpy==2.3.4 --with scipy==1.16.3 \
  --with skia-pathops==0.9.2 \
  --with brotli==1.2.1 \
  python fonts/torchlette-sans/verify_variable.py \
  --masters /absolute/path/to/fourteen-statics \
  --font /absolute/scratch/TorchletteSans-Variable.ttf \
  --woff2 /absolute/scratch/TorchletteSans-Variable.woff2 \
  --report /absolute/scratch/variable-verification.json
```

For the complete registered-feature gate, also pass `--corpus` with the frozen
module input-corpus JSON and `--require-corpus`. The built-in sample strings alone
do not establish coverage of every module. Recreate that corpus when the active
module configuration changes; a historical corpus does not cover new repertoire.

The corpus is an object with a nonempty `cases` list and optional `provenance`.
Each case supplies a unique `(module, id)`, nonempty `text`, and a `features`
object mapping four-character OpenType tags to unsigned integer values. It may
also supply `preserve_default_ignorables` (boolean) and `language`:

```json
{
  "cases": [
    {
      "id": "bashkir-smallcaps-i",
      "module": "cyrillic",
      "text": "і",
      "features": {"smcp": 1},
      "language": "ba"
    }
  ]
}
```

`language` is an optional nonempty ASCII hyphen-separated HarfBuzz language tag,
for example `ba`, `cv`, or `sr-Latn`. Components contain at most eight characters;
the first contains letters, and later components contain letters or digits. This
checks tag syntax, not registration or font support. An absent `language` keeps
the existing `guess_segment_properties()` behavior. A declared language is applied
to a fresh buffer for both the original static oracle and the variable font;
it does not change the cached font or subsequent default-language calls. A null,
empty, malformed or non-string language is rejected. Generic `context`, `script`
and `direction` fields are not accepted. Do not discard a source verifier's locale
when harvesting its cases. Expected output fields are never part of this corpus.

The JSON report records the exact static input hashes, complete branch mapping,
canonicalized glyphs and missing contours, sparse anchor rules, output hashes,
and retained feature/table inventories. The builder checks that all input font
bytes remain unchanged. It fixes output timestamps and orders generated records
so identical inputs and the pinned toolchain can produce identical font bytes.

Before publication, independently compare all fourteen named endpoints with the
statics: outlines and winding, metrics, marks, kerning, feature substitutions,
default-ignorables, and all MATH records. Inspect intermediate weights for counter
closures, stray islands, or spikes. Check TTF/WOFF2 parity and repeat-build byte
identity. Review native-size Roman and italic specimens against the corresponding
statics and a professional reference. A successful merge is not a visual approval.

The companion retains embedded copyright and OFL names from the statics. Distribute
the project's complete attributed `OFL.txt` alongside it, just as for the static
family. This entry point does not install fonts, update the app, overwrite public
assets, rebuild statics, or publish a release. The owner must integrate it only
after rebuilding and verifying the final fourteen-style module snapshot.

References: the [registered italic axis](https://learn.microsoft.com/en-us/typography/opentype/otspec190/dvaraxistag_ital),
[fontTools variable-font tooling](https://fonttools.readthedocs.io/en/latest/varLib/),
[feature variations](https://fonttools.readthedocs.io/en/stable/varLib/featureVars.html),
and the OpenType [gvar phantom metrics](https://learn.microsoft.com/en-us/typography/opentype/spec/gvar)
and [optional HVAR table](https://learn.microsoft.com/en-us/typography/opentype/spec/hvar).

## Structural missing glyphs and the native raster runtime

The independent verifier accepts either the original two-namespace architecture
or an actually shared structural glyph ID 0. It derives sharing from original and
variable missing-character shaping at all fourteen named endpoints, with and
without preservation of default ignorables, and verifies the original glyph order.
It does not consult the builder report or recognize a glyph-name allowlist.
When ID 0 is shared, its actual native outline, bearings and raster are checked
against each original style; its name or advance alone cannot establish correctness.
Other glyphs retain the existing strict namespace identity checks. Built-in
regressions now include unencoded ZWJ/ZWNJ and an ordinary absent character,
both normally and with preservation requested. A visible missing glyph is never
normalized to hidden space to make these comparisons pass.

`freetype-py` pins the Python binding, not the native FreeType library. Success
and verifier-error reports identify the actual loaded library version, absolute
path and SHA-256. The verifier never selects another backend or retries with one;
an unresolved library path is an explicit provenance failure. The caller must
select its native runtime before importing the binding and preserve that selection
with the proof. For example, a private `PYTHONPATH` binding directory can contain
the pinned `freetype` Python package and its normal platform library filename
linked to a caller-built FreeType library, then invoke the command above with
`PYTHONPATH=/absolute/path/to/that/private-binding`. Verify the recorded native
path/hash rather than assuming that environment variable selected it.

A known scoped runtime difference is preserved in the added-repertoire audit:
the unchanged Hamilton-formula fleuron in both the original static and variable
fonts passes `FT_Outline_Check` but overflows the rasterizer at 160 ppem with
FreeType 2.13.2. The explicitly selected, separately hashed FreeType 2.14.1 library
renders the same unchanged outlines at that same size. This is evidence for those
artifacts and renderers, not a blanket support claim for all FreeType versions.
Do not lower the size, skip the glyph or silently switch libraries after an error.

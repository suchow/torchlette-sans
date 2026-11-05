# Coordinate-aligned MATH-aware saved-instance export

`export_math_instance.py` exports a fully pinned font through two real saved stages.
It aligns pinned coordinates with the immutable original source's HarfBuzz
normalization, then derives MATH values from that same source. This custom path
does not change generic fontTools instancing or certify a finished font family.

Use Python 3.12, fonttools 4.68.0 and uharfbuzz 0.57.0 with HarfBuzz 15.0.0. The
repacker and HarfBuzz version are checked before output creation. Exact rational
16.16/avar/F2Dot14 arithmetic supplies the source coordinates; native HarfBuzz
must agree before instancing. From the repository root:

```sh
uv run --no-project --python 3.12 \
  --with fonttools==4.68.0 --with uharfbuzz==0.57.0 \
  python fonts/torchlette-sans/export_math_instance.py \
  --source /path/to/untouched-full-variable.ttf \
  --source-sha256 ACTUAL_LOWERCASE_SHA256 \
  --wght 850 --ital 0 --order wght,ital \
  --out-dir /path/to/new-output
```

Both `wght,ital` and `ital,wght` are supported. Coordinates accept finite decimal
or rational text; range restrictions are not supported. Output must be a new
directory. External partial fonts and resumable receipts cannot replace the
original source.

## Supported source profile

The source must have axes `wght` (minimum/default/maximum 300/400/900) and `ital`
(0/0/1), version-1 avar, the exact reviewed weight mapping in `WEIGHT_MAP`, and
the italic map `(-1,-1), (0,0), (8191/16384,0), (1/2,1), (1,1)`. This serialized
profile has only five reachable normalized italic values for public 16.16 inputs:
`0, 1/4, 1/2, 3/4, 1`. Every source MATH record must preserve its complete style
branch at those values. The exporter follows the normalized branch rather than
assuming that nominal public `ital >= .5` selects italic.

MATH/GDEF variation data must be present. Record paths, coverage, namespaces and
counts are discovered from the source; no glyph IDs or record counts are fixed.
Unknown axes/maps/layout versions, changed remaining-axis ranges or maps, avar2,
VARC/CFF outlines, invalid variation references, unsupported ppem Device tables,
and an explicitly disabled repacker reject. This interface is not for arbitrary
variable-font profiles or other variation-store consumers needing custom repairs.

## Coordinate alignment and saved stages

FontTools' float normalization can disagree with the source's HarfBuzz coordinate.
For the reviewed source at weight 850, these values are 0.87493896484375 and 0.875,
respectively. This affects outlines, advances and layout together. The exporter
uses the original source coordinate for each pin, including after reopening the
saved partial; it does not patch individual glyphs or kerning pairs.

On a private in-memory copy, each pinned axis receives a temporary monotonic avar
map that makes the public fontTools instancer evaluate the requested user-space
pin at the verified source coordinate. Identity knots and normalized results are
checked. This temporary map is never serialized: the instancer must remove the
pinned axis/map, while surviving axis ranges and maps remain exactly unchanged.
User-space pins and their metadata retain the requested values.

For weight-first export, complete Roman/italic MATH values become `round(R)` plus
`round(I) - round(R)`. The coordinate-aligned partial is serialized and reopened
before capturing its preservation baseline, including compiled `loca` offsets.
Only MATH rows/regions are appended to GDEF; existing variation indices and store
prefixes remain intact. Italic-first uses the aligned first-stage result.

The actual saved partial is bound to the original source hash, partial hash,
first pin and order. The aligned second-stage target is also saved and reopened.
Final MATH values come from the original full source, avoiding independent
rounding of already rounded intermediate MATH values.

Plain MATH structures and record identities must remain equal. After weight-first
MATH repair, every non-MATH/GDEF raw table must match its aligned serialized
baseline. After final MATH repair, every non-MATH raw table, including GDEF and
GPOS, must match the aligned chained target. Only `head.checkSumAdjustment` is
excepted. These are preservation checks for the MATH repair stage; they do not
claim equality with ordinary float-normalized fontTools output. Coordinate
alignment deliberately can change non-MATH tables compared with that output.

The output directory contains:

- `aligned-partial.ttf`: serialized pre-MATH-repair weight partial, weight-first only;
- `partial.ttf` and `receipt.json`: actual first-stage bytes and their binding;
- `aligned-final.ttf`: aligned second-stage output from that partial;
- `final.ttf`: MATH-repaired final output;
- `proof.json`: source identity, pins/order, normalized traces, record count,
  hashes, tool versions and preservation checks against aligned baselines.

Source and partial hashes are rechecked at completion. Changed bytes, altered or
unbound receipts, wrong order, reused output paths and aliases reject. Failed
exports may retain diagnostic intermediates but do not produce a successful
proof. These hash checks are not locks against concurrent filesystem changes.

## Validation scope

The private reviewed integration passed five weight 850 readbacks: both sequential
finals, both partials evaluated at 850 upright, and the weight partial at 850 italic.
Each checked the existing 16025-case layout bank at the unchanged 1-unit per-field
bound, 1737 source MATH records, and native MATH consumers. Both finals were byte
identical. Source-relative outline and finite 16/19px native shaping controls were
also checked. These results cover the bound private candidate and source; they
are not a new full acceptance matrix for every future source or shared revision.
Historical generic-export fixture results do not automatically transfer to the
new coordinate convention.

The separate weight 650 combining-mark chain rounding failure remains unresolved:
FontTools and HarfBuzz already agree on its normalized coordinate 0.375, so this
alignment does not fix it. No mark-anchor correction or tolerance relaxation is
included. Full real-family, retained-axis, native-size and layout acceptance
still require a frozen source-bound integration gate. Validation receipts should
bind the actual driver and runtime implementation hashes before and after runs,
not only their version numbers.

Focused guards use a complete canonical source without constructing new fonts:

```sh
TORCHLETTE_TEST_VF=/path/to/untouched-full-variable.ttf \
  uv run --no-project --python 3.12 \
  --with fonttools==4.68.0 --with uharfbuzz==0.57.0 \
  python -m unittest discover -s fonts/torchlette-sans \
  -p test_math_export_alignment.py
```

Without `TORCHLETTE_TEST_VF`, these source-backed guards are explicitly skipped.

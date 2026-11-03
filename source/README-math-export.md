# MATH-aware saved-instance export

`export_math_instance.py` exports a fully pinned font through two real saved stages,
while deriving MATH values from the immutable original full variable font. This
is a supported custom export path; it does not change generic fontTools chains or
certify a finished font family.

Use Python 3.12, fonttools 4.68.0 and uharfbuzz 0.57.0. The pinned HarfBuzz repacker
is required for large layout tables and checked before output creation. HarfBuzz
is not the coordinate arithmetic oracle. From the repository root:

```sh
uv run --no-project --python 3.12 \
  --with fonttools==4.68.0 --with uharfbuzz==0.57.0 \
  python fonts/torchlette-sans/export_math_instance.py \
  --source /path/to/untouched-full-variable.ttf \
  --source-sha256 ACTUAL_LOWERCASE_SHA256 \
  --wght 425 --ital 32767/65536 --order wght,ital \
  --out-dir /path/to/new-output
```

Both `wght,ital` and `ital,wght` are supported. Coordinates accept finite decimal
or rational text. Output must be a new directory. No external partial font or
resumable receipt is accepted as a replacement for the original source.

## Supported source profile

The source must have axes `wght` (minimum/default/maximum 300/400/900) and `ital`
(0/0/1), version-1 avar, valid monotone weight mapping, and exactly the reviewed
italic map `(-1,-1), (0,0), (8191/16384,0), (1/2,1), (1,1)`. This exact serialized
profile has only five reachable normalized italic values for public 16.16 inputs:
`0, 1/4, 1/2, 3/4, 1`. Every source MATH record must preserve its complete style
branch at those values. The exporter follows the normalized branch, rather than
assuming that a nominal public `ital >= .5` chooses italic.

MATH/GDEF variation data must be present. Record paths, coverage, namespaces and
counts are discovered from the source; no glyph IDs or record counts are fixed.
Unknown axes, maps or layout table versions, invalid variation references, ppem
Device tables requiring composition, and an explicitly disabled repacker reject.
This interface is not for arbitrary variable-font profiles or other variation
store consumers needing custom repairs.

## Saved stages and preservation

Source coordinates use exact rational arithmetic with normative 16.16
normalization, serialized avar mapping and final F2Dot14 rounding. For weight-first
export, complete Roman and italic MATH values become `round(R)` plus the paired
style delta `round(I) - round(R)`. The ordinary partial is serialized and reopened
before capturing its preservation baseline: ordinary glyph compilation can
refresh `loca` offsets. Only MATH rows/regions are appended to GDEF; existing
variation indices and store prefixes remain intact. Ital-first uses the ordinary
first-stage instancer result.

The actual saved partial is reopened and bound to the original source hash,
partial hash, first pin and axis order. The ordinary second-stage target is also
saved and reopened. Final MATH values come from the original full source, avoiding
independent rounding of already rounded intermediate values.

Plain MATH structures and record identities must remain equal. After weight-first
partial repair, every non-MATH/GDEF raw table must match its ordinary serialized
baseline, including `loca`. After final repair, every non-MATH raw table, including
GDEF and GPOS, must match the actual ordinary chained target. Only
`head.checkSumAdjustment` is excepted. These checks do not repair unrelated
outlines, layout, hints or metadata.

The output directory contains:

- `ordinary-partial.ttf`: ordinary serialized weight partial, for weight-first only;
- `partial.ttf` and `receipt.json`: actual first-stage bytes and their binding;
- `ordinary-final.ttf`: ordinary second-stage output from that partial;
- `final.ttf`: MATH-repaired final output;
- `proof.json`: source identity, pins/order, normalized traces, record count,
  hashes, tool versions and preservation checks.

Source and partial hashes are rechecked at completion. Changed source/partial
bytes, altered or unbound receipts, wrong order and reused or aliasing output
paths reject. Failed exports may retain diagnostic intermediate artifacts but do
not produce a successful proof. These are hash-bound private outputs, not a lock
against hostile concurrent filesystem changes.

## Validation scope

Historical validation covered 700 small-fixture stages using real own-lane MATH
tables on harmless geometry. The current phase correction preserves all 14
weight-partial bytes and the numerical/completion functions; that matrix is
reused through explicit byte and function binding, rather than claimed as a new
700-stage run. A separate two-namespace, 1,223-record fixture supplied six newly
checked saved stages at weight 850 and italic 0, across both orders, with exact
frozen-file matches and native MATH checks. Generic instancer rounding failures
remain preserved; native advance fallbacks are distinguished from coverage-backed
MATH values. Existing guard and dependency controls also passed.

Final real-family, full/partial native-consumer and layout acceptance still require
a frozen source-bound integration gate. Matching ordinary non-MATH bytes does not
prove that generic instancer layout equals the original source; independent layout
checks retain their separate one-unit per-field bound.

# Coordinate-aligned MATH-aware saved-instance export

`source/export_math_instance.py` exports a fully pinned font through two actual saved stages. It aligns pins with the immutable full source's HarfBuzz normalization and derives MATH values from that source. It does not change generic fontTools instancing or certify family, layout or browser acceptance.

Use Python 3.12 (reviewed environment 3.12.10), fontTools 4.68.0 and uharfbuzz 0.57.0 with HarfBuzz 15.0.0. Package/repacker and HarfBuzz versions are checked before output creation. From this repository root:

```sh
uv run --no-project --python 3.12.10 \
  --with fonttools==4.68.0 --with uharfbuzz==0.57.0 \
  python source/export_math_instance.py \
  --source fonts/variable/TorchletteSansVariable.ttf \
  --source-sha256 0a4e6f9fa86dbdde41cc935441469681a930c5a591063d6497738cb5eecdf906 \
  --wght 850 --ital 0 --order wght,ital \
  --out-dir /path/to/new-output
```

The hash shown identifies the included full TTF, not its WOFF2. Both `wght,ital` and `ital,wght` orders are accepted. Coordinates accept finite decimal or rational text, not ranges. The output directory must be new. The API is `Exporter(raw_source_bytes, expected_sha256)`; both pins use the same exporter invocation/instance and its registered actual partial. External partials and saved receipt JSON are not a resumable replacement for the original source.

## Source profile and coordinate convention

The source must have `wght` minimum/default/maximum 300/400/900, `ital` 0/0/1, version-1 avar, the exact reviewed weight map in the code, and italic map `(-1,-1), (0,0), (8191/16384,0), (1/2,1), (1,1)`. The five reachable normalized italic states are 0, 1/4, 1/2, 3/4, 1. Every MATH record must retain its complete style branch at those states; selection follows normalized coordinates, not a nominal `ital >= .5` rule. MATH/GDEF variation data are required. Unsupported axes/maps/tables, variation references, remaining-axis changes, avar2, VARC/CFF outlines, ppem devices and a disabled repacker reject. Record paths and counts are discovered, not fixed glyph IDs.

Exact rational 16.16/avar/F2Dot14 arithmetic supplies source coordinates; native HarfBuzz must agree. Ordinary fontTools float normalization can differ: at reviewed weight 850 it gives 0.87493896484375 while the source coordinate is 0.875. Before each pin, a temporary in-memory avar map makes the instancer evaluate that verified source coordinate. The pinned map is removed; surviving axis ranges/maps stay unchanged. Alignment can therefore change outlines, advances and layout compared with ordinary float-normalized output. That ordinary output is not the preservation baseline.

## Saved stages and preservation

Weight-first MATH uses rounded Roman base values and italic variation deltas equal to round(Italic) minus round(Roman). Its aligned partial is serialized and reopened before baseline capture, including compiled loca offsets. MATH rows/regions are appended to GDEF while existing variation indices/store prefixes are preserved. Italic-first uses its aligned first stage. Completion reopens the actual hash-bound partial and saves/reopens the aligned chained target; final MATH values come from the untouched original full source.

Decoded plain MATH structures, coverage and record identities remain equal. After weight-partial MATH repair, all raw tables except MATH/GDEF match the aligned serialized baseline. After final MATH repair, every non-MATH table, including GDEF/GPOS, matches the aligned chained baseline. Only head.checkSumAdjustment is excepted. These are MATH-phase preservation checks; they neither assert equality with ordinary float output nor establish source-relative accuracy for unrelated tables.

Outputs are `aligned-partial.ttf` (weight-first only), `partial.ttf`, `receipt.json`, `aligned-final.ttf`, `final.ttf` and `proof.json`. The proof records source identity, pins/order, normalization, record counts, runtime versions and exporter hash and preservation checks. Source and partial hashes are rechecked; altered/unbound state, wrong order, aliases and reused output paths reject. Failed exports may retain diagnostics without a successful proof. Hash checks are not filesystem locks.

## Separate limitations and evidence

This standalone tool has no canonical mark-anchor correction or ON flag. Its weight 650 combining-mark rounding limitation remains: source and fontTools already agree at normalized 3/8, so coordinate alignment does not fix it. The separately proposed `source/canonical_export/` tool has its own explicit opt-in, policy, exact-source/native-runtime restrictions and proof contract; its ON evidence does not transfer to this default path. Consult that tool's adjacent README/POLICY if it is included.

Existing alignment checks are finite, source-bound evidence; no complete current gate pass is claimed here. Layout/native-MATH acceptance and browser acceptance remain separate. See [compatibility observations](../docs/COMPATIBILITY.md) and [historical build/browser evidence](../BUILD-v0.3.md); this guide does not relabel those measurements as aligned-core or optional-ON results. Full static masters are in `fonts/ttf`, including `fonts/ttf/TorchletteSans-BlackItalic.ttf`; `fonts/webfonts` contains subsets. Preserve original evidence epochs and bind actual code/runtime/source before and after any new validation.

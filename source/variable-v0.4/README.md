# Rebuilding the v0.4 variable companion

This package builds the v0.4 variable companion from fourteen verified static masters. `masters/` are the final outputs of Torchlette source commit `ac9da96c31dd1bcec98cb8ad1094dd9c11b90db4`. The `v03/` files are the v0.3 original masters and raw auxiliary geometry retained to reconstruct ten unchanged selected glyph outlines; `transplant.py` checks every selected original outline and metric against the v0.4 master before reuse. `augment-aux.py` constructs nine repeated-stroke glyphs from source components at each master's pitch. These auxiliary contours are build inputs, not substitutes for independent comparisons with the original static masters.

`variable.py` is based on source SHA-256 `4afaaf6a191b5883897da0d2034a8b4897f1e0976019ebaa0a412faeae357a8d`, patched to preserve inkless accent-spacing contours and to materialize recursively owned advances before removing USE_MY_METRICS. Non-identity metric-owner transforms are rejected rather than silently approximated. The raw overlapping components preserve correspondence as weights vary. Endpoint outline differences from Boolean-union rounding must be tested against the original statics.

The verified environment was Python 3.13.3 with fonttools 4.68.0, skia-pathops 0.9.2 and brotli 1.2.1. The independent verifier additionally used uharfbuzz 0.57.0, freetype-py 2.5.1 with native FreeType 2.14.1, numpy 2.3.4 and scipy 1.16.3. Check `freetype.version()` in the actual environment: the 2.13.2 bundled library raised raster overflow on the Bold static uniE934 at 160 ppem. `INPUTS.sha256` is a manifest of original package inputs and scripts; generated outputs and working files are excluded. Verify all listed hashes before running.

From this directory, in a pinned environment:

```sh
shasum -a 256 -c INPUTS.sha256
python transplant.py
python augment-aux.py
python variable.py --masters "$PWD/masters" \
  --auxiliary-manifest "$PWD/aux-all-components/geometry.json" \
  --auxiliary-sha256 d70249414fe63162a7a7db7ccde78b93cb6a3bf7b6e021d98a5ba839204270e4 \
  --output "$PWD/output/TorchletteSansVariable.ttf" \
  --woff2 "$PWD/output/TorchletteSansVariable.woff2" \
  --work-dir "$PWD/work" --report "$PWD/output/build-report.json"
```

Use a fresh work and output directory. The expected TTF SHA-256 is `7a2de49f520ecc17f716f7fdb3395f1eb893b84e900f9a6796ee8d11174218c7`; the expected WOFF2 SHA-256 is `e8119329d3b03787e58164e440fecaf49209678230753909f3082d51c13e3f95`. Relative manifest paths are independent of the checkout location. Auxiliary manifest hash changes if scripts or their hashed inputs change; never substitute a stale value.

```sh
python verify_variable.py --masters "$PWD/masters" \
  --font "$PWD/output/TorchletteSansVariable.ttf" \
  --woff2 "$PWD/output/TorchletteSansVariable.woff2" \
  --corpus "$PWD/corpus-bounded.json" --require-corpus \
  --report "$PWD/output/verification.json"
```

The reference run against the unaltered final masters reported no endpoint raster, shaping, MATH, or intermediate failures at 14 named styles and 12 intermediate locations; decoded WOFF2 table parity passed separately. `corpus-bounded.json` contains 16,112 historical/current harvested and manually transcribed inputs; it is not complete registered-module coverage for this source version. Endpoint tests resolve MATH records and do not certify saved-instance export or browser layout. The earlier v0.3 browser-MATH and saved-export compatibility evidence is tied to its original font and cannot be asserted for this new build without rerunning the relevant checks. Subjective native-size and math-rendering review remains separate.

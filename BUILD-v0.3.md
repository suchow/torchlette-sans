# Building the v0.3.0 variable fonts

Jordan authorized publication of v0.3.0. The finite explicit-ON saved-instance gate completed 560 stages with zero failures; the recorded scope and compatibility limits below continue to apply.

The variable TTF and WOFF2 were reproduced byte for byte from a relocated copy of this source tree. Separately, all five auxiliary source generators reproduced their 70 packaged font files, and the combiner reproduced all 14 combined auxiliary files. These results establish reproducibility in the recorded environment; they do not replace geometry, shaping, native MATH or browser acceptance tests.

## Environment

The tested full-build environment uses Python 3.12.10, fonttools 4.68.0, skia-pathops 0.9.2 and brotli 1.2.1. Auxiliary source construction additionally uses freetype-py 2.5.1 with the native FreeType 2.14.1 library. Installing the Python wrapper alone does not ensure that native library version. Check the library actually loaded before regenerating the component package:

```sh
python -c 'import freetype; print(freetype.version()); assert freetype.version() == (2, 14, 1)'
```

The source replay used an explicitly configured FreeType wrapper/library environment. Its exact runtime, library hash and configuration are recorded in `provenance/replays/source-runtime.json`; the library itself is not bundled. Paths in that historical receipt identify the test environment, not required build-directory names. The tested native library hash is platform-specific, rather than a claim that every FreeType 2.14.1 binary has identical bytes.

The builder is `source/variable.py`, SHA256 `4afaaf6a191b5883897da0d2034a8b4897f1e0976019ebaa0a412faeae357a8d`. Use a separate environment with the pinned dependencies and run the following commands from the repository root.

## Reproduce the variable files

```sh
python source/auxiliary-v03/prepare_manifest.py
python source/auxiliary-v03/verify_portable.py --report build/portable-intake.json
python source/variable.py --masters fonts/ttf \
  --auxiliary-manifest source/auxiliary-v03/combined/geometry.json \
  --auxiliary-sha256 "$(cat source/auxiliary-v03/combined/geometry.sha256)" \
  --output build/TorchletteSansVariable.ttf \
  --woff2 build/TorchletteSansVariable.woff2 \
  --work-dir build/variable-work --report build/variable-report.json
```

Use a fresh build directory. The first two commands prepare the manifest and validate existing inputs; the third builds the variable fonts. The relocated replay ran these commands once, exited successfully, and produced:

| File | SHA256 |
| --- | --- |
| `TorchletteSansVariable.ttf` | `0a4e6f9fa86dbdde41cc935441469681a930c5a591063d6497738cb5eecdf906` |
| `TorchletteSansVariable.woff2` | `b5a367f459ded2a99ba063cc3bab430f130e6da3fd10ebd1aa017270fadb2f20` |

These match the supplied `fonts/variable` files. All 273 packaged inputs were checked before and after the run without drift; all font and auxiliary dependencies recorded by the builder resolved within the relocated tree. The pinned Python environment remained an external runtime dependency. See `provenance/replays/portable-completion.json`, `portable-launch.json` and `portable-dependency-scope.json` for the result, command and input bindings.

`fonts/ttf` contains the 14 original full static masters. `fonts/webfonts` contains the approved static subsets, which are not build masters. This recipe does not regenerate or replace those statics.

## Auxiliary geometry and source reconstruction

Ten glyphs use raw auxiliary geometry to maintain corresponding contours across weights. Some constructions deliberately approximate source post-union polish or polygonal arcs. Reproducibility does not make those approximations exact copies of every static outline, nor prove continuous behavior between all tested axis locations.

The original masters remain authoritative for target metrics and layout. Selected auxiliary left bearings preserve each source package's coordinate frame: substituting original left bearings can shift contours during import. `verify_portable.py` checks 140 glyph/style combinations before and after rebasing, including coordinates, all flags, contour endpoints and bounds. It also checks unchanged nonselected glyph bytes and metrics, original advances, and preservation of target metrics during geometry import.

The `component`, `prec`, `galton`, `escape` and `hatch` packages contain their source generators, configurations and 70 frozen auxiliary fonts. Reconstruct the combined inputs from those packaged candidates with:

```sh
python source/auxiliary-v03/combine.py --out build/combined-replay
```

The output directory must not already exist. This command reproduced all 14 combined auxiliary fonts byte for byte and passed builder intake. It creates auxiliary fonts, not a variable font.

To regenerate each package directly from its construction source, use fresh output directories:

```sh
for package in component prec galton escape hatch; do
  python "source/auxiliary-v03/packages/$package/generate.py" \
    --repo . --masters fonts/ttf --out "build/$package-source-replay"
done
```

All five generators exited successfully. All 70 generated font files matched the packaged references byte for byte; the comparison also checked 140 selected glyph/style geometries, flags, endpoints, bounds and metrics. Generated JSON manifests/configurations differ because they record the actual output paths and adapted provenance; this is not a font-data difference. See `provenance/replays/source-completion.json` and `source-comparison.json`.

The combiner replay used the packaged candidates, and the full variable replay used the packaged combined inputs. Source-generator outputs were separately proven byte-identical to those candidates. This evidence chain is not described as a single uninterrupted constructor-to-variable build.

The portable adapters change source-directory lookup to `source/` and replace implicit Git HEAD lookup with `SOURCE-REVISION.txt`. `packages.json` records original and adapted generator hashes. Do not overwrite packaged candidates with new constructions without repeating the relevant checks.

## Provenance and scope

Active manifests use relative paths. The portable manifest hash is `466218477f5167482e20b6fbfa59eb275f4239c1e4c71bf685e9dce29d1f9909`; it differs from the historical manifest because paths and generator metadata changed. Historical generator/config/manifest/seal files remain under `source/auxiliary-v03/provenance`. Old paths there are evidence strings, not runtime dependencies. `SOURCE-REVISION.txt` identifies the reviewed builder and standalone base rather than inventing a Git commit.

The existing static Makefile still requires explicit `WEB_DIR`/`WEB_REF` overrides for this standalone layout. The variable recipe above does not invoke it. All ten license notices and the root OFL are retained.

The 119-page `specimen/torchlette-sans-v0.3-specimen.pdf` has SHA256 `ddbfe1fa7f17b782ce4942abe07eeefbb75562e91d95da5c628250358bb6ff38`. It presents 3,032 Regular designs, 76 table-qualified feature demonstrations and examples of all 14 static faces. It is not an exhaustive variable-axis proof. Rebuilding that PDF requires its separate generator, corpus and browser inputs; this document covers font reproduction.

## Tested Chromium 148 and Chrome 156 variable-MATH limitation

At `wght=900`, `ital=1`, two 20px native MathML fixtures produced the same measured variable-versus-static layout differences in both tested versions: Chromium 148.0.7778.96 and Chrome 156.0.8078.80. The results for each version were:

| Fixture | Variable TTF and WOFF2 | Supported saved static | Approved original static |
| --- | --- | --- | --- |
| Indexed nested roots | 47px | 54.296875px | 54.296875px |
| Nested fractions | 56.046875px | 60.359375px | 60.359375px |

The first companion browser run records Chromium **148.0.7778.96**. A separate Chrome run records **156.0.8078.80** in each of its eight saved result rows and reproduces all eight measured rectangles exactly. For Chromium 148, the isolated saved-font diagnostic uses the same Playwright installation as its companion run; that diagnostic records the fixtures and source hashes but omits its own version field. Chrome 156 records its version directly. Fonts were loaded before MathML insertion, each format had an isolated browser, and all recorded inputs remained unchanged. These are measured compatibility differences for these fixtures and coordinates in those two tested browser versions, not a general claim about all Chromium versions, every browser, equation or variable font. The earlier blank-arrow observation was retracted and is not a release condition.

Evidence is included under `provenance/browser-math/`: `saved-browser-result.json`, the fixture/harness files, screenshots, `export-900-1-proof.json` and checked bindings. The separately bound Chrome 156 result, harness and screenshots are under `provenance/browser-math/chrome156/`. The source variable fonts retain the exact hashes above. This disclosure does not waive the finding: browser-MATH acceptance remains on hold. The separate explicit-ON saved-export matrix has passed terminal evidence review; that result does not resolve this browser finding.

For a fixed coordinate requiring the tested static MATH behavior, use the approved static face or the supported saved-instance exporter, deriving values from the unchanged original variable source:

```sh
python source/export_math_instance.py \
  --source fonts/variable/TorchletteSansVariable.ttf \
  --source-sha256 0a4e6f9fa86dbdde41cc935441469681a930c5a591063d6497738cb5eecdf906 \
  --wght 900 --ital 1 --order wght,ital \
  --out-dir build/math-900-italic
```

The current standalone exporter requires Python 3.12, fonttools 4.68.0, uharfbuzz 0.57.0 and HarfBuzz 15.0.0. Use a new output directory and its `final.ttf`; see [the repository-relative exporter guide](source/README-math-export.md). It uses coordinate-aligned baselines and retains the known default weight-650 mark-chain limitation.

The saved output SHA `b78034cc5b3c6ca649a77dbd9a342fba8d08401840117bf481471c189e59a452` belongs to the historical browser test and its bound earlier exporter, not a new execution of the command above. That historical output matched the original static layout heights for both fixtures. Do not transfer those browser measurements to a new exporter or optional mode without binding the actual output.

Jordan authorized publication with these documented compatibility limits. The root README contains specimen images only; no proprietary professional-reference font assets are distributed.


## Optional canonical-source correction in v0.3.0

The exact tested four-file bundle is under `source/canonical_export/`. Read its
[usage, runtime acquisition and limitations](source/canonical_export/README.md)
before running it. Keep `export.py`, `erratum.py`, `core_exporter.py` and `POLICY.md`
together. The bundled core is byte-identical to the aligned standalone exporter;
the optional wrapper's proof/stdout schema differs, and it still reports its
legacy private-experiment status label.

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 source/canonical_export/export.py \
  --source fonts/variable/TorchletteSansVariable.ttf \
  --source-sha256 0a4e6f9fa86dbdde41cc935441469681a930c5a591063d6497738cb5eecdf906 \
  --wght 650 --ital 1 --order wght,ital --canonical-mm-erratum \
  --out-dir /path/to/new-output
```

This command assumes the verified environment; it is not an installation recipe.
The optional mode is tested only on the existing macOS arm64 host with the exact
HarfBuzz extension hash specified by its guide. The universal2 wheel does not
establish x86_64 execution, and Linux/Windows binaries do not satisfy the policy.
No runtime binary is redistributed here.

Removing the option selects default OFF, which does not fix the known 650
mark-chain error. The completed 560-stage, 1,797,040-layout gate and its terminal
evidence review apply to explicit ON and its exact source/runtime/corpus, not OFF.
The gate supplies finite evidence for this release; it does not establish
browser-MATH acceptance or an all-renderer/no-regression guarantee. Individual
native-size tradeoffs remain in the optional guide. The tested producer/core/policy
bytes retain their legacy private-experiment labels; publication authorization is
recorded here without rewriting those frozen files.

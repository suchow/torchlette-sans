# Optional canonical-font mark-position correction

Jordan authorized v0.3.0 publication after the finite explicit-ON 560-stage gate completed with zero failures. The four tested files retain their legacy private-experiment labels byte-for-byte; this guide records the release decision without changing their code or proof schema.

This optional exporter applies four curated mark-anchor adjustments to one exact Torchlette variable font at a particular normalized weight. It is separate from the default MATH-aware exporter. It is not a general rounding algorithm or a claim of improved accuracy for every string or display size.

Without `--canonical-mm-erratum`, the wrapper delegates to the unchanged core exporter. Default OFF does not correct the known weight-650 mark-chain discrepancy. Passing tests with the option ON does not establish that the default command passes those same cases.

## Required files and runtime

Keep these files together in one directory:

- `export.py`: command-line entry point.
- `erratum.py`: optional correction and receipt handling.
- `core_exporter.py`: the reviewed coordinate-aligned MATH exporter.
- `POLICY.md`: the versioned scope and correction data. The CLI reads this file even with the option OFF.

The reviewed versions are Python 3.12.10, fontTools 4.68.0, and uharfbuzz 0.57.0 containing HarfBuzz 15.0.0. ON additionally checks the SHA-256 of the actual loaded HarfBuzz extension:

```text
bb5f9abe6f722ff11df22fe9d462fff53dd08c017358ed547c8ea0413f2b7737
```

The inspected extension is a macOS Mach-O universal binary containing arm64 and x86_64 code. This identifies the tested binary; it does not establish successful execution on both architectures. Linux and Windows extensions cannot satisfy this exact binary requirement. A package with the same version number, including another wheel or a local build, may also fail the check.

Installing the version numbers alone does not select the exact tested binary. The following official wheel was downloaded and independently checked:

- Artifact: `uharfbuzz-0.57.0-cp311-abi3-macosx_10_9_universal2.whl`
- [Official wheel download](https://files.pythonhosted.org/packages/72/8e/334849c356e47c939e835c45f163e1ce51477f77a28efc872ee0b41353fb/uharfbuzz-0.57.0-cp311-abi3-macosx_10_9_universal2.whl)
- Archive SHA-256: `e3901acbed68995516ba272bb3ff3777adb07d832b328941da7915dd6cd145fd`
- Archive size: 3,610,563 bytes.

The ZIP passed its CRC checks, and all eight payloads hashed in its RECORD matched the tested installation byte-for-byte, including the extension hash above. Verify the archive hash before installing it into a separate environment. This archive hash is distinct from the extension hash.

A clean virtual environment on the existing macOS arm64 host installed this wheel and cached fontTools 4.68.0 offline with copy mode. All 362 installed Python/native implementation files matched the prior tested runtime. System and user site packages were disabled, and the export subprocess had no PYTHONPATH override. The environment used the existing CPython 3.12.10 interpreter; this was not a new operating system or independently provisioned interpreter.

This establishes acquisition and one installation on macOS arm64, not execution on x86_64, other macOS versions, Linux or Windows. The wheel tag describes packaging compatibility, not tested coverage. Do not bypass the binary check to make an unsupported installation run. A fresh-machine recipe still needs reproducible interpreter and fontTools artifact acquisition, followed by verification of actual loaded module origins and hashes.

The core must have SHA-256:

```text
25b836d0a9412ae6fd3e778782c8d35ad6b367872ff27ac7d3be7ad90f8ac061
```

Even a comment or line-ending change changes this hash. The optional policy accepts only the original complete variable TTF with SHA-256:

```text
0a4e6f9fa86dbdde41cc935441469681a930c5a591063d6497738cb5eecdf906
```

Renaming that file is fine. Repacking it, changing metadata, or using a different build may change its hash and cause rejection. A WOFF2 file is not a substitute for these TTF bytes.

## Usage in the verified environment

From the repository root, the following command assumes that the required files and exact runtime above are already installed and verified. It is not an installation command. Replace the paths with local paths; the output directory must not exist.

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 source/canonical_export/export.py \
  --source fonts/variable/TorchletteSansVariable.ttf \
  --source-sha256 0a4e6f9fa86dbdde41cc935441469681a930c5a591063d6497738cb5eecdf906 \
  --wght 650 --ital 1 --order wght,ital \
  --canonical-mm-erratum \
  --out-dir /path/to/new-output
```

Use `--order ital,wght` for the other sequential pin order. Both pins run in the same invocation, and completion consumes the actual saved partial and its bound receipt. External partials cannot be resumed through this interface. Removing `--canonical-mm-erratum` selects default OFF.

Applicability is determined by agreement between independent fixed-point normalization and the original font’s native HarfBuzz normalized weight: both must equal `3/8`. It is not a test that the input text is exactly `650`. For example, the reviewed `650.01` probe falls in the same effective cell. A disagreement at a rounding boundary rejects; an agreed coordinate outside the cell receives no optional adjustment. Exact source and runtime guards still apply whenever ON is requested.

For weight-first export, the correction is applied once to the saved partial; completion verifies the inherited values. For italic-first export, the weight-variable partial remains unchanged and the correction is deferred until weight is pinned. Retained italic lookup data is treated consistently even when the Roman branch is active.

`math-*` files preserve the pre-correction MATH-stage output. `partial.ttf`, `final.ttf`, `receipt.json`, and `proof.json` identify actual outputs and the optional GPOS phase. MATH-stage GPOS-preservation statements do not mean that the overall optional export leaves GPOS unchanged. The optional phase permits exactly four decoded X-coordinate changes while preserving other decoded GPOS data and other raw tables, except the required head checksum adjustment.

## Evidence and limits

A relocated CLI smoke using the exact copied source and four sibling files completed one weight-first export at `wght=650, ital=1` with ON and one with OFF. Both saved partials and finals matched their corresponding reviewed references byte-for-byte, and all 370 bound inputs and original source files remained unchanged. ON took about 28 seconds and OFF about 19 seconds on that run. This was a packaging smoke, not a performance guarantee, a fresh full-bank run, or an italic-first relocation test.

A separate direct-CLI smoke covered ON and default OFF in both pin orders at `wght=650, ital=1`, using a copied prospective package from an unrelated working directory and the existing pinned runtime. All four commands exited zero; all eight partial/final font files matched their reviewed API references byte-for-byte. This adds both-order CLI evidence, but it was not a second clean-environment installation or a new layout bank.

That smoke checked receipt, stdout and proof schemas, source/runtime inputs, actual saved-partial hashes, policy mode and phase events. ON weight-first applies once and then inherits; ON italic-first defers and applies at completion. OFF has no optional GPOS events. Separate checks confirmed six MATH-stage preservation pairs and the optional phase’s four logical X-coordinate changes, with other decoded GPOS data and raw tables preserved except the head checksum. Six negative CLI cases rejected wrong hashes, changed source, source/output aliasing, reused output, malformed coordinates and invalid order without a new successful certificate.

The optional CLI’s JSON/stdout schema differs from the legacy exporter. Its proof still says `private experiment, not adopted or complete gate`, even when the smoke succeeds. Consumers must not reinterpret that legacy label as a runtime support guarantee or assume legacy-schema compatibility. Publication is authorized separately; any future schema/status changes require separate review.

The historical scoped study completed eleven rows with 16,025 layout cases per row, the existing one-unit per-field layout bound, and the stated source/native MATH checks. This is historical, finite evidence. The subsequent fresh-corpus explicit-ON gate completed 560 stages with zero recorded failures, covering 1,797,040 layout evaluations. Its independent terminal evidence review checked declared coverage, bindings and persisted outputs; it was not an independent numerical rerun. Gate proof SHA-256 is `430edaabcab237979e60191c93291e1261e9e98a2ff635b5233eefc31716d18f`; terminal review SHA-256 is `e5d34844b56b58432a6a9dd73273ac2450c0b6de0a4e6ac9ecb129fa80ff5337`. This result applies only to the bound source, runtime, corpus and explicit ON policy. Publication is authorized separately; this result does not establish coverage for default OFF, additional platforms or arbitrary rendering.

The earlier four-anchor experiment exposed tradeoffs despite meeting its selected bounds. At 16px, four individual fields in two tested strings worsened from exact agreement to a `1/64`-pixel error. Individual isolated mark pairs also worsened, and one selected synthetic chain at 19px worsened from `2/64` to `3/64` pixel. A group maximum can improve while individual cases worsen. The later historical study did not repeat those display-size controls.

These observations do not establish accuracy for arbitrary strings, font sizes, renderers, browser MathML, operating systems, or future source fonts. They do not resolve the separately documented browser variable-MATH limitation. Keep the supported static-font/export guidance appropriate to the actual validated release.

The tested files retain their legacy private-experiment proof labels to preserve the validated bytes. v0.3.0 is authorized for publication with the exact-source/runtime and compatibility limits above. See [build and compatibility scope](../../BUILD-v0.3.md) and [compatibility notes](../../docs/COMPATIBILITY.md).

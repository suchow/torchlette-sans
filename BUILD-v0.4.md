# Torchlette Sans v0.4.0 build record

## Source and assets

The static source is Torchlette revision `ac9da96c31dd1bcec98cb8ad1094dd9c11b90db4`, path `fonts/torchlette-sans/`. The 87 tracked files from that path are in `source/`, with hashes in `provenance/v0.4/static-source-sha256.txt`. Other files retained under `source/` are historical v0.3 auxiliary material; they are not claimed as v0.4 static build inputs. Historical v0.3 provenance remains in `provenance/`; its source identity and compatibility record are preserved in `SOURCE-REVISION-v0.3.txt`, `docs/COMPATIBILITY-v0.3.md`, and standalone repository commit `aa4794dec1688494a5b9781cce901dbb337c23d7`.

The name-table version is `Version 1.000`; the distribution version is v0.4.0. The distribution contains fourteen static TTFs, fourteen web-subset WOFF2s, variable TTF and WOFF2, the specimen, licenses and compatibility record. `provenance/v0.4/staging-verification.txt` binds the assets to their source hashes. Static WOFF2 bytes were extracted from the source commit. The team reported that `make verify` passed all fourteen final static styles; that report has not been independently reproduced here or bound to a retained full static verification log. The source snapshot alone has not been demonstrated to be a portable clean static rebuild.

## Variable build and checks

`source/variable-v0.4/README.md` documents the portable variable build inputs, dependencies, commands, hashes, and scope. The input manifest validates in this checkout. The same-toolchain replay in a relocated copy produced the same TTF SHA-256 `7a2de49f520ecc17f716f7fdb3395f1eb893b84e900f9a6796ee8d11174218c7` as the distributed variable TTF. The relocated replay also produced the same WOFF2 SHA-256 `e8119329d3b03787e58164e440fecaf49209678230753909f3082d51c13e3f95`; the retained parity report finds no differences in decoded tables and head, excluding the WOFF2 transform flag.

`provenance/v0.4/variable/verify.json` records no failures for its tested endpoints and intermediate probes, with FreeType 2.14.1 at 160 pixels per em. Its 16,112-case registered corpus is partial, not exhaustive current-module coverage; finite geometric, raster and shaping tests cannot establish behavior for every input or renderer. The build, replay, and parity reports are retained beside it. The historical paths inside these reports identify the original execution environment; input hashes identify the retained artifacts.

## Browser mathematics

The retained Chrome 156 test compared variable TTF and WOFF2 with the Black Italic static TTF at weight 900, italic 1 and 20px. For indexed nested roots, the variable formats measured 50.047px high and the static 59.375px; for nested fractions they measured 56.047px and 60.359px. A saved instance at that coordinate matched the static in those two fixtures. This is limited to those fixtures and conditions; it is not browser or saved-export acceptance in general. See `docs/COMPATIBILITY.md` and `provenance/v0.4/browser-math/` for bindings, fixture definitions, screenshots, browser results, exporter proofs and receipts. Report paths name their original scratch locations; their copied artifacts and SHA-256 values are retained here.

## Specimen

The static specimen uses the frozen final static TTFs. Its coverage checker reported 826 passes, zero failures and no measured page overflow. The original text and font checker reported fourteen embedded Torchlette fonts and verified 47 excerpts against twelve sources. All 126 pages were rendered and examined as contact sheets; the new mathematics page was also examined at full render size. Its SHA-256 is `284ff0b3e6dfde43bf82394b8f20d4739fc12126d468e2516bdd2896414fe8b4`. These checks cover the PDF and its static inputs, not variable-font behavior.

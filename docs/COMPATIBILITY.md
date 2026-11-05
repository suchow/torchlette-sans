# Torchlette Sans v0.4.0 compatibility

## Variable font checks

The variable TTF tested for this release has SHA-256 `7a2de49f520ecc17f716f7fdb3395f1eb893b84e900f9a6796ee8d11174218c7`; the corresponding WOFF2 has SHA-256 `e8119329d3b03787e58164e440fecaf49209678230753909f3082d51c13e3f95`. Its axes are `wght` 300–900, default 400, and `ital` 0–1, default 0. A source-bound verifier reported no failures for the tested 14 static endpoints and intermediate weight probes in both styles. Raster checks used FreeType 2.14.1 at 160 pixels per em. The verifier's supplied corpus contained 16,112 cases, but it is a partial corpus, not an exhaustive representation of the current modules. These finite tests do not establish every intermediate shape, text, renderer, or platform.

## Native browser mathematics

Native MathML in Chrome 156.0.8078.81 displayed differences between the variable fonts and the included Black Italic static TTF in two tested equations at 20px, weight 900 and `ital` 1. The variable TTF and WOFF2 gave the same measurements:

| Fixture | Variable TTF / WOFF2 height | Black Italic static TTF height |
| --- | ---: | ---: |
| Indexed nested roots | 50.047px | 59.375px |
| Nested fractions | 56.047px | 60.359px |

For these fixed-style examples, the included static face avoids the observed variable-font difference. These measurements are limited to the two fixtures, browser version, size and axis settings tested; they do not establish behavior in other browsers or for arbitrary equations. Browser MathML acceptance of the variable fonts is not established by these checks.

## Saved-instance experiment

For the same two Chrome fixtures, a saved static instance made from the TTF above at `wght=900`, `ital=1`, with weight pinned before italic, measured 59.375px and 60.359px respectively, matching the original Black Italic static in this experiment. The saved TTF's SHA-256 was `8762b36ffe5e90fb56e70d2dcf5ab39748a37382d418563bf52d9a115ef29899`. This one-coordinate, two-fixture observation is not a general exporter, browser or all-string acceptance. The exporter proof covers coordinate-aligned two-stage MATH export and explicitly does not establish source-family or glyph acceptance.

## Scope of evidence

The verifier used fontTools 4.68.0, uharfbuzz 0.57.0, freetype-py 2.5.1, NumPy 2.3.4, SciPy 1.16.3 and skia-pathops 0.9.2. The browser measurement used loaded fonts in isolated browser sessions and retained the tested input hashes, fixture definitions, screenshots and results. Consult the release repository's accompanying build and provenance records for the exact artifacts, commands and reports. Earlier v0.3.0 browser measurements and saved-instance matrix apply to their own source and output hashes and are not evidence of v0.4.0 behavior.

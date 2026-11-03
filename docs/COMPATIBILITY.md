# v0.3.0 compatibility

Jordan authorized publication of v0.3.0 with the validated explicit-ON scope and compatibility limits below.

## Saved-instance checks

The source-bound MATH/layout matrix completed with the optional canonical mark-position correction explicitly ON: 140 locations, both sequential axis orders, and 560 saved-stage observations, with no reported failures. It retained the existing one-unit per-coordinate layout bound and exact glyph-name/cluster checks. The larger layout set ran at selected locations; other locations used five explicit layout contexts. MATH and native HarfBuzz MATH checks covered every location. This is finite saved-instance evidence, not browser MathML or arbitrary-string acceptance.

Earlier matrix failures remain part of the evidence history. Coordinate alignment addresses the identified weight-850 normalization discrepancy. It does not address the weight-650 combining-mark discrepancy; the optional correction addresses that case for the exact source and effective normalized-weight cell. The standalone exporter and the optional wrapper with its flag omitted remain OFF and retain that limitation. The ON result must not be attributed to either default path or to generic fontTools instancing.

The optional exporter requires the exact source TTF, reviewed core bytes and native HarfBuzz extension. The reviewed runtime is Python 3.12.10, fontTools 4.68.0, uharfbuzz 0.57.0 and HarfBuzz 15.0.0, executed on macOS arm64. Its native-extension SHA-256 is `bb5f9abe6f722ff11df22fe9d462fff53dd08c017358ed547c8ea0413f2b7737`. The universal macOS wheel includes x86_64 code, but execution there has not been established; Linux and Windows binaries do not satisfy this guard. Follow the source repository’s optional-export guide for exact acquisition, source identity, commands and proof semantics. Version numbers alone are insufficient.

The correction is curated rather than a general rounding algorithm. Earlier display-size controls found individual mark-position errors that worsened, including two tested strings at 16px and a selected synthetic chain at 19px. Passing the matrix does not establish that every string, size or renderer improves.

## Browser mathematics

The variable TTF and WOFF2 have a measured native MathML limitation in Chromium 148.0.7778.96 and Chrome 156.0.8078.80. Both versions produced the same measurements for the tested fixtures. At weight 900, italic 1 and 20px, indexed nested roots measured 47px high with either variable format, versus 54.296875px with the original static and the historical saved static. Nested fractions measured 56.046875px with the variables, versus 60.359375px with those statics.

For that fixed style, use the included `TorchletteSans-BlackItalic.ttf`. The historical saved-instance export also matched the static heights for these fixtures. That browser evidence belongs to its recorded exporter and output hashes; it is not a fresh browser test of the coordinate-aligned or optional-ON exporter. See the source repository’s build record and export guides for the historical evidence and current commands. Arbitrary generic partial-instancing chains are not covered.

These observations do not establish behavior in all Chromium versions, other browsers or every equation. The completed ON saved-instance matrix does not resolve this browser limitation or constitute browser-MATH acceptance. The earlier blank-arrow observation was retracted.

## Distribution

The v0.3.0 font archive contains 14 static TTFs, 14 static WOFF2 subsets, the variable TTF and WOFF2, a 119-page PDF, the root OFL and ten donor notices, plus this compatibility note. The separate source repository supplies reconstruction files, exporter instructions and evidence. No proprietary reference font assets are included.

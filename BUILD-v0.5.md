# Torchlette Sans v0.5.0

This release packages 14 static TTFs and matching full WOFF2 fonts, plus the variable TTF and WOFF2. The static TTF SHA-256 values match the r3 verification report in `provenance/v0.5/variable-verify-160.json`; the WOFF2 files were converted from those TTFs. The static build's `make verify` passed. The variable verification completed with one remaining intermediate-counter flag: ⋠ (U+22E0), weight 850 italic. It is not a clean verifier pass.

The release is built from an r3 working-tree font build, not a single committed source revision. The `source/` directory remains the previous release's source; it does not reproduce these v0.5 binaries. The updated source is to be committed separately. The variable-build and verification reports record the build inputs and limits.

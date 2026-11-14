# Changelog

## Unreleased

- The Vietnamese letters kern against Cyrillic as their base letters do, and accented letters kern against ⟨ and ⟩ no closer than their base letters.
- The accented a's keep clear of T, V, W, and Y in the heavy weights and the italics.
- mgrk turns Σ, Π, and Δ into the math symbols ∑, ∏, and ∆.
- Greek gets a grek script record with the same features as DFLT.
- The en and em quads (U+2000, U+2001), the three-, four-, and six-per-em spaces (U+2004 to U+2006), the medium mathematical space (U+205F), the zero width no-break space (U+FEFF), and the zero width non-joiner and joiner (U+200C, U+200D), at every weight, upright and italic.
- 111 glyphs that no character, feature, or MATH entry reached are no longer in the fonts: unused sizes of the stretchy arrows and of the wide hat, and the numerators 6, 8, and 9 that no fraction uses.
- make dist in source/ makes the release zip and its SHA256SUMS from the committed files, the same bytes on every run.

## v0.5.10 (2026-11-14)

Kerning for the twelve Vietnamese forms of a (ạ ả ấ ầ ẩ ẫ ậ ắ ằ ẳ ẵ ặ), as in Tạ, Vậ, and Yấ, at every weight, upright and italic.

## v0.5.9 (2026-11-13)

- The zip now holds the specimen PDF, TorchletteSans-v0.5.9-specimen.pdf, beside OFL.txt, so the release has one download instead of two.
- The fonts are those of v0.5.8 with the version set to 0.509; no glyph, metric, or feature changed.

## v0.5.8 (2026-11-12)

- locl for Romanian, Azerbaijani, Crimean Tatar, Kazakh, and Tatar: Romanian gets S and T with a comma below in place of the cedilla, and the four Turkic languages get the i that keeps its dot, as in Turkish.
- Every glyph but .notdef has a GDEF glyph class, among them the 313 glyphs Mulish left unclassed.
- frac changes only the digits on either side of a slash, so a lone 7, the 7 of "7 1/2", and the slash of "and/or" stay as they are.
- Г Ѓ Ґ Ғ and У Ў Ӯ Ӱ Ӳ kern against punctuation as T and Y do.
- dlig turns on the Th and th ligatures, which ss01 and ss03 already had.
- make release and make check in source/ rebuild the release and compare it with fonts/, and the web fonts now come out the same byte for byte on every build.

## v0.5.7 (2026-11-11)

The leftwards arrow with tip upwards (⬑, U+2B11), at every weight, upright and italic.

## v0.5.6 (2026-11-10)

Circle arrows with centred heads, and more room around the old-style multiplication sign.

## v0.5.4 (2026-11-06)

Cleaner heavy vector marks, version numbers inside the fonts, and a PDF specimen.

## v0.5.3 (2026-11-06)

Ten random forms of the vector word mark.

## v0.5.2 (2026-11-06)

Thicker e crossbar in the heavier weights.

## v0.5.1 (2026-11-06)

Fixes ⋠ in heavier italics.

## v0.5.0 (2026-11-05)

Math: display integrals, negated relations, big operators, stretchy arrows, larger brackets and braces, and gapless radicals. Slashed lone zeros and a gradients ligature.

## v0.4.0 (2026-11-05)

Torchlette Sans v0.4.0 adds expanded mathematical typesetting, including display operators, radicals, stretchy delimiters, accents, primes and additional symbols, alongside apostrophe kerning and a refreshed specimen.

## v0.3.0 (2026-11-03)

[Download the 119-page specimen PDF](https://github.com/suchow/torchlette-sans/releases/download/v0.3.0/torchlette-sans-v0.3-specimen.pdf)

Torchlette Sans v0.3.0 includes 14 static faces, their WOFF2 web subsets, variable TTF and WOFF2 fonts, and a revised 119-page specimen PDF.

## v0.2.0 (2026-11-03)

No notes were published with this release.

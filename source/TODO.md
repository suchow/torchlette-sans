# Torchlette Sans: remaining work

From the measured audit of 2026-11-01 (`font-preview/feature-audit-2.html`, 89 have, 13 partial,
24 missing of 141) plus open items. Each line names its owner. Rules for every item:

- Work in a module (`modules/<name>.py` + `verify_<name>.py`) or an isolated copy; build into your
  own scratch `BUILD_DIR`, never the shared `build/` folder.
- Do not write `web/public/fonts`; Claude integrates and rebuilds the family once.
- Glyph work is gated visually: a specimen on white in ink `#33241b`, read glyph by glyph at full
  resolution beside a professional reference, before it is shown to Jordan.
- Uprights and italics both: every item must work in all fourteen styles.

| # | Item | Owner |
|---|---|---|
| 1 | Ship Greek: enable the Commissioner-based `greek` module (drop `MODULES_OFF`), check it in italic: ready in all fourteen styles (dialytika-tonos fixed); MODULES_OFF dropped at item 12 | Claude |
| 2 | Double-struck ℝ ℕ ℤ ℚ ℂ redrawn properly (in progress) | Claude |
| 3 | ML math letters: ℙ ℍ ℒ ℏ ∥ ∖ ⟂ ⟦ ⟧ ⋆, plus 𝔼 𝟙 (needs a format-12 cmap): done, `modules/mathletters.py` | Claude |
| 4 | `lnum` feature (lining figures override `onum`): done, module committed; ships in the item-12 rebuild | Claude |
| 5 | Font checks in CI (`make verify`, FontBakery gate): done, `fonts` job in `ci.yml` | Claude |
| 6 | UI symbols: ✓ ✗ ■ □ ▶ ● ○ ★, circled ①–⑳, keyboard ⌘ ⌥ ⇧ ⏎ ⌫: done, `modules/ui.py` | Claude |
| 7 | OpenType MATH table for MathML Core | Gemini |
| 8 | Cyrillic small caps and Cyrillic in the web subset: done (`08fe93e`); web subset gets U+0400-04FF at item 12 (+17 KiB per style) | Gemini |
| 9 | Latin gaps: ĳ, Pinyin ǎ ǐ ǒ ǔ ǖ ǘ ǚ ǜ, ⅓ ⅔ ⅛ …, `afrc`, remaining case-mapping partners | Gemini |
| 10 | Variable font (wght + ital) alongside the statics: tooling done (`328451b`: variable.py, verify_variable.py, README-variable.md; baseline gate passes, builds reproduce byte for byte); final run on the integrated fourteen masters (Greek, MATH, new modules) with the same gate is part of item 12: Claude builds the fourteen statics and runs `variable.py` + `verify_variable.py --require-corpus` (exact command in Codex 2026-11-02 04:33 UTC chat message); Codex refreshes the input corpus for the new repertoire and runs the saved MATH instance checks | Codex |
| 11 | Hinting proof on Windows-style rasterization (FreeType v35/ClearType-like renders): tooling done (`5b8ce7d`, `README-hinting-proof.md`); rerun on the item-12 build | Codex |
| 12 | Final integration: rebuild all fourteen, verify, fontbakery, woff2, chat copy, GitHub repo; widen the web subset `UNICODES` to carry the new ranges (U+2460-2473, U+2600-26FF as used, U+2A00-2AFF, U+1D400-1D7FF as used, plus Gemini's Cyrillic and fractions) and drop `MODULES_OFF`; with greek + latin_gaps on, FontBakery has zero FAILs, which crashes fontbakery 1.1.0's `--ghmarkdown` reporter (it also crashes at WARN on PASS-only reports, per Codex): drop `--ghmarkdown` from the analysis run, write the human summary from the validated JSON, keep JSON completeness + exit-status agreement in the gate, and drop `case_mapping` from `fontbakery_gate.py` ALLOWED | Claude |
| 12a | Integration feature policy: decide and document, per new tag (ss17-ss20, ornm, cvNN additions), whether it ships in the web subset (`web_features.txt`) or only in the full fonts, and add a positive check that every promised web feature is present in the subset (subset verifiers skip omitted tags, so a pass there proves nothing) | Claude |
| 13 | Specimen book (PDF), added to github.com/suchow/torchlette-sans and linked from its README (Jordan, 2026-11-01): existing public-domain texts in CS, AI, ML, cognitive science, philosophy and math only, showing every major feature and what makes the face distinctive; no comparisons with other fonts; built from the item-12 fonts (Jordan, 2026-11-01); final pass adds the new modules' pages, the fleurons, and small caps in all seven weights on page 12 | Claude |
| 14 | Fleurons (round 2 traced from MIT/Apache/OFL designs, Jordan 2026-11-01): ML / technology / math / cognitive-science ornaments in the font's stroke language; candidate page for Jordan's pick, then encoded (PUA + `ornm`) and used in the specimen book (Jordan, 2026-11-01) Round 2 review page up (`font-preview/fleurons-review.html`); round 3 page (`font-preview/fleurons-round3.html`, 2026-11-02) adds the Lissajous family `U+E940-E94B` and the Tower of Hanoi family `U+E950-E96A`; at integration add `U+E900-E925` (+ `U+E930-E938` for kept drafts, + `U+E940-E96A` for kept families), `U+2619 U+261C U+261E U+2766 U+2767` to UNICODES, `ornm` to web_features.txt if used, and the full upstream notice files (see `font-preview/fleurons-round3/licenses/`; Lucide is no longer used) to the full, web and variable distributions and the repository notices | Claude |
| 15 | Repertoire, math notation (ML1 ML3 ML4 ML5 ML7 ML8 ML9 ML10 LG5 SH4 SH5), `modules/mathnotation.py` (Jordan: build all repertoire items, 2026-11-01): built, review page up; full default build with every module passes; at integration add `U+2AAF-2AB0,U+2AEB,U+1D49C-1D4B5,U+1D538-1D550,U+1D7D8-1D7E1` (or the planned U+2A00-2AFF, U+1D400-1D7FF) | Claude |
| 16 | Repertoire, code and keyboard (CP1 CP2 CP3 SH1 SH2 SC1 SC3 ML6 LG4 LG6), `modules/codekeys.py`: built, review page up; at integration add `U+2423,U+2581-2588,U+2669-266F` to UNICODES and the chosen CP1 set (ss17/18/19) to web_features.txt and app CSS | Claude |
| 17 | Repertoire, Penrose tensor-diagram glyphs (SH3), `modules/tensordiagram.py`: built, review page up; at integration add `U+EE00-EE07` to UNICODES and `ss20` to web_features.txt if the app should honour the ASCII triggers | Claude |
| 18 | Repertoire, logic and games (LG1 LG2 LG3 GM1-4 CP4 CP5 SC2 SC4) | Gemini |
| 19 | Circled numbers ①–⑳: rebalance figure vs ring weight; Jordan picked B (ring 0.8 of stem): done (`a76a172`) | Claude |
| 20 | Every approval request is a review page built on `font-preview/review-kit.js` (votes, notes, copy feedback) (Jordan, 2026-11-01) | all |
| 21 | Harpoons ⇌ ⇋ joined, single harpoons and ⇅ ⇵ added, heavy ⇄ ⇆ ↻ ↺ fixed: done (`36315ba`), approved by Jordan | Claude |

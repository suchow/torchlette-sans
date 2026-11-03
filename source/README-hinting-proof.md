# FreeType hinting proof

`hinting-proof.py` produces native-size white specimens in ink `#33241b`, a JSON
bytecode/rasterization inventory, and an HTML gallery for all fourteen static faces.
It writes only to a new output directory. It copies and hashes its inputs before
rendering and rejects source drift. Run against one frozen source epoch, never a
mixture of the shared build directory and newer web fonts.

This is a **FreeType simulation**, not a Windows, DirectWrite, or native ClearType
capture. Interpreter 35 is the classic TrueType interpreter; it is not the newer
interpreter 40 approximation of DirectWrite behavior. The LCD column uses RGB
subpixel coverage and FreeType's default five-tap filter. The renderer requires
successful interpreter-property set/readback and LCD-filter installation; an
unsupported filter is an error, not permission to relabel Harmony rendering.
See FreeType's [interpreter properties](https://freetype.org/freetype2/docs/reference/ft2-properties.html)
and [LCD rendering API](https://freetype.org/freetype2/docs/reference/ft2-lcd_rendering.html).

## Reproduce

Freeze the desired commit in a temporary directory with `git archive`, then run
`make ttf BUILD_DIR=/absolute/scratch/full` from that snapshot's
`fonts/torchlette-sans` directory. This builds all fourteen faces without changing
shipped fonts. Use the snapshot's `web/public/fonts` and original `mulish` sources.
Keep the normal build log and the commit identity alongside the proof.

Use a FreeType library compiled with `FT_CONFIG_OPTION_SUBPIXEL_RENDERING` enabled.
For the recorded proof, the source is official FreeType 2.14.1. Unpack that
release into scratch, enable that define
in `include/freetype/config/ftoption.h`, then run `./configure --prefix=...`, `make`
and `make install` **inside its source directory**. On macOS, set `SDKROOT` to
the installed macOS SDK and use an explicit compiler/toolchain path if the system
compiler wrapper stalls or cannot find libSystem. Preserve the downloaded archive
hash, edited configuration, configure/build logs and installed library. The
library path is explicit; the bundled freetype-py library is not used for face
creation, glyph loading, or rendering. freetype-py supplies ctypes structures and
constants only. This avoids mixing objects from two FreeType libraries.

```sh
uv run --no-project --python 3.12 \
  --with freetype-py==2.5.1 --with fonttools==4.68.0 \
  --with uharfbuzz==0.57.0 --with pillow==12.0.0 --with brotli==1.2.1 \
  python fonts/torchlette-sans/hinting-proof.py \
  --source-commit FULL_COMMIT_SHA \
  --full-dir /absolute/scratch/full \
  --web-dir /absolute/snapshot/web/public/fonts \
  --reference-dir /absolute/snapshot/fonts/torchlette-sans/mulish \
  --freetype-library /absolute/scratch/ft-install/lib/libfreetype.dylib \
  --out /absolute/scratch/new-proof
```

The default sizes are 12, 14, 16, 18, 20 and 24 physical pixels, at device scale
one. Every face compares full-font hinting on/off, app-subset hinting on/off, and
original Mulish at the same donor design-weight coordinate and slant. These
references use actual original outlines, not synthetic weight or oblique styles.
No x-height normalization or image resampling is applied. Horizontal scrolling
in the gallery preserves pixels; inspect the original PNG, not a scaled thumbnail.

HarfBuzz supplies glyph selection, kerning and positioning adjustments. Each mode
uses FreeType's actual advance for each selected glyph. Fractional advances
accumulate, but glyph origins are rounded to integer canvas pixels; this is not
DirectWrite fractional positioning. The features are recorded
in the proof: `kern`, `liga`, `ss16`, `onum`, `pnum`. Pedantic TrueType loading is enabled to surface instruction errors. Autohinting and bitmap strikes
are disabled so full-font native TrueType instructions are tested. Web WOFF2s are
copied byte-exact, then decompressed to scratch SFNTs for rendering. They are
expected to have no hint tables or glyph instructions; this intentional production
subset policy is not silently converted into a claim that web fonts are hinted.
Even without glyph instructions, FreeType can round advances differently with
`NO_HINTING`; a web on/off layout difference is not evidence of hidden bytecode.

## Interpret evidence

The proof records each font's hash, version, UPEM, glyph/cmap counts, `fpgm`, `prep`,
`cvt `, glyph instruction counts, `maxp` limits and `gasp` ranges. Raster records
include actual glyph IDs, advances, bitmap dimensions and bearings, plus aligned
on/off changed-pixel counts. Gray and LCD modes are separate: LCD buffers contain
three coverage samples per output pixel. RGB compositing uses the returned byte
coverage directly against white; Windows gamma, contrast, RGB/BGR device layout
and display scaling are not reproduced.

Successful rasterization and nonzero differences establish execution evidence,
not visual quality or universal bytecode validity. Review all fourteen native-size
sheets glyph by glyph beside Mulish, especially I/l/1, counters, stems, curves,
accents, italics and the numeral 2. Record concrete defects separately from aesthetic
preferences. A missing glyph, clipping or FreeType error aborts the run. Preserve
failed unsupported-library probes as diagnostics. No output here constitutes
production approval or a native-Windows compatibility certification.

To check determinism, rerun with the same frozen inputs/library into another new
directory and compare all fourteen PNG hashes and per-style diagnostic records;
source paths and platform metadata may differ. A later integration epoch needs a
new proof and must not inherit this epoch's source identity.

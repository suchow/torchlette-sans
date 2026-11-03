# Torchlette Sans

## v0.2.0

Seven weights, Light through Black, each with a genuine italic: 14 static styles. This release adds Greek, mathematical italic Latin and Greek, OpenType MATH, logic and technical symbols, Fraktur, fractions, keyboard forms, tensor diagrams and fleurons. The 29 script characters use Noto Sans Math-derived forms.

Full fonts are in [fonts/ttf](fonts/ttf). The smaller [web fonts](fonts/webfonts) retain the selected repertoire and features listed in [source/web_features.txt](source/web_features.txt); they are not substitutes for every optional feature in the full fonts. Variable-font work is separate.

Licensed under the [SIL Open Font License 1.1](OFL.txt), with derivation and upstream notices in [licenses](licenses) (10 notice files). Build sources and vendored inputs are in [source](source).

### Build

With `uv` and `make` installed, from this repository:

```sh
make -C source ttf
make -C source WEB_DIR=../fonts/webfonts
```

Full TTF output is written to `source/build`. The explicit `WEB_DIR` keeps web output inside this repository. Tools are version-pinned in the Makefile. `make -C source verify WEB_DIR=../fonts/webfonts` runs font checks; its optional lesson-prose check additionally requires the Torchlette lesson corpus, which is not bundled here. Without it, that corpus check is skipped. See [source/README.md](source/README.md) for the pipeline and feature details.

### Historical specimen images

These six images predate the November 2 integration and show the earlier font. They are retained as historical samples, not proof of the current repertoire or shapes. The old specimen PDF is omitted; an updated book is separate work.

![Earlier alphabet and figures](specimen/hero-light.png)
![Earlier size waterfall](specimen/sizes-light.png)
![Earlier seven-weight sample](specimen/weights-light.png)
![Earlier prose, figures and small capitals](specimen/text-light.png)
![Earlier technical features](specimen/features-light.png)
![Earlier prose ligatures](specimen/ligatures-light.png)

# Torchlette Sans: build from Mulish and Mulish Italic and write the web fonts.
#
#   make          build/TorchletteSans-<style>.ttf for each of STYLES (seven weights, upright and italic) and their subset woff2 in web/public/fonts/
#   make ttf      the .ttf only (no woff2 written)
#   make verify   HarfBuzz feature check (verify.py, verify_ss16.py, modules/verify_*.py) of each built font and of its web subset, and make fontbakery
#   make fontbakery  fontbakery check-universal on every built .ttf; fails on an error, an incomplete report or a FAIL outside fontbakery_gate.py's ALLOWED
#   make check    clean rebuild of every style, compared with the committed woff2 files byte for byte
#   make clean
#
# Variables (see modules/README.md):
#   MODULES=a,b | none   build with only these modules/*.py (default: all of them but MODULES_OFF)
#   BUILD_DIR=dir        where the .ttf, the Mulish instances and the check files go (default: build)
#   WEB_DIR=dir          where `make` writes the woff2 (default: the committed ../../web/public/fonts)
#
# Tool versions are pinned so that a rebuild is byte-identical.

.DEFAULT_GOAL := all

PY     := uv run -q --no-project --python 3.12 --with fonttools==4.68.0 --with skia-pathops==0.9.2 --with brotli==1.2.1 --with ttfautohint-py==0.6.1 python
PYHB   := uv run -q --no-project --python 3.12 --with fonttools==4.68.0 --with uharfbuzz==0.57.0 --with skia-pathops==0.9.2 python
SUBSET := uv run -q --no-project --python 3.12 --with fonttools==4.68.0 --with brotli==1.2.1 pyftsubset
FB     := uv run -q --no-project --python 3.12 --with fontbakery==1.1.0 fontbakery

# The variable sources, upright and italic. Make reads the brackets in their names as
# a glob, so recipes quote VF and VFI and prerequisites name the vendored fonts through
# a wildcard.
VF     := mulish/Mulish[wght].ttf
VFI    := mulish/Mulish-Italic[wght].ttf
VF_DEP := $(wildcard mulish/*.ttf)
# the greek module's source fonts (see README, "Greek sources")
REF_DEP := $(wildcard commissioner/*.ttf notosans/*.ttf notosansmath/*.ttf notosansmath/OFL.txt)
NORMAL_HELPER_DEPS := $(sort $(wildcard modules/_*.py mathitalic_references.py))

BUILD_DIR := build
WEB_REF   := ../../web/public/fonts
WEB_DIR   := $(WEB_REF)

# Modules: every modules/*.py but verify_*.py and _*.py, in sorted order, less
# MODULES_OFF; MODULES picks a subset (a comma list, or none) and may name a module
# that MODULES_OFF holds back. Each built font records the selection in
# $(BUILD_DIR)/modules.txt, which changes only when the selection does.
# Greek and mathitalic are explicitly included in the approved release default.
MODULES_OFF  :=
# Approved release default: the exact 22 modules exercised in the combined gate.
MODULES_DEFAULT := codekeys cyrillic fleurons fraktur games graphnodes greek kern latin_gaps lnum logic math_table mathitalic mathletters mathnotation meta otfeatures sigmoid supsub symbols tensordiagram ui
comma        := ,
empty        :=
space        := $(empty) $(empty)
rparen       := )
MODULE_FILES := $(sort $(filter-out modules/verify_%.py modules/_%.py,$(wildcard modules/*.py)))
ifeq ($(strip $(MODULES)),none)
MODULES_ON :=
else ifeq ($(strip $(MODULES)),)
MODULES_ON := $(filter-out $(MODULES_OFF),$(MODULES_DEFAULT))
else
MODULES_ON := $(sort $(subst $(comma), ,$(MODULES)))
endif
MODULE_STAMP := $(BUILD_DIR)/modules.txt
# what build.py gets: the selection itself, so MODULES_OFF reaches it too
MODULES_ARG  := $(if $(MODULES_ON),$(subst $(space),$(comma),$(strip $(MODULES_ON))),none)

# The styles and the Mulish wght each is built from: stems 66, 92 and 119 units,
# 1.39 and 1.80 times Regular's (see README); Light, Medium, ExtraBold and Black
# continue the progression at stems 50, 79, 141 and 163. Each weight has an italic,
# built from Mulish Italic at the same wght (build.py unslants it, draws, and reslants).
UPRIGHTS       := Light Regular Medium SemiBold Bold ExtraBold Black
ITALICS        := LightItalic Italic MediumItalic SemiBoldItalic BoldItalic ExtraBoldItalic BlackItalic
STYLES         := $(UPRIGHTS) $(ITALICS)
WGHT_Light     := 242
WGHT_Regular   := 324
WGHT_Medium    := 388
WGHT_SemiBold  := 510
WGHT_Bold      := 675
WGHT_ExtraBold := 762
WGHT_Black     := 845
WGHT_LightItalic     := $(WGHT_Light)
WGHT_Italic          := $(WGHT_Regular)
WGHT_MediumItalic    := $(WGHT_Medium)
WGHT_SemiBoldItalic  := $(WGHT_SemiBold)
WGHT_BoldItalic      := $(WGHT_Bold)
WGHT_ExtraBoldItalic := $(WGHT_ExtraBold)
WGHT_BlackItalic     := $(WGHT_Black)
# the static instance a style starts from: Mulish-<wght>.ttf, or MulishItalic-<wght>.ttf
STATIC = $(BUILD_DIR)/Mulish$(if $(findstring Italic,$(1)),Italic,)-$(WGHT_$(1)).ttf
TTFS   := $(foreach s,$(STYLES),$(BUILD_DIR)/TorchletteSans-$(s).ttf)
WEBS   := $(foreach s,$(STYLES),$(WEB_DIR)/TorchletteSans-$(s).woff2)

# What the app needs: Latin, Latin-1, Latin Extended A, B and Additional, IPA and
# spacing modifiers, combining marks, general punctuation, super- and subscripts,
# currency, letterlike symbols, arrows, mathematical operators, geometric shapes,
# the angle brackets and the fi/fl ligatures; the modules' phonetic modifier
# letters, Latin Extended-C's subscript j and modifier V, miscellaneous technical
# symbols and the supplemental arrows; the ui module's ★ ✓ ✗ (U+2605, U+2713,
# U+2717), which the app's interface shows. Exact additions from the selected
# module contracts follow below; existing ranges and math-italic inputs remain.
UNICODES := U+0000-00FF,U+0100-024F,U+0250-02FF,U+0300-036F,U+0370-03FF,U+1E00-1EFF,U+2000-206F,U+2070-209F,U+20A0-20CF,U+2100-214F,U+2190-21FF,U+2200-22FF,U+25A0-25FF,U+27C0-27EF,U+FB00-FB06,U+1D2C-1D6A,U+1D9C-1DBF,U+2C7C-2C7D,U+2300-23FF,U+27F0-27FF,U+2900-297F,U+2605,U+2713,U+2717,U+1D434-1D467,U+1D6A4-1D6A5,U+1D6E2-1D71B

# Exact encoded contracts of the selected modules; no inferred whole blocks.
# mathnotation: 18 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+1D49C,U+1D49E-1D49F,U+1D4A2,U+1D4A5-1D4A6,U+1D4A9-1D4AC,U+1D4AE-1D4B5
# fraktur: 47 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+1D504-1D505,U+1D507-1D50A,U+1D50D-1D514,U+1D516-1D51C,U+1D51E-1D537
# symbols+mathletters+mathnotation: 29 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+1D538-1D539,U+1D53B-1D53E,U+1D540-1D544,U+1D546,U+1D54A-1D550,U+1D7D8-1D7E1
# cyrillic: 236 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+0400-045F,U+0462-0463,U+046A-046B,U+0472-0475,U+048A-04A5,U+04A8-04FF,U+0510-0513,U+051A-051D,U+0524-0529,U+052E-052F
# latin_gaps: 17 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+2150-215F,U+2189
# mathnotation: 3 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+2AAF-2AB0,U+2AEB
# logic: 1 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+2621
# codekeys: 15 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+2423,U+2581-2588,U+2669-266B,U+266D-266F
# games: 29 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+2609,U+263D,U+2641,U+2654-265F,U+2680-2689,U+26C0-26C3
# ui: 20 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+2460-2473
# tensordiagram: 8 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+EE00-EE07
# fleurons: 33 additional encoded characters from the selected source contract.
UNICODES := $(UNICODES),U+2619,U+261C,U+261E,U+2766-2767,U+E900-E915,U+E920-E925

# The web subset keeps only the features in web_features.txt (what browsers apply by
# default and what the app turns on); the .ttf keeps them all.
WEB_FEATURES := $(shell grep -v '^\#' web_features.txt | paste -sd, -)

.SECONDEXPANSION:
# Math italic uses matched, source-bound references in this release. The
# reference fonts are explicit ordinary Make prerequisites, never module recursion.
MATHITALIC_ON := $(filter mathitalic,$(MODULES_ON))
MATHITALIC_ENV :=
ifneq ($(MATHITALIC_ON),)
ifneq ($(MAKECMDGOALS),clean)
ifeq ($(filter greek,$(MODULES_ON)),)
$(error mathitalic requires an explicit Greek selection; default Greek policy is unchanged)
endif
MATHITALIC_REF_MODULES := $(filter-out mathitalic,$(MODULES_ON))
MATHITALIC_REF_ARG := $(subst $(space),$(comma),$(strip $(MATHITALIC_REF_MODULES)))
MATHITALIC_INPUTS := $(BUILD_DIR)/mathitalic-reference-inputs.json
MATHITALIC_EPOCH := $(shell $(PY) mathitalic_references.py epoch --root . --modules '$(MATHITALIC_REF_ARG)' --record '$(MATHITALIC_INPUTS)')
ifeq ($(strip $(MATHITALIC_EPOCH)),)
$(error unable to bind mathitalic reference source/config/tool epoch)
endif
mathitalic_style = $(if $(filter Regular Italic,$(1)),Italic,$(if $(filter %Italic,$(1)),$(1),$(1)Italic))
MATHITALIC_REF_STYLES := $(sort $(foreach s,$(STYLES),$(call mathitalic_style,$(s))))
MATHITALIC_REF_DIR := $(BUILD_DIR)/mathitalic-references/$(MATHITALIC_EPOCH)
MATHITALIC_REFS := $(foreach s,$(MATHITALIC_REF_STYLES),$(MATHITALIC_REF_DIR)/TorchletteSans-$(s).ttf)
MATHITALIC_MANIFEST := $(MATHITALIC_REF_DIR)/references.json
# Retain reference-only donor instances: reuse receipts also bind their bytes.
.SECONDARY: $(foreach s,$(MATHITALIC_REF_STYLES),$(call STATIC,$(s)))
MATHITALIC_ENV := MATHITALIC_REFERENCE_MANIFEST='$(abspath $(MATHITALIC_MANIFEST))' MATHITALIC_SOURCE_EPOCH='$(MATHITALIC_EPOCH)'
$(MATHITALIC_REF_DIR)/TorchletteSans-%.ttf: build.py $$(call STATIC,$$*) $(MATHITALIC_INPUTS) $(VF_DEP) $(REF_DEP) $(MODULE_FILES) $(NORMAL_HELPER_DEPS)
	@mkdir -p $(dir $@)
	MODULES='$(MATHITALIC_REF_ARG)' $(PY) build.py $(call STATIC,$*) $@ $(WGHT_$*) $*
	$(PY) mathitalic_references.py record-ref --inputs '$(MATHITALIC_INPUTS)' --font '$@' --style '$*' --donor '$(call STATIC,$*)'
$(MATHITALIC_MANIFEST): $(MATHITALIC_REFS) FORCE
	$(PY) mathitalic_references.py manifest --inputs '$(MATHITALIC_INPUTS)' --directory '$(MATHITALIC_REF_DIR)' --styles $(MATHITALIC_REF_STYLES) --output '$@'
$(TTFS): $(MATHITALIC_MANIFEST)
endif
endif

SUBSET_FLAGS = --unicodes='$(UNICODES)' --layout-features='$(WEB_FEATURES)' --name-IDs='*' --name-languages='*' \
	--notdef-outline --recalc-average-width --no-hinting --flavor=woff2

.PHONY: all ttf verify fontbakery check clean FORCE
all: $(WEBS)
ttf: $(TTFS)

$(BUILD_DIR)/Mulish-%.ttf: instance.py $(VF_DEP)
	@mkdir -p $(BUILD_DIR)
	$(PY) instance.py "$(VF)" $* $@

$(BUILD_DIR)/MulishItalic-%.ttf: instance.py $(VF_DEP)
	@mkdir -p $(BUILD_DIR)
	$(PY) instance.py "$(VFI)" $* $@

$(MODULE_STAMP): FORCE
	@mkdir -p $(BUILD_DIR)
	@echo '$(MODULES_ON)' | cmp -s - $@ || echo '$(MODULES_ON)' > $@

$(BUILD_DIR)/TorchletteSans-%.ttf: build.py $$(call STATIC,$$*) $(VF_DEP) $(REF_DEP) $(MODULE_FILES) $(NORMAL_HELPER_DEPS) $(MODULE_STAMP)
	$(if $(MATHITALIC_ON),$(PY) mathitalic_references.py guard --inputs '$(MATHITALIC_INPUTS)' --manifest '$(MATHITALIC_MANIFEST)' --style '$*',:)
	$(MATHITALIC_ENV) MODULES='$(MODULES_ARG)' $(PY) build.py $(call STATIC,$*) $@ $(WGHT_$*) $*

$(WEB_DIR)/TorchletteSans-%.woff2: $(BUILD_DIR)/TorchletteSans-%.ttf web_features.txt
	@mkdir -p $(dir $@)
	$(SUBSET) $< $(SUBSET_FLAGS) --output-file=$@
	@ls -l $@

# Each full font, then its web subset (as a .ttf that keeps glyph names, which the
# shipped woff2 drops; the glyphs and layout tables are the same), each against
# stock Mulish (Mulish Italic for an italic style) at the same wght for Mulish's own
# features; then ss16 (the prose ligatures) on each, with the lesson prose in
# ../../web/levels for the full font; then each built module's
# modules/verify_<name>.py, if it has one, on both.
# The subset runs have TS_WEB_SUBSET=1: the scripts skip the checks of features that
# web_features.txt leaves out (webfeatures.py). The full font's checks are complete.
verify: fontbakery verify.py verify_ss16.py webfeatures.py web_features.txt $(TTFS) $(foreach s,$(STYLES),$(call STATIC,$(s)))
	@set -e; for s in $(STYLES); do \
	  case $$s in $(foreach t,$(STYLES),$(t)$(rparen) st=$(call STATIC,$(t));;) esac; \
	  echo "== $$s ($$st)"; \
	  MULISH_STATIC=$$st $(PYHB) verify.py $(BUILD_DIR)/TorchletteSans-$$s.ttf ss04 ss05 ss06 ss07; \
	  $(SUBSET) $(BUILD_DIR)/TorchletteSans-$$s.ttf $(subst --flavor=woff2,--glyph-names,$(SUBSET_FLAGS)) --output-file=$(BUILD_DIR)/web-subset-$$s.ttf; \
	  TS_WEB_SUBSET=1 MULISH_STATIC=$$st $(PYHB) verify.py $(BUILD_DIR)/web-subset-$$s.ttf ss04 ss05 ss06 ss07; \
	  $(PYHB) verify_ss16.py $(BUILD_DIR)/TorchletteSans-$$s.ttf ../../web/levels; \
	  TS_WEB_SUBSET=1 $(PYHB) verify_ss16.py $(BUILD_DIR)/web-subset-$$s.ttf; \
	  for m in $(MODULES_ON); do \
	    if [ -f modules/verify_$$m.py ]; then \
	      echo "-- module $$m"; \
	      $(MATHITALIC_ENV) MULISH_STATIC=$$st $(PYHB) modules/verify_$$m.py $(BUILD_DIR)/TorchletteSans-$$s.ttf $$s full; \
	      $(MATHITALIC_ENV) TS_WEB_SUBSET=1 MULISH_STATIC=$$st $(PYHB) modules/verify_$$m.py $(BUILD_DIR)/web-subset-$$s.ttf $$s subset; \
	    fi; \
	  done; \
	done

# fontbakery's universal profile on the full fonts together (so its family
# checks run too), offline, about 30 s. The reports go to $(BUILD_DIR)/fontbakery.{json,md}.
# fontbakery_gate.py gets fontbakery's exit status with the report and fails the
# target on an operational error, an incomplete report, or any FAIL, FATAL or ERROR
# but the known open checks it allows (each with its reason); then
# verify_fontbakery_gate.py checks that the gate rejects broken runs. The warning
# silenced is fontbakery failing to import a Google Fonts module that
# check-universal does not use.
fontbakery: fontbakery_gate.py verify_fontbakery_gate.py $(TTFS)
	@rm -f $(BUILD_DIR)/fontbakery.json $(BUILD_DIR)/fontbakery.md
	status=0; PYTHONWARNINGS=ignore::UserWarning $(FB) check-universal --skip-network --auto-jobs --succinct --loglevel FAIL \
	  --json $(BUILD_DIR)/fontbakery.json $(TTFS) || status=$$?; \
	$(PY) fontbakery_gate.py $$status $(BUILD_DIR)/fontbakery.json $(TTFS) --markdown $(BUILD_DIR)/fontbakery.md
	$(PY) verify_fontbakery_gate.py $(BUILD_DIR)/fontbakery.json $(TTFS)

# A clean rebuild of every style must match the committed woff2 files byte for byte.
check:
	rm -rf $(BUILD_DIR)
	@set -e; for s in $(STYLES); do \
	  $(MAKE) --no-print-directory $(BUILD_DIR)/TorchletteSans-$$s.ttf >/dev/null; \
	  $(SUBSET) $(BUILD_DIR)/TorchletteSans-$$s.ttf $(SUBSET_FLAGS) --output-file=$(BUILD_DIR)/rebuilt-$$s.woff2; \
	  cmp $(BUILD_DIR)/rebuilt-$$s.woff2 $(WEB_REF)/TorchletteSans-$$s.woff2 && echo "identical: $$s"; \
	done

clean:
	rm -rf $(BUILD_DIR)

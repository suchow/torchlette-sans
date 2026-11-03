"""lnum: lining figures, so `font-variant-numeric: lining-nums` overrides old-style figures.

The font's default figures are lining (tabular `zero` ... `nine`, proportional `.pnum`); onum
makes them old-style (proportional `.osf`, tabular `.tosf`, and the ss08 sevens
`seven.osf.ss08`, `seven.tosf.ss08`). lnum maps every old-style figure back to the lining
figure of the same spacing:

    d.osf -> d.pnum        d.tosf -> d        seven.osf.ss08 -> seven.pnum.ss08        seven.tosf.ss08 -> seven.ss08

so lnum changes the figures' style and keeps whatever spacing onum, tnum and pnum chose: onum +
lnum is proportional lining, onum + tnum + lnum tabular lining, and lnum with no onum changes
nothing. The pairs come from build.py's FIG, FORMS_O and FORMS_L, and the build stops if any
old-style figure in the font has no lining partner.

Layout: one lookup, LNUM_FIGURES, registered as the new tag lnum, placed right after build.py's
main block (after='main'): after Mulish's onum and build.py's onum, tnum, pnum and ss08, so lnum
wins over onum whatever the order the features are listed in, and before ss16 and the
otfeatures lookups (zero, the figure-mark case forms), which then see lining figures: ss16's
old-style operators, ordinals and percent (minus.osf, one.ord.osf ...) and the slashed
old-style zeros do not form under lnum. Small-cap figures (smcp, c2sc) are untouched.

No glyph, advance or cmap entry is added or changed.
"""
import re

FIG_RE = re.compile(r'^(zero|one|two|three|four|five|six|seven|eight|nine)(\.(osf|tosf|pnum|ss08))+$')


def _lining(name):
    """The lining figure of the same spacing as an old-style one."""
    return name.replace('.tosf', '').replace('.osf', '.pnum')


def features(ctx):
    order = ctx.font.getGlyphOrder()
    have = set(order)
    old = [n for d in ctx.FIG for n in ctx.FORMS_O[d]]
    # every old-style figure form in the font, also any that FORMS_O might miss
    found = [n for n in order if FIG_RE.match(n) and ('.osf' in n or '.tosf' in n)]
    missing = sorted(set(found) - set(old))
    if missing:
        raise SystemExit(f'lnum: old-style figures not in FORMS_O: {missing}')
    pairs = []
    for d in ctx.FIG:
        for o in ctx.FORMS_O[d]:
            ln = _lining(o)
            if o not in have or ln not in have or ln not in ctx.FORMS_L[d]:
                raise SystemExit(f'lnum: no lining partner for {o} ({ln})')
            pairs.append((o, ln))
    src, dst = ' '.join(a for a, _ in pairs), ' '.join(b for _, b in pairs)
    ctx.gsub(f'lookup LNUM_FIGURES {{ sub [{src}] by [{dst}]; }} LNUM_FIGURES;\n'
             'feature lnum { lookup LNUM_FIGURES; } lnum;\n', after='main')
    ctx.log(f'{len(pairs)} old-style figures mapped to lining')

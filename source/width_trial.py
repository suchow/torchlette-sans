"""Disposable Regular condensed-width study; not a release-font build step.

Compress Latin letters, figures, and punctuation horizontally. A horizontal
outline expansion compensates vertical-stem weight. A 256-fold vertical stretch
before stroking limits vertical expansion to less than 0.05 font units. This is
a geometric trial; counter shapes, corners, and spacing require visual review.
Both output fonts are unhinted for a consistent comparison. No width axis is added.
"""
import copy
import json
import sys
from pathlib import Path

import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

SCALE = 0.85
Y_STRETCH = 256
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
FIGURES = '0123456789'
PUNCTUATION = '.,:;!?-–—()[]{}“”‘’"\'…/\\%&@#*+=<>'


def path_of(font, name):
    gs = font.getGlyphSet()
    p = pathops.Path()
    gs[name].draw(p.getPen(glyphSet=gs))
    return p


def stem_at_baseline(font, name):
    g = font['glyf'][name]
    points, _, _ = g.getCoordinates(font['glyf'])
    xs = sorted({x for x, y in points if y == 0})
    if len(xs) < 2:
        raise ValueError(f'Cannot measure baseline stem of {name}')
    return xs[1] - xs[0]


def condensed_path(p, stem):
    correction = (1 - SCALE) * stem
    q = pathops.Path()
    p.draw(TransformPen(q.getPen(),
                        (SCALE, 0, 0, Y_STRETCH, correction / 2, 0)))
    edge = pathops.Path()
    q.draw(edge.getPen())
    edge.stroke(correction, pathops.LineCap.BUTT_CAP,
                pathops.LineJoin.ROUND_JOIN, 4)
    edge.convertConicsToQuads(0.1)
    expanded = pathops.op(q, edge, pathops.PathOp.UNION)
    out = pathops.Path()
    expanded.draw(TransformPen(out.getPen(), (1, 0, 0, 1 / Y_STRETCH, 0, 0)))
    return out, correction


def unhint(font):
    for name in font.getGlyphOrder():
        font['glyf'][name].removeHinting()
    for tag in ('fpgm', 'prep', 'cvt ', 'hdmx', 'LTSH', 'VDMX'):
        if tag in font:
            del font[tag]


def label(font, family, postscript):
    for record in font['name'].names:
        value = {1: family, 2: 'Regular', 3: postscript,
                 4: family + ' Regular', 6: postscript, 16: family, 17: 'Regular'}.get(record.nameID)
        if value is not None:
            record.string = value.encode(record.getEncoding())


def main(source, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    control = TTFont(source)
    unhint(control)
    trial = copy.deepcopy(control)
    cmap = trial.getBestCmap()
    cap_stem = stem_at_baseline(control, cmap[ord('H')])
    lower_stem = stem_at_baseline(control, cmap[ord('l')])
    zero = sorted((c.bounds for c in path_of(control, cmap[ord('0')]).contours),
                  key=lambda b: b[0])
    digit_stem = zero[1][0] - zero[0][0]
    report = {'scale': SCALE, 'stems': {'capital': cap_stem,
              'lowercase': lower_stem, 'figure': digit_stem}, 'glyphs': []}
    seen = set()
    for char in LETTERS + FIGURES + PUNCTUATION:
        name = cmap.get(ord(char))
        if name is None:
            raise ValueError(f'Missing trial input U+{ord(char):04X}')
        if name in seen:
            continue
        seen.add(name)
        stem = cap_stem if char.isupper() else digit_stem if char in FIGURES else lower_stem
        p = path_of(control, name)
        q, correction = condensed_path(p, stem)
        pen = TTGlyphPen(None)
        q.draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
        glyph = pen.glyph(dropImpliedOnCurves=True)
        trial['glyf'][name] = glyph
        glyph.recalcBounds(trial['glyf'])
        advance = round(control['hmtx'][name][0] * SCALE + correction)
        trial['hmtx'][name] = (advance, glyph.xMin)
        report['glyphs'].append({'character': char, 'glyph': name,
                                'advance_before': control['hmtx'][name][0],
                                'advance_after': advance})
    trial['OS/2'].usWidthClass = 3
    label(control, 'Torchlette Sans Width Control', 'TorchletteSans-WidthControl')
    label(trial, 'Torchlette Sans Condensed Trial', 'TorchletteSans-CondensedTrial')
    control.save(output / 'TorchletteSans-Regular-Control.ttf')
    trial.save(output / 'TorchletteSans-Regular-CondensedTrial.ttf')
    (output / 'construction.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['stems']), len(report['glyphs']), 'trial glyphs')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: width_trial.py SOURCE.ttf NEW_OUTPUT_DIRECTORY')
    main(*sys.argv[1:])

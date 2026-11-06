"""Contour correspondence regressions using portable synthetic source fonts."""
import unittest

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

import variable as b


def polygon(points):
    return [(a, b.lerp(a, z, .5), z) for a, z in zip(points, points[1:] + points[:1])]


def rect(x, y, w, h, hole=False):
    contour = polygon([(x, y), (x, y + h), (x + w, y + h), (x + w, y)])
    return b.reverse(contour) if hole else contour


class Mixed(unittest.TestCase):
    def sources(self):
        notch = polygon([(0, 0), (0, 100), (40, 100), (40, 60), (60, 60),
                         (60, 100), (100, 100), (100, 0)])
        return [[notch, rect(20, 20, 10, 10, True)], [notch],
                [rect(0, 0, 100, 100), rect(45, 70, 10, 20, True)]]

    def test_mixed_closing_and_opening_keep_separate_lineage(self):
        sources = self.sources()
        aligned, count, proof = b.mixed_counter_correspondence(sources)
        self.assertEqual(count, 2)
        self.assertEqual([r['transition'] for r in proof['groups']], ['closing', 'opening'])
        for before, after in zip(sources, aligned):
            difference = b.pathops.op(b.contours_path(before), b.contours_path(after),
                                     b.pathops.PathOp.XOR)
            self.assertEqual(difference.area, 0)
        self.assertTrue(all(len(cs) == 2 for cs in aligned))

    def test_single_counter_family_keeps_existing_path(self):
        box = rect(0, 0, 100, 100)
        self.assertIsNone(b.mixed_counter_correspondence([
            [box, rect(20, 20, 10, 10, True)], [box],
            [box, rect(20, 20, 10, 10, True)]]))

    def test_two_closing_counters_do_not_select_mixed_strategy(self):
        box = rect(0, 0, 100, 100)
        self.assertIsNone(b.mixed_counter_correspondence([
            [box, rect(20, 20, 10, 10, True)], [box],
            [box, rect(70, 70, 10, 10, True)]]))

    def test_noncontained_counter_rejected(self):
        source = self.sources()
        source[0][1] = rect(-40, -40, 10, 10, True)
        self.assertIsNone(b.mixed_counter_correspondence(source))

    def test_multiple_outer_or_multiple_hole_master_rejected(self):
        source = self.sources()
        source[0].append(rect(200, 200, 10, 10))
        self.assertIsNone(b.mixed_counter_correspondence(source))
        source = self.sources()
        source[0].append(rect(80, 20, 5, 5, True))
        self.assertIsNone(b.mixed_counter_correspondence(source))


def source_font():
    pen = TTGlyphPen(None)
    pen.moveTo((40, 0))
    pen.qCurveTo((0, 0), (0, 50))
    pen.qCurveTo((0, 100), (40, 100))
    pen.qCurveTo((80, 100), (80, 50))
    pen.qCurveTo((80, 0), (40, 0))
    pen.closePath()
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'probe'])
    fb.setupCharacterMap({0xE000: 'probe'})
    fb.setupGlyf({'.notdef': TTGlyphPen(None).glyph(), 'probe': pen.glyph()})
    fb.setupHorizontalMetrics({'.notdef': (1000, 0), 'probe': (100, 0)})
    return fb.font


class IdentityTests(unittest.TestCase):
    def test_identical_source_outline_and_metrics_preserved(self):
        fonts = [source_font() for _ in range(3)]
        # Metrics may vary even when source outlines are fixed.
        fonts[1]['hmtx']['probe'] = (110, 5)
        before = [f['glyf']['probe'].compile(f['glyf']) for f in fonts]
        metrics = [f['hmtx']['probe'] for f in fonts]
        stats = b.canonicalize(fonts, only={'probe'})
        self.assertEqual(stats['changed_glyphs'], [])
        self.assertEqual(before, [f['glyf']['probe'].compile(f['glyf']) for f in fonts])
        self.assertEqual(metrics, [f['hmtx']['probe'] for f in fonts])

    def test_matching_signatures_do_not_freeze_different_geometry(self):
        fonts = [source_font() for _ in range(2)]
        x, y = fonts[1]['glyf']['probe'].coordinates[0]
        fonts[1]['glyf']['probe'].coordinates[0] = (x + 7, y)
        self.assertEqual(b.signature(fonts[0], 'probe'), b.signature(fonts[1], 'probe'))
        stats = b.canonicalize(fonts, only={'probe'})
        self.assertIn('probe', stats['changed_glyphs'])
        self.assertNotEqual(b.contours(fonts[0], 'probe'), b.contours(fonts[1], 'probe'))


class InklessContour(unittest.TestCase):
    def test_canonicalized_glyph_keeps_two_point_spacing_contour(self):
        # mathglyphs/math_table give accents a two-point contour under their ink;
        # it carries their bounds for math accent placement and has no area, so
        # Boolean normalization drops it. Canonical masters must restore it.
        fonts = [source_font() for _ in range(2)]
        x, y = fonts[1]['glyf']['probe'].coordinates[0]
        fonts[1]['glyf']['probe'].coordinates[0] = (x + 7, y)
        for f, spot in zip(fonts, ((40, -90), (44, -95))):
            pen = TTGlyphPen(None)
            f['glyf']['probe'].draw(pen, f['glyf'])
            pen.moveTo(spot); pen.lineTo((spot[0] + 1, spot[1])); pen.closePath()
            f['glyf']['probe'] = pen.glyph(dropImpliedOnCurves=False)
        stats = b.canonicalize(fonts, only={'probe'})
        self.assertIn('probe', stats['changed_glyphs'])
        for f, spot in zip(fonts, ((40, -90), (44, -95))):
            g = f['glyf']['probe']
            coords, ends, _ = g.getCoordinates(f['glyf'])
            self.assertEqual(list(coords[ends[-2] + 1:]), [spot, (spot[0] + 1, spot[1])])
            g.recalcBounds(f['glyf'])
            self.assertEqual(g.yMin, spot[1])


class Closing(unittest.TestCase):
    def test_closing_retains_independent_counter_and_exact_endpoint_fill(self):
        sources = [[rect(0, 0, 100, 100), rect(30, 30, 20, 20, True)],
                   [rect(0, 0, 100, 100)]]
        result = b.mixed_counter_correspondence(sources, allow_single_closing=True)
        self.assertIsNotNone(result)
        aligned, count, proof = result
        self.assertEqual(count, 1)
        self.assertEqual(proof['mode'], 'closing_spatial_counter_identity')
        self.assertEqual([len(cs) for cs in aligned], [2, 2])
        self.assertEqual(b.area(aligned[1][1]), 0)
        for before, after in zip(sources, aligned):
            difference = b.pathops.op(b.contours_path(before), b.contours_path(after),
                                     b.pathops.PathOp.XOR)
            self.assertEqual(difference.area, 0)

    def test_opening_only_does_not_take_closing_dispatch(self):
        closed = [rect(0, 0, 100, 100), rect(40, 60, 20, 20, True)]
        opened = [polygon([(0, 0), (0, 100), (40, 100), (40, 50), (60, 50),
                           (60, 100), (100, 100), (100, 0)])]
        self.assertIsNone(b.mixed_counter_correspondence(
            [closed, opened], allow_single_closing=True))

    def test_persistent_counter_does_not_take_transition_dispatch(self):
        source = [rect(0, 0, 100, 100), rect(30, 30, 20, 20, True)]
        self.assertIsNone(b.mixed_counter_correspondence(
            [source, source], allow_single_closing=True))


if __name__ == '__main__':
    unittest.main()

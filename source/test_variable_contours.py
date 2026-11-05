"""Filled-shape regression for mixed-reference contour winding."""
import importlib.util
import os
from pathlib import Path
import unittest

source = Path(os.environ.get('VARIABLE_SOURCE', Path(__file__).with_name('variable.py')))
spec = importlib.util.spec_from_file_location('variable_under_test', source)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def rectangle(x0, y0, x1, y1, positive=False):
    points = [(x0,y0),(x0,y1),(x1,y1),(x1,y0)]
    result = [(a, ((a[0]+b[0])/2,(a[1]+b[1])/2), b)
              for a,b in zip(points,points[1:]+points[:1])]
    return v.reverse(result) if positive else result


class ContourMatching(unittest.TestCase):
    def assert_fill_preserved(self, before, after):
        self.assertEqual(len(before), len(after))
        for original, matched in zip(before, after):
            delta = v.pathops.op(v.contours_path(original), v.contours_path(matched),
                                v.pathops.PathOp.XOR)
            self.assertEqual(delta.area, 0.0)

    def test_mixed_reference_largest_contour_is_counter(self):
        # Two small disjoint components become a large ring. The reference
        # takes both negative components from the light master and the larger
        # positive counter from the heavy master, unlike any actual master.
        light = [rectangle(0,0,100,100), rectangle(200,0,300,100)]
        heavy = [rectangle(0,0,400,400), rectangle(40,40,360,360,True)]
        sources = [light, light, heavy]
        result, missing = v.match_contours(sources, 1000)
        self.assertEqual(missing, 3)
        self.assertTrue(all(len(c) == 3 for c in result))
        self.assert_fill_preserved(sources, result)
        for original, matched in zip(sources,result):
            self.assertEqual(sorted(1 if v.area(c)>0 else -1 for c in original),
                             sorted(1 if v.area(c)>0 else -1 for c in matched if abs(v.area(c))>1))

    def test_global_reversal_and_contour_order_preserve_ring(self):
        ring = [rectangle(0,0,400,400), rectangle(40,40,360,360,True)]
        sources = [ring, ring, [v.reverse(c) for c in reversed(ring)]]
        result, missing = v.match_contours(sources, 1000)
        self.assertEqual(missing, 0)
        self.assert_fill_preserved(sources, result)
        self.assertTrue(all(sorted(1 if v.area(c)>0 else -1 for c in cs)==[-1,1]
                            for cs in result))

    def test_component_disappearance_preserves_remaining_ink(self):
        first, second = rectangle(0,0,100,100), rectangle(200,0,300,100)
        sources = [[first,second], [first,second], [first]]
        result, missing = v.match_contours(sources, 1000)
        self.assertEqual(missing, 1)
        self.assert_fill_preserved(sources, result)


if __name__ == '__main__':
    unittest.main()

import unittest

from forgebridge import native_scene as ns


class GeometryTests(unittest.TestCase):
    def test_world_transform_matches_toolkit_import(self):
        # Values verified against the Toolkit's own UVTT import of Count's Crypt.
        self.assertEqual(ns._world({'x': 7.5, 'y': 11}, ns.UNITS_PER_GRID), (19.2, -28.16))
        x, y = ns._world({'x': 24.95, 'y': 3.29}, ns.UNITS_PER_GRID)
        self.assertAlmostEqual(x, 63.872); self.assertAlmostEqual(y, -8.4224)

    def test_segments_split_polylines(self):
        uvtt = {'line_of_sight': [[{'x': 0, 'y': 0}, {'x': 1, 'y': 0}, {'x': 1, 'y': 1}]]}
        self.assertEqual(len(list(ns._segments(uvtt))), 2)

    def test_non_finite_coordinates_rejected(self):
        with self.assertRaises(ValueError):
            ns._world({'x': float('nan'), 'y': 0}, ns.UNITS_PER_GRID)

    def test_invalid_inputs_fail_before_writing(self):
        with self.assertRaises(ValueError):
            ns.synthesize_map(b'', b'', {}, name='', image_meta_path='x', asset_name='x')


if __name__ == '__main__':
    unittest.main()

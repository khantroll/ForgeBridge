import unittest
import io
from PIL import Image

from forgebridge import native_scene as ns
from forgebridge.scene_records import record, LIBRARIES, encode, canonical_graph, template_map, blank_map
from forgebridge.nrbf import Reader
from test_native_map import FixtureWriter


class GeometryTests(unittest.TestCase):
    def fixture(self):
        # Synthetic records only, written independently by the test FixtureWriter.
        container = record('blank')
        control = record('blank')
        tiles = control.members['_tiles'].members
        tiles['_items'].items = [record(k) for k in ('wall', 'door', 'light', 'image')]
        tiles.update(_size=4, _version=4)
        serialize = lambda n: FixtureWriter(LIBRARIES).write(n)
        uvtt = {'resolution': {'pixels_per_grid': 50, 'map_size': {'x': 8, 'y': 4}},
                'line_of_sight': [[{'x': 0, 'y': 0}, {'x': 8, 'y': 0}]],
                'portals': [{'bounds': [{'x': 1, 'y': 0}, {'x': 2, 'y': 0}], 'closed': False}],
                'lights': [{'position': {'x': 2, 'y': 1}, 'range': 3}]}
        return serialize(container), serialize(control), uvtt

    def test_fixture_writer_end_to_end_map_matches_schema_factory(self):
        blank, control, uvtt = self.fixture()
        options = dict(name='Synthetic map', image_meta_path='MyAssets/Media/Generated/Background.rwmeta', asset_name='Background')
        data, report = ns.synthesize_map(blank, control, uvtt, **options)
        built, _ = ns.synthesize_map(blank_map(), template_map(), uvtt, **options)
        self.assertEqual(canonical_graph(data), canonical_graph(built))
        self.assertEqual(report['records'], {'walls': 1, 'doors': 1, 'lights': 1, 'image': 1})
        reader = Reader(data); graph = reader.read()
        values = [o['members'] for o in reader.objects.values() if isinstance(o, dict)
                  and o.get('class') == 'ArkenTilePresetRepeatable']
        active = [o for o in values if o.get('_uID') in (2, 3)]
        self.assertEqual(len(active), 2)

    def test_background_pair_and_map_thumbnail_use_generated_pixels(self):
        source = io.BytesIO(); Image.new('RGB', (400, 200), 'red').save(source, 'PNG')
        full = FixtureWriter(LIBRARIES).write(record('asset'))
        meta = FixtureWriter(LIBRARIES).write(record('asset_meta'))
        before_limit = Image.MAX_IMAGE_PIXELS
        file, info, report = ns.background_asset(full, meta, source.getvalue(), 'Synthetic')
        self.assertEqual(Image.MAX_IMAGE_PIXELS, before_limit)
        self.assertEqual(report['dimensions'], [400, 200])
        def pixels(data):
            reader = Reader(data, max_items=64000000); reader.read()
            blob = next(v['bytes'] for v in reader.objects.values() if isinstance(v, dict) and 'bytes' in v)
            return Image.open(io.BytesIO(blob))
        self.assertEqual(pixels(file).size, (400, 200))
        self.assertEqual(pixels(info).size, (128, 64))
        thumbnail = ns.map_metadata(encode(record('map_meta')), 'Synthetic', source.getvalue())
        self.assertEqual(pixels(thumbnail).size, (256, 128))
        self.assertEqual(pixels(thumbnail).convert('RGB').getpixel((0, 0)), (255, 0, 0))

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

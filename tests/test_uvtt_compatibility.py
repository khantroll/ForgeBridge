"""Regression cases for the real Arkenforge import failures observed 2026-10-08."""
import base64
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from forgebridge.cli import main
from forgebridge.uvtt import _scene_to_uvtt, _walls_to_uvtt, build_uvtt_slice
from forgebridge.validate import InventoryFatal, load_schema, repo_schema, validate


class ArkenforgeCompatibilityTests(unittest.TestCase):
    def test_fireplace_movement_wall_does_not_become_an_opaque_barrier(self):
        walls = [
            {'_id': 'fireplace-front', 'c': [2000, 1600, 2000, 2900],
             'light': 0, 'sight': 0, 'move': 20, 'sound': 0},
            {'_id': 'outer-wall', 'c': [1962, 1575, 1962, 2900],
             'light': 20, 'sight': 20},
        ]
        original = json.loads(json.dumps(walls))
        lines = []
        los, portals = _walls_to_uvtt(walls, 100, lines, (800, 1000))
        self.assertEqual(len(los), 1)
        self.assertAlmostEqual(los[0][0]['x'], 11.62)
        self.assertAlmostEqual(los[0][1]['x'], 11.62)
        self.assertEqual([p['y'] for p in los[0]], [5.75, 19])
        self.assertEqual(portals, [])
        self.assertEqual(walls, original)
        warning = next(x for x in lines if x['code'] == 'wall-transparent-omitted')
        self.assertIn('fireplace-front', warning['summary'])
        self.assertIn('"move": 20', warning['summary'])
        self.assertIn('"x": 12', warning['summary'])
        self.assertIn('recreate', warning['summary'])

    def test_mixed_optical_walls_keep_geometry_and_get_specific_instructions(self):
        for light, sight, instruction in [(0, 20, 'disable Blocks Light'),
                                           (20, 0, 'disable Blocks Vision'),
                                           (0, 10, 'not equivalent to a simple on/off')]:
            with self.subTest(light=light, sight=sight):
                lines = []
                los, _ = _walls_to_uvtt([{'_id': 'mixed', 'c': [0, 0, 100, 0],
                                         'light': light, 'sight': sight}], 100, lines)
                self.assertEqual(len(los), 1)
                warning = next(x for x in lines if x['code'] == 'wall-blocking-properties')
                self.assertIn('line_of_sight 0', warning['summary'])
                self.assertIn(instruction, warning['summary'])

    def test_missing_optical_settings_do_not_imply_transparency(self):
        for restrictions in [{}, {'light': 0}, {'sight': 0}]:
            with self.subTest(restrictions=restrictions):
                lines = []
                los, _ = _walls_to_uvtt([{'c': [0, 0, 100, 0], **restrictions}], 100, lines)
                self.assertEqual(len(los), 1)
                self.assertTrue(any(x['code'] == 'wall-blocking-properties' for x in lines))

    def test_directional_and_threshold_walls_are_reported_for_review(self):
        for overrides in [{'dir': 1}, {'threshold': {'light': 5}}, {'light': 30}]:
            with self.subTest(overrides=overrides):
                lines = []
                los, _ = _walls_to_uvtt([{'c': [0, 0, 100, 0], 'light': 20,
                                         'sight': 20, **overrides}], 100, lines)
                self.assertEqual(len(los), 1)
                self.assertTrue(any(x['code'] == 'wall-blocking-properties' for x in lines))

    def test_transparent_doors_remain_portals_with_source_state(self):
        lines = []
        los, portals = _walls_to_uvtt([{'_id': 'entrance', 'c': [0, 0, 100, 0],
                                      'door': 1, 'ds': 0, 'light': 0, 'sight': 0}], 100, lines)
        self.assertEqual(los, [])
        self.assertEqual(len(portals), 1)
        self.assertTrue(portals[0]['closed'])
        self.assertTrue(any(x['code'] == 'portal-blocking-properties' for x in lines))

    def test_default_null_thresholds_do_not_require_optical_adjustment(self):
        lines = []
        _walls_to_uvtt([{'c': [0, 0, 100, 0], 'light': 20, 'sight': 20,
                        'threshold': {'attenuation': False, 'light': None,
                                      'sight': None, 'sound': None}}], 100, lines)
        self.assertFalse(any(x['code'] == 'wall-blocking-properties' for x in lines))

    def scene(self, root, *, mode='RGB', image_format='PNG', **overrides):
        output = io.BytesIO()
        Image.new(mode, (30, 40)).save(output, format=image_format)
        suffix = image_format.lower()
        (root / ('map.' + suffix)).write_bytes(output.getvalue())
        scene = {
            '_id': 'scene', 'name': 'Compatibility test', 'width': 3000, 'height': 4000,
            'padding': 0.25, 'grid': {'type': 1, 'size': 100, 'distance': 5},
            'background': {'src': 'map.' + suffix},
            'walls': [
                {'_id': 'wall', 'c': [800, 1000, 900, 1100], 'door': 0},
                {'_id': 'door', 'c': [900, 1200, 900, 1000], 'door': 1, 'ds': 1,
                 'light': 20, 'sight': 20, 'move': 20},
            ],
            'lights': [{'_id': 'lamp', 'x': 850, 'y': 1150,
                        'config': {'color': '#abc', 'dim': 10, 'bright': 5}}],
        }
        scene.update(overrides)
        return scene

    def test_padding_normalizes_every_placeable_and_preserves_absolute_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            uvtt, lines = _scene_to_uvtt(root, self.scene(root))
        self.assertEqual(uvtt['line_of_sight'], [[{'x': 0, 'y': 0}, {'x': 1, 'y': 1}]])
        portal = uvtt['portals'][0]
        self.assertEqual(portal['bounds'], [{'x': 1, 'y': 2}, {'x': 1, 'y': 0}])
        self.assertEqual(portal['position'], {'x': 0, 'y': 2})
        self.assertEqual(portal['rotation'], 0)
        self.assertFalse(portal['closed'])
        self.assertEqual(uvtt['lights'][0]['position'], {'x': .5, 'y': 1.5})
        self.assertEqual(uvtt['lights'][0]['color'], 'ffaabbcc')
        self.assertNotIn('lights', uvtt['environment'])
        self.assertEqual(validate(uvtt, load_schema(repo_schema('uvtt-core.schema.json'))), [])
        warning = next(line for line in lines if line['code'] == 'portal-blocking-properties')
        self.assertIn('"light": 20', warning['summary'])
        self.assertIn('ds=1', warning['summary'])

    def test_origin_is_not_a_manor_specific_constant(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scene = self.scene(root, width=1200, height=800, padding=.1,
                               walls=[], lights=[{'x': 200, 'y': 100, 'config': {'color': '#123456'}}])
            uvtt, _ = _scene_to_uvtt(root, scene)
            self.assertEqual(uvtt['lights'][0]['position'], {'x': 0, 'y': 0})
            scene['dimensions'] = {'sceneX': 10, 'sceneY': 20}
            scene['background'].update(offsetX=5, offsetY=-5)
            uvtt, _ = _scene_to_uvtt(root, scene)
            self.assertEqual(uvtt['lights'][0]['position'], {'x': 1.85, 'y': .85})

    def test_webp_and_palette_png_decode_as_rgba_png_without_resizing(self):
        for mode, fmt in [('RGB', 'WEBP'), ('P', 'PNG'), ('L', 'PNG')]:
            with self.subTest(mode=mode, fmt=fmt), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                uvtt, _ = _scene_to_uvtt(root, self.scene(root, mode=mode, image_format=fmt))
                data = base64.b64decode(uvtt['image'])
                self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
                with Image.open(io.BytesIO(data)) as image:
                    self.assertEqual(image.mode, 'RGBA')
                    self.assertEqual(image.size, (30, 40))

    def test_invalid_image_and_unsupported_background_transform_fail_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scene = self.scene(root)
            scene['background']['rotation'] = 45
            with self.assertRaisesRegex(InventoryFatal, 'rotation'):
                _scene_to_uvtt(root, scene)
            scene['background']['rotation'] = 0
            (root / 'map.png').write_bytes(b'\x89PNG\r\n\x1a\ninvalid')
            with self.assertRaisesRegex(InventoryFatal, 'decoded'):
                _scene_to_uvtt(root, scene)

    def test_source_scene_preserves_window_properties_and_untinted_lights(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scene = self.scene(root)
            scene['walls'][1].update(light=0, sight=0, ds=0)
            scene['lights'].append({'_id': 'untinted', 'x': 900, 'y': 1000,
                                    'config': {'color': None, 'dim': 20}})
            scene['flags'] = {'original': {'unknown': 123}}
            (root / 'module.json').write_text(json.dumps({'id': 'module', 'title': 'Test',
                'packs': [{'name': 'scenes', 'label': 'Scenes', 'type': 'Scene', 'path': 'scenes.db'}]}))
            (root / 'scenes.db').write_text(json.dumps(scene)+'\n')
            document = build_uvtt_slice(root, 'scene')
            self.assertEqual(document['source_scene'], scene)
            self.assertTrue(document['uvtt']['portals'][0]['closed'])
            self.assertEqual(len(document['uvtt']['lights']), 2)
            self.assertEqual(document['uvtt']['lights'][1]['color'], 'ffffffff')
            warning = next(line for line in document['loss_report']['manual']
                           if line['code'] == 'portal-blocking-properties')
            self.assertIn('leave Blocks Light disabled', warning['summary'])
            self.assertIn('leave Blocks Vision disabled', warning['summary'])
            dest = root / 'out' / 'test.uvtt'
            from contextlib import redirect_stdout
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(root), '--uvtt-scene', 'scene', '--uvtt-out', str(dest)]), 0)
            companion = json.loads(dest.with_suffix('.forgebridge.json').read_text())
            self.assertEqual(companion['source_scene'], scene)
            self.assertIn('loss_report', companion)
            self.assertNotIn('source_scene', json.loads(dest.read_text()))

    def test_unset_light_tints_are_valid_but_bad_colors_and_positions_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lights = [{'x': 900, 'y': 1100, 'config': {'dim': 5, 'color': color}}
                      for color in (None, '', '  ', '#123456', 'invalid', 42)]
            lights.append({'y': 1100, 'config': {'color': None, 'dim': 5}})
            uvtt, lines = _scene_to_uvtt(root, self.scene(root, lights=lights))
            self.assertEqual([light['color'] for light in uvtt['lights']],
                             ['ffffffff', 'ffffffff', 'ffffffff', 'ff123456'])
            self.assertEqual([light['range'] for light in uvtt['lights']], [1, 1, 1, 1])
            self.assertEqual(sum(line['code'] == 'light-untinted' for line in lines), 3)
            self.assertEqual(sum(line['code'] == 'light-not-written' for line in lines), 3)


if __name__ == '__main__':
    unittest.main()

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
from forgebridge.uvtt import _scene_to_uvtt, build_uvtt_slice
from forgebridge.validate import InventoryFatal, load_schema, repo_schema, validate


class ArkenforgeCompatibilityTests(unittest.TestCase):
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

    def test_source_scene_preserves_window_properties_and_skipped_lights(self):
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
            dest = root / 'out' / 'test.uvtt'
            from contextlib import redirect_stdout
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(root), '--uvtt-scene', 'scene', '--uvtt-out', str(dest)]), 0)
            companion = json.loads(dest.with_suffix('.forgebridge.json').read_text())
            self.assertEqual(companion['source_scene'], scene)
            self.assertIn('loss_report', companion)
            self.assertNotIn('source_scene', json.loads(dest.read_text()))


if __name__ == '__main__':
    unittest.main()

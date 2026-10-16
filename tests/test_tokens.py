import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from dataclasses import replace

from PIL import Image

from forgebridge.foundry_tokens import scene_tokens
from forgebridge.native import Array
from forgebridge.native_tokens import token_canvas, token_files, write_token_zip, png_control
from forgebridge.native_images import native_image_pair
from forgebridge.nrbf import Reader
from test_native_map import node, FixtureWriter
from test_native_media import sample, fixture_node, FixtureWriter as ImageFixtureWriter


def scene():
    return {'_id': 'scene', 'width': 3000, 'height': 4000, 'padding': .25,
        'grid': {'type': 1, 'size': 100}, 'tokens': [{'_id': 'stoker', 'name': 'Stoker',
        'x': 2000, 'y': 2800, 'width': 1, 'height': 1, 'rotation': 45, 'hidden': True,
        'actorId': 'retained', 'texture': {'src': 'token.png', 'scaleX': .8, 'scaleY': .6},
        'flags': {'script': 'never execute'}}]}


def control():
    vector = lambda x, y: node('SVector2', {'x': (0, 11, x), 'y': (0, 11, y)})
    fields = {'_tileName': (1, None, 'Control'), '_name': (1, None, 'Control'),
        '_defaultPlacementType': (2, None, node('MapOptions+ObjectPlacementType', {'value__': (0, 8, 2)})),
        '_contentBasePath': (1, None, 'MyAssets/Encyclopedia/Notes/Control.rwmeta'),
        '_contentType': (1, None, 'note'), '_sortingOrder': (0, 8, 0), '_groupID': (0, 8, -1)}
    for prefix in ('', 'ArkenTilePresetBase+'):
        fields.update({prefix + '_position': (2, None, vector(10., -20.)),
            prefix + '_scale': (2, None, vector(1.024, 1.024)),
            prefix + '_rotation': (0, 11, 0.), prefix + '_hidden': (0, 1, False),
            prefix + '_uID': (0, 9, 17)})
    preset = node('ArkenTilePresetContentLink', fields)
    wrapper = node('ArkenMapTileUpgradeBase', {'_tileInfo': (2, None, preset)})
    tiles = node('Tiles', {'_items': (2, None, Array([wrapper], 2)),
                         '_size': (0, 8, 1), '_version': (0, 8, 1)})
    root = node('ArkenMapUpgrade', {'_name': (1, None, 'ControlMap'),
        '_tiles': (2, None, tiles), '_nextUID': (0, 8, 18)})
    icon = node('ArkenNoteIcon', {'_iconPath': (1, None, 'MyAssets/Media/Sample/Image.rwmeta')})
    size = node('ArkenNoteFieldSize', {'_squareSizeNew': (0, 11, 2.)})
    note = node('ArkenNoteUpgrade', {'_name': (1, None, 'Control'),
        '_tooltipSummary': (1, None, ''), '_noteIcon': (2, None, icon), '_sizeField': (2, None, size)})
    meta = node('ArkenNoteUpgradeMeta', {'_name': (1, None, 'Control'),
        '_tooltipSummary': (1, None, ''), '_noteIcon': (2, None, icon)})
    serialize = lambda n: FixtureWriter({2: 'Assembly-CSharp'}).write(n)
    return serialize(root), serialize(note), serialize(meta)


class TokenTests(unittest.TestCase):
    def test_observed_webp_control_is_reencoded_as_png_and_animation_refused(self):
        raw = io.BytesIO(); Image.new('RGBA', (20, 20), 'red').save(raw, 'WEBP', lossless=True)
        image = fixture_node('ArkenImage', {'_packImgX': -2, '_packImgY': -2,
            '_packImgChannels': 4, '_packImageRAW': Array(list(raw.getvalue()), 0, 2)},
            [0, 0, 0, 7], [8, 8, 8, 2])
        control_image = ImageFixtureWriter({2: 'Assembly-CSharp'}).write(image)
        converted = png_control(control_image)
        graph = Reader(converted).read()
        self.assertEqual(graph['objects'][graph['root_id']]['members']['_packImgX'], -1)
        full, _, _ = native_image_pair(converted, converted, token_canvas(raw.getvalue(), (.8, .8), 20))
        graph = Reader(full).read()
        blob = next(o['bytes'] for o in graph['objects'].values() if isinstance(o, dict) and 'bytes' in o)
        self.assertTrue(bytes(blob).startswith(b'\x89PNG'))
        image.members['_packImageRAW'] = Array(list(b'invalid sentinel payload'), 0, 2)
        with self.assertRaisesRegex(ValueError, 'sentinel'):
            png_control(ImageFixtureWriter({2: 'Assembly-CSharp'}).write(image))
        gif = io.BytesIO()
        Image.new('RGB', (20, 20), 'red').save(gif, 'GIF', save_all=True,
            append_images=[Image.new('RGB', (20, 20), 'blue')], duration=100)
        with self.assertRaisesRegex(ValueError, 'static'):
            token_canvas(gif.getvalue(), (1., 1.), 20)

    def test_complete_zip_is_deterministic_closed_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root / 'source'; package.mkdir()
            raw = io.BytesIO(); Image.new('RGBA', (20, 20), 'red').save(raw, 'PNG')
            (package / 'token.png').write_bytes(raw.getvalue())
            from copy import deepcopy
            s = scene(); companion = root / 'source.json'
            original = deepcopy(s['tokens'][0])
            for i, size in enumerate((2., .5), start=1):
                token = deepcopy(original)
                token.update(_id='other-' + str(i), name='Other ' + str(i),
                             width=size, height=size, x=2000+200*i,
                             rotation=90*i, hidden=i == 1)
                s['tokens'].append(token)
            missing = deepcopy(original)
            missing['_id'] = 'missing'; missing['texture']['src'] = 'missing.png'
            rectangle = deepcopy(original); rectangle.update(_id='rectangle', width=2)
            s['tokens'].extend((missing, rectangle, deepcopy(original)))
            companion.write_text(json.dumps({'source_scene': s}))
            image_pack = root / 'image.zip'; sample(image_pack)
            with zipfile.ZipFile(image_pack) as z:
                full, thumb, _ = native_image_pair(z.read('MyAssets/Media/Sample/Image.rwfile'),
                    z.read('MyAssets/Media/Sample/Image.rwmeta'), raw.getvalue())
            map_data, note, meta = control()
            map_meta = FixtureWriter({2: 'Assembly-CSharp'}).write(node('ArkenMapMeta', {'_name': (1, None, 'ControlMap')}))
            originals = {'MyAssets/Maps/Control.rwmap': map_data, 'MyAssets/Maps/Control.rwmeta': map_meta,
                'MyAssets/Encyclopedia/Notes/Control.rwnote': note,
                'MyAssets/Encyclopedia/Notes/Control.rwmeta': meta,
                'MyAssets/Media/Sample/Image.rwfile': full, 'MyAssets/Media/Sample/Image.rwmeta': thumb}
            template = root / 'template.zip'
            with zipfile.ZipFile(template, 'w') as z:
                for p, d in originals.items(): z.writestr(p, d)
            args = dict(name='Converted', units_per_grid=2.56, control_units_per_grid=2.56, control_name='Control')
            a, b = root / 'a.zip', root / 'b.zip'
            report = write_token_zip(template, companion, package, a, **args)
            write_token_zip(template, companion, package, b, **args)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(len(report['unsupported']), 3)
            self.assertEqual(len(report['tokens']), 3)
            self.assertEqual(len({t['source_id'] for t in report['tokens']}), 3)
            self.assertEqual(len({t['placement']['target'] for t in report['tokens']}), 3)
            self.assertEqual(len({t['placement']['native_uid'] for t in report['tokens']}), 3)
            with zipfile.ZipFile(a) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(json.loads(z.read('token-report.json'))['source_scene'], s)
                for p, d in originals.items(): self.assertEqual(z.read(p), d)
                for p in z.namelist():
                    if p.endswith(('.rwmap', '.rwnote', '.rwmeta', '.rwfile')):
                        graph = Reader(z.read(p), max_items=64000000).read()
                        for value in graph['objects'].values():
                            if isinstance(value, str) and value.startswith('MyAssets/') and value.endswith('.rwmeta'):
                                self.assertIn(value, z.namelist())
            with self.assertRaisesRegex(ValueError, 'distinct map'):
                write_token_zip(template, companion, package, root / 'collision.zip', **{**args, 'name': 'Control'})
            self.assertFalse((root / 'collision.zip').exists())
            # Texture traversal is rejected before producing an archive.
            s['tokens'] = [deepcopy(original)]
            s['tokens'][0]['texture']['src'] = '../escape.png'
            companion.write_text(json.dumps({'source_scene': s}))
            with self.assertRaises(ValueError):
                write_token_zip(template, companion, package, root / 'unsafe.zip', **args)
            self.assertFalse((root / 'unsafe.zip').exists())

    def test_foundry_padding_grid_center_and_retained_behavior(self):
        tokens, rejected = scene_tokens(scene())
        self.assertEqual(rejected, [])
        t = tokens[0]
        self.assertEqual(t.center, (12.5, 18.5))
        self.assertEqual(t.identity, 'Scene.scene.Token.stoker')
        self.assertEqual(t.texture_scale, (.8, .6))
        self.assertIn('flags', t.retained_only)
        s = scene(); s['dimensions'] = {'sceneX': 100, 'sceneY': 200}
        self.assertEqual(scene_tokens(s)[0][0].center, (19.5, 26.5))

    def test_refuse_geometry_without_losing_reason(self):
        for key, value in [('width', 2), ('x', float('nan')), ('hidden', 'yes')]:
            s = scene(); s['tokens'][0][key] = value
            tokens, rejected = scene_tokens(s)
            self.assertFalse(tokens); self.assertEqual(rejected[0]['status'], 'unsupported')
        s = scene(); s['tokens'][0]['texture']['scaleX'] = 1.1
        self.assertIn('scale', scene_tokens(s)[1][0]['reason'])
        s = scene(); s['tokens'] *= 2
        self.assertEqual(len(scene_tokens(s)[1]), 1)

    def test_texture_scale_changes_canvas_not_footprint(self):
        data = io.BytesIO(); Image.new('RGBA', (20, 20), 'red').save(data, 'PNG')
        image = Image.open(io.BytesIO(token_canvas(data.getvalue(), (.8, .6), 100)))
        self.assertEqual(image.size, (100, 100))
        self.assertEqual(image.getbbox(), (10, 20, 90, 80))
        self.assertEqual(image.getpixel((0, 0))[3], 0)

    def test_native_token_identity_size_duplicate_fields_and_calibration(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_pack = Path(tmp) / 'media.zip'; sample(image_pack)
            with zipfile.ZipFile(image_pack) as z:
                image, meta = [z.read('MyAssets/Media/Sample/Image' + ext) for ext in ('.rwfile', '.rwmeta')]
            raw = io.BytesIO(); Image.new('RGBA', (20, 20), 'red').save(raw, 'PNG')
            t = scene_tokens(scene())[0][0]; original, note, note_meta = control()
            args = dict(name='Test', units_per_grid=3., origin=(7., 11.), control_name='Control',
                note_control=note, note_metadata=note_meta, image_control=image, image_metadata=meta,
                control_canvas_edge=100, control_units_per_grid=2.56)
            updated, files, rows = token_files(original, [t], {t.texture: raw.getvalue()}, **args)
            self.assertEqual(token_files(original, [t], {t.texture: raw.getvalue()}, **args), (updated, files, rows))
            r = Reader(updated); r.read()
            resolve = lambda x: r.objects[x['ref']] if isinstance(x, dict) and 'ref' in x else x
            presets = [o['members'] for o in r.objects.values() if isinstance(o, dict)
                       and o.get('class') == 'ArkenTilePresetContentLink']
            old = next(p for p in presets if resolve(p['_tileName']) == 'Control')
            self.assertEqual(resolve(old['_position'])['members'], {'x': 10., 'y': -20.})
            new = next(p for p in presets if resolve(p['_tileName']) == 'Stoker')
            for prefix in ('', 'ArkenTilePresetBase+'):
                self.assertEqual(resolve(new[prefix + '_position'])['members'], {'x': 44.5, 'y': -44.5})
                self.assertAlmostEqual(resolve(new[prefix + '_scale'])['members']['x'], .6, places=5)
                self.assertEqual(new[prefix + '_rotation'], -45.)
                self.assertTrue(new[prefix + '_hidden'])
                self.assertEqual(new[prefix + '_uID'], 18)
            for path, data in files.items():
                graph = Reader(data, max_items=64000000).read()
                if path.endswith('.rwnote'):
                    self.assertTrue(any(o.get('class') == 'ArkenNoteFieldSize' and
                        abs(o['members']['_squareSizeNew'] - 3 / 2.56) < 1e-6
                        for o in graph['objects'].values() if isinstance(o, dict)))
            self.assertIn('Actual player visibility of hidden token', rows[0]['unverified'])
            self.assertEqual(rows[0]['placement']['native_position'], {'x': 44.5, 'y': -44.5})
            with self.assertRaises(ValueError):
                token_files(original, [replace(t, footprint=(1, 2))], {t.texture: raw.getvalue()}, **args)

    def test_invalid_output_or_archive_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'existing.zip'; dest.write_bytes(b'preserve')
            with self.assertRaisesRegex(ValueError, 'new output'):
                write_token_zip('absent', 'absent', 'absent', dest, name='Test', units_per_grid=1,
                    control_units_per_grid=1, control_name='Control')
            self.assertEqual(dest.read_bytes(), b'preserve')
            companion = Path(tmp) / 'source.json'; companion.write_text(json.dumps({'source_scene': scene()}))
            archive = Path(tmp) / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as z: z.writestr('MyAssets/../escape', b'no')
            dest = Path(tmp) / 'new.zip'
            with self.assertRaisesRegex(ValueError, 'native export'):
                write_token_zip(archive, companion, tmp, dest, name='Test', units_per_grid=1,
                    control_units_per_grid=1, control_name='Control')
            self.assertFalse(dest.exists())

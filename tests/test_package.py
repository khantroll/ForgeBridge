import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from forgebridge.native_export import companion_files
from forgebridge.nrbf import Reader
from forgebridge.package import build_package
from test_native_images import inputs
from test_native_export import recovered
from test_native_map import fixture, node, FixtureWriter


def map_template(root, extras=None):
    p = Path(root) / 'map.zip'
    meta = node('ArkenMapMeta', {'_mapName': (1, None, 'Original')})
    with zipfile.ZipFile(p, 'w') as z:
        z.writestr('MyAssets/Maps/Original.rwmap', fixture())
        z.writestr('MyAssets/Maps/Original.rwmeta', FixtureWriter({2: 'Assembly-CSharp'}).write(meta))
        z.writestr('MyAssets/Media/background.rwfile', b'unchanged background')
        cal_meta = node('ArkenNoteUpgradeMeta', {'_name': (1, None, 'Calibration'),
            '_map': (1, None, 'MyAssets/Maps/Original.rwmeta')})
        z.writestr('MyAssets/Encyclopedia/Notes/Cal.rwmeta',
                   FixtureWriter({2: 'Assembly-CSharp'}).write(cal_meta))
        for path, data in (extras or {}).items():
            z.writestr(path, data)
    return p


class PackageTests(unittest.TestCase):
    def test_case_aliased_export_fails_before_package_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            media, companion, _, _ = inputs(tmp)
            template = map_template(tmp, {'MyAssets/Media/Background.rwfile': b'unchanged background'})
            original = template.read_bytes()
            out = root / 'must-not-exist.zip'
            with self.assertRaisesRegex(ValueError, 'Case-conflicting'):
                build_package(companion, template, media, out, name='Alias test',
                    note_folder='Notes', units_per_grid=2.56, package=root/'package')
            self.assertFalse(out.exists())
            self.assertEqual(template.read_bytes(), original)

    def test_combined_scene_contains_multiple_tokens_and_explicit_partial_rejections(self):
        from copy import deepcopy
        from PIL import Image
        from test_tokens import control, scene
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            media, companion, _, source = inputs(tmp)
            package = root / 'package'
            Image.new('RGBA', (40, 40), 'red').save(package / 'token.png')
            s = scene()
            first = s['tokens'][0]
            s['tokens'] = []
            for i, size in enumerate((1., 2., .5)):
                t = deepcopy(first)
                t.update(_id='t' + str(i), name='Token ' + str(i), width=size, height=size,
                         x=900 + 200*i, y=1200, rotation=90*i, hidden=i == 2)
                s['tokens'].append(t)
            bad = deepcopy(first); bad.update(_id='rect', width=2)
            missing = deepcopy(first); missing['_id'] = 'missing'; missing['texture']['src'] = 'absent.png'
            s['tokens'].extend([bad, missing, deepcopy(s['tokens'][0])])
            source['source_scene'] = s
            companion.write_text(json.dumps(source))
            map_data, note, meta = control()
            with zipfile.ZipFile(media) as z:
                image_files = {n:z.read(n) for n in z.namelist() if n.startswith('MyAssets/')}
            from forgebridge.native_images import native_image_pair
            full, thumb, _ = native_image_pair(image_files['MyAssets/Media/Sample/Image.rwfile'],
                image_files['MyAssets/Media/Sample/Image.rwmeta'], (package/'token.png').read_bytes())
            image_files['MyAssets/Media/Sample/Image.rwfile'] = full
            image_files['MyAssets/Media/Sample/Image.rwmeta'] = thumb
            control_files = {'MyAssets/Maps/TokenControl.rwmap': map_data,
                'MyAssets/Maps/TokenControl.rwmeta': FixtureWriter({2:'Assembly-CSharp'}).write(
                    node('ArkenMapMeta', {'_name': (1,None,'TokenControl')})),
                'MyAssets/Encyclopedia/Notes/Control.rwnote': note,
                'MyAssets/Encyclopedia/Notes/Control.rwmeta': meta, **image_files}
            controls = root / 'controls.zip'
            with zipfile.ZipFile(controls, 'w') as z:
                for p,d in control_files.items(): z.writestr(p,d)
            out = root / 'combined.zip'
            report = build_package(companion, map_template(tmp), media, out, name='All in one',
                note_folder='Scene', units_per_grid=3., origin=(7.,11.), package=package,
                token_control_pack=controls, token_control_name='Control', control_units_per_grid=2.56)
            self.assertEqual(report['counts']['native_tokens'], 3)
            self.assertEqual(report['counts']['unsupported_tokens'], 3)
            with zipfile.ZipFile(out) as z:
                self.assertEqual(json.loads(z.read('token-report.json'))['source_scene'], s)
                for p,d in control_files.items(): self.assertEqual(z.read(p),d)
                r=Reader(z.read('MyAssets/Maps/All in one.rwmap')); r.read()
                resolve=lambda v:r.objects[v['ref']] if isinstance(v,dict) and 'ref' in v else v
                root_map=r.objects[r.root_id]['members'] if hasattr(r,'root_id') else r.objects[1]['members']
                tiles=resolve(root_map['_tiles'])['members']
                presets=[resolve(resolve(v)['members']['_tileInfo']) for v in
                         resolve(tiles['_items'])['items'][:tiles['_size']]]
                self.assertEqual(len(presets),6)  # original wall/calibration + room marker + 3 tokens
                self.assertEqual(len({p['members']['_uID'] for p in presets}),6)
                converted=[p['members'] for p in presets if resolve(p['members'].get('_tileName')) in
                           ('Token 0','Token 1','Token 2')]
                self.assertEqual(len({resolve(p['_contentBasePath']) for p in converted}),3)
                for i,p in enumerate(converted):
                    self.assertEqual(resolve(p['_position'])['members'],
                        {'x':7+((900+200*i-800)/100+(1.,2.,.5)[i]/2)*3,
                         'y':11-(2+(1.,2.,.5)[i]/2)*3})
                    self.assertEqual(p['_rotation'],-90*i)
                    self.assertEqual(p['_hidden'],i==2)
            # Refuse a missing original native backlink before writing partial output.
            broken=root/'broken.zip'
            with zipfile.ZipFile(map_template(tmp)) as z, zipfile.ZipFile(broken,'w') as b:
                for n in z.namelist():
                    if not n.endswith('Cal.rwmeta'): b.writestr(n,z.read(n))
            with self.assertRaisesRegex(ValueError,'Missing native dependency'):
                build_package(companion,broken,media,root/'absent.zip',name='Broken',
                    note_folder='Scene',units_per_grid=3.,package=package)
            self.assertFalse((root/'absent.zip').exists())

    def test_one_package_collects_media_and_closes_map_and_note_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            media, companion, _, source = inputs(tmp)
            template = map_template(tmp)
            out = Path(tmp) / 'complete.zip'
            report = build_package(companion, template, media, out, name='Readable map',
                note_folder='Readable notes', units_per_grid=2.56, package=Path(tmp) / 'package')
            self.assertEqual(report['native_map']['markers'], 1)
            self.assertEqual(report['native_map']['marker_labels'], 'off')
            self.assertEqual(report['counts']['native_image_attachments'], 3)
            with zipfile.ZipFile(out) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(z.read('MyAssets/Media/background.rwfile'), b'unchanged background')
                self.assertEqual(json.loads(z.read('source-companion.json')), source)
                self.assertIn('handout-report.json', z.namelist())
                note_strings = recovered({p: z.read(p) for p in z.namelist()
                                          if p.endswith('.rwnote')})[0]
                self.assertTrue(any('Room markers are supplied in the separate native map copy.' in s
                                    for s in note_strings))
                self.assertFalse(any('Map markers are not placed automatically.' in s
                                     for s in note_strings))
                for p in report['placements']:
                    self.assertTrue(p['native_map_placement'])
                    self.assertIn(p['target'], z.namelist())
                for a in report['attached_media']:
                    self.assertIn(a['target'], z.namelist())
                r = Reader(z.read('MyAssets/Maps/Readable map.rwmap'));r.read()
                self.assertTrue(any(o == report['placements'][0]['target'] for o in r.objects.values()))
            before = out.read_bytes()
            with self.assertRaisesRegex(ValueError, 'new output'):
                build_package(companion, template, media, out, name='Readable map',
                    note_folder='Readable notes', units_per_grid=2.56, package=Path(tmp) / 'package')
            self.assertEqual(out.read_bytes(), before)

    def test_existing_exported_notes_need_explicit_regeneration(self):
        with tempfile.TemporaryDirectory() as tmp:
            media, companion, bundle, source = inputs(tmp)
            notes, _ = companion_files(source, note_folder='Readable notes')
            preserved = {p: b for p, b in notes.items() if p.endswith(('.rwnote', '.rwmeta'))}
            template = map_template(tmp, preserved)
            out = Path(tmp) / 'complete.zip'
            kwargs = dict(name='Copy', note_folder='Readable notes', units_per_grid=2.56, media_bundle=bundle)
            with self.assertRaisesRegex(ValueError, 'regenerate-notes'):
                build_package(companion, template, media, out, **kwargs)
            self.assertFalse(out.exists())
            report = build_package(companion, template, media, out, regenerate_notes=True, **kwargs)
            self.assertEqual(set(report['regenerated_exported_note_files']), set(preserved))
            self.assertEqual(report['counts']['native_image_attachments'], 3)

    def test_wrong_media_bundle_fails_without_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            media, companion, bundle, source = inputs(tmp)
            source['scene_id'] = 'other-scene';companion.write_text(json.dumps(source))
            out = Path(tmp) / 'complete.zip'
            with self.assertRaisesRegex(ValueError, 'different scene'):
                build_package(companion, map_template(tmp), media, out, name='Copy',
                    note_folder='Readable notes', units_per_grid=2.56, media_bundle=bundle)
            self.assertFalse(out.exists())

    def test_conflicting_exported_media_is_not_silently_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            media, companion, bundle, _ = inputs(tmp)
            template = map_template(tmp)
            kwargs = dict(name='Copy', note_folder='Readable notes', units_per_grid=2.56, media_bundle=bundle)
            first = Path(tmp) / 'first.zip'
            report = build_package(companion, template, media, first, **kwargs)
            target = report['attached_media'][0]['target']
            template = map_template(tmp, {target: b'conflicting user asset'})
            out = Path(tmp) / 'conflict.zip'
            with self.assertRaisesRegex(ValueError, 'conflicts'):
                build_package(companion, template, media, out, **kwargs)
            self.assertFalse(out.exists())

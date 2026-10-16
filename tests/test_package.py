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
        for path, data in (extras or {}).items():
            z.writestr(path, data)
    return p


class PackageTests(unittest.TestCase):
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

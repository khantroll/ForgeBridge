from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from forgebridge.cli import main
from forgebridge.convert import convert
from forgebridge.native_dependencies import read_package, check_metadata_references
from forgebridge.nrbf import Reader
from forgebridge.installer import uninstall

FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'


class DirectPackageTests(unittest.TestCase):
    def fixture(self, root, empty=False):
        package = root / 'source'; shutil.copytree(FIXTURE, package)
        path = package / 'packs/scenes.db'; scene = json.loads(path.read_text())
        if empty:
            scene.update(tokens=[], notes=[])
            manifest = json.loads((package / 'module.json').read_text())
            manifest['packs'] = [p for p in manifest['packs'] if p['type'] == 'Scene']
            (package / 'module.json').write_text(json.dumps(manifest))
        else:
            scene['notes'][0].update(x=100, y=100)
            token = {'_id': 'one', 'name': 'Same readable name', 'x': 20, 'y': 40,
                     'width': 1, 'height': 1, 'texture': {'src': 'assets/crypt.png'},
                     'rotation': 90, 'hidden': True, 'actorId': 'actor-retained'}
            second = deepcopy(token); second.update(_id='two', x=100, rotation=180, hidden=False)
            bad = deepcopy(token); bad.update(_id='bad', height=2)
            scene['tokens'] = [token, second, bad]
        path.write_text(json.dumps(scene))
        return package, scene

    def test_synthesized_map_contains_geometry_thumbnail_notes_markers_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package, scene = self.fixture(root)
            report = convert(package, root / 'out')
            self.assertEqual(report['status'], 'PASS')
            result = report['scenes'][0]['native_report']
            self.assertEqual(result['counts']['native_tokens'], 2)
            self.assertEqual(result['counts']['unsupported_tokens'], 1)
            self.assertEqual(result['native_map']['markers'], 1)
            self.assertEqual(result['native_map']['units_per_grid'], 2.56)
            self.assertEqual(result['native_map']['origin'], [0., 0.])
            self.assertAlmostEqual(result['token_conversion']['tokens'][0]['placement']['native_position']['x'], 1.792)
            files = read_package(root / 'out/scene-001/native-package.zip')
            maps = [n for n in files if n.endswith('.rwmap')]
            self.assertEqual(len(maps), 1)
            self.assertFalse(any('GeneratedControls/' in n or '_ForgeBridgeSchema' in n for n in files))
            self.assertGreater(check_metadata_references(files), 0)
            reader = Reader(files[maps[0][:-6] + '.rwmeta']); graph = reader.read()
            self.assertIsNotNone(reader.objects[graph['root_id']]['members']['_thumbnail'])
            self.assertEqual(json.loads(files['source-companion.json'])['source_scene'], scene)
            for name, data in files.items():
                if name.startswith('MyAssets/'):
                    self.assertEqual((root / 'out' / name).read_bytes(), data)

    def test_zero_token_no_journal_scene_still_builds_native_map_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package, _ = self.fixture(root, empty=True)
            report = convert(package, root / 'out')
            self.assertEqual(report['status'], 'PASS')
            native = report['scenes'][0]['native_report']
            self.assertEqual(native['counts']['native_tokens'], 0)
            self.assertEqual(native['native_map']['markers'], 0)
            self.assertEqual(native['counts']['notes'], 1)

    def test_identical_scene_ids_in_identical_adventures_get_distinct_native_scopes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package, scene = self.fixture(root)
            (package / 'packs/adventure.db').write_text('\n'.join(json.dumps({'_id': identity, 'scenes': [scene]}) for identity in ('A', 'B')))
            manifest = json.loads((package / 'module.json').read_text())
            manifest['packs'] = [{'name': 'adventure', 'type': 'Adventure', 'path': 'packs/adventure.db'}]
            (package / 'module.json').write_text(json.dumps(manifest))
            report = convert(package, root / 'out')
            self.assertEqual(report['status'], 'PASS')
            self.assertEqual(len(report['scenes']), 2)
            scopes = [s['native_report']['native_synthesis']['scope'] for s in report['scenes']]
            self.assertEqual(len(set(scopes)), 2)
            self.assertEqual(len(list((root / 'out/MyAssets/Maps').rglob('*.rwmap'))), 2)

    def test_convert_install_uses_add_only_backend_with_fake_myassets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package, _ = self.fixture(root)
            assets = root / 'MyAssets'; assets.mkdir(); (assets / 'user.txt').write_text('keep')
            backups = root / 'Backups'; backups.mkdir()
            with patch('forgebridge.installer.require_toolkit_closed'), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(['convert', str(package), '--out', str(root / 'out'), '--install',
                                       '--myassets', str(assets), '--backup-root', str(backups)]), 0)
            result = json.loads(output.getvalue()); self.assertTrue(result['installed'])
            self.assertEqual((assets / 'user.txt').read_text(), 'keep')
            self.assertTrue((root / 'out/installation-report.json').is_file())
            with patch('forgebridge.installer.require_toolkit_closed'):
                uninstall(result['installation']['receipt'])
            self.assertEqual([p.relative_to(assets).as_posix() for p in assets.rglob('*') if p.is_file()], ['user.txt'])

    def test_flat_zip_with_module_qualified_background_and_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package, scene = self.fixture(root)
            qualified = 'modules/synthetic-module/assets/crypt.png'
            scene['img'] = qualified; scene['levels'][0]['background']['src'] = qualified
            for token in scene['tokens']: token['texture']['src'] = qualified
            (package / 'packs/scenes.db').write_text(json.dumps(scene))
            archive_path = root / 'flat.zip'
            with zipfile.ZipFile(archive_path, 'w') as archive:
                for file in package.rglob('*'):
                    if file.is_file(): archive.write(file, file.relative_to(package).as_posix())
            report = convert(archive_path, root / 'out')
            self.assertEqual(report['status'], 'PASS')
            self.assertEqual(report['scenes'][0]['native_report']['counts']['native_tokens'], 2)

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from forgebridge.cli import main
from forgebridge.convert import discover, convert
from forgebridge.gui import native_outputs, install_outputs, report_text


class GuiControllerTests(unittest.TestCase):
    def test_summary_distinguishes_manual_source_losses_from_native_output(self):
        text = report_text({'status': 'PASS', 'counts': {'unsupported': 3},
            'scenes': [{'id': 'a', 'name': 'Room', 'status': 'MANUAL', 'folder': 'scene-001',
                        'artifact': 'uvtt-package.zip'}], 'manual_steps': ['Import UVTT in Toolkit']})
        self.assertIn('Source/UVTT stage: unsupported: 3', text)
        self.assertIn('Room: MANUAL', text)
        self.assertIn('Import UVTT', text)
        self.assertIn('does not prove Toolkit', text)
    def test_help_requires_no_desktop_or_tk_window(self):
        with redirect_stdout(io.StringIO()) as text, self.assertRaises(SystemExit) as stopped:
            main(['gui', '--help'])
        self.assertEqual(stopped.exception.code, 0)
        self.assertIn('local Tk front end', text.getvalue())

    def test_only_complete_native_outputs_reach_installer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root / 'scene-001'; folder.mkdir()
            package = folder / 'native-package.zip'; package.write_bytes(b'test placeholder')
            manual = {'status': 'PASS', 'scenes': [{'status': 'MANUAL', 'folder': 'scene-001', 'artifact': 'uvtt-package.zip'}]}
            with patch('forgebridge.gui.install') as installer:
                with self.assertRaisesRegex(ValueError, 'No native packages'):
                    install_outputs(manual, root, 'MyAssets', 'Backups')
                installer.assert_not_called()
                report = {'status': 'PASS', 'scenes': [{'status': 'BUILT', 'folder': 'scene-001', 'artifact': 'native-package.zip'}]}
                install_outputs(report, root, 'MyAssets', 'Backups')
                installer.assert_called_once_with([package], 'MyAssets', 'Backups')
            report['status'] = 'PARTIAL'
            with self.assertRaisesRegex(ValueError, 'rejected scenes'): native_outputs(report, root)
            report['status'] = 'PASS'; report['scenes'][0]['folder'] = '../outside'
            with self.assertRaisesRegex(ValueError, 'outside'): native_outputs(report, root)

    def test_scoped_selection_does_not_merge_identical_ids_in_two_adventures(self):
        fixture = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root / 'source'
            shutil.copytree(fixture, package)
            scene = json.loads((package / 'packs/scenes.db').read_text())
            a, b = deepcopy(scene), deepcopy(scene)
            a['name'], b['name'] = 'Adventure A scene', 'Adventure B scene'
            (package / 'packs/adventures.db').write_text('\n'.join(json.dumps({'_id': identity, 'scenes': [s]})
                for identity, s in [('adv-A', a), ('adv-B', b)]))
            manifest = json.loads((package / 'module.json').read_text())
            manifest['packs'] = [{'name': 'adventures', 'path': 'packs/adventures.db', 'type': 'Adventure'}]
            (package / 'module.json').write_text(json.dumps(manifest))
            scenes = discover(package)['scenes']
            self.assertEqual(len(scenes), 2)
            self.assertEqual(scenes[0]['id'], scenes[1]['id'])
            self.assertNotEqual(scenes[0]['key'], scenes[1]['key'])
            selected = next(row for row in scenes if row['parent_adventure_id'] == 'adv-B')
            report = convert(package, root / 'out', scene_keys=[selected['key']])
            self.assertEqual(len(report['scenes']), 1)
            self.assertEqual(report['scenes'][0]['name'], 'Adventure B scene')
            self.assertEqual(report['scenes'][0]['parent_adventure_id'], 'adv-B')

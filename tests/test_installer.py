import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from forgebridge.installer import install, uninstall, require_toolkit_closed
from test_native_capture import record
from test_scene_profile import archive


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.closed = patch('forgebridge.installer.require_toolkit_closed')
        self.check = self.closed.start(); self.addCleanup(self.closed.stop)

    def inputs(self, root):
        target = root / 'MyAssets'; target.mkdir()
        (target / 'Maps').mkdir(); (target / 'Maps/Existing.rwmap').write_bytes(record())
        (target / 'user.txt').write_bytes(b'original user notes')
        (target / 'empty').mkdir()
        backups = root / 'Backups'; backups.mkdir()
        package = root / 'scene.zip'
        archive(package, {'MyAssets/Maps/Existing.rwmap': record(),
                          'MyAssets/Maps/New.rwmap': record('new'), 'conversion-report.json': b'{}'})
        return target, backups, package

    def test_add_only_full_backup_and_uninstall_preserve_every_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            result = install([package], target, backups)
            self.assertEqual(result['added'], 1)
            receipt = json.loads(Path(result['receipt']).read_text())
            self.assertEqual([r['path'] for r in receipt['added']], ['MyAssets/Maps/New.rwmap'])
            backup = Path(result['backup'])
            self.assertEqual((backup / 'user.txt').read_bytes(), b'original user notes')
            self.assertTrue((backup / 'empty').is_dir())
            self.assertFalse((target / 'conversion-report.json').exists())
            (target / 'later-user-file.txt').write_bytes(b'keep')
            removed = uninstall(result['receipt'])
            self.assertEqual(removed['removed'], 1)
            self.assertFalse((target / 'Maps/New.rwmap').exists())
            self.assertEqual((target / 'Maps/Existing.rwmap').read_bytes(), record())
            self.assertEqual((target / 'later-user-file.txt').read_bytes(), b'keep')
            self.assertTrue(backup.exists())

    def test_conflict_and_running_toolkit_refuse_without_backup_or_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            self.check.side_effect = ValueError('Toolkit is running')
            with self.assertRaisesRegex(ValueError, 'running'): install([package], target, backups)
            self.assertEqual(list(backups.iterdir()), [])
            self.check.side_effect = None
            (target / 'Maps/New.rwmap').write_bytes(b'user-edited')
            with self.assertRaisesRegex(ValueError, 'conflicts'): install([package], target, backups)
            self.assertEqual((target / 'Maps/New.rwmap').read_bytes(), b'user-edited')
            self.assertEqual(list(backups.iterdir()), [])

    def test_modified_added_file_blocks_uninstall_before_any_deletion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            result = install([package], target, backups)
            (target / 'Maps/New.rwmap').write_bytes(b'new manual edits')
            with self.assertRaisesRegex(ValueError, 'changed/missing'): uninstall(result['receipt'])
            self.assertEqual((target / 'Maps/New.rwmap').read_bytes(), b'new manual edits')
            self.assertTrue((target / 'Maps/Existing.rwmap').exists())

    def test_case_alias_backup_overlap_and_existing_lock_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            with self.assertRaisesRegex(ValueError, 'separate trees'): install([package], target, target)
            (root / '.forgebridge-install.lock').write_text('other install')
            with self.assertRaises(FileExistsError): install([package], target, backups)
            self.assertEqual((root / '.forgebridge-install.lock').read_text(), 'other install')
            self.assertFalse((target / 'Maps/New.rwmap').exists())

    def test_receipt_cannot_delete_preexisting_or_escaping_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            result = install([package], target, backups)
            manifest = Path(result['receipt']); receipt = json.loads(manifest.read_text())
            receipt['added'][0]['path'] = 'MyAssets/Maps/Existing.rwmap'
            manifest.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'pre-existing'): uninstall(manifest)
            self.assertTrue((target / 'Maps/Existing.rwmap').exists())
            receipt['added'][0]['path'] = 'MyAssets/../outside'
            manifest.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'Unsafe'): uninstall(manifest)

    def test_backup_failure_never_copies_new_assets_and_releases_owned_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            with patch('forgebridge.installer._tree', side_effect=ValueError('unsafe tree')):
                with self.assertRaisesRegex(ValueError, 'unsafe tree'): install([package], target, backups)
            self.assertFalse((target / 'Maps/New.rwmap').exists())
            self.assertFalse((root / '.forgebridge-install.lock').exists())

    def test_process_detection_and_failure_are_fail_closed(self):
        self.closed.stop()
        # Match both spellings; Linux and Windows response parsing are exercised.
        result = subprocess.CompletedProcess([], 0, stdout='MastersToolkit.exe\n', stderr='')
        with patch('forgebridge.installer.subprocess.run', return_value=result):
            with self.assertRaisesRegex(ValueError, 'running'): require_toolkit_closed()
        with patch('forgebridge.installer.subprocess.run', side_effect=OSError('inspection denied')):
            with self.assertRaisesRegex(ValueError, 'Cannot verify'): require_toolkit_closed()

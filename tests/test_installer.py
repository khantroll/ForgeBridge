import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from forgebridge.installer import install, uninstall, require_toolkit_closed, main
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

    def test_missing_backup_folder_is_created_only_under_existing_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            backups.rmdir()
            result = install([package], target, backups)
            self.assertTrue(backups.is_dir())
            self.assertTrue(Path(result['backup']).is_relative_to(backups))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            deep = root / 'missing-parent' / 'Backups'
            with self.assertRaisesRegex(ValueError, 'parent folder exists'):
                install([package], target, deep)
            self.assertFalse((root / 'missing-parent').exists())

    def test_modified_added_file_blocks_uninstall_before_any_deletion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            result = install([package], target, backups)
            (target / 'Maps/New.rwmap').write_bytes(b'new manual edits')
            with self.assertRaisesRegex(ValueError, 'changed/missing'): uninstall(result['receipt'])
            self.assertEqual((target / 'Maps/New.rwmap').read_bytes(), b'new manual edits')
            self.assertTrue((target / 'Maps/Existing.rwmap').exists())

    def test_refused_uninstall_cli_exits_1_with_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            result = install([package], target, backups)
            (target / 'Maps/New.rwmap').write_bytes(b'opened in Toolkit')
            with patch('sys.stderr') as err, self.assertRaises(SystemExit) as stop:
                main(['--uninstall', result['receipt']])
            self.assertEqual(stop.exception.code, 1)
            self.assertIn('--keep-changed', ''.join(c.args[0] for c in err.write.call_args_list))
            self.assertEqual((target / 'Maps/New.rwmap').read_bytes(), b'opened in Toolkit')

    def test_keep_changed_removes_only_unchanged_added_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups = self.inputs(root)[:2]
            package = root / 'two.zip'
            archive(package, {'MyAssets/Maps/A.rwmap': record('a'), 'MyAssets/Maps/B.rwmap': record('b'),
                              'conversion-report.json': b'{}'})
            result = install([package], target, backups)
            (target / 'Maps/B.rwmap').write_bytes(b'note edited by user')
            out = uninstall(result['receipt'], keep_changed=True)
            self.assertEqual((out['removed'], out['kept_changed']), (1, ['MyAssets/Maps/B.rwmap']))
            self.assertFalse((target / 'Maps/A.rwmap').exists())
            self.assertEqual((target / 'Maps/B.rwmap').read_bytes(), b'note edited by user')
            self.assertTrue((target / 'Maps/Existing.rwmap').exists())
            self.assertEqual((target / 'user.txt').read_bytes(), b'original user notes')
            receipt = json.loads(Path(result['receipt']).read_text())
            self.assertEqual(receipt['state'], 'UNINSTALLED_KEPT_CHANGED')
            again = uninstall(result['receipt'])  # already uninstalled: folders only, never files
            self.assertEqual((again['removed'], again['already_uninstalled']), (0, True))
            self.assertEqual((target / 'Maps/B.rwmap').read_bytes(), b'note edited by user')

    def test_uninstall_removes_only_created_folders_that_are_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups = self.inputs(root)[:2]
            package = root / 'nested.zip'
            archive(package, {'MyAssets/Maps/New Set/A.rwmap': record('a'),
                              'MyAssets/Encyclopedia/Notes/New Set/N1.rwnote': record('n1'),
                              'MyAssets/Encyclopedia/Notes/New Set/N2.rwnote': record('n2'),
                              'conversion-report.json': b'{}'})
            result = install([package], target, backups)
            (target / 'Encyclopedia/Notes/New Set/N2.rwnote').write_bytes(b'opened in Toolkit')
            out = uninstall(result['receipt'], keep_changed=True)
            self.assertFalse((target / 'Maps/New Set').exists())
            self.assertTrue((target / 'Encyclopedia/Notes/New Set/N2.rwnote').exists())  # kept file keeps its folder
            self.assertTrue((target / 'Maps').is_dir())  # pre-existing folder untouched
            self.assertTrue((target / 'empty').is_dir())  # pre-existing empty folder untouched
            self.assertGreaterEqual(out['removed_empty_folders'], 1)
            self.assertNotIn('Encyclopedia/Notes/New Set', json.loads(Path(result['receipt']).read_text())['removed_directories'])

    def test_rerun_on_old_receipt_tidies_folders_and_never_deletes_reinstalled_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups = self.inputs(root)[:2]
            package = root / 'nested.zip'
            archive(package, {'MyAssets/Maps/New Set/A.rwmap': record('a'), 'conversion-report.json': b'{}'})
            first = install([package], target, backups)
            receipt = Path(first['receipt']); data = json.loads(receipt.read_text())
            uninstall(receipt)
            # Simulate an older receipt that left its folder behind, then a reinstall of the same content.
            data['state'] = 'UNINSTALLED'; receipt.write_text(json.dumps(data))
            (target / 'Maps/New Set').mkdir()
            out = uninstall(receipt)
            self.assertEqual((out['removed'], out['removed_empty_folders']), (0, 1))
            self.assertFalse((target / 'Maps/New Set').exists())
            install([package], target, backups)
            self.assertEqual(uninstall(receipt)['removed'], 0)
            self.assertTrue((target / 'Maps/New Set/A.rwmap').exists())

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

    def test_uvtt_only_or_unknown_asset_package_is_not_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target, backups, package = self.inputs(root)
            for files in ({'scene.uvtt': b'{}'}, {'MyAssets/script.js': b'do not run'}):
                archive(package, files)
                with self.assertRaisesRegex(ValueError, 'native scene package'):
                    install([package], target, backups)
            self.assertEqual(list(backups.iterdir()), [])

    def test_process_detection_and_failure_are_fail_closed(self):
        self.closed.stop()
        # Match both spellings; Linux and Windows response parsing are exercised.
        result = subprocess.CompletedProcess([], 0, stdout='MastersToolkit.exe\n', stderr='')
        with patch('forgebridge.installer.subprocess.run', return_value=result):
            with self.assertRaisesRegex(ValueError, 'running'): require_toolkit_closed()
        with patch('forgebridge.installer.subprocess.run', side_effect=OSError('inspection denied')):
            with self.assertRaisesRegex(ValueError, 'Cannot verify'): require_toolkit_closed()

    def test_windows_guard_filters_only_candidates_and_still_refuses_unknown_state(self):
        self.closed.stop()
        windows = SimpleNamespace(name='nt', environ={'SystemRoot': 'C:/Windows'})
        with patch('forgebridge.installer.os', windows):
            for name in ('MastersToolkit.exe', 'MasterToolkit.exe'):
                result = subprocess.CompletedProcess([], 0, stdout=f'"{name}","123","Console","1","1 K"\n')
                with patch('forgebridge.installer.subprocess.run', return_value=result) as query:
                    with self.assertRaisesRegex(ValueError, 'running'): require_toolkit_closed()
                    self.assertEqual(query.call_args.args[0],
                        ['tasklist', '/FI', 'IMAGENAME eq Master*', '/FO', 'CSV', '/NH'])
                    self.assertEqual(query.call_args.kwargs['timeout'], 15)
            absent = subprocess.CompletedProcess([], 0, stdout='INFO: No tasks are running which match the specified criteria.\n')
            with patch('forgebridge.installer.subprocess.run', return_value=absent): require_toolkit_closed()
            with patch('forgebridge.installer.subprocess.run', side_effect=subprocess.TimeoutExpired('tasklist', 15)):
                with self.assertRaisesRegex(ValueError, 'Cannot verify'): require_toolkit_closed()
            with patch('forgebridge.installer.subprocess.run', return_value=subprocess.CompletedProcess([], 0, stdout='')):
                with self.assertRaisesRegex(ValueError, 'Empty process inventory'): require_toolkit_closed()

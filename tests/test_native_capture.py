from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile
import sys
from types import SimpleNamespace
from unittest.mock import patch

from forgebridge.native_capture import capture, portable_profile, capture_saved, safe_name
from forgebridge.native_capture import _toolkit_closed
from forgebridge.scene_profile import load_profile, preflight_profile
from forgebridge.uvtt import _load_leveldb_scene
from forgebridge.validate import InventoryFatal
from test_native_map import FixtureWriter, node
from test_scene_profile import setup_profiles, archive, contents


def record(ref=''):
    return FixtureWriter({2: 'Assembly-CSharp'}).write(node('Fixture', {'ref': (1, None, ref)}))


class NativeCaptureTests(unittest.TestCase):
    def test_split_exports_deduplicate_cycles_and_record_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = 'MyAssets/Maps/A.rwmap'
            shared = 'MyAssets/Notes/Shared.rwmeta'
            note = 'MyAssets/Notes/Shared.rwnote'
            common = {shared: record(note), note: record(primary)}
            first = {primary: record(shared), 'MyAssets/Maps/A.rwmeta': record(), **common}
            second = {**common, 'MyAssets/Notes/Unrelated.rwnote': record()}
            archive(root/'map.zip', first)
            archive(root/'dependencies.zip', second)
            originals = {p: p.read_bytes() for p in (root/'map.zip', root/'dependencies.zip')}
            report = capture(originals, root/'out')
            self.assertEqual(contents(root/'out/native.zip'), first)
            self.assertEqual(len(report['files']), len(first))
            self.assertEqual(len(report['inputs']), 2)
            self.assertIn({'from': note, 'to': primary}, report['dependencies'])
            self.assertEqual({p: p.read_bytes() for p in originals}, originals)
            alias = {'MyAssets/Notes/shared.rwmeta': common[shared]}
            archive(root/'alias.zip', alias)
            with self.assertRaisesRegex(ValueError, 'Case-conflicting'):
                capture([root/'map.zip', root/'alias.zip'], root/'rejected')
            self.assertFalse((root/'rejected').exists())
            self.assertEqual(contents(root/'out/native.zip'), first)

    def test_unknown_native_reference_is_not_silently_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = 'MyAssets/Media/unsupported.png'
            files = {'MyAssets/Maps/A.rwmap': record(reference),
                     'MyAssets/Maps/A.rwmeta': record()}
            archive(root/'in.zip', files)
            original = (root/'in.zip').read_bytes()
            with self.assertRaisesRegex(ValueError, 'Unsupported native dependency in MyAssets/Maps/A.rwmap'):
                capture([root/'in.zip'], root/'out')
            self.assertFalse((root/'out').exists())
            self.assertEqual((root/'in.zip').read_bytes(), original)
            assets = root/'MyAssets'
            (assets/'Maps').mkdir(parents=True)
            for name, data in files.items():
                (root/name).write_bytes(data)
            with patch('forgebridge.native_capture._toolkit_closed'):
                with self.assertRaisesRegex(ValueError, 'unsupported.png'):
                    capture_saved(assets, 'MyAssets/Maps/A.rwmap', root/'saved', True)
            self.assertFalse((root/'saved').exists())
            unsafe = 'MyAssets/../escape.png'
            files['MyAssets/Maps/A.rwmap'] = record(unsafe)
            archive(root/'unsafe.zip', files)
            with self.assertRaisesRegex(ValueError, 'Unsafe native path'):
                capture([root/'unsafe.zip'], root/'unsafe-out')

    def test_saved_snapshot_requires_closed_and_preserves_bytes(self):
        probe = SimpleNamespace(Error=RuntimeError)
        with patch('forgebridge.native_capture.os.name', 'nt'), patch.dict(sys.modules, {'psutil': probe}):
            probe.process_iter = lambda attrs: [SimpleNamespace(info={'name': 'MastersToolkit.exe'})]
            with self.assertRaisesRegex(ValueError, 'Close Toolkit'):
                _toolkit_closed()
            probe.process_iter = lambda attrs: [SimpleNamespace(info={'name': None})]
            with self.assertRaisesRegex(ValueError, 'Incomplete'):
                _toolkit_closed()
            probe.process_iter = lambda attrs: [SimpleNamespace(info={'name': 'ordinary.exe'})]
            _toolkit_closed()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root/'MyAssets'
            (assets/'Maps').mkdir(parents=True)
            data = record()
            for ext in ('.rwmap', '.rwmeta'):
                (assets/'Maps'/('A'+ext)).write_bytes(data)
            with self.assertRaisesRegex(ValueError, 'acknowledgement'):
                capture_saved(assets, 'MyAssets/Maps/A.rwmap', root/'out')
            with patch('forgebridge.native_capture._toolkit_closed', side_effect=ValueError('Toolkit running')):
                with self.assertRaisesRegex(ValueError, 'running'):
                    capture_saved(assets, 'MyAssets/Maps/A.rwmap', root/'out', True)
            with patch('forgebridge.native_capture._toolkit_closed') as closed:
                capture_saved(assets, 'MyAssets/Maps/A.rwmap', root/'out', True)
                self.assertEqual(closed.call_count, 3)
            self.assertEqual(contents(root/'out/native.zip')['MyAssets/Maps/A.rwmap'], data)

    def test_closure_bytes_and_determinism(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {'MyAssets/Maps/A.rwmap': record('MyAssets/Media/B.rwmeta'),
                     'MyAssets/Maps/A.rwmeta': record(),
                     'MyAssets/Media/B.rwmeta': record(),
                     'MyAssets/Media/B.rwfile': record(),
                     'MyAssets/Maps/Unrelated.rwmap': record()}
            archive(root/'in.zip', files)
            a = capture([root/'in.zip'], root/'a', 'MyAssets/Maps/A.rwmap')
            b = capture([root/'in.zip'], root/'b', 'MyAssets/Maps/A.rwmap')
            expected = {n:d for n,d in files.items() if 'Unrelated' not in n}
            self.assertEqual(contents(root/'a/native.zip'), expected)
            self.assertEqual(a['bundle_sha256'], b['bundle_sha256'])
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                capture([root/'in.zip'], root/'a', 'MyAssets/Maps/A.rwmap')
            self.assertEqual(contents(root/'a/native.zip'), expected)

    def test_missing_conflict_and_unsafe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {'MyAssets/Maps/A.rwmap': record('MyAssets/Missing.rwmeta'),
                     'MyAssets/Maps/A.rwmeta': record()}
            archive(root/'a.zip', files)
            with self.assertRaisesRegex(ValueError, 'Missing'):
                capture([root/'a.zip'], root/'out')
            self.assertFalse((root/'out').exists())
            archive(root/'b.zip', {'MyAssets/Maps/A.rwmap': record('different')})
            with self.assertRaisesRegex(ValueError, 'conflicts'):
                capture([root/'a.zip', root/'b.zip'], root/'out')
            archive(root/'alias.zip', {'MyAssets/Maps/A.rwmap': record(),
                                      'MyAssets/Maps/a.rwmap': record()})
            with self.assertRaisesRegex(ValueError, 'Case-conflicting'):
                capture([root/'alias.zip'], root/'out')
            unsafe = 'MyAssets' + chr(92) + '..' + chr(92) + 'outside.rwmeta'
            archive(root/'unsafe.zip', {'MyAssets/Maps/A.rwmap': record(unsafe),
                                       'MyAssets/Maps/A.rwmeta': record()})
            with self.assertRaisesRegex(ValueError, 'Unsafe native path'):
                capture([root/'unsafe.zip'], root/'out')
        for name in ('MyAssets/../escape', 'MyAssets/CON.rwmap', 'MyAssets/A./x',
                     'MyAssets//x', 'MyAssets/./x', 'MyAssets/C:/x'):
            with self.assertRaises(ValueError):
                safe_name(name)

    def test_portable_profile_relocation_and_changed_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profiles = setup_profiles(root)
            (root/'fake-db').mkdir()
            failure = SimpleNamespace(opened=False, diagnostics=[('warning', 'leveldb-not-decoded', 'controlled snapshot failure')])
            with patch('forgebridge.uvtt.read_leveldb_directory', return_value=failure):
                with self.assertRaisesRegex(InventoryFatal, 'controlled snapshot failure'):
                    _load_leveldb_scene(root, {'source_path': 'fake-db'}, 'A')
            before, _, _ = load_profile(profiles[0])
            portable_profile(profiles[0], root/'portable')
            shutil.move(root/'portable', root/'relocated')
            p, paths, _ = load_profile(root/'relocated/scene-profile.json')
            self.assertEqual(p['geometry']['calibration'], before['geometry']['calibration'])
            self.assertEqual(preflight_profile(root/'relocated/scene-profile.json')[0]['status'], 'PASS')
            self.assertTrue(all(path.is_relative_to(root/'relocated') for path in paths.values()))
            original_text = profiles[1].read_text()
            original_copy = shutil.copyfile
            changed = []
            def changing_copy(*args, **kwargs):
                result = original_copy(*args, **kwargs)
                if not changed:
                    profiles[1].write_text(original_text+'\n')
                    changed.append(True)
                return result
            with patch('forgebridge.native_capture.shutil.copyfile', side_effect=changing_copy):
                with self.assertRaisesRegex(ValueError, 'Profile changed'):
                    portable_profile(profiles[1], root/'unstable')
            self.assertFalse((root/'unstable').exists())
            self.assertEqual(profiles[1].read_text(), original_text+'\n')
            paths['source.companion'].write_text('{}')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                load_profile(root/'relocated/scene-profile.json')


if __name__ == '__main__':
    unittest.main()


class NativeAuditTests(unittest.TestCase):
    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}

    def test_clean_audit_matches_capture_selection_and_writes_nothing(self):
        from forgebridge.native_capture import audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {'MyAssets/Maps/A.rwmap': record('MyAssets/Media/B.rwmeta'),
                     'MyAssets/Maps/A.rwmeta': record(),
                     'MyAssets/Media/B.rwmeta': record(),
                     'MyAssets/Media/B.rwfile': record(),
                     'MyAssets/Maps/Unrelated.rwmap': record()}
            archive(root/'in.zip', files)
            before = self.snapshot(root)
            report = audit([root/'in.zip'], 'MyAssets/Maps/A.rwmap', root/'planned')
            self.assertEqual(self.snapshot(root), before)
            self.assertFalse((root/'planned').exists())
            self.assertTrue(report['ok'], report['findings'])
            self.assertTrue(report['destination']['available'])
            self.assertEqual(report['unselected'], ['MyAssets/Maps/Unrelated.rwmap'])
            captured = capture([root/'in.zip'], root/'planned', 'MyAssets/Maps/A.rwmap')
            self.assertEqual([f['path'] for f in report['files']], [f['path'] for f in captured['files']])
            self.assertEqual([f['sha256'] for f in report['files']], [f['sha256'] for f in captured['files']])
            self.assertEqual(report['dependencies'], captured['dependencies'])
            again = audit([root/'in.zip'], 'MyAssets/Maps/A.rwmap', root/'planned')
            self.assertFalse(again['ok'])
            self.assertEqual([f['check'] for f in again['findings']], ['destination-exists'])

    def test_audit_lists_every_gap_instead_of_stopping(self):
        from forgebridge.native_capture import audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = 'MyAssets/Maps/A.rwmap'
            archive(root/'a.zip', {primary: record('MyAssets/Missing.rwmeta'),
                                   'MyAssets/Maps/A.rwmeta': record('MyAssets/Media/x.png'),
                                   'MyAssets/Notes/N.rwmeta': record()})
            archive(root/'b.zip', {'MyAssets/Notes/N.rwmeta': record('different'),
                                   'MyAssets/Notes/n.rwnote': record()})
            (root/'broken.zip').write_bytes(b'not a zip')
            before = self.snapshot(root)
            report = audit([root/'a.zip', root/'b.zip', root/'broken.zip'], primary)
            self.assertEqual(self.snapshot(root), before)
            checks = sorted(f['check'] for f in report['findings'])
            self.assertEqual(checks, ['conflicting-bytes', 'missing-dependency',
                                      'unreadable-export', 'unsupported-reference'])
            self.assertFalse(report['ok'])
            self.assertEqual(report['inputs'][2]['readable'], False)

    def test_ambiguous_exports_summarise_each_candidate(self):
        from forgebridge.native_capture import audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive(root/'in.zip', {'MyAssets/Maps/A.rwmap': record(), 'MyAssets/Maps/A.rwmeta': record(),
                                    'MyAssets/Maps/B.rwmap': record('MyAssets/Gone.rwmeta')})
            report = audit([root/'in.zip'])
            self.assertEqual(report['findings'][0]['check'], 'map-selection')
            candidates = {c['map']: c for c in report['candidates']}
            self.assertTrue(candidates['MyAssets/Maps/A.rwmap']['complete'])
            self.assertFalse(candidates['MyAssets/Maps/B.rwmap']['complete'])
            self.assertIsNone(report['primary_map'])

    def test_case_alias_across_exports_and_unsafe_reference(self):
        from forgebridge.native_capture import audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unsafe = 'MyAssets' + chr(92) + '..' + chr(92) + 'outside.rwmeta'
            archive(root/'a.zip', {'MyAssets/Maps/A.rwmap': record(unsafe), 'MyAssets/Maps/A.rwmeta': record()})
            archive(root/'b.zip', {'MyAssets/Maps/a.rwmeta': record()})
            report = audit([root/'a.zip', root/'b.zip'], 'MyAssets/Maps/A.rwmap')
            checks = sorted(f['check'] for f in report['findings'])
            self.assertEqual(checks, ['case-conflict', 'unsafe-path'])

    def test_cli_audit_exit_codes_and_no_output(self):
        import io, json, contextlib
        from forgebridge.native_capture import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive(root/'in.zip', {'MyAssets/Maps/A.rwmap': record(), 'MyAssets/Maps/A.rwmeta': record()})
            out = io.StringIO()
            with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as done:
                main(['--audit', '--export', str(root/'in.zip')])
            self.assertEqual(done.exception.code, 0)
            self.assertTrue(json.loads(out.getvalue())['ok'])
            archive(root/'bad.zip', {'MyAssets/Maps/A.rwmap': record('MyAssets/Gone.rwmeta'),
                                     'MyAssets/Maps/A.rwmeta': record()})
            out = io.StringIO()
            with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as done:
                main(['--audit', '--export', str(root/'bad.zip')])
            self.assertEqual(done.exception.code, 1)
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['bad.zip', 'in.zip'])
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as done:
                main(['--export', str(root/'in.zip')])
            self.assertEqual(done.exception.code, 2)

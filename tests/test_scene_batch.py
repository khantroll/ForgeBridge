from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forgebridge.native_dependencies import read_package, merge_native, check_metadata_references
from forgebridge.scene_batch import preflight_batch, build_batch, main
from forgebridge.scene_profile import fingerprint
from test_scene_profile import setup_profiles, archive, contents


class SceneBatchTests(unittest.TestCase):
    def test_read_only_preflight_reports_shared_ids_dependencies_and_losses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profiles = setup_profiles(root)
            before = fingerprint(root)
            with patch('forgebridge.scene_batch.build_package', side_effect=AssertionError('must not build')):
                report, _ = preflight_batch(profiles)
            self.assertEqual(report['status'], 'PASS')
            self.assertTrue(report['shared_dependencies'])
            self.assertTrue(report['duplicate_source_tokens'])
            self.assertTrue(report['duplicate_source_notes'])
            self.assertEqual([s['preflight']['supported_tokens'] for s in report['scenes']], [1, 1, 0])
            self.assertEqual([len(s['rejected_tokens']) for s in report['loss_report']], [2, 2, 0])
            self.assertEqual(fingerprint(root), before)

    def test_build_separate_packages_closed_together_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / 'inputs'; inputs.mkdir()
            profiles = setup_profiles(inputs)
            before = fingerprint(inputs)
            out = root / 'batch'
            report = build_batch(profiles, out)
            combined = {}
            for scene in report['scenes']:
                package = out / scene['package']
                self.assertEqual(fingerprint(package), scene['package_sha256'])
                files = read_package(package)
                merge_native(combined, {n: d for n, d in files.items() if n.startswith('MyAssets/')})
            self.assertGreater(check_metadata_references(combined), 0)
            self.assertEqual(json.loads((out / 'batch-report.json').read_text())['status'], 'PASS')
            stable = fingerprint(out)
            with self.assertRaisesRegex(ValueError, 'new batch output'):
                build_batch(profiles, out)
            self.assertEqual(stable, fingerprint(out))
            self.assertEqual(before, fingerprint(inputs))

    def test_map_name_aliases_and_duplicate_profile_block_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, _ = setup_profiles(root)
            p = json.loads(b.read_text()); p['output']['map_name'] = 'output a'
            b.write_text(json.dumps(p))
            report, _ = preflight_batch([a, b, a])
            self.assertEqual(report['status'], 'FAIL')
            kinds = {r['kind'] for r in report['conflicts']}
            self.assertTrue({'map_name', 'duplicate_scope', 'note_folder'} <= kinds)
            with self.assertRaisesRegex(ValueError, 'preflight failed'):
                build_batch([a, b], root / 'absent')
            self.assertFalse((root / 'absent').exists())

    def test_conflicting_native_bytes_and_case_alias_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, _ = setup_profiles(root)
            # Add a second valid native control note under an alias of one
            # preserved by the other scene; both profiles remain valid alone.
            files = contents(root / 'B.zip')
            controls = contents(root / 'controls.zip')
            files['MyAssets/Encyclopedia/Notes/control.rwnote'] = controls['MyAssets/Encyclopedia/Notes/Control.rwnote']
            archive(root / 'B.zip', files)
            p = json.loads(b.read_text()); digest = fingerprint(root / 'B.zip')
            p['geometry']['export']['sha256'] = p['geometry']['calibration']['geometry_sha256'] = digest
            b.write_text(json.dumps(p))
            report, _ = preflight_batch([a, b])
            self.assertEqual(report['status'], 'FAIL')
            # A within-profile alias fails the shared parser before batch merge.
            self.assertTrue(report['conflicts'])

    def test_preserved_dependency_cannot_shadow_new_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, _ = setup_profiles(root)
            p = json.loads(b.read_text()); p['output']['map_name'] = 'A'
            b.write_text(json.dumps(p))
            report, _ = preflight_batch([a, b])
            self.assertTrue(any(c['kind'] == 'output_dependency_collision' for c in report['conflicts']))

    def test_individually_valid_native_dependencies_with_different_bytes_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, _ = setup_profiles(root)
            for sid, profile in [('A', a), ('B', b)]:
                export = root / (sid + '.zip')
                files = contents(export)
                files['MyAssets/Maps/Shared.rwmeta'] = files['MyAssets/Maps/' + sid + '.rwmeta']
                archive(export, files)
                p = json.loads(profile.read_text()); digest = fingerprint(export)
                p['geometry']['export']['sha256'] = p['geometry']['calibration']['geometry_sha256'] = digest
                profile.write_text(json.dumps(p))
            report, _ = preflight_batch([a, b])
            self.assertEqual(len(report['scenes']), 2)
            self.assertEqual(report['status'], 'FAIL')
            self.assertTrue(any(c['kind'] == 'native_dependency' for c in report['conflicts']))

    def test_invalid_input_does_not_stop_remaining_profile_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, zero = setup_profiles(root)
            (root / 'A.json').write_text('{}')
            before = fingerprint(root)
            report, _ = preflight_batch([a, b, zero])
            self.assertEqual(report['status'], 'FAIL')
            self.assertEqual(len(report['scenes']), 2)
            self.assertIn('hash mismatch', report['conflicts'][0]['error'])
            self.assertEqual(before, fingerprint(root))

    def test_failed_staged_build_or_changed_profile_never_publishes(self):
        from forgebridge.package import build_package
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, _ = setup_profiles(root)
            out = root / 'absent'
            with patch('forgebridge.scene_batch.build_package', side_effect=ValueError('stage failure')):
                with self.assertRaisesRegex(ValueError, 'stage failure'):
                    build_batch([a, b], out)
            self.assertFalse(out.exists())
            def change_profile(**kwargs):
                result = build_package(**kwargs)
                a.write_bytes(a.read_bytes() + b'\n')
                return result
            with patch('forgebridge.scene_batch.build_package', side_effect=change_profile):
                with self.assertRaisesRegex(ValueError, 'Profile changed'):
                    build_batch([a, b], out)
            self.assertFalse(out.exists())

    def test_cli_and_input_output_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, _ = setup_profiles(root)
            with redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(main(['--profile', str(a), '--profile', str(b), '--preflight']), 0)
            self.assertEqual(json.loads(stdout.getvalue())['status'], 'PASS')
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(['--profile', str(a), '--preflight']), 1)
            with self.assertRaisesRegex(ValueError, 'outside every input'):
                build_batch([a, b], root / 'package' / 'output')

    def test_changed_source_input_is_rejected_without_reopening_source_adapter(self):
        from forgebridge.package import build_package
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, b, _ = setup_profiles(root)
            out = root / 'absent'
            def change_source(**kwargs):
                result = build_package(**kwargs)
                token = root / 'package' / 'token.png'
                token.write_bytes(token.read_bytes() + b'changed')
                return result
            with patch('forgebridge.scene_batch.build_package', side_effect=change_source):
                with self.assertRaisesRegex(ValueError, 'source.package changed'):
                    build_batch([a, b], out)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()

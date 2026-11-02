from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from forgebridge.cli import main
from forgebridge.convert import convert, discover
from forgebridge.scene_profile import fingerprint

FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'


class ConvertTests(unittest.TestCase):
    def test_public_convert_discovers_scenes_preserves_source_and_reports_losses(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'export'
            before = fingerprint(FIXTURE)
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(['convert', str(FIXTURE), '--out', str(dest)]), 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report['scenes'][0]['id'], 'scene-crypt')
            self.assertEqual(report['scenes'][0]['status'], 'BUILT')
            self.assertGreater(report['counts']['unsupported'], 0)
            self.assertEqual(json.loads((dest / 'conversion-report.json').read_text()), report)
            with zipfile.ZipFile(dest / 'scene-001/uvtt-package.zip') as archive:
                self.assertIn('scene.uvtt', archive.namelist())
                self.assertIn('source-assets/assets/drip.wav', archive.namelist())
                companion = json.loads(archive.read('scene.forgebridge.json'))
                self.assertEqual(companion['source_scene']['_id'], 'scene-crypt')
                self.assertEqual(companion['loss_report'], report['scenes'][0]['loss_report'])
            self.assertTrue((dest / 'MyAssets/Maps/Synthetic Module').is_dir())
            self.assertGreater(report['closed_native_metadata_references'], 0)
            self.assertEqual(fingerprint(FIXTURE), before)
            stable = fingerprint(dest)
            with self.assertRaises(ValueError): convert(FIXTURE, dest)
            self.assertEqual(stable, fingerprint(dest))

    def test_zip_discovery_and_conversion_match_directory_scene_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); zipped = root / 'source.zip'
            with zipfile.ZipFile(zipped, 'w') as z:
                for path in FIXTURE.rglob('*'):
                    if path.is_file(): z.write(path, path.relative_to(FIXTURE).as_posix())
            self.assertEqual(discover(zipped), discover(FIXTURE))
            report = convert(zipped, root / 'out')
            self.assertEqual(report['status'], 'PASS')
            self.assertFalse(report['installed'])

    def test_missing_selection_and_output_inside_source_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'not found'):
                convert(FIXTURE, Path(tmp) / 'absent', scene_ids=['missing'])
            self.assertFalse((Path(tmp) / 'absent').exists())
        with self.assertRaisesRegex(ValueError, 'outside'):
            convert(FIXTURE, FIXTURE / 'bad-output')

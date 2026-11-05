from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from forgebridge.install_review import review
from test_native_capture import record
from test_scene_profile import archive


class InstallReviewTests(unittest.TestCase):
    def test_classification_preserves_snapshot_reports_and_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); snapshot = root/'MyAssets'; snapshot.mkdir()
            files = {'MyAssets/Maps/A.rwmap': record(), 'MyAssets/Maps/A.rwmeta': record(),
                     'MyAssets/Notes/Edited.rwnote': record(), 'conversion-report.json': b'{}'}
            package = root/'scene.zip'; archive(package, files)
            (snapshot/'Maps').mkdir(); (snapshot/'Notes').mkdir()
            (snapshot/'Maps/A.rwmap').write_bytes(files['MyAssets/Maps/A.rwmap'])
            (snapshot/'Notes/Edited.rwnote').write_bytes(b'user edits')
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = review([package], snapshot)
            self.assertFalse(result['ok'])
            self.assertEqual(result['counts'], {'new': 1, 'identical': 1, 'conflict': 1, 'blocked': 0})
            self.assertEqual(result['not_installed'][0]['path'], 'conversion-report.json')
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_existing_map_name_conflict_names_library_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); snapshot = root / 'MyAssets'; snapshot.mkdir()
            path = 'MyAssets/Maps/Folder/Room.rwmap'
            package = root / 'scene.zip'
            archive(package, {path: record(), 'MyAssets/Maps/Folder/Room.rwmeta': record(),
                              'conversion-report.json':
                              b'{"output_names":{"map_path":"MyAssets/Maps/Folder/Room.rwmap"}}'})
            (snapshot / 'Maps/Elsewhere').mkdir(parents=True)
            (snapshot / 'Maps/Elsewhere/Room.rwmap').write_bytes(b'user map')
            result = review([package], snapshot)
            self.assertFalse(result['ok'])
            detail = next(row['detail'] for row in result['files'] if row['path'] == path)
            self.assertIn('MyAssets library', detail)
            self.assertIn('Room.rwmap', detail)
            self.assertIn('library-wide', detail)
            self.assertNotIn('another package', detail.casefold())

    def test_case_alias_and_parent_file_are_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); snapshot=root/'MyAssets'; snapshot.mkdir()
            archive(root/'scene.zip', {'MyAssets/Maps/A.rwmap': record(), 'MyAssets/Maps/A.rwmeta': record()})
            (snapshot/'maps').mkdir()
            result=review([root/'scene.zip'],snapshot)
            self.assertEqual(result['counts']['blocked'],2)
            (snapshot/'maps').rmdir(); (snapshot/'Maps').write_bytes(b'user file')
            self.assertEqual(review([root/'scene.zip'],snapshot)['counts']['blocked'],2)

    def test_conflicting_packages_and_unsafe_archives_fail_before_snapshot_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); snapshot=root/'MyAssets'; snapshot.mkdir()
            archive(root/'a.zip', {'MyAssets/Maps/A.rwmap': record()})
            archive(root/'b.zip', {'MyAssets/Maps/A.rwmap': record('different')})
            with self.assertRaisesRegex(ValueError,'conflicts'):
                review([root/'a.zip',root/'b.zip'],snapshot)
            info=zipfile.ZipInfo('MyAssets/link.rwmap'); info.create_system=3; info.external_attr=0o120777<<16
            with zipfile.ZipFile(root/'link.zip','w') as z: z.writestr(info,b'outside')
            with self.assertRaisesRegex(ValueError,'symbolic link'):
                review([root/'link.zip'],snapshot)
            self.assertEqual(list(snapshot.iterdir()),[])

    def test_missing_metadata_reference_refuses_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); snapshot=root/'MyAssets'; snapshot.mkdir()
            archive(root/'a.zip', {'MyAssets/Maps/A.rwmap': record('MyAssets/Missing.rwmeta')})
            with self.assertRaisesRegex(ValueError,'Missing native dependency'):
                review([root/'a.zip'],snapshot)

    def test_snapshot_mutation_during_comparison_is_not_a_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); snapshot=root/'MyAssets'; snapshot.mkdir()
            files={'MyAssets/Maps/A.rwmap':record(), 'MyAssets/Maps/A.rwmeta':record()}
            archive(root/'a.zip',files)
            (snapshot/'Maps').mkdir()
            for n,d in files.items(): (root/n).write_bytes(d)
            original=Path.read_bytes
            changed=[]
            def changing_read(path):
                data=original(path)
                if path == snapshot/'Maps/A.rwmap' and not changed:
                    path.write_bytes(b'concurrent user change')
                    changed.append(True)
                return data
            with patch.object(Path,'read_bytes',changing_read):
                with self.assertRaisesRegex(ValueError,'Snapshot changed'):
                    review([root/'a.zip'],snapshot)
            self.assertEqual((snapshot/'Maps/A.rwmap').read_bytes(),b'concurrent user change')


if __name__ == '__main__':
    unittest.main()

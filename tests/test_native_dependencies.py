"""Shared export validation used by capture and production package assembly."""
from pathlib import Path
import tempfile
import unittest
import zipfile

from forgebridge.native_dependencies import merge_native, read_export


class NativeDependencyTests(unittest.TestCase):
    def test_merge_is_atomic_on_late_content_conflict(self):
        original = {'MyAssets/Maps/A.rwmap': b'user-edited-map'}
        files = dict(original)
        with self.assertRaisesRegex(ValueError, 'conflicts.*MyAssets/Maps/A.rwmap'):
            merge_native(files, {'MyAssets/Notes/New.rwnote': b'new',
                                 'MyAssets/Maps/A.rwmap': b'generated-map'})
        self.assertEqual(files, original)

    def test_cross_export_aliases_fail_even_for_identical_bytes(self):
        original = {'MyAssets/Notes/Shared.rwmeta': b'identical'}
        for alias in ('MyAssets/Notes/shared.rwmeta', 'MyAssets/notes/Shared.rwmeta'):
            with self.subTest(alias=alias):
                files = dict(original)
                with self.assertRaisesRegex(ValueError, 'Case-conflicting'):
                    merge_native(files, {'MyAssets/Notes/New.rwnote': b'new', alias: b'identical'})
                self.assertEqual(files, original)

    def test_identical_dependency_deduplicates_and_distinct_paths_coexist(self):
        files = {'MyAssets/Notes/Shared.rwmeta': b'original', 'conversion-report.json': b'{}'}
        merge_native(files, {'MyAssets/Notes/Shared.rwmeta': b'original',
                             'MyAssets/Notes/Other.rwmeta': b'original'})
        self.assertEqual(len(files), 3)
        self.assertEqual(files['conversion-report.json'], b'{}')
        self.assertEqual(files['MyAssets/Notes/Other.rwmeta'], b'original')

    def test_shared_loader_rejects_aliases_unsafe_names_and_symlinks(self):
        cases = [
            [('MyAssets/Maps/A.rwmap', b'a'), ('MyAssets/Maps/a.rwmap', b'a')],
            [('MyAssets/Maps/CON.rwmap', b'a')],
            [('MyAssets/Maps/A./x.rwmap', b'a')],
            [('MyAssets//Maps/A.rwmap', b'a')],
            [('MyAssets/../A.rwmap', b'a')],
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.zip'
            for entries in cases:
                with self.subTest(entries=entries):
                    with zipfile.ZipFile(path, 'w') as archive:
                        for name, data in entries:
                            archive.writestr(name, data)
                    before = path.read_bytes()
                    with self.assertRaises(ValueError):
                        read_export(path)
                    self.assertEqual(path.read_bytes(), before)
            info = zipfile.ZipInfo('MyAssets/Maps/Link.rwmap')
            info.create_system = 3
            info.external_attr = 0o120777 << 16
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr(info, b'outside')
            with self.assertRaisesRegex(ValueError, 'symbolic link'):
                read_export(path)


if __name__ == '__main__':
    unittest.main()

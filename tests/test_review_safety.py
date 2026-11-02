"""Regression cases for the Part B1 file-level review; no installed assets."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from contextlib import redirect_stdout, redirect_stderr

from forgebridge.native_map import write_map_zip, clone
from forgebridge.native_tokens import write_token_zip
from forgebridge.package import build_package
from forgebridge.scene_profile import preflight_profile, fingerprint
from forgebridge.nrbf import Reader
from forgebridge.uvtt import _square_grid
from forgebridge.cli import main
from forgebridge.notes import correlate_notes
from forgebridge.convert import convert
from forgebridge.validate import InventoryFatal
from test_scene_profile import setup_profiles, contents, archive
from test_nrbf import stream, cls, i


class ReviewSafetyTests(unittest.TestCase):
    def test_standalone_writers_reject_alias_ads_reserved_and_link_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, _, _ = setup_profiles(root)
            _, settings = preflight_profile(a)
            original = contents(root / 'controls.zip')
            for bad in ('MyAssets/Maps/Control.rwmap:stream', 'MyAssets/Maps/CON.rwmap',
                        'MyAssets/Maps/control.rwmap', 'MyAssets/Maps/trailing./x.rwmeta'):
                files = dict(original); files[bad] = b'inert'
                archive(root / 'hostile.zip', files)
                for writer in ('map', 'token'):
                    dest = root / (writer + '.zip')
                    with self.subTest(bad=bad, writer=writer), self.assertRaises(ValueError):
                        if writer == 'map':
                            write_map_zip(root / 'hostile.zip', settings['companion'], dest,
                                          name='Output', units_per_grid=3, template_name='Control')
                        else:
                            write_token_zip(root / 'hostile.zip', settings['companion'], settings['package'], dest,
                                name='Output', units_per_grid=3, control_units_per_grid=2.56, control_name='Control')
                    self.assertFalse(dest.exists())
            with zipfile.ZipFile(root / 'hostile.zip', 'w') as z:
                for name, data in original.items(): z.writestr(name, data)
                entry = zipfile.ZipInfo('MyAssets/Maps/link.rwmap')
                entry.create_system = 3; entry.external_attr = 0o120777 << 16
                z.writestr(entry, 'outside')
            with self.assertRaisesRegex(ValueError, 'symbolic link'):
                write_map_zip(root / 'hostile.zip', settings['companion'], root / 'map.zip',
                              name='Output', units_per_grid=3)

    def test_package_bytes_do_not_depend_on_clock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a, _, _ = setup_profiles(root)
            _, settings = preflight_profile(a)
            before = fingerprint(settings['package'])
            # A real time change, without sleeps; defaults in writestr use localtime.
            for n, year in enumerate((2027, 2037)):
                with patch('zipfile.time.localtime', return_value=(year, 2, 3, 4, 5, 6, 0, 0, -1)):
                    build_package(**settings, dest=root / f'{n}.zip')
            self.assertEqual((root / '0.zip').read_bytes(), (root / '1.zip').read_bytes())
            self.assertEqual(fingerprint(settings['package']), before)

    def test_profile_hash_is_bounded_even_if_file_grows_after_stat(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input'; path.write_bytes(b'a')
            with patch('forgebridge.scene_profile.MAX_PROFILE_FILE_BYTES', 4), \
                    patch.object(Path, 'open', return_value=io.BytesIO(b'12345')):
                with self.assertRaisesRegex(ValueError, 'grew beyond'):
                    fingerprint(path)

    def test_profile_input_rejects_linked_ancestor_without_os_link_privileges(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input'; path.write_bytes(b'a')
            original = Path.is_junction
            def junction(p):
                return p == path.parent or original(p)
            with patch.object(Path, 'is_junction', junction):
                with self.assertRaisesRegex(ValueError, 'links/junctions'):
                    fingerprint(path)

    def test_flat_nrbf_reference_chain_has_explicit_clone_bound(self):
        body = b''.join(cls(n, ['next'], [2]) + b'\x09' + i(n + 1) for n in range(1, 140))
        body += cls(140, ['next'], [2]) + b'\x0a'
        reader = Reader(stream(body)); reader.read()
        with self.assertRaisesRegex(ValueError, 'clone depth limit'):
            clone(reader, 1)

    def test_fractional_grid_is_refused_instead_of_silently_truncated(self):
        with self.assertRaisesRegex(InventoryFatal, 'Fractional grid'):
            _square_grid({'grid': {'type': 1, 'size': 50.5}})
        self.assertEqual(_square_grid({'grid': {'type': 1, 'size': 50}}), 50.)

    def test_existing_legacy_uvtt_output_and_duplicate_source_zip_are_refused(self):
        fixture = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); dest = root / 'scene.uvtt'; dest.write_bytes(b'user edits')
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(fixture), '--uvtt-scene', 'scene-crypt', '--uvtt-out', str(dest)]), 1)
            self.assertEqual(dest.read_bytes(), b'user edits')
            self.assertFalse(dest.with_suffix('.forgebridge.json').exists())
            with zipfile.ZipFile(root / 'hostile.zip', 'w') as archive:
                archive.writestr('module.json', '{}'); archive.writestr('MODULE.JSON', '{}')
            with self.assertRaisesRegex(InventoryFatal, 'case-aliased'):
                convert(root / 'hostile.zip', root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_malformed_or_oversized_note_placements_are_explicitly_refused(self):
        for value in (None, 'bad', [{}] * 2049):
            with self.subTest(value=type(value)), self.assertRaisesRegex(ValueError, '2048'):
                correlate_notes({'_id': 'scene', 'notes': value}, [], (0, 0), 100)

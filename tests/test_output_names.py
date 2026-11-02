import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from forgebridge.convert import convert, discover, pdf_mode
from forgebridge.output_names import sanitize_name, plan_names, default_folder
from forgebridge.install_review import review
from forgebridge.native_dependencies import read_package, write_archive, check_metadata_references
from forgebridge.nrbf import Reader
from test_pdf_pages import pdf_fixture
from test_native_capture import record

FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'


class OutputNamingTests(unittest.TestCase):
    def test_windows_sanitization_and_bounds(self):
        self.assertEqual(sanitize_name('Count\'s <>:"/\\|?*Lair\x00\x1f\x7f. '), "Count's Lair")
        self.assertEqual(sanitize_name('a' * 80), 'a' * 80)
        for value in ['a' * 81, '', '... ', '<>', 'CON', 'prn.txt', 'AUX', 'NUL',
                      *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}.txt' for i in range(1, 10))]:
            with self.subTest(value=value), self.assertRaises(ValueError): sanitize_name(value)

    def test_default_names_and_sanitized_overrides(self):
        row = {'key': 'key', 'id': 'id', 'name': "Count's Lair", 'parent_adventure_name': "The Count's Manor"}
        plan = plan_names([row], 'Package title')['key']
        self.assertEqual(plan, {'map_folder': "The Count's Manor", 'notes_folder': "The Count's Manor",
            'map_name': "Count's Lair", 'map_path': "MyAssets/Maps/The Count's Manor/Count's Lair.rwmap"})
        self.assertEqual(default_folder({}, 'Package title'), 'Package title')
        self.assertEqual(default_folder({}), 'ForgeBridge')
        self.assertEqual(plan_names([row], map_folder='New: Maps', notes_folder='My notes. ',
                                    map_names=['key=Our / Lair'])['key']['map_name'], 'Our  Lair')
        self.assertEqual(plan_names([row], map_names=['Single name'])['key']['map_name'], 'Single name')

    def test_clashes_refuse_and_explicit_scoped_overrides_resolve_them(self):
        rows = [{'key': '5e', 'id': 'same', 'name': 'Room'}, {'key': 'sa', 'id': 'same', 'name': 'ROOM'}]
        with self.assertRaisesRegex(ValueError, 'Map name conflict.*Rename'): plan_names(rows)
        plans = plan_names(rows, map_names=['5e=Room 5e', 'sa=Room SA'])
        self.assertEqual(plans['sa']['map_name'], 'Room SA')
        for overrides in [['missing=Name'], ['5e=One', '5e=Two'], ['one unscoped name']]:
            with self.assertRaises(ValueError): plan_names(rows, map_names=overrides)

    def test_pdf_mode_defaults_explicit_modes_and_import_failure_loss(self):
        with patch('forgebridge.convert._pdf_renderer', return_value=object()):
            self.assertEqual(pdf_mode(), ('pages', None))
            self.assertEqual(pdf_mode('pages'), ('pages', None))
        with patch('forgebridge.convert._pdf_renderer', side_effect=ImportError('missing renderer')):
            mode, loss = pdf_mode()
            self.assertEqual(mode, 'references'); self.assertIn('missing renderer', loss)
            with self.assertRaisesRegex(ValueError, 'pypdfium2'): pdf_mode('pages')
            self.assertIn('selected', pdf_mode('references')[1])
        with self.assertRaises(ValueError): pdf_mode('unbounded')

    def test_review_refuses_same_named_map_across_packages_even_with_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); assets = root / 'MyAssets'; assets.mkdir()
            packages = []
            for folder in ('A', 'B'):
                path = f'MyAssets/Maps/{folder}/Room.rwmap'
                archive = root / (folder + '.zip')
                write_archive(archive, {path: record(), 'conversion-report.json':
                    json.dumps({'output_names': {'map_path': path}}).encode()})
                packages.append(archive)
            with self.assertRaisesRegex(ValueError, 'Map name conflicts.*Rename'):
                review(packages, assets)
            self.assertEqual(list(assets.iterdir()), [])

    def test_generated_names_both_records_scope_preservation_and_existing_map_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = convert(FIXTURE, root / 'first', map_names=['Our: Room'], map_folder='My Maps',
                             notes_folder="Owner's notes", pdf='references')
            names = report['scenes'][0]['native_report']['output_names']
            self.assertEqual(names['map_name'], 'Our Room')
            files = read_package(root / 'first/scene-001/native-package.zip')
            self.assertEqual(names['map_path'], 'MyAssets/Maps/My Maps/Our Room.rwmap')
            for path in (names['map_path'], names['map_path'][:-6] + '.rwmeta'):
                reader = Reader(files[path]); graph = reader.read()
                value = reader.objects[graph['root_id']]['members']['_name']
                if isinstance(value, dict): value = reader.objects[value['ref']]
                self.assertEqual(value, 'Our Room')
            self.assertTrue(any(p.startswith("MyAssets/Encyclopedia/Notes/Owner's notes/") for p in files))
            scope = report['scenes'][0]['native_report']['native_synthesis']['scope']
            second = convert(FIXTURE, root / 'second', map_names=['Other Room'], pdf='references')
            self.assertEqual(scope, second['scenes'][0]['native_report']['native_synthesis']['scope'])
            second_files = read_package(root / 'second/scene-001/native-package.zip')
            self.assertEqual({p: d for p, d in files.items() if p.startswith('MyAssets/Media/')},
                             {p: d for p, d in second_files.items() if p.startswith('MyAssets/Media/')})
            self.assertGreater(check_metadata_references(files), 0)
            assets = root / 'MyAssets'; (assets / 'Maps/Elsewhere').mkdir(parents=True)
            (assets / 'Maps/Elsewhere/OUR ROOM.rwmap').write_bytes(b'user map')
            audit = review([root / 'first/scene-001/native-package.zip'], assets)
            self.assertFalse(audit['ok'])
            self.assertIn('rename', next(r for r in audit['files'] if r['path'].endswith('.rwmap'))['detail'])
            self.assertEqual((assets / 'Maps/Elsewhere/OUR ROOM.rwmap').read_bytes(), b'user map')

    def test_pdf_pages_flow_through_default_convert_and_references_stay_explicit(self):
        try:
            import pypdfium2
        except ImportError:
            self.skipTest('optional PDF renderer not installed')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root / 'source'; shutil.copytree(FIXTURE, package)
            (package / 'assets/handout.pdf').write_bytes(pdf_fixture())
            journal_path = package / 'packs/journal.db'
            journal = json.loads(journal_path.read_text())
            journal['pages'].append({'_id': 'pdf-page', 'name': 'Letter', 'type': 'pdf', 'src': 'assets/handout.pdf'})
            journal_path.write_text(json.dumps(journal))
            pages = convert(package, root / 'pages')
            native = pages['scenes'][0]['native_report']
            self.assertEqual(pages['pdf_mode'], 'pages')
            self.assertGreater(native['counts']['native_pdf_pages'], 0)
            refs = convert(package, root / 'refs', pdf='references')
            self.assertEqual(refs['scenes'][0]['native_report']['counts']['native_pdf_pages'], 0)
            self.assertTrue(any(r['feature'] == 'pdf-mode' for r in refs['native_losses'][0]['losses']))


class DefaultFolderRobustnessTests(unittest.TestCase):
    def test_malformed_retained_fields_fall_back(self):
        from forgebridge.output_names import default_folder
        self.assertEqual(default_folder({'retained_fields': None}), 'ForgeBridge')
        self.assertEqual(default_folder({'retained_fields': {'_forgebridge_parent_adventure': 'x'}}, 'Pack'), 'Pack')
        self.assertEqual(default_folder({'parent_adventure_name': '  '}, None), 'ForgeBridge')

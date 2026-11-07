from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from forgebridge.cli import main
from forgebridge.convert import discover, convert
from forgebridge.fantasy_grounds import ModuleError
from forgebridge.gui import report_text, scene_label
from forgebridge.installer import uninstall
from forgebridge.native_dependencies import read_package, check_metadata_references
from forgebridge.nrbf import Reader
from test_fantasy_grounds import module, DEFINITION, png
from test_gui import run_headless_gui, click, finish_job


def needs_grid(root):
    return module(root, {'definition.xml': DEFINITION, 'images/ice.png': png(2048, 1024),
        'db.xml': b'<root><image><id-ice><name>Ice Caverns</name><image type="image"><bitmap>images/ice.png</bitmap>'
                  b'<grid>on</grid><occluders><occluder><points>-1024,512,1024,512</points></occluder>'
                  b'<occluder><points>-1024,512,-1024,-512</points></occluder>'
                  b'<occluder><points>-1024,-512,1024,-512</points></occluder></occluders></image></id-ice></image></root>'})


def encrypt_flag(path):
    data = bytearray(path.read_bytes())
    for sig, offset in [(b'PK\x03\x04', 6), (b'PK\x01\x02', 8)]:
        data[data.find(sig) + offset] |= 1
    path.write_bytes(data)


class FantasyGroundsConversionTests(unittest.TestCase):
    def test_foundry_manifest_wins_over_incidental_fg_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'
            folder = root / 'module'; folder.mkdir()
            with zipfile.ZipFile(root / 'source.zip', 'w') as archive:
                for file in source.rglob('*'):
                    if file.is_file():
                        relative = file.relative_to(source); target = folder / relative
                        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(file.read_bytes())
                        archive.writestr(relative.as_posix(), file.read_bytes())
                archive.writestr('modules/FG/definition.xml', DEFINITION)
            (folder / 'definition.xml').write_bytes(DEFINITION)
            self.assertEqual(discover(folder)['scenes'][0]['id'], 'scene-crypt')
            self.assertEqual(discover(root / 'source.zip')['scenes'][0]['id'], 'scene-crypt')

    def test_sidecar_geometry_without_grid_is_not_hidden_as_art(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = module(tmp, {'definition.xml': DEFINITION, 'db.xml':
                b'<root><image><id><name>Sidecar</name><image type="image"><bitmap>images/m.png</bitmap></image></id></image></root>',
                'images/m.png': png(), 'images/m.xml': b'<root><occluders><occluder><points>0,0,1,1</points></occluder></occluders></root>'})
            row = discover(path)['scenes'][0]
            self.assertEqual(row['status'], 'NEEDS_GRID'); self.assertEqual(row['metadata_source'], 'images/m.xml')

    def test_invalid_stored_grid_and_resampling_limits_refuse_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            for grid in ('0.2,0.2', '100.6,100.6'):
                body = b'<root><image><id><name>Map</name><image type="image"><bitmap>images/m.png</bitmap>'
                path = module(tmp, {'definition.xml': DEFINITION, 'db.xml': body +
                    f'<gridsize>{grid}</gridsize></image></id></image></root>'.encode(), 'images/m.png': png()})
                with patch('forgebridge.fantasy_grounds.MAX_IMAGE_PIXELS', 120000):
                    row = discover(path)['scenes'][0]
                    self.assertEqual(row['status'], 'BLOCKED')

    def test_mod_to_native_uses_shared_geometry_and_campaign_notes_and_reports_source_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = module(root); before = package.read_bytes()
            discovery = discover(package); row = discovery['scenes'][0]
            self.assertEqual(discovery['source_type'], 'fantasy_grounds')
            self.assertEqual(len(discovery['scenes']), 2)  # ART hidden
            self.assertEqual(row['pixels_per_square'], 100)
            self.assertIn('100 px/square', scene_label(row))
            result = convert(package, root / 'out', scene_keys=[row['key']])
            self.assertEqual(result['status'], 'PASS')
            native = result['scenes'][0]['native_report']; fg = native['fantasy_grounds']
            self.assertEqual(fg['counts'], {'walls': 2, 'doors': 1, 'windows': 1, 'lights': 2, 'lights_off': 1, 'terrain': 1})
            # FG polylines split into native straight barrier records.
            self.assertEqual(native['native_synthesis']['records'], {'walls': 5, 'doors': 2, 'lights': 2, 'image': 1})
            self.assertEqual(native['output_names']['map_path'], 'MyAssets/Maps/ForgeBridge test/Layered Map.rwmap')
            self.assertEqual(native['output_names']['notes_folder'], 'ForgeBridge test')
            files = read_package(root / 'out/scene-001/native-package.zip')
            self.assertTrue(any(p.endswith('.rwnote') for p in files))
            self.assertEqual(len([p for p in files if p.startswith('MyAssets/')]), 14)
            reader = Reader(files[native['output_names']['map_path']]); graph = reader.read()
            tiles = reader.objects[reader.objects[graph['root_id']]['members']['_tiles']['ref']]
            self.assertEqual(tiles['members']['_size'], 11)
            self.assertEqual(len(native['placements']['markers']),1)
            self.assertGreater(check_metadata_references(files), 0)
            self.assertTrue({'terrain', 'windows'} <= {l['field'] for l in fg['losses']})
            summary = report_text(result)
            for text in ['Fantasy Grounds module', 'lights_off: 1', 'Metadata: db.xml', 'terrain']:
                self.assertIn(text, summary)
            self.assertEqual(package.read_bytes(), before)

    def test_needs_grid_refuses_then_resamples_fractional_grid_and_cli_bare_squares(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = needs_grid(root); row = discover(package)['scenes'][0]
            self.assertEqual(row['status'], 'NEEDS_GRID')
            refused = convert(package, root / 'refused')
            self.assertEqual(refused['status'], 'PARTIAL')
            self.assertIn('no grid size', refused['scenes'][0]['error'])
            self.assertFalse(list((root / 'refused').rglob('*.rwmap')))
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(['convert', str(package), '--squares', '40', '--out', str(root / 'out')]), 0)
            result = json.loads(output.getvalue()); native = result['scenes'][0]['native_report']
            self.assertEqual(native['fantasy_grounds']['pixels_per_square'], 51.2)
            self.assertEqual(native['fantasy_grounds']['resampling']['output_size_px'], [2040, 1020])
            self.assertEqual(native['native_synthesis']['records']['walls'], 3)
            keyed = convert(package, root / 'keyed', grid_size=[row['key'] + '=51.2'])
            self.assertEqual(keyed['scenes'][0]['fantasy_grounds']['uvtt_pixels_per_grid'], 51)

    def test_stored_grid_wins_and_grid_overrides_are_scoped_and_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = module(root); rows = discover(package)['scenes']
            result = convert(package, root / 'out', scene_keys=[rows[0]['key']], grid_size=['50'], squares=['1000'])
            self.assertEqual(result['scenes'][0]['fantasy_grounds']['pixels_per_square'], 100)
            for options in [{'grid_size': ['50']}, {'squares': ['unknown=10']},
                            {'grid_size': [rows[0]['key'] + '=nan']}, {'squares': [rows[0]['key'] + '=0']}]:
                with self.subTest(options=options), self.assertRaises(ValueError): convert(package, root / 'bad', **options)

    def test_art_filter_folder_and_vault_discovery_match_mod_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = module(root); standard = discover(package)
            self.assertEqual(standard['hidden_art'], 1)
            all_rows = discover(package, include_art=True)['scenes']
            self.assertEqual(len(all_rows), 3); self.assertEqual(all_rows[-1]['status'], 'ART')
            folder = root / 'folder'; folder.mkdir(); vault = root / 'vault.zip'
            with zipfile.ZipFile(package) as src, zipfile.ZipFile(vault, 'w') as dst:
                for name in src.namelist():
                    file = folder / name; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(src.read(name))
                    dst.writestr('modules/Test/' + name, src.read(name))
            self.assertEqual(discover(folder), standard); self.assertEqual(discover(vault), standard)
            built = convert(vault, root / 'out', scene_keys=[standard['scenes'][0]['key']])
            self.assertEqual(built['status'], 'PASS')

    def test_encrypted_input_refused_by_convert_and_headless_gui(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = module(root); encrypt_flag(package)
            with self.assertRaisesRegex(ValueError, 'encrypted'): convert(package, root / 'out')
            self.assertFalse((root / 'out').exists())
            with redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit) as stopped:
                main(['convert', str(package), '--out', str(root / 'out')])
            self.assertEqual(stopped.exception.code, 2); self.assertIn('encrypted', error.getvalue())
            def scenario(ui):
                click(ui, 'Discover scenes'); finish_job(ui)
                self.assertIn('encrypted', ui['errors'][0][1])
            with patch('forgebridge.gui.convert') as converter:
                run_headless_gui(scenario, package=package); converter.assert_not_called()

    def test_fake_install_and_uninstall_use_existing_receipts_and_preserve_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = module(root); key = discover(package)['scenes'][0]['key']
            assets = root / 'MyAssets'; assets.mkdir(); (assets / 'user.txt').write_text('keep')
            backups = root / 'Backups'
            with patch('forgebridge.installer.require_toolkit_closed'), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(['convert', str(package), '--scene-key', key, '--out', str(root / 'out'),
                    '--map-folder', 'Our module', '--notes-folder', 'Future notes', '--map-name', key + '=Our map',
                    '--install', '--myassets', str(assets), '--backup-root', str(backups)]), 0)
            result = json.loads(output.getvalue()); install = result['installation']
            self.assertEqual(install['added'], 14)
            self.assertTrue((assets / 'Maps/Our module/Our map.rwmap').is_file())
            with patch('forgebridge.installer.require_toolkit_closed'):
                removed = uninstall(install['receipt'])
            self.assertEqual(removed['removed'], 14)
            self.assertEqual([p.name for p in assets.rglob('*') if p.is_file()], ['user.txt'])

    def test_gui_grid_prompts_and_art_toggle_reach_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = needs_grid(tmp); report = discover(package); row = report['scenes'][0]
            def scenario(ui):
                click(ui, 'Discover scenes'); finish_job(ui); ui['list'].selection_set(0)
                click(ui, 'Build / export'); self.assertEqual(ui['errors'][-1][0], 'Grid required')
                ui['simpledialog'].askfloat = lambda *a, **kw: 40.0
                click(ui, 'Squares across'); click(ui, 'Build / export')
            with patch('forgebridge.gui.discover', return_value=report), patch('forgebridge.gui.convert') as converter:
                run_headless_gui(scenario)
                self.assertEqual(converter.call_args.kwargs['squares'], {row['key']: 40.0})
                self.assertFalse(converter.call_args.kwargs['include_art'])
            def toggle(ui):
                ui['fields']['Include artwork (FG ART)'].set(True)
                click(ui, 'Include artwork (FG ART)'); finish_job(ui)
            with patch('forgebridge.gui.discover', return_value=report) as discovery:
                run_headless_gui(toggle)
                discovery.assert_called_once_with('test-source', include_art=True)

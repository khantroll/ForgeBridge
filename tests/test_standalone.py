from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from forgebridge.cli import main
from forgebridge.version import get_version, PackageNotFoundError
from forgebridge.gui_errors import error_log, report_error
from forgebridge.validate import repo_schema, InventoryFatal, load_schema, validate
from forgebridge.inventory import inventory_path
from test_gui import run_headless_gui, click, finish_job


class StandaloneTests(unittest.TestCase):
    def test_release_version_matches_metadata_and_source_fallback(self):
        from forgebridge import __version__
        metadata = tomllib.loads((Path(__file__).resolve().parents[1] / 'pyproject.toml').read_text())
        self.assertEqual(metadata['project']['version'], '0.13.0')
        self.assertEqual(__version__, metadata['project']['version'])
        with tempfile.TemporaryDirectory() as tmp, \
                patch('forgebridge.version.version', side_effect=PackageNotFoundError), \
                patch('forgebridge.version.__file__', str(Path(tmp) / 'version.py')):
            self.assertEqual(get_version(), metadata['project']['version'])

    def test_gui_version_exits_before_creating_a_window(self):
        from forgebridge.gui import main as gui_main
        with patch('forgebridge.gui.get_version', return_value='0.13.0'), redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as stopped:
                gui_main(['--version'])
        self.assertEqual(stopped.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), 'ForgeBridge 0.13.0')

    def test_generator_release_version_does_not_change_the_ir_version(self):
        fixture = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'
        document = inventory_path(fixture)
        self.assertEqual(document['generator']['version'], get_version())
        self.assertEqual(document['ir_version'], '0.1.0')
        self.assertEqual(validate(document, load_schema()), [])
        document['generator']['version'] = '0.13.0'
        self.assertEqual(validate(document, load_schema()), [])
        document['ir_version'] = '0.13.0'
        self.assertTrue(validate(document, load_schema()))
    def test_gui_title_and_callback_exception_handler(self):
        def scenario(ui):
            self.assertIn('ForgeBridge 0.13.0', ui['title'])
            value = ValueError('callback failure')
            ui['root'].report_callback_exception(type(value), value, None)
        with patch('forgebridge.gui.get_version', return_value='0.13.0'), patch('forgebridge.gui.report_error') as reporter:
            run_headless_gui(scenario)
            self.assertEqual(reporter.call_args.args[0], 'callback failure')
            self.assertEqual(reporter.call_args.kwargs['output'], 'test-output')

    def test_cli_version_needs_no_package_argument(self):
        with patch('forgebridge.cli.get_version', return_value='0.13.0'), redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as stopped: main(['--version'])
        self.assertEqual(stopped.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), 'ForgeBridge 0.13.0')

    def test_version_metadata_then_embedded_fallback(self):
        with patch('forgebridge.version.version', return_value='0.13.0'):
            self.assertEqual(get_version(), '0.13.0')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'build-info.json').write_text(json.dumps({'version': '0.10.1'}))
            with patch('forgebridge.version.version', side_effect=PackageNotFoundError), \
                    patch('forgebridge.version.__file__', str(root / 'version.py')):
                self.assertEqual(get_version(), '0.10.1')

    def test_frozen_schema_is_self_contained_and_never_borrows_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root / 'internal/forgebridge'; (package / 'schema').mkdir(parents=True)
            bundled = package / 'schema/test.json'; bundled.write_text('{}')
            (root / 'schema').mkdir(); (root / 'schema/test.json').write_text('{"wrong":"checkout"}')
            with patch('forgebridge.validate.__file__', str(package / 'validate.py')), patch('sys.frozen', True, create=True):
                self.assertEqual(repo_schema('test.json'), bundled.resolve())
                bundled.unlink()
                with self.assertRaisesRegex(InventoryFatal, 'bundled schema not found'): repo_schema('test.json')

    def test_errors_append_beside_output_and_dispatch_visible_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); shown = []
            first = report_error('failure message', 'Traceback: first', output=root / 'new-output',
                                 show=lambda *args: shown.append(args))
            self.assertEqual(first, root / 'forgebridge-error.log')
            second = error_log('second failure', root / 'new-output')
            self.assertEqual(first, second)
            self.assertIn('Traceback: first', first.read_text()); self.assertIn('second failure', first.read_text())
            self.assertIn('failure message', shown[0][1]); self.assertIn(str(first), shown[0][1])

    def test_log_fallback_when_output_parent_is_not_writable_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); occupied = root / 'occupied'; occupied.write_text('keep')
            with patch.dict('os.environ', {'LOCALAPPDATA': str(root / 'local')}):
                path = error_log('fallback trace', occupied / 'output')
            self.assertEqual(path, root / 'local/ForgeBridge/forgebridge-error.log')
            self.assertEqual(occupied.read_text(), 'keep')

    def test_gui_worker_errors_preserve_traceback_and_output_location(self):
        def scenario(ui): click(ui, 'Discover scenes'); finish_job(ui)
        with patch('forgebridge.gui.discover', side_effect=RuntimeError('worker failure')), \
                patch('forgebridge.gui.report_error') as reporter:
            run_headless_gui(scenario)
            self.assertEqual(reporter.call_args.args[0], 'worker failure')
            self.assertIn('Traceback', reporter.call_args.args[1])
            self.assertEqual(reporter.call_args.kwargs['output'], 'test-output')

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from forgebridge.cli import main
from forgebridge.convert import discover, convert
from forgebridge.gui import native_outputs, install_outputs, report_text, populate_scenes, scene_label, main as gui_main


class FakeListbox:
    def __init__(self, *args, **kwargs):
        self.items, self.selected = [], set()

    def pack(self, **kwargs): pass

    def delete(self, *args):
        self.items.clear(); self.selected.clear()

    def insert(self, where, value): self.items.append(value)

    def selection_clear(self, *args): self.selected.clear()

    def selection_set(self, start, end=None):
        stop = len(self.items) - 1 if end == 'end' else start if end is None else end
        self.selected.update(range(start, stop + 1))

    def curselection(self): return tuple(sorted(self.selected))


def run_headless_gui(scenario):
    """Exercise the actual callbacks with inert widgets; never instantiate Tk."""
    ui = {'buttons': {}, 'labels': [], 'afters': [], 'list': FakeListbox()}

    class Variable:
        def __init__(self, value=''): self.value, self.callbacks = value, []
        def get(self): return self.value
        def set(self, value):
            self.value = value
            for callback in self.callbacks: callback()
        def trace_add(self, mode, callback): self.callbacks.append(callback)

    class Widget:
        def __init__(self, *args, **kwargs):
            self.options = kwargs
            if 'command' in kwargs: ui['buttons'][kwargs['text']] = self
            if 'textvariable' in kwargs: ui['labels'].append(kwargs['textvariable'])
        def pack(self, **kwargs): pass
        def configure(self, **kwargs): self.options.update(kwargs)
        def delete(self, *args): pass
        def insert(self, *args): pass

    class Root:
        def title(self, *args): pass
        def geometry(self, *args): pass
        def protocol(self, *args): pass
        def after(self, delay, callback): ui['afters'].append(callback)
        def mainloop(self): scenario(ui)

    class Thread:
        def __init__(self, target, **kwargs): self.target = target
        def start(self): self.target()

    dialogs = SimpleNamespace(askdirectory=lambda **kw: '', askopenfilename=lambda **kw: '')
    messages = SimpleNamespace(showerror=lambda *args: ui.setdefault('errors', []).append(args),
                               askyesno=lambda *args: ui.setdefault('confirmations', []).append(args) or False)
    tk = SimpleNamespace(Tk=Root, StringVar=Variable, Listbox=lambda *a, **kw: ui['list'], Text=Widget,
                         filedialog=dialogs, messagebox=messages,
                         ttk=SimpleNamespace(Frame=Widget, Label=Widget, Entry=Widget, Button=Widget))
    ui['dialogs'] = dialogs
    with patch.dict('sys.modules', {'tkinter': tk}), patch('forgebridge.gui.threading.Thread', Thread):
        return gui_main(['--package', 'test-source', '--out', 'test-output'])


def click(ui, label): ui['buttons'][label].options['command']()


def finish_job(ui): ui['afters'].pop(0)()


class GuiControllerTests(unittest.TestCase):
    def test_discovery_starts_empty_and_selection_buttons_are_explicit(self):
        report = {'scenes': [{'key': 'b', 'id': 'same', 'name': 'B', 'source_path': 'packs/scenes'},
                             {'key': 'a', 'id': 'other', 'name': 'A', 'source_path': 'packs/scenes'}]}
        def scenario(ui):
            click(ui, 'Discover scenes'); finish_job(ui)
            self.assertEqual(ui['list'].curselection(), ())
            self.assertIn('2 scenes found. Select the scenes to convert, then choose an output folder.',
                          [v.get() for v in ui['labels']])
            click(ui, 'Build / export')
            self.assertEqual(ui['errors'][-1][0], 'Selection required')
            click(ui, 'Select all'); self.assertEqual(ui['list'].curselection(), (0, 1))
            click(ui, 'Clear'); self.assertEqual(ui['list'].curselection(), ())
        with patch('forgebridge.gui.discover', return_value=report), patch('forgebridge.gui.convert') as converter:
            run_headless_gui(scenario)
            converter.assert_not_called()

    def test_sorted_display_row_key_is_the_one_converted(self):
        report = {'scenes': [
            {'key': 'z-key', 'id': 'same', 'name': 'A scene', 'source_path': 'packs/sa',
             'parent_adventure_name': 'Z Adventure', 'parent_adventure_id': 'z'},
            {'key': 'a-later', 'id': 'different', 'name': 'Z scene', 'source_path': 'packs/5e',
             'parent_adventure_name': 'A Adventure', 'parent_adventure_id': 'a'},
            {'key': 'a-key', 'id': 'same', 'name': 'A scene', 'source_path': 'packs/5e',
             'parent_adventure_name': 'A Adventure', 'parent_adventure_id': 'a'}]}
        def scenario(ui):
            click(ui, 'Discover scenes'); finish_job(ui)
            self.assertEqual(ui['list'].items, ['A scene — A Adventure (5e)',
                                               'Z scene — A Adventure (5e)', 'A scene — Z Adventure (sa)'])
            ui['list'].selection_set(0)
            click(ui, 'Build / export')
        with patch('forgebridge.gui.discover', return_value=report), patch('forgebridge.gui.convert') as converter:
            run_headless_gui(scenario)
            converter.assert_called_once_with('test-source', 'test-output', scene_keys=['a-key'], profiles=[])

    def test_pack_fallback_and_rediscovery_clear_previous_selection(self):
        row = {'key': 'one', 'id': 'id', 'name': 'Room', 'source_path': 'packs/scenes.db',
               'parent_adventure_name': None}
        self.assertEqual(scene_label(row), 'Room — scenes.db')
        widget = FakeListbox(); widget.insert('end', 'old'); widget.selection_set(0)
        rows = populate_scenes(widget, {'scenes': [row]})
        self.assertEqual(rows, [row]); self.assertEqual(widget.curselection(), ())

    def test_output_path_preview_tracks_output_choice(self):
        def scenario(ui):
            previews = [v for v in ui['labels'] if v.get().startswith('Folder to create:')]
            self.assertEqual(previews[0].get(), 'Folder to create: test-output')
            ui['dialogs'].askdirectory = lambda **kwargs: 'parent-folder'
            with patch('forgebridge.gui.uuid.uuid4', return_value=SimpleNamespace(hex='12345678abcdef')):
                click(ui, 'Choose where to save output')
            self.assertEqual(previews[0].get(), 'Folder to create: ' + str(Path('parent-folder') / 'ForgeBridge-output-12345678'))
        run_headless_gui(scenario)

    def test_discovery_names_follow_parent_record_without_changing_scoped_keys(self):
        fixture = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'
        documents = [{'document_type': 'Scene', 'id': 'shared', 'name': 'Room',
                      'source_path': 'packs/' + pack,
                      'retained_fields': {'_forgebridge_parent_adventure': {'id': 'shared-parent', 'name': name}}}
                     for pack, name in [('adventure-5e', 'Fifth Edition'), ('adventure-sa', 'System Agnostic')]]
        documents.append({'document_type': 'Scene', 'id': 'standalone', 'name': 'Room', 'source_path': 'packs/scenes'})
        inventory = {'provenance': {'package_id': 'test'}, 'documents': documents}
        with patch('forgebridge.convert.inventory_path', return_value=inventory):
            rows = discover(fixture)['scenes']
            self.assertEqual([r['parent_adventure_name'] for r in rows], ['Fifth Edition', 'System Agnostic', None])
            self.assertNotEqual(rows[0]['key'], rows[1]['key'])
            documents[0]['retained_fields']['_forgebridge_parent_adventure']['name'] = 'Renamed'
            renamed = discover(fixture)['scenes']
            self.assertEqual([r['key'] for r in rows], [r['key'] for r in renamed])
            self.assertEqual([r['id'] for r in rows], [r['id'] for r in renamed])
            self.assertEqual([r['parent_adventure_id'] for r in rows], [r['parent_adventure_id'] for r in renamed])

    def test_install_confirmation_warns_about_preserving_note_edits(self):
        discovered = {'scenes': [{'key': 'one', 'id': 'scene', 'name': 'Room', 'source_path': 'packs/scenes'}]}
        built = {'status': 'PASS', 'scenes': [{'name': 'Room', 'status': 'BUILT', 'folder': 'scene-001',
                                             'artifact': 'native-package.zip', 'native_report': {'counts': {}}}]}
        def scenario(ui):
            click(ui, 'Discover scenes'); finish_job(ui)
            ui['list'].selection_set(0); click(ui, 'Build / export'); finish_job(ui)
            ui['dialogs'].askdirectory = lambda **kwargs: 'fake-directory'
            click(ui, 'Install reviewed native outputs')
            self.assertIn('Opening notes in the Toolkit can change them; uninstall with --keep-changed later keeps those edits.',
                          ui['confirmations'][0][1])
        with patch('forgebridge.gui.discover', return_value=discovered), patch('forgebridge.gui.convert', return_value=built), \
                patch('forgebridge.gui.native_outputs', return_value=['test.zip']), patch('forgebridge.gui.install_outputs') as installer:
            run_headless_gui(scenario)
            installer.assert_not_called()

    def test_summary_distinguishes_manual_source_losses_from_native_output(self):
        text = report_text({'status': 'PASS', 'counts': {'unsupported': 3},
            'scenes': [{'id': 'a', 'name': 'Room', 'status': 'MANUAL', 'folder': 'scene-001',
                        'artifact': 'uvtt-package.zip'}], 'manual_steps': ['Import UVTT in Toolkit']})
        self.assertIn('Source/UVTT stage: unsupported: 3', text)
        self.assertIn('Room: MANUAL', text)
        self.assertIn('Import UVTT', text)
        self.assertIn('does not prove Toolkit', text)
    def test_help_requires_no_desktop_or_tk_window(self):
        with redirect_stdout(io.StringIO()) as text, self.assertRaises(SystemExit) as stopped:
            main(['gui', '--help'])
        self.assertEqual(stopped.exception.code, 0)
        self.assertIn('local Tk front end', text.getvalue())

    def test_only_complete_native_outputs_reach_installer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root / 'scene-001'; folder.mkdir()
            package = folder / 'native-package.zip'; package.write_bytes(b'test placeholder')
            manual = {'status': 'PASS', 'scenes': [{'status': 'MANUAL', 'folder': 'scene-001', 'artifact': 'uvtt-package.zip'}]}
            with patch('forgebridge.gui.install') as installer:
                with self.assertRaisesRegex(ValueError, 'No native packages'):
                    install_outputs(manual, root, 'MyAssets', 'Backups')
                installer.assert_not_called()
                report = {'status': 'PASS', 'scenes': [{'status': 'BUILT', 'folder': 'scene-001', 'artifact': 'native-package.zip'}]}
                install_outputs(report, root, 'MyAssets', 'Backups')
                installer.assert_called_once_with([package], 'MyAssets', 'Backups')
            report['status'] = 'PARTIAL'
            with self.assertRaisesRegex(ValueError, 'rejected scenes'): native_outputs(report, root)
            report['status'] = 'PASS'; report['scenes'][0]['folder'] = '../outside'
            with self.assertRaisesRegex(ValueError, 'outside'): native_outputs(report, root)

    def test_scoped_selection_does_not_merge_identical_ids_in_two_adventures(self):
        fixture = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-module'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root / 'source'
            shutil.copytree(fixture, package)
            scene = json.loads((package / 'packs/scenes.db').read_text())
            a, b = deepcopy(scene), deepcopy(scene)
            a['name'], b['name'] = 'Adventure A scene', 'Adventure B scene'
            (package / 'packs/adventures.db').write_text('\n'.join(json.dumps({'_id': identity, 'name': name, 'scenes': [s]})
                for identity, name, s in [('adv-A', 'Z Adventure', a), ('adv-B', 'A Adventure', b)]))
            manifest = json.loads((package / 'module.json').read_text())
            manifest['packs'] = [{'name': 'adventures', 'path': 'packs/adventures.db', 'type': 'Adventure'}]
            (package / 'module.json').write_text(json.dumps(manifest))
            scenes = discover(package)['scenes']
            self.assertEqual(len(scenes), 2)
            self.assertEqual(scenes[0]['id'], scenes[1]['id'])
            self.assertNotEqual(scenes[0]['key'], scenes[1]['key'])
            displayed = populate_scenes(FakeListbox(), {'scenes': scenes})
            selected = displayed[0]
            self.assertEqual(selected['parent_adventure_name'], 'A Adventure')
            self.assertEqual(selected['parent_adventure_id'], 'adv-B')
            report = convert(package, root / 'out', scene_keys=[selected['key']])
            self.assertEqual(len(report['scenes']), 1)
            self.assertEqual(report['scenes'][0]['name'], 'Adventure B scene')
            self.assertEqual(report['scenes'][0]['parent_adventure_id'], 'adv-B')

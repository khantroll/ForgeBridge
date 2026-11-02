import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import zipfile

from forgebridge.native import NoteBuilder, Writer, smoke_files, write_smoke_zip
from forgebridge.nrbf import inspect_nrbf


def resolve(graph, value):
    return graph['objects'][value['ref']] if isinstance(value, dict) and 'ref' in value else value


def list_values(graph, value):
    members = resolve(graph, value)['members']
    array = resolve(graph, members['_items'])
    assert len(array['items']) == members['_size']
    return [resolve(graph, v) for v in array['items']]


def text_data(graph, value):
    members = resolve(graph, value)['members']
    chars = list_values(graph, members['_characters'])
    return ''.join(c['members']['_character'] for c in chars), {
        resolve(graph, c['members']['_link']) for c in chars if c['members']['_link'] is not None}


class NativeTests(unittest.TestCase):
    def test_generated_links_close_over_metadata_files(self):
        files = smoke_files()
        self.assertEqual(len(files), 4)
        for path, data in files.items():
            graph = inspect_nrbf(data)
            if path.endswith('.rwnote'):
                texts = [o for o in graph['objects'].values() if isinstance(o, dict) and o.get('class') == 'ArkenNoteFieldText']
                self.assertEqual(len(texts), 1)
                text, links = text_data(graph, texts[0]['members']['_text'])
                self.assertIn('\nSecond line: 12345.', text)
                self.assertEqual(len(links), 1)
                target = next(iter(links))
                self.assertIn(target, files)
                self.assertNotEqual(target[:-7], path[:-7])
                other = inspect_nrbf(files[target[:-7] + '.rwnote'])
                other_field = next(o for o in other['objects'].values() if isinstance(o, dict) and o.get('class') == 'ArkenNoteFieldText')
                self.assertEqual(text_data(other, other_field['members']['_text'])[1], {path[:-7] + '.rwmeta'})

    def test_table_ranges_text_and_active_list_length(self):
        data = next(v for k, v in smoke_files().items() if k.endswith('Test A.rwnote'))
        graph = inspect_nrbf(data)
        table = next(o for o in graph['objects'].values() if isinstance(o, dict) and o.get('class') == 'ArkenNoteFieldRollableTable')
        rows = list_values(graph, table['members']['_rows'])
        self.assertEqual([(r['members']['_from'], r['members']['_to'], text_data(graph, r['members']['_data'])[0]) for r in rows],
            [(1, 1, 'ForgeBridge result one'), (2, 2, 'ForgeBridge result two'), (3, 3, 'ForgeBridge result three')])

    def test_metadata_names_and_no_old_map_references(self):
        for path, data in smoke_files().items():
            graph = inspect_nrbf(data)
            root = graph['objects'][graph['root_id']]
            name = resolve(graph, root['members']['_name'])
            self.assertTrue(path.endswith(name + ('.rwmeta' if path.endswith('.rwmeta') else '.rwnote')))
            self.assertFalse(any(isinstance(o, str) and ('FB Test ' in o or 'New Map' in o or 'bowers1950' in o) for o in graph['objects'].values()))
            if path.endswith('.rwmeta'):
                self.assertEqual(list_values(graph, root['members']['_links']), [])

    def test_repeated_fields_have_matching_inherited_values(self):
        for data in smoke_files().values():
            graph = inspect_nrbf(data)
            for o in graph['objects'].values():
                if isinstance(o, dict) and 'members' in o:
                    for name, value in o['members'].items():
                        if '+' in name and name.split('+')[-1] in o['members']:
                            self.assertEqual(value, o['members'][name.split('+')[-1]])

    def test_bmp_text_and_empty_text(self):
        b = NoteBuilder()
        for text in ('', 'café — Ω\n'):
            node = b.text([(text, None)])
            graph = inspect_nrbf(Writer(b.schema['libraries']).write(node))
            self.assertEqual(text_data(graph, {'ref': graph['root_id']})[0], text)

    def test_invalid_text_links_and_table_ranges_fail(self):
        b = NoteBuilder()
        for text, link in [('😀', None), ('x' * 64001, None), ('x', '../../bad.rwmeta')]:
            with self.assertRaises(ValueError): b.text([(text, link)])
        for rows in ([], [(0, 1, 'bad')], [(2, 1, 'bad')], [(1, 2, 'one'), (2, 3, 'overlap')], [(True, 1, 'bool')]):
            with self.assertRaises(ValueError): b.table_field('test', rows, 1)

    def test_zip_only_contains_generated_note_folder_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'test.zip'
            self.assertEqual(write_smoke_zip(p), 4)
            with zipfile.ZipFile(p) as z:
                self.assertEqual(set(z.namelist()), set(smoke_files()))
                self.assertIsNone(z.testzip())
            before = p.read_bytes()
            with self.assertRaises(ValueError): write_smoke_zip(p)
            self.assertEqual(p.read_bytes(), before)

    def test_cli_creates_test_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'smoke.zip'
            result = subprocess.run([sys.executable, '-m', 'forgebridge.native', '--out', str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('unverified', result.stdout)
            self.assertTrue(p.exists())

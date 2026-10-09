import copy
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
import zipfile

from forgebridge.native_export import companion_files, write_companion_zip
from forgebridge.nrbf import inspect_nrbf
from test_native import list_values, text_data


def source():
    origin = {'source_path': 'packs/adventure', 'parent_adventure_id': 'adventure'}
    journal = {'document_type': 'JournalEntry', 'source': origin, 'payload': {
        '_id': 'j', 'name': 'Rooms', 'ownership': {'default': 0}, 'pages': [
            {'_id': 'a', 'name': 'A', 'text': {'content': '<p>See @UUID[.b]{B} and @UUID[RollTable.t]{Table}.</p><script>BAD()</script>', 'format': 1}},
            {'_id': 'b', 'name': 'B', 'text': {'content': 'Back @UUID[.a]{A}', 'format': 2}},
            {'_id': 'c', 'name': 'Image', 'src': 'private/image.webp', 'type': 'image'}]}}
    table = {'document_type': 'RollTable', 'source': origin, 'payload': {
        '_id': 't', 'name': 'Outcomes', 'formula': '1d2', 'replacement': True,
        'results': [{'name': 'One', 'description': '<p>First</p>', 'type': 'text', 'range': [1, 1], 'weight': 1},
                    {'name': 'Two', 'description': '<p>Second</p>', 'type': 'text', 'range': [2, 2], 'weight': 1}]}}
    refs = [{'uuid': uuid, 'origin': {'document_index': 0, 'path': f'pages[{pi}].text.content'},
             'status': 'resolved', 'target': {'document_index': di, 'page_index': target, 'anchor': ''}}
            for uuid, pi, di, target in [('.b', 0, 0, 1), ('RollTable.t', 0, 1, None), ('.a', 1, 0, 0)]]
    return {'scene_notes': {'scene_id': 'scene', 'scene_name': 'Test scene', 'journals': [copy.deepcopy(journal)],
        'notes': [{'note_id': 'n', 'title': 'A', 'status': 'resolved', 'journal_index': 0, 'page_index': 0, 'position': {'x': 2, 'y': 3}}],
        'dependencies': {'documents': [journal, table], 'references': refs, 'truncated': False}, 'read_errors': []}}


def recovered(files):
    texts, links, tables = [], set(), []
    for path, data in files.items():
        if not path.endswith('.rwnote'):
            continue
        graph = inspect_nrbf(data)
        for obj in graph['objects'].values():
            if not isinstance(obj, dict):
                continue
            if obj.get('class') == 'ArkenTextString':
                value, targets = text_data(graph, obj)
                texts.append(value)
                links.update(targets)
            elif obj.get('class') == 'ArkenNoteFieldRollableTable':
                tables.append([(r['members']['_from'], r['members']['_to'], text_data(graph, r['members']['_data'])[0])
                               for r in list_values(graph, obj['members']['_rows'])])
    return texts, links, tables


class NativeExportTests(unittest.TestCase):
    def test_pages_cycles_and_all_targets_exist(self):
        files, report = companion_files(source())
        texts, links, tables = recovered(files)
        self.assertEqual(report['counts']['notes'], 6)
        self.assertEqual(report['counts']['rewritten_uuid_occurrences'], 3)
        self.assertEqual(report['counts']['unresolved_uuid_occurrences'], 0)
        self.assertTrue(links)
        self.assertTrue(links <= set(files))
        self.assertTrue(all(p.startswith(report['native_folder'] + '/') for p in links))
        self.assertFalse(any('BAD()' in t or '@UUID[' in t for t in texts))
        self.assertEqual(tables, [[(1, 1, 'One\nFirst'), (2, 2, 'Two\nSecond')]])
        self.assertTrue(any(t == 'private/image.webp' for t in texts))

    def test_source_preserved_exactly_and_no_map_generated(self):
        original = source()
        before = copy.deepcopy(original)
        files, report = companion_files(original)
        self.assertEqual(original, before)
        self.assertEqual(json.loads(files['source-companion.json']), original)
        self.assertFalse(any(p.endswith('.rwmap') for p in files))
        placement = report['placements'][0]
        self.assertEqual(placement['grid_position'], {'x': 2, 'y': 3})
        self.assertIn(placement['target'], files)
        self.assertFalse(placement['native_map_placement'])
        self.assertIn('visibility', report['permissions'])

    def test_missing_unscanned_and_anchor_links_are_explicit(self):
        x = source()
        graph = x['scene_notes']['dependencies']
        graph['references'][0]['status'] = 'missing_page'
        graph['references'][1]['target']['anchor'] = 'section'
        graph['documents'][0]['payload']['pages'][1]['text']['content'] += ' @UUID[.missing]{Lost}'
        files, report = companion_files(x)
        texts, links, _ = recovered(files)
        self.assertTrue(any('@UUID[.b]{B}' in t for t in texts))
        self.assertEqual({r['status'] for r in report['unresolved_links']}, {'missing_page'})
        self.assertTrue(any(i['code'] == 'anchor_not_preserved' for i in report['issues']))

    def test_unsupported_table_semantics_never_become_rollable(self):
        for change in ({'formula': '2d6'}, {'replacement': False}):
            x = source()
            x['scene_notes']['dependencies']['documents'][1]['payload'].update(change)
            files, report = companion_files(x)
            self.assertEqual(recovered(files)[2], [])
            self.assertEqual(report['counts']['native_tables'], 0)
            self.assertTrue(any(i['code'] == 'table_semantics_reference_only' for i in report['issues']))
        for change in ({'range': [1, 2]}, {'weight': 3}, {'documentUuid': 'Actor.x'}, {'type': 'document'}):
            x = source()
            x['scene_notes']['dependencies']['documents'][1]['payload']['results'][0].update(change)
            self.assertEqual(companion_files(x)[1]['counts']['native_tables'], 0)

    def test_unicode_and_html_losses_are_reported(self):
        x = source()
        x['scene_notes']['dependencies']['documents'][0]['payload']['pages'][1]['text'] = {
            'content': '<p>😀 <a href="https://example.com">site</a><img src="x.png"></p>'}
        files, report = companion_files(x)
        codes = {i['code'] for i in report['issues']}
        self.assertTrue({'unicode_replaced', 'html_link_reference_only', 'media_reference_only'} <= codes)
        self.assertTrue(any('�' in t for t in recovered(files)[0]))

    def test_deterministic_paths_and_distinct_imports(self):
        x = source()
        a, ar = companion_files(x)
        b, br = companion_files(x)
        self.assertEqual(a, b)
        x['scene_notes']['dependencies']['documents'][0]['payload']['name'] = 'Changed'
        self.assertNotEqual(ar['native_folder'], companion_files(x)[1]['native_folder'])

    def test_missing_or_large_graph_rejected(self):
        with self.assertRaises(ValueError): companion_files({})
        x = source()
        x['scene_notes']['dependencies']['documents'] *= 129
        with self.assertRaises(ValueError): companion_files(x)

    def test_zip_layout_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = Path(tmp) / 'source.json', Path(tmp) / 'native.zip'
            src.write_text(json.dumps(source()))
            report = write_companion_zip(src, dest)
            with zipfile.ZipFile(dest) as z:
                self.assertIsNone(z.testzip())
                self.assertIn('INSTALL.txt', z.namelist())
                self.assertEqual(json.loads(z.read('conversion-report.json')), report)
                self.assertFalse(any('..' in Path(p).parts for p in z.namelist()))
            before = dest.read_bytes()
            with self.assertRaises(ValueError): write_companion_zip(src, dest)
            self.assertEqual(dest.read_bytes(), before)

    def test_companion_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = Path(tmp) / 'source.json', Path(tmp) / 'native.zip'
            src.write_text(json.dumps(source()))
            result = subprocess.run([sys.executable, '-m', 'forgebridge.native', '--companion', str(src), '--out', str(dest)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('6 native notes', result.stdout)
            self.assertTrue(dest.exists())

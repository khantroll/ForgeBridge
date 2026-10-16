"""Journal correlation must not mix Adventure variants or execute rich text."""
import io
import json
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from forgebridge.notes import correlate_notes, render_notes_text
from forgebridge.uvtt import build_uvtt_slice, _journal_pack_payloads
from forgebridge.cli import main
from forgebridge.validate import InventoryFatal


class NotesTests(unittest.TestCase):
    def candidate(self, *, priority=0, name='Crypt', pages=None, source='packs/adventure.json'):
        return {'priority': priority, 'source': {'pack': 'adventure', 'source_path': source,
                                               'parent_adventure_id': 'adventure'},
                'payload': {'_id': 'journal', 'name': name, 'ownership': {'default': 0},
                            'pages': pages if pages is not None else [
                                {'_id': 'page', 'name': 'Room One', 'type': 'text',
                                 'text': {'format': 1, 'content': '<p>Room description</p>'},
                                 'flags': {'preserved': True}}]}}

    def scene(self, notes=None):
        return {'_id': 'scene', 'name': 'Crypt', 'width': 4000, 'height': 4200,
                'padding': .25, 'grid': {'type': 1, 'size': 100, 'distance': 5},
                'background': {'src': 'map.png'},
                'notes': notes if notes is not None else [
                    {'_id': 'note', 'entryId': 'journal', 'pageId': 'page', 'x': 3450, 'y': 1750}]}

    def test_exact_page_origin_and_full_journal_retention(self):
        c = self.candidate()
        b = correlate_notes(self.scene(), [c], (1000, 1100), 100)
        self.assertEqual(b['counts'], {'resolved': 1})
        self.assertEqual(b['notes'][0]['position'], {'x': 24.5, 'y': 6.5})
        self.assertEqual(b['notes'][0]['title'], 'Room One')
        self.assertEqual(b['journals'][0]['payload'], c['payload'])
        self.assertIn('Room description', render_notes_text(b))

    def test_adventure_scope_wins_over_same_id_in_other_sources(self):
        c = self.candidate()
        other = self.candidate(priority=2, name='Wrong variant', source='other')
        b = correlate_notes(self.scene(), [other, c], (0, 0), 100)
        self.assertEqual(b['journals'][0]['payload']['name'], 'Crypt')

    def test_missing_ambiguous_and_unqualified_links_never_choose_substitute(self):
        for candidates, note, status in [([], {'entryId': 'journal'}, 'missing_entry'),
                                         ([self.candidate(), self.candidate()], {'entryId': 'journal'}, 'ambiguous_entry'),
                                         ([self.candidate()], {'entryId': 'journal', 'pageId': 'bad'}, 'missing_page'),
                                         ([self.candidate()], {'entryId': 'Compendium.unavailable.pack.journal'}, 'missing_entry'),
                                         ([], {'text': 'A label'}, 'label_only'),
                                         ([], {'entryId': ['bad']}, 'invalid_reference')]:
            with self.subTest(status=status):
                b = correlate_notes(self.scene([note]), candidates, (0, 0), 100)
                self.assertEqual(b['notes'][0]['status'], status)
                self.assertNotIn('Room description', render_notes_text(b))

    def test_whole_entry_and_legacy_text_are_supported(self):
        scene = self.scene([{'entryId': 'JournalEntry.journal'}])
        c = self.candidate(pages=[])
        c['payload']['content'] = '<p>Old journal</p>'
        b = correlate_notes(scene, [c], (0, 0), 100)
        self.assertEqual(b['counts'], {'resolved': 1})
        self.assertIn('Old journal', render_notes_text(b))

    def test_duplicate_page_and_invalid_position_remain_explicit(self):
        c = self.candidate()
        c['payload']['pages'].append(dict(c['payload']['pages'][0]))
        scene = self.scene()
        scene['notes'][0]['x'] = 'invalid'
        b = correlate_notes(scene, [c], (0, 0), 100)
        self.assertEqual(b['notes'][0]['status'], 'ambiguous_page')
        self.assertIsNone(b['notes'][0]['position'])
        self.assertNotIn('Room description', render_notes_text(b))

    def test_active_html_stays_in_json_and_is_not_in_readable_output(self):
        c = self.candidate()
        c['payload']['pages'][0]['text']['content'] = '<p>Hello &amp; welcome</p><script>evil()</script><img src="https://example.invalid/a" onerror="evil()">'
        b = correlate_notes(self.scene(), [c], (0, 0), 100)
        self.assertIn('evil()', json.dumps(b))
        plain = render_notes_text(b)
        self.assertIn('Hello & welcome', plain)
        self.assertNotIn('evil()', plain)
        self.assertNotIn('https://example.invalid', plain)

    def fixture(self, root, storage='json', adventure=True):
        Image.new('RGB', (40, 42)).save(root / 'map.png')
        (root / 'packs').mkdir()
        scene = self.scene()
        if adventure:
            objects = [{'_id': 'adventure', 'name': 'Adventure', 'scenes': [scene],
                        'journal': [self.candidate()['payload']]},
                       {'_id': 'other', 'name': 'Other variant', 'scenes': [],
                        'journal': [self.candidate(name='Wrong')['payload']]}]
            typ, collection = 'Adventure', 'adventures'
        else:
            objects = [self.candidate()['payload']]
            typ, collection = 'JournalEntry', 'journal'
            (root / 'packs/scenes.json').write_text(json.dumps([scene]))
        path = f'packs/{collection}' + ('.json' if storage == 'json' else '.db' if storage == 'nedb' else '')
        if storage == 'leveldb':
            import plyvel_next as plyvel
            db = plyvel.DB(str(root / path), create_if_missing=True)
            for obj in objects:
                db.put(f"!{collection}!{obj['_id']}".encode(), json.dumps(obj).encode())
            db.close()
        else:
            (root / path).write_text(json.dumps(objects) if storage == 'json' else '\n'.join(json.dumps(o) for o in objects))
        packs = [{'name': collection, 'path': path, 'type': typ}]
        if not adventure:
            packs.append({'name': 'scenes', 'path': 'packs/scenes.json', 'type': 'Scene'})
        (root / 'module.json').write_text(json.dumps({'id': 'notes-test', 'title': 'Notes test', 'packs': packs}))

    def test_adventure_and_standalone_journals_in_all_supported_storage(self):
        for storage in ['json', 'nedb', 'leveldb']:
            for adventure in [True, False]:
                with self.subTest(storage=storage, adventure=adventure), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    self.fixture(root, storage, adventure)
                    d = build_uvtt_slice(root, 'scene')
                    self.assertEqual(d['scene_notes']['counts'], {'resolved': 1})
                    self.assertEqual(d['scene_notes']['read_errors'], [])
                    self.assertEqual(d['scene_notes']['journals'][0]['payload']['name'], 'Crypt')
                    self.assertEqual(d['source_scene'], self.scene())

    def test_zip_cli_writes_correlated_companion_and_readable_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'module'; root.mkdir()
            self.fixture(root)
            archive = Path(tmp) / 'module.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                for p in root.rglob('*'):
                    if p.is_file():
                        z.write(p, p.relative_to(root))
            dest = Path(tmp) / 'out' / 'scene.uvtt'
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(archive), '--uvtt-scene', 'scene', '--uvtt-out', str(dest)]), 0)
            companion = json.loads(dest.with_suffix('.forgebridge.json').read_text())
            self.assertEqual(companion['scene_notes']['counts'], {'resolved': 1})
            self.assertIn('Room description', dest.with_suffix('.notes.txt').read_text())
            self.assertNotIn('scene_notes', json.loads(dest.read_text()))

    def test_adventure_dependency_loader_follows_journal_to_table_in_each_storage(self):
        for storage in ['json', 'nedb', 'leveldb']:
            with self.subTest(storage=storage), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root, storage)
                if storage == 'leveldb':
                    import plyvel_next as plyvel
                    db = plyvel.DB(str(root / 'packs/adventures'))
                    parent = json.loads(db.get(b'!adventures!adventure'))
                else:
                    path = root / ('packs/adventures.json' if storage == 'json' else 'packs/adventures.db')
                    objects = json.loads(path.read_text()) if storage == 'json' else [json.loads(s) for s in path.read_text().splitlines()]
                    parent = objects[0]
                parent['journal'][0]['pages'][0]['text']['content'] = '@UUID[JournalEntry.rules.JournalEntryPage.page]{Fear}'
                rules = self.candidate()['payload']; rules['_id'] = 'rules'
                rules['pages'][0]['text']['content'] = '@UUID[RollTable.fear]{Fear Table}'
                parent['journal'].append(rules)
                parent['tables'] = [{'_id': 'fear', 'name': 'Fear Table', 'formula': '1d20',
                                     'results': [{'_id': 'r', 'range': [1, 20], 'weight': 1, 'text': 'Afraid'}]}]
                if storage == 'leveldb':
                    db.put(b'!adventures!adventure', json.dumps(parent).encode()); db.close()
                else:
                    objects[0] = parent
                    path.write_text(json.dumps(objects) if storage == 'json' else '\n'.join(json.dumps(o) for o in objects))
                document = build_uvtt_slice(root, 'scene')
                graph = document['scene_notes']['dependencies']
                self.assertEqual(graph['counts'], {'resolved': 2})
                self.assertEqual(len(graph['documents']), 3)
                self.assertIn('Afraid', render_notes_text(document['scene_notes']))

    def test_journal_paths_cannot_escape_package_or_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'module'; root.mkdir()
            outside = Path(tmp) / 'outside.json'; outside.write_text('[]')
            for path in ['../outside.json', 'linked.json']:
                if path == 'linked.json':
                    try:
                        (root / path).symlink_to(outside)
                    except OSError as exc:
                        if getattr(exc, "winerror", None) != 1314:
                            raise
                        self.skipTest("Windows symlink creation privilege unavailable (WinError 1314)")
                with self.assertRaises(InventoryFatal):
                    _journal_pack_payloads(root, {'source_path': path, 'storage': 'json'})

    def test_readable_notes_output_does_not_overwrite_a_symlink_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'module'; root.mkdir()
            self.fixture(root)
            dest = Path(tmp) / 'out' / 'scene.uvtt'; dest.parent.mkdir()
            target = Path(tmp) / 'protected.txt'; target.write_text('keep')
            try:
                dest.with_suffix('.notes.txt').symlink_to(target)
            except OSError as exc:
                if getattr(exc, "winerror", None) != 1314:
                    raise
                self.skipTest("Windows symlink creation privilege unavailable (WinError 1314)")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(root), '--uvtt-scene', 'scene', '--uvtt-out', str(dest)]), 1)
            self.assertEqual(target.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()

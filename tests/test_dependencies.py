"""Dependency traversal follows exact source links, not executable expressions."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from forgebridge.dependencies import resolve_dependencies
from forgebridge.notes import correlate_notes, render_notes_text


class DependencyTests(unittest.TestCase):
    def candidate(self, kind, id, payload=None, *, path='packs/adventure', parent='adventure', pack_id=None):
        return {'document_type': kind, 'priority': 0,
                'source': {'source_path': path, 'parent_adventure_id': parent, 'pack_id': pack_id},
                'payload': {'_id': id, 'name': id, **(payload or {})}}

    def journal(self, id, html, **kwargs):
        return self.candidate('JournalEntry', id, {'pages': [{'_id': 'page', 'name': id + ' page',
                    'text': {'content': html, 'format': 1}}]}, **kwargs)

    def bundle(self, root):
        return {'journals': [{'source': root['source'], 'payload': root['payload']}]}

    def test_recursive_pages_tables_and_cycle_keep_full_data_without_repeats(self):
        root = self.journal('crypt', '@UUID[JournalEntry.rules.JournalEntryPage.page]{Fear}')
        rules = self.journal('rules', '@UUID[RollTable.fear]{Fear Table}')
        table = self.candidate('RollTable', 'fear', {'formula': '1d20', 'replacement': False,
                    'results': [{'_id': 'result', 'range': [1, 20], 'weight': 3,
                                 'text': '@UUID[JournalEntry.crypt.JournalEntryPage.page]{Back}'}]})
        candidates = [root, rules, table]
        originals = copy.deepcopy(candidates)
        graph = resolve_dependencies(self.bundle(root), candidates)
        self.assertEqual(len(graph['documents']), 3)
        self.assertEqual(graph['counts'], {'resolved': 3})
        self.assertFalse(graph['truncated'])
        self.assertEqual(candidates, originals)
        saved = next(d['payload'] for d in graph['documents'] if d['document_type'] == 'RollTable')
        self.assertEqual(saved, table['payload'])

    def test_relative_page_link_uses_the_current_journal(self):
        root = self.journal('crypt', '@UUID[.page#heading]{Local}')
        other = self.journal('other', 'Other')
        graph = resolve_dependencies(self.bundle(root), [root, other])
        self.assertEqual(graph['counts'], {'resolved': 1})
        self.assertEqual(graph['references'][0]['target'], {'document_index': 0, 'page_index': 0, 'anchor': 'heading'})

    def test_external_compendium_namespace_never_matches_by_id_only(self):
        root = self.journal('crypt', '@UUID[Compendium.available.rules.rules.JournalEntryPage.page] '
                                        '@UUID[Compendium.missing.rules.rules.JournalEntryPage.page]')
        rules = self.journal('rules', 'External', path='packs/rules', parent=None, pack_id='available.rules')
        graph = resolve_dependencies(self.bundle(root), [root, rules])
        self.assertEqual(graph['counts'], {'resolved': 1, 'missing_document': 1})

    def test_ambiguity_and_missing_pages_are_explicit(self):
        root = self.journal('crypt', '@UUID[JournalEntry.rules.JournalEntryPage.missing]')
        rules = self.journal('rules', 'Rules')
        graph = resolve_dependencies(self.bundle(root), [root, rules])
        self.assertEqual(graph['counts'], {'missing_page': 1})
        graph = resolve_dependencies(self.bundle(root), [root, rules, copy.deepcopy(rules)])
        self.assertEqual(graph['counts'], {'ambiguous_document': 1})

    def test_local_adventure_wins_and_other_adventure_is_not_a_fallback(self):
        root = self.journal('crypt', '@UUID[JournalEntry.rules]')
        rules = self.journal('rules', 'Right')
        wrong = self.journal('rules', 'Wrong', path='packs/other', parent='other')
        graph = resolve_dependencies(self.bundle(root), [root, wrong, rules])
        self.assertEqual(graph['counts'], {'resolved': 1})
        self.assertEqual(graph['documents'][1]['payload'], rules['payload'])
        graph = resolve_dependencies(self.bundle(root), [root, wrong])
        self.assertEqual(graph['counts'], {'missing_document': 1})

    def test_table_document_result_links_are_followed_but_rolls_are_not_evaluated(self):
        root = self.journal('crypt', '@UUID[RollTable.fear]')
        table = self.candidate('RollTable', 'fear', {'formula': 'not executable()', 'results': [
            {'range': [1, 1], 'weight': 1, 'documentCollection': 'JournalEntry', 'documentId': 'rules', 'text': 'Result'}]})
        rules = self.journal('rules', 'More rules')
        scene = {'_id': 'scene', 'notes': [{'entryId': 'crypt', 'pageId': 'page'}]}
        bundle = correlate_notes(scene, [root, table, rules], (0, 0), 100)
        self.assertEqual(bundle['dependencies']['counts'], {'resolved': 2})
        plain = render_notes_text(bundle)
        self.assertIn('More rules', plain)
        self.assertIn('Range [1, 1]; weight 1: Result', plain)
        self.assertIn('no roll executed', plain)

    def test_limits_report_incomplete_graph_instead_of_silently_stopping(self):
        root = self.journal('crypt', '@UUID[JournalEntry.rules] @UUID[JournalEntry.other]')
        candidates = [root, self.journal('rules', 'Rules'), self.journal('other', 'Other')]
        graph = resolve_dependencies(self.bundle(root), candidates, max_documents=1)
        self.assertTrue(graph['truncated'])
        self.assertEqual(graph['counts'], {'document_limit': 2})
        graph = resolve_dependencies(self.bundle(root), candidates, max_references=1)
        self.assertTrue(graph['truncated'])
        self.assertEqual(len(graph['references']), 1)

    def test_unknown_types_and_malformed_links_stay_unresolved(self):
        root = self.journal('crypt', '@UUID[Macro.foo] @UUID[] @UUID[.missing]')
        graph = resolve_dependencies(self.bundle(root), [root])
        self.assertEqual(graph['counts'], {'unsupported_reference': 2, 'missing_page': 1})

    def test_relative_link_to_unplaced_page_is_in_readable_reference(self):
        root = self.journal('crypt', '@UUID[.extra]{Extra room}')
        root['payload']['pages'].append({'_id': 'extra', 'name': 'Unplaced room',
                                        'text': {'content': '<p>Extra details</p>'}})
        scene = {'_id': 'scene', 'notes': [{'entryId': 'crypt', 'pageId': 'page'}]}
        bundle = correlate_notes(scene, [root], (0, 0), 100)
        self.assertEqual(bundle['dependencies']['counts'], {'resolved': 1})
        self.assertIn('Extra details', render_notes_text(bundle))


from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image
from forgebridge.cli import main
from forgebridge.convert import convert
from forgebridge.native_campaign import campaign_files
from forgebridge.scene_profile import fingerprint
from forgebridge.spell_source import spell_source, resolve_spells
from test_campaign import actor, campaign, content, document, find, node


IDS = ('MAxM77CDUu8dgIRQ', 'JbxsYXxSOTZbf9I0', '8dzaICjGy6mTUaUr')


def spell(ident=IDS[0], description='Synthetic spell text.'):
    return {'_id': ident, 'name': 'Synthetic ' + ident, 'type': 'spell', 'system': {
        'level': 1, 'school': 'div', 'activation': {'type': 'action', 'value': 1},
        'range': {'value': 60, 'units': 'ft'}, 'components': {'vocal': True},
        'duration': {'value': 1, 'units': 'minute'}, 'description': {'value': description}}}


class SpellSourceTests(unittest.TestCase):
    def test_bare_leveldb_uses_snapshot_and_invalid_archive_paths_are_refused(self):
        import plyvel_next as plyvel
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); pack = root / 'spells'
            with plyvel.DB(str(pack), create_if_missing=True) as db:
                db.put(('!items!' + IDS[0]).encode(), json.dumps(spell()).encode())
            before = fingerprint(pack)
            with spell_source(pack) as source:
                self.assertIn('Compendium.dnd5e.spells.' + IDS[0], source['index'])
                self.assertIsNone(source['root'])
            self.assertEqual(fingerprint(pack), before)
            archive = root / 'unsafe.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('../system.json', '{}')
                z.writestr('system.json', '{"id":"dnd5e"}')
            with self.assertRaises(ValueError):
                with spell_source(archive): pass

    def test_optional_source_boundary_and_bare_pack_media_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); pack = root / 'spells.json'
            s = spell(); s['img'] = 'neighbor.png'; Image.new('RGB', (8, 8)).save(root / 'neighbor.png')
            pack.write_text(json.dumps([s]))
            ir = campaign([document('Item', spell('local', '@UUID[Compendium.dnd5e.spells.' + IDS[0] + ']{Spell}'))])
            with spell_source(pack) as source:
                files, report = campaign_files(resolve_spells(ir, source), root, notes_folder='Spells', spell_root=source['root'])
            self.assertFalse(any(p.endswith('.rwfile') for p in files))
            self.assertTrue(any('media root unavailable' in l['summary'] for l in report['losses']))
            with self.assertRaisesRegex(ValueError, 'outside the optional spell source'):
                convert(Path(__file__).parents[1] / 'fixtures/synthetic-module', root / 'out', dnd5e_system=root)
            self.assertFalse((root / 'out').exists())

    def test_exact_uuid_closure_aliases_actor_links_and_captured_spell_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); pack = root / 'spells.json'
            docs = [spell(IDS[0], '@UUID[Compendium.dnd5e.spells.Item.' + IDS[1] + ']{Next}'),
                    spell(IDS[1], '@UUID[Compendium.dnd5e.spells.' + IDS[0] + ']{Back}'),
                    spell(IDS[2]), spell('unused')]
            pack.write_text(json.dumps(docs))
            a = actor(); a['items'][0]['system']['description']['value'] = 'Cast ' + ' '.join(
                '@UUID[Compendium.dnd5e.spells.' + ident + ']{Spell}' for ident in IDS)
            ir = campaign([document('Actor', a)])
            before = fingerprint(pack)
            with spell_source(pack) as source:
                enriched = resolve_spells(ir, source)
                files, report = campaign_files(enriched, root, notes_folder='Spells', spell_root=source['root'])
            self.assertEqual(len(ir['documents']), 1)  # no mutation
            self.assertEqual(report['counts']['spells'], 3)
            self.assertEqual(report['spell_source']['imported_spells'], 3)
            self.assertFalse(report['spell_source']['unresolved_uuids'])
            self.assertEqual(fingerprint(pack), before)
            actor_note = node(files[report['links']['Actor.actor'][:-7] + '.rwnote'])
            links = {c.members['_link'] for c in find(actor_note, 'ArkenTextCharacter') if c.members['_link']}
            self.assertEqual(links, {report['links']['Compendium.dnd5e.spells.' + ident] for ident in IDS})
            fixture = node((Path(__file__).parents[1] / 'fixtures/arkenforge-5e-templates/5e-Spell.rwnote').read_bytes())
            reference = find(fixture, 'ArkenNoteField5eSpellBlock')[0]
            for row in report['documents'][1:]:
                emitted = find(node(files[row['target'][:-7] + '.rwnote']), 'ArkenNoteField5eSpellBlock')[0]
                def shape(schema):
                    return {k: ([{a: b for a, b in info.items() if a != 'library_id'} if isinstance(info, dict) else info
                                 for info in v] if k == 'infos' else v)
                            for k, v in schema.items() if k != 'library_id'}
                self.assertEqual(shape(emitted.schema), shape(reference.schema))
                self.assertEqual(set(emitted.members), set(reference.members))
                self.assertEqual(content(emitted.members['_nameText']), row['name'])
                self.assertEqual(emitted.members['_nameText'].members['_font'], reference.members['_nameText'].members['_font'])
            # External IDs cannot steal unqualified world Item aliases.
            self.assertNotIn('Item.' + IDS[0], report['links'])

    def test_missing_input_and_missing_exact_id_remain_graded_losses(self):
        ir = campaign([document('Item', {'_id': 'scroll', 'type': 'loot', 'system': {
            'description': {'value': '@UUID[Compendium.dnd5e.spells.' + IDS[0] + ']{Scroll}'}}})])
        result = resolve_spells(ir, None)
        self.assertEqual(result['spell_source']['imported_spells'], 0)
        self.assertEqual(result['losses'][0]['feature'], 'external-spell')
        self.assertEqual(result['losses'][0]['grade'], 'manual')
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'spells.db'; p.write_text(json.dumps(spell('different-id')) + '\n')
            with spell_source(p) as source:
                self.assertEqual(resolve_spells(ir, source)['spell_source']['unresolved_uuids'],
                                 result['spell_source']['unresolved_uuids'])

    def test_system_zip_namespace_portrait_and_invalid_or_duplicate_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); system = root / 'dnd5e'; system.mkdir(); (system / 'packs').mkdir()
            manifest = {'id': 'dnd5e', 'title': 'Synthetic dnd5e', 'version': 'test',
                        'packs': [{'name': 'spells', 'path': 'packs/spells.json', 'type': 'Item', 'system': 'dnd5e'}]}
            (system / 'system.json').write_text(json.dumps(manifest))
            s = spell(); s['img'] = 'systems/dnd5e/icon.png'; Image.new('RGB', (8, 8), 'red').save(system / 'icon.png')
            (system / 'packs/spells.json').write_text(json.dumps([s]))
            archive = root / 'system.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                for p in system.rglob('*'):
                    if p.is_file(): z.write(p, 'dnd5e/' + p.relative_to(system).as_posix())
            ir = campaign([document('Item', spell('local', '@UUID[Compendium.dnd5e.spells.' + IDS[0] + ']{External}'))])
            with spell_source(archive) as source:
                files, report = campaign_files(resolve_spells(ir, source), root, notes_folder='Spells', spell_root=source['root'])
                self.assertEqual(report['spell_source']['provenance']['version'], 'test')
                self.assertTrue(any(p.endswith('.rwfile') for p in files))
            (system / 'packs/spells.json').write_text(json.dumps([s, s]))
            with self.assertRaisesRegex(ValueError, 'Ambiguous'):
                with spell_source(system): pass
            manifest['id'] = 'other'; (system / 'system.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'dnd5e system'):
                with spell_source(system): pass

    def test_public_convert_and_changed_optional_input_never_publishes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'source'
            shutil.copytree(Path(__file__).parents[1] / 'fixtures/synthetic-module', source)
            (source / 'packs/items.db').write_text(json.dumps({'_id': 'scroll', 'type': 'loot', 'system': {
                'description': {'value': '@UUID[Compendium.dnd5e.spells.' + IDS[0] + ']{Spell}'}}}))
            pack = root / 'spells.json'; pack.write_text(json.dumps([spell()]))
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(['convert', str(source), '--out', str(root / 'out'),
                                       '--dnd5e-system', str(pack), '--pdf', 'references']), 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report['native_counts']['spells'], 1)
            self.assertEqual(report['campaign_content'][0]['spell_source']['imported_spells'], 1)
            self.assertEqual(report['spell_source']['input_sha256'], fingerprint(pack))
            original = campaign_files
            def change(*args, **kwargs):
                result = original(*args, **kwargs)
                pack.write_text(pack.read_text() + ' ')
                return result
            with patch('forgebridge.native_campaign.campaign_files', side_effect=change):
                with self.assertRaisesRegex(ValueError, 'spell input changed'):
                    convert(source, root / 'changed', dnd5e_system=pack, pdf='references')
            self.assertFalse((root / 'changed').exists())

"""Owned FG shapes modelling real-module layouts; no third-party module content."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from forgebridge.convert import convert, discover
from forgebridge.fg_campaign import build_campaign, campaign_ir, _formatted
from forgebridge.fantasy_grounds import ModuleSource, parse_xml, ModuleError
from forgebridge.native_dependencies import read_package, check_metadata_references
from forgebridge.installer import native_outputs, install_conversion, uninstall
from forgebridge.gui import report_text
from test_campaign import node, find, content
from test_gui import run_headless_gui, click, finish_job

FIXTURE=Path(__file__).resolve().parents[1]/'fixtures/synthetic-fg-adventure'

class FGRealAdventureTests(unittest.TestCase):
    def copy(self,root):
        path=Path(root)/'module';shutil.copytree(FIXTURE,path);return path

    def test_category_reference_blocks_module_links_and_derived_strings(self):
        files,report=build_campaign(FIXTURE)
        links=report['links'];self.assertEqual(links['npc.id-watcher'],links['npc.id-watcher@FB FG Owned Adventure'])
        self.assertIn('image.map',links)
        self.assertEqual(discover(FIXTURE)['scenes'][0]['id'],'image.map')
        note=node(files[links['npc.id-watcher'][:-7]+'.rwnote'])
        block=find(note,'ArkenNoteFieldStatBlock5e')[0].members
        self.assertEqual(content(block['_armorClassText']),'Armor Class 16 (natural armor)')
        self.assertEqual(block['_trackedHitPoints'].members['_maxValue'],22)
        self.assertIn('4d8 + 4',content(block['_hitPointsText']))
        self.assertIn('Con +3, Wis +4',content(block['_savingThrowsText']))
        self.assertIn('poison',content(block['_damageImmunitiesText']))
        self.assertEqual(block['_legendaryActions'].members['_size'],1)
        self.assertEqual(block['_actions'].members['_size'],2)
        room=node(files[links['encounter.room'][:-7]+'.rwnote']);body=find(room,'ArkenNoteFieldText')[0].members['_text']
        self.assertIn('First paragraph.\nSecond paragraph.',content(body))
        self.assertIn('• One',content(body));self.assertIn('Read aloud.',content(body))
        self.assertTrue(any(c.members['_link']==links['npc.id-watcher'] for c in body.members['_characters'].members['_items'].items))

    def test_reference_groups_repeated_categories_and_legacy_stats_are_not_5e(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.copy(tmp)
            (p/'definition.xml').write_bytes(b'<root><name>Legacy</name><ruleset>3.5E</ruleset></root>')
            (p/'db.xml').write_bytes(b'<root><npc><category><a><name>Old Guard</name><strength>17</strength><ac>18, Touch 10</ac><atk>Spear +4 Melee</atk><cr>2</cr></a></category><category><b><name>Second Guard</name></b></category></npc><reference><npcdata><third><name>Third Guard</name></third></npcdata><magicitemdata><key><name>Old Key</name><description>Key text.</description></key></magicitemdata><refmanualdata><page><name>Page</name><blocks><id><blocktype>singletext</blocktype><text type="formattedtext"><p>Block text.</p></text></id></blocks></page></refmanualdata></reference></root>')
            files,r=build_campaign(p)
        self.assertEqual(r['counts']['actors'],3);self.assertEqual(r['counts']['items'],1);self.assertEqual(r['counts']['stories'],1)
        block=find(node(files[r['links']['npc.a'][:-7]+'.rwnote']),'ArkenNoteFieldStatBlock5e')[0].members
        self.assertIn('18, Touch 10',content(block['_armorClassText']))
        self.assertEqual(content(block['_proficiencyBonusText']),'')
        self.assertTrue(any('Spear +4 Melee' in content(v) for v in block['_actions'].members['_items'].items))
        self.assertTrue(any('Non-5e' in json.dumps(l) for l in r['losses']))

    def test_combined_map_notes_markers_tokens_and_fake_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=self.copy(root)
            report=convert(p,root/'out',map_folder='Check',notes_folder='Check')
            self.assertEqual(report['status'],'PASS');self.assertEqual(report['native_counts']['markers'],1)
            self.assertEqual(report['native_counts']['tokens'],2)
            row=report['scenes'][0];placement=row['native_report']['placements']
            self.assertEqual(placement['markers'][0]['grid_position'],{'x':2.,'y':1.5})
            self.assertEqual(placement['markers'][0]['native_position'],{'x':5.12,'y':-3.84})
            self.assertEqual(len(set(t['source_id'] for t in placement['tokens'])),2)
            self.assertEqual(placement['tokens'][0]['footprint'],[2.,2.])
            self.assertTrue(placement['tokens'][0]['hidden_flag']);self.assertEqual(placement['tokens'][0]['rotation_clockwise'],90.)
            self.assertEqual(placement['bindings'][0]['npc_note'],report['campaign_content'][0]['links']['npc.id-watcher'])
            self.assertTrue(any(x['feature']=='token-npc-link' for x in placement['losses']))
            files=read_package(native_outputs(report,root/'out')[0]);self.assertGreater(check_metadata_references(files),0)
            self.assertTrue(any('Map' in x and x.endswith('.rwmap') for x in files))
            assets=root/'MyAssets';assets.mkdir();(assets/'user.txt').write_bytes(b'keep')
            with patch('forgebridge.installer.require_toolkit_closed'):
                result=install_conversion(report,root/'out',assets,root/'backups')
                removed=uninstall(result['receipt'],keep_changed=True)
            self.assertEqual(removed['removed'],result['added']);self.assertEqual((assets/'user.txt').read_bytes(),b'keep')
            self.assertIn('Pins: 1; tokens: 2',report_text(report))

    def test_missing_external_assets_links_and_duplicate_placement_identity_are_losses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=self.copy(root);db=p/'db.xml'
            s=db.read_text(encoding='utf-8').replace('tokens/watcher.png@FB FG Owned Adventure','tokens/watcher.png@Other Module').replace('<id>second</id>','<id>watcher</id>')
            s=s.replace('<recordname>encounter.room</recordname>','<recordname>encounter.room@Other Module</recordname>')
            db.write_bytes(s.encode())
            r=convert(p,root/'out');loss=r['scenes'][0]['native_report']['placements']['losses']
            self.assertEqual(r['native_counts']['tokens'],0);self.assertEqual(r['native_counts']['markers'],0)
            self.assertTrue(any('another module' in x['summary'] for x in loss));self.assertTrue(any('Duplicate token' in x['summary'] for x in loss))

    def test_notes_only_no_grid_and_gui_empty_selection_build_campaign(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=self.copy(root);db=p/'db.xml';db.write_bytes(db.read_bytes().replace(b'<gridsize>100,100</gridsize>',b'').replace(b'<grid>on</grid>',b''))
            discovered=discover(p);self.assertEqual(discovered['scenes'],[])
            r=convert(p,root/'out');self.assertEqual(r['scenes'],[]);self.assertGreater(r['native_counts']['notes'],0)
            self.assertFalse(any(n.endswith('.rwmap') for n in read_package(native_outputs(r,root/'out')[0])))
            def scenario(ui):
                click(ui,'Discover scenes');finish_job(ui);click(ui,'Build / export')
            with patch('forgebridge.gui.discover',return_value=discovered),patch('forgebridge.gui.convert',return_value=r) as build:
                run_headless_gui(scenario);self.assertTrue(build.call_args.kwargs['notes_only'])

    def test_external_module_link_is_not_rebound_to_local_record(self):
        value=_formatted(parse_xml(b'<text type="formattedtext"><p><link class="npc" recordname="npc.a@Other">Elsewhere</link></p></text>','test'))
        self.assertEqual(value,'@UUID[npc.a@Other]{Elsewhere}')

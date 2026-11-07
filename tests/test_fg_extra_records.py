"""Additional owned FG content: range tables, manuals, rewards and unknown types."""
from pathlib import Path
import tempfile
import shutil
import unittest
from forgebridge.fg_campaign import build_campaign
from forgebridge.convert import convert
from forgebridge.installer import native_outputs
from forgebridge.native_dependencies import check_metadata_references,read_package
from test_campaign import node,find,content
from test_fg_real_adventure import FIXTURE

class FGExtraRecordTests(unittest.TestCase):
    def test_table_rows_and_result_links_use_native_rollable_table(self):
        files,r=build_campaign(FIXTURE);target=r['links']['tables.t-one']
        table=find(node(files[target[:-7]+'.rwnote']),'ArkenNoteFieldRollableTable')[0]
        rows=table.members['_rows'].members
        self.assertEqual(rows['_size'],2)
        first=rows['_items'].items[0].members
        self.assertEqual((first['_from'],first['_to']),(1,1))
        chars=first['_data'].members['_characters'].members['_items'].items
        self.assertTrue(any(c.members['_link']==r['links']['npc.id-watcher'] for c in chars))
        self.assertEqual(r['links']['tables.t-one@*'],r['links']['tables.t-one'])
        self.assertEqual(r['counts']['tables'],1)
        self.assertTrue(any(l['feature']=='table-settings' for l in r['losses']))

    def test_chapters_pages_parcels_quests_and_all_links_are_closed(self):
        files,r=build_campaign(FIXTURE)
        self.assertEqual(r['counts']['reference_pages'],1);self.assertEqual(r['counts']['reference_chapters'],3)
        self.assertEqual(r['counts']['parcels'],1);self.assertEqual(r['counts']['quests'],1)
        expected={
          'reference.refmanualindex':'reference.refmanualindex.chapters.c1',
          'reference.refmanualindex.chapters.c1':'reference.refmanualindex.chapters.c1.subchapters.s1',
          'reference.refmanualindex.chapters.c1.subchapters.s1':'reference.refmanualdata.page-a',
          'reference.refmanualdata.page-a':'tables.t-one',
          'treasureparcel.p1':'item.id-item','quest.q1':'item.id-item'}
        for source,dest in expected.items():
            # Character class names differ between schemas; examine text fields instead.
            texts=find(node(files[r['links'][source][:-7]+'.rwnote']),'ArkenTextString')
            self.assertTrue(any(c.members['_link']==r['links'][dest] for t in texts for c in t.members['_characters'].members['_items'].items),source)
        unknown=[l for l in r['losses'] if l['feature']=='unknown-record-type']
        self.assertEqual({l['source_id'] for l in unknown},{'reference.widgets.w1','unknown-owned.u1'})
        self.assertTrue(all(l['grade']=='unsupported' for l in unknown));self.assertGreater(check_metadata_references(files),0)

    def test_bad_ranges_preserve_text_and_percentile_settings_are_not_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'module';shutil.copytree(FIXTURE,source)
            p=source/'db.xml';s=p.read_text(encoding='utf-8').replace('</reference>','<futureindex><x><name>Unknown future record</name></x></futureindex></reference>').replace('<dice>d2</dice>','<dice>d10,d100</dice>').replace('<fromrange>2</fromrange>','<fromrange>1</fromrange>')
            p.write_bytes(s.encode());files,r=build_campaign(source)
        data=node(files[r['links']['tables.t-one'][:-7]+'.rwnote'])
        self.assertTrue(any(l.get('feature')=='unknown-record-type' and l.get('record_type')=='futureindex' for l in r['losses']))
        self.assertFalse(find(data,'ArkenNoteFieldRollableTable'))
        texts=find(data,'ArkenTextString');self.assertTrue(any('The watcher' in content(t) for t in texts))
        self.assertTrue(any('FG dice: d10,d100' in content(t) for t in texts))
        self.assertTrue(any(l['feature']=='roll-table' and l['grade']=='manual' for l in r['losses']))

    def test_combined_output_counts_and_pin_can_target_new_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'module';shutil.copytree(FIXTURE,source)
            p=source/'db.xml';p.write_bytes(p.read_bytes().replace(b'<recordname>encounter.room</recordname>',b'<recordname>tables.t-one</recordname>'))
            r=convert(source,root/'out');self.assertEqual(r['status'],'PASS')
            self.assertEqual(r['native_counts']['tables'],1);self.assertEqual(r['native_counts']['quests'],1)
            pin=r['scenes'][0]['native_report']['placements']['markers'][0]
            self.assertEqual(pin['target'],r['campaign_content'][0]['links']['tables.t-one'])
            files=read_package(native_outputs(r,root/'out')[0]);self.assertGreater(check_metadata_references(files),0)

    def test_quest_attachment_does_not_replace_quest_text_and_hp_has_one_parenthesis_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'module';shutil.copytree(FIXTURE,source)
            p=source/'db.xml';s=p.read_text(encoding='utf-8').replace('recordname="tables.t-one"','recordname="tables.t-one@*"').replace('recordname="item.id-item"','recordname="item.id-item@*"').replace('<quest><q1>', '<quest><q1><image type="image"><bitmap>images/map.png</bitmap></image>')
            s=s.replace('<hp type="string">22 (4d8 + 4)</hp>', '<hp>22</hp><hd>(4d8 + 4)</hd>')
            p.write_bytes(s.encode());files,r=build_campaign(source)
        self.assertFalse(any(l.get('feature')=='link' and l.get('uuid','').endswith('@*') for l in r['losses']))
        q=node(files[r['links']['quest.q1'][:-7]+'.rwnote'])
        self.assertTrue(find(q,'ArkenNoteFieldMedia'))
        self.assertTrue(any('xp: 50' in content(t) for t in find(q,'ArkenTextString')))
        npc=find(node(files[r['links']['npc.id-watcher'][:-7]+'.rwnote']),'ArkenNoteFieldStatBlock5e')[0].members
        self.assertEqual(content(npc['_hitPointsText']),'(4d8 + 4)')

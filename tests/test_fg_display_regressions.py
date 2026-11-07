"""Owned FG display/merge regressions. Written fields only, never Toolkit proof."""
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from forgebridge.convert import convert
from forgebridge.fg_campaign import build_campaign
from forgebridge.native import NoteBuilder
from forgebridge.native_export import TextCompiler
from forgebridge.native_dependencies import read_package, check_metadata_references
from test_campaign import node, find, content
from test_fg_campaign import module
from test_fg_real_adventure import FIXTURE


class FGDisplayRegressions(unittest.TestCase):
    def test_newline_escapes_are_real_breaks_in_written_fields(self):
        db = r"""<root><npc><a><name>Owned Priest</name><ac>15</ac><cr>4</cr>
        <specialattacks>Spells\r\rLevel 0 Spells\\rLevel 1 Spells\r\nEnd\nDone</specialattacks>
        <skills>Listen +2\rSpot +3</skills></a></npc>
        <item><i><name>Key</name><description>First\r\rSecond</description></i></item>
        <encounter><s><name>Story</name><text>First\\r\\rSecond\nThird</text></s></encounter>
        <reference><refmanualdata><p><name>Page</name><text>One\rTwo</text></p></refmanualdata></reference></root>"""
        with tempfile.TemporaryDirectory() as tmp:
            m = module(tmp, db)
            # Legacy special attacks are preserved without inventing 5e mechanics.
            import zipfile
            with zipfile.ZipFile(m) as z: members = {n:z.read(n) for n in z.namelist()}
            members['definition.xml'] = b'<root><name>Owned legacy control</name><ruleset>3.5E</ruleset></root>'
            with zipfile.ZipFile(m, 'w') as z:
                for n,b in members.items(): z.writestr(n,b)
            files,r = build_campaign(m)
        texts = [content(t) for p,b in files.items() if p.endswith('.rwnote')
                 for t in find(node(b),'ArkenTextString')]
        self.assertTrue(any('Spells\n\nLevel 0 Spells\nLevel 1 Spells\nEnd\nDone' in t for t in texts))
        for value in texts:
            self.assertNotIn('\r',value)
            self.assertIsNone(re.search(r'\\+[rn]',value),repr(value))
        self.assertTrue(any('First\n\nSecond' in t for t in texts))

    def test_story_and_reference_use_shared_readable_journal_style(self):
        with tempfile.TemporaryDirectory() as tmp:
            files,r = build_campaign(module(tmp, '<root><encounter><s><name>Story</name><text type="formattedtext"><p>First.</p><p>Second.</p></text></s></encounter><reference><refmanualdata><p><name>Page</name><text type="formattedtext"><p>First.</p><p>Second.</p></text></p></refmanualdata></reference></root>'))
        builder=NoteBuilder()
        expected=builder.text_field('Journal',TextCompiler(lambda _:None,[],{}).compile('<p>First.</p><p>Second.</p>'),1)
        self.assertEqual(content(expected.members['_text']),'First.\n\nSecond.')
        for row in r['documents']:
            field=find(node(files[row['target'][:-7]+'.rwnote']),'ArkenNoteFieldText')[0]
            self.assertEqual(content(field.members['_text']),content(expected.members['_text']))
            for key,value in expected.members['_fieldColor'].members.items():
                self.assertAlmostEqual(field.members['_fieldColor'].members[key],value,places=6)
            chars=field.members['_text'].members['_characters'].members['_items'].items
            self.assertTrue(chars)
            self.assertTrue(all(c.members['_hexColour']=='FFFFFF' and c.members['_size']==40 for c in chars))

    def test_legacy_missing_rows_request_collapsed_metrics_without_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'legacy';p.mkdir()
            (p/'definition.xml').write_bytes(b'<root><name>Owned</name><ruleset>3.5E</ruleset></root>')
            (p/'db.xml').write_bytes(b'<root><npc><p><name>Owned Blood Priest Layout</name><ac>15</ac><hp>36 (4d8+4)</hp><cr>4</cr></p></npc></root>')
            files,r=build_campaign(p)
        block=find(node(files[r['links']['npc.p'][:-7]+'.rwnote']),'ArkenNoteFieldStatBlock5e')[0].members
        for flag in ('_savingThrowsFieldActive','_damageResistanceFieldActive','_damageImmunitiesFieldActive','_conditionImmunitiesFieldActive','_damageVulnerabilitiesFieldActive'):
            self.assertFalse(block[flag])
        for key in ('_skillsText','_sensesText','_languagesText','_proficiencyBonusText'):
            self.assertEqual(content(block[key]),'\u200b')
            chars=block[key].members['_characters'].members['_items'].items
            self.assertEqual([c.members['_size'] for c in chars],[0])
        self.assertEqual(content(block['_challengeText']),'Challenge 4')
        self.assertTrue(any(l['feature']=='actor-empty-layout' for l in r['losses']))

    def test_combined_fg_placements_then_visibility_with_layer_pc(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'module';shutil.copytree(FIXTURE,p)
            xml=ET.parse(p/'db.xml');image=xml.find('./image/category/map/image')
            ET.SubElement(image,'los').text='on';ET.SubElement(image,'fogexploration').text='on'
            light=ET.SubElement(ET.SubElement(image,'lights'),'light')
            ET.SubElement(light,'position').text='0,0';ET.SubElement(light,'range').text='2,1'
            ET.SubElement(light,'flicker');ET.SubElement(light,'on')
            tokens=image.find('tokens');pc=tokens.findall('token')[1];tokens.remove(pc)
            pc.find('recordname').text='charsheet.owned'
            sight=ET.SubElement(pc,'sight')
            for k,v in [('enabled','true'),('range','3'),('units','squares')]: ET.SubElement(sight,k).text=v
            layer=ET.SubElement(ET.SubElement(image,'layers'),'layer');ET.SubElement(layer,'tokens').append(pc)
            xml.write(p/'db.xml')
            report=convert(p,Path(tmp)/'out')
            self.assertEqual(report['status'],'PASS')
            native=report['scenes'][0]['native_report'];v=native['visibility']
            self.assertEqual(len(native['placements']['tokens']),2)
            self.assertEqual(len(native['placements']['markers']),1)
            self.assertEqual(v['fog'],{'enabled':True,'mode':2,'persists':True,'historical_masks_migrated':False})
            self.assertEqual(v['lights'][0]['effect']['kind'],'flicker')
            self.assertEqual(len(v['tokens']),1)
            self.assertAlmostEqual(v['tokens'][0]['native_radius'],7.68,places=4)
            self.assertEqual(v['tokens'][0]['source_id'],'image.map.token.second')
            files=read_package(Path(tmp)/'out'/'native-package.zip')
            check_metadata_references(files)
            actual=node(files[native['output_names']['map_path']])
            self.assertEqual(actual.members['_fogMode'].members['value__'],2)

    def test_duplicate_pc_identity_cannot_grant_vision_to_first_npc(self):
        from forgebridge.visibility_ir import foundry_visibility
        scene={'_id':'s','width':100,'height':100,'padding':0,'grid':{'size':100,'type':1,'distance':5},'tokenVision':True,'tokens':[
            {'_id':'dup','actorId':'npc','sight':{'enabled':False}},
            {'_id':'dup','actorId':'pc','sight':{'enabled':True,'range':30}}]}
        ir=foundry_visibility(scene,[{'_id':'npc','type':'npc'},{'_id':'pc','type':'character','ownership':{'default':3}}])
        self.assertEqual(ir['tokens'],[])
        self.assertTrue(any('Duplicate token identity' in l['summary'] for l in ir['losses']))
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'module';shutil.copytree(FIXTURE,p)
            xml=ET.parse(p/'db.xml');tokens=xml.find('./image/category/map/image/tokens')
            duplicate=tokens.findall('token')[1];duplicate.find('id').text='watcher'
            duplicate.find('recordname').text='charsheet.owned'
            sight=ET.SubElement(duplicate,'sight')
            for k,v in [('enabled','true'),('range','3'),('units','squares')]: ET.SubElement(sight,k).text=v
            xml.write(p/'db.xml')
            report=convert(p,Path(tmp)/'out')
        native=report['scenes'][0]['native_report']
        self.assertEqual(len(native['placements']['tokens']),1)
        self.assertEqual(native['visibility']['tokens'],[])
        self.assertTrue(any('Duplicate token identity' in l['summary'] for l in native['visibility']['losses']))

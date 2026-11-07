"""Owned, decoded-native regressions for B3--B6. No Toolkit acceptance."""
import json,shutil,tempfile,unittest
from pathlib import Path
from PIL import Image
from forgebridge.spell_source import spell_source,resolve_spells
from forgebridge.native_campaign import campaign_files
from forgebridge.scene_profile import fingerprint
from forgebridge.native_dependencies import read_package,check_metadata_references
from forgebridge.native_audio import playlist_files
from forgebridge.convert import convert
from test_campaign import actor,campaign,document,node,find,content
from test_fantasy_grounds import module,DEFINITION,png

ROOT=Path(__file__).resolve().parents[1]

class ScopeB3B6Tests(unittest.TestCase):
    def system(self,root):
        p=root/'system';(p/'packs').mkdir(parents=True)
        Image.new('RGB',(6,8),'red').save(p/'portrait.png')
        a=actor();a['_id']='same';a['img']='systems/dnd5e/portrait.png'
        a['items'][0]['system']['description']['value']='Uses @UUID[Compendium.dnd5e.items.Item.same]{Blade}'
        w={'_id':'same','name':'System Blade','type':'weapon','system':{'description':{'value':'Held by @UUID[Compendium.dnd5e.monsters.Actor.same]{Monster}'}}}
        for name,rows in [('monsters',[a,{**a,'_id':'unused'}]),('items',[w,{**w,'_id':'unused'}])]:
            (p/'packs'/ (name+'.json')).write_text(json.dumps(rows))
        (p/'system.json').write_text(json.dumps({'id':'dnd5e','version':'owned','packs':[{'name':n,'path':'packs/'+n+'.json','type':k,'system':'dnd5e'} for n,k in [('monsters','Actor'),('items','Item')]]}))
        return p

    def test_referenced_monster_item_closure_cycles_portraits_and_namespace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);system=self.system(root);before=fingerprint(system)
            local={'_id':'local','name':'Scroll','type':'loot','system':{'description':{'value':'@UUID[Compendium.dnd5e.monsters.Actor.same]{Monster}'}}}
            ir=campaign([document('Item',local)])
            with spell_source(system) as source:
                direct=resolve_spells({**campaign([]),'reference_payloads':[{'documentUuid':'Compendium.dnd5e.items.Item.same'}]},source)
                self.assertEqual(direct['compendium_source']['imported_documents'],2)
                enriched=resolve_spells(ir,source)
                files,r=campaign_files(enriched,root,notes_folder='Check',spell_root=source['root'])
            self.assertEqual(fingerprint(system),before)
        self.assertEqual(r['compendium_source']['actors'],1);self.assertEqual(r['compendium_source']['items'],1)
        self.assertEqual(len(enriched['documents']),3);self.assertEqual(len(ir['documents']),1)
        self.assertFalse(any(d['source_id']=='unused' for d in r['documents']))
        self.assertEqual(r['spell_source']['imported_spells'],0)
        self.assertNotIn('Actor.same',r['links']);self.assertNotIn('Item.same',r['links'])
        a=r['links']['Compendium.dnd5e.monsters.Actor.same'];w=r['links']['Compendium.dnd5e.items.Item.same']
        self.assertNotEqual(a,w)
        monster=node(files[a[:-7]+'.rwnote'])
        self.assertEqual(len(find(monster,'ArkenNoteFieldStatBlock5e')),1)
        self.assertEqual(len(find(monster,'ArkenNoteFieldMedia')),1)
        self.assertEqual(len(find(node(files[w[:-7]+'.rwnote']),'ArkenNoteField5eItemBlock')),1)
        self.assertTrue(any(c.members['_link']==w for c in find(monster,'ArkenTextCharacter')))
        check_metadata_references(files)

    def test_journal_reference_resolves_through_public_convert_and_missing_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);system=self.system(root);src=root/'source';shutil.copytree(ROOT/'fixtures/synthetic-module',src)
            journal=json.loads((src/'packs/journal.db').read_text());journal['pages'][0]['text']['content']='@UUID[Compendium.dnd5e.items.Item.same]{Blade}'
            (src/'packs/journal.db').write_text(json.dumps(journal))
            r=convert(src,root/'out',dnd5e_system=system)
            self.assertEqual(r['status'],'PASS');self.assertEqual(r['campaign_content'][0]['compendium_source']['items'],1)
        ir=campaign([document('Item',{'_id':'a','type':'loot','system':{'description':{'value':'@UUID[Compendium.dnd5e.monsters.Actor.missing]{Missing}'}}})])
        result=resolve_spells(ir,None)
        self.assertEqual(result['losses'][0]['feature'],'external-compendium')
        _,r=campaign_files(result,ROOT,notes_folder='Check')
        self.assertEqual(len([l for l in r['losses'] if l.get('uuid','').endswith('missing')]),1)

    def test_playlist_gain_zero_multiplication_and_individual_manual_settings(self):
        fixture=ROOT/'fixtures/arkenforge-user-playlist/toolkit-made-music-playlist/sources/FBMusicControl-MP3.mp3'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copyfile(fixture,root/'tone.mp3')
            source={'_id':'p','name':'Owned','volume':.5,'mode':2,'fade':100,'channel':'music','sounds':[{'_id':'s','name':'Tone','path':'tone.mp3','volume':.4,'repeat':True,'fade':25,'channel':'music'}]}
            files,r=playlist_files(source,root,'scope')
            track=find(node(files[r['playlist']]),'MusicTrackInfo')[0]
            pair=track.members['_trackVolumes'].members['KeyValuePairs'].items[0]
            self.assertAlmostEqual(pair.members['value'],.2,places=6)
            from forgebridge.nrbf import Reader
            reader=Reader(files[r['songs'][0]['native_file']]);reader.read()
            audio=next(o for o in reader.objects.values() if isinstance(o,dict) and o.get('class')=='AudioTrack')
            self.assertEqual(bytes(reader.objects[audio['members']['_clipRAW']['ref']]['bytes']),fixture.read_bytes())
            self.assertEqual(r['settings']['mode']['source'],{'mode':2})
            for field in ('loop','fade','channel','mode'):
                self.assertTrue(any(l['feature']=='playlist-'+field and l['grade']=='manual' for l in r['losses']))
            source['sounds'][0]['volume']=0
            files,r=playlist_files(source,root,'scope')
            self.assertEqual(r['songs'][0]['native_master_volume'],0)
            source['sounds'][0]['volume']=3
            _,r=playlist_files(source,root,'scope')
            self.assertTrue(any(l['feature']=='playlist-volume' and l['grade']=='manual' for l in r['losses']))

    def table(self,payload):
        return campaign_files(campaign([document('RollTable',payload)]),ROOT,notes_folder='Tables')

    def test_weighted_native_ranges_keep_links_and_report_source_state(self):
        a={'_id':'a','name':'Weighted','formula':'1d4','replacement':False,'results':[{'range':[1,1],'weight':1,'name':'One','drawn':True},{'range':[2,4],'weight':3,'name':'Three','documentUuid':'RollTable.b'}]}
        b={'_id':'b','name':'Other','formula':'1d1','results':[{'range':[1,1],'name':'Result'}]}
        files,r=campaign_files(campaign([document('RollTable',a),document('RollTable',b)]),ROOT,notes_folder='Tables')
        self.assertEqual(len(r['table_conversion']),2)
        table=find(node(files[r['links']['RollTable.a'][:-7]+'.rwnote']),'ArkenNoteFieldRollableTable')[0]
        rows=table.members['_rows'].members['_items'].items
        self.assertEqual([(x.members['_from'],x.members['_to']) for x in rows],[(1,1),(2,4)])
        self.assertTrue(any(c.members['_link']==r['links']['RollTable.b'] for c in find(table,'ArkenTextCharacter')))
        for key in ('replacement','drawn','chained'):self.assertTrue(any(l['feature']=='roll-table-'+key and l['grade']=='manual' for l in r['losses']))

    def test_simple_dice_probability_tickets_and_unsupported_reference(self):
        source={'_id':'dice','name':'2d6','formula':'2d6+1','results':[{'range':[3,3],'name':'Low'},{'range':[4,8],'name':'Middle'},{'range':[9,13],'name':'High'}]}
        files,r=self.table(source)
        n=node(files[r['links']['RollTable.dice'][:-7]+'.rwnote']);rows=find(n,'ArkenNoteFieldRollableTable')[0].members['_rows'].members['_items'].items
        self.assertEqual([(x.members['_from'],x.members['_to']) for x in rows],[(1,1),(2,21),(22,36)])
        self.assertTrue(any(l.get('source_formula')=='2d6+1' and l['grade']=='approximate' for l in r['losses']))
        for formula in ('2d6kh1','99d100','1d6 + __import__("os")'):
            files,r=self.table({**source,'formula':formula})
            self.assertEqual(r['counts']['tables'],0);self.assertTrue(any(l['feature']=='roll-table' and l['grade']=='manual' for l in r['losses']))

    def test_zero_weight_and_inconsistent_weights_are_never_silent(self):
        source={'_id':'w','formula':'1d2','results':[{'range':[0,0],'weight':0,'name':'Never'},{'range':[1,2],'weight':2,'name':'Twice'}]}
        files,r=self.table(source);self.assertEqual(r['counts']['tables'],1)
        self.assertTrue(any('zero probability' in str(l) for l in r['losses']))
        written=node(files[r['links']['RollTable.w'][:-7]+'.rwnote'])
        self.assertTrue(any('Never' in content(f.members['_text']) for f in find(written,'ArkenNoteFieldText')))
        files,r=self.table({**source,'formula':'2d6'})
        self.assertEqual(r['counts']['tables'],0)

    def test_fg_native_light_rgb_gain_radius_layers_and_manual_falloff(self):
        db=b'<root><image><m><name>Layers</name><image type="image"><gridsize>100,100</gridsize><layers><layer><id>base</id><bitmap>images/m.png</bitmap></layer><layer><id>overlay</id><bitmap>images/o.png</bitmap><position>100,-50</position><scale>2,3</scale><rotation>90</rotation><invisible/></layer><layer><id>opaque</id><bitmap>images/o.png</bitmap><transform>1,2,3,4</transform></layer></layers><lights><light><position>0,0</position><range>1,.75,3,.5</range><color>FF804020</color><intensity>1.5</intensity><on/></light></lights></image></m></image></root>'
        with tempfile.TemporaryDirectory() as tmp:
            p=module(tmp,{'definition.xml':DEFINITION,'db.xml':db,'images/m.png':png(400,300),'images/o.png':png(20,10)})
            r=convert(p,Path(tmp)/'out');self.assertEqual(r['status'],'PASS')
            native=r['scenes'][0]['native_report'];files=read_package(Path(tmp)/'out/native-package.zip')
            n=node(files[native['output_names']['map_path']]);presets=find(n,'ArkenTilePresetBase')
            light=next(p for p in presets if p.members['_tileName']=='Light Source').members['_lighting'].members
            self.assertAlmostEqual(light['_lightR'],128/255,places=6);self.assertAlmostEqual(light['_lightG'],64/255,places=6);self.assertAlmostEqual(light['_lightB'],32/255,places=6)
            self.assertAlmostEqual(light['_lightIntensity'],1.5,places=6)
            self.assertAlmostEqual(light['_lightRadius'].members['_items'].items[0],7.68,places=5)
            overlay=next(p for p in presets if p.members.get('_name')=='FG bitmap layer' and p.members['_hidden'])
            self.assertAlmostEqual(overlay.members['_position'].members['x'],7.68,places=5)
            self.assertAlmostEqual(overlay.members['_position'].members['y'],-5.12,places=5)
            self.assertEqual(overlay.members['_rotation'],90)
            self.assertEqual(len(native['bitmap_layers']['layers']),2)
            losses=native['fantasy_grounds']['losses']
            self.assertTrue(any(l.get('feature')=='fg-light-falloff' and l['grade']=='manual' for l in losses))
            self.assertTrue(any('Opaque persisted transform' in str(l) for l in losses))
            check_metadata_references(files)

    def test_large_uniform_formula_and_gaps_are_bounded_and_explicit(self):
        files,r=self.table({'_id':'large','formula':'1d1000000','results':[{'range':[1,1000000],'name':'Any'}]})
        self.assertEqual(r['table_conversion'][0]['tickets'],1000000)
        table=find(node(files[r['links']['RollTable.large'][:-7]+'.rwnote']),'ArkenNoteFieldRollableTable')[0]
        self.assertEqual(table.members['_rows'].members['_items'].items[0].members['_to'],1000000)
        files,r=self.table({'_id':'gap','formula':'2d6','results':[{'range':[2,3],'name':'Only low'}]})
        self.assertEqual(r['counts']['tables'],0)
        self.assertEqual(r['table_conversion'][0]['status'],'reference')

    def test_fg_invalid_gain_alpha_and_off_state_have_explicit_losses(self):
        db=b'<root><image><m><name>Lights</name><image type="image"><bitmap>images/m.png</bitmap><gridsize>100,100</gridsize><lights><light><position>0,0</position><range>2,1</range><color>bad</color><intensity>nan</intensity></light><light><position>50,0</position><range>1,1</range><color>8000FF00</color><intensity>.5</intensity><on/></light></lights></image></m></image></root>'
        with tempfile.TemporaryDirectory() as tmp:
            p=module(tmp,{'definition.xml':DEFINITION,'db.xml':db,'images/m.png':png(400,300)})
            r=convert(p,Path(tmp)/'out')
            self.assertEqual(r['status'],'PASS')
            v=r['scenes'][0]['native_report']['visibility']
            self.assertFalse(v['lights'][0]['enabled']);self.assertEqual(v['lights'][0]['intensity'],1)
            self.assertEqual(v['lights'][1]['rgb'],[0,1,0]);self.assertEqual(v['lights'][1]['intensity'],.5)
            for feature in ('fg-light-intensity','fg-light-alpha'):
                self.assertTrue(any(l['feature']==feature and l['grade']=='manual' for l in v['losses']))

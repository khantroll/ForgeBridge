import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import hashlib

from PIL import Image
from forgebridge.campaign import read_campaign, display_document
from forgebridge.native_campaign import CampaignBuilder, campaign_files, link_token_actors
from forgebridge.native_audio import playlist_files
from forgebridge.native_tiles import add_tiles
from forgebridge.native import Node, Writer
from forgebridge.native_map import clone
from forgebridge.native_dependencies import check_metadata_references
from forgebridge.nrbf import Reader
from forgebridge.scene_records import blank_map, canonical_graph, record, encode
from forgebridge.convert import convert
from forgebridge.native_dependencies import write_archive
from forgebridge.installer import install, uninstall


def node(data):
    r=Reader(data);g=r.read();return clone(r,g['root_id'])


def find(root, name):
    seen=set();found=[]
    def walk(v):
        if id(v) in seen:return
        seen.add(id(v))
        if isinstance(v,Node):
            if v.schema['name']==name:found.append(v)
            for x in v.members.values():walk(x)
        elif hasattr(v,'items'):
            for x in v.items:walk(x)
    walk(root);return found


def content(v):return ''.join(c.members['_character'] for c in v.members['_characters'].members['_items'].items)


def document(kind,payload,adventure='A'):
    return display_document({'kind':kind,'id':payload['_id'],'source_path':'packs/adventure.json','adventure_id':adventure,'payload':payload},'dnd5e')


def campaign(docs):return {'scope':'a'*20,'package_id':'synthetic','losses':[],'documents':docs}


def actor():
    return {'_id':'actor','name':'Guard','type':'npc','system':{
        'abilities':{k:{'value':value,'proficient':1 if k=='str' else 0} for k,value in zip(('str','dex','con','int','wis','cha'),(16,12,14,8,10,10))},
        'attributes':{'ac':{'flat':16},'hp':{'value':12,'max':22,'formula':'4d8 + 4'},'movement':{'walk':30,'units':'ft'},'senses':{'darkvision':60,'units':'ft'}},
        'details':{'cr':1,'alignment':'neutral','type':{'value':'humanoid'}},
        'traits':{'size':'med','di':{'value':['poison']},'dr':{'value':['cold']},'dv':{'value':['fire']},'ci':{'value':['charmed']},'languages':{'value':['common']}},
        'skills':{'ath':{'value':1,'ability':'str'}}},
        'items':[{'name':'Spear','type':'weapon','system':{'activation':{'type':'action'},'description':{'value':'<p><i>Melee Weapon Attack:</i> +5 to hit. <i>Hit:</i> 6 [[/r 1d6+3]].</p>'}}},
                 {'name':'Parry','type':'feat','system':{'activation':{'type':'reaction'},'description':{'value':'Blocks.'}}},
                 {'name':'Stride','type':'feat','system':{'activation':{'type':'legendary'},'description':{'value':'Moves.'}}}]}


class CampaignTests(unittest.TestCase):
    def test_token_actor_link_preserves_icon_size_and_original_note(self):
        from forgebridge.scene_records import control_files
        with tempfile.TemporaryDirectory() as tmp:
            generated,c=campaign_files(campaign([document('Actor',actor())]),tmp,notes_folder='Campaign')
            _,controls,_=control_files()
            original=controls['MyAssets/Encyclopedia/Notes/GeneratedControls/Control.rwnote']
            ident='Scene.s.Token.t';key=hashlib.sha256(('scope\0'+ident).encode()).hexdigest()[:24]
            path='MyAssets/Encyclopedia/Notes/ForgeBridgeTokens/'+key+'.rwnote'
            files={**controls,**generated,path:original}
            scene={'_id':'s','tokens':[{'_id':'t','actorId':'actor','hidden':True,'rotation':90}]}
            before=node(original)
            report=link_token_actors(files,scene,'scope',c)
            self.assertEqual(report['count'],0)
            after=node(files[path])
            self.assertEqual(find(before,'ArkenNoteFieldSize')[0].members['_squareSizeNew'],find(after,'ArkenNoteFieldSize')[0].members['_squareSizeNew'])
            self.assertEqual(after.members['_noteIcon'].members['_iconPath'],before.members['_noteIcon'].members['_iconPath'])
            self.assertEqual(files[path],original)
            self.assertFalse(find(after,'ArkenNoteFieldText'))
            self.assertTrue(any(l['feature']=='token-actor-link' and l['grade']=='manual' for l in report['losses']))
            self.assertEqual(controls['MyAssets/Encyclopedia/Notes/GeneratedControls/Control.rwnote'],original)
            self.assertGreater(check_metadata_references(files),0)

    def test_campaign_playlist_fake_install_uninstall_keeps_edited_stat_block(self):
        with tempfile.TemporaryDirectory() as tmp,patch('forgebridge.installer.require_toolkit_closed'):
            root=Path(tmp);target=root/'MyAssets';target.mkdir();(target/'user.txt').write_text('keep')
            files,c=campaign_files(campaign([document('Actor',actor()),document('Playlist',{'_id':'p','name':'Ambient','sounds':[]})]),root,notes_folder='Campaign')
            package=root/'package.zip';write_archive(package,files)
            installed=install([package],target,root/'backups')
            self.assertEqual(installed['added'],4)
            edited=target/Path(c['links']['Actor.actor'].replace('MyAssets/','',1)).with_suffix('.rwnote')
            edited.write_bytes(edited.read_bytes()+b'edit')
            result=uninstall(installed['receipt'],keep_changed=True)
            self.assertEqual(result['removed'],3);self.assertEqual(len(result['kept_changed']),1)
            self.assertTrue(edited.exists());self.assertEqual((target/'user.txt').read_text(),'keep')

    def test_actor_fields_flags_hp_runs_and_empty_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            files,report=campaign_files(campaign([document('Actor',actor())]),tmp,notes_folder='Campaign')
            root=node(files[next(p for p in files if p.endswith('.rwnote'))]);block=find(root,'ArkenNoteFieldStatBlock5e')[0].members
            self.assertEqual(content(block['_strValNew']),'16 (+3)')
            self.assertEqual(content(block['_savingThrowsText']),'Saving Throws STR +5')
            self.assertEqual(content(block['_skillsText']),'Skills Athletics +5')
            self.assertEqual(content(block['_challengeText']),'Challenge 1 (200 XP)')
            self.assertEqual(content(block['_hitPointsText']),'(4d8 + 4)')
            self.assertEqual(block['_armorClassText'].members['_font'],'5eText')
            self.assertEqual(block['_armorClassText'].members['_characters'].members['_items'].items[0].members['_hexColour'],'58180D')
            self.assertEqual(block['_typeText'].members['_characters'].members['_items'].items[0].members['_defaultFont'],'5eText')
            hp=block['_trackedHitPoints'].members
            self.assertEqual((hp['_currentValueStr'],hp['_maxValueStr'],hp['_minValueStr']),('12','22','0'))
            for flag in ('_savingThrowsFieldActive','_damageResistanceFieldActive','_damageImmunitiesFieldActive','_damageVulnerabilitiesFieldActive','_conditionImmunitiesFieldActive'):self.assertTrue(block[flag])
            action=block['_actions'].members['_items'].items[0]
            chars=action.members['_characters'].members['_items'].items
            self.assertTrue(all(c.members['_fontSettings'].members['value__']==1 for c in chars[:6]))
            self.assertEqual(chars[7].members['_fontSettings'].members['value__'],2)
            self.assertNotIn('[[',content(action));self.assertNotIn('<',content(action))
            self.assertEqual(action.members['_font'],'5eText')
            self.assertEqual(block['_abilities'].members['_size'],0)
            self.assertEqual(block['_reactions'].members['_size'],1)
            self.assertEqual(block['_legendaryActions'].members['_size'],1)
            self.assertEqual(report['counts']['actors'],1)
            self.assertEqual(check_metadata_references(files),0)

    def test_optional_flags_off_and_unknown_actor_is_reported(self):
        p=actor();p['system']['traits']={};p['system']['abilities']={};p['items']=[]
        with tempfile.TemporaryDirectory() as tmp:
            good=document('Actor',p);bad=document('Actor',{'_id':'bad','name':'Alien','type':'npc'})
            bad.pop('format');bad.pop('display')
            files,r=campaign_files(campaign([good,bad]),tmp,notes_folder='Campaign')
            b=find(node(files[r['documents'][0]['target'][:-7]+'.rwnote']),'ArkenNoteFieldStatBlock5e')[0].members
            self.assertFalse(b['_damageImmunitiesFieldActive']);self.assertFalse(b['_savingThrowsFieldActive'])
            self.assertNotIn('Actor.bad',r['links']);self.assertTrue(any(l['grade']=='unsupported' for l in r['losses']))

    def test_item_spell_portrait_and_links_are_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);Image.new('RGB',(20,30),'red').save(root/'portrait.png')
            docs=[document('Item',{'_id':'i','name':'Blade','type':'weapon','img':'portrait.png','system':{'rarity':'rare','description':{'value':'<b>Open</b> @UUID[Item.s]{Spell} [[/r 1d6]]'}}}),
                  document('Item',{'_id':'s','name':'Flame','type':'spell','system':{'level':1,'school':'evo','activation':{'type':'action','value':1},'range':{'value':60,'units':'ft'},'description':{'value':'Burn.'}}})]
            files,r=campaign_files(campaign(docs),root,notes_folder='Campaign')
            self.assertEqual((r['counts']['items'],r['counts']['spells']),(1,1))
            item=node(files[r['links']['Item.i'][:-7]+'.rwnote'])
            field=find(item,'ArkenNoteField5eItemBlock')[0]
            self.assertEqual(content(field.members['_typeText']),'weapon, rare')
            self.assertEqual(content(field.members['_descriptionText']),'Open Spell 1d6')
            chars=find(item,'ArkenTextCharacter')
            self.assertTrue(any(c.members['_link']==r['links']['Item.s'] for c in chars))
            self.assertEqual(len(find(item,'ArkenNoteFieldMedia')),1)
            self.assertGreater(check_metadata_references(files),0)

    def test_all_tables_convert_and_bad_source_formula_is_not_repaired(self):
        table={'_id':'t','name':'Injuries','formula':'1d2','replacement':True,'results':[{'range':[1,1],'weight':1,'description':'One'},{'range':[2,9],'weight':1,'description':'Other'}]}
        with tempfile.TemporaryDirectory() as tmp:
            files,r=campaign_files(campaign([document('RollTable',table)]),tmp,notes_folder='Campaign')
            self.assertEqual(r['counts']['tables'],1)
            self.assertEqual(len(find(node(files[r['links']['RollTable.t'][:-7]+'.rwnote']),'ArkenNoteFieldRollableTableRow')),2)
            self.assertTrue(any(l.get('formula')=='1d2' and l['grade']=='approximate' for l in r['losses']))

    def test_playlist_mp3_is_manual_and_ogg_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'song.mp3').write_bytes(b'ID3')
            # Bounded synthetic Vorbis identification page (no playback claim).
            packet=b'\x01vorbis'+struct.pack('<I',0)+b'\x01'+struct.pack('<I',48000)+bytes(14)
            ogg=b'OggS'+bytes([0,6])+struct.pack('<QII',96000,1,0)+bytes(4)+bytes([1,len(packet)])+packet
            (root/'song.ogg').write_bytes(ogg)
            files,r=playlist_files({'_id':'p','name':'Ambient','sounds':[{'_id':'m','path':'song.mp3'},{'_id':'o','path':'song.ogg','name':'Track'}]},root,'scope')
            self.assertEqual((r['playlists'],r['tracks'],r['manual_tracks']),(1,1,1))
            audio=next(data for path,data in files.items() if path.endswith('.rwfile'))
            reader=Reader(audio);reader.read()
            self.assertIn(ogg,[bytes(o['bytes']) for o in reader.objects.values() if isinstance(o,dict) and 'bytes' in o])
            playlist=next(data for path,data in files.items() if path.endswith('.rwpl'))
            self.assertEqual(node(playlist).members['_songs'].members['_entries'].members['_size'],1)
            info=find(node(playlist),'MusicTrackInfo')[0]
            volumes=info.members['_trackVolumes'].members
            self.assertEqual(volumes['HashSize'],3)
            self.assertEqual(volumes['Version'],2)
            pair=volumes['KeyValuePairs'].items[0].members
            self.assertEqual(pair['key'],'Master')
            self.assertAlmostEqual(pair['value'],.8)
            self.assertGreater(check_metadata_references(files),0)

    def test_tiles_preserve_existing_map_and_use_padding_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);Image.new('RGBA',(100,50),'red').save(root/'tile.png')
            original=record('blank');existing=record('wall');existing.members['_tileInfo'].members['_uID']=1
            original.members['_tiles'].members['_items'].items=[existing];original.members['_tiles'].members.update(_size=1,_version=1);original.members['_nextUID']=2
            before=encode(original)
            scene={'_id':'s','width':400,'height':200,'padding':.25,'grid':{'type':1,'size':50},'tiles':[{'_id':'tile','x':150,'y':100,'width':100,'height':50,'rotation':30,'texture':{'src':'tile.png'}},{'_id':'video','texture':{'src':'clip.webm'}},{'_id':'unsafe','texture':{'src':'../bad.png'}}]}
            after,files,r=add_tiles(before,scene,root,'scope')
            self.assertEqual(r['count'],1);self.assertEqual(len(r['losses']),3)
            tiles=node(after).members['_tiles'].members['_items'].items
            self.assertEqual(canonical_graph(encode(tiles[0])),canonical_graph(encode(existing)))
            self.assertEqual(len(tiles),2);self.assertEqual(node(after).members['_nextUID'],3)
            pos=tiles[1].members['_tileInfo'].members['_position'].members
            self.assertAlmostEqual(pos['x'],5.12,places=5);self.assertAlmostEqual(pos['y'],-3.84,places=5)
            self.assertEqual(tiles[1].members['_tileInfo'].members['_rotation'],-30)

    def test_adventure_wide_tables_links_and_isolation_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'source';root.mkdir();(root/'packs').mkdir()
            Image.new('RGB',(200,200),'red').save(root/'map.png')
            scene={'_id':'s','name':'Scene','width':200,'height':200,'padding':0,'grid':{'type':1,'size':50,'distance':5},'background':{'src':'map.png'},'notes':[{'_id':'n','entryId':'j','x':25,'y':25}]}
            table=lambda ident:{'_id':ident,'name':ident,'formula':'1d1','replacement':True,'results':[{'range':[1,1],'weight':1,'description':'Result'}]}
            adventure={'_id':'A','name':'Campaign','scenes':[scene],'tables':[table('linked'),table('unreachable')],'journal':[{'_id':'j','name':'Room','content':'@UUID[RollTable.linked]{Table} @UUID[Actor.actor]{Guard}'}],'actors':[actor()],'items':[]}
            other={'_id':'B','name':'Other','scenes':[],'tables':[table('foreign')]}
            (root/'module.json').write_text(json.dumps({'id':'campaign','title':'Campaign','packs':[{'name':'adventure','path':'packs/adventure.json','type':'Adventure','system':'dnd5e'}]}))
            (root/'packs/adventure.json').write_text(json.dumps([adventure,other]))
            report=convert(root,Path(tmp)/'out',pdf='references')
            self.assertEqual(report['status'],'PASS')
            c=report['campaign_content'][0];self.assertEqual((c['counts']['tables'],c['counts']['actors']),(2,1))
            self.assertNotIn('RollTable.foreign',c['links'])
            native=report['scenes'][0]['native_report']
            actual_notes=sum(1 for p in (Path(tmp)/'out/MyAssets/Encyclopedia/Notes').rglob('*.rwnote'))
            self.assertEqual(report['native_counts']['notes'],actual_notes)
            self.assertTrue(any(r['target']==c['links']['RollTable.linked'] for r in native['rewritten_links']))
            self.assertTrue(any(r['target']==c['links']['Actor.actor'] for r in native['rewritten_links']))
            self.assertEqual(report['runtime_validation'],'not performed')

    def test_captured_schema_field_sets_match_generated_fields(self):
        fixtures=Path(__file__).resolve().parents[1]/'fixtures/arkenforge-5e-templates'
        builder=CampaignBuilder()
        for kind in ('Character','Item','Spell'):
            captured=node((fixtures/('5e-'+kind+'.rwnote')).read_bytes());built=builder.block(kind)
            reference=find(captured,built.schema['name'])[0]
            self.assertEqual(set(built.members),set(reference.members))
            self.assertEqual(built.schema['types'],reference.schema['types'])

    def test_user_audio_metadata_matches_captured_base_and_visible_paths(self):
        from forgebridge.native_audio import record
        from forgebridge.scene_records import canonical_graph
        fixture=Path(__file__).resolve().parents[1]/'fixtures/arkenforge-user-playlist/toolkit-empty-playlist.rwmeta'
        reader=Reader(fixture.read_bytes());graph=reader.read();expected=reader.object_metadata[graph['root_id']]
        schema=json.loads((Path(__file__).resolve().parents[1]/'src/forgebridge/audio-schema.json').read_text())
        playlist=record(schema,'playlist_meta');song=record(schema,'song_meta')
        self.assertEqual(playlist.schema,expected)
        audio_control=json.loads((fixture.parent/'toolkit-user-audio-meta.schema.json').read_text())
        self.assertEqual(song.schema,audio_control['schema'])
        self.assertTrue(song.members['_isSong'])
        offset=song.schema['names'].index('_name')
        for key in ('names','types','infos'):self.assertEqual(song.schema[key][offset:],expected[key])
        for target in (playlist,song):
            self.assertIsNone(target.members['_prevPathIfDeleted'])
            self.assertIsNone(target.members['ArkenBaseMeta+_prevPathIfDeleted'])
        with tempfile.TemporaryDirectory() as tmp:
            files,_=playlist_files({'_id':'p','name':'Ambient','sounds':[]},tmp,'scope',folder='FB Campaign Check')
            self.assertIn('MyAssets/Playlists/FB Campaign Check/Ambient.rwpl',files)
            meta=node(files['MyAssets/Playlists/FB Campaign Check/Ambient.rwmeta'])
            self.assertEqual(meta.members['_creator'],'')

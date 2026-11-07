"""Owned fog/vision/effect regression data; runtime behavior is not inferred."""
import json
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest
from forgebridge.visibility_ir import foundry_visibility,fg_visibility
from forgebridge.native_visibility import apply_visibility,effect_node,schema,token_target
from forgebridge.scene_records import blank_map,template_map,record,encode
from forgebridge.native_scene import synthesize_map,_set
from forgebridge.native import Writer
from forgebridge.uvtt import _lights_to_uvtt, _scene_origin
from forgebridge.convert import convert
from forgebridge.native_dependencies import read_package,check_metadata_references
from forgebridge.fantasy_grounds import ModuleSource,list_images,to_uvtt
from test_campaign import node,find
from test_fantasy_grounds import module,DEFINITION,png


def scene():return {'_id':'s','width':400,'height':300,'padding':0,'grid':{'type':1,'size':100,'distance':5},'tokenVision':True,'fog':{'exploration':True},'lights':[],'tokens':[]}
def lamp(identity,kind='',dim=10,**fields):
    return {'_id':identity,'x':50,'y':70,'config':{'dim':dim,'bright':0,'animation':{'type':kind,'intensity':10}},**fields}
def geometry(s):
    u={'resolution':{'pixels_per_grid':100,'map_size':{'x':4,'y':3}},'lights':[v for v in _lights_to_uvtt(s['lights'],s,100,[],_scene_origin(s,100,[])) if v.get('range',0)>0]}
    return synthesize_map(blank_map(),template_map(),u,name='Test',image_meta_path='MyAssets/Media/Background.rwmeta',asset_name='Background')[0]
def presets(data):
    n=node(data);seq=n.members['_tiles'].members
    return n,[t.members['_tileInfo'] for t in seq['_items'].items[:seq['_size']]]

class VisibilityTests(unittest.TestCase):
    def test_captured_effect_defaults_and_schema_roundtrip(self):
        for kind,cls in [('flicker','ObjectEffectLightFlicker'),('blink','ObjectEffectLightBlink')]:
            e=effect_node(kind);self.assertEqual(e.schema,schema()['classes'][cls]);self.assertEqual(node(Writer({2:schema()['libraries']['2']}).write(e)).members,e.members)
            self.assertTrue(e.members['_enabled']);self.assertEqual(e.members['_name'],e.members['ObjectEffectBase+_name'])
        self.assertEqual(effect_node('flicker').members['_intensity'],1.)
        b=effect_node('blink').members;self.assertAlmostEqual(b['_timeBetweenBlinks'],.075,places=6);self.assertEqual(b['_maxBlinkCount'],5);self.assertEqual(b['_waitTime'],4.)

    def test_dynamic_fog_flags_no_historical_mask_or_custom_intensity_claim(self):
        s=scene();s['fog']['exploration']=False;s['environment']={'darknessLevel':.8}
        original=geometry(s);old=node(original);data,r=apply_visibility(original,foundry_visibility(s),namespace='x');n=node(data)
        self.assertTrue(n.members['_fogEnabled']);self.assertEqual(n.members['_fogMode'].members['value__'],2);self.assertFalse(n.members['_fogPersists'])
        self.assertEqual(n.members['_useCustomLightIntensity'],old.members['_useCustomLightIntensity']);self.assertEqual(n.members['_customLightIntensity'],old.members['_customLightIntensity'])
        self.assertTrue(any(l['feature']=='scene-darkness' and l['grade']=='manual' for l in r['losses']));self.assertFalse(r['fog']['historical_masks_migrated'])
        s['tokenVision']=False;data,_=apply_visibility(original,foundry_visibility(s),namespace='x');self.assertFalse(node(data).members['_fogEnabled'])

    def test_flicker_blink_darkness_reveal_and_unsupported_animation(self):
        s=scene();s['lights']=[lamp('torch','torch',vision=True),lamp('pulse','pulse'),lamp('ghost','ghost'),lamp('negative','',-15),lamp('dark-flag','torch')]
        s['lights'][-1]['config']['negative']=True
        before=geometry(s);data,r=apply_visibility(before,foundry_visibility(s),namespace='x');n,ps=presets(data)
        self.assertEqual(len(r['lights']),5);self.assertEqual(len(ps),6);self.assertEqual(n.members['_nextUID'],max(p.members['_uID'] for p in ps)+1)
        mapped={v['source_id']:v for v in r['lights']}
        self.assertTrue(mapped['torch']['reveals']);self.assertTrue(mapped['negative']['darkness']);self.assertAlmostEqual(mapped['negative']['native_radius'],7.68)
        self.assertFalse(mapped['dark-flag']['reveals']);self.assertTrue(any(l.get('source_id')=='ghost' and l['grade']=='unsupported' for l in r['losses']))
        self.assertEqual(len(find(n,'ObjectEffectLightFlicker')),2);self.assertEqual(len(find(n,'ObjectEffectLightBlink')),1)
        self.assertTrue(next(p for p in ps if p.members['_uID']==mapped['torch']['native_uid']).members['_lighting'].members['_flicker'])

    def test_player_ownership_darkvision_and_npc_exclusion_with_calibrated_radius(self):
        s=scene();actors=[{'_id':'pc','type':'character','ownership':{'p':3}},{'_id':'npc','type':'npc','ownership':{'p':3}},{'_id':'none','type':'character','ownership':{'default':0}}]
        for identity,actor,mode in [('a','pc','basic'),('b','pc','darkvision'),('c','npc','darkvision'),('d','none','basic')]:s['tokens'].append({'_id':identity,'name':identity,'actorId':actor,'sight':{'enabled':True,'range':30,'visionMode':mode}})
        root=node(geometry(s));seq=root.members['_tiles'].members
        for t in s['tokens']:
            tile=record('content');p=tile.members['_tileInfo'].members
            _set(p,_contentBasePath=token_target('scope','Scene.s.Token.'+t['_id']),_uID=root.members['_nextUID']);root.members['_nextUID']+=1;seq['_items'].items.append(tile);seq['_size']+=1
        data,r=apply_visibility(encode(root),foundry_visibility(s,actors),namespace='scope',units_per_grid=3.2)
        self.assertEqual(len(r['tokens']),2);self.assertEqual(len(r['excluded_tokens']),2)
        self.assertAlmostEqual(r['tokens'][0]['native_radius'],19.2);self.assertEqual(r['tokens'][1]['intensity'],.15)
        _,ps=presets(data);self.assertFalse(ps[-1].members['_lighting'].members['_hasLight']);self.assertFalse(ps[-2].members['_lighting'].members['_hasLight'])
        self.assertTrue(any(l['feature']=='token-vision' and l['grade']=='approximate' for l in r['losses']))

    def test_disabled_missing_unlimited_sight_and_unknown_modes_are_not_guessed(self):
        s=scene();s['tokens']=[{'_id':'a','actorId':'pc','sight':{'enabled':True,'range':0}},{'_id':'b','actorId':'pc','sight':{'enabled':True,'range':30,'visionMode':'tremor'}},{'_id':'c','actorId':'pc','sight':{'enabled':False,'range':30}}]
        ir=foundry_visibility(s,[{'_id':'pc','type':'character','ownership':{'default':3}}]);self.assertEqual(ir['tokens'],[]);self.assertEqual(len(ir['excluded_tokens']),1);self.assertTrue(any(l['feature']=='token-vision' for l in ir['losses']))

    def test_source_origin_negative_light_and_hidden_emitter(self):
        s=scene();s['padding']=.5;s['lights']=[lamp('dark','',-5),lamp('hide','blink',hidden=True,vision=True)]
        data,r=apply_visibility(geometry(s),foundry_visibility(s),namespace='x')
        dark=next(x for x in r['lights'] if x['source_id']=='dark');self.assertAlmostEqual(dark['position']['x'],(50-200)/100*2.56);self.assertAlmostEqual(dark['position']['y'],-(70-200)/100*2.56)
        hidden=next(x for x in r['lights'] if x['source_id']=='hide');self.assertFalse(hidden['enabled']);self.assertFalse(hidden['reveals'])

    def test_foundry_convert_uses_scoped_actor_ownership_and_closed_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';shutil.copytree(Path(__file__).resolve().parents[1]/'fixtures/synthetic-module',source)
            sp=source/'packs/scenes.db';s=json.loads(sp.read_text(encoding='utf-8'));actorpath=source/'packs/actors.db';actor=json.loads(actorpath.read_text(encoding='utf-8'));actor.update(type='character',ownership={'player':3});actorpath.write_bytes((json.dumps(actor)+'\n').encode())
            s.update(tokenVision=True,fog={'exploration':True},tokens=[{'_id':'pc','name':'PC','actorId':actor['_id'],'x':20,'y':40,'width':1,'height':1,'texture':{'src':'assets/crypt.png'},'sight':{'enabled':True,'range':30,'visionMode':'darkvision'}}]);sp.write_bytes(json.dumps(s).encode())
            r=convert(source,root/'out');self.assertEqual(r['status'],'PASS');native=r['scenes'][0]['native_report'];self.assertEqual(len(native['visibility']['tokens']),1)
            files=read_package(root/'out/scene-001/native-package.zip');self.assertGreater(check_metadata_references(files),0)
            n=node(files[native['output_names']['map_path']]);self.assertEqual(n.members['_fogMode'].members['value__'],2)

    def test_fg_los_light_animation_and_disabled_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=module(tmp,{'definition.xml':DEFINITION,'images/m.png':png(),'db.xml':b'<root><image><m><name>Map</name><image type="image"><bitmap>images/m.png</bitmap><gridsize>100,100</gridsize><occluders/><los>on</los><fogexploration>off</fogexploration><lights><light><position>0,0</position><range>2,1</range><animation>pulse</animation><on/></light><light><position>50,0</position><range>1,1</range><flicker/></light></lights></image></m></image></root>'})
            r=convert(p,Path(tmp)/'out');self.assertEqual(r['status'],'PASS');v=r['scenes'][0]['native_report']['visibility'];self.assertEqual(v['fog']['mode'],2);self.assertFalse(v['fog']['persists']);self.assertEqual(v['lights'][0]['effect']['kind'],'blink');self.assertFalse(v['lights'][1]['enabled'])

    def test_missing_native_token_never_becomes_global_reveal_light(self):
        s=scene();s['tokens']=[{'_id':'pc','actorId':'pc','sight':{'enabled':True,'range':30}}]
        ir=foundry_visibility(s,[{'_id':'pc','type':'character','ownership':{'default':3}}]);data,r=apply_visibility(geometry(s),ir,namespace='missing')
        self.assertEqual(r['tokens'],[]);self.assertEqual(len(presets(data)[1]),1);self.assertTrue(any('No generated native token' in l['summary'] for l in r['losses']))

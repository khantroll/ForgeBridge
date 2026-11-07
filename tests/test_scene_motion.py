"""Owned media controls and synthetic scene conversion; no runtime claims."""
import copy
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from PIL import Image
from forgebridge.convert import convert
from forgebridge.native import Writer, Array
from forgebridge.nrbf import Reader
from forgebridge.native_motion import motion_asset, record
from forgebridge.native_tiles import add_tiles
from forgebridge.native_ambience import add_ambience, sfx_files
from forgebridge.scene_records import blank_map, record as scene_record, encode
from forgebridge.native_dependencies import write_archive, read_package, check_metadata_references
from forgebridge.native_capture import dependency_closure
from forgebridge.installer import install, uninstall
from test_campaign import node, find, content
from test_native_music import parsed, objects

ROOT=Path(__file__).parents[1]
FIXTURE=ROOT/'fixtures/synthetic-motion-adventure'
CONTROLS=ROOT/'fixtures/arkenforge-native-controls-2026-11-03'
SOURCE=json.loads((FIXTURE/'packs/adventure.db').read_text(encoding='utf-8'))
SCENE=SOURCE['scenes'][0]


class SceneMotionTests(unittest.TestCase):
    def test_video_controls_codec_payload_and_typed_preset(self):
        for filename,codec in [('FBReference-motion.webm','VP9'),('FBReference-video.mp4','H.264')]:
            source=CONTROLS/'sources'/filename;raw=source.read_bytes()
            asset,meta,preset,info,losses=motion_asset(raw,source.suffix,'Motion')
            self.assertEqual((info['width'],info['height'],info['codec']),(64,64,codec))
            r,_=parsed(asset)
            video=objects(r,'ArkenVideo')[0]
            self.assertEqual(bytes(video.members['_rawFile'].items),raw)
            self.assertEqual(video.members['_originalFile'],hashlib.sha256(raw).hexdigest()[:20]+source.suffix)
            self.assertEqual(preset.schema['name'],'ArkenTilePresetVideo')
            self.assertTrue(preset.members['_videoPlaying']);self.assertTrue(preset.members['_loop'])
            self.assertFalse(preset.members['_soundEnabled'])
            metadata=parsed(meta)[1]
            self.assertEqual(metadata.members['_tileCategory'].members['value__'],2)
            variant=metadata.members['_variations'].members['_items'].items[0]
            self.assertTrue(all(v=='Motion' for k,v in variant.members.items() if k.split('+')[-1] in ('_name','_tileName')))
            self.assertTrue(losses)

    def test_gif_frames_and_timing_preserved_with_position_rotation_hidden(self):
        scene=copy.deepcopy(SCENE);scene.update(grid={'size':50,'type':1,'distance':5},dimensions={'sceneX':100,'sceneY':50})
        tile=scene['tiles'][1];tile.update(x=150,y=100,width=100,height=50,rotation=30,hidden=True);scene['tiles']=[tile]
        data,files,audit=add_tiles(blank_map(),scene,FIXTURE,'test')
        self.assertEqual(audit['animated_count'],1)
        preset=node(data).members['_tiles'].members['_items'].items[0].members['_tileInfo'].members
        self.assertAlmostEqual(preset['_position'].members['x'],5.12,places=5)
        self.assertAlmostEqual(preset['_position'].members['y'],-3.84,places=5)
        self.assertAlmostEqual(preset['_rotation'],-30);self.assertTrue(preset['_hidden'])
        self.assertAlmostEqual(preset['_scale'].members['x'],8)
        self.assertAlmostEqual(preset['_scale'].members['y'],4)
        self.assertEqual(preset['_category'].members['value__'],1)
        self.assertEqual(preset['_animation'].members['_noOfFrames'],4.)
        self.assertEqual(preset['_animation'].members['_framesPerSecond'],4.)
        r,asset=parsed(next(data for key,data in files.items() if key.endswith('.rwfile')))
        sequence=asset.members['_content'].members
        self.assertEqual(sequence['_size'],4)
        self.assertEqual(asset.members['_category'].members['value__'],1)
        with Image.open(FIXTURE/'assets/moving.gif') as source:
            for index,image in enumerate(sequence['_items'].items):
                source.seek(index);raw=bytes(image.members['_packImageRAW'].items)
                with Image.open(io.BytesIO(raw)) as result:self.assertEqual(result.convert('RGBA').tobytes(),source.convert('RGBA').tobytes())

    def test_repeated_motion_texture_has_unique_placements_and_shared_assets(self):
        scene=copy.deepcopy(SCENE);tile=scene['tiles'][1];other=copy.deepcopy(tile);other['_id']='other';other['x']+=100;scene['tiles']=[tile,other]
        data,files,audit=add_tiles(blank_map(),scene,FIXTURE,'scope')
        self.assertEqual(len(files),2);self.assertEqual(audit['count'],2)
        items=node(data).members['_tiles'].members['_items'].items
        self.assertNotEqual(items[0].members['_tileInfo'].members['_uID'],items[1].members['_tileInfo'].members['_uID'])
        self.assertEqual(audit['tiles'][0]['target'],audit['tiles'][1]['target'])

    def test_unknown_codec_truncated_container_and_bad_paths_are_explicit_losses(self):
        mp4=(CONTROLS/'sources/FBReference-video.mp4').read_bytes().replace(b'avc1',b'hvc1')
        with self.assertRaisesRegex(ValueError,'H.264'):motion_asset(mp4,'.mp4','Bad')
        with self.assertRaises(ValueError):motion_asset(b'bad','.webm','Bad')
        scene=copy.deepcopy(SCENE);template=copy.deepcopy(scene['tiles'][0])
        scene['tiles']=[{**template,'texture':{'src':'../secret.webm'}},{**template,'texture':{'src':'missing.webm'}},{**template,'width':float('nan')},{**template,'texture':None},{**template,'texture':{'src':123}}]
        data,files,audit=add_tiles(blank_map(),scene,FIXTURE,'bad')
        self.assertEqual(audit['count'],0);self.assertFalse(files);self.assertEqual(len(audit['losses']),5)
        self.assertTrue(all(row['grade']=='manual' for row in audit['losses']))

    def test_variable_frame_timing_is_reported_and_frame_budget_enforced(self):
        frames=[Image.new('RGB',(8,8),colour) for colour in ('red','green')];out=io.BytesIO()
        frames[0].save(out,'GIF',save_all=True,append_images=frames[1:],duration=[100,300],loop=0)
        asset,meta,preset,info,losses=motion_asset(out.getvalue(),'.gif','Variable')
        self.assertEqual(info['source_frame_ms'],[100.,300.]);self.assertAlmostEqual(info['fps'],5.)
        self.assertTrue(any('fixed FPS' in loss for loss in losses))
        missing=io.BytesIO();frames[0].save(missing,'GIF',save_all=True,append_images=frames[1:],loop=0)
        self.assertTrue(any('assumes 100 ms' in loss for loss in motion_asset(missing.getvalue(),'.gif','Missing')[4]))
        frames=[Image.new('RGB',(8,8),(i,0,0)) for i in range(129)];out=io.BytesIO()
        frames[0].save(out,'GIF',save_all=True,append_images=frames[1:],duration=100,optimize=False)
        with self.assertRaisesRegex(ValueError,'budget'):motion_asset(out.getvalue(),'.gif','Large')

    def test_sound_radius_distance_padding_volume_and_hidden_are_independent(self):
        scene=copy.deepcopy(SCENE);scene.update(grid={'type':1,'size':50,'distance':5},dimensions={'sceneX':100,'sceneY':50})
        sound=scene['sounds'][0];sound.update(x=250,y=150,radius=15,volume=.3,hidden=True);scene['sounds']=[sound]
        data,files,audit=add_ambience(blank_map(),scene,FIXTURE,'radius')
        self.assertEqual(audit['count'],1);row=audit['sounds'][0]
        self.assertAlmostEqual(row['native_position']['x'],7.68);self.assertAlmostEqual(row['native_position']['y'],-5.12)
        self.assertAlmostEqual(row['native_outer_radius'],7.68)
        tile=node(data).members['_tiles'].members['_items'].items[0].members['_tileInfo'].members
        ambience=tile['ArkenTilePresetBase+_ambience'].members
        self.assertFalse(ambience['_active']);self.assertTrue(ambience['_playWhenHidden'])
        self.assertAlmostEqual(ambience['_volume'],.3)
        self.assertEqual(tile['_contentType'],'Ambience Preset')
        self.assertTrue(tile['_contentBasePath'].endswith('.rwamb'))
        preset=node(files[row['preset']]);self.assertEqual(preset.members['_defaultVolume'],1.)
        track=preset.members['_tracks'].members['_items'].items[0].members['_content']
        self.assertEqual(track.members['_options'].members['KeyValuePairs'].items[0].members['value'],1.)

    def test_sfx_payloads_wav_ogg_mp3_are_embedded_as_sfx_not_songs(self):
        with self.assertRaisesRegex(ValueError,'Only OGG'):sfx_files(b'not flac','.flac','Bad')
        paths=[FIXTURE/'assets/left.ogg',FIXTURE/'assets/right.wav',ROOT/'fixtures/arkenforge-user-playlist/toolkit-made-music-playlist/sources/FBMusicControl-MP3.mp3']
        for source in paths:
            with self.subTest(source=source):
                raw=source.read_bytes();asset,meta,duration=sfx_files(raw,source.suffix,'Tone');r,root=parsed(asset)
                self.assertFalse(root.members['_isSong']);self.assertFalse(node(meta).members['_isSong']);self.assertGreater(duration,0)
                audio=objects(r,'AudioTrack')[0]
                self.assertEqual(bytes(audio.members['_clipRAW'].items),raw)
                self.assertEqual(audio.members['_originalFile'],hashlib.sha256(raw).hexdigest()[:20]+source.suffix)

    def test_sound_invalid_grid_volume_audio_missing_or_unsafe_are_losses(self):
        for change in ({'radius':-1},{'volume':2},{'path':'../secret.wav'},{'path':'missing.flac'},{'path':123}):
            scene=copy.deepcopy(SCENE);scene['sounds']=[{**scene['sounds'][0],**change}]
            data,files,audit=add_ambience(blank_map(),scene,FIXTURE,'bad')
            self.assertEqual(audit['count'],0);self.assertFalse(files);self.assertEqual(audit['losses'][0]['grade'],'manual')
        scene=copy.deepcopy(SCENE);scene['grid']['distance']=0
        self.assertEqual(add_ambience(blank_map(),scene,FIXTURE,'bad')[2]['count'],0)

    def test_ambience_dependency_closure_includes_preset_meta_and_audio_pair(self):
        data,files,audit=add_ambience(blank_map(),SCENE,FIXTURE,'closure')
        files.update({'MyAssets/Maps/Control.rwmap':data,'MyAssets/Maps/Control.rwmeta':encode(scene_record('map_meta'))})
        check_metadata_references(files)
        primary,found,edges=dependency_closure(files)
        self.assertTrue(any(path.endswith('.rwamb') for path in found))
        self.assertEqual(set(found),set(files))
        broken=dict(files);broken.pop(audit['sounds'][0]['preset'])
        with self.assertRaisesRegex(ValueError,'Missing native'):check_metadata_references(broken)
        broken=dict(files);broken.pop(audit['sounds'][0]['audio'])
        with self.assertRaisesRegex(ValueError,'audio payload'):check_metadata_references(broken)

    def test_full_fixture_install_uninstall_and_empty_line_encoding(self):
        with tempfile.TemporaryDirectory() as tmp,patch('forgebridge.installer.require_toolkit_closed'):
            root=Path(tmp);out=root/'out';report=convert(FIXTURE,out,map_folder='FB Motion Check',notes_folder='FB Motion Check',pdf='references')
            self.assertEqual(report['status'],'PASS');self.assertEqual(report['native_counts']['animated_tiles'],2);self.assertEqual(report['native_counts']['ambient_sounds'],2)
            native=read_package(out/'scene-001/native-package.zip')
            notes=[node(v) for k,v in native.items() if k.endswith('.rwnote')]
            block=next(b for n in notes for b in find(n,'ArkenNoteFieldStatBlock5e'))
            for field in ('_skillsText','_sensesText','_languagesText','_proficiencyBonusText','_challengeText'):
                value=block.members[field]
                self.assertEqual(content(value),'\u200b')
                self.assertTrue(all(c.members['_size']==0 for c in value.members['_characters'].members['_items'].items))
            self.assertFalse(block.members['_savingThrowsFieldActive'])
            assets=root/'MyAssets';assets.mkdir();(assets/'user.txt').write_bytes(b'user')
            installed=install([out/'scene-001/native-package.zip'],assets,root/'backups')
            self.assertGreater(installed['added'],10)
            result=uninstall(installed['receipt']);self.assertEqual(result['removed'],installed['added'])
            self.assertEqual([p.relative_to(assets).as_posix() for p in assets.rglob('*') if p.is_file()],['user.txt'])

    def test_opaque_byte_array_limit_remains_bounded_and_opt_in(self):
        payload=b'a'*2000001
        with self.assertRaises(ValueError):Writer({}).write(Array(payload,0,2))
        data=Writer({},max_items=64000000).write(Array(payload,0,2))
        reader=Reader(data,max_items=64000000);graph=reader.read();self.assertEqual(reader.objects[graph['root_id']]['bytes'],payload)

    def test_saved_map_capture_keeps_ambience_metadata_and_original_bytes(self):
        from forgebridge.native_capture import capture_saved
        data, files, audit=add_ambience(blank_map(),SCENE,FIXTURE,'snapshot')
        files.update({'MyAssets/Maps/Control.rwmap':data,'MyAssets/Maps/Control.rwmeta':encode(scene_record('map_meta'))})
        with tempfile.TemporaryDirectory() as tmp, patch('forgebridge.native_capture._toolkit_closed') as closed:
            root=Path(tmp); assets=root/'MyAssets'; assets.mkdir()
            for name, payload in files.items():
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
            result=capture_saved(assets,'MyAssets/Maps/Control.rwmap',root/'bundle',closed=True)
            self.assertEqual(closed.call_count,3)
            self.assertEqual({row['path'] for row in result['files']},set(files))
            self.assertEqual(read_package(root/'bundle/native.zip'),files)
            self.assertEqual({name:(root/name).read_bytes() for name in files},files)

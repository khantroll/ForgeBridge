"""Foundry sound IR to schema-built SFX, presets and map content-link anchors."""
import hashlib
import io
import math
from pathlib import Path
from urllib.parse import unquote
import wave
from forgebridge.native import Array, Writer
from forgebridge.native_audio import names, sequence, vorbis_duration, mp3_duration
from forgebridge.native_motion import record, encode
from forgebridge.native_map import clone
from forgebridge.nrbf import Reader
from forgebridge.scene_records import record as scene_record
from forgebridge.native_scene import _set, UNITS_PER_GRID
from forgebridge.scene_media import sound_ir
from forgebridge.uvtt import _safe_ref, _package_file
from forgebridge.validate import InventoryFatal


def sfx_files(data,suffix,name):
    if suffix=='.ogg':duration=vorbis_duration(data)
    elif suffix=='.mp3':duration=mp3_duration(data)
    elif suffix=='.wav':
        with wave.open(io.BytesIO(data),'rb') as source:
            if source.getcomptype()!='NONE' or source.getnchannels() not in (1,2) or source.getsampwidth() not in (1,2,3,4) or not 8000<=source.getframerate()<=192000:
                raise ValueError('Only mono/stereo uncompressed PCM WAV is supported')
            if len(source.readframes(source.getnframes()))!=source.getnframes()*source.getnchannels()*source.getsampwidth():raise ValueError('Truncated WAV payload')
            duration=source.getnframes()/source.getframerate()
    else:raise ValueError('Only OGG Vorbis, MP3 and PCM WAV ambient audio are supported')
    if not math.isfinite(duration) or duration<=0:raise ValueError('Empty/invalid audio duration')
    sfx,meta=record('sfx'),record('sfx_meta')
    for node in (sfx,meta):names(node,name);node.members.update(_duration=duration,_isSong=False)
    track=sfx.members['_tracks'].members['_items'].items[0]
    track.members.update(_trackName='Master',_originalFile=hashlib.sha256(data).hexdigest()[:20]+suffix,_clipRAW=Array(data,0,2),_parentName=name)
    sequence(sfx.members['_tracks'],[track])
    return encode(sfx),encode(meta),duration


def add_ambience(data,scene,package,scope):
    source=scene.get('sounds',[])
    if not isinstance(source,list) or len(source)>256:raise ValueError('Ambient sound collection exceeds 256')
    if not source:return data,{}, {'count':0,'sounds':[],'losses':[]}
    reader=Reader(data,max_items=64000000);graph=reader.read();root=clone(reader,graph['root_id'])
    collection=root.members['_tiles'].members;items=collection['_items'].items[:collection['_size']]
    uid=root.members['_nextUID'];files={};rows=[];losses=[]
    for index,sound in enumerate(source):
        ref=sound.get('path') if isinstance(sound,dict) else None
        try:
            if not isinstance(sound,dict):raise ValueError('Invalid ambient sound document')
            ir=sound_ir(scene,sound,index)
            if not isinstance(ref,str):raise ValueError('Unsafe/missing ambient audio path')
            safe,problem=_safe_ref(unquote(ref))
            if problem or not safe:raise ValueError('Unsafe/missing ambient audio path')
            path=_package_file(Path(package),safe)
            if path.stat().st_size>16*1024*1024:raise ValueError('Ambient audio exceeds 16 MiB')
            payload=path.read_bytes();key=hashlib.sha256((scope+'\0'+str(ir['source_id'])).encode()+payload).hexdigest()[:20]
            audio='MyAssets/Audio/SFX/ForgeBridge-'+scope+'/'+key
            preset_path='MyAssets/AmbiencePresets/ForgeBridge-'+scope+'/'+key
            sfx,meta,duration=sfx_files(payload,path.suffix.lower(),ir['name'])
            preset,preset_meta=record('ambience'),record('ambience_meta')
            for node in (preset,preset_meta):names(node,ir['name'])
            preset.members['_defaultVolume']=1.
            entry=preset.members['_tracks'].members['_items'].items[0]
            entry.members['_filePath']=audio+'.rwmeta'
            track=entry.members['_content'];names(track,ir['name'])
            options=track.members['_options'].members
            options['KeyValuePairs'].items[0].members['value']=1.
            sequence(preset.members['_tracks'],[entry])
            node=scene_record('content');p=node.members['_tileInfo'].members
            p['_position'].members.update(x=ir['position_squares'][0]*UNITS_PER_GRID,y=-ir['position_squares'][1]*UNITS_PER_GRID)
            p['_scale'].members.update(x=1.,y=1.)
            _set(p,_contentBasePath=preset_path+'.rwamb',_contentType='Ambience Preset',_name=ir['name'],_tileName=ir['name'],_uID=uid,_sortingOrder=len(items),_hidden=True,_locked=False,_groupID=-1,_mapLevel=0)
            ambience=p['ArkenTilePresetBase+_ambience'].members
            radius=ir['radius_squares']*UNITS_PER_GRID
            inner=0. if ir['easing'] else radius*.999
            ambience.update(_active=not ir['hidden'],_audioPath=preset_path+'.rwamb',_radius=inner,_falloffRadius=radius,_volume=float(ir['volume']),_playWhenHidden=True,_playOnAllLevels=False)
            files.update({audio+'.rwfile':sfx,audio+'.rwmeta':meta,preset_path+'.rwamb':encode(preset),preset_path+'.rwmeta':encode(preset_meta)})
            items.append(node);uid+=1
            rows.append({**ir,'native_position':dict(p['_position'].members),'native_inner_radius':inner,'native_outer_radius':radius,'preset':preset_path+'.rwamb','audio':audio+'.rwfile','source_sha256':hashlib.sha256(payload).hexdigest(),'duration_seconds':duration,'bytes_preserved':True})
            losses.append({'grade':'approximate','feature':'ambient-sound','source_id':ir['source_id'],'summary':'Outer radius and volume mapped; native linear falloff approximates Foundry easing (0.1% edge when disabled); wall occlusion, timing/repeat, darkness conditions, channel/levels and effects require native review; preset/track gain 1; source hidden disables playback; anchor hidden is only an icon setting'})
        except (OSError,ValueError,InventoryFatal,wave.Error,EOFError) as exc:
            losses.append({'grade':'manual','feature':'ambient-sound','source_id':sound.get('_id') if isinstance(sound,dict) else None,'source':ref,'summary':str(exc)})
    collection['_items'].items=items;collection.update(_size=len(items),_version=collection['_version']+len(rows));root.members['_nextUID']=uid
    return Writer(reader.libraries,max_items=64000000).write(root),files,{'count':len(rows),'sounds':rows,'losses':losses}

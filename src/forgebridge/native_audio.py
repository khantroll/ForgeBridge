"""Schema-built playlists; only locally supplied OGG Vorbis is embedded.

MP3 playback is unverified and no encoder is assumed. Those tracks remain
explicit manual losses, without dangling native song references.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct

from forgebridge.native import Node, Array, Writer
from forgebridge.uvtt import _safe_ref, _package_file
from forgebridge.validate import InventoryFatal
from forgebridge.output_names import sanitize_name


def record(schema, name):
    memo={}
    def build(v):
        if not isinstance(v,dict):return deepcopy(v)
        if 'use' in v:return memo[v['use']]
        if 'class' in v:
            definition=deepcopy(schema['classes'][v['class']])
            if set(v['members'])!=set(definition['names']):raise ValueError('Audio schema/default mismatch')
            result=Node(definition,{},v['inline']);memo[v['id']]=result
            result.members.update({k:build(x) for k,x in v['members'].items()})
        else:
            result=Array([], *deepcopy(v['array']));memo[v['id']]=result
            result.items.extend(build(x) for x in v['items'])
        return result
    return build(schema['defaults'][name])


def names(node,name):
    for key in node.members:
        bare=key.split('+')[-1]
        if bare=='_name':node.members[key]=name
        elif bare=='_creator':node.members[key]=''


def sequence(node, values):
    node.members['_items'].items=list(values);node.members.update(_size=len(values),_version=len(values))


def vorbis_duration(data):
    """Validate page bounds/sequence, identify Vorbis and derive duration."""
    offset=0;granule=0;rate=None;serial=None;seq=0;end=False;packet=bytearray()
    while offset<len(data):
        if data[offset:offset+4]!=b'OggS' or offset+27>len(data) or data[offset+4]!=0:raise ValueError('Invalid OGG page')
        flags=data[offset+5];n=data[offset+26];table=data[offset+27:offset+27+n]
        if len(table)!=n:raise ValueError('Truncated OGG lacing table')
        length=27+n+sum(table)
        if offset+length>len(data):raise ValueError('Truncated OGG payload')
        sid,number=struct.unpack_from('<II',data,offset+14)
        if serial is None:serial=sid
        if sid!=serial or number!=seq:raise ValueError('Chained/multiplexed OGG is unsupported')
        seq+=1
        g=struct.unpack_from('<Q',data,offset+6)[0]
        if g!=2**64-1:granule=max(granule,g)
        payload=memoryview(data)[offset+27+n:offset+length];pos=0
        if rate is None:
            for part in table:
                packet.extend(payload[pos:pos+part]);pos+=part
                if part<255:
                    if len(packet)<30 or packet[:7]!=b'\x01vorbis':raise ValueError('Only OGG Vorbis audio is supported')
                    rate=struct.unpack_from('<I',packet,12)[0]
                    if not rate:raise ValueError('Invalid Vorbis sample rate')
                    break
        end=bool(flags&4);offset+=length
    if rate is None or not end:raise ValueError('Incomplete OGG Vorbis stream')
    return granule/rate


def playlist_files(source, package, scope, *, folder='ForgeBridge'):
    schema=json.loads(Path(__file__).with_name('audio-schema.json').read_text(encoding='utf-8'))
    playlist=record(schema,'playlist');meta=record(schema,'playlist_meta')
    name=sanitize_name(str(source.get('name') or 'Playlist'));folder=sanitize_name(folder)
    names(playlist,name);names(meta,name)
    key=hashlib.sha256((scope+'\0'+str(source.get('_id',source.get('id')))).encode()).hexdigest()[:20]
    base='MyAssets/Playlists/'+folder+'/'+name
    files={};entries=[];losses=[];tracks=0;songs=[]
    sounds=source.get('sounds',[])
    if not isinstance(sounds,list) or len(sounds)>256:raise ValueError('Invalid/oversized playlist')
    for sound in sounds:
        ref=sound.get('path');track_name=str(sound.get('name') or 'Track')
        try:
            safe,problem=_safe_ref(ref)
            if problem or not safe:raise ValueError('Unsafe/missing audio reference')
            path=_package_file(Path(package),safe)
            if path.suffix.lower()!='.ogg':raise ValueError('MP3/native playback unverified; no bundled encoder demonstrated. Supply OGG Vorbis manually; Toolkit ffmpeg is never used')
            if path.stat().st_size>64*1024*1024:raise ValueError('Audio exceeds 64 MiB')
            data=path.read_bytes();duration=vorbis_duration(data)
            songkey=hashlib.sha256((key+'\0'+str(sound.get('_id',tracks))+'\0').encode()+data).hexdigest()[:20]
            songbase='MyAssets/Audio/Songs/'+folder+'/'+sanitize_name(track_name)
            if songbase+'.rwfile' in files:raise ValueError('Song name conflict; rename source tracks before building: '+track_name)
            song=record(schema,'song');songmeta=record(schema,'song_meta');names(song,track_name);names(songmeta,track_name)
            song.members['_duration']=songmeta.members['_duration']=duration
            audio=record(schema,'audio_track');audio.members.update(_trackName='Master',_originalFile=songkey+'.ogg',_clipRAW=Array(list(data),0,2),_parentName=track_name)
            sequence(song.members['_tracks'],[audio])
            files[songbase+'.rwfile']=Writer(schema['libraries']).write(song)
            files[songbase+'.rwmeta']=Writer(schema['libraries']).write(songmeta)
            info=record(schema,'track_info');info.members.update(_name=track_name,_songPath=songbase+'.rwmeta',_creator='')
            content=record(schema,'content');content.members.update(_filePath=songbase+'.rwmeta',_content=info,_officialFlag=False)
            entry=record(schema,'entry');entry.members.update(_order=tracks,_value=content);entries.append(entry);tracks+=1
            songs.append({'source_id':sound.get('_id'),'source':ref,'source_sha256':hashlib.sha256(data).hexdigest(),
                          'native_file':songbase+'.rwfile','native_metadata':songbase+'.rwmeta','duration_seconds':duration,
                          'bytes_preserved':True,'runtime_validation':'not performed'})
        except (OSError,ValueError,InventoryFatal) as exc:
            losses.append({'grade':'manual','feature':'playlist-track','source':ref,'name':track_name,'summary':str(exc)})
    sequence(playlist.members['_songs'].members['_entries'],entries)
    files[base+'.rwpl']=Writer(schema['libraries']).write(playlist)
    files[base+'.rwmeta']=Writer(schema['libraries']).write(meta)
    losses.append({'grade':'approximate','feature':'playlist','summary':'Ordered song references only; source loop, fades, channel, mode, volume and playback state require manual review; playback not runtime-validated'})
    return files,{'playlists':1,'playlist':base+'.rwpl','source_id':source.get('_id',source.get('id')),
                  'tracks':tracks,'songs':songs,'manual_tracks':len(sounds)-tracks,'losses':losses}

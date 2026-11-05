"""Schema-built playlists embedding supplied MP3 and OGG Vorbis unchanged."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct
from urllib.parse import unquote

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


def music_track_info(schema, name, path):
    """Initialize the single Master stem emitted by this writer.

    Toolkit 0.5.1.18's file-import control creates Master at 80 percent.
    An empty dictionary still advances the playlist timer but has no stem
    volume. Keep the payload format decision separate from this mixer state.
    """
    info = record(schema, 'track_info')
    info.members.update(_name=name, _songPath=path, _creator='')
    pair_name = ('System.Collections.Generic.KeyValuePair`2[[System.String, mscorlib, Version=4.0.0.0, '
                 'Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.Single, mscorlib, '
                 'Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]')
    pair_schema = {'name': pair_name, 'names': ['key', 'value'], 'types': [1, 0],
                   'infos': [None, 11], 'library_id': None}
    pair = Node(pair_schema, {'key': 'Master', 'value': .8}, inline=True)
    info.members['_trackVolumes'].members.update(Version=2, HashSize=3,
        KeyValuePairs=Array([pair], 3, pair_name))
    return info


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


def mp3_duration(data):
    """Bounded MPEG Layer III frame walk; no decoder or external encoder."""
    offset = 0
    if data.startswith(b'ID3'):
        if len(data) < 10 or any(x & 128 for x in data[6:10]):
            raise ValueError('Invalid MP3 ID3 header')
        offset = 10 + sum(x << shift for x, shift in zip(data[6:10], (21, 14, 7, 0)))
        if data[5] & 16: offset += 10
    total = 0.0; frames = 0
    while offset < len(data):
        if data[offset:offset+3] == b'TAG' and len(data)-offset == 128: break
        if data[offset] == 0 and not any(data[offset:]): break  # encoder padding
        if offset + 4 > len(data): raise ValueError('Truncated MP3 header')
        header = int.from_bytes(data[offset:offset+4], 'big')
        version = (header >> 19) & 3; layer = (header >> 17) & 3
        bitrate = (header >> 12) & 15; rate = (header >> 10) & 3
        if header >> 21 != 2047 or version == 1 or layer != 1 or bitrate in (0, 15) or rate == 3:
            raise ValueError('Invalid/unsupported MP3 Layer III frame')
        rates = (44100, 48000, 32000)
        hz = rates[rate] // (1 if version == 3 else 2 if version == 2 else 4)
        table = (0,32,40,48,56,64,80,96,112,128,160,192,224,256,320) if version == 3 else (0,8,16,24,32,40,48,56,64,80,96,112,128,144,160)
        size = (144000 if version == 3 else 72000) * table[bitrate] // hz + ((header >> 9) & 1)
        if offset + size > len(data): raise ValueError('Truncated MP3 frame')
        total += (1152 if version == 3 else 576) / hz
        frames += 1; offset += size
    if frames < 2: raise ValueError('Incomplete MP3 stream')
    return total


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
            safe,problem=_safe_ref(unquote(ref) if isinstance(ref,str) else ref)
            if problem or not safe:raise ValueError('Unsafe/missing audio reference')
            path=_package_file(Path(package),safe)
            suffix=path.suffix.lower()
            if suffix not in ('.mp3','.ogg'):raise ValueError('Only MP3 and OGG Vorbis songs are supported')
            if path.stat().st_size>64*1024*1024:raise ValueError('Audio exceeds 64 MiB')
            data=path.read_bytes();duration=mp3_duration(data) if suffix=='.mp3' else vorbis_duration(data)
            songkey=hashlib.sha256((key+'\0'+str(sound.get('_id',tracks))+'\0').encode()+data).hexdigest()[:20]
            songbase='MyAssets/Audio/Songs/'+folder+'/'+sanitize_name(track_name)
            if songbase+'.rwfile' in files:raise ValueError('Song name conflict; rename source tracks before building: '+track_name)
            song=record(schema,'song');songmeta=record(schema,'song_meta');names(song,track_name);names(songmeta,track_name)
            song.members['_duration']=songmeta.members['_duration']=duration
            audio=record(schema,'audio_track');audio.members.update(_trackName='Master',_originalFile=songkey+suffix,_clipRAW=Array(list(data),0,2),_parentName=track_name)
            sequence(song.members['_tracks'],[audio])
            files[songbase+'.rwfile']=Writer(schema['libraries']).write(song)
            files[songbase+'.rwmeta']=Writer(schema['libraries']).write(songmeta)
            info=music_track_info(schema,track_name,songbase+'.rwmeta')
            content=record(schema,'content');content.members.update(_filePath=songbase+'.rwmeta',_content=info)
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

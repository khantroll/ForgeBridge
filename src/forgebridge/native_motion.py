"""Schema-driven video and decoded-frame native assets; no installed files needed."""
from functools import lru_cache
import io
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from forgebridge.native import Array, Writer
from forgebridge.native_audio import record as schema_record, names
from forgebridge.media_codecs import video_dimensions


@lru_cache(maxsize=1)
def schema():return json.loads(Path(__file__).with_name('motion-schema.json').read_text(encoding='utf-8'))


def record(kind):return schema_record(schema(),kind)


def encode(node):return Writer(schema()['libraries'],max_items=64000000).write(node)


def image(data):
    node=record('video_asset').members['_thumbnail']
    node.members['_packImageRAW']=Array(data,0,2)
    return node


def motion_asset(data,suffix,name):
    losses=[]
    if suffix in ('.webm','.mp4'):
        width,height,codec=video_dimensions(data,suffix)
        thumb=Image.new('RGBA',(96,64),'#263d50');draw=ImageDraw.Draw(thumb);draw.polygon([(35,16),(35,48),(65,32)],fill='white')
        stream=io.BytesIO();thumb.save(stream,'PNG');first=stream.getvalue()
        asset,meta=record('video_asset'),record('video_meta')
        asset.members['_content'].members.update(_rawFile=Array(data,0,2),_originalFile=hashlib.sha256(data).hexdigest()[:20]+suffix)
        preset=record('video_preset')
        names(preset,name)
        for key in preset.members:
            if key.split('+')[-1]=='_tileName':preset.members[key]=name
        variations=meta.members['_variations'].members
        variations['_items'].items=[preset];variations.update(_size=1,_version=1)
        info={'kind':'video','codec':codec,'width':width,'height':height,'bytes_preserved':True}
        losses.append('Video sound is muted; thumbnail is a generated play symbol; autoplay/loop use captured defaults')
    else:
        with Image.open(io.BytesIO(data)) as source:
            width,height=source.size;count=getattr(source,'n_frames',1)
            if source.format not in ('GIF','PNG','WEBP') or count<2:raise ValueError('Not a supported animated image')
            if count>128 or width*height*count>16000000:raise ValueError('Animated frames exceed 128/16-megapixel budget')
            frames=[];durations=[];missing_timing=False
            for index in range(count):
                source.seek(index);frame=source.convert('RGBA');stream=io.BytesIO();frame.save(stream,'PNG');frames.append(stream.getvalue())
                duration=source.info.get('duration')
                valid=isinstance(duration,(int,float)) and 0<duration<=60000
                missing_timing=missing_timing or not valid
                durations.append(float(duration) if valid else 100.)
        asset,meta=record('animated_asset'),record('animated_meta')
        sequence=asset.members['_content'].members
        sequence['_items'].items=[image(frame) for frame in frames];sequence.update(_size=count,_version=count)
        first=frames[0];preset=None;fps=min(60.,1000./(sum(durations)/len(durations)))
        info={'kind':'animated-image','width':width,'height':height,'frames':count,'fps':fps,'source_frame_ms':durations,'bytes_preserved':False}
        if missing_timing:losses.append('Source frame timing absent/invalid; assumes 100 ms per such frame')
        if len(set(durations))!=1 or fps==60:losses.append('Native fixed FPS approximates variable/very short source frame durations')
    for node in (asset,meta):
        names(node,name);node.members['_thumbnail']=image(first)
    return encode(asset),encode(meta),preset,info,losses

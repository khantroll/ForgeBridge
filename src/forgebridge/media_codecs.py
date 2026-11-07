"""Bounded header inspection for captured native video paths; no external decoder."""
import struct


def video_dimensions(data, suffix):
    if suffix == '.webm':
        if data[:4]!=bytes.fromhex('1a45dfa3'):raise ValueError('Invalid WEBM header')
        tracks=[];doctype=None;elements=0
        def vint(pos, limit, identifier=False):
            if pos>=limit or data[pos]==0: raise ValueError('Invalid EBML integer')
            width=next((n for n in range(1,9) if data[pos] & (1 << (8-n))),None)
            if width is None or pos+width>limit or (identifier and width>4): raise ValueError('Truncated EBML integer')
            value=int.from_bytes(data[pos:pos+width],'big')
            if not identifier:value &= (1 << (7*width))-1
            return value,pos+width,width
        def walk(start,end,depth=0,track=None):
            nonlocal doctype,elements
            if depth>8:raise ValueError('Video header nesting limit')
            pos=start
            while pos<end:
                elements+=1
                if elements>10000:raise ValueError('Video header element limit')
                tag,pos,_=vint(pos,end,True);size,pos,width=vint(pos,end)
                stop=end if size==(1 << (7*width))-1 else pos+size
                if stop>end:raise ValueError('Truncated WEBM element')
                if tag==0xAE:
                    entry={};walk(pos,stop,depth+1,entry);tracks.append(entry)
                elif tag in (0x1A45DFA3,0x18538067,0x1654AE6B,0xE0):walk(pos,stop,depth+1,track)
                elif tag==0x4282:doctype=data[pos:stop]
                elif track is not None:
                    if tag==0x86:track['codec']=data[pos:stop]
                    elif tag in (0x83,0xB0,0xBA):track[tag]=int.from_bytes(data[pos:stop],'big')
                pos=stop
        walk(0,len(data))
        videos=[t for t in tracks if t.get(0x83)==1]
        if doctype!=b'webm' or len(videos)!=1 or videos[0].get('codec')!=b'V_VP9':raise ValueError('Only one captured WEBM VP9 video track is supported')
        width,height=videos[0].get(0xB0,0),videos[0].get(0xBA,0);codec='VP9'
    elif suffix == '.mp4':
        if data[4:8]!=b'ftyp':raise ValueError('Invalid MP4 container header')
        found=[];boxes=0
        def walk(start,end,depth=0):
            nonlocal boxes
            if depth>8:raise ValueError('MP4 header nesting limit')
            pos=start
            while pos<end:
                boxes+=1
                if boxes>10000:raise ValueError('MP4 box limit')
                if pos+8>end:raise ValueError('Truncated MP4 box')
                size=int.from_bytes(data[pos:pos+4],'big');kind=data[pos+4:pos+8];header=8
                if size==1:
                    if pos+16>end:raise ValueError('Truncated MP4 extended box')
                    size=int.from_bytes(data[pos+8:pos+16],'big');header=16
                elif size==0:size=end-pos
                if size<header or pos+size>end:raise ValueError('Invalid MP4 box bounds')
                body=pos+header;stop=pos+size
                if kind in (b'moov',b'trak',b'mdia',b'minf',b'stbl'):walk(body,stop,depth+1)
                elif kind==b'stsd':
                    if body+8>stop:raise ValueError('Truncated MP4 sample description')
                    walk(body+8,stop,depth+1)
                elif kind==b'avc1':
                    if body+78>stop or b'avcC' not in data[body+78:stop]:raise ValueError('Missing AVC configuration')
                    found.append(struct.unpack_from('>HH',data,body+24))
                pos=stop
        walk(0,len(data))
        if len(found)!=1:raise ValueError('Only one captured MP4 H.264/AVC video track is supported')
        width,height=found[0];codec='H.264'
    else:raise ValueError('Unsupported video container')
    if width<=0 or height<=0 or width*height>16000000:raise ValueError('Invalid/oversized video dimensions')
    return width,height,codec

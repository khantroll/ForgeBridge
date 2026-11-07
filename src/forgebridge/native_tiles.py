"""Square-based source tile IR to static, animated-image and video map assets."""
import hashlib
import io
import math
from pathlib import Path
from PIL import Image
from urllib.parse import unquote
from forgebridge.scene_media import tile_ir
from forgebridge.native_motion import motion_asset

from forgebridge.native import Writer
from forgebridge.native_map import clone
from forgebridge.nrbf import Reader
from forgebridge.native_scene import background_asset, UNITS_PER_GRID, _set
from forgebridge.scene_records import record, asset_templates
from forgebridge.uvtt import _square_grid, _scene_origin, open_art
from forgebridge.validate import InventoryFatal


def add_tiles(data, scene, package, scope, foundry_data=None):
    reader=Reader(data,max_items=64000000);graph=reader.read();root=clone(reader,graph['root_id'])
    collection=root.members['_tiles'].members
    items=collection['_items'].items[:collection['_size']]
    uid=root.members['_nextUID']
    source=scene.get('tiles',[])
    if not isinstance(source,list) or len(source)>2048:raise ValueError('Invalid/oversized tile collection')
    files={};rows=[];losses=[]
    for index,tile in sorted(enumerate(source),key=lambda pair:pair[1].get('sort',0) if isinstance(pair[1],dict) and type(pair[1].get('sort',0)) in (int,float) else 0):
        texture=tile.get('texture') if isinstance(tile,dict) else None
        ref=(texture.get('src') if isinstance(texture,dict) else None) or (tile.get('img') if isinstance(tile,dict) else None)
        try:
            if not isinstance(tile,dict):raise ValueError('Invalid tile document')
            ir=tile_ir(scene,tile,index)
            if not isinstance(ref,str):raise ValueError('Unsafe/missing tile texture')
            path=open_art(package, unquote(ref), foundry_data)
            if path.stat().st_size>16*1024*1024:raise ValueError('Tile exceeds 16 MiB')
            image=path.read_bytes();suffix=path.suffix.lower()
            if suffix in ('.mov','.m4v','.avi','.mkv'):raise ValueError('Unsupported video container: '+suffix)
            animated=suffix in ('.webm','.mp4')
            if suffix not in ('.webm','.mp4'):
                with Image.open(io.BytesIO(image)) as img:
                    animated=getattr(img,'n_frames',1)>1
                    width,height=img.size
                    if width*height>16000000:raise ValueError('Tile exceeds 16 megapixels')
            preset=None;details={'kind':'static'};media_losses=[]
            if animated:
                asset,meta,preset,details,media_losses=motion_asset(image,suffix,'Animated tile')
                width,height=details['width'],details['height']
            else:asset,meta,_=background_asset(*asset_templates(),image,'Static tile')
            rotation=ir['rotation_clockwise']
            key=hashlib.sha256(image).hexdigest()[:20]
            base='MyAssets/Media/Cartographer/Quick Import/ForgeBridge-'+scope+'/Tile-'+key
            if base+'.rwfile' not in files:
                files[base+'.rwfile']=asset;files[base+'.rwmeta']=meta
            node=record('image')
            if preset is not None:node.members['_tileInfo']=preset
            p=node.members['_tileInfo'].members
            p['_position'].members.update(x=ir['center_squares'][0]*UNITS_PER_GRID,y=-ir['center_squares'][1]*UNITS_PER_GRID)
            p['_scale'].members.update(x=ir['size_squares'][0]*UNITS_PER_GRID*100/width,y=ir['size_squares'][1]*UNITS_PER_GRID*100/height)
            _set(p,_rotation=-rotation,_tilePath=base+'.rwmeta',_name='Static tile' if not animated else 'Animated tile',_tileName='Static tile' if not animated else 'Animated tile',_uID=uid,_sortingOrder=index+1,_groupID=-1,_hidden=bool(tile.get('hidden',False)),_mapLevel=0)
            if details['kind']=='animated-image':
                p['_category'].members['value__']=1
                p['_animation'].members.update(_playing=True,_framesPerSecond=details['fps'],_noOfFrames=float(details['frames']))
            node.members['spriteWidth']=float(max(width,height))
            items.append(node);uid+=1
            rows.append({**details,'media_losses':media_losses,'source_id':tile.get('_id',str(index)),'source':ref,'target':base+'.rwmeta','position':dict(p['_position'].members),'rotation_clockwise':rotation,'hidden':bool(tile.get('hidden',False))})
            losses.append({'grade':'approximate','feature':'static-tile' if not animated else 'animated-tile','source_id':tile.get('_id'),'details':media_losses,'summary':'Rectangle, position, rotation and hidden mapped; source alpha/tint, texture offsets/scale, occlusion, elevation/levels and behavior require review; Toolkit display unverified'})
        except (OSError,ValueError,InventoryFatal) as exc:
            losses.append({'grade':'manual','feature':'tile','source_id':tile.get('_id') if isinstance(tile,dict) else None,'source':ref,'summary':str(exc)})
    collection['_items'].items=items;collection.update(_size=len(items),_version=collection['_version']+len(rows));root.members['_nextUID']=uid
    return Writer(reader.libraries,max_items=64000000).write(root),files,{'count':len(rows),'static_count':sum(r['kind']=='static' for r in rows),'animated_count':sum(r['kind']!='static' for r in rows),'tiles':rows,'losses':losses}

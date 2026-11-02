"""Static source tile placements on generated maps; animated media is manual."""
import hashlib
import io
import math
from pathlib import Path
from PIL import Image

from forgebridge.native import Writer
from forgebridge.native_map import clone
from forgebridge.nrbf import Reader
from forgebridge.native_scene import background_asset, UNITS_PER_GRID, _set
from forgebridge.scene_records import record, asset_templates
from forgebridge.uvtt import _square_grid, _scene_origin, _safe_ref, _package_file
from forgebridge.validate import InventoryFatal


def add_tiles(data, scene, package, scope):
    reader=Reader(data);graph=reader.read();root=clone(reader,graph['root_id'])
    collection=root.members['_tiles'].members
    items=collection['_items'].items[:collection['_size']]
    uid=root.members['_nextUID'];size=_square_grid(scene);origin=_scene_origin(scene,size,[])
    source=scene.get('tiles',[])
    if not isinstance(source,list) or len(source)>2048:raise ValueError('Invalid/oversized tile collection')
    files={};rows=[];losses=[]
    for index,tile in sorted(enumerate(source),key=lambda pair:pair[1].get('sort',0)):
        ref=tile.get('texture',{}).get('src') or tile.get('img')
        try:
            safe,problem=_safe_ref(ref)
            if problem or not safe:raise ValueError('Unsafe/missing tile texture')
            path=_package_file(Path(package),safe)
            if path.suffix.lower() in ('.webm','.mp4','.gif','.m4v','.mov'):raise ValueError('Animated/video tile remains manual')
            if path.stat().st_size>32*1024*1024:raise ValueError('Tile exceeds 32 MiB')
            image=path.read_bytes()
            with Image.open(io.BytesIO(image)) as img:
                if getattr(img,'n_frames',1)!=1:raise ValueError('Animated tile remains manual')
                width,height=img.size
                if width*height>16000000:raise ValueError('Tile exceeds 16 megapixels')
            vals=[tile.get(k) for k in ('x','y','width','height')]
            rotation=tile.get('rotation',0)
            if not all(type(v) in (int,float) and math.isfinite(v) for v in vals+[rotation]) or min(vals[2:])<=0:raise ValueError('Unsupported tile geometry')
            x,y,w,h=vals
            key=hashlib.sha256(image).hexdigest()[:20]
            base='MyAssets/Media/Cartographer/Quick Import/ForgeBridge-'+scope+'/Tile-'+key
            if base+'.rwfile' not in files:
                asset,meta,_=background_asset(*asset_templates(),image,'Static tile')
                files[base+'.rwfile']=asset;files[base+'.rwmeta']=meta
            node=record('image');p=node.members['_tileInfo'].members
            p['_position'].members.update(x=(x+w/2-origin[0])/size*UNITS_PER_GRID,y=-(y+h/2-origin[1])/size*UNITS_PER_GRID)
            p['_scale'].members.update(x=w/size*UNITS_PER_GRID*100/width,y=h/size*UNITS_PER_GRID*100/height)
            _set(p,_rotation=-rotation,_tilePath=base+'.rwmeta',_name='Static tile',_tileName='Static tile',_uID=uid,_sortingOrder=index+1,_groupID=-1,_hidden=bool(tile.get('hidden',False)),_mapLevel=0)
            node.members['spriteWidth']=float(max(width,height))
            items.append(node);uid+=1
            rows.append({'source_id':tile.get('_id',str(index)),'source':ref,'target':base+'.rwmeta','position':dict(p['_position'].members),'rotation_clockwise':rotation,'hidden':bool(tile.get('hidden',False))})
            losses.append({'grade':'approximate','feature':'static-tile','source_id':tile.get('_id'),'summary':'Rectangle, position, rotation and hidden mapped; source alpha/tint, texture offsets/scale, occlusion, elevation/levels and behavior require review; Toolkit display unverified'})
        except (OSError,ValueError,InventoryFatal) as exc:
            losses.append({'grade':'manual','feature':'tile','source_id':tile.get('_id'),'source':ref,'summary':str(exc)})
    collection['_items'].items=items;collection.update(_size=len(items),_version=collection['_version']+len(rows));root.members['_nextUID']=uid
    return Writer(reader.libraries).write(root),files,{'count':len(rows),'tiles':rows,'losses':losses}

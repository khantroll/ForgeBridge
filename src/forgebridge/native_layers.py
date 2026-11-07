"""Grid-space static layer IR to captured native image presets; no source parser."""
import hashlib,io
from PIL import Image
from forgebridge.native import Writer
from forgebridge.native_map import clone
from forgebridge.nrbf import Reader
from forgebridge.scene_records import record,asset_templates
from forgebridge.native_scene import background_asset,_set

def add_layers(data,records,scope,background_target,background_pixels):
    r=Reader(data,max_items=64000000);g=r.read();root=clone(r,g['root_id'])
    seq=root.members['_tiles'].members;items=seq['_items'].items[:seq['_size']];uid=root.members['_nextUID']
    files={};rows=[];losses=[]
    backgrounds=[n for n in items if n.members['_tileInfo'].members.get('_tilePath')==background_target]
    if len(backgrounds)!=1:raise ValueError('Expected exactly one generated background')
    for row in records:
        try:
            if row['base']:node=backgrounds[0];width,height=background_pixels
            else:
                if len(row['image'])>16*1024*1024:raise ValueError('Layer exceeds 16 MiB')
                with Image.open(io.BytesIO(row['image'])) as img:
                    if getattr(img,'n_frames',1)>1:raise ValueError('Animated FG layer unsupported by static bitmap adapter')
                    width,height=img.size
                if width*height>16000000:raise ValueError('Overlay layer exceeds 16 megapixels')
                asset,meta,_=background_asset(*asset_templates(),row['image'],'FG bitmap layer')
                base='MyAssets/Media/Cartographer/Quick Import/ForgeBridge-'+scope+'/Layer-'+hashlib.sha256(row['image']).hexdigest()[:20]
                if base+'.rwfile' not in files:
                    if sum(map(len,files.values()))+len(asset)+len(meta)>256*1024*1024:raise ValueError('FG layer dependency output exceeds 256 MiB')
                    files[base+'.rwfile']=asset;files[base+'.rwmeta']=meta
                node=record('image');items.append(node)
                _set(node.members['_tileInfo'].members,_tilePath=base+'.rwmeta',_uID=uid,_groupID=-1,_mapLevel=0);uid+=1
                node.members['spriteWidth']=float(max(width,height))
            p=node.members['_tileInfo'].members
            p['_position'].members.update(x=row['center_squares'][0]*2.56,y=-row['center_squares'][1]*2.56)
            p['_scale'].members.update(x=row['size_squares'][0]*2.56*100/width,y=row['size_squares'][1]*2.56*100/height)
            _set(p,_name=row['name'],_tileName='FG Bitmap Layer',_rotation=row['rotation_ccw'],_hidden=row['hidden'],_sortingOrder=row['order'])
            rows.append({k:v for k,v in row.items() if k!='image'}|{'native_uid':p['_uID'],'native_target':p['_tilePath']})
        except (ValueError,OSError) as exc:losses.append(dict(grade='manual',feature='fg-bitmap-layer',source_id=row['source_id'],summary=str(exc)))
    seq['_items'].items=items;seq.update(_size=len(items),_version=seq['_version']+len(rows));root.members['_nextUID']=uid
    return Writer(r.libraries,max_items=64000000).write(root),files,{'layers':rows,'losses':losses,'runtime_validation':'not performed'}

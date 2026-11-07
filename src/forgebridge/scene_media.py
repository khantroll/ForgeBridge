"""Foundry scene-media adapter to square-based display IR."""
import math
from forgebridge.uvtt import _square_grid, _scene_origin


def finite(value):return type(value) in (int,float) and math.isfinite(value)


def point(scene,x,y):
    if not all(finite(v) for v in (x,y)):raise ValueError('Non-finite source position')
    grid=_square_grid(scene);origin=_scene_origin(scene,grid,[])
    return ((x-origin[0])/grid,(y-origin[1])/grid)


def tile_ir(scene,tile,index):
    values=[tile.get(k) for k in ('x','y','width','height')];rotation=tile.get('rotation',0)
    if not all(finite(v) for v in values+[rotation]) or min(values[2:])<=0:raise ValueError('Unsupported tile geometry')
    x,y,w,h=values;grid=_square_grid(scene)
    texture=tile.get('texture');ref=texture.get('src') if isinstance(texture,dict) else None
    return {'source_id':tile.get('_id',str(index)),'texture':ref or tile.get('img'),
            'center_squares':point(scene,x+w/2,y+h/2),'size_squares':(w/grid,h/grid),
            'rotation_clockwise':rotation,'hidden':bool(tile.get('hidden',False))}


def sound_ir(scene,sound,index):
    grid=scene.get('grid',{});distance=grid.get('distance') if isinstance(grid,dict) else None
    radius=sound.get('radius');volume=sound.get('volume',1.)
    if not finite(distance) or distance<=0:raise ValueError('Ambient radius needs a positive source grid distance')
    if not finite(radius) or radius<=0:raise ValueError('Ambient sound needs a positive radius')
    if not finite(volume) or not 0<=volume<=1:raise ValueError('Ambient volume must be between 0 and 1')
    return {'source_id':sound.get('_id',str(index)),'name':sound.get('name') or 'Ambient sound '+str(index+1),
            'source':sound.get('path'),'position_squares':point(scene,sound.get('x'),sound.get('y')),
            'radius_squares':radius/distance,'source_radius':radius,'source_grid_distance':distance,
            'volume':volume,'hidden':bool(sound.get('hidden',False)),'easing':bool(sound.get('easing',True)),
            'walls':bool(sound.get('walls',False))}

"""FG bitmap layer source adapter to grid-space image IR.

Bounded scalar/API-style fields only. Opaque transform tuples/parent groups are
reported rather than guessed. Image.addLayer documents w/h as grid units.
"""
import math
from forgebridge.fantasy_grounds import _text,_floats,_Frame,image_size

def layer_ir(source,entry,result):
    layers=entry['_node'].findall('.//layers/layer');records=[];losses=[];base=False
    if len(layers)>256:raise ValueError('FG layer count exceeds 256')
    nested={id(child) for parent in layers for child in parent.findall('.//layers/layer')}
    frame=_Frame(*result['size_px'],result['pixels_per_square'])
    def loss(i,message,**fields):losses.append(dict(grade='manual',feature='fg-bitmap-layer',source_id=str(i),summary=message,**fields))
    for i,node in enumerate(layers):
        ref=_text(node,'bitmap') or _text(node,'asset');identity=_text(node,'id') or str(i)
        if not ref:
            loss(identity,'Non-bitmap layer not represented',layer_type=_text(node,'type'),fields=[c.tag for c in node]);continue
        is_base=not base and ref==entry['bitmap']
        if is_base:base=True
        try:
            if id(node) in nested:raise ValueError('Nested layer/group coordinates unsupported; no implicit flattening')
            if node.find('transform') is not None:raise ValueError('Opaque persisted transform tuple has no calibrated field ordering; not guessed')
            if (_text(node,'parentid') or '0') not in ('0','-1'):raise ValueError('Nested parent/group transform unsupported')
            width,height,data=image_size(source,ref)
            pos=_floats(_text(node,'position') or ((_text(node,'x') or '0')+','+(_text(node,'y') or '0')),'layer position')
            scale=_floats(_text(node,'scale') or '1,1','layer scale',even=False)
            if len(scale)==1:scale*=2
            if len(pos)!=2 or len(scale)!=2 or min(scale)<=0:raise ValueError('Layer position/positive scale malformed')
            if (_text(node,'w') or _text(node,'h')) and scale!=[1.,1.]:raise ValueError('Ambiguous simultaneous size and scale')
            angle=float(_text(node,'angle') or _text(node,'rotation') or '0')
            if not math.isfinite(angle):raise ValueError('Nonfinite layer angle')
            w=float(_text(node,'w')) if _text(node,'w') else width/result['pixels_per_square']*scale[0]
            h=float(_text(node,'h')) if _text(node,'h') else height/result['pixels_per_square']*scale[1]
            if not all(math.isfinite(v) and 0<v<=100000 for v in (w,h)):raise ValueError('Invalid layer dimensions')
            center=frame.point(*pos)
            records.append(dict(source_id=identity,source=ref,image=data,base=is_base,
                center_squares=[center['x'],center['y']],size_squares=[w,h],rotation_ccw=angle,
                hidden=any(node.find(k) is not None and (_text(node,k) is None or _text(node,k).lower() in ('1','on','true')) for k in ('invisible','gmonly')),order=i,
                name=_text(node,'name') or 'FG bitmap layer'))
            unsupported={c.tag:c.text for c in node if c.tag not in ('id','name','type','bitmap','asset','parentid','position','x','y','scale','angle','rotation','w','h','invisible','gmonly','locked','occluders','lights','tokens','shortcuts')}
            if unsupported:loss(identity,'Layer tint/opacity/blend/mask or unknown fields require manual review',fields=unsupported)
            losses.append(dict(grade='approximate',feature='fg-layer-transform',source_id=identity,
                summary='Bitmap center/scale/angle mapped in existing centre-origin y-up pixel frame; w/h are grid units. Angle direction and relative edit-layer order unverified in Toolkit. Original input unchanged; pixels encoded through the existing native image writer.'))
            if (pos!=[0.,0.] or scale!=[1.,1.] or angle) and any(node.find(k) is not None for k in ('occluders','lights','tokens','shortcuts')):
                loss(identity,'Bitmap transform does not calibrate attached geometry/placement coordinate space; existing map-space geometry retained for review')
        except (ValueError,OSError) as exc:loss(identity,str(exc),source=ref,background_retained_untransformed=is_base)
    if len(records)>1:loss('map','Browser thumbnail remains the first bitmap; transformed canvas extents/preview composite are not rebuilt')
    return records,losses

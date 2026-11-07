"""FG image shortcuts and placed tokens to source-neutral native placement IR.

The bounded FGU XML slice uses the existing centre-origin, y-up image frame.
Other dialect fields remain losses; real placement calibration is runtime pending.
"""
import math
from pathlib import Path
from forgebridge.fantasy_grounds import _Frame, ModuleError
from forgebridge.fg_campaign import _stage_image, _field
from forgebridge.token_ir import Token


def placements(source, entry, result, links, documents, staged):
    frame = _Frame(*result['size_px'], result['pixels_per_square'])
    markers, tokens, losses, bindings = [], [], [], []
    names = {r['target']:r['name'] for r in documents}
    def loss(feature, message, identity, **details):
        losses.append(dict(grade='manual', feature=feature, summary=message, source_id=identity, **details))
    def point(node):
        if node.find('position') is not None:
            values = (node.findtext('position') or '').split(',')
        else: values = [node.findtext('x'), node.findtext('y')]
        if len(values) != 2: raise ValueError('Expected two image coordinates')
        xy = [float(v) for v in values]
        if not all(math.isfinite(v) for v in xy): raise ValueError('Non-finite image coordinate')
        return frame.point(*xy)
    nodes = [entry['_node']] + entry['_node'].findall('./layers/layer')
    pin_nodes = [n for parent in nodes for n in parent.findall('./shortcuts/shortcut')]
    token_nodes = [n for parent in nodes for n in parent.findall('./tokens/token')]
    if len(pin_nodes)>2048 or len(token_nodes)>256: raise ModuleError('Map placement count exceeds limits')
    seen = set()
    for index, node in enumerate(pin_nodes):
        identity = entry['record']+'.shortcut.'+(node.findtext('id') or str(index))
        ref = node.findtext('recordname') or node.findtext('link/recordname')
        target = links.get(ref)
        try:
            if identity in seen: raise ValueError('Duplicate shortcut identity')
            seen.add(identity)
            if not target: raise ValueError('Pin target not converted or belongs to another module')
            markers.append(dict(source_id=identity, title=_field(node,'name') or names.get(target) or ref,
                                target=target, grid_position=point(node)))
        except (ValueError,TypeError) as exc: loss('pin',str(exc),identity,record=ref)
    for index,node in enumerate(token_nodes):
        identity = entry['record']+'.token.'+(node.findtext('id') or str(index))
        try:
            if identity in seen: raise ValueError('Duplicate token identity')
            seen.add(identity)
            pos = point(node)
            ref = node.findtext('recordname') or node.findtext('link/recordname')
            npc = next((r for r in documents if r['target']==links.get(ref) and r['kind']=='Actor'),None)
            texture = node.findtext('prototype') or node.findtext('token') or node.findtext('bitmap')
            if not texture: raise ValueError('Placed token has no stored portrait/prototype')
            texture = _stage_image(source,texture,staged,losses,identity)
            if not texture: raise ValueError('Token texture unavailable; no placeholder invented')
            size = float(node.findtext('size') or '1')
            scale = float(node.findtext('scale') or '1')
            angle = float(node.findtext('rotation') or float(node.findtext('orientation') or '0')*45)
            if not all(math.isfinite(v) for v in (size,scale,angle)) or not 0<size<=32 or not 0<scale<=1:
                raise ValueError('Only positive square footprints <=32 and texture scale <=1 supported')
            visibility = (node.findtext('visibility') or 'visible').lower()
            if visibility not in ('0','1','on','off','visible','hidden'): raise ValueError('Unsupported token visibility')
            hidden = visibility in ('0','off','hidden')
            tokens.append(Token(identity,_field(node,'name') or (npc or {}).get('name') or 'FG token',texture,
                (pos['x'],pos['y']),(size,size),(scale,scale),angle,hidden,tuple(child.tag for child in node)))
            if node.find('size') is None:
                losses.append(dict(grade='approximate',feature='token-size',source_id=identity,
                    summary='No stored square footprint: uses one square; native sizing requires review'))
            if ref:
                bindings.append(dict(source_id=identity,record=ref,npc_note=links.get(ref)))
                loss('token-npc-link','Portrait preserved; native linked-text changes tokens into note pins. Open the separate NPC note by name; automatic binding not emitted',identity,record=ref,target=links.get(ref))
        except (ValueError,TypeError) as exc: loss('token',str(exc),identity)
    if markers or tokens:
        losses.append(dict(grade='approximate',feature='placement-frame',source_id=entry['record'],
            summary='FGU centre-origin y-up frame mapped through source pixels/grid to native 2.56 units/square. Shortcut/token coordinate dialect and visual alignment need Toolkit review; layer transforms and combat state not converted'))
    return markers,tokens,losses,bindings


def add_placements(map_data, source, entry, result, campaign, *, name, scope, staged_root):
    from forgebridge.scene_records import control_files
    from forgebridge.native_map import insert_markers
    from forgebridge.native_tokens import compile_ir_tokens
    staged = {}
    markers,tokens,losses,bindings = placements(source,entry,result,campaign['links'],campaign['documents'],staged)
    root=Path(staged_root)
    for rel,data in staged.items():
        target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    marker,token,_=control_files();control='MyAssets/Maps/_ForgeBridgeSchemaControl.rwmap'
    rows=[]
    if markers:
        map_data,rows=insert_markers(map_data,markers,name=name,units_per_grid=2.56,
            template_name='ForgeBridge Control',template_data=marker[control])
    files={};converted=[];rejected=[]
    if tokens:
        map_data,files,converted,rejected=compile_ir_tokens(map_data,tokens,root,token,control,
            name=name,units_per_grid=2.56,control_units_per_grid=2.56,
            control_name='ForgeBridge Control',namespace=scope)
    # Discard unreachable control strings retained by the shared byte-patching writer.
    from forgebridge.nrbf import Reader
    from forgebridge.native import Writer
    from forgebridge.native_map import clone
    for path,data in list(files.items()):
        if path.startswith('MyAssets/Encyclopedia/Notes/ForgeBridgeTokens/'):
            reader=Reader(data);graph=reader.read()
            files[path]=Writer(reader.libraries).write(clone(reader,graph['root_id']))
    losses += [dict(grade='manual',feature='token',summary=r['reason'],source_id=r['source_id']) for r in rejected]
    return map_data,files,dict(markers=rows,tokens=converted,rejected_tokens=rejected,bindings=bindings,losses=losses)

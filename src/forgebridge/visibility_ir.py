"""Foundry/FG visibility and light-effect adapters; inert source data only."""
import math
from forgebridge.uvtt import _square_grid, _scene_origin, _lights_to_uvtt

FLICKER={'torch','flame','flames','flicker','fire','fairy','candle','campfire'}
BLINK={'pulse','pulsing','blink','blinking'}


def number(v):return type(v) in (int,float) and math.isfinite(v)
def loss(rows,grade,feature,summary,**details):rows.append(dict(grade=grade,feature=feature,summary=summary,**details))


def animation(config, losses, identity):
    config=config if isinstance(config,dict) else {}
    kind=config.get('type') or ''
    if not kind:return None
    if not isinstance(kind,str):
        loss(losses,'manual','light-animation','Invalid animation type',source_id=identity);return None
    kind=kind.lower()
    effect='flicker' if kind in FLICKER else 'blink' if kind in BLINK else None
    if effect is None:
        loss(losses,'unsupported','light-animation','No observed native mapping for '+kind,source_id=identity,source_animation=config);return None
    intensity=config.get('intensity');scaled=None
    if effect=='flicker' and intensity is not None:
        if number(intensity) and 0<=intensity<=10:scaled=intensity/10
        else:loss(losses,'manual','animation-intensity','Expected 0–10; captured native default retained',source_id=identity)
    loss(losses,'approximate','light-animation','Captured '+effect+' effect; flicker intensity /10 where stored; source speed/reverse/color/phase are not equivalent. Blink uses captured timing defaults',source_id=identity,source_animation=config)
    return dict(kind=effect,intensity=scaled)


def foundry_visibility(scene, actors=()):
    losses=[];size=_square_grid(scene);origin=_scene_origin(scene,size,[])
    grid=scene.get('grid',{});distance=grid.get('distance')
    fog=scene.get('fog') if isinstance(scene.get('fog'),dict) else {}
    enabled=scene.get('tokenVision');persists=fog.get('exploration',scene.get('fogExploration'))
    if type(enabled) is not bool: enabled=None;loss(losses,'manual','fog','No explicit scene tokenVision; native fog defaults retained')
    if type(persists) is not bool: persists=None;loss(losses,'manual','fog-persistence','No explicit exploration flag; native persistence default retained')
    loss(losses,'approximate','fog','Configuration only: Dynamic mode; exploration flag maps to native persistence. Saved Foundry explored masks, per-user vision, overlays, fog colors and global illumination are not migrated; Toolkit Simulate darkness is not a map field')
    darkness=scene.get('environment',{}).get('darknessLevel',scene.get('darkness')) if isinstance(scene.get('environment',{}),dict) else scene.get('darkness')
    if darkness is not None:loss(losses,'manual','scene-darkness','Custom light-intensity direction was not exercised by the capture; native custom intensity unchanged',source_value=darkness)
    lights=[];geometry_index=0
    for i,source in enumerate(scene.get('lights',[])):
        if not isinstance(source,dict):continue
        identity=source.get('_id',str(i));config=source.get('config') if isinstance(source.get('config'),dict) else {}
        emitted=_lights_to_uvtt([source],scene,size,[],origin)
        valid=emitted and number(emitted[0].get('range')) and emitted[0]['range']>0
        index=geometry_index if valid else None
        if valid:geometry_index+=1
        radii=[v for v in (config.get('dim'),config.get('bright')) if number(v)]
        negative=config.get('negative') is True or source.get('negative') is True or any(v<0 for v in radii) or (number(config.get('luminosity')) and config['luminosity']<0)
        point=None;radius=None
        if not valid:
            if not negative:continue
            if not emitted or not number(distance) or distance<=0 or not radii or max(abs(v) for v in radii)<=0:
                loss(losses,'manual','darkness-light','No safe positive radius/position/grid conversion for negative source',source_id=identity);continue
            point=emitted[0]['position'];radius=max(abs(v) for v in radii)/distance
        lights.append(dict(source_id=identity,index=index,position=point,radius=radius,darkness=negative,
            reveals=source.get('vision') is True,enabled=source.get('hidden') is not True,
            effect=animation(config.get('animation'),losses,identity)))
        if negative:loss(losses,'approximate','darkness-light','Native darkness flag mapped; Foundry priority, light/vision suppression and shader equivalence need runtime review',source_id=identity)
        if source.get('vision') is True:loss(losses,'approximate','light-reveals','Foundry AmbientLight vision source maps to native visibleThroughFog; player sharing/occlusion equivalence unverified',source_id=identity)
    actor_ids={}
    for actor in actors:
        if isinstance(actor,dict):actor_ids.setdefault(actor.get('_id',actor.get('id')),[]).append(actor)
    tokens=[];excluded=[]
    for t in scene.get('tokens',[]):
        if not isinstance(t,dict):continue
        identity='Scene.'+str(scene.get('_id'))+'.Token.'+str(t.get('_id'))
        sight=t.get('sight') if isinstance(t.get('sight'),dict) else {}
        candidates=actor_ids.get(t.get('actorId'),[])
        actor=candidates[0] if len(candidates)==1 else t.get('actorData',{})
        if not isinstance(actor,dict):actor={}
        owners=t.get('ownership',actor.get('ownership',{}))
        pc=actor.get('type')=='character' and isinstance(owners,dict) and any(number(v) and v==3 for v in owners.values())
        if not pc or sight.get('enabled') is not True or enabled is not True:
            excluded.append(dict(source_id=identity,name=t.get('name'),reason='NPC/unknown ownership, disabled sight, or scene token vision off'));continue
        mode=sight.get('visionMode') or 'basic';radius=sight.get('range')
        if mode not in ('basic','darkvision'):
            loss(losses,'unsupported','token-vision','No observed native mapping for vision mode '+str(mode),source_id=identity);continue
        if mode=='darkvision' and (not number(radius) or radius<=0):
            radius=actor.get('system',{}).get('attributes',{}).get('senses',{}).get('darkvision')
        if not number(radius) or radius<=0 or not number(distance) or distance<=0:
            loss(losses,'manual','token-vision','No positive finite sight radius and grid distance; zero/unlimited sight not guessed',source_id=identity);continue
        tokens.append(dict(source_id=identity,name=t.get('name'),radius=radius/distance,intensity=.15 if mode=='darkvision' else 1.,mode=mode))
        loss(losses,'approximate','token-vision','Player-owned character sight becomes a shared revealing token light; darkvision uses intensity 0.15, not true desaturation/nightvision. Character OWNER level 3 is used; export user roles may be absent. Per-user permissions, detection modes, cones and vision effects are not reproduced',source_id=identity,mode=mode)
    return dict(source='foundry',fog=dict(enabled=enabled,persists=persists),lights=lights,tokens=tokens,excluded_tokens=excluded,losses=losses)


def fg_visibility(source,entry,result):
    from forgebridge.fantasy_grounds import _metadata_nodes,_all,_first,_floats,_text,_Frame
    nodes,_=_metadata_nodes(source,entry);losses=[];lights=[];index=0
    def flag(value):return True if str(value).lower() in ('on','true','1') else False if str(value).lower() in ('off','false','0') else None
    enabled=flag(_first(nodes,'los'))
    if enabled is None and any(n.findall('./occluders/occluder') for n in nodes):
        enabled=True;loss(losses,'approximate','fg-los','Stored occluders enable native Dynamic fog; saved FG LOS enable state may differ')
    persists=flag(_first(nodes,'fogexploration'))
    frame=_Frame(*result['size_px'],result['pixels_per_square'])
    for i,node in enumerate(_all(nodes,'./lights/light')):
        ranges=_floats(_text(node,'range') or '', 'FG light range',even=False)[::2]
        radius=max(ranges) if ranges else 0
        native_index=index if radius>0 else None
        negative=bool(ranges and any(r<0 for r in ranges)) or _text(node,'type')=='darkness'
        if radius<=0 and not negative:continue
        pos=_floats(_text(node,'position'),'FG light position')
        if len(pos)!=2:continue
        if radius>0:index+=1
        anim=node.find('animation');kind=(anim.get('type') or anim.findtext('type') or anim.text or '').strip() if anim is not None else ''
        if not kind and node.find('flicker') is not None and (not (node.findtext('flicker') or '').strip() or flag(node.findtext('flicker')) is True):kind='flicker'
        if not kind and node.find('blink') is not None and (not (node.findtext('blink') or '').strip() or flag(node.findtext('blink')) is True):kind='blink'
        lights.append(dict(source_id='light.'+str(i),index=native_index,position=frame.point(*pos) if native_index is None else None,
            radius=max(abs(v) for v in ranges) if native_index is None else None,darkness=negative,
            reveals=flag(_text(node,'vision')) is True,enabled=node.find('on') is not None,
            effect=animation({'type':kind},losses,'light.'+str(i))))
    tokens=[]
    parents = [entry['_node']] + entry['_node'].findall('./layers/layer')
    for i,node in enumerate([t for parent in parents for t in parent.findall('./tokens/token')]):
        ref=node.findtext('recordname') or node.findtext('link/recordname') or ''
        if not ref.startswith('charsheet.'):continue # NPCs/friendly NPCs are never vision sources.
        if flag(node.findtext('sight/enabled')) is not True:continue
        if node.findtext('sight/units')!='squares':
            loss(losses,'manual','fg-token-vision','Stored PC sight range units are not explicitly squares; no campaign-distance guess',source_id=ref);continue
        try:radius=float(node.findtext('sight/range'))
        except (ValueError,TypeError):radius=0
        if not math.isfinite(radius) or radius<=0:
            loss(losses,'manual','fg-token-vision','PC sight lacks a positive stored range in squares',source_id=ref);continue
        mode=node.findtext('sight/visionMode') or 'basic'
        if mode not in ('basic','darkvision'):
            loss(losses,'unsupported','fg-token-vision','Unsupported FG vision mode',source_id=ref);continue
        identity=entry['record']+'.token.'+(node.findtext('id') or str(i))
        tokens.append(dict(source_id=identity,name=node.findtext('name'),radius=radius,intensity=.15 if mode=='darkvision' else 1.,mode=mode))
    loss(losses,'approximate','fg-vision','Only stored LOS/PC sight/light animation flags mapped. FG token placement must exist to attach vision; missing ownership/range, masks, exploration history, ambient/darkness and effects stay manual')
    return dict(source='fantasy_grounds',fog=dict(enabled=enabled,persists=persists),lights=lights,tokens=tokens,excluded_tokens=[],losses=losses)

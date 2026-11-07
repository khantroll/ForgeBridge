"""Apply source-neutral fog/light IR using captured native member definitions.

Preserves original map bytes except selected fields; never edits installed files.
New darkness records use the existing schema light factory. Saved masks are opaque.
"""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from forgebridge.native import Node,Array
from forgebridge.native_map import AppendWriter,Reference,clone,patch_stream
from forgebridge.nrbf import Reader
from forgebridge.scene_records import record
from forgebridge.native_scene import _set


@lru_cache(maxsize=1)
def schema():return json.loads(Path(__file__).with_name('fog-light-schema.json').read_text(encoding='utf-8'))


def effect_node(kind,intensity=None):
    data=schema();name={'flicker':'ObjectEffectLightFlicker','blink':'ObjectEffectLightBlink'}[kind]
    values=deepcopy(data['defaults'][name])
    if kind=='flicker' and intensity is not None:values['_intensity']=intensity
    return Node(deepcopy(data['classes'][name]),values,data['inline'][name])


def token_target(namespace,identity):
    key=hashlib.sha256((namespace+'\0'+identity).encode('utf-8')).hexdigest()[:24]
    return 'MyAssets/Encyclopedia/Notes/ForgeBridgeTokens/'+key+'.rwmeta'


def apply_visibility(data, ir, *, namespace, units_per_grid=2.56, origin=(0.,0.)):
    import math
    if not math.isfinite(units_per_grid) or units_per_grid<=0 or len(origin)!=2 or not all(math.isfinite(v) for v in origin):raise ValueError('Invalid visibility calibration')
    r=Reader(data,max_items=64000000);graph=r.read();objects=r.objects;rootid=graph['root_id'];root=objects[rootid]['members'];captured=schema()
    if r.libraries!={int(k):v for k,v in captured['libraries'].items()}:raise ValueError('Visibility schema library mismatch')
    def val(v):return objects[v['ref']] if isinstance(v,dict) and 'ref' in v else v
    def oid(v):return v['ref']
    def bare(k):return k.split('+')[-1]
    tilesid=oid(root['_tiles']);tiles=objects[tilesid]['members'];arrayid=oid(tiles['_items']);active=objects[arrayid]['items'][:tiles['_size']]
    presets=[oid(val(v)['members']['_tileInfo']) for v in active]
    lights=[i for i in presets if objects[i].get('class')=='ArkenTilePresetBase' and val(objects[i]['members'].get('_tileName'))=='Light Source']
    tokens={val(objects[i]['members'].get('_contentBasePath')):i for i in presets if objects[i].get('class')=='ArkenTilePresetContentLink'}
    writer=AppendWriter(r);patches=[];losses=list(ir['losses']);report=dict(source=ir['source'],fog={},lights=[],tokens=[],excluded_tokens=ir.get('excluded_tokens',[]),losses=losses,runtime_validation='not performed')
    def field(objid,key,value):
        metadata=r.object_metadata[objid];index=metadata['names'].index(key)
        if metadata['types'][index]==0:
            old=writer.out;writer.out=bytearray();writer.primitive(metadata['infos'][index],value);encoded=bytes(writer.out);writer.out=old
        else:encoded=writer.encoded(value)
        patches.append((*r.member_spans[objid][key],encoded))
    for key in ('_fogEnabled','_fogMode','_fogPersists','_fogColour'):
        m=r.object_metadata[rootid];j=m['names'].index(key);expected=captured['map_fields'][key]
        if (m['types'][j],m['infos'][j])!=(expected['type'],expected['info']):raise ValueError('Captured fog schema mismatch: '+key)
    fog=ir['fog'];enabled=fog.get('enabled')
    if enabled is not None:
        field(rootid,'_fogEnabled',enabled)
        modeid=oid(root['_fogMode'])
        if r.object_metadata[modeid]!=captured['classes']['FogOfWarOptions+FogMode']:raise ValueError('Fog enum mismatch')
        field(modeid,'value__',2)
        if enabled and val(root['_fogColour']) is None:
            colour=Node(deepcopy(captured['classes']['SVector3']),dict(x=0.,y=0.,z=0.),captured['inline']['SVector3'])
            field(rootid,'_fogColour',colour)
    if fog.get('persists') is not None:field(rootid,'_fogPersists',fog['persists'])
    report['fog']=dict(enabled=enabled,mode=2 if enabled is not None else 'unchanged',persists=fog.get('persists'),historical_masks_migrated=False)
    def lighting(node,row):
        if node.schema!=captured['classes']['TileLightingProperties']:raise ValueError('Captured lighting schema mismatch')
        m=node.members
        m.update(_hasLight=row.get('enabled',True),_visibleThroughFog=bool(row.get('reveals')) and not row.get('darkness',False) and row.get('enabled',True),_darkness=bool(row.get('darkness')), _flicker=bool(row.get('effect') and row['effect']['kind']=='flicker'))
        if row.get('intensity') is not None:m['_lightIntensity']=float(row['intensity'])
        if row.get('rgb') is not None:
            if len(row['rgb'])!=3 or not all(math.isfinite(v) and 0<=v<=1 for v in row['rgb']):raise ValueError('Invalid light RGB')
            m.update(zip(('_lightR','_lightG','_lightB'),row['rgb']))
        if row.get('radius') is not None:
            radius=row['radius']*units_per_grid
            if not math.isfinite(radius) or radius<=0:raise ValueError('Invalid calibrated light radius')
            seq=m['_lightRadius'].members;seq['_items'].items[0]=float(radius);seq['_size']=1;seq['_version']+=1
        return node
    def effects(node,row):
        m=node.members;items=m['_items'].items[:m['_size']]
        items=[v for v in items if v is not None and v.schema['name'] not in ('ObjectEffectLightFlicker','ObjectEffectLightBlink')]
        if row.get('effect'):items.append(effect_node(row['effect']['kind'],row['effect'].get('intensity')))
        m['_items'].items=items;m['_size']=len(items);m['_version']+=1
        return node
    def modify(presetid,row):
        p=objects[presetid]['members'];lit=lighting(clone(r,oid(p['_lighting'])),row);eff=effects(clone(r,oid(p['_effectsNew'])),row)
        for key in p:
            if bare(key)=='_lighting':field(presetid,key,lit)
            elif bare(key)=='_effectsNew':field(presetid,key,eff)
        point=val(p['_position'])['members']
        return dict(rgb=[lit.members[k] for k in ('_lightR','_lightG','_lightB')],intensity=lit.members['_lightIntensity'],source_id=row['source_id'],native_uid=p['_uID'],position=dict(point),native_radius=lit.members['_lightRadius'].members['_items'].items[0],reveals=lit.members['_visibleThroughFog'],darkness=lit.members['_darkness'],effect=row.get('effect'),enabled=lit.members['_hasLight'])
    new=[];nextuid=max(root['_nextUID'],max((objects[i]['members'].get('_uID',0)+1 for i in presets),default=1))
    for row in ir['lights']:
        if row['index'] is not None:
            if row['index']>=len(lights):raise ValueError('Source/native light ordering mismatch')
            report['lights'].append(modify(lights[row['index']],row));continue
        tile=record('light');p=tile.members['_tileInfo'].members
        point=row['position'];p['_position'].members.update(x=origin[0]+point['x']*units_per_grid,y=origin[1]-point['y']*units_per_grid)
        _set(p,_uID=nextuid,_sortingOrder=nextuid,_groupID=-1,_name='Darkness Source '+str(row['source_id']),_tileName='Darkness Source '+str(row['source_id']))
        p['_lighting']=lighting(p['_lighting'],row);p['_effectsNew']=effects(p['_effectsNew'],row)
        # Preserve inherited aliases when adding a fresh record.
        _set(p,_lighting=p['_lighting'],_effectsNew=p['_effectsNew'])
        new.append(Reference(writer.allocate(tile)));report['lights'].append(dict(source_id=row['source_id'],native_uid=nextuid,position=dict(p['_position'].members),native_radius=row['radius']*units_per_grid,darkness=True,reveals=False,effect=row.get('effect'),enabled=row.get('enabled',True),added=True));nextuid+=1
    for row in ir['tokens']:
        target=token_target(namespace,row['source_id'])
        if target not in tokens:
            losses.append(dict(grade='manual',feature='token-vision',source_id=row['source_id'],summary='No generated native token placement; vision not emitted as an unattached light'));continue
        values={**row,'enabled':True,'reveals':True,'darkness':False,'effect':None}
        report['tokens'].append({**modify(tokens[target],values),'name':row.get('name'),'target':target,'mode':row['mode'],'intensity':row['intensity']})
    if new:
        refs=[Reference(oid(v)) for v in active]+new
        replacement=Array(refs,*r.array_metadata[arrayid]);previous=writer.out;writer.out=bytearray();writer.array(replacement,arrayid);encoded=bytes(writer.out);writer.out=previous
        patches.append((*r.record_spans[arrayid],encoded));field(tilesid,'_size',len(refs));field(tilesid,'_version',tiles['_version']+len(new));field(rootid,'_nextUID',nextuid)
    updated=patch_stream(r,patches,writer,max_items=64000000)
    return updated,report

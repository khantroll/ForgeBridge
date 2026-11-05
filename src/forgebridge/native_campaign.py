"""Campaign IR to native schema-built 5e notes and rollable tables.

All records are constructed from member declarations. Captured templates supply
protocol defaults, never mutable user files or byte offsets.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from forgebridge.native import NoteBuilder, Node, Array, Writer
from forgebridge.dependencies import UUID_LINK
from forgebridge.campaign_dnd5e import text, number
from forgebridge.native_scene import background_asset
from forgebridge.scene_records import asset_templates
from forgebridge.uvtt import _safe_ref, _package_file
from forgebridge.validate import InventoryFatal

NATIVE_CAMPAIGN_REVISION = 3


class CampaignBuilder(NoteBuilder):
    def __init__(self):
        super().__init__()
        self.campaign = json.loads(Path(__file__).with_name('campaign-schema.json').read_text(encoding='utf-8'))
        known = {c['name'] for c in self.schema['classes']}
        self.schema['classes'] += [v for k,v in self.campaign['classes'].items() if k not in known]

    def note(self, name, fields, **kwargs):
        root=super().note(name,fields,**kwargs);seen=set();uid=1
        def walk(v):
            nonlocal uid
            if id(v) in seen:return
            seen.add(id(v))
            if isinstance(v,Node):
                if '_UID' in v.members and v.schema['name']!='ArkenNoteFieldCategory':
                    for key in v.members:
                        if key.split('+')[-1]=='_UID':v.members[key]=uid
                    uid+=1
                for x in v.members.values():walk(x)
            elif isinstance(v,Array):
                for x in v.items:walk(x)
        walk(root);root.members['nextUID']=uid
        return root

    def block(self, kind):
        memo = {}
        def build(v):
            if not isinstance(v, dict): return deepcopy(v)
            if 'use' in v: return memo[v['use']]
            if 'class' in v:
                schema = self.campaign['classes'][v['class']]
                if set(v['members']) != set(schema['names']): raise ValueError('Campaign schema/default mismatch')
                result = Node(deepcopy(schema), {}, v['inline']); memo[v['id']] = result
                result.members.update({k:build(x) for k,x in v['members'].items()})
            else:
                result = Array([], *deepcopy(v['array'])); memo[v['id']] = result
                result.items.extend(build(x) for x in v['items'])
            return result
        return build(self.campaign['defaults'][kind])

    def rich(self, runs, *, size=40, colour='000000'):
        result = self.text([(value, link) for value, font, link in runs])
        chars = result.members['_characters'].members['_items'].items
        offset = 0
        for value, font, link in runs:
            for char in chars[offset:offset+len(value)]:
                char.members.update(_size=size, _hexColour='B9CEFF' if link else colour)
                char.members['_fontSettings'].members['value__'] = font | (1024 if link else 0)
            offset += len(value)
        return result

    def style_block(self, block, kind):
        for key,style in self.campaign['styles'][kind].items():
            value=block.members[key]
            if value.schema['name']=='ArkenTextString': texts=[value]
            else:
                seq=value.members;texts=seq['_items'].items[:seq['_size']]
            for text_node in texts:
                text_node.members['_font']=style['_font']
                seq=text_node.members['_characters'].members
                for char in seq['_items'].items[:seq['_size']]:
                    char.members.update(_size=style['_size'],_defaultFont=style['_defaultFont'])
                    if not char.members['_link']:char.members['_hexColour']=style['_hexColour']
        return block


def campaign_files(ir, package, *, notes_folder, spell_root=None):
    builder = CampaignBuilder(); files, links, rows, playlists = {}, {}, [], []
    losses = list(ir['losses']); scope = ir['scope']; docs = ir['documents']
    # Revision 1 stat-block/linked-token check can leave edited notes after
    # --keep-changed. A visible revision in generated filenames preserves those
    # user edits instead of requiring overwrites or silently repinning identity.
    base = 'MyAssets/Encyclopedia/Notes/' + notes_folder + '/Campaign-v' + str(NATIVE_CAMPAIGN_REVISION) + '-' + scope + '-'
    paths = {}
    aliases = {}
    def loss(grade, feature, summary, **details): losses.append(dict(grade=grade, feature=feature, summary=summary, **details))
    # Missing external spells already carry one graded 'external-spell' loss;
    # their prose links stay as text without a second 'link' loss.
    external_missing = set((ir.get('spell_source') or {}).get('unresolved_uuids') or [])
    for doc in docs:
        if doc['kind'] == 'Playlist': continue
        if doc['kind'] == 'Actor' and doc.get('format') != 'dnd5e-actor': continue
        identity = (doc['kind'], doc['source_path'], doc['adventure_id'], doc['id'])
        paths[identity] = base + hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:20]
        pack_id=doc.get('pack_id') or str(ir.get('package_id',''))+'.'+Path(doc['source_path']).name
        candidates=[] if doc.get('external_system') else [doc['kind']+'.'+doc['id']]
        candidates += doc.get('uuid_aliases', [])
        if doc['adventure_id']:
            candidates.append('Compendium.'+pack_id+'.Adventure.'+doc['adventure_id']+'.'+doc['kind']+'.'+doc['id'])
        else:candidates += ['Compendium.'+pack_id+'.'+doc['kind']+'.'+doc['id'], 'Compendium.'+pack_id+'.'+doc['id']]
        for alias in sorted(set(candidates)):
            aliases.setdefault(alias, []).append(identity)
    # Only references to successfully emitted notes are exposed below.
    def segments(value):
        value=text(value); result=[]; end=0
        unsupported=sum(ord(c)>65535 or 0xD800<=ord(c)<=0xDFFF for c in value)
        if unsupported:
            loss('approximate','text','Non-BMP/surrogate characters replaced for the native Char field; original retained',count=unsupported)
            value=''.join('\uFFFD' if ord(c)>65535 or 0xD800<=ord(c)<=0xDFFF else c for c in value)
        for m in UUID_LINK.finditer(value):
            result.append((value[end:m.start()],0,None))
            targets=aliases.get(m[1],[])
            target=paths[targets[0]]+'.rwmeta' if len(targets)==1 else None
            result.append((m[2] or m[1],0,target)); end=m.end()
            if target is None and m[1] not in external_missing: loss('manual','link','Unresolved or ambiguous source link retained as text',uuid=m[1])
        result.append((value[end:],0,None))
        return result
    def txt(value, label=None, italic=False, title=False):
        runs=([(label+' ',1,None)] if label else [])+segments(value)
        if italic:runs=[(s,2,link) for s,_,link in runs]
        return builder.rich(runs,size=90 if title else 40,colour='58180D' if title else '000000')
    def portrait(ref, *, external=False):
        if not ref:return None
        try:
            safe, problem=_safe_ref(ref)
            if problem or not safe:raise ValueError('unsafe/remote portrait reference')
            root = spell_root if external else package
            if external and safe.startswith('systems/dnd5e/'):
                safe = safe[len('systems/dnd5e/'):]
            if root is None:
                raise ValueError('External spell media root unavailable')
            path=_package_file(Path(root),safe)
            if path.stat().st_size>32*1024*1024:raise ValueError('portrait exceeds 32 MiB')
            image=path.read_bytes(); key=hashlib.sha256(image).hexdigest()[:20]
            target='MyAssets/Media/Encyclopedia/Images/ForgeBridgeCampaign-'+scope+'/'+key
            if target+'.rwfile' not in files:
                asset,meta,_=background_asset(*asset_templates(),image,'Portrait')
                files[target+'.rwfile']=asset;files[target+'.rwmeta']=meta
            return target+'.rwmeta'
        except (OSError,ValueError,InventoryFatal) as exc:
            loss('manual','portrait',str(exc),source=ref);return None
    counts=dict(tables=0,actors=0,items=0,spells=0,playlists=0,tracks=0,manual_tracks=0)
    for doc in docs:
        p=doc['payload'];kind=doc['kind']; identity=(kind,doc['source_path'],doc['adventure_id'],doc['id']); path=paths.get(identity)
        fields=[];name=str(p.get('name') or doc['id'])
        if kind=='RollTable':
            table=[]
            for r in p.get('results',[]):
                span=r.get('range',[])
                if len(span)!=2:continue
                runs=segments(str(r.get('name') or '')+'\n'+str(r.get('description',r.get('text',''))))
                table.append((*span,[(s,link) for s,font,link in runs]))
            try: fields.append(builder.table_field(name,table,1));counts['tables']+=1
            except ValueError as exc:
                fields.append(builder.text_field('Table reference',[(text(json.dumps(p.get('results',[]))),None)],1))
                loss('manual','roll-table','Cannot represent source ranges: '+str(exc),source_id=doc['id'])
            fields.append(builder.text_field('Source roll settings',[(f"Formula: {p.get('formula')}; replacement: {p.get('replacement')}; weights/drawn/permissions are not automated.",None)],2))
            maximum=max((r[1] for r in table),default=0)
            if p.get('formula')!=f'1d{maximum}' or p.get('replacement') is not True or any(r.get('weight',1)!=1 or r.get('documentUuid') or r.get('documentId') for r in p.get('results',[])):
                loss('approximate','roll-table','Native range table retained; source formula/weights/replacement/document draws require review (not repaired)',source_id=doc['id'],formula=p.get('formula'))
        elif kind=='Actor':
            if doc.get('format') != 'dnd5e-actor':
                loss('unsupported','actor','Only dnd5e npc/character stat blocks supported',source_id=doc['id']);continue
            a=doc['display'];block=builder.block('Character');m=block.members
            values={'_nameText':txt(a['name'],title=True),'_typeText':txt(a['type'],italic=True),'_armorClassText':txt(a['ac'],'Armor Class'),
                    '_hitPointsText':txt('('+a['hp_formula']+')' if a['hp_formula'] else ''),'_speedText':txt(a['speed'],'Speed'),
                    '_savingThrowsText':txt(a['saves'],'Saving Throws'),'_skillsText':txt(a['skills'],'Skills'),
                    '_damageVulnerabilitiesText':txt(a['vulnerabilities'],'Damage Vulnerabilities'), '_damageResistancesText':txt(a['resistances'],'Damage Resistances'),
                    '_damageImmunitiesText':txt(a['immunities'],'Damage Immunities'),'_conditionImmunitiesText':txt(a['conditions'],'Condition Immunities'),
                    '_sensesText':txt(a['senses'],'Senses'),'_languagesText':txt(a['languages'],'Languages'),
                    '_challengeText':txt(a['challenge'],'Challenge'),'_proficiencyBonusText':txt(a['proficiency'],'Proficiency Bonus')}
            values.update({'_'+key+'ValNew':txt(value) for key,value in a['abilities'].items()});m.update(values)
            for key,value in [('_savingThrowsFieldActive',a['saves']),('_damageVulnerabilitiesFieldActive',a['vulnerabilities']),('_damageResistanceFieldActive',a['resistances']),('_damageImmunitiesFieldActive',a['immunities']),('_conditionImmunitiesFieldActive',a['conditions'])]:m[key]=bool(value)
            tracked=m['_trackedHitPoints'].members
            for suffix,value in [('currentValue',a['hp']),('maxValue',a['hp_max']),('minValue',0)]:
                tracked['_'+suffix]=float(value) if number(value) else 0.;tracked['_'+suffix+'Str']=str(value) if value is not None else ''
            for group,entries in a['actions'].items():
                seq=m['_'+group]; seq.members['_items'].items=[]
                for entry in entries:
                    runs=[(entry['name']+'. ',1,None)]
                    for value,font,link in segments(entry['description']):
                        parts=re.split(r'((?:Melee|Ranged)(?: or (?:Melee|Ranged))? (?:Weapon|Spell) Attack:|Hit:)',value)
                        runs.extend((part,2 if re.fullmatch(r'.*Attack:|Hit:',part) else font,link) for part in parts if part)
                    seq.members['_items'].items.append(builder.rich(runs))
                seq.members.update(_size=len(entries),_version=len(entries))
            builder.style_block(block,'Character')
            fields=[block]
            image=portrait(a['portrait'])
            if image:fields.insert(0,builder.media_field('Portrait',image,2))
            if a['biography']:fields.append(builder.text_field('Biography',[(s,link) for s,font,link in segments(a['biography'])],3))
            counts['actors']+=1
            loss('approximate','actor','Display stat block only; effects, automation, resources, spells/slots, ownership, actor deltas and vision are not converted',source_id=doc['id'],details=a['approximations'],
                 retained_only_fields=['effects','flags','ownership','prototypeToken','system.bonuses','system.currency','system.resources','system.spells','system.attributes.hp.temp','system.attributes.hp.tempmax','items[].system.activities','items[].effects','items[].flags'])
        elif kind=='Item':
            a=doc['display']; spell=doc['format']=='dnd5e-spell';block=builder.block('Spell' if spell else 'Item');m=block.members
            m.update(_nameText=txt(a['name'],title=True),_typeText=txt(a['type'],italic=True),_descriptionText=txt(a['description']))
            if spell:
                for key,field,label in [('casting','_castingTimeText','Casting Time'),('range','_rangeText','Range'),('components','_componentsText','Components'),('duration','_durationText','Duration'),('attack_save','_attackSaveText','Attack/Save'),('damage_effect','_damageEffectText','Damage/Effect'),('higher','_higherLevelsText','At Higher Levels')]:m[field]=txt(a[key],label)
            builder.style_block(block,'Spell' if spell else 'Item')
            fields=[block];image=portrait(a['portrait'],external=doc.get('external_system',False))
            if image:fields.insert(0,builder.media_field('Item image',image,2))
            counts['spells' if spell else 'items']+=1
            loss('approximate','spell' if spell else 'item','Display text/image only; mechanical activities, effects, formula evaluation and uses are not automated',source_id=doc['id'])
        elif kind=='Story':
            fields=[builder.text_field('Story',[(s,link) for s,font,link in segments(p.get('text') or '')],1)]
            image=portrait(p.get('image'))
            if image:fields.insert(0,builder.media_field('Image',image,2))
        elif kind=='Playlist':
            from forgebridge.native_audio import playlist_files
            audio,audit=playlist_files(p,package,scope,folder=notes_folder)
            files.update(audio);counts['playlists']+=audit['playlists'];counts['tracks']+=audit['tracks'];counts['manual_tracks']+=audit['manual_tracks'];losses.extend(audit['losses']);playlists.append(audit)
            continue
        else:continue
        files[path+'.rwnote']=Writer(builder.schema['libraries']).write(builder.note(name,fields,tag='ForgeBridge campaign'))
        files[path+'.rwmeta']=Writer(builder.schema['libraries']).write(builder.metadata(name))
        rows.append({'kind':kind,'source_id':doc['id'],'source_path':doc['source_path'],'adventure_id':doc['adventure_id'],'target':path+'.rwmeta','name':name,
                     **({'derived_values':a['derived_values']} if kind=='Actor' else {})})
    emitted={r['target'] for r in rows}
    for alias,ids in aliases.items():
        if len(ids)==1 and paths[ids[0]]+'.rwmeta' in emitted:links[alias]=paths[ids[0]]+'.rwmeta'
    # Failed targets cannot remain dangling inside emitted rich text.
    from forgebridge.native_dependencies import check_metadata_references
    check_metadata_references(files)
    files['campaign-source-'+scope+'.json']=json.dumps(ir,ensure_ascii=True,sort_keys=True).encode()
    from collections import Counter
    return files,{'scope':scope,'native_revision':NATIVE_CAMPAIGN_REVISION,'adventure_id':ir.get('adventure_id'),'spell_source':ir.get('spell_source'),'counts':{**counts,'notes':len(rows)},'documents':rows,'playlists':playlists,'links':links,'losses':losses,
                  'loss_counts':dict(Counter(l['grade'] for l in losses)),'runtime_validation':'not performed'}


def link_token_actors(files, scene, namespace, campaign):
    """Preserve v0.10 token bytes; linked text triggered note-marker rendering.

    Toolkit observation 2026-11-03 showed that adding a text/link field changes
    the map appearance despite an unchanged icon in metadata/selection. Until a
    separate native actor binding is demonstrated, emit no link and no mutation.
    """
    losses=[]
    for token in scene.get('tokens',[]):
        identity='Scene.'+scene['_id']+'.Token.'+str(token.get('_id'))
        key=hashlib.sha256((namespace+'\0'+identity).encode()).hexdigest()[:24]
        path='MyAssets/Encyclopedia/Notes/ForgeBridgeTokens/'+key+'.rwnote'
        if path in files and token.get('actorId'):
            losses.append({'grade':'manual','feature':'token-actor-link',
                'source_id':token.get('_id'),'actor_id':token['actorId'],
                'summary':'Link omitted: adding a text/link field rendered a note-marker icon in Toolkit. Token note/icon/Size bytes preserved; open the separate actor stat-block note by name.'})
    return {'count':0,'links':[],'losses':losses}

"""Bounded static dnd5e 4.3.5 arithmetic; no rolls, hooks, effects or scripts.

Rules: foundryvtt/dnd5e release-4.3.5, config.mjs armorClasses,
data/actor/templates/attributes.mjs, data/activity/attack-data.mjs.
"""
import math
import re


def finite(value):return type(value) in (int,float) and math.isfinite(value)


def static_number(value, refs=None):
    if value in (None,''):return 0
    if finite(value):return value
    if not isinstance(value,str) or len(value)>256:return None
    value=re.sub(r'@([A-Za-z_][\w.]*)',lambda m:str(refs[m[1]]) if refs and m[1] in refs and finite(refs[m[1]]) else m[0],value)
    value=re.sub(r'\s+','',value)
    for _ in range(8):value=value.replace('+-','-').replace('-+','-').replace('--','+').replace('++','+')
    if not re.fullmatch(r'[+-]?\d+(?:\.\d+)?(?:[+-]\d+(?:\.\d+)?)*',value):return None
    result=sum(float(term) for term in re.findall(r'[+-]?\d+(?:\.\d+)?',value))
    return result if math.isfinite(result) and abs(result)<1000000 else None


def armor_class(actor,mods):
    s=actor.get('system',{});ac=s.get('attributes',{}).get('ac',{});mode=ac.get('calc') or 'flat'
    details={'mode':mode,'source_flat':ac.get('flat'),'equipment':[],'warnings':[]}
    refs={'abilities.'+k+'.mod':v for k,v in mods.items()}
    gear=[];shields=[]
    for item in actor.get('items',[]):
        data=item.get('system',{});kind=data.get('type',{}).get('value')
        if item.get('type')!='equipment' or not data.get('equipped'):continue
        if kind=='shield':shields.append(item)
        elif kind in ('light','medium','heavy','natural'):gear.append(item)
    if len(gear)>1 or len(shields)>1:details['warnings'].append('Multiple equipped armors/shields: first source record used, matching Foundry preparation order')
    def equipment(item):
        a=item['system'].get('armor',{});base=a.get('value')
        magic=static_number(a.get('magicalBonus',item['system'].get('magicalBonus')),refs)
        details['equipment'].append(item.get('name'))
        return base+magic if finite(base) and magic is not None else None
    if mode=='flat':
        base=ac.get('value') if not ac.get('calc') and finite(ac.get('value')) else ac.get('flat')
        details['value']=base if finite(base) else None
        return details
    if mode=='natural':base=ac.get('flat')
    elif mode in ('default','armor'):
        base=10;dex=mods.get('dex')
        if gear:
            item=gear[0];base=equipment(item);kind=item['system']['type']['value'];cap=item['system'].get('armor',{}).get('dex')
            if kind=='heavy':dex=0
            elif finite(dex):dex=min(dex,cap if finite(cap) else (2 if kind=='medium' else dex))
        base=base+dex if finite(base) and finite(dex) else None
    elif mode in ('mage','draconic'):base=13+mods['dex'] if finite(mods.get('dex')) else None
    elif mode in ('unarmoredMonk','unarmoredBarb','unarmoredBard'):
        other={'unarmoredMonk':'wis','unarmoredBarb':'con','unarmoredBard':'cha'}[mode]
        base=10+mods['dex']+mods[other] if finite(mods.get('dex')) and finite(mods.get(other)) else None
    elif mode=='custom':base=static_number(ac.get('formula'),refs)
    else:base=None;details['warnings'].append('Unsupported AC mode: '+str(mode))
    shield=equipment(shields[0]) if shields else 0
    bonus=static_number(ac.get('bonus'),refs);cover=static_number(ac.get('cover'),refs);minimum=static_number(ac.get('min'),refs)
    details['value']=max(minimum,base+shield+bonus+cover) if all(finite(v) for v in (base,shield,bonus,cover,minimum)) else None
    if details['value'] is None:details['warnings'].append('AC requires unsupported/dynamic calculation; no value guessed')
    return details


def attacks(actor,item,mods,prof):
    system=actor.get('system',{});s=item.get('system',{});activities=s.get('activities',{})
    candidates=[(key,a) for key,a in activities.items() if a.get('type')=='attack'] if isinstance(activities,dict) else []
    if not candidates and s.get('actionType') in ('mwak','rwak','msak','rsak'):
        candidates=[('legacy',{'attack':{'ability':s.get('ability',''),'bonus':s.get('attackBonus',''),
            'type':{'value':'ranged' if s['actionType'].startswith('r') else 'melee','classification':'spell' if 'sak' in s['actionType'] else 'weapon'}}})]
    result=[]
    for key,activity in candidates:
        attack=activity.get('attack',{});kind=attack.get('type',{});ability=attack.get('ability') or s.get('ability')
        classification=kind.get('classification','weapon');ranged=kind.get('value')=='ranged'
        if ability=='spellcasting':ability=system.get('attributes',{}).get('spellcasting')
        if not ability:
            if classification=='spell':ability=system.get('attributes',{}).get('spellcasting')
            elif 'fin' in s.get('properties',[]) and finite(mods.get('str')) and finite(mods.get('dex')):ability=max(('str','dex'),key=lambda k:mods[k])
            else:ability='dex' if ranged else 'str'
        modifier=0 if ability=='none' else mods.get(ability)
        rank=s.get('proficient')
        if type(rank) is bool:rank=int(rank)
        if not finite(rank):rank=1 if actor.get('type')=='npc' or classification=='spell' else None
        refs={'mod':modifier,'prof':prof,**{'abilities.'+k+'.mod':v for k,v in mods.items()}}
        bonus=static_number(attack.get('bonus',s.get('attackBonus')),refs)
        magic=static_number(s.get('magicalBonus'),refs)
        code=('r' if ranged else 'm')+('sak' if classification=='spell' else 'wak')
        actor_bonus=static_number(system.get('bonuses',{}).get(code,{}).get('attack'),refs)
        if attack.get('flat'):total=bonus
        else:total=modifier+math.floor(rank*prof)+bonus+magic+actor_bonus if all(finite(v) for v in (modifier,rank,prof,bonus,magic,actor_bonus)) else None
        result.append({'item_id':item.get('_id'),'item':item.get('name'),'activity_id':key,
            'ability':ability,'ability_modifier':modifier,'proficiency':prof,'proficiency_multiplier':rank,
            'item_bonus':bonus,'magic_bonus':magic,'actor_bonus':actor_bonus,'flat_override':bool(attack.get('flat')),'total':total})
    return result

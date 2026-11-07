"""D&D5e source fields to display-only stat/item IR; never evaluate rolls."""
import math
import re
from forgebridge.notes import _plain_text
from forgebridge.enrichers import display_enrichers
from forgebridge.dnd5e_derived import armor_class, attacks

ABILITIES = ('str', 'dex', 'con', 'int', 'wis', 'cha')
SKILLS = dict(zip(('acr','ani','arc','ath','dec','his','ins','itm','inv','med','nat','prc','prf','per','rel','slt','ste','sur'),
                 ('Acrobatics','Animal Handling','Arcana','Athletics','Deception','History','Insight','Intimidation','Investigation','Medicine','Nature','Perception','Performance','Persuasion','Religion','Sleight of Hand','Stealth','Survival')))
XP = [10,25,50,100,200,450,700,1100,1800,2300,2900,3900,5000,5900,7200,8400,10000,11500,13000,15000,18000,20000,22000,25000,33000,41000,50000,62000,75000,90000,105000,120000,135000,155000]


def text(value):
    result = display_enrichers(_plain_text(str(value or '')))
    result = re.sub(r'\[\[(.*?)\]\](?:\{([^}]+)\})?', lambda m: m[2] or m[1].removeprefix('/r '), result)
    return result


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def signed(value): return f'{value:+g}'


def trait(value, *, deduplicate=False):
    if not isinstance(value, dict): return text(value)
    values = value.get('value', [])
    if isinstance(values, str): values = [values]
    custom=value.get('custom')
    parts = [str(v) for v in values or []] + ((re.split(r'[,;]',custom) if deduplicate else [custom]) if custom else [])
    if deduplicate:
        seen=set();parts=[v.strip() for v in parts if v.strip() and not (v.strip().casefold() in seen or seen.add(v.strip().casefold()))]
    if value.get('bypasses'): parts.append('except ' + ', '.join(value['bypasses']))
    return ', '.join(parts)


def actor_ir(actor):
    s = actor.get('system', {}); attrs = s.get('attributes', {}); details = s.get('details', {}); traits = s.get('traits', {})
    hp = attrs.get('hp', {}); ac = attrs.get('ac', {})
    cr = details.get('cr'); level = details.get('level')
    prof = attrs.get('prof', s.get('prof'))
    if not number(prof):
        basis = cr if actor.get('type') == 'npc' else level
        prof = max(2, 2 + math.floor((max(1, basis) - 1) / 4)) if number(basis) else None
    abilities, saves, skills, approximations = {}, [], [], []
    derived_attacks=[];changes=[]
    modifiers = {}
    def bonus(value, label):
        if value in (None, ''): return 0
        try:
            result = float(value)
            if math.isfinite(result): return result
        except (ValueError, TypeError): pass
        approximations.append(label + ': formula ' + str(value) + ' not evaluated')
        return 0
    for key in ABILITIES:
        ability = s.get('abilities', {}).get(key, {}); score = ability.get('value')
        mod = math.floor((score - 10) / 2) if number(score) else None; modifiers[key] = mod
        abilities[key] = f'{score:g} ({signed(mod)})' if mod is not None else 'Unknown'
        proficiency = ability.get('proficient', 0)
        if proficiency and mod is not None and number(proficiency) and number(prof):
            total = ability.get('save')
            if not number(total): total = mod + prof * proficiency + bonus(ability.get('bonuses', {}).get('save'), key + ' save')
            saves.append(key.upper() + ' ' + signed(total))
    for key, skill in s.get('skills', {}).items():
        if not isinstance(skill, dict): continue
        rank = skill.get('value', 0); mod = modifiers.get(skill.get('ability'))
        if rank and number(rank) and mod is not None and number(prof):
            total = skill.get('total')
            if not number(total): total = mod + rank * prof + bonus(skill.get('bonuses', {}).get('check'), key + ' skill')
            skills.append(SKILLS.get(key, key) + ' ' + signed(total))
    creature = details.get('type', {})
    if isinstance(creature, dict): creature = creature.get('custom') or ' '.join(str(creature.get(k) or '') for k in ('value','subtype')).strip()
    size = {'tiny':'Tiny','sm':'Small','med':'Medium','lg':'Large','huge':'Huge','grg':'Gargantuan'}.get(traits.get('size'), traits.get('size', ''))
    movement = attrs.get('movement', {}); units = movement.get('units', 'ft')
    speed = ', '.join((('' if k == 'walk' else k + ' ') + f'{movement[k]:g} {units}') for k in ('walk','burrow','climb','fly','swim') if number(movement.get(k)) and movement[k])
    if movement.get('hover'): speed += ' (hover)'
    senses = attrs.get('senses', {}); sensory = ', '.join(k + f' {v:g} ' + senses.get('units','ft') for k,v in senses.items() if number(v) and v)
    if senses.get('special'): sensory += ', ' + senses['special']
    xp = details.get('xp', {}).get('value') if isinstance(details.get('xp'), dict) else details.get('xp')
    if not number(xp) and number(cr):
        values = {0:10,.125:25,.25:50,.5:100, **{i:XP[i+3] for i in range(1,31)}}
        xp = values.get(cr)
    challenge = str(cr) if cr is not None else ''
    if xp is not None: challenge = (challenge + f' ({xp:g} XP)').strip()
    derived_ac=armor_class(actor,modifiers)
    armor=derived_ac['value']
    approximations.extend(derived_ac['warnings'])
    armor=f'{armor:g}' if number(armor) else 'Unknown (dynamic/unsupported AC)'
    actions = {k:[] for k in ('abilities','actions','reactions','legendaryActions')}
    for item in actor.get('items', []):
        ins = item.get('system', {}); acts = ins.get('activities', {})
        activation = ins.get('activation', {}).get('type')
        modes = {v.get('activation', {}).get('type') for v in acts.values() if isinstance(v, dict)} if isinstance(acts, dict) else set()
        modes.add(activation)
        group = 'legendaryActions' if 'legendary' in modes else 'reactions' if any(str(x).startswith('reaction') for x in modes) else 'actions' if 'action' in modes or item.get('type') in ('weapon','spell') else 'abilities'
        description = ins.get('description', {})
        description = description.get('value', '') if isinstance(description, dict) else description
        description=text(description)
        computed=attacks(actor,item,modifiers,prof);derived_attacks.extend(computed)
        totals={a['total'] for a in computed if number(a['total'])}
        if computed and len(totals)==1 and all(number(a['total']) for a in computed):
            total=next(iter(totals));old=description
            description,n=re.subn(r'(?<!\w)[+-]?\d+(?:\.\d+)?\s+to hit\b',signed(total)+' to hit',description,count=1,flags=re.I)
            if not n:description=f'Attack: {signed(total)} to hit. '+description
            if description!=old:changes.append({'field':'attack-to-hit','item':item.get('name'),'item_id':item.get('_id'),'source_text':re.findall(r'[+-]?\d+(?:\.\d+)?\s+to hit',old),'computed':signed(total)})
        elif computed:
            approximations.append('Attack bonus unresolved or differs by activity: '+str(item.get('name')))
        actions[group].append({'name': text(item.get('name','Unnamed')).rstrip('.'), 'description': description})
    return {'name': actor.get('name','Unnamed'), 'portrait': actor.get('img'),
            'type': f'{size} {creature}, {details.get("alignment", "")}'.strip(' ,'),
            'ac': str(armor), 'hp_formula': str(hp.get('formula') or ''),
            'hp': hp.get('value'), 'hp_max': hp.get('max'), 'speed': speed or 'Unknown',
            'abilities': abilities, 'saves': ', '.join(saves), 'skills': ', '.join(skills),
            'vulnerabilities': trait(traits.get('dv')), 'resistances': trait(traits.get('dr')),
            'immunities': trait(traits.get('di')), 'conditions': trait(traits.get('ci')),
            'senses': sensory.strip(', '), 'languages': trait(traits.get('languages'),deduplicate=True),
            'challenge': challenge, 'challenge_has_cr': cr is not None, 'proficiency': signed(prof) if number(prof) else '',
            'biography': text(details.get('biography', {}).get('value','')),
            'actions': actions, 'approximations': approximations,
            'derived_values':{'ac':derived_ac,'attacks':derived_attacks,'prose_corrections':changes}}


def item_ir(item):
    s = item.get('system', {}); description = s.get('description', {})
    result = {'name': item.get('name','Unnamed'), 'portrait': item.get('img'),
              'type': ', '.join(str(x) for x in (item.get('type'), s.get('rarity')) if x),
              'description': text(description.get('value','') if isinstance(description,dict) else description)}
    if item.get('type') == 'spell':
        def value(key):
            v=s.get(key, {})
            return ' '.join(str(v.get(k)) for k in ('value','units','special') if v.get(k) not in (None,'')) if isinstance(v,dict) else str(v or '')
        activation=s.get('activation', {}); materials=s.get('materials', {})
        properties=s.get('properties', [])
        components=s.get('components', {})
        if isinstance(components,dict): properties=list(properties or [])+[k for k in ('vocal','somatic','material') if components.get(k)]
        school = s.get('school') or ''
        school = {'abj':'abjuration','con':'conjuration','div':'divination','enc':'enchantment',
                  'evo':'evocation','ill':'illusion','nec':'necromancy','trs':'transmutation'}.get(school, school)
        spell_type = ((school.capitalize() + ' cantrip') if school else 'Cantrip') if s.get('level') == 0 else f'{s.get("level", "?")}-level {school}'
        result.update(type=spell_type,
            casting=' '.join(str(activation.get(k)) for k in ('cost','value','type') if activation.get(k) not in (None,'')),
            range=value('range'), components=', '.join(properties or []) + (' ('+str(materials.get('value'))+')' if materials.get('value') else ''),
            duration=value('duration'), attack_save=value('save'), damage_effect=value('damage'), higher=text(s.get('higherLevel','')))
    return result

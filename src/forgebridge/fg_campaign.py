"""Fantasy Grounds NPCs, items and story entries to native 5e notes.

File-level only, Toolkit check pending. Map geometry is untouched. Spell text
is taken only from the module; there is no dnd5e compendium input on this path.
Missing or conflicting fields are losses. Nothing is substituted.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile

from forgebridge.campaign_dnd5e import actor_ir, item_ir, number, text
from forgebridge.fantasy_grounds import MAX_IMAGE_BYTES, MAX_XML_BYTES, IMAGE_SUFFIXES, ModuleError, ModuleSource, definition, parse_xml
from forgebridge.native_campaign import campaign_files

ABILITIES = (('str', 'strength'), ('dex', 'dexterity'), ('con', 'constitution'),
             ('int', 'intelligence'), ('wis', 'wisdom'), ('cha', 'charisma'))
SKILL_KEYS = {
    'acrobatics': 'acr', 'animal handling': 'ani', 'arcana': 'arc', 'athletics': 'ath',
    'deception': 'dec', 'history': 'his', 'insight': 'ins', 'intimidation': 'itm',
    'investigation': 'inv', 'medicine': 'med', 'nature': 'nat', 'perception': 'prc',
    'performance': 'prf', 'persuasion': 'per', 'religion': 'rel', 'sleight of hand': 'slt',
    'stealth': 'ste', 'survival': 'sur',
    'acr': 'acr', 'ani': 'ani', 'arc': 'arc', 'ath': 'ath', 'dec': 'dec', 'his': 'his',
    'ins': 'ins', 'itm': 'itm', 'inv': 'inv', 'med': 'med', 'nat': 'nat', 'prc': 'prc',
    'prf': 'prf', 'per': 'per', 'rel': 'rel', 'slt': 'slt', 'ste': 'ste', 'sur': 'sur',
}
SKILL_ABILITY = {
    'acr': 'dex', 'ani': 'wis', 'arc': 'int', 'ath': 'str', 'dec': 'cha', 'his': 'int',
    'ins': 'wis', 'itm': 'cha', 'inv': 'int', 'med': 'wis', 'nat': 'int', 'prc': 'wis',
    'prf': 'cha', 'per': 'cha', 'rel': 'int', 'slt': 'dex', 'ste': 'dex', 'sur': 'wis',
}
STORY_CATEGORIES = ('encounter', 'story')


def _loss(grade, feature, summary, **details):
    return dict(grade=grade, feature=feature, summary=summary, **details)


def _number(node):
    if node is None or node.text is None or not str(node.text).strip():
        return None
    try:
        value = float(str(node.text).strip())
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    return int(value) if value.is_integer() else value


def _child_number(node, tag):
    return _number(node.find(tag)) if node is not None else None


def _links(value):
    return text(value or '')


def _newlines(value):
    """Normalize FG prose escapes only; never unicode-decode IDs or asset paths."""
    value = value.replace('\r\n', '\n').replace('\r', '\n')
    return re.sub(r'\\+(?:r\\+n|[rn])', '\n', value)


def _formatted(node):
    """Readable block boundaries and explicit FG record links; never execute markup."""
    if node is None:
        return None
    parts = []
    blocks = {'p', 'h', 'frame', 'list', 'linklist', 'li', 'table', 'tr'}
    def walk(el):
        if el.tag == 'link':
            record = (el.get('recordname') or el.findtext('recordname') or '').strip()
            label = ''.join(el.itertext()).strip() or record
            parts.append('@UUID[' + record + ']{' + label + '}' if record else label)
            return
        if el.tag in blocks: parts.append('\n')
        if el.tag == 'li': parts.append('• ')
        if el.tag == 'td': parts.append(' | ')
        if el.text: parts.append(el.text)
        for child in el:
            walk(child)
            if child.tail: parts.append(child.tail)
        if el.tag in blocks or el.tag == 'br': parts.append('\n')
    walk(node)
    value = text(_newlines(''.join(parts)))
    return re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', value).strip() or None


def _field(record, *tags):
    for tag in tags:
        value = _formatted(record.find(tag))
        if value:
            return value
    return None


def _cr_value(raw):
    if raw is None:
        return None
    try:
        if '/' in raw:
            left, right = raw.split('/', 1)
            value = float(left) / float(right)
        else:
            value = float(raw)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _proficiency(cr_text):
    value = _cr_value(cr_text)
    if value is None:
        return None
    return max(2, 2 + math.floor((max(1, value) - 1) / 4))


def _speed(raw):
    if not raw:
        return None, None
    movement, units, seen = {}, None, set()
    for part in (piece.strip() for piece in re.split(r'[,;]', raw) if piece.strip()):
        match = re.fullmatch(r'(?:(burrow|climb|fly|swim|walk)\s+)?(\d+(?:\.\d+)?)\s*(ft\.?|feet|m|meters?)?\.?', part, re.I)
        if not match:
            return None, 'Speed text is not a list of distances; the source text is kept and walk-first ordering is not applied'
        mode = (match.group(1) or 'walk').lower()
        if mode in seen:
            return None, 'A speed mode is repeated; the source text is kept and walk-first ordering is not applied'
        unit = match.group(3)
        unit = 'm' if unit and unit.lower().startswith('m') else 'ft'
        if units and unit != units:
            return None, 'Speed mixes units; the source text is kept and walk-first ordering is not applied'
        units, seen = unit, seen | {mode}
        movement[mode] = float(match.group(2))
    if not movement:
        return None, None
    return {'movement': movement, 'units': units or 'ft'}, None


def _image(record):
    token = record.find('token')
    if token is not None and token.get('type') in (None, 'token') and (token.text or '').strip():
        return token.text.strip()
    image = record.find('image')
    if image is not None:
        bitmap = image.find('bitmap')
        if bitmap is not None and (bitmap.text or '').strip():
            return bitmap.text.strip()
        if image.get('type') == 'image' and (image.text or '').strip():
            return image.text.strip()
    picture = record.find('picture')
    if picture is not None and (picture.text or '').strip():
        return picture.text.strip()
    return None


def _stage_image(source, ref, staged, losses, identity):
    original = ref
    if ref and '@' in ref:
        ref, module = ref.rsplit('@', 1)
        if module != definition(source).get('name'):
            losses.append(_loss('manual', 'image', 'Image belongs to another module; no external module lookup', source_id=identity, source=original))
            return None
    if not ref:
        return None
    suffix = Path(ref).suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        losses.append(_loss('unsupported', 'image', 'Image attachment is not a PNG, JPEG or WebP and was not copied',
                            source_id=identity, source=ref))
        return None
    if not source.exists(ref):
        losses.append(_loss('manual', 'image', 'Image attachment is missing or its path leaves the module; it was not opened',
                            source_id=identity, source=ref))
        return None
    try:
        staged[ref] = source.read(ref, MAX_IMAGE_BYTES)
    except ModuleError as exc:
        losses.append(_loss('manual', 'image', str(exc), source_id=identity, source=ref))
        return None
    return ref


def _entries(record, tag):
    parent = record.find(tag)
    if parent is None:
        return []
    found = []
    for child in list(parent):
        name = _field(child, 'name') or ''
        desc = _field(child, 'desc', 'description', 'text') or ''
        if name or desc:
            found.append((child, name, desc))
    return found


def _action_item(child, name, desc, activation):
    """Build a Foundry-shaped item only from fields the FG record stores."""
    stat = (_field(child, 'attackstat', 'ability') or '').lower()
    ability = dict(ABILITIES).get(stat[:3], None)
    for key, full in ABILITIES:
        if stat in (key, full):
            ability = key
    item_bonus = _child_number(child, 'bonus')
    stored_total = _child_number(child, 'attackbonus')
    lowered = desc.lower()
    ranged = 'ranged' in lowered
    melee = 'melee' in lowered
    item = {'name': name or 'Unnamed', '_id': child.tag, 'type': 'feat',
            'system': {'activation': {'type': activation}, 'description': {'value': desc}}}
    if ability and (ranged or melee) and activation in ('action', 'bonus', 'reaction', 'legendary'):
        item['system'].update(actionType='rwak' if ranged and not melee else 'mwak', ability=ability,
                              proficient=1, attackBonus=item_bonus if item_bonus is not None else 0, activities={})
    # The captured 5e Character block has actions, reactions and legendary actions.
    # Bonus actions have no field of their own, so they share the actions list.
    if activation in ('action', 'bonus'):
        item['type'] = 'weapon'
    return item, stored_total, ability, ranged or melee


def _npc(record, identity, losses, *, is_5e=True):
    gaps = []
    actor = {'name': _field(record, 'name') or 'Unnamed', 'type': 'npc', 'img': _image(record), 'items': [],
             'system': {'abilities': {}, 'attributes': {'hp': {}, 'ac': {}, 'movement': {}, 'senses': {}},
                        'details': {}, 'traits': {}, 'skills': {}}}
    system, attrs, details, traits = actor['system'], actor['system']['attributes'], actor['system']['details'], actor['system']['traits']
    for key, full in ABILITIES:
        node = record.find('abilities/' + full) if record.find('abilities') is not None else record.find(full)
        score = _child_number(node, 'score') if node is not None and node.find('score') is not None else _number(node)
        if score is None:
            gaps.append(full + ' score is not stored')
            continue
        ability = {'value': score}
        save = record.find('savingthrows/' + full)
        prof = _child_number(save, 'prof') if save is not None else None
        if prof:
            ability['proficient'] = prof
        system['abilities'][key] = ability
    skills_node = record.find('skills')
    skill_text = None
    if skills_node is not None and list(skills_node):
        for skill in list(skills_node):
            key = SKILL_KEYS.get(skill.tag.replace('_', ' ').lower())
            rank = _child_number(skill, 'prof')
            if key is None or not rank:
                gaps.append('Skill ' + skill.tag + ' has no proficiency rank that maps to a 5e skill')
                continue
            entry = {'value': rank, 'ability': SKILL_ABILITY[key]}
            misc = _child_number(skill, 'misc')
            if misc is not None:
                entry['bonuses'] = {'check': misc}
            total = _child_number(skill, 'total')
            if total is not None:
                entry['total'] = total
            system['skills'][key] = entry
    elif skills_node is not None and (skills_node.text or '').strip():
        skill_text = _formatted(skills_node)
    speed_raw = _field(record, 'speed')
    parsed, problem = _speed(speed_raw)
    if parsed:
        attrs['movement'] = {**parsed['movement'], 'units': parsed['units']}
    elif speed_raw:
        gaps.append(problem or 'Speed could not be ordered walk-first')
    ac = _child_number(record, 'ac')
    actext = _field(record, 'actext')
    if ac is not None:
        attrs['ac'] = {'value': ac}
    elif not actext:
        actext = _field(record, 'ac')
        if not actext: gaps.append('Armor class is not stored')
    hp_raw = _field(record, 'hp')
    hp = _child_number(record, 'hp')
    if hp is None and hp_raw:
        match = re.fullmatch(r'(\d+)\s*\(([^)]+)\)', hp_raw)
        if match: hp = int(match[1])
    if hp is not None:
        attrs['hp']['value'] = hp
        attrs['hp']['max'] = _child_number(record, 'hpmax') if record.find('hpmax') is not None else hp
    else:
        gaps.append('Hit points are not stored')
    formula = _field(record, 'hd', 'hpformula')
    if not formula and hp_raw and '(' in hp_raw: formula = hp_raw.partition('(')[2].rstrip(')')
    if formula:
        if re.fullmatch(r'\([^()]*\)',formula.strip()): formula=formula.strip()[1:-1].strip()
        attrs['hp']['formula'] = formula
    else:
        gaps.append('Hit point formula is not stored')
    cr_text = _field(record, 'cr')
    prof = _child_number(record, 'profbonus')
    if prof is None and cr_text and is_5e:
        prof = _proficiency(cr_text)
        if prof is not None:
            gaps.append('Proficiency bonus ' + str(prof) + ' is derived from CR ' + cr_text + ' because the module does not store one')
    elif prof is None:
        gaps.append('Proficiency bonus is not stored and CR is absent, so attack bonuses are not derived')
    if prof is not None:
        attrs['prof'] = prof
    size = _field(record, 'size') or ''
    kind = _field(record, 'type', 'creaturetype') or ''
    alignment = _field(record, 'alignment') or ''
    traits['size'] = size
    details['type'] = kind
    details['alignment'] = alignment
    if _field(record, 'languages'):
        traits['languages'] = {'value': [part.strip() for part in re.split(r'[,;]', _field(record, 'languages')) if part.strip()]}
    senses = _field(record, 'senses')
    if senses:
        attrs['senses']['special'] = senses
    xp = _child_number(record, 'xp')
    if xp is not None:
        details['xp'] = {'value': xp}
    details['cr'] = cr_text
    details['biography'] = {'value': _field(record, 'text', 'description') or ''}
    for source, target in [('damagevulnerabilities','dv'),('damageresistances','dr'),('damageimmunities','di'),('conditionimmunities','ci')]:
        value = _field(record, source)
        if value: traits[target] = value
    stored_totals = {}
    for tag, activation in (('traits', None), ('actions', 'action'), ('bonusactions', 'bonus'),
                            ('reactions', 'reaction'), ('legendaryactions', 'legendary')):
        for child, name, desc in _entries(record, tag):
            if activation is None:
                actor['items'].append({'name': name or 'Trait', 'type': 'feat', '_id': child.tag,
                                       'system': {'description': {'value': desc}}})
                continue
            item, stored_total, ability, shaped = _action_item(child, name, desc, activation)
            if activation == 'bonus':
                gaps.append('Bonus action "' + (name or child.tag) + '" is in the actions list; the 5e Character template has no bonus-action field')
            if shaped and not ability:
                gaps.append('Attack "' + (name or child.tag) + '" has no ability score, so its bonus was not derived')
            elif shaped and ability and prof is None:
                gaps.append('Attack "' + (name or child.tag) + '" was not given a derived bonus because proficiency is unknown')
            item['_id'] = tag + '.' + child.tag
            actor['items'].append(item)
            if stored_total is not None:
                stored_totals[item['_id']] = stored_total
    for tag in ('lairactions', 'lairaction'):
        for child, name, desc in _entries(record, tag):
            actor['items'].append({'name':'Lair action: '+(name or child.tag),'type':'feat','_id':tag+'.'+child.tag, 'system':{'description':{'value':desc}}})
            gaps.append('Lair action retained as an ability; native 5e template has no separate lair field')
    for tag in ('spells','innatespells'):
        value = _field(record, tag)
        if value:
            details['biography']['value'] += '\n' + tag + ': ' + value
            gaps.append(tag + ' preserved as biography text; slots/actions/automation not converted')
    display = actor_ir(actor)
    display['challenge_has_cr'] = bool(cr_text)
    if actext:
        display['ac'] = (f'{ac:g} ' if ac is not None and not re.match(r'^\s*\d', actext) else '') + actext
    elif ac is None:
        display['ac'] = ''
    saves_text = _field(record, 'savingthrows') if record.find('savingthrows') is not None and not list(record.find('savingthrows')) else None
    if saves_text: display['saves'] = saves_text
    if not is_5e:
        display['proficiency'] = ''
        display['derived_values']['attacks'] = []
        for tag,label in [('atk','Attack'),('fullatk','Full attack'),('specialattacks','Special attacks'),('specialqualities','Special qualities'),('feats','Feats'),('fortitudesave','Fortitude'),('reflexsave','Reflex'),('willsave','Will')]:
            value = _field(record, tag)
            if value: display['actions']['actions' if tag in ('atk','fullatk') else 'abilities'].append({'name':label,'description':value})
        gaps.append('Non-5e ruleset: native 5e template is display-only; source attacks/saves retained verbatim, no 5e proficiency derived')
    if skill_text is not None:
        display['skills'] = skill_text
        gaps.append('Skills are kept as the module text; individual bonuses were not re-derived')
    if not parsed and speed_raw:
        display['speed'] = speed_raw
    if not formula and hp_raw and hp is None: display['hp_formula'] = hp_raw
    if cr_text:
        display['challenge'] = cr_text + (f' ({xp:g} XP)' if number(xp) else '')
    elif xp is not None:
        display['challenge'] = f'({xp:g} XP)'
    else:
        display['challenge'] = ''
        gaps.append('Challenge rating is not stored')
    for group in display['actions'].values():
        for entry in group:
            for item in actor['items']:
                if text(item.get('name', '')).rstrip('.') != entry['name']:
                    continue
                stored = stored_totals.get(item.get('_id'))
                source = item['system'].get('description', {}).get('value', '')
                derived = next((row for row in display['derived_values']['attacks']
                                if row.get('item_id') == item.get('_id') and number(row.get('total'))), None)
                if stored is not None and (derived is None or derived['total'] != stored):
                    entry['description'] = text(source)
                    gaps.append('Stored attack bonus ' + str(stored) + ' for "' + entry['name'] +
                                '" is not ability modifier + proficiency + item bonus; the source text was kept')
                break
    if gaps:
        losses.append(_loss('approximate', 'npc', 'NPC "' + actor['name'] + '" is incomplete', source_id=identity, gaps=gaps))
    return display, actor


def _has_spell_text(description):
    stripped = re.sub(r'@UUID\[[^\]]*\](?:\{[^}]*\})?', '', description or '')
    return bool(stripped.strip())


def _item(record, identity, losses):
    name = _field(record, 'name') or 'Unnamed'
    kind = (_field(record, 'type', 'subtype') or '')
    description = _field(record, 'description', 'text', 'desc') or ''
    spell = kind.lower() == 'spell' or (record.find('school') is not None and record.find('level') is not None)
    if spell and not _has_spell_text(description):
        losses.append(_loss('unsupported', 'spell',
                            'Spell "' + name + '" does not store its text in this module. FG has no dnd5e spell-pack input, so no spell note was written',
                            source_id=identity))
        return None
    level = _child_number(record, 'level')
    school = _field(record, 'school') or ''
    payload = {'name': name, 'type': 'spell' if spell else (kind or 'item'), 'img': _image(record),
               'system': {'description': {'value': description}, 'rarity': _field(record, 'rarity') or ''}}
    if spell:
        payload['system'].update(school=school,
                                 activation={'type': _field(record, 'castingtime') or ''},
                                 range=_field(record, 'range') or '',
                                 duration=_field(record, 'duration') or '',
                                 properties=[part.strip() for part in re.split(r'[, ]+', _field(record, 'components') or '') if part.strip()],
                                 materials={'value': _field(record, 'material') or ''},
                                 save=_field(record, 'save', 'attack') or '',
                                 damage=_field(record, 'damage') or '',
                                 higherLevel=_field(record, 'athigherlevels', 'higher') or '')
        if level is not None:
            payload['system']['level'] = level
    extra = []
    for tag in ('subtype','cost','weight','properties','aura','cl','nonidentified'):
        value = _field(record, tag)
        if value: extra.append(tag + ': ' + value)
    if extra: payload['system']['description']['value'] += '\n' + '\n'.join(extra)
    display = item_ir(payload)
    if spell and level is None:
        display['type'] = ' '.join(part for part in (school, 'spell') if part).strip() or kind
        losses.append(_loss('approximate', 'spell', 'Spell "' + name + '" has no level; the type line uses only the stored school/type',
                            source_id=identity))
    missing = [label for label, value in (('casting time', display.get('casting')), ('range', display.get('range')),
                                           ('components', display.get('components')), ('duration', display.get('duration')))
               if spell and not value]
    if missing:
        losses.append(_loss('approximate', 'spell', 'Spell "' + name + '" is missing ' + ', '.join(missing), source_id=identity))
    if not spell and not description:
        losses.append(_loss('approximate', 'item', 'Item "' + name + '" has no description', source_id=identity))
    return display, spell


def _records(root, category):
    """FG category containers are transparent in record addresses."""
    groups = {'npc': ('reference.npcdata',),
              'item': ('reference.equipmentdata', 'reference.magicrefitemdata', 'reference.magicitemdata'),
              'spell': ('reference.spelldata',), 'story': ('reference.refmanualdata',)}
    result = []
    def visit(node, prefix):
        for child in node:
            if child.tag == 'category': visit(child, prefix)
            elif child.find('name') is not None or child.find('text') is not None:
                result.append((prefix + '.' + child.tag, child))
    parent = root.find(category)
    if parent is not None: visit(parent, category)
    for path in groups.get(category, ()):
        parent = root.find(path.replace('.', '/'))
        if parent is not None: visit(parent, path)
    return result


def _notes_folder(name):
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', ' ', name or '').strip().rstrip('.')
    return cleaned or 'Fantasy Grounds'


def campaign_ir(source: ModuleSource):
    if not source.exists('db.xml'):
        raise ModuleError('No db.xml; NPC, item and story records were not read')
    root = parse_xml(source.read('db.xml', MAX_XML_BYTES), 'db.xml')
    info = definition(source)
    module = info.get('name') or 'fantasy-grounds'
    losses, docs, staged = [], [], {}
    seen = set()

    def add_image(record, identity):
        ref = _image(record)
        staged_ref = _stage_image(source, ref, staged, losses, identity) if ref else None
        return staged_ref

    for identity, record in _records(root, 'npc'):
        if identity in seen:
            losses.append(_loss('unsupported', 'npc', 'Duplicate NPC record skipped', source_id=identity))
            continue
        seen.add(identity)
        if not _field(record, 'name'):
            losses.append(_loss('unsupported', 'npc', 'NPC record has no name and was not converted', source_id=identity))
            continue
        unmapped = [c.tag for c in record if c.tag not in {'name','abilities','strength','dexterity','constitution','intelligence','wisdom','charisma','ac','actext','hp','hpmax','hd','hpformula','speed','profbonus','cr','xp','size','type','creaturetype','alignment','languages','senses','skills','savingthrows','traits','actions','bonusactions','reactions','legendaryactions','lairactions','lairaction','text','description','token','picture','image','damagevulnerabilities','damageresistances','damageimmunities','conditionimmunities','spells','innatespells','atk','fullatk','specialattacks','specialqualities','feats','fortitudesave','reflexsave','willsave'}]
        if unmapped: losses.append(_loss('manual','npc-fields','Additional source NPC fields not mapped to the native display',source_id=identity,fields=unmapped))
        display, _actor = _npc(record, identity, losses, is_5e=not info.get('rulesets') or any(r.casefold() in ('5e','dnd5e') for r in info['rulesets']))
        image = add_image(record, identity)
        display['portrait'] = image
        docs.append({'kind': 'Actor', 'format': 'dnd5e-actor', 'id': identity, 'source_path': 'db.xml',
                     'adventure_id': module, 'uuid_aliases': [identity, identity + '@' + module, identity + '@*'], 'display': display,
                     'payload': {'name': display['name']}})
    for identity, record in _records(root, 'item') + _records(root, 'spell'):
        if identity in seen:
            losses.append(_loss('unsupported', 'item', 'Duplicate item record skipped', source_id=identity))
            continue
        seen.add(identity)
        built = _item(record, identity, losses)
        if built is None:
            continue
        display, spell = built
        unmapped = [c.tag for c in record if c.tag not in {'name','type','subtype','description','text','desc','rarity','token','picture','image','level','school','castingtime','range','duration','components','material','save','attack','damage','athigherlevels','higher','cost','weight','properties','aura','cl','nonidentified'}]
        if unmapped: losses.append(_loss('manual','item-fields','Additional identification, mechanical or linked-spell fields are not automated',source_id=identity,fields=unmapped))
        image = add_image(record, identity)
        display['portrait'] = image
        docs.append({'kind': 'Item', 'format': 'dnd5e-spell' if spell else '5e-item-text', 'id': identity,
                     'source_path': 'db.xml', 'adventure_id': module, 'uuid_aliases': [identity, identity + '@' + module, identity + '@*'],
                     'display': display, 'payload': {'name': display['name']}})
    for category in STORY_CATEGORIES:
        for identity, record in _records(root, category):
            if identity in seen:
                losses.append(_loss('unsupported', 'story', 'Duplicate story record skipped', source_id=identity))
                continue
            seen.add(identity)
            body = _field(record, 'text', 'description', 'desc')
            blocks = record.find('blocks')
            if blocks is not None:
                parts = [body] if body else []
                for block in blocks:
                    value = _field(block, 'text', 'text2')
                    if value: parts.append(value)
                    if block.find('text') is not None and block.find('text2') is not None:
                        value = _field(block, 'text2')
                        if value: parts.append(value)
                    unsupported = [x.tag for x in block if x.tag not in ('text','text2','align','blocktype','frame')]
                    if unsupported: losses.append(_loss('manual','story-block','Reference block media/layout fields need review',source_id=identity,fields=unsupported))
                body = '\n'.join(parts)
            name = _field(record, 'name') or identity
            if not body:
                losses.append(_loss('unsupported', 'story', 'Story entry "' + name + '" has no text and was not given a note',
                                    source_id=identity))
                continue
            image = add_image(record, identity)
            docs.append({'kind': 'Story', 'format': 'fg-story', 'id': identity, 'source_path': 'db.xml',
                         'adventure_id': module, 'uuid_aliases': [identity, identity + '@' + module, identity + '@*'],
                         'display': {}, 'payload': {'name': name, 'text': body, 'image': image}})
            if identity.startswith('reference.refmanualdata.'):
                docs[-1]['format']='fg-reference-page'
    from forgebridge.fg_records import extra_documents
    docs.extend(extra_documents(root,module,seen,losses,add_image))
    from forgebridge.fantasy_grounds import list_images
    for entry in list_images(source):
        identity = entry['record']
        if identity in seen: continue
        seen.add(identity)
        image = _stage_image(source, entry['bitmap'], staged, losses, identity)
        if image:
            docs.append({'kind':'Story','format':'fg-image','id':identity,'source_path':'db.xml',
                         'adventure_id':module,'uuid_aliases':[identity,identity+'@'+module,identity+'@*'],
                         'display':{},'payload':{'name':entry['name'],'text':'Source image; no grid/calibration inferred.','image':image}})
    if len(docs) > 2048:
        raise ModuleError('Campaign exceeds 2048 content records')
    losses.append(_loss('approximate','formattedtext','Paragraph/list/frame text and supported record links retained; original typography, frames, tables and interactive layout are flattened'))
    from forgebridge.scene_profile import fingerprint
    scope = hashlib.sha256(json.dumps(['fg-records-v2', module, fingerprint(source.path), sorted(doc['id'] for doc in docs)], sort_keys=True).encode()).hexdigest()[:20]
    return {'version': 1, 'scope': scope, 'package_id': module, 'adventure_id': module, 'documents': docs,
            'losses': losses, 'notes_folder': _notes_folder(info.get('displayname') or info.get('name'))}, staged


def build_campaign(module, *, notes_folder=None):
    """Return native files and a report. Evidence is file-level only."""
    with ModuleSource(module) as source:
        ir, staged = campaign_ir(source)
    with tempfile.TemporaryDirectory(prefix='forgebridge-fg-notes-') as tmp:
        root = Path(tmp)
        for rel, data in staged.items():
            target = root / rel
            if target.resolve().is_relative_to(root.resolve()):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        files, report = campaign_files(ir, root, notes_folder=notes_folder or ir['notes_folder'])
    report['counts']['stories'] = sum(d['format']=='fg-story' for d in ir['documents'])
    for count,form in [('reference_pages','fg-reference-page'),('reference_chapters','fg-reference-chapter'),('parcels','fg-parcel'),('quests','fg-quest'),('table_references','fg-table-reference')]:
        report['counts'][count] = sum(d['format']==form for d in ir['documents'])
    report['counts']['images'] = sum(d['format']=='fg-image' for d in ir['documents'])
    report['evidence'] = 'file-level only, Toolkit check pending'
    report['runtime_validation'] = 'not performed'
    report['reference_policy'] = 'Qualified local references and @* match unique converted local records only; other modules are not loaded; unresolved references stay labels with losses'
    report['source'] = 'fantasy_grounds'
    return files, report


def write_campaign(module, destination):
    """Write loose MyAssets files plus an installable native-package.zip.

    The zip is the same add-only review/install/uninstall receipt path Foundry
    native packages use. Evidence remains file-level only, Toolkit check pending.
    """
    destination = Path(destination)
    if destination.exists():
        raise ModuleError('Campaign output already exists: ' + str(destination))
    files, report = build_campaign(module)
    root = destination.resolve()
    for name, data in files.items():
        target = destination / name
        try:
            target.resolve().relative_to(root)
        except ValueError as exc:
            raise ModuleError('Campaign output path leaves the destination: ' + name) from exc
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(data)
    report_path = destination / 'fg-campaign-report.json'
    report_bytes = json.dumps(report, indent=2, ensure_ascii=True).encode()
    report_path.write_bytes(report_bytes)
    from forgebridge.native_dependencies import write_archive
    package = {**files, 'fg-campaign-report.json': report_bytes,
               'conversion-report.json': json.dumps({
                   'format': 'forgebridge.fg-campaign', 'version': 1,
                   'evidence': report.get('evidence'),
                   'runtime_validation': report.get('runtime_validation'),
                   'counts': report.get('counts'),
               }, indent=2).encode()}
    write_archive(destination / 'native-package.zip', package)
    report['native_package'] = 'native-package.zip'
    report_path.write_bytes(json.dumps(report, indent=2, ensure_ascii=True).encode())
    return report


def install_campaign(module, destination, myassets, backup_root):
    """Build campaign notes then install through the normal add-only path."""
    report = write_campaign(module, destination)
    from forgebridge.installer import install
    package = Path(destination) / 'native-package.zip'
    installation = install([package], myassets, backup_root)
    report['installed'] = True
    report['installation'] = installation
    report_path = Path(destination) / 'fg-campaign-report.json'
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding='utf-8')
    return report

"""Optional, read-only dnd5e compendium source; no name/suffix matching."""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

from forgebridge.campaign import display_document
from forgebridge.dependencies import UUID_LINK
from forgebridge.inventory import inventory_path
from forgebridge.scene_profile import fingerprint
from forgebridge.uvtt import _journal_pack_payloads


def spell_uuids(value):
    """Find enrichers in inert source strings, including actor item prose."""
    if isinstance(value, str):
        yield from (m[1] for m in UUID_LINK.finditer(value)
                    if m[1].startswith('Compendium.dnd5e.'))
    elif isinstance(value, dict):
        for child in value.values():
            yield from spell_uuids(child)
    elif isinstance(value, list):
        for child in value:
            yield from spell_uuids(child)


@contextmanager
def spell_source(path):
    """Accept a system folder/ZIP, or the standalone legacy spells pack.

    Bare JSON/NeDB/LevelDB packs explicitly mean dnd5e.spells. A system
    manifest supplies pack namespaces for newer layouts. Only referenced
    spell objects are imported; media stays inside the selected source root.
    """
    if path is None:
        yield None
        return
    from forgebridge.convert import source_root
    source = Path(path).absolute()
    digest = fingerprint(source)
    # source_root checks ancestor links as well as archive containment.
    for parent in (source, *source.parents):
        if parent.is_symlink() or parent.is_junction():
            raise ValueError('Spell source must not contain links/junctions')
    bare = (source.is_file() and source.suffix.lower() in ('.json', '.db')) or (
        source.is_dir() and (source / 'CURRENT').is_file())
    if bare:
        storage = 'leveldb' if source.is_dir() else 'json' if source.suffix.lower() == '.json' else 'nedb'
        rows = _journal_pack_payloads(source.parent, {
            'source_path': source.name, 'storage': storage, 'document_type': 'Item'})
        # A bare pack grants no enclosing Data/media root. External portraits
        # remain manual instead of reading arbitrary neighboring user files.
        result = _index([(rows, source.name, 'spells')], None,
                        {'input_sha256': digest, 'system_id': 'dnd5e', 'version': None,
                         'layout': 'standalone dnd5e.spells pack'})
        yield result
    else:
        with source_root(source) as (root, rejected):
            if rejected:
                raise ValueError('Spell source archive contains rejected paths')
            inventory = inventory_path(root)
            provenance = inventory['provenance']
            if provenance['package_type'] != 'system' or provenance['package_id'] != 'dnd5e':
                raise ValueError('Optional spell system must be a dnd5e system package')
            packs = []
            for pack in inventory['packs']:
                if pack['document_type'] != 'Item':
                    continue
                if not pack.get('decoded'):
                    raise ValueError('Spell system Item pack could not be decoded: ' + str(pack['path']))
                rows = _journal_pack_payloads(root, {'source_path': pack['path'],
                    'storage': pack['storage'], 'document_type': 'Item'})
                packs.append((rows, pack['path'], pack['name']))
            yield _index(packs, root, {'input_sha256': digest, 'system_id': 'dnd5e',
                'version': provenance.get('version'), 'layout': 'system package'})


def _index(packs, root, provenance):
    index = {}
    for rows, path, pack in packs:
        for obj in rows:
            if obj.get('type') != 'spell':
                continue
            ident = obj.get('_id', obj.get('id'))
            if not isinstance(ident, str) or not ident or '.' in ident:
                raise ValueError('External spell has an invalid source identity')
            aliases = [f'Compendium.dnd5e.{pack}.{ident}', f'Compendium.dnd5e.{pack}.Item.{ident}']
            doc = display_document({'kind': 'Item', 'id': ident, 'source_path': 'dnd5e-system/' + path,
                'pack_id': 'dnd5e.' + pack, 'adventure_id': None, 'payload': obj,
                'external_system': True, 'uuid_aliases': aliases}, 'dnd5e')
            for alias in aliases:
                if alias in index:
                    raise ValueError('Ambiguous external spell UUID: ' + alias)
                index[alias] = doc
    if len({id(doc) for doc in index.values()}) > 4096:
        raise ValueError('External spell source exceeds 4096 spells')
    return {'root': root, 'index': index, 'provenance': provenance}


def resolve_spells(ir, source):
    """Append the exact referenced closure to campaign IR, leaving gaps explicit."""
    result = deepcopy(ir)
    pending = set(spell_uuids([d['payload'] for d in result['documents']]))
    seen, imported, resolved, missing = set(), set(), [], []
    while pending:
        uuid = min(pending)
        pending.remove(uuid)
        if uuid in seen:
            continue
        seen.add(uuid)
        doc = source['index'].get(uuid) if source else None
        if doc is None:
            missing.append(uuid)
            result['losses'].append({'grade': 'manual', 'feature': 'external-spell', 'uuid': uuid,
                'summary': 'External spell unavailable; provide --dnd5e-system with the matching system/spells pack. No replacement invented.'})
            continue
        resolved.append(uuid)
        identity = (doc['source_path'], doc['id'])
        if identity not in imported:
            imported.add(identity)
            result['documents'].append(deepcopy(doc))
            pending.update(spell_uuids(doc['payload']))
            if len(result['documents']) > 2048:
                raise ValueError('Campaign with external spells exceeds 2048 documents')
    result['spell_source'] = {'provenance': source['provenance'] if source else None,
        'resolved_uuids': resolved, 'unresolved_uuids': missing, 'imported_spells': len(imported),
        'runtime_validation': 'not performed'}
    return result

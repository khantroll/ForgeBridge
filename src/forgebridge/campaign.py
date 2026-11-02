"""Foundry campaign source adapter. No source scripts or formulae are executed."""
import hashlib
import json
from forgebridge.uvtt import _journal_pack_payloads, _parent_adventure_id
from forgebridge.campaign_dnd5e import actor_ir, item_ir


COLLECTIONS = {'tables': 'RollTable', 'actors': 'Actor', 'items': 'Item', 'playlists': 'Playlist'}


def display_document(doc, system=None):
    """Attach source-system display IR while retaining the original inert object."""
    p=doc['payload']
    if doc['kind']=='Actor':
        system=p.get('_stats',{}).get('systemId') or system
        if system=='dnd5e' and p.get('type') in ('npc','character'):
            doc.update(format='dnd5e-actor', display=actor_ir(p))
    elif doc['kind']=='Item':doc.update(format='dnd5e-spell' if p.get('type')=='spell' else '5e-item-text',display=item_ir(p))
    return doc


def read_campaign(package, inventory, scene_row, *, cache=None):
    """Adventure-scoped full objects, plus world/compendium actors and items.

    Complete objects come from the bounded readers, never truncated inventory
    summaries. Other Adventures are deliberately excluded.
    """
    cache = {} if cache is None else cache
    parent = _parent_adventure_id(scene_row)
    source = scene_row.get('source_path')
    docs, errors = [], []
    def payloads(row):
        key = (row.get('source_path'), row['document_type'])
        if key not in cache: cache[key] = _journal_pack_payloads(package, row)
        return cache[key]
    def add(kind, obj, path, adventure=None):
        ident = obj.get('_id', obj.get('id'))
        if not isinstance(ident, str) or not ident:
            raise ValueError('Campaign document has no source identity')
        pack = next((p for p in inventory.get('packs',[]) if p.get('path')==path),{})
        docs.append(display_document({'kind': kind, 'id': ident, 'source_path': path,
                     'pack_id': inventory['provenance']['package_id'] + '.' + str(pack.get('name') or path.rsplit('/',1)[-1]),
                     'adventure_id': adventure, 'payload': obj}, pack.get('system') or inventory['provenance'].get('system')))
    if parent:
        rows = payloads({**scene_row, 'document_type': 'Adventure'})
        found = [p for p in rows if p.get('_id', p.get('id')) == parent]
        if len(found) != 1: raise ValueError('Selected campaign Adventure missing or ambiguous')
        for collection, kind in COLLECTIONS.items():
            objects = found[0].get(collection, [])
            if not isinstance(objects, list) or len(objects) > 2048:
                raise ValueError('Invalid/oversized campaign ' + collection)
            for obj in objects:
                if not isinstance(obj, dict):
                    errors.append({'grade': 'manual', 'feature': kind, 'summary': 'Adventure contains an unresolved document reference', 'source': obj})
                else: add(kind, obj, source, parent)
    seen = set()
    for row in inventory['documents']:
        kind = row.get('document_type')
        if kind not in ({'Actor', 'Item'} if parent else set(COLLECTIONS.values())): continue
        key = (row.get('source_path'), kind)
        if key in seen: continue
        seen.add(key)
        for obj in payloads(row): add(kind, obj, row.get('source_path'))
    identities = [(d['kind'], d['source_path'], d['adventure_id'], d['id']) for d in docs]
    if len(set(identities)) != len(identities): raise ValueError('Duplicate campaign source identity')
    if len(docs) > 2048: raise ValueError('Campaign exceeds 2048 documents')
    scope = hashlib.sha256(json.dumps([inventory['provenance']['package_id'], source if parent else None, parent]).encode()).hexdigest()[:20]
    return {'version': 1, 'scope': scope, 'documents': docs, 'losses': errors,
            'system': inventory['provenance'].get('system'), 'adventure_id': parent}

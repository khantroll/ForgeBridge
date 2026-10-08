"""Bounded, inert dependency graph for journal links and roll-table results."""
from collections import Counter, deque
import re

UUID_LINK = re.compile(r'@UUID\[([^\]\r\n]*)\](?:\{([^}\r\n]*)\})?')
SUPPORTED_TYPES = {'JournalEntry', 'RollTable'}


def _id(payload):
    return payload.get('_id', payload.get('id'))


def _key(kind, source, payload):
    return (kind, source.get('source_path'), source.get('parent_adventure_id'), _id(payload))


def _strings(value, path=''):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(item, f'{path}.{key}' if path else key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _strings(item, f'{path}[{i}]')


def _links(payload, kind, page_index=None):
    if page_index is not None:
        value = payload['pages'][page_index]
        prefix = f'pages[{page_index}]'
    else:
        value, prefix = payload, ''
    for path, text in _strings(value, prefix):
        for m in UUID_LINK.finditer(text):
            yield path, m.group(1), m.group(2)
    if kind == 'RollTable':
        results = payload.get('results', [])
        for i, result in enumerate(results if isinstance(results, list) else []):
            if not isinstance(result, dict):
                continue
            collection, doc_id = result.get('documentCollection'), result.get('documentId')
            if isinstance(collection, str) and collection and isinstance(doc_id, str) and doc_id:
                uuid = f'{collection}.{doc_id}' if '.' not in collection else f'Compendium.{collection}.{doc_id}'
                yield f'results[{i}].documentId', uuid, result.get('text')


def _parse(uuid, context):
    base, _, anchor = uuid.partition('#')
    parts = base.split('.')
    if len(parts) == 2 and parts[0] == '' and parts[1] and context['document_type'] == 'JournalEntry':
        return {'kind': 'JournalEntry', 'id': _id(context['payload']), 'page_id': parts[1],
                'relative': True, 'anchor': anchor}
    if len(parts) in {2, 4} and parts[0] in SUPPORTED_TYPES and parts[1]:
        if len(parts) == 4 and (parts[0] != 'JournalEntry' or parts[2] != 'JournalEntryPage' or not parts[3]):
            return None
        return {'kind': parts[0], 'id': parts[1], 'page_id': parts[3] if len(parts) == 4 else None,
                'relative': False, 'anchor': anchor}
    if len(parts) in {4, 6, 5, 7} and parts[0] == 'Compendium':
        # Support old pack.ID and explicit pack.DocumentType.ID spellings.
        offset = 3
        kind = None
        if len(parts) in {5, 7}:
            kind, offset = parts[3], 4
            if kind not in SUPPORTED_TYPES:
                return None
        if not all(parts[1:offset + 1]):
            return None
        remainder = parts[offset + 1:]
        if remainder and (len(remainder) != 2 or remainder[0] != 'JournalEntryPage' or not remainder[1]):
            return None
        if remainder and kind not in {None, 'JournalEntry'}:
            return None
        return {'kind': kind, 'id': parts[offset], 'page_id': remainder[1] if remainder else None,
                'pack_id': f'{parts[1]}.{parts[2]}', 'relative': False, 'anchor': anchor}
    return None


def resolve_dependencies(bundle, candidates, *, max_documents=256, max_references=4096):
    """Retain full linked objects; references point to exact pages where requested."""
    graph = {'schema_version': '1.0', 'documents': [], 'references': [], 'counts': {},
             'truncated': False, 'limits': {'documents': max_documents, 'references': max_references}}
    indexes, queue, scanned, seen_edges = {}, deque(), set(), set()
    for journal in bundle['journals']:
        key = _key('JournalEntry', journal['source'], journal['payload'])
        if key in indexes:
            continue
        if len(graph['documents']) >= max_documents:
            graph['truncated'] = True
            break
        indexes[key] = len(graph['documents'])
        graph['documents'].append({'document_type': 'JournalEntry', **journal})
        queue.append((indexes[key], None))
    while queue:
        origin_index, page_index = queue.popleft()
        if (origin_index, page_index) in scanned:
            continue
        scanned.add((origin_index, page_index))
        context = graph['documents'][origin_index]
        for path, uuid, label in _links(context['payload'], context['document_type'], page_index):
            edge_key = (origin_index, path, uuid)
            if edge_key in seen_edges:
                continue
            if len(graph['references']) >= max_references:
                graph['truncated'] = True
                queue.clear()
                break
            seen_edges.add(edge_key)
            edge = {'uuid': uuid, 'label': label, 'origin': {'document_index': origin_index, 'path': path},
                    'target': None}
            graph['references'].append(edge)
            parsed = _parse(uuid, context)
            if parsed is None:
                edge['status'] = 'unsupported_reference'
                continue
            matches = [c for c in candidates
                       if c.get('document_type', 'JournalEntry') in SUPPORTED_TYPES
                       and (parsed['kind'] is None or c.get('document_type', 'JournalEntry') == parsed['kind'])
                       and _id(c['payload']) == parsed['id']]
            if parsed['relative']:
                matches = [{'document_type': 'JournalEntry', 'source': context['source'], 'payload': context['payload']}]
            elif parsed.get('pack_id'):
                matches = [c for c in matches if c['source'].get('pack_id') == parsed['pack_id']]
            else:
                local = [c for c in matches if c['source'].get('source_path') == context['source'].get('source_path')
                         and c['source'].get('parent_adventure_id') == context['source'].get('parent_adventure_id')]
                # Do not jump to another Adventure when its IDs happen to match.
                matches = local or [c for c in matches if not c['source'].get('parent_adventure_id')]
            if len(matches) != 1:
                edge['status'] = 'missing_document' if not matches else 'ambiguous_document'
                continue
            candidate = matches[0]
            kind = candidate.get('document_type', 'JournalEntry')
            target_page = None
            if parsed['page_id']:
                pages = candidate['payload'].get('pages', [])
                found = [i for i, p in enumerate(pages if isinstance(pages, list) else [])
                         if isinstance(p, dict) and _id(p) == parsed['page_id']]
                if kind != 'JournalEntry' or len(found) != 1:
                    edge['status'] = 'missing_page' if not found else 'ambiguous_page'
                    continue
                target_page = found[0]
            key = _key(kind, candidate['source'], candidate['payload'])
            if key not in indexes:
                if len(graph['documents']) >= max_documents:
                    graph['truncated'] = True
                    edge['status'] = 'document_limit'
                    continue
                indexes[key] = len(graph['documents'])
                graph['documents'].append({'document_type': kind, 'source': candidate['source'], 'payload': candidate['payload']})
            edge['status'] = 'resolved'
            edge['target'] = {'document_index': indexes[key], 'page_index': target_page, 'anchor': parsed['anchor']}
            queue.append((indexes[key], target_page))
    graph['counts'] = dict(Counter(e['status'] for e in graph['references']))
    return graph

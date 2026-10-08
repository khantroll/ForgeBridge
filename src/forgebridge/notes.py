"""Correlate map notes with journal data; never render or execute source HTML."""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import math


def _id(value):
    return value.get('_id', value.get('id')) if isinstance(value, dict) else None


def correlate_notes(scene, candidates, origin, size, read_errors=()):
    """Candidates contain source, payload, and priority (lower is more local)."""
    result = {'schema_version': '1.0', 'scene_id': _id(scene),
              'scene_name': scene.get('name'), 'notes': [], 'journals': [],
              'read_errors': list(read_errors)}
    retained = {}
    for index, source_note in enumerate(scene.get('notes', [])):
        if not isinstance(source_note, dict):
            result['notes'].append({'note_index': index, 'status': 'invalid_note',
                                    'source_note': source_note})
            continue
        note = {'note_index': index, 'note_id': _id(source_note),
                'source_note': source_note, 'position': None,
                'entry_id': source_note.get('entryId'), 'page_id': source_note.get('pageId'),
                'journal_index': None, 'page_index': None,
                'title': source_note.get('text') or _id(source_note) or f'Note {index + 1}'}
        x, y = source_note.get('x'), source_note.get('y')
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (x, y)):
            note['position'] = {'x': (x - origin[0]) / size, 'y': (y - origin[1]) / size}
        entry_id = source_note.get('entryId')
        if not entry_id:
            note['status'] = 'label_only'
        elif not isinstance(entry_id, str):
            note['status'] = 'invalid_reference'
        else:
            if entry_id.startswith('JournalEntry.') and len(entry_id.split('.')) == 2:
                entry_id = entry_id.split('.')[1]
            # Unknown UUID namespaces stay explicit; never resolve by a suffix alone.
            matches = [c for c in candidates if c.get('document_type', 'JournalEntry') == 'JournalEntry'
                       and _id(c['payload']) == entry_id]
            if matches:
                priority = min(c['priority'] for c in matches)
                matches = [c for c in matches if c['priority'] == priority]
            if not matches:
                note['status'] = 'missing_entry'
            elif len(matches) != 1:
                note['status'] = 'ambiguous_entry'
            else:
                candidate = matches[0]
                key = (candidate['source']['source_path'], candidate['source'].get('parent_adventure_id'), entry_id)
                if key not in retained:
                    retained[key] = len(result['journals'])
                    result['journals'].append({'source': candidate['source'], 'payload': candidate['payload']})
                note['journal_index'] = retained[key]
                entry = candidate['payload']
                note['title'] = source_note.get('text') or entry.get('name') or note['title']
                page_id = source_note.get('pageId')
                pages = entry.get('pages', [])
                pages = pages if isinstance(pages, list) else []
                found = [(i, p) for i, p in enumerate(pages) if isinstance(p, dict) and _id(p) == page_id]
                if page_id and len(found) != 1:
                    note['status'] = 'missing_page' if not found else 'ambiguous_page'
                else:
                    note['status'] = 'resolved'
                    if page_id:
                        note['page_index'] = found[0][0]
                        note['title'] = source_note.get('text') or found[0][1].get('name') or note['title']
        result['notes'].append(note)
    result['counts'] = dict(Counter(n['status'] for n in result['notes']))
    from forgebridge.dependencies import resolve_dependencies
    result['dependencies'] = resolve_dependencies(result, candidates)
    return result


class _PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.suppressed = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'iframe', 'object'}:
            self.suppressed.append(tag)
        if not self.suppressed:
            if tag in {'p', 'div', 'br', 'tr', 'h1', 'h2', 'h3', 'h4', 'li'}:
                self.parts.append('\n')
            elif tag in {'td', 'th'}:
                self.parts.append('\t')

    def handle_endtag(self, tag):
        if self.suppressed:
            if tag == self.suppressed[-1]:
                self.suppressed.pop()
        elif tag in {'p', 'div', 'tr', 'li', 'h1', 'h2', 'h3', 'h4'}:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.suppressed:
            self.parts.append(data)


def _plain_text(value):
    parser = _PlainText()
    parser.feed(value if isinstance(value, str) else '')
    return '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())


def render_notes_text(bundle):
    """Readable GM reference. Original rich text and links remain in JSON."""
    parts = [str(bundle.get('scene_name') or bundle['scene_id']),
             'GM reference; not an Arkenforge import file. Original formatting, links, permissions, and media references remain in the companion JSON.']
    for note in bundle['notes']:
        parts += ['', f"NOTE {note['note_index'] + 1}: {note.get('title', 'Invalid note')}",
                  f"Status: {note['status']}"]
        if note.get('position'):
            parts.append(f"Map position (grid squares): x={note['position']['x']:g}, y={note['position']['y']:g}")
        if note['status'] != 'resolved':
            parts.append('Reference not resolved; no substitute room text was chosen.')
            continue
        entry = bundle['journals'][note['journal_index']]['payload']
        pages = entry.get('pages', [])
        pages = pages if isinstance(pages, list) else []
        if note['page_index'] is not None:
            pages = [pages[note['page_index']]]
        if not pages:
            parts.append(_plain_text(entry.get('content', '')))
            if entry.get('img'):
                parts.append(f"Media reference: {entry['img']}")
        for page in pages:
            if not isinstance(page, dict):
                continue
            parts.append(str(page.get('name') or 'Untitled page'))
            text = page.get('text')
            if isinstance(text, dict):
                content = text.get('content')
                parts.append(content if text.get('format') == 2 and isinstance(content, str) else _plain_text(content))
            if page.get('src'):
                parts.append(f"Media reference: {page['src']}")
    if bundle.get('read_errors'):
        parts += ['', 'Source read errors:'] + list(bundle['read_errors'])
    graph = bundle.get('dependencies')
    if graph:
        parts += ['', 'LINKED REFERENCES', 'Source UUIDs remain unchanged; this list records their resolution.']
        for edge in graph['references']:
            parts.append(f"{edge.get('label') or edge['uuid']}: {edge['status']} ({edge['uuid']})")
        if graph['truncated']:
            parts.append('Dependency traversal reached its documented limit; this reference is incomplete.')
        root_keys = {(j['source']['source_path'], j['source'].get('parent_adventure_id'), _id(j['payload']))
                     for j in bundle['journals']}
        shown_pages = {}
        for note in bundle['notes']:
            if note['status'] == 'resolved':
                journal = bundle['journals'][note['journal_index']]
                key = (journal['source']['source_path'], journal['source'].get('parent_adventure_id'), _id(journal['payload']))
                shown_pages.setdefault(key, set()).add(note['page_index'])
        for index, document in enumerate(graph['documents']):
            payload, source = document['payload'], document['source']
            key = (source['source_path'], source.get('parent_adventure_id'), _id(payload))
            targets = [e['target']['page_index'] for e in graph['references']
                       if e['status'] == 'resolved' and e['target']['document_index'] == index]
            pages = payload.get('pages', [])
            pages = pages if isinstance(pages, list) else []
            selected_pages = {i for i in range(len(pages)) if None in targets or i in targets}
            if key in root_keys and document['document_type'] == 'JournalEntry':
                shown = shown_pages.get(key, set())
                if None in shown:
                    continue
                selected_pages -= shown
                if not selected_pages:
                    continue
            parts += ['', f"LINKED {document['document_type']}: {payload.get('name') or _id(payload)}"]
            if document['document_type'] == 'RollTable':
                parts.append(f"Formula: {payload.get('formula', 'unspecified')} (reference only; no roll executed)")
                results = payload.get('results', [])
                for result in results if isinstance(results, list) else []:
                    if isinstance(result, dict):
                        parts.append(f"Range {result.get('range')}; weight {result.get('weight')}: " + _plain_text(result.get('text', '')))
            else:
                for i, page in enumerate(pages):
                    if isinstance(page, dict) and i in selected_pages:
                        parts.append(str(page.get('name') or 'Untitled page'))
                        text = page.get('text')
                        if isinstance(text, dict):
                            content = text.get('content')
                            parts.append(content if text.get('format') == 2 and isinstance(content, str) else _plain_text(content))
                        if page.get('src'):
                            parts.append(f"Media reference: {page['src']}")
                if not pages:
                    parts.append(_plain_text(payload.get('content', '')))
    return '\n'.join(parts) + '\n'

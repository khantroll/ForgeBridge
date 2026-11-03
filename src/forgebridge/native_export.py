"""Compile preserved Foundry companions to experimental native note packages.

Only resolved dependency edges become native links. Source data is retained
unchanged in the package; markup, media, permissions and map placements are
reported rather than silently represented as supported destination features.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import zipfile

from forgebridge.dependencies import UUID_LINK, resolve_dependencies
from forgebridge.native import NoteBuilder, Writer


class TextCompiler(HTMLParser):
    def __init__(self, resolve_link, issues, origin, *, strip_enrichers=False):
        super().__init__(convert_charrefs=True)
        self.resolve_link, self.issues, self.origin = resolve_link, issues, origin
        self.parts, self.suppressed = [], []
        self.strip_enrichers = strip_enrichers

    def issue(self, code, **details):
        self.issues.append({'code': code, 'origin': self.origin, **details})

    def append(self, text, link=None):
        bad = sum(ord(c) > 65535 or 0xD800 <= ord(c) <= 0xDFFF for c in text)
        if bad:
            self.issue('unicode_replaced', count=bad)
            text = ''.join('\uFFFD' if ord(c) > 65535 or 0xD800 <= ord(c) <= 0xDFFF else c for c in text)
        if text:
            if self.parts and self.parts[-1][1] == link:
                self.parts[-1] = (self.parts[-1][0] + text, link)
            else:
                self.parts.append((text, link))

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'iframe', 'object'}:
            self.suppressed.append(tag)
            self.issue('active_markup_omitted', tag=tag)
        if self.suppressed:
            return
        values = dict(attrs)
        if tag in {'p', 'div', 'br', 'tr', 'h1', 'h2', 'h3', 'h4', 'li'}:
            self.append('\n')
        elif tag in {'td', 'th'}:
            self.append('\t')
        if tag in {'img', 'audio', 'video'}:
            self.issue('media_reference_only', src=values.get('src'))
            self.append(f"[Media: {values.get('src') or values.get('alt') or tag}]")
        if tag == 'a' and values.get('href'):
            self.issue('html_link_reference_only', href=values['href'])
            self.append(f"[Link: {values['href']}] ")

    def handle_endtag(self, tag):
        if self.suppressed:
            if tag == self.suppressed[-1]:
                self.suppressed.pop()
        elif tag in {'p', 'div', 'tr', 'li', 'h1', 'h2', 'h3', 'h4'}:
            self.append('\n')

    def handle_data(self, data):
        if self.suppressed:
            return
        start = 0
        for match in UUID_LINK.finditer(data):
            self.append(data[start:match.start()])
            target = self.resolve_link(match.group(1))
            if target:
                self.append(match.group(2) or match.group(1), target)
            else:
                self.append((match.group(2) or match.group(1)) if self.strip_enrichers else match.group(0))
            start = match.end()
        self.append(data[start:])

    def compile(self, text, *, plain=False):
        if plain:
            self.handle_data(text)
        else:
            self.issue('html_rendered_as_plain_text')
            self.feed(text)
            self.close()
        # Keep paragraph breaks and links; trim only outer whitespace.
        if self.parts:
            self.parts[0] = (self.parts[0][0].lstrip(), self.parts[0][1])
            self.parts[-1] = (self.parts[-1][0].rstrip(), self.parts[-1][1])
        return self.parts or [('', None)]


def companion_files(companion, *, map_markers=False, media_fields=None, note_folder=None, note_prefix=''):
    media_fields = media_fields or {}
    campaign_links = companion.get('campaign_links', {})
    if (not isinstance(campaign_links,dict) or len(campaign_links)>4096 or
            any(not isinstance(k,str) or not isinstance(v,str) or
                not v.startswith('MyAssets/Encyclopedia/Notes/') or not v.endswith('.rwmeta')
                for k,v in campaign_links.items())):
        raise ValueError('Invalid campaign note links')
    from forgebridge.native_dependencies import safe_name
    for target in campaign_links.values(): safe_name(target)
    bundle = companion.get('scene_notes')
    if not isinstance(bundle, dict) or not isinstance(bundle.get('dependencies'), dict):
        raise ValueError('Companion needs scene_notes.dependencies; export it again with ForgeBridge')
    graph = bundle['dependencies']
    documents, edges = graph.get('documents'), graph.get('references')
    if not isinstance(documents, list) or len(documents) > 256 or not isinstance(edges, list) or len(edges) > 4096:
        raise ValueError('Invalid or oversized dependency graph')
    for document in documents:
        if not isinstance(document, dict) or document.get('document_type') not in {'JournalEntry', 'RollTable'} or not isinstance(document.get('payload'), dict) or not isinstance(document.get('source'), dict):
            raise ValueError('Invalid dependency document')
        pages = document['payload'].get('pages', [])
        if not isinstance(pages, list) or len(pages) > 512 or any(not isinstance(p, dict) for p in pages):
            raise ValueError('Invalid or oversized journal pages')
    if 1 + len(documents) + sum(len(d['payload'].get('pages', [])) for d in documents) > 2048:
        raise ValueError('Native note count exceeds limit')
    def identity(source, payload):
        return (source.get('source_path'), source.get('parent_adventure_id'), payload.get('_id', payload.get('id')))
    # Retained full journals may contain pages outside the original traversal.
    # Resolve their edges using only already-retained, scoped documents. Never
    # overwrite a prior edge status or reach into a different source package.
    expanded = resolve_dependencies({'journals': [d for d in documents if d.get('document_type') == 'JournalEntry']}, documents)
    originals = {(d['document_type'], identity(d['source'], d['payload'])): i for i, d in enumerate(documents)}
    if len(originals) != len(documents):
        raise ValueError('Duplicate retained document identity')
    remap = {i: originals[(d['document_type'], identity(d['source'], d['payload']))] for i, d in enumerate(expanded['documents'])}
    edges = list(edges)
    known = {(e['origin']['document_index'], e['origin']['path'], e['uuid']) for e in edges}
    for edge in expanded['references']:
        origin = {**edge['origin'], 'document_index': remap[edge['origin']['document_index']]}
        key = (origin['document_index'], origin['path'], edge['uuid'])
        if key in known or len(edges) >= 4096:
            continue
        target = edge.get('target')
        if target:
            target = {**target, 'document_index': remap[target['document_index']]}
        edges.append({**edge, 'origin': origin, 'target': target})
        known.add(key)
    digest = hashlib.sha256(json.dumps({'scene': bundle.get('scene_id'), 'documents': documents}, sort_keys=True).encode()).hexdigest()[:12]
    if note_folder is not None and (not isinstance(note_folder, str) or not note_folder or
            len(note_folder) > 160 or re.search(r'[<>:"/\\|?*\x00-\x1f]', note_folder) or
            note_folder[-1] in '. ' or note_folder in ('.', '..') or
            note_folder.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL',
                *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}):
        raise ValueError('Note folder must be a portable single folder name')
    base = 'MyAssets/Encyclopedia/Notes/' + (note_folder or f'ForgeBridge-{digest}') + '/'
    if note_prefix and not re.fullmatch(r'[a-f0-9]{20}-', note_prefix):
        raise ValueError('Invalid internal note prefix')
    paths, names = {(None, None): base + note_prefix + '000-Scene-Index'}, {}
    for di, document in enumerate(documents):
        payload = document['payload']
        if document['document_type'] not in {'JournalEntry', 'RollTable'} or not isinstance(payload, dict):
            raise ValueError('Unsupported dependency document')
        paths[(di, None)] = base + note_prefix + f'D{di:03d}'
        if document['document_type'] == 'RollTable':
            external = campaign_links.get('RollTable.' + str(payload.get('_id', payload.get('id'))))
            if external: paths[(di, None)] = external[:-7]
        names[(di, None)] = str(payload.get('name') or f'Document {di + 1}')
        pages = payload.get('pages', [])
        if not isinstance(pages, list) or len(pages) > 512:
            raise ValueError('Invalid or oversized journal pages')
        for pi, page in enumerate(pages):
            if not isinstance(page, dict):
                raise ValueError('Invalid journal page')
            paths[(di, pi)] = base + note_prefix + f'D{di:03d}-P{pi:03d}'
            names[(di, pi)] = names[(di, None)] + ' — ' + str(page.get('name') or f'Page {pi + 1}')
    if len(paths) > 2048:
        raise ValueError('Native note count exceeds limit')
    issues, files, native_tables = [], {}, []
    rewritten, unresolved = [], []
    edge_map = {}
    for edge in edges:
        origin = edge.get('origin', {})
        key = (origin.get('document_index'), origin.get('path'), edge.get('uuid'))
        edge_map.setdefault(key, []).append(edge)

    def compile_text(text, di, source_path, *, plain=False):
        origin = {'document_index': di, 'path': source_path}
        def resolve(uuid):
            if uuid in campaign_links:
                rewritten.append({'origin': origin, 'uuid': uuid, 'target': campaign_links[uuid]})
                return campaign_links[uuid]
            matches = edge_map.get((di, source_path, uuid), [])
            edge = matches[0] if len(matches) == 1 else None
            target = edge.get('target') if edge else None
            target_path = paths.get((target.get('document_index'), target.get('page_index'))) if isinstance(target, dict) else None
            if edge and edge.get('status') == 'resolved' and target_path:
                rewritten.append({'origin': origin, 'uuid': uuid, 'target': target_path + '.rwmeta'})
                if target.get('anchor'):
                    issues.append({'code': 'anchor_not_preserved', 'origin': origin, 'uuid': uuid})
                return target_path + '.rwmeta'
            unresolved.append({'origin': origin, 'uuid': uuid, 'status': edge.get('status') if edge else 'not_in_retained_graph'})
            return None
        value = text if isinstance(text, str) else ''
        if campaign_links:
            value = re.sub(r'\[\[([^\]]+)\]\](?:\{([^}]+)\})?', lambda m: m[2] or m[1].removeprefix('/r '), value)
        return TextCompiler(resolve, issues, origin, strip_enrichers=bool(campaign_links)).compile(value, plain=plain)

    builder = NoteBuilder()
    attached_media = []
    def emit(key, name, specs):
        fields = []
        for uid, (kind, title, value) in enumerate(specs, 1):
            fields.append(builder.table_field(title, value, uid) if kind == 'table' else builder.text_field(title, value, uid))
        for attachment in media_fields.get(key, []):
            fields.append(builder.media_field(attachment.get('label') or 'Image attachment ' + str(len(attached_media) + 1), attachment['target'], len(fields) + 1))
            attached_media.append({'note': paths[key] + '.rwmeta', **attachment})
        files[paths[key] + '.rwnote'] = Writer(builder.schema['libraries']).write(builder.note(name, fields, tag='ForgeBridge import'))
        files[paths[key] + '.rwmeta'] = Writer(builder.schema['libraries']).write(builder.metadata(name))

    for di, document in enumerate(documents):
        payload = document['payload']
        if document['document_type'] == 'RollTable' and ('RollTable.' + str(payload.get('_id', payload.get('id')))) in campaign_links:
            continue
        fields = []
        if document['document_type'] == 'JournalEntry':
            pages = payload.get('pages', [])
            if payload.get('content'):
                fields.append(('text', 'Journal text', compile_text(payload['content'], di, 'content')))
            navigation = []
            for pi, page in enumerate(pages):
                navigation += [(str(page.get('name') or f'Page {pi + 1}'), paths[(di, pi)] + '.rwmeta'), ('\n', None)]
                text = page.get('text') if isinstance(page.get('text'), dict) else {}
                page_fields = [('text', 'Journal', [(names[(di, None)], paths[(di, None)] + '.rwmeta')]),
                               ('text', 'Page text', compile_text(text.get('content', ''), di, f'pages[{pi}].text.content', plain=text.get('format') == 2))]
                if page.get('src'):
                    page_fields.append(('text', 'Media reference', [(str(page['src']), None)]))
                    issues.append({'code': 'page_media_reference_only', 'origin': {'document_index': di, 'page_index': pi}, 'src': page['src']})
                emit((di, pi), names[(di, pi)], page_fields)
            if navigation:
                fields.append(('text', 'Pages', navigation))
            if payload.get('img'):
                fields.append(('text', 'Media reference', [(str(payload['img']), None)]))
                issues.append({'code': 'journal_media_reference_only', 'origin': {'document_index': di}, 'src': payload['img']})
        else:
            fields.append(('text', 'Description', compile_text(payload.get('description', ''), di, 'description')))
            results = payload.get('results', [])
            if not isinstance(results, list) or len(results) > 256 or any(not isinstance(r, dict) for r in results):
                raise ValueError('Invalid or oversized table results')
            rows, reference = [], []
            compatible = bool(results) and payload.get('replacement') is True
            formula = re.fullmatch(r'1d([1-9][0-9]*)', str(payload.get('formula', '')))
            compatible &= formula is not None
            for ri, result in enumerate(results):
                segments = []
                if result.get('name'):
                    segments = compile_text(result['name'], di, f'results[{ri}].name', plain=True) + [('\n', None)]
                field = 'description' if 'description' in result else 'text'
                segments += compile_text(result.get(field, ''), di, f'results[{ri}].{field}')
                span = result.get('range')
                valid = isinstance(span, list) and len(span) == 2 and all(type(n) is int for n in span) and 1 <= span[0] <= span[1] <= 1000000
                compatible &= valid and result.get('weight') == 1 and result.get('type') in (0, 'text') and not result.get('documentUuid') and not result.get('documentId')
                if valid:
                    rows.append((*span, segments))
                reference += [(f"Range {span}; weight {result.get('weight')}: ", None)] + segments + [('\n', None)]
            ordered = sorted(rows, key=lambda r: r[0])
            expected = 1
            for start, end, _ in ordered:
                compatible &= start == expected and start == end
                expected = end + 1
            compatible &= bool(formula) and expected - 1 == (int(formula.group(1)) if formula else 0)
            if compatible:
                fields.append(('table', 'Roll', ordered))
                native_tables.append({'document_index': di, 'name': names[(di, None)], 'formula': payload['formula'], 'rows': len(rows)})
            else:
                fields.append(('text', 'Table reference (not rollable)', reference or [('No results', None)]))
                issues.append({'code': 'table_semantics_reference_only', 'origin': {'document_index': di}, 'formula': payload.get('formula')})
            fields.append(('text', 'Source roll settings', [(f"Formula: {payload.get('formula')}; replacement: {payload.get('replacement')}; displayRoll: {payload.get('displayRoll')}. Source drawn state and permissions are not applied.", None)]))
        emit((di, None), names[(di, None)], fields or [('text', 'Contents', [('', None)])])

    # Map placements remain a report. Match retained journal provenance exactly.
    journal_map = {identity(d['source'], d['payload']): di for di, d in enumerate(documents) if d['document_type'] == 'JournalEntry'}
    placements, navigation = [], []
    for note in bundle.get('notes', []):
        target = None
        if note.get('status') == 'resolved':
            journal = bundle['journals'][note['journal_index']]
            di = journal_map.get(identity(journal['source'], journal['payload']))
            target = paths.get((di, note.get('page_index')))
        placement = {'note_id': note.get('note_id'), 'title': note.get('title'), 'source_status': note.get('status'),
                     'grid_position': note.get('position'), 'target': target + '.rwmeta' if target else None,
                     'native_map_placement': False}
        placements.append(placement)
        navigation += [(str(note.get('title') or 'Map note'), placement['target']), ('\n', None)]
    emit((None, None), str(bundle.get('scene_name') or bundle.get('scene_id')) + ' — Start Here', [
        ('text', 'Import limitations', [('Plain text conversion. Review player visibility before sharing. ' + ('Supported images have native attachments; other media remain references. ' if media_fields else 'Media are references. ') + ('Room markers are supplied in the separate native map copy. ' if map_markers else 'Map markers are not placed automatically. ') + 'Keep this folder at the exact path in INSTALL.txt.', None)]),
        ('text', 'Scene notes', navigation or [('No placed notes in source', None)]),
        ('text', 'Linked documents', sum(([(names[(di, None)], paths[(di, None)] + '.rwmeta'), ('\n', None)] for di in range(len(documents))), []))])
    attached_refs = {a['ref'] for a in attached_media}
    for issue in issues:
        if issue.get('src') in attached_refs and issue['code'] in {'media_reference_only', 'page_media_reference_only', 'journal_media_reference_only'}:
            issue['code'] = 'media_attached_native_field'
    report = {'schema_version': '1.0', 'native_folder': base.rstrip('/'), 'scene_id': bundle.get('scene_id'),
        'counts': {'notes': sum(p.endswith('.rwnote') for p in files), 'journal_pages': sum(k[1] is not None for k in paths),
                   'documents': len(documents), 'native_tables': len(native_tables), 'rewritten_uuid_occurrences': len(rewritten),
                   'unresolved_uuid_occurrences': len(unresolved), 'map_note_references': len(placements),
                   'native_image_attachments': len(attached_media)},
        'attached_media': attached_media,
        'native_tables': native_tables, 'rewritten_links': rewritten, 'unresolved_links': unresolved,
        'placements': placements, 'issues': issues, 'source_read_errors': bundle.get('read_errors', []),
        'dependency_truncated': graph.get('truncated', False) or expanded['truncated'] or len(edges) >= 4096,
        'permissions': 'Source ownership retained in source-companion.json; native visibility defaults are unverified. Review before player use.',
        'status': 'Synthetic text/links/table passed Toolkit tests. This source conversion requires manual validation.'}
    files['conversion-report.json'] = json.dumps(report, ensure_ascii=True, indent=2).encode()
    files['source-companion.json'] = json.dumps(companion, ensure_ascii=True, indent=2).encode()
    files['INSTALL.txt'] = (f"ForgeBridge native notes: experimental source conversion\n\n"
        f"Close Arkenforge. Back up MyAssets. Copy the folder {base.rstrip('/').split('/')[-1]}\n"
        "from this ZIP's MyAssets/Encyclopedia/Notes into the EXISTING\n"
        "<Arkenforge data folder>/MyAssets/Encyclopedia/Notes directory.\n"
        "Do not move or rename the generated folder or its files: links use these exact paths.\n"
        "Do not copy reports/source-companion.json into MyAssets.\n\n"
        "Reopen the Toolkit and find the ForgeBridge scene index note.\n"
        "Verify a Crypt room, a linked rules page, Despair and Nightmare rolls.\n"
        "Review visibility before player use. Images/PDFs are references, not embedded.\n"
        "Map markers are not generated; conversion-report.json records source grid positions.\n"
        "To remove this import, close Arkenforge and move only the generated folder outside MyAssets.\n"
        "This archive includes private source content; do not publish it.\n").encode()
    return files, report


def write_companion_zip(source, dest):
    source, dest = Path(source), Path(dest)
    if source.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('Companion exceeds 64 MiB limit')
    if dest.exists() or dest.is_symlink():
        raise ValueError('Choose a new output filename')
    files, report = companion_files(json.loads(source.read_text(encoding='utf-8')))
    if sum(len(data) for data in files.values()) > 256 * 1024 * 1024:
        raise ValueError('Native package exceeds size limit')
    from forgebridge.native_dependencies import write_archive
    write_archive(dest, files)
    return report

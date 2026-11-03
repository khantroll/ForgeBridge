"""Read-only installed-content audit; writes only this validation JSON."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from forgebridge.native import Node
from forgebridge.native_map import clone
from forgebridge.nrbf import Reader

ROOT = Path(r'C:\Program Files (x86)\ArkenforgeData\MyAssets')
REPO = Path(__file__).resolve().parents[2]


def decode(data):
    reader = Reader(data)
    graph = reader.read()
    return clone(reader, graph['root_id'])


def load(path):
    return decode(path.read_bytes())


def differences(a, b, path=''):
    result = []
    if isinstance(a, Node) and isinstance(b, Node):
        for key in sorted(set(a.members) | set(b.members)):
            if key not in a.members or key not in b.members:
                result.append({'path': path + '/' + key, 'before': a.members.get(key), 'after': b.members.get(key), 'after_member_present': key in b.members})
            else:
                result.extend(differences(a.members[key], b.members[key], path + '/' + key))
    elif hasattr(a, 'items') and hasattr(b, 'items'):
        if len(a.items) != len(b.items):
            result.append({'path': path + '/length', 'before': len(a.items), 'after': len(b.items)})
        for i, (x, y) in enumerate(zip(a.items, b.items)):
            result.extend(differences(x, y, path + '/' + str(i)))
    elif a != b:
        result.append({'path': path, 'before': a, 'after': b})
    return result


def nodes(root):
    seen = set()
    def visit(value):
        if id(value) in seen:
            return
        seen.add(id(value))
        if isinstance(value, Node):
            yield value
            for child in value.members.values():
                yield from visit(child)
        elif hasattr(value, 'items'):
            for child in value.items:
                yield from visit(child)
    return list(visit(root))


def text(value):
    return ''.join(c.members['_character'] for c in value.members['_characters'].members['_items'].items)


def signature(schema):
    if isinstance(schema, dict):
        return {k: signature(v) for k, v in schema.items() if k != 'library_id'}
    if isinstance(schema, list):
        return [signature(v) for v in schema]
    return schema


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def installed(path):
    assert path.startswith('MyAssets/')
    return ROOT / path.removeprefix('MyAssets/')


result = {'scope': 'File inspection, not runtime or audible playback validation', 'playlists': [], 'songs': [], 'receipts': []}
fixture = load(REPO / 'fixtures/arkenforge-user-playlist/toolkit-empty-playlist.rwmeta')
for name in ('Ambient', 'FB MP3 Test'):
    base = ROOT / 'Playlists/FB Campaign Check' / name
    meta = load(base.with_suffix('.rwmeta'))
    playlist = load(base.with_suffix('.rwpl'))
    result['playlists'].append({
        'name': name, 'path': str(base.with_suffix('.rwpl')),
        'metadata_schema_matches_fixture': signature(meta.schema) == signature(fixture.schema),
        'previous_paths': {k: v for k, v in meta.members.items() if 'prevPath' in k},
        'song_entries': sum(n.schema['name'] == 'MusicTrackInfo' for n in nodes(playlist)),
        'metadata_sha256': sha(base.with_suffix('.rwmeta')),
        'value_differences': {k: [fixture.members[k], meta.members[k]] for k in meta.members
                              if isinstance(meta.members[k], (str, bool, int, float, type(None)))
                              and meta.members[k] != fixture.members.get(k)},
    })
audio_schema = json.loads((REPO / 'fixtures/arkenforge-user-playlist/toolkit-user-audio-meta.schema.json').read_text())['schema']
for path in sorted((ROOT / 'Audio/Songs/FB Campaign Check').glob('FB MP3 Test*.rwmeta')):
    meta = load(path)
    reader = Reader(path.with_suffix('.rwfile').read_bytes())
    reader.read()
    def resolve(value):
        return reader.objects[value['ref']] if isinstance(value, dict) and 'ref' in value else value
    tracks = [n['members'] for n in reader.objects.values() if isinstance(n, dict) and n.get('class') == 'AudioTrack']
    result['songs'].append({
        'name': meta.members['_name'], 'path': str(path),
        'schema_matches_user_audio_fixture': signature(meta.schema) == signature(audio_schema),
        'isSong': meta.members['_isSong'], 'duration': meta.members['_duration'],
        'previous_paths': {k: v for k, v in meta.members.items() if 'prevPath' in k},
        'tracks': [{
            'original_file': resolve(t['_originalFile']),
            'raw_sha256': hashlib.sha256(bytes(resolve(t['_clipRAW'])['bytes'])).hexdigest(),
        } for t in tracks],
    })
boris_path = ROOT / 'Encyclopedia/Notes/FB Campaign Check/Campaign-v2-edfc87a75fc39f64264e-7160079c8c68016e7452.rwnote'
boris = load(boris_path)
block = next(n for n in nodes(boris) if n.schema['name'] == 'ArkenNoteFieldStatBlock5e')
control = load(REPO / 'fixtures/arkenforge-5e-templates/5e-Character.rwnote')
control_block = next(n for n in nodes(control) if n.schema['name'] == 'ArkenNoteFieldStatBlock5e')
result['boris'] = {
    'path': str(boris_path), 'sha256': sha(boris_path),
    'block_schema_matches_fixture': signature(block.schema) == signature(control_block.schema),
    'text': {k: text(block.members[k]) for k in ('_armorClassText', '_speedText', '_languagesText', '_proficiencyBonusText')},
    'actions': [text(v) for v in block.members['_actions'].members['_items'].items],
    'field_active': {k: v for k, v in block.members.items() if k.endswith('FieldActive')},
    'expected_differences': 'Filled actor values, portrait and actions replace generic template defaults; same typed stat-block declaration.',
}
map_path = ROOT / "Maps/FB Campaign Check/Count's Lair.rwmap"
native_map = load(map_path)
tokens = []
markers = []
for n in nodes(native_map):
    if n.schema['name'] != 'ArkenMapTileUpgradeBase':
        continue
    info = n.members['_tileInfo'].members
    reference = info.get('_contentBasePath', '') or ''
    if '/ForgeBridgeTokens/' not in reference:
        if n.members['_placementType'].members['value__'] == 14:
            markers.append(info['_name'])
        continue
    note = load(installed(reference).with_suffix('.rwnote'))
    fields = [v.schema['name'] for v in nodes(note) if v.schema['name'].startswith('ArkenNoteField')]
    icon = note.members['_noteIcon'].members['_iconPath']
    tokens.append({'name': info['_name'], 'hidden': info['_hidden'],
                   'position': info['_position'].members, 'reference': reference,
                   'fields': fields, 'icon': icon, 'icon_exists': installed(icon).exists()})
result['map'] = {'path': str(map_path), 'sha256': sha(map_path), 'tokens': tokens,
                 'token_count': len(tokens), 'hidden_tokens': sum(t['hidden'] for t in tokens),
                 'intentional_journal_markers': markers,
                 'expected_template_difference': 'Token notes intentionally contain Size/icon rather than a 5e stat block or text/link field; actor notes are separate.'}
for ident in ('034c85bacbe7477d8b4f76713e2b2072', '0c74d4820ef94387863b38923f695505'):
    receipt_path = Path('C:/AMD/fb-backups') / ('forgebridge-' + ident) / 'uninstall.json'
    receipt = json.loads(receipt_path.read_text())
    changed = []
    missing = []
    for entry in receipt['added']:
        path = installed(entry['path'])
        if not path.is_file():
            missing.append(entry['path'])
        elif sha(path) != entry['sha256']:
            changed.append(entry['path'])
    original_zip = Path('C:/AMD') / ('fb-campaign-lair-recheck-2026-11-03/scene-001/native-package.zip' if ident.startswith('034') else 'fb-audio-playback-recheck-2026-11-03/native-package.zip')
    with ZipFile(original_zip) as archive:
        semantic_changes = {path: differences(decode(archive.read(path)), load(installed(path))) for path in changed}
    result['receipts'].append({'path': str(receipt_path), 'files': len(receipt['added']), 'missing': missing, 'changed_after_toolkit': changed, 'decoded_value_differences_from_package': semantic_changes})
result['screenshots'] = {path.name: sha(path) for path in sorted(Path(__file__).parent.glob('*.png'))}
output = Path(__file__).with_name('installed-audit.json')
output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(result, indent=2))

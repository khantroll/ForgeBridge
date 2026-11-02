"""Compare serialized token state after runtime tests; this is file evidence only."""
import hashlib
import json
from pathlib import Path
import zipfile
from forgebridge.nrbf import Reader

root = Path(__file__).parent
name = 'MyAssets/Maps/ForgeBridge Multi Scene 2026-10-16.rwmap'
saved = (Path('C:/Program Files (x86)/ArkenforgeData') / name).read_bytes()
with zipfile.ZipFile(root / 'multi-runtime-private/scene-v2.zip') as archive:
    generated = archive.read(name)
    report = json.loads(archive.read('token-report.json'))

def active_tokens(data):
    reader = Reader(data)
    graph = reader.read()
    def value(v):
        return reader.objects[v['ref']] if isinstance(v, dict) and 'ref' in v else v
    tiles = value(reader.objects[graph['root_id']]['members']['_tiles'])['members']
    presets = [value(value(t)['members']['_tileInfo'])['members'] for t in
               value(tiles['_items'])['items'][:tiles['_size']]]
    result = {}
    for token in report['tokens']:
        target = token['placement']['target']
        matches = [p for p in presets if value(p.get('_contentBasePath')) == target]
        assert len(matches) == 1, target
        p = matches[0]
        result[token['source_id']] = {
            'name': value(p['_tileName']), 'uid': p['_uID'],
            'position': value(p['_position'])['members'],
            'scale': value(p['_scale'])['members'],
            'rotation': p['_rotation'], 'hidden': p['_hidden']}
    return result

before, after = active_tokens(generated), active_tokens(saved)
assert before == after, (before, after)
result = {'scope': 'File comparison only; runtime observations are in VALIDATION.md',
          'saved_map_sha256': hashlib.sha256(saved).hexdigest(),
          'generated_map_sha256': hashlib.sha256(generated).hexdigest(),
          'generated_token_count': len(after), 'token_fields_equal': True,
          'tokens': after}
(root / 'saved-multi-audit.json').write_text(json.dumps(result, indent=2) + '\n', newline='\n')
print(json.dumps(result, indent=2))

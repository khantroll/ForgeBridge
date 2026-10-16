"""Read saved validation artifacts; this script makes no runtime PASS claims."""
from pathlib import Path
import hashlib
import json
import zipfile
from forgebridge.nrbf import Reader

ROOT = Path(__file__).parent
DATA = Path('C:/Program Files (x86)/ArkenforgeData')

def inspect_map(path):
    raw = path.read_bytes()
    reader = Reader(raw)
    reader.read()
    def value(x):
        return reader.objects[x['ref']] if isinstance(x, dict) and 'ref' in x else x
    tokens, animations = [], []
    for obj in reader.objects.values():
        if not isinstance(obj, dict):
            continue
        members = obj.get('members', {})
        if obj.get('class') == 'ArkenTilePresetContentLink':
            name = value(members['_tileName'])
            if name in ('Stoker', 'Stoker_token_1'):
                tokens.append({'name': name, 'position': value(members['_position'])['members'],
                               'scale': value(members['_scale'])['members']})
        if obj.get('class') == 'TileAnimationProperties' and members.get('_noOfFrames', 0) > 0:
            animations.append(members)
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'tokens': tokens,
            'animation_properties': animations}

result = {'scope': 'file inspection only; runtime observations are in VALIDATION.md',
          'packages': {}, 'saved_maps': {}}
preflight = json.loads((ROOT / 'runtime-install-preflight.json').read_text())
for name, prior in preflight.items():
    package = ROOT / name
    raw = package.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == prior['sha256']
    parsed = 0
    refs = 0
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        for name_in_zip in sorted(names):
            if not name_in_zip.endswith(('.rwmap', '.rwmeta', '.rwnote', '.rwfile')):
                continue
            reader = Reader(archive.read(name_in_zip), max_items=64000000)
            reader.read()
            parsed += 1
            for obj in reader.objects.values():
                if isinstance(obj, str) and obj.startswith('MyAssets/') and obj.endswith('.rwmeta'):
                    assert obj in names, (name_in_zip, obj)
                    refs += 1
    result['packages'][name] = {'sha256': digest, 'bytes': len(raw),
                              'native_files_parsed': parsed, 'closed_metadata_references': refs}
for name in ('ForgeBridge Token Slice 2026-10-16', 'ForgeBridge Runtime 2026-10-15 Blank',
             'ForgeBridge Fresh Combined 2026-10-16'):
    result['saved_maps'][name] = inspect_map(DATA / 'MyAssets' / 'Maps' / (name + '.rwmap'))
installed = json.loads((ROOT / 'runtime-installed.json').read_text())
result['new_files_installed'] = len(installed)
(ROOT / 'runtime-file-audit.json').write_text(json.dumps(result, indent=2) + '\n', newline='\n')
print(json.dumps(result, indent=2))

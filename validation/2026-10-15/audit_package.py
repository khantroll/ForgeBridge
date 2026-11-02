"""Read-only validation of generated native package; no Toolkit runtime claims."""
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
import shutil
import zipfile
from forgebridge.nrbf import inspect_nrbf

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    companion = json.loads((ROOT / 'manor-second-floor.forgebridge.json').read_text(encoding='utf8'))
    previous = json.loads((REPO / 'counts_manor_second_floor_test.forgebridge.json').read_text(encoding='utf8'))
    assert companion['source_scene'] == previous['source_scene']
    with zipfile.ZipFile(ROOT / 'manor-second-floor-validation.zip') as archive:
        assert archive.testzip() is None
        files = {n: archive.read(n) for n in archive.namelist() if not n.endswith('/')}
        assert len(files) == len(set(files))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n for n in files)
    report = json.loads(files['conversion-report.json'])
    native = {n: inspect_nrbf(data, max_items=64 * 1024 * 1024) for n, data in files.items() if n.endswith(('.rwmap', '.rwmeta', '.rwnote', '.rwfile'))}
    targets = []
    for graph in native.values():
        for obj in graph['objects'].values():
            if isinstance(obj, str) and obj.startswith('MyAssets/') and obj.endswith('.rwmeta'):
                targets.append(obj)
    assert all(t in files for t in targets), sorted(set(targets) - files.keys())
    assert all(p['target'] in files for p in report['placements'])
    assert all(a['note'] in files and a['target'] in files for a in report['attached_media'])
    with zipfile.ZipFile(REPO / 'MyAssets(1).zip') as template:
        preserved = [n for n in template.namelist() if n.startswith('MyAssets/Media/') and not n.endswith('/')]
        assert all(files[n] == template.read(n) for n in preserved)
    source = files['source.forgebridge.json'] if 'source.forgebridge.json' in files else None
    retained = [n for n in files if n.endswith('.json') and json.loads(files[n]) == companion]
    assert retained, 'Semantically identical companion not found'
    scene = companion['source_scene']
    token_dir = ROOT / 'token-import-assets'
    token_dir.mkdir(exist_ok=True)
    token_rows = []
    for token in scene.get('tokens', []):
        ref = token['texture']['src']
        prefix = 'modules/lob-counts_manor-pk-v13/'
        assert ref.startswith(prefix)
        relative = PurePosixPath(ref[len(prefix):])
        assert '..' not in relative.parts
        asset = REPO / 'lob-counts_manor-pk-v13' / relative
        data = asset.read_bytes()
        dest = token_dir / asset.name
        if dest.exists():
            assert dest.read_bytes() == data
        else:
            dest.write_bytes(data)
        token_rows.append({'name': token['name'], 'source': ref, 'sha256': digest(data), 'source_x': token['x'], 'source_y': token['y'], 'width_grid': token['width'], 'height_grid': token['height'], 'texture_scale': [token['texture']['scaleX'], token['texture']['scaleY']], 'native_conversion': 'not implemented; loose asset for separate UI import'})
    result = {'scope': 'FILE LEVEL ONLY; Arkenforge not observed', 'zip_crc': 'PASS', 'native_parse': 'PASS', 'native_files': len(native), 'metadata_references_checked': len(targets), 'target_closure': 'PASS', 'template_media_byte_preservation': 'PASS', 'preserved_template_media_files': len(preserved), 'fresh_source_matches_previous_scene': 'PASS', 'retained_companion': retained, 'map': report['native_map'], 'counts': report['counts'], 'source_read_errors': report['source_read_errors'], 'unresolved_links': report['unresolved_links'], 'source_media_statuses': dict(Counter(r['status'] for r in report['source_media'])), 'tokens': token_rows, 'fog_source': scene.get('fog'), 'animations_in_source': [str(p.relative_to(REPO)) for p in (REPO / 'lob-counts_manor-pk-v13').rglob('*') if p.suffix.lower() in ('.gif', '.mp4', '.m4v', '.webm')], 'input_sha256': {n: digest((REPO/n).read_bytes()) for n in ['MyAssets(1).zip', 'FB_Media_notes.zip', 'counts_manor_second_floor_test.forgebridge.json']}, 'package_sha256': digest((ROOT/'manor-second-floor-validation.zip').read_bytes())}
    (ROOT / 'file-audit.json').write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()


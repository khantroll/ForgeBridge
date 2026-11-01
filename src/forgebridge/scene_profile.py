"""Versioned, hash-bound scene calibration; read-only preflight, no installation.

Native controls are reusable schemas. Geometry/calibration belong to one source
scene. A pinned hash records provenance, never an Arkenforge runtime result.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re

from forgebridge.inventory import inventory_path
from forgebridge.native_dependencies import read_export, merge_native, check_metadata_references
from forgebridge.nrbf import Reader
from forgebridge.uvtt import _load_scene_payload
from forgebridge.validate import InventoryFatal

FORMAT = 'forgebridge.scene-profile'
MANUAL_STEPS = [
    'Native UVTT import, save/export and scene-specific origin/grid calibration',
    'Reviewed installation: back up user content; copy only absent/identical files; stop on conflicts',
    'Manual GIF import and FPS setup; procedural light animation is not converted',
    'Bounded native fog reveal/hide human gesture and persistence/player check remain deferred',
    'Labels off; Foundry vision/fog, actor/stat/combat behavior remain unmapped',
]


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def fingerprint(path):
    """Hash file bytes or a sorted directory manifest; reject links and bound IO."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError('Profile inputs must not be symlinks: ' + str(path))
    if path.is_file():
        if path.stat().st_size > 256 * 1024 * 1024:
            raise ValueError('Profile input exceeds 256 MiB: ' + str(path))
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        return digest.hexdigest()
    if not path.is_dir():
        raise ValueError('Profile input is missing: ' + str(path))
    rows, total = [], 0
    base = path.resolve()
    # Do not traverse junctions or symlink directories, including empty ones.
    pending = [path]
    entries = 0
    while pending:
        for child in sorted(pending.pop().iterdir()):
            entries += 1
            if entries > 50000 or child.is_symlink() or not child.resolve().is_relative_to(base):
                raise ValueError('Linked, escaping or oversized package tree: ' + str(child))
            if child.is_dir():
                pending.append(child)
            elif child.is_file():
                total += child.stat().st_size
                if total > 1024 * 1024 * 1024:
                    raise ValueError('Profile package exceeds 1 GiB')
                rows.append([child.relative_to(path).as_posix(), fingerprint(child)])
            else:
                raise ValueError('Unsupported profile input: ' + str(child))
    return canonical_hash(sorted(rows))


def _keys(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        raise ValueError('Invalid profile fields; expected ' + ', '.join(required))


def _text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 2048:
        raise ValueError('Profile requires ' + field)
    return value


def _json(path):
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('Profile JSON exceeds 64 MiB')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def _validate_shape(p):
    _keys(p, ('format', 'version', 'source', 'geometry', 'controls', 'output', 'options'))
    if p['format'] != FORMAT or type(p['version']) is not int or p['version'] != 1:
        raise ValueError('Unsupported scene-profile format/version; expected version 1')
    _keys(p['source'], ('package_id', 'scene_id', 'package', 'companion', 'scene_sha256'), ('selector',))
    if p['source'].get('selector') is not None:
        _keys(p['source']['selector'], ('source_path', 'parent_adventure_id'))
    for key in ('package_id', 'scene_id'):
        _text(p['source'][key], 'source.' + key)
    _keys(p['geometry'], ('export', 'map_path', 'calibration'))
    _text(p['geometry']['map_path'], 'geometry.map_path (primary map in export)')
    c = p['geometry']['calibration']
    _keys(c, ('package_id', 'scene_id', 'scene_sha256', 'geometry_sha256', 'map_path',
              'origin', 'units_per_grid', 'evidence'), ('selector',))
    _text(c['evidence'], 'calibration.evidence (manual measurement/export record)')
    if not isinstance(c['origin'], list) or len(c['origin']) != 2:
        raise ValueError('Calibration origin must have two finite native coordinates')
    for n in [*c['origin'], c['units_per_grid']]:
        if type(n) not in (int, float) or not math.isfinite(n):
            raise ValueError('Calibration values must be finite numbers')
    if c['units_per_grid'] <= 0:
        raise ValueError('Calibration units_per_grid must be positive')
    _keys(p['controls'], ('marker', 'media', 'token'))
    _keys(p['controls']['marker'], ('input', 'name'))
    _keys(p['controls']['media'], ('input',))
    _text(p['controls']['marker']['name'], 'marker.name')
    token = p['controls']['token']
    if token is not None:
        _keys(token, ('input', 'name', 'units_per_size_square'))
        _text(token['name'], 'token.name')
        n = token['units_per_size_square']
        if type(n) not in (int, float) or not math.isfinite(n) or n <= 0:
            raise ValueError('Token units_per_size_square must be finite and positive')
    _keys(p['output'], ('map_name', 'note_namespace'))
    for key, limit in [('map_name', 128), ('note_namespace', 120)]:
        name = _text(p['output'][key], 'output.' + key)
        if (len(name) > limit or re.search(r'[<>:"/\\|?*\x00-\x1f]', name)
                or name.endswith(('.', ' ')) or name.split('.')[0].upper() in
                {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}):
            raise ValueError('Output names must be portable single names: ' + key)
    _keys(p['options'], ('pdf_pages',))
    if type(p['options']['pdf_pages']) is not bool:
        raise ValueError('options.pdf_pages must be boolean')


def _inputs(p):
    rows = [('source.package', p['source']['package']),
            ('source.companion', p['source']['companion']), ('geometry.export', p['geometry']['export'])]
    rows += [('controls.' + key, value['input']) for key, value in p['controls'].items() if value is not None]
    return rows


def _source_identity(p, paths):
    package = paths['source.package']
    if not package.is_dir():
        raise ValueError('Scene-profile v1 requires an unpacked original source package directory')
    try:
        inventory = inventory_path(package)
    except InventoryFatal as exc:
        raise ValueError('Cannot verify profile source package: ' + str(exc)) from exc
    if inventory['provenance']['package_id'] != p['source']['package_id']:
        raise ValueError('Source package identity mismatch; select the matching original package')
    scene_id = p['source']['scene_id']
    matches = [d for d in inventory['documents'] if d.get('document_type') == 'Scene' and d.get('id') == scene_id]
    selector = p['source'].get('selector')
    if selector is not None:
        from forgebridge.uvtt import _parent_adventure_id
        matches = [d for d in matches if d.get('source_path') == selector['source_path']
                   and _parent_adventure_id(d) == selector['parent_adventure_id']]
    if len(matches) != 1:
        raise ValueError('Source scene identity is missing or ambiguous; select one exact scene')
    try:
        scene = _load_scene_payload(package, matches[0], scene_id)
    except InventoryFatal as exc:
        raise ValueError('Cannot verify profile source scene: ' + str(exc)) from exc
    companion = _json(paths['source.companion'])
    if selector is not None:
        for journal in companion.get('scene_notes', {}).get('journals', []):
            origin = journal.get('source', {})
            if origin.get('parent_adventure_id') is not None and any(
                    origin.get(key) != selector[key] for key in ('source_path', 'parent_adventure_id')):
                raise ValueError('Companion journal scope mismatch; regenerate it from the selected Adventure')
    if (companion.get('scene_id') != scene_id or companion.get('scene_notes', {}).get('scene_id') != scene_id
            or companion.get('source_scene', {}).get('_id') != scene_id
            or canonical_hash(companion['source_scene']) != canonical_hash(scene)):
        raise ValueError('Companion/source scene mismatch; regenerate the companion from the selected package/scene')
    return companion, canonical_hash(scene)


def load_profile(path):
    path = Path(path).absolute()
    p = _json(path)
    _validate_shape(p)
    paths, checked = {}, {}
    for role, item in _inputs(p):
        _keys(item, ('path', 'sha256'))
        ref = _text(item['path'], role + '.path')
        if not isinstance(item['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', item['sha256']):
            raise ValueError('Profile needs pinned SHA256 for ' + role)
        target = path.parent / ref
        digest = fingerprint(target)
        if digest != item['sha256']:
            raise ValueError(f'{role} hash mismatch: expected {item["sha256"]}, got {digest}. '
                             'Restore the pinned input or regenerate the companion, recheck calibration and explicitly capture a new profile.')
        paths[role], checked[role] = target, digest
    companion, digest = _source_identity(p, paths)
    c = p['geometry']['calibration']
    if (digest != p['source']['scene_sha256'] or any(c[k] != p['source'][k]
            for k in ('package_id', 'scene_id', 'scene_sha256'))
            or c.get('selector') != p['source'].get('selector') or c['map_path'] != p['geometry']['map_path']
            or c['geometry_sha256'] != checked['geometry.export']):
        raise ValueError('Calibration binding mismatch; measure this exact scene/export and capture its own calibration')
    return p, paths, companion


def capture_profile(draft_path, destination):
    """Explicitly pin a manually authored scene binding; never infer calibration."""
    draft_path, destination = Path(draft_path).absolute(), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError('Choose a new profile output filename')
    p = _json(draft_path)
    _validate_shape(p)
    paths = {}
    for role, item in _inputs(p):
        _keys(item, ('path', 'sha256'))
        paths[role] = draft_path.parent / _text(item['path'], role + '.path')
    _, digest = _source_identity(p, paths)
    if destination.resolve().is_relative_to(paths['source.package'].resolve()):
        raise ValueError('Write profiles outside the pinned original package directory')
    c = p['geometry']['calibration']
    if (any(c[k] != p['source'][k] for k in ('package_id', 'scene_id'))
            or c.get('selector') != p['source'].get('selector') or c['map_path'] != p['geometry']['map_path']):
        raise ValueError('Calibration belongs to another package/scene; do not reuse its geometry/origin/scale')
    for role, item in _inputs(p):
        item['sha256'] = fingerprint(paths[role])
        # Preserve relocatable references when capturing to a different directory.
        import os
        item['path'] = Path(os.path.relpath(paths[role], destination.absolute().parent)).as_posix()
    p['source']['scene_sha256'] = c['scene_sha256'] = digest
    c['geometry_sha256'] = p['geometry']['export']['sha256']
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(p, stream, indent=2, allow_nan=False)
        stream.write('\n')
    return p


def profile_settings(p, paths, overrides=None):
    p = deepcopy(p)
    for key, value in (overrides or {}).items():
        if key in ('name', 'note_folder'):
            p['output']['map_name' if key == 'name' else 'note_namespace'] = value
        elif key == 'pdf_pages':
            p['options']['pdf_pages'] = value
        else:
            raise ValueError('Profile does not allow override: ' + key)
    _validate_shape(p)
    scope = canonical_hash([p['source']['package_id'], p['source']['scene_id'], p['source'].get('selector'),
                            p['output']['map_name'], p['output']['note_namespace']])[:20]
    c, controls = p['geometry']['calibration'], p['controls']
    settings = dict(companion=paths['source.companion'], package=paths['source.package'],
        map_template=paths['geometry.export'], media_template=paths['controls.media'],
        geometry_map_path=p['geometry']['map_path'],
        marker_template_pack=paths['controls.marker'], template_name=controls['marker']['name'],
        name=p['output']['map_name'], note_folder=p['output']['note_namespace'] + '-' + scope,
        units_per_grid=c['units_per_grid'], origin=tuple(c['origin']), pdf_pages=p['options']['pdf_pages'],
        asset_namespace=scope, token_namespace=scope)
    if controls['token'] is not None:
        settings.update(token_control_pack=paths['controls.token'], token_control_name=controls['token']['name'],
                        control_units_per_grid=controls['token']['units_per_size_square'])
    provenance = {'format': FORMAT, 'version': 1, 'profile_sha256': canonical_hash(p),
        'source': p['source'], 'geometry': p['geometry'], 'controls': p['controls'],
        'output': p['output'], 'effective_note_folder': settings['note_folder'], 'scope': scope,
        'options': p['options'], 'runtime_validation': 'not established by profile or input hashes'}
    return settings, provenance


def preflight_profile(path, overrides=None, *, plan=None):
    """Read inputs/compile control probes in memory; no files or settings changed."""
    from forgebridge.native_export import companion_files
    from forgebridge.native_map import insert_markers
    from forgebridge.native_tokens import compile_scene_tokens
    from forgebridge.handouts import PackageMedia, media_references
    p, paths, source = load_profile(path)
    settings, provenance = profile_settings(p, paths, overrides)
    provenance['profile_file_sha256'] = fingerprint(path)
    provenance['profile_hash_method'] = 'profile_sha256 is canonical effective JSON, including allowed overrides'
    exports = {role: read_export(target) for role, target in paths.items()
               if role.startswith('controls.') or role == 'geometry.export'}
    def one_map(role):
        matches = [n for n in exports[role] if n.endswith('.rwmap')]
        if role == 'geometry.export':
            selected = p['geometry']['map_path']
            if selected not in matches or selected[:-6]+'.rwmeta' not in exports[role]:
                raise ValueError('Selected primary geometry map/metadata is missing from export')
            return selected
        if len(matches) != 1:
            raise ValueError(role + ' must contain one saved native map')
        return matches[0]
    map_name = one_map('geometry.export')
    native = dict(exports['geometry.export'])
    # Media/marker controls supply schemas, not installed original notes/assets.
    # The token control's original note/map backlink dependencies are preserved.
    for role in ('controls.token',):
        if role in exports:
            merge_native(native, exports[role])
    references = check_metadata_references(native)
    from forgebridge.native_media import media_smoke_files
    media_smoke_files(paths['controls.media'])
    # Parse control files inertly, including the media payloads.
    for files in exports.values():
        for data in files.values():
            Reader(data, max_items=64000000).read()
    marker_files, report = companion_files(source, note_folder=settings['note_folder'], map_markers=True)
    updated, _ = insert_markers(native[map_name], report['placements'], name=settings['name'],
        origin=settings['origin'], units_per_grid=settings['units_per_grid'], template_name=settings['template_name'],
        template_data=exports['controls.marker'][one_map('controls.marker')])
    if any(n.endswith('/' + settings['name'] + ext) for n in native for ext in ('.rwmap', '.rwmeta')):
        raise ValueError('Output map name collides with preserved native content; choose a distinct name')
    merge_native(native, marker_files)
    rows, rejected = [], []
    if p['controls']['token'] is not None:
        updated, generated, rows, rejected = compile_scene_tokens(updated, source['source_scene'], settings['package'],
            exports['controls.token'], one_map('controls.token'), name=settings['name'], origin=settings['origin'],
            units_per_grid=settings['units_per_grid'], control_name=settings['token_control_name'],
            control_units_per_grid=settings['control_units_per_grid'], namespace=settings['token_namespace'])
        merge_native(native, generated)
    elif source['source_scene'].get('tokens'):
        raise ValueError('Scene has tokens but profile has no token control; supply a validated control')
    native[map_name] = updated
    check_metadata_references(native)
    media = PackageMedia(settings['package'])
    try:
        gaps = [{'ref': ref, **row} for ref in media_references(source)
                if (row := media.read(ref)[0]).get('status') != 'copied']
    finally:
        media.close()
    if plan is not None:
        # In-memory batch planning only: no archive, rendering or output writes.
        # Schema-only marker/media controls are deliberately excluded. The builder
        # preserves the original geometry and adds a separately named output map.
        plan.update(profile=p, paths=paths, source=source, note_report=report,
                    native={n: data for n, data in native.items()
                            if n.startswith('MyAssets/')},
                    output_map=str(PurePosixPath(map_name).parent) + '/' + settings['name'])
        plan['native'][map_name] = exports['geometry.export'][map_name]
    return {'status': 'PASS', 'scope': 'read-only input/dependency/control preflight; no package or runtime validation',
        'provenance': provenance, 'closed_input_metadata_references': references,
        'supported_tokens': len(rows), 'rejected_tokens': rejected, 'source_media_gaps': gaps,
        'manual_steps': MANUAL_STEPS}, settings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', required=True, help='Manually bound draft JSON; hashes may be empty')
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    capture_profile(args.capture, args.out)
    print('Pinned profile inputs. Run forgebridge.package --profile PROFILE --preflight before building.')


if __name__ == '__main__':
    main()

"""Portable, inert capture of native exports and pinned scene-profile inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

from forgebridge.native_dependencies import read_export, merge_native
from forgebridge.nrbf import Reader
from forgebridge.scene_profile import load_profile, fingerprint, _inputs


def safe_name(name):
    parts = name.split('/')
    reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{p}{n}' for p in ('COM', 'LPT') for n in range(1, 10)}
    if (not name.startswith('MyAssets/') or '\\' in name or ':' in name
            or any(not p or p in ('.', '..') or p.endswith((' ', '.'))
                   or any(ord(c) < 32 or c in '<>"|?*' for c in p)
                   or p.split('.')[0].upper() in reserved for p in parts)):
        raise ValueError('Unsafe native path: ' + name)
    return name


def checked_export(path):
    with zipfile.ZipFile(path) as z:
        if any((i.external_attr >> 16) & 0o170000 == 0o120000 for i in z.infolist()):
            raise ValueError('Native export contains a symbolic link')
    files = read_export(path)
    seen = set()
    for name in files:
        safe_name(name)
        if name.casefold() in seen:
            raise ValueError('Case-conflicting native paths: ' + name)
        seen.add(name.casefold())
    return files


def native_references(data, origin):
    """Fail closed on native paths outside the dependency formats we can parse."""
    reader = Reader(data, max_items=64000000)
    reader.read()
    references = set()
    for value in reader.objects.values():
        if isinstance(value, str) and value.casefold().startswith(('myassets/', 'myassets\\')):
            safe_name(value)
            if not value.endswith(('.rwmeta', '.rwmap', '.rwnote', '.rwfile')):
                raise ValueError('Unsupported native dependency in ' + origin + ': ' + value
                                 + '; export a supported native control or extend the dependency parser')
            references.add(value)
    return sorted(references)


def dependency_closure(files, primary=None):
    maps = sorted(n for n in files if n.endswith('.rwmap'))
    if primary is None:
        if len(maps) != 1:
            raise ValueError('Select --map explicitly; export contains ' + str(len(maps)) + ' maps')
        primary = maps[0]
    safe_name(primary)
    if primary not in maps:
        raise ValueError('Selected map is missing: ' + primary)
    pending = [primary, primary[:-6] + '.rwmeta']
    found, edges, missing = {}, [], set()
    while pending:
        name = pending.pop()
        safe_name(name)
        if name in found:
            continue
        if name not in files:
            missing.add(name)
            continue
        data = found[name] = files[name]
        for value in native_references(data, name):
            edges.append({'from': name, 'to': value})
            pending.append(value)
        if name.endswith('.rwmeta'):
            siblings = [name[:-7] + suffix for suffix in ('.rwmap', '.rwnote', '.rwfile')]
            pending.extend(n for n in siblings if n in files)
            if not any(n in files for n in siblings):
                missing.add(name[:-7] + '.[rwmap|rwnote|rwfile]')
    if missing:
        raise ValueError('Missing native dependencies: ' + ', '.join(sorted(missing)))
    return primary, found, sorted(edges, key=lambda e: (e['from'], e['to']))


def _remove_owned(path, parent):
    if path.is_symlink() or path.resolve() != parent.resolve() / path.name:
        raise ValueError('Refusing cleanup outside the selected output parent: ' + str(path))
    shutil.rmtree(path)


def _new_output(destination, operation):
    destination = Path(destination).absolute()
    safe_name('MyAssets/' + destination.name)
    if destination.exists() or destination.is_symlink():
        raise ValueError('Refusing to overwrite output: ' + str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    parent = destination.parent.resolve()
    staging = Path(tempfile.mkdtemp(prefix='.native-capture-', dir=parent))
    try:
        result = operation(staging)
        # mkdir is exclusive: never replace an output created during capture.
        destination.mkdir()
        try:
            for child in staging.iterdir():
                target = destination / child.name
                if (not child.resolve().is_relative_to(staging.resolve())
                        or not target.resolve().is_relative_to(destination.resolve())):
                    raise ValueError('Unsafe publication path')
                shutil.move(str(child), target)
        except BaseException:
            _remove_owned(destination, parent)
            raise
        return result
    finally:
        _remove_owned(staging, parent)


def _json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def capture(exports, destination, primary=None, role='control', *, snapshot_provenance=None):
    """Capture from exports only; no installed-asset reads or runtime claims."""
    exports = list(exports)
    if not exports or len(exports) > 32:
        raise ValueError('Select between 1 and 32 native export inputs')
    files, provenance, folded = {}, [], {}
    for export in exports:
        digest = fingerprint(export)
        entries = checked_export(export)
        if fingerprint(export) != digest:
            raise ValueError('Export changed during capture: ' + str(export))
        for name in entries:
            prior = folded.setdefault(name.casefold(), name)
            if prior != name:
                raise ValueError('Case-conflicting native paths: ' + prior + ' / ' + name)
        merge_native(files, entries)
        if len(files) > 2048 or sum(map(len, files.values())) > 256 * 1024 * 1024:
            raise ValueError('Merged native dependencies exceed export limits')
        provenance.append({'filename': Path(export).name, 'sha256': digest})
    primary, selected, edges = dependency_closure(files, primary)
    manifest = {'format': 'forgebridge.native-capture', 'version': 1, 'role': role,
        'primary_map': primary, 'inputs': provenance, 'dependencies': edges,
        'files': [{'path': n, 'sha256': hashlib.sha256(d).hexdigest(), 'bytes': len(d)}
                  for n, d in sorted(selected.items())],
        'calibration': 'not inferred; scene-specific geometry requires its own calibrated profile',
        'runtime_validation': 'not performed'}
    if snapshot_provenance is not None:
        manifest['saved_snapshot'] = snapshot_provenance
    def write(stage):
        with zipfile.ZipFile(stage / 'native.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(selected.items()):
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)
        manifest['bundle_sha256'] = fingerprint(stage / 'native.zip')
        _json(stage / 'manifest.json', manifest)
        return manifest
    return _new_output(destination, write)


def portable_profile(profile, destination):
    """Copy all pinned inputs, preserving hashes, calibration and original ZIP bytes."""
    profile_digest = fingerprint(profile)
    p, paths, _ = load_profile(profile)
    destination = Path(destination).absolute()
    if any(destination.resolve().is_relative_to(path.resolve()) for path in paths.values() if path.is_dir()):
        raise ValueError('Output must be outside source inputs')
    def write(stage):
        rows = []
        for role, item in _inputs(p):
            source = paths[role]
            target = stage / 'inputs' / role / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copyfile(source, target)
            if fingerprint(target) != item['sha256'] or fingerprint(source) != item['sha256']:
                raise ValueError('Input changed during portable copy: ' + role)
            item['path'] = target.relative_to(stage).as_posix()
            rows.append({'role': role, 'path': item['path'], 'sha256': item['sha256']})
        # Controls are independent schema examples and can deliberately contain
        # different bytes at identical native paths. Never merge them into geometry.
        capture([stage / p['geometry']['export']['path']], stage / 'capture',
                p['geometry']['map_path'], role='scene-geometry')
        _json(stage / 'scene-profile.json', p)
        load_profile(stage / 'scene-profile.json')
        if fingerprint(profile) != profile_digest:
            raise ValueError('Profile changed during capture; choose stable inputs and retry')
        report = {'format': 'forgebridge.portable-profile', 'version': 1, 'inputs': rows,
                  'source_profile_sha256': profile_digest,
                  'native_controls': 'original exports kept separate from scene geometry',
                  'runtime_validation': 'not performed; existing calibration preserved without inference'}
        _json(stage / 'manifest.json', report)
        return report
    return _new_output(destination, write)


def _toolkit_closed():
    if os.name != 'nt':
        raise ValueError('Saved-map snapshot requires Windows process verification; use a native export ZIP')
    try:
        import psutil
    except ImportError as exc:
        raise ValueError('Saved-map capture requires requirements-native-capture.txt; alternatively use an exported ZIP') from exc
    try:
        names = [p.info['name'] for p in psutil.process_iter(['name'])]
    except psutil.Error as exc:
        raise ValueError('Cannot verify Toolkit is closed; use an exported ZIP') from exc
    if any(n and n.lower() == 'masterstoolkit.exe' for n in names):
        raise ValueError('Close Toolkit normally before capturing saved assets; use exported ZIPs while running')
    if not names or any(n is None for n in names):
        raise ValueError('Incomplete process-verification response; use an exported ZIP')


def capture_saved(asset_root, primary, destination, closed=False, role='scene-geometry'):
    """Read a verified closed-Toolkit snapshot, never write to installed assets."""
    if not closed:
        raise ValueError('Saved-map reads require --toolkit-closed acknowledgement')
    _toolkit_closed()
    root = Path(asset_root).resolve()
    safe_name(primary)
    if not root.is_dir() or root.name != 'MyAssets':
        raise ValueError('--asset-root must select the MyAssets directory')
    if Path(destination).resolve().is_relative_to(root):
        raise ValueError('Output must be outside installed assets')
    pending = [primary, primary[:-6] + '.rwmeta']
    files = {}
    def source(name):
        safe_name(name)
        path = root.parent / name
        if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('Unsafe saved-asset path: ' + name)
        return path
    while pending:
        name = pending.pop()
        if name in files:
            continue
        path = source(name)
        if not path.is_file():
            raise ValueError('Missing native dependency: ' + name)
        if len(files) >= 2048 or path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('Saved snapshot exceeds native export limits')
        data = files[name] = path.read_bytes()
        if sum(map(len, files.values())) > 256 * 1024 * 1024:
            raise ValueError('Saved snapshot exceeds byte limit')
        pending.extend(native_references(data, name))
        if name.endswith('.rwmeta'):
            pending.extend(name[:-7] + ext for ext in ('.rwmap', '.rwnote', '.rwfile')
                           if source(name[:-7] + ext).is_file())
    _toolkit_closed()
    if any(source(n).read_bytes() != data for n, data in files.items()):
        raise ValueError('Saved assets changed during snapshot; close Toolkit and retry')
    _toolkit_closed()
    with tempfile.TemporaryDirectory() as tmp:
        export = Path(tmp) / 'closed-toolkit-snapshot.zip'
        with zipfile.ZipFile(export, 'w') as z:
            for n, data in sorted(files.items()):
                z.writestr(n, data)
        return capture([export], destination, primary, role, snapshot_provenance={
            'asset_root': str(root), 'toolkit_closed_checks': 3,
            'consistency': 'all captured files reread byte-for-byte before emission',
            'installation_modified': False})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--export', action='append', help='Native export ZIP; repeat for dependencies')
    source.add_argument('--profile', help='Pinned scene profile: copy and rebase all inputs')
    source.add_argument('--asset-root', help='Explicit MyAssets directory; Toolkit must be closed')
    parser.add_argument('--toolkit-closed', action='store_true', help='Acknowledge Toolkit is closed for snapshot reads')
    parser.add_argument('--map', help='Exact MyAssets map path; required for ambiguous exports')
    parser.add_argument('--role', choices=('control', 'scene-geometry'), default='control')
    parser.add_argument('--out', required=True, help='New output directory; never overwritten')
    args = parser.parse_args(argv)
    if args.profile and args.map:
        parser.error('--map is only valid with --export')
    if args.asset_root and not args.map:
        parser.error('--asset-root requires an explicitly selected --map')
    if args.toolkit_closed and not args.asset_root:
        parser.error('--toolkit-closed requires --asset-root')
    try:
        if args.asset_root:
            result = capture_saved(args.asset_root, args.map, args.out, args.toolkit_closed, args.role)
        else:
            result = portable_profile(args.profile, args.out) if args.profile else capture(args.export, args.out, args.map, args.role)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

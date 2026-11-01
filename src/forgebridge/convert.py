"""Discover Foundry scenes and export reviewable packages through existing adapters."""
import argparse
import hashlib
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

from forgebridge.inventory import inventory_path
from forgebridge.native_dependencies import write_member
from forgebridge.notes import render_notes_text
from forgebridge.package import build_package
from forgebridge.scene_profile import fingerprint, preflight_profile
from forgebridge.uvtt import (_safe_extract_zip, _slice_directory, _parent_adventure_id,
                              _scene_asset_action, _safe_ref, _package_file, MAX_ENTRY_BYTES)
from forgebridge.validate import InventoryFatal, load_schema, repo_schema, validate


@contextmanager
def source_root(package):
    package = Path(package).absolute()
    if any(p.is_symlink() or p.is_junction() for p in (package, *package.parents)):
        raise ValueError('Source path must not contain links or junctions')
    if package.is_dir():
        yield package, []
    elif package.is_file() and package.suffix.lower() == '.zip':
        with tempfile.TemporaryDirectory(prefix='forgebridge-source-') as tmp:
            root, rejected = _safe_extract_zip(package, Path(tmp))
            yield root, rejected
    else:
        raise ValueError('Select a Foundry package directory or ZIP')


def _identity(row):
    return (row.get('id'), row.get('source_path'), _parent_adventure_id(row))


def scene_key(row):
    return hashlib.sha256(json.dumps(_identity(row)).encode()).hexdigest()[:24]


def discover(package):
    """Read-only discovery used by CLI and GUI; no native calibration inference."""
    with source_root(package) as (root, _):
        inventory = inventory_path(root)
        return {'package_id': inventory['provenance']['package_id'],
                'scenes': [{'key': scene_key(row), 'id': row.get('id'), 'name': row.get('name'),
                            'source_path': row.get('source_path'),
                            'parent_adventure_id': _parent_adventure_id(row)}
                           for row in inventory['documents'] if row.get('document_type') == 'Scene']}


def _new_destination(destination, package):
    dest = Path(destination).absolute()
    if any(p.is_symlink() or p.is_junction() for p in (dest, *dest.parents)):
        raise ValueError('Output must not contain links/junctions')
    if dest.exists() or not dest.parent.is_dir():
        raise ValueError('Choose a new output directory under an existing parent')
    package = Path(package).absolute()
    if package.is_dir() and dest.resolve().is_relative_to(package.resolve()):
        raise ValueError('Output must be outside the source package')
    return dest


def convert(package, destination, *, scene_ids=(), scene_keys=(), profiles=()):
    package = Path(package).absolute()
    dest = _new_destination(destination, package)
    before = fingerprint(package)
    report = {'format': 'forgebridge.conversion', 'version': 1, 'status': 'PASS',
              'source_sha256': before, 'scenes': [], 'counts': {g: 0 for g in
                  ('native', 'approximate', 'manual', 'unsupported')},
              'runtime_validation': 'not performed', 'installed': False,
              'native_synthesis': 'pending A0; no target origin/scale inferred',
              'manual_steps': ['Without a matching calibrated profile, import each scene.uvtt in Toolkit; '
                               'native export/calibration and profile capture are still needed for the native stage',
                               'Review losses and installation conflicts; labels off; GIF/FPS setup remains manual']}
    with source_root(package) as (root, rejected), tempfile.TemporaryDirectory(prefix='forgebridge-convert-') as tmp:
        inventory = inventory_path(root)
        report['package_id'] = inventory['provenance']['package_id']
        rows = [r for r in inventory['documents'] if r.get('document_type') == 'Scene']
        rows.sort(key=lambda r: tuple(str(x or '') for x in _identity(r)))
        if len({_identity(r) for r in rows}) != len(rows):
            raise ValueError('Duplicate source scene identity in one pack/Adventure; resolve before converting')
        if scene_ids and scene_keys: raise ValueError('Select by scene IDs or scoped keys, not both')
        if scene_keys:
            if set(scene_keys) - {scene_key(r) for r in rows}: raise ValueError('Scoped scene key not found')
            rows = [r for r in rows if scene_key(r) in scene_keys]
        if scene_ids:
            missing = set(scene_ids) - {r.get('id') for r in rows}
            if missing:
                raise ValueError('Scene IDs not found: ' + ', '.join(sorted(missing)))
            rows = [r for r in rows if r.get('id') in scene_ids]
        if not 1 <= len(rows) <= 256:
            raise ValueError('Package must contain between 1 and 256 selected scenes')
        native, guards = {}, []
        for profile in profiles:
            plan = {}
            audit, settings = preflight_profile(profile, plan=plan)
            guards.append((profile, audit['provenance']['profile_file_sha256'], plan))
            source = audit['provenance']['source']
            if (not package.is_dir() or fingerprint(settings['package']) != before
                    or source['package_id'] != report['package_id']):
                raise ValueError('Native profile must pin this exact unpacked source package')
            selector = source.get('selector') or {}
            matches = [r for r in rows if r.get('id') == source['scene_id'] and
                       (not selector or (r.get('source_path') == selector['source_path'] and
                                         _parent_adventure_id(r) == selector['parent_adventure_id']))]
            if len(matches) != 1 or _identity(matches[0]) in native:
                raise ValueError('Profile is missing, ambiguous, duplicated or outside selected scenes')
            native[_identity(matches[0])] = (audit, settings)
        stage = Path(tmp)
        for index, row in enumerate(rows, 1):
            folder = stage / f'scene-{index:03d}'; folder.mkdir()
            result = {'id': row.get('id'), 'name': row.get('name'),
                      'source_path': row.get('source_path'), 'parent_adventure_id': _parent_adventure_id(row),
                      'folder': folder.name}
            try:
                document = _slice_directory(root, row['id'], rejected, inventory=inventory, scene_row=row)
                for key, schema in [('uvtt', 'uvtt-core.schema.json'), ('loss_report', 'uvtt-loss-report.schema.json')]:
                    errors = validate(document[key], load_schema(repo_schema(schema)))
                    if errors: raise ValueError('Invalid ' + key + ': ' + '; '.join(errors))
                companion = {'schema_version': '1.0', 'scene_id': row['id'],
                             **{k: document[k] for k in ('source_scene', 'scene_notes', 'loss_report')}}
                files = {'scene.uvtt': json.dumps(document['uvtt'], sort_keys=True, ensure_ascii=True).encode(),
                         'scene.forgebridge.json': json.dumps(companion, sort_keys=True, ensure_ascii=True).encode(),
                         'scene.notes.txt': render_notes_text(document['scene_notes']).encode()}
                # Reuse the existing loose import policy, preserving paths instead
                # of flattening basenames and silently losing colliding files.
                for asset in inventory['assets']:
                    if _scene_asset_action(asset, row['id']) != 'copy': continue
                    safe, problem = _safe_ref(asset.get('ref'))
                    if problem or not safe: continue
                    path = _package_file(root, safe)
                    with path.open('rb') as stream: data = stream.read(MAX_ENTRY_BYTES + 1)
                    if len(data) > MAX_ENTRY_BYTES: raise ValueError('Loose asset exceeds byte limit')
                    files['source-assets/' + safe] = data
                    if sum(map(len, files.values())) > 256 * 1024 * 1024:
                        raise ValueError('Scene export exceeds 256 MiB')
                with zipfile.ZipFile(folder / 'uvtt-package.zip', 'x') as archive:
                    for name, data in sorted(files.items()): write_member(archive, name, data)
                result.update(status='MANUAL', artifact='uvtt-package.zip', loss_report=document['loss_report'])
                for grade, count in document['loss_report']['counts'].items(): report['counts'][grade] += count
                if _identity(row) in native:
                    audit, settings = native[_identity(row)]
                    conversion = build_package(**settings, dest=folder / 'native-package.zip',
                                               profile_provenance=audit['provenance'])
                    result.update(status='BUILT', artifact='native-package.zip', native_report=conversion)
            except (ValueError, OSError, InventoryFatal, zipfile.BadZipFile) as exc:
                result.update(status='REJECTED', error=str(exc))
                report['counts']['unsupported'] += 1
                report['status'] = 'PARTIAL'
            report['scenes'].append(result)
        if fingerprint(package) != before:
            raise ValueError('Source package changed during conversion; nothing published')
        # Revalidate all native inputs after compilation, without re-reading source DBs.
        from forgebridge.scene_profile import _inputs
        for profile, digest, plan in guards:
            if fingerprint(profile) != digest:
                raise ValueError('Profile changed during conversion')
            for role, item in _inputs(plan['profile']):
                if fingerprint(plan['paths'][role]) != item['sha256']:
                    raise ValueError('Pinned profile input changed during conversion')
        (stage / 'conversion-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        _new_destination(dest, package)
        dest.mkdir()
        for path in sorted(stage.rglob('*')):
            if path == stage / 'conversion-report.json': continue
            target = dest / path.relative_to(stage)
            if path.is_dir(): target.mkdir()
            else:
                with path.open('rb') as source, target.open('xb') as output: shutil.copyfileobj(source, output)
        with (stage / 'conversion-report.json').open('rb') as source, (dest / 'conversion-report.json').open('xb') as output:
            shutil.copyfileobj(source, output)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(prog='forgebridge convert', description=__doc__)
    parser.add_argument('package')
    parser.add_argument('--out')
    parser.add_argument('--list-scenes', action='store_true')
    parser.add_argument('--scene', action='append', default=[])
    parser.add_argument('--scene-key', action='append', default=[])
    parser.add_argument('--profile', action='append', default=[])
    args = parser.parse_args(argv)
    try:
        if args.list_scenes:
            report = discover(args.package)
        else:
            if not args.out: raise ValueError('Provide --out NEW_DIRECTORY or --list-scenes')
            report = convert(args.package, args.out, scene_ids=args.scene, scene_keys=args.scene_key, profiles=args.profile)
        print(json.dumps(report, indent=2))
        return 0 if report.get('status', 'PASS') == 'PASS' else 1
    except (OSError, ValueError, InventoryFatal, zipfile.BadZipFile) as exc:
        parser.exit(2, str(exc) + '\n')

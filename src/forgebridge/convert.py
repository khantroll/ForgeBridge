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
from forgebridge.native_dependencies import write_member, read_package, merge_native, check_metadata_references
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
        def adventure_name(row):
            # Inventory promotes scenes from this same parent Adventure record.
            retained = row.get('retained_fields')
            parent = retained.get('_forgebridge_parent_adventure') if isinstance(retained, dict) else None
            name = parent.get('name') if isinstance(parent, dict) else None
            return name if isinstance(name, str) and name else None
        return {'package_id': inventory['provenance']['package_id'],
                'scenes': [{'key': scene_key(row), 'id': row.get('id'), 'name': row.get('name'),
                            'source_path': row.get('source_path'),
                            'parent_adventure_id': _parent_adventure_id(row),
                            'parent_adventure_name': adventure_name(row)}
                           for row in inventory['documents'] if row.get('document_type') == 'Scene']}


def _new_destination(destination, package):
    dest = Path(destination).absolute()
    if any(p.is_symlink() or p.is_junction() for p in (dest, *dest.parents)):
        raise ValueError('Output must not contain links/junctions')
    if dest.exists():
        raise ValueError(f'Output folder already exists: {dest}. ForgeBridge never overwrites; '
                         'choose a new folder name (for example add -2).')
    if not dest.parent.is_dir():
        raise ValueError(f'The folder that should contain the output does not exist: {dest.parent}')
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
              'counts_scope': 'Source/UVTT grades; native outcomes and remaining losses are reported separately',
              'native_counts': {'scenes': 0, 'tokens': 0, 'rejected_tokens': 0, 'notes': 0, 'markers': 0},
              'native_losses': [],
              'runtime_validation': 'not performed', 'installed': False,
              'native_synthesis': 'Schema-built Toolkit 0.5.1.18 records; default calibration 2.56 units/grid, upper-left origin (0,0)',
              'manual_steps': ['Review combined losses and installation conflicts before player use; labels off',
                               'GIF/FPS setup, manual native fog and unsupported actor/vision/behavior remain manual',
                               'Generating files is not runtime validation of this output']}
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
        combined_native = {}
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
                else:
                    from forgebridge.direct_package import build_direct
                    conversion = build_direct(root, document, row, report['package_id'], folder / 'native-package.zip')
                    result.update(status='BUILT', artifact='native-package.zip', native_report=conversion)
                members = read_package(folder / 'native-package.zip')
                candidate = {n: d for n, d in members.items() if n.startswith('MyAssets/')}
                additions = {n: d for n, d in candidate.items() if n not in combined_native}
                if (len(combined_native) + len(additions) > 16384 or
                        sum(map(len, combined_native.values())) + sum(map(len, additions.values())) > 1024 * 1024 * 1024):
                    raise ValueError('Combined native output exceeds 1 GiB/16384-file limit; select fewer scenes')
                merge_native(combined_native, candidate)
            except (ValueError, OSError, InventoryFatal, zipfile.BadZipFile) as exc:
                result.update(status='REJECTED', error=str(exc))
                report['counts']['unsupported'] += 1
                report['status'] = 'PARTIAL'
            report['scenes'].append(result)
            if result.get('status') == 'BUILT':
                native_report = result['native_report']; counts = native_report['counts']
                report['native_counts']['scenes'] += 1
                for key, source in [('tokens', 'native_tokens'), ('rejected_tokens', 'unsupported_tokens'), ('notes', 'notes')]:
                    report['native_counts'][key] += counts.get(source, 0)
                report['native_counts']['markers'] += native_report['native_map']['markers']
                remaining = list(native_report.get('native_synthesis', {}).get('losses', []))
                remaining += [{'grade': 'unsupported', 'feature': 'light', **row}
                              for row in native_report.get('native_synthesis', {}).get('omitted_lights', [])]
                remaining += [{'grade': 'unsupported', 'feature': 'token', **row}
                              for row in native_report.get('token_conversion', {}).get('unsupported', [])]
                remaining += [{'grade': 'manual', 'feature': 'room-marker', **row}
                              for row in native_report.get('unplaced_markers', [])]
                remaining += [{'grade': 'manual', 'feature': 'native-attachment', **row}
                              for row in native_report.get('source_media', [])
                              if row.get('status') not in {'native_image', 'native_pdf_pages'}]
                report['native_losses'].append({'scene_id': result['id'], 'folder': result['folder'],
                    'losses': remaining, 'unresolved_links': native_report.get('unresolved_links', [])})
        report['closed_native_metadata_references'] = check_metadata_references(combined_native)
        # A directly copyable MyAssets tree, alongside per-scene archives and losses.
        for name, data in combined_native.items():
            target = stage / name; target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream: stream.write(data)
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
    parser.add_argument('--install', action='store_true', help='Explicit add-only installation after building/review checks')
    parser.add_argument('--myassets', help='Actual MyAssets destination; required with --install')
    parser.add_argument('--backup-root', help='Separate existing full-backup directory; required with --install')
    args = parser.parse_args(argv)
    try:
        if args.list_scenes:
            if args.install or args.myassets or args.backup_root:
                raise ValueError('--list-scenes is read-only; do not combine it with installation options')
            report = discover(args.package)
        else:
            if args.install and (not args.myassets or not args.backup_root):
                raise ValueError('--install requires --myassets and --backup-root')
            if not args.install and (args.myassets or args.backup_root):
                raise ValueError('Installation destinations require explicit --install')
            if not args.out and args.install:
                import uuid
                args.out = str(Path.cwd() / ('ForgeBridge-output-' + uuid.uuid4().hex[:10]))
            if not args.out: raise ValueError('Provide --out NEW_DIRECTORY, --install, or --list-scenes')
            report = convert(args.package, args.out, scene_ids=args.scene, scene_keys=args.scene_key, profiles=args.profile)
            if args.install:
                if report['status'] != 'PASS': raise ValueError('Resolve rejected scenes before installation; outputs retained for review')
                from forgebridge.installer import install_conversion
                installation = install_conversion(report, args.out, args.myassets, args.backup_root)
                report['installed'] = True; report['installation'] = installation
                with (Path(args.out) / 'installation-report.json').open('x', encoding='utf-8') as stream:
                    json.dump(installation, stream, indent=2)
                report['installation_report'] = 'installation-report.json (conversion-report.json records the pre-install build)'
        print(json.dumps(report, indent=2))
        return 0 if report.get('status', 'PASS') == 'PASS' else 1
    except (OSError, ValueError, InventoryFatal, zipfile.BadZipFile) as exc:
        parser.exit(2, str(exc) + '\n')

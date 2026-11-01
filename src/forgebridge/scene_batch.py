"""Preflight two or more pinned scene profiles together; build separate packages.

Never installs, infers calibration, or certifies Toolkit runtime behavior.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from forgebridge.native_dependencies import read_package, merge_native, check_metadata_references
from forgebridge.package import build_package
from forgebridge.scene_profile import preflight_profile, fingerprint, MANUAL_STEPS, _inputs


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _duplicates(rows):
    grouped = defaultdict(list)
    for identity, owner in rows:
        if identity is not None:
            grouped[str(identity)].append(owner)
    return [{'identity': key, 'scenes': owners, 'resolution': 'separate scene scopes'}
            for key, owners in sorted(grouped.items()) if len(set(owners)) > 1]


def preflight_batch(profiles):
    """Read-only all-scene planning. No temporary builds, PDFs or output writes."""
    profiles = list(profiles)
    if not 2 <= len(profiles) <= 32:
        raise ValueError('Provide between two and 32 scene profiles')
    report = {'format': 'forgebridge.scene-batch', 'version': 1, 'status': 'PASS',
              'scope': 'file-only; no installation or runtime validation',
              'scenes': [], 'conflicts': [], 'shared_dependencies': [],
              'duplicate_source_tokens': [], 'duplicate_source_notes': [],
              'loss_report': [], 'manual_steps': list(MANUAL_STEPS)}
    plans, names, scopes, dependencies = [], {}, {}, defaultdict(list)
    tokens, notes = [], []
    for index, profile in enumerate(profiles):
        label = f'scene-{index + 1:02d}'
        plan = {}
        try:
            audit, settings = preflight_profile(profile, plan=plan)
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            report['conflicts'].append({'scene': label, 'kind': 'invalid_profile', 'error': str(exc)})
            continue
        p, source = plan['profile'], plan['source']
        provenance = audit['provenance']
        row = {'scene': label, 'profile': str(Path(profile).absolute()),
               'provenance': provenance, 'preflight': audit,
               'output_folder': label, 'package': label + '/scene.zip'}
        report['scenes'].append(row)
        for kind, value in [('map_name', settings['name']), ('note_folder', settings['note_folder'])]:
            key = (kind, value.casefold())
            if key in names:
                report['conflicts'].append({'kind': kind, 'value': value, 'scenes': [names[key], label]})
            names[key] = label
        scope = provenance['scope']
        if scope in scopes:
            report['conflicts'].append({'kind': 'duplicate_scope', 'scenes': [scopes[scope], label]})
        scopes[scope] = label
        for name, data in plan['native'].items():
            dependencies[name.casefold()].append({'scene': label, 'path': name, 'sha256': _digest(data)})
        for token in source['source_scene'].get('tokens', []):
            tokens.append((token.get('_id'), label))
        bundle = source.get('scene_notes', {})
        for note in bundle.get('notes', []):
            notes.append((note.get('note_id'), label))
        for document in bundle.get('dependencies', {}).get('documents', []):
            notes.append((document.get('payload', {}).get('_id'), label))
        report['loss_report'].append({'scene': label,
            'source_loss_report': source.get('loss_report'),
            'source_loss_report_status': 'retained' if 'loss_report' in source else 'not supplied',
            'rejected_tokens': audit['rejected_tokens'], 'source_media_gaps': audit['source_media_gaps'],
            'note_issues': plan['note_report']['issues'],
            'unresolved_links': plan['note_report']['unresolved_links'],
            'source_read_errors': plan['note_report']['source_read_errors'],
            'dependency_truncated': plan['note_report']['dependency_truncated'],
            'limits': list(MANUAL_STEPS)})
        plans.append((profile, audit, settings, plan))
    for key, rows in sorted(dependencies.items()):
        if len({row['scene'] for row in rows}) < 2:
            continue
        if len({(row['path'], row['sha256']) for row in rows}) > 1:
            report['conflicts'].append({'kind': 'native_dependency', 'path': key, 'inputs': rows})
        else:
            report['shared_dependencies'].append({'path': rows[0]['path'], 'inputs': rows})
    # A preserved backlink/dependency must not shadow another scene's new map.
    for _, _, _, plan in plans:
        for ext in ('.rwmap', '.rwmeta'):
            target = plan['output_map'] + ext
            if target.casefold() in dependencies:
                report['conflicts'].append({'kind': 'output_dependency_collision', 'path': target,
                                            'inputs': dependencies[target.casefold()]})
    report['duplicate_source_tokens'] = _duplicates(tokens)
    report['duplicate_source_notes'] = _duplicates(notes)
    if report['conflicts']:
        report['status'] = 'FAIL'
    return report, plans


def _destination(destination, plans):
    root = Path(destination).absolute()
    # Reject aliases/junctions in existing ancestors; never create through links.
    for part in (root, *root.parents):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Output path must not contain links/junctions: ' + str(part))
    if root.exists():
        raise ValueError('Choose a new batch output folder; nothing is overwritten')
    if not root.parent.is_dir():
        raise ValueError('Batch output parent must already exist')
    for _, _, _, plan in plans:
        for path in plan['paths'].values():
            if path.is_dir() and root.resolve().is_relative_to(path.resolve()):
                raise ValueError('Batch output must be outside every input directory')
    return root


def build_batch(profiles, destination):
    report, plans = preflight_batch(profiles)
    if report['status'] != 'PASS':
        raise ValueError('Batch preflight failed: ' + json.dumps(report['conflicts']))
    root = _destination(destination, plans)
    # Build/validate everything before publishing any batch output. Temporary
    # compilation is a build operation, never part of read-only preflight.
    with tempfile.TemporaryDirectory(prefix='forgebridge-batch-') as tmp:
        stage = Path(tmp)
        combined = {}
        for row, (profile, audit, settings, _) in zip(report['scenes'], plans):
            folder = stage / row['output_folder']
            folder.mkdir()
            output = folder / 'scene.zip'
            conversion = build_package(**settings, dest=output, profile_provenance=audit['provenance'])
            native = {n: d for n, d in read_package(output).items() if n.startswith('MyAssets/')}
            merge_native(combined, native)
            row['package_sha256'] = fingerprint(output)
            row['conversion_report'] = conversion
        report['combined_closed_metadata_references'] = check_metadata_references(combined)
        # Refuse changed inputs before publishing. No retries or repinning.
        for profile, audit, _, plan in plans:
            if fingerprint(profile) != audit['provenance']['profile_file_sha256']:
                raise ValueError('Profile changed during batch build; review and start a new build')
            for role, pinned in _inputs(plan['profile']):
                if fingerprint(plan['paths'][role]) != pinned['sha256']:
                    raise ValueError(role + ' changed during batch build; restore/review the pinned input')
        report['inputs_revalidated_before_publication'] = True
        for loss, row in zip(report['loss_report'], report['scenes']):
            loss['conversion_report'] = row['conversion_report']
        # Exclusive mkdir reserves a new destination, including against races.
        # If publication IO fails, retain incomplete files for inspection; never
        # delete or overwrite a directory that another process could have edited.
        _destination(root, plans)
        root.mkdir()
        for row in report['scenes']:
            folder = root / row['output_folder']
            folder.mkdir()
            with (stage / row['package']).open('rb') as source, (folder / 'scene.zip').open('xb') as target:
                shutil.copyfileobj(source, target)
        with (root / 'batch-report.json').open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(report, stream, indent=2, ensure_ascii=True)
            stream.write('\n')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='append', required=True, help='Repeat for two or more profiles')
    parser.add_argument('--preflight', action='store_true', help='Read-only combined report; no output written')
    parser.add_argument('--out', help='New output directory under an existing parent')
    args = parser.parse_args(argv)
    try:
        if args.preflight:
            if args.out:
                raise ValueError('--preflight does not accept --out; redirect JSON stdout if desired')
            report, _ = preflight_batch(args.profile)
        else:
            if not args.out:
                raise ValueError('Provide --preflight or --out NEW_FOLDER')
            report = build_batch(args.profile, args.out)
        print(json.dumps(report, indent=2, ensure_ascii=True))
        return 0 if report['status'] == 'PASS' else 1
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

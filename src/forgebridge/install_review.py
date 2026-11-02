"""Read-only package conflict review against a user-supplied static MyAssets copy.

Never installs, writes the snapshot, or follows links. The caller must select a
static copy prepared with Toolkit closed; its origin cannot be inferred here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from forgebridge.native_dependencies import read_package, merge_native, check_metadata_references
from forgebridge.scene_profile import fingerprint


def _linked(path):
    return path.is_symlink() or path.is_junction()


def _target(root, name):
    """Inspect every existing component without following aliases or links."""
    current = root
    for part in name.split('/')[1:]:
        if current.exists():
            if not current.is_dir():
                raise ValueError('Parent is not a directory: ' + str(current))
            matches = [child for child in current.iterdir() if child.name.casefold() == part.casefold()]
            if len(matches) > 1 or (matches and matches[0].name != part):
                raise ValueError('Case-conflicting snapshot path: ' + name)
            if matches and _linked(matches[0]):
                raise ValueError('Linked snapshot path refused: ' + name)
        current = current / part
    return current


def review(packages, snapshot_root):
    root = Path(snapshot_root).absolute()
    if root.name != 'MyAssets' or not root.is_dir():
        raise ValueError('Select a static copy named MyAssets, not its parent')
    if any(_linked(p) for p in (root, *root.parents)):
        raise ValueError('Snapshot root/ancestors must not be links or junctions')
    packages = list(packages)
    if not 1 <= len(packages) <= 256:
        raise ValueError('Select between 1 and 256 packages')
    native, inputs, ignored = {}, [], []
    for package in packages:
        digest = fingerprint(package)
        files = read_package(package)
        if fingerprint(package) != digest:
            raise ValueError('Package changed during review: ' + str(package))
        merge_native(native, {n: d for n, d in files.items() if n.startswith('MyAssets/')})
        if len(native) > 16384 or sum(map(len, native.values())) > 1024 * 1024 * 1024:
            raise ValueError('Combined packages exceed review limits')
        inputs.append({'filename': Path(package).name, 'sha256': digest})
        ignored.extend({'package': Path(package).name, 'path': n}
                       for n in files if not n.startswith('MyAssets/'))
    references = check_metadata_references(native)
    rows, observed, snapshot_bytes = [], [], 0
    for name, data in sorted(native.items()):
        row = {'path': name, 'package_sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
        try:
            target = _target(root, name)
            if not target.exists():
                row['status'] = 'new'
            elif not target.is_file():
                raise ValueError('Target is not a regular file: ' + name)
            elif target.stat().st_size > 64 * 1024 * 1024:
                raise ValueError('Snapshot file exceeds review byte limit: ' + name)
            else:
                snapshot_bytes += target.stat().st_size
                if snapshot_bytes > 1024 * 1024 * 1024:
                    raise ValueError('Snapshot comparison exceeds total byte limit')
                existing = target.read_bytes()
                row['snapshot_sha256'] = hashlib.sha256(existing).hexdigest()
                row['status'] = 'identical' if existing == data else 'conflict'
            observed.append((name, row['status'], row.get('snapshot_sha256')))
        except (OSError, ValueError) as exc:
            row.update(status='blocked', detail=str(exc))
        rows.append(row)
    # A point-in-time review is not authorization to install later. Detect changes
    # during this read as well as possible, without writing locks into the copy.
    for name, status, digest in observed:
        target = _target(root, name)
        if status == 'new':
            if target.exists():
                raise ValueError('Snapshot changed during review: ' + name)
        elif (not target.is_file() or target.stat().st_size > 64 * 1024 * 1024
              or hashlib.sha256(target.read_bytes()).hexdigest() != digest):
            raise ValueError('Snapshot changed during review: ' + name)
    counts = {s: sum(r['status'] == s for r in rows) for s in ('new', 'identical', 'conflict', 'blocked')}
    return {'format': 'forgebridge.install-review', 'version': 1,
            'ok': not counts['conflict'] and not counts['blocked'], 'inputs': inputs,
            'snapshot_root': str(root), 'files': rows, 'counts': counts,
            'closed_package_metadata_references': references, 'not_installed': ignored,
            'writes': 'none; review only', 'runtime_validation': 'not performed',
            'limitations': ['Static copy must be prepared with Toolkit closed; this command does not verify its origin',
                           'Point-in-time comparison, not an installer or authorization to overwrite',
                           'Recheck the real destination with Toolkit closed before any reviewed installation']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', action='append', required=True)
    parser.add_argument('--snapshot-root', required=True, help='Static MyAssets copy prepared with Toolkit closed')
    parser.add_argument('--static-snapshot', action='store_true', required=True,
                        help='Acknowledge this is a static copy, not the running installation')
    args = parser.parse_args(argv)
    try:
        report = review(args.package, args.snapshot_root)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(2, str(exc)+'\n')
    print(json.dumps(report, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

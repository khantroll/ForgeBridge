"""Explicit add-only installation with full backup and hash-checked uninstall.

Only invoked by an operator selecting a destination. Tests use fake MyAssets.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

from forgebridge.install_review import review, _target, _linked
from forgebridge.native_dependencies import read_package, merge_native, safe_name
from forgebridge.scene_profile import fingerprint

MAX_BACKUP_BYTES = 16 * 1024 * 1024 * 1024


def require_toolkit_closed():
    """Read-only process inspection, fail closed if inspection is unavailable."""
    try:
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True,
                                    text=True, check=True, timeout=15)
            names = [row[0] for row in csv.reader(io.StringIO(result.stdout)) if row]
        else:
            result = subprocess.run(['ps', '-A', '-o', 'comm='], capture_output=True,
                                    text=True, check=True, timeout=15)
            names = result.stdout.splitlines()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError('Cannot verify Toolkit is closed; installation refused') from exc
    if not result.stdout.strip():
        raise ValueError('Empty process inventory; installation refused')
    for name in names:
        bare = name.strip().replace('\\', '/').split('/')[-1].casefold()
        if bare in {'masterstoolkit.exe', 'mastertoolkit.exe', 'masterstoolkit', 'mastertoolkit'}:
            raise ValueError('Toolkit is running; close it normally before installing/uninstalling')


def _hash(path, budget=MAX_BACKUP_BYTES):
    digest, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(block)
            if size > budget: raise ValueError('Backup byte limit exceeded')
            digest.update(block)
    return digest.hexdigest(), size


def _tree(root):
    result, total, pending, entries = {}, 0, [root], 0
    while pending:
        folder = pending.pop()
        folded = set()
        for path in sorted(folder.iterdir()):
            entries += 1
            if entries > 100000 or path.name.casefold() in folded or _linked(path):
                raise ValueError('Linked, case-aliased or oversized backup tree: ' + str(path))
            folded.add(path.name.casefold())
            if path.is_dir(): pending.append(path)
            elif path.is_file():
                digest, size = _hash(path, MAX_BACKUP_BYTES - total)
                total += size
                result[path.relative_to(root).as_posix()] = {'sha256': digest, 'bytes': size}
            else: raise ValueError('Unsupported file in MyAssets: ' + str(path))
    return result


def _json(path, value):
    # Receipts are outside MyAssets; atomic replacement only of this run's own
    # journal, never of user assets. A complete receipt gates uninstall.
    temporary = path.with_suffix('.new')
    with temporary.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')
    os.replace(temporary, path)


def install(packages, myassets, backup_root):
    require_toolkit_closed()
    root, backups = Path(myassets).absolute(), Path(backup_root).absolute()
    packages = list(packages)
    audit = review(packages, root)
    if not audit['ok']: raise ValueError('Install conflicts/blocked paths; nothing installed: ' + json.dumps(audit['counts']))
    if not backups.is_dir() or any(_linked(p) for p in (backups, *backups.parents)):
        raise ValueError('Choose an existing unlinked backup directory')
    if backups.resolve().is_relative_to(root.resolve()) or root.resolve().is_relative_to(backups.resolve()):
        raise ValueError('Backup directory and MyAssets must be separate trees')
    native = {}
    for package, pinned in zip(packages, audit['inputs']):
        if fingerprint(package) != pinned['sha256']: raise ValueError('Package changed after review')
        merge_native(native, {n: d for n, d in read_package(package).items() if n.startswith('MyAssets/')})
    lock = root.parent / '.forgebridge-install.lock'
    token = uuid.uuid4().hex
    with lock.open('x', encoding='ascii') as stream: stream.write(token)
    receipt = {'format': 'forgebridge.installation', 'version': 1, 'id': token,
               'myassets': str(root), 'state': 'INCOMPLETE', 'added': [], 'created_directories': [],
               'inputs': audit['inputs'], 'identical_files_left_untouched': audit['counts']['identical']}
    run = backups / ('forgebridge-' + token)
    try:
        require_toolkit_closed()
        baseline = _tree(root)
        run.mkdir(); copy = run / 'MyAssets'; copy.mkdir()
        for name, row in baseline.items():
            source, target = root / name, copy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open('rb') as src, target.open('xb') as dest:
                remaining = row['bytes']
                while block := src.read(min(1024 * 1024, remaining + 1)):
                    remaining -= len(block)
                    if remaining < 0: raise ValueError('MyAssets changed during backup')
                    dest.write(block)
            if _hash(target)[0] != row['sha256']: raise ValueError('Backup hash mismatch')
        # Preserve empty folders too.
        for directory in root.rglob('*'):
            if _linked(directory): raise ValueError('MyAssets changed during backup')
            if directory.is_dir(): (copy / directory.relative_to(root)).mkdir(parents=True, exist_ok=True)
        if _tree(root) != baseline: raise ValueError('MyAssets changed during backup')
        _json(run / 'backup-manifest.json', baseline)
        receipt['backup'] = str(copy)
        _json(run / 'uninstall.json', receipt)
        require_toolkit_closed()
        second = review(packages, root)
        if not second['ok'] or second['files'] != audit['files']:
            raise ValueError('Destination changed since review; backup retained, nothing added')
        for row in audit['files']:
            if row['status'] != 'new': continue
            name = row['path']; target = _target(root, name)
            missing = []; parent = target.parent
            while parent != root and not parent.exists(): missing.append(parent); parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                receipt['created_directories'].append(directory.relative_to(root).as_posix())
            # Record ownership immediately after exclusive creation, before writes;
            # failures retain a receipt whose hash guard refuses partial-file removal.
            with target.open('xb') as output:
                receipt['added'].append({'path': name, 'sha256': row['package_sha256']})
                _json(run / 'uninstall.json', receipt)
                output.write(native[name])
            if _hash(target)[0] != row['package_sha256']: raise ValueError('Installed file hash mismatch')
        receipt['state'] = 'COMPLETE'
        _json(run / 'uninstall.json', receipt)
        return {'status': 'PASS', 'added': len(receipt['added']), 'receipt': str(run / 'uninstall.json'),
                'backup': str(copy), 'runtime_validation': 'not performed'}
    finally:
        if lock.is_file() and not _linked(lock) and lock.read_text(encoding='ascii') == token:
            lock.unlink()


def uninstall(manifest):
    require_toolkit_closed()
    manifest = Path(manifest).absolute()
    if any(_linked(p) for p in (manifest, *manifest.parents)) or manifest.stat().st_size > 8 * 1024 * 1024:
        raise ValueError('Unsafe/oversized uninstall receipt')
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if data.get('format') != 'forgebridge.installation' or data.get('version') != 1 or data.get('state') != 'COMPLETE':
        raise ValueError('Uninstall requires a complete supported installation receipt')
    root = Path(data['myassets'])
    # Reuse root/ancestor validation without writing or trusting an arbitrary path.
    if not root.is_absolute() or root.name != 'MyAssets' or not root.is_dir() or any(_linked(p) for p in (root, *root.parents)):
        raise ValueError('Unsafe MyAssets root')
    if (not isinstance(data.get('added'), list) or len(data['added']) > 8192 or
            any(not isinstance(row, dict) or not isinstance(row.get('path'), str) or
                not isinstance(row.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', row['sha256'])
                for row in data['added'])):
        raise ValueError('Invalid/oversized uninstall list')
    baseline_path = manifest.parent / 'backup-manifest.json'
    if _linked(baseline_path) or baseline_path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('Unsafe backup manifest')
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    targets, seen = [], set()
    for row in data['added']:
        name = safe_name(row['path'])
        if name.casefold() in seen or name[9:] in baseline:
            raise ValueError('Receipt duplicates or includes a pre-existing file')
        seen.add(name.casefold())
        target = _target(root, name)
        if not target.is_file() or _hash(target)[0] != row['sha256']:
            raise ValueError('Added file changed/missing; preserve edits and review manually: ' + name)
        targets.append(target)
    lock = root.parent / '.forgebridge-install.lock'
    token = uuid.uuid4().hex
    with lock.open('x', encoding='ascii') as stream: stream.write(token)
    try:
        require_toolkit_closed()
        for target, row in zip(targets, data['added']):
            target = _target(root, row['path'])
            if _linked(target) or _hash(target)[0] != row['sha256']:
                raise ValueError('Target changed during uninstall; stop and inspect')
            target.unlink()
        # Leave directories and backups intact; they may now contain user content.
        data['state'] = 'UNINSTALLED'
        _json(manifest, data)
        return {'status': 'PASS', 'removed': len(targets), 'backup_retained': True}
    finally:
        if lock.is_file() and not _linked(lock) and lock.read_text(encoding='ascii') == token: lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', action='append', default=[])
    parser.add_argument('--myassets')
    parser.add_argument('--backup-root')
    parser.add_argument('--uninstall')
    args = parser.parse_args(argv)
    try:
        if args.uninstall:
            if args.package or args.myassets or args.backup_root: raise ValueError('Uninstall takes only its receipt')
            result = uninstall(args.uninstall)
        else:
            if not args.package or not args.myassets or not args.backup_root:
                raise ValueError('Install requires --package, --myassets and --backup-root')
            result = install(args.package, args.myassets, args.backup_root)
        print(json.dumps(result, indent=2)); return 0
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        parser.exit(1, str(exc) + '\n')

"""Bounded native-export loading and dependency closure; never CLR execution."""
import zipfile
import os
from pathlib import Path

from forgebridge.nrbf import Reader


def write_member(archive, name, data):
    """Stable ZIP metadata; callers retain their exclusive-write/cleanup policy."""
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o600 << 16
    archive.writestr(info, data)


def write_archive(destination, files):
    """Exclusive, deterministic publication; never leave our truncated archive."""
    destination = Path(destination)
    if any(p.is_symlink() or p.is_junction() for p in (destination, *destination.absolute().parents)):
        raise ValueError('Archive output must not contain links/junctions')
    _check_paths(files, native_only=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    output = destination.open('xb')
    identity = os.fstat(output.fileno())
    try:
        with output, zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(files.items()): write_member(archive, name, data)
    except BaseException:
        # Preserve a file another writer replaced while this operation failed.
        if not destination.is_symlink() and destination.exists():
            current = destination.stat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                destination.unlink()
        raise


def safe_name(name):
    """Require a portable native asset path without Windows aliases."""
    parts = name.split('/')
    reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{p}{n}' for p in ('COM', 'LPT') for n in range(1, 10)}
    if (not name.startswith('MyAssets/') or '\\' in name or ':' in name
            or any(not p or p in ('.', '..') or p.endswith((' ', '.'))
                   or any(ord(c) < 32 or c in '<>"|?*' for c in p)
                   or p.split('.')[0].upper() in reserved for p in parts)):
        raise ValueError('Unsafe native path: ' + name)
    return name


def _check_paths(names, *, native_only=True):
    folded = {}
    for name in names:
        # Combined packages also contain inert reports outside MyAssets.
        safe_name(name if native_only or name.startswith('MyAssets/') else 'MyAssets/' + name)
        prior = folded.setdefault(name.casefold(), name)
        if prior != name:
            raise ValueError('Case-conflicting native paths: ' + prior + ' / ' + name)


def read_export(path):
    return _read_archive(path, native_only=True, max_entries=2048)


def read_package(path):
    """Bounded combined-package loading, including inert supplemental reports."""
    return _read_archive(path, native_only=False, max_entries=8192)


def _read_archive(path, *, native_only, max_entries):
    with zipfile.ZipFile(path) as archive:
        entries = [e for e in archive.infolist() if not e.is_dir()]
        names = [e.filename for e in entries]
        if (len(entries) > max_entries or len(names) != len(set(names))
                or sum(e.file_size for e in entries) > 256 * 1024 * 1024
                or any(e.file_size > 64 * 1024 * 1024 for e in entries)):
            raise ValueError('Invalid or oversized native export')
        if any((e.external_attr >> 16) & 0o170000 == 0o120000 for e in archive.infolist()):
            raise ValueError('Native export contains a symbolic link')
        _check_paths(names, native_only=native_only)
        return {n: archive.read(n) for n in names}


def merge_native(files, dependencies):
    """Validate the entire merge before mutating; identical paths deduplicate."""
    _check_paths((*files, *dependencies), native_only=False)
    for path, data in dependencies.items():
        if path in files and files[path] != data:
            raise ValueError('Native dependency conflicts with exported content: ' + path)
    files.update(dependencies)


def check_metadata_references(files):
    """Check native map/note/metadata links; preserved media bytes stay opaque."""
    _check_paths(files, native_only=False)
    count = 0
    for path, data in files.items():
        if not path.endswith(('.rwmap', '.rwnote', '.rwmeta', '.rwpl')):
            continue
        reader = Reader(data, max_items=64000000)
        reader.read()
        for value in reader.objects.values():
            if isinstance(value, str) and value.startswith('MyAssets/') and value.endswith('.rwmeta'):
                if value not in files:
                    raise ValueError('Missing native dependency: ' + value + ' (from ' + path + ')')
                count += 1
    return count

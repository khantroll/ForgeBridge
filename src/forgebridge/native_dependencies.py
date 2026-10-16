"""Bounded native-export loading and dependency closure; never CLR execution."""
from pathlib import PurePosixPath
import zipfile

from forgebridge.nrbf import Reader


def read_export(path):
    with zipfile.ZipFile(path) as archive:
        entries = [e for e in archive.infolist() if not e.is_dir()]
        names = [e.filename for e in entries]
        if (len(entries) > 2048 or len(names) != len(set(names))
                or sum(e.file_size for e in entries) > 256 * 1024 * 1024
                or any(e.file_size > 64 * 1024 * 1024 for e in entries)
                or any(not n.startswith('MyAssets/') or '..' in PurePosixPath(n).parts
                       or '\\' in n or ':' in n for n in names)):
            raise ValueError('Invalid or oversized native export')
        return {n: archive.read(n) for n in names}


def merge_native(files, dependencies):
    for path, data in dependencies.items():
        if path in files and files[path] != data:
            raise ValueError('Native dependency conflicts with exported content: ' + path)
        files[path] = data


def check_metadata_references(files):
    """Check native map/note/metadata links; preserved media bytes stay opaque."""
    count = 0
    for path, data in files.items():
        if not path.endswith(('.rwmap', '.rwnote', '.rwmeta')):
            continue
        reader = Reader(data, max_items=64000000)
        reader.read()
        for value in reader.objects.values():
            if isinstance(value, str) and value.startswith('MyAssets/') and value.endswith('.rwmeta'):
                if value not in files:
                    raise ValueError('Missing native dependency: ' + value + ' (from ' + path + ')')
                count += 1
    return count

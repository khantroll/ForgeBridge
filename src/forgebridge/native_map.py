"""Experimental marker insertion into a user-supplied native map.

Coordinates must be calibrated explicitly. Existing records are copied as bytes;
only the map name, tile list and UID counter are patched. No CLR types are loaded.
"""
from dataclasses import dataclass
import argparse
import json
import math
from pathlib import Path, PurePosixPath
import struct
import zipfile

from forgebridge.native import Array, Node, Writer
from forgebridge.nrbf import Reader


@dataclass
class Reference:
    oid: int


class AppendWriter(Writer):
    """Write appended records using the source stream's existing metadata."""
    def __init__(self, reader):
        super().__init__(reader.libraries)
        self.next_id = max(abs(oid) for oid in reader.objects) + 1
        self.metadata_ids = {json.dumps(m, sort_keys=True): oid
                             for oid, m in reader.classes.items()}

    def value(self, value):
        if isinstance(value, Reference):
            self.out.append(9)
            self.integer(value.oid)
        else:
            super().value(value)

    def primitive(self, kind, value):
        if kind == 9:
            self.out += struct.pack('<q', value)
        else:
            super().primitive(kind, value)

    def array(self, array, oid):
        self.out.append(7)
        self.integer(oid)
        self.out.append(0)
        self.integer(1)
        self.integer(len(array.items))
        self.out.append(array.kind)
        self.type_info(array.kind, array.info)
        for item in array.items:
            if array.kind == 0:
                self.primitive(array.info, item)
            else:
                self.value(item)

    def encoded(self, value):
        previous = self.out
        self.out = bytearray()
        self.value(value)
        data = bytes(self.out)
        self.out = previous
        return data

    def finish(self):
        while self.queue:
            value = self.queue.popleft()
            if isinstance(value, Node):
                self.node(value, self.ids[id(value)])
            else:
                self.array(value, self.ids[id(value)])
            self.records += 1
            if self.records > 200000 or len(self.out) > 64 * 1024 * 1024:
                raise ValueError('Appended map records exceed limit')
        return bytes(self.out)


def clone(reader, oid, memo=None):
    """Clone a small marker graph, retaining shared references inside the clone."""
    memo = {} if memo is None else memo
    if oid in memo:
        return memo[oid]
    obj = reader.objects[oid]
    if isinstance(obj, str):
        return obj
    if 'members' in obj:
        result = Node(reader.object_metadata[oid], {}, inline=oid < 0)
        memo[oid] = result
        result.members.update({k: clone(reader, v['ref'], memo) if isinstance(v, dict) and 'ref' in v else v
                               for k, v in obj['members'].items()})
    elif 'items' in obj and len(obj['lengths']) == 1 and obj['lower_bounds'] is None:
        kind, info = reader.array_metadata[oid]
        result = Array([], kind, info)
        memo[oid] = result
        result.items.extend(clone(reader, v['ref'], memo) if isinstance(v, dict) and 'ref' in v else v
                            for v in obj['items'])
    else:
        raise ValueError('Unsupported marker graph object')
    return result


def patch_stream(reader, patches, writer):
    """Apply disjoint byte spans, append records before the original message end."""
    result = bytearray()
    end = 0
    for start, stop, replacement in sorted(patches):
        if start < end or stop < start or stop >= len(reader.data):
            raise ValueError('Overlapping or invalid native patch')
        result += reader.data[end:start]
        result += replacement
        end = stop
    result += reader.data[end:-1]
    # A replaced field can contain the first definition of a shared string.
    # Retain that definition even when the old name becomes unreachable.
    for oid, (start, stop) in reader.record_spans.items():
        if isinstance(reader.objects[oid], str) and any(a <= start and stop <= b for a, b, _ in patches):
            result += reader.data[start:stop]
    result += writer.finish()
    result.append(11)
    updated = bytes(result)
    if len(updated) > 64 * 1024 * 1024:
        raise ValueError('Native map exceeds limit')
    Reader(updated).read()
    return updated


def rename_metadata(data, name):
    reader = Reader(data)
    graph = reader.read()
    root = graph['root_id']
    if reader.objects[root]['class'] != 'ArkenMapMeta':
        raise ValueError('Expected native map metadata')
    writer = AppendWriter(reader)
    patches = [(a, b, writer.encoded(name)) for key, (a, b) in reader.member_spans[root].items()
               if key.split('+')[-1] in ('_name', '_mapName')]
    return patch_stream(reader, patches, writer)


def insert_markers(data, placements, *, name, units_per_grid, origin=(0., 0.),
                   template_name='FB Cal A', remove_names=()):
    """Return a new map and insertion report; source bytes are never modified.

    Source grid coordinates increase right/down; native coordinates right/up.
    The origin and scale refer to the image's upper-left corner, not its centre.
    """
    if not isinstance(name, str) or not name or len(name) > 256:
        raise ValueError('Invalid map name')
    if not math.isfinite(units_per_grid) or units_per_grid <= 0 or len(origin) != 2 or not all(math.isfinite(v) for v in origin):
        raise ValueError('Invalid calibrated map transform')
    if not isinstance(placements, list) or not 1 <= len(placements) <= 2048:
        raise ValueError('Expected 1 to 2048 marker placements')
    reader = Reader(data)
    graph = reader.read()
    objects = reader.objects
    root_id = graph['root_id']
    root = objects[root_id]
    if root['class'] != 'ArkenMapUpgrade':
        raise ValueError('Expected supported native map')
    def resolve(v):
        return objects[v['ref']] if isinstance(v, dict) and 'ref' in v else v
    def members(v):
        return resolve(v)['members']
    tiles_id = root['members']['_tiles']['ref']
    tiles = objects[tiles_id]['members']
    array_id = tiles['_items']['ref']
    array = objects[array_id]
    active = array['items'][:tiles['_size']]
    template, kept, max_uid, max_order = [], [], 0, 0
    for ref in active:
        tile = members(ref)
        preset = resolve(tile['_tileInfo'])
        p = preset['members']
        max_uid = max(max_uid, p.get('_uID', 0))
        max_order = max(max_order, p.get('_sortingOrder', 0))
        title = resolve(p.get('_tileName'))
        marker = preset['class'] == 'ArkenTilePresetContentLink'
        if marker and title == template_name:
            template.append(ref['ref'])
        if not (marker and title in remove_names):
            kept.append(ref)
    if len(template) != 1:
        raise ValueError('Expected exactly one named calibration marker')
    max_uid = max(max_uid, root['members']['_nextUID'] - 1)
    writer = AppendWriter(reader)
    refs = [Reference(ref['ref']) for ref in kept]
    report = []
    for i, placement in enumerate(placements):
        target, position = placement.get('target'), placement.get('grid_position')
        if not isinstance(target, str) or not target.startswith('MyAssets/Encyclopedia/Notes/') or not target.endswith('.rwmeta') or '\\' in target or '..' in target.split('/'):
            raise ValueError('Marker target must be a native note metadata path')
        if not isinstance(position, dict) or not all(type(position.get(k)) in (int, float) and math.isfinite(position[k]) for k in ('x', 'y')):
            raise ValueError('Marker has no finite grid position')
        tile = clone(reader, template[0])
        p = tile.members['_tileInfo'].members
        x, y = origin[0] + position['x'] * units_per_grid, origin[1] - position['y'] * units_per_grid
        p['_position'].members.update(x=x, y=y)
        uid, order = max_uid + i + 1, max_order + i + 1
        title = str(placement.get('title') or 'Map note')
        for key in p:
            bare = key.split('+')[-1]
            if bare == '_contentBasePath': p[key] = target
            elif bare == '_contentType': p[key] = 'note'
            elif bare in ('_tileName', '_name'): p[key] = title
            elif bare == '_uID': p[key] = uid
            elif bare == '_sortingOrder': p[key] = order
            elif bare == '_groupID': p[key] = -1
        refs.append(Reference(writer.allocate(tile)))
        report.append({**placement, 'native_map_placement': True, 'native_position': {'x': x, 'y': y}, 'native_uid': uid})
    capacity = max(len(refs), len(array['items']))
    replacement = Array(refs + [None] * (capacity - len(refs)), *reader.array_metadata[array_id])
    writer.array(replacement, array_id)
    array_bytes = bytes(writer.out)
    writer.out.clear()
    patches = [(*reader.record_spans[array_id], array_bytes)]
    def field(oid, key, encoded):
        patches.append((*reader.member_spans[oid][key], encoded))
    field(root_id, '_name', writer.encoded(name))
    kind = reader.object_metadata[root_id]['infos'][reader.object_metadata[root_id]['names'].index('_nextUID')]
    if kind not in (8, 9):
        raise ValueError('Unsupported UID counter type')
    field(root_id, '_nextUID', struct.pack('<i' if kind == 8 else '<q', max_uid + len(placements) + 1))
    field(tiles_id, '_size', struct.pack('<i', len(refs)))
    field(tiles_id, '_version', struct.pack('<i', tiles['_version'] + 1))
    updated = patch_stream(reader, patches, writer)
    checked = Reader(updated).read()['objects']
    changed = {root_id, tiles_id, array_id}
    if any(checked.get(oid) != obj for oid, obj in objects.items() if oid not in changed):
        raise ValueError('Existing native map objects changed unexpectedly')
    return updated, report


def write_map_zip(template_pack, companion, dest, *, name, units_per_grid,
                  origin=(0., 0.), template_name='FB Cal A', remove_names=()):
    """Build a separate native test package from a single saved-map export."""
    from forgebridge.native_export import companion_files
    dest, companion = Path(dest), Path(companion)
    if dest.exists() or dest.is_symlink():
        raise ValueError('Choose a new output filename')
    if not name or PurePosixPath(name).name != name or '\\' in name or name in ('.', '..'):
        raise ValueError('Map name must be a plain filename')
    if companion.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('Companion exceeds size limit')
    with zipfile.ZipFile(template_pack) as archive:
        entries = [e for e in archive.infolist() if not e.is_dir()]
        if len(entries) > 2048 or sum(e.file_size for e in entries) > 256 * 1024 * 1024 or any(e.file_size > 64 * 1024 * 1024 for e in entries):
            raise ValueError('Template archive exceeds limits')
        paths = [e.filename for e in entries]
        if len(set(paths)) != len(paths) or any(not p.startswith('MyAssets/') or '..' in PurePosixPath(p).parts or '\\' in p for p in paths):
            raise ValueError('Invalid template archive paths')
        maps = [p for p in paths if p.endswith('.rwmap')]
        if len(maps) != 1 or maps[0][:-6] + '.rwmeta' not in paths:
            raise ValueError('Export must contain one saved map and its metadata')
        files = {p: archive.read(p) for p in paths}
    generated, report = companion_files(json.loads(companion.read_text(encoding='utf-8')), map_markers=True)
    map_path = maps[0]
    metadata_path = map_path[:-6] + '.rwmeta'
    updated, placements = insert_markers(files.pop(map_path), report['placements'], name=name,
        units_per_grid=units_per_grid, origin=origin, template_name=template_name, remove_names=remove_names)
    metadata = rename_metadata(files.pop(metadata_path), name)
    folder = str(PurePosixPath(map_path).parent)
    files[folder + '/' + name + '.rwmap'] = updated
    files[folder + '/' + name + '.rwmeta'] = metadata
    report['placements'] = placements
    report['native_map'] = {'name': name, 'units_per_grid': units_per_grid, 'origin': list(origin),
                            'markers': len(placements), 'runtime_validation': 'pending'}
    report['status'] = 'Generated native map placement requires Toolkit validation. See project status for previously verified source imports.'
    generated['conversion-report.json'] = json.dumps(report, ensure_ascii=True, indent=2).encode()
    generated['INSTALL.txt'] = (f'ForgeBridge native map test: {name}\n\n'
        'Close the Toolkit and back up MyAssets. Extract this ZIP outside Arkenforge.\n'
        'Merge its MyAssets contents into your EXISTING ArkenforgeData/MyAssets folder.\n'
        'Keep all relative paths intact. Do not put a second MyAssets folder inside MyAssets.\n'
        f'Open the new saved map {name}. The original saved map is not replaced.\n'
        'Verify room marker positions, clicking a room note, and save/reload.\n'
        'Existing image, barriers, doors and lights are preserved from the exported map.\n'
        'Player visibility is unverified; review it before player use.\n'
        'PDF/image handouts remain references; their files are not supplied.\n'
        'Keep reports outside MyAssets. This package contains private source content.\n').encode()
    for path, data in generated.items():
        if path in files and files[path] != data:
            raise ValueError('Generated notes conflict with exported content')
        files[path] = data
    if sum(len(data) for data in files.values()) > 256 * 1024 * 1024:
        raise ValueError('Output archive exceeds limit')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in files.items():
            archive.writestr(path, data)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template-pack', required=True)
    parser.add_argument('--companion', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--units-per-grid', required=True, type=float)
    parser.add_argument('--origin', nargs=2, type=float, default=(0., 0.))
    parser.add_argument('--template-name', default='FB Cal A')
    parser.add_argument('--remove-marker', action='append', default=[])
    args = parser.parse_args()
    report = write_map_zip(args.template_pack, args.companion, args.out, name=args.name,
        units_per_grid=args.units_per_grid, origin=args.origin,
        template_name=args.template_name, remove_names=args.remove_marker)
    print(f"Wrote {report['native_map']['markers']} markers; Toolkit map validation pending.")


if __name__ == '__main__':
    main()

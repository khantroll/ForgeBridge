"""Write a native Arkenforge map directly from ForgeBridge UVTT geometry.

Replaces the manual Toolkit "import UVTT -> export map -> calibrate" step.
Calibration is computed, not measured: the Toolkit's UVTT import places the
image's upper-left corner at native (0, 0), y up, at 2.56 native units per grid
square (Unity sprites use 100 px per unit; 256 / pixels_per_grid scales a
source pixel). Verified record-for-record against the Toolkit's own import of
Count's Crypt: 199 walls, 23 doors with open/closed state, 66 lights.

Record shapes (wall/door Barrier, Light Source, image tile) are cloned from a
map the user already has in MyAssets; no Arkenforge data ships with
ForgeBridge. No CLR types are loaded and nothing is executed.
"""
import math
import struct

from forgebridge.native import Array
from forgebridge.native_map import AppendWriter, Reference, clone, patch_stream
from forgebridge.nrbf import Reader

UNITS_PER_GRID = 2.56
MAX_RECORDS = 20000


def _resolver(reader):
    def resolve(v):
        return reader.objects[v['ref']] if isinstance(v, dict) and 'ref' in v else v
    return resolve


def find_templates(template_data):
    """Locate one wall, one door, one light and one image tile in a native map."""
    reader = Reader(template_data, max_items=64000000)
    graph = reader.read()
    resolve = _resolver(reader)
    root = reader.objects[graph['root_id']]
    if root.get('class') != 'ArkenMapUpgrade':
        raise ValueError('Template must be a native map')
    tiles = resolve(root['members']['_tiles'])['members']
    found = {}
    for ref in resolve(tiles['_items'])['items'][:tiles['_size']]:
        preset = resolve(resolve(ref)['members']['_tileInfo'])
        p = preset['members']
        if preset['class'] == 'ArkenTilePresetRepeatable' and resolve(p.get('_tileName')) == 'Barrier':
            blocking = resolve(p['_blocking'])['members']
            found.setdefault('door' if blocking['_toggleable'] else 'wall', ref['ref'])
        elif preset['class'] == 'ArkenTilePresetBase' and resolve(p.get('_tileName')) == 'Light Source':
            found.setdefault('light', ref['ref'])
        elif (preset['class'] == 'ArkenTilePresetBase' and isinstance(resolve(p.get('_tilePath')), str)
              and resolve(p.get('_tilePath')).startswith('MyAssets/Media/')):
            found.setdefault('image', ref['ref'])
    missing = {'wall', 'door', 'light', 'image'} - set(found)
    if missing:
        raise ValueError('Template map lacks native ' + ', '.join(sorted(missing))
                         + '; choose a map that was created by a Toolkit UVTT import')
    return reader, found


def _world(point, size):
    x, y = point['x'], point['y']
    if not all(type(v) in (int, float) and math.isfinite(v) for v in (x, y)):
        raise ValueError('Non-finite UVTT coordinate')
    return x * size, -y * size


def _segments(uvtt):
    for line in uvtt.get('line_of_sight') or []:
        for a, b in zip(line, line[1:]):
            yield a, b


def _set(members, **values):
    for key in list(members):
        bare = key.split('+')[-1]
        if bare in values:
            members[key] = values[bare]


def _barrier(template, a, b, size, uid, order, closed=None):
    tile = clone(*template)
    p = tile.members['_tileInfo'].members
    (ax, ay), (bx, by) = _world(a, size), _world(b, size)
    cx, cy = (ax + bx) / 2, (ay + by) / 2
    p['_position'].members.update(x=cx, y=cy)
    points = p['_points'].members
    items = points['_items'].items
    if len(items) < 2 or not all(hasattr(items[i], 'members') for i in (0, 1)):
        raise ValueError('Template barrier lacks two point records')
    items[0].members.update(x=ax - cx, y=ay - cy)
    items[1].members.update(x=bx - cx, y=by - cy)
    for i in range(2, len(items)):
        items[i] = None
    points['_size'] = 2
    if closed is not None:
        p['_blocking'].members.update(_blockingEnabled=True, _light=bool(closed), _vision=bool(closed),
                                      _movement=False, _toggleable=True)
    _set(p, _uID=uid, _sortingOrder=order, _groupID=-1, _hidden=False, _mapLevel=0)
    return tile


def _light(template, light, size, uid, order):
    tile = clone(*template)
    p = tile.members['_tileInfo'].members
    x, y = _world(light['position'], size)
    p['_position'].members.update(x=x, y=y)
    rng = light.get('range')
    if type(rng) not in (int, float) or not math.isfinite(rng) or rng <= 0:
        raise ValueError('Light range must be positive')
    radius = p['_lighting'].members['_lightRadius'].members
    radius['_items'].items[0] = float(rng * size)
    radius['_size'] = 1
    # The Toolkit's own UVTT import stores intensity 1.0 regardless of the file.
    _set(p['_lighting'].members, _hasLight=True, _lightIntensity=1.0)
    _set(p, _uID=uid, _sortingOrder=order, _groupID=-1, _hidden=False, _mapLevel=0)
    return tile


def _image(template, uvtt, size, image_meta_path, asset_name, uid, order):
    tile = clone(*template)
    p = tile.members['_tileInfo'].members
    res = uvtt['resolution']
    ppg = res['pixels_per_grid']
    if type(ppg) not in (int, float) or not ppg > 0:
        raise ValueError('UVTT pixels_per_grid must be positive')
    width, height = res['map_size']['x'], res['map_size']['y']
    p['_position'].members.update(x=width * size / 2, y=-height * size / 2)
    scale = size * 100 / ppg
    p['_scale'].members.update(x=scale, y=scale)
    _set(p, _tilePath=image_meta_path, _name=asset_name, _tileName=asset_name,
         _uID=uid, _sortingOrder=order, _groupID=-1, _hidden=False, _mapLevel=0)
    tile.members['spriteWidth'] = float(max(width, height) * ppg)
    return tile


def synthesize_map(blank_data, template_data, uvtt, *, name, image_meta_path, asset_name):
    """Return native map bytes and a report. Neither input stream is modified.

    blank_data: a native map to use as the container (an empty Toolkit map).
    template_data: a Toolkit-imported native map supplying record shapes.
    """
    if not isinstance(name, str) or not name or len(name) > 256:
        raise ValueError('Invalid map name')
    reader = Reader(blank_data, max_items=64000000)
    graph = reader.read()
    objects, root_id = reader.objects, graph['root_id']
    root = objects[root_id]
    if root.get('class') != 'ArkenMapUpgrade':
        raise ValueError('Expected a native map container')
    template_reader, found = find_templates(template_data)
    if template_reader.libraries != reader.libraries:
        raise ValueError('Template and container libraries differ')
    tiles_id = root['members']['_tiles']['ref']
    tiles = objects[tiles_id]['members']
    array_id = tiles['_items']['ref']
    array = objects[array_id]
    if tiles['_size']:
        raise ValueError('Container map must be empty')
    size = UNITS_PER_GRID
    writer = AppendWriter(reader)
    refs, uid, order = [], 0, 0
    def add(tile):
        nonlocal uid, order
        refs.append(Reference(writer.allocate(tile)))
    def tpl(kind):
        return (template_reader, found[kind])
    uid = order = 1
    add(_image(tpl('image'), uvtt, size, image_meta_path, asset_name, uid, 0))
    counts = {'walls': 0, 'doors': 0, 'lights': 0}
    for a, b in _segments(uvtt):
        uid += 1; order += 1
        add(_barrier(tpl('wall'), a, b, size, uid, order))
        counts['walls'] += 1
    for portal in uvtt.get('portals') or []:
        bounds = portal.get('bounds') or []
        if len(bounds) != 2:
            raise ValueError('Portal needs two bounds')
        uid += 1; order += 1
        add(_barrier(tpl('door'), bounds[0], bounds[1], size, uid, order, closed=bool(portal.get('closed'))))
        counts['doors'] += 1
    for light in uvtt.get('lights') or []:
        uid += 1; order += 1
        add(_light(tpl('light'), light, size, uid, order))
        counts['lights'] += 1
    if len(refs) > MAX_RECORDS:
        raise ValueError('Too many native records')
    replacement = Array(refs, *reader.array_metadata[array_id])
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
    field(root_id, '_nextUID', struct.pack('<i' if kind == 8 else '<q', uid + 1))
    field(tiles_id, '_size', struct.pack('<i', len(refs)))
    field(tiles_id, '_version', struct.pack('<i', tiles['_version'] + len(refs)))
    updated = patch_stream(reader, patches, writer)
    return updated, {'name': name, 'calibration': {'units_per_grid': size, 'origin': [0.0, 0.0],
                     'source': 'computed (Toolkit UVTT import convention)'},
                     'records': {**counts, 'image': 1}, 'image_meta_path': image_meta_path}


def _rename(data, name, max_items=64000000):
    """Patch every `_name` member of the root object; other bytes unchanged."""
    from forgebridge.native_map import AppendWriter as _AW
    reader = Reader(data, max_items=max_items, max_bytes=128 * 1024 * 1024)
    graph = reader.read()
    root = graph['root_id']
    writer = _AW(reader)
    patches = [(a, b, writer.encoded(name)) for key, (a, b) in reader.member_spans[root].items()
               if key.split('+')[-1] in ('_name', '_mapName')]
    if not patches:
        raise ValueError('Native object has no name field')
    return patch_stream(reader, patches, writer, max_items=max_items)


def background_asset(template_file, template_meta, image, asset_name):
    """Native background tile asset pair (.rwfile, .rwmeta) for one map image.

    Map backgrounds exceed the 16 MP note-image cap (Count's Crypt is 16.8 MP);
    the Toolkit's own import stored that image, so allow up to 64 MP here.
    """
    import io
    from PIL import Image, ImageOps
    from forgebridge.native_images import replace_image_payload
    with Image.open(io.BytesIO(image)) as source:
        if source.format not in {'PNG', 'JPEG', 'WEBP'} or getattr(source, 'n_frames', 1) != 1:
            raise ValueError('Map background must be a still PNG, JPEG or WEBP')
        if source.width * source.height > 64_000_000:
            raise ValueError('Map background exceeds 64 megapixel limit')
        picture = ImageOps.exif_transpose(source).convert('RGBA')
    full = io.BytesIO(); picture.save(full, 'PNG')
    thumb = picture.copy(); thumb.thumbnail((128, 128), Image.Resampling.LANCZOS)
    preview = io.BytesIO(); thumb.save(preview, 'PNG')
    scale = max(thumb.size) / max(picture.size)  # Toolkit: 128 / longer side
    rwfile = _rename(replace_image_payload(template_file, full.getvalue(), scale), asset_name)
    rwmeta = _rename(replace_image_payload(template_meta, preview.getvalue(), scale), asset_name)
    return rwfile, rwmeta, {'dimensions': list(picture.size), 'thumbnail_scale': scale}


def map_metadata(template_meta, name, image=None):
    from forgebridge.native_map import rename_metadata
    data = rename_metadata(template_meta, name)
    if image is None:
        return data
    import io
    from PIL import Image, ImageOps
    from forgebridge.native import Node
    from forgebridge.native_scene_schema import CLASSES
    with Image.open(io.BytesIO(image)) as source:
        if source.width * source.height > 64_000_000 or getattr(source, 'n_frames', 1) != 1:
            raise ValueError('Map thumbnail needs a bounded static background')
        preview = ImageOps.exif_transpose(source).convert('RGBA')
    preview.thumbnail((256, 256), Image.Resampling.LANCZOS)
    output = io.BytesIO(); preview.save(output, 'PNG')
    thumbnail = Node(CLASSES['ArkenImage'], {'_packImgX': -1, '_packImgY': -1,
        '_packImgChannels': 4, '_packImageRAW': Array(list(output.getvalue()), 0, 2)})
    reader = Reader(data); graph = reader.read(); root = graph['root_id']
    writer = AppendWriter(reader)
    span = reader.member_spans[root].get('_thumbnail')
    if span is None: raise ValueError('Map metadata lacks thumbnail field')
    return patch_stream(reader, [(*span, writer.encoded(thumbnail))], writer)

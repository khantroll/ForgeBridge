"""Read-only Fantasy Grounds module reader (groundwork for a second input path).

Reads a Fantasy Grounds module (a ``.mod`` ZIP or an unpacked folder), lists its
map images, and converts one map's grid, line of sight, doors/windows and
lights into the same UVTT-shaped scene that ForgeBridge's native map writer and
Arkenforge's own UVTT import already accept.

Nothing here writes into a Fantasy Grounds or Arkenforge install. Module XML is
parsed with DTDs/entities refused and every read bounded. Every mapping that is
not exact is reported as a loss line; anything not yet understood is reported,
never guessed silently.

Format sources (see docs/FANTASY-GROUNDS-ADAPTER.md): FG "Module - Data Files"
and "Image Line of Sight Data" pages, and uvtt2fgu's writer (BSD-3). Image
coordinates are pixels with the origin at the image centre and y pointing up;
light ranges are in grid squares. These are documented for the per-image
metadata XML; their use inside ``db.xml`` image records is an assumption until
checked against a real module.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image

MAX_ENTRIES = 20000
MAX_XML_BYTES = 64 * 1024 * 1024
MAX_IMAGE_BYTES = 256 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024
MAX_IMAGE_PIXELS = 64_000_000
MAX_POINTS = 200_000
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp'}


class ModuleError(ValueError):
    """The module cannot be read safely or is not a Fantasy Grounds module."""


def _clean(name: str) -> str | None:
    name = name.replace('\\', '/')
    path = PurePosixPath(name)
    if (not name or name.startswith('/') or re.match(r'^[A-Za-z]:', name)
            or any(part in ('', '.', '..') for part in path.parts)):
        return None
    return path.as_posix()


class ModuleSource:
    """Bounded, read-only access to files inside a .mod ZIP or a module folder."""

    def __init__(self, path):
        self.path = Path(path)
        self._zip = None
        self._names: dict[str, str] = {}
        try:
            self._index()
        except Exception:
            self.close()
            raise

    def _index(self):
        if self.path.is_dir():
            root = self.path.resolve()
            count = 0
            for file in self.path.rglob('*'):
                if file.is_symlink():
                    continue
                if file.is_file():
                    count += 1
                    if count > MAX_ENTRIES:
                        raise ModuleError('Module folder has too many files')
                    try:
                        rel = file.resolve().relative_to(root).as_posix()
                    except ValueError:
                        continue
                    self._add(rel, rel)
        elif self.path.is_file():
            try:
                self._zip = zipfile.ZipFile(self.path)
            except zipfile.BadZipFile as exc:
                raise ModuleError('Not a .mod/ZIP archive: ' + str(self.path)) from exc
            infos = [i for i in self._zip.infolist() if not i.is_dir()]
            if any(i.flag_bits & 0x1 for i in infos):
                raise ModuleError('This module is encrypted (Fantasy Grounds vault/store protection). '
                                  'ForgeBridge does not read protected content; use a module you can '
                                  'export from your own campaign, or an unprotected .mod.')
            if len(infos) > MAX_ENTRIES:
                raise ModuleError('Module archive has too many entries')
            if sum(i.file_size for i in infos) > MAX_TOTAL_BYTES:
                raise ModuleError('Module archive expands beyond the size limit')
            for info in infos:
                rel = _clean(info.filename)
                is_link = ((info.external_attr >> 16) & 0o170000) == 0o120000
                if rel is not None and not is_link:
                    self._add(rel, info.filename)
        else:
            raise ModuleError('Module path not found: ' + str(self.path))
        if 'definition.xml' not in self._names:
            # FG vault packages (Forge downloads, vault/<guid>.dat) are ZIPs holding
            # exactly one module under modules/<name>/; read that module in place.
            nested = [k for k in self._names if re.fullmatch(r'modules/[^/]+/definition\.xml', k)]
            if len(nested) != 1:
                raise ModuleError('definition.xml missing from module root; not a Fantasy Grounds module')
            prefix = nested[0][:-len('definition.xml')]
            self._names = {k[len(prefix):]: v for k, v in self._names.items() if k.startswith(prefix)}
            self.vault_prefix = prefix

    def _add(self, rel, raw):
        key = rel.casefold()
        if key in self._names:
            raise ModuleError('Duplicate/case-aliased module path: ' + rel)
        self._names[key] = raw

    def exists(self, rel: str) -> bool:
        rel = _clean(rel)
        return rel is not None and rel.casefold() in self._names

    def read(self, rel: str, limit: int) -> bytes:
        clean = _clean(rel)
        if clean is None or clean.casefold() not in self._names:
            raise ModuleError('File not in module: ' + rel)
        raw = self._names[clean.casefold()]
        if self._zip is not None:
            info = self._zip.getinfo(raw)
            if info.file_size > limit:
                raise ModuleError('File too large: ' + clean)
            with self._zip.open(info) as stream:
                data = stream.read(limit + 1)
        else:
            file = self.path / raw
            if file.stat().st_size > limit:
                raise ModuleError('File too large: ' + clean)
            data = file.read_bytes()
        if len(data) > limit:
            raise ModuleError('File too large: ' + clean)
        return data

    def close(self):
        if self._zip is not None:
            self._zip.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def parse_xml(data: bytes, label: str) -> ET.Element:
    """Parse module XML, refusing DTDs and entity declarations outright."""
    if re.search(rb'<!DOCTYPE|<!ENTITY', data, re.I):
        raise ModuleError(label + ': DTD/entity declarations are not accepted')
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise ModuleError(label + ': not well-formed XML (' + str(exc) + ')') from exc


def _text(node, tag, default=None):
    child = node.find(tag) if node is not None else None
    return child.text.strip() if child is not None and child.text and child.text.strip() else default


def definition(source: ModuleSource) -> dict:
    root = parse_xml(source.read('definition.xml', 1024 * 1024), 'definition.xml')
    return {'name': _text(root, 'name'), 'displayname': _text(root, 'displayname'),
            'author': _text(root, 'author'), 'category': _text(root, 'category'),
            'rulesets': [r.text.strip() for r in root.findall('ruleset') if r.text and r.text.strip()],
            'version': root.get('version')}


def _record_path(parents, node):
    parts, cur = [], node
    while cur is not None and cur in parents:
        if cur.tag != 'category': parts.append(cur.tag)
        cur = parents[cur]
    return '.'.join(reversed(parts))


def _bitmap(image_node):
    """Bitmap path of an image value node: FGU layered form first, then classic."""
    layers = image_node.find('layers')
    if layers is not None:
        for layer in layers.findall('layer'):
            path = _text(layer, 'bitmap') or _text(layer, 'asset')
            if path:
                return path, len(layers.findall('layer'))
    return _text(image_node, 'bitmap'), 1


def list_images(source: ModuleSource, db_name='db.xml') -> list[dict]:
    """Every node with type="image" in db.xml, with its record name and bitmap."""
    if not source.exists(db_name):
        return []
    root = parse_xml(source.read(db_name, MAX_XML_BYTES), db_name)
    parents = {child: parent for parent in root.iter() for child in parent}
    found = []
    for node in root.iter():
        if node.get('type') != 'image':
            continue
        record = parents.get(node)
        bitmap, layers = _bitmap(node)
        found.append({
            'record': _record_path(parents, record) if record is not None else node.tag,
            'name': _text(record, 'name') or (Path(bitmap).stem if bitmap else node.tag),
            'bitmap': bitmap,
            'layers': layers,
            'has_line_of_sight': node.find('.//occluders') is not None,
            'has_lights': node.find('.//lights') is not None,
            'pins': len(node.findall('./shortcuts/shortcut')),
            'grid_on': (_text(node, 'grid') or '').lower() == 'on',
            '_node': node,
        })
    return found


def _floats(text, label, even=True):
    try:
        values = [float(v) for v in (text or '').replace(';', ',').split(',') if v.strip()]
    except ValueError as exc:
        raise ModuleError(label + ': non-numeric value') from exc
    if not all(math.isfinite(v) for v in values) or (even and len(values) % 2) or len(values) > MAX_POINTS * 2:
        raise ModuleError(label + ': malformed number list')
    return values


class _Frame:
    """FG pixel space (centre origin, y up) to UVTT grid space (top-left, y down)."""

    def __init__(self, width, height, ppg):
        self.w, self.h, self.ppg = width, height, ppg

    def point(self, x, y):
        return {'x': round((x + self.w / 2) / self.ppg, 6), 'y': round((self.h / 2 - y) / self.ppg, 6)}


def _pairs(values):
    return list(zip(values[0::2], values[1::2]))


def _door_bounds(pts):
    """Centre line of a door: rectangle midline, else the farthest-apart pair."""
    if len(pts) == 4:
        (a, b, c, d) = pts
        e1 = ((a[0] + d[0]) / 2, (a[1] + d[1]) / 2), ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
        e2 = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), ((c[0] + d[0]) / 2, (c[1] + d[1]) / 2)
        length = lambda seg: math.dist(seg[0], seg[1])
        return max(e1, e2, key=length)
    best = (pts[0], pts[-1])
    for i, p in enumerate(pts):
        for q in pts[i + 1:]:
            if math.dist(p, q) > math.dist(*best):
                best = (p, q)
    return best


def _color(text):
    value = (text or '').strip().lstrip('#')
    if re.fullmatch(r'[0-9A-Fa-f]{6}', value):
        return 'ff' + value.lower(), True
    if re.fullmatch(r'[0-9A-Fa-f]{8}', value):
        return value.lower(), True
    return 'ffffffff', False


def image_size(source: ModuleSource, bitmap: str) -> tuple[int, int, bytes]:
    if not bitmap or Path(bitmap).suffix.lower() not in IMAGE_SUFFIXES:
        raise ModuleError('Unsupported or missing map image: ' + str(bitmap))
    data = source.read(bitmap, MAX_IMAGE_BYTES)
    try:
        with Image.open(io.BytesIO(data)) as picture:
            width, height = picture.size
    except Exception as exc:
        raise ModuleError('Unreadable map image: ' + bitmap) from exc
    if width * height > MAX_IMAGE_PIXELS:
        raise ModuleError('Map image exceeds 64 MP: ' + bitmap)
    return width, height, data


def _metadata_nodes(source, entry):
    """Elements holding grid/LoS/lights: the db.xml image node and its layers
    (FGU 4.3 stores occluders per layer), else the per-image sidecar XML."""
    node = entry['_node']
    nodes = [node] + node.findall('./layers/layer')
    if any(n.find('occluders') is not None or n.find('lights') is not None for n in nodes):
        return nodes, 'db.xml'
    sidecar = str(PurePosixPath(entry['bitmap']).with_suffix('.xml')) if entry['bitmap'] else None
    if sidecar and source.exists(sidecar):
        return [parse_xml(source.read(sidecar, MAX_XML_BYTES), sidecar)] + nodes, sidecar
    return nodes, 'none'


def _first(nodes, tag):
    for n in nodes:
        value = _text(n, tag)
        if value:
            return value
    return None


def _all(nodes, path):
    return [item for n in nodes for item in n.findall(path)]


def to_uvtt(source: ModuleSource, entry: dict, *, include_image=True, grid_size=None, squares=None) -> dict:
    """Convert one listed image to {'uvtt': ..., 'losses': [...], 'counts': {...}}.

    FG modules often do not store a grid size (e.g. FGU 4.3 maps with only
    <grid>on</grid>); pass grid_size (pixels per square) or squares (squares
    across the image width) then. A stored <gridsize> always wins.
    """
    width, height, data = image_size(source, entry['bitmap'])
    nodes, origin = _metadata_nodes(source, entry)
    losses = []
    stored = _first(nodes, 'gridsize')
    if stored:
        grid = _floats(stored, 'gridsize')
        if len(grid) != 2 or grid[0] <= 0:
            raise ModuleError(entry['record'] + ': malformed <gridsize>')
        if abs(grid[0] - grid[1]) > 1e-6:
            losses.append(('grid', 'approximate', f'non-square grid {grid[0]}x{grid[1]} px; using width'))
        true_ppg = grid[0]
    elif grid_size or squares:
        true_ppg = float(grid_size) if grid_size else width / float(squares)
        if not math.isfinite(true_ppg) or true_ppg < 4 or true_ppg > max(width, height):
            raise ModuleError(entry['record'] + ': grid size out of range')
        losses.append(('grid', 'manual', f'module stores no grid size; {true_ppg:g} px per square supplied by the user'))
    else:
        raise ModuleError(entry['record'] + ': module stores no grid size; supply pixels per square '
                          '(--grid-size) or squares across the map (--squares)')
    ppg = int(round(true_ppg))
    if ppg < 1:
        raise ModuleError(entry['record'] + ': grid size must round to at least one pixel per square')
    out_w, out_h = width, height
    if abs(ppg - true_ppg) > 1e-6:
        # UVTT needs whole pixels per square: resample the image so the grid stays exact.
        out_w, out_h = round(width * ppg / true_ppg), round(height * ppg / true_ppg)
        losses.append(('image', 'approximate', f'{true_ppg:g} px squares: image resampled {width}x{height} -> '
                                               f'{out_w}x{out_h} so each square is {ppg} px; geometry unchanged'))
    if out_w < 1 or out_h < 1 or out_w * out_h > MAX_IMAGE_PIXELS:
        raise ModuleError(entry['record'] + ': resampled map image exceeds dimension/64 MP limits')
    offset = _floats(_first(nodes, 'gridoffset') or '0,0', 'gridoffset')
    if any(abs(v) > 1e-6 for v in offset[:2]):
        losses.append(('grid', 'approximate', f'grid offset {offset[:2]} px not represented; grid starts at the image corner'))
    if (_first(nodes, 'gridtype') or 'square').lower() not in ('square', ''):
        losses.append(('grid', 'unsupported', 'non-square (hex/iso) grid type'))
    if entry['layers'] > 1:
        losses.append(('image', 'approximate', f"{entry['layers']} image layers; UVTT carries the first bitmap; native output audits additional layers separately"))
    frame = _Frame(width, height, true_ppg)

    walls, objects, portals = [], [], []
    counts = {'walls': 0, 'doors': 0, 'windows': 0, 'terrain': 0, 'lights': 0, 'lights_off': 0}
    for occ in _all(nodes, './occluders/occluder'):
        pts = _pairs(_floats(_text(occ, 'points'), entry['record'] + ' occluder'))
        if len(pts) < 2:
            continue
        flags = {child.tag for child in occ if child.text is None or not child.text.strip()}
        if 'terrain' in flags:
            counts['terrain'] += 1
            continue
        if 'toggleable' in flags:
            a, b = _door_bounds(pts)
            window = 'allow_vision' in flags
            counts['windows' if window else 'doors'] += 1
            pa, pb = frame.point(*a), frame.point(*b)
            portals.append({'position': {'x': (pa['x'] + pb['x']) / 2, 'y': (pa['y'] + pb['y']) / 2},
                            'bounds': [pa, pb],
                            'rotation': math.atan2(pb['y'] - pa['y'], pb['x'] - pa['x']),
                            'closed': not window and 'closed' in flags, 'freestanding': False})
            continue
        line = [frame.point(*p) for p in pts]
        if 'closed' in flags and line[0] != line[-1]:
            line.append(dict(line[0]))
        (objects if 'allow_vision' in flags else walls).append(line)
        counts['walls'] += 1
    if counts['terrain']:
        losses.append(('terrain', 'unsupported', f"{counts['terrain']} terrain/movement-only occluders not converted"))
    if counts['windows']:
        losses.append(('windows', 'approximate', f"{counts['windows']} windows written as open portals (see-through)"))
    if counts['doors']:
        losses.append(('doors', 'approximate', 'door centre line taken from the FG door shape; open/closed state as saved'))

    lights = []
    for light in _all(nodes, './lights/light'):
        pos = _floats(_text(light, 'position'), entry['record'] + ' light position')
        if len(pos) != 2:
            continue
        ranges = _floats(_text(light, 'range') or '', 'light range', even=False)
        radius = max(ranges[0::2]) if ranges else 0
        if radius <= 0:
            continue
        color, ok = _color(_text(light, 'color'))
        if not ok:
            losses.append(('lights', 'approximate', 'unreadable light colour replaced with white'))
        if light.find('on') is None:
            counts['lights_off'] += 1
        lights.append({'position': frame.point(*pos), 'range': radius, 'intensity': 1.0,
                       'color': color, 'shadows': True})
        counts['lights'] += 1
    if lights:
        losses.append(('lights', 'approximate', 'FG bright/dim falloff reduced to one radius (the larger)'))
    if counts['lights_off']:
        losses.append(('lights', 'approximate', f"{counts['lights_off']} lights saved off are retained in source metadata; native visibility applies the off state"))
    if origin == 'none':
        losses.append(('line_of_sight', 'manual', 'no line-of-sight/lighting data found for this map'))
    if entry['pins']:
        losses.append(('pins', 'manual', f"{entry['pins']} map pins (story/encounter links) not converted yet"))
    losses.append(('tokens', 'manual', 'tokens placed on FG maps are not read yet'))

    uvtt = {'format': 0.3,
            'resolution': {'map_origin': {'x': 0, 'y': 0},
                           'map_size': {'x': round(out_w / ppg, 6), 'y': round(out_h / ppg, 6)},
                           'pixels_per_grid': ppg},
            'line_of_sight': walls, 'objects_line_of_sight': objects, 'portals': portals,
            'environment': {'baked_lighting': False},
            'image': base64.b64encode(_resampled(data, out_w, out_h) if (out_w, out_h) != (width, height) else data
                                      ).decode('ascii') if include_image else 'omitted',
            'lights': lights}
    return {'record': entry['record'], 'name': entry['name'], 'bitmap': entry['bitmap'],
            'metadata_source': origin, 'size_px': [width, height], 'pixels_per_square': true_ppg, 'counts': counts,
            'losses': [{'field': f, 'grade': g, 'detail': d} for f, g, d in losses], 'uvtt': uvtt}


def _resampled(data, width, height):
    with Image.open(io.BytesIO(data)) as picture:
        out = io.BytesIO()
        picture.convert('RGBA' if picture.mode in ('RGBA', 'LA', 'P') else 'RGB').resize(
            (width, height), Image.LANCZOS).save(out, 'PNG')
        return out.getvalue()


def inventory(module) -> dict:
    with ModuleSource(module) as source:
        info = definition(source)
        maps = []
        for entry in list_images(source):
            row = {k: v for k, v in entry.items() if not k.startswith('_')}
            try:
                result = to_uvtt(source, entry, include_image=False)
                row.update(status='READABLE', counts=result['counts'], size_px=result['size_px'],
                           metadata_source=result['metadata_source'], losses=result['losses'],
                           pixels_per_square=result['pixels_per_square'])
            except ModuleError as exc:
                status = 'NEEDS_GRID' if 'no grid size' in str(exc) else 'BLOCKED'
                if status == 'NEEDS_GRID':
                    nodes, origin = _metadata_nodes(source, entry)
                    row.update(metadata_source=origin,
                               has_line_of_sight=any(n.find('occluders') is not None for n in nodes),
                               has_lights=any(n.find('lights') is not None for n in nodes))
                    if not entry.get('grid_on') and not row['has_line_of_sight'] and not row['has_lights']:
                        status = 'ART'  # no grid/geometry/lighting: a picture rather than a map
                row.update(status=status, reason=str(exc))
            maps.append(row)
        if not source.exists('db.xml'):
            info['note'] = 'No db.xml (player-only or asset module); no GM map records read.'
        return {'module': info, 'maps': maps}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only Fantasy Grounds module inventory / map to UVTT')
    parser.add_argument('module', help='.mod file or unpacked module folder')
    parser.add_argument('--map', help='record path (from the inventory) to convert')
    parser.add_argument('--out', help='new .uvtt file to write for --map (must not exist)')
    parser.add_argument('--grid-size', type=float, help='pixels per square, when the module stores none')
    parser.add_argument('--squares', type=float, help='squares across the map width, when the module stores none')
    parser.add_argument('--campaign-out', help='write native 5e notes for NPCs, items and story into a new directory')
    parser.add_argument('--install', action='store_true',
                        help='After --campaign-out, install the native-package.zip through the add-only path')
    parser.add_argument('--myassets', help='Actual MyAssets destination; required with --install')
    parser.add_argument('--backup-root', help='Separate existing full-backup directory; required with --install')
    args = parser.parse_args(argv)
    try:
        if args.install or args.myassets or args.backup_root or args.campaign_out:
            if args.install and (not args.myassets or not args.backup_root):
                raise ModuleError('--install requires --myassets and --backup-root')
            if not args.install and (args.myassets or args.backup_root):
                raise ModuleError('Installation destinations require explicit --install')
            if args.install and not args.campaign_out:
                import uuid
                args.campaign_out = str(Path.cwd() / ('ForgeBridge-fg-campaign-' + uuid.uuid4().hex[:10]))
            if not args.campaign_out:
                raise ModuleError('Provide --campaign-out, or --install with --myassets and --backup-root')
            from forgebridge.fg_campaign import write_campaign, install_campaign
            if args.install:
                report = install_campaign(args.module, args.campaign_out, args.myassets, args.backup_root)
            else:
                report = write_campaign(args.module, args.campaign_out)
            printed = {'evidence': report.get('evidence'), 'counts': report.get('counts'),
                       'losses': report.get('losses'), 'links': report.get('links'),
                       'native_package': report.get('native_package'),
                       'runtime_validation': report.get('runtime_validation')}
            if report.get('installation'):
                printed['installation'] = report['installation']
            print(json.dumps(printed, indent=2))
            if not args.map:
                return 0
        if not args.map:
            print(json.dumps(inventory(args.module), indent=2))
            return 0
        if not args.out:
            raise ModuleError('--map needs --out')
        with ModuleSource(args.module) as source:
            matches = [e for e in list_images(source) if e['record'] == args.map]
            if len(matches) != 1:
                raise ModuleError('Map record not found (or ambiguous): ' + args.map)
            result = to_uvtt(source, matches[0], grid_size=args.grid_size, squares=args.squares)
        with open(args.out, 'x', encoding='utf-8') as stream:
            json.dump(result['uvtt'], stream)
        print(json.dumps({k: v for k, v in result.items() if k != 'uvtt'}, indent=2))
        return 0
    except (ModuleError, OSError, ValueError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

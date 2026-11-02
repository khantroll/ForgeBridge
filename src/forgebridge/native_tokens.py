"""Experimental token target adapter, using an explicitly supplied native control.

Size is authoritative on Toolkit 0.5.1.18: transform-only scale is normalized on
load. Texture scaling is baked into a transparent canvas matching the control.
This module writes files only; it neither installs content nor executes scripts.
"""
import hashlib
import io
import math
import struct
import json
import re
from pathlib import Path, PurePosixPath
import zipfile

from PIL import Image, ImageOps

from forgebridge.native_images import native_image_pair
from forgebridge.native_map import AppendWriter, insert_markers, patch_stream
from forgebridge.nrbf import Reader
from forgebridge.token_ir import Token
from forgebridge.native_dependencies import read_export, write_member


def patch_note(data, token, image_path, *, metadata=False, native_size=None):
    reader = Reader(data)
    graph = reader.read()
    expected = 'ArkenNoteUpgradeMeta' if metadata else 'ArkenNoteUpgrade'
    if reader.objects[graph['root_id']]['class'] != expected:
        raise ValueError('Expected native token note control')
    writer, patches, sizes, icons = AppendWriter(reader), [], 0, 0
    for oid, obj in reader.objects.items():
        if not isinstance(obj, dict) or 'members' not in obj:
            continue
        for key, span in reader.member_spans[oid].items():
            bare = key.split('+')[-1]
            value = None
            if oid == graph['root_id'] and bare == '_name':
                value = writer.encoded(token.name)
            elif oid == graph['root_id'] and bare == '_tooltipSummary':
                value = writer.encoded('ForgeBridge source Token: ' + token.identity)
            elif obj['class'] == 'ArkenNoteIcon' and bare == '_iconPath':
                icons += 1
                value = writer.encoded(image_path)
            elif obj['class'] == 'ArkenNoteFieldSize' and bare == '_squareSizeNew':
                sizes += 1
                value = struct.pack('<f', token.footprint[0] if native_size is None else native_size)
            if value is not None:
                patches.append((*span, value))
    if icons != 1 or (not metadata and sizes != 1):
        raise ValueError('Control must have one icon and one native Size field')
    return patch_stream(reader, patches, writer)


def token_canvas(data, scale, edge):
    if not 1 <= edge <= 4096:
        raise ValueError('Control canvas exceeds token bound')
    with Image.open(io.BytesIO(data)) as source:
        if source.width * source.height > 16000000 or getattr(source, 'n_frames', 1) != 1:
            raise ValueError('Token slice requires static images below 16 megapixels')
        image = ImageOps.exif_transpose(source).convert('RGBA')
        if image.width != image.height:
            raise ValueError('Non-square token textures remain references')
        image = image.resize((max(1, round(edge * scale[0])), max(1, round(edge * scale[1]))),
                             Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (edge, edge))
        canvas.alpha_composite(image, ((edge - image.width) // 2, (edge - image.height) // 2))
        out = io.BytesIO(); canvas.save(out, 'PNG')
        return out.getvalue()


def png_control(data):
    """Convert the observed WEBP sentinel (-2) to the observed PNG sentinel (-1).

    The general image writer deliberately accepts PNG controls only. Keep this
    narrowly scoped to encoded static WEBP token controls, with their blob checked.
    """
    reader = Reader(data, max_items=64 * 1024 * 1024); reader.read()
    writer, patches = AppendWriter(reader), []
    blobs = [o['bytes'] for o in reader.objects.values() if isinstance(o, dict) and 'bytes' in o]
    for oid, obj in reader.objects.items():
        if not isinstance(obj, dict) or obj.get('class') != 'ArkenImage': continue
        m = obj['members']
        if (m['_packImgX'], m['_packImgY'], m['_packImgChannels']) == (-2, -2, 4):
            if len(blobs) != 1 or not bytes(blobs[0]).startswith(b'RIFF') or bytes(blobs[0])[8:12] != b'WEBP':
                raise ValueError('WEBP control sentinel does not match encoded data')
            for key in ('_packImgX', '_packImgY'):
                patches.append((*reader.member_spans[oid][key], struct.pack('<i', -1)))
    return patch_stream(reader, patches, writer, max_items=64 * 1024 * 1024) if patches else data


def token_files(map_data, tokens, textures, *, name, units_per_grid, origin,
                control_name, note_control, note_metadata, image_control,
                image_metadata, control_canvas_edge, control_units_per_grid, control_map_data=None,
                namespace=None):
    """Return a new native map, companion native files and an honest loss report.

    All source interpretation happens before this target adapter. Calibration is
    explicit, never inferred from source pixels. The manually placed control is
    preserved, along with every other existing map object.
    """
    if (not tokens or len(tokens) > 256 or not all(isinstance(t, Token) for t in tokens)
            or len({t.identity for t in tokens}) != len(tokens)):
        raise ValueError('Expected 1 to 256 unique IR tokens')
    if not math.isfinite(control_units_per_grid) or control_units_per_grid <= 0:
        raise ValueError('Invalid control calibration')
    if (not math.isfinite(units_per_grid) or units_per_grid <= 0 or len(origin) != 2
            or not all(math.isfinite(v) for v in origin)):
        raise ValueError('Invalid target calibration')
    # Read the saved control's Size/scale; callers must supply a normalized export.
    nr = Reader(note_control); nr.read()
    sizes = [o['members']['_squareSizeNew'] for o in nr.objects.values()
             if isinstance(o, dict) and o.get('class') == 'ArkenNoteFieldSize']
    mr = Reader(map_data if control_map_data is None else control_map_data); mr.read()
    def resolve(v): return mr.objects[v['ref']] if isinstance(v, dict) and 'ref' in v else v
    controls = [o['members'] for o in mr.objects.values() if isinstance(o, dict)
                and o.get('class') == 'ArkenTilePresetContentLink'
                and resolve(o['members'].get('_tileName')) == control_name]
    if len(sizes) != 1 or not math.isfinite(sizes[0]) or sizes[0] <= 0 or len(controls) != 1:
        raise ValueError('Expected one sized native control token')
    placement_type = resolve(controls[0].get('_defaultPlacementType'))
    if not isinstance(placement_type, dict) or placement_type.get('members', {}).get('value__') != 2:
        raise ValueError('Control must use native Token placement type')
    control_scale = resolve(controls[0]['_scale'])['members']
    if control_scale['x'] != control_scale['y'] or control_scale['x'] <= 0:
        raise ValueError('Control must have normalized square scale')
    files, placements, rows = {}, [], []
    for token in tokens:
        w, h = token.footprint
        if (not 0 < w <= 32 or w != h or not all(math.isfinite(v) for v in (*token.center,
                *token.texture_scale, token.rotation)) or not all(0 < v <= 1 for v in token.texture_scale)
                or type(token.hidden) is not bool):
            raise ValueError('Unsupported IR token geometry')
        # Identity, rather than readable name, determines stable collision-free paths.
        key = hashlib.sha256(((namespace + '\0' if namespace is not None else '') + token.identity).encode('utf8')).hexdigest()[:24]
        base = 'MyAssets/Encyclopedia/Notes/ForgeBridgeTokens/' + key
        media = 'MyAssets/Media/Encyclopedia/Tokens/ForgeBridgeTokens/' + key + '/Token'
        png = token_canvas(textures[token.texture], token.texture_scale, control_canvas_edge)
        full, thumb, image_report = native_image_pair(png_control(image_control), png_control(image_metadata), png)
        files[media + '.rwfile'], files[media + '.rwmeta'] = full, thumb
        native_size = token.footprint[0] * units_per_grid / control_units_per_grid
        if not 0 < native_size <= 32: raise ValueError('Calibrated native Size exceeds bound')
        files[base + '.rwnote'] = patch_note(note_control, token, media + '.rwmeta', native_size=native_size)
        files[base + '.rwmeta'] = patch_note(note_metadata, token, media + '.rwmeta', metadata=True)
        placements.append({'title': token.name, 'target': base + '.rwmeta',
                           'grid_position': dict(zip(('x', 'y'), token.center))})
        rows.append({'source_id': token.identity, 'texture': token.texture,
                     'footprint': list(token.footprint), 'texture_scale': list(token.texture_scale),
                     'native_size_squares': native_size,
                     'rotation_clockwise': token.rotation, 'hidden_flag': token.hidden,
                     'status': 'experimental_native_token', 'retained_only_fields': list(token.retained_only),
                     'approximations': ['Texture scale baked into centered RGBA canvas; pixel rounding/resampling',
                        'Native Size controls square footprint; no independent persistent transform scale'],
                     'unverified': ['Rotated token orientation', 'Actual player visibility of hidden token'],
                     'image': image_report})
    updated, report = insert_markers(map_data, placements, name=name, units_per_grid=units_per_grid,
                                     origin=origin, template_name=control_name, template_data=control_map_data)
    reader = Reader(updated); reader.read(); writer = AppendWriter(reader); patches = []
    targets = {p['target']: (t, r) for t, p, r in zip(tokens, placements, rows)}
    def value(v): return reader.objects[v['ref']] if isinstance(v, dict) and 'ref' in v else v
    for oid, obj in reader.objects.items():
        if not isinstance(obj, dict) or obj.get('class') != 'ArkenTilePresetContentLink': continue
        members = obj['members']; target = value(members['_contentBasePath'])
        if target not in targets: continue
        token, row = targets[target]
        scale = control_scale['x'] / sizes[0] * token.footprint[0] * units_per_grid / control_units_per_grid
        row['serialized_scale'] = scale
        for key, span in reader.member_spans[oid].items():
            bare = key.split('+')[-1]
            if bare == '_hidden': patches.append((*span, struct.pack('<?', token.hidden)))
            elif bare == '_rotation': patches.append((*span, struct.pack('<f', -token.rotation)))
            elif bare in ('_position', '_scale'):
                from forgebridge.native_map import clone
                vec = clone(reader, members[key]['ref'])
                vec.members.update(x=scale if bare == '_scale' else origin[0] + token.center[0] * units_per_grid,
                                   y=scale if bare == '_scale' else origin[1] - token.center[1] * units_per_grid)
                patches.append((*span, writer.encoded(vec)))
    updated = patch_stream(reader, patches, writer)
    for row, placement in zip(rows, report): row['placement'] = placement
    return updated, files, rows


def compile_scene_tokens(map_data, source_scene, package, control_files, control_map_path, *,
                         name, units_per_grid, control_units_per_grid, control_name, origin=(0., 0.), namespace=None):
    """Compose source-adapted tokens into an existing map using a separate control.

    Returns generated dependencies and explicit per-token refusals. The caller
    merges dependencies without overwriting unrelated native content.
    """
    from forgebridge.foundry_tokens import scene_tokens
    from forgebridge.uvtt import _package_file, _safe_ref
    from forgebridge.validate import InventoryFatal
    reader = Reader(control_files[control_map_path]); reader.read()
    def value(v): return reader.objects[v['ref']] if isinstance(v, dict) and 'ref' in v else v
    controls = [o['members'] for o in reader.objects.values() if isinstance(o, dict)
                and o.get('class') == 'ArkenTilePresetContentLink'
                and value(o['members'].get('_tileName')) == control_name]
    if len(controls) != 1: raise ValueError('Expected one named control')
    note_path = value(controls[0]['_contentBasePath'])
    note = control_files[note_path[:-7] + '.rwnote']
    nr = Reader(note); nr.read()
    icons = [o['members']['_iconPath'] for o in nr.objects.values()
             if isinstance(o, dict) and o.get('class') == 'ArkenNoteIcon']
    if len(icons) != 1: raise ValueError('Expected one token image')
    image_path = nr.objects[icons[0]['ref']]
    image = control_files[image_path[:-7] + '.rwfile']
    ir = Reader(image, max_items=64 * 1024 * 1024); ir.read()
    blobs = [o['bytes'] for o in ir.objects.values() if isinstance(o, dict) and 'bytes' in o]
    if len(blobs) != 1: raise ValueError('Expected one encoded control image')
    with Image.open(io.BytesIO(bytes(blobs[0]))) as control_image:
        if control_image.width != control_image.height: raise ValueError('Control image must be square')
        edge = control_image.width
    tokens, rejected = scene_tokens(source_scene)
    textures, ready = {}, []
    for token in tokens:
        try:
            safe, problem = _safe_ref(token.texture)
            if problem or not safe: raise ValueError('Unsafe source texture path')
            path = _package_file(Path(package), safe)
            if path.stat().st_size > 32 * 1024 * 1024: raise ValueError('Source texture exceeds bound')
            with path.open('rb') as stream:
                data = stream.read(32 * 1024 * 1024 + 1)
            if len(data) > 32 * 1024 * 1024:
                raise ValueError('Source texture exceeds bound')
            token_canvas(data, token.texture_scale, edge)  # refuse unsupported media before any output
            textures[token.texture] = data
            ready.append(token)
        except (ValueError, OSError, InventoryFatal) as exc:
            rejected.append({'source_id': token.identity, 'status': 'unsupported', 'reason': str(exc)})
    if not ready:
        return map_data, {}, [], rejected
    updated, generated, rows = token_files(map_data, ready, textures, name=name,
        units_per_grid=units_per_grid, origin=origin, control_name=control_name,
        note_control=note, note_metadata=control_files[note_path], image_control=image,
        image_metadata=control_files[image_path], control_canvas_edge=edge,
        control_units_per_grid=control_units_per_grid,
        control_map_data=control_files[control_map_path], namespace=namespace)
    return updated, generated, rows, rejected


def write_token_zip(template_pack, companion, package, dest, *, name,
                    units_per_grid, control_units_per_grid, control_name,
                    origin=(0., 0.)):
    """Build from a native export containing the sized control and its assets."""
    from forgebridge.native_map import rename_metadata
    dest = Path(dest)
    if dest.exists() or dest.is_symlink(): raise ValueError('Choose a new output filename')
    if (not name or len(name) > 128 or PurePosixPath(name).name != name
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', name) or name.endswith(('.', ' '))
            or name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL',
                *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}):
        raise ValueError('Invalid native map filename')
    if Path(companion).stat().st_size > 64 * 1024 * 1024:
        raise ValueError('Companion exceeds bound')
    source = json.loads(Path(companion).read_text(encoding='utf8'))
    files = read_export(template_pack)
    paths = list(files)
    maps = [p for p in paths if p.endswith('.rwmap')]
    if len(maps) != 1: raise ValueError('Expected one native map')
    map_path = maps[0]; meta_path = map_path[:-6] + '.rwmeta'
    updated, generated, rows, rejected = compile_scene_tokens(files[map_path], source['source_scene'],
        package, files, map_path, name=name, units_per_grid=units_per_grid, origin=origin,
        control_name=control_name, control_units_per_grid=control_units_per_grid)
    if not rows:
        raise ValueError('No supported tokens; refusals: ' + json.dumps(rejected, ensure_ascii=True))
    for path in generated:
        if path in files: raise ValueError('Generated token would replace exported content; use a clean control export')
    # Native note metadata can link back to its original map. Preserve that
    # control map and metadata as dependencies rather than changing user notes
    # or leaving a dangling link after renaming the generated map.
    metadata = rename_metadata(files[meta_path], name)
    base = str(PurePosixPath(map_path).parent / name)
    if base + '.rwmap' in files or base + '.rwmeta' in files:
        raise ValueError('Choose a distinct map name; the control map is preserved')
    files[base + '.rwmap'], files[base + '.rwmeta'] = updated, metadata
    files.update(generated)
    report = {'status': 'experimental; generated files are not runtime PASS evidence',
        'preserved_control_map': map_path,
        'calibration': {'units_per_grid': units_per_grid, 'origin': list(origin),
                        'control_units_per_grid': control_units_per_grid},
        'tokens': rows, 'unsupported': rejected,
        'limits': ['No actors, stat blocks, scripts, vision, fog, light animation or combat behavior converted',
                   'Labels off; actual player visibility unverified'],
        'source_scene': source['source_scene']}
    files['token-report.json'] = json.dumps(report, indent=2, ensure_ascii=True).encode()
    files['INSTALL.txt'] = (f'Open separate test map {name}. Close Toolkit before installing.\n'
        'Preserve MyAssets; copy only absent files or byte-identical dependencies. Abort on conflicts.\n'
        'Do not overwrite manually edited notes. Keep token-report.json outside MyAssets.\n').encode()
    if sum(map(len, files.values())) > 256 * 1024 * 1024: raise ValueError('Output exceeds bound')
    from forgebridge.native_dependencies import write_archive
    write_archive(dest, files)
    return {k: v for k, v in report.items() if k != 'source_scene'}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('template-pack', 'companion', 'package', 'out', 'name', 'control-name'):
        parser.add_argument('--' + arg, required=True)
    parser.add_argument('--units-per-grid', type=float, required=True)
    parser.add_argument('--control-units-per-grid', type=float, required=True)
    parser.add_argument('--origin', nargs=2, type=float, default=(0., 0.))
    args = vars(parser.parse_args())
    args['dest'] = args.pop('out')
    print(json.dumps(write_token_zip(**args), indent=2))


if __name__ == '__main__': main()

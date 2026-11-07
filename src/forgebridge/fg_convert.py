"""Fantasy Grounds source orchestration over the shared native target writer."""
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile
import zipfile

from forgebridge.fantasy_grounds import ModuleSource, inventory, list_images, to_uvtt
from forgebridge.direct_package import geometry_files
from forgebridge.native_dependencies import write_archive, merge_native, check_metadata_references
from forgebridge.output_names import plan_names, sanitize_name
from forgebridge.scene_profile import canonical_hash, fingerprint
from forgebridge.validate import validate, load_schema, repo_schema


def is_fg_input(path):
    path = Path(path).absolute()
    if any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
        raise ValueError('Source path must not contain links or junctions')
    if path.suffix.lower() == '.mod' and path.is_file():
        return True
    if path.is_dir():
        if any((path / name).is_file() for name in ('module.json', 'world.json', 'system.json')):
            return False
        return any(p.name.casefold() == 'definition.xml' for p in path.iterdir())
    if path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = [n.filename.replace('\\', '/').casefold() for n in archive.infolist()]
            if any(n in names for n in ('module.json', 'world.json', 'system.json')):
                return False
            if 'definition.xml' in names:
                return True
            if any(len(n.split('/')) == 2 and n.split('/')[-1] in ('module.json', 'world.json', 'system.json') for n in names):
                return False
            return any(re.fullmatch(r'modules/[^/]+/definition\.xml', n) for n in names)
    return False


def discover_fg(package, *, include_art=False):
    data = inventory(package)
    definition = data['module']
    module = definition.get('displayname') or definition.get('name') or 'ForgeBridge'
    scenes = []
    for entry in data['maps']:
        if entry['status'] == 'ART' and not include_art:
            continue
        key = hashlib.sha256(json.dumps(['fantasy_grounds', definition.get('name'), entry['record']]).encode()).hexdigest()[:24]
        scenes.append({**entry, 'key': key, 'id': entry['record'], 'source_type': 'fantasy_grounds',
                       'source_path': 'db.xml', 'parent_adventure_id': None, 'parent_adventure_name': module,
                       'module_name': module})
    if len({s['key'] for s in scenes}) != len(scenes):
        raise ValueError('Duplicate Fantasy Grounds image record identity')
    return {'source_type': 'fantasy_grounds', 'module_definition': definition,
            'package_id': definition.get('name'), 'package_title': module, 'scenes': scenes,
            'hidden_art': sum(r['status'] == 'ART' for r in data['maps']) if not include_art else 0}


def grid_options(values, rows, label):
    result = {}
    entries = values.items() if isinstance(values, dict) else (values or [])
    keys = {r['key'] for r in rows}
    for entry in entries:
        if isinstance(entry, tuple): key, value = entry
        elif '=' in str(entry): key, value = str(entry).split('=', 1)
        elif len(rows) == 1: key, value = rows[0]['key'], entry
        else: raise ValueError(f'{label} needs KEY=VALUE when multiple maps are selected')
        if key not in keys or key in result:
            raise ValueError(f'{label}: unknown or repeated map key {key}')
        try: number = float(value)
        except (ValueError, TypeError) as exc: raise ValueError(f'{label} needs a positive number') from exc
        if not math.isfinite(number) or number <= 0:
            raise ValueError(f'{label} needs a finite positive number')
        result[key] = number
    return result


def convert_fg(package, destination, *, scene_ids=(), scene_keys=(), profiles=(), map_folder=None,
               notes_folder=None, map_names=None, include_art=False, grid_size=(), squares=(), notes_only=False):
    from forgebridge.convert import _new_destination, publish
    package = Path(package).absolute()
    destination = _new_destination(destination, package)
    before = fingerprint(package)
    discovery = discover_fg(package, include_art=include_art)
    rows = discovery['scenes']
    if profiles:
        raise ValueError('Foundry scene profiles are not supported for Fantasy Grounds inputs')
    if scene_ids and scene_keys:
        raise ValueError('Select by scene IDs or scoped keys, not both')
    selected = set(scene_keys or scene_ids)
    if selected:
        field = 'key' if scene_keys else 'id'
        if selected - {r[field] for r in rows}:
            raise ValueError('Fantasy Grounds map key not found; use --include-art to select ART records')
        rows = [r for r in rows if r[field] in selected]
    if notes_only:
        if selected: raise ValueError('--notes-only cannot select maps')
        rows = []
    if not 0 <= len(rows) <= 256:
        raise ValueError('Select between 1 and 256 Fantasy Grounds maps; use --include-art for artwork')
    grids, across = grid_options(grid_size, rows, '--grid-size'), grid_options(squares, rows, '--squares')
    names = plan_names(rows, discovery['package_title'], map_folder=map_folder,
                       notes_folder=notes_folder, map_names=map_names)
    report = {'format': 'forgebridge.conversion', 'version': 1, 'source_type': 'fantasy_grounds',
              'module_definition': discovery['module_definition'], 'source_sha256': before, 'status': 'PASS',
              'scenes': [], 'counts': {g: 0 for g in ('native', 'approximate', 'manual', 'unsupported')},
              'counts_scope': 'FG mapping loss lines; source shapes and native segment records reported separately',
              'native_counts': {'scenes': 0, 'tokens': 0, 'rejected_tokens': 0, 'notes': 0, 'markers': 0, 'actors':0, 'items':0, 'spells':0, 'stories':0, 'images':0, 'tables':0, 'reference_pages':0, 'reference_chapters':0, 'parcels':0, 'quests':0, 'table_references':0},
              'native_losses': [], 'runtime_validation': 'not performed', 'installed': False,
              'manual_steps': ['Labels off; NPC links on tokens omitted to preserve portrait rendering; uncalibrated artwork remains a note attachment, not a map',
                               'FG @* resolves unique converted local targets only; external modules are not loaded',
                               'Review losses and native fog/player framing; generated files are not runtime validation']}
    combined = {}
    with tempfile.TemporaryDirectory(prefix='forgebridge-fg-') as tmp, ModuleSource(package) as source:
        stage = Path(tmp)
        from forgebridge.fg_campaign import build_campaign
        campaign_folder = sanitize_name(notes_folder or map_folder or discovery['package_title'])
        campaign_files, campaign = build_campaign(package, notes_folder=campaign_folder)
        merge_native(combined, {n:d for n,d in campaign_files.items() if n.startswith('MyAssets/')})
        report['campaign_content'] = [campaign]
        report['native_counts'].update({k:v for k,v in campaign['counts'].items() if k in report['native_counts']})
        report['native_losses'].append({'scope':'campaign','losses':campaign['losses']})
        for loss in campaign['losses']: report['counts'][loss['grade']] += 1
        report['unbuilt_images'] = [r for r in inventory(package)['maps'] if r['record'] not in {x['id'] for x in rows}]
        entries = {e['record']: e for e in list_images(source)}
        for index, row in enumerate(rows, 1):
            folder = stage / f'scene-{index:03d}'; folder.mkdir()
            item = {**row, 'folder': folder.name}
            try:
                if row['status'] == 'BLOCKED': raise ValueError(row['reason'])
                if row['status'] != 'READABLE' and row['key'] in grids and row['key'] in across:
                    raise ValueError('Choose pixels per square OR squares across for this map')
                result = to_uvtt(source, entries[row['id']], grid_size=grids.get(row['key']), squares=across.get(row['key']))
                errors = validate(result['uvtt'], load_schema(repo_schema('uvtt-core.schema.json')))
                if errors: raise ValueError('Invalid FG UVTT: ' + '; '.join(errors))
                scope = canonical_hash(['native-scene-schema-v1', 'fantasy_grounds', before, row['id']])[:20]
                files, synthesis, background, omitted = geometry_files(result['uvtt'], scope,
                    name=names[row['key']]['map_name'], map_path=names[row['key']]['map_path'])
                from forgebridge.fg_layers import layer_ir
                from forgebridge.native_layers import add_layers
                layer_records, layer_losses = layer_ir(source, entries[row['id']], result)
                files[names[row['key']]['map_path']], layer_files, layer_report = add_layers(files[names[row['key']]['map_path']], layer_records, scope, synthesis['image_meta_path'], background['dimensions'])
                merge_native(files, layer_files)
                layer_report['losses'].extend(layer_losses)
                from forgebridge.fg_scene import add_placements
                files[names[row['key']]['map_path']], placed_files, placement_report = add_placements(
                    files[names[row['key']]['map_path']], source, entries[row['id']], result, campaign,
                    name=names[row['key']]['map_name'], scope=scope, staged_root=stage/'source-media')
                merge_native(files, placed_files)
                merge_native(files, {n:d for n,d in campaign_files.items() if n.startswith('MyAssets/')})
                losses = [l for l in result['losses'] if l['field'] not in ('pins','tokens')] + [
                    {'field':l['feature'],'grade':l['grade'],'detail':l['summary'],**l} for l in placement_report['losses']] + [
                    {'field': 'environment', 'grade': 'manual', 'detail': 'FG ambient/tint settings are not mapped; native environment defaults are used'},
                    {'field': 'fog-vision', 'grade': 'manual', 'detail': 'Native fog configuration mapped separately where stored; saved FG explored masks are not converted'}]
                losses += [{'field':l['feature'],'grade':l['grade'],'detail':l['summary'],**l} for l in layer_report['losses']]
                if result['counts']['lights']:
                    losses.append({'field': 'native-light-rendering', 'grade': 'approximate',
                                   'detail': 'Native writer uses observed UVTT-import light defaults; source color/falloff equivalence is not established'})
                if result['uvtt']['objects_line_of_sight']:
                    losses.append({'field': 'objects_line_of_sight', 'grade': 'unsupported',
                                   'detail': 'See-through non-door occluders are retained in UVTT, not emitted by the native writer'})
                if omitted:
                    losses.append({'field': 'lights', 'grade': 'unsupported', 'detail': 'Native writer omitted lights without a positive radius'})
                from forgebridge.visibility_ir import fg_visibility
                from forgebridge.native_visibility import apply_visibility
                files[names[row['key']]['map_path']], visibility = apply_visibility(
                    files[names[row['key']]['map_path']], fg_visibility(source,entries[row['id']],result), namespace=scope)
                losses += [{'field':l['feature'],'grade':l['grade'],'detail':l['summary'],**l} for l in visibility['losses']]
                fg = {k: v for k, v in result.items() if k != 'uvtt'}
                fg.update(pins=row['pins'], resampling={'source_size_px': result['size_px'],
                    'output_size_px': background['dimensions'], 'applied': result['size_px'] != background['dimensions']},
                    uvtt_pixels_per_grid=result['uvtt']['resolution']['pixels_per_grid'], losses=losses)
                native = {'output_names': names[row['key']], 'source_type': 'fantasy_grounds', 'fantasy_grounds': fg,
                          'visibility': visibility, 'bitmap_layers': layer_report,
                          'counts': {'notes': campaign['counts']['notes'], 'native_tokens': len(placement_report['tokens']), 'unsupported_tokens': len(placement_report['rejected_tokens']), 'native_pdf_pages': 0},
                          'campaign_content': campaign, 'placements': placement_report,
                          'native_map': {'name': names[row['key']]['map_name'], 'markers': len(placement_report['markers']), 'marker_labels': 'off',
                                         **synthesis['calibration']},
                          'native_synthesis': {**synthesis, 'background': background, 'scope': scope,
                                               'runtime_validation': 'not performed'},
                          'closed_metadata_references': check_metadata_references(files)}
                files.update({'conversion-report.json': json.dumps(native, indent=2).encode(),
                              'fg-source.json': json.dumps(fg, indent=2).encode()})
                write_archive(folder / 'native-package.zip', files)
                write_archive(folder / 'uvtt-package.zip', {'scene.uvtt': json.dumps(result['uvtt']).encode(),
                                                          'fg-source.json': json.dumps(fg, indent=2).encode()})
                candidate = {n: d for n, d in files.items() if n.startswith('MyAssets/')}
                additions = {n: d for n, d in candidate.items() if n not in combined}
                if len(combined) + len(additions) > 16384 or sum(map(len, combined.values())) + sum(map(len, additions.values())) > 1024**3:
                    raise ValueError('Combined native output exceeds limits; select fewer maps')
                merge_native(combined, candidate)
                item.update(status='BUILT', artifact='native-package.zip', fantasy_grounds=fg, native_report=native)
                report['native_counts']['scenes'] += 1
                report['native_counts']['markers'] += len(placement_report['markers'])
                report['native_counts']['tokens'] += len(placement_report['tokens'])
                report['native_counts']['rejected_tokens'] += len(placement_report['rejected_tokens'])
                for loss in losses: report['counts'][loss['grade']] += 1
                report['native_losses'].append({'scene_id': row['id'], 'folder': folder.name, 'losses': losses})
            except (ValueError, OSError) as exc:
                item.update(status='REJECTED', error=str(exc)); report['status'] = 'PARTIAL'
                report['counts']['unsupported'] += 1
            report['scenes'].append(item)
        if not combined:
            raise ValueError('No readable maps or campaign notes in this module')
        if len(combined)>16384 or sum(map(len,combined.values()))>1024**3:
            raise ValueError('Combined native output exceeds 1 GiB / file limits')
        report['closed_native_metadata_references'] = check_metadata_references(combined)
        report['combined_artifact'] = 'native-package.zip'
        write_archive(stage / report['combined_artifact'], {**combined, 'conversion-report.json':json.dumps(report,indent=2).encode()})
        import shutil
        shutil.rmtree(stage/'source-media',ignore_errors=True)
        report['closed_native_metadata_references'] = check_metadata_references(combined)
        for name, data in combined.items():
            target = stage / name; target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream: stream.write(data)
        if fingerprint(package) != before:
            raise ValueError('Fantasy Grounds source changed during conversion; nothing published')
        publish(stage, destination, package, report)
    return report

"""Build a complete native scene using schema controls and existing target writers."""
import base64
import json
from pathlib import Path
import math
import tempfile

from forgebridge.native import Writer
from forgebridge.native_map import clone
from forgebridge.native_dependencies import read_package, write_archive, check_metadata_references
from forgebridge.native_scene import synthesize_map, background_asset, map_metadata, UNITS_PER_GRID
from forgebridge.nrbf import Reader
from forgebridge.package import build_package
from forgebridge.scene_profile import canonical_hash
from forgebridge.scene_records import blank_map, template_map, asset_templates, record, encode, control_files
from forgebridge.uvtt import _parent_adventure_id


def geometry_files(uvtt, scope, *, name, map_path):
    """Source-independent UVTT → schema-native map/background, no notes or tokens."""
    media_base = 'MyAssets/Media/Cartographer/Quick Import/ForgeBridge-' + scope + '/Background'
    image = base64.b64decode(uvtt['image'], validate=True)
    omitted_lights = [light for light in uvtt.get('lights', []) if type(light.get('range')) not in (int, float)
                      or not math.isfinite(light['range']) or light['range'] <= 0]
    geometry_uvtt = {**uvtt, 'lights': [light for light in uvtt.get('lights', []) if light not in omitted_lights]}
    geometry, synthesis = synthesize_map(blank_map(), template_map(), geometry_uvtt, name=name,
        image_meta_path=media_base + '.rwmeta', asset_name='Background')
    asset, metadata, background = background_asset(*asset_templates(), image, 'Background')
    exports = {map_path: geometry,
        map_path[:-6] + '.rwmeta': map_metadata(encode(record('map_meta')), name, image),
        media_base + '.rwfile': asset, media_base + '.rwmeta': metadata}
    return exports, synthesis, background, omitted_lights


def build_direct(package, document, row, package_id, destination, *, names, pdf_pages=False, campaign=None, foundry_data=None):
    scene = document['source_scene']
    scope = canonical_hash(['native-scene-schema-v1', package_id, row.get('source_path'),
                            _parent_adventure_id(row), scene])[:20]
    name = names['map_name']
    geometry_path = 'MyAssets/Maps/ForgeBridge/_ForgeBridgeSchemaGeometry.rwmap'
    exports, synthesis, background, omitted_lights = geometry_files(document['uvtt'], scope,
        name='_ForgeBridgeSchemaGeometry', map_path=geometry_path)
    uvtt = document['uvtt']
    with tempfile.TemporaryDirectory(prefix='forgebridge-direct-') as tmp:
        root = Path(tmp)
        companion = root / 'scene.json'
        companion.write_text(json.dumps({'schema_version': '1.0', 'scene_id': scene['_id'],
            'campaign_links': campaign[1]['links'] if campaign else {},
            **{k: document[k] for k in ('source_scene', 'scene_notes', 'loss_report')}}), encoding='utf-8')
        write_archive(root / 'geometry.zip', exports)
        marker, token, media = control_files()
        for label, files in [('marker', marker), ('token', token), ('media', media)]:
            write_archive(root / (label + '.zip'), files)
        staged = root / 'combined.zip'
        report = build_package(companion, root / 'geometry.zip', root / 'media.zip', staged,
            name=name, note_folder=names['notes_folder'], note_prefix=scope + '-', pdf_pages=pdf_pages,
            units_per_grid=UNITS_PER_GRID, origin=(0., 0.), package=package,
            template_name='ForgeBridge Control', marker_template_pack=root / 'marker.zip',
            token_control_pack=root / 'token.zip', token_control_name='ForgeBridge Control',
            control_units_per_grid=UNITS_PER_GRID, geometry_map_path=geometry_path,
            asset_namespace=scope,             token_namespace=scope,
            campaign_dependencies=campaign[0] if campaign else None,
            foundry_data=foundry_data)
        files = read_package(staged)
        # These are owned generated controls, not exported user content. Re-emit
        # token notes to discard unreachable strings retained by byte patching.
        for path, data in list(files.items()):
            if path.startswith('MyAssets/Encyclopedia/Notes/ForgeBridgeTokens/'):
                reader = Reader(data); graph = reader.read()
                files[path] = Writer(reader.libraries).write(clone(reader, graph['root_id']))
        removed = []
        for path in list(files):
            if (path in (geometry_path, geometry_path[:-6] + '.rwmeta') or
                path.startswith(('MyAssets/Maps/_ForgeBridgeSchemaControl.',
                                 'MyAssets/Encyclopedia/Notes/GeneratedControls/',
                                 'MyAssets/Media/Encyclopedia/Images/GeneratedControls/'))):
                removed.append(path); del files[path]
        old_map = 'MyAssets/Maps/ForgeBridge/' + name
        new_map = names['map_path'][:-6]
        for suffix in ('.rwmap', '.rwmeta'):
            files[new_map + suffix] = files.pop(old_map + suffix)
        report['output_names'] = dict(names)
        if campaign:
            from forgebridge.native_dependencies import merge_native
            from forgebridge.native_campaign import link_token_actors
            merge_native(files, campaign[0])
            report['campaign_content'] = campaign[1]
            report['campaign_token_links'] = link_token_actors(files, scene, scope, campaign[1])
        from forgebridge.native_tiles import add_tiles
        files[names['map_path']], tile_files, tile_report = add_tiles(files[names['map_path']], scene, package, scope, foundry_data)
        from forgebridge.native_dependencies import merge_native
        merge_native(files, tile_files)
        report['static_tiles'] = tile_report
        from forgebridge.native_ambience import add_ambience
        files[names['map_path']], audio_files, audio_report = add_ambience(files[names['map_path']], scene, package, scope)
        merge_native(files, audio_files)
        report['ambient_sounds'] = audio_report
        report['closed_metadata_references'] = check_metadata_references(files)
        report['native_synthesis'] = {**synthesis, 'background': background,
            'schema_version': 1, 'toolkit_reference': '0.5.1.18', 'scope': scope,
            'runtime_validation': 'not performed for this output', 'removed_generated_controls': sorted(removed),
            'omitted_lights': [{'uvtt_index': i, 'reason': 'No supported positive radius; source retained'}
                               for i, light in enumerate(uvtt.get('lights', [])) if light in omitted_lights],
            'losses': [{'grade': 'approximate', 'feature': 'light-rendering',
                       'summary': 'Uses the observed Toolkit UVTT-import color/intensity defaults, not independent Foundry color/animation equivalence'},
                      {'grade': 'manual', 'feature': 'environment',
                       'summary': 'Uses the known native container defaults; source ambient/time-of-day/environment settings remain retained rather than independently mapped'},
                      {'grade': 'manual', 'feature': 'fog-vision',
                       'summary': 'Fresh native manual fog starts covered; Foundry exploration/token vision is not converted'}]}
        files['conversion-report.json'] = json.dumps(report, indent=2).encode()
        write_archive(destination, files)
    return report

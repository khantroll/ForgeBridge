"""Build one native map, note and media package from calibrated inputs."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import zipfile

from forgebridge.handouts import write_handouts_zip
from forgebridge.native_images import write_source_images_zip
from forgebridge.native_map import write_map_zip

MAX_TOTAL = 256 * 1024 * 1024


def build_package(companion, map_template, media_template, dest, *, name,
                  note_folder, units_per_grid, origin=(0., 0.), package=None,
                  media_bundle=None, pdf_pages=False, template_name='FB Cal A',
                  regenerate_notes=False, token_control_pack=None, token_control_name=None,
                  control_units_per_grid=None, marker_template_pack=None):
    if (package is None) == (media_bundle is None):
        raise ValueError('Provide exactly one source package or collected media bundle')
    token_options = (token_control_pack, token_control_name, control_units_per_grid)
    if any(v is not None for v in token_options) and not all(v is not None for v in token_options):
        raise ValueError('Tokens require control pack, control name and control units per grid')
    if token_control_pack is not None and (package is None or not Path(package).is_dir()):
        raise ValueError('Tokens require the original source package directory for texture resolution')
    dest = Path(dest)
    if dest.exists() or dest.is_symlink():
        raise ValueError('Choose a new output filename')
    with tempfile.TemporaryDirectory(prefix='forgebridge-package-') as tmp:
        root = Path(tmp)
        if package is not None:
            media_bundle = root / 'collected.zip'
            collection = write_handouts_zip(package, companion, media_bundle)
        else:
            collection = None
        map_zip, notes_zip = root / 'map.zip', root / 'notes.zip'
        map_report = write_map_zip(map_template, companion, map_zip, name=name,
            units_per_grid=units_per_grid, origin=origin, template_name=template_name,
            marker_labels=False, note_folder=note_folder, marker_template_pack=marker_template_pack)
        preserved = map_report['preserved_exported_note_files']
        if preserved and not regenerate_notes:
            raise ValueError('Export contains existing generated notes. Back up manual edits and use --regenerate-notes to replace them')
        report = write_source_images_zip(companion, media_bundle, media_template,
            notes_zip, pdf_pages=pdf_pages, note_folder=note_folder, map_markers=True)
        if report['native_folder'] != map_report['native_folder']:
            raise ValueError('Map and media note folders do not match')
        with zipfile.ZipFile(map_zip) as archive:
            files = {n: archive.read(n) for n in archive.namelist()}
        with zipfile.ZipFile(notes_zip) as archive:
            for n in archive.namelist():
                data = archive.read(n)
                # Newly compiled notes replace the text-only map-stage notes.
                generated_note = n.startswith(report['native_folder'] + '/') and n.endswith(('.rwnote', '.rwmeta'))
                if n in files and files[n] != data and not generated_note and n not in ('INSTALL.txt', 'conversion-report.json'):
                    raise ValueError('Media conflicts with exported content: ' + n)
                files[n] = data
        report['native_map'] = map_report['native_map']
        report['placements'] = map_report['placements']
        report['regenerated_exported_note_files'] = preserved
        report['status'] = 'Combined native package built; check this scene in Toolkit. See STATUS.md for tested scenes. Player visibility remains unverified.'
        if collection is not None:
            files['handout-report.json'] = json.dumps(collection, indent=2).encode()
        if token_control_pack is not None:
            from forgebridge.native_dependencies import read_export, merge_native
            from forgebridge.native_tokens import compile_scene_tokens
            controls = read_export(token_control_pack)
            control_maps = [p for p in controls if p.endswith('.rwmap')]
            if len(control_maps) != 1:
                raise ValueError('Expected one token control map')
            map_path = next(p for p in files if p.endswith('/' + name + '.rwmap'))
            source = json.loads(Path(companion).read_text(encoding='utf8'))
            updated, generated, rows, rejected = compile_scene_tokens(files[map_path], source['source_scene'],
                package, controls, control_maps[0], name=name, units_per_grid=units_per_grid,
                origin=origin, control_name=token_control_name, control_units_per_grid=control_units_per_grid,
                namespace=name)
            merge_native(files, controls)
            if set(generated) & set(files):
                raise ValueError('Generated tokens conflict with existing exported content; use a clean source export')
            merge_native(files, generated)
            files[map_path] = updated
            token_report = {'tokens': rows, 'unsupported': rejected, 'native_namespace': name,
                'calibration': {'units_per_grid': units_per_grid, 'origin': list(origin),
                                'control_units_per_grid': control_units_per_grid},
                'source_scene': source['source_scene'],
                'limits': ['No actor/stat blocks, scripts, vision/fog or procedural light animation converted',
                           'GIF migration remains manual; labels off; runtime validation is separate']}
            files['token-report.json'] = json.dumps(token_report, indent=2).encode()
            report['token_conversion'] = {k: v for k, v in token_report.items() if k != 'source_scene'}
            report['counts']['native_tokens'] = len(rows)
            report['counts']['unsupported_tokens'] = len(rejected)
        from forgebridge.native_dependencies import check_metadata_references
        report['closed_metadata_references'] = check_metadata_references(files)
        for placement in report['placements']:
            if placement['target'] not in files:
                raise ValueError('Room marker target is missing')
        for attachment in report['attached_media']:
            if attachment['target'] not in files:
                raise ValueError('Media attachment target is missing')
        files['conversion-report.json'] = json.dumps(report, indent=2).encode()
        files['INSTALL.txt'] = (f'ForgeBridge complete native package: {name}\n\n'
            'Close Arkenforge and back up MyAssets, including manually edited notes.\n'
            'Extract outside Arkenforge; merge MyAssets into the EXISTING MyAssets.\n'
            f'Open map: {name}\nNotes folder: {note_folder}\n'
            'The output reflects the supplied map export, not later edits in Toolkit.\n'
            'Generated source notes are regenerated; retain manual edits in your backup.\n'
            'Check marker positions/targets, images, PDF page order/readability,\n'
            'door blocking, note/map reopening and Toolkit restart.\n'
            'PDF originals and reports stay outside MyAssets. PDFs are page images\n'
            'when --pdf-pages is enabled; otherwise they remain references.\n'
            'Labels are off. Native marker icons are retained. Player visibility is unverified.\n'
            'If UVTT automatic opening fails, open the saved map from the map browser.\n').encode()
        if len(files) > 8192 or sum(map(len, files.values())) > MAX_TOTAL:
            raise ValueError('Combined native package exceeds size limits')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for n, data in files.items():
                archive.writestr(n, data)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--package', help='Original Foundry package ZIP or directory')
    source.add_argument('--media-bundle', help='Previously collected bundle for this companion')
    parser.add_argument('--companion', required=True)
    parser.add_argument('--map-template', required=True, help='Native saved-map export with calibration marker')
    parser.add_argument('--media-template', required=True, help='Native image note export')
    parser.add_argument('--name', required=True, help='Separate output map name')
    parser.add_argument('--note-folder', required=True, help='Readable folder unique to this scene/package')
    parser.add_argument('--units-per-grid', required=True, type=float)
    parser.add_argument('--origin', nargs=2, type=float, default=(0., 0.))
    parser.add_argument('--template-name', default='FB Cal A')
    parser.add_argument('--pdf-pages', action='store_true')
    parser.add_argument('--regenerate-notes', action='store_true')
    parser.add_argument('--marker-template-pack', help='Separate native marker control export when absent from geometry map')
    parser.add_argument('--token-control-pack', help='Native export with sized control token and closed dependencies')
    parser.add_argument('--token-control-name')
    parser.add_argument('--control-units-per-grid', type=float)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    try:
        report = build_package(args.companion, args.map_template, args.media_template,
            args.out, name=args.name, note_folder=args.note_folder,
            units_per_grid=args.units_per_grid, origin=args.origin, package=args.package,
            media_bundle=args.media_bundle, pdf_pages=args.pdf_pages,
            template_name=args.template_name, regenerate_notes=args.regenerate_notes,
            marker_template_pack=args.marker_template_pack, token_control_pack=args.token_control_pack,
            token_control_name=args.token_control_name, control_units_per_grid=args.control_units_per_grid)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    c = report['counts']
    print(f"Built {report['native_map']['markers']} room markers, {c['notes']} notes and {c['native_image_attachments']} image/PDF attachments. See conversion-report.json.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

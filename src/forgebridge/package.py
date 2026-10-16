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
                  regenerate_notes=False):
    if (package is None) == (media_bundle is None):
        raise ValueError('Provide exactly one source package or collected media bundle')
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
            marker_labels=False, note_folder=note_folder)
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
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    try:
        report = build_package(args.companion, args.map_template, args.media_template,
            args.out, name=args.name, note_folder=args.note_folder,
            units_per_grid=args.units_per_grid, origin=args.origin, package=args.package,
            media_bundle=args.media_bundle, pdf_pages=args.pdf_pages,
            template_name=args.template_name, regenerate_notes=args.regenerate_notes)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    c = report['counts']
    print(f"Built {report['native_map']['markers']} room markers, {c['notes']} notes and {c['native_image_attachments']} image/PDF attachments. See conversion-report.json.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

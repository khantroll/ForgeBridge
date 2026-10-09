"""Generate a new note Media field using a supplied native image asset pair.

This controlled import test preserves the supplied embedded image and thumbnail.
It does not yet turn arbitrary Foundry image/PDF files into native assets.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

from PIL import Image

from forgebridge.native import NoteBuilder, Writer
from forgebridge.native_map import AppendWriter, patch_stream
from forgebridge.nrbf import Reader


def renamed_asset(data, name, expected_class):
    reader = Reader(data)
    graph = reader.read()
    if reader.objects[graph['root_id']].get('class') != expected_class:
        raise ValueError('Unexpected native image asset type')
    writer, patches = AppendWriter(reader), []
    for oid, obj in reader.objects.items():
        if not isinstance(obj, dict) or 'members' not in obj:
            continue
        for key in obj['members']:
            bare = key.split('+')[-1]
            value = name if bare in {'_name', '_tileName'} else 'ForgeBridge' if bare in {'_creator', '_tileCreator'} else None
            if value is not None:
                a, b = reader.member_spans[oid][key]
                patches.append((a, b, writer.encoded(value)))
    result = patch_stream(reader, patches, writer)
    check = Reader(result)
    check.read()
    # Renaming never changes embedded content, thumbnails or preset values.
    for oid, obj in reader.objects.items():
        if isinstance(obj, dict) and 'bytes' in obj and check.objects.get(oid) != obj:
            raise ValueError('Embedded image changed unexpectedly')
    return result


def media_smoke_files(template):
    with zipfile.ZipFile(template) as archive:
        if len(archive.infolist()) > 256:
            raise ValueError('Use a small note/image sample export')
        if sum(i.file_size for i in archive.infolist()) > 128 * 1024 * 1024:
            raise ValueError('Native sample exceeds size limit')
        files = {}
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            path = PurePosixPath(entry.filename)
            if (not entry.filename.startswith('MyAssets/') or '\\' in entry.filename or
                    '..' in path.parts or entry.file_size > 64 * 1024 * 1024 or
                    entry.filename in files):
                raise ValueError('Invalid or oversized native sample entry')
            files[entry.filename] = archive.read(entry)
    notes = [n for n in files if n.endswith('.rwnote')]
    assets = [n for n in files if n.endswith('.rwfile') and n.startswith('MyAssets/Media/')]
    if len(notes) != 1 or len(assets) != 1:
        raise ValueError('Sample needs one note and one native image asset')
    asset = assets[0]
    meta = asset[:-7] + '.rwmeta'
    if meta not in files or notes[0][:-7] + '.rwmeta' not in files:
        raise ValueError('Sample needs matching note and image metadata')
    reader = Reader(files[notes[0]])
    reader.read()
    fields = [o for o in reader.objects.values() if isinstance(o, dict) and o.get('class') == 'ArkenNoteFieldMedia']
    if len(fields) != 1:
        raise ValueError('Sample needs exactly one Media field')
    link = fields[0]['members']['_contentPathRelative']
    if not isinstance(link, dict) or reader.objects.get(link.get('ref')) != meta:
        raise ValueError('Sample Media field does not target the supplied image metadata')
    image_reader = Reader(files[asset])
    image_reader.read()
    images = [o['bytes'] for o in image_reader.objects.values() if isinstance(o, dict) and 'bytes' in o]
    if len(images) != 1:
        raise ValueError('Expected one embedded image in the sample asset')
    with Image.open(io.BytesIO(images[0])) as image:
        if image.format != 'PNG' or image.width * image.height > 16000000:
            raise ValueError('Expected a bounded PNG image sample')
        dimensions = [image.width, image.height]
        image.verify()
    digest = hashlib.sha256(files[asset] + files[meta]).hexdigest()[:12]
    folder = 'ForgeBridgeMediaTest-' + digest
    name = 'ForgeBridge Generated Image Test'
    note_path = 'MyAssets/Encyclopedia/Notes/' + folder + '/Image-Test'
    media_path = 'MyAssets/Media/' + folder + '/Image-Test'
    builder = NoteBuilder()
    note_fields = [builder.text_field('Test instructions', [('The image below should match your original image-handout test. Close and reopen this note, then save/restart and verify it remains visible. Player visibility is unverified.', None)], 1),
                   builder.media_field('Generated image attachment', media_path + '.rwmeta', 2)]
    output = {
        note_path + '.rwnote': Writer(builder.schema['libraries']).write(builder.note(name, note_fields)),
        note_path + '.rwmeta': Writer(builder.schema['libraries']).write(builder.metadata(name)),
        media_path + '.rwfile': renamed_asset(files[asset], 'ForgeBridge Test Image', 'ArkenTileUpgrade'),
        media_path + '.rwmeta': renamed_asset(files[meta], 'ForgeBridge Test Image', 'ArkenTileMeta'),
    }
    report = {'schema_version': '1.0', 'note_name': name, 'note_path': note_path + '.rwmeta',
              'media_path': media_path + '.rwmeta', 'image_dimensions': dimensions,
              'embedded_image_sha256': hashlib.sha256(images[0]).hexdigest(),
              'image_and_thumbnail_preserved': True, 'native_media_field_generated': True,
              'arbitrary_source_image_conversion': False, 'pdf_conversion': False,
              'runtime_status': 'Requires Toolkit display and save/reopen testing'}
    output['media-test-report.json'] = json.dumps(report, indent=2).encode()
    output['INSTALL.txt'] = ("ForgeBridge generated native image-field test\n\n"
        "Close Arkenforge and back up MyAssets. Merge this ZIP's MyAssets folder\n"
        "into your EXISTING ArkenforgeData/MyAssets folder.\n"
        "Keep the folder paths exactly as supplied. Reports belong outside MyAssets.\n"
        f"Open the note: {name}\n"
        "Confirm the image matches the original sample, close/reopen the note,\n"
        "then restart the Toolkit and confirm it remains visible.\n"
        "This is a new note and image copy; original notes/maps are untouched.\n"
        "It tests a generated Media field and relocated native image asset.\n"
        "Source image bytes/thumbnail are preserved. PDF/source-media conversion\n"
        "and player visibility are not verified. No map or labels are included.\n"
        f"To remove, move only {folder} from both Notes and Media outside MyAssets.\n"
        "This contains private sample media; do not publish it.\n").encode()
    return output, report


def write_media_smoke_zip(template, dest):
    dest = Path(dest)
    if dest.exists() or dest.is_symlink():
        raise ValueError('Choose a new output filename')
    files, report = media_smoke_files(template)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in files.items():
            archive.writestr(path, data)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template-pack', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    try:
        report = write_media_smoke_zip(args.template_pack, args.out)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print('Wrote ' + report['note_name'] + '; see INSTALL.txt. Toolkit validation required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

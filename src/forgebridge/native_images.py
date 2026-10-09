"""Attach collected source images to retained native journal notes."""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
import zipfile
from urllib.parse import unquote, urlsplit

from PIL import Image, ImageOps

from forgebridge.handouts import media_references
from forgebridge.native_export import companion_files
from forgebridge.native_map import AppendWriter, patch_stream
from forgebridge.native_media import media_smoke_files
from forgebridge.nrbf import Reader

MAX_TOTAL = 256 * 1024 * 1024
MAX_FILE = 64 * 1024 * 1024
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}


def replace_image_payload(data, png, thumbnail_scale):
    reader = Reader(data, max_items=MAX_FILE)
    reader.read()
    blobs = [(oid, o) for oid, o in reader.objects.items() if isinstance(o, dict) and 'bytes' in o]
    if len(blobs) != 1:
        raise ValueError('Image template needs one encoded byte array')
    for obj in reader.objects.values():
        if isinstance(obj, dict) and obj.get('class') == 'ArkenImage':
            m = obj['members']
            if (m['_packImgX'], m['_packImgY'], m['_packImgChannels']) != (-1, -1, 4):
                raise ValueError('Unsupported native image encoding')
    oid, _ = blobs[0]
    a, b = reader.record_spans[oid]
    # ArraySinglePrimitive, same identity, Byte payload. All other graph IDs
    # and metadata stay intact; shared image/thumbnail references still work.
    replacement = bytes([15]) + struct.pack('<iiB', oid, len(png), 2) + png
    patches = [(a, b, replacement)]
    for object_id, fields in reader.member_spans.items():
        if '_thumbnailScale' in fields:
            a, b = fields['_thumbnailScale']
            patches.append((a, b, struct.pack('<f', thumbnail_scale)))
    return patch_stream(reader, patches, AppendWriter(reader), max_items=MAX_FILE)


def native_image_pair(template_file, template_meta, data):
    with Image.open(io.BytesIO(data)) as source:
        if source.format not in {'PNG', 'JPEG', 'WEBP', 'GIF'}:
            raise ValueError('Unsupported image encoding')
        if source.width * source.height > 16000000:
            raise ValueError('Image exceeds 16 megapixel limit')
        if getattr(source, 'n_frames', 1) != 1:
            raise ValueError('Animated images remain references')
        image = ImageOps.exif_transpose(source).convert('RGBA')
        full = io.BytesIO()
        image.save(full, 'PNG')
        thumb = image.copy()
        thumb.thumbnail((128, 128), Image.Resampling.LANCZOS)
        preview = io.BytesIO()
        thumb.save(preview, 'PNG')
        if len(full.getvalue()) > 60 * 1024 * 1024:
            raise ValueError('Normalized image exceeds native size limit')
        scale = thumb.width / image.width
        return (replace_image_payload(template_file, full.getvalue(), scale),
                replace_image_payload(template_meta, preview.getvalue(), scale),
                {'dimensions': list(image.size), 'thumbnail_dimensions': list(thumb.size),
                 'normalized_png_sha256': hashlib.sha256(full.getvalue()).hexdigest(),
                 'thumbnail_scale': scale,
                 'thumbnail_scale_status': 'Computed width ratio; Count\'s Crypt source-image display/reopen/restart passed; other packages require testing',
                 'native_preset_defaults': 'Copied from supplied image; map placement behavior is unverified'})


def source_image_files(companion, media_bundle, template_pack):
    occurrences = []
    refs = media_references(companion, occurrence_order=occurrences)
    template, tr = media_smoke_files(template_pack)
    native_base = tr['media_path'][:-7]
    template_file, template_meta = template[native_base + '.rwfile'], template[native_base + '.rwmeta']
    basename = PurePosixPath(native_base).name
    parent = PurePosixPath(native_base).parent.parent
    fields, output, rows, compiled, total = {}, {}, [], {}, 0
    with zipfile.ZipFile(media_bundle) as archive:
        entries = archive.infolist()
        if len(entries) > 4096 or sum(i.file_size for i in entries) > MAX_TOTAL:
            raise ValueError('Media bundle exceeds archive limits')
        names = [i.filename for i in entries]
        if len(names) != len(set(names)) or 'handout-report.json' not in names:
            raise ValueError('Media bundle needs one unambiguous handout-report.json')
        if archive.getinfo('handout-report.json').file_size > 4 * 1024 * 1024:
            raise ValueError('Handout report exceeds size limit')
        report = json.loads(archive.read('handout-report.json'))
        collected = report.get('references')
        if not isinstance(collected, list) or len(collected) != len(refs):
            raise ValueError('Handout report does not match retained companion references')
        expected_scene = companion.get('scene_id') or companion.get('scene_notes', {}).get('scene_id')
        if report.get('scene_id') != expected_scene:
            raise ValueError('Handout report belongs to a different scene')
        seen = set()
        for row in collected:
            ref = row.get('ref')
            if ref not in refs or ref in seen or row.get('origins') != refs[ref]:
                raise ValueError('Handout origins do not match retained companion')
            seen.add(ref)
            item = {'ref': ref, 'collection_status': row.get('status')}
            if row.get('status') != 'copied':
                rows.append({**item, 'status': 'collection_gap'})
                continue
            if Path(ref.split('?', 1)[0]).suffix.lower() not in IMAGE_SUFFIXES:
                rows.append({**item, 'status': 'non_image_reference_only'})
                continue
            path = row.get('bundled_path')
            if (not isinstance(path, str) or not path.startswith('assets/') or '\\' in path or
                    '..' in PurePosixPath(path).parts or path not in names):
                raise ValueError('Invalid bundled image path')
            if archive.getinfo(path).file_size > MAX_FILE:
                raise ValueError('Bundled image exceeds size limit')
            data = archive.read(path)
            digest = hashlib.sha256(data).hexdigest()
            if len(data) != row.get('size') or digest != row.get('sha256'):
                raise ValueError('Bundled image does not match collection hash/size')
            try:
                if digest not in compiled:
                    rwfile, rwmeta, details = native_image_pair(template_file, template_meta, data)
                    media_path = str(parent / ('ForgeBridgeImage-' + digest[:20]) / basename)
                    total += len(rwfile) + len(rwmeta)
                    if total > MAX_TOTAL:
                        raise ValueError('Native images exceed total package limit')
                    output[media_path + '.rwfile'], output[media_path + '.rwmeta'] = rwfile, rwmeta
                    compiled[digest] = (media_path + '.rwmeta', details)
                target, details = compiled[digest]
            except (OSError, ValueError, Image.DecompressionBombError) as exc:
                if total > MAX_TOTAL:
                    raise
                rows.append({**item, 'status': 'image_reference_only', 'reason': str(exc)})
                continue
            rows.append({**item, 'status': 'native_image', 'target': target,
                         'source_sha256': digest, **details})
    targets = {row['ref']: row['target'] for row in rows if row['status'] == 'native_image'}
    # Scan order is scoped to each note: a reused image can precede another
    # image on one page and follow it on another. Archive order is irrelevant.
    for ref, origin in occurrences:
        if ref not in targets:
            continue
        match = re.match(r'^pages\[(\d+)\]\.', origin['path'])
        key = (origin['document_index'], int(match.group(1)) if match else None)
        stem = PurePosixPath(unquote(urlsplit(ref).path)).stem
        label = re.sub(r'\s+', ' ', stem.replace('_', ' ').replace('-', ' ')).strip()[:160] or 'Image'
        attachment = {'ref': ref, 'target': targets[ref], 'label': 'Image — ' + label}
        bucket = fields.setdefault(key, [])
        if not any(a['ref'] == ref for a in bucket):
            bucket.append(attachment)
    return output, fields, rows


def write_source_images_zip(companion_path, media_bundle, template_pack, dest):
    companion_path, dest = Path(companion_path), Path(dest)
    if companion_path.stat().st_size > MAX_FILE:
        raise ValueError('Companion exceeds size limit')
    if dest.exists() or dest.is_symlink():
        raise ValueError('Choose a new output filename')
    companion = json.loads(companion_path.read_text(encoding='utf-8'))
    media, fields, rows = source_image_files(companion, media_bundle, template_pack)
    notes, report = companion_files(companion, media_fields=fields)
    if set(media) & set(notes):
        raise ValueError('Media conflicts with note output')
    files = {**notes, **media}
    report['source_media'] = rows
    report['counts']['native_image_assets'] = len(media) // 2
    report['status'] = 'Count\'s Crypt source-image display, proportions, note reopening and Toolkit restart passed user testing. Other packages require Toolkit testing.'
    files['conversion-report.json'] = json.dumps(report, indent=2, ensure_ascii=True).encode()
    files['INSTALL.txt'] = ("ForgeBridge native journal image attachments\n\n"
        "Close Arkenforge and back up MyAssets, including the existing generated notes.\n"
        "Merge this ZIP's MyAssets contents into the EXISTING ArkenforgeData/MyAssets.\n"
        "Replace matching generated note files to add image attachments. This regenerates\n"
        "those notes from the source companion; preserve any manual edits in your backup.\n"
        "Keep all paths intact; reports/source-companion.json stay outside MyAssets.\n"
        "Open the existing ForgeBridge scene index or an existing Crypt room marker.\n"
        "Follow a link to an image handout; confirm it displays at the correct aspect ratio.\n"
        "Check both a portrait and a landscape image, then close/reopen and restart.\n"
        "PNG/JPEG/static WebP/GIF are normalized to native RGBA PNG with thumbnails.\n"
        "PDFs, animations, unsupported/missing media remain references in the report.\n"
        "No map/labels are generated; existing room marker targets stay the same.\n"
        "Player visibility remains unverified. This package contains private content.\n").encode()
    if sum(map(len, files.values())) > MAX_TOTAL:
        raise ValueError('Native note/media package exceeds 256 MiB limit')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in files.items():
            archive.writestr(path, data)
    return report

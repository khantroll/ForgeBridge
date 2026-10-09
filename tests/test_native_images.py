import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from PIL import Image

from forgebridge.handouts import write_handouts_zip
from forgebridge.native_export import companion_files
from forgebridge.native_images import native_image_pair, write_source_images_zip
from forgebridge.nrbf import Reader
from test_native_export import source, recovered
from test_native_media import sample


def inputs(root, *, animated=False):
    root = Path(root)
    template = root / 'template.zip'
    sample(template)
    package = root / 'package'
    package.mkdir()
    (package / 'module.json').write_text('{"id":"sample"}')
    (package / 'private').mkdir()
    image = Image.new('RGBA', (360, 90), (30, 90, 160, 128))
    image.save(package / 'private/image.webp', 'WEBP', lossless=True)
    Image.new('RGB', (60, 240), (200, 20, 80)).save(package / 'private/portrait.jpg')
    (package / 'private/file.pdf').write_bytes(b'%PDF-test')
    x = source()
    x['scene_id'] = 'scene'
    pages = x['scene_notes']['dependencies']['documents'][0]['payload']['pages']
    pages[0]['text']['content'] += '<img src="private/image.webp"><img src="private/image.webp">'
    pages.extend([{'_id': 'portrait', 'name': 'Portrait', 'src': 'private/portrait.jpg', 'type': 'image'},
                  {'_id': 'pdf', 'name': 'PDF', 'src': 'private/file.pdf', 'type': 'pdf'}])
    if animated:
        images = [Image.new('RGB', (10, 10), c) for c in ('red', 'blue')]
        images[0].save(package / 'private/animated.gif', save_all=True, append_images=images[1:], duration=100)
        pages.append({'_id': 'gif', 'name': 'Animated', 'src': 'private/animated.gif'})
    companion = root / 'source.json'
    companion.write_text(json.dumps(x))
    bundle = root / 'handouts.zip'
    write_handouts_zip(package, companion, bundle)
    return template, companion, bundle, x


class NativeImageTests(unittest.TestCase):
    def test_scoped_attachments_shared_assets_and_existing_note_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            template, companion, bundle, x = inputs(tmp)
            original_files, original_report = companion_files(x)
            dest = Path(tmp) / 'native.zip'
            report = write_source_images_zip(companion, bundle, template, dest)
            self.assertEqual(report['native_folder'], original_report['native_folder'])
            self.assertEqual(report['placements'], original_report['placements'])
            self.assertEqual(report['counts']['native_image_assets'], 2)
            self.assertEqual(report['counts']['native_image_attachments'], 3)
            self.assertEqual(len({a['target'] for a in report['attached_media']}), 2)
            self.assertEqual({r['status'] for r in report['source_media']}, {'native_image', 'non_image_reference_only'})
            with zipfile.ZipFile(dest) as z:
                self.assertIsNone(z.testzip())
                files = {n: z.read(n) for n in z.namelist()}
            self.assertTrue(set(original_files) <= set(files))
            self.assertEqual(json.loads(files['source-companion.json']), x)
            self.assertFalse(any(n.endswith('.rwmap') for n in files))
            self.assertEqual(recovered(files)[1:], recovered(original_files)[1:])
            for a in report['attached_media']:
                self.assertIn(a['target'], files)
                r = Reader(files[a['note'][:-7] + '.rwnote']);r.read()
                targets = [r.objects[o['members']['_contentPathRelative']['ref']] for o in r.objects.values()
                           if isinstance(o, dict) and o.get('class') == 'ArkenNoteFieldMedia']
                self.assertIn(a['target'], targets)
            for row in report['source_media']:
                if row['status'] != 'native_image': continue
                r = Reader(files[row['target'][:-7] + '.rwfile']);r.read()
                data = next(o['bytes'] for o in r.objects.values() if isinstance(o, dict) and 'bytes' in o)
                with Image.open(io.BytesIO(data)) as image:
                    self.assertEqual(list(image.size), row['dimensions'])
                    self.assertEqual(image.mode, 'RGBA')
                    if row['ref'].endswith('.webp'):
                        self.assertEqual(image.getpixel((0, 0)), (30, 90, 160, 128))

    def test_animation_stays_reference_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            template, companion, bundle, _ = inputs(tmp, animated=True)
            dest = Path(tmp) / 'native.zip'
            report = write_source_images_zip(companion, bundle, template, dest)
            self.assertTrue(any(r['status'] == 'image_reference_only' and 'Animated' in r['reason'] for r in report['source_media']))
            before = dest.read_bytes()
            with self.assertRaises(ValueError):
                write_source_images_zip(companion, bundle, template, dest)
            self.assertEqual(dest.read_bytes(), before)

    def test_tampered_asset_hash_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            template, companion, bundle, _ = inputs(tmp)
            with zipfile.ZipFile(bundle) as z:
                files = {n: z.read(n) for n in z.namelist()}
            image_path = next(n for n in files if n.endswith('.webp'))
            files[image_path] = b'tampered'
            bad = Path(tmp) / 'bad.zip'
            with zipfile.ZipFile(bad, 'w') as z:
                for n, data in files.items(): z.writestr(n, data)
            with self.assertRaisesRegex(ValueError, 'hash/size'):
                write_source_images_zip(companion, bad, template, Path(tmp) / 'output.zip')
            self.assertFalse((Path(tmp) / 'output.zip').exists())

    def test_wrong_companion_origins_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            template, companion, bundle, x = inputs(tmp)
            x['scene_notes']['dependencies']['documents'][0]['payload']['name'] = 'Wrong document'
            companion.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError, 'origins'):
                write_source_images_zip(companion, bundle, template, Path(tmp) / 'output.zip')

    def test_thumbnail_and_image_payload_change_with_native_name_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'template.zip';sample(path)
            with zipfile.ZipFile(path) as z:
                template_file = z.read('MyAssets/Media/Sample/Image.rwfile')
                template_meta = z.read('MyAssets/Media/Sample/Image.rwmeta')
            data = io.BytesIO();Image.new('RGB', (200, 600), 'green').save(data, 'PNG')
            rwfile, rwmeta, report = native_image_pair(template_file, template_meta, data.getvalue())
            self.assertEqual(report['dimensions'], [200, 600])
            self.assertEqual(report['thumbnail_dimensions'], [43, 128])
            for binary in (rwfile, rwmeta):
                r = Reader(binary);g=r.read()
                m = r.objects[g['root_id']]['members']
                self.assertEqual(r.objects[m['_name']['ref']], 'Original image')


if __name__ == '__main__': unittest.main()

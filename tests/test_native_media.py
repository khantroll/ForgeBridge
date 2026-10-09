import io
from pathlib import Path
import tempfile
import unittest
import zipfile

from PIL import Image

from forgebridge.native import Array, Node, NoteBuilder, Writer
from forgebridge.native_media import media_smoke_files, write_media_smoke_zip
from forgebridge.nrbf import Reader


class FixtureWriter(Writer):
    def type_info(self, kind, info):
        if kind == 7:
            self.out.append(info)
        else:
            super().type_info(kind, info)

    def array(self, array, oid):
        if array.kind == 0 and array.info == 2:
            self.out.append(15)
            self.integer(oid)
            self.integer(len(array.items))
            self.out.append(2)
            self.out += bytes(array.items)
        else:
            super().array(array, oid)


def fixture_node(name, members, types, infos):
    return Node({'name': name, 'names': list(members), 'types': types,
                 'infos': infos, 'library_id': 2}, members)


def sample(path, *, target=None, valid_image=True, extra_field=False):
    builder = NoteBuilder()
    note = 'MyAssets/Encyclopedia/Notes/Sample/Test'
    asset = 'MyAssets/Media/Sample/Image'
    buffer = io.BytesIO()
    Image.new('RGBA', (4, 3), (30, 80, 150, 200)).save(buffer, 'PNG')
    data = buffer.getvalue() if valid_image else b'not an image'
    image = fixture_node('ArkenImage', {'_packImgX': -1, '_packImgY': -1,
        '_packImgChannels': 4, '_packImageRAW': Array(list(data), 0, 2)}, [0, 0, 0, 7], [8, 8, 8, 2])
    fields = [builder.media_field('Image', target or asset + '.rwmeta', 1)]
    if extra_field:
        fields.append(builder.media_field('Other image', asset + '.rwmeta', 2))
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(note + '.rwnote', Writer(builder.schema['libraries']).write(builder.note('Original note', fields)))
        z.writestr(note + '.rwmeta', Writer(builder.schema['libraries']).write(builder.metadata('Original note')))
        for ext, kind, field in [('.rwfile', 'ArkenTileUpgrade', '_content'), ('.rwmeta', 'ArkenTileMeta', '_thumbnail')]:
            obj = fixture_node(kind, {'_name': 'Original image', '_creator': 'Test author', field: image},
                [1, 1, 4], [None, None, {'name': 'ArkenImage', 'library_id': 2}])
            z.writestr(asset + ext, FixtureWriter(builder.schema['libraries']).write(obj))
    return data


class NativeMediaTests(unittest.TestCase):
    def test_new_note_target_and_image_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sample.zip'
            original = sample(path)
            source = path.read_bytes()
            files, report = media_smoke_files(path)
            self.assertEqual(path.read_bytes(), source)
            self.assertEqual(report['image_dimensions'], [4, 3])
            self.assertFalse(report['arbitrary_source_image_conversion'])
            r = Reader(files[report['note_path'][:-7] + '.rwnote'])
            r.read()
            fields = [o['members'] for o in r.objects.values() if isinstance(o, dict) and o.get('class') == 'ArkenNoteFieldMedia']
            self.assertEqual(len(fields), 1)
            f = fields[0]
            self.assertEqual(r.objects[f['_contentPathRelative']['ref']], report['media_path'])
            self.assertEqual(f['_UID'], f['ArkenNoteField+_UID'])
            self.assertEqual(f['_visibleToPlayers'], f['ArkenNoteField+_visibleToPlayers'])
            self.assertIn(report['media_path'], files)
            for ext in ('.rwfile', '.rwmeta'):
                asset = Reader(files[report['media_path'][:-7] + ext])
                graph = asset.read()
                self.assertEqual([o['bytes'] for o in asset.objects.values() if isinstance(o, dict) and 'bytes' in o], [original])
                m = asset.objects[graph['root_id']]['members']
                self.assertEqual(asset.objects[m['_name']['ref']], 'ForgeBridge Test Image')
                self.assertEqual(asset.objects[m['_creator']['ref']], 'ForgeBridge')

    def test_zip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, dest = Path(tmp) / 'source.zip', Path(tmp) / 'new.zip'
            sample(source)
            write_media_smoke_zip(source, dest)
            before = dest.read_bytes()
            with zipfile.ZipFile(dest) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(len([n for n in z.namelist() if n.endswith('.rwnote')]), 1)
            with self.assertRaises(ValueError):
                write_media_smoke_zip(source, dest)
            self.assertEqual(dest.read_bytes(), before)

    def test_bad_target_and_multiple_fields_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source.zip'
            sample(source, target='MyAssets/Media/Elsewhere/Other.rwmeta')
            with self.assertRaisesRegex(ValueError, 'does not target'):
                media_smoke_files(source)
            sample(source, extra_field=True)
            with self.assertRaisesRegex(ValueError, 'exactly one Media'):
                media_smoke_files(source)

    def test_unsafe_zip_and_bad_image_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source.zip'
            sample(source, valid_image=False)
            with self.assertRaises(OSError):
                media_smoke_files(source)
            sample(source)
            with zipfile.ZipFile(source, 'a') as z:
                z.writestr('MyAssets/../escape.rwfile', b'bad')
            with self.assertRaisesRegex(ValueError, 'Invalid'):
                media_smoke_files(source)

    def test_media_target_constraints(self):
        builder = NoteBuilder()
        for path in ('https://example.com/x.rwmeta', 'MyAssets/Media/../x.rwmeta',
                     'MyAssets/Encyclopedia/Notes/x.rwmeta', 'MyAssets/Media/x.png'):
            with self.assertRaises(ValueError):
                builder.media_field('Image', path, 1)


if __name__ == '__main__':
    unittest.main()

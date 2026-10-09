import struct
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from forgebridge.native import Array, Node, Writer
from forgebridge.native_map import AppendWriter, insert_markers, rename_metadata, write_map_zip
from forgebridge.nrbf import Reader
from test_native_export import source


def node(name, fields):
    return Node({'name': name, 'names': list(fields), 'types': [v[0] for v in fields.values()],
                 'infos': [v[1] for v in fields.values()], 'library_id': 2},
                {k: v[2] for k, v in fields.items()})


class FixtureWriter(AppendWriter):
    def __init__(self, libraries):
        Writer.__init__(self, libraries)


def fixture(capacity=4, next_uid=0):
    position = node('SVector2', {'x': (0, 11, 1.28), 'y': (0, 11, -1.28)})
    marker = node('ArkenTilePresetContentLink', {
        '_tileName': (1, None, 'FB Cal A'), '_name': (1, None, 'FB Cal A'),
        '_contentBasePath': (1, None, 'MyAssets/Encyclopedia/Notes/Cal.rwmeta'),
        '_contentType': (1, None, 'note'), '_position': (2, None, position),
        'ArkenTilePresetBase+_position': (2, None, position),
        '_uID': (0, 9, 100), 'ArkenTilePresetBase+_uID': (0, 9, 100),
        '_sortingOrder': (0, 8, 1), '_groupID': (0, 8, 3),
        '_radii': (2, None, Array([3., 4.], 0, 11))})
    wall = node('ArkenTilePresetRepeatable', {'_tileName': (1, None, 'Wall'),
        '_uID': (0, 9, 99), '_sortingOrder': (0, 8, 0),
        '_position': (2, None, node('SVector2', {'x': (0, 11, 12.), 'y': (0, 11, -9.)}))})
    wrap = lambda p: node('ArkenMapTileUpgradeBase', {'_tileInfo': (2, None, p)})
    tiles = node('TileList', {'_items': (2, None, Array([wrap(wall), wrap(marker)] + [None] * (capacity - 2), 2)),
                             '_size': (0, 8, 2), '_version': (0, 8, 2)})
    root = node('ArkenMapUpgrade', {'_name': (1, None, 'Original'), '_tiles': (2, None, tiles),
                                   '_nextUID': (0, 8, next_uid)})
    return FixtureWriter({2: 'Assembly-CSharp'}).write(root)


def placements(n=1):
    return [{'title': f'Room {i}', 'target': f'MyAssets/Encyclopedia/Notes/Room{i}.rwmeta',
             'grid_position': {'x': 2.5 + i, 'y': 3.5}} for i in range(n)]


class NativeMapTests(unittest.TestCase):
    def test_preserves_wall_and_shared_marker_position_and_assigns_unique_uid(self):
        original = fixture()
        before = Reader(original).read()['objects']
        data, report = insert_markers(original, placements(), name='Copy', units_per_grid=2.56,
                                     origin=(10., 20.), remove_names=['FB Cal A'])
        after = Reader(data).read()['objects']
        wall_id = next(i for i, obj in before.items() if isinstance(obj, dict) and obj.get('class') == 'ArkenTilePresetRepeatable')
        self.assertEqual(before[wall_id], after[wall_id])
        self.assertEqual(report[0]['native_position'], {'x': 16.4, 'y': 11.04})
        self.assertEqual(report[0]['native_uid'], 101)
        marker = next(obj['members'] for i, obj in after.items() if i not in before and isinstance(obj, dict) and obj.get('class') == 'ArkenTilePresetContentLink')
        self.assertEqual(marker['_position'], marker['ArkenTilePresetBase+_position'])
        self.assertEqual(marker['_uID'], marker['ArkenTilePresetBase+_uID'])
        self.assertEqual(marker['_groupID'], -1)
        self.assertEqual(after[marker['_contentBasePath']['ref']], placements()[0]['target'])
        self.assertEqual(original, fixture())

    def test_grows_full_array_and_keeps_existing_counter(self):
        data, report = insert_markers(fixture(capacity=2, next_uid=1000), placements(3),
                                     name='Copy', units_per_grid=1.)
        objects = Reader(data).read()['objects']
        root = objects[1]['members']
        tiles = objects[root['_tiles']['ref']]['members']
        self.assertEqual(tiles['_size'], 5)
        self.assertEqual(objects[tiles['_items']['ref']]['lengths'], [5])
        self.assertEqual([p['native_uid'] for p in report], [1000, 1001, 1002])
        self.assertEqual(root['_nextUID'], 1003)

    def test_rejects_invalid_transform_and_target(self):
        for scale in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                insert_markers(fixture(), placements(), name='Copy', units_per_grid=scale)
        for target in ('../../bad.rwmeta', 'MyAssets/Encyclopedia/Notes/../bad.rwmeta', 'MyAssets/Encyclopedia/Notes/a.rwnote'):
            p = placements(); p[0]['target'] = target
            with self.assertRaises(ValueError):
                insert_markers(fixture(), p, name='Copy', units_per_grid=1.)

    def test_rejects_missing_template_or_position(self):
        with self.assertRaises(ValueError):
            insert_markers(fixture(), placements(), name='Copy', units_per_grid=1., template_name='Missing')
        p = placements(); p[0]['grid_position'] = {'x': float('inf'), 'y': 0}
        with self.assertRaises(ValueError):
            insert_markers(fixture(), p, name='Copy', units_per_grid=1.)

    def test_renames_metadata_without_breaking_shared_name(self):
        root = node('ArkenMapMeta', {'_mapName': (1, None, 'Original'), '_name': (1, None, 'Original'),
                                    'ArkenBaseMeta+_name': (1, None, 'Original')})
        source = FixtureWriter({2: 'Assembly-CSharp'}).write(root)
        result = Reader(rename_metadata(source, 'Copy')).read()['objects']
        for ref in result[1]['members'].values():
            self.assertEqual(result[ref['ref']], 'Copy')

    def test_reader_spans_identify_primitive_and_original_record(self):
        data = fixture()
        reader = Reader(data); reader.read()
        a, b = reader.member_spans[1]['_nextUID']
        self.assertEqual(data[a:b], struct.pack('<i', 0))
        for oid, (a, b) in reader.record_spans.items():
            self.assertIn(data[a], (1, 4, 5, 6, 7, 15, 16, 17))
            self.assertGreater(b, a)

    def test_package_keeps_media_closes_note_targets_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            meta = node('ArkenMapMeta', {'_mapName': (1, None, 'Original')})
            original = fixture()
            with zipfile.ZipFile(folder / 'template.zip', 'w') as archive:
                archive.writestr('MyAssets/Maps/Original.rwmap', original)
                archive.writestr('MyAssets/Maps/Original.rwmeta', FixtureWriter({2: 'Assembly-CSharp'}).write(meta))
                archive.writestr('MyAssets/Media/background.rwfile', b'unchanged media')
            (folder / 'source.json').write_text(json.dumps(source()))
            report = write_map_zip(folder / 'template.zip', folder / 'source.json', folder / 'new.zip', name='Copy', units_per_grid=1.)
            with zipfile.ZipFile(folder / 'new.zip') as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(archive.read('MyAssets/Media/background.rwfile'), b'unchanged media')
                self.assertNotIn('MyAssets/Maps/Original.rwmap', archive.namelist())
                self.assertIn(report['placements'][0]['target'], archive.namelist())
                self.assertTrue(report['placements'][0]['native_map_placement'])
            with self.assertRaises(ValueError):
                write_map_zip(folder / 'template.zip', folder / 'source.json', folder / 'new.zip', name='Copy', units_per_grid=1.)
            with zipfile.ZipFile(folder / 'template.zip') as archive:
                self.assertEqual(archive.read('MyAssets/Maps/Original.rwmap'), original)

    def test_package_rejects_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / 'source.json').write_text(json.dumps(source()))
            with zipfile.ZipFile(folder / 'template.zip', 'w') as archive:
                archive.writestr('MyAssets/../bad', b'bad')
            with self.assertRaises(ValueError):
                write_map_zip(folder / 'template.zip', folder / 'source.json', folder / 'new.zip', name='Copy', units_per_grid=1.)


if __name__ == '__main__':
    unittest.main()

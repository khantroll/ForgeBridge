import struct
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from forgebridge.native import Array, Node, Writer, NoteBuilder
from forgebridge.native_export import companion_files
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


def fixture(capacity=4, next_uid=0, text=False):
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
    items = [wrap(wall), wrap(marker)]
    if text:
        text_position = node('SVector2', {'x': (0, 11, 5.), 'y': (0, 11, -5.)})
        label = node('ArkenTilePresetText', {'_text': (1, None, "Igor's Room"),
            '_name': (1, None, "TEXT: Igor's Room"), '_tileName': (1, None, 'TEXT:'),
            '_position': (2, None, text_position), 'ArkenTilePresetBase+_position': (2, None, text_position),
            '_uID': (0, 9, 200), '_sortingOrder': (0, 8, 2), '_groupID': (0, 8, -1),
            '_mapLevel': (0, 8, 0), '_hidden': (0, 1, False), 'ArkenTilePresetBase+_hidden': (0, 1, False),
            '_blocksLight': (0, 1, True), '_ignoreTimeOfDay': (0, 1, False), '_fontSize': (0, 11, 10.),
            '_blocking': (2, None, node('TileBlockingProperties', {k: (0, 1, True) for k in
                ('_blockingEnabled', '_light', '_vision', '_sound', '_movement')})),
            '_lighting': (2, None, node('TileLightingProperties', {'_hasLight': (0, 1, True)}))})
        items.append(wrap(label))
    tiles = node('TileList', {'_items': (2, None, Array(items + [None] * max(0, capacity - len(items)), 2)),
                             '_size': (0, 8, len(items)), '_version': (0, 8, len(items))})
    root = node('ArkenMapUpgrade', {'_name': (1, None, 'Original'), '_tiles': (2, None, tiles),
                                   '_nextUID': (0, 8, next_uid)})
    return FixtureWriter({2: 'Assembly-CSharp'}).write(root)


def placements(n=1):
    return [{'title': f'Room {i}', 'target': f'MyAssets/Encyclopedia/Notes/Room{i}.rwmeta',
             'grid_position': {'x': 2.5 + i, 'y': 3.5}} for i in range(n)]


class NativeMapTests(unittest.TestCase):
    def active_presets(self, data):
        objects = Reader(data).read()['objects']
        tiles = objects[objects[1]['members']['_tiles']['ref']]['members']
        return objects, [objects[objects[ref['ref']]['members']['_tileInfo']['ref']] for ref in
                         objects[tiles['_items']['ref']]['items'][:tiles['_size']]]

    def test_labels_opt_in_hidden_nonblocking_and_native_text(self):
        original = fixture(text=True)
        off, report = insert_markers(original, placements(), name='Off', units_per_grid=2.)
        _, presets = self.active_presets(off)
        self.assertEqual(sum(p['class'] == 'ArkenTilePresetText' for p in presets), 1)  # User's text remains.
        self.assertNotIn('label', report[0])
        on, report = insert_markers(original, placements(2), name='On', units_per_grid=2., marker_labels=True)
        objects, presets = self.active_presets(on)
        labels = [p['members'] for p in presets if p['class'] == 'ArkenTilePresetText']
        self.assertEqual(len(labels), 2)
        self.assertEqual([objects[p['_text']['ref']] for p in labels], ['Room 0', 'Room 1'])
        for label in labels:
            self.assertTrue(label['_hidden'])
            self.assertTrue(label['ArkenTilePresetBase+_hidden'])
            self.assertEqual(label['_position'], label['ArkenTilePresetBase+_position'])
            self.assertEqual(label['_fontSize'], 10.)
            self.assertFalse(any(objects[label['_blocking']['ref']]['members'].values()))
            self.assertFalse(objects[label['_lighting']['ref']]['members']['_hasLight'])
        self.assertEqual(report[0]['label']['native_position'], {'x': 7.5, 'y': -7.})
        self.assertEqual(len(set(p['members']['_uID'] for p in presets)), len(presets))

    def test_labels_require_native_template_only_when_enabled(self):
        with self.assertRaisesRegex(ValueError, 'native text'):
            insert_markers(fixture(), placements(), name='Copy', units_per_grid=1., marker_labels=True)
        insert_markers(fixture(), placements(), name='Copy', units_per_grid=1.)

    def test_existing_marker_position_and_uid_are_preserved(self):
        p = placements(); p[0]['target'] = 'MyAssets/Encyclopedia/Notes/Cal.rwmeta'
        original = fixture(text=True)
        updated, report = insert_markers(original, p, name='Copy', units_per_grid=99., marker_labels=True)
        self.assertTrue(report[0]['existing_marker_preserved'])
        self.assertEqual(report[0]['native_uid'], 100)
        self.assertAlmostEqual(report[0]['native_position']['x'], 1.28, places=5)
        before, _ = self.active_presets(original)
        after, presets = self.active_presets(updated)
        mid = next(i for i, obj in before.items() if isinstance(obj, dict) and obj.get('class') == 'ArkenTilePresetContentLink')
        self.assertEqual(after[mid], before[mid])
        self.assertEqual(sum(p['class'] == 'ArkenTilePresetContentLink' for p in presets), 1)

    def test_reexport_switch_removes_generated_labels_without_duplicate_markers(self):
        p = placements(); p[0]['target'] = 'MyAssets/Encyclopedia/Notes/Cal.rwmeta';p[0]['title'] = "Igor's Room"
        original, old_report = insert_markers(fixture(text=True), p, name='On', units_per_grid=1., marker_labels=True)
        off, off_report = insert_markers(original, old_report, name='Off', units_per_grid=1.)
        self.assertNotIn('label', off_report[0])
        _, presets = self.active_presets(off)
        self.assertFalse(any(p['class'] == 'ArkenTilePresetText' for p in presets))
        on, report = insert_markers(original, p, name='OnAgain', units_per_grid=1., marker_labels=True)
        _, presets = self.active_presets(on)
        self.assertEqual(sum(p['class'] == 'ArkenTilePresetText' for p in presets), 1)
        self.assertEqual(sum(p['class'] == 'ArkenTilePresetContentLink' for p in presets), 1)

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
                self.assertEqual(archive.read('MyAssets/Maps/Original.rwmap'), fixture())
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

    def test_package_preserves_existing_edited_note(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            content = source()
            generated, report = companion_files(content)
            target = report['placements'][0]['target']
            note_path = target[:-7] + '.rwnote'
            builder = NoteBuilder()
            edited = Writer(builder.schema['libraries']).write(builder.note('User edit', [builder.text_field('Contents', [('Keep this edit', None)], 1)]))
            meta = node('ArkenMapMeta', {'_mapName': (1, None, 'Original')})
            with zipfile.ZipFile(folder / 'template.zip', 'w') as archive:
                archive.writestr('MyAssets/Maps/Original.rwmap', fixture())
                archive.writestr('MyAssets/Maps/Original.rwmeta', FixtureWriter({2: 'Assembly-CSharp'}).write(meta))
                archive.writestr(note_path, edited)
            (folder / 'source.json').write_text(json.dumps(content))
            result = write_map_zip(folder / 'template.zip', folder / 'source.json', folder / 'new.zip', name='Copy', units_per_grid=1.)
            self.assertIn(note_path, result['preserved_exported_note_files'])
            with zipfile.ZipFile(folder / 'new.zip') as archive:
                self.assertEqual(archive.read(note_path), edited)


if __name__ == '__main__':
    unittest.main()

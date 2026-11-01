import unittest
from unittest.mock import patch
from pathlib import Path

from forgebridge.scene_records import record, encode, blank_map, template_map, canonical_graph
from forgebridge.native_scene import find_templates
from forgebridge.nrbf import Reader


class SceneRecordTests(unittest.TestCase):
    def test_schema_records_need_no_native_files_and_round_trip(self):
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('No native file reads')):
            for kind in ('wall', 'door', 'light', 'image', 'asset', 'asset_meta', 'blank', 'map_meta', 'content', 'size'):
                with self.subTest(kind=kind):
                    data = encode(record(kind))
                    self.assertEqual(canonical_graph(data), canonical_graph(encode(record(kind))))
            reader, templates = find_templates(template_map())
            self.assertEqual(set(templates), {'wall', 'door', 'light', 'image'})
            g = Reader(blank_map()).read()
            root = g['objects'][g['root_id']]['members']
            tiles = g['objects'][root['_tiles']['ref']]['members']
            self.assertEqual(tiles['_size'], 0)

    def test_defaults_are_fresh_and_inherited_members_preserve_aliases(self):
        first, second = record('wall'), record('wall')
        first.members['_tileInfo'].members['_position'].members['x'] = 999.
        self.assertEqual(second.members['_tileInfo'].members['_position'].members['x'], 0.)
        p = second.members['_tileInfo'].members
        self.assertIs(p['_position'], p['ArkenTilePresetBase+_position'])

    def test_blank_has_no_saved_fog_or_bookmarks(self):
        blank = record('blank')
        self.assertEqual(blank.members['_fogLevelDataFull'].members['HashSize'], 0)
        self.assertNotIn('KeyValuePairs', blank.members['_fogLevelDataFull'].members)
        self.assertEqual(blank.members['_bookmarks'].members['_size'], 0)
        self.assertEqual(blank.members['_creator'], 'ForgeBridge')

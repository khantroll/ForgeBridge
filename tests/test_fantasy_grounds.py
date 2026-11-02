import io
import json
import math
from pathlib import Path
import tempfile
import unittest
import unittest.mock
import zipfile

from PIL import Image

from forgebridge.fantasy_grounds import (ModuleError, ModuleSource, inventory, list_images, main, to_uvtt)
from forgebridge.validate import load_schema, repo_schema, validate

W, H, PPG = 400, 300, 100


def fg(gx, gy):
    """uvtt2fgu's own grid->FG pixel transform (centre origin, y up)."""
    return gx * PPG - W / 2, H / 2 - gy * PPG


def pts(*grid_points):
    return ','.join(f'{v:.1f}' for g in grid_points for v in fg(*g))


def png(w=W, h=H):
    out = io.BytesIO(); Image.new('RGB', (w, h), (40, 40, 40)).save(out, 'PNG'); return out.getvalue()


DEFINITION = b'<?xml version="1.0"?><root version="4.1"><name>FBTest</name><displayname>ForgeBridge test</displayname><author>synthetic</author><ruleset>Any</ruleset></root>'

LOS = f'''<gridsize>{PPG},{PPG}</gridsize>
<occluders>
  <occluder><id>0</id><points>{pts((0, 0), (4, 0), (4, 3))}</points></occluder>
  <occluder><id>1</id><points>{pts((1, 1), (2, 1), (2, 2))}</points><closed /></occluder>
  <occluder><id>2</id><points>{pts((1, 2.9), (2, 2.9), (2, 3.1), (1, 3.1))}</points><toggleable /><closed /><single_sided /><counterclockwise /></occluder>
  <occluder><id>3</id><points>{pts((3, 2.9), (4, 2.9), (4, 3.1), (3, 3.1))}</points><toggleable /><closed /><allow_vision /></occluder>
  <occluder><id>4</id><points>{pts((0, 2), (1, 2))}</points><terrain /><allow_move /></occluder>
</occluders>
<lights>
  <light><id>0</id><position>{pts((2, 1.5))}</position><color>#ffeccd8b</color><range>2,0.75,4,0.5</range><on /></light>
  <light><id>1</id><position>{pts((3, 0.5))}</position><color>#336699</color><range>1,0.75,3,0.5</range></light>
</lights>'''

DB = f'''<?xml version="1.0" encoding="utf-8"?>
<root version="4.1">
  <image>
    <id-00001>
      <name type="string">Layered Map</name>
      <image type="image">
        <layers><layer><name>map.png</name><id>0</id><bitmap>images/map.png</bitmap></layer></layers>
        {LOS}
        <shortcuts><shortcut><x>0</x><y>0</y><class>encounter</class><recordname>encounter.id-00001</recordname></shortcut></shortcuts>
      </image>
    </id-00001>
    <id-00002>
      <name type="string">Classic With Sidecar</name>
      <image type="image"><bitmap>images/side.png</bitmap></image>
    </id-00002>
    <id-00003>
      <name type="string">No Grid</name>
      <image type="image"><bitmap>images/nogrid.png</bitmap></image>
    </id-00003>
  </image>
  <encounter><id-00001><name type="string">Room 1</name><text type="formattedtext"><p>Read aloud.</p></text></id-00001></encounter>
</root>'''.encode()

SIDECAR = f'<root version="4.1" dataversion="20210302">{LOS}</root>'.encode()


def module(root, files=None):
    files = files or {'definition.xml': DEFINITION, 'db.xml': DB, 'images/map.png': png(),
                      'images/side.png': png(), 'images/side.xml': SIDECAR, 'images/nogrid.png': png()}
    path = Path(root) / 'test.mod'
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return path


class FantasyGroundsTests(unittest.TestCase):
    def test_inventory_lists_maps_definition_and_blocks_uncalibrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = inventory(module(tmp))
        self.assertEqual(report['module']['displayname'], 'ForgeBridge test')
        maps = {row['record']: row for row in report['maps']}
        self.assertEqual(set(maps), {'image.id-00001', 'image.id-00002', 'image.id-00003'})
        self.assertEqual(maps['image.id-00001']['name'], 'Layered Map')
        self.assertEqual(maps['image.id-00001']['metadata_source'], 'db.xml')
        self.assertEqual(maps['image.id-00002']['metadata_source'], 'images/side.xml')
        self.assertEqual(maps['image.id-00003']['status'], 'BLOCKED')
        self.assertIn('gridsize', maps['image.id-00003']['reason'])

    def test_geometry_inverts_uvtt2fgu_transform_and_fits_schema(self):
        with tempfile.TemporaryDirectory() as tmp, ModuleSource(module(tmp)) as source:
            entry = [e for e in list_images(source) if e['record'] == 'image.id-00001'][0]
            result = to_uvtt(source, entry)
        uvtt = result['uvtt']
        self.assertEqual(validate(uvtt, load_schema(repo_schema('uvtt-core.schema.json'))), [])
        self.assertEqual(uvtt['resolution'], {'map_origin': {'x': 0, 'y': 0}, 'map_size': {'x': 4, 'y': 3},
                                              'pixels_per_grid': 100})
        self.assertEqual(uvtt['line_of_sight'][0], [{'x': 0, 'y': 0}, {'x': 4, 'y': 0}, {'x': 4, 'y': 3}])
        self.assertEqual(uvtt['line_of_sight'][1][-1], uvtt['line_of_sight'][1][0])  # closed shape
        door, window = uvtt['portals']
        self.assertEqual(door['bounds'], [{'x': 1, 'y': 3}, {'x': 2, 'y': 3}])
        self.assertTrue(door['closed']); self.assertFalse(window['closed'])
        self.assertTrue(math.isclose(door['rotation'], 0.0, abs_tol=1e-9))
        self.assertEqual(result['counts'], {'walls': 2, 'doors': 1, 'windows': 1, 'terrain': 1,
                                            'lights': 2, 'lights_off': 1})
        bright, off = uvtt['lights']
        self.assertEqual((bright['position'], bright['range'], bright['color']), ({'x': 2, 'y': 1.5}, 4, 'ffeccd8b'))
        self.assertEqual(off['color'], 'ff336699')
        fields = {(l['field'], l['grade']) for l in result['losses']}
        self.assertTrue({('terrain', 'unsupported'), ('pins', 'manual'), ('tokens', 'manual'),
                         ('lights', 'approximate')} <= fields)

    def test_sidecar_and_folder_module_match_db_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod = module(tmp)
            folder = Path(tmp) / 'unpacked'
            with zipfile.ZipFile(mod) as archive: archive.extractall(folder)
            with ModuleSource(folder) as source:
                entries = {e['record']: e for e in list_images(source)}
                layered = to_uvtt(source, entries['image.id-00001'])['uvtt']
                sidecar = to_uvtt(source, entries['image.id-00002'])['uvtt']
        for key in ('line_of_sight', 'portals', 'lights', 'resolution'):
            self.assertEqual(layered[key], sidecar[key])

    def test_unsafe_inputs_are_refused_or_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ModuleError, 'definition.xml'):
                ModuleSource(module(tmp, {'db.xml': DB}))
            bomb = b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY a "aaaa">]><root>&a;</root>'
            path = module(tmp, {'definition.xml': DEFINITION, 'db.xml': bomb})
            with self.assertRaisesRegex(ModuleError, 'DTD'):
                inventory(path)
            path = module(tmp, {'definition.xml': DEFINITION, '../escape.xml': b'<root/>',
                                'C:/abs.xml': b'<root/>'})
            with ModuleSource(path) as source:
                self.assertFalse(source.exists('../escape.xml'))
                self.assertEqual(inventory(path)['module']['note'][:9], 'No db.xml')
            huge = module(tmp, {'definition.xml': DEFINITION, 'db.xml': DB, 'images/map.png': png(9000, 8000),
                                'images/side.png': png(), 'images/side.xml': SIDECAR, 'images/nogrid.png': png()})
            rows = {r['record']: r for r in inventory(huge)['maps']}
            self.assertEqual(rows['image.id-00001']['status'], 'BLOCKED')
            self.assertIn('64 MP', rows['image.id-00001']['reason'])

    def test_cli_writes_new_uvtt_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod, out = module(tmp), Path(tmp) / 'map.uvtt'
            with unittest.mock.patch('sys.stdout'):
                self.assertEqual(main([str(mod), '--map', 'image.id-00001', '--out', str(out)]), 0)
            self.assertEqual(json.loads(out.read_text())['resolution']['pixels_per_grid'], 100)
            with unittest.mock.patch('sys.stderr'):
                self.assertEqual(main([str(mod), '--map', 'image.id-00001', '--out', str(out)]), 1)


if __name__ == '__main__':
    unittest.main()

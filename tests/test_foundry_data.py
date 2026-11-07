"""Optional Foundry Data folder resolves art that lives outside the package."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from PIL import Image

from forgebridge.convert import convert
from forgebridge.uvtt import open_art
from forgebridge.validate import InventoryFatal

FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures' / 'synthetic-module'
PORTRAIT = 'modules/legends-of-barovia-pk/assets/actors/Igor_token.webp'
TILE = 'modules/other-pack/assets/tiles/floor.png'
MISSING = 'modules/missing/assets/gone.png'
LINKED = 'modules/linked/assets/escape.png'


def _webp():
    out = io.BytesIO()
    Image.new('RGB', (4, 4), (12, 34, 56)).save(out, 'WEBP')
    return out.getvalue()


def _png():
    return (FIXTURE / 'assets' / 'crypt.png').read_bytes()


def _snapshot(root: Path):
    rows = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            rows.append((path.relative_to(root).as_posix(), 'link', path.readlink()))
        elif path.is_file():
            rows.append((path.relative_to(root).as_posix(), 'file', hashlib.sha256(path.read_bytes()).hexdigest()))
    return rows


class FoundryDataArtTests(unittest.TestCase):
    def build(self, root):
        package = root / 'source'
        shutil.copytree(FIXTURE, package)
        scene_path = package / 'packs' / 'scenes.db'
        scene = json.loads(scene_path.read_text(encoding='utf-8'))
        scene['tokens'] = [{
            '_id': 'token-igor', 'name': 'Igor', 'x': 20, 'y': 40, 'width': 1, 'height': 1,
            'texture': {'src': PORTRAIT}, 'rotation': 0, 'hidden': False,
        }]
        scene['tiles'] = [
            {'_id': 'tile-floor', 'x': 0, 'y': 0, 'width': 50, 'height': 50, 'texture': {'src': TILE}},
            {'_id': 'tile-missing', 'x': 50, 'y': 0, 'width': 50, 'height': 50, 'texture': {'src': MISSING}},
            {'_id': 'tile-escape', 'x': 0, 'y': 50, 'width': 10, 'height': 10, 'texture': {'src': '../../outside.png'}},
            {'_id': 'tile-link', 'x': 20, 'y': 50, 'width': 10, 'height': 10, 'texture': {'src': LINKED}},
        ]
        scene_path.write_text(json.dumps(scene), encoding='utf-8')
        actor_path = package / 'packs' / 'actors.db'
        actor = json.loads(actor_path.read_text(encoding='utf-8'))
        actor['img'] = PORTRAIT
        actor_path.write_text(json.dumps(actor) + '\n', encoding='utf-8')
        manifest = json.loads((package / 'module.json').read_text(encoding='utf-8'))
        for pack in manifest['packs']:
            if pack.get('type') == 'Actor':
                pack['system'] = 'dnd5e'
        (package / 'module.json').write_text(json.dumps(manifest), encoding='utf-8')
        data = root / 'Data'
        (data / PORTRAIT).parent.mkdir(parents=True)
        (data / TILE).parent.mkdir(parents=True)
        (data / Path(LINKED)).parent.mkdir(parents=True)
        (data / PORTRAIT).write_bytes(_webp())
        (data / TILE).write_bytes(_png())
        outside = root / 'outside.png'
        outside.write_bytes(b'not-in-data')
        (data / LINKED).symlink_to(outside)
        return package, data

    def test_data_folder_embeds_found_art_and_keeps_missing_losses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package, data = self.build(root)
            before = _snapshot(data)
            report = convert(package, root / 'out', foundry_data=data)
            self.assertEqual(report['status'], 'PASS')
            self.assertEqual(report['foundry_data']['access'], 'read-only')
            self.assertEqual(report['foundry_data']['evidence'], 'file-level only, Toolkit check pending')
            native = report['scenes'][0]['native_report']
            self.assertEqual([row['texture'] for row in native['token_conversion']['tokens']], [PORTRAIT])
            self.assertEqual([row['source'] for row in native['static_tiles']['tiles']], [TILE])
            tile_losses = {row['source']: row['summary'] for row in native['static_tiles']['losses'] if row.get('source')}
            self.assertIn(MISSING, tile_losses)
            self.assertIn('Foundry Data folder', tile_losses[MISSING])
            self.assertIn('unsafe/remote', tile_losses['../../outside.png'])
            self.assertIn('symlink was not followed', tile_losses[LINKED])
            portrait_losses = [row for row in native['campaign_content']['losses']
                               if row.get('feature') == 'portrait' and row.get('source') == PORTRAIT]
            self.assertEqual(portrait_losses, [])
            self.assertEqual(_snapshot(data), before)
            self.assertEqual((root / 'outside.png').read_bytes(), b'not-in-data')

    def test_without_the_folder_the_same_art_stays_a_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package, data = self.build(root)
            before = _snapshot(data)
            report = convert(package, root / 'out')
            native = report['scenes'][0]['native_report']
            self.assertEqual(native['token_conversion']['tokens'], [])
            self.assertIn(PORTRAIT, native['token_conversion']['unsupported'][0]['reason'])
            self.assertEqual(native['static_tiles']['tiles'], [])
            self.assertTrue(any(row.get('source') == PORTRAIT and row['feature'] == 'portrait'
                                for row in native['campaign_content']['losses']))
            self.assertIsNone(report['foundry_data'])
            self.assertEqual(_snapshot(data), before)

    def test_traversal_is_refused_before_the_data_folder_is_opened(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'Data').mkdir()
            with self.assertRaises(InventoryFatal) as caught:
                open_art(root / 'missing-package', '../../outside.png', root / 'Data')
        self.assertIn('unsafe/remote', str(caught.exception))


if __name__ == '__main__':
    unittest.main()

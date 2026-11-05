"""Regression against a populated, Toolkit-created user music playlist."""
from pathlib import Path
import tempfile
import unittest

from forgebridge.native_audio import playlist_files
from forgebridge.native import Writer, Node, Array
from forgebridge.nrbf import Reader
from forgebridge.native_map import clone


FIXTURE = Path(__file__).parents[1] / 'fixtures/arkenforge-user-playlist/toolkit-made-music-playlist'
MUSIC = 'MyAssets/Audio/Songs/Quick Import/FB Native Music Control/'


def parsed(data):
    reader = Reader(data); graph = reader.read()
    # Marker clone intentionally excludes optimized byte-array records. Expand
    # those inert arrays in this test adapter, without changing production IO.
    for oid, value in list(reader.objects.items()):
        if isinstance(value, dict) and 'bytes' in value:
            raw = value['bytes']
            reader.objects[oid] = {'items': list(raw), 'lengths': [len(raw)], 'lower_bounds': None}
            reader.array_metadata[oid] = (0, 2)
    return reader, clone(reader, graph['root_id'])


def objects(reader, kind):
    return [clone(reader, oid) for oid, obj in reader.objects.items()
            if isinstance(obj, dict) and obj.get('class') == kind]


def semantic(value):
    if isinstance(value, Node):
        members = dict(value.members)
        if value.schema['name'].startswith('System.Collections.Generic.List`1'):
            members['_items'] = members['_items'].items[:members['_size']]
            members.pop('_version')  # mutation counter, not displayed content
        return {'class': value.schema['name'], 'members': {k: semantic(v) for k, v in members.items()}}
    if isinstance(value, Array): return [semantic(v) for v in value.items]
    if isinstance(value, list): return [semantic(v) for v in value]
    return value


class NativeMusicTests(unittest.TestCase):
    def test_native_import_embeds_original_codec_bytes_without_sidecars(self):
        sources = [('FBReference-tone', Path(__file__).parents[1] / 'fixtures/arkenforge-native-controls-2026-11-03/sources/FBReference-tone.wav', b'RIFF'),
                   ('FBMusicControl-MP3', FIXTURE / 'sources/FBMusicControl-MP3.mp3', b'ID3'),
                   ('FBMusicControl-OGG', FIXTURE / 'sources/FBMusicControl-OGG.ogg', b'OggS')]
        for name, path, header in sources:
            with self.subTest(name=name):
                original = path.read_bytes()
                reader, root = parsed((FIXTURE / (MUSIC + name + '.rwfile')).read_bytes())
                track = objects(reader, 'AudioTrack')[0]
                self.assertTrue(root.members['_isSong'])
                self.assertEqual(track.members['_trackName'], 'Master')
                self.assertTrue(track.members['_originalFile'].endswith(path.suffix))
                self.assertEqual(bytes(track.members['_clipRAW'].items), original)
                self.assertTrue(original.startswith(header))
                # Schema serialization preserves the payload after native import.
                rebuilt, _ = parsed(Writer(reader.libraries).write(root))
                self.assertEqual(bytes(objects(rebuilt, 'AudioTrack')[0].members['_clipRAW'].items), original)

    def test_generated_ogg_matches_native_song_metadata_and_stem_mixer(self):
        source = FIXTURE / 'sources/FBMusicControl-OGG.ogg'
        native_reader, native = parsed((FIXTURE / (MUSIC + 'FBMusicControl-OGG.rwfile')).read_bytes())
        native_playlist, _ = parsed((FIXTURE / 'MyAssets/Playlists/FB Native Music Control.rwpl').read_bytes())
        control_info = next(n for n in objects(native_playlist, 'MusicTrackInfo') if n.members['_name'] == 'FBMusicControl-OGG')
        with tempfile.TemporaryDirectory() as tmp:
            files, report = playlist_files({'_id': 'p', 'name': 'Generated', 'sounds': [
                {'_id': 's', 'name': 'FBMusicControl-OGG', 'path': source.name}]}, source.parent, 'test', folder='Test')
        self.assertEqual(report['tracks'], 1)
        song_reader, generated = parsed(files[report['songs'][0]['native_file']])
        track = objects(song_reader, 'AudioTrack')[0]
        self.assertEqual(bytes(track.members['_clipRAW'].items), source.read_bytes())
        self.assertEqual(bytes(track.members['_clipRAW'].items), bytes(objects(native_reader, 'AudioTrack')[0].members['_clipRAW'].items))
        # Only the provenance filename differs; embedded bytes are unchanged.
        generated.members['_tracks'].members['_items'].items[0].members['_originalFile'] = objects(native_reader, 'AudioTrack')[0].members['_originalFile']
        self.assertAlmostEqual(generated.members['_duration'], native.members['_duration'], delta=.001)
        generated.members['_duration'] = native.members['_duration']
        self.assertEqual(semantic(generated), semantic(native))
        generated_meta = parsed(files[report['songs'][0]['native_metadata']])[1]
        native_meta = parsed((FIXTURE / (MUSIC + 'FBMusicControl-OGG.rwmeta')).read_bytes())[1]
        self.assertAlmostEqual(generated_meta.members['_duration'], native_meta.members['_duration'], delta=.001)
        generated_meta.members['_duration'] = native_meta.members['_duration']
        self.assertEqual(semantic(generated_meta), semantic(native_meta))
        playlist_reader, _ = parsed(files[report['playlist']])
        self.assertEqual(set(objects(playlist_reader, 'ContentItem')[0].members), {'_filePath', '_content'})
        info = objects(playlist_reader, 'MusicTrackInfo')[0]
        info.members['_songPath'] = control_info.members['_songPath']
        self.assertEqual(semantic(info), semantic(control_info))
        pair = info.members['_trackVolumes'].members['KeyValuePairs'].items[0]
        self.assertEqual(pair.members['key'], 'Master')
        self.assertAlmostEqual(pair.members['value'], .8)

    def test_production_mp3_remains_manual_until_playback_is_confirmed(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, report = playlist_files({'name': 'MP3', 'sounds': [
                {'path': 'FBMusicControl-MP3.mp3'}]}, FIXTURE / 'sources', 'test')
        self.assertEqual(report['tracks'], 0)
        self.assertEqual(report['manual_tracks'], 1)
        self.assertFalse(any(p.endswith('.rwfile') for p in files))

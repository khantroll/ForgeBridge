from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from PIL import Image
from forgebridge.native import Array
from forgebridge.native_dependencies import check_metadata_references, merge_native
from forgebridge.native_images import native_image_pair
from forgebridge.package import main, build_package
from forgebridge.scene_profile import (FORMAT, capture_profile, canonical_hash,
    fingerprint, load_profile, preflight_profile, profile_settings)
from test_native_images import inputs
from test_native_map import node, FixtureWriter
from test_tokens import control, scene


def archive(path, files):
    with zipfile.ZipFile(path, 'w') as z:
        for name, data in files.items():
            z.writestr(name, data)


def contents(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def setup_profiles(root):
    media, _, _, companion = inputs(root)
    package = root / 'package'
    Image.new('RGBA', (40, 40), 'red').save(package / 'token.png')
    native = contents(media)
    full, thumb, _ = native_image_pair(native['MyAssets/Media/Sample/Image.rwfile'],
        native['MyAssets/Media/Sample/Image.rwmeta'], (package / 'token.png').read_bytes())
    native.update({'MyAssets/Media/Sample/Image.rwfile': full, 'MyAssets/Media/Sample/Image.rwmeta': thumb})
    map_data, note, meta = control()
    native.update({'MyAssets/Maps/Control.rwmap': map_data,
        'MyAssets/Maps/Control.rwmeta': FixtureWriter({2: 'Assembly-CSharp'}).write(
            node('ArkenMapMeta', {'_name': (1, None, 'ControlMap')})),
        'MyAssets/Encyclopedia/Notes/Control.rwnote': note,
        'MyAssets/Encyclopedia/Notes/Control.rwmeta': meta})
    archive(root / 'controls.zip', native)
    scenes = []
    for i, sid in enumerate(('A', 'B', 'Zero')):
        s = scene(); s['_id'] = sid
        s['tokens'][0].update(rotation=90, hidden=True)  # same ID, name and texture in both scenes
        if i == 1:
            s.update(padding=0., grid={'type': 1, 'size': 50})
        if i == 2:
            s['tokens'] = []
        else:
            bad = deepcopy(s['tokens'][0]); bad.update(_id='bad', width=2)
            missing = deepcopy(s['tokens'][0]); missing['_id']='missing'; missing['texture']['src']='absent.png'
            s['tokens'].extend([bad, missing])
        scenes.append(s)
    (package / 'scenes.db').write_text('\n'.join(json.dumps(s) for s in scenes))
    (package / 'module.json').write_text(json.dumps({'id': 'sample', 'packs': [
        {'name': 'scenes', 'path': 'scenes.db', 'type': 'Scene', 'label': 'Synthetic scenes'}]}))
    result = []
    for i, s in enumerate(scenes):
        sid = s['_id']
        c = deepcopy(companion); c.update(scene_id=sid, source_scene=s)
        c['scene_notes']['scene_id'] = sid
        (root / (sid+'.json')).write_text(json.dumps(c))
        # Distinct scene geometry, no controls embedded: only that scene's wall.
        wall = node('ArkenTilePresetRepeatable', {'_tileName': (1,None,'Wall-'+sid),
            '_uID': (0,9,10), '_position': (2,None,node('SVector2',
                {'x': (0,11,float(i)), 'y': (0,11,-float(i))}))})
        wrap = node('ArkenMapTileUpgradeBase', {'_tileInfo': (2,None,wall)})
        tiles = node('TileList', {'_items': (2,None,Array([wrap],2)), '_size': (0,8,1), '_version': (0,8,1)})
        geometry = FixtureWriter({2:'Assembly-CSharp'}).write(node('ArkenMapUpgrade',
            {'_name': (1,None,sid), '_tiles': (2,None,tiles), '_nextUID': (0,8,11)}))
        archive(root / (sid+'.zip'), {'MyAssets/Maps/'+sid+'.rwmap': geometry,
            'MyAssets/Maps/'+sid+'.rwmeta': FixtureWriter({2:'Assembly-CSharp'}).write(
                node('ArkenMapMeta', {'_name': (1,None,sid)}))})
        ref = lambda p: {'path': p, 'sha256': ''}
        draft = {'format': FORMAT, 'version': 1,
            'source': {'package_id': 'sample', 'scene_id': sid, 'package': ref('package'),
                       'companion': ref(sid+'.json'), 'scene_sha256': ''},
            'geometry': {'export': ref(sid+'.zip'), 'map_path':'MyAssets/Maps/'+sid+'.rwmap',
                'calibration': {'package_id': 'sample',
                'scene_id': sid, 'scene_sha256': '', 'geometry_sha256': '', 'map_path':'MyAssets/Maps/'+sid+'.rwmap',
                'origin': [7.+i,11.+i], 'units_per_grid': 3.+i,
                'evidence': 'Synthetic coordinate control for '+sid+'; no runtime claim'}},
            'controls': {'marker': {'input': ref('controls.zip'), 'name': 'Control'},
                         'media': {'input': ref('template.zip')},
                         'token': {'input': ref('controls.zip'), 'name': 'Control', 'units_per_size_square': 2.56}},
            'output': {'map_name': 'Output '+sid, 'note_namespace': 'Same readable namespace'},
            'options': {'pdf_pages': False}}
        draft_path=root/(sid+'.draft.json'); draft_path.write_text(json.dumps(draft))
        profile = root/(sid+'.profile.json'); capture_profile(draft_path, profile)
        result.append(profile)
    return result


class SceneProfileTests(unittest.TestCase):
    def test_primary_map_is_explicit_when_geometry_has_backlink_maps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a,b,_=setup_profiles(root)
            files=contents(root/'A.zip');files.update(contents(root/'B.zip'))
            archive(root/'A.zip',files)
            p=json.loads(a.read_text());digest=fingerprint(root/'A.zip')
            p['geometry']['export']['sha256']=p['geometry']['calibration']['geometry_sha256']=digest
            a.write_text(json.dumps(p))
            audit,settings=preflight_profile(a)
            out=root/'multi-map.zip';build_package(**settings,dest=out)
            self.assertEqual(contents(out)['MyAssets/Maps/B.rwmap'],files['MyAssets/Maps/B.rwmap'])
            # Selecting a different map inside the same archive still invalidates the binding.
            p['geometry']['map_path']='MyAssets/Maps/B.rwmap';a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'Calibration binding mismatch'):preflight_profile(a)

    def test_zero_token_profile_can_omit_token_control_but_nonempty_scene_cannot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a,_,zero=setup_profiles(root)
            for profile in (a,zero):
                p=json.loads(profile.read_text());p['controls']['token']=None;profile.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'Scene has tokens'):preflight_profile(a)
            audit,settings=preflight_profile(zero)
            report=build_package(**settings,dest=root/'zero-output.zip')
            self.assertEqual(report['counts']['native_tokens'],0)
            self.assertEqual(audit['supported_tokens'],0)

    def test_ambiguous_adventure_identity_requires_matching_companion_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a,_,_=setup_profiles(root)
            p=json.loads(a.read_text());c=json.loads((root/'A.json').read_text())
            scene_a=c['source_scene'];package=root/'package'
            (package/'adv.db').write_text('\n'.join(json.dumps({'_id':parent,'scenes':[scene_a]})
                                                       for parent in ('first','second')))
            (package/'module.json').write_text(json.dumps({'id':'sample','packs':[
                {'name':'adv','path':'adv.db','type':'Adventure','label':'Adventure variants'}]}))
            c['scene_notes']['journals'][0]['source']={'source_path':'adv.db','parent_adventure_id':'first'}
            (root/'A.json').write_text(json.dumps(c))
            p['source']['package']['sha256']=fingerprint(package)
            p['source']['companion']['sha256']=fingerprint(root/'A.json');a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'ambiguous'):load_profile(a)
            p['source']['selector']=p['geometry']['calibration']['selector']={
                'source_path':'adv.db','parent_adventure_id':'first'}
            a.write_text(json.dumps(p));load_profile(a)
            p['source']['selector']=p['geometry']['calibration']['selector']={
                'source_path':'adv.db','parent_adventure_id':'second'}
            a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'journal scope mismatch'):load_profile(a)

    def test_two_scenes_coexist_with_isolated_notes_media_tokens_and_rebuilds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a,b,zero = setup_profiles(root)
            outputs, reports = [], []
            for profile in (a,b,zero):
                audit, settings = preflight_profile(profile)
                out=root/(profile.stem+'.zip')
                reports.append(build_package(**settings, dest=out, profile_provenance=audit['provenance']))
                outputs.append(out)
            af,bf,zf = map(contents, outputs)
            ar,br,zr = reports
            self.assertEqual([r['counts']['native_tokens'] for r in reports], [1,1,0])
            self.assertEqual([r['counts']['unsupported_tokens'] for r in reports], [2,2,0])
            for files in (af,bf,zf):
                self.assertGreater(check_metadata_references(files),0)
                self.assertEqual(json.loads(files['profile-provenance.json'])['runtime_validation'],
                                 'not established by profile or input hashes')
            self.assertNotEqual(ar['native_folder'],br['native_folder'])
            self.assertEqual(set(a['target'] for a in ar['attached_media']) &
                             set(a['target'] for a in br['attached_media']),set())
            at,bt=[r['token_conversion']['tokens'][0] for r in (ar,br)]
            self.assertEqual(at['placement']['title'],bt['placement']['title'])
            self.assertNotEqual(at['placement']['target'],bt['placement']['target'])
            self.assertEqual(at['placement']['native_position'], {'x':44.5,'y':-44.5})
            self.assertEqual(bt['placement']['native_position'], {'x':170.,'y':-214.})
            # Both scenes keep only their own source geometry plus identical reusable controls.
            self.assertNotIn('MyAssets/Maps/B.rwmap', af)
            self.assertNotIn('MyAssets/Maps/A.rwmap', bf)
            combined = {p:d for p,d in af.items() if p.startswith('MyAssets/')}
            merge_native(combined,{p:d for p,d in bf.items() if p.startswith('MyAssets/')})
            self.assertGreater(check_metadata_references(combined),0)
            a_native={p for p in af if p.startswith('MyAssets/')}
            b_native={p for p in bf if p.startswith('MyAssets/')}
            for p in a_native & b_native: self.assertEqual(af[p],bf[p])
            # Simulated installed/user-edited notes and B's ZIP are untouched by a rebuild.
            user=root/'user-note.rwnote';user.write_bytes(b'manual edits')
            b_before=outputs[1].read_bytes()
            audit, settings=preflight_profile(a)
            again=root/'again.zip';build_package(**settings,dest=again,profile_provenance=audit['provenance'])
            self.assertEqual({p:d for p,d in af.items() if p.startswith('MyAssets/')},
                             {p:d for p,d in contents(again).items() if p.startswith('MyAssets/')})
            self.assertEqual(outputs[1].read_bytes(),b_before)
            self.assertEqual(user.read_bytes(),b'manual edits')
            with self.assertRaisesRegex(ValueError,'new output'):
                build_package(**settings,dest=outputs[0])
            installed=dict(combined); installed[at['placement']['target']]=b'user edits'
            with self.assertRaisesRegex(ValueError,'conflicts'):
                merge_native(installed,{p:d for p,d in af.items() if p.startswith('MyAssets/')})
            self.assertEqual(installed[at['placement']['target']], b'user edits')

    def test_preflight_relative_paths_read_only_and_cli_override_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); a,_,_=setup_profiles(root)
            before={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
            audit,settings=preflight_profile(a, {'name':'Other map','pdf_pages':False})
            self.assertEqual(settings['package'],root/'package')
            self.assertEqual(audit['status'],'PASS')
            self.assertEqual({p:p.read_bytes() for p in root.rglob('*') if p.is_file()},before)
            stream=io.StringIO()
            with redirect_stdout(stream),redirect_stderr(stream):
                self.assertEqual(main(['--profile',str(a),'--preflight','--out',str(root/'unused.zip')]),0)
                self.assertEqual(main(['--profile',str(a),'--origin','0','0','--preflight']),1)
            self.assertFalse((root/'unused.zip').exists())
            self.assertIn('may override',stream.getvalue())
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(['--profile',str(a),'--name','CLI map','--note-folder','CLI notes',
                    '--no-pdf-pages','--out',str(root/'cli.zip')]),0)
            self.assertIn('MyAssets/Maps/CLI map.rwmap',contents(root/'cli.zip'))

    def test_changed_input_identity_geometry_and_calibration_fail_actionably(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); a,b,_=setup_profiles(root)
            original=json.loads(a.read_text())
            for role,path in [('package',root/'package/token.png'),('companion',root/'A.json'),
                              ('geometry',root/'A.zip'),('control',root/'controls.zip')]:
                raw=path.read_bytes();path.write_bytes(raw+b'changed')
                with self.assertRaisesRegex(ValueError,'hash mismatch.*Restore'):
                    preflight_profile(a)
                path.write_bytes(raw)
            p=deepcopy(original);p['geometry']['calibration']['scene_id']='B';a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'Calibration binding mismatch'):preflight_profile(a)
            p=deepcopy(original);p['geometry']['export']=json.loads(b.read_text())['geometry']['export']
            a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'Calibration binding mismatch'):preflight_profile(a)
            p=deepcopy(original);p['source']['package_id']='wrong';a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'package identity mismatch'):preflight_profile(a)
            p=deepcopy(original);p['version']=2;a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'format/version'):preflight_profile(a)
            # Updating a companion hash alone cannot detach it from the actual package scene.
            a.write_text(json.dumps(original)); companion=root/'A.json'; c=json.loads(companion.read_text())
            c['source_scene']['padding']=.5;companion.write_text(json.dumps(c))
            p=deepcopy(original);p['source']['companion']['sha256']=fingerprint(companion);a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'Companion/source scene mismatch'):preflight_profile(a)

    def test_missing_native_dependency_and_nonfinite_calibration_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); a,_,_=setup_profiles(root)
            p=json.loads(a.read_text())
            files=contents(root/'controls.zip'); del files['MyAssets/Media/Sample/Image.rwmeta']
            archive(root/'controls.zip',files)
            digest=fingerprint(root/'controls.zip')
            for role in ('marker','token'):p['controls'][role]['input']['sha256']=digest
            a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'Missing native dependency'):preflight_profile(a)
            p['geometry']['calibration']['origin']=[float('nan'),0];a.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'finite'):preflight_profile(a)

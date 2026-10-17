"""Snapshot existing real exports and explicitly pin measured scene profiles.

Read-only against original source and Toolkit data. Never installs or edits maps.
"""
import json
import sys
from pathlib import Path
import zipfile
from forgebridge.nrbf import Reader
from forgebridge.scene_profile import FORMAT, capture_profile

ROOT = Path(__file__).parent
OUT = ROOT / 'profile-runtime-private'
resume = '--resume' in sys.argv
OUT.mkdir(exist_ok=resume)  # explicit recovery of a partial profile capture
DATA = Path('C:/Program Files (x86)/ArkenforgeData')

def snapshot(name, destination):
    if resume and destination.exists():
        with zipfile.ZipFile(destination) as z: return len(z.namelist())
    pending=[name, name[:-6]+'.rwmeta']; files={}
    while pending:
        path=pending.pop()
        if path in files: continue
        if not path.startswith('MyAssets/') or '..' in path.split('/') or '\\' in path:
            raise ValueError(path)
        data=(DATA/path).read_bytes(); files[path]=data
        r=Reader(data,max_items=64000000);r.read()
        for value in r.objects.values():
            if isinstance(value,str) and value.startswith('MyAssets/') and value.endswith('.rwmeta'):
                pending.append(value)
                for ext in ('.rwnote','.rwfile','.rwmap'):
                    sibling=value[:-7]+ext
                    if (DATA/sibling).is_file(): pending.append(sibling)
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for path,data in sorted(files.items()):z.writestr(path,data)
    return len(files)

count=snapshot('MyAssets/Maps/ForgeBridge Runtime 2026-10-15 Fresh Manor 2nd.rwmap',OUT/'manor-native.zip')
print('Manor/control dependency files:',count)
count=snapshot('MyAssets/Maps/Counts_with_markers.rwmap',OUT/'crypt-native.zip')
print('Crypt dependency files:',count)

for slug,scene_id,companion,geometry,evidence in [
    ('manor','d0XKyRuR4GqdOagf','../../2026-10-15/manor-second-floor.forgebridge.json','manor-native.zip',
     'VALIDATION.md fresh map calibration: 3000x4000, native center (38.4,-51.2), scale2.56; FB Cal A UI (.5,-.5). Origin0; grid100.'),
    ('crypt','fP7VKkP46gQPED6X','../../../counts_crypt_links.forgebridge.json','crypt-native.zip',
     'Existing Counts_with_markers Crypt export: 4000x4200 background, native center (51.2,-53.76), scale2.56. Source grid100; upper-left origin0. Existing room-marker correlation inspected separately; runtime check remains separate.')]:
    ref=lambda path:{'path':path,'sha256':''}
    p={'format':FORMAT,'version':1,
       'source':{'package_id':'lob-counts_manor-pk-v13','scene_id':scene_id,
                 'package':ref('../../../lob-counts_manor-pk-v13'),
                 'companion':ref(companion),'scene_sha256':''},
       'geometry':{'export':ref(geometry),
            'map_path':'MyAssets/Maps/'+('Counts_with_markers' if slug=='crypt' else 'ForgeBridge Runtime 2026-10-15 Fresh Manor 2nd')+'.rwmap',
            'calibration':{'package_id':'lob-counts_manor-pk-v13',
            'scene_id':scene_id,'scene_sha256':'','geometry_sha256':'','origin':[0.,0.],
            'units_per_grid':2.56,'evidence':evidence}},
       'controls':{'marker':{'input':ref('../../../MyAssets(1).zip'),'name':'FB Cal A'},
           'media':{'input':ref('../../../FB_Media_notes.zip')},
           'token':{'input':ref('manor-native.zip'),'name':'Stoker_token_1','units_per_size_square':2.56}},
       'output':{'map_name':'ForgeBridge Profile '+slug.title()+' 2026-10-16',
                 'note_namespace':'ForgeBridge Profile '+slug.title()+' 2026-10-16'},
       'options':{'pdf_pages':False}}
    selector={'source_path':'packs/adventure-5e','parent_adventure_id':'N63YevXMYeDZPCMh'}
    p['source']['selector']=selector
    p['geometry']['calibration']['selector']=selector
    p['geometry']['calibration']['map_path']=p['geometry']['map_path']
    draft=OUT/(slug+'.draft.json');draft.write_text(json.dumps(p,indent=2),newline='\n')
    # Export evidence is a manual binding; capture only hashes and checks exact source identity.
    capture_profile(draft,OUT/(slug+'.scene-profile.json'))
    print('Pinned',slug)

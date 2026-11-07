"""Review two completed profile ZIPs; installation is a separate explicit option.

Never called by a build/preflight. Only absent files may be installed, with Toolkit
closed; any existing conflicting content aborts. File checks are not runtime PASS.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from forgebridge.native_dependencies import check_metadata_references, merge_native

ROOT=Path(__file__).parent
PRIVATE=ROOT/'profile-runtime-private'
DATA=Path('C:/Program Files (x86)/ArkenforgeData')
parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');args=parser.parse_args()
packages=[]; combined={}; token_targets=[]; note_folders=[]; image_targets=[]
for slug in ('manor','crypt'):
    path=PRIVATE/(slug+'-profile.zip')
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        report=json.loads(z.read('conversion-report.json'))
        provenance=json.loads(z.read('profile-provenance.json'))
        native={n:z.read(n) for n in z.namelist() if n.startswith('MyAssets/')}
    refs=check_metadata_references(native)
    token=report['token_conversion']
    token_targets.append({t['placement']['target'] for t in token['tokens']})
    image_targets.append({a['target'] for a in report['attached_media']})
    note_folders.append(report['native_folder'])
    shared=set(combined)&set(native)
    merge_native(combined,native)
    packages.append({'scene':slug,'map':report['native_map']['name'],
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'native_files':len(native),
        'closed_metadata_references':refs,'counts':report['counts'],
        'source':{k:provenance['source'][k] for k in ('package_id','scene_id','selector','scene_sha256')},
        'primary_geometry_map':provenance['geometry']['map_path'],
        'calibration':provenance['geometry']['calibration'],
        'profile_file_sha256':provenance['profile_file_sha256'],
        'scope':provenance['scope'],'note_folder':report['native_folder'],
        'tokens':[{'name':t['placement']['title'],'source_id':t['source_id'],
            'position':t['placement']['native_position'],'target':t['placement']['target']}
            for t in token['tokens']], 'rejected_tokens':token['unsupported']})
assert not token_targets[0]&token_targets[1]
assert not image_targets[0]&image_targets[1]
assert note_folders[0]!=note_folders[1]
rows=[]
for name,data in combined.items():
    target=DATA/name
    status='new' if not target.exists() else 'identical' if target.read_bytes()==data else 'CONFLICT'
    rows.append({'path':name,'status':status})
result={'scope':'file-only pair audit; runtime observations are separate', 'packages':packages,
    'combined_metadata_references':check_metadata_references(combined),
    'distinct_token_note_and_media_scopes':True,'shared_native_files_identical':len(shared),
    'installation_review':{s:sum(r['status']==s for r in rows) for s in ('new','identical','CONFLICT')}}
if args.install:
    assert 'MastersToolkit.exe' not in subprocess.run(['tasklist','/FI','IMAGENAME eq MastersToolkit.exe'],
        capture_output=True,text=True,check=True).stdout
    assert not result['installation_review']['CONFLICT'],[r for r in rows if r['status']=='CONFLICT']
    created=[]
    for name,data in combined.items():
        target=DATA/name
        if target.exists():
            assert target.read_bytes()==data
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as stream:stream.write(data)
        created.append(name)
    (PRIVATE/'installed-profile-files.json').write_text(json.dumps(created,indent=2),newline='\n')
    result['new_files_installed']=len(created)
(ROOT/'profile-pair-audit.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
print(json.dumps(result,indent=2))

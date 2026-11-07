"""Audit a private combined package; optionally install absent files only.

File checks never imply runtime PASS. --install requires Toolkit to be closed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from forgebridge.native_dependencies import check_metadata_references, read_export
from forgebridge.nrbf import Reader

parser=argparse.ArgumentParser()
parser.add_argument('package',type=Path)
parser.add_argument('--install',action='store_true')
args=parser.parse_args()
root=Path('C:/Program Files (x86)/ArkenforgeData')
with zipfile.ZipFile(args.package) as z:
    assert z.testzip() is None
    report=json.loads(z.read('conversion-report.json'))
    tokens=json.loads(z.read('token-report.json'))
    files={n:z.read(n) for n in z.namelist() if n.startswith('MyAssets/')}
    assert len(z.namelist())==len(set(z.namelist()))
parsed=0
for raw in files.values():
    r=Reader(raw,max_items=64000000);r.read();parsed+=1
references=check_metadata_references(files)
target_map=next(n for n in files if n.endswith('/'+report['native_map']['name']+'.rwmap'))
r=Reader(files[target_map]);g=r.read()
value=lambda v:r.objects[v['ref']] if isinstance(v,dict) and 'ref' in v else v
tiles=value(r.objects[g['root_id']]['members']['_tiles'])['members']
presets=[value(value(t)['members']['_tileInfo'])['members'] for t in
         value(tiles['_items'])['items'][:tiles['_size']]]
uids=[]
for token in tokens['tokens']:
    target=token['placement']['target']
    matches=[p for p in presets if value(p.get('_contentBasePath'))==target]
    assert len(matches)==1,(target,len(matches))
    uids.append(matches[0]['_uID'])
assert len(uids)==len(set(uids))
rows=[]
for n,b in files.items():
    dst=root/n
    status='new' if not dst.exists() else 'identical' if dst.read_bytes()==b else 'CONFLICT'
    rows.append({'path':n,'status':status})
result={'scope':'file checks only; see VALIDATION.md for observed behavior',
    'package':args.package.name,'sha256':hashlib.sha256(args.package.read_bytes()).hexdigest(),
    'native_files_parsed':parsed,'closed_metadata_references':references,
    'counts':report['counts'],'tokens':tokens['tokens'],'unsupported':tokens['unsupported'],
    'native_namespace':tokens['native_namespace'],
    'unique_generated_token_instances':len(uids),
    'preflight':{s:sum(row['status']==s for row in rows) for s in ('new','identical','CONFLICT')}}
if args.install:
    assert 'MastersToolkit.exe' not in subprocess.run(['tasklist','/FI','IMAGENAME eq MastersToolkit.exe'],
        capture_output=True,text=True,check=True).stdout
    assert result['preflight']['CONFLICT']==0,[row for row in rows if row['status']=='CONFLICT']
    created=[]
    for n,b in files.items():
        dst=root/n
        if dst.exists():
            assert dst.read_bytes()==b
            continue
        dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('xb') as f:f.write(b)
        created.append(n)
    result['new_files_installed']=len(created)
    (args.package.parent/'installed.json').write_text(json.dumps(created,indent=2),newline='\n')
Path(__file__).with_name('multi-runtime-audit.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('tokens',)},indent=2))

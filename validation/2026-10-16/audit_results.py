from pathlib import Path
import hashlib,json,zipfile
from forgebridge.nrbf import Reader
root=Path('validation/2026-10-16'); report={'kind':'file-level only; no runtime claims','packages':{},'controls':{}}
for name in ['manor-token-closed.zip','manor-fresh-combined.zip']:
 p=root/name
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  count=0;refs=[]
  for n in z.namelist():
   if n.endswith(('.rwmap','.rwmeta','.rwnote','.rwfile')):
    r=Reader(z.read(n),max_items=64000000);r.read();count+=1
    for value in r.objects.values():
     if isinstance(value,str) and value.startswith('MyAssets/') and value.endswith('.rwmeta'):
      if value not in z.namelist():raise ValueError((n,value))
      refs.append(value)
  report['packages'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'native_files_parsed':count,'closed_metadata_reference_occurrences':len(refs)}
for stage in ['control-before','control-size2','control-moved','control-transform','control-reopened']:
 p=next((root/stage).glob('*.rwmap'));r=Reader(p.read_bytes());r.read()
 def v(x):return r.objects[x['ref']] if isinstance(x,dict) and 'ref' in x else x
 for o in r.objects.values():
  if isinstance(o,dict) and o.get('class')=='ArkenTilePresetContentLink' and v(o['members']['_tileName'])=='Stoker_token_1':
   m=o['members'];report['controls'][stage]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'position':v(m['_position'])['members'],'scale':v(m['_scale'])['members'],'uid':m['_uID']}
(root/'file-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

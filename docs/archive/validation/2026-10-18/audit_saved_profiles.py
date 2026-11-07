from pathlib import Path
import json,zipfile,hashlib
from forgebridge.nrbf import Reader
out=[]
for slug in ('manor','crypt'):
 p=Path('validation/2026-10-16/profile-runtime-private')/(slug+'-profile.zip')
 with zipfile.ZipFile(p) as z:
  report=json.loads(z.read('conversion-report.json'));name='MyAssets/Maps/'+report['native_map']['name']+'.rwmap';before=z.read(name)
 saved=(Path('C:/Program Files (x86)/ArkenforgeData')/name).read_bytes()
 targets={t['placement']['target']:t['placement']['title'] for t in report['token_conversion']['tokens']}
 def extract(data):
  r=Reader(data);r.read();val=lambda v:r.objects[v['ref']] if isinstance(v,dict) and 'ref' in v else v
  rows=[];notes=[]
  for obj in r.objects.values():
   if not isinstance(obj,dict) or 'members' not in obj:continue
   m=obj['members'];target=val(m.get('_contentBasePath'))
   if not isinstance(target,str):continue
   if target in targets:
    rows.append({'name':targets[target],'target':target,'hidden':val(m.get('_hidden')),'position':val(m['_position'])['members']})
   elif target.startswith(report['native_folder']+'/'):
    notes.append(target)
  return rows,notes
 baseline,bnotes=extract(before);runtime,rnotes=extract(saved)
 assert baseline==runtime,(slug,'token state mismatch')
 assert bnotes==rnotes,(slug,'room target mismatch')
 assert len(runtime)==len(targets)
 out.append({'scene':slug,'scope':'file-only support; does not establish observed runtime behavior','package_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'saved_map_sha256':hashlib.sha256(saved).hexdigest(),'token_identity_hidden_position_equal_to_generated':True,'room_targets_equal_to_generated':True,'room_target_count':len(rnotes),'generated_tokens':runtime})
Path('validation/2026-10-18/profile-runtime-file-audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
print([(x['scene'],len(x['generated_tokens']),x['room_target_count'],x['saved_map_sha256']) for x in out])

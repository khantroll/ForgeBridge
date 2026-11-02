"""Prepare isolated private inputs; build with the production package command.

Copies source assets and reads native saved files. Never installs or edits the
original module, native maps or user notes. The arrow is an original test asset.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from PIL import Image, ImageDraw
from forgebridge.nrbf import Reader

ROOT = Path(__file__).parent
OUT = ROOT / 'multi-runtime-private'
OUT.mkdir()  # refuse reuse/overwrite
package = OUT / 'lob-counts_manor-pk-v13'
shutil.copytree(Path('lob-counts_manor-pk-v13/assets'), package / 'assets')
shutil.copy2('lob-counts_manor-pk-v13/module.json', package / 'module.json')
image = Image.new('RGBA', (128,128))
draw = ImageDraw.Draw(image)
draw.polygon([(64,4),(105,53),(78,53),(78,119),(50,119),(50,53),(23,53)], fill='white')
draw.polygon([(64,4),(105,53),(23,53)], fill='red')
draw.rectangle((14,67,49,84), fill='blue')
draw.ellipse((87,96,112,121), fill='lime')
texture = package / 'assets/forgebridge-arrow.png'
image.save(texture)
source = json.loads(Path('validation/2026-10-15/manor-second-floor.forgebridge.json').read_text())
scene = source['source_scene']
original = deepcopy(scene['tokens'])
for i,(size,rotation,hidden) in enumerate(((1,0,False),(1,90,False),(2,180,True),(.5,270,False))):
    scene['tokens'].append({'_id':f'fb-arrow-{i}', 'name':f'FB Arrow {rotation}',
        'x':800+(2+3*i-size/2)*100, 'y':1000+(2-size/2)*100,
        'width':size, 'height':size, 'rotation':rotation, 'hidden':hidden,
        'texture':{'src':'modules/lob-counts_manor-pk-v13/assets/forgebridge-arrow.png',
                   'scaleX':1.,'scaleY':1.},
        'flags':{'forgebridgeFixture':'original synthetic arrow; no behavior'}})
bad=deepcopy(scene['tokens'][-1]); bad.update(_id='fb-rectangle',width=2,height=1)
missing=deepcopy(scene['tokens'][-1]); missing['_id']='fb-missing'
missing['texture']['src']='assets/intentionally-missing.png'
scene['tokens'].extend([bad,missing,deepcopy(scene['tokens'][-2])])
assert scene['tokens'][:len(original)] == original
(OUT/'companion.json').write_text(json.dumps(source,indent=2),newline='\n')

# A read-only snapshot of the genuinely UVTT-imported map and its full dependency closure.
data=Path('C:/Program Files (x86)/ArkenforgeData')
first='MyAssets/Maps/ForgeBridge Runtime 2026-10-15 Fresh Manor 2nd.rwmap'
pending=[first,first[:-6]+'.rwmeta']; files={}
while pending:
    name=pending.pop()
    if name in files: continue
    if not name.startswith('MyAssets/') or '..' in name.split('/') or '\\' in name:
        raise ValueError(name)
    raw=(data/name).read_bytes(); files[name]=raw
    reader=Reader(raw,max_items=64000000); reader.read()
    for value in reader.objects.values():
        if isinstance(value,str) and value.startswith('MyAssets/') and value.endswith('.rwmeta'):
            pending.append(value)
            for ext in ('.rwnote','.rwfile','.rwmap'):
                sibling=value[:-7]+ext
                if (data/sibling).is_file(): pending.append(sibling)
with zipfile.ZipFile(OUT/'fresh-native-export.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
    for name,raw in sorted(files.items()): z.writestr(name,raw)
print(json.dumps({'private_inputs':str(OUT),'native_files':len(files),
    'arrow_sha256':hashlib.sha256(texture.read_bytes()).hexdigest(),
    'source_tokens':len(scene['tokens'])},indent=2))

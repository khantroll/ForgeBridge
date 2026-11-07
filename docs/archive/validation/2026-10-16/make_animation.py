from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
root=Path('validation/2026-10-16/synthetic-animation');root.mkdir(exist_ok=True)
frames=[]
for i,color in enumerate(['#e33a3a','#3979ef','#48bd64']):
 image=Image.new('RGBA',(128,128),color);d=ImageDraw.Draw(image);d.text((35,55),f'FB {i+1}',fill='white',stroke_width=1)
 image.save(root/f'frame-{i+1:02d}.png');frames.append(image)
frames[0].save(root/'forgebridge-signal.gif',save_all=True,append_images=frames[1:],duration=600,loop=0,disposal=2)
(root/'manifest.json').write_text(json.dumps({'description':'ForgeBridge synthetic three-frame signal; original technical fixture, 600ms/frame, red FB1, blue FB2, green FB3','sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.suffix in ['.png','.gif']}},indent=2))

"""WAR-72 fifth-round side-by-side clean frames; crops explicitly marked diagnostic only."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;P=R/'evidence'
J=json.loads((P/'comparisons.json').read_text())
try:
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
 small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
except:
 font=ImageFont.load_default();small=font
layout=Image.new('RGB',(3*640,3*396+42),(243,245,247))
d=ImageDraw.Draw(layout)
titles=['F0 | 40mm MS · relation','F1 | 40mm closer · action','F2 | 40mm tight · key']
for col,name in enumerate(titles):
 d.text((col*640+16,4),name,font=font,fill=(30,44,58))
for row,f in enumerate((1,10,20)):
 for col,id in enumerate(('F0','F1','F2')):
  im=Image.open(P/(f'{id}_f{f:02d}.png')).convert('RGB')
  im.thumbnail((640,360))
  px=col*640;py=42+row*396
  layout.paste(im,(px,py))
  d.text((px+8,py+363),f'{id} frame {f:02d}  |  '+('covered' if f==1 else 'partial reveal' if f==10 else 'revealed'),
         font=small,fill=(36,50,65))
layout.save(P/'shot02_three_framings_3states.png')
rows=[r for r in J['measurements'] if r['frame']==20]
compare=Image.new('RGB',(4*480,320+100),(247,247,248))
d=ImageDraw.Draw(compare)
for col,id in enumerate(('F0','F1','F2','F3')):
 im=Image.open(P/f'{id}_f20.png').convert('RGB')
 im.thumbnail((480,270))
 x=col*480
 compare.paste(im,(x,42))
 data=next(r for r in rows if r['id']==id)
 bb=data['K_bbox']
 d.text((x+12,8),f'{id}  |  K {bb["width_px"]:.0f}x{bb["height_px"]:.0f}px',
        font=small,fill=(16,31,43))
 d.text((x+12,319),f'K rays {data["K_patch_clear"]}/9  Face {int(data["LinFace_in_frame"])}  Zhou {int(data["ZhouHead_in_frame"])}',
        font=small,fill=(42,56,71))
d.text((12,374),'Same 960x540 source resolution. Smaller cells shown here only for side-by-side inspection.',font=small,fill=(64,78,90))
compare.save(P/'revealed_state_4way.png')
# Diagnostic enlarged sample of K location; NOT a simulation of viewer viewing.
detail=Image.new('RGB',(4*400,450),(253,253,253));d=ImageDraw.Draw(detail)
for col,id in enumerate(('F0','F1','F2','F3')):
 data=next(r for r in rows if r['id']==id)
 u,v,z=data['K_center_norm']
 src=Image.open(P/f'{id}_f20.png').convert('RGB')
 x=int(u*960);y=int((1-v)*540)
 crop=src.crop((x-65,y-40,x+65,y+40)).resize((390,240),Image.Resampling.NEAREST)
 detail.paste(crop,(col*400+5,48))
 d.text((col*400+12,10),f'{id} / center K',font=font,fill=(35,48,64))
 d.text((col*400+12,300),'Zoom 3x / pixelated diagnostic',font=small,fill=(64,70,82))
d.text((15,411),'WARNING: These enlarged crops must NOT be used as evidence of real-size key recognition.',
        font=small,fill=(135,36,40))
detail.save(P/'key_zoom_diagnostics_NOT_viewer_test.png')
print('collages:',*[x.name for x in (P/'shot02_three_framings_3states.png',P/'revealed_state_4way.png',P/'key_zoom_diagnostics_NOT_viewer_test.png')])

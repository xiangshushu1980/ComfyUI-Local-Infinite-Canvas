#!/usr/bin/env python3
"""WAR-72 coordinates+screenshots derived summary; does not alter Blender evidence."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parent
img=Image.new('RGB',(1160,770),'#f4f6f8')
d=ImageDraw.Draw(img)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except: font=ImageFont.load_default()
try: title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
except: title=font
left,right,bottom,top=-3.35,2.65,-2.75,1.30
W,H=900,570;ox,oy=95,125
def pos(x,y):return (round(ox+(x-left)/(right-left)*W),round(oy+(top-y)/(top-bottom)*H))
def disc(x,y,r,col,label=None):
 a,b=pos(x-r,y+r);c,e=pos(x+r,y-r)
 d.ellipse((a,b,c,e),fill=col,outline='#2e4053',width=2)
 if label:d.text((c+7,b),label,font=font,fill='#16202a')
def rect(x0,y0,x1,y1,color,outline='#374151',width=2):
 a,b=pos(x0,y1);c,e=pos(x1,y0)
 d.rectangle((a,b,c,e),fill=color,outline=outline,width=width)
def ln(p,q,col,w=3):d.line([pos(*p),pos(*q)],fill=col,width=w)
d.text((75,25),'WAR-72 · B2-B3 derived spatial fixture · T1',font=title,fill='#172536')
d.text((75,65),'World: +X east, +Y north | all numerical dimensions are test assumptions',font=font,fill='#475569')
rect(-2.50,-2.65,2.5,.92,'#e7ebee')
rect(-1.1,0,1.1,.8,'#a77e59')
rect(-.72,.33,-.34,.59,'#f9fafb')
rect(-.99,.0,-.61,.29,'#2f61b2')
disc(-.25,.45,.042,'#e2e8f0','K fixed')
disc(.42,-.28,.20,'#475569','Lin')
pstart=(2.,-1.30);pend=(.85,-.35)
ln(pstart,pend,'#0e927a',4)
for i in range(21):
 t=i/20;x=pstart[0]+(pend[0]-pstart[0])*t;y=pstart[1]+(pend[1]-pstart[1])*t
 u,v=pos(x,y);d.ellipse((u-3,v-3,u+3,v+3),fill='#066d5d')
disc(*pstart,.06,'#00a68d','Zhou start')
disc(*pend,.06,'#00a68d','Zhou end')
for p,col,name in [((-1.6,-1.6),'#d97706','Shot02 baseline'),((-2.5,-2.4),'#c1322d','Shot02 revised'),((-.95,-.65),'#673ab7','Shot03')]:
 disc(*p,.07,col,name)
 ln(p,(-.25,.45),col,2)
d.text((1030,85),'N',font=title,fill='#0f172a')
d.line((1040,145,1040,105),fill='#0f172a',width=3)
d.polygon([(1040,96),(1033,113),(1047,113)],fill='#0f172a')
d.text((78,711),'Line-of-sight rays shown schematically. A clear ray is NOT proof of audience recognition.',font=font,fill='#334155')
d.text((78,739),'Note: nominal actor torso footprints and actual arm reach must be validated separately.',font=font,fill='#7c2d12')
img.save(ROOT/'spatial-relationship-diagram.png')
b=Image.open(ROOT/'baseline/T1_Shot02.png').convert('RGB')
r=Image.open(ROOT/'revision/T1_Shot02.png').convert('RGB')
o=Image.new('RGB',(1600,505),'white')
o.paste(b,(0,55));o.paste(r,(800,55))
t=ImageDraw.Draw(o);t.text((20,16),'SHOT02 ORIGINAL | overexposed / cropped actor / key low',font=font,fill='#222')
t.text((820,16),'SHOT02 REVISED | clearer framing / smaller key / long arm',font=font,fill='#222')
o.save(ROOT/'shot02-before-after.png')
print('DIAGRAMS',ROOT/'spatial-relationship-diagram.png',ROOT/'shot02-before-after.png')

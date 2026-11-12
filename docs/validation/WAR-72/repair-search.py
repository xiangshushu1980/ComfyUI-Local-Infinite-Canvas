#!/usr/bin/env python3
"""Derived position-only repair, using analytical 2D ellipse-ray minimum."""
import math,json
from pathlib import Path
P=Path(__file__).parent
K=(-.25,.45,.76); LIN=(.35,-.45); CAM=(-1.60,-1.60,1.55)
START=(2.,-1.3);END=(.85,-.35)
heading=math.atan2(END[1]-START[1],END[0]-START[0])
def eyes():
 for i in range(21):
  t=i/20;p=(START[0]*(1-t)+END[0]*t,START[1]*(1-t)+END[1]*t)
  for s in [-1,1]:yield (p[0]-math.sin(heading)*s*.032,p[1]+math.cos(heading)*s*.032,1.60)
E=list(eyes())
def hit(o,c,ax=.30,ay=.17):
 a=((o[0]-c[0])/ax,(o[1]-c[1])/ay)
 b=((K[0]-o[0])/ax,(K[1]-o[1])/ay)
 t=max(0,min(1,-(a[0]*b[0]+a[1]*b[1])/(b[0]**2+b[1]**2)))
 z=o[2]+t*(K[2]-o[2])
 return (a[0]+t*b[0])**2+(a[1]+t*b[1])**2<=1 and .85<=z<=1.75
choices=[]
for ix in range(-10,101,2):
 for iy in range(-90,-9,2):
  pos=(ix/100,iy/100)
  if math.dist(pos,K[:2])>1.15 or hit(CAM,pos):continue
  if all(hit(e,pos) for e in E):choices.append((round(math.dist(pos,LIN),3),pos))
choices.sort()
print('feasible count',len(choices),'nearest',choices[:12])
res={'assumed_torso':'elliptical width 0.60m depth 0.34m, world axes','fixed_key':K,'fixed_camera':CAM,'fixed_zhou_start':START,'fixed_zhou_end':END,'search_grid_m':.02,'lin_center_grid_x':[-.10,1.0],'lin_center_grid_y':[-.90,-.10],'count':len(choices),'nearest_candidates':choices[:20],'selected':choices[0][1] if choices else None,'limits':'derived, limited grid, no actors or cinematography'}
(P/'repair-search-results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')

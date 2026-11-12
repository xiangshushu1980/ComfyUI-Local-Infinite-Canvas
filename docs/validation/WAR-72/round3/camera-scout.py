"""WAR-72 read-only framing scout over derived 40mm Shot02 placements."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'baseline/WAR72_baseline.blend'))
sc=bpy.context.scene
cam=bpy.data.objects['SHOT02_40MM']
K=Vector((-.25,.45,.792))
L=Vector((.42,-.21,1.72))
Z=Vector((1.37,-.77,1.68))
rows=[]
for x,y,z in [(-1.6,-1.6,1.55),(-2,-2,1.65),(-2.5,-2.4,1.7),(-3,-2.5,1.8),
              (-2.3,-2.2,2.0),(-3.0,-2.6,2.1),(-1.9,-2.5,1.7)]:
 for alpha in [.35,.45,.55,.65]:
  p=Vector((x,y,z))
  target=K*(1-alpha)+L*alpha
  cam.location=p;cam.rotation_euler=(target-p).to_track_quat('-Z','Y').to_euler()
  bpy.context.view_layer.update()
  uv=[world_to_camera_view(sc,cam,Vector(a)) for a in [K,L,Z,(-.17,.45,.792),(-.28,.45,.792)]]
  uk,ul,uz=uv[:3]
  keypx=abs(uv[3].x-uv[4].x)*800
  margin=min(uk.x,1-uk.x,uk.y,1-uk.y,ul.x,1-ul.x,ul.y,1-ul.y)
  zinside=0<=uz.x<=1 and 0<=uz.y<=1
  # Prefer two-subject reading; eye can be offscreen but must be documented.
  score=margin+(.07 if zinside else 0)+(.04 if keypx>22 else -.04)
  rows.append({'position':(x,y,z),'aim_alpha_face':alpha,'key_uv':[round(uk.x,3),round(uk.y,3)],
  'lin_uv':[round(ul.x,3),round(ul.y,3)],'zhou_uv':[round(uz.x,3),round(uz.y,3)],
  'key_px':round(keypx,1),'min_margin':round(margin,3),'score':round(score,3)})
rows.sort(key=lambda a:a['score'],reverse=True)
(root/'shot02-camera-scout.json').write_text(json.dumps(rows,indent=2)+'\n')
for a in rows[:20]: print(a)

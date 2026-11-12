#!/usr/bin/env python3
"""WAR-72 derived 3D cylinder / tabletop ray check (not Blender; no image renderer)."""
import json,math
from pathlib import Path
d=json.loads((Path(__file__).parent/'geometry-results.json').read_text())
k=(-.25,.45,.76); lin=(.35,-.45); radius=.40
def obstruction(origin,dest):
    dx=dest[0]-origin[0];dy=dest[1]-origin[1]; dz=dest[2]-origin[2]
    vx=lin[0]-origin[0];vy=lin[1]-origin[1]
    t=max(0,min(1,(vx*dx+vy*dy)/(dx*dx+dy*dy)))
    gap=math.hypot(origin[0]+t*dx-lin[0],origin[1]+t*dy-lin[1])
    z=origin[2]+t*dz
    return gap<radius and .85<=z<=1.75,round(z,3),round(gap,3)
for c in ['candidate_A','candidate_B']:
    q=d[c];camera=tuple(q['camera'])+(1.55,)
    cam=obstruction(camera,k)
    checks=[]
    for row in q['zhou_samples']:
        p=tuple(row['zhou'])+(1.60,)
        checks.append(obstruction(p,k))
    print(c,'cam blocked',cam,'zhou hidden all',all(x[0] for x in checks),'ray-height bounds',[min(x[1] for x in checks),max(x[1] for x in checks)])
    q['derived_3D_check']={'camera_blocked':cam,'zhou_21_all_blocked':all(x[0] for x in checks),'zhou_ray_heights_at_nearest_body_axis':checks}
(Path(__file__).parent/'geometry-3d-results.json').write_text(json.dumps({'parameters':{'table_height':.76,'key_z':.76,'zhou_eye_z':1.60,'camera_z':1.55,'lin_occluder_radius':radius,'lin_occluder_z_range':[.85,1.75]},'candidates':{x:d[x]['derived_3D_check'] for x in ['candidate_A','candidate_B']}},ensure_ascii=False,indent=2)+'\n')

#!/usr/bin/env python3
"""WAR-72 second-pass sensitivity: 3D ray vs upright oriented torso ellipse (derived-only)."""
import json, math, itertools
from pathlib import Path
OUT=Path(__file__).parent
K=(-.25,.45,.76); LIN=(.35,-.45); CAM=(-1.60,-1.60,1.55)
START=(2.0,-1.30); END=(.85,-.35)
def ray_ellipse(eye,center,half_x,half_y,theta,low=.85,high=1.75):
    # Horizontal ray segment sample at 201 points, including height for finite torso.
    ct,st=math.cos(theta),math.sin(theta)
    for j in range(1,201):
        t=j/201
        x=eye[0]+(K[0]-eye[0])*t-center[0]
        y=eye[1]+(K[1]-eye[1])*t-center[1]
        z=eye[2]+(K[2]-eye[2])*t
        u=ct*x+st*y;v=-st*x+ct*y
        if (u/half_x)**2+(v/half_y)**2<=1 and low<=z<=high:
            return True
    return False
def path_points(n=21):
    for i in range(n):
        a=i/(n-1)
        yield (START[0]*(1-a)+END[0]*a,START[1]*(1-a)+END[1]*a)
def eye_at(p,z,offset,heading):
    # eye separation along local left/right perpendicular to walking direction
    return (p[0]-math.sin(heading)*offset,p[1]+math.cos(heading)*offset,z)
heading=math.atan2(END[1]-START[1],END[0]-START[0])
scenarios=[]
for label,hx,hy,theta,eye_z,delta in [
    ("prior cylinder equivalent",.40,.40,0,1.60,(0,0)),
    ("torso width 0.48m, depth 0.28m",.24,.14,0,1.60,(0,0)),
    ("broader torso width 0.60m, depth 0.34m",.30,.17,0,1.60,(0,0)),
    ("shoulders 0.76m, depth 0.38m",.38,.19,0,1.60,(0,0)),
    ("shoulders 0.76m, rotated 30deg",.38,.19,math.radians(30),1.60,(0,0)),
    ("shoulders 0.76m, rotated 60deg",.38,.19,math.radians(60),1.60,(0,0)),
    ("old cylinder shifted Lin 0.10m west",.40,.40,0,1.60,(-.10,0)),
    ("old cylinder shifted Lin 0.10m east",.40,.40,0,1.60,(.10,0)),
    ("old cylinder tall Zhou eyes 1.75m",.40,.40,0,1.75,(0,0)),
    ("old cylinder short Zhou eyes 1.45m",.40,.40,0,1.45,(0,0)),
]:
    center=(LIN[0]+delta[0],LIN[1]+delta[1])
    samples=[]
    for pos in path_points():
        eyes=[eye_at(pos,eye_z,s*0.032,heading) for s in (-1,1)]
        samples.append([ray_ellipse(e,center,hx,hy,theta) for e in eyes])
    camera_clear=not ray_ellipse(CAM,center,hx,hy,theta)
    count=sum(all(pair) for pair in samples)
    uncovered=[i for i,pair in enumerate(samples) if not all(pair)]
    scenarios.append({'scenario':label,'lin_center':center,'ellipse_half_axes':(hx,hy),'body_rotation_degrees':round(math.degrees(theta)),'eye_z':eye_z,'camera_clear':camera_clear,'both_eyes_occluded_count':count,'total_path_points':len(samples),'first_failed_index':uncovered[0] if uncovered else None,'failed_indices':uncovered,'both_eyes_all_blocked':count==len(samples)})
for s in scenarios:
    print(s['scenario'],': camera_clear',s['camera_clear'],'zhou both eyes hidden',str(s['both_eyes_occluded_count'])+'/21','first_failed',s['first_failed_index'])
# Near-camera FOV and target composition: simple pinhole under framing angle, not optics simulator.
def target_projection(camera,target,aim,focal):
    v=[aim[i]-camera[i] for i in range(3)];norm=math.sqrt(sum(x*x for x in v));v=[x/norm for x in v]
    u=[target[i]-camera[i] for i in range(3)]
    depth=sum(u[i]*v[i] for i in range(3))
    angle=math.degrees(math.acos(max(-1,min(1,depth/max(1e-8,math.sqrt(sum(x*x for x in u)))))))
    diag_hfov=2*math.degrees(math.atan(36/(2*focal)))
    diag_vfov=2*math.degrees(math.atan(20.25/(2*focal)))
    return {'depth_m':round(depth,3),'target_angle_from_axis_deg':round(angle,2),'full_horizontal_fov_deg':round(diag_hfov,2),'full_vertical_fov_deg':round(diag_vfov,2)}
optics={
 'shot02_40mm_cameraB_aim_key':target_projection(CAM,K,K,40),
 'shot02_40mm_cameraB_aim_lin_face':target_projection(CAM,K,(LIN[0],LIN[1],1.65),40),
 'shot03_85mm_cameraB_aim_key':target_projection(CAM,K,K,85),
 'note':'Target-angle radial test does not ensure 16:9 frame x/y placement, occluding hands, or correct MS/ECU size. Lens center directed at K is not a sufficient Shot02 framing plan.'
}
payload={'model':'derived finite-height oriented ellipse body; 201 uniform points per ray (not continuous root solver)','reference':'WAR-72 2026-11-12 first pass','camera':CAM,'key':K,'eye_separation_m':.064,'path_samples':21,'scenarios':scenarios,'optics':optics}
(OUT/'robustness-results.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')

#!/usr/bin/env python3
"""WAR-72 derived 2D horizontal-plane visibility check; all values are test assumptions."""
import json, math
from pathlib import Path
OUT=Path(__file__).parent
K=(-0.25,0.45); LIN=(0.35,-0.45); R=.40
DOOR=(2.0,-1.30); END=(0.85,-0.35)
CAM=(-1.60,-1.60)
CAM_BAD=(1.55,-1.50)
TABLE=(-1.10,1.10,0.0,0.80)
PAPER=(-.38,-.12,.32,.57)
FOLDER=(-.55,-.03,.30,.62)
def dist_seg(p,a,b):
    vx=b[0]-a[0];vy=b[1]-a[1];den=vx*vx+vy*vy
    t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/den))
    return math.hypot(p[0]-(a[0]+t*vx),p[1]-(a[1]+t*vy)),t
def occluded(a):
    dd,t=dist_seg(LIN,a,K)
    return dd<R and 0<t<1,round(dd,4),round(t,4)
def side(cam,p):
    v=(p[0]-LIN[0],p[1]-LIN[1]);w=(cam[0]-LIN[0],cam[1]-LIN[1])
    return v[0]*w[1]-v[1]*w[0]
def interp(a,b,t):return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
def check(cam):
    path=[]
    for i in range(21):
        p=interp(DOOR,END,i/20);block,d,t=occluded(p)
        path.append({'fraction':round(i/20,2),'zhou':tuple(round(x,3) for x in p),'lin_blocks_K_2D':block,'distance_to_line_m':d,'axis_side':round(side(cam,p),4)})
    cam_block,cam_dist,_=occluded(cam)
    return {'camera':cam,'camera_blocked_by_lin_2D':cam_block,'camera_line_clear_2D':not cam_block,'camera_line_min_distance_to_lin_m':cam_dist,'zhou_samples':path,'zhou_all_blocked_2D':all(p['lin_blocks_K_2D'] for p in path),'axis_sign_constant':min(p['axis_side'] for p in path)*max(p['axis_side'] for p in path)>0,'camera_key_distance_m':round(math.dist(cam,K),3),'key_width_fraction_40mm_36mm_sensor_approx':round((.06/math.dist(cam,K))/(36/40),4)}
data={'units':'m','world':'x east+, y north+','frozen_constraints':['north-wall table','east-wall door','Lin south of table','Zhou door to table','K fixed'],'derived_2D_assumptions':{'table':TABLE,'key_K':K,'lin_center':LIN,'lin_occluder_disc_radius_m':R,'zhou_start':DOOR,'zhou_end':END,'paper_at_initial':PAPER,'folder_after_B3':FOLDER,'paper_and_folder_are_top_down_cover_rectangles':True,'key_nominal_width_m':.06},'candidate_A':check(CAM_BAD),'candidate_B':check(CAM)}
for name,v in [('A',data['candidate_A']),('B',data['candidate_B'])]:
 print(name,'cam clear',v['camera_line_clear_2D'],'zhou blocked all',v['zhou_all_blocked_2D'],'axis consistent',v['axis_sign_constant'],'range d',[min(p['distance_to_line_m'] for p in v['zhou_samples']),max(p['distance_to_line_m'] for p in v['zhou_samples'])],'axis range',[min(p['axis_side'] for p in v['zhou_samples']),max(p['axis_side'] for p in v['zhou_samples'])])
(OUT/'geometry-results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

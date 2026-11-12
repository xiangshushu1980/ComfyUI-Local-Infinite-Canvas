#!/usr/bin/env python3
"""Supplementary WAR-72 geometry metrics, using already-frozen third-round JSON."""
import json,math
from pathlib import Path
P=Path(__file__).resolve().parent
a=json.loads((P/'baseline/measurements.json').read_text())
b=json.loads((P/'revision/measurements.json').read_text())
LIN=(.42,-.28); START=(2.,-1.30); END=(.85,-.35)
CAM={'shot02_baseline':(-1.6,-1.6),'shot02_revised':(-2.5,-2.4),
     'shot03':(-.95,-.65)}
def cross(v,w):return v[0]*w[1]-v[1]*w[0]
axes={}
for name,c in CAM.items():
 vals=[]
 for i in range(21):
  t=i/20;z=(START[0]*(1-t)+END[0]*t,START[1]*(1-t)+END[1]*t)
  vals.append(round(cross((z[0]-LIN[0],z[1]-LIN[1]),(c[0]-LIN[0],c[1]-LIN[1])),4))
 axes[name]={'all_negative':all(x<0 for x in vals),'sign_crossing':min(vals)<0<max(vals),
             'min':min(vals),'max':max(vals),'values_21':vals}
v1=tuple(a['coordinates']['CAM2'][i]-a['coordinates']['K'][i] for i in range(3))
v2=tuple(b['coordinates']['CAM2'][i]-b['coordinates']['K'][i] for i in range(3))
v3=tuple(b['coordinates']['CAM3'][i]-b['coordinates']['K'][i] for i in range(3))
def angle(x,y):
 dot=sum(xx*yy for xx,yy in zip(x,y))
 return round(math.degrees(math.acos(max(-1,min(1,dot/(math.dist(x,(0,0,0))*math.dist(y,(0,0,0))))))),2)
metrics={'dynamic_actor_axis':axes,
         'shot02_to_shot03_optical_station_angle_deg_baseline':angle(v1,v3),
         'shot02_to_shot03_optical_station_angle_deg_revision':angle(v2,v3),
         'camera_key_clear_all_21':{
           'baseline_cam2':all(not k['camera2']['blocked'] for k in b['camera_path_21']) if False else None,
           'revision_cam2':all(not k['camera2']['blocked'] for k in b['camera_path_21']),
           'revision_cam3':all(not k['camera3']['blocked'] for k in b['camera_path_21'])},
         'world_east_screen_direction':{
          name:round(j['projection']['key_east_end']['uv_depth'][0]-
                     j['projection']['key_center']['uv_depth'][0],4)
          for name,j in [('shot02_revised',b['camera_checks']['SHOT02_40MM_f20']),
                         ('shot03',b['camera_checks']['SHOT03_85MM_f20'])]},
         'key_surface_assumptions':{
           'table_top_z':.75,
           'key_mesh_lowest_z':.787,
           'key_table_air_gap_m':round(.787-.75,3),
           'revision_paper_stack_top_z':.827,
           'revision_folder_bottom_z':.829,
           'folder_paper_gap_m':.002,
           'folder_above_key_top_gap_m':.029,
           'invalid_realism_warning':'Key physically floats 3.7 cm above tabletop; cannot claim realistic prop physics.'}}
(P/'axis-and-contact-checks.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in metrics.items() if k!='dynamic_actor_axis'},indent=2))
print('axis extrema',[(k,d['min'],d['max']) for k,d in axes.items()])

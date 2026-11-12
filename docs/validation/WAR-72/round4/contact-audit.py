"""WAR-72 round4 additional contact and framing audit. Non-mutating: opens candidate B .blend."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent
F=R/'candidate-b/WAR72_physical_B.blend'
bpy.ops.wm.open_mainfile(filepath=str(F))
sc=bpy.context.scene
ob=bpy.data.objects
def setframe(f):sc.frame_set(f);bpy.context.view_layer.update()
def pts(o):return [o.matrix_world@Vector(c) for c in o.bound_box]
def zrange(o):return [round(min(x.z for x in pts(o)),5),round(max(x.z for x in pts(o)),5)]
def bvh(o):
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
 [tuple(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=1e-7)
def overlap(a,b):return len(bvh(a).overlap(bvh(b)))>0
def screen_bbox(cam,objects):
 points=[]
 for o in objects:
  for v in o.data.vertices:
   world=o.matrix_world@v.co
   uv=world_to_camera_view(sc,cam,world)
   points.append((uv.x,uv.y,uv.z))
 return {'left':round(min(x[0] for x in points),5),
         'right':round(max(x[0] for x in points),5),
         'bottom':round(min(x[1] for x in points),5),
         'top':round(max(x[1] for x in points),5),
         'span_px':round((max(x[0] for x in points)-min(x[0] for x in points))*sc.render.resolution_x,2),
         'height_px':round((max(x[1] for x in points)-min(x[1] for x in points))*sc.render.resolution_y,2)}
pairs=[('LIN_TORSO','DESK_TOP'),('LIN_HEAD','DESK_TOP'),('LIN_L_FOREARM','DESK_TOP'),
       ('LIN_R_FOREARM','DESK_TOP'),('LIN_LEFT_HAND','PAPER_MOVING'),
       ('LIN_LEFT_HAND','BLUE_FOLDER'),('PAPER_MOVING','BLUE_FOLDER'),
       ('BLUE_FOLDER','KEY_FIXED_RING'),('PAPER_MOVING','KEY_FIXED_RING'),
       ('LIN_LEFT_HAND','KEY_FIXED_RING')]
out={'filename':str(F),'contact_matrix':{},'screen_extent':{},'axis_cross_sign':{},'derived_only':True}
key_objs=[ob[x] for x in ['KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH']]
for f in [1,8,20,30,34,40]:
 setframe(f)
 state={}
 for a,b in pairs:
  try:state[a+' / '+b]=overlap(ob[a],ob[b])
  except Exception as e:state[a+' / '+b]='error '+str(e)
 state['desk_top']=zrange(ob['DESK_TOP'])
 state['key_torus']=zrange(ob['KEY_FIXED_RING'])
 state['file_paper']=zrange(ob['PAPER_MOVING'])
 state['folder']=zrange(ob['BLUE_FOLDER'])
 state['lin_left_hand']=zrange(ob['LIN_LEFT_HAND'])
 out['contact_matrix'][str(f)]=state
 if f in (20,40):
  out['screen_extent'][str(f)]={}
  for cam in ['SHOT02_40MM','SHOT03_85MM']:
   out['screen_extent'][str(f)][cam]=screen_bbox(ob[cam],key_objs)
for cam in ['SHOT02_40MM','SHOT03_85MM']:
 v=[]
 for i in range(21):
  t=i/20
  z=Vector((2.+(1.10-2.)*t,-1.30+(-.52+1.30)*t,0))
  LIN=(.42,-.28);o=ob[cam].location
  cross=(z.x-LIN[0])*(o.y-LIN[1])-(z.y-LIN[1])*(o.x-LIN[0])
  v.append(round(cross,5))
 out['axis_cross_sign'][cam]={'min':min(v),'max':max(v),'crosses_axis':min(v)<0<max(v),'samples':v}
(R/'candidate-b/contact-audit.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('WORLD AUDIT',json.dumps({
 'desk':out['contact_matrix']['20']['desk_top'],
 'key':out['contact_matrix']['20']['key_torus'],
 'actor_desk_overlaps':{f:{k:v for k,v in s.items() if 'DESK_TOP' in k} for f,s in out['contact_matrix'].items()},
 'prop_mesh_overlap_40':{k:v for k,v in out['contact_matrix']['40'].items() if ' / ' in k},
 'key_in_frame':out['screen_extent'],
 'axis_cross_sign':{k:{a:b for a,b in v.items() if a!='samples'} for k,v in out['axis_cross_sign'].items()}}),flush=True)

"""WAR-72 round4: independent physically corrected Blender CPU proxy.
Loads round3/revision .blend read-only; preserves all earlier evidence.
"""
import bpy, json, math, csv
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

R=Path(__file__).resolve().parent
IN=R.parent/'round3/revision/WAR72_revision.blend'
OUT=R/'candidate-a';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(IN))
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU'
sc.cycles.samples=10;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=960;sc.render.resolution_y=540
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
objs=bpy.data.objects;ob=lambda n:objs[n]
V=Vector
frames=[1,8,20,30,34,40]
K=V((-.25,.45,.755));LIN=(.42,-.28)
ZSTART=V((2.,-1.30,0));ZEND=V((1.10,-.52,0))
def frame(f):sc.frame_set(f);bpy.context.view_layer.update()
def keypose(obj,f,point):
 obj.location=V(point);obj.keyframe_insert(data_path='location',frame=f)
def bone(o,a,b,r,f=None):
 a,b=V(a),V(b);o.location=(a+b)*.5
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 o.scale=(r,r,(b-a).length/2)
 if f is not None:
  for x in ['location','rotation_euler','scale']:o.keyframe_insert(data_path=x,frame=f)
# Correct actual mesh bottom to z=0.750, preserving K x/y in every frame.
for name in ['KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH']:
 ob(name).location.z-=.037
for i in range(4):ob('STACK_%02d'%i).location.z-=.0355
paper=ob('PAPER_MOVING');folder=ob('BLUE_FOLDER')
paper_z={1:.764,8:.831,20:.7885,30:.7885,34:.7885,40:.7885}
folder_z={1:.757,8:.757,20:.757,30:1.07,34:.91,40:.791}
for f in frames:
 frame(f)
 p=paper.location.copy();p.z=paper_z[f];keypose(paper,f,p)
 p=folder.location.copy();p.z=folder_z[f];keypose(folder,f,p)
# Bent Lin proxy: hip fixed in same location, neck and shoulders shift forward-left.
hip=V((.42,-.28,.91));shoulders=V((.105,.060,1.290))
sL=shoulders+V((-.235,0,0));sR=shoulders+V((.235,0,0))
t=ob('LIN_TORSO');t.location=(hip+shoulders)*.5
t.rotation_euler=(shoulders-hip).to_track_quat('Z','Y').to_euler()
t.scale=(.30,.17,(shoulders-hip).length*.61)
ob('LIN_SHOULDERS').location=shoulders+V((0,0,.015))
ob('LIN_HEAD').location=shoulders+V((-.005,.09,.18))
bone(ob('LIN_NECK'),shoulders+V((0,.02,.09)),shoulders+V((0,.07,.14)),.064)
# Left hand handles paper and folder, right hand braced on desk.
L={1:(-.265,.45,.777),8:(-.40,.45,.88),20:(-.53,.45,.808),
  30:(-.67,.30,1.093),34:(-.48,.43,.945),40:(-.37,.46,.807)}
RT=(.42,.12,.812)
ARM=(.385,.385)
def elbow(s,w,sign):
 diff=w-s;dist=diff.length;u=diff.normalized();a,b=ARM
 ok=abs(a-b)+1e-7<dist<=a+b+1e-7
 if not ok:return s+u*a,False,dist
 along=(a*a-b*b+dist*dist)/(2*dist)
 height=math.sqrt(max(0,a*a-along*along))
 side=u.cross(V((0,0,1)))
 if side.length<1e-8:side=V((0,1,0))
 return s+along*u+sign*height*side.normalized(),True,dist
reach=[]
for f in frames:
 for side,sh,target,hand,upper,fore,sign in [
  ('L',sL,L[f],'LIN_LEFT_HAND','LIN_L_UPPER','LIN_L_FOREARM',1),
  ('R',sR,RT,'LIN_RIGHT_HAND','LIN_R_UPPER','LIN_R_FOREARM',-1)]:
  wrist=V(target);e,ok,dist=elbow(sh,wrist,sign)
  keypose(ob(hand),f,wrist)
  bone(ob(upper),sh,e,.066,f);bone(ob(fore),e,wrist,.054,f)
  reach.append({'f':f,'hand':side,'shoulder_wrist_distance_m':round(dist,5),
   'arm_length_m':sum(ARM),'can_reach':ok,
   'upper_length_m':round((e-sh).length,5),
   'forearm_length_m':round((wrist-e).length,5)})
zh=ob('ZHOU_ROOT_PATH')
vec=(ZEND-ZSTART).normalized()
zh.rotation_euler.z=math.atan2(-vec.x,vec.y)
for f,ratio in [(1,0),(20,.55),(40,1)]:
 keypose(zh,f,ZSTART*(1-ratio)+ZEND*ratio)
# Use LINEAR rather than bezier interpolation between derived key pose targets
for ac in bpy.data.actions:
 if hasattr(ac,'fcurves'):
  for fc in ac.fcurves:
   for pt in fc.keyframe_points:pt.interpolation='LINEAR'

cam2=ob('SHOT02_40MM');cam3=ob('SHOT03_85MM')
ign={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST',
     'KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH'}
blockers=[o for o in objs if o.type=='MESH' and o.name not in ign]
def ray(start,target,skip_self=False):
 a,b=V(start),V(target);best=(1.,None)
 for o in blockers:
  if skip_self and o.name.startswith('ZHOU_'):continue
  inv=o.matrix_world.inverted()
  x,y=inv@a,inv@b;vec=y-x
  if vec.length<1e-8:continue
  hit,p,n,ix=o.ray_cast(x,vec.normalized(),distance=vec.length*.995)
  if hit:
   frac=(p-x).length/vec.length
   if frac<best[0]:best=(frac,o.name)
 return {'blocker':best[1],'blocked':best[1] is not None,
    'distance_from_eye_m':round((b-a).length*best[0],5),
    'lin_occluder':(best[1] or '').startswith('LIN_')}
def do_path(n,z=1.6,turn=0):
 rows=[]
 for i in range(n):
  ratio=i/(n-1);zh.location=ZSTART*(1-ratio)+ZEND*ratio
  bpy.context.view_layer.update()
  eyes=[]
  for name in ['ZHOU_LEFT_EYE','ZHOU_RIGHT_EYE']:
   x=ob(name).matrix_world.translation.copy()
   if turn:
    pivot=ob('ZHOU_HEAD').matrix_world.translation.copy()
    phi=math.radians(turn);delta=x-pivot
    x=pivot+V((delta.x*math.cos(phi)-delta.y*math.sin(phi),
               delta.x*math.sin(phi)+delta.y*math.cos(phi),delta.z))
   x.z+=z-1.6
   eyes.append(ray(x,K,True))
  both=all(a['lin_occluder'] and a['distance_from_eye_m']>.16 for a in eyes)
  rc2=ray(cam2.location,K);rc3=ray(cam3.location,K)
  rows.append({'i':i,'ratio':round(ratio,4),'zhou_xy':[round(zh.location.x,4),round(zh.location.y,4)],
               'left':eyes[0],'right':eyes[1],'both_lin_hidden_at_safe_distance':both,
               'cam2_clear':not rc2['blocked'],'cam3_clear':not rc3['blocked'],
               'center_separation_m':round(math.dist((zh.location.x,zh.location.y),LIN),4)})
 return rows
def summ(rs):
 return {'n':len(rs),'both_hidden':sum(r['both_lin_hidden_at_safe_distance'] for r in rs),
         'failed_indices':[r['i'] for r in rs if not r['both_lin_hidden_at_safe_distance']],
         'cam2_clear':sum(r['cam2_clear'] for r in rs),
         'cam3_clear':sum(r['cam3_clear'] for r in rs),
         'min_centers_m':min(r['center_separation_m'] for r in rs)}
frame(20)
P21=do_path(21);P81=do_path(81)
sens={name:summ(do_path(21,z,yaw)) for name,z,yaw in [
 ('left12',1.6,-12),('right12',1.6,12),('short1.5',1.5,0),('tall1.7',1.7,0)]}
# BVH triangle-triangle surface intersections for the Lin/Zhou actor geometry
linmesh=[x for x in blockers if x.name.startswith('LIN_')]
zhmesh=[x for x in blockers if x.name.startswith('ZHOU_')]
def bvh(o):
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                             [tuple(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=0)
collisions=[]
for i in range(21):
 r=i/20;zh.location=ZSTART*(1-r)+ZEND*r;bpy.context.view_layer.update()
 matches=[]
 for a in linmesh:
  t=bvh(a)
  for b in zhmesh:
   if t.overlap(bvh(b)):matches.append([a.name,b.name])
 collisions.append({'i':i,'world_mesh_triangle_overlap_pairs':matches})
def bounds(o):
 v=[o.matrix_world@V(c) for c in o.bound_box]
 return [[round(min(x[j] for x in v),5),round(max(x[j] for x in v),5)] for j in range(3)]
prop={}
for f in (1,8,10,20,30,34,40):
 frame(f)
 prop[str(f)]={'key_bounds':bounds(ob('KEY_FIXED_RING')),
               'moving_paper_bounds':bounds(paper),
               'folder_bounds':bounds(folder),
               'top_stack_page_bounds':bounds(ob('STACK_03'))}
patch=[V((x,y,K.z)) for x in (-.28,-.23,-.17) for y in (.43,.45,.47)]
keypatch={}
for f in (1,20,34,40):
 frame(f)
 keypatch[str(f)]={'cam2':[ray(cam2.location,q)['blocked'] for q in patch],
                   'cam3':[ray(cam3.location,q)['blocked'] for q in patch]}
views={}
for f,c in [(1,cam2),(20,cam2),(20,cam3),(34,cam3),(40,cam3)]:
 frame(f)
 v={}
 for label,point in [('K',K),('LinHead',ob('LIN_HEAD').matrix_world.translation),
  ('ZhouHead',ob('ZHOU_HEAD').matrix_world.translation),
  ('LeftHand',ob('LIN_LEFT_HAND').matrix_world.translation)]:
  x=world_to_camera_view(sc,c,V(point))
  v[label]=[round(x.x,4),round(x.y,4),round(x.z,4)]
 views[c.name+'_'+str(f)]=v
result={'context':'WAR-72 independent next physics gate, candidate A','source_blend':str(IN),
'blender_version':bpy.app.version_string,'cpu_only':sc.cycles.device=='CPU',
'derived':{'K':list(K),'K_z_shift_m':-.037,'table_top':.75,'LinFeet':LIN,
           'LinBentShoulders':list(shoulders),'left_shoulder':list(sL),
           'arm_segments':ARM,'ZhouStart':list(ZSTART),'ZhouEnd':list(ZEND),
           'paper_z':paper_z,'folder_z':folder_z},
'arm_reach':reach,'path_21':P21,'path_21_summary':summ(P21),
'path_81_summary':summ(P81),'sensitivity_summary':sens,
'actor_surface_overlaps_21':collisions,'prop_states':prop,
'key_3x3_visibility':keypatch,'views':views,
'limits':['BVH mesh surface intersection may miss total mesh containment',
'Elbow IK tests key poses, not continuous joint biomechanics',
'Path samples do not prove every continuous point','Rendered framing does not prove attention',
'Blue folder and paper have no rigid-body gravity simulation']}
(OUT/'physical-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'eyes-21.csv').open('w',newline='',encoding='utf-8') as file:
 w=csv.writer(file)
 w.writerow(['i','zhou_xy','left_block','left_distance','right_block','right_distance',
             'both_safe_occluded','cam2_clear','cam3_clear','actor_mesh_collisions'])
 for x in P21:
  i=x['i'];w.writerow([i,x['zhou_xy'],x['left']['blocker'],x['left']['distance_from_eye_m'],
    x['right']['blocker'],x['right']['distance_from_eye_m'],
    x['both_lin_hidden_at_safe_distance'],x['cam2_clear'],x['cam3_clear'],
    collisions[i]['world_mesh_triangle_overlap_pairs']])
print('RESULTS',json.dumps({'21':summ(P21),'81':summ(P81),'sensitivity':sens,
 'unreachable':[x for x in reach if not x['can_reach']],
 'actor_overlap_count':sum(bool(x['world_mesh_triangle_overlap_pairs']) for x in collisions),
 'patch':{f:{name:sum(arr) for name,arr in state.items()} for f,state in keypatch.items()}},
 ensure_ascii=False),flush=True)
frame(20);sc.camera=cam2
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAR72_physical_A.blend'))
for f,c,name in [(1,cam2,'T0_Shot02.png'),(10,cam2,'transition_T0_T1.png'),
 (20,cam2,'T1_Shot02.png'),(20,cam3,'T1_Shot03.png'),
 (34,cam3,'transition_T1_T2.png'),(40,cam3,'T2_Shot03.png'),
 (20,ob('TOP_PLAN'),'top_T1.png')]:
 frame(f);sc.camera=c;sc.render.filepath=str(OUT/name)
 bpy.ops.render.render(write_still=True)
 print('RENDERED',name,flush=True)
print('DONE_PHYSICAL_A',flush=True)

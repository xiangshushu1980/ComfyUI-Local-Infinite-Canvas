"""WAR-90 light V2 swept proxy spot checks, only sampled paths, no rig or video."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
src,out=[Path(x) for x in sys.argv[sys.argv.index('--')+1:]]
EXPECT='a4c7b48a9dac825c5422c626b17242599eeacbb9115eb640fe8d7f20e34f75a3'
assert hashlib.sha256(src.read_bytes()).hexdigest()==EXPECT
bpy.ops.wm.open_mainfile(filepath=str(src))
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';O=bpy.data.objects
sc.frame_set(40);bpy.context.view_layer.update()
# Local proxy correction BEFORE the step: old WAR72 right forearm intersects tabletop.
# Bring the right wrist to an above-table resting/sorting location outside the desk footprint.
ss=V((.34,.06,1.29));ww=V((.38,-.18,1.00));u=(ww-ss).normalized();length=(ww-ss).length
up=V((0,0,1));side=(up-u*up.dot(u)).normalized();ee=ss+(ww-ss)*.5+side*math.sqrt(.385**2-(length*.5)**2)
def setarm(obj,a,b,r):
 obj.location=(a+b)*.5;obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();obj.scale=(r,r,(b-a).length*.5)
setarm(O['LIN_R_UPPER'],ss,ee,.066);setarm(O['LIN_R_FOREARM'],ee,ww,.054)
O['LIN_RIGHT_HAND'].location=ww;bpy.context.view_layer.update()
VEC=V;K=V((-.25,.45,.755));keynames=['KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH']
ign={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST',*keynames}
blocks=[ob for ob in O if ob.type=='MESH' and ob.name not in ign]
lin=[ob for ob in O if ob.name.startswith('LIN_') and ob.type=='MESH']
lin0={ob.name:ob.location.copy() for ob in lin}
folder=O['BLUE_FOLDER'];f0=folder.location.copy()
key0={n:O[n].location.copy() for n in keynames}
def update():bpy.context.view_layer.update()
def first(a,b,skipzhou=False):
 a,b=V(a),V(b);best=(1.,None)
 for obj in blocks:
  if skipzhou and obj.name.startswith('ZHOU_'):continue
  tx=obj.matrix_world.inverted();x,y=tx@a,tx@b;v=y-x
  if v.length<1e-7:continue
  hit,p,_,_=obj.ray_cast(x,v.normalized(),distance=v.length*.997)
  if hit:
   frac=(p-x).length/v.length
   if frac<best[0]:best=(frac,obj.name)
 return best[1]
def bounds(obj):
 pts=[obj.matrix_world@V(x) for x in obj.bound_box]
 return [(min(q[i] for q in pts),max(q[i] for q in pts)) for i in range(3)]
def bvh(ob):
 return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],
 [tuple(p.vertices) for p in ob.data.polygons],epsilon=1e-6)
def hit(a,b):return bool(bvh(O[a]).overlap(bvh(O[b])))
def actor_contact():
 # test only actors' actual triangle surfaces (not complete mesh containment)
 overlap=[]
 L=[obj for obj in lin]
 Z=[obj for obj in O if obj.type=='MESH' and obj.name.startswith('ZHOU_')]
 for a in L:
  ga=bvh(a)
  for b in Z:
   if ga.overlap(bvh(b)):overlap.append([a.name,b.name])
 return overlap
folder_center=lambda:V((K.x,K.y,bounds(folder)[2][1]+.002))
rows=[]
for i in range(11):
 t=i/10
 for ob in lin:ob.location=lin0[ob.name]+V((-.2*t,-.2*t,0))
 update()
 eyes=[]
 for n in ('ZHOU_LEFT_EYE','ZHOU_RIGHT_EYE'):
  p=O[n].matrix_world.translation
  eyes.append({'eye':n,'folder_xy_hit':first(p,folder_center(),True),
               'K_hit':first(p,K,True)})
 contacts=actor_contact()
 rows.append({'t':t,'eyes':eyes,'actor_mesh_crossings':contacts,
  'lin_desk_crossings':[n for n in ['LIN_TORSO','LIN_R_FOREARM','LIN_RIGHT_HAND','LIN_L_FOREARM','LIN_LEFT_HAND','LIN_PANTS'] if hit(n,'DESK_TOP')],
  'cam_K_hits':{n:first(O[n].location,K) for n in ['WAR91_Action40','WAR91_Desk40']}})
for ob in lin:ob.location=lin0[ob.name]+V((-.2,-.2,0))
update()
uncover=[]
folder_move=V((-.3,-.2,.27))
for i in range(11):
 t=i/10
 folder.location=f0+folder_move*t
 update()
 uncleared={n:first(O[n].location,K) for n in ('WAR91_Action40','WAR91_Desk40')}
 collisions={n:hit('BLUE_FOLDER',n) for n in keynames}
 paper=hit('BLUE_FOLDER','PAPER_MOVING')
 uncover.append({'t':t,'camera_to_K':uncleared,
  'folder_key_mesh_intersection':collisions,'folder_paper_surface_intersection':paper})
folder.location=f0+folder_move;update()
H=V((.75,-.25,1.16));r_sh=V((.16,.18,1.18))
zh_sh=O['ZHOU_SHOULDERS'].matrix_world.translation+V((.20*math.cos(O['ZHOU_ROOT_PATH'].rotation_euler.z),.20*math.sin(O['ZHOU_ROOT_PATH'].rotation_euler.z),0))
trans=[]
for i in range(11):
 t=i/10
 p=K+(H-K)*t
 for n in keynames:O[n].location=key0[n]+(p-K)
 update()
 contacts={obj:sum(hit(n,obj) for n in keynames) for obj in ['DESK_TOP','PAPER_MOVING','BLUE_FOLDER','LIN_TORSO','ZHOU_TORSO']}
 wrist=V((-.25,.45,.8))+(V((.715,-.25,1.175))-V((-.25,.45,.8)))*t
 trans.append({'t':t,'key_proxy_center':[round(x,4) for x in p],
   'Lin_arm_reach_m':round((wrist-r_sh).length,5),'key_mesh_surface_intersections':contacts})
results={'source_sha256':EXPECT,'blender':bpy.app.version_string,'rendered':False,
 'steps':'11 evenly spaced discrete positions per path, not continuous collision guarantee',
 'Lin_step_after_cover':rows,'folder_uncover_translation':uncover,'key_transfer_proxy_line':trans,
 'Zhou_right_shoulder_proxy':[round(z,4) for z in zh_sh],
 'Zhou_right_shoulder_to_transfer_m':round((zh_sh-H).length,5),
 'limitations':['Lin step interpolates whole proxy actor, ignoring balance/footfall.',
   'Folder motion changes rigid object without animating Lin hand grip; swept hand and object interactions are unverified.',
   'Key moves linearly without articulated finger grip or two-player arm collision test; state-matching proof remains semantic.',
   'Surface BVH misses complete containment and is not a dynamics/real-avatar guarantee.',
   'No actual camera-cut sequence, timing, H3 media or audience interpretation was tested.']}
out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('SWEEP_STEP',[(z['t'],z['eyes'][0]['folder_xy_hit'],z['eyes'][1]['folder_xy_hit']) for z in rows])
print('SWEEP_ACTOR_COLL',[(z['t'],len(z['actor_mesh_crossings']),z['lin_desk_crossings']) for z in rows])
print('SWEEP_FOLDER',[(z['t'],z['camera_to_K'],z['folder_key_mesh_intersection']) for z in uncover])
print('SWEEP_KEY',[(z['t'],z['Lin_arm_reach_m'],z['key_mesh_surface_intersections']) for z in trans])
print('SWEEP_DONE')

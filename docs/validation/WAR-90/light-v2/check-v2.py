"""WAR-90 D V2 fast, bounded Blender geometry + state seam test.
Source is WAR-91 derived cam proxy, not the approved four-shot production scene.
No render, CPU only, no edit of source; snapshots are discrete NOT timed animation.
"""
import bpy,sys,hashlib,json,math
from pathlib import Path
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
src,out=[Path(x) for x in sys.argv[sys.argv.index('--')+1:]]
EXPECTED='a4c7b48a9dac825c5422c626b17242599eeacbb9115eb640fe8d7f20e34f75a3'
assert src.is_file() and hashlib.sha256(src.read_bytes()).hexdigest()==EXPECTED
assert 'WAR-90' in str(out)
bpy.ops.wm.open_mainfile(filepath=str(src))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU'
O=bpy.data.objects
K=V((-.25,.45,.755))
KEY=('KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH')
CAM=('WAR91_Action40','WAR91_Desk40')
ign={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST',*KEY}
block=[o for o in O if o.type=='MESH' and o.name not in ign]
def vv(v):return [round(float(z),5) for z in v]
def box(obj):
 pts=[obj.matrix_world@V(x) for x in obj.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def ray(a,b,skip_zhou=False):
 a,b=V(a),V(b);best=(1.,None)
 for ob in block:
  if skip_zhou and ob.name.startswith('ZHOU_'):continue
  t=ob.matrix_world.inverted();aa,bb=t@a,t@b;dif=bb-aa
  if dif.length<1e-7:continue
  hit,p,_,_=ob.ray_cast(aa,dif.normalized(),distance=dif.length*.997)
  if hit:
   frac=(p-aa).length/dif.length
   if frac<best[0]:best=(frac,ob.name)
 return best[1]
def updated():bpy.context.view_layer.update()
def folder_spots():
 b=box(O['BLUE_FOLDER'])
 return [V((b[0][0]+(i+.5)/5*(b[0][1]-b[0][0]),
   b[1][0]+(j+.5)/5*(b[1][1]-b[1][0]),b[2][1]+.002))
   for i in range(5) for j in range(5)]
def eye_report():
 spots=folder_spots();b=box(O['BLUE_FOLDER'])
 target=V((K.x,K.y,b[2][1]+.002))
 ret=[]
 for eye in ('ZHOU_LEFT_EYE','ZHOU_RIGHT_EYE'):
  p=O[eye].matrix_world.translation.copy()
  hits=[ray(p,q,True) for q in spots]
  keyhit=ray(p,K,True)
  ret.append({'eye':eye,'folder_visible_of_25':sum(h in (None,'BLUE_FOLDER') for h in hits),
   'covered_xy_target_hit':ray(p,target,True),'key_ray_occluder':keyhit})
 return ret
def camera_patch(frame):
 scene.frame_set(frame);updated()
 patch=[V((x,y,K.z)) for x in (-.28,-.23,-.17) for y in (.43,.45,.47)]
 return {n:{'clear_9':sum(ray(O[n].location,p) is None for p in patch),
             'folder_in_frame':bool(0<=world_to_camera_view(scene,O[n],O['BLUE_FOLDER'].matrix_world.translation).x<=1)}
         for n in CAM}
def pose_beam(o,a,b,r):
 a,b=V(a),V(b);o.location=(a+b)*.5
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 o.scale=(r,r,(b-a).length/2)
def elbow(s,w,side=1):
 s,w=V(s),V(w);delta=w-s;dist=delta.length;a=b=.385
 if dist>a+b or dist<1e-5:return None
 u=delta.normalized();z=V((0,0,1));perp=z-u*u.dot(z)
 if perp.length<1e-6:perp=V((0,1,0))
 return s+u*(dist/2)+side*math.sqrt(max(0,a*a-(dist/2)**2))*perp.normalized()
def pose_lin(center,left_w,right_w):
 center=V(center);left_w=V(left_w);right_w=V(right_w)
 hip=V((.42,-.28,.91))+V((-.2,-.2,0))
 pose_beam(O['LIN_TORSO'],hip,center,.3)
 O['LIN_TORSO'].scale.y=.17;O['LIN_TORSO'].scale.z=(center-hip).length*.61
 O['LIN_SHOULDERS'].location=center+V((0,0,.015))
 O['LIN_HEAD'].location=center+V((-.005,.09,.18))
 pose_beam(O['LIN_NECK'],center+V((0,.02,.09)),center+V((0,.07,.14)),.064)
 vals={}
 for side,sh,w,h,upper,fore in [
   ('left',center+V((-.235,0,0)),left_w,'LIN_LEFT_HAND','LIN_L_UPPER','LIN_L_FOREARM'),
   ('right',center+V((.235,0,0)),right_w,'LIN_RIGHT_HAND','LIN_R_UPPER','LIN_R_FOREARM')]:
  e=elbow(sh,w)
  if e is None:raise ValueError('unreachable '+side+str(vv(w)))
  O[h].location=w
  pose_beam(O[upper],sh,e,.066)
  pose_beam(O[fore],e,w,.054)
  vals[side]={'shoulder':vv(sh),'wrist':vv(w),'elbow':vv(e),
              'shoulder_to_wrist_m':round((w-sh).length,5),'reach_le_0p77':(w-sh).length<=.77}
 updated()
 return vals
def overlapping(a,b):
 def mk(ob):
  return BVHTree.FromPolygons(
   [ob.matrix_world@v.co for v in ob.data.vertices],
   [tuple(p.vertices) for p in ob.data.polygons],epsilon=1e-6)
 return bool(mk(O[a]).overlap(mk(O[b])))
def scene_contacts():
 names=['LIN_TORSO','LIN_R_UPPER','LIN_R_FOREARM','LIN_RIGHT_HAND',
        'LIN_L_UPPER','LIN_L_FOREARM','LIN_LEFT_HAND']
 return {n:overlapping(n,'DESK_TOP') for n in names}
def snap(label,owner,folder_state,lin_state=None,notes=None):
 updated()
 return {'label':label,'key':vv(O['KEY_FIXED_RING'].matrix_world.translation),
  'key_all_mesh_origins':{n:vv(O[n].matrix_world.translation) for n in KEY},
  'key_owner':owner,'folder':vv(O['BLUE_FOLDER'].matrix_world.translation),
  'folder_state':folder_state,'lin_left_hand':vv(O['LIN_LEFT_HAND'].matrix_world.translation),
  'lin_right_hand':vv(O['LIN_RIGHT_HAND'].matrix_world.translation),
  'zhou_root':vv(O['ZHOU_ROOT_PATH'].matrix_world.translation),
  'lin_contacts_with_desk':scene_contacts(),'lin_reach':lin_state,'notes':notes}
result={'task':'WAR-90 lightweight continuity V2','method':'Blender CPU, discrete proxy poses; no render/frames/timing proof',
 'source_blend_sha256':EXPECTED,'blender':bpy.app.version_string,'evidence_status':'candidate, not approved',
 'approved_B_modified':False,'baseline_source':{'WAR72_B':'23fc26a252390e73ac50efd16001248ceec362bd0d590f16dbbe8a16385a0373'}}
scene.frame_set(20);updated()
result['first_reveal']={'frame':20,'camera_K':camera_patch(20),'zhou_eyes':eye_report()}
scene.frame_set(40);updated()
result['baseline_covered']={'camera_K':camera_patch(40),'zhou_eyes':eye_report()}
# Independent OBS modification occurs only AFTER folder is fully down.
delta=V((-.2,-.2,0))
for ob in O:
 if ob.name.startswith('LIN_') and ob.type=='MESH':ob.location+=delta
updated()
result['obs']={'change':'Lin proxy body steps (-0.20,-0.20,0.00) m after folder settles',
 'eyes':eye_report(),'camera_K_when_covered':{n:ray(O[n].location,K) for n in CAM},
 'post_step_contacts':scene_contacts()}
assert all(e['folder_visible_of_25']>=8 for e in result['obs']['eyes'])
assert all(e['key_ray_occluder'] is not None for e in result['obs']['eyes'])
# Shot02 -> Shot03: exactly same world snapshot; left folder was released, both right hands empty.
s02=snap('S02-out','table','covering K',
 notes='Zhou sees folder, not K; Lin has stepped back after cover; source pose not physically timed')
s03in=snap('S03-in','table','covering K',
 notes='Identical geometrical state; Zhou question follows; Lin continues existing paper-straightening (not animated)')
# Shot03: left hand re-grasps folder, moves folder off K; no key pickup yet.
P1=V((-.095,-.14,1.29));P2=V((-.075,.18,1.18))
folder_initial=O['BLUE_FOLDER'].location.copy()
# first left hand near actual near edge of folder; then keep same contact offset when moving
grip=V((-.57,.26,.85))
rest_r=V((.15,-.12,.98))
step_grip=pose_lin(P1,grip,rest_r)
folder_move=V((-.30,-.20,.27))
O['BLUE_FOLDER'].location=folder_initial+folder_move
updated()
step_uncover=pose_lin(P1,grip+folder_move,rest_r)
clear_from_cam={n:ray(O[n].location,K) for n in CAM}
assert all(x is None for x in clear_from_cam.values()),clear_from_cam
s03out=snap('S03-out','table','held by Lin left; K uncovered',
  step_uncover,'K unchanged after second reveal; Lin discovers K, responds, then pauses; right hand empty')
s04in=snap('S04-in','table','held by Lin left; K uncovered',
  step_uncover,'Identical world; no extra uncover or dialogue')
# Shot04 right hand goes to stationary K; wrist proxy 45 mm over center.
pickup=V((K.x,K.y,.800))
pickreach=pose_lin(P2,grip+folder_move,pickup)
s04pick=snap('S04-pre-pick','table','held by Lin left; K uncovered',
  pickreach,'No ownership change before right-hand pickup')
# Bounded contact test: wrist bottom close above K top; not articulated finger-grip proof.
key_top=max(box(O[n])[2][1] for n in KEY)
wrist_bottom=box(O['LIN_RIGHT_HAND'])[2][0]
result['pickup_clearance']={'hand_mesh_bottom_minus_key_top_m':round(wrist_bottom-key_top,5),
 'right_forearm_table_surface_intersect':overlapping('LIN_R_FOREARM','DESK_TOP'),
 'right_hand_table_surface_intersect':overlapping('LIN_RIGHT_HAND','DESK_TOP')}
# Transfer is a new proxy state after key has been lifted; advance same three key meshes.
key_orig={n:O[n].location.copy() for n in KEY}
lift=V((0,0,.07))
for n in KEY:O[n].location=key_orig[n]+lift
updated()
s04lift=snap('S04-Lin-right-lift','Lin-right','held by Lin left; K uncovered',
 notes='Same key objects, lifted once; not animated finger grip')
H=V((.75,-.25,1.16))
# Actor wrists are 7 cm apart and touch the same transferred key proxy.
handoff_l=H+V((-.035,0,.015));handoff_z=H+V((.035,0,.015))
handoff_reach=pose_lin(P2,grip+folder_move,handoff_l)
zhou_center=O['ZHOU_SHOULDERS'].matrix_world.translation.copy()
theta=O['ZHOU_ROOT_PATH'].rotation_euler.z
zhou_right_shoulder=zhou_center+V((.20*math.cos(theta),.20*math.sin(theta),0))
zh_dist=(handoff_z-zhou_right_shoulder).length
z_elbow=elbow(zhou_right_shoulder,handoff_z)
# Move actual same key objects to handover point, not duplicate.
key_translation=H-K
for n in KEY:O[n].location=key_orig[n]+key_translation
updated()
s04shared=snap('S04-one-shared-contact','Lin-right + Zhou-right','held by Lin left; K uncovered',
 handoff_reach,'Zhou proxy right wrist computed analytically; source has no Zhou arm rig')
assert z_elbow is not None and zh_dist<=.77
release_reach=pose_lin(P2,grip+folder_move,V((.25,-.15,1.07)))
s04end=snap('S04-Zhou-right','Zhou-right','held by Lin left; K uncovered',
 release_reach,'Lin RIGHT hand retracts after one release; key remains near Zhou RIGHT; exit not animated')
# Exactly match required cut boundaries in world state.
def comparable(x):
 return {k:x[k] for k in ('key','key_all_mesh_origins','key_owner','folder','folder_state',
   'lin_left_hand','lin_right_hand','zhou_root')}
result['joins']={'S02_S03_geometry_equal':comparable(s02)==comparable(s03in),
 'S03_S04_geometry_equal':comparable(s03out)==comparable(s04in)}
result['stages']=[s02,s03in,s03out,s04in,s04pick,s04lift,s04shared,s04end]
result['reach']={'post_cover_grip':step_grip,'after_uncover':step_uncover,
 'Lin_pickup':pickreach,'handoff_Lin':handoff_reach,'after_Lin_release':release_reach,
 'Zhou_right_shoulder_proxy':vv(zhou_right_shoulder),
 'Zhou_right_wrist_proxy':vv(handoff_z),'Zhou_right_elbow_proxy':vv(z_elbow),
 'Zhou_shoulderto_wrist_m':round(zh_dist,5),'Zhou_reach_le_0p77':zh_dist<=.77,
 'handoff_key_xyz':vv(H),'two_wrist_distance_m':round((handoff_l-handoff_z).length,5)}
result['single_transfer']={'key_mesh_count':len(KEY),'owners_sequence':[
 'table','table','table','Lin-right','Lin-right+Zhou-right','Zhou-right'],
 'completed_world_ownership_transfers':1,'key_K_until_pickup':True,
 'semantic_assertion_only_not_animated_grip':True}
result['key_reveal_after_uncover_camera_blockers']=clear_from_cam
result['open_risks']=[
 'Source scene lacks Zhou arms/rig: Zhou wrist/shoulder/elbow are bounded analytical proxy, not mesh collision proof.',
 'Lin rebuilt 2-segment arm elbow/forearm poses are a first geometry candidate, not real human joint constraints.',
 'Folder is moved as one rigid object: folder-left-hand grip and continuous support/hand pose are not demonstrated.',
 'Discrete world snapshots do not prove natural 35-40 second performance, intermediate sweeps, hand contact, exact four-shot framing or real audience recognition.',
 'Lin torso proxy step and later forward lean need continuous pose/mesh collision validation before claiming full action.',
 'This reuses old WAR72 frozen mesh and WAR91 cameras, not a complete reauthored four-shot scene.']
assert result['joins']['S02_S03_geometry_equal'] and result['joins']['S03_S04_geometry_equal']
assert result['single_transfer']['key_mesh_count']==3
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V2_OBS',result['obs']['eyes'])
print('V2_PICKUP',result['pickup_clearance'])
print('V2_REACH',result['reach']['Lin_pickup']['right'],result['reach']['handoff_Lin']['right'],zh_dist)
print('V2_JOINS',result['joins'])
print('V2_OK',out)

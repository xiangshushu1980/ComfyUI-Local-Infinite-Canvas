"""WAR-91 V1: only CPU Blender, only derived scene and evidence.
Original: WAR-72 round4 candidate B; user-approved WAR-90 Shot Plan remains immutable.
Run from WSL via Windows Blender 5.2.3 --background --threads 2 --python run-v1.py
-- <source_blend_windows_path> <output_windows_dir>
"""
import bpy, sys, json, csv, math, hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index('--')+1:]
assert len(args)==2, args
SOURCE,OUT=Path(args[0]),Path(args[1])
assert SOURCE.is_file() and 'WAR-72' in str(SOURCE), str(SOURCE)
OUT.mkdir(parents=True,exist_ok=True)
assert 'WAR-91' in str(OUT), str(OUT)
source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert source_sha=='23fc26a252390e73ac50efd16001248ceec362bd0d590f16dbbe8a16385a0373'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.device='CPU'
sc.cycles.samples=3
sc.render.threads_mode='FIXED'
sc.render.threads=2
sc.render.resolution_x=960
sc.render.resolution_y=540
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.film_transparent=False
O=bpy.data.objects
KEY_NAMES=('KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH')
K=Vector((-.25,.45,.755))
Z_START=Vector((2.,-1.30,0))
Z_END=Vector((1.10,-.52,0))
LIN_FOOT=Vector((.42,-.28,0))
def frame(f):
    sc.frame_set(f)
    bpy.context.view_layer.update()
def vv(p):
    return [round(float(x),5) for x in p]
def bounds(o):
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)]
def bound_dict(o):
    return [[round(q,5) for q in v] for v in bounds(o)]
def project(cam,p):
    x=world_to_camera_view(sc,cam,Vector(p))
    return [float(x.x),float(x.y),float(x.z)]
def in_image(p):
    return 0 <= p[0] <= 1 and 0 <= p[1] <= 1 and p[2] > 0
def key_bbox(cam):
    pts=[project(cam,o.matrix_world@v.co) for n in KEY_NAMES for o in [O[n]] for v in o.data.vertices]
    return {'width_px':round((max(x[0] for x in pts)-min(x[0] for x in pts))*960,2),
            'height_px':round((max(x[1] for x in pts)-min(x[1] for x in pts))*540,2),
            'fully_in_frame':all(in_image(x) for x in pts)}
SKIP={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST'}
BLOCKERS=[o for o in O if o.type=='MESH' and o.name not in SKIP.union(KEY_NAMES)]
def ray(a,b,skip_zhou=False):
    a,b=Vector(a),Vector(b)
    winner=(math.inf,None)
    for o in BLOCKERS:
        if skip_zhou and o.name.startswith('ZHOU_'):
            continue
        inv=o.matrix_world.inverted()
        p=inv@a
        q=inv@b
        diff=q-p
        if diff.length<1e-7:continue
        hit,hitpoint,_,_=o.ray_cast(p,diff.normalized(),distance=diff.length*.995)
        if hit:
            fraction=(hitpoint-p).length/diff.length
            if fraction<winner[0]:
                winner=(fraction,o.name)
    return {'blocked':winner[1] is not None, 'blocker':winner[1],
            'distance_m':round((b-a).length*winner[0],5) if winner[1] else None}
def camera(name,location,target,lens=40):
    data=bpy.data.cameras.new(name)
    o=bpy.data.objects.new(name,data)
    sc.collection.objects.link(o)
    o.location=location
    o.data.lens=lens
    o.data.sensor_width=36
    o.data.sensor_fit='HORIZONTAL'
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    return o
def key_patch():
    return [Vector((x,y,K.z)) for x in (-.28,-.23,-.17) for y in (.43,.45,.47)]
def overlap_length(a,b):
    return max(0.,min(a[1],b[1])-max(a[0],b[0]))
def contact():
    folder=bounds(O['BLUE_FOLDER'])
    stack=bounds(O['STACK_03'])
    key_bounds={i:(min(bounds(O[n])[i][0] for n in KEY_NAMES),
                   max(bounds(O[n])[i][1] for n in KEY_NAMES)) for i in range(3)}
    xy=overlap_length(folder[0],stack[0])*overlap_length(folder[1],stack[1])
    over_k=overlap_length(folder[0],key_bounds[0])*overlap_length(folder[1],key_bounds[1])
    bvh=lambda n:BVHTree.FromPolygons(
        [O[n].matrix_world@v.co for v in O[n].data.vertices],
        [tuple(poly.vertices) for poly in O[n].data.polygons],epsilon=1e-6)
    collisions={}
    for n in KEY_NAMES:
        collisions[n]=len(bvh('BLUE_FOLDER').overlap(bvh(n)))
    return {
      'folder_bounds':bound_dict(O['BLUE_FOLDER']),
      'stack_top_bounds':bound_dict(O['STACK_03']),
      'key_ring_bounds':bound_dict(O['KEY_FIXED_RING']),
      'folder_stack_xy_overlap_area_m2':round(xy,7),
      'folder_stack_z_gap_m':round(folder[2][0]-stack[2][1],6),
      'folder_key_xy_overlap_area_m2':round(over_k,7),
      'folder_bottom_minus_key_top_m':round(folder[2][0]-key_bounds[2][1],6),
      'folder_key_surface_intersections':collisions,
      'limits':'AABB+surface overlap only: no rigid-body friction or dynamic gravity proof.'
    }
frame(20)
face=O['LIN_HEAD'].matrix_world.translation.copy()
left=O['LIN_LEFT_HAND'].matrix_world.translation.copy()
CAMERAS=[
 ('ACTION40',camera('WAR91_Action40',(-1.6,-1.6,1.55),K*.53+face*.47)),
 ('DESK40',camera('WAR91_Desk40',(-1.15,-1.10,1.34),K*.75+left*.25)),
]
caminfo=[]
for cid,cam in CAMERAS:
    caminfo.append({'id':cid,'xyz':vv(cam.location),
                    'rotation_euler':vv(cam.rotation_euler),'lens_mm':cam.data.lens,
                    'sensor_width_mm':cam.data.sensor_width})
frameids=(1,8,20,30,34,40)
rows=[]
for cid,cam in CAMERAS:
    for f in frameids:
        frame(f)
        rays=[ray(cam.location,p) for p in key_patch()]
        ctr=ray(cam.location,K)
        p={'camera':cid,'frame':f,'key_projected':key_bbox(cam),
           'key_sample_clear_9':sum(not r['blocked'] for r in rays),
           'key_sample_blocker_counts':dict(Counter(r['blocker'] or 'CLEAR' for r in rays)),
           'center_ray':ctr,'folder_bounds':bound_dict(O['BLUE_FOLDER']),
           'moving_paper_bounds':bound_dict(O['PAPER_MOVING']),
           'left_hand_location':vv(O['LIN_LEFT_HAND'].matrix_world.translation),
           'right_hand_location':vv(O['LIN_RIGHT_HAND'].matrix_world.translation),
           'lin_face_in_frame':in_image(project(cam,O['LIN_HEAD'].matrix_world.translation)),
           'lin_left_hand_in_frame':in_image(project(cam,O['LIN_LEFT_HAND'].matrix_world.translation)),
           'zhou_face_in_frame':in_image(project(cam,O['ZHOU_HEAD'].matrix_world.translation)),
           'axis_start_end_sign':[]}
        for end in [Z_START,Z_END]:
            a=(end.x-LIN_FOOT.x,end.y-LIN_FOOT.y)
            b=(cam.location.x-LIN_FOOT.x,cam.location.y-LIN_FOOT.y)
            p['axis_start_end_sign'].append(round(a[0]*b[1]-a[1]*b[0],5))
        rows.append(p)
        print('SHOT02',cid,'f',f,'px',p['key_projected']['width_px'],
              p['key_projected']['height_px'],'clear9',p['key_sample_clear_9'],
              'blockers',p['key_sample_blocker_counts'],flush=True)
# Source model has a real initial/reveal/cover sequence, not the new Script's 4-shot cut points.
frame(40)
prop=contact()
print('PROP_CONTACT',json.dumps(prop,ensure_ascii=False),flush=True)
# G2: old proxy Zhou root path, 21 samples. Positions/eyes and the camera are from same
# source, but camera positions are new. No eye direction/attention is modeled.
path=[]
root=O['ZHOU_ROOT_PATH']
for f in [20,40]:
    frame(f)
    for i in range(21):
        frac=i/20.
        root.location=Z_START*(1-frac)+Z_END*frac
        bpy.context.view_layer.update()
        eyes=[]
        for n in ['ZHOU_LEFT_EYE','ZHOU_RIGHT_EYE']:
            pos=O[n].matrix_world.translation.copy()
            k=ray(pos,K,skip_zhou=True)
            fold=ray(pos,O['BLUE_FOLDER'].matrix_world.translation.copy(),skip_zhou=True)
            eyes.append({'eye':n,'at':vv(pos),'key_raycast':k,'folder_center_raycast':fold,
                         'key_occluded_by_lin':bool(k['blocker'] and k['blocker'].startswith('LIN_') and k['distance_m']>.16)})
        path.append({'frame':f,'sample':i,'ratio':frac,
                     'zhou_root':vv(root.location),'eyes':eyes,
                     'both_key_blocked_by_lin':all(e['key_occluded_by_lin'] for e in eyes),
                     'both_folder_center_line_clear_of_lin':all(not (e['folder_center_raycast']['blocker'] or '').startswith('LIN_') for e in eyes),
                     'camera_K_center':{cid:ray(cam.location,K) for cid,cam in CAMERAS}})
    print('PATH_EYES',f,'LinOcclusion',sum(p['both_key_blocked_by_lin'] for p in path if p['frame']==f),
          '/21',flush=True)
# Verify world coordinate K remains fixed, previous scene unchanged. We don't animate key transfer.
frame(40)
root.location=Z_END
bpy.context.view_layer.update()
k_actual={n:vv(O[n].matrix_world.translation) for n in KEY_NAMES}
shoulders=O['LIN_SHOULDERS'].matrix_world.translation
right_shoulder=Vector((.340,.060,1.290))  # round4 explicit derived right-arm anchor
left_shoulder=Vector((-.130,.060,1.290))
right_pickup=(right_shoulder-K).length
left_pickup=(left_shoulder-K).length
# Candidate handoff point only: no accurate right-hand rig or grip, not a collision pass.
handoff_point=Vector((.75,-.10,1.09))
zhou_shoulder=O['ZHOU_SHOULDERS'].matrix_world.translation
handoff={
  'source_reach_model_arm_segment_m':[.385,.385],
  'old_lin_right_shoulder_m':vv(right_shoulder),
  'old_lin_left_shoulder_m':vv(left_shoulder),
  'key_m':vv(K),
  'old_lin_right_shoulder_to_K_m':round(right_pickup,5),
  'old_lin_left_shoulder_to_K_m':round(left_pickup,5),
  'old_lin_right_shoulder_can_reach_K_static':right_pickup<=.77,
  'old_lin_left_shoulder_can_reach_K_static':left_pickup<=.77,
  'candidate_handoff_point_m':vv(handoff_point),
  'right_shoulder_to_candidate_handoff_m':round((right_shoulder-handoff_point).length,5),
  'zhou_shoulder_proxy_m':vv(zhou_shoulder),
  'zhou_shoulder_center_to_handoff_m':round((zhou_shoulder-handoff_point).length,5),
  'owner_states':['table(K)','Lin-right-picking','Lin-right-and-Zhou-right-overlap','Zhou-right-held'],
  'owner_transfer_count':1,
  'actual_3d_right_hand_pickup_and_finger_contact':'NOT_TESTED: source has right hand braced on desk, no posed right-hand-to-K or Zhou right hand grip',
  'implication':'If static source right shoulder to K >0.77m, requires derived Lin torso/stance or acquisition path change; NOT proof script impossible.'
}
# C1: only existing left-hand animation up to old frame 40; after release to question
# and re-grasp is new script content, not in WAR-72 model.
joint={
  'shot01_to_02':'derived baseline f1/f8/f20 contains paper movement; not an actual four-shot cut render',
  'shot02_to_03':'source f40 covers K, left hand near folder; NO AFTER-f40 question/return/re-grasp keys; new freeze requested stop action lacks modeled referent',
  'shot03_to_04':'source has NO uncover-and-right-hand-to-Zhou pickup/grip, only static reach estimate',
  'status':'UNTESTED performance/cut continuity; old discrete geometry cannot substitute.'
}
output={'task':'WAR-91 V1 narrow Blender CPU proxy','date':'2026-11-15',
 'source_blend':str(SOURCE),'source_sha256':source_sha,
 'baseline_B_run':'d23b8bdab90f43ef8ff0098fb8021f78',
 'blender_version':bpy.app.version_string,
 'device':sc.cycles.device,'engine':sc.render.engine,'threads':2,'samples':3,
 'resolution':[960,540],
 'old_round4_model_reused_unmodified_on_disk':True,
 'candidate_cameras':caminfo,'frames':list(frameids),'K':vv(K),
 'key_model_locations_at_finish':k_actual,
 'shot02_rows':rows,'folder_support_contact':prop,
 'zhou_path_eye_samples':path,'continuity_C1':joint,'handoff_C2':handoff,
 'limitations':[
   'This is a derived test of a prior DirectorSKILL proxy, not new WAR-90 geometry authored to spec.',
   'The prior model has right forearm/table penetration; do not call its actor motion physical.',
   'Ray to K distinguishes physical line-of-sight, not character gaze, attention, knowledge or audience recognition.',
   'Camera projection bbox dimensions and key patch visibility are not a viewer recognition score.',
   'Two scene cameras were hypotheses from WAR-72 F1/F2, not required lens numbers from approved WAR-90.',
   'Key pickup, right-hand grip and after-f40 move were not animated; only reach/missing coverage audited.',
   'No rigid-body friction, natural movement, full 35-40s cut timing, true POV attribution, H3 or GPU.'
 ]}
(OUT/'results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'shot02-metrics.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f)
    w.writerow(['camera','frame','key_width_px','key_height_px','clear_9','blocked_names','lin_face_in','zhou_face_in','hand_in'])
    for x in rows:
        w.writerow([x['camera'],x['frame'],x['key_projected']['width_px'],
         x['key_projected']['height_px'],x['key_sample_clear_9'],
         str(x['key_sample_blocker_counts']),x['lin_face_in_frame'],
         x['zhou_face_in_frame'],x['lin_left_hand_in_frame']])
# Save derived .blend but exclude media and .blend from Git. Never write to source.
frame(20)
root.location=Z_START*.45+Z_END*.55
sc.camera=CAMERAS[0][1]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAR91_derived_cameras.blend'))
for cid,cam in CAMERAS:
    for f in [1,20,34,40]:
        frame(f)
        root.location=Z_START*.45+Z_END*.55
        bpy.context.view_layer.update()
        sc.camera=cam
        sc.render.filepath=str(OUT/(cid+'_f'+str(f).zfill(2)+'.png'))
        bpy.ops.render.render(write_still=True)
        print('RENDER',cid,f,flush=True)
print('WAR91_V1_DONE',flush=True)

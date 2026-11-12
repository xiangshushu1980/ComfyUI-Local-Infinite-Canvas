"""WAR-72 round5 Shot02 information coverage test (Blender CPU only).
Read-only source round4/candidate-b; all cameras derived, frozen Shot Plan unchanged.
F0 inherited 40mm MS; F1 closer 40mm action+K; F2 tighter 40mm desk; F3 85mm insert diagnostic.
"""
from pathlib import Path
import bpy,json,math,hashlib,csv
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
SRC=P.parent/'round4/candidate-b/WAR72_physical_B.blend'
assert SRC.is_file()
OUT=P/'evidence';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC))
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=7
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
OBJ=bpy.data.objects
K=Vector((-.25,.45,.755))
def frame(f):
 sc.frame_set(f);bpy.context.view_layer.update()
def uv(cam,p):
 x=world_to_camera_view(sc,cam,Vector(p));return [float(x.x),float(x.y),float(x.z)]
def inside(pt):
 return 0<=pt[0]<=1 and 0<=pt[1]<=1 and pt[2]>0
def bbox(cam,obs):
 points=[]
 for o in obs:
  for v in o.data.vertices:
   points.append(uv(cam,o.matrix_world @ v.co))
 return {'x_min':round(min(p[0] for p in points),5),
         'x_max':round(max(p[0] for p in points),5),
         'y_min':round(min(p[1] for p in points),5),
         'y_max':round(max(p[1] for p in points),5),
         'width_px':round((max(p[0] for p in points)-min(p[0] for p in points))*960,2),
         'height_px':round((max(p[1] for p in points)-min(p[1] for p in points))*540,2),
         'in_bounds': all(inside(p) for p in points)}
ign={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST'}
keynames={'KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH'}
blockers=[o for o in OBJ if o.type=='MESH' and o.name not in keynames|ign]
def ray(origin,target):
 a,b=Vector(origin),Vector(target)
 best=(1.0,None)
 for o in blockers:
  inv=o.matrix_world.inverted();x,y=inv@a,inv@b;v=y-x
  if v.length<1e-6: continue
  hit,p,n,k=o.ray_cast(x,v.normalized(),distance=v.length*.995)
  if hit:
   t=(p-x).length/v.length
   if t<best[0]:best=(t,o.name)
 return {'blocked':bool(best[1]),'name':best[1],'fraction':round(best[0],5)}
def make_camera(name,xyz,target,lens):
 info=bpy.data.cameras.new(name);c=bpy.data.objects.new(name,info)
 sc.collection.objects.link(c)
 c.location=xyz;c.data.lens=lens;c.data.sensor_width=36
 c.data.sensor_fit='HORIZONTAL'
 c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update()
 return c
frame(20)
lin_face=OBJ['LIN_HEAD'].matrix_world.translation.copy()
lh=OBJ['LIN_LEFT_HAND'].matrix_world.translation.copy()
orig=OBJ['SHOT02_40MM']
s0=orig
s1=make_camera('F1_40mm_ACTION',(-1.6,-1.6,1.55),K*.53+lin_face*.47,40)
s2=make_camera('F2_40mm_DESK',(-1.15,-1.10,1.34),K*.75+lh*.25,40)
s3=OBJ['SHOT03_85MM']
candidates=[
 {'id':'F0','name':'Frozen-style derived 40mm MS inherited fourth-round framing','cam':s0,
  'story_function':'single 40mm MS, actor+table+approaching Zhou'},
 {'id':'F1','name':'Closer 40mm action-and-reveal single shot','cam':s1,
  'story_function':'more prop size but may crop face or Zhou'},
 {'id':'F2','name':'40mm prop-priority tighter desk framing','cam':s2,
  'story_function':'key/hand readability at expense of character relation'},
 {'id':'F3','name':'85mm key ECU spatial insert reference; adds shot','cam':s3,
  'story_function':'stronger key disclosure but would add another shot/cut'}]
rows=[]
meshkey=[OBJ[n] for n in sorted(keynames)]
patch=[Vector((x,y,K.z)) for x in (-.28,-.23,-.17) for y in (.43,.45,.47)]
# fixed camera cone and in-frame geometry at three selected temporal key states.
for entry in candidates:
 cid,cam=entry['id'],entry['cam']
 # static recording of the exact derived parameters
 desc={'id':cid,'label':entry['name'],'story_function':entry['story_function'],
       'position':[round(float(q),5) for q in cam.location],
       'quaternion':[round(float(q),6) for q in cam.rotation_euler.to_quaternion()],
       'lens_mm':float(cam.data.lens),'sensor_width_mm':float(cam.data.sensor_width),
       'sensor_fit':cam.data.sensor_fit}
 entry['meta']=desc
 for f in (1,10,20):
  frame(f)
  center=uv(cam,K);face=uv(cam,OBJ['LIN_HEAD'].matrix_world.translation)
  actor=uv(cam,OBJ['LIN_TORSO'].matrix_world.translation)
  hand=uv(cam,OBJ['LIN_LEFT_HAND'].matrix_world.translation)
  paper=uv(cam,OBJ['PAPER_MOVING'].matrix_world.translation)
  zhou=uv(cam,OBJ['ZHOU_HEAD'].matrix_world.translation)
  samples=[ray(cam.location,p) for p in patch]
  keybbox=bbox(cam,meshkey)
  # continuity axis sampled at beginning and final endpoints
  axis=[]
  for world in [(2.0,-1.30),(1.10,-.52)]:
   lin=(.42,-.28);a=(world[0]-lin[0],world[1]-lin[1]);b=(cam.location.x-lin[0],cam.location.y-lin[1])
   axis.append(round(a[0]*b[1]-a[1]*b[0],5))
  data={'id':cid,'frame':f,'K_center_norm':[round(v,4) for v in center],
   'K_bbox':keybbox,'K_patch_rays':samples,'K_patch_clear':sum(not x['blocked'] for x in samples),
   'K_center_ray':ray(cam.location,K),'LinFace_uv':[round(v,4) for v in face],
   'LinTorso_uv':[round(v,4) for v in actor],
   'LinHand_uv':[round(v,4) for v in hand],
   'ZhouHead_uv':[round(v,4) for v in zhou],
   'Paper_uv':[round(v,4) for v in paper],
   'LinFace_in_frame':inside(face),
   'LinHand_in_frame':inside(hand),
   'ZhouHead_in_frame':inside(zhou),
   'K_in_frame':keybbox['in_bounds'],
   'actor_axis_cross_start_end':axis,
   'crosses_actor_axis':axis[0]*axis[1]<0}
  rows.append(data)
  print('MEASURE',cid,f,'Kpx',keybbox['width_px'],keybbox['height_px'],'Kclear',data['K_patch_clear'],
        'head',data['LinFace_in_frame'],'hand',data['LinHand_in_frame'],
        'zhou',data['ZhouHead_in_frame'],'ray',data['K_center_ray'],flush=True)

payload={'date':'2026-11-12','task':'WAR-72 round5 Shot02 cinematic information coverage',
  'source_scene':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
  'frozen_shotplan':'WAR-65/d-assisted-v1-step7-raw.md; Shot02 40mm MS fixed, 6s; NOT modified',
  'scene_unchanged':True,'engine':sc.render.engine,'cycles_device':sc.cycles.device,
  'frame_resolution':[960,540],'samples':7,'candidates':[x['meta'] for x in candidates],
  'measurements':rows,
  'interpretation_limits':[
   'This is static low-poly geometry with known forearm/desk intersection in source.',
   'Projected key pixels and clear rays are NOT human recognition measurements.',
   'Single frame cannot prove timing or performance in the six-second beat.',
   'F3 is a diagnostic extra-shot hypothesis, not part of the frozen eight-shot plan.',
   'S1/S2 are derived alternative camera placements, not modifications to original Skill/Shot Plan.',
   'Two camera projections can share axis side and still cut awkwardly due to scale or direction.']}
(OUT/'comparisons.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
with (OUT/'metrics.csv').open('w',encoding='utf8',newline='') as f:
 writer=csv.writer(f)
 writer.writerow(['candidate','frame','lens_mm','key_width_px','key_height_px','clear_key_9','key_center_ray_blocked','lin_face_in','hand_in','zhou_face_in','key_bbox_in'])
 for c in candidates:
  for p in [r for r in rows if r['id']==c['id']]:
   writer.writerow([c['id'],p['frame'],c['meta']['lens_mm'],p['K_bbox']['width_px'],
    p['K_bbox']['height_px'],p['K_patch_clear'],p['K_center_ray']['blocked'],
    p['LinFace_in_frame'],p['LinHand_in_frame'],p['ZhouHead_in_frame'],p['K_in_frame']])
# Record a reusable camera-scene snapshot, not a revision of the frozen .blend.
frame(20);sc.camera=s0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAR72_shot02_coverage.blend'))
for c in candidates:
 cam=c['cam'];id=c['id']
 selected=[1,10,20] if id in ('F0','F1','F2') else [20]
 for f in selected:
  frame(f);sc.camera=cam;sc.render.filepath=str(OUT/f'{id}_f{f:02d}.png')
  bpy.ops.render.render(write_still=True)
  print('RENDER',id,f,flush=True)
print('DONE_ROUND5',flush=True)

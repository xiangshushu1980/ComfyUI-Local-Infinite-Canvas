"""WAR-91 isolated follow-up audit: exact paper support and physically visible folder edges.
No render; reads original round4 B source and does not modify prior V1 evidence.
"""
import bpy,sys,hashlib,json,math
from pathlib import Path
from mathutils import Vector
src,out=[Path(s) for s in sys.argv[sys.argv.index('--')+1:]]
assert src.is_file() and hashlib.sha256(src.read_bytes()).hexdigest()=='23fc26a252390e73ac50efd16001248ceec362bd0d590f16dbbe8a16385a0373'
assert 'WAR-91' in str(out)
bpy.ops.wm.open_mainfile(filepath=str(src))
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.device='CPU'
O=bpy.data.objects;V=Vector
K=V((-.25,.45,.755));Z0=V((2.,-1.3,0));Z1=V((1.10,-.52,0))
IGNORE={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST','KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH'}
blocks=[o for o in O if o.type=='MESH' and o.name not in IGNORE]
def frame(f):
 sc.frame_set(f);bpy.context.view_layer.update()
def box(o):
 p=[o.matrix_world@V(q) for q in o.bound_box]
 return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
def ray(a,b,skip_zhou=True):
 a,b=V(a),V(b);best=(float('inf'),None)
 for o in blocks:
  if skip_zhou and o.name.startswith('ZHOU_'):continue
  inv=o.matrix_world.inverted();aa=inv@a;bb=inv@b;v=bb-aa
  if v.length<1e-8:continue
  hit,p,_,_=o.ray_cast(aa,v.normalized(),distance=v.length*.997)
  if hit:
   r=(p-aa).length/v.length
   if r<best[0]:best=r,o.name
 return {'first_mesh':best[1],'fraction':round(best[0],5) if best[1] else None}
def xy_overlap(A,B):
 return max(0,min(A[0][1],B[0][1])-max(A[0][0],B[0][0]))*max(0,min(A[1][1],B[1][1])-max(A[1][0],B[1][0]))
frame(40)
f=box(O['BLUE_FOLDER']);p=box(O['PAPER_MOVING']);s=box(O['STACK_03'])
supports={
 'folder':f,'moved_paper_top_page':p,'underlying_stack_top':s,
 'folder_bottom_minus_moved_paper_top_m':round(f[2][0]-p[2][1],6),
 'folder_bottom_minus_underlying_stack_top_m':round(f[2][0]-s[2][1],6),
 'folder_moved_paper_overlap_xy_m2':round(xy_overlap(f,p),6),
 'folder_underlying_stack_overlap_xy_m2':round(xy_overlap(f,s),6),
 'interpretation':'The moved paper is the top member of the pile, not the lower STACK_03 sheet; pair folder to actual PAPER_MOVING top at final pose.'
}
# f40 folder world bounds intersect key XY. Sample 5x5 on physically present top face of folder;
# ray to positions 1mm above top surface, require ray hit not LIN. Positive line-of-sight is
# geometric only; Zhou ability to NOTICE any given region is separately unknown.
spots=[]
for i in range(5):
 for j in range(5):
  x=f[0][0]+(i+.5)/5*(f[0][1]-f[0][0])
  y=f[1][0]+(j+.5)/5*(f[1][1]-f[1][0])
  spots.append(V((x,y,f[2][1]+.001)))
folder_visibility=[]
root=O['ZHOU_ROOT_PATH']
for u in [0,.25,.5,.75,1.]:
 root.location=Z0*(1-u)+Z1*u;bpy.context.view_layer.update()
 pair=[]
 for eye in ['ZHOU_LEFT_EYE','ZHOU_RIGHT_EYE']:
  origin=O[eye].matrix_world.translation.copy()
  outcomes=[ray(origin,q) for q in spots]
  clear=[(k,r) for k,r in enumerate(outcomes) if not r['first_mesh'] or r['first_mesh']=='BLUE_FOLDER']
  blocked_by_lin=[(k,r) for k,r in enumerate(outcomes) if (r['first_mesh'] or '').startswith('LIN_')]
  pair.append({'eye':eye,'clear_or_folder_visible_of_25':len(clear),
   'lin_blocks_of_25':len(blocked_by_lin),
   'clear_spot_indices':[k for k,_ in clear],
   'counts':{n:sum(r['first_mesh']==n for r in outcomes) for n in sorted(set(r['first_mesh'] for r in outcomes),key=str)}})
 folder_visibility.append({'path_ratio':u,'eyes':pair})
# Visibility of exact covered K location on folder surface is not same as visibility of any folder corner.
pts=[V((-.25,.45,f[2][1]+.001)),V((-.2,.45,f[2][1]+.001)),V((-.55,.55,f[2][1]+.001))]
center_cover={}
root.location=Z1;bpy.context.view_layer.update()
for eye in ['ZHOU_LEFT_EYE','ZHOU_RIGHT_EYE']:
 center_cover[eye]=[ray(O[eye].matrix_world.translation,p) for p in pts]
# Original scene: prior folder drop keyframe f34 to f40; sample transition, not just endpoints.
cam0=O['SHOT02_40MM']
samples=[V((x,y,K.z)) for x in (-.28,-.23,-.17) for y in (.43,.45,.47)]
transition=[]
for fnum in range(34,41):
 frame(fnum)
 dd=[ray(cam0.location,q) for q in samples]
 transition.append({'frame':fnum,'legacy_cam_clear_K_9':sum(not x['first_mesh'] for x in dd),
  'legacy_occluders':{n:sum(x['first_mesh']==n for x in dd) for n in sorted(set(x['first_mesh'] for x in dd),key=str)},
  'folder_bottom_z':round(box(O['BLUE_FOLDER'])[2][0],5)})
res={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'source_frame':40,'support_correction':supports,'folder_visibility_25_spots_5_path':folder_visibility,
 'final_covered_location_from_Zhou_both_eyes':center_cover,
 'legacy_camera_final_cover_transition':transition,
 'limits':['Folder ray first hit includes folder geometry and other meshes, not human gaze or ability to identify contents.',
 'Pixel visibility and hand/key ownership are not assessed in this follow-up.',
 'The source is frozen older proxy; new B approved staging may need a new pose, not automatic failure.']}
out.write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('SUPPORT',json.dumps(supports))
print('FOLDER_VISIBILITY',[(r['path_ratio'],[(e['clear_or_folder_visible_of_25'],e['lin_blocks_of_25']) for e in r['eyes']]) for r in folder_visibility])
print('K_COVER_ZHOU',center_cover)
print('TRANSITION',transition)
print('AUDIT_DONE')

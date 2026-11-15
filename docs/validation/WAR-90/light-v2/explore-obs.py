"""Light V2 OBS parameter scan. Blender CPU geometry only; source immutable."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector as V
s,o=[Path(x) for x in sys.argv[sys.argv.index('--')+1:]]
assert hashlib.sha256(s.read_bytes()).hexdigest()=='23fc26a252390e73ac50efd16001248ceec362bd0d590f16dbbe8a16385a0373'
bpy.ops.wm.open_mainfile(filepath=str(s))
scene=bpy.context.scene;O=bpy.data.objects
scene.frame_set(40);bpy.context.view_layer.update()
ignore={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST','KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH'}
block=[a for a in O if a.type=='MESH' and a.name not in ignore]
moving=[a for a in O if a.type=='MESH' and a.name.startswith('LIN_') and 'LEG' not in a.name]
orig={a.name:a.location.copy() for a in moving}
corners=[O['BLUE_FOLDER'].matrix_world@V(p) for p in O['BLUE_FOLDER'].bound_box]
lo=[min(p[i] for p in corners) for i in range(3)];hi=[max(p[i] for p in corners) for i in range(3)]
patch=[V((lo[0]+(i+.5)/5*(hi[0]-lo[0]),lo[1]+(j+.5)/5*(hi[1]-lo[1]),hi[2]+.002)) for i in range(5) for j in range(5)]
cover=V((-.25,.45,hi[2]+.002))
def first(a,b):
 a,b=V(a),V(b);best=(1.,None)
 for ob in block:
  if ob.name.startswith('ZHOU_'):continue
  t=ob.matrix_world.inverted();x,y=t@a,t@b;dif=y-x
  if dif.length<1e-7:continue
  hit,p,_,_=ob.ray_cast(x,dif.normalized(),distance=dif.length*.997)
  if hit:
   frac=(p-x).length/dif.length
   if frac<best[0]:best=(frac,ob.name)
 return best[1]
def measure():
 ret=[]
 for n in ('ZHOU_LEFT_EYE','ZHOU_RIGHT_EYE'):
  eye=O[n].matrix_world.translation.copy();hits=[first(eye,p) for p in patch]
  ret.append({'eye':n,'clear_or_folder':sum(x in (None,'BLUE_FOLDER') for x in hits),
    'lin_blocked':sum(bool(x and x.startswith('LIN_')) for x in hits),
    'covered_location_blocker':first(eye,cover)})
 return ret
baseline=measure();rs=[]
for i in range(-10,11,2):
 for j in range(-8,9,2):
  dx,dy=i/20,j/20
  for a in moving:a.location=orig[a.name]+V((dx,dy,0))
  bpy.context.view_layer.update()
  pair=measure();minimum=min(x['clear_or_folder'] for x in pair)
  if minimum>=3:
   rs.append({'dx':dx,'dy':dy,'displacement_m':round(math.hypot(dx,dy),4),
    'minimum_visible':minimum,'eyes':pair})
for a in moving:a.location=orig[a.name]
bpy.context.view_layer.update()
rs.sort(key=lambda x:(x['displacement_m'],-x['minimum_visible']))
out={'source_sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'frame':40,
 'moving_meshes':[a.name for a in moving],'folder_bounds':[lo,hi],
 'baseline':baseline,'matching_candidates':rs[:60],
 'limit':'Exploratory upper-mesh translation on legacy proxy; no rig or continuous physical motion proof.'}
o.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('OBS_BASELINE',baseline)
print('OBS_TOP',[(x['dx'],x['dy'],x['minimum_visible'],[e['covered_location_blocker'] for e in x['eyes']]) for x in rs[:20]])
print('OBS_TOTAL',len(rs))

# Alternative: change Zhou's terminal step instead of Lin's torso.
root=O['ZHOU_ROOT_PATH'];z_orig=root.location.copy()
zrs=[]
for i in range(-12,13,2):
 for j in range(-12,11,2):
  dx,dy=i/20,j/20
  root.location=z_orig+V((dx,dy,0));bpy.context.view_layer.update()
  pair=measure();minimum=min(x['clear_or_folder'] for x in pair)
  if minimum>=9 and all(x['covered_location_blocker'] in (None,'BLUE_FOLDER') for x in pair):
   zrs.append({'dx':dx,'dy':dy,'moved_xy':[float(root.location.x),float(root.location.y)],
    'distance_m':round(math.hypot(dx,dy),4),'minimum_visible':minimum,'eyes':pair})
root.location=z_orig;bpy.context.view_layer.update()
zrs.sort(key=lambda x:(x['distance_m'],-x['minimum_visible']))
out['zhou_alternative_candidates']=zrs[:40]
o.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('ZHOU_TOP',[(x['dx'],x['dy'],x['minimum_visible']) for x in zrs[:15]])
print('ZHOU_TOTAL',len(zrs))

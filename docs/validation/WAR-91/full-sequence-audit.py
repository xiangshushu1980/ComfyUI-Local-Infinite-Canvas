"""WAR-91 narrow new-camera transition sampling: no rerender or Blender source changes."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector as V
src,out=[Path(x) for x in sys.argv[sys.argv.index('--')+1:]]
assert src.name=='WAR91_derived_cameras.blend' and src.is_file()
bpy.ops.wm.open_mainfile(filepath=str(src))
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.device='CPU'
cams=[bpy.data.objects[n] for n in ('WAR91_Action40','WAR91_Desk40')]
ign={'FLOOR','NORTH_WALL','EAST_WALL_LOWER','EAST_WALL_UPPER','DOOR_EAST','KEY_FIXED_RING','KEY_FIXED_STEM','KEY_FIXED_TOOTH'}
blocks=[o for o in bpy.data.objects if o.type=='MESH' and o.name not in ign]
patch=[V((x,y,.755)) for x in (-.28,-.23,-.17) for y in (.43,.45,.47)]
rows=[]
for f in range(1,41):
 sc.frame_set(f);bpy.context.view_layer.update()
 for cam in cams:
  blockers=[]
  for target in patch:
   a,b=cam.location.copy(),target.copy();best=(float('inf'),None)
   for o in blocks:
    inv=o.matrix_world.inverted();x,y=inv@a,inv@b;vec=y-x
    if vec.length<1e-6:continue
    hit,p,_,_=o.ray_cast(x,vec.normalized(),distance=vec.length*.995)
    if hit:
     z=(p-x).length/vec.length
     if z<best[0]:best=(z,o.name)
   blockers.append(best[1])
  counts={name:blockers.count(name) for name in set(blockers)}
  rows.append({'frame':f,'camera':cam.name,'clear_9':blockers.count(None),
               'blockers':{'CLEAR' if k is None else k:v for k,v in counts.items()}})
res={'input_blend_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'device':'CPU',
     'frames':list(range(1,41)),'rows':rows,
     'limits':'9 fixed key patch points; occlusion is camera ray geometry only, not audience reading; derived WAR-72 source.'}
out.write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for r in rows:print('V1_TRANSITION',r)

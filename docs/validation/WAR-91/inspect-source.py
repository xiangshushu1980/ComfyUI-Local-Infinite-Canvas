import bpy,json,sys
from pathlib import Path
src=Path(sys.argv[sys.argv.index('--')+1])
bpy.ops.wm.open_mainfile(filepath=str(src))
s=bpy.context.scene
print('INSPECT_VERSION',bpy.app.version_string)
print('INSPECT_FRAME',s.frame_start,s.frame_end,'CURRENT',s.frame_current)
for n in sorted(bpy.data.objects.keys()):
 if n.startswith(('KEY_','PAPER_','STACK_','BLUE_','ZHOU_','LIN_','SHOT')):
  o=bpy.data.objects[n]
  print('OBJ',n,o.type,tuple(round(float(t),4) for t in o.matrix_world.translation),'scale',tuple(round(float(t),4) for t in o.scale))

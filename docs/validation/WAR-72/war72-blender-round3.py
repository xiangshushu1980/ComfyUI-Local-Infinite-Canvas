# WAR-72 third-pass derived Blender CPU fixture; never edits WAR-65/frozen sources.
# Run via Windows Blender 5.2.3 --background --factory-startup --threads 2 --python this_file -- --variant baseline|revision
import bpy, math, json, csv, sys, hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
variant = args[args.index('--variant')+1] if '--variant' in args else 'baseline'
assert variant in ('baseline','revision')
OUT = ROOT / 'round3' / variant
OUT.mkdir(parents=True, exist_ok=True)
K = Vector((-.25,.45,.792))
LIN=(.42,-.28)                 # WAR-72 second-pass candidate, not frozen
ZSTART=Vector((2.,-1.30,0))
ZEND=Vector((.85,-.35,0))
CAM2=Vector((-1.60,-1.60,1.55) if variant=='baseline' else (-2.50,-2.40,1.70))
CAM3=Vector((-.95,-.65,1.50)) # unverified derived ECU camera, not frozen
PATH_N=21
# The only revision, if selected, shifts Shot02 camera aim, not any scene state.
CAM2_AIM = Vector((-.05,-.04,1.25)) if variant=='baseline' else (K*.45+Vector((LIN[0],LIN[1]+.07,1.72))*.55)
X=Vector((1,0,0))
def mat(name, rgb, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metallic
    p.inputs['Roughness'].default_value=.45
    return m
wall=mat('warm neutral wall',(.50,.53,.54)); floor=mat('floor',(.29,.33,.38))
wood=mat('desk wood',(.39,.27,.17)); silver=mat('silver K',(.78,.81,.84),.6)
paper=mat('paper',(.88,.86,.78)); blue=mat('blue folder',(.08,.28,.7))
linmat=mat('Lin torso charcoal',(.18,.23,.27)); skin=mat('skin',(.65,.45,.33))
zhoumat=mat('Zhou cream',(.76,.70,.56)); dark=mat('dark pants',(.10,.12,.16))
red=mat('trace marks',(.8,.10,.07))

def cube(n, loc, dim, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc);o=bpy.context.object;o.name=n
    o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material); return o
def sphere(n,loc,scale,material,segments=16,rings=10):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
    o=bpy.context.object;o.name=n;o.scale=scale;o.data.materials.append(material);return o
def beam(n, a,b,r,material):
    a,b=Vector(a),Vector(b);mid=(a+b)*.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=1,depth=2,location=mid)
    o=bpy.context.object;o.name=n;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    o.scale=(r,r,(b-a).length/2);o.data.materials.append(material)
    return o
def set_beam(o,a,b):
    a,b=Vector(a),Vector(b)
    o.location=(a+b)*.5;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    o.scale=(.063,.063,(b-a).length/2)
    for t in ('location','rotation_euler','scale'):o.keyframe_insert(data_path=t)
def keyloc(o,frame,loc):
    o.location=loc;o.keyframe_insert('location',frame=frame)
def aim(cam,target):
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    return cam
def camera(name,xyz,target,lens):
    data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(cam);cam.location=xyz;cam.data.lens=lens
    cam.data.sensor_width=36.;cam.data.sensor_fit='HORIZONTAL'
    aim(cam,target);return cam

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU'
sc.cycles.samples=7;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=800;sc.render.resolution_y=450;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.world.color=(.45,.45,.45) if variant=='baseline' else (.08,.08,.08)
sc.view_settings.view_transform='Standard'
sc.camera=None
cube('FLOOR',(0,-.8,-.025),(5.8,5.3,.05),floor)
cube('NORTH_WALL',(0,.87,1.3),(5.4,.10,2.6),wall)
cube('EAST_WALL_UPPER',(2.4,.4,1.3),(.1,.95,2.6),wall)
cube('EAST_WALL_LOWER',(2.4,-2.15,1.3),(.1,.75,2.6),wall)
cube('DOOR_EAST',(2.4,-1.25,1.05),(.045,.88,2.1),wood)
cube('DESK_TOP',(0,.40,.725),(2.2,.8,.05),wood)
for x in [-.95,.95]:
 for y in [.14,.67]:
    cube('desk leg',(x,y,.35),(.07,.07,.70),wood)

# One and only one key. Never transform key in any timeline state.
bpy.ops.mesh.primitive_torus_add(major_radius=.019,minor_radius=.005,location=(-.265,.45,.792),major_segments=22,minor_segments=8)
key_ring=bpy.context.object;key_ring.name='KEY_FIXED_RING';key_ring.data.materials.append(silver)
key_stem=beam('KEY_FIXED_STEM',(-.246,.45,.791),(-.182,.45,.791),.004,silver)
key_tooth=cube('KEY_FIXED_TOOTH',(-.184,.460,.791),(.011,.021,.008),silver)
key_objs=[key_ring,key_stem,key_tooth]; key_transform={o.name:[round(v,5) for v in o.location] for o in key_objs}
# Stationary paper stack has top z=0.824. Moving cover starts over the key.
stack=[]
for i in range(4):
    stack.append(cube('STACK_%02d'%i,(-.53,.46,.789+.009*i),(.38,.26,.007),paper))
cover=cube('PAPER_MOVING',(-.265,.45,.811),(.31,.22,.006),paper)
folder=cube('BLUE_FOLDER',(-.78,.20,.849),(.44,.32,.014),blue)
for f,p in ([(1,(-.265,.45,.811)),(8,(-.40,.45,.856)),(20,(-.53,.45,.838)),(40,(-.53,.45,.838))] if variant=='baseline' else [(1,(-.265,.45,.811)),(8,(-.40,.45,.856)),(20,(-.53,.45,.824)),(40,(-.53,.45,.824))]):
    keyloc(cover,f,p)
for f,p in ([(1,(-.78,.20,.849)),(20,(-.78,.20,.849)),(30,(-.67,.30,1.07)),(34,(-.48,.43,.91)),(40,(-.37,.46,.832))] if variant=='baseline' else [(1,(-.80,.13,.764)),(20,(-.80,.13,.764)),(30,(-.67,.30,1.07)),(34,(-.48,.43,.91)),(40,(-.37,.46,.836))]):
    keyloc(folder,f,p)

# Torso, shoulders, neck, head, separate arms.
lin_torso=sphere('LIN_TORSO',(LIN[0],LIN[1],1.27),(.30,.17,.46),linmat)
lin_shoulders=sphere('LIN_SHOULDERS',(LIN[0],LIN[1]+.012,1.52),(.345,.16,.16),linmat)
lin_head=sphere('LIN_HEAD',(LIN[0],LIN[1]+.07,1.72),(.119,.106,.147),skin)
lin_neck=beam('LIN_NECK',(LIN[0],LIN[1]+.02,1.57),(LIN[0],LIN[1]+.04,1.62),.08,skin)
lin_hips=sphere('LIN_PANTS',(LIN[0],LIN[1],.89),(.245,.16,.24),dark)
for s in [-1,1]:
   beam('LIN_LEG_'+str(s),(LIN[0]+s*.13,LIN[1],.82),(LIN[0]+s*.13,LIN[1]-.015,.1),.09,dark)
sL=(LIN[0]-.235,LIN[1]+.015,1.46);sR=(LIN[0]+.235,LIN[1]+.015,1.46)
elL=(-.10,.00,1.14); elR=(.56,-.03,1.16)
lu=beam('LIN_L_UPPER',sL,elL,.073,linmat);ll=beam('LIN_L_FOREARM',elL,(-.265,.45,.875),.060,skin)
ru=beam('LIN_R_UPPER',sR,elR,.073,linmat);rl=beam('LIN_R_FOREARM',elR,(.44,.1,.98),.060,skin)
lh=sphere('LIN_LEFT_HAND',(-.265,.45,.87),(.060,.047,.034),skin)
rh=sphere('LIN_RIGHT_HAND',(.44,.10,.98),(.062,.05,.036),skin)
hands={
 1: ((-.265,.45,.87),(.45,.10,.99)),
 8: ((-.40,.45,.91),(.45,.10,.99)),
 20:((-.53,.45,.89),(.45,.10,.99)),
 30:((-.53,.38,1.13),(-.65,.3,1.14)),
 34:((-.53,.38,1.13),(-.49,.43,.99)),
 40:((-.53,.45,.89),(-.37,.46,.89))
}
def rigbeam_key(o,a,b,f,r):
    a,b=Vector(a),Vector(b);o.location=(a+b)*.5
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    o.scale=(r,r,(b-a).length/2)
    for p in ('location','rotation_euler','scale'):o.keyframe_insert(p,frame=f)
for f,(l,r) in hands.items():
 for ob,loc in [(lh,l),(rh,r)]:keyloc(ob,f,loc)
 rigbeam_key(lu,sL,elL,f,.073);rigbeam_key(ll,elL,l,f,.060)
 rigbeam_key(ru,sR,elR,f,.073);rigbeam_key(rl,elR,r,f,.060)

# Zhou independently movable proxy; root + local body, head and both eye markers.
zh=bpy.data.objects.new('ZHOU_ROOT_PATH',None);sc.collection.objects.link(zh)
direction=(ZEND-ZSTART).normalized()
heading=math.atan2(-direction.x,direction.y)
zh.rotation_euler.z=heading
def attach(o):o.parent=zh;return o
zt=attach(sphere('ZHOU_TORSO',(0,0,1.26),(.225,.145,.43),zhoumat))
zs=attach(sphere('ZHOU_SHOULDERS',(0,.0,1.51),(.26,.16,.14),zhoumat))
zhead=attach(sphere('ZHOU_HEAD',(0,.035,1.68),(.112,.108,.14),skin))
for ss in [-1,1]:
 attach(beam('ZHOU_LEG'+str(ss),(ss*.12,0,.90),(ss*.12,0,.09),.08,dark))
eyeobjs=[]
for s,name in [(-1,'ZHOU_LEFT_EYE'),(1,'ZHOU_RIGHT_EYE')]:
   o=bpy.data.objects.new(name,None);sc.collection.objects.link(o);o.parent=zh;o.location=(s*.032,.125,1.60)
   eyeobjs.append(o)
for f,t in [(1,0),(20,.55),(40,1.0)]:
 keyloc(zh,f,(ZSTART*(1-t)+ZEND*t))
def set_zhou(t):
 zh.location=ZSTART*(1-t)+ZEND*t
 bpy.context.view_layer.update()

cam2=camera('SHOT02_40MM',CAM2,CAM2_AIM,40)
cam3=camera('SHOT03_85MM',CAM3,(-.36,.46,.817),85)
camtop=camera('TOP_PLAN',(0,-.20,7.6),(0,-.20,0),50)
camtop.data.type='ORTHO';camtop.data.ortho_scale=6.0
cam2.data.dof.use_dof=False;cam3.data.dof.use_dof=False
# Lights CPU Cycles only.
def light(n,loc,power,size):
    dat=bpy.data.lights.new(n,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size
    ob=bpy.data.objects.new(n,dat);sc.collection.objects.link(ob);ob.location=loc;aim(ob,(0,0,.7))
light('soft overhead',(-.5,-.8,3.0),550 if variant=='baseline' else 90,3.0)
light('east fill',(1.5,-.8,2.8),250 if variant=='baseline' else 45,2.0)

# World-space mesh cast against all relevant low-poly candidates. No scene raycast
# that would conflate a hit on the key itself with an occlusion.
occluders=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('KEY_FIXED') and o.name not in ('FLOOR','NORTH_WALL','EAST_WALL_UPPER','EAST_WALL_LOWER','DOOR_EAST')]
def ray(origin,target):
    start=Vector(origin);end=Vector(target);worldlen=(end-start).length
    best=(1.0,None)
    for o in occluders:
        if o.hide_render:continue
        inv=o.matrix_world.inverted()
        a=inv@start;b=inv@end;v=b-a
        if v.length<1e-9:continue
        ok,point,norm,poly=o.ray_cast(a,v.normalized(),distance=v.length*.995)
        if ok:
            frac=(point-a).length/v.length
            if frac<best[0]:best=(frac,o.name)
    return {'blocked':best[1] is not None,'blocker':best[1], 'fraction':round(best[0],5)}
def pix(o,point):
    n=world_to_camera_view(sc,o,Vector(point))
    return [round(n.x,4),round(n.y,4),round(n.z,4)]
def inside(p):return p[2]>0 and 0<=p[0]<=1 and 0<=p[1]<=1
def eye_for(t,s,z=1.60,turn_deg=0):
    # Same 6.4 cm binocular separation, plus 12.5 cm anterior head offset.
    a=heading+math.radians(turn_deg);c,si=math.cos(a),math.sin(a)
    x=s*.032;y=.125
    p=ZSTART*(1-t)+ZEND*t
    return Vector((p.x+c*x-si*y,p.y+si*x+c*y,z))
def state(frame):
    sc.frame_set(frame);bpy.context.view_layer.update()
def check_path(z=1.60,turn=0,n=PATH_N):
    records=[]
    for i in range(n):
        t=i/(n-1);set_zhou(t)
        lr=[ray(eye_for(t,s,z,turn),K) for s in [-1,1]]
        records.append({'index':i,'t':round(t,4),
                        'zhou_xy':[round(zh.location.x,4),round(zh.location.y,4)],
                        'left':lr[0],'right':lr[1],
                        'both_blocked':all(q['blocked'] for q in lr)})
    return records
def summary(records):
    return {'count':len(records),'both_blocked':sum(a['both_blocked'] for a in records),
            'failed_indices':[r['index'] for r in records if not r['both_blocked']]}
def write_csv(rows,name):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        wr=csv.writer(f)
        wr.writerow(['index','t','zhou_x','zhou_y','L_blocked','L_by','L_frac','R_blocked','R_by','R_frac','both'])
        for a in rows:
            l,r=a['left'],a['right']
            wr.writerow([a['index'],a['t'],*a['zhou_xy'],l['blocked'],l['blocker'],l['fraction'],
                         r['blocked'],r['blocker'],r['fraction'],a['both_blocked']])
def shoot(frame,cam,filename):
    state(frame);sc.camera=cam
    sc.render.filepath=str(OUT/filename)
    bpy.ops.render.render(write_still=True)
    print('RENDERED',filename,flush=True)

# Baseline verification before image-making; no model or frozen data rewritten.
state(20)
path=check_path()
write_csv(path,'zhou_binocular_path_21.csv')
perturb={}
for label,z,turn in [('short_1m50',1.50,0),('tall_1m70',1.70,0),
                      ('head_left_12deg',1.60,-12),('head_right_12deg',1.60,12)]:
    perturb[label]=summary(check_path(z,turn))
dense=check_path(n=81)
# Spatial reach and rough lower-body overlaps are not substitutes for full mocap.
reach={}
for f,(handleft,handright) in hands.items():
    sh=Vector(sL);target=Vector(handleft);length=(target-sh).length
    reach[str(f)]={'left_shoulder_to_hand_m':round(length,4),
                   'over_0p75m':length>.75}
# Conservative ellipse proximity indicator; contact must be checked visually/physically.
collision=[]
for i in range(21):
    t=i/20;p=ZSTART*(1-t)+ZEND*t;dx=p.x-LIN[0];dy=p.y-LIN[1]
    # World AABB-normalized elliptical sum approximates parallel-section overlap.
    rx=.30+math.hypot(.225*math.cos(heading),.145*math.sin(heading))
    ry=.17+math.hypot(.225*math.sin(heading),.145*math.cos(heading))
    proxy=(dx/rx)**2+(dy/ry)**2
    collision.append({'i':i,'normalized_center_separation':round(proxy,4),
                      'potential_torso_overlap':proxy<1})
# Camera and composition at each state
state(20)
camera_path=[]
for i in range(21):
 t=i/20;set_zhou(t)
 camera_path.append({'i':i,'camera2':ray(cam2.location,K),'camera3':ray(cam3.location,K)})
# 3-by-3 key surface locations test whether the whole key footprint is covered.
keypatch=[Vector((xx,yy,.792)) for xx in (-.28,-.23,-.17) for yy in (.43,.45,.47)]
keypatch_results={}
for f in (1,20,34,40):
 state(f);keypatch_results[str(f)]={
 'cam2': [ray(cam2.location,p)['blocked'] for p in keypatch],
 'cam3': [ray(cam3.location,p)['blocked'] for p in keypatch]}

views={}
for f,cam in [(1,cam2),(10,cam2),(20,cam2),(20,cam3),(34,cam3),(40,cam3)]:
    state(f)
    mark=f'{cam.name}_f{f:02d}'
    targets={'key_center':K,'key_east_end':(-.17,.45,.792),
             'lin_face':(LIN[0],LIN[1]+.08,1.72),
             'lin_hands':tuple(lh.matrix_world.translation),
             'folder_center':tuple(folder.matrix_world.translation),
             'stack_center':(-.53,.46,.819),
             'zhou_face':tuple(zhead.matrix_world.translation)}
    views[mark]={'camera':list(cam.location),'aim':list(CAM2_AIM if cam==cam2 else Vector((-.36,.46,.817))),
                 'lens_mm':cam.data.lens,
                 'projection':{n:{'uv_depth':pix(cam,p),'inside_frame':inside(pix(cam,p))} for n,p in targets.items()},
                 'ray_to_key':ray(cam.location,K),
                 'key_span_px':round(abs(pix(cam,(-.17,.45,.792))[0]-pix(cam,(-.28,.45,.792))[0])*sc.render.resolution_x,2)}
# Check props in state: no fixed key movement and no overlap with key top.
props={}
for f in (1,8,20,30,34,40):
    state(f)
    box=folder.matrix_world.translation
    paperloc=cover.matrix_world.translation
    props[str(f)]={'paper_cover_center':[round(a,4) for a in paperloc],
                   'folder_center':[round(a,4) for a in box],
                   'folder_bottom_z':round(box.z-.007,4),
                   'key_top_z':.800,
                   'key_transforms_unchanged':all(key_transform[o.name]==[round(v,5) for v in o.location] for o in key_objs)}
key_point_unchanged=all(item['key_transforms_unchanged'] for item in props.values())
result={'variant':variant,'engine':'Blender Cycles CPU only','blender_version':bpy.app.version_string,
        'source_frozen_context':'WAR-65 D assisted v1 Step3/6/7; WAR-72 first+second round',
        'all_scene_dimensions_are_derived_assumptions':True,
        'coordinates':{'K':list(K),'LIN':list(LIN),'ZHOU_START':list(ZSTART),'ZHOU_END':list(ZEND),
                       'CAM2':list(CAM2),'CAM3':list(CAM3),'CAM2_AIM':list(CAM2_AIM)},
        'path_21':path,'path_21_summary':summary(path),'path_81_summary':summary(dense),
        'camera_path_21':camera_path,'keypatch_3x3':keypatch_results,
        'sensitivity':perturb,'potential_torso_collision':collision,
        'arm_reach':reach,'camera_checks':views,'prop_states':props,
        'key_remained_unchanged':key_point_unchanged,
        'caveats':['Eye positions move with walking heading, no actual perception/attention proof',
         'Torso is ellipsoid; shoulder/arm positions are illustrative and may be unphysical',
         '21 discrete points do not prove continuous occlusion','2D proximity overlap is a screening proxy',
         'Rendered pixel size and unobstructed ray do not prove audience comprehension',
         'Frames of moving props do not prove physical dynamics or gravity']}
(OUT/'measurements.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SUMMARY',variant,summary(path),'dense',summary(dense),'head_height',perturb,'reach',reach,
      'overlap_count',sum(c['potential_torso_overlap'] for c in collision),
      'camera_f20',views['SHOT02_40MM_f20']['ray_to_key'],flush=True)
# Scene saved in reviewable T1 state; all timeline keyframes preserved.
state(20);set_zhou(.55)
sc.camera=cam2
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('WAR72_' + variant + '.blend')))
for f,cam,n in [(1,cam2,'T0_Shot02.png'),(10,cam2,'transition_T0_T1_Shot02.png'),
                 (20,cam2,'T1_Shot02.png'),(20,cam3,'T1_Shot03.png'),
                 (34,cam3,'transition_T1_T2_Shot03.png'),
                 (40,cam3,'T2_Shot03.png'),(20,camtop,'top_T1.png')]:
    shoot(f,cam,n)
print('DONE',variant,flush=True)

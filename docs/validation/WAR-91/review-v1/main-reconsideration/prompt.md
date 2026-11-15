你是 WAR-91 V1 Blender 低模真实分层核证后的**证据复议主审阅人**，请核查上轮主审阅 needs_evidence_correction 是否已经由后来真正执行的新摄像机全序列抽样补证。
此前所有审阅在本追加 Blender 测试之前完成，当时确实缺少新机位 f2–7 和 f35–39 数据。后续独立采样源文件是新保存的 WAR91_derived_cameras.blend（保持旧场景，只包含新 ACTION40/DESK40 摄影机），使用 Windows Blender 5.2.3、CPU。
本次真正针对两新机位每帧f1..40的3x3 K补丁射线首交，必须逐项对照，不得继续称这两段未测、也不可用老机位的帧数据替代。
如果证据有效，明确哪些原有 blocker 已关闭、哪些（文件夹支承由 PAPER_MOVING 顶页而非 STACK_03、周0/25夹面不可见、右肩0.887>0.770、C1和C2无动画）仍是老姿态约束或待证。
仍不允许声称新版 B 的真实几何/观看通过，更不能声称有真人观众测试。
输出 ready_for_limited_V1_report|still_needs_evidence_correction，依据与最小后续行动，中文 300–700 字。不修改文件、用户A/B、原剧本。
=== PREVIOUS LEAD (BEFORE FULL 1..40 AUDIT) ===
**needs_evidence_correction**

冻结包确认的是 WAR-72 round4 旧 B 场景（源 SHA `23fc26a…a0373`，Blender 5.2.3、CPU、2 线程），并非按新 WAR-90 四镜规格重建。以下可列为有限已测事实：旧场景两个候选机位在 f1 的钥匙 9/9 采样均被 `PAPER_MOVING` 遮挡，f8、20、30、34 均为 9/9 清通，f40 均被 `BLUE_FOLDER` 遮挡。由于候选机位没测 f2–7，尚不能称已测出“首次露出”时刻；f34–40 的 6、6、6、4、2、0、0 清通数来自旧 `SHOT02_40MM`，不能代替新机位的再遮挡过程。约 40×15 与 56×18 像素是网格投影框尺寸，不是观众认出钥匙的结果。

支承对象应纠正为 `PAPER_MOVING`：f40 文件夹底与移动纸页顶面高差为 `-0.0 m`、XY 重叠 `0.0473 m²`；与下层 `STACK_03` 顶面相差 `0.0075 m`。原 `contact()`只检 `STACK_03`，不足以证明支承；纠正数据仍只是边界框与表面检查，不含承重动力学。

G2 旧代理显示周路径五个站位、双眼各 25 个文件夹顶面样点都被林遮挡；眼到 K 的 f20、f40 各 21/21 样本也被林遮挡。因此“周实际看到蓝夹、摄影机看 K”的联合条件在此旧站位未实现；这些样点并非完整表面覆盖，射线仅证明几何首交，不证明角色注意或观众辨识。应改林的站位／姿态或夹位置，在修订姿态下对准真实文件夹表面复测。

C1 未测停手、问话、回手及再抓的连续表演或四镜接缝：旧源 f40 后没有相应动作键。C2 的静态锚点反例是右肩至 K 为 `0.88681 m`，超过两段各 `0.385 m` 的简化臂长总和 `0.77 m`；它说明旧肩位下右手直达不可行。新姿态、躯干／脚步调整和绕行取物均未测，且旧源码有右前臂穿桌，不能据此判新方案不可达或可达。最少局部修订是更正报告中的支承对象和首露措辞，明确 G2 射线及 C1/C2 的未测范围；V2 再决定是否重构姿态并实测连续动作、手物接触和镜头接缝。

**结论：旧代理暴露了可修正的站位与动作约束，不能据此认定新四镜 B 失效。**
=== VERIFIED NEW CAMERA 1..40 RAYS ===
{
  "WAR91_Action40": {
    "all_40_frame_clear_counts": [
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        0
      ],
      [
        4,
        0
      ],
      [
        5,
        6
      ],
      [
        6,
        9
      ],
      [
        7,
        9
      ],
      [
        8,
        9
      ],
      [
        9,
        9
      ],
      [
        10,
        9
      ],
      [
        11,
        9
      ],
      [
        12,
        9
      ],
      [
        13,
        9
      ],
      [
        14,
        9
      ],
      [
        15,
        8
      ],
      [
        16,
        9
      ],
      [
        17,
        9
      ],
      [
        18,
        9
      ],
      [
        19,
        9
      ],
      [
        20,
        9
      ],
      [
        21,
        9
      ],
      [
        22,
        9
      ],
      [
        23,
        9
      ],
      [
        24,
        9
      ],
      [
        25,
        9
      ],
      [
        26,
        9
      ],
      [
        27,
        9
      ],
      [
        28,
        9
      ],
      [
        29,
        9
      ],
      [
        30,
        9
      ],
      [
        31,
        9
      ],
      [
        32,
        9
      ],
      [
        33,
        9
      ],
      [
        34,
        9
      ],
      [
        35,
        9
      ],
      [
        36,
        9
      ],
      [
        37,
        3
      ],
      [
        38,
        0
      ],
      [
        39,
        0
      ],
      [
        40,
        0
      ]
    ],
    "first_partial": 5,
    "first_full": 6,
    "first_blocked_later": 38
  },
  "WAR91_Desk40": {
    "all_40_frame_clear_counts": [
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        0
      ],
      [
        4,
        0
      ],
      [
        5,
        6
      ],
      [
        6,
        9
      ],
      [
        7,
        9
      ],
      [
        8,
        9
      ],
      [
        9,
        9
      ],
      [
        10,
        9
      ],
      [
        11,
        9
      ],
      [
        12,
        9
      ],
      [
        13,
        9
      ],
      [
        14,
        9
      ],
      [
        15,
        9
      ],
      [
        16,
        9
      ],
      [
        17,
        9
      ],
      [
        18,
        9
      ],
      [
        19,
        9
      ],
      [
        20,
        9
      ],
      [
        21,
        9
      ],
      [
        22,
        9
      ],
      [
        23,
        9
      ],
      [
        24,
        9
      ],
      [
        25,
        9
      ],
      [
        26,
        9
      ],
      [
        27,
        9
      ],
      [
        28,
        9
      ],
      [
        29,
        9
      ],
      [
        30,
        9
      ],
      [
        31,
        9
      ],
      [
        32,
        9
      ],
      [
        33,
        9
      ],
      [
        34,
        9
      ],
      [
        35,
        9
      ],
      [
        36,
        9
      ],
      [
        37,
        3
      ],
      [
        38,
        0
      ],
      [
        39,
        0
      ],
      [
        40,
        0
      ]
    ],
    "first_partial": 5,
    "first_full": 6,
    "first_blocked_later": 38
  }
}
=== SUPPORT CONTACT CORRECTION ===
{
  "folder": [
    [
      -0.5900000333786011,
      -0.15000000596046448
    ],
    [
      0.30000001192092896,
      0.6200000047683716
    ],
    [
      0.7914999723434448,
      0.8055000305175781
    ]
  ],
  "moved_paper_top_page": [
    [
      -0.684999942779541,
      -0.3749999701976776
    ],
    [
      0.3399999737739563,
      0.5600000023841858
    ],
    [
      0.7854999899864197,
      0.7915000319480896
    ]
  ],
  "underlying_stack_top": [
    [
      -0.7199999690055847,
      -0.3399999737739563
    ],
    [
      0.33000001311302185,
      0.5900000333786011
    ],
    [
      0.7770000100135803,
      0.7839999794960022
    ]
  ],
  "folder_bottom_minus_moved_paper_top_m": -0.0,
  "folder_bottom_minus_underlying_stack_top_m": 0.0075,
  "folder_moved_paper_overlap_xy_m2": 0.0473,
  "folder_underlying_stack_overlap_xy_m2": 0.065,
  "interpretation": "The moved paper is the top member of the pile, not the lower STACK_03 sheet; pair folder to actual PAPER_MOVING top at final pose."
}
=== ACTUAL FULL SEQUENCE SCRIPT ===
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

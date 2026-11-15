"""WAR-91 actual isolated review process. Writes real Codex prompts, events, model outputs.
No geometric re-execution and no user A/B approvals. """
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,subprocess,os,shutil,tempfile,time,datetime
ROOT=Path('/home/sean/projects/canvas-lab/docs/validation/WAR-91')
OUT=ROOT/'review-v1'
OUT.mkdir(exist_ok=True)
def jd(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(data):return hashlib.sha256(data).hexdigest()
d=json.loads((ROOT/'v1/results.json').read_text())
f=json.loads((ROOT/'v1/followup-audit.json').read_text())
def slim_row(x):
 return {k:x[k] for k in ['camera','frame','key_projected','key_sample_clear_9','key_sample_blocker_counts','lin_face_in_frame','zhou_face_in_frame','axis_start_end_sign']}
small={'B_approved_run':d['baseline_B_run'],'source_sha':d['source_sha256'],
       'blender_version':d['blender_version'],'device':d['device'],'threads':d['threads'],
       'candidate_cameras':d['candidate_cameras'],'G1_shot02':[slim_row(r) for r in d['shot02_rows']],
       'G1_support_corrected':f['support_correction'],
       'G1_static_3d_contact_surface':d['folder_support_contact'],
       'G1_transition_f34_to40':f['legacy_camera_final_cover_transition'],
       'G2_path_counts_by_frame':[{ 'frame':t,'n':len([x for x in d['zhou_path_eye_samples'] if x['frame']==t]),
         'both_key_blocked_by_lin':sum(x['both_key_blocked_by_lin'] for x in d['zhou_path_eye_samples'] if x['frame']==t),
         'both_can_see_folder_origin_without_lin_blocking':sum(x['both_folder_center_line_clear_of_lin'] for x in d['zhou_path_eye_samples'] if x['frame']==t)} for t in (20,40)],
       'G2_corrected_folder_surface_visibility':f['folder_visibility_25_spots_5_path'],
       'G2_final_k_cover_targets':f['final_covered_location_from_Zhou_both_eyes'],
       'C1':d['continuity_C1'],'C2':d['handoff_C2'],
       'limits':d['limitations']}
packet='=== FROZEN ISSUE AND EVIDENCE SUMMARY ===\n'+json.dumps(small,ensure_ascii=False,indent=2)+'\n'
for name in ['run-v1.py','followup-audit.py']:
 packet+='\n=== INDEPENDENTLY INSPECT SOURCE: '+name+' ===\n'+(ROOT/name).read_text()
packet+='\n=== END FROZEN REVIEW PACKET ===\n'
(OUT/'frozen-review-packet.txt').write_text(packet,encoding='utf8')
jd(OUT/'manifest.json',{'packet_sha256':sha(packet.encode()),'source_sha':d['source_sha256'],
                       'run_results_sha':sha((ROOT/'v1/results.json').read_bytes()),
                       'followup_results_sha':sha((ROOT/'v1/followup-audit.json').read_bytes()),
                       'review_count':2,'lead_count':1,'user_B_approved_still_true':True})
def call(label,model,effort,task):
 dest=OUT/label
 dest.mkdir(exist_ok=False)
 prompt=('你是 Canvas Lab WAR-91 V1 Blender CPU 最小复检的真实独立核证 Reviewer。'
         '你不能修改实验、不能签用户批准。审阅范围是已记录的旧 Blender 低模代理实测相对新四镜 B 基线的含义，'
         '不仅仅复述报告。请区别已测通过、旧代理反例、尚未测和真人/观众不可推出。'
         '逐项核验 G1 初盖/首露/再遮挡、纸叠支承纠错、G2 周能否实际看到蓝夹而摄影机看 K、'
         'C1 动作停手缺少真实连续表演模型、C2 右手起取可达性。'
         '旧代理不能证明新四镜结构必然不可行，也不能把代理条件性结果判成实际观众辨识成功。'
         '只输出关键发现、能引用的数字、实质代码测量错误/过度推断、对应局部修订方向，400–900字。'
         '\n专项：'+task+'\n'+packet)
 (dest/'prompt.md').write_text(prompt)
 home=Path(tempfile.mkdtemp(prefix='.auth-',dir=dest))
 st=time.monotonic()
 try:
  auth=Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'auth.json'
  if auth.exists():
   (home/'auth.json').write_bytes(auth.read_bytes())
   (home/'auth.json').chmod(0o600)
  cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
       '--sandbox','read-only','--json','-m',model,
       '-c',f'model_reasoning_effort="{effort}"','-c','approval_policy="never"',
       '-c','features.shell_tool=false','-c','project_doc_max_bytes=0',
       '-C',str(dest),'-o',str(dest/'result.md'),'-']
  with (dest/'events.jsonl').open('wb') as so,(dest/'stderr.txt').open('wb') as se:
   p=subprocess.run(cmd,input=prompt.encode('utf8'),stdout=so,stderr=se,
        env=dict(os.environ,CODEX_HOME=str(home)),timeout=900)
  meta={'label':label,'model':model,'effort':effort,'exit':p.returncode,
        'duration_sec':round(time.monotonic()-st,1),'prompt_sha256':sha(prompt.encode()),
        'result_sha256':sha((dest/'result.md').read_bytes()) if (dest/'result.md').exists() else None}
  jd(dest/'run.json',meta)
  print('REVIEW_DONE',label,meta['exit'],meta['duration_sec'],flush=True)
  return meta
 finally:
  shutil.rmtree(home,ignore_errors=True)
roles=[
 ('reviewer-geometry','gpt-6-astra','medium','独立检查实际射线、场景支承/遮挡物体选错的风险、周能否看见夹位置、静态手臂0.887>0.770的含义，以及代理结论是否高估。'),
 ('reviewer-coverage','gpt-6-luna','low','核对新旧 Shot 命名与差异、是否错把旧镜头测试作新镜头测试、结果对四镜接缝/单次交付覆盖不足、文件冻结和测量代码可复现性。')]
with ThreadPoolExecutor(max_workers=2) as pool:
 futures=[pool.submit(call,*task) for task in roles]
 results=[x.result() for x in as_completed(futures)]
if any(x['exit']!=0 or not x['result_sha256'] for x in results):
 print('REVIEW_BLOCKED',flush=True)
 jd(OUT/'summary.json',{'complete':False,'reviews':results})
 raise SystemExit(2)
orig='\n'.join('=== '+label+' ORIGINAL ===\n'+(OUT/label/'result.md').read_text() for label,*_ in roles)
leadtask=('主审阅核证：独立对照冻结实测包、两份真实独立意见。'
  '不要按票数合并，必须区分关键不可行旧代理与新 B 方案绝对不可行。'
  '明确核对唯一物件支承面是 PAPER_MOVING 还是 STACK_03，'
  '周看到夹面的位置/射线样本是否确实朝真实表面，'
  '右手静态臂长反例与可变 Blocking 约束的关系，'
  '旧源码残余右臂穿桌和 C1/C2 的未测试部分，'
  '不要把像素大小等同观众认出。'
  '给出：ready_report/needs_evidence_correction；哪些结果可以作为有限已测事实；'
  '最少局部修订/后续 V2 决策；一条不让用户误认为 B 失效的简洁结论。500–900字。'
  '\n=== REVIEWS ===\n'+orig)
lead=call('main-reviewer','gpt-6-luna','medium',leadtask)
jd(OUT/'summary.json',{'complete':lead['exit']==0,'reviews':results,'lead':lead,
   'B_accepted_not_modified':True,'no_Geometry_code_changes':True})
print('WAR91_HIERARCHICAL_REVIEW_DONE',flush=True)

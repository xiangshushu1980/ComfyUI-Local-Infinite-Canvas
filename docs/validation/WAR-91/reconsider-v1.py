"""Follow-up main adjudication of actual new camera 1..40 frame-ray evidence."""
from pathlib import Path
import json,hashlib,subprocess,tempfile,os,shutil,time
root=Path('/home/sean/projects/canvas-lab/docs/validation/WAR-91')
out=root/'review-v1'/'main-reconsideration'
out.mkdir(exist_ok=False)
old=(root/'review-v1/main-reviewer/result.md').read_text()
raw=json.loads((root/'v1/new-camera-full-sequence.json').read_text())
support=json.loads((root/'v1/followup-audit.json').read_text())['support_correction']
digest=lambda b:hashlib.sha256(b).hexdigest()
sumrows={}
for cam in ['WAR91_Action40','WAR91_Desk40']:
 rr=[r for r in raw['rows'] if r['camera']==cam]
 sumrows[cam]={'all_40_frame_clear_counts':[(r['frame'],r['clear_9']) for r in rr],
       'first_partial':next((r['frame'] for r in rr if r['clear_9']>0),None),
       'first_full':next((r['frame'] for r in rr if r['clear_9']==9),None),
       'first_blocked_later':next((r['frame'] for r in rr if r['frame']>20 and r['clear_9']==0),None)}
prom=('你是 WAR-91 V1 Blender 低模真实分层核证后的**证据复议主审阅人**，请核查上轮主审阅 needs_evidence_correction 是否已经由后来真正执行的新摄像机全序列抽样补证。\n'
'此前所有审阅在本追加 Blender 测试之前完成，当时确实缺少新机位 f2–7 和 f35–39 数据。后续独立采样源文件是新保存的 WAR91_derived_cameras.blend（保持旧场景，只包含新 ACTION40/DESK40 摄影机），使用 Windows Blender 5.2.3、CPU。\n'
'本次真正针对两新机位每帧f1..40的3x3 K补丁射线首交，必须逐项对照，不得继续称这两段未测、也不可用老机位的帧数据替代。\n'
'如果证据有效，明确哪些原有 blocker 已关闭、哪些（文件夹支承由 PAPER_MOVING 顶页而非 STACK_03、周0/25夹面不可见、右肩0.887>0.770、C1和C2无动画）仍是老姿态约束或待证。\n'
'仍不允许声称新版 B 的真实几何/观看通过，更不能声称有真人观众测试。\n'
'输出 ready_for_limited_V1_report|still_needs_evidence_correction，依据与最小后续行动，中文 300–700 字。不修改文件、用户A/B、原剧本。\n'
'=== PREVIOUS LEAD (BEFORE FULL 1..40 AUDIT) ===\n'+old+'\n'
'=== VERIFIED NEW CAMERA 1..40 RAYS ===\n'+json.dumps(sumrows,ensure_ascii=False,indent=2)+'\n'
'=== SUPPORT CONTACT CORRECTION ===\n'+json.dumps(support,ensure_ascii=False,indent=2)+'\n'
'=== ACTUAL FULL SEQUENCE SCRIPT ===\n'+(root/'full-sequence-audit.py').read_text())
(out/'prompt.md').write_text(prom)
home=Path(tempfile.mkdtemp(prefix='.auth-',dir=out))
try:
 a=Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'auth.json'
 if a.exists():
  (home/'auth.json').write_bytes(a.read_bytes());(home/'auth.json').chmod(0o600)
 cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json',
      '-m','gpt-6-luna','-c','model_reasoning_effort="medium"','-c','approval_policy="never"',
      '-c','features.shell_tool=false','-c','project_doc_max_bytes=0','-C',str(out),'-o',str(out/'result.md'),'-']
 start=time.monotonic()
 with (out/'events.jsonl').open('wb') as so,(out/'stderr.txt').open('wb') as se:
  p=subprocess.run(cmd,input=prom.encode(),stdout=so,stderr=se,env=dict(os.environ,CODEX_HOME=str(home)),timeout=900)
 meta={'model':'gpt-6-luna','effort':'medium','exit':p.returncode,
       'duration_sec':round(time.monotonic()-start,1),
       'input_full_sequence_sha256':digest((root/'v1/new-camera-full-sequence.json').read_bytes()),
       'prompt_sha256':digest(prom.encode()),
       'result_sha256':digest((out/'result.md').read_bytes()) if (out/'result.md').exists() else None}
 (out/'run.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print('RECONSIDERATION',json.dumps(meta,ensure_ascii=False),flush=True)
finally:shutil.rmtree(home,ignore_errors=True)

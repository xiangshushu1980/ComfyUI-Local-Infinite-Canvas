#!/usr/bin/env python3
"""WAR-90 explicit hierarchical review: two independent, then lead. No pilot mutations."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,os,subprocess,tempfile,shutil,time

ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/review-round1-20261115'
PILOT=ROOT/'docs/planning/WAR-90/pilot-D'
RUNID='93fc96166f56424c8a69bfa6f12ff5e9'
SOURCE=ROOT/'docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-D/script-D.txt'
CAND=PILOT/'runs'/RUNID/'result.txt'
def digest(b): return hashlib.sha256(b).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def write_json(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def model_call(role,model,effort,prompt):
 target=OUT/role
 if target.exists(): raise RuntimeError('Refusing reviewer overwrite '+role)
 target.mkdir(parents=True)
 (target/'prompt.md').write_text(prompt)
 home=Path(tempfile.mkdtemp(prefix='.review-home-',dir=target))
 start=time.monotonic()
 try:
  auth=Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'auth.json'
  if auth.exists():
   (home/'auth.json').write_bytes(auth.read_bytes())
   (home/'auth.json').chmod(0o600)
  cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
       '--sandbox','read-only','--json','-m',model,'-c',f'model_reasoning_effort="{effort}"',
       '-c','approval_policy="never"','-c','features.shell_tool=false',
       '-c','project_doc_max_bytes=0','-C',str(target),
       '-o',str(target/'result.md'),'-']
  with (target/'events.jsonl').open('wb') as ev, (target/'stderr.txt').open('wb') as err:
   p=subprocess.run(cmd,input=prompt.encode(),stdout=ev,stderr=err,
                    env=dict(os.environ,CODEX_HOME=str(home)),timeout=720)
  info={'role':role,'model':model,'effort':effort,'exit':p.returncode,
        'seconds':round(time.monotonic()-start,1),'prompt_sha256':digest(prompt.encode()),
        'result_sha256':digest((target/'result.md').read_bytes()) if (target/'result.md').exists() else None,
        'ended_at':now()}
  write_json(target/'run.json',info)
  print('REVIEWER_DONE',role,info['exit'],info['seconds'],flush=True)
  return info
 finally:
  shutil.rmtree(home,ignore_errors=True)

def main():
 if (OUT/'manifest.json').exists(): raise RuntimeError('Round already exists; do not overwrite')
 src=SOURCE.read_bytes(); raw=CAND.read_bytes()
 assert digest(src)=='65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d'
 state=json.loads((PILOT/'state.json').read_text())
 assert state['active']['id']==RUNID and not state['pilot_A'] and not state['pilot_B']
 assert digest(raw)==json.loads((PILOT/'runs'/RUNID/'metadata.json').read_text())['result_sha256']
 write_json(OUT/'manifest.json',{'began_at':now(),'source_sha256':digest(src),
     'candidate_sha256':digest(raw),'review_topology':'2 isolated Luna Low, 1 Luna Medium lead',
     'pilot_A_on_start':None})
 (OUT/'frozen-source.txt').write_bytes(src)
 (OUT/'frozen-candidate.json').write_bytes(raw)
 s=src.decode();c=raw.decode()
 common=('WAR-90 首次独立 Director Intent A 预审；你不是导演生成器或人类批准者。'
         '仅使用下方剧本与候选，不能看其他 Reviewer 结论或外部研究，不能编辑文件。'
         '这是 Intent 而非 Beat/Blocking/Shot，不以缺乏镜头表或真实媒体判失败。'
         '分辨 P0 已证故事硬冲突、P1 影响表达的实质漏洞、P2 局部/未证、P3 合理多解。'
         '请引用源/候选确切证据，不凭偏好、格式、字数评判。'
         '给出严重性、证据、理由、修法或后续验证，500-900字中文结论。')
 raw_input='\n===已冻结源剧本及确认意图===\n'+s+'\n===未批准 Intent 候选 JSON===\n'+c+'\n===结束===\n'
 jobs={
 'reviewer-story': '只审故事事实/信息时序：钥匙首次显露林未见、蓝夹无意覆盖、周只因位置异常怀疑、再次发现、单把钥匙交周右手及剧情忠实度；抓出强行补写的背景、错误批准。',
 'reviewer-craft': '只审专业导演判断：观众体验主轴、真实替代及成本、表演指导是否可执行、时间/声音政策是否过早定死、是否过度反复规则、媒体验证边界。'
 }
 with ThreadPoolExecutor(max_workers=2) as pool:
  futures={pool.submit(model_call,name,'gpt-6-luna','low',common+'\n专项：'+focus+raw_input):name for name,focus in jobs.items()}
  responses=[f.result() for f in as_completed(futures)]
 if any(z['exit']!=0 or not z['result_sha256'] for z in responses):
  print('INDEPENDENT_FAILED_NOT_STARTING_MAIN',flush=True);return
 opinions='\n'.join('===独立审阅 '+name+'===\n'+(OUT/name/'result.md').read_text() for name in jobs)
 lead=('你是 WAR-90 本次真实主审阅 Agent。你必须综合两份独立 Reviewer 的实际报告，但不能按投票决定。'
       '核对冻结剧本与候选原文，判断哪些意见证据充分、哪些不成立或留待媒体。'
       '对结果作 ready_for_user_A / needs_local_revision / blocked 单一裁定；如有硬冲突必须指出确切原句。'
       '输出：1裁定与关键理由；2采纳/拒绝每份 Reviewer 的主要意见及依据；'
       '3交主流程的 120-250 字精简 A 导演意图，含真正替代方案及其代价；'
       '4用户 A 唯一应决定的表达方向；5待验证风险。不改任何文件，不自签 A 或正式 WAR-35。'
       '普通合理导演多解不得强制按某一镜头；用户不需逐份审阅所有中间报告。')
 main=model_call('main-reviewer','gpt-6-luna','medium',lead+raw_input+'\n===两个独立审阅原文===\n'+opinions)
 write_json(OUT/'summary.json',{'ended_at':now(),'independent':responses,'lead':main,
   'source_sha256':digest(src),'candidate_sha256':digest(raw),'pilot_A_still_unapproved':True,
   'completed':all(z['exit']==0 for z in responses+[main])})
 print('HIERARCHICAL_REVIEW_DONE',main['exit'],flush=True)
if __name__=='__main__': main()

"""Independent post-implementation review: dual-entry architecture + compact Shot view."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import os,hashlib,json,time,subprocess
ROOT=Path('/home/sean/projects/canvas-lab')
D=ROOT/'docs/planning/WAR-90/permission-compact-20261116'
REV=D/'implementation-review'
REV.mkdir(exist_ok=True)
def sha(x):return hashlib.sha256(x).hexdigest()
def contents(p):return Path(p).read_text()
design=contents(D/'dual-entry-architecture-20261116.md')
previous_lead=contents(D/'review/lead-reviewer/result.md')
filediff=subprocess.run(['git','diff','--','tools/director-runtime-v0/runtime.py',
    'tools/director-runtime-v0/cli.py','tools/director-runtime-v0/tests/test_runtime.py'],
    cwd=ROOT,capture_output=True,text=True,check=True).stdout
assert 'review_shot' in filediff and 'review-shot' in filediff
def get(section):
    return section
frozen='\n\n'.join([
'## USER-APPROVED DUAL-ENTRY PRIORITY\nCanvas Agent inside Canvas main; ChatGPT via Eric as half-automated second formal entry; separate Eric Codex backup only.',
'## DOCUMENT: DUAL ENTRY ARCHITECTURE\n'+design,
'## IMPLEMENTATION: COMPLETE SCOPED GIT DIFF\n'+filediff,
'## APPROVED SOURCE GUARD (EXISTING)\n'+contents(ROOT/'tools/director-runtime-v0/runtime.py').split('    def review_packet(self):',1)[1].split('    def review_shot(self, shot_id):',1)[0],
'## PREVIOUS MAIN DESIGN REVIEW (BEFORE IMPLEMENTATION)\n'+previous_lead,
'## ORIGIN PROBE JSON\n'+contents(D/'config-origin-probe.json'),
'## PREVIOUS DEMONSTRATED MODEL ERROR\nB candidate hash and Stage Shot text hash refer to different objects; cannot compare for equality.',
'## TEST RESULTS\n61 Python unittest tests passed; actual approved B unchanged SHA256=23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7. This is reported by the orchestrator, not an independently reproduced claim by reviewers.'
])
(REV/'frozen-packet.md').write_text(frozen)
manifest={'frozen_sha256':sha(frozen.encode()),'architecture_sha256':sha(design.encode()),
          'scoped_diff_sha256':sha(filediff.encode()),'prior_review_sha256':sha(previous_lead.encode()),
          'status':'postimplementation independent review; no B approval'}
(REV/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
def run(name,model,effort,prompt):
    target=REV/name
    if target.exists():raise RuntimeError('Reviewer already exists: '+name)
    target.mkdir()
    (target/'prompt.md').write_text(prompt)
    t=time.monotonic()
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
         '--sandbox','read-only','--json','-m',model,
         '-c',f'model_reasoning_effort="{effort}"','-c','approval_policy="never"',
         '-c','features.shell_tool=false','-c','web_search="disabled"',
         '-c','project_doc_max_bytes=0','-C',str(target),'-o',str(target/'result.md'),'-']
    with (target/'events.jsonl').open('wb') as out,(target/'stderr.txt').open('wb') as err:
        r=subprocess.run(cmd,input=prompt.encode(),stdout=out,stderr=err,timeout=900)
    info={'name':name,'model':model,'effort':effort,'exit_code':r.returncode,
          'elapsed_seconds':round(time.monotonic()-t,2),
          'prompt_sha256':sha(prompt.encode()),
          'result_sha256':sha((target/'result.md').read_bytes()) if (target/'result.md').exists() else None}
    (target/'run.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
    print('DONE',name,r.returncode,info['elapsed_seconds'],flush=True)
    return info
common="""你是独立审阅 Agent，审计已实现的 WAR-90 试点 Compact Shot View 及新确定的 Canvas Agent 主力、ChatGPT 半自动协作、Eric Codex 备用架构。
只能基于冻结文本/真实代码 diff/回归结果判断。不要运行 shell 或修改文件；不可签署用户 A/B，不可把来源 SHA 与候选 SHA 跨对象比较。
优先找实质缺陷、API 误用、未覆盖的反例和越界的验收断言，不提不必要的新工程系统。
独立输出 P0/P1/P2、证据定位、最小可执行修正或延期、accept/targeted-revision/block/unknown。"""
roles={
 'reviewer-runtime':('gpt-6-astra','medium','重点审阅：review_shot 与 review_packet 之间的真实守门关系、后续语义误读、关联邻镜和来源/阶段缺失、SHA 对象名称、不可变保障、单测缺口、CLI 读写边界。'),
 'reviewer-entry':('gpt-6-luna','medium','重点审阅：Canvas UI 内置 Agent 主力、ChatGPT 经 DCR 半自动协作、独立 Codex 备用，是否诚实区分实测和未来授权；@节点/选区、冲突防护、受控代理、权限隔离/身份/审阅关口。'),
}
with ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(run,n,m,e,common+'\n专项：'+task+'\n=== FROZEN ===\n'+frozen)
             for n,(m,e,task) in roles.items()]
    results=[x.result() for x in as_completed(futures)]
if any(x['exit_code']!=0 or not x['result_sha256'] for x in results):
    print('REVIEW_INCOMPLETE',flush=True);raise SystemExit(2)
notes='\n'.join('### '+n+'\n'+contents(REV/n/'result.md') for n in roles)
lead=('你是这轮 WAR-90 的主审阅 Agent，对 Compact CLI 真实代码与双入口架构完成独立复核。'
      '你必须亲自核对冻结原始 diff、此前主审意见及双方 Reviewer 原文，逐项裁定分歧，不能机械按票数接受。'
      '用户明确 Canvas Agent 主力 + ChatGPT 也能半自动参与，独立 Codex 备用；不能把 Chat 路径排除。'
      '审查当前只读通过是否足以正式上线、权限隔离未证的准入门槛和必须先修的实现 bug/文档歧义。'
      '给出 accept/targeted-revision/block/unknown，必须/可选/延期，并写一份可以对用户直接汇报的当前阶段/测试目的/实测状态。'
      '无需重做前轮测试，不发明批准、不运行 shell。'
      '\n=== FROZEN ===\n'+frozen+'\n=== TWO REVIEWER ORIGINALS ===\n'+notes)
main=run('lead-reviewer','gpt-6-astra','medium',lead)
(REV/'summary.json').write_text(json.dumps({'frozen_sha256':manifest['frozen_sha256'],'reviewers':results,
 'lead':main,'complete':main['exit_code']==0},ensure_ascii=False,indent=2)+'\n')
print('REVIEW_COMPLETE',main['exit_code'],flush=True)

"""Independent review of Canvas Agent native integration; no mutations or approvals."""
from pathlib import Path
import os,subprocess,json,hashlib,time
from concurrent.futures import ThreadPoolExecutor,as_completed
R=Path('/home/sean/projects/canvas-lab/docs/planning/WAR-90/native-agent-integrated-20261115')
OUT=R/'review';OUT.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def content(name):return (R/name).read_text(encoding='utf-8')
# Only launch after the actual native runtime result has finished and been captured.
results=json.loads(content('native-smoke-result.json'))
assert results.get('native_turn_accepted') is True
assert results.get('production_untouched') is True
history=json.loads(content('native-thread-history.json'))
assert history.get('historyReady') is True
source=(Path('/home/sean/projects/canvas-lab/infinite-canvas/canvas-agent/src/server/http.ts').read_text())
source=source[source.index('    app.post("/agent/codex/turn"'):source.index('    /** 将 Codex 写操作串行化')]
frozen=(
'## Proposed architecture\n'+content('next-integration-plan.md')+
'\n## Native test result JSON\n'+json.dumps(results,ensure_ascii=False,indent=2)+
'\n## Historical native thread first run\n'+json.dumps(json.loads(content('native-smoke-phase1.json')),ensure_ascii=False,indent=2)+
'\n## Full native final messages and tool activity summaries\n'+
json.dumps([{'role':m.get('role'),'title':m.get('title'),'text':str(m.get('text',''))[:3200],
             'detail':str(m.get('detail',''))[:1000]}
            for m in history.get('messages',[])],ensure_ascii=False,indent=2)+
'\n## Source of native HTTP turn endpoint\n'+source+
'\n## Director Skill entry\n'+Path('/home/sean/projects/canvas-lab/docs/planning/WAR-89/director-skill-v0-candidate/SKILL.md').read_text()+
'\n## Frozen latest user stance\nThe user answered no current Shot02 changes, requested follow-on work and required lead agent multi-agent review for complex logic/design. Original B unchanged. No media and no production changes authorized.\n'
)
(OUT/'frozen-review-packet.md').write_text(frozen)
manifest={'frozen_sha256':sha(frozen.encode()),'B_state_sha256':'23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7',
          'purpose':'review native Canvas Agent integration, not user A/B approval','read_only':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
def run(name,model,effort,instructions):
 d=OUT/name
 if d.exists():raise RuntimeError('Already reviewed: '+name)
 d.mkdir()
 prompt=instructions+'\n\n--- FROZEN EVIDENCE ---\n'+frozen
 (d/'prompt.md').write_text(prompt)
 cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json',
      '-m',model,'-c',f'model_reasoning_effort="{effort}"','-c','approval_policy="never"',
      '-c','features.shell_tool=false','-c','project_doc_max_bytes=0',
      '-C',str(d),'-o',str(d/'result.md'),'-']
 t=time.monotonic()
 with (d/'events.jsonl').open('wb') as out,(d/'stderr.txt').open('wb') as err:
  p=subprocess.run(cmd,input=prompt.encode(),stdout=out,stderr=err,timeout=900)
 data={'role':name,'model':model,'effort':effort,'returncode':p.returncode,'seconds':round(time.monotonic()-t,2),
       'prompt_sha256':sha(prompt.encode()),
       'result_sha256':sha((d/'result.md').read_bytes()) if (d/'result.md').exists() else None}
 (d/'run.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('REVIEW',name,p.returncode,data['seconds'],flush=True)
 return data
common=('你是独立审阅 Agent。审阅的是 WAR-90 内置 Canvas Agent 集成实验与下一步方案，非生成器，不能修改文件、执行工具或自行签署 A/B。'
        '严格区分真实 native Thread 接受、实际 Skill 读取、MCP 调用成功、Runtime CLI 只读调用、Runtime 修改提交尚未发生、生产安装尚未发生。'
        '对未完成/不可信证据不得自动判通过；指明最小阻塞，避免另建导演 Agent、HTTP bridge、重复原 Skill。'
        '回答简明分级 P0/P1/P2，源证据定位及建议。')
roles={
 'reviewer-integration':('gpt-6-luna','medium','重点：唯一导演 Agent + 专业 Skill + 工程 Runtime + Canvas MCP 的角色边界、上下文噪声、用户可理解阶段/测试目的、WAR-90 与 WAR-37/35 范围。'),
 'reviewer-engineering':('gpt-6-astra','medium','重点：实际原生 turn 工具日志、native approval 规则、Skill path 与变更迁移、隔离 HOME 与 inherited MCP、只读 Runtime 是否真被调用、未知项及可靠停止/失败回滚。'),
}
with ThreadPoolExecutor(max_workers=2) as pool:
 fs=[pool.submit(run,n,model,effort,common+'本次专项：'+special)
     for n,(model,effort,special) in roles.items()]
 rs=[f.result() for f in as_completed(fs)]
if any(x['returncode']!=0 or not x['result_sha256'] for x in rs):
 print('INCOMPLETE_REVIEW',flush=True);raise SystemExit(2)
reports='\n'.join('### '+n+'\n'+(OUT/n/'result.md').read_text() for n in roles)
lead=('你是主审阅 Agent，由你主持 Canvas Lab WAR-90 的独立多 Agent 架构/实现审阅。'
      '必须独立核对冻结原始证据和两个相互隔离 Reviewer 原始意见，不能机械投票。'
      '如有分歧逐项裁定，严禁把 native read-only 当候选修订通过，不得宣称生产安装。'
      '指出现有原生调用验证的真实里程碑和剩余风险，特别是全局 MCP 污染/skill path/CLI 与未证审批。'
      '输出 accept|targeted-revision|block|unknown，必须/可选/延期与下一步最小可执行动作，中文 700～1300 字。'
      '若本轮只读无用户修改，也不要求重新制造反馈；永不签 A/B。')
main=run('lead-reviewer','gpt-6-astra','medium',lead+'\n=== REVIEWERS ORIGINAL REPORTS ===\n'+reports)
(OUT/'summary.json').write_text(json.dumps({'frozen_sha256':manifest['frozen_sha256'],
 'reviewers':rs,'lead':main,'complete':main['returncode']==0},ensure_ascii=False,indent=2)+'\n')
print('LEAD_COMPLETE',main['returncode'],flush=True)

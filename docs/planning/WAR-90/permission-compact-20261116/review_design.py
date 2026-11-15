"""Multi-agent independent design review before any Runtime implementation."""
from pathlib import Path
import hashlib,json,time,subprocess,os
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/permission-compact-20261116'
REV=OUT/'review';REV.mkdir(exist_ok=True)
def shab(data):return hashlib.sha256(data).hexdigest()
def read(relative):return (ROOT/relative).read_text()
design=(OUT/'design-proposal-v0.md').read_text()
probe=(OUT/'config-origin-probe.json').read_text()
src=read('infinite-canvas/canvas-agent/src/agent/codex-client.ts')
runtime=read('tools/director-runtime-v0/runtime.py')
p=[
('CANDIDATE DESIGN',design),
('REAL CODEX CONFIG ORIGIN PROBE JSON',probe),
('EXISTING CANVAS CODEX START AND MCP CONFIG',src[src.index('    static async start('):src.index('    /** 创建新的 Codex 线程')]+src[src.index('function codexConfig('):src.index('function skillDraftThreadSettings(')]),
('EXISTING RUNTIME FULL APPROVED READ GUARD',runtime[runtime.index('    def review_packet('):runtime.index('    def status(',runtime.index('    def review_packet('))]),
('PRIOR LEAD REVIEW',read('docs/planning/WAR-90/native-agent-integrated-20261115/review/lead-reviewer/result.md'))
]
frozen='\n\n'.join('## '+n+'\n'+t for n,t in p)
(REV/'frozen-packet.md').write_text(frozen)
manifest={'frozen_sha256':shab(frozen.encode()),'design_sha256':shab(design.encode()),
          'roles':['reviewer-security','reviewer-director','lead-reviewer'],'formal_approval':False}
(REV/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
def run(name,model,effort,prompt):
    d=REV/name
    if d.exists():raise RuntimeError('Review dir exists: '+name)
    d.mkdir()
    (d/'prompt.md').write_text(prompt)
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
         '--sandbox','read-only','--json','-m',model,
         '-c',f'model_reasoning_effort="{effort}"',
         '-c','approval_policy="never"','-c','features.shell_tool=false',
         '-c','project_doc_max_bytes=0','-c','web_search="disabled"',
         '-C',str(d),'-o',str(d/'result.md'),'-']
    ts=time.monotonic()
    with (d/'events.jsonl').open('wb') as ev,(d/'stderr.txt').open('wb') as err:
        r=subprocess.run(cmd,input=prompt.encode(),stdout=ev,stderr=err,timeout=900)
    result={'role':name,'model':model,'effort':effort,'exit_code':r.returncode,'seconds':round(time.monotonic()-ts,1),
            'prompt_sha256':shab(prompt.encode()),
            'result_sha256':shab((d/'result.md').read_bytes()) if (d/'result.md').exists() else None}
    (d/'run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('REVIEW',name,r.returncode,result['seconds'],flush=True)
    return result
common="""你是独立 Reviewer，专审 WAR-90 在隔离测试环境中的 Permission Isolation 和 Compact Shot View 设计候选。请依据冻结源码/实验记录，不做任何文件、网络或工具操作，不生成媒体，也不为用户批准 B。
严禁把 CODEX_HOME clean config/read 直接等同于工具审批、禁止把已批准候选 SHA 与阶段纯文本 SHA 比较。重点查找可复现的隐藏权限/回滚/上下文错误，不先发明正式 WAR-35 schema 或平行 Agent。
须给出 accept/targeted-revision/block/unknown，P0/P1/P2，证据定位、具体最小修订及尚未证项。"""
roles={
'reviewer-security':('gpt-6-astra','medium','专项：native app-server 工具审批事件类型 vs MCP 默认 approval；令拒绝反例可实测；CODEX_HOME isolation 与认证/权限的安全边界；配置原点和 thread scope；fail-closed 过宽或危险的假设。'),
'reviewer-director':('gpt-6-luna','medium','专项：Compact Shot View 是否为单镜头导演判断提供充分的窗口、角色知情和邻镜条件；视图不能替代 Resume 或正式审阅。检查 SHA 对象、源依据与能力标记的歧义、伪 Schema 风险。'),
}
with ThreadPoolExecutor(max_workers=2) as pool:
 fs=[pool.submit(run,name,model,effort,common+'\n专项：'+topic+'\n=== FROZEN ===\n'+frozen)
     for name,(model,effort,topic) in roles.items()]
 independent=[f.result() for f in as_completed(fs)]
if any(r['exit_code']!=0 or not r['result_sha256'] for r in independent):
 print('REVIEW_BLOCKED',flush=True);raise SystemExit(2)
originals='\n'.join('### '+name+'\n'+(REV/name/'result.md').read_text() for name in roles)
lead=("""你是主审阅 Agent，主持本轮 WAR-90 的双 Reviewer 专业/工程方案审阅。必须亲自核对冻结设计、Codex 配置探针以及现有源码，再读两份相互隔离的 Reviewer 原报告；不能机械投票。
裁定 A2/A3 真实审批拒绝的可行性，尤其检查 MCP 工具请求是否属于现有 codex_approval 所支持的类型。对 Compact View 做最低充分性审计，判断是否应该先实现试点 CLI / 必须怎样补源上下文。明确 accept/targeted-revision/block/unknown，必须/可选/延期及允许 ChatGPT 实施的最小下一步；不写文件，不签 A/B，不假报通过。中文 800-1500 字。"""+'\n=== FROZEN ===\n'+frozen+'\n=== TWO REVIEWERS ORIGINAL ===\n'+originals)
main=run('lead-reviewer','gpt-6-astra','medium',lead)
(REV/'summary.json').write_text(json.dumps({'manifest':manifest,'reviewers':independent,'lead':main,
 'complete':main['exit_code']==0},ensure_ascii=False,indent=2)+'\n')
print('LEAD_DONE',main['exit_code'],flush=True)

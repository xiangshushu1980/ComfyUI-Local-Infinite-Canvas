"""Independent reviewers, then lead decision; all model calls read-only, frozen packet."""
import json,hashlib,subprocess,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path('/home/sean/projects/canvas-lab')
SRC=ROOT/'docs/planning/WAR-90/main-entry-preflight-20261116'
REVIEW=SRC/'review'
REVIEW.mkdir(exist_ok=True)
def sha(x):return hashlib.sha256(x).hexdigest()
def grab(rel):return (ROOT/rel).read_text(encoding='utf8')
def section(name,body):return '## '+name+'\n'+body+'\n'
x=grab('infinite-canvas/canvas-agent/src/skills/store.ts')
session=grab('infinite-canvas/canvas-agent/src/canvas/session.ts')
server=grab('infinite-canvas/canvas-agent/src/server/http.ts')
packet=(
 section('Current candidate and decisions',grab('docs/planning/WAR-90/main-entry-preflight-20261116/README.md'))+
 section('Seven-file native exact result',grab('docs/planning/WAR-90/main-entry-preflight-20261116/codex-skill-lifecycle-result.json'))+
 section('Current source tree file validation',grab('docs/planning/WAR-90/permission-compact-20261116/director-skill-source-sha256.json') if (ROOT/'docs/planning/WAR-90/permission-compact-20261116/director-skill-source-sha256.json').exists() else 'Not separately available; see native manifest')+
 section('Chat pure-data gate',grab('docs/planning/WAR-90/main-entry-preflight-20261116/chat_read_preflight.py'))+
 section('SkillStore entry/update/revision implementation',
   x[x.index('export class SkillStore'):x.index('    private mutate')]+ '\n'+x[x.index('function revision('):x.index('async function ensurePlainDirectory(')])+
 section('CanvasSession target routing implementation',
   session[session.index('    private get canvasState()'):session.index('    /** 返回 Canvas Agent 当前连接状态。')]+
   session[session.index('    async callTool('):session.index('    /** 将当前 turn 的附件转换为画布图片节点。')])+
 section('API tool route',server[server.index('    app.post("/api/tools"'):server.index('    app.get("/agent/codex/models"')])+
 section('Agent targeted unit tests',grab('docs/planning/WAR-90/main-entry-preflight-20261116/native-agent-targeted-tests.log')[-1500:])+
 section('Prior architecture direction',grab('docs/planning/WAR-90/permission-compact-20261116/dual-entry-architecture-20261116.md'))
)
(REVIEW/'frozen-packet.md').write_text(packet)
manifest={'packet_sha256':sha(packet.encode()),'report_scope':'single Canvas native primary + Chat alternate preflight; no production install',
          'original_B_state_sha256':'23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7',
          'not_authorized':['production service start','production Skill install','media','B approval','production Canvas mutations']}
(REVIEW/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
def run(name,model,effort,prompt):
    out=REVIEW/name
    out.mkdir(exist_ok=False)
    (out/'prompt.md').write_text(prompt)
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
         '--sandbox','read-only','--json','-m',model,
         '-c',f'model_reasoning_effort="{effort}"',
         '-c','approval_policy="never"','-c','features.shell_tool=false',
         '-c','project_doc_max_bytes=0','-C',str(out),'-o',str(out/'result.md'),'-']
    t=time.monotonic()
    with (out/'events.jsonl').open('wb') as events,(out/'stderr.txt').open('wb') as err:
        p=subprocess.run(cmd,input=prompt.encode(),stdout=events,stderr=err,timeout=900)
    res={'name':name,'model':model,'effort':effort,'return_code':p.returncode,
         'seconds':round(time.monotonic()-t,2),
         'prompt_sha256':sha(prompt.encode()),
         'result_sha256':sha((out/'result.md').read_bytes()) if (out/'result.md').exists() else None}
    (out/'run.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
    print('REVIEW_DONE',name,p.returncode,res['seconds'],flush=True)
    return res
base=('你是 Canvas Lab WAR-90 正式接入预检的独立 Reviewer。仅基于完整冻结包和源码片段进行只读审阅，不调用工具，不改文件/画布/配置/Linear，不批准 A/B。'
'必须区别原生 Codex skills/list 已通过与 Canvas Agent HTTP 路由没测、生产安装未发生；严格识别 Chat 只读 gate 和真正原子写权限之间的边界。'
'给出 accept/targeted-revision/block/unknown，P0/P1/P2 问题、可复现证据、最低修改、后续仍未知，不要自动扩建新 Agent。')
roles={
'reviewer-skill-lifecycle':('gpt-6-luna','medium','重点审计多文件 Skill 的发现/升级/回退、SkillStore revision 只覆盖两文件、active turn、工作区路径及候选发布版本治理。'),
'reviewer-canvas-ownership':('gpt-6-astra','medium','重点审计 Client/Project/Node/Shot 绑定，单用户多标签与 Chat API routing，chat_read_preflight 是否错误授予写入，MCP permission 与工具权限假设。'),
}
with ThreadPoolExecutor(max_workers=2) as pool:
    tasks=[pool.submit(run,n,m,e,base+'专项：'+special+'\n\n'+packet) for n,(m,e,special) in roles.items()]
    rev=[f.result() for f in as_completed(tasks)]
if any(v['return_code']!=0 or not v['result_sha256'] for v in rev):
    print('INDEPENDENT_REVIEW_INCOMPLETE',flush=True);raise SystemExit(2)
reports='\n\n'.join('### '+n+'\n'+(REVIEW/n/'result.md').read_text() for n in roles)
lead=('你是 WAR-90 的主审阅 Agent，主持独立方案审阅。先独立核对冻结证据，随后核对两个 Reviewer 原始报告，'
      '逐项解决分歧，拒绝缺乏源证据的主张，不能用投票替代核证。'
      '输出 accept/targeted-revision/block/unknown、必须/建议/延期及可直接实施的下一阶段。'
      '务必判断是否可以仅保存预检结果继续等待正式用户授权，是否有当前不应保留的安全错误。'
      '指出如何将 Canvas Agent 主入口与 Chat 半自动入口共享 Skill/CLI，但避免绕过权限和误选画布。'
      '不声称生产 Skill 安装完成或真实 MCP 权限通过；不签 B。中文 700-1400 字。\n\n'
      +'=== FROZEN ===\n'+packet+'\n=== INDEPENDENT REPORTS ===\n'+reports)
main=run('lead-reviewer','gpt-6-astra','medium',lead)
(REVIEW/'summary.json').write_text(json.dumps({'manifest':manifest,'reviewers':rev,'lead':main,
    'complete':main['return_code']==0},ensure_ascii=False,indent=2)+'\n')
print('LEAD_COMPLETE',main['return_code'],flush=True)

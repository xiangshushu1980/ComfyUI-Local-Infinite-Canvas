"""Genuine independent preflight reviewers then lead; no media, user approval, or repo mutation."""
from pathlib import Path
import hashlib,subprocess,os,shutil,tempfile,json,time
from concurrent.futures import ThreadPoolExecutor,as_completed
R=Path('/home/sean/projects/canvas-lab/docs/planning/WAR-90/human-feedback-preflight-20261115')
packet=(R/'frozen-packet.md').read_text()
expected=json.loads((R/'manifest.json').read_text())['frozen_sha256']
assert hashlib.sha256(packet.encode()).hexdigest()==expected
def invoke(name,model,effort,prompt):
    dest=R/name
    if dest.exists(): raise RuntimeError('Reviewer directory already exists: '+str(dest))
    dest.mkdir()
    (dest/'prompt.md').write_text(prompt)
    home=Path(tempfile.mkdtemp(prefix='.auth-',dir=dest))
    start=time.monotonic()
    try:
        auth=Path('/home/sean/.codex/auth.json')
        if auth.exists():
            (home/'auth.json').write_bytes(auth.read_bytes())
            (home/'auth.json').chmod(0o600)
        cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
             '--sandbox','read-only','--json','-m',model,
             '-c',f'model_reasoning_effort="{effort}"',
             '-c','approval_policy="never"','-c','features.shell_tool=false',
             '-c','web_search="disabled"','-c','project_doc_max_bytes=0',
             '-C',str(dest),'-o',str(dest/'result.md'),'-']
        with (dest/'events.jsonl').open('wb') as output,(dest/'stderr.txt').open('wb') as errors:
            res=subprocess.run(cmd,input=prompt.encode(),stdout=output,stderr=errors,
                               env=dict(os.environ,CODEX_HOME=str(home)),timeout=900)
        summary={'name':name,'model':model,'effort':effort,'exit_code':res.returncode,
                 'duration_seconds':round(time.monotonic()-start,1),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                 'result_sha256':hashlib.sha256((dest/'result.md').read_bytes()).hexdigest() if (dest/'result.md').exists() else None}
        (dest/'run.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
        print('REVIEW_DONE',name,res.returncode,summary['duration_seconds'],flush=True)
        return summary
    finally:shutil.rmtree(home,ignore_errors=True)
common="""你是 WAR-90 的隔离独立审阅者。审阅的是尚未执行的『真人反馈采集测试方案』而不是现有 B 的专业质量、也不是生成导演候选。仅使用提供的冻结证据。绝不可自行创建用户修改意见，不得声称真人已审阅，不运行媒体/Canvas/工具、不修改文件。根据事实边界和测试目的做最小阻塞清单。必须区分 ①工程可证 ②专业待实测 ③真人必须提供的输入 ④WAR-37 正式 UI scope。指出具体证据片段与反例；输出 P0/P1/P2 及可执行的最小方案，禁止为测试扩展新 HTTP bridge。审阅报告控制在 500～1100 中文字。"""
roles={
'reviewer-human':('gpt-6-luna','medium','重点审阅：给人看的 Shot02 材料是否能让普通审阅者真正指出一条局部修改，不误把审阅目标写成测试答案；反馈来自 Chat 还是 Canvas UI 应如何标识；如果缺用户回复现在能做什么，哪些必须停。'),
'reviewer-engineer':('gpt-6-astra','medium','重点审阅：新隔离浏览器/Agent 与生产画布的隔离可信度；B/Source/Shot/selection绑定；信任边界和人类反馈真实性；CLI prepare/submit 过期/二次模型调用；测试证据、失败停点、回滚清理；必要最小技术修改。'),
}
with ThreadPoolExecutor(max_workers=2) as pool:
    fs=[pool.submit(invoke,n,m,e,common+'\n专项:'+topic+'\n=== FROZEN ===\n'+packet) for n,(m,e,topic) in roles.items()]
    reports=[f.result() for f in as_completed(fs)]
if any(r['exit_code']!=0 or not r['result_sha256'] for r in reports):
    print('REVIEW_BLOCKED: reviewer incomplete',flush=True); raise SystemExit(2)
lead="""你是 Canvas Lab WAR-90 的主审阅 Agent（审阅主持人）。要求：亲自核对同一冻结方案与已批准 B 权威，阅读 2 份相互隔离的 Reviewer 原文，不机械数票，驳回脱离来源或把未来 UI 缺口算当前 pilot P0 的主张。跨层把关：在未提供真实用户修改意见时，是否适合先创建用户可见的持久测试 Canvas，还是优先通过 Chat 展示 Shot02、收取实际意见后再隔离 Canvas 复演？明确授权边界、浏览器 Agent 稳定性与失败时停止策略。请给出 accept / targeted-revision / block / unknown；必须/可选/延期；一份人可读测试目的与阶段报告模板；下一步可执行最小任务清单；审阅是否产生正式 A/B：否。对每个 reviewer 关键结论说明采纳与否。不要代替真人签 B，不要虚构实测。"""+'\n=== FROZEN ===\n'+packet+'\n=== INDEPENDENT REVIEW ORIGINALS ===\n'+'\n'.join('## '+n+'\n'+(R/n/'result.md').read_text() for n in roles)
head=invoke('lead-reviewer','gpt-6-astra','medium',lead)
(R/'summary.json').write_text(json.dumps({'frozen_sha256':expected,'reviewers':reports,'lead':head,'complete':head['exit_code']==0},ensure_ascii=False,indent=2)+'\n')
print('PREFLIGHT_REVIEW_COMPLETE',head['exit_code'],flush=True)

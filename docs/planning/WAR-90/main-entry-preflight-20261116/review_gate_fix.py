"""Targeted independent review of the P1 gate fixes; no production operations."""
from pathlib import Path
import hashlib,subprocess,time,json
R=Path('/home/sean/projects/canvas-lab/docs/planning/WAR-90/main-entry-preflight-20261116')
D=R/'review-gate-fix';D.mkdir(exist_ok=True)
def sha(x):return hashlib.sha256(x).hexdigest()
packet=('## Gate source\n'+(R/'chat_read_preflight.py').read_text()+
 '\n## New unit tests\n'+(R/'test_chat_read_preflight.py').read_text()+
 '\n## Test result\n'+(R/'chat-preflight-tests.log').read_text()+
 '\n## Real B projection + explicitly synthetic Canvas fixture result\n'+(R/'actual-B-synthetic-canvas-preflight.json').read_text()+
 '\n## Original independent review P1 problems\n'+(R/'review/reviewer-canvas-ownership/result.md').read_text()+
 '\n## Main review\n'+(R/'review/lead-reviewer/result.md').read_text())
(D/'frozen-fix-packet.md').write_text(packet)
(D/'manifest.json').write_text(json.dumps({'packet_sha256':sha(packet.encode()),
 'scope':'postreview P1 pure-data gate, not HTTP approval or production install'},ensure_ascii=False,indent=2)+'\n')
def run(name,model,effort,prompt):
 folder=D/name;folder.mkdir()
 (folder/'prompt.md').write_text(prompt)
 args=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
       '--sandbox','read-only','--json','-m',model,'-c',f'model_reasoning_effort="{effort}"',
       '-c','approval_policy="never"','-c','features.shell_tool=false',
       '-c','project_doc_max_bytes=0','-C',str(folder),'-o',str(folder/'result.md'),'-']
 started=time.monotonic()
 with (folder/'events.jsonl').open('wb') as e,(folder/'stderr.txt').open('wb') as err:
  p=subprocess.run(args,input=prompt.encode(),stdout=e,stderr=err,timeout=700)
 meta={'model':model,'effort':effort,'returncode':p.returncode,'seconds':round(time.monotonic()-started,2),
       'prompt_sha':sha(prompt.encode()),'result_sha':sha((folder/'result.md').read_bytes()) if (folder/'result.md').exists() else None}
 (folder/'run.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print('REVIEW_GATE',name,p.returncode,flush=True)
 return meta
prompt=('你是独立 Reviewer，仅审阅 Canvas Lab WAR-90 Chat 只读 Gate 的定向 P1 修复。'
'请用冻结代码验证是否阻止了 B/SHA 双缺失误放行、是否实算 Source/Shot 全文 SHA、是否只断言输入标识一致并明确 Node→Shot/快照关联未验证、能否避免意外写入授权。'
'指出实质性漏洞、缺陷风险和不足的测试。不得调用工具、修改文件、扩大生产权限或假冒 B。中文简明分级 accept/targeted-revision/block/unknown。\n\n'+packet)
first=run('independent','gpt-6-luna','medium',prompt)
if first['returncode'] or not first['result_sha']:raise SystemExit(2)
lead=('你是主审阅 Agent，独立核对冻结修订代码及测试，随后结合 Reviewer 原始结果裁定 P1 是否关闭。'
      '不能把纯数据测试归结为真实 Canvas Agent HTTP 的权限/竞态通过；不批准 A/B。'
      '如果发现仍有具体 P1，请给出最小修正。输出 accept/targeted-revision/block/unknown 并区分离线修订通过与生产集成准入。\n\n'
      +packet+'\n\n## Independent reviewer result\n'+(D/'independent/result.md').read_text())
second=run('lead','gpt-6-astra','medium',lead)
(D/'summary.json').write_text(json.dumps({'reviewer':first,'lead':second,
'complete':first['returncode']==0 and second['returncode']==0},ensure_ascii=False,indent=2)+'\n')
print('GATE_FIX_COMPLETE',second['returncode'],flush=True)

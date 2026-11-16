#!/usr/bin/env python3
"""Repair ONLY a named new display node via the existing native Canvas Agent.
Never create additional nodes; no Chat HTTP writes. Exit nonzero if exact SHA not matched.
"""
import hashlib,json,sys,time,traceback
from pathlib import Path
import requests
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/live-b-projection-20261116'
audit=OUT/'projection-final-audit.json'
if audit.is_file() and __import__('json').loads(audit.read_text()).get('success') is True:
    raise SystemExit('Projection is already audited PASS; refusing further model text repair')
sys.path.insert(0,str(OUT))
from prepare_projection import payload
SHOT=sys.argv[1] if len(sys.argv)>1 else 'Shot01'
assert SHOT in ('Shot01','Shot02','Shot03','Shot04')
PROJECT='mrEXrMQoY-2ef3U6NsHtj'
CLIENT='04wsd618VDFdUWb74oZZI'
EXISTING={'Shot01':'text-1794823805462-0','Shot02':'text-1794823805462-1',
          'Shot03':'text-1794823805462-2','Shot04':'text-1794823805462-3'}
OLD={'text-1793372915213-2q1pb','image-1793372917582-2pevr','audio-1793372920916-z4dgp'}
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
url=cfg['url'].rstrip('/')
res={'shot':SHOT,'targetNodeId':EXISTING[SHOT],'no_chat_http_writes':True,'no_new_nodes':True}
def chk(ok,msg):
 if not ok:raise RuntimeError(msg)
def save(): (OUT/('repair-'+SHOT+'.json')).write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
def health():return s.get(url+'/health',timeout=7).json()
def read():
 r=s.post(url+'/api/tools',json={'name':'canvas_get_state','input':{}},timeout=20)
 chk(r.ok and r.json().get('ok') is True,'Canvas read failed')
 return r.json()['result']
try:
 items=payload()['input']['items']
 item=next(x for x in items if SHOT in x['title'])
 desired=item['text']
 expected_sha=hashlib.sha256(desired.encode()).hexdigest()
 b=read()
 h=health()
 chk(h.get('clients')==1 and h.get('hasCanvas') and not h.get('codexBusy'),'Canvas not single/idle')
 chk(b.get('projectId')==PROJECT and b.get('title')=='无限画布 1' and b.get('clientId')==CLIENT,'Project/client mismatch')
 chk({n['id'] for n in b['nodes']}==OLD|set(EXISTING.values()),'Node set changed')
 before={n['id']:n for n in b['nodes']}
 chk(before[EXISTING[SHOT]]['title']==item['title'],'Target title mismatch')
 res['expected_sha256']=expected_sha
 res['before_text_sha256']=hashlib.sha256(str((before[EXISTING[SHOT]].get('metadata') or {}).get('content') or '').encode()).hexdigest()
 if res['before_text_sha256']==expected_sha:
  res['already_exact']=True;res['passed']=True
 else:
  work=s.get(url+'/agent/codex/workspace',timeout=20).json()
  c=work.get('conversation') or {}
  chk(c.get('status') in ('ready','warning') and c.get('threadId'),'Codex not ready')
  skill=s.get(url+'/agent/codex/skills?forceReload=1',timeout=45).json()
  skills=[x for x in skill.get('data',[]) if x.get('name')=='director-skill-v0-candidate' and x.get('enabled')]
  chk(len(skills)==1,'Skill missing')
  prompt=(
   '用户已授权新增已批准 B 的四个镜头展示节点。四个节点已经创建，但原生模型转写长正文时错误地截断。'
   '这次只修复现有四个节点的内容，不新增或删除，不动原有三个空节点，不运行生成或修改批准 B。'
   '请不要再将长文本复制到 MCP 参数，避免省略。'
   '请在当前 Canvas Agent 原生 Codex turn 内仅使用终端执行以下确定性本地帮助脚本一次：'
   'python3 /home/sean/projects/canvas-lab/docs/planning/WAR-90/live-b-projection-20261116/apply_exact_projection.py --apply'
   '。它仅在当前 Agent turn 正在执行、画布唯一连接、项目及全部七节点 ID/来源 SHA 完全一致时才允许一次批量内容更新。'
   '数据直接来自 Eric 已批准 B，不经模型复制。它不创建节点、不更新原三个节点、不操作媒体，不新建常驻 Agent。'
   '成功后可读取画布核实；失败后立即说明，不重复执行。'
  )
  params={'clientId':CLIENT,'threadId':c['threadId'],
    'conversationId':c.get('conversationId',''),'expectedRevision':c.get('revision',0),
    'prompt':prompt,
    'messageText':'修复已创建展示节点 '+SHOT+' 的省略正文（只更新该节点，内容必须与批准 B 完全一致）',
    'permissionMode':'automatic','model':'gpt-6-luna','effort':'medium',
    'skill':{'name':skills[0]['name'],'path':skills[0]['path']}}
  t=time.monotonic()
  r=s.post(url+'/agent/codex/turn',json=params,timeout=90)
  res['turn_http_code']=r.status_code
  chk(r.ok,'Native turn rejected')
  res['native_turn_accepted']=True;save()
  saw=False
  for _ in range(170):
   time.sleep(.7)
   h=health()
   saw=saw or bool(h.get('codexBusy'))
   if saw and not h.get('codexBusy'):break
  res['elapsed_s']=round(time.monotonic()-t,1)
  res['turn_settled']=bool(saw and not h.get('codexBusy'))
  if not res['turn_settled']:
   try:res['interrupt_code']=s.post(url+'/agent/codex/interrupt',json={'threadId':c['threadId']},timeout=12).status_code
   except Exception as e:res['interrupt_error']=type(e).__name__
  after=read() if not health().get('codexBusy') else None
  if after:
   nodes={n['id']:n for n in after['nodes']}
   res['node_count_after']=len(nodes)
   res['original_node_ids_kept']=OLD.issubset(nodes)
   res['after_node_id_preserved']=EXISTING[SHOT] in nodes
   res['after_text_sha256']=hashlib.sha256(str((nodes[EXISTING[SHOT]].get('metadata') or {}).get('content') or '').encode()).hexdigest() if EXISTING[SHOT] in nodes else None
   res['exact_text']=res['after_text_sha256']==expected_sha
   res['passed']=bool(res['turn_settled'] and res['exact_text'] and
     after.get('projectId')==PROJECT and len(nodes)==7 and res['original_node_ids_kept'])
except Exception as e:
 res['error_type']=type(e).__name__;res['error_message']=str(e)[:400]
 traceback.print_exc()
finally:
 save()
 print('REPAIR_RESULT',json.dumps({k:res.get(k) for k in ('shot','turn_http_code','elapsed_s','turn_settled','exact_text','node_count_after','passed','error_type','error_message')},ensure_ascii=False),flush=True)
 if not res.get('passed'):sys.exit(2)

#!/usr/bin/env python3
"""Trigger exactly one native read-only Director Skill review on canonical Shot02.
No Canvas write operations, no GPU, no H3, no Linear modification.
"""
import json,requests,time,sys
from pathlib import Path
OUT=Path('/home/sean/projects/canvas-lab/docs/planning/WAR-90/canonical-display-20261116')
P=OUT/'shot02-native-review-audit.json'
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
url=cfg['url'].rstrip('/')
audit={'purpose':'read-only Shot02 interaction using native Canvas Agent + Director Skill',
       'expected_project':'2FwEbySI5PYe7d6BL4pES',
       'expected_client':'jeUNwaV-t0QApaAKC2pMh',
       'expected_shot2_node':'text-1794832120997-1',
       'accepted':False,'done':False}
def check(x,msg):
 if not x:raise RuntimeError(msg)
def save():P.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
def health():return s.get(url+'/health',timeout=7).json()
def state():
 r=s.post(url+'/api/tools',json={'name':'canvas_get_state','input':{}},timeout=18)
 check(r.ok and r.json().get('ok'),'Read Canvas failed')
 return r.json()['result']
try:
 check(not P.exists(),'Native Shot02 review was already started; refusing duplicate')
 h=health(); st=state()
 check(h.get('clients')==1 and h.get('codexBusy') is False and h.get('hasCanvas'),'Not single idle canvas')
 check(st.get('projectId')==audit['expected_project'] and st.get('clientId')==audit['expected_client'],'Wrong canvas')
 check(len(st.get('nodes') or [])==4 and st.get('selectedNodeIds')==[audit['expected_shot2_node']],'Shot02 not selected')
 check(any(n.get('id')==audit['expected_shot2_node'] and 'Shot02' in n.get('title','') for n in st['nodes']),'Shot02 mapping missing')
 w=s.get(url+'/agent/codex/workspace',timeout=20).json()
 c=w.get('conversation') or {}
 check(c.get('status')=='ready' and c.get('threadId'),'Native Codex not ready')
 skills=s.get(url+'/agent/codex/skills?forceReload=1',timeout=40).json().get('data') or []
 matched=[x for x in skills if x.get('name')=='director-skill-v0-candidate' and x.get('enabled')]
 check(len(matched)==1,'Director Skill unavailable')
 prompt=(
  '请使用当前启用的 director-skill-v0-candidate 对 D《错过的钥匙》已批准B的 Shot02 进行一次真实、只读、短篇导演交互审阅。'
  '当前唯一允许目标是 canvas.localhost 的真实画布：项目ID 2FwEbySI5PYe7d6BL4pES、标题“无限画布 1”、'
  '已选中真实节点ID text-1794832120997-1（Shot02）。'
  '你必须先通过 infinite-canvas MCP 的 canvas_get_state、canvas_get_selection 确认 projectId 和已选镜头映射；'
  '有任何不符立即停止、不动节点。'
  '之后从 Eric Director Runtime 只读 CLI 读取源方案：'
  'python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-shot '
  '--workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2 --shot-id Shot02。'
  '请依据真实 Shot Plan/Review 信息，简明回答：'
  '①观众在 Shot02 应当首先注意什么，'
  '②钥匙的显露、人物遮挡与空间连续性最关键的两个表达风险，'
  '③文字画布现在能证明什么、哪些视觉效果尚未实际验证。'
  '给出一项最有判别力的用户交互审阅问题，然后停在用户确认点。'
  '不要创建/修改/删除任何节点，不要生成媒体，不要运行 Gateway/H3/ComfyUI/Blender，'
  '不生成或签批新的 B，不访问/更新 Linear，也不要自行进行下一步。'
 )
 params={'clientId':audit['expected_client'],'threadId':c['threadId'],
         'conversationId':c.get('conversationId',''),'expectedRevision':c.get('revision',0),
         'prompt':prompt,'messageText':'在规范画布中只读审阅已选中的 Shot02：验证观看目标、钥匙显露与空间连续性；不修改、不生成',
         'permissionMode':'automatic','model':'gpt-6-luna','effort':'medium',
         'skill':{'name':matched[0]['name'],'path':matched[0]['path']}}
 audit['preflight_pass']=True
 audit['turn_submit_called']=True
 save()
 start=time.monotonic()
 response=s.post(url+'/agent/codex/turn',json=params,timeout=90)
 audit['turn_http_code']=response.status_code
 check(response.ok,'Native model turn rejected')
 audit['accepted']=True
 save()
 busy=False
 for _ in range(200):
  time.sleep(.8)
  h=health()
  busy=busy or bool(h.get('codexBusy'))
  if busy and not h.get('codexBusy'):break
 audit['duration_s']=round(time.monotonic()-start,1)
 audit['done']=bool(busy and not h.get('codexBusy'))
 audit['final_agent_conversation_status']=(h.get('conversation') or {}).get('status')
 if h.get('codexBusy'):
  audit['still_busy']=True
 if not h.get('codexBusy'):
  after=state()
  audit['post_canvas']={'project_id':after.get('projectId'),'nodes':len(after.get('nodes') or []),
                        'selected_ids':after.get('selectedNodeIds')}
  audit['no_canvas_count_or_selection_change']=after.get('projectId')==audit['expected_project'] and len(after.get('nodes') or [])==4 and after.get('selectedNodeIds')==[audit['expected_shot2_node']]
 try:
  t=s.get(url+'/agent/codex/threads/'+c['threadId'],timeout=30)
  audit['thread_fetch_http_code']=t.status_code
  if t.ok:
   value=t.json();msgs=value.get('messages') or []
   audit['history_message_count']=len(msgs)
   audit['assistant_messages']=[str(m.get('text') or '')[:6500] for m in msgs if m.get('role')=='assistant'][-2:]
   audit['tool_titles']=[m.get('title') for m in msgs if m.get('role')=='tool'][-12:]
 except Exception as e:audit['history_error_type']=type(e).__name__
 save()
 print('SHOT02_NATIVE_RESULT',json.dumps({k:audit.get(k) for k in (
  'turn_http_code','accepted','done','duration_s','no_canvas_count_or_selection_change',
  'thread_fetch_http_code','history_message_count','tool_titles','assistant_messages')},ensure_ascii=False),flush=True)
except Exception as exc:
 audit['error_type']=type(exc).__name__;audit['error_message']=str(exc)[:400]
 save()
 raise

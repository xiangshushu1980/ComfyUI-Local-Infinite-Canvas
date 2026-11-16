#!/usr/bin/env python3
"""Send ONE user-authorized native Codex turn to Canvas Agent.
POST /api/tools is used for READS ONLY; Canvas writes occur through native MCP.
"""
import hashlib,json,sys,time,traceback
from pathlib import Path
import requests
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/live-b-projection-20261116'
sys.path.insert(0,str(OUT))
from prepare_projection import payload
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
BASE_SHA='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
PROJECT='mrEXrMQoY-2ef3U6NsHtj'
TITLE='无限画布 1'
OLD_IDS={'text-1793372915213-2q1pb','image-1793372917582-2pevr','audio-1793372920916-z4dgp'}
CLIENT='04wsd618VDFdUWb74oZZI'
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
url=cfg['url'].rstrip('/')
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
result={'purpose':'User-authorized 4 exact approved B text display nodes via native Canvas Agent',
        'no_chat_http_writes':True,'expected_project':PROJECT,'expected_title':TITLE,
        'approved_B_state_sha256':BASE_SHA,'model':'gpt-6-luna','effort':'medium'}
def check(x,what):
 if not x:raise RuntimeError(what)
def save():
 (OUT/'native-projection-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
def health():return s.get(url+'/health',timeout=7).json()
def read(name):
 r=s.post(url+'/api/tools',json={'name':name,'input':{}},timeout=20)
 check(r.ok and r.json().get('ok') is True,'Read failed '+name)
 return r.json()['result']
def digest(node):return hashlib.sha256(json.dumps(node,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
try:
 expected=payload()
 check(hashlib.sha256(B.read_bytes()).hexdigest()==BASE_SHA,'B state SHA changed')
 h=health()
 check(h.get('hasCanvas') is True and h.get('clients')==1 and h.get('codexBusy') is False,
       'Must have one idle connected Canvas client')
 before=read('canvas_get_state')
 check(before.get('projectId')==PROJECT and before.get('title')==TITLE,'Canvas project changed')
 check(before.get('clientId')==CLIENT,'Canvas browser client changed')
 check({n['id'] for n in before.get('nodes',[])}==OLD_IDS,'Canvas original nodes changed')
 check(not before.get('selectedNodeIds'),'Canvas selection changed')
 old_hash={n['id']:digest(n) for n in before['nodes']}
 c=(s.get(url+'/agent/codex/workspace',timeout=20).json().get('conversation') or {})
 check(c.get('status') in ('ready','warning') and c.get('threadId'),'Native thread not ready')
 sl=s.get(url+'/agent/codex/skills?forceReload=1',timeout=50).json()
 skills=[x for x in sl.get('data',[]) if x.get('name')=='director-skill-v0-candidate' and x.get('enabled')]
 check(len(skills)==1,'Director Skill missing or disabled')
 result['preflight']={'old_nodes_sha256':old_hash,'old_node_ids':sorted(OLD_IDS),
     'title':TITLE,'projectId':PROJECT,'clientId':CLIENT,
     'skill':skills[0]['name'],'thread_id':c['threadId'],'revision':c.get('revision'),
     'shot_id_order':list(expected['shot_sha256']),
     'node_expected_text_sha256':{x['title']:hashlib.sha256(x['text'].encode()).hexdigest()
                                  for x in expected['input']['items']}}
 save()
 prompt=(
 '用户已明确授权你直接操作当前画布，添加 D《错过的钥匙》已批准 B 的四个镜头审阅文本节点。'
 '请使用 director-skill-v0-candidate。只能新增四个文本节点，不创建其它节点、不修改/删除/选择/移动三个原有空节点，不生成任何媒体或审批新版本。'
 '【唯一允许目标】title=无限画布 1，projectId='+PROJECT+'，客户端 '+CLIENT+'。'
 '先用 infinite-canvas MCP 的 canvas_get_state 检查项目 title 与 projectId，以及目前恰好三个节点 ID：'+','.join(sorted(OLD_IDS))+'。'
 '如果目标/节点/客户端发生变化，请立即停止，不写画布。'
 '接着使用终端只读执行 python3 /home/sean/projects/canvas-lab/docs/planning/WAR-90/live-b-projection-20261116/prepare_projection.py。'
 '输出是由 Runtime 验证批准 B 后确定性产生的 JSON，input.items 含四个 Shot01-04 的完整原文，含标题、位置、尺寸。'
 '请将 JSON 的 input 对象原样完整传给当前 infinite-canvas MCP 的 canvas_create_text_nodes，一次批量创建恰好四项。'
 '严禁缩写、摘要、改写 text，严禁通过终端/HTTP 调用画布写入；只能通过 native Canvas MCP 创建。'
 '执行后读取 canvas_get_state，核查原三节点仍在且现有七节点、四个展示标题均存在。'
 '不调用 select_nodes 或 set_viewport，不触碰原图片/音频，不调用 ComfyUI/H3/Linear，不改 Runtime 批准 B。'
 '如果出错或可能部分创建，报告问题，绝不重试创建。最后简短汇报完成数和不确定项。'
 )
 params={'clientId':CLIENT,'threadId':c['threadId'],
   'conversationId':c.get('conversationId',''),'expectedRevision':c.get('revision',0),
   'prompt':prompt,
   'messageText':'根据用户明确授权：在当前“无限画布 1”新增四个已批准 B 镜头文本展示副本（保留原有三个节点）',
   'permissionMode':'automatic','model':'gpt-6-luna','effort':'medium',
   'skill':{'name':skills[0]['name'],'path':skills[0]['path']}}
 start=time.monotonic()
 r=s.post(url+'/agent/codex/turn',json=params,timeout=90)
 result['native_turn_http_code']=r.status_code
 if not r.ok:
  result['native_turn_error']=str(r.json().get('error',''))[:350]
  raise RuntimeError('Native turn not accepted')
 result['native_turn_accepted']=True
 save()
 busy=False
 for _ in range(280):
  time.sleep(.75)
  h=health()
  busy=busy or bool(h.get('codexBusy'))
  if busy and not h.get('codexBusy'):break
 result['model_turn_elapsed_s']=round(time.monotonic()-start,2)
 result['model_busy_observed']=busy
 result['model_turn_settled']=bool(busy and not h.get('codexBusy'))
 result['conversation_final_status']=(h.get('conversation') or {}).get('status')
 if not result['model_turn_settled']:
  try:
   result['interrupt_http_code']=s.post(url+'/agent/codex/interrupt',json={'threadId':c['threadId']},timeout=12).status_code
  except Exception as exc:result['interrupt_error_type']=type(exc).__name__
 finalhealth=health()
 result['post_health']={'clients':finalhealth.get('clients'),'busy':finalhealth.get('codexBusy')}
 if finalhealth.get('clients')==1 and finalhealth.get('hasCanvas') and not finalhealth.get('codexBusy'):
  after=read('canvas_get_state')
  nodes=after.get('nodes') or []
  result['post_canvas_title']=after.get('title')
  result['post_project_id']=after.get('projectId')
  result['post_node_count']=len(nodes)
  result['post_selection_ids']=after.get('selectedNodeIds')
  actual={n['title']:n for n in nodes}
  result['original_nodes_unchanged']=all(any(n['id']==id and digest(n)==sha for n in nodes)
       for id,sha in old_hash.items())
  result['new_nodes']=[]
  for item in expected['input']['items']:
   n=actual.get(item['title'])
   text=str((n.get('metadata') or {}).get('content') or '') if n else ''
   result['new_nodes'].append({'title':item['title'],'id':n.get('id') if n else None,
             'text_exact':bool(n and text==item['text']),
             'expected_sha256':hashlib.sha256(item['text'].encode()).hexdigest(),
             'actual_sha256':hashlib.sha256(text.encode()).hexdigest() if n else None})
  result['all_four_exact']=bool(after.get('projectId')==PROJECT and after.get('title')==TITLE
       and after.get('clientId')==CLIENT and len(nodes)==7 and len({n['id'] for n in nodes})==7
       and result['original_nodes_unchanged'] and after.get('selectedNodeIds')==[]
       and all(x['text_exact'] for x in result['new_nodes']))
 else:
  result['post_read_blocked_by_changed_client_or_busy']=True
 try:
  hr=s.get(url+'/agent/codex/threads/'+c['threadId'],timeout=30)
  result['history_http_status']=hr.status_code
  if hr.ok:
   history=hr.json()
   result['history_tool_items']=[{'title':m.get('title'),'status':(m.get('detail') or {}).get('status')}
       for m in history.get('messages',[]) if m.get('role')=='tool'][-16:]
 except Exception as exc:result['history_read_error_type']=type(exc).__name__
 result['B_unchanged']=hashlib.sha256(B.read_bytes()).hexdigest()==BASE_SHA
 result['result_pass']=bool(result['model_turn_settled'] and result.get('all_four_exact') and result['B_unchanged'])
except Exception as exc:
 result['error_type']=type(exc).__name__;result['error_message']=str(exc)[:400]
 traceback.print_exc()
finally:
 save()
 print('NATIVE_B_PROJECTION',json.dumps({k:result.get(k) for k in (
    'native_turn_http_code','native_turn_accepted','model_turn_elapsed_s','model_turn_settled',
    'post_canvas_title','post_node_count','original_nodes_unchanged','all_four_exact','result_pass',
    'new_nodes','error_type','error_message')},ensure_ascii=False),flush=True)
 if not result.get('result_pass'):sys.exit(2)

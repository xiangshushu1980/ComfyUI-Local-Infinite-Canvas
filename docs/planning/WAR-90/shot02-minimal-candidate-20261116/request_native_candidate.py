#!/usr/bin/env python3
"""One-shot native Canvas Agent request for an UNAPPROVED Shot02 proposal.

Only Canvas text and approved Runtime are read. No B candidate submission,
node creation/update, media generation, or user-approval spoofing.
"""
from __future__ import annotations
import json,hashlib,requests,time,traceback
from pathlib import Path
root=Path('/home/sean/projects/canvas-lab')
out=root/'docs/planning/WAR-90/shot02-minimal-candidate-20261116'
report=out/'agent-candidate-audit.json'
B=root/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
expected_B='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
expected_P='2FwEbySI5PYe7d6BL4pES'
expected_C='jeUNwaV-t0QApaAKC2pMh'
expected_N='text-1794832120997-1'
conf=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=conf['token']
url=conf['url'].rstrip('/')
audit={'purpose':'native Canvas Agent Director Skill Shot02 minimal revision draft for human review only',
       'origin':'http://canvas.localhost','projectId':expected_P,
       'approvedBSourceSha':expected_B,'callIssued':False,'callAccepted':False,
       'stage':'preflight'}
def assertf(value,message):
 if not value: raise RuntimeError(message)
def save():report.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
def api_get(path,timeout=20):
 r=s.get(url+path,timeout=timeout);r.raise_for_status();return r.json()
def call(name,args):
 r=s.post(url+'/api/tools',json={'name':name,'input':args},timeout=20)
 assertf(r.ok and r.json().get('ok') is True,f'{name} request failed')
 return r.json()['result']
def check_b():return hashlib.sha256(B.read_bytes()).hexdigest()==expected_B
def summary(state):
 return {'projectId':state.get('projectId'),'clientId':state.get('clientId'),
         'title':state.get('title'),'nodes':len(state.get('nodes') or []),
         'nodeIDs':[n.get('id') for n in state.get('nodes') or []],
         'nodeTitles':[n.get('title') for n in state.get('nodes') or []],
         'selected':state.get('selectedNodeIds'),
         'nodeContentsSHA256':[hashlib.sha256(str((n.get('metadata') or {}).get('content') or '').encode()).hexdigest() for n in state.get('nodes') or []]}
try:
 assertf(not report.exists(),'Proposal turn already attempted: will not submit twice')
 h=api_get('/health',6)
 st=call('canvas_get_state',{})
 before=summary(st)
 assertf(h.get('clients')==1 and h.get('hasCanvas') and not h.get('codexBusy'),'Requires one idle connected client')
 assertf(st.get('projectId')==expected_P and st.get('clientId')==expected_C,'Unexpected browser target')
 assertf(len(st.get('nodes') or [])==4,'Unexpected canvas node count')
 assertf(any(n['id']==expected_N and 'Shot02' in n.get('title','') for n in st['nodes']),'Shot02 not in canvas')
 assertf(check_b(),'Approved B source changed')
 w=api_get('/agent/codex/workspace')
 conv=w.get('conversation') or {}
 assertf(conv.get('status')=='ready' and conv.get('threadId'),'Native Agent conversation not ready')
 skills=api_get('/agent/codex/skills?forceReload=1',40).get('data') or []
 skill=next((x for x in skills if x.get('name')=='director-skill-v0-candidate' and x.get('enabled')),None)
 assertf(skill,'Director Skill not enabled')
 thread_id=conv['threadId']
 previous=api_get('/agent/codex/threads/'+thread_id,30)
 past_messages=previous.get('messages') or []
 audit.update(stage='ready',preflight={'clients':h.get('clients'),'canvas':before,
              'approvedBUnchanged':True,'agentSkill':skill['name']},
              threadMessageCountBefore=len(past_messages))
 save()

 prompt=(
 '请作为 Canvas Lab **正式 Canvas Agent** 调用已经启用的 director-skill-v0-candidate。'
 '目的：提出 D《错过的钥匙》**Shot02** 的一个“最小局部修订候选 R1”，只供用户审阅；'
 '这不是用户同意修改 B，更不是用户同意签批、运行媒体或写画布。'
 '严格限制：不得调用 canvas_apply_ops、canvas_update_node、canvas_create_*、site_navigate，'
 '不得修改任何画布节点、选区或视口；不得对 Runtime 调用 prepare-stage、submit-stage、'
 'record-review、run-stage、resume-pack 或修改任何 Runtime 文件。只能只读查询。'
 '当前网页规范 Origin 为 http://canvas.localhost，项目ID=2FwEbySI5PYe7d6BL4pES，'
 '目标 Shot02 展示副本节点 text-1794832120997-1。'
 '先通过 infinite-canvas MCP canvas_get_state 找到明确 projectId 和 Shot02 节点 ID。'
 '如不存在或不匹配，停止并报告，不得转向别的同名画布。'
 '然后必须通过 Eric 本地只读 CLI 分别读取原批准 B 的 Shot01、Shot02、Shot03 全文：'
 'python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-shot '
 '--workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2 '
 '--shot-id <Shot01或Shot02或Shot03>。'
 '注意 CLI 只返回批准内容，不提供自动连续性结论；要用导演专业知识独立判断。'
 '核心问题：Shot02 同时处理纸边露出 K、观众辨认银钥匙、蓝夹落下再次遮 K、林让位、'
 '空右手轻理文件，是否在取景、动作/时间预算上信息过载？'
 '必须保护：Shot01 末尾提移已经开始、Shot02 首次显露与遮挡过程可读，'
 'K位置不变、无第二把钥匙，林无意遮挡、周没见到露出钥匙；'
 'Shot03 从 Shot02 的轻理动作尚未完成阶段跨切接入，周的提问才打断该动作。'
 '尤其不得简单删掉 Shot02 右手轻理而不解决 Shot03 的跨切依赖。'
 '输出严格格式：'
 '(1) 诊断：当前最大冲突与证据（不是只报文本长短），一句到三句；'
 '(2) 最小修订候选 R1：最多两处 Shot02 精确原句锚点→替换文本，'
 '说明是局部文字方案而非已签批准 B；确保能按此实施，避免泛泛“强化强调”；'
 '(3) 保持不变的约束及 Shot01→02 / Shot02→03 界面状态与 Shot03 依赖检查；'
 '(4) 风险与未知：指出没有实际时间/空间几何/观看证据；'
 '(5) 需要用户决定的**一个**选择问题，停止，不继续修订。'
 '如果专业判断认为根本不应改 Shot02，请诚实写“无必要修订”，给出理由，'
 '不要为了完成任务制造伪差异。'
 '只能在 Agent 聊天回复候选草稿，不保存成正式 Runtime 阶段，不创造画布上新候选节点。'
 )
 params={'clientId':expected_C,'threadId':thread_id,
        'conversationId':conv.get('conversationId',''),'expectedRevision':conv.get('revision',0),
        'prompt':prompt,
        'messageText':'Director Skill v0: Shot02 最小局部修订候选 R1（仅提案；不改批准 B/Canvas）',
        'permissionMode':'automatic','model':'gpt-6-luna','effort':'high',
        'skill':{'name':skill['name'],'path':skill['path']}}
 audit.update(callIssued=True,stage='in_flight')
 save()
 r=s.post(url+'/agent/codex/turn',json=params,timeout=90)
 audit['submitHttpStatus']=r.status_code
 assertf(r.ok,f'Native Agent rejected turn {r.status_code}')
 audit['callAccepted']=True;save()
 started=time.monotonic();saw_busy=False
 for i in range(160):
  time.sleep(1)
  health=api_get('/health',8)
  saw_busy=saw_busy or bool(health.get('codexBusy'))
  if saw_busy and not health.get('codexBusy'):break
 audit['elapsedSeconds']=round(time.monotonic()-started,1)
 audit['modelTurnSettled']=saw_busy and not health.get('codexBusy')
 thread=api_get('/agent/codex/threads/'+thread_id,30)
 msgs=thread.get('messages') or []
 increment=msgs[len(past_messages):]
 audit['threadMessageCountAfter']=len(msgs)
 audit['newMessagesCount']=len(increment)
 audit['assistantMessages']=[{'text':m.get('text') or '', 'id':m.get('id')}
                            for m in increment if m.get('role')=='assistant']
 audit['toolEvents']=[{'title':m.get('title'),'name':m.get('name')}
                     for m in increment if m.get('role')=='tool']
 aft=call('canvas_get_state',{})
 audit['postCanvas']=summary(aft)
 audit['canvasPreserved']=audit['postCanvas']==before
 audit['BSourcePreserved']=check_b()
 audit['outcomePass']=bool(audit['modelTurnSettled'] and audit['canvasPreserved']
                           and audit['BSourcePreserved'] and audit['assistantMessages'])
 audit['stage']='done'
 save()
 print('CANDIDATE_AUDIT',json.dumps({k:audit.get(k) for k in
  ('submitHttpStatus','modelTurnSettled','elapsedSeconds','threadMessageCountBefore',
    'threadMessageCountAfter','canvasPreserved','BSourcePreserved','toolEvents','outcomePass')},
    ensure_ascii=False),flush=True)
 print('CANDIDATE_TEXT',audit['assistantMessages'][-1]['text'][-12000:] if audit['assistantMessages'] else '(no agent answer)',flush=True)
except Exception as e:
 audit['errorType']=type(e).__name__;audit['errorText']=str(e)[:400];save()
 traceback.print_exc();raise

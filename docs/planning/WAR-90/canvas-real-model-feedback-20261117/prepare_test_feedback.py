#!/usr/bin/env python3
"""Provenance-safe synthetic Director feedback, bound to live canonical canvas.
Not a real user instruction or approval. Does NOT alter approved B content.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,requests,sys
ROOT=Path('/home/sean/projects/canvas-lab')
HERE=ROOT/'docs/planning/WAR-90/canvas-real-model-feedback-20261117'
sys.path.insert(0,str(ROOT/'docs/planning/WAR-90/canvas-feedback-20261115'))
from feedback_bridge import (approved_packet, capture_feedback,check_catalog,
                             clone_for_revision)
p=approved_packet()
EXPECTED_PROJECT='2FwEbySI5PYe7d6BL4pES'
EXPECTED_CLIENT='jeUNwaV-t0QApaAKC2pMh'
EXPECTED_NODE='text-1794832120997-1'
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
EXPECTED_B='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
def tool(name,input={}):
 r=s.post(cfg['url']+'/api/tools',json={'name':name,'input':input},timeout=20)
 if not r.ok or not r.json().get('ok'):raise RuntimeError('Canvas read/selection error: '+name)
 return r.json()['result']
def save(name,value): (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
if (HERE/'feedback.json').exists():raise RuntimeError('feedback already prepared')
h=s.get(cfg['url']+'/health',timeout=7).json()
assert h.get('clients')==1 and h.get('hasCanvas') and not h.get('codexBusy'),h.get('clients')
st=tool('canvas_get_state')
assert st['projectId']==EXPECTED_PROJECT and st.get('clientId')==EXPECTED_CLIENT and len(st['nodes'])==4
assert hashlib.sha256(B.read_bytes()).hexdigest()==EXPECTED_B
nodes=st['nodes'];current_selection=st.get('selectedNodeIds') or []
expected={x['id']:x['text_sha256'] for x in p['shots']}
assert {n.get('title','').split(' · ')[1].split('｜')[0] for n in nodes}==set(expected)
catalog={'format':'war90-canvas-shot-selection-v0','project_id':EXPECTED_PROJECT,
 'approved_B_id':p['authority']['approved_B_id'],
 'approved_B_content_sha256':p['authority']['approved_B_content_sha256'],
 'source_sha256':p['authority']['source_sha256'],'nodes':[]}
for shot in p['shots']:
 found=[n for n in nodes if ' · '+shot['id']+'｜B 展示副本' in n['title']]
 assert len(found)==1
 n=found[0]
 preview=(n.get('metadata') or {}).get('content','')
 assert shot['id'] in preview and p['authority']['approved_B_id'] in preview
 catalog['nodes'].append({'id':n['id'],'title':n['title'],'shot_id':shot['id'],'shot_text_sha256':expected[shot['id']]})
check_catalog(p,catalog)
assert any(x['id']==EXPECTED_NODE and x['shot_id']=='Shot02' for x in catalog['nodes'])
# User did not manually select Shot02. Selection below is a recorded agent action
# for synthetic workflow testing, not evidence that the user clicked Shot02.
try:
 tool('canvas_select_nodes',{'ids':[EXPECTED_NODE]})
 selection=tool('canvas_get_selection')
 assert len(selection.get('nodes') or [])==1 and selection['nodes'][0]['id']==EXPECTED_NODE
 instruction=(
  '【合成测试意见，非用户本人导演反馈，禁止自动批准】'
  '希望 Shot02 的视觉重点更集中于“纸边退开→观众辨认唯一银色钥匙→蓝色文件夹自然落下并再遮挡”的因果过程。'
  '落夹后的林让位与空右手轻理保留，但请尝试将轻理作为本镜尾部短暂可见的动作启动，'
  '完整动作连续到 Shot03，并且只有周的提问才真正打断轻理。'
  '不要把周在背景接近与林轻理变成与首次认出钥匙竞争的注意力中心；'
  '保持斜俯桌面近景、固定钥匙、蓝夹由纸叠承托、林无意遮挡、周未先看见钥匙。'
  '只考虑修改 Shot02 的观看任务/镜头画幅组织/切点相关描述，'
  'Shot01、Shot03、Shot04 文本必须逐字不变。'
  '如果要维持连续性就不得取消 Shot02→Shot03 同一次右手轻理；'
  '如果专业判断改变毫无增益，请给出 No-change，不要制造差异。'
 )
 feedback=capture_feedback(p,catalog,st,selection,instruction,origin='synthetic-test')
 assert feedback['actor_identity_verified'] is False and feedback['human_B_decision'] is False
 # Persist all evidence before model execution; do not record a fake user identity.
 save('catalog.json',catalog)
 save('feedback.json',feedback)
 prepared=clone_for_revision(p,feedback,ROOT/'docs/planning/WAR-90/pilot-D-canvas-shot02-flowtest-20261117')
 save('prepared-branch.json',prepared)
 save('preflight.json',{'at':datetime.now(timezone.utc).isoformat(),
  'source_B_state_sha256':EXPECTED_B,
  'project_id':EXPECTED_PROJECT,'client_id':EXPECTED_CLIENT,'original_selection':current_selection,
  'test_selected_shot':'Shot02','browser_node_ids':[n['id'] for n in nodes],
  'feedback_origin':'synthetic-test','actual_user_creative_feedback':False,
  'actor_identity_verified':False,'approval_recorded':False})
 print('SYNTHETIC_FEEDBACK_PREPARED',json.dumps({'workspace':prepared['workspace'],'origin':feedback['origin'],
   'feedback_sha':feedback['instruction_sha256'],'selected_node':feedback['canvas_node_id'],
   'original_selection':current_selection,'original_B_unchanged':hashlib.sha256(B.read_bytes()).hexdigest()==EXPECTED_B},ensure_ascii=False))
finally:
 # Preserve previous user selection; prevents side effects in normal canvas.
 tool('canvas_select_nodes',{'ids':current_selection})
 after=tool('canvas_get_state')
 assert after['projectId']==EXPECTED_PROJECT and after['selectedNodeIds']==current_selection and len(after['nodes'])==4

#!/usr/bin/env python3
"""One-off, synthetic-test-labeled Canvas diff preview, without touching B nodes."""
from pathlib import Path
import json,requests,hashlib,sys,time
ROOT=Path('/home/sean/projects/canvas-lab')
E=ROOT/'docs/planning/WAR-90/canvas-real-model-feedback-20261117'
work=ROOT/'docs/planning/WAR-90/pilot-D-canvas-shot02-flowtest-20261117'
orig=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
expected_sha='23e78d5994ed18ea02d59c2eb588f36cc41d3b495b81009713ec7570d7e4b7'  # replaced below from fixed known value
expected_sha='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
expected_project='2FwEbySI5PYe7d6BL4pES'
expected_client='jeUNwaV-t0QApaAKC2pMh'
expected_shot02_node='text-1794832120997-1'
E.mkdir(exist_ok=True)
audit_file=E/'canvas-display-audit.json'
if audit_file.exists():raise RuntimeError('Existing display audit: one-off write will not be repeated')
model=json.loads((E/'model-result.json').read_text())
diff=json.loads((E/'candidate-diff.json').read_text())
feedback=json.loads((E/'feedback.json').read_text())
assert model['status']=='candidate-ready-for-human-review' and model['metadata']['generator']=='codex-cli'
assert model['metadata']['status']=='candidate-saved' and model['metadata']['model']=='gpt-6-astra'
assert model['metadata']['verified_changed_shots']==['Shot02']
assert model['source_b_unchanged'] and diff['candidate_id']==model['candidate_id']
assert diff['changed_shots']==['Shot02'] and diff['pending_review_shots']==['Shot01','Shot02','Shot03']
assert diff['pilot_B_approved'] is False and diff['formal_WAR35_approval'] is False
assert feedback['origin']=='synthetic-test' and feedback['human_B_decision'] is False
assert hashlib.sha256(orig.read_bytes()).hexdigest()==expected_sha
sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
from runtime import Pilot
st_branch=Pilot(work).load()
assert st_branch['phase']=='awaiting-human-B' and st_branch['pilot_B'] is None
assert st_branch['active']['id']==diff['candidate_id']
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token'];base=cfg['url'].rstrip('/')
def tool(name,inp):
 resp=s.post(base+'/api/tools',json={'name':name,'input':inp},timeout=30)
 if not resp.ok or not resp.json().get('ok'):raise RuntimeError(name+' failed')
 return resp.json()['result']
h=s.get(base+'/health',timeout=8).json();state=tool('canvas_get_state',{})
assert h.get('clients')==1 and h.get('hasCanvas') and not h.get('codexBusy')
assert state.get('projectId')==expected_project and state.get('clientId')==expected_client
assert len(state.get('nodes',[]))==4 and not state.get('connections')
titles={x['title'] for x in state['nodes']}
assert all(any('Shot0'+str(i) in title for title in titles) for i in range(1,5))
assert any(x['id']==expected_shot02_node for x in state['nodes'])
original_selection=state.get('selectedNodeIds') or []
previous_ids={x['id'] for x in state['nodes']}
previous_sha={x['id']:hashlib.sha256(str((x.get('metadata') or {}).get('content','')).encode()).hexdigest() for x in state['nodes']}
# Present an edited excerpt, not a whole pasted second Shot Plan. The exact
# full diff and entire revised Shot02 are saved in local evidence.
text=(
 '【WAR-90 · Shot02 局部修订实验（待审，不是批准版）】\n'
 '⚠ 这是一条合成测试反馈，不是你提出的正式导演修改意见；不计作用户批准。\n\n'
 '批准基线 B：b7b4fd156b884907b2431b6b1e0d9960\n'
 f'试验候选：{diff["candidate_id"]}\n'
 '技术范围：仅修改 Shot02 正文；Shot01、Shot03、Shot04 均保持逐字一致。\n'
 '需要复检：Shot01 → Shot02 → Shot03。\n\n'
 '【改变 1｜观看任务】\n'
 '原：先辨认钥匙，再跟随蓝夹覆盖；最后把注意交给林让位与轻理。\n'
 '新：以同一 K 的可见变化为核心。落夹后的轻理只交付“可见启动+方向”，不要求完整观看轻理过程。\n\n'
 '【改变 2｜画面构图】\n'
 '原：K、纸叠落点、蓝夹取用区、承托边均为画面核心。\n'
 '新：退开的纸边、K、蓝夹覆盖边形成同一个主要阅读区域；右手路径与林让位仍可见，但不和 K 争夺视觉中心。\n\n'
 '【改变 3｜跨镜切点】\n'
 '原：让位完成、右手轻理已自然开始且仍进行中时切 Shot03。\n'
 '新：右手接触纸边、轻理刚出现明确的运动方向时即可动作中切；Shot03 接续同一动作，由周的提问才打断。\n\n'
 '【必须保留】\n'
 '唯一钥匙始终固定；蓝夹落在纸叠且自然再遮；林/周在首次显露时均未认出钥匙；Shot03 的问句必须真正打断仍在进行的右手轻理。\n\n'
 '【核心未证风险】\n'
 '较早切点与周走到桌边的时序是否匹配？如果不匹配，需要回到 Blocking 复检；当前没有观看、连续动作或 H3 成片证据。\n\n'
 '【审阅】\n'
 '这只是可比较的实验候选；原四个 B 文本节点没有替换。由真人选择保留原 B、要求修改候选或批准试点新 B；Agent 不得自签。\n'
 '完整逐字差异保存 Eric：docs/planning/WAR-90/canvas-real-model-feedback-20261117/candidate-diff.json\n'
)
item={'title':'【实验待审｜非批准】Shot02 R2 · 最小局部差异','text':text,
      'x':720,'y':1270,'width':760,'height':1040}
audit={'origin':'http://canvas.localhost','projectId':expected_project,
       'clientId':expected_client,'baseline_node_ids':sorted(previous_ids),
       'baseline_compact_content_sha256':previous_sha,
       'initial_node_count':4,'original_selection':original_selection,
       'candidate_id':diff['candidate_id'],'candidate_content_sha256':diff['candidate_content_sha256'],
       'feedback_origin':'synthetic-test','human_B_decision':False,
       'model_generator':'codex-cli','writeCalled':True,'writeSuccess':False,
       'display_node_title':item['title'],'display_text_sha256':hashlib.sha256(text.encode()).hexdigest()}
audit_file.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
# Exactly one write API call; audit marker prevents unsafe retries on timeout.
result=tool('canvas_create_text_nodes',{'items':[item]})
audit['writeSuccess']=True
n=result.get('nodes') or []
audit['tool_full_node_count']=len(n)
new=[x for x in n if x['id'] not in previous_ids]
assert len(new)==1 and new[0]['title']==item['title']
assert ((new[0].get('metadata') or {}).get('content') or '')==text
audit['display_node_id']=new[0]['id']
time.sleep(.5)
final=tool('canvas_get_state',{})
audit['post_node_count']=len(final.get('nodes') or [])
audit['baseline_nodes_preserved']= all(x['id'] in previous_ids and hashlib.sha256(str((x.get('metadata') or {}).get('content','')).encode()).hexdigest()==previous_sha[x['id']] for x in final['nodes'] if x['id'] in previous_ids) and sum(x['id'] in previous_ids for x in final['nodes'])==4
audit['candidate_displayed']=sum(x['id']==audit['display_node_id'] for x in final['nodes'])==1
audit['selection_preserved']=final.get('selectedNodeIds')==original_selection
audit['approved_B_state_sha256_unchanged']=hashlib.sha256(orig.read_bytes()).hexdigest()==expected_sha
audit['pass']=bool(audit['writeSuccess'] and audit['post_node_count']==5 and
                  audit['baseline_nodes_preserved'] and audit['candidate_displayed'] and
                  audit['selection_preserved'] and audit['approved_B_state_sha256_unchanged'])
audit_file.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print('CANVAS_DIFF_DISPLAY',json.dumps({k:audit.get(k) for k in ('pass','display_node_id','post_node_count',
 'baseline_nodes_preserved','candidate_displayed','selection_preserved',
 'approved_B_state_sha256_unchanged')},ensure_ascii=False),flush=True)
if not audit['pass']:sys.exit(2)

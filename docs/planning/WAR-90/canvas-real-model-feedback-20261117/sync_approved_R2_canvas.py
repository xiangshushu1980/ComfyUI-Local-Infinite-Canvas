#!/usr/bin/env python3
"""One-shot WAR-90 pilot-B R2 -> existing five canonical Canvas text displays.

This is NOT typed DirectorPlan persistence. Source of authority is the approved
Director Runtime branch; no new nodes/media/generation; do not change positions.
"""
from pathlib import Path
import hashlib,json,requests,sys
ROOT=Path('/home/sean/projects/canvas-lab')
P=ROOT/'docs/planning/WAR-90/canvas-real-model-feedback-20261117'
OUT=P/'approved-R2-canvas-sync-audit.json'
ORIG=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
BRANCH=ROOT/'docs/planning/WAR-90/pilot-D-canvas-shot02-flowtest-20261117'
ORIG_SHA='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
PROJECT='2FwEbySI5PYe7d6BL4pES'
CLIENT='jeUNwaV-t0QApaAKC2pMh'
ID_MAP={
  'Shot01':'text-1794832120997-0',
  'Shot02':'text-1794832120997-1',
  'Shot03':'text-1794832120997-2',
  'Shot04':'text-1794832120997-3',
}
DIFF_ID='text-1794847881140-0'
OLD_B='b7b4fd156b884907b2431b6b1e0d9960'
R2='6cbcaf51a55e4bb0a097147eb34dd3cb'
sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
from runtime import Pilot,shot_sections
def sha(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def write(value):OUT.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
if OUT.exists():raise RuntimeError('Sync already attempted: refusing second call')
assert hashlib.sha256(ORIG.read_bytes()).hexdigest()==ORIG_SHA
old=Pilot(ORIG.parent).review_packet()
new=Pilot(BRANCH).review_packet()
assert old['authority']['approved_B_id']==OLD_B
assert new['authority']['approved_B_id']==R2 and new['review']['pilot_B_accepted'] is True
assert new['review']['formal_WAR35_approval'] is False and new['review']['pending_shots']==[]
assert new['authority']['approval_evidence_sha256']['B']=='73310fdec6d87b24f4cde822236d694a0e239d850d5eca556be73cdff3ccba0f'
assert [x['id'] for x in new['shots']]==list(ID_MAP)
assert [x['id'] for x in old['shots']]==list(ID_MAP)
for o,n in zip(old['shots'],new['shots']):
 assert sha(n['text'])==n['text_sha256']
 if n['id']!='Shot02':assert o['text']==n['text'] and o['text_sha256']==n['text_sha256']
 else:assert o['text']!=n['text']
conf=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
ses=requests.Session();ses.trust_env=False;ses.headers['x-canvas-agent-token']=conf['token']
url=conf['url'].rstrip('/')
def call(name,args):
 r=ses.post(url+'/api/tools',json={'name':name,'input':args},timeout=32)
 if not r.ok or r.json().get('ok') is not True:raise RuntimeError('Canvas API '+name+' error')
 return r.json()['result']
h=ses.get(url+'/health',timeout=7).json()
st=call('canvas_get_state',{})
assert h.get('clients')==1 and h.get('hasCanvas') and not h.get('codexBusy')
assert st['projectId']==PROJECT and st['clientId']==CLIENT and len(st['nodes'])==5
ids={n['id']:n for n in st['nodes']}
assert set(ids)==set(ID_MAP.values())|{DIFF_ID}
assert not (st.get('connections') or [])
initial_selection=st['selectedNodeIds']
diff_node=ids[DIFF_ID]
assert diff_node['title']=='【实验待审｜非批准】Shot02 R2 · 最小局部差异'
assert str((diff_node.get('metadata') or {}).get('content','')).startswith('【WAR-90 · Shot02 局部修订实验（待审，不是批准版）】')
baseline_audit=json.loads((P/'canvas-display-audit.json').read_text())
ops=[]
expected={}
for shot in new['shots']:
 shot_id=shot['id']
 old_header=ids[ID_MAP[shot_id]]
 assert old_header['type']=='text' and 'B 展示副本' in old_header['title']
 preview=str((old_header.get('metadata') or {}).get('content') or '')
 assert OLD_B in preview and f'镜头：{shot_id}' in preview
 assert sha(preview)==baseline_audit['baseline_compact_content_sha256'][ID_MAP[shot_id]],'Previously verified base text preview changed'
 title=f'D《错过的钥匙》 · {shot_id}｜R2 试点 B 展示'
 header=(
  '【导演计划 R2 · WAR-90 试点 B 已接受｜文本展示副本】\n'
  '影片：D《错过的钥匙》\n'
  f'试点已接受 B ID：{R2}\n'
  f'镜头：{shot_id}\n'
  f'镜头原文 SHA256：{shot["text_sha256"]}\n'
  '来源：Eric Director Runtime（pilot-D-canvas-shot02-flowtest-20261117）\n'
  '仅验证试点文本审阅与版本同步，不是 WAR-35 正式批准，也不是视觉/几何证明。\n\n'
 )
 content=header+shot['text']
 ops.append({'type':'update_node','id':ID_MAP[shot_id],'patch':{'title':title},
             'metadata':{'content':content}})
 expected[ID_MAP[shot_id]]={'title':title,'sha256':sha(content),'shotTextSha':shot['text_sha256']}
summary=(
 '【WAR-90 · R2 试点 B 已接受｜历史差异记录】\n'
 '状态：用户在当前对话明确回复“认可R2.”，运行壳已记录 checkpoint B / human accept。\n'
 '注意：原反馈本身是 synthetic-test 工程测试输入，非用户最初写的导演要求。'
 ' 用户审阅后认可了实际生成的 R2 文本候选。\n'
 f'原试点 B：{OLD_B}\n'
 f'新试点 B：{R2}\n'
 f'新 B 文本内容 SHA256：{new["authority"]["approved_B_content_sha256"]}\n'
 f'人工审阅证据 SHA256：{new["authority"]["approval_evidence_sha256"]["B"]}\n\n'
 '变更范围：仅 Shot02 的“观看任务”“画面构造”“切点与出态”三处。'
 ' Shot01、03、04 正文完全不变。\n'
 '观看重点：纸边退开 → 观众认出唯一银钥匙 → 蓝夹自然落放重新遮住 K。\n'
 'Shot02 尾部只交付右手接触文件边并开始轻理的方向；Shot03 接续同一动作，直到周的提问才停止。\n'
 '未证风险：较早切点与周接近桌边的时序、实际遮挡几何和观众可读性仍需未来验证。\n\n'
 '状态约束：WAR-90 Pilot B 已接受；正式 WAR-35 Review 尚未实现，identity_verified=false。'
 ' 不代表任何图像/H3/观众质量验收。\n'
 '详细逐字 diff：Eric docs/planning/WAR-90/canvas-real-model-feedback-20261117/candidate-diff.json\n'
)
diff_title='【R2 试点 B 已接受】Shot02 · 修改差异记录'
ops.append({'type':'update_node','id':DIFF_ID,'patch':{'title':diff_title},'metadata':{'content':summary}})
expected[DIFF_ID]={'title':diff_title,'sha256':sha(summary),'shotTextSha':None}
audit={
 'projectId':PROJECT,'clientId':CLIENT,'origin':'http://canvas.localhost',
 'oldB':OLD_B,'approvedR2':R2,
 'acceptedBSourceSha256':hashlib.sha256((BRANCH/'state.json').read_bytes()).hexdigest(),
 'oldBSourceSha256':ORIG_SHA,
 'humanPilotApprovalEvidenceSha256':new['authority']['approval_evidence_sha256']['B'],
 'preflight':{'nodeIds':sorted(ids),'selectedNodeIds':initial_selection,
              'nodePositions':{i:n['position'] for i,n in ids.items()},
              'nodeSizes':{i:[n['width'],n['height']] for i,n in ids.items()},
              'nodeTitleAndCompactContentSHA':{i:{'title':n['title'],'contentSHA':sha(str((n.get('metadata') or {}).get('content') or ''))} for i,n in ids.items()}},
 'expected':expected,'writeIssued':True,'writeSuccess':False,
 'notes':'One batch update of five existing text nodes. No add/remove/reorder, media, connection or approval operations.'
}
write(audit) # marker prevents a blind second write after timeout
result=call('canvas_apply_ops',{'ops':ops})
audit['writeSuccess']=True
returned=result.get('nodes') or []
lookup={n['id']:n for n in returned}
audit['fullResultNodes']=len(returned)
audit['fullTextMatch']={i: i in lookup and lookup[i]['title']==v['title'] and sha((lookup[i].get('metadata') or {}).get('content') or '')==v['sha256'] for i,v in expected.items()}
audit['fullResultSelectionPreserved']=result.get('selectedNodeIds')==initial_selection
write(audit)
after=call('canvas_get_state',{})
actual={n['id']:n for n in (after.get('nodes') or [])}
audit['postNodeCount']=len(actual)
audit['compactTitlesMatch']=all(actual.get(i,{}).get('title')==expected[i]['title'] for i in expected)
audit['positionsPreserved']=all(actual.get(i,{}).get('position')==a['position'] for i,a in ids.items())
audit['sizesPreserved']=all((actual.get(i,{}).get('width'),actual.get(i,{}).get('height'))==(a['width'],a['height']) for i,a in ids.items())
audit['selectionPreserved']=after.get('selectedNodeIds')==initial_selection
audit['graphConnectionsPreserved']=(after.get('connections') or [])==(st.get('connections') or [])
audit['newApprovedBUnchanged']=hashlib.sha256((BRANCH/'state.json').read_bytes()).hexdigest()==audit['acceptedBSourceSha256']
audit['oldApprovedBUnchanged']=hashlib.sha256(ORIG.read_bytes()).hexdigest()==ORIG_SHA
audit['pass']=bool(audit['writeSuccess'] and all(audit['fullTextMatch'].values()) and
                   len(audit['fullTextMatch'])==5 and audit['fullResultSelectionPreserved'] and
                   audit['postNodeCount']==5 and audit['compactTitlesMatch'] and
                   audit['positionsPreserved'] and audit['sizesPreserved'] and
                   audit['selectionPreserved'] and audit['graphConnectionsPreserved'] and
                   audit['newApprovedBUnchanged'] and audit['oldApprovedBUnchanged'])
write(audit)
print('CANVAS_APPROVED_R2_SYNC',json.dumps({k:audit.get(k) for k in ('pass','fullResultNodes','fullTextMatch','selectionPreserved','positionsPreserved','sizesPreserved','postNodeCount','newApprovedBUnchanged','oldApprovedBUnchanged')},ensure_ascii=False),flush=True)
if not audit['pass']:sys.exit(2)

#!/usr/bin/env python3
"""Read-only audit: full tool-result hashes + compact preview semantics."""
import hashlib,json,sys
from pathlib import Path
import requests
OUT=Path('/home/sean/projects/canvas-lab/docs/planning/WAR-90/live-b-projection-20261116')
sys.path.insert(0,str(OUT))
from prepare_projection import payload
B=Path('/home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2/state.json')
PRE=json.loads((OUT/'native-projection-result.json').read_text())['preflight']
DIAG=json.loads((OUT/'exact-tool-inner-diagnostic.json').read_text())
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
h=s.get(cfg['url']+'/health',timeout=7).json()
r=s.post(cfg['url']+'/api/tools',json={'name':'canvas_get_state','input':{}},timeout=20)
assert r.ok and r.json().get('ok'), 'read failed'
view=r.json()['result']
nodes=view.get('nodes') or []
bytitle={n['title']:n for n in nodes}
oldhash=PRE['old_nodes_sha256']
def fp(node):return hashlib.sha256(json.dumps(node,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
originals_ok=all(any(n['id']==nid and fp(n)==sha for n in nodes) for nid,sha in oldhash.items())
items=payload()['input']['items']
shots=[]
for i,x in enumerate(items):
 sid=['Shot01','Shot02','Shot03','Shot04'][i]
 n=bytitle.get(x['title'])
 compact=str((n.get('metadata') or {}).get('content') or '') if n else ''
 wantsha=hashlib.sha256(x['text'].encode()).hexdigest()
 full_toolsha=DIAG.get('inner_returned_text_sha256',{}).get(sid)
 shots.append({'shot':sid,'node_id':n['id'] if n else None,
     'full_update_tool_return_exact_sha':full_toolsha==wantsha,
     'compact_read_matches_source_prefix':compact==x['text'][:120]+'...',
     'compact_chars':len(compact),
     'expected_full_chars':len(x['text']),
     'unchanged_position':bool(n and n.get('position')=={'x':x['x'],'y':x['y']}),
     'unchanged_dimensions':bool(n and n.get('width')==x['width'] and n.get('height')==x['height'])})
result={'phase':'user-live-canvas-approved-B-display-projection',
        'target_project_title':view.get('title'),
        'target_project_id':view.get('projectId'),
        'connected_clients':h.get('clients'),'has_canvas':h.get('hasCanvas'),'agent_busy':h.get('codexBusy'),
        'expected_node_count':7,'actual_node_count':len(nodes),
        'original_three_nodes_unchanged':originals_ok,
        'selected_ids':view.get('selectedNodeIds'),
        'approved_B_state_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),
        'four_shots':shots,
        'preexisting_model_transcription_failure_not_authoritative':True,
        'audit_limit':'Agent canvas_get_state intentionally truncates long metadata.content to first 120 characters + ...; exact full SHA is validated from browser tool returned full post-update snapshot. Browser reload durability not tested.',
        'success':len(nodes)==7 and h.get('clients')==1 and view.get('title')=='无限画布 1' and view.get('projectId')=='mrEXrMQoY-2ef3U6NsHtj' and originals_ok and all(x['full_update_tool_return_exact_sha'] and x['compact_read_matches_source_prefix'] and x['unchanged_position'] and x['unchanged_dimensions'] for x in shots) and hashlib.sha256(B.read_bytes()).hexdigest()=='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'}
(OUT/'projection-final-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('FINAL_PASS',result['success'],'count',len(nodes),'originals',originals_ok,'shots',[(x['shot'],x['full_update_tool_return_exact_sha'],x['compact_read_matches_source_prefix']) for x in shots])
if not result['success']:sys.exit(2)

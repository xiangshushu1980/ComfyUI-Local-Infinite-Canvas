#!/usr/bin/env python3
"""Read-only terminal verification for WAR-90's narrow pilot B approval/sync."""
import json,hashlib,requests,sys
from pathlib import Path
ROOT=Path('/home/sean/projects/canvas-lab')
D=ROOT/'docs/planning/WAR-90/canvas-real-model-feedback-20261117'
W=ROOT/'docs/planning/WAR-90/pilot-D-canvas-shot02-flowtest-20261117'
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2'
sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
from runtime import Pilot
sha=lambda b:hashlib.sha256(b).hexdigest()
base=Pilot(B)
next_=Pilot(W)
bs=base.load();ns=next_.load()
base.check(bs);next_.check(ns)
bp=base.review_packet();rp=next_.review_packet()
approval=json.loads((D/'R2-approval-validation.json').read_text())
audit=json.loads((D/'approved-R2-canvas-sync-audit.json').read_text())
source_evidence=D/'user-R2-acceptance-evidence.md'
model=json.loads((D/'model-result.json').read_text())
expected_ids=['text-1794832120997-0','text-1794832120997-1','text-1794832120997-2','text-1794832120997-3','text-1794847881140-0']
config=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=config['token']
h=s.get(config['url']+'/health',timeout=7).json()
r=s.post(config['url']+'/api/tools',json={'name':'canvas_get_state','input':{}},timeout=20)
assert r.ok and r.json().get('ok') is True
canvas=r.json()['result']
ids={n.get('id'):n for n in canvas.get('nodes') or []}
checks={
 'original_approved_B_unchanged':sha((B/'state.json').read_bytes())=='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7',
 'original_B_id_retained':bp['authority']['approved_B_id']=='b7b4fd156b884907b2431b6b1e0d9960',
 'new_R2_accepted_B_id':rp['authority']['approved_B_id']=='6cbcaf51a55e4bb0a097147eb34dd3cb',
 'R2_authority_integrity_ok':ns['pilot_B']['id']==ns['active']['id'] and ns['phase']=='pilot-B-accepted',
 'R2_no_pending_neighbor_flags':ns['pending_shots']==[],
 'actual_human_evidence_sha':sha(source_evidence.read_bytes())==ns['reviews'][-1]['evidence_sha256'],
 'pilot_not_formal_WAR35_review':ns['reviews'][-1]['identity_verified'] is False and ns['reviews'][-1]['formal_WAR35_approval'] is False,
 'external_evidence_recorded':rp['review']['external_human_evidence_recorded'] and rp['review']['pilot_B_accepted'],
 'only_Shot02_text_changed':[(o['id']) for o,n in zip(bp['shots'],rp['shots']) if o['text']!=n['text']]==['Shot02'],
 'real_professional_model_came_from_codex_cli':model['metadata']['generator']=='codex-cli' and bool(model['metadata'].get('thread_id')),
 'one_expected_canvas_project':canvas.get('projectId')=='2FwEbySI5PYe7d6BL4pES' and canvas.get('clientId')=='jeUNwaV-t0QApaAKC2pMh',
 'five_nodes_no_additional_ones':len(ids)==5 and set(ids)==set(expected_ids),
 'all_nodes_display_R2':all('R2' in ids[i]['title'] for i in expected_ids),
 'no_canvas_graph_edges_added':not (canvas.get('connections') or []),
 'full_content_verified_by_batch_write_reply':audit.get('pass') and len(audit.get('fullTextMatch') or {})==5 and all(audit['fullTextMatch'].values()),
 'canvas_compact_still_mentions_R2':all(rp['authority']['approved_B_id'] in (ids[i].get('metadata',{}).get('content') or '') for i in expected_ids[:4]),
 'B_saved_after_canvas_write_same_byte':sha((W/'state.json').read_bytes())==audit['acceptedBSourceSha256'],
 'canvas_gateway_services_running':h.get('hasCanvas') and h.get('clients')==1 and not h.get('codexBusy'),
}
result={'checkpoint':'post-approval live Canvas read-back','checks':checks,
        'pass':all(checks.values()),'checks_count':len(checks),
        'approvedBId':rp['authority']['approved_B_id'],'approvedBStateSHA':sha((W/'state.json').read_bytes()),
        'canvasProjectId':canvas.get('projectId'),'canvasNodeCount':len(ids),
        'notes':['This is an experimental WAR-90 pilot approval, not formal WAR-35 review.',
                 'The user approved the R2 candidate, not the synthetic feedback origin.',
                 'Browser refresh/IndexedDB rehydration has not been independently tested.',
                 'No media, audience, continuous-geometry, or live acting validation was done.']}
(D/'R2-post-sync-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('POST_SYNC_CHECK',{'pass':result['pass'],'total':len(checks),'failed':[k for k,v in checks.items() if not v]})
if not result['pass']:sys.exit(2)

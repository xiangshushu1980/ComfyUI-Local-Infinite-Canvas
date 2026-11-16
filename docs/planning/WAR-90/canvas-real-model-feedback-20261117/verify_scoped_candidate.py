#!/usr/bin/env python3
"""Independent evidence checks; this is not a film quality or user approval test."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path('/home/sean/projects/canvas-lab')
E=ROOT/'docs/planning/WAR-90/canvas-real-model-feedback-20261117'
base=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
branch=ROOT/'docs/planning/WAR-90/pilot-D-canvas-shot02-flowtest-20261117'
sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
from runtime import Pilot,shot_sections
p=Pilot(branch);candidate=p.load();approved=Pilot(base.parent).load()
m=json.loads((E/'model-result.json').read_text())
d=json.loads((E/'candidate-diff.json').read_text())
fb=json.loads((E/'feedback.json').read_text())
ca=json.loads((E/'canvas-display-audit.json').read_text())
old=approved['active']['artifacts']['shot']
new=candidate['active']['artifacts']['shot']
ids=['Shot01','Shot02','Shot03','Shot04']
o=shot_sections(old['proposal'],ids)
n=shot_sections(new['proposal'],ids)
checks={
 'baseline_authority_unchanged':hashlib.sha256(base.read_bytes()).hexdigest()=='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7',
 'baseline_still_approved':bool(approved['pilot_B']) and approved['phase']=='pilot-B-accepted',
 'isolated_branch_awaiting_real_human_review':candidate['phase']=='awaiting-human-B' and candidate['pilot_B'] is None,
 'no_formal_WAR35_authority':candidate.get('formal_WAR35_approval',False) is False,
 'real_model_generator':candidate['active']['generator']=='codex-cli' and m['metadata']['model']=='gpt-6-astra' and bool(m['metadata'].get('thread_id')),
 'branch_passes_integrity_check':True,
 'only_Shot02_edited':[i for i in ids if o[i]!=n[i]]==['Shot02'],
 'other_shots_byte_identical':all(o[x]==n[x] for x in ('Shot01','Shot03','Shot04')),
 'shot_list_stable':new['shot_ids']==old['shot_ids']==ids,
 'revised_Shot02_mentions_dynamic_handoff':all(x in n['Shot02'] for x in ['已接触','尚未完成','Shot03','轻理']),
 'Shot03_still_continues_and_stops_only_on_question':all(x in n['Shot03'] for x in ['右手仍空而轻理未停','周说“你刚刚是不是盖住了什么？”','停下右手']),
 'review_neighbors_tagged':candidate['pending_shots']==['Shot01','Shot02','Shot03'],
 'transport_feedback_is_synthetic':fb['origin']=='synthetic-test' and fb['human_B_decision'] is False and fb['actor_identity_verified'] is False,
 'canvas_display_audit_pass':ca['pass'] and ca['baseline_nodes_preserved'] and ca['post_node_count']==5,
 'candidate_preview_is_not_base_node':ca['display_node_id'] not in ca['baseline_node_ids'],
}
p.check(candidate)
assert m['metadata']['status']=='candidate-saved'
assert d['candidate_id']==candidate['active']['id']
out={'checks':checks,'pass':all(checks.values()),'candidate_id':candidate['active']['id'],
 'approved_B_id':approved['pilot_B']['id'],
 'changed_shots':[i for i in ids if o[i]!=n[i]],
 'review_neighbors':candidate['pending_shots'],
 'new_shot02_sha256':hashlib.sha256(n['Shot02'].encode()).hexdigest(),
 'old_shot02_sha256':hashlib.sha256(o['Shot02'].encode()).hexdigest(),
 'warning':'Static identity and token checks do not prove human acceptance, final editing permission, or actual film continuity.'}
(E/'scope-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('SCOPE_CHECK',{'pass':out['pass'],'count':len(checks),'bad':[k for k,v in checks.items() if not v],'candidate':out['candidate_id']})
if not out['pass']:sys.exit(2)

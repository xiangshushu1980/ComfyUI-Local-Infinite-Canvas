"""Verify the user-approved WAR-90 pilot B without altering prior audit evidence."""
import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parent
B=json.loads((E/'baseline.json').read_text());P=json.loads((R/'pilot-D/state.json').read_text())
S=json.loads((R/'pilot-D-local-repair-v2/state.json').read_text())
approval=json.loads((E/'pilot-B-accept-record-20261115.json').read_text())
pre=json.loads((E/'final-state-snapshot.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
def chk(n,v):checks[n]=bool(v);print(n,'OK' if v else 'FAIL')
chk('original_unchanged',sha(R/'pilot-D/state.json')==B['original_state_sha256'])
chk('old_B_unchanged',P['pilot_B']['id']==B['original_B_candidate'] and P['active']['id']==B['original_B_candidate'])
chk('same_active_new_candidate',S['active']['id']==pre['active']['id']==approval['candidate_id']=='b7b4fd156b884907b2431b6b1e0d9960')
chk('new_candidate_bytes_and_hash_preserved',S['active']==pre['active'] and approval['candidate_sha256']==S['active']['content_sha256'])
chk('A_baseline_kept',S['pilot_A']==pre['pilot_A'])
chk('B_recorded',S['phase']=='pilot-B-accepted' and S['pilot_B']==S['active'])
chk('B_gate_only_pilot',S['format']=='war90-pilot-only-v0' and S['formal_WAR35_approval'] is False and approval['formal_WAR35_approval'] is False)
chk('evidence_exact',sha(E/'user-B-approval-20261115.md')==approval['evidence_sha256'])
chk('user_text_present', '批准.' in (E/'user-B-approval-20261115.md').read_text())
chk('review_append_only',len(S['reviews'])==len(pre['reviews'])+1 and S['reviews'][:-1]==pre['reviews'] and S['reviews'][-1]==approval)
chk('review_explicit_human',approval['actor']=='human' and approval['checkpoint']=='B' and approval['decision']=='accept' and approval['identity_verified'] is False)
chk('single_B_in_history',sum(x['checkpoint']=='B' and x['decision']=='accept' for x in S['reviews'])==2)
chk('pending_cleared',not S['pending_shots'])
chk('stages_unchanged',S['active']['artifacts']['intent']==pre['active']['artifacts']['intent'] and S['active']['artifacts']['beat']==pre['active']['artifacts']['beat'] and S['active']['artifacts']['blocking']==pre['active']['artifacts']['blocking'] and S['active']['artifacts']['shot']==pre['active']['artifacts']['shot'])
chk('unknown_kept',S['unknown']==pre['unknown'])
chk('no_new_model_runs',S['runs']==pre['runs'])
result={'passed':sum(checks.values()),'total':len(checks),'checks':checks,'approved_candidate':S['active']['id'],'approval_sha':approval['evidence_sha256'],'original_workspace_sha':B['original_state_sha256']}
(E/'post-B-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('POST_B_VERIFIED',result['passed'],'/',result['total'])
if result['passed']!=result['total']:raise SystemExit(2)

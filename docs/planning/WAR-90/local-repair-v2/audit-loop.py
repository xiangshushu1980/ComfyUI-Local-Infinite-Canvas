"""WAR-90 independent local loop audit; no runtime mutations."""
from pathlib import Path
import json, hashlib, re
root=Path(__file__).resolve().parents[1]
ori=root/'pilot-D'
branch=root/'pilot-D-local-repair-v2'
out=Path(__file__).resolve().parent
before=json.loads((out/'baseline.json').read_text())
original=json.loads((ori/'state.json').read_text())
state=json.loads((branch/'state.json').read_text())
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
def ok(k,v,more=None):
 checks[k]={'ok':bool(v),'detail':more}
 if not v:print('FAIL',k,more)
ok('original_unmodified',h(ori/'state.json')==before['original_state_sha256'])
ok('historical_B_unchanged',original['pilot_B']['id']==before['original_B_candidate'] and original['active']['id']==before['original_B_candidate'])
ok('same_source_skill_hashes',original['inputs']==state['inputs'])
ok('pilot_A_authority_preserved',original['pilot_A']==state['pilot_A'])
ok('user_B_record_still_historical',any(x.get('checkpoint')=='B' and x.get('decision')=='accept' and x.get('candidate_id')==before['original_B_candidate'] for x in state['reviews']))
ok('new_B_not_self_approved',state['pilot_B'] is None and state['formal_WAR35_approval'] is False)
ok('new_candidate_at_shot',state['active'] is not None and state['active']['stage']=='shot' and state['phase']=='awaiting-human-B')
base=original['active']['artifacts']
live=state['active']['artifacts']
ok('source_B_intent_unchanged',base['intent']==live['intent'])
ok('source_B_beat_unchanged',base['beat']==live['beat'])
ok('blocking_revised',base['blocking']['proposal']!=live['blocking']['proposal'])
ok('shot_revised',base['shot']['proposal']!=live['shot']['proposal'])
ok('shot_order_preserved',base['shot']['shot_ids']==live['shot']['shot_ids']==['Shot01','Shot02','Shot03','Shot04'])
def shothunks(t):
 matches=list(re.finditer(r"(?m)^Shot0([1-4])[｜|：:]",t))
 return {f"Shot0{m.group(1)}":t[m.start():matches[i+1].start() if i+1<len(matches) else len(t)] for i,m in enumerate(matches)}
oldshoot=shothunks(base['shot']['proposal'])
newshoot=shothunks(live['shot']['proposal'])
ok('full_four_shot_sections',set(oldshoot)==set(newshoot)=={'Shot01','Shot02','Shot03','Shot04'})
ok('unchanged_Shot01_byte_exact',oldshoot.get('Shot01')==newshoot.get('Shot01') and len(oldshoot.get('Shot01',''))>300)
for k in ('Shot02','Shot03','Shot04'):
 ok('modified_'+k,oldshoot.get(k)!=newshoot.get(k) and len(newshoot.get(k,''))>500)
ok('shot2_actual_repair_semantics',all(term in newshoot.get('Shot02','') for term in ('让位','轻理','蓝夹','纸叠')))
ok('shot3_actual_repair_semantics',all(term in newshoot.get('Shot03','') for term in ('轻理','停','左手','钥匙')))
ok('shot4_actual_repair_semantics',all(term in newshoot.get('Shot04','') for term in ('前倾','右手','握稳','钥匙')))

ok('changed_target_subset',set(live['shot']['changed_targets'])<=set(['Shot02','Shot03','Shot04']))
ok('no_upstream_hard_conflict',not live['blocking']['hard_conflicts'] and not live['shot']['hard_conflicts'] and not live['blocking']['upstream_change'] and not live['shot']['upstream_change'])
ok('whole_blocking_proposal',all('BLOCKING-'+str(i).zfill(2) in live['blocking']['proposal'] for i in range(1,7)))
ok('shot_has_all_four',all('Shot'+str(i).zfill(2) in live['shot']['proposal'] for i in range(1,5)))
ok('pilot_unknown_kept',set(original['unknown'])<=set(state['unknown']))
ok('formal_approval_false',state['formal_WAR35_approval'] is False)
ok('pending_neighbors_kept',set(['Shot01','Shot02','Shot03','Shot04'])<=set(state['pending_shots']),state['pending_shots'])
newruns=state['runs'][len(original['runs']):]
ok('exactly_two_new_calls',len(newruns)==2,[(r.get('stage'),r.get('status')) for r in newruns])
ok('both_real_resumes',len(newruns)==2 and all(r.get('generator')=='codex-cli' and r.get('status')=='candidate-saved' and r.get('mode')=='resume' and r.get('thread_id') for r in newruns))
ok('new_inputs_outputs_saved',all((branch/'runs'/r['id']/'input.txt').is_file() and (branch/'runs'/r['id']/'result.txt').is_file() and (branch/'runs'/r['id']/'candidate.json').is_file() for r in newruns))
ok('candidate_content_sha',h(ori/'state.json')==before['original_state_sha256'] and state['active']['content_sha256']==hashlib.sha256((json.dumps(live,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest())
ok('no_extra_human_B',not any(r.get('checkpoint')=='B' and r.get('candidate_id')==state['active']['id'] for r in state['reviews']))
result={'passed':sum(x['ok'] for x in checks.values()),'total':len(checks),'checks':checks,
 'original_B_candidate_id':before['original_B_candidate'],'new_candidate_id':state['active']['id'] if state['active'] else None,
 'new_run_ids':[r['id'] for r in newruns],'pending_shots':state['pending_shots']}
(out/'loop-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('LOOP_AUDIT',result['passed'],'/',result['total'])
if result['passed']!=result['total']:raise SystemExit(2)

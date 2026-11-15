"""Compare frozen full-context Astra pilot to freshly generated compact-context pilot.

Evidence-only: no model calls, no B acceptance, no mutation of the pilot states.
Textual/transport checks are NOT proof of cinematic or audience quality.
"""
from pathlib import Path
import json,hashlib,re,datetime
PROJECT=Path('/home/sean/projects/canvas-lab')
P=PROJECT/'docs/planning/WAR-90'
OUT=P/'compact-live-20261115'
F=P/'local-repair-v2/evidence'
W=P/'pilot-D-compact-live-20261115'
S_OLD=P/'pilot-D/state.json'
S_APPROVED=P/'pilot-D-local-repair-v2/state.json'
b=json.loads((OUT/'baseline.json').read_text())
orig=json.loads(S_OLD.read_text())
approved=json.loads(S_APPROVED.read_text())
current=json.loads((W/'state.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S_OLD)==b['original_sha256']
assert sha(S_APPROVED)==b['approved_new_B_sha256']
assert current['pilot_A']==orig['pilot_A']
assert current['inputs']==orig['inputs']
assert current['formal_WAR35_approval'] is False
assert current['pilot_B'] is None
assert current['active'] and current['active']['stage']=='shot'
archive={x:json.loads((F/x/'metadata.json').read_text()) for x in (
'ecc8a553cd0543eaa39448b0c922a44e','b7b4fd156b884907b2431b6b1e0d9960')}
new_runs=current['runs'][len(orig['runs']):]
assert [x['stage'] for x in new_runs]==['blocking','shot']
assert all(x['generator']=='codex-cli' and x['status']=='candidate-saved' for x in new_runs)
def duration(record):
 return round((datetime.datetime.fromisoformat(record['finished_at'])-
  datetime.datetime.fromisoformat(record['started_at'])).total_seconds(),3)
def sections(text):
 hits=list(re.finditer(r'(?m)^Shot0([1-4])[｜|：:]',text))
 if [x.group(1) for x in hits]!=['1','2','3','4']:
  raise AssertionError('Missing or ambiguous Shot headings')
 return {f'Shot0{h.group(1)}':text[h.start():hits[i+1].start() if i<len(hits)-1 else len(text)]
         for i,h in enumerate(hits)}
old_base=sections(orig['active']['artifacts']['shot']['proposal'])
full=sections(approved['active']['artifacts']['shot']['proposal'])
compact=sections(current['active']['artifacts']['shot']['proposal'])
observations={}
for k in ('Shot01','Shot02','Shot03','Shot04'):
 observations[k]={
   'base_length':len(old_base[k]),
   'full_length':len(full[k]),
   'compact_length':len(compact[k]),
   'full_unchanged_base':full[k]==old_base[k],
   'compact_unchanged_base':compact[k]==old_base[k],
   'full_and_compact_same':full[k]==compact[k],
   'full_changed_base':full[k]!=old_base[k],
   'compact_changed_base':compact[k]!=old_base[k]}
assert observations['Shot01']['full_unchanged_base']
assert observations['Shot01']['compact_unchanged_base']
assert all(observations[k]['compact_changed_base'] and observations[k]['full_changed_base']
           for k in ('Shot02','Shot03','Shot04'))
source=(W/'source.txt').read_text()
def stat(t):
 return {'characters':len(t),'lines':len(t.splitlines())}
def cues(stage,proposal):
 if stage=='shot':
  sec=sections(proposal)
  return {
   'Shot02_late_reposition':any(x in sec['Shot02'] for x in ('让位','后退','侧后')),
   'Shot02_cover':all(x in sec['Shot02'] for x in ('夹','纸叠','K')),
   'Shot02_right_hand_activity':all(x in sec['Shot02'] for x in ('右手','轻理')),
   'Shot03_question':('你刚刚是不是盖住了什么' in sec['Shot03']),
   'Shot03_interrupt_motion':all(x in sec['Shot03'] for x in ('停','轻理')),
   'Shot03_left_hand_lift':all(x in sec['Shot03'] for x in ('左手','夹')),
   'Shot03_Lin_discovers_after_question':'首次' in sec['Shot03'] or '第一次' in sec['Shot03'],
   'Shot03_fourth_line':'找到了' in sec['Shot03'],
   'Shot04_forward_lean':'前倾' in sec['Shot04'],
   'Shot04_single_right_handoff':all(x in sec['Shot04'] for x in ('周','右手','钥匙','松')),
   'Shot04_ownership_sequence':'shared' in sec['Shot04'] or '共同' in sec['Shot04'],
   'Shot04_to_door':'门' in sec['Shot04']
  }
 return {
  'six_BLOCKING_segments':all('BLOCKING-'+str(i).zfill(2) in proposal for i in range(1,7)),
  'late_reposition':'让位' in proposal,
  'sorting_continuation':'轻理' in proposal,
  'right_hand_transfer':'右手' in proposal,
  'left_hand_folder':'左手' in proposal,
 }
comparison={}
for pair in zip(('blocking','shot'),archive.values(),new_runs):
 stage,arch,live=pair
 assert arch['stage']==stage==live['stage']
 assert arch['model']==live['model']=='gpt-6-astra'
 assert arch['reasoning_effort']==live['reasoning_effort']=='medium'
 assert arch['scope']==live['scope'], 'Scopes changed -- invalid paired comparison'
 assert arch['targets']==live['targets']==['Shot02','Shot03','Shot04']
 assert live['mode']=='resume'==arch['mode']
 assert live['context_profile']=='war90-local-compact-v1'
 a_prompt=(F/arch['id']/'input.txt')
 a_result=(F/arch['id']/'result.txt')
 l_prompt=W/'runs'/live['id']/'input.txt'
 l_result=W/'runs'/live['id']/'result.txt'
 assert sha(a_prompt)==arch['input_sha256'] and sha(a_result)==arch['result_sha256']
 assert sha(l_prompt)==live['input_sha256'] and sha(l_result)==live['result_sha256']
 old_obj=json.loads(a_result.read_text())
 new_obj=json.loads(l_result.read_text())
 assert old_obj['handoff'] and new_obj['handoff']
 assert not old_obj['hard_conflicts'] and not new_obj['hard_conflicts']
 assert not old_obj['upstream_change'] and not new_obj['upstream_change']
 assert set(new_obj['changed_targets'])<=set(live['targets'])
 assert set(old_obj['changed_targets'])<=set(arch['targets'])
 if stage=='shot':
  assert new_obj['shot_ids']==old_obj['shot_ids']==['Shot01','Shot02','Shot03','Shot04']
  assert live.get('verified_changed_shots')==['Shot02','Shot03','Shot04']
 comparison[stage]={
  'model':arch['model'], 'reasoning_effort':arch['reasoning_effort'],
  'same_exact_scope':arch['scope']==live['scope'],
  'same_frozen_source_inputs':current['inputs']==orig['inputs'],
  'full_reference_run_id':arch['id'], 'compact_fresh_run_id':live['id'],
  'full_prompt_bytes':a_prompt.stat().st_size,'compact_prompt_bytes':l_prompt.stat().st_size,
  'bytes_reduction_pct':round(100*(1-l_prompt.stat().st_size/a_prompt.stat().st_size),2),
  'full_seconds':duration(arch),'compact_seconds':duration(live),
  'seconds_delta':round(duration(live)-duration(arch),3),
  'latency_reduction_pct':round(100*(1-duration(live)/duration(arch)),2),
  'full_proposal':stat(old_obj['proposal']),
  'compact_proposal':stat(new_obj['proposal']),
  'full_cues':cues(stage,old_obj['proposal']),
  'compact_cues':cues(stage,new_obj['proposal']),
  'new_output_sha256':sha(l_result),
  'full_output_sha256':sha(a_result),
  'has_hard_conflict':bool(new_obj['hard_conflicts']),
  'has_upstream_change':new_obj['upstream_change'],
  'compact_unknown_count':len(new_obj['unknown']),
  'full_unknown_count':len(old_obj['unknown']),
 }
results={'study':'WAR-90 compact live vs archived full one-pair comparison',
 'note':'Single non-randomized matched-scope historical comparison, not controlled latency or quality equivalence proof.',
 'original_B_state_sha256':sha(S_OLD),
 'approved_new_B_state_sha256':sha(S_APPROVED),
 'compact_local_state_sha256':sha(W/'state.json'),
 'real_new_calls':2, 'raw_model_calls_not_fake':True,
 'branch_phase':current['phase'], 'branch_newB':current['pilot_B'] is not None,
 'original_B_preserved':orig['phase']=='pilot-B-accepted',
 'new_approved_B_preserved':approved['phase']=='pilot-B-accepted',
 'working_candidate_id':current['active']['id'],
 'pending_shots':current['pending_shots'],
 'comparisons':comparison,'shots':observations,
 'not_proven':['Real model quality equivalence: lexical cues are not semantic tests',
 'Runtime speed due to prompt: model jitter/time of day/queue can affect two samples',
 'Four-shot final audience readability, natural continuous animation, media quality']}
(OUT/'comparison.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('COMPARE_REAL_MODEL_CALLS',results['real_new_calls'])
for st,c in comparison.items(): print(st,'PROMPTS',c['full_prompt_bytes'],c['compact_prompt_bytes'],'SECONDS',c['full_seconds'],c['compact_seconds'],
 'CUES',sum(c['compact_cues'].values()),'/',len(c['compact_cues']))
print('SHOT01_EXACT',observations['Shot01']['compact_unchanged_base'])
print('NO_B_APPROVAL',not results['branch_newB'])

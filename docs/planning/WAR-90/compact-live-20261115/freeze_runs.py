"""Freeze real compact live call evidence without changing approved workspaces."""
from pathlib import Path
import json,hashlib,shutil,os
P=Path('/home/sean/projects/canvas-lab/docs/planning/WAR-90')
E=P/'compact-live-20261115'
W=P/'pilot-D-compact-live-20261115'
old=json.loads((P/'pilot-D/state.json').read_text())
s=json.loads((W/'state.json').read_text())
assert s['active']['stage']=='shot' and s['phase']=='awaiting-human-B' and s['pilot_B'] is None
new=s['runs'][len(old['runs']):]
assert len(new)==2 and [x['stage'] for x in new]==['blocking','shot']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for item in new:
 assert item['generator']=='codex-cli' and item['status']=='candidate-saved'
 source=W/'runs'/item['id']
 target=E/'evidence'/item['id']
 target.mkdir(parents=True,exist_ok=True)
 for name in ['input.txt','result.txt','events.jsonl','stderr.txt',
              'metadata.json','candidate.json','command.json']:
  f=source/name
  assert f.is_file(),f
  shutil.copyfile(f,target/name)
 assert sha(target/'input.txt')==item['input_sha256']
 assert sha(target/'result.txt')==item['result_sha256']
 assert not (source/'.codex-home').exists()
shutil.copyfile(W/'state.json',E/'final-experiment-state.json')
sums={'old_original_sha':sha(P/'pilot-D/state.json'),
 'new_approved_sha':sha(P/'pilot-D-local-repair-v2/state.json'),
 'compact_experiment_sha':sha(W/'state.json'),
 'call_metadata':[{x:item.get(x) for x in
   ('stage','id','model','reasoning_effort','generator','status',
    'started_at','finished_at','input_sha256','result_sha256','thread_id',
    'prompt_bytes','context_profile','verified_changed_shots')} for item in new],
 'approval_not_granted':s['pilot_B'] is None,
 'four_shot_pending':s['pending_shots']}
(E/'frozen-runs-summary.json').write_text(json.dumps(sums,ensure_ascii=False,indent=2)+'\n')
print('FROZEN_LIVE_EVIDENCE',len(new),'REAL_RUNS')
print('NO_AUTH_COPIES',True)

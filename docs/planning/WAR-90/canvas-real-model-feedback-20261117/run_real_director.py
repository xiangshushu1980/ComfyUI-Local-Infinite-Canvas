#!/usr/bin/env python3
"""Generate a genuinely model-produced, unapproved isolated Shot02 candidate.
Pilot.run uses real Eric Codex CLI gpt-6-astra; not a fake generator.
"""
from pathlib import Path
import json,sys,time,hashlib,traceback
ROOT=Path('/home/sean/projects/canvas-lab')
HERE=ROOT/'docs/planning/WAR-90/canvas-real-model-feedback-20261117'
sys.path.insert(0,str(ROOT/'docs/planning/WAR-90/canvas-feedback-20261115'))
sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
from feedback_bridge import approved_packet,stage_scope,validate_feedback,compare_local_revision
from runtime import Pilot
source=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
bsha='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
workspace=ROOT/'docs/planning/WAR-90/pilot-D-canvas-shot02-flowtest-20261117'
meta_path=HERE/'model-result.json'
if meta_path.exists():raise RuntimeError('Already ran: refuse duplicate model action')
packet=approved_packet()
fb=json.loads((HERE/'feedback.json').read_text())
validate_feedback(packet,fb)
assert fb['origin']=='synthetic-test' and fb['human_B_decision'] is False
assert fb['target_shot_id']=='Shot02'
assert hashlib.sha256(source.read_bytes()).hexdigest()==bsha
p=Pilot(workspace);st=p.load()
assert st['active']['id']==fb['base_B_id'] and st['pilot_B'] and st['phase']=='pilot-B-accepted'
started=time.monotonic()
(HERE/'model-invocation-marker.json').write_text(json.dumps({'generator':'real-codex-cli','model':'gpt-6-astra','stage':'shot',
 'target':'Shot02','started_at_unix':time.time(),
 'feedback_origin':'synthetic-test','human_approval':False},indent=2)+'\n')
try:
 metadata=p.run('shot',mode='resume',scope=stage_scope(packet,fb),targets=['Shot02'])
 result={'metadata':metadata,'elapsed_seconds':round(time.monotonic()-started,2),'source_b_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==bsha}
 if metadata['status']=='candidate-saved':
  diff=compare_local_revision(packet,fb,workspace)
  (HERE/'candidate-diff.json').write_text(json.dumps(diff,ensure_ascii=False,indent=2)+'\n')
  result['candidate_id']=diff['candidate_id']
  result['changed_shots']=diff['changed_shots']
  result['pending_review_shots']=diff['pending_review_shots']
  result['diff_lines']=len(diff['diff'].splitlines())
  result['status']='candidate-ready-for-human-review'
 elif metadata['status']=='no-handoff':
  result['status']='agent-declined-revision'
 else:result['status']='unexpected-pilot-status'
 (meta_path).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('DIRECTOR_REAL_MODEL',json.dumps({k:result.get(k) for k in ['status','elapsed_seconds','candidate_id','changed_shots','pending_review_shots','diff_lines','source_b_unchanged']},ensure_ascii=False),flush=True)
 if result['status'] not in ['candidate-ready-for-human-review','agent-declined-revision']:sys.exit(2)
except BaseException as e:
 (HERE/'model-error.json').write_text(json.dumps({'errorType':type(e).__name__,'error':str(e)[:700],
  'source_b_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==bsha},indent=2)+'\n')
 traceback.print_exc()
 raise

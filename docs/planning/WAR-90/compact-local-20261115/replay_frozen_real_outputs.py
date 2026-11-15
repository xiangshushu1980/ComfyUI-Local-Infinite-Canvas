"""WAR-90: replay two previously REAL saved model responses through NEW runtime.
This is an offline generator replay, not a fresh model-inference test.
Never mutate the already approved real workspaces.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
sys.dont_write_bytecode = True
PROJECT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT/'tools/director-runtime-v0'))
from runtime import PILOTS,Pilot

R=PROJECT/'docs/planning/WAR-90'
OUT=Path(__file__).resolve().parent
ORIG=R/'pilot-D'
STORED=R/'local-repair-v2'
CALLS=[
    ('blocking', 'ecc8a553cd0543eaa39448b0c922a44e', 'blocking-scope.md'),
    ('shot', 'b7b4fd156b884907b2431b6b1e0d9960', 'shot-scope.md')]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
initial_sha=sha(ORIG/'state.json')
target=['Shot02','Shot03','Shot04']
results=[]
with tempfile.TemporaryDirectory(prefix='.replay-local-',dir=PILOTS) as td:
    workspace=Path(td)/'pilot'
    shutil.copytree(ORIG,workspace)
    pilot=Pilot(workspace)
    assert pilot.status()['gates']['B'] is True
    for stage,ref,scope_file in CALLS:
        scope=(STORED/scope_file).read_text().rstrip('\n')
        current=pilot.load()
        compact=pilot.packet(current,stage,'resume',scope,target)
        old_original=STORED/'evidence'/ref/'input.txt'
        old_result=STORED/'evidence'/ref/'result.txt'
        old_meta=json.loads((STORED/'evidence'/ref/'metadata.json').read_text())
        assert sha(old_original)==old_meta['input_sha256']
        assert sha(old_result)==old_meta['result_sha256']
        def replay(prompt,run_dir):
            assert 'war90-local-compact-v1' in prompt
            assert prompt==compact
            (run_dir/'events.jsonl').write_text('{"source":"frozen-real-response","replay":true}\n')
            return old_result.read_text(), 'OFFLINE-REPLAY-NO-MODEL-SESSION'
        actual=pilot.run(stage,mode='resume',scope=scope,targets=target,generator=replay)
        check=pilot.load()
        result={'stage':stage,'archived_real_call_id':ref,
                'archived_real_model':old_meta['model'],
                'frozen_real_output_sha256':sha(old_result),
                'old_input_bytes':old_original.stat().st_size,
                'new_compact_input_bytes':len(compact.encode()),
                'reduction_pct':round(100*(1-len(compact.encode())/old_original.stat().st_size),2),
                'new_code_metadata_profile':actual['context_profile'],
                'generator':'offline archived real response replay (not new inference)',
                'new_code_candidate_status':actual['status'],
                'verified_changed_shots':actual.get('verified_changed_shots',[]),
                'candidate_shot_ids':check['active']['artifacts']['shot']['shot_ids'],
                'new_candidate_approval':check['pilot_B'] is not None,
                'new_candidate_phase':check['phase'],
                'pending_shots':check['pending_shots']}
        assert actual['status']=='candidate-saved'
        assert actual['context_profile']=='war90-local-compact-v1'
        assert check['pilot_B'] is None
        assert set(check['pending_shots'])==set(['Shot01','Shot02','Shot03','Shot04'])
        if stage=='shot':
            assert actual['verified_changed_shots']==target
            original=json.loads((ORIG/'state.json').read_text())['active']['artifacts']['shot']['proposal']
            new=check['active']['artifacts']['shot']['proposal']
            from runtime import shot_sections
            assert shot_sections(original,['Shot01','Shot02','Shot03','Shot04'])['Shot01']==shot_sections(new,['Shot01','Shot02','Shot03','Shot04'])['Shot01']
        results.append(result)
        print('REPLAY',stage,'archived',result['old_input_bytes'],
              'compact',result['new_compact_input_bytes'],
              'percent',result['reduction_pct'],'status',actual['status'])
    assert sha(ORIG/'state.json')==initial_sha
assert sha(ORIG/'state.json')==initial_sha
report={'date':'2026-11-15',
  'kind':'offline replay of two frozen real Astra responses, not fresh model call',
  'frozen_original_state_sha256':initial_sha,
  'source_was_left_unchanged':True,'real_user_B_not_reapproved_by_replay':True,
  'results':results,'limitations':[
    'Byte reduction is measured, but actual model latency/tokens/quality for compact prompts are unmeasured.',
    'Frozen model outputs were generated under the old full packet; replay validates runtime compatibility only.',
    'Freeform preamble and outro continuity remain human/professional review, not formal WAR-35 checks.']}
(OUT/'replay-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('REPLAY_SUCCEEDED')

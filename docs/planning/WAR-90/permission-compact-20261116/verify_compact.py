"""Read-only audit of the real approved B pilot; records no auth secrets."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/permission-compact-20261116'
PILOT=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2'
CLI=ROOT/'tools/director-runtime-v0/cli.py'
def snapshot():
    return {str(p.relative_to(PILOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in PILOT.rglob('*') if p.is_file()}
before=snapshot()
assert before.get('state.json')=='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
results={}
for target in ('Shot01','Shot02','Shot03','Shot04','Shot99'):
    r=subprocess.run([sys.executable,str(CLI),'review-shot','--workspace',str(PILOT),
                      '--shot-id',target],capture_output=True,text=True,timeout=25)
    if target=='Shot99':
        assert r.returncode==2 and 'Blocked: Unknown approved Shot' in r.stderr
        results[target]={'code':r.returncode,'blocked':True,'stdout_empty':not r.stdout}
    else:
        assert r.returncode==0,r.stderr
        data=json.loads(r.stdout)
        assert data['target_shot']['id']==target
        assert data['pilot_only'] is True
        assert data['review_flags']['formal_WAR35_approval'] is False
        assert data['review_flags']['identity_verified'] is False
        assert data['capabilities']['write_canvas'] is False
        assert hashlib.sha256(data['target_shot']['text'].encode()).hexdigest()==data['target_shot']['text_sha256']
        results[target]={'code':r.returncode,'bytes':len(r.stdout.encode()),
                         'target_sha256':data['target_shot']['text_sha256'],
                         'source_sha256':data['source']['sha256'],
                         'unknown_count':data['review_flags']['unknown_count'],
                         'trial_only':True}
after=snapshot()
assert before==after,({'added':list(after.keys()-before.keys())})
result={'purpose':'real CLI read-only pilot audit; no candidate generated or modified',
        'baseline_file_count':len(before),
        'pilot_all_file_hashes_unchanged':True,
        'pilot_state_sha256':before['state.json'],
        'test_results':results,'formal_WAR35_approval':False}
(OUT/'compact-cli-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('COMPACT_CLI_AUDIT',json.dumps(result,ensure_ascii=False))

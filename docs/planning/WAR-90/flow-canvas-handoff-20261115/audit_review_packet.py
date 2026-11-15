"""WAR-90 read-only B review packet preflight using REAL approved pilot state."""
import subprocess,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
CLI=ROOT/'tools/director-runtime-v0/cli.py'
ROOT_P=ROOT/'docs/planning/WAR-90'
paths={
'original_B':ROOT_P/'pilot-D',
'approved_new_B':ROOT_P/'pilot-D-local-repair-v2',
'unapproved_compact_candidate':ROOT_P/'pilot-D-compact-live-20261115',
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
def check(label,condition,detail=None):
 checks[label]={'ok':bool(condition),'detail':detail}
 if not condition: print('FAIL',label,detail)
baseline={key:sha(path/'state.json') for key,path in paths.items()}
results={}
for key,path in paths.items():
 run=subprocess.run(['python3',str(CLI),'review-pack','--workspace',str(path)],
                    capture_output=True,text=True,check=False)
 if key=='unapproved_compact_candidate':
  check('unapproved_rejected',run.returncode==2 and 'Blocked:' in run.stderr,
        {'return_code':run.returncode,'stderr':run.stderr.strip()[:400]})
 else:
  check('approved_'+key+'_allowed',run.returncode==0,run.stderr.strip()[:400])
  if run.returncode==0:results[key]=json.loads(run.stdout)
 check('state_unchanged_'+key,sha(path/'state.json')==baseline[key])
if len(results)==2:
 new=results['approved_new_B']
 old=results['original_B']
 fromhash='b7b4fd156b884907b2431b6b1e0d9960'
 check('new_B_correct_binding',new['authority']['approved_B_id']==fromhash)
 check('original_B_still_independent',old['authority']['approved_B_id']!=fromhash)
 check('pilot_only_disclaimer',new['format']=='war90-director-preview-only-v0'
       and new['review']['formal_WAR35_approval'] is False
       and new['review']['identity_verified'] is False)
 check('no_external_actions',new['capabilities']['display_text'] is True and
       all(new['capabilities'][x] is False for x in
           ('propose_edit','write_canvas','generate_media','production_approval')))
 check('four_ordered_shots',[x['id'] for x in new['shots']]==
       ['Shot01','Shot02','Shot03','Shot04'])
 check('full_stage_texts',set(new['stages'])==
       {'intent','beat','blocking','shot'} and
       all(len(x['text'])>300 for x in new['stages'].values()))
 check('source_canonical_hash',
       hashlib.sha256(new['authority']['source_text'].encode()).hexdigest()==
       new['authority']['source_sha256'])
 check('all_stage_and_shot_text_hashes', all(
       hashlib.sha256(stage['text'].encode()).hexdigest()==stage['text_sha256']
       for stage in new['stages'].values()) and all(
       hashlib.sha256(shot['text'].encode()).hexdigest()==shot['text_sha256']
       for shot in new['shots']))
 check('risk_unknown_preserved',
       len(new['review']['unknown'])>=3 and
       new['review']['media_verified'] is False and
       new['review']['geometry_verified'] is False and
       new['review']['audience_verified'] is False)
 (OUT/'approved-B-review-preview.json').write_text(
       json.dumps(new,ensure_ascii=False,indent=2)+'\n')
result={'checks':checks,'passed':sum(v['ok'] for v in checks.values()),
        'total':len(checks),'baseline_state_sha256':baseline,
        'approved_packet_sha256':sha(OUT/'approved-B-review-preview.json')
         if (OUT/'approved-B-review-preview.json').exists() else None,
        'data_only_no_canvas_API_call':True}
(OUT/'review-preflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('REVIEW_PREFLIGHT',result['passed'],'/',result['total'])
print('APPROVED_PACKET_SHA',result['approved_packet_sha256'])
if result['passed']!=result['total']:raise SystemExit(2)

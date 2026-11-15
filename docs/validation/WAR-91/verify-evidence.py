"""WAR-91: deterministic offline checks of frozen actual Blender V1 output."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
one=json.loads((root/'v1/results.json').read_text())
two=json.loads((root/'v1/followup-audit.json').read_text())
third=json.loads((root/'v1/new-camera-full-sequence.json').read_text())
counter=0
def check(ok,label):
 global counter
 assert ok,label
 counter+=1
 print('PASS',label)
check(one['source_sha256']=='23fc26a252390e73ac50efd16001248ceec362bd0d590f16dbbe8a16385a0373','frozen old B proxy sha')
check(one['device']=='CPU' and one['engine']=='CYCLES' and one['threads']==2,'CPU only engine threads')
check(one['resolution']==[960,540] and len(one['candidate_cameras'])==2,'960x540 at most two new cameras')
check(all(r['key_sample_clear_9']==0 for r in one['shot02_rows'] if r['frame']==1),'initial paper fully conceals')
check(all(r['key_sample_clear_9']==9 for r in one['shot02_rows'] if r['frame']==20),'revealed reference frame clear')
check(all(r['key_sample_clear_9']==0 for r in one['shot02_rows'] if r['frame']==40),'blue folder obscures K')
check(abs(two['support_correction']['folder_bottom_minus_moved_paper_top_m'])<.0001,'folder reaches movable paper top')
check(two['support_correction']['folder_moved_paper_overlap_xy_m2']>0,'folder and paper overlap XY')
check(two['support_correction']['folder_bottom_minus_underlying_stack_top_m']>0,'lower stack not actual contact top')
check(all(e['clear_or_folder_visible_of_25']==0 for p in two['folder_visibility_25_spots_5_path'] for e in p['eyes']),'old stance Zhou folder occluded at five path samples')
check(all(p['both_key_blocked_by_lin'] for p in one['zhou_path_eye_samples']),'old stance Zhou K 21 points both frames')
check(one['handoff_C2']['old_lin_right_shoulder_to_K_m']>.77,'static right shoulder cannot reach K')
check(one['handoff_C2']['actual_3d_right_hand_pickup_and_finger_contact'].startswith('NOT_TESTED'),'right hand actual grab correctly untested')
check(one['continuity_C1']['status'].startswith('UNTESTED'),'new four-shot cut action not falsely tested')
check(len(third['rows'])==80,'two new cameras x full 40 frame sequence')
for cam in ('WAR91_Action40','WAR91_Desk40'):
 rows=[r for r in third['rows'] if r['camera']==cam]
 check(len(rows)==40 and [x['frame'] for x in rows]==list(range(1,41)),'all 40 frames '+cam)
 m={r['frame']:r['clear_9'] for r in rows}
 check(all(m[f]==0 for f in range(1,5)) and m[5]==6 and m[6]==9,'first reveal is measured '+cam)
 check(m[37]==3 and all(m[f]==0 for f in range(38,41)),'re-cover transition measured '+cam)
check(one['baseline_B_run']=='d23b8bdab90f43ef8ff0098fb8021f78','approved B identity')
check((root/'review-v1/main-reconsideration/result.md').exists(),'actual independent lead reconsideration saved')
print('WAR91_CHECKS_OK',counter)

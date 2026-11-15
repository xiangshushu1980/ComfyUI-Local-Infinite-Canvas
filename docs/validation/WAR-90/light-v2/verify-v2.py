"""WAR-90 light V2 independent static result checks; no Blender or media."""
import json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=ROOT.parents[1]
a=json.loads((ROOT/'v2-geometry.json').read_text())
b=json.loads((ROOT/'v2-sweep.json').read_text())
old=json.loads((ROOT/'v2-sweep-source-arm-baseline.json').read_text())
scan=json.loads((ROOT/'obs-scan.json').read_text())
src=P/'WAR-91/v1/WAR91_derived_cameras.blend'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
expected='a4c7b48a9dac825c5422c626b17242599eeacbb9115eb640fe8d7f20e34f75a3'
checks={}
def check(tag,cond,detail=None):
 checks[tag]={'pass':bool(cond),'detail':detail}
 if not cond:print('FAIL',tag,detail)
check('source_exact',sha(src)==expected and a['source_blend_sha256']==expected and b['source_sha256']==expected)
check('not_production',a['approved_B_modified'] is False and a['evidence_status']=='candidate, not approved')
check('camera_original_reveal',all(v['clear_9']==9 for v in a['first_reveal']['camera_K'].values()))
check('zhou_cannot_see_first_K',all(str(x['key_ray_occluder']).startswith('LIN_') for x in a['first_reveal']['zhou_eyes']))
check('original_covered_zhou_blocked',all(x['folder_visible_of_25']==0 for x in a['baseline_covered']['zhou_eyes']))
check('cover_camera_K_hidden',all(v['clear_9']==0 for v in a['baseline_covered']['camera_K'].values()))
check('obs_after_cover', min(x['folder_visible_of_25'] for x in a['obs']['eyes'])>=15)
check('obs_K_still_covered',all(x['key_ray_occluder']=='BLUE_FOLDER' for x in a['obs']['eyes']))
check('obs_target_unblocked',all(x['covered_xy_target_hit'] is None for x in a['obs']['eyes']))
check('obs_repair_not_source_teleport', a['obs']['change'].startswith('Lin proxy body steps'))
check('baseline_arm_earlier_fail_preserved',any('LIN_R_FOREARM' in x['lin_desk_crossings'] for x in old['Lin_step_after_cover']))
check('swept_step_no_actor_body_contact',all(not x['actor_mesh_crossings'] for x in b['Lin_step_after_cover']))
check('swept_step_no_desk_contact',all(not x['lin_desk_crossings'] for x in b['Lin_step_after_cover']))
check('swept_step_never_K_reveal',all(set(x['cam_K_hits'].values())=={'BLUE_FOLDER'} for x in b['Lin_step_after_cover']))
check('swept_step_end_zhou_covered_target',all(x['folder_xy_hit'] is None for x in b['Lin_step_after_cover'][-1]['eyes']))
check('folder_uncover_no_key_contact',all(not any(x['folder_key_mesh_intersection'].values()) for x in b['folder_uncover_translation']))
check('folder_uncover_camera_K_clean',all(all(z is None for z in x['camera_to_K'].values()) for x in b['folder_uncover_translation'][2:]))
check('key_transfer_reach_along_samples',max(x['Lin_arm_reach_m'] for x in b['key_transfer_proxy_line'])<.77,
 round(max(x['Lin_arm_reach_m'] for x in b['key_transfer_proxy_line']),5))
check('transfer_zhu_right_reach',b['Zhou_right_shoulder_to_transfer_m']<.77)
check('key_lift_no_intermediate_collisions',all(all(x['key_mesh_surface_intersections'][k]==0 for k in ['DESK_TOP','PAPER_MOVING','BLUE_FOLDER','LIN_TORSO','ZHOU_TORSO']) for x in b['key_transfer_proxy_line'][1:]))
check('key_rest_contact_exception',b['key_transfer_proxy_line'][0]['key_mesh_surface_intersections']['DESK_TOP']>0,
 'K initial resting on table; prior known mesh surface overlap at f40')
st=a['stages'];by={x['label']:x for x in st}
check('joins_equal',all(a['joins'].values()))
check('key_unchanged_until_pick',all(by[n]['key_all_mesh_origins']==by['S02-out']['key_all_mesh_origins'] for n in ['S03-in','S03-out','S04-in','S04-pre-pick']))
check('key_single_owner_sequence',a['single_transfer']['completed_world_ownership_transfers']==1 and a['single_transfer']['owners_sequence']==['table','table','table','Lin-right','Lin-right+Zhou-right','Zhou-right'])
check('end_Zhou_owner',by['S04-Zhou-right']['key_owner']=='Zhou-right')
check('right_retracts_clear_of_key',math.dist(by['S04-Zhou-right']['lin_right_hand'],a['reach']['handoff_key_xyz'])>.30,
 round(math.dist(by['S04-Zhou-right']['lin_right_hand'],a['reach']['handoff_key_xyz']),4))
check('pose_no_table_surface_contact',all(not any(x['lin_contacts_with_desk'].values()) for x in st))
check('lin_reaches_pick_and_handoff',a['reach']['Lin_pickup']['right']['reach_le_0p77'] and a['reach']['handoff_Lin']['right']['reach_le_0p77'])
check('source_has_no_zhou_arms_recorded',any('Zhou arms/rig' in s for s in a['open_risks']))
result={'passed':sum(c['pass'] for c in checks.values()),'total':len(checks),
 'checks':checks,'scope':'proxy geometry and discrete semantic seams; no production camera sequence or timed animation'}
(ROOT/'verification-v2.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('V2_ASSERTIONS',result['passed'],'/',result['total'])
if result['passed']!=result['total']:raise SystemExit(2)

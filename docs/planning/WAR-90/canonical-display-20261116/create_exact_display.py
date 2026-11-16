#!/usr/bin/env python3
"""User-authorized, one-time canonical Canvas Lab display creation.

Run only against the Windows browser at canvas.localhost opened during this
conversation. Browser project IDs and client IDs are strict; caller is the
ChatGPT DCR session, writing through the actual Canvas Agent tool transport.
No model transcription, no media generation, no Director Runtime mutation.
"""
from __future__ import annotations
import hashlib,json,sys,time,traceback
from pathlib import Path
import requests
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/canonical-display-20261116'
SRC=ROOT/'docs/planning/WAR-90/live-b-projection-20261116'
sys.path.insert(0,str(SRC))
from prepare_projection import payload
PROJECT='2FwEbySI5PYe7d6BL4pES'
CLIENT='jeUNwaV-t0QApaAKC2pMh'
BASE_SHA='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
url=cfg['url'].rstrip('/')
audit_path=OUT/'creation-audit.json'
audit={'purpose':'create 4 approved B text display nodes in canonical Windows browser Canvas Lab',
       'canonical_origin':'http://canvas.localhost','project_id':PROJECT,'client_id':CLIENT,
       'B_sha256_expected':BASE_SHA,'one_off_creation_requested':True,'write_called':False,
       'write_successful':False,'result_pass':False,'method':'Canvas Agent API canvas_create_text_nodes'}
def check(ok,reason):
 if not ok:raise RuntimeError(reason)
def save():
 audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
def health():return s.get(url+'/health',timeout=7).json()
def state():
 r=s.post(url+'/api/tools',json={'name':'canvas_get_state','input':{}},timeout=20)
 check(r.ok and r.json().get('ok') is True,'Canvas Agent read-state failed')
 return r.json()['result']
def sha(value:str)->str:return hashlib.sha256(value.encode('utf-8')).hexdigest()
def main():
 check(not audit_path.exists() or not json.loads(audit_path.read_text()).get('write_called'),
       'Refusing repeated call: a previous creation attempt already reached the browser')
 pack=payload()
 items=[]
 for i,shot in enumerate(pack['input']['items']):
  # Place first node in the initial viewport; four display nodes in a neat row.
  items.append({**shot,'x':160+i*700,'y':120,'width':650,'height':900 if i<3 else 1040})
 check(pack['state_sha256']==BASE_SHA and hashlib.sha256(B.read_bytes()).hexdigest()==BASE_SHA,'Approved source B state changed')
 check(pack['approved_B_id']=='b7b4fd156b884907b2431b6b1e0d9960','Approved B mismatch')
 check([f'Shot0{i}' in x['title'] for i,x in enumerate(items,1)]==[True]*4,'Shot order mismatch')
 h=health();before=state()
 check(h.get('clients')==1 and h.get('hasCanvas') is True and h.get('codexBusy') is False,'Requires exactly 1 idle connected client')
 check(before.get('projectId')==PROJECT and before.get('title')=='无限画布 1' and before.get('clientId')==CLIENT,'Target browser canvas changed')
 check(before.get('nodes')==[] and not before.get('selectedNodeIds'),'New canvas not empty; refuse repeated or wrong-target create')
 audit['preflight']={'connected_clients':h.get('clients'),'canvas_title':before.get('title'),
                   'node_count':0,'B_sha256':BASE_SHA,'shot_character_lengths':[len(x['text']) for x in items],
                   'expected_text_sha256':{x['title']:sha(x['text']) for x in items}}
 save()
 # Browser content creation, one request only. Source bytes are not model-generated.
 request={'name':'canvas_create_text_nodes','input':{'items':items,'direction':'row'}}
 audit['write_called']=True;save() # If network reply fails, never blindly retry.
 r=s.post(url+'/api/tools',json=request,timeout=40)
 audit['write_http_code']=r.status_code
 check(r.ok, 'Create tool HTTP failure')
 j=r.json();check(j.get('ok') is True,'Create tool returned an error')
 audit['write_successful']=True
 inner=j.get('result') or {}
 audit['write_response_keys']=list(inner.keys()) if isinstance(inner,dict) else []
 # Web tool returns full applied canvas snapshot, not compact text.
 full_nodes=inner.get('nodes') if isinstance(inner,dict) else None
 audit['returned_node_count']=len(full_nodes) if isinstance(full_nodes,list) else None
 if isinstance(full_nodes,list):
  bytitle={n.get('title'):n for n in full_nodes}
  audit['complete_return_sha_matches']={
   x['title']:sha(str((bytitle.get(x['title'],{}).get('metadata') or {}).get('content') or ''))==sha(x['text'])
   for x in items
  }
  audit['created_ids']={x['title']:bytitle.get(x['title'],{}).get('id') for x in items}
  audit['full_return_project_id']=inner.get('projectId')
 else: audit['full_return_unavailable']=True
 save()
 time.sleep(.5)
 h2=health();final=state()
 audit['postflight']={'clients':h2.get('clients'),'busy':h2.get('codexBusy'),
       'project_id':final.get('projectId'),'client_id':final.get('clientId'),'title':final.get('title'),
       'nodes':len(final.get('nodes') or []),'selected_ids':final.get('selectedNodeIds'),
       'source_B_unchanged':hashlib.sha256(B.read_bytes()).hexdigest()==BASE_SHA}
 post_by_title={n.get('title'):n for n in final.get('nodes') or []}
 audit['compact_prefix_matches']={x['title']:
    str((post_by_title.get(x['title'],{}).get('metadata') or {}).get('content') or '')==
    (x['text'][:120]+'...' if len(x['text'])>240 else x['text']) for x in items}
 audit['result_pass']=bool(
    audit['write_successful'] and audit.get('returned_node_count')==4 and
    all(audit.get('complete_return_sha_matches',{}).values()) and
    len(audit.get('complete_return_sha_matches',{}))==4 and
    len(final.get('nodes') or [])==4 and
    final.get('projectId')==PROJECT and final.get('clientId')==CLIENT and
    set(post_by_title)=={x['title'] for x in items} and
    all(audit['compact_prefix_matches'].values()) and
    audit['postflight']['source_B_unchanged'])
 save()
 print('CREATE_AUDIT',json.dumps({k:audit.get(k) for k in ('write_http_code','write_successful','returned_node_count','full_return_project_id','created_ids','complete_return_sha_matches','compact_prefix_matches','postflight','result_pass')},ensure_ascii=False),flush=True)
 if not audit['result_pass']:sys.exit(2)
if __name__=='__main__':
 try:main()
 except Exception as e:
  audit['error_type']=type(e).__name__
  audit['error_message']=str(e)[:300]
  save();traceback.print_exc();sys.exit(2)

#!/usr/bin/env python3
"""One-off guarded display-node exact-copy repair after native-model truncation.

This narrow DCR-to-Canvas-Agent batch is NOT a general Chat HTTP editing
permission: it touches only four exact, already-created node IDs, with
verified source SHA and original nodes, and fails unless one idle canvas
client is connected to the exact authorized project.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import requests

ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/live-b-projection-20261116'
sys.path.insert(0,str(OUT))
from prepare_projection import payload
BASE_SHA='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
PROJECT='mrEXrMQoY-2ef3U6NsHtj'
CLIENT='04wsd618VDFdUWb74oZZI'
OLD={'text-1793372915213-2q1pb','image-1793372917582-2pevr','audio-1793372920916-z4dgp'}
NEW={'Shot01':'text-1794823805462-0','Shot02':'text-1794823805462-1',
     'Shot03':'text-1794823805462-2','Shot04':'text-1794823805462-3'}
def digest(n):
 return hashlib.sha256(json.dumps(n,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def checked(ok,msg):
 if not ok:raise RuntimeError(msg)
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--apply',action='store_true')
 parser.add_argument('--one-off-user-authorized',action='store_true')
 args=parser.parse_args()
 cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
 s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
 url=cfg['url'].rstrip('/')
 expected=payload()['input']['items']
 assert [i['title'].split(' · ')[-1].split('｜')[0] for i in expected]==list(NEW)
 recorded=json.loads((OUT/'native-projection-result.json').read_text())
 orig=recorded['preflight']['original_node_sha256'] if 'original_node_sha256' in recorded.get('preflight',{}) else recorded['preflight']['old_nodes_sha256']
 def snapshot():
  r=s.post(url+'/api/tools',json={'name':'canvas_get_state','input':{}},timeout=20)
  checked(r.ok and r.json().get('ok') is True,'Canvas read failed')
  return r.json()['result']
 def guard(state,allow_existing_content_any=True):
  checked(state.get('projectId')==PROJECT and state.get('title')=='无限画布 1' and state.get('clientId')==CLIENT,
          'Current Canvas target changed')
  nodes=state.get('nodes',[])
  checked(len(nodes)==7 and {n['id'] for n in nodes}==OLD|set(NEW.values()),'Canvas nodes changed')
  by_id={n['id']:n for n in nodes}
  for oid in OLD:
   checked(digest(by_id[oid])==orig[oid],f'Original node modified {oid}')
  for sid,nid in NEW.items():
   item=next(x for x in expected if sid in x['title'])
   checked(by_id[nid].get('type')=='text' and by_id[nid].get('title')==item['title'],
           f'New display node ID/title mismatch {sid}')
  checked(set(state.get('selectedNodeIds') or []).issubset(set(NEW.values())), 'Unexpected Canvas selection')
  return by_id
 h=s.get(url+'/health',timeout=7).json()
 checked(h.get('hasCanvas') is True and h.get('clients')==1,'Only one connected Canvas allowed')
 checked(hashlib.sha256(B.read_bytes()).hexdigest()==BASE_SHA,'Original B changed')
 before=snapshot()
 before_nodes=guard(before)
 result={'mode':'apply' if args.apply else 'dry-run',
         'expected_project':PROJECT,'original_nodes_verified':3,
         'new_nodes_verified':4,'B_state_sha256':BASE_SHA,
         'before_text_sha256':{sid:sha(str((before_nodes[nid].get('metadata') or {}).get('content') or '')) for sid,nid in NEW.items()},
         'expected_text_sha256':{sid:sha(next(x for x in expected if sid in x['title'])['text']) for sid in NEW}}
 if args.apply:
  recorded=OUT/'projection-final-audit.json'
  if recorded.is_file() and json.loads(recorded.read_text()).get('success') is True:
   raise RuntimeError('One-off projection already audited PASS: refusing another write')
  checked(args.one_off_user_authorized, 'Explicit one-off user authorization flag required')
  checked(h.get('codexBusy') is False and (h.get('conversation') or {}).get('status') in ('ready','warning'),
          'Refuse to race a running native Agent Codex turn')
  checked(sum(result['before_text_sha256'][k]==result['expected_text_sha256'][k] for k in NEW)<4,
          'Exact projection already complete; no batch update necessary')
  # Single request, all exact source bytes; no model rewriting.
  ops=[]
  for sid,nid in NEW.items():
   item=next(x for x in expected if sid in x['title'])
   ops.append({'type':'update_node','id':nid,'patch':{'title':item['title']},
               'metadata':{'content':item['text'],'status':'success'}})
  r=s.post(url+'/api/tools',json={'name':'canvas_apply_ops','input':{'ops':ops}},timeout=40)
  checked(r.ok and r.json().get('ok') is True,'Canvas Agent batch tool rejected')
  result['single_batch_tool_http_status']=r.status_code
  inner=r.json().get('result')
  result['inner_result_type']=type(inner).__name__
  result['inner_result_keys']=list(inner.keys()) if isinstance(inner,dict) else []
  if isinstance(inner,dict):
   result['inner_result_project']=inner.get('projectId')
   result['inner_result_node_count']=len(inner.get('nodes') or [])
   result['inner_returned_text_sha256']={
      sid: sha(str((next((n for n in (inner.get('nodes') or []) if n.get('id')==nid),{}) .get('metadata') or {}).get('content') or ''))
      for sid,nid in NEW.items()
   }
  (OUT/'exact-tool-inner-diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  result['ops_updated_exactly_four_existing_nodes']=True
  after=snapshot();actual=guard(after)
  checked(after.get('selectedNodeIds')==before.get('selectedNodeIds'), 'Selection changed during repair')
  result['after_text_sha256']={sid:sha(str((actual[nid].get('metadata') or {}).get('content') or '')) for sid,nid in NEW.items()}
  (OUT/'exact-tool-inner-diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  checked(result['after_text_sha256']==result['expected_text_sha256'],'Display text hashes mismatched after update')
  checked(hashlib.sha256(B.read_bytes()).hexdigest()==BASE_SHA,'Source B changed')
  result['exact_projection_pass']=True
 else:
  result['would_update_only']=list(NEW)
  result['dry_run_ready']=True
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

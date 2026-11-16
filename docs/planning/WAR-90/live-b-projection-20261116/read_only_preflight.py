#!/usr/bin/env python3
"""Read-only user canvas preflight, with no token or arbitrary node data written to disk."""
import json,requests,hashlib
from pathlib import Path
ROOT=Path('/home/sean/projects/canvas-lab')
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
from sys import path
path.insert(0,str(ROOT/'tools/director-runtime-v0'))
from runtime import Pilot
cfg=json.loads((Path.home()/'.infinite-canvas/canvas-agent.json').read_text())
url=cfg['url'].rstrip('/')
s=requests.Session();s.trust_env=False;s.headers['x-canvas-agent-token']=cfg['token']
health=s.get(url+'/health',timeout=5).json()
if health.get('clients')!=1 or health.get('hasCanvas') is not True or health.get('codexBusy'):
 raise RuntimeError('Single connected, idle canvas is required')
r=s.post(url+'/api/tools',json={'name':'canvas_get_state','input':{}},timeout=15)
r.raise_for_status();j=r.json();assert j.get('ok') is True,j.get('error')
state=j['result']
c=health.get('conversation') or {}
p=Pilot(B.parent).review_packet()
print('PREVIEW_APPROVED',p['authority']['approved_B_id'],'SHOTS',[(x['id'],len(x['text']),x['text_sha256'][:12]) for x in p['shots']])
print('CANVAS_METADATA',json.dumps({
 'projectId':state.get('projectId'),'clientId':state.get('clientId'),
 'state_keys':list(state.keys()),
 'projectName':state.get('projectName'),'name':state.get('name'),'title':state.get('title'),
 'node_count':len(state.get('nodes',[])),
 'nodes':[{'id':x.get('id'),'type':x.get('type'),'title':x.get('title'),'metaContentLength':len(str((x.get('metadata') or {}).get('content') or ''))} for x in state.get('nodes',[])],
 'selectedNodeIds':state.get('selectedNodeIds'),'conversation_status':c.get('status'),
 'conversation_revision':c.get('revision'),'threadId_present':bool(c.get('threadId'))},ensure_ascii=False))

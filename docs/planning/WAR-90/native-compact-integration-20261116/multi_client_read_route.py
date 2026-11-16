#!/usr/bin/env python3
"""Read-only /api/tools target drift reproduction using two fake SSE tabs.

Only synthetic /canvas/state snapshots are posted to an isolated Agent. Never
touch user browsers, production HTTP, business data, or any write Canvas tool.
"""
import json,os,secrets,subprocess,tempfile,time
from pathlib import Path
import requests
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/native-compact-integration-20261116'
URL='http://127.0.0.1:17473'
def require(ok,what):
 if not ok:raise RuntimeError(what)
def call(s,name):
 r=s.post(URL+'/api/tools',json={'name':name,'input':{}},timeout=15)
 require(r.ok and r.json().get('ok'),'api read failed')
 return r.json()['result']
def main():
 result={'test':'isolated Canvas Agent /api/tools read target follows active client',
         'synthetic_clients':True,'api_read_only':True,'production_untouched':True}
 with tempfile.TemporaryDirectory(prefix='war90-two-sse-') as td:
  root=Path(td);home=root/'home';home.mkdir()
  codehome=root/'codex';codehome.mkdir()
  cfg=home/'.infinite-canvas';cfg.mkdir()
  token=secrets.token_hex(20)
  (cfg/'canvas-agent.json').write_text(json.dumps({'url':URL,'token':token,
    'mcpOverrides':{'hindsight':False,'codegraph':False}}))
  env=dict(os.environ,HOME=str(home),CODEX_HOME=str(codehome),PORT='17473')
  log=(root/'log.txt').open('wb')
  proc=subprocess.Popen(['node',str(ROOT/'infinite-canvas/canvas-agent/dist/index.js')],
      cwd=str(ROOT/'infinite-canvas/canvas-agent'),env=env,stdout=log,stderr=subprocess.STDOUT,
      stdin=subprocess.DEVNULL,start_new_session=True)
  a=None;b=None
  try:
   s=requests.Session();s.headers['x-canvas-agent-token']=token
   for _ in range(70):
    require(proc.poll() is None,'Agent crashed')
    try:
     if s.get(URL+'/health',timeout=1).ok:break
    except requests.RequestException:pass
    time.sleep(.1)
   else:raise RuntimeError('Agent not started')
   a=s.get(URL+'/events?clientId=war90-probe-A',stream=True,timeout=10)
   b=s.get(URL+'/events?clientId=war90-probe-B',stream=True,timeout=10)
   require(a.ok and b.ok,'SSE sessions not connected')
   for _ in range(20):
    if s.get(URL+'/health',timeout=5).json().get('clients')==2:break
    time.sleep(.1)
   require(s.get(URL+'/health',timeout=5).json().get('clients')==2,'two clients not attached')
   states=[('war90-probe-A','war90-project-A','war90-node-A'),
           ('war90-probe-B','war90-project-B','war90-node-B')]
   for client,project,node in states:
    snap={'projectId':project,'clientId':client,'nodes':[{'id':node,'type':'text',
      'title':'Synthetic read-only', 'position':{'x':0,'y':0},
      'width':160,'height':100, 'metadata':{'content':'synthetic'}}],
      'selectedNodeIds':[node],'connections':[],'viewport':{'x':0,'y':0,'k':1}}
    r=s.post(URL+'/canvas/state',params={'clientId':client},json=snap,timeout=5)
    require(r.ok,'synthetic state rejected')
   views=[]
   for client,expected in [('war90-probe-A','war90-project-A'),('war90-probe-B','war90-project-B'),
                           ('war90-probe-A','war90-project-A')]:
    r=s.post(URL+'/canvas/activate',params={'clientId':client},json={},timeout=5)
    require(r.ok,'activate failed')
    state=call(s,'canvas_get_state')
    selection=call(s,'canvas_get_selection')
    require(state.get('projectId')==expected,'routing mismatch')
    require(len(selection.get('nodes') or [])==1,'selection mismatch')
    views.append({'active':client,'get_state_project':state.get('projectId'),
                  'get_state_client':state.get('clientId'),
                  'selection_node':selection['nodes'][0]['id']})
   result.update({'status':'PASS','observed_routes':views,
                  'http_tool_request_has_no_client_id_binding':True,
                  'multi_client_read_target_changed_by_activate':True,
                  'runtime_permission_not_tested':True})
  finally:
   for response in (a,b):
    if response:response.close()
   proc.terminate()
   try:proc.wait(timeout=9)
   except subprocess.TimeoutExpired:proc.kill()
   log.close()
 (OUT/'multi-client-read-route-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('MULTI_CLIENT_READ_ROUTING',json.dumps({'status':result.get('status'),
      'route_projects':[x['get_state_project'] for x in result.get('observed_routes',[])],
      'writes_to_user_canvas':False}))
if __name__=='__main__':main()

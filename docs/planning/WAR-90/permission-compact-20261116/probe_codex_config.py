#!/usr/bin/env python3
"""Read-only Codex app-server config-origin probe; never prints config values."""
import os,subprocess,tempfile,json,select,time,shutil
from pathlib import Path
OUT=Path(__file__).resolve().parent
CWD=Path('/home/sean/projects/canvas-lab')
def rpc(proc,method,params,id,seconds=15):
    proc.stdin.write(json.dumps({'id':id,'method':method,'params':params})+'\n')
    proc.stdin.flush()
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        remaining=max(0,deadline-time.monotonic())
        ready,_,_=select.select([proc.stdout],[],[],remaining)
        if not ready:break
        line=proc.stdout.readline()
        if not line:break
        try: msg=json.loads(line)
        except json.JSONDecodeError:continue
        if msg.get('id')==id:
            if 'error' in msg:return {'error_code':msg['error'].get('code'),'error_message':str(msg['error'].get('message'))[:180]}
            return msg.get('result',{})
    return {'error':'timeout/no_matching_response'}
def do(home):
    env=dict(os.environ,CODEX_HOME=str(home))
    proc=subprocess.Popen(['codex','app-server','--stdio'],stdin=subprocess.PIPE,
             stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1,env=env)
    try:
        init=rpc(proc,'initialize',{'clientInfo':{'name':'war90-config-probe','title':'WAR-90 isolated config test','version':'1'},'capabilities':{'experimentalApi':True,'requestAttestation':False}},1)
        if 'error' in init:return {'initialized':False,'error':init['error']}
        proc.stdin.write(json.dumps({'method':'initialized'})+'\n');proc.stdin.flush()
        result=rpc(proc,'config/read',{'cwd':str(CWD),'includeLayers':False},2)
        if 'error' in result:return {'initialized':True,'error':result['error']}
        c=result.get('config') or {}
        servers=c.get('mcp_servers') or {}
        out={'initialized':True,'mcp_names':sorted(servers),
             'enabled':{n:v.get('enabled',True) for n,v in servers.items() if isinstance(v,dict)}}
        return out
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill()
with tempfile.TemporaryDirectory(prefix='war90-codex-empty-') as temp:
    blank=do(Path(temp))
global_config=do(Path('/home/sean/.codex'))
result={'test':'read-only config/read via actual Codex app-server; no model or browser',
        'inherited_HOME_CODEX_HOME':'/home/sean/.codex',
        'inherited_config':global_config,'empty_isolated_config':blank,
        'no_auth_material_read':True,'no_global_config_modified':True,
        'important_scope':'config/read is config origin evidence, NOT actual thread tool scope or approval denial'}
(OUT/'config-origin-probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('CONFIG_ORIGIN_PROBE',json.dumps(result,ensure_ascii=False))

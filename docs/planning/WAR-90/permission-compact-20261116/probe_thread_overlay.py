"""Native Codex thread MCP override validation with only two /bin/false fake servers."""
from pathlib import Path
import os,subprocess,tempfile,json,select,time
OUT=Path(__file__).resolve().parent
class RPC:
    def __init__(self,p):self.p=p;self.counter=0
    def send(self,method,params,timeout=25):
        self.counter+=1;id=self.counter
        self.p.stdin.write(json.dumps({'id':id,'method':method,'params':params})+'\n')
        self.p.stdin.flush();until=time.monotonic()+timeout
        while time.monotonic()<until:
            readable,_,_=select.select([self.p.stdout],[],[],max(0,until-time.monotonic()))
            if not readable:break
            line=self.p.stdout.readline()
            if not line:break
            try:v=json.loads(line)
            except json.JSONDecodeError:continue
            if v.get('id')==id:
                if 'error' in v:
                    return {'error_code':v['error'].get('code'),'error':str(v['error'].get('message'))[:250]}
                return v.get('result',{})
        return {'error':'timeout'}
def run(override):
    with tempfile.TemporaryDirectory(prefix='war90-thread-config-') as temp:
        home=Path(temp);cwd=home/'cwd';cwd.mkdir()
        (home/'config.toml').write_text(
            '[mcp_servers.war90-fake-a]\ncommand = "/bin/false"\n'+
            '[mcp_servers.war90-fake-b]\ncommand = "/bin/false"\n')
        env=dict(os.environ,CODEX_HOME=str(home))
        proc=subprocess.Popen(['codex','app-server','--stdio'],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,text=True,bufsize=1)
        try:
            cli=RPC(proc)
            init=cli.send('initialize',{'clientInfo':{'name':'war90-thread-overlay','title':'WAR-90','version':'1'},
                                        'capabilities':{'experimentalApi':True,'requestAttestation':False}})
            if 'error' in init:return {'init':init}
            proc.stdin.write(json.dumps({'method':'initialized'})+'\n');proc.stdin.flush()
            global_c=cli.send('config/read',{'cwd':str(cwd),'includeLayers':False})
            servers=(global_c.get('config') or {}).get('mcp_servers') or {}
            config={'mcp_servers':{'war90-fake-a':{'enabled':False},'war90-fake-b':{'enabled':False}}} if override else {}
            t=cli.send('thread/start',{'cwd':str(cwd),'threadSource':'user','approvalPolicy':'on-request',
                                       'sandbox':'workspace-write','config':config},timeout=35)
            if 'error' in t:return {'config_names':sorted(servers),'thread_error':t['error']}
            tid=(t.get('thread') or {}).get('id')
            if not tid:return {'config_names':sorted(servers),'thread_missing':True}
            v=cli.send('mcpServerStatus/list',{'threadId':tid,'limit':100,'detail':'toolsAndAuthOnly'},timeout=30)
            result={'config_names':sorted(servers),'override_disabled_requested':override,
                    'thread_started':True,'status_names':[x.get('name') for x in v.get('data',[])],
                    'status_error':v.get('error')}
            return result
        finally:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill()
results={'no_override':run(False),'disable_both_thread_override':run(True),
         'no_credentials_or_user_mcp_used':True,'fake_command':'/bin/false',
         'scope':'thread/status is not proof of every model tool permission'}
(OUT/'thread-overlay-probe.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('THREAD_OVERLAY_PROBE',json.dumps(results,ensure_ascii=False))

#!/usr/bin/env python3
"""No-network, no-auth, no-model Codex app-server Skill 7-file lifecycle probe."""
import hashlib,json,os,re,select,shutil,subprocess,tempfile,time
from pathlib import Path
ROOT=Path("/home/sean/projects/canvas-lab")
SRC=ROOT/"docs/planning/WAR-89/director-skill-v0-candidate"
OUT=ROOT/"docs/planning/WAR-90/main-entry-preflight-20261116"
NAME="director-skill-v0-candidate"
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(root):return {str(p.relative_to(root)):hashfile(p) for p in sorted(root.rglob("*")) if p.is_file()}
class Rpc:
 def __init__(self,proc):self.proc=proc;self.n=0
 def req(self,method,params,timeout=35):
  self.n+=1
  n=self.n
  self.proc.stdin.write(json.dumps({'id':n,'method':method,'params':params})+'\n')
  self.proc.stdin.flush()
  end=time.monotonic()+timeout
  while time.monotonic()<end:
   r,_,_=select.select([self.proc.stdout],[],[],max(0,end-time.monotonic()))
   if not r:break
   line=self.proc.stdout.readline()
   if not line:break
   try:msg=json.loads(line)
   except json.JSONDecodeError:continue
   if msg.get('id')==n:
    if 'error' in msg:raise RuntimeError(method+' '+str(msg['error'])[:280])
    return msg.get('result') or {}
  raise RuntimeError(method+' no response')
 def notif(self,method):self.proc.stdin.write(json.dumps({'method':method})+'\n');self.proc.stdin.flush()
def validate_links(root):
 hits=[]
 for p in sorted(root.rglob("*.md")):
  for ref in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding="utf8")):
   if ref.startswith(("https:","http:","#")):continue
   q=(p.parent/ref.split('#')[0]).resolve()
   if not q.is_file() or root.resolve() not in q.parents:raise RuntimeError('broken relative link '+ref)
   hits.append(str(p.relative_to(root))+": "+ref)
 return hits
def run():
 original=inventory(SRC)
 assert len(original)==7
 links=validate_links(SRC)
 with tempfile.TemporaryDirectory(prefix="war90-codex-discovery-") as td:
  tmp=Path(td)
  home=tmp/"home";home.mkdir()
  config=tmp/"codex";config.mkdir()
  ws=home/"site";skills=ws/".agents/skills";skills.mkdir(parents=True)
  active=skills/NAME;shutil.copytree(SRC,active)
  env=dict(os.environ,HOME=str(home),CODEX_HOME=str(config))
  proc=subprocess.Popen(['codex','app-server','--stdio'],cwd=str(ws),env=env,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
  try:
   rpc=Rpc(proc)
   rpc.req('initialize',{'clientInfo':{'name':'war90-skill-preflight','title':'WAR-90 offline','version':'1'},
                         'capabilities':{'experimentalApi':True,'requestAttestation':False}})
   rpc.notif('initialized')
   def get():
    v=rpc.req('skills/list',{'cwds':[str(ws)],'forceReload':True})
    items=[x for x in v.get('data',[]) if x.get('cwd')==str(ws)]
    if len(items)!=1:raise RuntimeError('skills/list missing cwd '+str(v)[:500])
    e=items[0]
    matches=[x for x in e.get('skills',[]) if x.get('name')==NAME]
    if len(matches)!=1:raise RuntimeError('Skills discovery count '+str(len(matches)))
    m=matches[0]
    if m.get('path')!=str(active/'SKILL.md'):raise RuntimeError('Skill path mismatch')
    return {'name':m['name'],'path_matches_workspace':True,
            'enabled':m.get('enabled'),'errors_count':len(e.get('errors') or [])}
   a=get()
   assert a['enabled'] and a['errors_count']==0
   assert inventory(active)==original
   v2=tmp/'staged-v2';shutil.copytree(SRC,v2)
   target=v2/'stages/shot-plan.md'
   target.write_bytes(target.read_bytes()+b'\n<!-- WAR90-SYNTHETIC-V2-NOT-FOR-PRODUCTION -->\n')
   assert hashfile(target)!=original['stages/shot-plan.md']
   prev=tmp/'backup-v1'
   active.rename(prev);v2.rename(active)
   b=get()
   assert b['enabled'] and hashfile(active/'stages/shot-plan.md')!=original['stages/shot-plan.md']
   active.rename(v2);prev.rename(active)
   c=get()
   assert c['enabled'] and inventory(active)==original and not (active/'stages/shot-plan.md').is_symlink()
   assert not (skills/NAME).is_symlink()
   res={'probe':'direct Codex app-server skills/list used by Canvas Agent, without network or model',
        'result':'PASS','source_relative_paths_hash':original,
        'source_reference_links_checked':links,
        'initial_discovery':a,'synthetic_v2_discovery':b,'rollback_discovery':c,
        'reloaded_skill_path_same':True,'seven_file_original_restored':True,
        'models_called':False,'canvas_agent_http_called':False,'production_modified':False,
        'no_auth_files_or_codex_global_config_used':True,
        'limitations':['7-file sibling update has same Skill path; skills/list alone does not attest sibling hashes',
          'directory exchange requires quiesced thread; two renames have short unavailable window',
          'active Codex thread may cache previous Skill and must not be hot-swapped mid-turn',
          'Canvas Agent HTTP path not verified here due unavailable loopback']}
   (OUT/'codex-skill-lifecycle-result.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
   print('CODEX_SKILL_PROBE PASS',json.dumps({'files':len(original),'links':len(links),
       'v2_changed':True,'rollback':True,'enabled':c['enabled']},ensure_ascii=False))
  finally:
   proc.terminate()
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:proc.kill()
if __name__=='__main__':run()

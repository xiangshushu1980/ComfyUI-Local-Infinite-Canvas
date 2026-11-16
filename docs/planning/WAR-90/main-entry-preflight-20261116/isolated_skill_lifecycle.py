#!/usr/bin/env python3
"""Isolated Canvas Agent seven-file Skill discovery, update, rollback smoke.
Never touches the user's active Agent, Canvas, Codex config, or credential files.
"""
import hashlib,json,os,re,shutil,subprocess,tempfile,time
from pathlib import Path
import requests
ROOT=Path("/home/sean/projects/canvas-lab")
SOURCE=ROOT/"docs/planning/WAR-89/director-skill-v0-candidate"
OUT=ROOT/"docs/planning/WAR-90/main-entry-preflight-20261116"
NAME="director-skill-v0-candidate"
PORT=17467
URL=f"http://127.0.0.1:{PORT}"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def manifest(root):
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob("*")) if p.is_file()}
def check_refs(root):
    checked=[];missing=[]
    for p in sorted(root.rglob("*.md")):
        for val in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if val.startswith(("https:","http:","#","mailto:")):continue
            target=(p.parent/val.split("#")[0]).resolve()
            item=str(p.relative_to(root))+": "+val
            checked.append(item)
            if not target.is_file() or root.resolve() not in target.parents:missing.append(item)
    return checked,missing
def require(c,reason):
    if not c:raise RuntimeError(reason)
def collect_skills(session):
    resp=session.get(URL+"/agent/codex/skills?forceReload=1",timeout=90)
    require(resp.status_code==200,"skills API HTTP "+str(resp.status_code))
    j=resp.json()
    require(j.get("ok"),"skills API failure")
    matches=[s for s in j.get("data",[]) if s.get("name")==NAME]
    require(len(matches)==1,"expected exactly one candidate; got "+str(len(matches)))
    return {"enabled":matches[0].get("enabled"),"managed":matches[0].get("managed"),
            "path":matches[0].get("path"),"list_errors":len(j.get("errors") or [])}
def main():
    base=manifest(SOURCE)
    checked,missing=check_refs(SOURCE)
    require(len(base)==7 and not missing,"source files or relative links invalid")
    res={"purpose":"seven-file Skill lifecycle on isolated Canvas Agent / no model calls",
         "source_manifest":base,"relative_references_checked":checked,
         "missing_references":missing,"production_modified":False}
    try:
        if requests.get(URL+"/health",timeout=1).ok:
            raise RuntimeError("test port is not free")
    except requests.RequestException:
        pass  # No listener; the isolated Agent, if started, owns this test port.
    with tempfile.TemporaryDirectory(prefix="war90-skill-lifecycle-") as td:
        private=Path(td);home=private/"home";home.mkdir()
        codex=private/"codex";codex.mkdir()
        skillroot=home/".infinite-canvas/codex-workspaces/site/.agents/skills"
        skillroot.mkdir(parents=True)
        install=skillroot/NAME
        staged=private/"staged-v2";backup=private/"v1-backup"
        shutil.copytree(SOURCE,install)
        require(manifest(install)==base,"initial seven-file copy incomplete")
        env=dict(os.environ,HOME=str(home),CODEX_HOME=str(codex),PORT=str(PORT))
        stdout=(private/"agent.log").open("wb")
        proc=subprocess.Popen(["node",str(ROOT/"infinite-canvas/canvas-agent/dist/index.js")],
              cwd=str(ROOT/"infinite-canvas/canvas-agent"),env=env,
              stdin=subprocess.DEVNULL,stdout=stdout,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            for _ in range(100):
                require(proc.poll() is None,"private Agent exited")
                try:
                    if requests.get(URL+"/health",timeout=2).ok:break
                except requests.RequestException:pass
                time.sleep(.15)
            else:raise RuntimeError("private agent startup timeout")
            settings=json.loads((home/".infinite-canvas/canvas-agent.json").read_text())
            require(settings.get("url")==URL,"wrong test Agent URL")
            session=requests.Session()
            session.headers["x-canvas-agent-token"]=settings["token"]
            first=collect_skills(session)
            require(first["enabled"] and first["list_errors"]==0,"source Skill not discovered/enabled")
            require(first["path"]==str(install/"SKILL.md"),"unexpected Skill location")
            res["v1_discovery"]=first
            res["v1_exact_seven_file_sha"]=manifest(install)==base
            shutil.copytree(SOURCE,staged)
            stage=staged/"stages/shot-plan.md"
            stage.write_bytes(stage.read_bytes()+b"\n\n<!-- WAR-90 SYNTHETIC V2 STAGING; NEVER PRODUCTION -->\n")
            require(sha(stage)!=base["stages/shot-plan.md"],"synthetic v2 not different")
            # No turn running. Rename existing tree out, new staged tree in.
            # This is NOT an atomic two-tree swap; production must quiesce turns.
            install.rename(backup)
            staged.rename(install)
            second=collect_skills(session)
            require(second["enabled"] and second["path"]==first["path"],"hot reload changed path")
            require(sha(install/"stages/shot-plan.md")!=base["stages/shot-plan.md"],"v2 not visible on disk")
            res["v2_discovery"]=second
            res["v2_sibling_file_changed"]=True
            res["reload_does_not_attest_all_7_files"]=True
            # Exact original version restores without touching source.
            install.rename(staged)
            backup.rename(install)
            third=collect_skills(session)
            require(third["enabled"] and third["path"]==first["path"],"rollback discovery failed")
            require(manifest(install)==base,"rollback file hashes differ")
            checked2,missing2=check_refs(install)
            require(not missing2,"rollback relative references invalid")
            res["rollback_discovery"]=third
            res["rollback_restored_all_7_hashes"]=True
            res["rollback_relative_references_checked"]=len(checked2)
            res["clean_codex_home"]=True
            res["no_auth_or_model_turn"]=True
            res["no_web_canvas_client_created"]=True
            res["two_rename_swap_has_unavailable_window"]=True
            res["result"]="PASS: isolated skill discovery/reload/rollback"
        finally:
            proc.terminate()
            try:proc.wait(timeout=12)
            except subprocess.TimeoutExpired:proc.kill()
            stdout.close()
    out=OUT/"isolated-skill-lifecycle-result.json"
    out.write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n")
    print("SKILL_LIFECYCLE",json.dumps({"result":res["result"],"source_file_count":len(base),
        "ref_count":len(checked),"rollback":res["rollback_restored_all_7_hashes"],
        "no_model":res["no_auth_or_model_turn"]},ensure_ascii=False))
if __name__=="__main__":
    main()

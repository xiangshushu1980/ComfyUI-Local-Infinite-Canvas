#!/usr/bin/env python3
"""WAR-66: three independent Codex CLI prompt replays; do not edit original frozen evidence."""
import json, hashlib, subprocess, pathlib, datetime, sys
base=pathlib.Path("/home/sean/projects/canvas-lab/docs/validation/WAR-66")
old=base/"minimal-C-text-v1"
dest=base/"minimal-C-independent-v1"
dest.mkdir(exist_ok=True)
entries=json.loads((old/"decomposition-messages.json").read_text())
aggregate=json.loads((old/"decomposition-schema.json").read_text())
single=aggregate["properties"]["decompositions"]["items"]
props={k:v for k,v in single["properties"].items() if k!="idx"}
schema={"type":"object","properties":props,"required":[k for k in single["required"] if k!="idx"],"additionalProperties":False}
def freeze(p,s):
    if p.exists(): raise RuntimeError("Would overwrite existing evidence: "+str(p))
    p.write_text(s,encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
freeze(dest/"single-schema.json",json.dumps(schema,ensure_ascii=False,indent=2)+"\n")
for item in entries:
    n=item["idx"]
    target=dest/("shot-"+str(n))
    target.mkdir(exist_ok=True)
    # Original ViMax system/human messages preserved exactly, with only Codex-role packaging.
    frozen={"idx":n,"source_messages_sha256":sha(old/"decomposition-messages.json"),"system":item["system"],"human":item["human"]}
    freeze(target/"messages.json",json.dumps(frozen,ensure_ascii=False,indent=2)+"\n")
    prompt="以下是 ViMax 原始的 SYSTEM 与 HUMAN 消息，请依照 SYSTEM 的规则和给定输出 Schema，直接输出单个 JSON 对象。只处理此一个镜头；不浏览文件、不使用工具。SYSTEM:\n"+item["system"]+"\nHUMAN:\n"+item["human"]
    freeze(target/"request.txt",prompt)
    cmd=["codex","exec","-m","gpt-6.1-terra","-c",'model_reasoning_effort="medium"', "--ephemeral","--ignore-user-config","--ignore-rules","--sandbox","read-only","--skip-git-repo-check","-C",str(target),"--json","--output-schema",str(dest/"single-schema.json"),"-o",str(target/"response.json"),"-"]
    start=datetime.datetime.now().isoformat()
    try:
        result=subprocess.run(cmd,input=prompt,text=True,capture_output=True,timeout=240)
        freeze(target/"events.jsonl",result.stdout)
        freeze(target/"stderr.txt",result.stderr)
        status={"start":start,"end":datetime.datetime.now().isoformat(),"command":cmd,"returncode":result.returncode,"response_exists":(target/"response.json").exists()}
    except subprocess.TimeoutExpired as exc:
        status={"start":start,"end":datetime.datetime.now().isoformat(),"command":cmd,"timeout":True,"error":str(exc)}
    freeze(target/"execution.json",json.dumps(status,ensure_ascii=False,indent=2)+"\n")
    if not status.get("returncode")==0 or not status.get("response_exists"):
        print("FAILED",n,json.dumps(status),flush=True)
        continue
    x=json.loads((target/"response.json").read_text())
    print(json.dumps({"shot":n,"variation":x.get("variation_type"),"ff":x.get("ff_desc"),"lf":x.get("lf_desc"),"motion":x.get("motion_desc")},ensure_ascii=False),flush=True)
manifest={"protocol":"Each shot separate Codex exec, isolated run root, same frozen original ViMax system/human message content and same model settings as batch; Codex role packaging and JSON schema are adapters, not native ViMax.","model":"gpt-6.1-terra","effort":"medium","codex_cli":"0.166.0","comparison_source":"../minimal-C-text-v1/decomposition-raw.txt","original_prompt_source":"../minimal-C-text-v1/decomposition-messages.json","files":{}}
for p in sorted(dest.rglob("*")):
    if p.is_file():
        manifest["files"][str(p.relative_to(dest))]={"sha256":sha(p),"bytes":p.stat().st_size}
freeze(dest/"sha256-manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print("MANIFEST",dest/"sha256-manifest.json",flush=True)

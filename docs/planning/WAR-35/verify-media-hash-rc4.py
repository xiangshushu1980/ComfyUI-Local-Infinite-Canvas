#!/usr/bin/env python3
"""WAR-35 RC4 strict media SHA syntax regression: design-only, not bytes resolver."""
import copy
import hashlib
import json
import runpy
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from raw_ijson_gate import parse_raw_ijson
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, '/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages')
import rfc8785
script=(ROOT/"verify-d-jcs1.py").read_text().split('fox=load("cross-shot-once.example.review-v0.json")')[0]
env={"__file__":str(ROOT/"verify-d-jcs1.py")}
exec(compile(script,str(ROOT/"verify-d-jcs1.py"),"exec"),env)
digest=env["digest"]
g=runpy.run_path(str(ROOT/"verify-phase-a.py"))["gates"]
pkg=json.loads((ROOT/"cross-shot-once.example.v0-rc4.json").read_text())
validator=Draft202012Validator(json.loads((ROOT/"director-plan.schema.v0-rc4.json").read_text()))
Draft202012Validator.check_schema(validator.schema)
base={
 "targetRefs":["intent:I-CROSS"],"dependencyRefs":[],"collectionPaths":[],
 "checkSpec":"Actual output has visible landing","checkSpecVersion":"media-v1","method":"media",
 "executionTarget":{"unitRef":"U","projectionRevision":"PR1","projectionContentSha256":"a"*64,"projectionHashRule":"war52-projection-test/1"},
 "evidenceBindings":[{"evidenceRef":"media:frame","contentSha256":"b"*64,"conditionSha256":"c"*64}],
}
rows=[]
def check(name,actual,expected=True):
 ok=actual == expected
 rows.append({"case":name,"observed":actual,"expected":expected,"passed":ok})
 print(("PASS" if ok else "FAIL"),name)
def package_with(s,rev="R2"):
 p=copy.deepcopy(pkg)
 p["plan"]["revisionId"]=rev
 sha=digest(p,s)
 record=dict(s,id="C-M",target=g["plan_target"](p),dependencyHashRule=env["RULE"],
             dependencyFingerprintSha256=sha or "0"*64,result="pass",applicability="valid")
 p["reviewLedger"]={"checks":[record]}
 raw=json.dumps(p,ensure_ascii=False).encode()
 return p,parse_raw_ijson(raw),sha
control,raw,control_hash=package_with(base)
check("valid-media-declaration-schema",validator.is_valid(raw))
check("valid-media-declaration-hash",isinstance(control_hash,str) and len(control_hash)==64)
check("valid-media-payload-canonical",hashlib.sha256(rfc8785.dumps(env["payload"](pkg,base))).hexdigest()==control_hash)
same,_,same_hash=package_with(base,"R3")
check("unchanged-media-dependency-survives-revision",same_hash==control_hash)
malformed=[
 ("projection-trailing-newline",lambda s:s["executionTarget"].update(projectionContentSha256="a"*64+"\n")),
 ("content-trailing-newline",lambda s:s["evidenceBindings"][0].update(contentSha256="b"*64+"\n")),
 ("condition-trailing-newline",lambda s:s["evidenceBindings"][0].update(conditionSha256="c"*64+"\n")),
 ("projection-nonhex",lambda s:s["executionTarget"].update(projectionContentSha256="g"*64)),
 ("content-nonhex",lambda s:s["evidenceBindings"][0].update(contentSha256="g"*64)),
 ("condition-nonhex",lambda s:s["evidenceBindings"][0].update(conditionSha256="g"*64)),
 ("projection-short",lambda s:s["executionTarget"].update(projectionContentSha256="a"*63)),
 ("content-short",lambda s:s["evidenceBindings"][0].update(contentSha256="b"*63)),
 ("condition-short",lambda s:s["evidenceBindings"][0].update(conditionSha256="c"*63)),
 ("projection-uppercase",lambda s:s["executionTarget"].update(projectionContentSha256="A"*64)),
 ("content-uppercase",lambda s:s["evidenceBindings"][0].update(contentSha256="B"*64)),
 ("condition-uppercase",lambda s:s["evidenceBindings"][0].update(conditionSha256="C"*64)),
]
for name,change in malformed:
 s=copy.deepcopy(base);change(s)
 for rev in ("R2","R3"):
  _,raw,sha=package_with(s,rev)
  check(name+"-"+rev+"-schema-reject",not validator.is_valid(raw))
  check(name+"-"+rev+"-no-digest",sha is None)
# Unconditional text checks stay valid, no media validation implied.
text=dict(base,checkSpec="v0 Intent A dependency test",checkSpecVersion="intentA/v1",method="text")
text.pop("executionTarget");text.pop("evidenceBindings")
check("ordinary-intent-text-still-allowed",digest(pkg,text) is not None)
old=json.loads((ROOT/"v0-rc3-golden.report.json").read_text())["golden"]
new=json.loads((ROOT/"v0-rc4-golden.report.json").read_text())["golden"]
for name,row in new.items():
 original=old[name.replace("rc4","rc3")]
 check("unchanged-P-golden-"+name,row["sha256"]==original["sha256"])
 check("unchanged-valid-D-golden-"+name,row["candidateIntentDependencySha256"]==original["candidateIntentDependencySha256"])
passed=sum(x["passed"] for x in rows)
report={"task":"WAR-35","phase":"A RC4 media SHA syntax","passed":passed,"total":len(rows),
        "cases":rows,"realMediaBytesValidated":False,"gateCoverageValidated":False}
(ROOT/"media-hash-rc4-verification.report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",passed,"/",len(rows))
if passed != len(rows):raise SystemExit(1)

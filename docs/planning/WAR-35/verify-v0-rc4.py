#!/usr/bin/env python3
"""WAR-35 v0.1.0-RC4 P-JCS-1 Golden and structural regression, design only."""
import copy, hashlib, json, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,"/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages")
from raw_ijson_gate import parse_raw_ijson
import rfc8785

SCHEMA="director-plan.schema.v0-rc4.json"
REVIEW_SCHEMA="director-plan.schema.review-rc4.json"
VERSION="director-plan/0.1.0"
ORIGINAL_VERSION="director-plan/0.0-review"
FIXTURES=[("no-action-beat.example.review-v0.json","no-action-beat.example.v0-rc4.json"),
          ("cross-shot-once.example.review-v0.json","cross-shot-once.example.v0-rc4.json")]
schema=json.loads((ROOT/SCHEMA).read_text(encoding="utf-8"))
old_schema=json.loads((ROOT/REVIEW_SCHEMA).read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
validator=Draft202012Validator(schema)
assert schema["properties"]["contractVersion"]["const"]==VERSION
assert schema["$id"]=="urn:canvas-lab:director-plan:0.1.0-rc4"
# Only metadata and contractVersion const differ; no accidental semantic Schema drift.
orig=copy.deepcopy(old_schema)
new=copy.deepcopy(schema)
for obj in (orig,new):
    obj.pop("$id");obj.pop("title");obj.pop("description")
    obj["properties"]["contractVersion"].pop("const")
assert orig==new, "RC Schema has unrelated drift from review baseline"
results=[]
def check(name,ok):
    assert ok,name
    results.append({"case":name,"passed":True})
    print("PASS",name)

check("RC-schema-identical-except-version-and-metadata",True)
digests={}
for old_name,new_name in FIXTURES:
    old=parse_raw_ijson((ROOT/old_name).read_bytes())
    doc=parse_raw_ijson((ROOT/new_name).read_bytes())
    check("RC-raw-and-schema-"+new_name,validator.is_valid(doc))
    check("review-version-rejected-"+old_name,not validator.is_valid(old))
    check("new-version-rejected-by-old-schema-"+new_name,
          not Draft202012Validator(old_schema).is_valid(doc))
    test_doc=copy.deepcopy(doc)
    test_doc["contractVersion"]=ORIGINAL_VERSION
    check("fixture-identical-except-version-"+new_name,test_doc==old)
    payload={"contractVersion":doc["contractVersion"],"plan":doc["plan"]}
    raw=rfc8785.dumps(payload)
    sha=hashlib.sha256(raw).hexdigest()
    js=subprocess.run(["node","/home/sean/.local/share/canvas-lab-jcs/verify_js.mjs"],
            input=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
    check("cross-language-RC-JCS-"+new_name,raw==js)
    old_sha=hashlib.sha256(rfc8785.dumps({"contractVersion":old["contractVersion"],"plan":old["plan"]})).hexdigest()
    check("changed-version-changes-golden-"+new_name,sha!=old_sha)
    changed=copy.deepcopy(doc);changed["sourceLocators"]=[{"sourceId":doc["plan"]["storyBasis"]["sources"][0]["sourceId"],"locator":"file:///other/location"}]
    check("locator-change-independent-"+new_name,
          rfc8785.dumps({"contractVersion":changed["contractVersion"],"plan":changed["plan"]})==raw)
    changed=copy.deepcopy(doc);changed["reviewLedger"]={"checks":[],"decisions":[]}
    check("review-change-independent-"+new_name,
          rfc8785.dumps({"contractVersion":changed["contractVersion"],"plan":changed["plan"]})==raw)
    changed=copy.deepcopy(doc);changed["plan"]["revisionId"]="NEW-REV"
    check("revision-change-changes-golden-"+new_name,
          rfc8785.dumps({"contractVersion":changed["contractVersion"],"plan":changed["plan"]})!=raw)
    for src in doc["sourceSnapshots"]:
        check("snapshot-sha-consistent-"+new_name,
              hashlib.sha256(src["text"].encode("utf-8")).hexdigest()==src["contentSha256"])
    # RC version bump must invalidate dependency fingerprints too.
    source=(ROOT/"verify-d-jcs1.py").read_text()
    module={"__file__":str(ROOT/"verify-d-jcs1.py")}
    exec(compile(source.split('fox=load("cross-shot-once.example.review-v0.json")')[0],
                 str(ROOT/"verify-d-jcs1.py"),"exec"),module)
    intent_id=doc["plan"]["intents"][0]["id"]
    spec={"targetRefs":["intent:"+intent_id],"dependencyRefs":[],"collectionPaths":[],
          "checkSpec":"v0 Intent A dependency test","checkSpecVersion":"intentA/v1", "method":"text"}
    d_rc=module["digest"](doc,spec); d_review=module["digest"](old,spec)
    check("contractVersion-changes-D-JCS-1-"+new_name, bool(d_rc and d_review and d_rc!=d_review))
    digests[new_name]={"sha256":sha,"canonicalBytes":len(raw),"reviewDraftSha256":old_sha,
                       "candidateIntentDependencySha256":d_rc}
# These are proposed final-version profile Golden values; RC files themselves remain NOT FROZEN.
report={
  "task":"WAR-35",
  "status":"v0.1.0 release candidate 4; candidate Golden, NOT final freeze",
  "schema":SCHEMA,
  "schemaId":schema["$id"],
  "contractVersion":VERSION,
  "planHashRule":"war35-plan-jcs8785-sha256/1",
  "dependencyHashRule":module["RULE"],
  "hashPayload":"{contractVersion,plan}",
  "golden":digests,
  "cases":results,"passed":len(results),"total":len(results),
  "finalFrozen":False,"productionHashAndSemanticValidatorImplemented":False,
}
(ROOT/"v0-rc4-golden.report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",len(results),"PASS")

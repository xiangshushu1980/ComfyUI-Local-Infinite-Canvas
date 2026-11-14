#!/usr/bin/env python3
"""WAR-35 Phase A RC3: registered CheckSpec method/target contract red-green tests."""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

sys.path.insert(0, '/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages')
ROOT=Path(__file__).resolve().parent
prelude=(ROOT/"verify-d-jcs1.py").read_text().split('fox=load("cross-shot-once.example.review-v0.json")')[0]
env={"__file__":str(ROOT/"verify-d-jcs1.py")}
exec(compile(prelude,str(ROOT/"verify-d-jcs1.py"),"exec"),env)
digest=env["digest"]
candidate = "rc3" if (ROOT/"cross-shot-once.example.v0-rc3.json").exists() else "rc2"
fixture=json.loads((ROOT/f"cross-shot-once.example.v0-{candidate}.json").read_text())
dummy_target={"unitRef":"UNIT-01","projectionRevision":"PR1","projectionContentSha256":"a"*64,
              "projectionHashRule":"war52-projection-test/1"}
dummy_media=[{"evidenceRef":"media:FRAME-01","contentSha256":"b"*64}]
specs={
 "fact-script/1":("Target Facts agree with the supplied script text",["fact:F-ONCE"],"text"),
 "intentA/2":("Intent A: narrative goal consistency",["intent:I-CROSS"],"text"),
 "A/2":("Intent A respects story evidence",["intent:I-CROSS"],"text"),
 "intentA/v1":("v0 Intent A dependency test",["intent:I-CROSS"],"text"),
 "fact-local/1":("Fact statement is nonempty",["fact:F-ONCE"],"text"),
 "closure/1":("Plan dependency closure",["subject:CREEK"],"text"),
 "shotB/1":("Shot B: output evidence criteria",["shot:S02"],"text"),
 "media-v1":("Actual output has visible landing",["intent:I-CROSS"],"media"),
}
cases=[]
def record(name,actual,expected):
    ok=actual==expected
    cases.append({"case":name,"expected":expected,"observed":actual,"passed":ok})
    print(("PASS " if ok else "FAIL ")+name+" expected="+str(expected)+" observed="+str(actual))
def spec(ver,text,targets,method):
    obj={"checkSpecVersion":ver,"checkSpec":text,"targetRefs":targets,
         "dependencyRefs":[],"collectionPaths":[],"method":method}
    if method=="media":
        obj.update(executionTarget=copy.deepcopy(dummy_target),
                   evidenceBindings=copy.deepcopy(dummy_media))
    return obj
for name,(title,targets,method) in specs.items():
    s=spec(name,title,targets,method)
    record(name+"-valid-method-and-kind",digest(fixture,s) is not None,True)
    for bad_method in ("text","media","human","geometry_proxy"):
        if bad_method==method:
            continue
        wrong=spec(name,title,targets,bad_method)
        # A media spec declared text must not bypass mediaBindings.
        record(name+"-wrong-method-"+bad_method,digest(fixture,wrong) is None,True)
    if name=="closure/1":
        bad_target=["nonsense:FAKE"]
    elif name.startswith("fact-"):
        bad_target=["subject:CREEK"]
    elif name=="shotB/1":
        bad_target=["intent:I-CROSS"]
    else:
        bad_target=["fact:F-ONCE"]
    wrong=spec(name,title,bad_target,method)
    record(name+"-wrong-target-kind",digest(fixture,wrong) is None,True)
    unknown=spec(name,title,["intent:MISSING"] if targets[0].startswith("intent:") else [targets[0].split(":")[0]+":MISSING"],method)
    record(name+"-missing-target",digest(fixture,unknown) is None,True)
    fake=spec(name,title+" (spoofed)",targets,method)
    record(name+"-mismatched-spec-text",digest(fixture,fake) is None,True)

# The two independently discovered counterexamples, with matching revision digests.
media_text=spec("media-v1",specs["media-v1"][0],["intent:I-CROSS"],"text")
fact_subject=spec("fact-local/1",specs["fact-local/1"][0],["subject:CREEK"],"text")
changed=copy.deepcopy(fixture);changed["plan"]["revisionId"]="R3"
for name,s in [("attack-media-as-text",media_text),("attack-fact-as-subject",fact_subject)]:
    a,b=digest(fixture,s),digest(changed,s)
    record(name+"-no-reusable-hash",a is None and b is None,True)
# The local Fact check must NOT depend on the script when it says only nonempty.
orphan=copy.deepcopy(fixture);orphan["plan"]["storyBasis"]["facts"][0]["sourceRefs"]=[]
local=spec("fact-local/1",specs["fact-local/1"][0],["fact:F-ONCE"],"text")
record("ordinary-orphan-fact-local-remains-allowed",digest(orphan,local) is not None,True)
# Media declaration is not permission to treat self-reported digests as observed bytes.
missing_evidence=spec("media-v1",specs["media-v1"][0],["intent:I-CROSS"],"media")
missing_evidence.pop("evidenceBindings")
record("media-missing-evidence-unresolved",digest(fixture,missing_evidence) is None,True)
wrong_reg=spec("media-v1",specs["media-v1"][0],["intent:I-CROSS"],"text")
wrong_reg["evidenceBindings"]=copy.deepcopy(dummy_media)
record("media-with-evidence-but-text-method-unresolved",digest(fixture,wrong_reg) is None,True)
# Introspect registered policy, ensure eight definitions and no unchecked registrations.
record("registry-exactly-eight",set(env["CHECK_SPECS"])==set(specs),True)
# media-v1 deliberately permits both Intent and Shot targets. The method is
# still media, and neither a self-reported digest nor a synthetic check is
# evidence of inspected pixels.
media_shot=spec("media-v1",specs["media-v1"][0],["shot:S02"],"media")
record("media-v1-valid-shot-kind",digest(fixture,media_shot) is not None,True)
# At the serialized profile level, old /3 claims must never pass /4.
if candidate=="rc3" and "--common" not in sys.argv:
    old_digest=spec("fact-local/1",specs["fact-local/1"][0],["fact:F-ONCE"],"text")
    old_digest["dependencyHashRule"]="war35-dep-jcs8785-sha256/3"
    record("old-profile-rejected-before-hash",digest(fixture,old_digest) is None,True)
    schema2=json.loads((ROOT/"director-plan.schema.v0-rc2.json").read_text())
    schema3=json.loads((ROOT/"director-plan.schema.v0-rc3.json").read_text())
    record("independent-rc2-rc3-schema-ids",schema2["$id"]!=schema3["$id"],True)
    for entity in ("check","inheritance"):
        old_rule=schema2["$defs"][entity]["properties"]["dependencyHashRule"]["const"]
        new_rule=schema3["$defs"][entity]["properties"]["dependencyHashRule"]["const"]
        record("schema-version-isolated-"+entity,
               old_rule.endswith("/3") and new_rule.endswith("/4") and old_rule!=new_rule,True)
    old_golden=json.loads((ROOT/"v0-rc2-golden.report.json").read_text())["golden"]
    new_golden=json.loads((ROOT/"v0-rc3-golden.report.json").read_text())["golden"]
    for n,old_values in old_golden.items():
        newer=new_golden[n.replace("rc2","rc3")]
        record("unchanged-P-JCS-"+n,old_values["sha256"]==newer["sha256"],True)
        record("changed-D-JCS-"+n,
               old_values["candidateIntentDependencySha256"]!=newer["candidateIntentDependencySha256"],True)
    # The /4 digest binds the registered allowed methods and target kinds.
    payload=env["payload"](fixture,spec("fact-local/1",specs["fact-local/1"][0],["fact:F-ONCE"],"text"))
    record("canonical-binds-method-and-kind",
           payload["checkSpec"]["allowedMethods"]==["text"] and
           payload["checkSpec"]["targetKinds"]==["fact"],True)
    import rfc8785
    golden=json.loads((ROOT/"v0-rc3-golden.report.json").read_text())["golden"]
    for filename,row in golden.items():
        pkg=json.loads((ROOT/filename).read_text())
        it=pkg["plan"]["intents"][0]
        chk=spec("intentA/v1",specs["intentA/v1"][0],["intent:"+it["id"]],"text")
        obj=env["payload"](pkg,chk)
        pybytes=rfc8785.dumps(obj)
        jsbytes=subprocess.check_output(
            ["node","/home/sean/.local/share/canvas-lab-jcs/verify_js.mjs"],
            input=json.dumps(obj,ensure_ascii=False).encode("utf-8"))
        record("independent-node-D-golden-"+filename,
               pybytes==jsbytes and hashlib.sha256(jsbytes).hexdigest()==
               row["candidateIntentDependencySha256"],True)
failed=sum(not r["passed"] for r in cases)
print(f"TOTAL {len(cases)-failed}/{len(cases)} PASS")
report={"task":"WAR-35","scope":"Phase A CheckSpec method + target type before D-JCS digest",
        "profile":env["RULE"],"passed":len(cases)-failed,"total":len(cases),
        "cases":cases,"independentMediaBytesVerified":False,
        "fullGateValidityTested":False}
mode=("rc2-reproduction" if "--baseline" in sys.argv else
      "rc3-common" if "--common" in sys.argv else "rc3")
(ROOT/("checkspec-"+mode+"-verification.report.json")).write_text(
    json.dumps(report,ensure_ascii=False,indent=2)+"\n")
if failed and "--baseline" not in sys.argv:
    raise SystemExit(1)

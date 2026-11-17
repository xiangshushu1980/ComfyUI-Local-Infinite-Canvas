#!/usr/bin/env python3
"""WAR-36 D0 offline contract examples; NOT a production Planner/Review service.

Uses the released WAR-35 v0.1.0 Schema and unmodified cross-shot fixture.
Evaluates deterministic design invariants, not creative quality, authenticated
approval, or media. Each candidate is an in-memory, untrusted proposal.
"""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parent
WAR35=Path("/home/sean/projects/canvas-lab-worktrees/war-35-v0-freeze-preflight-20261117/docs/planning/WAR-35")
SCHEMA=WAR35/"director-plan.schema.v0.1.0.json"
FIXTURE=WAR35/"cross-shot-once.example.v0.1.0.json"
REPORT=ROOT/"revision-d0-offline-cases.report.json"
SCHEMA_SHA="b14149c0bd79e3bca1b17ea21f2949e408cca770fb3d49549c5d85ff647538e7"

sha=lambda b: hashlib.sha256(b).hexdigest()
assert sha(SCHEMA.read_bytes())==SCHEMA_SHA, "frozen Schema mismatch"
schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
assert schema["$id"]=="urn:canvas-lab:director-plan:0.1.0"
validate=Draft202012Validator(schema)
base=json.loads(FIXTURE.read_text(encoding="utf-8"))
assert validate.is_valid(base)
fixture_sha=sha(FIXTURE.read_bytes())
initial_shot_ids=[s["id"] for s in base["plan"]["shots"]]
expected_revision=base["plan"]["revisionId"]
results=[]

def ptr(path,segment):
    return path+"/"+str(segment).replace("~","~0").replace("/","~1")

def diff(left,right,path=""):
    # Reports actual RFC6901 paths, not model-declared changes.
    if type(left) is not type(right): return [path or "/"]
    if isinstance(left,dict):
        out=[]
        for k in sorted(set(left)|set(right)):
            p=ptr(path,k)
            if k not in left or k not in right:out.append(p)
            else:out.extend(diff(left[k],right[k],p))
        return out
    if isinstance(left,list):
        if len(left)!=len(right):return [path or "/"]
        if path=="/plan/shots":
            lhs=[s.get("id") for s in left]
            rhs=[s.get("id") for s in right]
            if lhs!=rhs:return ["/plan/shots"]
        out=[]
        for i,(a,b) in enumerate(zip(left,right)):out.extend(diff(a,b,ptr(path,i)))
        return out
    return [] if left==right else [path or "/"]

def duplicates(plan):
    for key in ("shots","actions","beats","intents"):
        ids=[i.get("id") for i in plan.get(key,[])]
        if len(ids)!=len(set(ids)):return key
    return None

def completion_duplicate(plan):
    seen=set()
    for shot in plan.get("shots",[]):
        for cov in shot.get("actionCoverage",[]):
            delta=cov.get("completionDeltaRef")
            if not delta:continue
            pair=(cov.get("actionRef"),delta)
            if pair in seen:return pair
            seen.add(pair)
    return None

def affected(plan,changed):
    shots=plan["shots"]
    indices=set()
    for p in changed:
        if p=="/plan/shots":indices.update(range(len(shots)))
        elif p.startswith("/plan/shots/"):
            try:indices.add(int(p.split("/")[3]))
            except (IndexError,ValueError):pass
    out=set()
    for idx in indices:
        if idx>=len(shots):continue
        out.add("shot:"+shots[idx]["id"])
        for neighbor in (idx-1,idx+1):
            if 0<=neighbor<len(shots):out.add("shot:"+shots[neighbor]["id"])
        for cov in shots[idx].get("actionCoverage",[]):
            out.add(cov["actionRef"])
    return sorted(out)

def run(proposal,allowed,*,revision=None,source_sha=None,target="S02",note=""):
    result={"kind":None,"changed":[],"unexpected":[],"recheckTargets":[],"media":"not_checked","approved":False,"reason":note}
    if revision is None:revision=expected_revision
    if source_sha is None:source_sha=fixture_sha
    if revision!=expected_revision or source_sha!=fixture_sha:
        result.update(kind="Blocked",reason="stale revision or source fingerprint")
        return result
    if target not in initial_shot_ids:
        result.update(kind="Blocked",reason="unknown Shot target")
        return result
    if proposal["plan"]["planId"]!=base["plan"]["planId"] or proposal["plan"]["revisionId"]!=expected_revision:
        result.update(kind="Blocked",reason="base identity or revision mismatch")
        return result
    if not validate.is_valid(proposal):
        result.update(kind="Blocked",reason="Schema structural validation failed")
        return result
    if duplicates(proposal["plan"]):
        result.update(kind="Blocked",reason="duplicate stable semantic ID")
        return result
    changes=diff(base["plan"],proposal["plan"],"/plan")
    result["changed"]=changes
    if not changes:
        result.update(kind="NoChange",reason="actual complete Plan diff empty")
        return result
    if any(p.startswith(("/plan/storyBasis","/plan/intents","/plan/beats","/plan/blockings")) for p in changes):
        result.update(kind="NeedsUpstreamChange",reason="approved upstream Story/Intent/Beat/Blocking change")
        return result
    if completion_duplicate(proposal["plan"]):
        result.update(kind="Blocked",reason="same Action completion delta referenced as completed twice")
        return result
    unexpected=[p for p in changes if not any(p==s or p.startswith(s+"/") for s in allowed)]
    result["unexpected"]=unexpected
    if unexpected:
        result.update(kind="Blocked",reason="actual changes exceed explicitly authorized scope")
        return result
    result.update(kind="Candidate",reason="isolated candidate; no real review decision",
                  recheckTargets=affected(proposal["plan"],changes))
    return result

def case(name,proposal,allowed,expected,assertions=None,**kwargs):
    r=run(proposal,allowed,**kwargs)
    assert r["kind"]==expected,(name,r)
    if assertions:assertions(r)
    results.append({"case":name,"resultKind":r["kind"],"reason":r["reason"],
                    "changedPaths":r["changed"],"unexpectedChanges":r["unexpected"],
                    "recheckTargets":r["recheckTargets"],"approved":r["approved"],
                    "media":r["media"],"passed":True})
    print("PASS",name,"=>",expected)

def edited(mutator):
    x=copy.deepcopy(base)
    mutator(x)
    return x

def assert_check(cond,name):
    assert cond,name

allowed_visual=["/plan/shots/1/visualDesign"]
allowed_target=["/plan/shots/1"]
case("target-S02-visual-only",
     edited(lambda x:x["plan"]["shots"][1]["visualDesign"].update(description="同一次狐狸跳跃的远岸落点更清楚")),
     allowed_visual,"Candidate",
     lambda r:assert_check(r["changed"]==["/plan/shots/1/visualDesign/description"] and
         "shot:S01" in r["recheckTargets"] and "shot:S02" in r["recheckTargets"],"strict local diff and neighbor"))
case("nochange-same-plan",copy.deepcopy(base),allowed_target,"NoChange",
     lambda r:assert_check(not r["changed"] and not r["recheckTargets"],"NoChange has no revision/effects"))
case("unauthorized-change-S01",
     edited(lambda x:(x["plan"]["shots"][1]["visualDesign"].update(description="改变S02"),
                      x["plan"]["shots"][0].update(primaryPurpose="暗改S01"))),
     allowed_visual,"Blocked",
     lambda r:assert_check("/plan/shots/0/primaryPurpose" in r["unexpected"],"must expose out-of-scope S01"))
case("upstream-fact-change",
     edited(lambda x:x["plan"]["storyBasis"]["facts"][0].update(statement="狐狸跳跃两次")),
     allowed_target,"NeedsUpstreamChange")
case("stale-revision",copy.deepcopy(base),allowed_target,"Blocked",revision="R1")
case("wrong-source-fingerprint",copy.deepcopy(base),allowed_target,"Blocked",source_sha="0"*64)
case("unknown-target",copy.deepcopy(base),allowed_target,"Blocked",target="S99")
case("duplicate-shot-id",
     edited(lambda x:x["plan"]["shots"].append(copy.deepcopy(x["plan"]["shots"][0]))),
     allowed_target,"Blocked")
case("reorder-without-scope",
     edited(lambda x:x["plan"]["shots"].reverse()),allowed_target,"Blocked",
     lambda r:assert_check(r["unexpected"]==["/plan/shots"],"reorder requires structural scope"))
case("explicit-reorder-structural-scope",
     edited(lambda x:x["plan"]["shots"].reverse()),["/plan/shots"],"Candidate",
     lambda r:assert_check(r["changed"]==["/plan/shots"] and
         "shot:S01" in r["recheckTargets"] and "shot:S02" in r["recheckTargets"],"reorder rechecks all"))
case("repeated-action-completion",
     edited(lambda x:x["plan"]["shots"][0]["actionCoverage"][0].update(completionDeltaRef="delta:D-LAND")),
     ["/plan/shots/0/actionCoverage"],"Blocked")
# Partial acceptance creates a new isolated candidate from the trusted base and
# recomputes actual changes instead of accepting a subset of DOM/editor patches.
def both(x):
    s=x["plan"]["shots"][1]
    s["primaryPurpose"]="落地完成更有节奏"
    s["visualDesign"]["description"]="更清楚的远岸落地"
two=edited(both)
case("two-field-proposal",two,allowed_target,"Candidate")
partial=edited(lambda x:x["plan"]["shots"][1]["visualDesign"].update(description="更清楚的远岸落地"))
case("partial-accept-rederived",partial,allowed_visual,"Candidate",
     lambda r:assert_check(r["changed"]==["/plan/shots/1/visualDesign/description"],"partial re-diff"))
case("nochange-ui-layout-is-not-plan",copy.deepcopy(base),allowed_target,"NoChange")
case("unknown-media-stays-not-checked",
     edited(lambda x:x["plan"]["shots"][1]["evidenceCriteria"][0].update(statement="落地可辨性仍需要画面验证")),
     ["/plan/shots/1/evidenceCriteria"],"Candidate",
     lambda r:assert_check(r["media"]=="not_checked" and not r["approved"],"media must not auto-pass"))
case("wrong-plan-identity",
     edited(lambda x:x["plan"].update(planId="wrong")),allowed_target,"Blocked")
check={
"scopeTestNature":"offline isolated design logic; NOT production code",
"productionSchemaUsed":schema["$id"],
"schemaSha256":sha(SCHEMA.read_bytes()),
"fixture":FIXTURE.name,
"fixtureSha256":fixture_sha,
"baseRevision":expected_revision,
"rules":"stable ID, explicit scope, actual RFC6901 Plan diff, conservative neighbor/action recheck",
"limitations":[
  "Context Builder not executed; simulated trusted base is a frozen example, not a real approved Plan",
  "No true Check/Risk/Decision store or /4 D-JCS trust-manifest semantics in this harness",
  "No full state-transition/causal timing/real media/human visual verification",
  "No real Canvas plugin API, persistence or user approval executed",
  "Only illustrative fox shared-action typed fixture; D key scene applied in manual design analysis"
],
"tests":results,
"passed":len(results),"total":len(results),
"productionApproved":False
}
REPORT.write_text(json.dumps(check,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("TOTAL",len(results),"PASS — D0 illustrative design checks only")

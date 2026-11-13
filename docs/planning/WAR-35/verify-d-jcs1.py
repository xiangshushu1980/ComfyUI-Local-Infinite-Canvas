#!/usr/bin/env python3
"""WAR-35 D-JCS-1 design-only closure verifier (not production validation)."""
import copy, hashlib, json, re
from pathlib import Path
import rfc8785
ROOT=Path(__file__).resolve().parent
RULE="war35-dep-jcs8785-sha256/1"
SETS={"sourceRefs","basisRefs","intentRefs","actionRefs","deltaRefs","afterBeatRefs","participantRefs","objectRefs","afterDeltaRefs","provenanceRefs","scopeRefs","spatialBasisRefs","beatRefs","blockingRefs","subjectRefs","entryDeltaRefs","exitDeltaRefs"}
SINGLES={"deltaRef","triggerRef","actionRef","completionDeltaRef"}
REG={"source":("storyBasis","sources","sourceId"),"fact":("storyBasis","facts","id"),"constraint":("storyBasis","constraints","id"),"subject":("storyBasis","subjects","id"),"intent":("intents","id"),"beat":("beats","id"),"action":("actions","id"),"delta":("state","deltas","id"),"blocking":("blockings","id"),"shot":("shots","id")}
class Unresolved(Exception): pass
def load(name): return json.loads((ROOT/name).read_text())
def normalized(v):
    refs=set()
    def walk(x):
        if isinstance(x,list): return [walk(y) for y in x]
        if not isinstance(x,dict): return x
        out={}
        for k,y in x.items():
            if k in SETS:
                if not isinstance(y,list) or not all(isinstance(z,str) for z in y): raise Unresolved(k)
                refs.update(y); out[k]=sorted(set(y))
            elif k in SINGLES:
                if not isinstance(y,str): raise Unresolved(k)
                refs.add(y); out[k]=y
            else: out[k]=walk(y)
        return out
    return walk(v),refs
def resolve(plan,ref):
    if not isinstance(ref,str) or ":" not in ref: raise Unresolved("bad ref")
    kind,local=ref.split(":",1)
    if kind=="plan":
        if local!=plan["planId"]: raise Unresolved(ref)
        return plan
    parts=REG.get(kind)
    if not parts: raise Unresolved(ref)
    if len(parts)==3:
        a,b,k=parts; items=plan.get(a,{}).get(b,[])
    else:
        a,k=parts; items=plan.get(a,[])
    matches=[v for v in items if v.get(k)==(ref if kind=="source" else local)]
    if len(matches)!=1: raise Unresolved(ref)
    return matches[0]
def verify_source(pkg,src):
    sha=src.get("contentSha256")
    if not sha: raise Unresolved("missing source hash")
    matches=[s for s in pkg.get("sourceSnapshots",[]) if s.get("sourceId")==src["sourceId"] and s.get("contentSha256")==sha]
    # Research verifier only resolves inline text; external resolver remains unverified.
    if len(matches)!=1 or not isinstance(matches[0].get("text"),str): raise Unresolved("source unavailable")
    if hashlib.sha256(matches[0]["text"].encode()).hexdigest()!=sha: raise Unresolved("source mismatch")
def collection(plan,path):
    if not isinstance(path,str) or not path.startswith("/"): raise Unresolved("pointer")
    value=plan
    for seg in path.split("/")[1:]:
        if re.search(r"~(?![01])",seg): raise Unresolved("pointer escape")
        seg=seg.replace("~1","/").replace("~0","~")
        try:
            if isinstance(value,list):
                if not seg.isascii() or not seg.isdecimal() or (len(seg)>1 and seg.startswith("0")): raise Unresolved("index")
                value=value[int(seg)]
            else: value=value[seg]
        except (KeyError,IndexError,TypeError): raise Unresolved("pointer missing")
    if not isinstance(value,list): raise Unresolved("not collection")
    return value
def payload(pkg,spec):
    plan=pkg["plan"]
    scope={k:sorted(set(spec.get(k,[]))) for k in ("targetRefs","dependencyRefs","collectionPaths")}
    pending=set(scope["targetRefs"]+scope["dependencyRefs"]); objects={}; cols=[]
    for path in scope["collectionPaths"]:
        val,extra=normalized(collection(plan,path)); cols.append({"path":path,"value":val}); pending.update(extra)
    while pending:
        ref=min(pending); pending.remove(ref)
        if ref in objects: continue
        obj=resolve(plan,ref)
        if ref.startswith("source:"): verify_source(pkg,obj)
        val,extra=normalized(obj); objects[ref]=val; pending.update(extra-set(objects))
    return {"profile":RULE,"contractVersion":pkg["contractVersion"],"planIdentity":{"planId":plan["planId"],"sceneId":plan["sceneId"]},"checkSpec":{"text":spec["checkSpec"],"version":spec["checkSpecVersion"],"method":spec["method"]},"scope":scope,"resolvedObjects":[{"ref":k,"value":objects[k]} for k in sorted(objects)],"collections":sorted(cols,key=lambda x:x["path"])}
def digest(pkg,spec):
    try: return hashlib.sha256(rfc8785.dumps(payload(pkg,spec))).hexdigest()
    except Unresolved: return None
fox=load("cross-shot-once.example.review-v0.json"); doubt=load("no-action-beat.example.review-v0.json")
spec={"targetRefs":["intent:I-CROSS"],"dependencyRefs":[],"collectionPaths":[],"checkSpec":"Intent A respects story evidence","checkSpecVersion":"A/1","method":"text"}
results=[]
def expect(name,ok):
    if not ok: raise AssertionError(name)
    results.append(name); print("PASS",name)
baseline=digest(fox,spec)
expect("baseline-resolved",baseline is not None)
seed=copy.deepcopy(spec); seed.update(targetRefs=["fact:F-ONCE","intent:I-CROSS"],dependencyRefs=["source:S-FOX","fact:F-ONCE"],collectionPaths=["/beats","/shots"])
a=digest(fox,seed)
for k in ("targetRefs","dependencyRefs","collectionPaths"): seed[k].reverse()
expect("D-P01-scope-set-order",a==digest(fox,seed))
dup=copy.deepcopy(fox); dup["plan"]["intents"][0]["basisRefs"].append("fact:F-ONCE")
expect("D-P02-typed-ref-set-normalization",digest(dup,spec)==baseline)
new=copy.deepcopy(fox); new["plan"]["revisionId"]="R3"; new["plan"]["shots"].append(copy.deepcopy(new["plan"]["shots"][-1])); new["plan"]["shots"][-1]["id"]="S-NEW"
expect("D-P03-new-shot-no-A-dependency",digest(new,spec)==baseline)
changed=copy.deepcopy(fox); changed["plan"]["storyBasis"]["facts"][0]["statement"]+=" changed"
expect("D-N01-D-N05-closure-not-allowlist",digest(changed,spec)!=baseline)
broken=copy.deepcopy(fox); broken["plan"]["intents"][0]["basisRefs"]=["fact:MISSING"]
expect("D-N02-missing-ref",digest(broken,spec) is None)
broken=copy.deepcopy(fox); del broken["plan"]["storyBasis"]["sources"][0]["contentSha256"]
expect("D-N02-missing-source-sha",digest(broken,spec) is None)
broken=copy.deepcopy(fox); del broken["sourceSnapshots"]
expect("D-N02-source-unavailable",digest(broken,spec) is None)
broken=copy.deepcopy(fox); broken["sourceSnapshots"][0]["text"]+="!"
expect("D-N02-source-mismatch",digest(broken,spec) is None)
expect("D-N02-collection-path-missing",digest(fox,dict(spec,collectionPaths=["/missing"])) is None)
act=dict(spec,targetRefs=["action:A-JUMP"])
broken=copy.deepcopy(fox); broken["plan"]["actions"][0]["description"]+="!"
expect("D-N03-complete-object-changed",digest(broken,act)!=digest(fox,act))
allshots=dict(spec,collectionPaths=["/shots"])
expect("D-N04-collection-member",digest(new,allshots)!=digest(fox,allshots))
reverse=copy.deepcopy(fox); reverse["plan"]["shots"].reverse()
expect("D-N04-collection-order",digest(reverse,allshots)!=digest(fox,allshots))
expect("other-fixture",digest(doubt,dict(spec,targetRefs=["intent:I-DOUBT"])) is not None)
report={"task":"WAR-35","profile":RULE,"scope":"design-only; inline source resolver, no production media","baselineDigest":baseline,"cases":results,"passed":len(results),"externalResolverTested":False}
(ROOT/"d-jcs1-verification.report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",len(results),"PASS")

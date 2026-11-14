#!/usr/bin/env python3
"""WAR-35 D-JCS-1 design-only closure verifier (not production validation)."""
import copy, hashlib, json, re
from pathlib import Path
import rfc8785
ROOT=Path(__file__).resolve().parent
RULE="war35-dep-jcs8785-sha256/3"
# Plan-relative schema locations. None denotes an array item (never an object key).
REF_FIELDS = {
    ("storyBasis", "constraints", None): ("sourceRefs",),
    ("storyBasis", "facts", None): ("sourceRefs",),
    ("storyBasis", "subjects", None): ("sourceRefs",),
    ("intents", None): ("basisRefs",),
    ("beats", None): ("intentRefs", "actionRefs", "deltaRefs", "afterBeatRefs"),
    ("actions", None): ("participantRefs", "objectRefs"),
    ("state", "baseline", None): ("sourceRefs",),
    ("state", "deltas", None): ("afterDeltaRefs", "provenanceRefs"),
    ("blockings", None): ("scopeRefs", "spatialBasisRefs"),
    ("shots", None): ("intentRefs", "beatRefs", "blockingRefs"),
    ("shots", None, "visualDesign"): ("subjectRefs",),
    ("shots", None, "boundary"): ("entryDeltaRefs", "exitDeltaRefs"),
}
REF_SETS = {parent + (name,) for parent, names in REF_FIELDS.items() for name in names}
REF_SINGLES = {
    ("actions", None, "completion", "deltaRef"),
    ("state", "deltas", None, "triggerRef"),
    ("shots", None, "actionCoverage", None, "actionRef"),
    ("shots", None, "actionCoverage", None, "completionDeltaRef"),
}
SOURCE_ITEM = ("storyBasis", "sources", None)
REG={"source":("storyBasis","sources","sourceId"),"fact":("storyBasis","facts","id"),"constraint":("storyBasis","constraints","id"),"subject":("storyBasis","subjects","id"),"intent":("intents","id"),"beat":("beats","id"),"action":("actions","id"),"delta":("state","deltas","id"),"blocking":("blockings","id"),"shot":("shots","id")}
class Unresolved(Exception): pass
def load(name): return json.loads((ROOT/name).read_text())
def normalized(value, location, refs):
    if location == SOURCE_ITEM:
        # Even an embedded binding must resolve uniquely to verified source bytes.
        refs.add(value["sourceId"])
    if location in REF_SETS:
        refs.update(value)
        return sorted(set(value))
    if location in REF_SINGLES:
        refs.add(value)
    if isinstance(value, list):
        return [normalized(item, location + (None,), refs) for item in value]
    if isinstance(value, dict):
        return {key: normalized(item, location + (key,), refs) for key, item in value.items()}
    return value

def resolve(plan,ref):
    if not isinstance(ref,str) or ":" not in ref: raise Unresolved("bad ref")
    kind,local=ref.split(":",1)
    if kind=="plan":
        if local!=plan["planId"]: raise Unresolved(ref)
        return plan, ()
    parts=REG.get(kind)
    if not parts: raise Unresolved(ref)
    if len(parts)==3:
        a,b,k=parts; items=plan.get(a,{}).get(b,[])
    else:
        a,k=parts; items=plan.get(a,[])
    matches=[v for v in items if v.get(k)==(ref if kind=="source" else local)]
    if len(matches)!=1: raise Unresolved(ref)
    return matches[0], (*parts[:-1], None)
def verify_source(pkg,src):
    sha=src.get("contentSha256")
    if src.get("mediaKind") != "text": raise Unresolved("asset resolver unavailable")
    if not sha: raise Unresolved("missing source hash")
    matches=[s for s in pkg.get("sourceSnapshots",[]) if s.get("sourceId")==src["sourceId"] and s.get("contentSha256")==sha]
    # Research verifier only resolves inline text; external resolver remains unverified.
    if len(matches)!=1 or not isinstance(matches[0].get("text"),str): raise Unresolved("source unavailable")
    if hashlib.sha256(matches[0]["text"].encode()).hexdigest()!=sha: raise Unresolved("source mismatch")
def collection(plan,path):
    if not isinstance(path,str) or not path.startswith("/"): raise Unresolved("pointer")
    location = ()
    value=plan
    for seg in path.split("/")[1:]:
        if re.search(r"~(?![01])",seg): raise Unresolved("pointer escape")
        seg=seg.replace("~1","/").replace("~0","~")
        try:
            if isinstance(value,list):
                if not seg.isascii() or not seg.isdecimal() or (len(seg)>1 and seg.startswith("0")): raise Unresolved("index")
                location += (None,)
                value=value[int(seg)]
            else:
                location += (seg,)
                value=value[seg]
        except (KeyError,IndexError,TypeError): raise Unresolved("pointer missing")
    if not isinstance(value,list): raise Unresolved("not collection")
    return value, location
# Trusted research CheckSpec definitions. Match text only for exact identity.
# The versioned policy determines which provenance edges are required.
CHECK_SPECS = {
    "fact-script/1": ("Target Facts agree with the supplied script text", "target-fact-sources/1"),
    "intentA/2": ("Intent A: narrative goal consistency", "intent-basis-fact-sources/1"),
    "A/2": ("Intent A respects story evidence", "intent-basis-fact-sources/1"),
    "intentA/v1": ("v0 Intent A dependency test", "intent-basis-fact-sources/1"),
    "fact-local/1": ("Fact statement is nonempty", "closure-only/1"),
    "closure/1": ("Plan dependency closure", "closure-only/1"),
    "shotB/1": ("Shot B: output evidence criteria", "closure-only/1"),
    "media-v1": ("Actual output has visible landing", "closure-only/1"),
}


def require_source_path(plan, ref):
    # These schema edges only point downstream: Intent -> Constraint/Fact/Source,
    # Constraint -> Fact/Source, Fact -> Source. Verify bytes in the shared closure.
    obj, _ = resolve(plan, ref)
    kind = ref.split(":", 1)[0]
    if kind == "source":
        return
    field = "basisRefs" if kind == "intent" else "sourceRefs"
    if kind not in ("intent", "constraint", "fact") or not obj.get(field):
        raise Unresolved("missing target-to-source edge")
    for child in set(obj[field]):
        require_source_path(plan, child)


def source_policy(plan, spec, targets):
    definition = CHECK_SPECS.get(spec["checkSpecVersion"])
    if definition is None or definition[0] != spec["checkSpec"]:
        raise Unresolved("unregistered CheckSpec")
    policy = definition[1]
    if policy == "closure-only/1":
        return policy
    prefix = "fact:" if policy == "target-fact-sources/1" else "intent:"
    if not targets or any(not ref.startswith(prefix) for ref in targets):
        raise Unresolved("wrong target for source proof")
    for ref in targets:
        require_source_path(plan, ref)
    return policy


def payload(pkg,spec):
    if spec.get("dependencyHashRule", RULE) != RULE:
        raise Unresolved("incompatible dependency profile")
    if spec["method"] != "media" and (
        spec["method"] in ("human", "geometry_proxy") or
        spec.get("evidenceRefs") or spec.get("evidenceBindings") or spec.get("executionTarget")
    ):
        raise Unresolved("external observation content and scope cannot be verified")
    plan=pkg["plan"]
    scope={k:sorted(set(spec.get(k,[]))) for k in ("targetRefs","dependencyRefs","collectionPaths")}
    policy = source_policy(plan, spec, scope["targetRefs"])
    pending=set(scope["targetRefs"]+scope["dependencyRefs"]); objects={}; cols=[]
    for path in scope["collectionPaths"]:
        value, location = collection(plan, path)
        cols.append({"path": path, "value": normalized(value, location, pending)})
    while pending:
        ref=min(pending); pending.remove(ref)
        if ref in objects: continue
        obj, location = resolve(plan,ref)
        if ref.startswith("source:"): verify_source(pkg,obj)
        objects[ref] = normalized(obj, location, pending)
    result={"profile":RULE,"contractVersion":pkg["contractVersion"],"planIdentity":{"planId":plan["planId"],"sceneId":plan["sceneId"]},"checkSpec":{"sourcePolicy":policy,"text":spec["checkSpec"],"version":spec["checkSpecVersion"],"method":spec["method"]},"scope":scope,"resolvedObjects":[{"ref":k,"value":objects[k]} for k in sorted(objects)],"collections":sorted(cols,key=lambda x:x["path"])}
    if spec["method"]=="media":
        target=spec.get("executionTarget")
        evidence=spec.get("evidenceBindings")
        required={"unitRef","projectionRevision","projectionContentSha256","projectionHashRule"}
        if not isinstance(target,dict) or set(target)!=required:
            raise Unresolved("missing/invalid immutable executionTarget")
        if not isinstance(evidence,list) or not evidence:
            raise Unresolved("missing media evidence")
        if any(not isinstance(x,dict) or not {"evidenceRef","contentSha256"}.issubset(x) or
               set(x)-{"evidenceRef","contentSha256","conditionSha256"} for x in evidence):
            raise Unresolved("invalid media evidence binding")
        if any(not isinstance(x["evidenceRef"],str) or not x["evidenceRef"] or
               not isinstance(x["contentSha256"],str) or len(x["contentSha256"])!=64 for x in evidence):
            raise Unresolved("invalid media SHA")
        refs=[x["evidenceRef"] for x in evidence]
        if len(set(refs))!=len(refs):
            raise Unresolved("duplicate media evidenceRef")
        # Research calculator binds declared digests; actual media bytes MUST
        # be verified by resolver before recording a real media pass.
        result["mediaBindings"]={"executionTarget":target,
                                 "evidenceBindings":sorted(evidence,key=lambda x:x["evidenceRef"])}
    return result
def digest(pkg,spec):
    try: return hashlib.sha256(rfc8785.dumps(payload(pkg,spec))).hexdigest()
    except Unresolved: return None
fox=load("cross-shot-once.example.review-v0.json"); doubt=load("no-action-beat.example.review-v0.json")
spec={"targetRefs":["intent:I-CROSS"],"dependencyRefs":[],"collectionPaths":[],"checkSpec":"Intent A respects story evidence","checkSpecVersion":"A/2","method":"text"}
results=[]
def expect(name,ok):
    if not ok: raise AssertionError(name)
    results.append(name); print("PASS",name)
baseline=digest(fox,spec)
expect("baseline-resolved",baseline is not None)
local_spec=dict(spec,checkSpec="Plan dependency closure",checkSpecVersion="closure/1")
seed=copy.deepcopy(local_spec); seed.update(targetRefs=["fact:F-ONCE","intent:I-CROSS"],dependencyRefs=["source:S-FOX","fact:F-ONCE"],collectionPaths=["/beats","/shots"])
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
act=dict(local_spec,targetRefs=["action:A-JUMP"])
broken=copy.deepcopy(fox); broken["plan"]["actions"][0]["description"]+="!"
expect("D-N03-complete-object-changed",digest(broken,act)!=digest(fox,act))
allshots=dict(spec,collectionPaths=["/shots"])
expect("D-N04-collection-member",digest(new,allshots)!=digest(fox,allshots))
reverse=copy.deepcopy(fox); reverse["plan"]["shots"].reverse()
expect("D-N04-collection-order",digest(reverse,allshots)!=digest(fox,allshots))
expect("other-fixture",digest(doubt,dict(spec,targetRefs=["intent:I-DOUBT"])) is not None)
report={"task":"WAR-35","profile":RULE,"scope":"design-only; inline source resolver, no production media","baselineDigest":baseline,"cases":results,"passed":len(results),"externalResolverTested":False}
(ROOT/"d-jcs1-rc2-verification.report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",len(results),"PASS")

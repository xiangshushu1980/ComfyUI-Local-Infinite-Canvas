#!/usr/bin/env python3
"""WAR-35 Blocking 2: media Check structural and immutable-binding regression."""
import copy, json, sys
from pathlib import Path
# Research verification only: use pinned RFC8785 from Eric's isolated JCS venv.
sys.path.insert(0, '/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages')
from jsonschema import Draft202012Validator
root=Path(__file__).resolve().parent
schema=json.loads((root/"director-plan.schema.review-v0.json").read_text())
Draft202012Validator.check_schema(schema)
check=Draft202012Validator({"$defs":schema["$defs"],"$ref":"#/$defs/check"})
target={"unitRef":"UNIT-01","projectionRevision":"PR1","projectionContentSha256":"a"*64,"projectionHashRule":"war52-projection-test/1"}
evidence=[{"evidenceRef":"media:FRAME-01","contentSha256":"b"*64,"conditionSha256":"c"*64},
          {"evidenceRef":"media:FRAME-02","contentSha256":"d"*64,"conditionSha256":"c"*64}]
base={"id":"C-MEDIA","target":{"planId":"P-FOX","revisionId":"R2","planContentSha256":"0"*64,"hashRule":"war35-plan-jcs8785-sha256/1"},"targetRefs":["intent:I-CROSS"],"dependencyRefs":[],"checkSpec":"Actual output has visible landing","checkSpecVersion":"media-v1","method":"media","result":"pass","applicability":"valid","dependencyHashRule":"war35-dep-jcs8785-sha256/2","dependencyFingerprintSha256":"e"*64,"executionTarget":target,"evidenceBindings":evidence}
passed=[]
def test(name,actual,expected=True):
    if actual!=expected: raise AssertionError(f"{name}: expected {expected}, got {actual}")
    passed.append(name); print("PASS",name)
test("M-P01-media-pass-complete-binding",check.is_valid(base))
test("M-P02-media-fail-complete-binding",check.is_valid(dict(base,result="fail")))
test("M-N01-pass-missing-executionTarget",check.is_valid({k:v for k,v in base.items() if k!="executionTarget"}),False)
test("M-N02-pass-missing-evidenceBindings",check.is_valid({k:v for k,v in base.items() if k!="evidenceBindings"}),False)
test("M-N03-pass-empty-evidenceBindings",check.is_valid(dict(base,evidenceBindings=[])),False)
test("M-N04-fail-missing-executionTarget",check.is_valid({**base,"result":"fail","executionTarget":None}),False)
test("M-N05-fail-missing-evidenceBindings",check.is_valid({k:v for k,v in dict(base,result="fail").items() if k!="evidenceBindings"}),False)
test("M-N06-binding-missing-media-digest",check.is_valid(dict(base,evidenceBindings=[{"evidenceRef":"media:FRAME-01"}])),False)
test("M-N07-binding-duplicate-exact",check.is_valid(dict(base,evidenceBindings=[evidence[0],evidence[0]])),False)
test("M-N08-pass-missing-dependency-digest",check.is_valid({k:v for k,v in base.items() if k!="dependencyFingerprintSha256"}),False)
test("M-P03-nonmedia-pass-no-media-bindings",check.is_valid({k:v for k,v in base.items() if k not in ("executionTarget","evidenceBindings") and k!="method"} | {"method":"text"}))
# unknown media check with no resolved evidence is valid but cannot claim pass
test("M-P04-unknown-media-no-bindings",check.is_valid({**{k:v for k,v in base.items() if k not in ("executionTarget","evidenceBindings","dependencyFingerprintSha256")},"result":"unknown"}))
# Research-only D-JCS implementation is loaded without running main block/tests
# Extract functions by suppressing bottom-level test setup at the known fox=load boundary.
code=(root/"verify-d-jcs1.py").read_text()
module={"__file__":str(root/"verify-d-jcs1.py")}
exec(compile(code.split('fox=load("cross-shot-once.example.review-v0.json")')[0],str(root/"verify-d-jcs1.py"),"exec"),module)
digest=module["digest"]
fox=json.loads((root/"cross-shot-once.example.review-v0.json").read_text())
spec={"targetRefs":["intent:I-CROSS"],"dependencyRefs":[],"collectionPaths":[],"checkSpec":"Actual output has visible landing","checkSpecVersion":"media-v1","method":"media","executionTarget":target,"evidenceBindings":evidence}
first=digest(fox,spec)
test("M-P05-media-dependency-resolves",first is not None)
changed=copy.deepcopy(spec); changed["evidenceBindings"]=list(reversed(changed["evidenceBindings"]))
test("M-P06-evidence-order-independent",digest(fox,changed)==first)
changed=copy.deepcopy(spec); changed["evidenceBindings"][0]["contentSha256"]="f"*64
test("M-N09-media-content-changed-cannot-inherit",digest(fox,changed)!=first)
changed=copy.deepcopy(spec); changed["executionTarget"]["projectionContentSha256"]="f"*64
test("M-N10-projection-content-changed-cannot-inherit",digest(fox,changed)!=first)
changed=copy.deepcopy(spec); changed["evidenceBindings"][0]["conditionSha256"]="f"*64
test("M-N11-generation-condition-changed-cannot-inherit",digest(fox,changed)!=first)
changed=copy.deepcopy(spec); del changed["executionTarget"]
test("M-N12-missing-execution-target-no-digest",digest(fox,changed) is None)
changed=copy.deepcopy(spec); changed["evidenceBindings"]=[]
test("M-N13-no-media-evidence-no-digest",digest(fox,changed) is None)
changed=copy.deepcopy(spec); changed["evidenceBindings"].append({**evidence[0],"contentSha256":"f"*64})
test("M-N14-duplicate-ref-conflict-no-digest",digest(fox,changed) is None)
# Research digests bind declared SHAs; bytes and authentic checks are intentionally not claimed.
report={"task":"WAR-35","scope":"Blocking 2 Media Check design-only synthetic regression","total":len(passed),"passed":len(passed),"cases":passed,"mediaBytesVerified":False,"conditionSHAProfileVerified":False,"firstSyntheticDigest":first}
(root/"media-check-verification.report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",len(passed),"PASS")

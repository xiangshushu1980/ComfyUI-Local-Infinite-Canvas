#!/usr/bin/env python3
"""WAR-35 structural D-JCS-1 regression checks (Python environment with jsonschema)."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator
root=Path(__file__).resolve().parent
schema=json.loads((root/"director-plan.schema.review-v0.json").read_text())
Draft202012Validator.check_schema(schema)
checks=[]
def verify(label, value, expected):
    ok=bool(value)
    if ok!=expected: raise AssertionError(f"{label}: expected {expected}, got {ok}")
    checks.append(label); print("PASS",label)
for name in ("no-action-beat.example.review-v0.json","cross-shot-once.example.review-v0.json"):
    obj=json.loads((root/name).read_text())
    verify("fixture-"+name,Draft202012Validator(schema).is_valid(obj),True)
check=Draft202012Validator({"$defs":schema["$defs"],"$ref":"#/$defs/check"})
base={"id":"C-1","target":{"planId":"P-FOX","revisionId":"R2","planContentSha256":"0"*64,"hashRule":"war35-plan-jcs8785-sha256/1"},"targetRefs":["intent:I-CROSS"],"dependencyRefs":[],"checkSpec":"test","checkSpecVersion":"A/1","method":"text","result":"unknown","applicability":"valid","dependencyHashRule":"war35-dep-jcs8785-sha256/1"}
fixtures=[
 ("unknown-no-fingerprint",base,True),
 ("not_checked-no-fingerprint",dict(base,result="not_checked"),True),
 ("pass-no-fingerprint",dict(base,result="pass"),False),
 ("fail-no-fingerprint",dict(base,result="fail"),False),
 ("pass-with-fingerprint",dict(base,result="pass",dependencyFingerprintSha256="f"*64),True),
 ("empty-extra-dependencies",base,True),
 ("duplicate-extra-dependencies",dict(base,dependencyRefs=["fact:F-ONCE","fact:F-ONCE"]),False)
]
for name,case,expected in fixtures: verify(name,check.is_valid(case),expected)
out={"task":"WAR-35","scope":"D-JCS-1 review draft structural regression","total":len(checks),"passed":len(checks),"cases":checks}
(root/"d-jcs1-schema-verification.report.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",len(checks),"PASS")

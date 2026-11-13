#!/usr/bin/env python3
"""WAR-35 P-JCS-1 raw I-JSON before-parse regression and digest evidence."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, "/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages")
from raw_ijson_gate import parse_raw_ijson, RawIJsonError
from jsonschema import Draft202012Validator
import rfc8785

cases = []
def expect(name, raw, accepted):
    try:
        value = parse_raw_ijson(raw)
        outcome = True
    except (RawIJsonError, ValueError) as exc:
        outcome = False
        value = None
    if outcome != accepted:
        raise AssertionError(f"{name}: got {outcome}, wanted {accepted}")
    cases.append({"case": name, "accepted": accepted, "passed": True})
    print("PASS", name, "accept" if accepted else "reject")
    return value

def jb(s):
    return s.encode("utf-8")

for name, raw in [
    ("duplicate-root-key", b'{"a":1,"a":2}'),
    ("duplicate-nested-key", b'{"a":{"x":1,"x":2}}'),
    ("duplicate-decoded-escaped-key", b'{"a":1,"\\u0061":2}'),
    ("duplicate-unicode-key", jb('{"é":1,"\\u00e9":2}')),
    ("unsafe-positive-integer", b'9007199254740993'),
    ("unsafe-negative-integer", b'-9007199254740992'),
    ("unsafe-integer-as-float", b'9007199254740993.0'),
    ("unsafe-integer-as-exponent", b'9.007199254740993e15'),
    ("overflow-binary64", b'1e400'),
    ("underflow-to-zero", b'1e-400'),
    ("unpaired-high-surrogate", b'"\\ud800"'),
    ("unpaired-low-surrogate", b'"\\udc00"'),
    ("unpaired-surrogate-as-key", b'{"\\ud800":"value"}'),
    ("noncharacter-in-string", b'"\\ufdd0"'),
    ("noncharacter-as-key", b'{"\\ufffe":1}'),
    ("NaN-not-JSON", b'NaN'),
    ("Infinity-not-JSON", b'Infinity'),
    ("malformed-JSON", b'{"x":1,,}'),
    ("bad-utf8", b'{"x":"\xff"}'),
    ("utf8-BOM", b'\xef\xbb\xbf{"x":1}'),
]:
    expect(name, raw, False)

for name, raw in [
    ("max-safe-positive", b'9007199254740991'),
    ("max-safe-negative", b'-9007199254740991'),
    ("normal-decimal", b'{"time":0.1,"duration":3.5}'),
    ("negative-zero", b'{"n":-0.0}'),
    ("subnormal-finite", b'5e-324'),
    ("legal-surrogate-pair", b'{"emoji":"\\ud83d\\ude00"}'),
    ("different-normalization-stays-different", jb('{"é":1,"é":2}')),
    ("reordered-keys-valid", b'{"b":2,"a":1}'),
]:
    expect(name, raw, True)

schema = json.loads((ROOT/"director-plan.schema.review-v0.json").read_text())
validator = Draft202012Validator(schema)
Draft202012Validator.check_schema(schema)
plan_digests = {}
for name in ("no-action-beat.example.review-v0.json", "cross-shot-once.example.review-v0.json"):
    pkg = expect("real-package-"+name, (ROOT/name).read_bytes(), True)
    validator.validate(pkg)
    payload = {"contractVersion":pkg["contractVersion"],"plan":pkg["plan"]}
    canonical = rfc8785.dumps(payload)
    sha = hashlib.sha256(canonical).hexdigest()
    # Existing independent JavaScript canonicalizers must produce equal bytes.
    js = subprocess.run(["node","/home/sean/.local/share/canvas-lab-jcs/verify_js.mjs"],
        input=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
    assert js == canonical, f"cross-language JCS disagreement: {name}"
    plan_digests[name] = sha
    cases.append({"case":"independent-JCS-"+name,"accepted":True,"passed":True})
    print("PASS independent-JCS", name, sha)
    # A malicious duplicate key must be caught BEFORE creating the Plan hash.
    raw = (ROOT/name).read_bytes()
    attack = raw.replace(b'"contractVersion":',b'"contractVersion":"director-plan/0.0-review","contractVersion":',1)
    expect("tampered-package-duplicate-"+name, attack, False)

report={"task":"WAR-35","scope":"P-JCS-1 raw UTF-8 I-JSON pre-parse, research only",
        "cases":cases,"passed":len(cases),"total":len(cases),
        "reviewPlanDigests":plan_digests,
        "runtimeIntegrated":False,"rawIntegerProfile":"WAR-35 strict: exact integer-valued tokens must be within ±(2^53−1); larger exact integers as JSON strings",
        "jcsLibrary":"rfc8785==0.1.4; cross-checked with independent JS canonicalization"}
(ROOT/"raw-ijson-verification.report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",len(cases),"PASS")

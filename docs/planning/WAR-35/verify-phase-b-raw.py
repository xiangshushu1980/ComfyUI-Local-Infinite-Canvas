#!/usr/bin/env python3
"""Phase B raw I-JSON -> JCS -> raw-parse closure tests. Research-only."""
import copy
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, "/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages")
import rfc8785
from jsonschema import Draft202012Validator
from raw_ijson_gate import parse_raw_ijson, RawIJsonError

ROOT = Path(__file__).resolve().parent
validator = Draft202012Validator(json.loads((ROOT / "director-plan.schema.v0-rc4.json").read_text()))
results = []

def check(name, raw, accepted, as_package=False):
    try:
        decoded = parse_raw_ijson(raw)
        if as_package:
            validator.validate(decoded)
        canonical1 = rfc8785.dumps(decoded)
        decoded2 = parse_raw_ijson(canonical1)
        canonical2 = rfc8785.dumps(decoded2)
        assert canonical1 == canonical2, "unstable JCS byte output"
        if as_package:
            validator.validate(decoded2)
        passed = True
    except (RawIJsonError, ValueError):
        passed = False
    assert accepted == passed, (name, accepted, passed)
    results.append({"case": name, "expectedAccepted": accepted, "passed": True})
    print("PASS", name, "accepted" if passed else "rejected")

rejected = [
    b"9007199254740991.9",
    b"-9007199254740991.9",
    b"9.0071992547409919e15",
    b"-9.0071992547409919e15",
    b"9007199254740992.0000001",
    b"-9007199254740992.0000001",
    b"9007199254740993.0",
    b"1e400",
    b"1e-400",
    b"9007199254740992",
    b"-9007199254740992",
]
for i, token in enumerate(rejected):
    check(f"raw-B-N{i+1:02d}-{token.decode()}", token, False)

accepted = [
    b"9007199254740991",
    b"-9007199254740991",
    b"9007199254740991.0",
    b"-9007199254740991.0",
    b"9007199254740990.1",
    b"-9007199254740990.1",
    b"1e-300",
    b"0e999999999999999999999",
    b"-0.0",
    b"5e-324",
    b"0.1",
    b'{"nested":[1.25,0.0,9007199254740991],"safe":"value"}',
]
for i, token in enumerate(accepted):
    check(f"raw-B-P{i+1:02d}-{token.decode()}", token, True)

for name in ("no-action-beat.example.v0-rc4.json", "cross-shot-once.example.v0-rc4.json"):
    raw = (ROOT / name).read_bytes()
    check("raw-B-package-" + name, raw, True, as_package=True)
    package = parse_raw_ijson(raw)
    # Parent independent of unknown fields; exact binary64 boundary appears in
    # a REAL package numeric slot, not only as a standalone number.
    if package["plan"].get("shots"):
        copy_pkg = copy.deepcopy(package)
        copy_pkg["plan"]["shots"][0]["timing"]["estimatedSeconds"] = 1.5
        safe = json.dumps(copy_pkg, ensure_ascii=False).encode()
        injected = safe.replace(b'"estimatedSeconds": 1.5',
                                b'"estimatedSeconds": 9007199254740991.9', 1)
        assert injected != safe
        check("raw-B-bad-package-boundary-" + name, injected, False, as_package=True)
report = {
    "task": "WAR-35", "scope": "Phase B raw I-JSON fixed point closure (research)",
    "schemaId": "urn:canvas-lab:director-plan:0.1.0-rc4",
    "passed": len(results), "total": len(results), "cases": results,
    "property": "accepted raw -> JCS -> raw accepted and JCS bytes identical",
    "runtimeIntegrated": False, "productionParserVerified": False,
}
(ROOT / "phase-b-raw-verification.report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print("TOTAL", len(results), "/", len(results))

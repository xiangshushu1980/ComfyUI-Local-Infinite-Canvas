#!/usr/bin/env python3
"""WAR-35 public DirectorPlan v0.1.0 design release verification.

Checks a published, immutable Schema and Golden report against the accepted RC4
baseline, original fixture bytes, Python/Node JCS, and /4 dependency digests.
This is NOT a production-grade Review authorization or media validator.
"""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, "/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages")
import rfc8785
from raw_ijson_gate import parse_raw_ijson

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_json(name):
    return parse_raw_ijson((ROOT / name).read_bytes())

def verify():
    successes = []
    def check(name, condition):
        assert condition, name
        successes.append(name)
        print("PASS", name)

    published_name = "director-plan.schema.v0.1.0.json"
    release = read_json("v0.1.0-freeze-golden.report.json")
    schema_bytes = (ROOT / published_name).read_bytes()
    published = read_json(published_name)
    candidate = read_json("director-plan.schema.v0-rc4.json")
    golden_rc4 = read_json("v0-rc4-golden.report.json")
    check("release-record-status", release["releaseType"] == "public-schema-design-freeze"
        and release["schemaId"] == "urn:canvas-lab:director-plan:0.1.0"
        and release["contractVersion"] == "director-plan/0.1.0"
        and not release["productionAuthorized"])
    check("published-schema-byte-seal", sha(schema_bytes) == release["schemaSha256"])
    check("rc4-schema-byte-seal", sha((ROOT / "director-plan.schema.v0-rc4.json").read_bytes()) == release["rc4SourceSha256"])
    check("rc4-golden-byte-seal", sha((ROOT / "v0-rc4-golden.report.json").read_bytes()) == release["rc4GoldenSourceSha256"])
    for name, obj in [("published", published), ("rc4", candidate)]:
        Draft202012Validator.check_schema(obj)
        check(name + "-meta-schema-valid", True)
    check("official-schema-identity", published["$id"] == release["schemaId"]
        and published["properties"]["contractVersion"]["const"] == release["contractVersion"])
    check("only-top-level-publishing-metadata-changes",
        {k: v for k, v in published.items() if k not in ("$id", "title", "description")}
        == {k: v for k, v in candidate.items() if k not in ("$id", "title", "description")})
    check("RC4-retains-candidate-identity",
        candidate["$id"] == "urn:canvas-lab:director-plan:0.1.0-rc4")
    check("hash-profiles-unchanged", release["planHashRule"] == "war35-plan-jcs8785-sha256/1"
        and release["dependencyHashRule"] == "war35-dep-jcs8785-sha256/4")
    validate = Draft202012Validator(published)

    # Use the already reviewed /4 canonical payload evaluator, without executing
    # the historic self-testing bottom half of the module.
    source = (ROOT / "verify-d-jcs1.py").read_text(encoding="utf-8")
    marker = 'fox=load("cross-shot-once.example.review-v0.json")'
    assert source.count(marker) == 1
    env = {"__file__": str(ROOT / "verify-d-jcs1.py")}
    exec(compile(source.split(marker)[0], str(ROOT / "verify-d-jcs1.py"), "exec"), env)
    check("trusted-checkspec-profile-loaded", env["RULE"] == release["dependencyHashRule"])
    d_digest = env["digest"]
    assert len(release["fixtures"]) == 2
    for published_fixture, record in sorted(release["fixtures"].items()):
        rc4_fixture = record["rc4Fixture"]
        raw = (ROOT / published_fixture).read_bytes()
        obj = read_json(published_fixture)
        old = read_json(rc4_fixture)
        label = published_fixture.removesuffix(".json")
        check(label + "-exact-rc4-byte-copy",
            raw == (ROOT / rc4_fixture).read_bytes()
            and sha(raw) == record["fileSha256"])
        check(label + "-schema-valid", validate.is_valid(obj))
        invalid = copy.deepcopy(obj)
        invalid["contractVersion"] = "director-plan/0.0-review"
        check(label + "-old-version-rejected", not validate.is_valid(invalid))
        payload = {"contractVersion": obj["contractVersion"], "plan": obj["plan"]}
        py_bytes = rfc8785.dumps(payload)
        js_bytes = subprocess.run(
            ["node", "/home/sean/.local/share/canvas-lab-jcs/verify_js.mjs"],
            input=json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        check(label + "-JCS-python-node-match", py_bytes == js_bytes)
        check(label + "-P-JCS-golden", sha(py_bytes) == record["planSha256"]
            and len(py_bytes) == record["canonicalBytes"]
            and record["planSha256"] == golden_rc4["golden"][rc4_fixture]["sha256"]
            and record["canonicalBytes"] == golden_rc4["golden"][rc4_fixture]["canonicalBytes"])
        it = obj["plan"]["intents"][0]
        spec = {"targetRefs": ["intent:" + it["id"]],
                "dependencyRefs": [], "collectionPaths": [],
                "checkSpec": "v0 Intent A dependency test",
                "checkSpecVersion": "intentA/v1", "method": "text"}
        d = d_digest(obj, spec)
        check(label + "-D-JCS-4-golden", d is not None
            and d == record["intentDependencySha256"]
            and d == golden_rc4["golden"][rc4_fixture]["candidateIntentDependencySha256"])
        modified = copy.deepcopy(obj)
        modified["reviewLedger"] = {"checks": [], "decisions": []}
        check(label + "-review-outside-P-JCS",
            rfc8785.dumps({"contractVersion": modified["contractVersion"], "plan": modified["plan"]}) == py_bytes)
        modified = copy.deepcopy(obj)
        modified["plan"]["revisionId"] += "-modified"
        check(label + "-plan-edit-changes-P-JCS",
            sha(rfc8785.dumps({"contractVersion": modified["contractVersion"], "plan": modified["plan"]})) != record["planSha256"])

    check("stage-b-scope-not-production-approval", release["approvedCarryForwardRule"]
        == "risk-free-unconditional-approved-intent-A-only"
        and release["shotBAutomaticCarryForward"] is False
        and release["stageBTrustManifestImplemented"] is False)
    check("regression-preflight-source-sealed", sha((ROOT / "v0-freeze-preflight-20261117.report.json").read_bytes())
        == release["preflightReportSha256"])
    print("TOTAL", len(successes), "PASS — PUBLIC DESIGN SCHEMA VERIFIED; PRODUCTION NOT AUTHORIZED")

if __name__ == "__main__":
    verify()

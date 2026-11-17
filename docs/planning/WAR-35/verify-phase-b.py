#!/usr/bin/env python3
"""WAR-35 Phase B independent research matrix: whole Gate, risk, revision."""
import copy
import json
from pathlib import Path
from phase_b_gate_rules import (
    ROOT, GATE_PROFILE, dependency_sha, plan_target, seal, stage_b_validate,
)

def check(cid, pkg, kind, member):
    ver, title, method, target_kind = GATE_PROFILE[kind]
    spec = {"targetRefs": [member], "dependencyRefs": [], "collectionPaths": [],
            "checkSpec": title, "checkSpecVersion": ver, "method": method}
    digest = dependency_sha(pkg, spec)
    assert digest is not None, (cid, member, "D-JCS unresolved")
    return {"id": cid, "target": plan_target(pkg),
            "dependencyHashRule": "war35-dep-jcs8785-sha256/4",
            "dependencyFingerprintSha256": digest, "result": "pass",
            "applicability": "valid", **spec}

def make_case():
    r2 = json.loads((ROOT / "cross-shot-once.example.v0-rc4.json").read_text())
    r2.pop("reviewLedger", None)
    r2.pop("revisionControl", None)
    r3 = copy.deepcopy(r2)
    r3["plan"]["revisionId"] = "R3"
    added = copy.deepcopy(r3["plan"]["shots"][-1])
    added["id"] = "S-ADDED"
    # This is a second presentation of the action, not a second completion.
    for coverage in added.get("actionCoverage", []):
        coverage.pop("completionDeltaRef", None)
    r3["plan"]["shots"].append(added)
    r3["revisionControl"] = {
        "candidates": [{
            "revisionId": "R3",
            "basedOnRevisionId": "R2",
            "actualChangedPaths": ["/shots"],
        }]
    }
    a2 = check("C-A2", r2, "intentA", "intent:I-CROSS")
    a3 = check("C-A3", r3, "intentA", "intent:I-CROSS")
    b_checks = [check("C-B-" + s["id"], r3, "shotB", "shot:" + s["id"])
                for s in r3["plan"]["shots"]]
    da2 = {"id": "D-A2", "gate": "intentA", "target": plan_target(r2),
           "verdict": "approved", "checkIds": ["C-A2"], "decisionBasis": "reviewed",
           "rationale": "reviewed original Director Intent"}
    da3 = {"id": "D-A3", "gate": "intentA", "target": plan_target(r3),
           "verdict": "approved", "checkIds": ["C-A3"], "decisionBasis": "verified_carry_forward",
           "fromDecisionId": "D-A2", "rationale": "same intent proven in direct parent"}
    db3 = {"id": "D-B3", "gate": "shotB", "target": plan_target(r3),
           "verdict": "approved", "checkIds": [c["id"] for c in b_checks],
           "decisionBasis": "reviewed", "rationale": "all shot criteria text-reviewed"}
    inheritance = {"fromCheckId": "C-A2", "intoCheckId": "C-A3",
                   "intoTarget": plan_target(r3),
                   "dependencyHashRule": "war35-dep-jcs8785-sha256/4",
                   "dependencyFingerprintSha256": a2["dependencyFingerprintSha256"],
                   "basis": "unchanged_dependencies"}
    assert a2["dependencyFingerprintSha256"] == a3["dependencyFingerprintSha256"]
    case = {
        "packages": [r2, r3],
        "currentKey": ["P-FOX", "R3"],
        "sealedPlans": {"P-FOX|R2": plan_target(r2)["planContentSha256"],
                        "P-FOX|R3": plan_target(r3)["planContentSha256"]},
        "sealedParentEdges": {"P-FOX|R3": seal({
            "childTarget": plan_target(r3), "parentTarget": plan_target(r2)})},
        "sealedRiskManifests": {"P-FOX|R2": seal([]), "P-FOX|R3": seal([])},
        "checks": [a2, a3, *b_checks],
        "decisions": [da2, da3, db3],
        "inheritances": [inheritance],
        "risks": [],
        "sealedRisks": {},
        "sealedChecks": {"C-A2": seal(a2)},
        "sealedDecisions": {"D-A2": seal(da2)},
        "approvedPlan": {"decisionId": "D-B3", "gate": "shotB", "target": plan_target(r3)},
    }
    refresh_authoritative(case)
    return case

def refresh_authoritative(case):
    """Research fixture only: simulate an EXTERNALLY TRUSTED append-only store.

    Never perform this from user-provided data in a production validator.
    Call only after intentionally adding/reviewing a legitimate record, so
    negative cases test precise semantics rather than an unrelated stale seal.
    """
    case["trustedCurrentTarget"] = plan_target(case["packages"][-1])
    case["sealedChecks"] = {c["id"]: seal(c) for c in case["checks"]}
    case["sealedDecisions"] = {d["id"]: seal(d) for d in case["decisions"]}
    manifests = {}
    for pkg in case["packages"]:
        for gate in GATE_PROFILE:
            rows = sorted([
                [d["id"], seal(d)] for d in case["decisions"]
                if d["gate"] == gate and d["target"] == plan_target(pkg)
            ])
            manifests[pkg["plan"]["planId"] + "|" + pkg["plan"]["revisionId"] + "|" + gate] = seal(rows)
    case["sealedDecisionManifests"] = manifests

def refresh_current(case):
    """Restore legitimate current signatures after a Plan edit to isolate Gate bugs."""
    pkg = case["packages"][-1]
    t = plan_target(pkg)
    case["sealedPlans"]["P-FOX|" + pkg["plan"]["revisionId"]] = t["planContentSha256"]
    for c in case["checks"]:
        if c["id"] == "C-A2":
            continue
        c["target"] = t
        c["dependencyFingerprintSha256"] = (
            dependency_sha(pkg, c) or "f" * 64)
    for d in case["decisions"]:
        if d["id"] != "D-A2":
            d["target"] = t
    for e in case["inheritances"]:
        e["intoTarget"] = t
    for r in case["risks"]:
        r["target"] = t
        case["sealedRisks"][r["id"] + "|" + r["riskVersionId"]] = seal(r)
    case["approvedPlan"]["target"] = t
    case["sealedParentEdges"]["P-FOX|R3"] = seal({
        "childTarget": t, "parentTarget": plan_target(case["packages"][0])})
    reseal_manifest(case)
    refresh_authoritative(case)

def reseal_manifest(case):
    for pkg in case["packages"]:
        target = plan_target(pkg)
        rows = sorted([
            [r["id"], r["riskVersionId"], seal(r)]
            for r in case["risks"] if r["target"] == target
        ])
        case["sealedRiskManifests"][
            pkg["plan"]["planId"] + "|" + pkg["plan"]["revisionId"]] = seal(rows)

def add_risk(case, name="R-UNKNOWN", version="V1", kind="unknown",
             status="open", refs=None):
    risk = {"id": name, "riskVersionId": version,
            "target": plan_target(case["packages"][-1]),
            "targetRefs": refs if refs is not None else ["shot:S02"],
            "kind": kind, "description": "Current version still needs review",
            "status": status}
    case["risks"].append(risk)
    case["sealedRisks"][name + "|" + version] = seal(risk)
    reseal_manifest(case)

def conditional(case, *risk_names):
    d = case["decisions"][-1]
    d["verdict"] = "conditionally_approved"
    d["acceptedRisks"] = [
        {"riskId": name, "riskVersionId": "V1"} for name in risk_names
    ]
    d["rationale"] = "Explicitly accept evidence uncertainty"
    refresh_authoritative(case)

def new_intent(case):
    i = copy.deepcopy(case["packages"][-1]["plan"]["intents"][0])
    i["id"] = "I-NEW"
    i["creativeGoal"] = "Withhold the landing"
    case["packages"][-1]["plan"]["intents"].append(i)
    refresh_current(case)

def new_shot(case):
    s = copy.deepcopy(case["packages"][-1]["plan"]["shots"][-1])
    s["id"] = "S-LATE"
    case["packages"][-1]["plan"]["shots"].append(s)
    refresh_current(case)

def skip_parent(case):
    mid = copy.deepcopy(case["packages"][0])
    mid["plan"]["revisionId"] = "R-intermediate"
    case["packages"].insert(1, mid)
    case["sealedPlans"]["P-FOX|R-intermediate"] = plan_target(mid)["planContentSha256"]
    case["packages"][-1]["revisionControl"]["candidates"][0]["basedOnRevisionId"] = "R-intermediate"
    reseal_manifest(case)
    refresh_authoritative(case)

def duplicate_revision(case):
    alt = copy.deepcopy(case["packages"][0])
    alt["plan"]["storyBasis"]["facts"][0]["statement"] += "!"
    case["packages"].insert(1, alt)

def set_wrong_B_target(case):
    c = next(c for c in case["checks"] if c["id"] == "C-B-S01")
    c["targetRefs"] = ["subject:CREEK"]
    c["dependencyFingerprintSha256"] = dependency_sha(case["packages"][-1], c) or "f" * 64
    refresh_authoritative(case)

def set_wrong_B_method(case):
    c = next(c for c in case["checks"] if c["id"] == "C-B-S01")
    c["method"] = "geometry_proxy"
    c["dependencyFingerprintSha256"] = dependency_sha(case["packages"][-1], c) or "f" * 64
    refresh_authoritative(case)

def external_check(case):
    c = case["checks"][1]
    c["evidenceRefs"] = ["evidence:UNVERIFIED-1"]
    c["dependencyFingerprintSha256"] = dependency_sha(case["packages"][-1], c) or "f" * 64
    refresh_authoritative(case)

def conflicting_decision(case):
    d = copy.deepcopy(case["decisions"][-1])
    d["id"] = "D-B3-LATER"
    d["verdict"] = "rejected"
    case["decisions"].append(d)
    refresh_authoritative(case)

def scoped_decision(case):
    case["decisions"][-1]["executionTarget"] = {
        "unitRef": "UNIT-1", "projectionRevision": "PR1",
        "projectionContentSha256": "a"*64,
        "projectionHashRule": "war52-projection-test/1",
    }
    refresh_authoritative(case)

def no_direct_parent(case):
    case["packages"][-1]["revisionControl"]["candidates"] = []

def risk_new_version(case):
    add_risk(case, name="R-UNKNOWN", version="V1", status="closed")
    add_risk(case, name="R-UNKNOWN", version="V2", status="open")

def tamper_source(case):
    case["packages"][0]["plan"]["storyBasis"]["facts"][0]["statement"] += "!"

def lost_check(case):
    case["decisions"][-1]["checkIds"].remove("C-B-S01")
    refresh_authoritative(case)

def stale_current_decision(case):
    case["decisions"][-1]["verdict"] = "changes_requested"
    refresh_authoritative(case)

def unknown_risk_scope(case):
    add_risk(case, refs=["subject:FOX"])

def omit_indexed_risk(case):
    add_risk(case, kind="hard_conflict")
    case["risks"].clear()  # trusted manifest still contains R-UNKNOWN

# Astra's fixed-commit independent counterexamples. Each malicious omission
# retains the preexisting trusted manifest; this is deliberately NOT resealed.
def omit_conflicting_decision(case):
    conflicting_decision(case)  # explicitly register the competing rejection
    case["decisions"].pop()     # caller hides it; trusted index stays unchanged

def mutate_current_decision(case):
    case["decisions"][-1]["verdict"] = "rejected"
    refresh_authoritative(case)  # independent history now seals rejected
    case["decisions"][-1]["verdict"] = "approved"  # caller-only rewrite

def scoped_A_decision(case, idx):
    case["decisions"][idx]["executionTarget"] = {
        "unitRef": "UNIT-1", "projectionRevision": "PR1",
        "projectionContentSha256": "a" * 64,
        "projectionHashRule": "war52-projection-test/1",
    }
    refresh_authoritative(case)

def bad_risk_status_with_valid_manifest(case):
    add_risk(case, kind="hard_conflict")
    risk = case["risks"][0]
    risk["status"] = "OPEN"  # not the Schema enum
    case["sealedRisks"][risk["id"] + "|" + risk["riskVersionId"]] = seal(risk)
    reseal_manifest(case)  # simulate accepted immutable blob; Schema still fails

def missing_inheritance_basis(case):
    del case["inheritances"][0]["basis"]

def change_trusted_current(case):
    case["currentKey"] = ["P-FOX", "R2"]  # trusted current stays R3

def missing_decision_manifest(case):
    del case["sealedDecisionManifests"]["P-FOX|R3|shotB"]

def current_check_rewritten(case):
    case["checks"][-1]["result"] = "fail"  # seal retains original pass

CASES = [
    ("B-P01-direct-parent-A-carry-full-B-text-coverage", lambda c: None, True),
    ("B-N01-added-intent-missing-A-check", new_intent, False),
    ("B-N02-added-shot-missing-B-check", new_shot, False),
    ("B-N03-omitted-required-shot-B-check", lost_check, False),
    ("B-N04-B-check-target-wrong-kind", set_wrong_B_target, False),
    ("B-N05-B-check-forged-geometry-method", set_wrong_B_method, False),
    ("B-N06-A-check-dependent-on-unbound-external-evidence", external_check, False),
    ("B-N07-hard-conflict-omitted-from-approval", lambda c: add_risk(c, kind="hard_conflict"), False),
    ("B-N08-open-unknown-risk-not-accepted", lambda c: add_risk(c), False),
    ("B-P02-conditional-accept-all-current-unknown-risks",
     lambda c: (add_risk(c), conditional(c, "R-UNKNOWN")), True),
    ("B-N09-conditional-omits-second-relevant-risk",
     lambda c: (add_risk(c), add_risk(c, "R-SECOND"), conditional(c, "R-UNKNOWN")), False),
    ("B-N10-conflicting-same-target-reviewed-decisions", conflicting_decision, False),
    ("B-N11-projection-scoped-B-not-whole-Plan", scoped_decision, False),
    ("B-N12-identical-revision-ID-different-content", duplicate_revision, False),
    ("B-N13-direct-parent-skipped", skip_parent, False),
    ("B-N14-missing-direct-parent-candidate", no_direct_parent, False),
    ("B-N15-unsealed-current-Plan-revision", lambda c: c["sealedPlans"].pop("P-FOX|R3"), False),
    ("B-N16-tampered-trusted-ancestor", tamper_source, False),
    ("B-N17-stale-approvedPlan-pointer", lambda c: c["approvedPlan"].update(decisionId="D-A3"), False),
    ("B-N18-two-current-risk-versions-ambiguous", risk_new_version, False),
    ("B-N19-unprovable-risk-applicability", unknown_risk_scope, False),
    ("B-N20-current-B-not-approved", stale_current_decision, False),
    ("B-N21-inherited-source-check-unsealed", lambda c: c["sealedChecks"].clear(), False),
    ("B-N22-inherited-source-decision-unsealed", lambda c: c["sealedDecisions"].clear(), False),
    ("B-N23-caller-omits-trusted-risk-ledger-entry", omit_indexed_risk, False),
    ("B-N24-parent-edge-seal-missing", lambda c: c["sealedParentEdges"].clear(), False),
    ("B-N25-omitted-conflicting-decision-with-trusted-index", omit_conflicting_decision, False),
    ("B-N26-current-decision-content-forged-after-seal", mutate_current_decision, False),
    ("B-N27-scoped-source-A-cannot-carry-to-whole-gate", lambda c: scoped_A_decision(c, 0), False),
    ("B-N28-scoped-current-A-cannot-authorize-whole-gate", lambda c: scoped_A_decision(c, 1), False),
    ("B-N29-malformed-risk-enum-even-when-sealed", bad_risk_status_with_valid_manifest, False),
    ("B-N30-inheritance-missing-required-basis", missing_inheritance_basis, False),
    ("B-N31-untrusted-current-revision-selection", change_trusted_current, False),
    ("B-N32-missing-trusted-decision-manifest", missing_decision_manifest, False),
    ("B-N33-current-check-content-forged-after-seal", current_check_rewritten, False),
]
results = []
for name, edit, expected in CASES:
    c = make_case()
    edit(c)
    evaluation = stage_b_validate(c)
    accepted = evaluation["wholePlan"]
    passed = accepted == expected
    results.append({"case": name, "expected": expected, "observed": accepted,
                    "passed": passed, "reason": evaluation.get("reason")})
    print(("PASS " if passed else "FAIL ") + name +
          (": " + str(evaluation.get("reason")) if not accepted else ""))
report = {
    "task": "WAR-35", "scope": "Phase B candidate research semantic Gate/risk/direct-parent",
    "sourceSchema": "urn:canvas-lab:director-plan:0.1.0-rc4",
    "passed": sum(r["passed"] for r in results), "total": len(results),
    "cases": results, "productionApprovalServiceImplemented": False,
    "trustedHistory": "synthetic immutable seals, not authenticated storage",
    "realMediaVerified": False,
}
(ROOT / "phase-b-gates-verification.report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print("TOTAL", report["passed"], "/", report["total"])
if report["passed"] != report["total"]:
    raise SystemExit(1)

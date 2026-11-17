#!/usr/bin/env python3
"""WAR-35 Phase B research evaluator. Not a production approval service.

The trusted seals in an input case are synthetic stand-ins for append-only,
authenticated review/version records. Never accept self-declared seals in
production. This validator deliberately fails closed outside its v0 profile.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
sys.path.insert(0, "/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages")
import rfc8785

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "director-plan.schema.v0-rc4.json").read_text())
CHECK_VALIDATOR = Draft202012Validator({"$defs": SCHEMA["$defs"], "$ref": "#/$defs/check"})
DECISION_VALIDATOR = Draft202012Validator({"$defs": SCHEMA["$defs"], "$ref": "#/$defs/decision"})
RISK_VALIDATOR = Draft202012Validator({"$defs": SCHEMA["$defs"], "$ref": "#/$defs/risk"})
INHERITANCE_VALIDATOR = Draft202012Validator({"$defs": SCHEMA["$defs"], "$ref": "#/$defs/inheritance"})
PACKAGE_VALIDATOR = Draft202012Validator(SCHEMA)

# The immutable RC4 CheckSpec registry + /4 D-JCS implementation are reused.
PRELUDE = (ROOT / "verify-d-jcs1.py").read_text().split(
    'fox=load("cross-shot-once.example.review-v0.json")'
)[0]
ENV = {"__file__": str(ROOT / "verify-d-jcs1.py")}
exec(compile(PRELUDE, str(ROOT / "verify-d-jcs1.py"), "exec"), ENV)
dependency_sha = ENV["digest"]

GATE_PROFILE = {
    "intentA": ("intentA/2", "Intent A: narrative goal consistency", "text", "intent"),
    "shotB": ("shotB/1", "Shot B: output evidence criteria", "text", "shot"),
}

def seal(value):
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()

def plan_target(package):
    plan = package["plan"]
    return {
        "planId": plan["planId"],
        "revisionId": plan["revisionId"],
        "planContentSha256": seal({"contractVersion": package["contractVersion"], "plan": plan}),
        "hashRule": "war35-plan-jcs8785-sha256/1",
    }

class InvalidGate(ValueError):
    pass

def demand(condition, reason):
    if not condition:
        raise InvalidGate(reason)

def indexed(items, key):
    out = {}
    for value in items:
        identity = key(value)
        demand(identity not in out, f"duplicate record: {identity}")
        out[identity] = value
    return out

def stage_b_validate(case):
    """Return per-gate booleans and rejection reasons for a frozen research case."""
    result = {}
    try:
        packages = indexed(case["packages"], lambda p: (p["plan"]["planId"], p["plan"]["revisionId"]))
        for key, pkg in packages.items():
            demand(PACKAGE_VALIDATOR.is_valid(pkg), "invalid package shape")
            demand(case["sealedPlans"].get("|".join(key)) == plan_target(pkg)["planContentSha256"],
                   "untrusted or changed plan revision")
        current = packages[tuple(case["currentKey"])]
        current_target = plan_target(current)
        # Same trust rule as revision/risk manifests: the authoritative
        # workspace selects the current target, not the approval caller.
        demand(case["trustedCurrentTarget"] == current_target,
               "caller selected an untrusted current revision")
        checks = indexed(case["checks"], lambda c: c["id"])
        decisions = indexed(case["decisions"], lambda d: d["id"])
        inheritance = indexed(case["inheritances"], lambda e: e["intoCheckId"])
        risks = indexed(case["risks"], lambda r: (r["id"], r["riskVersionId"], r["target"]["revisionId"]))
        demand(all(RISK_VALIDATOR.is_valid(r) for r in risks.values()), "invalid risk shape")
        demand(all(INHERITANCE_VALIDATOR.is_valid(i) for i in inheritance.values()),
               "invalid inheritance shape")
        target_to_package = indexed(case["packages"], lambda p: json.dumps(plan_target(p), sort_keys=True))
        # The caller cannot omit an inconvenient Risk: the complete risk index
        # for each revision is from an independently sealed authoritative ledger.
        for key, pkg in packages.items():
            expected = [
                [r["id"], r["riskVersionId"], seal(r)]
                for r in risks.values() if r["target"] == plan_target(pkg)
            ]
            expected.sort()
            demand(case["sealedRiskManifests"].get("|".join(key)) == seal(expected),
                   "risk manifest incomplete or untrusted")
            for gate in GATE_PROFILE:
                # Complete, independently trusted decision index is essential:
                # omitting a conflicting rejection must not restore approval.
                rows = sorted([
                    [dec["id"], seal(dec)] for dec in decisions.values()
                    if dec["gate"] == gate and dec["target"] == plan_target(pkg)
                ])
                manifest_key = "|".join(key) + "|" + gate
                demand(case["sealedDecisionManifests"].get(manifest_key) == seal(rows),
                       "decision manifest incomplete or untrusted")
        competing = {}
        for dec in decisions.values():
            key = (dec["gate"], json.dumps(dec["target"], sort_keys=True))
            competing.setdefault(key, []).append(dec["id"])

        def required(gate, pkg):
            key = "intents" if gate == "intentA" else "shots"
            kind = GATE_PROFILE[gate][3]
            members = {kind + ":" + o["id"] for o in pkg["plan"][key]}
            demand(len(members) == len(pkg["plan"][key]) and len(members) > 0,
                   "gate members missing or duplicated")
            if gate == "shotB":
                for shot in pkg["plan"]["shots"]:
                    criteria = shot.get("evidenceCriteria", [])
                    demand(bool(criteria), "shot has no observable evidence criteria")
                    demand(len({c["id"] for c in criteria}) == len(criteria),
                           "shot criteria IDs are not unique")
            return members

        def verified_check(check, expected_gate, pkg):
            expected = GATE_PROFILE[expected_gate]
            demand(CHECK_VALIDATOR.is_valid(check), "invalid check schema")
            demand(check["target"] == plan_target(pkg), "check target mismatch")
            demand(case["sealedChecks"].get(check["id"]) == seal(check),
                   "check content not backed by trusted history")
            demand(check["result"] == "pass" and check["applicability"] == "valid",
                   "check is not valid pass")
            demand(check["checkSpecVersion"] == expected[0] and
                   check["checkSpec"] == expected[1] and check["method"] == expected[2],
                   "method/spec/gate spoofing")
            # External observations are not independently bound in nonmedia /4.
            demand(not check.get("evidenceRefs") and not check.get("evidenceBindings") and
                   not check.get("executionTarget"), "unresolved external evidence")
            demand(len(check["targetRefs"]) == 1 and
                   check["targetRefs"][0] in required(expected_gate, pkg),
                   "uncovered or incorrectly typed member")
            digest = dependency_sha(pkg, check)
            demand(digest is not None and digest == check["dependencyFingerprintSha256"],
                   "missing/stale dependency proof")
            return check["targetRefs"][0]

        def current_risks(gate, pkg, dec):
            scope = required(gate, pkg)
            other_gate = "shotB" if gate == "intentA" else "intentA"
            other = required(other_gate, pkg)
            current_risk = [r for r in risks.values() if r["target"] == plan_target(pkg)]
            # Do not guess which version is current if two appear for the same plan.
            demand(len({r["id"] for r in current_risk}) == len(current_risk),
                   "ambiguous current risk versions")
            applicable = {}
            for risk in current_risk:
                key = (risk["id"], risk["riskVersionId"])
                demand(case["sealedRisks"].get("|".join(key)) == seal(risk),
                       "risk version modified or untrusted")
                refs = set(risk["targetRefs"])
                demand(bool(refs), "risk has unknown scope")
                if refs & scope:
                    applicable[key] = risk
                elif refs <= other:
                    # e.g. an Intent-only risk is outside the Shot gate
                    continue
                else:
                    demand(False, "risk applicability cannot be proved")
            accept = {(p["riskId"], p["riskVersionId"]) for p in dec.get("acceptedRisks", [])}
            demand(len(accept) == len(dec.get("acceptedRisks", [])), "duplicate risk selection")
            demand(accept <= set(applicable), "invented or out-of-scope accepted risk")
            open_risks = {k: r for k, r in applicable.items() if r["status"] == "open"}
            demand(not any(r["kind"] == "hard_conflict" for r in open_risks.values()),
                   "open hard conflict")
            if dec["verdict"] == "approved":
                demand(not open_risks and not accept, "unaccepted applicable risk")
            elif dec["verdict"] == "conditionally_approved":
                demand(set(open_risks) == accept, "incomplete applicable risk coverage")
                demand(bool(dec.get("rationale")), "conditional approval without rationale")
            return True

        def valid_decision(dec_id, seen=None):
            seen = set() if seen is None else seen
            demand(dec_id not in seen, "cyclic decision")
            dec = decisions[dec_id]
            demand(DECISION_VALIDATOR.is_valid(dec), "invalid decision shape")
            demand(case["sealedDecisions"].get(dec["id"]) == seal(dec),
                   "decision content not backed by trusted history")
            gate = dec["gate"]
            demand(gate in GATE_PROFILE, "unsupported gate")
            demand("executionTarget" not in dec,
                   "projection-scoped decision cannot authorize a whole gate")
            key = (gate, json.dumps(dec["target"], sort_keys=True))
            demand(len(competing[key]) == 1, "conflicting decisions without trusted supersession")
            pkg = target_to_package.get(json.dumps(dec["target"], sort_keys=True))
            demand(pkg is not None, "unknown decision target")
            scope = required(gate, pkg)
            demand(bool(dec["checkIds"]), "empty gate checks")
            got = {verified_check(checks[check_id], gate, pkg) for check_id in dec["checkIds"]}
            demand(len(got) == len(dec["checkIds"]) and got == scope,
                   "whole gate member/check coverage incomplete")
            current_risks(gate, pkg, dec)
            if dec["decisionBasis"] == "verified_carry_forward":
                demand(gate == "intentA" and dec["verdict"] == "approved" and
                       not dec.get("acceptedRisks"), "carry is not risk-free A approval")
                source = decisions[dec["fromDecisionId"]]
                demand(case["sealedDecisions"].get(source["id"]) == seal(source),
                       "source decision untrusted")
                demand(source["gate"] == "intentA" and source["verdict"] == "approved" and
                       not source.get("acceptedRisks"), "prior decision cannot carry")
                demand(source["target"]["planId"] == dec["target"]["planId"] and
                       source["target"] != dec["target"], "source target not an earlier revision")
                # Trust the versioned basedOnRevisionId edge, not revision name ordering.
                candidates = (pkg.get("revisionControl") or {}).get("candidates", [])
                own_candidates = [c for c in candidates if c["revisionId"] == pkg["plan"]["revisionId"]]
                demand(len(own_candidates) == 1, "missing or ambiguous revision parent")
                parent_revision = own_candidates[0]["basedOnRevisionId"]
                demand(parent_revision == source["target"]["revisionId"],
                       "carry skips direct parent revision")
                parent = packages.get((pkg["plan"]["planId"], parent_revision))
                demand(parent is not None and plan_target(parent) == source["target"],
                       "direct parent is untrusted or does not match source")
                edge = {"childTarget": plan_target(pkg), "parentTarget": plan_target(parent)}
                demand(case["sealedParentEdges"].get(
                    pkg["plan"]["planId"] + "|" + pkg["plan"]["revisionId"]) == seal(edge),
                    "direct parent edge not in trusted history")
                valid_decision(source["id"], seen | {dec_id})
                prior_checks = set(source["checkIds"])
                mapped = set()
                for cid in dec["checkIds"]:
                    entry = inheritance.get(cid)
                    demand(entry is not None and entry["intoTarget"] == dec["target"],
                           "inheritance missing or target changed")
                    prior = checks[entry["fromCheckId"]]
                    demand(prior["id"] in prior_checks and
                           case["sealedChecks"].get(prior["id"]) == seal(prior),
                           "source check missing or tampered")
                    demand(prior["target"] == source["target"] and
                           entry["dependencyHashRule"] == prior["dependencyHashRule"] ==
                           checks[cid]["dependencyHashRule"] and
                           entry["dependencyFingerprintSha256"] == prior["dependencyFingerprintSha256"] ==
                           checks[cid]["dependencyFingerprintSha256"],
                           "inherited check proof differs")
                    mapped.add(prior["id"])
                demand(mapped == prior_checks and len(prior_checks) == len(dec["checkIds"]),
                       "partial source check mapping")
            return True

        for gate in GATE_PROFILE:
            current_decisions = [d for d in decisions.values()
                                 if d["gate"] == gate and d["target"] == current_target]
            demand(len(current_decisions) == 1, "missing/ambiguous current gate decision")
            dec = current_decisions[0]
            valid_decision(dec["id"])
            demand(dec["verdict"] in ("approved", "conditionally_approved"),
                   "current gate not approved")
            result[gate] = True
        pointer = case["approvedPlan"]
        bdec = next(d for d in decisions.values()
                    if d["gate"] == "shotB" and d["target"] == current_target)
        demand(pointer == {"decisionId": bdec["id"], "gate": "shotB", "target": current_target},
               "approvedPlan pointer mismatch")
        demand("executionTarget" not in bdec, "projection-scoped approval is not whole Plan approval")
        result["wholePlan"] = True
    except (KeyError, TypeError, ValueError, AttributeError, StopIteration) as exc:
        result["wholePlan"] = False
        result["reason"] = str(exc)
    return result

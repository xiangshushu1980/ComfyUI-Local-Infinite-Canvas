"""WAR-35 versioned Fact source-proof checks through digest and Intent A carry."""
import hashlib
import json
import runpy
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
phase = runpy.run_path(str(ROOT / "verify-phase-a.py"))
g = phase["gates"]
fixture = phase["fixture"]
fact_spec = dict(g["spec"], targetRefs=["fact:F-ONCE"], checkSpecVersion="fact-script/1",
                 checkSpec="Target Facts agree with the supplied script text")
local_spec = dict(fact_spec, checkSpecVersion="fact-local/1", checkSpec="Fact statement is nonempty")


def vary(old, mode):
    new = deepcopy(old)
    new["plan"]["revisionId"] = "R3"
    if mode == "missing":
        del new["sourceSnapshots"]
    if mode == "changed":
        text = "狐狸留在近岸，没有跳过小溪。"
        sha = hashlib.sha256(text.encode()).hexdigest()
        new["sourceSnapshots"][0].update(text=text, contentSha256=sha)
        new["plan"]["storyBasis"]["sources"][0]["contentSha256"] = sha
    return new


def carry(old, new, spec):
    case = g["make_case"]()
    case["packages"] = [old, new]
    for idx, pkg in enumerate(case["packages"]):
        check = g["make_check"](case["checks"][idx]["id"], pkg, spec)
        # Present a shape-valid pass even when the caller lacks a verified digest.
        check["dependencyFingerprintSha256"] = check["dependencyFingerprintSha256"] or "0" * 64
        case["checks"][idx] = check
        case["decisions"][idx]["target"] = check["target"]
    previous = case["checks"][0]
    case["sealed"]["C-A1"] = g["seal"](previous)
    case["sealed"]["D-A1"] = g["seal"](case["decisions"][0])
    case["inheritances"][0].update(intoTarget=g["plan_target"](new),
                                   dependencyFingerprintSha256=previous["dependencyFingerprintSha256"])
    return g["valid_case"](case, False)


rows = []


def record(name, observed, expected):
    rows.append(dict(case=name, observed=observed, expected=expected, passed=observed == expected))


for linked in (False, True):
    prior = deepcopy(fixture)
    if not linked:
        prior["plan"]["storyBasis"]["facts"][0]["sourceRefs"] = []
    for mode in ("unchanged", "changed", "missing"):
        current = vary(prior, mode)
        for pkg in (prior, current):
            phase["validator"].validate(pkg)
        a, b = [g["dep_sha"](pkg, fact_spec) for pkg in (prior, current)]
        relation = "unresolved" if b is None else "same" if a == b else "different"
        expected = "unresolved" if not linked or mode == "missing" else "different" if mode == "changed" else "same"
        label = ("linked" if linked else "orphan") + "-" + mode
        record(label + "-digest", relation, expected)
        record(label + "-Intent-A", carry(prior, current, g["spec"]), linked and mode == "unchanged")

orphan = deepcopy(fixture)
orphan["plan"]["storyBasis"]["facts"][0]["sourceRefs"] = []
for spec in (fact_spec, g["spec"]):
    seeded = dict(spec, dependencyRefs=["source:S-FOX"])
    record(spec["targetRefs"][0] + "-unrelated-seed", g["dep_sha"](orphan, seeded) is None, True)
record("unrelated-seed-Intent-A", carry(orphan, vary(orphan, "unchanged"),
                                       dict(g["spec"], dependencyRefs=["source:S-FOX"])), False)
a = g["dep_sha"](orphan, local_spec)
record("local-orphan-no-bytes", a is not None and a == g["dep_sha"](vary(orphan, "missing"), local_spec), True)
record("unregistered-spec", g["dep_sha"](fixture, dict(fact_spec, checkSpecVersion="unknown")) is None, True)
record("mislabeled-spec", g["dep_sha"](orphan, dict(fact_spec, checkSpecVersion="fact-local/1")) is None, True)
record("old-profile-refused", g["dep_sha"](fixture, dict(fact_spec, dependencyHashRule="war35-dep-jcs8785-sha256/2")) is None, True)
# A second well-sourced seed cannot stand in for the checked orphan.
other = deepcopy(orphan)
other["plan"]["storyBasis"]["facts"].append(dict(fixture["plan"]["storyBasis"]["facts"][0], id="OTHER"))
record("other-fact-seed", g["dep_sha"](other, dict(fact_spec, dependencyRefs=["fact:OTHER"])) is None, True)
# An independently sourced sibling must not hide an orphan behind a Constraint.
mixed = deepcopy(orphan)
mixed["plan"]["storyBasis"]["constraints"] = [
    {"id": "K", "statement": "story constraint", "sourceRefs": ["fact:F-ONCE"]}]
mixed["plan"]["intents"][0]["basisRefs"] = ["constraint:K", "source:S-FOX"]
phase["validator"].validate(mixed)
record("indirect-orphan-Intent-A", carry(mixed, vary(mixed, "unchanged"), g["spec"]), False)
mixed["plan"]["storyBasis"]["facts"][0]["sourceRefs"] = ["source:S-FOX"]
record("indirect-linked-Intent-A", carry(mixed, vary(mixed, "unchanged"), g["spec"]), True)
mixed["plan"]["intents"][0]["basisRefs"] = ["source:S-FOX"]
record("direct-script-Intent-A", carry(mixed, vary(mixed, "unchanged"), g["spec"]), True)
record("local-policy-cannot-authorize-Intent-A", carry(orphan, vary(orphan, "missing"), local_spec), False)
report = dict(profile=g["inherit"]["dependencyHashRule"], cases=rows, passed=sum(r["passed"] for r in rows))
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] == len(rows) else 1)

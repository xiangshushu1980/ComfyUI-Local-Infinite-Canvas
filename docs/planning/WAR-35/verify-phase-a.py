"""RC1 Phase A regressions. Run with Eric's system python3."""
import json
import unittest
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent


def definitions(name, end):
    path = ROOT / name
    env = {"__file__": str(path)}
    exec(compile(path.read_text().split(end)[0], str(path), "exec"), env)
    return env


gates = definitions("verify-decision-gates.py", "tests=[]")
digest = gates["dep_sha"]
fixture = json.loads((ROOT / "cross-shot-once.example.v0-rc1.json").read_text())
validator = Draft202012Validator(json.loads((ROOT / "director-plan.schema.v0-rc1.json").read_text()))


class PhaseA(unittest.TestCase):
    def fingerprint(self, pkg, path=None, target="subject:CREEK"):
        validator.validate(pkg)
        spec = dict(gates["spec"], targetRefs=[target], collectionPaths=[path] if path else [])
        return digest(pkg, spec)

    def test_direct_reference_set_closure(self):
        changed = deepcopy(fixture)
        changed["plan"]["storyBasis"]["facts"][0]["statement"] += "!"
        path = "/intents/0/basisRefs"
        before = self.fingerprint(fixture, path)
        self.assertIsNotNone(before)
        self.assertNotIn(self.fingerprint(changed, path), (None, before))

    def test_required_source(self):
        for path, target in [("/storyBasis/sources", "subject:CREEK"),
                             ("/intents/0/basisRefs", "subject:CREEK"),
                             (None, "plan:P-FOX")]:
            for failure in ("missing", "forged", "asset"):
                with self.subTest(path=path, target=target, failure=failure):
                    changed = deepcopy(fixture)
                    if failure == "missing":
                        del changed["sourceSnapshots"]
                    elif failure == "forged":
                        changed["sourceSnapshots"][0]["text"] += "!"
                    else:
                        changed["plan"]["storyBasis"]["sources"][0]["mediaKind"] = "asset"
                    self.assertIsNotNone(self.fingerprint(fixture, path, target))
                    self.assertIsNone(self.fingerprint(changed, path, target))

    def test_opaque_order(self):
        first = deepcopy(fixture)
        value = {"subjectRefs": ["subject:FOX", "subject:CREEK"]}
        first["plan"]["state"]["deltas"][0]["after"]["value"] = value
        second = deepcopy(first)
        second["plan"]["state"]["deltas"][0]["after"]["value"]["subjectRefs"].reverse()
        for path in (None, "/state/deltas/0/after/value/subjectRefs"):
            with self.subTest(path=path):
                a = self.fingerprint(first, path, "delta:D-LAND")
                self.assertIsNotNone(a)
                self.assertNotIn(self.fingerprint(second, path, "delta:D-LAND"), (None, a))

    def test_typed_set_order(self):
        path = "/shots/0/visualDesign/subjectRefs"
        changed = deepcopy(fixture)
        changed["plan"]["shots"][0]["visualDesign"]["subjectRefs"].reverse()
        first = self.fingerprint(fixture, path)
        self.assertIsNotNone(first)
        self.assertEqual(first, self.fingerprint(changed, path))

    def test_indirect_action(self):
        path = "/beats/0/actionRefs"
        changed = deepcopy(fixture)
        changed["plan"]["actions"][0]["description"] += "!"
        first = self.fingerprint(fixture, path)
        self.assertIsNotNone(first)
        self.assertNotIn(self.fingerprint(changed, path), (None, first))

    def test_opaque_literal_is_not_a_dependency(self):
        pkg = deepcopy(fixture)
        value = {"actionRef": "action:absent", "basisRefs": [None, {"nested": 1}]}
        pkg["plan"]["state"]["deltas"][0]["after"]["value"] = value
        self.assertIsNotNone(self.fingerprint(pkg, target="delta:D-LAND"))

    def test_whole_plan_with_unreferenced_source(self):
        pkg = deepcopy(fixture)
        src = dict(pkg["plan"]["storyBasis"]["sources"][0], sourceId="source:unused")
        pkg["plan"]["storyBasis"]["sources"].append(src)
        self.assertIsNone(self.fingerprint(pkg, target="plan:P-FOX"))

    def test_incompatible_profile(self):
        spec = dict(gates["spec"], dependencyHashRule="war35-dep-jcs8785-sha256/1")
        self.assertIsNone(digest(fixture, spec))

    def test_safe_carry_and_scope_order(self):
        case = gates["make_case"]()
        self.assertTrue(gates["valid_case"](case, True))
        refs = ["fact:F-ONCE", "source:S-FOX"]
        for pkg, check, order in zip(case["packages"], case["checks"], [refs, refs[::-1]]):
            check["dependencyRefs"] = order
            check["dependencyFingerprintSha256"] = digest(pkg, check)
        prior = case["checks"][0]
        case["sealed"][prior["id"]] = gates["seal"](prior)
        case["inheritances"][0]["dependencyFingerprintSha256"] = prior["dependencyFingerprintSha256"]
        self.assertTrue(gates["valid_case"](case, True))

    def test_external_carry(self):
        for method in ("human", "geometry_proxy", "text"):
            for same_ref in (False, True):
                with self.subTest(method=method, same_ref=same_ref):
                    case = gates["make_case"]()
                    for pkg, check in zip(case["packages"], case["checks"]):
                        check.update(method=method, evidenceRefs=["observation:" + ("shared" if same_ref else check["id"])])
                        # A claimant can supply an old or otherwise plausible SHA.
                        check["dependencyFingerprintSha256"] = digest(pkg, check) or "0" * 64
                    prior = case["checks"][0]
                    case["inheritances"][0]["dependencyFingerprintSha256"] = prior["dependencyFingerprintSha256"]
                    case["sealed"][prior["id"]] = gates["seal"](prior)
                    self.assertFalse(gates["valid_case"](case, True))


if __name__ == "__main__":
    unittest.main(verbosity=2)

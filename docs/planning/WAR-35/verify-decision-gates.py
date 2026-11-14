#!/usr/bin/env python3
"""WAR-35 Blocking 3 — design-only semantic negative/positive tests, not production validator."""
import copy, hashlib, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,"/home/sean/.local/share/canvas-lab-jcs/venv/lib/python3.12/site-packages")
import rfc8785
schema=json.loads((ROOT/"director-plan.schema.review-rc3.json").read_text())
Draft202012Validator.check_schema(schema)
decl=Draft202012Validator(schema)
d_defs=schema["$defs"]
decision_schema=Draft202012Validator({"$defs":d_defs,"$ref":"#/$defs/decision"})
# Reuse the exact D-JCS research algorithm without rerunning its fixture-writing tests.
script=(ROOT/"verify-d-jcs1.py").read_text()
env={"__file__":str(ROOT/"verify-d-jcs1.py")}
exec(compile(script.split('fox=load("cross-shot-once.example.review-v0.json")')[0],str(ROOT/"verify-d-jcs1.py"),"exec"),env)
dep_sha=env["digest"]
fixture=json.loads((ROOT/"cross-shot-once.example.review-v0.json").read_text())
older=copy.deepcopy(fixture)
newer=copy.deepcopy(older)
newer["plan"]["revisionId"]="R3"
newer["plan"]["shots"].append(copy.deepcopy(newer["plan"]["shots"][-1]))
newer["plan"]["shots"][-1]["id"]="S-ADDED"
def sha(v): return hashlib.sha256(rfc8785.dumps(v)).hexdigest()
def plan_target(pkg):
    p=pkg["plan"]
    return {"planId":p["planId"],"revisionId":p["revisionId"],
            "planContentSha256":sha({"contractVersion":pkg["contractVersion"],"plan":p}),
            "hashRule":"war35-plan-jcs8785-sha256/1"}
t1,t2=plan_target(older),plan_target(newer)
spec={"targetRefs":["intent:I-CROSS"],"dependencyRefs":[],"collectionPaths":[],
      "checkSpec":"Intent A: narrative goal consistency", "checkSpecVersion":"intentA/2", "method":"text"}
def make_check(cid,pkg,sp):
    return {"id":cid,"target":plan_target(pkg),
            "targetRefs":sp["targetRefs"],"dependencyRefs":sp["dependencyRefs"],
            "collectionPaths":sp["collectionPaths"],
            "checkSpec":sp["checkSpec"],"checkSpecVersion":sp["checkSpecVersion"],
            "method":sp["method"],"dependencyHashRule":"war35-dep-jcs8785-sha256/4",
            "dependencyFingerprintSha256":dep_sha(pkg,sp),"result":"pass","applicability":"valid"}
c1,c2=make_check("C-A1",older,spec),make_check("C-A2",newer,spec)
b_spec=dict(spec,targetRefs=["shot:S-ADDED"],checkSpec="Shot B: output evidence criteria",checkSpecVersion="shotB/1")
cb=make_check("C-B",newer,b_spec)
old_d={"id":"D-A1","gate":"intentA","target":t1,"verdict":"approved",
       "checkIds":["C-A1"],"decisionBasis":"reviewed","rationale":"User approved A intent"}
new_d={"id":"D-A2","gate":"intentA","target":t2,"verdict":"approved",
       "checkIds":["C-A2"],"decisionBasis":"verified_carry_forward",
       "fromDecisionId":"D-A1","rationale":"Unchanged A intent"}
b_d={"id":"D-B2","gate":"shotB","target":t2,"verdict":"approved",
      "checkIds":["C-B"],"decisionBasis":"reviewed","rationale":"Shot B reviewed"}
inherit={"fromCheckId":"C-A1","intoCheckId":"C-A2","intoTarget":t2,
         "dependencyHashRule":"war35-dep-jcs8785-sha256/4",
         "dependencyFingerprintSha256":c1["dependencyFingerprintSha256"],
         "basis":"unchanged_dependencies"}
risk={"id":"R-1","riskVersionId":"V1","target":t2,"targetRefs":["shot:S-ADDED"],
      "kind":"unknown","description":"Lighting uncertain","status":"open"}
def seal(o): return sha(o)
def make_case():
    return {"packages":[copy.deepcopy(older),copy.deepcopy(newer)],
            "checks":[copy.deepcopy(c1),copy.deepcopy(c2),copy.deepcopy(cb)],
            "decisions":[copy.deepcopy(old_d),copy.deepcopy(new_d),copy.deepcopy(b_d)],
            "inheritances":[copy.deepcopy(inherit)],"risks":[copy.deepcopy(risk)],
            "sealed":{"C-A1":seal(c1),"D-A1":seal(old_d)},
            "sealedRisks":{("R-1","V1"):seal(risk)},
            "approvedPlan":{"decisionId":"D-B2","gate":"shotB","target":copy.deepcopy(t2)}}
def unique_by(items,field):
    vals=[i[field] for i in items]
    if len(vals)!=len(set(vals)): raise ValueError("duplicate record identity")
    return {i[field]:i for i in items}
def valid_case(case,check_current=False):
    try:
        decisions=unique_by(case["decisions"],"id")
        checks=unique_by(case["checks"],"id")
        risk_keys=[(r["id"],r["riskVersionId"]) for r in case["risks"]]
        if len(set(risk_keys))!=len(risk_keys): return False
        risks={k:v for k,v in zip(risk_keys,case["risks"])}
        gate_spec={("intentA/2","Intent A: narrative goal consistency"):"intentA",
                   ("shotB/1","Shot B: output evidence criteria"):"shotB"} # synthetic approved-spec fixture
        inheritances=unique_by(case["inheritances"],"intoCheckId")
        pkgs={json.dumps(plan_target(p),sort_keys=True):p for p in case["packages"]}
        if len(pkgs)!=len(case["packages"]): return False
        current=plan_target(case["packages"][-1])
        def archive_ok(obj):
            record=case["sealed"].get(obj["id"])
            return record is not None and record==seal(obj)
        def verified_check(c):
            if not Draft202012Validator({"$defs":d_defs,"$ref":"#/$defs/check"}).is_valid(c): return False
            if c["result"]!="pass" or c["applicability"]!="valid": return False
            pkg=pkgs.get(json.dumps(c["target"],sort_keys=True))
            if pkg is None: return False
            if c["method"]=="media": return False  # no media auto carry in v0 A
            fingerprint = dep_sha(pkg, c)
            return fingerprint is not None and fingerprint == c["dependencyFingerprintSha256"]
        def risk_valid(dec):
            pairs=dec.get("acceptedRisks",[])
            if len({p["riskId"] for p in pairs})!=len(pairs): return False  # one accepted version per risk identity
            for p in pairs:
                risk_obj=risks.get((p["riskId"],p["riskVersionId"]))
                if not risk_obj or risk_obj["riskVersionId"]!=p["riskVersionId"]: return False
                if case["sealedRisks"].get((p["riskId"],p["riskVersionId"]))!=seal(risk_obj): return False
                if risk_obj["target"]!=dec["target"]: return False
                if risk_obj["kind"]=="hard_conflict" and risk_obj["status"]=="open": return False
            return True
        def decide(identifier,seen):
            if identifier in seen: return False
            dec=decisions.get(identifier)
            if not dec or not decision_schema.is_valid(dec): return False
            if dec["target"] not in [plan_target(p) for p in case["packages"]]: return False
            if not risk_valid(dec): return False
            ids=dec["checkIds"]
            if len(ids)!=len(set(ids)) or not ids: return False
            if not all(cid in checks and checks[cid]["target"]==dec["target"] and verified_check(checks[cid]) and
                       gate_spec.get((checks[cid]["checkSpecVersion"],checks[cid]["checkSpec"]))==dec["gate"] for cid in ids): return False
            if dec["decisionBasis"]=="reviewed": return True
            src=decisions.get(dec.get("fromDecisionId"))
            if not src or not archive_ok(src) or not decide(src["id"],seen|{identifier}): return False
            if src["gate"]!="intentA" or dec["gate"]!="intentA": return False
            if src["verdict"]!="approved" or dec["verdict"]!="approved": return False
            if src.get("acceptedRisks") or dec.get("acceptedRisks"): return False
            if src["target"]["planId"]!=dec["target"]["planId"] or src["target"]==dec["target"]: return False
            prev_ids=set(src["checkIds"])
            if len(prev_ids)!=len(ids): return False
            predecessors=set()
            for cid in ids:
                item=inheritances.get(cid)
                if not item or item["intoTarget"]!=dec["target"]: return False
                prior=checks.get(item["fromCheckId"])
                current_c=checks[cid]
                if not prior or not archive_ok(prior) or not verified_check(prior): return False
                if prior["target"]!=src["target"] or current_c["target"]!=dec["target"]: return False
                if item["fromCheckId"] not in prev_ids: return False
                if item["dependencyHashRule"]!=prior["dependencyHashRule"] or item["dependencyHashRule"]!=current_c["dependencyHashRule"]: return False
                if item["dependencyFingerprintSha256"]!=prior["dependencyFingerprintSha256"] or item["dependencyFingerprintSha256"]!=current_c["dependencyFingerprintSha256"]: return False
                # Equal recomputed /4 fingerprints already compare normalized scopes and specs.
                predecessors.add(item["fromCheckId"])
            return predecessors==prev_ids
        if not decide("D-A2",set()): return False
        if check_current:
            ptr=case["approvedPlan"]
            dec=decisions.get(ptr["decisionId"])
            if not dec or ptr["gate"]!="shotB" or dec["gate"]!="shotB": return False
            if ptr["target"]!=current or dec["target"]!=ptr["target"]: return False
            if dec["verdict"] not in ("approved","conditionally_approved"): return False
            if dec["decisionBasis"]!="reviewed": return False  # shotB cannot be carried
            if not decide(dec["id"],set()): return False
        return True
    except (KeyError,ValueError,TypeError,AttributeError):
        return False
tests=[]
def test(name,mutator,expected):
    case=make_case(); mutator(case)
    got=valid_case(case,check_current=True)
    assert got==expected,(name,got,expected)
    tests.append({"case":name,"passed":True})
    print("PASS",name)
def mutate_dec(case,id,**values):
    next(d for d in case["decisions"] if d["id"]==id).update(values)
def reseal_source(case):
    case["sealed"]["D-A1"]=seal(case["decisions"][0])
def source_rejected(c):
    mutate_dec(c,"D-A1",verdict="rejected"); reseal_source(c)
def source_changed(c):
    mutate_dec(c,"D-A1",verdict="changes_requested"); reseal_source(c)
def source_conditional(c):
    mutate_dec(c,"D-A1",verdict="conditionally_approved"); reseal_source(c)
def source_risk(c):
    mutate_dec(c,"D-A1",acceptedRisks=[{"riskId":"R-1","riskVersionId":"V1"}]); reseal_source(c)
def target_mismatch(c):
    mutate_dec(c,"D-A2",target=t1)
def pointer_rejected(c):
    mutate_dec(c,"D-B2",verdict="rejected")
def pointer_wrong_target(c):
    c["approvedPlan"]["target"]=t1
def wrong_check_target(c):
    next(i for i in c["checks"] if i["id"]=="C-A2")["target"]=t1
def missing_risk(c):
    mutate_dec(c,"D-B2",verdict="conditionally_approved",acceptedRisks=[{"riskId":"R-NO","riskVersionId":"V1"}])
def wrong_risk_version(c):
    mutate_dec(c,"D-B2",verdict="conditionally_approved",acceptedRisks=[{"riskId":"R-1","riskVersionId":"V2"}])
def valid_risk(c):
    mutate_dec(c,"D-B2",verdict="conditionally_approved",acceptedRisks=[{"riskId":"R-1","riskVersionId":"V1"}])
def hard_risk(c):
    valid_risk(c); c["risks"][0]["kind"]="hard_conflict"
def risk_dropped(c):
    source_risk(c); c["decisions"][1].pop("acceptedRisks",None)
def carry_duplicate_checks(c):
    c["decisions"][1]["checkIds"]=["C-A2","C-A2"]
def new_check_hash_different(c):
    next(i for i in c["checks"] if i["id"]=="C-A2")["dependencyFingerprintSha256"]="e"*64
def source_unverifiable(c):
    c["sealed"].clear()
def old_check_changed(c):
    next(i for i in c["checks"] if i["id"]=="C-A1")["result"]="fail"
def source_check_fail_verified(c):
    old_check_changed(c); c["sealed"]["C-A1"]=seal(c["checks"][0])
def source_check_stale_verified(c):
    c["checks"][0]["applicability"]="stale"; c["sealed"]["C-A1"]=seal(c["checks"][0])
def newer_check_unknown(c):
    c["checks"][1]["result"]="unknown"
def same_revision_carry(c):
    c["decisions"][1]["target"]=t1
def conditional_without_risk(c):
    mutate_dec(c,"D-B2",verdict="conditionally_approved")
def conditional_without_rationale(c):
    valid_risk(c); c["decisions"][2].pop("rationale",None)
def mapping_missing(c):
    c["inheritances"].clear()
def approved_pointer_A(c):
    c["approvedPlan"]={"decisionId":"D-A2","gate":"shotB","target":t2}
def B_wrong_check(c):
    c["decisions"][2]["checkIds"]=["C-A1"]
def risks_modified(c):
    valid_risk(c); c["risks"][0]["target"]=t1
def risk_same_version_rewritten(c):
    valid_risk(c); c["risks"][0]["description"]="New unsealed risk text"
def reviewed_new_risk_version(c):
    next_risk=copy.deepcopy(c["risks"][0]);next_risk["riskVersionId"]="V2"
    next_risk["description"]="Newly reviewed lighting risk"
    c["risks"].append(next_risk); c["sealedRisks"][("R-1","V2")]=seal(next_risk)
    mutate_dec(c,"D-B2",verdict="conditionally_approved",acceptedRisks=[{"riskId":"R-1","riskVersionId":"V2"}])
def duplicate_risk_pair(c):
    valid_risk(c);c["risks"].append(copy.deepcopy(c["risks"][0]))
def two_accepted_versions_same_risk(c):
    reviewed_new_risk_version(c)
    c["decisions"][2]["acceptedRisks"].append({"riskId":"R-1","riskVersionId":"V1"})
def wrong_gate_check(c):
    c["decisions"][2]["checkIds"]=["C-A2"]
def upgrade(c):
    source_conditional(c); mutate_dec(c,"D-A2",verdict="approved")
def conditional_to_conditional(c):
    source_conditional(c); mutate_dec(c,"D-A2",verdict="conditionally_approved")
def reviewed_conditional(c):
    valid_risk(c)
def plan_digest_modified(c):
    c["approvedPlan"]["target"]={**t2,"planContentSha256":"f"*64}
test("D-P01-valid-A-carry-and-approved-B",lambda c:None,True)
test("D-P02-reviewed-conditional-B-with-risk",reviewed_conditional,True)
test("D-P03-reviewed-new-risk-version-explicit",reviewed_new_risk_version,True)
test("D-N01-rejected-to-approved",source_rejected,False)
test("D-N02-changes-requested-to-approved",source_changed,False)
test("D-N03-conditional-to-approved-upgrade",upgrade,False)
test("D-N04-conditional-to-conditional-not-automatic",conditional_to_conditional,False)
test("D-N05-accepted-risk-silently-dropped",risk_dropped,False)
test("D-N06-source-approved-but-risk-bearing",source_risk,False)
test("D-N07-approvedPlan-points-to-rejected-B",pointer_rejected,False)
test("D-N08-approvedPlan-points-to-A",approved_pointer_A,False)
test("D-N09-approvedPlan-target-mismatch",pointer_wrong_target,False)
test("D-N10-approvedPlan-falsified-content-hash",plan_digest_modified,False)
test("D-N11-new-check-uses-old-target",wrong_check_target,False)
test("D-N12-new-check-fingerprint-changed",new_check_hash_different,False)
test("D-N13-source-history-missing",source_unverifiable,False)
test("D-N14-source-check-mutated",old_check_changed,False)
test("D-N15-inheritance-record-missing",mapping_missing,False)
test("D-N16-duplicate-current-check-ids",carry_duplicate_checks,False)
test("D-N17-B-decision-check-wrong-target",B_wrong_check,False)
test("D-N18-B-unknown-risk",missing_risk,False)
test("D-N19-B-risk-version-substituted",wrong_risk_version,False)
test("D-N20-B-risk-target-different-revision",risks_modified,False)
test("D-N21-B-open-hard-conflict",hard_risk,False)
test("D-N22-risk-same-version-in-place-rewrite",risk_same_version_rewritten,False)
test("D-N23-duplicate-risk-version-pair",duplicate_risk_pair,False)
test("D-N24-B-gate-backed-by-A-only-check",wrong_gate_check,False)
test("D-N25-source-check-fail-even-if-sealed",source_check_fail_verified,False)
test("D-N26-source-check-stale-even-if-sealed",source_check_stale_verified,False)
test("D-N27-new-check-unknown",newer_check_unknown,False)
test("D-N28-same-revision-not-carry",same_revision_carry,False)
test("D-N29-conditional-without-explicit-risk",conditional_without_risk,False)
test("D-N30-conditional-without-rationale",conditional_without_rationale,False)
test("D-N31-two-accepted-versions-of-same-risk",two_accepted_versions_same_risk,False)
# Shape-only checks prove that semantic prohibitions cannot be delegated to JSON Schema.
shape=make_case()
assert decl.is_valid({"contractVersion":newer["contractVersion"],"plan":newer["plan"],
                      "sourceSnapshots":newer["sourceSnapshots"],"reviewLedger":{
                          "checks":shape["checks"],"decisions":shape["decisions"],
                          "risks":shape["risks"],"inheritances":shape["inheritances"]},
                      "revisionControl":{"approvedPlan":shape["approvedPlan"]}})
print("PASS original-full-package-shape")
tests.append({"case":"original-full-package-shape","passed":True})
# Crucial: schema itself rejects verified_carry_forward conditional verdict and carried risk.
bad=copy.deepcopy(new_d);bad["verdict"]="conditionally_approved"
assert not decision_schema.is_valid(bad)
tests.append({"case":"schema-no-conditional-carry","passed":True})
print("PASS schema-no-conditional-carry")
bad=copy.deepcopy(new_d);bad["acceptedRisks"]=[{"riskId":"R-1","riskVersionId":"V1"}]
assert not decision_schema.is_valid(bad)
tests.append({"case":"schema-no-risk-bearing-carry","passed":True})
print("PASS schema-no-risk-bearing-carry")
report={"task":"WAR-35","scope":"Blocking 3 Decision / approvedPlan design-only semantic test",
        "passed":len(tests),"total":len(tests),"cases":tests,
        "historyAssumption":"Immutable prior revisions/checks/decisions with independently verified SHA; cannot establish trust from unverified claims",
        "productionValidatorImplemented":False}
(ROOT/"decision-gates-rc3-verification.report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("TOTAL",len(tests),"PASS")

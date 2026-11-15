#!/usr/bin/env python3
"""Deterministic transport tests against actual approved WAR-90 B, no model calls."""
import copy
import json
import shutil
import sys
import unittest
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).parent))
import feedback_bridge as bridge
from feedback_bridge import Pilot, PilotError


class CanvasFeedbackBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_sha=bridge.sha_file(bridge.ORIGINAL/"state.json")
        cls.packet=bridge.approved_packet()
        cls.nodes=[]
        b=cls.packet["authority"]["approved_B_id"]
        for shot in cls.packet["shots"]:
            cls.nodes.append({"id":"mock-"+shot["id"],
                 "title":f"WAR-90｜{shot['id']} · B Review",
                 "metadata":{"content":f"{shot['id']} ｜ 已批准 B 文本展示\nB: {b}\n"}})
        cls.catalog=bridge.make_catalog(cls.packet,"private-test-project",cls.nodes)
    @classmethod
    def tearDownClass(cls):
        assert bridge.sha_file(bridge.ORIGINAL/"state.json")==cls.base_sha

    def make_feedback(self,target="Shot02",origin="synthetic-test"):
        selection={"nodes":[next(n for n in self.nodes if target in n["title"])]}
        return bridge.capture_feedback(self.packet,self.catalog,
            {"projectId":"private-test-project"},selection,
            "合成测试：检查镜头首次钥匙显露读得清楚吗？",origin)

    def test_good_catalog_and_feedback(self):
        f=self.make_feedback()
        bridge.validate_feedback(self.packet,f)
        self.assertEqual(f["target_shot_id"],"Shot02")
        self.assertFalse(f["human_B_decision"])
        self.assertFalse(f["actor_identity_verified"])
        self.assertTrue(f["requires_director_candidate_revision"])
        self.assertEqual(f["origin"],"synthetic-test")
        scope=bridge.stage_scope(self.packet,f)
        self.assertIn("Shot02",scope)
        self.assertIn("not a human B approval",scope)

    def test_catalog_rejects_stale_b_and_missing_shots(self):
        bad=copy.deepcopy(self.catalog)
        bad["approved_B_content_sha256"]="stale-B"
        with self.assertRaisesRegex(ValueError,"Stale Canvas"):bridge.check_catalog(self.packet,bad)
        bad=copy.deepcopy(self.catalog)
        bad["nodes"].pop()
        with self.assertRaises(ValueError):bridge.check_catalog(self.packet,bad)
        bad=copy.deepcopy(self.catalog)
        bad["nodes"][0]["shot_text_sha256"]="changed"
        with self.assertRaisesRegex(ValueError,"text changed"):bridge.check_catalog(self.packet,bad)

    def test_feedback_rejects_unbound_wrong_project_and_multi_selection(self):
        with self.assertRaisesRegex(ValueError,"project changed"):
            bridge.capture_feedback(self.packet,self.catalog,{"projectId":"wrong"},
                 {"nodes":[self.nodes[1]]},"wrong project")
        with self.assertRaisesRegex(ValueError,"exactly one"):
            bridge.capture_feedback(self.packet,self.catalog,{"projectId":"private-test-project"},
                 {"nodes":[self.nodes[1],self.nodes[2]]},"too many")
        with self.assertRaisesRegex(ValueError,"not a bound"):
            bridge.capture_feedback(self.packet,self.catalog,{"projectId":"private-test-project"},
                 {"nodes":[{"id":"spoof-id","title":self.nodes[1]["title"]}]},"spoof")
        stale=copy.deepcopy(self.nodes[1]);stale["metadata"]["content"]="Shot02 changed by UI"
        with self.assertRaisesRegex(ValueError,"display changed"):
            bridge.capture_feedback(self.packet,self.catalog,{"projectId":"private-test-project"},
                 {"nodes":[stale]},"stale selected display")
        with self.assertRaisesRegex(ValueError,"Empty"):
            bridge.capture_feedback(self.packet,self.catalog,{"projectId":"private-test-project"},
                 {"nodes":[self.nodes[1]]}," ")
        with self.assertRaisesRegex(ValueError,"provenance"):
            bridge.capture_feedback(self.packet,self.catalog,{"projectId":"private-test-project"},
                 {"nodes":[self.nodes[1]]},"danger",origin="verified-human")

    def test_tamper_rejected_and_no_approval_impersonation(self):
        f=self.make_feedback()
        for key,val in (("base_B_id","other"),("base_B_content_sha256","other"),
                        ("source_sha256","other"),("target_shot_sha256","other"),
                        ("instruction","silently altered"),("human_B_decision",True)):
            changed=copy.deepcopy(f);changed[key]=val
            with self.assertRaises(ValueError):bridge.validate_feedback(self.packet,changed)

    def test_fake_candidate_is_unapproved_and_non_target_is_byte_stable(self):
        f=self.make_feedback()
        destination=bridge.PILOT_ROOT/("pilot-D-canvas-feedback-unit-"+uuid4().hex[:12])
        try:
            result=bridge.clone_for_revision(self.packet,f,destination)
            self.assertEqual(result["original_state_sha256"],self.base_sha)
            self.assertFalse(result["fresh_model_call_performed"])
            report=bridge.fake_director_for_transport_only(self.packet,f,destination)
            state=Pilot(destination).load()
            self.assertEqual(report["generator_provenance"],
                             "synthetic-fake-NOT-a-real-Director-run")
            self.assertEqual(report["changed_shots"],["Shot02"])
            self.assertEqual(state["phase"],"awaiting-human-B")
            self.assertIsNone(state["pilot_B"])
            self.assertFalse(report["pilot_B_approved"])
            self.assertFalse(report["formal_WAR35_approval"])
            self.assertIn("Shot03",report["pending_review_shots"])
            self.assertIn("Shot01",report["pending_review_shots"])
            self.assertIn("SYNTHETIC-NO-CODEX-SESSION",
                         state["thread_id"])
            self.assertEqual(bridge.sha_file(bridge.ORIGINAL/"state.json"),self.base_sha)
        finally:
            if destination.exists():shutil.rmtree(destination)

    def test_non_target_forgery_is_quarantined(self):
        f=self.make_feedback()
        destination=bridge.PILOT_ROOT/("pilot-D-canvas-feedback-unit-"+uuid4().hex[:12])
        try:
            bridge.clone_for_revision(self.packet,f,destination)
            pilot=Pilot(destination)
            state=pilot.load()
            art=state["active"]["artifacts"]["shot"]
            altered=art["proposal"].replace("Shot01｜","Shot01｜SIMULATED HIDDEN CHANGE ",1)
            result={"proposal":altered,"reason":"fake","changes":"fake",
                    "impact":"fake","unknown":["media"],"next_action":"fake",
                    "handoff":True,"changed_targets":["Shot02"],"shot_ids":art["shot_ids"],
                    "hard_conflicts":[],"upstream_change":False}
            def fake(_prompt,_path):return json.dumps(result,ensure_ascii=False),"fake"
            with self.assertRaisesRegex(PilotError,"Non-target"):
                pilot.run("shot",targets=["Shot02"],generator=fake)
            self.assertEqual(pilot.load()["phase"],"pilot-B-accepted")
            self.assertEqual(pilot.load()["active"],state["active"])
        finally:
            if destination.exists():shutil.rmtree(destination)


if __name__=="__main__":
    unittest.main()

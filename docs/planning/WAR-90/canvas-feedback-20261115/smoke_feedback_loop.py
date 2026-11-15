#!/usr/bin/env python3
"""Actual Canvas Agent transport + synthetic Director candidate round-trip.

No real user feedback, no Director model, no new approval. Isolated test browser.
"""
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

HERE=Path(__file__).resolve().parent
PILOT_ROOT=HERE.parent
sys.path.insert(0,str(PILOT_ROOT/"canvas-agent-smoke-20261115"))
from smoke_canvas_agent import BrowserCDP
import feedback_bridge as bridge

def require(ok, label):
    if not ok:raise RuntimeError(label)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    config=json.loads((Path.home()/".infinite-canvas/canvas-agent.json").read_text())
    agent=config["url"].rstrip("/")
    token=config["token"]
    ses=requests.Session()
    ses.headers.update({"x-canvas-agent-token":token})
    health=ses.get(agent+"/health",timeout=8).json()
    require(health.get("ok") and health.get("clients")==0 and not health.get("hasCanvas"),
            "Refuse to run with existing Canvas attached")
    packet=bridge.approved_packet()
    before=sha(bridge.ORIGINAL/"state.json")
    require(packet["authority"]["approved_B_id"]=="b7b4fd156b884907b2431b6b1e0d9960",
            "Unexpected approved B")
    dest=PILOT_ROOT/"pilot-D-canvas-feedback-demo-20261115"
    require(not dest.exists(),"Do not overwrite experimental candidate")
    with tempfile.TemporaryDirectory(prefix="war90-feedback-browser-") as temp:
        browser=BrowserCDP(temp)
        try:
            browser.launch()
            url="http://127.0.0.1:3000/canvas?mode=new#"+urlencode({
                "agentUrl":agent,"agentToken":token})
            browser.send("Page.navigate",{"url":url})
            for _ in range(160):
                time.sleep(.25)
                h=ses.get(agent+"/health",timeout=6).json()
                if h.get("hasCanvas") and h.get("clients")==1:break
            require(h.get("hasCanvas") and h.get("clients")==1,
                    "Private browser cannot reach Canvas Agent")
            def call(name,data):
                rsp=ses.post(agent+"/api/tools",json={"name":name,"input":data},timeout=35)
                rsp.raise_for_status()
                obj=rsp.json()
                require(obj.get("ok")==True,f"Canvas tool {name} failed")
                return obj["result"]
            first={}
            for _ in range(90):
                first=call("canvas_get_state",{})
                if first.get("projectId"):break
                time.sleep(.25)
            project_id=first.get("projectId")
            require(project_id and len(first.get("nodes",[]))==0,
                    "Canvas not safely empty")
            a=packet["authority"]
            header=("WAR-90 | Director B 审阅测试\n"
                    "从真实已批准 B 只读导出，但本轮修订是自动化模拟，不是导演专业判断。\n"
                    f"B id: {a['approved_B_id']}\n"
                    f"B SHA256: {a['approved_B_content_sha256']}\n"
                    f"Source SHA256: {a['source_sha256']}\n"
                    "媒体、几何、观众效果均未实测。")
            items=[{"title":"WAR-90｜Director B Test Only", "text":header,
                    "x":0,"y":0,"width":500,"height":470}]
            for i,shot in enumerate(packet["shots"]):
                content=(f"{shot['id']} ｜ 已批准 B 文本展示\n"
                         f"B: {a['approved_B_id']}\n"
                         f"Shot SHA256: {shot['text_sha256']}\n"
                         f"Source SHA256: {a['source_sha256']}\n"
                         "仅用于文字审阅；不是生成指令。\n\n"+shot["text"])
                items.append({"title":f"WAR-90｜{shot['id']} · B Review",
                              "text":content,
                              "x":560+i*560,"y":0,"width":530,"height":570})
            call("canvas_create_text_nodes",{"items":items,"direction":"row"})
            state=call("canvas_get_state",{})
            require(state.get("projectId")==project_id and len(state.get("nodes",[]))==5,
                    "Did not create all approval preview nodes")
            catalog=bridge.make_catalog(packet,project_id,state["nodes"])
            shot02=next(n for n in catalog["nodes"] if n["shot_id"]=="Shot02")
            call("canvas_select_nodes",{"ids":[shot02["id"]]})
            selected=call("canvas_get_selection",{})
            require([x.get("id") for x in selected.get("nodes",[])]==[shot02["id"]],
                    "Selection not routed to Shot02")

            # A deliberately synthetic request, NEVER recorded as human feedback.
            text=("【合成流程测试】测试仅用于验证 Canvas 选镜、修订候选、"
                  "邻镜复检与差异回显，不是用户提出的专业修改要求。")
            feedback=bridge.capture_feedback(packet,catalog,
                  call("canvas_get_state",{}),selected,text,origin="synthetic-test")
            bridge.validate_feedback(packet,feedback)
            prepared=bridge.clone_for_revision(packet,feedback,dest)
            diff=bridge.fake_director_for_transport_only(packet,feedback,dest)

            # Show a truthful diff: synthetic only, not model or user approval.
            feedback_body=("WAR-90｜Shot02 模拟反馈\n"
                           f"Canvas Project: {project_id}\n"
                           f"Bound node: {feedback['canvas_node_id']}\n"
                           f"Base B: {feedback['base_B_id']}\n"
                           "来源: synthetic-test；actor_identity_verified=false\n"
                           "此反馈尚未由用户提交。\n"
                           f"Request: {feedback['instruction']}\n")
            diff_body=("WAR-90｜Shot02 测试差异（不是专业导演输出）\n"
                       f"Base B: {diff['base_B_id']}\n"
                       f"Candidate: {diff['candidate_id']}\n"
                       "Status: awaiting-human-B; NOT APPROVED\n"
                       "Generator: fake (no new model call)\n"
                       f"Changed: {', '.join(diff['changed_shots'])}\n"
                       f"Neighbors pending: {', '.join(diff['pending_review_shots'])}\n"
                       "几何/媒体/观众均未验证。\n\n"
                       +diff["diff"])
            call("canvas_create_text_nodes",{"items":[
                {"title":"WAR-90｜Shot02 Synthetic Feedback", "text":feedback_body,
                 "x":550,"y":670,"width":530,"height":390},
                {"title":"WAR-90｜Shot02 Synthetic Diff · NOT APPROVED", "text":diff_body,
                 "x":1120,"y":670,"width":700,"height":550}
            ],"direction":"row"})
            after=call("canvas_get_state",{})
            require(after.get("projectId")==project_id and len(after.get("nodes",[]))==7,
                    "Diff not displayed in private Canvas")
            title_set={x.get("title") for x in after["nodes"]}
            require("WAR-90｜Shot02 Synthetic Diff · NOT APPROVED" in title_set,
                    "No diff display node")
            require(bridge.sha_file(bridge.ORIGINAL/"state.json")==before,
                    "Approved B state changed")

            (HERE/"catalog.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n")
            (HERE/"synthetic-feedback.json").write_text(
                json.dumps(feedback,ensure_ascii=False,indent=2)+"\n")
            (HERE/"prepared-workspace.json").write_text(
                json.dumps({k:v for k,v in prepared.items() if k!="scope"},
                           ensure_ascii=False,indent=2)+"\n")
            (HERE/"synthetic-diff.json").write_text(json.dumps(diff,ensure_ascii=False,indent=2)+"\n")
            record={
                "run_mode":"real Canvas Agent API + isolated browser + fake Director transport",
                "project_id":project_id,
                "approved_B_id":a["approved_B_id"],
                "approved_B_content_sha256":a["approved_B_content_sha256"],
                "approved_state_before_and_after_sha256":before,
                "selected_shot":"Shot02",
                "real_canvas_selection_verified":True,
                "read_back_nodes":len(after["nodes"]),
                "catalog_node_count":len(catalog["nodes"]),
                "synthetic_feedback_origin":feedback["origin"],
                "synthetic_feedback_id_verification":False,
                "new_candidate_id":diff["candidate_id"],
                "candidate_generator_provenance":diff["generator_provenance"],
                "candidate_approval":False,
                "candidate_pending_shots":diff["pending_review_shots"],
                "changed_shots":diff["changed_shots"],
                "no_real_user_feedback":True,
                "no_new_director_model_call":True,
                "no_media_generated":True,
                "user_production_canvas_touched":False,
                "private_browser_cleanup":True,
                "not_full_loop":True
            }
            (HERE/"loop-demo-result.json").write_text(
                 json.dumps(record,ensure_ascii=False,indent=2)+"\n")
            print("CANVAS_TRANSPORT_ROUNDTRIP_PASS","nodes",len(after["nodes"]),
                  "selected",feedback["target_shot_id"],
                  "changed",diff["changed_shots"],
                  "pending",diff["pending_review_shots"])
            print("REAL_USER_FEEDBACK",False,"MODEL",False,"B_APPROVAL",False)
        finally:
            browser.close()
    h=ses.get(agent+"/health",timeout=8).json()
    require(h.get("clients")==0 and not h.get("hasCanvas"),
            "Private Chromium browser cleanup incomplete")
    print("CHROME_CLEANED; AGENT_CLIENTS=0")
if __name__=="__main__":main()

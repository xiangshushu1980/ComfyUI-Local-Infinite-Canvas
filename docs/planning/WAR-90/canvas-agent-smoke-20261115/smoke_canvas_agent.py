#!/usr/bin/env python3
"""WAR-90 isolated Canvas Agent smoke: no model, media, user canvas or production writes."""
import hashlib, json, os, subprocess, tempfile, time
from pathlib import Path
from urllib.parse import urlencode

import requests
import websocket

ROOT = Path("/home/sean/projects/canvas-lab")
HERE = Path(__file__).resolve().parent
WORKSPACE = ROOT / "docs/planning/WAR-90/pilot-D-local-repair-v2"
CLI = ROOT / "tools/director-runtime-v0/cli.py"
CHROME = Path.home() / ".cache/puppeteer/chrome/linux-156.0.8078.47/chrome-linux64/chrome"
AGENT_CONFIG = Path.home() / ".infinite-canvas/canvas-agent.json"

def assert_true(condition, message):
    if not condition: raise RuntimeError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def validated_feedback(packet, request):
    """Pure input validation, not submission or user acceptance."""
    a = packet["authority"]
    if not (request.get("approved_B_id") == a["approved_B_id"]
            and request.get("approved_B_content_sha256") == a["approved_B_content_sha256"]
            and request.get("source_sha256") == a["source_sha256"]):
        raise ValueError("Stale or mismatched Director authority")
    shots={s["id"] for s in packet["shots"]}
    if request.get("target_shot_id") not in shots:
        raise ValueError("Missing Shot target")
    if not isinstance(request.get("instruction"),str) or not request["instruction"].strip():
        raise ValueError("Empty feedback")
    return {"feedback_status":"unsubmitted_example_only",
            "target_shot_id":request["target_shot_id"],
            "baseline_B_id":a["approved_B_id"],
            "baseline_B_content_sha256":a["approved_B_content_sha256"],
            "source_sha256":a["source_sha256"],
            "requires_director_candidate_revision":True,
            "new_B_user_approval":False}

class BrowserCDP:
    def __init__(self, profile):
        self.profile=Path(profile)
        self.proc=None
        self.ws=None
        self.port=None
        self.msgid=0
    def launch(self):
        command=[str(CHROME),"--headless=new","--no-sandbox","--disable-gpu",
                 "--disable-dev-shm-usage","--no-first-run","--no-default-browser-check",
                 "--window-size=1700,1000","--remote-debugging-port=0", "--remote-allow-origins=http://localhost",
                 f"--user-data-dir={self.profile}","about:blank"]
        self.proc=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,start_new_session=True)
        dev=self.profile/"DevToolsActivePort"
        for _ in range(100):
            if dev.exists():break
            if self.proc.poll() is not None:raise RuntimeError("Headless Chromium exited")
            time.sleep(.1)
        assert_true(dev.exists(),"No DevToolsActivePort")
        self.port=int(dev.read_text().splitlines()[0])
        for _ in range(20):
            entries=requests.get(f"http://127.0.0.1:{self.port}/json",timeout=2).json()
            pages=[x for x in entries if x.get("type")=="page"]
            if pages:break
            time.sleep(.1)
        assert_true(bool(pages),"No headless page")
        self.ws=websocket.create_connection(pages[0]["webSocketDebuggerUrl"],
                                            origin="http://localhost",timeout=30)
        self.send("Page.enable")
        self.send("Runtime.enable")
    def send(self,method,params=None):
        self.msgid+=1;id=self.msgid
        self.ws.send(json.dumps({"id":id,"method":method,"params":params or {}}))
        while True:
            x=json.loads(self.ws.recv())
            if x.get("id")==id:
                if x.get("error"):raise RuntimeError(f"CDP {method} error: {x['error'].get('message','')}")
                return x.get("result",{})
    def evaluate(self,expr):
        return self.send("Runtime.evaluate",
                         {"expression":expr,"returnByValue":True,"awaitPromise":True}).get("result",{}).get("value")
    def close(self):
        if self.ws:self.ws.close()
        if self.proc:
            self.proc.terminate()
            try:self.proc.wait(timeout=8)
            except subprocess.TimeoutExpired:self.proc.kill()

def main():
    assert_true(CHROME.is_file(),"Missing isolated Chromium")
    assert_true(AGENT_CONFIG.is_file(),"Missing protected Agent config")
    config=json.loads(AGENT_CONFIG.read_text())
    url=config["url"].rstrip("/")
    token=config["token"]
    assert_true(bool(token),"Agent token absent")
    session=requests.Session()
    session.headers.update({"x-canvas-agent-token":token})
    before=session.get(url+"/health",timeout=8).json()
    assert_true(before.get("ok") is True and before.get("clients")==0
                and before.get("hasCanvas") is False,
                "A Canvas browser is already attached; refuse ambiguous writes")
    cmd=["python3",str(CLI),"review-pack","--workspace",str(WORKSPACE)]
    model=subprocess.run(cmd,text=True,capture_output=True,check=True)
    packet=json.loads(model.stdout)
    assert_true(packet["capabilities"]=={"display_text":True,"propose_edit":False,
                "write_canvas":False,"generate_media":False,"production_approval":False},
                "Preview capabilities changed")
    a=packet["authority"]
    assert_true(a["approved_B_id"]=="b7b4fd156b884907b2431b6b1e0d9960",
                "Unexpected approved B")

    example={"approved_B_id":a["approved_B_id"],
             "approved_B_content_sha256":a["approved_B_content_sha256"],
             "source_sha256":a["source_sha256"],
             "target_shot_id":"Shot02",
             "instruction":"自动化反例样例（非真实用户）：请复核 Shot02 钥匙首次显露是否容易辨认。"}
    valid=validated_feedback(packet,example)
    for changed in (dict(example,approved_B_id="stale-B"),
                    dict(example,approved_B_content_sha256="stale-hash"),
                    dict(example,target_shot_id="Shot99"),
                    dict(example,instruction="")):
        try:validated_feedback(packet,changed)
        except ValueError:pass
        else:raise RuntimeError("Invalid feedback unexpectedly accepted")

    # All live browser state is private to this fresh temporary profile.
    with tempfile.TemporaryDirectory(prefix="war90-private-chrome-") as temp:
        browser=BrowserCDP(temp)
        try:
            browser.launch()
            # Token is sent only via authenticated local browser DevTools, NOT process args.
            page="http://127.0.0.1:3000/canvas?mode=new#"+urlencode({
                "agentUrl":url,"agentToken":token})
            browser.send("Page.navigate",{"url":page})
            health={}
            for _ in range(160):
                time.sleep(.25)
                health=session.get(url+"/health",timeout=6).json()
                if health.get("hasCanvas") and health.get("clients")==1:break
            assert_true(health.get("hasCanvas") and health.get("clients")==1,
                        "Private browser did not connect Canvas Agent")
            def call(name,data):
                res=session.post(url+"/api/tools",json={"name":name,"input":data},
                                 timeout=40)
                res.raise_for_status()
                response=res.json()
                assert_true(response.get("ok") is True,f"{name} returned error")
                return response["result"]
            initial={}
            for _ in range(90):
                initial=call("canvas_get_state",{})
                if initial.get("projectId"):break
                time.sleep(.25)
            assert_true(initial.get("projectId"),
                        f"No project ID; state keys={list(initial)}; browser path={browser.evaluate('location.pathname')}")
            assert_true(len(initial.get("nodes",[]))==0,
                        "Private canvas should be fresh/empty")
            project_id=initial["projectId"]
            header=(f"WAR-90｜Director B 试点 · 只读审阅演示\n"
                    f"当前试点 B：{a['approved_B_id']}\n"
                    f"B 内容 SHA256：{a['approved_B_content_sha256']}\n"
                    f"Source SHA256：{a['source_sha256']}\n"
                    f"审阅：A/B 试点已由外部真实用户批准；正式 WAR-35 未批准\n"
                    f"未证：geometry / media / audience\n"
                    f"本次为临时私有测试画布，禁止生成媒体或覆盖生产数据。")
            items=[{"title":"WAR-90｜试点 B 只读说明","text":header,
                    "x":0,"y":0,"width":500,"height":420}]
            for i,shot in enumerate(packet["shots"]):
                content=(f"{shot['id']} ｜ 已批准 B 文本展示\n"
                         f"B: {a['approved_B_id']}\n"
                         f"Shot SHA256: {shot['text_sha256']}\n"
                         f"Source SHA256: {a['source_sha256']}\n"
                         f"未证：几何/媒体/观众；非生成指令\n\n"+shot["text"])
                items.append({"title":f"WAR-90｜{shot['id']} · B Review",
                              "text":content,"x":550+i*550,"y":0,
                              "width":520,"height":590})
            created=call("canvas_create_text_nodes",{"items":items,"direction":"row"})
            after=call("canvas_get_state",{})
            assert_true(after.get("projectId")==project_id,"Canvas project switched")
            nodes=after.get("nodes",[])
            assert_true(len(nodes)==5,"Expected five review text nodes")
            titles={n.get("title") for n in nodes}
            assert_true(titles=={x["title"] for x in items},"Missing Shot nodes")
            for node,item in zip(sorted(nodes,key=lambda x:x["position"]["x"]),
                                 sorted(items,key=lambda x:x["x"])):
                preview=node.get("metadata",{}).get("content","")
                assert_true(item["text"][:100]==preview[:100],
                            f"Node preview does not match {item['title']}")
            # Real Canvas selection plumbing, independent of a model. This is NOT
            # the real user's feedback and does not launch a Director run.
            selected_node=next(n for n in nodes if "Shot02" in (n.get("title") or ""))
            call("canvas_select_nodes",{"ids":[selected_node["id"]]})
            selection=call("canvas_get_selection",{})
            selected=selection.get("nodes",[])
            assert_true(len(selected)==1 and selected[0]["id"]==selected_node["id"],
                        "Selected Shot02 did not come back via Canvas Agent")
            assert_true("Shot02" in selected[0].get("title",""),
                        "Selected node lacks Shot02 identity")
            assert_true(valid["target_shot_id"]=="Shot02", "Feedback was routed to wrong Shot")
            visible=browser.evaluate("document.body.innerText.slice(0,1800)") or ""
            # Browser UI has a real project route; text nodes live in its frontend store.
            current_url=browser.evaluate("location.pathname") or ""
            assert_true(current_url.endswith("/"+project_id),"Browser is not in new test project")
            results={
                "mode":"real Canvas Agent API + isolated headless Chrome frontend; no model or media",
                "real_canvas_agent_calls":["canvas_get_state","canvas_create_text_nodes",
                                           "canvas_get_state","canvas_select_nodes",
                                           "canvas_get_selection"],
                "selected_target":"Shot02",
                "selected_node_binding_verified":True,
                "private_project_id":project_id,
                "node_count":len(nodes),
                "node_titles":sorted(titles),
                "approved_B_id":a["approved_B_id"],
                "approved_B_content_sha256":a["approved_B_content_sha256"],
                "source_sha256":a["source_sha256"],
                "test_profile_deleted_on_exit":True,
                "user_real_canvas_touched":False,
                "feedback_test":{"accepted_synthetic_example":valid,
                                 "rejected_invalid_examples":4,
                                 "real_user_feedback_received":False,
                                 "model_candidate_created":False},
                "agent_page_connected":True,
                "browser_project_route_verified":True,
                "browser_ui_contains_review_title":"WAR-90" in visible,
                "limitations":["Canvas canvas_get_state intentionally truncates node content previews",
                               "No real user edits or actual Director return-call",
                               "No WAR-35 integration, identity verification, video generation or real audience check"]
            }
            (HERE/"canvas-agent-smoke-result.json").write_text(
                json.dumps(results,ensure_ascii=False,indent=2)+"\n")
            print("CANVAS_SMOKE_SUCCESS",len(nodes),"NODES; PROJ_CREATED; FEEDBACK_GUARDS=4")
            print("UI_HAS_REVIEW_TITLE",results["browser_ui_contains_review_title"])
            print("RESULT_SHA256",digest((HERE/"canvas-agent-smoke-result.json").read_bytes()))
        finally:
            browser.close()
    final=session.get(url+"/health",timeout=8).json()
    # Browser has been shut down; async SSE teardown can take a moment.
    print("PRIVATE_CHROME_CLOSED",True,"LIVE_CLIENTS_AFTER",final.get("clients"))

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""WAR-90 native Canvas Agent integration smoke. Isolated HTTP Agent, web, browser.
Only the private canvas receives test nodes; approved B and production are read only.
"""
import hashlib,json,os,secrets,shutil,subprocess,sys,tempfile,time,traceback,threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,urlencode
import requests

ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/native-compact-integration-20261116'
SKILL=ROOT/'docs/planning/WAR-89/director-skill-v0-candidate'
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
WEB=ROOT/'infinite-canvas/web/dist'
sys.path.insert(0,str(ROOT/'docs/planning/WAR-90/single-agent-live-20261115'))
from hold_canvas import BrowserCDP
AGENT_PORT=17471
WEB_PORT=17472
AGENT_URL=f'http://127.0.0.1:{AGENT_PORT}'
WEB_URL=f'http://127.0.0.1:{WEB_PORT}'
BASE_SHA='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
def h(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise RuntimeError(message)
def saved(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kw):
        super().__init__(*args,directory=str(WEB),**kw)
    def do_GET(self):
        if urlparse(self.path).path in ('/canvas','/canvas/'):
            self.path='/index.html'
        return super().do_GET()
    def log_message(self,*args):pass
def tool(s,name,input):
    r=s.post(AGENT_URL+'/api/tools',json={'name':name,'input':input},timeout=50)
    need(r.ok and r.json().get('ok') is True, 'Private tool call failed: '+name)
    return r.json()['result']
def manifest(root):
    return {str(p.relative_to(root)):h(p) for p in sorted(root.rglob('*')) if p.is_file()}
def redact_history(doc,token):
    body=json.dumps(doc,ensure_ascii=False)
    need(token not in body,'Native thread history includes private token; refusing raw save')
    return doc
def main():
    before=h(B)
    need(before==BASE_SHA,'Approved B changed before isolated smoke')
    import sys
    sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
    from runtime import Pilot
    data=Pilot(B.parent).review_shot('Shot02')
    need(data['target_shot']['id']=='Shot02','Unexpected target')
    source_manifest=manifest(SKILL)
    need(len(source_manifest)==7,'Source Skill no longer 7 files')
    result={'phase':'isolated-native-compact-shot-readonly','baseline_sha256':before,
            'source_skill_sha256':source_manifest,
            'native_http_agent':False,'native_thread':False,
            'native_turn':False,'native_cli_execution_proven':False,
            'native_canvas_mcp_read_proven':False,
            'production_untouched':False,'production_services_started':False,
            'model_execution_mode':'isolated native Codex, existing authorized CODEX_HOME; no credentials copied',
            'not_approval_test':True}
    temp=tempfile.mkdtemp(prefix='war90-native-compact-')
    root=Path(temp)
    proc=None;log=None;browser=None;webserver=None
    started=time.monotonic()
    try:
        webserver=ThreadingHTTPServer(('127.0.0.1',WEB_PORT),AppHandler)
        threading.Thread(target=webserver.serve_forever,daemon=True).start()
        need(requests.get(WEB_URL+'/canvas?mode=new',timeout=5).status_code==200,'Private web SPA missing')
        home=root/'home';home.mkdir()
        workspace=home/'.infinite-canvas/codex-workspaces/site'
        target=workspace/'.agents/skills/director-skill-v0-candidate'
        target.parent.mkdir(parents=True)
        shutil.copytree(SKILL,target)
        need(manifest(target)==source_manifest,'Skill copy SHA mismatch')
        token=secrets.token_hex(20)
        settings={'url':AGENT_URL,'token':token,
                  'mcpOverrides':{k:False for k in ('hindsight','codegraph','hindsight-direct','blender','cua_repl')},
                  'workspace':{'workspacePath':str(workspace)}}
        conf=home/'.infinite-canvas/canvas-agent.json'
        conf.write_text(json.dumps(settings))
        conf.chmod(0o600)
        env=dict(os.environ,HOME=str(home),PORT=str(AGENT_PORT),CODEX_HOME='/home/sean/.codex')
        log=(root/'agent.log').open('wb')
        proc=subprocess.Popen(['node',str(ROOT/'infinite-canvas/canvas-agent/dist/index.js')],
                 cwd=str(ROOT/'infinite-canvas/canvas-agent'),env=env,
                 stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        session=requests.Session()
        for _ in range(100):
            need(proc.poll() is None,'isolated Canvas Agent exited')
            try:
                if session.get(AGENT_URL+'/health',timeout=1).ok:break
            except requests.RequestException:pass
            time.sleep(.18)
        else:raise RuntimeError('Isolated Canvas Agent did not start')
        result['native_http_agent']=True
        session.headers['x-canvas-agent-token']=token
        skill_list=session.get(AGENT_URL+'/agent/codex/skills?forceReload=1',timeout=60).json()
        candidates=[x for x in skill_list.get('data',[]) if x.get('name')=='director-skill-v0-candidate']
        need(len(candidates)==1 and candidates[0]['enabled'],'Native Skill not enabled/discovered')
        need(candidates[0]['path']==str(target/'SKILL.md'),'Not isolated Skill')
        result['skill_discovered_by_http']=True
        result['skill_errors_count']=len(skill_list.get('errors',[]))
        mcp=session.get(AGENT_URL+'/agent/codex/mcp',timeout=35).json()
        result['mcp_config_summary']=[{'name':x['name'],'effective_enabled':x.get('enabled'),
                                       'overridden':x.get('overridden')} for x in mcp.get('data',[])]
        result['undesired_effective_mcp_enabled']=[x['name'] for x in result['mcp_config_summary']
                         if x['name'] in ('hindsight','codegraph','hindsight-direct','blender','cua_repl') and x['effective_enabled']]
        need(not result['undesired_effective_mcp_enabled'],'Nonessential MCP still enabled via HTTP config')
        browser=BrowserCDP(root/'chrome')
        browser.launch()
        browser.send('Page.navigate',{'url':WEB_URL+'/canvas?mode=new#'+urlencode(
                     {'agentUrl':AGENT_URL,'agentToken':token})})
        info={}
        for _ in range(130):
            time.sleep(.25)
            info=session.get(AGENT_URL+'/health',timeout=5).json()
            if info.get('hasCanvas') and info.get('clients')==1:break
        need(info.get('hasCanvas') and info.get('clients')==1,'Private Canvas browser did not attach')
        for _ in range(65):
            state=tool(session,'canvas_get_state',{})
            if state.get('projectId'):break
            time.sleep(.2)
        need(state.get('projectId') and not state.get('nodes'), 'Private test Canvas not fresh')
        result['private_project_id_verified']=True
        items=[{'title':'WAR-90 Pilot B / test only','text':'No real user edits. B='+data['authority']['approved_B_id'],'x':0,'y':0,'width':400,'height':240}]
        full=Pilot(B.parent).review_packet()
        for i,shot in enumerate(full['shots']):
            items.append({'title':'WAR-90 '+shot['id']+' approved pilot B',
             'text':'B: '+data['authority']['approved_B_id']+'\nSHA256: '+shot['text_sha256']+'\n\n'+shot['text'],
             'x':420+i*540,'y':0,'width':510,'height':560})
        tool(session,'canvas_create_text_nodes',{'items':items,'direction':'row'})
        after_create=tool(session,'canvas_get_state',{})
        need(after_create.get('projectId')==state['projectId'] and len(after_create.get('nodes',[]))==5,
             'Private Canvas nodes not created')
        shot02=next(x for x in after_create['nodes'] if 'Shot02' in x.get('title',''))
        tool(session,'canvas_select_nodes',{'ids':[shot02['id']]})
        selected=tool(session,'canvas_get_selection',{}).get('nodes') or []
        need(len(selected)==1 and selected[0]['id']==shot02['id'],'Selected Shot02 not active')
        client_id=browser.evaluate('sessionStorage.getItem("canvas-agent-client-id")')
        need(client_id,'Private client ID absent')
        result['test_canvas_nodes_before_model']=5
        result['test_canvas_selected']='Shot02'
        # The current Web UI may auto-create a draft Codex thread on connection.
        # Reuse it after preheat; do not race /threads/new against the UI.
        conversation={}
        for _ in range(240):
            snap=session.get(AGENT_URL+'/agent/codex/workspace',timeout=15).json()
            conversation=snap.get('conversation') or {}
            if conversation.get('status') in ('ready','warning') and conversation.get('threadId'):
                break
            if conversation.get('status')=='failed':
                raise RuntimeError('Web-prepared native Codex thread failed')
            time.sleep(.5)
        thread_id=conversation.get('threadId')
        if not thread_id:
            reply=session.post(AGENT_URL+'/agent/codex/threads/new',
                 json={'clientId':client_id,'permissionMode':'automatic'},timeout=150)
            if not reply.ok:
                error=reply.json().get('error','')
                result['thread_start_error']=str(error)[:400]
            need(reply.ok,'Native thread creation failed '+str(reply.status_code)+': '+str(result.get('thread_start_error','')))
            thread_id=(reply.json().get('thread') or {}).get('id')
            need(thread_id,'No native thread ID')
            for _ in range(240):
                snap=session.get(AGENT_URL+'/agent/codex/workspace',timeout=15).json()
                conversation=snap.get('conversation') or {}
                if conversation.get('threadId')==thread_id and conversation.get('status') in ('ready','warning'):break
                time.sleep(.5)
            result['thread_origin']='created_by_test'
        else:
            result['thread_origin']='auto_created_by_isolated_web_client'
        result['native_thread']=True
        result['thread_id']=thread_id
        need(conversation.get('status') in ('ready','warning'),'Native thread preheat did not settle')
        result['thread_conversation_status']=conversation.get('status')
        result['thread_mcp_status_names']=sorted((conversation.get('mcpStatuses') or {}).keys())
        prompt=(
            'WAR-90 私有隔离画布中的原生 Canvas Agent 只读集成测试。你是唯一专业 Agent，选择的 Skill 是 director-skill-v0-candidate。'
            '按需阅读此 Skill 的 shot-plan 与 review-method 阶段卡。'
            '请通过终端工具真实执行以下只读命令（不是自己编造 JSON）：'
            'python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-shot '
            '--workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2 --shot-id Shot02 。'
            '它会返回目标 Shot02 的完整原文、故事源、版本哈希与未知项。'
            '然后真实调用 infinite-canvas MCP 的 canvas_get_state 与 canvas_get_selection，核对这是五节点的试验画布，唯一选中 Shot02。'
            '明确指出 B candidate 内容 SHA、Shot Plan 全文 SHA、Shot02 文本 SHA 是三个不同对象，不能比较相等。'
            '只输出 100-250 字中文简短事实与一个观看风险：目标 Shot02 / B ID / CLI 读成功否 / MCP 读成功否 / 工具范围或未知。'
            '当前没有真人修改意见，因此必须 no-handoff。'
            '不得用 shell 写临时文件，不调用 prepare/submit/run-stage，不修改任何画布或已批准 B，不生成媒体，不自签 A/B。'
        )
        params={'clientId':client_id,'threadId':thread_id,
            'conversationId':conversation.get('conversationId',''),
            'expectedRevision':conversation.get('revision',0),
            'prompt':prompt,'messageText':'WAR-90 isolated native Compact Shot read smoke; not user revision',
            'permissionMode':'automatic','model':'gpt-6-luna','effort':'medium',
            'skill':{'name':candidates[0]['name'],'path':candidates[0]['path']}}
        start=session.post(AGENT_URL+'/agent/codex/turn',json=params,timeout=100)
        result['turn_http_code']=start.status_code
        if not start.ok:
            result['turn_http_error']=str(start.json().get('error',''))[:400]
            raise RuntimeError('Native turn was rejected')
        result['native_turn']=True
        saw_busy=False;last={}
        for _ in range(320):
            time.sleep(.5)
            last=session.get(AGENT_URL+'/health',timeout=10).json()
            if last.get('codexBusy'):saw_busy=True
            if saw_busy and not last.get('codexBusy'):break
        result['busy_observed']=saw_busy
        result['busy_finished']=saw_busy and not last.get('codexBusy')
        result['conversation_final_status']=(last.get('conversation') or {}).get('status')
        history=session.get(AGENT_URL+'/agent/codex/threads/'+thread_id,timeout=60).json()
        redact_history(history,token)
        saved('native-thread-history.json',history)
        result['history_messages_count']=len(history.get('messages') or [])
        result['settled_turn_ids_count']=len(history.get('settledTurnIds') or [])
        final=tool(session,'canvas_get_state',{})
        result['private_canvas_unchanged']=len(final.get('nodes',[]))==5 and final.get('projectId')==state['projectId']
        afterselect=tool(session,'canvas_get_selection',{}).get('nodes') or []
        result['private_selection_unchanged']=len(afterselect)==1 and afterselect[0]['id']==shot02['id']
        # Real tool evidence must be established from raw history, not model self-report.
        dump=json.dumps(history,ensure_ascii=False)
        result['history_mentions_review_shot']=('review-shot' in dump)
        result['history_mentions_canvas_get_state']=('canvas_get_state' in dump)
        result['history_mentions_canvas_get_selection']=('canvas_get_selection' in dump)
        result['history_has_hindsight_tool_call']=('hindsight_search_pages' in dump)
        result['native_cli_execution_proven']=False  # requires structured event inspection
        result['native_canvas_mcp_read_proven']=False
    except Exception as exc:
        result['error_type']=type(exc).__name__
        result['error_message']=str(exc)[:550]
        traceback.print_exc()
    finally:
        if browser:
            try:browser.close()
            except Exception:pass
        if proc:
            proc.terminate()
            try:proc.wait(timeout=12)
            except subprocess.TimeoutExpired:proc.kill()
        if log:log.close()
        if webserver:
            webserver.shutdown();webserver.server_close()
        result['production_untouched']=h(B)==before
        result['private_test_cleaned']=True
        result['duration_s']=round(time.monotonic()-started,2)
        saved('native-compact-smoke-result.json',result)
        shutil.rmtree(root,ignore_errors=True)
    print('NATIVE_COMPACT_SMOKE',json.dumps({k:v for k,v in result.items()
               if k in ('native_http_agent','skill_discovered_by_http','mcp_config_summary',
                        'undesired_effective_mcp_enabled','native_thread','native_turn',
                        'turn_http_code','busy_observed','busy_finished','history_messages_count',
                        'history_mentions_review_shot','history_mentions_canvas_get_state',
                        'history_mentions_canvas_get_selection','history_has_hindsight_tool_call',
                        'private_canvas_unchanged','private_selection_unchanged',
                        'production_untouched','duration_s','error_type','error_message')},ensure_ascii=False),flush=True)
    if result.get('error_type'):raise SystemExit(2)
if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""WAR-90 native Canvas Agent read-only skill smoke; isolated app and browser."""
from pathlib import Path
import os,sys,time,json,hashlib,shutil,tempfile,subprocess,traceback
from urllib.parse import urlencode
import requests
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/native-agent-integrated-20261115'
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
SKILL=ROOT/'docs/planning/WAR-89/director-skill-v0-candidate'
sys.path.insert(0,str(ROOT/'docs/planning/WAR-90/single-agent-live-20261115'))
from hold_canvas import BrowserCDP
URL='http://127.0.0.1:17461'
def need(v,msg):
    if not v: raise RuntimeError(msg)
def hashfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(file,data):Path(file).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def call(s,name,data):
    r=s.post(URL+'/api/tools',json={'name':name,'input':data},timeout=45).json()
    need(r.get('ok'),name+' failed')
    return r['result']
def main():
    before=hashfile(B)
    need(before=='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7','baseline invalid')
    sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
    from runtime import Pilot
    pack=Pilot(B.parent).review_packet()
    result={'phase':'native-embedded-codex-readonly','baseline_sha':before,'production_untouched':None}
    work=tempfile.mkdtemp(prefix='war90-native-private-')
    private=Path(work)
    agent=None;browser=None;agent_log=None
    try:
        home=private/'home';home.mkdir()
        w=home/'.infinite-canvas/codex-workspaces/site'
        target=w/'.agents/skills/director-skill-v0-candidate'
        target.parent.mkdir(parents=True)
        shutil.copytree(SKILL,target)
        env=dict(os.environ,HOME=str(home),PORT='17461',CODEX_HOME='/home/sean/.codex')
        agent_log=(private/'agent.log').open('wb')
        agent=subprocess.Popen(['node',str(ROOT/'infinite-canvas/canvas-agent/dist/index.js')],
                              cwd=str(ROOT/'infinite-canvas/canvas-agent'),env=env,
                              stdout=agent_log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
        s=requests.Session()
        for _ in range(90):
            need(agent.poll() is None,'private Agent exited')
            try:
                if s.get(URL+'/health',timeout=2).ok:break
            except requests.RequestException:pass
            time.sleep(.2)
        else:raise RuntimeError('private agent did not start')
        localconf=json.loads((home/'.infinite-canvas/canvas-agent.json').read_text())
        need(localconf['url']==URL,'unexpected Agent endpoint')
        s.headers.update({'x-canvas-agent-token':localconf['token']})
        # This test instance alone disables nonessential inherited MCP servers.
        localconf['mcpOverrides']={k:False for k in
            ('codegraph','hindsight','hindsight-direct','blender','cua_repl')}
        (home/'.infinite-canvas/canvas-agent.json').write_text(
            json.dumps(localconf,ensure_ascii=False,indent=2))
        result['temporary_mcp_overrides']=sorted(localconf['mcpOverrides'])
        skills=s.get(URL+'/agent/codex/skills?forceReload=1',timeout=100).json()
        found=[x for x in skills.get('data',[]) if x.get('name')=='director-skill-v0-candidate']
        result['skill_listing']=[{'name':x.get('name'),'path':x.get('path'),'enabled':x.get('enabled')} for x in found]
        result['skill_listing_errors_count']=len(skills.get('errors',[]))
        need(len(found)==1 and found[0]['enabled'],'candidate not discovered exactly once')
        need(found[0]['path']==str(target/'SKILL.md'),'Skill not isolated copy')
        browser=BrowserCDP(private/'chrome')
        browser.launch()
        browser.send('Page.navigate',{'url':'http://127.0.0.1:3000/canvas?mode=new#'+urlencode({'agentUrl':URL,'agentToken':localconf['token']})})
        for _ in range(130):
            h=s.get(URL+'/health',timeout=5).json()
            if h.get('hasCanvas') and h.get('clients')==1:break
            time.sleep(.2)
        need(h.get('hasCanvas') and h.get('clients')==1,'no isolated/unique Canvas browser')
        for _ in range(90):
            state=call(s,'canvas_get_state',{})
            if state.get('projectId'):break
            time.sleep(.2)
        need(state.get('projectId') and not state.get('nodes'),'new test Canvas not empty')
        project=state['projectId']
        items=[{'title':'WAR-90｜已批准 B','text':'已批准 B: '+pack['authority']['approved_B_id']+'；仅只读测试，不接受新 B 审批','x':0,'y':0,'width':460,'height':260}]
        for i,shot in enumerate(pack['shots']):
            items.append({'title':'WAR-90｜'+shot['id']+' B Review',
                          'text':shot['id']+'\nB: '+pack['authority']['approved_B_id']+'\nShot SHA: '+shot['text_sha256']+'\n\n'+shot['text'],
                          'x':490+i*540,'y':0,'width':525,'height':580})
        call(s,'canvas_create_text_nodes',{'items':items,'direction':'row'})
        state=call(s,'canvas_get_state',{})
        need(state.get('projectId')==project and len(state.get('nodes',[]))==5,'test project changed')
        shot02=next(n for n in state['nodes'] if 'Shot02' in n.get('title',''))
        call(s,'canvas_select_nodes',{'ids':[shot02['id']]})
        selected=call(s,'canvas_get_selection',{}).get('nodes',[])
        need(len(selected)==1 and selected[0]['id']==shot02['id'],'test selection mismatch')
        client_id=browser.evaluate('sessionStorage.getItem("canvas-agent-client-id")')
        need(client_id,'actual UI clientId not accessible')
        result.update({'project_id':project,'nodes':5,'selected_shot':'Shot02','private_skill_loaded':True,
                       'actual_client_id_present':True,'client_id_safe_omitted':True})
        execute_native_turn(s,found[0],client_id,result)
        final=call(s,'canvas_get_state',{})
        result['canvas_unchanged_after_turn']=final.get('projectId')==project and len(final.get('nodes',[]))==5
    except Exception as e:
        result['exception']=type(e).__name__+': '+str(e)[:500]
        traceback.print_exc()
    finally:
        if browser:
            try:browser.close()
            except Exception:pass
        if agent:
            agent.terminate()
            try:agent.wait(timeout=10)
            except subprocess.TimeoutExpired:agent.kill()
        if agent_log:agent_log.close()
        shutil.rmtree(private,ignore_errors=True)
        result['production_untouched']=hashfile(B)==before
        save(OUT/'native-smoke-result.json',result)
    print('NATIVE_RESULT',json.dumps(result,ensure_ascii=False),flush=True)
def execute_native_turn(session,skill,client_id,result):
    reply=session.post(URL+'/agent/codex/threads/new',
        json={'clientId':client_id,'permissionMode':'automatic'},timeout=180)
    result['native_thread_http_status']=reply.status_code
    if not reply.ok:
        result['native_thread_error']=str(reply.json().get('error',''))[:500]
        return
    thread=reply.json().get('thread') or {}
    thread_id=thread.get('id')
    need(thread_id,'native Agent thread/new missing id')
    result['native_thread_id']=thread_id
    for _ in range(130):
        snap=session.get(URL+'/agent/codex/workspace',timeout=10).json()
        conversation=snap.get('conversation') or {}
        if conversation.get('status') in ('ready','warning') and conversation.get('threadId')==thread_id:break
        time.sleep(.4)
    result['native_conversation_status']=conversation.get('status')
    need(conversation.get('status') in ('ready','warning'),'native Agent Codex not ready')
    prompt=('WAR-90 独立测试中的 Canvas Agent 内置 Codex，是本轮唯一专业导演 Agent。'
        '你已显式选择 director-skill-v0-candidate。先按需阅读它的 Shot Plan 和 Review 阶段知识。'
        '请使用终端工具真实执行只读 CLI：python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-pack '
        '--workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2 '
        '获取已批准 B 的权威全文及 Shot02，不可只凭 Canvas MCP 的截断预览作专业判断。'
        '然后通过 infinite-canvas MCP 实际读取 canvas_get_state、canvas_get_selection，核对测试画布 5 节点及唯一 Shot02 选区。'
        '根据权威全文，只指出 Shot02 一个最重要的待观看验证风险；用户此刻没有新修改要求，故 no-handoff。'
        '禁止写文件、调用 prepare-stage、submit-stage 或 run-stage，不创建候选、不修改画布、不生成媒体、不批准 A/B。'
        '报告实际 CLI 与 MCP 是否成功、B ID 和完整正文是否可信、尚未验证的部分。')
    params={'clientId':client_id,'threadId':thread_id,
        'conversationId':conversation.get('conversationId',''),
        'expectedRevision':conversation.get('revision',0),
        'prompt':prompt,'messageText':'WAR-90 原生单 Agent 只读测试（非用户新反馈）',
        'permissionMode':'automatic','model':'gpt-6-luna','effort':'medium',
        'skill':{'name':skill['name'],'path':skill['path']}}
    out=session.post(URL+'/agent/codex/turn',json=params,timeout=90)
    body=out.json()
    result['native_turn_http_status']=out.status_code
    result['native_turn_accepted']=body.get('ok') is True
    if not out.ok:
        result['native_turn_error']=str(body.get('error',''))[:600]
        return
    seen_busy=False
    last={}
    for _ in range(220):
        last=session.get(URL+'/health',timeout=6).json()
        if last.get('codexBusy'):seen_busy=True
        if seen_busy and not last.get('codexBusy'):break
        time.sleep(.4)
    result['native_busy_observed']=seen_busy
    result['native_finished_observed']=seen_busy and not last.get('codexBusy')
    result['conversation_last_status']=(last.get('conversation') or {}).get('status')
    history=session.get(URL+'/agent/codex/threads/'+thread_id,timeout=40).json()
    save(OUT/'native-thread-history.json',history)
    result['history_keys']=list(history)
    result['history_messages']=len(history.get('messages') or [])
    result['history_has_thread']=bool(history.get('thread'))
    result['settled_turns']=len(history.get('settledTurnIds') or [])
    result['private_skill_selected_in_turn']=True
if __name__=='__main__':main()

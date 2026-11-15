#!/usr/bin/env python3
"""WAR-90 genuine hierarchical B pre-review. Does NOT approve A/B, modify pilot, or run media."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,os,shutil,subprocess,tempfile,time
ROOT=Path('/home/sean/projects/canvas-lab')
OUT=ROOT/'docs/planning/WAR-90/review-B-round1-20261115'
PILOT=ROOT/'docs/planning/WAR-90/pilot-D'
def digest(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def jwrite(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def call_agent(label,model,effort,prompt):
    dest=OUT/label
    if dest.exists():raise RuntimeError('Reviewer folder already exists: '+label)
    dest.mkdir(parents=True)
    (dest/'prompt.md').write_text(prompt,encoding='utf-8')
    home=Path(tempfile.mkdtemp(prefix='.tmp-home-',dir=dest))
    st=time.monotonic()
    try:
        auth=Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'auth.json'
        if auth.is_file():
            (home/'auth.json').write_bytes(auth.read_bytes())
            (home/'auth.json').chmod(0o600)
        command=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
                 '--sandbox','read-only','--json','-m',model,
                 '-c',f'model_reasoning_effort="{effort}"','-c','approval_policy="never"',
                 '-c','features.shell_tool=false','-c','project_doc_max_bytes=0',
                 '-C',str(dest),'-o',str(dest/'result.md'),'-']
        with (dest/'events.jsonl').open('wb') as stdout,(dest/'stderr.txt').open('wb') as stderr:
            p=subprocess.run(command,input=prompt.encode('utf-8'),stdout=stdout,stderr=stderr,
                             env=dict(os.environ,CODEX_HOME=str(home)),timeout=900)
        meta={'role':label,'model':model,'effort':effort,'exit':p.returncode,
              'duration_s':round(time.monotonic()-st,1),'start_and_end':now(),
              'prompt_sha256':digest(prompt.encode()),'result_sha256':digest((dest/'result.md').read_bytes())
                     if (dest/'result.md').exists() else None}
        jwrite(dest/'run.json',meta)
        print('REVIEW_FINISHED',label,meta['exit'],meta['duration_s'],flush=True)
        return meta
    finally:
        shutil.rmtree(home,ignore_errors=True)
def main():
    if (OUT/'manifest.json').exists(): raise RuntimeError('B review already initialized')
    state=json.loads((PILOT/'state.json').read_text(encoding='utf-8'))
    assert state['phase']=='awaiting-human-B' and state['active']['stage']=='shot'
    assert state['pilot_A'] and state['pilot_A']['stage']=='intent' and not state['pilot_B']
    assert state['active']['baseline_A']==state['pilot_A']['id']
    a=state['active']
    for stage in ('intent','beat','blocking','shot'):
        assert stage in a['artifacts'],f'missing stage {stage}'
    raw_source=(PILOT/'source.txt').read_bytes()
    frozen=json.dumps({
       'frozen_source_sha256':digest(raw_source),
       'approved_A_pilot_only':state['pilot_A'],
       'active_shot_candidate':a,
       'pending_shots':state['pending_shots'],
       'unknown':state['unknown'],
       'actual_review_context':state['reviews'],
       'formal_WAR35_approval':False
    },ensure_ascii=False,indent=2)
    packet='=== FROZEN SCRIPT (SOURCE AUTHORITY) ===\n'+raw_source.decode()+'\n=== PILOT A APPROVAL AND FULL BEAT/BLOCKING/SHOT ACTIVE CANDIDATE ===\n'+frozen+'\n=== END ===\n'
    (OUT/'frozen-B-packet.txt').write_text(packet,encoding='utf-8')
    jwrite(OUT/'manifest.json',{'started_at':now(),
      'source_sha256':digest(raw_source),'B_candidate_id':a['id'],
      'B_candidate_content_sha256':a['content_sha256'],
      'A_pilot_id':state['pilot_A']['id'],
      'packet_sha256':digest(packet.encode('utf-8')),
      'reviewers':'story Luna Low; directing Luna Medium; complex geometry Astra Medium; lead Luna Medium',
      'B_user_approval_at_start':None})
    common=("你是 Canvas Lab WAR-90 的真实独立 B 整场 Shot Plan 预审 Reviewer，非导演生成器，禁止写文件、调用媒体或伪造人类批准。"
       "必须依据冻结故事、真实已批准 pilot A Intent、Beat/Blocking/Shot 当前完整阶段成果，以及未证项判断。"
       "从故事决定性事件/四句对白/首次认知窗口/二次遮挡/最后右手交付逐项映射到镜与声音，再从每镜反查是否新增情节；严查重复动作和切点连续性。"
       "区分 P0 已证故事/数据硬冲突，P1 明确的文本专业缺口，P2 未证几何/观看风险，P3 合理拍法差异。"
       "没有媒体/Blender/观众实际证据时不得宣称几何或受众效果已过验证；也不能用媒体未知掩盖明确文字冲突。"
       "这是 pilot B 预审，不是正式 WAR-35 Decision，不得代替用户 B 批准。"
       "明确受影响 Shot/Beat、依据、原因和最小修法。无需大而全审阅其他研究，中文报告 500–1100 字。")
    roles={
       'reviewer-story':('故事事实、对白/动作双向覆盖、角色知情与交接连续性；重点找错漏和无源新增', 'gpt-6-luna','low'),
       'reviewer-craft':('观众钥匙细节优先的镜头任务、观看注意竞争、假 POV、切点及表达代价；重点评估是否真的服务用户 A', 'gpt-6-luna','medium'),
       'reviewer-space':('复杂 Blocking→Shot 空间/物件/眼线/动作状态逻辑：物理可见≠注意≠观众读懂；首次露出林仍未见、周只察觉蓝夹位置；唯一钥匙同一坐标/右手交接；跨镜阶段与潜在空间不可同时满足的风险，不假装算过真实几何', 'gpt-6-astra','medium')
    }
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks=[pool.submit(call_agent,n,model,effort,common+'\n本次专项：'+role+'\n'+packet)
              for n,(role,model,effort) in roles.items()]
        reports=[f.result() for f in as_completed(tasks)]
    if any(r['exit']!=0 or not r['result_sha256'] for r in reports):
        print('REVIEWER_FAILURE_NO_LEAD',flush=True);return
    originals='\n\n'.join('=== '+n+' original report ===\n'+(OUT/n/'result.md').read_text()
                          for n in roles)
    lead=("你是 WAR-90 的主审阅 Agent，负责筛选 3 个彼此隔离 Reviewer 的原始意见，而不是票数汇总。"
         "亲自对照冻结故事及全场候选审查每项潜在 P0/P1，明确哪些意见依据不足、过度保守、误把媒体验证未知判失败。"
         "如果确实存在文本事实矛盾或关键 Shot 未能交付用户批准的钥匙细节主轴，则 needs_targeted_revision 并说明最小改动层次/Shot，不能直接批准 B。"
         "如果仅开放几何或受众风险则 ready_for_user_B，明确它们必须交用户理解，绝不可宣称实测通过。"
         "输出：1 ready_for_user_B|needs_targeted_revision|blocked，依据；2 用户批准 A 的真实承接与事件/对白/状态覆盖；"
         "3 三份 Reviewer 意见采纳/不采纳及理由；4 120–280 字 B 导演方案摘要，逐镜任务和大致切点；"
         "5 未证风险/待实测；6 交主流程的唯一下一步。"
         "禁止写文件或自签用户 B、不要将模型评分当成观众证据。")
    leadresult=call_agent('main-reviewer','gpt-6-luna','medium',lead+'\n'+packet+'\n=== 3 INDEPENDENT REVIEWS ===\n'+originals)
    jwrite(OUT/'summary.json',{'ended_at':now(),'complete':leadresult['exit']==0 and all(x['exit']==0 for x in reports),
       'reviewers':reports,'lead':leadresult,'B_candidate_id':a['id'],
       'B_candidate_content_sha256':a['content_sha256'],'user_B_still_unapproved':True})
    print('B_HIERARCHICAL_REVIEW_COMPLETE',leadresult['exit'],flush=True)
if __name__=='__main__':main()

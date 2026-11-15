#!/usr/bin/env python3
"""One bounded WAR-90 reviewer-evidence reconciliation; do not mutate active pilot."""
import json,runpy,hashlib
from pathlib import Path

ROOT=Path('/home/sean/projects/canvas-lab')
RD=ROOT/'docs/planning/WAR-90/review-round2-20261115'
PILOT=ROOT/'docs/planning/WAR-90/pilot-D'
source=runpy.run_path(str(RD/'review_runner.py'))
model_call=source['model_call']
p=PILOT/'runs/68d2717b905641d5a872550a896abcfc/input.txt'
packet=json.loads(p.read_text().split('\nB-FLEX INPUT\n',1)[1].split('\n\nSOURCE VERBATIM\n',1)[0])
data=packet['knowledge']
verifications=[]
for name,text in data.items():
    file=PILOT/'skill'/name
    verifications.append({'entry':name,'in_prompt':True,'content_equals_frozen_file':file.is_file() and text==file.read_text(),
                          'sha256':hashlib.sha256(text.encode()).hexdigest(),'bytes':len(text.encode())})
assert len(verifications)==4 and all(x['content_equals_frozen_file'] for x in verifications)
(RD/'knowledge-evidence.json').write_text(json.dumps({
    'source_input':str(p.relative_to(ROOT)),
    'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
    'knowledge_entries':verifications,
    'distinct_terms':'in-prompt knowledge-index/review-method full bodies versus EXTERNAL director sources referenced by index (not loaded)'
},ensure_ascii=False,indent=2)+'\n')
old=(PILOT/'runs/93fc96166f56424c8a69bfa6f12ff5e9/result.txt').read_text()
new=(PILOT/'runs/68d2717b905641d5a872550a896abcfc/result.txt').read_text()
feedback=(ROOT/'docs/planning/WAR-90/user-feedback-A-revision-20261115.md').read_text()
for name in ('reviewer-story','reviewer-craft','main-reviewer'):
    assert (RD/name/'run.json').is_file() and (RD/name/'result.md').is_file()
review_old='\n\n'.join('=== '+name+' ===\n'+(RD/name/'result.md').read_text() for name in ('reviewer-story','reviewer-craft','main-reviewer'))
evidence=(RD/'knowledge-evidence.json').read_text()
# Third independent reviewer, narrow FACT CHECK; not re-litigating shot-level craft.
checker_prompt=f"""你是 WAR-90 的第三名独立 Reviewer，负责限定范围的证据事实核对。不得修改文件或批 A。请独立裁定：新候选“仅采用输入中提供的候选 SKILL、Intent、knowledge-index、review-method 正文”和“外部 DS/TF/VM 源章节未加载”是否互相矛盾？确证哪些正文实际在模型输入，哪些并未加载。不能把外部三套 Skill 正文与 knowledge-index/review-method 正文混为一谈。只在确有输入证据虚假时判 P1；普通措辞差异 P2 或无需修改。注意此前其他 reviewer 可能判断错，但你还没有看到他们的原文；不得根据他们投票。
=== VERIFIED ACTUAL INPUT PACKET / HASH (obtained by deterministic parser) ===
{evidence}
=== FOUR KNOWN KNOWLEDGE BODY EXCERPTS ===
{chr(10).join(n+': '+t[:300] for n,t in data.items())}
=== ACTUAL NEW CANDIDATE ===
{new}
请 250–500 中文字，做独立事实核对，给 ready_for_user_A 或 needs_local_revision，并引用可核查的输入位置。"""
check=model_call('reviewer-evidence','gpt-6-luna','low',checker_prompt)
assert check['exit']==0 and check.get('result_sha256'),"Third evidence reviewer failed"
lead_prompt=f"""你是 WAR-90 此轮主审阅 Agent 的证据重审会话。你的上一份综合报告原文在下方；现在新增第三份独立证据核查，须**对之前意见负责并在新证据面前纠错**。不得修改任何文件，不得代用户批 A。不要为了维持旧判断而强行找理由；也不能因为新增 reviewer 一人改变意见就自动采纳。请裁定需要或不需要局部修候选，再交用户 A。主流程已实证输入包实际包含完整 knowledge-index/review-method 两份正文，不能混同于这两份索引指向的外部 DS/TF/VM 原始内容。保留原两名 reviewer 的有效专业风险，但不要把 Beat/Shot/mid-render 责任强行塞进 Intent。最多一次证据纠错，不开启无限轮审查。
回答：
1. final_status: ready_for_user_A | needs_local_revision | blocked；
2. 是否撤回原有依据矛盾的阻断，以及为什么；
3. 最终应采纳/暂缓的专业意见（不把来源事实和表演实现混淆）；
4. 交给真实用户的 120–220 字**钥匙细节优先** A 核心方案与取舍；
5. 重要未证风险，明确用户批准尚未发生。

=== ACTUAL EXTERNAL USER FEEDBACK ===
{feedback}
=== DETERMINISTIC KNOWLEDGE PACKET CHECK ===
{evidence}
=== INDEPENDENT REVIEWER #3 ===
{(RD/'reviewer-evidence/result.md').read_text()}
=== TWO ORIGINAL INDEPENDENT REVIEWERS AND PRIOR MAIN REVIEW ===
{review_old}
=== FULL NEW CANDIDATE ===
{new}
=== FULL PREVIOUS UNAPPROVED CANDIDATE FOR DELTA ===
{old}
"""
lead=model_call('main-evidence-reconsideration','gpt-6-luna','medium',lead_prompt)
assert lead['exit']==0 and lead.get('result_sha256'),"Reconsideration failed"
(RD/'reconsideration-summary.json').write_text(json.dumps({'evidence_check':check,'lead_reconsideration':lead,
    'note':'Third independent reviewer brought in only to adjudicate a demonstrated possible review false-positive; no model results changed; user A remains unapproved'},ensure_ascii=False,indent=2)+'\n')
print('RECONCILIATION_DONE',flush=True)

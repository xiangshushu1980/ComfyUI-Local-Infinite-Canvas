from pathlib import Path
import sys, json, hashlib
root=Path('/home/sean/projects/canvas-lab')
out=root/'docs/planning/WAR-90/human-feedback-preflight-20261115'
sys.path.insert(0,str(root/'tools/director-runtime-v0'))
from runtime import shot_sections,Pilot
state_file=root/'docs/planning/WAR-90/pilot-D-local-repair-v2/state.json'
assert hashlib.sha256(state_file.read_bytes()).hexdigest()=='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
packet=Pilot(state_file.parent).review_packet()
shots=shot_sections(packet['stages']['shot']['text'],[s['id'] for s in packet['shots']])
plan="""# WAR-90｜真人反馈关口设计候选（尚未执行）
当前阶段：B 已批准后的真人 Shot02 修改意见采集预检，尚无用户新意见，也无生产 Canvas/媒体授权。
面向人的测试目的：让用户看清 Shot02 的『首次露钥匙→蓝夹再遮→整理动作持续→切 Shot03』，指出一个最需要改的表达问题；确认单一 Codex 可以将真实意见绑定 B/Source/Shot 版本后修订、复检邻镜、回显差异、停在真人 B 审阅，不自行批准。
拟定最小动作：
1. 不在已有真实 Canvas 上写入。可用现有隔离的 Canvas Agent 临时配置 + 专用持久浏览器 profile 搭建可见的独立测试画布；如果无法可靠保证浏览器/agent独立，退回 Chat 文本审阅，明确“未完成 Canvas UI 真人输入”。不改生产服务和全局 MCP。
2. 只展示 frozen review-pack 已批准四镜文本。用户选 Shot02 后，使用 Chat 提供**明确的实际修改意见**，作为 external-user-unverified 原文；不可把模型提出的修改建议自动算用户反馈。当前轮不预填任何反馈。
3. 真实意见之后复用已实现 feedback_bridge.py 的 make_catalog/check_catalog/capture_feedback/clone_for_revision/stage_scope，读回实际 Canvas projectId、selection、源 B/Shot SHA；若未选择或版本不一致，拒绝提交。不得写原批准 B。
4. 唯一专业 Codex 使用 director-skill-v0-candidate + Canvas MCP + Runtime CLI prepare-stage/submit-stage；如果需要修改 Beat/Blocking/Source，则上报停下，不硬做 Shot-only 修订。局部已提交后 Runtime 应复位新 B 并标记相邻镜头待复核；主流程组织独立 Reviewer/主审对新候选审阅，再给用户审 B。Reviewer 没有审批权。
5. 差异回显只用隔离测试画布的文本节点，不触发生成、不依赖正式 Canvas UI 写反馈，不增加临时 HTTP 桥接层；本轮至多准备“可给人看的目标和正式反馈输入点”，无真人意见就停在关口。
6. 每份报告显式写“当前阶段”和“给人看的测试目的”，并列出实测通过/未知/需要人操作。保存 SHA、原始对话文字、run ID 和安全边界。
拟验证：用户真实反馈的 provenance、Selection/B/Shot版本绑定、单Agent工具调用、实际差异与邻镜、主审阅接受范围、测试画布隔离。不可用 fake 结果冒充真实模型，也不能由自动化签署 B。
请主审判断是否需要先不搭建额外浏览器，而改为先将 Shot02 与相邻镜头在 Chat 中人可读展示，待用户给出反馈后再在隔离画布复现。请权衡是否存在不可消除的安全/真实性混淆。
"""
sections=[
("PROPOSED HUMAN TEST PLAN",plan),
("CURRENT FROZEN AUTHORITY", json.dumps(packet['authority'],ensure_ascii=False,indent=2)),
("APPROVED SHOT01-03", '\n\n'.join(shots[k] for k in ['Shot01','Shot02','Shot03'])),
("REVIEW COLLAB RULES",(root/'docs/agent/review-agent-collaboration.md').read_text()),
("PRIOR INTEGRATION EVIDENCE",(root/'docs/planning/WAR-90/single-agent-live-20261115/README.md').read_text()),
("EXISTING FEEDBACK TRANSPORT",(root/'docs/planning/WAR-90/canvas-feedback-20261115/feedback_bridge.py').read_text().split('def fake_director_for_transport_only')[0]),
]
frozen='\n\n'.join('## '+x+'\n'+y for x,y in sections)
(out/'frozen-packet.md').write_text(frozen)
(out/'manifest.json').write_text(json.dumps({'state_sha256':hashlib.sha256(state_file.read_bytes()).hexdigest(),'frozen_sha256':hashlib.sha256(frozen.encode()).hexdigest(),'B_id':packet['authority']['approved_B_id'],'purpose':'preflight; no real user feedback yet','candidate':'human-facing test plan; not a DirectorPlan'},ensure_ascii=False,indent=2)+'\n')
print('FROZEN_PREVIEW',len(frozen.encode()),'SHA',hashlib.sha256(frozen.encode()).hexdigest())

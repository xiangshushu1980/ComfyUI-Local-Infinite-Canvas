# WAR-90｜D《错过的钥匙》真实 Intent A 与分层审阅收口（2026-11-15）

## 1. 执行结果与当前门禁

- Eric，项目 `/home/sean/projects/canvas-lab`；源剧本 `docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-D/script-D.txt`，SHA-256 `65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`。
- 经 `tools/director-runtime-v0/cli.py run-stage --workspace docs/planning/WAR-90/pilot-D --stage intent --mode resume` **真实调用成功**：Codex `gpt-6-astra` Medium，run ID `93fc96166f56424c8a69bfa6f12ff5e9`；实际输出 SHA-256 `9179fdb542e5dcfa74085d5e2a0a30cac390ccf70e2d4182eee5eb76b060c522`。输入、原始输出、JSONL、stderr、metadata 和 candidate 在 `docs/planning/WAR-90/pilot-D/runs/93fc96166f56424c8a69bfa6f12ff5e9/`。
- 运行壳保存首份有效**探索候选**，`phase=awaiting-human-A`，`active=93fc96166f56424c8a69bfa6f12ff5e9`，`pilot_A=null`，`pilot_B=null`，`formal_WAR35_approval=false`，此前额度不足的 run 仍隔离；未执行 Beat/Blocking/Shot。首次 `Resume` 是从无批准/无工作候选的源输入建立新候选，不声称恢复历史已批准 Intent。
- 当前未证 media、geometry、audience，原候选存在约 35–40 秒的**导演试排估算**，未确认为全场制作时长；不得把它当 H3 片段上限、冻结预算或交互 A 必批内容。

## 2. 用户新确认的审阅组织规则

2026-11-15 用户确定：**一个主审阅 Agent，按复杂度开 1–3 个相互隔离 Reviewer**；一般使用轻量模型，复杂逻辑/框架设计才升级至更强模型。Reviewer 意见先汇总至主审阅 Agent，由它对证据与必要性做裁定，再把唯一汇总交 ChatGPT 主流程；审阅 Agent 不拥有用户 A/B 批准权。

权威项目级规则：`docs/agent/review-agent-collaboration.md`，根 `AGENTS.md` 有使用入口。本轮真实拓扑如下：

1. `reviewer-story` — `gpt-6-luna` Low，独立源事实/知情审查，exit=0，18.3 秒；
2. `reviewer-craft` — `gpt-6-luna` Low，独立导演专业表达审查，exit=0，19.0 秒；
3. `main-reviewer` — `gpt-6-luna` Medium，收到同一冻结剧本、同一未批准 Intent 以及两份原始 Reviewer 报告后独立综合裁定，exit=0，22.5 秒。

每个均单独 ephemeral Codex 会话；独立 Reviewer 互不看对方报告。真实 prompt、原始响应、运行 JSONL、模型与 effort、SHA、summary 都在本目录的 `reviewer-story/`、`reviewer-craft/`、`main-reviewer/`、`summary.json` 中；审阅内容不返回受测 Director 模型，不进行二次创作污染。

## 3. 主审阅 Agent 决定及主流程复核

**主审阅裁定：`ready_for_user_A`。ChatGPT 独立核对原始 Intent 与剧本后接受这项阶段裁定。**

- 故事核心符合：观众先看到、林未注意；林整理时以蓝夹无意挡回；周只观察到被覆盖的位置而起疑；林第二次看到后略尴尬；同一钥匙由林交周右手，周去门、林留桌。没有已证 P0 事实冲突。
- 方向是**共享日常整理动作里，观众短暂领先于林**，而非刻意钥匙谜题。真实表达替代是以**钥匙道具细节**为中心，增加首次显露的可读性，但代价是削弱人物动作关系并加强谜题感。两者可以在 Shot 规划时局部结合，不需在 Intent 阶段锁死镜数或机位。
- reviewer-story 的“周提问时应更明确林仍未注意”属于表达提醒，原候选已明确首次露出时林没注意、蓝夹遮回且直到二次发现前不让人物发现；**不是文本事实硬冲突**。原文声音效果可能含纸声、提示音或门响等均未提供真实素材；以发现顺序/自然表演为审核目标，后续不要让非必要声音政策成为来源事实。
- reviewer-craft 对“寻宝谜题感”、声音禁项、35–40 秒估算可能过早定死的提醒有意义，但仍是非阻断 P2/未证。原候选清楚不固定镜数、焦距和实体布局，且标出媒体与观众验证未知。现阶段不为了这些提醒修改最终 Prompt 或覆盖已保存的 Intent 原始候选。
- 两个 Reviewer 的独立意见及主审阅综合报告都保留为证据，不通过人数投票决定；审阅结论绝不视为用户 A approved 或正式 WAR-35 Decision。

## 4. 交用户 A 的精简决策包

**建议 A 方向**：让观众像旁观者一样看两人自然整理与寻找；文件移开时观众先注意到钥匙，林依然没看见；蓝文件夹无意再次盖住，周只是注意遮挡位置不对。林重新发现后的短暂停顿产生轻微尴尬，不表演成刻意藏物或喜剧夸张。最终一把钥匙交到周的右手。

**真实替代**：把首次露出的钥匙拍得更突出，观众更容易辨认，但可能削弱两人的行动连续关系，使片段偏向解谜。当前主审阅建议优先“共享动作／自然错位”，必要时后续局部用道具镜头提高可读性。

**用户需要决策的唯一方向问题**：是否采用“共享动作中的注意力错位”作为 Director Intent A，或更偏向“钥匙细节引导观看”？其余 Beat/Blocking/Shot、秒数、音效、几何与视觉效果均未进入已批准状态，不要求用户阅读完整中间稿。

## 5. 下一步与执行边界

在用户**明确回复**批准/调整 A 之前，不调用 `record-review` 写 pilot A、不运行 Beat/Blocking/Shot、不做生产 Canvas 操作。不把主审阅 Agent 的 `ready_for_user_A` 解读为 `pilot_A=accepted`。用户反馈届时先保存外部真实证据文件、记录 actor=human（仍只是 pilot-only）后继续 stage Resume。下一轮真实交互若有重大演员/媒体效果缺口，局部修订而不是补写通用七文件 Prompt。

当前 WAR-90 仍 In Progress；本记录为项目 Eric 本地权威正文，Linear 仅保留状态与入口。Git 保存请仅加入 WAR-90 与项目审阅规则文件，保留现有 WAR-35 混合工作树，不 push。

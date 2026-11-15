你是独立审阅 Agent。审阅的是 WAR-90 内置 Canvas Agent 集成实验与下一步方案，非生成器，不能修改文件、执行工具或自行签署 A/B。严格区分真实 native Thread 接受、实际 Skill 读取、MCP 调用成功、Runtime CLI 只读调用、Runtime 修改提交尚未发生、生产安装尚未发生。对未完成/不可信证据不得自动判通过；指明最小阻塞，避免另建导演 Agent、HTTP bridge、重复原 Skill。回答简明分级 P0/P1/P2，源证据定位及建议。本次专项：重点：唯一导演 Agent + 专业 Skill + 工程 Runtime + Canvas MCP 的角色边界、上下文噪声、用户可理解阶段/测试目的、WAR-90 与 WAR-37/35 范围。

--- FROZEN EVIDENCE ---
## Proposed architecture
# WAR-90｜Director Skill 接入 Canvas Agent 原生调用的设计候选

## 当前阶段与给人看的测试目的

当前阶段：Canvas Lab 内置 Agent 的 Skill 发现与原生 Codex 对话只读验证。

给人看的测试目的：导演专业调用直接发生在画布里的同一个 Agent，先验证 Skill 发现 → 原生线程 Skill 选择 → MCP 画布/选区读取 → 导演无交接输出，再判断是否有必要加薄适配。不再由 ChatGPT 充当每次转发者，不由 Runtime 启动第二个 Agent。

## 已有事实与限制

- B 权威在 docs/planning/WAR-90/pilot-D-local-repair-v2/state.json，SHA256=23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7，必须不变。
- 原生 Canvas Agent http.ts 支持 skills 列表、threads/new、turn Skill name/path 校验。同一 Codex startTurn 负责模型调用与 infinite-canvas MCP。
- WAR-89 的 Director Skill 仍是七文件候选，未正式安装；Runtime 已有 prepare-stage / submit-stage 无二次模型调用。
- 前一轮独立 Codex CLI + Canvas MCP 的只读 no-handoff 已验证；它不是画布内 Codex 原生对话。
- 本轮为隔离 Agent HOME、浏览器与技能副本 smoke；不能修改真实用户画布、生产配置、正式 WAR-35 Schema。
- 用户明确当前没有 Shot02 修改意见，所以不运行候选提交、不自动签 B、不运行媒体。
- 原生 MCP 可能要求审批；工具可用性须以真实 Codex 日志为准，不凭服务状态或输出自述声称成功。
- 其他原生 MCP 可能由 Eric 全局环境继承，须按任务减少上下文噪声，不在生产 Agent 上盲目禁用。
- Canvas 节点的返回内容会截断，正文仍以当前已批准本地资料和 SHA 为准。

## 最小下一步

1. 收口原生 Agent Skill Discover、原生 turn/Tool 的实测证据，逐条区分成功/失败/未知。
2. 先只使用隔离配置、项目里的候选 Skill 副本和现有 CLI；不新建长期运行的导演 Agent 或 Canvas HTTP 桥。
3. 若未证真实 MCP 调用或审批阻塞，先解决原生消息工具权限和适当 Skill 路径发现，禁止虚构已通过。
4. 若要安装到用户正在使用的正式 Agent，另行审阅安装范围、Skill 命名、审批与回滚；本轮不操作用户生产配置。
5. 设计/代码复杂变更交两名独立 Reviewer 与主审阅 Agent，审阅是外围质量控制，不能装进正式导演运行链当第二专业 Agent。
6. UI 导演节点映射留 WAR-37，typed DirectorPlan/Review 留 WAR-35；WAR-90 只验证单 Agent 试点。
7. 尚无真人修改意见时只读停点；真实修改闭环留待未来具体反馈再执行。

审阅产物要求：accept / targeted-revision / block / unknown；明示证据、不确定、必须/可选/延期及最小行动。不替用户签署 A/B。

## 本轮原生 Runtime 真实结果与新发现（独立核对）

- 新一次 Native turn: Skill selector 返回 200，内置 Codex 线程在测试画布执行 16 条历史消息，1 个 settled turn，codexBusy true→false；未触碰原 B、测试画布保持 5 节点。
- 同一个 Agent 终端实际执行 Runtime CLI review-pack 成功，之后查询本地 JSON 并获得完整 Shot02；还实际执行 MCP canvas_get_state / canvas_get_selection 成功。模型最后回答 no-handoff。
- **不能据此宣称无越界行为**：模型另调用了 hindsight_search_pages，失败（既定输入并不需要这个无关历史检索）。虽然独立 Agent 配置尝试禁用 Hindsight/Codegraph，仍出现 Hindsight tool 与 Codegraph 的 warning。须区分用户全局 Codex 配置、原生线程 config override 与实际暴露 Tool。
- 模型为了避免 CLI 巨大 JSON 导致终端截断，额外写入了 /tmp/war90-review-pack.json。该文件属于这轮模型临时输出而不是 Runtime 候选；已检查格式和 B ID 后明确删除。下一轮更应通过精简、明确权威层次的只读 CLI 提供目标 Shot，避免写临时中间文件。
- **重大误判核验**：模型把 B candidate content SHA256=64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7 与 Stage shot text SHA256=b2c2d5e14eb292cfafa1e9049913f97c6229ea5f1be51b1f7a94020f90fe8817 直接比较而报错。它们是不同对象，无需相等。工程侧独立验证 Stage shot text sha256 实算与 Stage 声明完全一致；B 原始 state SHA 亦保持不变。不允许把此模型解释性错误记为真实 Authority 损坏。
- Native Test 是隔离新 Agent + headless 浏览器，**非用户生产画布与其现有 Agent 线程**。没有真人修改请求、候选生成、媒体或身份认证。
- 下一步审阅需判断：优先补一个只读目标镜头 compact view / 模型工具规则约束，还是只修 Skill 规程；如何控制非必要 MCP（先证明配置原因），以及是否需要不同 Issue。所有复杂更改先出方案再改。

## Native test result JSON
{
  "phase": "native-embedded-codex-readonly",
  "baseline_sha": "23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7",
  "production_untouched": true,
  "temporary_mcp_overrides": [
    "blender",
    "codegraph",
    "cua_repl",
    "hindsight",
    "hindsight-direct"
  ],
  "skill_listing": [
    {
      "name": "director-skill-v0-candidate",
      "path": "/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site/.agents/skills/director-skill-v0-candidate/SKILL.md",
      "enabled": true
    }
  ],
  "skill_listing_errors_count": 0,
  "project_id": "aMWLszUPVij73DtP74aXB",
  "nodes": 5,
  "selected_shot": "Shot02",
  "private_skill_loaded": true,
  "actual_client_id_present": true,
  "client_id_safe_omitted": true,
  "native_thread_http_status": 200,
  "native_thread_id": "01a1dfed-14d1-7de0-8ed9-d73026b450f6",
  "native_conversation_status": "warning",
  "native_turn_http_status": 200,
  "native_turn_accepted": true,
  "native_busy_observed": true,
  "native_finished_observed": true,
  "conversation_last_status": "warning",
  "history_keys": [
    "ok",
    "workspace",
    "conversation",
    "thread",
    "messages",
    "settledTurnIds",
    "historyReady"
  ],
  "history_messages": 16,
  "history_has_thread": true,
  "settled_turns": 1,
  "private_skill_selected_in_turn": true,
  "canvas_unchanged_after_turn": true
}
## Historical native thread first run
{
  "phase": "native-embedded-codex-readonly",
  "baseline_sha": "23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7",
  "production_untouched": true,
  "skill_listing": [
    {
      "name": "director-skill-v0-candidate",
      "path": "/tmp/war90-native-private-m3k5p6q1/home/.infinite-canvas/codex-workspaces/site/.agents/skills/director-skill-v0-candidate/SKILL.md",
      "enabled": true
    }
  ],
  "skill_listing_errors_count": 0,
  "project_id": "QgUnNcg52AglU6a5cF9dT",
  "nodes": 5,
  "selected_shot": "Shot02",
  "private_skill_loaded": true,
  "actual_client_id_present": true,
  "client_id_safe_omitted": true,
  "native_thread_http_status": 200,
  "native_thread_id": "01a1dfe9-742d-78d2-95ca-392ab1eca8ee",
  "native_conversation_status": "warning",
  "native_turn_http_status": 200,
  "native_turn_accepted": true,
  "native_busy_observed": false,
  "native_finished_observed": false,
  "history_keys": [
    "ok",
    "workspace",
    "conversation",
    "thread",
    "messages",
    "settledTurnIds",
    "historyReady"
  ],
  "history_messages": 8,
  "history_has_thread": true,
  "private_skill_selected_in_turn": true,
  "canvas_unchanged_after_turn": true
}
## Full native final messages and tool activity summaries
[
  {
    "role": "user",
    "title": null,
    "text": "WAR-90 原生单 Agent 只读测试（非用户新反馈）",
    "detail": ""
  },
  {
    "role": "assistant",
    "title": "Codex",
    "text": "我会按此技能的 Review/Shot Plan 阶段核对权威输入，并只做用户指定的只读 CLI 与当前画布读取。先确认技能相关方法和可用 MCP 工具，再执行审阅；不会触发候选或生成流程。",
    "detail": ""
  },
  {
    "role": "tool",
    "title": "调用工具：hindsight_search_pages",
    "text": "",
    "detail": "{'kind': 'tool', 'status': 'failed', 'rows': []}"
  },
  {
    "role": "assistant",
    "title": "Codex",
    "text": "Hindsight 搜索工具返回了 API 错误，暂时没有可用的历史页面内容。我继续读技能要求的 Review 与 Shot Plan 说明，并按要求实际运行 CLI、读取当前画布状态和选区。",
    "detail": ""
  },
  {
    "role": "tool",
    "title": "执行命令",
    "text": "/bin/bash -lc 'python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-pack --workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2'",
    "detail": "{'kind': 'command', 'status': 'completed', 'rows': [{'label': '工作目录', 'value': '/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site'}, {'label': '退出状态', 'value': '0'}], 'output': '{\\n  \"format\": \"war90-director-preview-only-v0\",\\n  \"purpose\": \"read-only director review presentation for future Canvas Agent\",\\n  \"authority\": {\\n    \"source_sha256\": \"65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d\",\\n    \"source_text\": \"# 《错过的钥匙》\\\\n类型：现实主义短剧情\\\\n目标时长：约 35–40 秒\\\\n地点：一间小型办公室，傍晚\\\\n人物：林（男，30多岁）、周（女，30岁左右）\\\\n\\\\n内景 · 办公室 · 傍晚\\\\n\\\\n办公室里，一张长桌靠着墙，门在桌子的另一侧。桌上有一叠文件、一个蓝色文件夹和一把银色钥匙。\\\\n\\\\n林站在桌前整理文件。周站在靠近门的位置，准备离开。\\\\n\\\\n周：「钥匙呢？」\\\\n\\\\n林：「刚才还在桌上。」\\\\n\\\\n林低头寻找。他把桌上的文件挪到一边，露出那把银色钥匙。\\\\n\\\\n周从门边向桌子走来。\\\\n\\\\n林没有注意到钥匙已经露出来。他拿起蓝色文件夹，放到那叠文件上，文件夹恰好挡住了钥匙。\\\\n\\\\n周走到桌旁，目光落在蓝色文件夹上。\\\\n\\\\n周：「你刚刚是不是盖住了什么？」\\\\n\\\\n林停下手里的动作。\\\\n\\\\n他移开蓝色文件夹，钥匙重新露出来。\\\\n\\\\n林看着钥匙，短暂沉默。\\\\n\\\\n林：「找到了。」\\\\n\\\\n周伸出右手。林拿起钥匙，将它交到周的右手中。\\\\n\\\\n周握住钥匙，转身朝门口走去。\\\\n\\\\n林留在桌边。\\\\n\\\\n【已确认的创作意图】\\\\n这是一个关于注意力错位的小片段。\\\\n- 观众应该先于林发现钥匙"
  },
  {
    "role": "tool",
    "title": "执行命令",
    "text": "/bin/bash -lc 'python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-pack --workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2 --help'",
    "detail": "{'kind': 'command', 'status': 'completed', 'rows': [{'label': '工作目录', 'value': '/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site'}, {'label': '退出状态', 'value': '0'}], 'output': 'usage: cli.py review-pack [-h] --workspace WORKSPACE\\n\\noptions:\\n  -h, --help            show this help message and exit\\n  --workspace WORKSPACE'}"
  },
  {
    "role": "assistant",
    "title": "Codex",
    "text": "CLI 已成功返回完整 JSON，但终端默认输出超过显示上限，关键的 B 正文被截断。我会再次执行同一个只读命令，将输出保存到 `/tmp` 后按 JSON 提取已批准 B 的全文和 Shot02，确保专业判断依据完整；随后直接读取画布两个 MCP 状态。",
    "detail": ""
  },
  {
    "role": "tool",
    "title": "执行命令",
    "text": "/bin/bash -lc \"python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-pack --workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2 > /tmp/war90-review-pack.json && python3 -c 'import json; p=json.load(open(\\\"/tmp/war90-review-pack.json\\\")); print(\\\"APPROVED_B_ID:\\\",p[\\\"authority\\\"][\\\"approved_B_id\\\"]); print(\\\"APPROVED_B_CONTENT_SHA256:\\\",p[\\\"authority\\\"][\\\"approved_B_content_sha256\\\"]); print(\\\"B_TEXT_SHA256:\\\",p[\\\"stages\\\"][\\\"shot_plan\\\"][\\\"text_sha256\\\"]); print(\\\"--- APPROVED B FULL TEXT ---\\\"); print(p[\\\"stages\\\"][\\\"shot_plan\\\"][\\\"text\\\"]); print(\\\"--- REVIEW FLAGS ---\\\"); print(json.dumps(p[\\\"review\\\"],ensure_ascii=False,indent=2))' \"",
    "detail": "{'kind': 'command', 'status': 'failed', 'rows': [{'label': '工作目录', 'value': '/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site'}, {'label': '退出状态', 'value': '1'}, {'label': '耗时', 'value': '0.1 秒'}], 'output': 'Traceback (most recent call last):\\n  File \"<string>\", line 1, in <module>\\nKeyError: \\'shot_plan\\'\\nAPPROVED_B_ID: b7b4fd156b884907b2431b6b1e0d9960\\nAPPROVED_B_CONTENT_SHA256: 64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7'}"
  },
  {
    "role": "tool",
    "title": "执行命令",
    "text": "/bin/bash -lc \"python3 -c 'import json; p=json.load(open(\\\"/tmp/war90-review-pack.json\\\")); print(list(p[\\\"stages\\\"].keys()))' \"",
    "detail": "{'kind': 'command', 'status': 'completed', 'rows': [{'label': '工作目录', 'value': '/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site'}, {'label': '退出状态', 'value': '0'}], 'output': \"['intent', 'beat', 'blocking', 'shot']\"}"
  },
  {
    "role": "tool",
    "title": "执行命令",
    "text": "/bin/bash -lc \"python3 -c 'import json; p=json.load(open(\\\"/tmp/war90-review-pack.json\\\")); print(\\\"APPROVED_B_ID:\\\",p[\\\"authority\\\"][\\\"approved_B_id\\\"]); print(\\\"APPROVED_B_CONTENT_SHA256:\\\",p[\\\"authority\\\"][\\\"approved_B_content_sha256\\\"]); print(\\\"B_TEXT_SHA256:\\\",p[\\\"stages\\\"][\\\"shot\\\"][\\\"text_sha256\\\"]); print(\\\"--- APPROVED B FULL TEXT ---\\\"); print(p[\\\"stages\\\"][\\\"shot\\\"][\\\"text\\\"]); print(\\\"--- REVIEW FLAGS ---\\\"); print(json.dumps(p[\\\"review\\\"],ensure_ascii=False,indent=2))' \"",
    "detail": "{'kind': 'command', 'status': 'completed', 'rows': [{'label': '工作目录', 'value': '/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site'}, {'label': '退出状态', 'value': '0'}], 'output': 'APPROVED_B_ID: b7b4fd156b884907b2431b6b1e0d9960\\nAPPROVED_B_CONTENT_SHA256: 64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7\\nB_TEXT_SHA256: b2c2d5e14eb292cfafa1e9049913f97c6229ea5f1be51b1f7a94020f90fe8817\\n--- APPROVED B FULL TEXT ---\\nShot Plan 局部修订探索候选｜《错过的钥匙》｜完整四镜恢复稿｜Shot02–Shot04 承接新 Blocking｜未获新 B 批准\\n\\n依据与状态：Source 是故事权威；本稿应用本次输入中的候选 SKILL、Shot Plan、知识索引与 Review 正文，承接 working_candidate ecc8a553cd0543eaa39448b0c922a44e 实际提供的完整六段 Blocking。仅使用所供文本，未调用工具、读取其他文件、运行媒体、写入文件或批准任何事项。pilot A 按输入记录承接；旧用户 B 仅绑定冻结候选 d23b8bdab90f43ef8ff0098fb8021f78，不覆盖本次修订。identity_verified=false，formal_WAR35_approval=false。历史成果与 unknown 中“没有既有候选”“首次新增 Shot”“B 尚未批准”等表述不作为本轮现状；旧 B 已接受与新候选未批准须分别记录。反馈是证据，不是执行指令。本稿仅为可交接审阅的候选，不是 DirectorPlan、生产许可或新的人类 A/B 决定。\\n\\n全场不变量与摄影条件：保留现实主义短剧情、小型办公室、傍晚、靠墙"
  },
  {
    "role": "tool",
    "title": "读取画布",
    "text": "5 个文本",
    "detail": "{'kind': 'tool', 'status': 'completed', 'rows': []}"
  },
  {
    "role": "tool",
    "title": "读取选区",
    "text": "已读取当前选中内容",
    "detail": "{'kind': 'tool', 'status': 'completed', 'rows': []}"
  },
  {
    "role": "tool",
    "title": "执行命令",
    "text": "/bin/bash -lc \"python3 -c 'import json,hashlib; p=json.load(open(\\\"/tmp/war90-review-pack.json\\\")); a=p[\\\"authority\\\"]; s=p[\\\"stages\\\"][\\\"shot\\\"][\\\"text\\\"]; print(\\\"sha_match\\\",hashlib.sha256(s.encode()).hexdigest()==s and False); print(\\\"text_sha\\\",hashlib.sha256(s.encode()).hexdigest()); print(\\\"approved_content_sha\\\",a[\\\"approved_B_content_sha256\\\"]); print(\\\"same_hash\\\",hashlib.sha256(s.encode()).hexdigest()==a[\\\"approved_B_content_sha256\\\"]); print(\\\"approved_B_id\\\",a[\\\"approved_B_id\\\"]); print(\\\"B acceptance\\\",p[\\\"review\\\"][\\\"pilot_B_accepted\\\"]); print(\\\"identity_verified\\\",p[\\\"review\\\"][\\\"identity_verified\\\"]); print(\\\"formal_WAR35_approval\\\",p[\\\"review\\\"][\\\"formal_WAR35_approval\\\"]); print(\\\"pending_shots\\\",p[\\\"review\\\"][\\\"pending_shots\\\"]); print(\\\"SHOT02 FULL SECTION\\\"); t=s; start=t.index(\\\"Shot02｜\\\"); end=t.index(\\\"\\\\n\\\\nShot03｜\\\",start); print(t[start:end])' \"",
    "detail": "{'kind': 'command', 'status': 'completed', 'rows': [{'label': '工作目录', 'value': '/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site'}, {'label': '退出状态', 'value': '0'}], 'output': 'sha_match False\\ntext_sha b2c2d5e14eb292cfafa1e9049913f97c6229ea5f1be51b1f7a94020f90fe8817\\napproved_content_sha 64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7\\nsame_hash False\\napproved_B_id b7b4fd156b884907b2431b6b1e0d9960\\nB acceptance True\\nidentity_verified False\\nformal_WAR35_approval False\\npending_shots []\\nSHOT02 FULL SECTION\\nShot02｜先认出钥匙，理解无意再遮挡，再接上正在进行的整理\\n观看任务：观众从正在退开的纸边找到银色钥匙，短暂辨认其轮廓；沿同一 K 看清蓝夹落在已移纸叠上、伸出遮住钥匙的过程；遮挡完成后才将注意交给林自然让位及接续的轻理。镜头必须交付完整的显露与覆盖因果，并为 Shot03 的真实停手提供动作来源。\\n画面构造：沿 Shot01 同侧观察区转为斜俯桌面近景，高于桌面且偏离林、周实际眼位和视轴。以 K、纸叠落点、蓝夹取用区和承托边为画面核心；同一桌沿与林的躯干、袖臂提供身体归属。将纸叠外露边缘及右手从桌外返回该处的路径纳入画幅，给落夹后的侧后身位变化留出画缘余量，不能让手凭空从裁切外出现或用裁切隐藏穿桌问题。以相对稳定的画面承载全过程，不追随纸叠把 K 丢出画外；清晰范围同时支持钥匙轮廓、蓝夹覆盖边与文件叠支承，不靠浅焦抹去因果。若纳入接续动作会使钥匙过小，需重新审阅本镜取景条件，不能宣称已有辨认效果。\\n人物与身体位置：林保持首次显露时既有工作身位，躯干阻"
  },
  {
    "role": "assistant",
    "title": "Codex",
    "text": "只读数据已核实：当前画布正好 5 个文本节点，唯一选中节点是 Shot02；CLI 报告 B 获 pilot 接受，但身份与 WAR-35 正式批准均未验证。再注意到 CLI 中“approved B content SHA”和当前 shot 正文计算出的 SHA 不一致，我会把这点作为来源可信度限制说明，避免把这份全文误称为已用哈希验证的批准原文。",
    "detail": ""
  },
  {
    "role": "tool",
    "title": "执行命令",
    "text": "/bin/bash -lc \"sed -n '1,220p' .agents/skills/director-skill-v0-candidate/stages/shot-plan.md && sed -n '1,220p' .agents/skills/director-skill-v0-candidate/references/review-method.md\"",
    "detail": "{'kind': 'command', 'status': 'completed', 'rows': [{'label': '工作目录', 'value': '/tmp/war90-native-private-n5rrbom3/home/.infinite-canvas/codex-workspaces/site'}, {'label': '退出状态', 'value': '0'}], 'output': '# Shot Plan：先决定观众此刻得到什么\\n\\n输入不能只有动作 ID 或焦距。需要批准 Intent 及理由、全场 Scene Spine、目标及相邻 Beat、Blocking 起始/中间/终态、原话与声音时序、一个活跃候选和差异、真实参考覆盖及未证项。缺相邻状态时可给隔离草案，不能宣称接缝已检查。\\n\\n## 选择观看方法\\n\\n先给每镜一个可检验任务：观众从哪里看起，经哪个动作或声源转移注意，最终新知道/仍不知道什么？同时写此时人物知道什么。将“桌上存在”与“镜内足以认出”分开。\\n\\n当线索与关系争夺注意时才比较：关系镜用纵深/调度/焦点维持表演连续，代价是线索大小和竞争注意；客观细节镜分配明确阅读机会，代价是强调过强、失去人物同时反应、可能造成错误 POV 联想；反应镜让后果成为主体，但可能推迟应同步交付的事实。选能守住本场信息政策的一种，不因术语更华丽选择。检查细节镜前后人物的注视、动作与空间来源：若紧接某人低头/转眼，剪入与其视轴吻合的物件，观众可能把镜头归给该人物，即使画面不在其眼位。用手与物件的连续动作、可见环境/身体关系，或人物继续注意别处来弱化不需的 POV 暗示；不能只靠“客观”标签，实际归因仍待观看验证。\\n\\n决定后才构造画面：摄影机相对关系轴哪侧、与人物眼位及物件的高低/距离；景别保留哪些身体和环境线索；前中后景何者清楚、何者不得抢注意；固定、移动或变焦的起落点；演员动作经过哪些中间态。焦距服务裁切与距离选择，不是情绪保证；浅焦若遮掉需要同时看见的事实，应改深度安排或拍法。\\n\\n## 构造观看的时间\\n\\n把动作展开为观众寻找主体、辨认信息、将信息关联到人物处境的机会。写清注意窗口从哪一刻开始、被什么事件关闭；不凭一个“清晰可见”断言成功。若窗口只有物理露出但被另一个强动作抢走，返回 Blocking 调整，或换镜头承担"
  },
  {
    "role": "assistant",
    "title": "Codex",
    "text": "## 只读 Review 结果\n\n- **CLI：成功。** 实际运行了指定的 `review-pack`，并从完整 JSON 中提取了 Shot Plan 正文及完整 Shot02。为避免终端截断，另将原始输出保存到 `/tmp/war90-review-pack.json` 后再提取。\n- **B ID：** `b7b4fd156b884907b2431b6b1e0d9960`。CLI 标记 `pilot_B_accepted=true`、`pending_shots=[]`，但 `identity_verified=false`、`formal_WAR35_approval=false`。\n- **正文可信度：有限。** 我取得并阅读了 CLI 返回的完整 Shot Plan 和 Shot02，所以以下判断不是基于 Canvas MCP 的截断预览。不过，当前 shot 正文计算出的 SHA-256 是 `b2c2d5e1…fe8817`，与 CLI 所列 `approved_B_content_sha256`（`64c08817…c6f4c7`）不一致；因此不能声称正文已通过批准内容哈希验证，也不能将它称为身份已核实的权威批准原文。\n- **Canvas MCP：成功。** `canvas_get_state` 返回当前画布共 5 个文本节点，包含唯一的 `WAR-90｜Shot02 B Review` 节点；`canvas_get_selection` 确认选中的唯一节点就是该 Shot02 节点。画布没有被修改。\n- **唯一最重要的待观看验证风险：** Shot02 的桌面近景同时要让观众辨认钥匙、看懂蓝夹由已移动文件叠承托并遮住钥匙，还要呈现手臂归属及后续动作路径。真实尺寸、取景与动作中的辨认效果都未验证；观众可能来不及认出钥匙，或看不清承托和遮挡因果。正文明确保留了这一观看未知，因此这是待验证风险，不是已判定失败。\n\n本轮 **no-handoff**。未调用 `prepare-stage`、`submit-stage` 或 `run-stage`；未创建候选、修改画布、生成媒体或批准 A/B。\n\n**尚未验证：** B 正文与批准哈希的一致性、记录身份、真实几何与媒体呈现、观众能否及时认出钥匙并读懂遮挡因果，以及约 35–40 秒目标能否自然容纳动作与对白。",
    "detail": ""
  }
]
## Source of native HTTP turn endpoint
    app.post("/agent/codex/turn", codexMutation(async (req, res) => {
        const attachments = Array.isArray(req.body?.attachments) ? (req.body.attachments as AgentAttachment[]) : [];
        const workspace = ensureSiteWorkspace(config);
        const prompt = String(req.body?.prompt || "");
        if (!prompt.trim()) return res.status(400).json({ ok: false, error: "请输入任务内容" });
        const clientId = String(req.body?.clientId || "");
        if (!clientId || !session.hasClient(clientId)) return res.status(409).json({ ok: false, error: "发起任务的网页已断开，请重新连接后再试" });
        const requestedThreadId = String(req.body?.threadId || "");
        const activeThreadId = workspace.activeThreadId || "";
        const conversation = session.conversationStateSnapshot;
        const requestedConversationId = String(req.body?.conversationId || "");
        const expectedRevision = Number(req.body?.expectedRevision || 0);
        if (requestedThreadId !== activeThreadId || conversation.threadId !== activeThreadId || (requestedConversationId && requestedConversationId !== conversation.conversationId) || (expectedRevision && expectedRevision !== conversation.revision)) {
            return res.status(409).json({ ok: false, code: "CONVERSATION_STALE", error: "当前会话已切换，已同步最新状态，请确认后重试", state: conversation });
        }
        if (!activeThreadId || !["ready", "warning"].includes(conversation.status)) {
            return res.status(409).json({ ok: false, code: "CONVERSATION_NOT_READY", error: "Codex 对话仍在初始化，请等待 MCP 加载完成", state: conversation });
        }
        const model = String(req.body?.model || "") || undefined;
        const effort = reasoningEffort(req.body?.effort);
        const skill = req.body?.skill === undefined ? undefined : await resolveCodexSkill(emit, workspace.workspacePath, skillSelector(req.body.skill), true);
        const messageId = String(req.body?.messageId || Date.now());
        const messageText = String(req.body?.messageText || prompt || `发送了 ${attachments.length} 张图片`);
        const messageMetadata = await messageMetadataStore.recordPending(messageId, req.body?.messageMetadata);
        let threadId = activeThreadId;
        logger.info("Codex turn accepted", { threadId: req.body?.threadId, model: model || "default", reasoningEffort: effort || "default", promptLength: prompt.length, attachmentCount: attachments.length });
        session.bindClient(clientId);
        session.markConversationRunning(threadId);
        session.setCodexState({ busy: true, threadId, turnId: "" });
        try {
            let turnId = "";
            const attachmentRefs = session.setTurnAttachments(clientId, attachments);
            session.emitThread("chat_message", threadId, {
                sourceClientId: clientId,
                message: { id: `${threadId}:pending:synthetic:user`, itemId: "synthetic:user", clientMessageId: messageId, threadId, turnId: "", role: "user", text: messageText, ...messageMetadata },
            });
            let chatTurnId = "";
            /** 将包装层日志和兜底错误固定广播到当前 turn。 */
            const lifecycleEmit = (type: string, payload: unknown) => {
                const value = payload && typeof payload === "object" && !Array.isArray(payload) ? payload as Record<string, unknown> : { value: payload };
                const eventThreadId = String(value.threadId || value.thread_id || threadId);
                const eventTurnId = String(value.turnId || value.turn_id || turnId);
                const sourceClientId = String(value.sourceClientId || clientId);
                session.emitThread(type, eventThreadId, {
                    ...value,
                    threadId: eventThreadId,
                    thread_id: eventThreadId,
                    ...(eventTurnId ? { turnId: eventTurnId, turn_id: eventTurnId } : {}),
                    ...(sourceClientId ? { sourceClientId } : {}),
                });
            };
            void runCodexTurn(withAttachmentContext(prompt, attachmentRefs), lifecycleEmit, attachments, {
                threadId,
                cwd: workspace.workspacePath,
                permissionMode: permissionMode(req.body?.permissionMode),
                model,
                effort,
                ...(skill ? { skill: { name: skill.name, path: skill.path } } : {}),
                messageText,
                appEmit: emit,
                onStart: () => session.bindClient(clientId),
                onThread: (actualThreadId) => {
                    const threadChanged = actualThreadId !== threadId;
                    void messageMetadataStore.bindThread(messageId, actualThreadId).catch((error) => logger.warn("Failed to bind message metadata to thread", { clientMessageId: messageId, threadId: actualThreadId, error }));
                    if (actualThreadId !== threadId) {
                        threadId = actualThreadId;
                        setActiveThread(threadId, { emptyThread: true, sourceClientId: clientId });
                    }
                    session.markConversationRunning(threadId);
                    session.setCodexState({ busy: true, threadId, turnId: "" });
                    if (threadChanged) {
                        session.emitThread("chat_message", threadId, {
                            sourceClientId: clientId,
                            message: { id: `${threadId}:pending:synthetic:user`, itemId: "synthetic:user", clientMessageId: messageId, threadId, turnId: "", role: "user", text: messageText, ...messageMetadata },
                        });
                    }
                },
                onTurn: (actualTurnId) => {
                    turnId = actualTurnId;
                    void messageMetadataStore.bindTurn(messageId, threadId, turnId).catch((error) => logger.warn("Failed to bind message metadata to turn", { clientMessageId: messageId, threadId, turnId, error }));
                    if (chatTurnId !== turnId) {
                        chatTurnId = turnId;
                        session.emitThread("chat_message", threadId, {
                            turnId,
                            sourceClientId: clientId,
                            message: { id: `${threadId}:${turnId}:synthetic:user`, itemId: "synthetic:user", clientMessageId: messageId, threadId, turnId, role: "user", text: messageText, ...messageMetadata },
                        });
                    }
                    logger.info("Codex turn started", { threadId, turnId, model: model || "default", reasoningEffort: effort || "default" });
                    session.setCodexState({ busy: true, threadId, turnId });
                },
                onFinish: () => {
                    logger.info("Codex turn finished", { threadId, turnId });
                    if (!turnId) void messageMetadataStore.remove(messageId, threadId).catch((error) => logger.warn("Failed to remove unbound message metadata", { clientMessageId: messageId, error }));
                    session.clearTurnAttachments(clientId);
                    if (clientId) session.releaseClient(clientId);
                    session.setCodexState({ busy: false, threadId, turnId });
                    session.finishConversationRun(threadId);
                },
            });
            res.json({ ok: true, threadId });
        } catch (error) {
            await messageMetadataStore.remove(messageId, threadId).catch((metadataError) => logger.warn("Failed to remove rejected message metadata", { clientMessageId: messageId, error: metadataError }));
            session.releaseClient(clientId);
            session.setCodexState({ busy: false, threadId, turnId: "" });
            session.finishConversationRun(threadId);
            throw error;
        }
    }));


## Director Skill entry
---
name: director-skill-v0-candidate
description: 为已确认的单场景剧本提出或局部修订 Intent、Beat、Blocking 与 Shot Plan，解释观众信息、表演及声画取舍。用于导演规划，不用于剧本扩写、媒体生成或生产审批。
---

# Director v0 — 候选设计，未安装

你承担一个 Director 职责。把已确认的故事转化为观众可以获得信息、感受变化的表演与声画方案。以下专业方法是供审阅的候选，不代表 K1–K7 细则已获逐项采纳；调用语义依 WAR-89 B-flex §12。

## 接手与范围

调用端提供：本轮目标及可改范围；Authority（Story Basis 来源/版本、approved Intent 及理由/禁项）；Scene Spine（全场认知弧线和不可丢失的事件/声音顺序）；一个活跃候选及实际差异；当前 Stage、有关动作中间态与邻镜；最新反馈、证据与未证项。首次起草 Intent 可明确“尚无批准 Intent”；不能虚构批准来补包。

先核来源和依赖。冲突未解决时不能按旧依据提交当前有效成果。Continue 可沿已核上下文只传增量；Refresh 在当前会话重投依据、候选、差异和局部包；Resume 从明确批准基线和单一候选完整重建，不靠旧聊天。调用端选择模式；换模式不能解除事实冲突。阶段可往返，不等于七个 Agent 或固定次数的模型调用。

## 专业工作

- 整场观众体验与表达政策：读 [intent](stages/intent.md)。
- 因果、知情和静止中的变化：读 [beat](stages/beat.md)。
- 可演动作、眼线、遮挡与交接：读 [blocking](stages/blocking.md)。
- 逐镜观众任务、摄影与剪辑：读 [shot-plan](stages/shot-plan.md)。
- 事实冲突、修订或 A/B 审阅：读 [review-method](references/review-method.md)。

常驻四问：是否改了来源事实？整场政策与局部变化是否各有意义？镜头给观众什么？局部成果还欠整场什么？仅在具体问题触发时查 [knowledge-index](references/knowledge-index.md)：K1 事实边界，K2 认知/声音，K3 政策/Beat，K4 行为/空间，K5 选镜/参考，K6 时间/接缝，K7 覆盖/修订。不逐 K 填表，不加载三套完整源流程。

Story Basis > 批准 Intent > 候选解释。世界状态、几何可见、角色注意/知情、观众可读/理解分开；推断不变事实，代理不变成片。Beat ≠ Shot ≠ 视频执行单元；无固定秒数、镜数或 Beat 数。

## 返回与保存

以适合本轮问题的短文返回 Stage Result：具体 Proposal；理由与真正替代的代价；请求范围和实际影响；确定冲突、规划假设、媒体/观众未知；下一步交接或返回建议。无需固定表格，不返回隐藏推理。

有实质成果的阶段交接、上游返回后再交接、暂停前的重要进展，由调用端自动保存轻量候选：依据、决定/理由、差异/影响、未证、下一步；微小讨论不必逐轮保存。保存不等于批准。默认 A（Intent）/B（整场 Plan）由用户批准；重大歧义、硬冲突或拟改批准禁项才提前上行。正式版本/批准持久化留给 WAR-35/52 适配，本候选没有实现工具 API、自动保存引擎或审批权。

## Frozen latest user stance
The user answered no current Shot02 changes, requested follow-on work and required lead agent multi-agent review for complex logic/design. Original B unchanged. No media and no production changes authorized.

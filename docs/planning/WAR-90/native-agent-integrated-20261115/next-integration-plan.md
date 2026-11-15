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

# WAR-90｜Canvas 主入口接入预检与 Chat 第二入口边界（2026-11-16）

## 当前阶段与给人看的测试目的

**当前阶段**：已确认双入口架构后的 A 主入口接入准备，不是生产部署。

**给人看的测试目的**：验证 Canvas Agent 是否发现完整的七文件 Director Skill，如何在不改项目权威原件的情况下升级/回退；确认 Chat 半自动调用现有 Canvas Agent API 时如何避免误选多浏览器画布。Eric 独立 Codex 是备用，不是 Chat 日常必经 Agent。

## 观察与实测结果

**正式工作空间与服务现状**：Eric 的 Canvas Agent 用户配置的 workspace 是 /home/sean/.infinite-canvas/codex-workspaces/canvas-agent，而不等于默认初装的 site。项目七文件候选在 docs/planning/WAR-89/director-skill-v0-candidate，当前正式 workspace 未安装该候选。正式配置已将 codegraph 和 hindsight 的 mcpOverrides 置为 false；这只能证明配置，尚未验收正式线程的实际工具和 MCP 拒绝生效。检查时 canvas-lab-agent.service 与 canvas-lab-web.service 都为 inactive，本轮不擅自启动。

**真实原生 Skill 生命周期**：通过干净临时 HOME/CODEX_HOME、无认证文件和模型调用的 Codex app-server stdio 协议执行三次 skills/list(forceReload)。先装入七文件包，原生发现唯一 enabled Skill，错误为零；12 处相对 Markdown 引用全部有效。只在临时副本改动 shot-plan 阶段卡，刷新后仍能发现；回退旧版后七文件 SHA 全部恢复。证据 codex-skill-lifecycle-result.json，复现脚本 codex_skill_discovery_probe.py。此测试没有调用 Canvas Agent HTTP、没有生成或更改画布。单独 HTTP 测试受 Eric localhost 连接超时影响未能完成，不能冒称通过；失败尝试源码 isolated_skill_lifecycle.py 留作定位。

**七文件版本限制**：Canvas Agent 的 SkillStore.create/update 主要管理 SKILL.md 和可选 agents/openai.yaml；其 revision() 也只由这两个文件的内容算出，不能保证 stages/ 和 references/ 没有变更。Codex Skill 列表的 enabled 与 path 同样不是七文件的内容签名。建议正式安装统一由原件复制的完整文件包管理，冻结七份 SHA/相对链接/对应 Git 版本；先经审阅将标注“候选，未安装”的内容确定为发布版本。禁用运行中的专业 turn 后才进行更换/回退，不要误认为两次目录 rename 是一个原子事务，也不能假定活动 thread 自动刷新知识。完整包安装不应只靠 UI 粘贴 SKILL.md。

**现有 Canvas API 的目标归属风险**：/api/tools 目前不接受带原子校验的 clientId/expectedProjectId 写入目标。CanvasSession.targetClientId 选择正在执行的 Codex turn 的 boundClientId，或者最近激活的 activeClientId。/canvas/activate 只是变更焦点，不形成事务；多个浏览器窗口、其他 turn、重新连接都可能改变目标。当前 Chat 无法通过简单的工具参数锁定一个画布。

**Chat 只读前检**：新增纯数据函数 chat_read_preflight.verify（不发网络请求、不写 Canvas）。该函数只比较调用者提供的 health/state/selection/Runtime 字段，要求单客户端、Codex 不忙、显式 project/client/node/Shot ID 分别一致、B ID 有效、Source/Shot SHA 格式有效且与传入完整原文的实际 UTF-8 SHA 相同。结果仅为提供的标识字段内部一致（provided_identifiers_consistent），无论如何 can_write=false。没有读取时间或快照修订，也不验证选中 Node 实际映射到该 Shot、selection 与 state 同源/同一时刻、内容来自真实批准 B、真实审批身份或检查之后的竞态。18 项离线测试通过（含原来双方缺失 SHA 误放行的反例、无效版本字段、错配正文、错误 Node/Shot 映射的显式未知）。源码与测试在 chat_read_preflight.py、test_chat_read_preflight.py。

**既有 Canvas Agent 单元回归**：对 Skills Store、Codex Client、CanvasSession 三个相关模块实际运行 84 项测试，84/84 通过。测试日志 native-agent-targeted-tests.log。未修改正式 Canvas Agent 源码和服务。

## 两入口最小权限与归属矩阵

| 能力 | A · Canvas 主入口 | B · Chat 协作入口 | 当前边界 |
| --- | --- | --- | --- |
| 导演知识 | 原生 Codex 加载可发现的 7 文件 Director Skill | DCR 读取 Eric 同一原件 | 主入口正式安装未执行，必须对齐完整包 SHA |
| 只读 B 文案 | Runtime review-shot/review-pack | 相同 Runtime CLI | 只读 CLI 已验证，新增 review-shot 的原生 Agent 复测未执行 |
| 画布和选区 | 内置 infinite-canvas MCP；turn 绑定客户端 | 现有 Agent HTTP /api/tools；单客户端且显式项目/选区 | 已有隔离画布各自读测，当前不在正式画布运行 |
| 节点写入 | 必须有用户授权、实际工具权限及版本校验 | 不由只读 preflight 授权；须用户明确确认唯一画布 | Chat HTTP 缺少原子 client/project 绑定，不能声称无竞态 |
| prepare/submit | 当前专业 Agent 经 Runtime 保存候选，不让 Runtime 启动第二 Agent | 相同 CLI，保留 Chat 意见来源 | 真实修改/B 复审未执行 |
| A/B 用户批准 | 真人显式确认，不许模型自签 | 同一规则，记录 Chat 输入来源 | 正式身份核验未实现 |
| 媒体/ComfyUI/H3 | 另行明确授权 | 本轮不调用 | 未测试 |
| 并发 | 原生 busy 与 Runtime 文件锁是局部门禁 | 多窗口/忙碌/不一致拒绝继续 | 没有跨入口统一 CAS 和事务 |

重要：Canvas Agent 代码中的 default_tools_approval_mode=approve 不等于每次 MCP 工具调用都会请求真人允许。之前主审已明确当前 codex_approval 事件不能直接作为 MCP 工具执行拒绝的证明，正式工具授权须单独核证。

## 正式安装提案（未执行）

1. 用户确认安装与启动时机后，确认当前真实工作空间、无活动任务、目标画布归属和现有 Skill 安装状态；不得默认 site、不得覆盖同名目录。
2. 将七文件原件做独立 staged 副本，扫描引用和逐文件 SHA，与冻结 Git 版本比对，保存来源。部署到当前工作空间的普通目录，避免符号链接；旧版本保留可恢复备份。
3. 在新的原生线程中强制重新发现 Skill，并验证七文件实际内容与权限范围。失败恢复旧目录，保留失败记录，不篡改已有候选/B。
4. 先以隔离画布执行只读 review-shot 与 Canvas 选区一致性测试，再按授权决定是否开放正式操作。Chat 路径先读并核对 project/client/selection/B/Source/Shot，检查失败立即停；多客户端或 Codex 忙碌不写入。
5. 跨入口原子路由、revision/CAS、正式 UI 映射留 WAR-35/WAR-37；WAR-90 不复制第二套存储、审批或导演 Agent。

**独立审阅与定向修复收口（2026-11-16）**：首轮相互隔离的两名 Reviewer + 一名主审裁定 targeted-revision，指出 Chat 纯数据检查在 B/SHA 双方均缺失时可能误放行，以及 Node→Shot 和“新近快照”声明超出证据。修正为校验 B/SHA 格式、Source/Shot 全文 SHA，返回 provided_identifiers_consistent，明确未知、记录 clientId，并固定 can_write=false。随后 18/18 测试及真实 B 投影配合明确标注为模拟的画布状态验证通过；另由一名独立 Reviewer + 一名主审裁定 accept（仅针对离线定向修复）。原始冻结审阅见 review/，修复后的复审见 review-gate-fix/，二者不互相覆盖。

**Chat HTTP 写入验收明确阻断**：经 /api/tools 的目标安全写入当前为 BLOCK。单客户端、codexBusy 检查、人工确认及本纯数据 Gate 的成功，均不能解除缺少请求级 client/project 原子绑定的风险；需未来有服务端约束与真实端到端验证才能准入，不以当前规程替代权限机制。

**本阶段验收状态**：七文件 Skill 原生发现、临时升级、回退通过；Chat 输入标识只读前检离线测试通过；正式服务没有启动、生产 Skill 没有安装、MCP 真实审批拒绝和双入口真写入都未通过验收。没有新 Shot02 修改意见，未生成候选、不生成媒体、不自签 B。

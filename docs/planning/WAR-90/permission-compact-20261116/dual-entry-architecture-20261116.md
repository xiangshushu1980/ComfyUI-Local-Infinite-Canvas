# Canvas Lab｜Director Skill 双入口执行决策（2026-11-16）

决策来源：用户明确要求 **Eric 上 Canvas Agent 为主力，ChatGPT 可以半自动参与，Eric 独立 Codex 为备用**。

## 目标与适用边界

Canvas Lab 的真实创作入口有两个，复用同一导演方法与工程工具，而非为 Chat 与 Canvas 分别维护两套导演引擎。每次具体修订由一个执行者负责专业判断，外围独立 Reviewer 只负责设计/代码/导演产物的质量检查。单 Agent 是一次任务的执行拓扑，不是限制用户只有一个入口。

### 路径 A：主力，Eric Canvas Agent（画布内置 Codex）

- 用户在 Canvas Lab 中使用 @画布元素、选区、节点引用与对话；Canvas Agent 自己加载可发现的 Director Skill（正式安装仍未批准），按阶段调用本地 Director Runtime CLI 的只读、准备与提交命令，并直接通过既有 infinite-canvas MCP 读写所连接的画布。
- 已在**隔离** Canvas Agent 真实验证 Skill 发现/选择、原生 Codex turn、按需读 Shot Plan 知识、Runtime review-pack 和 Canvas MCP 双读取，结论是只读 no-handoff。尚未在现有正式 Canvas Agent 上安装该候选 Skill；媒体、真实候选写入、人类 B 重审未证。
- Canvas Agent 会根据启动环境继承 CODEX_HOME 配置。独立对话不等于配置隔离；正式 Agent 启用状态不能依据一次隔离 smoke 的全局配置继承现象判断。

### 路径 B：协作，ChatGPT → Eric

- ChatGPT 负责讨论设计、召集外围审阅 Agent、查阅 Eric 的本地权威 Markdown、组织半自动审阅和明确授权范围的画布操作。
- ChatGPT 通过 DCR 显式访问 Eric；可以读取适用 Director Skill 文件，执行**同一** Director Runtime CLI，必要时通过**现有** Canvas Agent API 控制已确认的画布，或将一段受控任务交给 Canvas Agent 原生对话。没有为 Chat 新建长期运行的 Director Agent 或专门的 HTTP 桥接服务。
- Chat **不能自动将远端 Eric Skill/MCP 当成本会话的内建工具**：实际需要显式读取 Skill 文件、经远程命令执行 CLI 或通过已有 API 操作画布。Chat 路径的 API 实验曾在独立测试画布验证节点创建、选区、差异回显；完整的真实用户修改与 B 再批准仍未测。
- Chat 没有 Canvas UI 内置 @ 元素交互语义；如需访问元素，必须显式核对项目/节点/选区 ID、B/Source/Shot 版本及实际 Canvas Agent 连接归属。不能凭 Chat 文本里的“@某元素”假设已解析到当前画布，也不能自动回退到未知的最近画布。

### 备用执行端：Eric 独立 Codex

- 仅用于画布内 Agent 不可用、自动化批处理、独立验证/代码审阅等情况；不作为主力和 Chat 的日常必经中转。
- 备用执行时仍指向同一套 Skill、Runtime CLI 和被授权的 Canvas Agent 工具；不用自己的另一本专业规范或独立 DirectorPlan 状态。
- 多 Reviewer + 主审阅 Agent 是**外围质量控制**，不加入每次导演运行的调用链，也不代签用户 A/B。

## 共享的单套能力与数据

1. **Director Skill 权威**：Eric 项目中的七文件专业 Skill；Canvas Agent 安装的是可发现副本/引用，Chat 按阶段读取原件。正式安装需七文件 SHA 清单、相对路径可用性与更新回退检查，不能让两入口使用不一致版本。
2. **Director Runtime CLI**：同一实现、同一试点权限及来源校验；只读视图不生成新候选，prepare/submit 也不自行启动专业模型。未来正式持久化归 WAR-35，不在此复制第二套数据契约。
3. **Canvas 工具**：Eric 已有 Canvas Agent 的 infinite-canvas MCP / HTTP 工具；Chat 用 HTTP/API 协作并不意味着它拥有 UI 内置 Codex 的一切上下文，Canvas 内置 Agent 更适合直接消化 @引用和画布选择。
4. **用户批准与材料**：Eric 本地 Markdown/Runtime 冻结证据为权威，Linear 是索引与状态；Canvas 文本节点是展示投影，不是最终的 B 授权记录。Chat 审阅意见、Canvas UI 反馈要保留各自真实来源，不得互相冒充。

## 并发与操作边界（当前是规程，尚非已实现锁机制）

- **同一画布的一次修改只由一个主控路径执行**；先核项目 ID、实际连接的 clientId、当前选区与 B/Source/Shot SHA。Chat 不应在 Canvas Agent 忙于同一画布时并发提交修订。冲突或版本变化时停止，重新读状态并获取人工确认。
- 现有 Canvas Agent 的 busy 状态与 Runtime 文件锁只覆盖各自局部操作，**不能声称已实现跨 Chat/Canvas 的通用编辑锁、事务或 revision/CAS**。这些工程语义不在 WAR-90 偷偷落地，后续与 WAR-35/WAR-37 对齐。
- 不得凭一个随机项目名、最近画布或截断节点预览自动提交修改；要从实际 UI 选区/@引用或受用户确认的精确 ID 发起。
- 不从本轮实验向生产安装技能、切换服务、修改用户 Canvas、生成媒体或自动签 A/B。后续正式写操作必须明确授权及回滚范围。

## 当前真实验收（截至 2026-11-16）

- 路径 A 原生 Skill+Runtime+MCP **只读 PASS（有限）**；Codegraph/Hindsight 在隔离试验中的意外暴露，导致正式工具隔离**未验收**。
- 路径 B Chat→DCR→Canvas Agent API **独立测试画布读写/选区 PASS（有限）**；Chat 直接用 Skill 的完整专业修订及同一 Runtime 提交新 B **未验收**。
- 备用独立 Codex→Skill+CLI+MCP **只读 PASS（有限）**。
- Runtime 新增的目标 Shot 只读 compact 视图为试点能力，尚无原生 Agent 复测。生产集成仍未执行；真实 Shot02 用户表示暂时没有修改意见，不得伪造修订候选。
- 用户真正的修订→邻镜复检→Canvas 差异→再次人审 B **未验收**，按真实需求择期测试，不人为制造需求。

## 下一步优先级

1. 在 WAR-90 收口当前的 Runtime compact Shot 只读视图与多 Agent 代码审阅，不扩大到新 schema。
2. 独立核验 Codec/Codex 配置来源（空 CODEX_HOME 与用户环境已对照），在已有 Canvas Agent 工具审批路径上找到可验证的拒绝/拒执行证据；如果 MCP 工具默认自动通过且客户端没有可拒绝事件，记录**当前通路无法证明拒绝**，不为实验擅改生产权限机制。
3. 形成路径 A 与 B 的共同运行说明与最小权限矩阵；确认正式 Skill 安装/新会话/回滚的实际边界后，再让用户决定何时在正式 Canvas 使用。
4. 真正有用户修改要求时，选择一个入口完成隔离的完整改动闭环，外围多 Agent 审阅结论只能提供质量建议，不得代替用户 B 审批。

用户的主次排序属于已确认决策，不重新将 Chat 设为专业 Agent 的必经路由。

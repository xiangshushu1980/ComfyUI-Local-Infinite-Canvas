# WAR-90｜Canvas Shot 反馈回传 → Director 候选 → Canvas 差异展示

2026-11-15｜Eric｜**本轮工程传输闭环 PASS；真人反馈和真实 Director 修订尚未发生，不能按完整人机闭环验收。**

## 目标与边界

按用户确认的优先级，先保证 **Canvas 选定 Shot → 收集具体修改文本 → 绑定有效 B / Source / Shot 版本 → 独立 Resume 候选 → 邻镜复检 → 差异回显 → 真人重审** 的流程正确性。性能与 Continue/Refresh 延期。当前 WAR-90 的试点 B 是有效文本导演成果，不是正式 WAR-35 数据契约，也没有媒体/几何/观众效果批准。

- 机器 Eric，项目 `/home/sean/projects/canvas-lab`。使用现有实验 `review-pack`、`Pilot.run` 与 Canvas Agent 自带的 `canvas_get_state`、`canvas_create_text_nodes`、`canvas_select_nodes`、`canvas_get_selection`。**没有修改生产 Canvas/Agent/API、正式 WAR-35/52、原始导演 Skill、剧本、用户真实画布，也没有运行 H3/ComfyUI/Blender。**
- 既有已批准 B：`docs/planning/WAR-90/pilot-D-local-repair-v2/`，candidate ID `b7b4fd156b884907b2431b6b1e0d9960`、`state.json` SHA256 `23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7`（执行后仍相同）。
- 隔离测试派生候选：`docs/planning/WAR-90/pilot-D-canvas-feedback-demo-20261115/`，其结果是 **fake generator** 仅添加一行醒目标记，专用于检验信息传递和非目标正文锁定，**不是专业导演修订**。本派生工作区仍为 `awaiting-human-B` 且 `pilot_B=null`；原批准版不受影响。

## 已实现的局部适配

`feedback_bridge.py` 是**实验传输适配**，不是 WAR-35 Schema，也不是 Canvas 正式插件：

1. 每次先调用 `Pilot.review_packet()` 重新验证已批准 B、Source/Skill/内容哈希和审阅证据（不信任 Canvas 上的文本卡为权威）。
2. 创建用于该测试画布的 `catalog`：每个真实 `node_id` 必须与 `ShotNN`、镜头正文 SHA、批准 B ID/内容 SHA、Source SHA、画布 `project_id` 严格绑定。节点必须存在且唯一；Canvas API 会截断长节点内容，所以只能验证可见前缀，其**全文仍以 Director 工作区为权威**。
3. `canvas_get_selection` 只允许**一个**已绑定的 Shot，且当前显示前缀仍含原始 Shot ID / B ID；未绑定节点、旧版本、被修改的显示卡、多重选中均拒绝。
4. `capture_feedback` 额外接受一条外部文本，并核对非空、大小、源/版本绑定；输出 `status=revision-request-only`，`actor_identity_verified=false`，`human_B_decision=false`。仅允许 `origin=synthetic-test` 或 `external-user-unverified`，不声明身份认证通过。
5. `clone_for_revision` 核对实际源 B 不变且符合检验包，将旧批准 B **字节一致**复制至一个新的 WAR-90 工作区；绝不覆盖已存在工作区；从该克隆按单 Shot 目标构造可信 `Resume` 范围输入。用户要求若涉及 Blocking/Beat/Source，应报告上游需求并停止伪装成纯 Shot 变更。
6. 真实 Director 调用仍需**在收到真实反馈后另外执行** `Pilot.run(stage='shot', mode='resume', targets=[...])`。本轮为避免伪造专业结果，`fake_director_for_transport_only` 仅插入明确测试标记，用运行壳验证实际 `candidate-saved` 和未批准状态。
7. `compare_local_revision` 只对已保存的活动候选做只读差异分析，要求实际改变仅目标 Shot，且 `pilot_B=null`，输出待复检邻镜和 `status=awaiting-real-user-B-review`；不得将测试稿和用户批准混为一谈。

## 真实 Canvas API + 合成内容端到端测试

执行 `smoke_feedback_loop.py`；前提：仅当本机 Canvas Agent 健康且**没有任何已连接用户画布**时执行，以独立临时 headless Chromium profile 打开全新空白 Canvas，操作结束自动清理浏览器。真实 API 交互实际完成：

1. 新画布 1 个 B 说明节点 + 4 个真实 Shot 预览节点，读回 **5 个**；
2. Agent `canvas_select_nodes` 真实选择 Shot02，并由 `canvas_get_selection` 读回唯一相同 ID；
3. 用**明显标记的合成文本**捕获 Shot02 的请求，catalog 绑定正确；没有收到真人新意见；
4. 独立复制已经批准 B、使用 **fake generator（没有新 Codex/LLM 调用）**产生 Shot02 唯一差异；运行壳验证邻镜 `pending_shots=[Shot01, Shot02, Shot03]`，新候选仍未批准；
5. 通过 Agent 追加“synthetic feedback”和“synthetic diff — NOT APPROVED”两个真实文本节点，读回同一画布合计 **7 节点**；
6. 浏览器 URL 确认当前为临时画布，结束 Chrome profile 自动清理；Agent `clients=0`；
7. 原正式 B 工作区状态 SHA 保持 `23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7`，未进行 B 审批或任何媒体生成。

证据文件：`catalog.json`、`synthetic-feedback.json`、`prepared-workspace.json`、`synthetic-diff.json`、`loop-demo-result.json` 及执行日志。**注意：所记录的 Canvas project ID 属于已删除的临时浏览器 profile，不是仍可打开的用户画布。**

## 反例检查

独立测试 `test_feedback_bridge.py`：**6/6 测试通过**，覆盖：

- 正确 Shot ID/内容 SHA 与已批准 B/Source SHA；候选请求不能伪装成人类 B 决策；
- 旧版 B、被替换 Shot 文本哈希、缺失或重复映射；
- 画布项目错误、虚构选中 ID、单次多选、显示文本篡改、空反馈、虚假的身份来源；
- 反馈 SHA 修改、过期 B/Source、伪造 `human_B_decision=true`；
- 独立克隆的 fake 生成只改变 Shot02；Shot01/03/04 保持，邻镜标记、原 B 不变；
- 当生成器偷偷修改非目标 Shot01，运行壳隔离结果，批准基线不受污染。

原 WAR-90 运行壳全套 **37/37** 回归测试通过。合计 **43/43 自动化测试**，含原始运行壳与新适配层，不能因此宣称专业导演质量或真人闭环已通过。

## 已验证、未知和下次真实交互关口

**已验证的机制**：Canvas Agent 真实节点创建/读取/选中，目标及版本绑定、孤立的 Resume 工作区准备、受限候选写入、非目标修改隔离、邻镜待复检传播及将差异重新在真实临时画布上显示。

**未验证**：真人直接在 Canvas UI 提交编辑文本、真人身份认证；真实 Director 模型根据该新反馈作出专业判断（例如纯 Shot 还是需回 Blocking）、用户真实审阅候选/拒绝或批准；正式 `revision` 递增/CAS，WAR-35/52 typed 语义映射；编辑器长期持久化/跨用户并发、视频/观众效果。当前脚本不替代 WAR-37 的未来 UI/节点映射设计。

**下一步真实用户关口**：先获得用户针对一个具体 Shot 的**明确修改意见**（可以在 Chat 中先提供，随后再把 Canvas 原生反馈 UI 纳入 WAR-37）。用该意见和实际已批准 B 的最新 SHA 新建**非模拟**的隔离工作区，通过 Director Resume 产生候选，检查上游/邻镜，再在独立 Canvas 展示**真实**差异并停在真人 B 审阅。没有新用户意见时，不应让模拟指令驱动真实模型、也不应“自动批准”新 B。

跟踪：WAR-90 保持 In Progress，WAR-37 Backlog 负责真正的画布 UI 设计，WAR-89/35/52 原目标与版本约束不变。
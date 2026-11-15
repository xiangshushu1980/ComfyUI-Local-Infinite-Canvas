# WAR-90｜v0 会话简化决策与 Canvas Agent 独立画布联调

日期：2026-11-15｜工作机器：Eric｜**本轮实测通过第一层真实 Canvas Agent 文本展示 + 选镜；未完成真人反馈→Director 再修订的整轮交互。**

## 1. 用户确认的 v0 简化方案（取代 WAR-89 的会话策略实施优先级）

用户在本对话明确确认：先完成导演流程正确性、然后接入 Canvas Agent；不将上下文节省、推理时延或复杂自动会话模式作为前置目标。此决策仅调整 **v0 的实现优先级**，WAR-89 原 B-flex 多模式语义仍可作历史设计参考，不能假装所有模式都已经实现和验收。

| 项目 | v0 决定 | 现状 |
| --- | --- | --- |
| Agent 运行方式 | **一律从已核验权威状态构造 Resume 包**。不要求可靠持有上一模型会话 | WAR-90 运行壳已经 `Resume` 实用，`Continue`/`Refresh` 显式拒绝；本轮不改这一安全行为 |
| 会话优化 | 未来如确有价值，可增加 Continue/Refresh，但不能改变批准/Source/Review 权威边界 | **延期**，不能再作为 v0 联调阻塞项；性能不验收 |
| 版本并发 | **一个递增 `revision` + 检查期望版本相等（CAS）** 作为未来 Canvas typed DirectorPlan 的最小乐观并发控制 | **当前 WAR-90 尚无递增 revision 字段**；仅现有候选 UUID、状态摘要/内容 SHA、原子提交和文件锁已实现。正式 revision 字段和跨 Canvas 写入以 WAR-35 定稿契约为准，本轮不引入平行 Schema |
| 原权威保护 | Source/Skill SHA、候选和内容 SHA、A/B 批准证据、阶段完整文本与局部邻镜检查 | **全部保留**，不因版本号而删除 |
| 工程证据 | 历史候选和批准快照保持不可变、失败候选隔离、未证风险保留 | **全部保留**；历史资料不默认整批加载到模型 |
| Canvas 连接 | 从试验运行壳只读 `review-pack` 取当前已批准 B；显示时绑定来源/批准版本；反馈只作为导演修订请求，不代表用户批准 | 本轮已真实测试文本展示与选择 Shot02；尚未完成真实用户反馈触发 Director 修改 |

若 `source/approvedB/active candidate` 的任何版本或哈希不一致，**阻止覆盖并重新读取**，而不是切换模型会话绕开不一致。不能用一个递增 revision 代替内容 SHA 和人工批准。当前运行壳的 `Resume` 恢复、审批、安全检查继续是 v0 基线，无须为了消除“模式复杂性”重写既有验证代码。

## 2. Eric 上的真实 Canvas Agent 调用范围

- 从 `docs/planning/WAR-90/pilot-D-local-repair-v2` 的**已批准新 B**（`b7b4fd156b884907b2431b6b1e0d9960`）实时执行运行壳 `review-pack`；不是预先硬编码四镜文字。外部审批证据、来源/候选 SHA 仍由运行壳检验。
- 检查 Canvas Agent HTTP `/health` 为正常，且启动前 `clients=0`、`hasCanvas=false`；如已有连接则主动拒绝，避免误写用户工作画布。
- 启动 **临时、隔离 headless Chromium profile**，打开 `/canvas?mode=new`。通过本地 DevTools 通道短暂传入 Agent URL/token 以完成自动连接；**token 不写入命令参数、报告、Git 或聊天**。所有节点只产生在该临时浏览器的新画布项目里，结束后关闭浏览器、清理临时 profile。
- 通过 Agent 自己的 `POST /api/tools` 调用 `canvas_get_state` 确认一个真正的新空画布；用 `canvas_create_text_nodes` 创建五个文本节点：1 个只读说明节点 + Shot01–04 四镜正文（均带试点 B ID、B 内容 SHA、Source SHA、Shot SHA、未证标志）；再读回并核对项目 ID/数量/标题/各节点前缀。
- 通过 Agent `canvas_select_nodes` **实际选中 Shot02 节点**；通过 `canvas_get_selection` 返回该节点 ID 和标题，映射到 `Shot02` 的修订目标。这是自动化模拟用户选择；**没有人类通过 Canvas UI 进行真实反馈**。
- 通过只读的独立 `validated_feedback` 逻辑验证示例请求必须绑定 `approved_B_id`、`approved_B_content_sha256`、`source_sha256` 和现存的 Shot ID；一个合规的**模拟**问题通过前置检验，4 个过期/不存在/空白反例被拒绝。**没有向 Director 模型发送该反馈，没有创建新候选，也没有审批新 B**。
- Chromium 前端实际进入了私有项目 URL，页面能读到 WAR-90 审阅标题。返回的 `canvas_get_state` 对长文本节点的 metadata 只保留截断预览，因此本轮核对标题及内容前缀，未把返回数据错误表述为全量节点正文的逐字验证。
- 结束时私有浏览器关闭、Agent 客户端计数回到 **0**；未编辑用户真实画布，无 GPU/媒体生成/模型调用。

## 3. 本轮可重放证据与界限

- `smoke_canvas_agent.py`：在 Eric 机器实际连接本地 Agent 和隔离 Chromium 运行前述流程；若检测到其他已连接画布，直接中止而非抢占。
- `canvas-agent-smoke-result.json`：记录新测试项目 ID、5 个真实节点、Shot02 实际选择/返回、命中 B 与 Source SHA、4 例模拟反馈拒绝及所有限制；不包含 Agent token。
- WAR-90 运行壳 `tools/director-runtime-v0/cli.py review-pack` 已在上一轮通过 **37/37 单测 + 15/15 真实工作区只读预检**，证据在 `docs/planning/WAR-90/flow-canvas-handoff-20261115/`。本轮调用该已验证入口，不改动其运行壳代码或原 SHA。
- 测试中曾出现浏览器调试 Origin 403 及刚连接未有 project ID 的短暂初始化问题。前者通过只允许 localhost 调试源解决，后者通过等待前端项目 hydration 后再检查解决；**最终真实 E2E 已通过**，而不是跳过错误假定成功。
- **本轮仅为“已批准 Director B → 真实 Canvas Agent → 独立测试画布可视化文本 + 选择 Shot02 → 合法反馈目标校验”**，不是完整用户介入的导演修订与重新审批闭环。

## 4. 下一阶段真正需要验证什么

下一阶段重点**不再是上下文速度优化**，也不立即安装完整 Skill、改生产 API 或生成 H3：

1. 在受控 Canvas 测试项目中，用户真实选中某个 Shot 并提交一句修改反馈；用 `approved_B_id/sha + shot_id + source_sha` 形成可审计修订请求。画布编辑不会直接覆写已批准 DirectorPlan。
2. Director Agent 从冻结批准 B 和反馈发起独立 `Resume`；判断属于仅 Shot 还是需回 Blocking；产生隔离的新专业候选和邻镜复检记录。
3. 在 Canvas 展示差异、已证/未证风险，用户审阅并明确是否批准新 B。不同用户意见、失败或版本冲突都保留原批准版；正式 WAR-35/52 的 typed Review/Join 对接须在公共 Schema 冻结后实现。
4. 本轮没有实现主动接收 UI 反馈的产品适配 API、正式的递增 `revision` 或用户身份认证。若要将试验逻辑并入生产，必须明确这些工程边界及对应开发 Issue，不能把测试脚本当长期正式服务。

**决定**：目前不重新开发 Continue/Refresh、不压缩历史性能实验、不重构 WAR-90 的试验数据结构；先以版本/审批可靠的 Resume 完成 Canvas 人机交互闭环。
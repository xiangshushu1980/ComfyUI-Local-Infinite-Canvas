# WAR-90｜真人反馈关口预审结论

2026-11-15｜Eric

**当前阶段**：已批准 B 后的文字修改意见采集；尚无真人反馈。
**给人看的测试目的**：人读 Shot02 与邻镜的批准原文，提出一条具体表达修改意见；后续验证同一个专业 Codex 在严格绑定版本后局部修改、邻镜复审与 Canvas 差异回显，停在真人 B 审阅，不验证成片。

## 已完成

- 冻结 B、Source、Shot01-03 SHA 及审阅方案；并行启动两个相互隔离 Reviewer：human Luna Medium 与 engineer Astra Medium；由 lead-reviewer Astra Medium 主持综合裁定。三份真实模型会话退出码均为 0。
- 主审结果：targeted-revision。改执行顺序为 **Chat 展示批准文字并采集真实意见 → 核验反馈来源及上游边界 → 在获授权的隔离测试 Canvas 复演 selection → 单 Agent 真修改 → 邻镜/差异独立复审 → 人工 B 决策**。
- 本轮生成 human-review-card.md，Shot01/02/03 全部从已批准专业计划逐字复制，中性提问不泄露“预设答案”，不编写或润色用户原话。
- 保存冻结方案、原始 reviewer/lead 输入输出/事件记录及 SHA。证据见本目录 manifest.json / summary.json。

## 主审采纳的限制

- Chat 反馈要准确标为 Chat 来源、external-user-unverified、human_B_decision=false；不能算 Canvas UI 输入、证明真人身份或签署 B。
- 尚无意见，不可预生成修改候选或模拟填充用户需求；不启动本轮媒体和专业修订。
- 实际 Canvas 写入前必须重新核对进程、端口、浏览器 profile、连接数、MCP 路由与 projectId；被截断的 Canvas 节点内容前缀不能证明后段全文一致。
- 修改执行前确保 feedback envelope 原文和 SHA、B/Source/Shot 版本/selection 绑定，越界或需要改变 Blocking/Beat/Source 时停止 Shot-only。
- 新结果若交接，必须核对非目标镜头逐字锁定、邻镜 pending、未证风险，并由独立审阅 Agent 主持多 Agent 检查后交真人 B；正式 UI 属于 WAR-37，typed Schema 属于 WAR-35。

## 停点

**等待用户通过本 Chat 提供一条明确 Shot02 修改意见，或声明“暂时没有修改意见”。** 此前不创建任何修改 run，不更新 A/B。原批准 B 保持不变，WAR-90 In Progress。

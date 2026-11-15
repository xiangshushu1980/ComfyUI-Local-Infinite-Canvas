# WAR-90 · 双入口决策与 Compact Shot 试点收口（2026-11-16）

## 当前阶段
Canvas Agent 原生只读集成后，确定双入口架构、校验 Codex MCP 配置原点，收口 Compact Shot View 离线实现。用户没有提出新的 Shot02 修改意见，本轮不做导演候选修订。

## 面向人的测试目的
Canvas Lab 日常由 Eric 画布内 Canvas Agent 原生操作 @画布元素；ChatGPT 通过 Eric 的既有 API、远程文件/CLI 参与半自动操作。两入口使用同一 Director Skill / Runtime CLI / 版本与审阅证据；独立 Codex 仅备用，不再搭新导演 Agent 或 HTTP bridge。

## 确认的架构
- 路径 A（主力）：Eric Canvas Agent + 原生 Codex + Director Skill + Runtime CLI + Canvas MCP。原生只读链路在隔离环境 PASS，正式 Skill 安装与权限门槛未验收。
- 路径 B（协作）：ChatGPT → DCR → Eric，显式读取同一 Director Skill/CLI，按已确认 Canvas project/client/selection ID 使用现有 Canvas Agent API。隔离画布的创建、读取、选区、差异展示有限 PASS；Chat 不天然解析 UI 的 @元素。
- 备用：Eric 独立 Codex，仅在主 Agent 不可用、批处理或独立研究/审阅时运行；不成为 Chat 入口的必经中转。
- 并发：同一次修改只允许一个专业入口主控。这是暂行操作规程，跨入口锁/CAS 尚未实现，必须靠授权与版本检查拒绝冲突。

详细决策见 dual-entry-architecture-20261116.md。

## 真实证据与边界
- 真实 Codex config/read 对照：Eric 原 CODEX_HOME 中 Hindsight/Codegraph enabled；空 CODEX_HOME 中两者不存在。配置隔离成立，但不等于运行时权限/审批拒绝已证。
- 现有 Canvas Agent codex_approval 接线没有证明普通 Canvas MCP 读取可发出可拒绝的工具审批；双 Reviewer + 主审裁定此实验假设 BLOCK，权限隔离仍 UNKNOWN。
- WAR-90 的只读 review-shot 复用 Pilot.review_packet() 已批准 A/B、Source/Skill、真实人工证据和 pending 守门，返回目标 Shot 全文、来源原文、哈希对象及邻镜节选；不能据此验收完整导演连续性或生成候选。
- Runtime 64/64 unittest 通过；真实 CLI 检查 Shot01–Shot04 成功、Shot99 拒绝，原 B 65 个原有文件前后哈希一致。B state.json SHA256=23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7。
- 设计与实现均执行独立 2 Reviewer + 1 主审；结论 targeted-revision：离线只读试点保留，生产安装、原生 compact 复测、权限、真人修改/审批仍未验证。
- 正式 WAR-35 Schema 和 WAR-37 Canvas UI 映射均不在本轮修改范围，不生成媒体。

## 下一步
优先针对 Canvas 主入口核实 Skill 七文件安装版本/回退与实际工具权限；并保留 Chat→Eric 受控协作入口，分别验证 API 和 MCP 权限。只有在用户提出实际修改、权限与画布归属已确认时才测试真实修改闭环。本文不构成生产部署批准。

参考：
- dual-entry-architecture-20261116.md
- design-proposal-v0.md、review/（独立方案审阅）
- implementation-review/（独立实现审阅）
- config-origin-probe.json、thread-overlay-probe.json
- compact-cli-audit.json、runtime-tests-64.log

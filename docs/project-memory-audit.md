# XIA-25 — Project Memory / Hindsight 接入核查

> 2026-11-01，只读配置和本机健康核查；不调用 retain/recall、不建 bank、不读取其它项目记忆。

## 已确认
- Codex 全局技能 `project-memory` 存在，由 `~/.codex/skills/project-memory` 链接到 `~/.pi/agent/skills/project-memory`；内置 `references/local-files.md` 和 `references/project-onboarding.md` 管理项目文档、Git、知识位置和按需恢复。
- `hindsight-docs` 是技术参考，不是另一个记忆管理入口；`project-doc-system` 已禁用。
- `~/.codex/config.toml` 的 Hindsight MCP 地址为 `http://127.0.0.1:8888/mcp/`；本轮只读 HTTP GET `http://127.0.0.1:8888/health` 返回 200。
- 当前工具会话中未暴露可直接调用的 Hindsight MCP 工具；没有通过本次检查证明该连接在当前 Agent 上可执行。
- 本项目文档未声明已确认的专属 Hindsight bank/tenant；未凭其它项目或服务健康推断存在或归属。

## 既定知识分工
- 权威技术结论、实验条件、正式决策与证据留在当前仓库 docs 并由 Git 追踪。
- 可复用短经验与重要未决问题，在确定本项目 bank 且按授权可用时，遵循用户级 `project-memory` 的取舍与修订规则进入 Hindsight。
- Linear 负责任务状态和验收；不能把 Done 视作知识已存。
- 不自动跨项目读取、迁移知识；不创建 bank、不以 HTTP 绕过未暴露的 MCP 接口。

## 未验收内容
- 本项目 Hindsight bank 的存在/归属、可用 MCP 工具及适用的检索与保存权限，均未核实。
- 当前核查**完成了客户端配置、服务健康与缺口记录**，不代表 Hindsight 已完成项目级接入。下一步须按 project-memory 的接入协议取得/核对这些信息。

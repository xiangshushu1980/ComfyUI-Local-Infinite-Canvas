# XIA-23 — 两套 Agent 的职责与剥离边界

> 2026-11-01；HEAD 480fd6e，源码静态检查，非运行验收。

## 原生 Canvas Agent（保留）
- `infinite-canvas/canvas-agent/src/index.ts` 启动 HTTP 或 MCP 入口；`src/server/http.ts` 承接 Agent / Codex / Claude 的交互。
- `src/canvas/schemas.ts` 声明 `canvas_get_state`、`canvas_apply_ops` 等工具与操作 schema；`session.ts` 管理画布连接、选择客户端、读状态和分派写操作，`operations.ts` 将具体操作编成画布 ops。
- 证据：`session.test.ts` 覆盖当前画布切换、工具调用、连接丢失等单元场景；并不能替代当前机器联调。
- 原生 Agent 承担创作画布控制、用户交互和本地 MCP 桥接；**优先保留并复用**。

## 根目录 assistant/（2026-11-01 审查记录；2026-11-03 已从当前版本剥离）
- `assistant/server.mjs`、`repair-tools.mjs`、`diagnostics.mjs`、`skill.mjs` 是面向程序源码检查、修复、部署的独立辅助系统，并非上面的画布创作 Agent。
- Gateway `comfyui-gateway/src/assistant.js` 对 `assistant/server.mjs`、workspace、Pi agent 依赖等进行运行时检查与管理。
- `launcher/start.mjs` 的 assistantRuntimeReady / archive 解包逻辑与该运行时耦合，属于上游发布包的能力。
- 上述说明是 2026-11-01 的源码审查快照；后续影响检查与用户范围决定已更新于本文末尾。当前不得再按“待确认”解释。

## 变更前的保留/剥离建议
1. 保留 canvas-agent、前端 Agent Bridge、MCP 画布操作和权限机制。
2. 2026-11-01 时将源码修复助手和 Windows 发布启动器列为待审候选；源码修复助手的后续处理见本文末尾。
3. 任何删除须检查 CodeGraph callers/impact、资源引用、前端路由、测试与打包回归。

## Codex Web 与 Canvas Agent 会话整合讨论（2026-11-02）

状态：**架构讨论与 Agent 建议，尚未由用户采纳，也没有实施或联调验收。** 本次检查 Canvas Lab HEAD `826867e`、Codex Web HEAD `c9bf4f0`；两边工作树均有未提交改动，代码证据以当时磁盘内容为准。运行状态及版本均为当时快照，复用前须重新检查。

### 现有边界与证据

- 进程检查显示 Codex Web 服务启动了 Codex `0.166.0` app-server；Canvas Agent 另行启动项目依赖中的 `0.146.0` app-server，方式为 `app-server --stdio`。同一用户环境及可访问对话数据不表示共享运行进程、活动 turn、MCP 子进程或内存状态。源码见 `infinite-canvas/canvas-agent/src/agent/codex-client.ts` 的 `CodexAppClient.start`。
- Canvas Agent 在 `thread/start` 和 `thread/resume` 的设置中注入 `infinite-canvas` MCP、审批和超时设置，并以线程级 `mcpServerStatus/list` 查询预热结果。MCP stdio 服务通过带 token 的本地 HTTP 请求将工具调用转发至 Canvas Agent；`canvas/session.ts` 管理画布客户端、活动/绑定目标及操作分派。Agent 自身还维护串行 turn 队列。参考 `src/agent/codex-client.ts`、`src/agent/codex.ts`、`src/server/mcp.ts`、`src/canvas/session.ts`（均位于 `infinite-canvas/canvas-agent/`）。
- 当时 Agent 健康响应报告一个已连接画布、空闲，当前对话的 `infinite-canvas` ready，`codegraph` 初始化握手失败。这是该时刻该对话的状态，健康响应不证明工具实际调用成功，也不代表其他线程状态。
- Codex Web 的 `src/server/main.ts` 暴露的是供桌面 renderer 使用的 `/__backend/ipc` WebSocket 桥，每个连接创建应用视图；本次未发现提供给 Canvas Agent 的稳定通用会话 API。未完整审计上游桌面 MCP 设置界面，不能据此断言其没有 MCP 开关或状态展示。
- Codex Web 根 `README.md` 和 `scripts/codex_remote_proxy` 描述由独立 Unix socket app-server 服务供 Web 连接的方式；其 `docs/development.md` 记录本机尚未验证切换。这不是当前 Web 子进程已向 Canvas Agent 暴露复用接口的证据，也未证明多客户端共享语义。

### 备选与暂定建议

1. **保持两个 app-server**：隔离较好，可先统一配置入口和状态展示；仍应按实例、线程展示实际 MCP 生效和错误，而非假设状态一致。
2. **两个客户端连接共享 app-server**：可探索独立于 Codex Web 生命周期的服务，但需新增或适配 Canvas Agent 连接，验证版本、并发、线程订阅、审批和断线语义；共享服务成为共同故障点。直接依赖当前 Web 子进程仍会受到 Web 重启影响。
3. **将 Canvas 能力并入 Codex Web 后端/会话层**：可形成单一产品控制面，但需要迁移画布连接、路由、事件、审批等职责，并增加桌面上游补丁及升级成本，故不建议在缺少明确收益与验证前实施。

建议先明确 MCP 配置权威来源、开关的作用域及生效时点，区分配置启用、进程启动、线程握手和工具调用；保留 Canvas Agent 的画布连接和路由。随后在隔离环境验证外置共享 app-server，再依据实测决定是否迁移。减少进程数量本身不是充分理由。

### 迁移前必须验证

- 两客户端的版本与协议兼容、同时初始化、断线重连及大消息；记录精确配置与启动参数。
- 用户级配置和 Canvas 线程注入的合并规则；开关对新建、恢复及运行中线程的作用；分别核验启动通知、线程 MCP 清单和真实工具调用。
- 同一线程在两客户端读取、恢复、订阅、执行、中断和审批的归属与冲突处理；持久化对话可见不等于活动会话共享。
- 至少两个画布客户端切换、断线和重连时，turn 与画布身份绑定、读写目标及错误处理；用可清理的操作验证不发生跨画布误写。
- 分别重启客户端、代理及共享服务时的运行任务、待审批请求、MCP 和恢复行为；明确安全边界、资源/性能、回退方案及上游升级成本。

本轮未更改应用代码、依赖、服务或 MCP 配置，未重启服务；共享 app-server 和统一管理均未实测。

## 2026-11-02 后续实现与证据

本文关于 Codex `0.146.0` 等内容是审查时快照；Canvas Agent 已升级到 `0.166.0`，并实现画布 MCP 显式注入、Canvas Agent 独立 MCP/Skill 启用覆盖。两个 app-server 仍独立；详细实现、验证边界、CodeGraph 工作空间复核和未完成的 UI 验收见 [Canvas Agent 升级与配置记录](canvas-agent-codex-upgrade-progress.md)。

## 2026-11-03 当前产品范围决定

- 用户决定将根目录源码修复助手（`assistant/`）从当前版本完全剥离，并使用自己的 Agent 修复项目。
- 保留 `infinite-canvas/canvas-agent/` 原生 Canvas Agent。不要把两个 Agent 的职责、代码目录或剥离结论混为一谈。
- 该决定 supersedes 上文“暂不删除 / 待用户价值判断”的旧结论。2026-11-03 已清理源码目录、前端插件、Gateway 管理/API、启动器运行时解包、打包脚本及补丁包包含项；更新器仍保护旧版 workspace/data 用户文件。dist 中修复插件清单/文件已移除，但完整 dist 和回归尚未验证。
- 当前项目 Agent 所需的代码地图见 [`current-code-map.md`](current-code-map.md)。

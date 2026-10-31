# XIA-23 — 两套 Agent 的职责与剥离边界

> 2026-11-01；HEAD 480fd6e，源码静态检查，非运行验收。

## 原生 Canvas Agent（保留）
- `infinite-canvas/canvas-agent/src/index.ts` 启动 HTTP 或 MCP 入口；`src/server/http.ts` 承接 Agent / Codex / Claude 的交互。
- `src/canvas/schemas.ts` 声明 `canvas_get_state`、`canvas_apply_ops` 等工具与操作 schema；`session.ts` 管理画布连接、选择客户端、读状态和分派写操作，`operations.ts` 将具体操作编成画布 ops。
- 证据：`session.test.ts` 覆盖当前画布切换、工具调用、连接丢失等单元场景；并不能替代当前机器联调。
- 原生 Agent 承担创作画布控制、用户交互和本地 MCP 桥接；**优先保留并复用**。

## 根目录 assistant/（暂不删除）
- `assistant/server.mjs`、`repair-tools.mjs`、`diagnostics.mjs`、`skill.mjs` 是面向程序源码检查、修复、部署的独立辅助系统，并非上面的画布创作 Agent。
- Gateway `comfyui-gateway/src/assistant.js` 对 `assistant/server.mjs`、workspace、Pi agent 依赖等进行运行时检查与管理。
- `launcher/start.mjs` 的 assistantRuntimeReady / archive 解包逻辑与该运行时耦合，属于上游发布包的能力。
- 本项目纯 WSL 部署，Windows Launcher 不作为入口；**源码修复助手是剥离或停用候选，但需要先核对前端功能入口、Gateway 路由和用户是否仍需自动修复能力。** 禁止仅根据用途差异直接删除整个目录。

## 变更前的保留/剥离建议
1. 保留 canvas-agent、前端 Agent Bridge、MCP 画布操作和权限机制。
2. 将源码修复助手和 Windows 发布启动器标记为待剥离；先完成调用方与用户价值判断。
3. 任何删除须检查 CodeGraph callers/impact、资源引用、前端路由、测试与打包回归。

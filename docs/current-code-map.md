# 当前代码地图：Infinite Canvas、Canvas Agent 与 ComfyUI Gateway

> 用途：帮助项目 Agent 和开发者理解当前工作树的模块职责、来源边界、运行方式与关键调用链。本文是代码导航，不是功能验收，也不替代源码、测试或运行记录。
>
> 快照：2026-11-03；分支 `main`，HEAD `093e11e`。写作时工作树已有大量未提交改动；本图基于当时磁盘源码和项目文档，复用前应检查当前 HEAD、diff 与 CodeGraph 状态。

## 来源与保留范围

以下来源划分依据用户在 2026-11-03 的明确说明：

- **Infinite Canvas**：画布产品与前端能力来自 Infinite Canvas 上游。
- **Canvas Agent**：面向画布交互的原生 Agent 也来自 Infinite Canvas 上游，负责理解当前画布并通过受控工具读写画布。
- **ComfyUI Gateway**：参考项目加入的 ComfyUI 工作流接入层；它将画布/工作台生成请求转换为 ComfyUI 工作流执行，并负责工作流选择、参数绑定、任务跟踪及结果交付。

当前 Rebuild 的目标是保留并理解这三部分，按 WSL 环境适配参考项目。源码修复助手（根目录 `assistant/` 及其界面、服务和运行时集成）已按用户决定从当前源码、Gateway 和打包入口中剥离；启动时会清理浏览器插件库中旧的修复助手插件记录，但保留用户画布数据。旧版 `assistant/workspace` 与 `assistant/data` 仍作为历史用户文件由更新器保护。Web 的 `dist` 插件清单和插件文件已移除，但没有重建整个 dist；生产构建及回归仍待验证。不要把源码修复助手与 Canvas Agent 混为一谈。

## 模块地图

| 模块 | 主要目录 | 职责与边界 | 关键入口 |
|---|---|---|---|
| Infinite Canvas 前端 | `infinite-canvas/web/src/` | 画布、节点、工作台、设置、客户端状态与生成 API 调用；前端本地存储负责项目/素材状态 | `src/pages/canvas/project.tsx`、`src/services/api/image.ts`、`src/services/api/video.ts`、`src/stores/` |
| Canvas Agent | `infinite-canvas/canvas-agent/src/` | 独立服务；管理浏览器画布客户端、对话/turn、Codex app-server，以及画布 MCP 工具和操作分派 | `src/index.ts`、`src/server/http.ts`、`src/server/mcp.ts`、`src/agent/codex-client.ts`、`src/canvas/session.ts`、`src/canvas/schemas.ts`、`src/canvas/operations.ts` |
| ComfyUI Gateway | `comfyui-gateway/src/` | 参考项目加入的工作流执行与 ComfyUI 适配层；对前端暴露 API，维护注册表、bindings、任务、ComfyUI 客户端和资源状态 | `src/server.js`、`src/registry.js`、`src/bindings.js`、`src/runner.js`、`src/tasks.js`、`src/comfy-client.js` |
| 工作流与资源声明 | `comfyui-gateway/workflows/`、`comfyui-gateway/resources/` | 工作流注册、参数映射及随项目维护的资源/节点声明；声明存在不等于本机依赖齐全或运行成功 | `workflows/registry.json`、`resources/index.json`、`resources/nodes/` |
| WSL 开发部署 | `deploy/systemd/`、`deploy/install-user-services.sh` | 用户级 systemd 单元分别运行 Web、Gateway、Canvas Agent；Windows Launcher 不作为此项目部署入口 | 具体启动边界和时间性状态见 [`runtime-boundary.md`](runtime-boundary.md) |

## 关键调用链

### 图片生成

1. 画布节点或图片工作台在 `web/src/pages/canvas/project.tsx` / `web/src/pages/image/index.tsx` 收集 prompt、模型、参数及参考图。
2. `web/src/services/api/image.ts` 构造 OpenAI 兼容请求并发送到 Gateway 的 `/v1/images/generations` 或 `/v1/images/edits`。
3. `comfyui-gateway/src/server.js` 执行路由、输入校验、workflow/model 解析和上下文构造；`registry.js` 与 `bindings.js` 负责选取 workflow 并把通用参数映射到节点输入。
4. `runner.js` 提交 ComfyUI `/prompt`，读取 `/history` 和输出；`comfy-client.js` 封装 ComfyUI 通信。
5. 响应回到前端，由画布逻辑创建或更新节点，并通过前端存储服务保存结果。逐分支的持久化和失败路径仍需按实际功能审计；静态链路不证明端到端成功。

### 视频任务

1. `web/src/services/api/video.ts` 创建 Gateway 视频任务；画布节点路径由 `web/src/pages/canvas/project.tsx` 管理，工作台路径位于 `web/src/pages/video/index.tsx`。
2. Gateway `server.js` 创建任务并交给 `tasks.js` 排队/跟踪；任务执行调用 `runner.js` 的视频工作流。
3. Gateway 返回任务状态、进度/预览或最终内容；前端轮询、处理取消与错误，并将成功视频写回画布节点或工作台日志。

### Canvas Agent 操作画布

1. 前端 Agent 面板与 bridge 位于 `web/src/components/agent/`、`web/src/services/api/canvas-agent.ts` 及相关 stores；浏览器客户端与画布状态通过 Canvas Agent 协议连接独立服务。
2. `canvas-agent/src/server/http.ts` 承接会话请求；`src/agent/codex-client.ts` 管理 Codex app-server 子进程和线程/事件交互。
3. `src/server/mcp.ts` 暴露本地 MCP 转发；`src/canvas/session.ts` 选择活动或绑定的画布客户端、维护状态并分派操作。
4. `src/canvas/schemas.ts` 定义工具/操作合同，`src/canvas/operations.ts` 执行画布操作。验证“服务健康”不等于验证真实工具调用或目标画布写入。

## 运行与部署边界

项目采用纯 WSL 开发部署。`docs/runtime-boundary.md` 记录的开发方式是：Web 由 Vite 开发服务器运行源码并提供 HMR；Gateway 以 Node watch 运行源码；Canvas Agent 以 `tsx watch` 运行 TypeScript 源码。三个 user unit 由 `canvas-lab.target` 聚合。该记录有时间戳，复用前检查 unit、进程和监听地址。

因此，开发阶段访问的 Web 页面通常来自 Vite 源码服务，不应默认把 `web/dist` 当作当前页面入口。Gateway 和 Canvas Agent 也是各自的独立开发进程。生产静态部署与开发服务的行为需分别判断；任何服务启停、依赖安装或 ComfyUI 操作遵守项目授权边界。

## Agent 阅读与工作约定

- 开始前先读本图和 [`docs/README.md`](README.md)；按任务再读 `feature-audit.md`、`validation-matrix.md`、`workflow-integration-audit.md`、`runtime-boundary.md`、`wsl-validation-protocol.md`。
- 当前代码、当前 AGENTS 约束和用户明确决定优先于本图；遇到不一致，标注差异并更新文档，不要把旧快照当现状。
- 仓库存在 `.codegraph/` 时，理解入口、调用关系和影响范围先用 CodeGraph，再按需读具体源码；索引只辅助静态分析，不是测试或运行证据。
- 修改前检查目标文件的现有 diff 和调用影响；项目默认只读研究。未获授权不改应用代码、依赖、服务配置或 GPU 工作流。
- 报告时区分来源声明、源码静态定位、测试、WSL 服务检查、用户视觉/行为验收和真实 ComfyUI 工作流结果。

## 证据与未覆盖范围

- 本图的来源划分中，“Infinite Canvas / Canvas Agent 为上游已有、Gateway 为参考项目加入”是用户确认的项目事实；精确提交级归属仍应结合 Git 历史和相关上游版本核查。
- 关键路径依据当前工作树源码和 CodeGraph 静态定位整理；没有因此运行测试、重启服务或执行 ComfyUI 生成。
- Gateway 多数执行环节、图片/视频结果持久化、取消/失败/重试路径和 Canvas Agent 写操作仍需按 [`validation-matrix.md`](validation-matrix.md) 分层验证。
- `docs/source-path-audit.md` 保留此前的核心生成链路审查和历史证据；本图提供面向 Agent 的总览，不会覆盖或改写其原始审查记录。

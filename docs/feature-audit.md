# Canvas Lab Rebuild — 功能与依赖审查

> 状态：初版；2026-10-31。依据当前目录、Git、核心文档和部分 CodeGraph 查询；不是运行验证结论。
> 判定术语：**保留候选**、**剥离候选**、**适配候选**、**待确认**均是审查决定，不代表已经实施。

## 基线与证据
- 当前 HEAD：`dd07e55`；参考 fork 版本：`9e6d56b`（v0.23.1）；旧对照起点：`7d4f558`。
- 当前分支：`codex/canvas-lab-rebuild`，基于 `origin/main` ahead 1。
- 修改中的文件：`comfyui-gateway/prompts/image-prompt-enhance.json`、`comfyui-gateway/src/prompt-optimizer.js`；未经评估不得覆盖。
- `.codegraph/` 为本地未跟踪索引，当前 status 显示 up to date（853 files / 23,069 nodes / 62,664 edges）。
- README 的运行成功声明属于参考项目报告；本工作树尚无本次实测证据。

## 初版模块台账

| 模块 | 位置 | 建议 | 证据等级 | 依赖与风险 / 下一步 |
|---|---|---|---|---|
| 画布交互、节点与状态 | `infinite-canvas/web/src` | 保留候选 | 目录与参考文档 | 先定位节点、连线、存储、生成服务入口；不得先删上游节点 |
| Gateway Comfy 客户端 | `comfyui-gateway/src/comfy-client.js` | 保留候选 | 源码索引 | ComfyUI 端口探测与请求路径耦合；核实本机 ComfyUI 的连接方式 |
| 工作流注册与参数绑定 | `src/registry.js`、`src/bindings.js`、`workflows/registry.json` | 核心保留候选 | 目录与配置（20 条） | 分离业务 preset 与通用映射；增加/变更 workflow 前测试兼容性 |
| 执行、任务、预览 | `src/runner.js`、`src/tasks.js`、`src/preview-hub.js` | 核心保留候选 | 源码索引与文档 | 取消、状态、异常与结果回写需完整验证 |
| Qwen/H3/放大等业务工作流 | `comfyui-gateway/workflows/` | 按工作流逐项评估 | 配置存在 | JSON 存在不等于模型/节点齐全或本机可运行 |
| 资源安装和模型管理 | `src/resources.js`、`src/setup.js`、`resources/` | 适配候选 | 目录与文档 | 自动安装/写 ComfyUI 环境有副作用；先只读研究，不操作 |
| Windows 启动器 | `launcher/`、`start-local.bat` | 剥离/隔离候选 | 源码、文档及用户确定纯 WSL | Windows 启停和自动接管不作为部署入口；审查与 Gateway 等模块的耦合后才允许剥离 |
| 原生 Canvas Agent / MCP | `infinite-canvas/canvas-agent/` | 优先保留研究 | README、CodeGraph 对 `CanvasSession` 和画布操作路径的定位 | 进一步核对操作集合、授权、前端接入与状态同步；尚未联调 |
| 源码修复助手 | `assistant/` | 待确认；剥离候选 | README 与目录 | 作用在源码、构建与部署，并非创作画布 Agent；检查前端卡片、启动器与网关调用后再定 |
| 原生 Canvas Proxy | `infinite-canvas/canvas-proxy/` | 待确认 | README 与目录 | 本地 ComfyUI 请求是否需要该转发层；需审查实际调用方 |
| 自更新与发布工具 | `src/update.js`、`tools/`、`update.json` | 剥离/隔离候选 | 目录与文档 | 和启动、版本提示、保护数据路径耦合；不能直接删除 |
| 皮肤、商业业务与提示词功能 | `skin-unlocks.js`、`prompt-optimizer.js` 等 | 待确认 | 文件存在 | 查找使用者、相关 UI 和测试；保留两个既有未提交修改 |

## 删除前必过检查
1. 用 CodeGraph `callers`/`impact` 检查入口与下游依赖，再用源码确认。
2. 列出关联的前端路由/卡片、Gateway 接口、注册工作流、持久化字段、测试与启动器逻辑。
3. 先标记隐藏/停用是否可行，再考虑删除；每一步保持可回滚。
4. 记录删除前后验证矩阵中的关键链路与异常路径。
5. 不修改本地 ComfyUI、依赖、服务、GPU 工作流，除非获得单独授权。

## 下一轮源码审查重点
- 画布生成服务 → Gateway 接口 → registry/bindings → runner/tasks → ComfyUI → 结果回写的文件级映射。
- Canvas Agent MCP 状态/操作、授权机制与前端桥接。
- assistant、update、resources、launcher 的入口依赖图。
- 评估这些模块后把候选项升级为正式结论并附证据链接/命令/结果。

# 核心生成链路 — 静态定位

> 2026-10-31 使用 CodeGraph 和定向源码检索确认入口；仅为初步文件级定位，尚未形成完整调用图或执行测试。Linear: XIA-22。

## 画布与 Gateway
- 画布核心 `infinite-canvas/web/src/pages/canvas/project.tsx`：存在 `generateImageFromTextNode`，使用 `createVideoGenerationTask` 及结果节点处理；包含 `storageKey` 素材关联逻辑。
- 图片 API 入口候选：`infinite-canvas/web/src/services/api/image.ts`；后续需确认生成、编辑、失败路径及取消请求。
- 视频 API：`infinite-canvas/web/src/services/api/video.ts`，可定位 `createVideoGenerationTask`、`waitForVideoGenerationTask`、视频上传/存储调用。
- Gateway：`comfyui-gateway/src/server.js` 承载 API 入口；`registry.js` / `bindings.js` 负责工作流模型和参数；`runner.js` / `comfy-client.js` 对接执行；`tasks.js` / `preview-hub.js` 管理异步任务和预览。
- 工作流配置位于 `comfyui-gateway/workflows/registry.json`，本轮直接解析其根键和条目数为 20；实际可用性仍取决于 ComfyUI 的节点、模型、参数匹配和运行状态。

## 2026-11-01 增量源码核查（HEAD `480fd6e`，XIA-26 后）
- 升级记录：XIA-26 关联提交 `107504a` 移除 Local Only 并升级 Vite 8、`ecd2cbf` 合并 v0.24.0、`96cde5e` 重建 dist；当前 package.json 为 Vite `^8.3.5`，CodeGraph status 报告最新。XIA-26 的服务与 Agent 健康记录属于当次验收，本轮未复测。
- **图片请求**：`image.ts:764` `requestGeneration` 经过 `aiApiUrl(..., '/images/generations')` 发送请求、附加本地请求 ID；`image.ts:133/148` 提供 Gateway 取消及进度入口。Gateway `server.js:1132` `/v1/images/generations` 调用 registry reload、requireModel、mode variant resolution 并构建 context；编辑入口位于 `server.js:1250`。
- **视频异步**：`video.ts:101/56/217` 分别创建任务、轮询结果、`storeGeneratedVideo`。`project.tsx:428-438` 将 task ID 写入节点，成功时 `storeGeneratedVideo` 后经 `applyGeneratedVideo` 更新节点；`server.js:1551/1709/1758/1766` 分别提供创建、状态、内容与取消接口。`project.tsx:442+` 存在恢复轮询入口。
- **存储边界**：`storeGeneratedVideo` 在 URL 上传失败时会返回 `storageKey: ''` 的远端 URL 退化结果（`video.ts:217-226`）。这是否影响重开画布后媒体持久可用，须专项验证；不能推定已经损坏。
- **仍需核实**：Gateway server → runner → bindings → ComfyUI 的所有动态路径与错误/取消一致性；图片结果回写的全部分支；XIA-26 之后的构建与全量回归。

## XIA-22 网关执行链核查（2026-11-01）
- 图片入口 `server.js:1132` reload registry → `requireModel` / `resolveForMode` → `buildContext` → `runImage` → 输出编码或 `tasks.saveOutput`。网络断开通过 `abortOnDisconnect` 取消当前请求。
- 视频入口 `server.js:1551` 读取工作流和多媒体输入 → `tasks.create` → `tasks.enqueue`，任务体调用 `runVideo`；状态、内容与取消位于 `server.js:1709/1758/1766`。
- `runner.js:119` 的 `runWorkflow` 先执行 `resolveForMode`、`applyBindings`、主模型、LoRA 与模型别名，随后 `comfy.submit`，循环读取 `comfy.history`，按产物调用 `comfy.view`；AbortSignal 可调用 `comfy.cancel` 或 `comfy.interrupt`。
- 动态节点绑定和模型文件路径依赖实际 ComfyUI 工作流，**静态路径已定位，运行兼容性未验收**。图像结果与视频持久化仍应在独立 WSL 验证中覆盖。

## 依赖审查待完成
- 正向核对图片生成与编辑各路由的真实调用关系，以及结果对象写入节点与 IndexedDB 的位置。
- 确认取消/重试、预览、错误、请求中断与异步任务的状态一致性。
- 验证多工作流 variant / bindings 变化是否影响前端展示。
- 检查 `assistant/` 与 `canvas-agent/` 的依赖边界，禁止直接删除。
- CodeGraph 的宽泛检索会命中第三方 ComfyUI 节点包；后续使用文件路径/精确符号缩小范围，再读源码确认。

## 当前结论
已有可追踪模块，但**没有证明真实端到端运行或结果回写成功**。后续据此更新 `feature-audit.md` 和 `validation-matrix.md`。

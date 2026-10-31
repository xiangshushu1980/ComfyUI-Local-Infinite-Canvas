# 核心生成链路 — 静态定位

> 2026-10-31 使用 CodeGraph 和定向源码检索确认入口；仅为初步文件级定位，尚未形成完整调用图或执行测试。Linear: XIA-22。

## 画布与 Gateway
- 画布核心 `infinite-canvas/web/src/pages/canvas/project.tsx`：存在 `generateImageFromTextNode`，使用 `createVideoGenerationTask` 及结果节点处理；包含 `storageKey` 素材关联逻辑。
- 图片 API 入口候选：`infinite-canvas/web/src/services/api/image.ts`；后续需确认生成、编辑、失败路径及取消请求。
- 视频 API：`infinite-canvas/web/src/services/api/video.ts`，可定位 `createVideoGenerationTask`、`waitForVideoGenerationTask`、视频上传/存储调用。
- Gateway：`comfyui-gateway/src/server.js` 承载 API 入口；`registry.js` / `bindings.js` 负责工作流模型和参数；`runner.js` / `comfy-client.js` 对接执行；`tasks.js` / `preview-hub.js` 管理异步任务和预览。
- 工作流配置位于 `comfyui-gateway/workflows/registry.json`，本轮直接解析其根键和条目数为 20；实际可用性仍取决于 ComfyUI 的节点、模型、参数匹配和运行状态。

## 依赖审查待完成
- 正向核对图片生成与编辑各路由的真实调用关系，以及结果对象写入节点与 IndexedDB 的位置。
- 确认取消/重试、预览、错误、请求中断与异步任务的状态一致性。
- 验证多工作流 variant / bindings 变化是否影响前端展示。
- 检查 `assistant/` 与 `canvas-agent/` 的依赖边界，禁止直接删除。
- CodeGraph 的宽泛检索会命中第三方 ComfyUI 节点包；后续使用文件路径/精确符号缩小范围，再读源码确认。

## 当前结论
已有可追踪模块，但**没有证明真实端到端运行或结果回写成功**。后续据此更新 `feature-audit.md` 和 `validation-matrix.md`。

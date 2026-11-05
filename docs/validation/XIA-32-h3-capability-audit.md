# XIA-32 · Canvas Agent / ComfyUI H3 可复用能力基线审计
日期：2026-11-05。性质：源码静态检查 + 局部 Node 测试；未改动应用代码、服务或 GPU 工作流。

## 版本和现场
- Canvas Lab: `main` / HEAD `2bb636f`，根目录 VERSION `v0.24.3`；Gateway package `0.1.0`；Canvas Agent package `0.6.0`。
- ComfyUI: `v0.44.0` / HEAD `2c75dc1b`；`comfy-ops` HEAD `0249c45`。
- `canvas-lab` 与 `ComfyUI` 均存在大量原有未提交更改；本次未覆盖。基线反映**磁盘工作树**，非纯 HEAD。
- 本轮 `ss -ltn` 未看到 8188/3001/3002/17371/5173 监听；`curl /health` 对 8188/3001 连接失败。不能把文件存在视为服务在线，更不能声称 H3 实时生成已验证。

## 可复用入口和证据等级
| 能力 | 已存在的源码/契约 | 证据与状态 |
|---|---|---|
| Canvas Agent 画布读写、节点创建、连线、生成、状态查询 | `infinite-canvas/canvas-agent/src/canvas/schemas.ts` 的 `canvas_get_state`、`canvas_apply_ops`、`canvas_create_generation_flow`、`canvas_generate_video`、`canvas_run_generation`、`generation_get_status`；`web/src/pages/canvas/hooks/use-agent-bridge.ts` | 静态已确认；本轮未执行浏览器真实节点操作 |
| 视频生成和结果轮询 | `comfyui-gateway/src/server.js`：`POST /v1/videos`、`GET /v1/videos/:id`、`GET /v1/videos/:id/content`、`POST /v1/videos/:id/cancel`；`src/registry.js`、`src/bindings.js`、`src/runner.js`、`src/tasks.js` | 静态已确认；未执行真实视频任务/裁剪拼接 |
| 工作流模型发现与映射 | `GET /v1/models`、`GET /api/workflows`、`GET /api/workflows/:id/schema`；`workflows/registry.json` | 静态已确认；本轮未验证在线返回、模型依赖满足程度 |
| H3 工作流 | `workflows/h3-ref2va-drama.json`、`h3-ref2va-drama-vdn.json`、`h3-character-swap-vdn.json`；`test/h3-refresh-models.test.js` 还包含 T2V、frames 与无 VDN 模型 ID | 文件/测试定义存在；VDN、TRT、模型权重、GPU 执行和音视频输出未实测 |
| H3 本地提示词优化 | `POST /v1/prompts/optimize`、`src/prompt-optimizer.js`、`src/h3-lora-workflow.js`、`prompts/h3-lora/training-prompts.json` | 静态已确认：Qwen3.5-9B INT8 + Ref2VA/FL2VA LoRA，TextGenerate 输出；本轮未在 GPU 完成真实推理 |
| H3 优化输入约束 | `src/h3-lora-workflow.js` | 支持 T2AV、I2AV、L2AV、FL2AV、REF2AV；仅静态图片输入，不提供音频/视频参考附件；秒数按 24fps、17 帧步幅换算 |
| 测试基线 | `test/h3-lora-workflow.test.js`、`test/prompt-optimizer.test.js` | 执行 `node --test test/h3-lora-workflow.test.js test/prompt-optimizer.test.js` 发现 Qwen PE alias 断言失败：期望 `Qwen3.5-9B-Q6_K.gguf`，实际 `undefined`（`prompt-optimizer.test.js:426-450`）；不能记为全绿 |

## 风险与复用建议
1. **优先复用而不重造**：上层导演 Agent 使用 `canvas_create_generation_flow` / `canvas_generate_video` 管理生成节点，Gateway 的视频 API 承担提交、轮询、内容与取消。结构化 Sequence/Shot/Beat 只作为编排层元数据，不先改现有执行协议。
2. **剪辑能力是缺口**：本轮只证实 H3 分段生成、任务跟踪入口存在；未找到并验证可组合 1.7–1.9 秒镜头的稳定时间线、裁剪、转场、拼接统一入口。XIA-40 需要单独验证 FFmpeg/编辑器路径与镜头边界、音频连续性。
3. **本地优化器验证不完整**：LoRA 文档说明共享 ComfyUI GPU/RAM，空闲时卸载；冷启动与资源抢占、中文输出一致性需实测。图像优化 alias 测试失败需要定位原因，不在本审计中修复。
4. **服务运行状态未证实**：没有监听端口，不进行写入性探针、不启动服务或触发 GPU。后续集成先确认配置及健康，再做小样本任务，并记录输出、耗时、显存、取消/失败行为。
5. **工作树污染风险**：已有大量用户改动，不直接切换分支、不重置、不批量格式化。若后续改代码，先读取目标 diff，列出影响文件、测试和按文件回滚方案，再实施。
6. **验收边界**：当前为静态能力审计与局部失败证据；Canvas Agent 端到端、H3 GPU 实测、VDN 与无 VDN 实际可用性、真实视频合成仍属待验证。

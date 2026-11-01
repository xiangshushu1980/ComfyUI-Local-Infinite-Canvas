# XIA-28 — 自有 ComfyUI 工作流接入研究

> 2026-11-01。基于当前 Rebuild checkout 的 CodeGraph 与定向源码只读审查。未改应用代码、依赖、服务或 ComfyUI；未执行测试、安装或 GPU 生成。以下为 S 级静态证据。

## 范围与前置约束

- checkout：HEAD `99cd2d3`，分支 `codex/canvas-lab-rebuild`；CodeGraph status 为 up to date。
- 复用 XIA-27 的安全结果，见 [`resource-install-audit.md`](resource-install-audit.md)：资源安装可能写共享 ComfyUI 模型/节点目录、Python 环境和 Gateway data，部分路径可请求重启或运行 GPU bake。因此本轮只研究文件式接入，不调用资源安装 API。
- 选取已有自有样本 `minimax_h3_ref2va_img_vid_api.json`。只读检查，未复制或修改原文件。它是 24 节点的 ComfyUI API JSON，构成 H3 参考图/参考视频转带音频视频的工作流。

## 样本节点和依赖

工作流含 UNETLoader、CLIPLoader、两个 VAELoader、LoadImage、MiniMaxH3ReferenceToVideo、VHS_LoadVideo、采样器/调度器、视频和音频解码、CreateVideo、SaveVideo。静态输入包括提示词、1024×576、length 124、seed 20260805、steps 20、fps 24；LoadImage 指向 `start/alya169_flat.png`，VHS_LoadVideo 指向 `material/action/woman_dancing_8039424_960x506.mp4`。

模型文件引用至少包括 `minimax_h3_ref2va_pruned_int8_convrot.safetensors`、`qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`、`minimax_h3_video_vae_fp16.safetensors`、`minimax_h3_audio_vae_fp32.safetensors`。自定义节点包含 `MiniMaxH3ReferenceToVideo`、`VHS_LoadVideo`、`VAEDecodeAudio` 等。静态 JSON 解析没有检查这些文件或节点是否在本机存在，也没有核验外部依赖、版本或许可。

## 内置工作流与自由卡片调用路径

### Registry 路径

`comfyui-gateway/workflows/registry.json` 声明 workflow ID、type、文件、bindings、参数、presets 和 base model 元数据。`src/registry.js` 负责装载、校验、reload、schema 和 mode variant；`src/bindings.js` 按明确的 node/input/from/transform 将请求参数写入工作流；`src/runner.js` 提交 ComfyUI、轮询 history、获取输出并处理取消。HTTP 入口在 Gateway `src/server.js` 的图像及异步视频 API。它适合需要稳定参数界面、显式约束和长期维护的集成。

### 自由工作流路径

画布侧栏 free tab 可列举 Gateway 配置的 ComfyUI workflows 根目录中的工作流文件。用户选择 JSON 后调用 `POST /api/free-workflows/import`；Gateway 校验相对路径、文件大小、JSON/UI/API 格式并检测 bindings，将工作流元数据保存在 Gateway data 的 `free-workflows.json`。随后可把条目添加为画布 free card。图像和视频分别调用 `/v1/free-workflows/:id/images` 和 `/v1/free-workflows/:id/videos`；后端复用 Gateway task/runner 机制。视频任务有任务状态端点，项目页轮询并将生成视频存入画布素材存储后更新节点。源文件变化可触发同步。UI JSON 转换需要 ComfyUI `object_info`；API JSON 可直接读取。

对应静态定位：`server.js:929-1006`、`free-workflows.js:110-150,230+`、`ui-workflow.js:358+`、前端 `services/api/free-workflow.ts:86-224`、`pages/canvas/project.tsx:3653,3701`、视频回写 `project.tsx:3653+`、`components/canvas/canvas-free-card-panel.tsx` 和 `canvas-side-panel.tsx`。具体源码以本 checkout 当前行号和 CodeGraph 结果为准。这里证明调用路径存在，不证明它已与本机 ComfyUI 或生成结果完成端到端联调。

## 自有 H3 样本适配判断

自动绑定检测可以从输出节点和可达节点识别部分通用 prompt、LoadImage、seed、尺寸/比例输入。但它不会自动理解所有 H3 多模态节点语义，也不能证明模型或节点就绪。样本要求外部参考视频，而其中 `VHS_LoadVideo.video` 是固定 ComfyUI 文件路径；没有源码证据证明当前 free card 的视频上传引用能映射至该静态文件输入。因此导入成功不能代表完整绑定成功。

最小可评审方案：

1. 先用 Gateway free card 对样本副本做无 GPU 的导入/检测探索；把参考图和参考视频路径改为显式 API 输入之前，先核对现有视频上传与 binding 协议。可以先限定为 prompt + 一张参考图，视频输入另列适配点。
2. 若要提供正式产品入口，则将版本化 API JSON 放入 `comfyui-gateway/workflows/`，在 `registry.json` 明确声明 prompt、图像/视频、width、height、length、seed、steps、fps 等 bindings 和参数；增加 Registry/Bindings fixture 与定向测试。避免为单条工作流增加新的框架。
3. 缺失提示应区分节点 class 不可用、模型/辅助文件缺失和绑定目标不匹配；不能用 Gateway 或 ComfyUI reachable 表示 workflow ready。当前样本没有静态依赖探测配置。
4. 本次选定样本是自有 workflow；仓库已有注册的 `video-h3-ref2va` 可作现有实现对照，其 Registry 声明图像/视频/音频输入范围，但它不是该自有样本，也没有因此获得本机可运行证明。

实施计划涉及的新 workflow JSON、Registry entry、Bindings 测试 fixture，以及可能需要的前端输入适配均待授权；本轮没有添加它们。资源安装索引和自动安装逻辑不在建议的首轮改动范围内。

## 分层验证与回滚

1. 无 GPU 单元/Mock：检查注册 schema、ID 唯一性、文件解析、每个 binding 的目标节点/输入，图像和视频可选/必填条件，缺失节点/模型/绑定错误分类。
2. 隔离 Gateway + 临时 data + mock ComfyUI：断言提交 payload、任务 history/进度/失败/取消和 SaveVideo 输出收集；不连接共享 `8188`，不调用安装 API。
3. 本机实机需单独授权：先核实目标 ComfyUI 的节点和模型，再提交单次 GPU 任务，记录任务 ID、history、输出以及画布回写；重开画布验证持久化。不得将连接健康或队列空闲当成生成证据。
4. 回滚：新增 JSON 与 registry entry 放在一个 scoped commit 中，反向提交即可撤销；不覆盖现存 workflow，不改 ComfyUI 文件。

本轮未运行测试、build、服务、安装器或生成工作流。真实节点/模型存在性、上传视频映射、绑定兼容、取消进度、输出回写和重开持久化均仍未验证。

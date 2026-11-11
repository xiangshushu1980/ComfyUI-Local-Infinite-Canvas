# WAR-66｜ViMax 原版管线预检与 C 冻结

## 状态（2026-11-11）

**已完成：** 依据最新版 `linear-task-collab` 接手；核对三份源码快照与前置清单；从 WAR-65 原始归档提取并逐字节冻结剧本 C。**未完成：** 原版 ViMax 模型运行及任何阶段输出。未生成图像/视频、未修改上游源码或环境。

## 原版文本阶段（代码观察，不是运行结果）

`Script2VideoPipeline.plan_text_artifacts()` 依次执行 `extract_characters`（可由调用方提供角色跳过）、`design_storyboard`、`decompose_visual_descriptions`、`construct_camera_tree`（出错时允许二次尝试）。设计调用 `StoryboardArtist.design_storyboard`，逐镜拆解调用 `StoryboardArtist.decompose_visual_description`，机位树调用 `CameraImageGenerator.construct_camera_tree`。代码通过 Pydantic 解析结构化输出；分镜阶段提示词要求单一场景、同镜尽可能复用机位、画面空间关系明确；FF/Motion/LF 由每个镜头的 `visual_desc` 分解，并非独立的全片连续性状态规划。Camera Tree 组织参考机位与镜头依赖，不代表已经证明跨镜人物/道具连续性。

`plan_text_artifacts` 不调用实际图片或视频生成，但 `Script2VideoPipeline.__init__` 会构造 `BestImageSelector`、`CharacterPortraitsGenerator`、`CameraImageGenerator` 等对象，默认 `init_from_config` 还通过 `RenderBackend.from_config` 初始化渲染后端。因此 **text-only 是可停止在文本输出的代码分支，不等于完全不依赖渲染模块的独立环境**。是否能不改源码运行须用完整依赖与配置验证。

## 代码证据

- 原有快照：`docs/validation/XIA-59-shotplan/upstream/vimax/{storyboard_artist.py,script2video_pipeline.py,camera_image_generator.py}`。
- 对照索引：`docs/validation/XIA-59-shotplan/upstream/manifest.json`，其来源为 HKUDS/ViMax `main` raw URL，**没有固定上游 Git commit**。不能仅凭当前快照 SHA 声称已验证具体上游提交。
- 本轮复算 SHA 均与该清单一致；具体字节数及全 SHA 见 `preflight-manifest.json`。
- Eric 仓库读取时 HEAD `c96a8bc4f61fbcc4eea7500f2a16d101c039eb86`；工作区已有无关未提交变更，本任务不得触碰。

## C 剧本冻结

- 权威输入副本：`c-original-v1/script-C-frozen.txt`；SHA-256 `ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d`。
- 来源：`docs/validation/WAR-65/evidence/war-65-cd-original-execution-20261111.tar.gz` 内 `war-65-script-C/step2/script-C.txt`；提取字节哈希与 WAR-65 记录相符。
- 剧本包含原始场景、对白、编剧创作意图及实验边界。不能加入 D 样本的专属人物/空间卡。
- 尚未调用模型；角色抽取、Storyboard、镜头拆解、Camera Tree 均**无本次原始模型输出**，不能人工补写为原版结果。

## 依赖和阻塞

- Eric 默认 `python3` 缺失：`langchain`、`langchain_core`、`moviepy`；`pydantic` 与 `yaml` 可导入。仅检验了默认解释器；未证明 Eric 上其他隔离环境均不可用。
- 当前保存的 ViMax 源码是三个文件的快照，不包含 `agents`、`interfaces`、`utils`、`tools` 等完整依赖树；直接运行原版入口不可复现。
- `init_chat_model` 的实际配置、凭证、模型及是否产生远端/付费调用尚未冻结。按 WAR-66 边界，本轮不安装、不下载、不改部署、不调用未知费用的 API。

## 下一步

1. 确认授权可使用的完整 ViMax 仓库版本、现有隔离环境与文本模型调用方式；优先采用已有环境，不修改原始代码与配置。
2. 冻结 `model/config/prompt/输入`；使用 C 冻结输入执行原版 `plan_text_artifacts`，逐阶段捕获完整 JSON、原始调用与日志、校验及 SHA；保留失败证据。
3. 审阅每一阶段的实际镜头叙事选择、道具/站位传递、FF/Motion/LF 自洽与 Camera Tree 的限制；未解决问题如实记录。完成 C 后才推进 D/E。

**结论类型：** 以上流程为代码确认，运行阻塞为环境检查，任何模型行为均未知。不存在图像、视频或本次 ViMax 生成的文本产物。

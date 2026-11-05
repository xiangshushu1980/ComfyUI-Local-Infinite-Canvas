# XIA-27 — 内置工作流资源与安装路径审查

> 审查日期：2026-11-01。对象为当时 checkout（HEAD `99cd2d3`，分支 `codex/canvas-lab-rebuild`），只读源码/JSON 审查。没有下载资源、安装依赖、运行安装入口、连接或重启 ComfyUI，也没有 GPU 操作。本报告是该审查快照的 S 级静态证据，不等于第三方来源实时可用、许可证法律意见、安装测试或 WSL 实测；当前 checkout 信息见 [`restart-baseline.md`](restart-baseline.md)。

## 范围与盘点口径

- `comfyui-gateway/workflows/registry.json`：21 个已注册工作流条目，引用 18 个文件，其中 `h3-ref2va-drama-vdn.json` 和 `h3-ref2va-drama.json` 各由多个入口共用；另有 1 个内部工作流文件，共 19 个 JSON 文件。逐项 ID、类型、文件名见下表。
- `comfyui-gateway/resources/index.json`：8 个资源包、72 个资源条目（17 node、46 model/dir、7 pip、2 bake）。资源条目和包 ID 是完整的静态盘点；详细源 URL、大小、哈希、许可证声明及依赖均保留在该 JSON 的同名对象中，以下按来源/校验风险分组，避免复制整份可变索引造成两套维护入口。
- `workflows/*.json` 与资源依赖关系由 `resources/index.json` 的 `workflowDependencies` 声明；JSON 中存在依赖不证明该资源可下载、可安装或工作流可运行。

### 注册工作流清单（21 条）

| ID | 类型 | 文件 |
|---|---|---|
| image-z-image-turbo | image | `z-image-turbo.json` |
| video-h3-ref2va | video | `h3-ref2va-drama-vdn.json` |
| video-h3-t2v | video | `h3-ref2va-drama-vdn.json` |
| video-h3-frames | video | `h3-ref2va-drama-vdn.json` |
| video-h3-ref2va-novdn | video | `h3-ref2va-drama.json` |
| video-h3-t2v-novdn | video | `h3-ref2va-drama.json` |
| video-h3-frames-novdn | video | `h3-ref2va-drama.json` |
| video-esrgan_2x | video | `video-esrgan_2x.json` |
| video-seedvr2-upscale | video | `video-seedvr2-upscale.json` |
| image-krea2-aesthetics | image | `image-krea2-aesthetics.json` |
| image-seedvr2-upscale | image | `image-seedvr2-upscale.json` |
| image-esrgan-upscale | image | `image-esrgan-upscale.json` |
| image-qwen21 | image | `image-qwen21-edit-turbo.json` |
| image-moss-sft-8step | image | `image-moss-sft-8step.json` |
| image-moss-sft-50step | image | `image-moss-sft-50step.json` |
| image-qwen21-angle | image | `image-qwen21-angle.json` |
| image-krea2-four-view | image | `image-krea2-four-view.json` |
| video-h3-character-swap | video | `h3-character-swap-vdn.json` |
| image-moss-sft-int8-8step | image | `image-moss-sft-int8-8step.json` |
| image-moss-sft-int8-50step | image | `image-moss-sft-int8-50step.json` |
| image-krea2-turbo | image | `image-krea2-turbo.json` |

`workflows/_internal/video-rife.json` is present but is not one of those 21 public registry entries. `registry.json` workflow presence is configuration evidence only.

### 8 resource packs

| ID | Label | Declared workflow coverage |
|---|---|---|
| core | 画布与基础工作流 | none |
| moss | MOSS-Image | 4 |
| qwen21 | 千问 2.1 全能工作流 | 2 |
| zimage | Z-Image Turbo | 1 |
| krea2 | Krea2 Turbo | 1 |
| h3 | MiniMax-H3 | 7 |
| prompt-local | 本地反推/本地提示词 | none（本地提示词资源）|
| upscale | 超分 | 4 |

资源完整逐项索引：[`comfyui-gateway/resources/index.json`](../comfyui-gateway/resources/index.json)。以下按校验状态盘点 72 个 ID；来源与许可字符串请以索引对应对象为准。完整清单由上述权威索引承载。

**顶层资源对象配置 SHA256（32 条）**：`moss_image_sft_bf16`, `qwen3.5_9b_int8_convrot`, `flux2-vae`, `qwen_image_2.1_turbo_int8_convrot`, `qwen3vl_8b_int8_convrot`, `qwen_image_2.1_vae_bf16`, `qwen21_outpaint_lora`, `moss_image_sft_8steps_lora`, `moss_image_sft_int8_convrot`, `z_image_turbo_bf16`, `qwen_3_4b`, `ae`, `krea2_turbo_fp8_scaled`, `qwen3vl_4b_fp8_scaled`, `qwen_image_vae`, `z_image_turbo_int8_convrot`, `krea2_turbo_int8_convrot`, `krea2_four_view_lora`, `tespeed_moss`, `moss_guanlan_lora`, `h3_unet_singularity_ref2va_v13_int8`, `h3_latent_upscaler_3d_fp16`, `prompt_qwen_gguf`, `prompt_qwen_mmproj`, `prompt_florence_model`, `seedvr2_3b_dit`, `seedvr2_7b_dit`, `seedvr2_vae`, `esrgan_x2plus`, `esrgan_anime6b`, `esrgan_x4plus`.

**无资源级 SHA256**：node 无 SHA 的 16 条：`qwenmultiangle`, `inpaint_cropandstitch`, `kjnodes`, `h3_vdn_node`, `h3_te_speed_node`, `h3_audio_t8_node`, `h3_yc_nodes`, `h3_selflift_node`, `h3_solattn_node`, `h3_trt_vae_node`, `h3_vhs_node`, `prompt_llama_node`, `prompt_florence_node`, `prompt_te_man`, `seedvr2_node`, `qwen_angle_prompt`。model/dir 无 SHA 的 15 条：`h3_te_qwen3vl_32b_int8_convrot`, `h3_audio_vae_fp32`, `h3_lightx2v_8step_lora`, `h3_character_swap_lora`, `h3_vdn_stage_model`, `h3_vdn_stage_turbo_adapter`, `h3_vdn_stage_default_adapter`, `h3_vdn_stage_spec`, `h3_vdn_stage_metadata`, `h3_vdn_stage_linear_config`, `h3_vdn_stage_turbo_config`, `h3_vdn_stage_default_config`, `h3_vae_onnx_decoder`, `h3_vae_onnx_decoder_data`, `h3_vae_onnx_encoder`。另有 2 个 bake、7 个 pip 资源对象没有顶层 SHA；wheel 校验见下文。完整 target、来源和声明许可证见索引。

> 计数口径：脚本复核得到 72 条中顶层 `resources[].sha256` 有 32 条、无顶层 SHA 40 条（17 node 中 16 条无 SHA；45 model 中 15 条无 SHA；1 dir 有 SHA；2 bake、7 pip 无资源级 SHA）。另有 wheelMatrix 来源级 SHA（SageAttention 与 SeedVR2 wheel），不可与资源级 SHA合并；`prompt_llama_python` 的 URL 字符串映射没有 wheel SHA。来源级 SHA只校验对应固定 wheel，不证明其他 fallback 来源。

## 来源、固定性与许可证证据

- 模型与 LoRA 来源主要是 ModelScope / Hugging Face / `hf-mirror.com`，少数来自项目 ModelScope 数据集；多源回退提高可获取性，但常用 `master`、`main` 或 HF `resolve/main` 浮动分支，没有索引内 commit/revision 锁。登记的许可证是项目索引中的声明，不是本审查逐一核对的上游许可证原文或分发权证据。
- 绝大多数体积文件有预期大小及资源 SHA256；普通文件下载完成后比较资源大小，有资源 SHA 时再比较 SHA 后才 rename 到目标。HTTP 使用 `fetch` 且允许 redirect follow；来源域名/重定向目标没有静态 allowlist。校验值本身与索引同源，提供完整性检查但不形成独立签名或来源真实性证明。pip wheelMatrix 路径单独按选中 wheel 的 size/SHA 验证；`prompt_llama_python` wheel URL 映射没有这些校验值。
- 15 个 H3 模型/目录文件缺资源 SHA256，节点归档 16/17 无 SHA。若仅有 size，代码只能检查长度；同大小的替换内容不被识别。部分节点 source 显式 `verify:false`，跳过大小和哈希验证；虽有随包 `bundleDir` 可优先安装，损坏/缺失时会回退到这些浮动上游归档。
- `h3_vdn_stage_*` 多文件指向同一 `OpenVDN/vdn-minimax-h3` 浮动模型仓库的不同路径，无逐文件 hash。未审阅远端 revision、对象内容和 license 原文。
- 许可证缺口在索引中明示：`moss_guanlan_lora` 标为未知社区 LoRA；TE-Speed MOSS、TE-Speed MiniMax H3、SelfLift、SolAttn 等有“未声明 LICENSE”；TE_MAN 声明作者授权但无法在本任务内验证授权原件。打包是否满足各组件再分发条款未作法律判断。
- SeedVR2 依赖与 SageAttention 的 wheelMatrix 提供 URL/大小/SHA；其哈希会校验所选 wheel。`prompt_llama_python` 的 wheels 是按 Python 版本映射的 URL 字符串，没有 SHA/size 矩阵字段。多个 wheel 标记为 `win_amd64`；没有 Linux/WSL wheel 对照。源码/发布页 fallback 不等同于固定 wheel。

### 来源固定/校验重点（风险分组）

| 类别 | 数量/对象 | 静态发现 | 结论 |
|---|---|---|---|
| 有资源 SHA 的普通模型/归档 | 31 个对象 | 普通模型、LoRA 与部分随包节点；下载代码检查大小及可用 SHA | S 级校验配置，未实际下载核验 |
| 无 SHA 模型/目录资源 | 15 个 H3 条目 | 大小字段存在但无 SHA；多为浮动仓库路径 | 仅尺寸校验，内容身份未固定 |
| 无 SHA 第三方节点 | 16 个 | 多为 GitHub `main`/`master` archive；部分 `verify:false` | 浮动源码；归档身份与解压内容未固定 |
| pip | 7 个 | SageAttention、SeedVR2 的 matrix wheel 有固定 SHA；llama-cpp Python wheel URL 无哈希，且有 Windows 标签 | 不能据此认定 WSL/Linux 可装 |
| TRT 本机编译 | 2 个 | 输出依赖本机 GPU/驱动/TRT/节点编译器，不带产物 SHA | 属运行环境变更，不在本轮执行 |
## 安装入口、写入与副作用

1. Gateway 资源 API 经 `comfyui-gateway/src/resources.js` 创建安装任务：资源状态查询/计划为只读；只有调用 install 路径才运行下载/复制/pip/bake。界面检查状态与实际安装须区分。
2. `targetParts()` 限制目标首段为已知模型目录或 `custom_nodes`，并拒绝 `.` / `..`；通常写入 ComfyUI 根目录下模型或节点子目录。模型目录可按 ComfyUI `folder_paths`/extra model paths 解析到实际目录；资源路径本身不接受任意绝对目标。
3. 下载先写目标旁 `.part`，可 Range 续传；大小/可用 SHA 校验后 rename；锁状态写入 Gateway data。节点下载写入 `data/resource-downloads` 与同卷 `.canvas-install` 临时目录，解压后替换节点目录，尝试备份/回滚已有目录。存在取消时保留部分下载以续传的分支。
4. 节点安装以 `tar -xf` 为首选，失败后尝试 PowerShell `Expand-Archive`。源码没有在应用层逐个检查归档成员路径、symlink/hardlink 或解压炸弹配额；目前静态证据不能确认系统 tar/Expand-Archive 对恶意归档的具体处置，须单独审查或隔离测试。
5. pip 安装用配置/推断到的 ComfyUI Python 调用 `python -m pip install --disable-pip-version-check --no-input <wheel>`；wheel 缓存落在 Gateway data，某些矩阵会先备份并在失败时回滚包。没有看到统一的最小权限/虚拟环境隔离保证。运行库还可请求 `launcherControlUrl/restart-comfy`；这属于改变 ComfyUI 服务状态的显式副作用。
6. 两个 `bake` 资源调用项目 `scripts/build-h3-trt-vae.py`，再执行 ComfyUI-H3VAE_TRT 的 `compile.py`，可能占用 GPU、CPU、内存、磁盘并生成 TRT engine；不属于只读安装。
7. 资源安装可能对配置的 ComfyUI 根、额外模型目录、`custom_nodes`、Gateway `data/`、ComfyUI Python 环境及（若配置）launcher 控制端产生文件、网络和进程副作用。设置保存还可能写 `data/directory-settings.json`，并在自动目录同步路径写入 ComfyUI `extra_model_paths.yaml` 的 managed 区块。
8. 单独的 Gateway Comfy Bridge 会把 `comfyui-gateway` 内置前端扩展复制/覆盖到探测到的 ComfyUI `web/extensions` 目录。此路径不同于资源 install API；在 WSL 审核中须确认是否关闭/调用。

## WSL 兼容性结论（源码证据）

- Gateway 本身使用 Node.js `fetch`、文件系统、路径、`tar` 和子进程接口，部分逻辑有 Linux 分支；但“能在 WSL 启动”不推出资源安装栈兼容。
- 多处资源描述和处理是 Windows 导向：`prompt_llama_python` wheels 明确 `win_amd64`；SageAttention wheel matrix 同为 Windows；SeedVR2 OpenCV 固定 wheel 为 `win_amd64`；安装失败提示引用 Windows 启动器。Linux 上 pip 若选择这些 wheel 将不兼容。不能安装/执行以验证。
- `pythonFromRunningComfy()` 在 `process.platform !== 'win32'` 直接返回空值；用户指定 Python 路径或自动发现其它路径是否足够，需逐路径验证。文件选择器依赖 Windows PowerShell/System.Windows.Forms，因此 WSL Gateway 的该 UI 能力不可用。
- Windows 目录 fallback（C:/、D:/、E:/ComfyUI）和 Windows Launcher 控制消息体现跨平台残留。tar 对 GNU/Linux 有自然可用性，但应用没有压缩包成员安全审查，因此仅支持常见归档命令不等于安全/兼容通过。
- 目标是纯 WSL 部署：前端/Gateway/Agent 可另行研究；ComfyUI 的真实 WSL 根目录、Python、额外模型目录与目录权限未核实。本次没有安装资源，也没有修改现有 ComfyUI。

## WSL 适配建议（供后续决策）

1. 建立 Linux wheel/runtime matrix，按 ComfyUI 实际 Python、Torch、CUDA 与架构分别锁定来源、尺寸、SHA；不满足的 Windows wheel 应标阻塞并隐藏安装入口，而非试装。
2. 对 GitHub 节点归档锁 tag/commit 与 SHA256；仓库若浮动分支回退，应至少校验下载归档清单/固定提交，避免仅按字节数接受。
3. 对无 SHA 的 H3/VAE 文件补可信哈希来源或明确列为未验证下载；许可证/社区权重分发证据单独归档。
4. 解压前枚举归档并拒绝路径穿越、绝对路径、危险链接和异常膨胀率；测试失败回滚、保留旧目录、磁盘满和取消路径。
5. 把 Windows 文件选择、自动 restart-comfy、注册表/启动器控制路径与 WSL 流程隔离；安装按钮对实际写入根目录和将执行的命令给出可见摘要。
6. 在获准后，仅用临时目录和独立 Python 做 Mock/测试；不针对共享 ComfyUI 做安装、pip 修改、节点复制、引擎编译或重启。

## 尚未核实 / 验证限制

- 没有对外部 URL 发请求：来源当前是否存在、branch 当前指向、远端 checksum、文件大小实际匹配均未核实。
- 没有逐个打开上游 LICENSE、模型卡、作者授权原件；索引中的 license/说明只是项目声明。
- 未运行安装器或测试，未验证下载续传、失败回滚、恶意归档处置、权限、WSL 下载/解压及 Linux pip 选择结果。
- 未实测 21 个工作流所需自定义节点、模型、显存条件和结果质量；资源索引只提供静态映射。
- 本地 ComfyUI 地址、实际使用的模型根、Python 环境、额外路径和服务控制接口均未探测。

## 当前 checkout 增量盘点（2026-11-01）

> 本节是对上述 `99cd2d3` 快照的只读增量核对，不代表已对新增资源完成同等级的来源、许可证、下载与安装路径审查。当前项目目录已迁移，当前分支为 `main`；详见 [`restart-baseline.md`](restart-baseline.md)。

- 当前 checkout：`/home/sean/projects/canvas-lab`，HEAD `eee8dac`（`[文档] 更新旧项目资料路径`），分支 `main`；tracked tree clean。工作树此前保留的两个 prompt 修改不在此 checkout 当前状态中；`.codegraph/` 为本地索引。
- 只读解析当前 `registry.json` 与 `resources/index.json`：21 个注册工作流条目、18 个唯一引用文件、9 个资源包、73 项资源（45 model、18 node、7 pip、2 bake、1 dir）；33 项有顶层 SHA256，40 项无顶层 SHA256。旧快照的 21/19、8/72、32/40 计数不代表当前索引。
- 相比旧快照新增 `krea2-four-view` 资源包及 `krea2_edit_node` 节点资源；该节点在当前索引有资源级 SHA256。此项只确认索引存在和字段计数，未核远端 revision、归档内容、许可证原文或安装代码行为。
- CodeGraph 对 `resources/index.json` 无唯一索引项，不能用该索引读取 JSON；对 `resources.js`/`setup.js` 的符号查询返回安装/路径代码及调用信息。没有编辑这些应用文件，也没有执行安装入口、测试、网络请求、ComfyUI 操作或 GPU 工作流。
- 当前建议：旧快照可用于历史审查；如要满足“当前 checkout 全部资源逐项审查”的验收口径，需将新增资源纳入逐项来源/许可/安全复核。外部来源和 WSL 实际安装兼容仍未验证。

## 节点下载与导入路径（2026-11-01，只读源码审查）

- 资源中心对 `type: node` 的资源调用 `installNode`，目标固定为 `<ComfyUI>/custom_nodes/<目录>`；任务开始时若目标目录已存在就标记 skipped，不升级或覆盖现有节点。否则先创建 `<ComfyUI>/.canvas-install/<资源ID-进程号-随机值>/` 临时目录。
- 安装器优先检查 `bundleDir`，其相对路径以 Gateway `config.rootDir`（`comfyui-gateway`）解析；若目录存在，递归复制到临时区，寻找含 `__init__.py` 的节点根并 rename 到目标。该直拷贝分支没有对目录内容/文件数/哈希做清单校验。失败会回退 `sources`。
- 当前 checkout 的 18 个 node 资源都声明 `bundleDir`，但所声明目录在本 checkout 均不存在。因此本 checkout 静态上会进入 source 路径；这只代表仓库文件状态，不证明发布包或其他安装包中也缺失。索引中只有 `tespeed_moss`、`qwen_angle_prompt` 使用内置 ZIP/目录 source，且相应 `resources/nodes/...` 路径在此 checkout 也不存在；`krea2_edit_node` 有 SHA256 的多个 HTTP source。其余 node 当前索引均无可用 source，安装器会报告没有配置下载源或因缺少可信 SHA 而拒绝安装。
- HTTP source 使用 Node `fetch`、跟随 redirect、写临时 archive，失败时可尝试同一资源的下一 source。对非 bundled node ZIP，`verifyNodeArchive` 强制要求 64 位十六进制 SHA256，并拒绝 `verify:false`；可选 size 也会核对。随后以 `tar -xf <basename> -C <dest>` 解压；仅当 tar 失败才调用 Windows PowerShell `Expand-Archive`。所以解压主路径是跨平台命令，但回退明确依赖 Windows PowerShell；WSL/Linux 没有该回退。
- 解压完成后递归寻找 `__init__.py`，将原目标目录先 rename 到临时 backup，再将新节点目录 rename 到 `custom_nodes`；替换失败时尝试恢复 backup。任务结束删除本次 `.canvas-install` 临时根。安装器没有在应用层先枚举并验证 ZIP 成员的路径穿越、symlink/hardlink、膨胀配额或内容清单；归档有 SHA 只验证字节与索引期望一致，不代表上游可信或成员安全。
- pip 资源由独立阶段 `installPipResource` 处理，而非节点 ZIP 解压的一部分；节点索引项本身没有统一的 requirements 安装/节点代码执行阶段。选择 pip 资源会写入推断/配置的 ComfyUI Python 环境，可能安装或替换包。`pythonFromRunningComfy` 明确仅在 `process.platform === "win32"` 下通过 PowerShell 查 ComfyUI 进程；非 Windows 返回空值，因此 WSL 必须依赖显式 Python 配置或 Linux 路径发现逻辑。源码未证明当前 WSL Python 选择正确。
- WSL/Windows 差别：目标路径、Node 文件操作与 `tar` 主解压路径没有 Windows 必需调用；Windows 专属参与点是 tar 失败后的 `Expand-Archive` 兜底，以及运行中 ComfyUI Python 的 PowerShell 进程探测。资源源自身还可能是浮动 URL、无 SHA 或 Windows wheel，须按资源逐项判断；本节没有运行安装、pip、测试或 WSL 归档验证。

## 复核命令（只读）

```bash
node - <<'NODE'
const fs = require('fs');
const w = require('./comfyui-gateway/workflows/registry.json');
const x = require('./comfyui-gateway/resources/index.json');
console.log(`workflow entries: ${w.workflows.length}`);
console.log(`workflow files: ${new Set(w.workflows.map(e => e.file)).size}`);
console.log(`packs: ${x.packs.length}; resources: ${x.resources.length}`);
console.log(x.resources.reduce((a, r) => (a[r.type] = (a[r.type] || 0) + 1, a), {}));
console.log('no top-level sha:', x.resources.filter(r => !r.sha256).map(r => r.id).join(', '));
NODE
```

记录：源码与 JSON 静态阅读；没有执行上述可选复核脚本，本表计数来自只读解析输出。没有改动应用代码、依赖、服务、ComfyUI、资源文件或 GPU 工作流。工作树原有两个 Gateway prompt 修改、`.codegraph/` 与未跟踪 `node_modules` 均保留。

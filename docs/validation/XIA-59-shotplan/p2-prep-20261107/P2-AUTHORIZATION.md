# XIA-59 P2 视频实验审批包（待用户批准）

状态：**提案完成，未授权、未排队、未生成**。任何 GPU/H3 提交须等待用户对本文件所列方案明确批准。

## 候选小样本

| 组 | 目标 | 输入版本 | Seed | 次数 | 计划规格 |
|---|---|---|---:|---:|---|
| E2-A | 同镜内对白中断：检验明确的实际发声与动作时点是否被 H3 实现 | `E2-A-same-shot.md` | 34001 | 1 | Ref2VA, 8s, 1024×576, 24fps, 8 steps |
| E2-B | 跨镜对白中断：同素材/seed/规格，唯一关键变量是中断跨越 4.20s 切点 | `E2-B-cross-shot.md` | 34001 | 1 | 同上 |
| E3-D | DirectorSKILL 交杯 v2 结构诊断样本 | 原始 `p1/02-handoff/director/prompt-v2.txt` | 34001 | 1 | 同上 |
| E3-M | 简化状态控制：同 Beat、相同三镜与切点，保留唯一杯、A 右手推、B 左手接、一次 A→B 归属变化；省去未测角度/距离与额外演出描述 | 待批准后依据 E3 约束编译的独立新候选 | 34001 | 1 | 同上 |

这是两组匹配的诊断对照，共 4 条；不比较跨场景的分数，也不排名导演方法。若审阅时希望更小规模，可仅先跑 E2-A/B 两条，把 E3 留到后续审批。单 seed 只用于低成本排错；任何稳健性结论须另批准重复 seed。

## 已有素材和执行依赖（只读核验）

- 真正 reference 图，均在 `/home/sean/projects/ComfyUI/input/`，没有复制进 XIA-59，也不改 XIA-56：
  - Picture 1 `XIA56_ref1_woman.png` 490×535, SHA256 `8b846eabbc58600c43c36d322ab341ab13034cdbca38cfb3c1f91ea18b4ae5d7`
  - Picture 2 `XIA56_ref2_man.png` 504×535, SHA256 `d70ec498a488d6ee57710162e12606e993a3deeb41a3286f183e69ca0c949554`
  - Picture 3 `XIA56_ref3_cafe-two-shot.png` 1024×576, SHA256 `721617ab9d9f761c4c515da270de72fe3c7087b381a1a35e34412c4dbada75bf`
- 官方兼容 H3 Skill 冻结副本与本机版本 SHA 相同：`SKILL.md` `12f813d46f7c120c033d538b6c785837b94bdafd41498ed865a099c29331985d`；`ref-en.txt` `1e574f356716ad55612247ffb7bbccbcdb484ad96599d63c7dca1af186b1fab7`。
- LoRA 存在：`minimax_h3_ref2v_turbo_8step_v1.1_768p_comfyui_bf16.safetensors` SHA256 `e56863a7524e0300729cbb7b64cc8b548d90698c1abbf7d83898b0122fbe1e81`，权重 strength 1.0。输出仍为 1024×576，不能称 768p。
- XIA-56 既有成功 API JSON 用 H3 Ref2VA INT8、`res_multistep`、`steps=8`、1024×576、192 frames、24fps、seed 34001、`ref_image_size=match`；实测本轮只读过往 history 表明 ComfyUI 0.44.0 `/system_stats` 可达，队列当时 0 running/0 pending。`nvidia-smi` 不在当前 shell 的 PATH，故**当前 GPU 显存状态未核验**。
- 实图检查：Picture 1 与 Picture 3 可见 A 右手握着杯把。所选 H3 文本将 Picture 1 用作身份/服装来源、Picture 3 用作场景/左右布局参考，未将它们指定为首帧或 storyboard pose anchor；因此这是**潜在姿态干扰**而非已证明的硬冲突。P2 的 E2 Prompt 必须维持该参考职责边界；E3 使用原 Director v2 时保留其原始文本版本并记录相同素材条件。QC 需检查开头 A 手/杯状态，以及是否发生提示要求之外的提前放杯/触杯。若用户要求图片姿态作为字面首帧锚点，当前姿态与 Beat 的“杯未移动/不触杯”不兼容，应先停止该组并另行批准替代参考方案；本轮没有改图或搜寻并挑选未核验素材。
- 项目内另有官方兼容工作流 `/home/sean/projects/comfy-ops/workflows/minimax_h3_vdn_ref2va_img_vid_api.json`，但它绑定 Krea 图片输入，不能直接当本实验的可提交版本。审批后需从 XIA-56 API JSON 复用已验证的模型/规格参数，并只替换 prompt / 参考图片 node 路径；另存独立 JSON/API 与 ComfyUI run record，不改原工作流。

## 成本与风险估算

XIA-56 同规格单条成功作业历史：136.2、136.4、136.5、237.7 秒（冷热缓存混杂）；四条预计约 9–16 分钟 GPU 执行时间，另需约 30–45 分钟人工全片声音/画面复核。没有计费 API 单价；本机 GPU 的货币成本为本地机会成本，需按实际运行机账单/电费核算，本提案不编造金额。运行前仍需确认 GPU 空闲、工作流所有模型和参考路径解析正确及 ComfyUI lease/资源协调。

主要风险：中文短片段发音、人物声音身份、嘴型、跨镜音频衔接、杯子/手指接触、H3 忽略指定硬切、模型结果对 prompt 敏感、单 seed 不代表稳定性。对 E3 额外标注 Director 候选角度/距离是规划目标，不是图像测量。

## 逐片 QC 表

1. 先记录 API prompt、workflow SHA、参考图 SHA、模型/LoRA 文件名与 SHA、seed、采样器、steps、尺寸、时长、fps、提交 ID、history 起止时间、MP4 SHA。
2. 自动 QC：视频 stream 为 8 秒/192 frames/1024×576/24fps；检查编码音轨存在；场景切点检测仅作定位线索，检测到 0 个硬切不等于没有构图切换。
3. 人工完整审片并听音：对白字词/发声起止/停顿/中断位置/跨切连续性；人物身份、左右座位、杯子只出现一个；A 右手单次推杯、B 左手接杯且仅一次归属变化；中断时谁先行动；场景轴线、嘴型、动作因果与结尾状态。每项 pass/fail/uncertain 并附时间码。
4. 若生成不符，先归类 Beat 未定 / Shot Plan / H3 编译 / reference binding / H3 执行；不在当批中临时返修重跑。任何额外 seed 或修订都需新批准。

## 停止条件

首批最多 4 条（或用户确认的 2 条 E2 子集），无自动重试。引用素材不可用、工作流有未解节点依赖、ComfyUI 资源冲突或当前显存无法安全运行时停止并报告。完成人工审片后交付证据，再决定是否扩大样本。

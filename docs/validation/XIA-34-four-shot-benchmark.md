# XIA-34 · 8 秒四镜头导演基准 v1

状态：测试**输入规范与空白结果模板**，不代表生成视频已实测。日期 2026-11-05。依据 XIA-32 已审计的 Gateway/H3 接口；用于 XIA-33 离线 Skill 对照、XIA-39 单次多镜头生成、XIA-40 分段生成/剪辑。

## 1. 固定案例 A（T2VA，零外部素材依赖）
- 用途：消除外部图片、视频版权和文件不同步引起的变数。输出 16:9、24 fps、8.000s 播放时间，**192 帧**，不预设文本上屏、台词或背景音乐。
- 固定导演意图：一只**赤狐**在清晨的湿润针叶林中发现浅溪对岸的小石台，奔跑、跃过溪流、落地并回望。狐狸须保持橙红皮毛、白胸、黑色四肢、左耳小缺口；环境、光线、方向、溪流位置不变。自然声：轻微风声、鸟鸣、水声、奔跑/落地声。无音乐。
- 正向完整输入（锁定，供各 Skill/模型使用）：
  `An orange-red fox with a white chest, black lower legs and a small notch on its left ear crosses a shallow forest creek at dawn. Wet evergreen forest, soft cold sunlight, mossy stones, same creek and same fox across all four shots. Four editorial cuts at 1.833 s, 3.667 s, and 5.500 s. Shot 1: side-view medium-wide shot: fox runs left-to-right along creek bank, paws kicking up droplets. Shot 2: low close shot: its paws plant firmly on a mossy rock before the leap. Shot 3: tracking side shot: one continuous plausible jump over the narrow creek, body moves left-to-right. Shot 4: medium shot from opposite bank: fox lands, recovers balance, pauses and looks back toward the creek. Preserve identity, anatomy, motion direction, light and spatial continuity across cuts. Natural water, footsteps, leaves and distant birds; no dialogue, titles or music.`
- 不允许运行过程中重新生成参考角色或补编剧本；如果真实实验需要参考图，另建 B 类变体，不与 A 类混合统计。

## 2. 固定时间轴 / Shot Deck
| ID | 半开区间（帧） | 时间（秒） | 时长 | 镜头动作、景别与验收可观测点 |
|---|---|---|---|---|
| S1 | [0,44) | 0–1.833 | 44f / 1.833s | 中远景侧拍，狐狸由左向右跑向河边；身份/方向/环境 |
| S2 | [44,88) | 1.833–3.667 | 44f / 1.833s | 低机位脚部特写，踩在苔藓石上起跳蓄力；动作匹配 |
| S3 | [88,132) | 3.667–5.500 | 44f / 1.833s | 横向跟拍，单次完整跃过窄溪；运动连续性 |
| S4 | [132,192) | 5.500–8.000 | 60f / 2.500s | 对岸中景落地、稳定、回望；身份/场景空间一致 |
明确：四镜头平均必须为 2 秒；前三镜头可各 1.83 秒，但第四镜头必须 2.5 秒，不能宣称四个镜头均 1.7–1.9 秒且总计 8 秒。

## 3. 双路径实验，不混淆生成时长与剪辑时长
- A 单次生成：向 H3 提交一个约 8 秒 T2VA 任务，提示词包含 4 shot/cut 时间；**切点是模型希望遵循的语义指令，不是保证的精确编辑点**。结果直接检查观测切点。
- B 分段剪辑：每个镜头独立生成**模型实际支持的时长**（参照该模型/工作流可用区间，例如 4–15 秒，必须以当前部署核实为准），然后从生成片段选择性提取 44f / 44f / 44f / 60f，按照半开区间拼接为 192f；不要提交 1.83 秒生成任务。必须记录采样片段的 source in/out frame、解码 fps、是否变速、音轨跨切点策略。
- 同一 seed 仅作为尽可能一致的条件；分段任务间 seed 相同不能保证角色一致。A/B 采用相同主导演意图和角色锚点。
- 本地 `h3EffectiveDuration` 依据 `ceil((24*t-5)/17)*17+5` 计算帧数；记录 requested/effective/decoded durations，不能用 requested 冒充实际生成时长。
- 现成测试素材：`comfyui-gateway/mock/assets/mock.png`、`ref2.png`、`ref3.png`（512×512，仅供接口 smoke）、`mock.mp4`（1 秒，仅供响应/拼接 smoke）；**不得将 mock 媒体计入画质/角色连续性的正式成绩**。历史 `data/outputs/*.mp4` 暂不入基准，缺少可核对的 prompt/seed/版权来源映射。

## 4. 固定记录口径
- 可复现标识：`case_id=XIA34-A-v1`、`prompt_sha256`、`repo_commit`、`gateway/comfy/VDN/workflow versions`、`model checkpoint/LoRA hash`、`hardware`、`mode`、`seed`、`width,height,fps`、`requested/effective/decoded duration`、`generation params`、`reference assets SHA256`、`started/finished timestamps`。
- 切点观测：人工标注帧级切点 `observed_cut_frame` (如未出现填 null)；偏差 `abs(observed_cut_frame - target_cut_frame)/24` 秒；每点独立记录及 max/mean，缺失切点单独计数（不可填 0 秒）。
- 镜头匹配：四个 shot 各自检查景别、动作里程碑、摄像机角度（pass/fail + 证据帧），记录多余镜头/漏镜头。
- 角色连续性：耳缺口、胸毛、四肢颜色、体形四项各按 0/1/2（不符/部分/符合），加总 0–8；动作连续性按空间方向、起跳承接、跨岸轨迹、落地承接各 0/1/2，总分 0–8，记录矛盾的相邻帧。
- 画面质量：按 0–5 评分可读性、闪烁/形变、运动清晰度（越高越好）；多人评审报告平均数与原始分，无法观察记 N/A。
- 音频：环境连续、动作同步、跨镜头断裂，各 0/1/2；静音/无音频单列，与原设无音乐不等价。
- 时间成本：提交到首帧、提交到完成、后处理和总 wall time 秒；GPU 型号、峰值 VRAM、功耗信息如不可用填 null；云计费币种/credits、调用次数、人工时长分别列出，不能假设本地免费（电费/折旧可选）。
- 重试及失败：记录每次尝试、HTTP/Comfy 错误、OOM、超时、空音频、输出不达标；成功率 `successful_attempts / all_attempts`，失败次数为 `all_attempts - successful_attempts`；单次与多次 run 分开报。
- 不可比较情况：不同尺寸/模型/seed/参考图/音轨策略须作为单独实验组；无可回放文件、无可追踪参数时标记不可复现。

## 5. 空白结果模板（每个 run 复制填写）
```json
{
  "case_id": "XIA34-A-v1", "route": "single|segmented", "run_id": null,
  "prompt_sha256": null, "repo_commit": null, "workflow_id": null,
  "model_hashes": {}, "seed": null, "references_sha256": {},
  "hardware": null, "params": {"fps":24,"width":null,"height":null},
  "duration_sec": {"requested":8,"effective":null,"decoded":null},
  "target_cut_frames":[44,88,132], "observed_cut_frames":[null,null,null],
  "missing_cuts":null,"mean_cut_error_sec":null,"max_cut_error_sec":null,
  "shot_checks":[null,null,null,null],
  "identity_score_0_8":null,"action_score_0_8":null,
  "visual_scores_0_5": {"readability":null,"artifacts":null,"motion":null},
  "audio_scores_0_2":{"ambience":null,"sync":null,"cross_cut":null},
  "latency_sec":{"first_frame":null,"generation":null,"postprocess":null,"total":null},
  "cost":{"currency":null,"amount":null,"credits":null,"calls":null},
  "attempts":null,"failures":null,
  "source_clip_ranges":[], "output_path":null,"artifact_sha256":null,
  "notes":"Not executed — template only"
}
```

## 6. 验收范围与后续
本 issue 仅交付**固定输入和结果口径**；无需启动 ComfyUI 或 GPU。XIA-39/XIA-40 负责填真实 run、人工标注与可复核证据。任何正式验收不得以模型提示词结构通过或 mock 视频代替生成质量。
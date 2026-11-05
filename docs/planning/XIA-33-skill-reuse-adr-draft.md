# XIA-33 · Skill 复用调研与 ADR（初版，待决策）

2026-11-05；状态：**进行中**。研究范围只读，未安装 Skill、未调用付费 API、未启动 GPU。统一输入见 [XIA-34-four-shot-benchmark.md](../validation/XIA-34-four-shot-benchmark.md)。以下「离线手动试写」是按公开 SKILL 规则人工制作的结构样例，**不是**两套 Skill 通过相同 LLM 实际运行得到的实测质量结果。

## 1. 可追踪候选 / 复用矩阵
| 候选与来源 | 版本 / License 状态 | 已检查运行依赖 / 安全边界 | 与项目重合 | 暂定四选一 |
|---|---|---|---|---|
| [MiniMax H3 h3-prompt-writing](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md) | upstream main，2026-11-05 访问；仓库声明 **MiniMax H3 Community License**，**尚未逐条确认 Skill 内容独立再分发授权**；具体 SHA 待补 | SKILL.md + base/ref 两份 reference；文本规则，本身不需外部 API/Hub；不应执行不可信样例中的工具调用 | 与 `comfyui-gateway/prompts/h3-lora/training-prompts.json` 和 `src/h3-lora-workflow.js` 部分重复 | **仅借鉴规则**（授权确认后可进一步封装/直接阅读；不盲拷贝全文） |
| [MiniMax 3d-animation-short-generator](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/3d-animation-short-generator/SKILL.md) | 同上，Hub 绑定 | 依赖 Hub 专属 `hub_generate_video` / 画布 choice cards，含模型生成调用，隐私/付费边界由 Hub 决定 | 对应 Canvas Agent 中已有画布编排与视频提交 | **仅借鉴规则**（审核关口与镜头流程），不安装不移植 |
| [DirectorSKILL / cinematic-director](https://github.com/wuwangzhang1216/DirectorSKILL/blob/main/SKILL.md) | README 声明 **MIT**，现行 v2.0.0 结构（A–J）；需锁具体 SHA/比对 LICENSE | SKILL.md + references + assets，含 Shot Plan (D)、Motion Prompt (F)、Continuity (G)、Edit Plan (I)；规则型，可只读；默认安装路径、不同模型 adapters 不宜直接赋予执行权 | Shot/Beat/编辑计划与 XIA-36 重合，但非可编辑 Canvas IR；其适配器并非本地 H3 | **封装适配（候选）**：只读提示词和表格模板，保留 Canvas 自有时序/审核结构 |
| [Bdandc/storyboard](https://github.com/Bdandc/antigravity-skills/blob/main/storyboard/SKILL.md) | main，许可证/具体 SHA 尚未确认 | 读 `CLAUDE.md`，输出 shot table；默认前提是已有脚本和 art direction，存在读取本地上下文边界 | Shot Deck 输出可作形式参考，但与不做剧本分析的产品目标存在输入冲突 | **仅借鉴规则** |
| [Higgsfield DoP](https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-dop) | 闭源平台，非可复用 Skill | 预设摄影运动 + 图生视频 + 付费 credits；非本地 H3 | 摄影参数词汇重合 | **仅借鉴规则**（分类：镜头运动、镜头幅度、速度、取景等） |
| [TapNow Agent](https://docs.tapnow.ai/en/docs/agent/tapnow-agent) | 闭源产品，非可复用 Skill | 节点上下文→选择工具→审核→执行→定点修改；平台网络/隐私不在本地控制 | Canvas Agent 已有画布上下文/节点工具 | **仅借鉴规则**（可暂停/审核/只改指定节点） |
| [Topview generate skill](https://github.com/topviewai/skill/blob/main/topview-generate/SKILL.md) | main，许可/SHA 待查 | routing → 其 API/Canvas；在线生成需 API key、平台计费与数据上传；含 storyboard API | 已有 Gateway 任务流程，非本地 H3 | **不采用为运行依赖**，仅看多段视频与 Canvas workflow |

证据：MiniMax 官方 [Skills README](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/README.md) 明确 1 个通用提示词 Skill + 8 个 Hub 风格 Skill；[MiniMax README](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/README.md) 说明通用 Skill 与 Hub 专用的兼容差异。[DirectorSKILL README](https://github.com/wuwangzhang1216/DirectorSKILL/blob/main/README.md) 声明 MIT / v2 A–J。Topview [Storyboard API](https://docs.topview.ai/reference/storyboard-submit-task) 实为异步计费图片网格，不是完整本地视频剪辑。

## 2. 统一 8 秒四镜头案例离线样例（规则手动演练）
共同固定输入：XIA-34 A，狐狸过溪，目标切点 1.833 / 3.667 / 5.500 秒，24 fps，8 秒，无台词/字幕/BGM。

### 2.1 按 MiniMax h3-prompt-writing Base 模式规则输出的**人工试写**（非模型/Skill 运行结果）
```text
integrated_multimodal_description: [Shot 1] At dawn in a wet evergreen forest beside a narrow creek, the same orange-red fox with a white chest, black lower legs and a small notch on its left ear runs left-to-right along the near bank. Side-view medium-wide framing follows the fox and flying droplets. [Shot 2] At 00:01.833, cut to a low close-up of the same fox's paws planting on a mossy rock; its body compresses before takeoff, still directed left-to-right. [Shot 3] At 00:03.667, cut to a side-tracking view of one physically continuous leap across the shallow creek. Keep identical fur markings, cold dawn light, water direction and creek geography. [Shot 4] At 00:05.500, cut to a medium view from the opposite bank as the fox lands, regains balance and turns its head back toward the creek. The final frame holds the same fox in the same location.
overall_soundscape: A continuous quiet creek, distant birds and a faint breeze in wet branches; synchronized paws, splashes, takeoff and landing carry through the cuts without a change in forest ambience.
non_diegetic_music: N/A
```
结构检查（人工）：3 个固定字段和顺序 ✓；Shot 2–4 递增切点 ✓；动物身份可复核 ✓；音轨贯穿 ✓；**H3 实际切点准确性未知**；API 与本地工作流尚未运行。

### 2.2 按 DirectorSKILL Shot Plan D / Edit Plan I 形式的**人工试写**（非模型/Skill 运行结果）
| Shot | Time / Frames | Framing / Camera | Event / Match | Risk / Gate |
|---|---|---|---|---|
| 1 | 0–44f | side medium-wide tracking | fox runs → mossy rock; match left-to-right | G1: ear notch and creek geography consistent |
| 2 | 44–88f | low close-up fixed | foot plant and compression → leap | G2: match on action, paws and rock |
| 3 | 88–132f | side tracking | one single jump; same travel direction | G3: no teleportation or extra limbs |
| 4 | 132–192f | opposite-bank medium | land → recover → look back | G4: same fox, wet forest, water direction |
编辑说明：切点以 24fps 目标帧为准，hard cut；镜头 1–3 44f、镜头 4 60f；独立生成时切的是符合模型时长下限的源片段，不能把 44f 当作 H3 原生生成时长。音频溪流 ambiance 尽量使用一条连续底轨，动作声以画面位置匹配。

### 2.3 逐项对照（仅证明规则表达能力，**不是效果评分**）
| 维度 | H3 官方规则手动试写 | DirectorSKILL 模板手动试写 |
|---|---|---|
| 时序 | 能在 prompt 中明确写 00:01.833/03.667/05.500 | 能以帧半开区间明确剪辑表 |
| 动作与空间 | 文本要求连续，生成是否遵循待测 | 显式 match-on-action/Gate，仍需实际视频验证 |
| H3 适配 | 符合 3 核心字段；本地模式需名称映射 T2VA→T2AV | 不含本地 H3 特定字段，需极薄转换 |
| 可编辑性 | 输出是一段提示词，非 Canvas Shot IR | Shot 表易转换，但缺稳定节点 IDs、素材引用 |
| 离线/稳定性 | 文本规则不需网络；重放一致性需同一模型多次 run | 规则不需网络；重放一致性需同一模型多次 run |

## 3. ADR-初版：Reuse First / Adapt Second / Build Last
**建议（待用户确认）**：
1. **不再重造 H3 官方提示词语法**。现有 `training-prompts.json` + `h3-lora-workflow.js` 已实现基础模式/参考模式结构，下一步应做逐条差异测试和版本更新策略。官方 Skill 原始规则的复制或打包需先核实其 LICENSE 与适用范围。
2. **缩小 XIA-36 自研范围**：不用再做通用导演知识库/剧本拆解/模板库。只做 **用户意图 → 可编辑、带稳定 IDs 和素材引用的 Shot/Beat 结构 → 人工审核**；导演 Shot Plan 技巧通过独立可替换的只读模板适配器注入。
3. **缩小 XIA-38 自研范围**：不是再训练/实现通用 prompt writer，而是 **Shot IR → 现有 H3 模式及提示词优化器的薄编译层**（时码、切点、音轨、引用角色一致性、T2AV/Ref2AV 约束校验）。
4. **禁止直接重建** Canvas Agent 的节点读写、Gateway 视频提交/状态、H3 LoRA 优化、Higgsfield 的闭源摄影 preset 模型、TapNow 的闭源画布。以现有接口编排。
5. 风险：同一个 8s 任务内部四个 hard cut **不保证** H3 对时。Shot Planner 只负责计划，XIA-39/XIA-40 的人工标注视频实验决定采用单次还是分段路径。

## 4. 未达到 XIA-33 完成条件的证据缺口
- 具体 upstream git commit SHA/更新时间和所有候选 LICENSE 文本尚未冻结；远端 GitHub API 触发限流，部分 raw 路径未能稳定读取。不要把 README 的许可证声明自动理解为全部内容都可再分发。
- 尚未完整审阅 DirectorSKILL 的 `references`、`assets`、`evals` 与 MiniMax 官方 `base-en.txt/ref-en.txt` 的锁版本全文，未形成可机器复算的两套 Skill 同模型多次运行结果。
- 需要用同一可控 LLM 在不安装外部 Skill、不授权工具调用的前提下读取固定文本，对 **实际输出** 做至少两次同输入离线比较，再由人工评测镜头规划的稳定性；上面的试写只是设计验证，不能宣称已达到真实样例验收。
- 等用户参与确认 XIA-36、XIA-38 的自研缩减/适配方案，再更改任务范围。
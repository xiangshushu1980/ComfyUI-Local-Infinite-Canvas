# XIA-59 · P0 可追溯文本分镜对照（启动记录）

## 2026-11-06 用户更新：模型与阶段门

已完成的 P0 正式批次由 `deepseek/deepseek-flash`、thinking off 生成，原始材料及案例对照原样保留；不因模型选择重做。若发现影响结论的具体证据缺口，先向用户说明原因与拟补测范围。

后续文本生成或编译由 Codex 或 Codex subagent 直接完成，不通过 DeepSeek、Pi 或其他外部 LLM API 代为生成；记录能确认的模型和执行条件，无法确认的版本明确标记未知。跨模型结果分别标注来源，不将模型差异直接归因于 Skill 或方法。`runner/run_p0.py` 是历史 DeepSeek/Pi 批次的可审计记录，不用于后续生成。

当前先提交并讨论 P0，等待用户确认才进入 P1；获准后使用冻结的 H3 Skill 静态编译各 Shot Plan，另保留独立 Beat→H3 直出基线。P2 视频仍需另行确认。禁止运行 GPU、修改 Canvas 或 XIA-56。


**新 Agent / subagent 交接入口：** [HANDOFF.md](HANDOFF.md)（已冻结文件、实际保存路径、当前失败记录、下一步执行指令）。

状态：**P0 单轮文本对照已完成，等待用户审阅；不作方法排名**。依据 [Linear XIA-59](https://linear.app/xiangshushu/issue/XIA-59) 和已完成的 [XIA-57](https://linear.app/xiangshushu/issue/XIA-57)。只使用文本 LLM，**不调用 ComfyUI/H3 GPU、不更改 Canvas、不修改 XIA-56**。

## 固定输入和上游快照

- `inputs/01-dialogue.json`：问答、犹豫和反应（杯子不移动）。
- `inputs/02-handoff.json`：在相同空间增加杯子归属和持物手转移。
- `inputs/03-overlap.json`：并行说话/离开、发现后停止和转身。
- `upstream/manifest.json`：各原始下载 URL、文件 SHA256、字节数；真实原文在 `upstream/toonflow/`、`upstream/director/`、`upstream/vimax/`，官方兼容 H3 Skill 冻结在 `upstream/h3/`。注意：下载的是访问时 main/master 分支的文件快照，不应误称所有项目都在同一个 Git 提交。
- `runner/prepare.py` 创建快照和固定输入；重复运行会更新快照，**首次实验完成后不得重跑而不标记版本变化**。

## 四组与适配声明（关键）

共同契约：所有组生成 8 秒 JSON Shot Plan，字段见 `runner/run_p0.py`，不指定镜头数量。共同契约是**评估接口**，不是任何上游项目的原生文件格式。各组固定使用同一 `deepseek/deepseek-flash`、thinking off、无工具、独立进程、同场景同素材。提示词长度不是评分维度，原生格式差异需要保留说明。

- **native**：固定场景、Beat 和共同格式契约；不提供导演方法。
- **toonflow**：完整原文 `shotCraft.md` + `storyboardTable.md`；这是上游真实知识文本的隔离调用，跳过其产品 UI/资产生成步骤。未调用完整 Toonflow-app 团队流程。
- **director**：原样注入 `SKILL.md`、Beat Sheet、Blocking、Shot Plan、Continuity Bible；只要求文本 Shot Plan。跳过原生产包其他步骤，故并非完整 Skill 全流程评测。
- **vimax**：原样注入 `storyboard_artist.py` 内的 `design_storyboard` / `decompose_visual_description` Prompt 与代码；**这是 Prompt replay / JSON adapter**，不等于运行原 LangChain+Pydantic 链；不涉及 Camera Tree 的图像依赖执行。要声称原生 ViMax 运行效果，需另做原管线试验。
- **差异**：各组保留原规则语义和原文；唯一额外的文本是共同输出契约与“只执行文本规划”的隔离说明。源文件可通过 SHA256 核对；每轮完整输入另存 `p0/<scene>/<group>/input-prompt.txt`。

## 历史批次的执行及证据

以下 runner 命令仅记录已完成的 DeepSeek/Pi P0，不是后续实验的执行指令。

`python3 runner/run_p0.py --batch <新批次名> --scene 01-dialogue` 对四组依次独立调用。逐条保存 `metadata.json`、`input-prompt.txt`、`raw-output.txt`、`stderr.txt`。不要手改原始输出；失败或超时单独保留。随后执行 `python3 runner/evaluate.py --batch <批次名>`，其仅做 JSON/时段/原文台词的**机械检查**，不以该检查替代人工导演评审。

人工案例级检查：剧情/原对白完整性；每次切镜的新增信息；景别/角度/运动与观察重点；Blocking、人物相对位置/眼线、动作起止状态/held_by/hand；总时长、镜头数和 H3 可执行复杂度；是否新增剧情。记录逐句错误证据，**首轮不做胜率或方法优劣排名**。多轮调用须记录模型实际解析 ID、设置、重复次数和调用条件差异。

## 阶段门槛

当前仅 P0。任务正文 P0 部分要求用户确认诊断差异之后才能继续 P1（尽管概述处先列 P0/P1），故遵守较严格门槛：**先交 P0 供审阅，再决定 P1**。P1 使用同一个冻结的 H3 官方兼容 Skill 把各 Shot Plan 原样编译成六段 Ref2VA，不得二次导演改镜；保留 Beat→H3 直出额外独立链路。P2 H3 视频须再次单独获得用户确认；Canvas 留到最终测试讨论之后。

## 2026-11-06 P0 单轮结果

[批次总览](p0/batches/20261106-deepseek-offline/RESULTS.md)及逐场人工对照： [对话](p0/batches/20261106-deepseek-offline/review-01.md)、[交杯](p0/batches/20261106-deepseek-offline/review-02.md)、[并行离开](p0/batches/20261106-deepseek-offline/review-03.md)。旧超时样本保留，未混入正式批次。P1 等待用户审阅后决定。

## P1 静态编译进度

用户已批准进入 P1。[P1 审查记录](p1/RESULTS.md)包含 12 份 Codex 编译初稿、3 份独立 Beat 直出及来源、限制和逐项审查。补全后的 [P1 修订与案例对照](p1/review-20261107/RESULTS.md)已完成静态检查；并行对白存在原始计划冲突，不能作为已解决的无损编译或视频执行证据。P2 需另行确认。

## P1-R 定向验证（2026-11-07）

[R1/R2/R3 最终决策报告](p1/review-20261107-followup/DECISION.md)及证据、候选与哈希索引已保存；待人工评审。P2 视频仍需另行确认。

## 2026-11-07 · P1-R 后可执行验证准备

[E0–E3 执行报告](p2-prep-20261107/EXECUTION-REPORT.md)记录证据冻结、时间口播阻塞、两套新的对白中断导演方案及 H3 静态稿、交杯状态保真和归因；[E0 哈希冻结](p2-prep-20261107/E0-FREEZE.json)核验 137 个既有实验文件及 13 个 upstream 源文件；[P2 审批包](p2-prep-20261107/P2-AUTHORIZATION.md)列明真实素材、模型、参数、成本、QC 和停止条件。E2 A/B 新候选分别见同镜和跨镜文件。当前停在 P2 用户审批关口，不会提交生成。

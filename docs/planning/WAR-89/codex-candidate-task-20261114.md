# WAR-89｜Eric Codex Astra — Director Skill v0 独立候选作者任务（2026-11-14）

你的角色：**主作者，不是产品实现者**。ChatGPT GPT-6 负责委派、独立验收和向用户报告；不要在 Codex 中启动其他子 Agent。模型选择 gpt-6-astra Medium（专业跨源整合）。当前 Linear WAR-89 是 In Progress，用户已经授权**七文件候选与 D 纸面走查**，尚未授权真正的 C/D/E LLM 对照实验或安装生产 Skill。

项目 /home/sean/projects/canvas-lab；当前分支可能是 WAR-35，工作树混入大量非本任务修改。先只读检查 git branch/status/HEAD；**只能新建或修改 docs/planning/WAR-89/ 内本轮候选和证据**；不得 touch、stage、reset、checkout、stash、clean、commit 其他路径，也不要主动 Git commit（ChatGPT 复核后决定）。不要修改已有的 WAR-89 历史冻结稿，另建输出。

## 必读的具体输入（直接从本机文件；只按需读取，勿重做三源完整审计）
1. /home/sean/.pi/agent/skills/linear-task-collab/SKILL.md；以及本项目 docs/planning/WAR-89/next-conversation-codex-brief-20261114.md
2. docs/planning/WAR-74/director-v0-concept-v1.md §1–6
3. docs/planning/WAR-89/director-skill-v0-knowledge-context-architecture-proposal-20261114.md §11–12，特别**已确认的 B-flex §12**
4. docs/planning/WAR-89/director-skill-v0-file-and-prompt-design-20261114.md（七文件设计草案，全部）
5. docs/planning/WAR-89/director-knowledge-decision-rules-v0.md（目录、§7/8/9，按问题）
6. 针对 K1–K7 的每一个精确原始入口，只查相关的三源独立知识稿及需要的冻结文本依据；不要导入全部原 Skill。冻结案例优先使用已有本地 D《错过的钥匙》、C《没说出口》、E《最后一张照片》文档，按明确引用回读相应原文，不捏造原文。WAR-35/52 只遵守已确认的边界，不动 Schema/API。

## 交付物位置
docs/planning/WAR-89/director-skill-v0-candidate/ （**设计草案目录，不安装到 .agents/skills 或生产路径**）
精准七个文件：
- SKILL.md
- stages/intent.md
- stages/beat.md
- stages/blocking.md
- stages/shot-plan.md
- references/knowledge-index.md
- references/review-method.md

本轮另在 docs/planning/WAR-89/ 创建三份独立**证据与待实验输入** Markdown：
- director-skill-v0-d-paper-walkthrough-20261114.md（真正完成一次纸面 Stage Call/Stage Result 路径；只能称“人工纸面推演”，不是 LLM 文本实测）
- director-skill-v0-ce-minimal-text-cases-20261114.md（冻结 C、E 的最小输入、必要 source path/行号、严格失败信号/允许多解和证据未知；**不运行对照测试**）
- director-skill-v0-candidate-author-note-20261114.md（七文件目录、与此前草案差异、关键专业选择、未证与许可证缺口、清单及每文件 SHA-256、git status 范围；面向 ChatGPT 复核）

## 专业质量要求（请比格式更加重视）
- 一个Director职责，B-flex Continue/Refresh/Resume；不拆为七 Agents，不按 K1–K7 逐项强制填表，不再粘贴三源完整流程。
- 常驻 SKILL 应薄；stage 各有独立**专业判断**，写输入、具体选择、真实替代及代价、失败反例、交接/返回条件，不能四张同一模板改标题。
- Intent：观众认知弧线、整场表达政策与审阅 A。Beat：实质因果/知情状态/静止中的变化；声音时序。Blocking：可演动作、可见中间阶段与眼线遮挡，不抢机位。Shot：逐镜观众任务先行，摄影、剪辑、声画及少量**真正替代**，邻镜复检；不以焦距/特写术语充数。
- K1–K7 按真实专业问题路由；knowledge-index 每个 K 有触发、任务、主要源码编号＋**精确可定位原始路径/章节（或明确未核）**、停止条件、许可证/版本风险；不把未获用户逐项批准的规则写成产品硬要求。DS upstream MIT 已核；TF 上游许可、VM 上游 commit/许可缺口。不得复制版权不明原 Prompt/代码，也不要把案例事实写入静态通用 Skill。
- B-flex §12 只作为**Stage Call/Result 语义**；Authority + approved Intent + Scene Spine + 活跃单候选和差异 + 当前 Stage/邻镜 + evidence。候选阶段自动保存语义是调用端责任，并不等于批准；A/B 是默认用户批准，局部可往返、上游批准事实不可暗改、正式工程接口未实现。勿把 Scene Plan 混同 H3 一次执行单元；无强制 8s、镜头数、Beat 数限制。
- 证据必须区分事实文本、专业合理推断、代理/几何、真实媒体/观众未知。用户优先专业质量，不要堆长 Prompt 或自创 Schema。

## D《错过的钥匙》纸面走查必须真的决策
以当前冻结剧本为权威（可引用行号）：唯一银钥匙、首次移开文件观众先看见、林尚未注意；蓝夹再次遮住；周只看到异常遮盖而没有目击钥匙；后续第二次移开蓝夹林才看到；最终林交给周**右手**。注意 D 角色来源中林/周的实际称谓，不凭想象修剧情。
- 模拟一个 **明确标注“示例虚拟已批准 A”** 的 Intent（绝不是项目正式批准），构造 B2/B3 Beat、Blocking 的*单一活跃候选*轻量快照，提供 Scene Spine/相邻状态。
- 完成 Shot02/Shot03 的实际 Stage Call（Continue），列出 K1/K2/K4/K5/K6/K7 为什么触发/何时停止；**关系镜内调度/焦点 vs 客观钥匙插镜**各自能改变什么，哪种更恰当、为什么、代价与清晰失败反例。不得把客观镜默认为周 POV；不得把旧 960x540 代理约 27x9px 当成片验证。
- 给出 Shot02/03 具体 shot construction 候选：观察路径、演员动作中间态、注意窗口、反应、机位/景别相对关系、切点与声画选择，至少保留两次发现时间差和钥匙遮回；如果文本或参考不足，给可审核的“需证”而不是直接宣称画面可读。
- 设计一次 Shot→Blocking 的局部返回修订，提出修改前后明确语义差异、为什么不越界、自动保存的候选交接内容、哪些邻镜/时序需局部复检、B 整场审核仍未发生。
- 再用模拟的 Refresh 或 Resume 恢复包检验局部交接与旧候选污染风险；示例不能生成真实用户批准或伪造已存在工具 API。
- 标明“纸面导演选择不等于真实图像/几何/观众结果”；有明确可供 ChatGPT 反驳审阅的专业选择。

## C/E 只准备，绝不调用试验模型
C：陈「过年的时候……」**自主停句**、许听懂但不替他说、**第二次广播**发生于陈后续「嗯」之后；避免广播造成被动打断的错判；克制表演可微动。E：不提前泄露背面过去承诺的核心语义（不是只看是否全文露出），林与观众**同步首次**读字；照片正面朝上**留在相册旁**没有收起来；背面字迹资产/可读尚未证。两者保留实际剧本文字/引用；严格反例与允许替代拍法，分清语义失败 vs 视觉未知。不要做新 LLM 实验或打分。

## 收口
完成本轮七文件 + D 走查 + C/E 备测包并进行静态文件自查。输出精简总结：具体路径、最关键的专业取舍与风险、所有文件 SHA-256、是否仅 WAR-89 变更、没有执行何种实验、给 ChatGPT 的重点审阅问题。不要直接宣布“通过”或更新 Linear（由 ChatGPT 管理）。

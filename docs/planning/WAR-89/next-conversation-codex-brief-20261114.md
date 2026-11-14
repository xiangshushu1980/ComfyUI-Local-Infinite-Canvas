# WAR-89｜下一轮 Eric Codex Agent 设计任务交接（2026-11-14）

状态：**新对话接手提示词及任务范围**。此文档保存行动边界与资料索引；不是正式已安装的 Director Skill 或实验结果。接手 Issue：WAR-89。机器 Eric。项目根目录：/home/sean/projects/canvas-lab。

## 1. 本轮已达成的批准结论

1. 自研 v0：通用单场景导演方法 + H3 Ref2VA 后续薄适配；Story Basis 为共同依据，Intent → Beat → Blocking → Shot Plan，Review 横切；**默认审阅 A（Intent）与 B（整场 Plan）**；详 WAR-74 概念规格。
2. B-flex：**同一导演职责**、可连续创作并跨阶段往返；需要时 Refresh/Resume，用正式批准基线与**选定单一活跃候选**重建，不依赖旧聊天；不强制每个阶段启动独立 Agent。§12 最小语义调用契约**已由用户确认作为设计基线**。
3. **有意义的阶段交接自动保存轻量候选**，不等于批准；A/B 是两处默认用户批准关口，额外专业 Review 按风险触发。候选和批准状态由未来工程适配 WAR-35/52，Director Skill 不自行审批、计算 hash 或编造生产 API。
4. Shot Plan 必带全场 Intent/观众认知 Scene Spine、相关 Beat/Blocking 关键中间状态、邻镜、硬约束和真实证据等级。知识组织按 L0 常驻薄原则→阶段卡→K1–K7 问题触发源专项→正式项目状态/媒体证据分工。**K1–K7 的具体专业细则目前仍属静态审阅后的候选，不得默认为全部批准的硬执行规则**。
5. 文本最小验收方向已批准；**媒体生成、真实几何、观众体验/H3 效果仍未验证**。参考源 DS 已核 MIT；Toonflow 上游许可、ViMax 上游 commit/许可仍有未关闭的出处/授权缺口，不能复制未核源原 Prompt/代码分发。

## 2. 必须先阅读（按需，禁止加载全部历史）

- /home/sean/.pi/agent/skills/linear-task-collab/SKILL.md（最新版；按需引用 references）。
- Linear WAR-89 最新状态、范围及本文资料路径；不要扩扫 WAR Team/其他 Project。
- 权威概念：docs/planning/WAR-74/director-v0-concept-v1.md（§1–6）。
- 已确认的调用/上下文方案：docs/planning/WAR-89/director-skill-v0-knowledge-context-architecture-proposal-20261114.md（优先 §9–12，必要时回读前文）。
- **本轮核心输入**：docs/planning/WAR-89/director-skill-v0-file-and-prompt-design-20261114.md（全部 8 节；已写拟建七文件树与可审阅 Prompt）。
- 专业索引：docs/planning/WAR-89/director-knowledge-decision-rules-v0.md（优先 §§0–2,7–9；具体有争议才回读对应独立知识稿与冻结源）。
- WAR-35/52：只读取需要确认的已有批准/候选/Review 接口边界；WAR-35 当前在 RC 独立冻结审阅中，**不要修改它的 Schema/测试/生产代码或把未冻结候选宣布已发布**。

## 3. 下一轮目标：由 Codex 起草**可阅读的独立候选 Director Skill v0**

**第一步先完成七文件候选**，建议保存在 WAR-89 下的独立草案目录（例如 docs/planning/WAR-89/director-skill-v0-candidate/），不要安装到真实 Agent 的技能目录、不要改变原始三套 Skill：
- SKILL.md：最短有用的导演定位、Story Basis 与版本/证据边界、B-flex 接手、阶段定位、K1–K7 触发策略、专业反馈原则；**不塞入剧本具体内容和全部参考知识**。
- stages/intent.md：整场观众体验、知情时序、风格/表演政策、真实可调整空间；Review A 交接。
- stages/beat.md：因果事件与信息/动作状态变化、时间和声音时序；不要变成 Shot 或 Video Unit。
- stages/blocking.md：可演行为、空间与眼线、道具/遮挡中间态；不抢 Shot 摄影选择。
- stages/shot-plan.md：观众画面任务→少量真替代→构图/动作/剪辑/声画→邻镜连续性→信息可读目标与真实风险；依赖全场 Intent + 当前详细 Beat/Blocking。
- references/knowledge-index.md：K1–K7 **短索引**，每条含专业触发、决策任务、优先源编号及精确原始入口、何时停读、已知许可证/出处风险。不要把七个 K 变成七个 Agent 或七份全量常驻 Prompt。
- references/review-method.md：Creative Review 横切；A/B，局部/整场双向检查，证据等级与专业错误反馈；不重复 WAR-35 CheckSpec/指纹或虚构 Engine。

每份文件写明输入需求、专业决定、真实交接产物、失败反例与是否需要上行请求。保持专业自然语言，**不要为了结构化而让导演变成数据校验员**；不固定镜数、Beat 数或 H3 8 秒上限；Scene Plan 与一次视频执行单元分开。

## 4. Codex 分工与执行节奏

- **主设计（复杂专业整合）**：优先 Codex gpt-6-astra Medium/High（以实际可用模型选择，依成本与复杂度调整），产出七文件候选，先着重审视 Shot Plan 的摄影/观众表达能力是否扎实，不能只是“策略词清单”。
- **简易辅助（可选）**：gpt-6-luna Low 仅做文件路径/来源编号/短交叉引用检查，不让简单模型替代跨源创作裁决。
- **独立审阅（按需）**：若第一轮发现专业规则冲突、阶段职责不清或 D 案例决定不足，可用第二次 Astra Medium 审阅，要求只指出高价值缺口。不要把原三源技能重新大规模审计。
- **保存机制**：阶段决定/候选产出在 Eric Markdown 留权威正文，Linear 更新状态、文档路径、SHA、剩余风险和停点；不把所有详细研究复制进 Linear Issue。
- 项目工作目录可能处于 WAR-35 相关 Git 分支或含其他任务改动；Git 操作必须检查分支/工作树并**仅提交 WAR-89 路径**，不修改/提交 WAR-35、构建产物、媒体/冻结上游原件。

## 5. 最小纸面验收以及后续文本验证安排

先对 D《错过的钥匙》**纸面走查一次真实 Stage Call**：批准 Intent（若示例为假设，标注“示例虚拟批准”）→ Beat / Blocking 候选快照 → Shot02 的观众发现任务与 Shot03 再遮、周知情差 → 提出关系镜 vs 客观插镜的取舍、时序/遮挡/参考风险 → Shot 返回 Blocking 并要求局部复检。**不能**把 960×540 代理 27×9px 的过往结果当真实视频可读证明。

再准备 C《没说出口》与 E《最后一张照片》的文本用例输入包/误判信号，沿用 WAR-89 既有冻结例和静态正反例，**不重复之前的审计**。其中 C 检自停/广播声画因果；E 检核心承诺语义的提前泄露、林与观众同步第一次读字、照片留在相册旁未收起。**先完成七文件候选及 D 纸面验收并呈现给用户**；若需要真正的新模型 A/B 对照，先报告实验设计、输入冻结、模型/预算和风险，再按本轮授权/用户下一步决定执行，绝不把文本推演冒充已测试的模型效果。

成功标准：七文件职责不重叠，首次调用可按需加载、局部修订可恢复，D 案例产生**有观众任务的真实镜头取舍**，不更改已批准剧情事实；公开专业理由与证据等级；不靠长 Prompt 堆砌、不靠工程 Schema 代替导演判断。

## 6. 本轮执行禁止项与停点

**不做** Canvas Agent/Canvas 启动、Blender、ComfyUI/H3、图片/视频/付费模型实验、生产代码/Schema 改动、原始 DS/TF/VM Skill 复制或修改、自动审批写入、跨项目任务扫描或删除。可以在本任务范围写**独立七文件候选草案**和 D 文本纸面走查；只读来源核对按需执行。

**停点**：展示七文件草案组织、关键 Prompt 和 D 的专业抉择；明确源方法是否值得正式纳入、尚未证实的风险、是否准备进入最小文本调用实验；先请用户审阅，再决定安装、实际 LLM 对照与 Canvas 集成。不得把设计稿已保存当作真实 Skill 验收通过。

## 7. 给新对话直接使用的启动提示词

继续 Canvas Lab 的 WAR-89，下一轮使用 Eric 上的 Codex Agent 作为**候选 Director Skill v0 的文件作者**，由 ChatGPT 负责任务范围、审阅与裁决。

先读取 Eric 最新 linear-task-collab Skill、Linear WAR-89 和 docs/planning/WAR-89/next-conversation-codex-brief-20261114.md；依该交接稿按需读取 WAR-74、WAR-89 的已确认 B-flex §12、七文件组织与 Prompt 草案、K1–K7 索引。不要重新做三套导演 Skill 的完整调研。

请先让 Codex 以适合复杂专业整合的模型起草**独立七文件候选 Director Skill**，放入 WAR-89 下的独立候选目录（不安装为生产 Skill）；用 D《错过的钥匙》进行一次**纸面调用走查**，同时准备 C/E 最小文本反例输入与预期信号。优先看 Shot Plan 是否真能解释“观众此刻需要看到什么、为什么选这种镜头、替代方案代价是什么”，而不是仅靠镜头术语或 Schema 填表。按 B-flex 保留连续创作和候选/批准隔离；A/B 两处默认审阅不变。

只保存 Eric Markdown、更新 Linear 索引与停点，工作树仅允许 WAR-89 文件变动；不更改 WAR-35/52、原始 Skill 或生产代码，不运行 GPU/Canvas/Blender/H3，不把纸面走查称为模型实测。完成候选和 D 走查后先交我审阅，再决定是否启动真正的 C/D/E 文本对照实验。请根据工作复杂度选 Codex Astra 或 Luna，并保留来源、实际差异与 SHA 证据。

# WAR-89｜导演专业知识继承审计与 Skill 执行规则方案

状态：**In Progress／三源知识稿、交叉审计及 Astra 八项复核已保存。用户认可八项修订方向；K1–K7 已完成 GPT-6 主导、Eric Codex 按需 Luna Low 来源核查/Astra Medium 对抗审阅的第一轮分组静态复核。具体执行细则仍待用户采纳；下一步组织最小常驻触发、按问题检索与专业反馈方案。未融合、未开发自研 Skill**。创建：2026-11-14。Linear：[WAR-89](https://linear.app/xiangshushu/issue/WAR-89)。

## 1. 为什么新增这一阶段

截至 WAR-74，已确认 Story Basis → Director Intent → Beat → Blocking → Shot Plan，加上横切 Review；WAR-35 正将其表达成可追踪、可编辑的数据契约。这些负责**记录、关联和复检决策**，却不能自动提供专业导演判断。原始 DirectorSKILL、Toonflow、ViMax 中关于潜台词、表演、景别/机位、角度/构图/运镜、节奏与视觉表达的具体规则，不能因数据字段存在就视为已纳入自研 Skill。

已有研究综合：`docs/validation/WAR-59/director-skill-predesign-synthesis-20261113.md`；概念设计：`docs/planning/WAR-74/director-v0-concept-v1.md`。这些证明研究与方法选择的依据，**不证明**已经实现专业知识调用或实际成片效果。

## 2. 主线阶段关系

1. **已研究**：三套源 Skill 的规则、样本、局部交互、限制与正反例，WAR-57/59/61/65/66/68–73。
2. **数据契约**：WAR-35（仍在 RC 验收）与 WAR-52（H3 专用设计已 Done），用于稳定表达、来源、状态和 Review。
3. **专业知识继承与执行设计（本任务）**：先审计原始 Skill 的行业规则，再决定规则可直接复用、薄适配、整理改造或暂缓；明确哪个导演步骤在什么条件下使用哪些知识，以及最小案例和验证。
4. **经批准的自研 Director Skill 实现**：以第三步为输入组织可执行的 Skill 规则、引用知识和必要工具，而不是按数据 Schema 直接生成一个空壳。WAR-36 Shot Planner 是其中一个独立实现范围，但不替代整个知识继承。
5. **以后再考虑 Canvas 集成**：本次不涉及、不提前推进。

顺序不等于阻塞所有并行工作：WAR-35 验收期间可以进行本项的只读审计，但**不能以此认定 Schema 冻结或实现获得授权**。

## 3. 审计范围与初步职责映射（待核对，不是已经集成）

| 专业知识 | 拟调用位置 | 核心问题 |
| --- | --- | --- |
| 故事分析、潜台词、角色知情、观众信息/情绪 | Story Basis 引用与 Director Intent | 观众何时应知道、误会、注意或感受到什么，事实与创意如何区分 |
| 叙事节奏、行动变化、注意力转换 | Intent / Beat | 何处发生有意义的变化，哪个变化值得镜头表达 |
| 表演指导、动作设计、空间调度、眼线/遮挡 | Blocking | 如何让人物行为在空间与时间上可执行且有表演意义 |
| 景别、摄影角度、构图、焦点、运镜、镜头衔接和节奏 | Shot Plan | **为什么**选择某镜头以传达信息；应比较必要替代而非只是列术语 |
| 整体视觉风格与一致性 | Intent 的整体原则，Shot 的实现，Review 的一致性检查 | 避免每个 Shot 独立生成互不相容的风格 |
| 连续性、媒体可见性、决策理由、风险检查 | Review（跨层） | 不把文字规划当成真实摄影或观众可读效果 |

**特别注意**：方法/知识与数据格式分开：可继承摄影专业知识而不复制源 Skill 的整个 Agent 数量、工作流、文件格式；除技术兼容性，还须核对来源、版本和 License。

## 4. Agent 与工程层职责边界（2026-11-14 讨论确认方向，接口待设计）

**原则**：专业导演知识交给 Director Agent 进行情境判断；正式结构化产物遵循公共契约；确定性的格式、来源、版本、依赖、差异、批准有效性由普通工程程序处理。Schema 是**交付和交互的协议**，不是强迫模型按字段思考的推理流程。原始导演 Skill 的按需执行/返工机制应该保留。

建议的最小往返：
1. **Agent 创作**：读取已确认故事依据、有关导演状态与专业知识，自由产生少量候选；说明观众目标、镜头/表演选择的专业理由及不确定性，无须自行计算哈希或持久化图。
2. **结构化提交**：Agent 将选定的 Intent、Beat、Blocking、Shot 等语义字段输出给明确的提交入口（可能是结构化响应或工具调用；具体接口、粒度和责任归属尚未设计，不预设已存在生产 API）。模型不能偷偷修改来源事实，且不能把决定交给纯程序补造。
3. **Engine 验证与持久化**：程序使用 WAR-35/52 契约和验证器检查 schema、引用、版本、连续性可计算约束、变更影响与 Review 继承；维护正式对象并返回可定位的结果。
4. **语义反馈/审阅**：将程序发现的**创作相关**问题简化反馈给 Agent/用户（如跨轴线风险、已完成动作又重复、某已批准镜头需复检），不把 SHA、JCS、CheckSpec 细节长期塞给 Agent。对需要创意判断或媒体实证的内容明确标未知，不由规则引擎假装已经判定。

**研发边界**：
- WAR-74：概念职责与分级审阅，已 Done；并非工具 API。
- WAR-35：DirectorPlan 结构、来源、验证语义、RC 测试；**当前不交付生产级 Engine 或 Agent tool interface**。
- WAR-52：H3 执行投影设计，非生产转换服务。
- WAR-36：Shot Planner 选型/实现 Backlog，尚未交付 Agent 调用端点。
- WAR-89：专业知识继承审计，连带**提出** Agent→工程层最小结构化提交、错误反馈和工作流迭代要求；不擅自扩大为 Engine 的生产实现任务。接口与生产引擎的独立设计/实施归属、工具粒度及转换策略需在后继规划中明确，再经用户批准。

**创作与验收分离**：候选探索可以是自然语言/轻量草案，正式提交才要求足够的可验证语义结构；不把 Schema 作为每轮推理提示模板，不要求普通机位候选逐一通过全部审批。

## 5. 交付与验收建议

- 建立逐条的**知识继承矩阵**：规则名称、来源路径/版本/许可、原规则目的、适用与不适用条件、采纳策略（复用／薄适配／改造／暂缓）、调用层及触发、输出判断/理由、失败风险与验证方式。
- 对 v0 选择最小但完整的实例，至少包含「导演意图 → 表演/Blocking → 镜头选型理由」及一次局部反馈造成的修改/复检；不以更长 Prompt 或更多镜头代表提升。
- 明确专业规则何时由模型主动检索/应用、何时仅参考、何时由可计算检查验证；对难以通过文本核实的视觉效果如实标为未证。
- 输出「已阅读／计划继承／已编入 Skill／已独立运行验证」状态表，不能把四种状态混淆。
- 在用户审阅采纳范围后，再决定最小 Skill 实现和是否为具体专业域拆任务。

## 6. 边界与现有资料

只读审计第一步，无 GPU、Blender、H3、生产代码更改、原始 Skill 更改或付费调用；未经进一步决定，不自动将后续实施列为已授权。

现有研究与源码索引：`docs/validation/WAR-59/director-skill-predesign-synthesis-20261113.md`、`docs/validation/WAR-68/README.md`、`docs/validation/WAR-59/toonflow-upstream-v118workflow/`、`docs/validation/WAR-65/`、`docs/validation/WAR-66/`。实际研究时按问题读取所需文件，不批量加载。WAR-35 独立审阅不因本任务改变验收结论。

## 7. 2026-11-14｜分套知识提取执行入口

用户确认顺序为 **Toonflow → DirectorSKILL → ViMax**：先分别抽取、保留差异和来源，三份独立材料完成后才讨论融合与取舍；优先复用 WAR-57/59/61/65/66 已有研究，仅在具体专业方法不足时回读源文件，不重做实验。

- **Toonflow 第一轮独立稿已写入**：`docs/planning/WAR-89/toonflow-directing-knowledge-v0.md`；17 条专业导演方法候选，标注原始出处、适用阶段、旧 Canvas/迁移内容排除、未证/授权缺口、示意例子和下一轮需求。
- **来源完整性**：`docs/validation/WAR-59/toonflow-upstream-v118workflow/SOURCE-MANIFEST.json` 所列 24/24 SHA-256 已比对一致。此快照是经整合/迁移的 Toonflow 知识封装，不等于未经加工的旧上游原版；License 尚未核实。
- **DirectorSKILL 独立稿 v0.2 已补齐核心专业细则**：`docs/planning/WAR-89/directorskill-directing-knowledge-v0.md`；Eric 完整 v2.1.0 冻结仓库（Git `c65ae0d`，MIT），核心五份 5/5 SHA 一致。第一轮 31 个主题＋第二轮 §9–11 详细说明镜头功能、景别/焦段、Blocking、视线、切点、声音、照明、风格选择与风险修订的触发条件、替代方案、失败反例，并以 C/D 样本作说明性推演。**不表示 20 个导演风格模块或 F1–F19 逐项操作细则已全量移植**。
- **ViMax 独立稿已写入**：`docs/planning/WAR-89/vimax-directing-knowledge-v0.md`；依据 Eric 三份 SHA 匹配的 Python Prompt/管线快照及 WAR-66 已完成文本研究，整理 14 条专业表达与参考内容判断候选、FF/Motion/LF 事实/时序复检、Camera Tree 机位参考依赖的职责和缺口。**上游精确 commit、许可证未核；未执行原版 Python Pipeline 或媒体**。
- **三源交叉审计候选已形成，待用户批准**：`docs/planning/WAR-89/three-source-directing-knowledge-cross-audit-v0.md`（覆盖、重复、冲突、遗漏；7 条最小核心规则；5 项待决取舍；SHA-256 `05e4a8a00de612de7eb80674713dffea55800f1523df59379f67f7c6a0f17d30`）。仍未做：正式知识采纳、v0 Skill 知识加载、生产接口或新 H3/图像/Blender 实验。Toonflow 上游 license、ViMax 上游 commit/license 待核；DirectorSKILL 20 位风格模块按需阅读来源。
- **Astra 独立复核与修订方向（2026-11-14）**：`docs/planning/WAR-89/three-source-independent-review-astra-v0.md`（本地 Git `fe2b29f`）提出 8 项实质意见；用户已同意按此方向修订，仍保留 K1–K7 与三源按问题分工。
- **专业决策规则细则 v0（待审，K1–K7 全部完成第一轮分组静态专项）**：`docs/planning/WAR-89/director-knowledge-decision-rules-v0.md`（SHA-256 `38f376cd9e1b097a7c88e02a78695276cb223249f0f8392723d32e139c4a12bb`）。K1/K6/K7 的九组样例在 §7；K2/K5 八组在 §8；K3/K4 八组、授权边界与简短常驻触发候选在 §9。最后一轮明确**仅可偏离可调整风格倾向，不可未经授权解除已确认禁项**；纠正 D 首次未发现与二次发现的时间区别。**具体细则仍待用户采纳，未编入 Skill，未实测成片。**
- **本轮独立审阅证据**：`docs/planning/WAR-89/k1-k6-k7-astra-independent-static-review-20261114.md`（SHA-256 `7624b05bd9ef7565c4b05bc4aa6ff3c6fe7e2823c862ab6902eae7b43c81806f`），Eric Codex CLI `gpt-6-astra` Medium、只读。四项实质发现，六组静态正反例；GPT-6 补充时间省略/明显不可信的阅读窗口/局部审查边界后写入候选细则。原始证据独立保留，不将文本推演视为模型或媒体测试。
- **本轮模型证据**：`docs/planning/WAR-89/k2-k5-luna-source-index-check-20261114.md`（SHA-256 `022857e8114e14f58d605c56e192f60ac4b510af109ebf31aab22f16546fe252`，Luna Low，六项出处核对；首条 TF-15 索引有误，已在 §8 标注纠正）；`docs/planning/WAR-89/k2-k5-astra-independent-static-review-20261114.md`（SHA-256 `6c49813681cd70e38b7aa4ac9005d9ff45b371ed67c573b29ffd8e71eea02197`，Astra Medium，只读对抗复核，1 项需修语义缝隙）。全部是静态文档审阅，没有运行 Director Skill/媒体实验。
- **K3/K4 独立证据（2026-11-14）**：`docs/planning/WAR-89/k3-k4-luna-source-index-check-20261114.md`（SHA-256 `ae5b0ee4aebc4190fdf9472207aa73802b6811460dd47f43d8600917c90e5a37`，Luna Low，六项来源核查）；`docs/planning/WAR-89/k3-k4-astra-independent-static-review-20261114.md`（SHA-256 `1959a10c4b4743769ab234859b8b300aa631c8d81dacf0dde8d75fe222a12b72`，Astra Medium，八组静态正反例，一项局部政策例外措辞修订）。原始意见保留，无新媒体/导演模型实验。
- **下一步**：用户按需确认 K1–K7 的专业继承取舍；整理「最小常驻问题触发→按情境选择 DS/TF/VM 专业模块→阶段性专业反馈→审阅/验证边界」的**方案草案**与最小评估案例，先讨论再开发。未获批准不写 Skill、运行实验或修改 WAR-35 Schema；WAR-74 原有阶段不变。
- **状态/交接**：资料正文以 Eric Markdown 为权威，Linear WAR-89 仅登记状态和索引。本次文件尚未在专用 WAR-89 分支提交/推送；当前项目工作树在 WAR-35 分支且含其他在途改动，避免混合任务提交。

本文件原有第 1–6 节为阶段安排与审计方案；第 7 节只记录执行入口，具体提取以所指独立知识稿为准。
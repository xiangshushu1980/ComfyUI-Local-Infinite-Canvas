# WAR-36｜Shot Planner 复用 ADR 与局部修订接口 v0（D0 已确认）

状态：**D0 设计决策已确认，§8 D0.2 工程边界细化已记录待静态复核；WAR-35 v0.1.0 已冻结；D1 仍受 WAR-33 复用/许可门槛和另行实现授权约束；本文件不是第二套公共 Schema**。2026-11-17；机器 Eric；Issue [WAR-36](https://linear.app/xiangshushu/issue/WAR-36)。本文件是 WAR-36 当前详细设计与有效决定的唯一权威正文，不替代 WAR-35、WAR-37、WAR-33 的权威资料。

## 1. 决策范围与已知边界

近期目标是决定 Shot Planner 怎样从已确认的 Director Intent + Beat/Action + Blocking 生成**可编辑的 Shot Plan**，以及反馈如何形成可审计的候选、真实差异、影响范围与复检请求。**本轮不开发生产 Planner、Canvas UI、typed Review/CAS、H3 Prompt Compiler，不触碰已批准的镜头和原始 Skill。**

依据与证据性质：

| 来源 | 支持的事实 | 尚不能声称 |
| --- | --- | --- |
| WAR-74 `docs/planning/WAR-74/director-v0-concept-v1.md`，Git `0523ef0` | Story Basis + Intent/Beat/Blocking/Shot 四薄产物 + 横切 Review；A/B 两审；Beat ≠ Shot ≠ 视频执行单元；信息判据与修订传播原则已确认 | JSON Schema / Agent 实现 / 视频品质 |
| WAR-35 冻结发布 Git `f00be85` / `director-plan-v0.1.0-design-freeze`，Eric 独立 worktree `docs/planning/WAR-35/director-plan.schema.v0.1.0.json` | Shot / Action / Review / Revision 正式**设计**契约；阶段 A/B 已独立验收，公共 v0.1.0 已冻结（详见 §8） | 把 Schema/设计验收当成生产可信 Decision、媒体验收或运行接口已实现 |
| WAR-33 `docs/planning/XIA-33-skill-reuse-adr-draft.md`；WAR-89 `docs/planning/WAR-89/director-skill-v0-candidate/stages/shot-plan.md` | 现成导演规则及 H3 官方 Skill 可借鉴；已存在自研的独立七文件 Director Skill 候选，按问题注入方法；复用优先 | WAR-33 全部许可/版本/正式复用 ADR 已验收 |
| WAR-90 `docs/planning/WAR-90/canvas-real-model-feedback-20261117/README.md`，Git `a905c1a` | 真实模型仅修改 Shot02 文本，Shot01/03/04 字节不变；R2 试点经用户认可、Canvas 原位更新；文本守门/哈希/展示试点通过 | 真人独立原创反馈、正式身份、typed Decision、刷新恢复、视觉或媒体 QA |
| WAR-72 与 WAR-59 已冻结研究 | 仅有文本信息链不保证钥匙视觉可读；跨镜动作与知情窗口需要单独验证 | 修镜头文字即可保证观众识别 |

注意：旧「8秒四镜、精确切点、资料存 Linear Document」均仅为历史样例/旧要求。当前按 Eric `linear-task-collab`：项目 `docs/` 为唯一正文，8 秒不设为通用上限；H3 12 秒常用、允许**设计至** 15 秒不等于真实成功率证据。

## 2. ADR-36-01｜已确认“专业知识复用 + 小型 Planner 编排/验证适配”，不复制完整外部 Skill

### 2.1 四种候选与判定

| 方案 | 优点 | 不足/风险 | 建议 |
| --- | --- | --- | --- |
| A. 直接运行完整 Toonflow/DirectorSKILL/ViMax | 专业规则覆盖广 | 重复工作流和上下文，难保输入/输出权威与局部目标；许可和适配差异仍有缺口 | **不作为默认 Planner Runtime** |
| B. 直接原生 LLM、不设稳定契约或验证层 | 最少组件 | 字段/来源/版本不稳定；超范围变化与状态冲突可能隐身 | **不采用裸模式** |
| C. **沿用 WAR-89 自研 Director Skill 候选（只读规则），另设小型 Planner 编排与确定性验证/修订适配** | 已有 D 文本试验及 WAR-90 真实 R2，职责清楚；保留专业模型创造性、可替换知识；复用现有 Runtime 守门 | 需按 WAR-35 正式契约补结构化 Diff/引用/审批；WAR-33 复用收口未完 | **2026-11-17 用户已确认 D0 架构；非 D1 开发许可** |
| D. 重写独立算法式 Shot Planner/新多 Agent 系统 | 可专门优化复杂镜头 | 工作量、重复能力和维护成本大，无证据证明必需 | **不预先立项** |

“复用”的准确范围：借鉴 **Toonflow 的观众信息任务**、**DirectorSKILL 的 Beat→Blocking→Shot/连续性**、**ViMax 的镜头内视觉方法**；使用 WAR-89 的经审阅本地原创知识摘要/阶段卡，而非未经许可复制/部署三套完整代码或将它们串联。H3 官方 Prompt 仍归 WAR-38 编译/执行适配，不由 WAR-36 再造。**ADR-36-01 的 D0 方向已确认**；WAR-33 继续独立完成剩余版本、许可及复用决策门槛，正式 D1 不提前关闭 blocker。

### 2.2 能力边界及责任归属

- **创作推理（专业模型 + Shot 阶段知识）**：从观众信息变化和 Blocking 出发，提出合理镜头职责、构图、节奏/切换、替代及取舍；允许 No-change。
- **Planner 编排薄层（WAR-36）**：收集权威 Story Basis/approved Intent、当前 Beat/Action/Blocking/Shot、冻结来源与目标；发起首版或局部候选；定位 ID 与作用域，保存模型原始输出/差异，不替人类签名。
- **确定性检查/Review 适配（WAR-35 的规格；WAR-36 实现其 Planner 侧使用）**：引用存在、顺序/状态/Action 覆盖、计划与请求实际 Diff、适用方法/版本、硬冲突和证据失效；模糊时扩大**复检集合**而不是自动扩大重写。
- **表现与批准（WAR-37 / 后续 WAR-42）**：专业镜头卡、轻量实体引用、关系边、反馈输入、逐项差异、风险与身份化批准；不将 Canvas 的文本节点当 Plan 原始权威。
- **H3 投影（WAR-38 / WAR-52）**：在获批 Shot Plan 之外另行切分视频执行单元、Prompt/Guide/Join；不得让模型单次最大长度倒逼场景镜头设计。

## 3. WAR-36 提议的语义接口（非最终 JSON 字段）

下列是调用边界的**最少语义**，键名不是承诺的 WAR-35 required 字段，也不另起第二套 Review Schema。

| 方向 | 输入/输出 | 核心不变量 |
| --- | --- | --- |
| `plan(request)` | 冻结 Story Basis + source fingerprint；Intent A；Beat/Action/StateDelta、Blocking；时长/素材/风格约束 → `ShotPlanCandidate`（逐镜主观众任务、证据判据、机位/构图、动作覆盖、状态、节奏/切点理由、风险、可替代方案） | 一 Beat 可覆盖多 Shot；一 Shot 可服务多 Beat；不强制镜数/秒数/精确帧；所有新事实必须标明假设或上游申请 |
| `proposeRevision(request)` | base approved/candidate revision + 来源/Skill 指纹；`targetRefs` + `requestedScope` + 用户反馈证据 → `Candidate` 或 `NoChange` / `Escalation` | 不隐式修改已批准基线；明确绑定反馈来源与身份状态；无实际改动不创建“已修复”假象 |
| `calculateImpact(candidate,base)` | 完整结构实际差异、依赖引用、动作/状态前后检查 → `actualChangedRefs/Paths`、`unexpectedChanges`、`recheckTargets`、`staleEvidence`、`upstreamEscalation` | 模型自述 `changed_targets` 仅供交叉核验，不能当真实 Diff；“受影响”不等于“已改动” |
| `handoffReview(candidate)` | 提交完整场景镜序、主要职责、画面判据、diff、复检结果/待做项、仍未证项与用户选择范围 | 审阅 B 针对特定 revision；经适用检查/身份守门后才产生批准；文本检查不能冒充媒体验证 |

一个 Shot 在接口内**至少能提供这些语义**：稳定 Shot 身份（不是 Canvas nodeId）、关联 Intent/Beat/Action/Blocking、主要观看责任与可见证据判据、观看时机/切镜原因与估计时间、视觉方案、Action 覆盖阶段、边界状态 refs、当前假设/风险；借用共享事实/动作/StateDelta，不复制注册表。字段 required/optional、ref 编码、CAS/指纹计算和正式 Decision 仍由 WAR-35 冻结。

首版 `plan()` 与局部 `proposeRevision()` 共用专业 Shot 决策能力，但局部必须加载源剧本、A 约束、当前完整场景骨架、目标及相关邻镜/动作/信息窗口。保留 WAR-89/WAR-90 已确认的 **Resume** 路径；Continue/Refresh 会话优化非 v0 前置。缺必要来源/阶段或指纹不符时不“补猜”，返回有范围的阻塞/待审。

## 4. 局部修订决策与传播

1. **目标绑定**：读取已批准版本及当前目标；用户请求如“加强 Shot02 钥匙首次辨认”，明确只授权该镜摄影/观看安排，不能偷改 Story Basis 的钥匙数量、林/周知情先后。
2. **专业判断**：模型可建议 No-change（已有镜头满足目标、或反馈实际要求越过已批准硬事实）；必须给理由、未证项和可替代方案。No-change 不需制造假正例。
3. **隔离候选**：复制已批准基线建立候选；获取结构化/逐文本精确 Diff。模型声明与真实 Diff 比对。超目标变更默认阻挡自动提交，作为候选方案请求人类扩大授权；不能静默改邻镜来“修好”。
4. **影响图扩展**：从实际改变的字段/引用追到同一观众信息任务、共享 Action、状态接缝、必要前后镜、关键时长/切点；当依赖未知时列待复检，不自动重写全场。邻镜只是**保守基础集合**，不替代 Action/信息/跨镜依赖分析。
5. **检查证据分级**：可确定的事实引用、动作完成次数、对白和因果顺序进行静态验证；遮挡、可读性、演技、H3 时序留为几何/媒体/真人未证，不改写成 pass。旧证据保留原版本/方法，受影响的新版检查须重跑或标 stale。
6. **审阅与提交**：WAR-37 展示目标/非目标差异、复检与未证风险、A/B 需要的额外审阅；用户接受全部/部分/退回。部分接受需要重新计算的候选和 Diff。WAR-35 正式 Revision/Decision 未冻结前，不实施生产级批准/覆盖。

`requestedScope`、`actualChangedRefs`、`recheckTargets` 必须分开；例如 Shot01/03 的待复检**不等于** Shot01/03 被实际改写。`NoChange` 路径仍保存建议、当前哪些证据不足，不能因用户不喜欢当前答案而虚构修订。

### 4.1 WAR-90 R2 的一条正例与必要限制

2026-11-17 真实 Codex gpt-6-astra/medium（非 fake）针对 **Shot02** 的 synthetic-test 反馈生成候选：实际改动 `Shot02`，`Shot01/03/04` 精确未改；当时 `pending_shots=[Shot01, Shot02, Shot03]`，这是连续性**待复检提示**，并非专业风险已验收。用户随后认可 R2，Pilot B 接受且 Canvas 同步成功，`identity_verified=false`、`formal_WAR35_approval=false`；Pilot 会清空待复检数组，不等于已经做动作接缝、视线或媒体检查。

WAR-36 正式方案应解决这个缺口：**将专业复检记录与试点审批标记解耦**。候选通过文本检查可进入 B 决策，但跨镜动作/空间/媒体未证项依然保留在 Review，只有匹配版本和检查方法的有效证据才可关闭。不要把 R2 的已认可状态直接迁移成正式 WAR-35 Approval。

### 4.2 必须覆盖的反例

- 只请求 S02 景别，却偷偷改变 S03/04 对白、动作或故事知情 → 披露超范围，不能自动应用。
- 为增强钥匙可读性，改成“周在蓝夹遮挡前看见 K” → 故事硬事实冲突；升级 Intent/Story Basis 审阅，不能只改镜头。
- 在 S02 镜尾启动右手轻理，S03 又从动作起点重复执行 → 同一 Action 跨镜阶段重叠；复检 Join/Action。
- 仅把镜头标成“ECU 可见”而无可观察判据/观看时间 → 文本交付不合格；焦距变化不构成媒体验收。
- 依赖不存在、源改变或证据绑定旧 revision，仍想沿用旧 pass → 必须拒绝继承或标 stale。
- 请求目标已满足且没有合理修改，或者修改会降低信息交付 → 合法 No-change，给出解释，不虚构正例。

### 4.3 只读接口细化｜四种结果与影响传播（D0 建议，非字段冻结）

该细化是上述已批准设计方向下的**待联审实现语义**，不定义最终 JSON Schema、不授予代码执行权。专业模型只负责给出镜头判断及候选，工程层必须从两个实际 Plan 快照重新计算修改与复检结果，不能直接信任模型自述。

| 结果语义 | 触发条件 | 允许交给 Review 的信息 | 不能发生 |
| --- | --- | --- | --- |
| **Candidate** | 可定位目标、来源有效、候选内容可比对，且实际变更均在授权 scope 内 | 目标内真实 Diff、影响引用/待复检、开放风险、制作选择理由 | 自动批准、自动修邻镜 |
| **NoChange** | 专业判断认为无合理变更，或者要求已由当前方案满足；没有实际变化 | 不变的依据、仍未证事项、可选替代/建议 | 为制造新 revision 虚构修改或关闭旧风险 |
| **NeedsUpstreamChange** | 请求会改变已确认 Story Basis、Intent/Beat/Blocking 的授权边界 | 冲突证据、上游需审的对象和提议、不继续传播的下游草案 | 让 Shot Planner 偷改作者事实/知情顺序 |
| **Blocked** | 目标不存在、来源/版本/Check 不适用、上下文不完整、超范围变更或确定性硬冲突 | 失败原因、最小可修复前提、原候选仅供隔离检查的标记 | 把模型声称的“通过”当已满足门槛 |

注：`Blocked` 与 `NeedsUpstreamChange` 不互斥于“建议另起候选”的创作提议，但**当前提交事务的单一状态**只能选一个主结果，并列出次要问题；`NoChange` 不自动意味着专业质量或媒体通过。

只读参考流程（不得直接实现生产写入）：

1. **Preflight**：验证 request、targetRefs、source/approved A、base revision 与 Check 适用性；缺关键项即 Blocked，保存审查依据。
2. **Professional proposal**：以 WAR-89 Shot 阶段知识调用现有专业模型；允许选择 NoChange / NeedsUpstreamChange；模型输出是候选，不是命令也不是正式 Decision。
3. **Scope guard**：计算 `actualChangedRefs/Paths`，与请求允许的改写集合逐项对照。只要出现目标外变更，即保留隔离差异、返回 Blocked/扩大授权建议；不得因为“顺带更好”而静默应用。
4. **Impact graph**：从修改镜头及其依赖传播到共享 Action phase、StateDelta、同一观众信息窗口、前后剪接与时长；生成 `recheckTargets` 和各项 `reason`，并将受影响旧 Evidence 标 stale/conditional（由 WAR-35 规范裁定）。
5. **Review handoff**：输出原批准基线引用、候选与实差、待复检、已检方法/版本、未证风险及决策选项；WAR-37 负责可读显示，正式接受/拒绝属于 WAR-35/42 的审批机制。

例子：S02 的镜尾轻理动作更早开始，若 S03 仍承担同一次动作的接续，则 **S02 可是唯一 actualChanged Shot**，S03 应在 recheckTargets 中；只有核查 Action phase 与观看窗口之后才能关闭文本接缝检查。跨镜视线、演员可执行性、真实观看识别仍未证。R2 Pilot B 接受不自动证明这些问题解决。

**待 WAR-35/37 联审的问题**：基础版本是整份 Plan revision 还是候选指定祖先（当前倾向直接父修订、遵循 WAR-35）；允许的镜头增删重排应如何被显式授权；复检 reason 分类如何映射为 WAR-35 的 Check ID/方法；部分接受时派生新候选与再次检查的边界。这些不是 D0 已批准的生产字段。

## 5. 设计验收矩阵与开发门槛

| 层次 | 检查用例 / 要求 | 本轮 |
| --- | --- | --- |
| ADR | 四选一、复用边界、许可证/版本残缺、依赖和替代方案说清 | **D0 决策经用户确认；WAR-33 复用证据仍待收口** |
| 首版静态规划 | 同一 8s 输入至少比较不同可辩护的节奏/镜序（含少切、不强制四镜或固定约 1.8s 切点）；另用 >15s 单场景证明 Scene Plan/执行单元分离 | 未运行；需独立样本/回放 |
| 局部 | D 的 S02 No-change 和 R2 有变化路径；S01/03/04 不被暗改；动作/知情窗口/邻镜复检队列完整 | WAR-90 试点证据存在；**正式 typed 路径未运行** |
| 拒绝/升级 | 非目标 Diff、重复 Action、上游硬事实冲突、版本失配、部分接受、旧证据失效 | 待 WAR-35 适用契约与离线测试 |
| 审阅 | 指定版本完整 Diff、观众证据判据、剩余未证风险、A/B 判断分离；无用户权限不签署决定 | 候选设计；WAR-37/42 后续接入 |
| 媒体 | 物理遮挡、H3 实际切点、观众理解、真实刷新持久化 | **不属于此设计验收；必须另行实测** |

建议实施分段：
- **D0（当前，已确认）**：复用/薄适配 ADR、严格目标边界、语义接口、R2/No-change/越权例子设计；后续可继续细化未冻结的接口细节，但不自动进入编码；
- **D1（条件成立后）**：WAR-35 公共 Schema 与 WAR-33 复用门槛就绪，建立 Planner 到正式 Plan/Review 的薄映射和离线正反例；最小编码仅加 Planner 层检查与结构化输出，不重建 Canvas/Gateway；
- **D2（另行授权）**：向 WAR-37/42 提供目标、关系、Diff、Decision 交互契约并真实浏览器集成；不在 WAR-36 执行 Canvas 改造；
- **D3（后续）**：H3 执行与媒体反馈入环另走 WAR-38/43/44 等任务，不能以文本验收替代。

**进入 D1 必须核对**：WAR-35 所需字段/Check/Review/Revision 已正式冻结或取得明确可用子集；WAR-33 本 Issue 适用的复用许可/ADR 门槛已审阅；用户批准具体编码与回滚范围。设计可并行，但不擅自移除 Linear blockers。

## 6. 2026-11-17 用户已确认的三项决定（D0 正式设计基线）

1. **ADR-36-01（已确认）**：采用方案 C——WAR-89 Shot 专业知识 + 现有模型/Runtime + 最薄 Planner 编排、确定性检查和修订适配；不另造大型 Shot Planner Skill。知识和代码的复用许可仍需 WAR-33 相应证据，不能据此宣称外部 Skill 获得安装授权。
2. **局部修订守界（已确认）**：目标外实际变更默认不得自动提交；可给出独立建议候选并由用户扩展授权。依赖与邻镜检查范围可扩大，但**不能因此自动扩大改写范围**。保留 No-change 和明确上游升级路径。
3. **分期（已确认）**：D0 设计交接可继续完善，正式 D1 编码在 WAR-35 适用契约、WAR-33 复用门槛和具体实施/回滚授权全部满足后另行启动。本次确认**不授权**修改生产代码、Canvas、Runtime、媒体，亦不改变 Backlog 和已登记的 blocks。

### 6.1 尚未冻结的实现选择（后续按缺口细化）

- **WAR-35 字段绑定**：稳定 ref 的编码、Revision/CAS 的适用规则、指纹/证据的可继承边界、Gate 必审 Check 和 Decision 身份真实性以 WAR-35 最新规范为准；WAR-36 只消费，不另造 authoritative Schema。
- **模型输出与结构边界**：首版生成可提出不同数量/节奏方案，局部修订是否允许重排/增删 Shot 应由请求显式 scope 与适用契约判断；WAR-90 现有基于 ShotNN 文本段的守门仅覆盖“同镜序、指定镜头文本修改”的试点，不代表正式通用 Planner 的全部能力。
- **专业复检准则**：邻镜只是默认起点；共享 Action 的跨镜阶段、状态接缝、信息首次揭示、动作声音时序和总时长须按实际影响计算。缺依赖时扩大 recheck，而不是隐式修改。
- **交互责任**：WAR-36 输出目标/实际变更/待检项目的可机读语义；WAR-37 定义人可读卡片和批准交互；WAR-42 在获批契约后做真实 Canvas 绑定与持久化。不可把临时节点文本哈希当正式 typed Revision。
- **正式测试集**：正例 No-change/R2，反例非目标改写、硬事实越权、同一 Action 重复完成、引用/版本失配、旧 Evidence 失效、部分接受后重算、镜头数/切点不机械固定；待 D1 则依冻结契约编写可运行断言。

### 6.2 下一次讨论建议（由 §8 D0.2 更新）

§8 已补齐四结果、Agent/Context/Runtime 边界、历史加载、Scope/Impact、部分接受和 WAR-37 交接候选。**下一步是对冻结 WAR-35 v0.1.0 进行只读字段映射核查与负例评审**，而不是重讨论已确认的 D0 选型；在 WAR-33 许可复用与专项编码授权到位前不启动 D1。

## 7. 交接与文件边界

- WAR-35：DirectorPlan、Review/Decision、有效性/指纹和 Action/StateDelta 的正式字段与 Schema；WAR-36 不自建冲突版本。
- WAR-37：专业 Shot 卡、轻量实体/节点绑定、Shot/Action 图关系、反馈/差异/审核 UI。
- WAR-42：正式 Canvas typed 集成、持久化、浏览器刷新与生产访问控制。
- WAR-33 / WAR-89：专业规则来源、许可证与必要复用结论，不重复大规模研究。
- WAR-90：R2 冻结试点为参考证据；不修改其来源、已批准状态和现有画布节点。
- 本文档：经用户确认的 WAR-36 D0 设计基线与尚未冻结的接口候选；后续只定向修订本文件与本 Issue，原始实验/证据仍各归原任务，禁止复制维护第二份权威结论。

## 8. D0.2｜冻结契约后的 Agent、Context Builder 与工程 Runtime 边界（2026-11-17）

**本节性质**：用户要求继续下一阶段，强调 Agent 智能/工程化分离、`reviewLedger` 和 `revisionControl` 不常驻模型上下文、只加载关联修改历史；同时 WAR-37 正在并行。本节作为 **WAR-36 D0 接口细化和 WAR-37 交接候选**，不修改公共 Schema/生产 Runtime/原始 Skill/Canvas、不构成 D1 实施授权。此前确认的方案 C、严格局部守界和分期门槛不变。

**新冻结前提**：WAR-35 已 Done，公共契约 `director-plan/0.1.0`、Schema ID `urn:canvas-lab:director-plan:0.1.0`；正式 SHA-256 `b14149c0bd79e3bca1b17ea21f2949e408cca770fb3d49549c5d85ff647538e7`，Git `f00be854382259a3dc8f7aff4958570807b4a6fc`，tag `director-plan-v0.1.0-design-freeze`。该发布在**独立 worktree** `/home/sean/projects/canvas-lab-worktrees/war-35-v0-freeze-preflight-20261117`，**尚未合并当前主工作树**，不可误用主分支 RC3/RC4 当冻结契约。A/B 设计验证通过不等于生产受信 Review/Gate 可用。

### 8.1 职责（逻辑模块，不要求七个微服务）

| 组件 | 应做 | 不应做 |
| --- | --- | --- |
| **Planner Orchestrator**（WAR-36） | 用已核验 revision/来源/目标组织一次 initial plan 或 revise，协调 Resume、调用模型与纯函数校验 | 直接覆盖批准 Plan、签署审批 |
| **Context Builder**（WAR-36 对接 WAR-89） | 按当前阶段构造最小专业上下文；标明已批准事实、限制、相关历史、未证风险，必要时调用只读检索 | 常驻完整 ledger/历史、发出审批决定、充当第二个 Agent |
| **Director Agent**（WAR-89 Shot 规则） | 选择镜头任务、构图、节奏/切点，提出理由、替代方案、创作风险或 NoChange | 自证 SHA/CAS、声称自己“正式批准”或主动扩大写入范围 |
| **Revision / Diff / Scope Guard**（确定性工程） | 从 base 与隔离候选的**实际快照**计算 ChangedPaths/Refs，校验 authorized scope 与版本、拒绝越权 | 相信模型的 `changed_targets` 自述 |
| **Impact + Review Adapter**（WAR-35 消费方） | 从 Action phase、StateDelta、依赖指纹、相邻信息窗口计算 recheckTargets，标记旧 Check/Evidence stale，准备 handoff | 把复检范围当自动重写范围，把文本通过当媒体通过 |
| **Trusted Store/Review**（后续 WAR-42） | 保存完整不可变 Plan/事件/审批、父版本关系、身份、实际 source/media 证明；以 CAS 推进 approved pointer | 通过压缩历史或模型自签 Decision 给予批准 |
| **Canvas View Adapter**（WAR-37/42） | 展示专业 Shot、轻量上下文、真实 Diff、风险和操作入口 | 存第二份批准 Plan、在 CanvasConnection 中写叙事关系 |

强调：这些是**职责**，不是开发前必须新造的服务清单；v0 优先复用现有 Runtime/Resume，避免复杂流程引擎和多 Agent 套娃。

### 8.2 Context Builder 的输入与裁剪契约

`buildCreativeContext(verifiedPlanRef, task, targetRefs, requestedScope, feedbackRef)`（**伪 API**）从受信存储读取：
- 当前 base Plan 的身份及完整原文快照（工程侧核验），冻结 Story Basis/Intent A 的相关事实、禁项、来源；目标 Shot 的 professional purpose、visualDesign、evidenceCriteria、timing；关联 Beat/Blocking、共享 Action phase、StateDelta；必要的上一个/下一个 Shot 及信息揭示依赖。
- 用户**原始反馈**、本轮授权范围、少量相关的创作历史摘要（例：“R1、R2 钥匙出现过早”）。摘要需关联来源事件以便回查，并保留硬事实/用户否决/未证风险，不得把“未证”简写为“已通过”。
- 只对复杂创作需求按需加载 WAR-89 专业规则/历史；默认不注入 Schema 全文、完整 `reviewLedger.checks/risks/decisions/inheritances`、`revisionControl.candidates`、全部祖先版本、Check/Decision ID、P/D-JCS 算法。
- Agent 如要“看上次 Shot02 驳回理由”，通过带范围的只读工具取**经过过滤的事件/证据摘要**，而非直接从长聊天猜真实历史。
- 缺已批准 source、完整基线或目标时 **Blocked/fail closed**。未知创意可明确作为待审假设；不得凭模型补写已批准事实。

`ContextBuilder` 是**可重建投影**，不是新的历史权威；上下文压缩只影响模型可见内容，**不可以压缩 Runtime 真正进行依赖核验与审批所用的历史集合**。

### 8.3 版本与审阅记录：受信存储 / 上下文投影分层

WAR-35 v0.1.0 `reviewLedger` 含 `checks, risks, decisions, inheritances`，`revisionControl` 含 `candidates, approvedPlan`，`plan` 中含 `planId/sceneId/revisionId` 和稳定的 Shot/Action ID。这些字段表达**公共传递契约**，不是已经实现的事件数据库或要求 Agent 全量记忆的结构。

工程侧未来持有：完整 Plan 快照、原始 feedback、提案原文、不可变 Revision/Review 事件、可信父链、真实 Check/Risk/Decision、approved 指针及乐观并发条件。Agent 默认只看到“当前版 + 本次目标 + 相关反馈与失败理由”。ID 保留给引用/审计，UI 可用 Shot02 等可读标签，模型不必看到每一个底层 Check ID。

**历史正确性**：任何 carry-forward 都由可信 Review 服务对**完整**记录重算，遵守 WAR-35 保守 Intent A（仅无风险、旧 `approved`、可信直接父链、/4 依赖一致、新 Check/Decision）；Shot B 不自动继承。不能因为摘要没提到风险就当不存在。WAR-90 Pilot B `identity_verified=false`，绝不能转写为正式 `approvedPlan`。

### 8.4 语义调用序列与四结果（字段名是临时内部建议，不新增 WAR-35 Schema）

```text
request = {task, expectedRevision, basePlanRef, sourceFingerprint,
           targetRefs, requestedScope, userFeedbackRef}
context = ContextBuilder.build(request)    # 未核验版本/来源/目标 -> Blocked
proposal = DirectorAgent.propose(context)  # 创作输出，不可信，不可直接持久化审批
candidate = Normalizer.isolate(base, proposal)
actualDiff = RevisionDiff.compare(base, candidate)  # 真实快照差异，不信自报
ScopeGuard.check(requestedScope, actualDiff)
impact = ImpactAnalyzer.expand(actualDiff, fullAuthoritativeDependencies)
review = ReviewHandoff.prepare(candidate, actualDiff, impact, openRisks)
# → Candidate | NoChange | NeedsUpstreamChange | Blocked
```

| 结果 | 工程条件 | 不可产生的副作用 |
| --- | --- | --- |
| **Candidate** | 非空实差均在授权 scope，结构/来源可核，无硬事实越权 | 不自动改批准 Plan、邻镜或清除旧风险 |
| **NoChange** | 完整 Plan 实差为空；附专业理由/未证项 | 不造伪 revision、不暗示媒体或 Review 已通过 |
| **NeedsUpstreamChange** | 必须先变更 Story Basis、Intent A、Beat/Blocking 或关键知情/因果事实 | 不让 Shot Planner 偷改上游批准内容 |
| **Blocked** | 版本/source/目标/必要上下文失效，确定性冲突，或有未授权真实修改 | 不自动提交；只保留隔离提案及解锁原因 |

模型可以**建议** NoChange / NeedsUpstreamChange，但最终结果由 Runtime 检查得出。初次规划需经相同来源/契约校验，创建新隔离 Plan；局部修订以当前直接父为基线。与已批准 Plan 不同的两个镜头顺序、增删镜头、共享 Action 变更，需要用户明确授权结构/上游 scope。

### 8.5 局部变更权限、传播与部分接受

- **requestedScope**：用户准许改动的目标对象及路径；**actualChangedRefs/Paths**：两个真实 Plan 快照计算的变更；**recheckTargets**：受影响、需重新检查的对象——三者严格分离。Shot02 构图变更可以使 Shot01/03 在 `recheckTargets`，但不能因此自动重写它们。
- **默认局部安全线**：允许在目标 Shot 的指定摄影/节奏/观看判据范围提出修改；更改邻镜、增删/重排 Shot、共享 Action/StateDelta、Story Basis、知情事实，默认必须显式扩权或上游升级。
- **Impact 规则**：用真实 Diff 与镜序、相邻切点、同 Action phase、StateDelta、Beat/Intent 引用、信息第一次露出/再次遮蔽、时长预算传播，返回每一项 `reason`、建议 `method`、`evidenceStatus`；缺依赖时保守扩大复检，**不得扩大自动写入**。
- **部分接受**：从可信 approved base（或明确已批准的候选父版本）生成**新派生候选**，仅放入允许的路径，再重新算 Diff、Impact、旧 Evidence 失效及需审阅项。不能简单合并 DOM patch、复用旧 Decision。
- **并发与历史**：expectedRevision/Plan SHA 不匹配则 Blocked，不能静默 rebase；布局/选中 Shot 等纯视图变化不产生 Plan revision；不因 `NoChange` 清空 Review 风险。

### 8.6 WAR-37 并行交接（本轮只读协调，不改 WAR-37 文件）

WAR-36 向 WAR-37 交付**可机读、无 UI 约束**的 `baseRevision / targetRefs / requestedScope / resultKind / actualChangedRefs/Paths / unexpectedChanges / recheckTargets[{target,reason,method,evidenceStatus}] / openRisks / upstreamEscalation / professionalRationale` 等**语义视图候选**，真实字段仍以 WAR-35 v0.1.0 为权威。WAR-37 负责专业层级、卡片、Context 抽屉、关系 overlay、差异和审阅操作的呈现；真实持久化/签批归 WAR-42。

WAR-37 目前静态原型仍引用 WAR-35 RC3 候选作为结构化演示数据。**这不否定其已通过的静态 UI 验证**，但正式 WAR-42 typed 接入前要补做 RC3 → `v0.1.0` 映射核对；不得把 WAR-90 已接受的文本 Pilot B 冒充正式 typed Plan/Decision。此处仅交接事实，不修改 WAR-37 原型或让其被另一对话覆盖。

### 8.7 D0.2 静态验收案例与 D1 门槛

| 典型输入 | 期望行为 |
| --- | --- |
| S02 仅景别改变 | Candidate；S02 是实际变更，S01/03/相关 Action 可列复检 |
| S02 本来满足目标 | NoChange；无新版本、不清风险 |
| S02 修改暗改 S03 对白 | Blocked/越权隔离、需扩权，approved 保持不变 |
| 借修镜头提前让周知道钥匙 | NeedsUpstreamChange；不得重写 Story Basis |
| D-JCS 依赖变更 / 旧 Check 绑定旧版本 | stale 或重新检查，不能继承伪 pass |
| 完整依赖未变，旧无条件批准 Intent A | 仅受信 Review 可按 /4 重验证形成新 Check/Decision；B 不自动继承 |
| source SHA 缺失或 expectedRevision 过期 | Blocked，不调用 LLM 补猜或覆盖 |
| 同一 Action phase 在两镜重复完成 | 检出连续性风险/复检，不宣称媒体已验证 |
| 用户未授权的增删/重排 Shot | Blocked + 结构权限升级建议 |
| 用户只接受两项改动之一 | 新候选、重新 Diff/Impact/Review，非 DOM 直接合并 |
| 只调整 Canvas 布局 | 无 Plan 变更、无 revision |
| 钥匙真实视觉可辨性未知 | media/human 仍 `unknown/not_checked`，不能把文本校验说成媒体通过 |

**本轮只读映射检查**：对 Eric 上已冻结 `director-plan.schema.v0.1.0.json` 的真实 bytes SHA、Schema ID、contractVersion、Plan/Shot ID 与主字段、顶层 Review/Revision 的 optional 性、Review 四数组、Candidate 直接父 revision 结构、approvedPlan 指针、P-JCS /1 与 D-JCS /4 规则、Intent A/Shot B gate 等进行 **19/19 静态断言通过**。该一次性检查没有验证 WAR-36 运行时 API、模型质量、旧历史服务、WAR-37 真正 typed UI 或浏览器持久化；没有用 RC3 演示冒充正式 v0.1.0 数据。

**结论/下一门槛（由 §9 更新）**：本轮已完成 §9 的独立离线设计用例 16/16；仍不开新 Agent、不建第二套 Review/History Schema。WAR-35 v0.1.0 适用版本门槛已满足；WAR-33 复用/许可证 ADR 及 D1 的实施/测试/回滚授权未满足。WAR-37 最新已进行**原生 Canvas 插件+Agent 节点定位**，非仅静态 HTML，按 §9 向其提供集成目标与数据守界交接；本轮不修改生产代码/原 Skill/Canvas/H3。

## 9. D0.3｜冻结契约上的离线修订反例验证与 Canvas-first 交接（2026-11-17）

### 9.1 输入真实性与验证范围

- 正式契约：Eric 独立 worktree `docs/planning/WAR-35/director-plan.schema.v0.1.0.json`，SHA `b14149c0bd79e3bca1b17ea21f2949e408cca770fb3d49549c5d85ff647538e7`；字节已检查，不复制/改写 Schema。
- **可执行结构测试输入**：`cross-shot-once.example.v0.1.0.json`，真实冻结的**狐狸跳溪两 Shot/同 Action** typed 示例；使用 `jsonschema` 对原包与隔离候选校验，再以 RFC 6901 路径计算两快照的真实 Diff。**这个例子不是《错过的钥匙》真实 typed DirectorPlan，也没有 ReviewLedger 的真实授权历史。**
- **专业纸面评审输入**：`WAR-90/canvas-real-model-feedback-20261117/evidence/approved-R2-four-shot-projection.json`；它是《错过的钥匙》**四个纯文本镜头的 Pilot R2 已接受投影**，含 `identity_verified=false` / `formal_WAR35_approval=false`。用于分镜信息、知情状态和 Action 风险的语义分析，不冒充 WAR-35 typed/正式批准。
- **Canvas 对照输入**：WAR-37 在独立测试画布的原生插件预览，`canvas-native-preview-v2.md` + `canvas-native-preview-smoke.report.json`（**17/17 PASS**）：真实 1 Beat + 4 Shot + 1 Story Basis 节点、原生 Agent `canvas_select_nodes`/回读、Panel 及零 CanvasConnection；不代表正式 Gate 或已接持久化。
- 离线实现：`docs/planning/WAR-36/verify_revision_d0_cases.py`；输出 `revision-d0-offline-cases.report.json`。该脚本是隔离的**设计规则回归工具**，不是生产 Planner、Review Service、许可证检查或真实模型调用。

### 9.2 已运行的 16 个静态设计用例

| 分类 | 用例 | 结果 | 证据所能说明 |
| --- | --- | --- | --- |
| 合法改动 | 只改第二 Shot 视觉描述 | Candidate | 实差精准定位目标；邻镜和共享 Action 进入保守复检 |
| 无改动 | 完全相同 Plan；只发生 UI 布局变化 | NoChange ×2 | 不造伪 Revision，不清除风险 |
| 越权 | 同时偷偷改第一 Shot | Blocked | 模型自述不可信；意外变更被显式列出 |
| 上游升级 | 修改已确认 Story Basis 事实 | NeedsUpstreamChange | Shot Planner 不越权修改故事事实 |
| 身份/来源 | 过期 revision、source SHA 不匹配、错误 target、Plan ID 变化 | Blocked ×4 | 来源/版本/目标不合条件必须拒绝提交 |
| 数据结构 | 重复 Shot ID | Blocked | JSON Schema 合法不等于语义身份合法 |
| 镜序 | 未授权重排；显式授权重排 | Blocked / Candidate | 结构变更单独 scope，合法重排扩大复检但不自动批准 |
| Action | 同一 Action completion delta 被两个镜头声称完成 | Blocked | 保守拒绝重复完成；跨镜观看仍需另证 |
| 部分接受 | 两字段提案与只接受其中一个字段的重算 | Candidate ×2 | 从基线派生真实新候选，重新 Diff |
| 媒体未知 | 只改观众判据文字但未提供媒体 | Candidate + not_checked | 不能从文字变更推断媒体通过 |

执行结果：**16/16 PASS**，均在内存中，不写批准 Plan、历史账本或真实 Canvas。仅测试 `requestedScope` 和 actual Diff 的确定性骨架及简单 conservative impact。未实现受信签批、完整跨镜时间/遮挡、全来源 resolver、D-JCS /4 的完整真实 Check/Risk/Decision 继承、CAS 持久化或正式 typed UI，故不能声称 D1 已完成。

冻结证据校验值：`verify_revision_d0_cases.py` SHA-256 `7db15d262bf3f62499a18fb1e3f4c1be47b31c85dfb033afe7a5e192159fd118`；`revision-d0-offline-cases.report.json` SHA-256 `5099fa668df76cc179d7355ddb7c2da3cce1ef89bdd58e6572da7855c5434bde`。测试基于真实冻结示例执行，但用于示范的 Scope/Impact 辅助逻辑是**本轮研究工具**，不能替代正式服务的结构约束或 Trusted Review Gate。

### 9.3 《错过的钥匙》的人工专业反例审阅（与自动测试分开）

| 假设反馈 / 候选 | Agent 应判断 | 工程判断 / Canvas 展示 | 当前证据等级 |
| --- | --- | --- | --- |
| “Shot02 钥匙出现太明显，调整观众看到的时机” | 维持“观众先知、周未知、钥匙不移动、再被蓝夹遮住”；提出镜头构图与信息窗口调整 | 只授权 Shot02 相关参数/文本，呈现实际 Diff；Shot01/03、同 Action 与信息遮挡窗口进入 reason 化复检，不自动改邻镜 | 只读推断；未执行新模型 |
| 为强化悬念把周改成提前看见钥匙 | 识别破坏已确定的知情顺序 | `NeedsUpstreamChange` 并保持已批准事实；前端不能只提供“覆盖并通过” | 只读推断 |
| 改 Shot02 后 Shot03 又从起点整理纸张 | 识别同一共享 Action 跨切重复起始风险 | 记录 Action phase / boundary 的待检 Check；不可用文本“接续”声明覆盖实际动作证据 | 只读推断；需真实 typed data |
| 用户只接受“推迟首次露出”，不接受“删除 S03” | Agent 解释部分采纳的叙事影响 | 新隔离候选重新计算 scope/Diff/Impact/证据有效性；不原地修改批准 B 或 DOM | 设计场景，非真实人工审批 |
| 用户仅移动画布上 Shot 卡片 | 不必调用导演模型 | UI 变更属于 Canvas view，不更新 DirectorPlan/Revision/Review | 可据定义判断；实际产品回归待 WAR-42 |

特别说明：当前 **WAR-37 原生插件的四镜与 R2 文字来自 Pilot**，而 WAR-35 正式 v0.1.0 typed 两镜示例来自狐狸案例。**不存在已验证的《错过的钥匙》四镜 typed Plan + 正式受信 Review**；正式集成前必须有适用版本的迁移/映射、真实 revision 和批准身份，否则不能把这两套证据拼装成“已经接好”。

### 9.4 给 WAR-37 / WAR-42 的 Canvas-first 机器交接

**先建立真实定位链，再支持编辑事务**，避免让模型、UI、存储各自维护一份 shotId→nodeId：

```text
User/Agent: select or propose edit on Shot02
  -> CanvasProject identity / active DirectorPlan identity
  -> verified planRevision + sourceFingerprint
  -> stable shotId -> registered canvasNodeId lookup
  -> Canvas Agent select_nodes(real canvasNodeId)
  -> UI reads ProjectedShotView (derived only)
  -> user requests edit with requestedScope and feedbackRef
  -> WAR-36: CreativeContext -> Agent candidate -> ActualDiff -> Scope/Impact
  -> WAR-42: trusted Review + CAS + persistence
  -> WAR-37: reproject Plan and display Diff / review state
```

- WAR-37 自身目标包含**在真实 Canvas 中的原生节点交互与 Agent 定位**，不再是 HTML 原型收口。其 17/17 隔离插件验证满足“真实 Canvas API 预览”的部分门槛；**并不意味着固定侧栏、一键聊天定位、权限、正式批准、历史恢复已完成**。
- WAR-36 向 Canvas 只传**语义数据**：`resultKind`、`baseRevision`、`targetRefs/requestedScope`、`actualChangedRefs/Paths`、`unexpectedChanges`、`recheckTargets` 的 reason/evidenceStatus、`openRisks`、`professionalRationale` 和受信服务可解析的引用。**不要**从 Canvas 节点文本、模型输出或拖线重建权威 DirectorPlan。
- `reviewLedger` 和 `revisionControl` 保留在受信 Store，并提供**按需投影/事件摘要**供右侧专业 Panel 和 Agent；不常驻 Agent 上下文。Shot 位置/布局属于可重建 UI 状态。
- 避免错误连线：Beat/Shot/Action 的关系是 **semantic overlay**，不落入 Canvas 原生 `CanvasConnection`（其下游生成引用语义不同）。Agent 使用真实 `canvas_get_state` + metadata 对照后的 `nodeId`，不按屏幕标签猜 ID。
- **集成职责边界**：WAR-37 负责真实 Canvas 预览与交互体验/节点定位的设计验证；WAR-42 才负责由 WAR-35/36 支撑的 typed Plan/Review、身份权限、真实 CAS 持久化与发布/回滚。两个任务协作，不重复开发第二套 Runtime。

### 9.5 后续 D1 进入门槛

- 已满足：WAR-35 v0.1.0 公共设计契约冻结；WAR-36 D0 复用与严格局部守界设计经用户采纳；本轮 16/16 只读验证、专业纸面反例及 WAR-37 原生插件参考入口已记录。
- 仍待：WAR-33 适用于本次代码复用的版本/许可证/ADR 收口；用户此前要求的**具体 D1 编码范围、测试与回滚授权**；真实 typed 《错过的钥匙》Plan 以及可进行可信 Review/CAS 的存储实现方案。**不以 16/16 或 17/17 代替这些门槛。**
- 推荐下一步：先交 WAR-37 用户原生 Canvas UI 审阅；同时对 WAR-33 **只核最小可影响 Shot Planner D1 的复用/许可缺口**，不重开完整 Toonflow/ViMax 调研；准备 D1 的可执行 ScopeGuard/Impact 接口测试包与回滚方案供用户决策。

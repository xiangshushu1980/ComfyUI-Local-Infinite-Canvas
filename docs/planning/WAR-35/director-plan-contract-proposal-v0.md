# WAR-35｜Director Plan v0 最小数据契约：第二轮设计提案

状态：**既有架构／分级 Review、Beat/Action 2 项、Blocking 3 项、Shot Plan 3 项、独立 Schema 结构，以及 F1–F4 公共字段方向与按需 Action phase，均已获用户确认。** 具体 Ref 编码、hash 规范、状态值表达、校验轮廓与正式 JSON Schema 仍待审阅；未授权实现。2026-11-13。
设备：Eric；仓库：/home/sean/projects/canvas-lab。
上游权威概念规格：docs/planning/WAR-74/director-v0-concept-v1.md（Git 0523ef0e924530b5a27b1b85653a85faeaf36893）。
案例依据：docs/planning/WAR-74/d-b2-b3-paper-contract-walkthrough.md。
任务状态入口：WAR-35；WAR-52 已 Done（design-0.2 设计交付，交叉边界仍待 WAR-35 正式 Schema 联审）；WAR-33 In Progress（复用研究）；WAR-32 已 Done 但 Linear 阻塞关联仍存在。

## 1. 用户已确认的四项决定（2026-11-13）

1. **DirectorPlan 的逻辑契约独立于 Canvas。** 集成 Canvas Lab 时，采用由 CanvasProject 承载的类型化数据结构（可由适配层绑定），不要求 Director Skill 依赖 Canvas 运行，也不另造 Project/Asset/Graph 系统。
2. 采用**关键状态基线 + 事件状态变化 + Shot 边界检查**，不要求每镜完整状态快照。
3. 采用**已批准版本 + 候选修订 + Diff / 检查记录**；候选不覆盖批准基线。
4. WAR-35 先定义通用语义，WAR-52 细化单次 H3 内部 Join，之后才冻结交叉 Schema。

讨论不授权代码实现、改变 Canvas、运行模型/GPU/视频或修改原始 Skill。当前文件是方案正文，不是生产配置。

## 2. 作用域与权威归属（设计提案）

- **已确认（架构修正）**：Director Skill 独立接收一个已确认单场景的剧本/约束和最小主体描述，产出可序列化的 DirectorPlan；本契约不得要求 CanvasProject、CanvasNode 或 AssetStore 必然存在。CanvasProject 内承载 Plan 是 Canvas 集成选择，绑定关系由适配层管理；**不设一个 CanvasProject 只能有一个 DirectorPlan 的规则**，具体多场景组织留待 Canvas 设计。
- 接入 Canvas 时，CanvasProject 持续拥有 projectId、nodes、connections、导入/导出和持久化；Asset Store 持续拥有文字/图片/视频资产。独立 Skill 的 Story Basis 可以使用外部剧本文本/文件的稳定引用及简化场景主体 alias，不要求预建剧本编辑器或资产系统；接入后再绑定现有 Canvas 资产，不复制原素材二进制或新建完整角色/道具实体库。
- DirectorPlan 负责单场景**规划语义、稳定引用、状态变化、审阅和版本**。画布上的文字/图片/视频节点是视图、参考和执行结果，不能成为另一个相互分叉的导演事实源。
- Story Basis 是**当前创作已经采纳的故事依据索引**：源剧本文本/资产的引用与版本、已确定事实与知情/动作/空间约束。它描述当前已采纳的故事边界，而不固化创作者的身份；创意可提议修改这些边界，但不能静默覆盖批准版本。原剧本全文仍存于来源，不在四个产物里复制。
- Director Intent、Beat、Blocking、Shot Plan 分别负责为什么表达、叙事变化、动作空间执行安排、摄影交付；Review 是横切记录，不是第五/第六本事实账。
- Scene/Action/Shot/Join 命名仅有一套**共享语义身份**：WAR-35 定义 Scene 作用域、Action 和 Shot 稳定身份及通用约束；WAR-52 对单次 H3 视频内的 action_phase、shot_boundary、join_constraints、frame_idx 等做执行投影，不能再造并行的 Action/Shot 身份系统。
- Video Execution Unit 是后续 H3 适配/编译的交付单元，不是 Beat 也不是 Shot。Scene Plan 可规划 30–40 秒及更长；12 秒常用、可设计到 15 秒只属于首个 H3 适配设计目标，未证明真实成功率。

## 3. 一个 DirectorPlan 的逻辑组成（不是 JSON 字段定稿）

| 区域 | 最小数据责任 | 关键边界 |
| --- | --- | --- |
| plan header | 独立 planId、schemaVersion（契约版本）、当前 approvedRevision / candidateRevision、scene source binding | **不要求 projectId**；Canvas 侧的 projectId / canvasNodeId 属于适配绑定，不进入导演方法必填条件 |
| storyBasis | sourceRefs（已有文本/资产与版本/指纹）、factRefs、confirmedConstraints、未决事实及其来源 | approved facts 不被模型下游静默改写 |
| directorIntents | stable intentId、basisRefs、creativeGoal（观众信息/注意力/情绪）、信息释放设计、rationale、decisionStatus | 不存焦距/机位/镜头数；按**表达目标与决策约束**分层，而非作者/导演身份；改变已确认故事约束须提出修改案 |
| beats | beatId、事件与因果、intentRefs、eventRefs/actionRefs、state change refs、order/可选节奏偏好 | 不预设 Beat = Shot 或 Beat = 一条 H3 片段 |
| shared actions | 单份稳定 actionRef 及关键行为、参与者/道具 refs、发生/阶段/完成约束 | 允许 Action 跨 Shot，WAR-52 复用 ID；不在 Shot 再定义重复动作 |
| blockings | blockingId、beat/actionRefs、位置/运动/交互/注意力及眼线条件、几何假设和来源 | 世界方向≠屏幕左右；实际看见≠朝某方向看 |
| shots | shotId、intent/beat/blocking/actionRefs、画面信息任务、摄影与覆盖范围、scene-relative timing、必须交付的可见证据判据、边界检查引用 | 不在 Shot 偷改故事因果或角色知情；执行 frame_idx/guide 留给 H3 投影 |
| state | baseline + event deltas + shot boundary expectations/checks，键指向共享主体与事件 | 不为每镜复制所有人物/道具状态 |
| revisions | approved snapshot、候选 revision、patch/diff、影响范围、修订原因、拆合映射 | 批准必须绑定具体 revision，退回可还原 |
| reviews | targetRef + targetRevision + checkKind/method/coverage/result/evidence + decision/openRisk | 检查事实、用户批准和模型建议分开，不冒充媒体实测 |

最小共享主体引用仅需在 Story Basis 为当前场景维护短 alias（例如“林”“周”“银钥匙 K”），可指向来源剧本事实；**资产引用可选**，待 Canvas 接入时才绑定资产 ID，不为其创建跨项目人物数据库。

## 4. 状态模型：四维要分开，但不做四套完整快照

### 4.1 状态值、约束与证据分工

1. **World**：道具位置、遮挡、持有者，动作是否已发生/完成；记录已确认基线和事件引起的变更。
2. **Character awareness/knowledge**：角色实际注意或知道什么；在剧本已确认时可以成为 state delta，但不从物理视线自动推导。
3. **Geometric visibility / sightline**：物理可看见的条件；优先记录为 Blocking 假设与检查条件。除非有充分证据，不将空间猜测升级为“已证事实”。
4. **Audience on-screen legibility/understanding**：Intent 记录**目标**，Shot 记录可检验画面判据，Review 记录文本/代理几何/媒体等实际检查结果；不能因为期望观众看到就填成“已看清”。

### 4.2 计算顺序和粒度

- Scene baseline：关键对象在首个相关事件之前的已确认状态，只记录实际需要判定的不变量。
- Event delta：由 beatId / actionRef 关联的状态变化（主体、维度、从何状态到何状态、来源、顺序、是否完成）。
- Shot entry/exit boundary：引用事件链中适用的状态版本/检查点，并记录镜头实际覆盖的动作**阶段**；若缺状态或证据，标注 unresolved，不填造的通过状态。
- Action “只完成一次”由共享 actionRef + completion marker + 覆盖区间的约束检查表达；Shot 对 Action 的引用不是再次执行事件。
- 受影响状态可以从最近有效 checkpoint 重新推导；性能优化的缓存是派生数据，不作为另一份事实权威。
- 若同一镜头中有多个动作或一个动作跨切点，不要求 Shot/Beat 同长，也不能靠纯镜头文字推断动作已完成。

## 5. ID、来源与版本

- 使用带类型的、**单场景作用域内稳定的逻辑引用**：fact / intent / beat / event / action / blocking / shot / review；真正的 UUID/前缀格式待 Schema 决定。
- 这些逻辑 ID 与 canvasNodeId、assetId、jobId、模型生成 taskId 必须区分；源信息通过外部引用连接，不能硬依赖 UI 上当前节点位置。
- 名字、顺序、镜头景别/焦距/长度变化不改变同一对象的稳定 ID；对象拆分/合并应保留 originRefs、旧→新映射以及历史引用可追溯性。
- 来源和状态至少区分：当前已采纳的故事依据、已批准的创作决定、候选创意/解释、假设、实验或验证证据；是否采纳、是否已验证与提出者身份是不同问题，**不要求按作者/导演职业角色分类**。来源不是可信度自动评分。
- 区分 **contract/schema version**（数据格式）、**story source revision/hash**（剧本依据）、**plan revision**（导演规划）、**evidence target revision**（哪个方案曾被检查）；不能一个版本号包办。
- 已批准基线不可原位覆写。候选基于某一批准修订产生，记录 user requested scope、actual changed paths、unexpected changes、dependencies checked、审阅结果；仅复检且用户批准后更新批准指针。
- v0 暂建议“批准时留完整 Plan 快照 + 候选记录 patch/diff”，避免复杂事件溯源；如需彻底还原候选，可保留候选快照。不用每个 Shot 都独立开版本树。
- 复制或导入新 CanvasProject 时，重绑定 project/asset/node 外部引用，保留场景内部语义 ID 与可追溯来源；失联引用不能悄悄指向同名但不同内容的资产。
- 源脚本或已确认资产变化：通过版本/指纹发现不一致，先标记基线可能失效并请求确认，不自动按新文本改写已经批准的 Story Basis。

## 6. 显式依赖与局部传播

依赖表达优先采用每个规划对象的 refs（基于这些 refs 计算反向索引），不另起一套与 CanvasConnection 并存的“第二画布 Graph”。关系至少能表达：derivedFrom / servesIntent / coversEventOrAction / dependsOnBlocking / requiresState / reviewedAtRevision。

| 修改对象 | 至少需要失效并复检的对象 | 上行边界 |
| --- | --- | --- |
| Story Basis 硬事实/作者意图 | 直接引用的 Intent/Beat/Blocking/Shot + 后继状态 | 必须用户明确批准基础事实变更 |
| Intent | 相关 Beats、Blocking、Shots、观众信息释放顺序 | 不默默改变既有作者意图 |
| Beat / Action | 行为覆盖、Blocking、Shots、后继状态 | 若要求剧本因果变化，上行请求 |
| Blocking | 相关 Shots、眼线、邻镜 continuity、空间假设 | 不将几何假设自动写成 world fact |
| Shot | 信息判据、动作覆盖、时间预算、直接相邻镜头、WAR-52 Join 投影 | 若要求改变人物知情/故事事件，必须上行请求 |

传播流程：意图改动 → 生成候选 → 按实际 changed paths 比对 → 影响闭包/有针对性的检查（不必所有下游重生成）→ 标记 stale/failed/unknown → 展示未解决项 → 用户接受、部分接受或退回。若依赖不明，宁可扩大**复检**范围，不静默批准；“复检范围”不等于“重写范围”。

Review 信息至少包含：被检查对象及 revision、检查类型、方法/证据覆盖范围、结论、未证风险、修复建议、实际修订引用、复检状态、用户决定。规划批准和媒体效果通过是两个正交维度。硬冲突阻塞批准；几何/观众媒体验证未证可在用户明确接受后有条件批准规划。

## 7. D《错过的钥匙》B2/B3 最小数据走查（沿用 WAR-74 说明用 ID，不是冻结样本重跑）

**Story Basis**：F-K1 = 唯一银钥匙在拿起前留在 K；F-INFO1 = 观众先于林发现，周未提前看见；F-SPACE1 = 北墙长桌、东门等确认空间。源内容按版本和来源锚点引用。
**Intent**：I-REVEAL = B2 让观众先认出 K，人物仍未察觉；I-CONCEAL = B3 让观众看到蓝夹把答案再次遮住。
**Events / Beat / Action**：B2 引用 A-MOVE-DOC、A-REVEAL-K，world delta 是“文件遮 K→钥匙在 K 露出”，知识状态中的林/周未察觉保持不变；B3 引用 A-PLACE-FOLDER，world delta 为“钥匙仍在 K，但再次遮挡”，周仅察觉遮挡位置。事件 ID/Action ID 为示意用，不从冻结原始文件伪称已存在。
**Blocking**：BL-B2 是林移走文件且目光不落 K，周从东门接近；几何遮挡为假设。BL-B3 是蓝夹遮 K；尺寸和遮挡是否可实现未证。
**Shots**：S02 = 既有候选 40mm MS，6–12s，任务“观众实际可辨认银钥匙且不误认为角色已发现”；S03 = 85mm ECU，12–18s，任务“观众看见蓝夹逐渐遮住同一 K”。时间为整个场景相对时间，不是独立 H3 unit 的 frame_idx。
**Review**：冻结 WAR-72 低模代理发现 S02 钥匙约 27×9px 且部分遮挡，无法据此宣布观众必然看清；真实观众/H3 效果未证。此证据指向特定 S02 候选与代理条件。

**局部改动样例**：用户拟将 S02 改为 85mm ECU。生成候选 revision R4（基于假定 R3，不代表实际版本存在）；S02 保持 ID，记录 lens/framing 改动。应复检 S02 是否丢失“林移文件”动作因果、构图视觉证据、S02→S03 邻镜关系、时间和动作边界、关联 BL 假设；不触碰 F-K1/F-INFO1/B2。若模型另改 S03，diff 标为超范围变化；若改“周先发现钥匙”，则触发 F-INFO1 硬冲突和上行用户审批。不得声称仅由焦距变化已解决可读性。

## 8. 必须成立的不变量（候选）

1. DirectorPlan 的每个引用可解析到同一规划版本的有效对象或显式未决/历史映射；禁止孤儿引用静默通过。
2. 上游经批准的硬性事件/对白/对象唯一性/知情顺序不能由 Blocking 或 Shot 改写。
3. Action 可跨 Shot，但完成状态不由 Shot 出现次数累加；镜头覆盖不是重复行为授权。
4. 相邻 Shot 共享的世界/动作/持物/对白状态必须显式兼容，或产生可见 Join 风险；WAR-52 决定单次 H3 的细项。
5. Shot 有信息任务及**可观察的画面证据判据**；验证结果必须有方法、范围及所检查的版本。
6. Plan approval 不能引用过期 Review；已接受开放风险不能掩盖确定性硬冲突。
7. Scene-relative 时间和 H3 执行 unit-relative frame/timestamp 分开；不得用 8/12/15 秒或固定镜数限制完整 Scene Plan。
8. 已批准 revision 可恢复；候选不能静默覆盖它；输出的实际 Diff 必须包含超出请求范围的变化。
9. 丢失源资产、源版本变化或引用迁移失败均标记显式风险，不静默重映射。
10. 人工批准导演方案不等于授权 H3 生成，也不等于媒体或观众理解已经实测。

## 9. WAR-52 / WAR-33 对齐及冻结门槛

- WAR-35 先确认同一 Scene 内的 subject/action/shot 身份、通用 state boundary、引用与版本；WAR-52 已 Done（仅设计交付），其单次 H3 执行投影独立持有 action_phases、shot_responsibilities、join_constraints、dialogue_cues、guide_points；公共字段的正式映射留第 18 节审阅，不在 DirectorPlan 内复制 H3 参数。
- WAR-33 的复用研究保留“现有 Canvas 编辑 → 官方 H3 Skill/优化器 → 最薄适配/检查”的边界；当前 Add Guide 非 v0 强制前置，未证 strength/weight 不写成已支持。
- WAR-32 已 Done 但 blocker 仍留在 Linear；在设计/正式 Schema 门槛阶段核查关系是否应解除，不在本文自行改关系。
- 正式 Schema 冻结之前须对齐 WAR-52 核心字段；核验 CanvasProject 的持久化、import/export、复制项目/资产、Agent 节点映射与遗留项目兼容；给出非重复存储/转换的测试设计，不在此轮实现。

## 10. 用户已确认的三项补充决定及独立性原则（2026-11-13）

1. **共享 Action**：DirectorPlan 内一份轻量 action registry（非全局角色/道具实体库），供 Beat/Blocking/Shot 共同引用；WAR-52 用同一 action ID 做 H3 执行投影。
2. **修订粒度**：Plan 级批准版本 + 对象级 lastChangedAtRevision 和 changedPaths/diff，不为每个镜头建立单独批准版本树。
3. **未解析依赖**：缺失对象、引用失效或关键检查过期时，不得无条件批准；扩大复检范围，不自动扩大重写范围。
4. **独立性**：Skill 的输入为已确认单场景文本/来源、创作约束和场景内主体引用；逻辑 DirectorPlan 可以脱离 Canvas 独立读写、审阅和修订。CanvasProject 类型化承载属于后续适配，不强制一 CanvasProject 一 Plan。剧本管理和实体资产管理均不是 WAR-35 前置要求。

## 11. 分级审阅：用户确认的全阶段通用原则（2026-11-13）

**适用范围**：Story Basis 的事实提取及后续 Intent / Beat / Action / Blocking / Shot / Review，统一采用分级审阅；不把每条候选事实都设计为一个人工点击步骤，也不取消 WAR-74 已批准的两处默认审阅门 A（Intent）与 B（Shot / Review）。

1. **剧本直接给出的普通事实**：自动提取，保留具体 sourceRef / sourceVersion / provenance；无歧义时无需逐项重复确认，但提取过程本身不授权重写源故事。
2. **普通导演解释、补足和空间假设**：允许作为显式候选 / assumption 继续规划，记录来源和不确定性，不能被静默升级为已确认世界事实或经验证结果。
3. **影响因果、人物知情、叙事意图、时间先后、关键空间约束的歧义**：若该歧义会改变后续硬约束或导致无法可靠规划，在依赖环节触发作者审阅；未解决不能冒充 approved fact。
4. **已批准且未改变的来源/事实**：引用已批准版本和来源指纹复用，不因重复运行或局部修订要求再次逐项批准；版本变更或新冲突使相关检查过期。
5. **硬冲突与未证风险分开**：硬性矛盾不得无条件批准；视觉、几何或成片效果未证可以在风险明确呈现且用户认可时有条件通过规划审阅，不能宣称媒体已经验证。
6. **审阅触发方式**：Intent 与 Shot/Review 两处仍为默认审阅节点；其他阶段仅因关键歧义、硬冲突、影响批准事实的修改或用户主动请求才额外确认。未解决项需携带至 Review，不能被跳过。

上述是审阅策略决定，不是字段 required/optional 或具体机器执行状态的冻结。

## 12. Director Intent 的职责与创造性（用户确认，2026-11-13）

**基本原则**：Story Basis 与 Director Intent 的边界是创作决策所处的**层次**，不是作者/导演的人员或 Agent 职业分工。一个人或同一个 AI Agent 可以依次完成故事写作、意图设计与镜头设计。我们追求最好的叙事表达，Director Intent 是主动提出表达策略的创造性阶段，而非机械摘抄剧本的“原作者意图”。

- **Story Basis** 回答“当前采纳的故事发生什么、有哪些约束和来源”；可以被新的创作提案修订，但必须保留修订前事实与批准痕迹。
- **Director Intent** 回答“让观众在何时知道/关注/感受到什么，以及为什么这种表达更好”；可以提供多个候选，比较叙事效果和取舍，再由默认审阅门 A 选择或修改。
- **Beat / Blocking / Shot** 分别负责叙事事件与状态、演员/对象空间调度、具体摄影与视觉证据；Intent 不先规定焦距、机位或镜头数。
- **来源和状态不是职业身份**：basisRefs 指向当前故事依据；creativeGoal 与 rationale 说明表达目标和理由；decisionStatus 表示候选/已批准等阶段状态。不要把“作者”和“导演”设为必填身份标签，也不要求模型解释永远低于原作者创意。
- **自由提出上行修改**：若更好的表达需要改变 Story Basis 已确认的事件顺序、知情状态或关键事实，提出显式 story-change proposal，列明受影响约束、收益与代价，并按分级审阅请求批准；在批准之前不得悄悄把候选当成现行故事事实。
- **D《错过的钥匙》案例**：观众先看到钥匙是当前已采纳约束；导演可优化何时聚焦、如何建立期待、如何强调再次遮挡；若提出“观众直到最后才发现”，可以作为新的剧本/表达修改候选供选择，但不得自动覆盖现有版本。

上述字段名是**语义候选**，不是 JSON Schema 锁定；具体 required/optional 留待后续评审。

## 13. 下一步字段级评审范围（尚未开始 Schema）

- 给 Story Basis、Intent、Beat/Action、Blocking、Shot、Review、Revision 确认最少必填字段与可选扩展字段；严格区分独立契约与 Canvas 适配字段。
- 继续使用 D《错过的钥匙》B2/B3 纸面材料检查有效引用、状态变化、修改失效传播；不重复 Blender 或 H3 实验。
- 与 WAR-52 对齐执行投影前不冻结 Join 字段。后续 Canvas 持久化、import/export、多 Plan 组织及资源重新绑定交由集成阶段单独评估。

尚未完成：正式 Schema、字段 required/optional 冻结、项目持久化/导入迁移实现、WAR-52 Join 具体定义、Canvas UI、模型/媒体测试。

## 14. 第四轮｜Beat / Action 的字段级语义提案（2026-11-13，待用户审阅）

### 14.1 概念与允许关系

- **Beat**：叙事层面的有意义变化（因果、信息、情绪、人物关系/知情）；回答「这一段为什么有戏剧意义」。
- **Action**：可追踪的一次具体行为或表演任务（动作、操作、说话），回答「谁对谁/什么做了什么、进行了多少、是否完成」。
- **Shot**：对 Beat/Action 的取景与呈现覆盖，回答「观众通过画面可获得哪些证据」，不是另一次行为发生。
- Beat ↔ Action 是多对多且可覆盖部分：一个 Beat 可含多 Action，一个 Action 可跨 Beat；Beat 可以是纯知情/情绪转折，**不强制拥有 Action**。
- Action ↔ Shot 也是多对多；跨 Shot 是一条 Action 的不同覆盖区间或阶段，不能因 Shot 引用了它两次而重复提交完成事件。
- **不建议 v0 额外创建独立 Event Registry**：世界/知情变化仅在一份共享 StateDelta 结构中保存，由 Action 或 Beat 的触发引用指向；Beat/Action/Shot 各层仅引用，防止重复事实账。如果未来真实例子证明 Event 需要独立身份再增补。

### 14.2 候选最小字段（没有冻结 required 标记）

| 对象 | 候选必要语义 | 按需字段／留给下游 |
| --- | --- | --- |
| Beat | beatId、intentRefs、dramaticChange（含观众信息目标）、因果/顺序约束、actionRefs、stateDeltaRefs | 估计时间/节奏、表演建议；不含镜头硬参数 |
| Action | actionId、actorRef/主体、行为描述与目标对象引用、必要前置与完成条件、相关状态变化 refs、跨 Beat/Shot 复用身份 | 完整 phase 序列、精确时帧、H3 控制词由 WAR-52 执行投影决定 |
| Shared StateDelta | 发生变化的主体与维度、before/after、时间/顺序触发（actionRef 或 beatRef）、事实/假设性质及来源 | 不要求逐 Shot 拷贝对象全量状态 |
| Shot 对动作覆盖 | shotId 引用 actionId、覆盖的概念阶段或起止条件、入/出边界 expected state | 帧级 begin/end、Join 枚举和 Guide 参数由 WAR-52 对齐 |

特别区分**规划预期**和**真实验证结果**：Action 在计划中「预期完成」不等于媒体已实际完成；验证归 Review。角色实际知道什么与观众应理解什么不互相推导。

### 14.3 纸面样例和检查

- D《错过的钥匙》B2：Beat = 钥匙短暂露出、观众获得发现机会；Action = 林移开文件（稳定 ID），世界状态变化 = K 从遮挡变成露出；角色未发现保持原约束；观众是否真的辨认得出由 Shot 判据与 Review 判断。
- B3：新的 Action = 林将蓝夹盖住 K，状态 K 再次遮挡且位置不移动；并非再次执行 B2 的文件移动。
- 狐狸一次跳跃：用同一 actionId 在多个 Shot 中引用起跳、腾空、落地；只发生一次完成。若故事确实让狐狸第二次跳跃，则创建不同 actionId，并可记录 repeatOf。
- 预期检查：Action 引用有效；前置状态满足；动作完成不因多个 Shot 重复；缺少动作阶段不自动填补；相邻 Shot 状态不矛盾；未观察到的媒体结果不被误标为已实现。

### 14.4 两项语义取舍（2026-11-13 用户已确认）

A. **v0 不独立建立 Event Registry**，StateDelta 可引用其触发的 Beat 或 Action，避免第三套行为身份；后续真实场景需要时再增补。
B. **Action 只描述可执行行为/表演**，人物内心知情变化留在 Beat 所关联的 StateDelta；允许有叙事意义但无显式 Action 的 Beat。

上述 A/B 两项已获用户在后续轮次明确确认；不等于正式字段/JSON Schema 已批准。

### 14.5 Codex 并行建议（用户于 2026-11-13 确认已经独立启动 WAR-52；结果待回收）

现有 WAR-52 可并行由 Codex 在 Eric 做只读研究：核对冻结狐狸一次跳跃与 A→B→A 双人对话证据，给出同一 actionId 跨 Shot 的阶段覆盖、state boundary、intra-H3 Join 与至少五种 failure/repair 纸面案例；用 WAR-35 的已确认公共原则做边界检查，不擅自创造新的共享 Scene/Action/Shot IDs，也不提前冻结 WAR-52 Schema。不修改原始 Skill/证据、不运行 H3/GPU、不写 WAR-35 文档。研究正文放 Eric 的 WAR-52 对应 docs 路径并在该 Issue 更新索引。

## 15. 第五轮｜Blocking（表演与空间调度）最小契约提案（2026-11-13，待审阅）

**后续核对更新**：WAR-52 已在 2026-11-13 完成设计交付，见其第 13 节；此 Blocking 提案是历史阶段研究，未在此节运行新实验。

### 15.1 专业职责与阶段边界

**Blocking 负责：在已确认的故事与 Beat/Action 条件下，创造可实行、服务叙事意图的人物、道具、注意力、行动和相对空间调度。** 它不是 3D 建模、不是全场物理仿真，也不是决定最终镜头的 Shot Plan。

- Story Basis 只保存**已采纳**的空间事实与约束（例如北墙长桌、东门、钥匙位置 K）。
- Action Registry 对某次行为的唯一身份、必要前置和完成条件负责（例如“林将遮挡文件移走”）。
- Blocking 描述这条 Action 在空间中的**候选实现**（哪只手/从哪个相对方向、人物从哪里到哪里、朝向/眼线/自然动作），可有多个候选方案，不重复创建 actionId 或提交事实变化。
- Beat/StateDelta 负责世界事实、人物知情等共享状态变化。Blocking 可以对这些状态提出几何可行性约束或冲突，但不得把未经批准的方案直接回写为 Story Basis 硬事实。
- Shot Plan 决定摄影机、景别、镜头节奏与画面可见证据；Blocking 只能提出适合拍摄的观察条件或风险，不提前硬编码具体焦距/机位/画面左右。

### 15.2 最小语义字段（名称及 required/optional 均未冻结）

| 字段候选 | v0 责任 | 与下游边界 |
| --- | --- | --- |
| blockingId | 稳定的调度方案身份 | 不等于 beatId/actionId/shotId |
| scopeRefs | 关联 beatRef / actionRef / 相关 scene portion，支持跨 Beat 的调度 | 不强制一 Beat 一 Blocking 或一 Action 一 Blocking |
| spatialBasisRefs | 引用已确认空间事实、主体、对象、坐标系或相对方位依据 | 不新建资产库或复制场景事实 |
| positions / movements | 关键节点的相对站位、朝向、移动路径/阶段，与 actionId 对齐 | **相对拓扑优先**，XYZ/精确尺寸仅证据需要时补充 |
| interactions | 手/道具/身体的接触、移动/遮挡等表现要求及相对关系 | 世界状态变化仍引用共享 StateDelta |
| gazeAndAttention | 角色头部/眼线指向、角色表现出来的关注对象 | “朝向”不自动推导“物理看见”或“实际知晓” |
| visibilityConditions | 需要实现的视线限制、人物/道具遮挡等**空间条件**，不是镜头最终可读性结论 | 画面观众是否看清交 Shot + Review |
| assumptions / unresolvedRisks | 模型假定的空间布局、尺寸、物理接触与遮挡条件，标明确认来源/待证层级 | 未证条件不能成为已证几何事实 |

并非所有字段对每段都必须出现。核心最低要求是 scopeRefs、足以理解与检查关键行为的调度决定，以及影响叙事的未知风险；精确几何、路径节点、器官/双眼模拟、摄像机参数不作为所有 Blocking 的必填项。

### 15.3 四类状态严格分离

1. **World**：钥匙是否在 K、是否被盖住、谁持有 —— 已确认事实与动作导致的状态变化归 Story Basis / Beat / StateDelta。
2. **Physical sightline**：从周的眼睛是否有被林或文件夹遮住的视线 —— Blocking 的待核几何关系。
3. **Character awareness**：周是否注意到钥匙或理解其意义 —— 故事知情状态，不从眼线几何自动推导。
4. **Audience legibility**：成片中观众是否辨认出钥匙 —— Intent/Shot 的目标加 Review 的证据，不由 Blocking 自行宣告通过。

### 15.4 D《错过的钥匙》最小纸面走查

- **B2 / 林移文件**：确认事实是林在桌南、周从东门侧靠近，钥匙固定在 K；Blocking 候选安排林向西移开文件、视线跟随文件而非 K，周逐渐接近，须维持周不提前看见钥匙的情节约束。林身体遮住周的视线、相机可看清 K 等仍为**待证方案假设**，不能填“已验证”。
- **B3 / 林放蓝夹**：Blocking 安排林在文件堆上放置蓝夹、使伸出部分覆盖 K；要检查蓝夹尺寸/厚度、文件堆支撑和手臂遮挡是否允许此动作，同时保持 K 不移动。既有 WAR-72 代理结果只能约束特定几何/画幅候选，不能证实真实镜头或演员执行。
- 如果调度不可行，先提出**Blocking 候选修改**（文件/人物相对位置/手势），评估是否会与 Story Basis 硬约束冲突。若必须改变已批准的事件或位置，提出上行 story-change proposal，不静默重写。
- 如果用户仅调整人物站位，保留 Beat 与 Action 稳定 ID；复检相关眼线、遮挡、动作可执行性、所有依赖此 Blocking 的 Shots 和邻镜关系，其他无关 Beat/Shot 不自动重生成。

### 15.5 最小验证能力和边界

**文本级可静态检查**：引用缺失、动作对象矛盾、关键前置冲突、移动前后位置关系、空间方位与故事已知事实是否矛盾、知情/视线概念是否混淆、状态不连续风险。

**需要几何/媒体证据**：双眼视线路径、复杂物体接触/碰撞、手/身体遮挡、观众真的看清，以及 H3 是否按调度完成。v0 可以明确未证风险并供审阅，但不得当作已通过。

### 15.6 三项语义取舍（2026-11-13 用户已确认）

1. **默认轻量拓扑/相对空间**：把精确 3D 坐标、物理检测作为按需验证工具，不做 Blocking 成立的前置要求。
2. **允许 Blocking 提供 Shot 的观察约束**：例如“镜头须有机会看清 K 同时不让周看到”，但禁止在 Blocking 中预先定焦距、景别、具体机位。Shot 负责实现可见证据。
3. **允许方案风险有条件留存**：但仅在不与已确认故事硬约束冲突、风险已显式呈现且用户认可时进入下游；文本检查通过≠空间与媒体验证通过。

上述 Blocking 1–3 三项及前轮 Beat/Action 两项均已在后续轮次获用户明确确认；Blocking 字段及正式 Schema 尚未冻结。

## 16. 第六轮｜Shot Plan 最小契约提案（2026-11-13，待审阅）

**输入**：当前 Story Basis、Director Intent、Beat / 共享 Action / StateDelta、Blocking 调度与开放风险。**输出**：逐镜可解释、可修订、有观众画面交付责任的摄影计划。不预先定义 H3 prompt、guide、frame_idx、固定镜数或 H3 执行单元。

### 16.1 Shot 的四类核心责任

1. **叙事任务**：镜头为何存在，观众应得知／暂不知、关注和感受到什么；服务而不重复定义 Intent/Beat。
2. **电影表达**：主体、景别、画面重心、机位/角度、构图、层次、焦点、运动与视觉节奏，以及简短的选择理由；对简单镜头不要求完整摄影参数。
3. **动作与时间覆盖**：Shot 对 actionId 的覆盖阶段，必要的对白、注意力停留、前后镜关系、顺序/时长及切换原因；不得把动作重复展示当作再次发生。
4. **可见证据与风险**：在目标画面中必须能辨认的对象、行为、因果和人物关系，以及防止误读的条件；计划中的可见目标与实际媒体检验分开。

### 16.2 逻辑字段候选（未决定 required/optional）

| 字段候选 | 最小语义 | 不应承担 |
| --- | --- | --- |
| shotId | 稳定身份、顺序锚点 | 不等于 Canvas 节点或 H3 task ID |
| intentRefs / beatRefs / blockingRefs | 上游创作目的、叙事段与调度的引用 | 不拷贝上游事实全文 |
| narrativePurpose | 主要信息/情绪任务，可补充次要任务 | 不是只能服务一个 Beat 的刚性约束 |
| actionCoverage | 复用 actionId 与覆盖的连续阶段、完成条件 | 不因镜头重复引用就重复执行动作 |
| visualDesign | 主体、视觉焦点、构图、空间关系、景别、角度、运动（按需展开）及 rationale | 精确焦距/XYZ 不强制所有镜头填写 |
| timingAndCutIntent | 场景相对顺序、估计时长或范围、重要进入/退出时机、切换动机 | 不等于单次 H3 中的 frame_idx / Join 枚举 |
| audienceEvidenceCriteria | 画面需要展示的可观察证据，关键时机、持续或不可误读条件（按需） | 不宣称观众已经理解或画面已经实现 |
| boundaryStateRefs | Shot 起止世界状态、角色知情、Action 完成及持物等关键 StateDelta/checkpoint 引用 | 不重复建立状态真相 |
| assumptionsAndRisks | 未证几何、遮挡、动作时长、视觉可读性以及版本依赖 | 实际验证结果应归 Review |

Shot 的批准状态属于 Plan Revision / 横切 Review，不需要另建一份镜头事实账。Shot 可有多种职责，但至少明确**主要叙事任务**，在 WAR-52 执行投影中可提炼主要的 shot responsibility。

### 16.3 镜头创作质量，不等于字段完整或多镜头

- 一个 Shot 可以承载多个 Beat 或多条 Action，也可以仅表达情绪变化；每镜一个唯一职责、每 Beat 一个 Shot 均非 v0 通用硬规则。
- 序列级评价包括：信息释放顺序、观众关注点、镜头切换动机、叙事节奏、相邻镜头的画面与空间关系、动作/对白覆盖。不要把更多切镜等同更好表达。
- Shot 能提出需调整 Blocking 的候选，但不得悄悄修改既有事实、人物知情、Action 完成与剧本硬约束。
- 导演阶段的 timing 可先用相对先后＋时长估计或范围；已确认对白、硬性时间条件及因果顺序仍是约束。Scene Plan 不被 H3 单次 12–15 秒目标限死；H3 执行时再精化切点。

### 16.4 D《错过的钥匙》B2/B3 的纸面检验

| Shot | 原冻结候选 | 主要叙事任务 | 预期画面证据 | 尚未证明 |
| --- | --- | --- | --- | --- |
| S02 | 6–12s、40mm MS、西南稍高固定机位 | 观众先于林/周看到唯一银钥匙 K | 林移文件 → K 在同一位置露出，有足够辨认机会且不误导角色知情 | WAR-72 的 960×540 简化代理中 K 约 27×9px 且部分遮挡，不能宣布观众可读性已通过 |
| S03 | 12–18s、85mm ECU、固定机位 | 观众看到答案再次被蓝夹遮住 | 能辨认蓝夹跨过并遮 K 的过程，K 不移动，周不提前看见 | 实体尺寸、手部/蓝夹遮挡、镜头状态切换和真实媒体表现未证 |

**局部改变 S02 的 40mm MS 为 85mm ECU**：候选调整须复检移文件的动作因果是否仍被看到、人物注意力如何呈现、钥匙识别时机、与 S03 的切换/景别/节奏、Action 覆盖和邻镜状态。不能仅凭加长焦距宣称已解决可读性；也不强制通过新增镜头补救。修改 Blocking 时上行提出候选并显示真实 diff，不擅自改 Story Basis。

### 16.5 检查与默认审阅 B

**可文本检查**：上游引用有效、关键观众目标是否有镜头承担、Action/对白覆盖、硬时间与顺序约束、入出状态、Shot 的交付判据是否清楚、是否偷改故事事实。

**需要画面/媒体证据**：对象实际可辨识、眼线和遮挡、表演自然度、镜头节奏实际效果、观众是否理解、H3 是否按计划执行。验证方法、条件、证据文件、目标版本与结果保存在横切 Review；文本通过不代表媒体通过。

审阅 B 呈现镜头序列与创作理由、关键证据判据、Action 和状态覆盖、问题与未证风险、候选修复和实际 diff，用户按分级审阅选择批准、条件批准、退回或局部修改。不要求逐个审普通摄影参数。

### 16.6 三项语义取舍（2026-11-13 用户已确认）

1. **一个 Shot 可以承担多个任务，但必须说明主要叙事职责**；不采用一镜只能服务一个 Beat/信息任务的硬规则。
2. **导演规划允许时长估计/范围和关键切换条件**；不必预先写精确帧，和 WAR-52 的 H3 执行投影分开。
3. **每镜应有可观察的视觉交付判据语义，但不要求统一数值阈值**；关键揭示/遮挡需要更多条件，真实验证结果另存 Review。

本节三个 Shot 取舍已于后续轮次获用户确认；Beat/Action 与 Blocking 共五项亦已确认。WAR-52 已于 2026-11-13 完成 design-0.2 设计交付（见 WAR-52 第 13 节），其 Join 语义可联审但并未交付运行时实现；上述批准仅限语义，不代表字段/正式 Schema 冻结。

## 17. 第七轮｜Review 横切契约（2026-11-13，待审阅）

**定位**：Review 横切 Story Basis、Director Intent、Beat/Action、Blocking、Shot Plan。它不存第二份故事事实、行为状态或摄影内容，也不代替用户的审美选择；负责可追踪的检查、证据、问题与风险、修订影响、批准与复检。Skill 独立于 Canvas；Review 可只依赖本地/外部的证据引用与计划版本。

### 17.1 最小职责分离

1. **Check（检查）**：针对某个具体条件对某一对象或对象集合做可重复的检查（例如钥匙不能复制，Action 不能因跨 Shot 重复完成，重要观众信息任务有对应的画面交付判据）。
2. **Evidence（证据）**：标记来源、实际方法、证据覆盖范围与适用条件（文本审阅、几何代理、真实媒体、人工观看等），绑定被检查的 targetRevision/sourceFingerprint。不能因为方法“更高级”就默认结论可信。
3. **Issue/Risk（问题及风险）**：区分已经确认的硬性冲突、规划假设风险、缺证据的未知、实际媒体失败；注明影响目标与严重性、是否仍开放。风险状态不等于验证结果。
4. **Decision（创作决定）**：在审阅 A/B 或必要额外审阅，对**特定 Plan Revision**批准、附条件批准、退回、请求修改、接受一项明确的开放风险；决定可带理由及范围，不能自动产生已应用修订。

### 17.2 建议的一份 Review 记录引用内容（非正式字段冻结）

| 概念字段候选 | 必须保留的语义 | 边界 |
| --- | --- | --- |
| reviewId / targetRefs | 唯一记录及被检查对象（Intent/Beat/Action/Blocking/Shot/Plan）、适用的 stage/gate | 不复制对象正文；目标可能是多对象或序列级 |
| targetPlanRevision / sourceFingerprint | 对**哪个方案版本**及来源作出的判断 | 修订后旧证据保留历史，不得自动视为适用于新版 |
| checkSpec / scope | 检查的条件、覆盖的对象/动作阶段、前提和无法覆盖的方面 | 不以“整镜通过”掩盖局部缺口 |
| method / result / applicability | 方法（text/static、geometry proxy、actual media、human）、结论（pass/fail/unknown/not-checked）与**是否仍适用**（valid/stale）分别记录 | 方法不等于结果；stale 是版本适用性失效而非画面失败 |
| evidenceRefs | 可追溯来源文档/素材/截图或审阅结论、适用条件/限制、可选哈希 | 不制造虚构证据或要求所有证据保存在 Canvas |
| issues / risks | 冲突或未证风险、受影响目标、可能的后果、当前处理状态 | 保留原风险，即使后续建议修复 |
| proposedChanges / appliedRevision | 建议改动、实际 applied diff、相关 impact/recheck 清单 | 建议、候选修改、已应用版本不能混淆 |
| decision / rationale | 对 targetPlanRevision 的用户选择、条件、未解决项及理由 | Plan 级审阅为默认，必要时可引用特定条目 |

以上为逻辑信息清单，**不要求每个 Review 对象填满所有字段**。一个简单镜头的低风险通过可以简短；关键遮挡/多阶段动作需要展开证据及约束。候选字段细分（Check/Evidence/Risk/Decision 是独立对象还是一份记录的子结构）留到 Schema 评审。

### 17.3 两组正交状态（不合成分数）

- **检查方法、结论及适用性**：method 分 text/static、geometry proxy、actual media、human；result 分 not-checked / pass / fail / unknown；applicability 分 valid / stale（均为语义示意）。无证据并非失败，文本通过并非媒体通过，证据过期也不意味着旧镜头失败。
- **方案决策**：candidate / approved / conditionally-approved / rejected（示意）；审批指向某一完整 Plan Revision，可明确接受开放风险，不自动授权视频生成/最终媒体合格。
- **约束优先级**：已确认的硬事实、对白与知情状态确定性冲突 → 阻塞无条件批准；作者/用户若主动要改动，先正式批准 Story Basis 修改，再重做对应检查。几何可行性、镜头可读性、观众理解、真实媒体等未知 → 有条件通过规划可选，但必须逐项留痕，不能写成已实测。
- **创作质量评审**：可以说明“某镜头为何提升／削弱信息释放、节奏或情绪”的判断和替代方案，但不要求统一评分阈值、自动视觉评测或为了全绿牺牲导演创造性。

### 17.4 A/B 默认审阅与按需触发

- **A（Director Intent）**：审阅观众信息/关注/情绪与揭示顺序，比较候选理由；只将用户采纳的方案纳入当前批准创作方向。Story Basis 中原本已确认内容不要求再次逐条批准。
- **中间步骤自动检查**：Beat/Action/Blocking/Shot 在改变后可重跑引用、因果、动作覆盖/状态和基础时间等检查；只有关键歧义、硬冲突、须改变故事硬约束等触发额外人工审阅。
- **B（Shot Plan/Review）**：展示完整镜头序列、主要叙事职责、视觉交付判据、关键动作覆盖、文本检查结论、空间/视觉/媒体开放项及修订 Diff，由用户决定是否批准方案或有条件批准。
- 对话中的用户可针对任何阶段提出局部修改和额外审阅，但**不是默认每个字段都要确认**。

### 17.5 版本、Diff 与增量复检的五个操作

1. 基于明确的 approved Plan Revision 和 sourceFingerprint 创建 candidate；保留 requestedScope。
2. 修改产生的 actualChangedPaths 与请求对照，必须显示超范围变化；未获得批准前不能静默覆盖 approved snapshot。
3. 计算依赖影响：对修改目标、引用它的下游与必要邻镜的 **Check 适用性**标记需复核；未影响的 checks 可保留，不需要重跑全场。
4. 先选择针对性的检查方法；保留历史 Evidence 原文件/目标版本并标记当前适用性（valid/stale/conditional），未重新做媒体实测不得声称“修复后已通过”。
5. Review 展示 candidate 的问题、实际 Diff、可继承证据、待复检风险与决策；接受全部/部分需形成可追溯的**新批准 revision**（部分接受也要产生可验证的新候选），拒绝则保留旧批准版不变。

**状态传播不等于自动重写**；模糊依赖时扩大复检范围而非让模型重写所有镜头。实现细节和引用版本/条件签名的具体格式留待 Schema。

### 17.6 D《错过的钥匙》B2/B3 的 Review 纸面实例

| 检查条件 | 材料/方法 | 本轮可以支持的结论 | 不能支持的结论 |
| --- | --- | --- | --- |
| 唯一银钥匙 K 在移走前不复制、不移动 | 已确认剧本＋冻结方案文本 | 当前文字链遵守 K 固定、文件遮→露→蓝夹再遮 | 实际生成影像中道具没有漂移 |
| 观众先知、林/周在指定时间未注意 | 剧本文本与计划知情关系 | 叙事意图和候选方案可文字比对 | 周双眼几何全路不可见、观众真正理解 |
| S02 的“观众看清 K” | WAR-72 960×540 几何代理（约 27×9px、部分遮） | 指出在特定简化构图中**可读性未获证明／存在风险** | 真实成片必失败，或真实观众必然发现 K |
| S03 蓝夹实际遮盖 K | 文字/Blocking/Shot 提案 | 可检查叙事覆盖与期望状态 | 未验证尺寸、触碰、手臂遮挡的实体可执行性 |

尚未有用户针对此案例新版本批准的证据，**不得将上述纸面检查记为实际审核 B 已通过**。

假设仅将 S02 从 40mm MS 改为 85mm ECU：旧 S02 视觉/媒体代理证据仍保存在旧 revision；新版本 S02 的画面可读性、动作覆盖、与 S03 邻接关系和受影响 Blocking 假设须重检；Story Basis 的唯一钥匙事实文本检查不因焦距变化而自动失效。新焦距不会自行证明目标成立。

### 17.7 用户已确认的 Review 三项设计决定（2026-11-13；不是正式 Schema）

A. **横切的一份 Review 记录体系**：逻辑上区分 Check / Evidence / Risk / Decision；不为每阶段复制独立事实账或完整 QA 数据库。
B. **检查结果与批准决定正交**：允许附条件批准「导演规划」，但确定性硬冲突阻塞无条件批准；验证证据必须绑定特定版本及其适用条件，不能将文本检查当作媒体效果已验证。
C. **按依赖和实际 Diff 增量失效/复检**：旧证据可追溯、未受影响检查可复用，部分接受产生新候选并再次检查，不覆盖已有批准版本。

三项均为**已批准的 Review 语义原则**；字段 required/optional、状态枚举/JSON Schema、具体检查程序尚未批准或实现。

**历史续接备注**：本段是第七轮当时的下一步；后续用户已明确确认 2+3+3 项及独立 Schema 结构，WAR-52 设计交付已完成。当前入口以第 18 节为准。本轮仍不编码、不改原始 Skill、不运行实验。

## 18. 第八轮｜语义决定确认与公共字段第二次收口（2026-11-13）

### 18.1 已确认决定（本轮用户明确批准）

- **Beat/Action（2 项）**：v0 不建立独立 Event Registry；纯信息、认知或情绪转折允许成为无显式 Action 的 Beat。若没有世界/人物知情的实际变化，不为“观众理解变化”虚构 StateDelta。
- **Blocking（3 项）**：相对站位、拓扑与动作条件优先；允许向 Shot 传递“需要看见／不能误读”的观察约束，但不代替 Shot 决定机位焦距；未证空间风险可在明确接受且无硬冲突时继续规划。
- **Shot（3 项）**：一镜可承担多项叙事任务但需标出主要职责；导演层允许估计时长/范围与切换条件；每镜须有可观察的视觉交付判据语义，不要求统一数值阈值，媒体结果仍交 Review。
- **Schema 结构方向**：独立 DirectorPlan＋横切 Review；共享 Action/StateDelta；WAR-52 H3 投影独立且引用公共身份。此确认不代表正式字段、enum、Draft Schema 文件或生产校验器获批。
- Review 三原则、分级 A/B 审阅门、Plan 级 revision、Scene/source 作用域和独立 Canvas 运行边界继续有效。

### 18.2 去重原则与候选最小结构（以下均待审阅）

| 语义权威 | 候选结构 | 其他层只保留 |
| --- | --- | --- |
| Story Basis | sourceRefs（定位＋版本/指纹），采纳的事实/约束，主体场景 alias | source/fact/subject refs |
| Director Intent | intentId、basisRefs、creativeGoal、rationale；可选信息释放安排 | intentRef 与镜头交付目标，不复写目标全文 |
| Beat | beatId、dramaticChange、可选 intentRefs/actionRefs/deltaRefs；顺序及因果约束 | beatRef；不为每 Beat 复制 Action |
| Action Registry | actionId、描述、必要前置、一次性完成条件；按需阶段 key | actionRef＋阶段覆盖，不重新声明完成事实 |
| State | 有限 baseline＋deltaId/stateKey/before/after/triggerRef；分别处理 world/characterKnowledge | 关键 checkpoint / delta refs；无每镜全量快照 |
| Blocking | blockingId、scopeRefs、必要 staging，按需空间关系、眼线／遮挡假设及观察约束 | blockingRef；不定 Shot 摄影参数 |
| Shot | shotId、上游目的 refs、primaryPurpose、visualDesign、evidenceCriteria；按需 coverage、scene-relative timing、boundary refs | H3 再细化 unit frame/Guide/Join |
| Review & Revision | Plan 级 revision / approved baseline + candidate Diff；横切 check/evidence/risk/decision 独立引用目标 revision/hash | 不在每对象另建批准字段／版本树 |

候选统一规则：各对象 **创建后**的身份/核心内容必填；整个 Plan **保存工作草稿时**不要求下游数组已经生成。资产、CanvasProject、CanvasNode、job、H3 frame_idx 和 Guide 均非独立 DirectorPlan 必填字段。

### 18.3 F1–F4 公共字段设计方向（后续获用户明确批准，字段表示仍待审阅）

**F1｜引用身份与来源**。推荐：场景内单一 planId/sceneId 作用域，registry 中 id 稳定，跨类型引用应能确定 kind＋id（采用字符串编码还是结构化 Ref 留待字段冻结）；Story Basis 外部来源记录 locator/版本/sha256，允许缺 Canvas assetId。源内容版本变化不得静默绑定同名资源。各对象的 lastChangedAtRevision 为可选索引/派生元数据，最终以修订 Diff 为准。

**F2｜StateDelta 与 Action 覆盖（含按需 phase）**。已确认方向：StateDelta 统一具有 deltaId、stateKey、before/after、triggerRef（指向 Beat 或 Action）及顺序依据；world 与角色知识使用不同 stateKey 范畴；只记录真实拟发生的关键事实变化。Action 只维护一次完成条件（单次完成动作才要求）；必要时附稳定 phaseKey。Shot actionCoverage 从现有仅 [actionId] 升为可选 `{actionRef,phaseFrom?,phaseTo?,completionDeltaRef?}`：它是“计划覆盖”而非再次触发动作，completionDeltaRef 指向**同一共享 StateDelta**。完整／部分交付的 H3 unit 标记和帧时点由 WAR-52 Projection 决定，媒体实际完成由 Review 判定。

**F3｜Revision/Review 绑定与无自引用指纹**。推荐：独立 Plan 核心内容计算 versioned contentFingerprint；Review ledger 逻辑上与 Plan 分离（可同一外层 bundle 运输），但不纳入该 Plan 指纹，否则审阅会引起递归失效。Review check 具 targetRefs、plan revision/content fingerprint、checkSpec、method、result、applicability、evidenceRefs；decision 绑定目标 revision/gate（Intent A、Shot B、exception）和明确接受的 riskRefs。审批指向具体 Plan revision，不是各镜独立审批树；A 门审创作方向不等于整场 Plan 已获 B 门或执行授权。approved pointer 属于 Plan 的 revision/存储索引层，不应作为被自身指纹覆盖的业务可变内容。正式 canonical JSON/hash 规则尚待明确，WAR-52 的合成示例算法不自动成为生产算法。

**F4｜分阶段保存与门槛**。推荐：一套 DirectorPlan schema，另给 `draft-saveable`（只校验输入与已有对象）、`intent-review-ready`（必须具可审意图及来源）、`shot-review-ready`（有成序列 Shot、判据、必要覆盖/状态及开放风险）、`h3-projection-ready`（WAR-52 unit 精确帧/Join/asset/Guide 检查）的语义检查 profile。缺席的后续阶段是“未形成”，不是“已验证通过”；未解决硬约束禁止无条件批准。不得把 12–15 秒或固定四镜限制施于 DirectorPlan Scene Plan。

### 18.4 WAR-52 已完成设计的兼容边界

WAR-52 design-0.2（Git de755b5）已定：复用共享 plan/scene/action/shot refs 与 source Plan hash；Plan StateDelta 完成引用不可产生第二 completed 真值；Join 使用视觉变化与状态关系两维，`state_at(b)` 检查；完整/部分动作覆盖有不同完成要求；Guide 可空但无效/未知能力不可静默忽略；projection 与 Plan 有独立版本/内容指纹。公共 Draft **不复制** H3 的 action_phases 时间帧、join_constraints、Picture、Guide 参数；F1–F4 的具体公共字段映射仍须评审。

### 18.5 本轮评审出口

**已确认（2026-11-13，本轮用户回复）**：F1–F4 全部采用推荐方向，Action phase 仅在跨镜或关键行为需要时在公共 Plan 中记录，H3 执行投影再细化。用户要求主动报告值得关注的设计问题，并授权必要时使用 Eric 的 Codex Agent 做只读交叉审阅。具体 Ref 编码、StateValue/状态顺序、Review 检查可继承指纹、批准指针的规范化与 draft 语义门槛仍需进入正式 Schema 字段评审；**F1–F4 无须再次确认**。下一步准备最小 JSON Schema v0 草案、两类样例（无 Action Beat／跨 Shot 一次性 Action）及不变量对照，冻结前检查 WAR-33/32 与 Canvas 最薄适配边界；不编码、不运行实验、不修改原始 Skill、不更新生产数据。

## 19. 第九轮｜Codex 只读交叉审阅与 Schema 冻结前四个缺口（2026-11-13）

### 19.1 审阅事实与范围

- **用户已确认**：§18 F1–F4 的架构/字段方向，以及公共 Action phase 按需保存、H3 投影再细化；不得把这些已有决定重新列为待选项。
- **独立审阅**：ChatGPT 使用 DCR 在 **Eric** 调用本机 Codex CLI v0.167.2、read-only sandbox（本轮 session `01a1d536-4432-7543-9983-091f3663c097`），只读 §18、WAR-52 §12–13 与其 draft schema 相关字段；审阅进程完成，未编辑仓库文件、运行测试、联网或调用 GPU。Codex 输出属于独立设计意见，不自动构成用户批准、Schema 实现或证据验证。
- **结论**：已批准方向无根本矛盾，但 v0 正式 Schema 前有四个必须闭合的表示/语义缺口。以下为 **ChatGPT 综合建议，均待字段级审阅**。

### 19.2 审阅发现与最小修正（非正式冻结决定）

| 缺口 | 具体失败例 | 推荐最小表示/规则 | 阶段门槛 |
| --- | --- | --- | --- |
| R1 Review 的 A 门有效性 | r1 Intent A 通过，r2 仅新增 Shot；完整 Plan hash 改变，错误地取消 A 或错误地无条件沿用 | 每 Check 除原 planRevision+planHash 外，保存所检查 targetRefs、dependencyRefs 和 `dependencyFingerprint`；跨 revision 重新计算依赖闭包一致才记录显式继承，原证据/决定始终指回 r1。继承 A 既不批准 r2 的 B，也不授权 H3 | 正式 Review Schema 前 |
| R2 未落盘剧本文本来源 | 粘贴剧本尚无文件，只有内存/会话定位或 hash，导出后找不到原文 | 外部 source 可为不可变且可解析的引用，或在独立 `DirectorPackage` 的 sourceSnapshots 随包保存**一次**文本快照；Story Basis 只引用 sourceId、版本和原始字节指纹，不在多个产物复制全文；来源丢失可保存 draft、不能标已验证/无条件批准 | Story Basis Schema 前 |
| R3 StateDelta 非确定性 | 同一个 Beat 先拾取再转交同一道具但 triggerRef 相同；未知 holder 被误当成 null | StateValue 区分 `known(value)`（value 可为 null）与 `unknown`；缺值不得隐式理解为已知空值。共享 Delta 以 `afterDeltaRefs` 或等价依据给同一 stateKey 变化可验证顺序；未知/环/冲突须报告 unresolved/fail，不杜撰执行链 | State/Action Schema 前 |
| R4 phase/ref 解析不闭合 | 两个 Action 同有 `reach` phase；公共 Plan 无相位而 H3 必须有 phase_key | ref 类型、场景作用域、目标 registry 固定；公共 phase 身份由 `actionRef + phaseKey` 唯一化，按 Action 定义顺序，Shot phaseFrom/To 只在定义了公共 phase 时出现（推荐两端均包含）；公共 phase 缺席时 H3 可独立细化并指回同一个 Action ID，不得要求所有投影 phase 必须存在于公共层。禁止不存在的 event 类型引用 | Ref/投影映射 Schema 前 |

**R1 进一步规范**：需要定义 Plan 核心指纹范围：Story Basis 引用及被规划内容、Intents、Beats、Actions、StateDeltas、Blocking、Shots 与契约/修订身份；排除 reviewLedger、approved 指针、派生 diff/changedPaths、缓存和指纹自身。检查继承依据是“被检查内容及其依赖未变化”，不是只凭相同对象 ID 或相同 Plan revision。源版本变更导致受影响检查 stale，不能静默复用。选择具体 canonical JSON 算法/版本是后续格式冻结事项。

**R2 进一步规范**：`sourceId` 身份与 `sourceVersion` 内容版本分别维护；对粘贴文本按捕获的精确 UTF-8 字节计算 SHA-256（如要换成规范化文本哈希，必须声明独立算法/版本，不能混用）。仅改变 locator 不视为修改原文；快照不必先写入 Canvas AssetStore。正式导出时必须确保 embedded 或 external immutable source 可解析，来源缺失不能谎称可移植。

**R3 进一步规范**：只要求**对同一 stateKey 的变化**有可推导的局部顺序，避免对互不相关的状态强制完全排序；StateDelta 应标明 triggerRef（Beat/Action）、source/provenance、已知性与必要完成引用。一次性 Action completionCondition 引用共享完成 delta，Shot coverage 与 WAR-52 phase completion 只能引用该 delta，不能建立第二个独立布尔值。世界状态与角色知情的 stateKey 彼此分区，不从眼线推出知情。

**R4 进一步规范**：公共对象 ID 在同一 Scene/Plan 作用域内稳定，类型前缀是候选序列化方案（如 `action:A-JUMP`），WAR-52 `action_ref` 映射到同一原始稳定 actionId，不得分配新 identity；是否选择字符串编码还是结构化 Ref 仍属于字段审阅，不因本次审阅自动冻结。

### 19.3 用于审阅的两个最小示例（语义 sketch，非 JSON Schema 文件）

**无需显式 Action 的 Beat：** `{ "beatId": "B-DOUBT", "intentRefs": ["intent:I-DOUBT"], "dramaticChange": "观众开始怀疑角色在隐瞒", "actionRefs": [], "deltaRefs": [] }`。不必为了观众理解发生变化而编造 world 或 character-knowledge delta；仍需有来源与可审故事约束。

**Action 跨两镜：** 一份 `actionId: "A-JUMP"` 定义可选 `phaseKeys: ["prepare","takeoff","airborne","land"]` 与 `completionDeltaRef: "delta:D-LAND"`；S01 coverage 指 `action:A-JUMP` 的 `prepare→airborne`，S02 指 `airborne→land`；两镜重复覆盖 `airborne` 不等于重复执行。没有公共 phase 的普通 Action，Shot 可只指 actionRef，执行时 WAR-52 生成绑定同一 ID 的投影 phase。实际是否完成仍须媒体 Review，不从计划完成推断。

### 19.4 本轮决策边界与下一步

- **已确认**：F1–F4 方向、phase 按需、全部既有架构与 Review 语义（§18）。
- **待确认/待审阅**：R1–R4 所提出的最小字段规则、具体 Ref 编码、StateValue 结构、Action 完成 Delta 引用、版本化 hash 算法和 Review 依赖指纹表示。Codex 不替用户作决定。
- **下一步**：以 R1–R4 的最小修正为候选细化 required/optional 表和 Draft 2020-12 JSON Schema v0（设计稿），提供上述正例及缺源/旧 Check 错继承/状态乱序/跨镜重完成等反例的语义检查清单；核对 WAR-52 的 identity、projection hash 和 H3 的严格就绪门槛。用户审阅前不冻结、不实施。

## 20. 第十轮｜独立 DirectorPlan JSON Schema 设计候选（2026-11-13，待用户审阅）

**候选状态与文件入口**：本节为 WAR-35 的唯一详细设计分析；机器可读格式在同目录 `director-plan.schema.review-v0.json`（JSON Schema Draft 2020-12，`director-plan/0.0-review`，**非正式冻结 v0**）。两个合成正例为 `no-action-beat.example.review-v0.json`、`cross-shot-once.example.review-v0.json`。这些是设计规格资产，不是生产代码或 Director Skill，实现/Canvas/H3 运行均未授权。上一轮 F1–F4 和公共 phase 按需原则已获批准；此处的具体字段、Ref 编码、StateValue 结构、hash 规则及校验职责仍是待审阅候选。

### 20.1 最小契约与权威分离

`DirectorPackage` 仅是便携交付封装：根对象 `contractVersion`、`plan`（required），`sourceSnapshots`、`reviewLedger`、`revisionControl`（optional）。**Plan 内容指纹候选 payload 为 `{contractVersion, plan}` 的规范化值**；外层修订批准指针、候选 diff、Review 证据与原剧本全文快照排除，且 Plan 自身不保存自己的 hash。因为 Plan 的 Story Basis 已绑定 `sourceId+contentSha256`，正确核对来源快照的语义门禁能防止源内容变化被忽略。正式 canonical JSON 与 hashRule 标识仍待定，不得直接拿 WAR-52 合成 fixture 的算法充当生产约定。

| 区域 | 生成该区域时的必要信息（Schema required） | 按需或可缺席 | 不做的事 |
| --- | --- | --- | --- |
| Package | `contractVersion`, `plan` | snapshots、Review、revisionControl | 不强制 CanvasProject |
| Plan | `planId`, `sceneId`, `revisionId`, `storyBasis` | 未形成阶段的数组可完全缺席 | 不把审批指针/差异加入哈希 |
| Story Basis | 至少一条 `sources`；每条 `sourceId`, `mediaKind` | sha、定位、版本、事实、主体、约束；缺 sha 只允许草稿 | 不复制剧本全文到各层 |
| Intent | `id`, `basisRefs`, `creativeGoal`, `rationale` | releaseStrategy | 不存镜头焦距和切点 |
| Beat | `id`, `dramaticChange` | intentRefs/actionRefs/deltaRefs/afterBeatRefs | 允许无 Action/Delta |
| Action | `id`, `description`, `temporalKind`; once 条件必需 `completion` | phases、参与主体和前置条件 | 不因跨镜变出第二个 Action |
| State | 基线项 `key/value`；Delta 的 id/key/before/after/triggerRef | baseline、deltas 整体可缺席；delta afterDeltaRefs/provenanceRefs 可缺席 | unknown 不等于 null |
| Blocking | `id`, `scopeRefs`, `staging` | 空间依据、观察约束、假设 | 不决定摄影参数 |
| Shot | `id`, `primaryPurpose`, `visualDesign`, 非空 `evidenceCriteria` | Intent/Beat/Blocking refs，覆盖、估时和状态边界 | 不含帧级 Join/Guide |
| Review Check | id、Plan revision/hash、target/dependency refs、dependency hash＋规则版本、checkSpec＋版本、method/result/applicability | evidenceRefs | 证据继承须复核目标与依赖范围 |
| Review Decision | id、gate、Plan revision/hash、依据的 checkIds、verdict | 有版本的 acceptedRisks/rationale | Check 可继承不等于 Decision 可继承 |
| Revision Control | 可持 approvedPlan（decisionId＋gate＋target）或候选列表 | candidate 的 request/actualChangedPaths | Intent A 不能直接形成整 Plan approved 指针；不进入内容指纹 |

**Ref 草案**：公共 `kind:localId`，kind 仅为 `plan/source/fact/subject/intent/beat/action/delta/blocking/shot`，不引入 `event`；各 registry 项用单独的 `id` 保存 localId，通过上下文 registry 解析。Action phase 只在所属 Action 内拥有 `key`，身份是 (actionId, phaseKey)，不能直接当全局实体引用。公共 `phaseSpan.from/through` 是**两端包含**的阶段范围；具体同镜/跨镜叙事覆盖是否完整由语义检查判断。WAR-52 使用源 Action 稳定身份，必要时再建立投影自己的细化 phase 键。

### 20.2 核心不变量与检查门槛（Schema 形状≠语义验证）

| 规则 | 归属 | 检查/拒绝条件 |
| --- | --- | --- |
| P01 | JSON Schema | required、类型、非空判据、once 必需 completion、合法 ref kind、禁止未知结构键 |
| P02 | Semantic / all stages | 本 Plan registry ID 唯一且 typedRef 对应正确 registry；缺引用标 unresolved，类型错绑拒绝 |
| P03 | Story source | inline 快照 UTF-8 字节 SHA 与 sourceBinding 一致；导出时每个必需 source 均可独立解析；更改 locator 不冒充改剧本 |
| P04 | State chain | 同 key 的 delta 通过 `afterDeltaRefs` 或等价已证明顺序形成非冲突可重复计算的偏序；禁止环/冲突，无声明即不能凭数组顺序捏造事件先后 |
| P05 | Known vs unknown | known(null) 是合法已知业务空值；unknown 是未证，不能暗作空值、不能据此判断前置为 pass |
| P06 | Action completed once | once Action 只有一份 completion.deltaRef，指向共享 Delta 且 triggerRef 属于该 Action，条件与 Delta 内容一致；Shot coverage 只引用该 Delta |
| P07 | Phase / Coverage | 需要的 phaseKey 解析到该 Action、phaseSpan 顺序合法；跨镜相邻覆盖可以重复某阶段用于镜头表现，不能重复提交完成 Delta |
| P08 | Shot/Story | 镜头叙事任务、可观察判据、关键故事知情和世界状态约束一致；正文修改不能在 Shot 私设新故事 |
| P09 | Review binding | Check 保留原 Plan 版本/内容 hash，并记录依赖范围 hash；只有对新版本复算完全一致，才允许显式继承，失败/未知不能继承为 pass |
| P10 | Gate A/B | A 的有效证据继承不自动批准 B 或视频生成；硬冲突阻止无条件批准，媒体未知可被明确有条件接受 |
| P11 | WAR-52 projection | 公共 ID 共享，H3 具体帧/Join/Guide/Reference/Dialogue cue 由投影检查；投影的完成 marker 引用同一 StateDelta，Join 不二次 apply Delta |
| P12 | Revision Diff | approval/candidate/check 间的 revision、sourceDigest 与实际 changedPaths 一致；扩复检不等于扩重写 |

Schema 的 `draft-saveable` profile 只要求已出现的对象格式正确、已知硬矛盾不得误报通过；`intent-review-ready` 增加可定位故事依据、Intent 目标及 A 门条件；`shot-review-ready` 增加 Shot 序列、动作覆盖、关键状态与视觉证据/开放风险；`h3-projection-ready` 才按 WAR-52 设计要求检查 unit 精确帧、状态继承、Reference/Guide 语义和适配能力。**一套 Schema 四个检查 profile，不增加四套 JSON 格式。**

### 20.3 正例与故障/修复检查规格

两份正例均为**合成的待审设计示例**，未伪造用户批准记录、没有 H3 媒体结论：

- A：`no-action-beat.example.review-v0.json`：直接粘贴剧本由 sourceSnapshots 便携保存，Beat 的观众怀疑变化有 creativeGoal，但没有显式 Action，也不虚构角色知情 StateDelta。
- B：`cross-shot-once.example.review-v0.json`：一次 A-JUMP 有 prepare/takeoff/airborne/land 可选 phases，两镜共同覆盖 airborne；共享 D-LAND 只在最后落地时作为完成 delta 使用。没有精确帧、Guide 或第二套完成真值。

| 反例 ID | 变体 / 预期拒绝 | 检查层 |
| --- | --- | --- |
| N01 | `event:E01` 假装全局事件 Ref；未知引用类型直接拒绝 | Schema |
| N02 | once Action 没有 completion；拒绝其作为已定义 once 动作 | Schema |
| N03 | 文本快照改字但沿用旧 contentSha256；不许标来源可用 | semantic source |
| N04 | baseline 缺失却将 unknown holder 判为 null/无人持有；检查 unknown | semantic state |
| N05 | 同一状态键两个冲突 Delta 未指定顺序，或 `afterDeltaRefs` 构成环 | semantic state |
| N06 | Shot 引用另一个 Action 的完成 Delta、或一次 Action 在两镜完成两次 | semantic action |
| N07 | r2 改了 A 的来源/意图，却静默继承 r1 的 A 门检查 pass | semantic review |
| N08 | r2 只新增 Shot，全 Plan hash 改变而 A 依赖未变；应允许**显式检查继承**，不得强制旧 A 无条件失效，也不能自动通过 B | semantic review |
| N09 | 相同 Action 重复 phaseKey，或 phaseSpan 端点/顺序无效 | semantic phase |
| N10 | 无公共 phase 的合法 Action 在 H3 投影补 phase，但擅自分配新 Action ID | projection mapping |
| N11 | r2 新镜头变更了 source/预期事实但 Review 未标 stale | revision/review |
| N12 | Guide 无效时静默丢弃后提交 H3；错误，应明确失败/待核 | WAR-52 execution |

### 20.4 已完成的静态设计检查和剩余收口

Eric 本机 `jsonschema` Draft 2020-12 meta-validation 通过，两例符合本 Schema 的**结构校验**；两份 sourceSnapshots 的 SHA-256 按 UTF-8 原文本复算一致。尚未交付 P02–P12 的完整跨字段语义校验器，没有运行任何视频/GPU/Blender 或生产接口。机器可读 draft 在项目 repo 的 docs 下，仍属非冻结设计资产；具体 JSON canonicalization、hashRule、Review 依赖闭包和 source resolver 在正式冻结时仍须明确并验证。

**需要用户实际审阅的点**：R1–R4 的字段化取舍（尤以 A 门跨 revision 继承）、`kind:localId` 的公共引用编码、sourceSnapshots 便携策略、unknown 值结构及 phaseSpan 包含端点。无须重审已确认的 F1–F4 架构方向。依据本轮同一批文件的只读独立审阅结果（如有）可补充独立缺口，但不擅自将推论升格为用户批准。

### 20.5 Codex 第二次只读审阅后的候选修订（尚未批准）

Eric 本机 Codex CLI v0.167.2（session `01a1d542-d4d7-7b92-82d8-9510fa43fc9c`）以严格只读方式审阅 Schema、两份合成示例、§18–19 和 WAR-52 局部设计；Codex 未修改文件、未运行测试或调用生成服务。审阅结果为 **5 项正式冻结前须闭合、1 项可延后**；均不推翻用户已批准的架构。

| 审阅结论 | 本轮如何处理 | 仍待什么 |
| --- | --- | --- |
| C1：Check 依赖指纹可能漏掉目标自身、检查规则版本、集合/序列成员关系 | draft 的 Check 增加 `checkSpecVersion` 和 `dependencyHashRule`，Inheritance 增加同名 hashRule；文档要求依赖闭包包含 target、自身、相关来源与成员/顺序 | 精确的依赖闭包、hash profile 与重算规则需冻结 |
| C2：Check 可继承不代表原 Decision 可自动继承；批准指针与 gate 未绑定，接受风险可变 | Decision 增加 `checkIds`；RevisionControl 候选 `approvedPlan={decisionId,gate,target}`，不接受 Intent A 直接写整 Plan 指针；Risk 增加 `riskVersionId` 和绑定 Plan target，决定通过 `acceptedRisks=[{riskId,riskVersionId}]` 引用 | 需要语义检查：decision 的 checks/risks/gate 与指针一致；风险记录不可原位改写，Check 继承不自动继承 Decision |
| C3：StateDelta unknown、同键顺序、完成判据未闭合 | 维持 `known(value)` / `unknown` 结构；要求“缺 baseline = unknown；unknown 不作匹配通配符，同键变化无环且顺序足够确定；完成 Delta before/after 必须与 Action completionCondition 一致” | 实际语义验证程序未实现，不能声称 P04–P07 已通过 |
| C4：WAR-52 中只有必需 `phase_key`，缺公共 phase 映射 | 规划侧仍允许无 phase 的 Action；建议 WAR-52 后续投影草案增加可选 `publicPhaseKey`（按同一 actionRef 解析）；无公共 phase 时为投影内部 key | **尚未修改 WAR-52 的 schema**；必须在交叉 schema 正式冻结前联审 |
| C5：Plan hash 只算 `plan` 会漏掉根层 contractVersion；来源快照匹配与 hash 规则未知 | 草案 hash payload 说明修正为 **`{contractVersion,plan}`**；快照按 `(sourceId,contentSha256)` 匹配，UTF-8 原始文本复算，不自动归一化；Revision/Review/源全文不入 hash | canonical JSON 算法、命名的 hashRule 及 WAR-52 相应映射尚待正式冻结 |
| C6：Story Basis 已有 constraints 但不能单独引用（可延后） | 草案先增加 `constraint:` typedRef 并允许 Intent/Blocking 引用已有 constraint，无独立约束数据库 | 具体消费位置和引用解析由字段联审确认 |

**必须主动提醒的设计风险**：草案可以结构合法但错误继承 A 门审阅、错误设置整 Plan approved 指针或把未知状态判为动作完成。当前 draft 已增加表示能力，但这些都还需 P02–P12 语义校验与用户审阅方可获得真正保证；请勿将 Schema 结构校验通过视为审批安全性已经通过。

本轮只修订 WAR-35 的非冻结设计 JSON；未触碰 WAR-52 原始 schema、生产 Canvas、Skill、模型或视频。以上 C1–C6 是下一轮正式字段/联审的候选解决方案，**不是用户已确认决定**。

## 21. 第十一轮｜版本化指纹、Review 继承与 WAR-52 投影交叉收口（2026-11-13；候选待最终冻结）

### 21.1 本轮授权与结论边界

用户明确“按照建议继续下一轮”，采用第 20.5 节 C1–C5 的**最小修正方向**与 C6 的轻量 constraint 引用；该授权允许完成设计与交叉审阅，不等于正式 JSON Schema 已冻结、验证器已实施或批准 WAR-52 已 Done 的原始设计基线发生变更。研究正文仍仅此文件为唯一权威；机器可读 design draft 见同目录。WAR-35 保持独立：不要求 CanvasProject、实体库、Storyboard 或 H3/Guide 先存在。

本轮聚焦三个可验证的设计不变量：(1) 相同 Plan 内容跨宿主得到相同 SHA-256，避免“看起来一样但指纹不同”；(2) Check 只在其实际审查依赖未变时继承，**检查继承不等于审批或媒体通过**；(3) WAR-52 仅投影既有 Action/StateDelta，不产生第二权威完成状态。

### 21.2 Plan 内容指纹 Profile：P-JCS-1（推荐采用，尚未正式发布）

- Profile 标识：`war35-plan-jcs8785-sha256/1`（设计约定）。被哈希对象严格是 `{"contractVersion": package.contractVersion, "plan": package.plan}`，不是整个 Package，也不是单独的 Plan。
- 解析先执行 JSON 与 **I-JSON** 有效性检查：拒绝重复 object key、不能被正确表达为有限 IEEE-754 binary64 的数值或不合法 Unicode；拒绝非有限数值。不因为格式合法就允许非法来源或引用。
- 编码遵守 **RFC 8785 JCS**：对象属性按 UTF-16 code units 规则递归排序；数组保留原始顺序；字符串保留原 Unicode 码点序列且不进行 NFC/NFD/换行规范化；JSON 数值按 ECMAScript 规范串行化；对最终 canonical JSON 的 UTF-8 字节计算 SHA-256，输出小写 64 位十六进制。
- 内容中 `planId/sceneId/revisionId` 与 Story Basis 已绑定的 `sourceId/contentSha256` 都参与哈希。修改 revisionId 产生不同整 Plan 指纹，这是预期；使用 Review 依赖指纹以继承**未改内容的**检查，不能因此从完整 Plan hash 中去掉 revisionId。
- **不参与**：`sourceSnapshots` 全文（但 binding 的 source 内容 hash 参与）、`reviewLedger`、`revisionControl` 的 approved/candidate/diff、Check/Evidence/Risk/Decision、生成缓存/适配器上下文、Plan 外存储位置及 digest 字段本身。
- `sourceSnapshots` 以内联 `text` 解析后的 Unicode 内容按 UTF-8 字节计算原始文本 hash，不做独立 JCS 规范化；以 `(sourceId, contentSha256)` 与 Story Basis 的 sourceBinding 精确匹配。**本轮非冻结草案已将纯解析 locator 移至 Package 的 `sourceLocators` sidecar**（见 §21.6），因此仅变更来源解析位置不改变 Plan 内容指纹；正式冻结前仍须校验对应内容确实可解析。
- 两个版本 Profile 必须有不同标识；不允许 RFC 8785 与 WAR-52 早期合成样例的 Python “sorted-keys compact JSON” 混称相同 SHA。已有 WAR-52 `design-0.2` 的 hash 是 fixture 约定，不反向变更/重算其已存冻结样例。
- **验证门槛**：Eric 上已创建隔离环境并通过 **21 组**跨 Python/Node 三实现的 JCS 字节/哈希一致性测试（含 RFC 8785 Appendix B 选定数字向量），详见 §22 和 `jcs-verification.report.json`；官方全量语料与其他宿主、正式 D-JCS-1 依赖闭包实现仍未验证。采用公开固定规格，不把 Python `json.dumps(sort_keys=True)` 冒充 JCS。

### 21.3 Check 依赖闭包 Profile：D-JCS-1（推荐）

`dependencyHashRule = war35-dep-jcs8785-sha256/1`；对每个 Check 固定如下明确的依赖范围及可复现闭包：

- **target**：`targetRefs` 的真实对象及被检查字段值（不是仅其 ID）。
- **transitive dependencies**：对应 Story Basis 来源内容 hash（不是仅文件定位）、facts/constraints、依赖 Action/StateDelta/Blocking 等引用值及指定路径，直到全部引用闭包解析完成；缺/无法解析时返回 unresolved 而不是伪造 digest。
- **collection dependencies**：检查如依赖“全部 Beat/镜头是否覆盖叙事任务”，须通过 `collectionPaths` 明确纳入选定数组的成员**身份、相关字段值和顺序**。未列出集合则不得声称检查过集合完整性。
- **check specification**：`checkSpec`、不可变 `checkSpecVersion`、`method`、`targetRefs`、`dependencyRefs`、`collectionPaths`、`planId`、`sceneId`、依赖范围算法 Profile 都纳入依赖指纹。target/依赖引用一律解析到内容，不仅哈希标签；字段路径必须用明确版本的规范 JSON Pointer。
- **fallback**：无法证明完整依赖闭包时，保守依赖整 Plan（会令新修订需要复检），绝不依靠“只比较 ID”“仅比较 source hash”自动复用旧 pass。
- 对 `method=media` 的 Check，额外绑定不可变 `executionTarget` 与 `evidenceRefs` 的内容指纹、对应生成条件/适用范围。**Plan 相同不能推断不同成片媒体检查仍适用**。
- 跨修订重新计算 D-JCS-1 指纹，且检查规范相同、原检查结果为 `pass`、适用性仍 valid、目标依赖未变时，才允许 `inheritance = {fromCheckId,intoCheckId,intoTarget,dependencyHashRule,dependencyFingerprintSha256,basis:"unchanged_dependencies"}`；被继承的新 Check 目标是新 Revision，引用原始不可变证据。Result fail/unknown/not_checked、stale 或依赖不完整不能作为 pass 继承。
- `intentA` 若只依赖 Story Basis＋Intent，新增 Shot 通常不会改变 A 的依赖指纹；若 A 审查条件含“所有镜头均可覆盖目标”，必须把镜头集合纳入依赖，新增 Shot 会触发重新检查。这由 checkSpec 决定，不凭阶段名猜测。

### 21.4 Review gate / Decision 的明确继承边界

**示例**：R1 的 Intent A 获批准，R2 只新增 S03，Story Basis + Intent 未改变。

1. R1 Check C-A1 及 Decision D-A1 **保持原 revision/hash 和证据绑定不可变**；用户先前的批准事实不会被覆盖。
2. 根据 C-A1 的 spec/依赖集合，在 R2 重新计算 D-JCS-1。相同且 old Check pass/valid 时，创建 R2 Check C-A2 与 `inheritance(C-A1 → C-A2)`。这只是**检查证据复用**，不是再次测量媒体。
3. 若要对 R2 产生有效 A 门审阅记录，新增 R2 Decision D-A2，`decisionBasis=verified_carry_forward`，`fromDecisionId=D-A1`、`checkIds=[C-A2]`，显式审计该继承。**不要求用户对不变的 A 意图重复人工确认**；但必须逐项核对原 Decision 作用域、rationale、verdict、已接受风险的同版本适用性，不能把条件批准静默升级为无条件批准。无有效来源决定、内容依赖变化、原风险/条件不适用 → 新 Decision 不能自动生成，需升级审阅。
4. R2 的 B 门（完整镜头交付）仍是独立 Decision。只有绑定 R2 且 gate 为 `shotB` 的 `approved` / `conditionally_approved` Decision，才可形成 `revisionControl.approvedPlan={decisionId,gate:"shotB",target}`；**A 门、exception 检查不能冒充已批准 Plan，Plan 批准也不是视频生成授权**。
5. Decision 必须引用目标版本可解析的 Check，Check 可以是原生计算或经有效 inheritance 到目标版本的 Check；acceptedRisks 指向 `{riskId,riskVersionId}` 的不可变风险快照。原始风险记录文字一旦变化，应写新 riskVersion、重检必要条件，不静默改旧批准含义。
6. Review 本身的内容变化不重新计算 Plan hash；但可改变该 Plan 当前**审阅有效性/审批状态**，这是两套正交事实。不能因为 Plan hash 相同就认为 Decision 原样有效。
7. 要便携恢复 Review 历史，源 Check/Decision、risk 的不可变记录及前版 Plan 目标指纹需要保留或可独立解析。仅携带 R2 Plan + 无法核对来源的“继承声明”不足以作审计证明；缺历史时保留 Plan 草稿，Review 状态 unknown/unverified。

### 21.5 WAR-52 design-0.2 的最后一次交叉映射（不改已冻结设计稿）

| WAR-35 公共层 | WAR-52 投影层（design-0.2 现状） | 交叉决定 |
| --- | --- | --- |
| `plan.planId`、`revisionId`、`sceneId` | `plan_ref`、`plan_revision`、`scene_ref` | 不创建第二 identity，映射有明确的前缀剥离规则 |
| `P-JCS-1 hash({contractVersion,plan})` | 必需 `plan_content_sha256` | 未来从真实源 Plan 计算，与投影 SHA 同时绑定 Review；现有 fixture hash 不重新解释 |
| `Action.id` / `action:A-JUMP` | `action_ref` 及 `action_scopes/action_phases` | 源 Action ID 绝对唯一；`action_ref` 不得是第二生成 ID |
| 可选 `Action.phases[].key`，PhaseSpan inclusive | 投影必需 `phase_key`，`span=[start,end)` | 同一 action_ref 下投影局部 phase_key 唯一；**建议后续兼容升级在 action_phase 增加可选 `public_phase_key`**。若公共 phase 存在，投影局部 phase 可一对多映射；若无公共 phase，纯投影 phase 仍合法 |
| `Action.completion.deltaRef` / Shot.coverage.completionDeltaRef | `completion_delta_ref`、`completion_at` | 唯一 Plan Delta，H3 仅加帧锚点。必须验证触发 Action 相同、完成条件相同，跨镜与 Join 不重复 apply |
| `StateDelta.before/after`、`afterDeltaRefs` | `join_constraints.delta_refs`、`state_relation=inherit/explicit_delta` | cut/continuous 与 state_relation 是正交维度；同键 Delta 有可推导顺序，Join delta_refs 只引用 |
| Shot 主要任务/估计时长、观察判据 | `shot_responsibilities/visible_evidence`、精确 FPS/frame_count/span | 估计 ≠ 强制帧数，导演不要求 8s/四镜；转 H3 后要按 WAR-52 执行 profile 验证 |
| StoryBasis alias + sourceHash，主体引用 | Scene anchors、asset_bindings、Reference/Guide、dialogue_cues | Canvas 资源解析是执行适配而非 DirectorPlan 必填；Guide 可缺，若存在但不可用不得静默忽略 |

**现状兼容限制**：WAR-52 `design-0.2` 的 `action_phase` 拒绝未知字段、没有 `public_phase_key`，因此现行投影不能直接序列化 proposed mapping；该需求只归未来 WAR-52 合同版本的**最小兼容扩展**，不能偷偷把字段注入 `design-0.2` 或擅自重写既有已完成证据。若当前投影无映射字段，可用单次投影/联审侧映射清单辅助，但不能声称完整无损交叉验证。新交叉版本需维护升级/回滚路径。
**Review 跨层绑定限制**：现行 WAR-52 使用 Plan+projection 两类版本/内容指纹，但投影 hash profile 未宣称等同 P-JCS-1，未来 `h3-projection-ready` 必须规定独立 `projectionHashRule`，并在 Review 的执行目标绑定 unitRef/revision/projection SHA。此项属于执行审阅目标的扩展，不让公共 Plan 依赖 H3。

### 21.6 收口前的三个小边界（明确说明，不无限扩大模型）

- **Locator 的字段归属**：本轮已在 **WAR-35 未冻结 review draft** 里按推荐 B 将纯解析 `locator` 从 `storyBasis.sources` 移到 Package 级可选 `sourceLocators`，以避免重定位改变 Plan 内容指纹。sourceBinding 保留 `sourceId/contentSha256` 等语义绑定，resolver 必须核对目标来源真实内容。此为待最终审阅的字段候选，非已发布格式；不涉及 WAR-52 设计基线或生产数据迁移。
- **Review 依赖指纹版本化**：Profile 固定以上 D-JCS-1，`collectionPaths` 标识该 Check 的规范列表依赖，不能事后增删来源清单而保持旧指纹；媒体类额外依赖不可变媒体证据，不继承不同成片结果。此为**推荐直接定稿**的技术规范。
- **Phase map 的交付位置**：公共 Plan **不增加必填 phase**；WAR-52 projection 未来增 optional `public_phase_key`，而当前 design-0.2 保持只读冻结。推荐以版本化 H3 契约候选记录映射，正式修改须由后续 WAR-38/适配设计获授权执行。

### 21.7 完成/未完成边界与冻结门槛

- 本节是本轮**设计提议**，C1–C5 及 C6 轻量方向由用户回复授权推进，但 §21.6 locator 精确落点、正式的 hash profile、verified-carry-forward 规则细节与未来 WAR-52 schema 扩展尚待最终审阅，不声称已冻结。
- 冻结 WAR-35 的 schema **仅在** Schema Draft 2020-12 及两份最小正例格式有效、P01–P12 的语义校验规格和必要反例覆盖完整、Plan/Review/Profile 可复算以及 WAR-52 交叉可追溯时进行。完整生产运行时校验器、真实媒体/Guide 生成验证不在 WAR-35 设计冻结的前置条件内；不以等实际产品实现为由无限延期。
- 本轮严禁将 WAR-52 design-0.2 的旧合成 hash 和公共 P-JCS-1 视为同一哈希；也严禁“没有独立 Check 验证，模型声称通过”。

### 21.8 本轮机器可读草案的静态核验与未证项

在 Eric 上仅对 WAR-35 的非冻结 `director-plan.schema.review-v0.json` 作 JSON Schema Draft 2020-12 结构检查（`jsonschema 4.26.0`），结果：

- Schema meta-schema 合法；`no-action-beat.example.review-v0.json` 与 `cross-shot-once.example.review-v0.json` **均通过结构校验**，两份文本快照的 UTF-8 SHA-256 与 source binding 匹配。
- 11 项结构性用例均符合预期：两个正例；一次性 Action 无 completion 被拒绝；不存在的 event ref 被拒绝；Plan source 夹带 locator 被拒绝；Package sourceLocators 被接受；Intent A 冒充 approvedPlan 被拒绝；Shot B pointer 形状被接受；缺来源决定的继承式 A Decision 被拒绝；有来源决定引用的 A Decision 形状被接受；Shot B 决定不得继承式自动通过。
- 这些只是**结构断言**：`approvedPlan` 是否真实指向 ledger 的有效 B Decision、`fromDecisionId` 是否可信、Check 的目标/来源/依赖闭包/风险版本是否合法、Action 只完成一次、H3 真实可见证据，**全部仍由尚未实施的语义检查约束**。合成测试中的哈希值不是实际批准指纹，不得用于执行授权。
- **本轮后续补充（见 §22）**：Eric 已隔离安装 Python `rfc8785` 与两个 Node JCS 库，验证 RFC 8785 选定测试向量及两份完整 Plan payload 的跨语言相同字节与 SHA-256。此结果仅针对 P-JCS-1 示例，不证明 D-JCS-1 依赖闭包、不同执行媒体或正式审批规则已经通过。
- 已尝试在 Eric 运行本轮第三次 Codex 严格只读交叉审阅，CLI 返回 **usage limit**（未执行审阅，process exit 1）；本节交叉判断为 ChatGPT 基于 WAR-35 / WAR-52 文件及静态 schema 的核对，不声称得到第三方 Codex 独立通过报告。此前两轮 Codex 只读报告仍存 §19–20。
- **本轮未改** WAR-52 `design-0.2` 文件、原始 Skill、Canvas、GPU/Blender 或媒体。WAR-35 文档与草案仍在 Eric 项目仓库未提交 Git；待最终设计审阅通过后再冻结/提交。

### 21.9 推进建议（本轮结论，不提前冻结）

1. **公共 WAR-35 设计**：C1–C5 及轻量 C6 已有可审阅的字段和规则候选。**P-JCS-1 的基础三实现交叉测试已通过（§22）**；下一轮短检查集中于 D-JCS-1 依赖闭包的规范序列化/缺源处理，以及 A 门证据转移与新 Decision 的纸面正反例，无须重复部署 JCS。没有新增架构阻塞项。
2. **WAR-52 交叉范围**：已有 source/action/shot/delta 身份映射不冲突。对公共 phase 必需映射的路径，`design-0.2` 不能存新增字段；记为下游版本化映射或 sidecar 的明确缺口。它不要求推翻 WAR-35 的独立 Schema，**但完整的 H3 跨层无损冻结和执行就绪不能据此声称已完成**。
3. **开发阶段分离**：公共契约设计冻结、后续 WAR-36 Shot Planner 设计/编码、WAR-37 Canvas 适配、WAR-38 H3 投影升级是不同验收；不因本轮 JSON 结构通过而自动取消 WAR-35 的现有 blockers 或标为 Done。

## 22. JCS 独立环境与 P-JCS-1 跨语言一致性验证（2026-11-13）

### 22.1 Eric 隔离环境与安装记录

用户明确授权在目标机器建立 JCS 环境。本轮通过 **DCR → Eric** 直接操作，没有使用受额度限制的 Codex。仅在以下用户级目录安装，不修改 Canvas Lab 生产依赖、ComfyUI、原始 Skill、WAR-52 design-0.2、系统级 Python 或项目 package.json：

```text
/home/sean/.local/share/canvas-lab-jcs/
  venv/             # Python 3.12.3，由 uv 建立
  requirements.txt  # rfc8785==0.1.4
  js/
    package.json      # pinned Node dependencies
    package-lock.json
    node_modules/
  verify_js.mjs
  verify_jcs.py
  README.md
```

本机已安装 `uv`，因此无需 `apt`/sudo。直接运行系统 `python3 -m venv` 因缺少 `ensurepip` 失败，之后通过 `uv venv --clear` 成功创建隔离 venv。依赖锁定：

| 环境 | 包与版本 | 作用 |
| --- | --- | --- |
| Python 3.12.3 | `rfc8785==0.1.4` | JCS 规范序列化，返回 bytes |
| Node 24.18.0 | `canonicalize==5.1.0` | 独立 JS 实现，符合 RFC 所引用的生态路线 |
| Node 24.18.0 | `json-canonicalize==3.0.1` | 第二个 JS 实现，比较完全一致的字节 |

复测命令（只作用于研究示例，不启动服务器/GPU）：

```bash
/home/sean/.local/share/canvas-lab-jcs/venv/bin/python /home/sean/.local/share/canvas-lab-jcs/verify_jcs.py
```

本地版本管理证据（SHA-256）：

- 测试脚本 `verify_jcs.py`：`9338b553e0bcaf1e3180f97f1c9cd83ff7e1bc46972a9413c60e18d67ca48d11`。
- JS 比较助手 `verify_js.mjs`：`e6d130ab4097765bed828fc5149c04f2ddd1ed28d7a67b1bd0ee49cf39658ef0`。
- npm `package-lock.json`：`353726ff96e61636873104fff82f00cd32e8161cbc66b1ef0d4753316df2f1ce`。
- **报告**：`docs/planning/WAR-35/jcs-verification.report.json`，SHA-256 `82fbd1315f7a3b7ca1aa127b1ecbbab5548fe48eb2a9a673f68f270ffad92248`。

测试脚本和依赖存在于 Eric 用户级目录，未纳入仓库 Git；项目内报告与本节为可追溯研究记录。不能据此声称已有异机备份或生产可用软件包。

### 22.2 已成功核验的范围

**21/21 组正向用例通过**：Python `rfc8785` 与两个 JS 库对相同 JSON 值生成逐字节一致的 RFC 8785 canonical JSON，三者的 SHA-256 也一致，其中：

- RFC 8785 Appendix B **15 个选定 IEEE-754 金标测试向量**：含正负零、最小正/负浮点数、极大值、2^53 附近及不同科学记数法边界；
- JSON 属性重排、中文/emoji/Unicode 字符串及嵌套对象、数字边缘情况、RFC §3 数字组合；
- WAR-35 两份合成 `DirectorPackage` 按 P-JCS-1 提取 `{contractVersion,plan}` 的完整 Plan 指纹，并与两 JS 库一致。

两份 Plan 内容 SHA-256：

| 示例 | P-JCS-1 完整 Plan 指纹 |
| --- | --- |
| `no-action-beat.example.review-v0.json` | `c15b2272d787862a1366f24391982c25df906375ebf141e17427df2d633e3322` |
| `cross-shot-once.example.review-v0.json` | `0bb91a8f207effbe17756217e92bf9f5311243339b1a0064a6f19554f7c35dbc` |

另验证输入门槛：使用解析前的重复键检查拒绝重复 JSON 属性；Python JCS 库拒绝 NaN、Infinity、不安全超大整数和孤立 surrogate。这些不是说所有运行时的内置 JSON 解析器天然拒绝这些输入，**I-JSON 的入口校验仍是契约实施责任**。

对两份真实草案示例分别确认四种变化：
- 仅改变 JSON 对象属性排列：**Plan 指纹不变**；
- 增加或更改 Package 的 `sourceLocators`：**Plan 指纹不变**；
- 增加外层 `reviewLedger`：**Plan 指纹不变**；
- 实质修改 Beat 文本或 Shot 主要目的：**Plan 指纹变化**；同时验证 sourceSnapshots 的文本 UTF-8 SHA 与 source binding 一致。

这是一次独立运行的研究工具验证，不能被描述为正式生产哈希计算器、WAR-35 完整语义验证器或通过审批的 Plan。也未运行上游官方全量测试语料或跨实体机器验证。

### 22.3 下一步与剩余门槛

- **P-JCS-1 基础跨语言一致性**：已通过 Eric 同机 Python＋Node 三实现的测试，当前不需要再因“没有 JCS 实现”而阻塞 WAR-35 设计讨论。
- **D-JCS-1 Review 依赖指纹**：仍没有规范的依赖闭包 serializable payload、旧 Check→新 Check 及 Decision 的语义测试；这是 WAR-35 设计冻结前的独立待处理事项。
- **WAR-52 phase/publicPhase 映射与 Review 执行目标**：依旧由后续交叉适配版本处理，本轮无修改。
- **Codex 独立复核**：额度在此时仍不可用，如确需 Codex，可在额度恢复后通过新对话做最后只读复核；本次安装/验证完全由 ChatGPT 使用 DCR 执行。

状态：**JCS 工具环境建立并完成首轮可重复验证，公共 Schema 设计尚未冻结。**

## 23. D-JCS-1 冻结前最后修正提案（2026-11-14，待用户确认）

本节只收口独立复核的 Blocking 1，不改 WAR-52、不扩展 DirectorPlan 架构，也不提前处理 Media Check、Decision carry-forward 或 raw I-JSON。目标是让不同实现者对同一 Review Check 必然得到同一依赖指纹，并在任一必要依赖/来源无法完整解析时**没有指纹、不能继承旧 pass**。

### 23.1 推荐契约

D-JCS-1 profile 保持：`war35-dep-jcs8785-sha256/1`。

最终指纹定义为：

```text
dependencyFingerprintSha256 =
  SHA-256( UTF-8( JCS( canonicalDependencyPayload ) ) )
```

唯一 payload 冻结为：

```json
{
  "profile": "war35-dep-jcs8785-sha256/1",
  "contractVersion": "<package.contractVersion>",
  "planIdentity": {
    "planId": "<plan.planId>",
    "sceneId": "<plan.sceneId>"
  },
  "checkSpec": {
    "text": "<check.checkSpec>",
    "version": "<check.checkSpecVersion>",
    "method": "<check.method>"
  },
  "scope": {
    "targetRefs": ["<normalized typed ref>", "..."],
    "dependencyRefs": ["<normalized typed ref seed>", "..."],
    "collectionPaths": ["<normalized JSON Pointer>", "..."]
  },
  "resolvedObjects": [
    {
      "ref": "<typed ref>",
      "value": "<full normalized resolved object>"
    }
  ],
  "collections": [
    {
      "path": "<plan-relative JSON Pointer>",
      "value": "<full value at that path, original semantic order preserved>"
    }
  ]
}
```

关键边界：

1. `targetRefs` 是被检查对象的 typed-ref seeds；`dependencyRefs` 只表示**额外 dependency seeds**，不是“允许实现者漏掉真实依赖的白名单”。为减少 review-draft 改动，v0 建议保留字段名 `dependencyRefs`，但在 Schema description 和规范中明确 seed 语义。
2. 从 `targetRefs ∪ dependencyRefs` 出发，按 v0 Schema 定义的 typed-ref 边递归解析闭包；`collectionPaths` 指向的值也进入 payload，并从其中 schema-defined typed refs 继续扩展闭包。
3. v0 保守处理：每个 resolved typed ref 哈希其**完整 resolved object**，不做字段级裁剪。这样可能导致额外复检，但不会因为依赖裁剪错误而错误继承。
4. `check.target` 的 revision/content hash 不进入 D-JCS payload，否则跨 revision 永远无法继承；目标 revision 仍由 Check 自身独立绑定。D-JCS 通过 `planId + sceneId + actual dependency content` 防止跨 Plan 误复用。
5. `contractVersion` 进入 payload。Schema/契约版本改变时保守失效，不跨版本静默复用旧依赖指纹。

### 23.2 typed-ref resolver 与闭包规则

v0 resolver 只按 Schema 明确定义的引用字段建边，**禁止扫描任意字符串并凭正则猜引用**。typed ref 解析表：

| ref kind | 唯一解析位置 |
| --- | --- |
| `plan:<id>` | 当前 `plan`，且 id 必须等于 `plan.planId` |
| `source:<id>` | `plan.storyBasis.sources[]` 的 `sourceId` |
| `fact:<id>` | `plan.storyBasis.facts[]` |
| `constraint:<id>` | `plan.storyBasis.constraints[]` |
| `subject:<id>` | `plan.storyBasis.subjects[]` |
| `intent:<id>` | `plan.intents[]` |
| `beat:<id>` | `plan.beats[]` |
| `action:<id>` | `plan.actions[]` |
| `delta:<id>` | `plan.state.deltas[]` |
| `blocking:<id>` | `plan.blockings[]` |
| `shot:<id>` | `plan.shots[]` |

递归边仅来自当前 Schema 的明确引用字段：Story constraint/fact/subject 的 `sourceRefs`；Intent `basisRefs`；Beat `intentRefs/actionRefs/deltaRefs/afterBeatRefs`；Action `participantRefs/objectRefs/completion.deltaRef`；State baseline `sourceRefs`；Delta `triggerRef/afterDeltaRefs/provenanceRefs`；Blocking `scopeRefs/spatialBasisRefs`；Shot 的 `intentRefs/beatRefs/blockingRefs`、`visualDesign.subjectRefs`、`actionCoverage[].actionRef/completionDeltaRef`、`boundary.entryDeltaRefs/exitDeltaRefs`。身份字段（例如 `sourceBinding.sourceId`）不是递归边；自由文本、StateValue 内字符串、preconditions 等也不得被猜成引用。

闭包使用 typed ref 作为节点身份，节点最多解析一次；循环引用不会导致无限递归，但其他语义 validator 仍可按 P04/P07 等规则拒绝非法环或冲突。

### 23.3 来源解析与 unresolved

`source:<id>` 属于闭包时，只有同时满足以下条件才算 resolved：

1. sourceBinding 可唯一解析；
2. `contentSha256` 存在；
3. 当前 Package 的 `sourceSnapshots` 或 `sourceLocators`/外部 resolver 能取得实际来源内容；
4. 对实际内容复算 SHA-256 与 sourceBinding 的 `contentSha256` 一致。

locator/snapshot 本身不进入 D-JCS payload；payload 保存的是已经验证过的 sourceBinding 内容指纹。这样来源搬迁不改变依赖指纹，但来源不可取得、哈希不符或 sourceBinding 缺 hash 都属于 unresolved。

任一 seed、递归 ref、collectionPath 或必要 source unresolved 时：

- **不生成 `dependencyFingerprintSha256`**；
- Check 的 `result` 只能为 `unknown` 或 `not_checked`；
- 不得创建针对该 Check 的 inheritance；
- 不得把旧 Check 的 pass 视作当前 revision 的有效 pass。

不使用空字符串、全零 SHA、局部闭包 digest 或“已知部分”的 digest 充当完整 D-JCS-1 指纹。

### 23.4 排序、去重与数组顺序

JCS 本身只规范 object key 顺序，不会重排数组，因此 D-JCS-1 在进入 JCS 前增加唯一的 profile normalization：

- `scope.targetRefs`、`scope.dependencyRefs`、`scope.collectionPaths`：精确字符串去重后升序排序。
- `resolvedObjects`：按 `ref` 升序排列，每个 ref 只出现一次。
- Plan 内**纯 typed-ref 数组**视作无序引用集合：精确字符串去重并升序排序后再放入 resolved object 的 normalized value。该规则适用于上述 resolver 表中的 `*Refs` 数组；单值 `*Ref` 不变。
- 其他数组保留原始顺序。尤其 `plan.beats`、`plan.shots`、Action `phases`、Shot `actionCoverage` 及 `collectionPaths` 指向的叙事/时序数组，均不因 D-JCS 重新排序。
- v0 不尝试判断数组“其实像集合”后再智能排序；没有被明确声明为 typed-ref set 的数组保持原样，以换取保守、可复算的行为。

当前 typed refs 与正式 Plan 字段名均为 ASCII；profile 的排序按字符串 Unicode code point 升序，现有值上与常见 UTF-8/UTF-16 字典序一致。

### 23.5 Schema 最小修改

对 `$defs.check` 建议只做以下最小修正：

1. 从无条件 `required` 中移除 `dependencyFingerprintSha256`。
2. 增加条件约束：`result in [pass, fail]` 时必须存在 `dependencyFingerprintSha256`；若 fingerprint 缺席，则 `result` 只能为 `unknown | not_checked`。
3. `targetRefs`、`dependencyRefs`、`collectionPaths` 增加 `uniqueItems: true`；profile 仍负责 canonical sort。
4. `dependencyRefs` 从“至少一项”改为**允许空数组**。理由：target 的递归闭包本身可能已经完整，额外 dependency seed 不应为了满足 Schema 被伪造。字段仍建议 required，使 canonical scope 总有显式的 `dependencyRefs: []`。
5. descriptions 明确：
   - `targetRefs` = target seeds；
   - `dependencyRefs` = additional seeds, never an allowlist；
   - `collectionPaths` = plan-relative RFC 6901 JSON Pointers，其指向值的成员与原始顺序属于依赖；
   - `dependencyFingerprintSha256` 只表示**完整 resolved closure**的 D-JCS-1 指纹。
6. `$defs.inheritance` 形状暂不扩展；它已经强制 fingerprint。语义 validator 再机械要求 source Check 与 into Check 的完整 D-JCS-1 指纹一致、旧 Check=pass/valid、当前 Check 可解析且无 stale。

不增加 `resolutionStatus`、字段级 dependency path DSL、Event Registry 或第二套审批树。

### 23.6 冻结正反例

冻结 D-JCS-1 至少需要以下机械用例：

| ID | 变化 | 预期 |
| --- | --- | --- |
| D-P01 | 仅交换 `targetRefs/dependencyRefs/collectionPaths` 输入顺序 | 指纹相同 |
| D-P02 | 仅交换 resolved object 内纯 typed-ref 数组顺序/重复同一 ref | 规范化后指纹相同 |
| D-P03 | Intent A 的 target 为 Intent，R2 只新增未进入 closure/collection 的 Shot | A 的 D-JCS 指纹相同，可继续检查 inheritance 条件 |
| D-N01 | `dependencyRefs=[]`，但 Intent.basisRefs → Fact → Source；修改 Fact 内容 | 即使未手填 Fact seed，递归闭包使指纹变化 |
| D-N02 | 任一 seed/ref 找不到、source 缺 `contentSha256`、来源内容不可解析或 SHA 不匹配 | 不生成 fingerprint；result 只能 unknown/not_checked；禁止 inheritance |
| D-N03 | target/resolved Action/Blocking/Shot 的任一完整对象字段改变 | 指纹变化（v0 保守失效） |
| D-N04 | `collectionPaths=["/shots"]`，新增、删除、重排 Shot | 指纹变化；叙事顺序不得排序抹平 |
| D-N05 | 只比较 ID 或只哈希手写 `dependencyRefs`，导致遗漏 target 的递归 basis/source | 实现不符合 D-JCS-1 |

### 23.7 设计权衡与本轮建议

**推荐采用以上方案。**它有意选择“可能多复检、绝不错误继承”的 v0 行为：

- 代价：完整 resolved object 会让某些无关字段变化也触发复检；plan/ref resolver 必须知道 Schema 的 typed-ref 边。
- 收益：payload 唯一、跨实现可复算；不需要字段级依赖 DSL；不会因为人工 `dependencyRefs` 漏写而错误保留 pass；unresolved 状态无法被一个占位 SHA 伪装。
- 不在 v0 做的优化：字段级 selective hashing、自动最小依赖推导、跨 contractVersion 兼容继承。等真实复检成本出现后再版本化 D-JCS profile，而不是现在扩大模型。

**用户已于 2026-11-14 确认本节整体方案并授权纳入 Git。** 本节设计取舍已确认；D-JCS-1 研究验证完成，**不等于 WAR-35 整体 Schema 已冻结**。后续进入 Blocking 2 Media Check。

### 23.8 落地记录、验证范围及可复现入口（2026-11-14）

**修改点**：在 `director-plan.schema.review-v0.json` 的 `$defs.check` 精确完成：`dependencyFingerprintSha256` 从无条件 required 中移除，`pass/fail` 分支条件必需；`unknown/not_checked` 允许无指纹；`dependencyRefs` 保留 required 但移除 `minItems:1`，明确为空时仍执行 target closure；`targetRefs/dependencyRefs/collectionPaths` 加 `uniqueItems:true` 与说明文字。未改动 Plan、Action、StateDelta、Shot、Review Decision 等模型结构。

**研究性可复算脚本**（均置于本目录，不进入生产依赖）：

- `verify-d-jcs1.py`：使用 Eric 隔离 JCS 环境的 `rfc8785`，实际组装 §23.1 payload、递归解析 Schema 明确 typed refs、保守归一化集合及完整对象、验证内联来源 SHA；必要引用无法解析时返回无指纹。14/14 通过。该 verifier 只支持 package 内联文本快照；`sourceLocators`/外部 resolver、asset 源与运行时 inheritance 审批校验仍未实现，不能称生产 validator。
- `verify-d-jcs1-schema.py`：使用 Eric 现有 `jsonschema` 环境执行 Draft 2020-12 meta 校验、原有两份合成示例及 7 项 `Check` 分支/去重门槛测试。9/9 通过。
- `d-jcs1-verification.report.json`、`d-jcs1-schema-verification.report.json`：可重复验证结果与基线指纹；是**研究性验证证据**，不是批准或媒体 pass 记录。两份旧合成示例保持原始输入，不为增加新功能而改写证据。

复测命令：

```bash
cd /home/sean/projects/canvas-lab
/home/sean/.local/share/canvas-lab-jcs/venv/bin/python docs/planning/WAR-35/verify-d-jcs1.py
python3 docs/planning/WAR-35/verify-d-jcs1-schema.py
```

**重要限度**：本轮验证是同一 Eric 机器的研究脚本测试；尚未证明独立实现者跨语言复算 D-JCS-1、外部来源 resolver、媒体 executionTarget/evidenceBindings、Decision 单调性或 raw I-JSON 前置验收。上述三类后续公共 Blocking 应依序独立收口。WAR-52 design-0.2、Skill、生产代码和 GPU 均未修改。

**Git 记录**：本轮只暂存并提交 `docs/planning/WAR-35/` 文件；当前仓库其他未提交改动保留原状。正式 WAR-35 v0 冻结时应再次切换 `contractVersion` 并重算最终 Golden。

# WAR-52｜单次 H3 内部连续性契约候选 v0

2026-11-13。状态：**第三轮：五项语义已由用户确认，已产出 draft-0.1 JSON Schema；字段格式仍为设计草案，未接入应用或运行模型。** 第 12 节是当前契约入口，之前轮次的待审阅措辞按第 12 节确认范围解释。

本轮按 WAR-52 开始执行指令开展设计。唯一详细正文为本文件；Linear 保存状态和入口。工作基于 Canvas Lab `0523ef0e924530b5a27b1b85653a85faeaf36893`，但 WAR-35 方案和若干实验依据是当前未提交文件，不能视作该 commit 已包含。未修改应用、原始 Skill、Gateway、工作流或其他任务文件。

## 1. 目标、依据及未决项

定义一个**单场景、一次 H3 直出视频**内 Action 阶段、Shot 表现和相邻 Join 的规划关系。契约能排除自相矛盾的计划，不能保证 H3 实际遵循计划。8 秒四镜只是示例，不是 Scene 时长上限；12–15 秒是 WAR-35 提及的适配目标，仍需执行能力核验。

必读对齐依据：

- [WAR-35 当前设计](../WAR-35/director-plan-contract-proposal-v0.md)，第 1–6、9–16 节：独立 DirectorPlan、共享 Action/Shot ID、baseline + deltas + boundary checks、Plan revision、分级审阅。第二轮核对文件 SHA-256 `0eb0a692ef4171b4c5d2e9d8e903634f44bda4d04415327ad5f2b7931fbf151f`（未提交快照）。第 14–16 节 Beat/Action、Blocking、Shot 字段仍是候选，本提案不替它们作决定。
- [WAR-33 复用 ADR 初稿](../XIA-33-skill-reuse-adr-draft.md)：只作为历史候选，不将旧续接建议作为现行范围。
- [现有候选 Prompt 方法](../../validation/XIA-53-independent-guides/prompt-method-candidate-v1.md)：每镜唯一职责、Guide 与文本 Reference 分工、人工 QC 边界；这是历史方法提案，不是本轮媒体结果。
- [官方 Multiframe 实验记录](../../validation/XIA-53-official-multiframe/README.md)与同目录 `official-multiframe-api.proposed.json`：本轮回读冻结 API 图，确认三个 AddGuide 节点只表达帧锚点，且图片 2–4 未同时进入 `ref_images`。不由该图推断当前服务已支持所有参数。
- [冻结 DirectorSKILL Continuity Bible](../../validation/XIA-33-actual-skill-comparison/director-skill-upstream/references/continuity-bible.md)：借鉴轴线、持物、目光、起止状态等维度，不复制整套实体库。

WAR-33 仍 In Progress，最终复用决策和动态强度能力未收口；WAR-35 仍在字段讨论。可以产出本候选，不能因此解除 blocker 或冻结交叉 Schema。无需为设计稿生成新视频。

## 2. 归属：共享身份，单向执行投影

DirectorPlan 拥有 scene / subject / action / shot / stateDelta 的语义身份及事实来源。WAR-52 的 projection 只引用固定 `planRef + planRevision`，细化一个 execution unit 内的阶段覆盖、帧区间和边界检查。不能把投影中的局部描述回写为已批准故事事实。

| 候选信息 | WAR-52 的职责 | 不重复维护的内容 |
| --- | --- | --- |
| source binding | planRef、planRevision、sceneRef、unitRef、sceneStart；contractVersion | 不生成另一套 Action/Shot ID，不要求 Canvas projectId |
| scene_anchor | 引用源 Plan 的空间、光线、声场约束；必要执行解释单列 assumption | 不复制完整场景实体库 |
| characters / props | 使用源主体 refs；角色、道具或身份资产绑定可选 | 不另建人物数据库；无资产也能做纯文本规划 |
| continuity_axes | 需要检查的状态键、轴线、屏幕方向/眼线与依据 refs | 世界方向、屏幕方向、角色知情、观众可读性分开 |
| action_phases | actionRef、phaseKey、顺序、unit 帧区间、预期完成标记 | Action 定义与实际完成证据留在源 Plan / Review |
| shot_responsibilities | shotRef、unit 帧区间、主要叙事职责、摄影投影、phase refs、边界 refs、可见证据判据 | 可承担多个任务；同一动作被两个 Shot 引用不代表发生两次 |
| guide_points | frame_idx、外部资产绑定、语义目标、参考接线和预检结果 | 不默认启用，不内嵌图片/音频，不编造强度接口 |
| dialogue_cues | 稳定 cueRef、speakerRef、精确文本、unit 时间、画内/画外 | 一句跨切点只是一条 cue，不按 Shot 重复存台词 |
| join_constraints | 邻镜、边界帧、应继承状态、允许的摄影变化 | 不是上一个视频的 latent/video continuation |
| review binding | 所检查 projection/Plan revision、方法、范围、证据、结果 | 计划有效、用户批准、生成成功、媒体通过分别记录 |

资产 binding 可由 Canvas 适配层提供 assetId/nodeId/storageKey，也可由独立 Skill 的外部文件引用提供。它们不能替代语义 subject/action/shot ID。两个 JSON 示例使用嵌入的 `source_fixture` 便于独立纸面走查；这是示意上游输入，不是第二个生产 registry。

## 3. 时间、阶段与完成语义

- unit 用有理数 fps（num/den）与 `frame_count`，帧从 0 起。覆盖区间统一半开 `[start,end)`；最后 end 可以等于 frame_count，Guide 点必须 `< frame_count`。
- sceneStart 用场景相对秒数；`sceneTime = sceneStart + frame * den / num`。场景时间与 unit 帧数不混写，编译时记录取整误差；改变 fps/frame_count 会使所有派生时点和 Review 过期。
- 阶段是**预期动作执行**，Shot 是覆盖。一个阶段可跨切点；用相同 phaseRef 的不同子区间覆盖，不产生第二次动作。phase ID 仅在 actionRef 内部有意义。
- 一次性动作在同一规划版本中**至多一个**预期 completion marker。只有此 unit 承诺完整完成动作时才要求一个，标记落在完成阶段区间内部；未完成或仅覆盖中间阶段不能伪造标记。示例在落地已稳定的帧标完成，不把“镜头结束”自动当动作完成。不同 unit 的投影也不能再次登记同一动作的完成，跨 unit 查重留给 Plan 级检查，本任务不实现视频续接。
- 允许阶段仅部分可见，但必须显式标记 coverage 和未显示的因果风险；不自动补一个“已完成”。本轮狐狸例要求所有必要阶段可见。
- 多个独立动作可时间重叠；有前置/先后约束的阶段必须满足约束。不能用全场景全局单调阶段号禁止所有并行动作。单位边界前已开始的动作需要源 checkpoint 和 phase offset；缺失时标 unresolved，不自动重开 prepare。当前 JSON 只演示完整动作。
- baseline + 单份 deltas 推导期望状态，边界只引用所需 checkpoint/key；缓存是派生值，不逐镜复制全量角色状态。source 未决或缺失时返回 unknown/unresolved。

## 4. Join 的候选表示与边界检查

建议把两个维度分开：`visual_transition = continuous | cut` 描述影像表达；`state_relation = inherit | explicit_delta` 描述世界/动作状态。**cut 不重置动作，continuous 也不代表动作停止。** 这是候选语义，不替 WAR-35 冻结 enum。

单场景 unit 的 new_scene 应拒绝或转交上游重新划分 unit；本任务不实现跨场景续接。跳时只能显式引用已获准的状态变化及省略覆盖风险，不可凭镜头切换让角色瞬移。本轮两个示例都使用 cut + inherit。

在边界 b，比较左镜覆盖结束前与右镜覆盖开始后的期望状态：

1. 同一 unit 的相邻 Shot 必须指向同一边界 b。边界继承由同一状态链推导，不将 b-1 与 b 的相机画面强制像素相等。
2. 角色/道具身份、位置拓扑、持物手、动作已完成标记按声明保持；自然运动可由跨边界的同一 phase 连续推进，不要求姿态冻结。
3. 变更只有在源 Plan deltas 或明确允许的摄影变化内合法。状态键未知不当作 match；显式硬冲突为 fail。
4. 轴线侧、机位/景别、屏幕运动方向与世界坐标分别检查。反打可换景别与观察方向，但必须满足已声明轴线和眼线关系。
5. dialogue cue 可跨切点，保持 speaker 和文本身份；画内/画外按 cue 的可见区间划分。画外不等于静音，也不等于人物换人。

## 5. Guide / Reference / Dialogue 的能力边界

Guide 默认为空。只有用户对特定时点的姿态/构图有要求，且参考语义与该时点的状态兼容时，才提出 Guide。角色参考不自动充当起始姿态或场景布局约束。

每条 Guide 设计信息至少包括 `frame_idx`、mediaKind（image/video/audio）、外部 assetRef、目标 state/shot refs、语义 QA、是否也接文本 ref_images。**image/video/audio 是候选规划类别，不承诺当前 Gateway 全支持。** 编译前必须查询并冻结实际节点版本/输入能力；多帧长度、负索引及音视频长度规则由所选适配器核验，不在公共契约固化历史节点的特有限制。v0 对外只用非负绝对帧，避免负索引随片长改变语义。

若 Prompt 出现 `<Picture N>`，必须在实际文本编码器 Reference manifest 中解析到图片槽 N-1 和正确内容；仅接 AddGuide 不满足这个检查。同一图片双输入是两条用途明确的绑定，不复制权重或资产文件。没有实际绑定时不能把 Guide 图伪称为 Picture。Guide 资产未决或 QA 冲突禁止编译为执行请求。

本候选不设置 strength/weight/start_percent/end_percent 的默认值。历史 WAR-33 源码检查报告原生 AddGuide 无这些输入，本轮不实时核对 ComfyUI 服务，也不把其缺省理解成“强度=1”。以后验证支持的扩展需要 capability/version/evidence 后才能进入适配层。

对白保留 speakerRef、原句和时间；H3 `<d>` 等语法由既有官方规则/薄编译层负责，不在本任务重写 Prompt Writer。文本规划只能发现 speaker/时序/重复文本标记冲突；是否说对、声音是否串人、口型同步、语速是否可完成需完整播放和听审。

## 6. TypeScript 形状草案（非最终 Schema，无运行时接入）

以下是首轮讨论用历史形状（含 camelCase 命名），不与最新 Schema 并列维护。第三轮机器可读字段以 [draft-0.1 JSON Schema](h3-projection.schema.draft.json) 为唯一格式草案；后续若生成 TS，应从该 Schema 派生。

```ts
type Ref = string; // 由固定 Plan revision 的 resolver 解析；不指定生产 ID 格式
type Span = { start: number; end: number }; // integer, half-open; cross-field check
type Phase = { actionRef: Ref; phaseKey: string; span: Span;
  completionAt?: number }; // 单次 Action 至多一个；本 unit 承诺完成时才必需
type Coverage = { actionRef: Ref; phaseKey: string; span: Span };
type Boundary = { stateDeltaRefs: Ref[]; requiredKeys: string[] };
type ShotProjection = { shotRef: Ref; span: Span; responsibility: string;
  camera: { framing: string; axisSide: string }; covers: Coverage[];
  entry: Boundary; exit: Boundary; visibleEvidence: string[] };
type Join = { fromShotRef: Ref; toShotRef: Ref; atFrame: number;
  visualTransition: 'continuous' | 'cut';
  stateRelation: 'inherit' | 'explicit_delta';
  deltaRefs: Ref[]; preserveKeys: string[]; allowedCameraChanges: string[] };
type DialogueCue = { cueRef: Ref; speakerRef: Ref; text: string; span: Span;
  presentation: { span: Span; visibility: 'onscreen' | 'offscreen' }[] };
type H3ProjectionCandidate = {
  contractVersion: 'proposal-0'; projectionRevision: string;
  planRef: Ref; planRevision: string;
  sceneRef: Ref; unitRef: Ref; sceneStart: number;
  fps: { num: number; den: number }; frameCount: number;
  sceneAnchorRefs: Ref[]; characterRefs: Ref[]; propRefs: Ref[];
  continuityAxes: { key: string; constraintRef: Ref }[];
  actionPhases: Phase[]; shots: ShotProjection[]; joins: Join[];
  dialogueCues: DialogueCue[];
  // Guide 字段待实际 adapter 能力交叉评审；不可接受任意 provider 参数透传
  guidePoints: { frame_idx: number; assetRef: Ref;
    mediaKind: 'image' | 'video' | 'audio'; targetRefs: Ref[];
    textReference: false | { pictureIndex: number };
    qa: 'pending' | 'pass' | 'conflict' }[];
};
```

这是必要语义走查；JSON 示例使用 snake_case 以便阅读，最终字段命名/required/optional 和正式 Schema 均留 WAR-35 联审。Schema 负责形状/枚举/整数，resolver 和 semantic checks 负责跨引用、状态推导与时间关系，不能把 JSON Schema 通过当成全部检查通过。

## 7. 两份实例与机器/媒体不变量

- [狐狸 8 秒四镜 JSON](fox-once.example.json)：同一 A-JUMP，prepare / takeoff / airborne / land 四阶段；完成帧 160 一次；Shot 1 还展示走近。airborne 横跨 S3→S4 的 frame 132 切点，验证切镜不重启动作。
- [双人 A→B→A JSON](dialogue-aba.example.json)：A 始终右手持杯，三个 cue；A 的第一句跨 frame 56 的反打边界继续，B 在 frame 56–64 只听不说，B 台词从 68 起。示意对白/时长为本轮设计，不是冻结 H3 样本或媒体听审结果。

| 不变量 | 可机器检查的计划信息 | 必须由媒体证据判断 |
| --- | --- | --- |
| 引用/版本 | 所有语义引用指向所绑定 Plan revision，缺失/stale 阻止无条件批准 | 模型是否保持同一人/物 |
| 时间覆盖 | Shot 完整分割 [0,N)，阶段/台词/Guide 在界内，邻镜边界一致 | 实际切点、混剪/溶解、动作自然度 |
| 一次完成 | 单次 actionRef 至多一枚 completion marker；完整交付动作必须一枚，阶段顺序和先决状态合法 | 实际是否真的跳一次、漏跳或重跳 |
| 边界连续 | baseline+deltas 无冲突、所需状态已知、显式变化有来源 | 姿态、持物手、空间、轴线视觉连续 |
| 台词与知识 | cue speaker/text 不被切点复制，source 硬知情约束未改变 | 台词正确、声音/口型、观众是否理解 |
| Reference/Guide | 图片标签与 manifest 对应，Guide 目标无已知语义冲突 | 锚点符合度、Guide 是否削弱切点 |

机器检查结果 pass / fail / unknown / stale；unknown 不能伪装 pass。已知硬冲突需修复；无冲突但视觉风险未证，可按 WAR-35 分级审阅有条件批准规划，Review 明示风险；这不授权生成。

## 8. Failure / Repair（计划修订与成片问题分开）

| 失败输入/观察 | 检出层 | 最小修复提案与复检范围 |
| --- | --- | --- |
| S4 再添加 A-JUMP takeoff 或第二 completion | 计划 semantic check；实际重跳仍需审片 | 保留同一 A-JUMP，移除重启；复检阶段覆盖、S3→S4、终态，不改故事为“两跳” |
| airborne 缺失，prepare 直接变 landed | 必要 phase/前置检查 | 恢复缺失阶段及展示预算；复检动作因果与所有受影响时点，不自动填“已完成” |
| 切后 A 的杯子从右手变左手，无 transfer delta | 状态键冲突或媒体 QC | 保持右手约束，局部修订参考/描述；确需换手须上游批准动作变化，复检相邻镜 |
| 狐狸落地 Guide 在近岸而非远岸 | Guide 语义 QA | 拒绝该素材或提出更换；复检 asset 内容指纹、目标阶段和 Picture manifest，不运行生成来掩盖冲突 |
| 反打跨轴，A/B 屏幕关系无解释翻转 | 机位约束检查；图像效果需审片 | 调整机位保持同侧；若有意跨轴，提请叙事/空间约束审阅，复检相邻眼线 |
| A 跨切点的一句在 B 镜重新说一遍 | cue ID/时间重复检查；音频需听审 | 保留一条 cue 和画内/画外分段，复检声画与 B 开口时间；不删改精确台词 |
| Prompt 写 Picture 2，但仅接 AddGuide | 编译 manifest 检查 | 删除不需要的标签或显式绑定文本 Reference；复检编号与内容，不推断“Guide 已经让编码器看见” |
| 改 fps/片长却沿用旧 frame_idx 与检查结果 | version/依赖检查 | 重新投影时点、标 stale、产生 Diff；仅复检受影响对象，不覆盖批准基线 |
| 生成接口 success，被标为 action/对白全部 pass | Review 证据范围检查 | 分开 pipeline success 与媒体未知；安排逐帧/全片听审后记录实际结果 |

**最小返修不是局部视频重生成承诺。** 本任务仅提议修改计划、Prompt 或参考；单次 H3 再生成可能改变整段。未经后续实验不能声称可无损替换某一 Shot。

## 9. WAR-35 兼容、迁移与回滚提案

1. 共享语义 resolver 从固定 Plan revision 取得 subject/action/shot/delta；projection 只加执行信息。未采纳候选决策（如是否独立 Event Registry）不在本任务提前固化；必要 stateDeltaRefs 足以表达本轮例子。
2. 保留源 Shot/Action ID，scene time 到 unit frame 的映射显式保存。一个 Scene 可映射多个 unit，但这里只校验一个 unit 内部，不实现 unit 之间的视频续接。
3. 无正式迁移实施。未来遇到仅有 Shot 文本的旧计划，应导入为候选，保留原文/来源；动作身份、阶段和终态无法可靠提取时标 unresolved，不能按相同动词自动合并，也不能自动认定重复跳跃。
4. 未来 Canvas 适配：Plan 仍独立；CanvasProject 的类型化承载与 asset/node 绑定按 WAR-35 设计。当前 CodeGraph 核对到既有导出仍使用 Canvas export v3，`exportCanvasProjects` 收集 storageKey 并封装 projects/files；不能声称它已持久化或理解本候选 projection。新字段保留/重绑/import-export 需要独立实施和测试。
5. 不复制 Canvas graph、connections、资产内容、生成 job/task、提示词优化器、H3 权重或导演 Skill。Guide 接线属于将来 Gateway 薄适配，当前不新增工作流。
6. 回滚以 Plan 级 approved revision 与候选 Diff 为单位，恢复旧批准指针和对应 projection；新证据保留但标明 target revision。不删除原始证据，不让新候选覆盖批准基线。因本轮无应用接入，当前回退只需不采纳本设计文件。

后续实施时的必要验证：导入/导出/复制后的引用与资产内容不漂移；scene↔unit 时间映射误差；动作跨镜、跨切点台词；旧版本拒绝未知必需字段而不静默丢弃；候选回滚恢复批准快照。测试建议不等于已运行。

## 10. 本轮检查及下一步

本轮只做本地文档和 JSON 结构/语义走查；没有加载模型、调用 ComfyUI、生成视频或回放历史媒体。

2026-11-13 离线检查记录：两份 JSON 均可解析；一次性脚本对 source fixture 引用、Shot 分割、phase 顺序与子区间覆盖、单次 completion、delta before/after、Join 边界及 cue 展示分段进行断言，两个正例通过。七个内存中变异例均被拒绝：重复 completion、缺少 airborne、Shot 时间缺口、悬空 actionRef、Join 时点不一致、重复 cue、对白展示区间缺口。脚本未作为生产校验器交付，未声称穷尽所有状态和 Guide 能力检查。`git diff --check` 对本轮路径无空白错误；新增文件另在暂存后检查。

下一步供 WAR-35 联审的具体取舍：

1. 接受 visual transition 与 state relation 分离，还是保留单一 Join 枚举但额外约束？推荐分离，避免把 cut 当状态重置。
2. 确认 completion marker 属于预期事件，单次动作至多一次；本 unit 承诺完整完成时才必须存在。实际完成另归 Review。
3. 确认 Guide 非必填、文本 Reference manifest 独立、未验证参数不进入公共 Schema。

以上是可审阅候选，不是用户已批准决定。WAR-52 保持 In Progress，WAR-33/35 依赖不解除；正式 Schema、运行时校验器、Canvas/Gateway 接入与 GPU 验证均未交付。

## 11. 第二轮｜与 WAR-35 的字段交叉评审

本轮依据用户“开始下一步”继续设计对齐，不将这句执行指令解释为批准所有候选字段。未写 WAR-35 文件。核对其第 15–16 节新增的 Blocking / Shot 方案后，修正主要职责与部分动作完成边界；第 6 节 TS 和 JSON 仍是候选形状，以下补充为下一版 Schema 的输入，不是生产约束。

### 11.1 交叉结论与字段级建议

“必需”在下表中仅为建议，区分**可审阅候选**和**可交给 H3 编译的投影**。允许草案缺信息，但必须带 unresolved，不能伪装可执行。

| 信息 | 可审阅候选 | 执行投影前建议要求 | 权威归属与变化影响 |
| --- | --- | --- | --- |
| plan / scene / action / shot refs | 场景与来源可定位；缺对象显式列出 | 引用全部解析到固定 Plan revision | WAR-35；对象失联或版本变化令依赖检查 stale |
| projection revision | 保存候选自己的修订，区别于 schemaVersion / Plan revision | 精确绑定被批准的投影修订及内容指纹 | WAR-52；改切点也会改变投影，不能继续引用旧媒体 Review |
| unit 时间映射 | 可标预计帧率、片长/区间待定 | 正有理 fps、frame_count、sceneStart 与明确取整规则 | WAR-52；源 Shot 允许估计时长，不反向要求导演先写精确帧 |
| shot responsibility | 主要任务必须清楚，可列次要任务 | 投影保持上游 narrativePurpose 和关键 evidence criteria | WAR-35 的 Shot；不把“唯一动作实例”误写为“每镜只能有一个任务” |
| 摄影与空间 | 可用相对拓扑、观察条件、未证假设 | 所选模式实际要求的摄影/轴线约束足够明确 | Blocking 提供空间条件，Shot 决定摄影；不强迫所有镜头写 XYZ/焦距 |
| action phases | 仅细化需要跨镜或检查的关键动作 | 参与投影的阶段顺序、覆盖、必要前置可检查 | 复用 actionRef；静态情绪镜头不硬造 Action，是否无 Action 的 Beat 仍由 WAR-35 决定 |
| 完成状态 | 显示 complete-in-unit / partial / unresolved 的语义 | complete-in-unit 必须一枚，partial 至多一枚且不得伪称完整交付 | 完成条件/StateDelta 属于 Plan；投影的 completionAt 只是该事件的执行时点 |
| 边界状态 | 引用必要状态键/检查点，未知显式列出 | 硬性继承键已知且不冲突；视觉未知可进入风险评审 | 同一 baseline + deltas；不用每镜快照覆盖源事实 |
| Join | 有邻镜、表达意图与需保持状态 | 固定 atFrame、视觉方式、状态关系和变化依据 | WAR-52；切镜不能另建 Action，也不能洗掉持物/知情约束 |
| dialogue cues | speaker + 精确原句可定位；时点可待定 | cue 时间/画内外覆盖无缺口，speaker/text 解析有效 | 若源已有说话 Action，cue 引用该 actionRef；不新建平行语义身份。无源 ID 时保留未绑定候选 |
| Reference binding | 无图也可规划；需图时允许 pending | 使用 Picture 的每个槽有可解析外部资产和内容指纹 | 独立 Reference manifest；资产 ID 本身不能证明内容没变 |
| Guide | 可完全不提供；提供时标 QA/能力未知 | 仅所选模式支持、素材语义通过、时间合法的 Guide 才能编译 | 薄适配；不把候选 assetRef 当已存在素材或授权生成 |
| Review / 批准 | 保留 check result、方法、范围和风险 | 绑定 Plan revision + projection revision；硬冲突未解不得无条件批准 | 延用 WAR-35 横切 Review，不在投影再建一套审核系统 |

两个 JSON 增加 `projection_revision` 区分执行时点调整与源 Plan 修订。新增信息不代表 Schema 已冻结；`source_fixture` 始终是合成的上游片段，没有伪造批准记录。对话例未绑定真实说话 Action，其 cueRef 是投影内的 cue 身份，不表示已有完整 Plan 的所有 Action 引用已验收。

### 11.2 Join 的三种走查与精确语义

| 例子 | 视觉 / 状态关系候选 | 应检查的条件 |
| --- | --- | --- |
| 狐狸 frame 132 从追拍切远岸机位 | cut / inherit | 同一 airborne 阶段跨边界；没有第二 takeoff/completion；世界轨迹继续 |
| 对话 frame 56 切 B，但 A 仍说到 frame 64 | cut / inherit | D1 不复制；A 画外声音继续，B 此时听；杯子仍由 A 右手持有 |
| 上游明确允许省略部分动作，切后已到远岸 | cut / explicit_delta | 引用源 Plan 允许的变化、时间省略与覆盖风险；没有依据时 fail，不能用枚举授权瞬移 |

`inherit` 表示**按已有状态链自然推进**，并非所有值恒定。边界处恰好有正常动作 delta（例如 frame 88 起跳结束）仍可 inherit。`explicit_delta` 表示边界存在需额外解释的省略/变化，必须引用源依据；这些变化仍从单份 state delta 流应用一次，不能先按时间流应用、再因 Join 引用重复应用。

边界 checkpoint 统一建议用 `state_at(b)`：先应用逻辑时点不晚于 b 的 delta，再评价该边界条件。JSON 左镜 exit 与右镜 entry 因而可共同引用此 checkpoint。它不等于左镜最后一张画面 b-1 的观察值，也不要求跨切点姿态像素相同。若以后需要明确 before/after，必须分别标 side，不能混用两个约定。

`preserve_keys` 应解释为“沿状态链保持连续的键”，不是“强制相邻快照值相等”；更清楚的字段名建议为 `continuity_keys`，本轮不静默改动既有 JSON 命名。静态文本的 south 等机位侧标记只能检查声明是否一致，不能证明实际画面未跨轴。

### 11.3 一次完成与单份状态权威

Action 的 completion condition 由源 Plan 持有，WAR-52 将它定位到 unit 时帧。若 Plan 已用 StateDelta 表达 `jump.completed: false → true`，completion marker 应引用同一 delta/事件；不能另维护一个可独立改写的 completed 真值。狐狸例的 marker 160 与 D-LAND 的 frame 160 是同一预期完成的两种投影视角。

| 情况 | 标记与边界 | 处理 |
| --- | --- | --- |
| 完整一次跳跃 | 本 unit 一枚 marker，落地条件成立 | 计划可检查；实际完成仍 unknown |
| unit 只覆盖已在进行的腾空 | 使用上游进入状态与阶段偏移，不补 prepare | 无足够源 checkpoint 则 unresolved；不将无 marker 判成漏动作 |
| 结尾仍在腾空 | 不写 landed/completed，不冒充完整交付 | 仅在上游允许 partial 目标时成立；与完整落地目标冲突则 fail |
| 两次独立跳跃 | 上游需两个 actionRef | 不能靠把 once 改成 false 掩盖单次 Action 的重复完成 |

### 11.4 Guide 可选的决策路径

1. 未要求特定锚点、无证据说明必须加 Guide：保持空数组，继续纯文本或已有 Reference 的规划。
2. 需要时点构图：提出候选 Guide，记录 target shot/phase、mediaKind、资产用途和 semantic QA；素材未准备标 pending，规划风险可审阅。
3. 真正编译前：核对所选 adapter 版本能力、实际素材、帧点、编码器 Reference manifest；不支持或冲突则返回明确问题，不丢字段继续提交。
4. 只希望稳定身份：先核对 Reference 的用途，不能自动加姿态 Guide。Guide 同时进文本 Reference 时，两个绑定都引用同一内容指纹。

本轮没有查询实时 ComfyUI，也没有验证音频/短片 Guide 参数；因此能力矩阵不能标成全支持。未提供 Guide 与提供了无效 Guide 是两种不同情况，不能把后者自动降级成无 Guide 后静默生成。

### 11.5 第二轮检查与评审出口

本轮一次性 Python 断言复核通过：两 JSON 可解析、跨切点 phase/cue 连续、D-LAND 与唯一 jump completion 同帧、投影修订独立于源 Plan、无 Guide 路径、media result 保持 unknown；正文相对文件链接均可解析，`git diff --check` 通过。另补充四个纸面边界案例：partial 合法、不完整目标冲突、隐式正常 delta、缺省略依据；这些纸面推演未由运行时校验器执行。没有新增生产代码或自动化测试套件。

本轮提出的三个具体建议：**Join 双维表达；完成标记按完整/部分覆盖区分；Guide 可选但出现时不得静默忽略错误。** 加上“主要职责可带次要任务”“源 Shot 可先用估计时间”，这五项已于第三轮由用户确认，见第 12 节。字段命名、部分覆盖字段和 WAR-35 待决 Action 规则仍需共同形成 Schema。保持 WAR-52 In Progress，不单方面宣布跨层联审通过。

## 12. 第三轮｜已确认语义与 draft-0.1 Schema

用户明确回复“采用上述建议，继续”，确认第 11.5 节的五项语义：Join 双维、完成标记按完整/部分覆盖区分、Guide 可选但无效时不得静默忽略、主要职责可带次要任务、源 Shot 可以先使用估计时间。本轮据此细化格式，不重复请求这些决定。未因此批准 WAR-35 其他待决项、应用实施、GPU 或未知 Guide 能力。

### 12.1 产物与适用层次

- [h3-projection.schema.draft.json](h3-projection.schema.draft.json)：JSON Schema Draft 2020-12，`contract_version = draft-0.1`，**已定时的审阅投影**格式草案。不对尚未精确时点的上游 DirectorPlan 施加此格式。
- 两份既有 `.example.json` 更新为 envelope：`source_fixture` 是合成上游输入，`projection` 才是 Schema 的校验对象，`media_review` 保持 unknown。不能把合成 fixture 当作真实批准 Plan 或资产仓库。旧样例保留在前两轮 Git commit 中。
- 格式不存第二套审批记录；最终 Plan/projection 审批与证据仍交横切 Review。没有实现 resolver、生产 semantic validator、Prompt compiler、运行时门禁或视频提交。

### 12.2 必需、可选和条件必需字段

| 区域 | 此草案必需 | 可选或条件必需 |
| --- | --- | --- |
| 版本与来源 | contract_version、projection_revision、plan_ref、plan_revision、scene_ref、unit_ref | source 内容/指纹最终复用 WAR-35 的绑定；本轮不伪造 source 审批 |
| 时间 | scene_start ≥ 0、正有理 fps、frame_count > 0 | 所有整数帧区间、取整与总长关系另做 semantic check |
| 场景与主体 | 非空 scene_anchor_refs；character_refs、prop_refs、continuity_axes 数组 | 无人物/道具可空；不造全局角色库 |
| 动作 | action_scopes、action_phases 数组 | 无动作时可空；scope 的 entry=already_active 必须有 entry_checkpoint_ref |
| 阶段完成 | phase 的 action_ref、phase_key、span | completion_at 与 completion_delta_ref 成对出现；跨 phase 的唯一性和 complete 必须完成由 semantic check 负责 |
| 镜头 | shot_responsibilities 至少一项；shot_ref、span、responsibility、camera、covers、entry、exit、visible_evidence | secondary_responsibilities 可省；camera 内精确参数不必填；无关键继承键可空列表 |
| Join | join_constraints 数组；邻镜 refs、at_frame、visual_transition、state_relation、delta_refs、continuity_keys、allowed_camera_changes | 一镜无 Join；explicit_delta 要求非空 delta_refs；引用合法性不能靠枚举保证 |
| 对白 | dialogue_cues 数组；cue_ref、speaker_ref、text、span、presentation | cue.action_ref 可选，已有源说话 Action 时应绑定；未核对绑定保持 unresolved |
| Guide | guide_points 可省，省略与空数组都表示没有 Guide | 每项必须 frame_idx、asset_ref、media_kind、target_refs、text_reference、qa；capability_evidence_ref 可在审阅时缺省，执行前必须核实 |
| Reference / 资产 | reference_bindings、asset_bindings 可省 | 出现时绑定 asset_ref、内容 SHA-256 和种类；Picture 索引从 1 起；locator 可省，交宿主 resolver 解析 |
| 开放项 | unresolved 数组，可空 | 非空允许保留候选，不宣称执行就绪；空也不自动证明外部源、素材和 adapter 已核实 |

采用 snake_case 与 JSON 示例一致，`preserve_keys` 改为 `continuity_keys`，明确沿状态链连续而不是快照值必须相等。所有结构对象拒绝未知字段；因此 Guide 的 strength/weight/start_percent/end_percent 不会被作为合法参数悄悄透传。扩展能力应在后续有版本依据时增加，而非开放任意 provider JSON。

### 12.3 Schema 之外的语义规则目录

这些是检查规格，不是“JSON Schema 已执行”的声称：

| 编号 | 必须检查的关系 | 失败/未知的处理 |
| --- | --- | --- |
| S01 | Plan/scene/subject/action/shot/delta 引用、修订与来源可解析；ID 在对应作用域唯一 | 缺引用 unknown/unresolved；硬性错绑 fail |
| S02 | [start,end) 满足 start < end，所有区间/Guide 在 [0,N)；Shot 完整连续分割 [0,N) | 超界、重叠或空隙 fail |
| S03 | Join 与实际相邻 Shot 对应，at_frame 等于双方边界 | 错位或遗漏 fail；不自动插切点 |
| S04 | scope/phase/coverage 使用同一 action_ref；required phase 顺序、前置和覆盖满足源约束 | 少必要阶段、悬空引用、重启 once Action 均 fail |
| S05 | 每 action 至多一个 completion；delivery=complete 必须一个，partial 无标记可合法 | 不为填绿自动添加完成；承诺完整却未完成则 fail |
| S06 | completion_delta_ref 指向同一 Action 的完成变化，时点与完成条件一致 | 不能引用任意无关 delta 冒充完成；外部完成条件缺失时 unknown |
| S07 | already_active 的进入 checkpoint 与源版本、阶段偏移相容 | 缺证据 unknown；不默认为重新 prepare |
| S08 | baseline + deltas 按时序应用一次，before 与当前状态一致；边界采用 state_at(b) | 冲突 fail；Join delta_refs 只引用，不重复 apply |
| S09 | explicit_delta 的省略/跳时确有源授权；continuity_keys 可按状态链推导 | 枚举不能单独允许瞬移；轴线图像仍需媒体核验 |
| S10 | 同一 cue 的展示分段完整覆盖其 span；speaker/text 不因切点复制；说话 Action 如存在则复用 | 结构缺口/已知文本冲突 fail；实际声音和口型 unknown |
| S11 | Reference 的 Picture 槽唯一且解析到 image 资产与内容指纹；Guide 同时作文本 ref 时一致 | 无绑定、错槽、内容漂移阻止编译；纯 Guide 不等于编码器 Reference |
| S12 | Guide 的素材语义、target、时点、实际 adapter 能力/evidence 均有效，qa=pass | pending 保留候选；冲突/能力未知阻止提交，不静默丢 Guide |
| S13 | Plan revision + projection_revision + 输入指纹匹配 Review；未知媒体不写 pass | 时点/素材变化标 applicability=stale，检查结果与版本适用性分开 |

S05 中 partial 的含义是本 unit 不承诺完整动作交付；它可以覆盖动作结束但漏掉开始，因此 partial 有完成标记也不自动矛盾。already_active 的源 checkpoint 和阶段偏移须由 S07 核对，不能只凭字段存在判断合法。动作跨 unit 的唯一完成由 Plan 级 resolver 检查，本任务仍不实现跨视频续接。

**检查状态修正**：按 WAR-35 第 17 节新增候选，result（pass/fail/unknown/not-checked）与 applicability（valid/stale）应分开；前文将 stale 并列在结果中仅为首轮简写。WAR-35 Review 的具体对象结构仍未确认，本 Schema 不先行创建第二套 Review。

### 12.4 草案迁移、测试与剩余门槛

本轮只迁移可编辑合成示例：增加 projection envelope、action_scopes 和 completion_delta_ref，把旧 preserve_keys 改名 continuity_keys，并补走近完成的示意 StateDelta。真实/历史冻结 GPU 输入未修改。不存在已部署生产数据迁移；旧格式应通过显式适配生成候选，未知信息保留 unresolved，禁止静默丢弃。回退可恢复前一 commit 的示例与设计稿；不影响服务或用户资产。

测试使用已存在的 Python jsonschema 4.26.0。Schema 自身通过 Draft 2020-12 meta-validation，两份示例的 projection 格式通过；13 个格式反例均被拒绝（缺版本、未知字段、无效帧率/帧数、非整数帧、错误 Join、显式变化无引用、完成标记缺源、进行中动作缺 checkpoint、无镜头、Guide strength 透传、Picture 0、非法内容 hash）。省略可选数组、pending Guide 的审阅形状及 partial 无 completion 的单项规则均通过。

独立一次性跨字段断言检查了两个合成 fixture 的镜头分割、覆盖、完成 delta、状态链、Join 时点和 cue 分段；8 个**格式合法但语义有错**的变体均被拒绝（重复 completion、complete 缺 completion、完成时点与 delta 不同、Shot 缺口、Join 错时、phase 悬空、cue 重复、cue 分段缺口）。此断言只是本轮设计验证，不证明完整 S01–S13 已实现；外部源 resolver、checkpoint 几何/阶段偏移、真实 Guide 能力/素材及媒体未检查，也未交付生产运行时门禁或新增测试套件。

五项语义已确认，不再列为待决定。后续交付门槛是 WAR-35 正式公共 refs/StateDelta/Review 字段的交叉收口、WAR-33 Guide/复用能力依据，以及本格式草案联审；未完成前不声称正式跨层 Schema 冻结或将 WAR-52 标 Done。接入应用和真实生成分别由后续实施/实验授权决定。

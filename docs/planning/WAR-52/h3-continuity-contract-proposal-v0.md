# WAR-52｜单次 H3 内部连续性契约候选 v0

2026-11-13。状态：**设计提案，待 WAR-35 交叉评审；没有冻结正式 Schema，也没有实施或运行模型。**

本轮按 WAR-52 开始执行指令开展设计。唯一详细正文为本文件；Linear 保存状态和入口。工作基于 Canvas Lab `0523ef0e924530b5a27b1b85653a85faeaf36893`，但 WAR-35 方案和若干实验依据是当前未提交文件，不能视作该 commit 已包含。未修改应用、原始 Skill、Gateway、工作流或其他任务文件。

## 1. 目标、依据及未决项

定义一个**单场景、一次 H3 直出视频**内 Action 阶段、Shot 表现和相邻 Join 的规划关系。契约能排除自相矛盾的计划，不能保证 H3 实际遵循计划。8 秒四镜只是示例，不是 Scene 时长上限；12–15 秒是 WAR-35 提及的适配目标，仍需执行能力核验。

必读对齐依据：

- [WAR-35 当前设计](../WAR-35/director-plan-contract-proposal-v0.md)，第 1–6、9–14 节：独立 DirectorPlan、共享 Action/Shot ID、baseline + deltas + boundary checks、Plan revision、分级审阅。第 14 节的“不独立建 Event Registry”“无 Action 的 Beat”仍是候选，本提案不替它们作决定。
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
| shot_responsibilities | shotRef、unit 帧区间、唯一叙事职责、摄影投影、phase refs、边界 refs、可见证据判据 | 同一动作被两个 Shot 引用不代表发生两次 |
| guide_points | frame_idx、外部资产绑定、语义目标、参考接线和预检结果 | 不默认启用，不内嵌图片/音频，不编造强度接口 |
| dialogue_cues | 稳定 cueRef、speakerRef、精确文本、unit 时间、画内/画外 | 一句跨切点只是一条 cue，不按 Shot 重复存台词 |
| join_constraints | 邻镜、边界帧、应继承状态、允许的摄影变化 | 不是上一个视频的 latent/video continuation |
| review binding | 所检查 projection/Plan revision、方法、范围、证据、结果 | 计划有效、用户批准、生成成功、媒体通过分别记录 |

资产 binding 可由 Canvas 适配层提供 assetId/nodeId/storageKey，也可由独立 Skill 的外部文件引用提供。它们不能替代语义 subject/action/shot ID。两个 JSON 示例使用嵌入的 `source_fixture` 便于独立纸面走查；这是示意上游输入，不是第二个生产 registry。

## 3. 时间、阶段与完成语义

- unit 用有理数 fps（num/den）与 `frame_count`，帧从 0 起。覆盖区间统一半开 `[start,end)`；最后 end 可以等于 frame_count，Guide 点必须 `< frame_count`。
- sceneStart 用场景相对秒数；`sceneTime = sceneStart + frame * den / num`。场景时间与 unit 帧数不混写，编译时记录取整误差；改变 fps/frame_count 会使所有派生时点和 Review 过期。
- 阶段是**预期动作执行**，Shot 是覆盖。一个阶段可跨切点；用相同 phaseRef 的不同子区间覆盖，不产生第二次动作。phase ID 仅在 actionRef 内部有意义。
- 一次性动作有一个预期 completion marker；标记落在完成阶段区间内部。示例在落地已稳定的帧标完成，不把“镜头结束”自动当动作完成。
- 允许阶段仅部分可见，但必须显式标记 coverage 和未显示的因果风险；不自动补一个“已完成”。本轮狐狸例要求所有必要阶段可见。
- 多个独立动作可时间重叠；有前置/先后约束的阶段必须满足约束。不能用全场景全局单调阶段号禁止所有并行动作。
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

```ts
type Ref = string; // 由固定 Plan revision 的 resolver 解析；不指定生产 ID 格式
type Span = { start: number; end: number }; // integer, half-open; cross-field check
type Phase = { actionRef: Ref; phaseKey: string; span: Span;
  completionAt?: number }; // 单次 Action 仅一个；预期，不是观察结果
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
  contractVersion: 'proposal-0'; planRef: Ref; planRevision: string;
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
| 一次完成 | 单次 actionRef 一枚 completion marker，阶段顺序和先决状态合法，Shot 覆盖不重复执行 | 实际是否真的跳一次、漏跳或重跳 |
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
2. 确认 completion marker 属于预期事件，在跨 Shot 覆盖中只引用一次；实际完成另归 Review。
3. 确认 Guide 非必填、文本 Reference manifest 独立、未验证参数不进入公共 Schema。

以上是可审阅候选，不是用户已批准决定。WAR-52 保持 In Progress，WAR-33/35 依赖不解除；正式 Schema、运行时校验器、Canvas/Gateway 接入与 GPU 验证均未交付。

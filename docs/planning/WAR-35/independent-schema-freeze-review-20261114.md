# WAR-35 · DirectorPlan Schema v0 独立冻结前复核

- 任务：WAR-35
- 证据类型：独立只读设计复核
- 执行机器：Eric
- 项目：`/home/sean/projects/canvas-lab`
- 复核时间：2026-11-14（Eric，UTC+08:00）
- 状态：审阅证据；未修改 Schema、WAR-52、生产代码、原始 Skill 或 Linear
- 结论：**Not ready**

## 1. 总体判断

WAR-35 距离冻结已经很近。当前没有发现需要推翻 **独立 DirectorPlan + 横切 Review + 共享 Action/StateDelta + 独立 H3 Projection** 架构的重大问题，也没有发现 WAR-52 会反向阻止公共 Schema 独立冻结。

真正阻止立即冻结的是 **3 个公共层 Blocking 问题**，另有 **1 个 P-JCS 验证缺口**和 **1 个 WAR-52 Cross-layer 缺口**。

其中最重要的是 D-JCS-1：设计意图基本正确，但还没有达到“不同实现者必然算出同一依赖指纹、且依赖缺失时绝不会错误继承”的程度。

WAR-52 当前仍为 Done；本轮核对 `design-0.2` 的文档与 Schema 均与 Git `de755b5` 一致，没有修改其冻结证据。

## 2. 本轮复核输入

重点读取和检查：

- `docs/planning/WAR-35/director-plan-contract-proposal-v0.md`，重点 §18–22
- `docs/planning/WAR-35/director-plan.schema.review-v0.json`
- `docs/planning/WAR-35/no-action-beat.example.review-v0.json`
- `docs/planning/WAR-35/cross-shot-once.example.review-v0.json`
- `docs/planning/WAR-35/jcs-verification.report.json`
- `docs/planning/WAR-52/h3-continuity-contract-proposal-v0.md`，重点 §12–13
- `docs/planning/WAR-52/h3-projection.schema.draft.json`
- Eric 隔离 JCS 环境：`/home/sean/.local/share/canvas-lab-jcs/`

本轮按需执行了最小静态负例检查，不联网、不运行 GPU、不运行 H3。

## 3. 已验证的关键不变量

| 项目 | 独立复核结果 |
| --- | --- |
| DirectorPlan 与 Canvas/资产系统独立 | **成立**。Schema 没有把 CanvasProject、Asset、H3 frame/Guide 变成 Plan 必填前置。 |
| 无 Action Beat | **成立**。正例没有为了“观众认知变化”虚构 Action/StateDelta。 |
| Action 跨 Shot 只执行一次 | **成立**。A-JUMP 只有一份 Action，D-LAND 只有一份共享 StateDelta；两个 Shot 是 coverage，不产生第二 Action。 |
| P-JCS-1 hash 输入范围 | **方向正确**：`{contractVersion, plan}`；Review、revisionControl、sourceSnapshots、sourceLocators 均在外层。 |
| Locator 不影响 Plan 内容 | **成立**。移动 sourceLocators 不改变 P-JCS-1 hash。 |
| Review 不污染 Plan hash | **成立**。Review ledger 改变不会改变 Plan hash。 |
| Plan 实质内容变化改变 hash | **成立**。现有 JCS 实验证明 Beat/Shot 内容变化会改变 digest。 |
| RFC 8785 实现选择 | **成立**。Python rfc8785 + 两个 Node 实现，对 21 组正向数据产生相同 canonical bytes/SHA。 |
| H3 Action/Shot/Delta 身份 | **设计兼容**。WAR-52 不需要创造第二份 Action/StateDelta identity。 |
| H3 completion / Join | **设计兼容**。completion_delta_ref 是对公共 Delta 的帧锚定；Join delta_refs 按设计只引用、不重复 apply。 |

因此，Action/State/Shot 的公共模型本身不是当前阻塞点。

## 4. 关键缺口

### Blocking 1 · D-JCS-1 的规范 payload 与 unresolved 语义尚未闭合

位置：

- `director-plan-contract-proposal-v0.md` §21.3
- `director-plan.schema.review-v0.json` 的 `$defs.check`

两个独立问题：

1. 文档要求“依赖/来源无法解析时不伪造 digest”，但当前 `dependencyFingerprintSha256` 是无条件 required。最小测试中，构造 `result=unknown` 且不提供 digest 会被 Schema 拒绝，这会诱导实现生成部分或占位 fingerprint。
2. `dependencyRefs` 等字段本质上是集合，但 JCS 保留数组顺序。相同依赖集合仅交换顺序，就会得到不同 SHA。本轮已用最小数据复现。

最小修正：

- 冻结唯一的 D-JCS-1 canonical payload。
- `targetRefs`、`dependencyRefs`、`collectionPaths` 这类集合采用规范排序和去重；真正表达语义顺序的 collection 成员保持 Plan 原始顺序。
- v1 建议从 target 与 dependency seeds 出发，递归解析 schema-defined typed refs，并对 resolved object 内容计算闭包；不要只 hash ID。
- 任一必要依赖或来源无法完整解析：**不产生 dependency fingerprint；Check 只能是 unknown/not_checked，禁止 inheritance**。
- 因此 `dependencyFingerprintSha256` 应从无条件 required 改为条件必填。
- `dependencyRefs` 不应被解释为可以漏依赖的人工白名单；更安全的语义是“额外 dependency seeds”。

### Blocking 2 · media Check 的执行目标与媒体证据绑定没有形成强制门槛

位置：

- §21.3
- `$defs.check.executionTarget`
- `$defs.check.evidenceBindings`

失败实例：

本轮构造 `method=media, result=pass`，但完全不提供 `executionTarget` 或 `evidenceBindings`，当前 JSON Schema **0 errors**。

风险：

如果实现遗漏语义检查，不同生成结果/不同媒体可以错误复用旧 media pass。

最小修正：

- `method=media` 且检查结果为 pass/fail 时，`executionTarget` 和非空 `evidenceBindings` 必须存在。
- D-JCS-1 必须绑定 projection target 与实际媒体/证据内容 SHA。
- 若结果依赖特定生成条件，再绑定对应 `conditionSha256`。
- 增加“Plan 相同但媒体 SHA 改变，旧 media Check 不得继承”的冻结反例。

### Blocking 3 · Decision carry-forward 与 approvedPlan 的不可升级规则尚未成为精确不变量

位置：

- §21.4
- `$defs.decision`
- `$defs.risk`
- `$defs.revisionControl`

失败实例：

本轮构造：

- 来源 `D-A1 = rejected`
- 新 `D-A2 = verified_carry_forward + approved`
- `approvedPlan` 指向一个 `shotB + rejected` Decision

当前结构 Schema 全部通过。

这不要求继续扩展数据模型，但必须冻结 semantic validator 的机械规则：

- `verified_carry_forward.fromDecisionId` 必须解析到同一 gate 的有效来源 Decision。
- 来源必须是正向批准状态；不得从 rejected / changes_requested 自动继承。
- carry-forward 不得扩大批准强度，尤其 `conditionally_approved → approved` 不能自动升级。
- accepted risk 的版本不得静默删除、替换或改写；必须重新确认其在新 revision 上仍适用。
- 新 Decision 的 `checkIds` 必须全部解析到新 target 上有效的 Check。
- `approvedPlan` 必须解析到同一 target、gate=shotB、且 verdict 为 approved 或 conditionally_approved 的 Decision。
- 冻结至少四个负例：rejected→approved、conditional→approved、accepted risk 丢失、approvedPlan 指向 rejected B。

## 5. P-JCS-1 独立结论

**RFC 8785 + SHA-256 算法和 hash 输入范围本身可以接受。**

当前 profile：

`war35-plan-jcs8785-sha256/1`

输入：

`{"contractVersion": package.contractVersion, "plan": package.plan}`

这个选择没有发现设计错误。

现有 21 组 Python/Node 三实现测试足以证明“已经形成的合法 JSON value”在所选 JCS 实现中具有基本跨实现一致性。

但现有测试没有完全覆盖 **raw JSON → I-JSON value** 的入口安全。

本轮在 Eric 实测：

- Node `JSON.parse('{"n":9007199254740993}')` 会先变成 `9007199254740992`，之后 JCS 已无法知道原始数值。
- Node/Python 普通 JSON parser 对重复 key 都可能先保留最后一个值，原始重复信息丢失。
- 孤立 surrogate 和 Infinity 能在 canonicalization 阶段被拒绝，但仍应作为输入门槛的一部分。

最小修正：

- hash API 只能接受已经通过 I-JSON 验证的数据模型；或
- raw JSON 必须先经过不会丢失 duplicate key / unsafe number 信息的 lossless validation，再进入普通 parser。
- 增加 raw-input 负例：duplicate key、`9007199254740993`、unpaired surrogate、数值溢出到 Infinity。

完成这组负例后，**P-JCS-1 足以支持设计冻结，不需要等待完整官方测试语料或跨物理机器测试。**

正式 v0 发布时还要做一个机械动作：

- 当前 `contractVersion = director-plan/0.0-review`
- 当前 Schema ID 仍是 review-v0

发布 v0 时应切换到最终版本标识，然后重新计算最终 Golden Plan digest；不要把 review draft SHA 当作最终 v0 Golden。

## 6. Check / Decision / Approval 继承结论

目标场景：

R1 Intent A 已批准；R2 只新增一个 Shot，Intent 与真实依赖没有变化。

设计目标是合理的，现有字段也基本足够。

正确链路应为：

`R1 Check → R2 重新计算 D-JCS-1 → R2 Check + inheritance → R2 verified_carry_forward Decision`

而不是把 R1 Decision 直接挂到 R2。

要求：

1. R1 原 Check / Decision / Evidence 保持不可变。
2. R2 创建新的 Check，并根据新 revision 重新计算 D-JCS-1。
3. dependency fingerprint 相同且旧 Check=pass/valid 时，允许显式 inheritance。
4. R2 新建 Decision，记录 `decisionBasis=verified_carry_forward` 和 `fromDecisionId`。
5. 不要求用户重新审阅没有变化的 Intent A。
6. R2 Shot B 继续独立审阅。
7. 旧风险、条件批准或媒体检查不能无条件复用。

不建议增加 Event Registry、Approval Tree 或每镜版本树。

## 7. WAR-52 兼容性

WAR-52 `design-0.2` 与公共层的 Action/Shot/StateDelta 身份设计兼容。

已经成立：

- H3 `action_ref` 复用公共 Action identity。
- `completion_delta_ref` 指向公共唯一 StateDelta。
- H3 仅增加 frame anchor，不建立第二个 completed 真值。
- Join 的 `delta_refs` 是引用，不应再次 apply。
- 公共 Shot 估计时长不等于 H3 精确帧。

剩余 Cross-layer 缺口：

WAR-52 `action_phase` 当前只有必填 `phase_key`，且 `additionalProperties=false`，无法原生保存公共 phase 映射。

最小兼容方案：

- 未来 H3 契约版本增加 optional `public_phase_key`；或
- adapter sidecar 保存 `(action_ref, projection phase → public phase)`。

公共 Action 没有 phase 时，H3 自己细化 projection-local phase 仍然合法。

WAR-52 还需在未来跨层执行适配中显式声明 Plan hashRule / projectionHashRule；不应把 design-0.2 的历史 fixture hash 重新解释成 P-JCS-1。

以上均属于 **Cross-layer**，不阻塞公共 WAR-35 Schema 独立冻结。

## 8. 冻结条件

### WAR-35 公共 Schema

建议按以下最小顺序完成后立即冻结：

1. D-JCS-1 canonical payload、集合排序规则、typed-ref closure 与 unresolved/no-digest 规则。
2. media Check execution/evidence 绑定负例。
3. Decision carry-forward / approvedPlan 单调性与风险版本负例。
4. P-JCS-1 raw I-JSON 输入负例。
5. 切换最终 contractVersion，并重新计算 Golden Plan SHA。

不需要等待：

- 完整生产 semantic validator
- Canvas 接入
- H3 adapter
- 真实视频生成
- Guide 实测
- 完整媒体 QA

### WAR-52 跨层适配

公共 Schema 冻结后再处理：

- optional public phase mapping 或 adapter sidecar
- Plan hashRule 映射
- projectionHashRule
- 实际 resolver / adapter
- h3-projection-ready 执行 profile

## 9. 最终建议

**当前不要立即冻结 WAR-35。**

优先只处理 **Blocking 1：D-JCS-1**。这是唯一真正需要先重新收口规范文本与 Schema requiredness 的核心问题。

Blocking 2、3、P-JCS raw-input 缺口主要是冻结语义与补负例，不需要扩大数据模型。

如果 D-JCS-1 按上述最小方案闭合，下一轮复核应可进入：

> **Ready — freeze WAR-35 public Schema；WAR-52 phase/hash mapping 留作明确的 Cross-layer follow-up。**

## 10. 本轮只读保证

本轮没有修改：

- WAR-35 Schema
- WAR-35 原研究正文
- WAR-52 design-0.2
- Linear
- 原始 Director Skill
- Canvas / H3 / ComfyUI
- 生产代码

只执行了本地、轻量、可重复的静态读取与负例验证。

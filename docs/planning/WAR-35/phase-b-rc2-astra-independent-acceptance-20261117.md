**Accepted——仅针对 WAR-35 阶段 B RC2 研究候选。**

固定复核提交为 `adc71b5a9e000cf21fa5c4c0763044e71fc5af72`。本轮定向复现未发现错误返回 `wholePlan=True` 的反例；旧报告所列四类缺口均已被拒绝，同时新增完整性约束允许实际改变内容的合法合成正例通过。

开始与结束时 HEAD 一致、工作树干净。执行仅包含只读检查和内存 Python；关闭字节码缓存，并用 Python audit hook 禁止文件写入及子进程。没有执行报告写入段，没有修改仓库、Git、Linear，也没有操作 WAR-52、生产或 GPU/H3。

**原四项复现结果**

| 复现输入 | 本轮 `wholePlan` | 判定依据 |
|---|---:|---|
| 登记同 target／gate 的冲突 rejected Decision，再从请求数组中隐藏，保留可信完整清单 | `False` | `decision manifest incomplete or untrusted` |
| 当前 B 已封存为 rejected，调用方改成 approved | `False` | 完整清单不匹配；额外隔离测试确认，即使 manifest 匹配传入内容，旧 `sealedDecisions` 仍独立阻止篡改 |
| 来源 Intent A 带合法 `executionTarget`，当前 A 尝试承接为整门批准 | `False` | `projection-scoped decision cannot authorize a whole gate` |
| 当前 Intent A 自身带合法 `executionTarget` | `False` | 同上；这些测试已同步完整封存，排除了“只是 seal 过期”的干扰 |
| hard_conflict 的 `Risk.status="OPEN"`，同步风险 seal 与清单 | `False` | `invalid risk shape` |
| 删除 Inheritance 必填 `basis` | `False` | `invalid inheritance shape` |

对应实现可见 [Risk／Inheritance 与完整清单校验](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-rc2-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:86)、[Decision 封存与整门范围限制](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-rc2-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:180)。

**新增信任约束的省略与合法变动对照**

三个约束均测了恶意省略，也测了非空操作的合法内容变化：

| 约束 | 恶意省略／不一致：均拒绝 | 合法合成变动：均通过 |
|---|---|---|
| trusted Decision manifest | 删除整个 manifest；逐条删除当前／历史 gate 的条目，包括历史空 B 清单；隐藏冲突决定 | 新增开放 unknown 风险，并作出明确接受该风险的 conditional Decision，同步可信决定与清单 |
| trusted current target | 删除 `trustedCurrentTarget`；选择 R2 冒充当前 R3；新版本仍沿用旧可信目标 | 当前 Plan 改为 R4，并实际改变 Shot 时长、重新进行 A/B reviewed 批准、更新相应证明及可信当前目标 |
| current Check seals | 删除整个 `sealedChecks`；逐条删除来源及当前 A/B seal；将已封存 fail 改报 pass | 同一 B Check 增加 `/shots` 依赖集合，重算得到不同 D 指纹，只更新对应 Check seal，仍通过 |

其中最清晰的 Check 正反对照是：

```text
相同 Check ID、相同 Decision：
  改 collectionPaths 和 D 指纹，保留旧 Check seal → wholePlan=False
  仅将对应可信 Check seal 更新为新内容          → wholePlan=True
```

范围限制也做了对照：来源 A／当前 A 携带 `executionTarget` 且封存完整时均为 `False`；去掉局部范围并同步合成可信记录后均恢复 `True`。Inheritance 则仅删除／恢复 `basis`，结果分别为 `False`／`True`。这些结果支持修复并非通过一律拒绝来掩盖问题。

可信目标与 Check 的实现分别位于 [当前目标校验](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-rc2-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:76)、[Check 封存与依赖证明校验](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-rc2-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:130)。

**回归证据**

- 仓库 Gate 矩阵 **35/35** 通过，包含原 26 项和 RC2 新增 9 项。
- 本轮额外定向断言 **39/39** 通过；合计 **74/74**。这是测试断言数，包含用于隔离检查层和正反对照的重复场景。
- raw 往返矩阵 **26/26** 通过，接受输入的两次 JCS 字节一致。
- 两份 RC4 fixture 的 **P、D 四个摘要**均重新计算并与已提交固定 Golden 完全匹配：

| Fixture | P SHA-256 | D SHA-256 |
|---|---|---|
| `no-action-beat` | `c3a7e1b938fb16aedb0f3e28c6693223c80d3cab4c9a450adfe896778b33ef0e` | `7043382336e1aad8fb6ac4b0e234cbb00dcef6ecb73bb8145178cd14e7c29d5a` |
| `cross-shot-once` | `8b163c5db47ef392da2181b3801fef051eb63a0012f773021d434c036df261ac` | `69d960d6f2d6ac8350c17d59540deb4d570b86937dd7f127fc51fc305f8606f4` |

另外，只读 Git 对比确认：RC4 Schema、两份 fixture、Golden 报告及 D-JCS 实现，相对阶段 A 固定提交 `0dcdadf1237e6f0442e17684637d22da8488269c` 无变化。本轮遵守仅内存 Python 的限制，**未重新运行 Node 跨语言校验，也未重跑旧报告的 10,007 个数值扩展采样**。

**验收边界**

上述 Accepted 依赖[第 30 节明确规定的研究前提](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-rc2-20261117/docs/planning/WAR-35/director-plan-contract-proposal-v0.md:1241)：`sealed*`、完整 Decision 清单和当前目标来自独立可信来源。测试中的“合法变动”是内容确实发生变化、相关证明一致更新的**合成授权事件**，没有验证现实用户身份或外部账本写入权限。

仍未证明真实审批权限、不可变历史、完整目录的可信生成与防回滚、生产接口对调用方自签 seals 的隔离、媒体字节与执行目标归属，以及 WAR-52／GPU／H3 执行。因此，本结论不构成公共 Schema 正式冻结、WAR-35 整体完成或生产授权。
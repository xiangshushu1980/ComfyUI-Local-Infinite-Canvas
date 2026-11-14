# WAR-35 阶段 A · RC1 依赖指纹与外部观察

Eric，2026-11-14。适用于 director-plan/0.1.0 RC1。基线 cbfc75d，独立报告 f323e15。阶段 A 的局部检查通过，整体冻结结论仍为 Not ready。

## 现行规则

D-JCS-1 使用 `war35-dep-jcs8785-sha256/2`。canonical payload 保留 §23 的字段及 §24 的 mediaBindings。profile 改为 /2，collections[].value、resolvedObjects[].value 和闭包成员由以下规则决定。Check 和 inheritance 都要求 /2。/1 历史记录保存在旧提交，重新审核时使用 /2 从原始依赖计算，禁止将旧摘要改标签后沿用。

1. Pointer 从 Plan 根携带 Schema 位置；列表的实际索引映射为数组项，字典键保持字面值。解析出的引用对象从 §23.2 注册位置继续遍历。仅 §23.2 明列的引用数组排序去重，单引用继续解析，按 typed ref 去重终止环。直接选择引用数组与从对象内部到达该数组使用同一规则。
2. 其余数组保序。known.value 中任何业务键、字符串、任意嵌套数组均保留，不新增边。非局部依赖（例如需要所有 Shot）仍须检查规格明确声明范围；决定整个 gate 的最低覆盖留给阶段 B。
3. 任何到达的 sourceBinding 都触发唯一身份解析，包括来源集合及整 Plan 中从未被 Fact 引用的来源。仅支持实际取得的内联 text 快照，按 UTF-8 原文重算 SHA-256，与 binding 和 snapshot 的 SHA 对齐。缺失、歧义、内容变更、仅提供 locator 或需要 asset resolver 时无指纹。
4. human、geometry_proxy 均可能依赖包外观察。本阶段研究 resolver 无法核验观察字节、条件及归属，统一返回 unresolved；text 显式带外部 evidenceRefs、evidenceBindings 或 executionTarget 也按此处理。相同字符串引用不能证明内容与适用范围相同。研究路径无法据此作有效 pass/fail 或自动承接，应重新审阅，未解决时仅记录 unknown/not_checked。未增加外部证据注册表。media 保留 §24 声明摘要研究路径与运行时验证边界。
5. Decision 验证以整份 Check 重算摘要，两端明确要求有同一有效指纹。scope 的集合顺序已进入规范化载荷，Decision 不再额外按列表原序比较。此处只支持局部检查证据的相等判定。

## 红绿对照

`verify-phase-a.py` 在改实现前先跑六个测试方法，17 个失败断言。扩展到十个方法后把同一文件复制到 f323e15 的 git archive 上重跑，21 个失败断言。修复后十个方法及全部子例通过。依赖变异从 RC1 Cross Shot 构造，两侧先过 RC1 Schema；Decision 走既有合成历史入口。

| 测试输入 | /1 实测 | /2 实测 |
| --- | --- | --- |
| 直接选择 basisRefs 后改 Fact；直接选择 Beat.actionRefs 后改 Action | 两对分别同摘要 | 两对分别得到不同有效摘要 |
| 来源集合、直接 basisRefs 间接来源，分别删除快照、篡改原文、将 text 源改为 asset | 六例均得到摘要 | 六例均 unresolved |
| 整 Plan 上述三项变异；另加一个没有快照的未引用来源 | 拒绝前两项，接受 asset 和新增无快照来源 | 四例均 unresolved |
| Delta.after.value 中 subjectRefs 两项交换，分别选 Delta 或另含该数组的 Pointer | Delta 摘要相同；显式 Pointer 可区分 | 两条路径均可区分 |
| 业务 JSON 包含不存在的 actionRef 和混合类型 basisRefs | 无指纹 | 得到有效指纹 |
| 直接选 visualDesign.subjectRefs 并重排 | 指纹改变 | 指纹相同 |
| 两代 human、geometry_proxy、带证据的 text，观察引用分别不同或相同但不可验证 | 六例均承接旧 pass | 六例均拒绝 |
| 显式请求旧 hashRule | 仍生成 /1 摘要 | 无 /2 摘要 |
| 不改 Intent，仅新增无关 Shot；两代额外依赖集合重排 | 基本承接成功，重排被拒 | 两例均承接成功 |

## 回归与 Golden

在本目录运行 `python3 verify-phase-a.py`。按 §27.4 重跑生成器及六组回归，D-JCS 14、D-Schema 9、Media 20、Decision 37、Raw 34、RC 23，共 137/137。Eric 隔离环境原 verify_jcs.py 的 21 个 Python/Node JCS 案例及输入、Plan 不变量通过。再运行 build-v0-rc.py 对比全部 JSON，逐字节相同。独立审阅报告 SHA-256 为 074963c73eba638565a8de994e30b66cebd968b02994c967df0b912de8fd4d00。

| RC1 Intent 用例 | 基线 /1 | 当前 /2 |
| --- | --- | --- |
| No Action | a04aeb2dc8f601b5ae21d22cb23166819e127b5670d2edbf69afb29ff22b6711 | 24ba48c4cc22877df43abe56f7c8b1f91e354b730edaf07979f0ab63a03e83d1 |
| Cross Shot | 5de00b76a687852101095144a4d849c3797a39d71ad45a3f25cb5acc277ce74f | 048d0befa6be64eee9305941a8eed9a7ffe8bdcee4add9c03747f8a9635ddba3 |

两例 P-JCS-1 Golden 与 §27.2 相同。两份 Plan 示例未变。review Schema 修改 Check/inheritance profile 常量和说明，生成的 RC1 Schema 同步。review 的 D 基线及合成 media 摘要也随 profile 更新。可复算报告为 d-jcs1-verification.report.json、media-check-verification.report.json 与 v0-rc1-golden.report.json。

阶段 B 可从整门 A/B 的目标、方法和成员覆盖、适用风险、冲突 Decision 与执行范围、直接父修订证明接续。raw I-JSON 往返、固定 Golden 的只读发布断言、media resolver 负例与最终独立再复核仍待处理。本阶段为设计验证，生产与 H3 未执行。

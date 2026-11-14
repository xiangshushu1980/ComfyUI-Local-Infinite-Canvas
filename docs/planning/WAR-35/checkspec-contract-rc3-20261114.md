# WAR-35 · 阶段 A 最终局部 CheckSpec 收口 · RC3（2026-11-14）

**状态：实现修复已通过研究测试，等待独立 Astra 复核；阶段 A 尚未正式验收，WAR-35 整体 Not ready，B 未开始。**

基线：`edcbd82b269c86ce03e7dc746a47b430ed826bcf`；独立审阅入口：`phase-a-rc2-independent-acceptance-20261114.md`（仅用作输入、原样保留；SHA `4557b6d2c47901e3f525643bc53493198409aafd5f4ad83fd7a77a7946c26194`）。前次阶段 A 审计原件：`phase-a-independent-audit-20261114.md`（SHA `e788395e75325b07c7214cd9e35eb26a1e5d9200ec10d68aa96d60b2feb34109`）。

## 1. 根因与最小修复

RC2 的 `CHECK_SPECS` 仅登记 `(text,sourcePolicy)`，任何已登记 text 条目均可被调用方改报为 media，或 media-v1 改报 text，且 `closure-only/1` 无目标种类约束。Astra 两个反例在缺少真实受检对象/证据时仍得到可复用的真实 /3 摘要。

RC3 为**现有全部 8 个**规格登记不可由 Check 自行选择的 `text/sourcePolicy/allowedMethods/targetKinds`；计算 D-JCS 指纹之前先核对：
1. `checkSpecVersion`、规格全文精确匹配登记项；
2. `method` 属于登记的 `allowedMethods`；
3. `targetRefs` 非空，每一项 kind 匹配 `targetKinds`，并在当前 Plan 唯一解析目标；
4. `fact-local/1` 目标实际拥有非空 `statement`；
5. 必要的来源关联、来源 SHA 及外部观察/媒体条件仍沿用阶段 A 的 fail-closed 验证。

| CheckSpec version | 允许的方法 | 目标种类 | 来源政策 |
| --- | --- | --- | --- |
| `fact-script/1` | text | fact | target-fact-sources/1 |
| `intentA/2` | text | intent | intent-basis-fact-sources/1 |
| `A/2` | text | intent | intent-basis-fact-sources/1 |
| `intentA/v1` | text | intent | intent-basis-fact-sources/1 |
| `fact-local/1` | text | fact | closure-only/1 |
| `closure/1` | text | 所有已有 typed-ref kind（plan/source/fact/constraint/subject/intent/beat/action/delta/blocking/shot） | closure-only/1 |
| `shotB/1` | text | shot | closure-only/1 |
| `media-v1` | media | intent、shot | closure-only/1 |

`closure/1` 作为保守完整依赖测试允许多个目标种类，**不是 Intent A/Shot B gate 审批资格**。`media-v1` 在真实 bytes resolver 尚未实施时仅绑定调用方声明的证据 SHA 与执行目标——绝不宣称已实际验证媒体、得到生产级 pass。普通无来源 Fact 仍可用 `fact-local/1` 进行非来源检查。Check 本身可否产生摘要与整个 Gate 的必审覆盖严格分离，后者仍属阶段 B。

## 2. 版本隔离和 Golden

有效指纹语义已改变；因此 **D-JCS-1 升级为 `war35-dep-jcs8785-sha256/4`**。新 `checkSpec` canonical payload 同时绑定 `sourcePolicy`、`allowedMethods`（排序数组）及 `targetKinds`（排序数组），并保留 `text/version/method`。RC3 Schema ID `urn:canvas-lab:director-plan:0.1.0-rc3`，工作 review Schema 有单独 `review-rc3` ID。RC1、RC2 原有 Schema、示例、Golden 不覆盖。

- `contractVersion` 仍为 `director-plan/0.1.0`（**候选，非冻结**）。
- P-JCS-1 两份 Golden 与 RC2 一致：No Action `c3a7e1b938fb16aedb0f3e28c6693223c80d3cab4c9a450adfe896778b33ef0e`；Cross Shot `8b163c5db47ef392da2181b3801fef051eb63a0012f773021d434c036df261ac`。
- RC3 D-JCS-1 /4 Golden：No Action `7043382336e1aad8fb6ac4b0e234cbb00dcef6ecb73bb8145178cd14e7c29d5a`；Cross Shot `69d960d6f2d6ac8350c17d59540deb4d570b86937dd7f127fc51fc305f8606f4`。
- RC3 Schema 的 Check/inheritance 均只允许 /4；携带 /3 的记录不被 RC3 接纳，把旧 digest 直接改贴 /4 也无法通过重算验证。

## 3. 同案红绿和全量回归

`verify-checkspec-contract.py` 为本次统一测试入口，在 `edcbd82` 的干净 git archive 与当前 RC3 使用相同的 63 项测试名称：

| 样本 | 结果 | 证据 |
| --- | ---: | --- |
| 原 RC2 `edcbd82` | 50/63，13 个反例失败 | `checkspec-rc2-reproduction-verification.report.json` |
| 修复 RC3（相同 63 项） | 63/63 | `checkspec-rc3-common-verification.report.json` |
| RC3 外加版本兼容、Golden、canonical 字段及两组独立 Node D-JCS SHA 验证 | 74/74 | `checkspec-rc3-verification.report.json` |

原六组回归 **137/137**（D 14、Schema 9、Media 20、Decision 37、Raw 34、RC 23），来源证明 **24/24**，阶段 A 原专项 **10/10** 均通过。RC3 Python/Node 两实现 JCS bytes 一致（见 `v0-rc3-golden.report.json` 的 23 项中跨语言检查）。新增测试包括每个注册规格四种 method 的正确/错误组合，目标种类/不存在的对象、错误规格文本，及两项 Astra 攻击复现。

以上是**研究性质的结构和指纹验证**；不存在用户真实审批、完整 Gate 成员覆盖、媒体字节 resolver 或生产权限执行器。不能以 74/74 推断 WAR-35 可冻结。

## 4. 复跑

```bash
cd /home/sean/projects/canvas-lab
python3 docs/planning/WAR-35/build-v0-rc.py
python3 docs/planning/WAR-35/verify-checkspec-contract.py --common
python3 docs/planning/WAR-35/verify-checkspec-contract.py
python3 docs/planning/WAR-35/verify-phase-a.py
python3 docs/planning/WAR-35/verify-fact-source-proof.py
python3 docs/planning/WAR-35/verify-decision-gates.py
python3 docs/planning/WAR-35/verify-media-check.py
python3 docs/planning/WAR-35/verify-d-jcs1-schema.py
/home/sean/.local/share/canvas-lab-jcs/venv/bin/python docs/planning/WAR-35/verify-d-jcs1.py
python3 docs/planning/WAR-35/verify-raw-ijson.py
python3 docs/planning/WAR-35/verify-v0-rc.py
```

独立验证原红例：先 `git archive edcbd82 docs/planning/WAR-35` 到临时目录，将当前 `verify-checkspec-contract.py` 复制到该临时副本，运行 `python3 verify-checkspec-contract.py --baseline`；RC2 只含公共 63 项，不执行 RC3 专属兼容测试。**不在当前工作树上执行 /3 的旧生成器**，避免改写候选证据。

## 5. 下一步

以本轮独立 Git commit 为候选基线，交回原 Astra 审核 Agent 做**阶段 A 定向只读验收**；重点独立检验 CHECK_SPECS 的 method/targetKinds 完整性、无法骗过的媒体/Fact 负例和 /3→/4 隔离。即使 A 获接受，WAR-35 也因 Gate 覆盖、适用风险、修订父版本和 raw I-JSON 往返仍为 Not ready。**未经用户启动，不进入阶段 B。**

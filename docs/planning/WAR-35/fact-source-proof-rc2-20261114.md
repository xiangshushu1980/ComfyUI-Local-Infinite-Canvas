# WAR-35 · 阶段 A 来源证明复核入口

Eric，2026-11-14。实现基线 cb7e8fd；输入为本目录 phase-a-independent-audit-20261114.md，SHA-256 e788395e75325b07c7214cd9e35eb26a1e5d9200ec10d68aa96d60b2feb34109。阶段 A 等待独立复核，整体 Not ready。§28 的进入 B 判断由此次独立审阅取代。

## 基线与闭包

先在 cb7e8fd 干净归档运行独立报告原始 probe。Fact.sourceRefs=[] 时，原文、相反原文（同步更新 binding/snapshot SHA）、无快照三者的 Fact 指纹都是 c48d4ad4c59dc1d5defa6660db423344a787943aed187459f08717b91bbb1736。用报告的两个修订重新生成 PlanTarget、Check 和封存记录，valid_case(case, False) 对两种变化均允许 Intent A 承接。

RC2 复用 Check.checkSpecVersion。研究验证器 verify-d-jcs1.py 的 CHECK_SPECS 给每个已登记版本固定规格文本与来源策略；精确文本核对防止冒用另一版本，策略只由登记项选择。新增规格必须明确登记，未知版本、版本与文本冲突均 unresolved。没有增加 Check 字段。Fact.sourceRefs 仍允许空数组，草稿保存与 Check 可承接性各自校验。

- target-fact-sources/1 要求每个 Fact 目标自身有来源边。intent-basis-fact-sources/1 从每个目标 Intent 的 basisRefs 出发；所有 Fact（含经 constraint 间接到达者）须有自身来源，所有分支最终到达 Source。允许 Intent 直接以可验证的 Source 为 basis。空根、空分支、错目标或不唯一引用均无法证明。额外 dependencyRefs 和 collectionPaths 无法替代任一目标的证明。
- 普通 Plan 闭包继续独立收集所有已声明依赖，对每个 Source 唯一解析 binding/snapshot，复算 UTF-8 原文字节 SHA。验证的是不可变内容与结构归属；Fact 陈述的语义是否符合原文仍由实际 Check 判断。没有新原文语义评判器。
- closure-only/1 不追加来源必需条件。普通局部检查可检查没有来源的 Fact，已有引用边仍按普通闭包验证。研究用 Intent A 入口只接受其已登记 gate/spec；改用普通局部规格无法满足 Intent A 映射。该映射仍是局部研究夹具。
- D-JCS-1 升至 war35-dep-jcs8785-sha256/3，canonical payload 的 checkSpec 新增 sourcePolicy，并绑定规格文本、版本与方法。文本 Intent A 规格从 intentA/1 升至 intentA/2。旧 Check/inheritance 的 /2 规则不能在新候选使用；对旧 SHA 改标签也无法通过重新计算。

## 红绿验证与候选分发

同一 verify-fact-source-proof.py 分别在 cb7e8fd 的归档及当前目录运行。24 项在旧版通过 10 项（14 项暴露缺陷），新版 24/24。fact-source-proof-verification.report.json 保留逐项期望和实际结果。无来源且剧本变化或缺失均无摘要，两个 Intent A 承接均拒绝；正确绑定时原文变化使摘要不同，缺快照无摘要，不变的来源允许承接。附加来源或其他有来源的 Fact 都不能补足目标 Fact 的空边。补测混合直接/间接 basis、直接剧本 basis、伪装和未知规格、局部无来源检查及 /2 profile。

原阶段 A 10 个测试方法及全部子例通过。六组原回归按新候选复跑：D 14、Schema 9、Media 20、Decision 37、Raw 34、RC 23，总计 137/137。通用 Python/Node JCS 21 例及附加不变量通过。

独立 Schema ID 为 urn:canvas-lab:director-plan:0.1.0-rc2。review Schema 同步获得独立 review-rc2 ID，生成器只生成 RC2。RC1 Schema、示例、Golden 与 /2 摘要报告保留。contractVersion 与 P-JCS-1 未变，两份 RC 的 Plan SHA 相同；RC2 的新 D Golden 分别为 No Action 25f9b12c58afbedd19ceaf392ae311447b3ec615c1e99ed386370193b79cc590 和 Cross Shot 5f7f678e225ea6e992b45156f2dbfa5d9125cec12bd4c72c44077a95fa139142。全部 RC2 JSON 在第二次生成与 Golden 计算后逐字节相同。

在本目录运行 python3 verify-fact-source-proof.py、python3 verify-phase-a.py；按提案 §27.4 的命令运行生成器及六组验证。完整复现旧结果时，将新专项脚本复制到 cb7e8fd 的 WAR-35 归档目录运行。对照报告 before/after 即可复查。交付范围停在本次来源证明，待独立审核 Agent 验收。

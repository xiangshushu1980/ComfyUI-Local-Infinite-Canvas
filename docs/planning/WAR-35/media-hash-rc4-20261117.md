# WAR-35 · 阶段 A 媒体 SHA 严格验证｜RC4 研究候选（2026-11-17）

**状态：RC4 定向修复与隔离回归已通过，等待独立复核。阶段 A 尚未 Accepted；WAR-35 Not ready；阶段 B 未启动。**

## 前置依据和变更

- 原始 RC3 Git：0ed1388a8bef597ac6547485179b437ca9735471；独立审阅事实见同目录 phase-a-rc3-astra-independent-review-20261117.md。
- 研究计算器 verify-d-jcs1.py 增加严格 re.fullmatch 对 executionTarget.projectionContentSha256、evidenceBindings[].contentSha256 及存在时的 conditionSha256 校验，非法字段拒绝计算。
- 新建 director-plan.schema.review-rc4.json 与 director-plan.schema.v0-rc4.json，为共享 $defs.hash 增加 minLength=64、maxLength=64，保留原 RC3 Schema 和报告；RC4 Schema ID 为 urn:canvas-lab:director-plan:0.1.0-rc4。
- 新增 build-v0-rc4.py、verify-v0-rc4.py、verify-checkspec-contract-rc4.py、verify-media-hash-rc4.py、两份 RC4 示例及独立报告。原 RC3 实验脚本和冻结报告不覆盖。
- contractVersion 仍为未冻结候选 director-plan/0.1.0。D-JCS /4 profile 暂不升级：合法 payload 与两个 D Golden 没有变化，收紧的是尚未发布的非法接受域；既有任何声称的依赖摘要都必须基于最新规则重新验证。是否需要额外版本升级仍留待独立验收审阅。

## 固定输入与测试结果

在 Eric 通过 git archive 0ed1388 对 docs/planning/WAR-35 建隔离副本，先在 /tmp/war35-rc4-stage-jKpB1R/docs/planning/WAR-35 修改、生成并执行，再复制研究候选到项目；没有在带其他未提交文件的工作树上执行旧候选生成器。

| 验证 | 通过 |
| --- | ---: |
| RC4 媒体 SHA：合法媒体、投影/内容/条件 SHA 的尾换行、非十六进制、长度异常、大写反例与两修订；P/D Golden 保持 | 57/57 |
| RC4 CheckSpec 规格与版本隔离 | 74/74 |
| RC4 Schema / Golden | 23/23 |
| 阶段 A、Fact 来源 | 10/10、24/24 |
| Decision、Media、D-Schema、D-JCS、Raw I-JSON | 37/37、20/20、9/9、14/14、34/34 |

合法 P-JCS Golden 未变：No Action c3a7e1b938fb16aedb0f3e28c6693223c80d3cab4c9a450adfe896778b33ef0e；Cross Shot 8b163c5db47ef392da2181b3801fef051eb63a0012f773021d434c036df261ac。

合法 D-JCS /4 Golden 未变：No Action 7043382336e1aad8fb6ac4b0e234cbb00dcef6ecb73bb8145178cd14e7c29d5a；Cross Shot 69d960d6f2d6ac8350c17d59540deb4d570b86937dd7f127fc51fc305f8606f4。

## 未证范围与下一步

本次仅是研究性声明格式与依赖计算器验证；未验证真实媒体 bytes、实际用户 Decision、A/B 整门 Check 覆盖、适用风险、可信直接父版本、raw I-JSON 规范化读回，以及 WAR-52 H3 投影互认。下一步交回原 Astra 对固定 RC4 commit 进行阶段 A 定向只读验收。未经接受，既不宣布 A 通过，也不启动 B 或正式冻结公共 Schema。

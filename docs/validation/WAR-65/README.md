# WAR-65｜DirectorSKILL 研究资料索引

> 设备：Eric；项目：`/home/sean/projects/canvas-lab`。本目录的研究 Markdown 是详细判断的权威正文；Linear [WAR-65](https://linear.app/xiangshushu/issue/WAR-65) 只维护任务状态、决定、边界与入口。这里不是新实验或新结论。

## 当前阶段

C/D/E 原版文本流程的阶段记录及跨样本综合评审已形成；整体待用户最终讨论并确认收口。下一步优先 WAR-66 ViMax 原版观察，再由 WAR-59 汇总三种 Skill。未经批准不修改 Skill、冻结结果或执行 GPU/图片/视频。

## 按问题读取

| 要查什么 | 权威材料 |
| --- | --- |
| 跨样本结论、阶段职责、能力边界与未证实项 | [cde-cross-sample-review-20261111.md](cde-cross-sample-review-20261111.md)；Git `c51b0bf` |
| 几何可行性、Red 风险、镜间切点与复检方法 | [directing-verification-findings.md](directing-verification-findings.md) |
| C 原始阶段观察、历史讨论 | [linear-export/c-observation.md](linear-export/c-observation.md)；C 冻结原始执行文件见下述证据包 |
| D 冻结辅助输入 | [d-assisted-v1-input.md](d-assisted-v1-input.md) |
| D Step 2/3 原始输出与审阅 | `d-assisted-v1-step2-raw.md`、`d-assisted-v1-step2-review.md`、`d-assisted-v1-step3-raw.md`、`d-assisted-v1-step3-review.md` |
| D Step 5/6/7 原始输出与跨阶段审阅 | `d-assisted-v1-step5-raw.md`、`d-assisted-v1-step6-raw.md`、`d-assisted-v1-step7-raw.md`、[d-assisted-v1-step4-7-review.md](d-assisted-v1-step4-7-review.md)；Git `485ddcc` |
| E 冻结剧本与逐阶段执行材料 | `e-script-frozen.txt`、`e-original-v1/step{2,3,5,6,7}/`、[e-original-v1/review-and-findings.md](e-original-v1/review-and-findings.md)；Git `01bed8e` |
| C/D 原始日志、模型输入与 Skill 快照 | [evidence/README.md](evidence/README.md) 和 `evidence/war-65-cd-member-manifest.json`（含 137 项） |
| 已从 Linear Document 全文迁移的历史来源 | [linear-export/export-manifest.md](linear-export/export-manifest.md)，历史 Issue 快照、C 观察、D 输入候选在 `linear-export/`，均**非当前指令** |

## 证据冻结与重要版本

- C/D 原始包：`evidence/war-65-cd-original-execution-20261111.tar.gz`；SHA256 `3cd2eb5b84653aaa384612b05f49166283454faa17cff1a407125a784629cc51`；原包不入 Git；说明与成员级 SHA 见 `evidence/README.md`。
- D 辅助输入 SHA256 `d0d8968488d23e627bf020776786e64e1ac2efef94eadc974ed3704e3e7f6c49`；各步独立输出 SHA 见对应审阅文件或冻结清单。
- E 原剧本 SHA256 `466d257d3ac684ea20e76eb01f80589270484478cc75b084c1f0640c77d576ec`；各步 `sha256-manifest.txt` 为原始输出依据。
- 原上游 DirectorSKILL commit `c65ae0d14457053efb1e354c7e7f7e120d97fad1`；`gpt-6.1-terra` / Medium / read-only / ephemeral；使用原始规则文本回放，**非正式安装 Skill 的完整应用运行**。
- C/D 证据已从 Terry 迁移至 Eric 并逐成员验证；异机备份尚未核验，旧 Linear Document/Resources 与 Terry 旧副本尚未清理。不得覆盖原始冻结文件，也不得宣称灾备完成。

## 文件责任

本索引用于按需查找；不复制全部研究正文、原始日志或逐阶段完整 SHA 列表。当前决策和验收状态请以 Linear Issue 为准；跨样本具体论证请以本地综合评审为准。


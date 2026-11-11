# WAR-61｜Toonflow C/D/E 研究资料

> 设备：Eric；项目：`/home/sean/projects/canvas-lab`。本目录的当前研究概述与证据索引是本地权威入口；Linear [WAR-61](https://linear.app/xiangshushu/issue/WAR-61/研究toonflow-多剧本-script-director-plan-storyboard只读观察) 维护任务状态、执行边界和本入口。两份 Linear Document 的逐字导出留在 `linear-export/`，作为来源副本，不再作为日常编辑位置。

## 当前状态｜2026-11-11

C/D/E 三个文本样本已逐例收口并经用户审阅；**WAR-61 整体仍 In Progress**。迁移子任务 WAR-67 已按本地文件、哈希和资源包成员核验。跨样本综合评审与研究结论仍待 WAR-61 收口；本迁移不代表研究验收完成。

| 样本 | 原始输出 | 当前观察 |
| --- | --- | --- |
| C《没说出口》 | 12 Shot / 4 片段 / 36s（目标约30s） | 保留停顿、未尽之言与告别；近景切分、表演可读性和超时风险未实测。 |
| D《错过的钥匙》 | 13 Shot / 3 片段 / 40s | 观众先看到钥匙、文件夹遮挡与再显露、右手交接及走位各有镜头功能；精确几何和动作时长未实测。 |
| E《最后一张照片》 | 15 Shot / 4 片段 / 42s（目标约40s） | 翻面→首次揭示手写文字→人物反应的顺序清楚；跨片段手部/文字可读性、余韵及时长未实测。 |

三例的 Script → Director Plan → Storyboard 文本传递整体忠实，不支持“只按台词机械切镜”的简单判断。样本量、单轮文本回放不足以证明普遍导演质量、模型稳定性、真实调度或视频生成效果。上表是已有研究观察，非新实验或制作验收。

## 研究依据与边界

- 执行是 Terry 上 Codex CLI 对冻结 Toonflow 规则进行只读文本回放，C/D/E 的 Director 与 Storyboard 调用日志记录 `gpt-6.1-terra`、Medium。**不是完整 Toonflow App 运行**；未写入画布、未制作图像或 Animatic、未运行 H3/GPU。
- 原始规则、真实调用输入和日志以证据包为准；原始剧本、Director Plan、Storyboard 及其 SHA 索引见 [C/D/E 原始文本导出](linear-export/cde-original-texts.md)。历史阶段讨论和整理前正文见 [历史导出](linear-export/history-and-analysis.md)，其中旧待办不构成当前指令。
- 尚未知：真实画布/资产及确认状态、场景精确几何、实际动作与对白时长、模型可用时长、画面连续性和视频效果。风险必须与已见文本问题区分。
- 不改 Toonflow Skill/规则、冻结剧本和输出、模型参数或画布；不执行图片、Animatic、H3、GPU 或新实验。若要扩样、做配对对照或开发 Skill，须另定目标与授权。
- 跨样本综合评审及整体研究结论尚未在 WAR-61 完成；下一步由 WAR-61 继续，不把本次资料迁移算作结论验收。

## 原始资料与迁移核验

- [迁移 manifest](migration-manifest.json) 记录两个 Linear Document 的源 ID、标题、UTF-8 字节数与 SHA-256，原始附件包的 ID、SHA-256、大小与成员数量，以及 C/D/E 九份冻结文本的逐项核对结果。
- [资源包成员 SHA-256 清单](evidence/member-manifest.json) 覆盖解包所得所有文件；[Linear 原始证据包](evidence/war-61-original-evidence.tar.gz) 保持原样，解包副本在 `evidence/raw-package/toonflow-20261107/`。
- 附件包 SHA-256 为 `c484936a3ab3ad00f4217c752f16602516e97d740493c683d4a297b416749d2e`，280,221 bytes；归档含 65 个 tar 条目（58 个文件、7 个目录），普通文件解包共 912,413 bytes。
- C/D/E 九份 script、Director 输出和 Storyboard 输出的 SHA-256 均与 Linear 原始文本导出所列相符；两个 Linear Document 的原始内容以 UTF-8 原样写入并与来源响应 SHA-256 相符。
- 证据包根部 `MANIFEST.json` 中的 `gpt-6-luna/high` 和 19 项清单适用于较早的 A/B 样本；**不能用于标注 C/D/E**。C/D/E 自身日志均记录 `gpt-6.1-terra/medium`。
- 二进制原始包和解包证据保留在 Eric 本机工作树，尚未核验异机备份；不得据此声称已完成灾备。Terry 上旧副本及 Linear Documents/Resources 均未删除。

## 文件索引

- `linear-export/cde-original-texts.md`：C/D/E 九份原始文本和源 SHA。
- `linear-export/history-and-analysis.md`：完整历史进度与旧分析。
- `evidence/raw-package/toonflow-20261107/`：原始输入、输出、日志、冻结规则副本及上游元数据。
- `evidence/member-manifest.json`：每个原始包成员的字节数与 SHA-256。

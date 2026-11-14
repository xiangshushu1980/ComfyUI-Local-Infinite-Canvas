# WAR-89｜Director Skill v0 候选作者说明

2026-11-14。交付给 ChatGPT 独立复核。本轮角色为主作者；没有启动子 Agent，没有进行新模型对照或独立模型验收。七文件是设计候选，不是生产 Skill，不宣布专业验收通过。

## 1. 交付范围

候选根：`docs/planning/WAR-89/director-skill-v0-candidate/`，精准七文件：

```text
SKILL.md
stages/intent.md
stages/beat.md
stages/blocking.md
stages/shot-plan.md
references/knowledge-index.md
references/review-method.md
```

独立证据/备测包同在 WAR-89：
- `director-skill-v0-d-paper-walkthrough-20261114.md`：人工纸面推演；示例虚拟已批准 A → 单候选 Beat/Blocking → Continue Shot02/03 → 返回 Blocking → 应用 Shot 修订 → 模拟 Resume。
- `director-skill-v0-ce-minimal-text-cases-20261114.md`：两份短剧本原文、行号、原件 SHA、任务与严格反例/允许多解/未知；没有试验结果。
- 本文件：范围、取舍与校验记录。所有历史稿保持原字节。

## 2. 与此前七文件草案的实质差异

依据是 `director-skill-v0-file-and-prompt-design-20261114.md`；没有覆盖它。原稿规定职责和 Prompt 方向，本候选把方向落为可执行的专业选择：

1. 主 SKILL 压为 32 行的入口与调用/返回语义；四阶段不复述同一模板。Intent 比较关系观察与主观体验的代价；Beat 用因果而非动作数量判断沉默；Blocking 比较让出通道与动作分相；Shot 明确观察路径、注意窗口、动作中途切和声画归因。
2. 阶段不强制成为独立会话；Continue/Refresh/Resume 都先守 Authority。没有批准 Intent 的首次 Intent 起草明确写“尚无”，不伪造批准补包。候选交接、正式批准、旧结果隔离分别说明。
3. 知识索引每 K 提供触发、任务、主源编号、可定位原始路径/章节、停止条件和源许可风险；不再只是来源名字。DS/TF/VM 按问题选择；原始 Prompt 的固定镜数、秒数、评分、Camera Tree 和生成流程未复制。
4. D 不停在“可选关系镜或插镜”：本轮选客观桌面细节 Shot02，Shot03 回关系镜，随后实际返回并应用 Blocking-r1。保留一个活跃 P1；恢复时仅带旧候选失效原因，不混合旧无窗口方案。
5. C/E 备测保留准确原文字节的逐行内容。C 检查自主停句与第二次广播因果；E 检查核心承诺语义、同步首次阅读和未收相册，避免只做全文字符串或“露出字数”检查。

这些具体专业选择仍待复核，不把用户批准七文件写作或 B-flex 语义误作采纳全部细则。

## 3. 最重要的专业取舍

D 的作者要求观众确实先知道钥匙，本轮用一次客观细节镜分配辨认机会，接受线索更显著、表演连续性较弱的代价。关系镜并未被理论否决，若以后证明能兼顾小钥匙和自然表演，它仍是合理替代。不能仅靠“客观镜”标签保证观众不会归为周 POV；须检查相邻注视、机位和反应。

Shot 返回 Blocking 只调整林移文件的手退出观察通道后再取蓝夹，以及周抵桌与遮回的相对时点。钥匙位置不变、林首次未注意、周未目击、第二次移夹林才发现、最终周右手接均保留。真正薄弱处是蓝夹/纸叠覆盖 K、林身体遮挡周的几何能否同时成立；本轮不把它写成事实。

C 允许微表演和不同切法，不能把克制误为不动。E 允许同镜翻面或插镜，但“文字部分泄露已传达承诺”同样违背信息政策；背面不可辨纹理不是自动失败。语义硬冲突与真实视觉未知分别记录。

## 4. 输入、出处和许可

实际逐行核对的冻结剧情：
- `docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-C/script-C.txt`：`ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d`
- `docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-D/script-D.txt`：`65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`
- `docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-E/script-E.txt`：`466d257d3ac684ea20e76eb01f80589270484478cc75b084c1f0640c77d576ec`

具体输入按用户指定读取：本地 linear-task-collab、交接 brief、WAR-74 §1–6、B-flex §11–12、七文件设计稿全稿、K1–K7 规则目录及 §7/8/9；三源独立稿仅沿相关编号与原始章节展开。未重做三源完整审计。skill-creator 用于薄入口、渐进加载与静态验证；明确用户禁止委派，未做该技能可选的独立 Agent 验证。

DS 本地 LICENSE 本轮核为 MIT；冻结 commit/版本沿已有独立稿定位。TF 为迁移整合快照，上游许可仍未核；VM 上游 commit/许可仍未核。候选只写原创专业表述与位置索引，未复制原 Prompt/代码，也没有作分发授权保证。VM camera 文件实物 SHA 为 `b3165016eb6942ebb3bfc3a4d93a73caad2b6d7700297642d6a2126a7c5e777c`，与规则稿更正吻合；没有改历史独立稿中的笔误。

历史代理仅引用 WAR-74 §7 对旧 960×540、约 27×9px 的总结，本轮未重测代理。剧情资产按 D L58、C L36、E L56 均未制作；不把“假设只有照片正面参考”写成当前项目事实。

## 5. 静态自查与限制

- 文件树核对：候选恰好七文件，另三份本轮 Markdown；未生成 agents/openai.yaml 或安装目录。
- `python3 /home/sean/.codex/skills/.system/skill-creator/scripts/quick_validate.py docs/planning/WAR-89/director-skill-v0-candidate` 返回 `Skill is valid!`。它只核格式，不核导演能力。
- 候选/两份证据中 12 个 Markdown 相对链接定位存在；原始来源入口按章节定位，修正 DS Director's book 起行到 L189。
- C/E 编号原文与冻结原件逐行程序比对一致；所有 SHA 以本机文件字节计算。
- 作者人工检查了 D 两次发现、遮回、知情、一次交付/右手、局部修订实际落入 Shot-r1、Resume 拒绝污染。此为作者静态自查，不是独立验收或 LLM 调用实测。
- 缺少真实几何、图像/声音、观众理解证据；1–1.5 秒仅 D 排练起点，不是已校准可读阈值。全场预算和 B 审阅未完成。

## 6. Git 范围与操作记录

开始时分支 `war-35-schema-freeze-review-20261114`，HEAD `cf4bb60a83fa562b2368fd4e8994b37bfbe34e4d`。工作树原有 docs 导航、构建产物、节点目录和多份研究/媒体未跟踪内容；本轮不整理它们。原有 WAR-89 未跟踪 `codex-candidate-task-20261114.md` 也未改。

本轮新增仅为上述七文件目录及三份独立 Markdown，全部处于未跟踪、未 stage 状态。写作前后：原 WAR-89 的 16 个文件 SHA 均相同；全仓已有 tracked diff（二进制形式）SHA 相同；staged diff SHA 相同；git status 原条目无移除，只增加本轮 WAR-89 输出。该比较不声称审计了全部外部未跟踪大素材的内容，但本轮工具写入目标只在明确授权的十个新文件。

没有 commit、push、stage、reset、checkout、stash、clean；没有更新 Linear，没有修改应用/Schema/API/服务/模型环境，没有启动 Canvas、Blender、ComfyUI/H3、图像/视频或真正 C/D/E LLM 实验。没有新增产品实现。所有交付尚未上传。

## 7. 文件 SHA-256

下表是七候选与两份证据的最终字节 SHA。**本说明自身的 SHA 在交付回复中列出**：完整文件不能把自身最终 SHA 嵌入自身而仍保持该 SHA，因此不制造自指校验值。复核时对十文件重新 sha256sum 即可。

| 文件（相对 WAR-89） | SHA-256 |
| --- | --- |
| `director-skill-v0-candidate/SKILL.md` | `3eee7d6f3c3032fc43e97b86a9606f8ae77943fa377aa2f56e2770c2b76e8676` |
| `director-skill-v0-candidate/references/knowledge-index.md` | `4d8edcb664659d78f897aa7baa8c1f275a57b5ff128ab433c95745b32a5e2519` |
| `director-skill-v0-candidate/references/review-method.md` | `72b23f163fe1fdea6a547d5b47f39392ba0b9b63b814a7a285db4a7df0e88e8e` |
| `director-skill-v0-candidate/stages/beat.md` | `6e81d45db1d0249cf33a200135f0ab790a49b65d92c7d036b0e253ac978121a1` |
| `director-skill-v0-candidate/stages/blocking.md` | `7619f6e10a2790c623fa4689f5d7e85c729de0384f34f025585888dcecbf625f` |
| `director-skill-v0-candidate/stages/intent.md` | `ac07ecb95cbd511888911a0f85aa08f5fee2824cbf8e23749ef0d6ffec065a38` |
| `director-skill-v0-candidate/stages/shot-plan.md` | `7a8aea0c5314ecc1dc95e258807ae9b0800582660adbd258d38bfb6438e4ea83` |
| `director-skill-v0-d-paper-walkthrough-20261114.md` | `0248d4e056bdfb8925a8df9d4552ba9ca9966de5e02d321afde0f2f299a5f5db` |
| `director-skill-v0-ce-minimal-text-cases-20261114.md` | `e34c4b7f9f70eb87193d2bbe16227d4b8ec5ba07229b4c9e3caf1d5a85b8b126` |

## 8. 请 ChatGPT 优先挑战

1. 客观插镜的明确性收益是否值得牺牲自然观察感？现有相邻视线设计是否足以避免把它误认为周的所见？
2. Blocking-r1 的动作分相有没有把无意遮挡演得刻意？不移 K 的前提下，蓝夹/纸叠与周路线的几何假设是否仍需另一个更稳妥候选？
3. 七文件是否真正提供不同专业判断，尤其 Shot 是否足以从观众任务落到可审核 construction，而非在运行时又退回术语堆积？
4. 单一活跃候选、虚拟 A 标记、未发生 B 与恢复污染边界是否明确；哪些内容适合进入后续最小文本对照，哪些须等真实媒体？

停在可审阅候选交付；安装、生产接入、正式模型对照与批准由后续决定。


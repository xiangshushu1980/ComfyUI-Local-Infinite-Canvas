# 按专业问题检索，不按七项填表

本索引是候选方法路由，非产品硬规则。先读下列独立稿对应编号；仍有判断缺口才回原始章节，读完能解释当前选择即停。以下路径均相对 `/home/sean/projects/canvas-lab`；根目录别名与后缀组合就是精确文件路径。静态 Skill 不存场景事实。

## 来源定位与许可边界

- **DS** = `docs/validation/XIA-33-actual-skill-comparison/director-skill-upstream/`。独立稿 `docs/planning/WAR-89/directorskill-directing-knowledge-v0.md` §3、§9；DS-D-xx 对应其 §9 表中的 D-xx。冻结 commit `c65ae0d14457053efb1e354c7e7f7e120d97fad1`，v2.1.0；本地 `LICENSE` 为 MIT，Copyright (c) 2026 wangzhang-wu。这里独立表述方法；日后实质复制须保留许可/版权声明。
- **TF** = `docs/validation/WAR-59/toonflow-upstream-v118workflow/references/`。独立稿 `docs/planning/WAR-89/toonflow-directing-knowledge-v0.md` §2。整合快照 commit `6086cdffceb704a632eca143dd16cd461a78cdac`，旧版映射见 `sourceMap.md`，不是无加工的旧版原 Skill。上游许可未核；仅索引/原创概括，不复制原 Prompt。具体旧版逐句归属未全核。
- **VM** = `docs/validation/XIA-59-shotplan/upstream/vimax/`。独立稿 `docs/planning/WAR-89/vimax-directing-knowledge-v0.md` §3–4。仅三文件冻结快照，上游 commit/许可未核；来源及文件 hash 以相邻 `../manifest.json` 为准。独立稿 camera 文件 hash 有笔误，见 `director-knowledge-decision-rules-v0.md` §5 末附注，勿从笔误推断版本。只借判断方法，不复制代码/Prompt。

## K1 — 事实与自由拍法

触发：接手故事，或新拍法改变知情、原话、物件、因果。任务：找明确事实与可自由细化处，判断是候选选择还是上游改写。主源 DS-01/02：DS `SKILL.md` §2 Script and subtext breakdown（L156 起）；信息差补 TF-01/02：TF `knowledge/scriptCraft.md` §故事核、矛盾与结构（L28）、§信息差、钩子与反转（L62）。停止：本轮依赖的事实与自由度已清楚，不遍历剧本创作流程。风险：DS/MIT；TF/许可及迁移归属缺口如上；源允许改编不授权改本项目故事。

## K2 — 认知差与声画因果

触发：先见后见、声音影响行为、回看或延迟揭示。任务：排角色/观众获得信息的不同时间，比较注意与误归因。主源 TF-02/11/15：TF `knowledge/scriptCraft.md` §信息差、钩子与反转；`knowledge/shotCraft.md` §审阅方法与本集落点（L123）；`knowledge/narrativeGenres.md` §悬疑推理（L31，仅实际有悬念时）。声音补 DS-23/24、DS-D-24/25：DS `references/sound-and-dialogue.md` §Sound is a directing decision（L7）、§Dialogue for AI video（L118）。停止：时序、声源和观看目标可核对，不继续加载类型词库。风险：TF 未核许可；DS/MIT；源数值混音/固定静默/反转频次不继承为硬要求。

## K3 — 整场政策与实质 Beat

触发：政策空泛、Beat 只随切镜划分、静止被当无变化。任务：分别回答全场表达为何一致、此段为何改变理解。主源 DS-03/04/05/06：DS `assets/beat-sheet-template.md` §What makes a beat a beat（L5）、§Pressure notation；`SKILL.md` §5 Director's book / visual treatment（L189）。情绪解释有缺口才补 TF-03：TF `knowledge/scriptCraft.md` §单集情绪、动作与台词（L112）。停止：边界有因果、政策能指导选择；无需写全 Director's Book。风险：DS/MIT、TF/许可未核；不继承压力分数、每 Beat 一镜或固定变化数量。

## K4 — 行动、眼线与遮挡

触发：关键微表演、接近/远离、道具交接、遮挡、跨切动作。任务：选择可演行动，展开决定性的中间状态，区分视线与注意。主源 DS-09/10/11/20/21、DS-D-10/12/13：DS `references/blocking-and-staging.md` §Depth staging（L246）、§Eyeline and attention（L266）、§Blocking notation（L276）；`references/continuity-bible.md` §Shot-to-shot continuity schema（L215）、§State-change ledger（L295）。表演补 TF-04：TF `knowledge/shotCraft.md` §分场与表演依据（L7）。停止：动作路径及未证空间条件已具体；不枚举调度图式。风险：DS/MIT、TF/许可未核；米数与模型可靠性是源启发，非真实几何。

## K5 — 观众任务、选镜与参考缺口

触发：线索与表演竞争、新角度/背面/文字、拍法有实质分歧。任务：比较关系镜、焦点、客观细节、反应或运动改变什么，指出素材支持范围。主源 DS-12/13/14、DS-D-01—07：DS `references/cinematic-language.md` §Shot functions（L18）、§Shot sizes（L34）、§Camera height and the objective/subjective ladder（L70）、§Focus as direction（L176）。补 TF-05/06/11：TF `knowledge/shotCraft.md` §镜头语法（L28）、§审阅方法与本集落点。仅参考缺口触发 VM-10/11/14：VM `camera_image_generator.py` 的 `system_prompt_template_select_reference_camera`（L20）、`missing_info`（L93）。停止：选定拍法及真替代代价、缺素材已明确，不启动 Camera Tree。风险：DS/MIT；TF 未核许可；VM 未核 commit/许可；覆盖判断不是像素/几何实测。

## K6 — 镜内时间与跨切延续

触发：瞬时显露、首尾相同但中间有事、动作切、声音抢先、阅读窗口。任务：核对起点—关键中间态—终点与邻镜接续，不预支完成/重复动作。主源 VM-05/06/07/08：VM `storyboard_artist.py` 的 `system_prompt_template_decompose_visual_description`（L73）。剪辑补 DS-18/19/25、DS-D-14/16/19/21：DS `references/editing-and-assembly.md` §Cut motivation taxonomy、§The hard-cut agreement checklist、§Pacing math；声音补 DS `references/sound-and-dialogue.md` §The continuity-glue rule（L19）。停止：动作/声画相对时点与未证容量已明确，不强制制作 FF/LF。风险：VM commit/许可未核；DS/MIT；源允许合理补充不授权新增故事，连续环境声不修复状态错误。

## K7 — 双向覆盖与实际修订

触发：阶段交接/局部返回，整场 B。任务：故事→实际镜头查遗漏，镜头→来源查越界；区分建议、实际改动、复检。主源 DS-20/21/31：DS `references/continuity-bible.md` §State-change ledger；`assets/qc-checklist.md` §Gate 3 — SEQUENCE（L79）、§From a failed row to a repair（L117）。补 TF-16：TF `knowledge/shotCraft.md` §审阅方法与本集落点。停止：局部影响明确则交接；B 须全场反查完并呈现未证才可建议提交。风险：DS/MIT、TF 未核许可；源评分门槛和 Canvas 写回流程不继承，专业审阅不是用户 Decision。

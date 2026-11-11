# WAR-66 · ViMax 镜头拆解与 Camera Tree 机制研究

任务：[WAR-66](https://linear.app/xiangshushu/issue/WAR-66)，父任务 [WAR-59](https://linear.app/xiangshushu/issue/WAR-59)。

## 当前目标与验收（2026-11-11 缩减范围）

不再将 ViMax 当作与 Toonflow、DirectorSKILL 同类型的第三套完整导演 Skill 进行 C/D/E 三剧本实测。聚焦 ViMax 如何将 Shot/Storyboard 转化为 FF/Motion/LF 执行描述，以及如何用 Camera Tree 组织机位与参考图依赖；判断它与 Shot Plan、Blocking、Continuity 的职责与重叠及 Canvas Lab 借鉴价值。

验收：
1. 依据已有冻结源码和 Prompt，确认 Storyboard → Shot Decomposition → Camera Tree 的输入输出、规则、数据流和图像生成链路（后者仅源码分析）。
2. 解释 Camera Tree 的 parent camera/shot、覆盖与缺失信息判断，以及与跨镜剧情状态账本、真实空间几何验证的区别；区分已读源码、模型预测与尚未验证。
3. 提供 Shot Plan / Blocking / 连续性检查 vs FF/Motion/LF / Camera Tree 的简短职责映射和 Canvas Lab 建议，向 WAR-59 汇总。

## 执行边界

- 取消原定 C/D/E 全量模型回放、跨样本 ViMax 评审及以此为前提的完整 Python 环境/Codex CLI 适配；不为形式对称而实跑。
- 首先复用 Eric 的源码快照和 WAR-57 研究；不自动部署 ViMax、下载依赖、调用外部付费 API。
- 如源码不能回答关键问题，可提议仅用 C 的一个代表镜头进行有界文本试验，待用户决定；试验不是当前验收必需项，也不能伪称原版 Python 管线运行。
- 不生成图片/视频、不调用 GPU/H3、不修改 ViMax、Canvas/ComfyUI、不覆盖冻结证据。
- FF/Motion/LF 是单镜头内部拆解；Camera Tree 是机位/参考图依赖，不等于跨镜剧情状态账本或真实几何校验。

## 已完成与保留证据

- preflight-review.md：源码与 plan_text_artifacts 预检、依赖边界。其原有「下一步完整运行」建议已由本次缩减决定替代，历史不修改。
- preflight-manifest.json：三个上游 Python 快照 SHA 与环境检查；上游准确 Git commit 尚未冻结。
- c-original-v1/script-C-frozen.txt：剧本 C 冻结输入，SHA-256 ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d；保留作证据和可选示例，不意味着要实跑。
- 原预检冻结提交 010b1f6941bdf0cdcf6c257d6cfc3cba24377150；没有生成任何本次 ViMax LLM 输出。
- 源码位置 docs/validation/XIA-59-shotplan/upstream/vimax/；上游 manifest 为 docs/validation/XIA-59-shotplan/upstream/manifest.json。
- 跨项目参考 docs/planning/ai-filmmaking-open-source-directing-review.md；关联 WAR-61 和 WAR-65。

## 下一步

按缺口补齐针对性源码机制分析，形成职责映射和选用建议，随后交 WAR-59 综合讨论。确需模型输出时另议一个镜头试验，不自动恢复 C/D/E 实跑。

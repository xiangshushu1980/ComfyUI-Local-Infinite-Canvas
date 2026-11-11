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
- 用户已授权 C 三镜最小文本实验；使用 Codex CLI 回放原版 Shot Decomposition 与 Camera Tree Prompt（有单次批量包装及 JSON Schema 适配），不是原版 Python Pipeline。原始输入、输出、日志与 SHA 全部归档。
- 不生成图片/视频、不调用 GPU/H3、不修改 ViMax、Canvas/ComfyUI、不覆盖冻结证据。
- FF/Motion/LF 是单镜头内部拆解；Camera Tree 是机位/参考图依赖，不等于跨镜剧情状态账本或真实几何校验。

## 已完成与保留证据

- preflight-review.md：源码与 plan_text_artifacts 预检、依赖边界。其原有「下一步完整运行」建议已由本次缩减决定替代，历史不修改。
- preflight-manifest.json：三个上游 Python 快照 SHA 与环境检查；上游准确 Git commit 尚未冻结。
- c-original-v1/script-C-frozen.txt：剧本 C 冻结输入，SHA-256 ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d；保留作证据和可选示例，不意味着要实跑。
- 原预检冻结提交 010b1f6941bdf0cdcf6c257d6cfc3cba24377150；没有生成任何本次 ViMax LLM 输出。
- 源码位置 docs/validation/XIA-59-shotplan/upstream/vimax/；上游 manifest 为 docs/validation/XIA-59-shotplan/upstream/manifest.json。
- 跨项目参考 docs/planning/ai-filmmaking-open-source-directing-review.md；关联 WAR-61 和 WAR-65。

## 最小文本测试（2026-11-11）

- `minimal-C-text-v1/REVIEW.md`：三镜 FF/Motion/LF 与 Camera Tree 观察、职责映射及限制。
- `minimal-C-text-v1/`：冻结的三镜候选、Prompt 消息、Schema、原始输出、Codex JSONL、stderr、执行条件和 SHA 清单；两阶段退出码均为 0。
- 模型：Eric Codex CLI 0.166.0 / gpt-6.1-terra / medium / ephemeral / read-only。三镜分解聚合成一次调用，不可等同 ViMax 原版逐镜调用；Camera Tree 单独一次。

## 独立调用复核（2026-11-11）

- `minimal-C-independent-v1/REVIEW.md`：三镜分别调用与此前集中调用的逐镜对照、越界动作及状态时序问题、适配差异、因果限制。
- `minimal-C-independent-v1/shot-{0,1,2}/`：逐镜完整请求/输出、调用日志与执行信息；总 SHA：`minimal-C-independent-v1/sha256-manifest.json`；可复现脚本 `independent_C_runner.py`。
- 观察：独立 Shot 0 增加未授权离场动作且未反映至 LF；Shot 1/2 首帧与 Motion 部分动作重复；两种调用方式均保留主要持票/离场状态。单轮观察**不能证明集中调用更好**，更不能单独归因于单镜提示词专业度。

## 下一步

已完成集中回放与三镜独立回放，审阅两个 REVIEW.md 后进入 WAR-59 综合讨论；不自动恢复 C/D/E 实跑或生成媒体。

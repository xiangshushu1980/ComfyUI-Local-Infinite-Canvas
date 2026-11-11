# WAR-66 · ViMax 原版多剧本文本观察

任务：[WAR-66](https://linear.app/xiangshushu/issue/WAR-66)；父任务：[WAR-59](https://linear.app/xiangshushu/issue/WAR-59)。

## 研究入口与边界

- 研究目标与验收、当前下一步以 WAR-66 Issue 当前正文为准。
- 前置源码依据：[WAR-57](https://linear.app/xiangshushu/issue/WAR-57)；本仓库 `docs/planning/ai-filmmaking-open-source-directing-review.md`。
- 目标是复用原版 ViMax 的 Storyboard → FF/Motion/LF 分解 → Camera Tree 文本规划；优先核对真实 `plan_text_artifacts` 入口与依赖，禁止自定义模拟冒充原版执行。
- 测试 C《没说出口》、D《错过的钥匙》、E《最后一张照片》，先逐一核对冻结原剧本、创作意图与输入条件。不得将 D 的 DirectorSKILL 专属辅助空间/人物设定无声加入 ViMax。
- 只观察，先不修改/扩展 Skill；不执行 GPU、图片、参考图渲染或 H3。所有原始输入、输出、日志、SHA 留本目录，新证据不可覆盖。
- ViMax 研究完成后，由 WAR-59 汇总 Toonflow、DirectorSKILL、ViMax 的阶段职责、中间产物和未证实范围，用户再决定下一阶段。暂不启动 Native 多路对照。

## 当前状态

仅创建任务与权威研究目录；**ViMax 新实验尚未运行**。开始执行时先核验代码版本、原始文本管线能否运行以及 C 样本的冻结来源。

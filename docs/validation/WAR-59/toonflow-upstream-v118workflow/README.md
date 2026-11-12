# Toonflow v1.1.8 原始 Skill 与知识库完整快照

> **研究存档，不是部署的 Skill。** Eric：`/home/sean/projects/canvas-lab`。本目录位于 `docs/validation/WAR-59/`，不属于翻译学习目录 `docs/study/`，不允许以本快照直接操作项目画布或发起生成。

## 源码与版本

- 上游：[HBAI-Ltd/Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app)，子目录 `packages/skills/v118workflow/`。
- 固定 Git commit：`6086cdffceb704a632eca143dd16cd461a78cdac`（不使用浮动 `master`）。
- 原始 Markdown **23 份**（`SKILL.md` 1、`references/` 普通文件 15、`references/knowledge/` 7），共 **238,783 字节**。
- [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json)：文件路径、字节数、SHA-256、精确到 commit 的原始 URL；全部文件写入后已按字节回读校验。
- 与 XIA-59 已冻结的 `directorPlan.md`、`storyboardTable.md`、`shotCraft.md` **逐字节一致**。原始冻结目录 `docs/validation/XIA-59-shotplan/upstream/toonflow/` 未修改；该目录属于历史实验独立快照。
- 本目录的目录结构与上游一致，内部引用的相对路径可按原样追踪。未运行 Toonflow App、未修改 Skill 原文，也未运行任何生成流程。

## 阅读入口（围绕故事理解 → 导演意图）

| 顺序 | 文件 | 阅读目标 |
| --- | --- | --- |
| 1 | [SKILL.md](SKILL.md) | 整体制作阶段、确认关口与按需加载知识的机制 |
| 2 | [scriptCraft.md](references/knowledge/scriptCraft.md) | 故事核、冲突、人物关系、信息差、改编方法 |
| 3 | [narrativeGenres.md](references/knowledge/narrativeGenres.md) | 十二类叙事的类型专属表现方法，需先由创作阶段确认类型 |
| 4 | [storySkeleton.md](references/storySkeleton.md) → [episodeScript.md](references/episodeScript.md) | 上游剧本/分集的来源、产物与确认机制 |
| 5 | [directorPlan.md](references/directorPlan.md) | 单集分场、情绪、表演、场间衔接 |
| 6 | [shotCraft.md](references/knowledge/shotCraft.md) → [storyboardTable.md](references/storyboardTable.md) | 从导演规划到镜头表达，镜头与连续性方法 |

其他知识：[visualStyles.md](references/knowledge/visualStyles.md)、[assetDesign.md](references/knowledge/assetDesign.md)、[imagePromptCraft.md](references/knowledge/imagePromptCraft.md)、[videoPromptCraft.md](references/knowledge/videoPromptCraft.md)。

## 画布与宿主 API（不是导演理论）

[canvasOperations.md](references/canvasOperations.md) 规定了 Toonflow 宿主中 `getCanvas`、`switchCanvas`、`getCanvasNodes`、`addNode`、`node:setText`、生成节点与回读确认的操作契约。它是**产品实现与持久化接口**，不可直接推断 Canvas Lab 的 API 具有相同语义；不应将其执行指令当成本次只读研究的授权。

## 使用边界与此前研究的关系

1. 旧 WAR-61 C/D/E 的 Toonflow 结果来自**隔离文本回放**，不等于本完整 Skill 在原生画布宿主中端到端运行；此次补全不追溯改变旧实验的模型输入、技能规则或验收性质。
2. 故事理解不能仅根据 `directorPlan.md` 判断。Toonflow 上游还有 `scriptCraft.md`、`narrativeGenres.md` 和故事骨架/剧本阶段的编排规则；应区分**被引用的知识存在**与**旧实验实际加载过该知识**。
3. 原始文档保留中文，不制作第二套 study 副本；阅读时直接打开上述链接。目录内的原文视为冻结的上游研究材料，后续升级应另建版本而不是直接覆盖。

关联：[WAR-59 三技能综合研究](../three-method-synthesis-20261111.md) · [WAR-61 Toonflow 文本观察](../../WAR-61/README.md)。

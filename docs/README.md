# Canvas Lab 文档入口

> 本目录是当前 Rebuild 工作树的资料导航；项目实际状态以当前源码、Git diff 与新鲜验证为准。历史报告里的 HEAD/运行结果不可自动继承。根目录 README 含参考 fork 内容，不应当作本机验收记录。

## Agent 快速入口

- **代码定位、画布与 Gateway**：[当前代码地图](current-code-map.md) → [架构与工作流](architecture/README.md)
- **Canvas Agent、MCP 与 Skill**：[Agent 与上下文](agent/README.md)
- **H3 提示词、模型与生成工作流**：[工作流接入审查](workflow-integration-audit.md) → [Gateway H3 Skill](../comfyui-gateway/prompts/skills/h3-prompt-writing/SKILL.md) → [本地 H3 LoRA 说明](../comfyui-gateway/prompts/h3-lora/README.md)
- **WSL 部署与排障**：[运行边界](runtime-boundary.md) → [验证与操作](validation/README.md)
- **需求取舍与实施计划**：[规划与决策](planning/README.md)
- **旧方案、来源和历史研究**：[历史研究](history/README.md)

## 分类目录

| 类别 | 入口 | 主要用途 |
| --- | --- | --- |
| Agent 与上下文 | [agent/](agent/README.md) | Agent 职责、CodeGraph、Codex、记忆边界 |
| 架构与工作流 | [architecture/](architecture/README.md) | 代码调用链、Gateway、工作流与资源 |
| 验证与操作 | [validation/](validation/README.md) | 证据矩阵、WSL 验证、已有改动 |
| 规划与决策 | [planning/](planning/README.md) | 功能取舍、阶段计划、Git 基线 |
| 历史研究 | [history/](history/README.md) | 旧项目来源，非当前实现事实 |

## 最小读取规则

1. 先读根目录 [AGENTS.md](../AGENTS.md) 的约束；随后按任务选择上方一个分类。
2. 定位源码时优先查 `.codegraph/`（确认索引新鲜度），然后只打开相关文件；不要一次性读取整个 `docs/`。
3. 当前行为以源码、当前 Git diff、测试与运行实测为准。静态审查、规划、旧版本说明不能替代运行验收。
4. 改动前先检查 `git status` 与相关 diff；不得因整理文档覆盖已有未提交工作。
5. 用户级 `project-memory` 管理长期知识；本仓库保留项目专属决策与可复核证据。

## 维护约定

新增资料优先挂入对应分类入口；无需为短期调查重复创建总览。现有根级 `docs/*.md` 暂不迁移，以保持历史链接稳定。后续仅在引用清点和迁移测试完成后再做实体迁移。

## 关于版本

- [restart-baseline.md](restart-baseline.md) 是起点与历史工作树记录，不是自动更新的 HEAD 状态。
- [ARCHITECTURE.md](ARCHITECTURE.md) 属参考 fork 旧版本架构说明，不代表当前 WSL 部署事实。
- 旧项目 `/home/sean/projects/canvas-lab-backup/docs/` 仅可作为带来源的研究参考。

# Canvas Lab Rebuild — 文档入口

> 本目录记录新工作树的当前结论和验证证据；根目录 `README.md` 仍为 fork 参考项目说明，不代表本项目已完成验证。

> 当前项目目录为 `/home/sean/projects/canvas-lib`。历史审查中的目录、分支、HEAD 和运行结果按其记录日期理解；当前 Git 快照见 [起点与 Git 基线](restart-baseline.md)，不能把历史验证视为当前 HEAD 的重新验证。

## 开始阅读
- [起点与 Git 基线](restart-baseline.md)：当前代码来源、版本、未提交修改边界。
- [功能审查](feature-audit.md)：保留、适配、剥离候选及依赖风险。
- [核心链路静态定位](source-path-audit.md)：画布、Gateway、ComfyUI 与回写的文件级调用链。
- [Agent 职责审查](agent-boundary-audit.md)：Canvas Agent 与源码修复助手的边界。
- [WSL 验证协议](wsl-validation-protocol.md)：测试命令、副作用、分层验收。
- [Project Memory 接入核查](project-memory-audit.md)：用户级技能、Hindsight 服务健康和未完成的 bank 归属。
- [验证矩阵](validation-matrix.md)：哪些仅存在于源码，哪些实际测试通过。
- [运行环境边界](runtime-boundary.md)：纯 WSL 部署、Gateway 和 ComfyUI 的安全约束。
- [分阶段计划](rebuild-plan.md)：阶段、完成条件与回滚要求。
- [知识归属](knowledge-governance.md)：仅记录本项目特定的文档/历史来源约定；常规管理由用户级 `project-memory` Skill 执行。
- [旧项目来源索引](legacy-source-index.md)：按保留、摘录、拒绝继承的方式归类历史研究。
- [内置资源安装安全审查](resource-install-audit.md)：资源来源固定、校验、安装副作用与 WSL 兼容性的静态审查（XIA-27）。
- [自有工作流接入审查](workflow-integration-audit.md)：Registry 与自由工作流路径，以及 H3 样本适配边界（XIA-28）。

## 历史与证据
- [ARCHITECTURE.md](ARCHITECTURE.md) 是参考 fork **v0.22.12 的历史说明**，不是当前实现权威。
- 旧项目 `/home/sean/projects/canvas-lab/docs/` 是历史研究来源，不共享可编辑的当前基线。
- 代码及 Git 状态优先于 README 声明；当前机器实测须单独记录 commit、环境、命令和结果。

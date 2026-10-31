# Canvas Lab Rebuild — 文档入口

> 本目录记录新工作树的当前结论和验证证据；根目录 `README.md` 仍为 fork 参考项目说明，不代表本项目已完成验证。

## 开始阅读
- [起点与 Git 基线](restart-baseline.md)：当前代码来源、版本、未提交修改边界。
- [功能审查](feature-audit.md)：保留、适配、剥离候选及依赖风险。
- [核心链路静态定位](source-path-audit.md)：文件级入口；需要进一步代码审查和测试。
- [验证矩阵](validation-matrix.md)：哪些仅存在于源码，哪些实际测试通过。
- [运行环境边界](runtime-boundary.md)：纯 WSL 部署、Gateway 和 ComfyUI 的安全约束。
- [分阶段计划](rebuild-plan.md)：阶段、完成条件与回滚要求。
- [知识归属](knowledge-governance.md)：仅记录本项目特定的文档/历史来源约定；常规管理由用户级 `project-memory` Skill 执行。

## 历史与证据
- [ARCHITECTURE.md](ARCHITECTURE.md) 是参考 fork **v0.22.12 的历史说明**，不是当前实现权威。
- 旧项目 `/home/sean/projects/canvas-lab/docs/` 是历史研究来源，不共享可编辑的当前基线。
- 代码及 Git 状态优先于 README 声明；当前机器实测须单独记录 commit、环境、命令和结果。

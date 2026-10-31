# Canvas Lab rebuild worktree

- This project starts from the `ComfyUI-Local-Infinite-Canvas` reference repository, not from the upstream-derived `/home/sean/projects/canvas-lab` implementation.
- The current goal is to test the reference project and selectively strip/adapt it. Keep conclusions tied to the checkout and commit being examined.
- Use the local CodeGraph index (`.codegraph/`) before searching or reading code when it covers the question. Refresh it after source changes when needed.
- Read `docs/restart-baseline.md` for the starting commit, carried-over changes, and the relationship to the updated Canvas Lab documents.
- Do not treat old Canvas Lab stage plans or the current upstream-derived worktree as implementation truth for this project.
- Consult `docs/feature-audit.md`, `docs/validation-matrix.md`, and `docs/rebuild-plan.md` for current review decisions, verification status, and sequencing. These documents are planning evidence, not proof of runtime success.
- This project deploys entirely in WSL. The reference Windows launcher is not the deployment entrypoint. Before deleting or replacing a module, inspect CodeGraph impact/callers and confirm in source; record tests and rollback. Do not modify application code, dependencies, services, GPU workflows, or the existing ComfyUI environment without explicit authorization.

## Development agent workflow

- **Project Memory**：使用用户级 `project-memory` 统一管理项目文档、Git 知识记录、Hindsight 经验积累与上下文恢复，按需加载其参考资料，不重复建立文档或记忆管理机制。
- **Linear**: Use the available user-level Linear integration for this Rebuild project's tasks, progress and acceptance; the `linear-local-agent-pilot` skill is for bounded local-agent pilots, not general project management. Do not reuse the old Infinite Canvas project's completion status.

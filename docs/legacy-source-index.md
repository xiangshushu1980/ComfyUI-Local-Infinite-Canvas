# XIA-21 — 旧 Canvas Lab 文档来源索引

> 2026-11-01，只读检查旧项目文件头与版本声明。旧项目原件不移动、不改写；仅建立新项目引用索引。当前新项目源码以本仓库 HEAD 为准。

| 原始文档（相对于 `/home/sean/projects/canvas-lab-backup/`） | 历史依据 | 处理方式 | 边界 |
|---|---|---|---|
| `docs/design/product-brief.md` | 2026-10-28，早期目标草图 | **摘录候选**：AI 影片创作目标、角色/场景/镜头/素材概念；需逐项确认 | 产品愿景，不证明已有实现；当前目标以项目说明为准 |
| `docs/research/comfyui-local-infinite-canvas.md` | v0.21.0 / `3f7ec94`，2026-10-28～29 研究与隔离验证 | **保留原处并引用** | 旧参考版本及旧环境；不得作为 v0.24.0 运行证据 |
| `docs/research/local-infinite-canvas-development-notes.md` | 2026-10-29，旧参考 v0.21.0 | **摘录候选**：共享画布、Agent 与 Gateway 的历史问题 | 经验需按当前源码重新验证 |
| `docs/research/canvas-lab-lineage-module-map-2026-10-31.md` | 2026-10-31，含旧项目 HEAD 与参考 7d4f558 | **保留原处并引用** | 版本关系研究，当前架构以新仓库为准 |
| `docs/design/comfyui-multi-workflow-architecture-draft-2026-10-31.md` | 2026-10-31 未实施设计建议 | **仅研究参考，不迁移为方案** | 先复用本 fork Registry/Bindings，避免重建旧 Adapter |
| `docs/design/infinite-canvas-milestones-2026-10-31.md` | 旧项目已批准计划重排 | **不迁移** | 旧任务/里程碑状态不适用于 Rebuild |
| `docs/design/workflow-integration-redesign-handoff-2026-10-31.md` | 旧项目交接 | **保留原处** | 不作为本项目实施授权或新阶段状态 |
| `docs/design/m2-code-review-fixes-handoff-2026-10-31.md` | 旧项目交接 | **保留原处** | 不能无差别应用旧补丁 |
| `docs/research/product-observations.md`、`docs/Tapnow_无限画布与Agent协作研究_实操增补版.md` | 旧研究，版本/证据逐条核对 | **按需摘录** | 外部产品观察，不等于当前 Rebuild 功能 |

## 迁移原则
- 当前项目文档 [README](README.md)、[功能审查](feature-audit.md)、[验证矩阵](validation-matrix.md) 已记录经本轮确认的部分事实；不批量复制旧文档。
- 需要使用某条旧经验时，引用旧路径、日期和对应 commit，再查本项目源码/运行证据。历史用户验收属于历史环境，不自动继承。
- 旧文件不在本次任务中改变；本索引本身不是内容迁移或批准实施记录。

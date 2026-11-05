# Restart baseline

## Purpose

At initialization, this worktree was the separate reference-based route for testing and selectively adapting `ComfyUI-Local-Infinite-Canvas`; the upstream-derived route was then at `/home/sean/projects/canvas-lab`. That upstream-derived worktree and its archived documents have since moved to `/home/sean/projects/canvas-lab-backup`.

## Starting point

- Source repository: `1314521gjy/ComfyUI-Local-Infinite-Canvas`
- Starting commit: `9e6d56bc904851b218230aedd763ac32671727ad` (`release: v0.23.1 add on-demand canvas repair agent`)
- Source branch: `origin/main`
- Project branch at initialization: `codex/canvas-lab-rebuild-latest`
- Initial directory: `/home/sean/projects/canvas-lab-rebuild`
- Two pre-existing uncommitted Gateway source changes from the previous local reference worktree are carried over: `comfyui-gateway/prompts/image-prompt-enhance.json` and `comfyui-gateway/src/prompt-optimizer.js`.
- Rebuilt `infinite-canvas/web/dist` assets were not copied; they are generated output, not the source baseline.

The source branch was fetched from the configured fork remote immediately before initialization. The older local-only commit `7d4f558` was retained in a separate worktree for rollback/comparison at that time; it was later reviewed and its UI functionality was already present in the current main baseline.

## Current checkout confirmation (2026-10-31)

- Merge commit: `ecd2cbf14ff47f702437553580a42cf8236808c8` (merged `origin/main` at `559e97ddf1e022041cc142ff70b2f753dc532490`, v0.24.0).
- Actual branch reported by Git: `codex/canvas-lab-rebuild` (the earlier starting-point branch name above records initialization history).
- The v0.24.0 source changes merged cleanly from upstream commits `aaccfaf7` and `559e97d`; review summary is recorded in `feature-audit.md`.
- Existing uncommitted modifications remain in `comfyui-gateway/prompts/image-prompt-enhance.json` and `comfyui-gateway/src/prompt-optimizer.js`; both were preserved outside the merge commit.
- Upstream-generated `infinite-canvas/web/dist` artifacts were excluded from the merge; afterward the tracked dist was regenerated with local Vite 8 from the merged source.
- `.codegraph/` is untracked; index reported up to date. Do not confuse the local index with application test evidence.
- See `feature-audit.md`, `validation-matrix.md`, and `rebuild-plan.md` for this worktree's new review and verification records.

## Fork main baseline (2026-11-01)

- The retained working checkout is the fork's `main` branch at `2585d89b005b4694921937db108efeb68e10c341`, tracking `origin/main` on `xiangshushu1980/ComfyUI-Local-Infinite-Canvas`.
- The old reference checkout and comparison checkout were removed after reviewing their unique local changes. The older Agent-panel commit is superseded by the current `main` UI; generated `dist` assets and CodeGraph indexes were not retained as source changes.
- Ongoing changes to preserve on this fork are committed directly to `main` and pushed to `origin` after review.

## Directory move record (2026-11-01)

- Project root at the time of this record: `/home/sean/projects/canvas-lib` (path recorded from the then-current project-local instructions; it was incorrect).
- Branch at the time: `main`; HEAD `0d5fee308fbee420fb973910bde501f089398060` (`[审查] 归档资源与工作流审查结论`), matching `origin/main` at inspection time.
- Tracked working tree was clean at that inspection. `.codegraph/` was an untracked local index, not an application source change; `codegraph status` reported the index up to date (872 files, 23,491 nodes, 64,074 edges).
- Older paths and branch names above are initialization/history records, not current checkout metadata. Runtime and audit results elsewhere in this directory remain dated evidence and were not rerun by this path/Git check.

## Current project path (2026-11-01)

- Current project root: `/home/sean/projects/canvas-lab`.
- The upstream-derived Canvas Lab worktree and its archived documents are at `/home/sean/projects/canvas-lab-backup`; this reference-based Rebuild worktree is separate.
- Branch, HEAD, and working-tree state are time-sensitive; check Git directly instead of treating older snapshots above as current state.

## CodeGraph

Initialized for this worktree on 2026-10-31. Check the current index with `codegraph status`; sync or rebuild it after relevant code changes.

## Documentation relationship

The updated product and lineage documents are archived under `/home/sean/projects/canvas-lab-backup/docs`. They are context for deciding what to test and preserve; their upstream-derived phase status is not automatically the current state of this reference-based worktree. Keep test evidence and new decisions with this project when they become concrete. The current project root is `/home/sean/projects/canvas-lab`; references above to `/home/sean/projects/canvas-lab-rebuild` describe the earlier location.

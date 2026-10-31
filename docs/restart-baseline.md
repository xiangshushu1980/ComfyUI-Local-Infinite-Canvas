# Restart baseline

## Purpose

This worktree is the separate reference-based route for testing and selectively adapting `ComfyUI-Local-Infinite-Canvas`. The existing `/home/sean/projects/canvas-lab` remains the upstream-derived route and is preserved for comparison.

## Starting point

- Source repository: `1314521gjy/ComfyUI-Local-Infinite-Canvas`
- Starting commit: `9e6d56bc904851b218230aedd763ac32671727ad` (`release: v0.23.1 add on-demand canvas repair agent`)
- Source branch: `origin/main`
- Project branch: `codex/canvas-lab-rebuild-latest`
- Initial directory: `/home/sean/projects/canvas-lab-rebuild`
- Two pre-existing uncommitted Gateway source changes from the previous local reference worktree are carried over: `comfyui-gateway/prompts/image-prompt-enhance.json` and `comfyui-gateway/src/prompt-optimizer.js`.
- Rebuilt `infinite-canvas/web/dist` assets were not copied; they are generated output, not the source baseline.

The source branch was fetched from the configured fork remote immediately before initialization. The older local-only commit `7d4f558` is retained in a separate worktree for rollback/comparison and is not part of this latest-fork base.

## Current checkout confirmation (2026-10-31)

- Merge commit: `ecd2cbf14ff47f702437553580a42cf8236808c8` (merged `origin/main` at `559e97ddf1e022041cc142ff70b2f753dc532490`, v0.24.0).
- Actual branch reported by Git: `codex/canvas-lab-rebuild` (the earlier starting-point branch name above records initialization history).
- The v0.24.0 source changes merged cleanly from upstream commits `aaccfaf7` and `559e97d`; review summary is recorded in `feature-audit.md`.
- Existing uncommitted modifications remain in `comfyui-gateway/prompts/image-prompt-enhance.json` and `comfyui-gateway/src/prompt-optimizer.js`; both were preserved outside the merge commit.
- Upstream-generated `infinite-canvas/web/dist` artifacts were excluded from the merge; afterward the tracked dist was regenerated with local Vite 8 from the merged source.
- `.codegraph/` is untracked; index reported up to date. Do not confuse the local index with application test evidence.
- See `feature-audit.md`, `validation-matrix.md`, and `rebuild-plan.md` for this worktree's new review and verification records.

## CodeGraph

Initialized for this worktree on 2026-10-31. Check the current index with `codegraph status`; sync or rebuild it after relevant code changes.

## Documentation relationship

The updated product and lineage documents remain in `/home/sean/projects/canvas-lab/docs`. They are context for deciding what to test and preserve; their upstream-derived phase status is not automatically the current state of this reference-based worktree. Keep test evidence and new decisions with this project when they become concrete.

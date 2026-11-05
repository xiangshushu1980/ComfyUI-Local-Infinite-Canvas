# XIA-47 PoseAtlas × Canvas Lab P1 验收记录

日期：2026-11-05。主工程：`/home/sean/projects/canvas-lab`；ComfyUI：`/home/sean/projects/ComfyUI`。

## 目标与实现

- 复用用户自行安装的 PoseAtlas 图集，而不是复制受版权保护的素材到 Canvas 仓库。
- ComfyUI Gateway：`GET /api/poseatlas/search`（分页、分类、关键词）、`GET /api/poseatlas/asset/:index/:variant`（只允许索引中指定的缩略图和原图；不接受任意路径）。
- 无限画布工具栏增加 PoseAtlas 入口，支持搜索、浏览姿势/服饰/肖像、选图插入为已有图片节点，以及替换单选图片节点。
- 图片节点 metadata 的 `poseAtlas` 保存 `index`、`id`、`collection`、`label`；实际图片通过已有 `uploadImage` 和 Canvas 节点存储机制进行本地持久化，后续镜头可直接用已有图片引用链路。
- 深度图不通过 API 进行批量抓取。图集不存在或原图尚未下载时，UI 显示不可用或禁用选择，不悄悄以低清缩略图作为原图。

## 证据

- Gateway: `curl http://127.0.0.1:8190/api/poseatlas/search?collection=pose&q=敬礼` 返回 5 个结果；`asset/864/full` 返回 HTTP 200 (543,549 bytes)；`asset/864/thumb` 返回 HTTP 200；越界索引返回 404。
- Gateway Node 单测：`node --test test/pose-atlas.test.js`：2 passed，覆盖搜索/分页和路径安全。
- Vite 开发服务：`/src/components/canvas/pose-atlas-picker-modal.tsx` 及 `/src/pages/canvas/project.tsx` 均 HTTP 200。
- 独立 Playwright 测试浏览器（session `poseatlas-p1`）访问 `http://127.0.0.1:3000/canvas`；建立测试画布；工具栏出现“PoseAtlas 参考图库”。
- 在模态框中搜索“敬礼姿势”显示 5 条；插入“[上半身] 可爱系 / P021 敬礼姿势 / 正面”后画布显示图片节点；刷新后图片仍在。
- 单选该图片节点，选择“替换选中图片”，替换为“[性感全身] 站姿 / P001 S形站姿・胯部侧顶 / 正面”；刷新后新图片仍在。
- `tsc --noEmit` 在当前主工程报告一处**既有**错误：`canvas-node.tsx(128,5): Property 'onViewImage' does not exist on type 'CanvasNodeProps'`；`git show HEAD` 中已有该属性用法，并非本次 PoseAtlas 改动引入。本次新增模块未产生新 TypeScript 诊断。
- `git diff --check` 无错误。Git 当前有其他任务并行更新的文档和资源，未触碰这些文件。

## 未完成与边界

- 本阶段使用已有图片节点而非新建独立的 Reference Asset 类型；后续根据镜头使用体验再决定新类型是否必要。
- 画布 UI 已实测插入、替换和刷新持久化；尚未实测 Canvas Agent 自动调用或 H3 控制图生成，分别属于 P2/P3。
- 图库资源在本地 ComfyUI 中，不可作为公开产品资源包转载或再分发；深度原图必须按需获取。

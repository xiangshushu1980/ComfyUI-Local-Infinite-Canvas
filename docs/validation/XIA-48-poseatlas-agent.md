# XIA-48｜Canvas Agent × PoseAtlas P2 端到端验收

日期：2026-11-05。工程：`/home/sean/projects/canvas-lab`。

## 范围

通过已有 Canvas Agent 的 MCP → HTTP → browser bridge 路由新增 3 个工具：
- `pose_atlas_search`：分类 pose/costume/portrait、中文/英文/日文关键词、视角 angle、上游 first/second 分类 key 与候选评分及 top N；无匹配时返回 0，不虚构条目。
- `pose_atlas_get`：按 index 精确取回中/英/日名称、类别、当前方向、同姿势其他视角以及线稿/深度资源可用性。
- `pose_atlas_insert`：按 index 加载本地 Gateway 的原图；通过 Canvas 浏览器 `uploadImage` → `imageMetadata` → `CanvasAgentOp` 创建真实图片节点，或按明确的 replaceNodeId 替换单图节点。保留 poseAtlas {index,id,collection,label,render} 来源元数据。其他画布不会被改写。

Agent 指令规定：先 search，必要时 get 确认，用户明确要求后才能 insert；深度资源不存在则报错，不批量下载；替换需要先读画布节点 ID。

## API / MCP 实测

- Gateway `GET /api/poseatlas/semantic-search?query=敬礼` 返回 upper80v2_P021 五角度；`GET /api/poseatlas/item/866` 返回中/英/日名称、series/category、side 方向和全组 5 种 angle 的索引。
- 当前运行中的 Agent `POST /api/tools` 实际调用 `pose_atlas_search({query:"敬礼",angle:"side"})` 返回 **index=866** 唯一结果，随后 `pose_atlas_get({index:866})` 返回准确详情。
- Agent 实测英文 Salute、日文 敬礼ポーズ、中文 敬礼均返回相同 pose ID；不存在关键词返回 0。
- 独立 MCP stdio client `tools/list`：37 个工具，其中新增 3 个 pose_atlas_*；`tools/call` 实际执行 search("Salute",side) 与 get(866) 正常返回。
- `pose_atlas_insert({index:999999})` 报条目不存在；`pose_atlas_insert({index:864,render:"depth"})` 报深度原图未下载，且不修改目标画布。

## 真正画布插入和持久化实测

- 使用隔离 Playwright 浏览器新建测试画布 `qU0GR8vZztYPWPg6sZSnY`，连接到 Agent 127.0.0.1:17373；通过 `canvas_get_state` 确认目标为该空画布，而非用户其他活动画布。
- 通过 Agent HTTP 工具 `pose_atlas_insert({index:864,render:"line"})` 完成真实插入，返回 `nodeId=image-wLGaQHTeW0Wlykiv16Qla`。随后 `canvas_get_state` 返回 1 个图片节点，metadata.poseAtlas.index=864、id=upper80v2_P021、collection=pose、render=line。
- 独立浏览器刷新该测试画布后，图片仍显示。使用现有浏览器本地图片存储与画布存储，不在 MCP 请求或工具结果中返回原始 dataURL。
- 插入工具继承 Canvas Agent `targetClientId` / `boundClientId` 路由；`session.test.ts` 增补了跨客户端精确目标和无误写测试；`isCanvasWriteTool` 加入该工具，使人工审批模式仍适用。

## 自动化 / 已知问题

- Canvas Agent `npm test`：132/132 pass；`npm run build` 通过。
- Gateway PoseAtlas `node --test comfyui-gateway/test/pose-atlas.test.js`：8/8 pass；新增语义检索和详情单测。
- 前端 `tsc --noEmit` 仍只有仓库原有错误：`src/components/canvas/canvas-node.tsx(128,5): onViewImage does not exist on CanvasNodeProps`，与 P2 无关。本次修改未引入新增类型诊断。
- 新 MCP 工具由 Agent 服务的 MCP 实例启动时注册；对话中的既有 Codex MCP 工具快照可能需要新建会话后才能识别，未强制终止用户运行中的线程。
- 没有执行真实 H3 关键帧生成或多镜头连续性评估，这属于 P3。

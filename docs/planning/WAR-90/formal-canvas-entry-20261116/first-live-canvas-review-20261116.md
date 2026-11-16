# WAR-90｜首次真实 Canvas Agent 只读镜头审阅：当前画布无 Shot02 映射

日期：2026-11-16，机器 Eric。此记录接续正式工作空间七文件 Skill 内部部署。目的是记录用户通过实际 Canvas Lab UI 与原生 Agent 的第一次只读交互，不把用户回报冒充底层 API 原始载荷。

## 用户侧回报（直接转述，尚非独立节点快照）

用户自己打开并选择了一个画布，而此前提供的 http://localhost:3000/canvas?mode=recent 链接未能可靠打开目标。画布名称为“无限画布 1”，包含三个内容为空的文本、图片、音频节点，无当前选中节点；没有对应 Shot02 的节点。原生 Agent 已告知只能依 Runtime 文本审阅 Shot02，不能核对画布中镜头呈现，且没有创建节点。

这个文本是用户从实际 Agent 交互回传的报告，不是从 /api/tools 独立冻结的 JSON 节点快照。不能因此声明 Node→Shot 自动映射、选区检查或 UI 导航已经在产品层实现。

## Eric 独立回核

- Agent /health：hasCanvas=true、clients=1、codexBusy=false、conversation status=ready，infinite-canvas/codex_apps MCP 均 ready。
- Canvas Agent systemd 日志：同一轮实际模型 turn accepted/started/finished；期间真实 MCP 工具调用 canvas_get_state 与 canvas_get_selection。审计未见该次 turn 的 Canvas 创建、删除、更新调用；日志非全部工具底层载荷的完备证明。
- 批准 B 的 docs/planning/WAR-90/pilot-D-local-repair-v2/state.json SHA256 仍为 23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7。
- 正式七文件 Skill 安装未改动，无媒体生成或此轮人工修改批准。
- 曾出现 GET /agent/codex/threads/... 返回 “list_turns is not supported yet” 的独立日志错误；与用户打不开 /canvas?mode=recent 链接是否相关，**尚无证据证明**，不得当作根因。

## 下一停点与范围

第一轮只读交互真实执行，证实“Runtime 中已有 B，但用户所开画布没有可审阅的 Shot02 节点”这一业务集成缺口。正确下一步是**让同一个正式 Canvas Agent 将已批准 B 的镜头内容作为审阅用展示节点投影到用户明确选择的当前画布**，而不是让用户重新生成 B 或由 Chat HTTP 直接跨客户端写画布。

拟议最小投影：Shot01–Shot04 四个明确标注“来源：已批准 B / 展示副本”的文本节点，可增加一条头部说明；保留既有三个空节点、不清理，不创建图片/音频/视频或对原 B 进行修改，不把画布文本节点当成独立的权威 DirectorPlan。模型先通过 canvas_get_state 确认当前 project/已有节点且仅一客户端已连接，再由原生 Canvas Agent 负责写入及写后复核，避免 Chat /api/tools 的全局 activeClientId 竞态。Node→Shot ID 映射先作为可追踪试验记录，正式契约归 WAR-37。

**本轮尚未取得用户授权来向该真实画布添加展示节点**，故此项仍是建议，未执行。用户在原生 Agent 中的自然语言修改/审批须另行授权与版本守门；没有新真人修改意见。

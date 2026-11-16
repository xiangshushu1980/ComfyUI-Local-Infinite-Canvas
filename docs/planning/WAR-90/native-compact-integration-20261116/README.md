# WAR-90 · Canvas 原生 Compact Shot 与 Chat 双客户端路由复检

日期：2026-11-16；执行机器 Eric。当前为隔离联调，不是正式 Skill 安装或真实修订授权。

## 当前阶段 / 面向人的测试目的

主入口 A（画布内置 Canvas Agent）使用完整七文件 Director Skill，真实发起原生 Codex turn，尝试经 Director Runtime 读取已批准 Shot02，并从 Canvas MCP 复核选区。协作入口 B（ChatGPT→DCR→Eric→现有 Canvas Agent HTTP）验证多浏览器客户端下的工具目标路由。独立 Codex 仍只作备用。

没有新的用户镜头修改意见；不生成修改候选、不重新签 B、不执行 GPU/ComfyUI/H3/图片/视频。所有 HTTP、浏览器和节点均位于临时独立实例。

## 1. Canvas Agent HTTP Skill 生命周期：有限 PASS

上轮尚未跑通的 HTTP 层已于本轮真实完成。通过独立 HOME/CODEX_HOME 与临时 Canvas Agent 的 GET /agent/codex/skills?forceReload=1，发现并启用七文件 director-skill-v0-candidate；12 处相对引用有效。只在临时目录更换合成的测试版阶段卡并回退后，七文件 SHA 全部恢复。未调用模型或修改正式工作区。

权威结果 ../main-entry-preflight-20261116/isolated-skill-lifecycle-result.json，复现脚本同目录 isolated_skill_lifecycle.py。它只证明 API 发现/刷新/回退，不证明模型已使用知识或正式安装。

## 2. 原生 Compact Shot 模型调用：未完成

隔离脚本 native_compact_test.py，结果 native-compact-smoke-result.json、native-thread-history.json：

| 验证点 | 结果 |
| --- | --- |
| 临时 Canvas Web/Agent、单独浏览器和 Skill HTTP 发现 | PASS |
| 私有画布 5 节点、唯一 Shot02 选区 | PASS |
| HTTP MCP 配置 infinite-canvas enabled，无关 MCP override disabled | PASS（配置层） |
| 画布自己预备的 Codex thread 就绪且被复用 | PASS |
| 原生 POST /agent/codex/turn 接受请求、busy=true | PASS |
| 模型真实执行 review-shot、读到完整 Shot02 | UNKNOWN，未验收 |
| 模型通过 Canvas MCP 实际执行 get_state/get_selection | UNKNOWN，未验收 |
| MCP 工具权限与拒执行、完整审批 | UNKNOWN，未验收 |
| 完成结果及 settled turn | 未获得：约 168 秒后 busy 仍为 true，history messages=0，settledTurnIds=0 |
| 业务状态及清理 | 私有画布/选区未变；原批准 B 未变；临时浏览器、Agent、端口已清理 |

重要：提示词含 review-shot、canvas_get_state、canvas_get_selection 字符串，不构成真实工具调用证明。native_cli_execution_proven 与 native_canvas_mcp_read_proven 均保持 false。

隔离 Agent 日志曾出现云端模型列表刷新和远程 MCP 连接超时。目前无法将未完成原因唯一归因于网络，也不应猜测是 Director Skill/Runtime 缺陷。首轮在 UI 自动准备 thread 期间主动 POST threads/new 返回 409；修正后直接复用 UI 准备的 thread。最初 409 的原始控制台被后续运行覆盖，故此处为诊断记录而非独立冻结轨迹。

模型使用原有已授权的 CODEX_HOME，但临时 Canvas Agent HOME/配置/Skill/浏览器独立，禁用无关 MCP 的覆盖在进程启动前写入；没有复制或公开认证文件。测试采用 automatic 模式，不构成审批拒绝证据。本轮并未得到业务 no-handoff 终态。

## 3. Chat 双客户端的真实只读路由反例：PASS

脚本 multi_client_read_route.py 在独立 Agent 上建立两条模拟 SSE 客户端，分别提交合成的 canvas state，并使用相同的 POST /api/tools 参数读取 canvas_get_state。

- 激活 A → 返回合成 Project-A / Node-A。
- 激活 B → 返回合成 Project-B / Node-B。
- 再激活 A → 再次返回 Project-A / Node-A。

证据 multi-client-read-route-result.json。直接观察到 HTTP 读目标随全局客户端焦点改变，而不是由调用的请求参数绑定。只验证读操作路由，未尝试写操作，更未造成生产误写。

在本轮原生 Codex turn 忙碌时，Chat 的只读 preflight 使用真实私有浏览器读到的 health/state/selection 和已批准 B 的 review-shot，正确返回 BLOCK：Canvas Codex turn busy or unknown，can_write=false。结果 chat-real-browser-readonly-preflight.json。此项不等于拥有 Node→Shot 可信映射或原子 CAS。

因此 Chat HTTP 的目标安全写入继续 BLOCK；单客户端检查、人工确认与纯数据前检均无法解除跨请求焦点/项目变更竞态。请求级 client/project/revision 绑定须在正式 WAR-35/WAR-37 设计内解决。

## 4. 收口 / 下一关口

已通过：Canvas Agent HTTP 七文件生命周期；隔离 Web/Agent/浏览器/画布；UI 原生 thread 创建及 turn 接受；MCP 配置覆盖；Chat 双客户端只读路由反例；原生忙时 Chat 读前检正确拒绝。

未通过：在同一原生 turn 中真正完成 review-shot 和 Canvas MCP 两次读取；工具拒执行与审批；异常后服务内 busy 恢复；正式 Skill 安装；跨入口安全编辑；真实修改和 B 重审。

下一步先诊断 Eric Codex 云端请求的稳定性；若恢复，再做一次有明确终止上限的原生只读 turn 验证，必须以真实 thread/turn/item 工具结果而非模型自述为准。持续阻塞则保留 unknown，不降级安全要求或切换成另一个常驻导演 Agent。

本阶段不启动正式 Canvas 服务，不改用户画布、原批准 B、正式 Skill、WAR-35/37 或媒体。

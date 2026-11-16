# WAR-90｜网络恢复后原生 Compact Shot 只读复测

- 日期：2026-11-16，Eric。
- 目标：验证既有 Canvas Agent 内置 Codex + 七文件 Director Skill + Runtime CLI review-shot + infinite-canvas MCP 的同一 turn 只读闭环；不验证修改或生产发布。
- 样本：D《错过的钥匙》，已批准 B 的 Shot02。测试工具为本目录 native_compact_retry.py，从上轮隔离程序复制并修订；改用本目录、独立 17481/17482 端口、受控完成窗口、自动准备线程复用和结构化工具结果判断。
- 输入源：/home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2，批准 state.json SHA256 = 23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7。
- Skill 源：docs/planning/WAR-89/director-skill-v0-candidate（七文件逐项 SHA 存 native-compact-smoke-result.json）；临时完整复制到私有 HOME 工作区；正式 workspace 的候选仍未安装。
- 服务环境：隔离 Canvas Agent + 独立 Web 端口 + Headless Chromium 私有 profile；使用 Eric 已授权的 CODEX_HOME 调用原生模型，无认证文件复制，无本机正式服务启停；未启用 H3/ComfyUI/Blender。
- 模型参数：gpt-6-luna、medium、测试隔离线程、permissionMode=automatic。原生 turn 内约束只读，不将 prompt 当作安全的执行隔离。

## 结果（有限 PASS）

从独立 Canvas Agent 的正式 HTTP 接口选中 enabled 的七文件 Skill，Canvas Web 自动创建 Codex thread；Native Codex 收到 turn (HTTP 200)，真实执行成功，最终 busy 返回 false。此次用时 42.43 秒，history 有 8 条消息与 1 个 settledTurnId。

证据来自 native-thread-history.json 的结构化 item，而不是提示词字符串或模型自述：

1. 一条 kind=command、status=completed 的实际工具记录，退出状态 0。所执行的 shell 命令读取 Skill/shot-plan 阶段文档并调用 Runtime review-shot --shot-id Shot02；工具 output 15580 字符，包含 Shot02 与批准 B ID b7b4fd156b884907b2431b6b1e0d9960。没有观察到命令型修改调用。
2. 两条实际 kind=tool、status=completed 的 Canvas MCP 工具记录，分别为 读取画布 和 读取选区；读取画布返回 5 个文本节点，唯一选中 Shot02。此类历史条目只有简要结果，未将底层 MCP 原始载荷当作已捕获。
3. 原生最后一条 assistant 消息确认 CLI 与 MCP 的只读结果，并指出一条待观看验证的风险：观众是否能在林取起文件夹前认出钥匙。该意见不替代真人视听审阅。
4. private_canvas_unchanged=true、private_selection_unchanged=true、production_untouched=true。结束后独立 Web/Agent/浏览器退出，17481/17482 不再监听；正式 canvas-lab-agent/web/gateway 服务保持 inactive。
5. HTTP MCP 配置显示 infinite-canvas enabled，hindsight/codegraph/hindsight-direct/blender/cua_repl disabled。成功线程历史未出现 Hindsight 工具调用；这不是对权限拒绝的强制执行测试。

正式 B state SHA256 复核不变；没有新的用户反馈、新候选、A/B 重签、生成媒体或真实用户画布改动。脚本输出 read_only_end_to_end_pass=true，独立审计进一步确认一个 exit0 CLI item 与两个已完成 Canvas MCP item 均存在。

## 边界与未验收

- 通过的是私有测试画布，不是用户的生产 Canvas / project / Node→Shot 正式映射。
- 只验证了具体只读任务；没有证明 MCP 写工具可以被逐次拒绝、权限策略已隔离、Chat HTTP 具备原子目标绑定或并发 CAS。Chat 入口对 Canvas 写入仍 BLOCK。
- 尚未在正式工作空间安装七文件发布版，候选仍标记未安装；不能把这一成功测试当作发布授权。
- 最终画面质量、钥匙可见性与观众体验仍需交互审阅/后续生成验证。
- 复用了已授权 CODEX_HOME，仅隔离 HOME/Agent/Skill/画布；不是无任何环境继承的沙箱。
- 2026-11-16 前一轮模型连接超时的证据仍在 docs/planning/WAR-90/native-compact-integration-20261116/，本轮不覆盖其原始结果。

## 冻结证据与下一步

- native_compact_retry.py：重现脚本，基于前次脚本的带版本副本。
- native-compact-smoke-result.json：关口判断、七文件 SHA、服务配置与清理/基线状态。
- native-thread-history.json：原生 turn 完成历史，保留命令及工具的执行事实。
- native-retry-console.log：外部执行控制台。
- evidence.sha256：逐文件哈希清单。

下一步宜进行正式 Skill 安装/回退与实际用户画布只读审阅的授权讨论：明确何时启用服务、如何将七文件 candidate 定版与新线程生效、如何在用户真实画布确认目标 Shot 并按只读原则操作。权限拒执行及 Chat 写入目标绑定需单独验证；不以本轮自动放行修改权限。

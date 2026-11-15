**主审裁定：targeted-revision；A3 按现稿执行为 block，实际隔离与拒绝效果为 unknown，不予 accept。** 我已对照冻结设计，亲自读取 Eric 的配置探针、审批分派、CLI 与 Runtime 源码，并核对两份 Reviewer 原报告。结论不依据票数；本轮未写文件、未运行模型试验、未签 A/B，未复算原 B 状态 SHA。

**审批问题比两份报告描述的更具体。** [codex-client.ts:706](/home/sean/projects/canvas-lab/infinite-canvas/canvas-agent/src/agent/codex-client.ts:706) 只将三类请求纳入 `codex_approval`：命令执行、文件变更、权限申请。`mcpServer/elicitation/request` 不在其中，普通线程分支反而自动返回 `action: "accept"`；其他未知请求返回通用 decline，也不构成人工审批闭环。不能把 elicitation 等同于工具执行授权，更不能把原生命令审批当作 `canvas_get_state` 自身审批。

因此，现有源码没有支持“A3 必能通过 codex_approval 拒绝 MCP 调用”的依据；`on-request` 也不能抵消配置中明确的 `default_tools_approval_mode: "approve"`。这不证明所有 Codex 版本均不支持 MCP 审批，但足以阻断当前测试脚本假设。两位 Reviewer 的“事件类型未证”须升级为“现有客户端接线存在明确缺口”。

**必须先修权限试验定义。** 核定安装版本支持的 MCP 控制配置、请求类型及响应结构，确认是否有现成通路；若没有，就报告当前通路不可验证，不为完成测试擅自扩建审批系统。A2 可作为独立隔离试验继续设计：探针仅证明全局配置启用 Hindsight/Codegraph、空 CODEX_HOME 无 MCP；须另核临时进程环境、cwd、认证来源、新线程生效配置及真实工具集合。`workspace-write` 只能称业务只读测试，不能称文件权限只读。

A3 的成功条件必须是调用与审批关联、decline 形成终态、工具入口证明确未执行。没有成功返回、超时或断连都不足以证明拒绝有效；无执行观测则保持 unknown，并验证取消后的迟到调用、进程和 busy/client 恢复。

**Compact 仅对定位与局部文本核对达到接近最低充分，尚不足以支撑导演判断。** 我确认 [runtime.py:528](/home/sean/projects/canvas-lab/tools/director-runtime-v0/runtime.py:528) 已复核来源、候选、A/B 人类证据及 pending_shots；`locked()` 读取并加锁，不自动保存。投影应直接复用 packet 的目标正文、哈希、review、capabilities 和 provenance，不再次解析审批或重建权威逻辑。B 哈希对应候选 artifacts 的规范编码，另两层对应 UTF-8 文本，不可跨对象比较。

必须补的是**故事源上下文**，不必塞入程序源码全文：从 `authority.source_text` 提供相关原文及可复现位置，并按判断需要补批准 Intent、Beat、Blocking 中的目标、人物知情、声音时序和空间依据。不能稳定关联就标 unknown，提供完整来源/阶段补读路径；不能靠模型摘要填空。邻镜节选须带范围、全文 SHA 和全文补读方式，连续性判断仍需完整邻镜。三层哈希只能验对象一致性，不能补足语义上下文。

**顺序裁定：不要求 A3 成功后才允许离线 CLI 实现。** 采纳工程 Reviewer 的依赖拆分；导演 Reviewer 对上下文的要求成立，但不必阻塞独立投影开发。允许 ChatGPT 的最小下一步是修订上述测试契约、固定字段与降级规则，随后仅实现试点 CLI 和确定性测试；原生集成复测仍受审批门槛约束。新增测试须覆盖逐字一致、来源失效、边界/重复 ID、哈希对象及业务状态不变，不能借既有 54 项宣称通过。

可选：独立允许分支验证观测链、结构化字段选择。延期：生产安装、正式 Schema/UI、候选提交、A/B 批准及媒体验证。

本轮终端读取命令被工具审批机制拒绝，原因是需要审批而当前策略为 never；已改用获准的只读文件工具完成核对，该拒绝不作为 A3 证据。
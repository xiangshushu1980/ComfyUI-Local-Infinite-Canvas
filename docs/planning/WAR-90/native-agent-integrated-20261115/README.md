# WAR-90｜Canvas Agent 内置 Codex + Director Skill + Runtime CLI + Canvas MCP 原生只读集成

日期：2026-11-15｜设备：Eric｜权威工作机目录：/home/sean/projects/canvas-lab
Linear：WAR-90（In Progress）

## 当前阶段与给人看的测试目的

**当前阶段**：Director Skill v0 从独立 Codex CLI 走向 Canvas Agent **原生 Codex 对话**的最小集成验证。此前用户对于 Shot02 表示“暂时没有修改意见”，因此这一轮只有只读检查，不产生修订。

**给人看的测试目的**：证明一个 Canvas Agent 会话自己发现并使用 Director Skill、读取已批准 B 的权威全文（通过 Director Runtime CLI），再调用同一画布 MCP 读取节点与 Shot02 选区，最后返回专业只读检查；无需 ChatGPT 每步转发、无需 Runtime 启动第二个 Codex。评估是否可安全推进到正式安装或修改型候选，不证明媒体效果。

## 实际结果（逐级证据）

| 项目 | 当前判断 | 可核对的依据 |
| --- | --- | --- |
| 独立测试 Agent 可发现候选 Skill | **PASS** | 列表找到唯一 director-skill-v0-candidate，enabled=true，errors=0；路径位于专用临时 workspace |
| 新隔离浏览器与 Canvas MCP | **PASS** | 新测试画布 5 个节点，选中 Shot02，确认 projectId 和唯一真实选区；两次回归均成功 |
| Canvas Agent 原生 Codex thread/turn | **PASS** | 第二轮 POST threads/new/turn 皆 200；codexBusy true→false，historyReady=true，一个 settledTurnId |
| 显式 Skill 使用 | **部分 PASS** | 同一原生会话实际读取 shot-plan.md 和 review-method.md；Skill 选择器有效，完整入口注入/七文件全读非本轮验收且未证 |
| Director Runtime CLI 只读读取 | **PASS** | 同线程执行 review-pack，退出码 0，后续按 stages.shot 取出完整正文和 Shot02；非 Canvas 截断预览 |
| 真实 Canvas Agent MCP | **PASS（UI 历史摘要）** | 同一 thread/turn 中两条 completed“读取画布”和“读取选区”，Agent 回复称 canvas_get_state / canvas_get_selection；UI 历史不含完整原始请求参数 |
| no-handoff 与画布未被本轮改写 | **PASS（受限）** | 原生回复明确 no-handoff，测试画布仍是同一 5 个节点；原 B state SHA 复核未变 |
| 禁用无关工具、权限隔离 | **NOT ACCEPTED** | 明确出现一次失败的 hindsight_search_pages 调用；Codegraph startup warning；虽尝试临时 mcpOverrides=false，实际工具暴露仍不干净 |
| 修改候选、生产安装、A/B 再批准、媒体 | **NOT TESTED** | 无真人修改意见、不调用 prepare/submit/run-stage、未安装生产 Skill、无图像视频或观众证据 |

本轮**不是完全无文件写入的模型执行**：第二轮原生 Codex 由于 CLI 大包截断，将同一只读 JSON 临时保存到 /tmp/war90-review-pack.json，并做了二次 JSON 解析。该文件事后经格式/B ID 检查后删除。没有留下 Runtime 修改候选，也没有新 B 批准。

## 独立发现的两个问题

### 1. 意外 MCP 暴露

实验以单独 HOME、独立浏览器 profile 与临时 Skill 副本运行 Canvas Agent，使用 Eric 现有 CODEX_HOME 仅作为同一机器的 Codex 环境（没有拷贝认证或修改用户全局配置）。临时配置对 Hindsight、Codegraph 等名称设置 mcpOverrides=false；然而新会话仍显示 Hindsight ready、Codegraph failed，实际有一次 hindsight_search_pages 失败调用。静态检查 Eric 全局 Codex 配置确有这两个服务器条目，且未显式 enabled=false。

现可确认的是**无关工具暴露/尝试调用发生**；但尚未确认具体由 app-server 启动配置继承、thread config merge 或插件层造成。不能把临时 mcpOverrides 的字段存在当作隔离成功，也不能在用户生产 Agent 上直接禁用全局服务。

### 2. 模型对权威 SHA 的错误解释

模型误将 approved_B_content_sha256（整个候选的内容指纹）与 stages.shot.text_sha256（Shot Plan 阶段纯文本）当成应该相等，因而错误报告“批准正文哈希不可信”。另有测试命令用了不存在的 shot_plan 键及恒假的 and False 表达式。

**独立工程核验**：
- B Candidate content SHA256：64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7
- Shot Plan 阶段文本 SHA256（声明与实算完全一致）：b2c2d5e14eb292cfafa1e9049913f97c6229ea5f1be51b1f7a94020f90fe8817
- 原 B state.json SHA256：23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7（未变）

以上 SHA 属于**不同的对象或序列化范围**，不能直接互相比较。不能把模型的错误当作真正的 B Authority 损坏。候选 compact view 应明确每个 SHA 所指的对象与用途。

## 原生模型输出的专业判断边界

模型在拿到 Shot02 全文后指出一个待验证镜头风险：近景中观众是否有足够注意窗口辨认银钥匙、理解文件叠承托蓝夹和再次遮挡，并认出手臂动作与切点。它没有发现本轮需要直接修改的已证硬冲突，正确停在 no-handoff。**真实性、几何、观看效果未知；不是用户批准的新 B。**

## 多 Agent 分层审阅（外围质量控制）

依据 docs/agent/review-agent-collaboration.md，在**导演实际执行完成之后**，两个隔离 Reviewer 分别用 Luna Medium（架构/上下文）和 Astra Medium（工程/安全）审阅相同冻结证据；Astra Medium 主审阅读两份原始意见并核对源证据，3/3 真实模型执行成功。主审判定 **targeted-revision**：

- 接受 **有限的原生只读调用里程碑**，不允许推广为完整编辑闭环、安全隔离或生产安装成功。
- 优先补脱敏的 thread/turn/item 证据索引、MCP 配置来源和审批/错误清理边界；进入修改或生产前必须验证隔离与拒绝权限行为。
- 将只读目标 Shot compact view 作为**独立小方案候选**，不抢先实现第二套 Schema，也不因大 JSON 截断而重新造 Agent。
- 保持生产安装、Runtime prepare/submit、修改失败回滚、用户 B 审批、正式 Canvas UI、媒体效果为未来验证。

审阅证据在 review/：frozen-review-packet.md、manifest.json、两个 reviewer 及 lead 的原始 prompt/result/events/run、summary.json。

## 安全与执行范围

- 未修改原 Canvas Agent 的生产代码、配置或正在使用的用户画布；临时测试 Agent、浏览器与 Skill 副本已关闭/删除；这里的“生产未动”仅是本轮未执行该类写操作，**逐字复算只覆盖批准 B state.json**，不声称扫描了全部生产文件。
- 真实独立浏览器项目 ID 和原生 thread ID 属于已结束的测试实例，不能当作用户仍可见的正式画布。
- 从模型输出可见其临时 JSON 文件写入，不应将模型执行称为绝对只读；具体只读的是 Runtime 试点的业务状态。
- 不运行媒体、ComfyUI、H3、Blender/GPU，不改变 WAR-35/52 生产 Schema，不自签用户批准。

## 下一个最小关口

1. 依据 native-evidence-index.json 保存 UI 事件的 thread/turn/item 对应关系，并继续定位非必要 MCP 的来源、明确审批/取消时的实际边界；在正式生产更改前需要单独隔离反例。
2. 先设计最小只读目标 Shot 输入（含必要上下文、哈希对象标签、压缩响应与完整性校验）并由主审阅 Agent 检查，确认必要性后才动 CLI。
3. 若未来要给实际 Canvas Agent 安装候选 Skill，须先确认七文件清单、版本/回滚和新建线程的生效边界；正式生产 Skill 安装、UI 写入均不是本轮授权内容。

本轮 WAR-90 保持 **In Progress**。既有无人提出修改意见的停点不变。

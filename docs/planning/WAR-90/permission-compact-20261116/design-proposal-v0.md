# WAR-90｜原生工具隔离与 Compact Shot View v0（待独立审阅）

日期：2026-11-16；设备：Eric。当前阶段：Canvas Agent 原生只读集成完善，不是 DirectorPlan 生产 Schema、正式安装或用户 B 批准。

## 给人看的测试目的

让画布里的同一个 Codex Agent 只看到导演操作必要的工具，并从 Director Runtime 一次取得目标 Shot 的完整原文、必要相邻状态和明确分层的哈希；不需要打开巨大的 review-pack 造成输出截断，也不用再启动第二个模型。无新真人修改意见，因此本轮仅做只读和拒绝审批测试。

## 冻结事实与边界

1. 基线 B state.json SHA256=23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7，原 B candidate id=b7b4fd156b884907b2431b6b1e0d9960；必须字节不变。
2. Eric 实测全局 CODEX_HOME=/home/sean/.codex 的 config/read 看到 Hindsight 与 Codegraph 为 enabled。全新空 CODEX_HOME 的独立 app-server config/read 得到 MCP server 列表为空。两种都是无需模型的真实 RPC 请求，见 config-origin-probe.json。
3. 上轮 Native Agent 使用独立 HOME 但复用了全局 CODEX_HOME；即便测试 local mcpOverrides=false，原生模型仍调用了一次无关 Hindsight 并失败。配置来源继承被证实，但为何临时覆盖未生效尚不确定。具体 Tool Scope 和审批拒绝也未证。
4. Runtime review-pack 的 B candidate content SHA256=64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7；stages.shot.text SHA256=b2c2d5e14eb292cfafa1e9049913f97c6229ea5f1be51b1f7a94020f90fe8817。它们对应不同对象；各自值与本身预期一致。
5. 正式 UI 映射归 WAR-37；正式持久化/Schema 归 WAR-35；WAR-90 只做隔离试点。无媒体、无原画布、无正式 Agent 设置改动、无审批模拟。

## A. 工具隔离试验设计

- A1 配置原点对照（已执行）：原 Codex 配置/空配置分别 config/read，只记录 server name/enabled，不读取或泄漏 URL、命令参数、认证信息。
- A2 真正隔离的 native Agent 试验（下一步）：为临时 Agent 使用独立 HOME + 独立 CODEX_HOME（仅为受控临时模型调用提供授权，不拷贝任何研究资料中的凭证），不得加载用户原 config.toml。新线程采用 permissionMode=request，仅启用现有无限画布 MCP；查询 /agent/codex/mcp、thread MCP 预热状态，以及真实可见工具。将原生产 Agent 服务、画布客户端数与原 B SHA 作为前后检查。
- A3 审批拒绝反例：在专用测试画布上请求一个无害的只读 canvas_get_state MCP 调用，并对该工具自己的真实权限请求显式执行 decline。保存请求/决议及对应 thread/turn/item；预期工具未返回成功数据。若无权限请求、工具事前执行或监听不可靠，则记 unknown/block，绝不声称隔离通过。禁止在用户真实 Canvas 上测试；禁止用 permissionMode=full 绕开审批。可选随后再在 request 模式批准仅一个读取，以证明允许与拒绝区分；真实审批规则不因测试放宽。
- A4 失败与清理：未收到审批、会话超时、断连均按 fail-closed，中止该专用线程并关闭临时 Agent/browser，仅清理本次资源；不修改用户配置，记录 client busy 恢复证据。无需为试验建设新服务器 API。
- 入生产门槛：必须证明实际工具列表和拒绝审批有效，且没有 Hindsight/Codegraph；即使 A1/A2 通过也不能由此直接声称所有运行模式隔离。

## B. Compact Shot View v0 只读数据设计

新增试点 CLI 子命令（经审阅后才实现）：

    python3 tools/director-runtime-v0/cli.py review-shot --workspace PILOT --shot-id Shot02

实施边界：

- 内部直接复用 Pilot.review_packet() 的既有已批准 A/B、来源/Skill SHA、完整四阶段 artifact、Human review evidence 及 pending_shots 校验；然后只做无副作用投影，绝不绕开其守门逻辑，不复刻第二套 Authority/Review 实现。
- 接受精确出现在批准 Shot list 中的 Shot ID，未知/重复/无审阅凭据/已过期输入一律 fail closed；输出 JSON stdout，异常 stderr exit 2。
- 内容：format=war90-director-shot-preview-only-v0，read_only=true，target_shot 的原封不动完整文本与自身 SHA，neighbors 的前后 Shot ID/SHA/明确标记为节选而非全文的动作/切点段落（例如前镜末段与后镜入镜段），authority 的 B candidate id、source SHA、批准 A/B ID，hashes 的对象/算法 SHA256/实际 hash 具名三层：B_candidate_canonical_content、ShotPlan_stage_utf8_text、target_Shot_section_utf8_text，显式不能跨对象比较；unknown、审批 provenance 为 pilot_only、formal_WAR35_approval=false。此投影不包含源码全文/全场其他阶段文本，只用于已批准 B 的 Shot 定位/只读判断，不可据此生成新合法候选。
- 邻镜节选必须从原批准文本抽取，保留确切文字、可再查完整邻镜；若段落定位不稳定，应安全退化为完整邻镜或返回片段不可确定，不可由模型补写，亦不得暗示只凭节选可以验收连续性。
- 直接输出尽量短（目标 Shot 文字与两段邻镜资料），预期明显小于完整 review-pack；如仍超终端阈值，提供 stdout 结构化局部字段选择而非擅自截断目标文本。无 approve 或写入参数。
- 保留 CLI 旧 review-pack，不改变 WAR-35 正式 Schema、不更改原七文件 Skill、不复制原生产工作区。

## C. 测试与审阅

- Compact 命令确定性测试：正常 Shot02；前后边界 Shot01/04；未知 Shot；B 未批准；源材料/凭据失效；每个 SHA 对应正确对象；完整 target 与批准原文逐字相等；邻镜节选原文可追溯；无业务状态写入。原 Runtime 54 项测试全通过。
- 同一原生 Agent 只读复测 A2/A3 与 Compact 命令，不以模型自述代替工具记录；保留失败轨迹、实际批准与未批准分支。
- 两名独立 Reviewer 从工程边界、导演阶段上下文分别检查；主审独立核对证据决定 accept / targeted-revision / block / unknown。Reviewer 仅为外围质量保证，不成为导演运行时第二个 Agent。
- 不在本轮执行候选 prepare/submit、原 Canvas UI 写入、Skill 生产安装、A/B 重新批准或媒体。

## 请 Reviewer 重点回答

1. A2/A3 是否是最小且安全的权限证明？是否错误假设原生 MCP 工具一定产生 app-server approval event？
2. Compact View 是否提供专业只读判断所需的最少上下文，是否过度节选邻镜导致虚假连续性结论？
3. 本设计是否存在隐含的新数据契约/第二套审批或绕过 read-only 守门？如何收窄？
4. 先执行 A2/A3、再实施 B CLI 是否合理？指出 blocking 与必须先修的地方。

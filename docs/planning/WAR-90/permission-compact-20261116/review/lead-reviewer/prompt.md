你是主审阅 Agent，主持本轮 WAR-90 的双 Reviewer 专业/工程方案审阅。必须亲自核对冻结设计、Codex 配置探针以及现有源码，再读两份相互隔离的 Reviewer 原报告；不能机械投票。
裁定 A2/A3 真实审批拒绝的可行性，尤其检查 MCP 工具请求是否属于现有 codex_approval 所支持的类型。对 Compact View 做最低充分性审计，判断是否应该先实现试点 CLI / 必须怎样补源上下文。明确 accept/targeted-revision/block/unknown，必须/可选/延期及允许 ChatGPT 实施的最小下一步；不写文件，不签 A/B，不假报通过。中文 800-1500 字。
=== FROZEN ===
## CANDIDATE DESIGN
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


## REAL CODEX CONFIG ORIGIN PROBE JSON
{
  "test": "read-only config/read via actual Codex app-server; no model or browser",
  "inherited_HOME_CODEX_HOME": "/home/sean/.codex",
  "inherited_config": {
    "initialized": true,
    "mcp_names": [
      "blender",
      "codegraph",
      "cua_repl",
      "hindsight",
      "hindsight-direct",
      "infinite-canvas"
    ],
    "enabled": {
      "cua_repl": false,
      "hindsight": true,
      "codegraph": true,
      "blender": false,
      "hindsight-direct": false,
      "infinite-canvas": false
    }
  },
  "empty_isolated_config": {
    "initialized": true,
    "mcp_names": [],
    "enabled": {}
  },
  "no_auth_material_read": true,
  "no_global_config_modified": true,
  "important_scope": "config/read is config origin evidence, NOT actual thread tool scope or approval denial"
}


## EXISTING CANVAS CODEX START AND MCP CONFIG
    static async start(emit: AgentEmit, onExit: () => void) {
        logger.info("Starting Codex app-server", { executable: process.execPath, codex: codexBin() });
        const child = spawn(process.execPath, [codexBin(), "app-server", "--stdio"], { stdio: ["pipe", "pipe", "pipe"], windowsHide: true });
        const client = new CodexAppClient(child, emit);
        let stopped = false;
        const stop = () => {
            if (stopped) return;
            stopped = true;
            onExit();
        };
        child.stdout?.on("data", (chunk) => client.read(chunk.toString()));
        const stderr = createAgentLogWriter((text) => {
            logger.warn("Codex app-server stderr", { text });
            emit("agent_log", { text });
        }, (text) => text.replace(/^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s+/, ""));
        child.stderr?.on("data", (chunk) => {
            if (client.skillDraftActive) return stderr.clear();
            stderr.write(chunk.toString());
        });
        child.on("error", (error) => {
            stderr.flush();
            logger.error("Codex app-server process error", error);
            emit("agent_error", { message: error.message });
            client.failAll(error.message, true);
            stop();
        });
        child.on("exit", (code) => {
            stderr.flush();
            logger.warn("Codex app-server exited", { code });
            client.failAll(`Codex app-server exited: ${code ?? 0}`);
            stop();
            emit("agent_log", { text: `Codex app-server exited: ${code ?? 0}` });
        });
        await client.request("initialize", { clientInfo: { name: "canvas-agent", title: "Infinite Canvas Agent", version: VERSION }, capabilities: { experimentalApi: true, requestAttestation: false } });
        client.notify("initialized");
        return client;
    }

function codexConfig(permissionMode: AgentPermissionMode): JsonRecord {
    const mcpOverrides = canvasMcpOverrides(loadConfig().mcpOverrides || {});
    return { model_reasoning_summary: "auto", ...(permissionMode === "automatic" ? { approvals_reviewer: "auto_review" } : {}), mcp_servers: { ...mcpOverrides, "infinite-canvas": { enabled: true, command: canvasAgentMcp.command, args: canvasAgentMcp.args, default_tools_approval_mode: "approve", startup_timeout_sec: 20, tool_timeout_sec: 90 } } };
}

export function mergeSkillConfig(entries: unknown[], overrides: Record<string, boolean>) {
    const config = entries.filter((entry): entry is JsonRecord => Boolean(entry && typeof entry === "object" && !Array.isArray(entry))).map((entry) => ({ ...entry }));
    for (const [skillPath, enabled] of Object.entries(overrides)) {
        if (!path.isAbsolute(skillPath) || typeof enabled !== "boolean") continue;
        const index = config.findIndex((entry) => entry.path === skillPath);
        if (index >= 0) config[index] = { ...config[index], enabled };
        else config.push({ path: skillPath, enabled });
    }
    return { config };
}

/** Constrain local overrides to enabled flags on ordinary configured server names. */
export function canvasMcpOverrides(overrides: Record<string, boolean>) {
    return Object.fromEntries(Object.entries(overrides).filter(([name, enabled]) => name !== "infinite-canvas" && /^[A-Za-z0-9_-]+$/.test(name) && typeof enabled === "boolean").map(([name, enabled]) => [name, { enabled }]));
}

function threadSettings(permissionMode: AgentPermissionMode) {
    return { approvalPolicy: permissionMode === "full" ? "never" as const : "on-request" as const, sandbox: permissionMode === "full" ? "danger-full-access" as const : "workspace-write" as const, config: codexConfig(permissionMode) };
}



## EXISTING RUNTIME FULL APPROVED READ GUARD
    def review_packet(self):
        """Read-only, source-verified presentation view; never a Canvas execution API."""
        with self.locked() as state:
            self.check(state)
            active, a, b = state['active'], state['pilot_A'], state['pilot_B']
            if not a or not b or not active or state['stage'] != 'shot':
                raise PilotError('Canvas review preview requires a pilot A/B approved Shot')
            if state['phase'] != 'pilot-B-accepted' or state['pending_shots']:
                raise PilotError('Unresolved Shot neighbor review or unapproved revision')
            if active != b or active['id'] != b['id']:
                raise PilotError('Active candidate differs from the accepted pilot B')
            artifacts = active['artifacts']
            if set(artifacts) != {'intent', 'beat', 'blocking', 'shot'}:
                raise PilotError('Review preview requires four complete stage artifacts')
            if artifacts['intent'] != a['artifacts']['intent']:
                raise PilotError('Active Intent no longer matches approved pilot A')
            order = artifacts['shot']['shot_ids']
            segments = shot_sections(artifacts['shot']['proposal'], order)

            def matching_review(checkpoint, candidate):
                for review in reversed(state['reviews']):
                    if (review['checkpoint'] == checkpoint
                        and review['decision'] == 'accept'
                        and review['actor'] == 'human'
                        and review['candidate_id'] == candidate['id']
                        and review['candidate_sha256'] == candidate['content_sha256']
                        and review.get('pilot_only') is True
                        and review.get('formal_WAR35_approval') is False):
                        evidence = Path(review['evidence_origin'])
                        if digest(read_text(evidence)) != review['evidence_sha256']:
                            raise PilotError(f'Pilot {checkpoint} approval evidence has changed')
                        if digest(review['text'].encode()) != review['evidence_sha256']:
                            raise PilotError(f'Pilot {checkpoint} review text has changed')
                        return review
                raise PilotError(f'No matching external human pilot {checkpoint} approval evidence')

            review_a = matching_review('A', a)
            review_b = matching_review('B', b)
            source = read_text(self.path / 'source.txt').decode('utf-8')
            return {
                'format': 'war90-director-preview-only-v0',
                'purpose': 'read-only director review presentation for future Canvas Agent',
                'authority': {
                    'source_sha256': state['inputs']['source.txt']['sha256'],
                    'source_text': source,
                    'skill_sha256': {key: value['sha256'] for key, value
                                     in state['inputs'].items() if key.startswith('skill/')},
                    'approved_A_id': a['id'],
                    'approved_A_content_sha256': a['content_sha256'],
                    'approved_B_id': b['id'],
                    'approved_B_content_sha256': b['content_sha256'],
                    'approval_evidence_sha256': {
                        'A': review_a['evidence_sha256'], 'B': review_b['evidence_sha256']},
                },
                'stages': {stage: {'text': data['proposal'],
                                   'text_sha256': digest(data['proposal'].encode('utf-8'))}
                           for stage, data in artifacts.items()},
                'shots': [{'id': shot_id, 'text': segments[shot_id],
                           'text_sha256': digest(segments[shot_id].encode('utf-8'))}
                          for shot_id in order],
                'review': {'pilot_A_accepted': True, 'pilot_B_accepted': True,
                           'external_human_evidence_recorded': True,
                           'identity_verified': False,
                           'formal_WAR35_approval': False,
                           'pending_shots': [],
                           'unknown': state['unknown'],
                           'media_verified': False,
                           'geometry_verified': False,
                           'audience_verified': False},
                'capabilities': {'display_text': True, 'propose_edit': False,
                                 'write_canvas': False, 'generate_media': False,
                                 'production_approval': False},
                'warning': ('This is an experimental review projection, not WAR-35 '
                            'DirectorPlan and not a Canvas Agent write command. '
                            'Media/geometry/audience require separate evidence.')}



## PRIOR LEAD REVIEW
**主审结论：targeted-revision。** 我逐项对照冻结 JSON、工具活动、HTTP 源码、Skill 入口及两份 Reviewer 原始意见裁定；结论不基于投票。认可隔离原生只读调用的有限里程碑，**不构成候选修订通过，更不代表生产安装获准。**

真实里程碑：最新运行有 Skill 发现与选择、HTTP 200、busy→finished、一个 settled turn，并有 `review-pack` 退出码 0、改用 `shot` 后提取正文的执行记录。画布、选区读取均显示 completed，支持原生读取已发生；精确工具名、参数与返回的关联仍缺原始事件。历史首次运行没有完成观察，不能拼入最新记录补证。Skill 两个方法文件有读取命令，但输出截断，入口注入及完整读取范围未知。

**分歧与证据强度裁定：**

- **隔离与审批：采工程 Reviewer 的更严格门槛，但不判整个只读里程碑失败。** Hindsight 失败调用证明非必要工具仍可被尝试，失败不等于隔离有效；Codegraph warning 不能证明调用。全局 MCP 污染路径尚未定位，不能直接归罪全局配置或 override。源码只传递 `permissionMode`，未证明实际 approval/sandbox 边界。此项阻塞修改与生产准入。
- **哈希：驳回原生模型的可信度判断。** B content 与 Stage text 是不同对象，且 `sha_match` 含 `and False`，恒假；不能登记 Authority 损坏。展示的实算 text SHA 与声明值相同，B state 未变则来自冻结核对摘要，本审未复算。身份与正式批准仍未验证。
- **compact view：要求先出设计，不把实现列为本轮只读验收前提。** 仅改措辞不能解决大 JSON 截断、猜错键名及临时落盘；但暂无证据要求立即扩展 CLI。原 Skill 按任务读取相关方法，不要求每轮通读七文件；七文件来源一致性和相对引用仍须核对。

**必须：** 修订测试目的与证据表，逐项区分成功、失败、未知；保留 warning、Hindsight 失败、`shot_plan` 错误及修正。准确称为“业务数据只读测试，发生临时文件写入”，no-handoff 仅表示没有交接。补同一 thread/turn/item 的脱敏事件、有效配置来源、实际工具列表和审批记录，解释 HOME、Codex 配置目录、进程环境与继承关系；进入修改前，在隔离环境验证拒绝审批后不执行。补 Skill 规范源、七文件摘要、路径引用及替换回退方案。`void runCodexTurn` 的后续拒绝不受外层 catch 兜底，内部清理未知；取消、超时和失败后的 busy/client/附件释放须验证。

**可选：** 在 WAR-90 范围提出目标 Shot compact view，保留必要邻接依据，标明权威层次、哈希对象与序列化范围；沿用原 Skill 和现有 CLI，不另造导演 Agent 或 HTTP bridge。

**延期：** 候选 prepare/submit、修改失败回滚、生产安装、身份认证与正式批准、真实几何和媒体观看验证。UI 映射归 WAR-37，typed Schema 归 WAR-35。节点数及 B SHA 不变不足以证明所有生产文件未触碰。

**最小下一步：** 先整理已有日志为可关联证据表，并定位 MCP 配置来源；缺失项明确 unknown，再提出隔离验证与 compact view 小方案。本轮没有用户修改意见，保持只读停点，无需制造新反馈；不生成候选，不签 A/B。
=== TWO REVIEWERS ORIGINAL ===
### reviewer-security
**结论：targeted-revision。** A2/A3 按现稿执行前须修订；工具隔离与拒绝生效目前为 **unknown**，阻塞修改和生产准入。未发现已证实的 P0。以下仅依据冻结源码和实验记录，不涉及工具操作，也不批准 B。

### 1. P1：A3 假定 MCP 读取必然产生可拒绝的审批请求，源码不支持

**证据定位：** `codexConfig()` 为 `infinite-canvas` 明确设置 `default_tools_approval_mode: "approve"`；`threadSettings(request)` 设置的是 `approvalPolicy: "on-request"`。冻结材料没有给出两者的优先级、适用事件或审批处理实现。

原生 app-server 的工具审批事件不能与 MCP 默认审批策略混为一谈。即使捕获到命令执行、文件变更或其他原生审批请求，也不能证明它约束了 `canvas_get_state`。当前无法断言该 MCP 调用会发出哪一种可 decline 的事件，甚至无法断言会发出事件。

**最小修订：**

- A2 先核定当前版本中 MCP 工具审批的实际控制入口、有效值和真实事件类型，再安排 A3。
- 若支持逐工具请求审批，仅在测试实例中将 `canvas_get_state` 配置为该模式；记录线程实际生效配置。不能只修改 `permissionMode` 后假定生效。
- 若现有通路不能产生此工具的真实审批请求，记录“该通路无法验证拒绝”，阻塞此项准入；不要拿其他工具的审批代证，也无需为测试新增服务器 API。

**尚未证：** MCP 默认 `approve` 的实际语义、覆盖顺序、事件类型、决议处理路径与线程内生效情况。

### 2. P1：拒绝反例的成功判据不足以证明“未执行”

**证据定位：** A3 预期“工具未返回成功数据”；A4 把未收到审批、超时、断连统一描述为 fail-closed。

工具执行成功但响应丢失，同样会表现为没有成功数据。客户端发出 decline、关闭浏览器或中止线程，也不自动证明服务端停止执行；更不等于已回滚。

**最小修订：** 将 A3 的通过条件写成：

1. 审批请求明确绑定该次工具名、参数及同一 thread/turn/item。
2. decline 被处理并形成终态。
3. 由现有工具入口或服务端调用记录确认该次调用没有进入执行。
4. 可选的单次允许分支使用独立调用标识，验证观测链确实能捕获执行。

监听须在调用前就绪；若无法观测工具是否执行，则拒绝效果仍为 **unknown**。无审批事件、响应丢失、终态缺失应分别记录，不能统称已经 fail-closed。取消后还需确认临时进程退出、无迟到调用及 busy/client 恢复。

**尚未证：** 服务端执行观测能力、取消传播、异步失败清理及断连后的工具生命周期。

### 3. P1：独立 CODEX_HOME 是配置隔离措施，尚非认证或完整权限边界

**证据定位：** probe 仅证明空配置的 `mcp_names=[]`；`start()` 的 `spawn()` 没有显式 `env` 或 `cwd`，按该片段会继承父进程环境与工作目录。`threadSettings(request)` 仍为 `workspace-write`。

A2 的“独立 HOME + 独立 CODEX_HOME”没有在冻结启动代码中体现。空配置也不能证明凭据环境变量、其他配置来源、原生工具或文件访问均已隔离。“受控临时模型调用授权”本身不是认证供应机制。

**最小修订：**

- 明确临时 app-server 的启动环境、工作目录及认证来源；认证材料不进入审阅日志。
- 在新进程、新线程上记录生效配置及来源，关联 `/agent/codex/mcp`、预热记录、实际模型可见工具与 thread ID；服务级列表不能代替线程工具清单。
- 将模型认证、工具审批、文件访问分别列为验证项。若声称只读隔离，应使用可验证的只读约束；否则准确称为“业务只读测试”，注明仍存在写能力。
- “仅启用画布 MCP”只限定 MCP 服务集合；若还暴露原生执行或写文件工具，须如实列出。

**尚未证：** 项目级及启动参数配置来源、线程覆盖是否生效、认证继承、原生工具集合和实际文件权限。

### 4. P2：Compact 投影应保留现有否定性边界，避免缩短输出时扩大解释权限

**证据定位：** `review_packet()` 已输出 `identity_verified=false`、媒体/几何/观众验证状态及全部 capability 限制；B 的字段说明没有明确要求保留这些字段。完整四阶段通过校验，也不意味着只看目标 Shot 和邻镜节选就获得了四阶段判断上下文。

**最小修订：**

- 投影直接保留现有 `review` 与 `capabilities` 的限制，不另造审批逻辑。
- 明确用途为定位和局部文本检查；跨阶段意图、空间关系及连续性验收需要补读对应批准原文。
- 邻镜节选附 Shot ID、全文 SHA 和可复现的原文位置；定位失败可以返回明确的“不可确定”，不必把整个读取判为失败。
- 哈希直接复用 packet 中对应对象的值；目标正文复用既有 `shots` 条目，避免再次解析或规范化。

这只是试点展示格式，无须升级成 WAR-35 正式 Schema。三层 SHA 对象不同，冻结材料没有证明 Authority 损坏。

**尚未证：** `self.check()`、`locked()`、`shot_sections()` 的具体行为；重复 ID、逐字保留、无业务写入等仍须实现后验证，既有 54 项通过不能替代新增测试。

先修订并执行 A2/A3、再开展同一 Agent 的 Compact 集成复测是合理顺序；纯离线 Compact 实现和确定性测试不依赖审批成功。当前阻塞点是**审批机制尚未对齐、拒绝无法证明未执行、启动与线程权限边界尚未闭合**，不是两个不同对象的 SHA 不相等。
### reviewer-director
**结论：targeted-revision｜P1**。这份设计把关键边界写清了，但 Compact Shot View 的判断窗口还不够可审阅，权限试验也不能预设原生 MCP 调用必然产生可拒绝的审批请求。当前没有依据接受候选或声称审批拒绝有效。

### Compact Shot View

- 设计要求目标镜头全文、前后镜节选和三类哈希，但没有冻结节选的提取规则、边界标记或无法定位时的输出形态。节选不足以支撑连续性判断时，读者可能误以为已检查邻镜。最小修订：节选必须是可追溯的原文并标明范围；定位不可靠时返回完整邻镜或明确“片段不可确定”，并要求读者需要连续性判断时查阅完整邻镜。
- 目标镜头全文加邻镜节选未必提供单镜头导演判断所需的窗口和角色知情信息。设计未明确这些信息如何从已批准材料中呈现，且不能靠模型补写。最小修订：列出支持目标镜头判断所需的批准来源字段；缺少角色知情或相关阶段依据时明确标为 unknown，并说明须查阅相应完整阶段文本。Compact 视图不能替代 Resume 或正式审阅。
- 设计列出 B candidate、Stage 文本和 Shot section 的 SHA，但调用者如何确认这些值各自对应的确切对象仍需落实。冻结记录特别说明 B candidate content SHA 与 `stages.shot.text` SHA 是不同对象。最小修订：每个 SHA 同屏标出对象名、字节/编码范围和来源字段；禁止跨对象比较，保留目标镜头文本自身 SHA。
- `format=war90-director-shot-preview-only-v0`、`read_only`、`authority`、`hashes`、`unknown` 和 `capabilities` 容易被误当成新正式数据契约或权限证明。最小修订：明确它们只是一次性只读投影的展示字段，不构成 WAR-35 Schema、身份认证、审批或工具权限依据；能力标记仅陈述投影能展示什么，不能证明运行时权限。

### 权限与顺序

A2 的独立 HOME 和 CODEX_HOME，以及 A3 的显式拒绝方案方向合理；但设计没有证明原生 MCP 工具一定产生 app-server approval event，也没有给出事件缺失、工具预先执行或审批与调用关联失败时的可判定证据。按设计中的 fail-closed 规则，这些情况应记为 **unknown/block**，不能声称隔离通过。配置原点探测只证明配置来源差异，不等同于线程工具范围或拒绝审批有效。

**先补齐 A2/A3 的事件与拒绝判定方案，再实现 Compact CLI**，顺序合理；但不应让这些试验成为 Compact View 的替代证据。Compact CLI 实施前还须固定投影字段与降级规则，确认它复用 `review_packet()` 的现有守门逻辑，且不产生正式 Schema 或第二套审批逻辑。当前材料未提供运行时权限证明、Compact 命令的确定性测试结果、邻镜及角色知情字段的实际来源，也未证明该投影在真实输出中能满足判断窗口要求；这些仍属未证项。
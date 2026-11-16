你是 WAR-90 的主审阅 Agent，主持独立方案审阅。先独立核对冻结证据，随后核对两个 Reviewer 原始报告，逐项解决分歧，拒绝缺乏源证据的主张，不能用投票替代核证。输出 accept/targeted-revision/block/unknown、必须/建议/延期及可直接实施的下一阶段。务必判断是否可以仅保存预检结果继续等待正式用户授权，是否有当前不应保留的安全错误。指出如何将 Canvas Agent 主入口与 Chat 半自动入口共享 Skill/CLI，但避免绕过权限和误选画布。不声称生产 Skill 安装完成或真实 MCP 权限通过；不签 B。中文 700-1400 字。

=== FROZEN ===
## Current candidate and decisions
# WAR-90｜Canvas 主入口接入预检与 Chat 第二入口边界（2026-11-16）

## 当前阶段与给人看的测试目的

**当前阶段**：已确认双入口架构后的 A 主入口接入准备，不是生产部署。

**给人看的测试目的**：验证 Canvas Agent 是否发现完整的七文件 Director Skill，如何在不改项目权威原件的情况下升级/回退；确认 Chat 半自动调用现有 Canvas Agent API 时如何避免误选多浏览器画布。Eric 独立 Codex 是备用，不是 Chat 日常必经 Agent。

## 观察与实测结果

**正式工作空间与服务现状**：Eric 的 Canvas Agent 用户配置的 workspace 是 /home/sean/.infinite-canvas/codex-workspaces/canvas-agent，而不等于默认初装的 site。项目七文件候选在 docs/planning/WAR-89/director-skill-v0-candidate，当前正式 workspace 未安装该候选。正式配置已将 codegraph 和 hindsight 的 mcpOverrides 置为 false；这只能证明配置，尚未验收正式线程的实际工具和 MCP 拒绝生效。检查时 canvas-lab-agent.service 与 canvas-lab-web.service 都为 inactive，本轮不擅自启动。

**真实原生 Skill 生命周期**：通过干净临时 HOME/CODEX_HOME、无认证文件和模型调用的 Codex app-server stdio 协议执行三次 skills/list(forceReload)。先装入七文件包，原生发现唯一 enabled Skill，错误为零；12 处相对 Markdown 引用全部有效。只在临时副本改动 shot-plan 阶段卡，刷新后仍能发现；回退旧版后七文件 SHA 全部恢复。证据 codex-skill-lifecycle-result.json，复现脚本 codex_skill_discovery_probe.py。此测试没有调用 Canvas Agent HTTP、没有生成或更改画布。单独 HTTP 测试受 Eric localhost 连接超时影响未能完成，不能冒称通过；失败尝试源码 isolated_skill_lifecycle.py 留作定位。

**七文件版本限制**：Canvas Agent 的 SkillStore.create/update 主要管理 SKILL.md 和可选 agents/openai.yaml；其 revision() 也只由这两个文件的内容算出，不能保证 stages/ 和 references/ 没有变更。Codex Skill 列表的 enabled 与 path 同样不是七文件的内容签名。建议正式安装统一由原件复制的完整文件包管理，冻结七份 SHA/相对链接/对应 Git 版本；先经审阅将标注“候选，未安装”的内容确定为发布版本。禁用运行中的专业 turn 后才进行更换/回退，不要误认为两次目录 rename 是一个原子事务，也不能假定活动 thread 自动刷新知识。完整包安装不应只靠 UI 粘贴 SKILL.md。

**现有 Canvas API 的目标归属风险**：/api/tools 目前不接受带原子校验的 clientId/expectedProjectId 写入目标。CanvasSession.targetClientId 选择正在执行的 Codex turn 的 boundClientId，或者最近激活的 activeClientId。/canvas/activate 只是变更焦点，不形成事务；多个浏览器窗口、其他 turn、重新连接都可能改变目标。当前 Chat 无法通过简单的工具参数锁定一个画布。

**Chat 只读前检**：新增纯数据函数 chat_read_preflight.verify（不发网络请求、不写 Canvas）。仅当确切一名浏览器客户端连接、Codex 不忙、用户明确指定的 project/client/node/Shot ID 与新近读到的快照和选区完全匹配、并且 Runtime 已批准 B/source/shot SHA 相符时返回只读上下文匹配；无论如何 can_write=false。它不能验证画布节点全文与 B 候选一致、真实审批身份，也不能在检查到写入间提供 CAS。13 项离线测试通过（多窗口、忙碌、ID/版本/选区错误全部拒绝），源码与测试在 chat_read_preflight.py、test_chat_read_preflight.py。

**既有 Canvas Agent 单元回归**：对 Skills Store、Codex Client、CanvasSession 三个相关模块实际运行 84 项测试，84/84 通过。测试日志 native-agent-targeted-tests.log。未修改正式 Canvas Agent 源码和服务。

## 两入口最小权限与归属矩阵

| 能力 | A · Canvas 主入口 | B · Chat 协作入口 | 当前边界 |
| --- | --- | --- | --- |
| 导演知识 | 原生 Codex 加载可发现的 7 文件 Director Skill | DCR 读取 Eric 同一原件 | 主入口正式安装未执行，必须对齐完整包 SHA |
| 只读 B 文案 | Runtime review-shot/review-pack | 相同 Runtime CLI | 只读 CLI 已验证，新增 review-shot 的原生 Agent 复测未执行 |
| 画布和选区 | 内置 infinite-canvas MCP；turn 绑定客户端 | 现有 Agent HTTP /api/tools；单客户端且显式项目/选区 | 已有隔离画布各自读测，当前不在正式画布运行 |
| 节点写入 | 必须有用户授权、实际工具权限及版本校验 | 不由只读 preflight 授权；须用户明确确认唯一画布 | Chat HTTP 缺少原子 client/project 绑定，不能声称无竞态 |
| prepare/submit | 当前专业 Agent 经 Runtime 保存候选，不让 Runtime 启动第二 Agent | 相同 CLI，保留 Chat 意见来源 | 真实修改/B 复审未执行 |
| A/B 用户批准 | 真人显式确认，不许模型自签 | 同一规则，记录 Chat 输入来源 | 正式身份核验未实现 |
| 媒体/ComfyUI/H3 | 另行明确授权 | 本轮不调用 | 未测试 |
| 并发 | 原生 busy 与 Runtime 文件锁是局部门禁 | 多窗口/忙碌/不一致拒绝继续 | 没有跨入口统一 CAS 和事务 |

重要：Canvas Agent 代码中的 default_tools_approval_mode=approve 不等于每次 MCP 工具调用都会请求真人允许。之前主审已明确当前 codex_approval 事件不能直接作为 MCP 工具执行拒绝的证明，正式工具授权须单独核证。

## 正式安装提案（未执行）

1. 用户确认安装与启动时机后，确认当前真实工作空间、无活动任务、目标画布归属和现有 Skill 安装状态；不得默认 site、不得覆盖同名目录。
2. 将七文件原件做独立 staged 副本，扫描引用和逐文件 SHA，与冻结 Git 版本比对，保存来源。部署到当前工作空间的普通目录，避免符号链接；旧版本保留可恢复备份。
3. 在新的原生线程中强制重新发现 Skill，并验证七文件实际内容与权限范围。失败恢复旧目录，保留失败记录，不篡改已有候选/B。
4. 先以隔离画布执行只读 review-shot 与 Canvas 选区一致性测试，再按授权决定是否开放正式操作。Chat 路径先读并核对 project/client/selection/B/Source/Shot，检查失败立即停；多客户端或 Codex 忙碌不写入。
5. 跨入口原子路由、revision/CAS、正式 UI 映射留 WAR-35/WAR-37；WAR-90 不复制第二套存储、审批或导演 Agent。

**本阶段验收状态**：七文件 Skill 原生发现、临时升级、回退通过；Chat 只读前检离线测试通过；正式服务没有启动、生产 Skill 没有安装、MCP 真实审批拒绝和双入口真写入都未通过验收。没有新 Shot02 修改意见，未生成候选、不生成媒体、不自签 B。

## Seven-file native exact result
{
  "probe": "direct Codex app-server skills/list used by Canvas Agent, without network or model",
  "result": "PASS",
  "source_relative_paths_hash": {
    "SKILL.md": "3eee7d6f3c3032fc43e97b86a9606f8ae77943fa377aa2f56e2770c2b76e8676",
    "references/knowledge-index.md": "4d8edcb664659d78f897aa7baa8c1f275a57b5ff128ab433c95745b32a5e2519",
    "references/review-method.md": "72b23f163fe1fdea6a547d5b47f39392ba0b9b63b814a7a285db4a7df0e88e8e",
    "stages/beat.md": "6e81d45db1d0249cf33a200135f0ab790a49b65d92c7d036b0e253ac978121a1",
    "stages/blocking.md": "2663d5acc282d636400539aecc643871c26c12867c5d480d9c02793ad45c5563",
    "stages/intent.md": "ac07ecb95cbd511888911a0f85aa08f5fee2824cbf8e23749ef0d6ffec065a38",
    "stages/shot-plan.md": "fa0c7d4cc39fdf6b5df9c8a0e3e9b0ee6eafa921142b5a5f07efcdc8cf989476"
  },
  "source_reference_links_checked": [
    "SKILL.md: stages/intent.md",
    "SKILL.md: stages/beat.md",
    "SKILL.md: stages/blocking.md",
    "SKILL.md: stages/shot-plan.md",
    "SKILL.md: references/review-method.md",
    "SKILL.md: references/knowledge-index.md",
    "references/review-method.md: knowledge-index.md",
    "stages/beat.md: ../references/knowledge-index.md",
    "stages/blocking.md: ../references/knowledge-index.md",
    "stages/intent.md: ../references/knowledge-index.md",
    "stages/shot-plan.md: ../references/review-method.md",
    "stages/shot-plan.md: ../references/knowledge-index.md"
  ],
  "initial_discovery": {
    "name": "director-skill-v0-candidate",
    "path_matches_workspace": true,
    "enabled": true,
    "errors_count": 0
  },
  "synthetic_v2_discovery": {
    "name": "director-skill-v0-candidate",
    "path_matches_workspace": true,
    "enabled": true,
    "errors_count": 0
  },
  "rollback_discovery": {
    "name": "director-skill-v0-candidate",
    "path_matches_workspace": true,
    "enabled": true,
    "errors_count": 0
  },
  "reloaded_skill_path_same": true,
  "seven_file_original_restored": true,
  "models_called": false,
  "canvas_agent_http_called": false,
  "production_modified": false,
  "no_auth_files_or_codex_global_config_used": true,
  "limitations": [
    "7-file sibling update has same Skill path; skills/list alone does not attest sibling hashes",
    "directory exchange requires quiesced thread; two renames have short unavailable window",
    "active Codex thread may cache previous Skill and must not be hot-swapped mid-turn",
    "Canvas Agent HTTP path not verified here due unavailable loopback"
  ]
}

## Current source tree file validation
Not separately available; see native manifest
## Chat pure-data gate
#!/usr/bin/env python3
"""Pure-data Chat→Canvas read preflight; never issues HTTP, MCP or Canvas writes.

A matching result is NOT write authorization, not a cross-endpoint CAS, and not
cryptographic proof that a rendered Canvas node matches a Director B candidate.
"""
import json

class PreflightBlocked(ValueError):
    pass

def verify(health, state, selection, authority, *, project_id, client_id,
           node_id, expected_shot_id, approved_b_id, source_sha256, shot_sha256):
    def require(test, reason):
        if not test: raise PreflightBlocked(reason)
    require(health.get('ok') is True and health.get('hasCanvas') is True,
            'no connected Canvas state')
    require(health.get('clients') == 1, 'not exactly one Canvas browser client')
    require(health.get('codexBusy') is False, 'Canvas Codex turn busy or unknown')
    require(project_id and client_id and node_id and expected_shot_id, 'explicit project/client/node/shot identity required')
    require(state.get('projectId') == project_id, 'project ID changed or missing')
    require(state.get('clientId') == client_id, 'Canvas client ID changed or missing')
    nodes = state.get('nodes') or []
    require(sum(n.get('id') == node_id for n in nodes) == 1, 'target node missing or duplicate')
    selected = state.get('selectedNodeIds') or []
    require(selected == [node_id], 'exactly one intended Canvas selection required')
    chosen = (selection or {}).get('nodes') or []
    require(len(chosen)==1 and chosen[0].get('id')==node_id,
            'selected node readback disagrees')
    require(authority.get('pilot_only') is True,
            'expected WAR-90 pilot projection')
    require(authority.get('authority',{}).get('approved_B_id') == approved_b_id,
            'approved B identity changed')
    require(authority.get('source',{}).get('sha256') == source_sha256,
            'source version changed')
    target=authority.get('target_shot') or {}
    require(target.get('text_sha256') == shot_sha256,
            'target Shot text SHA changed')
    require(target.get('id') == expected_shot_id, 'target Shot ID mismatch')
    require(target.get('text'), 'target Shot full text missing')
    require(authority.get('capabilities',{}).get('production_approval') is False,
            'pilot-only approval boundary missing')
    require(authority.get('capabilities',{}).get('write_canvas') is False,
            'view claims write capability unexpectedly')
    return {'read_context_verified': True, 'can_write': False,
            'reason': 'No atomic client/project binding or write approval in /api/tools',
            'project_id':project_id, 'target_node_id':node_id,
            'target_shot_id':expected_shot_id,
            'approved_B_id':approved_b_id,
            'source_sha256':source_sha256,'shot_sha256':shot_sha256,
            'not_verified':[
                'whether the rendered Canvas node text is the complete approved B source',
                'identity of user authorizing a future mutation',
                'no race after this check (server has no cross-entry CAS)',
                'permissions of native Codex MCP tools']}

if __name__ == '__main__':
    # Designed as a reusable pure function; no CLI takes the Agent access token.
    print('Pure-data only: import verify() with fresh read results; never treat as write permission.')

## SkillStore entry/update/revision implementation
export class SkillStoreError extends Error {
    override name = "SkillStoreError";
    constructor(message: string, readonly statusCode: 400 | 404 | 409 | 500) {
        super(message);
    }
}

/** 只管理站点工作空间下 `.agents/skills` 中的画布专属 Skill。 */
export class SkillStore {
    readonly workspacePath: string;
    readonly skillsPath: string;
    private writeQueue: Promise<unknown> = Promise.resolve();

    constructor(workspacePath: string) {
        this.workspacePath = path.resolve(workspacePath);
        this.skillsPath = path.join(this.workspacePath, ".agents", "skills");
    }

    /** 判断 Codex 返回的绝对路径是否属于本 Store 的标准 Skill 入口。 */
    isManagedPath(filePath: string) {
        if (!path.isAbsolute(filePath)) return false;
        const relative = path.relative(this.skillsPath, path.resolve(filePath));
        const segments = relative.split(path.sep);
        return segments.length === 2 && validName(segments[0]) && segments[1].toLowerCase() === "skill.md";
    }

    /** 读取一个可编辑 Skill 的正文与界面元数据。 */
    async get(name: string): Promise<ManagedSkillDetail> {
        try {
            await this.writeQueue.catch(() => undefined);
            const paths = await this.safeExistingPaths(name);
            return await this.readDetail(name, paths.skillFile, paths.openAiFile);
        } catch (error) {
            throw storeError(error, "读取 Skill 失败");
        }
    }

    /** 创建新的画布专属 Skill。 */
    create(input: CreateManagedSkillInput) {
        return this.mutate(async () => {
            const name = skillName(input?.name);
            const description = skillDescription(input?.description);
            const instructions = skillInstructions(input?.instructions);
            const skillInterface = skillInterfaceValue(input?.interface, name);
            await this.ensureRoot();
            const skillDir = path.join(this.skillsPath, name);
            const existing = await lstatOptional(skillDir);
            if (existing) {
                if (existing.isSymbolicLink()) throw new SkillStoreError("Skill 目录不能是符号链接或目录联接", 400);
                throw new SkillStoreError("同名 Skill 已存在", 409);
            }
            await fs.mkdir(skillDir);
            try {
                const skillFile = path.join(skillDir, "SKILL.md");
                await writeFileAtomic(skillFile, serializeSkill({ name, description }, instructions));
                const openAiFile = path.join(skillDir, "agents", "openai.yaml");
                if (skillInterface) await this.writeOpenAi(openAiFile, {}, skillInterface);
                return await this.readDetail(name, skillFile, openAiFile);
            } catch (error) {
                await fs.rm(skillDir, { recursive: true, force: true }).catch(() => undefined);
                throw error;
            }
        });
    }

    /** 通过 revision 防止覆盖已被其他窗口或外部编辑器修改的内容。 */
    update(nameValue: string, input: UpdateManagedSkillInput) {
        return this.mutate(async () => {
            const name = skillName(nameValue);
            const description = skillDescription(input?.description);
            const instructions = skillInstructions(input?.instructions);
            const expectedRevision = expectedRevisionValue(input?.expectedRevision);
            const interfaceInput = input?.interface;
            const skillInterface = interfaceInput === undefined ? undefined : skillInterfaceValue(interfaceInput, name);
            const paths = await this.safeExistingPaths(name);
            const currentSkill = await readSkill(paths.skillFile, name);
            const currentOpenAi = await readOpenAi(paths.openAiFile, name);
            assertRevision(expectedRevision, revision(currentSkill.raw, currentOpenAi.raw));
            const frontmatter = { ...currentSkill.frontmatter, name, description };
            await writeFileAtomic(paths.skillFile, serializeSkill(frontmatter, instructions));
            if (interfaceInput !== undefined) {
                try {
                    await this.writeOpenAi(paths.openAiFile, currentOpenAi.data, skillInterface);
                } catch (error) {
                    if (!await restoreSkillFiles(paths.skillFile, currentSkill.raw, paths.openAiFile, currentOpenAi.raw)) {
                        throw new SkillStoreError("Skill 更新失败且无法完全恢复，请检查本地文件", 500);
                    }
                    throw error;
                }
            }
            return await this.readDetail(name, paths.skillFile, paths.openAiFile);
        });
    }

    /** 删除 revision 仍匹配的画布专属 Skill。 */
    delete(nameValue: string, expectedRevisionValueInput: string) {
        return this.mutate(async () => {
            const name = skillName(nameValue);
            const expectedRevision = expectedRevisionValue(expectedRevisionValueInput);
            const paths = await this.safeExistingPaths(name);
            const currentSkill = await readSkill(paths.skillFile, name);
            const currentOpenAi = await readOpenAi(paths.openAiFile, name);
            assertRevision(expectedRevision, revision(currentSkill.raw, currentOpenAi.raw));
            await assertTreeHasNoLinks(paths.skillDir);
            const realRoot = await fs.realpath(this.skillsPath);
            const realSkill = await fs.realpath(paths.skillDir);
            if (!inside(realRoot, realSkill)) throw new SkillStoreError("Skill 路径不安全", 400);
            await fs.rm(realSkill, { recursive: true });
        });
    }


function revision(skillRaw: string, openAiRaw: string) {
    return crypto.createHash("sha256").update(skillRaw).update("\0").update(openAiRaw).digest("hex");
}


## CanvasSession target routing implementation
    private get canvasState() {
        return this.clients.has(this.targetClientId) ? this.canvasStates.get(this.targetClientId) || null : null;
    }

    /** 获取当前 turn 绑定或最近激活的网页客户端。 */
    private get targetClientId() {
        return this.boundClientId || this.activeClientId;
    }

    async callTool(name: unknown, rawInput: unknown) {
        if (!isToolName(name)) throw new Error(`未知工具：${String(name)}`);
        logger.info("MCP tool called", { name, input: rawInput, targetClientId: this.targetClientId });
        const input = parseToolInput(name, rawInput) as Record<string, unknown>;
        if (SITE_TOOLS.has(name)) {
            if (!this.clients.size) throw new Error("当前没有已连接网页");
            return await this.requestCanvasTool(name, input);
        }
        const readTool = ["canvas_get_state", "canvas_get_selection", "canvas_export_snapshot"].includes(name);
        if (readTool && (!this.clients.size || !this.canvasState)) throw new Error("当前没有已连接画布");
        if (name === "canvas_get_state" || name === "canvas_export_snapshot") return compactCanvasState(this.canvasState);
        if (name === "canvas_get_selection") {
            const ids = new Set(this.canvasState?.selectedNodeIds || []);
            return { nodes: (this.canvasState?.nodes || []).filter((node) => ids.has(node.id)).map(compactNode) };
        }
        if (name === "pose_atlas_insert") {
            if (!this.clients.size || !this.canvasState) throw new Error("请先打开并连接目标画布");
            return await this.requestCanvasTool(name, input);
        }
        if (name === "canvas_create_attachment_nodes") return await this.createAttachmentNodes(input as { attachmentIds: string[]; x?: number; y?: number; gap?: number; direction?: "row" | "column" });
        if (!this.clients.size) throw new Error("当前没有已连接画布");
        const request = buildCanvasToolRequest(name, input, this.canvasState);
        return await this.requestCanvasTool(request.name, request.input);
    }


## API tool route
    app.post("/api/tools", route(async (req, res) => res.json({ ok: true, result: await session.callTool(req.body?.name, req.body?.input || {}) })));
    app.get("/agent/codex/workspace", (_req, res) => {
        const workspace = ensureSiteWorkspace(config);
        res.json({ ok: true, workspace, conversation: session.conversationStateSnapshot });
    });

## Agent targeted unit tests
te and later updates (0.649382ms)
✔ 对话 revision 单调递增且 MCP 全部进入终态前保持 preparing (0.434722ms)
✔ 可选 MCP 失败进入 warning，画布 MCP 失败进入 failed (0.194804ms)
✔ 无启动通知和工具的清单项不视为已连接 (0.102051ms)
✔ Codex 写操作在多窗口之间互斥且不能与运行 turn 并发 (0.127498ms)
✔ Skill draft generation broadcasts shared busy state and restores the previous thread (0.635917ms)
✔ Skill draft busy state preserves the previous turn replay until history acknowledges it (0.62697ms)
✔ a bound client remains the tool target while focus changes (1.094152ms)
✔ a disconnected bound client never falls back and can resume with the same client id (1.817573ms)
✔ 新连接会回放当前运行 turn 的最新事件快照 (0.634805ms)
✔ 同一 item 的多次增量只回放最新内容 (0.433519ms)
✔ 增量事件重放时转换为完整文本快照 (0.452134ms)
✔ 并行 item 更新后重放仍保留开始顺序和命令字段 (0.972365ms)
✔ 长 turn 不会淘汰仍在更新的活动条目快照 (1.525838ms)
✔ 内置生图事件会回放展示但标记为不可重复执行 (0.669209ms)
✔ turn 结束后保留实时快照，直到网页确认权威历史 (1.100915ms)
✔ 开始下一 turn 时只回放当前 turn 的事件 (0.853263ms)
✔ 同一用户消息从 pending 绑定 turn 后只回放最终版本 (0.595802ms)
✔ 切换活动线程会清除上一线程的实时快照 (0.587748ms)
✔ 创建、读取和更新画布专属 Skill (37.537169ms)
✔ revision 不匹配时拒绝覆盖或删除 (11.775053ms)
✔ 清空界面字段时保留未由画布管理的 openai 元数据 (17.576533ms)
✔ 名称、正文大小和默认提示词均经过校验 (1.920269ms)
✔ 更新校验失败时不会提前改写 SKILL.md (7.80619ms)
✔ 拒绝读取非对象格式的 openai.yaml (9.859162ms)
✔ 不完整更新请求返回校验错误而不是运行时异常 (1.517538ms)
✔ 空 interface 元数据读取为空 (10.333197ms)
✔ 读取或修改不存在的 Skill 不会创建目录 (2.244119ms)
✔ 更新后只保留完整文件且不遗留临时文件 (15.862798ms)
✔ 拒绝读取非对象格式的 interface 元数据 (8.931421ms)
ℹ tests 84
ℹ suites 0
ℹ pass 84
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 735.153623

## Prior architecture direction
# Canvas Lab｜Director Skill 双入口执行决策（2026-11-16）

决策来源：用户明确要求 **Eric 上 Canvas Agent 为主力，ChatGPT 可以半自动参与，Eric 独立 Codex 为备用**。

## 目标与适用边界

Canvas Lab 的真实创作入口有两个，复用同一导演方法与工程工具，而非为 Chat 与 Canvas 分别维护两套导演引擎。每次具体修订由一个执行者负责专业判断，外围独立 Reviewer 只负责设计/代码/导演产物的质量检查。单 Agent 是一次任务的执行拓扑，不是限制用户只有一个入口。

### 路径 A：主力，Eric Canvas Agent（画布内置 Codex）

- 用户在 Canvas Lab 中使用 @画布元素、选区、节点引用与对话；Canvas Agent 自己加载可发现的 Director Skill（正式安装仍未批准），按阶段调用本地 Director Runtime CLI 的只读、准备与提交命令，并直接通过既有 infinite-canvas MCP 读写所连接的画布。
- 已在**隔离** Canvas Agent 真实验证 Skill 发现/选择、原生 Codex turn、按需读 Shot Plan 知识、Runtime review-pack 和 Canvas MCP 双读取，结论是只读 no-handoff。尚未在现有正式 Canvas Agent 上安装该候选 Skill；媒体、真实候选写入、人类 B 重审未证。
- Canvas Agent 会根据启动环境继承 CODEX_HOME 配置。独立对话不等于配置隔离；正式 Agent 启用状态不能依据一次隔离 smoke 的全局配置继承现象判断。

### 路径 B：协作，ChatGPT → Eric

- ChatGPT 负责讨论设计、召集外围审阅 Agent、查阅 Eric 的本地权威 Markdown、组织半自动审阅和明确授权范围的画布操作。
- ChatGPT 通过 DCR 显式访问 Eric；可以读取适用 Director Skill 文件，执行**同一** Director Runtime CLI，必要时通过**现有** Canvas Agent API 控制已确认的画布，或将一段受控任务交给 Canvas Agent 原生对话。没有为 Chat 新建长期运行的 Director Agent 或专门的 HTTP 桥接服务。
- Chat **不能自动将远端 Eric Skill/MCP 当成本会话的内建工具**：实际需要显式读取 Skill 文件、经远程命令执行 CLI 或通过已有 API 操作画布。Chat 路径的 API 实验曾在独立测试画布验证节点创建、选区、差异回显；完整的真实用户修改与 B 再批准仍未测。
- Chat 没有 Canvas UI 内置 @ 元素交互语义；如需访问元素，必须显式核对项目/节点/选区 ID、B/Source/Shot 版本及实际 Canvas Agent 连接归属。不能凭 Chat 文本里的“@某元素”假设已解析到当前画布，也不能自动回退到未知的最近画布。

### 备用执行端：Eric 独立 Codex

- 仅用于画布内 Agent 不可用、自动化批处理、独立验证/代码审阅等情况；不作为主力和 Chat 的日常必经中转。
- 备用执行时仍指向同一套 Skill、Runtime CLI 和被授权的 Canvas Agent 工具；不用自己的另一本专业规范或独立 DirectorPlan 状态。
- 多 Reviewer + 主审阅 Agent 是**外围质量控制**，不加入每次导演运行的调用链，也不代签用户 A/B。

## 共享的单套能力与数据

1. **Director Skill 权威**：Eric 项目中的七文件专业 Skill；Canvas Agent 安装的是可发现副本/引用，Chat 按阶段读取原件。正式安装需七文件 SHA 清单、相对路径可用性与更新回退检查，不能让两入口使用不一致版本。
2. **Director Runtime CLI**：同一实现、同一试点权限及来源校验；只读视图不生成新候选，prepare/submit 也不自行启动专业模型。未来正式持久化归 WAR-35，不在此复制第二套数据契约。
3. **Canvas 工具**：Eric 已有 Canvas Agent 的 infinite-canvas MCP / HTTP 工具；Chat 用 HTTP/API 协作并不意味着它拥有 UI 内置 Codex 的一切上下文，Canvas 内置 Agent 更适合直接消化 @引用和画布选择。
4. **用户批准与材料**：Eric 本地 Markdown/Runtime 冻结证据为权威，Linear 是索引与状态；Canvas 文本节点是展示投影，不是最终的 B 授权记录。Chat 审阅意见、Canvas UI 反馈要保留各自真实来源，不得互相冒充。

## 并发与操作边界（当前是规程，尚非已实现锁机制）

- **同一画布的一次修改只由一个主控路径执行**；先核项目 ID、实际连接的 clientId、当前选区与 B/Source/Shot SHA。Chat 不应在 Canvas Agent 忙于同一画布时并发提交修订。冲突或版本变化时停止，重新读状态并获取人工确认。
- 现有 Canvas Agent 的 busy 状态与 Runtime 文件锁只覆盖各自局部操作，**不能声称已实现跨 Chat/Canvas 的通用编辑锁、事务或 revision/CAS**。这些工程语义不在 WAR-90 偷偷落地，后续与 WAR-35/WAR-37 对齐。
- 不得凭一个随机项目名、最近画布或截断节点预览自动提交修改；要从实际 UI 选区/@引用或受用户确认的精确 ID 发起。
- 不从本轮实验向生产安装技能、切换服务、修改用户 Canvas、生成媒体或自动签 A/B。后续正式写操作必须明确授权及回滚范围。

## 当前真实验收（截至 2026-11-16）

- 路径 A 原生 Skill+Runtime+MCP **只读 PASS（有限）**；Codegraph/Hindsight 在隔离试验中的意外暴露，导致正式工具隔离**未验收**。
- 路径 B Chat→DCR→Canvas Agent API **独立测试画布读写/选区 PASS（有限）**；Chat 直接用 Skill 的完整专业修订及同一 Runtime 提交新 B **未验收**。
- 备用独立 Codex→Skill+CLI+MCP **只读 PASS（有限）**。
- Runtime 新增的目标 Shot 只读 compact 视图为试点能力，尚无原生 Agent 复测。生产集成仍未执行；真实 Shot02 用户表示暂时没有修改意见，不得伪造修订候选。
- 用户真正的修订→邻镜复检→Canvas 差异→再次人审 B **未验收**，按真实需求择期测试，不人为制造需求。

## 下一步优先级

1. 在 WAR-90 收口当前的 Runtime compact Shot 只读视图与多 Agent 代码审阅，不扩大到新 schema。
2. 独立核验 Codec/Codex 配置来源（空 CODEX_HOME 与用户环境已对照），在已有 Canvas Agent 工具审批路径上找到可验证的拒绝/拒执行证据；如果 MCP 工具默认自动通过且客户端没有可拒绝事件，记录**当前通路无法证明拒绝**，不为实验擅改生产权限机制。
3. 形成路径 A 与 B 的共同运行说明与最小权限矩阵；确认正式 Skill 安装/新会话/回滚的实际边界后，再让用户决定何时在正式 Canvas 使用。
4. 真正有用户修改要求时，选择一个入口完成隔离的完整改动闭环，外围多 Agent 审阅结论只能提供质量建议，不得代替用户 B 审批。

用户的主次排序属于已确认决策，不重新将 Chat 设为专业 Agent 的必经路由。


=== INDEPENDENT REPORTS ===
### reviewer-skill-lifecycle
# 结论：targeted-revision

冻结包足以支持“有限的原生 Skill 生命周期通过”和“Chat 只读前检通过”，但不足以证明 Canvas Agent HTTP 路由、正式安装或生产操作已通过。对 WAR-90 的阶段性预检可有条件接受；不得据此批准 A/B 或开放 Chat 写入。

## P0

无。提供的证据没有显示已经发生生产写入、误改画布或自动批准；当前只读 gate 也明确返回 `can_write=false`。

## P1

1. **原生 Codex Skill 发现通过，不代表 Canvas Agent HTTP 集成通过。**  
   可复现证据：`codex-skill-lifecycle-result.json` 记录干净临时环境下 `skills/list(forceReload)` 三次发现均无错误、临时升级后发现仍在、回退后七文件 SHA 恢复；同时明确 `canvas_agent_http_called=false`。HTTP 尝试因 localhost 超时未完成。  
   **最低修改：** 在隔离环境完成一次 Canvas Agent HTTP 路由验证，记录实际 workspace、发现结果和错误；在此之前将 HTTP 路径标为未验证。不要把原生 skills/list 的 PASS 延伸为 Agent HTTP PASS。

2. **多文件 Skill 的 revision 与回退治理不完整。**  
   可复现证据：给出的 `SkillStore.revision()` 只对 `SKILL.md` 和可选 `agents/openai.yaml` 的原始内容计算 SHA；`update()` 也只更新这两者。它不会发现 `stages/` 或 `references/` 的变更。原生 Skill 列表中的 `enabled` 和 `path` 同样不提供七文件内容签名。  
   **最低修改：** 将正式安装候选固定为完整七文件发布包：对每个相对路径记录 SHA，并绑定到已审阅的源码 Git 版本。部署前校验完整清单；升级或回退后再次校验。未有多文件版本校验的 Store revision 不得作为包版本或回退成功的证明。

3. **目录替换不构成原子更新，活动 turn 可能继续使用旧知识。**  
   可复现证据：冻结结果明确说明两次 rename 之间存在不可用窗口，且活动 Codex thread 可能缓存旧 Skill；测试是在临时副本完成，不能证明正式 workspace 的活动线程会刷新。  
   **最低修改：** 替换或回退前确认相关专业 turn 已停止，并在新线程强制重新发现后核对七文件清单。保留旧版本备份和失败记录；不得在活动 turn 中热切换。

4. **Chat gate 是只读一致性前检，不是原子写授权。**  
   可复现证据：`chat_read_preflight.verify()` 只检查传入的健康状态、project/client/node/selection 与 B、Source、Shot 标识；通过时仍返回 `can_write=false`。它不发网络请求，不验证 Canvas 节点全文与批准 B 一致，也无法阻止检查之后状态改变。源码路由为 `/api/tools` → `session.callTool(...)`，没有 client/project 的原子绑定参数。`CanvasSession.targetClientId` 使用 turn 绑定客户端或最近激活客户端；`/canvas/activate` 也不创建事务。  
   **最低修改：** 保持 gate 为只读前检。不要把通过结果解释成可写许可，也不要以该结果声称消除了竞态。Chat 写操作继续受阻，直到现有 API 提供并验证原子目标绑定及相应授权路径；该工程能力属于后续 WAR-35/WAR-37 范围。

5. **配置声明不等于正式工具权限已经验证。**  
   可复现证据：正式配置将 codegraph、hindsight 的 `mcpOverrides` 置为 false，但冻结包指出正式线程的实际工具列表和拒绝生效尚未验收。`default_tools_approval_mode=approve` 也不能证明每次 MCP 调用会请求真人批准。  
   **最低修改：** 将正式 MCP 工具可见性、实际拒绝路径、以及真实写入权限分别标为未验证；在隔离环境取得对应运行证据后再更新结论。

## P2

- **候选发布版本的名称和状态容易误读。** 目录名 `director-skill-v0-candidate` 仍明确是候选，冻结包也说明正式 workspace 未安装它。  
  **最低修改：** 在候选发布清单上标明候选身份、来源 Git 版本、七文件 SHA、审阅状态和“未安装”；经审阅确定发布版本后再使用发布标识，避免仅凭目录名或 Codex Skill 名称推断版本。

- **路径治理的证据限于给出的临时测试。** 冻结包记录正式 workspace 是 `/home/sean/.infinite-canvas/codex-workspaces/canvas-agent`，并说明它不是默认 site；正式服务当时 inactive，候选未安装。  
  **最低修改：** 将未来安装前的 workspace、活动任务、现有同名 Skill 和目标画布检查作为发布记录项。当前证据不支持宣称正式工作区已安装、已运行或已回退。

- **84 项测试是定向单元回归，不覆盖端到端权限语义。** 日志显示 Skills Store、Codex Client、CanvasSession 的 84 项测试通过；不能据此证明真实 MCP 拒绝、Chat 跨端竞态控制或生产安装安全。13 项纯数据 gate 测试同样不能覆盖网络读写时序。  
  **最低修改：** 保留测试范围描述，不把单元测试结果升级为生产验收结论。

## 当前可确认与仍未知

可确认的范围：

- 七文件 Skill 在临时 CODEX_HOME 下经原生 `skills/list(forceReload)` 发现；临时升级和回退后仍可发现，七文件恢复原 SHA。
- Chat 纯数据只读 gate 的 13 项离线测试通过；该 gate 明确不授予写权限。
- 三个相关模块的 84 项定向测试通过。
- 按冻结包记录，Canvas Agent 和 Web 服务当时均 inactive；正式候选 Skill 未安装。

仍未知的范围：

- Canvas Agent HTTP 路由是否能发现并使用这份多文件 Skill。
- 正式 workspace 中的安装、完整七文件校验、升级、失败恢复及回退是否实际完成。
- 正式线程是否确实看不到 codegraph/hindsight，以及 MCP 工具是否存在可验证的拒绝执行路径。
- Chat 经现有 HTTP API 的真实写入是否能原子锁定指定 client/project；当前源码和 gate 证据不支持这一点。
- Canvas 节点全文是否与批准的 B 候选完全一致、批准用户身份如何核验、以及 A/B 真人审批闭环是否完成。
- 真实用户修改、Canvas 差异、B 再审、媒体与 ComfyUI/H3 操作均未由本冻结包证明。

**验收边界：** 可记录为“临时环境原生 Skill 生命周期通过；Chat 只读前检通过”。Canvas Agent HTTP、正式安装、生产权限拒绝和双入口原子写入均保持未验证；不批准 A/B，不据此扩建新 Agent 或授权 Chat 写入。

### reviewer-canvas-ownership
## 结论

**targeted-revision**。当前材料可支持“主入口安装前准备”的有限结论。Chat 写入与生产权限验收维持 **block**，真实 HTTP 路由及 MCP 拒执行能力为 **unknown**。

仅依据本消息冻结材料与源码片段审阅，未调用工具、未执行复现、未批准 A/B。

- **原生 Codex `skills/list` 已通过**临时七文件包发现、刷新与回退，manifest 记录七份 SHA 恢复。
- **本轮 Canvas Agent HTTP 路径未测通**。此前隔离 API 读写结果不能覆盖本轮候选与正式配置。
- **生产安装未发生**，正式服务未启动。84 项单元测试与 13 项离线 gate 测试均不能替代生产路由和权限验收。

## P1 问题

### 1. Node 与 Shot 缺少关联验证，成功结果扩大了实际证明范围

**证据**

`verify()` 分别验证 Canvas 中的 `node_id` 和 Runtime 中的 `expected_shot_id`，没有验证二者之间的映射。`selection` 也仅比较节点 ID，未携带或核对 client/project/version。

**可复现输入**

在有效 fixture 中，把 Canvas 节点及选区换为另一个合法节点 N2，并将参数 `node_id` 同步改成 N2。保留原 Shot S1、B 与 SHA。只要其他字段匹配，函数仍返回 `read_context_verified=True`，即使 N2 展示的是 S2。

**最低修改**

将成功语义明确收窄为“所提供身份字段分别匹配”，并在 `not_verified` 中加入 Node→Shot 映射与 selection 的 client/project 归属。若继续宣称完整上下文匹配，则必须取得并校验可信映射及读取来源信息。WAR-90 可以先收窄声明，无需扩建 schema。

### 2. B 与 SHA 允许缺失值相等后通过

**证据**

仅 project/client/node/shot 参数检查非空。以下比较允许两侧均为 `None`：

```python
authority.get('authority', {}).get('approved_B_id') == approved_b_id
authority.get('source', {}).get('sha256') == source_sha256
target.get('text_sha256') == shot_sha256
```

**可复现输入**

使用其余字段有效的输入，删除 authority 中对应 B、source SHA、Shot SHA，将三个预期参数设为 `None`。保留目标 Shot ID、非空 text 及要求的 capability 字段。上述校验全部通过。

**最低修改**

比较前校验 B ID 为非空有效标识，两个 SHA 为合法的 64 位十六进制字符串。增加缺失值、空值和非法格式回归用例。若 `text_sha256` 被用于证明返回全文的完整性，还需对返回 `text` 重新计算摘要并核对。

### 3. “新近快照”和单客户端检查无法证明同一次读取上下文

**证据**

函数没有时间、快照 revision 或统一读取标识。`health`、`state`、`selection`、`authority` 都是调用方传入的独立对象。

**可复现时序**

1. 保存客户端 C1、项目 P1 的有效数据。
2. C1 切换项目，或另一标签连接并激活。
3. 将保存的数据再次传给 `verify()`。

返回结果仍为成功。该问题同样影响只读结果归属，即使始终保持 `can_write=False`。

**最低修改**

删除函数能够验证“新近”的表述，明确它只验证输入数据内部的部分一致性。将读取时间、来源关联和跨请求一致性列为未验证项。调用规程可以要求立即重读，但其竞态限制仍需保留。

### 4. Chat HTTP 写入缺少请求级目标约束，人工确认无法消除路由竞态

**证据**

`/api/tools` 仅传入工具名和 input。目标由共享的：

```typescript
this.boundClientId || this.activeClientId
```

决定。展示的路由与 `callTool()` 入口没有强制执行 `chat_read_preflight`，也没有校验期望 client/project/revision。

**可复现时序**

- Chat 读取 C1/P1 并完成前检。
- C2 激活，或另一原生 turn 绑定 C2。
- Chat 调用写工具，目标选择逻辑此时指向 C2。

原生 turn 的 bound-client 测试证明焦点变化期间的客户端绑定行为。它未证明 Chat 请求归属，也未证明同一 client 切换项目时的 project 绑定。

**最低修改**

将权限矩阵中“须用户明确确认唯一画布”补充为明确的验收阻断条件。现有通路尚不能验收目标安全写入，单客户端、busy 检查和人工确认均不足以解除该阻断。原子路由继续留给 WAR-35/WAR-37，WAR-90 无需增加新 Agent 或桥接服务。

## P2 问题

### 5. 成功输出遗漏 client 身份

输入验证了 `client_id`，返回对象却仅保留 project/node/shot，降低后续记录的可追溯性。

**最低修改**

返回 `client_id`，并明确结果属于本次输入校验。该字段只能帮助追踪，无法锁定服务器目标。

### 6. MCP 权限和 HTTP 工具权限需要分别保留未知状态

**证据**

冻结材料已正确指出 `default_tools_approval_mode=approve` 与 `codex_approval` 事件不能证明 MCP 调用可由真人拒绝。HTTP 路由直接调用 `session.callTool()`，片段未展示请求鉴权、逐工具授权或拒执行控制。

**最低修改**

在验收表中分别列出：

- 原生 MCP 实际工具清单与拒执行证据。
- HTTP 调用者鉴权、可调用工具范围与拒执行证据。
- 正式线程中 codegraph/hindsight overrides 的实际生效结果。

这些都保持 **unknown**。源码片段不足以判定整个服务无鉴权，也不足以证明 HTTP 继承原生 Codex 的审批机制。

## P0 与只读 gate 判断

**未从提供片段确认 P0。**

`chat_read_preflight.verify()` 没有网络或写入副作用，返回值固定包含 `can_write=False`，因此本函数没有直接授予写权限。现存缺陷集中于只读“上下文已验证”的声明过宽，以及缺失 B/SHA 时的错误通过。

若下游仅依据 `read_context_verified=True` 开放写工具，会越过当前授权边界。冻结包没有提供该下游实现，其实际行为为 **unknown**。

## 后续仍未知

- 当前源码树是否与 manifest 一致，材料未提供独立验证。
- 七文件专业正文的完整权限约束，本消息仅提供摘要、路径和 SHA。
- `compactCanvasState` 是否实际返回 gate 所需 client/project 字段。
- 同一 client 切换项目、断线重连、请求在途时的端到端目标行为。
- HTTP 前检接线、请求鉴权、逐工具授权和真正拒执行路径。
- 正式安装、新线程加载、正式 MCP 权限及真实修改后人审 B 闭环。

完成上述最小修订后，可重新审阅 WAR-90 的准备阶段结论。生产安装与 Chat 写入仍分别依赖其实际验收证据。
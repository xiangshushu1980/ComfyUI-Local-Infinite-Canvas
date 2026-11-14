# WAR-90｜Codex 实施 Director Skill v0 B-flex 最小文本运行壳

你是 Eric Codex，项目 `/home/sean/projects/canvas-lab`。Linear Issue **WAR-90**（新建，In Progress，Canvas Lab · AI Video Director），ChatGPT 负责组织和独立审阅。首先读取最新版 `/home/sean/.pi/agent/skills/linear-task-collab/SKILL.md`，按需 references；先核 `git status`。**不得自行 Git commit/stage/reset/stash/切分支，也不要更新 Linear**。

**严格写入白名单：**
- `tools/director-runtime-v0/`：新增隔离的 Python 3 标准库 CLI、最小存储和 unittest；不修改现有生产项目、依赖、Agent、Canvas UI、WAR-35 Schema、WAR-52、WAR-36/37、原始技能。
- `docs/planning/WAR-90/`：实验文档和 D 的独立快照/运行记录；源输入与 Skill 只读复制，不修改 WAR-89。
现有分支 `war-35-schema-freeze-review-20261114` 有约 35 项他人改动，务必原样保留。遵循根目录 AGENTS.md 生产变更限制；不跑 Canvas/ComfyUI/H3/Blender/GPU，也不安装包/启全局服务。

**语义必读**：
1. `docs/planning/WAR-89/director-skill-v0-knowledge-context-architecture-proposal-20261114.md` §12（已批准语义，不是实现 API/Schema）；
2. `docs/planning/WAR-89/director-skill-v0-candidate/SKILL.md` + 四个阶段卡、knowledge-index/review-method 按需；
3. `docs/planning/WAR-89/text-test-round1-20261114/review-chatgpt.md` 只需结论；
4. `docs/planning/WAR-74/director-v0-concept-v1.md` 仅相关原则。
WAR-35 仍 In Progress、冻结未完成，不得重建第二套正式 DirectorPlan schema/Approval Engine。D 原文 `docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-D/script-D.txt`，冻结 SHA256 `65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`。

**实际实现**：一个可运行的小型本地 `python3 tools/director-runtime-v0/cli.py`： 
- `init --workspace docs/planning/WAR-90/pilot-D --source <D path> --skill <seven-file path>`：防覆写，将来源、SHA、七文件复制到独立目录并记录哈希、状态与初始化时间，候选=none、approved Intent=none。创建和状态保存原子化，校验输入路径，不给生产写入。
- `run-stage --workspace ... --stage intent --mode resume`：按 B-flex 提交真实 Source、Authority（首次没有 approved Intent）、Scene Spine/硬事实来自源文本（不得虚构批准）、一活跃候选或 none、阶段卡/知识引用、范围/审阅要求；调用已有 Codex CLI read-only sandbox，`gpt-6-astra` Medium，保存真实输入、原始 result、事件、thread ID 与 SHA；保存有意义阶段候选并停在 `awaiting-human-A`，模型不可以自签批准。提供 `--dry-run` 纯查看 prompt 无副作用（除可选文件）。必须明确模型输出仅探索候选。
- 后续 `record-review --checkpoint A|B --decision accept|reject|revise --evidence-file ... --actor human` 对**真实用户交来的**意见进行显式试验性记录，未批准 A 禁止 Beat/Blocking/Shot；**pilot-only，不是 WAR-35 正式 Review/Decision 或安全身份验证**。
- `run-stage --stage beat|blocking|shot --mode continue|refresh|resume`：选定一活跃候选，验证来源 SHA/批准基线/知识快照，记录本轮 Scope/差异/影响/未知。Continue/Refresh 只有在真实 thread ID 与 `codex exec resume` 支持时声称“复用原会话”；无法执行时不允许伪称 Continue 成功，可明确拒绝或记录切换为真正新会话 Resume 的原因。Resume 从批准基线+一个候选重建全文，不能只有 ID。新阶段有实质交接才存轻量候选，空转不生成新版本；被否决候选不应污染。
- `status` 显示当前阶段、单活跃候选、Approval gates、未证风险、下一步。允许 `resume-pack` 纯构造输入用于确定性测试（跨会话恢复、拒旧）。
- `Shot→Blocking→Shot` 局部退回：可以做离线模拟状态转移，标记受影响 Shot 待复检，不能全局宣布通过；提供非越权范围检查。
- source 内容或 Skill SHA 改变后，禁止将旧结果作为当前有效候选交接；换 mode 不能绕过；保留隔离历史证据。Review 不得自动从模型输出派生批准。
- 自动化测试使用 unittest **真实文件系统 + 假生成器**（区分 fake 与真实模型，不将模拟测试写成专业能力测试），重点 9 种：未批准 A 阻断；单候选与恢复全文；来源 hash 变化阻断；被拒候选不污染；变更阻断；无实质结果不存快照；局部返修标记邻镜；approval 不等于正式 WAR35；unknown 不变 verified；正例可推进；prompt 准确包含原文。测试不需要模型成本。
- CLI 必须有 README 快速上手、明示未实现或未验证的能力与 WAR-35 替换策略；生成物不可暗示已完成正式工程审批。

**交付顺序**：1. 实现+unittest；2. `python3 -m unittest discover ...` 全部通过；3. ChatGPT 来独立审阅代码后再发起真实 D A 生成。若你有能力本轮实施完并执行只读真实 A，也可在**不获得用户 A 审阅前**停在 A；不执行后续 B 段。Codex 不应自行生成批准/将 fake 结果当真。

最终在对话输出文件清单、测试数、真实 Continue/Refresh/Resume 支持等级、运行/使用命令、未证风险、下一审阅点和 Git diff scope，**不自动 Git 提交或改任务状态**。适度实现，优先安全、隔离、可测试，不造过度工程。

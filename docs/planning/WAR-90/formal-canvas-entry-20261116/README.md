# WAR-90｜Director Skill v0 内部试用部署与真实画布交互入口

日期：2026-11-16，设备 Eric。与 WAR-89 七文件候选、WAR-90 原生只读端到端 PASS（Git 6dcdbe4）衔接。**这是正式 Canvas Agent 工作流的内部试用部署，不是知识许可完成、Skill 正式发布或生产写入授权。**

## 目标与面向人的测试目的

把已经实测通过的七文件 Director Skill 原样接入 Eric 正式 Canvas Agent 工作空间。第一次真正的人机交互在用户自己打开的 Canvas Lab 中完成，只读审阅 D《错过的钥匙》已经批准的 B / Shot02；没有真实用户修订意见时保持 no-handoff。

ChatGPT/DCR 负责安装核验、证据和独立评估；画布内置 Canvas Agent 负责实际导演工作。共享同一份 Eric 原件/Runtime/批准状态，不建立第二套 Agent。Chat HTTP 跨客户端原子路由未证，不授权自动写画布。

## 安装位置、指纹和不可越过的边界

- 权威候选源（未修改）：项目根目录 docs/planning/WAR-89/director-skill-v0-candidate/，7 文件专业方法仍为候选。
- Canvas Agent 实际 workspace：/home/sean/.infinite-canvas/codex-workspaces/canvas-agent，以受保护配置中的 workspace.workspacePath 确认，未输出 token。
- 已安装试用 Skill：/home/sean/.infinite-canvas/codex-workspaces/canvas-agent/.agents/skills/director-skill-v0-candidate/。
- 安装包性质：内部交互试用 Candidate，七文件逐字节原样复制，保留原 SKILL.md 的候选标签，不声称知识规则和许可已经最终验收。WAR-89 知识源许可仍有缺口，未经审核不分发。
- 核验数据：preflight.json、install-result.json、verify-result.json、formal-agent-http-verify.json；包含7文件逐项 SHA，验证目标路径与原件一致，12 条相对 Markdown 路径全部存在。
- 安装前：正式 Agent 服务 inactive、无同名 Skill、无 director 相关 skillOverrides；原批准 B state.json SHA256 23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7。
- 安装方式：install_pilot_skill.py preflight → install → verify。先在同一文件系统临时目录复制和哈希校验，再原子移动整包到目标名称。拒绝覆盖已有同名包，拒绝 Agent 服务运行时改动。
- 回退离线验证：test_install_pilot_skill.py 在独立临时 HOME 和模拟 systemctl 环境内复用同一脚本，确认安装校验、覆盖碰撞阻断、active 服务修改阻断、retire 后完整包移入保留备份且重新允许安装，详见 isolated-install-retire-test-result.json；**不是在真实正式服务上实际回滚一次**。
- 可回退：先停止 Agent 服务，再运行 install_pilot_skill.py retire；校验后将整个包移动至用户 HOME 的 .infinite-canvas/skill-rollback/ 按时间命名的保留目录，不删除证据。此回退命令已实现，但尚未在正式工作空间执行回退演练。此前独立实例的完整回退已通过。
- 正式服务：只启动 canvas-lab-agent.service 和 canvas-lab-web.service；未启动 canvas-lab-gateway.service、未启用开机自启动。Agent /health = 200，Web HTTP = 200，正式原生 Skill API 列表唯一 enabled Candidate，错误 0。native MCP 清单只有 infinite-canvas enabled（仍非工具强制审批证明）。
- 初次核验：hasCanvas=false、clients=0、codexBusy=false；Agent 恢复原有线程后状态最终 ready，infinite-canvas/codex_apps ready。没有用户导演 turn，也未访问真实画布工具。旧 activeThreadId 不变；第一次交互建议在 Canvas Agent UI **新建对话**，显式启用本 Skill。

## 首次真实画布互动：由真实用户在 Canvas Lab 操作

1. 在 Windows 本机浏览器打开 http://localhost:3000/canvas?mode=recent ，或打开自己指定的项目画布。如果没有连接 Agent，使用 Canvas Lab 现有连接操作；不要向 Chat 粘贴 token。
2. 核对当前画布项目名称、现有选区是否真正对应 D《错过的钥匙》Shot02。**隔离联调创建的五个文本节点不会出现在你的真实画布**。若当前项目并无 Shot02 节点，不猜测映射、不自动创建。
3. 在画布内置 Canvas Agent 中新建对话，明确选择 director-skill-v0-candidate。如果选择器没有此 Skill，先诊断 UI / Agent 连接，不把 API 发现冒充 UI 选择成功。
4. 在原生 Agent 发送下方首次互动提示词：只核对已批准 B 的 Shot02、实际项目/选区和专业观看风险。用户可暂无修改意见。
5. 返回后，根据真实用户反馈决定是否进入局部修订；Chat 可以只读复核执行证据，但 **未批准前不创建/改写画布节点、不提交或重签 B、不跑 GPU 或媒体**。

### 首次互动提示词（给 Canvas Agent）

请作为画布中的导演助手，显式使用 director-skill-v0-candidate，对 D《错过的钥匙》已批准 B 的 Shot02 做一次只读镜头审阅。这是导演工作，不是执行 Linear 工程任务，不需要查询 WAR-90。先通过终端工具真实执行：

    python3 /home/sean/projects/canvas-lab/tools/director-runtime-v0/cli.py review-shot --workspace /home/sean/projects/canvas-lab/docs/planning/WAR-90/pilot-D-local-repair-v2 --shot-id Shot02

然后通过 infinite-canvas MCP 读取当前画布与选区，说明项目和节点是否确实对应 Shot02；如无对应节点，不猜测或自行创建。请按 Skill 的 Shot Plan/Review 方法说明观众观看任务、一个重要风险与未证依据，询问我是否有实际修改意见。没有反馈即停在 no-handoff。禁止修改画布或批准 B，不调用 prepare/submit、ComfyUI/H3 或任何媒体生成。

**职责分界纠正（2026-11-16）**：实际原生 Codex skills/list 列出 linear-task-collab、project-docs、director-skill-v0-candidate 为 enabled；但 config/read 的 MCP 服务名称中未发现 Linear，不能声称内置 Agent 已验证能直接读取 Linear Issue。WAR-90 仅是当前 Chat/Linear 对研究交互证据的索引，不应将“开始 WAR-90”当成导演 Agent 的用户工作指令，也不把“能够阅读 Linear Skill”误当作“能够查询 Issue”。CLI 参数中的 WAR-90 是本地批准 B 的存储路径，不指示访问 Linear。首次交互无需读取任务全文。

这只是第一次试点的一次性启动包，不是最终产品要求用户每次粘贴全部上下文。后续需按 WAR-35/37 设计自动装配 Source/Shot/画布状态。

## 验收状态、限制和下一关口

**PASS**：真实 Canvas Agent workspace 中的七文件试用包安装/静态校验；Agent/Web 服务启动；正式原生 Skill HTTP API enabled/path 一致；独立原生只读端到端此前已验收；正式批准 B 保持不变。

**未执行/不可宣称通过**：用户浏览器真实 Canvas 连接、真实项目 Node→Shot 映射、真人反馈、工具拒执行与审批、Chat 跨客户端请求级 CAS、生产修改、正式 Skill 发行许可与知识规则验收。

**下一关口**：用户在 Canvas 内打开目标画布并使用内置 Agent 只读审阅，记录真实 Node→Shot 映射或缺失；存在可定位真实修改反馈后，再单独授权局部修订候选及 B 复审。WAR-90 保持 In Progress。

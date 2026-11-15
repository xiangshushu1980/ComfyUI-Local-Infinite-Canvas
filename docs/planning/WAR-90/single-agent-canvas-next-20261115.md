# WAR-90｜下轮交接：单 Agent Director Skill + Runtime CLI + Canvas MCP

日期：2026-11-15｜设备：Eric｜项目：`/home/sean/projects/canvas-lab`｜Linear：[WAR-90](https://linear.app/xiangshushu/issue/WAR-90)

## 1. 本轮最新用户决策（优先级高于前面的 HTTP 桥接试验计划）

**下一轮要以 Eric 原有的 Canvas Agent（画布内 Codex，或 Eric 本地 Codex + Canvas Skill / MCP）为唯一的实际专业执行 Agent。** Director Skill 是该 Agent 加载的导演方法、专业知识与阶段工作规程；Director Runtime 是工程工具集合（版本/来源核验、候选保存、人工批准、局部检验/Resume），而不是第二个长期活跃的 Director Agent。画布作为工具，经已有 Canvas MCP 操作。ChatGPT 可以协调研究、评审和通过 DCR 做辅助检查，但不应成为每次“专业导演→结果→Canvas API”转发链条中的必经执行层。

期望的目标调用链：

```text
用户 ↔ Canvas Lab（画布审阅/反馈）
            ↕
Eric Canvas Agent (Codex) [或受控 Eric Codex 独立导演会话]
    ├── Director Skill（导演阶段判断；按阶段按需加载专业知识）
    ├── Director Runtime CLI（准备输入/核验保存/版本/审阅/恢复）
    └── Canvas Skill + infinite-canvas MCP（画布读/写/选镜/可视化）
```

现有 Canvas Agent 内部 MCP/Skill 已存在，不要新建平行 Agent 或平行 Canvas HTTP 后端。最小改造目标是让同一个 Codex **直接作出专业判断，然后向 Runtime 提交候选**；不要默认形成 `Canvas Codex → runtime.run-stage → 第二个 Codex` 的嵌套模型调用。**目前这一新路径仍是已确认的设计方向，尚未实现、尚未实际验证。**

## 2. 事实与当前实现（防止新对话误以为已经集成）

- 最近由 ChatGPT 通过 DCR 在 Eric 运行 Python 脚本，调用已有的 Canvas Agent HTTP `/api/tools`。它与现有 `infinite-canvas` MCP 基于相同 Canvas Session 能力，但最近实验**不是让 Canvas Agent 内 Codex 自主调用 Director Skill**。先前专业导演真实生成是 Runtime CLI 在 Eric 启动独立 Codex 模型轮次；最近 Canvas 往返试验的修订结果是明确标记的 `fake` 生成器。
- 已通过的工程验证：只读 approved B → 独立 Chromium 临时画布 5 个节点/选中 Shot02；模拟反馈 → 隔离工作区假候选 → Canvas 差异展示（7 节点）；43/43 回归与适配测试。**不能把它当作实际导演质量或真实用户 Canvas 审阅完成。**
- Director Runtime 路径 `tools/director-runtime-v0/`。现有 CLI `status`、`resume-pack`、`run-stage`、`record-review`、`review-pack`。其中 `run-stage` **默认会再次启动 Codex**；`run-stage` 内部有传入 generator 的受控接口供测试，但**尚无正式由当前 Agent 提交专业输出并校验/保存的 CLI 命令**。这就是下一轮应评估的最小工程拆分：`prepare/resume` / `validate-and-commit candidate` / `review`，而不是继续发明第二套 API。
- `Continue/Refresh` 的真实会话复用未实现且 v0 不需要；用户已决定 v0 统一使用 `Resume`。保留来源/Skill/候选 SHA、阶段完整快照、审批 A/B、候选不可变、局部变更影响与邻镜复检、失败隔离、原子写入。递增 revision/CAS 只是未来 Canvas typed DirectorPlan 的建议语义，**当前运行壳没有实现**。
- **正式 WAR-35 DirectorPlan Schema 尚未冻结**，不能用 pilot 状态冒充正式 Review 或正式审批。真实模型判断与独立证据保持清楚边界；不伪造用户批准，也不得自行把媒体/几何/观众风险标记为验证通过。
- 已批准当前 D《错过的钥匙》B：`docs/planning/WAR-90/pilot-D-local-repair-v2/`，candidate ID `b7b4fd156b884907b2431b6b1e0d9960`；`state.json` SHA256 `23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7`。不要改写或覆盖。之前的 `pilot-D-canvas-feedback-demo-20261115/` 是 **fake 未批准** 候选（ID `525d8738cdc34975954cf8687005eac2`），不是可用的新 B。
- Eric 当前 git 分支 `war-35-schema-freeze-review-20261114`，截至上轮提交 `847611825a13ea7df77c1d84db5d6f62ab05985b`；Git **本地已提交，尚未 push**。工作树有其他历史未提交文件、web/dist 改动，勿覆盖/混入。

## 3. 最小必要资料入口（先读当前任务与这些文件，不扫全部项目）

1. `/home/sean/.pi/agent/skills/linear-task-collab/SKILL.md`——新对话按项目规则读取，接续 WAR-90 与必要关联任务。
2. 本文：`docs/planning/WAR-90/single-agent-canvas-next-20261115.md`，当前用户决策及执行路线。
3. `docs/planning/WAR-90/canvas-feedback-20261115/README.md`——最近 API/测试桥接和边界，实验成果仅复用证据。
4. `tools/director-runtime-v0/README.md` 与 `tools/director-runtime-v0/cli.py`——当前实际 CLI，按需读取 `runtime.py` 中 `packet/run/review`。
5. `docs/agent/canvas-agent-remote-control-20261112.md`——Eric 上**实际存在**的 Canvas Agent 远控指南；项目描述旧链接 `docs/agent/canvas-agent-remote-control.md` 目前不存在。按需读取 `infinite-canvas/canvas-agent/agent-instructions.md` 与 `infinite-canvas/plugins/infinite-canvas/skills/canvas/SKILL.md`。
6. 导演 Skill 七文件现候选：`docs/planning/WAR-89/director-skill-v0-candidate/`，**只按当前阶段加载必要部分**；不遍历三套原 Skill 的全部历史。
7. `docs/planning/WAR-90/flow-canvas-handoff-20261115/README.md`——只读批准 B 输出的校验和证据。

## 4. 下轮具体工作建议

**先观察**现有 Eric Canvas Agent 的正常 Skill/MCP 调用流和真实输入输出路径：优先静态小范围阅读 + 现成操作、测试画布，不重复全面研究或大规模重构。确认可以怎样让它加载项目里的 Director Skill、如何调用用户工作目录下的 CLI、如何从画布选区及文字输入获得结构化反馈并回写节点；明确 Canvas MCP 已可做到的事情和唯一缺口。

**再设计并实现最小适配**（若验证确有需要）：Runtime 提供不二次发起模型的工程接口；同一个 Codex 直接执行 Director Skill 的专业阶段，提交结果给 Runtime 做规范化/检查/保存，而不是 Runtime 启动另一个 Codex。保持已有 37/37 单测与批准 B 字节不变；增加必要的对应测试，并保留可回滚的增量更改。实现细节应遵循当轮真正观察到的 Canvas Agent 能力，不先定义未经验证的 RPC 契约。

**最后在独立测试画布/新 Codex 会话真实验证**：已批准 B 只读恢复与展示 → 用户选中镜头并给出真实反馈 → 单一 Codex/Director Skill 通过 Resume 产生有专业依据的独立候选 → 受影响邻镜检查 → Canvas 展示版本差异 → **用户审阅**。不可代用户决定批准，不默认操作其已有真实画布；未经授权不做 GPU、ComfyUI、H3、Blender 或收费媒体生成。

**新会话管理**：推荐新开 ChatGPT 讨论和新开 Eric Codex 导演会话，加载 **Skill + 目前有效阶段包 + 必需画布工具**，不要把之前所有模型对话和实验日志作为常驻上下文；Git、文件、Linear 用于跨会话恢复。

## 5. 任务组织

继续 [WAR-90](https://linear.app/xiangshushu/issue/WAR-90)，当前仍 **In Progress**；相关 [WAR-37](https://linear.app/xiangshushu/issue/WAR-37) 负责正式 Canvas UI/节点映射（Backlog），不要在实验适配里抢先改生产画布 UI。若研究显示需要新增独立目标/验收，再遵循 linear-task-collab 的查重与关联规则决定是否拆 Issue。

以上为本轮明确的**新技术路线**，之前 HTTP 测试脚本仍可用于回归验证，不再继续扩展为正式长期架构。

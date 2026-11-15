# WAR-90｜Director Skill 正确性闭环与 Canvas Agent 只读交接出口

2026-11-15 · Eric · **结果：完成已批准试点 B → 可验证只读审阅包的最小工程出口；尚未完成 Canvas Agent 实际导入，也没有实现 WAR-35 正式 Schema/Review。**

## 1. 本轮范围与权威输入

- 用户明确将优先级调整为 **流程与正确性 > 性能**，期望导演闭环稳定后与 Canvas Agent 整合。未运行模型、Blender、ComfyUI/H3，也没有启动或修改 Canvas；没有改原始 Skill 或 WAR-35/52。
- 运行壳代码：`tools/director-runtime-v0/runtime.py`、`cli.py`、`tests/test_runtime.py`，只属于 WAR-90 实验运行壳，非生产 DirectorPlan 数据契约。
- 真实用户批准的新 B：`docs/planning/WAR-90/pilot-D-local-repair-v2/`，候选 `b7b4fd156b884907b2431b6b1e0d9960`，源工作区 `state.json` SHA `23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7`。
- 另外对照原批准 B `pilot-D`（`d23b8bdab90f43ef8ff0098fb8021f78`）及未批准紧凑试验 `pilot-D-compact-live-20261115`。三者的批准状态和原始 SHA 都没有被改写。
- 已验证的 Canvas Agent 操作指南当前在 `docs/agent/canvas-agent-remote-control-20261112.md`（先前项目文件 `canvas-agent-remote-control.md` 在本轮工作树中不存在），它报告 2026-11-12 对 Canvas Agent API/画布只读、单个临时文本节点写入删除的实测；**并非本轮重新进行的 Canvas E2E 验证**。

## 2. 可重放的正确性闭环

当前已经通过真实文本试点完成：`Source → Intent 候选 → 真实用户 A → Beat → Blocking → Shot 候选 → 真实用户 B → [发现几何反例] → Shot→Blocking→Shot 局部修订 → 新候选 B 用户重批`。原候选和新候选各自具有 ID、SHA 和审批证据；未证 geometry/media/audience 不被“文本 B 已批准”清除。以前两次真实 Astra 生成已验证模型能完成专业修订；本轮**不重复真实生成**，专注工程交接边界。

新增运行壳命令（**只读**）：

```bash
python3 tools/director-runtime-v0/cli.py review-pack \
  --workspace docs/planning/WAR-90/pilot-D-local-repair-v2
```

返回 `war90-director-preview-only-v0` 的实验投影视图，主要字段：

| 输出字段 | 用途与硬边界 |
| --- | --- |
| `authority` | 源 SHA 与逐字原文、Skill 快照 SHA、当前 A/B 候选 ID/内容 SHA、A/B 审阅证据 SHA。此输出不能自己签署新批准 |
| `stages` | Intent/Beat/Blocking/Shot 四阶段的现行全文 + 每段 SHA；完整可读，但不是 WAR-35 定稿 Schema |
| `shots` | 每个 ShotNN 的独立段落和 SHA，顺序不变；供 Canvas **显示**、关联视觉审阅位置，不是生成任务单 |
| `review` | 明示 A/B 为**试点**接受、`identity_verified=false`、`formal_WAR35_approval=false`、`pending_shots=[]`，geometry/media/audience 仍未验证 |
| `capabilities` | 仅 `display_text=true`；`propose_edit/write_canvas/generate_media/production_approval=false`。调用端必须遵守，只读并不等于拥有写画布权限 |

准入规则由**工程检查**确定（不信任模型自由文本）：四阶段齐全、当前 Shot 候选与已批准试点 B 完全一致、原始 Source/Skill 与候选哈希有效、A/B 两份真人审阅记录能匹配精确候选及 SHA 且原始证据文件/审阅正文哈希有效、无 `pending_shots`，才允许输出。任何一项失败就退出码 2，不能把历史批准误用到新候选。

**本包明确不提供**：运行 Canvas tools 的授权、生成资产/视频的指令、生产 DirectorPlan Review/Decision 记录、H3 Prompt 或镜头媒体可行性断言。旧运行壳的 `actor human` 仍只表示操作者声明，`identity_verified=false`；不是实际身份认证。

## 3. 本轮测试和真实工作区审计

- 运行壳原 31 项 + 新 6 项 = **37/37 通过**。新增覆盖真实 A/B 审阅与只读输出、未批准局部修改拒绝、源文篡改拒绝、审阅证据篡改拒绝、审阅文本/活跃版本错配拒绝、没有匹配的 B 人类决策时拒绝。
- `audit_review_packet.py` 对三个**实际** Eric 工作区做只读 CLI 测试：**15/15 通过**。原 B 和新版 B 分别能导出、互不串号；未批准 compact 实验候选 `review-pack` 返回 2；三份 `state.json` 在执行前后 SHA 完全相等。
- `approved-B-review-preview.json` 是从真实新 B 导出的**只读冻结试验包**（约 83.9KB），SHA `04538955e5950e20744815e0d2bc5fab328c7b343ac14a5b27eb9e128a26ef04`。`review-preflight.json` 保存 15 项硬检查与三源状态 SHA；`runtime-unittest.log` 保存 37 条测试全记录。
- 没有新的真实模型调用；这些检查证明运行壳审阅出口的来源/版本/权限行为，不证明导演专业含义已经被程序形式化证明。

## 4. 下一步与 Canvas Agent 的最小连接边界（设计，未实施）

1. **调用端**：Canvas Agent 或其经批准的本机薄适配层在 Eric 读取当前工程选定的导演工作区，再调用 `review-pack`，核对来源/版本哈希。不要让 Browser 或大模型自行读写 `state.json` 拼接批准证据；更不能从某次聊天里复制 JSON 当最新有效状态。
2. **画布展示**：将四镜分别以可识别 Shot ID 的只读审阅卡/节点或文本叠层展现，保留该次 `approved_B_id` / content SHA / source SHA，必要时查看完整 Blocking、Beat 与 Intent。优先使用独立测试画布，**先获得画布写入授权**；不得默认向用户真实画布创建节点。
3. **用户反馈**：画布上的 Shot02 修改要求必须记录为指向具体 `candidate_id + candidate_content_sha + target_shots + observed issue/evidence` 的反馈；反馈只是输入，不是批准，也不得让几何代理“通过”自动改变 A/B 状态。
4. **回传执行**：反馈归因于 Shot 表达的，回到 Shot 局部候选；涉及人物动作/观察通道的，回 Blocking，再传播到相关 Shot；涉及上游故事硬事实，先阻止并要求真实用户上行决定。执行仍由当前导演 Skill/运行壳负责，画布不得直接重写 DirectorPlan/已批准版本。
5. **审阅和发布**：新候选与批准版本分离，跨镜与知情差完成复核后，展示文本/媒体证据给真实用户；只有真实新 B 决定才可置换有效试点版本。将来 WAR-35/52 正式契约冻结后，再通过适配层绑定 typed DirectorPlan/Review；**不得**把这个试验投影提升成第二套正式 Schema。

Canvas Agent 2026-11-12 曾验证 `canvas_get_state` / `canvas_create_text_node` / `canvas_delete_nodes` 能在已连接浏览器画布上调用；本轮**没有**重测在线连接、未向 Canvas Agent 传递本包，也没有验证模型正确渲染四镜审阅卡。最小真实联调必须在受控测试画布上另做。

## 5. 未完成项与收口建议

- 当前 WAR-90 的 **Resume、阶段快照、真实 A/B、人机局部修订及可信只读交接**已形成可重放试点；但验收列表中的 **Continue/Refresh** 仍未真正验证且在运行壳显式拒绝。不能因此直接标记 WAR-90 Done。
- 系统层确定性检查已覆盖源/版本/批准绑定和已编号 Shot 段落非目标文本保护；**还不能**形式化核对世界状态、动作重入、几何、人物知情与媒体读懂，Blocking 的自然语言修改范围也主要依赖模型申报。
- 建议下一轮优先完成 WAR-90 剩余**会话正确性**（Continue/Refresh 版本锚、污染与过期降级到 Resume 的机制；没有信任依据则继续拒绝），再用已批准文本在**独立测试画布**与 Canvas Agent 做一轮真实的只读审阅呈现。不会为了省时改全阶段正文生成策略。

本报告和原始 JSON、审计脚本为同一研究轮次的权威记录；Linear 仅索引当前状态与路径。

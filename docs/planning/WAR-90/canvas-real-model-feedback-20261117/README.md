# WAR-90｜真实模型 Shot02 局部修订与 Canvas 差异测试

时间：2026-11-17，机器：Eric，项目 Canvas Lab。用户授权继续 WAR-90 最小真实修改闭环，但**未提供具体的真人导演改稿意见**。为验证流程，明确使用 synthetic-test 输入：让 Shot02 重点交付唯一银钥匙 K 首次显露→辨认→蓝色文件夹自然再遮挡，镜尾右手轻理仅交付可辨的启动与运动方向，留给 Shot03 的同一动作与周问话打断。合成测试反馈不是用户导演意见，不得触发用户 B 批准。

## 权威与隔离

唯一批准 B 来源：docs/planning/WAR-90/pilot-D-local-repair-v2/state.json，SHA256 23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7，批准 B ID b7b4fd156b884907b2431b6b1e0d9960。
试验派生工作区：docs/planning/WAR-90/pilot-D-canvas-shot02-flowtest-20261117/。此文件夹不是新的权威 B，包含已经批准资料的派生副本，因此不随本次提交重复纳入 Git；本目录的 evidence/ 保存新真实模型调用的原始冻结证据。

## 实测执行

1. 在唯一已连接的正式 Canvas Agent 浏览器客户端中，核对 canonical Origin 对应项目 2FwEbySI5PYe7d6BL4pES、client ID jeUNwaV-t0QApaAKC2pMh、四个原 Shot 节点和原 B SHA。临时选中 Shot02 节点 text-1794832120997-1，用既有 feedback_bridge.capture_feedback 生成与来源、镜头文本指纹绑定的 synthetic-test envelope，明确 actor_identity_verified=false、human_B_decision=false；随后恢复用户原有 Shot04 选区。
2. 从批准 B 逐字复制隔离分支，在 Eric 使用真实 Codex CLI gpt-6-astra/medium 执行 Director Runtime 的 Pilot.run(stage=shot,mode=resume,targets=[Shot02],scope=反馈)。实际耗时 161.62 秒，生成器 codex-cli 非 fake，真实 model thread 与原始 events/result 存于 evidence/。生成候选 ID 6cbcaf51a55e4bb0a097147eb34dd3cb。
3. 原 B → 新候选 diff：只修改 Shot02 的三个段落（观看任务、画面构造、切点与出态），Shot01/03/04 均逐字相同。新候选更集中桌面阅读区，右手轻理仅镜尾启动，Shot03 延续同一次运动直到周提问才停止。自动标记 pending_shots=[Shot01,Shot02,Shot03]；有意义的风险：较早动作中切点必须与周到达桌边的自然时序相容，若不相容应报告 Blocking 依赖而非静默更改动作和速度。**这一点尚未实测验证。**
4. 候选 Runtime 分支状态 phase=awaiting-human-B、pilot_B=null、formal_WAR35_approval=false；批准 B 原 SHA 始终不变。原运行壳 64/64 tests PASS，反馈适配器 6/6 PASS，独立 scope-verification.py 共 15/15 静态边界断言 PASS。文本/哈希检查不证明几何、演技、观众识别。
5. 在当前 canonical 真实画布 Shot02 下方 x=720,y=1270，新增一张测试差异卡：【实验待审｜非批准】Shot02 R2 · 最小局部差异，节点 text-1794847881140-0。写入前 4 节点，写后 5 节点，原 4 个文本内容、原 B SHA 都未变。Canvas 新建时自动切换选区，后按实际回读显式恢复此前 Shot04 选区；canvas-display-audit.json PASS。差异卡是演示，不是类型化正式 Shot 卡。完整精确 diff 与新版 Shot02 保存在 candidate-diff.json，不重复铺满 Canvas。

## 已验收边界、未完成与后续停点

**本轮工程有限 PASS**：规范 Canvas 的真实节点目标绑定→合成反馈与身份防伪→隔离克隆→真实专业模型 Shot02 Resume→非目标精确 diff 守门→相邻 Shot 待复检标记→真实浏览器差异摘要节点→批准 B 未污染。

**仍待真正闭环**：真人创作改稿意见、真人的批准/拒绝/要求再改、正式批准后重新加载及画布版本同步；正式身份/CAS/typed Review 的设计归 WAR-35/37，而非本轮另造。浏览器刷新后的 IndexedDB 恢复尚未单独验证。没有媒体/Blender/H3 生成，不增删旧镜头、不安装新资产或实体系统。

接下来的真人决定：A 拒绝合成候选、保留原 B；B 明确接受这个新的具体镜头主张，并进入真实 B 人审确认；C 要求进一步修改一处具体条件。**没有真实用户回复时，Agent 不得写入批准决定**。审阅即便同意，也需遵循现行试点审批流程，不能宣称 WAR-35 正式批准。

## 2026-11-17｜用户认可 R2 后的试点 B 落账与 Canvas 同步（补充最终记录）

用户明确回复“认可R2.”，并在后续讨论中允许 **WAR-90 仅简要完成流程闭环，再由其他任务设计专业交互界面**。本轮严格使用现有 Pilot.record_review 和原生 Canvas Agent API，不建设新的产品层审批机制。用户认可的是经真实模型生成的 R2 修改候选，原发起修改的 instruction **仍是 synthetic-test**，不得倒填为用户亲自书写的改稿意见。

- 真人原话证据保存在 user-R2-acceptance-evidence.md（SHA256 73310fdec6d87b24f4cde822236d694a0e239d850d5eca556be73cdff3ccba0f）；作为**候选工作区外**的证据，调用 Director Runtime CLI record-review --checkpoint B --decision accept --actor human，原始回执 pilot-B-R2-accept-receipt.json。运行壳记录身份 identity_verified=false、formal_WAR35_approval=false，**不是**生产级授权认证或 WAR-35 正式审批。
- 被接受的试点 B ID：6cbcaf51a55e4bb0a097147eb34dd3cb；**仅**在隔离的工作区 pilot-D-canvas-shot02-flowtest-20261117/ 中 phase=pilot-B-accepted、pilot_B.id=R2、pending_shots=[]、gates B=true；新工作区权威 state.json SHA256 f8b3922311074f6d7c126596939ecd468c1f452bce67f1faf9f5875d0f8afffa。原批准 B 工作区 pilot-D-local-repair-v2/state.json SHA256 23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7，完整保持不变。
- 为避免仅存本机未跟踪分支，本 Issue 证据包 evidence/ 内保存批准后的 state.json 冻结快照 approved-R2-pilot-state-snapshot.json，及包含四个精确镜头文本的 approved-R2-four-shot-projection.json；不是第二套生产数据契约。操作前快照 before-acceptance-state.json、审批复核 R2-approval-validation.json 均在当前目录。
- 为避免 Canvas 展示出现两个不一致的“当前 B”，对唯一规范项目 2FwEbySI5PYe7d6BL4pES 使用一次批量 Canvas Agent canvas_apply_ops，**原位更新**四个 Shot 文本展示节点的批准 B 元信息与原文（Shot02 内容切换为 R2；Shot01/03/04 正文逐字相同）。历史差异节点 text-1794847881140-0 由“实验待审”改成“【R2 试点 B 已接受】Shot02 · 修改差异记录”，明确反馈来源 synthetic-test 及用户审阅后接受。
- Canvas 仍然只有 **5 个节点**（四镜和一历史差异节点），未增删节点、关系边、媒体；没有改变任何原节点 ID、位置、大小或用户当时的选区。浏览器批量写入返回完整五节点文本 SHA **5/5** 精确相符，后续 Canvas Agent live compact 只读回查通过；画布同步审计 approved-R2-canvas-sync-audit.json pass=true。
- 新的独立后续校验 R2-post-sync-verification.json **18/18 PASS**：原 B、R2 试点批准、真人证据、输入非合成身份的正确标注、仅 Shot02 修改、五节点展示版本、无多余图关系与服务状态均满足当前可测不变量。注意 Pilot 试点批准会**按机制清除 pending_shots**，这是用户试点文本审批状态收口，**不是**新增了连续动作专业复验或看过成片。
- 本轮**没有**重新打开/刷新 Windows 浏览器验证 IndexedDB reload，因此只能宣布 Runtime 已持久写盘、当前浏览器 Canvas 已同步并回读；重载持久化仍需一次浏览器刷新后的核验，不应冒称所有产品级闭环完成。
- User 对“文本显得粗糙、不工程化”给出了明确产品反馈：当前通用 Text 节点是单纯的**技术投影**，不是理想的导演镜头交互。专业术语、镜头卡层级、实体关联、连续动作连线、精确 Diff 和批准交互的设计由总控已分配的 WAR-37（设计）及 WAR-42（工程集成）承接，**不要在 WAR-90 增加新的产品层数据协议或临时定制面板**。

**阶段判断：WAR-90 试点“已认可 R2 → 独立 B 审批落账 → 原生 Canvas 文本版本同步 → 读回无污染”有限闭环完成。** 尚无正式 WAR-35 typed Review/Decision、产品身份认证、刷新恢复/图形审阅视图与媒体质量验收。详细记录均属 Eric 项目目录，Linear 只保存状态及索引。

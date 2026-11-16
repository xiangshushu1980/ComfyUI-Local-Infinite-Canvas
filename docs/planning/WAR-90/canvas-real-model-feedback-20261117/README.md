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

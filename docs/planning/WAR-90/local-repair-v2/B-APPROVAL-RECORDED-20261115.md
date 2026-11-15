# WAR-90｜2026-11-15 新试点 B 审批记录（追加）

**结果：用户已批准派生四镜 B，运行壳已成功记录；仅适用于 WAR-90 pilot。**

- 用户原话与审阅问题对应：`user-B-approval-20261115.md`；用户原话为“批准.”；原文不是模型自签。
- 真实新 B 候选：`b7b4fd156b884907b2431b6b1e0d9960`，candidate content SHA-256：`64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7`。
- 审阅动作：`tools/director-runtime-v0/cli.py record-review --checkpoint B --decision accept --actor human`，证据文件位于工作区外。
- CLI 原始回执：`pilot-B-accept-record-20261115.json`。正式状态快照：`post-B-state-snapshot.json`。
- 当前 branch：`pilot-D-local-repair-v2` 中 `phase=pilot-B-accepted`，`gates.A=true`、`gates.B=true`，`pilot_B.id=b7b4fd156b884907b2431b6b1e0d9960`，`pending_shots=[]`，`formal_WAR35_approval=false`。
- 保留原工作区 `pilot-D`：原 B ID `d23b8bdab90f43ef8ff0098fb8021f78`，`state.json` SHA `020a2bda99e85d34a4f2441055c0c6d8fcd5cc14151fd66750ebc09d81d099ca` 未改变。
- 复核：`verify-post-B.py` 的 **16/16** 检查全部通过；B 接受仅对审阅记录追加一条并使指定新候选正式成为试点 B，Intent、Beat、Blocking、Shot 文本保持批准前的 SHA，未知项和真实模型调用证据也没有被改写。
- 批准不意味着 Blender 真实运动、Canvas、H3、观众可读性、时间节奏已通过；此前 `local-repair-v2/README.md` 为**批准前实验报告**，保留原始状态和 hash，不将历史“待批准”描述覆盖成新事实。
- 运行壳 Continue/Refresh 会话复用仍禁用，WAR-35 正式 Schema/Review 审批未进行，故 WAR-90 任务仍可保持 In Progress。下一步独立研究运行壳性能、会话恢复模式及生产数据契约，先与用户确定优先级。

# WAR-90｜D《错过的钥匙》真实 Shot→Blocking→Shot 局部修订闭环

2026-11-15｜执行机器 Eric｜**结果：Resume 模式真实往返可行、候选及影响保存正确，尚待新的人工 B 审阅；Continue/Refresh 依旧未实现。**

## 1. 授权、冻结基线与安全隔离

- 本轮按用户“无结构变更则连续完成验证、遇到需要人工确认才停止”的授权执行。没有修改导演架构、WAR-35/52 Schema、原始 Skill、生产 Canvas、Blender/H3/媒体。
- 只读原试点工作区：`docs/planning/WAR-90/pilot-D/`；启动前及执行后 `state.json` SHA-256 均为 `020a2bda99e85d34a4f2441055c0c6d8fcd5cc14151fd66750ebc09d81d099ca`。既有用户 B 指向 `d23b8bdab90f43ef8ff0098fb8021f78`，不改写。
- 独立工作区 `docs/planning/WAR-90/pilot-D-local-repair-v2/` 从原版本字节相等复制（`baseline.json` 保存快照），供真实修订测试使用；单独保存新 candidate。此目录包含重复的历史资料，不作为新的唯一权威正文；所需两轮原始模型证据另存 `local-repair-v2/evidence/` 并 Git 冻结。
- 修改范围只允许 Shot02 / Shot03 / Shot04 的专业计划。Shot01 完整保留。输入的既有几何证据：`docs/validation/WAR-90/light-v2/README.md`（SHA `7f57693b0d598e3851cc92eb2849560dae7a38f979107ce2e56e3bacd199f993`），仅为 Blender CPU 代理，不等于实际导演影片。

## 2. 真实模型调用和阶段成果

| 阶段 | 模型与方式 | 真实候选 ID | 时长 | 实际变化 |
| --- | --- | --- | --- | --- |
| Shot → Blocking | Eric Codex CLI 0.169.0，`gpt-6-astra` Medium，`Resume` | `ecc8a553cd0543eaa39448b0c922a44e` | 140.30s | 六段完整 Blocking；首次显露时林仍挡周，蓝夹盖回后才让位，右手接续轻理供 Shot03 问句打断；揭夹后林才发现，Shot04 再前倾一次递物 |
| Blocking → Shot | 同模型 Medium，新 ephemeral 会话，`Resume` | `b7b4fd156b884907b2431b6b1e0d9960` | 214.07s | 完整四镜 Shot Plan；Shot02 明确在落夹后让位并开始轻理；Shot03 同一轻理跨切被问句打断，再左手揭夹、林发现；Shot04 前倾、右手取 K、单次交周右手 |

**运行身份与证据**：两次 CLI `generator=codex-cli`、真实 `thread_id`、真实 `events.jsonl`、逐轮输入/输出原文及 candidate SHA 都保存于 `evidence/<run-id>/`；不是 fake generator/模拟 LLM。`blocking-scope.md`、`shot-scope.md` 是本轮经授权的任务边界说明。输入分别约 119,045 和 128,933 字节，包含庞大旧 stage/artifact 历史，模型调用耗时显著，后继需压缩局部恢复包的历史杂音；**不在本轮未经授权改架构来修复性能**。

## 3. 最终候选具体变化与状态切点

- **Shot01**：逐字与已批准旧 B 的本镜段落一致（628 字符），镜头号、动作来源和“提移开始但 K 尚不可辨”切点不动。
- **Shot02**：从已起提文件接入；观众首次看 K，同时周到 K 的通道被林挡；左手蓝夹由移动文件叠承托且盖住固定 K。夹落稳且左手松开后，林自然偏侧后让位；空右手从桌外路径接续轻理纸叠边缘。切出于**轻理仍在发生**、周只看夹覆盖区的时候。
- **Shot03**：入镜接续同一次轻理（不能重启），第三句问话真正打断它；林停下右手、问后左手移夹，再次显露 K，**第一次由林认出**；短暂停顿及第四句后，林左手持夹、右手空、K 还在桌、周未伸右手、取物前倾未启动。
- **Shot04**：周先伸右手；林这时才自然前倾、右手取起唯一 K、双手短暂共同承接、周右手握稳，林右手松开撤出，周持钥匙朝门走、林留桌。K 起取前不移动，整场四句原话各一次，四镜顺序不变。
- **邻镜复核**：Shot01→02 仅检查；Shot02→03 是右手轻理的动态跨切，不能只检查静帧；Shot03→04 是“发现结束但尚未拿取”的静态/行动边界。新候选变更不意味着新 B 已获批准。

## 4. 工程检查和未完成事项

- `audit-loop.py` **32/32**：原 B 工作区 SHA 不变，真实 A 与冻结旧 B 评论保留；Intent/Beat 完全不变；完整六段 Blocking + 四镜 Shot，新目标仅 Shot02–04；**Shot01 正文段落逐字一致**；两次 real Codex CLI Resume、关联 candidate 全存在；审批 gate B 复位 `false`、`formal_WAR35_approval=false`；pending 关联镜头仍含 Shot01–04（Shot01 是邻镜复核，不代表允许修改）。
- `compare-shots.py` 的 `shot-diff-check.json`：Shot01 exact=true，Shot02/03/04 exact=false，且均有明显实质正文差异；独立人工读稿核对了两处接缝以及首次可见信息顺序。
- `runtime-unittest.log`：原运行壳 **26/26** 回归通过。`mode-guard-tests.txt`：`Continue`、`Refresh` 与非法 `Shot99` 均返回 exit 2，拒绝后 branch `state.json` SHA 不变；**只能声明 Resume 模式已实测，不能说三种模式全部已实现**。
- 原 B 审阅历史记录保留，但 branch `pilot_B=null`、最终 `phase=awaiting-human-B`，不自签批准；原 `pilot-D` 仍为 B 已批准。当前试点没有真实身份验证，正式 WAR-35 批准仍 false。
- 模型指出的几何/表演/观众未知依旧有效：代理 11 点取样不等于连续自然步态；轻理和揭夹动作未由真实人体 Rig 动画验证；周缺右臂/手指 Rig；完整四镜图像、空间轴线、角色朝向/POV、声音、约 35–40s 真实成片与观众辨认都未证。本轮不运行新的 Blender/媒体。
- 值得后继工程解决：本实验传输字段仅检验 `changed_targets` 声明，不自动防止模型在非目标正文中偷偷重写。此次额外做了 Shot01 逐字 diff 才确认未越界；生产版本需要正式字段级 diff/修订边界验算。长恢复包输入约 119/129KB，模型总耗时约 **354.37s**，应作为性能证据而不是期望用户每次等待。

## 5. 结论与下一停点

**本次真实局部修订闭环验收为 LIMITED PASS（Resume 模式和候选保存/依赖传播）；完整 B-flex 所有模式验收仍 NOT COMPLETE。** 既有四镜 B 历史不受影响，新候选已进入真实用户 B 检查点。后续由用户审阅“落夹后让位→正在轻理被问话打断→左手揭夹发现→Shot04 才前倾一次交付”的新调度与镜头代价；同意后才可按 user-B 实际意见记录新 branch 的 pilot B。未经用户批准不得把 `awaiting-human-B` 改为 `pilot-B-accepted`，更不能升级 WAR-35 正式审批。

原始依据、输入、候选、模型事件、日志与最终状态保存于本目录及其 `evidence/`；`evidence.sha256` 为全部证据文件的字节散列索引。Clone 工作区保留在 Eric 用于实际 CLI 继续，但通过本地 `.gitignore` 不重复把历史试点资料再提交一遍。

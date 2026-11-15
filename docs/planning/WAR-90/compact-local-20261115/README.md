# WAR-90｜局部上下文重建与非目标镜头保护：实现及验证记录

日期：2026-11-15｜机器：Eric｜工作方向：Director Skill v0 B-flex 最小运行壳。

**本轮结论：试验运行壳的局部 Resume 紧凑包与非目标 Shot 文本守卫已编码、确定性回归通过；以两次冻结的真实模型输出离线重放均成功。尚未新调用模型测量推理速度/专业质量；Continue/Refresh 仍禁用。**

## 1. 输入基线与修改权限

- Linear：WAR-90 In Progress。原试点 `docs/planning/WAR-90/pilot-D/` 的 `state.json` 原始 SHA-256：`020a2bda99e85d34a4f2441055c0c6d8fcd5cc14151fd66750ebc09d81d099ca`；获用户新 B 批准的独立工作区 `pilot-D-local-repair-v2` 状态 SHA-256：`23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7`。运行前后均未改变。
- 上一轮用户批准的四镜候选 `b7b4fd156b884907b2431b6b1e0d9960` 和审批记录没有修改、没有再签 B。原始导演文本、WAR-35/52 Schema、Blender/H3/Canvas、真实媒体亦未修改。
- 依据：`tools/director-runtime-v0/runtime.py`、`cli.py`、`tests/test_runtime.py`，`tools/director-runtime-v0/README.md`，旧真实模型输入与输出：`docs/planning/WAR-90/local-repair-v2/evidence/ecc8a553cd0543eaa39448b0c922a44e/` 与 `.../b7b4fd156b884907b2431b6b1e0d9960/`；两次原输出是真实 Astra Medium，**本轮 replay 不是新的真实模型调用**。

## 2. 工程变更与其边界

1. **仅局部修订启用紧凑上下文**：`--stage blocking` 或 `--stage shot` 加有效 `--targets`，使用 `war90-local-compact-v1`。不指定目标时保留原 full Resume。继续调用原已知的 Resume 新 ephemeral 会话，不凭此宣称实现 Continue/Refresh。
2. **完整性保留**：全部源文、当前 Intent/Beat/Blocking/Shot 各阶段的**完整 `proposal`**、对应阶段 Skill 以及 knowledge-index/review 方法、全部既存真人审阅文字及其候选/hash 绑定、批准 A 引用及当前阶段的未知风险，仍进入调用包。精简的是重复 pilot A artifact、历史累积模型 unknown、阶段附加传输 notes 与同一源文的第二份副本。`self.check(state)` 依旧对 authority、skill snapshots、候选内容及批准基线执行来源 SHA 核验。
3. **非目标 Shot 原文保护**：局部 Shot 输出须按顺序包含恰好一次行首 `ShotNN｜`（接受 `|`、冒号）段落；缺失/重复/乱序/新增标题会被拒绝。按同名段落比较原 candidate 与模型新 proposal，**非目标镜头正文逐字符（含空白）不变**；模型 `changed_targets` 不得漏报实际变化，亦不得申报目标范围外的修改。非法输出进入 quarantined run，原 candidate 和审批门槛保持不动。
4. **状态传播修复**：直接在 Shot 阶段做局部改动时（不经过 Blocking）也会在 `pending_shots` 标记目标及前后邻镜；真正 B 通过后仍由本人审阅记录清空 pending。无 `handoff` 情况无需编造 `shot_ids`，仅保存 run 不更新 candidate。
5. **可追溯元数据**：增加 `prompt_bytes`、`context_profile`；成功局部 Shot 回传 `verified_changed_shots`。JSON 仍为 WAR-90 pilot-only 的试验 transport，不改 WAR-35 正式数据契约。

## 3. 原真实调用与新版输入的独立体积对照

| 阶段 | 原 Astra 调用原始 input.txt | 新 `packet` 输入字节数 | 减少 |
| --- | ---: | ---: | ---: |
| Shot→Blocking | 119,045 B | 72,486 B | **39.11%** |
| Blocking→Shot | 128,933 B | 77,431 B | **39.94%** |

两轮同样使用冻结的真实 Source/Skill、当前批准基线、相同 scope、相同 Shot02/03/04 目标；原模型输出作为**只读、已存在的答案**送入新的运行壳测试路径，未使用新的模型调用。两次均 `candidate-saved`；最后 `verified_changed_shots` 为 Shot02/03/04，原 B 源工作区 byte SHA 未变，新测试分支 B 仍为待审。详见 `replay_frozen_real_outputs.py` 与 `replay-results.json`。

**严格不得外推**：字节数减少不能直接代表 token 数减少同样比例，更不能据此前 140.30 秒与 214.07 秒实际调用时长推算新模型耗时或断言紧凑输入的导演质量相当。新模型推理及用户交互体验要另行验证，但不应借一次效率测试改动用户已经批准的 B。

## 4. 回归、隔离与仍未覆盖的检查

- `python3 -m unittest discover -s tools/director-runtime-v0/tests -v`：**31/31 PASS**（旧 26 条 + 新 5 条）。新增检查覆盖 compact source/skill/阶段正文及真人审阅保留、合法局部修改及邻镜传播、隐藏非目标 Shot 修改、缺失/重复镜头与漏报修改、no-handoff 不提交。
- `replay_frozen_real_outputs.py`：按两次历史真实 Astra 输出离线重放、核对旧输入 SHA、完成本次 scope 的两阶段候选交接；明确 generator=`fake/replay`，不产生新的模型 thread，不修改两个已经批准工作区。`replay-results.json` 保存字节数与隔离判断。
- 原始 runtime 继续保证来源改变阻断、用户 A/B 显式决策、防旧被拒正文污染、锁/原子状态写入、模型不可自签批准。`Continue`/`Refresh` 仍拒绝，不把有限试验成功记作全部 B-flex 验收。
- **未知限制 1**：文本解析器仅认识稳定行首 Shot 编号，不是 WAR-35 类型化 ShotPlan。未列为 Shot 的全局导言仍可由模型改写，需要工程化公共语义校验或人工审阅；不能把“段落未变”写作所有故事事实未变。
- **未知限制 2**：Blocking 的 `changed_targets` 仍主要依赖模型申报，程序没有依据结构化 Blocking→Shot 映射验证内部语义是否越界；不能借 Shot 原文保护宣称全阶段逻辑正确。
- **未知限制 3**：只有紧凑包的构造与冻结输出重放通过，没有新真实模型在紧凑包下推理的视觉/叙事质量、时长和多次迭代压力测试；不改既有批准版本。

## 5. 结果与建议停点

本轮 **代码与确定性验证可以收口**，留下的下一项任务是决定是否做一次**真正的紧凑输入新模型调用与专业质量对照**，或先推进 Continue/Refresh 的可靠会话使用策略；无论哪一种，都应从已批准 B 派生独立试验分支，不自动更新或撤销真人 B。没有理由为上下文压缩再重复 Blender 的几何研究。

源码与最小复现脚本在本机 Git 项目内；完整数值和 SHA 由 `replay-results.json` 及 `evidence.sha256` 保存。

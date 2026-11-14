# WAR-90｜Director Skill v0 B-flex 运行壳独立验收与停点（2026-11-14）

## 本轮实际完成

工作机器 Eric；项目 `/home/sean/projects/canvas-lab`。ChatGPT 组织、审阅与验证；Eric Codex `gpt-6-astra` Medium 实现。新 Linear Issue WAR-90（In Progress）；WAR-89 研究独立保留，未修改七文件和冻结 C/D/E 剧本。

- 新增隔离 `tools/director-runtime-v0/{cli.py,runtime.py,README.md,tests/test_runtime.py}`，仅 Python 标准库。支持安全初始化、冻结来源和 Skill SHA、单活跃候选、明示 `pilot-only` 的人工 A/B 审阅、实质候选快照、拦截旧来源、局部 Shot/Blocking 影响标记、resume-pack 与 status。
- 初始 D 工作区 `docs/planning/WAR-90/pilot-D/`：复制 D 原文（SHA `65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`）和七文件 Skill，state 仅 `ready`，active=null、pilot_A=null、pilot_B=null、formal_WAR35_approval=false。
- **独立复测**：`PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tools/director-runtime-v0/tests -p 'test*.py' -v`，`26 tests in 1.346s; OK`。含 A 未批准下游阻断、旧 SHA 阻断、用户意见与模型输出隔离、候选单支与拒绝恢复、Beat→下游失效、局部 Shot 邻镜影响、并发初始化/生成冲突、原文完整输入及不可达路径保护。
- `run-stage --dry-run --stage intent --mode resume` 实际生成约 23.5 KB 完整调用包，存在 `docs/planning/WAR-90/pilot-D-intent-dry-run.txt`。包含冻结原文及必要 Stage、Authority、Skill、未证信息；**这是组包验证，不是实际模型生成**。
- 对 `runtime.py` 、`cli.py` 的门禁/候选/版本/执行路径做了独立静态审阅，状态和隔离目标正确；不把 pilot 审阅升级为正式 WAR-35 Review/Decision，不自动从模型返回文字签署批准。

## 真正模型调用的结果和阻塞

ChatGPT 于本轮通过新 CLI 实际运行 D `Intent/Resume`：`python3 tools/director-runtime-v0/cli.py run-stage --workspace docs/planning/WAR-90/pilot-D --stage intent --mode resume`。

**模型调用没有成功，属于平台额度阻塞而非导演模型失败**：
- 原始证据：`pilot-D/runs/7216f497b1bb4c14a61ce1a96d7fd1e6/{input.txt,events.jsonl,stderr.txt,metadata.json,command.json}`；
- 运行 events 返回 `turn.failed`，原文信息为 `You’ve hit your usage limit ... try again at Nov 15th, 2026 2:33 AM`（本地日期时区/实际恢复仍以届时平台显示为准）；Codex exit=1；
- CLI 正确标记本 run 为 `quarantined`，未产生有效 `result.txt` 或 candidate，状态依旧 `phase=ready`、`active=null`、A/B=false、未知 `media/geometry/audience` 未被提升，未发生任何用户审批；
- Eric Codex 负责实现的主进程也在写入 README 后遇到相同额度限制，已落盘成果与离线验证不因此被视为失败或完整真实实验。

## 能力分级及不能宣称的结果

**已做确定性实现测试**：init、来源 SHA、阶段门禁、candidate 保存、单候选 resume-pack、局部影响、状态原子写入、异常隔离。CLI 对真实 `Continue/Refresh` 采用显式拒绝：本版未实现同一 Codex 会话复用，不把每次全文新会话叫做 Continue。**真实 Resume 的完整 prompt 组装通过离线测试，但真实模型返回/解析/阶段交接尚未通过**，因为额度阻塞。未来需要实际成功的 D Intent 调用、用户 A 的真实选择、后续 Beat/Blocking/Shot，再做 B 审阅才算第一次人机交互通过。

实现风险/延期事项：
1. Codex 真实输出是否稳定符合 JSON 传输形状尚未知；失败日志不构成 JSON 失败证据。
2. 全文 prompt 包含 Skill + original source；仅 Stage 常驻，知识索引触发外部三源正文尚未实现按需检索，不要声称 K1–K7 源全文动态装配已完成。
3. `pilot-only` 本地审批依赖外部操作者忠实记录用户意见、无正式身份认证；WAR-35 冻结后需重绑真实 Approval/Decision 与指纹继承。
4. 运行时临时 auth 子目录在正常退出中删除；若非正常 SIGKILL 需手工核对 `runs/*/.codex-home`，不得版本控制认证材料。
5. 外部目录并发篡改、模型在自然语言中隐瞒越界、导演专业质量、真实媒体/观众理解仍未经过强验证。

## 下一个真实动作

Codex 额度恢复且操作者重新检查状态后，从 `phase=ready` 继续同一个 D 工作用例重试 Intent/Resume（不得复用失败 run 作为候选）。成功返回后只把 A 的导演意图与一项真实替代的代价简短交由用户审阅；**未经用户确认绝不继续 Beat/Blocking/Shot**。以后将当前 pilot 视为可弃置原型，WAR-35 规格冻结后通过薄适配迁移，不能自动升级状态。

## Git / Linear

本文件与试验工具和证据将由 ChatGPT 在检查 Git scope 后单独提交；当前共存 WAR-35 分支其它未提交改动不得触碰。WAR-90 维持 In Progress。原 WAR-89 研究阶段已完成首轮专业文本对照；没有因新运行壳修改其研究证据。

# WAR-90 Director text pilot

Python 3 标准库 CLI，面向 WSL/Linux。语义依据为 WAR-89 B-flex §12 和只读七文件 Skill。所有运行状态均标记 `war90-pilot-only-v0`，正式 WAR-35 approval 恒为 false。

## 快速上手

从 `/home/sean/projects/canvas-lab` 运行。此次已创建 `pilot-D`，重复 init 会明确报错。

```bash
python3 tools/director-runtime-v0/cli.py init \
  --workspace docs/planning/WAR-90/pilot-D \
  --source docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-D/script-D.txt \
  --skill docs/planning/WAR-89/director-skill-v0-candidate

python3 tools/director-runtime-v0/cli.py status \
  --workspace docs/planning/WAR-90/pilot-D

python3 tools/director-runtime-v0/cli.py run-stage \
  --workspace docs/planning/WAR-90/pilot-D \
  --stage intent --mode resume --dry-run

python3 tools/director-runtime-v0/cli.py resume-pack \
  --workspace docs/planning/WAR-90/pilot-D --stage intent

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tools/director-runtime-v0/tests -v
```

`--dry-run` / `resume-pack` 仅输出 prompt。需要留档时，由调用者将 stdout 重定向到白名单目录内的新文件。CLI 所有 workspace 写入限定在 `docs/planning/WAR-90/` 的子目录。初始化不覆盖既有目录，路径中的软链接被拒绝。

## 真实 Intent 调用与停点

ChatGPT 独立审阅代码后执行下列命令。真实模型固定 `gpt-6-astra`、Medium，最长等待 900 秒。

```bash
python3 tools/director-runtime-v0/cli.py run-stage \
  --workspace docs/planning/WAR-90/pilot-D \
  --stage intent --mode resume
```

有效结果形成探索候选并停在 `awaiting-human-A`。模型返回的批准字段不会进入有效传输对象。实际用户交来 A 意见后，操作人保存原文为工作区之外的文件，例如 `docs/planning/WAR-90/user-A.txt`，再显式运行下列命令。示例文件需由真实意见创建。

```bash
python3 tools/director-runtime-v0/cli.py record-review \
  --workspace docs/planning/WAR-90/pilot-D \
  --checkpoint A --decision accept \
  --evidence-file docs/planning/WAR-90/user-A.txt --actor human
```

`accept|reject|revise` 均记录候选 ID、内容 SHA、用户意见原文与 SHA、时间及外部路径。`actor human` 是操作人的显式声明，`identity_verified` 恒为 false。操作人负责确认意见真实来自用户，CLI 无身份鉴别能力。工作区内的模型输出不能直接用作 evidence-file。复制到外部再冒充用户的行为仍依赖操作纪律。

获得真实 A 后，可按同一命令入口执行 `--stage beat`、`--stage blocking`、`--stage shot`，每次使用 `--mode resume`。B 通过 `record-review --checkpoint B` 记录，要求当前 Shot 及 Beat/Blocking 全场交接存在。B 人工接受表示用户已审阅 pending shots 的文本问题，媒体、几何、观众未知继续保留。

## 会话模式支持

| 模式 | 当前支持 | 验证边界 |
| --- | --- | --- |
| Resume | 每次创建新 ephemeral 会话，完整重投原文、pilot Intent、一个累积候选、审阅原因和知识 | 输入包和适配器通过假进程测试，真实模型调用待独立代码审阅 |
| Continue | 显式拒绝，退出码 2 | 本机 0.167.2 帮助提供 exec resume，持久会话复用尚未实施 |
| Refresh | 显式拒绝，退出码 2 | 同上，调用者可明确选择 Resume |

实际调用保存 Codex `thread.started` ID。ephemeral 会话 ID 仅用于追溯。模型可跨阶段的全文恢复依赖存储内容。CLI 不自动把 Continue/Refresh 改名为成功。

真实适配器启用 read-only sandbox、禁用 shell 工具和 web search、忽略用户配置，并将项目说明读取预算置零。它创建 workspace 内的临时 CODEX_HOME，从现有 CODEX_HOME 读取 auth.json 的临时私有副本，供现有登录认证使用。普通结束/异常会清理该目录，SIGKILL 或主机断电可能留下临时认证副本，恢复操作前应由操作人检查 `runs/*/.codex-home`。运行日志、缓存目录均指向该隔离目录。真实 CLI 对参数、认证、沙箱和模型输出的兼容性仍待运行核验。

## 候选、变更和局部返修

一个 `state.json` 原子替换决定当前活跃候选及 pilot A/B。写操作由 flock 串行化。初始化在同目录临时目录中完成后 rename，父目录锁阻止协作进程重复创建。源码、Skill 原始路径及八份冻结副本在调用前后和 review 前逐一验 SHA，变更会阻断旧结果交接。status 将失效候选仅列为 history_candidate。历史 run 证据保留，新输入需新建 pilot 并重新取得所需用户审阅。

每个活跃候选携带目前有效的阶段全文。Beat 重写会使下游 Blocking/Shot 失效。Shot 返回 Blocking 时保留 Shot 上下文并标记目标及直接前后邻镜待复检，再回 Shot 时继续显示 pending。整场知情窗口、覆盖责任随 prompt 提交复核。

已有 Shot 后，局部回退可用下列形式。真实运行要在真实 A 后，离线模拟由 unittest 完成。

```bash
python3 tools/director-runtime-v0/cli.py run-stage \
  --workspace docs/planning/WAR-90/pilot-D \
  --stage blocking --mode resume \
  --targets Shot02 --scope '调整 Shot02 的动作间隙，保持原文知情顺序'
```

目标须属于当前有序 Shot 列表。模型报告的实际修改对象须落在允许目标内。局部 Shot 修订禁止增删或重排镜表。模型报告硬冲突或上游事实变更时结果隔离，保留原有有效候选。范围检查依据传输字段，隐藏在自然语言里的越界和虚假自报仍需独立人类审阅。

`handoff=false` 或相同阶段 proposal 完全相同会只留 run 证据，不新建 candidate.json。是否有专业实质依赖模型诚实报告和人类复核，文字变化检测无法证明专业进展。reject/revise 清除活跃候选及线程引用，恢复包保留用户原因和有效 pilot A，历史被拒方案正文不进入工作候选。用户意见自身若引用旧方案，按否决背景阅读。

## 存储与验证边界

- `source.txt` 与 `skill/` 保存原字节快照，权限 0444，state 中记录来源、SHA 和初始化时间。
- `state.json` 保存单活跃候选、pilot A/B、用户意见与未知项。A 仅授权试验下游探索。
- `runs/<id>/` 保存 input、原始 result、events、stderr、command、metadata，以及实质交接的 candidate.json。
- metadata 包含输入/输出/事件 SHA、真实 thread ID、模型、模式、时间、范围和失败原因。失败/中断保留隔离证据。崩溃后 `started` 记录表示尚未提交的尝试，可检查后显式重试，重试创建新 run。
- 模型 JSON 仅为本 CLI 的实验传输封装。四阶段成果保留专业短文，未建立正式 DirectorPlan 类型或依赖签名算法。
- knowledge-index 和相关阶段卡全文进入输入。DS/TF/VM 外部章节仅以索引引用呈现，本版不自动检索这些章节，知识缺口需要模型明确报告。
- 测试使用临时真实文件系统、假生成器和假 Codex 子进程。fake 标记持续保留。测试结论覆盖状态/存储/输入包，导演专业能力、真实恢复等价性和媒体表现待验证。
- 信任本机操作人。软链接与路径检查防常见误写，无法抵御恶意并发文件替换、手工篡改状态或伪造用户身份。

## WAR-35 替换策略

保留原文、Skill 快照、原始调用、意见和 SHA 为迁移证据。WAR-35 冻结并提供真实接口后，用薄适配层替换 state 存储与 pilot review gate，按正式规则重新绑定来源、版本、Review/Decision 和依赖。现有 pilot accept 只能作为人工意见证据，迁移时需正式重新审阅与绑定，不能直接升级正式批准。WAR-52 投影、Canvas、GPU、媒体流程均留待其授权任务。

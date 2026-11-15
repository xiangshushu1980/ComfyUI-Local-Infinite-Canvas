# WAR-90｜D《错过的钥匙》A 批准后 Beat→Blocking→Shot Plan 全场 B 预审（2026-11-15）

## 执行状态与批准边界

- 工作机器 Eric，项目 `/home/sean/projects/canvas-lab`，Linear WAR-90；本次沿用 `tools/director-runtime-v0`（pilot-only，不是生产 DirectorPlan/Review）。
- 用户当前对话的明确批准原话与关联候选：`docs/planning/WAR-90/user-A-approval-20261115.md`，SHA-256 `5fc92ce15dd12cedfa933666270c47793e99c9ced5a5e4ae7851d964fc83e032`，指向修订版 A `68d2717b905641d5a872550a896abcfc`（**钥匙细节优先**）。`record-review --checkpoint A --decision accept --actor human` 已真实执行并保存 `pilot-A-record-20261115.json`。此处的 `identity_verified=false` 说明本地 pilot 操作不提供正式身份认证，但本轮 evidence 内容来自用户当前对话的真实批准，不是模型自签。
- 已按用户授权连续执行 `Beat → Blocking → Shot Plan`，每一阶段调用均为 Eric Codex `gpt-6-astra` Medium，通过 **新会话完整 Resume 包** 串接；并非经测试的同一会话 Continue/Refresh。每阶段均有真实 Codex events、input/result、SHA 和单活跃候选记录。
- 截至本报告：`phase=awaiting-human-B`，`gates.A=true`，`gates.B=false`，`formal_WAR35_approval=false`，当前活跃 Shot 候选 `d23b8bdab90f43ef8ff0098fb8021f78`。没有用户 B 批准，没有 GPU、Canvas、Blender、ComfyUI 或 H3 调用。

## 三阶段真实输出（原始证据）

| 阶段 | Run ID | 输出 SHA-256 | 简述 |
| --- | --- | --- | --- |
| Beat | `bd5a44cc27324852a8efdaacc7fc5e82` | `5065a80e33e7cdb905234fb43e21508109687eae47676a300e79eb774a6a6fc5` | 六个认知／行动 Beat，明确 **六 Beat ≠ 六镜**，完整四句对白、首次先知、中途再遮挡及单次右手交接 |
| Blocking | `eca2cde95240498baf7fb01302cd9f6b` | `b358ae440fbbafc17cb275c50b95b45a7bd7a5fbf1dea0c439d17881a26e802e` | 固定钥匙位置 K、文件挪开后蓝夹由文件叠承托且伸出遮 K，林与周观察通道及各自知情边界；左手持夹、右手取钥匙交周右手的连续中间态 |
| Shot | `d23b8bdab90f43ef8ff0098fb8021f78` | `57665d7e94b5a004c6d864940fc17f9c86595d58dd94e633f0c20d54e15e9e6e` | **四镜整场**：Shot01 寻找与空间；Shot02 首次辨认+再遮挡连续近景；Shot03 周问→林重新发现与停顿；Shot04 一次右手交接+离开与留下 |

原始逐份数据：`docs/planning/WAR-90/pilot-D/runs/<run-id>/`，均已保存模型 input、events、metadata、result、candidate。冻结剧本 SHA-256 `65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`，没有修改原始剧本或 WAR-89 七文件 Skill。

### 四镜 B 候选的观看与切点

1. **Shot01（关系中全景）**：周近门、林桌前整理，两句原话“钥匙呢？”“刚才还在桌上。”；林开始提移文件，未露出可辨钥匙时切 Shot02。
2. **Shot02（斜俯桌面近景）**：同一文件提移动作接续，观众先认出固定 K 的银色钥匙；林仍未注意。保持连续观看，让蓝夹落于文件叠并伸出盖住同一 K，避免钥匙突变或重复遮挡；夹落稳后切 Shot03。周正在接近，不借镜头暗示她已见钥匙。
3. **Shot03（双人中景）**：周到桌，只看覆盖位置，问“你刚刚是不是盖住了什么？”；林停下整理，移开蓝夹，首次真正认出钥匙，短暂停顿后说“找到了。”；此时钥匙仍在桌上，切 Shot04。
4. **Shot04（稍宽关系景）**：周伸右手，林右手从 K 取唯一钥匙，手部短暂共同接触后只交付一次，周握稳后向门走，林留桌边；不新增越门槛、道歉、收钥匙或关门动作。

全场目标 **约 35–40 秒属于冻结剧本提出的目标**，未冻结各镜秒数，亦不是 H3 单片段限制。文本没有真实媒体可读性或几何验证。Shot Plan 只代表候选，不等于制作就绪。

## 多 Agent 分层独立审阅

实际四个不同模型会话：`reviewer-story` = Luna Low、`reviewer-craft` = Luna Medium、`reviewer-space` = Astra Medium（复杂眼线／道具依赖专项），由 `main-reviewer` = Luna Medium 综合核证原始故事和三份原始意见。实际四调用均 exit=0。权威本轮审阅证据：`docs/planning/WAR-90/review-B-round1-20261115/`，含 `manifest.json`、`frozen-B-packet.txt`、各独立 `prompt.md/result.md/events.jsonl/run.json`、主审阅原始报告及 `summary.json`。

**主审阅裁定：`ready_for_user_B`**，只是文本适宜用户 B 审阅，不等于 B 自动通过。主审阅逐项判断并未机械采纳 Reviewer 的所有 P1：首次钥匙窗口、假 POV、周能否未目击属于尚未证成的摄影视听／几何风险；文本已给出观看任务、顺序和窗口，不应强制继续在 Intent/Shot 中写死具体时间。Shot02→03 “林停下手里的动作”在文件夹落稳、双手空闲后略有排演措辞问题，建议后续明确停止的是仍在继续的手部回撤或整理动作，但并未出现要求另一次落放或新增动作的来源硬冲突。未发现遗漏决定性事件或重复交接。

### 用户 B 必须知悉的开放风险

- **几何组合条件尚未实测**：文件叠旁移后能否稳定承托伸出遮住固定 K 的蓝夹，且不碰动钥匙；林能否阻挡周的视线，同时让 Shot02 摄影机看清 K 与支承关系；周能否自然走到遮挡位置才看到异常。
- **实际观看尚未证实**：Shot02 首次钥匙轮廓是否容易辨认、近景会不会误读成某角色 POV、Shot03 双人面部与桌面信息能否同镜可读、交接手部与自然停顿是否清楚。
- **时间与声音尚未证实**：约 35–40 秒容纳自然四句对白、两次显露、观看窗口、短暂停顿与单次交接；未做观众观看、媒体或几何实测。
- **工程事项**：pilot state 的聚合 `unknown` 仍包含首次未批准 A 时的历史未知句子，当前 Authority/pilot A 审阅记录已更新且由各阶段明确识别历史时态。后续需改为按来源/时间分级聚合未证项，避免陈旧 unknown 干扰新的 Resume。此项不改变当前 B 候选与用户真实 A 审批。

## 下一停点

应把四镜候选及未证风险**交真实用户 B 审阅**。用户如批准，另记录其真实 B pilot-only 决定，再讨论后续 Canvas/Blender/H3 媒体验证；如要求调整，依据具体镜头/调度范围局部修订和相关邻镜复检。**本轮没有 B accept，不修改 WAR-35/52、不启动视频生成。** 项目详细证据以 Eric 本地 Markdown 与 Git 为权威，Linear WAR-90 只维护状态、入口和当前阻塞。

# WAR-90｜D《错过的钥匙》A 用户反馈局部修订及分层审阅（2026-11-15）

## 用户反馈、身份与成果

**用户原始反馈**：`WAR-90《错过的钥匙》的 A 导演意图需要修改：我更希望以钥匙细节引导观众观看。请先局部修订，再交我审阅。`

- 原始反馈独立原文与约束：`docs/planning/WAR-90/user-feedback-A-revision-20261115.md`，SHA-256 `279884d4449fa39ebf3a0b10636cf2d8a3842f23f29ff8a7c665cabf28f6e782`。
- 旧版 A 探索候选 run `93fc96166f56424c8a69bfa6f12ff5e9`，输出 SHA-256 `9179fdb542e5dcfa74085d5e2a0a30cac390ccf70e2d4182eee5eb76b060c522`；被替代但冻结保留，不覆盖。
- 此次基于**同一活跃未批准候选**进行 Intent 局部修订：`run-stage --stage intent --mode resume --scope <真实用户反馈、证据 SHA、最小修改范围和硬事实保护>`。新 run `68d2717b905641d5a872550a896abcfc`；实际模型 `gpt-6-astra` Medium，exit=0，`candidate-saved`；新输出 SHA `d7ab9dcafc200ca12e2fa3550d3a60de87304a66a8d8929663814bf08def05fe`，输入 SHA `02b7556381c2d58b67d2028487e18c152cfca203e3d6003bcedb8a7bd5040fbd`。
- 所有冻结原始证据 `docs/planning/WAR-90/pilot-D/runs/68d2717b905641d5a872550a896abcfc/`，含 prompt、result、事件、metadata、候选与 SHA。原剧本固定 SHA `65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`。
- 仍处 `phase=awaiting-human-A`、active 为本次 run，`pilot_A=null`、`pilot_B=null`、`formal_WAR35_approval=false`；用户只要求重审，**不是批准**。没有进入 Beat/Blocking/Shot、没有调用 Canvas/Blender/ComfyUI/H3。

## 真实修订差异与专业边界

从“共享行动关系优先、必要时突出钥匙”变为**“钥匙可见状态引导观众观看，人物动作解释钥匙变化原因”**：

1. 寻找对白建立目标，林挪开文件时，让观众通过显露变化注意到同一把银色钥匙；首次辨认必须获得**表达优先级**，不能只是偶然出现在画面里。
2. 之后沿同一位置理解蓝色文件夹无意再次遮住钥匙，不能让观众误以为钥匙位移或神秘消失，也不能让林或周提前认出钥匙。
3. 周只察觉文件夹遮挡位置，林重新看见钥匙后自然停顿，再完成一次交付到周右手。自然表演、对白和知情顺序不变；不机械规定镜数、特写、停顿秒数或实际媒体效果。
4. 明确真实代价：若强调细节过长，会挤压人物共同活动的观察余量，甚至让林未见钥匙显得不可信；具体画面、辨认时间、机位交给后续 Beat/Blocking/Shot 及媒体验证。

## 分层审阅与一次证据纠错

真实多 Agent 调用证据在 `docs/planning/WAR-90/review-round2-20261115/`：
- 第一轮：`reviewer-story` Luna Low、`reviewer-craft` Luna Low，两名隔离独立 Reviewer；`main-reviewer` Luna Medium 汇总并裁定。两 Reviewer 均认为用户要求已经实质落实，没有故事硬冲突；提出可辨认窗口/自然表演/时间与来源引用等问题。
- 初次主审阅裁定 `needs_local_revision`，理由是认为候选“已加载知识索引、Review 正文”与“未加载外部正文”矛盾。ChatGPT 没有直接按此修改候选，而是从本次实际 `input.txt` 提取 `B-FLEX INPUT` 中的 `knowledge` 字段，**逐字核对**与冻结 Skill 文件的四份正文完全一致：`SKILL.md`、`stages/intent.md`、`references/knowledge-index.md` 和 `references/review-method.md`。外部 DS/TF/VM 的源章节没有加载，二者不矛盾。证据 `knowledge-evidence.json`，包含输入 SHA、字段名、字节数和逐文件 SHA。
- **限一次**追加第三名独立 `reviewer-evidence` Luna Low 定向核验，裁定不存在 P1 来源矛盾；主审阅 Agent 通过新的独立 Luna Medium 会话 `main-evidence-reconsideration` 接收原三份审阅和证据，明确**撤回原阻断**，最终裁定 `ready_for_user_A`、不需进一步修订候选。原判断及更正证据均保留，不覆盖历史输出。
- 主审阅没有采纳“必须在 Intent 决定让出多少具体镜头时间”的要求，认为这会提前锁死 Shot；保留观众辨认、遮挡因果、周的视线与自然表演尚待验证。实际并未产生审阅后新导演候选或改写七文件 Prompt。

## 交用户的新版 A 决策包

**推荐新版**：以钥匙细节引导观看：先从寻找对白知道目标，文件移开时让观众先认出银色钥匙；随后跟随相同位置看到蓝色文件夹无意再次遮挡。林一直未注意钥匙，周只因遮挡位置异常而发问；林重新发现后短暂停顿，随后把同一钥匙交周右手，周朝门走、林留桌边。

**表达代价**：钥匙细节过重可能使人物动作退居次位，也更依赖构图与表演证明“林为何没看见”。因此仅确认观看优先级，不在 A 阶段定镜数、机位或秒数。

**下一步**：将以上新版 A 提交用户确认。用户明示认可或提出进一步修改后，再忠实保存意见/实际差异；只有获得真正 A accept 才记录 `pilot_A` 并进入 Beat。主审阅通过、生成成功均不等于用户已批准。

本次证据仅保存于 Eric Markdown/Git，Linear 是任务索引。没有新增正式 WAR-35 Schema 或批准接口。

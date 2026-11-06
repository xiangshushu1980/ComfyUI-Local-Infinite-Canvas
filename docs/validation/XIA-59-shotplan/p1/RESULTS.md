# XIA-59 P1：静态编译与对照（2026-11-06）

## 条件与边界

用户确认进入 P1。四路 P0 输入由 DeepSeek `deepseek/deepseek-flash`、thinking off 生成；P1 由本对话 Codex 手工翻译、编排与审阅，具体后端模型版本未由运行环境独立提供，标记未知。没有调用 DeepSeek、Pi 或其他外部 LLM 生成本阶段文本。每个样本 `metadata.json` 给出输入路径与 SHA256、输出 SHA256 和镜头起点；P0 原件保留不变。

P1 使用 P0 冻结的 `upstream/h3/SKILL.md` 和 `references/ref-en.txt`。Skill 引用的空间约束清单原先未冻结：本次从 `/home/sean/projects/comfy-ops/.pi/skills/h3-prompt-writing/references/spatial-camera-constraints.md` 读取并另存 [后补快照](spatial-camera-constraints-later-snapshot.md)，SHA256 `5e9ca18b3c9b2013da3a13708e539ee6469fa82a4824109a846b0ebeb097d639`。无法证明它与 P0 冻结时版本一致，不能称其为原冻结材料。三张图片均仅有输入中的文字描述，未读取图片，Picture 3 被用作场景和空间关系的来源描述，不把它指定为首帧或镜头锚点。

三个 `beat-direct` 是各自固定 Beat 的独立输出链路，没有将 Shot Plan 作为其输入或编译对象；但同一 Codex 在本对话先审阅过 P0，无法声称作者上下文隔离或盲测。每个直出基线采用一个连续镜头，是本次 Codex 的选择，不能当作 Skill 对该 Beat 的唯一输出。P0/P1 跨模型，不能把差异直接归因于 Skill 或方法。

共同适配：写六段 Ref2VA 英文结构，保留中文台词；将 A/B/场景映射为 Subject 1/2/3，并按实际首次发声分配 S 编号。为使无音频输入的六段可落地，统一补入轻微咖啡馆环境声、非画内配乐 N/A；这些是编译默认值而非 P0 已指定事实。各稿为了维持镜头和时间使用简洁文字，未达到 ref-en 通常建议的 350–500 词，亦非逐字段的无损翻译：具体景别、动作及关键状态被提炼，部分细微表情、遮挡可能性、镜头切换理由和 state 字段文字未逐项保留，不应称为完全原样编译。来源文件和下述审查用于追溯。由于生成 Prompt 不是机器代码，验证为静态人工阅读与机械检查，不等于 H3 执行。

## 逐场对照与分开评价

评级仅限当前单样本文本：**可追踪**=关键 Beat/时间可从文本追踪；**有风险**=存在潜在执行或来源冲突；**有损**=编译没有完整保留源细节。不是视频质量分数，也不构成方法排名。链接分别为编译稿，其旁 `metadata.json` 指向原始 P0。

| 场景 | P0 组与评价 | P1 稿与评价 |
|---|---|---|
| 对话 | Native：可追踪；B 回答仅 1.2 秒，A 反应 0.8 秒有时间压力。 | [Native](01-dialogue/native/prompt.txt)：保留 4 镜与对白；简化动作和焦点，**有损**，时间压力继承。 |
| 对话 | Toonflow：可追踪；首镜“固定”与“缓推”表述含糊。 | [Toonflow](01-dialogue/toonflow/prompt.txt)：保留 3 镜及矛盾措辞；省略部分手和呼吸细节，**有损**。 |
| 对话 | Director：可追踪；固定或缓推未定，2 秒需容纳停顿及回答。 | [Director](01-dialogue/director/prompt.txt)：保留原可选运动与时间；细节压缩，**有损**。 |
| 对话 | ViMax：有风险；2.5 秒同时包含“停顿数秒”和回答。 | [ViMax](01-dialogue/vimax/prompt.txt)：保留时间与该冲突；细节压缩，**有损**。 |
| 交杯 | Native：可追踪；4 镜，右手推、左手接与末态均明确。 | [Native](02-handoff/native/prompt.txt)：保留时间、手别和杯状态；其他场景细节压缩，**有损**。 |
| 交杯 | Toonflow：可追踪；交接前后各有一次抬眼，末镜仅 1 秒。 | [Toonflow](02-handoff/toonflow/prompt.txt)：保留两次抬眼、镜头与手别；其他细节压缩，**有损**。 |
| 交杯 | Director：有风险；源计划指定无测量依据的 30–35°、35–40°。 | [Director](02-handoff/director/prompt.txt)：保留源给出的角度作为计划值，不能当场景实测；省略了源中的约一前臂距离和抬头角度，**有损**。 |
| 交杯 | ViMax：可追踪；首镜固定与轻推表述有歧义。 | [ViMax](02-handoff/vimax/prompt.txt)：保留三镜、运动与手别；细节压缩，**有损**。 |
| 离开 | Native：有风险；完整台词字段与下镜截断的实际发声范围不清。 | [Native](03-overlap/native/prompt.txt)：沿用全文和跨镜截断的矛盾，未确定截断位置，**有风险且有损**。 |
| 离开 | Toonflow：有风险；两镜各有完整句，备注又说首镜完整说出、次镜延续后中断。 | [Toonflow](03-overlap/toonflow/prompt.txt)：显式保留重复字段及矛盾说明，不应直接视为无歧义的生成指令，**有风险且有损**。 |
| 离开 | Director：有风险；首镜台词完整字段、第二镜对白为空但说话中断。 | [Director](03-overlap/director/prompt.txt)：保留未完跨镜和中断语义，未指定截断字，**有风险且有损**。 |
| 离开 | ViMax：有风险；首镜写完整台词又写结束时仍在说，次镜中断。 | [ViMax](03-overlap/vimax/prompt.txt)：保留该冲突，未决定演出方案，**有风险且有损**。 |

Beat 直出基线：[对话](01-dialogue/beat-direct/prompt.txt)、[交杯](02-handoff/beat-direct/prompt.txt)、[离开](03-overlap/beat-direct/prompt.txt)。前两者为单镜、概括性表述，保留指定动作与对白；离开场景仍存在完整台词文本和中断位置的歧义。不得将这个独立链路并入 Native→Shot Plan→H3。

## 检查及未完成事项

15 份文本都包含六段且顺序正确；12 份编译稿的镜头数和起点与 P0 相同，原对白字符串均出现；15 份 Prompt 的 SHA256 与元信息匹配。以上是机械文字检查，不验证对白说话人语义、源字段逐项覆盖、跨镜音频标签或 H3 执行。人工检查已发现全部稿件使用压缩式改写，不能满足将 P0 原样无损编译的严格要求；交杯 Director 两个源量化细节也被省略。以上交付为可审查的 P1 初稿，**不能宣称 P1 无损编译与完整验收已完成**。下一步应逐字段补齐，独立复核，尤其处理台词跨镜的 `<scenetrans>` 表示和源内冲突；不能擅自改镜或编造截断字。

P2 未获授权；未运行 GPU、未修改 Canvas 或 XIA-56。

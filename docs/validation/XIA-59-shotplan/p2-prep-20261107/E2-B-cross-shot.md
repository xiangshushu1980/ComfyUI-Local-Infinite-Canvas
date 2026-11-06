# E2 候选 B：跨切点中断（新导演选择）

状态：静态候选，未冻结为原方案；不等同于 Toonflow 原始输出，不含原样恢复主张。

## 来源与选择

- 完整剧本原句（元数据，逐字保留）：B「我以为你会留下来。」
- Beat 未定：真实发声是否完整、实际中断字、起止时间均无源事实。
- 本候选实际发声：切点前 B「我以为你会」；切点后只接续「留」；「下来。」不发声。
- 中断因果：B 跨切点持续发声；A 在新镜头中起身后进入 B 的视野，B 约 4.60 秒停止。
- 计划时间：B 约 3.20 秒起声；4.20 秒切点；「留」约 4.20–4.55 秒；约 4.60 秒发现后停止。全为未经口播测量的导演目标。
- A 的起身重心转移始于切点前，Shot 2 接续站起和向左离开。唯一白杯保持原位。

## 新导演 Shot Plan

| Shot | 时间 | 实际声音 | 动作与状态 | 镜头职责 |
|---|---|---|---|---|
| 1 | 0.00–4.20s | B (S1) 约 3.20–4.20s 发声「我以为你会」；句子/声音连续越过切点。 | A 坐左、B 坐右；A 约 4.00s 开始移重心离座；B 尚未发现。杯子不动。 | 固定中景双人，建立 B 的句子与 A 起身动作开始。 |
| 2 | 4.20–8.00s | 同一声音连续接上「留」约 4.20–4.55s；B 约 4.60s 发现 A 后停声；不说「下来。」 | A 接续起身并向左侧出口走；B 仍在座位附近转向出口；杯子仍在 A 原位。 | 固定中远景保持人物、桌及出口，呈现发现—中断—沉默。 |

## H3 Ref2VA Prompt（静态候选）

subject_definitions:
<Subject 1> is A, the short dark curly-haired woman described by <Picture 1>, wearing a green cardigan and pale purple top.
<Subject 2> is B, the short dark-haired man described by <Picture 2>, wearing a navy overshirt and white T-shirt.
<Subject 3> is the daylight café, round table and left-right two-person layout described by <Picture 3>.

summary:
[reference generation] Create one eight-second natural café scene using <Picture 1>, <Picture 2>, and <Picture 3> as identity and setting references. A begins seated on the left, B seated on the right, and the single white ceramic cup stays in front of A throughout.

retention_analysis:
<Subject 1>: retain A's identity and clothing from <Picture 1>; she remains the person who rises and exits to the left.
<Subject 2>: retain B's identity and clothing from <Picture 2>; he remains seated near the table and turns toward the left exit.
<Subject 3>: retain the café and left-right seating arrangement from <Picture 3>.
The single cup remains at A's original place and is never touched. No second cup, third person, or extra spoken line is introduced.

detailed_description:
Live-action, natural daylight by a café window. Keep A on the left and B on the right at the round table. The only white ceramic cup remains in front of A for the full video. [Shot 1] A fixed medium two-shot shows both people and the cup. At about 00:03.200, B (S1), a quiet adult male voice, begins the sentence fragment: <d>[Chinese] 我以为你会</d><scenetrans> His same voice continues seamlessly across the cut without a pause. A begins shifting her weight toward standing at about 00:04.000. [Shot 2] At 00:04.200, cut to a fixed medium-wide view that keeps the table and left exit visible. <scenetrans> The same B (S1) voice continues the same interrupted sentence with: <d>[Chinese] 留</d> He notices A rising at about 00:04.600 and immediately stops speaking; the unspoken remainder “下来。” is not audible. A continues rising and walks toward the left exit without touching the cup. B stays near his seat, turns toward the exit, and remains silent. The single cup stays in A's former place through 00:08.000.

overall_soundscape:
Quiet café room tone. B's voice carries continuously across the 00:04.200 cut, then stops when he notices A leaving; no other dialogue is heard.

non_diegetic_music:
N/A

## 静态语法检查

六段字段顺序符合冻结 Ref2VA Skill；两个 `<d>` 只含导演候选实际发声的原句片段；speaker S1 在两段均指 B，保证身份一致；切点 00:04.200 在两处使用 `<scenetrans>` 并明示同一声音连续。没有使用 `<cutoff>`，因为中断发生在视频结束之前。该连接点写法依赖后补 base-en 快照中“连接两部分都标记”的说明；P1 冻结版 H3 Skill 仅指向 ref guide，本地精确 tag 解释范围以该冻结指南为准。静态语法通过不证明 H3 会生成无缝跨镜音频或匹配口型。

# E2 候选 A：同镜头内中断（新导演选择）

状态：静态候选，未冻结为原方案；不等同于 Toonflow 原始输出，不含原样恢复主张。

## 来源与选择

- 完整剧本原句（元数据，逐字保留）：B「我以为你会留下来。」
- Beat 未定：真实发声是否完整、实际中断字、起止时间均无源事实。
- 本候选实际发声：B「我以为你会」，不发出「留下来。」
- 中断因果：A 在同一镜内移重心并开始起身；B 察觉后停止发声。
- 计划时间：B 约 2.70–3.80 秒发声；A 约 3.35 秒开始移重心；B 约 3.80 秒停止。均为导演候选时间，不是口播实测。
- 切点：4.20 秒。Shot 1 内中断，Shot 2 静默。

## 新导演 Shot Plan

| Shot | 时间 | 实际声音 | 动作与状态 | 镜头职责 |
|---|---|---|---|---|
| 1 | 0.00–4.20s | B (S1) 于约 2.70–3.80s 说「我以为你会」；A 移重心起身时，B 在约 3.80s 停声；不说「留下来。」 | A 坐左、B 坐右；唯一白杯始终在 A 原位且无人触碰。A 约 3.35s 开始起身。B 发现 A 的移动时停止说话。 | 固定中景双人镜，观众同框看见发声、离开征兆和停止关系。 |
| 2 | 4.20–8.00s | 无台词；B 保持沉默。 | A 从左侧起身并向左侧出口走；B 留在座位附近转向出口；唯一白杯仍在 A 原位。 | 固定中远景同时保持两人、桌与出口方向可读。 |

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
Live-action, natural daylight by a café window. Keep A on the left and B on the right at the round table. The only white ceramic cup remains in front of A for the full video. [Shot 1] A fixed medium two-shot shows both people and the cup. B (S1), a quiet adult male voice, says: <d>[Chinese] 我以为你会</d> A begins shifting her weight toward standing at about 00:03.350. When B notices her movement, he stops speaking at about 00:03.800 within this same shot; the unspoken remainder “留下来。” is not audible. Hold their expressions briefly. [Shot 2] At 00:04.200, cut to a fixed medium-wide view that keeps the table and left exit visible. A continues rising and walks toward the left exit without touching the cup. B remains near his seat, turns toward the exit, and stays silent. The single cup remains in A's former place through 00:08.000.

overall_soundscape:
Quiet café room tone under the single spoken fragment. After B stops speaking, no further dialogue is heard.

non_diegetic_music:
N/A

## 静态语法检查

六段字段顺序符合冻结 Ref2VA Skill；`<d>` 只含本候选实际发声片段且 speaker S1 指向 B；该句没有跨镜，因此不需 `<scenetrans>`。没有使用 `<cutoff>`。中文原剧本全文只在本文件的来源元数据中保留。静态格式通过不证明 H3 能准确发音或呈现中断。

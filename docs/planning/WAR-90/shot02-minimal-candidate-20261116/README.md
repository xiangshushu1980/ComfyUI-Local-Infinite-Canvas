# WAR-90｜正式 Canvas Agent 对 Shot02 最小局部修订候选的审阅

日期：2026-11-16。用户明确采用“通过正式 Canvas Agent 对 Shot02 提出最小局部修订候选，先审阅，不修改批准 B”。

## 执行范围

- 正式浏览器 Origin：http://canvas.localhost；实际画布 projectId=2FwEbySI5PYe7d6BL4pES；Shot02 映射节点 text-1794832120997-1；4 个已批准 B 的文本展示节点。
- 模型通过正式 Canvas Agent 已启用的 director-skill-v0-candidate 执行原生 turn（gpt-6-luna/high）。禁止编辑 Canvas、Runtime B、批准与媒体生成。
- 在调用前严格校验浏览器唯一连接、对应 projectId/clientId、4 节点和已批准 B 的 authority state SHA256=23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7；本轮选区为空，因此按确切节点 ID 绑定，不虚构“已选中”。
- 原生 Agent 实际调用了 4 个工具：canvas_get_state，以及三次只读 Runtime CLI review-shot（Shot01、Shot02、Shot03）。调用已从正式 Agent thread 的真实工具历史核实，且无写 Canvas 的 tool call；不是 ChatGPT 自己模拟 Skill。
- HTTP turn 200、已正常结束；执行前后 Project、4 节点（包括 compact 内容 SHA）、标题、ID、选区均不变，批准 B state SHA 未变。详细取证见 agent-candidate-audit.json。临时脚本 request_native_candidate.py 使用 callIssued 标记拒绝自动重复发送。

## Agent 原生结论

**R1 结果：无必要修订（No-change disposition）。** 不能为了产生候选而强行修改。此结果不是“生成了可批准的新 B”，也不是用户已批准免修。

1. 当前真实冲突是注意力/动作时序负荷的风险，不是文本字数本身：要让观众先在纸边辨认唯一银色 K，再理解蓝夹落纸叠并重遮 K，同时林让位、右手轻理。实际过载尚未由观看、时间或几何证据证实。
2. 单纯取消 Shot02 的右手轻理不成立，Shot03 的入态明确从同一次轻理的进行阶段跨切，周的问句才将其打断。挪移轻理须同时重审 Shot03 与跨切方法，不是最小孤立修订。
3. 必须保留 Shot01 提移已启动、K 尚未辨认的切点；Shot02 同一动作显露、蓝夹自然无意再遮、K 固定唯一、周当时未见 K；Shot02 出态蓝夹受文件叠承托、K 已遮、林让位且轻理已开始未停；Shot03 接入右手轻理直到周提问才停。
4. 未证项：K 实际可辨时间和尺寸；演员视线与机位几何；纸叠对蓝夹的支承/落夹效果；轻理与周接近、第三句对白的时间关系。CLI 的 review-shot 是权威文本检索，不是自动连续性判定。

## 真实待审阅决策

本次没有有效“文字局部替换片段”需要用户签批。下一步先让用户决定：保留 B 文本并转向最小视觉/时间可读性观察（不自动运行 H3/GPU），还是即使尚无观看证据仍明确要求改变 Shot02 的具体一处导演选择；若后者，应先明确要改的是镜头任务、动作节奏、构图或跨切动作接口，才可据此形成可比较的新候选。

## 结果与权限

- 无画布写入，无生成，无 Runtime authority/approval 变更；未运行 prepare-stage/submit-stage/record-review/run-stage。
- 没有正式 Runtime 的新 pending B 候选，没有用户批准记录，没有改变 Script/Shot01–04。
- 与 WAR-90 所规定的“用户审阅先于修改/签批”的边界相符，维持 In Progress 的人机交互停点。

## 既有验证资料复用补充（ChatGPT 只读交叉核查，不是 Agent 本轮所读输入）

本轮正式 Canvas Agent 只读读取 Shot01–03 的批准 B 文本，**没有调用 WAR-72/WAR-90 已有 Blender 证据**；不能声称它已经独立分析过旧测试。完成本轮后，ChatGPT 又按需核对了：
- docs/planning/WAR-90/V0-evidence-reuse-and-V1-minimal-scope-20261115.md：旧 WAR-72 的 Shot02/03 镜头责任与新版四镜不等价；不可直接套用历史 Shot02→03 的镜头号和几何结论。
- docs/validation/WAR-90/light-v2/README.md：**确实已有**局部 CPU Blender 代理复检，修正过蓝夹落稳后林让位、周看到覆盖区域、K 不动、右前臂穿桌等问题；部分 11 点抽检与离散状态接缝通过，但仍**没有连续真人动作动画、观众观看判断或新版最终镜头视觉可读性的证明**。
- docs/planning/WAR-90/local-repair-v2/README.md：此前已经真实执行 Shot→Blocking→Shot 局部修订，最终候选 B 正是当前批准的 b7b4fd156b884907b2431b6b1e0d9960；轻理动作专为保持 Shot02→03 的“周问话实际打断”接口而补入，不是偶然多余动作。

故“没有几何证据”只能准确表述为“没有**足以确认新版最终 Shot02 视觉效果/动作时序**的完整证据”，不是说所有几何测试从未发生。原生 Agent R1 本轮没有提出新的文字改动，在已经进行过上述局部修订的背景下是合理保守的结果。若后续进入可读性测试，应按现有工作复用证据，不重新执行 WAR-72 或无限循环 Blender 几何搜索。

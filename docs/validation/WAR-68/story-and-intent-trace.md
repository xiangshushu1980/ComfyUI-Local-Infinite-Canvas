# WAR-69｜故事理解与导演意图：规则—输入输出追溯（C《没说出口》）

> 2026-11-12；Eric，Canvas Lab。**本报告是新做的只读证据分析，不是重新执行历史 LLM、完整 Toonflow 画布流程或媒体测试。** 研究的唯一详细正文在此；任务状态以 [WAR-69](https://linear.app/xiangshushu/issue/WAR-69) 为准，父研究方案见 [WAR-68](README.md)。不在本报告设计新 Skill、Agent 架构或工作流融合。

## 1. 问题、边界、证据等级

研究问题：从剧本事实与作者意图，经过故事解释、戏剧 Beat、可拍摄视觉命题到 Director's Book，究竟作出了什么**新的、可检验的创作决定**？哪些只是忠实转述，哪些是真正设计“观众何时知道什么、看哪里、感受什么”？对照 Toonflow 只问相应机制是否存在、何时生效；不以知识文件体积论高下。

证据类型：
- **[源规则/L0]**：固定源码规定应做什么，尚不是效果证据。
- **[模型补充/L1]**：旧模型回放输出的新增判断/数字/风格，不能反推为用户原意或源规则的唯一结果。
- **[观察/L1]**：可从冻结输入输出或 SHA 直接核对的文本事实。
- **[推断]**：对流程的解释，明确可证伪条件。
- **[未知]**：证据缺失或没做真实观众、表演、几何/媒体验证。用户已确认的剧本意图属于**源输入事实**，不算 Skill 创造。

环境：DirectorSKILL 固定上游 commit `c65ae0d14457053efb1e354c7e7f7e120d97fad1`，冻结 SKILL.md 标注 v2.1.0；历史 C 在隔离提示词中逐阶段运行，历史记录为 `gpt-6.1-terra` / Medium。Toonflow 固定上游 commit `6086cdffceb704a632eca143dd16cd461a78cdac`、工作流快照 v1.1.8（SKILL metadata v1.1.0），历史 C 同为隔离文本回放，`gpt-6.1-terra` / Medium。**并非对两份“完整部署运行”的能力比较。**

## 2. 最小冻结材料索引

项目根目录：`/home/sean/projects/canvas-lab`。下列相对路径均相对于该根目录。原样保留所有输入与输出；**未提取覆盖、重写或重新生成**历史文件。

### 2.1 原始剧本（两个实验相同）

- DirectorSKILL：`docs/validation/WAR-65/evidence/war-65-cd-original-execution-20261111.tar.gz` 的成员 `war-65-script-C/step2/script-C.txt`。
- Toonflow：`docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-C/script-C.txt`。
- 两份成员/文件逐字节 SHA-256 相同：`ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d`（1671 bytes，36 行）。
- **作者已确认的意图/约束就在剧本第 28–36 行**：两人关系亲近但不定义；陈想询问许会不会回来却没有问；许听懂但不正面回答；不哭、不吵、不拥抱；“过年的时候……”完整说到此处并主动停住；许走、陈不追；不新增背景或未来事实。类型标为“现实主义短剧情感片段”，非 Toonflow 十二类型中已确认的主类别。

### 2.2 DirectorSKILL 固定源码与 C 阶段

固定规则入口：`docs/validation/XIA-59-shotplan/upstream/director/SKILL.md`，SHA-256 `543be6ece626beaa7dbc36b8225dcdc0b763d8044563189e842b306bb5cfd792`；Beat 模板同目录 `beat-sheet-template.md`，SHA `e53e846e9f43cdc80cf261bde4978001628d6383a6d4bd702762f88131e04bda`。Director's Book 模板位于下述旧原始包的 `step5/director-book-template.md`（SHA `d6f0901207a822220fe87a7ca2feeea0ddeaf142a168a03704456e69b0ad68b0`），**不能错误地拼成扁平源码目录下不存在的文件**。

原始 C/D 证据总包：`docs/validation/WAR-65/evidence/war-65-cd-original-execution-20261111.tar.gz`；包级 SHA 与成员清单见 `docs/validation/WAR-65/evidence/README.md` 和 `war-65-cd-member-manifest.json`。下表成员路径均加前缀 `war-65-script-C/`，可以使用 `tar -xOf <包路径> <成员路径>` 只读检查。

| 阶段 | 冻结输入 / 输出成员 | 输出 SHA-256 | 本阶段可观察结论 |
| --- | --- | --- | --- |
| Step 2 Script/Subtext | `step2/step2-input.txt` → `step2/step2-output.txt` | `8c890ed9c80258fa9f148cc4f1180f461f0c826de966d7b9af251bc38d7dd0c0` | 戏剧问题、冲突、潜台词、情绪线；视觉命题是“并肩→距离拉开”；另给简要导演处理原则 |
| Step 3 Beat | `step3/step3-input.txt` → `step3/step3-output.txt` | `7a0ffb334a0d37eb9ef270f3167e4820f26caa153230bad958462a5442bdd041` | 5 个 Beat，各 6 秒，总 30 秒；压力差依次 +1/+1/+3/+1/+1；B3 是转折，B5 是余韵 |
| Step 4 Style Lens | `step5/step4-decision.txt` | `b1cad3fd7bde3e3b74ac70b498694c382e30150f837da52a706962f7f39a3ced` | 未指定导演，选 none；后续按 Drama 默认规则 |
| Step 5 Director's Book | `step5/step5-input.txt` → `step5/step5-output.txt` | `21187c2fc7c8bf45608f4d5c975c574b1173706429d9c6e2bb640df3f7e2027a` | 抄录核心/Beat/命题，增补 35/50/85mm、固定机位倾向、现实主义灯光、无配乐与表演禁忌等**拟定制作选择**；缺少可用人脸与世界光位锁定 |
| Step 6 Blocking | `step6/step6-output.txt` | `589b75e533f4c70d4dac01560611517dc1772193084ee4fee31cb2eee5f05bd3` | 落成暂定空间：“陈在许左侧、两人约 0.8m、检票口前方”；此几何为**模型拟定**，非剧本事实 |
| Step 7 Shot Plan | `step7/step7-output.txt` | `cec8e3e89ae509dec907dc061e830bb31e0db425651c3a8c919ae7cbd46d79da` | 7 镜 / 32 秒；第 7 镜共同空间中以两人分离距离表达告别；缺少实景拓扑，未证明纸面机位可拍 |

关键传递证据：`step3/step3-input.txt` 夹带完整原 Skill、Beat 模板、原剧本和前一阶段输出；`step5/step5-input.txt` 夹带完整规则、Director's Book 模板、参考章节、剧本、Step 2 与 Step 3；Step 6/7 的归档包含前序 Step 2/3/5 输出。可证明**文本被提供/有条件使用**，不能单凭这一点证明每个具体判断被真正采用。

### 2.3 Toonflow 固定源码与 C 阶段

版本入口：`docs/validation/WAR-59/toonflow-upstream-v118workflow/README.md`，其中含固定 commit、来源清单与 SHA；关联 `SKILL.md`、`references/knowledge/scriptCraft.md`、`references/knowledge/narrativeGenres.md`、`references/storySkeleton.md`、`references/episodeScript.md`、`references/directorPlan.md`、`references/knowledge/shotCraft.md`。

| 固定规则 | SHA-256 | 研究的局部章节 |
| --- | --- | --- |
| `SKILL.md` | `9d4a2cb89d1403187e883762b272d035b953894573f937b2e57d250b33b91928` | “主流程与确认关口”“知识如何随流程使用” |
| `references/knowledge/scriptCraft.md` | `e538088f8a1213f7f9b62127a1ff92bbb5d4adace93e251b8be512fe9236b103` | “事件判断与三种密度”“故事核、矛盾与结构”“信息差、钩子与反转”“单集情绪、动作与台词” |
| `references/knowledge/narrativeGenres.md` | `aa844ada5d04a7bf6dbd8575f3f96f1f2e0fcbad3d41a6d759716553de331a83` | “使用与落画布”“类型选择与复核模板”，仅将“家庭温情／青春成长／心理博弈”视为可能的比较对象，不擅自把 C 归入其中 |
| `references/directorPlan.md` | `a6fe68c1bb53d58f69cb3b5a398a414430b559c6a246ef53109f44ee0480e369` | “方法”“写入的成果”“回读与确认” |
| `references/knowledge/shotCraft.md` | `3567ca1ecb0e53522d7514ddb6240a488d28eb0794d7a2ee986aeebe6ec2bf3d` | “分场与表演依据”，不在此提前使用分镜章节 |

C 冻结文件基准目录：`docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-C/`：

| 文件 | SHA-256 | 作用 |
| --- | --- | --- |
| `script-C.txt` | `ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d` | 与 DirectorSKILL 完全相同的 C 输入 |
| `director-input.txt` | `505dd155183e375fdbe4aa4dade6f2d989d6cd47175f10b0be4804a1ae446545` | 实际提交的 Director Plan 阶段规则与上下文；并**非完整 Toonflow Skill** |
| `director-output.txt` | `6174646f605b39bcc48b3853a13daf039ecf66a68e4056ec5e0ad2d0d640366e` | 1 场，7 条/35 字台词，情绪浓度 4→6→4；表演、道具、声音、空间注意事项 |
| `storyboard-input.txt` | `c2af87accf6a6a6e8bab69f2c81ae7dffd12c8e3a78f70d6f367023e413bc981` | 原剧本 + 前一步规划 + 所选分镜规则 |
| `storyboard-output.txt` | `769adbb7277969b3b14682e18408169070e47a24a62977498fa5ab6829cb63ac` | 12 镜 / 4 片段 / 36 秒；未确认素材/画布/模型能力，独立标注风险 |

原始 `director-output.txt` 明确承认：实验没有提供对应 `narrativeGenres.md` 内容、叙事方法决策、创作决策节点、资产和画布。本研究新增阅读这些源码，不得**追溯说成历史模型已使用**它们。旧结果为单次 L1 文本表现。

## 3. 决策链可追溯矩阵（核心验收）

“消费”指规则规定的使用方式加可见 C 文本对应，非效果因果结论。若下游只有同义复述，必须单列为“保留但增量未知”。

| 创作问题 / 机制 | 源规则位置（规则类型） | C 输入 → 已有具体输出 | 下游如何消费 / 遗失 | 可检验增量假设与证据标签 |
| --- | --- | --- | --- | --- |
| **发生了什么／人物究竟想要什么？** | DS `SKILL.md`“Pipeline 2. Script and subtext breakdown”（顺序指令，L0） | 已确认“陈想问是否回来、许听懂” → Step 2 戏剧问题与内外冲突 | Step 3 B3/B4 继续叙述，Book `Story` 再次复述 | [观察/L1] 忠实理解；[推断] 与无需 Skill 的直接阅读相比，独立增量未证 |
| **未说的话和情绪如何推进？** | DS `SKILL.md` Step 2 的 `Subtext`、`Emotional movement`；Mode A 输出结构（L0） | 日常关切 + 停顿 → “未问出口的问题悬而未决”与四段情绪线 | Step 3 将其拆为 B1–B5；Book 又照录 | [观察/L1] 可追踪；[未知] 如果移除情绪分析，Beat 和镜头是否更差 |
| **观众该悬念什么？** | DS Step 2 `Dramatic question`；Beat 模板“last beat”、观众/角色分开计压力（L0） | “会不会问、许如何回应”；Step 3 数值将陈与观众**暂按同一条曲线** | Book 和镜头未建立逐镜“观众已知/未知”清单 | [推断] 戏剧问题已明确，但“观众何时能读出对话真正含义”没有独立证据；[未知] 观众实际理解 |
| **Beat 是否识别真实状态变化，而非对白分段？** | DS `beat-sheet-template.md`“Seven rules”“Pressure notation”“Self-check”（硬约束/L0） | 5 Beat；B3 压力 +3；B5 后果/余韵；各 6s | Book 沿用 0/6/12/18/24/30 秒；Step 7 变为 7 镜、32 秒 | [观察/L1] 确有意图与时长结构；[推断] B2 的“状态变化”弱，+1 为模型评分而非测量；[未知] 去掉 Beat 是否损失表达 |
| **如何将抽象主题变成可拍的视觉命题？** | DS Step 2 `Visual thesis` 要求 photographable/testable；Step 5 `Visual thesis` 应支配画面（L0） | “并肩→逐渐拉开的距离”，来自原剧本末尾分离事实，由模型选择为统一表达 | Book 第 28 行照录；Step 6 定走位；Step 7 第 7 镜保留共同空间/离开方向 | [观察/L1] 有从概念到空间/末镜的链条；[推断] 大部分镜头并未显式说明怎样服从“距离”命题；[未知] 此命题相对直接拍原剧本的实际增量 |
| **何种摄影视听风格保持一致？** | DS Step 5；`step5/director-book-template.md`“constraint document”“Story”“Lens…Sound”“never”“Invariants”（规范/L0） | Book 新增 35/50/85mm、固定优先、最多 1 镜重构图、2:1–3:1 拟定灯光、无配乐 | Step 7 均固定、借用焦段及光色政策；Book 暂拟 5 镜/ASL6，实际 7 镜/ASL4.57 | [模型补充/L1] 这些具体参数是选择，不是剧本原值；[观察/L1] 有部分执行及预算偏离；[未知] 是否改善观感/经济性 |
| **视觉约束可否真的复用？** | DS Step 5 `Invariants` 与模板世界坐标约束（L0） | Book 明确 `ID_CHEN/ID_XU/LIGHT_INVARIANT=n/a`；文本只锁得住地点、道具 | Step 6/7 如实保留部分待核，未伪装完整身份/光位 | [观察/L1] 正确认出缺口；[未知] 缺图时无法声称真正完成视觉一致性 |
| **Toonflow 怎样在编剧层设计观众知识？** | TF `scriptCraft.md`“信息差、钩子与反转”：事实／角色甲乙所知／观众所知／揭示位置；`episodeScript.md`、`storySkeleton.md` 的创作决定节点（L0） | C 剧本定稿且已有作者意图；旧回放**未使用完整知识和创作决策节点** | 完整流程按规则应将选定的信息/情绪决策传给 Director Plan/镜头 | [源规则/L0] 存在比“填情绪表”更明确的观众信息机制；[未知] 在 C 上是否会带来可见增量 |
| **类型方法能否决定叙事/观众感受？** | TF `narrativeGenres.md`“使用与落画布”“类型选择与复核模板”，要求确认主类型并记录采用的方法（L0） | C 只有“现实主义短剧情感片段”，未确认对应十二类型；旧阶段也缺少该文件 | 不应假定“家庭温情/青春成长/心理博弈”任一模板已生效；旧导演规划明确缺口 | [未知] 类型选择和方法落实均未在 C 被历史实验核验；“有知识文件”≠“实际使用知识” |
| **Toonflow Director Plan 究竟负责哪一层？** | TF `directorPlan.md`“方法”“写入的成果”；`shotCraft.md`“分场与表演依据”（L0） | 1 个 Sc1，7 句/35 字、情绪 4→6→4，停顿/视线/道具/广播注意事项 | `storyboard-output.txt` 把这类信息落实到 12 镜，但变成 36s，素材与空间仍待核 | [观察/L1] 传递可追踪；[推断] 不该拿此单独一步对等 DS Step 2/3/5 的组合；[未知] 完整上游 ScriptCraft 的增量 |
| **让观众“看什么”是事实还是决定？** | DS Rule 1 story function、Step 3 shot family；TF `shotCraft.md`“本镜给观众什么新信息”、`narrativeGenres.md`“观众新增信息”（L0） | 两方法都着重给“未说出口”留停顿和反应、结尾展示两人分开；DS 7 镜、TF 12 镜 | 其依据一部分来自原剧情，一部分来自模型选择景别与节奏 | [观察/L1] 有不同的表达组织；[未知] 何种切法更能让真实观众接收到想要的信息，没有观看实验或实际镜头 |

## 4. 沿 C 的最小有效决策链（源事实 ≠ 模型创作）

1. **原剧本事实**：陈想问是否回来但主动中止话语，许听懂但选择绕开，两人分离；这些已在作者约束中，不给任一 Skill 记“创造出潜台词”的分。
2. **DS Step 2 [模型补充]**：把“观众期待知道问题与回应”明确为戏剧问题；把距离拉开选为视觉命题。前者有认识上的组织增量；后者选择了一个视觉表达主轴，但该主轴也可由结尾动作自然推导，不能证明强创作。
3. **DS Step 3 [模型补充]**：把整场划 5 Beat，B3 暂定最强压力，画出单条陈/观众相同曲线。模板的“观众独立压力曲线”是源能力；本例**没有验证角色/观众视点差分是否必要或合理**。B1/B2 的状态差异很小，值得在下一任务请人审阅。
4. **DS Step 5 [模型补充]**：把剧情约束转为数值化政策，区分拟定和 n/a；但大部分光照、焦段、剪辑参数无法从原剧本事实推出，必须对实际下游作用与合理性分别验证。
5. **DS Step 6/7 [观察]**：末镜兑现空间拉开；5 Beat→7 Shot、30→32 秒，Book 暂定 5 镜与实际 7 镜不一致，文本输出**主动报告偏差**；35°机位关系只有纸面约束，没有真实拓扑或拍摄证据。
6. **TF Director Plan→Storyboard [观察]**：保住台词、停顿、回应、广播与离场；12 镜/36s。它本轮没有生成新的 ScriptCraft/类型选择判断；不可由“镜头数更多”判断其故事/导演能力优劣。

**重点分野 [推断]**：当前数据最能证明的是**事实保留与创作选择能被逐阶段追踪**，尚不能证明“创作选择造成了更好的观众体验”。“模型已读规则” “模型输出有栏目” “观众确实看懂/感到某情绪”是三个不同的事实等级。

## 5. 职责重叠、空白与未验证判断

### 5.1 重叠（不先判定为冗余）

- DS Step 2 的 Mode A 已含 Camera/Lens/Lighting/Editing/Sound 的初步“导演处理原则”，Step 5 又专门制定同类政策：**解释层先提方向、Book 后给具体约束**是可理解的分工，但“哪个阶段最终拥有决定权/是否需要改写”缺少独立验收。C Step 5 基本保留 Step 2 的克制、固定观察、停顿意图。
- DS 视觉命题在 Step 2 首次生成、Book `Story` 再写一遍：这是同一决定在下游携带，**不算两次独立创作**；应检验是否真的约束了其他镜头，而不只是被重复。
- TF `scriptCraft` 的情绪、信息、微动作与 `directorPlan` 的逐场情绪/表演有交集：正式设定是**编剧先明确创作决定，导演再落入可拍表演**。旧 C 缺先前节点，所以本轮不能检验正常交接是否重复劳动。

### 5.2 空白与风险

- **[未知] 观众信息**：原作者知道陈具体想问什么，不等于观众能仅靠“过年的时候……”明确推断为“是否回来”。需要分开记录**作者事实、角色认知、观众可见/可听线索、观众可能的解释**；本轮材料未做观众理解测试。
- **[未知] 情绪的独立表现证据**：Step 2/3 的“克制与压力”主要为文本判断；语速、停顿、演员表演和剪辑对观众感受的影响没有视频实测。
- **[观察/推断] Beat 自检与实际质量**：全部合格声明是模型自检，不是外部审核。B2 的状态变化量能否成立、B5 是否形成不同于人物的观众余韵，仍可被反驳。
- **[未知] 类型映射**：C 未选定 Toonflow 十二类型主类；示例中“青春/家庭/心理”仅供定位潜在机制，不应把其中任何情节模型强套进既有剧本。
- **[观察/未知] 视觉政策与实际可执行性**：Book 自认人脸、世界光源等约束缺失；Blocking 的 0.8m 和 Shot Plan 的约35°都属模型暂定，几何正确性尚未验证。
- **[观察] 计时/镜数漂移**：DS Book 5 镜/30s → Step 7 7 镜/32s；Toonflow 单场 → 12 镜/36s。不是自动错误，但必须区分“用户接受的偏差”和“模型自己生成的计划”，不能事后说已验证自然时长。
- **[未知] 因果归属**：两套旧回放的输入组织与加载规则范围不同；没有同模型同控制的删减实验、观众盲评或同脚本可比的视频，因此不能将差异归因于单个知识文件。

## 6. 可证伪假设与 WAR-70 交接（不是本轮执行授权）

| 假设 | 可做的最小对照 / 审阅 | 通过条件及反证 |
| --- | --- | --- |
| H1：DS `Script/Subtext` 给出超越原意复述的价值 | 对 C 每个结论反查剧本第 28–36 行，按“原文已有 / 合理解释 / 新导演决定”分类；和无需该阶段的同一模型解释对照 | 有独立正确且有用的下游判断才支持；只是改写作者说明则不支持 |
| H2：独立 Beat 能提高叙事压力与时间组织 | 审阅 B1/B2 是否有真正状态差异、B3/B5 是否承担不同工作；下游镜头逐项追溯 B 编号 | 删除或合并弱 Beat 导致真实信息/压力功能丢失才支持；不丢则可简化 |
| H3：单独的“观众知道/感觉/关注什么”判断比笼统情绪线更有效 | 固定 C 文本，先标 0–30s 中观众能从画面/对白得知的线索，检查关键时刻是否足以理解“没说出口”但不误认为剪掉台词 | 若出现误解/歧义且新增可检验线索约束能修复，支持；若已自然清晰则不必增环节 |
| H4：Book 政策真正限制镜头，而非后补格式 | 选 1 个易产生不同选择的 B3/B5 镜，逐字段核对 Book → Blocking/Shot：焦段、机位、节奏、末态、禁止项 | 重要字段有明确来源且能稳定限制不同输出才支持；无约束或频繁偏离则需重新判定价值 |
| H5：Toonflow 完整编剧/类型知识能改善 C 的观众信息布局 | 先明确是否适合/选择何种类型与创作边界，给完整 `scriptCraft` 与被选类型知识，再与旧未加载版本对照；明确新证据模型与输入 | 只有新决定与观众可见证据能够逐项映射且无加戏，才支持；文件存在本身不构成支持 |

这些是假设与审阅入口，不是已经安排的新 LLM 实验。新实验、单点修改和逐阶段用户讨论归 **WAR-70**；跨 D/E 反例及设计前结论归 **WAR-71**，均遵守父任务 WAR-68。旧 C 的原始数据一律不改。

## 7. 本轮验收判断

- **已完成 [观察]**：原始 C 输入跨两技能 SHA 一致；DS Step 2/3/4/5/6/7 与 TF Director Plan/Storyboard 的输入、输出、冻结位置、SHA 建立索引；按源规则、模型补充、观察、推断、未知分类；给出规则→输入→输出→下游消费→可证伪假设矩阵。
- **已完成 [判断]**：明确两套方法在故事层/导演层的实际职责与关键重叠；特别指出“作者意图已写入剧本”“TF 完整知识未参与 C 历史回放”“视觉命题有传递但增量未证”等三个易混淆点。
- **不属于本轮验收**：设计最终 Skill、做原始规则融合、选择 C 的唯一 Toonflow 类型、补造视频/资产证据、真实观众/演员/场景验证、替旧实验补做输入并冒充原证据。

报告限于静态源规则及单次已冻结回放，所述效果假设均需 WAR-70/71 的后续证据。
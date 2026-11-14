# WAR-89｜ViMax 专业知识与镜头执行机制提取 v0.1（独立稿）

> 日期：2026-11-14；[WAR-89](https://linear.app/xiangshushu/issue/WAR-89)。这是**第三套参考来源的独立提取稿**；不能把 ViMax 视作与 Toonflow / DirectorSKILL 同型的端到端导演知识库。本稿不修改原始代码、WAR-35 Schema，也不引入新的实验结果。

## 1. 依据、版本与证据限定

- **上游项目**：HKUDS/ViMax；Eric 冻结的 **3 份 Python 源码文件**位于 `docs/validation/XIA-59-shotplan/upstream/vimax/`。来源 URL、SHA 和字节数在 `docs/validation/XIA-59-shotplan/upstream/manifest.json`、`docs/validation/WAR-66/preflight-manifest.json`。
- **文件校验（本轮再计算）**：`storyboard_artist.py` SHA-256 `92c84362770d9123d80c5595cbf526c8d34288f69385a96e9e40c5450e83488e`；`camera_image_generator.py` `b3165016eb6942ebb3bfc3a4d93caad2b6d7700297642d6a2126a7c5e777c`；`script2video_pipeline.py` `682e1c2b6f726815ac4af34a09569af5309487ff48dbaf8c326305db68bf04e7`。以上与源清单一致，且未改源文件。
- **来源缺口**：该快照来自上游 `main` 的单文件来源，**没有固定到具体上游 Git commit**；三文件不代表完整仓库。当前快照中无可直接核验的 LICENSE，因此不推断其授权条款；独立改写专业方法，不复制大段原 Prompt。
- **已有实证**：`docs/validation/WAR-66/README.md`、`minimal-C-text-v1/REVIEW.md` 与 `minimal-C-independent-v1/REVIEW.md`；均为已有 C 三镜 Codex CLI 文本回放，**不是原版全链 Python Pipeline**；未执行真实 Camera Tree 图像参考/视频生成/空间几何校验。
- **证据等级**：下述“原 Prompt 规定”不等于“已独立证明”；“研究观察”仅指 WAR-66 冻结文本输出；“候选借鉴”不等于已集成自研 Skill。

## 2. 这套方法究竟解决什么

ViMax 主要有两类**相互独立的工作**：

1. **镜头专业表达**：`StoryboardArtist.design_storyboard` 将一场戏的剧本和角色表变成有叙事功能、景别、人物朝向、画面位置与动作的镜头候选；`decompose_visual_description` 将**已经设计好的单个 Shot**拆成静态首帧（FF）、中间运动（Motion）、静态尾帧（LF）。
2. **机位素材与参考关系**：`CameraImageGenerator.construct_camera_tree` 在多个机位间选择可能共享视觉内容的父机位/父镜头，推断哪些细节可延用、哪些需要额外参考。随后 Pipeline 可用父镜头首帧构造视觉迁移参考；这是素材生成策略，**不是空间真实性验证器**。

ViMax 也有 Storyboard Artist 的镜头选择规则，但它对 Intent、Beat 及 Blocking 的深度**远少于** DirectorSKILL 的明确阶段方法。我们不应该从其源码中的字段反推“它具备完整导演意图理解”。

## 3. 导演 Agent 可学习的方法（按实际创作问题提取）

| ID | 需要解决的专业问题 | 候选判断步骤／具体选择依据 | 应归入的阶段 | 原始依据／不继承的部分 |
| --- | --- | --- | --- | --- |
| VM-01 | 同一场戏该怎样分镜 | 从剧本中识别地点、事件、人物动作、对话、情绪节奏；对每镜先给明确叙事目的，如定场、关系、反应、信息揭示 | Shot Plan | `storyboard_artist.py::system_prompt_template_design_storyboard`；不把“单场景输入”当未来唯一合法剧本格式 |
| VM-02 | 镜头能否让观众找到角色和线索 | 在描述中明确人物画面左右、相对方向、主体部位、障碍物与环境的可见部分；不要描述镜内本来不可见的物体如同已经拍到 | Blocking→Shot | 同上；“可见”是表达要求，不证明真实摄像机几何或观众最终可辨性 |
| VM-03 | 为什么复用已有机位 | 比较新镜头的景别、角度、关注主体与旧机位是否真正不同；若无新增视觉收益可用已有机位与新表演完成，减少无意义切换 | Shot Plan | 同上；机位复用是节约复杂度的启发式，不为复用牺牲剧情视点 |
| VM-04 | 新机位是否服务戏剧 | 对需要新视点的镜头，先说明“新角度能让观众看到哪项原先看不到的信息”；否则保留同一场面的镜头关系 | Shot Plan | 同上；原 Prompt 规定大移动的机位不能后续再复用，属于其制作模型，不作通用电影规则 |
| VM-05 | 首帧应该写什么 | 将摄影机、人物初始位置/朝向/持物与环境、灯光、构图写成**时间点已经成立的静态快照**；不能用“即将起身”替代“坐着” | Shot→执行描述 | `storyboard_artist.py::system_prompt_template_decompose_visual_description` |
| VM-06 | Motion 应该怎么写 | 单独陈述人物移动、视线/姿态改变、镜头移动或灯光变化，写出动作**如何发生**，区分人物运动与摄影机运动，不能重复静态状态冒充运动 | Shot→执行描述 | 同上；动作是否实际生成属于媒体阶段 |
| VM-07 | 尾帧应该如何收束 | 由 FF + Motion 推出 LF，写清动作完成后的可观察位置、朝向、持物与构图；LF 不能继续写“正在开始”“正在走向”这样的未完成描述 | Shot→执行描述 / Review | 同上；需与原 Shot 的目标终态对照，不允许 LLM 擅自补做剧情 |
| VM-08 | FF/Motion/LF 如何避免越界 | 先比对输入 Shot 是否写明该动作；再逐项检查：FF 是否已提前发生？Motion 是否重复？LF 是否体现所有已完成变化？人物/物件是否凭空出现或消失？ | Review | `storyboard_artist.py` 分解 Prompt；WAR-66 独立回放提供反例 |
| VM-09 | 何时需要首尾帧而非只用首帧 | 按单镜内部构图/角色/主体变化幅度判断是否应额外明确结尾，尤其有不可逆动作或明显构图变化时要突出终点 | 执行适配 / Review | `storyboard_artist.py` 的 `variation_type`，`script2video_pipeline.py` 对 medium/large 生成尾帧；“small/medium/large”不是 Beat 的叙事重要度或 H3 能力测量 |
| VM-10 | 怎样选择视觉参考的父机位 | 首先看候选父机位镜头中是否包含子镜头所需人物、空间和视角；再看景别、信息重叠与时序相近程度 | Shot/参考规划 | `camera_image_generator.py::system_prompt_template_select_reference_camera`；这是相似/覆盖的文本判断，不是实测视线 |
| VM-11 | 父参考缺什么 | 逐项列出父镜头不能支持的额外信息，如角色新正脸、手部细节、未出现的道具角度；后续应补参考而非装作已覆盖 | 参考规划 / Review | 同上 `is_parent_fully_covers_child` 与 `missing_info`；LLM 给出的“全覆盖”不能替代像素检验 |
| VM-12 | 机位树怎样避免互相依赖 | 可选父镜头需存在，子机位不能依赖自己或形成环；优先让相似的广/中景成为局部参考来源，不必在每个 Shot 重新发明全场空间 | 工程／参考规划 | `camera_image_generator.py::construct_camera_tree`；索引/环校验是 Engine 任务，不占 Director Agent 创作注意 |
| VM-13 | 参考机位与全局状态有什么区别 | 不同时间的两个镜头即便同 `cam_idx`，人物与物件也可能变；先从 DirectorPlan 取得当时状态，再挑选能支持该状态的参考 | Blocking→Shot / Review | `script2video_pipeline.py::_group_shots_into_cameras` 与 WAR-66；树不管理跨镜时序状态 |
| VM-14 | 摄影画面不等于视觉事实 | 文本说父镜包含子镜角色，但可能缺正面、清楚细节、完整身体或可用遮挡；要告诉 Agent：可迁移的是什么、缺失的是什么、如何补证 | Review | `camera_image_generator.py` 的缺失信息；已有 Camera Tree 只证明字符串输出，不证明画面可行 |

### 应剥离的原项目约束

- **表格/字段**：`idx`、`cam_idx`、`ff_desc`、`lf_desc`、`ff_vis_char_idxs`、`variation_type` 等是接口与制作结构，不是 Director Agent 的哲学或专业判断本身。专业上只需理解“谁在镜头开始/结束时真实可见、动作是否跨时段成立”。
- **固定流程偏好**：“第一镜必须用最广定场”“尽量少机位”“每角色每镜最多一行对白”“运动后的机位不可再用”是原 Prompt 的策略或管线限制，不能作为适用于所有短片/H3 的硬性导演规则。
- **特定输出策略**：用人物服饰特征代替 Motion 内姓名、角色名包标签、JSON Schema 解析、Pydantic 重试、字符引用、帧事件与生成视频依赖树，主要属于制作翻译和工程控制，不应占用 Agent 的专业推理空间。
- **源模型安全措辞、敏感情节一律替换成非真实道具等**是原提示词处理方式，不是本次要继承的普遍叙事方法；实际内容政策和用户确定的剧情另行处理。
- **“镜头大小越近越好继承”**不是几何事实；正反打、转身、新增人物和视线变化都可能让特写缺失父镜关键像素。原 Camera Tree 的 parent 关系是参考建议而非物理包含证明。

## 4. 具体专业审核：每个 Shot 在 FF/Motion/LF 上如何自洽

把单镜简化为**原 Shot 设计目标 S → FF → Motion → LF**。对于每个真实出现在镜内的实体，要能够回答：

1. **源一致**：新描述有没有加入原 Shot 没有授权的决定（额外离场、无来源转身、增添对白/物件）？若有，作为候选提交给导演而不是默默变成已确认剧情。
2. **首帧静态**：FF 中人物朝向、持物手、面部朝向、所站位置是否是动作发生**以前**的状态？不能把稍后才发生的视线和站位提前画出来。
3. **运动时间序列**：Motion 从 FF 的真实状态开始；谁移动，谁保持不动，哪个时点说话、转头、递物、接物？摄影机的行动不能遮盖镜内必须清楚的变化。
4. **尾帧收束**：LF 必须体现 Motion 已经完成的全部变化，未完成的动作不得标为已经成功；如果 LF 没法说明，应返回 Shot/Blocking 明确终态。
5. **跨镜校验另做**：镜 A 的 LF → 镜 B 的 FF 由 DirectorPlan 的剧本、Blocking 和状态事实限定，不能假定 `Camera Tree` 自动保证。

**例：C《没说出口》**（说明性审阅，不修改既有冻结输出）：

- Shot 1 假定“陈手持车票，低头看票→抬头望向许→说出半句话并停住”。
- FF 适合写为“陈持票、目光仍落在票上”；Motion 写“抬头并短暂停住话语”；LF 写“陈仍持票，目光停在许的方向，句子已经中止”。
- 如果 FF 已写“正抬头/已经望许”，Motion 又写“抬头望许”，就是**时间点重复**。如果 Motion 自行增加“许离场”，但 LF 仍显示她停在原地，就是**越界 + 终态不一致**。
- 这不是重新决定应不应该切到许的反应镜；**切点和镜头功能仍由上游 Director Agent 选择**，ViMax 风格的拆解用于让选好的镜头更可执行。

## 5. Camera Tree 的参考价值与限制

| 关系 | ViMax 管理什么 | 它不证明什么 |
| --- | --- | --- |
| Parent camera / parent shot | 子机位倾向引用哪个更广／内容相关的父机位与该机位的某个 Shot | 两机位真实可站位、遵守交互轴与人的视线 |
| `is_parent_fully_covers_child` | 模型判断父画面能否覆盖子画面内容 | 细节具有足够像素、正反面真的相容、遮挡不存在 |
| `missing_info` | 需要附加的脸部、视点或物体外观信息 | 新参考已经被采集或某个图片生成结果最终正确 |
| Camera Tree 结构验证 | 索引、自己为父、环等确定性错误 | 叙事知情差、道具何时换手、人物何时走到哪里 |
| Render path | 原 Pipeline 可从父镜头的首帧出发生成视觉转场，再提取新机位参考；如有缺失还通过参考图选择/角色肖像补偿 | 实际生成成功、物理空间正确，或适合 H3 Ref2VA 的三实体输入约定 |

**源码复核注意**：`construct_camera_tree` 校验了父 Camera ID、父 Shot ID 存在与无环，但 Prompt 里的“第一个 Camera 是唯一根”“父镜全景覆盖真实子镜内容”等并没有在这段校验中变成完整的可计算几何保证。未来如果引入参考树，必须由 Engine 额外审查结构不变量，且仍需视觉证据。这里是可复核的代码边界观察，并非证明上游真实运行必有错误。


## 6. 既有 WAR-66 证据对照：已观察、未证明、未来可复检

| 原有冻结观察 | 对专业知识继承意味着什么 | 明确不推出什么 | 来源 |
| --- | --- | --- | --- |
| C 三个**研究者预先编写** Shot 都生成 FF/Motion/LF 的文本；Variation 三者均为 `small` | 原 Prompt 可在明确的单镜输入上执行拆解；Variation 是构图／内部改变的粗分类 | ViMax 已独立完成整个剧本的 Intent、Beat 或专业 Shot Plan；变化小就必然无需尾帧 | `WAR-66/minimal-C-text-v1/REVIEW.md` |
| 分开调用的 Shot 0 Motion 额外增加“许转向检票口”，LF 没完成该行为 | 单镜拆解需要检查**输入授权和尾帧结果**，才能阻止擅加剧情 | 分开调用普遍差于集中调用；额外行为在视频里必然发生 | `WAR-66/minimal-C-independent-v1/REVIEW.md` |
| Shot 1/2 分开调用时首帧已经存在运动开始以后才该出现的视线／朝向，Motion 再重复 | FF 必须先描述静态初态，Motion 不是把已经发生的变化再表演一次 | 共享上下文能百分百避免这种错误 | 同上 |
| Camera 0 为根、Camera 1 关联父镜头 0，且 `fully_covers=false`、缺少脸/手的近景信息 | `missing_info` 有助于指导补参考，而不是盲用父画面 | Camera Tree 已用图像证明父镜几何包含子镜；任何 H3 多镜一致性已经实现 | `WAR-66/minimal-C-text-v1/REVIEW.md` |
| 集中与分开调用均保留车票／背包／离场大状态 | 清楚的**单镜输入**本来已经携带不少事实，不能把保真全部归因于 Camera Tree | 三镜测试证明 ViMax 具有可靠跨镜状态账本，或证明调用方式优劣的因果关系 | `WAR-66/minimal-C-independent-v1/REVIEW.md` |

WAR-66 研究在 2026-11-11 已按缩减范围收口；**本次没有重跑 Codex、没有引入新模型试验**。

## 7. 与 Canvas Lab 当前导演目标的边界（候选，尚待三源交叉审阅）

| 能力问题 | 预计归属 | 不应从 ViMax 直接继承的假设 |
| --- | --- | --- |
| 故事/观众意图、Beat 状态、Blocking、决定何时切镜 | 自研 Director Agent 的专业导演阶段 | ViMax 单镜 FF/Motion/LF 能自动给出上游意图 |
| 单镜首尾状态、可见元素和运动描述 | Director Agent 需要理解其专业意义；未来独立执行投影／描述转换层可据此实现 | 现在必须在 WAR-35 增加 FF、LF 字段 |
| 单镜初态／运动／终态自洽核查 | 专业判断与确定性核查各司其职：Agent 判断内容意义，Engine 只检查可计算结构／已确定事实 | 三字段文本符合 JSON 就代表镜头可拍 |
| 跨镜人物、物件、位置与知情状态 | DirectorPlan / Blocking / Continuity 的权威状态和审阅机制 | Camera Tree 可替代跨镜状态账本 |
| 视觉参考之间的机位依赖与缺失补偿 | **将来**需要首尾帧／新机位参考素材时的制作策略候选 | 当前 H3 Ref2VA 三张实体参考必须先建立 Camera Tree |
| 真实空间视线、遮挡、文字可读性 | 后续 Canvas 审阅、必要时已有 Blender 几何验证或视觉媒体检验 | LLM 判断的“fully covers”就是空间验证成功 |

**最小可借鉴知识集**：VM-02（画面可见事实）、VM-05/06/07/08（FF/Motion/LF 自洽）、VM-10/11/14（参考内容与缺失信息的判断）、VM-13（时序状态独立于机位）为优先候选。Camera Tree 构建算法、视觉转场生成、角色肖像补偿、媒体调用属于**未来按需设计的实现机制**。

## 8. ViMax 来源处理清单与状态

- 现阶段只读提取了三个冻结 Python 文件的相关提示词与管线决策；**未获得带固定 commit 的完整上游源码树**，也未核对该版本许可证。后续若计划复制源代码实现或分发 Prompt 文本，应先补来源/许可核验。
- 本地引用的 WAR-66 综合研究与 C 三镜证据均已存在，不新建第二份实验数据，不改变历史冻结结果。
- **已阅读**：3/3 核心源码快照和 WAR-66 关键研究；**拟继承**：14 条专业/表达边界候选；**已编入自研 Skill**：否；**独立媒体实测有效**：否。
- **下一步**：让 Toonflow / DirectorSKILL / ViMax 三套**独立稿**分别接受来源与覆盖检查，然后**只比较方法上的重叠、冲突与缺口**，请用户做采纳取舍。不要在本篇预先合并三套、更不要以数据/工具字段名反向决定导演方法。

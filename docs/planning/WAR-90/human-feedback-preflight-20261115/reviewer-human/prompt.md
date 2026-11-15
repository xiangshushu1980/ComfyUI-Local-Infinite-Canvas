你是 WAR-90 的隔离独立审阅者。审阅的是尚未执行的『真人反馈采集测试方案』而不是现有 B 的专业质量、也不是生成导演候选。仅使用提供的冻结证据。绝不可自行创建用户修改意见，不得声称真人已审阅，不运行媒体/Canvas/工具、不修改文件。根据事实边界和测试目的做最小阻塞清单。必须区分 ①工程可证 ②专业待实测 ③真人必须提供的输入 ④WAR-37 正式 UI scope。指出具体证据片段与反例；输出 P0/P1/P2 及可执行的最小方案，禁止为测试扩展新 HTTP bridge。审阅报告控制在 500～1100 中文字。
专项:重点审阅：给人看的 Shot02 材料是否能让普通审阅者真正指出一条局部修改，不误把审阅目标写成测试答案；反馈来自 Chat 还是 Canvas UI 应如何标识；如果缺用户回复现在能做什么，哪些必须停。
=== FROZEN ===
## PROPOSED HUMAN TEST PLAN
# WAR-90｜真人反馈关口设计候选（尚未执行）
当前阶段：B 已批准后的真人 Shot02 修改意见采集预检，尚无用户新意见，也无生产 Canvas/媒体授权。
面向人的测试目的：让用户看清 Shot02 的『首次露钥匙→蓝夹再遮→整理动作持续→切 Shot03』，指出一个最需要改的表达问题；确认单一 Codex 可以将真实意见绑定 B/Source/Shot 版本后修订、复检邻镜、回显差异、停在真人 B 审阅，不自行批准。
拟定最小动作：
1. 不在已有真实 Canvas 上写入。可用现有隔离的 Canvas Agent 临时配置 + 专用持久浏览器 profile 搭建可见的独立测试画布；如果无法可靠保证浏览器/agent独立，退回 Chat 文本审阅，明确“未完成 Canvas UI 真人输入”。不改生产服务和全局 MCP。
2. 只展示 frozen review-pack 已批准四镜文本。用户选 Shot02 后，使用 Chat 提供**明确的实际修改意见**，作为 external-user-unverified 原文；不可把模型提出的修改建议自动算用户反馈。当前轮不预填任何反馈。
3. 真实意见之后复用已实现 feedback_bridge.py 的 make_catalog/check_catalog/capture_feedback/clone_for_revision/stage_scope，读回实际 Canvas projectId、selection、源 B/Shot SHA；若未选择或版本不一致，拒绝提交。不得写原批准 B。
4. 唯一专业 Codex 使用 director-skill-v0-candidate + Canvas MCP + Runtime CLI prepare-stage/submit-stage；如果需要修改 Beat/Blocking/Source，则上报停下，不硬做 Shot-only 修订。局部已提交后 Runtime 应复位新 B 并标记相邻镜头待复核；主流程组织独立 Reviewer/主审对新候选审阅，再给用户审 B。Reviewer 没有审批权。
5. 差异回显只用隔离测试画布的文本节点，不触发生成、不依赖正式 Canvas UI 写反馈，不增加临时 HTTP 桥接层；本轮至多准备“可给人看的目标和正式反馈输入点”，无真人意见就停在关口。
6. 每份报告显式写“当前阶段”和“给人看的测试目的”，并列出实测通过/未知/需要人操作。保存 SHA、原始对话文字、run ID 和安全边界。
拟验证：用户真实反馈的 provenance、Selection/B/Shot版本绑定、单Agent工具调用、实际差异与邻镜、主审阅接受范围、测试画布隔离。不可用 fake 结果冒充真实模型，也不能由自动化签署 B。
请主审判断是否需要先不搭建额外浏览器，而改为先将 Shot02 与相邻镜头在 Chat 中人可读展示，待用户给出反馈后再在隔离画布复现。请权衡是否存在不可消除的安全/真实性混淆。


## CURRENT FROZEN AUTHORITY
{
  "source_sha256": "65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d",
  "source_text": "# 《错过的钥匙》\n类型：现实主义短剧情\n目标时长：约 35–40 秒\n地点：一间小型办公室，傍晚\n人物：林（男，30多岁）、周（女，30岁左右）\n\n内景 · 办公室 · 傍晚\n\n办公室里，一张长桌靠着墙，门在桌子的另一侧。桌上有一叠文件、一个蓝色文件夹和一把银色钥匙。\n\n林站在桌前整理文件。周站在靠近门的位置，准备离开。\n\n周：「钥匙呢？」\n\n林：「刚才还在桌上。」\n\n林低头寻找。他把桌上的文件挪到一边，露出那把银色钥匙。\n\n周从门边向桌子走来。\n\n林没有注意到钥匙已经露出来。他拿起蓝色文件夹，放到那叠文件上，文件夹恰好挡住了钥匙。\n\n周走到桌旁，目光落在蓝色文件夹上。\n\n周：「你刚刚是不是盖住了什么？」\n\n林停下手里的动作。\n\n他移开蓝色文件夹，钥匙重新露出来。\n\n林看着钥匙，短暂沉默。\n\n林：「找到了。」\n\n周伸出右手。林拿起钥匙，将它交到周的右手中。\n\n周握住钥匙，转身朝门口走去。\n\n林留在桌边。\n\n【已确认的创作意图】\n这是一个关于注意力错位的小片段。\n- 观众应该先于林发现钥匙已经出现。\n- 林的整理动作无意间再次遮住钥匙，并非刻意隐藏。\n- 周发现异常，是因为她看到了文件夹遮住桌面的位置，而不是因为她已经看见钥匙。\n- 林重新发现钥匙后有一个短暂、略显尴尬的停顿；整体表演自然，不做夸张喜剧。\n- 钥匙始终只有一把，最终由林交给周。\n\n【空间与动作事实】\n- 桌上的钥匙起初被文件遮挡。\n- 林第一次挪开文件时，钥匙露出。\n- 蓝色文件夹随后遮住钥匙。\n- 林再次移开文件夹，钥匙重新露出。\n- 林拿起钥匙并交给周，周右手接过。\n- 周最终持钥匙朝门口离开，林留在桌边。\n不得新增钥匙、改变钥匙位置、安排额外的交接动作，或改变人物发现信息的顺序。\n\n【实验说明】创作意图属于确认的剧本资料，不是额外 Toonflow 导演规则；人物、环境与道具尚无真实图像资产。\n",
  "skill_sha256": {
    "skill/SKILL.md": "3eee7d6f3c3032fc43e97b86a9606f8ae77943fa377aa2f56e2770c2b76e8676",
    "skill/stages/intent.md": "ac07ecb95cbd511888911a0f85aa08f5fee2824cbf8e23749ef0d6ffec065a38",
    "skill/stages/beat.md": "6e81d45db1d0249cf33a200135f0ab790a49b65d92c7d036b0e253ac978121a1",
    "skill/stages/blocking.md": "2663d5acc282d636400539aecc643871c26c12867c5d480d9c02793ad45c5563",
    "skill/stages/shot-plan.md": "fa0c7d4cc39fdf6b5df9c8a0e3e9b0ee6eafa921142b5a5f07efcdc8cf989476",
    "skill/references/knowledge-index.md": "4d8edcb664659d78f897aa7baa8c1f275a57b5ff128ab433c95745b32a5e2519",
    "skill/references/review-method.md": "72b23f163fe1fdea6a547d5b47f39392ba0b9b63b814a7a285db4a7df0e88e8e"
  },
  "approved_A_id": "68d2717b905641d5a872550a896abcfc",
  "approved_A_content_sha256": "0160a83e8345f7b93957bc8dab2c0ec24bd3b21d5b2c2267d9964504af5f9d37",
  "approved_B_id": "b7b4fd156b884907b2431b6b1e0d9960",
  "approved_B_content_sha256": "64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7",
  "approval_evidence_sha256": {
    "A": "5fc92ce15dd12cedfa933666270c47793e99c9ced5a5e4ae7851d964fc83e032",
    "B": "7d7986b88e12451cfe0b06395fc2b2403fbf70d56c266a877bf214e2d3d15b1c"
  }
}

## APPROVED SHOT01-03
Shot01｜把寻找问题交给观众，并建立动作来源
观看任务：从门边准备离开的周与桌前整理文件的林，转向“桌上要找什么”；只建立寻找目标，不提前给出钥匙答案。
画面构造：桌外侧的斜向中全景，容纳林的脸、双手和桌面工作区，同时交代周在门边及门与桌的关系。靠墙长桌和傍晚办公室作为环境依据；不新增窗户、灯光事件或道具。前景桌沿提供稳定空间参照，不遮住整理动作；文件、蓝色文件夹可识别，K 被文件实际遮住。采用相对稳定的观看位置，不因人物问话进行强调性推拉。
人物眼线与知情：周看林，尚未接近、未见钥匙；林注意正在整理的文件，回答可朝交流方向短暂回应，但不确认 K。回答后林低头，目光跟随待提移的文件及其预定落点，而非先凝视钥匙位置。两人都未确认钥匙当前所在。
入镜、动作与出镜：从原有整理状态进入；周说“钥匙呢？”，林说“刚才还在桌上。”。随后林低头寻找，双手握住遮 K 的文件，开始提移。结束在纸叠已开始运动、K 仍未形成可辨钥匙轮廓的阶段。
切点与邻态：切至 Shot02 的依据是同一纸叠、同一双手的移动，不是在一个凝视 K 的面部特写后插入答案。Shot02 接续提移已经发生的阶段，不重做抓纸、低头或起提。此切点必须早于首次可辨显露，否则观众先知窗口会被切断。
声音与时间机会：两句原话完整、按顺序在本镜说出，不提前插入第三句。纸张接触声只可作为既有动作的自然声音，存在和强度未知。对白和开始寻找提供注意转向的机会；不规定秒数，不为等切镜增加停手。



Shot02｜先认出钥匙，理解无意再遮挡，再接上正在进行的整理
观看任务：观众从正在退开的纸边找到银色钥匙，短暂辨认其轮廓；沿同一 K 看清蓝夹落在已移纸叠上、伸出遮住钥匙的过程；遮挡完成后才将注意交给林自然让位及接续的轻理。镜头必须交付完整的显露与覆盖因果，并为 Shot03 的真实停手提供动作来源。
画面构造：沿 Shot01 同侧观察区转为斜俯桌面近景，高于桌面且偏离林、周实际眼位和视轴。以 K、纸叠落点、蓝夹取用区和承托边为画面核心；同一桌沿与林的躯干、袖臂提供身体归属。将纸叠外露边缘及右手从桌外返回该处的路径纳入画幅，给落夹后的侧后身位变化留出画缘余量，不能让手凭空从裁切外出现或用裁切隐藏穿桌问题。以相对稳定的画面承载全过程，不追随纸叠把 K 丢出画外；清晰范围同时支持钥匙轮廓、蓝夹覆盖边与文件叠支承，不靠浅焦抹去因果。若纳入接续动作会使钥匙过小，需重新审阅本镜取景条件，不能宣称已有辨认效果。
人物与身体位置：林保持首次显露时既有工作身位，躯干阻隔周到 K 的直视通道，同时为外部机位保留另一条通道。这是继承的工作姿态，不是林主动挡钥匙。林眼睛跟随纸叠及落点，再跟随文件夹对齐，不扫视、确认 K。首次显露后周才从门边起步，注意林和行进路径；她不是因看见钥匙而接近。周的低竞争身体运动可在画缘或背景承接，不能抢走钥匙首次辨认。近景不交付未拍到的面部反应，也不能以未拍周为未目击的证明。
同镜连续动作：接续 Shot01 已经启动的提移，不重做抓纸、低头或起提。纸边从仍遮 K，到局部退开，再到银色钥匙轮廓可辨；文件不拖带钥匙，纸叠落在可承托蓝夹的邻近位置。林松开文件，右手退出关键观察区并先收回桌外自然位置，左手转取蓝夹。左手把蓝夹移至纸叠上方，支承部分接触纸叠，伸出部分逐步遮 K；保留钥匙尚露、夹边接近、纸叠承托且 K 已遮住、左手松开这些中间态。不以只拍遮挡终态代替落放过程。
落夹后接续：只有蓝夹落稳、K 已被遮住且左手松开后，林才随整理自然小幅向侧后让位。首次显露期间不得提前让位。林不看周确认效果，不检查是否遮好，不演成故意隐藏或主动给线索。让位后左手保持空着；空右手从桌外安全路径接续轻理同一已移动文件叠的外露边缘，不穿桌、不扫过 K、不拿新物件，不推动纸叠整体、不改变蓝夹支承或造成再次遮挡。轻理是原整理的延续，不新增翻页、重复落夹或独立整理事件。
周的信息窗口：她只有在 K 已被蓝夹遮住、林落夹松手后让位时，才获得文件夹覆盖区域的观察通道。她看见蓝夹及其覆盖位置，没有见过首次露出的钥匙；不要求她目击蓝夹落放末段才成立。她从刚发生的整理与现有覆盖范围察觉异常的可信度仍待人审与观看证据。
观众首次辨认窗口：从纸边让出可辨轮廓开始，到蓝夹伸出部分重新遮去轮廓结束，由文件落稳、松手及转取蓝夹的自然动作提供阅读机会。侧后让位和接续轻理都在窗口关闭后发生，不挤入首次显露抢注意。不得以停手等待、慢动作、闪光、提示音或重复显露延长窗口。该镜属于外部细节观看；Shot01 的动作切、不同于人物的视轴、连续手部归属及林持续注意文件共同支持这一选择，仍不能保证观众不会误读为 POV。
切点与出态：在蓝夹由纸叠承托、K 已遮、左手已松、侧后让位完成、右手轻理已自然开始且仍进行中时切 Shot03。林左手空、右手空但正在接触轻理纸边，身体保持让位后的姿态；周处于门侧到桌边接近的末段，尚未见 K。选择这一次轻理中一个明确的运动方向和接触阶段跨切续接，不以轻理完成后的静帧切出，也不在下一镜重新启动轻理。文件叠落点、夹的伸出方向、K、人物姿态和周剩余接近阶段全部连续。
声音：无新增对白。纸张、落夹与轻理声音如存在，只随当次动作发生；切到 Shot03 时轻理声与动作阶段相接，不重放落夹声，不提前以第三句打断本镜。没有钥匙提示音或新增配乐事件。



Shot03｜周的疑问实际打断整理，林问后移夹并首次发现
观看任务：让观众看到周关注的只是已遮住 K 的文件夹覆盖位置；她的疑问打断林真实进行中的右手轻理，随后左手移夹引出林第一次确认钥匙及短暂尴尬。此镜结束于找到而尚未拿取，避免把发现和交付抢在同一时点。
画面构造：回到同侧斜向双人中景，容纳两人的脸、林双手、纸叠外露边缘、蓝夹与 K。前景桌沿与纸叠提供和 Shot02 相同的空间参照，背景保留周来路和门侧方向。为林让位后的实际身位和左手持夹终点留出空间，不把他摆回旧工作位置。周到桌旁时不挡住摄影机到 K 的观察通道；画面须能连接右手停止、左手揭夹与林目光落向 K。清晰范围不能只交付脸却丢掉停手和揭夹原因，也不能只见手却声称已交付尴尬表情。
入镜与跨切动作：从 Shot02 同一次轻理的正在进行阶段接入，续上同一方向、接触阶段与速度趋势，不补演让位、松夹或落夹。林左手已空、右手仍空而轻理未停，身体处于让位后姿态，注意仍在文件边缘；纸叠保持落点并承托蓝夹，K 仍在桌面原处被遮住。周续完接近的末段，到桌旁停下，保留以后伸右手和转身回门的空间。她的目光落到蓝夹覆盖部位，没有首次见钥匙后的会意、揭穿或责备表演。
对白与动作顺序：周说“你刚刚是不是盖住了什么？”。这句问话才打断林正在进行的右手轻理；不能让林在问句前已经完成动作，再以静止姿态冒充停手。林停下右手，随后看向她所问的文件夹位置，此时尚未发现钥匙，也不先演尴尬。右手停止后保持空着，留在桌外自然位置，不伸向 K。
林左手抓住蓝夹可取边缘，提离文件叠并移出 K，一次完成移夹，不拖动纸叠、碰钥匙或重复放下再拿。依次交代左手接触夹而 K 仍遮、夹边退出使 K 再次显露、夹完全让开且林目光落到钥匙并首次认出。左手将蓝夹持在身体一侧，避开他到 K 的视线、后续右手起取路径及周的接物区域。钥匙仍留桌面原位。
发现与第四句：林看着钥匙，短暂沉默，略显尴尬，随后说“找到了。”。沉默只发生在重新显露并认出之后，不提前到移夹之前，不扩大为喜剧反应段。周可在此次显露及回应中确认结果，不补一个独立惊讶事件，也不能倒推她此前已见过钥匙。左手持续持夹，林右手仍空；周尚未伸右手，林尚未前倾取物。
切点与出态：第四句完整结束之后、周伸右手之前切 Shot04。唯一钥匙仍由桌面 K 支承，文件叠保持原落点，蓝夹在林左手身体一侧；林右手空且未接触 K，身体没有启动取物前倾；周双手尚未接物，右手未伸出。Shot04 从完全相同的物件、手别、身位、视线和自然呼吸状态继续，不重演揭夹、认出、停顿或第四句，不在切点暗中拿起钥匙。
时间与声音：第三、第四句原话各一次，问句先于停手、移夹与发现，第四句在发现后的短暂停顿之后。持续轻理只自然承接至问句，不靠机械循环撑时间；若接近和对白需要反复轻理才成立，仍是本地时序的未解问题。移夹声如存在，只属于本次揭夹。短暂沉默是林未说话，不等于绝对静音；不用音效宣布笑点。



## REVIEW COLLAB RULES
# Canvas Lab｜分层独立审阅协作规则 v1

2026-11-15，用户确认。适用于 Canvas Lab 的方案、Skill、代码及导演产物审阅；**不改变实际用户 A/B 关口**。本文件是审阅组织规则，不是 DirectorPlan Schema 或生产 Agent API。由 ChatGPT 主流程组织，按任务情况将 Eric Codex 作为审阅执行端。

## 拓扑与模型预算

- **主流程（ChatGPT）**定义问题、权威事实、修改范围、证据和审阅验收；准备可独立核对的审阅包；最后接收主审阅 Agent 的结论、执行允许的下一步并向用户汇报。
- **主审阅 Agent**拥有本次审阅的汇总、争议裁定和最终建议责任。它须阅读原始证据以及 1–3 个 Reviewer 的原始报告；不能仅统计票数。可拒绝证据不足、过度保守、与冻结事实冲突或重复的意见；区分必须改、可以改、留待实测、不采用；将最终建议及尚存分歧交还主流程。主审阅 Agent 无权直接假冒用户批准。
- **1–3 个独立 Reviewer**在相互**隔离的新会话**中审同一冻结候选，但可分别侧重：①故事与来源事实／人物知情／声音时序，②专业导演表达与镜头可读性／替代代价，③工程契约／回归风险（只有需要时）。审阅人不互读意见、不能自行改冻结原文或生成物；每份结论指出证据位置、严重度、建议、验证边界与不确定性。
- 对简单/普通审阅，通常 **主审阅 Luna Medium + 2 个独立 Luna Low/Medium**（具体可动态取舍）；一个明显单点核查也可主审阅＋1 独立 Reviewer。只有涉及复杂依赖、Schema/框架、跨层一致性或重大互相矛盾证据时，才将**必要角色**升级至 Astra Medium/High，不自动全员升级。
- 按实际任务目标评估本次审阅需要何种证据，避免为了满足人数重复整套研究。审阅失败、模型不可用或使用额度不足时，必须说明实际完成几名，不能把主流程本人的检查虚构成独立 Agent。

## 执行规则与交付链

1. **冻结本次审阅目标**：指定源材料、候选版本/SHA、适用边界、问题分类。故事剧情、模型输出、纸面推断、实际生成画面和用户批准分别标记，不得混用。把失败判据与受测生成模型的输入隔离，避免将“正确答案”泄露给生成器。
2. **并行独立审阅**：每名 Reviewer 单独输入原始包与专项任务，在不同 Codex 临时会话中运行；记录模型、effort、prompt、输出及调用状态。禁止二者互看结论。
3. **主审阅综合**：主审阅 Agent 获取原始包、各份原始审阅以及必要完整生成物，独立核证主要事实。逐项判断是否可复现、来源是否充分、重大分歧如何处理。不能因为多名同意就自动判真；必要时回查一次原始证据，不无限递归开审阅 Agent。
4. **交回主流程**：输出短而明确的 `accept / targeted-revision / block / unknown` 判断与证据链接、需改文件/目标和未证风险。主流程负责决定是否实施候选局部修复、记录 Linear、Git 保存和用户汇报；重大来源事实与越权变更请求交用户。审阅结论**不能签署真实 A/B**。
5. **迭代标准**：一个明确 P0 故事硬冲突就阻断当前候选，但先归因（输入组包、Skill 路由、导演判断、运行时错误），不自动改通用 Prompt；稳定跨样本/重跑专业缺口才定向修 Skill；合理导演多解、媒体验证未知不作为 Prompt 失败。
6. **证据保存**：项目 Eric 本地 `docs/` 为唯一研究权威正文，线性任务只保存状态、路径与结论索引。审阅报告需能追溯原始输出、冻结 SHA、主审阅结论和实际接受/暂缓的建议，禁止覆盖原始证据。多 Agent 协作是**显式真实调用**，不能声称当前一个 Agent 的内部思路就是独立评审。

## WAR-90 当前应用

D《错过的钥匙》的 Intent 检查点 A：先由运行壳真实产生探索性 Intent，**不允许**提前自行批准或进入 Beat；独立审阅重点聚焦故事知情/悬念时序和表演策略/合理替代。主审阅 Agent 汇总后，ChatGPT 只给用户一个简洁 A 决策包。用户的接受/改动意见才可以经本地 pilot-only 记录为 A，并决定下一 Stage 是否继续。生产 WAR-35 正式批准须另做适配验证。

本规则是项目层协作偏好；任意阶段可因成本、工作复杂度或可靠性只做必要审阅，重大架构检查优先集中升级复杂角色，不让普遍审阅消耗 Astra 配额。


## PRIOR INTEGRATION EVIDENCE
# WAR-90｜单 Agent Director Skill + Runtime CLI + Canvas MCP 首轮真实联调

2026-11-15｜Eric｜当前状态：**单 Agent、已批准 B 的只读专业诊断/无交接闭环 PASS；真人 Canvas 反馈→真实局部修改→新 B 重审尚未验证，WAR-90 继续 In Progress。**

## 架构与输入

- **唯一专业 Agent**：Eric 独立新 Codex CLI 0.169.0、`gpt-6-astra` Medium；加载独立工作区 `.agents/skills/director-skill-v0-candidate`、阶段 `shot-plan.md` 与 `review-method.md`，对指定 Shot02 进行一次真实新模型判断；不是 Canvas Agent 内置 UI 对话线程的验证，也不是 Runtime 再启动第二个 Codex。
- **外部 CLI**：`tools/director-runtime-v0/cli.py prepare-stage / submit-stage`。同一 Codex 负责推理、结果写入，Runtime 不调用任何模型；旧 `run-stage` 保留回归路径。无新 HTTP bridge、无 Canvas 生产代码/API 修改。
- **画布工具**：通过同一 Codex 直接调用已有 `infinite-canvas` MCP 的 `canvas_get_state`、`canvas_get_selection`、`canvas_create_text_node`。Canvas MCP 本身内部代理现有 Canvas Agent，未新增桥接服务。
- **测试隔离**：原 Canvas Agent 仍有用户浏览器连接，原 smoke 程序因此拒绝操作。另起同一源码的隔离 Agent 实例（临时 HOME、17381 端口）及独立 Chromium profile，新建空测试项目 `jarkALjlasvWIMVq3t-2E`；原服务未改配置。测试脚本先创建 1 个 B 说明节点 + 4 个 Shot 文本节点，选中 Shot02。新专业 Agent 仅新增 1 个只读诊断节点，其余节点不改。
- **权威 B**：`docs/planning/WAR-90/pilot-D-local-repair-v2/state.json` SHA256 `23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7`；批准候选 `b7b4fd156b884907b2431b6b1e0d9960`、候选内容 SHA256 `64c08817a33fcebc2bad86c8c81b29b2297b4eab7de8bc7cb6db998823c6f4c7`，原 Source SHA256 `65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`。
- **单独试验工作区**：`docs/planning/WAR-90/pilot-D-canvas-single-agent-live-20261115/`，从批准 B 字节一致克隆。原批准 B 65 个文件比对无改动。

## Runtime 最小实现及确定性测试

仅修改 `tools/director-runtime-v0/` 下 `runtime.py`、`cli.py`、`README.md`、`tests/test_runtime.py`。新增两条命令：

1. `prepare-stage`：通过原 `packet()` 权威/审批/阶段/范围门禁与外部 Agent 专用 `external_packet()`，冻结只读 `input.txt`、输入 SHA、state SHA、run ID；不改 state。
2. `submit-stage --run-id`：仅接收本 run 下的 UTF-8 `result.txt`，复核准备状态、源/Skill/候选、冻结输入、状态变化和原阶段范围；与旧 `run-stage` 共享 `_apply_result()` 的结果解析与候选提交逻辑，不执行模型。过期、篡改、重复、非法镜头、冲突和坏格式隔离；A/B 不得由模型自签。非目标 Shot 逐字保护及邻镜 pending 规则延续。

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/director-runtime-v0/tests -q`：**54/54 PASS**，包含原有 37 项、16 个新增外部阶段测试及 1 个外部 Agent 工具策略隔离测试；`git diff --check` PASS。外部结果 provenance 为 `external-agent`，`identity_verified=false`，`model/thread_id=null`：CLI 不认证实际 Agent 身份。各文件原子写入但无跨文件事务；正式 WAR-35 typed schema/revision/CAS 尚不存在。

## 真实执行记录与证据

- 第一次独立 CLI 会话使用默认工具审批 `never`，`canvas_get_state`、`canvas_get_selection` 均被 `MCP tool call requires approval, but approval policy is never` 拦截。Agent 停止，无伪造结果、无新 run。原始只读失败记录保留 `agent-session.log` 与 `agent-summary.txt`。
- 仅对第二次独立会话使用 `--approve-for-me` 运行（不改全局审批设置），显式启用本次 `infinite-canvas` MCP。**MCP 真正返回**测试画布 ID、5 个节点和唯一 Shot02 选区。
- 相同 Codex 调用 `prepare-stage --stage shot --mode resume --targets Shot02`，生成 run `e3e4286019a24f76ac39fe27ddb9620f`，冻结输入 **81,307 B**、SHA256 `c97c0c3a53b3d2bb501a19210fa003e95c18a8606e8e46e40e618b8d689c5492`。Same Agent 读取 Source/阶段知识与已批准 A/B 后提交专业诊断。
- `submit-stage` 返回 **`no-handoff`**，结果 SHA256 `a86462d862fa0b9f2e42959e62321415d1e759774d1c617ec2dcabe9866b688a`。结果中 `handoff=false`、`changed_targets=[]`、`hard_conflicts=[]`，未创建新 `candidate.json`，测试克隆仍为 `phase=pilot-B-accepted`、B=原 ID、`pending_shots=[]`，仅增加 run 追溯。
- Canvas MCP 在再次读取测试画布后成功创建一个“WAR-90 单Agent导演只读诊断 · 非新B批准”文本节点，ID `text-1794753260894-0`，没有改写原节点；第二次模型会话的原始证据 `agent-approved-session.log`，摘要 `agent-approved-summary.txt`。最初设置 5 节点的测试脚本证据 `hold_canvas.py`、`canvas-agent-smoke-result.json`。
- 本轮结束后，独立浏览器已关闭，Canvas Agent 测试客户端数回归 0，临时 Agent 进程已关闭；原 Canvas Agent / Web 服务仍 active，正式画布未写入。
- 关键运行文件复制到 `evidence/external-run-e3e4286019a24f76ac39fe27ddb9620f/` 的 `input.txt`、`result.txt`、`metadata.json`；保留原工作区里的同名 run。具体 SHA 清单见 `evidence.sha256`。

## 专业结论与未验证

Shot02 已用文字安排首次钥匙辨认、再次遮挡、让位和轻理；但钥匙像素大小、注意竞争、假 POV、周是否提前看到钥匙均需视觉检查。Shot02→03 必须保持同一次轻理动作的运动阶段，让问句真正造成停手；静态姿势一致不代表动作连续。Shot03→04 文本上保留发现后的拿取与单次右手交接。未发现当前文本的确定硬冲突，**没有来自用户的新修改请求**，因此正确结果是不移交新候选。本次不验证真实用户 Canvas UI 的文字反馈、修改型候选、邻镜实际再审或真实 B 再批准；不验证几何、演出、视频与观众效果。未执行 GPU、Blender、ComfyUI、H3/媒体生成，也未修改正式 Canvas 或 WAR-35/52 契约。

## 下一关口

在**用户可见、明确授权且与正式画布隔离**的测试 Canvas 中收取一次真实的 Shot 修改意见，绑定最新已批准 B/Source/Shot 哈希；从 B 克隆独立工作区，用同一 Agent 执行 `prepare-stage → 真正局部 Shot/必要 Blocking 修订 → submit-stage`，核对差异和邻镜 pending，在画布显示候选，并停在真人 B 重审。不得将本轮 no-handoff 或旧合成反馈当作该关口完成。正式 UI 归 WAR-37，不抢跑生产实现。


## EXISTING FEEDBACK TRANSPORT
#!/usr/bin/env python3
"""Experimental WAR-90 Canvas selection -> Director revision handoff.

Transport-only pilot. NOT a WAR-35 schema, user identity proof, approval,
production Canvas integration, model operator, or media command.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/director-runtime-v0"))
from runtime import Pilot, PilotError, shot_sections, digest  # noqa

PILOT_ROOT = ROOT / "docs/planning/WAR-90"
ORIGINAL = PILOT_ROOT / "pilot-D-local-repair-v2"
PREVIEW_FORMAT = "war90-director-preview-only-v0"
FEEDBACK_FORMAT = "war90-canvas-feedback-pilot-v0"
CATALOG_FORMAT = "war90-canvas-shot-selection-v0"


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def approved_packet(workspace=ORIGINAL):
    """Read back approval each time; never trust a cached UI JSON as authority."""
    return Pilot(workspace).review_packet()


def make_catalog(packet, project_id, nodes):
    """Bind real Canvas node IDs to exact approved Shot versions."""
    if packet["format"] != PREVIEW_FORMAT:
        raise ValueError("Unrecognized preview transport")
    if not isinstance(project_id, str) or not project_id:
        raise ValueError("Missing Canvas project ID")
    if len(nodes) < len(packet["shots"]):
        raise ValueError("Not all Shot nodes were created")
    out = []
    seen = set()
    b = packet["authority"]
    for shot in packet["shots"]:
        title = f"WAR-90｜{shot['id']} · B Review"
        matches = [n for n in nodes if n.get("title") == title]
        if len(matches) != 1:
            raise ValueError(f"Missing/duplicate Canvas shot node: {shot['id']}")
        node = matches[0]
        if not node.get("id") or node["id"] in seen:
            raise ValueError("Duplicate or empty Canvas node IDs")
        seen.add(node["id"])
        # Canvas Agent GET_STATE compact transport truncates node content.
        # Match the prefix but NEVER use it as the authoritative Shot text.
        preview = str(node.get("metadata", {}).get("content", ""))
        if shot["id"] not in preview or b["approved_B_id"] not in preview:
            raise ValueError(f"Canvas review node has mismatched preview: {shot['id']}")
        out.append({"id":node["id"], "title":title, "shot_id":shot["id"],
                    "shot_text_sha256":shot["text_sha256"]})
    return {"format":CATALOG_FORMAT, "project_id":project_id,
            "approved_B_id":b["approved_B_id"],
            "approved_B_content_sha256":b["approved_B_content_sha256"],
            "source_sha256":b["source_sha256"], "nodes":out}


def check_catalog(packet, catalog):
    a = packet["authority"]
    for key in ("approved_B_id", "approved_B_content_sha256", "source_sha256"):
        if catalog.get(key) != a[key]:
            raise ValueError(f"Stale Canvas review catalog: {key}")
    if catalog.get("format") != CATALOG_FORMAT:
        raise ValueError("Unknown Canvas review catalog")
    expected = {s["id"]:s["text_sha256"] for s in packet["shots"]}
    entries = catalog.get("nodes")
    if not isinstance(entries, list) or len(entries) != len(expected):
        raise ValueError("Catalog missing/extra Shot nodes")
    if len({x["id"] for x in entries}) != len(expected):
        raise ValueError("Duplicate node ID")
    if set(x["shot_id"] for x in entries) != set(expected):
        raise ValueError("Wrong Shot membership")
    if any(expected[x["shot_id"]] != x["shot_text_sha256"] for x in entries):
        raise ValueError("Shot text changed while Canvas displayed an old version")


def capture_feedback(packet, catalog, canvas_state, selection, instruction,
                     origin="synthetic-test"):
    """Bind selected Canvas node and actual text, with NO forged human approval."""
    check_catalog(packet, catalog)
    if canvas_state.get("projectId") != catalog["project_id"]:
        raise ValueError("Selected Canvas project changed")
    if origin not in ("synthetic-test", "external-user-unverified"):
        raise ValueError("Unsupported feedback provenance")
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("Empty feedback")
    if len(instruction) > 12000:
        raise ValueError("Feedback exceeds pilot text limit")
    selected = selection.get("nodes", [])
    if len(selected) != 1:
        raise ValueError("Select exactly one Shot")
    node = selected[0]
    match = [n for n in catalog["nodes"] if n["id"] == node.get("id")]
    if len(match) != 1 or node.get("title") != match[0]["title"]:
        raise ValueError("Selection is not a bound Shot node")
    # The display may have been manually edited since the catalog was made.
    # The Agent read API truncates long node contents, but its prefix still
    # contains the immutable Shot/B labels of this experimental projection.
    preview = str(node.get("metadata", {}).get("content", ""))
    if match[0]["shot_id"] not in preview or catalog["approved_B_id"] not in preview:
        raise ValueError("Selected Shot display changed since catalog creation")
    a = packet["authority"]
    return {
        "format": FEEDBACK_FORMAT, "status": "revision-request-only",
        "pilot_only": True, "origin": origin,
        "actor_identity_verified": False, "human_B_decision": False,
        "canvas_project_id":catalog["project_id"],
        "canvas_node_id":node["id"],
        "target_shot_id":match[0]["shot_id"],
        "target_shot_sha256":match[0]["shot_text_sha256"],
        "base_B_id":a["approved_B_id"],
        "base_B_content_sha256":a["approved_B_content_sha256"],
        "source_sha256":a["source_sha256"],
        "instruction":instruction,
        "instruction_sha256":digest(instruction.encode("utf-8")),
        "requires_director_candidate_revision":True,
    }


def validate_feedback(packet, feedback):
    a = packet["authority"]
    if feedback.get("format") != FEEDBACK_FORMAT or feedback.get("pilot_only") is not True:
        raise ValueError("Not a pilot Canvas feedback envelope")
    checks = {"base_B_id":a["approved_B_id"],
              "base_B_content_sha256":a["approved_B_content_sha256"],
              "source_sha256":a["source_sha256"]}
    for key, val in checks.items():
        if feedback.get(key) != val:
            raise ValueError(f"Stale revision feedback: {key}")
    sha_by_shot={s["id"]:s["text_sha256"] for s in packet["shots"]}
    target=feedback.get("target_shot_id")
    if target not in sha_by_shot or sha_by_shot[target]!=feedback.get("target_shot_sha256"):
        raise ValueError("Unknown/stale target Shot")
    text=feedback.get("instruction")
    if not isinstance(text,str) or not text.strip() or digest(text.encode())!=feedback.get("instruction_sha256"):
        raise ValueError("Feedback text empty or changed")
    if feedback.get("human_B_decision") is not False:
        raise ValueError("Feedback is not a B approval")


def stage_scope(packet, feedback):
    validate_feedback(packet, feedback)
    a = packet["authority"]
    return (
        "WAR-90 Canvas selected-Shot local revision REQUEST, not a human B approval.\n"
        f"Approved B baseline: {a['approved_B_id']} content={a['approved_B_content_sha256']}.\n"
        f"Source SHA256: {a['source_sha256']}.\n"
        f"Target and only permitted modified Shot: {feedback['target_shot_id']}, "
        f"Shot text SHA256={feedback['target_shot_sha256']}.\n"
        f"User-edit instruction provenance: {feedback['origin']}; "
        f"identity_verified=false; new_B_approved=false.\n"
        f"Exact request text:\n{feedback['instruction']}\n"
        "Do not alter any non-target Shot. Preserve story facts, current approved Intent,"
        " Beat and Blocking, knowledge order, four dialogue lines, only one key, and final "
        "right-hand transfer. If the request needs Blocking/Beat or source changes, report "
        "the upstream requirement and DO NOT pretend the requested change is a valid "
        "Shot-only revision. Do not approve new B yourself. Report unresolved risks.\n"
    )


def clone_for_revision(packet, feedback, destination, source=ORIGINAL):
    """Prepare isolated workspace with exact approval SHA; no model call."""
    validate_feedback(packet, feedback)
    source = Path(source).resolve(strict=True)
    destination = Path(destination).absolute()
    if destination.exists():
        raise ValueError("Revision workspace already exists")
    if destination.parent.resolve() != PILOT_ROOT.resolve():
        raise ValueError("Revision workspace must be directly under WAR-90")
    if not destination.name.startswith("pilot-D-canvas-"):
        raise ValueError("Only explicitly named isolated pilot workspace allowed")
    orig_sha=sha_file(source/"state.json")
    actual=approved_packet(source)
    if actual["authority"] != packet["authority"]:
        raise ValueError("Approved baseline changed before clone")
    shutil.copytree(source,destination,symlinks=False)
    try:
        if sha_file(destination/"state.json") != orig_sha or sha_file(source/"state.json") != orig_sha:
            raise ValueError("Copied/current pilot changed during clone")
        Pilot(destination).check(Pilot(destination).load())
    except BaseException:
        shutil.rmtree(destination)
        raise
    return {"workspace":str(destination), "original_state_sha256":orig_sha,
            "state_sha256":sha_file(destination/"state.json"),
            "stage":"shot", "mode":"resume",
            "target":feedback["target_shot_id"],
            "scope":stage_scope(packet, feedback),
            "fresh_model_call_performed":False,
            "B_approval_recorded":False}


def compare_local_revision(packet, feedback, destination):
    """Read-only comparison of candidate after separate Director Resume call."""
    validate_feedback(packet,feedback)
    state=Pilot(destination).load()
    Pilot(destination).check(state)
    active=state.get("active")
    if not active or active["id"]==feedback["base_B_id"]:
        raise ValueError("No new local candidate")
    if active["stage"]!="shot" or state["phase"]!="awaiting-human-B":
        raise ValueError("Candidate must await real B review")
    if state.get("pilot_B") is not None:
        raise ValueError("New candidate was incorrectly approved")
    baseline=packet["stages"]["shot"]["text"]
    current=active["artifacts"]["shot"]["proposal"]
    ids=[shot["id"] for shot in packet["shots"]]
    old=shot_sections(baseline,ids)
    new=shot_sections(current,ids)
    changed=[i for i in ids if old[i]!=new[i]]
    if changed!=[feedback["target_shot_id"]]:
        raise ValueError(f"Changed content outside requested Shot: {changed}")
    t=feedback["target_shot_id"]
    diff="\n".join(difflib.unified_diff(old[t].splitlines(),new[t].splitlines(),
                                      fromfile=f"approved-B/{t}",tofile=f"candidate/{t}",
                                      lineterm=""))
    return {"format":"war90-canvas-diff-preview-v0",
            "base_B_id":feedback["base_B_id"],
            "base_B_content_sha256":feedback["base_B_content_sha256"],
            "candidate_id":active["id"],
            "candidate_content_sha256":active["content_sha256"],
            "changed_shots":changed,
            "pending_review_shots":state["pending_shots"],
            "diff":diff,"new_shot_text":new[t],
            "status":"awaiting-real-user-B-review",
            "pilot_B_approved":False,
            "formal_WAR35_approval":False,
            "media_verified":False}



# <issue id="f0b1756c-6a6e-4e47-b74d-5161d65c1c65" label="WAR-65" href="https://linear.app/xiangshushu/issue/WAR-65/研究directorskill-多剧本-beat-blocking-shot-plan只读观察" /> · 整理前完整正文快照

> **历史备份，不是最新执行指令。** 2026-11-09 按 Eric `/home/sean/.codex/skills/linear-task-collab/SKILL.md` 整理 <issue id="f0b1756c-6a6e-4e47-b74d-5161d65c1c65" label="WAR-65" href="https://linear.app/xiangshushu/issue/WAR-65/研究directorskill-多剧本-beat-blocking-shot-plan只读观察" /> 时，保存原 Issue 正文，以便检索旧阶段判断和证据路径。关联 Linear Documents 及原始实验文件保持不变；原 Issue 评论也未删除。

* 原任务：研究｜DirectorSKILL 多剧本 Beat → Blocking → Shot Plan（只读观察）
* 原任务 URL：[https://linear.app/xiangshushu/issue/WAR-65/研究directorskill-多剧本-beat-blocking-shot-plan只读观察](<https://linear.app/xiangshushu/issue/WAR-65/%E7%A0%94%E7%A9%B6directorskill-%E5%A4%9A%E5%89%A7%E6%9C%AC-beat-blocking-shot-plan%E5%8F%AA%E8%AF%BB%E8%A7%82%E5%AF%9F>)
* 整理前 `updatedAt`：2026-11-09T08:40:59.077Z
* 整理前状态：In Progress

---

## 目标

研究原始 **DirectorSKILL** 如何把已确认剧本转化为 **Beat Sheet → Blocking/Staging → Shot Plan**，透明观察其阶段职责、导演意图传递、镜头选择与连续性约束。延续 [WAR-61 · Toonflow C/D/E 文本研究](<https://linear.app/xiangshushu/issue/WAR-61>) 的人工参与方法，但**不强制套用 Toonflow 的输出结构**。

## 研究依据与样本

* 上游源码研究：[WAR-57 · Toonflow × DirectorSKILL × ViMax 规则对照](<https://linear.app/xiangshushu/issue/WAR-57>)。需要重新核对实际使用的原始版本、原始 Skill/引用文件与 SHA，尤其 `SKILL.md`、`beat-sheet-template.md`、`blocking-and-staging.md`、`shot-plan-template.md`、`continuity-bible.md`。
* 第一轮优先复用 <issue id="6ef12d52-b547-466e-ad01-23818f825f30" label="WAR-61" href="https://linear.app/xiangshushu/issue/WAR-61/%E7%A0%94%E7%A9%B6toonflow-%E5%A4%9A%E5%89%A7%E6%9C%AC-script-director-plan-storyboard%E5%8F%AA%E8%AF%BB%E8%A7%82%E5%AF%9F" /> 已确认的三个剧本：C《没说出口》（情绪和潜台词）、D《错过的钥匙》（空间和道具状态）、E《最后一张照片》（信息揭示和转折）。确保原剧本与创作意图不变；如 DirectorSKILL 要求额外输入，应如实标记缺口，不自行改写事实。
* 用户可以逐个决定是否增加同类复测或其他类型样本，不进行批量黑盒运行。

## 执行流程（逐阶段与用户讨论）

1. **只读核查原始 DirectorSKILL**：展示实际规则路径、内容、阶段路由、模型/调用条件，说明哪些是 Skill 明文规则、哪些是 Agent 自主解释；先和用户讨论技能原理。
2. **Beat Sheet**：执行第一个已确认剧本，展示完整原始输出；讨论 Beat 的状态转变/压力、创作意图和是否有自主增补。
3. **Blocking/Staging**：依据原剧本和冻结的上游输出执行，观察人物位置、眼线、动作、道具交接等；向用户展示结果和实际补充。
4. **Shot Plan**：观察每镜叙事功能、时长、切镜依据、表演细节与持续性；不以镜头更多/更复杂直接作为优劣。
5. 每个案例阶段性收口并保存原始输入/输出、规则版本、模型设置、日志与 SHA；出现实质问题先提出、与用户讨论后再决定复测或扩样。
6. 等其他 Skill（含未来 ViMax）研究完成后再综合分析，再决定是否引入“意图 + 细节描述”双层 Prompt、修改 Skill 或进行受控视频生成对照。

## 不做事项

* **不修改 DirectorSKILL、Toonflow、ViMax、Canvas、ComfyUI 或任何 Skill**；不构建优化版。
* **不运行 GPU、图片、H3 视频**；当前仅原始规则/源码与文本规划的隔离研究。
* 不默默将 Beat 视为 Shot 或把输出硬转换成另一 Skill 格式；不擅加故事、对白、关系、动作结局。
* 不擅自调整 Eric/Terry、G/default 或研究资料的存放布局；这部分由用户开启的独立 Skill 负责。

## 完成标准

* 至少 C/D/E 三类样本依次获得可复核的原始 Beat/Blocking/Shot Plan 证据，留存重要例外、错误与不确定性；不追求未经验证的胜率或成片效果结论。
* 能明确回答 DirectorSKILL 对比原生叙述和 Toonflow **额外组织了什么、改善点属规则还是模型决定、可能引入了哪些偏差**。
* 用户逐次确认后收口；最终形成与 <issue id="6ef12d52-b547-466e-ad01-23818f825f30" label="WAR-61" href="https://linear.app/xiangshushu/issue/WAR-61/%E7%A0%94%E7%A9%B6toonflow-%E5%A4%9A%E5%89%A7%E6%9C%AC-script-director-plan-storyboard%E5%8F%AA%E8%AF%BB%E8%A7%82%E5%AF%9F" /> 可对照的阶段观察结论，不提前开始跨 Skill 改造。

## 当前阶段：D《错过的钥匙》输入准备（2026-11-09；候选待确认）

* 用户确认继续 <issue id="f0b1756c-6a6e-4e47-b74d-5161d65c1c65" label="WAR-65" href="https://linear.app/xiangshushu/issue/WAR-65/%E7%A0%94%E7%A9%B6directorskill-%E5%A4%9A%E5%89%A7%E6%9C%AC-beat-blocking-shot-plan%E5%8F%AA%E8%AF%BB%E8%A7%82%E5%AF%9F" />，转入 D；并提出补充**简化人物外观与办公室/桌面空间约束**，重点更可靠地评价 Shot Plan 几何和 Risk 评估。建议保留 C 的无实体基线，为 D 采用独立标记 `D-assisted v1`，因剧本不同不得将 C/D 差异直接归因于额外实体。
* 已从 Terry 核查 <issue id="6ef12d52-b547-466e-ad01-23818f825f30" label="WAR-61" href="https://linear.app/xiangshushu/issue/WAR-61/%E7%A0%94%E7%A9%B6toonflow-%E5%A4%9A%E5%89%A7%E6%9C%AC-script-director-plan-storyboard%E5%8F%AA%E8%AF%BB%E8%A7%82%E5%AF%9F" /> 冻结原始剧本：`/home/ubuntu/research/xia-59/toonflow-20261107/xia-61-script-D/script-D.txt`，SHA256 `65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`。已确认故事事实包括靠墙长桌、门在另一侧、蓝文件夹、唯一银色钥匙、二次显露、周仅看见遮挡异常、周右手接过钥匙；不变更。
* 新建直属本 Issue 的 Linear Document：[WAR-65｜D《错过的钥匙》｜输入与简化实体提案](<https://linear.app/xiangshushu/document/war-65d%E9%94%99%E8%BF%87%E7%9A%84%E9%92%A5%E5%8C%99%E8%BE%93%E5%85%A5%E4%B8%8E%E7%AE%80%E5%8C%96%E5%AE%9E%E4%BD%93%E6%8F%90%E6%A1%88-671b0c898cce>)，包含已确认事实、**待确认**的两张文字人物外观卡、办公室平面布局、桌面钥匙固定点和文件/文件夹遮挡状态，以及风险观察和接力指引。资料卡是候选，不冒充原剧本或真正图片资产。
* 后续建议以**新对话**开始 D 的正式执行，先审阅并冻结候选资料卡和输入哈希，再按原始 DirectorSKILL Step 2→3→5→6→7 逐阶段执行，用户每阶段审阅。此刻**尚未启动 D 的模型执行、未创建图片、未做 GPU/H3、未修改 Skill**。新对话读取 <issue id="f0b1756c-6a6e-4e47-b74d-5161d65c1c65" label="WAR-65" href="https://linear.app/xiangshushu/issue/WAR-65/%E7%A0%94%E7%A9%B6directorskill-%E5%A4%9A%E5%89%A7%E6%9C%AC-beat-blocking-shot-plan%E5%8F%AA%E8%AF%BB%E8%A7%82%E5%AF%9F" /> 最新记录、D 资料卡和 Terry 原始剧本即可接手；Eric 仍为 Canvas Lab 主项目。

## 当前阶段：C《没说出口》· Step 7 Shot Plan 已完成（2026-11-09）

* **结果：固定原始 DirectorSKILL / Terry Codex** `gpt-6.1-terra` **Medium 文本回放成功，退出码0；在5 Beat的基础上自主生成**7镜／32秒／平均4.57秒（01 B1 7s，02 B2 5s，03/04 B3 3+4s，05/06 B4 4+3s，07 B5 6s）。七镜均使用固定机位；风险按原始六维量表评分为 **6 Green + 1 Amber**，所有七行15列齐备、算术已核对。
* \*\*核心观察：\*\*未机械照搬 Step 5 的临时五镜×六秒预算，而将 B3 的看票/停话及 B4 的回应/点头分别拆为两镜；但实际总长从30秒变32秒，ASL下降到4.57秒，**没有协调先前冻结的 Beat 时间与 Drama 默认6–15秒 ASL**。01/02 两位角色同镜先后发声却被评为 Green，可能漏算口型风险；35°机位变化、同轴线、光线方向仍缺场景实体证据。均为研究观察，不重写结果。
* **成果入口：**[本 Issue 所属 Linear Document · C《没说出口》阶段原始观察](<https://linear.app/xiangshushu/document/war-65c%E6%B2%A1%E8%AF%B4%E5%87%BA%E5%8F%A3directorskill-%E9%98%B6%E6%AE%B5%E5%8E%9F%E5%A7%8B%E8%A7%82%E5%AF%9F-867e19e5b191>) 已追加 Step 7 原始完整输出、研究分析、输入输出与日志 SHA。Terry 证据路径：`/home/ubuntu/research/xia-59/directorskill-20261109/war-65-script-C/step7/`。输出 SHA256 `cec8e3e89ae509dec907dc061e830bb31e0db425651c3a8c919ae7cbd46d79da`。
* \*\*停点／下一步：\*\*<issue id="f0b1756c-6a6e-4e47-b74d-5161d65c1c65" label="WAR-65" href="https://linear.app/xiangshushu/issue/WAR-65/%E7%A0%94%E7%A9%B6directorskill-%E5%A4%9A%E5%89%A7%E6%9C%AC-beat-blocking-shot-plan%E5%8F%AA%E8%AF%BB%E8%A7%82%E5%AF%9F" /> 保持 **In Progress**，C 样本 Step 2–7 文本阶段证据已具备；等待用户讨论 C 的 Beat→Blocking→Shot 结果及下一步选择（原 Skill 后续步骤、D/E 样本或实体对照），**不自行执行 Step 8 Keyframe、视频、GPU、不修订原始输入及输出**。此前讨论与阶段记录保留为历史记录。

## 当前推进记录（2026-11-09）

**最新进度：C《没说出口》Step 4–5（2026-11-09，待讨论）**

* 用户已审阅并接受 Step 3 的原始输出（此前疑点仍保留，不静默修正）。Step 4 无指定导演镜头，按 Skill 原始路由记为 `none`，直接进入 Step 5 Drama 默认。
* Step 5 **Director's Book / Mode C 已成功输出**，模型/环境沿用 Terry Codex CLI `gpt-6.1-terra` / medium / read-only，固定上游 `c65ae0d` 的原始文本回放；退出码 0，不是正式安装 Skill 全流程。
* \*\*结果摘要：\*\*暂拟 16:9、35/50/85mm、5 镜×6s（仅预算）、摄影机基本固定（至多 1 镜小幅重新构图）、2:1–3:1 柔和环境光、低饱和与无配乐。均为设计选择而非剧本事实。
* \*\*新疑点：\*\*暂拟 5 镜×6s 完全对齐 5 Beat×6s，可能固化机械时长；没有人物外貌/服装和真实灯光资料，`ID_CHEN`、`ID_XU`、`LIGHT_INVARIANT` 均诚实标为 n/a，尚不具备完整可复用不变量。导演风格限制较强，需在 Blocking 和 Shot Plan 检验。
* \*\*原始成果归属：\*\*已追加全部 Step 5 原文和证据 SHA 到本 Issue 的 [DirectorSKILL 阶段观察文档](<https://linear.app/xiangshushu/document/war-65c%E6%B2%A1%E8%AF%B4%E5%87%BA%E5%8F%A3directorskill-%E9%98%B6%E6%AE%B5%E5%8E%9F%E5%A7%8B%E8%A7%82%E5%AF%9F-867e19e5b191>)，原始输入/输出/日志在 Terry `/home/ubuntu/research/xia-59/directorskill-20261109/war-65-script-C/step5/`。
* \*\*待用户讨论后下一阶段：\*\*Step 6 Blocking/Staging；未启动后续 Shot Plan、GPU、图片或 H3。
* **执行选择：A，保留原始完整流程**。已完成 C《没说出口》Step 2 Script/Subtext 和 Step 3 Beat Sheet（Mode B），每阶段均通过 Terry Codex 进行**固定上游原文规则的隔离文本回放**，不是正式安装的 DirectorSKILL 全流程运行。模型 `gpt-6.1-terra` / medium；未跑 GPU、H3、Canvas。
* **Step 3 事实结果**：模型输出 5 Beat × 6s = 30s；张力 `2→3→4→7→8→9`；最大 `+3` 在 B3（陈说「过年的时候……」后停住），累计时长 18s；未发现明显新增事实/台词/道具。
* **待讨论的观察**：B1/B2 的状态变化较弱，可能只是对白分段；每 Beat 恰好 6s 缺乏独立时间论证；最后 B5 张力 +1，未体现“角色释放、观众收紧”的不同曲线（不一定构成违反规则）。原始输出**不作静默修改**。
* **资料入口（本 Issue 所属 Linear Document）**：[WAR-65｜C《没说出口》｜DirectorSKILL 阶段原始观察](<https://linear.app/xiangshushu/document/war-65c%E6%B2%A1%E8%AF%B4%E5%87%BA%E5%8F%A3directorskill-%E9%98%B6%E6%AE%B5%E5%8E%9F%E5%A7%8B%E8%A7%82%E5%AF%9F-867e19e5b191>)；包含完整原始 Step 2/3 输出、模型与规则 SHA、Terry 文件位置。完整调用输入、日志及原始文件保留在 Terry：`/home/ubuntu/research/xia-59/directorskill-20261109/war-65-script-C/`。
* **Step 3 已审阅**：用户认可原始 Beat Sheet，保留疑点，不重写输出；Step 4–5 已按本文上方最新进度执行。仍须逐阶段讨论，不自动串行。

## C《没说出口》· 最新结果：Step 6 Blocking（2026-11-09）

* **已成功完成**原始 DirectorSKILL Step 6 Blocking/Staging 文本回放：Terry Codex CLI 0.166.0 / `gpt-6.1-terra` / Medium / read-only / ephemeral，固定提交 `c65ae0d`，退出码 0。仍非正式安装版 Skill 自动执行；无 GPU、H3、Storyboard 或 Shot Plan。
* \*\*结果摘要：\*\*模型自行暂定「陈位于许左侧、间距约 0.8m、立柱在陈左侧、检票口位于两人朝向的前方」。B1–B4 站位不变，以许看向检票口、陈看车票再看许、许回头看陈的目光变化推动表演；B5 许朝检票口走去而陈原地不动，距离增大。道具始终保持「陈握一张车票、许背小包」。
* \*\*观察与风险：\*\*未提前完成镜头拆解，阶段边界清晰；坐标和 0.8m 是模型在缺场景资产下提出的暂定假设。B5 增加「陈目光朝许离开的方向」，源剧本并未明确；B2 将许凝视检票口持续至 B4，也为模型解释，均保留原文不修订。尚未核验真实空间、目光与拍摄几何。
* **完整原文和条件：**[WAR-65｜C《没说出口》｜DirectorSKILL 阶段原始观察](<https://linear.app/xiangshushu/document/war-65c%E6%B2%A1%E8%AF%B4%E5%87%BA%E5%8F%A3directorskill-%E9%98%B6%E6%AE%B5%E5%8E%9F%E5%A7%8B%E8%A7%82%E5%AF%9F-867e19e5b191>) 已追加 Step 6；Terry 原始证据目录 `/home/ubuntu/research/xia-59/directorskill-20261109/war-65-script-C/step6/`。输出 SHA256 `589b75e533f4c70d4dac01560611517dc1772193084ee4fee31cb2eee5f05bd3`，调用输入和日志同文档登记。
* \*\*待讨论/下一步：\*\*用户审阅 Step 6 后，按 A 流程执行 Step 7 Shot Plan；重点观察是否照搬五 Beat 五镜各 6 秒，能否产生叙事有效的镜头选择，及是否保持连续性。**不修订当前输出、不增添实体资料、不提前运行后续阶段。**

## 最近决定与下一步（2026-11-09）

* 用户明确：继续**忠实观察 DirectorSKILL 原始行为**，不修订已冻结的 Step 2/3/5 结果，也不修改 Skill；后续再增加样本测试。
* 本轮讨论的核心观察：Director's Book 的统一视觉规则与 Shot Plan 的逐镜设计应有边界；Step 5 暂拟五镜六秒、最多一镜移动，需观察是否约束过强。Beat→Shot 的专业选择与“独立高注意力导演 Agent”属于后续研究，不注入当前原始流程。
* **待决定**：是否、何时另设同剧本简化实体资料对照；当前先保留无实体输入基准，避免中途引入新自变量。
* **当前下一步**：已沿用冻结输入完成 C《没说出口》Step 6 Blocking/Staging；等待用户审阅后继续 Step 7 Shot Plan。关于以上主题的详细讨论记录见本 Issue 2026-11-09 评论及已关联文档。

## 执行入口

父任务：[WAR-59 · AI Director Skill 研究总览](<https://linear.app/xiangshushu/issue/WAR-59>)。
历史源码研究：[WAR-57](<https://linear.app/xiangshushu/issue/WAR-57>)；前序交互实验：[WAR-61](<https://linear.app/xiangshushu/issue/WAR-61>)。

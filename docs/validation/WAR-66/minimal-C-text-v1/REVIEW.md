# WAR-66｜C 三镜最小文本回放观察（2026-11-11）

## 性质、边界和原始证据

- **性质：ViMax 原始 Prompt 的 Codex CLI 隔离文本回放，不是原版完整 Python Pipeline，也不是 ViMax 自己产出的 Storyboard。** 三个 ShotBrief 的 visual_desc 由研究者按冻结剧本 C 编写，cam_idx 为 0,1,0；没有执行 StoryboardArtist.design_storyboard。
- 原剧本：`../c-original-v1/script-C-frozen.txt` SHA-256 `ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d`。
- 上游来源：`docs/validation/XIA-59-shotplan/upstream/vimax/storyboard_artist.py` 与 `camera_image_generator.py`，与之前 `preflight-manifest.json` 的 SHA 一致。
- 模型：Eric Codex CLI `0.166.0`, `gpt-6.1-terra`, `medium`, `--ephemeral --ignore-user-config --ignore-rules --sandbox read-only`。两次 Codex 进程均退出码 0；未生成任何图片/视频、未调用 GPU/H3。
- **适配差异必须保留：** 第一阶段为节省调用，把三个独立的原 Prompt 消息顺序装进一次 Codex 请求并施加研究用聚合 JSON Schema；因此虽然逐镜 SYSTEM/HUMAN 文本内容来自原版模板，却**不是三次隔离 LLM 请求**。第二阶段为单独一次 Camera Tree 请求。Code 的 PydanticOutputParser.format_instructions 由研究脚本生成的等价字段 JSON Schema 文字替代；Codex 前置说明及 response schema 约束是适配器而非上游内容。未调用上游 Python 的 Pydantic 验证与重试。无法由此推导原版真实运行的稳定性。
- 研究脚本：`../minimal_C_runner.py`；完整输入：`fixture-shots.json`、`decomposition-messages.json`、`decomposition-request.txt`、`camera-tree-messages.json`、`camera-tree-request.txt`；Schema、模型输出、JSONL、stderr、退出码见同目录，全部文件原始 SHA 见 `sha256-manifest.json`。

## 第一阶段：Shot Decomposition

三个输入均成功产出静态 FF、运动、静态 LF、可见角色索引及 variation 类型：

| Shot | 镜头目的 | 首帧 → 运动 → 尾帧 | Variation | 观察 |
| --- | --- | --- | --- | --- |
| 0 / Camera 0 | 双人建立镜头 | 并肩持票／背包 → 陈侧头叮嘱、许回答 → 陈朝许侧头 | small | 角色、持票与机位一致；口型与对白物理执行未证明 |
| 1 / Camera 1 | 陈看票、欲言又止 | 陈持票半侧面 → 看票、抬头、说“过年的时候……”后停住 → 仍持票望向许 | small | 未丢失主动停住及手中车票；实际动作时长和可见范围未知 |
| 2 / Camera 0 | 许告别离场 | 两人立柱旁 → 许回应、陈点头、许转身离开 → 两人距离拉开 | small | 宏观动作顺序完整，但人物从近到远走开仍标为 small，分类是否充分依赖镜头构图而非叙事变化，需注意 |

- 原 Prompt 要求 motion 以外观/服饰特征指人，不直接使用角色名。结果以「手持车票的男子」「背小包的女子」指代，形式上符合，但因为输入没有衣着特征，只能使用道具/外观有限特征。
- 三镜分解是**每镜内部**状态，不会自动执行 Shot 0→1→2 的全局道具、人物和空间连续性状态比较；任何跨镜一致性仅是原始候选输入带来的初始约束或模型自然延续。

## 第二阶段：Camera Tree

输出有两个 camera 节点：Camera 0 为根，无父节点；Camera 1 的 parent_camera = 0、parent_shot = 0、`is_parent_fully_covers_child=false`。模型认为父全景包含陈与车票，但**缺乏中近景所需脸部、手部细节，亦提到动作信息不全**。

- 结构与原 Prompt 的第一机位为根、尽量用宽景父节点、相近时间与覆盖信息相符；根节点、子节点无循环，parent_shot_idx=0 存在于父机位的 Shot 0/2 中。
- 原源码的结构验证检查父节点索引、父镜头存在和无循环；**覆盖程度与 missing_info 是 LLM 判断，不是图像/几何检验**。此最小测试未执行真实视觉参考或生成，不能推断空间一致性最终达成。
- Camera 0 有两个不同时间的 Shot（0、2），但 Camera Tree 并没有单独建人物位置/手持物的跨时间状态迁移，因此不能代替 Continuity Bible/Blocking。

## 与 Shot Plan／空间一致性的职责映射

| 方法 | 解决的问题 | 不解决的关键问题 |
| --- | --- | --- |
| Shot Plan / Beat / Blocking（DirectorSKILL） | 哪一刻切镜、机位/景别理由、人物站位、谁知道什么、道具与动作状态 | 不保证单镜首尾描述已可生成，也无法仅靠文字保证几何真实可行 |
| ViMax FF / Motion / LF | 单个镜头起点、运动与终点的视觉可生成描述 | 不自动维护跨镜的全局状态账本，不代替导演选镜 |
| ViMax Camera Tree | 不同机位/Shot 的参考依赖、父节点覆盖与缺失内容的文本判断 | 不保证物理摄像机位置、视线、遮挡，亦不校验跨镜动作/道具状态 |

**建议：** Canvas Lab 继续将 Shot Plan + 必要 Blocking/Continuity 作为上游；在后续需要独立首尾帧/关键帧或多机位一致性时借鉴 ViMax 的 FF/Motion/LF 和 Camera Tree。当前 H3 Ref2VA 多镜直出阶段，不应误把 Camera Tree 作为可替代空间状态约束的验证器。单次三镜文本回放足以观察 JSON 行为与明显边界，但不能比较三个项目导演质量，也不能预测 H3 成片效果。

## 待核与限制

1. 三个分解在一次模型请求中包装执行，可能存在互相感知上下文；**不能当成原版每镜独立 LLM 调用的严格复现**。
2. 只有单个剧本、三个人工镜头和两种机位；覆盖判断与 variation_type 的质量不能泛化。
3. 未测试素材生成、Camera Tree 真实引用、空间拓扑或动作遮挡；未评估真实生产链后续质量。
4. ViMax 上游快照具体 commit 未确定；使用的是冻结文件 SHA，不是锁定 upstream commit。

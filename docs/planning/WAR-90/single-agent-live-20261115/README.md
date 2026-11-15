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

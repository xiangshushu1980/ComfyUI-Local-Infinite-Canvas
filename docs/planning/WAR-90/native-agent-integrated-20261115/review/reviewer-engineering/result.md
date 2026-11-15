**结论：targeted-revision。** 可接受“隔离环境中的原生只读链路已实际运行”这一有限结论；不能扩展为审批隔离有效、完整 Skill 已读、修改闭环通过或生产可安装。本审阅仅依据冻结材料，未执行工具、修改文件或签署 A/B。

**P0｜进入修改或生产前阻塞：native approval 与工具隔离未证实**

- **证据定位：** HTTP endpoint 仅将 `permissionMode(req.body?.permissionMode)` 传入 `runCodexTurn`；没有提供其映射、实际 turn 的权限值、底层 approval/sandbox 配置或审批事件。`warning` 状态允许启动，也不能说明警告无害。
- **实际反证：** `temporary_mcp_overrides` 包含 Hindsight，但工具记录仍出现 `hindsight_search_pages: failed`。这证明发生了非必要调用尝试；失败不等于隔离成功。Codegraph warning 只证明加载相关异常，不能认定已调用。
- **最小行动：** 补同一 thread/turn 的有效配置来源、实际暴露工具及审批事件，解释隔离 HOME、Codex 配置目录、进程环境和 inherited MCP 的关系。验证拒绝审批后工具不执行。证据齐备前保持只读，不动生产全局配置；Skill 文字约束不能替代权限边界。

**P1｜原生执行已证，但证据层级需拆开**

| 项目 | 判定及证据 |
|---|---|
| 原生 Thread/turn 接受 | **accept**：最新 JSON 的 HTTP 200、busy 转换、`settled_turns=1`，结合实际工具活动；200 单独只证明接受请求。 |
| Skill 选择 | **accept**：listing 的绝对路径及 `private_skill_selected_in_turn=true`。 |
| Skill 实际读取 | **部分已证／其余 unknown**：`sed` 命令成功读取 `shot-plan.md` 和 `review-method.md`；展示输出截断，无法核对全部正文。没有入口 `SKILL.md` 的读取或注入明细，不能由 selector 成功推定七文件全部读过。 |
| Runtime 只读调用 | **accept**：`cli.py review-pack` 实际执行，退出码 0；后续提取 Shot02 成功。 |
| Canvas MCP | **摘要层 accept**：“读取画布”“读取选区”均 completed；精确工具名、参数及返回对应关系仍应补原始事件，不能仅依赖最终自述。 |
| Runtime 修改提交、生产安装 | **未发生，未验证**；不计入通过范围。 |

历史首次运行没有 busy/finished 观察及 settled 证据，不能与最新运行合并补成完整成功记录。现有工具摘要也缺少逐项 thread/turn/item 标识，建议补一份可关联的脱敏原始事件记录。

**P1｜哈希判断错误与输出截断应一起修正**

- **证据定位：** 哈希命令跨对象比较 `approved_B_content_sha256` 与 `stages.shot.text`；`sha_match` 表达式末尾还有 `and False`，结果恒假，完全不能充当校验。
- **判定：** 模型最终“正文可信度有限”的这项理由不成立，不应登记为 Authority 损坏。工程核对摘要报告 Stage 声明与实算一致、原 B state SHA 不变；本审阅未独立复算。
- **建议：** 优先设计现有 Runtime 的只读目标镜头 compact view，返回完整目标段、必要邻接依据，并为各哈希明确对象、算法及序列化范围；同时修正原 Skill 的比较规程。仅修措辞不足以消除大 JSON 截断、猜错 `shot_plan` 键和落盘绕路。不得复制一套导演 Skill。

**P1｜Skill 迁移与可靠停止仍为 unknown**

- **路径迁移：** 两轮 Skill 都位于不同 `/tmp/.../site/.agents/skills/`。发现成功不能证明候选副本与规范源一致。最小补件是七文件来源及内容摘要清单、相对引用校验、更新替换方式与回退版本；正式安装继续另行审阅。
- **停止与失败：** endpoint 使用 `void runCodexTurn(...)` 后立即返回。外层 `catch` 不能覆盖该 Promise 后续拒绝；内部是否保证 `onFinish`、释放 client、清理 busy 和附件，材料未提供。
- **最小行动：** 补审批拒绝、取消、超时及异步失败的终止证据，确认没有遗留执行、客户端占用或写入。删除临时 JSON 不等于 Runtime 修改失败回滚；后者尚未测试，应延期到有具体修改授权时验证。

**P2｜收口表述**

本轮应称为“业务数据只读测试，发生临时文件写入及一次非必要 MCP 调用失败”。`/tmp/war90-review-pack.json` 已删除目前只有核对摘要，画布五节点与 B SHA 不变也不能单独证明所有生产文件均未触碰。

建议继续沿用**同一 Canvas Agent＋原 Skill＋现有 Runtime CLI**，先补权限与原始事件证据，再审 compact view 方案。无需新增导演 Agent、HTTP bridge；当前没有 Shot02 修改意见，停在只读审阅边界。
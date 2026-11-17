# WAR-35 · 阶段 A RC3｜Astra 独立复核记录（2026-11-17）

## 输入、身份和结论

- 审阅执行端：Eric Codex gpt-6-astra / High，接续原独立审阅会话 01a1d800-6e86-7e52-80b1-e245aefe96f2，sandbox=read-only。
- 审阅固定 Git 候选：0ed1388a8bef597ac6547485179b437ca9735471，比较基线 edcbd82b269c86ce03e7dc746a47b430ed826bcf。
- **结论：阶段 A Not Accepted。** 原 RC2 的 media-v1 改报 text、fact-local/1 指向 Subject 两项反例已关闭；发现媒体 SHA 格式非法仍能产出可复用的局部依赖指纹。阶段 B 未启动，WAR-35 整体 Not ready。
- 本记录由 ChatGPT 主流程根据真实只读 Astra 会话的输出整理，不冒充审阅 Agent 自行写入的原始报告。原始会话可从 Eric Codex 会话 ID 检索。

## 独立复核事实

1. 内存 Git archive 单独读取固定版本，旧 RC2 为 50/63、RC3 公共 63/63、RC3 扩展 74/74；D-JCS 14/14、来源证明 24/24、Decision 37/37、阶段 A 10/10。
2. 独立枚举 8 个 CheckSpec × 4 个 method × 11 个已有 typed target，共 352 种组合：允许 19 种，不允许的 333 种均拒绝；另 88 个混合目标组合符合注册约束。
3. 对直接 Source、Constraint、Fact 闭包进行正反例验证：缺失来源、伪造或重复快照无法承接；真实来源变更使摘要改变；稳定来源允许承接。旧 /3 Check、inheritance 和改贴 /4 的旧摘要无法通过当前 Gate 承接。
4. 两份 P/D Golden 的 canonical payload 由独立 Node JCS 复核与候选一致。

## 新增阻塞：媒体 SHA 的尾部换行

合法 media-v1 的 executionTarget.projectionContentSha256 设为 64 个小写十六进制字符后追加换行，原始 JSON 通过 I-JSON 入口后，包含 pass/valid Check 的完整 RC3 Package 仍能通过 Python Draft 2020-12 Schema 校验；两个不同 Plan revision 均得到相同 /4 D 摘要：8415dfc8a8436cd8cd0085077cbee294860eeaf3b08ed27433eeeb0a7bf0656a。evidenceBindings 中可选 conditionSha256 同样存在尾换行接受问题。根因是 Schema 的正则结尾 $ 在 Python 中可于尾换行前匹配，以及研究计算器未对上述两个字段进行严格整串校验。

**没有证据表明此反例能够冒充完整 Intent A Gate 的批准。** 此阻塞限定在阶段 A 的局部媒体 Check 指纹有效性。

## 定向修复与边界

- 对媒体投影 SHA、证据内容 SHA、可选条件 SHA 全部严格匹配 [0-9a-f]{64}，不得允许尾换行；共享 Schema 的 hash 增加精确 64 字符长度要求。
- 合法媒体绑定仍可出计算型指纹；不据此宣称已校验真实媒体 bytes。
- 原始输入必须先通过 raw I-JSON 与完整 Package Schema，之后才能运行 Check/Gate。单独调用研究 Gate 不等于完整生产校验。
- 定向修复后重新独立验收阶段 A，未验收前不得开始阶段 B 或冻结公共 Schema。

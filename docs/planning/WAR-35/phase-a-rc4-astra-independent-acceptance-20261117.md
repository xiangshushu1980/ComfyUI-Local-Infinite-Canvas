# WAR-35 · 阶段 A RC4｜原 Astra 独立验收（2026-11-17）

## 判定

**阶段 A：Accepted。** 固定候选 Git 0dcdadf1237e6f0442e17684637d22da8488269c 已满足先前 RC3 审阅列出的局部媒体 SHA 阻塞收口标准。**WAR-35 整体仍 Not ready；阶段 B 尚未启动。**

审阅由 Eric Codex gpt-6-astra（medium）接续原独立审核会话 01a1d800-6e86-7e52-80b1-e245aefe96f2 执行，sandbox=read-only。原始提交前版为 0ed1388a8bef597ac6547485179b437ca9735471。此文由 ChatGPT 主流程依真实 Codex 独立输出整理，并非伪装成 Astra 自己写入的报告。审阅只读 Git 对象的内存副本，不改仓库、Linear、WAR-52、生产代码，不运行 GPU/H3。

## 独立反例和验证

1. 三种媒体 SHA 字段各取 10 个恶意值，共 **30 个反例**，包括 LF/CRLF、63/65 位、等长大写、非十六进制、全角字符、NUL、null；从原始 JSON 字节进入后，RC4 全部被整包 Schema 拒绝，直接 D-JCS 计算均返回 None。RC3 的末尾 LF 反例在相同环境仍能复现原缺陷：投影和条件 SHA 可生成合法格式的指纹。
2. 合法小写媒体 SHA 均获接受；省略可选 conditionSha256 仍合法；改变任一有效媒体摘要都会改变依赖指纹。media-v1 改报 text、fact-local/1 指向 Subject 不得产生指纹。
3. 真实研究 Gate 对未变的来源允许安全承接，对缺失快照、原文篡改和 Fact 断链均拒绝。该判定不等于验证完整生产批准流程。
4. 分别从两份候选示例独立构造 P/D canonical payload 并用 Node JCS 复算，RC3/RC4 P/D Golden 逐项相同。RC4 Schema ID 已独立为 urn:canvas-lab:director-plan:0.1.0-rc4。
5. **未发布的 RC3→RC4 可以保留 D-JCS /4 规则**：合法输入的 canonical bytes 与 SHA 未变，仅收窄非法输入的接受域。对任何 RC3 既存声明都要依 RC4 重新计算/验证，不得只看相同的 Profile 标签。

## 验收边界与交接

- 仅确认阶段 A：局部 CheckSpec、依赖闭包、来源证据与媒体 SHA 格式的研究性边界。真实媒体 bytes resolver 及执行目标对应关系未验证，不可称媒体检验通过。
- 阶段 B 仍须单独建立并验收 A/B Gate 的必审成员、最低检查覆盖、适用风险发现与 Decision 替代、有效批准作用域、可信直接父版本；raw I-JSON → canonical → 再读回的接受域封闭性也须在正式冻结前收口。
- 旧 RC1、RC2、RC3 证据和未冻结 RC4 候选保留；**不得把阶段 A Accepted 当作公共 Schema 冻结、生产执行授权或真实用户审阅 A/B 已批准。**
- 下一步在 WAR-35 内按原冻结复核阻塞清单启动阶段 B 的最小 Gate/风险/Revision 设计与独立测试。

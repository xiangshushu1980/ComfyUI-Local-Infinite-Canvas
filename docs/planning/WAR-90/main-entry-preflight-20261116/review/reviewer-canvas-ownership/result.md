## 结论

**targeted-revision**。当前材料可支持“主入口安装前准备”的有限结论。Chat 写入与生产权限验收维持 **block**，真实 HTTP 路由及 MCP 拒执行能力为 **unknown**。

仅依据本消息冻结材料与源码片段审阅，未调用工具、未执行复现、未批准 A/B。

- **原生 Codex `skills/list` 已通过**临时七文件包发现、刷新与回退，manifest 记录七份 SHA 恢复。
- **本轮 Canvas Agent HTTP 路径未测通**。此前隔离 API 读写结果不能覆盖本轮候选与正式配置。
- **生产安装未发生**，正式服务未启动。84 项单元测试与 13 项离线 gate 测试均不能替代生产路由和权限验收。

## P1 问题

### 1. Node 与 Shot 缺少关联验证，成功结果扩大了实际证明范围

**证据**

`verify()` 分别验证 Canvas 中的 `node_id` 和 Runtime 中的 `expected_shot_id`，没有验证二者之间的映射。`selection` 也仅比较节点 ID，未携带或核对 client/project/version。

**可复现输入**

在有效 fixture 中，把 Canvas 节点及选区换为另一个合法节点 N2，并将参数 `node_id` 同步改成 N2。保留原 Shot S1、B 与 SHA。只要其他字段匹配，函数仍返回 `read_context_verified=True`，即使 N2 展示的是 S2。

**最低修改**

将成功语义明确收窄为“所提供身份字段分别匹配”，并在 `not_verified` 中加入 Node→Shot 映射与 selection 的 client/project 归属。若继续宣称完整上下文匹配，则必须取得并校验可信映射及读取来源信息。WAR-90 可以先收窄声明，无需扩建 schema。

### 2. B 与 SHA 允许缺失值相等后通过

**证据**

仅 project/client/node/shot 参数检查非空。以下比较允许两侧均为 `None`：

```python
authority.get('authority', {}).get('approved_B_id') == approved_b_id
authority.get('source', {}).get('sha256') == source_sha256
target.get('text_sha256') == shot_sha256
```

**可复现输入**

使用其余字段有效的输入，删除 authority 中对应 B、source SHA、Shot SHA，将三个预期参数设为 `None`。保留目标 Shot ID、非空 text 及要求的 capability 字段。上述校验全部通过。

**最低修改**

比较前校验 B ID 为非空有效标识，两个 SHA 为合法的 64 位十六进制字符串。增加缺失值、空值和非法格式回归用例。若 `text_sha256` 被用于证明返回全文的完整性，还需对返回 `text` 重新计算摘要并核对。

### 3. “新近快照”和单客户端检查无法证明同一次读取上下文

**证据**

函数没有时间、快照 revision 或统一读取标识。`health`、`state`、`selection`、`authority` 都是调用方传入的独立对象。

**可复现时序**

1. 保存客户端 C1、项目 P1 的有效数据。
2. C1 切换项目，或另一标签连接并激活。
3. 将保存的数据再次传给 `verify()`。

返回结果仍为成功。该问题同样影响只读结果归属，即使始终保持 `can_write=False`。

**最低修改**

删除函数能够验证“新近”的表述，明确它只验证输入数据内部的部分一致性。将读取时间、来源关联和跨请求一致性列为未验证项。调用规程可以要求立即重读，但其竞态限制仍需保留。

### 4. Chat HTTP 写入缺少请求级目标约束，人工确认无法消除路由竞态

**证据**

`/api/tools` 仅传入工具名和 input。目标由共享的：

```typescript
this.boundClientId || this.activeClientId
```

决定。展示的路由与 `callTool()` 入口没有强制执行 `chat_read_preflight`，也没有校验期望 client/project/revision。

**可复现时序**

- Chat 读取 C1/P1 并完成前检。
- C2 激活，或另一原生 turn 绑定 C2。
- Chat 调用写工具，目标选择逻辑此时指向 C2。

原生 turn 的 bound-client 测试证明焦点变化期间的客户端绑定行为。它未证明 Chat 请求归属，也未证明同一 client 切换项目时的 project 绑定。

**最低修改**

将权限矩阵中“须用户明确确认唯一画布”补充为明确的验收阻断条件。现有通路尚不能验收目标安全写入，单客户端、busy 检查和人工确认均不足以解除该阻断。原子路由继续留给 WAR-35/WAR-37，WAR-90 无需增加新 Agent 或桥接服务。

## P2 问题

### 5. 成功输出遗漏 client 身份

输入验证了 `client_id`，返回对象却仅保留 project/node/shot，降低后续记录的可追溯性。

**最低修改**

返回 `client_id`，并明确结果属于本次输入校验。该字段只能帮助追踪，无法锁定服务器目标。

### 6. MCP 权限和 HTTP 工具权限需要分别保留未知状态

**证据**

冻结材料已正确指出 `default_tools_approval_mode=approve` 与 `codex_approval` 事件不能证明 MCP 调用可由真人拒绝。HTTP 路由直接调用 `session.callTool()`，片段未展示请求鉴权、逐工具授权或拒执行控制。

**最低修改**

在验收表中分别列出：

- 原生 MCP 实际工具清单与拒执行证据。
- HTTP 调用者鉴权、可调用工具范围与拒执行证据。
- 正式线程中 codegraph/hindsight overrides 的实际生效结果。

这些都保持 **unknown**。源码片段不足以判定整个服务无鉴权，也不足以证明 HTTP 继承原生 Codex 的审批机制。

## P0 与只读 gate 判断

**未从提供片段确认 P0。**

`chat_read_preflight.verify()` 没有网络或写入副作用，返回值固定包含 `can_write=False`，因此本函数没有直接授予写权限。现存缺陷集中于只读“上下文已验证”的声明过宽，以及缺失 B/SHA 时的错误通过。

若下游仅依据 `read_context_verified=True` 开放写工具，会越过当前授权边界。冻结包没有提供该下游实现，其实际行为为 **unknown**。

## 后续仍未知

- 当前源码树是否与 manifest 一致，材料未提供独立验证。
- 七文件专业正文的完整权限约束，本消息仅提供摘要、路径和 SHA。
- `compactCanvasState` 是否实际返回 gate 所需 client/project 字段。
- 同一 client 切换项目、断线重连、请求在途时的端到端目标行为。
- HTTP 前检接线、请求鉴权、逐工具授权和真正拒执行路径。
- 正式安装、新线程加载、正式 MCP 权限及真实修改后人审 B 闭环。

完成上述最小修订后，可重新审阅 WAR-90 的准备阶段结论。生产安装与 Chat 写入仍分别依赖其实际验收证据。
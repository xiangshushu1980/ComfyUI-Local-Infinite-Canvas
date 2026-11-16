## Gate source
#!/usr/bin/env python3
"""Pure-data Chat→Canvas read preflight; never issues HTTP, MCP or Canvas writes.

A matching result is NOT write authorization, not a cross-endpoint CAS, and not
cryptographic proof that a rendered Canvas node matches a Director B candidate.
"""
import hashlib
import re

class PreflightBlocked(ValueError):
    pass

def verify(health, state, selection, authority, *, project_id, client_id,
           node_id, expected_shot_id, approved_b_id, source_sha256, shot_sha256):
    def require(test, reason):
        if not test: raise PreflightBlocked(reason)
    require(health.get('ok') is True and health.get('hasCanvas') is True,
            'no connected Canvas state')
    require(health.get('clients') == 1, 'not exactly one Canvas browser client')
    require(health.get('codexBusy') is False, 'Canvas Codex turn busy or unknown')
    require(project_id and client_id and node_id and expected_shot_id, 'explicit project/client/node/shot identity required')
    require(isinstance(approved_b_id,str) and re.fullmatch(r'[0-9a-f]{32}',approved_b_id),
            'valid approved B id is required')
    require(isinstance(source_sha256,str) and re.fullmatch(r'[0-9a-f]{64}',source_sha256),
            'valid source SHA256 is required')
    require(isinstance(shot_sha256,str) and re.fullmatch(r'[0-9a-f]{64}',shot_sha256),
            'valid Shot SHA256 is required')
    require(state.get('projectId') == project_id, 'project ID changed or missing')
    require(state.get('clientId') == client_id, 'Canvas client ID changed or missing')
    nodes = state.get('nodes') or []
    require(sum(n.get('id') == node_id for n in nodes) == 1, 'target node missing or duplicate')
    selected = state.get('selectedNodeIds') or []
    require(selected == [node_id], 'exactly one intended Canvas selection required')
    chosen = (selection or {}).get('nodes') or []
    require(len(chosen)==1 and chosen[0].get('id')==node_id,
            'selected node readback disagrees')
    require(authority.get('pilot_only') is True,
            'expected WAR-90 pilot projection')
    require(authority.get('authority',{}).get('approved_B_id') == approved_b_id,
            'approved B identity changed')
    require(authority.get('source',{}).get('sha256') == source_sha256,
            'source version changed')
    source_text=(authority.get('source') or {}).get('text')
    require(isinstance(source_text,str) and bool(source_text),
            'source full text missing')
    require(hashlib.sha256(source_text.encode('utf-8')).hexdigest()==source_sha256,
            'source text SHA256 does not match full text')
    target=authority.get('target_shot') or {}
    require(target.get('text_sha256') == shot_sha256,
            'target Shot text SHA changed')
    require(target.get('id') == expected_shot_id, 'target Shot ID mismatch')
    require(target.get('text'), 'target Shot full text missing')
    require(hashlib.sha256(target['text'].encode('utf-8')).hexdigest()==shot_sha256,
            'Shot text SHA256 does not match full text')
    require(authority.get('capabilities',{}).get('production_approval') is False,
            'pilot-only approval boundary missing')
    require(authority.get('capabilities',{}).get('write_canvas') is False,
            'view claims write capability unexpectedly')
    return {'provided_identifiers_consistent': True, 'can_write': False,
            'reason': 'No atomic client/project binding or write approval in /api/tools',
            'project_id':project_id, 'client_id':client_id, 'target_node_id':node_id,
            'target_shot_id':expected_shot_id,
            'approved_B_id':approved_b_id,
            'source_sha256':source_sha256,'shot_sha256':shot_sha256,
            'not_verified':[
                'whether selected Canvas Node actually maps to the claimed Director Shot',
                'whether selection and state originate from one atomic client/project snapshot',
                'whether any supplied snapshot is fresh or still current',
                'whether the rendered Canvas node text is the complete approved B source',
                'identity of user authorizing a future mutation',
                'no race after this check (server has no cross-entry CAS)',
                'permissions of native Codex MCP tools']}

if __name__ == '__main__':
    # Designed as a reusable pure function; no CLI takes the Agent access token.
    print('Pure-data only: import verify() with fresh read results; never treat as write permission.')

## New unit tests
import unittest
import hashlib
from chat_read_preflight import verify,PreflightBlocked

class ChatReadPreflightTests(unittest.TestCase):
    def setUp(self):
        self.health={'ok':True,'hasCanvas':True,'clients':1,'codexBusy':False}
        self.state={'projectId':'explicit-p','clientId':'explicit-client',
                    'nodes':[{'id':'chosen-node'}],'selectedNodeIds':['chosen-node']}
        self.selection={'nodes':[{'id':'chosen-node'}]}
        self.source_text='Original source exactly'
        self.shot_text='approved Shot02 full text'
        self.source_sha=hashlib.sha256(self.source_text.encode()).hexdigest()
        self.shot_sha=hashlib.sha256(self.shot_text.encode()).hexdigest()
        self.b_id='b7b4fd156b884907b2431b6b1e0d9960'
        self.authority={'pilot_only':True,'authority':{'approved_B_id':self.b_id},
            'source':{'text':self.source_text,'sha256':self.source_sha},
            'target_shot':{'id':'Shot02','text':self.shot_text,'text_sha256':self.shot_sha},
            'capabilities':{'write_canvas':False,'production_approval':False}}
        self.expected=dict(project_id='explicit-p',client_id='explicit-client',
                           node_id='chosen-node',expected_shot_id='Shot02',approved_b_id=self.b_id,
                           source_sha256=self.source_sha,shot_sha256=self.shot_sha)
    def call(self):
        return verify(self.health,self.state,self.selection,self.authority,**self.expected)
    def test_exact_data_allows_read_only_but_never_write(self):
        r=self.call()
        self.assertTrue(r['provided_identifiers_consistent'])
        self.assertEqual(r['client_id'],'explicit-client')
        self.assertIn('actually maps', ' '.join(r['not_verified']))
        self.assertFalse(r['can_write'])
    def test_multiple_tabs_denied(self):
        self.health['clients']=2
        with self.assertRaisesRegex(PreflightBlocked,'exactly one'):
            self.call()
    def test_codex_busy_or_unknown_denied(self):
        for v in (True,None):
            with self.subTest(v=v):
                self.health['codexBusy']=v
                with self.assertRaisesRegex(PreflightBlocked,'busy'):
                    self.call()
    def test_client_routing_mismatch_denied(self):
        self.state['clientId']='different-active-tab'
        with self.assertRaisesRegex(PreflightBlocked,'client ID'):
            self.call()
    def test_project_mismatch_denied(self):
        self.state['projectId']='other-project'
        with self.assertRaisesRegex(PreflightBlocked,'project ID'):
            self.call()
    def test_selection_mismatch_denied(self):
        self.state['selectedNodeIds']=['another-node']
        with self.assertRaisesRegex(PreflightBlocked,'selection'):
            self.call()
    def test_selection_readback_mismatch_denied(self):
        self.selection['nodes']=[{'id':'another-node'}]
        with self.assertRaisesRegex(PreflightBlocked,'readback'):
            self.call()
    def test_wrong_b_denied(self):
        self.authority['authority']['approved_B_id']='0'*32
        with self.assertRaisesRegex(PreflightBlocked,'approved B'):
            self.call()
    def test_wrong_source_and_shot_denied(self):
        self.authority['source']['sha256']='0'*64
        with self.assertRaisesRegex(PreflightBlocked,'source'):
            self.call()
        self.authority['source']['sha256']=self.source_sha
        self.authority['target_shot']['text_sha256']='0'*64
        with self.assertRaisesRegex(PreflightBlocked,'Shot'):
            self.call()
    def test_shot_id_mismatch_denied(self):
        self.expected['expected_shot_id']='Shot03'
        with self.assertRaisesRegex(PreflightBlocked,'Shot ID mismatch'):
            self.call()
    def test_all_missing_version_values_rejected(self):
        self.expected['approved_b_id']=None
        self.expected['source_sha256']=None
        self.expected['shot_sha256']=None
        self.authority['authority']['approved_B_id']=None
        self.authority['source']['sha256']=None
        self.authority['target_shot']['text_sha256']=None
        with self.assertRaisesRegex(PreflightBlocked,'valid approved B'):
            self.call()
    def test_empty_and_invalid_version_formats_rejected(self):
        for field in ('approved_b_id','source_sha256','shot_sha256'):
            for value in ('',None,'stale', 'g'*64):
                with self.subTest(field=field,value=value):
                    original=self.expected[field]
                    self.expected[field]=value
                    with self.assertRaises(PreflightBlocked):
                        self.call()
                    self.expected[field]=original
    def test_full_source_and_target_bytes_verified(self):
        self.authority['source']['text']='unapproved changed source'
        with self.assertRaisesRegex(PreflightBlocked,'source text SHA256'):
            self.call()
        self.authority['source']['text']=self.source_text
        self.authority['target_shot']['text']='unapproved changed Shot'
        with self.assertRaisesRegex(PreflightBlocked,'Shot text SHA256'):
            self.call()
    def test_stale_snapshot_cannot_be_proven_fresh(self):
        # Data may be replayed verbatim after a browser switches projects.
        result=self.call()
        self.assertTrue(result['provided_identifiers_consistent'])
        self.assertFalse(result['can_write'])
        self.assertIn('snapshot is fresh',' '.join(result['not_verified']))
    def test_node_shot_mapping_not_attested(self):
        # Distinct valid node and selected id remain internally consistent.
        # Pure-data checks must not claim that this node represents Shot02.
        self.state['nodes']=[{'id':'another-unrelated-node'}]
        self.state['selectedNodeIds']=['another-unrelated-node']
        self.selection['nodes']=[{'id':'another-unrelated-node'}]
        self.expected['node_id']='another-unrelated-node'
        r=self.call()
        self.assertFalse(r['can_write'])
        self.assertIn('Node actually maps',' '.join(r['not_verified']))
    def test_node_missing_duplicate_denied(self):
        self.state['nodes']=[]
        with self.assertRaisesRegex(PreflightBlocked,'missing or duplicate'):
            self.call()
        self.state['nodes']=[{'id':'chosen-node'},{'id':'chosen-node'}]
        with self.assertRaisesRegex(PreflightBlocked,'missing or duplicate'):
            self.call()
    def test_incomplete_authority_denied(self):
        self.authority['target_shot']['text']=''
        with self.assertRaisesRegex(PreflightBlocked,'full text'):
            self.call()
    def test_elevated_capability_claim_denied(self):
        self.authority['capabilities']['write_canvas']=True
        with self.assertRaisesRegex(PreflightBlocked,'write capability'):
            self.call()

if __name__=='__main__':unittest.main()

## Test result
----------------------------------------------------------------------
Ran 18 tests in 0.001s

OK

## Real B projection + explicitly synthetic Canvas fixture result
{
  "status": "PASS pure-data with actual approved-B review-shot projection",
  "canvas_state": "SYNTHETIC - no real browser API called",
  "can_write": false,
  "B_id": "b7b4fd156b884907b2431b6b1e0d9960",
  "source_sha256": "65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d",
  "shot_sha256": "92c27994389848915158d107bc6a304e012536f9f878d23049be9d9c3d7ded90",
  "unverified": [
    "whether selected Canvas Node actually maps to the claimed Director Shot",
    "whether selection and state originate from one atomic client/project snapshot",
    "whether any supplied snapshot is fresh or still current",
    "whether the rendered Canvas node text is the complete approved B source",
    "identity of user authorizing a future mutation",
    "no race after this check (server has no cross-entry CAS)",
    "permissions of native Codex MCP tools"
  ]
}

## Original independent review P1 problems
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
## Main review
**主审结论：targeted-revision。** 可保存本轮预检证据并等待正式用户授权，无须为收口启动服务或安装 Skill；但应同时记录已确认缺陷，撤回“完整只读上下文匹配”的成功声明。生产操作与 Chat 目标安全写入为 **block**；实际 MCP 拒执行、HTTP 权限及正式集成为 **unknown**。本审阅不签 B。

我先独立核对冻结源码与结果，再对照两份报告；以下为材料核证，未现场复现。原生结果支持临时环境三次 Skill 发现及七文件回退恢复，不证明模型实际使用阶段正文，也不证明 Canvas HTTP 集成。当前源码树没有独立校验，不能把 manifest 当作现树一致证明。84 项单测记录可确认通过；13 项离线测试仅有通过摘要，且不能排除源码直接揭示的漏检。

逐项裁决如下：

1. **生命周期与发布治理：采纳，但区分已写规程和未执行验收。** Store revision 确实只覆盖两个文件，不能代表七文件包。完整清单、Git 来源、停用活动 turn、备份及新线程重发现已在提案中，不应重复描述为方案完全缺失。Reviewer 要求补 HTTP 实测，属于后续集成验收前置，**不是保存预检、等待授权的前置条件**。
2. **只读 gate：采纳归属 Reviewer 的三个实质缺陷，修正另一报告的“前检通过”概括。** Node 与 Shot 分别存在不等于二者关联；独立输入对象不能证明同源、新近或同次快照；B/SHA 双方缺失时，`None == None` 确会放行。这些均可从源码推出，无须投票。`can_write=false` 阻止其直接授予写权限，却不能使错误的核验成功成立。
3. **Chat 写入：两报告风险判断成立，矩阵表述必须收紧。** `/api/tools` 未携带请求级目标约束，目标采用 bound/active client；单客户端检查、busy 检查和真人确认都不能消除随后切换的竞态。原生 turn 绑定测试不能外推为 Chat 请求或同一 client 内项目绑定已安全。
4. **权限与严重性：保留未知，拒绝扩大推论。** 配置关闭、默认 approve、审批事件均不是实际拒执行证据；片段也不足以断言整个 HTTP 服务无鉴权。没有证据确认生产误写、自动批准或 P0，更不能推测存在把 gate 成功值接到写工具的下游。

**必须**：修正 B ID 非空与 SHA 格式校验；将成功语义收窄为“输入字段部分一致”，明确未验证 Node→Shot、读取来源、新鲜度及审批身份，返回 client_id；删除“函数验证新近快照”的表述，并将 Chat 写入阻断写入矩阵。若声称摘要证明返回全文，还须重算文本 SHA。增加缺失值、非法摘要、错配节点与旧快照的针对性用例。错误放行和过宽成功声明不应作为可用安全门禁保留；原始失败证据可以保留。

**建议**：发布清单补候选状态、Git 来源、七份 SHA、审阅状态与未安装标记。**延期**：原子目标路由、revision/CAS 交 WAR-35/WAR-37；正式安装、权限实测及真实修改闭环等待对应授权与真实需求。

可直接实施的下一阶段是先完成上述纯函数和文案修订，保存“有限预检通过、缺陷待修/已修、生产未验收”的记录。两入口共用同版七文件 Skill、同一 Runtime CLI 与权威材料：Canvas 加载完整安装副本，Chat 显式读取原件并调用同一 CLI，保留意见来源，不增设导演 Agent 或审批存储。共享知识不继承权限；Chat 不以文本 @引用或最近焦点确定画布。授权后再核工作空间、安装、新线程只读验证，并分别核证 MCP 与 HTTP 权限；此前不声称生产 Skill 已安装或真实权限已通过。
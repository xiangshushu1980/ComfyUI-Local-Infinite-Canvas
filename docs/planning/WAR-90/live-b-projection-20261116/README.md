# WAR-90｜真实画布「无限画布 1」的 B 镜头展示副本

日期 2026-11-16；机器 Eric。用户在 Chat 明确授权向其已连接的“无限画布 1”增加 D《错过的钥匙》Shot01–Shot04 四个文本审阅节点，保留原有三个空节点。没有授权更改批准导演计划、生成媒体或建立新的通用写入协议。

## 目标与输入

- 真实目标：projectId mrEXrMQoY-2ef3U6NsHtj，title“无限画布 1”；写入前 Agent 单客户端、Codex ready。
- 三个原节点：text-1793372915213-2q1pb、image-1793372917582-2pevr、audio-1793372920916-z4dgp；原内容、属性与位置由只读工具冻结哈希，后续复核未变。
- 新四镜节点：Shot01=text-1794823805462-0、Shot02=text-1794823805462-1、Shot03=text-1794823805462-2、Shot04=text-1794823805462-3；x=1040/1740/2440/3140，y=140，宽650，最后节点高850，其余740。新建节点时画布自动选中了 Shot04。
- 权威源：docs/planning/WAR-90/pilot-D-local-repair-v2/state.json，SHA256 23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7。批准 B ID b7b4fd156b884907b2431b6b1e0d9960，属于 WAR-90 的 pilot-only 批准，并非正式 WAR-35 类型化数据/审批。prepare_projection.py 经 Pilot.review_packet() 验证来源后生成四节点的完整正文和哈希；文本清楚标记为展示副本、非权威版本。

## 实际执行与发现

1. read_only_preflight.py 确认了用户真实画布、三原节点、无选区与已批准 B。run_native_projection.py 由正式 Canvas Agent 的原生 Codex 线程执行，选择七文件 Director Skill，真实调用一次 Canvas MCP canvas_create_text_nodes 新增四个文本节点，随后再次读取。节点总数 3→7；无重复创建。
2. 初次自动审计发生了误判：Canvas Agent 源码 infinite-canvas/canvas-agent/src/canvas/tools.ts 的 compactNode() 明确规定 metadata.content 超过240字符时，canvas_get_state 返回前120字符加三个点，即长度123。此前审计把这个压缩预览当作真实全文来算 SHA，从而错误地认为四个镜头都被模型省略。**这个 123 字符不是数据丢失证据。**
3. 基于误判要求模型修复 Shot01，模型确实调用了一次 canvas_update_node_text，但写入的值只有111字符，造成 Shot01 的真实临时不完整。第二次尝试让模型终端执行确定性帮助脚本，受到 Codex shell 网络沙箱限制，连接本地 127.0.0.1:17373 报 Operation not permitted，因此未写入。
4. 最终为修复四个既存节点，在已有用户授权下采用**一次性严格守门的本地 Canvas Agent API 批量更新**：apply_exact_projection.py 检查只有一个客户端、Agent 无同时运行的 turn、projectId/title/clientId 精确匹配、七个节点 ID 精确匹配、原三个节点哈希未变、批准 B SHA 不变。一个 canvas_apply_ops 请求含四个 update_node 操作，只更新新建四镜的文本；无 add/delete/move/generate。文本来自 Runtime，完全绕开模型转写。
5. 该批量更新工具 HTTP 200，浏览器返回完整的七节点快照；exact-tool-inner-diagnostic.json 记录四镜实际**完整工具结果**的全文 SHA，Shot01–Shot04 与确定性来源预期 4/4 完全匹配。其后对 canvas_get_state 的只读回查仍返回四个123字符 compact 摘要，正是前述压缩行为。
6. verify_projection.py 结合浏览器完整工具结果 SHA 与最新 compact 前缀回读进行最终核查：目标项目正确、7节点、原三个哈希不变、四个展示节点正文完整工具结果 SHA 全匹配、缩略前缀全匹配、坐标/尺寸匹配、权威 B state SHA 未变。projection-final-audit.json success=true。**未通过浏览器页面刷新重新加载以验证持久化**，不得称存储恢复已验收。
7. apply_exact_projection.py 增加了完成后拒绝重复更新的保护：存在已通过的 projection-final-audit.json 时不再执行。no-repeat-guard-result.json 实测拒绝再次写入。Director Runtime 64/64 回归通过。

## 状态与边界

**PASS（文本展示副本试点）**：四个展示节点已创建，最新浏览器完整工具结果与权威 B 的四段文本哈希完全相同；原有三节点、批准 B 未改；没有执行媒体/GPU 工作。

**未验收**：刷新/重新打开画布后的持久化、正式 Node→Shot typed mapping、通用多客户端请求级 CAS、MCP 审批拒执行、真实视听/观众表达验证。该显示副本不取代 Runtime 中的批准 B。

**关于权限**：通用 Chat HTTP 画布写入仍 BLOCK。本次在用户明示授权、仅一个客户端、固定项目、固定四个**已创建**节点 ID 且无新增/删除的情况下进行一次性收窄修复，不代表跨客户端安全写入通过。原生 Agent 模型可判断专业问题，但不可将缩略工具回复冒充全文，或使用生成模型手抄内容作为确定性版本同步机制。

## 证据入口

- prepare_projection.py：来自已批准 Runtime B 的精确节点内容生成。
- run_native_projection.py、native-projection-result.json：原生 Agent 首轮创建及停点。
- repair_native_node.py、repair-Shot01.json：模型写入111字符的反例；原生 CLI 网络沙箱拒绝的诊断日志。
- apply_exact_projection.py、exact-preflight.json、exact-tool-inner-diagnostic.json：受控单次确定性修复、完整工具结果 SHA 与原始来源保护。
- verify_projection.py、projection-final-audit.json：正确理解 compact 行为的最终只读核验。
- no-repeat-guard-result.json：完成后阻止重复写入。
- evidence.sha256：此目录必要研究材料的文件指纹。

下一步在用户实际画布选中 Shot02，继续使用正式 Canvas Agent 与用户审阅镜头观看目标、注意力及钥匙可读风险，仍不自动修订 B 或生成媒体。


## 2026-11-16 19:19｜用户报告找不到刚才画布：同名项目与双客户端

只读诊断：Agent/Web 正常、HTTP 200，Agent clients=2、未执行 Codex turn。日志确认19:14:22新客户端 D1l1a2E-C7WZ3-bJch_zN 连接；原四镜投影客户端04wsd618VDFdUWb74oZZI 自16:54:06保持连接，未见断开记录，原标签页/窗口可能仍开着。

当前 active 客户端的 canvas_get_state 返回 title“无限画布1”，但 projectId=YDOXJBsX1hiZuK58rfmdy，节点数7，不含 Shot01–04。此客户端 canvas_list_projects 仅有两个项目：无限画布3（ID VBDrDdBK9cou6_nYrGCW3，0节点）、无限画布1（ID YDOXJBsX1hiZuK58rfmdy，7节点），不含先前已操作项目 ID mrEXrMQoY-2ef3U6NsHtj。不能仅凭名称选择项目，不应往当前同名画布写四镜。

Web 正式路由为 /canvas/:id。项目状态由浏览器本地 Zustand persist + localforage/IndexedDB 保存，存储键 infinite-canvas:canvas_store。同名不同 ID 可能源自不同浏览器配置、不同 URL origin，或多标签页状态未同步；哪一种尚未确认。HTTP GET /canvas/mrEXrMQoY-2ef3U6NsHtj 得到200只证明前端 SPA 路由存在，不能证明当前浏览器本地有该项目。

找回建议：优先切回19:14之前的原浏览器标签页/窗口，并使用它原有的协议、地址、端口进入 /canvas/mrEXrMQoY-2ef3U6NsHtj；若看不到，检查协议、域名、端口及 browser profile 差异。没有调用 activate/navigate，没有移动或重建节点，没有验证原项目刷新后的持久恢复。后续产品工作须显示精确 projectId/origin/active-client 并设计请求级写目标绑定，归 WAR-37。


## 2026-11-16 19:24｜单实例与多浏览器数据源核对（只读）

- 本轮实测 Eric systemd 中 Web 仅一个 vite 实例（PID7295，自16:08启动，监听127.0.0.1:3000）；Canvas Agent 单实例（PID7294 / 子进程7315，监听127.0.0.1:17373）；ComfyUI Gateway PID8636/8647监听127.0.0.1:8190。没有第二个 Web/Agent 监听端口，也没有同时运行的独立临时174xx私有测试服务。不能据此排除**用户其它机器**另有 Web 实例，当前只证明 Eric 的运行面。
- Eric Caddy配置中没有Canvas Lab Web代理路由；浏览器入口有可能从 WSL localhost、127.0.0.1、Tailscale/代理、浏览器 profile 等来源打开同一个Web实例。不同 scheme/host/port 属于不同origin，浏览器 IndexedDB/localforage 完全独立。实际两页访问origin尚未从浏览器确认，不能当作已经证实的根因。
- 官方操作指南 docs/agent/canvas-agent-remote-control-20261112.md 第26行记载当时用 Windows PowerShell Start-Process打开 http://localhost:3000/canvas?mode=recent；此入口是**浏览器本地最近项目**快捷方式，不是项目ID定位。源码 infinite-canvas/web/src/pages/canvas/index.tsx 表明mode=recent取本地projects[0]，若为空则创建新画布，可能误入另一张同名画布。因此不应再把 /canvas?mode=recent 作为本次固定项目的入口。
- 真实目标为 /canvas/mrEXrMQoY-2ef3U6NsHtj，但这是纯SPA路由：源码 infinite-canvas/web/src/pages/canvas/project.tsx 若本地 openProject(projectId) 缺失就navigate('/canvas')，故HTTP 200不能验证本地项目存在。需在**旧客户端相同浏览器profile和origin**访问。原浏览器客户端仍连接不代表刷新后的数据已保存；持续连接状态与本地IndexedDB持久性是不同命题。
- 当前Agent clients=2。19:23:16新客户端短断并于19:23:17重连；它最新呈现的是页面非画布（API canvas_get_state={hasCanvas:false, clientId:新客户端}），不能对它进行任何Canvas编辑。未激活/切换客户端、未重定向浏览器、未写项目。
- 辅助原因：本地 Zustand persist 持久化键 infinite-canvas:canvas_store，底层 localforage(name infinite-canvas, storeName app_state)；项目只有浏览器端权威数据。即便来自同一origin，两个已打开的标签页可能存在未同步的内存状态，不能只凭两个客户端就断言是两个不同origin。
- 恢复操作：先找回约18:08在用的原窗口，读取它地址栏中的scheme/host/port，直接进入相同origin加固定ID的 /canvas/mrEXrMQoY-2ef3U6NsHtj；若仍重定向列表，先检查原浏览器 profile 的本地项目列表是否含该ID，并避免新建空项目/删除缓存。原窗口URL尚未读到，因此不发送无条件可用的绝对链接。

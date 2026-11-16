# Canvas Lab｜Caddy 规范入口与浏览器 Origin 数据隔离

日期：2026-11-16；机器：Eric；工作方向：Canvas Lab Rebuild。

## 当前有效决定（2026-11-16 晚间更新）

**用户明确取消旧 Origin 数据迁移：不用开发或保留迁移页面。** 从现在起仅以 http://canvas.localhost/canvas 为 Canvas Lab 的标准访问地址，在该 Origin 新建画布并重新创建需要的 Shot01–Shot04 文本节点即可。此前临时创建、未提交的迁移原型 HTML/TS 已撤销，仓库中不保留该功能。旧 localhost:3000、127.0.0.1:3000 下的项目不迁入新 Origin；用户允许以后清理它们，但目前未执行清理，避免错删非试点项目。

**当前唯一待执行的产品操作**：用户用 Windows 浏览器打开规范入口并进入一张新画布，确认 Canvas Agent 与这张画布连接后，按批准 Runtime B 的只读输出重新创建四个文本审阅节点，并复核其内容。不可在未确认浏览器 Origin/projectId 的情况下通过 Chat HTTP 对当前 active client 写入。

## 有效约定

Canvas Lab 唯一推荐入口：**http://canvas.localhost/canvas**。
用户已明确请求沿用 Hive0 的既有 Caddy 服务，为 Canvas Lab 建立固定入口，后续统一从此地址访问。

Eric 上 Caddy 主文件 /etc/caddy/Caddyfile 包含 /var/lib/hivemind-caddy/Caddyfile。2026-11-16 新增单一站点：

    http://canvas.localhost {
        reverse_proxy 127.0.0.1:3000
    }

配置文件的实体路径 /var/lib/hivemind-caddy/Caddyfile（用户 sean，组 caddy），已由 Caddy reload 热更新。原 Hive0 站点 http://hive0.localhost、Hive 及其他代理保留不动。没有新增 Canvas Lab 实例、没有修改 Web 代码、没有重启 Canvas Lab 或 Agent 进程，也没有修改 ComfyUI/H3。

## 真实验收与证据

- Caddy 配置先经 /usr/local/bin/caddy validate --config /etc/caddy/Caddyfile 验证，返回 Valid configuration；随后 /usr/local/bin/caddy reload --config /etc/caddy/Caddyfile 成功。
- 原配置备份在 Eric 的 /var/lib/hivemind-caddy/Caddyfile.backup-canvaslab-20261116T194709。Caddy 运行中，重载后 Hive0 仍 HTTP 200。重启后服务从实体配置文件加载，配置持久。
- 固定入口通过 Caddy Host=canvas.localhost 获取 /canvas 与动态项目路由，HTTP 200、HTML 1229 字节，HTML SHA256 与 127.0.0.1:3000/canvas 一致（7320a09c4c0c9f8dd7807bddb0ee92b3f9a70fa2c0acc41c9773af25414fba14）。/src/stores/canvas/use-canvas-store.ts HTTP 200，JS 内容与原服务一致。
- WebSocket/HMR 以 Host: canvas.localhost 提交 Upgrade，收到 HTTP 101 Switching Protocols；测试客户端因仅请求握手、不保持消息而 5 秒超时，此时 101 已证明 Caddy 传递 Upgrade。
- Canvas Agent 原址 127.0.0.1:17373 对 Origin: http://canvas.localhost 的 OPTIONS 预检 HTTP 200，响应 Access-Control-Allow-Origin 和必要请求头。用户在新 Origin 连接 Agent 可能需在画布 Agent UI 重新授权/连接一次；不转移或公开原有 token。
- Eric 侧新站点经 HTTP 验证；**尚未从用户 Windows 浏览器实际点击、创建/打开项目并完成 Agent 对话验收**。Caddy 热重载日志有一条 autosave 目录不可写警告，但 load complete、实际站点响应与实体配置持久性均正常；这条警告不是本轮入口阻塞。

## 为什么过去出现三套画布

现有 Canvas Lab Web 项目保存在各浏览器 Origin 独立的 localforage/IndexedDB 中，而非 Eric 统一后端：

- http://localhost:3000
- http://127.0.0.1:3000
- **http://canvas.localhost（新的规范 Origin）**

这三者在浏览器安全模型下各有独立存储。浏览器 localforage name=infinite-canvas, storeName=app_state，Zustand 持久化 key=infinite-canvas:canvas_store。此规则不代表有三份 Canvas Lab 服务实例；只是三套互不自动共享的项目库。

## 历史方案：旧数据安全迁移策略（用户已取消，不再执行）

不做旧地址重定向、不删除旧项目、不合并覆盖浏览器数据库，因为那会令旧 Origin 的项目难以访问。用户确认新入口可正常打开后：

1. 分别进入两个旧地址的 /canvas 项目列表，将需要保留的画布**导出为 ZIP**，留一份外部备份。导出功能会收集相关资产引用。尤其注意之前已批准 B 的四镜头展示项目 ID mrEXrMQoY-2ef3U6NsHtj 位于旧 localhost:3000 Origin，需先核对其原浏览器存储中仍有此项目。
2. 在 http://canvas.localhost/canvas 的项目列表中使用 UI **导入** ZIP，然后逐个检查画布名称、节点、媒体引用与内容。源码中的 importProject 会给导入项目分配**新的 project ID**，因此不能把旧 URL 当作新画布的导航入口。原旧版项目与新版本内容可能同名，迁移后按新 ID 登记。
3. 仅在用户确认新 Origin 内全部需要的项目与 Agent 交互正常且备份有效后，才考虑弃用旧入口。**本次未执行任何迁移，不清理浏览器数据，也不重定向旧地址。**
4. 更长远的工程任务是项目身份、存储和 Agent 写入目标的稳定绑定；本次只有固定域名配置，不能将其误认为解决了跨 Origin 同步或 WAR-37 多客户端目标竞态。

## 回退

如有必要，先备份新配置，再在 Eric 恢复上面的旧 Caddyfile（或仅删除该独立站点块），运行 caddy validate，随后 caddy reload。不需要动用户浏览器的项目库。

## 2026-11-16 21:02｜Gateway CORS 标准域名修复

用户可在 http://canvas.localhost/canvas/2FwEbySI5PYe7d6BL4pES 看到四个镜头文本节点，但页面出现“本地网关连接断开，正在自动重连…”。Eric Web、Canvas Agent、Gateway 均 active；Gateway /health HTTP200、comfy.reachable=true。根因是 Gateway 的 CORS_ORIGINS 默认列表缺少 http://canvas.localhost；新域名请求 GET /health 和 OPTIONS /api/session/heartbeat 不能得到 Access-Control-Allow-Origin，浏览器拦截响应，UI 不断提示重连。旧 localhost:3000 和 127.0.0.1:3000 则被允许。

在 Eric 新增持久 systemd drop-in：
/home/sean/.config/systemd/user/canvas-lab-gateway.service.d/canvas-canonical-origin.conf

配置内容：
    [Service]
    Environment="CORS_ORIGINS=http://canvas.localhost,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8188,http://127.0.0.1:8188"

执行 systemctl --user daemon-reload 与 restart canvas-lab-gateway.service。复验新 Origin GET /health HTTP200 且返回 Access-Control-Allow-Origin=http://canvas.localhost；OPTIONS 心跳预检 HTTP204 也带同一允许头；旧两个来源继续允许；陌生 Origin http://evil.example 仍不允许，没有放宽到通配符。重启后 Gateway HTTP200、status=ok、comfy.reachable=true、setup.phase=ready；Windows PowerShell 携带新 Origin 实测同样 HTTP200 且 CORS 响应正确。后续 Gateway /v1/models 与 /health 日志持续 HTTP200。

只读复核规范画布 projectId=2FwEbySI5PYe7d6BL4pES，Shot01–Shot04 四节点全部仍在；没有删除、修改任何画布或调用媒体生成。

验收边界：服务端修复和 Windows 请求 PASS；浏览器顶部 banner 是否消失仍需用户在实际 UI 中确认，不能把命令行返回200当作 UI 证据。前端 GatewayStatus 探测恢复后会自动清除 warning 并刷新。无须改 Caddy 或 Director Skill。

## 2026-11-16 21:23｜Windows 浏览器 UI 最终验收

用户明确反馈：在固定入口 canvas.localhost 的四镜头画布上，先前“本地网关连接断开，正在自动重连…”的提示**已经消失**，Shot01–Shot04 **四个文本节点已正常显示**。因此新 Origin 的 Gateway CORS 修复获得真实用户浏览器 UI 验收。此前服务端健康/CORS/Windows 跨域请求 PASS，本轮用户确认补齐前端可见性。无需再改 Caddy/Gateway/画布数据。入口与连接故障可以收口；WAR-90 的 Shot02 导演交互审阅是下一独立工作，不应自动执行生成或修改批准 B。

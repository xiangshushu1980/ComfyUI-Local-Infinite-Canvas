# WAR-90｜canvas.localhost 四镜头规范画布

日期 2026-11-16，机器 Eric；用户明确决定取消跨 Origin 旧画布迁移，授权 ChatGPT 直接在唯一规范域名新建画布及四个 Shot 文本展示节点。

## 本轮实际环境与画布

- Web：https 未启用；标准入口为 http://canvas.localhost/canvas，Caddy 反代 Eric 127.0.0.1:3000。
- 由 Eric 的 WSL 使用 Windows PowerShell Start-Process 在 Windows 默认浏览器现有 profile 中打开 http://canvas.localhost/canvas?mode=new，使用本地仅瞬时 URL fragment 连接 Canvas Agent。原 token 未写到磁盘、日志或 Git。
- 实际新画布：名称 无限画布 1，ID 2FwEbySI5PYe7d6BL4pES。创建时 0 节点，唯一连接客户端 jeUNwaV-t0QApaAKC2pMh，Agent 无任务冲突。用户可在同一浏览器直接访问 http://canvas.localhost/canvas/2FwEbySI5PYe7d6BL4pES。
- 旧 localhost:3000、127.0.0.1:3000 是别的浏览器 Origin 与独立画布库；原项目未迁移或删除。

## 四镜头精确创建

- 来源：docs/planning/WAR-90/pilot-D-local-repair-v2/state.json；原 B SHA256 23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7，批准 B ID b7b4fd156b884907b2431b6b1e0d9960。
- 直接使用已验证的 prepare_projection.py 从 Director Runtime 取得 Shot01–Shot04 原文和内容指纹，无模型手工抄写。
- 使用 Canvas Agent API 的 canvas_create_text_nodes 向真实 Windows 浏览器唯一连接的一张空白画布发起一次创建。工具 HTTP200，Browser 返回完整结果 4 节点、四镜正文 SHA 4/4 完全匹配；compact 画布再读 4/4 前缀匹配。严格没有媒体生成、没有重批 B、没有创建其他节点。
- 新节点：Shot01 text-1794832120997-0、Shot02 text-1794832120997-1、Shot03 text-1794832120997-2、Shot04 text-1794832120997-3；每节点以“已批准 B 的非权威展示副本”标注来源。
- 布局：4 个横排（第1个 x=160），viewport x=70,y=65,k=0.55；选中 Shot02 text-1794832120997-1。通过独立工具回读总节点数4、精确 Shot02 选区、正文前缀未改，presentation-audit.json passed=true。
- create_exact_display.py 防重：在调用写工具前已写入 write_called=true；已创建成功，不得重新运行脚本产生重复节点。creation-audit.json result_pass=true。
- 尚未独立验证浏览器完全刷新后的持久化恢复；已确认真实客户端回写与只读状态回查。

## Gateway 启动状态

用户特别提醒必须启动 Canvas Lab Gateway。已执行 systemctl --user start canvas-lab-gateway.service。Web、Agent、Gateway 三服务均 active。Gateway 在127.0.0.1:8190，Eric /health HTTP200 status=ok、comfy.reachable=true、14 个工作流、setup phase=ready；Windows PowerShell 直接访问同一 Gateway /health 也 HTTP200 status=ok、comfyReachable=True。未执行 H3/GPU/媒体生成。

Gateway unit static，canvas-lab.target disabled；本次当前运行不代表系统重启后自动启动。今后操作画布时先检查并按需启动 Gateway。

## 后续

- 旧画布和浏览器数据保持原样。旧 Origin 数据迁移原型已按用户决定撤销，不再开发。
- 下一步在规范画布真实选中的 Shot02 上进行 Director Skill/Canvas Agent 导演审阅：观看目标、钥匙瞬间显露和连续性。B 仍是 Runtime 权威，文本展示不代表最终视觉验证完成。

# Canvas Lab Rebuild — 纯 WSL 运行边界

> 用户于 2026-10-31 明确：**本项目为纯 WSL 部署**。本轮只读静态检查，尚未实际启动、连接或测试服务。

## 已确认
- 当前项目路径 `/home/sean/projects/canvas-lab/`。原始环境检查记录的是旧目录 `/home/sean/projects/canvas-lab-rebuild/`，且本次目录核对没有重查 Node.js/npm 版本或依赖状态。
- 参考项目的 `start-local.bat`、`launcher/config.example.json` 和 Windows 自动启动/接管流程是上游发布机制，**不作为本项目启动入口**。
- 参考 Launcher 配置包含 `closeCanvasStopsBackend: true`、`stopAdoptedComfyOnCanvasClose: true`；避免误触发关停共享 ComfyUI。
- 本轮未发现项目本地 `launcher/config.json`、`comfyui-gateway/data/`、前端和 Gateway 的 `node_modules/`；不能据此推断其它 WSL 路径的 ComfyUI/依赖状态。

## WSL 部署原则
- 前端、Gateway 与 ComfyUI 的部署、管理和测试以 WSL 内环境为准；先确认现有 ComfyUI 地址和权限，不安装或改写现有模型、节点、配置。
- 优先研究可独立启动的 Gateway 和前端，而不是直接调用 Windows Launcher；若未来需要一键启动，再在实测基础上设计 WSL 原生入口，**不预先实现**。
- 默认仅本机回环监听；暴露 WSL 网络端口或桥接 Windows 主机时单独审查安全。
- 不修改 ComfyUI 服务状态；运行测试、构建、安装依赖及 GPU 工作流均按项目授权边界办理。

## 验证顺序（尚未执行）
1. 只读确认 WSL ComfyUI 进程/端口/项目路径以及是否被其他项目使用。
2. 检查源码配置、参数绑定、当前工作流及测试入口。
3. 获准后进行有隔离的静态/单元测试及 Mock 协议测试。
4. 获准后针对本机 ComfyUI 验证生成、取消、异常与画布回写，并把证据记入 `validation-matrix.md`。

## 未确认
- WSL 内 ComfyUI 的真实位置、服务/端口、模型与节点可用性。
- Gateway、前端和 Agent 的真实可运行状态与端到端表现。
- 现有 Qwen 提示词改动所需自定义节点、输入签名、模型权重及测试结果。

## 当前本机开发服务部署（2026-11-01）

- Web 由 `canvas-lab-web.service` 运行 Vite 开发服务器，绑定 `127.0.0.1:3000`，使用 HMR；开发阶段不要求先构建 `dist`。
- Gateway 由 `canvas-lab-gateway.service` 以 Node `--watch` 运行参考项目 JavaScript 源码，监听 `127.0.0.1:8190`；源码文件变化触发进程重启。
- Canvas Agent 由 `canvas-lab-agent.service` 以 `tsx watch src/index.ts` 运行参考项目 TypeScript 源码，监听 `127.0.0.1:17373`；源码文件变化触发进程重启。
- 三个 user unit 由 `canvas-lab.target` 聚合；Hive0“无线画布”卡片检查三个 HTTP 端点并提供启动/停止；Hive0 helper 的受控 API 另支持重启整个 target。服务只在手动启动时运行，不启用用户登录自启。
- 这些 WSL/systemd 启动模板由 Rebuild 项目 `deploy/systemd/` 和 `deploy/install-user-services.sh` 管理；安装到 `~/.config/systemd/user/` 的是本机副本，不属于参考项目上游配置。前端/Gateway/Agent 依赖按各自锁文件安装，未改动 package manifest 或 lock。
- Web Vite 声明 `^8.3.5`，lock 固定 8.3.5。Web 依赖安装使用 `npm ci --legacy-peer-deps`，因为锁内 `@ant-design/pro-components@3.0.0-beta.3` peer 要求 antd 5、项目同时锁定 antd 6；没有更改依赖声明。

## 组件更新与快速重启讨论（2026-11-01）

- **Gateway 沿用参考项目的 JavaScript 实现。** Gateway 属于该参考项目源码，不应为了和 Canvas Agent 语言统一而大范围改写成 TypeScript；这种改写会增加后续同步上游更新的冲突与维护成本。WSL 适配优先放在服务启动/配置等薄层，尽量让 Gateway 源码保持贴近上游。此为本次讨论中用户确认的维护约束。
- 三个运行组件由 Hive0 的无线画布入口统一启动、停止；后端健康检查覆盖三个 HTTP 端点，受控 helper API 可重启整个 target。
- **刷新与重启按改动类型区分：** Web 源码由 Vite HMR 自动应用，必要时手动刷新浏览器；Canvas Agent 与 Gateway 源码由 watch 进程变化后自动重启。画布状态/操作通过前端与 Agent 的状态同步接口传送，画布内容变化本身不要求重启 Agent。
- **开发阶段的用户优先级：** 用户明确当前更重视修改代码后尽快看到结果，暂不把运行效率作为首要目标。已将本地启动改为上述开发模式；这不应与上游正式发布构建流程混为一谈。
- Hive0 面板当前的服务卡仍是点击切换启动/停止，没有单独的重启按钮；helper API 已允许受控重启整个聚合 target。Infinity Canvas 页面内的“快速重启”按钮也未实现。重启可能中断进行中的 Gateway/Agent 请求，当前实现尚未增加任务检测或确认提示。
- 真实浏览器里的 HMR 视觉更新仍未由用户验收；本轮已确认 Vite 页面及 HMR client 可访问、Gateway 与 Agent 健康端点响应，并通过 Hive0 执行了一次整组服务重启。

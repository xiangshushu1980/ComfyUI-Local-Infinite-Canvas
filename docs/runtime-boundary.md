# Canvas Lab Rebuild — 纯 WSL 运行边界

> 用户于 2026-10-31 明确：**本项目为纯 WSL 部署**。本轮只读静态检查，尚未实际启动、连接或测试服务。

## 已确认
- 项目路径 `/home/sean/projects/canvas-lab-rebuild/`；本地可运行 Node.js v24.18.0、npm v11.16.0。
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

# XIA-24 — 纯 WSL 验证方案（不接管 ComfyUI）

> 2026-11-01 方案验收；当前任务只制定测试协议，实际服务/生成操作不在本轮授权范围。

## 安全基线
- 仅在 WSL 内部署前端、Gateway 与 Agent；不执行 `start-local.bat` 或 Windows Launcher。
- 尊重已运行的 8188 ComfyUI；任何自动节点安装、模型拷贝、路径写入、显存清理、服务退出/重启操作均需明确授权。
- 测试入口与结果分级：S 源码静态定位；T 可复现单元/Mock；R 当前 WSL 端到端实测。

## 建议命令与副作用
| 阶段 | 命令/动作 | 副作用与限制 |
|---|---|---|
| 只读 Git | `git status --short; git diff --check; codegraph status` | 不运行程序；查看索引是否最新 |
| 静态语法 | `node --check comfyui-gateway/src/{registry,bindings,runner,server}.js`（逐文件） | 不访问 GPU；Node 仅解析语法 |
| 前端 typecheck | 在 web 中 `npm run typecheck` | 可能写 tsbuildinfo/缓存；有现有依赖才执行 |
| 前端 build | 在 web 中 `npm run build` | **覆盖受 Git 跟踪的 web/dist；必须预先保存/恢复** |
| Gateway 定向测试 | `node --test comfyui-gateway/test/<具体测试文件>.test.js` | 可能写临时测试产物、监听本地端口；先审查测试 |
| Gateway 全量测试 | 见 Gateway package.json | XIA-26 记录 HOST 环境变量与 Windows 路径断言问题；不应直接宣称通过 |
| Gateway / ComfyUI health | 只读访问 `127.0.0.1:8190/health`、`127.0.0.1:8188/system_stats` | 只可证明连通性，不能证明工作流可执行 |
| Mock 协议和真实生成 | 分别制定隔离端口/临时数据目录及工作流参数 | 运行服务/占端口或 GPU，必须再获授权 |

## 验收矩阵
- V02/V03/V04：记录版本、命令、退出码、失败与实际写入文件。
- V05：Mock 验证 mode → registry → bindings → runner → 输出/取消，禁止假数据当生产证明。
- V06：只读端口和模型/节点清单；区分健康和可用工作流数。
- V07–V10：真实任务需另行授权并保存输入、任务 ID、输出、重开画布回写/持久化、取消失败案例。
- V11/V12：Agent 读取与操作的权限、状态同步、重连和结果回写。
- V13：工作流变化与注册绑定回归；V14：WSL 启动/退出边界（不使用 Windows Launcher）。

## 当前历史证据
XIA-26 曾记录画布、Gateway、Agent、ComfyUI 健康及部分前端/Gateway 测试，且用户确认基础 Agent 链接；不是本轮重测，更不能代替 V07–V10。

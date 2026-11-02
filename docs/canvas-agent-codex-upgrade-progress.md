# Canvas Agent Codex 升级进度（2026-11-02）

> 本文按时间记录；以下早期“尚未实现”等状态由后续条目更新，不代表最新结论。

- 基线：`main` HEAD `aa4d6f6`，工作树已有多项未提交修改；本次保留这些改动。
- 执行前 Agent 服务是源码监听模式，健康状态报告 `codexBusy=false`、`clients=1`、`hasCanvas=true`；这不是端到端验证。
- `canvas-agent` 的 npm 声明及 lockfile 已将 `@openai/codex` 从 0.146.0 更新到 0.166.0；本地可执行文件报告 `codex-cli 0.166.0`。已运行的 app-server 进程尚未重启，不能认为它已切换版本。
- Agent 现有测试 126/126 通过；TypeScript build 通过。测试是现有自动测试，不代表真实 app-server 或 UI 验收。
- 升级前运行日志中，部分历史线程 `thread/read(includeTurns=true)` 返回 `paginated threads do not support thread/read(includeTurns=true)`；需要在新版本中复现并适配分页后验证线程读取和恢复。
- MCP 配置界面、升级后真实线程创建与恢复、审批及画布工具调用尚未完成验证。升级前健康响应记录 CodeGraph 启动握手失败；按照任务顺序，升级及界面完成后应重新采证，不应把该旧错误当成升级后的结论。
- 回滚依赖可将本次 package.json 和 package-lock.json 中的 Codex 版本恢复到 0.146.0 并重新安装；不要回滚工作树其他未提交修改。

## 2026-11-02 重启后补充

- 用户确认重启后对话可用，且 Codex Web 与 Canvas Agent 的模型选项一致；不再将模型列表差异作为问题。
- 当前 Agent app-server 使用项目安装路径的 Codex；Agent 健康状态仍报告 CodeGraph 握手关闭。健康状态不能证明其他 MCP 工具调用成功。
- 对 `thread/read` 返回分页线程不支持完整读取的错误，客户端改为读取线程元数据并按升序分页读取完整回合；其他错误仍原样返回，分页游标重复会报错。新增模拟分页测试；Agent 测试 127/127 通过，TypeScript build 通过。
- 修改后，对先前日志中报错的一个线程执行一次真实 HTTP 读取，返回 HTTP 200、`ok=true`；未核对完整历史内容，也未证明全部旧线程、审批或画布调用通过。此前该线程曾报告 `list_turns is not supported yet`，是否还存在其他受影响线程未确定。
- MCP 配置界面尚未实现；CodeGraph 尚未重新定位或修复。启动脚本按工作目录查找索引是待验证线索，不是根因结论。

## MCP 配置界面（2026-11-02）

- Agent 面板新增 MCP 页面，读取站点工作空间中 Codex 的有效配置，并将 Canvas Agent 自身的启用覆盖保存在 `canvas-agent.json`；不修改共享 Codex 配置。服务命令、环境变量和凭据不会由此接口返回。界面允许覆盖现有配置服务的启用状态或恢复继承，不提供新增、删除或编辑服务命令。`infinite-canvas` 是必需项，不可关闭；来自插件或不支持名称的服务只展示。
- 开关用于新线程；页面单独展示当前线程的启动状态。Codex 的 MCP 状态清单可能包含未启动的服务，Agent 不再单凭清单存在就将无工具且无启动通知的服务标为 ready。
- 自动检查：Agent build 成功，测试 129/129；前端 Vite build 成功；默认 typecheck 因既有 `vite.config.ts` 的 TS5097 失败，显式允许 TypeScript 扩展名的 typecheck 通过。构建生成的 dist 已恢复到构建前的状态；开发服务使用源码。
- 真实接口检查：列出有效配置成功；临时将 CodeGraph 设置为禁用、读取并恢复继承成功；无 token 返回 401、关闭必需画布服务返回 400、未知服务返回 404。隔离临时 app-server 线程中禁用配置的服务没有启动通知且工具数为零。以上不代表完整 MCP 工具调用或用户界面验收。
- Agent 以源码监听运行，代码修改触发了重启；当前线程状态可能重新加载。页面视觉与实际交互尚待用户验收；CodeGraph 启动原因和修复仍未完成。

## Canvas Skill 独立启用设置（2026-11-02）

- Skill 开关保存到 Canvas Agent 的 `skillOverrides`，不再调用会改写共享设置的 `skills/config/write`；列表显示继承或画布覆盖，支持恢复继承。现有的 Skill 文件管理范围不变。新建或恢复线程时读取 Codex 当前有效 Skill 配置，保留其他配置项并按路径应用覆盖；用户界面以新建对话作为明确生效边界。当前线程不保证立即更新。
- Agent build 成功、自动测试 130/130；前端在 `--allowImportingTsExtensions` 下类型检查通过。真实 HTTP 测试对一个用户 Skill 关闭再恢复继承，两次对共享 `~/.codex/config.toml` 做哈希比较均未变化。
- 独立 app-server 临时线程接受了包含共享条目和线程级覆盖的配置。进一步在临时工作空间创建随机命名的 Skill，分别创建启用和禁用它的线程，向模型询问可见的测试 Skill：启用时返回准确名称，禁用时返回 NONE；两个 turn 均 completed。测试是一次受控模型观察，不等于所有 Skill 类型、既有线程恢复和界面视觉验收均已通过。
- 现有 Agent 工作空间仍是 `/home/sean/projects/canvas-lab-rebuild`；本次未更改。原有工作树改动保留。

## Canvas MCP 注入与共享入口（2026-11-02）

- 用户要求核查 Codex Web 的共享 MCP 配置关闭时 Canvas Agent 注入，修复共享入口并分别验证。未关闭或重启正在运行的 Codex Web；在复制配置的独立临时 CODEX_HOME 中将同名共享 MCP 设为 disabled，使用 Canvas Agent 的真实 `CodexAppClient.startThread` 验证。修复前线程启动成功但 infinite-canvas 工具数为 0：注入命令未覆盖继承的 disabled。修复后线程配置显式 `enabled: true`，同样条件下工具数为 34，`canvas_get_state` 返回且 `isError=false`。这不是当前 Web 页面验收。
- 共享 `~/.codex/config.toml` 的 infinite-canvas 入口由不存在的 `canvas-lab/app/canvas-agent/dist/index.js` 修复为当前 Node + `infinite-canvas/canvas-agent/node_modules/tsx/dist/cli.mjs` + `infinite-canvas/canvas-agent/src/index.ts mcp`，保留 enabled=true。修复前私有备份保存在 `~/.codex/backups/canvas-mcp/`；TOML 解析与语义比较确认其他设置未变。配置依赖当前项目及本地 tsx 依赖存在。
- 使用与 Codex Web 相同的 Codex 可执行文件和修复后的共享配置创建隔离临时线程：34 个工具可用，`canvas_get_state` 成功，返回 projectId/clientId 与画布服务的直接读取一致。该测试未通过已打开的 Codex Web 页面或其现有线程；其新线程是否已加载新配置仍需在 Web 界面验证。
- Agent build 通过、自动测试 130/130；新增断言画布 MCP 线程设置始终显式启用。Canvas Agent 服务健康响应显示有画布、1 个客户端和当前 infinite-canvas ready；该状态不是画布写入或完整 UI 验收。
- 后续用户截图发现共享 MCP 的 Node 命令被写成 `/run/user/1000/fnm_multishells/.../bin/node` 临时会话软链。已修正为该软链当时解析到的持久安装路径 `/home/sean/.local/share/fnm/node-versions/v24.18.0/installation/bin/node`；私有备份已保存，其他 TOML 配置语义未改变。新建隔离线程重测 34 个工具，`canvas_get_state` 成功且项目和客户端与当前画布一致；现有 Web 线程未验证。

## CodeGraph 工作空间复核（2026-11-02）

- 用户推测 Canvas Agent 的工作空间为原 rebuild 目录、没有代码和索引，因而 CodeGraph 启动失败；用户已在 Canvas Agent 内关闭 CodeGraph。
- 当前 `canvas-agent.json` 中工作空间为 `/home/sean/projects/canvas-lab-rebuild`，该目录存在且当前仅有 `AGENTS.md`，无 `.codegraph/`；Canvas Agent 的 `mcpOverrides.codegraph=false`。当前健康响应的线程状态为 ready，MCP 列表中没有 CodeGraph。配置关闭和当前状态不证明其他线程已重载。
- 用户级 wrapper `/home/sean/.pi/agent/bin/codex-codegraph-mcp` 默认按 `CODEGRAPH_CWD` 或进程工作目录查找 `.codegraph/`；在上述目录且不设置 `CODEGRAPH_CWD` 的直接运行返回退出码 1，提示“无 .codegraph/ 索引”。因此用户的推测与直接复现的启动条件一致；由于没有采集当初失败 MCP 子进程的 cwd/环境和 stderr，不能将它断言为那一次握手关闭的唯一已证实原因。
- 不改变工作空间、不初始化索引、不重新启用 CodeGraph。实际项目源码和索引在 `/home/sean/projects/canvas-lab`；如未来需要 Canvas Agent 使用 CodeGraph，应先明确工作空间及权限，再单独验证启动与工具调用。

# XIA-59 · 新 Agent / Subagent 交接（2026-11-06）

## 从哪里开始

**先阅读** [Linear XIA-59](https://linear.app/xiangshushu/issue/XIA-59) 描述与最新评论，再读本目录 [README.md](README.md)、[upstream/manifest.json](upstream/manifest.json)、[runner/run_p0.py](runner/run_p0.py)。研究结论以已完成的 [XIA-57](https://linear.app/xiangshushu/issue/XIA-57) 为准；背景摘要见 `../../planning/ai-filmmaking-open-source-directing-review.md`。XIA-56 的纯 Beat 原始实验必须保持独立。

本地根目录：`/home/sean/projects/canvas-lab/docs/validation/XIA-59-shotplan/`（**远端机器 Eric 的本地磁盘**；不是 ChatGPT 容器，也不只是 Linear 链接）。源文件已下载、核对哈希，`manifest.json` **13/13 存在且 SHA256 全匹配**。

## 已存资料和真实含义

| 位置 | 内容 / 边界 |
|---|---|
| `upstream/toonflow/` | 原始 `shotCraft.md`、`storyboardTable.md`、`directorPlan.md` 的快照；**不是**完整 Toonflow-app 项目运行部署 |
| `upstream/director/` | 原始 `SKILL.md`、Beat Sheet、Blocking、Shot Plan、Continuity Bible；**不是**已执行完整 DirectorSKILL 生产包 |
| `upstream/vimax/` | 原始 `storyboard_artist.py`、`camera_image_generator.py`、`script2video_pipeline.py`；**不是** ViMax 安装/运行成功的声明 |
| `upstream/h3/` | 本机 `comfy-ops/.pi/skills/h3-prompt-writing` 中的 `SKILL.md` 与 `references/ref-en.txt` 冻结副本，供后续 P1；本机原件路径 `/home/sean/projects/comfy-ops/.pi/skills/h3-prompt-writing/` |
| `inputs/*.json` | 三个固定 8 秒咖啡馆 Beat；对话、道具交接、并行离开；人物 A 左/B 右、三张 Picture 的**文字约束**；不是图片原文件 |
| `runner/prepare.py` | 下载/冻结实验快照；**不要在首轮实验中重跑**，否则可能改变上游源版本 |
| `runner/run_p0.py` | 四路完整原文注入的**文本 Prompt replay / JSON adapter**；不是原 Toonflow 或 ViMax 可执行框架的端到端调用 |
| `runner/evaluate.py` | 仅做机械校验，不能直接得出导演质量排名 |
| `p0/01-dialogue/native/` | 首轮请求输入、元信息；DeepSeek 请求超时 220 秒，**没有成功模型输出** |
| `p0/mechanical-report.json` | 12/12 均标记未取得输出，不能当失败率统计 |

## 已确认状态

- Linear XIA-59 = **In Progress**，研究 XIA-57 = Done。
- **未完成**：P0 的 4 组 × 3 场景实测及案例级对照；P1 H3 六段 Prompt 统一编译；P2 H3 视频。
- 本次 DeepSeek/PI 测试请求 `deepseek/deepseek-flash`、`thinking=off` 在 220 秒无模型输出；另有临时 beellama 40 秒短请求未返回。`pi auth check` 曾显示 ready，但不意味着请求链路健康。不要将超时计作方法劣于基线。
- 没有触碰 Canvas、ComfyUI/H3 GPU、XIA-56 产物，也没有修改已有未提交仓库文件。
- 当前截图/图像 Reference **只有描述，没有在 XIA-59 目录复制图片**；P0 纯文本可以使用描述。若 P2 需要图片和 SHA，请从 XIA-56 已有材料核对并冻结真实图片。

## 新 Agent 的执行顺序（适合委派给 subagent）

1. **先排除工具通道超时**：用无会话、无工具、无 Skill 的极短请求测试一个提供商，记录服务商、实际模型 ID、推理设置、响应状态和耗时；优先避免运行环境自带 MCP/插件阻塞启动。检查 `pi` 帮助和 `runner/run_p0.py` 的参数是否适合本机版本，切勿因超时继续盲目批量调用。
2. 确定真正可工作的**同一个模型**和配置，按共同契约启动 P0。保留四路**完整原文**、隔离上下文与原始输出。若改模型，请明确记录，与已超时样本不要混为同批。
3. 每次输出保存完整 Prompt、模型配置、原始输出、失败日志与 SHA；执行 `python3 runner/evaluate.py` 检查格式/时间/对白，人工逐场核对切镜新增信息、人物 Blocking、持杯手/held_by、首尾状态和未授权新剧情。至少每类场景展示一个四路错误证据对照；首轮不做胜率统计。
4. 向用户提交 P0 案例级差异，**在用户确认后**进入 P1 统一官方兼容 H3 Skill 静态 Prompt 编译。独立增加 Beat→H3 Skill 直出基线，不能并入 native Shot Plan 组。P2 视频仍需单独确认，Canvas 在所有测试及讨论之后考虑。

## 关键方法限制

- 四组不一定是真正的原项目可执行流程：Toonflow 与 DirectorSKILL 使用原始 Skill 文本；ViMax 把源码中的 Prompt/结构抽到文本调用，**未启动其 LangChain/Pydantic 和 Camera Tree**。因此必须称为“上游文本方法/Prompt replay 对照”，不能误标成“完整原框架效果”。
- `run_p0.py` 给所有组附加一份可比较的 JSON 输出协议。适配文案在脚本中可审计，绝不能暗中加入新的镜头启发式。
- 任务说明前段概述 P0/P1，但 P0 章节明确要求用户确认差异后才继续 P1；采用**更严格**的阶段门槛。
- 现有 git 工作区有其他任务未提交修改（包括构建产物和研究文档）。**不要清理、覆盖或打包提交整个工作树**；只操作本目录的新文件，必要时单独提交。

## 可发给 subagent 的启动指令

> 请接手 Linear XIA-59。首先读取本地 `docs/validation/XIA-59-shotplan/HANDOFF.md`、`README.md`、`upstream/manifest.json`、`runner/run_p0.py` 以及 Linear XIA-59/XIA-57。先排除 `pi` 模型调用超时，再用同一个真实可用 LLM 运行三场景四路 P0 Shot Plan，保留上游原始 Skill/Prompt、完整请求/响应/日志/哈希，形成案例级错误与镜头理由对照。不要运行 ComfyUI/GPU，不改 Canvas，不改 XIA-56，不把 ViMax 的 Prompt replay 宣称为完整 Camera Tree 测试。P0 结果先交给用户审阅，再决定是否进入 P1。

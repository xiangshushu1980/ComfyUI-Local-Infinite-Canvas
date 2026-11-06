# XIA-59 P0 单轮文本对照

2026-11-06；基准 HEAD `8775737a9b8c625517b0702af3b0e37ec474713a`，工作区有其他任务的未提交修改。Linux/WSL；仅文本 LLM，未使用 GPU。三场景各四路独立调用，每路一次；`deepseek/deepseek-flash`、thinking off，完整命令和哈希见各样本 metadata。批次目录名含 offline，但正式请求均未设置 `--offline` 或 `PI_OFFLINE`；该名称仅为标签。短请求 JSON 事件确认实际 provider/model、thinking 和正常停止；正式请求为文本输出，服务端内部版本不可见。

先前 220 秒无输出保留在原 `p0/01-dialogue/native/`。新短请求在有无 offline 时均成功，因此不能归因于 offline，根因未确定。一次误设 `PI_OFFLINE=1` 的 02/native 调用被中断，证据保留在 [诊断目录](../../../diagnostics/20261106-interrupted-offline-02-native/)，未纳入批次。其余诊断在 [diagnostics](../../../diagnostics/)。

12/12 正式请求退出码为 0 且有输出；[机械报告](mechanical-report.json)显示 JSON 解析、文字出现及端点连续。该脚本不验证台词归属、正向时长、语义或视觉效果。人工对照见 [对话](review-01.md)、[交杯](review-02.md)、[并行离开](review-03.md)。

四路均为文本方法和共同 JSON 协议下的 Prompt replay，不是完整原项目框架或 ViMax Camera Tree。每个单元的 input-prompt.txt、raw-output.txt、stderr.txt、metadata.json 保留完整请求、输出、错误流、命令、耗时与 SHA。冻结源文件 13/13 哈希匹配 manifest。每组每场一次，不能推断胜率、稳定性或质量排名。

重要案例：对话场景 ViMax 的 2.5 秒镜头同时要求“停顿数秒”和完整回答；交杯场景 Director 给出了缺乏输入依据的角度及距离；并行场景四路均未清楚区分完整台词字段与说话中断，Toonflow 两镜重复完整句、ViMax 同时要求完整台词与句中停止。具体上下文及其余组别见逐场对照。台词与画面的可执行性尚未运行验证。

阶段门：P0 交用户审阅；未经用户确认不进入 P1。P2 视频需单独确认。未修改 Canvas 或 XIA-56，也未运行 ComfyUI/GPU。回滚本次新增目录和 runner 修改可按 Git 提交范围进行，不涉及其他工作区改动。

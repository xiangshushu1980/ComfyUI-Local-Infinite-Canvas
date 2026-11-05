# XIA-39 · 实验 A 单次 H3 多镜头生成：首次真实执行记录

日期：2026-11-05（UTC 提交 15:42:36 / 完成 15:44:19）。本次**实际执行** Gateway → ComfyUI H3 → 输出 MP4；**未由 Canvas Agent 客户端发起**，因为 `GET :17373/health` 返回 `hasCanvas:false, clients:0`。不与画布端到端成功混淆。

## 固定输入与执行
- 基准：[XIA-34](XIA-34-four-shot-benchmark.md) `case_id=XIA34-A-v1`，赤狐过溪，4 shots，目标 cut frames `[44,88,132]`，目标时间 `[1.8333,3.6667,5.5]` 秒。
- H3 Prompt：按 XIA-33 官方规则手动试写的三字段完整提示词（`integrated_multimodal_description`、`overall_soundscape`、`non_diegetic_music: N/A`），存于 `docs/planning/XIA-33-skill-reuse-adr-draft.md` §2.1；提交时原样使用（没有在线优化/自动规划）。
- 工作流 `video-h3-t2v-novdn`，经 `POST http://127.0.0.1:8190/v1/videos` 提交，字段：`model=video-h3-t2v-novdn`, `seconds=8`, `size=1024x576`, `ratio=16:9`, `params={"seed":34001,"steps":8,"cfg":1,"interpolation":"off"}`。
- Gateway v0.24.3，ComfyUI v0.44.0，RTX 4090 24 GB（实测推理过程显存峰值单点采样约 23,150 MiB；非精确峰值），H3 环境由该工作流声明可用，未额外安装节点/权重。
- Gateway task `task_b223c624-3e42-4061-b432-bba7472eb497`；Comfy prompt `b4229817-1154-4b78-ae27-aaac86fb8d1a`。状态 `completed`，9/9 steps，运行完成 UTC 15:44:19.893；约 103.5s 总 wall time，首帧耗时未记录。
- 产物：`comfyui-gateway/data/outputs/task_b223c624-3e42-4061-b432-bba7472eb497.mp4`；2,145,498 字节；SHA256 `60c647560cb29f934ceecb69add723c7c096738cc7d6330e6bc51024c9a40a45`。ffprobe：H.264 1024×576、24fps、8.000秒、192 frames；AAC stereo 32 kHz 音轨 8.000秒。
- 产物可通过同机 Gateway `http://127.0.0.1:8190/files/task_b223c624-3e42-4061-b432-bba7472eb497.mp4` 查看（远端其他设备需正确网络转发；不是互联网 URL）。

## 观测与不确定性
- 按 ffmpeg `select='gt(scene,0.30)',showinfo` 检测到**两处**明显转场：`1.916667s` (frame 46)，`3.750000s` (frame 90)，相对目标 44/88f 均延迟 `2f=0.08333s`。0.10 阈值还在 1.95833s 检出紧邻峰值，不应误记为额外独立镜头。
- 第 3 个目标切点 `5.500s` **在 0.10/0.30 场景变化阈值下均未检测到**，不能声称 4 个 hard cuts 全部成功。报告为 `observed_cut_frames:[46,90,null]`、`missing_cuts:1`。仅对两个可测切点：MAE `0.08333s`、max `0.08333s`，完整三切点平均误差 **N/A**（不可把缺失当 0）。
- 已提取并实际视觉检查 0–7 秒每秒一帧组成的 8 张静帧 contact sheet（远端 `/tmp/xia34-contact.png`）：赤狐、溪流、左右运动方向、苔藓石头及回头动作大体吻合；约 2 秒明显切为脚/半身近景，约 4 秒回到侧面中远景；末段狐狸回头。但这只是**抽帧人工查看**，未完整实时播放逐帧验证角色耳缺口、跨镜头脚部物理连续性和音轨质量。
- 提示词遵循部分成功：角色环境与主要运动保持，但模型没有稳定呈现要求的第 3 个硬切；后续须人工复核运动突变、音频连续性和狐狸身份细节，不用抽帧替代全片评分。
- 首次任务 completed，`attempts=1, failures=0`；这里的成功是“可播放文件生成成功”，不等于导演 4 镜头成功。无云计费；本地 GPU 电耗等成本未计量。
- 该实验**证明直接 Gateway H3 生成链路**，**不证明 Canvas Agent → 画布真实节点发起生成**；画布 Agent 连接状态是阻碍，需要浏览器画布客户端重新建立连接后另行验证。

## 复测和下一步
- 保存相同 prompt + seed + size + 模型，至少重复一次，验证切点/动作稳定性。
- 对照 XIA-40 分段生成+裁剪版，明确是否可获得稳定 44/44/44/60 帧成片。
- 不主动更改用户应用代码或重启服务；此文档为已有产物只读评估结果。
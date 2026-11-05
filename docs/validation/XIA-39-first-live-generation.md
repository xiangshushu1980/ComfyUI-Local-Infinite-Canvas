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
## 2026-11-05 实验 A2：叙事约束强化（仅 prompt 变化）
- 用户人工观察 A1：「有 3 个切镜头，但整片逻辑不完整；Shot 1 与 Shot 3 重复狐狸跳过水面」。记录为 A1 主要失败案例：**动作里程碑重复**，比切点数量更影响导演交付。此前 FFmpeg `scene>0.3` 只识别两个较强硬切，不应否认人工看到的第三次机位变化；两种口径需要分别记录。
- A2 控制变量：与 A1 同工作流 `video-h3-t2v-novdn`、1024×576、8.0s、24fps、8 steps、seed=34001、CFG=1、interpolation=off；唯一改变为导演提示词，见 `XIA-39-prompt-v2.txt`（SHA256 `db97a76bf73c7162382df09bc22c4190c9e0af6b9692c17e54a9d3598373ce0b`），明确四阶段 walk-stop / compress / only jump / land-look-back，并逐镜头禁止重复动作。
- Task `task_a85eec7e-e2d1-4d06-86d7-b8a364f6a3cb`，Comfy prompt `8a57d852-85ae-44df-b820-0c1f1e75e03e`；提交 15:54:47.895 UTC，完成 15:56:29.748 UTC，**101.9s**。输出 `comfyui-gateway/data/outputs/task_a85eec7e-e2d1-4d06-86d7-b8a364f6a3cb.mp4`；SHA256 `6203472cddb645a37b237a13c9666990068fa4da76b7e9c46aeb88b5594b70d`。ffprobe：H.264 1024×576 24fps 192 frames/8.0s，AAC 8.0s。
- FFmpeg `scene>0.10` 检出候选变化点 2.5833s、4.2083s、5.7500s（frame 62、101、138；按最近目标 cut44/88/132 配对时偏差 18/13/6 帧，即 0.750/0.542/0.250s）；候选 MAE 约 0.514s，**并非人工逐帧确定的硬切**。`scene>0.30` 仅检出 2.5833s；镜头数强依赖阈值及人工定义。
- 实际查看 0–7s 逐秒 8 帧图像：前半段狐靠近溪流，近景踩岩石，后半段回到侧景并转身回望。**没有看到可信的一次完整腾空跨溪**，无法判定四阶段动作达标。严格强调跳跃并没有修好叙事控制，反而可能挤掉关键动作；不应凭增加负面约束认为能实现稳定四镜头。
- A1/A2 均证明单次 H3 T2VA 链路可生成符合尺寸/时长的视频，但**不能保证镜头具有独立叙事功能、物理动作连续或帧级切点**。此后进入 XIA-40 分段生成 / 硬裁剪对照。两次均无人工完整音频回放和峰值 VRAM 连续日志，音轨质量评分暂缺；没有额外 API 服务费，硬件能耗未计。

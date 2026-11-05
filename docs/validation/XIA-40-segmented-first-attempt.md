# XIA-40 · 分段 H3 首次实验：热更新中断记录

日期：2026-11-05 15:59 UTC。状态：未完成四镜头拼接验收。当前阻碍是 Gateway 热重启，并非模型生成结果。

## 实验设计
- 对照 XIA-34 狐狸跨溪 8 秒四镜头基准，目标每镜头帧数 44/44/44/60 @ 24fps。
- 四个独立 4 秒 T2VA 任务，统一工作流 video-h3-t2v-novdn、1024x576、seed=34001、8 steps、CFG=1、interpolation=off。目标分别为接近并停止/蓄力/唯一跳跃/落地回望。
- 四个输入提示词分别存于 XIA-40-S1_approach-prompt.txt、S2_prepare、S3_jump、S4_land；请求参数存于 XIA-40-source-task-requests.json。
- 计划在每条源片完成且经人工抽帧确认后，分别选取 44/44/44/60 帧并用 ffmpeg concat；不能把 1.83s 当作 H3 原生生成任务长度；音轨策略与连续性需单独验收。

## 实际调度
| 段落 | Task ID | 最终状态 |
|---|---|---|
| S1 接近 | task_c4d9c24a-70bf-454a-93bb-4151c12865f9 | failed: 网关在任务完成前重启 |
| S2 蓄力 | task_c50e5cf3-43c3-4d88-9b6c-707dc0de852b | cancelled |
| S3 跨溪 | task_075c1cac-25ff-41fb-bf40-bbe0d715465f | cancelled |
| S4 落地 | task_2979a171-98b6-459e-9aff-348f08844813 | cancelled |

- 本地时间 23:59:31 四个任务提交至 Gateway 队列；23:59:33 Node --watch 重启 server.js。日志另见 23:57:01、23:59:53、00:00:45 的重启。S1 仅运行约 2s 即失败，后续排队任务全部取消，ComfyUI 队列清空。
- 远端在同一时间有其他工作正在编辑 PoseAtlas 集成：comfyui-gateway/src/pose-atlas.js 和 src/server.js 源码更新时间与 watch 重启相近；这是高度可能的直接触发因素，但未抓到逐文件 watch 触发事件。
- systemd unit 仍 active 且 NRestarts=0；原因是 node --watch 的子进程重启，并非 systemd 重启。没有完整四段源视频，也没有组合片，所以不能比较四镜头画质/叙事或宣称 XIA-40 完成。
- 未修改 ComfyUI 模型、服务或现有应用源码；不自动重试以免干扰其他并行开发。

## 继续实验条件
1. 先确认并行源码变动结束、Gateway 连续稳定运行，再用已留存 prompt/seed 复测四段。
2. 每条产物各自 ffprobe、SHA256、抽帧审核动作、镜头空间与角色一致性；挑选源 in/out，裁成 44/44/44/60 帧，最终 8s/192f。
3. 比较单次生成与分段策略的动作、身份、转场、音轨、耗时、生成失败次数；跨段一致性预计需要图像锚点，留待实际数据判断。
4. 如果要调整 node --watch、任务重启恢复或稳定执行 worker，需另行评审测试与回滚方案并取得实施授权。
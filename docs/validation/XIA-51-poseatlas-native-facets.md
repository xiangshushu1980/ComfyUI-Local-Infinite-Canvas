# XIA-51｜PoseAtlas 三图库原生导航与深度切换验收

2026-11-05，工作区 `/home/sean/projects/canvas-lab`。

## 上游数据事实

- Pose 1,439 entries / 288 groups，系列 `series`、分类 `category`、每组 angle；287 组五视角、一组四视角。
- Costume 1,407 entries，`category_key` 季节/场景和 `group_key` 服装类型。
- Portrait 1,499 entries，`section_key` 分区和 `hair_key` 发型。
- 深度参考只对 Pose 生效，`depth_file` 与 `depth_thumb` 有独立位置；初始本机深度图片为 0，原站禁止程序化批量下载。

## 实现

- Gateway `/api/poseatlas/facets` 从上游索引提供每图集两级原生筛选维度、动态组合计数；`/api/poseatlas/search` 支持 `first`/`second` 组合过滤和分页，姿势按 ID 聚合，搜索某角度仍能显示同组全部角度。
- `/api/poseatlas/asset/:index/:variant` 追加受索引约束的 `depth-thumb`/`depth-full`，不存在则返回 404。
- 深度单张下载通过显式点击按钮调用 `POST /api/poseatlas/depth/:index`；Gateway 验证是 Pose 索引后转发原插件 `/poseatlas/depth`，不接受客户端路径，禁止批量操作；后端会生成该张深度缩略图。
- Canvas Picker 提供图集切换、系列/季节/分区、类别/服装类型/发型的动态筛选和组合筛选，Pose 下可切换线稿/深度。深度资源不存在时明确提示、禁止插入，不把线稿假装成深度；显示按需下载按钮。
- 图片节点原有 `metadata.poseAtlas` 扩充 `render: line|depth` 字段，保留数据来源以便后续 Agent 使用。

## 实测

- API `facets?collection=pose&first=full_std` 返回 73 组，站姿 14 组；`search?collection=costume&first=summer&second=dress` 返回 39 项。
- Playwright 浏览器实际在隔离测试画布操作：姿势选择“标准全身 → 站姿”后显示匹配 14 组；深度模式资源未下载显示不可用和单张下载入口。
- Playwright 服饰选择“夏”显示 254 项，继续选择“连衣裙”显示 39 项。
- Playwright 肖像切换后显示分区/发型；“脸部”显示 893 项，发型下拉出现“短发 (433)”。
- 通过 `POST /api/poseatlas/depth/0` **单张**下载第一张 Pose 的深度资源，返回 `200 {ok:true,cached:false,bytes:104901}`；随后 `depth-full` HTTP 200 104901 bytes、`depth-thumb` HTTP 200 8635 bytes。非法索引深度下载返回 404。
- Playwright 切回 Pose → 深度，第一张深度缩略图显示，点击插入画布图片节点成功；其余未下载项显示“深度图尚未下载”。
- ComfyUI 真正执行 `PoseAtlasLoader(render=深度) → PreviewImage` 返回 `status_str=success`，900 × 1200。
- `node --test comfyui-gateway/test/pose-atlas.test.js`：6/6 通过；`git diff --check` 通过。
- `tsc --noEmit` 的全工程检查仍报仓库原有问题 `canvas-node.tsx(128,5): Property 'onViewImage' does not exist on type 'CanvasNodeProps'`，本次改动没有引入新增类型诊断。

## 边界

深度图仅在主动操作时逐张下载，不进行预取/批量抓取。图库素材只存本机 ComfyUI 工作目录，不再分发。未包含多语言切换、对原生侧栏像素级复刻或 Agent 自动调用（属于后续阶段）。

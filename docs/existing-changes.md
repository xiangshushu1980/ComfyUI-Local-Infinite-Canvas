# 初始化前已有 Gateway 修改（保留、未运行验证）

> 2026-10-31 基于 `git diff` 对比参考 commit；本记录只解释变更，不暗示其有效性。两个源文件保留为工作树未提交改动，不混入本轮文档提交。

- `comfyui-gateway/prompts/image-prompt-enhance.json`：将原 `TE_Qwen_Image_2_1_Prompt_Enhancer` 模板切换为 `CLIPLoader` + `QwenImage21_T2IPromptRewrite` / `QwenImage21_EditPromptRewrite` + `PreviewAny` 节点。
- `comfyui-gateway/src/prompt-optimizer.js`：依据文生图/图生图选择 `qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors` 或 `...pe_i2i...`；重绑 prompt、image_N 输入以及输出选择。
- **风险**：依赖 ComfyUI 上实际节点类、输入名及模型文件；可能与旧工作流产生兼容差异。
- **验收未完成**：模型/节点扫描、参数校验、接口单测、真实优化结果、回归。
- **保护规则**：代码变更不要混合进基础文档提交；后续专项检查再单独暂存/提交或回退。

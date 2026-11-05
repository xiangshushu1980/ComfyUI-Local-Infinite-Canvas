# H3 local rewrite LoRA

This is the default local H3 prompt optimization backend for Canvas Lab.

- Base text encoder: `qwen3.5_9b_int8_convrot.safetensors`, Qwen3.5-9B INT8 ConvRot, installed under ComfyUI `models/text_encoders`.
- Ref2VA adapter: `minimax-h3-prompt-rewriter-9b-ref2va_lora_rank32_bf16.safetensors`, under `models/loras`.
- T2VA/I2VA/L2VA/FL2VA adapter: `minimax-h3-prompt-rewriter-9b-fl2va_lora_rank32_bf16.safetensors`, under `models/loras`.
- Original adapter source: https://huggingface.co/nynxz/Qwen3.5-9B
- Base INT8 source: https://huggingface.co/beycanai/Qwen-LM (file Qwen3.5-9B_int8_convrot.safetensors, renamed locally).
- Training prompts: https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/blob/main/system_prompt.py
- Training format: https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/blob/main/infer.py

The `training-prompts.json` file retains the two exact LightX2V SFT system prompts; they are selected according to the H3 task. The server sends the complete chat-template text with `use_default_template: false`, greedy sampling, thinking disabled and adapter strength 1.0.

The implementation is `src/h3-lora-workflow.js`, used by `src/prompt-optimizer.js`. Reference pictures are padded without cropping, packed in order and labeled `<Picture N>`. Only still-image references are currently accepted by the existing Canvas Lab endpoint. Video and audio reference attachments are not implemented in this endpoint.

The local implementation shares ComfyUI GPU and RAM with H3 video generation. After each optimization, when the ComfyUI queue is idle, the gateway requests model unload and memory release. Set `H3_LORA_UNLOAD_AFTER_GENERATE=0` to preserve the encoder in GPU cache for repeated hot requests. A cold run can be slow; the optimizer waits up to six minutes. No model files are deleted.

The adapters are trained for English descriptive output. Chinese raw requests are accepted and rewritten, but selecting `language=zh` does not guarantee Chinese output; H3 section identifiers remain English.

Verified on Eric 2026-11-03: local T2VA and two-image Ref2VA through `POST /v1/prompts/optimize` both succeeded; T2VA ~4.3s and Ref2VA ~14.1s hot HTTP elapsed time. GPU model residency ~9.7GiB, 606MiB after idle automatic unload. These are observations, not universal latency guarantees.

Sanity test:
```sh
cd /home/sean/projects/canvas-lab/comfyui-gateway
node --test test/h3-lora-workflow.test.js
```

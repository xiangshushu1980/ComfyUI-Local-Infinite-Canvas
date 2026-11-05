import fs from "node:fs";
import path from "node:path";

const BASE = "qwen3.5_9b_int8_convrot.safetensors";
const REF = "minimax-h3-prompt-rewriter-9b-ref2va_lora_rank32_bf16.safetensors";
const FL = "minimax-h3-prompt-rewriter-9b-fl2va_lora_rank32_bf16.safetensors";
const TASKS = new Map([
  ["全参考模式(Reference to Video)", "REF2AV"],
  ["文生视频(T2VA)", "T2AV"],
  ["首帧图生视频(I2VA)", "I2AV"],
  ["首尾帧视频(FL2VA)", "FL2AV"],
  ["尾帧图生视频(L2VA)", "L2AV"],
]);

export const H3_LORA_MODELS = { base: BASE, ref: REF, fl: FL };

export function h3EffectiveDuration(seconds) {
  const frames = Math.ceil((24 * Number(seconds) - 5) / 17) * 17 + 5;
  return (frames / 24).toFixed(2);
}

function imageFilename(uploaded) {
  return uploaded.subfolder ? `${uploaded.subfolder}/${uploaded.name}` : uploaded.name;
}

function requiredImageCount(task) {
  return task === "I2AV" || task === "L2AV" ? 1 : task === "FL2AV" ? 2 : task === "REF2AV" ? 1 : 0;
}

function validateImages(task, images) {
  const min = requiredImageCount(task);
  if (images.length < min) throw new Error(`${task} 至少需要 ${min} 张参考图`);
  if (task === "T2AV" && images.length) throw new Error("T2VA 不支持参考图片，请选择图生视频或全参考模式");
  if (task === "I2AV" && images.length !== 1) throw new Error("I2VA 需要恰好 1 张首帧图");
  if (task === "L2AV" && images.length !== 1) throw new Error("L2VA 需要恰好 1 张尾帧图");
  if (task === "FL2AV" && images.length !== 2) throw new Error("FL2VA 需要恰好 2 张首尾帧图");
}

export function createH3LoraWorkflow({ rootDir, prompt, mode, duration, referenceNote = "", language = "en", images = [] }) {
  const task = TASKS.get(mode);
  if (!task) throw new Error(`不支持的 H3 任务类型: ${mode}`);
  validateImages(task, images);
  const training = JSON.parse(fs.readFileSync(path.join(rootDir, "prompts", "h3-lora", "training-prompts.json"), "utf8"));
  const system = task === "REF2AV" ? training.REF2AV_SYSTEM_PROMPT : training.SYSTEM_PROMPT;
  const effective = h3EffectiveDuration(duration);
  const refs = images.map((_, i) => {
    const label = `<Picture ${i + 1}>`;
    const role = task === "I2AV" || (task === "FL2AV" && i === 0)
      ? " — exact first frame at 0.00 seconds:"
      : task === "L2AV" || (task === "FL2AV" && i === 1)
        ? ` — exact final frame at ${effective}s:`
        : ":";
    return `${label}${role}\n<|vision_start|><|image_pad|><|vision_end|>`;
  }).join("\n");
  const heading = task === "REF2AV" ? "Ordered MiniMax-H3 references:\n" : "";
  const notes = String(referenceNote || "").trim();
  const userPrompt = notes ? `${prompt}\n\nReference notes: ${notes}` : String(prompt);
  // The model was trained with English sections; Chinese source dialogue stays unchanged.
  const langGuide = language === "zh" ? "\nOutput preference: Chinese descriptions when compatible with the required English field identifiers; preserve source dialogue verbatim." : "";
  const userText = `${heading}${refs}${refs ? "\n\n" : ""}Rewrite request:\ntask: ${task}\nresolution: 16:9\neffective_duration: ${effective}s\nraw_prompt: ${userPrompt}${langGuide}`;
  const fullPrompt = `<|im_start|>system\n${system}<|im_end|>\n<|im_start|>user\n${userText}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n`;
  const lora = task === "REF2AV" ? REF : FL;
  const workflow = {
    "1": { class_type: "CLIPLoader", inputs: { clip_name: BASE, type: "stable_diffusion" }, _meta: { title: "Qwen3.5 9B INT8" } },
    "2": { class_type: "LoadLoraTextEncoder", inputs: { clip: ["1", 0], "loras.0.lora_name": lora, "loras.0.strength": 1.0, "loras.0.enabled": true }, _meta: { title: "H3 rewrite LoRA" } },
    "3": { class_type: "TextGenerate", inputs: { clip: ["2", 0], prompt: fullPrompt, max_length: 3072, sampling_mode: "off", thinking: false, use_default_template: false, mtp: "off" }, _meta: { title: "H3 Rewrite" } },
    "4": { class_type: "PreviewAny", inputs: { source: ["3", 0] }, _meta: { title: "H3 rewrite result" } },
  };
  images.forEach((image, i) => {
    const id = String(9101 + i);
    workflow[id] = { class_type: "LoadImage", inputs: { image: imageFilename(image) } };
    const normalized = String(9301 + i);
    workflow[normalized] = { class_type: "ImageResizeKJv2", inputs: { image: [id, 0], width: 768, height: 768, upscale_method: "lanczos", keep_proportion: "pad", pad_color: "0, 0, 0", crop_position: "center", divisible_by: 8 } };
    if (i === 0) workflow["3"].inputs.image = [normalized, 0];
    else {
      const batch = String(9200 + i);
      workflow[batch] = { class_type: "ImageBatch", inputs: { image1: i === 1 ? ["9301", 0] : [String(9200 + i - 1), 0], image2: [normalized, 0] } };
      workflow["3"].inputs.image = [batch, 0];
    }
  });
  return workflow;
}

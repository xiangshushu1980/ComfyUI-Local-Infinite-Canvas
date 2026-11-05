import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createH3LoraWorkflow, h3EffectiveDuration } from "../src/h3-lora-workflow.js";
import { createPromptOptimizer } from "../src/prompt-optimizer.js";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("H3 local FL2VA uses trained prompts, greedy decoding and correct frame roles", () => {
  const workflow = createH3LoraWorkflow({
    rootDir, prompt: "woman jumps", mode: "首尾帧视频(FL2VA)", duration: 5,
    images: [{ name: "start.png" }, { name: "end.png" }],
  });
  assert.equal(workflow["2"].inputs["loras.0.strength"], 1);
  assert.match(workflow["2"].inputs["loras.0.lora_name"], /fl2va/);
  assert.equal(workflow["3"].inputs.sampling_mode, "off");
  assert.equal(workflow["3"].inputs.use_default_template, false);
  assert.match(workflow["3"].inputs.prompt, /<\\|im_start\\|>system/);
  assert.match(workflow["3"].inputs.prompt, /task: FL2AV/);
  assert.match(workflow["3"].inputs.prompt, /exact first frame at 0.00 seconds/);
  assert.match(workflow["3"].inputs.prompt, /exact final frame at/);
  assert.equal(workflow["3"].inputs.image[0], "9201");
  assert.equal(workflow["9301"].inputs.keep_proportion, "pad");
  assert.equal(workflow["9302"].inputs.keep_proportion, "pad");
});

test("H3 local Ref2VA uses reference adapter and ordered image placeholders", () => {
  const workflow = createH3LoraWorkflow({
    rootDir, prompt: "Replace person", mode: "全参考模式(Reference to Video)", duration: 10,
    images: [{ name: "a.png" }, { name: "b.png" }, { name: "c.png" }],
  });
  assert.match(workflow["2"].inputs["loras.0.lora_name"], /ref2va/);
  assert.match(workflow["3"].inputs.prompt, /subject_definitions:/);
  assert.match(workflow["3"].inputs.prompt, /task: REF2AV/);
  assert.equal(workflow["3"].inputs.prompt.split("<|image_pad|>").length - 1, 3);
  assert.deepEqual(workflow["3"].inputs.image, ["9202", 0]);
  assert.equal(h3EffectiveDuration(10), "10.13");
});

test("H3 local input constraints reject missing or unaligned references", () => {
  assert.throws(() => createH3LoraWorkflow({ rootDir, mode: "首尾帧视频(FL2VA)", duration: 5, prompt: "a" }), /至少需要 2/);
  assert.throws(() => createH3LoraWorkflow({ rootDir, mode: "文生视频(T2VA)", duration: 5, prompt: "a", images: [{ name: "a.png" }] }), /不支持参考图片/);
});

test("H3 local Gateway returns PreviewAny UI text", async () => {
  let submitted;
  const optimized = createPromptOptimizer({
    config: { rootDir },
    comfy: {
      async submit(w) { submitted = w; return { promptId: "test-lora" }; },
      async history() { return { status: { completed: true }, outputs: { "4": { ui: { text: ["integrated_multimodal_description: [Shot 1] A fox runs.\noverall_soundscape: natural ambience.\nnon_diegetic_music: none."] } } } }; },
    },
  });
  const result = await optimized.optimize({ engine: "local", prompt: "fox", mode: "文生视频(T2VA)", duration: 5 });
  assert.equal(result.provider, "local");
  assert.match(result.prompt, /integrated_multimodal_description:/);
  assert.equal(submitted["1"].class_type, "CLIPLoader");
  assert.equal(submitted["4"].class_type, "PreviewAny");
});

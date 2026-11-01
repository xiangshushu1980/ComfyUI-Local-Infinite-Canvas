import assert from "node:assert/strict";
import test from "node:test";

import { mergeGpuSnapshot, nvidiaSmiCandidates } from "../src/system-stats.js";

const gpu = [{ index: 0, name: "NVIDIA GeForce RTX 4080 SUPER", memoryUsedMb: 18900, memoryTotalMb: 32768, utilization: 99, temperature: 78 }];

test("uses the WSL NVIDIA utility on Linux without trying Windows paths", () => {
  assert.deepEqual(nvidiaSmiCandidates({ platform: "linux", env: { SystemRoot: "C:\\Windows" } }), [
    "nvidia-smi",
    "/usr/lib/wsl/lib/nvidia-smi",
  ]);
});

test("keeps the Windows NVIDIA utility fallback on Windows", () => {
  assert.deepEqual(nvidiaSmiCandidates({ platform: "win32", env: { SystemRoot: "D:\\Windows" } }), [
    "nvidia-smi",
    "D:\\Windows\\System32\\nvidia-smi.exe",
  ]);
});

test("keeps the last GPU reading when nvidia-smi fails under load", () => {
  const first = mergeGpuSnapshot(null, { gpu, gpuError: null });
  assert.equal(first.gpuStale, false);
  assert.deepEqual(first.gpu, gpu);

  const next = mergeGpuSnapshot(gpu, { gpu: [], gpuError: "timeout" });
  assert.equal(next.gpuStale, true);
  assert.deepEqual(next.gpu, gpu);
  assert.equal(next.gpuError, "timeout");

  const recovered = mergeGpuSnapshot(gpu, { gpu, gpuError: null });
  assert.equal(recovered.gpuStale, false);
});

test("reports an empty GPU list when nothing has ever been read", () => {
  const empty = mergeGpuSnapshot(null, { gpu: [], gpuError: "nvidia-smi not found" });
  assert.equal(empty.gpuStale, false);
  assert.deepEqual(empty.gpu, []);
  assert.match(empty.gpuError, /nvidia-smi/);
});

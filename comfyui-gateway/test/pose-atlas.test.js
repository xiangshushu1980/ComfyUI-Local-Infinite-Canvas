import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { after, test } from "node:test";
import { createPoseAtlasCatalog } from "../src/pose-atlas.js";

const root = mkdtempSync(path.join(tmpdir(), "pose-atlas-test-"));
const atlas = path.join(root, "custom_nodes/ComfyUI-PoseAtlas/web/atlas");
mkdirSync(path.join(atlas, "thumbs"), { recursive: true });
mkdirSync(path.join(atlas, "img"), { recursive: true });
writeFileSync(path.join(atlas, "index.json"), JSON.stringify({
  series: [{ key: "standard", short: "标准", poseCount: 2 }],
  categoriesBySeries: { standard: [{ name: "站姿", count: 2 }] },
  costumeCategories: [{ key: "summer", name: "夏", count: 1 }],
  costumeGroups: [{ key: "dress", name: "连衣裙", count: 1 }],
  portraitSections: [{ key: "face", name: "脸部", count: 1 }],
  portraitHairs: [{ key: "short", name: "短发", count: 1 }],
  entries: [{ collection: "pose", id: "P001", label: "P001 敬礼 正面", series: "standard", category: "站姿", angle: "front", depth_file: "depth/img/one.png", thumb: "thumbs/one.jpg", file: "img/one.png" },
    { collection: "portrait", id: "F001", label: "F001 portrait", section_key: "face", hair_key: "short", thumb: "thumbs/two.jpg", file: "img/two.png" },
    { collection: "pose", id: "BAD", label: "unsafe", series: "standard", category: "站姿", thumb: "../../outside", file: "../../outside" },
    { collection: "pose", id: "P001", label: "P001 敬礼 侧面", series: "standard", category: "站姿", angle: "side", depth_file: "depth/img/one_side.png", thumb: "thumbs/one.jpg", file: "img/one.png" },
    { collection: "costume", id: "C001", label: "summer dress", category_key: "summer", group_key: "dress", thumb: "thumbs/one.jpg", file: "img/one.png" }],
}));
writeFileSync(path.join(atlas, "thumbs/one.jpg"), "thumb");
writeFileSync(path.join(atlas, "img/one.png"), "full");
after(() => rmSync(root, { recursive: true, force: true }));
const catalog = createPoseAtlasCatalog(() => root);

test("search handles collection, keyword, pagination, and availability", () => {
  assert.equal(catalog.search({ collection: "pose" }).total, 3);
  const result = catalog.search({ collection: "pose", q: "敬礼", page: 1, limit: 1 });
  assert.equal(result.total, 2);
  assert.equal(result.items[0].fullAvailable, true);
  assert.equal(catalog.search({ collection: "portrait" }).total, 1);
  assert.equal(catalog.search({ collection: "pose", q: "missed" }).total, 0);
});
test("grouped pose search keeps all viewpoints and pages groups", () => {
  const grouped = catalog.search({ collection: "pose", q: "敬礼", grouped: "1" });
  assert.equal(grouped.total, 1);
  assert.equal(grouped.items[0].id, "P001");
  assert.equal(grouped.items[0].variants.length, 2);
  assert.equal(grouped.items[0].variants[0].index, 0);
  assert.equal(catalog.search({ collection: "pose", grouped: "1", limit: 1, page: 2 }).items.length, 1);
  assert.equal(catalog.search({ collection: "portrait", grouped: "1" }).items[0].id, "F001");
});
test("asset routes reject unknown ordinals and path traversal", () => {
  assert.equal(catalog.asset(0, "full"), path.join(atlas, "img/one.png"));
  assert.equal(catalog.asset(0, "thumb"), path.join(atlas, "thumbs/one.jpg"));
  assert.equal(catalog.asset(2, "full"), null);
  assert.equal(catalog.asset("../../etc/passwd", "full"), null);
  assert.equal(catalog.asset(9999, "full"), null);
  assert.equal(catalog.asset(0, "invalid"), null);
});

test("native two-level facets honor contextual counts and independent collections", () => {
  const pose = catalog.facets({ collection: "pose", first: "standard" });
  assert.equal(pose.firstLabel, "系列");
  assert.equal(pose.total, 2);
  assert.equal(pose.second.find(f => f.key === "站姿").count, 2);
  const costume = catalog.facets({ collection: "costume", first: "summer" });
  assert.equal(costume.second.find(f => f.key === "dress").count, 1);
  assert.equal(catalog.search({ collection: "costume", first: "summer", second: "dress" }).total, 1);
  const portrait = catalog.facets({ collection: "portrait", first: "face" });
  assert.equal(portrait.second.find(f => f.key === "short").count, 1);
  assert.equal(catalog.search({ collection: "portrait", first: "face", second: "short" }).total, 1);
});
test("grouped angle search preserves full pose variant group", () => {
  const matches = catalog.search({ collection: "pose", grouped: "1", q: "侧面" });
  assert.equal(matches.total, 1);
  assert.equal(matches.items[0].variants.length, 2);
  assert.deepEqual(matches.items[0].variants.map(e => e.angle), ["front", "side"]);
});
test("depth is explicit and only allowed for pose entries", () => {
  assert.equal(catalog.depthStem(0), "one");
  assert.equal(catalog.depthStem(1), null);
  assert.equal(catalog.asset(0, "depth-full"), null);
  assert.equal(catalog.asset(1, "depth-full"), null);
  assert.equal(catalog.depthStem(99999), null);
});

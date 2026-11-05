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
  entries: [{ collection: "pose", id: "P001", label: "P001 敬礼 正面", thumb: "thumbs/one.jpg", file: "img/one.png" },
    { collection: "portrait", id: "F001", label: "F001 portrait", thumb: "thumbs/two.jpg", file: "img/two.png" },
    { collection: "pose", id: "BAD", label: "unsafe", thumb: "../../outside", file: "../../outside" }],
}));
writeFileSync(path.join(atlas, "thumbs/one.jpg"), "thumb");
writeFileSync(path.join(atlas, "img/one.png"), "full");
after(() => rmSync(root, { recursive: true, force: true }));
const catalog = createPoseAtlasCatalog(() => root);

test("search handles collection, keyword, pagination, and availability", () => {
  assert.equal(catalog.search({ collection: "pose" }).total, 2);
  const result = catalog.search({ collection: "pose", q: "敬礼", page: 1, limit: 1 });
  assert.equal(result.total, 1);
  assert.equal(result.items[0].fullAvailable, true);
  assert.equal(catalog.search({ collection: "portrait" }).total, 1);
  assert.equal(catalog.search({ collection: "pose", q: "missed" }).total, 0);
});
test("asset routes reject unknown ordinals and path traversal", () => {
  assert.equal(catalog.asset(0, "full"), path.join(atlas, "img/one.png"));
  assert.equal(catalog.asset(0, "thumb"), path.join(atlas, "thumbs/one.jpg"));
  assert.equal(catalog.asset(2, "full"), null);
  assert.equal(catalog.asset("../../etc/passwd", "full"), null);
  assert.equal(catalog.asset(9999, "full"), null);
  assert.equal(catalog.asset(0, "invalid"), null);
});

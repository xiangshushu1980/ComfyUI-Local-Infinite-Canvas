import fs from "node:fs";
import path from "node:path";

// Serve user-installed local reference assets, never ship them with Canvas Lab.
// Index ordinals are validated against the loaded catalog; clients cannot send paths.
export function createPoseAtlasCatalog(getComfyRoot) {
  let cache = null;
  function catalog() {
    const root = getComfyRoot();
    if (!root) return null;
    const dir = path.join(root, "custom_nodes", "ComfyUI-PoseAtlas", "web", "atlas");
    const indexPath = path.join(dir, "index.json");
    if (!fs.existsSync(indexPath)) return null;
    const stat = fs.statSync(indexPath);
    if (!cache || cache.indexPath !== indexPath || cache.mtimeMs !== stat.mtimeMs) {
      const data = JSON.parse(fs.readFileSync(indexPath, "utf8"));
      if (!Array.isArray(data.entries)) throw new Error("PoseAtlas index has no entries");
      cache = { indexPath, mtimeMs: stat.mtimeMs, dir, entries: data.entries };
    }
    return cache;
  }
  function search({ collection = "pose", q = "", page = 1, limit = 30 } = {}) {
    const data = catalog();
    if (!data) return null;
    const selected = ["pose", "costume", "portrait"].includes(collection) ? collection : "pose";
    const query = String(q).trim().toLocaleLowerCase();
    const safePage = Math.max(1, Math.floor(Number(page) || 1));
    const safeLimit = Math.min(60, Math.max(1, Math.floor(Number(limit) || 30)));
    const results = [];
    data.entries.forEach((entry, index) => {
      if ((entry.collection || "pose") !== selected) return;
      if (query && ![entry.label, entry.zh, entry.en, entry.ja, entry.id, entry.category, entry.series_name,
        ...(Object.values(entry.labels || {}).flatMap(v => typeof v === "string" ? [v] : []))]
        .some(value => String(value || "").toLocaleLowerCase().includes(query))) return;
      results.push({ index, id: entry.id, label: entry.label, collection: selected,
        thumbAvailable: existsAsset(data.dir, entry.thumb), fullAvailable: existsAsset(data.dir, entry.file) });
    });
    return { total: results.length, page: safePage, limit: safeLimit,
      items: results.slice((safePage - 1) * safeLimit, safePage * safeLimit) };
  }
  function asset(index, variant = "thumb") {
    const data = catalog();
    if (!data) return null;
    const n = Number(index);
    if (!Number.isSafeInteger(n) || n < 0 || n >= data.entries.length) return null;
    const entry = data.entries[n];
    const rel = variant === "full" ? entry.file : variant === "thumb" ? entry.thumb : null;
    if (!rel) return null;
    const file = assetPath(data.dir, rel);
    return file && fs.existsSync(file) && fs.statSync(file).isFile() ? file : null;
  }
  return { search, asset };
}
function assetPath(dir, rel) {
  if (typeof rel !== "string" || !rel || path.isAbsolute(rel)) return null;
  const candidate = path.resolve(dir, rel);
  return candidate.startsWith(path.resolve(dir) + path.sep) ? candidate : null;
}
function existsAsset(dir, rel) {
  const file = assetPath(dir, rel);
  return Boolean(file && fs.existsSync(file));
}

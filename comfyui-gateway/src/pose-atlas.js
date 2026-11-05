import fs from "node:fs";
import path from "node:path";

// Assets remain in the user's local ComfyUI directory; never redistribute them.
// Client-facing IDs are index ordinals, never file paths.
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
      cache = { indexPath, mtimeMs: stat.mtimeMs, dir, ...data };
    }
    return cache;
  }
  const collections = ["pose", "costume", "portrait"];
  const facetKeys = {
    pose: ["series", "category"],
    costume: ["category_key", "group_key"],
    portrait: ["section_key", "hair_key"],
  };
  function scoped(data, coll, q, first, second) {
    const [firstKey, secondKey] = facetKeys[coll];
    const query = String(q || "").trim().toLocaleLowerCase();
    return data.entries.filter(e => {
      if (e.collection !== coll) return false;
      if (first && e[firstKey] !== first) return false;
      if (second && e[secondKey] !== second) return false;
      return !query || [
        e.label, e.zh, e.en, e.ja, e.id, e.no, e.category, e.series_name,
        e.group, e.hair, e.section, e.color,
        ...Object.values(e.labels || {}).filter(v => typeof v === "string"),
      ].some(value => String(value || "").toLocaleLowerCase().includes(query));
    });
  }
  function facets({ collection = "pose", q = "", first = "", second = "" } = {}) {
    const data = catalog();
    if (!data) return null;
    const coll = collections.includes(collection) ? collection : "pose";
    const [key1, key2] = facetKeys[coll];
    const lists = coll === "pose"
      ? [
          data.series.map(s => ({ key: s.key, label: s.short_tri?.zh || s.short || s.name })),
          Object.values(data.categoriesBySeries).flat().filter((entry, idx, a) => a.findIndex(x => x.name === entry.name) === idx)
            .map(e => ({ key: e.name, label: e.name_tri?.zh || e.name })),
        ]
      : coll === "costume"
        ? [
            data.costumeCategories.map(e => ({ key: e.key, label: e.name_tri?.zh || e.name })),
            data.costumeGroups.map(e => ({ key: e.key, label: e.name_tri?.zh || e.name })),
          ]
        : [
            data.portraitSections.map(e => ({ key: e.key, label: e.name_tri?.zh || e.name })),
            data.portraitHairs.map(e => ({ key: e.key, label: e.name_tri?.zh || e.name })),
          ];
    const uniqueCount = entries => coll === "pose" ? new Set(entries.map(e => e.id)).size : entries.length;
    const makeOptions = (list, type) => list.map(option => {
      const matches = scoped(data, coll, q, type === 1 ? option.key : first, type === 2 ? option.key : second);
      return { ...option, count: uniqueCount(matches) };
    });
    return { first: makeOptions(lists[0], 1), second: makeOptions(lists[1], 2),
      total: uniqueCount(scoped(data, coll, q, first, second)),
      firstLabel: coll === "pose" ? "系列" : coll === "costume" ? "季节 / 场景" : "分区",
      secondLabel: coll === "pose" ? "姿势类别" : coll === "costume" ? "服装类型" : "发型" };
  }
  function search({ collection = "pose", q = "", page = 1, limit = 30, grouped = false, first = "", second = "" } = {}) {
    const data = catalog();
    if (!data) return null;
    const selected = collections.includes(collection) ? collection : "pose";
    const safePage = Math.max(1, Math.floor(Number(page) || 1));
    const safeLimit = Math.min(60, Math.max(1, Math.floor(Number(limit) || 30)));
    const matched = scoped(data, selected, q, first, second);
    const indices = new Map(data.entries.map((entry, i) => [entry, i]));
    const view = entry => {
      const index = indices.get(entry);
      return { index, id: entry.id, label: entry.label, collection: selected,
        angle: entry.angle, angleName: entry.angle_name || entry.angle || "",
        thumbAvailable: existsAsset(data.dir, entry.thumb), fullAvailable: existsAsset(data.dir, entry.file),
        depthThumbAvailable: existsAsset(data.dir, entry.depth_thumb),
        depthFullAvailable: existsAsset(data.dir, entry.depth_file) };
    };
    if (selected === "pose" && (grouped === "1" || grouped === "true")) {
      const groups = new Map();
      const matchedIds = new Set(matched.map(entry => entry.id));
      // Query on a specific angle must not hide the other angles of the pose.
      for (const entry of scoped(data, selected, "", first, second)) {
        if (!matchedIds.has(entry.id)) continue;
        if (!groups.has(entry.id)) groups.set(entry.id, {
          id: entry.id, label: `${entry.no || entry.id} ${entry.zh || entry.id}`,
          category: entry.category || "", variants: [],
        });
        groups.get(entry.id).variants.push(view(entry));
      }
      const items = Array.from(groups.values());
      return { total: items.length, page: safePage, limit: safeLimit,
        items: items.slice((safePage - 1) * safeLimit, safePage * safeLimit) };
    }
    const results = matched.map(view);
    return { total: results.length, page: safePage, limit: safeLimit,
      items: results.slice((safePage - 1) * safeLimit, safePage * safeLimit) };
  }
  function entryAt(index) {
    const data = catalog();
    const n = Number(index);
    if (!data || !Number.isSafeInteger(n) || n < 0 || n >= data.entries.length) return null;
    return data.entries[n];
  }
  function depthStem(index) {
    const entry = entryAt(index);
    if (!entry || entry.collection !== "pose" || !entry.depth_file) return null;
    return path.basename(entry.depth_file, ".png");
  }
  function asset(index, variant = "thumb") {
    const data = catalog();
    const entry = entryAt(index);
    if (!data || !entry) return null;
    const rel = {
      full: entry.file, thumb: entry.thumb,
      "depth-full": entry.collection === "pose" ? entry.depth_file : null,
      "depth-thumb": entry.collection === "pose" ? entry.depth_thumb : null,
    }[variant];
    if (!rel) return null;
    const file = assetPath(data.dir, rel);
    return file && fs.existsSync(file) && fs.statSync(file).isFile() ? file : null;
  }
  return { search, facets, asset, depthStem };
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

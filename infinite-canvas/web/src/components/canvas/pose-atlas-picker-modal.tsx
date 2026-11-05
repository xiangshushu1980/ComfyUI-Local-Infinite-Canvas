import { useEffect, useMemo, useState } from "react";
import { Button, Empty, Input, Modal, Pagination, Segmented, Select, Spin, message } from "antd";
import { localGatewayRoot } from "@/services/api/image";
import type { AiConfig } from "@/stores/use-config-store";

export type PoseAtlasSelection = {
    index: number;
    id: string;
    label: string;
    collection: "pose" | "costume" | "portrait";
    render: "line" | "depth";
    dataUrl: string;
};
type Item = Omit<PoseAtlasSelection, "render" | "dataUrl"> & {
    angle?: string;
    angleName?: string;
    thumbAvailable: boolean;
    fullAvailable: boolean;
    depthThumbAvailable?: boolean;
    depthFullAvailable?: boolean;
};
type PoseGroup = { id: string; label: string; category: string; variants: Item[] };
type SearchResult = { ok: boolean; total: number; items: Array<Item | PoseGroup> };
type Facet = { key: string; label: string; count: number };
type Facets = { ok: boolean; first: Facet[]; second: Facet[]; firstLabel: string; secondLabel: string };
const pageSize = 30;

function blobAsDataUrl(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = () => reject(reader.error || new Error("图片读取失败"));
        reader.readAsDataURL(blob);
    });
}

export function PoseAtlasPickerModal({
    open, config, onClose, onInsert, canReplace,
}: {
    open: boolean;
    config: AiConfig;
    onClose: () => void;
    onInsert: (selection: PoseAtlasSelection, replace: boolean) => Promise<void>;
    canReplace: boolean;
}) {
    const root = useMemo(() => localGatewayRoot(config.baseUrl), [config.baseUrl]);
    const [collection, setCollection] = useState<"pose" | "costume" | "portrait">("pose");
    const [query, setQuery] = useState("");
    const [page, setPage] = useState(1);
    const [first, setFirst] = useState("");
    const [second, setSecond] = useState("");
    const [render, setRender] = useState<"line" | "depth">("line");
    const [facets, setFacets] = useState<Facets | null>(null);
    const [results, setResults] = useState<SearchResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [inserting, setInserting] = useState<number | null>(null);
    const [downloading, setDownloading] = useState<number | null>(null);
    const [replace, setReplace] = useState(false);
    const [error, setError] = useState("");
    const [selectedAngles, setSelectedAngles] = useState<Record<string, number>>({});
    const [revision, setRevision] = useState(0);

    useEffect(() => {
        if (!open || !root) return;
        const controller = new AbortController();
        const params = new URLSearchParams({ collection, q: query, first, second });
        void fetch(`${root}/api/poseatlas/facets?${params}`, { signal: controller.signal })
            .then(async response => {
                if (!response.ok) throw new Error("分类目录不可用");
                return response.json() as Promise<Facets>;
            })
            .then(setFacets)
            .catch(() => { if (!controller.signal.aborted) setFacets(null); });
        return () => controller.abort();
    }, [open, root, collection, query, first, second]);

    useEffect(() => {
        if (!open || !root) return;
        const controller = new AbortController();
        setLoading(true);
        setError("");
        const params = new URLSearchParams({ collection, q: query, first, second, page: String(page), limit: String(pageSize), grouped: "1" });
        void fetch(`${root}/api/poseatlas/search?${params}`, { signal: controller.signal })
            .then(async response => {
                if (!response.ok) throw new Error(response.status === 404 ? "没有找到本机 PoseAtlas 图库" : `图库请求失败 (${response.status})`);
                return response.json() as Promise<SearchResult>;
            })
            .then(setResults)
            .catch(cause => { if (!controller.signal.aborted) { setError(cause instanceof Error ? cause.message : String(cause)); setResults(null); } })
            .finally(() => { if (!controller.signal.aborted) setLoading(false); });
        return () => controller.abort();
    }, [open, root, collection, query, first, second, page, revision]);

    const chooseCollection = (next: typeof collection) => {
        setCollection(next);
        setPage(1);
        setFirst("");
        setSecond("");
        setSelectedAngles({});
        setRender("line");
        setFacets(null);
        setResults(null);
    };
    const insert = async (item: Item) => {
        const depth = collection === "pose" && render === "depth";
        if (!root || (depth ? !item.depthFullAvailable : !item.fullAvailable) || inserting !== null) return;
        setInserting(item.index);
        try {
            const variant = depth ? "depth-full" : "full";
            const response = await fetch(`${root}/api/poseatlas/asset/${item.index}/${variant}`);
            if (!response.ok) throw new Error("当前图片不可用，请先下载深度原图");
            const dataUrl = await blobAsDataUrl(await response.blob());
            await onInsert({ index: item.index, id: item.id, label: item.label, collection: item.collection,
                render: depth ? "depth" : "line", dataUrl }, replace && canReplace);
            onClose();
        } catch (cause) {
            message.error(cause instanceof Error ? cause.message : "插入失败");
        } finally {
            setInserting(null);
        }
    };
    const downloadDepth = async (item: Item) => {
        if (!root || downloading !== null || inserting !== null) return;
        setDownloading(item.index);
        try {
            // Explicit per-image action; only one depth image is requested by a click.
            const response = await fetch(`${root}/api/poseatlas/depth/${item.index}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
            const result = await response.json() as { ok?: boolean; error?: string };
            if (!response.ok || !result.ok) throw new Error(result.error || "深度原图下载失败");
            message.success("已下载该方向深度原图");
            setRevision(value => value + 1);
        } catch (cause) {
            message.error(cause instanceof Error ? cause.message : "深度原图下载失败");
        } finally {
            setDownloading(null);
        }
    };

    return (
        <Modal title="PoseAtlas · 参考图库" open={open} onCancel={onClose} footer={null} width={1040} destroyOnHidden>
            {!root ? <Empty description="请先使用 Canvas Lab 本地 ComfyUI Gateway" /> : (
                <div className="space-y-3">
                    <div className="flex flex-wrap items-center gap-3">
                        <Segmented value={collection} onChange={value => chooseCollection(value as typeof collection)}
                            options={[{ label: "姿势", value: "pose" }, { label: "服饰", value: "costume" }, { label: "肖像", value: "portrait" }]} />
                        <Input.Search className="max-w-sm flex-1" placeholder="搜索名称、编号、类别" value={query}
                            onChange={event => { setQuery(event.target.value); setPage(1); }} allowClear />
                        <span className="text-xs text-stone-500">{results ? `匹配 ${results.total} ${collection === "pose" ? "组姿势" : "项"}` : ""}</span>
                        {canReplace ? <Segmented value={replace ? "replace" : "insert"} onChange={mode => setReplace(mode === "replace")}
                            options={[{ label: "新建图片节点", value: "insert" }, { label: "替换选中图片", value: "replace" }]} /> : null}
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                        {facets ? (
                            <>
                                <label className="text-xs text-stone-500">{facets.firstLabel}</label>
                                <Select aria-label={facets.firstLabel} size="small" className="min-w-40" value={first}
                                    onChange={value => { setFirst(value); setSecond(""); setPage(1); }}
                                    options={[{ label: "全部", value: "" }, ...facets.first.map(f => ({ label: `${f.label} (${f.count})`, value: f.key }))]} />
                                <label className="text-xs text-stone-500">{facets.secondLabel}</label>
                                <Select aria-label={facets.secondLabel} size="small" className="min-w-40" value={second}
                                    onChange={value => { setSecond(value); setPage(1); }}
                                    options={[{ label: "全部", value: "" }, ...facets.second.filter(f => f.count > 0 || f.key === second).map(f => ({
                                        label: `${f.label} (${f.count})`, value: f.key,
                                    }))]} />
                            </>
                        ) : null}
                        {collection === "pose" ? (
                            <Segmented size="small" aria-label="渲染方式" value={render} onChange={value => setRender(value as typeof render)}
                                options={[{ label: "线稿", value: "line" }, { label: "深度", value: "depth" }]} />
                        ) : null}
                        {(first || second || query) ? <Button size="small" onClick={() => { setFirst(""); setSecond(""); setQuery(""); setPage(1); }}>清除筛选</Button> : null}
                    </div>
                    {render === "depth" && collection === "pose" ? (
                        <p className="text-xs text-amber-600">深度原图未批量下载。每张卡片可单独点击“下载此方向深度图”，下载成功后才能插入画布；不会自动替换为线稿。</p>
                    ) : null}
                    {error ? <div role="alert" className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
                    <Spin spinning={loading}>
                        <div className="grid max-h-[53vh] min-h-[280px] grid-cols-3 gap-3 overflow-y-auto sm:grid-cols-5">
                            {results?.items.map(entry => {
                                const isGroup = "variants" in entry;
                                const variants = isGroup ? entry.variants : [entry];
                                const selected = variants.find(item => item.index === selectedAngles[entry.id]) || variants[0];
                                const depth = collection === "pose" && render === "depth";
                                const available = depth ? Boolean(selected.depthFullAvailable) : selected.fullAvailable;
                                const thumb = depth ? (selected.depthThumbAvailable ? "depth-thumb" : selected.depthFullAvailable ? "depth-full" : null) : selected.thumbAvailable ? "thumb" : null;
                                return (
                                    <div key={entry.id + (isGroup ? "" : `-${selected.index}`)}
                                        className="overflow-hidden rounded-lg border bg-white dark:bg-stone-900">
                                        <button type="button" disabled={!available || inserting !== null}
                                            onClick={() => void insert(selected)} title={available ? `插入「${selected.label}」` : "图片尚不可用"}
                                            className="w-full text-left transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-60 dark:hover:bg-stone-800">
                                            <div className="relative aspect-[3/4] bg-stone-100 dark:bg-stone-800">
                                                {thumb ? <img loading="lazy" src={`${root}/api/poseatlas/asset/${selected.index}/${thumb}`} alt={selected.label}
                                                    className="h-full w-full object-contain" /> :
                                                    <div className="grid h-full place-items-center p-2 text-center text-xs text-stone-500">
                                                        {depth ? "深度图尚未下载" : "缩略图缺失"}
                                                    </div>}
                                                {inserting === selected.index ? <div className="absolute inset-0 grid place-items-center bg-black/30"><Spin /></div> : null}
                                            </div>
                                            <div className="line-clamp-2 min-h-10 p-2 text-xs" title={selected.label}>{isGroup ? entry.label : selected.label}</div>
                                        </button>
                                        {isGroup && variants.length > 1 ? (
                                            <div className="flex flex-wrap gap-1 border-t p-1.5" aria-label={`${entry.label} 方向`}>
                                                {variants.map(variant => (
                                                    <button type="button" key={variant.index} disabled={!variant.thumbAvailable}
                                                        aria-pressed={selected.index === variant.index}
                                                        title={variant.label}
                                                        onClick={() => setSelectedAngles(prev => ({ ...prev, [entry.id]: variant.index }))}
                                                        className={`rounded px-1.5 py-1 text-[11px] transition ${selected.index === variant.index
                                                            ? "bg-blue-600 text-white" : "bg-stone-100 text-stone-700 hover:bg-blue-100 dark:bg-stone-700 dark:text-stone-200"}`}>
                                                        {variant.angleName || variant.angle || "方向"}
                                                    </button>
                                                ))}
                                            </div>
                                        ) : null}
                                        {depth && !selected.depthFullAvailable ? (
                                            <Button size="small" block loading={downloading === selected.index} disabled={downloading !== null}
                                                onClick={() => void downloadDepth(selected)}>下载此方向深度图</Button>
                                        ) : null}
                                    </div>
                                );
                            })}
                        </div>
                    </Spin>
                    <div className="flex items-center justify-between gap-2">
                        <span className="text-xs text-stone-500">选择角度后点击主图插入，图库原始素材不随项目分发。</span>
                        <Pagination simple current={page} total={results?.total || 0} pageSize={pageSize} onChange={setPage} />
                    </div>
                    <div className="flex justify-end"><Button onClick={onClose}>关闭</Button></div>
                </div>
            )}
        </Modal>
    );
}

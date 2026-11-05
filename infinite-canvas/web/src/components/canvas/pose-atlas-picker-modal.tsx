import { useEffect, useMemo, useState } from "react";
import { Button, Empty, Input, Modal, Pagination, Segmented, Spin, message } from "antd";
import { localGatewayRoot } from "@/services/api/image";
import type { AiConfig } from "@/stores/use-config-store";

export type PoseAtlasSelection = {
    index: number;
    id: string;
    label: string;
    collection: "pose" | "costume" | "portrait";
    dataUrl: string;
};

type Item = Omit<PoseAtlasSelection, "dataUrl"> & {
    angle?: string;
    angleName?: string;
    thumbAvailable: boolean;
    fullAvailable: boolean;
};
type PoseGroup = { id: string; label: string; category: string; variants: Item[] };
type SearchResult = { ok: boolean; total: number; items: Array<Item | PoseGroup> };
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
    const [results, setResults] = useState<SearchResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [inserting, setInserting] = useState<number | null>(null);
    const [replace, setReplace] = useState(false);
    const [error, setError] = useState("");
    const [selectedAngles, setSelectedAngles] = useState<Record<string, number>>({});

    useEffect(() => {
        if (!open || !root) return;
        const controller = new AbortController();
        setLoading(true);
        setError("");
        const params = new URLSearchParams({ collection, q: query, page: String(page), limit: String(pageSize), grouped: "1" });
        void fetch(`${root}/api/poseatlas/search?${params}`, { signal: controller.signal })
            .then(async response => {
                if (!response.ok) throw new Error(response.status === 404 ? "没有找到本机 PoseAtlas 图库" : `图库请求失败 (${response.status})`);
                return response.json() as Promise<SearchResult>;
            })
            .then(data => setResults(data))
            .catch(cause => { if (!controller.signal.aborted) { setError(cause instanceof Error ? cause.message : String(cause)); setResults(null); } })
            .finally(() => { if (!controller.signal.aborted) setLoading(false); });
        return () => controller.abort();
    }, [open, root, collection, query, page]);

    const insert = async (item: Item) => {
        if (!root || !item.fullAvailable || inserting !== null) return;
        setInserting(item.index);
        try {
            const response = await fetch(`${root}/api/poseatlas/asset/${item.index}/full`);
            if (!response.ok) throw new Error("原尺寸图片尚未下载，无法插入画布");
            const dataUrl = await blobAsDataUrl(await response.blob());
            await onInsert({ index: item.index, id: item.id, label: item.label, collection: item.collection, dataUrl }, replace && canReplace);
            onClose();
        } catch (cause) {
            message.error(cause instanceof Error ? cause.message : "插入失败");
        } finally {
            setInserting(null);
        }
    };

    return (
        <Modal title="PoseAtlas · 参考图库" open={open} onCancel={onClose} footer={null} width={960} destroyOnHidden>
            {!root ? (
                <Empty description="请先使用 Canvas Lab 本地 ComfyUI Gateway" />
            ) : (
                <div className="space-y-4">
                    <div className="flex flex-wrap items-center gap-3">
                        <Segmented value={collection} onChange={value => { setCollection(value as typeof collection); setPage(1); }}
                            options={[{ label: "姿势", value: "pose" }, { label: "服饰", value: "costume" }, { label: "肖像", value: "portrait" }]} />
                        <Input.Search className="max-w-sm flex-1" placeholder="搜索姿势、编号、角度或名称" value={query}
                            onChange={event => { setQuery(event.target.value); setPage(1); }} allowClear />
                        <span className="text-xs text-stone-500">{results ? `匹配 ${results.total} ${collection === "pose" ? "组姿势" : "项"}` : ""}</span>
                        {canReplace ? <Segmented value={replace ? "replace" : "insert"} onChange={mode => setReplace(mode === "replace")}
                            options={[{ label: "新建图片节点", value: "insert" }, { label: "替换选中图片", value: "replace" }]} /> : null}
                    </div>
                    {error ? <div role="alert" className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
                    <Spin spinning={loading}>
                        <div className="grid max-h-[55vh] min-h-[280px] grid-cols-3 gap-3 overflow-y-auto sm:grid-cols-5">
                            {results?.items.map(entry => {
                                const isGroup = "variants" in entry;
                                const variants = isGroup ? entry.variants : [entry];
                                const selected = variants.find(item => item.index === selectedAngles[entry.id]) || variants[0];
                                return (
                                    <div key={entry.id + (isGroup ? "" : `-${selected.index}`)}
                                        className="overflow-hidden rounded-lg border bg-white dark:bg-stone-900">
                                        <button type="button" disabled={!selected.fullAvailable || inserting !== null}
                                            onClick={() => void insert(selected)}
                                            title={selected.fullAvailable ? `将「${selected.label}」插入画布` : "原图尚未下载"}
                                            className="w-full text-left transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-stone-800">
                                            <div className="relative aspect-[3/4] bg-stone-100 dark:bg-stone-800">
                                                {selected.thumbAvailable ? <img loading="lazy" src={`${root}/api/poseatlas/asset/${selected.index}/thumb`} alt={selected.label}
                                                    className="h-full w-full object-contain" /> : null}
                                                {inserting === selected.index ? <div className="absolute inset-0 grid place-items-center bg-black/30"><Spin /></div> : null}
                                            </div>
                                            <div className="line-clamp-2 min-h-10 p-2 text-xs" title={selected.label}>
                                                {isGroup ? entry.label : selected.label}
                                            </div>
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
                                    </div>
                                );
                            })}
                        </div>
                    </Spin>
                    <div className="flex items-center justify-between gap-2">
                        <span className="text-xs text-stone-500">先选方向，再点击图片插入；深度原图仍遵守按需下载限制。</span>
                        <Pagination simple current={page} total={results?.total || 0} pageSize={pageSize} onChange={setPage} />
                    </div>
                    <div className="flex justify-end"><Button onClick={onClose}>关闭</Button></div>
                </div>
            )}
        </Modal>
    );
}

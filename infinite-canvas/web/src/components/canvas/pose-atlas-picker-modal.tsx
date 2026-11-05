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

type Item = Omit<PoseAtlasSelection, "dataUrl"> & { thumbAvailable: boolean; fullAvailable: boolean };
type SearchResult = { ok: boolean; total: number; items: Item[] };
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

    useEffect(() => {
        if (!open || !root) return;
        const controller = new AbortController();
        setLoading(true);
        setError("");
        const params = new URLSearchParams({ collection, q: query, page: String(page), limit: String(pageSize) });
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
                        <span className="text-xs text-stone-500">{results ? `匹配 ${results.total} 项` : ""}</span>
                        {canReplace ? <Segmented value={replace ? "replace" : "insert"} onChange={mode => setReplace(mode === "replace")}
                            options={[{ label: "新建图片节点", value: "insert" }, { label: "替换选中图片", value: "replace" }]} /> : null}
                    </div>
                    {error ? <div role="alert" className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
                    <Spin spinning={loading}>
                        <div className="grid max-h-[55vh] min-h-[280px] grid-cols-3 gap-3 overflow-y-auto sm:grid-cols-5">
                            {results?.items.map(item => (
                                <button key={item.index} type="button" disabled={!item.fullAvailable || inserting !== null}
                                    onClick={() => void insert(item)}
                                    title={item.fullAvailable ? item.label : "原图尚未下载"}
                                    className="overflow-hidden rounded-lg border text-left transition hover:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50">
                                    <div className="relative aspect-[3/4] bg-stone-100 dark:bg-stone-800">
                                        {item.thumbAvailable ? <img loading="lazy" src={`${root}/api/poseatlas/asset/${item.index}/thumb`} alt={item.label}
                                            className="h-full w-full object-contain" /> : null}
                                        {inserting === item.index ? <div className="absolute inset-0 grid place-items-center bg-black/30"><Spin /></div> : null}
                                    </div>
                                    <div className="line-clamp-2 min-h-10 p-2 text-xs">{item.label}</div>
                                </button>
                            ))}
                        </div>
                    </Spin>
                    <div className="flex items-center justify-between gap-2">
                        <span className="text-xs text-stone-500">素材保留来源引用；深度原图遵守原站按需下载限制。</span>
                        <Pagination simple current={page} total={results?.total || 0} pageSize={pageSize} onChange={setPage} />
                    </div>
                    <div className="flex justify-end"><Button onClick={onClose}>关闭</Button></div>
                </div>
            )}
        </Modal>
    );
}

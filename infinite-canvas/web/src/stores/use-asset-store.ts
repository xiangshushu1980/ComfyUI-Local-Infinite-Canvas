import { create } from "zustand";
import { persist, type PersistStorage, type StorageValue } from "zustand/middleware";

import { nanoid } from "nanoid";
import { localForageStorage } from "@/lib/localforage-storage";
import { cleanupUnusedImages, ensureImagePreview, previewUrlFor, resolveImageUrl, uploadImage } from "@/services/image-storage";
import { cleanupUnusedMedia, resolveMediaUrl } from "@/services/file-storage";

export type AssetKind = "text" | "image" | "video";
export type AssetFlag = { name: string; color: string; createdAt: string };
export type TextAsset = AssetBase<"text"> & { data: { content: string } };
export type ImageAsset = AssetBase<"image"> & { data: { dataUrl: string; storageKey?: string; width: number; height: number; bytes: number; mimeType: string } };
export type VideoAsset = AssetBase<"video"> & { data: { url: string; storageKey?: string; width: number; height: number; bytes: number; mimeType: string } };
export type Asset = TextAsset | ImageAsset | VideoAsset;

type AssetBase<T extends AssetKind> = {
    id: string;
    kind: T;
    title: string;
    coverUrl: string;
    tags: string[];
    source?: string;
    note?: string;
    createdAt: string;
    updatedAt: string;
    metadata?: Record<string, unknown>;
};

type AssetStore = {
    hydrated: boolean;
    assets: Asset[];
    flags: AssetFlag[];
    addAsset: (asset: Omit<Asset, "id" | "createdAt" | "updatedAt">) => string;
    updateAsset: (id: string, patch: Partial<Omit<Asset, "id" | "createdAt">>) => void;
    removeAsset: (id: string) => void;
    replaceAssets: (assets: Asset[]) => void;
    addFlag: (name: string, color: string) => string | null;
    updateFlag: (name: string, patch: Partial<Pick<AssetFlag, "name" | "color">>) => void;
    removeFlag: (name: string) => void;
    setAssetFlags: (assetIds: string[], flagNames: string[], mode: "add" | "remove" | "replace") => void;
    cleanupImages: (extra?: unknown) => void;
};

// 卡片用缩略图渲染，自定义封面（远程地址或单独上传的封面）保持原样。
export function assetCoverUrl(asset: Asset) {
    const own = asset.kind === "image" ? asset.data.dataUrl : "";
    const cover = asset.coverUrl || own;
    return asset.kind === "image" && cover === own ? previewUrlFor(asset.data.storageKey) || cover : cover;
}

const ASSET_STORE_KEY = "infinite-canvas:asset_store";
const DEFAULT_FLAG_COLOR = "#0ea5e9";

function ensureFlags(flags: AssetFlag[], tags: string[]) {
    const known = new Map(flags.map((flag) => [flag.name.toLocaleLowerCase(), flag.name]));
    const nextFlags = [...flags];
    const canonicalTags = tags.map((tag) => {
        const name = tag.trim();
        if (!name) return "";
        const key = name.toLocaleLowerCase();
        const existing = known.get(key);
        if (existing) return existing;
        known.set(key, name);
        nextFlags.push({ name, color: DEFAULT_FLAG_COLOR, createdAt: new Date().toISOString() });
        return name;
    }).filter(Boolean);
    return { flags: nextFlags, tags: [...new Set(canonicalTags)] };
}

const assetStorage: PersistStorage<AssetStore> = {
    getItem: async (name) => {
        const value = await localForageStorage.getItem(name);
        if (!value) return null;
        const parsed = JSON.parse(value) as StorageValue<AssetStore>;
        parsed.state.assets = await Promise.all(
            parsed.state.assets.map(async (asset) => {
                if (asset.kind === "video" && asset.data.storageKey) return { ...asset, data: { ...asset.data, url: await resolveMediaUrl(asset.data.storageKey, asset.data.url) } };
                if (asset.kind !== "image") return asset;
                if (asset.data.storageKey) {
                    void ensureImagePreview(asset.data.storageKey);
                    return {
                        ...asset,
                        coverUrl: asset.coverUrl.startsWith("blob:") ? await resolveImageUrl(asset.data.storageKey, asset.coverUrl) : asset.coverUrl,
                        data: { ...asset.data, dataUrl: await resolveImageUrl(asset.data.storageKey, asset.data.dataUrl) },
                    };
                }
                if (!asset.data.dataUrl.startsWith("data:image/")) return asset;
                const image = await uploadImage(asset.data.dataUrl);
                return { ...asset, coverUrl: asset.coverUrl.startsWith("data:image/") ? image.url : asset.coverUrl, data: { ...asset.data, dataUrl: image.url, storageKey: image.storageKey, bytes: image.bytes, mimeType: image.mimeType } };
            }),
        );
        const storedFlags = (parsed.state.flags || []) as Array<AssetFlag | { id: string; name: string; color: string; createdAt: string }>;
        const flagsById = new Map(storedFlags.flatMap((flag) => ("id" in flag ? [[flag.id, flag.name] as const] : [])));
        const flagsByName = new Map<string, AssetFlag>();
        storedFlags.forEach((flag) => {
            const normalized = { name: flag.name.trim(), color: flag.color, createdAt: flag.createdAt || new Date().toISOString() };
            if (normalized.name) flagsByName.set(normalized.name.toLocaleLowerCase(), normalized);
        });
        parsed.state.assets = parsed.state.assets.map((asset) => {
            const oldFlagNames = ((asset as Asset & { flags?: string[] }).flags || []).map((id) => flagsById.get(id)).filter((name): name is string => Boolean(name));
            const tags = [...new Set([...(asset.tags || []), ...oldFlagNames])];
            for (const name of tags) {
                const key = name.trim().toLocaleLowerCase();
                if (key && !flagsByName.has(key)) flagsByName.set(key, { name: name.trim(), color: "#0ea5e9", createdAt: new Date().toISOString() });
            }
            const canonicalTags = tags.map((name) => flagsByName.get(name.trim().toLocaleLowerCase())?.name || name.trim());
            const { flags: _oldFlags, ...rest } = asset as Asset & { flags?: string[] };
            return { ...rest, tags: [...new Set(canonicalTags)] };
        });
        parsed.state.flags = [...flagsByName.values()];
        return parsed;
    },
    setItem: (name, value) => localForageStorage.setItem(name, JSON.stringify(value)),
    removeItem: (name) => localForageStorage.removeItem(name),
};

export const useAssetStore = create<AssetStore>()(
    persist(
        (set, get) => ({
            hydrated: false,
            assets: [],
            flags: [],
            addAsset: (asset) => {
                const now = new Date().toISOString();
                const id = nanoid();
                set((state) => {
                    const ensured = ensureFlags(state.flags, asset.tags || []);
                    return { flags: ensured.flags, assets: [{ ...asset, tags: ensured.tags, id, createdAt: now, updatedAt: now } as Asset, ...state.assets] };
                });
                return id;
            },
            updateAsset: (id, patch) => set((state) => {
                const normalized = patch.tags ? ensureFlags(state.flags, patch.tags) : null;
                return {
                    ...(normalized ? { flags: normalized.flags } : {}),
                    assets: state.assets.map((asset) => (asset.id === id ? ({ ...asset, ...patch, ...(normalized ? { tags: normalized.tags } : {}), updatedAt: new Date().toISOString() } as Asset) : asset)),
                };
            }),
            removeAsset: (id) =>
                set((state) => {
                    const assets = state.assets.filter((asset) => asset.id !== id);
                    get().cleanupImages({ assets });
                    return { assets };
                }),
            replaceAssets: (assets) => set((state) => {
                const ensured = assets.reduce((result, asset) => {
                    const next = ensureFlags(result.flags, asset.tags || []);
                    result.flags = next.flags;
                    result.assets.push({ ...asset, tags: next.tags });
                    return result;
                }, { flags: state.flags, assets: [] as Asset[] });
                return ensured;
            }),
            addFlag: (name, color) => {
                const normalized = name.trim();
                if (!normalized) return null;
                const existing = get().flags.find((flag) => flag.name.toLocaleLowerCase() === normalized.toLocaleLowerCase());
                if (existing) return existing.name;
                set((state) => ({ flags: [...state.flags, { name: normalized, color, createdAt: new Date().toISOString() }] }));
                return normalized;
            },
            updateFlag: (name, patch) => set((state) => {
                const current = state.flags.find((flag) => flag.name === name);
                const nextName = patch.name?.trim() || current?.name || name;
                return {
                    flags: state.flags.map((flag) => flag.name === name ? { ...flag, ...patch, name: nextName } : flag),
                    assets: patch.name && nextName !== name ? state.assets.map((asset) => asset.tags.includes(name) ? { ...asset, tags: asset.tags.map((tag) => tag === name ? nextName : tag), updatedAt: new Date().toISOString() } : asset) : state.assets,
                };
            }),
            removeFlag: (name) => set((state) => ({
                flags: state.flags.filter((flag) => flag.name !== name),
                assets: state.assets.map((asset) => asset.tags.includes(name) ? { ...asset, tags: asset.tags.filter((tag) => tag !== name), updatedAt: new Date().toISOString() } : asset),
            })),
            setAssetFlags: (assetIds, flagNames, mode) => {
                const selectedAssets = new Set(assetIds);
                const selectedFlags = new Set(flagNames);
                set((state) => ({ assets: state.assets.map((asset) => {
                    if (!selectedAssets.has(asset.id)) return asset;
                    const current = new Set(asset.tags || []);
                    if (mode === "replace") return { ...asset, tags: [...selectedFlags], updatedAt: new Date().toISOString() };
                    for (const name of selectedFlags) mode === "add" ? current.add(name) : current.delete(name);
                    return { ...asset, tags: [...current], updatedAt: new Date().toISOString() };
                }) }));
            },
            cleanupImages: (extra) => {
                window.setTimeout(async () => {
                    const { useCanvasStore } = await import("@/stores/canvas/use-canvas-store");
                    const usedData = () => ({ assets: get().assets, projects: useCanvasStore.getState().projects, extra });
                    await cleanupUnusedImages(usedData);
                    await cleanupUnusedMedia(usedData);
                }, 0);
            },
        }),
        {
            name: ASSET_STORE_KEY,
            storage: assetStorage,
            partialize: (state) => ({ assets: state.assets, flags: state.flags }) as StorageValue<AssetStore>["state"],
            onRehydrateStorage: () => () => {
                useAssetStore.setState({ hydrated: true });
            },
        },
    ),
);

import { useMemo, useState } from "react";
import { App, Button, Checkbox, ColorPicker, Empty, Input, Modal, Popover, Select, Space, Tag, Typography } from "antd";
import { Check, Plus, Settings2, X } from "lucide-react";

import { useAssetStore, type Asset, type AssetFlag } from "@/stores/use-asset-store";

export type FlagFilterGroup = { join: "and" | "or"; match: "and" | "or"; ids: string[] };
export type FlagFilter = FlagFilterGroup[];

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#14b8a6", "#0ea5e9", "#6366f1", "#a855f7", "#ec4899", "#78716c"];

function text(zh: string, en: string) {
    return typeof navigator !== "undefined" && navigator.language.toLowerCase().startsWith("zh") ? zh : en;
}

export function AssetFlagBadges({ asset, limit = Number.POSITIVE_INFINITY, showEmpty = true }: { asset: Asset; limit?: number; showEmpty?: boolean }) {
    const flags = useAssetStore((state) => state.flags);
    const byName = new Map(flags.map((flag) => [flag.name, flag]));
    const assigned = (asset.tags || []).map((name) => byName.get(name)).filter((flag): flag is NonNullable<typeof flag> => Boolean(flag));
    if (!assigned.length) return showEmpty ? <span className="text-[10px] text-stone-400">{text("无 flag", "No flags")}</span> : null;
    return <span className="flex min-w-0 flex-wrap gap-x-1.5 gap-y-0.5">{assigned.slice(0, limit).map((flag) => <span key={flag.name} className="text-[10px] font-medium" style={{ color: flag.color }}>{flag.name}</span>)}</span>;
}

export function AssetFlagPicker({ assetIds, compact = false, triggerless = false, open: controlledOpen, onOpenChange }: { assetIds: string[]; compact?: boolean; triggerless?: boolean; open?: boolean; onOpenChange?: (open: boolean) => void }) {
    const { message } = App.useApp();
    const flags = useAssetStore((state) => state.flags);
    const assets = useAssetStore((state) => state.assets);
    const setAssetFlags = useAssetStore((state) => state.setAssetFlags);
    const addFlag = useAssetStore((state) => state.addFlag);
    const [localOpen, setLocalOpen] = useState(false);
    const open = controlledOpen ?? localOpen;
    const setOpen = onOpenChange ?? setLocalOpen;
    const [draft, setDraft] = useState("");
    const selected = useMemo(() => {
        const target = assets.filter((asset) => assetIds.includes(asset.id));
        return flags.filter((flag) => target.length > 0 && target.every((asset) => (asset.tags || []).includes(flag.name))).map((flag) => flag.name);
    }, [assets, assetIds, flags]);
    const partial = useMemo(() => new Set(flags.filter((flag) => assets.some((asset) => assetIds.includes(asset.id) && (asset.tags || []).includes(flag.name)) && !selected.includes(flag.name)).map((flag) => flag.name)), [assets, assetIds, flags, selected]);
    const onToggle = (name: string, checked: boolean) => setAssetFlags(assetIds, [name], checked ? "add" : "remove");
    const create = () => {
        const name = draft.trim();
        if (!name) return;
        const existing = flags.find((flag) => flag.name.toLocaleLowerCase() === name.toLocaleLowerCase());
        const flagName = existing?.name || addFlag(name, COLORS[flags.length % COLORS.length]);
        if (!flagName) {
            message.warning(text("Flag 名称已存在", "A flag with that name already exists"));
            return;
        }
        setAssetFlags(assetIds, [flagName], "add");
        setDraft("");
    };
    const content = <div className="w-64 space-y-2">
        <div className="max-h-56 overflow-y-auto">
            {flags.length ? flags.map((flag) => <div key={flag.name} className="flex items-center gap-2 rounded px-1 py-1 hover:bg-stone-50 dark:hover:bg-stone-800">
                <Checkbox checked={selected.includes(flag.name)} indeterminate={partial.has(flag.name)} onChange={(event) => onToggle(flag.name, event.target.checked)} />
                <span className="size-2.5 rounded-full" style={{ backgroundColor: flag.color }} />
                <span className="min-w-0 flex-1 truncate text-sm">{flag.name}</span>
            </div>) : <Typography.Text type="secondary">{text("还没有 flag", "No flags yet")}</Typography.Text>}
        </div>
        <Space.Compact className="w-full">
            <Input size="small" value={draft} placeholder={text("新建并添加 flag", "Create and add a flag")} onChange={(event) => setDraft(event.target.value)} onPressEnter={create} />
            <Button size="small" icon={<Plus className="size-3.5" />} onClick={create} aria-label={text("创建 flag", "Create flag")} />
        </Space.Compact>
        <div className="flex justify-end"><Button type="link" size="small" onClick={() => setOpen(false)}>{text("完成", "Done")}</Button></div>
    </div>;
    return <Popover content={content} trigger="click" open={open} onOpenChange={setOpen} placement="bottomLeft">
        {triggerless ? <span className="pointer-events-none absolute inset-0" /> : compact ? <button type="button" className="inline-flex items-center gap-1 rounded-md border border-stone-200 bg-white/90 px-1.5 py-1 text-[11px] text-stone-600 shadow-sm hover:text-stone-950 dark:border-stone-700 dark:bg-black/70 dark:text-stone-200 dark:hover:text-white"><Settings2 className="size-3" />{text("Flag", "Flags")}</button> : <Button size="small" icon={<Plus className="size-3.5" />}>{assetIds.length > 1 ? text("批量设置 flag", "Set flags") : text("设置 flag", "Set flags")}</Button>}
    </Popover>;
}

export function FlagManager({ open, onClose }: { open: boolean; onClose: () => void }) {
    const { message, modal } = App.useApp();
    const flags = useAssetStore((state) => state.flags);
    const assets = useAssetStore((state) => state.assets);
    const addFlag = useAssetStore((state) => state.addFlag);
    const updateFlag = useAssetStore((state) => state.updateFlag);
    const removeFlag = useAssetStore((state) => state.removeFlag);
    const [name, setName] = useState("");
    const [color, setColor] = useState(COLORS[5]);
    const [query, setQuery] = useState("");
    const [editing, setEditing] = useState<string | null>(null);
    const [editName, setEditName] = useState("");
    const filtered = flags.filter((flag) => flag.name.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()));
    const countFor = (name: string) => assets.filter((asset) => (asset.tags || []).includes(name)).length;
    const create = () => {
        if (!name.trim()) return;
        if (flags.some((flag) => flag.name.toLocaleLowerCase() === name.trim().toLocaleLowerCase())) {
            message.warning(text("Flag 名称已存在", "A flag with that name already exists"));
            return;
        }
        addFlag(name, color);
        setName("");
    };
    const rename = (flag: AssetFlag) => {
        const next = editName.trim();
        if (!next) return;
        if (flags.some((item) => item.name !== flag.name && item.name.toLocaleLowerCase() === next.toLocaleLowerCase())) {
            message.warning(text("Flag 名称已存在", "A flag with that name already exists"));
            return;
        }
        updateFlag(flag.name, { name: next });
        setEditing(null);
    };
    const confirmDelete = (flag: AssetFlag) => modal.confirm({
        title: text(`删除“${flag.name}”？`, `Delete “${flag.name}”?`),
        content: text(`这会从 ${countFor(flag.name)} 个资产上移除此 flag。`, `This removes the flag from ${countFor(flag.name)} assets.`),
        okText: text("删除", "Delete"), cancelText: text("取消", "Cancel"), okButtonProps: { danger: true },
            onOk: () => removeFlag(flag.name),
    });
    return <Modal title={text("Flag 管理", "Flag manager")} open={open} onCancel={onClose} footer={null} width={680} destroyOnHidden>
        <div className="space-y-4 pt-1">
            <Space.Compact className="w-full">
                <Input value={name} placeholder={text("输入新 flag 名称", "New flag name")} onChange={(event) => setName(event.target.value)} onPressEnter={create} />
                <Select value={color} onChange={setColor} style={{ width: 156 }} options={COLORS.map((value) => ({ value, label: <span className="inline-flex items-center gap-2"><i className="size-3 rounded-full" style={{ backgroundColor: value }} />{value}</span> }))} />
                <Button type="primary" icon={<Plus className="size-3.5" />} onClick={create}>{text("创建", "Create")}</Button>
            </Space.Compact>
            <Input.Search allowClear value={query} onChange={(event) => setQuery(event.target.value)} placeholder={text("搜索 flag", "Search flags")} />
            <div className="max-h-[55vh] divide-y divide-stone-100 overflow-y-auto dark:divide-stone-800">
                {filtered.map((flag) => <div key={flag.name} className="flex min-h-14 items-center gap-3 py-2">
                    <ColorPicker value={flag.color} onChange={(value) => updateFlag(flag.name, { color: value.toHexString() })} showText />
                    {editing === flag.name ? <Input autoFocus size="small" value={editName} onChange={(event) => setEditName(event.target.value)} onPressEnter={() => rename(flag)} className="max-w-64" /> : <span className="min-w-0 flex-1 truncate text-sm font-medium">{flag.name}</span>}
                    <Typography.Text type="secondary" className="w-28 text-right">{countFor(flag.name)} {text("个资产", "assets")}</Typography.Text>
                    {editing === flag.name ? <Button size="small" type="text" icon={<Check className="size-4" />} onClick={() => rename(flag)} /> : <Button size="small" type="text" onClick={() => { setEditing(flag.name); setEditName(flag.name); }}>{text("改名", "Rename")}</Button>}
                    <Button size="small" type="text" danger icon={<X className="size-4" />} onClick={() => confirmDelete(flag)} aria-label={text("删除 flag", "Delete flag")} />
                </div>)}
                {!filtered.length ? <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={text("没有匹配的 flag", "No matching flags")} /> : null}
            </div>
        </div>
    </Modal>;
}

export function FlagFilterPanel({ value, onChange }: { value: FlagFilter; onChange: (filter: FlagFilter) => void }) {
    const flags = useAssetStore((state) => state.flags);
    const updateGroup = (index: number, patch: Partial<FlagFilterGroup>) => onChange(value.map((group, i) => i === index ? { ...group, ...patch } : group));
    const addGroup = () => onChange([...value, { join: "or", match: "and", ids: [] }]);
    const options = flags.map((flag) => ({ value: flag.name, label: flag.name }));
    return <div className="space-y-2">
        {value.map((group, index) => <div key={index} className="flex flex-wrap items-center gap-2 rounded-lg border border-stone-200 p-2 dark:border-stone-800">
            <Select size="small" value={group.join} disabled={index === 0} onChange={(join) => updateGroup(index, { join })} options={[{ value: "or", label: text("或", "OR") }, { value: "and", label: text("且", "AND") }]} className="w-20" />
            <span className="text-xs text-stone-500">{index === 0 ? text("满足以下 flag", "Match flags") : text("条件组", "Group")}</span>
            <Select mode="multiple" allowClear size="small" value={group.ids} onChange={(ids) => updateGroup(index, { ids })} options={options} placeholder={text("选择 flag", "Choose flags")} className="min-w-48 flex-1" />
            {group.ids.length > 1 ? <Select size="small" value={group.match} onChange={(match) => updateGroup(index, { match })} options={[{ value: "or", label: text("任意一个", "Any") }, { value: "and", label: text("全部", "All") }]} className="w-24" /> : null}
            {index > 0 ? <Button size="small" type="text" danger icon={<X className="size-3.5" />} onClick={() => onChange(value.filter((_, i) => i !== index))} aria-label={text("移除条件组", "Remove group")} /> : null}
        </div>)}
        <div className="flex items-center gap-2">
            <Button size="small" type="dashed" icon={<Plus className="size-3.5" />} onClick={addGroup}>{text("添加条件组", "Add group")}</Button>
            {value.length ? <Button size="small" type="link" onClick={() => onChange([])}>{text("清除筛选", "Clear filters")}</Button> : null}
        </div>
    </div>;
}

export function QuickFlagFilters({ value, onChange }: { value: FlagFilter; onChange: (filter: FlagFilter) => void }) {
    const flags = useAssetStore((state) => state.flags);
    if (!flags.length) return null;
    const isSimple = value.length <= 1 && (!value[0] || value[0].ids.length <= 1 || value[0].match === "or");
    const selected = new Set(isSimple ? value[0]?.ids || [] : []);
    if (!isSimple) return <div className="flex flex-wrap items-center gap-2 text-xs text-stone-500">
        <span>{text("当前使用组合条件", "Using grouped conditions")}</span>
        <Button size="small" type="link" onClick={() => onChange([])}>{text("切换到快速筛选", "Switch to quick filters")}</Button>
    </div>;
    return <div className="grid grid-cols-2 gap-1.5 md:grid-cols-3">
        <Button size="small" type={!selected.size ? "primary" : "default"} className="w-full truncate" onClick={() => onChange([])}>{text("全部", "All")}</Button>
        {flags.map((flag) => <Button key={flag.name} size="small" type={selected.has(flag.name) ? "primary" : "default"} className="w-full truncate" aria-pressed={selected.has(flag.name)} onClick={() => {
            const checked = !selected.has(flag.name);
            const next = new Set(selected);
            checked ? next.add(flag.name) : next.delete(flag.name);
            const ids = [...next];
            onChange(ids.length ? [{ join: "or", match: "or", ids }] : []);
        }} style={selected.has(flag.name) ? { color: flag.color, borderColor: flag.color, background: `${flag.color}18` } : undefined}>{flag.name}</Button>)}
    </div>;
}

export function matchesFlagFilter(asset: Asset, filter: FlagFilter) {
    const groups = filter.filter((group) => group.ids.length > 0);
    if (!groups.length) return true;
    const has = new Set(asset.tags || []);
    const groupMatches = groups.map((group) => group.match === "and" ? group.ids.every((id) => has.has(id)) : group.ids.some((id) => has.has(id)));
    return groupMatches.slice(1).reduce((result, matched, index) => groups[index + 1].join === "and" ? result && matched : result || matched, groupMatches[0]);
}


import { useCallback, useEffect, useState } from "react";
import { Alert, Button, Spin, Switch } from "antd";
import { useTranslation } from "react-i18next";

import { fetchAgentJson } from "@/services/api/canvas-agent";
import { useAgentStore } from "@/stores/use-agent-store";

type Server = { name: string; enabled: boolean; inheritedEnabled: boolean; overridden: boolean; required: boolean };

export function AgentMcpView() {
    const { t } = useTranslation();
    const { url, token, connected, conversation, sending, waiting } = useAgentStore();
    const [servers, setServers] = useState<Server[]>([]);
    const [loading, setLoading] = useState(false);
    const [busy, setBusy] = useState("");
    const [error, setError] = useState("");
    const [changed, setChanged] = useState(false);
    const endpoint = url.trim().replace(/\/$/, "");
    const refresh = useCallback(async () => {
        if (!connected || !endpoint || !token) return;
        setLoading(true); setError("");
        try {
            const result = await fetchAgentJson<{ data: Server[] }>(endpoint, token, "/agent/codex/mcp");
            setServers(result.data);
        } catch (e) { setError(e instanceof Error ? e.message : String(e)); }
        finally { setLoading(false); }
    }, [connected, endpoint, token]);
    useEffect(() => { void refresh(); }, [refresh]);
    const update = async (name: string, enabled: boolean | null) => {
        setBusy(name); setError("");
        try {
            await fetchAgentJson(endpoint, token, `/agent/codex/mcp/${encodeURIComponent(name)}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ enabled }) });
            setChanged(true); await refresh();
        } catch (e) { setError(e instanceof Error ? e.message : String(e)); }
        finally { setBusy(""); }
    };
    const status = conversation.mcpStatuses;
    const extras = Object.keys(status).filter((name) => !servers.some((server) => server.name === name));
    const statusText = (name: string) => {
        const item = status[name];
        return item ? `${t(`agent.mcp.status.${item.status}`)}${item.error ? `: ${item.error}` : ""}` : t("agent.mcp.status.unknown");
    };
    return <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-4">
        <div className="flex items-center justify-between gap-2"><strong>{t("agent.mcp.title")}</strong><Button size="small" onClick={() => void refresh()} disabled={!connected || loading}>{t("agent.mcp.refresh")}</Button></div>
        <div className="text-xs opacity-70">{t("agent.mcp.explanation")}</div>
        {changed && <Alert type="info" showIcon message={t("agent.mcp.applyLater")} />}
        {error && <Alert type="error" showIcon message={error} />}
        {!connected ? <Alert type="info" message={t("agent.mcp.connectFirst")} /> : loading && !servers.length ? <Spin /> : servers.map((server) => <div key={server.name} className="rounded border p-3">
            <div className="flex items-center justify-between gap-2"><strong>{server.name}</strong><Switch aria-label={`${server.name} ${t("agent.mcp.configEnabled")}`} checked={server.enabled} loading={busy === server.name} disabled={server.required || !/^[A-Za-z0-9_-]+$/.test(server.name) || Boolean(busy) || sending || waiting} onChange={(value) => void update(server.name, value)} /></div>
            <div className="mt-1 text-xs opacity-70">{t("agent.mcp.configEnabled")}: {t(server.enabled ? "agent.mcp.yes" : "agent.mcp.no")} · {server.required ? t("agent.mcp.required") : !/^[A-Za-z0-9_-]+$/.test(server.name) ? t("agent.mcp.managedElsewhere") : server.overridden ? t("agent.mcp.override") : t("agent.mcp.inherited")}</div>
            <div className="mt-1 break-words text-xs">{t("agent.mcp.threadStatus")}: {statusText(server.name)}</div>
            {server.overridden && !server.required && <Button size="small" type="link" className="!px-0" disabled={Boolean(busy) || sending || waiting} onClick={() => void update(server.name, null)}>{t("agent.mcp.reset")}</Button>}
        </div>)}
        {extras.map((name) => <div key={name} className="rounded border p-3"><strong>{name}</strong><div className="mt-1 text-xs opacity-70">{t("agent.mcp.managedElsewhere")}</div><div className="mt-1 break-words text-xs">{t("agent.mcp.threadStatus")}: {statusText(name)}</div></div>)}
    </div>;
}

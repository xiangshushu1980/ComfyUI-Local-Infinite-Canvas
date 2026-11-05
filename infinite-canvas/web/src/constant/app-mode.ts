import { RUNTIME_LOCAL_GATEWAY_HOST, RUNTIME_LOCAL_GATEWAY_PORT, RUNTIME_LOCAL_GATEWAY_URL } from "./runtime-config";

function runtimeGatewayBaseUrl() {
    if (RUNTIME_LOCAL_GATEWAY_URL) return RUNTIME_LOCAL_GATEWAY_URL.replace(/\/+$/, "").endsWith("/v1") ? RUNTIME_LOCAL_GATEWAY_URL.replace(/\/+$/, "") : `${RUNTIME_LOCAL_GATEWAY_URL.replace(/\/+$/, "")}/v1`;
    const host = RUNTIME_LOCAL_GATEWAY_HOST || "127.0.0.1";
    const port = RUNTIME_LOCAL_GATEWAY_PORT || "8190";
    return `http://${host}:${port}/v1`;
}

export const LOCAL_GATEWAY_BASE_URL = import.meta.env.VITE_LOCAL_GATEWAY_URL || runtimeGatewayBaseUrl();
export const LOCAL_GATEWAY_ORIGIN = (() => {
    try {
        return new URL(LOCAL_GATEWAY_BASE_URL).origin;
    } catch {
        return "";
    }
})();
export const LOCAL_GATEWAY_CHANNEL_ID = "local-gateway";

export function isLocalGatewayUrl(url: string) {
    try {
        const parsed = new URL(String(url || ""));
        if (LOCAL_GATEWAY_ORIGIN && parsed.origin === LOCAL_GATEWAY_ORIGIN) return true;
        return ["127.0.0.1", "localhost", "::1", "[::1]"].includes(parsed.hostname);
    } catch {
        return false;
    }
}

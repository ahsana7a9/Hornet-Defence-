const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, options);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    console.warn(`[API] ${path} failed:`, err.message);
    return null;
  }
}

export const getStatus       = ()       => request("/status");
export const getLogs         = ()       => request("/logs/public");
export const getAlerts       = ()       => request("/alerts?limit=20&min_severity=INFO");
export const getAlertCounts  = ()       => request("/alerts/counts");
export const getBlocked      = ()       => request("/blocked");
export const getActions      = ()       => request("/actions?limit=20");
export const getLiveNetwork  = ()       => request("/network/live");
export const getNetworkStats = ()       => request("/network/stats");

export const blockIP = (ip, reason = "manual block") =>
  request("/block", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip, reason }),
  });

export const unblockIP = (ip) =>
  request(`/block/${ip}`, { method: "DELETE" });

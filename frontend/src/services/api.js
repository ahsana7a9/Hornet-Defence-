const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function getStatus() {
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    console.warn("[API] getStatus failed:", err.message);
    return { status: "unreachable", system: "ShadowMesh" };
  }
}

export async function getLogs(token) {
  try {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const res = await fetch(`${API_BASE}/logs/public`, { headers });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    console.warn("[API] getLogs failed:", err.message);
    return [];
  }
}

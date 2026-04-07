const API_BASE = "http://localhost:8000";

export async function getStatus() {
  const res = await fetch(`${API_BASE}/`);
  return res.json();
}

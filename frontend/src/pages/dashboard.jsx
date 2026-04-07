import { useEffect, useState, useCallback } from "react";
import {
  getStatus, getLogs, getAlerts, getAlertCounts,
  getBlocked, getActions, getLiveNetwork, getNetworkStats,
  blockIP, unblockIP
} from "../services/api";
import SwarmGraph from "../components/SwarmGraph";

const S = {
  page:     { background: "#080810", color: "#c8ffd4", fontFamily: "monospace", minHeight: "100vh", padding: "20px 28px" },
  h1:       { borderBottom: "1px solid #00ff88", paddingBottom: "10px", color: "#00ff88", fontSize: "20px", margin: "0 0 16px" },
  h2:       { fontSize: "13px", letterSpacing: "2px", marginBottom: "10px" },
  grid:     { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px", marginBottom: "20px" },
  card:     { background: "#0d0d1a", border: "1px solid #1a1a2e", borderRadius: "8px", padding: "14px" },
  badge:    (c) => ({ display: "inline-block", padding: "2px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "bold", background: c, color: "#000" }),
  table:    { width: "100%", borderCollapse: "collapse", fontSize: "12px" },
  th:       { color: "#555", textAlign: "left", padding: "5px 10px", borderBottom: "1px solid #1a1a2e" },
  td:       { padding: "5px 10px", borderBottom: "1px solid #111" },
  btn:      (c) => ({ background: "none", border: `1px solid ${c}`, color: c, padding: "3px 10px", borderRadius: "4px", cursor: "pointer", fontSize: "11px" }),
  input:    { background: "#111", border: "1px solid #333", color: "#fff", padding: "5px 8px", borderRadius: "4px", fontSize: "12px", width: "140px" },
  statVal:  { fontSize: "22px", fontWeight: "bold", margin: "4px 0" },
  label:    { color: "#555", fontSize: "11px" },
};

const SEV_COLOR = { CRITICAL: "#ff2244", HIGH: "#ff6600", WARNING: "#ffaa00", INFO: "#00aaff" };

function StatCard({ label, value, color = "#00ff88", sub }) {
  return (
    <div style={{ ...S.card, textAlign: "center" }}>
      <div style={S.label}>{label}</div>
      <div style={{ ...S.statVal, color }}>{value ?? "—"}</div>
      {sub && <div style={{ ...S.label, color: "#444" }}>{sub}</div>}
    </div>
  );
}

export default function Dashboard() {
  const [status,   setStatus]   = useState("connecting...");
  const [logs,     setLogs]     = useState([]);
  const [alerts,   setAlerts]   = useState([]);
  const [counts,   setCounts]   = useState({});
  const [blocked,  setBlocked]  = useState([]);
  const [actions,  setActions]  = useState([]);
  const [network,  setNetwork]  = useState(null);
  const [netStats, setNetStats] = useState(null);
  const [blockIP_,  setBlockIP_] = useState("");
  const [loading,  setLoading]  = useState(false);
  const [swarmNodes, setSwarmNodes] = useState([]);

  const refresh = useCallback(async () => {
    const [s, l, a, c, b, ac, n, ns] = await Promise.all([
      getStatus(), getLogs(), getAlerts(), getAlertCounts(),
      getBlocked(), getActions(), getLiveNetwork(), getNetworkStats(),
    ]);
    if (s) setStatus(s.status || "unknown");
    if (l) setLogs(l.slice(0, 15));
    if (a) setAlerts(a.slice(0, 15));
    if (c) setCounts(c);
    if (b) setBlocked(b);
    if (ac) setActions(ac.slice(0, 10));
    if (n) {
      setNetwork(n);
      // Build swarm nodes from real data
      const nodes = [];
      if (n.port_scanners?.length) n.port_scanners.forEach(p => nodes.push({ id: p.ip, type: "scanner" }));
      if (n.burst_ips?.length)     n.burst_ips.forEach(b => nodes.push({ id: b.ip, type: "burst" }));
      if (n.suspicious_hits?.length) n.suspicious_hits.forEach(h => nodes.push({ id: h.ip, type: "threat" }));
      setSwarmNodes(nodes);
    }
    if (ns) setNetStats(ns);
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
  }, [refresh]);

  const handleBlock = async () => {
    if (!blockIP_.trim()) return;
    setLoading(true);
    await blockIP(blockIP_.trim(), "manual block from dashboard");
    setBlockIP_("");
    await refresh();
    setLoading(false);
  };

  const handleUnblock = async (ip) => {
    setLoading(true);
    await unblockIP(ip);
    await refresh();
    setLoading(false);
  };

  const eth = netStats?.eth0 || {};

  return (
    <div style={S.page}>
      {/* Header */}
      <h1 style={S.h1}>⬡ HORNET DEFENCE — ShadowMesh Command Center</h1>

      {/* Status bar */}
      <div style={{ marginBottom: "18px", fontSize: "12px" }}>
        <span style={S.label}>System: </span>
        <span>Hornet-Defence</span>
        {"  |  "}
        <span style={S.label}>Status: </span>
        <span style={{ color: status === "operational" ? "#00ff88" : "#ff4444", fontWeight: "bold" }}>
          {status.toUpperCase()}
        </span>
        {"  |  "}
        <span style={S.label}>Live Connections: </span>
        <span style={{ color: "#00aaff" }}>{network?.total_connections ?? "..."}</span>
        {"  |  "}
        <span style={S.label}>Blocked IPs: </span>
        <span style={{ color: "#ff4444" }}>{blocked.length}</span>
      </div>

      {/* Alert summary */}
      <div style={{ ...S.grid, gridTemplateColumns: "repeat(4, 1fr)", marginBottom: "16px" }}>
        {["CRITICAL","HIGH","WARNING","INFO"].map(lvl => (
          <StatCard key={lvl} label={lvl} value={counts[lvl] ?? 0} color={SEV_COLOR[lvl]} />
        ))}
      </div>

      {/* Network stats */}
      <div style={S.grid}>
        <StatCard label="Total TCP Connections" value={network?.total_connections} color="#00aaff" />
        <StatCard label="Established"           value={network?.established}       color="#00ff88" />
        <StatCard label="SYN Pending (risk)"    value={network?.syn_pending}       color={network?.syn_pending > 10 ? "#ff4444" : "#ffaa00"} />
        <StatCard label="Unique Remote IPs"     value={network?.unique_remote_ips} color="#aa88ff" />
        <StatCard label="Port Scanners"         value={network?.port_scanners?.length ?? 0}   color="#ff6600" sub="detected" />
        <StatCard label="Burst Sources"         value={network?.burst_ips?.length ?? 0}        color="#ff2244" sub="high conn rate" />
        <StatCard label="RX Rate"               value={eth.rx_rate_kbs != null ? `${eth.rx_rate_kbs} KB/s` : "—"} color="#00ff88" sub="eth0 inbound" />
        <StatCard label="TX Rate"               value={eth.tx_rate_kbs != null ? `${eth.tx_rate_kbs} KB/s` : "—"} color="#00aaff" sub="eth0 outbound" />
      </div>

      {/* Two-column layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>

        {/* Swarm Graph */}
        <div style={S.card}>
          <h2 style={{ ...S.h2, color: "#00aaff" }}>SWARM TOPOLOGY</h2>
          <SwarmGraph realNodes={swarmNodes} />
        </div>

        {/* Live Alerts */}
        <div style={S.card}>
          <h2 style={{ ...S.h2, color: "#ff6600" }}>LIVE ALERTS ({alerts.length})</h2>
          <div style={{ maxHeight: "280px", overflowY: "auto" }}>
            {alerts.length === 0
              ? <p style={S.label}>No alerts — system nominal</p>
              : alerts.map((a, i) => (
                <div key={i} style={{ borderBottom: "1px solid #111", padding: "5px 0", fontSize: "12px" }}>
                  <span style={S.badge(SEV_COLOR[a.severity] || "#555")}>{a.severity}</span>
                  {" "}
                  <span style={{ color: "#ccc" }}>{a.message}</span>
                  <div style={S.label}>{a.source} · {a.timestamp ? new Date(a.timestamp * 1000).toLocaleTimeString() : ""}</div>
                </div>
              ))
            }
          </div>
        </div>
      </div>

      {/* Threat Log & Blocked IPs */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>

        {/* Threat log */}
        <div style={S.card}>
          <h2 style={{ ...S.h2, color: "#ff2244" }}>DETECTED THREATS ({logs.length})</h2>
          <div style={{ maxHeight: "260px", overflowY: "auto" }}>
            <table style={S.table}>
              <thead>
                <tr>
                  {["Agent","Source","Severity","Score","Real","Time"].map(h =>
                    <th key={h} style={S.th}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {logs.map((l, i) => (
                  <tr key={i}>
                    <td style={S.td}>{l.agent_name || `Agent ${l.agent_id}`}</td>
                    <td style={{ ...S.td, color: "#ff4444" }}>{l.source}</td>
                    <td style={{ ...S.td, color: SEV_COLOR[l.severity] || "#fff" }}>{l.severity}</td>
                    <td style={S.td}>{l.anomaly_score?.toFixed(2)}</td>
                    <td style={{ ...S.td, color: l.real_data ? "#00ff88" : "#555" }}>
                      {l.real_data ? "REAL" : "SIM"}
                    </td>
                    <td style={{ ...S.td, color: "#555" }}>
                      {l.timestamp ? new Date(l.timestamp * 1000).toLocaleTimeString() : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Blocked IPs */}
        <div style={S.card}>
          <h2 style={{ ...S.h2, color: "#ff4444" }}>BLOCKED IPs ({blocked.length})</h2>

          {/* Manual block */}
          <div style={{ display: "flex", gap: "8px", marginBottom: "10px" }}>
            <input
              style={S.input}
              placeholder="Enter IP to block"
              value={blockIP_}
              onChange={e => setBlockIP_(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleBlock()}
            />
            <button style={S.btn("#ff4444")} onClick={handleBlock} disabled={loading}>
              {loading ? "..." : "BLOCK"}
            </button>
          </div>

          <div style={{ maxHeight: "220px", overflowY: "auto" }}>
            {blocked.length === 0
              ? <p style={S.label}>No IPs blocked</p>
              : blocked.map((b, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #111", padding: "5px 0", fontSize: "12px" }}>
                  <div>
                    <span style={{ color: "#ff4444" }}>{b.ip}</span>
                    <span style={{ ...S.badge("#1a1a2e"), marginLeft: "6px" }}>{b.method}</span>
                    <div style={S.label}>{b.reason}</div>
                  </div>
                  <button style={S.btn("#00ff88")} onClick={() => handleUnblock(b.ip)}>
                    UNBLOCK
                  </button>
                </div>
              ))
            }
          </div>
        </div>
      </div>

      {/* Action Log & Suspicious Services */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>

        {/* Action log */}
        <div style={S.card}>
          <h2 style={{ ...S.h2, color: "#00ff88" }}>ACTION LOG</h2>
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            {actions.length === 0
              ? <p style={S.label}>No actions taken</p>
              : actions.slice().reverse().map((a, i) => (
                <div key={i} style={{ borderBottom: "1px solid #111", padding: "4px 0", fontSize: "12px" }}>
                  <span style={S.badge(a.action === "BLOCK" ? "#ff2244" : a.action === "UNBLOCK" ? "#00ff88" : "#ff6600")}>
                    {a.action}
                  </span>
                  {" "}
                  <span style={{ color: "#ccc" }}>{a.target}</span>
                  <div style={S.label}>{a.method} · {a.timestamp ? new Date(a.timestamp * 1000).toLocaleTimeString() : ""}</div>
                </div>
              ))
            }
          </div>
        </div>

        {/* Suspicious services / port scanners */}
        <div style={S.card}>
          <h2 style={{ ...S.h2, color: "#ffaa00" }}>SUSPICIOUS ACTIVITY</h2>
          <div style={{ maxHeight: "200px", overflowY: "auto", fontSize: "12px" }}>
            {network?.port_scanners?.length > 0 && (
              <div style={{ marginBottom: "8px" }}>
                <div style={{ color: "#ff6600", marginBottom: "4px" }}>Port Scanners</div>
                {network.port_scanners.map((p, i) => (
                  <div key={i} style={{ color: "#ff4444" }}>
                    {p.ip} — {p.ports_probed} ports probed
                  </div>
                ))}
              </div>
            )}
            {network?.suspicious_hits?.length > 0 && (
              <div style={{ marginBottom: "8px" }}>
                <div style={{ color: "#ffaa00", marginBottom: "4px" }}>Service Access</div>
                {network.suspicious_hits.map((h, i) => (
                  <div key={i} style={{ color: "#ccc" }}>
                    {h.ip} → {h.service} (:{h.port})
                  </div>
                ))}
              </div>
            )}
            {network?.burst_ips?.length > 0 && (
              <div>
                <div style={{ color: "#ff2244", marginBottom: "4px" }}>Connection Bursts</div>
                {network.burst_ips.map((b, i) => (
                  <div key={i} style={{ color: "#ccc" }}>
                    {b.ip} — {b.connections_30s} conns/30s
                  </div>
                ))}
              </div>
            )}
            {!network?.port_scanners?.length && !network?.suspicious_hits?.length && !network?.burst_ips?.length && (
              <p style={S.label}>No suspicious activity detected</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

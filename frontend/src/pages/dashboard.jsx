import { useEffect, useState } from "react";
import { getStatus, getLogs } from "../services/api";
import SwarmGraph from "../components/SwarmGraph";

export default function Dashboard() {
  const [status, setStatus] = useState("Connecting...");
  const [system, setSystem] = useState("ShadowMesh");
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    getStatus().then((data) => {
      setStatus(data.status || "unknown");
      setSystem(data.system || "ShadowMesh");
    });

    getLogs().then((data) => {
      setLogs(Array.isArray(data) ? data.slice(0, 10) : []);
    });

    const interval = setInterval(() => {
      getLogs().then((data) => setLogs(Array.isArray(data) ? data.slice(0, 10) : []));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      background: "#0a0a0f",
      color: "#00ff88",
      height: "100vh",
      fontFamily: "monospace",
      padding: "24px",
      overflowY: "auto"
    }}>
      <h1 style={{ borderBottom: "1px solid #00ff88", paddingBottom: "12px" }}>
        ⬡ ShadowMesh Command Center
      </h1>

      <div style={{ marginBottom: "24px" }}>
        <span style={{ color: "#888" }}>System: </span>
        <span style={{ color: "#fff" }}>{system}</span>
        {"  |  "}
        <span style={{ color: "#888" }}>Status: </span>
        <span style={{
          color: status === "operational" ? "#00ff88" : "#ff4444",
          fontWeight: "bold"
        }}>
          {status.toUpperCase()}
        </span>
      </div>

      <h2 style={{ color: "#00aaff" }}>Swarm Topology</h2>
      <SwarmGraph />

      <h2 style={{ color: "#ff6600", marginTop: "24px" }}>
        Recent Threats ({logs.length})
      </h2>
      {logs.length === 0 ? (
        <p style={{ color: "#666" }}>No threats detected — system nominal</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ color: "#888", textAlign: "left" }}>
              <th style={{ padding: "6px 12px" }}>Agent</th>
              <th style={{ padding: "6px 12px" }}>Source</th>
              <th style={{ padding: "6px 12px" }}>Severity</th>
              <th style={{ padding: "6px 12px" }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, i) => (
              <tr key={i} style={{ borderTop: "1px solid #222" }}>
                <td style={{ padding: "6px 12px" }}>Agent {log.agent_id}</td>
                <td style={{ padding: "6px 12px", color: "#ff4444" }}>{log.source}</td>
                <td style={{ padding: "6px 12px", color: "#ffaa00" }}>
                  {log.severity?.toUpperCase()}
                </td>
                <td style={{ padding: "6px 12px", color: "#666" }}>
                  {log.timestamp ? new Date(log.timestamp * 1000).toLocaleTimeString() : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

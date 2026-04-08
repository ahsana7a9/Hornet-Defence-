import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [results, setResults] = useState([]);
  const [quarantine, setQuarantine] = useState([]);
  const [status, setStatus] = useState("Idle");
  const [protection, setProtection] = useState(true);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "usb_scan") {
        setResults((prev) => [...data.results, ...prev]);
        setStatus("USB Event Detected!");
      }
    };
    ws.onclose = () => setStatus("WS Disconnected");
    return () => ws.close();
  }, []);

  const runScan = async () => {
    setStatus("Scanning (VT Rate-Limit Active)..."); // Inform user it will be slow
    try {
      const res = await axios.get("http://localhost:8000/scan");
      const newResults = res.data.files || res.data.results || [];
      setResults(newResults);
      setStatus("Scan Complete");
    } catch (err) {
      setStatus("Error: Backend Unreachable");
    }
  };

  const handleRestore = async (quarantinedPath, originalPath) => {
    if (!quarantinedPath) return alert("No quarantine record found.");
    try {
      const res = await axios.post("http://localhost:8000/restore", {
        quarantined_path: quarantinedPath,
        original_path: originalPath
      });
      if (res.data.status === "RESTORED") {
        setResults(prev => prev.filter(item => item.file !== originalPath));
        alert("Success: File Restored.");
      }
    } catch (err) {
      alert("Restore error - check console.");
    }
  };

  const threats = results.filter(r => r.status?.includes("INFECTED")).length;
  const suspicious = results.filter(r => r.status === "SUSPICIOUS").length;

  useEffect(() => {
    // Only show items in vault if they were successfully moved
    const q = results.filter(r => r.action === "QUARANTINED" && r.quarantined);
    setQuarantine(q);
  }, [results]);

  return (
    <div style={{ background: "#0a0a0a", color: "white", minHeight: "100vh", padding: "30px", fontFamily: "monospace" }}>
      {/* HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #333", paddingBottom: "10px" }}>
        <h1 style={{ margin: 0, color: "#f1c40f" }}>🛡️ HORNET DEFENCE</h1>
        <button
          onClick={() => setProtection(!protection)}
          style={{
            background: protection ? "#27ae60" : "#c0392b",
            color: "white", border: "none", padding: "10px 20px", borderRadius: "4px", cursor: "pointer", fontWeight: "bold"
          }}
        >
          {protection ? "PROTECTION ACTIVE" : "PROTECTION DISABLED"}
        </button>
      </div>

      {/* DASHBOARD STATS */}
      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        <div style={{ flex: 1, background: "#1a1a1a", padding: "15px", borderRadius: "8px" }}>
          <p style={{ margin: 0, color: "#888" }}>System Status</p>
          <h2 style={{ margin: "5px 0", color: status.includes("Scanning") ? "#3498db" : "#fff" }}>{status}</h2>
        </div>
        <div style={{ flex: 1, background: "#1a1a1a", padding: "15px", borderRadius: "8px", borderLeft: "4px solid red" }}>
          <p style={{ margin: 0, color: "#888" }}>Threats</p>
          <h2 style={{ margin: "5px 0", color: "red" }}>{threats}</h2>
        </div>
        <div style={{ flex: 1, background: "#1a1a1a", padding: "15px", borderRadius: "8px", borderLeft: "4px solid orange" }}>
          <p style={{ margin: 0, color: "#888" }}>Suspicious</p>
          <h2 style={{ margin: "5px 0", color: "orange" }}>{suspicious}</h2>
        </div>
      </div>

      {/* ACTION PANEL */}
      <div style={{ marginTop: "20px" }}>
        <button 
          onClick={runScan} 
          disabled={status.includes("Scanning")}
          style={{ padding: "10px 20px", background: "#3498db", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", opacity: status.includes("Scanning") ? 0.5 : 1 }}
        >
          Full System Scan
        </button>
      </div>

      {/* SCAN RESULTS */}
      <div style={{ marginTop: "30px" }}>
        <h2>Live Logs</h2>
        {results.map((item, i) => (
          <div key={i} style={{
              padding: "15px", marginBottom: "10px", borderRadius: "5px",
              background: item.status?.includes("INFECTED") ? "#2c0000" : item.status === "SUSPICIOUS" ? "#2c1a00" : "#001a00",
              border: `1px solid ${item.status?.includes("INFECTED") ? "red" : item.status === "SUSPICIOUS" ? "orange" : "green"}`
            }}>
            <p style={{ margin: "0 0 5px 0" }}><strong>{item.file}</strong></p>
            <p style={{ margin: 0, fontSize: "0.9em" }}>Status: {item.status} {item.engine_hits > 0 && `| ${item.engine_hits} Engines`}</p>
            {item.reasons?.map((r, idx) => (
              <p key={idx} style={{ color: "orange", fontSize: "0.8em", margin: "5px 0 0 0" }}>⚠️ {r}</p>
            ))}
          </div>
        ))}
      </div>

      {/* QUARANTINE VAULT */}
      <div style={{ marginTop: "40px", padding: "20px", background: "#111", borderRadius: "10px", border: "1px dashed #444" }}>
        <h2 style={{ color: "#e74c3c" }}>☣️ Quarantine Vault</h2>
        {quarantine.length === 0 && <p style={{ color: "#444" }}>Vault is empty.</p>}
        {quarantine.map((q, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#222", padding: "10px", marginBottom: "10px", borderRadius: "4px" }}>
            <span style={{ fontSize: "0.8em", overflow: "hidden", textOverflow: "ellipsis" }}>{q.file}</span>
            <div>
              <button onClick={() => handleRestore(q.quarantined, q.file)} style={{ background: "#27ae60", color: "white", border: "none", padding: "5px 10px", borderRadius: "3px", cursor: "pointer", marginRight: "5px" }}>Restore</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

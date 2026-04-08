import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [results, setResults] = useState([]);
  const [quarantine, setQuarantine] = useState([]);
  const [status, setStatus] = useState("Idle");
  const [progress, setProgress] = useState(0);
  const [protection, setProtection] = useState(true);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "usb_scan") {
        setResults((prev) => [...data.results, ...prev]);
        setStatus("USB Threat Detected!");
      }
    };
    return () => ws.close();
  }, []);

  const runScan = async () => {
    setResults([]);
    setProgress(0);
    setStatus("Scanning...");
    
    try {
      await axios.get("http://localhost:8000/scan");
      
      // Since background_tasks are used, we simulate progress 
      // In a pro app, the backend would send progress via WebSocket
      let p = 0;
      const interval = setInterval(() => {
        p += 5;
        setProgress(p);
        if (p >= 100) {
          clearInterval(interval);
          setStatus("Scan Complete");
        }
      }, 800); // Adjust based on expected scan time
      
    } catch (err) {
      setStatus("Scan Failed");
    }
  };

  const handleDelete = async (quarantinedPath) => {
    if (!window.confirm("PERMANENT DELETE: Are you sure?")) return;
    try {
      const res = await axios.post("http://localhost:8000/delete-quarantine", {
        quarantined_path: quarantinedPath
      });
      if (res.data.status === "DELETED") {
        setResults(prev => prev.filter(item => item.quarantined !== quarantinedPath));
        alert("File permanently erased.");
      }
    } catch (err) { alert("Delete failed."); }
  };

  const handleRestore = async (quarantinedPath, originalPath) => {
    try {
      const res = await axios.post("http://localhost:8000/restore", {
        quarantined_path: quarantinedPath,
        original_path: originalPath
      });
      if (res.data.status === "RESTORED") {
        setResults(prev => prev.filter(item => item.file !== originalPath));
        alert("File restored successfully.");
      }
    } catch (err) { alert("Restore failed."); }
  };

  useEffect(() => {
    setQuarantine(results.filter(r => r.action === "QUARANTINED" && r.quarantined));
  }, [results]);

  return (
    <div style={{ background: "#0a0a0a", color: "white", minHeight: "100vh", padding: "30px", fontFamily: "monospace" }}>
      
      {/* HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #333", paddingBottom: "10px" }}>
        <h1 style={{ margin: 0, color: "#f1c40f" }}>🛡️ HORNET DEFENCE</h1>
        <button onClick={() => setProtection(!protection)} style={{ background: protection ? "#27ae60" : "#c0392b", color: "white", padding: "10px 20px", border: "none", borderRadius: "4px", cursor: "pointer" }}>
          {protection ? "PROTECTION ACTIVE" : "PROTECTION OFF"}
        </button>
      </div>

      {/* PROGRESS BAR */}
      {status === "Scanning..." && (
        <div style={{ marginTop: "20px" }}>
          <div style={{ background: "#222", height: "8px", borderRadius: "4px", overflow: "hidden" }}>
            <div style={{ background: "#f1c40f", height: "100%", width: `${progress}%`, transition: "width 0.3s" }}></div>
          </div>
          <p style={{ fontSize: "12px", color: "#888" }}>Engine processing: {progress}%</p>
        </div>
      )}

      {/* DASHBOARD STATS */}
      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        <div style={{ flex: 1, background: "#111", padding: "15px", borderRadius: "8px", border: "1px solid #333" }}>
          <p style={{ margin: 0, color: "#555" }}>System Status</p>
          <h3 style={{ margin: "5px 0" }}>{status}</h3>
        </div>
        <div style={{ flex: 1, background: "#111", padding: "15px", borderRadius: "8px", borderLeft: "4px solid red" }}>
          <p style={{ margin: 0, color: "#555" }}>Threats</p>
          <h3 style={{ margin: "5px 0", color: "red" }}>{results.filter(r => r.status?.includes("INFECTED")).length}</h3>
        </div>
      </div>

      <button onClick={runScan} style={{ marginTop: "20px", padding: "10px 20px", background: "#3498db", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
        Initiate Full Scan
      </button>

      {/* QUARANTINE VAULT */}
      <div style={{ marginTop: "40px", padding: "20px", background: "#0a0a0a", border: "1px dashed #e74c3c", borderRadius: "8px" }}>
        <h2 style={{ color: "#e74c3c", marginTop: 0 }}>☣️ Quarantine Vault</h2>
        {quarantine.length === 0 ? <p style={{ color: "#444" }}>No threats in isolation.</p> : 
          quarantine.map((q, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", background: "#111", padding: "10px", marginBottom: "10px", borderRadius: "4px", border: "1px solid #222" }}>
              <span style={{ fontSize: "12px", color: "#ccc" }}>{q.file}</span>
              <div>
                <button onClick={() => handleRestore(q.quarantined, q.file)} style={{ background: "#27ae60", color: "white", border: "none", padding: "5px 10px", borderRadius: "3px", cursor: "pointer", marginRight: "10px" }}>Restore</button>
                <button onClick={() => handleDelete(q.quarantined)} style={{ background: "#c0392b", color: "white", border: "none", padding: "5px 10px", borderRadius: "3px", cursor: "pointer" }}>Delete</button>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}

export default App;

import { useEffect, useState, useRef } from "react";
import axios from "axios";

// 📟 TACTICAL MATRIX TERMINAL COMPONENT
const TacticalTerminal = ({ logs }) => {
  const logEndRef = useRef(null);
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div style={{
      background: "#050505",
      color: "#00ff41",
      padding: "15px",
      borderRadius: "5px",
      fontFamily: "'Courier New', Courier, monospace",
      height: "180px",
      overflowY: "auto",
      border: "1px solid #003300",
      boxShadow: "inset 0 0 10px #000",
      fontSize: "12px",
      marginTop: "20px",
      lineHeight: "1.4"
    }}>
      <div style={{ color: "#008f11", borderBottom: "1px solid #003300", marginBottom: "8px", fontWeight: "bold" }}>
        📡 DIRECT AGENT UPLINK -- SECURE_CHANNEL_ACTIVE
      </div>
      {logs.map((log, i) => (
        <div key={i} style={{ marginBottom: "2px" }}>
          <span style={{ color: "#004400" }}>{">"}</span> {log}
        </div>
      ))}
      <div ref={logEndRef} />
    </div>
  );
};

function App() {
  const [results, setResults] = useState([]);
  const [quarantine, setQuarantine] = useState([]);
  const [status, setStatus] = useState("Idle");
  const [progress, setProgress] = useState(0);
  const [protection, setProtection] = useState(true);
  
  // SWAT AGENT LOGS
  const [tacticalLogs, setTacticalLogs] = useState(["[SYSTEM]: Initializing SWAT Framework...", "[SYSTEM]: Agents VANGUARD, INTERCEPTOR, and WARDEN standing by."]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // 1. Handle Agent Personalities
      if (data.type === "agent_msg") {
        setTacticalLogs(prev => [...prev, data.text]);
      }

      // 2. Handle USB Scout Events
      if (data.type === "usb_scan") {
        setResults((prev) => [...data.results, ...prev]);
        setStatus("USB Event Detected");
      }
    };

    ws.onclose = () => setTacticalLogs(prev => [...prev, "❌ [CRITICAL]: Uplink lost. Backend unreachable."]);
    
    return () => ws.close();
  }, []);

  const runScan = async () => {
    setResults([]);
    setProgress(0);
    setStatus("Scanning...");
    
    try {
      await axios.get("http://localhost:8000/scan");
      
      // Progress simulation for UX
      let p = 0;
      const interval = setInterval(() => {
        p += 2;
        setProgress(p);
        if (p >= 100) {
          clearInterval(interval);
          setStatus("Scan Complete");
        }
      }, 500);
      
    } catch (err) {
      setStatus("Scan Failed");
      setTacticalLogs(prev => [...prev, "⚠️ [INTERCEPTOR]: Tactical sweep aborted. Connection error."]);
    }
  };

  const handleDelete = async (quarantinedPath) => {
    if (!window.confirm("PERMANENT DELETE: This will shred the file. Proceed?")) return;
    try {
      const res = await axios.post("http://localhost:8000/delete-quarantine", {
        quarantined_path: quarantinedPath
      });
      if (res.data.status === "DELETED") {
        setResults(prev => prev.filter(item => item.quarantined !== quarantinedPath));
      }
    } catch (err) { alert("Delete failed."); }
  };

  const handleRestore = async (quarantinedPath, originalPath, fileHash) => {
    try {
      const res = await axios.post("http://localhost:8000/restore", {
        quarantined_path: quarantinedPath,
        original_path: originalPath,
        file_hash: fileHash // Pass hash so agents "Learn" to trust it
      });
      if (res.data.status === "RESTORED") {
        setResults(prev => prev.filter(item => item.file !== originalPath));
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
        <h1 style={{ margin: 0, color: "#f1c40f", letterSpacing: "2px" }}>🛡️ HORNET DEFENCE</h1>
        <button 
          onClick={() => setProtection(!protection)} 
          style={{ 
            background: protection ? "rgba(39, 174, 96, 0.2)" : "rgba(192, 57, 43, 0.2)", 
            color: protection ? "#27ae60" : "#c0392b",
            border: `1px solid ${protection ? "#27ae60" : "#c0392b"}`, 
            padding: "10px 20px", borderRadius: "4px", cursor: "pointer", fontWeight: "bold"
          }}
        >
          {protection ? "SHIELD ACTIVE" : "SHIELD DOWN"}
        </button>
      </div>

      {/* MATRIX TERMINAL */}
      <TacticalTerminal logs={tacticalLogs} />

      {/* PROGRESS BAR */}
      {status === "Scanning..." && (
        <div style={{ marginTop: "20px" }}>
          <div style={{ background: "#111", height: "4px", borderRadius: "2px", overflow: "hidden", border: "1px solid #333" }}>
            <div style={{ background: "#f1c40f", height: "100%", width: `${progress}%`, transition: "width 0.4s", boxShadow: "0 0 10px #f1c40f" }}></div>
          </div>
        </div>
      )}

      {/* DASHBOARD STATS */}
      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        <div style={{ flex: 1, background: "#0f0f0f", padding: "15px", borderRadius: "8px", border: "1px solid #222" }}>
          <p style={{ margin: 0, color: "#555", fontSize: "10px", textTransform: "uppercase" }}>Deployment Status</p>
          <h3 style={{ margin: "5px 0", color: "#3498db" }}>{status}</h3>
        </div>
        <div style={{ flex: 1, background: "#0f0f0f", padding: "15px", borderRadius: "8px", border: "1px solid #222", borderLeft: "4px solid #e74c3c" }}>
          <p style={{ margin: 0, color: "#555", fontSize: "10px", textTransform: "uppercase" }}>Neutralized</p>
          <h3 style={{ margin: "5px 0", color: "#e74c3c" }}>{results.filter(r => r.status?.includes("INFECTED")).length}</h3>
        </div>
      </div>

      <button 
        onClick={runScan} 
        disabled={status === "Scanning..."}
        style={{ 
            marginTop: "20px", width: "100%", padding: "12px", 
            background: "transparent", color: "#3498db", border: "1px solid #3498db", 
            borderRadius: "4px", cursor: "pointer", fontWeight: "bold",
            opacity: status === "Scanning..." ? 0.5 : 1
        }}
      >
        [ EXECUTE FULL SECTOR SCAN ]
      </button>

      {/* QUARANTINE VAULT */}
      <div style={{ marginTop: "40px", padding: "20px", background: "#050505", border: "1px solid #e74c3c", borderRadius: "8px", boxShadow: "0 0 15px rgba(231, 76, 60, 0.1)" }}>
        <h2 style={{ color: "#e74c3c", marginTop: 0, fontSize: "18px" }}>☣️ QUARANTINE VAULT</h2>
        {quarantine.length === 0 ? <p style={{ color: "#333" }}>Vault empty. Perimeter secure.</p> : 
          quarantine.map((q, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#0a0a0a", padding: "12px", marginBottom: "8px", borderRadius: "4px", border: "1px solid #222" }}>
              <div style={{ overflow: "hidden" }}>
                <p style={{ margin: 0, fontSize: "12px", color: "#eee" }}>{q.file}</p>
                <small style={{ color: "#555" }}>Hash: {q.file_hash?.substring(0, 12)}...</small>
              </div>
              <div style={{ display: "flex", gap: "10px" }}>
                <button onClick={() => handleRestore(q.quarantined, q.file, q.file_hash)} style={{ background: "#27ae60", color: "white", border: "none", padding: "6px 12px", borderRadius: "3px", cursor: "pointer", fontSize: "11px" }}>RESTORE</button>
                <button onClick={() => handleDelete(q.quarantined)} style={{ background: "#c0392b", color: "white", border: "none", padding: "6px 12px", borderRadius: "3px", cursor: "pointer", fontSize: "11px" }}>SHRED</button>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}

export default App;

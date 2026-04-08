import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [results, setResults] = useState([]); 
  const [usbResults, setUsbResults] = useState([]); 
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "usb_scan") {
        setUsbResults(data.results);
      }
    };
    return () => ws.close();
  }, []);

  const runScan = async () => {
    setLoading(true);
    try {
      const res = await axios.get("http://localhost:8000/scan");
      setResults(res.data.files || res.data.results || []);
    } catch (err) {
      console.error("Scan failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (quarantinedPath, originalPath) => {
    try {
      const res = await axios.post("http://localhost:8000/restore", {
        quarantined_path: quarantinedPath,
        original_path: originalPath
      });
      alert(res.data.status === "RESTORED" ? "File restored successfully!" : "Restore failed.");
      // Refresh list logic could go here
    } catch (err) {
      console.error("Restore error:", err);
    }
  };

  return (
    <div style={{ padding: "40px", fontFamily: "sans-serif", backgroundColor: "#f4f4f9", minHeight: "100vh" }}>
      <h1 style={{ color: "#2c3e50" }}>🐝 Hornet Defence</h1>

      {/* Manual Scan Section */}
      <section style={{ marginBottom: "40px", padding: "20px", background: "white", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
        <h2>System Scanner</h2>
        <button 
          onClick={runScan} 
          disabled={loading}
          style={{ 
            padding: "10px 20px", 
            backgroundColor: loading ? "#bdc3c7" : "#2980b9", 
            color: "white", border: "none", borderRadius: "4px", cursor: loading ? "not-allowed" : "pointer" 
          }}
        >
          {loading ? "Scanning Engine Active..." : "Start System Scan"}
        </button>

        <h3>Scan Results</h3>
        <ul style={{ listStyle: "none", paddingLeft: 0 }}>
          {results.map((item, i) => (
            <li key={i} style={{ 
              padding: "15px", 
              borderBottom: "1px solid #eee", 
              color: item.status === "SAFE" ? "#27ae60" : "#d63031",
              backgroundColor: item.status === "SUSPICIOUS" ? "#fff9db" : "transparent"
            }}>
              <div>
                <strong>{item.file}</strong> — <span>{item.status}</span>
                
                {/* Heuristic Reasons Update */}
                {item.reasons && (
                  <ul style={{ fontSize: "0.85em", color: "#e67e22", margin: "5px 0" }}>
                    {item.reasons.map((r, idx) => (
                      <li key={idx} style={{ listStyle: "none" }}>⚠️ {r}</li>
                    ))}
                  </ul>
                )}

                {item.engine_hits && <span style={{ color: "#e67e22" }}> ({item.engine_hits} engines flagged)</span>}
                {item.action && <span style={{ fontWeight: "bold", color: "#34495e" }}> → {item.action}</span>}
                
                {/* Restore Button Logic */}
                {item.status?.includes("INFECTED") && item.action === "QUARANTINED" && (
                  <button 
                    onClick={() => handleRestore(item.quarantined, item.file)}
                    style={{ marginLeft: "15px", fontSize: "0.7em", padding: "2px 5px", cursor: "pointer" }}
                  >
                    Undo/Restore
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      </section>

      {/* Auto USB Scan Section */}
      <section style={{ padding: "20px", background: "#2d3436", color: "white", borderRadius: "8px" }}>
        <h2>Live USB Monitor (Auto)</h2>
        {usbResults.length === 0 ? (
          <p style={{ color: "#b2bec3" }}>Monitoring for hardware events...</p>
        ) : (
          <ul style={{ listStyle: "none", paddingLeft: 0 }}>
            {usbResults.map((item, i) => (
              <li key={i} style={{ color: "#fab1a0", padding: "5px 0" }}>
                ⚠️ {typeof item === 'string' ? item : item.file} — {item.status}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;

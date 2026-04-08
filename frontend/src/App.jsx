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
            color: "white", 
            border: "none", 
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer" 
          }}
        >
          {loading ? "Scanning Engine Active..." : "Start System Scan"}
        </button>

        <h3>Manual Results</h3>
        <ul style={{ listStyle: "none", paddingLeft: 0 }}>
          {results.map((item, i) => (
            <li key={i} style={{ 
              padding: "10px", 
              borderBottom: "1px solid #eee", 
              color: item.status?.includes("INFECTED") ? "#d63031" : "#27ae60"
            }}>
              {/* The core update: File info, Status, VT Hits, and the Action taken */}
              <strong>{item.file}</strong> — {item.status}
              {item.engine_hits && <span style={{ color: "#e67e22" }}> ({item.engine_hits} engines flagged)</span>}
              {item.action && <span style={{ fontStyle: "italic", color: "#34495e" }}> → {item.action}</span>}
            </li>
          ))}
        </ul>
      </section>

      {/* Auto USB Scan Section */}
      <section style={{ padding: "20px", background: "#2d3436", color: "white", borderRadius: "8px" }}>
        <h2>Live USB Monitor (Auto)</h2>
        {usbResults.length === 0 ? (
          <p style={{ color: "#b2bec3" }}>System clear. Monitoring for external drives...</p>
        ) : (
          <ul style={{ listStyle: "none", paddingLeft: 0 }}>
            {usbResults.map((item, i) => (
              <li key={i} style={{ color: "#fab1a0", padding: "5px 0" }}>
                ⚠️ {typeof item === 'string' ? item : item.file}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;

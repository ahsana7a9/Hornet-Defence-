import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [results, setResults] = useState([]); // For Manual Scans
  const [usbResults, setUsbResults] = useState([]); // For WebSocket USB Scans
  const [loading, setLoading] = useState(false);

  // --- WebSocket Logic for Real-time USB Monitoring ---
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

  // --- HTTP Logic for Manual System Scan ---
  const runScan = async () => {
    setLoading(true);
    try {
      const res = await axios.get("http://localhost:8000/scan");
      // Mapping to 'files' or 'results' depending on your FastAPI return key
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
          style={{ padding: "10px 20px", cursor: loading ? "not-allowed" : "pointer" }}
        >
          {loading ? "Scanning..." : "Start System Scan"}
        </button>

        <h3>Manual Results</h3>
        <ul style={{ listStyle: "none", paddingLeft: 0 }}>
          {results.map((item, i) => (
            <li key={i} style={{ 
              padding: "8px", 
              borderBottom: "1px solid #eee", 
              color: item.status?.includes("INFECTED") ? "#d63031" : "#27ae60",
              fontWeight: item.status?.includes("INFECTED") ? "bold" : "normal"
            }}>
              {item.file} — <strong>{item.status}</strong>
              {item.engine_hits && ` (${item.engine_hits} engines flagged)`}
            </li>
          ))}
        </ul>
      </section>

      {/* Auto USB Scan Section */}
      <section style={{ padding: "20px", background: "#2d3436", color: "white", borderRadius: "8px" }}>
        <h2>Live USB Monitor (Auto)</h2>
        {usbResults.length === 0 ? (
          <p style={{ color: "#b2bec3" }}>No USB threats detected. Waiting for insertion...</p>
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

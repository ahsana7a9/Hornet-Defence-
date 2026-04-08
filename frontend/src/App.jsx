// (Keep previous imports)

function App() {
  // ... existing state ...

  const handleDelete = async (quarantinedPath) => {
    if (!window.confirm("PERMANENT DELETE: Are you sure?")) return;
    
    try {
      const res = await axios.post("http://localhost:8000/delete-quarantine", {
        quarantined_path: quarantinedPath
      });
      
      if (res.data.status === "DELETED") {
        // Remove from the results to clear the UI
        setResults(prev => prev.filter(item => item.quarantined !== quarantinedPath));
        alert("File erased from disk.");
      }
    } catch (err) {
      alert("Delete failed.");
    }
  };

  return (
    <div style={{ background: "#0a0a0a", color: "white", minHeight: "100vh", padding: "30px", fontFamily: "monospace" }}>
      {/* ... previous Dashboard and Scan Results code ... */}

      {/* QUARANTINE VAULT */}
      <div style={{ marginTop: "40px", padding: "20px", background: "#111", borderRadius: "10px", border: "1px dashed #444" }}>
        <h2 style={{ color: "#e74c3c" }}>☣️ Quarantine Vault</h2>
        {quarantine.length === 0 && <p style={{ color: "#444" }}>Vault is empty.</p>}
        {quarantine.map((q, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#222", padding: "10px", marginBottom: "10px", borderRadius: "4px" }}>
            <span style={{ fontSize: "0.8em" }}>{q.file}</span>
            <div>
              <button 
                onClick={() => handleRestore(q.quarantined, q.file)} 
                style={{ background: "#27ae60", color: "white", border: "none", padding: "5px 10px", borderRadius: "3px", cursor: "pointer", marginRight: "5px" }}
              >
                Restore
              </button>
              
              {/* NEW: Delete Button */}
              <button 
                onClick={() => handleDelete(q.quarantined)} 
                style={{ background: "#c0392b", color: "white", border: "none", padding: "5px 10px", borderRadius: "3px", cursor: "pointer" }}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

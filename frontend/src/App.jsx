import { useState } from "react";
import axios from "axios";

function App() {

  const [results, setResults] = useState([]);

  const runScan = async () => {
    const res = await axios.get("http://localhost:8000/scan");
    setResults(res.data.results);
  };

  return (
    <div style={{padding:"40px"}}>

      <h1>Hornet Defence</h1>

      <button onClick={runScan}>
        Start Scan
      </button>

      <h2>Scan Results</h2>

    <ul>
  {results.map((item, i) => (
    <li key={i}>
      {item.file} — {item.status}
      {item.engine_hits && ` (${item.engine_hits} engines flagged)`}
    </li>
  ))}
</ul>

    </div>
  );
}

export default App;

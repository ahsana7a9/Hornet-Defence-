import { useState } from "react";
import axios from "axios";

function App() {

  const [result,setResult] = useState([]);

  const runScan = async () => {
    const res = await axios.get("http://localhost:8000/scan");
    setResult(res.data.files);
  }

  return (
    <div style={{padding:"40px"}}>

      <h1>Hornet Defence</h1>

      <button onClick={runScan}>
        Start System Scan
      </button>

      <h2>Scan Results</h2>

      <ul>
        {result.map((file,i)=>(
          <li key={i}>{file}</li>
        ))}
      </ul>

    </div>
  );
}

export default App;

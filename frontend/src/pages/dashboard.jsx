import { useEffect, useState } from "react";
import { getStatus } from "../services/api";
import SwarmGraph from "../components/SwarmGraph";

export default function Dashboard() {
  const [status, setStatus] = useState("");

  useEffect(() => {
    getStatus().then((data) => {
      setStatus(data.msg);
    });
  }, []);

  return (
    <div style={{ background: "black", color: "white", height: "100vh" }}>
      <h1>ShadowMesh Command Center</h1>

      <p>Backend Status: {status}</p>

      <SwarmGraph />
    </div>
  );
}

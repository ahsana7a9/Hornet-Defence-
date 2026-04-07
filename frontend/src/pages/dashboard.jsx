import SwarmGraph from "../components/SwarmGraph";

export default function Dashboard() {
  return (
    <div style={{ background: "black", color: "white", height: "100vh" }}>
      <h1>ShadowMesh Command Center</h1>
      <SwarmGraph />
    </div>
  );
}

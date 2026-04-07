import { useEffect, useRef } from "react";

export default function SwarmGraph() {
  const canvasRef = useRef(null);
  const animRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;

    const nodes = [
      { id: "Agent-1", x: 150, y: 100, vx: 0.5, vy: 0.3, color: "#00ff88", r: 10, type: "agent" },
      { id: "Agent-2", x: 450, y: 280, vx: -0.4, vy: 0.6, color: "#00aaff", r: 10, type: "agent" },
      { id: "Threat-1", x: 300, y: 200, vx: 0.2, vy: -0.5, color: "#ff4444", r: 14, type: "threat" },
      { id: "Recon", x: 80, y: 300, vx: 0.6, vy: -0.2, color: "#ffaa00", r: 8, type: "agent" },
      { id: "Brute", x: 520, y: 120, vx: -0.3, vy: 0.4, color: "#aa00ff", r: 8, type: "agent" },
    ];

    const links = [
      [0, 2], [1, 2], [3, 2], [4, 2]
    ];

    function draw() {
      ctx.fillStyle = "rgba(10,10,15,0.3)";
      ctx.fillRect(0, 0, W, H);

      links.forEach(([a, b]) => {
        const na = nodes[a], nb = nodes[b];
        ctx.beginPath();
        ctx.strokeStyle = "rgba(255,68,68,0.3)";
        ctx.lineWidth = 1;
        ctx.moveTo(na.x, na.y);
        ctx.lineTo(nb.x, nb.y);
        ctx.stroke();
      });

      nodes.forEach(n => {
        n.x += n.vx;
        n.y += n.vy;
        if (n.x < n.r || n.x > W - n.r) n.vx *= -1;
        if (n.y < n.r || n.y > H - n.r) n.vy *= -1;

        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.shadowColor = n.color;
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.fillStyle = "#fff";
        ctx.font = "10px monospace";
        ctx.fillText(n.id, n.x + n.r + 3, n.y + 4);
      });

      animRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(animRef.current);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={300}
      style={{
        border: "1px solid #1a1a2e",
        borderRadius: "8px",
        background: "#0a0a0f",
        display: "block"
      }}
    />
  );
}

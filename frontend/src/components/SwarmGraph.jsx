import { useEffect, useRef } from "react";

const NODE_TYPES = {
  agent:   { color: "#00ff88", r: 10 },
  threat:  { color: "#ff2244", r: 14 },
  scanner: { color: "#ff6600", r: 11 },
  burst:   { color: "#ffaa00", r: 11 },
  recon:   { color: "#00aaff", r: 10 },
  brute:   { color: "#aa44ff", r: 10 },
  log:     { color: "#44ffaa", r: 9  },
};

const DEFAULT_NODES = [
  { id: "ReconAgent",  type: "agent",  vx: 0.5,  vy: 0.3  },
  { id: "BruteAgent",  type: "brute",  vx: -0.4, vy: 0.5  },
  { id: "LogAgent",    type: "log",    vx: 0.3,  vy: -0.4 },
  { id: "Threat-Hub",  type: "threat", vx: 0.1,  vy: 0.2  },
  { id: "Recon-2",     type: "recon",  vx: -0.3, vy: -0.3 },
];

export default function SwarmGraph({ realNodes = [] }) {
  const canvasRef = useRef(null);
  const animRef   = useRef(null);
  const nodesRef  = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const W = canvas.width;
    const H = canvas.height;
    const ctx = canvas.getContext("2d");

    // Merge default agent nodes with real threat nodes
    const agentNodes = DEFAULT_NODES.map((n, i) => ({
      ...n,
      x: 80 + (i % 3) * 180,
      y: 50 + Math.floor(i / 3) * 130,
    }));

    const realThreatNodes = realNodes.slice(0, 6).map((n, i) => ({
      id:   n.id,
      type: n.type || "threat",
      x:    60 + (i % 4) * 130,
      y:    70 + Math.floor(i / 4) * 100,
      vx:   (Math.random() - 0.5) * 0.8,
      vy:   (Math.random() - 0.5) * 0.8,
    }));

    nodesRef.current = [...agentNodes, ...realThreatNodes];

    // Links: each agent → threat hub + each real node → nearest agent
    const agentCount = agentNodes.length;
    const links = agentNodes.slice(0, 3).map((_, i) => [i, 3]);
    realThreatNodes.forEach((_, ri) => {
      links.push([agentCount + ri, ri % 3]);
    });

    function draw() {
      ctx.fillStyle = "rgba(8,8,16,0.35)";
      ctx.fillRect(0, 0, W, H);

      const nodes = nodesRef.current;

      // Draw links
      links.forEach(([a, b]) => {
        if (!nodes[a] || !nodes[b]) return;
        ctx.beginPath();
        ctx.strokeStyle = "rgba(255,34,68,0.2)";
        ctx.lineWidth   = 1;
        ctx.moveTo(nodes[a].x, nodes[a].y);
        ctx.lineTo(nodes[b].x, nodes[b].y);
        ctx.stroke();
      });

      // Draw nodes
      nodes.forEach(n => {
        const cfg = NODE_TYPES[n.type] || NODE_TYPES.agent;

        n.x += n.vx;
        n.y += n.vy;
        if (n.x < cfg.r || n.x > W - cfg.r) n.vx *= -1;
        if (n.y < cfg.r || n.y > H - cfg.r) n.vy *= -1;

        // Glow
        ctx.shadowColor = cfg.color;
        ctx.shadowBlur  = n.type === "threat" ? 20 : 12;

        ctx.beginPath();
        ctx.arc(n.x, n.y, cfg.r, 0, Math.PI * 2);
        ctx.fillStyle = cfg.color;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Label
        const label = n.id.length > 14 ? n.id.slice(0, 13) + "…" : n.id;
        ctx.fillStyle = "#aaa";
        ctx.font = "9px monospace";
        ctx.fillText(label, n.x + cfg.r + 3, n.y + 4);
      });

      animRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(animRef.current);
  }, [realNodes]);

  return (
    <canvas
      ref={canvasRef}
      width={580}
      height={260}
      style={{ background: "#08080f", borderRadius: "6px", display: "block", width: "100%" }}
    />
  );
}

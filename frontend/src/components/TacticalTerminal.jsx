import { useEffect, useRef } from "react";

const TacticalTerminal = ({ logs }) => {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="bg-black/80 border border-green-900/30 p-4 rounded-lg font-mono text-[11px] h-48 overflow-y-auto shadow-inner text-green-400">
      <div className="text-green-700 border-b border-green-900/20 mb-2 pb-1 uppercase tracking-widest text-[10px]">
        Live Agent Uplink Established
      </div>
      {logs.map((log, i) => (
        <div key={i} className="mb-1 opacity-90">
          <span className="text-green-900 mr-2">»</span>{log}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
};

export default TacticalTerminal;
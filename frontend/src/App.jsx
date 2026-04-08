import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, ShieldAlert, Settings, Activity, Trash2, RotateCcw, BrainCircuit, Zap } from "lucide-react";

// --- COMPONENTS ---

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <div 
    onClick={onClick}
    className={`flex items-center gap-3 px-4 py-3 cursor-pointer transition-all ${
      active ? "bg-blue-600/20 text-blue-400 border-r-2 border-blue-500" : "text-gray-500 hover:text-gray-300"
    }`}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </div>
);

const TacticalTerminal = ({ logs }) => {
  const endRef = useRef(null);
  useEffect(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), [logs]);

  return (
    <div className="bg-black/80 border border-green-900/30 p-4 rounded-lg font-mono text-[11px] h-48 overflow-y-auto shadow-inner text-green-400">
      <div className="text-green-700 border-b border-green-900/20 mb-2 pb-1 uppercase tracking-widest text-[10px]">
        Live Agent Uplink Established
      </div>
      {logs.map((log, i) => <div key={i} className="mb-1 opacity-90"><span className="text-green-900 mr-2">»</span>{log}</div>)}
      <div ref={endRef} />
    </div>
  );
};

const ShieldStatus = ({ threatCount }) => (
  <div className="flex flex-col items-center justify-center py-6">
    <div className="relative">
      <motion.div
        animate={{ scale: [1, 1.15, 1], opacity: [0.2, 0.4, 0.2] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        className={`absolute inset-0 rounded-full blur-2xl ${threatCount > 0 ? "bg-red-500" : "bg-blue-600"}`}
      />
      <div className={`relative w-24 h-24 rounded-full border-2 bg-black flex items-center justify-center shadow-2xl ${threatCount > 0 ? "border-red-500/50" : "border-blue-500/50"}`}>
        <Shield size={32} className={threatCount > 0 ? "text-red-500" : "text-blue-400"} />
      </div>
    </div>
    <p className="mt-4 font-mono text-[10px] tracking-widest text-gray-500 uppercase">
      {threatCount > 0 ? "Perimeter Compromised" : "System Shield Active"}
    </p>
  </div>
);

// --- MAIN APP ---

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [results, setResults] = useState([]);
  const [tacticalLogs, setTacticalLogs] = useState(["[SYSTEM]: Service synchronized with Tray Icon."]);
  const [shreddingId, setShreddingId] = useState(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "agent_msg") setTacticalLogs(prev => [...prev, data.text]);
      if (data.type === "usb_scan") setResults(prev => [...data.results, ...prev]);
    };
    return () => ws.close();
  }, []);

  const handleShred = async (path) => {
    setShreddingId(path);
    setTimeout(async () => {
      try {
        await axios.post("http://localhost:8000/delete-quarantine", { quarantined_path: path });
        setResults(prev => prev.filter(r => r.quarantined !== path));
      } catch (err) {
        setTacticalLogs(prev => [...prev, " [WARDEN]: Shredding failed. Target resisted."]);
      }
      setShreddingId(null);
    }, 600);
  };

  const threatCount = results.filter(r => r.status?.includes("INFECTED")).length;

  return (
    <div className="flex h-screen bg-[#050505] text-gray-200 font-sans overflow-hidden">
      
      {/* SIDEBAR */}
      <nav className="w-64 bg-[#0a0a0a] border-r border-white/5 flex flex-col py-6">
        <div className="px-6 mb-10 flex items-center gap-3">
          <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center text-black font-bold italic shadow-lg shadow-yellow-500/20">H</div>
          <h1 className="text-lg font-bold tracking-tighter text-white uppercase italic">Hornet <span className="text-blue-500">SWAT</span></h1>
        </div>

        <div className="flex-1 space-y-1">
          <SidebarItem icon={Activity} label="Command Center" active={activeTab === "dashboard"} onClick={() => setActiveTab("dashboard")} />
          <SidebarItem icon={ShieldAlert} label="Quarantine" active={activeTab === "quarantine"} onClick={() => setActiveTab("quarantine")} />
          <SidebarItem icon={BrainCircuit} label="Intelligence" active={activeTab === "intelligence"} onClick={() => setActiveTab("intelligence")} />
          <SidebarItem icon={Settings} label="Settings" active={activeTab === "settings"} onClick={() => setActiveTab("settings")} />
        </div>

        <div className="px-6 mt-auto">
          <div className="p-4 bg-blue-500/5 border border-blue-500/20 rounded-xl text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
                <Zap size={12} className="text-blue-500 animate-pulse" />
                <p className="text-[10px] uppercase text-blue-500 font-bold">Vanguard Live</p>
            </div>
            <p className="text-[9px] text-gray-500">Real-time port monitoring active.</p>
          </div>
        </div>
      </nav>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 overflow-y-auto p-8 relative">
        <AnimatePresence mode="wait">
          
          {activeTab === "dashboard" && (
            <motion.div key="dashboard" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="max-w-4xl mx-auto space-y-6">
              <header className="flex justify-between items-end">
                <div>
                  <h2 className="text-3xl font-bold text-white">Dashboard</h2>
                  <p className="text-gray-500">Sector analysis and live agent communication.</p>
                </div>
                <button onClick={() => axios.get("http://localhost:8000/scan")} className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded-lg font-bold text-white transition-all shadow-lg shadow-blue-600/20 active:scale-95">
                  Execute Sector Scan
                </button>
              </header>

              <ShieldStatus threatCount={threatCount} />

              <div className="grid grid-cols-3 gap-6">
                <div className="bg-[#0f0f0f] p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity"><ShieldAlert size={40}/></div>
                  <p className="text-xs uppercase text-gray-500 font-bold tracking-widest">Active Threats</p>
                  <p className="text-4xl font-bold text-red-500 mt-2">{threatCount}</p>
                </div>
                <div className="bg-[#0f0f0f] p-6 rounded-2xl border border-white/5">
                  <p className="text-xs uppercase text-gray-500 font-bold tracking-widest">Agent Uptime</p>
                  <p className="text-4xl font-bold text-blue-400 mt-2">100%</p>
                </div>
              </div>

              <TacticalTerminal logs={tacticalLogs} />
            </motion.div>
          )}

          {activeTab === "quarantine" && (
            <motion.div key="quarantine" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold text-white mb-6 underline decoration-red-500/50 underline-offset-8 italic">Quarantine Vault</h2>
              <div className="space-y-3">
                <AnimatePresence>
                    {results.filter(r => r.quarantined).map((q, i) => (
                    <motion.div 
                        key={q.quarantined} 
                        layout
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: shreddingId === q.quarantined ? 0.5 : 1, x: 0 }}
                        exit={{ opacity: 0, scale: 0.9, x: 50, filter: "blur(10px)" }}
                        className="bg-[#0f0f0f] border border-white/5 p-4 rounded-xl flex justify-between items-center group hover:border-red-500/30 transition-all"
                    >
                        <div>
                        <p className="text-sm font-medium text-gray-200">{q.file.split('\\').pop()}</p>
                        <p className="text-[9px] text-gray-600 font-mono mt-1 uppercase tracking-tighter">{q.file}</p>
                        </div>
                        <div className="flex gap-2">
                        <button className="p-2 hover:bg-green-500/10 text-green-500 rounded-lg transition-all" title="Restore"><RotateCcw size={18} /></button>
                        <button 
                            onClick={() => handleShred(q.quarantined)}
                            className="p-2 hover:bg-red-500/10 text-red-500 rounded-lg transition-all" 
                            title="Shred Permanently"
                        >
                            <Trash2 size={18} />
                        </button>
                        </div>
                    </motion.div>
                    ))}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {activeTab === "intelligence" && (
            <motion.div key="intelligence" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto space-y-6">
                <h2 className="text-3xl font-bold text-white">Agent Intelligence</h2>
                <div className="bg-[#0f0f0f] border border-white/5 rounded-2xl p-8 text-center border-dashed">
                    <BrainCircuit size={48} className="mx-auto text-blue-500/30 mb-4" />
                    <h3 className="text-lg font-bold text-gray-300">Cognitive Learning Active</h3>
                    <p className="text-gray-500 text-sm max-w-sm mx-auto mt-2">Interceptor is currently building a whitelist of your specific system hashes to reduce false positives.</p>
                </div>
            </motion.div>
          )}

        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;

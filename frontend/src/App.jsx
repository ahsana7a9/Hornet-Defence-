import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, ShieldAlert, Settings, Activity, Trash2, RotateCcw, Terminal } from "lucide-react";

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

// --- MAIN APP ---

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [results, setResults] = useState([]);
  const [tacticalLogs, setTacticalLogs] = useState(["[SYSTEM]: Service synchronized with Tray Icon."]);
  const [status, setStatus] = useState("Idle");

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "agent_msg") setTacticalLogs(prev => [...prev, data.text]);
      if (data.type === "usb_scan") setResults(prev => [...data.results, ...prev]);
    };
    return () => ws.close();
  }, []);

  return (
    <div className="flex h-screen bg-[#050505] text-gray-200 font-sans overflow-hidden">
      
      {/* SIDEBAR */}
      <nav className="w-64 bg-[#0a0a0a] border-r border-white/5 flex flex-col py-6">
        <div className="px-6 mb-10 flex items-center gap-3">
          <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center text-black font-bold italic">H</div>
          <h1 className="text-lg font-bold tracking-tighter text-white">HORNET <span className="text-blue-500">DEFENCE</span></h1>
        </div>

        <div className="flex-1 space-y-1">
          <SidebarItem icon={Activity} label="Dashboard" active={activeTab === "dashboard"} onClick={() => setActiveTab("dashboard")} />
          <SidebarItem icon={ShieldAlert} label="Quarantine" active={activeTab === "quarantine"} onClick={() => setActiveTab("quarantine")} />
          <SidebarItem icon={Settings} label="Settings" active={activeTab === "settings"} onClick={() => setActiveTab("settings")} />
        </div>

        <div className="px-6 mt-auto">
          <div className="p-4 bg-green-500/5 border border-green-500/20 rounded-xl text-center">
            <p className="text-[10px] uppercase text-green-500 font-bold mb-1">Protection Live</p>
            <p className="text-[9px] text-gray-500 leading-tight">Vanguard & Interceptor are watching your ports.</p>
          </div>
        </div>
      </nav>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 overflow-y-auto p-8 relative">
        <AnimatePresence mode="wait">
          
          {/* DASHBOARD TAB */}
          {activeTab === "dashboard" && (
            <motion.div 
              key="dashboard"
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
              className="max-w-4xl mx-auto space-y-6"
            >
              <header className="flex justify-between items-end">
                <div>
                  <h2 className="text-3xl font-bold text-white">Command Center</h2>
                  <p className="text-gray-500">Real-time threat monitoring and agent comms.</p>
                </div>
                <button 
                  onClick={() => axios.get("http://localhost:8000/scan")}
                  className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded-lg font-bold text-white transition-all shadow-lg shadow-blue-600/20"
                >
                  Initiate Sector Scan
                </button>
              </header>

              <div className="grid grid-cols-3 gap-6">
                <div className="bg-[#0f0f0f] p-6 rounded-2xl border border-white/5">
                  <p className="text-xs uppercase text-gray-500 font-bold">Infections</p>
                  <p className="text-3xl font-bold text-red-500 mt-2">{results.filter(r => r.status?.includes("INFECTED")).length}</p>
                </div>
                {/* Add more stat cards here */}
              </div>

              <TacticalTerminal logs={tacticalLogs} />
            </motion.div>
          )}

          {/* QUARANTINE TAB */}
          {activeTab === "quarantine" && (
            <motion.div 
              key="quarantine"
              initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
              className="max-w-4xl mx-auto"
            >
              <h2 className="text-3xl font-bold text-white mb-6">☣️ Quarantine Vault</h2>
              <div className="space-y-3">
                {results.filter(r => r.quarantined).map((q, i) => (
                  <div key={i} className="bg-[#0f0f0f] border border-white/5 p-4 rounded-xl flex justify-between items-center group">
                    <div>
                      <p className="text-sm font-medium text-gray-200">{q.file.split('\\').pop()}</p>
                      <p className="text-[10px] text-gray-500 font-mono mt-1">{q.file}</p>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 hover:bg-green-500/10 text-green-500 rounded-lg transition-colors"><RotateCcw size={18} /></button>
                      <button className="p-2 hover:bg-red-500/10 text-red-500 rounded-lg transition-colors"><Trash2 size={18} /></button>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;

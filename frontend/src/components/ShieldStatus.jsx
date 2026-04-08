import { motion } from "framer-motion";
import { Shield } from "lucide-react";

const ShieldStatus = ({ threatCount }) => (
  <div className="flex flex-col items-center justify-center py-6">
    <div className="relative">
      <motion.div
        animate={{ scale: [1, 1.15, 1], opacity: [0.2, 0.4, 0.2] }}
        transition={{ duration: 3, repeat: Infinity }}
        className={`absolute inset-0 rounded-full blur-2xl ${threatCount > 0 ? "bg-red-500" : "bg-blue-600"}`}
      />
      <div className={`relative w-24 h-24 rounded-full border-2 bg-black flex items-center justify-center ${threatCount > 0 ? "border-red-500/50" : "border-blue-500/50"}`}>
        <Shield size={32} className={threatCount > 0 ? "text-red-500" : "text-blue-400"} />
      </div>
    </div>
  </div>
);

export default ShieldStatus;
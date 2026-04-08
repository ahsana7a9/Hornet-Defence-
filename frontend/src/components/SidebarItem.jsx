import React from "react";

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

export default SidebarItem;
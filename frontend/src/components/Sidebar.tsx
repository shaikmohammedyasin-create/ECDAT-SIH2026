import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();

  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: "dashboard" },
    { label: "New Scan", path: "/scan/new", icon: "play_circle" },
    { label: "Crypto Inventory", path: "/inventory", icon: "memory" },
    { label: "Finding Inspector", path: "/findings/1", icon: "troubleshoot" },
    { label: "Mosca Simulator", path: "/mosca", icon: "timeline" },
    { label: "Risk Analysis", path: "/risk", icon: "analytics" },
    { label: "Migration Guidance", path: "/migration", icon: "swap_calls" },
    { label: "CycloneDX 1.6 CBOM", path: "/cbom", icon: "verified_user" },
    { label: "Reports & Evidence", path: "/reports", icon: "description" },
    { label: "Terminal / Log", path: "/terminal", icon: "terminal" },
  ];

  return (
    <aside className="w-64 h-[calc(100vh-2.5rem)] flex flex-col justify-between p-2 border-r border-outline-variant bg-surface-container-lowest shrink-0 select-none">
      <div className="flex flex-col gap-2">
        {/* Node Identity Header */}
        <div className="px-3 py-2 border-b border-outline-variant">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <span className="material-symbols-outlined text-primary text-base">memory</span>
              <span className="text-primary font-mono text-xs font-bold uppercase tracking-tight">ECDAT Engine</span>
            </div>
            <span className="px-1 py-0.2 bg-tertiary/10 text-tertiary border border-tertiary/30 font-mono text-[9px] rounded">
              ONLINE
            </span>
          </div>
          <p className="text-outline font-mono text-[10px] mt-0.5">SIH 2026 // NTRO SEC (PS 26164)</p>
        </div>

        {/* Primary AST Action */}
        <div className="px-1">
          <button
            onClick={() => navigate("/scan/new")}
            className="w-full bg-surface-container hover:bg-surface-container-high border border-outline-variant hover:border-primary text-primary font-mono text-xs font-semibold py-1.5 px-3 rounded flex items-center justify-center gap-1.5 transition-all"
          >
            <span className="material-symbols-outlined text-primary-container text-sm">rocket_launch</span>
            <span>Initiate AST Scan</span>
          </button>
        </div>

        {/* Navigation Tabs List */}
        <nav className="flex flex-col gap-0.5 mt-1 overflow-y-auto max-h-[calc(100vh-16rem)]">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive
                  ? "bg-surface-container text-primary font-mono text-xs font-semibold border-l-2 border-primary-container px-3 py-1.5 rounded-none flex items-center gap-2.5 w-full shadow-inner"
                  : "text-on-surface-variant font-mono text-xs px-3 py-1.5 rounded-none flex items-center gap-2.5 w-full hover:text-on-surface hover:bg-surface-container-low transition-colors"
              }
            >
              <span className="material-symbols-outlined text-sm">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* SideNav Footer */}
      <div className="flex flex-col gap-1 border-t border-outline-variant pt-2">
        <div className="text-tertiary font-mono text-[11px] px-3 py-1 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm text-tertiary">check_circle</span>
            <span>System Health: Optimal</span>
          </div>
          <span className="text-[10px] text-outline">v2.4</span>
        </div>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            isActive
              ? "bg-surface-container text-primary font-mono text-xs font-semibold border-l-2 border-primary-container px-3 py-1 flex items-center gap-2 rounded-none"
              : "text-on-surface-variant font-mono text-xs px-3 py-1 flex items-center gap-2 hover:text-on-surface hover:bg-surface-container-low rounded transition-colors"
          }
        >
          <span className="material-symbols-outlined text-sm">settings</span>
          <span>Settings</span>
        </NavLink>

        <div className="px-3 py-1 bg-surface-container-high/40 rounded flex items-center justify-between text-[10px] font-mono text-outline mt-0.5">
          <span>AIR-GAP ID: NTRO-8841</span>
          <span className="text-primary font-bold">SEC-3</span>
        </div>
      </div>
    </aside>
  );
};

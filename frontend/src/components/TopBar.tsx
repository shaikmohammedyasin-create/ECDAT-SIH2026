import React from "react";
import { Link, useNavigate } from "react-router-dom";

interface TopBarProps {
  targetPath?: string;
  status?: string;
  cbomValid?: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  targetPath = "src/crypto-core",
  status = "Idle",
  cbomValid = true,
}) => {
  const navigate = useNavigate();
  const folderName = targetPath ? targetPath.split(/[\\/]/).filter(Boolean).pop() || "src/crypto-core" : "src/crypto-core";

  return (
    <header className="flex justify-between items-center h-10 px-4 w-full border-b border-outline-variant bg-surface-container-lowest shrink-0 select-none z-50">
      {/* Brand / ID & Working Branch */}
      <div className="flex items-center gap-3">
        <Link to="/scan/new" className="flex items-center gap-1.5 text-primary font-mono text-xs font-bold tracking-tight hover:opacity-90">
          <span className="material-symbols-outlined text-primary-container text-sm">shield</span>
          <span>ECDAT // PS-ID: 26164 (NTRO)</span>
        </Link>
        <div className="h-4 w-px bg-outline-variant"></div>
        <nav className="hidden md:flex items-center h-10 text-xs font-mono">
          <span className="text-primary border-b-2 border-primary px-2 h-full flex items-center gap-1">
            <span className="material-symbols-outlined text-xs">terminal</span>
            <span>target:{folderName}</span>
          </span>
          <span className="text-on-surface-variant px-2 h-full flex items-center gap-1.5">
            <span className={`inline-block w-1.5 h-1.5 rounded-full ${cbomValid ? "bg-tertiary" : "bg-error"}`}></span>
            <span className={cbomValid ? "text-tertiary" : "text-error"}>
              CycloneDX v1.6 [{cbomValid ? "VALID" : "INVALID"}]
            </span>
          </span>
        </nav>
      </div>

      {/* Right Actions / Controls */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1 text-xs font-mono text-on-surface-variant px-2 py-0.5 bg-surface-container rounded border border-outline-variant">
          <span className={`inline-block w-1.5 h-1.5 rounded-full ${status === "Running" ? "bg-primary animate-pulse" : "bg-tertiary"}`}></span>
          <span>Status: {status}</span>
        </div>

        <button
          onClick={() => navigate("/scan/new")}
          className="bg-primary-container text-on-primary font-mono text-xs font-semibold px-2.5 h-6 rounded flex items-center gap-1 hover:bg-primary transition-colors"
        >
          <span className="material-symbols-outlined text-xs">play_arrow</span>
          <span>Run Discovery</span>
        </button>

        <div className="h-4 w-px bg-outline-variant mx-1"></div>

        <div className="flex items-center text-on-surface-variant gap-0.5">
          <Link
            to="/terminal"
            className="w-6 h-6 flex items-center justify-center hover:bg-surface-container-high hover:text-on-surface rounded transition-colors"
            title="Terminal CLI"
          >
            <span className="material-symbols-outlined text-sm">terminal</span>
          </Link>
          <Link
            to="/settings"
            className="w-6 h-6 flex items-center justify-center hover:bg-surface-container-high hover:text-on-surface rounded transition-colors"
            title="Settings"
          >
            <span className="material-symbols-outlined text-sm">tune</span>
          </Link>
        </div>

        <div className="h-4 w-px bg-outline-variant mx-1"></div>

        {/* SecOps Token Avatar */}
        <div className="flex items-center gap-1 text-xs font-mono text-on-surface-variant" title="Lead Cryptographer SecOps Token">
          <div className="w-5 h-5 rounded bg-surface-container-highest border border-outline-variant flex items-center justify-center text-primary font-bold text-[10px]">
            NT
          </div>
          <span className="hidden lg:inline text-[11px] text-outline">secops-analyst-01</span>
        </div>
      </div>
    </header>
  );
};

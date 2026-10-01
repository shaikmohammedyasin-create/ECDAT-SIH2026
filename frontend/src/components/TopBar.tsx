import React from "react";
import { Link, useNavigate } from "react-router-dom";

interface TopBarProps {
  targetPath?: string;
  status?: string;
  cbomValid?: boolean;
  onToggleMobileNav?: () => void;
  isMobileNavOpen?: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  targetPath = "src/crypto-core",
  status = "Idle",
  cbomValid = true,
  onToggleMobileNav,
  isMobileNavOpen = false,
}) => {
  const navigate = useNavigate();
  const folderName = targetPath ? targetPath.split(/[\\/]/).filter(Boolean).pop() || "src/crypto-core" : "src/crypto-core";

  return (
    <header className="flex justify-between items-center h-10 px-2 sm:px-4 w-full border-b border-outline-variant bg-surface-container-lowest shrink-0 select-none z-40">
      {/* Brand / ID & Working Branch */}
      <div className="flex items-center gap-1.5 sm:gap-3">
        {/* Mobile Hamburger Menu Toggle */}
        <button
          type="button"
          onClick={onToggleMobileNav}
          className="md:hidden w-8 h-8 flex items-center justify-center rounded text-on-surface-variant hover:text-primary hover:bg-surface-container transition-colors"
          aria-label="Toggle Navigation Menu"
        >
          <span className="material-symbols-outlined text-lg">
            {isMobileNavOpen ? "close" : "menu"}
          </span>
        </button>

        <Link to="/scan/new" className="flex items-center gap-1.5 text-primary font-mono text-xs font-bold tracking-tight hover:opacity-90">
          <span className="material-symbols-outlined text-primary-container text-sm">shield</span>
          <span className="hidden sm:inline">ECDAT // PS-ID: 26164 (NTRO)</span>
          <span className="sm:hidden">ECDAT</span>
        </Link>
        <div className="hidden sm:block h-4 w-px bg-outline-variant"></div>
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
      <div className="flex items-center gap-1 sm:gap-2">
        <div className="flex items-center gap-1 text-[11px] sm:text-xs font-mono text-on-surface-variant px-1.5 sm:px-2 py-0.5 bg-surface-container rounded border border-outline-variant">
          <span className={`inline-block w-1.5 h-1.5 rounded-full ${status === "Running" ? "bg-primary animate-pulse" : "bg-tertiary"}`}></span>
          <span className="hidden sm:inline">Status: </span>
          <span>{status}</span>
        </div>

        <button
          onClick={() => navigate("/scan/new")}
          className="bg-primary-container text-on-primary font-mono text-xs font-semibold px-2 sm:px-2.5 h-6 rounded flex items-center gap-1 hover:bg-primary transition-colors"
          title="Run AST Cryptographic Discovery Scan"
        >
          <span className="material-symbols-outlined text-xs">play_arrow</span>
          <span className="hidden sm:inline">Run Discovery</span>
          <span className="sm:hidden text-[10px]">Scan</span>
        </button>

        <div className="h-4 w-px bg-outline-variant mx-0.5 sm:mx-1"></div>

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

        <div className="hidden xs:block h-4 w-px bg-outline-variant mx-1"></div>

        {/* SecOps Token Avatar */}
        <div className="hidden xs:flex items-center gap-1 text-xs font-mono text-on-surface-variant" title="Lead Cryptographer SecOps Token">
          <div className="w-5 h-5 rounded bg-surface-container-highest border border-outline-variant flex items-center justify-center text-primary font-bold text-[10px]">
            NT
          </div>
          <span className="hidden lg:inline text-[11px] text-outline">secops-analyst-01</span>
        </div>
      </div>
    </header>
  );
};

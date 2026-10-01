import React, { useEffect, useState, useRef } from "react";
import { fetchTerminalLogs, clearTerminalLogs, fetchScanStatus } from "../../services/api";
import type { TerminalLog } from "../../types";

export const TerminalPage: React.FC = () => {
  const [logs, setLogs] = useState<TerminalLog[]>([]);
  const [scanId, setScanId] = useState<string>("live-scan");
  const [loading, setLoading] = useState(true);
  const [selectedLevel, setSelectedLevel] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);
  const consoleBottomRef = useRef<HTMLDivElement>(null);

  const loadLogs = () => {
    fetchTerminalLogs()
      .then((data) => {
        setLogs(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load terminal logs:", err);
        setLoading(false);
      });

    fetchScanStatus()
      .then((status) => {
        if (status.scan_id) setScanId(status.scan_id);
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (autoScroll && consoleBottomRef.current) {
      consoleBottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, autoScroll]);

  const handleClear = async () => {
    await clearTerminalLogs();
    setLogs([]);
  };

  const copyBuffer = () => {
    const text = logs
      .map((l, idx) => `[${idx + 1}] [${l.timestamp}] [${l.level}] ${l.message}`)
      .join("\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const exportRawLog = () => {
    const text = logs
      .map((l, idx) => `[${idx + 1}] [${l.timestamp}] [${l.level}] ${l.message}`)
      .join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ecdat-scan-log-${Date.now()}.log`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredLogs = logs.filter((log) => {
    if (selectedLevel !== "ALL" && log.level !== selectedLevel) return false;
    if (searchQuery.trim() && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  const countByLevel = (level: string) => {
    if (level === "ALL") return logs.length;
    return logs.filter((l) => l.level === level).length;
  };

  return (
    <div className="flex-1 flex flex-col bg-surface overflow-hidden">
      {/* Top Context Section */}
      <section className="px-3 sm:px-4 py-2 border-b border-outline-variant bg-surface-container-low shrink-0 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-base sm:text-lg font-headline-md text-on-surface tracking-tight font-bold">
              Terminal / Scan Log
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-container-highest border border-outline-variant text-primary font-bold">
              STREAM: LIVE
            </span>
          </div>
          <p className="text-body-sm text-outline mt-0.5 text-xs">
            Real-time daemon telemetry, AST traversal traces, cryptographic normalization logs, and schema verification diagnostics.
          </p>
        </div>

        {/* Global Diagnostic Metrics Badge */}
        <div className="flex items-center gap-2 text-code-sm">
          <div className="px-2.5 py-1 bg-surface-container-lowest border border-outline-variant rounded flex items-center gap-2 text-on-surface-variant text-xs">
            <span className="text-outline">EXEC ID:</span>
            <span className="text-primary font-mono font-semibold" title={scanId}>
              {scanId.length > 18 ? scanId.substring(0, 15) + "..." : scanId}
            </span>
          </div>
          <div className="px-2.5 py-1 bg-surface-container-lowest border border-outline-variant rounded flex items-center gap-2 text-on-surface-variant text-xs">
            <span className="text-outline">PARSER:</span>
            <span className="text-tertiary font-mono">STRICT-FIPS-203</span>
          </div>
        </div>
      </section>

      {/* Control Toolbar */}
      <section className="px-4 py-2 border-b border-outline-variant bg-surface-container flex flex-wrap items-center justify-between gap-3 shrink-0">
        {/* Left Controls: Active Scan ID & Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-surface-container-lowest border border-outline-variant text-code-sm text-on-surface text-xs">
            <span className="material-symbols-outlined text-primary text-[14px]">fingerprint</span>
            <span className="text-outline">Scan ID:</span>
            <span className="font-mono text-primary font-medium" title={scanId}>{scanId}</span>
          </div>

          <div className="h-4 w-px bg-outline-variant hidden sm:block"></div>

          {/* Log Level Filters */}
          <div className="flex items-center gap-1 text-xs">
            {(["ALL", "INFO", "SUCCESS", "WARNING", "CRITICAL"] as const).map((lvl) => {
              const count = countByLevel(lvl);
              const isActive = selectedLevel === lvl;
              return (
                <button
                  key={lvl}
                  onClick={() => setSelectedLevel(lvl)}
                  className={`px-2 py-1 rounded font-mono transition-colors ${
                    isActive
                      ? "bg-surface-container-highest border border-primary text-primary font-bold"
                      : "bg-surface-container-lowest border border-outline-variant hover:bg-surface-container-high text-on-surface-variant"
                  }`}
                >
                  {lvl} <span className="text-outline ml-0.5">({count})</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Controls: Search, Auto-scroll, Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search log stream input */}
          <div className="relative flex items-center">
            <span className="absolute left-2 text-outline material-symbols-outlined text-[14px]">filter_list</span>
            <input
              className="h-7 w-48 bg-surface-container-lowest border border-outline-variant rounded pl-7 pr-3 text-xs text-on-surface placeholder:text-outline focus:outline-none focus:border-primary"
              placeholder="Filter regex / string..."
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Auto-scroll Switch */}
          <label className="flex items-center gap-1.5 px-2 py-1 rounded bg-surface-container-lowest border border-outline-variant cursor-pointer text-xs">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-outline-variant bg-surface-container text-primary focus:ring-0 h-3.5 w-3.5"
            />
            <span className="text-on-surface">Auto-scroll</span>
          </label>

          {/* Action Buttons */}
          <div className="flex items-center gap-1 text-xs">
            <button
              onClick={copyBuffer}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-surface-container-lowest hover:bg-surface-container-high border border-outline-variant text-on-surface transition-colors"
              title="Copy complete terminal buffer"
            >
              <span className="material-symbols-outlined text-[14px]">
                {copied ? "check" : "content_copy"}
              </span>
              <span>{copied ? "Copied" : "Copy Buffer"}</span>
            </button>
            <button
              onClick={exportRawLog}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-surface-container-lowest hover:bg-surface-container-high border border-outline-variant text-on-surface transition-colors"
              title="Export raw logs"
            >
              <span className="material-symbols-outlined text-[14px]">download</span>
              <span>Export Raw Log</span>
            </button>
            <button
              onClick={handleClear}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-surface-container-lowest hover:bg-surface-container-high border border-outline-variant text-error hover:text-error transition-colors"
              title="Clear displayed log buffer"
            >
              <span className="material-symbols-outlined text-[14px]">delete_sweep</span>
              <span>Clear</span>
            </button>
          </div>
        </div>
      </section>

      {/* Terminal Log Viewer Container */}
      <section className="flex-1 bg-surface-container-lowest p-2 overflow-hidden flex flex-col">
        {/* Terminal Window Frame */}
        <div className="flex-1 rounded border border-outline-variant bg-[#090f15] flex flex-col overflow-hidden shadow-2xl relative">
          {/* Terminal Tab/Header Bar */}
          <div className="h-7 px-3 bg-[#111720] border-b border-outline-variant flex items-center justify-between text-xs shrink-0 select-none">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 mr-2">
                <span className="h-2.5 w-2.5 rounded-full bg-red-500/80"></span>
                <span className="h-2.5 w-2.5 rounded-full bg-amber-500/80"></span>
                <span className="h-2.5 w-2.5 rounded-full bg-green-500/80"></span>
              </div>
              <div className="flex items-center gap-1 px-2 py-0.5 rounded bg-surface-container-lowest border border-outline-variant text-primary font-mono text-[11px]">
                <span className="material-symbols-outlined text-[12px]">terminal</span>
                <span>daemon:worker-01 (STDOUT/STDERR)</span>
              </div>
              <span className="text-outline font-mono text-[10px] tracking-widest">// AST_PIPELINE_ACTIVE</span>
            </div>
            <div className="flex items-center gap-3 text-outline font-mono text-[11px]">
              <span>UTF-8</span>
              <span>LF</span>
              <span className="text-tertiary">STREAM_SYNCHRONIZED</span>
            </div>
          </div>

          {/* Console Stream Viewport */}
          <div className="flex-1 p-3 overflow-y-auto font-mono text-xs space-y-1 leading-relaxed selection:bg-primary selection:text-background">
            {loading ? (
              <div className="text-outline py-4 text-center">Connecting to ECDAT daemon telemetry socket...</div>
            ) : filteredLogs.length === 0 ? (
              <div className="text-outline py-4 text-center">No terminal logs matching current filters.</div>
            ) : (
              filteredLogs.map((log, idx) => {
                const isCrit = log.level === "CRITICAL";
                const isWarn = log.level === "WARNING";
                const isSuccess = log.level === "SUCCESS";

                return (
                  <div
                    key={idx}
                    className={`flex items-start gap-2 hover:bg-surface-container-low/40 px-1 py-0.5 rounded group transition-colors ${
                      isCrit ? "bg-error/10" : isWarn ? "bg-amber-500/5" : isSuccess ? "bg-tertiary/5" : ""
                    }`}
                  >
                    <span className="text-outline select-none w-8 text-right shrink-0 opacity-60">
                      {String(idx + 1).padStart(3, "0")}
                    </span>
                    <span className="text-outline shrink-0 text-[11px]">[{log.timestamp}]</span>
                    <span
                      className={`px-1.5 py-0.2 rounded text-[10px] font-bold shrink-0 ${
                        isCrit
                          ? "bg-error-container text-on-error-container"
                          : isWarn
                          ? "bg-primary-container/20 text-primary border border-primary/30"
                          : isSuccess
                          ? "bg-tertiary/15 text-tertiary border border-tertiary/30"
                          : "bg-surface-container-high text-secondary"
                      }`}
                    >
                      {log.level}
                    </span>
                    <span className="text-on-surface break-all">{log.message}</span>
                  </div>
                );
              })
            )}
            <div ref={consoleBottomRef} />
          </div>
        </div>
      </section>
    </div>
  );
};
export default TerminalPage;

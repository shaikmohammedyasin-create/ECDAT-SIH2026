import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { fetchFindingDetail } from "../../services/api";
import type { FindingDetail } from "../../types";

export const FindingInspector: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const findingId = id !== undefined && /^\d+$/.test(id) ? parseInt(id, 10) : 0;

  const [finding, setFinding] = useState<FindingDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [mobileTab, setMobileTab] = useState<"meta" | "code">("meta");

  useEffect(() => {
    let isCurrent = true;
    const controller = new AbortController();

    // oxlint-disable-next-line react/set-state-in-effect
    setLoading(true);
    fetchFindingDetail(findingId, controller.signal)
      .then((data) => {
        if (isCurrent) {
          setFinding(data);
          setError(null);
          setLoading(false);
        }
      })
      .catch((err: any) => {
        if (err?.name === "AbortError") return;
        if (isCurrent) {
          setError(err?.message || "Failed to load finding details");
          setLoading(false);
        }
      });

    return () => {
      isCurrent = false;
      controller.abort();
    };
  }, [findingId]);

  const copyCode = () => {
    if (finding?.source_snippet) {
      navigator.clipboard.writeText(finding.source_snippet);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const exportFindingJson = () => {
    if (!finding) return;
    const blob = new Blob([JSON.stringify(finding, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `finding-${finding.rule_id || finding.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="font-code-sm text-on-surface-variant text-sm">Inspecting cryptographic AST node...</span>
        </div>
      </div>
    );
  }

  if (error || !finding) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="bg-surface-container border border-error/50 p-6 rounded max-w-md text-center flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-error text-3xl">error</span>
          <h2 className="text-headline-md font-bold text-on-surface">Finding Not Found</h2>
          <p className="text-body-sm text-on-surface-variant">{error || "No cryptographic finding exists with this index."}</p>
          <div className="flex gap-2 mt-2">
            <Link to="/inventory" className="px-3 py-1.5 bg-surface-container-high border border-outline-variant text-primary rounded text-code-sm">
              Return to Inventory
            </Link>
            <Link to="/findings/0" className="px-3 py-1.5 bg-primary-container text-on-primary-container font-semibold rounded text-code-sm">
              Load Finding #0
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Parse code snippet lines for IDE view
  const snippetLines = (finding.source_snippet || "").split("\n");
  const targetLine = finding.line_number || 1;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-surface overflow-hidden">
      {/* Top Finding Header & Action Toolbar */}
      <div className="border-b border-outline-variant bg-surface-container-low px-3 sm:px-4 py-2 flex flex-col lg:flex-row lg:items-center justify-between gap-3 shrink-0">
        {/* Left Breadcrumb & Severity Pill Stack */}
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <div className="flex items-center gap-2 font-code-md text-sm">
            <Link to="/inventory" className="text-on-surface-variant hover:text-on-surface">Finding Inspector</Link>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold font-mono">{finding.rule_id}</span>
          </div>
          {/* Status Badges */}
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={`px-2 py-0.5 rounded text-[11px] font-code-sm font-semibold tracking-wide flex items-center gap-1 ${
                finding.risk_band === "CRITICAL"
                  ? "bg-error-container text-on-error-container border border-error"
                  : finding.risk_band === "HIGH"
                  ? "bg-primary-container/20 text-primary border border-primary/40"
                  : "bg-surface-container-high text-secondary border border-outline-variant"
              }`}
            >
              <span className="material-symbols-outlined text-[12px]">
                {finding.risk_band === "CRITICAL" ? "dangerous" : "warning"}
              </span>
              {finding.risk_band}
            </span>
            <span className="px-2 py-0.5 bg-surface-container-highest text-primary border border-outline-variant rounded text-[11px] font-code-sm font-medium flex items-center gap-1">
              <span className="material-symbols-outlined text-[12px] text-primary">bolt</span>
              {finding.quantum_status}
            </span>
            <span className="px-2 py-0.5 bg-surface-container-high text-on-surface text-[11px] font-code-sm rounded border border-outline-variant">
              Confidence: <strong className="text-tertiary">{finding.confidence}</strong>
            </span>
          </div>
        </div>

        {/* Right Workbench Action Bar */}
        <div className="flex items-center gap-1.5 sm:gap-2 font-code-sm flex-wrap">
          <button
            onClick={() => navigate(`/mosca`)}
            className="bg-primary-container text-on-primary-container hover:bg-primary font-semibold px-3 py-1 rounded text-code-sm flex items-center gap-1 transition-colors text-xs"
          >
            <span className="material-symbols-outlined text-[14px]">timeline</span>
            <span>Run Mosca Simulation</span>
          </button>
          <button
            onClick={() => navigate(`/migration`)}
            className="bg-surface-container-high border border-outline-variant hover:border-outline text-on-surface px-2.5 py-1 rounded text-code-sm flex items-center gap-1 transition-colors text-xs"
          >
            <span className="material-symbols-outlined text-[14px]">swap_calls</span>
            <span>View Migration Plan</span>
          </button>
          <button
            onClick={exportFindingJson}
            className="bg-surface-container-high border border-outline-variant hover:border-outline text-on-surface px-2.5 py-1 rounded text-code-sm flex items-center gap-1 transition-colors text-xs"
            title="Download Finding JSON"
          >
            <span className="material-symbols-outlined text-[14px]">file_download</span>
            <span>Export JSON</span>
          </button>
          <div className="h-4 w-px bg-outline-variant mx-1"></div>
          <button
            onClick={() => navigate(`/findings/${findingId > 0 ? findingId - 1 : 0}`)}
            disabled={findingId <= 0}
            className="bg-surface-container-high border border-outline-variant hover:border-primary disabled:opacity-40 text-on-surface px-2 py-1 rounded text-code-sm flex items-center gap-1 text-xs"
          >
            <span className="material-symbols-outlined text-[14px]">navigate_before</span>
            <span>Prev</span>
          </button>
          <button
            onClick={() => navigate(`/findings/${findingId + 1}`)}
            className="bg-surface-container-high border border-outline-variant hover:border-primary text-primary px-2 py-1 rounded text-code-sm flex items-center gap-1 text-xs"
          >
            <span>Next</span>
            <span className="material-symbols-outlined text-[14px]">navigate_next</span>
          </button>
        </div>
      </div>

      {/* Mobile Tab Switcher */}
      <div className="lg:hidden flex border-b border-outline-variant bg-surface-container-low shrink-0 text-xs font-mono">
        <button
          type="button"
          onClick={() => setMobileTab("meta")}
          className={`flex-1 py-2 text-center border-b-2 font-semibold flex items-center justify-center gap-1.5 transition-colors ${
            mobileTab === "meta"
              ? "border-primary text-primary bg-surface-container"
              : "border-transparent text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <span className="material-symbols-outlined text-sm">badge</span>
          <span>Asset & Risk Vector</span>
        </button>
        <button
          type="button"
          onClick={() => setMobileTab("code")}
          className={`flex-1 py-2 text-center border-b-2 font-semibold flex items-center justify-center gap-1.5 transition-colors ${
            mobileTab === "code"
              ? "border-primary text-primary bg-surface-container"
              : "border-transparent text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <span className="material-symbols-outlined text-sm">code</span>
          <span>Source & Evidence</span>
        </button>
      </div>

      {/* Two-Column Workbench Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* ================= LEFT COLUMN: METADATA & CRYPTOGRAPHIC BREAKDOWN ================= */}
        <div
          className={`
            w-full lg:w-[42%] border-r border-outline-variant overflow-y-auto p-3 flex-col gap-3 bg-surface-container-lowest
            ${mobileTab === "meta" ? "flex" : "hidden lg:flex"}
          `}
        >
          {/* Asset Identity Card */}
          <div className="bg-surface-container border border-outline-variant rounded p-3 flex flex-col gap-2">
            <div className="flex items-center justify-between border-b border-outline-variant pb-1.5">
              <span className="font-code-md text-code-sm font-semibold text-primary uppercase flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[15px]">badge</span>
                Asset Identity & Parameters
              </span>
              <span className="font-code-sm text-[10px] text-on-surface-variant uppercase tracking-wider font-mono">
                ID #{finding.id}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-2 text-code-sm font-code-sm pt-1">
              <div>
                <span className="text-on-surface-variant block text-[10px] uppercase">Detected Algorithm</span>
                <span className="font-semibold text-primary font-code-lg font-mono">{finding.algorithm}</span>
              </div>
              <div>
                <span className="text-on-surface-variant block text-[10px] uppercase">Rule Identifier</span>
                <span className="text-on-surface font-mono">{finding.rule_id}</span>
              </div>
              <div className="col-span-2">
                <span className="text-on-surface-variant block text-[10px] uppercase">Primitive Type / Usage</span>
                <span className="text-on-surface font-mono">{finding.primitive} — {finding.usage || finding.asset_type}</span>
              </div>
              <div className="col-span-2">
                <span className="text-on-surface-variant block text-[10px] uppercase">Code Location</span>
                <span className="text-secondary font-mono flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">link</span>
                  {finding.file_path}:{finding.line_number}
                </span>
              </div>
            </div>

            {/* Parameter Synthesis Matrix */}
            <div className="mt-2 pt-2 border-t border-outline-variant">
              <span className="text-on-surface-variant block text-[10px] uppercase font-code-sm mb-1.5 font-semibold">
                Parameter Synthesis
              </span>
              <div className="grid grid-cols-2 gap-1.5 text-code-sm font-code-sm bg-surface-container-lowest p-2 rounded border border-outline-variant">
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">Key Size:</span>
                  <span className={`font-semibold font-mono ${finding.key_size === "unknown" ? "text-outline" : "text-primary"}`}>
                    {finding.key_size}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">Mode:</span>
                  <span className="text-on-surface font-mono">{finding.mode}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">Padding:</span>
                  <span className="text-on-surface font-mono">{finding.padding}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">Asset Type:</span>
                  <span className="text-on-surface font-mono">{finding.asset_type}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quantum Threat Classification Card */}
          <div className="bg-surface-container border border-outline-variant rounded p-3 flex flex-col gap-2">
            <div className="flex items-center justify-between border-b border-outline-variant pb-1.5">
              <span className="font-code-md text-code-sm font-semibold text-primary uppercase flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[15px]">blur_on</span>
                Quantum Threat Classification
              </span>
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-code-sm font-bold ${
                  finding.quantum_status === "Vulnerable" || finding.quantum_vuln_class === "SHOR_BROKEN"
                    ? "bg-error-container text-on-error-container"
                    : finding.quantum_status === "Weakened" || finding.quantum_vuln_class === "GROVER_WEAKENED"
                    ? "bg-amber-900/60 text-amber-200 border border-amber-600"
                    : finding.quantum_status === "Legacy-broken" || finding.quantum_vuln_class === "CLASSICALLY_BROKEN"
                    ? "bg-fuchsia-950/60 text-fuchsia-200 border border-fuchsia-600"
                    : "bg-surface-container-highest text-primary"
                }`}
              >
                {finding.quantum_status}
              </span>
            </div>
            <div className="flex flex-col gap-2 pt-1 font-code-sm text-code-sm">
              <div className="p-2 bg-surface-container-lowest rounded border border-outline-variant flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-on-surface-variant">Classification Signature:</span>
                  <span className="text-error font-bold font-mono">{finding.quantum_status}</span>
                </div>
                <p className="text-on-surface-variant text-[11px] leading-relaxed">
                  {finding.why_risky ||
                    "Vulnerable to polynomial-time period finding algorithms executing on a Cryptographically Relevant Quantum Computer (CRQC)."}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant">
                  <span className="text-on-surface-variant block text-[10px] uppercase font-bold">Shor Algorithm Impact</span>
                  <span className={`font-semibold text-[12px] block mt-0.5 ${
                    finding.quantum_status === "Vulnerable" || finding.quantum_vuln_class === "SHOR_BROKEN" ? "text-error" : "text-tertiary"
                  }`}>
                    {finding.quantum_status === "Vulnerable" || finding.quantum_vuln_class === "SHOR_BROKEN" ? "High Severity" : "Resistant"}
                  </span>
                  <span className="text-on-surface-variant text-[10px]">
                    {finding.quantum_status === "Vulnerable" || finding.quantum_vuln_class === "SHOR_BROKEN"
                      ? "Discrete log/factoring reduced to polynomial time."
                      : "No Shor period-finding weakness."}
                  </span>
                </div>
                <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant">
                  <span className="text-on-surface-variant block text-[10px] uppercase font-bold">Grover Algorithm Impact</span>
                  <span className={`font-semibold text-[12px] block mt-0.5 ${
                    finding.quantum_status === "Weakened" || finding.quantum_vuln_class === "GROVER_WEAKENED" ? "text-primary" : "text-on-surface-variant"
                  }`}>
                    {finding.quantum_status === "Weakened" || finding.quantum_vuln_class === "GROVER_WEAKENED" ? "Weakened (√N)" : "Minimal"}
                  </span>
                  <span className="text-on-surface-variant text-[10px]">
                    Effective key length halved under quadratic search.
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* HNDL / Mosca Theorem Engine */}
          <div className="bg-surface-container border border-outline-variant rounded p-3 flex flex-col gap-2">
            <div className="flex items-center justify-between border-b border-outline-variant pb-1.5">
              <span className="font-code-md text-code-sm font-semibold text-primary uppercase flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[15px]">timelapse</span>
                HNDL / Mosca Theorem Engine
              </span>
              <span
                className={`text-[10px] font-code-sm font-bold uppercase ${
                  finding.mosca_at_risk ? "text-error" : "text-tertiary"
                }`}
              >
                {finding.mosca_at_risk ? "Theorem Violated" : "Within Window"}
              </span>
            </div>
            {/* Mosca Parameter Metrics */}
            <div className="grid grid-cols-3 gap-2 text-center py-1">
              <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                <div className="text-on-surface-variant font-code-sm text-[10px]">Shelf-life (X)</div>
                <div className="font-code-lg text-[14px] font-bold text-on-surface mt-0.5">{finding.x_lifetime} Yrs</div>
                <div className="text-[9px] text-on-surface-variant truncate">Data Lifetime</div>
              </div>
              <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                <div className="text-on-surface-variant font-code-sm text-[10px]">Migration (Y)</div>
                <div className="font-code-lg text-[14px] font-bold text-on-surface mt-0.5">{finding.y_migration} Yrs</div>
                <div className="text-[9px] text-on-surface-variant">Transition Time</div>
              </div>
              <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                <div className="text-on-surface-variant font-code-sm text-[10px]">CRQC Horizon (Z)</div>
                <div className="font-code-lg text-[14px] font-bold text-primary mt-0.5">{finding.scenario_year}</div>
                <div className="text-[9px] text-on-surface-variant">Planning Scenario</div>
              </div>
            </div>
            {/* Constraint Condition Alert */}
            <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant font-code-sm text-code-sm flex flex-col gap-1.5">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-on-surface-variant">Mosca Constraint Condition:</span>
                <span className={`font-mono font-bold ${finding.mosca_at_risk ? "text-error" : "text-tertiary"}`}>
                  X + Y = {finding.x_lifetime + finding.y_migration} {finding.mosca_at_risk ? ">" : "≤"} {finding.scenario_year - 2026} (Z - 2026)
                </span>
              </div>
              <div
                className={`p-1.5 rounded text-[11px] font-semibold flex items-start gap-1.5 ${
                  finding.mosca_at_risk
                    ? "bg-error-container text-on-error-container"
                    : "bg-tertiary/10 text-tertiary border border-tertiary/30"
                }`}
              >
                <span className="material-symbols-outlined text-[15px] shrink-0">
                  {finding.mosca_at_risk ? "warning" : "check_circle"}
                </span>
                <span>
                  {finding.mosca_at_risk
                    ? "STATUS: HARVEST NOW, DECRYPT LATER (HNDL) CRITICAL RISK"
                    : "STATUS: WITHIN TIMELINE MARGIN - NO IMMEDIATE HNDL BREACH"}
                </span>
              </div>
            </div>
          </div>

          {/* Quantitative Risk Score Card */}
          <div className="bg-surface-container border border-outline-variant rounded p-3 flex flex-col gap-2">
            <div className="flex items-center justify-between border-b border-outline-variant pb-1.5">
              <span className="font-code-md text-code-sm font-semibold text-primary uppercase flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[15px]">analytics</span>
                Quantitative Risk Score
              </span>
              <span
                className={`font-code-sm text-xs font-bold ${
                  finding.risk_band?.toUpperCase() === "CRITICAL" ? "text-error" : "text-primary"
                }`}
              >
                {finding.risk_band} Band
              </span>
            </div>
            <div className="flex items-center gap-3 pt-1">
              <div
                className={`bg-surface-container-lowest border p-3 rounded flex flex-col items-center justify-center shrink-0 w-20 ${
                  finding.risk_band?.toUpperCase() === "CRITICAL" ? "border-error text-error" : "border-primary text-primary"
                }`}
              >
                <span className="text-2xl font-code-lg font-extrabold leading-none">{Math.round(finding.risk_score)}</span>
                <span className="text-[10px] font-code-sm text-on-surface-variant mt-1">/ 100</span>
              </div>
              <div className="flex-1 text-code-sm font-code-sm flex flex-col gap-1.5">
                <div className="flex justify-between text-[11px]">
                  <span className="text-on-surface-variant">Exposure Surface:</span>
                  <span className="font-mono text-on-surface">{finding.exposure || "Internal Library"}</span>
                </div>
                <div className="w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${finding.risk_band?.toUpperCase() === "CRITICAL" ? "bg-error" : "bg-primary"}`}
                    style={{ width: `${Math.min(100, Math.max(10, finding.risk_score))}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-[10px] text-outline">
                  <span>Classical Hygiene: {finding.hygiene_critical ? "FLAGGED" : "NOMINAL"}</span>
                  <span>Agility: {(finding.asset_type === "Certificate" ? 0.4 : (finding.asset_type === "Algorithm" || finding.asset_type === "Protocol" ? 0.3 : 0.8)).toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ================= RIGHT COLUMN: CODE EVIDENCE & AST CONTEXT ================= */}
        <div
          className={`
            w-full lg:w-[58%] flex-col bg-surface-container-lowest overflow-hidden
            ${mobileTab === "code" ? "flex" : "hidden lg:flex"}
          `}
        >
          {/* IDE Header with File Tabs & AST Status */}
          <div className="h-9 bg-surface-container-low border-b border-outline-variant flex items-center justify-between px-3 shrink-0 select-none">
            <div className="flex items-center h-full">
              <div className="bg-surface-container-lowest border-r border-t-2 border-t-primary border-outline-variant px-3 h-full flex items-center gap-2 text-code-sm font-code-md text-on-surface">
                <span className="material-symbols-outlined text-[14px] text-primary">description</span>
                <span>{finding.file_name}</span>
              </div>
            </div>
            <div className="flex items-center gap-3 font-code-sm text-code-sm text-on-surface-variant">
              <span>{finding.file_path}</span>
              <span className="text-outline">|</span>
              <span className="text-primary font-semibold">Line {finding.line_number}</span>
              <span className="text-outline">|</span>
              <span className="bg-surface-container-high px-1.5 py-0.5 rounded text-[10px] border border-outline-variant text-on-surface">
                AST Node Evaluator
              </span>
              <button
                onClick={copyCode}
                className="hover:text-on-surface flex items-center gap-1 text-on-surface-variant"
                title="Copy code snippet"
              >
                <span className="material-symbols-outlined text-[14px]">
                  {copied ? "check" : "content_copy"}
                </span>
                {copied && <span className="text-[10px] text-tertiary">Copied</span>}
              </button>
            </div>
          </div>

          {/* Code Editor View with Syntax Highlighting & Line Highlight */}
          <div className="flex-1 overflow-auto bg-[#090f15] p-3 font-code-lg text-code-sm select-text flex flex-col font-mono text-[12px] leading-5">
            {snippetLines.map((line, idx) => {
              const isVuln = idx === 0 || line.includes("generate") || line.includes("Cipher") || line.includes("AES") || line.includes("RSA");
              const lineNum = targetLine + idx;
              return (
                <div key={idx} className="flex flex-col">
                  <div
                    className={`flex items-center hover:bg-surface-container-low/50 py-0.5 ${
                      isVuln ? "bg-error-container/20 border-l-4 border-error" : ""
                    }`}
                  >
                    <span
                      className={`w-10 text-right pr-3 select-none shrink-0 ${
                        isVuln ? "text-error font-bold flex items-center justify-end gap-1" : "text-outline/50"
                      }`}
                    >
                      {isVuln && <span className="material-symbols-outlined text-[11px] text-error">priority_high</span>}
                      {lineNum}
                    </span>
                    <span className="text-on-surface whitespace-pre overflow-x-auto">{line}</span>
                  </div>

                  {/* Vulnerability Callout Card directly under vulnerable line */}
                  {isVuln && idx === 0 && (
                    <div className="ml-10 my-2 p-2 bg-surface-container border border-error rounded flex items-start gap-2 text-code-sm shadow-md">
                      <span className="material-symbols-outlined text-error text-[16px] shrink-0 mt-0.5">report_problem</span>
                      <div className="flex flex-col gap-0.5">
                        <div className="text-primary font-bold font-mono text-[11px]">
                          [{finding.rule_id}] {finding.algorithm} finding in source AST
                        </div>
                        <div className="text-on-surface-variant text-[11px] leading-relaxed">
                          {finding.why_risky || "Shor polynomial factorization reduces discrete log/factoring to O((log N)³). Lattice-based replacement mandatory."}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* AST Node Inspector & Lower Pane */}
          <div className="h-36 border-t border-outline-variant bg-surface-container flex flex-col shrink-0">
            <div className="bg-surface-container-high px-3 py-1 border-b border-outline-variant flex items-center justify-between text-code-sm font-code-sm">
              <span className="text-on-surface font-semibold flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[14px] text-primary">account_tree</span>
                Abstract Syntax Tree (AST) Evidence Inspector
              </span>
              <span className="text-[10px] text-on-surface-variant uppercase font-mono">Parser Mode: AST Visitor</span>
            </div>
            <div className="p-2 overflow-y-auto flex-1 font-code-sm text-code-sm flex flex-col gap-1.5">
              <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant font-mono text-[11px] leading-relaxed">
                <div className="text-secondary font-bold">Node: Cryptographic Invocation ({finding.rule_id})</div>
                <div className="text-on-surface-variant pl-3">
                  ↳ Target: <span className="text-primary">{finding.algorithm}</span> ({finding.primitive})
                </div>
                <div className="text-on-surface-variant pl-3">
                  ↳ Location: <span className="text-on-surface">{finding.file_path}:{finding.line_number}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Deterministic Migration Guidance Banner (Fixed at Bottom of Right Viewport) */}
          <div className="border-t border-outline-variant bg-surface-container-low p-3 flex flex-col gap-1.5 shrink-0">
            <div className="flex items-center justify-between">
              <span className="font-code-md text-code-sm font-bold text-primary flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[16px]">swap_horizontal_circle</span>
                Deterministic PQC Migration Guidance
              </span>
              <span className="font-code-sm text-[10px] text-tertiary border border-tertiary/40 px-1.5 py-0.5 rounded bg-surface-container">
                {finding.standard || "NIST FIPS 203/204 COMPLIANT"}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-code-sm font-code-sm">
              <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant flex items-center justify-between">
                <div>
                  <span className="text-on-surface-variant block text-[10px] uppercase">Current Primitive</span>
                  <span className="text-error font-bold font-mono">{finding.algorithm}</span>
                </div>
                <span className="material-symbols-outlined text-on-surface-variant">arrow_forward</span>
                <div>
                  <span className="text-on-surface-variant block text-[10px] uppercase">Target Primitive</span>
                  <span className="text-tertiary font-bold font-mono">
                    {finding.recommendation || (finding.hybrid_option ? `${finding.hybrid_option}` : "ML-KEM-768")}
                  </span>
                </div>
              </div>
              <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant text-[11px] flex flex-col justify-center">
                <span className="text-on-surface-variant text-[10px] font-mono">Effort: {finding.migration_effort || "Medium"}</span>
                <span className="text-on-surface line-clamp-1">{finding.recommendation}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default FindingInspector;

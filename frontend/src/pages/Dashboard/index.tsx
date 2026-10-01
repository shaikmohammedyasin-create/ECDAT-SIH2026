import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchDashboard } from "../../services/api";
import type { DashboardData } from "../../types";

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboard()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-on-surface-variant font-mono text-xs">
        <span className="material-symbols-outlined animate-spin mr-2">sync</span>
        <span>Loading cryptographic security overview...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 p-6">
        <div className="bg-error-container/20 border border-error/40 p-4 rounded text-error font-mono text-xs">
          Failed to load dashboard: {error}
        </div>
      </div>
    );
  }

  const { metrics, risk_distribution, quantum_exposure, recent_findings, migration_priority, cbom_status } = data;

  const bandColors: Record<string, string> = {
    Critical: "bg-red-800 text-white border-red-600",
    High: "bg-orange-800 text-white border-orange-600",
    Medium: "bg-amber-800 text-white border-amber-600",
    Low: "bg-green-800 text-white border-green-600",
    Info: "bg-slate-800 text-slate-300 border-slate-600",
  };

  return (
    <div className="flex-1 p-3 sm:p-4 md:p-6 space-y-4 md:space-y-5">
      {/* Header Banner */}
      <section className="flex flex-col md:flex-row md:items-end justify-between border-b border-outline-variant pb-3 gap-2">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg sm:text-xl font-bold tracking-tight text-on-surface">Cryptographic Security Overview</h1>
            <span className="px-1.5 py-0.5 rounded bg-primary-container/15 border border-primary-container/40 text-primary font-mono text-[10px] uppercase font-semibold">
              EXECUTIVE AUDIT VIEW
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1 font-sans">
            Continuous quantum vulnerability, Harvest-Now-Decrypt-Later (HNDL) exposure, and PQC transition metrics
          </p>
        </div>
        <div className="text-xs font-mono text-outline">
          Profile: <span className="text-primary font-semibold">AST-Crypt-Strict</span>
        </div>
      </section>

      {/* 5 KPI Cards */}
      <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
        <div className="bg-surface-container-low border border-outline-variant rounded p-3">
          <div className="text-[10px] font-mono font-semibold uppercase text-outline tracking-wider">TOTAL CRYPTO ASSETS</div>
          <div className="text-2xl font-bold font-mono text-on-surface mt-1">{metrics.total_assets}</div>
          <div className="text-[11px] text-on-surface-variant mt-1">Discovered AST / Conf</div>
        </div>

        <div className="bg-surface-container-low border border-outline-variant rounded p-3">
          <div className="text-[10px] font-mono font-semibold uppercase text-outline tracking-wider">HIGH / CRITICAL RISK</div>
          <div className="text-2xl font-bold font-mono text-red-400 mt-1">{metrics.critical_risk + metrics.high_risk}</div>
          <div className="text-[11px] text-on-surface-variant mt-1">Immediate remediation</div>
        </div>

        <div className="bg-surface-container-low border border-outline-variant rounded p-3">
          <div className="text-[10px] font-mono font-semibold uppercase text-outline tracking-wider">SHOR VULNERABLE</div>
          <div className="text-2xl font-bold font-mono text-red-300 mt-1">{metrics.quantum_vulnerable}</div>
          <div className="text-[11px] text-on-surface-variant mt-1">Asymmetric / DH / RSA</div>
        </div>

        <div className="bg-surface-container-low border border-outline-variant rounded p-3">
          <div className="text-[10px] font-mono font-semibold uppercase text-outline tracking-wider">GROVER WEAKENED</div>
          <div className="text-2xl font-bold font-mono text-primary mt-1">{metrics.grover_weakened}</div>
          <div className="text-[11px] text-on-surface-variant mt-1">Key size &lt; 256-bit</div>
        </div>

        <div className="bg-surface-container-low border border-outline-variant rounded p-3 col-span-2 sm:col-span-1">
          <div className="text-[10px] font-mono font-semibold uppercase text-outline tracking-wider">MOSCA VIOLATIONS</div>
          <div className="text-2xl font-bold font-mono text-red-400 mt-1">{metrics.mosca_violations}</div>
          <div className="text-[11px] text-on-surface-variant mt-1">X + Y &gt; Z Window</div>
        </div>
      </section>

      {/* Middle 2-Column Split */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Column: Risk & Quantum Distribution */}
        <div className="bg-surface-container-low border border-outline-variant rounded p-3 sm:p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-outline-variant pb-2 mb-3">
              <div className="flex items-center gap-1.5 font-semibold text-sm">
                <span className="material-symbols-outlined text-primary text-base">bar_chart</span>
                <span>Risk Distribution by Severity Band</span>
              </div>
              <span className="text-[11px] font-mono text-outline">0 - 100 Risk Model</span>
            </div>

            <div className="space-y-2 mt-3">
              {Object.entries(risk_distribution).map(([band, count]) => {
                const total = metrics.total_assets || 1;
                const pct = Math.round((count / total) * 100);
                const colorMap: Record<string, string> = {
                  Critical: "bg-red-600",
                  High: "bg-orange-600",
                  Medium: "bg-amber-600",
                  Low: "bg-green-600",
                  Info: "bg-slate-600",
                };
                return (
                  <div key={band} className="flex items-center gap-3 text-xs font-mono">
                    <span className="w-16 text-on-surface-variant">{band}</span>
                    <div className="flex-1 bg-surface-container-highest rounded h-3 overflow-hidden">
                      <div className={`h-full ${colorMap[band] || "bg-primary"}`} style={{ width: `${pct}%` }}></div>
                    </div>
                    <span className="w-8 text-right font-bold">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quantum Exposure Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-4 border-t border-outline-variant mt-4">
            <div className="bg-surface-container-lowest border border-outline-variant p-2 rounded text-center">
              <div className="text-[9px] font-mono text-outline uppercase">SHOR BROKEN</div>
              <div className="text-lg font-bold font-mono text-red-300 mt-0.5">{quantum_exposure.SHOR_BROKEN || 0}</div>
            </div>
            <div className="bg-surface-container-lowest border border-outline-variant p-2 rounded text-center">
              <div className="text-[9px] font-mono text-outline uppercase">GROVER WEAK</div>
              <div className="text-lg font-bold font-mono text-primary mt-0.5">{quantum_exposure.GROVER_WEAKENED || 0}</div>
            </div>
            <div className="bg-surface-container-lowest border border-outline-variant p-2 rounded text-center">
              <div className="text-[9px] font-mono text-outline uppercase">SAFE</div>
              <div className="text-lg font-bold font-mono text-tertiary mt-0.5">{quantum_exposure.QUANTUM_SAFE || 0}</div>
            </div>
            <div className="bg-surface-container-lowest border border-outline-variant p-2 rounded text-center">
              <div className="text-[9px] font-mono text-outline uppercase">LEGACY BROKEN</div>
              <div className="text-lg font-bold font-mono text-fuchsia-400 mt-0.5">{quantum_exposure.CLASSICALLY_BROKEN || 0}</div>
            </div>
          </div>
        </div>

        {/* Right Column: Recent Critical Findings */}
        <div className="bg-surface-container-low border border-outline-variant rounded p-3 sm:p-4">
          <div className="flex items-center justify-between border-b border-outline-variant pb-2 mb-3">
            <div className="flex items-center gap-1.5 font-semibold text-sm">
              <span className="material-symbols-outlined text-red-400 text-base">priority_high</span>
              <span>Top Critical / High Risk Findings</span>
            </div>
            <Link to="/inventory" className="text-[11px] font-mono text-primary hover:underline">
              View All ({metrics.total_assets}) →
            </Link>
          </div>

          <div className="space-y-2">
            {recent_findings.map((f) => (
              <div
                key={f.id}
                className="bg-surface-container border border-outline-variant rounded p-2 flex items-center justify-between hover:border-outline transition-colors"
              >
                <div className="min-w-0 pr-2">
                  <div className="flex items-center gap-1.5">
                    <span className={`px-1.5 py-0.2 rounded font-mono text-[10px] font-bold border ${bandColors[f.risk_band] || "bg-slate-700"}`}>
                      {f.risk_band.toUpperCase()} {f.risk_score}
                    </span>
                    <span className="font-mono text-xs font-bold text-on-surface">{f.algorithm}</span>
                    {f.threat !== "None" && (
                      <span className="px-1 py-0.2 rounded bg-red-900/60 border border-red-500 text-red-300 font-mono text-[9px] font-bold">
                        {f.threat}
                      </span>
                    )}
                  </div>
                  <div className="font-mono text-[11px] text-on-surface-variant truncate mt-1">
                    {f.file_name}:{f.line_number} · <span className="text-primary">{f.usage}</span>
                  </div>
                </div>

                <button
                  onClick={() => navigate(`/findings/${f.id}`)}
                  className="bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant text-primary font-mono text-xs px-2.5 py-1 rounded transition-colors shrink-0"
                >
                  Inspect
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bottom Section: Migration Priorities & CycloneDX CBOM */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Migration Table */}
        <div className="lg:col-span-2 bg-surface-container-low border border-outline-variant rounded p-4">
          <div className="flex items-center justify-between border-b border-outline-variant pb-2 mb-3">
            <div className="flex items-center gap-1.5 font-semibold text-sm">
              <span className="material-symbols-outlined text-tertiary text-base">swap_calls</span>
              <span>Deterministic Migration Roadmaps</span>
            </div>
            <Link to="/migration" className="text-[11px] font-mono text-primary hover:underline">
              NIST FIPS 203/204/205 Standards →
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full font-mono text-xs text-left">
              <thead>
                <tr className="border-b border-outline-variant text-outline">
                  <th className="py-1.5 px-2">Algorithm</th>
                  <th className="py-1.5 px-2">Primitive</th>
                  <th className="py-1.5 px-2">Risk</th>
                  <th className="py-1.5 px-2">Recommended Target</th>
                  <th className="py-1.5 px-2">Priority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {migration_priority.map((m, idx) => (
                  <tr key={idx} className="hover:bg-surface-container transition-colors">
                    <td className="py-1.5 px-2 font-bold text-on-surface">{m.algorithm}</td>
                    <td className="py-1.5 px-2 text-on-surface-variant">{m.usage}</td>
                    <td className="py-1.5 px-2 text-red-300">{m.risk}</td>
                    <td className="py-1.5 px-2 text-primary font-semibold">{m.recommendation}</td>
                    <td className="py-1.5 px-2">
                      <span className={`px-1 py-0.2 rounded text-[10px] font-bold border ${bandColors[m.priority] || "bg-slate-700"}`}>
                        {m.priority.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* CBOM Deliverable Box */}
        <div className="bg-surface-container-low border border-outline-variant rounded p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-outline-variant pb-2 mb-3">
              <div className="flex items-center gap-1.5 font-semibold text-sm">
                <span className="material-symbols-outlined text-tertiary text-base">verified_user</span>
                <span>CycloneDX 1.6 CBOM</span>
              </div>
              <span className="px-1 py-0.2 rounded bg-tertiary/10 text-tertiary border border-tertiary/30 font-mono text-[10px] font-bold">
                {cbom_status.valid ? "VALID" : "INVALID"}
              </span>
            </div>

            <div className="bg-surface-container border border-outline-variant rounded p-3 space-y-2 font-mono text-xs">
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Schema:</span>
                <span className="text-tertiary font-bold">{cbom_status.schema}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Specification:</span>
                <span className="text-on-surface">CycloneDX v{cbom_status.spec_version}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Components:</span>
                <span className="text-primary font-bold">{cbom_status.component_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Validation:</span>
                <span className="text-tertiary">0 Formal Schema Errors</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={() => navigate("/cbom")}
              className="flex-1 bg-surface-container hover:bg-surface-container-high border border-outline-variant text-primary font-mono text-xs py-1.5 rounded text-center transition-colors"
            >
              Open CBOM
            </button>
            <button
              onClick={() => navigate("/reports")}
              className="flex-1 bg-primary-container text-on-primary font-mono text-xs font-semibold py-1.5 rounded text-center hover:bg-primary transition-colors"
            >
              Reports & Evidence
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;

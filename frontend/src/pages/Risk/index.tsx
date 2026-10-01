import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchRiskAnalysis } from "../../services/api";
import type { RiskAnalysisData } from "../../types";

export const RiskAnalysis: React.FC = () => {
  const [riskData, setRiskData] = useState<RiskAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRiskAnalysis()
      .then((data) => {
        setRiskData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load risk analysis:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="font-code-sm text-on-surface-variant text-sm">Computing deterministic risk vectors...</span>
        </div>
      </div>
    );
  }

  const avg = riskData ? Math.round(riskData.average_score) : 0;
  const dist = riskData?.risk_distribution || {};
  const criticalCount = dist.Critical ?? dist.CRITICAL ?? 0;
  const topFindings = riskData?.top_findings || [];

  return (
    <div className="flex-1 flex flex-col overflow-y-auto bg-background p-3 sm:p-4 space-y-4">
      {/* Top Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-outline-variant pb-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg sm:text-xl font-headline-xl text-on-surface tracking-tight font-bold">
              Cryptographic Risk Analysis
            </h1>
            <span className="px-2 py-0.5 rounded text-code-sm font-code-sm bg-surface-container-highest border border-outline-variant text-primary font-mono">
              RFC-NTRO-892 Engine
            </span>
          </div>
          <p className="text-body-sm font-body-sm text-on-surface-variant mt-0.5 text-xs">
            Quantitative risk scoring and threat surface exposure engine according to ECDAT deterministic formula.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Link
            to="/inventory"
            className="border border-outline-variant bg-surface-container-low hover:bg-surface-container-high text-on-surface px-3 py-1 rounded text-code-sm font-code-sm flex items-center gap-1.5"
          >
            <span className="material-symbols-outlined text-[14px]">table_view</span>
            View Complete Inventory
          </Link>
          <Link
            to="/cbom"
            className="bg-primary-container text-on-primary-container hover:bg-primary font-semibold px-3 py-1 rounded text-code-sm font-code-sm flex items-center gap-1.5 transition-colors"
          >
            <span className="material-symbols-outlined text-[14px]">verified_user</span>
            Inspect CBOM
          </Link>
        </div>
      </div>

      {/* Row 1: Hero Metric Card & Deterministic Formula */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        {/* Overall Risk Hero Metric (5 Columns) */}
        <div className="xl:col-span-5 bg-surface-container-low border border-outline-variant rounded p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-outline-variant pb-2">
            <span className="text-label-caps font-label-caps text-on-surface-variant uppercase text-xs">
              GLOBAL THREAT EXPOSURE
            </span>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-code-sm uppercase font-bold tracking-wide ${
                avg >= 70
                  ? "bg-error-container text-on-error-container border border-error/40"
                  : avg >= 50
                  ? "bg-primary-container/20 text-primary border border-primary/40"
                  : "bg-tertiary/10 text-tertiary border border-tertiary/30"
              }`}
            >
              {avg >= 75 ? "CRITICAL RISK BAND" : avg >= 60 ? "HIGH RISK BAND" : "MODERATE BAND"}
            </span>
          </div>

          <div className="my-4 flex items-baseline gap-4">
            <div className="font-code-lg text-[52px] leading-none font-bold text-primary tracking-tight font-mono">
              {avg}<span className="text-headline-lg text-outline font-normal"> / 100</span>
            </div>
            <div className="space-y-1 text-code-sm">
              <div className="text-xs text-error flex items-center gap-1 font-semibold">
                <span className="material-symbols-outlined text-[14px]">warning</span>
                {criticalCount} Critical Vectors
              </div>
              <div className="text-[11px] text-on-surface-variant">
                {riskData?.hygiene_critical_count || 0} Flagged for Classical Hygiene
              </div>
            </div>
          </div>

          {/* Risk Band Severity Progress Scale */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[11px] font-code-sm text-on-surface-variant">
              <span>Tolerance Threshold: &lt; 35.0</span>
              <span className="text-primary font-medium">Calculated Avg: {avg}.0</span>
            </div>
            <div className="h-2 w-full bg-surface-container-lowest rounded-full overflow-hidden flex">
              <div className="bg-tertiary/60" style={{ width: "35%" }} title="Safe: 0-35"></div>
              <div className="bg-secondary/60" style={{ width: "25%" }} title="Moderate: 36-60"></div>
              <div className="bg-primary" style={{ width: "25%" }} title="High: 61-85"></div>
              <div className="bg-error" style={{ width: "15%" }} title="Critical: 86-100"></div>
            </div>
            <div className="flex justify-between text-[10px] font-code-sm text-outline pt-0.5">
              <span>0 (PQ-Hardened)</span>
              <span>35 (NIST Target)</span>
              <span>75 (Critical)</span>
              <span>100</span>
            </div>
          </div>

          <div className="mt-4 pt-2 border-t border-outline-variant flex items-center justify-between text-code-sm font-code-sm text-on-surface-variant">
            <span>Primary Driver: <strong className="text-on-surface font-mono">{topFindings.length > 0 ? `Shor-vulnerable Primitives (${topFindings[0].algorithm})` : "Cryptographic Primitives"}</strong></span>
            <Link to="/inventory" className="text-primary hover:underline text-xs">Inspect Inventory →</Link>
          </div>
        </div>

        {/* Mathematical Formula Panel (7 Columns) */}
        <div className="xl:col-span-7 bg-surface-container-low border border-outline-variant rounded p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-outline-variant pb-2">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[18px]">functions</span>
              <span className="text-label-caps font-label-caps text-on-surface uppercase text-xs font-semibold">
                ECDAT Deterministic Risk Formulation
              </span>
            </div>
            <span className="font-code-sm text-[11px] text-outline">Deterministic Engine Spec: NTRO-26164</span>
          </div>

          {/* Equation Display */}
          <div className="my-3 p-3 bg-surface-container-lowest border border-outline-variant rounded font-code-md text-xs overflow-x-auto leading-relaxed font-mono">
            <div className="text-on-surface">
              <span className="text-primary font-bold">Risk</span> = <span className="text-outline">100 × (</span>
              <br />
              &nbsp;&nbsp;<span className="text-primary font-semibold">0.35</span> × <span className="text-secondary">QuantumExposure</span> + 
              <br />
              &nbsp;&nbsp;<span className="text-primary font-semibold">0.25</span> × <span className="text-secondary">BusinessCriticality</span> + 
              <br />
              &nbsp;&nbsp;<span className="text-primary font-semibold">0.15</span> × <span className="text-secondary">ExposureSurface</span> + 
              <br />
              &nbsp;&nbsp;<span className="text-primary font-semibold">0.15</span> × <span className="text-secondary">DataSensitivity</span> + 
              <br />
              &nbsp;&nbsp;<span className="text-primary font-semibold">0.10</span> × <span className="text-outline">(1 −</span> <span className="text-tertiary">CryptoAgility</span><span className="text-outline">)</span>
              <br />
              <span className="text-outline">)</span>
            </div>
          </div>

          {/* Mathematical Weight Breakdown Tags */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-code-sm font-code-sm">
            <div className="p-2 bg-surface-container rounded border border-outline-variant/60">
              <div className="text-[10px] text-outline uppercase font-label-caps">W₁ (35%)</div>
              <div className="text-secondary font-medium text-xs truncate">Quantum Exp.</div>
              <div className="text-[10px] text-on-surface-variant mt-0.5">Shor / Grover</div>
            </div>
            <div className="p-2 bg-surface-container rounded border border-outline-variant/60">
              <div className="text-[10px] text-outline uppercase font-label-caps">W₂ (25%)</div>
              <div className="text-secondary font-medium text-xs truncate">Criticality</div>
              <div className="text-[10px] text-on-surface-variant mt-0.5">Production blast</div>
            </div>
            <div className="p-2 bg-surface-container rounded border border-outline-variant/60">
              <div className="text-[10px] text-outline uppercase font-label-caps">W₃ (15%)</div>
              <div className="text-secondary font-medium text-xs truncate">Exposure Surf.</div>
              <div className="text-[10px] text-on-surface-variant mt-0.5">Public API ingress</div>
            </div>
            <div className="p-2 bg-surface-container rounded border border-outline-variant/60">
              <div className="text-[10px] text-outline uppercase font-label-caps">W₄ (15%)</div>
              <div className="text-secondary font-medium text-xs truncate">Sensitivity</div>
              <div className="text-[10px] text-on-surface-variant mt-0.5">Confidential data</div>
            </div>
            <div className="p-2 bg-surface-container rounded border border-outline-variant/60">
              <div className="text-[10px] text-outline uppercase font-label-caps">W₅ (10%)</div>
              <div className="text-tertiary font-medium text-xs truncate">1 − Agility</div>
              <div className="text-[10px] text-on-surface-variant mt-0.5">Refactoring cost</div>
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-outline-variant flex items-center justify-between text-[11px] text-outline">
            <span className="flex items-center gap-1 font-code-sm">
              <span className="material-symbols-outlined text-[13px] text-tertiary">check_circle</span>
              All continuous coefficients normalized on unit interval [0.00, 1.00]
            </span>
          </div>
        </div>
      </div>

      {/* Row 2: Factor Breakdown Grid (5 Metric Cards) */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-headline-md text-headline-md text-on-surface font-semibold flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[16px]">tune</span>
            Factor Breakdown // Active Target Codebase
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Factor 1: Quantum Exposure */}
          <div className="bg-surface-container-low border border-outline-variant rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start">
                <span className="text-[10px] text-outline uppercase font-mono">Weight 0.35</span>
                <span className={`px-1.5 py-0.2 border text-[10px] font-mono rounded ${
                  (riskData?.factor_breakdown?.quantum_exposure ?? 0) >= 0.7
                    ? "bg-error-container/20 text-error border-error/30"
                    : "bg-tertiary/10 text-tertiary border-tertiary/30"
                }`}>
                  {(riskData?.factor_breakdown?.quantum_exposure ?? 0) >= 0.7 ? "CRITICAL" : "CONTROLLED"}
                </span>
              </div>
              <div className="font-semibold text-on-surface mt-1 text-sm">Quantum Exposure</div>
              <div className="font-code-lg text-2xl font-bold text-primary my-1 font-mono">
                {riskData?.factor_breakdown?.quantum_exposure?.toFixed(2) ?? "0.00"}
              </div>
              <p className="text-[11px] text-on-surface-variant leading-tight">
                Reliance on Shor-vulnerable factorization (RSA) and discrete log curves.
              </p>
            </div>
          </div>

          {/* Factor 2: Business Criticality */}
          <div className="bg-surface-container-low border border-outline-variant rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start">
                <span className="text-[10px] text-outline uppercase font-mono">Weight 0.25</span>
                <span className="px-1.5 py-0.2 bg-primary-container/20 text-primary border border-primary/30 text-[10px] font-mono rounded">
                  {(riskData?.factor_breakdown?.business_criticality ?? 0) >= 0.7 ? "HIGH" : "MODERATE"}
                </span>
              </div>
              <div className="font-semibold text-on-surface mt-1 text-sm">Business Criticality</div>
              <div className="font-code-lg text-2xl font-bold text-primary my-1 font-mono">
                {riskData?.factor_breakdown?.business_criticality?.toFixed(2) ?? "0.00"}
              </div>
              <p className="text-[11px] text-on-surface-variant leading-tight">
                Core authentication and security tokens guarding production transactions.
              </p>
            </div>
          </div>

          {/* Factor 3: Exposure Surface */}
          <div className="bg-surface-container-low border border-outline-variant rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start">
                <span className="text-[10px] text-outline uppercase font-mono">Weight 0.15</span>
                <span className="px-1.5 py-0.2 bg-surface-container-high text-secondary border border-outline-variant text-[10px] font-mono rounded">
                  {(riskData?.factor_breakdown?.exposure_surface ?? 0) >= 0.7 ? "EXTERNAL" : "ELEVATED"}
                </span>
              </div>
              <div className="font-semibold text-on-surface mt-1 text-sm">Exposure Surface</div>
              <div className="font-code-lg text-2xl font-bold text-primary my-1 font-mono">
                {riskData?.factor_breakdown?.exposure_surface?.toFixed(2) ?? "0.00"}
              </div>
              <p className="text-[11px] text-on-surface-variant leading-tight">
                Externally exposed endpoint certificates and public handshake handoffs.
              </p>
            </div>
          </div>

          {/* Factor 4: Data Sensitivity */}
          <div className="bg-surface-container-low border border-outline-variant rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start">
                <span className="text-[10px] text-outline uppercase font-mono">Weight 0.15</span>
                <span className="px-1.5 py-0.2 bg-primary-container/20 text-primary border border-primary/30 text-[10px] font-mono rounded">
                  {(riskData?.factor_breakdown?.data_sensitivity ?? 0) >= 0.7 ? "CONFIDENTIAL" : "STANDARD"}
                </span>
              </div>
              <div className="font-semibold text-on-surface mt-1 text-sm">Data Sensitivity</div>
              <div className="font-code-lg text-2xl font-bold text-primary my-1 font-mono">
                {riskData?.factor_breakdown?.data_sensitivity?.toFixed(2) ?? "0.00"}
              </div>
              <p className="text-[11px] text-on-surface-variant leading-tight">
                Long-lived credentials and encrypted data requiring 10+ years confidentiality.
              </p>
            </div>
          </div>

          {/* Factor 5: Inversed Agility */}
          <div className="bg-surface-container-low border border-outline-variant rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start">
                <span className="text-[10px] text-outline uppercase font-mono">Weight 0.10</span>
                <span className="px-1.5 py-0.2 bg-error-container/20 text-error border border-error/30 text-[10px] font-mono rounded">
                  {(riskData?.factor_breakdown?.inversed_agility ?? 0) >= 0.5 ? "RIGID" : "AGILE"}
                </span>
              </div>
              <div className="font-semibold text-on-surface mt-1 text-sm">Inversed Agility</div>
              <div className="font-code-lg text-2xl font-bold text-primary my-1 font-mono">
                {riskData?.factor_breakdown?.inversed_agility?.toFixed(2) ?? "0.00"}
              </div>
              <p className="text-[11px] text-on-surface-variant leading-tight">
                Hardcoded primitives with tight dependency coupling requiring refactor.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Top Risk Findings Table */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-headline-md text-headline-md text-on-surface font-semibold flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">list_alt</span>
            Top Risk-Ranked Findings in Inventory
          </h2>
          <span className="text-code-sm text-outline">Sorted by Deterministic Risk Score DESC</span>
        </div>

        <div className="border border-outline-variant rounded overflow-hidden">
          <table className="w-full text-left text-code-sm font-code-sm">
            <thead className="bg-surface-container border-b border-outline-variant text-on-surface-variant text-[11px]">
              <tr>
                <th className="py-2 px-3">Rule ID</th>
                <th className="py-2 px-3">Algorithm</th>
                <th className="py-2 px-3">Primitive</th>
                <th className="py-2 px-3">File Location</th>
                <th className="py-2 px-3">Quantum Status</th>
                <th className="py-2 px-3">Risk Band</th>
                <th className="py-2 px-3 text-right">Risk Score</th>
                <th className="py-2 px-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {topFindings.map((item) => (
                <tr key={item.id} className="hover:bg-surface-container-high/50 transition-colors">
                  <td className="py-2 px-3 text-primary font-mono">{item.rule_id}</td>
                  <td className="py-2 px-3 font-semibold text-on-surface font-mono">{item.algorithm}</td>
                  <td className="py-2 px-3 text-on-surface-variant">{item.primitive}</td>
                  <td className="py-2 px-3 text-secondary font-mono truncate max-w-xs">{item.file_path}:{item.line}</td>
                  <td className="py-2 px-3">
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-container border border-outline-variant text-primary">
                      {item.quantum}
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        item.risk_band?.toUpperCase() === "CRITICAL"
                          ? "bg-error-container text-on-error-container"
                          : item.risk_band?.toUpperCase() === "HIGH"
                          ? "bg-primary-container/20 text-primary border border-primary/30"
                          : "bg-surface-container-high text-secondary"
                      }`}
                    >
                      {item.risk_band}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-right font-bold text-on-surface font-mono">
                    {Math.round(item.risk_score)}
                  </td>
                  <td className="py-2 px-3 text-center">
                    <Link
                      to={`/findings/${item.id}`}
                      className="px-2 py-0.5 bg-surface-container-high border border-outline-variant hover:border-primary text-primary rounded text-xs transition-colors"
                    >
                      Inspect
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
export default RiskAnalysis;

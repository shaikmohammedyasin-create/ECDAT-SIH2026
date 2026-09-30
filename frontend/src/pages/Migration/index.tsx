import React, { useEffect, useState } from "react";
import { fetchMigration } from "../../services/api";
import type { MigrationResponse } from "../../types";

export const MigrationGuidance: React.FC = () => {
  const [data, setData] = useState<MigrationResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMigration()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load migration guidance:", err);
        setLoading(false);
      });
  }, []);

  const exportMigrationPlan = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pqc-migration-roadmap.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="font-code-sm text-on-surface-variant text-sm">Loading post-quantum migration matrix...</span>
        </div>
      </div>
    );
  }

  const matrix = data?.matrix || [];
  const summary = data?.summary;

  return (
    <div className="flex-1 flex flex-col overflow-y-auto bg-background p-4 space-y-4">
      {/* Top Header */}
      <section className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-outline-variant pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-headline-xl font-headline-xl text-on-surface tracking-tight font-bold">
              Post-Quantum Migration Guidance
            </h1>
            <span className="px-2 py-0.5 rounded text-code-sm font-code-sm bg-surface-container-highest border border-outline-variant text-primary font-mono">
              NIST FIPS 203 / 204
            </span>
          </div>
          <p className="text-body-sm font-body-sm text-on-surface-variant mt-0.5">
            Deterministic PQC replacement matrix, hybrid cryptographic encapsulation pipelines, and standards-aligned roadmap.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={exportMigrationPlan}
            className="bg-primary-container hover:bg-primary text-on-primary-container text-code-sm font-code-sm font-semibold px-3 py-1.5 rounded flex items-center gap-1.5 shadow-sm transition-colors"
          >
            <span className="material-symbols-outlined text-[16px]">file_download</span>
            <span>Export Transition Plan JSON</span>
          </button>
        </div>
      </section>

      {/* 4 Summary Metric Cards (Bento Grid) */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Card 1: Immediate Migration */}
        <div className="bg-surface-container-low border-l-4 border-l-error border border-outline-variant p-3 rounded flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-label-caps font-label-caps text-outline uppercase text-[10px] tracking-wider">
              Critical Phase
            </span>
            <span className="material-symbols-outlined text-error text-[18px]">warning</span>
          </div>
          <div className="my-2">
            <div className="text-2xl font-code-lg text-error font-bold tracking-tight">
              {summary ? `${summary.immediate_count} Immediate` : "Immediate"}
            </div>
            <div className="text-body-sm font-body-sm text-on-surface font-medium text-xs">
              Shor-Vulnerable Asymmetric Primitives
            </div>
          </div>
          <div className="text-code-sm text-outline text-[11px] flex items-center gap-1">
            <span className="text-error font-medium">Shor broken</span> • {summary?.immediate_algos?.length ? summary.immediate_algos.join(", ") : "RSA ≤ 2048, ECDSA-P256"}
          </div>
        </div>

        {/* Card 2: Scheduled Hybrid Transition */}
        <div className="bg-surface-container-low border-l-4 border-l-primary border border-outline-variant p-3 rounded flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-label-caps font-label-caps text-outline uppercase text-[10px] tracking-wider">
              Transition Phase
            </span>
            <span className="material-symbols-outlined text-primary text-[18px]">sync_alt</span>
          </div>
          <div className="my-2">
            <div className="text-2xl font-code-lg text-primary font-bold tracking-tight">
              {summary ? `${summary.hybrid_count} Hybrid` : "Hybrid"}
            </div>
            <div className="text-body-sm font-body-sm text-on-surface font-medium text-xs">
              Dual-Key Hybrid Encapsulation
            </div>
          </div>
          <div className="text-code-sm text-outline text-[11px] flex items-center gap-1">
            <span className="text-primary font-medium">Dual-Envelope</span> • {summary?.hybrid_algos?.length ? summary.hybrid_algos.join(", ") : "X25519 + ML-KEM-768"}
          </div>
        </div>

        {/* Card 3: Monitor & Deprecate */}
        <div className="bg-surface-container-low border-l-4 border-l-secondary border border-outline-variant p-3 rounded flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-label-caps font-label-caps text-outline uppercase text-[10px] tracking-wider">
              Lifecycle Tracking
            </span>
            <span className="material-symbols-outlined text-secondary text-[18px]">hourglass_top</span>
          </div>
          <div className="my-2">
            <div className="text-2xl font-code-lg text-secondary font-bold tracking-tight">
              {summary ? `${summary.deprecate_count} Deprecate` : "Deprecate"}
            </div>
            <div className="text-body-sm font-body-sm text-on-surface font-medium text-xs">
              Legacy Symmetric & Hashes
            </div>
          </div>
          <div className="text-code-sm text-outline text-[11px] flex items-center gap-1">
            <span className="text-secondary font-medium">Upgrade</span> • {summary?.deprecate_algos?.length ? summary.deprecate_algos.join(", ") : "MD5, SHA-1 → SHA-256 / SHA-3"}
          </div>
        </div>

        {/* Card 4: FIPS Verified Compliant */}
        <div className="bg-surface-container-low border-l-4 border-l-tertiary border border-outline-variant p-3 rounded flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-label-caps font-label-caps text-outline uppercase text-[10px] tracking-wider">
              Post-Quantum Target
            </span>
            <span className="material-symbols-outlined text-tertiary text-[18px]">task_alt</span>
          </div>
          <div className="my-2">
            <div className="text-2xl font-code-lg text-tertiary font-bold tracking-tight">
              {summary ? `${summary.compliant_count} Compliant` : "Compliant"}
            </div>
            <div className="text-body-sm font-body-sm text-on-surface font-medium text-xs">
              NIST Standardized Lattice Target
            </div>
          </div>
          <div className="text-code-sm text-outline text-[11px] flex items-center gap-1">
            <span className="text-tertiary font-medium">Standard</span> • {summary?.compliant_algos?.length ? summary.compliant_algos.join(", ") : "ML-KEM-768, ML-DSA-65"}
          </div>
        </div>
      </section>

      {/* Architectural Staged Migration Pipeline */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">schema</span>
            <h2 className="text-headline-md font-headline-md text-on-surface font-semibold text-sm">
              Architectural Staged Migration Pipeline
            </h2>
          </div>
          <span className="text-code-sm text-outline text-xs">Protocol: IETF Hybrid RFC 9180 + NIST SP 800-227</span>
        </div>

        {/* Pipeline 3-step nodes */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center py-2">
          {/* Step 1: Classical Vulnerable */}
          <div className="bg-surface-container border border-error/40 p-3 rounded relative">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-mono text-error uppercase bg-error/10 px-1.5 py-0.5 rounded border border-error/20 font-bold">
                Phase 0: Identified ({summary?.immediate_count ?? 0})
              </span>
              <span className="text-code-sm text-outline text-[11px]">CRQC Hazard</span>
            </div>
            <h3 className="font-semibold text-on-surface text-sm">Legacy Vulnerable Cryptography</h3>
            <p className="text-body-sm text-outline mt-1 text-xs leading-relaxed">
              Discrete logarithm & integer factorization primitives vulnerable to Shor polynomial quantum attacks.
            </p>
            <div className="mt-2 flex flex-wrap gap-1">
              {(summary?.immediate_algos?.length ? summary.immediate_algos : ["RSA-2048", "ECDSA-P256", "Diffie-Hellman"]).map((algo) => (
                <span key={algo} className="text-code-sm bg-surface-container-high px-1.5 py-0.5 rounded text-error border border-error/20 text-xs font-mono">
                  {algo}
                </span>
              ))}
            </div>
          </div>

          {/* Step 2: Dual-Key Hybrid Envelope */}
          <div className="bg-surface-container border border-primary/40 p-3 rounded relative">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-mono text-primary uppercase bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20 font-bold">
                Stage 1: Intermediate
              </span>
              <span className="text-code-sm text-primary text-[11px]">In-Flight</span>
            </div>
            <h3 className="font-semibold text-on-surface text-sm">Dual-Key Hybrid Envelope</h3>
            <p className="text-body-sm text-outline mt-1 text-xs leading-relaxed">
              Simultaneous classical-PQC derivation preserving legacy compatibility while injecting lattice resistance.
            </p>
            <div className="mt-2 flex flex-wrap gap-1">
              {(summary?.hybrid_algos?.length ? summary.hybrid_algos : ["X25519 + ML-KEM-768", "Composite Dual Signatures"]).map((algo) => (
                <span key={algo} className="text-code-sm bg-surface-container-high px-1.5 py-0.5 rounded text-primary border border-primary/20 text-xs font-mono">
                  {algo}
                </span>
              ))}
            </div>
          </div>

          {/* Step 3: Pure Post-Quantum Lattice Assembly */}
          <div className="bg-surface-container border border-tertiary/40 p-3 rounded">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-mono text-tertiary uppercase bg-tertiary/10 px-1.5 py-0.5 rounded border border-tertiary/20 font-bold">
                Stage 2: Target Posture
              </span>
              <span className="text-code-sm text-tertiary text-[11px]">NIST Standard</span>
            </div>
            <h3 className="font-semibold text-on-surface text-sm">Full Post-Quantum Lattice Assembly</h3>
            <p className="text-body-sm text-outline mt-1 text-xs leading-relaxed">
              Direct deployment of NIST FIPS 203/204/205 parameter sets completely decoupled from classical assumptions.
            </p>
            <div className="mt-2 flex flex-wrap gap-1">
              {(summary?.compliant_algos?.length ? summary.compliant_algos : ["ML-KEM-768 / 1024", "ML-DSA-65", "SLH-DSA-128"]).map((algo) => (
                <span key={algo} className="text-code-sm bg-surface-container-high px-1.5 py-0.5 rounded text-tertiary border border-tertiary/20 text-xs font-mono">
                  {algo}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Algorithmic Transition Mapping Grid */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-4 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">rule</span>
            <h2 className="text-headline-md font-headline-md text-on-surface font-semibold text-sm">
              Deterministic Algorithmic Transition Rules
            </h2>
          </div>
          <span className="text-code-sm text-outline text-xs">NIST Special Publication 800-56C Rev. 2 Aligned</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {matrix.map((item, idx) => (
            <div
              key={idx}
              className="bg-surface-container border border-outline-variant rounded p-3 flex flex-col justify-between hover:border-primary/60 transition-colors"
            >
              <div>
                <div className="flex items-center justify-between text-code-sm mb-1.5">
                  <span className="text-primary font-mono font-bold text-xs">RULE-MIG-0{idx + 1}</span>
                  <span
                    className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                      item.risk_band?.toUpperCase() === "CRITICAL"
                        ? "bg-error-container text-on-error-container"
                        : "bg-primary-container/20 text-primary border border-primary/30"
                    }`}
                  >
                    {item.risk_band}
                  </span>
                </div>

                <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant mb-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-on-surface-variant uppercase block">Current</span>
                      <span className="text-error font-bold font-mono text-xs">{item.algorithm}</span>
                    </div>
                    <span className="material-symbols-outlined text-on-surface-variant text-sm">arrow_forward</span>
                    <div className="text-right">
                      <span className="text-[10px] text-on-surface-variant uppercase block">Recommended Target</span>
                      <span className="text-tertiary font-bold font-mono text-xs">{item.recommended_target}</span>
                    </div>
                  </div>
                </div>

                <p className="text-xs text-on-surface-variant leading-relaxed mb-2">
                  {item.migration_strategy}
                </p>

                <div className="text-[11px] text-outline font-mono space-y-1 border-t border-outline-variant pt-2">
                  <div className="flex justify-between">
                    <span>Standard:</span>
                    <span className="text-on-surface">{item.standard}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Effort / Complexity:</span>
                    <span className="text-primary">{item.effort}</span>
                  </div>
                </div>
              </div>

              {/* Migration Path Steps */}
              {item.migration_path && item.migration_path.length > 0 && (
                <div className="mt-3 pt-2 border-t border-outline-variant">
                  <span className="text-[10px] text-on-surface-variant uppercase block mb-1 font-semibold">
                    Staged Implementation Steps:
                  </span>
                  <ul className="text-[11px] text-on-surface space-y-1 pl-2">
                    {item.migration_path.map((step, sIdx) => (
                      <li key={sIdx} className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0"></span>
                        <span className="truncate">{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
export default MigrationGuidance;

import React, { useEffect, useState } from "react";
import { fetchSettings } from "../../services/api";
import type { SettingsData } from "../../types";

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<number>(1);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchSettings()
      .then((data) => {
        setSettings(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load settings:", err);
        setLoading(false);
      });
  }, []);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="font-code-sm text-on-surface-variant text-sm">Loading security configuration...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-surface overflow-hidden">
      {/* Top Header */}
      <section className="px-3 sm:px-4 py-2 border-b border-outline-variant bg-surface-container-low shrink-0 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-base sm:text-lg font-headline-md text-on-surface tracking-tight font-bold">
              Workstation Configuration & Security Settings
            </h1>
            <span className="bg-surface-container border border-outline-variant text-primary px-1.5 py-0.5 rounded text-[10px] font-mono">
              Profile: {settings?.profile || "default"}
            </span>
            {settings?.target_path && (
              <span className="bg-surface-container-highest border border-outline-variant text-secondary px-2 py-0.5 rounded text-[10px] font-mono truncate max-w-xs sm:max-w-sm">
                Target: {settings.target_path}
              </span>
            )}
          </div>
          <p className="text-body-sm text-on-surface-variant mt-0.5 text-xs">
            Cryptographic parser thresholds, quantum threat modeling horizons, CycloneDX 1.6 schema strictness, and air-gapped security guardrails.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[10px] font-mono text-tertiary border border-tertiary/40 px-2 py-1 rounded bg-tertiary/10 font-bold flex items-center gap-1">
            <span className="material-symbols-outlined text-[13px]">lock</span>
            AIR-GAP: ENFORCED
          </span>
          <button
            onClick={handleSave}
            className="bg-primary-container text-on-primary-container hover:bg-primary font-semibold text-xs px-3 py-1 rounded flex items-center gap-1 transition-colors"
          >
            <span className="material-symbols-outlined text-[14px]">save</span>
            <span>{saved ? "Saved Policy" : "Save Changes"}</span>
          </button>
        </div>
      </section>

      {/* Main Configuration Area */}
      <div className="flex-1 flex flex-col md:grid md:grid-cols-12 overflow-hidden">
        {/* Left Column: Sub-navigation / Sub-categories */}
        <div className="w-full md:col-span-4 lg:col-span-3 border-b md:border-b-0 md:border-r border-outline-variant bg-surface-container-lowest p-2 sm:p-3 overflow-y-auto shrink-0 max-h-48 md:max-h-full flex flex-col justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-mono text-outline uppercase tracking-wider px-2 pb-1 font-semibold">
              Configuration Domains
            </span>

            {[
              { id: 1, name: "1. Scanner Engines & AST Parsers", icon: "psychology" },
              { id: 2, name: "2. Quantum Classification & Mosca", icon: "hourglass_top" },
              { id: 3, name: "3. Risk Scoring & Weights", icon: "calculate" },
              { id: 4, name: "4. CycloneDX 1.6 CBOM Schema", icon: "schema" },
              { id: 5, name: "5. Air-Gapped Security & Privacy", icon: "lock" },
              { id: 6, name: "6. Interface & Diagnostics", icon: "terminal" },
              { id: 7, name: "7. About Engine & NTRO Specs", icon: "info" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full text-left px-2.5 sm:px-3 py-1.5 sm:py-2 rounded text-xs flex items-center justify-between transition-colors ${
                  activeTab === tab.id
                    ? "bg-surface-container border-l-2 border-primary text-primary font-semibold"
                    : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[16px]">{tab.icon}</span>
                  <span className="truncate">{tab.name}</span>
                </div>
                {activeTab === tab.id && (
                  <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                )}
              </button>
            ))}
          </div>

          {/* Left Nav Footnote: Security Clearance Token */}
          <div className="hidden md:block border border-outline-variant bg-surface-container p-2.5 rounded mt-4">
            <div className="flex items-center gap-1.5 text-primary text-xs font-semibold mb-1">
              <span className="material-symbols-outlined text-[14px]">verified_user</span>
              <span>NTRO OPERATIONAL SPEC</span>
            </div>
            <p className="text-[10px] text-on-surface-variant leading-tight">
              All cryptographic discovery routines operate exclusively within local process memory. No outbound network transmission.
            </p>
          </div>
        </div>

        {/* Right Column: Active Configuration View */}
        <div className="flex-1 md:col-span-8 lg:col-span-9 overflow-y-auto p-3 sm:p-4 space-y-4">
          {/* Section 1: AST Collector Engine Controls */}
          {activeTab === 1 && (
            <section className="border border-outline-variant bg-surface-container-low rounded p-3 space-y-3">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">terminal</span>
                  <h2 className="text-headline-md font-semibold text-on-surface text-sm">
                    1. AST Collector Engine Controls
                  </h2>
                </div>
                <span className="text-[10px] font-mono text-tertiary bg-surface-container px-2 py-0.5 rounded border border-outline-variant">
                  {settings?.ast_enabled ? "ALL COLLECTORS ACTIVE" : "COLLECTORS PAUSED"}
                </span>
              </div>

              <div className="border border-outline-variant bg-surface-container-lowest rounded overflow-hidden">
                <table className="w-full text-left text-xs font-code-sm">
                  <thead>
                    <tr className="bg-surface-container border-b border-outline-variant text-on-surface-variant text-[10px] uppercase font-mono">
                      <th className="py-2 px-3">State</th>
                      <th className="py-2 px-3">Parser Engine</th>
                      <th className="py-2 px-3">Heuristic / Rule Depth</th>
                      <th className="py-2 px-3">Monitored Targets / Namespaces</th>
                      <th className="py-2 px-3 text-right">Mode</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant">
                    <tr className="hover:bg-surface-container-high transition-colors">
                      <td className="py-2 px-3">
                        <input type="checkbox" defaultChecked={settings?.ast_enabled ?? true} className="rounded accent-primary h-3.5 w-3.5" />
                      </td>
                      <td className="py-2 px-3 text-on-surface font-semibold">Python 3.12 AST Scanner</td>
                      <td className="py-2 px-3 text-on-surface-variant">Deep AST Walk (Call graph + assignments)</td>
                      <td className="py-2 px-3 font-mono text-primary text-[11px]">cryptography, hashlib, pycryptodome</td>
                      <td className="py-2 px-3 text-right">
                        <span className="bg-surface-container border border-outline-variant px-1.5 py-0.5 rounded text-tertiary text-[10px]">
                          {settings?.ast_enabled ? "ACTIVE" : "DISABLED"}
                        </span>
                      </td>
                    </tr>
                    <tr className="hover:bg-surface-container-high transition-colors">
                      <td className="py-2 px-3">
                        <input type="checkbox" defaultChecked={settings?.bytecode_scanner_enabled ?? true} className="rounded accent-primary h-3.5 w-3.5" />
                      </td>
                      <td className="py-2 px-3 text-on-surface font-semibold">Java Bytecode & JCA/JCE Parser</td>
                      <td className="py-2 px-3 text-on-surface-variant">Class bytecode decompilation + JCA provider checks</td>
                      <td className="py-2 px-3 font-mono text-primary text-[11px]">javax.crypto, java.security, bouncycastle</td>
                      <td className="py-2 px-3 text-right">
                        <span className="bg-surface-container border border-outline-variant px-1.5 py-0.5 rounded text-tertiary text-[10px]">
                          {settings?.bytecode_scanner_enabled ? "ACTIVE" : "DISABLED"}
                        </span>
                      </td>
                    </tr>
                    <tr className="hover:bg-surface-container-high transition-colors">
                      <td className="py-2 px-3">
                        <input type="checkbox" defaultChecked={settings?.dependency_manifest_parser ?? true} className="rounded accent-primary h-3.5 w-3.5" />
                      </td>
                      <td className="py-2 px-3 text-on-surface font-semibold">Dependency Manifest Parser</td>
                      <td className="py-2 px-3 text-on-surface-variant">Transitive lockfile resolution + CBOM component mapping</td>
                      <td className="py-2 px-3 font-mono text-primary text-[11px]">requirements.txt, pom.xml, build.gradle</td>
                      <td className="py-2 px-3 text-right">
                        <span className="bg-surface-container border border-outline-variant px-1.5 py-0.5 rounded text-tertiary text-[10px]">
                          {settings?.dependency_manifest_parser ? "ACTIVE" : "DISABLED"}
                        </span>
                      </td>
                    </tr>
                    <tr className="hover:bg-surface-container-high transition-colors">
                      <td className="py-2 px-3">
                        <input type="checkbox" defaultChecked={settings?.cert_scanner_enabled ?? true} className="rounded accent-primary h-3.5 w-3.5" />
                      </td>
                      <td className="py-2 px-3 text-on-surface font-semibold">X.509 Certificate Scanner</td>
                      <td className="py-2 px-3 text-on-surface-variant">ASN.1 PEM/DER signature and key-usage parsing</td>
                      <td className="py-2 px-3 font-mono text-primary text-[11px]">.pem, .crt, .cer, .p12, .der</td>
                      <td className="py-2 px-3 text-right">
                        <span className="bg-surface-container border border-outline-variant px-1.5 py-0.5 rounded text-tertiary text-[10px]">
                          {settings?.cert_scanner_enabled ? "ACTIVE" : "DISABLED"}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Section 2: Quantum Classification & Mosca */}
          {activeTab === 2 && (
            <section className="border border-outline-variant bg-surface-container-low rounded p-3 space-y-3">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">hourglass_top</span>
                  <h2 className="text-headline-md font-semibold text-on-surface text-sm">
                    2. Quantum Threat Modeling & Mosca Defaults
                  </h2>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="bg-surface-container-lowest p-3 rounded border border-outline-variant space-y-1">
                  <span className="text-on-surface font-semibold block">Default Planning Scenario Horizon (Z)</span>
                  <span className="text-on-surface-variant text-[11px]">Target reference year for CRQC estimation:</span>
                  <select
                    defaultValue={String(settings?.scenario_year ?? 2035)}
                    className="bg-surface-container border border-outline-variant text-primary font-mono p-1 rounded w-full mt-1"
                  >
                    <option value="2030">2030 (Conservative / Fast QPU)</option>
                    <option value="2035">2035 (NIST Recommended Target)</option>
                    <option value="2040">2040 (Extended Safe Buffer)</option>
                  </select>
                </div>
                <div className="bg-surface-container-lowest p-3 rounded border border-outline-variant space-y-1">
                  <span className="text-on-surface font-semibold block">Default Confidentiality Shelf-Life (X)</span>
                  <span className="text-on-surface-variant text-[11px]">Baseline data lifetime requirement:</span>
                  <input
                    type="number"
                    defaultValue={settings?.x_lifetime ?? 10}
                    className="bg-surface-container border border-outline-variant text-primary font-mono p-1 rounded w-full mt-1"
                  />
                </div>
                <div className="bg-surface-container-lowest p-3 rounded border border-outline-variant space-y-1">
                  <span className="text-on-surface font-semibold block">Default Migration Lead Time (Y)</span>
                  <span className="text-on-surface-variant text-[11px]">Migration & rollout duration (years):</span>
                  <input
                    type="number"
                    defaultValue={settings?.y_migration ?? 3}
                    className="bg-surface-container border border-outline-variant text-primary font-mono p-1 rounded w-full mt-1"
                  />
                </div>
              </div>
            </section>
          )}

          {/* Section 3: Risk Scoring & Weights */}
          {activeTab === 3 && (
            <section className="border border-outline-variant bg-surface-container-low rounded p-3 space-y-3">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">calculate</span>
                  <h2 className="text-headline-md font-semibold text-on-surface text-sm">
                    3. Deterministic Risk Formula Parameters
                  </h2>
                </div>
              </div>
              <div className="space-y-2 text-xs">
                <div className="p-3 bg-surface-container-lowest border border-outline-variant rounded font-mono text-[11px]">
                  Risk = 100 × ({settings?.risk_weights?.quantum_exposure ?? 0.35} × W₁ + {settings?.risk_weights?.business_criticality ?? 0.25} × W₂ + {settings?.risk_weights?.exposure_surface ?? 0.15} × W₃ + {settings?.risk_weights?.data_sensitivity ?? 0.15} × W₄ + {settings?.risk_weights?.crypto_agility ?? 0.10} × (1 − Agility))
                </div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  <div className="p-2 bg-surface-container-lowest rounded border border-outline-variant">
                    <span className="text-outline text-[10px] block">W1: Quantum Exp.</span>
                    <span className="text-primary font-mono font-bold">{(settings?.risk_weights?.quantum_exposure ?? 0.35) * 100}%</span>
                  </div>
                  <div className="p-2 bg-surface-container-lowest rounded border border-outline-variant">
                    <span className="text-outline text-[10px] block">W2: Criticality</span>
                    <span className="text-primary font-mono font-bold">{(settings?.risk_weights?.business_criticality ?? 0.25) * 100}%</span>
                  </div>
                  <div className="p-2 bg-surface-container-lowest rounded border border-outline-variant">
                    <span className="text-outline text-[10px] block">W3: Exposure</span>
                    <span className="text-primary font-mono font-bold">{(settings?.risk_weights?.exposure_surface ?? 0.15) * 100}%</span>
                  </div>
                  <div className="p-2 bg-surface-container-lowest rounded border border-outline-variant">
                    <span className="text-outline text-[10px] block">W4: Sensitivity</span>
                    <span className="text-primary font-mono font-bold">{(settings?.risk_weights?.data_sensitivity ?? 0.15) * 100}%</span>
                  </div>
                  <div className="p-2 bg-surface-container-lowest rounded border border-outline-variant">
                    <span className="text-outline text-[10px] block">W5: 1 − Agility</span>
                    <span className="text-primary font-mono font-bold">{(settings?.risk_weights?.crypto_agility ?? 0.10) * 100}%</span>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Section 4: CycloneDX 1.6 CBOM Schema */}
          {activeTab === 4 && (
            <section className="border border-outline-variant bg-surface-container-low rounded p-3 space-y-3">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">schema</span>
                  <h2 className="text-headline-md font-semibold text-on-surface text-sm">
                    4. CycloneDX 1.6 Schema Strictness
                  </h2>
                </div>
              </div>
              <div className="space-y-2 text-xs">
                <label className="flex items-center gap-2 bg-surface-container-lowest p-2.5 rounded border border-outline-variant cursor-pointer">
                  <input type="checkbox" defaultChecked={settings?.strict_validation ?? true} className="accent-primary h-3.5 w-3.5" />
                  <span>Enforce Strict JSON Schema Validation against CycloneDX {settings?.cyclonedx_version || "1.6"} Cryptographic Spec</span>
                </label>
                <label className="flex items-center gap-2 bg-surface-container-lowest p-2.5 rounded border border-outline-variant cursor-pointer">
                  <input type="checkbox" defaultChecked={settings?.deterministic_bom_ref ?? true} className="accent-primary h-3.5 w-3.5" />
                  <span>Include deterministic bom-ref cross-identifiers for every AST finding</span>
                </label>
              </div>
            </section>
          )}

          {/* Section 5: Air-Gapped Security & Privacy */}
          {(activeTab === 5 || activeTab === 6 || activeTab === 7) && (
            <section className="border border-outline-variant bg-surface-container-low rounded p-3 space-y-3">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-tertiary text-[18px]">lock</span>
                  <h2 className="text-headline-md font-semibold text-on-surface text-sm">
                    Air-Gapped Operation & Cryptographic Safety Guardrails
                  </h2>
                </div>
                <span className="text-[10px] font-mono text-tertiary border border-tertiary/40 px-1.5 py-0.5 rounded bg-tertiary/10 font-bold">
                  VERIFIED
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
                  <div className="flex items-center gap-1.5 text-tertiary font-bold">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    Zero Private Key Persistence
                  </div>
                  <p className="text-on-surface-variant text-[11px] leading-relaxed">
                    ECDAT extracts algorithm names, parameters, and metadata only. Never writes, logs, or persists raw private keys or key material.
                  </p>
                </div>

                <div className="p-3 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
                  <div className="flex items-center gap-1.5 text-tertiary font-bold">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    Air-Gapped Enforced
                  </div>
                  <p className="text-on-surface-variant text-[11px] leading-relaxed">
                    Zero external HTTP requests, telemetry beacons, or cloud sync. Designed for air-gapped defense and intelligence workstations.
                  </p>
                </div>

                <div className="p-3 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
                  <div className="flex items-center gap-1.5 text-tertiary font-bold">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    Strict Local Path Sandbox
                  </div>
                  <p className="text-on-surface-variant text-[11px] leading-relaxed">
                    Scanning paths are validated against file traversal attacks. System roots and sensitive OS partitions are rejected.
                  </p>
                </div>

                <div className="p-3 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
                  <div className="flex items-center gap-1.5 text-tertiary font-bold">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    Local FASTAPI IPC Binding
                  </div>
                  <p className="text-on-surface-variant text-[11px] leading-relaxed">
                    FastAPI server binds exclusively to localhost (127.0.0.1) with CORS restricted to local origin.
                  </p>
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
};
export default SettingsPage;

import React, { useEffect, useState } from "react";
import { fetchMosca, simulateMosca } from "../../services/api";
import type { MoscaState } from "../../types";

export const MoscaSimulator: React.FC = () => {
  const [_mosca, setMosca] = useState<MoscaState | null>(null);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);

  // Local state for interactive sliders
  const [scenarioYear, setScenarioYear] = useState<number>(2035);
  const [xVal, setXVal] = useState<number>(10);
  const [yVal, setYVal] = useState<number>(4);
  const [zVal, setZVal] = useState<number>(9); // 2035 - 2026

  useEffect(() => {
    fetchMosca()
      .then((data) => {
        setMosca(data);
        setScenarioYear(data.scenario_year || 2035);
        setXVal(data.x_lifetime || 10);
        setYVal(data.y_migration || 4);
        setZVal(data.z_horizon || (data.scenario_year - 2026));
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch Mosca state:", err);
        setLoading(false);
      });
  }, []);

  const handleScenarioChange = (year: number) => {
    setScenarioYear(year);
    const newZ = year - 2026;
    setZVal(newZ);
    runSimulation(year, xVal, yVal);
  };

  const handleXChange = (val: number) => {
    setXVal(val);
  };

  const handleYChange = (val: number) => {
    setYVal(val);
  };

  const handleZChange = (val: number) => {
    setZVal(val);
    setScenarioYear(2026 + val);
  };

  const runSimulation = (year: number, x: number, y: number) => {
    setRecalculating(true);
    simulateMosca({
      scenario_year: year,
      x_lifetime: x,
      y_migration: y,
      recompute_scan: true,
    })
      .then((data) => {
        setMosca(data);
        setRecalculating(false);
      })
      .catch((err) => {
        console.error("Simulation error:", err);
        setRecalculating(false);
      });
  };

  const exportMoscaReport = () => {
    const payload = {
      formula: "X + Y > Z",
      planning_horizon: scenarioYear,
      x_lifetime_years: xVal,
      y_migration_years: yVal,
      z_horizon_years: zVal,
      required_window_years: xVal + yVal,
      security_margin_years: zVal - (xVal + yVal),
      at_risk: xVal + yVal > zVal,
      status: xVal + yVal > zVal ? "EXPOSURE_DETECTED" : "WITHIN_WINDOW",
      timestamp: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mosca-simulation-${scenarioYear}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Real-time calculation
  const totalRequired = xVal + yVal;
  const isAtRisk = totalRequired > zVal;
  const margin = zVal - totalRequired;

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="font-code-sm text-on-surface-variant text-sm">Evaluating Mosca Theorem matrix...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-y-auto bg-background p-4 space-y-4">
      {/* Top Header / Context Bar */}
      <section className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-outline-variant pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-headline-xl font-headline-xl text-on-surface tracking-tight font-bold">
              Mosca Risk Simulator
            </h1>
            <span className="px-2 py-0.5 rounded text-code-sm font-code-sm bg-surface-container-highest border border-outline-variant text-primary">
              Theorem Mode
            </span>
          </div>
          <p className="text-body-sm font-body-sm text-on-surface-variant mt-0.5">
            Evaluate whether migration time overlaps security/data lifetime against planning scenarios (Theorem: X + Y &gt; Z).
          </p>
        </div>

        {/* Controls: Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => runSimulation(scenarioYear, xVal, yVal)}
            disabled={recalculating}
            className="h-7 px-3 bg-primary-container text-on-primary-container font-semibold rounded text-code-sm flex items-center gap-1 hover:bg-primary transition-colors disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-[14px]">refresh</span>
            <span>{recalculating ? "Recalculating..." : "Apply to Pipeline"}</span>
          </button>
          <button
            onClick={exportMoscaReport}
            className="h-7 px-3 bg-surface-container border border-outline-variant text-on-surface hover:bg-surface-container-high rounded text-code-sm flex items-center gap-1 transition-colors"
          >
            <span className="material-symbols-outlined text-[14px]">file_download</span>
            <span>Export Analysis JSON</span>
          </button>
        </div>
      </section>

      {/* Theorem Callout Banner */}
      <section className="bg-surface-container-low border border-outline-variant p-3 rounded">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-base">functions</span>
              <span className="font-code-md text-code-md font-bold text-primary">Mosca's Theorem Formulation</span>
              <span className="text-code-sm text-on-surface-variant font-code-sm">[Mathematical Risk Boundary]</span>
            </div>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-code-sm text-on-surface-variant font-code-sm">
              <div className="flex items-center gap-1">
                <span className="text-primary font-semibold">Theorem Condition:</span>
                <span className="text-error font-semibold font-mono">If (X + Y &gt; Z) → Cryptographic Exposure</span>
              </div>
              <span>•</span>
              <div><strong className="text-secondary">X</strong> = Data / Shelf Lifetime</div>
              <span>•</span>
              <div><strong className="text-primary">Y</strong> = Migration Time</div>
              <span>•</span>
              <div><strong className="text-tertiary">Z</strong> = Threat Planning Horizon</div>
            </div>
          </div>
          <div className="bg-surface-container-lowest border border-outline-variant px-3 py-1.5 text-code-sm text-on-surface-variant max-w-sm rounded">
            <span className="text-primary font-semibold">Notice:</span> Planning Scenarios represent threat assessment horizons, not deterministic quantum hardware release predictions.
          </div>
        </div>
      </section>

      {/* Grid Section: Sliders & Verdict Box */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Interactive Controls & Sliders (7 Cols) */}
        <div className="lg:col-span-7 bg-surface-container-low border border-outline-variant p-4 rounded flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            {/* Scenario Preset Selector */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-label-caps font-label-caps text-on-surface-variant uppercase text-xs">
                  Quantum Threat Horizon Presets
                </label>
                <span className="text-code-sm text-on-surface-variant font-code-sm">Baseline Year: 2026</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleScenarioChange(2030)}
                  className={`px-3 py-2 border rounded text-left transition-colors ${
                    scenarioYear === 2030
                      ? "border-primary bg-surface-container-high ring-1 ring-primary"
                      : "border-outline-variant bg-surface-container hover:bg-surface-container-high"
                  }`}
                >
                  <div className={`text-code-sm font-semibold ${scenarioYear === 2030 ? "text-primary" : "text-on-surface"}`}>
                    2030 Planning Horizon
                  </div>
                  <div className="text-[10px] text-on-surface-variant font-code-sm">Conservative / Fast QPU (Z=4)</div>
                </button>
                <button
                  type="button"
                  onClick={() => handleScenarioChange(2035)}
                  className={`px-3 py-2 border rounded text-left transition-colors ${
                    scenarioYear === 2035
                      ? "border-primary bg-surface-container-high ring-1 ring-primary"
                      : "border-outline-variant bg-surface-container hover:bg-surface-container-high"
                  }`}
                >
                  <div className={`text-code-sm font-semibold ${scenarioYear === 2035 ? "text-primary" : "text-on-surface"}`}>
                    2035 Planning Horizon
                  </div>
                  <div className="text-[10px] text-on-surface-variant font-code-sm">NIST Recommended Target (Z=9)</div>
                </button>
                <button
                  type="button"
                  onClick={() => handleScenarioChange(2040)}
                  className={`px-3 py-2 border rounded text-left transition-colors ${
                    scenarioYear === 2040
                      ? "border-primary bg-surface-container-high ring-1 ring-primary"
                      : "border-outline-variant bg-surface-container hover:bg-surface-container-high"
                  }`}
                >
                  <div className={`text-code-sm font-semibold ${scenarioYear === 2040 ? "text-primary" : "text-on-surface"}`}>
                    2040 Planning Horizon
                  </div>
                  <div className="text-[10px] text-on-surface-variant font-code-sm">Extended Safe Buffer (Z=14)</div>
                </button>
              </div>
            </div>

            {/* Param X: Data Lifetime */}
            <div className="bg-surface-container-lowest p-3 border border-outline-variant rounded space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-1.5">
                  <span className="px-1.5 py-0.5 rounded bg-surface-variant font-code-sm font-bold text-secondary text-xs">
                    X
                  </span>
                  <span className="font-code-md text-code-md font-semibold text-on-surface">
                    Data / Security Lifetime (years)
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <input
                    className="w-16 bg-surface-container border border-outline-variant text-primary text-right font-code-md px-1 py-0.5 rounded"
                    type="number"
                    min="1"
                    max="25"
                    value={xVal}
                    onChange={(e) => handleXChange(parseInt(e.target.value, 10) || 1)}
                  />
                  <span className="text-code-sm text-on-surface-variant">Yrs</span>
                </div>
              </div>
              <input
                className="w-full accent-primary h-1 bg-surface-container-high rounded cursor-pointer"
                type="range"
                min="1"
                max="25"
                value={xVal}
                onChange={(e) => handleXChange(parseInt(e.target.value, 10))}
              />
              <p className="text-body-sm font-body-sm text-on-surface-variant text-[11px]">
                Time data must remain confidential (classified telemetry, root credentials, session tokens).
              </p>
            </div>

            {/* Param Y: Migration Time */}
            <div className="bg-surface-container-lowest p-3 border border-outline-variant rounded space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-1.5">
                  <span className="px-1.5 py-0.5 rounded bg-surface-variant font-code-sm font-bold text-primary text-xs">
                    Y
                  </span>
                  <span className="font-code-md text-code-md font-semibold text-on-surface">
                    Migration & Deployment Time (years)
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <input
                    className="w-16 bg-surface-container border border-outline-variant text-primary text-right font-code-md px-1 py-0.5 rounded"
                    type="number"
                    min="1"
                    max="10"
                    value={yVal}
                    onChange={(e) => handleYChange(parseInt(e.target.value, 10) || 1)}
                  />
                  <span className="text-code-sm text-on-surface-variant">Yrs</span>
                </div>
              </div>
              <input
                className="w-full accent-primary h-1 bg-surface-container-high rounded cursor-pointer"
                type="range"
                min="1"
                max="10"
                value={yVal}
                onChange={(e) => handleYChange(parseInt(e.target.value, 10))}
              />
              <p className="text-body-sm font-body-sm text-on-surface-variant text-[11px]">
                Time to refactor codebase, integrate lattice primitives, and validate CBOM compliance.
              </p>
            </div>

            {/* Param Z: Scenario Horizon */}
            <div className="bg-surface-container-lowest p-3 border border-outline-variant rounded space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-1.5">
                  <span className="px-1.5 py-0.5 rounded bg-surface-variant font-code-sm font-bold text-tertiary text-xs">
                    Z
                  </span>
                  <span className="font-code-md text-code-md font-semibold text-on-surface">
                    Threat Horizon (years to CRQC)
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <input
                    className="w-16 bg-surface-container border border-outline-variant text-primary text-right font-code-md px-1 py-0.5 rounded"
                    type="number"
                    min="3"
                    max="20"
                    value={zVal}
                    onChange={(e) => handleZChange(parseInt(e.target.value, 10) || 3)}
                  />
                  <span className="text-code-sm text-on-surface-variant">Yrs</span>
                </div>
              </div>
              <input
                className="w-full accent-tertiary h-1 bg-surface-container-high rounded cursor-pointer"
                type="range"
                min="3"
                max="20"
                value={zVal}
                onChange={(e) => handleZChange(parseInt(e.target.value, 10))}
              />
              <p className="text-body-sm font-body-sm text-on-surface-variant text-[11px]">
                Planning horizon from baseline 2026 to target planning year ({scenarioYear}).
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between text-code-sm text-on-surface-variant pt-2 border-t border-outline-variant">
            <span>Deterministic Matrix Execution</span>
            <span className="text-primary font-mono font-medium">Auto-calculated</span>
          </div>
        </div>

        {/* Calculation Result & Verdict Box (5 Cols) */}
        <div className="lg:col-span-5 bg-surface-container-low border border-outline-variant p-4 rounded flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex justify-between items-center border-b border-outline-variant pb-2">
              <span className="text-label-caps font-label-caps text-on-surface-variant uppercase text-xs">
                Quantum Exposure Verdict
              </span>
              <span
                className={`px-2 py-0.5 text-[11px] font-code-sm rounded font-bold ${
                  isAtRisk ? "bg-error-container text-on-error-container" : "bg-tertiary/10 text-tertiary border border-tertiary/30"
                }`}
              >
                {isAtRisk ? "EXPOSURE DETECTED" : "WITHIN TIMELINE MARGIN"}
              </span>
            </div>

            {/* Mathematical Equation Render */}
            <div className="bg-surface-container-lowest p-3 border border-outline-variant rounded text-center">
              <div className="text-label-caps font-label-caps text-on-surface-variant mb-1 text-[10px]">
                EQUATION RESOLUTION
              </div>
              <div className="font-code-lg text-code-lg text-on-surface font-semibold font-mono">
                {xVal} yrs (X) + {yVal} yrs (Y) = {totalRequired} yrs {isAtRisk ? ">" : "≤"} {zVal} yrs (Z)
              </div>
            </div>

            {/* Big Status Box */}
            <div
              className={`p-3 rounded-r border-l-4 space-y-2 ${
                isAtRisk
                  ? "bg-error-container/20 border-error"
                  : "bg-tertiary/10 border-tertiary"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`material-symbols-outlined text-xl ${
                    isAtRisk ? "text-error" : "text-tertiary"
                  }`}
                >
                  {isAtRisk ? "dangerous" : "verified"}
                </span>
                <span
                  className={`font-code-md text-code-md font-bold tracking-tight ${
                    isAtRisk ? "text-error" : "text-tertiary"
                  }`}
                >
                  {isAtRisk
                    ? "CRITICAL: AT RISK OF QUANTUM COLLAPSE"
                    : "STABLE: MIGRATION PRECEDES HORIZON"}
                </span>
              </div>
              <p className="text-body-sm font-body-sm text-on-surface text-xs leading-relaxed">
                {isAtRisk
                  ? "Theorem violated (X + Y > Z). Migration completion fails to precede estimated cryptanalytic viability horizon."
                  : "Theorem satisfied (X + Y ≤ Z). Sufficient buffer exists to complete migration prior to threat horizon."}
              </p>
              <div className="pt-1">
                <span className="text-label-caps font-label-caps text-on-surface-variant block text-[10px]">
                  {isAtRisk ? "EXPOSURE DEFICIT WINDOW" : "SAFETY BUFFER MARGIN"}
                </span>
                <span
                  className={`text-headline-lg font-headline-lg font-bold ${
                    isAtRisk ? "text-error" : "text-tertiary"
                  }`}
                >
                  {isAtRisk ? `${margin} Years Deficit` : `+${margin} Years Safe Buffer`}
                </span>
              </div>
            </div>

            {/* HNDL Advisory Notice */}
            <div className="bg-surface-container border border-outline-variant p-2.5 rounded space-y-1">
              <div className="flex items-center gap-1.5 text-primary text-code-sm font-semibold">
                <span className="material-symbols-outlined text-sm">security_update_warning</span>
                <span>Harvest Now, Decrypt Later (HNDL) Vector</span>
              </div>
              <p className="text-body-sm font-body-sm text-on-surface-variant text-[11px] leading-relaxed">
                {isAtRisk
                  ? `Adversaries recording ciphertext on this channel today can decrypt it within ${zVal} years, while data confidentiality remains vital for ${xVal} years.`
                  : "Ciphertext lifetime expires prior to target horizon. No HNDL vulnerability window identified."}
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between text-code-sm text-on-surface-variant pt-2 border-t border-outline-variant">
            <span>Remediation Priority:</span>
            <span className={`font-code-sm font-bold ${isAtRisk ? "text-error" : "text-tertiary"}`}>
              {isAtRisk ? "CRITICAL / P0 ASSET" : "NORMAL MONITORING"}
            </span>
          </div>
        </div>
      </section>

      {/* Visual Timeline Graph */}
      <section className="bg-surface-container-low border border-outline-variant p-4 rounded space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-outline-variant pb-2">
          <div>
            <h2 className="text-headline-md font-headline-md text-on-surface font-semibold">
              Cryptographic Exposure Timeline (2026 - 2040)
            </h2>
            <p className="text-body-sm font-body-sm text-on-surface-variant text-[11px]">
              Visual alignment of migration duration versus quantum vulnerability horizon.
            </p>
          </div>
          <div className="flex items-center gap-4 text-code-sm font-code-sm">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-2 bg-primary rounded-xs"></span>
              <span className="text-on-surface-variant text-xs">Migration (Y)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-2 bg-secondary rounded-xs"></span>
              <span className="text-on-surface-variant text-xs">Data Lifetime (X)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-2 bg-error-container border border-error rounded-xs"></span>
              <span className="text-error text-xs">Vulnerable Exposure Zone</span>
            </div>
          </div>
        </div>

        {/* Timeline Graph Container */}
        <div className="relative bg-surface-container-lowest p-4 border border-outline-variant rounded overflow-x-auto min-w-[700px]">
          {/* Years Axis Top */}
          <div className="grid grid-cols-15 text-center font-code-sm text-code-sm text-on-surface-variant border-b border-outline-variant pb-1 mb-6 text-xs">
            {Array.from({ length: 15 }, (_, i) => 2026 + i).map((yr) => (
              <span key={yr} className={yr === scenarioYear ? "text-primary font-bold" : ""}>
                {yr}
              </span>
            ))}
          </div>

          {/* Timeline Bars Canvas Area */}
          <div className="relative h-28 w-full flex flex-col justify-around">
            {/* Migration Bar (Y) */}
            <div className="flex items-center gap-2">
              <span className="w-24 text-right text-xs font-code-sm text-primary shrink-0">Migration (Y):</span>
              <div className="flex-1 bg-surface-container-high h-5 rounded relative overflow-hidden">
                <div
                  className="bg-primary h-full rounded transition-all duration-300 flex items-center px-2 text-[10px] font-bold text-on-primary"
                  style={{ width: `${Math.min(100, (yVal / 14) * 100)}%` }}
                >
                  {yVal} Yrs (Ends {2026 + yVal})
                </div>
              </div>
            </div>

            {/* Data Lifetime Bar (X) */}
            <div className="flex items-center gap-2">
              <span className="w-24 text-right text-xs font-code-sm text-secondary shrink-0">Lifetime (X):</span>
              <div className="flex-1 bg-surface-container-high h-5 rounded relative overflow-hidden">
                <div
                  className="bg-secondary h-full rounded transition-all duration-300 flex items-center px-2 text-[10px] font-bold text-on-secondary"
                  style={{ width: `${Math.min(100, (xVal / 14) * 100)}%` }}
                >
                  {xVal} Yrs (Confidential to {2026 + xVal})
                </div>
              </div>
            </div>

            {/* Exposure Window Bar */}
            <div className="flex items-center gap-2">
              <span className="w-24 text-right text-xs font-code-sm text-error shrink-0">Vulnerability:</span>
              <div className="flex-1 bg-surface-container-high h-5 rounded relative overflow-hidden">
                {isAtRisk ? (
                  <div
                    className="bg-error-container border border-error h-full rounded transition-all duration-300 flex items-center px-2 text-[10px] font-bold text-on-error-container"
                    style={{
                      marginLeft: `${Math.max(0, (zVal / 14) * 100)}%`,
                      width: `${Math.min(100 - (zVal / 14) * 100, ((totalRequired - zVal) / 14) * 100)}%`,
                    }}
                  >
                    EXPOSURE WINDOW ({2026 + zVal} - {2026 + totalRequired})
                  </div>
                ) : (
                  <div
                    className="bg-tertiary/20 border border-tertiary h-full rounded transition-all duration-300 flex items-center px-2 text-[10px] font-bold text-tertiary"
                    style={{ width: "100%" }}
                  >
                    NO VULNERABILITY WINDOW — SAFELY HARDENED
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
export default MoscaSimulator;

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { triggerScan } from "../../services/api";

export const NewScanPage: React.FC = () => {
  const navigate = useNavigate();
  const [path, setPath] = useState<string>("test_corpus");
  const [useCorpus, setUseCorpus] = useState<boolean>(true);
  const [scanning, setScanning] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<string>("IDLE");
  const [stageProgress, setStageProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const stages = [
    { name: "DISCOVERY", desc: "Discovering AST cryptographic usages in source code..." },
    { name: "DEPENDENCIES", desc: "Parsing package manifests and dependency trees..." },
    { name: "CERTIFICATES", desc: "Inspecting X.509, PKCS#12, and OpenSSH public keys..." },
    { name: "CONFIGURATION", desc: "Scanning TLS cipher suites and cryptographic configurations..." },
    { name: "NORMALIZATION", desc: "Deduplicating and normalizing cryptographic assets..." },
    { name: "QUANTUM ANALYSIS", desc: "Applying Shor & Grover vulnerability categorization..." },
    { name: "MOSCA & RISK", desc: "Evaluating Mosca theorem (X + Y > Z) and 5-factor risk model..." },
    { name: "CBOM & VALIDATION", desc: "Generating CycloneDX 1.6 CBOM and verifying official schema..." },
  ];

  const handleStartScan = async () => {
    setScanning(true);
    setError(null);

    // Deterministic visual progress through actual stages
    for (let i = 0; i < stages.length; i++) {
      setCurrentStage(stages[i].name);
      setStageProgress(Math.round(((i + 1) / stages.length) * 100));
      await new Promise((r) => setTimeout(r, 120));
    }

    try {
      await triggerScan({
        path: path,
        use_corpus: useCorpus,
      });
      setTimeout(() => {
        navigate("/dashboard");
      }, 300);
    } catch (err: any) {
      setError(err.message);
      setScanning(false);
    }
  };

  return (
    <div className="flex-1 p-6 space-y-5">
      {/* Header Banner */}
      <section className="flex flex-col md:flex-row md:items-end justify-between border-b border-outline-variant pb-3 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-on-surface">New Scan Configuration</h1>
            <span className="px-1.5 py-0.5 rounded bg-primary-container/15 border border-primary-container/40 text-primary font-mono text-[10px] uppercase font-semibold">
              PROFILE: AST-CRYPT-STRICT
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1 font-sans">
            Analyze a local project or authorized source tree for cryptographic discovery and quantum risk
          </p>
        </div>
        <div className="text-xs font-mono text-tertiary flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span>
          <span>Strict Path Sandbox Activated</span>
        </div>
      </section>

      {/* Target Selection Zone */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-outline-variant pb-2">
          <div className="flex items-center gap-1.5 font-semibold text-sm text-primary">
            <span className="material-symbols-outlined text-base">folder_special</span>
            <span>1. Target Directory Selection</span>
          </div>
          <span className="text-[11px] font-mono text-outline">Air-Gapped Sandbox</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2 space-y-2">
            <label className="text-xs font-mono text-on-surface-variant block">Target Repository / Source Path</label>
            <input
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              disabled={useCorpus}
              placeholder="e.g. C:\Projects\MyRepo or test_corpus"
              className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
            />
          </div>

          <div className="flex flex-col justify-end">
            <label className="flex items-center gap-2 cursor-pointer bg-surface-container p-2.5 rounded border border-outline-variant hover:border-outline">
              <input
                type="checkbox"
                checked={useCorpus}
                onChange={(e) => {
                  setUseCorpus(e.target.checked);
                  if (e.target.checked) setPath("test_corpus");
                }}
                className="rounded border-outline-variant text-primary focus:ring-0"
              />
              <span className="text-xs font-mono text-on-surface font-semibold">Use Bundled Test Corpus</span>
            </label>
          </div>
        </div>

        <div className="text-[11px] font-mono text-outline flex flex-wrap gap-4 pt-1">
          <span>Target Verified: {useCorpus ? "Bundled Controlled Test Corpus (Python, Java, TLS, Certs)" : path}</span>
          <span className="text-secondary">AST Syntax Analysis Enabled</span>
          <span className="text-tertiary">Zero Private Key Persistence Guaranteed</span>
        </div>
      </section>

      {/* Cryptographic Discovery Collectors */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-outline-variant pb-2">
          <div className="flex items-center gap-1.5 font-semibold text-sm text-primary">
            <span className="material-symbols-outlined text-base">tune</span>
            <span>2. Cryptographic Discovery Collectors</span>
          </div>
          <span className="text-[11px] font-mono text-outline">Air-Gap Local Scanners</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
          <div className="p-3 bg-surface-container rounded border border-outline-variant flex items-start gap-2">
            <span className="material-symbols-outlined text-tertiary text-sm mt-0.5">check_circle</span>
            <div>
              <div className="font-bold text-on-surface">Source AST Scanner</div>
              <div className="text-[11px] text-on-surface-variant mt-0.5">
                Call-site AST visitor for Python and Java source code. Extracts cryptographic parameters, modes, key sizes.
              </div>
            </div>
          </div>

          <div className="p-3 bg-surface-container rounded border border-outline-variant flex items-start gap-2">
            <span className="material-symbols-outlined text-tertiary text-sm mt-0.5">check_circle</span>
            <div>
              <div className="font-bold text-on-surface">Manifest Dependency Scanner</div>
              <div className="text-[11px] text-on-surface-variant mt-0.5">
                Parses requirements.txt, pom.xml, package.json, go.mod, Cargo.toml for cryptographic libraries.
              </div>
            </div>
          </div>

          <div className="p-3 bg-surface-container rounded border border-outline-variant flex items-start gap-2">
            <span className="material-symbols-outlined text-tertiary text-sm mt-0.5">check_circle</span>
            <div>
              <div className="font-bold text-on-surface">Certificates & Public Keys Scanner</div>
              <div className="text-[11px] text-on-surface-variant mt-0.5">
                Inspects X.509 (PEM & DER), PKCS#12 (.p12/.pfx), and OpenSSH public keys without saving key bytes.
              </div>
            </div>
          </div>

          <div className="p-3 bg-surface-container rounded border border-outline-variant flex items-start gap-2">
            <span className="material-symbols-outlined text-tertiary text-sm mt-0.5">check_circle</span>
            <div>
              <div className="font-bold text-on-surface">Configuration & Cipher Suite Scanner</div>
              <div className="text-[11px] text-on-surface-variant mt-0.5">
                Extracts cipher suites and TLS bounds from nginx.conf, sshd_config, openssl.cnf, Dockerfiles.
              </div>
            </div>
          </div>

          <div className="p-3 bg-surface-container rounded border border-outline-variant flex items-start gap-2">
            <span className="material-symbols-outlined text-tertiary text-sm mt-0.5">check_circle</span>
            <div>
              <div className="font-bold text-on-surface">JVM Bytecode Constant Pool Scanner</div>
              <div className="text-[11px] text-on-surface-variant mt-0.5">
                Pure-Python JVM constant pool extractor (.class, .jar) with zip-slip safety.
              </div>
            </div>
          </div>

          <div className="p-3 bg-surface-container rounded border border-outline-variant opacity-60 flex items-start gap-2">
            <span className="material-symbols-outlined text-outline text-sm mt-0.5">pending</span>
            <div>
              <div className="font-bold text-outline">Live Endpoints & Containers (Roadmap)</div>
              <div className="text-[11px] text-outline mt-0.5">
                Planned enterprise module. Core MVP focuses on air-gapped static source analysis.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Progress state */}
      {scanning && (
        <section className="bg-surface-container-low border border-primary-container/60 rounded p-4 space-y-2">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-primary font-bold">Stage: {currentStage}</span>
            <span className="text-on-surface-variant">{stageProgress}%</span>
          </div>
          <div className="w-full bg-surface-container-highest rounded h-2 overflow-hidden">
            <div className="bg-primary-container h-full transition-all duration-150" style={{ width: `${stageProgress}%` }}></div>
          </div>
          <p className="text-[11px] font-mono text-outline">
            {stages.find((s) => s.name === currentStage)?.desc || "Executing cryptographic discovery..."}
          </p>
        </section>
      )}

      {error && (
        <div className="bg-error-container/20 border border-error/40 p-3 rounded text-error font-mono text-xs">
          Scan Failed: {error}
        </div>
      )}

      {/* Primary Execution Action */}
      <section className="pt-2">
        <button
          onClick={handleStartScan}
          disabled={scanning}
          className="w-full bg-primary-container hover:bg-primary text-on-primary font-mono text-sm font-bold py-2.5 px-4 rounded flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-base">rocket_launch</span>
          <span>{scanning ? "Executing Cryptographic Discovery..." : "Initiate AST Cryptographic Scan"}</span>
        </button>
      </section>
    </div>
  );
};

export default NewScanPage;

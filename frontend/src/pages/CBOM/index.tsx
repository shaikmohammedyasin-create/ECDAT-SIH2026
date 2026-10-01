import React, { useEffect, useState } from "react";
import { fetchCBOM, getCBOMDownloadUrl } from "../../services/api";
import type { CBOMData } from "../../types";

export const CBOMPage: React.FC = () => {
  const [cbomData, setCbomData] = useState<CBOMData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("ALL");
  const [copied, setCopied] = useState(false);
  const [validating, setValidating] = useState(false);
  const [mobileTab, setMobileTab] = useState<"tree" | "raw">("tree");

  useEffect(() => {
    loadCBOM();
  }, []);

  const loadCBOM = () => {
    setLoading(true);
    fetchCBOM()
      .then((data) => {
        setCbomData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load CBOM:", err);
        setLoading(false);
      });
  };

  const revalidateSchema = () => {
    setValidating(true);
    fetchCBOM()
      .then((data) => {
        setCbomData(data);
        setValidating(false);
      })
      .catch((err) => {
        console.error("Validation error:", err);
        setValidating(false);
      });
  };

  const copyRawJson = () => {
    if (cbomData?.cbom) {
      navigator.clipboard.writeText(JSON.stringify(cbomData.cbom, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="font-code-sm text-on-surface-variant text-sm">Validating CycloneDX 1.6 CBOM schema...</span>
        </div>
      </div>
    );
  }

  const rawJson = cbomData?.cbom ? JSON.stringify(cbomData.cbom, null, 2) : "{}";
  const isValid = cbomData?.validation?.valid ?? false;
  const errors = cbomData?.validation?.errors || [];
  const components: any[] = cbomData?.cbom?.components || [];

  const filteredComponents = components.filter((comp) => {
    if (filterType === "ALL") return true;
    if (filterType === "ALGORITHMS") return comp.type === "crypto-asset";
    if (filterType === "CERTS") return comp.name?.includes("Certificate") || comp.type === "certificate";
    return true;
  });

  return (
    <div className="flex-1 flex flex-col bg-surface overflow-hidden">
      {/* Top Header */}
      <div className="px-3 sm:px-4 py-2 border-b border-outline-variant bg-surface-container-low shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-base sm:text-lg font-headline-md text-on-surface tracking-tight font-bold">
              CycloneDX v1.6 Cryptographic Bill of Materials (CBOM)
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-container-highest border border-outline-variant text-primary">
              SPEC 1.6 DRAFT
            </span>
          </div>
          <p className="text-body-sm font-body-sm text-on-surface-variant mt-0.5 text-xs">
            NIST SP 800-56C & CycloneDX 1.6 formal cryptographic schema verification and component tree.
          </p>
        </div>

        <div className="flex items-center gap-2 text-code-sm">
          <div className="text-right">
            <span className="text-[10px] text-outline block">TARGET ASSETS</span>
            <span className="text-primary font-mono font-semibold">{components.length} Components</span>
          </div>
        </div>
      </div>

      {/* Formal Validation Status Banner */}
      <div className="px-4 py-2 border-b border-outline-variant bg-surface-container-lowest shrink-0">
        <div className="bg-surface-container border border-outline-variant p-2.5 rounded flex flex-col xl:flex-row xl:items-center justify-between gap-3">
          <div className="flex items-start sm:items-center gap-3">
            <div
              className={`w-8 h-8 rounded bg-surface-container-high border flex items-center justify-center shrink-0 ${
                isValid ? "border-tertiary text-tertiary" : "border-error text-error"
              }`}
            >
              <span className="material-symbols-outlined text-lg">
                {isValid ? "verified_user" : "error"}
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span
                  className={`font-code-md text-xs font-bold uppercase tracking-wide ${
                    isValid ? "text-tertiary" : "text-error"
                  }`}
                >
                  CBOM SCHEMA STATUS: {isValid ? "VALID" : "INVALID"}
                </span>
                <span className="text-outline text-xs">•</span>
                <span className="font-code-sm text-on-surface text-xs">
                  {isValid
                    ? "CycloneDX v1.6 JSON Schema Specification Compliant"
                    : "Validation errors detected in cryptographic component schema"}
                </span>
              </div>
              <div className="flex items-center gap-3 text-code-sm text-on-surface-variant mt-0.5 flex-wrap text-xs">
                <span className={`flex items-center gap-1 ${isValid ? "text-tertiary" : "text-error"}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${isValid ? "bg-tertiary" : "bg-error"}`}></span>
                  {errors.length} Validation Errors
                </span>
                <span className="text-outline">|</span>
                <span className="text-outline font-mono text-[11px]">
                  Spec: CycloneDX 1.6
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={revalidateSchema}
              disabled={validating}
              className="bg-surface-container-high hover:bg-surface-variant text-on-surface border border-outline-variant text-code-sm px-2.5 py-1 rounded flex items-center gap-1 transition-colors text-xs"
            >
              <span className="material-symbols-outlined text-sm">refresh</span>
              <span>{validating ? "Validating..." : "Re-Validate Schema"}</span>
            </button>
            <a
              href={getCBOMDownloadUrl()}
              download="cbom_cyclonedx_1.6.json"
              className="bg-primary-container text-on-primary-container hover:bg-primary font-semibold text-code-sm px-3 py-1 rounded flex items-center gap-1 transition-colors text-xs"
            >
              <span className="material-symbols-outlined text-sm">download</span>
              <span>Export CBOM JSON</span>
            </a>
            <button
              onClick={copyRawJson}
              className="bg-surface-container-lowest hover:bg-surface-container-high text-primary border border-primary/40 text-code-sm px-2.5 py-1 rounded flex items-center gap-1 transition-colors text-xs"
              title="Copy Raw CBOM to Clipboard"
            >
              <span className="material-symbols-outlined text-sm">
                {copied ? "check" : "content_copy"}
              </span>
              <span>{copied ? "Copied" : "Copy Raw JSON"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Tab Switcher */}
      <div className="lg:hidden flex border-b border-outline-variant bg-surface-container-low shrink-0 text-xs font-mono">
        <button
          type="button"
          onClick={() => setMobileTab("tree")}
          className={`flex-1 py-2 text-center border-b-2 font-semibold flex items-center justify-center gap-1.5 transition-colors ${
            mobileTab === "tree"
              ? "border-primary text-primary bg-surface-container"
              : "border-transparent text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <span className="material-symbols-outlined text-sm">account_tree</span>
          <span>Assets Tree ({filteredComponents.length})</span>
        </button>
        <button
          type="button"
          onClick={() => setMobileTab("raw")}
          className={`flex-1 py-2 text-center border-b-2 font-semibold flex items-center justify-center gap-1.5 transition-colors ${
            mobileTab === "raw"
              ? "border-primary text-primary bg-surface-container"
              : "border-transparent text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <span className="material-symbols-outlined text-sm">data_object</span>
          <span>Raw JSON Spec</span>
        </button>
      </div>

      {/* Split Workbench Canvases (45% Left / 55% Right on lg, Tabbed on mobile) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Cryptographic Components Tree */}
        <section
          className={`
            w-full lg:w-[45%] border-r border-outline-variant flex-col bg-surface-container-lowest overflow-hidden
            ${mobileTab === "tree" ? "flex" : "hidden lg:flex"}
          `}
        >
          <div className="h-9 px-3 border-b border-outline-variant bg-surface-container-low flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-sm">account_tree</span>
              <span className="font-code-md font-semibold text-on-surface uppercase tracking-wider text-xs">
                Discovered Cryptographic Assets
              </span>
              <span className="px-1.5 py-0.2 bg-surface-container font-mono text-[10px] text-outline border border-outline-variant">
                {filteredComponents.length} items
              </span>
            </div>
            {/* View / Filter Toggles */}
            <div className="flex items-center gap-1 text-code-sm text-outline">
              <button
                onClick={() => setFilterType("ALL")}
                className={`px-1.5 py-0.5 rounded text-[10px] ${
                  filterType === "ALL" ? "bg-surface-container text-primary border border-outline-variant font-bold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilterType("ALGORITHMS")}
                className={`px-1.5 py-0.5 rounded text-[10px] ${
                  filterType === "ALGORITHMS" ? "bg-surface-container text-primary border border-outline-variant font-bold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Algorithms
              </button>
            </div>
          </div>

          {/* Components List */}
          <div className="flex-1 overflow-y-auto divide-y divide-outline-variant/60 font-code-sm">
            {filteredComponents.map((comp, idx) => {
              const cryptoProps = comp.cryptoProperties || {};
              const algo = comp.name || "Unknown";
              const isPqc = algo.includes("ML-KEM") || algo.includes("Kyber") || algo.includes("Dilithium");
              const isWeak = algo.includes("RSA") || algo.includes("MD5") || algo.includes("SHA1") || algo.includes("3DES");

              return (
                <div
                  key={idx}
                  className="p-3 hover:bg-surface-container/60 cursor-pointer transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary text-sm">key</span>
                      <span className="text-on-surface font-semibold text-xs font-mono">{comp.name}</span>
                      <span
                        className={`px-1.5 py-0.2 text-[9px] rounded font-mono ${
                          isPqc
                            ? "bg-tertiary/10 text-tertiary border border-tertiary/30"
                            : isWeak
                            ? "bg-error-container/30 text-error border border-error/30"
                            : "bg-surface-container-high text-primary border border-outline-variant"
                        }`}
                      >
                        {isPqc ? "PQC-COMPLIANT" : isWeak ? "PQC-VULNERABLE" : "CRYPTO-ASSET"}
                      </span>
                    </div>
                    <span className="text-[10px] text-outline font-mono">
                      {comp["bom-ref"] || `ecdat-ref-${idx}`}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-x-3 gap-y-1 mt-2 text-[11px] text-on-surface-variant">
                    <div>
                      <span className="text-outline">Primitive: </span>
                      <span className="text-on-surface font-mono">{cryptoProps.assetType || comp.type}</span>
                    </div>
                    <div>
                      <span className="text-outline">Algorithm: </span>
                      <span className="text-primary font-mono">{cryptoProps.algorithmRef?.name || comp.name}</span>
                    </div>
                    <div>
                      <span className="text-outline">Security Level: </span>
                      <span className="text-on-surface font-mono">{cryptoProps.classicalSecurityLevel || "N/A"}</span>
                    </div>
                    <div>
                      <span className="text-outline">NIST Level: </span>
                      <span className="text-on-surface font-mono">{cryptoProps.nistQuantumSecurityLevel || "0"}</span>
                    </div>
                  </div>

                  <div className="mt-2 pt-1.5 border-t border-outline-variant/40 flex items-center justify-between text-[10px] text-outline">
                    <span>Type: <strong className="text-on-surface">{comp.type}</strong></span>
                    <span className="text-tertiary font-mono">CycloneDX 1.6</span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Right Pane: Live CycloneDX Raw JSON View */}
        <section
          className={`
            w-full lg:w-[55%] flex-col bg-[#090f15] overflow-hidden
            ${mobileTab === "raw" ? "flex" : "hidden lg:flex"}
          `}
        >
          <div className="h-9 px-3 border-b border-outline-variant bg-[#111720] flex items-center justify-between shrink-0 select-none">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[14px] text-primary">data_object</span>
              <span className="font-code-md text-xs text-on-surface font-mono">cyclonedx-cbom-1.6.json</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-outline font-mono">
              <span>{rawJson.split("\n").length} Lines</span>
              <span className="text-outline">|</span>
              <span className="text-tertiary">Schema: Valid</span>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-3 font-mono text-[11px] leading-5 text-on-surface select-text bg-[#090f15]">
            <pre className="whitespace-pre overflow-x-auto text-primary-fixed">
              {rawJson}
            </pre>
          </div>
        </section>
      </div>
    </div>
  );
};
export default CBOMPage;

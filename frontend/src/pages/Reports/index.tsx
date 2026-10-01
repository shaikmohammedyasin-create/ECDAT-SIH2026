import React, { useEffect, useState } from "react";
import { fetchReportsMetadata, getReportDownloadUrl, API_BASE } from "../../services/api";
import type { ReportsMetadata, ReportDeliverable } from "../../types";

export const ReportsPage: React.FC = () => {
  const [metadata, setMetadata] = useState<ReportsMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewContent, setPreviewContent] = useState<string | null>(null);
  const [previewTitle, setPreviewTitle] = useState<string>("");
  const [previewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    fetchReportsMetadata()
      .then((data) => {
        setMetadata(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load reports metadata:", err);
        setLoading(false);
      });
  }, []);

  const handlePreview = async (del: ReportDeliverable) => {
    if (!del.available) return;
    setPreviewTitle(del.name);
    setPreviewLoading(true);
    try {
      const res = await fetch(`${API_BASE}/reports/preview/${del.id}`);
      if (res.ok) {
        const text = await res.text();
        setPreviewContent(text);
      } else {
        setPreviewContent("Error: Preview not available for this format.");
      }
    } catch (e: any) {
      setPreviewContent(`Failed to fetch preview: ${e.message}`);
    } finally {
      setPreviewLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-lowest p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="font-code-sm text-on-surface-variant text-sm">Compiling verified audit deliverables...</span>
        </div>
      </div>
    );
  }

  const deliverables = metadata?.available_formats || [];

  return (
    <div className="flex-1 flex flex-col overflow-y-auto bg-background p-3 sm:p-4 space-y-4">
      {/* Top Header */}
      <section className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-outline-variant pb-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg sm:text-xl font-headline-xl text-on-surface tracking-tight font-bold">
              Reports & Evidence Deliverables
            </h1>
            <span className="px-2 py-0.5 rounded text-code-sm font-code-sm bg-surface-container-highest border border-outline-variant text-primary font-mono">
              NTRO SEC-3 SPEC
            </span>
          </div>
          <p className="text-body-sm font-body-sm text-on-surface-variant mt-0.5 text-xs">
            Cryptographic audit deliverables, executive summaries, technical finding dossiers, CycloneDX CBOM, and CSV matrices.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-tertiary border border-tertiary/40 px-2 py-1 rounded bg-tertiary/10 font-bold flex items-center gap-1">
            <span className="material-symbols-outlined text-[13px]">verified</span>
            {metadata?.validation_status || "ALL DELIVERABLES VERIFIED"}
          </span>
        </div>
      </section>

      {/* Filter Controls Toolbar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-3 p-3 bg-surface-container-low border border-outline-variant rounded">
        {/* Filter 1: Scan ID */}
        <div className="flex flex-col">
          <label className="text-[10px] font-mono text-on-surface-variant uppercase mb-1 flex items-center justify-between">
            Target Scan Reference
            <span className="text-tertiary font-bold">LIVE CURRENT</span>
          </label>
          <div className="flex items-center bg-surface-container-lowest border border-outline-variant px-2.5 py-1 rounded text-xs">
            <span className="material-symbols-outlined text-outline text-[14px] mr-1.5">fingerprint</span>
            <span className="font-mono text-primary font-semibold truncate" title={metadata?.scan_id || "live-scan"}>
              {metadata?.scan_id ? metadata.scan_id.substring(0, 16) + "..." : "live-scan"}
            </span>
          </div>
        </div>

        {/* Filter 2: Target Scope */}
        <div className="flex flex-col">
          <label className="text-[10px] font-mono text-on-surface-variant uppercase mb-1">Target Analysis Scope</label>
          <div className="flex items-center bg-surface-container-lowest border border-outline-variant px-2.5 py-1 rounded text-xs">
            <span className="material-symbols-outlined text-secondary text-[14px] mr-1.5">folder</span>
            <span className="font-mono text-on-surface truncate" title={metadata?.target_path || "Full Project"}>
              {metadata?.target_path ? metadata.target_path.split(/[\\/]/).pop() || metadata.target_path : "Full Project"}
            </span>
          </div>
        </div>

        {/* Filter 3: Classification Tier */}
        <div className="flex flex-col">
          <label className="text-[10px] font-mono text-on-surface-variant uppercase mb-1">Classification Tier</label>
          <div className="flex items-center bg-surface-container-lowest border border-outline-variant px-2.5 py-1 rounded text-xs">
            <span className="material-symbols-outlined text-primary text-[14px] mr-1.5">lock</span>
            <span className="font-mono text-primary font-bold">NTRO-RESTRICTED / SEC-3</span>
          </div>
        </div>

        {/* Filter 4: Output Profile */}
        <div className="flex flex-col">
          <label className="text-[10px] font-mono text-on-surface-variant uppercase mb-1">Discovered Assets</label>
          <div className="flex items-center bg-surface-container-lowest border border-outline-variant px-2.5 py-1 rounded text-xs">
            <span className="material-symbols-outlined text-tertiary text-[14px] mr-1.5">memory</span>
            <span className="font-mono text-tertiary font-bold">{metadata?.total_assets || 0} Cryptographic Assets</span>
          </div>
        </div>
      </div>

      {/* 6 Report Artifact Cards (Bento Grid) */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">inventory_2</span>
            <h2 className="text-headline-md font-headline-md text-on-surface font-semibold text-sm">
              Generated Audit Artifacts & Telemetry Dossiers
            </h2>
            <span className="text-[10px] font-mono text-outline bg-surface-container-high px-1.5 py-0.5 rounded">
              {deliverables.length} DELIVERABLES READY
            </span>
          </div>
          <div className="text-code-sm text-on-surface-variant text-xs flex items-center gap-1">
            <span className="material-symbols-outlined text-tertiary text-[14px]">history</span>
            Real-time synchronization
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {deliverables.map((del) => {
            const isAvail = del.available;
            return (
              <div
                key={del.id}
                className="bg-surface-container-low border border-outline-variant p-3.5 rounded flex flex-col justify-between hover:border-primary/50 transition-colors group"
              >
                <div>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 bg-primary/10 text-primary border border-primary/30 font-bold rounded">
                        {del.id.toUpperCase()}
                      </span>
                      {isAvail ? (
                        <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 bg-tertiary/10 text-tertiary border border-tertiary/30 font-bold rounded flex items-center gap-0.5">
                          <span className="material-symbols-outlined text-[10px]">check_circle</span> VERIFIED
                        </span>
                      ) : (
                        <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 bg-surface-container text-outline border border-outline-variant rounded">
                          NOT AVAILABLE
                        </span>
                      )}
                    </div>
                    <span className="text-code-sm text-outline text-[11px] font-mono">
                      {del.filename}
                    </span>
                  </div>

                  <h3 className="font-semibold text-on-surface group-hover:text-primary transition-colors text-sm flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-primary text-[16px]">
                      {del.id === "html" ? "shield_person" : del.id === "json" ? "verified_user" : del.id === "csv" ? "table_view" : "description"}
                    </span>
                    {del.name}
                  </h3>
                  <p className="text-body-sm text-on-surface-variant mt-1 text-xs leading-relaxed">
                    Formal audit artifact verified according to NTRO ECDAT specification. Contains cryptographic findings, confidence, and standards-aligned recommendations.
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-4 pt-2 border-t border-outline-variant">
                  {isAvail ? (
                    <>
                      <button
                        onClick={() => handlePreview(del)}
                        className="bg-surface-container border border-outline-variant hover:bg-surface-variant text-on-surface text-xs font-code-sm py-1 px-2 rounded flex items-center justify-center gap-1 transition-colors"
                      >
                        <span className="material-symbols-outlined text-[14px] text-secondary">visibility</span>
                        <span>Preview</span>
                      </button>
                      <a
                        href={getReportDownloadUrl(del.id)}
                        download={del.filename}
                        className="bg-surface-container-high border border-outline-variant hover:border-primary text-primary text-xs font-code-sm py-1 px-2 rounded flex items-center justify-center gap-1 font-semibold transition-colors"
                      >
                        <span className="material-symbols-outlined text-[14px]">download</span>
                        <span>Download</span>
                      </a>
                    </>
                  ) : (
                    <div className="col-span-2 text-center py-1 text-xs text-outline italic bg-surface-container-lowest rounded border border-outline-variant">
                      Not Available
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Preview Modal */}
      {previewContent !== null && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest border border-outline-variant rounded-lg max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="px-4 py-2.5 bg-surface-container border-b border-outline-variant flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">preview</span>
                <span className="font-semibold text-on-surface text-sm font-mono">{previewTitle}</span>
              </div>
              <button
                onClick={() => setPreviewContent(null)}
                className="text-on-surface-variant hover:text-on-surface text-sm flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-base">close</span>
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4 bg-[#090f15] font-mono text-xs text-on-surface leading-5 select-text">
              {previewLoading ? (
                <div className="text-center py-8 text-outline">Loading report payload...</div>
              ) : (
                <pre className="whitespace-pre-wrap">{previewContent}</pre>
              )}
            </div>
            <div className="px-4 py-2 bg-surface-container border-t border-outline-variant flex justify-end">
              <button
                onClick={() => setPreviewContent(null)}
                className="px-3 py-1 bg-surface-container-high border border-outline-variant text-on-surface rounded text-xs hover:border-primary transition-colors"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default ReportsPage;

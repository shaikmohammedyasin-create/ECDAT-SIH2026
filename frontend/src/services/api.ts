import type {
  DashboardData,
  InventoryResponse,
  FindingDetail,
  MoscaState,
  RiskAnalysisData,
  MigrationResponse,
  CBOMData,
  ReportsMetadata,
  TerminalLog,
  SettingsData,
} from "../types";

// Dynamic API Base URL supporting:
// 1. Explicit cloud environment variable (VITE_API_BASE_URL)
// 2. Relative /api on cloud deployments (proxied via vercel.json or same domain)
// 3. Local Vite dev server fallback (http://localhost:8000/api)
export const API_BASE: string = (() => {
  const envUrl = (import.meta as any).env?.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === "string" && envUrl.trim().length > 0) {
    const clean = envUrl.trim().replace(/\/+$/, "");
    return clean.endsWith("/api") ? clean : `${clean}/api`;
  }
  if (typeof window !== "undefined") {
    // If running in local Vite dev server on port 5173 or 3000
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      if (window.location.port === "5173" || window.location.port === "3000") {
        return window.location.hostname === "127.0.0.1"
          ? "http://127.0.0.1:8000/api"
          : "http://localhost:8000/api";
      }
    }
    // If served from Vercel (proxied by vercel.json) or same origin
    return "/api";
  }
  return "https://ecdat-sih2026.onrender.com/api";
})();

export async function fetchDashboard(): Promise<DashboardData> {
  const res = await fetch(`${API_BASE}/dashboard`);
  if (!res.ok) throw new Error(`Dashboard API error: ${res.statusText}`);
  return res.json();
}

export async function resetScanState(): Promise<any> {
  const res = await fetch(`${API_BASE}/scans/reset`, { method: "POST" });
  if (!res.ok) throw new Error(`Reset API error: ${res.statusText}`);
  return res.json();
}

export async function triggerScan(data: {
  path: string;
  use_corpus?: boolean;
  scenario_year?: number;
  x_lifetime?: number;
  y_migration?: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/scans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail?.detail ?? `Scan API error: ${res.statusText}`);
  }
  return res.json();
}

export async function triggerUploadScan(
  file: File,
  opts?: { scenario_year?: number; x_lifetime?: number; y_migration?: number },
  onProgress?: (percent: number) => void
): Promise<any> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/scans/upload`);

    if (onProgress && xhr.upload) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress(percent);
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          resolve(xhr.responseText);
        }
      } else {
        try {
          const data = JSON.parse(xhr.responseText);
          reject(new Error(data.detail || `Upload scan error: ${xhr.statusText}`));
        } catch {
          reject(new Error(`Upload scan error: ${xhr.statusText}`));
        }
      }
    };

    xhr.onerror = () => reject(new Error("Network connection error during file upload. Check container backend."));

    const fd = new FormData();
    fd.append("file", file);
    fd.append("scenario_year", String(opts?.scenario_year ?? 2035));
    fd.append("x_lifetime", String(opts?.x_lifetime ?? 10.0));
    fd.append("y_migration", String(opts?.y_migration ?? 3.0));
    xhr.send(fd);
  });
}

export async function triggerPasteScan(
  code: string,
  filename: string,
  opts?: { scenario_year?: number; x_lifetime?: number; y_migration?: number }
): Promise<any> {
  const fd = new FormData();
  fd.append("code", code);
  fd.append("filename", filename);
  fd.append("scenario_year", String(opts?.scenario_year ?? 2035));
  fd.append("x_lifetime", String(opts?.x_lifetime ?? 10.0));
  fd.append("y_migration", String(opts?.y_migration ?? 3.0));
  const res = await fetch(`${API_BASE}/scans/paste`, { method: "POST", body: fd });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail?.detail ?? `Paste scan error: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchScanStatus(): Promise<any> {
  const res = await fetch(`${API_BASE}/scans/status`);
  if (!res.ok) throw new Error(`Scan status API error: ${res.statusText}`);
  return res.json();
}

export async function fetchInventory(
  params?: {
    search?: string;
    algorithm?: string;
    quantum_status?: string;
    threat?: string;
    risk_band?: string;
    page?: number;
    page_size?: number;
  },
  signal?: AbortSignal
): Promise<InventoryResponse> {
  const q = new URLSearchParams();
  if (params?.search) q.set("search", params.search);
  if (params?.algorithm && params.algorithm !== "All") q.set("algorithm", params.algorithm);
  if (params?.quantum_status && params.quantum_status !== "All") q.set("quantum_status", params.quantum_status);
  if (params?.threat && params.threat !== "All") q.set("threat", params.threat);
  if (params?.risk_band && params.risk_band !== "All") q.set("risk_band", params.risk_band);
  if (params?.page) q.set("page", params.page.toString());
  if (params?.page_size) q.set("page_size", params.page_size.toString());

  const res = await fetch(`${API_BASE}/inventory?${q.toString()}`, { signal });
  if (!res.ok) throw new Error(`Inventory API error: ${res.statusText}`);
  return res.json();
}

export async function fetchFindingDetail(id: number | string, signal?: AbortSignal): Promise<FindingDetail> {
  const res = await fetch(`${API_BASE}/findings/${id}`, { signal });
  if (!res.ok) throw new Error(`Finding detail error: ${res.statusText}`);
  return res.json();
}

export async function fetchMosca(): Promise<MoscaState> {
  const res = await fetch(`${API_BASE}/mosca`);
  if (!res.ok) throw new Error(`Mosca API error: ${res.statusText}`);
  return res.json();
}

export async function simulateMosca(payload: {
  scenario_year: number;
  x_lifetime: number;
  y_migration: number;
  recompute_scan?: boolean;
}): Promise<MoscaState> {
  const res = await fetch(`${API_BASE}/mosca/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Mosca simulate error: ${res.statusText}`);
  return res.json();
}

export async function fetchRiskAnalysis(): Promise<RiskAnalysisData> {
  const res = await fetch(`${API_BASE}/risk`);
  if (!res.ok) throw new Error(`Risk API error: ${res.statusText}`);
  return res.json();
}

export async function fetchMigration(): Promise<MigrationResponse> {
  const res = await fetch(`${API_BASE}/migration`);
  if (!res.ok) throw new Error(`Migration API error: ${res.statusText}`);
  return res.json();
}

export async function fetchCBOM(): Promise<CBOMData> {
  const res = await fetch(`${API_BASE}/cbom`);
  if (!res.ok) throw new Error(`CBOM API error: ${res.statusText}`);
  return res.json();
}

export async function fetchReportsMetadata(): Promise<ReportsMetadata> {
  const res = await fetch(`${API_BASE}/reports`);
  if (!res.ok) throw new Error(`Reports metadata API error: ${res.statusText}`);
  return res.json();
}

export function getReportDownloadUrl(fmt: string): string {
  return `${API_BASE}/reports/download/${fmt}`;
}

export function getCBOMDownloadUrl(): string {
  return `${API_BASE}/cbom/download`;
}

export async function fetchTerminalLogs(): Promise<TerminalLog[]> {
  const res = await fetch(`${API_BASE}/terminal`);
  if (!res.ok) throw new Error(`Terminal logs API error: ${res.statusText}`);
  return res.json();
}

export async function clearTerminalLogs(): Promise<void> {
  await fetch(`${API_BASE}/terminal`, { method: "DELETE" });
}

export async function fetchSettings(): Promise<SettingsData> {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error(`Settings API error: ${res.statusText}`);
  return res.json();
}

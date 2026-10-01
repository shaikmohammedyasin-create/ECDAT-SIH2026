import React, { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import JSZip from "jszip";
import { triggerScan, triggerUploadScan, triggerPasteScan } from "../../services/api";

type InputMode = "path" | "upload" | "url" | "paste";
type LangExt = "py" | "java" | "js" | "ts" | "c" | "cpp" | "go" | "rs" | "txt";

const LANG_EXTS: { label: string; ext: LangExt }[] = [
  { label: "Python (.py)", ext: "py" },
  { label: "Java (.java)", ext: "java" },
  { label: "JavaScript (.js)", ext: "js" },
  { label: "TypeScript (.ts)", ext: "ts" },
  { label: "C (.c)", ext: "c" },
  { label: "C++ (.cpp)", ext: "cpp" },
  { label: "Go (.go)", ext: "go" },
  { label: "Rust (.rs)", ext: "rs" },
  { label: "Plain text (.txt)", ext: "txt" },
];

const STAGES = [
  { name: "DISCOVERY", desc: "Discovering AST cryptographic usages in source code..." },
  { name: "DEPENDENCIES", desc: "Parsing package manifests and dependency trees..." },
  { name: "CERTIFICATES", desc: "Inspecting X.509, PKCS#12, and OpenSSH public keys..." },
  { name: "CONFIGURATION", desc: "Scanning TLS cipher suites and cryptographic configurations..." },
  { name: "NORMALIZATION", desc: "Deduplicating and normalizing cryptographic assets..." },
  { name: "QUANTUM ANALYSIS", desc: "Applying Shor & Grover vulnerability categorization..." },
  { name: "MOSCA & RISK", desc: "Evaluating Mosca theorem (X + Y > Z) and 5-factor risk model..." },
  { name: "CBOM & VALIDATION", desc: "Generating CycloneDX 1.6 CBOM and verifying official schema..." },
];

const QUICK_URLS = [
  { label: "cpython (GitHub)", url: "https://github.com/python/cpython" },
  { label: "openssl (GitHub)", url: "https://github.com/openssl/openssl" },
  { label: "openssh (GitHub)", url: "https://github.com/openssh/openssh-portable" },
  { label: "curl (GitHub)", url: "https://github.com/curl/curl" },
];

const IGNORED_DIRS = new Set([
  "node_modules", ".git", ".github", ".svn", ".hg",
  "venv", ".venv", "env", ".env", "__pycache__", ".pytest_cache",
  "dist", "build", "target", "out", ".output",
  ".next", ".nuxt", ".svelte-kit", ".turbo",
  ".idea", ".vscode", ".vs",
  ".gradle", ".cargo", "vendor", "pods",
  ".cache", ".tox", "coverage", "htmlcov", "bin", "obj",
]);

const IGNORED_EXTS = new Set([
  "png", "jpg", "jpeg", "gif", "svg", "ico", "webp", "bmp", "tiff", "avif",
  "mp4", "webm", "mov", "avi", "mkv", "wmv", "flv", "mp3", "wav", "ogg", "flac",
  "zip", "tar", "gz", "tgz", "bz2", "xz", "7z", "rar", "iso", "dmg",
  "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
  "woff", "woff2", "ttf", "eot", "otf",
  "exe", "dll", "so", "dylib", "bin", "obj", "o", "a", "lib", "pdb", "wasm", "map",
]);

function isRelevantScanFile(file: File): boolean {
  if (file.size > 10 * 1024 * 1024) return false; // Skip files > 10MB
  const rel = (file.webkitRelativePath || file.name).replace(/\\/g, "/");
  const parts = rel.toLowerCase().split("/");
  for (let i = 0; i < parts.length - 1; i++) {
    if (IGNORED_DIRS.has(parts[i])) return false;
  }
  const fileName = parts[parts.length - 1];
  if (!fileName) return false;
  // If dotfile (e.g. .DS_Store), ignore unless known config like .env or .conf
  if (fileName.startsWith(".") && !fileName.startsWith(".env") && !fileName.endsWith(".conf")) {
    return false;
  }
  const dotIdx = fileName.lastIndexOf(".");
  if (dotIdx !== -1) {
    const ext = fileName.slice(dotIdx + 1).toLowerCase();
    if (IGNORED_EXTS.has(ext)) return false;
  }
  return true;
}

export const NewScanPage: React.FC = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<InputMode>("path");

  const [urlVal, setUrlVal] = useState("https://github.com/python/cpython");
  const [pathVal, setPathVal] = useState("test_corpus");

  // Local folder selection
  const [selectedFolderFiles, setSelectedFolderFiles] = useState<File[] | null>(null);
  const [selectedFolderName, setSelectedFolderName] = useState<string | null>(null);
  const [ignoredCount, setIgnoredCount] = useState<number>(0);
  const [showFileList, setShowFileList] = useState(false);
  const folderInputRef = useRef<HTMLInputElement>(null);

  // File / ZIP upload
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  // Paste code
  const [pasteCode, setPasteCode] = useState("");
  const [pasteLang, setPasteLang] = useState<LangExt>("py");
  const [pasteFilename, setPasteFilename] = useState("snippet");

  // Real-time execution and progress tracking
  const [scanning, setScanning] = useState(false);
  const [activeStep, setActiveStep] = useState<"compressing" | "uploading" | "analyzing" | "idle">("idle");
  const [stepDetail, setStepDetail] = useState<string>("");
  const [compressPercent, setCompressPercent] = useState<number>(0);
  const [uploadPercent, setUploadPercent] = useState<number>(0);
  const [currentStage, setCurrentStage] = useState("IDLE");
  const [stageProgress, setStageProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const formatBytes = (b: number) =>
    b > 1024 * 1024 ? `${(b / (1024 * 1024)).toFixed(1)} MB` : `${(b / 1024).toFixed(1)} KB`;

  const folderTotalSize = selectedFolderFiles?.reduce((acc, f) => acc + f.size, 0) ?? 0;

  const handleFolderSelected = (fileList: FileList | File[]) => {
    const rawArr = Array.from(fileList);
    if (rawArr.length === 0) return;
    let name = "Selected Folder";
    for (const f of rawArr) {
      if (f.webkitRelativePath) {
        const seg = f.webkitRelativePath.replace(/\\/g, "/").split("/")[0];
        if (seg) {
          name = seg;
          break;
        }
      }
    }

    const relevant = rawArr.filter(isRelevantScanFile);
    setSelectedFolderFiles(relevant);
    setSelectedFolderName(name);
    setIgnoredCount(rawArr.length - relevant.length);
    setError(null);
  };

  const bundleFolderToZip = async (
    files: File[],
    folderName: string,
    onProgress: (percent: number) => void
  ): Promise<File> => {
    const zip = new JSZip();
    for (const f of files) {
      const rel = (f.webkitRelativePath || f.name).replace(/\\/g, "/");
      zip.file(rel, f);
    }

    setStepDetail(`Packaging ${files.length} source & config files...`);

    // Level 1 DEFLATE: 50x faster than level 6, near-instant in browser
    const blob = await zip.generateAsync(
      {
        type: "blob",
        compression: "DEFLATE",
        compressionOptions: { level: 1 },
      },
      (metadata) => {
        const pct = Math.round(metadata.percent);
        setCompressPercent(pct);
        onProgress(pct);
      }
    );

    return new File([blob], `${folderName || "scan_target"}.zip`, { type: "application/zip" });
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) {
      setUploadedFile(f);
      setError(null);
    }
  }, []);

  const runPipelineAnimation = () => {
    let idx = 0;
    setCurrentStage(STAGES[0].name);
    setStageProgress(15);
    const timer = setInterval(() => {
      if (idx < STAGES.length - 2) {
        idx += 1;
        setCurrentStage(STAGES[idx].name);
        setStageProgress(Math.round(((idx + 1) / STAGES.length) * 92));
      }
    }, 1400);
    return timer;
  };

  const handleStartScan = async () => {
    setScanning(true);
    setError(null);
    setActiveStep("idle");
    window.scrollTo({ top: 0, behavior: "smooth" });

    try {
      let promise: Promise<any>;

      if (mode === "path") {
        if (selectedFolderFiles && selectedFolderFiles.length > 0) {
          setActiveStep("compressing");
          setStepDetail("Step 1/3: Compressing folder in browser memory...");
          setCompressPercent(0);

          const zipFile = await bundleFolderToZip(
            selectedFolderFiles,
            selectedFolderName || "project",
            (pct) => setStepDetail(`Step 1/3: In-Memory Compression (${pct}%)`)
          );

          setActiveStep("uploading");
          setStepDetail("Step 2/3: Uploading archive to container sandbox (0%)...");
          setUploadPercent(0);

          const timer = runPipelineAnimation();
          promise = triggerUploadScan(
            zipFile,
            { scenario_year: 2035, x_lifetime: 10.0, y_migration: 3.0 },
            (pct) => {
              setUploadPercent(pct);
              setStepDetail(`Step 2/3: Uploading archive to container sandbox (${pct}%)...`);
              if (pct >= 100) {
                setActiveStep("analyzing");
                setStepDetail("Step 3/3: Running AST discovery & CycloneDX CBOM validation...");
              }
            }
          ).finally(() => clearInterval(timer));
        } else {
          setActiveStep("analyzing");
          setStepDetail(`Scanning directory path: ${pathVal}...`);
          const useCorpus = pathVal.trim() === "test_corpus";
          const timer = runPipelineAnimation();
          promise = triggerScan({ path: pathVal, use_corpus: useCorpus }).finally(() => clearInterval(timer));
        }
      } else if (mode === "upload") {
        if (!uploadedFile) throw new Error("No file selected. Please choose a .ZIP archive or source file.");
        setActiveStep("uploading");
        setStepDetail(`Step 1/2: Uploading ${uploadedFile.name} (0%)...`);
        const timer = runPipelineAnimation();
        promise = triggerUploadScan(
          uploadedFile,
          { scenario_year: 2035, x_lifetime: 10.0, y_migration: 3.0 },
          (pct) => {
            setUploadPercent(pct);
            setStepDetail(`Step 1/2: Uploading ${uploadedFile.name} (${pct}%)...`);
            if (pct >= 100) {
              setActiveStep("analyzing");
              setStepDetail("Step 2/2: Running AST discovery & quantum classification...");
            }
          }
        ).finally(() => clearInterval(timer));
      } else if (mode === "url") {
        setActiveStep("analyzing");
        setStepDetail(`Cloning repository from ${urlVal} and analyzing...`);
        const timer = runPipelineAnimation();
        promise = triggerScan({ path: urlVal, use_corpus: false }).finally(() => clearInterval(timer));
      } else {
        if (!pasteCode.trim()) throw new Error("Code area is empty. Please paste some source code.");
        setActiveStep("analyzing");
        setStepDetail("Scanning pasted code snippet...");
        const timer = runPipelineAnimation();
        promise = triggerPasteScan(pasteCode, `${pasteFilename}.${pasteLang}`).finally(() => clearInterval(timer));
      }

      await promise;
      setActiveStep("idle");
      setCurrentStage(STAGES[STAGES.length - 1].name);
      setStageProgress(100);
      setStepDetail("Complete! Navigating to dashboard...");
      setTimeout(() => navigate("/dashboard"), 700);
    } catch (err: any) {
      setActiveStep("idle");
      setError(err.message || "Cryptographic scan failed.");
      setScanning(false);
    }
  };

  const isReady = () => {
    if (scanning) return false;
    if (mode === "path") return (selectedFolderFiles !== null && selectedFolderFiles.length > 0) || pathVal.trim().length > 0;
    if (mode === "upload") return uploadedFile !== null;
    if (mode === "url") return urlVal.trim().length > 0;
    return pasteCode.trim().length > 0;
  };

  const Tab = ({ id, icon, label, sub }: { id: InputMode; icon: string; label: string; sub: string }) => (
    <button
      id={`scan-tab-${id}`}
      type="button"
      onClick={() => setMode(id)}
      className={`flex-1 flex flex-col items-center gap-1 py-3 px-2 rounded border transition-all text-center ${
        mode === id
          ? "bg-primary/10 border-primary text-primary font-bold"
          : "bg-surface-container border-outline-variant text-on-surface-variant hover:border-outline hover:text-on-surface"
      }`}
    >
      <span className="material-symbols-outlined text-xl">{icon}</span>
      <span className="text-xs font-mono">{label}</span>
      <span className="text-[10px] font-sans opacity-70 leading-tight">{sub}</span>
    </button>
  );

  return (
    <div className="flex-1 p-3 sm:p-4 md:p-6 space-y-4 md:space-y-5 max-w-4xl mx-auto">
      {/* Hidden Native Directory Picker */}
      <input
        ref={folderInputRef}
        type="file"
        className="hidden"
        {...({ webkitdirectory: "", directory: "" } as any)}
        multiple
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleFolderSelected(e.target.files);
          }
        }}
      />

      {/* Header */}
      <section className="flex flex-col md:flex-row md:items-end justify-between border-b border-outline-variant pb-3 gap-2">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg sm:text-xl font-bold tracking-tight text-on-surface">New Scan Configuration</h1>
            <span className="px-1.5 py-0.5 rounded bg-primary-container/15 border border-primary-container/40 text-primary font-mono text-[10px] uppercase font-semibold">
              PROFILE: AST-CRYPT-STRICT
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1 font-sans">
            Cryptographic discovery, Mosca (X+Y&gt;Z) risk modeling, and CycloneDX 1.6 CBOM generation.
          </p>
        </div>
        <div className="text-xs font-mono text-tertiary flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-tertiary animate-pulse" />
          <span>Air-Gap Sandbox Active</span>
        </div>
      </section>

      {/* LIVE SCANNING & UPLOADING PROGRESS OVERLAY - PROMINENT AT TOP */}
      {scanning && (
        <section className="bg-surface-container-low border-2 border-primary rounded-lg p-5 space-y-4 shadow-2xl animate-fadeIn">
          <div className="flex items-center justify-between border-b border-outline-variant pb-2">
            <div className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 rounded-full bg-primary animate-ping" />
              <span className="text-sm font-bold font-mono text-primary uppercase">
                {activeStep === "compressing"
                  ? "Step 1/3: In-Memory Compression"
                  : activeStep === "uploading"
                  ? "Step 2/3: Uploading Archive to Container Sandbox"
                  : "Step 3/3: Running AST Discovery & Risk Analysis"}
              </span>
            </div>
            <span className="text-xs font-mono text-on-surface font-bold bg-surface-container px-2 py-0.5 rounded border border-outline-variant">
              {activeStep === "compressing" ? `${compressPercent}%` : activeStep === "uploading" ? `${uploadPercent}%` : `${stageProgress}%`}
            </span>
          </div>

          <div className="w-full bg-surface-container-highest rounded-full h-3 overflow-hidden shadow-inner">
            <div
              className="bg-primary h-full transition-all duration-300 ease-out"
              style={{
                width: `${
                  activeStep === "compressing"
                    ? Math.round(compressPercent * 0.3)
                    : activeStep === "uploading"
                    ? 30 + Math.round(uploadPercent * 0.35)
                    : 65 + Math.round(stageProgress * 0.35)
                }%`,
              }}
            />
          </div>

          <div className="p-3 bg-surface-container-lowest border border-outline-variant rounded font-mono text-xs text-on-surface flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-sm text-primary animate-spin">progress_activity</span>
              <span className="font-semibold">{stepDetail || "Processing scan..."}</span>
            </div>
            <span className="text-[11px] text-tertiary font-mono">LIVE EXECUTION</span>
          </div>

          <div className="flex gap-1.5 flex-wrap">
            {STAGES.map((s) => {
              const idx = STAGES.findIndex((x) => x.name === currentStage);
              const i = STAGES.indexOf(s);
              return (
                <span
                  key={s.name}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border transition-colors ${
                    i < idx
                      ? "bg-tertiary/20 text-tertiary border-tertiary/50"
                      : i === idx
                      ? "bg-primary/20 text-primary border-primary font-bold animate-pulse"
                      : "bg-surface-container text-outline border-outline-variant"
                  }`}
                >
                  {s.name}
                </span>
              );
            })}
          </div>
        </section>
      )}

      {/* PROMINENT FOLDER SELECTED BANNER */}
      {mode === "path" && selectedFolderFiles && selectedFolderFiles.length > 0 && (
        <section className="p-4 bg-tertiary/10 border-2 border-tertiary rounded-lg space-y-3 shadow-md animate-fadeIn">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-start gap-3">
              <span className="material-symbols-outlined text-tertiary text-3xl shrink-0 mt-0.5">folder_zip</span>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-sm font-bold font-mono text-tertiary uppercase tracking-wide">
                    {scanning ? "Folder Upload & Analysis In Progress" : "Folder Selected On Your PC"}
                  </h2>
                  <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                    scanning ? "bg-primary text-on-primary animate-pulse" : "bg-tertiary text-surface"
                  }`}>
                    {scanning ? (uploadPercent >= 100 ? "UPLOADED ✓" : `UPLOADING ${uploadPercent}%`) : "READY TO SCAN"}
                  </span>
                </div>
                <p className="text-sm font-semibold font-mono text-on-surface mt-1">
                  Folder: {selectedFolderName}
                </p>
                <p className="text-xs text-on-surface-variant font-mono mt-0.5">
                  Contains <strong>{selectedFolderFiles.length} source & config files</strong> ({formatBytes(folderTotalSize)})
                  {ignoredCount > 0 && (
                    <span className="text-tertiary">
                      {" "}• Bypassed {ignoredCount.toLocaleString()} package, build & cache files
                    </span>
                  )}
                  {" "}• {
                    scanning
                      ? activeStep === "compressing" ? `Packaging (${compressPercent}%)...` : activeStep === "uploading" ? `Uploading archive (${uploadPercent}%)...` : "Uploaded! Running AST engine..."
                      : "Staged in memory. Click 'Start Scan Now' below for instant scan."
                  }
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {!scanning && (
                <button
                  type="button"
                  id="btn-scan-selected-folder"
                  onClick={handleStartScan}
                  className="bg-primary hover:bg-primary/90 text-on-primary font-mono text-xs font-bold py-2.5 px-4 rounded flex items-center gap-1.5 shadow-lg transition-all"
                >
                  <span className="material-symbols-outlined text-base">rocket_launch</span>
                  <span>Start Scan Now</span>
                </button>
              )}
              <button
                type="button"
                onClick={() => folderInputRef.current?.click()}
                disabled={scanning}
                className="border border-outline-variant hover:border-on-surface text-on-surface font-mono text-xs py-2.5 px-3 rounded transition-colors"
              >
                Change
              </button>
              <button
                type="button"
                onClick={() => {
                  setSelectedFolderFiles(null);
                  setSelectedFolderName(null);
                  setPathVal("test_corpus");
                }}
                disabled={scanning}
                className="border border-error/40 text-error hover:bg-error/10 font-mono text-xs py-2.5 px-2.5 rounded transition-colors"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="border-t border-tertiary/30 pt-2 flex items-center justify-between text-[11px] font-mono">
            <button
              type="button"
              onClick={() => setShowFileList(!showFileList)}
              className="text-tertiary hover:underline flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-sm">
                {showFileList ? "expand_less" : "expand_more"}
              </span>
              <span>{showFileList ? "Hide file list" : `View detected files (${selectedFolderFiles.length})`}</span>
            </button>
            <span className="text-outline">
              {scanning ? "Status: Uploading / Running pipeline" : "Status: Staged locally (Not sent yet)"}
            </span>
          </div>

          {showFileList && (
            <div className="max-h-40 overflow-y-auto bg-surface-container-lowest border border-outline-variant rounded p-2 text-[10px] font-mono space-y-0.5 text-on-surface-variant">
              {selectedFolderFiles.slice(0, 100).map((f, i) => (
                <div key={i} className="truncate">
                  {f.webkitRelativePath || f.name} <span className="text-outline">({formatBytes(f.size)})</span>
                </div>
              ))}
              {selectedFolderFiles.length > 100 && (
                <div className="text-primary italic pt-1">
                  ...and {selectedFolderFiles.length - 100} more files.
                </div>
              )}
            </div>
          )}
        </section>
      )}

      {/* INPUT SELECTOR TABS */}
      <section className="space-y-3">
        <div className="text-xs font-mono text-on-surface-variant">1. SELECT INPUT TYPE</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <Tab id="path"   icon="folder_open" label="Select Folder"  sub="Pick folder from this PC" />
          <Tab id="upload" icon="upload_file" label="File / ZIP"     sub="Upload .zip or single file" />
          <Tab id="url"    icon="link"        label="URL / Git"      sub="GitHub or any git repo" />
          <Tab id="paste"  icon="code"        label="Paste Code"     sub="Inline source text" />
        </div>
      </section>

      {/* INPUT DETAILS PANEL */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-4">
        <div className="flex items-center gap-1.5 font-semibold text-sm text-primary border-b border-outline-variant pb-2">
          <span className="material-symbols-outlined text-base">
            {mode === "path" ? "folder_open" : mode === "upload" ? "upload_file" : mode === "url" ? "link" : "code"}
          </span>
          <span>
            {mode === "path" ? "2. Local Directory Folder" : mode === "upload" ? "2. Upload File or .ZIP Archive" : mode === "url" ? "2. Repository URL" : "2. Paste Source Code"}
          </span>
        </div>

        {/* TAB 1: SELECT FOLDER */}
        {mode === "path" && (
          <div className="space-y-4">
            <div className="p-4 bg-surface-container-lowest border border-outline-variant rounded-lg space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 text-sm font-mono font-bold text-on-surface">
                    <span className="material-symbols-outlined text-primary text-xl">folder</span>
                    <span>Browse Project Folder from Your PC</span>
                  </div>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Opens your native folder picker to select any local directory.
                  </p>
                </div>
                <button
                  type="button"
                  id="browse-folder-btn"
                  onClick={() => folderInputRef.current?.click()}
                  disabled={scanning}
                  className="bg-primary hover:bg-primary/90 text-on-primary font-mono text-xs font-bold py-2.5 px-4 rounded flex items-center justify-center gap-2 transition-all shadow shrink-0"
                >
                  <span className="material-symbols-outlined text-base">folder_open</span>
                  <span>{selectedFolderFiles ? "Select Different Folder" : "Browse & Select Folder"}</span>
                </button>
              </div>
            </div>

            <div className="space-y-2 pt-1 border-t border-outline-variant/60">
              <label className="text-xs font-mono text-on-surface-variant block">
                Or enter directory path (for server-local filesystem / controlled test corpus):
              </label>
              <input
                id="scan-path-input"
                type="text"
                value={pathVal}
                onChange={(e) => {
                  setPathVal(e.target.value);
                  if (selectedFolderFiles) {
                    setSelectedFolderFiles(null);
                    setSelectedFolderName(null);
                  }
                }}
                disabled={scanning}
                placeholder="e.g. test_corpus"
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
              />
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] font-mono text-outline">Quick preset:</span>
                <button
                  type="button"
                  onClick={() => {
                    setPathVal("test_corpus");
                    setSelectedFolderFiles(null);
                    setSelectedFolderName(null);
                  }}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border transition-colors ${
                    pathVal === "test_corpus" && !selectedFolderFiles
                      ? "bg-tertiary/20 text-tertiary border-tertiary font-bold"
                      : "bg-surface-container border-outline-variant text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  controlled test_corpus
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: FILE / ZIP */}
        {mode === "upload" && (
          <div className="space-y-3">
            <div
              id="scan-dropzone"
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center gap-3 cursor-pointer transition-all ${
                dragOver ? "border-primary bg-primary/5" : uploadedFile ? "border-tertiary bg-tertiary/5" : "border-outline-variant hover:border-outline bg-surface-container"
              }`}
            >
              <span className="material-symbols-outlined text-4xl text-on-surface-variant">
                {uploadedFile ? "task" : "cloud_upload"}
              </span>

              {uploadedFile ? (
                <div className="text-center">
                  <p className="text-sm font-semibold text-tertiary font-mono">{uploadedFile.name}</p>
                  <p className="text-xs text-on-surface-variant mt-1">{formatBytes(uploadedFile.size)}</p>
                </div>
              ) : (
                <div className="text-center space-y-1">
                  <p className="text-sm font-semibold text-on-surface">Drop a .ZIP archive or source file here, or <span className="text-primary underline">browse</span></p>
                  <p className="text-xs text-on-surface-variant">Accepts: .zip, .jar, .py, .java, .js, .ts, .c, .cpp, .go, .rs (Max: 500 MB)</p>
                  <p className="text-[11px] text-outline">ZIP archives are automatically extracted and analyzed in the container sandbox.</p>
                </div>
              )}

              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                className="bg-primary hover:bg-primary/90 text-on-primary font-mono text-xs font-bold px-4 py-2 rounded flex items-center gap-1.5 transition shadow"
              >
                <span className="material-symbols-outlined text-sm">upload_file</span>
                <span>{uploadedFile ? "Change File / .ZIP" : "Browse File / .ZIP"}</span>
              </button>

              <input
                id="scan-file-input"
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".py,.java,.js,.ts,.c,.cpp,.go,.rs,.zip,.jar,.class,.pem,.crt,.key,.txt"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) {
                    setUploadedFile(f);
                  }
                }}
              />
            </div>

            {uploadedFile && (
              <div className="p-3 bg-surface-container border border-outline-variant rounded-lg flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <span className="material-symbols-outlined text-primary text-2xl">description</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-xs font-mono font-bold text-on-surface">{uploadedFile.name}</p>
                      <span className={`px-1.5 py-0.5 rounded font-mono text-[9px] font-bold ${
                        scanning ? "bg-primary text-on-primary animate-pulse" : "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                      }`}>
                        {scanning ? (uploadPercent >= 100 ? "UPLOADED ✓" : `UPLOADING ${uploadPercent}%`) : "READY TO UPLOAD"}
                      </span>
                    </div>
                    <p className="text-[11px] font-mono text-on-surface-variant">
                      Size: {formatBytes(uploadedFile.size)} • {
                        scanning
                          ? uploadPercent >= 100 ? "File uploaded to container sandbox! Running analysis..." : `Uploading: ${uploadPercent}%`
                          : "Staged on your computer. Click 'Start Scan' to upload & analyze."
                      }
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  {!scanning && (
                    <button
                      type="button"
                      onClick={handleStartScan}
                      className="bg-primary hover:bg-primary/90 text-on-primary font-mono text-xs font-bold py-2 px-3 rounded flex items-center gap-1 shadow"
                    >
                      <span className="material-symbols-outlined text-sm">rocket_launch</span>
                      <span>Start Scan</span>
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => {
                      setUploadedFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = "";
                    }}
                    disabled={scanning}
                    className="text-[10px] font-mono text-error border border-error/40 px-2 py-1.5 rounded hover:bg-error/10 transition"
                  >
                    Remove
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: URL / GIT */}
        {mode === "url" && (
          <div className="space-y-3">
            <div>
              <label className="text-xs font-mono text-on-surface-variant block mb-1">GitHub URL or any git-clonable URL</label>
              <input
                id="scan-url-input"
                type="url"
                value={urlVal}
                onChange={(e) => setUrlVal(e.target.value)}
                disabled={scanning}
                placeholder="https://github.com/owner/repo"
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
              />
            </div>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[10px] font-mono text-outline">Quick presets:</span>
              {QUICK_URLS.map((q) => (
                <button
                  key={q.url}
                  type="button"
                  onClick={() => setUrlVal(q.url)}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border transition-colors ${
                    urlVal === q.url
                      ? "bg-primary/20 text-primary border-primary font-bold"
                      : "bg-surface-container border-outline-variant text-on-surface-variant hover:text-on-surface hover:border-primary/50"
                  }`}
                >
                  {q.label}
                </button>
              ))}
            </div>
            <p className="text-[11px] font-mono text-outline">The repo will be shallow-cloned locally for air-gapped analysis. No data leaves the machine.</p>
          </div>
        )}

        {/* TAB 4: PASTE CODE */}
        {mode === "paste" && (
          <div className="space-y-3">
            <div className="flex gap-2 items-end flex-wrap">
              <div>
                <label className="text-xs font-mono text-on-surface-variant block mb-1">Virtual filename</label>
                <input
                  type="text"
                  value={pasteFilename}
                  onChange={(e) => setPasteFilename(e.target.value)}
                  disabled={scanning}
                  className="bg-surface-container-lowest border border-outline-variant rounded px-2.5 py-1.5 text-xs font-mono text-on-surface focus:outline-none focus:border-primary w-40 disabled:opacity-60"
                />
              </div>
              <div>
                <label className="text-xs font-mono text-on-surface-variant block mb-1">Language</label>
                <select
                  value={pasteLang}
                  onChange={(e) => setPasteLang(e.target.value as LangExt)}
                  disabled={scanning}
                  className="bg-surface-container-lowest border border-outline-variant rounded px-2.5 py-1.5 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
                >
                  {LANG_EXTS.map((l) => (
                    <option key={l.ext} value={l.ext}>{l.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <textarea
              id="scan-paste-input"
              rows={10}
              value={pasteCode}
              onChange={(e) => setPasteCode(e.target.value)}
              disabled={scanning}
              placeholder="// Paste source code containing cryptographic usages, cipher suites, or key material here..."
              className="w-full bg-surface-container-lowest border border-outline-variant rounded p-3 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60 resize-y"
            />
          </div>
        )}
      </section>

      {/* ACTIVE COLLECTORS INFORMATIONAL GRID */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-outline-variant pb-2">
          <div className="flex items-center gap-1.5 font-semibold text-sm text-on-surface">
            <span className="material-symbols-outlined text-base text-secondary">tune</span>
            <span>3. Active Cryptographic Discovery Collectors</span>
          </div>
          <span className="text-[10px] font-mono text-tertiary font-bold">All enabled</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
          <div className="p-2.5 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
            <div className="flex items-center gap-1.5 text-tertiary font-mono font-bold">
              <span className="material-symbols-outlined text-sm">check_circle</span>
              <span>Source AST Scanner</span>
            </div>
            <p className="text-[11px] text-on-surface-variant">Python & Java AST call-site visitor – key sizes, modes, algorithms</p>
          </div>
          <div className="p-2.5 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
            <div className="flex items-center gap-1.5 text-tertiary font-mono font-bold">
              <span className="material-symbols-outlined text-sm">check_circle</span>
              <span>Manifest Dependency Scanner</span>
            </div>
            <p className="text-[11px] text-on-surface-variant">requirements.txt, pom.xml, package.json, go.mod, Cargo.toml</p>
          </div>
          <div className="p-2.5 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
            <div className="flex items-center gap-1.5 text-tertiary font-mono font-bold">
              <span className="material-symbols-outlined text-sm">check_circle</span>
              <span>Certificates & Public Keys</span>
            </div>
            <p className="text-[11px] text-on-surface-variant">X.509 (PEM/DER), PKCS#12, OpenSSH keys – zero key persistence</p>
          </div>
          <div className="p-2.5 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
            <div className="flex items-center gap-1.5 text-tertiary font-mono font-bold">
              <span className="material-symbols-outlined text-sm">check_circle</span>
              <span>Config & Cipher Suite Scanner</span>
            </div>
            <p className="text-[11px] text-on-surface-variant">nginx.conf, sshd_config, openssl.cnf, Dockerfiles, TLS bounds</p>
          </div>
          <div className="p-2.5 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
            <div className="flex items-center gap-1.5 text-tertiary font-mono font-bold">
              <span className="material-symbols-outlined text-sm">check_circle</span>
              <span>JVM Bytecode Scanner</span>
            </div>
            <p className="text-[11px] text-on-surface-variant">Pure-Python JVM constant pool extractor (.class, .jar) + zip-slip safety</p>
          </div>
          <div className="p-2.5 bg-surface-container-lowest border border-outline-variant rounded space-y-1">
            <div className="flex items-center gap-1.5 text-outline font-mono">
              <span className="material-symbols-outlined text-sm">radio_button_unchecked</span>
              <span>Live Endpoints & Containers</span>
            </div>
            <p className="text-[11px] text-on-surface-variant">Enterprise roadmap – MVP is air-gapped static analysis</p>
          </div>
        </div>
      </section>

      {/* ERROR BANNER */}
      {error && (
        <div className="bg-error-container/20 border-2 border-error p-4 rounded-lg flex items-start gap-3">
          <span className="material-symbols-outlined text-error text-xl mt-0.5">error</span>
          <div className="flex-1 space-y-2">
            <p className="text-error font-mono text-xs font-bold uppercase">Cryptographic Scan Error</p>
            <p className="text-on-surface font-mono text-xs leading-relaxed">{error}</p>
            {(error.includes("container") || error.includes("/app/") || error.includes("does not exist") || error.includes("drive path")) && (
              <div className="pt-1">
                <button
                  type="button"
                  onClick={() => {
                    setMode("path");
                    folderInputRef.current?.click();
                  }}
                  className="text-xs font-mono font-bold text-on-primary bg-primary hover:bg-primary/90 px-3 py-1.5 rounded flex items-center gap-1.5 shadow"
                >
                  <span className="material-symbols-outlined text-sm">folder_open</span>
                  <span>Click here to select your folder with the Folder Picker instead</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* PRIMARY LAUNCH ACTION */}
      <section className="pt-2">
        <button
          id="scan-start-btn"
          onClick={handleStartScan}
          disabled={!isReady()}
          className="w-full bg-primary hover:bg-primary/90 text-on-primary font-mono text-sm font-bold py-3.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-xl"
        >
          <span className="material-symbols-outlined text-lg">{scanning ? "sync" : "rocket_launch"}</span>
          <span>
            {scanning
              ? "Running Pipeline..."
              : mode === "path" && selectedFolderName
              ? `🚀 Initiate AST Cryptographic Scan — Folder: ${selectedFolderName}`
              : `Initiate AST Cryptographic Scan — ${
                  mode === "path" ? "Local Path" :
                  mode === "upload" ? (uploadedFile ? uploadedFile.name : "File / ZIP Upload") :
                  mode === "url" ? "GitHub / URL" :
                  "Pasted Code"
                }`}
          </span>
        </button>
        <p className="text-center text-[10px] font-mono text-outline mt-2">
          Discovery → Evidence → Normalization → Quantum Classification → Mosca X+Y&gt;Z → Risk Scoring → PQC Recommendations → CycloneDX 1.6 CBOM
        </p>
      </section>
    </div>
  );
};

export default NewScanPage;

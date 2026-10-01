import React, { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import JSZip from "jszip";
import { triggerScan, triggerUploadScan, triggerPasteScan } from "../../services/api";

type InputMode = "url" | "path" | "upload" | "paste";
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

export const NewScanPage: React.FC = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<InputMode>("path");

  const [urlVal, setUrlVal] = useState("https://github.com/python/cpython");
  const [pathVal, setPathVal] = useState("test_corpus");

  // Single file or folder upload state
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [selectedFolderFiles, setSelectedFolderFiles] = useState<File[] | null>(null);
  const [selectedFolderName, setSelectedFolderName] = useState<string | null>(null);

  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);

  const [pasteCode, setPasteCode] = useState("");
  const [pasteLang, setPasteLang] = useState<LangExt>("py");
  const [pasteFilename, setPasteFilename] = useState("snippet");

  const [scanning, setScanning] = useState(false);
  const [currentStage, setCurrentStage] = useState("IDLE");
  const [stageProgress, setStageProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const formatBytes = (b: number) =>
    b > 1024 * 1024 ? `${(b / (1024 * 1024)).toFixed(1)} MB` : `${(b / 1024).toFixed(1)} KB`;

  const folderTotalSize = selectedFolderFiles?.reduce((acc, f) => acc + f.size, 0) ?? 0;

  const handleFolderSelected = (fileList: FileList | File[]) => {
    const arr = Array.from(fileList);
    if (arr.length === 0) return;
    let name = "Selected Folder";
    for (const f of arr) {
      if (f.webkitRelativePath) {
        name = f.webkitRelativePath.split("/")[0] || name;
        break;
      }
    }
    setSelectedFolderFiles(arr);
    setSelectedFolderName(name);
    setUploadedFile(null);
    setError(null);
  };

  const bundleFolderToZip = async (files: File[], folderName: string): Promise<File> => {
    const zip = new JSZip();
    for (const f of files) {
      const rel = f.webkitRelativePath || f.name;
      // Skip heavy build / cache / vendor directories
      if (
        rel.includes("/node_modules/") ||
        rel.includes("/.git/") ||
        rel.includes("/venv/") ||
        rel.includes("/__pycache__/") ||
        rel.includes("/dist/") ||
        rel.includes("/build/") ||
        rel.includes("/target/") ||
        rel.includes("/.idea/") ||
        rel.includes("/.vscode/")
      ) {
        continue;
      }
      zip.file(rel, f);
    }
    const blob = await zip.generateAsync({
      type: "blob",
      compression: "DEFLATE",
      compressionOptions: { level: 6 },
    });
    return new File([blob], `${folderName || "scan_target"}.zip`, { type: "application/zip" });
  };

  const onDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const items = e.dataTransfer.items;
    if (items && items.length > 0) {
      const files: File[] = [];
      const queue: any[] = [];
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if ((item as any).webkitGetAsEntry) {
          const entry = (item as any).webkitGetAsEntry();
          if (entry) queue.push(entry);
        }
      }

      if (queue.length > 0) {
        const traverse = async (entry: any, currentPath = ""): Promise<void> => {
          if (entry.isFile) {
            await new Promise<void>((resolve) => {
              entry.file((file: File) => {
                Object.defineProperty(file, "webkitRelativePath", {
                  value: currentPath ? `${currentPath}/${file.name}` : file.name,
                  writable: false,
                });
                files.push(file);
                resolve();
              });
            });
          } else if (entry.isDirectory) {
            if (["node_modules", ".git", "venv", "__pycache__", "dist", "build", "target"].includes(entry.name)) {
              return;
            }
            const dirReader = entry.createReader();
            const readEntries = (): Promise<any[]> =>
              new Promise((resolve) => dirReader.readEntries((ents: any[]) => resolve(ents)));
            let entries = await readEntries();
            while (entries.length > 0) {
              for (const child of entries) {
                await traverse(child, currentPath ? `${currentPath}/${entry.name}` : entry.name);
              }
              entries = await readEntries();
            }
          }
        };

        for (const q of queue) {
          await traverse(q, "");
        }

        if (files.length > 1 || (files.length === 1 && files[0].webkitRelativePath)) {
          handleFolderSelected(files);
          setMode("path");
          return;
        }
      }
    }

    const f = e.dataTransfer.files[0];
    if (f) {
      setUploadedFile(f);
      setSelectedFolderFiles(null);
      setSelectedFolderName(null);
    }
  }, []);

  const runPipelineAnimation = () => {
    let idx = 0;
    setCurrentStage(STAGES[0].name);
    setStageProgress(12);
    const timer = setInterval(() => {
      if (idx < STAGES.length - 2) {
        idx += 1;
        setCurrentStage(STAGES[idx].name);
        setStageProgress(Math.round(((idx + 1) / STAGES.length) * 90));
      }
    }, 1400);
    return timer;
  };

  const handleStartScan = async () => {
    setScanning(true);
    setError(null);
    const timer = runPipelineAnimation();

    try {
      let promise: Promise<any>;

      // Priority 1: If user picked an entire folder via folder picker
      if (selectedFolderFiles && selectedFolderFiles.length > 0 && (mode === "path" || mode === "upload")) {
        setCurrentStage("PREPARING FOLDER");
        setStageProgress(8);
        const zipFile = await bundleFolderToZip(selectedFolderFiles, selectedFolderName || "project");
        promise = triggerUploadScan(zipFile);
      } else if (mode === "url") {
        promise = triggerScan({ path: urlVal, use_corpus: false });
      } else if (mode === "path") {
        const useCorpus = pathVal.trim() === "test_corpus";
        promise = triggerScan({ path: pathVal, use_corpus: useCorpus });
      } else if (mode === "upload") {
        if (!uploadedFile) throw new Error("No file or folder selected. Please select a file or folder to scan.");
        promise = triggerUploadScan(uploadedFile);
      } else {
        if (!pasteCode.trim()) throw new Error("Code area is empty. Please paste some source code.");
        promise = triggerPasteScan(pasteCode, `${pasteFilename}.${pasteLang}`);
      }

      await promise;
      clearInterval(timer);
      setCurrentStage(STAGES[STAGES.length - 1].name);
      setStageProgress(100);
      setTimeout(() => navigate("/dashboard"), 600);
    } catch (err: any) {
      clearInterval(timer);
      setError(err.message || "Cryptographic scan failed.");
      setScanning(false);
    }
  };

  const isReady = () => {
    if (scanning) return false;
    if (mode === "url") return urlVal.trim().length > 0;
    if (mode === "path") return (selectedFolderFiles !== null && selectedFolderFiles.length > 0) || pathVal.trim().length > 0;
    if (mode === "upload") return uploadedFile !== null || (selectedFolderFiles !== null && selectedFolderFiles.length > 0);
    return pasteCode.trim().length > 0;
  };

  const Tab = ({ id, icon, label, sub }: { id: InputMode; icon: string; label: string; sub: string }) => (
    <button
      id={`scan-tab-${id}`}
      type="button"
      onClick={() => setMode(id)}
      className={`flex-1 flex flex-col items-center gap-1 py-3 px-2 rounded border transition-all text-center ${
        mode === id
          ? "bg-primary/10 border-primary text-primary"
          : "bg-surface-container border-outline-variant text-on-surface-variant hover:border-outline hover:text-on-surface"
      }`}
    >
      <span className="material-symbols-outlined text-xl">{icon}</span>
      <span className="text-xs font-semibold font-mono">{label}</span>
      <span className="text-[10px] font-sans opacity-70 leading-tight">{sub}</span>
    </button>
  );

  return (
    <div className="flex-1 p-6 space-y-5 max-w-4xl mx-auto">
      {/* Hidden Native Folder Input */}
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

      <section className="flex flex-col md:flex-row md:items-end justify-between border-b border-outline-variant pb-3 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-on-surface">New Scan Configuration</h1>
            <span className="px-1.5 py-0.5 rounded bg-primary-container/15 border border-primary-container/40 text-primary font-mono text-[10px] uppercase font-semibold">
              PROFILE: AST-CRYPT-STRICT
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1 font-sans">
            Choose any input type — the full cryptographic discovery and quantum risk pipeline runs on all of them.
          </p>
        </div>
        <div className="text-xs font-mono text-tertiary flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-tertiary animate-pulse" />
          <span>Air-Gap Sandbox Active</span>
        </div>
      </section>

      <section className="space-y-3">
        <div className="text-xs font-mono text-on-surface-variant">1. SELECT INPUT TYPE</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <Tab id="path"   icon="folder_open" label="Select Folder"  sub="Pick directory from this PC" />
          <Tab id="upload" icon="upload_file" label="File / ZIP"     sub=".zip, .py, .java, .jar" />
          <Tab id="url"    icon="link"        label="URL / Git"      sub="GitHub or any git repo" />
          <Tab id="paste"  icon="code"        label="Paste Code"     sub="Inline source text" />
        </div>
      </section>

      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-4">
        <div className="flex items-center gap-1.5 font-semibold text-sm text-primary border-b border-outline-variant pb-2">
          <span className="material-symbols-outlined text-base">
            {mode === "path" ? "folder_open" : mode === "upload" ? "upload_file" : mode === "url" ? "link" : "code"}
          </span>
          <span>
            {mode === "path" ? "2. Local Directory Folder" : mode === "upload" ? "2. File or Archive Upload" : mode === "url" ? "2. Repository URL" : "2. Paste Source Code"}
          </span>
        </div>

        {mode === "path" && (
          <div className="space-y-4">
            {/* Primary Action: Direct Folder Selector */}
            <div className="p-4 bg-surface-container-lowest border-2 border-primary/40 rounded-lg space-y-3 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 text-sm font-mono font-bold text-on-surface">
                    <span className="material-symbols-outlined text-primary text-xl">folder</span>
                    <span>Select Any Project Folder from Your PC</span>
                  </div>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Click to open your file explorer and choose any directory. Works automatically with Docker and cloud containers.
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
                  <span>{selectedFolderFiles ? "Change Folder" : "Browse & Select Folder"}</span>
                </button>
              </div>

              {selectedFolderFiles && (
                <div className="p-3 bg-tertiary/10 border border-tertiary/40 rounded flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="material-symbols-outlined text-tertiary text-2xl shrink-0">check_circle</span>
                    <div className="truncate">
                      <p className="text-xs font-mono font-bold text-tertiary truncate">
                        Selected: {selectedFolderName}
                      </p>
                      <p className="text-[11px] font-mono text-on-surface-variant">
                        {selectedFolderFiles.length} files ({formatBytes(folderTotalSize)}) • Ready for full cryptographic discovery & CBOM generation
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedFolderFiles(null);
                      setSelectedFolderName(null);
                      setPathVal("test_corpus");
                    }}
                    className="text-[10px] font-mono text-error border border-error/40 px-2 py-1 rounded hover:bg-error/10 shrink-0"
                  >
                    Clear
                  </button>
                </div>
              )}
            </div>

            {/* Fallback: Direct server path or preset */}
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
              <p className="text-[11px] font-mono text-outline leading-relaxed">
                Note: In Docker container environments, host drive paths (e.g. C:\Users\...) are isolated from the container. Use <strong>"Browse & Select Folder"</strong> above to scan any PC folder seamlessly.
              </p>
            </div>
          </div>
        )}

        {mode === "upload" && (
          <div className="space-y-3">
            <div
              id="scan-dropzone"
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
              className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center gap-3 transition-all ${
                dragOver ? "border-primary bg-primary/5" : (uploadedFile || selectedFolderFiles) ? "border-tertiary bg-tertiary/5" : "border-outline-variant hover:border-outline bg-surface-container"
              }`}
            >
              <span className="material-symbols-outlined text-4xl text-on-surface-variant">
                {(uploadedFile || selectedFolderFiles) ? "task" : "cloud_upload"}
              </span>

              {selectedFolderFiles ? (
                <div className="text-center">
                  <p className="text-sm font-semibold text-tertiary font-mono">Folder: {selectedFolderName}</p>
                  <p className="text-xs text-on-surface-variant mt-1">{selectedFolderFiles.length} files ({formatBytes(folderTotalSize)})</p>
                </div>
              ) : uploadedFile ? (
                <div className="text-center">
                  <p className="text-sm font-semibold text-tertiary font-mono">{uploadedFile.name}</p>
                  <p className="text-xs text-on-surface-variant mt-1">{formatBytes(uploadedFile.size)}</p>
                </div>
              ) : (
                <div className="text-center space-y-1">
                  <p className="text-sm font-semibold text-on-surface">Drag & drop any folder or file here</p>
                  <p className="text-xs text-on-surface-variant">Accepts: Folders, .zip, .jar, .py, .java, .js, .ts, .c, .cpp, .go, .rs, or any source code</p>
                  <p className="text-xs text-outline">Max size: 500 MB (Auto-extracted in air-gapped sandbox)</p>
                </div>
              )}

              <div className="flex items-center gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => folderInputRef.current?.click()}
                  className="bg-primary/10 hover:bg-primary/20 text-primary border border-primary/40 px-3 py-1.5 rounded text-xs font-mono font-bold flex items-center gap-1.5 transition"
                >
                  <span className="material-symbols-outlined text-sm">folder_open</span>
                  <span>Select Folder</span>
                </button>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant text-on-surface px-3 py-1.5 rounded text-xs font-mono flex items-center gap-1.5 transition"
                >
                  <span className="material-symbols-outlined text-sm">upload_file</span>
                  <span>Select File / ZIP</span>
                </button>
              </div>

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
                    setSelectedFolderFiles(null);
                    setSelectedFolderName(null);
                  }
                }}
              />
            </div>

            {(uploadedFile || selectedFolderFiles) && (
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono text-on-surface-variant flex-1">
                  Selected: <span className="text-primary font-bold">{selectedFolderName || uploadedFile?.name}</span> ({formatBytes(folderTotalSize || uploadedFile?.size || 0)})
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setUploadedFile(null);
                    setSelectedFolderFiles(null);
                    setSelectedFolderName(null);
                    if (fileInputRef.current) fileInputRef.current.value = "";
                  }}
                  className="text-[10px] font-mono text-error border border-error/40 px-2 py-0.5 rounded hover:bg-error/10 transition"
                >
                  Remove
                </button>
              </div>
            )}
            <p className="text-[11px] font-mono text-outline">Archives and folders are extracted in an isolated sandbox. All temporary files are automatically cleaned up.</p>
          </div>
        )}

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

      {/* Active Collectors Informational Grid */}
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

      {scanning && (
        <section className="bg-surface-container-low border border-primary-container/60 rounded p-4 space-y-2">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-primary font-bold">⟳ Stage: {currentStage}</span>
            <span className="text-on-surface-variant">{stageProgress}%</span>
          </div>
          <div className="w-full bg-surface-container-highest rounded h-2 overflow-hidden">
            <div className="bg-primary h-full transition-all duration-300 ease-out" style={{ width: `${stageProgress}%` }} />
          </div>
          <p className="text-[11px] font-mono text-outline">
            {STAGES.find((s) => s.name === currentStage)?.desc ?? "Executing cryptographic discovery pipeline..."}
          </p>
          <div className="flex gap-1 flex-wrap mt-1">
            {STAGES.map((s) => {
              const idx = STAGES.findIndex((x) => x.name === currentStage);
              const i = STAGES.indexOf(s);
              return (
                <span key={s.name} className={`px-1.5 py-0.5 rounded text-[9px] font-mono border transition-colors ${
                  i < idx ? "bg-tertiary/20 text-tertiary border-tertiary/50" : i === idx ? "bg-primary/20 text-primary border-primary font-bold" : "bg-surface-container text-outline border-outline-variant"
                }`}>{s.name}</span>
              );
            })}
          </div>
        </section>
      )}

      {error && (
        <div className="bg-error-container/20 border border-error/40 p-3 rounded flex items-start gap-2">
          <span className="material-symbols-outlined text-error text-sm mt-0.5">error</span>
          <div className="flex-1">
            <p className="text-error font-mono text-xs font-bold">Scan Failed</p>
            <p className="text-error/90 font-mono text-xs mt-0.5">{error}</p>
            {(error.includes("container") || error.includes("/app/") || error.includes("does not exist") || error.includes("drive path")) && (
              <button
                type="button"
                onClick={() => folderInputRef.current?.click()}
                className="mt-2 text-xs font-mono font-bold text-primary bg-primary/10 hover:bg-primary/20 border border-primary/40 px-3 py-1.5 rounded flex items-center gap-1.5 transition"
              >
                <span className="material-symbols-outlined text-sm">folder_open</span>
                <span>Click here to select your folder with the Folder Picker</span>
              </button>
            )}
          </div>
        </div>
      )}

      <section className="pt-1">
        <button
          id="scan-start-btn"
          onClick={handleStartScan}
          disabled={!isReady()}
          className="w-full bg-primary hover:bg-primary/90 text-on-primary font-mono text-sm font-bold py-3 px-4 rounded flex items-center justify-center gap-2 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-lg"
        >
          <span className="material-symbols-outlined text-base">{scanning ? "sync" : "rocket_launch"}</span>
          <span>
            {scanning
              ? "Executing Cryptographic Discovery Pipeline..."
              : selectedFolderName
              ? `Initiate AST Cryptographic Scan — Folder: ${selectedFolderName}`
              : `Initiate AST Cryptographic Scan — ${
                  mode === "url" ? "GitHub / URL" :
                  mode === "path" ? "Local Path" :
                  mode === "upload" ? (uploadedFile ? uploadedFile.name : "File Upload") :
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

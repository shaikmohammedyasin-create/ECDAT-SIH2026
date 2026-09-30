import React, { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
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
  const [mode, setMode] = useState<InputMode>("url");

  const [urlVal, setUrlVal] = useState("https://github.com/python/cpython");
  const [pathVal, setPathVal] = useState("test_corpus");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [pasteCode, setPasteCode] = useState("");
  const [pasteLang, setPasteLang] = useState<LangExt>("py");
  const [pasteFilename, setPasteFilename] = useState("snippet");

  const [scanning, setScanning] = useState(false);
  const [currentStage, setCurrentStage] = useState("IDLE");
  const [stageProgress, setStageProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) setUploadedFile(f);
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
      if (mode === "url") {
        promise = triggerScan({ path: urlVal, use_corpus: false });
      } else if (mode === "path") {
        const useCorpus = pathVal.trim() === "test_corpus";
        promise = triggerScan({ path: pathVal, use_corpus: useCorpus });
      } else if (mode === "upload") {
        if (!uploadedFile) throw new Error("No file selected. Please choose a file to upload.");
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
    if (mode === "path") return pathVal.trim().length > 0;
    if (mode === "upload") return uploadedFile !== null;
    return pasteCode.trim().length > 0;
  };

  const formatBytes = (b: number) =>
    b > 1024 * 1024 ? `${(b / (1024 * 1024)).toFixed(1)} MB` : `${(b / 1024).toFixed(1)} KB`;

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
          <Tab id="url"    icon="link"        label="URL / Git"   sub="GitHub or any git repo" />
          <Tab id="path"   icon="folder_open" label="Local Path"  sub="Directory on this machine" />
          <Tab id="upload" icon="upload_file" label="File Upload" sub=".py, .java, .zip, ..." />
          <Tab id="paste"  icon="code"        label="Paste Code"  sub="Inline source text" />
        </div>
      </section>

      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3">
        <div className="flex items-center gap-1.5 font-semibold text-sm text-primary border-b border-outline-variant pb-2">
          <span className="material-symbols-outlined text-base">
            {mode === "url" ? "link" : mode === "path" ? "folder_open" : mode === "upload" ? "upload_file" : "code"}
          </span>
          <span>
            {mode === "url" ? "2. Repository URL" : mode === "path" ? "2. Local Directory Path" : mode === "upload" ? "2. File Upload" : "2. Paste Source Code"}
          </span>
        </div>

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

        {mode === "path" && (
          <div className="space-y-3">
            <div>
              <label className="text-xs font-mono text-on-surface-variant block mb-1">Absolute or relative path to a directory on this machine</label>
              <input
                id="scan-path-input"
                type="text"
                value={pathVal}
                onChange={(e) => setPathVal(e.target.value)}
                disabled={scanning}
                placeholder="e.g. C:\Projects\MyApp or test_corpus"
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
              />
            </div>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[10px] font-mono text-outline">Quick presets:</span>
              <button
                type="button"
                onClick={() => setPathVal("test_corpus")}
                className={`px-2 py-0.5 rounded text-[10px] font-mono border transition-colors ${
                  pathVal === "test_corpus"
                    ? "bg-tertiary/20 text-tertiary border-tertiary font-bold"
                    : "bg-surface-container border-outline-variant text-on-surface-variant hover:text-on-surface"
                }`}
              >
                controlled test_corpus
              </button>
            </div>
            <p className="text-[11px] font-mono text-outline">Path traversal tokens (..) are blocked. System root directories are prohibited.</p>
          </div>
        )}

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
                <div className="text-center">
                  <p className="text-sm font-semibold text-on-surface">Drop a file here or <span className="text-primary underline">browse</span></p>
                  <p className="text-xs text-on-surface-variant mt-1">Accepts: .py, .java, .js, .ts, .c, .cpp, .go, .rs, .zip, .jar, .class, or any source file</p>
                  <p className="text-xs text-on-surface-variant">Max size: 500 MB (ZIP auto-extracted)</p>
                </div>
              )}
              <input
                id="scan-file-input"
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".py,.java,.js,.ts,.c,.cpp,.go,.rs,.zip,.jar,.class,.pem,.crt,.key,.txt"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) setUploadedFile(f); }}
              />
            </div>
            {uploadedFile && (
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono text-on-surface-variant flex-1">
                  Selected: <span className="text-primary">{uploadedFile.name}</span> ({formatBytes(uploadedFile.size)})
                </span>
                <button
                  type="button"
                  onClick={() => { setUploadedFile(null); if (fileInputRef.current) fileInputRef.current.value = ""; }}
                  className="text-[10px] font-mono text-error border border-error/40 px-2 py-0.5 rounded hover:bg-error/10 transition"
                >
                  Remove
                </button>
              </div>
            )}
            <p className="text-[11px] font-mono text-outline">ZIP archives are extracted in a secure sandbox. All temp files are purged after scan completes.</p>
          </div>
        )}

        {mode === "paste" && (
          <div className="space-y-3">
            <div className="flex gap-2 items-end flex-wrap">
              <div className="flex-1 min-w-40">
                <label className="text-xs font-mono text-on-surface-variant block mb-1">Filename (without extension)</label>
                <input
                  id="scan-paste-filename"
                  type="text"
                  value={pasteFilename}
                  onChange={(e) => setPasteFilename(e.target.value.replace(/[^a-zA-Z0-9_\-]/g, "_"))}
                  disabled={scanning}
                  placeholder="snippet"
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
                />
              </div>
              <div className="w-52">
                <label className="text-xs font-mono text-on-surface-variant block mb-1">Language / Extension</label>
                <select
                  id="scan-paste-lang"
                  value={pasteLang}
                  onChange={(e) => setPasteLang(e.target.value as LangExt)}
                  disabled={scanning}
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
                >
                  {LANG_EXTS.map((l) => <option key={l.ext} value={l.ext}>{l.label}</option>)}
                </select>
              </div>
              <div className="text-[11px] font-mono text-outline self-end pb-2">
                saved as <span className="text-primary">{pasteFilename || "snippet"}.{pasteLang}</span>
              </div>
            </div>
            <div>
              <label className="text-xs font-mono text-on-surface-variant block mb-1">
                Source code <span className="text-outline">(paste directly — no file needed)</span>
              </label>
              <textarea
                id="scan-paste-code"
                value={pasteCode}
                onChange={(e) => setPasteCode(e.target.value)}
                disabled={scanning}
                rows={16}
                spellCheck={false}
                placeholder={`# Paste your source code here\n# Example:\nfrom Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_CBC)\n\nfrom cryptography.hazmat.primitives.asymmetric import rsa\nprivate_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)`}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:outline-none focus:border-primary disabled:opacity-60 resize-y leading-relaxed"
              />
            </div>
            <div className="flex items-center justify-between text-[11px] font-mono text-outline">
              <span>{pasteCode.length.toLocaleString()} chars · {pasteCode.split("\n").length} lines</span>
              {pasteCode.length > 0 && (
                <button type="button" onClick={() => setPasteCode("")} className="text-error border border-error/40 px-2 py-0.5 rounded hover:bg-error/10 transition text-[10px]">
                  Clear
                </button>
              )}
            </div>
          </div>
        )}
      </section>

      <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3">
        <div className="flex items-center gap-1.5 font-semibold text-sm text-primary border-b border-outline-variant pb-2">
          <span className="material-symbols-outlined text-base">tune</span>
          <span>3. Active Cryptographic Discovery Collectors</span>
          <span className="ml-auto text-[11px] font-mono font-normal text-outline">All enabled</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 font-mono text-xs">
          {[
            { icon: "check_circle", label: "Source AST Scanner", desc: "Python & Java AST call-site visitor — key sizes, modes, algorithms" },
            { icon: "check_circle", label: "Manifest Dependency Scanner", desc: "requirements.txt, pom.xml, package.json, go.mod, Cargo.toml" },
            { icon: "check_circle", label: "Certificates & Public Keys", desc: "X.509 (PEM/DER), PKCS#12, OpenSSH keys — zero key persistence" },
            { icon: "check_circle", label: "Config & Cipher Suite Scanner", desc: "nginx.conf, sshd_config, openssl.cnf, Dockerfiles, TLS bounds" },
            { icon: "check_circle", label: "JVM Bytecode Scanner", desc: "Pure-Python JVM constant pool extractor (.class, .jar) + zip-slip safety" },
            { icon: "pending",       label: "Live Endpoints & Containers", desc: "Enterprise roadmap — MVP is air-gapped static analysis", dim: true },
          ].map((c) => (
            <div key={c.label} className={`p-3 bg-surface-container rounded border border-outline-variant flex items-start gap-2 ${(c as any).dim ? "opacity-50" : ""}`}>
              <span className={`material-symbols-outlined text-sm mt-0.5 ${(c as any).dim ? "text-outline" : "text-tertiary"}`}>{c.icon}</span>
              <div>
                <div className={`font-bold ${(c as any).dim ? "text-outline" : "text-on-surface"}`}>{c.label}</div>
                <div className="text-[11px] text-on-surface-variant mt-0.5">{c.desc}</div>
              </div>
            </div>
          ))}
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
          <div>
            <p className="text-error font-mono text-xs font-bold">Scan Failed</p>
            <p className="text-error/80 font-mono text-xs mt-0.5">{error}</p>
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

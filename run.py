"""
ECDAT — Enterprise Cryptographic Discovery & Analysis Tool
PS ID: 26164 | NTRO | SIH 2026

Unified Launcher:
Starts FastAPI Backend on http://localhost:8000
Starts React + TypeScript Stitch UI Frontend on http://localhost:5173
"""
import sys
import os
import subprocess
import time
import argparse
import webbrowser

def run_backend(port: int = 8000, reload: bool = True):
    cmd = [sys.executable, "-m", "uvicorn", "backend.api.main:app", "--host", "127.0.0.1", "--port", str(port)]
    if reload:
        cmd.append("--reload")
    return subprocess.Popen(cmd)

def run_frontend():
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    return subprocess.Popen([npm_cmd, "run", "dev"], cwd="frontend")

def main():
    parser = argparse.ArgumentParser(description="ECDAT Unified Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Launch FastAPI backend only")
    parser.add_argument("--frontend-only", action="store_true", help="Launch React frontend only")
    parser.add_argument("--port", type=int, default=8000, help="FastAPI port (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload on code change")
    args = parser.parse_args()

    procs = []
    print("=" * 65)
    print("  ECDAT Security Workstation — SIH 2026 // NTRO (PS ID: 26164)")
    print("  Enterprise Cryptographic Discovery & Analysis Tool")
    print("=" * 65)

    try:
        if not args.frontend_only:
            print(f"[*] Starting FastAPI Backend on http://127.0.0.1:{args.port}...")
            p_back = run_backend(port=args.port, reload=not args.no_reload)
            procs.append(p_back)

        if not args.backend_only:
            print("[*] Starting React + TypeScript Stitch UI Frontend on http://localhost:5173...")
            p_front = run_frontend()
            procs.append(p_front)

        time.sleep(2)
        print("\n[✓] ECDAT System Operational:")
        print(f"    • Backend API:      http://127.0.0.1:{args.port}")
        print(f"    • OpenAPI Docs:     http://127.0.0.1:{args.port}/docs")
        print("    • React Frontend:   http://localhost:5173")
        print("\nPress Ctrl+C to terminate all services.\n")

        if not args.no_browser and not args.backend_only:
            try:
                webbrowser.open("http://localhost:5173")
            except Exception:
                pass

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Shutting down ECDAT services...")
    finally:
        for p in procs:
            try:
                p.terminate()
                p.wait(timeout=3)
            except Exception:
                pass
        print("[✓] All services stopped.")

if __name__ == "__main__":
    main()

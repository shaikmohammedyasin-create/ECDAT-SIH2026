# ECDAT Deployment Guide (100% Production Ready)

**Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)**  
**Smart India Hackathon 2026 | PS ID: 26164 | NTRO**

---

## 🚀 Choose Your Deployment Strategy

| Method | Where It Runs | Best For | Time to Deploy |
| :--- | :--- | :--- | :--- |
| **Option 1 (Fastest & Free)** | **Frontend on Vercel** + **Backend on Render/Railway** | Cleanest split, global CDN frontend | ~5 minutes |
| **Option 2 (Easiest All-in-One)** | **Render / Railway Web Service** (Unified) | Single URL, no CORS setup | ~3 minutes |
| **Option 3 (Docker / VPS)** | **Any Docker host / AWS / DigitalOcean / EC2** | Air-gapped / Production / Government | ~2 minutes |
| **Option 4 (Local Offline)** | **Local Machine** (`python run.py`) | Hackathon jury demo & air-gapped evaluation | Instant |

---

## Option 1: Frontend on Vercel + Backend on Render (Recommended)

### Step 1: Deploy Backend on Render
1. Push this repository to your GitHub.
2. Go to [dashboard.render.com](https://dashboard.render.com/) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Click **Deploy Web Service**.
6. Copy your Render backend URL (e.g. `https://ecdat-backend.onrender.com`).
   - You can test it by visiting: `https://ecdat-backend.onrender.com/health`

### Step 2: Deploy Frontend on Vercel
1. Go to [vercel.com](https://vercel.com/) and click **Add New...** -> **Project**.
2. Select your GitHub repository.
3. In the configuration:
   - **Root Directory**: Select `frontend`
   - **Framework Preset**: `Vite` (auto-detected)
   - **Environment Variables**:
     - Key: `VITE_API_BASE_URL`
     - Value: `https://ecdat-backend.onrender.com/api` (use your actual Render backend URL)
4. Click **Deploy**.
5. Your ECDAT UI is live with full SPA routing (`vercel.json` is pre-configured).

---

## Option 2: All-in-One on Render or Railway

FastAPI is pre-configured to automatically serve the React frontend build when `frontend/dist` is present!

1. In Render, select **New +** -> **Web Service**.
2. Connect your repo and set:
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
     ```
3. Open your Render URL: You will get both the React UI at `/` and the FastAPI docs at `/docs` on the same domain with **zero CORS configuration needed**.

---

## Option 3: Docker Deployment (1-Command)

Run locally or on any cloud server:

```bash
# Build and run with Docker Compose
docker compose up -d --build

# Open in browser:
# http://localhost:8000
```

---

## Option 4: Local Evaluation / Presentation (For SIH Jury)

For the SIH Jury presentation (recommended for NTRO problem statement due to air-gap emphasis):

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Launch Unified System
python run.py
```
This automatically starts:
- FastAPI Backend: `http://127.0.0.1:8000` (API & Swagger Docs at `/docs`)
- React Stitch UI: `http://localhost:5173`
- Opens the browser automatically.

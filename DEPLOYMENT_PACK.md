# Humain DecisionOps - Complete Deployment Pack

> **Copy-paste playbook for VS Code users. No coding required.**

---

## Table of Contents
1. [Open VS Code](#1-open-vs-code)
2. [Run Locally with Docker](#2-run-locally-with-docker)
3. [Run Locally with Dev Mode](#3-run-locally-with-dev-mode)
4. [Pre-Deploy Checks](#4-pre-deploy-checks)
5. [Publish to GitHub from VS Code](#5-publish-to-github-from-vs-code)
6. [Vercel Deploy (Frontend)](#6-vercel-deploy-frontend)
7. [Backend Remote Setup](#7-backend-remote-setup)
8. [Troubleshooting](#8-troubleshooting)
9. [Acceptance Checklist](#9-acceptance-checklist)

---

## 1. Open VS Code

### Option A: From File Explorer
1. Navigate to `C:\Users\acer\humain-decisionops`
2. Right-click → **"Open with Code"**

### Option B: From Command Line
```bash
cd C:\Users\acer\humain-decisionops
code .
```

### Option C: From VS Code
1. Open VS Code
2. **File** → **Open Folder**
3. Select `C:\Users\acer\humain-decisionops`

---

## 2. Run Locally with Docker

### Prerequisites
- Docker Desktop installed and running

### Steps

#### Step 1: Open Terminal in VS Code
Press `Ctrl+`` (backtick) or **Terminal** → **New Terminal**

#### Step 2: Start All Services
```bash
docker compose up --build
```

#### Step 3: Wait for Services
Wait until you see:
```
humain-frontend  | ▲ Next.js 14.1.0
humain-frontend  |   - Local: http://localhost:3000
humain-backend   | INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Step 4: Open Browser
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050 (admin@humain.local / admin123)

#### Step 5: Stop Services
Press `Ctrl+C` in terminal, then:
```bash
docker compose down
```

### Using VS Code Tasks (GUI Method)
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select **"Docker: Up (Build)"**

---

## 3. Run Locally with Dev Mode

### Prerequisites
- Node.js 20+ installed
- Python 3.11+ installed
- PostgreSQL running (via Docker or local)

### Step 1: Start Database Only
```bash
docker compose up postgres -d
```

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Install Frontend Dependencies (New Terminal)
```bash
cd frontend
npm install
```

### Step 5: Start Frontend
```bash
cd frontend
npm run dev
```

### Using VS Code Tasks (GUI Method)
1. Press `Ctrl+Shift+P` → "Tasks: Run Task"
2. Run **"Backend: Dev"**
3. Run **"Frontend: Dev"** (in new terminal)

### Using VS Code Debugger (GUI Method)
1. Press `F5` or click **Run and Debug** in sidebar
2. Select **"Full Stack (Backend + Frontend)"**
3. Click green play button

---

## 4. Pre-Deploy Checks

### Check 1: Frontend Build
```bash
cd frontend
npm run build
```
✅ Should complete without errors

### Check 2: Backend Tests
```bash
cd backend
pytest -v
```
✅ All tests should pass

### Check 3: Docker Compose
```bash
docker compose up --build
```
✅ All services should start healthy

### Check 4: UI Verification
1. Open http://localhost:3000
2. Navigate to **Claims Inbox**
3. Click any claim → verify detail page loads
4. Check **Settings** page shows operating mode

---

## 5. Publish to GitHub from VS Code

### If Repository Already Exists
```bash
git add .
git commit -m "Deployment pack: VS Code tasks, env files, Vercel config"
git push origin master
```

### Using VS Code GUI
1. Click **Source Control** icon in sidebar (or `Ctrl+Shift+G`)
2. Stage all changes: Click **"+"** next to "Changes"
3. Enter commit message: `Deployment pack update`
4. Click **"✓ Commit"**
5. Click **"Sync Changes"** or **"Push"**

---

## 6. Vercel Deploy (Frontend)

### Step 1: Go to Vercel
Open https://vercel.com/new in your browser

### Step 2: Import Repository
1. Click **"Import Git Repository"**
2. Select **"PyBADR/humain-decisionops"**

### Step 3: Configure Project
| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework Preset** | Next.js |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |

### Step 4: Add Environment Variable
Click **"Environment Variables"** and add:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` |

> **Note:** Update this to your backend URL after deploying backend

### Step 5: Deploy
Click **"Deploy"** button

### Step 6: Wait for Build
Build takes ~2-3 minutes. You'll see:
- ✅ Building
- ✅ Deploying
- ✅ Ready

### Step 7: Get Your URL
Your app is live at: `https://humain-decisionops-xxxxx.vercel.app`

---

## 7. Backend Remote Setup

### Step 1: Create Neon Database (Free Tier)
1. Go to https://neon.tech and sign up
2. Click **"Create Project"**
3. Project name: `humain-decisionops`
4. Click **"Create Project"**
5. Copy the connection string (starts with `postgresql://...`)

### Step 2: Initialize Database
1. In Neon Console, click **"SQL Editor"**
2. Copy contents of `infra/postgres/01-init.sql` → Paste → Run
3. Copy contents of `infra/postgres/02-seed.sql` → Paste → Run
4. Verify: `SELECT COUNT(*) FROM claims;` should return 12

### Step 3: Deploy Backend on Render (Free Tier)
1. Go to https://render.com
2. **New** → **Web Service**
3. Connect GitHub repo: `PyBADR/humain-decisionops`
4. Configure:
   - **Name:** `humain-decisionops-api`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   ```
   DATABASE_URL=<your-neon-connection-string>
   CORS_ALLOW_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   HEURISTIC_MODE=true
   AUTH_ENABLED=false
   ```
6. Click **"Create Web Service"**
7. Wait 2-5 minutes for deployment
8. Copy your Render URL (e.g., `https://humain-decisionops-api.onrender.com`)

### Step 4: Verify Backend
```bash
curl https://your-backend.onrender.com/health
# Expected: {"status":"healthy","database":"connected",...}

curl https://your-backend.onrender.com/api/claims
# Expected: JSON array with 12 claims
```

### Option B: Fly.io
```bash
cd backend
fly launch
fly secrets set DATABASE_URL=<your-postgres-url>
fly secrets set CORS_ALLOW_ORIGINS=https://your-app.vercel.app
fly secrets set HEURISTIC_MODE=true
fly deploy
```

### After Backend is Deployed
Update Vercel environment variable:
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` to your backend URL
3. Redeploy

---

## 8. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **Port 3000 in use** | Another app using port | `npx kill-port 3000` or change port |
| **Port 8000 in use** | Another app using port | `npx kill-port 8000` or change port |
| **Docker not starting** | Docker Desktop not running | Start Docker Desktop |
| **Database connection failed** | Postgres not running | `docker compose up postgres -d` |
| **CORS errors in browser** | Backend CORS misconfigured | Check `CORS_ALLOW_ORIGINS` includes frontend URL |
| **API calls return 404** | Wrong API URL | Check `NEXT_PUBLIC_API_URL` in `.env.local` |
| **Build fails on Vercel** | Wrong root directory | Set Root Directory to `frontend` |
| **"cd frontend" error on Vercel** | Old vercel.json | Update vercel.json (already fixed) |
| **Claims not loading** | Backend not running | Start backend or check API URL |
| **Empty database** | Seed not run | Run seed.sql or restart Docker |

### Quick Fixes

#### Reset Everything
```bash
docker compose down -v
docker compose up --build
```

#### Check Service Health
```bash
curl http://localhost:8000/health
```

#### View Logs
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

## 9. Acceptance Checklist

Run through this checklist to verify everything works:

### Local Development
- [ ] `docker compose up --build` starts all services
- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API docs at http://localhost:8000/docs
- [ ] Claims Inbox shows 12 seeded claims
- [ ] Claim Detail page loads with all tabs
- [ ] Settings page shows operating mode (OLLAMA/Heuristic)
- [ ] Run Pipeline button triggers decision
- [ ] Audit events appear in Governance page

### Build Verification
- [ ] `cd frontend && npm run build` succeeds
- [ ] `cd backend && pytest -v` passes all tests

### Vercel Deployment
- [ ] Repository imported successfully
- [ ] Root Directory set to `frontend`
- [ ] `NEXT_PUBLIC_API_URL` environment variable set
- [ ] Build completes without errors
- [ ] Live URL accessible

### Backend Deployment (if applicable)
- [ ] Backend deployed to Render/Fly
- [ ] `CORS_ALLOW_ORIGINS` includes Vercel URL
- [ ] `/health` endpoint returns OK
- [ ] Frontend can fetch claims from remote backend

---

## Environment Variables Reference

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql+psycopg://humain:humain_secret@localhost:5432/humain_decisionops
CORS_ALLOW_ORIGINS=http://localhost:3000
HEURISTIC_MODE=true
```

### Vercel (Production)
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Render/Fly (Production)
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
CORS_ALLOW_ORIGINS=https://your-app.vercel.app
HEURISTIC_MODE=true
```

---

## Quick Commands Reference

| Action | Command |
|--------|---------|
| Start all (Docker) | `docker compose up --build` |
| Stop all (Docker) | `docker compose down` |
| Reset database | `docker compose down -v && docker compose up --build` |
| Frontend dev | `cd frontend && npm run dev` |
| Backend dev | `cd backend && uvicorn app.main:app --reload` |
| Run tests | `cd backend && pytest -v` |
| Build frontend | `cd frontend && npm run build` |
| Push to GitHub | `git add . && git commit -m "update" && git push` |

---

**🎉 You're all set! The Humain DecisionOps Console is ready for deployment.**

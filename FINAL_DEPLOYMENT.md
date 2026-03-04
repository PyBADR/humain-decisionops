# HUMAIN DecisionOps - Final Deployment Guide

## Project Complete ✅

This is a production-ready Decision Intelligence Platform for insurance operations.

---

## Quick Start (Local)

```bash
cd C:\Users\acer\humain-decisionops
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Railway Deployment (Recommended)

### Step 1: Push to GitHub

```bash
cd C:\Users\acer\humain-decisionops
git add .
git commit -m "Railway deployment ready"
git push origin master
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `PyBADR/humain-decisionops`

### Step 3: Add PostgreSQL

1. Click **+ New** → **Database** → **PostgreSQL**
2. Railway provisions the database automatically

### Step 4: Deploy Backend

1. Click **+ New** → **GitHub Repo** → `PyBADR/humain-decisionops`
2. Set **Root Directory**: `backend`
3. Add environment variables:
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
   - `CORS_ALLOW_ORIGINS` = `*` (update after frontend deploys)
   - `HEURISTIC_MODE` = `true`
   - `SEED_ON_STARTUP` = `true`

### Step 5: Deploy Frontend

1. Click **+ New** → **GitHub Repo** → `PyBADR/humain-decisionops`
2. Set **Root Directory**: `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://<backend-url>.railway.app`

### Step 6: Update CORS

After frontend deploys, update backend:
- `CORS_ALLOW_ORIGINS` = `https://<frontend-url>.railway.app`

---

## Verification Checklist

| Check | Expected |
|-------|----------|
| `/health` | `{"status": "healthy"}` |
| `/api/claims` | 12 claims returned |
| Frontend loads | Dashboard visible |
| Claims Inbox | Table with claims |
| Claim Detail | Decision + Audit tabs work |

---

## Architecture

```
User → Next.js (Vercel/Railway) → FastAPI (Render/Railway) → PostgreSQL (Neon/Railway)
```

## Features

- ✅ 12 seeded claims with various statuses
- ✅ 12 fraud detection scenarios
- ✅ Decision pipeline with heuristic mode
- ✅ Full audit trail
- ✅ Dark-themed professional UI
- ✅ 10 dashboard pages

---

## GitHub Repository

https://github.com/PyBADR/humain-decisionops

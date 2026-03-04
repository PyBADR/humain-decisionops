# HUMAIN DecisionOps - Railway Deployment Guide

## Architecture

```
User → Railway Frontend (Next.js) → Railway Backend (FastAPI) → Railway PostgreSQL
```

## Prerequisites

- GitHub account with repo: `PyBADR/humain-decisionops`
- Railway account (free tier available)

---

## Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **Start a New Project**
3. Select **Deploy from GitHub repo**
4. Connect your GitHub account if not already connected
5. Select `PyBADR/humain-decisionops`

---

## Step 2: Add PostgreSQL Database

1. In your Railway project, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway will provision a PostgreSQL instance
4. Click on the PostgreSQL service to see connection details
5. Copy the `DATABASE_URL` (you'll need this)

---

## Step 3: Deploy Backend Service

1. Click **+ New** → **GitHub Repo**
2. Select `PyBADR/humain-decisionops`
3. Configure the service:
   - **Name**: `humain-backend`
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile.backend` (or leave empty to use Nixpacks)

4. Add Environment Variables:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   CORS_ALLOW_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}
   HEURISTIC_MODE=true
   SEED_ON_STARTUP=true
   PORT=8000
   ```

5. Click **Deploy**

6. After deployment, note the public URL (e.g., `humain-backend-production.up.railway.app`)

---

## Step 4: Deploy Frontend Service

1. Click **+ New** → **GitHub Repo**
2. Select `PyBADR/humain-decisionops`
3. Configure the service:
   - **Name**: `humain-frontend`
   - **Root Directory**: `frontend`

4. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://humain-backend-production.up.railway.app
   PORT=3000
   ```

5. Click **Deploy**

---

## Step 5: Update CORS (After Frontend Deploys)

1. Get your frontend URL from Railway (e.g., `humain-frontend-production.up.railway.app`)
2. Go to Backend service → Variables
3. Update `CORS_ALLOW_ORIGINS`:
   ```
   CORS_ALLOW_ORIGINS=https://humain-frontend-production.up.railway.app
   ```
4. Redeploy backend

---

## Step 6: Initialize Database

Option A: Automatic Seed (Recommended)
- Set `SEED_ON_STARTUP=true` on backend
- Restart backend service
- Set `SEED_ON_STARTUP=false` after first run

Option B: Manual SQL
1. Go to PostgreSQL service in Railway
2. Click **Data** tab
3. Open **Query** editor
4. Paste contents of `infra/postgres/01-init.sql`
5. Execute
6. Paste contents of `infra/postgres/02-seed.sql`
7. Execute

---

## Verification Checklist

| Check | URL | Expected |
|-------|-----|----------|
| Backend Health | `https://<backend>/health` | `{"status": "healthy"}` |
| API Docs | `https://<backend>/docs` | Swagger UI loads |
| Claims API | `https://<backend>/api/claims` | 10+ claims returned |
| Frontend | `https://<frontend>` | Dashboard loads |
| Claims Inbox | `https://<frontend>/claims` | Claims table visible |
| Claim Detail | `https://<frontend>/claims/CLM-001` | Claim details load |

---

## Troubleshooting

### Frontend shows "Failed to fetch" or blank data
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS is configured on backend
- Check backend is running (visit /health)

### Database connection failed
- Verify `DATABASE_URL` is set from Railway PostgreSQL
- Check PostgreSQL service is running

### Backend returns empty claims
- Run seed SQL or set `SEED_ON_STARTUP=true`
- Check database tables exist

### Build fails
- Check logs in Railway dashboard
- Ensure all dependencies are in requirements.txt / package.json

---

## Environment Variables Reference

### Backend
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| CORS_ALLOW_ORIGINS | Yes | Frontend URL for CORS |
| HEURISTIC_MODE | No | `true` to run without LLM |
| SEED_ON_STARTUP | No | `true` to seed DB on start |
| PORT | No | Default 8000 |

### Frontend
| Variable | Required | Description |
|----------|----------|-------------|
| NEXT_PUBLIC_API_URL | Yes | Backend API URL |
| PORT | No | Default 3000 |

---

## Final URLs

After successful deployment:

- **Frontend Dashboard**: `https://humain-frontend-production.up.railway.app`
- **Backend API**: `https://humain-backend-production.up.railway.app`
- **API Documentation**: `https://humain-backend-production.up.railway.app/docs`

---

## Cost (Railway Free Tier)

- $5/month credit (free)
- Covers small projects
- PostgreSQL included
- No credit card required to start

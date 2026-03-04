# Vercel Deployment Guide (Quick)

## Prerequisites
- GitHub repository: `PyBADR/humain-decisionops`
- Vercel account (free tier works)

## Steps

### 1. Import Repository
1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select `PyBADR/humain-decisionops`

### 2. Configure Project
| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework Preset** | Next.js (auto-detected) |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Install Command** | `npm install` |

### 3. Environment Variables
Add this environment variable:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-url.onrender.com` |

> **Note:** Replace with your actual backend URL. For demo/local testing, use `http://localhost:8000`

### 4. Deploy
Click **"Deploy"** and wait for build to complete.

## Post-Deployment

### Your URLs
- **Frontend:** `https://humain-decisionops.vercel.app` (or custom domain)
- **Backend:** Your Render/Fly backend URL

### Update Backend CORS
Ensure your backend's `CORS_ALLOW_ORIGINS` includes your Vercel URL:
```
CORS_ALLOW_ORIGINS=https://humain-decisionops.vercel.app
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails with "cd frontend" error | Ensure Root Directory is set to `frontend` |
| API calls fail | Check `NEXT_PUBLIC_API_URL` is set correctly |
| CORS errors | Update backend `CORS_ALLOW_ORIGINS` |
| 404 on pages | Ensure Next.js framework is detected |

## Redeploy
To redeploy after changes:
1. Push to GitHub
2. Vercel auto-deploys on push to main/master

Or manually:
1. Go to Vercel dashboard
2. Click **"Redeploy"**

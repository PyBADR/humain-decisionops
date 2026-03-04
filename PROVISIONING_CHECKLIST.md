# Provisioning Checklist - Humain DecisionOps

Use this checklist to troubleshoot GitHub - Vercel - Render connection issues.

## Pre-Deployment Checks

### GitHub Repository
- [ ] Repository is public OR Vercel/Render have access
- [ ] All files committed and pushed to `main` or `master`
- [ ] No sensitive data in committed files

### Environment Variables
| Service | Variable | Example Value |
|---------|----------|---------------|
| Vercel | `NEXT_PUBLIC_API_URL` | `https://humain-api.onrender.com` |
| Render | `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` |
| Render | `CORS_ALLOW_ORIGINS` | `https://humain-decisionops.vercel.app` |
| Render | `HEURISTIC_MODE` | `true` |

## Common Issues & Fixes

### Issue: Vercel Build Fails - "No such file or directory"
**Cause:** Root directory not set correctly
**Fix:**
1. Go to Vercel Project Settings > General
2. Set Root Directory = `frontend`
3. Redeploy

### Issue: Vercel Shows Blank Page
**Cause:** API URL not set or pointing to localhost
**Fix:**
1. Go to Vercel Project Settings > Environment Variables
2. Add `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
3. Redeploy

### Issue: CORS Errors
**Cause:** Backend CORS not configured
**Fix:**
1. Go to Render Dashboard > Your Service > Environment
2. Set `CORS_ALLOW_ORIGINS` = `https://your-app.vercel.app`
3. Redeploy backend

### Issue: Render Backend Returns 500
**Cause:** Database connection failed
**Fix:**
1. Verify `DATABASE_URL` is correct
2. Ensure Neon database is active
3. Check connection string includes `?sslmode=require`

### Issue: First Request Slow (30+ seconds)
**Cause:** Free tier spins down after inactivity
**Fix:** Expected behavior. First request wakes the service.

## Verification Commands

```bash
# Backend Health
curl https://your-backend.onrender.com/health

# Claims API
curl https://your-backend.onrender.com/api/claims
```

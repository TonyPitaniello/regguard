# RegGuard Production Deployment - Quick Start

## What Has Been Done

✅ Created `render.yaml` - Backend infrastructure configuration
✅ Added `gunicorn` to `backend/requirements.txt` - Production ASGI server
✅ Created `DEPLOYMENT.md` - Comprehensive 200+ line deployment guide
✅ Committed all changes to branch `cursor/regguard-production-deployment-81a2`
✅ Created PR #1 on GitHub

## Next Steps (Manual Actions Required)

### 1. Deploy Backend to Render

**Prerequisites:**
- Create free account at [render.com](https://render.com)
- Have all production secrets ready

**Steps:**
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the RegGuard repository
5. Configure with these settings:
   - Name: `regguard-backend`
   - Environment: `Python 3`
   - Root Directory: `backend/`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 300 --access-logfile -`
6. Add all environment variables from DEPLOYMENT.md (Backend section)
7. Click "Create Web Service"
8. Wait 5-10 minutes for deployment
9. Note the backend URL: `https://regguard-backend.onrender.com`

**Verify:**
```bash
curl https://regguard-backend.onrender.com/health
```

### 2. Deploy Frontend to Vercel

**Prerequisites:**
- Create free account at [vercel.com](https://vercel.com)
- Have backend URL from Step 1

**Steps:**
1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Click "Import Git Repository"
4. Search for and select RegGuard repository
5. Configure with these settings:
   - Project Name: `regguard`
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm install --legacy-peer-deps && npm run build`
   - Output Directory: `dist`
6. Add environment variables:
   - `VITE_BACKEND_ORIGIN`: `https://regguard-backend.onrender.com` (from Step 1)
   - `VITE_STRIPE_PUBLIC_KEY`: Your Stripe public key
   - `VITE_GOOGLE_MAPS_API_KEY`: Your Google Maps API key
7. Click "Deploy"
8. Wait 2-5 minutes for deployment
9. Note the frontend URL: `https://regguard.vercel.app`

**Verify:**
1. Open https://regguard.vercel.app in browser
2. Check browser DevTools (F12) for errors
3. Try making an API request to verify backend connectivity

### 3. Test End-to-End

```bash
# Test backend health
curl https://regguard-backend.onrender.com/health

# Test frontend loads
curl -I https://regguard.vercel.app
```

In browser:
1. Open https://regguard.vercel.app
2. Open DevTools (F12)
3. Go to Network tab
4. Interact with app (sign up, make API request)
5. Verify API calls to backend succeed (200 status)

## Critical Configuration Points

### Backend Environment Variables

**Must-have for functionality:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=sb_publishable_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
FIRECRAWL_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
GOOGLE_MAPS_API_KEY=AIzaSy...
RESEND_FROM_EMAIL=noreply@regguardagent.com
```

### Frontend Environment Variables

**Must-have:**
```
VITE_BACKEND_ORIGIN=https://regguard-backend.onrender.com
VITE_STRIPE_PUBLIC_KEY=pk_live_...
VITE_GOOGLE_MAPS_API_KEY=AIzaSy...
```

## Files Modified/Created

| File | Type | Purpose |
|------|------|---------|
| `render.yaml` | NEW | Render backend configuration |
| `backend/requirements.txt` | MODIFIED | Added gunicorn |
| `DEPLOYMENT.md` | NEW | Complete deployment guide |
| `vercel.json` | EXISTING | Frontend build config (already correct) |
| `.vercelignore` | EXISTING | Ignore Python backend for Vercel |

## Deployed URLs (After Following Steps Above)

- **Frontend**: https://regguard.vercel.app
- **Backend API**: https://regguard-backend.onrender.com
- **Backend Health**: https://regguard-backend.onrender.com/health

## Important Notes

1. **Auto-deploy**: Both Render and Vercel are configured to auto-deploy when you push to `main` branch
2. **Cold starts**: Render free tier may experience 50s+ cold starts after inactivity
3. **Costs**: Both free tiers are suitable for production; upgrade as needed
4. **Secrets**: Never commit `.env` files; only commit `.env.example`
5. **CORS**: Already configured in FastAPI for production domains

## Troubleshooting

**If backend doesn't start:**
- Check Render logs: Dashboard → Web Service → Logs
- Verify all environment variables are set
- Clear build cache and redeploy

**If frontend can't reach backend:**
- Verify `VITE_BACKEND_ORIGIN` is set correctly on Vercel
- Check backend health endpoint
- Check browser console for CORS errors

**If build fails:**
- Check Vercel/Render logs for build errors
- Verify Node/Python versions
- Clear cache and retry

## See Also

- **Full Documentation**: See `DEPLOYMENT.md` for 200+ line guide
- **Backend Config**: See `render.yaml` for infrastructure-as-code
- **Frontend Config**: See `vercel.json` and `vite.config.ts`
- **PR**: https://github.com/TonyPitaniello/regguard/pull/1

---

**Status**: Ready for production deployment
**Last Updated**: July 26, 2026

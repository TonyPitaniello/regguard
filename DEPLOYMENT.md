# RegGuard Production Deployment Guide

This document provides step-by-step instructions for deploying RegGuard to production across Render (backend) and Vercel (frontend).

## Overview

- **Backend**: FastAPI deployed to Render.com
- **Frontend**: Vite/React deployed to Vercel
- **Database**: Supabase PostgreSQL
- **Payments**: Stripe
- **Web Scraping**: Firecrawl API

## Prerequisites

1. **Render Account**: [render.com](https://render.com) - Free tier available
2. **Vercel Account**: [vercel.com](https://vercel.com) - Free tier available
3. **GitHub Account**: Repository must be on GitHub for CI/CD
4. **Production Secrets** available:
   - STRIPE_SECRET_KEY
   - STRIPE_PUBLISHABLE_KEY
   - STRIPE_WEBHOOK_SECRET
   - SUPABASE_URL
   - SUPABASE_KEY
   - FIRECRAWL_API_KEY
   - ANTHROPIC_API_KEY
   - GEMINI_API_KEY
   - GOOGLE_MAPS_API_KEY
   - RESEND_FROM_EMAIL (for transactional emails)
   - SENTRY_DSN (optional, for error tracking)

---

## Part 1: Backend Deployment (Render)

### Step 1: Create Render Account and Connect GitHub

1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect a repository"**
4. Search for your RegGuard repository and connect it
5. Choose the repository and click **"Connect"**

### Step 2: Configure Web Service

When creating the Web Service, use the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `regguard-backend` |
| **Environment** | `Python 3` |
| **Region** | Select closest to your users |
| **Branch** | `main` |
| **Root Directory** | `backend/` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 300 --access-logfile -` |

### Step 3: Configure Environment Variables

In Render dashboard, add the following environment variables:

```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
BACKEND_URL=https://regguard-backend.onrender.com
FRONTEND_URL=https://regguard.vercel.app
FRONTEND_APP_URL=https://regguard.vercel.app
RESEND_FROM_EMAIL=noreply@regguardagent.com

# Production Secrets (from your secret management system)
STRIPE_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXX
STRIPE_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXX
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=sb_publishable_XXXXXXXXXXXXXXXXXXXX
FIRECRAWL_API_KEY=XXXXXXXXXXXXXXXXXXXX
ANTHROPIC_API_KEY=XXXXXXXXXXXXXXXXXXXX
GEMINI_API_KEY=XXXXXXXXXXXXXXXXXXXX
GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX
SENTRY_DSN=https://your-sentry-key@o123456.ingest.sentry.io/123456 (optional)
```

### Step 4: Deploy Backend

1. Click **"Create Web Service"** to start the deployment
2. Render will automatically build and deploy your backend
3. Wait for the build to complete (typically 5-10 minutes)
4. Once deployed, note the URL: `https://regguard-backend.onrender.com`

### Step 5: Verify Backend

Test the backend deployment:

```bash
# Test health endpoint
curl https://regguard-backend.onrender.com/health

# Expected response:
# {"status":"ok","message":"API service running"}
```

If the health check returns a 200 status, your backend is successfully deployed.

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Create Vercel Account and Connect GitHub

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click **"Add New"** → **"Project"**
3. Click **"Import Git Repository"**
4. Search for your RegGuard repository and select it
5. Click **"Import"**

### Step 2: Configure Project Settings

When importing the project, configure:

| Setting | Value |
|---------|-------|
| **Project Name** | `regguard` |
| **Framework Preset** | `Vite` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install --legacy-peer-deps && npm run build` |
| **Output Directory** | `dist` |
| **Node.js Version** | `20.x` (or latest LTS) |

### Step 3: Configure Environment Variables

In Vercel dashboard, add the following environment variables:

```
VITE_BACKEND_ORIGIN=https://regguard-backend.onrender.com
VITE_STRIPE_PUBLIC_KEY=pk_live_XXXXXXXXXXXXXXXXXXXX
VITE_GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX
```

**Important**: 
- Set these as **Production** environment variables
- The `VITE_BACKEND_ORIGIN` must match your Render backend URL

### Step 4: Deploy Frontend

1. Click **"Deploy"** to start the deployment
2. Vercel will automatically build and deploy your frontend
3. Wait for the deployment to complete (typically 2-5 minutes)
4. Once deployed, your frontend will be accessible at `https://regguard.vercel.app` (or your custom domain)

### Step 5: Verify Frontend

1. Navigate to `https://regguard.vercel.app` in your browser
2. The application should load without errors
3. Check browser console for any errors

---

## Part 3: End-to-End Testing

### Test 1: Frontend Loads

```bash
curl -I https://regguard.vercel.app
# Should return 200 OK
```

### Test 2: Backend Health Check

```bash
curl https://regguard-backend.onrender.com/health
# Should return: {"status":"ok","message":"API service running"}
```

### Test 3: Frontend → Backend Communication

1. Open `https://regguard.vercel.app` in browser
2. Open Developer Tools (F12)
3. Go to **Network** tab
4. Try to interact with the app (e.g., sign up, make a request)
5. Verify that API calls to `https://regguard-backend.onrender.com/*` succeed (200 status)

### Test 4: Stripe Integration (if applicable)

If you have Stripe keys configured:
1. Test the checkout flow
2. Verify that Stripe redirects work correctly

---

## Deployment Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────┐
        │   https://regguard.vercel.app   │
        │     (Vite/React Frontend)       │
        │      Hosted on Vercel           │
        └──────────────┬────────────────┬─┘
                       │                │
         VITE_BACKEND_ORIGIN            │ Static Assets
         API Requests  │                │ (JS, CSS, HTML)
                       ▼                ▼
        ┌────────────────────────────────────┐
        │ https://regguard-backend.onrender  │
        │      (FastAPI Backend)             │
        │      Hosted on Render              │
        └──────────────┬────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐  ┌──────────┐  ┌────────────┐
    │Supabase│  │ Stripe   │  │ Firecrawl  │
    │(DB)    │  │(Payments)│  │(Web Search)│
    └────────┘  └──────────┘  └────────────┘
```

---

## Environment Variables Summary

### Backend (Render)

**Application URLs:**
- `BACKEND_URL` - URL where backend is deployed
- `FRONTEND_URL` - URL where frontend is deployed
- `FRONTEND_APP_URL` - URL for app-specific features

**Database & Payments:**
- `SUPABASE_URL` - PostgreSQL database URL
- `SUPABASE_KEY` - Database authentication key
- `STRIPE_SECRET_KEY` - Stripe secret for server-side
- `STRIPE_PUBLISHABLE_KEY` - Stripe public key
- `STRIPE_WEBHOOK_SECRET` - Webhook secret for Stripe events

**Third-party APIs:**
- `FIRECRAWL_API_KEY` - Web scraping/search API
- `ANTHROPIC_API_KEY` - Claude LLM API
- `GEMINI_API_KEY` - Google Gemini API
- `GOOGLE_MAPS_API_KEY` - Google Maps API

**Email & Error Tracking:**
- `RESEND_FROM_EMAIL` - Email sender address
- `SENTRY_DSN` - Error tracking (optional)

**Server Configuration:**
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=info`

### Frontend (Vercel)

**Backend Connection:**
- `VITE_BACKEND_ORIGIN=https://regguard-backend.onrender.com`

**Stripe:**
- `VITE_STRIPE_PUBLIC_KEY=pk_live_...`

**Maps:**
- `VITE_GOOGLE_MAPS_API_KEY=AIzaSy...`

---

## Monitoring & Updates

### Monitoring Backend

1. **Render Dashboard**: Monitor logs and uptime
   - Navigate to your web service on render.com
   - Click **"Logs"** to view real-time logs
   - Check **"Metrics"** for CPU, memory, bandwidth

2. **Health Check**:
   ```bash
   curl https://regguard-backend.onrender.com/health
   ```

### Monitoring Frontend

1. **Vercel Dashboard**: Monitor deployments and logs
   - Check deployment logs in vercel.com dashboard
   - View analytics and performance metrics

2. **Browser DevTools**: Monitor API calls and errors
   - Open developer tools in browser
   - Check Network tab for failed requests
   - Check Console for JavaScript errors

### Automatic Deploys

**Render**: Automatically redeploys when you push to the `main` branch
**Vercel**: Automatically redeploys when you push to the `main` branch

To disable auto-deploy:
- **Render**: Settings → Auto-deploy → Disable
- **Vercel**: Project Settings → Git → Toggle "Deployments"

---

## Troubleshooting

### Backend Won't Start

1. Check Render logs for errors:
   - Render dashboard → Web Service → Logs

2. Common issues:
   - Missing environment variables
   - Python dependency conflicts
   - Port not properly bound

3. Solutions:
   - Verify all required environment variables are set
   - Clear build cache: Render dashboard → Settings → Clear build cache
   - Retry deployment

### Frontend Not Loading

1. Check Vercel logs:
   - Vercel dashboard → Deployments → View build logs

2. Check browser console for errors (F12)

3. Common issues:
   - Build command failed
   - Missing npm dependencies
   - Environment variables not set

### Frontend Can't Reach Backend

1. Verify `VITE_BACKEND_ORIGIN` is set correctly on Vercel
2. Check backend health: `curl https://regguard-backend.onrender.com/health`
3. Check CORS configuration in backend
4. Verify firewall/network settings

### API Calls Return 500 Error

1. Check Render backend logs
2. Verify all backend environment variables are set
3. Check database connectivity (Supabase)
4. Check API quota limits (Stripe, Firecrawl, etc.)

---

## Cost Estimation

### Render (Backend)

- **Free Tier**: ~4 free instances, 0.5 GB RAM each
  - Suitable for low-traffic development
  - Spins down after 15 min of inactivity
  
- **Paid Tier**: $7/month - $100+/month
  - Recommended for production
  - Always-on instances with more resources

### Vercel (Frontend)

- **Free Tier**: Unlimited deployments, included analytics
  - Suitable for production
  - No overages for static sites
  
- **Pro**: $20/month
  - Analytics dashboard
  - Team collaboration

---

## Next Steps

1. **Custom Domain**: Point your domain to Vercel/Render
2. **SSL/TLS**: Already enabled on both platforms
3. **Analytics**: Set up Vercel Analytics for performance monitoring
4. **Monitoring**: Configure alerts for uptime/errors
5. **Backups**: Configure automated backups for Supabase database

---

## Quick Links

- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Supabase Console**: https://supabase.com/dashboard
- **Stripe Dashboard**: https://dashboard.stripe.com
- **Firecrawl Docs**: https://docs.firecrawl.dev

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Vite Docs**: https://vitejs.dev
- **Supabase Docs**: https://supabase.com/docs

---

Last Updated: July 26, 2026

# 🚀 RENDER BACKEND DEPLOYMENT FIX

## Current Status: Build Failing

**Error**: `Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`

**Root Cause**: Render is looking for `requirements.txt` in the root, but it's in `backend/`

---

## IMMEDIATE ACTION - 5 Minutes

### 1. Update Render Build Command

**Go to**: https://dashboard.render.com/
- Select service: `regguard-api`
- Click: **Settings**
- Find: **Build Command** field
- **DELETE** whatever is there
- **PASTE THIS EXACTLY**:

```bash
pip install --no-cache-dir -r backend/requirements.txt
```

### 2. Verify Render Start Command

**In the same Settings page**:
- Find: **Start Command** field
- **PASTE THIS EXACTLY**:

```bash
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3. Save & Deploy

- Click: **Save**
- Render auto-redeploys
- Wait 2-3 minutes for build
- Check **Logs** for success

---

## Verify All Environment Variables Are Set

**Still in Render Settings**:
1. Go to: **Environment** tab
2. Scroll through and verify EVERY one of these exists:

| Variable | Required | Status |
|----------|----------|--------|
| `GOOGLE_MAPS_API_KEY` | ✅ YES | (rotated) |
| `GEMINI_API_KEY` | ✅ YES | (rotated) |
| `STRIPE_SECRET_KEY` | ✅ YES | (rotated) |
| `STRIPE_WEBHOOK_SECRET` | ✅ YES | (rotated) |
| `SUPABASE_KEY` | ✅ YES | (service role) |
| `RESEND_FROM_EMAIL` | ✅ YES | noreply@regguardagent.com |
| `STRIPE_PUBLISHABLE_KEY` | ✅ YES | pk_live_... |
| `SUPABASE_URL` | ✅ YES | https://cukshjdvlydzxiqnjdaw.supabase.co |

**If any are EMPTY or MISSING**:
- Click the variable
- Fill in the value
- Save

---

## Vercel Frontend Setup

**Go to**: https://vercel.com/
- Select: `regguard-live`
- Settings → Environment Variables

Verify these exist (with `VITE_` prefix):

| Variable | Value |
|----------|-------|
| `VITE_STRIPE_PUBLIC_KEY` | pk_live_51TORV3L2e16brS4iF2IdyAQw6... |
| `VITE_SUPABASE_ANON_KEY` | sb_anon_... or sb_publishable_... |
| `VITE_GOOGLE_MAPS_API_KEY` | AIzaSy... |
| `VITE_BACKEND_ORIGIN` | https://regguard-api.onrender.com |

If added/changed:
- Click: **Redeploy**
- Wait for Vercel to rebuild

---

## Verify Deployment Success

### Check Render Backend

```bash
curl https://regguard-api.onrender.com/health
```

Should return: `{"status":"ok"}`

### Check Vercel Frontend

Visit: https://regguard-live.vercel.app

Should load without errors

### Check Free Trial

1. Go to free trial form
2. Submit test data
3. Check email for research memo
4. No errors in browser console

---

## If Still Failing

### Render Logs

1. Go to Render: regguard-api service
2. Click: **Logs**
3. Look for RED ERROR lines
4. Common errors:
   - `ModuleNotFoundError` = missing dependency in requirements.txt
   - `ImportError` = wrong Python version
   - `Environment variable not set` = missing API key

### Vercel Logs

1. Go to Vercel: regguard-live project
2. Click: **Deployments**
3. Latest deployment → **Logs**
4. Look for BUILD ERRORS or ERRORS

---

## Security Checklist ✅

- [x] Google Maps API Key rotated
- [x] Stripe Secret Key rotated
- [x] Stripe Webhook Secret rotated
- [x] Supabase Key (Service Role) in Render
- [x] Supabase Anon Key in Vercel
- [x] Gemini API Key rotated
- [x] `.env` removed from git
- [x] Supabase RLS enabled
- [x] All new keys in deployment services

---

## Success Indicators

✅ Render build completes without errors
✅ Vercel deployment completes without errors
✅ Backend /health endpoint returns 200
✅ Frontend loads without console errors
✅ Free trial form submits successfully
✅ Email received with research memo
✅ No "undefined" or API key errors

---

## Next Steps After Deployment

1. Test free trial end-to-end
2. Monitor Sentry for errors
3. Check Render logs for warnings
4. Verify all API integrations work
5. Test Stripe webhook delivery

Done! ✅

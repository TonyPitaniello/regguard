# 🎯 MASTER DEPLOYMENT CHECKLIST - EVERYTHING IN ONE PLACE

## PHASE 1: RENDER BACKEND FIX (10 minutes)

### A. Update Build & Start Commands

- [ ] Go to: https://dashboard.render.com/
- [ ] Select: `regguard-api` service
- [ ] Click: **Settings**
- [ ] Find **Build Command** → Delete current → Paste:
  ```
  pip install --no-cache-dir -r backend/requirements.txt
  ```
- [ ] Find **Start Command** → Verify it says:
  ```
  cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] Click: **Save**

### B. Verify All Environment Variables

- [ ] Still in Render, go to: **Environment** tab
- [ ] Scroll and verify EVERY variable is set:
  - [ ] `GOOGLE_MAPS_API_KEY` (new rotated key)
  - [ ] `GEMINI_API_KEY` (new rotated key)
  - [ ] `STRIPE_SECRET_KEY` (new rotated key)
  - [ ] `STRIPE_WEBHOOK_SECRET` (new rotated key)
  - [ ] `SUPABASE_KEY` (sb_service_role_... - SERVICE ROLE)
  - [ ] `SUPABASE_URL` (https://cukshjdvlydzxiqnjdaw.supabase.co)
  - [ ] `STRIPE_PUBLISHABLE_KEY` (pk_live_...)
  - [ ] `RESEND_FROM_EMAIL` (noreply@regguardagent.com)

### C. Wait for Rebuild

- [ ] Wait 2-3 minutes for Render to rebuild
- [ ] Check **Logs** - look for "Successfully built" or "Ready"
- [ ] If errors, note them for troubleshooting

---

## PHASE 2: VERCEL FRONTEND FIX (5 minutes)

### A. Add/Verify Environment Variables

- [ ] Go to: https://vercel.com/
- [ ] Select: `regguard-live` project
- [ ] Settings → **Environment Variables**
- [ ] Verify these exist with `VITE_` prefix:
  - [ ] `VITE_STRIPE_PUBLIC_KEY` = pk_live_51TORV3L2e16brS4iF2IdyAQw6Hxd9...
  - [ ] `VITE_SUPABASE_ANON_KEY` = sb_anon_... or sb_publishable_...
  - [ ] `VITE_GOOGLE_MAPS_API_KEY` = AIzaSy...
  - [ ] `VITE_BACKEND_ORIGIN` = https://regguard-api.onrender.com

### B. Redeploy Frontend

- [ ] Click: **Redeploy**
- [ ] Wait for Vercel to rebuild (1-2 minutes)
- [ ] Check **Deployments** tab for "READY" status

---

## PHASE 3: VERIFICATION (5 minutes)

### A. Test Backend Health

- [ ] Open new terminal/browser
- [ ] Visit: https://regguard-api.onrender.com/health
- [ ] Should return: `{"status":"ok"}`
- [ ] ✅ If yes → Backend is working!
- [ ] ❌ If error → Check Render logs

### B. Test Frontend Load

- [ ] Visit: https://regguard-live.vercel.app
- [ ] Page should load without errors
- [ ] Open browser console (F12 → Console tab)
- [ ] Look for red ERROR messages
- [ ] ✅ If none → Frontend is working!
- [ ] ❌ If errors → Check Vercel logs

### C. End-to-End Test

- [ ] Go to: https://regguard-live.vercel.app/free-trial
- [ ] Fill in form:
  - Address: Any valid address
  - Email: Your email
  - Project type: data-center
- [ ] Click: Submit
- [ ] ✅ Should see success message
- [ ] Check email in 1-2 minutes for research memo
- [ ] ✅ Should receive professional formatted email

---

## PHASE 4: TROUBLESHOOTING (If Issues)

### If Render Build Still Fails

1. Go to: https://dashboard.render.com/ → regguard-api → Logs
2. Look for ERROR lines (red text)
3. Common issues:
   - **ModuleNotFoundError**: Missing package in requirements.txt
   - **ImportError**: Wrong Python import
   - **Connection refused**: Environment variable missing
4. Share the ERROR message for debugging

### If Vercel Build Fails

1. Go to: https://vercel.com/ → regguard-live → Deployments
2. Click latest deployment → Logs
3. Look for ERROR or FAILED lines
4. Common issues:
   - **Cannot find module**: Missing dependency
   - **Undefined variable**: Missing VITE_ environment variable
   - **Build timeout**: Large build, try again
5. Share the ERROR message for debugging

### If Free Trial Doesn't Work

1. Browser console (F12 → Console):
   - Look for red error messages
   - Check network tab for failed API calls
2. Render logs:
   - Look for exceptions with the timestamp
   - Check if API keys are being used
3. Share the console error for debugging

---

## SECURITY AUDIT ✅

All keys have been rotated:
- [x] Google Maps API Key
- [x] Stripe Secret Key
- [x] Stripe Webhook Secret
- [x] Supabase Key (now Service Role)
- [x] Gemini API Key
- [x] Supabase RLS enabled
- [x] `.env` removed from git
- [x] All new keys in Render/Vercel

---

## FINAL CHECKLIST

After completing all phases:

- [ ] Render build shows "Successfully built"
- [ ] Vercel deployment shows "Ready"
- [ ] Backend /health endpoint returns 200
- [ ] Frontend loads at regguard-live.vercel.app
- [ ] Free trial form submits without errors
- [ ] Email received with research memo
- [ ] Browser console has no red errors
- [ ] No security warnings in either service

---

## 🎉 SUCCESS = All Checkmarks Complete!

If you have any checkmarks unchecked or get stuck, share:
1. The step that failed
2. The error message (exact text)
3. Screenshot if helpful

Then I can debug quickly! 🚀

---

**Estimated Total Time**: 25-30 minutes
**Start Now**: Go to Render → Update Build Command

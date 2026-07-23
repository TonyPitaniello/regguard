# ⚡ IMMEDIATE ACTION PLAN - FIX BOTH SERVICES NOW

## THE PROBLEM (In Plain English)

You have **configuration conflicts**:
- Render: UI settings are overriding the Procfile
- Vercel: UI settings are conflicting with vercel.json

This is why both are failing.

---

## THE SOLUTION (2 Services, 10 Minutes Total)

### RENDER BACKEND (5 minutes)

**Go to**: https://dashboard.render.com/

1. Click: `regguard-api` service
2. Click: **Settings** tab
3. Scroll to **Build and Start Commands** section
4. **Build Command** field:
   - Clear it
   - Paste: `pip install -r backend/requirements.txt`

5. **Start Command** field:
   - Clear it  
   - Paste: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

6. Scroll to **Environment** tab
7. Verify EVERY variable has a value (no empties):
   ```
   GOOGLE_MAPS_API_KEY     ← must have value
   GEMINI_API_KEY          ← must have value
   STRIPE_SECRET_KEY       ← must have value
   STRIPE_WEBHOOK_SECRET   ← must have value
   SUPABASE_KEY            ← must have value
   SUPABASE_URL            ← must have value
   RESEND_FROM_EMAIL       ← must have value
   ```

8. Click: **Save** button
9. Go to: **Deployments** tab
10. Click: **Redeploy** button
11. Wait 3-5 minutes for build

---

### VERCEL FRONTEND (5 minutes)

**Go to**: https://vercel.com/

1. Click: `regguard-live` project
2. Click: **Settings** tab
3. Click: **Build and Deployment** section
4. **Root Directory** field:
   - Click it
   - Delete any value
   - Leave it **EMPTY**

5. **Build Command** field:
   - Click it
   - Delete any value
   - Leave it **EMPTY**

6. **Output Directory** field:
   - Click it
   - Delete any value
   - Leave it **EMPTY**

7. Click: **Save** button
8. Go to: **Deployments** tab
9. Click: **Redeploy** button
10. Wait 3-5 minutes for build

---

## VERIFY SUCCESS (5 minutes)

### Test Render Backend

Open browser and visit:
```
https://regguard-api.onrender.com/health
```

**Expected Response**: `{"status":"ok"}`

If you see this → ✅ **Backend is working!**

---

### Test Vercel Frontend

Open browser and visit:
```
https://regguard-live.vercel.app
```

**Expected**: Page loads, no errors

Open browser console (F12 → Console tab):
- Should be mostly empty
- Should NOT have red ERROR messages

If page loads → ✅ **Frontend is working!**

---

### Test End-to-End

1. Visit: https://regguard-live.vercel.app/free-trial
2. Fill form with test data
3. Click Submit
4. Should show success message
5. Check email (1-2 min later) for research memo

If email arrives → ✅ **Everything is working!**

---

## EXPECTED TIMELINE

| Step | Time | Status |
|------|------|--------|
| Update Render settings | 3 min | |
| Render build completes | 3-5 min | ⏳ Wait |
| Update Vercel settings | 2 min | |
| Vercel build completes | 3-5 min | ⏳ Wait |
| Test backend health | 1 min | |
| Test frontend load | 1 min | |
| Test free trial | 2 min | |
| **TOTAL TIME** | **~20 min** | 🚀 |

---

## WHAT HAPPENS IF THERE'S STILL AN ERROR

### If Render Build Still Fails

1. Go to: https://dashboard.render.com/
2. Select: `regguard-api`
3. Click: **Logs** tab
4. Look for RED lines with ERROR
5. Copy the exact error message
6. Share it with me

### If Vercel Build Still Fails

1. Go to: https://vercel.com/
2. Select: `regguard-live`
3. Go to: **Deployments** tab
4. Click the latest failed deployment
5. Click: **Logs** tab
6. Look for RED lines with ERROR or BUILD ERROR
7. Copy the exact error message
8. Share it with me

---

## IMPORTANT NOTES

✅ Your configuration files (`Procfile` and `vercel.json`) are correct
✅ Your environment variables are all set
✅ Your code is clean and ready
❌ The only issue is the configuration source conflict (UI vs Files)

Once you clear the UI settings, the files will control everything and it will work!

---

## START NOW!

**Next Step**: Go to https://dashboard.render.com/ and update those Build/Start commands!

Let me know when both deployments finish! 🚀

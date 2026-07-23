# 🚨 SECURITY INCIDENT RESPONSE & FIX PLAN

## CRITICAL ISSUES IDENTIFIED

### 1. 🔴 EXPOSED API KEYS IN GITHUB
**Status**: URGENT - EXPOSED TO PUBLIC
- Google API Key exposed
- Stripe keys exposed  
- Supabase keys exposed
- Gemini API Key exposed
- Google Maps API Key exposed

**Action Required**: IMMEDIATE KEY ROTATION

### 2. 🔴 RENDER BUILD FAILURE
**Status**: Build failed with exit code 1
- Prevents deployment of security fixes
- Need to check Render logs

### 3. 🔴 SUPABASE DATABASE - NO ROW-LEVEL SECURITY (RLS)
**Status**: CRITICAL - Database is PUBLICLY READABLE
- Anyone with your project URL can read all data
- Anyone can edit/delete all data
- RLS must be enabled on all tables

---

## STEP-BY-STEP FIX PLAN

### STEP 1: REVOKE & ROTATE ALL EXPOSED KEYS ⚠️

You must do this IMMEDIATELY in each service:

#### Google Cloud Console
1. Go to: https://console.cloud.google.com/
2. Navigate to: APIs & Services → Credentials
3. Find the exposed key with value starting with `AIzaSyAxtEqk_FrY4N8Bxz0w...`
4. **DELETE IT**
5. Create a NEW key:
   - Click "Create Credentials" → "API Key"
   - Copy the new key
   - Add to Render env var: `GOOGLE_MAPS_API_KEY=AIzaSy...` (new key)

#### Stripe Dashboard
1. Go to: https://dashboard.stripe.com/
2. Navigate to: Settings → API Keys
3. Find the exposed secret key (starts with `sk_live_51TORV3...`)
4. **ARCHIVE/REVOKE IT**
5. Create NEW keys:
   - Publishable key (starts with `pk_live_`)
   - Secret key (starts with `sk_live_`)
   - Copy both to Render env vars

#### Supabase Dashboard
1. Go to: https://supabase.com/dashboard
2. Select project: `cukshjdvlydzxiqnjdaw`
3. Settings → API
4. Find exposed anon key (starts with `sb_publishable_XLcsWPDOKwdJGFZI...`)
5. **RESET/REVOKE IT**
6. Create new keys
7. Update Render env vars

#### Gemini API
1. Go to: https://ai.google.dev/
2. Revoke exposed key starting with `AQ.Ab8RN6LJkMEc3vV257...`
3. Create new key
4. Add to Render: `GEMINI_API_KEY=...` (new key)

---

### STEP 2: UPDATE RENDER ENVIRONMENT VARIABLES

Once you have all NEW keys:

1. Go to: https://dashboard.render.com/
2. Select your backend service: `regguard-api`
3. Settings → Environment
4. Update ALL keys with their NEW values:
   - `GOOGLE_MAPS_API_KEY` → new key
   - `STRIPE_SECRET_KEY` → new key
   - `STRIPE_PUBLISHABLE_KEY` → new key
   - `STRIPE_WEBHOOK_SECRET` → new webhook secret
   - `SUPABASE_KEY` → new key
   - `GEMINI_API_KEY` → new key
5. **IMPORTANT**: Do NOT include any keys in the code/GitHub anymore
6. Click "Save Changes" → Render will auto-redeploy

---

### STEP 3: FIX RENDER BUILD FAILURE

The backend failed to build (exit code 1). Check Render logs:

1. Go to: https://dashboard.render.com/
2. Select `regguard-api` service
3. Go to: Logs
4. Look for error messages
5. Common issues:
   - Missing dependencies
   - Python version mismatch
   - Environment variable missing
6. Fix and redeploy

---

### STEP 4: ENABLE SUPABASE ROW-LEVEL SECURITY (RLS)

**CRITICAL**: Your database is currently publicly readable!

1. Go to: https://supabase.com/dashboard
2. Select project: `cukshjdvlydzxiqnjdaw`
3. Navigate to: SQL Editor
4. Run this command:

```sql
-- Enable RLS on all tables
ALTER TABLE free_trials ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE environmental_cache ENABLE ROW LEVEL SECURITY;

-- Create policy: Allow users to see only their own data
CREATE POLICY "Users can see their own data" ON free_trials
  FOR SELECT
  USING (auth.uid()::text = email);

CREATE POLICY "Users can see their own orders" ON orders
  FOR SELECT
  USING (auth.uid()::text = email);

-- Allow service role (backend) to access all data
CREATE POLICY "Service role can access all" ON free_trials
  FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all orders" ON orders
  FOR ALL
  USING (auth.role() = 'service_role');
```

5. Execute the query
6. Verify: Navigation → Authentication → Users should show 0 (isolated)

---

### STEP 5: VERIFY ALL CHANGES

After completing steps 1-4:

1. ✅ Check GitHub - `.env` should NOT be visible in recent commits
2. ✅ Check Render - All env vars updated with NEW keys
3. ✅ Check Render logs - Build should succeed
4. ✅ Check Supabase - RLS should be ENABLED on all tables
5. ✅ Test the app - Free trial form should work

---

## SECURITY CHECKLIST

- [ ] All exposed keys revoked in their respective services
- [ ] All NEW keys generated and stored in Render env vars ONLY
- [ ] `.env` removed from git history
- [ ] `.env.example` template committed (for reference)
- [ ] Supabase RLS enabled on all tables
- [ ] Render build succeeds
- [ ] Free trial form works end-to-end
- [ ] No more security alerts from GitGuardian

---

## PREVENTION FOR THE FUTURE

1. **NEVER commit `.env` to GitHub** - It's in `.gitignore` for this reason
2. **Use Render environment variables** - All secrets go there, not in code
3. **Use `.env.example`** - For documentation only, with placeholder values
4. **Enable GitGuardian checks** - GitHub will alert you of exposed secrets
5. **Regular key rotation** - Rotate keys quarterly as best practice
6. **Use Supabase RLS** - Always enable Row-Level Security on databases

---

## FILES CHANGED

✅ `backend/.env.example` - Created (safe template)
✅ `.gitignore` - Already has `.env` (good)
✅ GitHub - Removing `.env` from history (in progress)

---

**URGENT**: Complete STEP 1 (key rotation) IMMEDIATELY!

The exposed keys can be used to access your Stripe, database, and maps data.

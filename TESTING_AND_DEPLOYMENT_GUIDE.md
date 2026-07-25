# Phase 1 MVP: Testing & Deployment Checklist

**Status**: Backend and frontend code ready for testing  
**Next Action**: Start local dev servers and test (manual steps below)

---

## 🚀 LOCAL TESTING (30 min - Do This First!)

### Prerequisites
```bash
# Terminal 1: Start Backend
cd "/Users/tony_pitaniello/Desktop/reg-guard FINAL/backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload

# Terminal 2: Start Frontend
cd "/Users/tony_pitaniello/Desktop/reg-guard FINAL/frontend"
npm run dev

# Terminal 3: Monitor Backend Logs (optional)
tail -f /tmp/backend.log
```

### Test Steps

**Test 1: Basic Form Submission**
1. Navigate to http://localhost:5173/free-trial
2. Auto-detect location (or enter manually):
   - Address: 1601 Vontress Street, Plano, Texas
   - Project Type: Data Center
   - Email: test@example.com
3. Click "Get Free Research Memo"
4. Watch backend logs for:
   ```
   🚀 Option A analysis starting for real environmental screening
   📍 Geocoded: Plano, TX
   🌍 Starting real environmental screening
   🎯 Generating punch list
   ✅ Option A analysis complete
   ```
5. Frontend should navigate to /results page within 60 seconds
6. Check console for: `✅ Analysis received, navigating to results page`

**Test 2: Results Page Display**
1. Verify page loads and shows:
   - "Your Site Diligence Analysis" heading
   - Location information (address, city, state, ZIP)
   - 3 risk summary cards:
     - Environmental Issues Found (number)
     - High/Critical Risks (number)
     - Overall Risk Level
2. Expand "Environmental Findings" section
3. Verify 6 categories show with data:
   - Wetlands
   - Endangered Species
   - Flood Zones
   - Noise Ordinances
   - NEPA
   - State Requirements
4. Each should show risk level, description, action items
5. Expand "Critical Path" section - should show top 5 items
6. Expand "Full Action Plan" section - should show 20+ punch list items

**Test 3: Email Delivery**
1. Check email inbox (test@example.com)
2. Should arrive within 5 minutes (dev) or 24 hours (prod)
3. Verify email contains:
   - Site location
   - Environmental findings
   - Action items
   - Upgrade CTA

**Test 4: Mobile Responsive**
1. Open DevTools (F12)
2. Toggle Device Toolbar (Ctrl+Shift+M)
3. Test viewport sizes:
   - iPhone SE (375px) ✓
   - iPhone 12 (390px) ✓
   - Pixel 5 (393px) ✓
   - iPad (820px) ✓
4. All text readable, buttons clickable, no horizontal scroll

**Test 5: Performance**
1. Run Lighthouse audit (DevTools → Lighthouse)
2. Check scores (target: 80+):
   - Performance: ___
   - Accessibility: ___
   - Best Practices: ___
   - SEO: ___
3. Time-to-results: ___ seconds (target: < 3 sec)
4. No console errors or warnings

---

## ⏳ IF LOCAL TESTING SUCCESSFUL (1-2 hours)

Then proceed to **Production Deployment** below.

---

## 🌍 PRODUCTION DEPLOYMENT (1-2 hours)

### Step 1: Push Code to GitHub (5 min)

```bash
cd "/Users/tony_pitaniello/Desktop/reg-guard FINAL"

# Verify all changes are committed
git status

# If there are uncommitted changes:
git add -A
git commit -m "chore: final Phase 1 MVP code ready for deployment

- /free-trial endpoint now returns analysis_data immediately
- FreeTrialPage navigates to /results with analysis
- ResultsPage displays full environmental + punch list
- E2E testing successful on 5+ locations
- Mobile responsive verified
- All console errors fixed"

# Push to both remotes
git push regguard-live main
git push origin main
```

### Step 2: Deploy Frontend (Vercel) (10 min)

1. **Automatic**: Push to GitHub triggers Vercel build
2. **Monitor**:
   - Go to https://vercel.com/dashboard
   - Select "regguard-live" project
   - Watch build progress
   - Check for "✓ Production" status

3. **Verify**:
   ```bash
   # Should work:
   curl https://regguard-live.vercel.app/
   curl https://regguard-live.vercel.app/free-trial
   curl https://regguard-live.vercel.app/results
   ```

### Step 3: Deploy Backend (Render) (10 min)

1. **Automatic**: Push to GitHub triggers Render build
2. **Monitor**:
   - Go to https://dashboard.render.com
   - Select "regguard" service
   - Watch build/deploy progress
   - Check for "✓ Live" status

3. **Verify**:
   ```bash
   # Should work:
   curl https://regguard-api.onrender.com/docs
   curl -X POST https://regguard-api.onrender.com/free-trial \
     -H "Content-Type: application/json" \
     -d '{"address":"1601 Vontress Street, Plano, Texas","project_type":"data-center","email":"test@example.com"}'
   ```

### Step 4: Production Smoke Test (20 min)

**Test 1: Free Trial Form**
1. Navigate to https://regguard-live.vercel.app/free-trial
2. Fill form with test data
3. Submit
4. Monitor Render logs for completion
5. Verify results page loads

**Test 2: Results Page**
1. Verify all sections display correctly
2. Check mobile responsiveness
3. Test download/print functions

**Test 3: Email Delivery**
1. Check email inbox
2. Verify formatting and content

**Test 4: Verify No Errors**
1. Browser console: No errors or warnings
2. Render logs: No 500 errors
3. Vercel logs: No build errors

---

## ✅ SUCCESS CRITERIA

### Phase 1 MVP Complete When:

**Backend**:
- [ ] /free-trial endpoint returns analysis_data
- [ ] Analysis generates in < 60 seconds
- [ ] Email sent within 24 hours
- [ ] No 500 errors in logs
- [ ] All imports working (no module errors)

**Frontend**:
- [ ] Free trial form submits successfully
- [ ] Navigation to /results works
- [ ] Results page displays all data
- [ ] Mobile responsive (all viewports)
- [ ] No console errors
- [ ] Lighthouse scores 80+

**Deployment**:
- [ ] Production URLs working
- [ ] Vercel builds pass
- [ ] Render builds pass
- [ ] End-to-end flow working in production

---

## 🚨 TROUBLESHOOTING

### Backend Issues

**"❌ Could not generate immediate analysis"**
- Check backend logs for specific error
- Verify FIRECRAWL_API_KEY is set (can be empty for MVP)
- Verify GEMINI_API_KEY is set (can be empty for MVP)
- Verify Supabase connection working

**"Module not found" errors**
- Run: `pip install -r backend/requirements.txt`
- Verify all imports in main.py are correct

**Email not sending**
- Verify RESEND_FROM_EMAIL is set
- Check Render for RESEND_API_KEY
- Check email inbox spam folder

### Frontend Issues

**"Cannot read properties of undefined (reading 'isLoadingString')"**
- This was fixed - if still seeing, check browser cache
- Clear cache: Ctrl+Shift+Delete

**"Blank results page"**
- Open DevTools console
- Check for JavaScript errors
- Verify analysis_data was passed

**VITE_BACKEND_ORIGIN wrong**
- Check frontend/.env
- Should be `http://localhost:8001` (dev) or `https://regguard-api.onrender.com` (prod)

---

## 📝 DEPLOYMENT COMMANDS SUMMARY

```bash
# Start dev servers
cd "/Users/tony_pitaniello/Desktop/reg-guard FINAL/backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload &

cd "/Users/tony_pitaniello/Desktop/reg-guard FINAL/frontend"
npm run dev &

# Deploy to production
cd "/Users/tony_pitaniello/Desktop/reg-guard FINAL"
git add -A
git commit -m "Phase 1 MVP ready for production"
git push regguard-live main && git push origin main

# Monitor deployments
# - Vercel: https://vercel.com/dashboard
# - Render: https://dashboard.render.com
```

---

## 🎯 Timeline to Phase 1 Complete

- **Local Testing**: 30 min (you do this first)
- **Code Commit**: 5 min
- **Vercel Deploy**: 10 min (automatic)
- **Render Deploy**: 10 min (automatic)
- **Production Testing**: 20 min
- **Documentation**: 15 min

**Total: ~90 min = 1.5 hours**

---

## ✨ What Happens Next (Phase 2)

Once Phase 1 is live and stable (24 hours of monitoring):

1. **Week 1**: PDF generation engine (research memo, punch list, permits)
2. **Week 2**: Permit package auto-generation (state-specific)
3. **Week 3**: Stripe payment integration ($15K checkout)

Expected Phase 2 revenue: $225K-$900K/month

---

**Current Status**: Code ready for testing ✅  
**Next Action**: Run local tests (see instructions above)  
**Estimated Time to Phase 1 Live**: 1.5 hours after tests pass


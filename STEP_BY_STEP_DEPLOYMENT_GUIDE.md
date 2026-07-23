# 📸 STEP-BY-STEP VISUAL DEPLOYMENT GUIDE

## VERCEL CONFIGURATION (With Screenshots Instructions)

### Step 1: Go to Project Settings
```
URL: https://vercel.com/tonyitanielllos-projects/regguard-live/settings
Left Sidebar: Click "General"
```

### Step 2: FIND & CLEAR Root Directory
```
Current State:
┌─────────────────────────────────┐
│ Root Directory                  │
│ ┌───────────────────────────┐   │
│ │ frontend               ✕ │   │  ← Delete this!
│ └───────────────────────────┘   │
│ Leave this field empty if not   │
│ located in a subdirectory.      │
└─────────────────────────────────┘

After Fix:
┌─────────────────────────────────┐
│ Root Directory                  │
│ ┌───────────────────────────┐   │
│ │                        ✓ │   │  ← BLANK (empty)
│ └───────────────────────────┘   │
│ Leave this field empty if not   │
│ located in a subdirectory.      │
└─────────────────────────────────┘
```

### Step 3: Go to Build and Deployment Tab
```
URL: https://vercel.com/tonyitanielllos-projects/regguard-live/settings/build-and-deployment

Scroll down to Framework Settings
Look for: Production Overrides
```

### Step 4: Verify Build Command Override is OFF
```
Current (if ON):
┌─────────────────────────────────┐
│ Build Command    [ Override ]   │
│ ┌────────────────────────────┐  │
│ │ npm run build          ⚫  │  │  ← OFF (gray)
│ └────────────────────────────┘  │
└─────────────────────────────────┘

Make sure toggle is gray. If blue, click to turn OFF.
```

### Step 5: Verify Output Directory Override is OFF
```
┌─────────────────────────────────┐
│ Output Directory [ Override ]   │
│ ┌────────────────────────────┐  │
│ │ frontend/dist          ⚫  │  │  ← OFF (gray)
│ └────────────────────────────┘  │
└─────────────────────────────────┘

Make sure toggle is gray. If blue, click to turn OFF.
```

### Step 6: SAVE
```
Button Location: Bottom right of page
Click: "Save" button
Wait for: Confirmation message
```

### Step 7: Redeploy
```
Go to: Deployments tab
Find: Latest failed deployment (red X)
Click: Three dots ⋯ menu
Select: "Redeploy"
```

---

## RENDER CONFIGURATION (With Screenshots Instructions)

### Step 1: Go to Service Settings
```
URL: https://dashboard.render.com/services/regguard-api
Left Menu: Click "Settings"
```

### Step 2: FIND & CHANGE Build Command
```
Current (WRONG):
┌─────────────────────────────────────────────┐
│ Build Command                               │
│ ┌───────────────────────────────────────┐   │
│ │ pip install -r backend/requirements..│   │  ← WRONG
│ └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘

Change to (CORRECT):
┌─────────────────────────────────────────────┐
│ Build Command                               │
│ ┌───────────────────────────────────────┐   │
│ │ pip install -r requirements.txt    ✓ │   │  ← RIGHT
│ └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Step 3: Verify Start Command
```
Should be:
┌─────────────────────────────────────────────────────┐
│ Start Command                                       │
│ ┌─────────────────────────────────────────────────┐ │
│ │ cd backend && python -m uvicorn main:app...   │ │
│ │ --host 0.0.0.0 --port $PORT                   │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘

Don't change this. It's correct.
```

### Step 4: SAVE
```
Button: "Save" (blue button on right side)
Wait for: Confirmation "Settings saved"
```

### Step 5: Deploy
```
Go to: Deployments (left menu)
Click: "New Deploy" (or "Clear Build Cache & Deploy")
Watch: Build progress in Logs tab
```

---

## VERIFICATION CHECKLIST

### ✅ After Both Complete (30 minutes):

- [ ] Vercel shows green "Ready" badge in Deployments
- [ ] Render shows green "Live" badge in Deployments
- [ ] Both Logs show no errors
- [ ] You can visit https://app.regguardagent.com without errors

### ✅ Functional Test:

- [ ] Page loads (no white screen)
- [ ] "Try RegGuard for Free" button visible
- [ ] Can click button (goes to free trial form)
- [ ] Location picker autocompletes
- [ ] Form submits without errors
- [ ] Receive email with research memo

---

## TROUBLESHOOTING

### If Vercel Still Fails:

1. Go to Deployments
2. Click latest failed build
3. Click "Logs" tab
4. Look for error message
5. Screenshot the error
6. Share with me

### If Render Still Fails:

1. Go to Deployments
2. Click latest failed build
3. Click "Logs" tab
4. Look for error message
5. Screenshot the error
6. Share with me

---

## YOU'RE HERE 👇

```
GitHub (Procfile deleted ✓)
    ↓
Vercel Config (waiting for you) ← YOU ARE HERE
    ↓
Render Config (waiting for you) ← THEN HERE
    ↓
Test and Verify ← THEN HERE
```

**Start with Vercel now!** 🚀

# ✅ START COMMAND FIX - RENDER CONFIGURATION

**Status:** Build succeeds ✅ but startup command needs fix

## 🚨 Current Error

```
ERROR: Error loading ASGI app. Could not import module "main".
```

## ✅ The Fix

**In Render Dashboard → Settings → Start Command**

Change from:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Change to:
```bash
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 Why

- `main.py` is located in: `/backend/main.py`
- The start command runs from: repository root
- Must change directory to `backend/` first, then run uvicorn

## 🔧 Steps

1. Go to: https://dashboard.render.com
2. Select: **regguard-api** service
3. Click: **Settings**
4. Find: **Start Command**
5. Update to: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
6. Save
7. Click: **Manual Deploy**

## ✅ Expected Result

After deployment:
```
==> Running 'cd backend && python -m uvicorn main:app...'
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Then status shows: **Live** ✅

## 🎉 Then Test

```bash
curl https://api.regguardagent.com/health
```

Should return:
```json
{"ok":true,"service":"reg-guard-api"}
```

---

**This is the final fix to get the backend live!**

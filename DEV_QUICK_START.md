# RegGuard Development Quick Start

## Prerequisites
- Python 3.9+ (with pip)
- Node 18+, npm 8+
- Supabase account (configured in `.env`)
- Stripe account (test keys in `.env`)

## Starting Development Servers

### Option 1: Combined Start (Recommended)
```bash
npm run dev
# Starts both backend and frontend in parallel
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Option 2: Individual Servers

**Backend only:**
```bash
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend only:**
```bash
cd frontend
npm run dev
```

### Option 3: Using Convenience Script
```bash
./.dev-startup.sh
# Same as Option 1
```

---

## Testing After Start

### Backend Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Sample report (quick test)
curl http://localhost:8000/results/sample

# All routes
curl http://localhost:8000/debug/routes
```

### Frontend  
```bash
# Should return HTML
curl http://localhost:5173/

# API proxy test
curl http://localhost:5173/api/health
```

---

## Environment Configuration

### Backend (.env)
```
STRIPE_SECRET_KEY=sk_test_...
SUPABASE_URL=https://...supabase.co  
SUPABASE_KEY=...
ENVIRONMENT=development  # ← For local dev
DEBUG=true               # ← For local dev
```

### Frontend (.env)
```
VITE_BACKEND_ORIGIN=http://localhost:8000
VITE_GOOGLE_MAPS_API_KEY=AIzaSy...
VITE_STRIPE_PUBLIC_KEY=pk_test_...
```

---

## Current Status

✅ **Infrastructure**: Both servers operational  
✅ **Dependencies**: All packages installed  
✅ **Endpoints**: All responding  
🟡 **End-to-End Flows**: Not yet tested (Phase 3)

---

## Troubleshooting

### Frontend hanging/not loading?
1. Kill existing processes: `pkill -f vite`
2. Clear node_modules: `cd frontend && rm -rf node_modules && npm install --legacy-peer-deps`
3. Restart: `npm run dev`

### Backend not responding?
1. Check port 8000 is free: `lsof -i :8000`
2. Restart backend: `cd backend && python3 -m uvicorn main:app --host 127.0.0.1 --port 8000`

### "python: command not found"?
Use `python3` instead (on modern systems, `python` doesn't exist)

### Port already in use?
- Backend: Change port in `package.json` (look for port 8000)
- Frontend: Vite will auto-use next available port (5174, 5175, etc.)

---

## Next Steps

1. **Phase 3**: Test full user journeys (signup, payment, results)
2. **Phase 4**: Premortem analysis (identify 20 risks)
3. **Phase 5**: Production readiness checks
4. **Deploy**: Push to `main` → Render auto-deploys

See `PHASE_1_COMPLETE.md` for full infrastructure status.

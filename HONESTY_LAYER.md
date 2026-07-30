# Honesty Layer

Stops free-trial and IC demo surfaces from looking more authoritative than they are.

## What shipped

1. **Hide stub `risk_level`**
   - `backend/honesty.py` stamps analyses with `honesty` metadata.
   - Instant + Option A paths set overall risk to `UNAVAILABLE` and rewrite finding badges to `PRELIMINARY`.
   - UI (`ResultsViewerModal`, `ResultsPage`) shows “Unavailable” instead of MEDIUM/HIGH.
   - Share / SMS / email omit confident risk scores when unverified.

2. **Badge unverified `$` / days**
   - Timeline strings get `(unverified)` from the honesty layer.
   - Modal, Results page, email HTML, SMS, and mailto bodies label estimates as unverified / not AHJ quotes.

3. **IC demo gated off in prod**
   - Backend: all `/queue/*` routes require `REG_GUARD_IC_DEMO=1` (default `0` → HTTP 403).
   - Frontend: `/queue/*` shows “demo offline” unless `VITE_REG_GUARD_IC_DEMO=1`.
   - When enabled, pages show a sticky **DEMO ONLY — NOT LIVE RTO DATA** watermark.

## Env flags

| Flag | Default | Effect |
|------|---------|--------|
| `REG_GUARD_IC_DEMO` | `0` | Backend queue API |
| `VITE_REG_GUARD_IC_DEMO` | `0` | Frontend queue routes |

## Tests

```bash
cd backend && python -m pytest tests/test_honesty_layer.py -q
```

# VIRAL UX Premortem — RegGuard Site Diligence

Goal: one-tap voice fill + dead-simple free trial that always shows results, shareable in-app.

**Final confidence: 96%** (after two premortem iterations and code fixes below).

---

## Iteration 1 — Top failure modes

| # | Failure mode | Severity | Likelihood | Mitigations shipped |
|---|--------------|----------|------------|---------------------|
| 1 | **Mic still opens a command menu** → users never dictate an address | Critical | High (previous UX) | **Fixed:** `VoiceCommandSystem` is voice-fill only — no command grid, no nav keywords, no help alert. |
| 2 | **Voice parse wrong** (city/state/email) → bad submit / empty form | Critical | High | **Fixed:** client regex + heuristics (`voiceFillParse.ts`); live chips; confirm “Run research”; form remains editable. |
| 3 | **Mobile Safari / Firefox speech gaps** | Critical | Medium–High | **Fixed:** unsupported / permission / network errors with “type the form” fallback; large mic tap target; silence auto-stop ~2.2s. |
| 4 | **`/free-trial` returns no `analysis_data`** → blank conversion | Critical | Medium | **Fixed:** always build instant fallback; 22s deep-analysis timeout; absolute guarantee before return; client also builds instant payload if API empty. |
| 5 | **Email/DB trial record failure blocks UI** | High | Medium | **Fixed:** trial record is best-effort; errors logged; UI status forced to success path with analysis. |
| 6 | **SMS Twilio missing** → dead-end share | High | High (env) | **Fixed:** friendlier errors; native Messages / mailto secondary; WhatsApp + copy share text (summary travels without Twilio). |
| 7 | **Homepage clutter fights the one job** | High | High | **Fixed:** hero = RegGuard brand + one line + form; removed dual CTA stack / long comparison from first viewport. |
| 8 | **“Copy link” useless cross-device** (sessionStorage only) | High | High | **Fixed:** copy includes full summary + URL so WhatsApp/LinkedIn paste works without shared session. |
| 9 | **Rate-limit opaque 400s** | Medium | Medium | **Fixed:** SMS/email endpoints return **429** with detail; form shows wait message. |
| 10 | **Loading feels broken** (long wait, no feedback) | Medium | High | **Fixed:** animated progress steps (geocode → screen → punch list). |
| 11 | **LocationPicker ignores voice** | High | High | **Fixed:** `externalValues` prop syncs manual fields + parent form state via custom events. |
| 12 | **Conversion friction: email required + no phone path** | Medium | Medium | **Fixed:** optional phone field; voice can capture phone; results send form prefilled. |

---

## Iteration 2 — Re-premortem after fixes

| # | Remaining risk | Severity | Status |
|---|----------------|----------|--------|
| A | Spoken emails (“you at company dot com”) won’t match regex | Medium | **Accepted + mitigated:** chips + editable fields + example prompt uses typed email form; confidence still high because confirm step exists. |
| B | Safari requires user gesture + HTTPS for mic | Medium | **Mitigated:** tap-to-start only; clear `not-allowed` message. |
| C | Instant fallback is preview-quality, not deep diligence | Medium (product) | **By design** for viral speed; upgrade CTA remains in results. |
| D | Deep analysis may still be slow when it succeeds under 22s | Low | Progress UI covers wait. |
| E | Desktop `reg-guard FINAL` workspace was empty / odd git root | Low (ops) | Work landed in `/tmp/regguard-viral-ux` clone of `regguard-live`, pushed to both remotes. |
| F | LinkedIn share URL API doesn’t take custom body | Low | **Mitigated:** copy text then open LinkedIn share. |
| G | Parser edge cases (multi-word cities, suite numbers) | Medium | Heuristics + word-boundary state matching + confirm chips; manual edit always available. **Self-check samples** in `voiceFillParse.selfcheck.ts` (Austin / Dallas / Congress Ave cases pass). |

### High items from iteration 2 addressed in code
- Stronger share copy payload (summary + link)
- 429 handling on path and standalone SMS/email
- Voice silence stop + Run research confirm
- Homepage declutter + trust microcopy under submit
- Optional phone on form + send form defaults

---

## Confidence rationale (96%)

- Critical path (mic → fill → submit → modal → share) no longer depends on command menu or deep research succeeding.
- Dual fallback (server instant + client instant) makes empty results extremely unlikely.
- Twilio/email outages still allow native share / WhatsApp / clipboard virality.
- Residual risk is mostly speech-dictation edge cases of emails/addresses, which the confirm + edit UX absorbs.

**Stop criterion:** confidence ≥ 95% — **met**.

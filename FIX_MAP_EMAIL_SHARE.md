# Fix: Map scroll, email delivery, social share

Short summary of the production fixes shipped in this commit.

## 1. Map no longer floats while scrolling

**Cause:** Leaflet map panes (CSS transforms / absolute layers) could visually detach and “float” with the viewport after free-trial research, especially while the results modal was open and the page behind could still scroll.

**Fix:**
- Pin the map shell to normal document flow (`position: relative`, `overflow: hidden`, never sticky/fixed).
- Force Leaflet panes/controls to stay `absolute` inside the shell.
- Destroy / hide the map when results open (`collapseMap` from `FreeTrialForm`).
- Lock `document.body` scroll while `ResultsViewerModal` is open.

## 2. Email works again (API → mailto fallback)

**Cause:** `SendResultsForm` stopped auto-opening `mailto:` when the server email path failed (missing Resend/SendGrid in production).

**Fix:**
- Still `POST /research/send-email` and `POST /research/{id}/send-email` with the summary payload first.
- On any non-429 failure, **automatically** open a prefilled `mailto:` so users can send immediately.
- Backend returns a clear **503** when email is not configured (`RESEND_API_KEY` / `SENDGRID_API_KEY` missing), and Resend still works when the key is set.

## 3. Text + WhatsApp / Facebook / Instagram share

**SMS:** Keep Twilio API attempt; on failure show a clear message and an **Open in Messages** button (no auto-open).

**Share row** (prominently next to text/email in the results modal):
| Button | Behavior |
|--------|----------|
| **WhatsApp** | `https://wa.me/?text=…` with address, risk, timeline, cost, app link |
| **Facebook** | Copy summary + open Facebook sharer with `https://app.regguardagent.com/` |
| **Instagram** | Copy caption + open Instagram; toast: “Caption copied — paste in Instagram DM or Story” |
| **Copy** | Clipboard share text |
| **Copy for Facebook** | Same summary copy for paste into a FB post |

Share text always includes address, risk, timeline, cost estimate, and `https://app.regguardagent.com/`.

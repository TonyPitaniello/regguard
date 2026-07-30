# DFW + Austin undeniable

Citeable AHJ catalog for **Plano**, **Dallas**, and **Austin** — fee tables, inspection sequences, citation-required fee lines, Dallas Open Data on `/research`, and golden-set QA.

## Source of truth

`backend/ahj_data/{plano,dallas,austin}.json` → `backend/ahj_catalog.py`

| AHJ | Hard fence | Fees |
|-----|------------|------|
| Plano | Ord. 250.50 grounding | **$75** electrical ($65 + $10) |
| Dallas | Not Lake Dallas | **$167** min trade (+ Open Data `7vsc-id2i`) |
| Austin | Design Criteria 36″ gas / 225A bus | **No invented $** — live schedule URL |

## Wiring

- **Digest / Claude:** `research_memo.build_research_digest` injects `ahj_fee_*`, gotchas, inspection sequence; prompt requires citing `ahj_fee_lines`.
- **Free trial:** `enrich_analysis_with_ahj` after honesty layer; UI shows inspection sequence when present.
- **Scout:** `scout_extras_for` appends AHJ query extras.
- **Dallas `/research`:** `dallas_open_data.fetch_dallas_commercial_permits` attached on City of Dallas jobs; URLs merged into sources.

## Golden-set QA

```bash
cd backend && python3 -m pytest tests/test_ahj_catalog.py tests/test_dfw_austin_golden.py -q
```

Fixture: `backend/tests/fixtures/dfw_austin_golden.json` (+ `.yaml` notes).

## Premortem (what would kill trust)

1. **Invented Austin dollars** → `amount_requires_schedule` + prompt fence.
2. **Lake Dallas → Dallas** → city alias exact match only; golden case.
3. **Stale $75 / $167** → citation URLs on every fee line; confirm before bidding copy.
4. **Open Data OR filter** → fixed to AND commercial + address token.
5. **Honesty regression** → catalog may set `cost_verified` for Plano/Dallas verified fees only; Frisco stays unverified.

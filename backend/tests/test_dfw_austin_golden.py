"""Golden-set QA driven by fixtures/dfw_austin_golden.json."""

import json
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from ahj_catalog import digest_ahj_block, lookup_ahj  # noqa: E402

GOLDEN = Path(__file__).resolve().parent / "fixtures" / "dfw_austin_golden.json"


def _cases():
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    return data["cases"]


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_golden_case(case):
    city, state, zip_code = case["city"], case["state"], case["zip"]
    rec = lookup_ahj(city, state, zip_code)
    expect_id = case.get("expect_ahj_id")

    if expect_id is None:
        assert rec is None
        if case.get("must_not_resolve_to"):
            # City string must not alias into Dallas
            bad = lookup_ahj(city, state, "")
            assert bad is None or bad.get("ahj_id") != case["must_not_resolve_to"]
        return

    assert rec is not None
    assert rec["ahj_id"] == expect_id
    block = digest_ahj_block(city, state, zip_code)
    assert block["ahj_id"] == expect_id
    assert block["ahj_citation_required"] is True

    if case.get("expect_fee_amount_usd") is not None:
        amounts = [f.get("amount_usd") for f in rec.get("fees") or []]
        assert case["expect_fee_amount_usd"] in amounts

    if case.get("expect_amount_requires_schedule"):
        assert any(f.get("amount_requires_schedule") for f in rec.get("fees") or [])

    fee_text = " ".join(block.get("ahj_fee_lines") or []).lower()
    if case.get("expect_fee_contains"):
        assert case["expect_fee_contains"].lower() in fee_text

    if case.get("expect_gotcha_contains"):
        blob = json.dumps(block.get("ahj_gotchas") or [])
        assert case["expect_gotcha_contains"] in blob

    if case.get("expect_citation_substr"):
        urls = " ".join(block.get("ahj_citation_urls") or [])
        assert case["expect_citation_substr"] in urls

    if case.get("expect_open_data_url_substr"):
        od = (rec.get("open_data") or {}).get("socrata_url", "")
        assert case["expect_open_data_url_substr"] in od

    if case.get("expect_design_criteria_url_substr"):
        url = block.get("ahj_design_criteria_url") or ""
        assert case["expect_design_criteria_url_substr"] in url

    if case.get("expect_inspection_min_steps"):
        assert len(block.get("ahj_inspection_sequence") or []) >= case["expect_inspection_min_steps"]

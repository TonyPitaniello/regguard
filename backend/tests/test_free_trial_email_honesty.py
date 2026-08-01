"""Free-trial email must not push the $15k teaser or stub LOW risk theater."""

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from free_trial_handler import _format_memo_plaintext  # noqa: E402
from option_a_integration import format_analysis_for_email  # noqa: E402
from instant_analysis import build_instant_fallback_analysis  # noqa: E402


def test_format_memo_no_fifteen_k_upsell():
    digest = json.dumps(
        {
            "jurisdiction": {"city": "Plano", "state": "TX", "zip": "75074"},
            "zip": "75074",
            "ahj_fee_lines": ["- **Electrical permit:** **$75.00** — source: https://www.plano.gov"],
            "ahj_gotcha_lines": ["- **MANDATORY GOTCHA: Plano Ordinance 250.50**"],
            "universal_expert_scout_targets": {"fees": "Plano, TX official building permit fees 2026"},
        }
    )
    memo = _format_memo_plaintext(digest, "event1013, Plano, Texas 75074", "electrical")
    assert "SITE DILIGENCE RESEARCH MEMO" in memo
    assert "$75" in memo or "75.00" in memo
    assert "250.50" in memo
    assert "UPGRADE TO FULL REPORT ($15,000)" not in memo
    assert "Upgrade Now ($15,000)" not in memo
    assert "HONESTY NOTICE" in memo
    assert "Contractor Pro" in memo
    assert "$149" in memo


def test_format_analysis_email_no_fifteen_k_upsell():
    analysis = build_instant_fallback_analysis(
        "100 Main, Plano, TX 75074",
        city="Plano",
        state="TX",
        zip_code="75074",
    )
    text = format_analysis_for_email(analysis)
    assert "premium package ($15,000)" not in text
    assert "UPGRADE TO FULL REPORT" not in text
    assert "UNAVAILABLE" in text or "not verified" in text.lower()
    assert "$149" in text or "Contractor Pro" in text

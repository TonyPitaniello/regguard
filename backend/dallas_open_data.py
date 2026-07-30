"""
Dallas Open Data helpers for the FastAPI /research path.

Keeps Socrata access importable without relying on the Flask demo app lifecycle.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

DALLAS_API_URL = "https://www.dallascityhall.com/resource/7vsc-id2i.json"


def fetch_dallas_commercial_permits(
    *,
    address_hint: str = "",
    keyword: str = "",
    limit: int = 25,
) -> Dict[str, Any]:
    """
    Pull recent Dallas commercial permits for research context.

    Returns a digest-friendly dict (never raises). Falls back to a documented
    fixture when the endpoint is down.
    """
    try:
        where_bits = ["upper(land_use) like '%COMMERCIAL%'"]
        hint = (address_hint or "").strip().upper().replace("'", "''")
        kw = (keyword or "").strip().upper().replace("'", "''")
        if hint:
            # Match street token (e.g. MUNGER) when present
            token = hint.split(",")[0].strip()
            for part in token.split():
                if len(part) >= 4 and not part.isdigit():
                    where_bits.append(f"upper(address) like '%{part}%'")
                    break
        if kw:
            where_bits.append(f"upper(project_description) like '%{kw}%'")

        params = {
            "$where": " AND ".join(where_bits),
            "$limit": str(limit),
            "$order": "issue_date DESC",
        }
        headers = {}
        token = os.environ.get("DALLAS_OPEN_DATA_APP_TOKEN")
        if token:
            headers["X-App-Token"] = token

        response = requests.get(DALLAS_API_URL, params=params, headers=headers, timeout=25)
        if response.status_code != 200:
            logger.warning(f"Dallas Open Data {response.status_code}; using fixture summary")
            return _fixture_summary(address_hint)

        rows = response.json()
        if not isinstance(rows, list):
            return _fixture_summary(address_hint)
        return _summarize_rows(rows, live=True)
    except (RequestException, json.JSONDecodeError, ValueError) as exc:
        logger.warning(f"Dallas Open Data failed ({type(exc).__name__}): {exc}")
        return _fixture_summary(address_hint)


def _summarize_rows(rows: List[Dict[str, Any]], *, live: bool) -> Dict[str, Any]:
    slim = []
    for r in rows[:15]:
        if not isinstance(r, dict):
            continue
        slim.append(
            {
                "permit_number": r.get("permit_number") or r.get("permit_no"),
                "address": r.get("address"),
                "issue_date": r.get("issue_date"),
                "valuation": r.get("valuation"),
                "project_description": (r.get("project_description") or "")[:240],
                "land_use": r.get("land_use"),
            }
        )
    return {
        "source": "dallas_open_data_live" if live else "dallas_open_data_fixture",
        "socrata_url": DALLAS_API_URL,
        "count": len(slim),
        "permits": slim,
        "note": (
            "Recent Dallas commercial permits from Open Data. "
            "Use for locality context — confirm fees via Building Inspection schedule ($167 min trade sync)."
        ),
    }


def _fixture_summary(address_hint: str = "") -> Dict[str, Any]:
    return {
        "source": "dallas_open_data_fixture",
        "socrata_url": DALLAS_API_URL,
        "count": 1,
        "permits": [
            {
                "permit_number": "RG-MOCK-BL-722-MUNGER",
                "address": "722 MUNGER AVE",
                "issue_date": "2026-05-01T00:00:00.000",
                "valuation": "2500000",
                "project_description": (
                    "722 Munger Ave fixture — min trade permit planning fee USD $167.00 "
                    "(2026 Reg Guard sync). Live Open Data unavailable."
                ),
                "land_use": "COMMERCIAL",
            }
        ],
        "note": (
            f"Fixture used (live Socrata unavailable). Address hint: {address_hint or 'n/a'}. "
            "Still cite Dallas Building Inspection for the $167 minimum trade permit."
        ),
    }

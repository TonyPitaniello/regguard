"""
Persistent store for forwardable research reports.

Priority:
1. Supabase table ``research_reports`` when SUPABASE_URL/KEY are set
2. Local JSON files under ``data/research_reports/`` (works on Render disk / local)
3. Process-local memory cache for hot reads

Public reports strip contact PII (email/phone) before return.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

_LOCK = threading.RLock()
_MEMORY: Dict[str, Dict[str, Any]] = {}
_DEFAULT_TTL_DAYS = int(os.getenv("REG_GUARD_REPORT_TTL_DAYS", "90"))

# Strip from public payloads
_PII_KEYS = {"email", "phone", "phone_number", "user_email", "user_phone", "contact_email"}


def _store_dir() -> Path:
    base = Path(os.getenv("REG_GUARD_REPORT_DIR") or (Path(__file__).resolve().parent / "data" / "research_reports"))
    base.mkdir(parents=True, exist_ok=True)
    return base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_research_id(research_id: Optional[str] = None) -> str:
    """Return a filesystem/URL-safe research id."""
    if research_id:
        cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "", research_id.strip())[:80]
        if cleaned:
            return cleaned
    return f"rg-{uuid.uuid4().hex[:16]}"


def app_base_url() -> str:
    return (os.getenv("REG_GUARD_APP_URL") or "https://app.regguardagent.com").rstrip("/")


def share_url_for(research_id: str) -> str:
    return f"{app_base_url()}/r/{research_id}"


def _strip_pii(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k.lower() in _PII_KEYS:
                continue
            out[k] = _strip_pii(v)
        return out
    if isinstance(obj, list):
        return [_strip_pii(x) for x in obj]
    return obj


def public_analysis(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Copy analysis safe for public share pages and emails forwarded to GCs."""
    return _strip_pii(deepcopy(analysis or {}))


def _file_path(research_id: str) -> Path:
    return _store_dir() / f"{research_id}.json"


def _supabase_available() -> bool:
    return bool((os.getenv("SUPABASE_URL") or "").strip() and (os.getenv("SUPABASE_KEY") or "").strip())


def _supabase_upsert(record: Dict[str, Any]) -> bool:
    if not _supabase_available():
        return False
    try:
        from supabase import create_client

        sb = create_client(os.environ["SUPABASE_URL"].strip(), os.environ["SUPABASE_KEY"].strip())
        sb.table("research_reports").upsert(
            {
                "id": record["id"],
                "analysis": record["analysis"],
                "project_address": record.get("project_address"),
                "project_city": record.get("project_city"),
                "project_state": record.get("project_state"),
                "project_zip": record.get("project_zip"),
                "preview": bool(record.get("preview")),
                "created_at": record.get("created_at"),
                "expires_at": record.get("expires_at"),
                "updated_at": record.get("updated_at") or _iso(_utcnow()),
            }
        ).execute()
        return True
    except Exception as e:
        logger.warning(f"Supabase research_reports upsert failed (local store still used): {e}")
        return False


def _supabase_get(research_id: str) -> Optional[Dict[str, Any]]:
    if not _supabase_available():
        return None
    try:
        from supabase import create_client

        sb = create_client(os.environ["SUPABASE_URL"].strip(), os.environ["SUPABASE_KEY"].strip())
        resp = sb.table("research_reports").select("*").eq("id", research_id).limit(1).execute()
        rows = resp.data or []
        if not rows:
            return None
        row = rows[0]
        return {
            "id": row["id"],
            "analysis": row.get("analysis") or {},
            "project_address": row.get("project_address"),
            "project_city": row.get("project_city"),
            "project_state": row.get("project_state"),
            "project_zip": row.get("project_zip"),
            "preview": row.get("preview"),
            "created_at": row.get("created_at"),
            "expires_at": row.get("expires_at"),
            "share_url": share_url_for(row["id"]),
        }
    except Exception as e:
        logger.warning(f"Supabase research_reports get failed: {e}")
        return None


def save_research(
    analysis: Dict[str, Any],
    *,
    research_id: Optional[str] = None,
    ttl_days: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Persist analysis and return metadata including share_url.
    Always writes local file + memory; best-effort Supabase.
    """
    rid = normalize_research_id(research_id or analysis.get("research_id"))
    now = _utcnow()
    ttl = ttl_days if ttl_days is not None else _DEFAULT_TTL_DAYS
    expires = now + timedelta(days=max(1, ttl))

    clean = public_analysis(analysis)
    clean["research_id"] = rid

    project = clean.get("project_info") or {}
    record = {
        "id": rid,
        "analysis": clean,
        "project_address": project.get("address"),
        "project_city": project.get("city"),
        "project_state": project.get("state"),
        "project_zip": project.get("zip"),
        "preview": bool(clean.get("preview")),
        "created_at": _iso(now),
        "expires_at": _iso(expires),
        "updated_at": _iso(now),
        "share_url": share_url_for(rid),
    }

    with _LOCK:
        _MEMORY[rid] = record
        try:
            _file_path(rid).write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed writing local research report {rid}: {e}")

    _supabase_upsert(record)
    logger.info(f"Persisted research report {rid} → {record['share_url']}")
    return {
        "research_id": rid,
        "share_url": record["share_url"],
        "created_at": record["created_at"],
        "expires_at": record["expires_at"],
        "preview": record["preview"],
    }


def _expired(record: Dict[str, Any]) -> bool:
    expires = record.get("expires_at")
    if not expires:
        return False
    try:
        exp = datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
        return _utcnow() > exp
    except Exception:
        return False


def get_research(research_id: str) -> Optional[Dict[str, Any]]:
    """Return stored record or None. Skips expired records."""
    rid = normalize_research_id(research_id)
    with _LOCK:
        mem = _MEMORY.get(rid)
        if mem and not _expired(mem):
            return deepcopy(mem)
        if mem and _expired(mem):
            _MEMORY.pop(rid, None)

    # Local file
    path = _file_path(rid)
    if path.exists():
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if _expired(record):
                return None
            with _LOCK:
                _MEMORY[rid] = record
            return deepcopy(record)
        except Exception as e:
            logger.warning(f"Failed reading local report {rid}: {e}")

    remote = _supabase_get(rid)
    if remote:
        if _expired(remote):
            return None
        with _LOCK:
            _MEMORY[rid] = remote
        return deepcopy(remote)
    return None


def get_analysis(research_id: str) -> Optional[Dict[str, Any]]:
    record = get_research(research_id)
    if not record:
        return None
    analysis = record.get("analysis") or {}
    analysis["research_id"] = record.get("id") or research_id
    analysis["share_url"] = record.get("share_url") or share_url_for(research_id)
    return analysis


def extract_sources(analysis: Dict[str, Any]) -> list:
    """Collect citeable source URLs / labels from analysis payload."""
    sources = []
    seen = set()

    def add(label: str, url: str = ""):
        key = (label or "").strip().lower() + "|" + (url or "").strip().lower()
        if key in seen or (not label and not url):
            return
        seen.add(key)
        sources.append({"label": label or url, "url": url or ""})

    for url in analysis.get("source_urls") or []:
        if isinstance(url, str):
            add(url, url)
        elif isinstance(url, dict):
            add(url.get("title") or url.get("label") or url.get("url") or "", url.get("url") or "")

    env = analysis.get("environmental_screening") or {}
    for finding in env.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        for src in finding.get("data_sources") or []:
            if isinstance(src, str):
                add(src, src if src.startswith("http") else "")
            elif isinstance(src, dict):
                add(src.get("label") or src.get("title") or "", src.get("url") or "")

    for item in (analysis.get("punch_list") or {}).get("punch_list") or []:
        if isinstance(item, dict) and item.get("source_url"):
            add(item.get("source_label") or item.get("task") or "Source", item.get("source_url"))

    return sources[:40]

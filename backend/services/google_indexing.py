"""Google Indexing API — request crawl/index of new or updated URLs.

Limit: 200 URL/day per project (Google enforced). Owner-level Search Console required.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database import db
from services.api_cost_tracker import track_api_usage
from services.google_common import load_credentials

logger = logging.getLogger(__name__)

SCOPES = ("https://www.googleapis.com/auth/indexing",)


def _client():
    creds = load_credentials(SCOPES)
    if not creds:
        return None
    return build("indexing", "v3", credentials=creds, cache_discovery=False)


@track_api_usage("google_indexing", "submit")
async def submit_url(url: str, action: str = "URL_UPDATED") -> Dict[str, Any]:
    """action: URL_UPDATED (default) or URL_DELETED."""
    idx = _client()
    if not idx:
        return {"ok": False, "error": "service_account_not_configured"}
    if action not in ("URL_UPDATED", "URL_DELETED"):
        return {"ok": False, "error": "invalid_action"}
    try:
        r = idx.urlNotifications().publish(
            body={"url": url, "type": action}
        ).execute()
        await db.indexing_log.insert_one({
            "url": url,
            "action": action,
            "result": r,
            "ts": datetime.now(timezone.utc),
        })
        return {"ok": True, "url": url, "action": action, "result": r}
    except HttpError as e:
        await db.indexing_log.insert_one({
            "url": url, "action": action, "error": e._get_reason(),
            "ts": datetime.now(timezone.utc),
        })
        return {"ok": False, "url": url, "error": e._get_reason()}


async def submit_batch(urls: List[str], action: str = "URL_UPDATED") -> Dict[str, Any]:
    """Submit up to 100 URLs sequentially. Stop early if quota exceeded."""
    submitted, failed = [], []
    for u in urls[:100]:
        r = await submit_url(u, action)
        if r.get("ok"):
            submitted.append(u)
        else:
            failed.append({"url": u, "error": r.get("error")})
            if "quota" in str(r.get("error", "")).lower():
                break
    return {"submitted": submitted, "failed": failed, "submitted_count": len(submitted), "failed_count": len(failed)}


@track_api_usage("google_indexing", "metadata")
async def get_metadata(url: str) -> Dict[str, Any]:
    """Get last indexing notification status for a URL."""
    idx = _client()
    if not idx:
        return {"error": "service_account_not_configured"}
    try:
        return idx.urlNotifications().getMetadata(url=url).execute()
    except HttpError as e:
        return {"error": e._get_reason()}


async def history(limit: int = 100) -> Dict[str, Any]:
    """Recent submissions log."""
    rows = await db.indexing_log.find(
        {}, {"_id": 0}
    ).sort("ts", -1).limit(limit).to_list(limit)
    for r in rows:
        if isinstance(r.get("ts"), datetime):
            r["ts"] = r["ts"].isoformat()
    return {"rows": rows, "total": len(rows)}

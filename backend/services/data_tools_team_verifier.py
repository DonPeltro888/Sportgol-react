"""
Weekly Team & Logo AI Verifier (Perplexity Sonar Pro).

Per ogni team in DB:
1. Chiede a Perplexity Sonar Pro: dati ufficiali aggiornati (founded, stadium, city, country, official_logo_url)
2. Confronta con DB
3. Flag changes: roster cambiato, stadium nuovo (es. nuovo stadio AC Milan 2027), logo refresh
4. (opzionale) auto-update non distruttivo (i campi che non cambiano vengono lasciati)

Costo: ~250 teams × Perplexity Sonar Pro (~$0.005/call) = ~$1.25 a run settimanale.
"""
import json
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import httpx
from rapidfuzz import fuzz

from database import db
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)

DRIFT_THRESHOLD_FUZZ = 75  # se i campi text differiscono >25% lo segnaliamo


async def _verify_one_team(team: Dict[str, Any], api_key: str) -> Optional[Dict[str, Any]]:
    name = team.get("name") or ""
    league_slug = team.get("league_slug") or ""
    if not name:
        return None

    prompt = (
        f"Provide CURRENT official information about the football club '{name}' (league: {league_slug}). "
        f"Return ONLY a JSON object with EXACTLY these keys (no markdown, no explanations): "
        f'{{"name":"current official name","founded":"YYYY","stadium":"current home stadium full name",'
        f'"capacity":12345,"city":"city","country":"country","official_logo_url":"url to current crest png/svg",'
        f'"recent_changes_summary":"any roster/stadium/logo changes in last 2 years, max 100 words"}}. '
        f"Use most authoritative source (Wikipedia, club official website, UEFA). If unknown, use null."
    )
    body = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
        "temperature": 0.0,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=60) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code not in (200, 201):
            return None
        text = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Team verifier {name}: {e}")
        return None

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        ai = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None

    # Compare AI vs DB
    drifts: List[Dict[str, Any]] = []
    for fld in ("stadium", "city", "country"):
        db_v = (team.get(fld) or "").strip()
        ai_v = (ai.get(fld) or "").strip() if ai.get(fld) else ""
        if not ai_v:
            continue
        if not db_v:
            drifts.append({"field": fld, "db_value": db_v, "ai_value": ai_v, "type": "MISSING_IN_DB"})
        elif fuzz.token_set_ratio(db_v.lower(), ai_v.lower()) < DRIFT_THRESHOLD_FUZZ:
            drifts.append({"field": fld, "db_value": db_v, "ai_value": ai_v, "type": "DRIFT"})

    # Logo url freshness
    db_logo = team.get("logo_url") or team.get("logo")
    ai_logo = ai.get("official_logo_url") or ""
    logo_drift = False
    if db_logo and ai_logo and db_logo != ai_logo:
        # Only flag if visually-suggesting URL change (not just CDN swap)
        if not (db_logo in ai_logo or ai_logo in db_logo):
            logo_drift = True
            drifts.append({"field": "logo_url", "db_value": db_logo, "ai_value": ai_logo, "type": "LOGO_CHANGED"})

    return {
        "team_slug": team.get("slug"),
        "team_name": name,
        "league_slug": league_slug,
        "ai_data": ai,
        "drifts": drifts,
        "drift_count": len(drifts),
        "needs_review": len(drifts) > 0,
        "logo_drift": logo_drift,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


async def verify_all_teams(limit: int = 250, only_with_drift: bool = False) -> Dict[str, Any]:
    api_key = await get_api_key("perplexity")
    if not api_key:
        return {"error": "Perplexity API key non configurata"}

    cursor = db.teams.find({}, {"_id": 0, "slug": 1, "name": 1, "league_slug": 1,
                                "stadium": 1, "city": 1, "country": 1, "logo_url": 1, "logo": 1}).limit(limit)
    teams = await cursor.to_list(limit)

    results: List[Dict[str, Any]] = []
    for t in teams:
        try:
            res = await _verify_one_team(t, api_key)
            if res:
                if only_with_drift and not res["needs_review"]:
                    continue
                results.append(res)
        except Exception as e:
            logger.warning(f"team verifier error for {t.get('name')}: {e}")

    # Persist log
    summary = {
        "source": "team_verifier",
        "total_checked": len(results),
        "teams_with_drift": sum(1 for r in results if r["needs_review"]),
        "logo_drifts": sum(1 for r in results if r["logo_drift"]),
        "results": results,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    await db.team_verifier_logs.insert_one({**summary, "log_at": datetime.now(timezone.utc)})
    return summary


async def latest_report() -> Dict[str, Any]:
    last = await db.team_verifier_logs.find_one(
        {}, {"_id": 0}, sort=[("log_at", -1)]
    )
    return last or {"error": "Nessun report disponibile. Lancia una verifica."}

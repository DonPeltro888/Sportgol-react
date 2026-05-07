"""
SEO Health Auto-fix — applica correzioni in modo BILANCIATO:
- Aggiunge dati mancanti (stadium/city/country/league_slug) se Perplexity li fornisce
- Sostituisce logo SOLO se Gemini Vision dice "no" con confidence >= 0.7
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from database import db
from services import seo_ai_validator

logger = logging.getLogger(__name__)
HIGH_CONFIDENCE = 0.7


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def fix_team(slug: str, mode: str = "balanced") -> Dict[str, Any]:
    """
    mode:
    - 'balanced': fill missing + replace logo if Gemini says "no" with confidence >= 0.7
    - 'safe': solo fill missing, mai sostituire logo
    """
    team = await db.teams.find_one({"slug": slug}, {"_id": 0})
    if not team:
        return {"ok": False, "error": "Team not found"}

    name = team.get("name", "")
    league_hint = team.get("league_slug", "") or team.get("league", "")
    actions: List[str] = []
    update: Dict[str, Any] = {}

    # 1. Fill missing fields via Perplexity
    needs_meta = not team.get("stadium") or not team.get("city") or not team.get("country") or not team.get("league_slug")
    perplexity_data = {}
    if needs_meta:
        perplexity_data = await seo_ai_validator.validate_team_via_perplexity(name, league_hint)
        if perplexity_data:
            if not team.get("stadium") and perplexity_data.get("stadium"):
                update["stadium"] = perplexity_data["stadium"]
                actions.append(f"+stadium: {perplexity_data['stadium']}")
            if not team.get("city") and perplexity_data.get("city"):
                update["city"] = perplexity_data["city"]
                actions.append(f"+city: {perplexity_data['city']}")
            if not team.get("country") and perplexity_data.get("country"):
                update["country"] = perplexity_data["country"]
                actions.append(f"+country: {perplexity_data['country']}")

    # 2. Logo verification + replacement
    logo_check = None
    current_logo = team.get("logo_url", "")
    if mode == "balanced":
        if current_logo:
            logo_check = await seo_ai_validator.verify_logo_with_gemini(name, current_logo)
            if logo_check.get("match") == "no" and logo_check.get("confidence", 0) >= HIGH_CONFIDENCE:
                # Cerca alternativa
                alt = await seo_ai_validator.find_alternative_logo(name)
                if alt and alt != current_logo:
                    update["logo_url"] = alt
                    update["logo_url_previous"] = current_logo
                    actions.append(f"~logo: replaced (Gemini detected {logo_check.get('detected_team', 'wrong')}) → {alt[:80]}")
        elif not current_logo:
            # Missing logo: trova nuovo
            alt = await seo_ai_validator.find_alternative_logo(name)
            if alt:
                update["logo_url"] = alt
                actions.append(f"+logo: {alt[:80]}")

    if update:
        update["health_fixed_at"] = _now_iso()
        await db.teams.update_one({"slug": slug}, {"$set": update})
        # Audit log
        await db.health_fixes.insert_one({
            "ts": _now_iso(),
            "team_slug": slug,
            "team_name": name,
            "mode": mode,
            "actions": actions,
            "logo_check": logo_check,
            "perplexity_data_keys": list(perplexity_data.keys()) if perplexity_data else [],
        })

    return {
        "ok": True,
        "slug": slug,
        "name": name,
        "actions": actions,
        "applied": len(update) > 0,
        "logo_check": logo_check,
    }


async def fix_bulk(slugs: List[str], mode: str = "balanced") -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    fixed = 0
    for slug in slugs:
        try:
            r = await fix_team(slug, mode=mode)
            results.append(r)
            if r.get("applied"):
                fixed += 1
        except Exception as e:
            logger.error(f"fix_team {slug} fail: {e}")
            results.append({"ok": False, "slug": slug, "error": str(e)})
    return {"total": len(slugs), "fixed": fixed, "results": results}

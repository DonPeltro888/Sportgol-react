"""
AI Validator — Perplexity per metadati team + Gemini Vision per logo verification.
"""
import os
import json
import re
import base64
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv
from pathlib import Path

from database import db
from services.seo_keys import get_api_key

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
logger = logging.getLogger(__name__)


async def validate_team_via_perplexity(team_name: str, league_hint: str = "") -> Dict[str, Any]:
    """
    Chiede a Perplexity i metadati ufficiali del team.
    Cache 30gg in db.team_validation_cache.
    """
    if not team_name:
        return {}
    cache_key = f"{team_name.lower()}|{league_hint.lower()}"
    cached = await db.team_validation_cache.find_one({"_id": cache_key}, {"_id": 0})
    if cached and (datetime.now(timezone.utc).timestamp() - cached.get("ts", 0)) < 30 * 86400:
        return cached.get("data", {})

    api_key = await get_api_key("perplexity")
    if not api_key:
        return {}

    prompt = (
        f"Fornisci i metadati UFFICIALI della squadra di calcio '{team_name}'"
        f"{' (lega: ' + league_hint + ')' if league_hint else ''}. "
        "Restituisci SOLO un JSON valido senza markdown nel formato esatto:\n"
        '{"official_name": "Inter Milan", "stadium": "Giuseppe Meazza", '
        '"city": "Milano", "country": "IT", "league": "Serie A", '
        '"wikipedia_url": "https://it.wikipedia.org/wiki/...", '
        '"official_website": "https://www.inter.it", '
        '"logo_url": "https://.../inter-logo.png"}\n'
        "Per logo_url usa preferibilmente Wikipedia/Wikidata Commons. "
        "Se non sei sicuro al 100% di un campo, omettilo."
    )
    body = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=45) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code in (200, 201):
            text = r.json()["choices"][0]["message"]["content"]
            text = text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```\w*\n?", "", text)
                text = re.sub(r"\n?```$", "", text).strip()
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                data = json.loads(m.group(0))
                if isinstance(data, dict):
                    await db.team_validation_cache.update_one(
                        {"_id": cache_key},
                        {"$set": {"data": data, "ts": datetime.now(timezone.utc).timestamp()}},
                        upsert=True,
                    )
                    return data
        else:
            logger.warning(f"Perplexity validate HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"validate_team_via_perplexity error: {e}")
    return {}


async def verify_logo_with_gemini(team_name: str, logo_url: str) -> Dict[str, Any]:
    """
    Usa Gemini Vision per verificare se logo_url è davvero il logo di team_name.
    Ritorna {match: 'yes'|'no'|'uncertain', confidence: 0-1, reason}.
    """
    if not team_name or not logo_url:
        return {"match": "uncertain", "confidence": 0, "reason": "missing inputs"}

    em_key = os.getenv("EMERGENT_LLM_KEY")
    if not em_key:
        return {"match": "uncertain", "confidence": 0, "reason": "EMERGENT_LLM_KEY missing"}

    # Download logo
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as cx:
            r = await cx.get(logo_url)
        if r.status_code != 200 or not r.content:
            return {"match": "uncertain", "confidence": 0, "reason": f"logo fetch HTTP {r.status_code}"}
        img_b64 = base64.b64encode(r.content).decode("utf-8")
    except Exception as e:
        return {"match": "uncertain", "confidence": 0, "reason": f"logo download fail: {e}"}

    # Use emergentintegrations LlmChat
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        chat = LlmChat(
            api_key=em_key,
            session_id=f"logo-verify-{team_name.lower().replace(' ', '-')}",
            system_message="You are an expert football logo identifier."
        )
        chat.with_model("gemini", "gemini-2.5-pro")
        prompt = (
            f"Analyze this image and tell me: is this the OFFICIAL logo/badge of the football team '{team_name}'? "
            "Look at colors, shape, letters, animals, symbols. "
            "Respond ONLY with a valid JSON object: "
            '{"match": "yes" | "no" | "uncertain", "confidence": 0.0 to 1.0, '
            '"reason": "short explanation", "detected_team": "name of team you see in logo (if recognizable)"}. '
            "No markdown, no code fences."
        )
        msg = UserMessage(text=prompt, file_contents=[ImageContent(image_base64=img_b64)])
        response = await chat.send_message(msg)
        text = (response or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            if isinstance(data, dict):
                return {
                    "match": data.get("match", "uncertain"),
                    "confidence": float(data.get("confidence") or 0),
                    "reason": data.get("reason", "")[:200],
                    "detected_team": data.get("detected_team", "")[:100],
                }
    except Exception as e:
        logger.error(f"verify_logo_with_gemini error: {e}")
        return {"match": "uncertain", "confidence": 0, "reason": str(e)[:200]}

    return {"match": "uncertain", "confidence": 0, "reason": "no parseable response"}


async def find_alternative_logo(team_name: str) -> Optional[str]:
    """
    Cerca un logo URL alternativo:
    1. Perplexity validate → wikipedia_url + logo_url
    2. TheSportsDB API search by name
    """
    val = await validate_team_via_perplexity(team_name)
    if val.get("logo_url"):
        return val["logo_url"]
    # TheSportsDB fallback
    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.get(f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}")
        if r.status_code == 200:
            d = r.json()
            for team in (d.get("teams") or []):
                badge = team.get("strBadge") or team.get("strTeamBadge")
                if badge and team.get("strSport", "").lower() == "soccer":
                    return badge
    except Exception as e:
        logger.warning(f"TheSportsDB lookup fail: {e}")
    return None

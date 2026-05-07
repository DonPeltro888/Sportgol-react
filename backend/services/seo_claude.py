"""
Anthropic Claude — copywriting master IT con tono persuasivo per ticketing.
"""
import json
import logging
import httpx
from typing import Dict, Any, Optional
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)
MODEL = "claude-sonnet-4-5"
MAX_RETRIES = 2


async def generate_master_it(target_type: str, ctx: Dict[str, Any], keywords: Optional[Dict] = None) -> Dict[str, str]:
    """
    Genera in un'unica chiamata: meta_title, meta_description, h1, intro_text,
    main_content, cta_text. Output JSON strutturato.
    """
    api_key = await get_api_key("claude")
    if not api_key:
        return {}

    keyword = (keywords or {}).get("primary") or ctx.get("title") or ""
    related = ", ".join((keywords or {}).get("related", [])[:5])

    prompt = _build_prompt(target_type, ctx, keyword, related)

    body = {
        "model": MODEL,
        "max_tokens": 2200,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=90) as cx:
                r = await cx.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
            if r.status_code == 200:
                data = r.json()
                text = data["content"][0]["text"]
                return _parse_json(text)
            logger.warning(f"Claude HTTP {r.status_code}: {r.text[:200]}")
        except Exception as e:
            logger.error(f"Claude call failed (attempt {attempt+1}): {e}")
    return {}


def _build_prompt(target_type: str, ctx: Dict[str, Any], keyword: str, related: str) -> str:
    title = ctx.get("title") or "?"
    common_rules = (
        "Tono: professionale, persuasivo, da ticketing premium (in stile SeatPick/Vivaticket). "
        "Inserisci EEAT signals (sicurezza, garanzia biglietti, settori). "
        "Lingua: italiano impeccabile. NON usare frasi tipo 'come AI' o disclaimer.\n\n"
        "Restituisci SOLO un JSON valido (no markdown, no commenti) con questa struttura ESATTA:\n"
        "{\n"
        '  "meta_title": "max 60 caratteri",\n'
        '  "meta_description": "max 160 caratteri",\n'
        '  "h1": "titolo H1",\n'
        '  "intro_text": "150-250 parole, tono caloroso, 1-2 keyword target",\n'
        '  "main_content": "400-600 parole con paragrafi separati da \\n\\n; struttura: descrizione → mappa stadio → prezzi medi → guida acquisto",\n'
        '  "cta_text": "1 frase d\'invito all\'azione, max 80 char"\n'
        "}\n"
    )

    if target_type == "event":
        home = ctx.get("home_team", "")
        away = ctx.get("away_team", "")
        venue = ctx.get("stadium") or ctx.get("location", "")
        date = ctx.get("date", "")
        league = ctx.get("league", "")
        return (
            f"Sei un Senior SEO Copywriter per un portale di biglietti calcio.\n\n"
            f"Match: {home} vs {away}\n"
            f"Competizione: {league}\n"
            f"Stadio: {venue}\n"
            f"Data: {date}\n"
            f"Keyword principale: {keyword}\n"
            f"Keyword correlate: {related}\n\n"
            f"{common_rules}\n"
            f"Il titolo H1 DEVE seguire il pattern: 'Biglietti {home} vs {away} | Confronta Prezzi e Posti'."
        )
    elif target_type == "league":
        return (
            f"Sei un Senior SEO Copywriter per un portale di biglietti calcio.\n\n"
            f"Lega: {title}\n"
            f"Paese: {ctx.get('country', '')}\n"
            f"Keyword principale: {keyword}\n"
            f"Keyword correlate: {related}\n\n"
            f"{common_rules}\n"
            f"Il titolo H1 DEVE seguire il pattern: 'Biglietti {title} 2025/26 | Calendario Match e Prezzi'."
        )
    else:  # team
        return (
            f"Sei un Senior SEO Copywriter per un portale di biglietti calcio.\n\n"
            f"Squadra: {title}\n"
            f"Lega: {ctx.get('league_slug', '')}\n"
            f"Stadio: {ctx.get('stadium', '')}\n"
            f"Keyword principale: {keyword}\n"
            f"Keyword correlate: {related}\n\n"
            f"{common_rules}\n"
            f"Il titolo H1 DEVE seguire il pattern: 'Biglietti {title} | Tutte le Partite Casa e Trasferta'."
        )


def _parse_json(text: str) -> Dict[str, str]:
    """Rimuove markdown fences eventuali e parsa JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except Exception as e:
        logger.error(f"Claude JSON parse error: {e}\nText: {text[:300]}")
        return {}

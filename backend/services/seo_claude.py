"""
Anthropic Claude — copywriting master IT con tono persuasivo per ticketing.
Output esteso: meta+h1+intro+main_content+cta+og_*+internal_links+image_alt_texts+legal_disclosure_text.
"""
import json
import logging
import re
import httpx
from typing import Dict, Any, Optional, List
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)
MODEL = "claude-sonnet-4-5"
MAX_RETRIES = 2


async def generate_master_it(
    target_type: str,
    ctx: Dict[str, Any],
    keywords: Optional[Dict] = None,
    related_entities: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Genera in un'unica chiamata l'intero blocco master IT.
    Output JSON strutturato con tutti i campi SEO + internal_links + image_alt_texts.
    """
    api_key = await get_api_key("claude")
    if not api_key:
        logger.warning("Claude API key not configured")
        return {}

    keyword = (keywords or {}).get("primary") or ctx.get("title") or ""
    related = ", ".join((keywords or {}).get("related", [])[:5])
    related_entities = related_entities or []

    prompt = _build_prompt(target_type, ctx, keyword, related, related_entities)

    body = {
        "model": MODEL,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    last_error = ""
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=120) as cx:
                r = await cx.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
            if r.status_code == 200:
                data = r.json()
                text = data["content"][0]["text"]
                parsed = _parse_json(text)
                if parsed:
                    return parsed
                last_error = "Empty/invalid JSON"
            else:
                last_error = f"HTTP {r.status_code}: {r.text[:200]}"
                logger.warning(f"Claude {last_error}")
        except Exception as e:
            last_error = str(e)
            logger.error(f"Claude call failed (attempt {attempt+1}): {e}")
    logger.error(f"Claude FINAL FAIL: {last_error}")
    return {}


def _build_prompt(
    target_type: str,
    ctx: Dict[str, Any],
    keyword: str,
    related: str,
    related_entities: List[Dict[str, str]],
) -> str:
    title = ctx.get("title") or "?"

    # Lista entità correlate per internal linking
    related_block = "Nessuna entità correlata."
    if related_entities:
        items = []
        for e in related_entities[:8]:
            url = e.get("url", "")
            label = e.get("label", "")
            kind = e.get("kind", "")
            if url and label:
                items.append(f"- [{kind}] {label} → {url}")
        if items:
            related_block = "\n".join(items)

    json_schema = """{
  "meta_title": "max 60 caratteri, include keyword principale",
  "meta_description": "max 155 caratteri, persuasiva, include keyword + CTA",
  "h1": "titolo H1 secondo pattern indicato",
  "intro_text": "150-220 parole, tono caloroso EEAT, 1-2 keyword target",
  "main_content": "400-600 parole, paragrafi separati da \\n\\n; struttura: descrizione → mappa stadio → settori e prezzi medi → guida acquisto → garanzie",
  "cta_text": "1 frase invito all'azione, max 80 char",
  "open_graph_title": "max 70 char, accattivante per social",
  "open_graph_description": "max 200 char, social-friendly",
  "twitter_card_title": "max 70 char, conciso",
  "twitter_card_description": "max 200 char",
  "internal_links": [
    {"url": "/biglietti-...", "anchor": "anchor text naturale che include keyword"}
  ],
  "image_alt_texts": [
    "Alt text descrittivo immagine 1 (logo/team/stadio)",
    "Alt text descrittivo immagine 2",
    "Alt text descrittivo immagine 3"
  ],
  "legal_disclosure_text": "1-2 frasi disclosure resale: 'I biglietti sono offerti tramite mercato secondario; i prezzi possono essere superiori al valore nominale.' adattata al contesto"
}"""

    common_rules = (
        f"OUTPUT JSON OBBLIGATORIO con questa struttura ESATTA (no markdown, no commenti):\n{json_schema}\n\n"
        "REGOLE:\n"
        "- Tono: professionale, persuasivo, da ticketing premium (in stile SeatPick/Vivaticket).\n"
        "- Inserisci EEAT signals (sicurezza, garanzia biglietti, mappa settori, supporto 7/7).\n"
        "- Lingua: italiano impeccabile. NON usare 'come AI' o disclaimer.\n"
        "- internal_links: 5-8 link ESCLUSIVAMENTE dalla lista entità correlate fornita; "
        "anchor text variati naturali che includono keyword pertinenti (NON stuffing).\n"
        "- image_alt_texts: 3-5 alt text descrittivi e contestuali (logo, stadio, tifosi, settori).\n"
        "- legal_disclosure_text: BREVE (1-2 frasi) in italiano, indica natura resale e conformità DDL 145/2018.\n"
    )

    if target_type == "event":
        home = ctx.get("home_team", "")
        away = ctx.get("away_team", "")
        venue = ctx.get("stadium") or ctx.get("location", "")
        date = ctx.get("date", "")
        league = ctx.get("league", "")
        return (
            f"Sei un Senior SEO Copywriter per portale di biglietti calcio.\n\n"
            f"Match: {home} vs {away}\n"
            f"Competizione: {league}\n"
            f"Stadio: {venue}\n"
            f"Data: {date}\n"
            f"Keyword principale: {keyword}\n"
            f"Keyword correlate: {related}\n"
            f"Entità correlate (USA SOLO QUESTI URL per internal_links):\n{related_block}\n\n"
            f"Pattern H1 OBBLIGATORIO: 'Biglietti {home} vs {away} | Confronta Prezzi e Posti'.\n\n"
            f"{common_rules}"
        )
    elif target_type == "league":
        return (
            f"Sei un Senior SEO Copywriter per portale di biglietti calcio.\n\n"
            f"Lega: {title}\n"
            f"Paese: {ctx.get('country', '')}\n"
            f"Keyword principale: {keyword}\n"
            f"Keyword correlate: {related}\n"
            f"Entità correlate (USA SOLO QUESTI URL per internal_links):\n{related_block}\n\n"
            f"Pattern H1 OBBLIGATORIO: 'Biglietti {title} 2025/26 | Calendario Match e Prezzi'.\n\n"
            f"{common_rules}"
        )
    else:  # team
        stadium = ctx.get("stadium", "")
        league = ctx.get("league", "") or ctx.get("league_slug", "")
        return (
            f"Sei un Senior SEO Copywriter per portale di biglietti calcio.\n\n"
            f"Squadra: {title}\n"
            f"Lega: {league}\n"
            f"Stadio: {stadium}\n"
            f"Keyword principale: {keyword}\n"
            f"Keyword correlate: {related}\n"
            f"Entità correlate (USA SOLO QUESTI URL per internal_links):\n{related_block}\n\n"
            f"Pattern H1 OBBLIGATORIO: 'Biglietti {title} | Tutte le Partite Casa e Trasferta'.\n\n"
            f"{common_rules}"
        )


def _parse_json(text: str) -> Dict[str, Any]:
    """Rimuove markdown fences e parsa JSON. Estrae il primo blocco {...}."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    # Estrai il primo oggetto JSON valido
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        text = m.group(0)
    try:
        return json.loads(text)
    except Exception as e:
        logger.error(f"Claude JSON parse error: {e}\nText: {text[:300]}")
        return {}

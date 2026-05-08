"""
Perplexity Sonar — live research per:
- FAQ "People Also Ask"
- Geo coordinates stadium (lat/lon + city + postal_code)
- sameAs Wikipedia/Wikidata URL
"""
import json
import logging
import re
import time
import httpx
from typing import List, Dict, Any, Optional
from services.seo_keys import get_api_key
from services.api_cost_tracker import manual_log

logger = logging.getLogger(__name__)


async def _call_sonar(prompt: str, max_tokens: int = 600, sub_type: str = "sonar") -> str:
    api_key = await get_api_key("perplexity")
    if not api_key:
        return ""
    body = {
        "model": sub_type,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=45) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        latency = int((time.time() - t0) * 1000)
        if r.status_code in (200, 201):
            await manual_log("perplexity", sub_type, "request",
                              units_used=1, status="ok", latency_ms=latency,
                              function="perplexity._call_sonar", http_status=r.status_code)
            return r.json()["choices"][0]["message"]["content"]
        await manual_log("perplexity", sub_type, "request",
                          status="failed", latency_ms=latency,
                          function="perplexity._call_sonar",
                          http_status=r.status_code, response_body_preview=r.text[:300])
        logger.warning(f"Perplexity HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        latency = int((time.time() - t0) * 1000)
        await manual_log("perplexity", sub_type, "request",
                          status="failed", latency_ms=latency, error_msg=str(e)[:300],
                          function="perplexity._call_sonar")
        logger.error(f"Perplexity error: {e}")
    return ""


async def lookup_geo(stadium: str) -> Optional[Dict[str, Any]]:
    """Restituisce {latitude, longitude, city, country, postal_code} per uno stadio."""
    if not stadium:
        return None
    prompt = (
        f"Trova le coordinate geografiche dello stadio '{stadium}'. "
        "Restituisci SOLO un JSON valido senza markdown nel formato esatto: "
        '{"latitude": 45.4781, "longitude": 9.1240, "city": "Milano", '
        '"country": "IT", "postal_code": "20151"}. '
        "Se non sei sicuro al 100% delle coordinate, restituisci {}."
    )
    text = await _call_sonar(prompt, max_tokens=300)
    if not text:
        return None
    text = _strip_fences(text)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        if isinstance(d, dict) and d.get("latitude") and d.get("longitude"):
            return {
                "latitude": float(d["latitude"]),
                "longitude": float(d["longitude"]),
                "city": d.get("city"),
                "country": d.get("country") or "IT",
                "postal_code": d.get("postal_code"),
            }
    except Exception as e:
        logger.error(f"lookup_geo parse error: {e}")
    return None


async def lookup_same_as(entity_name: str, kind: str = "team") -> List[str]:
    """Restituisce URL Wikipedia/Wikidata/sito ufficiale per l'entità."""
    if not entity_name:
        return []
    prompt = (
        f"Per la {'squadra di calcio' if kind=='team' else 'lega/competizione di calcio'} "
        f"'{entity_name}' restituisci SOLO un JSON array con gli URL ufficiali "
        "(Wikipedia italiano + Wikidata + sito ufficiale + Twitter ufficiale). "
        'Esempio: ["https://it.wikipedia.org/wiki/...", "https://www.wikidata.org/wiki/...", '
        '"https://www.acmilan.com", "https://twitter.com/acmilan"]. '
        "Se non sei certo di un URL, OMETTILO. Niente markdown."
    )
    text = await _call_sonar(prompt, max_tokens=400)
    if not text:
        return []
    text = _strip_fences(text)
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        return []
    try:
        arr = json.loads(m.group(0))
        if isinstance(arr, list):
            urls = [u for u in arr if isinstance(u, str) and u.startswith("http")]
            return urls[:5]
    except Exception as e:
        logger.error(f"lookup_same_as parse error: {e}")
    return []


def _strip_fences(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


async def fetch_paa_faq(target_type: str, ctx: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Restituisce 3 FAQ {q, a} dalle "People Also Ask" di Google.
    Default mock realistico se Perplexity non disponibile.
    """
    api_key = await get_api_key("perplexity")
    if not api_key:
        return _fallback_faq(target_type, ctx)

    title = ctx.get("title") or "?"
    if target_type == "event":
        h, a = ctx.get("home_team", ""), ctx.get("away_team", "")
        topic = f"biglietti {h} vs {a}"
    elif target_type == "league":
        topic = f"biglietti {title} stadio prezzi"
    else:
        topic = f"biglietti {title} stadio settori"

    prompt = (
        f"Fornisci le 3 domande più cercate su Google ('People Also Ask') riguardo: '{topic}'. "
        "Per ognuna scrivi una risposta concisa (max 250 caratteri) in italiano. "
        "Restituisci SOLO un JSON valido senza markdown nel formato: "
        '[{"q":"...","a":"..."},{"q":"...","a":"..."},{"q":"...","a":"..."}]'
    )

    body = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
        "temperature": 0.3,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=45) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code in (200, 201):
            data = r.json()
            text = data["choices"][0]["message"]["content"]
            return _parse_faq_array(text) or _fallback_faq(target_type, ctx)
        logger.warning(f"Perplexity HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"Perplexity error: {e}")
    return _fallback_faq(target_type, ctx)


def _parse_faq_array(text: str) -> List[Dict[str, str]]:
    text = text.strip()
    # Strip markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    # Extract first JSON array
    m = re.search(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)
    if m:
        text = m.group(0)
    try:
        arr = json.loads(text)
        if isinstance(arr, list):
            return [{"q": x.get("q", ""), "a": x.get("a", "")} for x in arr if isinstance(x, dict)][:3]
    except Exception as e:
        logger.error(f"Perplexity JSON parse error: {e}\nText: {text[:200]}")
    return []


def _fallback_faq(target_type: str, ctx: Dict[str, Any]) -> List[Dict[str, str]]:
    title = ctx.get("title") or "?"
    if target_type == "event":
        h = ctx.get("home_team", "")
        a = ctx.get("away_team", "")
        return [
            {"q": f"Quanto costano i biglietti per {h} vs {a}?",
             "a": f"I prezzi per {h} vs {a} variano in base al settore: si parte dalle tribune popolari (~50€) fino ai posti premium (~200€). Su Golevents puoi confrontare tutte le opzioni disponibili."},
            {"q": f"Dove si gioca {h} vs {a}?",
             "a": f"La partita si gioca presso {ctx.get('stadium','lo stadio ufficiale')}. Trovi mappa interattiva e indicazioni sulla pagina dell'evento."},
            {"q": f"I biglietti per {h} vs {a} sono ancora disponibili?",
             "a": "Sì, su Golevents trovi i biglietti aggiornati in tempo reale con le migliori offerte verificate. Acquisto sicuro e garantito."},
        ]
    if target_type == "league":
        return [
            {"q": f"Come comprare biglietti per la {title}?",
             "a": f"Su Golevents trovi tutti i biglietti ufficiali per la {title} 2025/26 con confronto prezzi e settori in tempo reale."},
            {"q": f"Quali sono le squadre della {title}?",
             "a": f"La {title} include i top club del campionato. Sulla nostra pagina trovi la lista completa con link diretti ai biglietti."},
            {"q": f"I biglietti per la {title} sono garantiti?",
             "a": "Tutti i biglietti su Golevents sono garantiti al 100% con assicurazione anti-frode e supporto clienti 7/7."},
        ]
    # team
    return [
        {"q": f"Dove comprare biglietti {title}?",
         "a": f"Su Golevents trovi tutti i biglietti ufficiali per i match casa e trasferta del {title} con prezzi aggiornati."},
        {"q": f"Quanto costano i biglietti {title}?",
         "a": f"I prezzi per i match del {title} partono da ~30€ per le curve fino a ~250€ per i posti premium. Confronta su Golevents."},
        {"q": f"Posso scegliere il settore per {title}?",
         "a": "Sì, sulla pagina di ogni match trovi la mappa interattiva dello stadio per scegliere il tuo settore preferito."},
    ]

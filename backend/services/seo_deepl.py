"""
DeepL — traduzione professionale IT→EN/ES con glossario tecnico.
Free tier: 500k char/mese (key suffisso :fx → endpoint api-free.deepl.com).
"""
import logging
from typing import Dict, List, Any
import httpx
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)

# Glossario tecnico (post-translation override) — DeepL Free non supporta glossari API
GLOSSARY: Dict[str, Dict[str, str]] = {
    "en": {
        "Settore Ospiti": "Away Section",
        "Settore Tifosi": "Home Section",
        "Curva Sud": "South Stand",
        "Curva Nord": "North Stand",
        "Tribuna": "Main Stand",
        "Distinti": "Side Stand",
        "Abbonati": "Season Ticket Holders",
        "Settori": "Sectors",
    },
    "es": {
        "Settore Ospiti": "Sector Visitante",
        "Settore Tifosi": "Sector Local",
        "Curva Sud": "Curva Sur",
        "Curva Nord": "Curva Norte",
        "Tribuna": "Tribuna",
        "Distinti": "Lateral",
        "Abbonati": "Abonados",
        "Settori": "Sectores",
    },
}


async def translate(text: str, target: str) -> str:
    """target: 'EN' o 'ES'. Restituisce stringa tradotta (vuoto se errore)."""
    if not text or not text.strip():
        return ""
    api_key = await get_api_key("deepl")
    if not api_key:
        return text  # fallback: ritorna originale

    base = "https://api-free.deepl.com" if api_key.endswith(":fx") else "https://api.deepl.com"
    headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
    data = {
        "text": text,
        "source_lang": "IT",
        "target_lang": target.upper(),
        "tag_handling": "html",
    }
    try:
        async with httpx.AsyncClient(timeout=45) as cx:
            r = await cx.post(f"{base}/v2/translate", headers=headers, data=data)
        if r.status_code == 200:
            translated = r.json()["translations"][0]["text"]
            return _apply_glossary(translated, target.lower())
        logger.warning(f"DeepL HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"DeepL error: {e}")
    return text


def _apply_glossary(text: str, lang: str) -> str:
    glossary = GLOSSARY.get(lang, {})
    for it_term, target_term in glossary.items():
        # Already translated by DeepL but force consistency
        text = text.replace(it_term, target_term)
    return text


async def translate_batch(texts: List[str], target: str) -> List[str]:
    """Traduzione di più stringhe con un solo round-trip (più economico)."""
    if not texts:
        return []
    api_key = await get_api_key("deepl")
    if not api_key:
        return list(texts)

    base = "https://api-free.deepl.com" if api_key.endswith(":fx") else "https://api.deepl.com"
    headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
    # httpx async requires dict (not list of tuples) for form data
    form: Dict[str, Any] = {
        "text": [t or " " for t in texts],
        "source_lang": "IT",
        "target_lang": target.upper(),
        "tag_handling": "html",
    }
    try:
        async with httpx.AsyncClient(timeout=60) as cx:
            r = await cx.post(f"{base}/v2/translate", headers=headers, data=form)
        if r.status_code == 200:
            translations = [t["text"] for t in r.json()["translations"]]
            return [_apply_glossary(t, target.lower()) for t in translations]
        logger.warning(f"DeepL batch HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"DeepL batch error: {e}")
    return list(texts)

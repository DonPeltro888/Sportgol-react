"""
SEO Validator — sanity check + auto-truncate dei field generati dall'AI.
- Tronca meta_title (60), meta_description (160), og_title (70), og_description (200)
- Verifica presenza keyword primary nei field principali
- Calcola un seo_score 0-100
"""
import re
from typing import Dict, Any, List, Tuple

LIMITS = {
    "meta_title": 60,
    "meta_description": 160,
    "h1": 90,
    "open_graph_title": 70,
    "open_graph_description": 200,
    "twitter_card_title": 70,
    "twitter_card_description": 200,
    "cta_text": 80,
    "legal_disclosure_text": 280,
}


def smart_truncate(text: str, max_len: int) -> str:
    """Tronca al limite di parola, aggiunge … se necessario."""
    if not isinstance(text, str):
        return text
    if len(text) <= max_len:
        return text
    cut = text[: max_len - 1].rsplit(" ", 1)[0]
    return cut + "…"


def validate_and_fix(lang_block: Dict[str, Any]) -> Dict[str, Any]:
    """Tronca i field oversize e ritorna dict pulito."""
    fixed = dict(lang_block or {})
    for key, max_len in LIMITS.items():
        v = fixed.get(key)
        if isinstance(v, str) and len(v) > max_len:
            fixed[key] = smart_truncate(v, max_len)
    # Sanitize internal_links
    links = fixed.get("internal_links") or []
    if isinstance(links, list):
        clean: List[Dict[str, str]] = []
        for it in links[:8]:
            if isinstance(it, dict) and it.get("url") and it.get("anchor"):
                clean.append({"url": str(it["url"])[:200], "anchor": str(it["anchor"])[:80]})
        fixed["internal_links"] = clean
    # Sanitize image_alt_texts
    alts = fixed.get("image_alt_texts") or []
    if isinstance(alts, list):
        fixed["image_alt_texts"] = [str(a)[:120] for a in alts if a][:5]
    # Sanitize FAQ
    faqs = fixed.get("faq_items") or []
    if isinstance(faqs, list):
        clean_faq: List[Dict[str, str]] = []
        for it in faqs[:5]:
            if isinstance(it, dict):
                q = (it.get("q") or "")[:200]
                a = (it.get("a") or "")[:500]
                if q:
                    clean_faq.append({"q": q, "a": a})
        fixed["faq_items"] = clean_faq
    return fixed


def keyword_in(text: str, keyword: str) -> bool:
    if not text or not keyword:
        return False
    return keyword.strip().lower() in str(text).lower()


def compute_score(lang_block: Dict[str, Any], keyword: str) -> Tuple[int, List[str]]:
    """Calcola SEO score 0-100 e ritorna (score, list of warnings)."""
    score = 100
    warnings: List[str] = []

    mt = lang_block.get("meta_title") or ""
    md = lang_block.get("meta_description") or ""
    h1 = lang_block.get("h1") or ""
    intro = lang_block.get("intro_text") or ""
    main = lang_block.get("main_content") or ""

    # Length checks
    if not mt:
        score -= 20; warnings.append("Meta title mancante")
    elif len(mt) < 30:
        score -= 8; warnings.append(f"Meta title troppo corto ({len(mt)})")
    elif len(mt) > 60:
        score -= 6; warnings.append(f"Meta title oversize ({len(mt)})")

    if not md:
        score -= 15; warnings.append("Meta description mancante")
    elif len(md) < 120:
        score -= 6; warnings.append(f"Meta description corta ({len(md)})")
    elif len(md) > 160:
        score -= 5; warnings.append(f"Meta description oversize ({len(md)})")

    if not h1:
        score -= 15; warnings.append("H1 mancante")

    if len(intro) < 80:
        score -= 8; warnings.append(f"Intro troppo corto ({len(intro)} char)")

    word_count = len(re.findall(r"\w+", main))
    if word_count < 250:
        score -= 8; warnings.append(f"Main content corto ({word_count} parole)")

    # Keyword presence
    if keyword:
        if not keyword_in(mt, keyword):
            score -= 6; warnings.append(f"Keyword '{keyword}' assente da meta_title")
        if not keyword_in(h1, keyword):
            score -= 6; warnings.append(f"Keyword '{keyword}' assente da H1")
        if not keyword_in(intro, keyword):
            score -= 4; warnings.append(f"Keyword '{keyword}' assente da intro")

    # Internal links + alts
    if not lang_block.get("internal_links"):
        score -= 5; warnings.append("Nessun internal link")
    elif len(lang_block["internal_links"]) < 3:
        score -= 2; warnings.append(f"Pochi internal link ({len(lang_block['internal_links'])})")

    if not lang_block.get("image_alt_texts"):
        score -= 3; warnings.append("Nessun alt text immagine")

    if not lang_block.get("faq_items"):
        score -= 4; warnings.append("Nessuna FAQ")

    return max(0, min(100, score)), warnings

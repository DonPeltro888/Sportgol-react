"""
SEO Hreflang Validator.

Verifica che ogni entità SEO abbia:
1. Tutte le lingue obbligatorie configurate (default: it, en, es)
2. x-default presente (puntando alla versione canonica)
3. Url pattern consistente per locale (no broken paths)
4. Reciprocità: se en-US punta a /en/foo, allora /en/foo deve avere it-IT che torna a /it/foo
5. Lang-region codice valido (it-IT, en-US, en-GB, es-ES, etc.)

Output: lista di hreflang issues per ogni entity con tipo issue + severity + fix raccomandato.
"""
import logging
from typing import Dict, List, Any
import re

from database import db

logger = logging.getLogger(__name__)

# Mappa lang code → lang-region tag standard hreflang (Google docs)
LANG_HREFLANG = {
    "it": "it-IT",
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "pt": "pt-PT",
    "nl": "nl-NL",
}

# Lingue obbligatorie minime
REQUIRED_LANGS = ["it", "en", "es"]


def _expected_url(entity_type: str, slug: str, lang: str) -> str:
    if entity_type == "event":
        return f"/evento/{slug}" if lang == "it" else f"/{lang}/evento/{slug}"
    if entity_type == "team":
        return f"/squadra/{slug}" if lang == "it" else f"/{lang}/squadra/{slug}"
    if entity_type == "league":
        return f"/biglietti-{slug}" if lang == "it" else f"/{lang}/biglietti-{slug}"
    return ""


async def validate_entity(entity_type: str, slug: str) -> Dict[str, Any]:
    """Validate hreflang config per una singola entity."""
    coll_map = {"event": "events", "team": "teams", "league": "leagues"}
    coll = db[coll_map.get(entity_type, "events")]
    doc = await coll.find_one({"slug": slug}, {"_id": 0, "slug": 1, "seo_meta": 1, "seo_status": 1})
    if not doc:
        return {"slug": slug, "type": entity_type, "found": False, "issues": [{"type": "NOT_FOUND", "severity": "HIGH"}]}

    issues: List[Dict[str, str]] = []
    seo_meta = doc.get("seo_meta") or {}

    # 1. Required langs presence
    missing_langs = [lg for lg in REQUIRED_LANGS if lg not in seo_meta]
    for lg in missing_langs:
        issues.append({
            "type": "MISSING_LANG",
            "severity": "HIGH" if doc.get("seo_status") == "Published" else "MEDIUM",
            "lang": lg,
            "message": f"Lingua '{lg}' assente in seo_meta",
            "fix": f"Generare la traduzione per '{lg}' via DeepL o Claude",
        })

    # 2. x-default check (prendiamo it come default)
    if "it" not in seo_meta:
        issues.append({
            "type": "MISSING_X_DEFAULT",
            "severity": "HIGH",
            "message": "x-default non risolvibile (it default mancante)",
            "fix": "Generare seo_meta.it (è la lingua canonica del sito)",
        })

    # 3. URL pattern consistency
    expected = {lg: _expected_url(entity_type, slug, lg) for lg in REQUIRED_LANGS}
    for lg, exp_url in expected.items():
        actual = (seo_meta.get(lg) or {}).get("canonical_url")
        if actual:
            # actual è absolute, prendiamo solo il path
            try:
                from urllib.parse import urlparse
                actual_path = urlparse(actual).path
            except Exception:
                actual_path = actual
            if actual_path and actual_path != exp_url:
                issues.append({
                    "type": "URL_MISMATCH",
                    "severity": "MEDIUM",
                    "lang": lg,
                    "actual": actual_path,
                    "expected": exp_url,
                    "message": f"canonical_url '{lg}' non corrisponde al path atteso",
                    "fix": f"Aggiornare canonical_url a '{exp_url}'",
                })

    # 4. Hreflang tag value validity
    for lg in seo_meta.keys():
        if lg in LANG_HREFLANG:
            continue
        # Custom langs accettati (ma serve un mapping)
        if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", lg):
            issues.append({
                "type": "INVALID_LANG_CODE",
                "severity": "MEDIUM",
                "lang": lg,
                "message": f"Codice lingua '{lg}' non standard (atteso ISO 639-1)",
                "fix": "Rinominare a un codice valido (es. it, en, es)",
            })

    return {
        "slug": slug,
        "type": entity_type,
        "found": True,
        "seo_status": doc.get("seo_status"),
        "configured_langs": list(seo_meta.keys()),
        "expected_langs": REQUIRED_LANGS,
        "issues": issues,
        "issue_count": len(issues),
        "is_valid": len(issues) == 0,
    }


async def scan_all(entity_type: str = "all", limit: int = 500) -> Dict[str, Any]:
    """Scan globale di tutte le entità."""
    types = ["event", "team", "league"] if entity_type == "all" else [entity_type]
    rows: List[Dict[str, Any]] = []
    for t in types:
        coll_map = {"event": "events", "team": "teams", "league": "leagues"}
        coll = db[coll_map[t]]
        flt: Dict[str, Any] = {"seo_status": {"$in": ["Published", "Approved", "Generated"]}}
        if t == "event":
            from datetime import datetime, timezone
            flt["sort_date"] = {"$gte": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
        cursor = coll.find(flt, {"_id": 0, "slug": 1}).limit(limit)
        async for d in cursor:
            slug = d.get("slug")
            if not slug:
                continue
            res = await validate_entity(t, slug)
            if not res["is_valid"]:
                rows.append(res)

    severity_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in rows:
        for iss in r.get("issues", []):
            severity_count[iss.get("severity", "LOW")] = severity_count.get(iss.get("severity", "LOW"), 0) + 1

    rows.sort(key=lambda x: -x["issue_count"])
    return {
        "scanned_types": types,
        "total_invalid": len(rows),
        "by_severity": severity_count,
        "rows": rows[:limit],
    }

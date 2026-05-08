"""
SEO Cannibalization Detector.

Trova entità (event/league/team) che competono per la STESSA keyword primaria
(o titolo molto simile) → SEO cannibalization, dilution di authority.

Strategia:
- Estrae `seo_meta.it.title` (oppure `title` fallback) da tutti i documenti SEO-attivi
- Normalizza: lowercase, rimuove stop-words, mantiene 3-grammi
- Confronta a coppie con rapidfuzz (token_set_ratio threshold ≥ 85)
- Filtra: pagine in stessa lingua e stesso path-pattern (es. /squadra/* vs /evento/*)
- Severity: HIGH se entrambi sono Published, MEDIUM se uno solo, LOW se Draft

Output: lista di "issues" {entity_a, entity_b, similarity, severity, recommendation}
"""
import logging
import re
from typing import Dict, List, Any
from itertools import combinations

from rapidfuzz import fuzz
from database import db

logger = logging.getLogger(__name__)

STOPWORDS_IT = {
    "biglietti", "ticket", "tickets", "calendario", "partita", "match", "vs", "vs.",
    "il", "la", "lo", "i", "gli", "le", "di", "a", "da", "in", "su", "con", "per",
    "del", "della", "dei", "degli", "delle", "al", "alla", "ai", "agli", "alle",
}


def _normalize(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^\w\sàèéìòù]+", " ", s)
    tokens = [t for t in s.split() if t and t not in STOPWORDS_IT and len(t) > 1]
    return " ".join(tokens)


async def _gather_entities() -> List[Dict[str, Any]]:
    """Raccoglie events, leagues, teams con seo_meta.it.title o title fallback."""
    items: List[Dict[str, Any]] = []
    today_str = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).strftime("%Y-%m-%d")

    cursor = db.events.find(
        {"sort_date": {"$gte": today_str}},
        {"_id": 0, "slug": 1, "title": 1, "seo_meta": 1, "seo_status": 1, "league": 1},
    )
    async for d in cursor:
        title = ((d.get("seo_meta") or {}).get("it") or {}).get("title") or d.get("title")
        if title:
            items.append({
                "type": "event", "slug": d.get("slug"), "title": title,
                "norm": _normalize(title),
                "league": d.get("league"),
                "seo_status": d.get("seo_status") or "Draft",
            })

    cursor = db.leagues.find(
        {"active": True},
        {"_id": 0, "slug": 1, "name": 1, "seo_meta": 1, "seo_status": 1},
    )
    async for d in cursor:
        title = ((d.get("seo_meta") or {}).get("it") or {}).get("title") or d.get("name")
        if title:
            items.append({
                "type": "league", "slug": d.get("slug"), "title": title,
                "norm": _normalize(title), "seo_status": d.get("seo_status") or "Draft",
            })

    cursor = db.teams.find(
        {}, {"_id": 0, "slug": 1, "name": 1, "seo_meta": 1, "seo_status": 1, "league_slug": 1},
    )
    async for d in cursor:
        title = ((d.get("seo_meta") or {}).get("it") or {}).get("title") or d.get("name")
        if title:
            items.append({
                "type": "team", "slug": d.get("slug"), "title": title,
                "norm": _normalize(title), "league_slug": d.get("league_slug"),
                "seo_status": d.get("seo_status") or "Draft",
            })
    return items


def _severity(a: Dict, b: Dict) -> str:
    pub_a = a.get("seo_status") == "Published"
    pub_b = b.get("seo_status") == "Published"
    if pub_a and pub_b:
        return "HIGH"
    if pub_a or pub_b:
        return "MEDIUM"
    return "LOW"


async def scan_cannibalization(threshold: int = 85, limit: int = 200) -> Dict[str, Any]:
    """Esegue scan globale e ritorna le issue ordinate per severity+similarity."""
    items = await _gather_entities()
    issues: List[Dict[str, Any]] = []
    seen_pairs = set()

    # Solo coppie diverse (a.slug != b.slug). Limit le coppie per non esplodere O(N²).
    if len(items) > 1500:
        # Sample heuristic: prima 1500 ordinate per severità potenziale
        items = sorted(items, key=lambda x: 0 if x.get("seo_status") == "Published" else 1)[:1500]

    for a, b in combinations(items, 2):
        if a["type"] == b["type"] and a["slug"] == b["slug"]:
            continue
        key = tuple(sorted([f"{a['type']}:{a['slug']}", f"{b['type']}:{b['slug']}"]))
        if key in seen_pairs:
            continue
        # Skip pairs from completely unrelated leagues per ridurre rumore
        if a.get("league") and b.get("league") and a.get("league") != b.get("league") \
                and a["type"] == "event" and b["type"] == "event":
            continue
        sim = fuzz.token_set_ratio(a["norm"], b["norm"])
        if sim >= threshold:
            issues.append({
                "entity_a": {"type": a["type"], "slug": a["slug"], "title": a["title"], "status": a["seo_status"]},
                "entity_b": {"type": b["type"], "slug": b["slug"], "title": b["title"], "status": b["seo_status"]},
                "similarity": sim,
                "severity": _severity(a, b),
                "recommendation": _recommendation(a, b, sim),
            })
            seen_pairs.add(key)

    sev_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    issues.sort(key=lambda x: (sev_order.get(x["severity"], 9), -x["similarity"]))

    return {
        "total_entities_scanned": len(items),
        "issues_found": len(issues),
        "issues": issues[:limit],
        "by_severity": {
            "HIGH": sum(1 for i in issues if i["severity"] == "HIGH"),
            "MEDIUM": sum(1 for i in issues if i["severity"] == "MEDIUM"),
            "LOW": sum(1 for i in issues if i["severity"] == "LOW"),
        },
        "threshold": threshold,
    }


def _recommendation(a: Dict, b: Dict, sim: int) -> str:
    if a["type"] == b["type"]:
        if a["type"] == "event":
            return "Differenziare H1 e meta_title aggiungendo competition phase (es. 'Semifinale', 'Quarti')"
        if a["type"] == "team":
            return "Verificare se sono effettivamente entità diverse (Inter vs Inter Miami) e differenziare con city"
        if a["type"] == "league":
            return "Probabile duplicato lega — consolidare in una singola entità"
    return "Differenziare con anchor diversi: keyword team-specific vs league-specific"

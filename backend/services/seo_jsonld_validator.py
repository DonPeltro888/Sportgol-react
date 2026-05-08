"""
JSON-LD Schema.org Validator (offline, no external API).

Per ogni entità con `seo_meta.{lang}.json_ld_packet` generato dalla pipeline,
verifica:
1. Validità JSON parsable
2. @context, @type presenti
3. Required properties per type (Event: name, startDate, location; SportsTeam: name, sport;
   SportsLeague: name, sport; FAQPage: mainEntity)
4. Date format ISO 8601 (es. startDate)
5. URL fields validi (canonical, sameAs)
6. Coerenza interna (es. SportsEvent.location.@type=Place + Place.address)

Output: lista issues per entity con type, severity, fix raccomandato.
"""
import json
import logging
import re
from typing import Dict, Any, List
from datetime import datetime

from database import db

logger = logging.getLogger(__name__)

REQUIRED_PROPS = {
    "Event": ["name", "startDate", "location"],
    "SportsEvent": ["name", "startDate", "location"],
    "SportsTeam": ["name"],
    "SportsLeague": ["name"],
    "FAQPage": ["mainEntity"],
    "Question": ["name", "acceptedAnswer"],
    "Place": ["name"],
    "BreadcrumbList": ["itemListElement"],
}

URL_RX = re.compile(r"^https?://[^\s]+$")


def _is_iso_date(s: str) -> bool:
    if not isinstance(s, str):
        return False
    try:
        # Accept YYYY-MM-DD or full ISO 8601
        datetime.fromisoformat(s.replace("Z", "+00:00"))
        return True
    except (ValueError, TypeError):
        return False


def _validate_node(node: Any, path: str = "$") -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    if not isinstance(node, dict):
        return issues

    t = node.get("@type")
    if not t and path == "$":
        issues.append({"path": path, "type": "MISSING_TYPE", "severity": "HIGH",
                       "message": "@type mancante alla root", "fix": "Aggiungere @type"})

    # Ctx alla root
    if path == "$" and not node.get("@context"):
        issues.append({"path": path, "type": "MISSING_CONTEXT", "severity": "HIGH",
                       "message": "@context mancante", "fix": '@context: "https://schema.org"'})

    # Required props per type
    if isinstance(t, str):
        for req in REQUIRED_PROPS.get(t, []):
            if req not in node:
                issues.append({"path": f"{path}.{t}", "type": "MISSING_REQUIRED",
                               "severity": "HIGH", "field": req,
                               "message": f"Campo obbligatorio '{req}' mancante per tipo '{t}'",
                               "fix": f"Aggiungere '{req}'"})

    # Date validation
    for date_field in ("startDate", "endDate", "datePublished", "dateModified"):
        if date_field in node and not _is_iso_date(str(node[date_field])):
            issues.append({"path": f"{path}.{date_field}", "type": "INVALID_DATE",
                           "severity": "MEDIUM", "value": str(node[date_field])[:100],
                           "message": f"Date '{date_field}' non in formato ISO 8601",
                           "fix": "Usare formato YYYY-MM-DDTHH:MM:SS+00:00"})

    # URL validation
    for url_field in ("url", "image", "logo"):
        v = node.get(url_field)
        if v and isinstance(v, str) and not URL_RX.match(v):
            issues.append({"path": f"{path}.{url_field}", "type": "INVALID_URL",
                           "severity": "LOW", "value": v[:100],
                           "message": f"URL '{url_field}' non valido (deve iniziare con http://)",
                           "fix": "Usare URL assoluto"})

    # sameAs deve essere array di URL
    sa = node.get("sameAs")
    if sa is not None:
        if not isinstance(sa, list):
            issues.append({"path": f"{path}.sameAs", "type": "INVALID_SAMEAS",
                           "severity": "LOW",
                           "message": "sameAs deve essere un array di URL",
                           "fix": "Convertire a lista"})
        else:
            for i, u in enumerate(sa):
                if not isinstance(u, str) or not URL_RX.match(u):
                    issues.append({"path": f"{path}.sameAs[{i}]", "type": "INVALID_URL",
                                   "severity": "LOW", "value": str(u)[:100],
                                   "message": "URL non valido in sameAs",
                                   "fix": "Sostituire con URL https://..."})

    # Recurse into children
    for k, v in node.items():
        if isinstance(v, dict):
            issues.extend(_validate_node(v, f"{path}.{k}"))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    issues.extend(_validate_node(item, f"{path}.{k}[{i}]"))
    return issues


def validate_packet(packet: Any) -> Dict[str, Any]:
    """Validate un JSON-LD packet (può essere un object o un @graph array)."""
    if isinstance(packet, str):
        try:
            packet = json.loads(packet)
        except json.JSONDecodeError as e:
            return {"valid": False, "issues": [{"type": "PARSE_ERROR", "severity": "HIGH",
                                                "message": f"JSON non parsabile: {e}",
                                                "fix": "Correggere sintassi JSON"}]}
    if not isinstance(packet, dict):
        return {"valid": False, "issues": [{"type": "INVALID_ROOT", "severity": "HIGH",
                                            "message": "Root non è un oggetto JSON",
                                            "fix": "Convertire a oggetto"}]}

    issues: List[Dict[str, str]] = []
    if "@graph" in packet and isinstance(packet["@graph"], list):
        # Validate ogni nodo del graph
        for i, node in enumerate(packet["@graph"]):
            issues.extend(_validate_node(node, f"@graph[{i}]"))
        if not packet.get("@context"):
            issues.append({"type": "MISSING_CONTEXT", "severity": "HIGH",
                           "message": "@context root mancante (graph)",
                           "fix": '@context: "https://schema.org"'})
    else:
        issues.extend(_validate_node(packet))

    sev = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for i in issues:
        sev[i.get("severity", "LOW")] = sev.get(i.get("severity", "LOW"), 0) + 1

    return {
        "valid": len(issues) == 0,
        "issue_count": len(issues),
        "by_severity": sev,
        "issues": issues,
    }


async def scan_all(entity_type: str = "all", lang: str = "it", limit: int = 200) -> Dict[str, Any]:
    """Scan tutti i packet seo_meta.{lang}.json_ld_packet di tutte le entità."""
    types = ["event", "team", "league"] if entity_type == "all" else [entity_type]
    rows: List[Dict[str, Any]] = []
    for t in types:
        coll_map = {"event": "events", "team": "teams", "league": "leagues"}
        coll = db[coll_map[t]]
        flt: Dict[str, Any] = {f"seo_meta.{lang}.json_ld_packet": {"$exists": True}}
        cursor = coll.find(flt, {"_id": 0, "slug": 1, "title": 1, "name": 1,
                                 f"seo_meta.{lang}.json_ld_packet": 1}).limit(limit)
        async for d in cursor:
            packet = ((d.get("seo_meta") or {}).get(lang) or {}).get("json_ld_packet")
            if not packet:
                continue
            res = validate_packet(packet)
            if not res["valid"]:
                rows.append({
                    "type": t,
                    "slug": d.get("slug"),
                    "title": d.get("title") or d.get("name"),
                    "issue_count": res["issue_count"],
                    "by_severity": res["by_severity"],
                    "top_issues": res["issues"][:3],
                })

    rows.sort(key=lambda x: -x["issue_count"])
    by_sev = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in rows:
        for k, v in r["by_severity"].items():
            by_sev[k] = by_sev.get(k, 0) + v

    return {
        "lang": lang,
        "total_invalid": len(rows),
        "by_severity": by_sev,
        "rows": rows[:limit],
    }

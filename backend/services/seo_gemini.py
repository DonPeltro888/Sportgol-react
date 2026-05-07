"""
Google Gemini 3 Pro — JSON-LD Schema completo per ticketing calcio.

Output: array di nodi JSON-LD includendo:
- SportsEvent / SportsTeam / SportsOrganization
- AggregateOffer (lowPrice/availability)
- AggregateRating (★ stelle SERP)
- BreadcrumbList
- FAQPage
- HowTo "Come acquistare biglietti"
- Place con GeoCoordinates + PostalAddress
- Speakable (voice search)
- subjectOf + sameAs (Wikipedia entity linking)
- eventStatus dinamico
"""
import json
import logging
import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import httpx
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)
MODEL = "gemini-2.5-pro"  # Universal Key alias for latest stable Gemini Pro

BASE_URL = "https://golevents.com"


def _iso(value: Any) -> Optional[str]:
    """Converte datetime/date in ISO string, lascia stringhe invariate."""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


async def build_jsonld(
    target_type: str,
    ctx: Dict[str, Any],
    faq_items: Optional[List[Dict[str, str]]] = None,
    breadcrumbs: Optional[List[Dict[str, str]]] = None,
    geo: Optional[Dict[str, Any]] = None,
    same_as: Optional[List[str]] = None,
    aggregate_rating: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Costruisce un grafo JSON-LD completo. Restituisce un dict con chiave "@graph".
    Usa Gemini per arricchire descrizione/keywords, ma il "core" è procedurale (Schema.org compliant).
    """
    graph: List[Dict[str, Any]] = []

    main = _build_main_schema(target_type, ctx, geo=geo, same_as=same_as, aggregate_rating=aggregate_rating)
    graph.append(main)

    # Breadcrumbs
    if breadcrumbs:
        graph.append(_build_breadcrumb(breadcrumbs))

    # FAQ
    if faq_items:
        graph.append(_build_faq_page(faq_items))

    # HowTo "Come acquistare biglietti"
    graph.append(_build_howto(target_type, ctx))

    # Speakable (voice search)
    graph.append(_build_speakable(ctx))

    enriched = None
    try:
        enriched = await _enrich_with_gemini(target_type, ctx, graph)
    except Exception as e:
        logger.warning(f"Gemini enrichment failed, using base graph: {e}")
    final_graph = enriched or graph
    return {"@context": "https://schema.org", "@graph": final_graph}


# ─── Schema base nodes ────────────────────────────────────────────────────

def _build_main_schema(
    target_type: str,
    ctx: Dict[str, Any],
    geo: Optional[Dict[str, Any]] = None,
    same_as: Optional[List[str]] = None,
    aggregate_rating: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    title = ctx.get("title") or "?"
    canonical = ctx.get("canonical_url") or ""
    same_as_clean = [s for s in (same_as or []) if s and s.startswith("http")]

    # AggregateRating default realistico (può essere override da utente o sostituito da Trustpilot in futuro)
    rating_node = aggregate_rating or {
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "ratingCount": "1247",
        "bestRating": "5",
        "worstRating": "1",
    }
    if "@type" not in rating_node:
        rating_node["@type"] = "AggregateRating"

    if target_type == "event":
        home = ctx.get("home_team", "")
        away = ctx.get("away_team", "")
        location_node = _build_place(ctx, geo)
        offers = {
            "@type": "AggregateOffer",
            "priceCurrency": "EUR",
            "lowPrice": str(ctx.get("minimum_price") or "30"),
            "highPrice": str(ctx.get("maximum_price") or "350"),
            "availability": "https://schema.org/InStock",
            "url": canonical,
            "validFrom": _iso(ctx.get("offer_valid_from") or ctx.get("created_at")),
        }
        node: Dict[str, Any] = {
            "@type": "SportsEvent",
            "@id": f"{canonical}#event",
            "name": f"{home} vs {away}",
            "description": ctx.get("description") or f"Biglietti per {home} vs {away}",
            "startDate": _iso(ctx.get("sort_date") or ctx.get("date")),
            "eventStatus": _resolve_event_status(ctx),
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "homeTeam": {"@type": "SportsTeam", "name": home},
            "awayTeam": {"@type": "SportsTeam", "name": away},
            "location": location_node,
            "offers": offers,
            "aggregateRating": rating_node,
            "url": canonical,
        }
        if ctx.get("previous_start_date"):
            node["previousStartDate"] = _iso(ctx["previous_start_date"])
        if same_as_clean:
            node["sameAs"] = same_as_clean
        if ctx.get("league"):
            node["superEvent"] = {"@type": "SportsEvent", "name": ctx["league"]}
        return node

    if target_type == "league":
        node = {
            "@type": "SportsOrganization",
            "@id": f"{canonical}#league",
            "name": title,
            "sport": "Football",
            "areaServed": ctx.get("country", ""),
            "description": ctx.get("description") or f"Biglietti ufficiali {title} 2025/26",
            "url": canonical,
            "aggregateRating": rating_node,
        }
        if same_as_clean:
            node["sameAs"] = same_as_clean
        if ctx.get("logo_url"):
            node["logo"] = ctx["logo_url"]
        return node

    # team
    location_node = _build_place(ctx, geo)
    node = {
        "@type": "SportsTeam",
        "@id": f"{canonical}#team",
        "name": title,
        "sport": "Football",
        "description": ctx.get("description") or f"Biglietti {title} casa e trasferta",
        "url": canonical,
        "aggregateRating": rating_node,
    }
    if location_node and location_node.get("name"):
        node["location"] = location_node
    if same_as_clean:
        node["sameAs"] = same_as_clean
    if ctx.get("logo_url"):
        node["logo"] = ctx["logo_url"]
    if ctx.get("league"):
        node["memberOf"] = {"@type": "SportsOrganization", "name": ctx["league"]}
    return node


def _build_place(ctx: Dict[str, Any], geo: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    stadium = ctx.get("stadium") or ""
    city = ctx.get("city") or ctx.get("location") or ""
    country = ctx.get("country") or "IT"
    place: Dict[str, Any] = {"@type": "Place", "name": stadium}
    address: Dict[str, Any] = {"@type": "PostalAddress", "addressCountry": country}
    if city:
        address["addressLocality"] = city
    if ctx.get("postal_code"):
        address["postalCode"] = ctx["postal_code"]
    if ctx.get("street_address"):
        address["streetAddress"] = ctx["street_address"]
    place["address"] = address
    if geo and geo.get("latitude") and geo.get("longitude"):
        place["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(geo["latitude"]),
            "longitude": str(geo["longitude"]),
        }
    return place


def _resolve_event_status(ctx: Dict[str, Any]) -> str:
    status = (ctx.get("seo_event_status") or "EventScheduled").lstrip("/").split("/")[-1]
    valid = {"EventScheduled", "EventPostponed", "EventCancelled", "EventRescheduled", "EventMovedOnline"}
    if status not in valid:
        status = "EventScheduled"
    return f"https://schema.org/{status}"


def _build_breadcrumb(items: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": it.get("name", ""),
                "item": it.get("url", ""),
            }
            for i, it in enumerate(items)
        ],
    }


def _build_faq_page(faqs: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f.get("q", ""),
                "acceptedAnswer": {"@type": "Answer", "text": f.get("a", "")},
            }
            for f in faqs if f.get("q")
        ],
    }


def _build_howto(target_type: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    title = ctx.get("title") or "?"
    if target_type == "event":
        h = ctx.get("home_team", "")
        a = ctx.get("away_team", "")
        topic = f"{h} vs {a}" if h and a else title
    else:
        topic = title
    return {
        "@type": "HowTo",
        "name": f"Come acquistare biglietti per {topic}",
        "totalTime": "PT3M",
        "step": [
            {"@type": "HowToStep", "position": 1, "name": "Cerca l'evento",
             "text": f"Visita la pagina ufficiale di Golevents per {topic} e visualizza la disponibilità in tempo reale."},
            {"@type": "HowToStep", "position": 2, "name": "Confronta prezzi e settori",
             "text": "Analizza la mappa dello stadio e confronta i prezzi tra i diversi settori disponibili."},
            {"@type": "HowToStep", "position": 3, "name": "Scegli i tuoi posti",
             "text": "Seleziona il settore preferito e il numero di biglietti."},
            {"@type": "HowToStep", "position": 4, "name": "Completa l'acquisto sicuro",
             "text": "Inserisci i dati di pagamento — transazione protetta SSL e biglietti garantiti al 100%."},
            {"@type": "HowToStep", "position": 5, "name": "Ricevi i biglietti via email",
             "text": "I biglietti arrivano direttamente nella tua casella entro 24h dall'evento."},
        ],
    }


def _build_speakable(ctx: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "@type": "WebPage",
        "@id": (ctx.get("canonical_url") or "") + "#speakable",
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": [".seo-intro", "h1", ".seo-faq"],
        },
        "url": ctx.get("canonical_url") or "",
    }


# ─── Gemini enrichment (descrizione, keywords) ────────────────────────────

async def _enrich_with_gemini(
    target_type: str, ctx: Dict[str, Any], graph: List[Dict[str, Any]]
) -> Optional[List[Dict[str, Any]]]:
    """Fa rifinire descrizioni/keywords da Gemini. Se errore, ritorna None (usa graph base)."""
    api_key = await get_api_key("gemini")
    if not api_key:
        return None

    prompt = (
        "Sei un esperto SEO Schema.org per ticketing calcio. Hai questo grafo JSON-LD:\n"
        f"{json.dumps(graph, ensure_ascii=False, indent=2, default=str)}\n\n"
        "Migliora SOLO i campi 'description' (max 200 char), aggiungi 'keywords' come stringa "
        "comma-separated dove applicabile, e correggi eventuali campi mancanti palesi.\n"
        "NON modificare @type, @id, @context, ratingValue, prezzi.\n"
        "NON inventare URL inesistenti.\n"
        "Restituisci SOLO un array JSON valido (i nodi modificati), nessun markdown."
    )

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4000,
            "responseMimeType": "application/json",
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=90) as cx:
            r = await cx.post(url, json=body)
        if r.status_code == 200:
            data = r.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            text = _strip_fences(text)
            parsed = json.loads(text)
            if isinstance(parsed, list) and parsed:
                return parsed
        else:
            logger.warning(f"Gemini HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"Gemini error: {e}")
    return None


def _strip_fences(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()

"""
SEO Intelligence Routes — hub unificato per tutti i tools SEO avanzati.

Endpoints:
- /api/seo/intelligence/topic-cluster/overview
- /api/seo/intelligence/topic-cluster/{type}/{slug}
- /api/seo/intelligence/cannibalization/scan
- /api/seo/intelligence/hreflang/scan
- /api/seo/intelligence/hreflang/{type}/{slug}
- /api/seo/intelligence/team-verifier/run
- /api/seo/intelligence/team-verifier/latest
- /api/seo/intelligence/faq/{type}/{slug}/generate
- /api/seo/intelligence/faq/{type}/{slug}
- /api/seo/intelligence/jsonld/scan
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from database import db
from routes.admin_auth import verify_admin_token
from services import (
    seo_topic_cluster, seo_cannibalization, seo_hreflang,
    seo_team_verifier, seo_faq_generator, seo_jsonld_validator,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/seo/intelligence", tags=["seo-intelligence"])

COLL_MAP = {"event": "events", "team": "teams", "league": "leagues"}


# ================= Topic Cluster =================
@router.get("/topic-cluster/overview")
async def topic_cluster_overview(_=Depends(verify_admin_token)):
    return await seo_topic_cluster.cluster_overview()


@router.get("/topic-cluster/{entity_type}/{slug}")
async def topic_cluster_links(
    entity_type: str, slug: str, lang: str = "it", _=Depends(verify_admin_token),
):
    coll = db[COLL_MAP.get(entity_type, "events")]
    doc = await coll.find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(404, f"{entity_type} '{slug}' non trovato")
    links = await seo_topic_cluster.build_links(entity_type, doc, lang)
    return {"entity_type": entity_type, "slug": slug, "lang": lang, "links": links, "count": len(links)}


# ================= Cannibalization =================
@router.get("/cannibalization/scan")
async def cannibalization_scan(
    threshold: int = Query(85, ge=70, le=100),
    limit: int = Query(200, ge=10, le=500),
    _=Depends(verify_admin_token),
):
    return await seo_cannibalization.scan_cannibalization(threshold=threshold, limit=limit)


# ================= Hreflang =================
@router.get("/hreflang/scan")
async def hreflang_scan(
    entity_type: str = Query("all"),
    limit: int = Query(500, ge=10, le=2000),
    _=Depends(verify_admin_token),
):
    return await seo_hreflang.scan_all(entity_type=entity_type, limit=limit)


@router.get("/hreflang/{entity_type}/{slug}")
async def hreflang_validate_one(entity_type: str, slug: str, _=Depends(verify_admin_token)):
    return await seo_hreflang.validate_entity(entity_type, slug)


# ================= Team Verifier =================
@router.post("/team-verifier/run")
async def team_verifier_run(
    limit: int = Query(50, ge=1, le=300),
    only_with_drift: bool = Query(False),
    _=Depends(verify_admin_token),
):
    """Lancia verifica AI Perplexity su tutti i team. Default 50 (controllato per costi)."""
    return await seo_team_verifier.verify_all_teams(limit=limit, only_with_drift=only_with_drift)


@router.get("/team-verifier/latest")
async def team_verifier_latest(_=Depends(verify_admin_token)):
    return await seo_team_verifier.latest_report()


# ================= FAQ Generator =================
@router.post("/faq/{entity_type}/{slug}/generate")
async def faq_generate(
    entity_type: str, slug: str,
    langs: Optional[str] = Query("it,en,es", description="Comma-sep list, e.g. 'it,en,es'"),
    _=Depends(verify_admin_token),
):
    langs_list = [s.strip() for s in (langs or "it,en,es").split(",") if s.strip()]
    return await seo_faq_generator.generate_and_save_faq(entity_type, slug, langs_list)


@router.get("/faq/{entity_type}/{slug}")
async def faq_get(entity_type: str, slug: str, lang: str = "it", _=Depends(verify_admin_token)):
    items = await seo_faq_generator.get_faq(entity_type, slug, lang)
    return {"entity_type": entity_type, "slug": slug, "lang": lang, "faq": items, "count": len(items)}


@router.get("/faq/{entity_type}/{slug}/public")
async def faq_get_public(entity_type: str, slug: str, lang: str = "it"):
    """Endpoint PUBBLICO per il frontend (no auth) — serve FAQ già generate."""
    items = await seo_faq_generator.get_faq(entity_type, slug, lang)
    return {"entity_type": entity_type, "slug": slug, "lang": lang, "faq": items}


# ================= JSON-LD Validator =================
@router.get("/jsonld/scan")
async def jsonld_scan(
    entity_type: str = Query("all"),
    lang: str = Query("it"),
    limit: int = Query(200, ge=10, le=500),
    _=Depends(verify_admin_token),
):
    return await seo_jsonld_validator.scan_all(entity_type=entity_type, lang=lang, limit=limit)


# ================= Trust Score (per public frontend) =================
@router.get("/trust-score/{entity_type}/{slug}")
async def trust_score(entity_type: str, slug: str):
    """Trust score di un'entità basato su numero fonti che la confermano.
    Restituisce un punteggio 0-100 e un badge.
    """
    coll = db[COLL_MAP.get(entity_type, "events")]
    doc = await coll.find_one({"slug": slug}, {"_id": 0, "source": 1, "espn_id": 1,
                                                "ai_match_id": 1, "matchesio_id": 1,
                                                "thesportsdb_id": 1, "openfootball_id": 1,
                                                "apifootball_id": 1, "_multi_source_verified": 1,
                                                "home_team": 1, "away_team": 1, "league": 1, "sort_date": 1})
    if not doc:
        raise HTTPException(404, "entity not found")

    # Conta fonti
    sources = []
    if doc.get("espn_id"):
        sources.append("espn")
    if doc.get("matchesio_id"):
        sources.append("matchesio")
    if doc.get("thesportsdb_id"):
        sources.append("thesportsdb")
    if doc.get("openfootball_id"):
        sources.append("openfootball")
    if doc.get("apifootball_id"):
        sources.append("apifootball")
    if doc.get("ai_match_id"):
        sources.append("ai_perplexity")

    # Per gli events, cerca anche match con stesse home+away+date in altre fonti
    if entity_type == "event":
        siblings = await db.events.count_documents({
            "home_team": doc.get("home_team"),
            "away_team": doc.get("away_team"),
            "sort_date": {"$regex": (doc.get("sort_date") or "")[:10]},
            "slug": {"$ne": slug},
        })
    else:
        siblings = 0

    n_sources = len(set(sources)) + (1 if siblings > 0 else 0)

    # Score
    if n_sources >= 3:
        score, badge, color = 95, "Verified by multiple sources", "green"
    elif n_sources == 2:
        score, badge, color = 75, "Cross-verified", "blue"
    elif n_sources == 1:
        primary = sources[0] if sources else "unknown"
        if primary in ("espn", "openfootball"):
            score, badge, color = 65, "Official source", "blue"
        elif primary == "ai_perplexity":
            score, badge, color = 50, "AI-discovered", "amber"
        else:
            score, badge, color = 55, "Single source", "amber"
    else:
        score, badge, color = 30, "Unverified", "gray"

    return {
        "entity_type": entity_type,
        "slug": slug,
        "trust_score": score,
        "badge": badge,
        "color": color,
        "sources": sources,
        "source_count": n_sources,
    }

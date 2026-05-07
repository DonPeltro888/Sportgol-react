"""
SEO Target manager – collega il SEO Admin alle entity esistenti
(events, leagues, teams). NON crea pagine nuove: scrive `seo_meta`,
`seo_draft` e `seo_locks` sulle collezioni esistenti.

Schema applicato a ogni entity (campo opzionale):
- seo_status: "Draft" | "Generated" | "Needs Review" | "Approved" | "Published"
- seo_score: 0-100
- seo_locks: {"<field_path>": true, ...}
- seo_meta: { it: {...}, en: {...}, es: {...} }   # PUBBLICATO
- seo_draft: { it: {...}, en: {...}, es: {...} }  # PIPELINE OUTPUT (da approvare)
- seo_generated_at, seo_audited_at, seo_published_at
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from bson import ObjectId

from database import db
from routes.admin_auth import verify_admin_token

router = APIRouter(prefix="/api/seo", tags=["seo-targets"])

# ─── Mapping type → collection ──────────────────────────────────────────────
COLLECTION_MAP = {
    "event": "events",
    "league": "leagues",
    "team": "teams",
}

# Campi multi-lingua gestiti dalla pipeline (per lingua)
SEO_FIELDS_PER_LANG: List[str] = [
    "meta_title",
    "meta_description",
    "h1",
    "intro_text",
    "main_content",
    "faq_items",          # list[{q,a}]
    "cta_text",
    "open_graph_title",
    "open_graph_description",
    "twitter_card_title",
    "twitter_card_description",
    "image_alt_texts",    # list[str]
    "internal_links",     # list[{url,anchor}]
    "schema_jsonld",      # dict (Event/SportsEvent/etc)
    "hero_image_url",     # for league/team pages (Nano Banana)
]

LANGS = ["it", "en", "es"]


# Mappatura draft → campi SEO reali esistenti nelle entity (per il PUBLISH).
# - events: usa già seo_title.{lang}, seo_description.{lang}, seo_h1.{lang}, seo_intro.{lang}, seo_cta.{lang}, faq_N_q/a.{lang}
# - leagues/teams: scrivono nei campi standard seo_title/seo_description/seo_h1/seo_intro/seo_cta multilingua
DRAFT_FIELD_MAP_EVENT = {
    "meta_title": "seo_title",
    "meta_description": "seo_description",
    "h1": "seo_h1",
    "intro_text": "seo_intro",
    "main_content": "seo_main_content",
    "cta_text": "seo_cta",
    "open_graph_title": "seo_og_title",
    "open_graph_description": "seo_og_description",
    "twitter_card_title": "seo_twitter_title",
    "twitter_card_description": "seo_twitter_description",
    "internal_links": "seo_internal_links",
    "image_alt_texts": "seo_image_alt_texts",
    "legal_disclosure_text": "seo_legal_disclosure",
}
DRAFT_FIELD_MAP_GENERIC = {
    "meta_title": "seo_title",
    "meta_description": "seo_description",
    "h1": "seo_h1",
    "intro_text": "seo_intro",
    "main_content": "seo_main_content",
    "cta_text": "seo_cta",
    "open_graph_title": "seo_og_title",
    "open_graph_description": "seo_og_description",
    "twitter_card_title": "seo_twitter_title",
    "twitter_card_description": "seo_twitter_description",
    "internal_links": "seo_internal_links",
    "image_alt_texts": "seo_image_alt_texts",
    "legal_disclosure_text": "seo_legal_disclosure",
}


def _publish_mapping(type_: str) -> Dict[str, str]:
    return DRAFT_FIELD_MAP_EVENT if type_ == "event" else DRAFT_FIELD_MAP_GENERIC


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_id(type_: str, id_: str) -> Any:
    """events e leagues/teams usano tutti string id (slug-friendly oppure ObjectId)."""
    if type_ == "event":
        # Event può essere ObjectId 24-char OR slug
        if len(id_) == 24:
            try:
                return ObjectId(id_)
            except Exception:
                return id_
        return id_
    return id_  # leagues/teams: lookup by slug or _id


def _identifier_field(type_: str, id_: str) -> Dict[str, Any]:
    """Costruisce il filter MongoDB corretto."""
    if type_ == "event":
        if len(id_) == 24:
            try:
                return {"_id": ObjectId(id_)}
            except Exception:
                pass
        return {"slug": id_}
    # leagues/teams
    return {"slug": id_}


# ─── Models ────────────────────────────────────────────────────────────────

class SeoTargetSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    type: str  # event|league|team
    title: str
    slug: Optional[str] = None
    league: Optional[str] = None
    country: Optional[str] = None
    sort_date: Optional[str] = None
    seo_status: str = "Draft"
    seo_score: Optional[int] = None
    seo_generated_at: Optional[str] = None
    has_draft: bool = False
    locked_fields_count: int = 0


class LockUpdate(BaseModel):
    field_path: str   # es. "it.meta_title"
    locked: bool


class DraftFieldUpdate(BaseModel):
    field_path: str   # "it.meta_title", "es.faq_items", "schema_jsonld" (no lang)
    value: Any
    is_locked: Optional[bool] = None


# ─── List ──────────────────────────────────────────────────────────────────

@router.get("/targets")
async def list_targets(
    type: str = Query("event"),
    q: Optional[str] = None,
    status: Optional[str] = None,
    league_slug: Optional[str] = None,
    team_slug: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Lista entity esistenti (events/leagues/teams) con stato SEO.
    Filtri opzionali:
    - league_slug: per type=team filtra per `league_slug`; per type=event filtra per nome lega.
    - team_slug: per type=event filtra per home_team/away_team del team (con scope di lega per anti-collision Inter vs Inter Miami).
    """
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "type must be event|league|team")

    coll = db[coll_name]
    flt: Dict[str, Any] = {}
    extra_and: List[Dict[str, Any]] = []
    if q:
        flt["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"slug": {"$regex": q, "$options": "i"}},
            {"name": {"$regex": q, "$options": "i"}},
            {"home_team": {"$regex": q, "$options": "i"}},
            {"away_team": {"$regex": q, "$options": "i"}},
        ]
    if status:
        flt["seo_status"] = status

    # League filter
    if league_slug:
        if type == "team":
            flt["league_slug"] = league_slug
        elif type == "event":
            league_doc = await db.leagues.find_one({"slug": league_slug}, {"_id": 0, "name": 1})
            if league_doc:
                import re as _re
                league_re = f"^{_re.escape(league_doc.get('name', ''))}$"
                extra_and.append({"$or": [
                    {"league": {"$regex": league_re, "$options": "i"}},
                    {"league_slug": league_slug},
                ]})
            else:
                # league not found → return empty
                extra_and.append({"_id": {"$exists": False}})
        elif type == "league":
            flt["slug"] = league_slug

    # Team filter (only events)
    if team_slug and type == "event":
        team_doc = await db.teams.find_one({"slug": team_slug}, {"_id": 0, "name": 1, "league_slug": 1})
        if team_doc:
            import re as _re
            team_re = f"^{_re.escape(team_doc.get('name', ''))}$"
            team_clause: Dict[str, Any] = {"$or": [
                {"home_team": {"$regex": team_re, "$options": "i"}},
                {"away_team": {"$regex": team_re, "$options": "i"}},
            ]}
            # scope league name to avoid Inter vs Inter Miami leakage
            t_league_slug = team_doc.get("league_slug")
            if t_league_slug:
                t_league_doc = await db.leagues.find_one({"slug": t_league_slug}, {"_id": 0, "name": 1})
                if t_league_doc:
                    league_re = f"^{_re.escape(t_league_doc.get('name', ''))}$"
                    team_clause = {"$and": [team_clause, {"league": {"$regex": league_re, "$options": "i"}}]}
            extra_and.append(team_clause)
        else:
            extra_and.append({"_id": {"$exists": False}})

    if extra_and:
        flt = {"$and": [flt, *extra_and]} if flt else {"$and": extra_and}

    total = await coll.count_documents(flt)
    sort = [("sort_date", -1)] if type == "event" else [("name", 1)]

    cursor = coll.find(flt, {
        "_id": 1, "title": 1, "name": 1, "slug": 1, "home_team": 1, "away_team": 1,
        "league": 1, "country": 1, "sort_date": 1, "date": 1,
        "seo_status": 1, "seo_score": 1, "seo_generated_at": 1,
        "seo_draft": 1, "seo_locks": 1,
    }).sort(sort).skip(offset).limit(limit)

    items: List[SeoTargetSummary] = []
    async for doc in cursor:
        title = doc.get("title") or doc.get("name") or doc.get("slug") or "?"
        if type == "event" and doc.get("home_team") and doc.get("away_team"):
            title = f"{doc['home_team']} vs {doc['away_team']}"
        items.append(SeoTargetSummary(
            id=doc.get("slug") or str(doc.get("_id")),
            type=type,
            title=title,
            slug=doc.get("slug"),
            league=doc.get("league"),
            country=doc.get("country"),
            sort_date=doc.get("sort_date") or doc.get("date"),
            seo_status=doc.get("seo_status") or "Draft",
            seo_score=doc.get("seo_score"),
            seo_generated_at=doc.get("seo_generated_at"),
            has_draft=bool(doc.get("seo_draft")),
            locked_fields_count=len([k for k, v in (doc.get("seo_locks") or {}).items() if v]),
        ))

    return {"total": total, "items": [i.model_dump() for i in items]}


# ─── Get single ────────────────────────────────────────────────────────────

def _existing_to_meta(type_: str, doc: Dict[str, Any]) -> Dict[str, Any]:
    """Costruisce seo_meta dai campi diretti esistenti (events/leagues/teams)."""
    field_map = _publish_mapping(type_)
    meta: Dict[str, Any] = {l: {} for l in LANGS}
    for our_key, existing_key in field_map.items():
        existing = doc.get(existing_key)
        if isinstance(existing, dict):
            for lang in LANGS:
                v = existing.get(lang)
                if v:
                    meta[lang][our_key] = v
        elif isinstance(existing, str) and existing:
            # campo non-multilingua → fallback su 'it'
            meta["it"][our_key] = existing
    # FAQ
    if type_ == "event":
        for lang in LANGS:
            faqs = []
            for i in range(1, 4):
                q = (doc.get(f"faq_{i}_q") or {}).get(lang) if isinstance(doc.get(f"faq_{i}_q"), dict) else None
                a = (doc.get(f"faq_{i}_a") or {}).get(lang) if isinstance(doc.get(f"faq_{i}_a"), dict) else None
                if q or a:
                    faqs.append({"q": q or "", "a": a or ""})
            if faqs:
                meta[lang]["faq_items"] = faqs
    return meta


@router.get("/targets/{type}/{id}")
async def get_target(type: str, id: str, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "Invalid type")
    doc = await db[coll_name].find_one(_identifier_field(type, id), {"_id": 0})
    if not doc:
        raise HTTPException(404, f"{type} not found")

    # Build seo_meta unifying existing direct fields + stored meta
    existing_meta = _existing_to_meta(type, doc)
    stored_meta = doc.get("seo_meta") or {}
    merged_meta: Dict[str, Any] = {l: {} for l in LANGS}
    for lang in LANGS:
        merged_meta[lang] = {**existing_meta.get(lang, {}), **(stored_meta.get(lang) or {})}

    doc["seo_meta"] = merged_meta
    doc.setdefault("seo_status", "Draft")
    doc.setdefault("seo_draft", {})
    doc.setdefault("seo_locks", {})
    return {"type": type, "data": doc}


# ─── Lock / Unlock field ───────────────────────────────────────────────────

@router.put("/targets/{type}/{id}/lock")
async def update_lock(type: str, id: str, payload: LockUpdate, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "Invalid type")
    field = f"seo_locks.{payload.field_path}"
    if payload.locked:
        await db[coll_name].update_one(_identifier_field(type, id), {"$set": {field: True}})
    else:
        await db[coll_name].update_one(_identifier_field(type, id), {"$unset": {field: ""}})
    return {"ok": True, "field_path": payload.field_path, "locked": payload.locked}


# ─── Edit a single SEO field (manual override) ─────────────────────────────

@router.put("/targets/{type}/{id}/field")
async def update_field(type: str, id: str, payload: DraftFieldUpdate, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Edit manuale di un campo SEO. Scrive in `seo_meta` E nel campo diretto entity (publish istantaneo)."""
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "Invalid type")

    # field_path es. "it.meta_title"
    parts = payload.field_path.split(".", 1)
    update: Dict[str, Any] = {f"seo_meta.{payload.field_path}": payload.value, "seo_updated_at": _now_iso()}

    # Mapping diretto: "it.meta_title" → "seo_title.it"
    if len(parts) == 2:
        lang, key = parts
        mapped = _publish_mapping(type).get(key)
        if mapped:
            update[f"{mapped}.{lang}"] = payload.value

    if payload.is_locked is not None:
        update[f"seo_locks.{payload.field_path}"] = bool(payload.is_locked)
    await db[coll_name].update_one(_identifier_field(type, id), {"$set": update})
    return {"ok": True}


# ─── Generate (FASE 2 — pipeline reale Dual-Engine async via job queue) ───

@router.post("/targets/{type}/{id}/generate")
async def generate_draft(type: str, id: str, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    """
    Avvia un job asincrono che genera il draft SEO usando la pipeline AI:
    DataForSEO → Claude → Perplexity → DeepL → Gemini → Validator.
    Restituisce subito {job_id}; il frontend fa polling su /jobs/{job_id}.
    """
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "Invalid type")
    target_filter = _identifier_field(type, id)
    doc = await db[coll_name].find_one(target_filter, {"_id": 0})
    if not doc:
        raise HTTPException(404, f"{type} not found")

    from services.seo_orchestrator import create_job
    job_id = await create_job(type, id, coll_name, target_filter)
    # Marca lo stato sull'entity
    await db[coll_name].update_one(target_filter, {"$set": {"seo_status": "Generating", "seo_current_job": job_id}})
    return {"ok": True, "job_id": job_id, "status": "queued", "note": "Pipeline reale Dual-Engine avviata in background"}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Polling status di un job pipeline."""
    doc = await db.seo_jobs.find_one({"_id": job_id}, {"target_filter_repr": 0})
    if not doc:
        raise HTTPException(404, "Job not found")
    # _id is string (uuid) → safe to return
    return doc


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = None,
    target_type: Optional[str] = None,
    limit: int = 50,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Lista job (per dashboard bulk)."""
    flt: Dict[str, Any] = {}
    if status:
        flt["status"] = status
    if target_type:
        flt["target_type"] = target_type
    cursor = db.seo_jobs.find(flt, {"target_filter_repr": 0}).sort("created_at", -1).limit(limit)
    items: List[Dict[str, Any]] = []
    async for d in cursor:
        items.append(d)
    return {"items": items, "count": len(items)}


@router.post("/targets/bulk-generate")
async def bulk_generate(
    payload: Dict[str, Any],
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """
    Avvia generazione bulk per un set di target.
    Body: {"type": "team|league|event", "ids": ["slug1", "slug2", ...]}
    """
    type_ = payload.get("type")
    ids = payload.get("ids") or []
    coll_name = COLLECTION_MAP.get(type_)
    if not coll_name or not isinstance(ids, list):
        raise HTTPException(400, "Invalid payload")
    from services.seo_orchestrator import create_job
    jobs: List[str] = []
    for entity_id in ids[:50]:
        target_filter = _identifier_field(type_, entity_id)
        doc = await db[coll_name].find_one(target_filter, {"_id": 1})
        if not doc:
            continue
        job_id = await create_job(type_, entity_id, coll_name, target_filter)
        await db[coll_name].update_one(target_filter, {"$set": {"seo_status": "Generating", "seo_current_job": job_id}})
        jobs.append(job_id)
    return {"ok": True, "queued": len(jobs), "job_ids": jobs}


# ─── Publish draft → meta (rispettando i lock) ─────────────────────────────

@router.post("/targets/{type}/{id}/publish")
async def publish_draft(type: str, id: str, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    """
    Copia seo_draft → seo_meta rispettando i field con lock.
    Se un campo è locked, il valore esistente in seo_meta resta intatto.
    """
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "Invalid type")
    doc = await db[coll_name].find_one(_identifier_field(type, id), {"_id": 0})
    if not doc:
        raise HTTPException(404, f"{type} not found")
    draft = doc.get("seo_draft") or {}
    if not draft:
        raise HTTPException(400, "No draft to publish")

    locks: Dict[str, bool] = doc.get("seo_locks") or {}
    current_meta: Dict[str, Any] = doc.get("seo_meta") or {l: {} for l in LANGS}
    new_meta: Dict[str, Any] = {l: dict(current_meta.get(l) or {}) for l in LANGS}

    field_map = _publish_mapping(type)
    direct_updates: Dict[str, Any] = {}  # campi diretti su entity (es. seo_title.it)

    applied = 0
    skipped_locked = 0
    for lang, fields in draft.items():
        if lang not in LANGS:
            continue
        for k, v in (fields or {}).items():
            field_path = f"{lang}.{k}"
            if locks.get(field_path):
                skipped_locked += 1
                continue
            new_meta[lang][k] = v
            # mapping diretto sui campi standard di entity (events/leagues/teams)
            mapped = field_map.get(k)
            if mapped:
                direct_updates[f"{mapped}.{lang}"] = v
            # FAQ items → mappati su faq_N_q/a per tutti i type (events/leagues/teams)
            if k == "faq_items" and isinstance(v, list):
                for i, item in enumerate(v[:3], start=1):
                    if isinstance(item, dict):
                        if item.get("q"):
                            direct_updates[f"faq_{i}_q.{lang}"] = item["q"]
                        if item.get("a"):
                            direct_updates[f"faq_{i}_a.{lang}"] = item["a"]
            applied += 1

    update: Dict[str, Any] = {
        "seo_meta": new_meta,
        "seo_status": "Published",
        "seo_published_at": _now_iso(),
        **direct_updates,
    }
    # Schema (also lock-aware)
    if not locks.get("schema_jsonld") and doc.get("seo_draft_schema_jsonld"):
        update["seo_meta_schema_jsonld"] = doc["seo_draft_schema_jsonld"]

    await db[coll_name].update_one(_identifier_field(type, id), {"$set": update})
    return {"ok": True, "applied": applied, "skipped_locked": skipped_locked, "status": "Published", "direct_fields_written": len(direct_updates)}


# ─── Discard draft ─────────────────────────────────────────────────────────

@router.delete("/targets/{type}/{id}/draft")
async def discard_draft(type: str, id: str, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "Invalid type")
    await db[coll_name].update_one(
        _identifier_field(type, id),
        {"$unset": {"seo_draft": "", "seo_draft_schema_jsonld": "", "seo_generated_at": ""},
         "$set": {"seo_status": "Draft"}},
    )
    return {"ok": True}

"""
SEO Tools — Hero Image Generation (Nano Banana 2) + Export Module.
"""
import io
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

from database import db
from routes.admin_auth import verify_admin_token
from services import seo_image_gen
from routes.seo_targets import COLLECTION_MAP, _identifier_field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/seo", tags=["seo-tools"])

SEO_UPLOAD_DIR = Path("/app/backend/uploads/seo")
SEO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEAM_LOGO_DIR = Path("/app/backend/uploads/team_logos")
TEAM_LOGO_DIR.mkdir(parents=True, exist_ok=True)


# ─── Static File Serving for Hero Images ───────────────────────────────────

@router.get("/uploads/{filename}")
async def serve_seo_upload(filename: str):
    """Serve hero banner generato (PNG)."""
    file_path = SEO_UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    if not file_path.resolve().is_relative_to(SEO_UPLOAD_DIR.resolve()):
        raise HTTPException(403, "Access denied")
    return FileResponse(file_path, media_type="image/png")


@router.get("/team-logo/{filename}")
async def serve_team_logo(filename: str):
    """Serve cached team logos (proxiati da Wikimedia per evitare 403)."""
    file_path = TEAM_LOGO_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "Logo not found")
    if not file_path.resolve().is_relative_to(TEAM_LOGO_DIR.resolve()):
        raise HTTPException(403, "Access denied")
    ext = (file_path.suffix or ".png").lstrip(".")
    media_type = {
        "svg": "image/svg+xml",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "png": "image/png",
    }.get(ext, "image/png")
    return FileResponse(file_path, media_type=media_type)


# ─── Hero Image (Nano Banana 2) ────────────────────────────────────────────

class HeroImageRequest(BaseModel):
    save_to_entity: bool = True


@router.post("/hero-image/{type}/{id}")
async def generate_hero_image(
    type: str,
    id: str,
    payload: Optional[HeroImageRequest] = None,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Genera hero banner via Nano Banana 2 e salva URL su entity (campo seo_hero_image_url)."""
    coll_name = COLLECTION_MAP.get(type)
    if not coll_name:
        raise HTTPException(400, "Invalid type")
    target_filter = _identifier_field(type, id)
    doc = await db[coll_name].find_one(target_filter, {"_id": 0})
    if not doc:
        raise HTTPException(404, f"{type} not found")

    # Build context
    ctx = dict(doc)
    title = ctx.get("title") or ctx.get("name") or ""
    if type == "event" and ctx.get("home_team") and ctx.get("away_team"):
        title = f"{ctx['home_team']} vs {ctx['away_team']}"
    ctx["title"] = title

    slug = doc.get("slug") or id
    result = await seo_image_gen.generate_hero(type, ctx, slug)
    if result.get("status") != "success":
        raise HTTPException(500, result.get("error", "Image generation failed"))

    # Save URL on entity
    if not payload or payload.save_to_entity:
        await db[coll_name].update_one(
            target_filter,
            {"$set": {
                "seo_hero_image_url": result["url"],
                "seo_hero_image_generated_at": datetime.now(timezone.utc).isoformat(),
                "seo_hero_image_prompt": result.get("prompt", "")[:300],
            }},
        )
    return result


# ─── Export Module ─────────────────────────────────────────────────────────

EXPORT_FIELDS = [
    "slug", "name", "title", "home_team", "away_team", "league", "country",
    "seo_status", "seo_score", "seo_published_at",
    "seo_title", "seo_description", "seo_h1", "seo_intro", "seo_main_content",
    "seo_cta", "seo_og_title", "seo_og_description",
    "seo_internal_links", "seo_image_alt_texts", "seo_legal_disclosure",
    "seo_hero_image_url",
    "faq_1_q", "faq_1_a", "faq_2_q", "faq_2_a", "faq_3_q", "faq_3_a",
    "seo_meta_schema_jsonld",
]


def _flatten_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Estrae solo i campi rilevanti SEO dal doc."""
    out: Dict[str, Any] = {}
    for k in EXPORT_FIELDS:
        v = doc.get(k)
        if v is not None and v != "" and v != {}:
            out[k] = v
    return out


@router.get("/export")
async def export_seo_data(
    type: Optional[str] = Query(None),
    format: str = Query("json"),
    only_published: bool = Query(False),
    _=Depends(verify_admin_token),
):
    """
    Esporta i dati SEO di tutte le entity (event/league/team/all).
    format: json | csv | ndjson
    """
    targets = ["event", "league", "team"] if not type or type == "all" else [type]
    flt: Dict[str, Any] = {}
    if only_published:
        flt["seo_status"] = "Published"

    all_data: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {}
    for t in targets:
        coll_name = COLLECTION_MAP.get(t)
        if not coll_name:
            continue
        cursor = db[coll_name].find(flt, {"_id": 0})
        items: List[Dict[str, Any]] = []
        async for doc in cursor:
            flat = _flatten_doc(doc)
            if flat:
                flat["_entity_type"] = t
                items.append(flat)
        all_data.extend(items)
        counts[t] = len(items)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"seo-export-{type or 'all'}-{timestamp}"

    if format == "csv":
        buf = io.StringIO()
        if all_data:
            # Use union of keys, prioritize EXPORT_FIELDS
            all_keys = ["_entity_type"] + EXPORT_FIELDS
            writer = csv.DictWriter(buf, fieldnames=all_keys, extrasaction="ignore")
            writer.writeheader()
            for row in all_data:
                # Stringify dict/list fields
                clean = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in row.items()}
                writer.writerow(clean)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'},
        )

    if format == "ndjson":
        buf = io.StringIO()
        for row in all_data:
            buf.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": f'attachment; filename="{filename}.ndjson"'},
        )

    # default json
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_data),
        "counts": counts,
        "items": all_data,
    }
    body = json.dumps(payload, ensure_ascii=False, default=str, indent=2)
    return StreamingResponse(
        iter([body]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}.json"'},
    )


# ─── Bulk Generate by League / Filter ──────────────────────────────────────

class BulkLeagueRequest(BaseModel):
    league_slug: str  # es. "serie-a"
    type: str = "team"   # team|event
    only_pending: bool = True   # salta entity con seo_status == 'Published'
    limit: int = 50


@router.post("/targets/bulk-generate-league")
async def bulk_generate_for_league(
    payload: BulkLeagueRequest,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """
    Avvia generazione bulk per tutte le entity di una lega.
    Esempio: bulk-generate-league {league_slug:'serie-a', type:'team'} → genera tutte le 20 squadre.
    """
    coll_name = COLLECTION_MAP.get(payload.type)
    if not coll_name or payload.type not in ("team", "event"):
        raise HTTPException(400, "type must be 'team' or 'event'")

    flt: Dict[str, Any] = {"league_slug": payload.league_slug}
    if payload.only_pending:
        flt["seo_status"] = {"$ne": "Published"}

    cursor = db[coll_name].find(flt, {"_id": 0, "slug": 1, "name": 1, "home_team": 1, "away_team": 1}).limit(payload.limit)
    from services.seo_orchestrator import create_job

    jobs: List[Dict[str, str]] = []
    async for doc in cursor:
        slug = doc.get("slug")
        if not slug:
            continue
        target_filter = {"slug": slug}
        job_id = await create_job(payload.type, slug, coll_name, target_filter)
        await db[coll_name].update_one(
            target_filter,
            {"$set": {"seo_status": "Generating", "seo_current_job": job_id}},
        )
        label = doc.get("name") or (f"{doc.get('home_team','')} vs {doc.get('away_team','')}" if payload.type == "event" else slug)
        jobs.append({"job_id": job_id, "slug": slug, "label": label})

    return {
        "ok": True,
        "queued": len(jobs),
        "league_slug": payload.league_slug,
        "type": payload.type,
        "jobs": jobs,
    }

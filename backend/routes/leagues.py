from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from database import db
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["leagues"])

# Models
class LeagueBase(BaseModel):
    name: str
    slug: str
    country: str
    type: str = "league"  # "league" or "cup"
    logo_url: Optional[str] = None
    active: bool = True
    order: int = 0

class LeagueCreate(LeagueBase):
    pass

class LeagueUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    logo_url: Optional[str] = None
    active: Optional[bool] = None
    order: Optional[int] = None

# Public endpoints
@router.get("/leagues/active-slugs")
async def get_active_slugs():
    """Restituisce solo l'array degli slug attivi - usato dal frontend per routing dinamico."""
    leagues = await db.leagues.find(
        {"active": True}, {"_id": 0, "slug": 1}
    ).to_list(200)
    return {"slugs": [l["slug"] for l in leagues if l.get("slug")]}


@router.get("/leagues")
async def get_leagues(type: Optional[str] = None, active_only: bool = True):
    """Get all leagues/cups"""
    query = {}
    if type:
        query["type"] = type
    if active_only:
        query["active"] = True
    
    leagues = await db.leagues.find(query, {"_id": 1, "name": 1, "slug": 1, "country": 1, "type": 1, "logo_url": 1, "order": 1}).sort("order", 1).to_list(100)
    
    result = []
    for league in leagues:
        result.append({
            "id": str(league["_id"]),
            "name": league.get("name", ""),
            "slug": league.get("slug", ""),
            "country": league.get("country", ""),
            "type": league.get("type", "league"),
            "logo_url": league.get("logo_url", ""),
            "order": league.get("order", 0)
        })
    
    return {"leagues": result, "total": len(result)}

@router.get("/leagues/{slug}")
async def get_league_by_slug(slug: str):
    """Get league by slug"""
    league = await db.leagues.find_one({"slug": slug})
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Get teams for this league
    teams = await db.teams.find({"league_slug": slug, "active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    
    return {
        "id": str(league["_id"]),
        "name": league.get("name", ""),
        "slug": league.get("slug", ""),
        "country": league.get("country", ""),
        "type": league.get("type", "league"),
        "logo_url": league.get("logo_url", ""),
        "teams": teams,
        # SEO fields multilingua (popolati dal SEO Admin)
        "seo_title": league.get("seo_title") or {},
        "seo_description": league.get("seo_description") or {},
        "seo_h1": league.get("seo_h1") or {},
        "seo_intro": league.get("seo_intro") or {},
        "seo_cta": league.get("seo_cta") or {},
    }

# Admin endpoints
@router.get("/admin/leagues")
async def admin_get_leagues():
    """Admin: Get all leagues including inactive"""
    leagues = await db.leagues.find({}).sort("order", 1).to_list(100)
    
    result = []
    for league in leagues:
        # Count teams
        team_count = await db.teams.count_documents({"league_slug": league.get("slug")})
        result.append({
            "id": str(league["_id"]),
            "name": league.get("name", ""),
            "slug": league.get("slug", ""),
            "country": league.get("country", ""),
            "type": league.get("type", "league"),
            "logo_url": league.get("logo_url", ""),
            "active": league.get("active", True),
            "order": league.get("order", 0),
            "team_count": team_count
        })
    
    return {"leagues": result, "total": len(result)}

@router.post("/admin/leagues")
async def admin_create_league(league: LeagueCreate):
    """Admin: Create a new league"""
    # Check if slug exists
    existing = await db.leagues.find_one({"slug": league.slug})
    if existing:
        raise HTTPException(status_code=400, detail="League with this slug already exists")
    
    league_dict = league.model_dump()
    league_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    league_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.leagues.insert_one(league_dict)
    
    return {"success": True, "id": str(result.inserted_id), "message": "League created"}

@router.put("/admin/leagues/{league_id}")
async def admin_update_league(league_id: str, league: LeagueUpdate):
    """Admin: Update a league"""
    try:
        oid = ObjectId(league_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid league ID")
    
    update_data = {k: v for k, v in league.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.leagues.update_one({"_id": oid}, {"$set": update_data})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="League not found")
    
    return {"success": True, "message": "League updated"}

@router.delete("/admin/leagues/{league_id}")
async def admin_delete_league(league_id: str):
    """Admin: Delete a league"""
    try:
        oid = ObjectId(league_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid league ID")
    
    # Get league slug first
    league = await db.leagues.find_one({"_id": oid})
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Delete league
    await db.leagues.delete_one({"_id": oid})
    
    # Also delete associated teams
    await db.teams.delete_many({"league_slug": league.get("slug")})
    
    return {"success": True, "message": "League and associated teams deleted"}

@router.post("/admin/leagues/seed")
async def admin_seed_leagues():
    """Admin: Seed default leagues and cups"""
    default_leagues = [
        {"name": "Serie A", "slug": "serie-a", "country": "Italy", "type": "league", "order": 1},
        {"name": "Premier League", "slug": "premier-league", "country": "England", "type": "league", "order": 2},
        {"name": "La Liga", "slug": "la-liga", "country": "Spain", "type": "league", "order": 3},
        {"name": "Bundesliga", "slug": "bundesliga", "country": "Germany", "type": "league", "order": 4},
        {"name": "Ligue 1", "slug": "ligue-1", "country": "France", "type": "league", "order": 5},
        {"name": "Liga Portugal", "slug": "liga-portugal", "country": "Portugal", "type": "league", "order": 6},
        {"name": "Super Lig", "slug": "super-lig", "country": "Turkey", "type": "league", "order": 7},
        {"name": "Champions League", "slug": "champions-league", "country": "Europe", "type": "cup", "order": 10},
        {"name": "Europa League", "slug": "europa-league", "country": "Europe", "type": "cup", "order": 11},
        {"name": "Coppa Italia", "slug": "coppa-italia", "country": "Italy", "type": "cup", "order": 12},
        {"name": "FA Cup", "slug": "fa-cup", "country": "England", "type": "cup", "order": 13},
        {"name": "Copa del Rey", "slug": "copa-del-rey", "country": "Spain", "type": "cup", "order": 14},
        {"name": "DFB Pokal", "slug": "dfb-pokal", "country": "Germany", "type": "cup", "order": 15},
    ]
    
    inserted = 0
    for league in default_leagues:
        existing = await db.leagues.find_one({"slug": league["slug"]})
        if not existing:
            league["active"] = True
            league["created_at"] = datetime.now(timezone.utc).isoformat()
            league["updated_at"] = datetime.now(timezone.utc).isoformat()
            await db.leagues.insert_one(league)
            inserted += 1
    
    return {"success": True, "message": f"Seeded {inserted} leagues", "inserted": inserted}

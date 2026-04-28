from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from database import db
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["teams"])

# Models
class TeamBase(BaseModel):
    name: str
    slug: str
    league_slug: str
    city: Optional[str] = None
    stadium: Optional[str] = None
    logo_url: Optional[str] = None
    active: bool = True
    order: int = 0

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    league_slug: Optional[str] = None
    city: Optional[str] = None
    stadium: Optional[str] = None
    logo_url: Optional[str] = None
    active: Optional[bool] = None
    order: Optional[int] = None

class BulkTeamCreate(BaseModel):
    league_slug: str
    teams: List[str]  # List of team names

# Public endpoints
@router.get("/teams")
async def get_teams(league_slug: Optional[str] = None, active_only: bool = True):
    """Get all teams, optionally filtered by league"""
    query = {}
    if league_slug:
        query["league_slug"] = league_slug
    if active_only:
        query["active"] = True
    
    teams = await db.teams.find(query, {"_id": 1, "name": 1, "slug": 1, "league_slug": 1, "city": 1, "stadium": 1, "logo_url": 1, "order": 1}).sort("order", 1).to_list(500)
    
    result = []
    for team in teams:
        result.append({
            "id": str(team["_id"]),
            "name": team.get("name", ""),
            "slug": team.get("slug", ""),
            "league_slug": team.get("league_slug", ""),
            "city": team.get("city", ""),
            "stadium": team.get("stadium", ""),
            "logo_url": team.get("logo_url", ""),
            "order": team.get("order", 0)
        })
    
    return {"teams": result, "total": len(result)}

@router.get("/teams/{slug}")
async def get_team_by_slug(slug: str):
    """Get team by slug"""
    team = await db.teams.find_one({"slug": slug})
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return {
        "id": str(team["_id"]),
        "name": team.get("name", ""),
        "slug": team.get("slug", ""),
        "league_slug": team.get("league_slug", ""),
        "city": team.get("city", ""),
        "stadium": team.get("stadium", ""),
        "logo_url": team.get("logo_url", "")
    }

# Admin endpoints
@router.get("/admin/teams")
async def admin_get_teams(league_slug: Optional[str] = None):
    """Admin: Get all teams including inactive"""
    query = {}
    if league_slug:
        query["league_slug"] = league_slug
    
    teams = await db.teams.find(query).sort([("league_slug", 1), ("order", 1), ("name", 1)]).to_list(500)
    
    result = []
    for team in teams:
        result.append({
            "id": str(team["_id"]),
            "name": team.get("name", ""),
            "slug": team.get("slug", ""),
            "league_slug": team.get("league_slug", ""),
            "city": team.get("city", ""),
            "stadium": team.get("stadium", ""),
            "logo_url": team.get("logo_url", ""),
            "active": team.get("active", True),
            "order": team.get("order", 0)
        })
    
    return {"teams": result, "total": len(result)}

@router.post("/admin/teams")
async def admin_create_team(team: TeamCreate):
    """Admin: Create a new team"""
    # Check if slug exists
    existing = await db.teams.find_one({"slug": team.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Team with this slug already exists")
    
    # Verify league exists
    league = await db.leagues.find_one({"slug": team.league_slug})
    if not league:
        raise HTTPException(status_code=400, detail="League not found")
    
    team_dict = team.model_dump()
    team_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    team_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.teams.insert_one(team_dict)
    
    return {"success": True, "id": str(result.inserted_id), "message": "Team created"}

@router.post("/admin/teams/bulk")
async def admin_bulk_create_teams(data: BulkTeamCreate):
    """Admin: Bulk create teams for a league"""
    # Verify league exists
    league = await db.leagues.find_one({"slug": data.league_slug})
    if not league:
        raise HTTPException(status_code=400, detail="League not found")
    
    inserted = 0
    for i, team_name in enumerate(data.teams):
        slug = team_name.lower().replace(" ", "-").replace(".", "").replace("'", "")
        
        existing = await db.teams.find_one({"slug": slug})
        if not existing:
            team_dict = {
                "name": team_name,
                "slug": slug,
                "league_slug": data.league_slug,
                "active": True,
                "order": i,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.teams.insert_one(team_dict)
            inserted += 1
    
    return {"success": True, "message": f"Created {inserted} teams", "inserted": inserted}

@router.put("/admin/teams/{team_id}")
async def admin_update_team(team_id: str, team: TeamUpdate):
    """Admin: Update a team"""
    try:
        oid = ObjectId(team_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid team ID")
    
    update_data = {k: v for k, v in team.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.teams.update_one({"_id": oid}, {"$set": update_data})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return {"success": True, "message": "Team updated"}

@router.delete("/admin/teams/{team_id}")
async def admin_delete_team(team_id: str):
    """Admin: Delete a team"""
    try:
        oid = ObjectId(team_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid team ID")
    
    result = await db.teams.delete_one({"_id": oid})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return {"success": True, "message": "Team deleted"}

@router.post("/admin/teams/seed")
async def admin_seed_teams():
    """Admin: Seed default teams for all leagues"""
    default_teams = {
        "serie-a": [
            "Atalanta", "Bologna", "Cagliari", "Como", "Cremonese", "Empoli",
            "Fiorentina", "Genoa", "Hellas Verona", "Inter", "Juventus", "Lazio",
            "Lecce", "Milan", "Monza", "Napoli", "Parma", "Pisa", "Roma", 
            "Salernitana", "Sassuolo", "Torino", "Udinese", "Venezia"
        ],
        "premier-league": [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
            "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
            "Leeds United", "Leicester City", "Liverpool", "Manchester City",
            "Manchester United", "Newcastle United", "Nottingham Forest",
            "Sheffield United", "Sunderland", "Tottenham", "West Ham", "Wolves"
        ],
        "la-liga": [
            "Alavés", "Athletic Bilbao", "Atlético Madrid", "Barcelona", "Betis",
            "Celta Vigo", "Elche", "Espanyol", "Getafe", "Girona", "Granada",
            "Las Palmas", "Levante", "Mallorca", "Osasuna", "Oviedo",
            "Rayo Vallecano", "Real Madrid", "Real Sociedad", "Sevilla",
            "Valencia", "Villarreal"
        ],
        "bundesliga": [
            "Augsburg", "Bayern Munich", "Borussia Dortmund", "Borussia Mönchengladbach",
            "Eintracht Frankfurt", "FC Köln", "Freiburg", "Hamburger SV",
            "Heidenheim", "Hoffenheim", "Leverkusen", "Mainz", "RB Leipzig",
            "St. Pauli", "Stuttgart", "Union Berlin", "Werder Bremen", "Wolfsburg"
        ],
        "ligue-1": [
            "Auxerre", "Brest", "Lens", "Lille", "Lyon", "Marseille",
            "Monaco", "Montpellier", "Nantes", "Nice", "PSG", "Reims",
            "Rennes", "Strasbourg", "Toulouse"
        ],
        "liga-portugal": [
            "Arouca", "AVS", "Benfica", "Boavista", "Braga", "Casa Pia",
            "Estoril", "Famalicão", "Farense", "Gil Vicente", "Moreirense",
            "Nacional", "Porto", "Rio Ave", "Santa Clara", "Sporting CP",
            "Estrela", "Vitória Guimarães"
        ],
        "super-lig": [
            "Adana Demirspor", "Alanyaspor", "Antalyaspor", "Başakşehir",
            "Beşiktaş", "Fenerbahçe", "Galatasaray", "Gaziantep",
            "Hatayspor", "İstanbulspor", "Kasımpaşa", "Kayserispor",
            "Konyaspor", "Pendikspor", "Rizespor", "Samsunspor",
            "Sivasspor", "Trabzonspor"
        ]
    }
    
    total_inserted = 0
    for league_slug, teams in default_teams.items():
        for i, team_name in enumerate(teams):
            slug = team_name.lower().replace(" ", "-").replace(".", "").replace("'", "").replace("ö", "o").replace("ü", "u").replace("ş", "s").replace("ı", "i").replace("ç", "c").replace("é", "e").replace("á", "a")
            
            existing = await db.teams.find_one({"slug": slug})
            if not existing:
                team_dict = {
                    "name": team_name,
                    "slug": slug,
                    "league_slug": league_slug,
                    "active": True,
                    "order": i,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                await db.teams.insert_one(team_dict)
                total_inserted += 1
    
    return {"success": True, "message": f"Seeded {total_inserted} teams", "inserted": total_inserted}

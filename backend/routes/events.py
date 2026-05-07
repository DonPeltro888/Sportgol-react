from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.event import Event, EventCreate, EventUpdate
from database import db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/events", tags=["events"])

# Location filters per language
LANGUAGE_FILTERS = {
    "it": {
        # Italy cities + Champions League cities (London, Manchester, Madrid, Barcelona)
        "locations": ["Milan", "Rome", "Turin", "Naples", "Florence", "Bologna", "Genoa", 
                     "Bergamo", "Verona", "Udine", "Cagliari", "Lecce", "Parma", "Como",
                     "Cremona", "Pisa", "Reggio Emilia", "London", "Manchester", "Madrid", "Barcelona"],
        "include_champions": True
    },
    "es": {
        # Spain cities + London, Manchester, Madrid, Barcelona
        "locations": ["Madrid", "Barcelona", "Seville", "Valencia", "Bilbao", "Vigo",
                     "Girona", "Elche", "Oviedo", "Palma", "London", "Manchester"],
        "include_champions": False
    },
    "en": {
        # UK cities + Madrid, Barcelona, Milan, Rome, Florence (Fiorentina)
        "locations": ["London", "Manchester", "Liverpool", "Birmingham", "Newcastle",
                     "Leeds", "Brighton", "Bournemouth", "Wolverhampton", "Burnley",
                     "Madrid", "Barcelona", "Milan", "Rome", "Florence"],
        "include_champions": False
    }
}

@router.get("", response_model=dict)
async def get_events(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    league: Optional[str] = None,
    featured: Optional[bool] = None,
    lang: Optional[str] = Query(None, description="Language filter: it, es, en"),
    include_past: Optional[bool] = Query(False, description="Include past events")
):
    """Get all events with pagination and filtering"""
    try:
        skip = (page - 1) * limit
        query = {}
        
        # Filter out past events (event visible until midnight of match day)
        if not include_past:
            # Get today's date at midnight (start of day)
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_str = today.strftime("%Y-%m-%d")
            
            # Events with sort_date >= today (visible until midnight of match day)
            query["sort_date"] = {"$gte": today_str}
        
        # Language-based location filter
        if lang and lang in LANGUAGE_FILTERS:
            filter_config = LANGUAGE_FILTERS[lang]
            locations = filter_config["locations"]
            
            location_query = {"location": {"$in": locations}}
            
            # For Italian, also include Champions League events
            if filter_config.get("include_champions"):
                query["$or"] = [
                    location_query,
                    {"categories": {"$regex": "Champions League", "$options": "i"}},
                    {"title": {"$regex": "Champions League", "$options": "i"}}
                ]
            else:
                query.update(location_query)
        
        if search:
            # Search only in title, not in location (to avoid city/team name confusion)
            search_query = [
                {"title": {"$regex": search, "$options": "i"}},
                {"categories": {"$regex": search, "$options": "i"}}
            ]
            if "$or" in query:
                # Combine with existing $or using $and
                query = {"$and": [query, {"$or": search_query}]}
            else:
                query["$or"] = search_query
        
        if league:
            query["league"] = league
        
        if featured is not None:
            query["featured"] = featured
        
        total = await db.events.count_documents(query)
        # Sort by sort_date (ascending - upcoming events first)
        events = await db.events.find(query).sort([("sort_date", 1), ("created_at", 1)]).skip(skip).limit(limit).to_list(length=limit)
        
        # Enrich events with team logos (single batch query for performance)
        from services.team_normalize import normalize_team
        team_names = set()
        for ev in events:
            if ev.get("home_team"): team_names.add(ev["home_team"])
            if ev.get("away_team"): team_names.add(ev["away_team"])

        team_logo_map: dict = {}
        if team_names:
            async for t in db.teams.find(
                {"logo_url": {"$exists": True, "$ne": ""}},
                {"_id": 0, "name": 1, "logo_url": 1}
            ):
                norm = normalize_team(t.get("name", ""))
                if norm and norm not in team_logo_map:
                    team_logo_map[norm] = t["logo_url"]

        # Convert ObjectId to string + attach logos
        for event in events:
            event["_id"] = str(event["_id"])
            event["id"] = str(event["_id"])
            event["home_team_logo"] = team_logo_map.get(normalize_team(event.get("home_team", "")))
            event["away_team_logo"] = team_logo_map.get(normalize_team(event.get("away_team", "")))
            # slug already stored in DB via backfill; fallback if missing
            if not event.get("slug"):
                from services.event_slug import compute_base_slug
                event["slug"] = compute_base_slug(event)
        
        return {
            "events": events,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-slug/{slug}", response_model=dict)
async def get_event_by_slug(slug: str):
    """Get single event by SEO slug (e.g. 'inter-vs-parma')."""
    try:
        event = await db.events.find_one({"slug": slug})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        event["_id"] = str(event["_id"])
        event["id"] = str(event["_id"])

        # Enrich with team logos (normalized lookup)
        from services.team_normalize import normalize_team
        for team_field, logo_field in [("home_team", "home_team_logo"), ("away_team", "away_team_logo")]:
            team_name = event.get(team_field)
            if team_name:
                norm = normalize_team(team_name)
                # find any team whose normalized name matches
                logo: str = ""
                async for t in db.teams.find({"logo_url": {"$exists": True, "$ne": ""}}, {"_id": 0, "name": 1, "logo_url": 1}):
                    if normalize_team(t.get("name", "")) == norm:
                        logo = t["logo_url"]
                        break
                event[logo_field] = logo or None

        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event by slug: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-team-slug/{team_slug}", response_model=dict)
async def get_events_by_team_slug(team_slug: str, limit: int = 50):
    """
    Get events of a SPECIFIC team using EXACT name+league match (no regex).
    Avoids name confusion (es. 'Inter' vs 'Inter Miami').
    Match: event.home_team == team.name OR event.away_team == team.name,
    AND event.league_slug == team.league_slug (if available on team).
    """
    try:
        team = await db.teams.find_one({"slug": team_slug}, {"_id": 0})
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        team_name = team.get("name", "")
        team_league_slug = team.get("league_slug", "")

        # Resolve league name (events store league name uppercase/titlecase, NOT slug)
        league_name = ""
        if team_league_slug:
            league_doc = await db.leagues.find_one({"slug": team_league_slug}, {"_id": 0, "name": 1})
            if league_doc:
                league_name = league_doc.get("name", "")

        # Exact match on home_team OR away_team (CASE-INSENSITIVE for safety)
        import re as _re
        team_re = f"^{_re.escape(team_name)}$"
        query: dict = {"$or": [
            {"home_team": {"$regex": team_re, "$options": "i"}},
            {"away_team": {"$regex": team_re, "$options": "i"}},
        ]}
        # If team belongs to a league, scope events to same league name (anti name-collision)
        if league_name:
            league_re = f"^{_re.escape(league_name)}$"
            query = {"$and": [query, {"league": {"$regex": league_re, "$options": "i"}}]}

        events = await db.events.find(query).sort("sort_date", 1).limit(limit).to_list(length=limit)

        # Enrich with team logos (batch with normalized matching)
        from services.team_normalize import normalize_team
        team_names = set()
        for ev in events:
            if ev.get("home_team"): team_names.add(ev["home_team"])
            if ev.get("away_team"): team_names.add(ev["away_team"])

        # Build team_logo_map keyed BY NORMALIZED name → logo
        team_logo_map: dict = {}
        if team_names:
            async for t in db.teams.find(
                {"logo_url": {"$exists": True, "$ne": ""}},
                {"_id": 0, "name": 1, "logo_url": 1}
            ):
                norm = normalize_team(t.get("name", ""))
                if norm and norm not in team_logo_map:
                    team_logo_map[norm] = t["logo_url"]

        for event in events:
            event["_id"] = str(event["_id"])
            event["id"] = str(event["_id"])
            event["home_team_logo"] = team_logo_map.get(normalize_team(event.get("home_team", "")))
            event["away_team_logo"] = team_logo_map.get(normalize_team(event.get("away_team", "")))

        return {
            "team": {"slug": team_slug, "name": team_name, "league_slug": team_league_slug},
            "events": events,
            "total": len(events),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching events by team slug: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str):
    """Get single event by ID"""
    try:
        from bson import ObjectId
        event = await db.events.find_one({"_id": ObjectId(event_id)})
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event["_id"] = str(event["_id"])
        event["id"] = str(event["_id"])

        # Ensure slug is present
        if not event.get("slug"):
            from services.event_slug import compute_base_slug
            event["slug"] = compute_base_slug(event)

        # Enrich with team logos
        for team_field, logo_field in [("home_team", "home_team_logo"), ("away_team", "away_team_logo")]:
            team_name = event.get(team_field)
            if team_name:
                team_doc = await db.teams.find_one(
                    {"name": team_name},
                    {"_id": 0, "logo_url": 1}
                )
                event[logo_field] = team_doc.get("logo_url") if team_doc else None
        
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=dict)
async def create_event(event: EventCreate):
    """Create new event"""
    try:
        event_dict = event.dict()
        event_dict["created_at"] = datetime.now(timezone.utc)
        event_dict["updated_at"] = datetime.now(timezone.utc)
        
        from services.db_normalize import normalize_event_doc
        result = await db.events.insert_one(normalize_event_doc(event_dict))
        event_dict["_id"] = str(result.inserted_id)
        event_dict["id"] = str(result.inserted_id)
        
        return event_dict
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{event_id}", response_model=dict)
async def update_event(event_id: str, event: EventUpdate):
    """Update event"""
    try:
        from bson import ObjectId
        update_data = {k: v for k, v in event.dict(exclude_unset=True).items()}
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.events.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        updated_event = await db.events.find_one({"_id": ObjectId(event_id)})
        updated_event["_id"] = str(updated_event["_id"])
        updated_event["id"] = str(updated_event["_id"])
        
        return updated_event
    except Exception as e:
        logger.error(f"Error updating event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """Delete event"""
    try:
        from bson import ObjectId
        result = await db.events.delete_one({"_id": ObjectId(event_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {"message": "Event deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from database import db
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/api/admin", tags=["sectors"])

# Default sectors template
DEFAULT_SECTORS = [
    {"name": "Cat 1 Premium", "price": 0, "available": True, "notes": ""},
    {"name": "Cat 1 Normal", "price": 0, "available": True, "notes": ""},
    {"name": "Cat 2 Short Side Lower", "price": 0, "available": True, "notes": ""},
    {"name": "Cat 2 Long Side Upper", "price": 0, "available": True, "notes": ""},
    {"name": "Cat 3 Short Side", "price": 0, "available": True, "notes": ""},
    {"name": "Best Available", "price": 0, "available": True, "notes": ""},
]

class Sector(BaseModel):
    name: str
    price: float = 0
    available: bool = True
    notes: str = ""

class SectorUpdate(BaseModel):
    sectors: List[Sector]

class BulkSectorUpdate(BaseModel):
    event_ids: List[str]
    sectors: List[Sector]

class BulkPriceUpdate(BaseModel):
    event_ids: List[str]
    sector_name: str
    price: float
    available: Optional[bool] = None

@router.get("/sectors/defaults")
async def get_default_sectors():
    """Get default sector template"""
    return {"sectors": DEFAULT_SECTORS}

@router.get("/sectors/events")
async def get_events_with_sectors():
    """Get all events with their sectors for management"""
    events = await db.events.find(
        {},
        {
            "_id": 1,
            "title": 1,
            "date": 1,
            "stadium": 1,
            "location": 1,
            "league": 1,
            "ticket_categories": 1,
            "price_range": 1
        }
    ).sort("sort_date", 1).to_list(500)
    
    result = []
    for event in events:
        result.append({
            "id": str(event["_id"]),
            "title": event.get("title", ""),
            "date": event.get("date", ""),
            "stadium": event.get("stadium", ""),
            "location": event.get("location", ""),
            "league": event.get("league", ""),
            "sectors": event.get("ticket_categories", []),
            "price_range": event.get("price_range", {}),
            "has_sectors": len(event.get("ticket_categories", [])) > 0
        })
    
    return {"events": result, "total": len(result)}

@router.get("/sectors/event/{event_id}")
async def get_event_sectors(event_id: str):
    """Get sectors for a specific event"""
    try:
        event = await db.events.find_one(
            {"_id": ObjectId(event_id)},
            {"_id": 1, "title": 1, "ticket_categories": 1, "price_range": 1}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {
        "id": str(event["_id"]),
        "title": event.get("title", ""),
        "sectors": event.get("ticket_categories", []),
        "price_range": event.get("price_range", {})
    }

@router.put("/sectors/event/{event_id}")
async def update_event_sectors(event_id: str, data: SectorUpdate):
    """Update sectors for a specific event"""
    try:
        oid = ObjectId(event_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    # Convert sectors to dict format
    sectors_data = [s.model_dump() for s in data.sectors]
    
    # Calculate price range from sectors
    prices = [s.price for s in data.sectors if s.price > 0]
    price_range = {
        "min": min(prices) if prices else 0,
        "max": max(prices) if prices else 0
    }
    
    result = await db.events.update_one(
        {"_id": oid},
        {
            "$set": {
                "ticket_categories": sectors_data,
                "price_range": price_range,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"success": True, "message": "Sectors updated", "sectors": sectors_data}

@router.post("/sectors/event/{event_id}/defaults")
async def add_default_sectors(event_id: str):
    """Add default sectors to an event"""
    try:
        oid = ObjectId(event_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    result = await db.events.update_one(
        {"_id": oid},
        {
            "$set": {
                "ticket_categories": DEFAULT_SECTORS.copy(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"success": True, "message": "Default sectors added", "sectors": DEFAULT_SECTORS}

@router.post("/sectors/bulk")
async def bulk_update_sectors(data: BulkSectorUpdate):
    """Bulk update sectors for multiple events"""
    sectors_data = [s.model_dump() for s in data.sectors]
    
    # Calculate price range
    prices = [s.price for s in data.sectors if s.price > 0]
    price_range = {
        "min": min(prices) if prices else 0,
        "max": max(prices) if prices else 0
    }
    
    updated_count = 0
    for event_id in data.event_ids:
        try:
            oid = ObjectId(event_id)
            result = await db.events.update_one(
                {"_id": oid},
                {
                    "$set": {
                        "ticket_categories": sectors_data,
                        "price_range": price_range,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            if result.modified_count > 0:
                updated_count += 1
        except Exception:
            continue
    
    return {
        "success": True,
        "message": f"Updated {updated_count} events",
        "updated_count": updated_count
    }

@router.post("/sectors/bulk-defaults")
async def bulk_add_default_sectors(event_ids: List[str]):
    """Add default sectors to multiple events"""
    updated_count = 0
    for event_id in event_ids:
        try:
            oid = ObjectId(event_id)
            result = await db.events.update_one(
                {"_id": oid},
                {
                    "$set": {
                        "ticket_categories": DEFAULT_SECTORS.copy(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            if result.modified_count > 0:
                updated_count += 1
        except Exception:
            continue
    
    return {
        "success": True,
        "message": f"Added default sectors to {updated_count} events",
        "updated_count": updated_count
    }

@router.post("/sectors/bulk-price")
async def bulk_update_sector_price(data: BulkPriceUpdate):
    """Bulk update price for a specific sector across multiple events"""
    updated_count = 0
    
    for event_id in data.event_ids:
        try:
            oid = ObjectId(event_id)
            
            # Get current event
            event = await db.events.find_one({"_id": oid})
            if not event:
                continue
            
            # Update the specific sector
            sectors = event.get("ticket_categories", [])
            updated = False
            for sector in sectors:
                if sector.get("name") == data.sector_name:
                    sector["price"] = data.price
                    if data.available is not None:
                        sector["available"] = data.available
                    updated = True
                    break
            
            if updated:
                # Recalculate price range
                prices = [s.get("price", 0) for s in sectors if s.get("price", 0) > 0]
                price_range = {
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0
                }
                
                await db.events.update_one(
                    {"_id": oid},
                    {
                        "$set": {
                            "ticket_categories": sectors,
                            "price_range": price_range,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                updated_count += 1
        except Exception:
            continue
    
    return {
        "success": True,
        "message": f"Updated price for {updated_count} events",
        "updated_count": updated_count
    }

@router.delete("/sectors/event/{event_id}")
async def clear_event_sectors(event_id: str):
    """Clear all sectors from an event"""
    try:
        oid = ObjectId(event_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    result = await db.events.update_one(
        {"_id": oid},
        {
            "$set": {
                "ticket_categories": [],
                "price_range": {"min": 0, "max": 0},
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"success": True, "message": "Sectors cleared"}

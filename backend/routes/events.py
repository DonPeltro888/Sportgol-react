from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.event import Event, EventCreate, EventUpdate
from database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("", response_model=dict)
async def get_events(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    league: Optional[str] = None,
    featured: Optional[bool] = None
):
    """Get all events with pagination and filtering"""
    try:
        skip = (page - 1) * limit
        query = {}
        
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}},
                {"categories": {"$regex": search, "$options": "i"}}
            ]
        
        if league:
            query["league"] = league
        
        if featured is not None:
            query["featured"] = featured
        
        total = await db.events.count_documents(query)
        # Sort by sort_date (ascending - upcoming events first)
        events = await db.events.find(query).sort([("sort_date", 1), ("created_at", 1)]).skip(skip).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string
        for event in events:
            event["_id"] = str(event["_id"])
            event["id"] = str(event["_id"])
        
        return {
            "events": events,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
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
        return event
    except Exception as e:
        logger.error(f"Error fetching event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=dict)
async def create_event(event: EventCreate):
    """Create new event"""
    try:
        event_dict = event.dict()
        event_dict["created_at"] = datetime.utcnow()
        event_dict["updated_at"] = datetime.utcnow()
        
        result = await db.events.insert_one(event_dict)
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
        update_data["updated_at"] = datetime.utcnow()
        
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

from fastapi import APIRouter, HTTPException, Query
from typing import List
from server import db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("", response_model=List[dict])
async def search_events(q: str = Query(..., min_length=1)):
    """Global search across events"""
    try:
        query = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"location": {"$regex": q, "$options": "i"}},
                {"categories": {"$regex": q, "$options": "i"}},
                {"stadium": {"$regex": q, "$options": "i"}},
                {"league": {"$regex": q, "$options": "i"}}
            ]
        }
        
        events = await db.events.find(query).limit(50).to_list(length=50)
        
        for event in events:
            event["_id"] = str(event["_id"])
            event["id"] = str(event["_id"])
        
        return events
    except Exception as e:
        logger.error(f"Error searching events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

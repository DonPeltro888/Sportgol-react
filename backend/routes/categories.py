from fastapi import APIRouter, HTTPException
from typing import List
from models.category import Category, CategoryCreate
from database import db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("", response_model=List[dict])
async def get_categories():
    """Get all categories"""
    try:
        categories = await db.categories.find().to_list(length=100)
        
        for category in categories:
            category["_id"] = str(category["_id"])
            category["id"] = str(category["_id"])
        
        return categories
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}", response_model=dict)
async def get_category_with_events(slug: str):
    """Get category with associated events"""
    try:
        category = await db.categories.find_one({"slug": slug})
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category["_id"] = str(category["_id"])
        category["id"] = str(category["_id"])
        
        # Find events with this category, sorted by date descending
        events = await db.events.find(
            {"categories": {"$regex": category["name"], "$options": "i"}}
        ).sort([("date", -1)]).to_list(length=100)
        
        for event in events:
            event["_id"] = str(event["_id"])
            event["id"] = str(event["_id"])
        
        category["events"] = events
        return category
    except Exception as e:
        logger.error(f"Error fetching category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=dict)
async def create_category(category: CategoryCreate):
    """Create new category"""
    try:
        from datetime import datetime
        category_dict = category.dict()
        category_dict["created_at"] = datetime.utcnow()
        category_dict["event_count"] = 0
        
        result = await db.categories.insert_one(category_dict)
        category_dict["_id"] = str(result.inserted_id)
        category_dict["id"] = str(result.inserted_id)
        
        return category_dict
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

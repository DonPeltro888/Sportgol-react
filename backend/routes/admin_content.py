from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.admin import (
    EventCreate, EventUpdate, MenuCategoryCreate, MenuCategoryUpdate,
    PageContentCreate, PageContentUpdate, SeoSettingsCreate, SeoSettingsUpdate,
    SiteSettings, TranslationCreate, TranslationUpdate, MultiLangText
)
from routes.admin_auth import verify_admin_token
from database import db
from datetime import datetime, timezone
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin-content"])

# Helper to parse date string to datetime for sorting
def parse_date_to_sortable(date_str):
    try:
        return datetime.strptime(date_str, "%B %d, %Y")
    except:
        return datetime.now()

# ================== EVENTS MANAGEMENT ==================

@router.get("/events")
async def get_all_events_admin(
    page: int = 1, 
    limit: int = 20,
    search: Optional[str] = None,
    token_data: dict = Depends(verify_admin_token)
):
    """Get all events for admin panel"""
    skip = (page - 1) * limit
    query = {}
    
    if search:
        query["$or"] = [
            {"title.it": {"$regex": search, "$options": "i"}},
            {"title.es": {"$regex": search, "$options": "i"}},
            {"title.en": {"$regex": search, "$options": "i"}},
            {"title": {"$regex": search, "$options": "i"}},  # Legacy support
            {"league": {"$regex": search, "$options": "i"}}
        ]
    
    total = await db.events.count_documents(query)
    events = await db.events.find(query).sort("sort_date", 1).skip(skip).limit(limit).to_list(limit)
    
    for event in events:
        event["_id"] = str(event["_id"])
        event["id"] = event["_id"]
    
    return {"events": events, "total": total, "page": page, "pages": (total + limit - 1) // limit}

@router.post("/events")
async def create_event_admin(event: EventCreate, token_data: dict = Depends(verify_admin_token)):
    """Create new event"""
    event_dict = event.model_dump()
    event_dict["created_at"] = datetime.now(timezone.utc)
    event_dict["updated_at"] = datetime.now(timezone.utc)
    event_dict["sort_date"] = parse_date_to_sortable(event.date)
    
    result = await db.events.insert_one(event_dict)
    event_dict["_id"] = str(result.inserted_id)
    event_dict["id"] = event_dict["_id"]
    
    # Log action
    await db.admin_logs.insert_one({
        "action": "create_event",
        "event_id": event_dict["id"],
        "username": token_data["username"],
        "timestamp": datetime.now(timezone.utc)
    })
    
    return event_dict

@router.put("/events/{event_id}")
async def update_event_admin(event_id: str, event: EventUpdate, token_data: dict = Depends(verify_admin_token)):
    """Update event"""
    update_data = {k: v for k, v in event.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    if "date" in update_data:
        update_data["sort_date"] = parse_date_to_sortable(update_data["date"])
    
    result = await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    updated_event = await db.events.find_one({"_id": ObjectId(event_id)})
    updated_event["_id"] = str(updated_event["_id"])
    updated_event["id"] = updated_event["_id"]
    
    return updated_event

@router.delete("/events/{event_id}")
async def delete_event_admin(event_id: str, token_data: dict = Depends(verify_admin_token)):
    """Delete event"""
    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await db.admin_logs.insert_one({
        "action": "delete_event",
        "event_id": event_id,
        "username": token_data["username"],
        "timestamp": datetime.now(timezone.utc)
    })
    
    return {"message": "Event deleted successfully"}

# ================== MENU CATEGORIES MANAGEMENT ==================

@router.get("/menu-categories")
async def get_menu_categories_admin(token_data: dict = Depends(verify_admin_token)):
    """Get all menu categories for admin"""
    categories = await db.menu_categories.find().sort("order", 1).to_list(100)
    
    for cat in categories:
        cat["_id"] = str(cat["_id"])
        cat["id"] = cat["_id"]
    
    return categories

@router.post("/menu-categories")
async def create_menu_category_admin(category: MenuCategoryCreate, token_data: dict = Depends(verify_admin_token)):
    """Create menu category"""
    cat_dict = category.model_dump()
    cat_dict["created_at"] = datetime.now(timezone.utc)
    
    result = await db.menu_categories.insert_one(cat_dict)
    cat_dict["_id"] = str(result.inserted_id)
    cat_dict["id"] = cat_dict["_id"]
    
    return cat_dict

@router.put("/menu-categories/{category_id}")
async def update_menu_category_admin(category_id: str, category: MenuCategoryUpdate, token_data: dict = Depends(verify_admin_token)):
    """Update menu category"""
    update_data = {k: v for k, v in category.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.menu_categories.update_one(
        {"_id": ObjectId(category_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    updated = await db.menu_categories.find_one({"_id": ObjectId(category_id)})
    updated["_id"] = str(updated["_id"])
    updated["id"] = updated["_id"]
    
    return updated

@router.delete("/menu-categories/{category_id}")
async def delete_menu_category_admin(category_id: str, token_data: dict = Depends(verify_admin_token)):
    """Delete menu category"""
    result = await db.menu_categories.delete_one({"_id": ObjectId(category_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}

# ================== PAGE CONTENT MANAGEMENT ==================

@router.get("/page-content")
async def get_all_page_content(token_data: dict = Depends(verify_admin_token)):
    """Get all page content"""
    content = await db.page_content.find().to_list(500)
    
    for item in content:
        item["_id"] = str(item["_id"])
        item["id"] = item["_id"]
    
    return content

@router.get("/page-content/{page_key}")
async def get_page_content(page_key: str, token_data: dict = Depends(verify_admin_token)):
    """Get content for specific page"""
    content = await db.page_content.find({"page_key": page_key}).to_list(100)
    
    for item in content:
        item["_id"] = str(item["_id"])
        item["id"] = item["_id"]
    
    return content

@router.post("/page-content")
async def create_page_content(content: PageContentCreate, token_data: dict = Depends(verify_admin_token)):
    """Create page content"""
    content_dict = content.model_dump()
    content_dict["created_at"] = datetime.now(timezone.utc)
    content_dict["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.page_content.insert_one(content_dict)
    content_dict["_id"] = str(result.inserted_id)
    content_dict["id"] = content_dict["_id"]
    
    return content_dict

@router.put("/page-content/{content_id}")
async def update_page_content(content_id: str, content: PageContentUpdate, token_data: dict = Depends(verify_admin_token)):
    """Update page content"""
    update_data = {k: v for k, v in content.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.page_content.update_one(
        {"_id": ObjectId(content_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Content not found")
    
    updated = await db.page_content.find_one({"_id": ObjectId(content_id)})
    updated["_id"] = str(updated["_id"])
    updated["id"] = updated["_id"]
    
    return updated

@router.delete("/page-content/{content_id}")
async def delete_page_content(content_id: str, token_data: dict = Depends(verify_admin_token)):
    """Delete page content"""
    result = await db.page_content.delete_one({"_id": ObjectId(content_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {"message": "Content deleted successfully"}

# ================== SEO SETTINGS ==================

@router.get("/seo")
async def get_all_seo_settings(token_data: dict = Depends(verify_admin_token)):
    """Get all SEO settings"""
    settings = await db.seo_settings.find().to_list(100)
    
    for item in settings:
        item["_id"] = str(item["_id"])
        item["id"] = item["_id"]
    
    return settings

@router.post("/seo")
async def create_seo_settings(seo: SeoSettingsCreate, token_data: dict = Depends(verify_admin_token)):
    """Create SEO settings for a page"""
    # Check if exists
    existing = await db.seo_settings.find_one({"page_key": seo.page_key})
    if existing:
        raise HTTPException(status_code=400, detail="SEO settings for this page already exist")
    
    seo_dict = seo.model_dump()
    seo_dict["created_at"] = datetime.now(timezone.utc)
    
    result = await db.seo_settings.insert_one(seo_dict)
    seo_dict["_id"] = str(result.inserted_id)
    seo_dict["id"] = seo_dict["_id"]
    
    return seo_dict

@router.put("/seo/{page_key}")
async def update_seo_settings(page_key: str, seo: SeoSettingsUpdate, token_data: dict = Depends(verify_admin_token)):
    """Update SEO settings"""
    update_data = {k: v for k, v in seo.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.seo_settings.update_one(
        {"page_key": page_key},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="SEO settings not found")
    
    updated = await db.seo_settings.find_one({"page_key": page_key})
    updated["_id"] = str(updated["_id"])
    updated["id"] = updated["_id"]
    
    return updated

# ================== SITE SETTINGS ==================

@router.get("/settings")
async def get_site_settings(token_data: dict = Depends(verify_admin_token)):
    """Get site settings"""
    settings = await db.site_settings.find_one({"_key": "main"})
    
    if not settings:
        # Return default settings
        return SiteSettings().model_dump()
    
    settings["_id"] = str(settings["_id"])
    return settings

@router.put("/settings")
async def update_site_settings(settings: SiteSettings, token_data: dict = Depends(verify_admin_token)):
    """Update site settings"""
    settings_dict = settings.model_dump()
    settings_dict["_key"] = "main"
    settings_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.site_settings.update_one(
        {"_key": "main"},
        {"$set": settings_dict},
        upsert=True
    )
    
    return settings_dict

# ================== TRANSLATIONS ==================

@router.get("/translations")
async def get_all_translations(
    category: Optional[str] = None,
    token_data: dict = Depends(verify_admin_token)
):
    """Get all translations"""
    query = {}
    if category:
        query["category"] = category
    
    translations = await db.translations.find(query).to_list(1000)
    
    for item in translations:
        item["_id"] = str(item["_id"])
        item["id"] = item["_id"]
    
    return translations

@router.post("/translations")
async def create_translation(translation: TranslationCreate, token_data: dict = Depends(verify_admin_token)):
    """Create translation"""
    # Check if key exists
    existing = await db.translations.find_one({"key": translation.key})
    if existing:
        raise HTTPException(status_code=400, detail="Translation key already exists")
    
    trans_dict = translation.model_dump()
    trans_dict["created_at"] = datetime.now(timezone.utc)
    
    result = await db.translations.insert_one(trans_dict)
    trans_dict["_id"] = str(result.inserted_id)
    trans_dict["id"] = trans_dict["_id"]
    
    return trans_dict

@router.put("/translations/{key}")
async def update_translation(key: str, translation: TranslationUpdate, token_data: dict = Depends(verify_admin_token)):
    """Update translation"""
    update_data = {k: v for k, v in translation.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.translations.update_one(
        {"key": key},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    updated = await db.translations.find_one({"key": key})
    updated["_id"] = str(updated["_id"])
    updated["id"] = updated["_id"]
    
    return updated

@router.delete("/translations/{key}")
async def delete_translation(key: str, token_data: dict = Depends(verify_admin_token)):
    """Delete translation"""
    result = await db.translations.delete_one({"key": key})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return {"message": "Translation deleted successfully"}

# ================== PUBLIC ENDPOINTS (No Auth) ==================

# These are for the frontend to fetch content

@router.get("/public/content/{page_key}")
async def get_public_page_content(page_key: str, lang: str = "it"):
    """Get page content for frontend (public)"""
    content = await db.page_content.find({"page_key": page_key}).to_list(100)
    
    result = {}
    for item in content:
        # Extract the correct language
        if isinstance(item.get("content"), dict):
            result[item["section_key"]] = item["content"].get(lang, item["content"].get("it", ""))
        else:
            result[item["section_key"]] = item.get("content", "")
    
    return result

@router.get("/public/seo/{page_key}")
async def get_public_seo(page_key: str, lang: str = "it"):
    """Get SEO for frontend (public)"""
    seo = await db.seo_settings.find_one({"page_key": page_key})
    
    if not seo:
        return {"title": "", "description": "", "keywords": ""}
    
    return {
        "title": seo.get("title", {}).get(lang, "") if isinstance(seo.get("title"), dict) else seo.get("title", ""),
        "description": seo.get("description", {}).get(lang, "") if isinstance(seo.get("description"), dict) else seo.get("description", ""),
        "keywords": seo.get("keywords", {}).get(lang, "") if isinstance(seo.get("keywords"), dict) else seo.get("keywords", ""),
        "og_image": seo.get("og_image", ""),
        "canonical_url": seo.get("canonical_url", "")
    }

@router.get("/public/translations")
async def get_public_translations(lang: str = "it", category: Optional[str] = None):
    """Get translations for frontend (public)"""
    query = {}
    if category:
        query["category"] = category
    
    translations = await db.translations.find(query).to_list(1000)
    
    result = {}
    for item in translations:
        result[item["key"]] = item.get(lang, item.get("it", ""))
    
    return result

@router.get("/public/menu-categories")
async def get_public_menu_categories(lang: str = "it"):
    """Get menu categories for frontend (public)"""
    categories = await db.menu_categories.find({"visible_home": True}).sort("order", 1).to_list(100)
    
    result = []
    for cat in categories:
        name = cat.get("name", {})
        result.append({
            "id": str(cat["_id"]),
            "name": name.get(lang, name.get("it", "")) if isinstance(name, dict) else name,
            "slug": cat.get("slug", ""),
            "type": cat.get("type", "league"),
            "icon": cat.get("icon", ""),
            "country": cat.get("country", ""),
            "flag": cat.get("flag", ""),
            "teams": cat.get("teams", []),
            "parent_id": cat.get("parent_id")
        })
    
    return result

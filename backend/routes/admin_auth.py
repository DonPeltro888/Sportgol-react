from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from models.admin import AdminLogin, AdminToken
from database import db
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import os

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])

# Simple admin credentials (in production, use environment variables)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "golevents2024")

# In-memory token storage (for simplicity)
active_tokens = {}

def generate_token():
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

async def verify_admin_token(authorization: Optional[str] = Header(None)):
    """Dependency to verify admin token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "")
    
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    token_data = active_tokens[token]
    if datetime.now(timezone.utc) > token_data["expires_at"]:
        del active_tokens[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    return token_data

@router.post("/login", response_model=AdminToken)
async def admin_login(login: AdminLogin):
    """Admin login endpoint"""
    if login.username != ADMIN_USERNAME or login.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    active_tokens[token] = {
        "username": login.username,
        "expires_at": expires_at
    }
    
    # Log login
    await db.admin_logs.insert_one({
        "action": "login",
        "username": login.username,
        "timestamp": datetime.now(timezone.utc),
        "ip": "N/A"
    })
    
    return AdminToken(token=token, username=login.username, expires_at=expires_at)

@router.post("/logout")
async def admin_logout(token_data: dict = Depends(verify_admin_token), authorization: str = Header(None)):
    """Admin logout endpoint"""
    token = authorization.replace("Bearer ", "")
    if token in active_tokens:
        del active_tokens[token]
    return {"message": "Logged out successfully"}

@router.get("/verify")
async def verify_token(token_data: dict = Depends(verify_admin_token)):
    """Verify if token is valid"""
    return {"valid": True, "username": token_data["username"]}

@router.get("/stats")
async def get_admin_stats(token_data: dict = Depends(verify_admin_token)):
    """Get dashboard statistics"""
    events_count = await db.events.count_documents({})
    categories_count = await db.categories.count_documents({})
    
    # Count by league
    pipeline = [
        {"$group": {"_id": "$league", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    events_by_league = await db.events.aggregate(pipeline).to_list(20)
    
    # Featured events
    featured_count = await db.events.count_documents({"featured": True})
    
    return {
        "total_events": events_count,
        "total_categories": categories_count,
        "featured_events": featured_count,
        "events_by_league": events_by_league
    }

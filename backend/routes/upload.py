from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from routes.admin_auth import verify_admin_token
from database import db
from datetime import datetime, timezone
import os
import uuid
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    token_data: dict = Depends(verify_admin_token)
):
    """Upload a file (image)"""
    
    # Validate extension
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{unique_id}{ext}"
    
    # Save file
    file_path = UPLOAD_DIR / safe_filename
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Generate URL
    file_url = f"/api/upload/files/{safe_filename}"
    
    # Save to database for tracking
    await db.media.insert_one({
        "filename": safe_filename,
        "original_name": file.filename,
        "url": file_url,
        "size": len(contents),
        "mime_type": file.content_type,
        "uploaded_by": token_data["username"],
        "uploaded_at": datetime.now(timezone.utc)
    })
    
    return {
        "success": True,
        "url": file_url,
        "filename": safe_filename,
        "size": len(contents)
    }

@router.get("/files/{filename}")
async def get_file(filename: str):
    """Serve uploaded file"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security: prevent path traversal
    if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(file_path)

@router.get("/list")
async def list_files(token_data: dict = Depends(verify_admin_token)):
    """List all uploaded files"""
    files = await db.media.find().sort("uploaded_at", -1).to_list(100)
    
    for f in files:
        f["_id"] = str(f["_id"])
        f["id"] = f["_id"]
    
    return files

@router.delete("/{filename}")
async def delete_file(filename: str, token_data: dict = Depends(verify_admin_token)):
    """Delete uploaded file"""
    file_path = UPLOAD_DIR / filename
    
    if file_path.exists():
        os.remove(file_path)
    
    await db.media.delete_one({"filename": filename})
    
    return {"success": True, "message": "File deleted"}

"""
Helper unificato per recuperare API key cifrate dal SEO Admin.
"""
from typing import Tuple
from database import db
from services.seo_crypto import decrypt


async def get_api_key(slug: str) -> str:
    """Restituisce la chiave in chiaro per un tool, o '' se non configurata/disattiva."""
    doc = await db.seo_api_keys.find_one({"slug": slug}, {"_id": 0})
    if not doc or not doc.get("active"):
        return ""
    return decrypt(doc.get("api_key_enc", ""))


async def get_login_and_key(slug: str) -> Tuple[str, str]:
    """Per provider con login+password (es. DataForSEO)."""
    doc = await db.seo_api_keys.find_one({"slug": slug}, {"_id": 0})
    if not doc or not doc.get("active"):
        return "", ""
    return doc.get("api_login", ""), decrypt(doc.get("api_key_enc", ""))

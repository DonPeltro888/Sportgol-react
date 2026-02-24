from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Category(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    label: str = "Tickets"
    slug: str
    event_count: int = 0
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class CategoryCreate(BaseModel):
    name: str
    label: str = "Tickets"
    slug: str

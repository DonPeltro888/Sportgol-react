from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)


class PriceRange(BaseModel):
    min: float
    max: float

class Event(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    title: str
    image: str
    categories: List[str]
    date: str
    location: str
    stadium: Optional[str] = None
    price_range: Optional[PriceRange] = None
    available_tickets: Optional[int] = 1000
    featured: bool = True
    league: Optional[str] = "SERIE A"
    created_at: Optional[datetime] = Field(default_factory=_utcnow)
    updated_at: Optional[datetime] = Field(default_factory=_utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class EventCreate(BaseModel):
    title: str
    image: str
    categories: List[str]
    date: str
    location: str
    stadium: Optional[str] = None
    price_range: Optional[PriceRange] = None
    available_tickets: Optional[int] = 1000
    featured: bool = True
    league: Optional[str] = "SERIE A"

class EventUpdate(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    categories: Optional[List[str]] = None
    date: Optional[str] = None
    location: Optional[str] = None
    stadium: Optional[str] = None
    price_range: Optional[PriceRange] = None
    available_tickets: Optional[int] = None
    featured: Optional[bool] = None
    league: Optional[str] = None

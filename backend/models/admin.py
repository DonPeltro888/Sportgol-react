from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Multilingual text field
class MultiLangText(BaseModel):
    it: str = ""
    es: str = ""
    en: str = ""

# Admin Authentication
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    token: str
    username: str
    expires_at: datetime

# Ticket Category for Events
class TicketCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: MultiLangText
    description: MultiLangText = Field(default_factory=MultiLangText)
    price_min: float = 0
    price_max: float = 0
    available: int = 0
    notes: MultiLangText = Field(default_factory=MultiLangText)

# Event with multilingual support
class EventCreate(BaseModel):
    title: MultiLangText
    slug: MultiLangText
    categories: List[str] = []  # Team names
    date: str
    location: MultiLangText
    stadium: str = ""
    league: str = ""
    featured: bool = False
    imageUrl: str = ""
    ticket_categories: List[TicketCategory] = []
    # SEO Meta
    seo_title: MultiLangText = Field(default_factory=MultiLangText)
    seo_description: MultiLangText = Field(default_factory=MultiLangText)
    seo_h1: MultiLangText = Field(default_factory=MultiLangText)
    # SEO Content (Details tab) - Following prompt structure
    seo_intro: MultiLangText = Field(default_factory=MultiLangText)  # 4) Intro
    seo_event_info: MultiLangText = Field(default_factory=MultiLangText)  # 5) Informazioni Evento
    seo_tickets_info: MultiLangText = Field(default_factory=MultiLangText)  # 6) Biglietti disponibili
    seo_sectors: MultiLangText = Field(default_factory=MultiLangText)  # 7) Settori consigliati
    seo_pricing: MultiLangText = Field(default_factory=MultiLangText)  # 8) Prezzi e domanda
    seo_venue: MultiLangText = Field(default_factory=MultiLangText)  # 9) Venue personalizzata
    seo_cta: MultiLangText = Field(default_factory=MultiLangText)  # 11) CTA finale
    # FAQ (10)
    faq_1_q: MultiLangText = Field(default_factory=MultiLangText)
    faq_1_a: MultiLangText = Field(default_factory=MultiLangText)
    faq_2_q: MultiLangText = Field(default_factory=MultiLangText)
    faq_2_a: MultiLangText = Field(default_factory=MultiLangText)
    faq_3_q: MultiLangText = Field(default_factory=MultiLangText)
    faq_3_a: MultiLangText = Field(default_factory=MultiLangText)

class EventUpdate(BaseModel):
    title: Optional[MultiLangText] = None
    slug: Optional[MultiLangText] = None
    categories: Optional[List[str]] = None
    date: Optional[str] = None
    location: Optional[MultiLangText] = None
    stadium: Optional[str] = None
    league: Optional[str] = None
    featured: Optional[bool] = None
    imageUrl: Optional[str] = None
    ticket_categories: Optional[List[TicketCategory]] = None
    seo_title: Optional[MultiLangText] = None
    seo_description: Optional[MultiLangText] = None
    seo_h1: Optional[MultiLangText] = None
    seo_intro: Optional[MultiLangText] = None
    seo_event_info: Optional[MultiLangText] = None
    seo_tickets_info: Optional[MultiLangText] = None
    seo_sectors: Optional[MultiLangText] = None
    seo_pricing: Optional[MultiLangText] = None
    seo_venue: Optional[MultiLangText] = None
    seo_cta: Optional[MultiLangText] = None
    faq_1_q: Optional[MultiLangText] = None
    faq_1_a: Optional[MultiLangText] = None
    faq_2_q: Optional[MultiLangText] = None
    faq_2_a: Optional[MultiLangText] = None
    faq_3_q: Optional[MultiLangText] = None
    faq_3_a: Optional[MultiLangText] = None

# Menu Category
class MenuCategoryCreate(BaseModel):
    name: MultiLangText
    slug: str
    type: str = "league"  # league, cup, other
    icon: str = ""
    country: str = ""
    flag: str = ""
    order: int = 0
    visible_home: bool = True
    parent_id: Optional[str] = None
    teams: List[str] = []

class MenuCategoryUpdate(BaseModel):
    name: Optional[MultiLangText] = None
    slug: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None
    country: Optional[str] = None
    flag: Optional[str] = None
    order: Optional[int] = None
    visible_home: Optional[bool] = None
    parent_id: Optional[str] = None
    teams: Optional[List[str]] = None

# Page Content
class PageContentCreate(BaseModel):
    page_key: str  # home, about, contact, event_detail, etc.
    section_key: str  # hero_title, hero_subtitle, faq_1, etc.
    content: MultiLangText
    content_type: str = "text"  # text, html, image

class PageContentUpdate(BaseModel):
    content: Optional[MultiLangText] = None
    content_type: Optional[str] = None

# SEO Settings
class SeoSettingsCreate(BaseModel):
    page_key: str
    title: MultiLangText
    description: MultiLangText
    keywords: MultiLangText = Field(default_factory=MultiLangText)
    og_image: str = ""
    canonical_url: str = ""

class SeoSettingsUpdate(BaseModel):
    title: Optional[MultiLangText] = None
    description: Optional[MultiLangText] = None
    keywords: Optional[MultiLangText] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None

# Site Settings
class SiteSettings(BaseModel):
    logo_url: str = ""
    site_name: MultiLangText = Field(default_factory=MultiLangText)
    site_description: MultiLangText = Field(default_factory=MultiLangText)
    contact_email: str = ""
    phone: str = ""
    address: MultiLangText = Field(default_factory=MultiLangText)
    social_facebook: str = ""
    social_instagram: str = ""
    social_twitter: str = ""
    footer_text: MultiLangText = Field(default_factory=MultiLangText)

# Translation
class TranslationCreate(BaseModel):
    key: str
    it: str = ""
    es: str = ""
    en: str = ""
    category: str = "general"  # general, menu, buttons, messages, etc.

class TranslationUpdate(BaseModel):
    it: Optional[str] = None
    es: Optional[str] = None
    en: Optional[str] = None
    category: Optional[str] = None

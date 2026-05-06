"""
Pydantic models for SEO Automation Admin.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


# ─── API Tools / Keys ───────────────────────────────────────────────────────

class ApiToolUpdateRequest(BaseModel):
    """Aggiornamento di un tool nel pannello API & Tools Settings."""
    model_config = ConfigDict(extra="ignore")

    api_key: Optional[str] = None  # Plain text dal client (cifrato lato server)
    api_login: Optional[str] = None  # Per DataForSEO (login + password)
    extra_config: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class ApiToolStatus(BaseModel):
    """Stato di un tool da mostrare nella UI (mai espone la chiave)."""
    model_config = ConfigDict(extra="ignore")

    slug: str
    name: str
    category: str  # "ai_llm" | "seo_data" | "research" | "translation" | "image" | "humanize"
    description: str
    website: str
    cost_type: str  # "free" | "paid" | "freemium"
    use_cases: List[str] = []
    active: bool = False
    has_key: bool = False
    api_key_masked: str = ""
    api_login: str = ""  # In chiaro (login email per DataForSEO)
    last_tested_at: Optional[str] = None
    last_test_status: Optional[str] = None  # "ok" | "fail"
    last_test_error: Optional[str] = None
    requires_login: bool = False
    p1_only: bool = False  # Tool placeholder per P1


# ─── SEO Page (foundation P0) ───────────────────────────────────────────────

class SeoFieldValue(BaseModel):
    """Valore di un singolo campo SEO con metadata di lock e versioning."""
    model_config = ConfigDict(extra="ignore")

    value: Any = None
    is_locked: bool = False
    generated_by_ai: bool = False
    approved: bool = False
    last_modified_by: Optional[str] = None
    last_modified_at: Optional[str] = None


class SeoPageCreate(BaseModel):
    """Creazione di una nuova pagina SEO."""
    model_config = ConfigDict(extra="ignore")

    page_type: str = "football_match"  # football_match | event | sports_event | venue | city
    language: str = "it"
    target_country: str = "IT"

    # Event fields (per match)
    event_name: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    competition: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    event_date: Optional[str] = None  # ISO
    ticket_availability: Optional[str] = "unknown"  # available|unavailable|unknown
    minimum_price: Optional[float] = None
    demand_level: Optional[str] = "medium"  # low|medium|high|very_high
    event_status: Optional[str] = "scheduled"  # scheduled|postponed|cancelled|past

    # SEO seed
    main_keyword: Optional[str] = None
    secondary_keywords: List[str] = []

    # Linkage to Golevents events DB (per auto-publish later)
    linked_event_id: Optional[str] = None
    linked_event_slug: Optional[str] = None


# ─── Audit ──────────────────────────────────────────────────────────────────

class SeoAuditIssue(BaseModel):
    severity: str  # "critical" | "warning" | "suggestion"
    category: str
    message: str
    recommendation: str = ""


class SeoAuditResult(BaseModel):
    score: int = 0
    issues: List[SeoAuditIssue] = []
    audited_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

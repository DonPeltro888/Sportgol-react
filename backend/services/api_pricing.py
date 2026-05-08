"""
API Pricing config — default + DB override.

I prezzi possono essere modificati via UI (POST /api/seo/cost-observatory/pricing)
e vengono salvati in db.api_pricing per ogni provider/op_type.

Unit semantica:
- "tokens"        → costo per 1k tokens (split input/output)
- "request"       → costo flat per chiamata
- "char"          → costo per carattere (DeepL)
- "image"         → costo per immagine generata
- "task"          → costo task DataForSEO
"""
from typing import Dict, Any, Optional
from database import db
from datetime import datetime, timezone

# Default pricing v1 (USD). Sources: provider docs as of 2026-05.
DEFAULT_PRICING: Dict[str, Dict[str, Any]] = {
    # ===== Anthropic Claude =====
    "claude:sonnet-4.5:input":     {"unit": "tokens_1k", "cost_per_unit": 0.003,  "currency": "USD",
                                     "note": "Claude Sonnet 4.5 input — $3 / 1M tokens"},
    "claude:sonnet-4.5:output":    {"unit": "tokens_1k", "cost_per_unit": 0.015,  "currency": "USD",
                                     "note": "Claude Sonnet 4.5 output — $15 / 1M tokens"},

    # ===== Google Gemini =====
    "gemini:3-pro:input":          {"unit": "tokens_1k", "cost_per_unit": 0.00125, "currency": "USD",
                                     "note": "Gemini 3 Pro input — $1.25 / 1M tokens"},
    "gemini:3-pro:output":         {"unit": "tokens_1k", "cost_per_unit": 0.005,   "currency": "USD",
                                     "note": "Gemini 3 Pro output — $5 / 1M tokens"},
    "gemini:3-pro-vision:image":   {"unit": "image",     "cost_per_unit": 0.0025,  "currency": "USD",
                                     "note": "Gemini Vision per image"},
    "gemini:nano-banana-2:image":  {"unit": "image",     "cost_per_unit": 0.04,    "currency": "USD",
                                     "note": "Nano Banana 2 1024x1024 — $0.04/img"},

    # ===== Perplexity =====
    "perplexity:sonar:request":    {"unit": "request",   "cost_per_unit": 0.005,   "currency": "USD",
                                     "note": "Perplexity Sonar base ~$5/1k req"},
    "perplexity:sonar-pro:request": {"unit": "request",  "cost_per_unit": 0.015,   "currency": "USD",
                                     "note": "Perplexity Sonar Pro ~$15/1k req"},

    # ===== DeepL =====
    "deepl:translate:char":        {"unit": "char",      "cost_per_unit": 0.000020, "currency": "USD",
                                     "note": "DeepL API Pro $20/1M char (Free=0 fino 500k/mo)"},

    # ===== DataForSEO =====
    "dataforseo:keywords:task":    {"unit": "task",      "cost_per_unit": 0.001,    "currency": "USD",
                                     "note": "DataForSEO keyword research task"},
    "dataforseo:serp:task":        {"unit": "task",      "cost_per_unit": 0.002,    "currency": "USD",
                                     "note": "DataForSEO SERP task"},

    # ===== Free providers =====
    "espn:scoreboard:request":     {"unit": "request",   "cost_per_unit": 0.0,      "currency": "USD", "note": "Free"},
    "thesportsdb:lookup:request":  {"unit": "request",   "cost_per_unit": 0.0,      "currency": "USD", "note": "Free"},
    "openfootball:fetch:request":  {"unit": "request",   "cost_per_unit": 0.0,      "currency": "USD", "note": "Free"},
    "wikimedia:logo:request":      {"unit": "request",   "cost_per_unit": 0.0,      "currency": "USD", "note": "Free"},
    "matchesio:export:request":    {"unit": "request",   "cost_per_unit": 0.0,      "currency": "USD", "note": "Free (deprecated 404)"},
    "apifootball:fetch:request":   {"unit": "request",   "cost_per_unit": 0.0,      "currency": "USD", "note": "Self-hosted free tier"},
}


async def get_pricing(provider: str, op_type: str, sub_type: Optional[str] = None) -> Dict[str, Any]:
    """Restituisce pricing per provider:op_type[:sub_type]. Cerca prima override DB poi default."""
    key = f"{provider}:{op_type}"
    if sub_type:
        key += f":{sub_type}"

    # DB override
    override = await db.api_pricing.find_one({"_id": key}, {"_id": 0})
    if override and override.get("cost_per_unit") is not None:
        return override

    # Default
    return DEFAULT_PRICING.get(key, {
        "unit": "request", "cost_per_unit": 0.0, "currency": "USD", "note": "unknown — defaulting to free",
    })


async def set_pricing(provider: str, op_type: str, sub_type: Optional[str], cost_per_unit: float,
                      unit: Optional[str] = None, note: Optional[str] = None) -> Dict[str, Any]:
    """Override pricing via UI. Salva in db.api_pricing."""
    key = f"{provider}:{op_type}"
    if sub_type:
        key += f":{sub_type}"

    default = DEFAULT_PRICING.get(key, {})
    doc = {
        "_id": key,
        "provider": provider,
        "op_type": op_type,
        "sub_type": sub_type,
        "unit": unit or default.get("unit") or "request",
        "cost_per_unit": float(cost_per_unit),
        "currency": "USD",
        "note": note or default.get("note") or "",
        "updated_at": datetime.now(timezone.utc),
    }
    await db.api_pricing.update_one({"_id": key}, {"$set": doc}, upsert=True)
    return doc


async def list_all_pricing() -> Dict[str, Any]:
    """Lista tutti i prezzi (default + override)."""
    overrides = {}
    async for d in db.api_pricing.find({}, {"_id": 1, "cost_per_unit": 1, "unit": 1, "note": 1, "updated_at": 1}):
        overrides[d["_id"]] = d

    rows = []
    for key, default in DEFAULT_PRICING.items():
        provider, op_type, *rest = key.split(":")
        sub_type = rest[0] if rest else None
        ov = overrides.get(key)
        rows.append({
            "key": key,
            "provider": provider,
            "op_type": op_type,
            "sub_type": sub_type,
            "unit": ov.get("unit") if ov else default.get("unit"),
            "cost_per_unit": ov["cost_per_unit"] if ov else default["cost_per_unit"],
            "currency": "USD",
            "note": ov.get("note") if ov and ov.get("note") else default.get("note"),
            "is_overridden": ov is not None,
            "updated_at": ov.get("updated_at").isoformat() if ov and ov.get("updated_at") else None,
        })

    return {"rows": rows, "count": len(rows)}


def compute_cost(pricing: Dict[str, Any], units_used: float) -> float:
    """cost_usd = cost_per_unit × units_used."""
    return float(pricing.get("cost_per_unit", 0.0)) * float(units_used or 0.0)

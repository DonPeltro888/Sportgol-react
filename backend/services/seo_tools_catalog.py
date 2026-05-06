"""
Catalogo dei tool API supportati nel SEO Automation Admin.
Definisce metadata + use cases + categoria. Le chiavi sono in `seo_api_keys`.
"""
from typing import List, Dict, Any

# ─── Catalogo statico ──────────────────────────────────────────────────────
TOOLS_CATALOG: List[Dict[str, Any]] = [
    # ── AI / LLM ─────────────────────────────────────────────────────────
    {
        "slug": "claude",
        "name": "Anthropic Claude",
        "category": "ai_llm",
        "description": "Claude Sonnet 4.5 — copywriting master IT (testi persuasivi, lunghi, EEAT).",
        "website": "https://console.anthropic.com",
        "cost_type": "paid",
        "use_cases": ["content_master_it", "intro", "main_content", "cta", "internal_linking_suggestions"],
        "requires_login": False,
        "p1_only": False,
    },
    {
        "slug": "gemini",
        "name": "Google Gemini 3 Pro + Nano Banana",
        "category": "ai_llm",
        "description": "Gemini 3 Pro per JSON-LD schema, meta tags strutturati, breadcrumbs. Nano Banana per banner hero (Lega/Squadra) WebP.",
        "website": "https://aistudio.google.com",
        "cost_type": "freemium",
        "use_cases": ["schema_jsonld", "meta_tags", "hreflang", "image_hero_league", "image_hero_team"],
        "requires_login": False,
        "p1_only": False,
    },
    # ── Web Research ─────────────────────────────────────────────────────
    {
        "slug": "perplexity",
        "name": "Perplexity Sonar Pro",
        "category": "research",
        "description": "Live research per FAQ 'people also ask' e news rilevanti del match. Sonar Pro model.",
        "website": "https://www.perplexity.ai/settings/api",
        "cost_type": "paid",
        "use_cases": ["faq_paa", "match_news", "trust_signals_research"],
        "requires_login": False,
        "p1_only": False,
    },
    # ── SEO Data ─────────────────────────────────────────────────────────
    {
        "slug": "dataforseo",
        "name": "DataForSEO",
        "category": "seo_data",
        "description": "Keyword volumes, SERP analysis, keyword gap, competitor research. Login email + password.",
        "website": "https://app.dataforseo.com/api-access",
        "cost_type": "paid",
        "use_cases": ["keyword_volumes", "serp_analysis", "keyword_gap", "competitor_top10"],
        "requires_login": True,
        "p1_only": False,
    },
    {
        "slug": "se_ranking",
        "name": "SE Ranking",
        "category": "seo_data",
        "description": "Ranking tracker + keyword research alternativo. Slot opzionale (già coperto da DataForSEO).",
        "website": "https://seranking.com/api.html",
        "cost_type": "paid",
        "use_cases": ["rank_tracking", "keyword_research"],
        "requires_login": False,
        "p1_only": False,
    },
    # ── Translation ──────────────────────────────────────────────────────
    {
        "slug": "deepl",
        "name": "DeepL Pro",
        "category": "translation",
        "description": "Traduzione professionale IT→EN/ES con glossario tecnico forzato (Settore Ospiti → Away Section).",
        "website": "https://www.deepl.com/pro-api",
        "cost_type": "freemium",
        "use_cases": ["translate_en", "translate_es", "glossary_management"],
        "requires_login": False,
        "p1_only": False,
    },
    # ── Humanize (opzionale) ────────────────────────────────────────────
    {
        "slug": "undetectable",
        "name": "Undetectable.ai",
        "category": "humanize",
        "description": "Humanization opzionale del testo Claude. Default DISABILITATO (Claude 4.5 è già naturale).",
        "website": "https://undetectable.ai/api",
        "cost_type": "paid",
        "use_cases": ["humanize_text"],
        "requires_login": False,
        "p1_only": False,
    },
    # ── P1 placeholders ──────────────────────────────────────────────────
    {
        "slug": "google_search_console",
        "name": "Google Search Console",
        "category": "seo_data",
        "description": "Posizionamenti reali, CTR, query indicizzate. OAuth2 (P1 placeholder).",
        "website": "https://console.cloud.google.com",
        "cost_type": "free",
        "use_cases": ["real_rankings", "indexed_queries"],
        "requires_login": False,
        "p1_only": True,
    },
    {
        "slug": "google_pagespeed",
        "name": "Google PageSpeed Insights",
        "category": "seo_data",
        "description": "Core Web Vitals + performance audit (P1 placeholder).",
        "website": "https://developers.google.com/speed/docs/insights/v5/get-started",
        "cost_type": "free",
        "use_cases": ["core_web_vitals", "perf_audit"],
        "requires_login": False,
        "p1_only": True,
    },
    {
        "slug": "google_analytics_4",
        "name": "Google Analytics 4",
        "category": "seo_data",
        "description": "Analytics traffico/comportamento utenti (P1 placeholder).",
        "website": "https://analytics.google.com",
        "cost_type": "free",
        "use_cases": ["traffic_analytics"],
        "requires_login": False,
        "p1_only": True,
    },
]


def get_tool(slug: str) -> Dict[str, Any] | None:
    for t in TOOLS_CATALOG:
        if t["slug"] == slug:
            return t
    return None

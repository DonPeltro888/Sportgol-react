"""
Dynamic Rendering endpoint per bot/crawler SEO.
Genera HTML pre-renderizzato completo per homepage, eventi, leghe, squadre.

Uso:
- GET /api/prerender/home
- GET /api/prerender/event/{id}
- GET /api/prerender/league/{slug}
- GET /api/prerender/team/{slug}

Utile per:
- Test SEO manuale (curl -A "Googlebot" <url>)
- Link preview WhatsApp/Facebook/Twitter
- Fallback noscript / CDN bot-routing in futuro
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from database import db
from datetime import datetime
import os
import json
import html as html_lib
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/api/prerender", tags=["prerender"])

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")


def _esc(text) -> str:
    """Safe HTML escape (for HTML body/attributes)."""
    if text is None:
        return ""
    return html_lib.escape(str(text), quote=True)


def _jsonld(data: dict) -> str:
    """Safely serialize a dict to JSON-LD (escapes </script to prevent XSS)."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _page_wrapper(
    title: str,
    description: str,
    canonical: str,
    og_image: str,
    body_content: str,
    structured_data: list = None,
    lang: str = "it",
) -> str:
    """Costruisce un HTML page completo SEO-ready."""
    structured_data = structured_data or []
    json_ld = "\n".join(
        f'<script type="application/ld+json">{d}</script>' for d in structured_data
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{_esc(title)}</title>
<meta name="description" content="{_esc(description)}"/>
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"/>
<link rel="canonical" href="{_esc(canonical)}"/>
<meta property="og:title" content="{_esc(title)}"/>
<meta property="og:description" content="{_esc(description)}"/>
<meta property="og:url" content="{_esc(canonical)}"/>
<meta property="og:type" content="website"/>
<meta property="og:image" content="{_esc(og_image)}"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:site_name" content="GOLEVENTS"/>
<meta property="og:locale" content="{'it_IT' if lang == 'it' else 'en_US' if lang == 'en' else 'es_ES'}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{_esc(title)}"/>
<meta name="twitter:description" content="{_esc(description)}"/>
<meta name="twitter:image" content="{_esc(og_image)}"/>
<link rel="alternate" hreflang="it" href="{BASE_URL}/"/>
<link rel="alternate" hreflang="en" href="{BASE_URL}/?lang=en"/>
<link rel="alternate" hreflang="es" href="{BASE_URL}/?lang=es"/>
{json_ld}
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif; margin: 0; padding: 0; background: #f8f9fa; color: #2D3436; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
header {{ background: #2D3436; color: white; padding: 16px 20px; }}
header h1 {{ font-size: 24px; margin: 0; }}
main h1 {{ font-size: 32px; margin-top: 20px; color: #2D3436; }}
main h2 {{ font-size: 24px; margin-top: 30px; color: #0984E3; }}
main h3 {{ font-size: 20px; margin-top: 20px; }}
ul {{ padding-left: 20px; }}
li {{ margin-bottom: 6px; }}
a {{ color: #0984E3; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.event-card {{ background: white; border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
.event-card h3 {{ margin-top: 0; color: #FF6B35; }}
.meta {{ color: #666; font-size: 14px; }}
.tag {{ display: inline-block; background: #0984E3; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; margin-right: 6px; }}
footer {{ background: #2D3436; color: #ccc; padding: 20px; text-align: center; font-size: 13px; margin-top: 40px; }}
</style>
</head>
<body>
<header>
<h1><a href="{BASE_URL}/" style="color:white;text-decoration:none">GOLEVENTS</a> - Travel Sport Fun</h1>
</header>
<main class="container">
{body_content}
</main>
<footer>
<p>&copy; {datetime.now().year} GOLEVENTS - Biglietti calcio ufficiali per Serie A, Premier League, La Liga, Champions League, World Cup 2026</p>
<p><a href="{BASE_URL}/">Home</a> | <a href="{BASE_URL}/api/sitemap.xml">Sitemap</a></p>
</footer>
</body>
</html>"""


@router.get("/home", response_class=HTMLResponse)
async def prerender_home(lang: str = "it"):
    """HTML pre-renderizzato per la homepage con lista eventi prossimi."""
    events = await db.events.find(
        {}, {"_id": 1, "slug": 1, "title": 1, "home_team": 1, "away_team": 1, "stadium": 1, "location": 1, "league": 1, "date": 1, "sort_date": 1}
    ).sort("sort_date", 1).limit(50).to_list(50)

    leagues = await db.leagues.find(
        {"active": {"$ne": False}}, {"_id": 0, "slug": 1, "name": 1, "country": 1, "type": 1}
    ).limit(50).to_list(50)

    events_count = await db.events.count_documents({})

    # Build events list HTML
    events_html = ""
    for ev in events:
        ev_slug = ev.get("slug") or str(ev.get("_id"))
        title = ev.get("title") or f"{ev.get('home_team','')} vs {ev.get('away_team','')}"
        stadium = ev.get("stadium") or ""
        location = ev.get("location") or ""
        league = ev.get("league") or ""
        date = ev.get("date") or ""
        events_html += f"""
<article class="event-card">
  <h3><a href="{BASE_URL}/biglietti-{_esc(ev_slug)}">{_esc(title)}</a></h3>
  <p class="meta">📅 {_esc(date)} · 📍 {_esc(stadium)}, {_esc(location)}</p>
  <span class="tag">{_esc(league)}</span>
</article>"""

    # Build leagues list HTML
    leagues_by_type = {"league": [], "cup": []}
    for lg in leagues:
        t = lg.get("type", "league")
        if t in leagues_by_type:
            leagues_by_type[t].append(lg)

    leagues_html = "<h2>Campionati</h2><ul>"
    for lg in leagues_by_type["league"]:
        slug = lg.get("slug")
        name = lg.get("name")
        country = lg.get("country", "")
        leagues_html += f'<li><a href="{BASE_URL}/biglietti-{_esc(slug)}">Biglietti {_esc(name)}</a> ({_esc(country)})</li>'
    leagues_html += "</ul><h2>Coppe e Tornei</h2><ul>"
    for lg in leagues_by_type["cup"]:
        slug = lg.get("slug")
        name = lg.get("name")
        leagues_html += f'<li><a href="{BASE_URL}/biglietti-{_esc(slug)}">Biglietti {_esc(name)}</a></li>'
    leagues_html += "</ul>"

    title = "GOLEVENTS - Biglietti Ufficiali Calcio | Serie A, Champions League, World Cup 2026"
    description = f"Biglietti ufficiali per {events_count}+ eventi calcistici: Serie A, Premier League, La Liga, Bundesliga, Champions League, World Cup 2026. Garanzia di autenticità, supporto WhatsApp 24/7."

    org_schema = _jsonld({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "GOLEVENTS",
        "url": f"{BASE_URL}/",
        "description": "Rivenditore biglietti calcio ufficiali",
    })
    website_schema = _jsonld({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "GOLEVENTS",
        "url": f"{BASE_URL}/",
        "inLanguage": ["it", "en", "es"],
    })

    body = f"""
<h1>Biglietti ufficiali calcio - Serie A, Premier League, Champions League</h1>
<p>Benvenuto su GOLEVENTS, il tuo punto di riferimento per biglietti calcio ufficiali. Attualmente abbiamo <strong>{events_count} eventi</strong> disponibili in catalogo.</p>

<h2>Prossimi eventi ({len(events)})</h2>
{events_html or '<p>Nessun evento al momento. Controlla più tardi.</p>'}

{leagues_html}

<h2>Perché scegliere GOLEVENTS</h2>
<ul>
<li>Biglietti 100% autentici con garanzia di ingresso</li>
<li>Assistenza WhatsApp 24/7</li>
<li>Supporto multilingua: italiano, inglese, spagnolo</li>
<li>Pagamenti sicuri e consegna veloce</li>
</ul>
"""

    return HTMLResponse(content=_page_wrapper(
        title=title,
        description=description,
        canonical=f"{BASE_URL}/",
        og_image=f"{BASE_URL}/og-image.jpg",
        body_content=body,
        structured_data=[org_schema, website_schema],
        lang=lang,
    ))


@router.get("/event/{event_id}", response_class=HTMLResponse)
async def prerender_event(event_id: str, lang: str = "it"):
    """HTML pre-renderizzato per un singolo evento. Accetta sia slug SEO ('inter-vs-parma') che ObjectId."""
    event = None
    # Try slug lookup first (more common going forward)
    if event_id and not all(c in "0123456789abcdef" for c in event_id.lower()) or "-" in event_id:
        event = await db.events.find_one(
            {"slug": event_id},
            {"_id": 1, "slug": 1, "title": 1, "home_team": 1, "away_team": 1, "stadium": 1, "location": 1, "league": 1, "date": 1, "sort_date": 1, "time": 1, "ticket_categories": 1, "categories": 1},
        )

    if not event:
        # Fallback: ObjectId
        query = None
        try:
            query = {"_id": ObjectId(event_id)}
        except (InvalidId, TypeError, ValueError):
            query = {"_id": event_id}
        event = await db.events.find_one(
            query,
            {"_id": 1, "slug": 1, "title": 1, "home_team": 1, "away_team": 1, "stadium": 1, "location": 1, "league": 1, "date": 1, "sort_date": 1, "time": 1, "ticket_categories": 1, "categories": 1},
        )

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_slug = event.get("slug") or str(event.get("_id"))

    title_raw = event.get("title") or f"{event.get('home_team','')} vs {event.get('away_team','')}"
    stadium = event.get("stadium") or ""
    location = event.get("location") or ""
    league = event.get("league") or ""
    date = event.get("date") or ""
    event_time = event.get("time") or ""
    sort_date = event.get("sort_date") or ""
    tickets = event.get("ticket_categories") or []
    cats = event.get("categories") or []

    title = f"Biglietti {title_raw} - {stadium}, {location}" if lang == "it" else f"{title_raw} Tickets - {stadium}, {location}"
    description = f"Acquista biglietti ufficiali per {title_raw} allo {stadium} di {location}. Data: {date}. Competizione: {league}. Garanzia di autenticità, supporto WhatsApp."

    # Build tickets HTML
    tickets_html = ""
    if tickets:
        tickets_html = "<h2>Settori disponibili</h2><ul>"
        for t in tickets:
            name = t.get("name") if isinstance(t.get("name"), str) else (t.get("name", {}).get("it") or "")
            tickets_html += f'<li>{_esc(name)}</li>'
        tickets_html += "</ul>"

    # Event structured data
    event_schema = _jsonld({
        "@context": "https://schema.org",
        "@type": "SportsEvent",
        "name": title_raw,
        "description": description,
        "startDate": sort_date or date,
        "location": {
            "@type": "StadiumOrArena",
            "name": stadium,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": location,
            },
        },
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "performer": [{"@type": "SportsTeam", "name": c} for c in cats[:2]],
        "organizer": {"@type": "Organization", "name": "GOLEVENTS", "url": BASE_URL},
        "url": f"{BASE_URL}/biglietti-{event_slug}",
    })

    breadcrumb_schema = _jsonld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": league, "item": f"{BASE_URL}/biglietti-{league.lower().replace(' ', '-')}" if league else f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 3, "name": title_raw},
        ],
    })

    body = f"""
<nav aria-label="breadcrumb"><a href="{BASE_URL}/">Home</a> &raquo; <a href="{BASE_URL}/biglietti-{_esc(league.lower().replace(' ', '-')) if league else ''}">{_esc(league)}</a> &raquo; {_esc(title_raw)}</nav>
<h1>{_esc(title)}</h1>
<div class="meta">
<p>🏆 Competizione: <strong>{_esc(league)}</strong></p>
<p>📅 Data: <strong>{_esc(date)}</strong> {_esc(event_time)}</p>
<p>📍 Stadio: <strong>{_esc(stadium)}</strong>, {_esc(location)}</p>
</div>
<p>{_esc(description)}</p>
{tickets_html}
<h2>Contattaci per prenotare</h2>
<p>Per acquistare biglietti per {_esc(title_raw)} o per qualsiasi informazione, contattaci via WhatsApp. Garantiamo biglietti autentici e assistenza completa.</p>
"""

    return HTMLResponse(content=_page_wrapper(
        title=title,
        description=description,
        canonical=f"{BASE_URL}/biglietti-{event_slug}",
        og_image=f"{BASE_URL}/og-event.jpg",
        body_content=body,
        structured_data=[event_schema, breadcrumb_schema],
        lang=lang,
    ))


@router.get("/league/{slug}", response_class=HTMLResponse)
async def prerender_league(slug: str, lang: str = "it"):
    """HTML pre-renderizzato per pagina lega/coppa."""
    league = await db.leagues.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1, "country": 1, "type": 1})
    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    name = league.get("name")
    country = league.get("country", "")
    league_type = league.get("type", "league")

    # Find teams for league
    teams = await db.teams.find({"league_slug": slug}, {"_id": 0, "name": 1, "slug": 1}).to_list(100)

    # Find events for this league
    events = await db.events.find(
        {"league": {"$regex": f"^{name}$", "$options": "i"}},
        {"_id": 1, "slug": 1, "title": 1, "home_team": 1, "away_team": 1, "stadium": 1, "date": 1, "sort_date": 1}
    ).sort("sort_date", 1).limit(30).to_list(30)

    title = f"Biglietti {name} - Calendario completo e prezzi ufficiali" if lang == "it" else f"{name} Tickets - Full fixtures"
    description = f"Biglietti ufficiali {name} ({country}). Calendario completo partite, settori e prezzi. Supporto WhatsApp, garanzia di autenticità."

    teams_html = ""
    if teams:
        teams_html = f"<h2>Squadre di {_esc(name)} ({len(teams)})</h2><ul>"
        for tm in teams:
            t_slug = tm.get("slug")
            t_name = tm.get("name")
            teams_html += f'<li><a href="{BASE_URL}/biglietti-{_esc(t_slug)}">Biglietti {_esc(t_name)}</a></li>'
        teams_html += "</ul>"

    events_html = ""
    if events:
        events_html = f"<h2>Prossimi eventi di {_esc(name)} ({len(events)})</h2>"
        for ev in events:
            ev_slug = ev.get("slug") or str(ev.get("_id"))
            ev_title = ev.get("title") or f"{ev.get('home_team','')} vs {ev.get('away_team','')}"
            events_html += f'<article class="event-card"><h3><a href="{BASE_URL}/biglietti-{_esc(ev_slug)}">{_esc(ev_title)}</a></h3><p class="meta">{_esc(ev.get("date",""))} · {_esc(ev.get("stadium",""))}</p></article>'

    schema_type = "SportsOrganization" if league_type == "league" else "SportsEvent"
    league_schema = _jsonld({
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": name,
        "sport": "Football",
        "url": f"{BASE_URL}/biglietti-{slug}",
    })

    body = f"""
<nav><a href="{BASE_URL}/">Home</a> &raquo; {_esc(name)}</nav>
<h1>Biglietti {_esc(name)}</h1>
<p>Calendario completo, squadre partecipanti e biglietti ufficiali per <strong>{_esc(name)}</strong> ({_esc(country)}).</p>
{teams_html}
{events_html}
"""

    return HTMLResponse(content=_page_wrapper(
        title=title,
        description=description,
        canonical=f"{BASE_URL}/biglietti-{slug}",
        og_image=f"{BASE_URL}/og-league.jpg",
        body_content=body,
        structured_data=[league_schema],
        lang=lang,
    ))


@router.get("/team/{slug}", response_class=HTMLResponse)
async def prerender_team(slug: str, lang: str = "it"):
    """HTML pre-renderizzato per pagina squadra."""
    team = await db.teams.find_one({"slug": slug}, {"_id": 0, "name": 1, "league_slug": 1, "league_name": 1})
    team_name = team.get("name") if team else slug.replace("-", " ").title()
    league_name = team.get("league_name") if team else ""

    # Find events with this team
    events = await db.events.find(
        {"$or": [
            {"home_team": {"$regex": f"^{team_name}$", "$options": "i"}},
            {"away_team": {"$regex": f"^{team_name}$", "$options": "i"}},
        ]},
        {"_id": 1, "slug": 1, "title": 1, "home_team": 1, "away_team": 1, "stadium": 1, "date": 1, "sort_date": 1, "league": 1}
    ).sort("sort_date", 1).limit(30).to_list(30)

    title = f"Biglietti {team_name} - Calendario completo casa e trasferta" if lang == "it" else f"{team_name} Tickets - Home & Away fixtures"
    description = f"Biglietti ufficiali {team_name}. Calendario completo partite casa e trasferta. Garanzia di autenticità, supporto WhatsApp 24/7."

    events_html = ""
    if events:
        events_html = f"<h2>Prossime partite di {_esc(team_name)} ({len(events)})</h2>"
        for ev in events:
            ev_slug = ev.get("slug") or str(ev.get("_id"))
            ev_title = ev.get("title") or f"{ev.get('home_team','')} vs {ev.get('away_team','')}"
            events_html += f'<article class="event-card"><h3><a href="{BASE_URL}/biglietti-{_esc(ev_slug)}">{_esc(ev_title)}</a></h3><p class="meta">{_esc(ev.get("date",""))} · {_esc(ev.get("stadium",""))} · {_esc(ev.get("league",""))}</p></article>'
    else:
        events_html = "<p>Nessuna partita programmata al momento. Contattaci via WhatsApp per richieste su partite future.</p>"

    team_schema = _jsonld({
        "@context": "https://schema.org",
        "@type": "SportsTeam",
        "name": team_name,
        "sport": "Football",
        "url": f"{BASE_URL}/biglietti-{slug}",
    })

    body = f"""
<nav><a href="{BASE_URL}/">Home</a> &raquo; {_esc(team_name)}</nav>
<h1>Biglietti {_esc(team_name)}</h1>
<p>Calendario completo di {_esc(team_name)} {_esc('in ' + league_name) if league_name else ''}. Biglietti ufficiali partite casa e trasferta.</p>
{events_html}
"""

    return HTMLResponse(content=_page_wrapper(
        title=title,
        description=description,
        canonical=f"{BASE_URL}/biglietti-{slug}",
        og_image=f"{BASE_URL}/og-team.jpg",
        body_content=body,
        structured_data=[team_schema],
        lang=lang,
    ))

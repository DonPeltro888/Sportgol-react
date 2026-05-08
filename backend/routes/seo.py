from fastapi import APIRouter
from fastapi.responses import Response
from database import db
from datetime import datetime
import os

router = APIRouter(prefix="/api", tags=["seo"])

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")

# Teams by league
TEAMS = {
    'serie-a': ['Inter', 'Milan', 'Juventus', 'Roma', 'Napoli', 'Lazio', 'Atalanta', 'Fiorentina', 'Bologna', 'Torino', 'Udinese', 'Sassuolo', 'Empoli', 'Lecce', 'Monza', 'Verona', 'Cagliari', 'Genoa', 'Parma', 'Venezia'],
    'premier-league': ['Manchester United', 'Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Tottenham', 'Newcastle United', 'West Ham', 'Brighton', 'Aston Villa', 'Crystal Palace', 'Brentford', 'Fulham', 'Wolves', 'Everton', 'Nottingham Forest', 'Bournemouth', 'Burnley'],
    'la-liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad', 'Villarreal', 'Athletic Bilbao', 'Valencia', 'Betis', 'Celta Vigo', 'Getafe', 'Osasuna', 'Mallorca', 'Girona', 'Alaves'],
    'bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Leverkusen', 'Eintracht Frankfurt', 'Union Berlin', 'Freiburg', 'Wolfsburg', 'Mainz', 'Hoffenheim', 'Werder Bremen', 'Augsburg', 'Stuttgart'],
    'ligue-1': ['PSG', 'Marseille', 'Monaco', 'Lyon', 'Lille', 'Nice', 'Rennes', 'Lens'],
    'liga-portugal': ['Porto', 'Benfica', 'Sporting CP', 'Braga'],
    'super-lig': ['Galatasaray', 'Fenerbahce', 'Besiktas', 'Trabzonspor']
}

LEAGUES = ['serie-a', 'premier-league', 'la-liga', 'bundesliga', 'ligue-1', 'liga-portugal', 'super-lig']
CUPS = ['champions-league', 'europa-league', 'coppa-italia', 'fa-cup', 'copa-del-rey', 'dfb-pokal']

@router.get("/sitemap.xml")
async def sitemap():
    """Generate multilingual sitemap.xml with hreflang tags"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    urls = []
    
    # Homepage
    urls.append(f"""
    <url>
        <loc>{BASE_URL}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>""")
    
    # Leagues & Cups - multilingual
    for slug in LEAGUES + CUPS:
        it_url = f"{BASE_URL}/biglietti-{slug}"
        en_url = f"{BASE_URL}/{slug}-tickets"
        es_url = f"{BASE_URL}/entradas-{slug}"
        
        urls.append(f"""
    <url>
        <loc>{it_url}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
        <xhtml:link rel="alternate" hreflang="it" href="{it_url}"/>
        <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>
        <xhtml:link rel="alternate" hreflang="es" href="{es_url}"/>
    </url>""")
    
    # Teams - multilingual
    for league, teams in TEAMS.items():
        for team in teams:
            team_slug = team.lower().replace(' ', '-')
            it_url = f"{BASE_URL}/biglietti-{team_slug}"
            en_url = f"{BASE_URL}/{team_slug}-tickets"
            es_url = f"{BASE_URL}/entradas-{team_slug}"
            
            urls.append(f"""
    <url>
        <loc>{it_url}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
        <xhtml:link rel="alternate" hreflang="it" href="{it_url}"/>
        <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>
        <xhtml:link rel="alternate" hreflang="es" href="{es_url}"/>
    </url>""")
    
    # Events from DB - multilingual URLs with SEO slug
    events = await db.events.find({"slug": {"$exists": True, "$ne": ""}, "_dropped_conflict": {"$ne": True}}, {"_id": 0, "slug": 1}).to_list(5000)
    for event in events:
        slug = event.get("slug")
        if not slug:
            continue
        it_url = f"{BASE_URL}/biglietti-{slug}"
        en_url = f"{BASE_URL}/{slug}-tickets"
        es_url = f"{BASE_URL}/entradas-{slug}"
        urls.append(f"""
    <url>
        <loc>{it_url}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.7</priority>
        <xhtml:link rel="alternate" hreflang="it" href="{it_url}"/>
        <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>
        <xhtml:link rel="alternate" hreflang="es" href="{es_url}"/>
    </url>""")
    
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">{''.join(urls)}
</urlset>"""
    
    return Response(content=sitemap_xml, media_type="application/xml")


@router.get("/robots.txt")
async def robots():
    """Generate robots.txt"""
    
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/api/sitemap.xml

# Crawl-delay for politeness
Crawl-delay: 1

# Disallow admin
Disallow: /admin/
"""
    
    return Response(content=robots_txt, media_type="text/plain")

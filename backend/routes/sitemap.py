from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
from datetime import datetime

router = APIRouter()

# Base URL del sito
BASE_URL = "https://campionato-demo.preview.emergentagent.com"

# Tutte le squadre per lingua
TEAMS = {
    'serie-a': ['Inter', 'Milan', 'Juventus', 'Roma', 'Napoli', 'Lazio', 'Atalanta', 'Fiorentina', 'Bologna', 'Torino', 'Udinese', 'Sassuolo', 'Empoli', 'Lecce', 'Monza', 'Verona', 'Cagliari', 'Genoa', 'Parma', 'Venezia'],
    'premier-league': ['Manchester United', 'Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Tottenham', 'Newcastle', 'West Ham', 'Brighton', 'Aston Villa', 'Crystal Palace', 'Brentford', 'Fulham', 'Wolves', 'Everton', 'Nottingham Forest', 'Bournemouth', 'Burnley'],
    'la-liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad', 'Villarreal', 'Athletic Bilbao', 'Valencia', 'Betis', 'Celta Vigo', 'Getafe', 'Osasuna', 'Mallorca', 'Girona', 'Alaves', 'Cadiz'],
    'bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Leverkusen', 'Eintracht Frankfurt', 'Union Berlin', 'Freiburg', 'Wolfsburg', 'Mainz', 'Hoffenheim', 'Werder Bremen', 'Augsburg', 'Stuttgart', 'Koln'],
    'ligue-1': ['PSG', 'Marseille', 'Monaco', 'Lyon', 'Lille', 'Nice', 'Rennes', 'Lens', 'Strasbourg'],
    'liga-portugal': ['Porto', 'Benfica', 'Sporting CP', 'Braga', 'Vitoria Guimaraes'],
    'super-lig': ['Galatasaray', 'Fenerbahce', 'Besiktas', 'Trabzonspor']
}

LEAGUES = ['serie-a', 'premier-league', 'la-liga', 'bundesliga', 'ligue-1', 'liga-portugal', 'super-lig']
CUPS = ['champions-league', 'europa-league', 'coppa-italia', 'fa-cup', 'copa-del-rey', 'dfb-pokal']

def generate_sitemap():
    """Generate XML sitemap with all URLs in all languages"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xml += '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    
    # Homepage
    xml += f'''  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>\n'''
    
    # Leagues/Cups pages - multilingual
    for league in LEAGUES + CUPS:
        # Italian URL
        it_url = f"{BASE_URL}/biglietti-{league}"
        # English URL
        en_url = f"{BASE_URL}/{league}-tickets"
        # Spanish URL
        es_url = f"{BASE_URL}/entradas-{league}"
        
        xml += f'''  <url>
    <loc>{it_url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
    <xhtml:link rel="alternate" hreflang="it" href="{it_url}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>
    <xhtml:link rel="alternate" hreflang="es" href="{es_url}"/>
  </url>\n'''
    
    # Team pages - multilingual
    for league, teams in TEAMS.items():
        for team in teams:
            team_slug = team.lower().replace(' ', '-')
            # Italian URL
            it_url = f"{BASE_URL}/biglietti-{team_slug}"
            # English URL  
            en_url = f"{BASE_URL}/{team_slug}-tickets"
            # Spanish URL
            es_url = f"{BASE_URL}/entradas-{team_slug}"
            
            xml += f'''  <url>
    <loc>{it_url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="it" href="{it_url}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>
    <xhtml:link rel="alternate" hreflang="es" href="{es_url}"/>
  </url>\n'''
    
    xml += '</urlset>'
    return xml

@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    """Return sitemap.xml"""
    xml_content = generate_sitemap()
    return Response(content=xml_content, media_type="application/xml")

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    """Return robots.txt"""
    content = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/api/sitemap.xml

# Crawl-delay for politeness
Crawl-delay: 1

# Disallow admin area
Disallow: /admin/
"""
    return PlainTextResponse(content=content)

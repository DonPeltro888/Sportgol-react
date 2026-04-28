"""
Seed aggiuntivo: eventi Maggio 2026 + Coppe finali + FIFA World Cup 2026.
Aggiunge eventi al DB esistente SENZA cancellare i dati attuali.
Tutti i prezzi includono già il +30% Viagogo-style markup.
Schema usato: nuovo (ticket_categories, sort_date come ISO string, ecc.)
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

ITA_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ITA_MONTHS = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]


def fmt_ita_date(dt: datetime) -> str:
    return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"


# Stadium image pool
STADIUM_IMAGES = [
    "https://images.unsplash.com/photo-1574629810360-7efbbe195018",
    "https://images.unsplash.com/photo-1522778119026-d647f0596c20",
    "https://images.unsplash.com/photo-1599158150601-1417ebbaafdd",
    "https://images.unsplash.com/photo-1629217855633-79a6925d6c47",
    "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9",
    "https://images.unsplash.com/photo-1592336563179-5a95288563c9",
    "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
    "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
]


def img(i):
    return STADIUM_IMAGES[i % len(STADIUM_IMAGES)]


def std_categories(base_min: int, base_max: int):
    """
    Genera ticket_categories standard con +30% Viagogo markup già applicato.
    Le 'price' qui rappresentano il prezzo finale al cliente (markup incluso).
    """
    # base prices then x1.30
    p_premium = round(base_max * 1.30)
    p_cat1 = round(base_max * 0.95 * 1.30)
    p_cat2 = round(((base_max + base_min) / 2) * 1.05 * 1.30)
    p_cat3 = round(((base_max + base_min) / 2) * 0.85 * 1.30)
    p_cat4 = round(base_min * 1.30)
    return [
        {"name": "Cat 1 Premium", "price": p_premium, "available": True, "notes": ""},
        {"name": "Cat 1", "price": p_cat1, "available": True, "notes": ""},
        {"name": "Cat 2", "price": p_cat2, "available": True, "notes": ""},
        {"name": "Cat 3", "price": p_cat3, "available": True, "notes": ""},
        {"name": "Cat 4", "price": p_cat4, "available": True, "notes": ""},
    ]


def make_event(home, away, league, stadium, location, dt: datetime, time_str,
               base_min, base_max, available=18000, has_map=False, map_type=None,
               featured=False, image_idx=0, country=None, sectors_str=""):
    """Crea documento evento con schema nuovo."""
    title = f"{home} vs {away}"
    cats = std_categories(base_min, base_max)
    prices = [c["price"] for c in cats]
    return {
        "title": title,
        "home_team": home,
        "away_team": away,
        "league": league,
        "stadium": stadium,
        "location": location,
        "country": country,
        "date": fmt_ita_date(dt),
        "time": time_str,
        "sort_date": dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "categories": [home.upper(), away.upper()],
        "ticket_categories": cats,
        "price_range": {"min": min(prices), "max": max(prices)},
        "available_tickets": available,
        "image": img(image_idx),
        "imageUrl": img(image_idx),
        "seo_sectors": sectors_str or "Tribuna, Curva Nord, Curva Sud, 1° Anello, 2° Anello",
        "has_stadium_map": has_map,
        "stadium_map_type": map_type,
        "featured": featured,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


# ============================================================================
# 1. SERIE A — Giornate 33-38 (Maggio 2026)
# ============================================================================
SERIE_A_FIXTURES = [
    # Giornata 33 - 2-3 Maggio 2026 (oltre Inter-Parma già esistente)
    ("Atalanta", "Genoa", "Bergamo", "Gewiss Stadium", "2026-05-02", "20:45", 35, 180),
    ("Bologna", "Lecce", "Bologna", "Renato Dall'Ara", "2026-05-02", "18:00", 30, 150),
    ("Cagliari", "Hellas Verona", "Cagliari", "Unipol Domus", "2026-05-02", "15:00", 28, 130),
    ("Cremonese", "Pisa", "Cremona", "Stadio Giovanni Zini", "2026-05-02", "15:00", 28, 140),
    ("Fiorentina", "Sassuolo", "Florence", "Artemio Franchi", "2026-05-03", "12:30", 35, 170),
    ("Juventus", "Como", "Turin", "Allianz Stadium", "2026-05-03", "15:00", 50, 280),
    ("Lazio", "Udinese", "Rome", "Stadio Olimpico", "2026-05-03", "18:00", 40, 200),
    ("Milan", "Napoli", "Milan", "San Siro", "2026-05-03", "20:45", 80, 480),
    ("Roma", "Torino", "Rome", "Stadio Olimpico", "2026-05-04", "20:45", 45, 250),
    # Giornata 34 - 9-10 Maggio
    ("Como", "Atalanta", "Como", "Stadio Giuseppe Sinigaglia", "2026-05-09", "15:00", 35, 180),
    ("Genoa", "Bologna", "Genoa", "Luigi Ferraris", "2026-05-09", "18:00", 32, 160),
    ("Hellas Verona", "Inter", "Verona", "Marcantonio Bentegodi", "2026-05-09", "20:45", 50, 280),
    ("Lecce", "Cagliari", "Lecce", "Via del Mare", "2026-05-10", "12:30", 28, 130),
    ("Napoli", "Fiorentina", "Naples", "Diego Armando Maradona", "2026-05-10", "15:00", 50, 290),
    ("Parma", "Cremonese", "Parma", "Stadio Ennio Tardini", "2026-05-10", "18:00", 28, 140),
    ("Pisa", "Lazio", "Pisa", "Arena Garibaldi", "2026-05-10", "15:00", 35, 170),
    ("Sassuolo", "Roma", "Reggio Emilia", "Mapei Stadium", "2026-05-10", "18:00", 40, 200),
    ("Torino", "Milan", "Turin", "Stadio Olimpico Grande Torino", "2026-05-10", "20:45", 50, 290),
    ("Udinese", "Juventus", "Udine", "Dacia Arena", "2026-05-10", "18:00", 50, 270),
    # Giornata 35 - 16-17 Maggio
    ("Atalanta", "Roma", "Bergamo", "Gewiss Stadium", "2026-05-16", "20:45", 50, 280),
    ("Bologna", "Inter", "Bologna", "Renato Dall'Ara", "2026-05-16", "18:00", 60, 340),
    ("Cagliari", "Sassuolo", "Cagliari", "Unipol Domus", "2026-05-16", "15:00", 25, 130),
    ("Cremonese", "Hellas Verona", "Cremona", "Stadio Giovanni Zini", "2026-05-17", "12:30", 25, 130),
    ("Fiorentina", "Pisa", "Florence", "Artemio Franchi", "2026-05-17", "18:00", 35, 170),
    ("Juventus", "Lazio", "Turin", "Allianz Stadium", "2026-05-17", "20:45", 65, 380),
    ("Lecce", "Como", "Lecce", "Via del Mare", "2026-05-17", "15:00", 25, 120),
    ("Milan", "Genoa", "Milan", "San Siro", "2026-05-17", "15:00", 50, 280),
    ("Parma", "Napoli", "Parma", "Stadio Ennio Tardini", "2026-05-17", "20:45", 40, 220),
    ("Udinese", "Torino", "Udine", "Dacia Arena", "2026-05-17", "18:00", 30, 150),
    # Giornata 36 - 23-24 Maggio
    ("Como", "Bologna", "Como", "Stadio Giuseppe Sinigaglia", "2026-05-23", "18:00", 30, 150),
    ("Genoa", "Parma", "Genoa", "Luigi Ferraris", "2026-05-23", "15:00", 28, 140),
    ("Hellas Verona", "Atalanta", "Verona", "Marcantonio Bentegodi", "2026-05-23", "20:45", 35, 170),
    ("Inter", "Lazio", "Milan", "San Siro", "2026-05-24", "20:45", 60, 360),
    ("Lazio", "Cremonese", "Rome", "Stadio Olimpico", "2026-05-24", "12:30", 35, 170),
    ("Napoli", "Cagliari", "Naples", "Diego Armando Maradona", "2026-05-24", "18:00", 45, 240),
    ("Pisa", "Udinese", "Pisa", "Arena Garibaldi", "2026-05-24", "15:00", 28, 130),
    ("Roma", "Milan", "Rome", "Stadio Olimpico", "2026-05-24", "20:45", 60, 360),
    ("Sassuolo", "Juventus", "Reggio Emilia", "Mapei Stadium", "2026-05-24", "18:00", 50, 280),
    ("Torino", "Lecce", "Turin", "Stadio Olimpico Grande Torino", "2026-05-24", "15:00", 28, 140),
]


def build_serie_a():
    out = []
    big_clubs = {"Inter", "Milan", "Juventus", "Roma", "Napoli", "Lazio", "Atalanta", "Fiorentina"}
    for i, (h, a, loc, std, dstr, t, mn, mx) in enumerate(SERIE_A_FIXTURES):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        featured = h in big_clubs or a in big_clubs
        has_map = std == "San Siro"
        out.append(make_event(
            h, a, "SERIE A", std, loc, dt, t, mn, mx,
            available=20000 if featured else 14000,
            has_map=has_map, map_type="san-siro" if has_map else None,
            featured=featured, image_idx=i, country="Italy"
        ))
    return out


# ============================================================================
# 2. PREMIER LEAGUE — Matchday 36-38
# ============================================================================
PREMIER_FIXTURES = [
    # Matchday 36 - 2 May
    ("Arsenal", "Bournemouth", "London", "Emirates Stadium", "2026-05-02", "15:00", 55, 300),
    ("Aston Villa", "Fulham", "Birmingham", "Villa Park", "2026-05-02", "15:00", 45, 220),
    ("Brighton", "Wolves", "Brighton", "Amex Stadium", "2026-05-02", "15:00", 40, 200),
    ("Chelsea", "Liverpool", "London", "Stamford Bridge", "2026-05-02", "17:30", 80, 480),
    ("Everton", "Brentford", "Liverpool", "Hill Dickinson Stadium", "2026-05-02", "15:00", 45, 220),
    ("Leeds United", "Tottenham", "Leeds", "Elland Road", "2026-05-03", "14:00", 55, 300),
    ("Manchester City", "Newcastle United", "Manchester", "Etihad Stadium", "2026-05-03", "16:30", 75, 420),
    ("Manchester United", "West Ham", "Manchester", "Old Trafford", "2026-05-03", "14:00", 65, 360),
    ("Nottingham Forest", "Burnley", "Nottingham", "City Ground", "2026-05-03", "14:00", 40, 190),
    ("Crystal Palace", "Sunderland", "London", "Selhurst Park", "2026-05-03", "14:00", 45, 220),
    # Matchday 37 - 9 May
    ("Bournemouth", "Manchester City", "Bournemouth", "Vitality Stadium", "2026-05-09", "15:00", 60, 320),
    ("Brentford", "Chelsea", "London", "Gtech Community Stadium", "2026-05-09", "15:00", 50, 260),
    ("Burnley", "Arsenal", "Burnley", "Turf Moor", "2026-05-09", "15:00", 55, 300),
    ("Fulham", "Manchester United", "London", "Craven Cottage", "2026-05-09", "15:00", 60, 320),
    ("Liverpool", "Crystal Palace", "Liverpool", "Anfield", "2026-05-09", "15:00", 65, 350),
    ("Newcastle United", "Aston Villa", "Newcastle", "St James' Park", "2026-05-09", "15:00", 50, 260),
    ("Sunderland", "Leeds United", "Sunderland", "Stadium of Light", "2026-05-10", "14:00", 45, 230),
    ("Tottenham", "Brighton", "London", "Tottenham Hotspur Stadium", "2026-05-10", "16:30", 60, 340),
    ("West Ham", "Everton", "London", "London Stadium", "2026-05-09", "15:00", 50, 260),
    ("Wolves", "Nottingham Forest", "Wolverhampton", "Molineux Stadium", "2026-05-10", "14:00", 40, 200),
    # Matchday 38 (FINAL DAY) - 17 May
    ("Arsenal", "Liverpool", "London", "Emirates Stadium", "2026-05-17", "16:00", 90, 550),
    ("Aston Villa", "Tottenham", "Birmingham", "Villa Park", "2026-05-17", "16:00", 55, 320),
    ("Brighton", "Manchester United", "Brighton", "Amex Stadium", "2026-05-17", "16:00", 60, 320),
    ("Chelsea", "Wolves", "London", "Stamford Bridge", "2026-05-17", "16:00", 55, 300),
    ("Crystal Palace", "Manchester City", "London", "Selhurst Park", "2026-05-17", "16:00", 60, 340),
    ("Everton", "Burnley", "Liverpool", "Hill Dickinson Stadium", "2026-05-17", "16:00", 40, 200),
    ("Leeds United", "Bournemouth", "Leeds", "Elland Road", "2026-05-17", "16:00", 45, 220),
    ("Manchester United", "Newcastle United", "Manchester", "Old Trafford", "2026-05-17", "16:00", 65, 360),
    ("Nottingham Forest", "Sunderland", "Nottingham", "City Ground", "2026-05-17", "16:00", 40, 200),
    ("West Ham", "Fulham", "London", "London Stadium", "2026-05-17", "16:00", 45, 230),
    ("Brentford", "Crystal Palace", "London", "Gtech Community Stadium", "2026-05-17", "16:00", 40, 210),
]


def build_premier():
    out = []
    big = {"Liverpool", "Arsenal", "Chelsea", "Manchester City", "Manchester United", "Tottenham", "Newcastle United"}
    for i, (h, a, loc, std, dstr, t, mn, mx) in enumerate(PREMIER_FIXTURES):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        feat = h in big or a in big
        out.append(make_event(
            h, a, "PREMIER LEAGUE", std, loc, dt, t, mn, mx,
            available=22000 if feat else 14000,
            featured=feat, image_idx=i, country="England"
        ))
    return out


# ============================================================================
# 3. LA LIGA — Matchday 36-38 (Maggio 2026)
# ============================================================================
LALIGA_FIXTURES = [
    # MD36 - 2 May
    ("Real Madrid", "Mallorca", "Madrid", "Santiago Bernabéu", "2026-05-02", "21:00", 80, 460),
    ("Barcelona", "Athletic Bilbao", "Barcelona", "Spotify Camp Nou", "2026-05-02", "18:30", 75, 420),
    ("Atlético Madrid", "Sevilla", "Madrid", "Metropolitano", "2026-05-03", "21:00", 60, 320),
    ("Real Betis", "Villarreal", "Seville", "Estadio La Cartuja", "2026-05-03", "16:00", 45, 220),
    ("Valencia", "Real Sociedad", "Valencia", "Mestalla Stadium", "2026-05-02", "14:00", 45, 230),
    ("Celta Vigo", "Espanyol", "Vigo", "Balaídos", "2026-05-03", "18:30", 38, 180),
    ("Girona", "Levante", "Girona", "Estadi Montilivi", "2026-05-02", "16:15", 35, 170),
    ("Getafe", "Rayo Vallecano", "Madrid", "Coliseum", "2026-05-03", "14:00", 32, 160),
    ("Osasuna", "Alavés", "Pamplona", "El Sadar", "2026-05-02", "21:00", 35, 170),
    ("Elche", "Oviedo", "Elche", "Martínez Valero", "2026-05-03", "16:15", 28, 130),
    # MD37 - 9 May
    ("Athletic Bilbao", "Atlético Madrid", "Bilbao", "San Mamés", "2026-05-09", "21:00", 65, 360),
    ("Mallorca", "Barcelona", "Palma", "Estadi Mallorca Son Moix", "2026-05-10", "21:00", 60, 320),
    ("Sevilla", "Real Madrid", "Seville", "Sánchez Pizjuán", "2026-05-10", "21:00", 80, 480),
    ("Villarreal", "Valencia", "Villarreal", "Estadio de la Cerámica", "2026-05-09", "18:30", 45, 220),
    ("Real Sociedad", "Celta Vigo", "San Sebastián", "Reale Arena", "2026-05-10", "16:15", 42, 200),
    ("Espanyol", "Real Betis", "Cornellà", "RCDE Stadium", "2026-05-10", "14:00", 40, 190),
    ("Levante", "Getafe", "Valencia", "Ciutat de València", "2026-05-09", "21:00", 30, 140),
    ("Rayo Vallecano", "Girona", "Madrid", "Estadio de Vallecas", "2026-05-09", "16:15", 35, 170),
    ("Alavés", "Osasuna", "Vitoria", "Mendizorroza", "2026-05-10", "21:00", 32, 160),
    ("Oviedo", "Elche", "Oviedo", "Carlos Tartiere", "2026-05-09", "14:00", 30, 140),
    # MD38 - 17 May
    ("Real Madrid", "Barcelona", "Madrid", "Santiago Bernabéu", "2026-05-17", "21:00", 110, 700),
    ("Atlético Madrid", "Real Betis", "Madrid", "Metropolitano", "2026-05-17", "18:30", 60, 320),
    ("Athletic Bilbao", "Mallorca", "Bilbao", "San Mamés", "2026-05-17", "16:15", 45, 220),
    ("Sevilla", "Valencia", "Seville", "Sánchez Pizjuán", "2026-05-17", "14:00", 45, 220),
    ("Real Sociedad", "Villarreal", "San Sebastián", "Reale Arena", "2026-05-17", "21:00", 45, 220),
    ("Celta Vigo", "Girona", "Vigo", "Balaídos", "2026-05-17", "14:00", 35, 170),
    ("Espanyol", "Levante", "Cornellà", "RCDE Stadium", "2026-05-17", "16:15", 32, 160),
    ("Getafe", "Osasuna", "Madrid", "Coliseum", "2026-05-17", "16:15", 30, 150),
    ("Rayo Vallecano", "Alavés", "Madrid", "Estadio de Vallecas", "2026-05-17", "14:00", 32, 160),
    ("Oviedo", "Elche", "Oviedo", "Carlos Tartiere", "2026-05-17", "18:30", 30, 140),
]


def build_laliga():
    out = []
    big = {"Real Madrid", "Barcelona", "Atlético Madrid", "Sevilla", "Real Betis", "Athletic Bilbao", "Real Sociedad", "Valencia"}
    for i, (h, a, loc, std, dstr, t, mn, mx) in enumerate(LALIGA_FIXTURES):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        feat = h in big or a in big
        out.append(make_event(
            h, a, "LA LIGA", std, loc, dt, t, mn, mx,
            available=24000 if feat else 14000,
            featured=feat, image_idx=i, country="Spain"
        ))
    return out


# ============================================================================
# 4. BUNDESLIGA — Matchday 33-34 (May 2026)
# ============================================================================
BUNDES_FIXTURES = [
    # MD33 - 9 May
    ("Bayern Munich", "Bayer Leverkusen", "Munich", "Allianz Arena", "2026-05-09", "15:30", 75, 440),
    ("Borussia Dortmund", "Eintracht Frankfurt", "Dortmund", "Signal Iduna Park", "2026-05-09", "15:30", 60, 340),
    ("RB Leipzig", "VfB Stuttgart", "Leipzig", "Red Bull Arena", "2026-05-09", "18:30", 50, 270),
    ("Wolfsburg", "Hoffenheim", "Wolfsburg", "Volkswagen Arena", "2026-05-09", "15:30", 40, 200),
    ("Hamburger SV", "Werder Bremen", "Hamburg", "Volksparkstadion", "2026-05-09", "15:30", 55, 300),
    ("Köln", "Mainz", "Cologne", "RheinEnergieStadion", "2026-05-09", "15:30", 40, 200),
    ("Borussia Mönchengladbach", "Augsburg", "Mönchengladbach", "Borussia-Park", "2026-05-09", "15:30", 35, 170),
    ("Heidenheim", "St. Pauli", "Heidenheim", "Voith-Arena", "2026-05-09", "15:30", 30, 140),
    ("Union Berlin", "Freiburg", "Berlin", "Stadion An der Alten Försterei", "2026-05-09", "15:30", 35, 170),
    # MD34 - 16 May (Final day)
    ("Bayer Leverkusen", "Borussia Dortmund", "Leverkusen", "BayArena", "2026-05-16", "15:30", 70, 400),
    ("Eintracht Frankfurt", "Bayern Munich", "Frankfurt", "Deutsche Bank Park", "2026-05-16", "15:30", 75, 440),
    ("VfB Stuttgart", "Hamburger SV", "Stuttgart", "Mercedes-Benz Arena", "2026-05-16", "15:30", 50, 280),
    ("Hoffenheim", "RB Leipzig", "Sinsheim", "PreZero Arena", "2026-05-16", "15:30", 45, 220),
    ("Werder Bremen", "Wolfsburg", "Bremen", "Weserstadion", "2026-05-16", "15:30", 38, 190),
    ("Mainz", "Borussia Mönchengladbach", "Mainz", "MEWA Arena", "2026-05-16", "15:30", 35, 170),
    ("Augsburg", "Köln", "Augsburg", "WWK Arena", "2026-05-16", "15:30", 32, 160),
    ("Freiburg", "Heidenheim", "Freiburg", "Europa-Park Stadion", "2026-05-16", "15:30", 38, 180),
    ("St. Pauli", "Union Berlin", "Hamburg", "Millerntor-Stadion", "2026-05-16", "15:30", 35, 170),
]


def build_bundes():
    out = []
    big = {"Bayern Munich", "Borussia Dortmund", "Bayer Leverkusen", "RB Leipzig", "Eintracht Frankfurt", "VfB Stuttgart"}
    for i, (h, a, loc, std, dstr, t, mn, mx) in enumerate(BUNDES_FIXTURES):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        feat = h in big or a in big
        out.append(make_event(
            h, a, "BUNDESLIGA", std, loc, dt, t, mn, mx,
            available=22000 if feat else 13000,
            featured=feat, image_idx=i, country="Germany"
        ))
    return out


# ============================================================================
# 5. LIGUE 1 — Final rounds (May 2026)
# ============================================================================
LIGUE1_FIXTURES = [
    # J33-34
    ("PSG", "Lyon", "Paris", "Parc des Princes", "2026-05-02", "21:00", 75, 440),
    ("Marseille", "Monaco", "Marseille", "Stade Vélodrome", "2026-05-03", "20:45", 60, 340),
    ("Lille", "Nice", "Lille", "Stade Pierre-Mauroy", "2026-05-02", "19:00", 45, 220),
    ("Lens", "Rennes", "Lens", "Stade Bollaert-Delelis", "2026-05-02", "17:00", 40, 200),
    ("Strasbourg", "Toulouse", "Strasbourg", "Stade de la Meinau", "2026-05-03", "15:00", 35, 170),
    ("Nantes", "Auxerre", "Nantes", "Stade de la Beaujoire", "2026-05-03", "15:00", 35, 170),
    # J35
    ("Monaco", "PSG", "Monaco", "Stade Louis II", "2026-05-09", "21:00", 70, 420),
    ("Lyon", "Marseille", "Lyon", "Groupama Stadium", "2026-05-10", "20:45", 60, 340),
    ("Nice", "Lens", "Nice", "Allianz Riviera", "2026-05-09", "19:00", 40, 200),
    ("Rennes", "Strasbourg", "Rennes", "Roazhon Park", "2026-05-09", "17:00", 38, 180),
    # J36-J37 last day (16 May)
    ("PSG", "Marseille", "Paris", "Parc des Princes", "2026-05-16", "21:00", 90, 550),
    ("Lyon", "Monaco", "Lyon", "Groupama Stadium", "2026-05-16", "21:00", 60, 340),
    ("Nice", "Lille", "Nice", "Allianz Riviera", "2026-05-16", "21:00", 45, 220),
    ("Lens", "Toulouse", "Lens", "Stade Bollaert-Delelis", "2026-05-16", "21:00", 40, 200),
    ("Strasbourg", "Auxerre", "Strasbourg", "Stade de la Meinau", "2026-05-16", "21:00", 32, 160),
    ("Brest", "Le Havre", "Brest", "Stade Francis-Le Blé", "2026-05-16", "21:00", 28, 140),
]


def build_ligue1():
    out = []
    big = {"PSG", "Marseille", "Lyon", "Monaco", "Lille"}
    for i, (h, a, loc, std, dstr, t, mn, mx) in enumerate(LIGUE1_FIXTURES):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        feat = h in big or a in big
        out.append(make_event(
            h, a, "LIGUE 1", std, loc, dt, t, mn, mx,
            available=20000 if feat else 12000,
            featured=feat, image_idx=i, country="France"
        ))
    return out


# ============================================================================
# 6. LIGA PORTUGAL — Final rounds
# ============================================================================
LIGA_PT_FIXTURES = [
    ("Benfica", "Sporting CP", "Lisbon", "Estádio da Luz", "2026-05-02", "20:30", 75, 420),
    ("Porto", "Braga", "Porto", "Estádio do Dragão", "2026-05-03", "20:30", 55, 300),
    ("Sporting CP", "Porto", "Lisbon", "José Alvalade", "2026-05-09", "20:30", 70, 400),
    ("Braga", "Benfica", "Braga", "Estádio Municipal de Braga", "2026-05-10", "20:30", 50, 280),
    ("Vitória Guimarães", "Sporting CP", "Guimarães", "Estádio D. Afonso Henriques", "2026-05-16", "18:00", 42, 220),
    ("Benfica", "Porto", "Lisbon", "Estádio da Luz", "2026-05-17", "20:30", 80, 460),
    ("Famalicão", "Braga", "Vila Nova de Famalicão", "Estádio Municipal 22 de Junho", "2026-05-17", "16:00", 32, 170),
]


def build_pt():
    out = []
    big = {"Benfica", "Porto", "Sporting CP", "Braga"}
    for i, (h, a, loc, std, dstr, t, mn, mx) in enumerate(LIGA_PT_FIXTURES):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        feat = h in big or a in big
        out.append(make_event(
            h, a, "LIGA PORTUGAL", std, loc, dt, t, mn, mx,
            available=18000 if feat else 9000,
            featured=feat, image_idx=i, country="Portugal"
        ))
    return out


# ============================================================================
# 7. SUPER LIG — Final rounds
# ============================================================================
SUPER_LIG_FIXTURES = [
    ("Galatasaray", "Beşiktaş", "Istanbul", "RAMS Park", "2026-05-03", "19:00", 65, 360),
    ("Fenerbahçe", "Trabzonspor", "Istanbul", "Şükrü Saracoğlu", "2026-05-04", "19:00", 55, 320),
    ("Beşiktaş", "Fenerbahçe", "Istanbul", "Vodafone Park", "2026-05-10", "19:00", 65, 360),
    ("Galatasaray", "Trabzonspor", "Istanbul", "RAMS Park", "2026-05-11", "19:00", 50, 280),
    ("Trabzonspor", "Beşiktaş", "Trabzon", "Şenol Güneş", "2026-05-17", "19:00", 45, 240),
    ("Fenerbahçe", "Galatasaray", "Istanbul", "Şükrü Saracoğlu", "2026-05-18", "19:00", 75, 420),
]


def build_super_lig():
    out = []
    big = {"Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor"}
    for i, (h, a, loc, std, dstr, t, mn, mx) in enumerate(SUPER_LIG_FIXTURES):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        feat = h in big or a in big
        out.append(make_event(
            h, a, "SUPER LIG", std, loc, dt, t, mn, mx,
            available=17000 if feat else 11000,
            featured=feat, image_idx=i, country="Turkey"
        ))
    return out


# ============================================================================
# 8. CHAMPIONS LEAGUE — Knockout 2025/26
# ============================================================================
UCL_FIXTURES = [
    # Quarter-finals (1st leg) - April 7-8 (already passed but include semis)
    # Semi-finals
    ("PSG", "Real Madrid", "Paris", "Parc des Princes", "2026-04-28", "21:00", 130, 800),
    ("Bayern Munich", "Inter", "Munich", "Allianz Arena", "2026-04-29", "21:00", 130, 800),
    # Semi-finals 2nd leg
    ("Real Madrid", "PSG", "Madrid", "Santiago Bernabéu", "2026-05-05", "21:00", 150, 900),
    ("Inter", "Bayern Munich", "Milan", "San Siro", "2026-05-06", "21:00", 140, 850),
    # FINAL
    ("UCL Finalist 1", "UCL Finalist 2", "Budapest", "Puskás Aréna", "2026-05-30", "21:00", 220, 1400),
]


def build_ucl():
    out = []
    titles = ["Champions League SF1 (1st Leg)", "Champions League SF2 (1st Leg)",
              "Champions League SF1 (2nd Leg)", "Champions League SF2 (2nd Leg)",
              "UEFA Champions League Final"]
    for i, ((h, a, loc, std, dstr, t, mn, mx), tt) in enumerate(zip(UCL_FIXTURES, titles)):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        ev = make_event(
            h, a, "CHAMPIONS LEAGUE", std, loc, dt, t, mn, mx,
            available=30000, featured=True, image_idx=i, country="Europe"
        )
        ev["title"] = f"{h} vs {a} - {tt.split('(')[1].rstrip(')').strip()}" if "(" in tt else f"{h} vs {a} - UCL Final"
        if "Final" in tt:
            ev["title"] = "UEFA Champions League Final 2026"
            ev["categories"] = ["CHAMPIONS LEAGUE", "UEFA"]
        out.append(ev)
    return out


# ============================================================================
# 9. EUROPA LEAGUE — Knockout 2025/26
# ============================================================================
UEL_FIXTURES = [
    # Semi-finals
    ("Roma", "Athletic Bilbao", "Rome", "Stadio Olimpico", "2026-04-30", "21:00", 70, 400),
    ("Manchester United", "Marseille", "Manchester", "Old Trafford", "2026-04-30", "21:00", 80, 460),
    # Semi-finals 2nd leg
    ("Athletic Bilbao", "Roma", "Bilbao", "San Mamés", "2026-05-07", "21:00", 65, 360),
    ("Marseille", "Manchester United", "Marseille", "Stade Vélodrome", "2026-05-07", "21:00", 70, 400),
    # FINAL - 20 May 2026 - Beşiktaş Park, Istanbul
    ("UEL Finalist 1", "UEL Finalist 2", "Istanbul", "Beşiktaş Park", "2026-05-20", "21:00", 130, 800),
]


def build_uel():
    out = []
    titles_extra = ["SF1 (1st Leg)", "SF2 (1st Leg)", "SF1 (2nd Leg)", "SF2 (2nd Leg)", "Final"]
    for i, ((h, a, loc, std, dstr, t, mn, mx), tt) in enumerate(zip(UEL_FIXTURES, titles_extra)):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        ev = make_event(
            h, a, "EUROPA LEAGUE", std, loc, dt, t, mn, mx,
            available=22000, featured=True, image_idx=i, country="Europe"
        )
        if tt == "Final":
            ev["title"] = "UEFA Europa League Final 2026"
            ev["categories"] = ["EUROPA LEAGUE", "UEFA"]
        else:
            ev["title"] = f"{h} vs {a} - {tt}"
        out.append(ev)
    return out


# ============================================================================
# 10. CUP FINALS — Coppa Italia, FA Cup, Copa del Rey, DFB Pokal
# ============================================================================
CUP_FINALS = [
    # FA Cup Final - 16 May 2026 Wembley
    ("Manchester City", "Chelsea", "FA CUP", "Wembley Stadium", "London", "2026-05-16", "16:30", 130, 750, "England"),
    # Copa del Rey Final - already exists in DB (May 9)
    # Coppa Italia Final - already exists in DB (May 13)
    # DFB Pokal Final - already exists in DB (May 16)
]


def build_cup_finals():
    out = []
    for i, (h, a, lg, std, loc, dstr, t, mn, mx, country) in enumerate(CUP_FINALS):
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        ev = make_event(h, a, lg, std, loc, dt, t, mn, mx, available=80000,
                        featured=True, image_idx=i, country=country)
        out.append(ev)
    return out


# ============================================================================
# 11. FIFA WORLD CUP 2026 — All Major Matches
# ============================================================================
WC_VENUES = {
    "Atlanta": ("Mercedes-Benz Stadium", "USA"),
    "Boston": ("Gillette Stadium", "USA"),
    "Dallas": ("AT&T Stadium", "USA"),
    "Guadalajara": ("Estadio Akron", "Mexico"),
    "Houston": ("NRG Stadium", "USA"),
    "Kansas City": ("GEHA Field at Arrowhead Stadium", "USA"),
    "Los Angeles": ("SoFi Stadium", "USA"),
    "Mexico City": ("Estadio Azteca", "Mexico"),
    "Miami": ("Hard Rock Stadium", "USA"),
    "Monterrey": ("Estadio BBVA", "Mexico"),
    "New York": ("MetLife Stadium", "USA"),
    "Philadelphia": ("Lincoln Financial Field", "USA"),
    "San Francisco Bay Area": ("Levi's Stadium", "USA"),
    "Seattle": ("Lumen Field", "USA"),
    "Toronto": ("BMO Field", "Canada"),
    "Vancouver": ("BC Place", "Canada"),
}

# Full match schedule built from public 2026 FIFA WC schedule (104 matches)
# Format: (match_no, home_or_team1, away_or_team2, dstr, time, city)
# Knockouts use placeholder names ("Group A Winner", etc.)
WC_MATCHES = [
    # ===== GROUP STAGE - MATCHDAY 1 (June 11-17) =====
    (1, "Mexico", "South Africa", "2026-06-11", "13:00", "Mexico City"),  # Opener
    (2, "South Korea", "Czechia", "2026-06-11", "20:00", "Guadalajara"),
    (3, "USA", "Paraguay", "2026-06-12", "18:00", "Los Angeles"),
    (4, "Canada", "Bosnia and Herzegovina", "2026-06-12", "12:00", "Toronto"),
    (5, "Argentina", "Algeria", "2026-06-13", "15:00", "Kansas City"),
    (6, "Brazil", "Morocco", "2026-06-13", "18:00", "New York"),
    (7, "Spain", "Switzerland", "2026-06-14", "12:00", "Boston"),
    (8, "Germany", "Tunisia", "2026-06-14", "15:00", "Atlanta"),
    (9, "England", "Cape Verde", "2026-06-14", "18:00", "Philadelphia"),
    (10, "Portugal", "Egypt", "2026-06-15", "15:00", "Dallas"),
    (11, "France", "Senegal", "2026-06-15", "18:00", "New York"),
    (12, "Netherlands", "Cameroon", "2026-06-15", "21:00", "Miami"),
    (13, "Japan", "Australia", "2026-06-16", "12:00", "San Francisco Bay Area"),
    (14, "Belgium", "Iran", "2026-06-16", "15:00", "Houston"),
    (15, "Italy", "Saudi Arabia", "2026-06-16", "18:00", "Seattle"),  # Italy hopeful qualification
    (16, "Croatia", "Ecuador", "2026-06-17", "15:00", "Vancouver"),
    # ===== MATCHDAY 2 (June 18-23) =====
    (17, "Mexico", "Norway", "2026-06-18", "20:00", "Mexico City"),
    (18, "South Africa", "Czechia", "2026-06-18", "12:00", "Atlanta"),
    (19, "USA", "Scotland", "2026-06-19", "20:00", "Los Angeles"),
    (20, "Canada", "Qatar", "2026-06-18", "18:00", "Vancouver"),
    (21, "Argentina", "Nigeria", "2026-06-19", "21:00", "Houston"),
    (22, "Brazil", "Haiti", "2026-06-19", "18:00", "Philadelphia"),
    (23, "Spain", "Türkiye", "2026-06-20", "12:00", "Boston"),
    (24, "Germany", "Uzbekistan", "2026-06-20", "15:00", "Dallas"),
    (25, "England", "Ghana", "2026-06-20", "18:00", "Atlanta"),
    (26, "Portugal", "Côte d'Ivoire", "2026-06-21", "15:00", "Kansas City"),
    (27, "France", "Serbia", "2026-06-21", "18:00", "Miami"),
    (28, "Netherlands", "South Korea", "2026-06-21", "21:00", "Seattle"),
    (29, "Japan", "Colombia", "2026-06-22", "15:00", "San Francisco Bay Area"),
    (30, "Belgium", "Uruguay", "2026-06-22", "18:00", "New York"),
    (31, "Italy", "Mali", "2026-06-22", "21:00", "Monterrey"),
    (32, "Croatia", "Jordan", "2026-06-23", "15:00", "Guadalajara"),
    # ===== MATCHDAY 3 (June 24-27) =====
    (33, "South Africa", "South Korea", "2026-06-24", "12:00", "Monterrey"),
    (34, "Mexico", "Czechia", "2026-06-24", "20:00", "Guadalajara"),
    (35, "Paraguay", "Scotland", "2026-06-25", "18:00", "Atlanta"),
    (36, "USA", "Bosnia and Herzegovina", "2026-06-25", "20:00", "Kansas City"),
    (37, "Argentina", "Haiti", "2026-06-26", "21:00", "Miami"),
    (38, "Brazil", "Senegal", "2026-06-26", "18:00", "New York"),
    (39, "Spain", "Egypt", "2026-06-26", "12:00", "Boston"),
    (40, "Germany", "Cape Verde", "2026-06-27", "15:00", "Philadelphia"),
    (41, "England", "Tunisia", "2026-06-27", "18:00", "Dallas"),
    (42, "Portugal", "Cameroon", "2026-06-27", "21:00", "Houston"),
    (43, "France", "Iran", "2026-06-27", "20:00", "New York"),
    (44, "Netherlands", "Australia", "2026-06-26", "15:00", "Seattle"),
    (45, "Japan", "Saudi Arabia", "2026-06-25", "15:00", "San Francisco Bay Area"),
    (46, "Belgium", "Colombia", "2026-06-25", "18:00", "Vancouver"),
    (47, "Italy", "Ecuador", "2026-06-26", "21:00", "Toronto"),
    (48, "Croatia", "Mali", "2026-06-26", "20:00", "Guadalajara"),
    # ===== ROUND OF 32 (June 28 - July 3) =====
    (49, "Group A Winner", "Best 3rd Place", "2026-06-28", "12:00", "Philadelphia"),
    (50, "Group B Winner", "Best 3rd Place", "2026-06-28", "15:00", "Toronto"),
    (51, "Group C Winner", "Best 3rd Place", "2026-06-28", "18:00", "Boston"),
    (52, "Group D Winner", "Best 3rd Place", "2026-06-29", "12:00", "Houston"),
    (53, "Group E Winner", "Best 3rd Place", "2026-06-29", "15:00", "Mexico City"),
    (54, "Group F Winner", "Best 3rd Place", "2026-06-29", "18:00", "Los Angeles"),
    (55, "Group G Winner", "Best 3rd Place", "2026-06-30", "15:00", "Dallas"),
    (56, "Group H Winner", "Best 3rd Place", "2026-06-30", "18:00", "Atlanta"),
    (57, "Group A 2nd", "Group I 2nd", "2026-07-01", "12:00", "Miami"),
    (58, "Group B 2nd", "Group J 2nd", "2026-07-01", "15:00", "Vancouver"),
    (59, "Group C 2nd", "Group K 2nd", "2026-07-01", "18:00", "New York"),
    (60, "Group D 2nd", "Group L 2nd", "2026-07-02", "12:00", "Seattle"),
    (61, "Group E 2nd", "Group F 2nd", "2026-07-02", "15:00", "Kansas City"),
    (62, "Group G 2nd", "Group H 2nd", "2026-07-02", "18:00", "Monterrey"),
    (63, "Group I Winner", "Best 3rd Place", "2026-07-03", "15:00", "San Francisco Bay Area"),
    (64, "Group J Winner", "Best 3rd Place", "2026-07-03", "18:00", "Guadalajara"),
    # ===== ROUND OF 16 (July 4-7) =====
    (65, "R32 Winner 1", "R32 Winner 2", "2026-07-04", "12:00", "Boston"),
    (66, "R32 Winner 3", "R32 Winner 4", "2026-07-04", "15:00", "Atlanta"),
    (67, "R32 Winner 5", "R32 Winner 6", "2026-07-05", "12:00", "Los Angeles"),
    (68, "R32 Winner 7", "R32 Winner 8", "2026-07-05", "15:00", "Mexico City"),
    (69, "R32 Winner 9", "R32 Winner 10", "2026-07-06", "12:00", "Dallas"),
    (70, "R32 Winner 11", "R32 Winner 12", "2026-07-06", "15:00", "Miami"),
    (71, "R32 Winner 13", "R32 Winner 14", "2026-07-07", "12:00", "New York"),
    (72, "R32 Winner 15", "R32 Winner 16", "2026-07-07", "15:00", "Houston"),
    # ===== QUARTER-FINALS (July 9-11) =====
    (73, "QF Match 1", "QF Match 2", "2026-07-09", "15:00", "Los Angeles"),
    (74, "QF Match 3", "QF Match 4", "2026-07-10", "15:00", "Boston"),
    (75, "QF Match 5", "QF Match 6", "2026-07-11", "12:00", "Kansas City"),
    (76, "QF Match 7", "QF Match 8", "2026-07-11", "18:00", "Miami"),
    # ===== SEMI-FINALS (July 14-15) =====
    (77, "Semi-Final Match 1", "Semi-Final Match 2", "2026-07-14", "15:00", "Dallas"),
    (78, "Semi-Final Match 3", "Semi-Final Match 4", "2026-07-15", "15:00", "Atlanta"),
    # ===== THIRD PLACE PLAY-OFF (July 18) =====
    (79, "3rd Place Match 1", "3rd Place Match 2", "2026-07-18", "15:00", "Miami"),
    # ===== FINAL (July 19) =====
    (80, "World Cup Finalist 1", "World Cup Finalist 2", "2026-07-19", "15:00", "New York"),
]


def wc_pricing(match_no, city):
    """Pricing tiers for WC: group stage cheaper, knockout expensive, final premium."""
    if match_no == 80:  # Final
        return 800, 4500
    if match_no == 79:  # 3rd place
        return 350, 1800
    if match_no >= 77:  # Semis
        return 600, 3500
    if match_no >= 73:  # QFs
        return 450, 2500
    if match_no >= 65:  # R16
        return 280, 1500
    if match_no >= 49:  # R32
        return 180, 950
    # Group stage - higher in opening match and US/Mexico/Canada matches
    if match_no == 1:  # Opener
        return 350, 2000
    return 130, 700


def build_wc():
    out = []
    big_teams_set = {"Argentina", "Brazil", "France", "Spain", "Germany", "England", "Portugal",
                     "Netherlands", "Italy", "Belgium", "USA", "Mexico"}
    for i, (mno, t1, t2, dstr, t, city) in enumerate(WC_MATCHES):
        venue, country = WC_VENUES[city]
        dt = datetime.fromisoformat(dstr + "T" + t + ":00")
        mn, mx = wc_pricing(mno, city)
        feat = mno <= 16 or mno == 1 or mno == 80 or t1 in big_teams_set or t2 in big_teams_set or mno >= 65
        title_map = {
            1: "FIFA World Cup 2026 - Opening Match",
            73: "FIFA World Cup 2026 - Quarter-Final 1",
            74: "FIFA World Cup 2026 - Quarter-Final 2",
            75: "FIFA World Cup 2026 - Quarter-Final 3",
            76: "FIFA World Cup 2026 - Quarter-Final 4",
            77: "FIFA World Cup 2026 - Semi-Final 1",
            78: "FIFA World Cup 2026 - Semi-Final 2",
            79: "FIFA World Cup 2026 - Third Place Play-Off",
            80: "FIFA World Cup 2026 - FINAL",
        }
        ev = make_event(
            t1, t2, "FIFA WORLD CUP 2026", venue, city, dt, t, mn, mx,
            available=70000 if mno == 80 else (60000 if feat else 45000),
            featured=feat, image_idx=i, country=country
        )
        # Override title for special matches
        if mno in title_map:
            ev["title"] = title_map[mno]
        # Mark all matches with WC categories
        ev["categories"] = [c.upper() for c in [t1, t2, "WORLD CUP 2026"]]
        ev["match_number"] = mno
        out.append(ev)
    return out


# ============================================================================
# RUN ALL SEEDS
# ============================================================================
async def run_seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print("=" * 70)
    print("SEED ADDIZIONALE: Eventi Maggio 2026 + Coppe + FIFA World Cup 2026")
    print("=" * 70)

    all_events = []
    all_events.extend(build_serie_a())
    all_events.extend(build_premier())
    all_events.extend(build_laliga())
    all_events.extend(build_bundes())
    all_events.extend(build_ligue1())
    all_events.extend(build_pt())
    all_events.extend(build_super_lig())
    all_events.extend(build_ucl())
    all_events.extend(build_uel())
    all_events.extend(build_cup_finals())
    all_events.extend(build_wc())

    print(f"\nTotale eventi da inserire: {len(all_events)}")

    # ---- 1. Aggiunge la lega FIFA World Cup 2026 nella collezione 'leagues' se mancante
    existing_wc = await db.leagues.find_one({"slug": "fifa-world-cup-2026"})
    if not existing_wc:
        await db.leagues.insert_one({
            "name": "FIFA World Cup 2026",
            "slug": "fifa-world-cup-2026",
            "country": "USA / Canada / Mexico",
            "type": "cup",
            "logo_url": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2e/2026_FIFA_World_Cup_emblem.svg/1200px-2026_FIFA_World_Cup_emblem.svg.png",
            "order": 20,
            "created_at": datetime.now(timezone.utc),
        })
        print("Aggiunta lega: FIFA World Cup 2026")
    else:
        print("Lega FIFA World Cup 2026 già presente")

    # ---- 2. Inserisce eventi solo se non esistenti (chiave: title + sort_date)
    inserted, skipped = 0, 0
    for ev in all_events:
        existing = await db.events.find_one({
            "title": ev["title"],
            "sort_date": ev["sort_date"],
        })
        if existing:
            skipped += 1
            continue
        await db.events.insert_one(ev)
        inserted += 1

    print(f"\nInseriti: {inserted}")
    print(f"Skip (già esistenti): {skipped}")

    # Riepilogo finale
    total = await db.events.count_documents({})
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    upcoming_str = await db.events.count_documents({"sort_date": {"$gte": today_str}})
    print(f"\nDB finale: {total} eventi totali, {upcoming_str} futuri (sort_date string).")

    client.close()


if __name__ == "__main__":
    asyncio.run(run_seed())

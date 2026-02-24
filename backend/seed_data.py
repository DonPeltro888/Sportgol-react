import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stadium images pool
stadium_images = [
    "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
    "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
    "https://images.pexels.com/photos/9739469/pexels-photo-9739469.jpeg",
    "https://images.pexels.com/photos/3452544/pexels-photo-3452544.jpeg",
    "https://images.unsplash.com/photo-1592336563179-5a95288563c9",
    "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9",
    "https://images.pexels.com/photos/18420916/pexels-photo-18420916.jpeg",
    "https://images.pexels.com/photos/18420917/pexels-photo-18420917.jpeg",
    "https://images.unsplash.com/photo-1522778119026-d647f0596c20",
    "https://images.unsplash.com/photo-1599158150601-1417ebbaafdd",
    "https://images.unsplash.com/photo-1629217855633-79a6925d6c47"
]

def get_stadium_image(index):
    return stadium_images[index % len(stadium_images)]

# Complete match data for all leagues
events_data = [
    # === SERIE A MATCHES ===
    # February-March
    {"title": "Parma vs Cagliari", "categories": ["PARMA", "CAGLIARI"], "date": "February 27, 2026", "location": "Parma", "stadium": "Stadio Ennio Tardini", "price_range": {"min": 25, "max": 120}, "available_tickets": 8000, "featured": True, "league": "SERIE A"},
    {"title": "Como vs Lecce", "categories": ["COMO", "LECCE"], "date": "February 28, 2026", "location": "Como", "stadium": "Stadio Giuseppe Sinigaglia", "price_range": {"min": 22, "max": 100}, "available_tickets": 7500, "featured": True, "league": "SERIE A"},
    {"title": "Hellas Verona vs Napoli", "categories": ["HELLAS VERONA", "NAPOLI"], "date": "February 28, 2026", "location": "Verona", "stadium": "Stadio Marcantonio Bentegodi", "price_range": {"min": 35, "max": 180}, "available_tickets": 11000, "featured": True, "league": "SERIE A"},
    {"title": "Inter vs Genoa", "categories": ["INTER", "GENOA"], "date": "February 28, 2026", "location": "Milan", "stadium": "San Siro", "price_range": {"min": 50, "max": 300}, "available_tickets": 18000, "featured": True, "league": "SERIE A"},
    {"title": "Cremonese vs Milan", "categories": ["CREMONESE", "MILAN"], "date": "March 1, 2026", "location": "Cremona", "stadium": "Stadio Giovanni Zini", "price_range": {"min": 35, "max": 200}, "available_tickets": 10000, "featured": True, "league": "SERIE A"},
    {"title": "Sassuolo vs Atalanta", "categories": ["SASSUOLO", "ATALANTA"], "date": "March 1, 2026", "location": "Reggio Emilia", "stadium": "Mapei Stadium", "price_range": {"min": 30, "max": 160}, "available_tickets": 14000, "featured": True, "league": "SERIE A"},
    {"title": "Torino vs Lazio", "categories": ["TORINO", "LAZIO"], "date": "March 1, 2026", "location": "Turin", "stadium": "Stadio Olimpico Grande Torino", "price_range": {"min": 30, "max": 150}, "available_tickets": 12000, "featured": True, "league": "SERIE A"},
    {"title": "Roma vs Juventus", "categories": ["ROMA", "JUVENTUS"], "date": "March 1, 2026", "location": "Rome", "stadium": "Stadio Olimpico", "price_range": {"min": 45, "max": 280}, "available_tickets": 15000, "featured": True, "league": "SERIE A"},
    {"title": "Pisa vs Bologna", "categories": ["PISA", "BOLOGNA"], "date": "March 2, 2026", "location": "Pisa", "stadium": "Arena Garibaldi", "price_range": {"min": 28, "max": 140}, "available_tickets": 9000, "featured": True, "league": "SERIE A"},
    {"title": "Udinese vs Fiorentina", "categories": ["UDINESE", "FIORENTINA"], "date": "March 2, 2026", "location": "Udine", "stadium": "Dacia Arena", "price_range": {"min": 28, "max": 130}, "available_tickets": 9500, "featured": True, "league": "SERIE A"},
    
    # March 8
    {"title": "Atalanta vs Udinese", "categories": ["ATALANTA", "UDINESE"], "date": "March 8, 2026", "location": "Bergamo", "stadium": "Gewiss Stadium", "price_range": {"min": 38, "max": 170}, "available_tickets": 11500, "featured": False, "league": "SERIE A"},
    {"title": "Bologna vs Hellas Verona", "categories": ["BOLOGNA", "HELLAS VERONA"], "date": "March 8, 2026", "location": "Bologna", "stadium": "Renato Dall'Ara", "price_range": {"min": 32, "max": 140}, "available_tickets": 10000, "featured": False, "league": "SERIE A"},
    {"title": "Cagliari vs Como", "categories": ["CAGLIARI", "COMO"], "date": "March 8, 2026", "location": "Cagliari", "stadium": "Unipol Domus", "price_range": {"min": 25, "max": 110}, "available_tickets": 8500, "featured": False, "league": "SERIE A"},
    {"title": "Fiorentina vs Parma", "categories": ["FIORENTINA", "PARMA"], "date": "March 8, 2026", "location": "Florence", "stadium": "Artemio Franchi", "price_range": {"min": 32, "max": 150}, "available_tickets": 12000, "featured": False, "league": "SERIE A"},
    {"title": "Genoa vs Roma", "categories": ["GENOA", "ROMA"], "date": "March 8, 2026", "location": "Genoa", "stadium": "Luigi Ferraris", "price_range": {"min": 35, "max": 180}, "available_tickets": 11000, "featured": False, "league": "SERIE A"},
    {"title": "Juventus vs Pisa", "categories": ["JUVENTUS", "PISA"], "date": "March 8, 2026", "location": "Turin", "stadium": "Allianz Stadium", "price_range": {"min": 45, "max": 250}, "available_tickets": 16000, "featured": False, "league": "SERIE A"},
    {"title": "Lazio vs Sassuolo", "categories": ["LAZIO", "SASSUOLO"], "date": "March 8, 2026", "location": "Rome", "stadium": "Stadio Olimpico", "price_range": {"min": 40, "max": 200}, "available_tickets": 14000, "featured": False, "league": "SERIE A"},
    {"title": "Lecce vs Cremonese", "categories": ["LECCE", "CREMONESE"], "date": "March 8, 2026", "location": "Lecce", "stadium": "Via del Mare", "price_range": {"min": 25, "max": 120}, "available_tickets": 9000, "featured": False, "league": "SERIE A"},
    {"title": "Milan vs Inter", "categories": ["MILAN", "INTER"], "date": "March 8, 2026", "location": "Milan", "stadium": "San Siro", "price_range": {"min": 80, "max": 500}, "available_tickets": 20000, "featured": True, "league": "SERIE A"},
    {"title": "Napoli vs Torino", "categories": ["NAPOLI", "TORINO"], "date": "March 8, 2026", "location": "Naples", "stadium": "Diego Armando Maradona", "price_range": {"min": 42, "max": 220}, "available_tickets": 16000, "featured": False, "league": "SERIE A"},
    
    # March 15
    {"title": "Como vs Roma", "categories": ["COMO", "ROMA"], "date": "March 15, 2026", "location": "Como", "stadium": "Stadio Giuseppe Sinigaglia", "price_range": {"min": 35, "max": 180}, "available_tickets": 7800, "featured": False, "league": "SERIE A"},
    {"title": "Cremonese vs Fiorentina", "categories": ["CREMONESE", "FIORENTINA"], "date": "March 15, 2026", "location": "Cremona", "stadium": "Stadio Giovanni Zini", "price_range": {"min": 28, "max": 140}, "available_tickets": 9500, "featured": False, "league": "SERIE A"},
    {"title": "Inter vs Atalanta", "categories": ["INTER", "ATALANTA"], "date": "March 15, 2026", "location": "Milan", "stadium": "San Siro", "price_range": {"min": 55, "max": 320}, "available_tickets": 19000, "featured": True, "league": "SERIE A"},
    {"title": "Lazio vs Milan", "categories": ["LAZIO", "MILAN"], "date": "March 15, 2026", "location": "Rome", "stadium": "Stadio Olimpico", "price_range": {"min": 45, "max": 240}, "available_tickets": 15000, "featured": True, "league": "SERIE A"},
    {"title": "Napoli vs Lecce", "categories": ["NAPOLI", "LECCE"], "date": "March 15, 2026", "location": "Naples", "stadium": "Diego Armando Maradona", "price_range": {"min": 38, "max": 200}, "available_tickets": 14000, "featured": False, "league": "SERIE A"},
    {"title": "Pisa vs Cagliari", "categories": ["PISA", "CAGLIARI"], "date": "March 15, 2026", "location": "Pisa", "stadium": "Arena Garibaldi", "price_range": {"min": 25, "max": 120}, "available_tickets": 8800, "featured": False, "league": "SERIE A"},
    {"title": "Sassuolo vs Bologna", "categories": ["SASSUOLO", "BOLOGNA"], "date": "March 15, 2026", "location": "Reggio Emilia", "stadium": "Mapei Stadium", "price_range": {"min": 30, "max": 150}, "available_tickets": 13000, "featured": False, "league": "SERIE A"},
    {"title": "Torino vs Parma", "categories": ["TORINO", "PARMA"], "date": "March 15, 2026", "location": "Turin", "stadium": "Stadio Olimpico Grande Torino", "price_range": {"min": 28, "max": 140}, "available_tickets": 11000, "featured": False, "league": "SERIE A"},
    {"title": "Udinese vs Juventus", "categories": ["UDINESE", "JUVENTUS"], "date": "March 15, 2026", "location": "Udine", "stadium": "Dacia Arena", "price_range": {"min": 45, "max": 240}, "available_tickets": 10000, "featured": False, "league": "SERIE A"},
    {"title": "Hellas Verona vs Genoa", "categories": ["HELLAS VERONA", "GENOA"], "date": "March 15, 2026", "location": "Verona", "stadium": "Marcantonio Bentegodi", "price_range": {"min": 28, "max": 130}, "available_tickets": 9500, "featured": False, "league": "SERIE A"},
    
    # March 22
    {"title": "Atalanta vs Hellas Verona", "categories": ["ATALANTA", "HELLAS VERONA"], "date": "March 22, 2026", "location": "Bergamo", "stadium": "Gewiss Stadium", "price_range": {"min": 35, "max": 160}, "available_tickets": 11000, "featured": False, "league": "SERIE A"},
    {"title": "Bologna vs Lazio", "categories": ["BOLOGNA", "LAZIO"], "date": "March 22, 2026", "location": "Bologna", "stadium": "Renato Dall'Ara", "price_range": {"min": 35, "max": 170}, "available_tickets": 10500, "featured": False, "league": "SERIE A"},
    {"title": "Cagliari vs Napoli", "categories": ["CAGLIARI", "NAPOLI"], "date": "March 22, 2026", "location": "Cagliari", "stadium": "Unipol Domus", "price_range": {"min": 32, "max": 160}, "available_tickets": 9000, "featured": False, "league": "SERIE A"},
    {"title": "Como vs Pisa", "categories": ["COMO", "PISA"], "date": "March 22, 2026", "location": "Como", "stadium": "Stadio Giuseppe Sinigaglia", "price_range": {"min": 22, "max": 100}, "available_tickets": 7500, "featured": False, "league": "SERIE A"},
    {"title": "Fiorentina vs Inter", "categories": ["FIORENTINA", "INTER"], "date": "March 22, 2026", "location": "Florence", "stadium": "Artemio Franchi", "price_range": {"min": 45, "max": 230}, "available_tickets": 12000, "featured": True, "league": "SERIE A"},
    {"title": "Genoa vs Udinese", "categories": ["GENOA", "UDINESE"], "date": "March 22, 2026", "location": "Genoa", "stadium": "Luigi Ferraris", "price_range": {"min": 28, "max": 140}, "available_tickets": 10500, "featured": False, "league": "SERIE A"},
    {"title": "Juventus vs Sassuolo", "categories": ["JUVENTUS", "SASSUOLO"], "date": "March 22, 2026", "location": "Turin", "stadium": "Allianz Stadium", "price_range": {"min": 45, "max": 250}, "available_tickets": 16000, "featured": False, "league": "SERIE A"},
    {"title": "Milan vs Torino", "categories": ["MILAN", "TORINO"], "date": "March 22, 2026", "location": "Milan", "stadium": "San Siro", "price_range": {"min": 45, "max": 260}, "available_tickets": 17000, "featured": False, "league": "SERIE A"},
    {"title": "Parma vs Cremonese", "categories": ["PARMA", "CREMONESE"], "date": "March 22, 2026", "location": "Parma", "stadium": "Stadio Ennio Tardini", "price_range": {"min": 25, "max": 120}, "available_tickets": 8500, "featured": False, "league": "SERIE A"},
    {"title": "Roma vs Lecce", "categories": ["ROMA", "LECCE"], "date": "March 22, 2026", "location": "Rome", "stadium": "Stadio Olimpico", "price_range": {"min": 38, "max": 200}, "available_tickets": 14000, "featured": False, "league": "SERIE A"},

    # April 4
    {"title": "Pisa vs Torino", "categories": ["PISA", "TORINO"], "date": "April 4, 2026", "location": "Pisa", "stadium": "Arena Garibaldi", "price_range": {"min": 28, "max": 140}, "available_tickets": 9000, "featured": False, "league": "SERIE A"},
    {"title": "Cremonese vs Bologna", "categories": ["CREMONESE", "BOLOGNA"], "date": "April 4, 2026", "location": "Cremona", "stadium": "Stadio Giovanni Zini", "price_range": {"min": 28, "max": 130}, "available_tickets": 9500, "featured": False, "league": "SERIE A"},
    {"title": "Hellas Verona vs Fiorentina", "categories": ["HELLAS VERONA", "FIORENTINA"], "date": "April 4, 2026", "location": "Verona", "stadium": "Marcantonio Bentegodi", "price_range": {"min": 30, "max": 150}, "available_tickets": 10000, "featured": False, "league": "SERIE A"},
    {"title": "Inter vs Roma", "categories": ["INTER", "ROMA"], "date": "April 4, 2026", "location": "Milan", "stadium": "San Siro", "price_range": {"min": 55, "max": 320}, "available_tickets": 19000, "featured": True, "league": "SERIE A"},
    {"title": "Juventus vs Genoa", "categories": ["JUVENTUS", "GENOA"], "date": "April 4, 2026", "location": "Turin", "stadium": "Allianz Stadium", "price_range": {"min": 45, "max": 240}, "available_tickets": 16000, "featured": False, "league": "SERIE A"},
    {"title": "Lazio vs Parma", "categories": ["LAZIO", "PARMA"], "date": "April 4, 2026", "location": "Rome", "stadium": "Stadio Olimpico", "price_range": {"min": 35, "max": 180}, "available_tickets": 14000, "featured": False, "league": "SERIE A"},
    {"title": "Lecce vs Atalanta", "categories": ["LECCE", "ATALANTA"], "date": "April 4, 2026", "location": "Lecce", "stadium": "Via del Mare", "price_range": {"min": 30, "max": 160}, "available_tickets": 9500, "featured": False, "league": "SERIE A"},
    {"title": "Napoli vs Milan", "categories": ["NAPOLI", "MILAN"], "date": "April 4, 2026", "location": "Naples", "stadium": "Diego Armando Maradona", "price_range": {"min": 55, "max": 300}, "available_tickets": 16000, "featured": True, "league": "SERIE A"},
    {"title": "Sassuolo vs Cagliari", "categories": ["SASSUOLO", "CAGLIARI"], "date": "April 4, 2026", "location": "Reggio Emilia", "stadium": "Mapei Stadium", "price_range": {"min": 28, "max": 140}, "available_tickets": 13000, "featured": False, "league": "SERIE A"},
    {"title": "Udinese vs Como", "categories": ["UDINESE", "COMO"], "date": "April 4, 2026", "location": "Udine", "stadium": "Dacia Arena", "price_range": {"min": 25, "max": 120}, "available_tickets": 9500, "featured": False, "league": "SERIE A"},

    # === PREMIER LEAGUE MATCHES ===
    # February-March
    {"title": "Wolves vs Aston Villa", "categories": ["WOLVES", "ASTON VILLA"], "date": "February 27, 2026", "location": "Wolverhampton", "stadium": "Molineux Stadium", "price_range": {"min": 40, "max": 200}, "available_tickets": 12000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Liverpool vs West Ham", "categories": ["LIVERPOOL", "WEST HAM"], "date": "February 28, 2026", "location": "Liverpool", "stadium": "Anfield", "price_range": {"min": 55, "max": 280}, "available_tickets": 18000, "featured": True, "league": "PREMIER LEAGUE"},
    {"title": "Manchester United vs Crystal Palace", "categories": ["MANCHESTER UNITED", "CRYSTAL PALACE"], "date": "February 28, 2026", "location": "Manchester", "stadium": "Old Trafford", "price_range": {"min": 60, "max": 320}, "available_tickets": 22000, "featured": True, "league": "PREMIER LEAGUE"},
    {"title": "Leeds vs Manchester City", "categories": ["LEEDS UNITED", "MANCHESTER CITY"], "date": "February 28, 2026", "location": "Leeds", "stadium": "Elland Road", "price_range": {"min": 50, "max": 260}, "available_tickets": 16000, "featured": True, "league": "PREMIER LEAGUE"},
    {"title": "Newcastle vs Everton", "categories": ["NEWCASTLE UNITED", "EVERTON"], "date": "February 28, 2026", "location": "Newcastle", "stadium": "St James' Park", "price_range": {"min": 45, "max": 240}, "available_tickets": 15000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Brighton vs Nottingham Forest", "categories": ["BRIGHTON", "NOTTINGHAM FOREST"], "date": "February 28, 2026", "location": "Brighton", "stadium": "Amex Stadium", "price_range": {"min": 38, "max": 180}, "available_tickets": 13000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Burnley vs Brentford", "categories": ["BURNLEY", "BRENTFORD"], "date": "February 28, 2026", "location": "Burnley", "stadium": "Turf Moor", "price_range": {"min": 35, "max": 160}, "available_tickets": 11000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Bournemouth vs Sunderland", "categories": ["BOURNEMOUTH", "SUNDERLAND"], "date": "February 28, 2026", "location": "Bournemouth", "stadium": "Vitality Stadium", "price_range": {"min": 35, "max": 170}, "available_tickets": 10000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Fulham vs Tottenham", "categories": ["FULHAM", "TOTTENHAM"], "date": "March 1, 2026", "location": "London", "stadium": "Craven Cottage", "price_range": {"min": 50, "max": 250}, "available_tickets": 14000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Arsenal vs Chelsea", "categories": ["ARSENAL", "CHELSEA"], "date": "March 1, 2026", "location": "London", "stadium": "Emirates Stadium", "price_range": {"min": 65, "max": 350}, "available_tickets": 20000, "featured": True, "league": "PREMIER LEAGUE"},
    
    # March 15-16
    {"title": "Arsenal vs Everton", "categories": ["ARSENAL", "EVERTON"], "date": "March 15, 2026", "location": "London", "stadium": "Emirates Stadium", "price_range": {"min": 55, "max": 300}, "available_tickets": 19000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Manchester United vs Aston Villa", "categories": ["MANCHESTER UNITED", "ASTON VILLA"], "date": "March 15, 2026", "location": "Manchester", "stadium": "Old Trafford", "price_range": {"min": 58, "max": 310}, "available_tickets": 21000, "featured": True, "league": "PREMIER LEAGUE"},
    {"title": "Liverpool vs Tottenham", "categories": ["LIVERPOOL", "TOTTENHAM"], "date": "March 15, 2026", "location": "Liverpool", "stadium": "Anfield", "price_range": {"min": 60, "max": 320}, "available_tickets": 18000, "featured": True, "league": "PREMIER LEAGUE"},
    {"title": "Brentford vs Wolves", "categories": ["BRENTFORD", "WOLVES"], "date": "March 16, 2026", "location": "London", "stadium": "Gtech Community Stadium", "price_range": {"min": 40, "max": 190}, "available_tickets": 12000, "featured": False, "league": "PREMIER LEAGUE"},
    {"title": "Chelsea vs Newcastle", "categories": ["CHELSEA", "NEWCASTLE UNITED"], "date": "March 14, 2026", "location": "London", "stadium": "Stamford Bridge", "price_range": {"min": 58, "max": 300}, "available_tickets": 16000, "featured": True, "league": "PREMIER LEAGUE"},

    # === LA LIGA MATCHES ===
    # February-March
    {"title": "Barcelona vs Villarreal", "categories": ["BARCELONA", "VILLARREAL"], "date": "February 28, 2026", "location": "Barcelona", "stadium": "Spotify Camp Nou", "price_range": {"min": 70, "max": 400}, "available_tickets": 25000, "featured": True, "league": "LA LIGA"},
    {"title": "Real Madrid vs Getafe", "categories": ["REAL MADRID", "GETAFE"], "date": "March 2, 2026", "location": "Madrid", "stadium": "Santiago Bernabéu", "price_range": {"min": 80, "max": 450}, "available_tickets": 28000, "featured": True, "league": "LA LIGA"},
    {"title": "Real Betis vs Sevilla", "categories": ["BETIS", "SEVILLA"], "date": "March 1, 2026", "location": "Seville", "stadium": "Estadio La Cartuja", "price_range": {"min": 45, "max": 220}, "available_tickets": 16000, "featured": True, "league": "LA LIGA"},
    {"title": "Atlético Madrid vs Oviedo", "categories": ["ATLÉTICO MADRID", "OVIEDO"], "date": "February 28, 2026", "location": "Oviedo", "stadium": "Estadio Carlos Tartiere", "price_range": {"min": 38, "max": 180}, "available_tickets": 11000, "featured": False, "league": "LA LIGA"},
    {"title": "Mallorca vs Real Sociedad", "categories": ["MALLORCA", "REAL SOCIEDAD"], "date": "February 28, 2026", "location": "Palma", "stadium": "Estadi Mallorca Son Moix", "price_range": {"min": 35, "max": 160}, "available_tickets": 9500, "featured": False, "league": "LA LIGA"},
    {"title": "Valencia vs Osasuna", "categories": ["VALENCIA", "OSASUNA"], "date": "March 1, 2026", "location": "Valencia", "stadium": "Mestalla Stadium", "price_range": {"min": 40, "max": 190}, "available_tickets": 14000, "featured": False, "league": "LA LIGA"},
    {"title": "Girona vs Celta Vigo", "categories": ["GIRONA", "CELTA VIGO"], "date": "March 1, 2026", "location": "Girona", "stadium": "Estadi Montilivi", "price_range": {"min": 32, "max": 150}, "available_tickets": 8500, "featured": False, "league": "LA LIGA"},
    {"title": "Rayo Vallecano vs Athletic Bilbao", "categories": ["RAYO VALLECANO", "ATHLETIC BILBAO"], "date": "February 28, 2026", "location": "Madrid", "stadium": "Estadio de Vallecas", "price_range": {"min": 30, "max": 140}, "available_tickets": 7800, "featured": False, "league": "LA LIGA"},
    {"title": "Elche vs Espanyol", "categories": ["ELCHE", "ESPANYOL"], "date": "March 1, 2026", "location": "Elche", "stadium": "Martínez Valero", "price_range": {"min": 28, "max": 130}, "available_tickets": 9000, "featured": False, "league": "LA LIGA"},
    {"title": "Levante vs Alavés", "categories": ["LEVANTE", "ALAVÉS"], "date": "February 27, 2026", "location": "Valencia", "stadium": "Ciutat de València", "price_range": {"min": 28, "max": 120}, "available_tickets": 8500, "featured": False, "league": "LA LIGA"},

    # March 7-9
    {"title": "Celta Vigo vs Real Madrid", "categories": ["CELTA VIGO", "REAL MADRID"], "date": "March 7, 2026", "location": "Vigo", "stadium": "Balaídos", "price_range": {"min": 48, "max": 250}, "available_tickets": 12000, "featured": True, "league": "LA LIGA"},
    {"title": "Atlético Madrid vs Real Sociedad", "categories": ["ATLÉTICO MADRID", "REAL SOCIEDAD"], "date": "March 7, 2026", "location": "Madrid", "stadium": "Metropolitano", "price_range": {"min": 55, "max": 280}, "available_tickets": 17000, "featured": True, "league": "LA LIGA"},
    {"title": "Getafe vs Betis", "categories": ["GETAFE", "BETIS"], "date": "March 7, 2026", "location": "Madrid", "stadium": "Coliseum", "price_range": {"min": 32, "max": 150}, "available_tickets": 10000, "featured": False, "league": "LA LIGA"},
    {"title": "Levante vs Girona", "categories": ["LEVANTE", "GIRONA"], "date": "March 7, 2026", "location": "Valencia", "stadium": "Ciutat de València", "price_range": {"min": 28, "max": 130}, "available_tickets": 8500, "featured": False, "league": "LA LIGA"},
    
    # March 14-16
    {"title": "Real Madrid vs Elche", "categories": ["REAL MADRID", "ELCHE"], "date": "March 14, 2026", "location": "Madrid", "stadium": "Santiago Bernabéu", "price_range": {"min": 75, "max": 420}, "available_tickets": 27000, "featured": True, "league": "LA LIGA"},
    {"title": "Barcelona vs Sevilla", "categories": ["BARCELONA", "SEVILLA"], "date": "March 15, 2026", "location": "Barcelona", "stadium": "Spotify Camp Nou", "price_range": {"min": 72, "max": 410}, "available_tickets": 26000, "featured": True, "league": "LA LIGA"},
    {"title": "Atlético Madrid vs Getafe", "categories": ["ATLÉTICO MADRID", "GETAFE"], "date": "March 14, 2026", "location": "Madrid", "stadium": "Metropolitano", "price_range": {"min": 48, "max": 240}, "available_tickets": 16000, "featured": False, "league": "LA LIGA"},
    {"title": "Girona vs Athletic Bilbao", "categories": ["GIRONA", "ATHLETIC BILBAO"], "date": "March 14, 2026", "location": "Girona", "stadium": "Estadi Montilivi", "price_range": {"min": 35, "max": 160}, "available_tickets": 8800, "featured": False, "league": "LA LIGA"},

    # March 22 (Derby weekend)
    {"title": "Real Madrid vs Atlético Madrid", "categories": ["REAL MADRID", "ATLÉTICO MADRID"], "date": "March 22, 2026", "location": "Madrid", "stadium": "Santiago Bernabéu", "price_range": {"min": 90, "max": 500}, "available_tickets": 30000, "featured": True, "league": "LA LIGA"},
    {"title": "Barcelona vs Rayo Vallecano", "categories": ["BARCELONA", "RAYO VALLECANO"], "date": "March 22, 2026", "location": "Barcelona", "stadium": "Spotify Camp Nou", "price_range": {"min": 65, "max": 380}, "available_tickets": 24000, "featured": True, "league": "LA LIGA"},
    {"title": "Athletic Bilbao vs Betis", "categories": ["ATHLETIC BILBAO", "BETIS"], "date": "March 22, 2026", "location": "Bilbao", "stadium": "San Mamés", "price_range": {"min": 42, "max": 210}, "available_tickets": 14000, "featured": False, "league": "LA LIGA"},

    # === BUNDESLIGA MATCHES ===
    # February-March
    {"title": "Borussia Dortmund vs Bayern Munich", "categories": ["BORUSSIA DORTMUND", "BAYERN MUNICH"], "date": "February 28, 2026", "location": "Dortmund", "stadium": "Signal Iduna Park", "price_range": {"min": 60, "max": 350}, "available_tickets": 22000, "featured": True, "league": "BUNDESLIGA"},
    {"title": "Hamburger SV vs RB Leipzig", "categories": ["HAMBURGER SV", "RB LEIPZIG"], "date": "March 1, 2026", "location": "Hamburg", "stadium": "Volksparkstadion", "price_range": {"min": 45, "max": 240}, "available_tickets": 18000, "featured": True, "league": "BUNDESLIGA"},
    {"title": "Leverkusen vs Mainz", "categories": ["LEVERKUSEN", "MAINZ"], "date": "February 28, 2026", "location": "Leverkusen", "stadium": "BayArena", "price_range": {"min": 40, "max": 200}, "available_tickets": 15000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Stuttgart vs Wolfsburg", "categories": ["STUTTGART", "WOLFSBURG"], "date": "March 1, 2026", "location": "Stuttgart", "stadium": "Mercedes-Benz Arena", "price_range": {"min": 38, "max": 180}, "available_tickets": 14000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Eintracht Frankfurt vs Freiburg", "categories": ["EINTRACHT FRANKFURT", "FREIBURG"], "date": "March 1, 2026", "location": "Frankfurt", "stadium": "Deutsche Bank Park", "price_range": {"min": 35, "max": 170}, "available_tickets": 13000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Borussia Mönchengladbach vs Union Berlin", "categories": ["BORUSSIA MÖNCHENGLADBACH", "UNION BERLIN"], "date": "February 28, 2026", "location": "Mönchengladbach", "stadium": "Borussia-Park", "price_range": {"min": 32, "max": 160}, "available_tickets": 12000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Augsburg vs Köln", "categories": ["AUGSBURG", "KÖLN"], "date": "February 27, 2026", "location": "Augsburg", "stadium": "WWK Arena", "price_range": {"min": 28, "max": 130}, "available_tickets": 10000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Werder Bremen vs Heidenheim", "categories": ["WERDER BREMEN", "HEIDENHEIM"], "date": "February 28, 2026", "location": "Bremen", "stadium": "Weserstadion", "price_range": {"min": 30, "max": 140}, "available_tickets": 11000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Hoffenheim vs St. Pauli", "categories": ["HOFFENHEIM", "ST. PAULI"], "date": "February 28, 2026", "location": "Sinsheim", "stadium": "PreZero Arena", "price_range": {"min": 32, "max": 150}, "available_tickets": 10500, "featured": False, "league": "BUNDESLIGA"},
    
    # March 6-8
    {"title": "Bayern Munich vs Borussia Mönchengladbach", "categories": ["BAYERN MUNICH", "BORUSSIA MÖNCHENGLADBACH"], "date": "March 6, 2026", "location": "Munich", "stadium": "Allianz Arena", "price_range": {"min": 65, "max": 380}, "available_tickets": 25000, "featured": True, "league": "BUNDESLIGA"},
    {"title": "Köln vs Borussia Dortmund", "categories": ["KÖLN", "BORUSSIA DORTMUND"], "date": "March 7, 2026", "location": "Cologne", "stadium": "RheinEnergieStadion", "price_range": {"min": 48, "max": 250}, "available_tickets": 16000, "featured": True, "league": "BUNDESLIGA"},
    {"title": "Freiburg vs Leverkusen", "categories": ["FREIBURG", "LEVERKUSEN"], "date": "March 7, 2026", "location": "Freiburg", "stadium": "Europa-Park Stadion", "price_range": {"min": 40, "max": 200}, "available_tickets": 12000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Wolfsburg vs Hamburger SV", "categories": ["WOLFSBURG", "HAMBURGER SV"], "date": "March 7, 2026", "location": "Wolfsburg", "stadium": "Volkswagen Arena", "price_range": {"min": 38, "max": 180}, "available_tickets": 11000, "featured": False, "league": "BUNDESLIGA"},
    
    # March 14-15
    {"title": "Leverkusen vs Bayern Munich", "categories": ["LEVERKUSEN", "BAYERN MUNICH"], "date": "March 14, 2026", "location": "Leverkusen", "stadium": "BayArena", "price_range": {"min": 58, "max": 320}, "available_tickets": 16000, "featured": True, "league": "BUNDESLIGA"},
    {"title": "Hamburger SV vs Köln", "categories": ["HAMBURGER SV", "KÖLN"], "date": "March 14, 2026", "location": "Hamburg", "stadium": "Volksparkstadion", "price_range": {"min": 42, "max": 220}, "available_tickets": 17000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Stuttgart vs RB Leipzig", "categories": ["STUTTGART", "RB LEIPZIG"], "date": "March 15, 2026", "location": "Stuttgart", "stadium": "Mercedes-Benz Arena", "price_range": {"min": 45, "max": 240}, "available_tickets": 14500, "featured": True, "league": "BUNDESLIGA"},
    
    # March 21-22
    {"title": "Köln vs Borussia Mönchengladbach", "categories": ["KÖLN", "BORUSSIA MÖNCHENGLADBACH"], "date": "March 21, 2026", "location": "Cologne", "stadium": "RheinEnergieStadion", "price_range": {"min": 40, "max": 200}, "available_tickets": 15000, "featured": False, "league": "BUNDESLIGA"},
    {"title": "Borussia Dortmund vs Hamburger SV", "categories": ["BORUSSIA DORTMUND", "HAMBURGER SV"], "date": "March 21, 2026", "location": "Dortmund", "stadium": "Signal Iduna Park", "price_range": {"min": 55, "max": 300}, "available_tickets": 21000, "featured": True, "league": "BUNDESLIGA"},
    {"title": "Mainz vs Eintracht Frankfurt", "categories": ["MAINZ", "EINTRACHT FRANKFURT"], "date": "March 22, 2026", "location": "Mainz", "stadium": "MEWA Arena", "price_range": {"min": 35, "max": 170}, "available_tickets": 12000, "featured": False, "league": "BUNDESLIGA"},
]

# Add timestamps and images to all events
for i, event in enumerate(events_data):
    event["image"] = get_stadium_image(i)
    event["created_at"] = datetime.utcnow()
    event["updated_at"] = datetime.utcnow()

# Team descriptions for categories
team_descriptions = {
    # Serie A
    "Atalanta": "Atalanta BC - Known for their attacking football and youth development. Based in Bergamo.",
    "Bologna": "Bologna FC 1909 - One of Italy's oldest clubs with a rich history. Plays at Renato Dall'Ara.",
    "Cagliari": "Cagliari Calcio - Sardinian pride with passionate supporters. Home at Unipol Domus.",
    "Como": "Como 1907 - Historic club recently promoted back to Serie A. Lake Como based.",
    "Cremonese": "US Cremonese - Traditional Italian club fighting to establish themselves in Serie A.",
    "Fiorentina": "ACF Fiorentina - The Viola of Florence, known for elegant football and iconic purple kits.",
    "Genoa": "Genoa CFC - Italy's oldest football club founded in 1893. Red and blue tradition.",
    "Hellas Verona": "Hellas Verona FC - Romeo and Juliet's city club with passionate tifosi.",
    "Inter": "FC Internazionale Milano - Nerazzurri, one of Italy's most successful clubs. 20 Scudetti winners.",
    "Juventus": "Juventus FC - The Old Lady of Turin. Italy's most successful club with 36 league titles.",
    "Lazio": "SS Lazio - Biancocelesti of Rome, fierce rivals of AS Roma. Based at Stadio Olimpico.",
    "Lecce": "US Lecce - Southern Italian charm from Puglia region. Fighting spirit personified.",
    "Milan": "AC Milan - Rossoneri, 7-time European champions. One of football's most decorated clubs.",
    "Napoli": "SSC Napoli - Partenopei, recent champions. Diego Maradona's legendary club.",
    "Parma": "Parma Calcio - Yellow and blue tradition from Emilia-Romagna. Historic Italian club.",
    "Pisa": "Pisa SC - Tuscan club with ambitious project. Tower of Pisa inspiration.",
    "Roma": "AS Roma - Giallorossi of Rome. Passionate supporters and attacking tradition.",
    "Sassuolo": "US Sassuolo - Modern success story from small town. Punching above their weight.",
    "Torino": "Torino FC - Il Toro, historic Turin club. Granata colors and proud tradition.",
    "Udinese": "Udinese Calcio - Friulian club known for developing young talent from worldwide.",
    
    # Premier League teams
    "Arsenal": "Arsenal FC - The Gunners of North London. 13-time English champions. Emirates Stadium pride.",
    "Aston Villa": "Aston Villa FC - Birmingham's historic club with European Cup glory. Proud Villans.",
    "Bournemouth": "AFC Bournemouth - The Cherries, plucky south coast club punching above weight.",
    "Brentford": "Brentford FC - The Bees, West London's data-driven success story.",
    "Brighton": "Brighton & Hove Albion - Seagulls of Sussex playing attractive football under modern approach.",
    "Burnley": "Burnley FC - The Clarets, traditional Lancashire club with passionate support.",
    "Chelsea": "Chelsea FC - The Blues of West London. 6 English titles, 2 European Cups. Stamford Bridge legends.",
    "Crystal Palace": "Crystal Palace FC - The Eagles of South London. Selhurst Park atmosphere.",
    "Everton": "Everton FC - The Toffees, Merseyside's oldest club. Goodison Park tradition.",
    "Fulham": "Fulham FC - The Cottagers beside the Thames. Craven Cottage charm.",
    "Leeds United": "Leeds United - The Whites of Yorkshire. Passionate Elland Road faithful.",
    "Liverpool": "Liverpool FC - The Reds, 19-time English champions, 6 European Cups. You'll Never Walk Alone.",
    "Manchester City": "Manchester City FC - The Sky Blues, modern dynasty. Guardiola's attractive football.",
    "Manchester United": "Manchester United - The Red Devils, 20 English titles. Theatre of Dreams at Old Trafford.",
    "Newcastle United": "Newcastle United - The Magpies, passionate Geordie nation. St James' Park fortress.",
    "Nottingham Forest": "Nottingham Forest - 2-time European champions. City Ground on the Trent.",
    "Sunderland": "Sunderland AFC - The Black Cats of Northeast. Stadium of Light atmosphere.",
    "Tottenham": "Tottenham Hotspur - Spurs of North London. Attacking football tradition.",
    "West Ham": "West Ham United FC - The Hammers of East London. London Stadium, European glory.",
    "Wolves": "Wolverhampton Wanderers - The Old Gold, Molineux magic in the Midlands.",
    
    # La Liga teams
    "Alavés": "Deportivo Alavés - Basque Country pride with passionate supporters.",
    "Athletic Bilbao": "Athletic Club - Unique Basque-only policy. San Mamés cathedral.",
    "Atlético Madrid": "Atlético Madrid - Rojiblancos, fighting spirit incarnate. Metropolitano passion.",
    "Barcelona": "FC Barcelona - Més que un club. Camp Nou legends, tiki-taka masters.",
    "Betis": "Real Betis - Green and white of Seville. Benito Villamarín atmosphere.",
    "Celta Vigo": "RC Celta de Vigo - Sky blues of Galicia. Balaídos by the Atlantic.",
    "Elche": "Elche CF - Alicante province club fighting in top flight.",
    "Espanyol": "RCD Espanyol - Barcelona's other club. Cornellà-El Prat base.",
    "Getafe": "Getafe CF - Madrid suburb club with defensive strength.",
    "Girona": "Girona FC - Catalan club's recent rise. Modern success story.",
    "Levante": "Levante UD - Valencian granotas (frogs) with passionate support.",
    "Mallorca": "RCD Mallorca - Balearic island paradise club. Son Moix home.",
    "Osasuna": "CA Osasuna - Pamplona's red pride. El Sadar atmosphere.",
    "Oviedo": "Real Oviedo - Asturian tradition and proud history.",
    "Rayo Vallecano": "Rayo Vallecano - Vallecas neighborhood club. Working class heroes.",
    "Real Madrid": "Real Madrid CF - Los Blancos, 14 European Cups. Santiago Bernabéu royalty.",
    "Real Sociedad": "Real Sociedad - Txuri-urdin of San Sebastián. Reale Arena elegance.",
    "Sevilla": "Sevilla FC - Record Europa League winners. Ramón Sánchez Pizjuán passion.",
    "Valencia": "Valencia CF - Los Che, Mestalla magic. Third force of Spanish football.",
    "Villarreal": "Villarreal CF - Yellow Submarine from small town. European success.",
    
    # Bundesliga teams
    "Augsburg": "FC Augsburg - Bavarian club with modern stadium and fighting spirit.",
    "Bayern Munich": "FC Bayern München - Die Roten, German giants. Record Bundesliga winners, European royalty.",
    "Borussia Dortmund": "Borussia Dortmund - The Black and Yellows. Yellow Wall at Signal Iduna Park.",
    "Borussia Mönchengladbach": "Borussia Mönchengladbach - The Foals, 5-time German champions. Borussia-Park home.",
    "Eintracht Frankfurt": "Eintracht Frankfurt - The Eagles. Deutsche Bank Park. Recent European champions.",
    "Freiburg": "SC Freiburg - Black Forest club with modern stadium and exciting football.",
    "Hamburger SV": "Hamburger SV - HSV, traditional German giants. Volksparkstadion legends.",
    "Heidenheim": "1. FC Heidenheim - Small town achieving big dreams in Bundesliga.",
    "Hoffenheim": "TSG 1899 Hoffenheim - Modern success story from Baden-Württemberg.",
    "Köln": "1. FC Köln - The Billy Goats. Cathedral city passion.",
    "Leverkusen": "Bayer 04 Leverkusen - Die Werkself, pharmaceutical city club. BayArena home.",
    "Mainz": "1. FSV Mainz 05 - Carnival club from Rhineland. MEWA Arena.",
    "RB Leipzig": "RB Leipzig - Modern powerhouse. Red Bull Arena energy.",
    "St. Pauli": "FC St. Pauli - Cult club of Hamburg's port district. Millerntor magic.",
    "Stuttgart": "VfV Stuttgart - The Swabians. Mercedes-Benz Arena tradition.",
    "Union Berlin": "1. FC Union Berlin - Eiserne (Iron Ones). Alte Försterei atmosphere.",
    "Werder Bremen": "SV Werder Bremen - Green and white tradition. Weser Stadium.",
    "Wolfsburg": "VfL Wolfsburg - Volkswagen city club. Modern success story.",
}

categories_data = []
for team_name, description in team_descriptions.items():
    slug = team_name.lower().replace(" ", "-").replace(".", "")
    categories_data.append({
        "name": team_name,
        "label": "Tickets",
        "slug": slug,
        "description": description,
        "event_count": 0,
        "created_at": datetime.utcnow()
    })

async def seed_database():
    print("🌱 Starting comprehensive database seeding...")
    print(f"📊 Preparing to insert {len(events_data)} matches")
    print(f"👥 Preparing to insert {len(categories_data)} teams")
    
    try:
        print("\n🗑️  Clearing existing data...")
        await db.events.delete_many({})
        await db.categories.delete_many({})
        print("✅ Old data cleared")
        
        print(f"\n📝 Inserting {len(events_data)} matches...")
        result = await db.events.insert_many(events_data)
        print(f"✅ Inserted {len(result.inserted_ids)} matches successfully")
        
        print(f"\n📝 Inserting {len(categories_data)} teams with descriptions...")
        result = await db.categories.insert_many(categories_data)
        print(f"✅ Inserted {len(result.inserted_ids)} teams successfully")
        
        print("\n🎉 Database seeding completed successfully!\n")
        
        # Print detailed summary
        event_count = await db.events.count_documents({})
        category_count = await db.categories.count_documents({})
        
        serie_a_count = await db.events.count_documents({"league": "SERIE A"})
        premier_count = await db.events.count_documents({"league": "PREMIER LEAGUE"})
        laliga_count = await db.events.count_documents({"league": "LA LIGA"})
        bundesliga_count = await db.events.count_documents({"league": "BUNDESLIGA"})
        
        print("=" * 60)
        print("📊 DATABASE SUMMARY")
        print("=" * 60)
        print(f"🎯 Total Events: {event_count}")
        print(f"   🇮🇹 Serie A: {serie_a_count} matches")
        print(f"   🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League: {premier_count} matches")
        print(f"   🇪🇸 La Liga: {laliga_count} matches")
        print(f"   🇩🇪 Bundesliga: {bundesliga_count} matches")
        print(f"\n👥 Total Teams: {category_count}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\n✨ Database connection closed. Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_database())

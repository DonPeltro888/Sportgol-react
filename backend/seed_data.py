import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Real match data from various leagues
events_data = [
    # SERIE A MATCHES
    {
        "title": "Roma – Juventus",
        "image": "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
        "categories": ["AS ROMA", "JUVENTUS FC"],
        "date": "March 1, 2026",
        "location": "Rome",
        "stadium": "Stadio Olimpico",
        "price_range": {"min": 45, "max": 280},
        "available_tickets": 15000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Parma vs Cagliari",
        "image": "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
        "categories": ["PARMA", "CAGLIARI"],
        "date": "February 27, 2026",
        "location": "Parma",
        "stadium": "Stadio Ennio Tardini",
        "price_range": {"min": 25, "max": 120},
        "available_tickets": 8000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Torino vs Lazio",
        "image": "https://images.pexels.com/photos/9739469/pexels-photo-9739469.jpeg",
        "categories": ["TORINO FC", "SS LAZIO"],
        "date": "March 1, 2026",
        "location": "Turin",
        "stadium": "Stadio Olimpico Grande Torino",
        "price_range": {"min": 30, "max": 150},
        "available_tickets": 12000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Udinese vs Fiorentina",
        "image": "https://images.pexels.com/photos/3452544/pexels-photo-3452544.jpeg",
        "categories": ["UDINESE", "FIORENTINA"],
        "date": "March 2, 2026",
        "location": "Udine",
        "stadium": "Dacia Arena",
        "price_range": {"min": 28, "max": 130},
        "available_tickets": 9500,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Hellas Verona vs Napoli",
        "image": "https://images.unsplash.com/photo-1592336563179-5a95288563c9",
        "categories": ["HELLAS VERONA", "SSC NAPOLI"],
        "date": "February 28, 2026",
        "location": "Verona",
        "stadium": "Stadio Marcantonio Bentegodi",
        "price_range": {"min": 35, "max": 180},
        "available_tickets": 11000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Como vs Lecce",
        "image": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9",
        "categories": ["COMO", "LECCE"],
        "date": "February 28, 2026",
        "location": "Como",
        "stadium": "Stadio Giuseppe Sinigaglia",
        "price_range": {"min": 22, "max": 100},
        "available_tickets": 7500,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Inter – Genoa",
        "image": "https://images.pexels.com/photos/18420916/pexels-photo-18420916.jpeg",
        "categories": ["INTER", "GENOA"],
        "date": "February 28, 2026",
        "location": "Milan",
        "stadium": "San Siro",
        "price_range": {"min": 50, "max": 300},
        "available_tickets": 18000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Sassuolo vs Atalanta",
        "image": "https://images.pexels.com/photos/18420917/pexels-photo-18420917.jpeg",
        "categories": ["SASSUOLO", "ATALANTA"],
        "date": "March 1, 2026",
        "location": "Reggio Emilia",
        "stadium": "Mapei Stadium",
        "price_range": {"min": 30, "max": 160},
        "available_tickets": 14000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Cremonese – Milan",
        "image": "https://images.unsplash.com/photo-1522778119026-d647f0596c20",
        "categories": ["CREMONESE", "MILAN"],
        "date": "March 1, 2026",
        "location": "Cremona",
        "stadium": "Stadio Giovanni Zini",
        "price_range": {"min": 35, "max": 200},
        "available_tickets": 10000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Pisa vs Bologna",
        "image": "https://images.unsplash.com/photo-1599158150601-1417ebbaafdd",
        "categories": ["PISA", "BOLOGNA"],
        "date": "March 2, 2026",
        "location": "Pisa",
        "stadium": "Arena Garibaldi",
        "price_range": {"min": 28, "max": 140},
        "available_tickets": 9000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },

    # PREMIER LEAGUE MATCHES
    {
        "title": "Arsenal vs Chelsea",
        "image": "https://images.unsplash.com/photo-1629217855633-79a6925d6c47",
        "categories": ["ARSENAL", "CHELSEA"],
        "date": "March 1, 2026",
        "location": "London",
        "stadium": "Emirates Stadium",
        "price_range": {"min": 65, "max": 350},
        "available_tickets": 20000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Liverpool vs West Ham",
        "image": "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
        "categories": ["LIVERPOOL", "WEST HAM"],
        "date": "February 28, 2026",
        "location": "Liverpool",
        "stadium": "Anfield",
        "price_range": {"min": 55, "max": 280},
        "available_tickets": 18000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Manchester United vs Crystal Palace",
        "image": "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
        "categories": ["MANCHESTER UNITED", "CRYSTAL PALACE"],
        "date": "February 28, 2026",
        "location": "Manchester",
        "stadium": "Old Trafford",
        "price_range": {"min": 60, "max": 320},
        "available_tickets": 22000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Leeds vs Manchester City",
        "image": "https://images.pexels.com/photos/9739469/pexels-photo-9739469.jpeg",
        "categories": ["LEEDS UNITED", "MANCHESTER CITY"],
        "date": "February 28, 2026",
        "location": "Leeds",
        "stadium": "Elland Road",
        "price_range": {"min": 50, "max": 260},
        "available_tickets": 16000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Newcastle vs Everton",
        "image": "https://images.pexels.com/photos/3452544/pexels-photo-3452544.jpeg",
        "categories": ["NEWCASTLE UNITED", "EVERTON"],
        "date": "February 28, 2026",
        "location": "Newcastle",
        "stadium": "St James' Park",
        "price_range": {"min": 45, "max": 240},
        "available_tickets": 15000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Wolves vs Aston Villa",
        "image": "https://images.unsplash.com/photo-1592336563179-5a95288563c9",
        "categories": ["WOLVES", "ASTON VILLA"],
        "date": "February 27, 2026",
        "location": "Wolverhampton",
        "stadium": "Molineux Stadium",
        "price_range": {"min": 40, "max": 200},
        "available_tickets": 12000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Fulham vs Tottenham",
        "image": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9",
        "categories": ["FULHAM", "TOTTENHAM"],
        "date": "March 1, 2026",
        "location": "London",
        "stadium": "Craven Cottage",
        "price_range": {"min": 50, "max": 250},
        "available_tickets": 14000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Brighton vs Nottingham Forest",
        "image": "https://images.pexels.com/photos/18420916/pexels-photo-18420916.jpeg",
        "categories": ["BRIGHTON", "NOTTINGHAM FOREST"],
        "date": "February 28, 2026",
        "location": "Brighton",
        "stadium": "Amex Stadium",
        "price_range": {"min": 38, "max": 180},
        "available_tickets": 13000,
        "featured": True,
        "league": "PREMIER LEAGUE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },

    # LA LIGA MATCHES
    {
        "title": "Barcelona vs Villarreal",
        "image": "https://images.pexels.com/photos/18420917/pexels-photo-18420917.jpeg",
        "categories": ["BARCELONA", "VILLARREAL"],
        "date": "February 28, 2026",
        "location": "Barcelona",
        "stadium": "Spotify Camp Nou",
        "price_range": {"min": 70, "max": 400},
        "available_tickets": 25000,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Real Madrid vs Getafe",
        "image": "https://images.unsplash.com/photo-1522778119026-d647f0596c20",
        "categories": ["REAL MADRID", "GETAFE"],
        "date": "March 2, 2026",
        "location": "Madrid",
        "stadium": "Santiago Bernabéu",
        "price_range": {"min": 80, "max": 450},
        "available_tickets": 28000,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Real Betis vs Sevilla",
        "image": "https://images.unsplash.com/photo-1599158150601-1417ebbaafdd",
        "categories": ["BETIS", "SEVILLA"],
        "date": "March 1, 2026",
        "location": "Seville",
        "stadium": "Estadio La Cartuja",
        "price_range": {"min": 45, "max": 220},
        "available_tickets": 16000,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Atlético Madrid vs Oviedo",
        "image": "https://images.unsplash.com/photo-1629217855633-79a6925d6c47",
        "categories": ["ATLÉTICO MADRID", "OVIEDO"],
        "date": "February 28, 2026",
        "location": "Oviedo",
        "stadium": "Estadio Carlos Tartiere",
        "price_range": {"min": 38, "max": 180},
        "available_tickets": 11000,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Mallorca vs Real Sociedad",
        "image": "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
        "categories": ["MALLORCA", "REAL SOCIEDAD"],
        "date": "February 28, 2026",
        "location": "Palma",
        "stadium": "Estadi Mallorca Son Moix",
        "price_range": {"min": 35, "max": 160},
        "available_tickets": 9500,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Valencia vs Osasuna",
        "image": "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
        "categories": ["VALENCIA", "OSASUNA"],
        "date": "March 1, 2026",
        "location": "Valencia",
        "stadium": "Mestalla Stadium",
        "price_range": {"min": 40, "max": 190},
        "available_tickets": 14000,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Girona vs Celta Vigo",
        "image": "https://images.pexels.com/photos/9739469/pexels-photo-9739469.jpeg",
        "categories": ["GIRONA", "CELTA VIGO"],
        "date": "March 1, 2026",
        "location": "Girona",
        "stadium": "Estadi Montilivi",
        "price_range": {"min": 32, "max": 150},
        "available_tickets": 8500,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Rayo Vallecano vs Athletic Bilbao",
        "image": "https://images.pexels.com/photos/3452544/pexels-photo-3452544.jpeg",
        "categories": ["RAYO VALLECANO", "ATHLETIC BILBAO"],
        "date": "February 28, 2026",
        "location": "Madrid",
        "stadium": "Estadio de Vallecas",
        "price_range": {"min": 30, "max": 140},
        "available_tickets": 7800,
        "featured": True,
        "league": "LA LIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },

    # BUNDESLIGA MATCHES
    {
        "title": "Borussia Dortmund vs Bayern Munich",
        "image": "https://images.unsplash.com/photo-1592336563179-5a95288563c9",
        "categories": ["BORUSSIA DORTMUND", "BAYERN MUNICH"],
        "date": "February 28, 2026",
        "location": "Dortmund",
        "stadium": "Signal Iduna Park",
        "price_range": {"min": 60, "max": 350},
        "available_tickets": 22000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Hamburger SV vs RB Leipzig",
        "image": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9",
        "categories": ["HAMBURGER SV", "RB LEIPZIG"],
        "date": "March 1, 2026",
        "location": "Hamburg",
        "stadium": "Volksparkstadion",
        "price_range": {"min": 45, "max": 240},
        "available_tickets": 18000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Leverkusen vs Mainz",
        "image": "https://images.pexels.com/photos/18420916/pexels-photo-18420916.jpeg",
        "categories": ["LEVERKUSEN", "MAINZ"],
        "date": "February 28, 2026",
        "location": "Leverkusen",
        "stadium": "BayArena",
        "price_range": {"min": 40, "max": 200},
        "available_tickets": 15000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Stuttgart vs Wolfsburg",
        "image": "https://images.pexels.com/photos/18420917/pexels-photo-18420917.jpeg",
        "categories": ["STUTTGART", "WOLFSBURG"],
        "date": "March 1, 2026",
        "location": "Stuttgart",
        "stadium": "Mercedes-Benz Arena",
        "price_range": {"min": 38, "max": 180},
        "available_tickets": 14000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Eintracht Frankfurt vs Freiburg",
        "image": "https://images.unsplash.com/photo-1522778119026-d647f0596c20",
        "categories": ["EINTRACHT FRANKFURT", "FREIBURG"],
        "date": "March 1, 2026",
        "location": "Frankfurt",
        "stadium": "Deutsche Bank Park",
        "price_range": {"min": 35, "max": 170},
        "available_tickets": 13000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Borussia Mönchengladbach vs Union Berlin",
        "image": "https://images.unsplash.com/photo-1599158150601-1417ebbaafdd",
        "categories": ["BORUSSIA MÖNCHENGLADBACH", "UNION BERLIN"],
        "date": "February 28, 2026",
        "location": "Mönchengladbach",
        "stadium": "Borussia-Park",
        "price_range": {"min": 32, "max": 160},
        "available_tickets": 12000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Augsburg vs Köln",
        "image": "https://images.unsplash.com/photo-1629217855633-79a6925d6c47",
        "categories": ["AUGSBURG", "KÖLN"],
        "date": "February 27, 2026",
        "location": "Augsburg",
        "stadium": "WWK Arena",
        "price_range": {"min": 28, "max": 130},
        "available_tickets": 10000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Werder Bremen vs Heidenheim",
        "image": "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
        "categories": ["WERDER BREMEN", "HEIDENHEIM"],
        "date": "February 28, 2026",
        "location": "Bremen",
        "stadium": "Weserstadion",
        "price_range": {"min": 30, "max": 140},
        "available_tickets": 11000,
        "featured": True,
        "league": "BUNDESLIGA",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Categories data
categories_data = [
    # Serie A Teams
    {"name": "Atalanta", "label": "Tickets", "slug": "atalanta", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Bologna", "label": "Tickets", "slug": "bologna", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Cagliari", "label": "Tickets", "slug": "cagliari", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Como", "label": "Tickets", "slug": "como", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Cremonese", "label": "Tickets", "slug": "cremonese", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Fiorentina", "label": "Tickets", "slug": "fiorentina", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Genoa", "label": "Tickets", "slug": "genoa", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Hellas Verona", "label": "Tickets", "slug": "hellas-verona", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Inter", "label": "Tickets", "slug": "inter", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Juventus", "label": "Tickets", "slug": "juventus", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Lazio", "label": "Tickets", "slug": "lazio", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Lecce", "label": "Tickets", "slug": "lecce", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Milan", "label": "Tickets", "slug": "milan", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Napoli", "label": "Tickets", "slug": "napoli", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Parma", "label": "Tickets", "slug": "parma", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Pisa", "label": "Tickets", "slug": "pisa", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Roma", "label": "Tickets", "slug": "roma", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Sassuolo", "label": "Tickets", "slug": "sassuolo", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Torino", "label": "Tickets", "slug": "torino", "event_count": 0, "created_at": datetime.utcnow()},
    {"name": "Udinese", "label": "Tickets", "slug": "udinese", "event_count": 0, "created_at": datetime.utcnow()},
]

async def seed_database():
    print("🌱 Starting database seeding with real match data...")
    
    try:
        # Clear existing data
        print("🗑️  Clearing existing data...")
        await db.events.delete_many({})
        await db.categories.delete_many({})
        
        # Insert events
        print(f"📝 Inserting {len(events_data)} real matches...")
        result = await db.events.insert_many(events_data)
        print(f"✅ Inserted {len(result.inserted_ids)} matches")
        
        # Insert categories
        print(f"📝 Inserting {len(categories_data)} categories...")
        result = await db.categories.insert_many(categories_data)
        print(f"✅ Inserted {len(result.inserted_ids)} categories")
        
        print("🎉 Database seeding completed successfully!")
        
        # Print summary
        event_count = await db.events.count_documents({})
        category_count = await db.categories.count_documents({})
        
        # Count by league
        serie_a_count = await db.events.count_documents({"league": "SERIE A"})
        premier_count = await db.events.count_documents({"league": "PREMIER LEAGUE"})
        laliga_count = await db.events.count_documents({"league": "LA LIGA"})
        bundesliga_count = await db.events.count_documents({"league": "BUNDESLIGA"})
        
        print(f"\n📊 Database Summary:")
        print(f"   - Total Events: {event_count}")
        print(f"   - Serie A: {serie_a_count} matches")
        print(f"   - Premier League: {premier_count} matches")
        print(f"   - La Liga: {laliga_count} matches")
        print(f"   - Bundesliga: {bundesliga_count} matches")
        print(f"   - Total Categories: {category_count}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())

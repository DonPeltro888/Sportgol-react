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

# Sample events data
events_data = [
    {
        "title": "Roma – Juventus",
        "image": "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
        "categories": ["AS ROMA", "FOOTBALL", "JUVENTUS FC", "SERIE A"],
        "date": "March 1, 2026",
        "location": "Stadio Olimpico",
        "stadium": "Stadio Olimpico",
        "price_range": {"min": 45, "max": 250},
        "available_tickets": 15000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Parma vs Cagliari",
        "image": "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
        "categories": ["CAGLIARI", "FOOTBALL", "PARMA", "SERIE A"],
        "date": "March 1, 2026",
        "location": "Ennio Tardini",
        "stadium": "Ennio Tardini Stadium",
        "price_range": {"min": 25, "max": 120},
        "available_tickets": 8000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Torino FC vs SS Lazio",
        "image": "https://images.pexels.com/photos/9739469/pexels-photo-9739469.jpeg",
        "categories": ["FOOTBALL", "SERIE A", "SS LAZIO", "TORINO FC"],
        "date": "March 1, 2026",
        "location": "Stadio Olimpico Grande Torino",
        "stadium": "Olimpico Grande Torino",
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
        "categories": ["FIORENTINA", "FOOTBALL", "SERIE A", "UDINESE"],
        "date": "March 1, 2026",
        "location": "Stadio Friuli",
        "stadium": "Dacia Arena",
        "price_range": {"min": 28, "max": 130},
        "available_tickets": 9500,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Hellas Verona vs SSC Napoli",
        "image": "https://images.unsplash.com/photo-1592336563179-5a95288563c9",
        "categories": ["FOOTBALL", "HELLAS VERONA", "SERIE A", "SSC NAPOLI"],
        "date": "March 1, 2026",
        "location": "Marcantonio Bentegodi",
        "stadium": "Stadio Marcantonio Bentegodi",
        "price_range": {"min": 35, "max": 180},
        "available_tickets": 11000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Como – Lecce",
        "image": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9",
        "categories": ["COMO 1907", "FOOTBALL", "LECCE", "SERIE A"],
        "date": "March 1, 2026",
        "location": "Giuseppe Sinigaglia",
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
        "categories": ["FOOTBALL", "GENOA", "INTER", "SERIE A"],
        "date": "March 1, 2026",
        "location": "San Siro Stadium",
        "stadium": "San Siro",
        "price_range": {"min": 50, "max": 300},
        "available_tickets": 18000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Lazio – Sassuolo",
        "image": "https://images.pexels.com/photos/18420917/pexels-photo-18420917.jpeg",
        "categories": ["FOOTBALL", "SERIE A", "SS LAZIO", "US SASSUOLO"],
        "date": "March 8, 2026",
        "location": "Stadio Olimpico",
        "stadium": "Stadio Olimpico",
        "price_range": {"min": 40, "max": 200},
        "available_tickets": 14000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Milan – Inter",
        "image": "https://images.unsplash.com/photo-1522778119026-d647f0596c20",
        "categories": ["FOOTBALL", "INTER", "MILAN", "SERIE A"],
        "date": "March 8, 2026",
        "location": "San Siro Stadium",
        "stadium": "San Siro",
        "price_range": {"min": 80, "max": 500},
        "available_tickets": 20000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Bologna vs Hellas Verona",
        "image": "https://images.unsplash.com/photo-1599158150601-1417ebbaafdd",
        "categories": ["BOLOGNA", "FOOTBALL", "HELLAS VERONA", "SERIE A"],
        "date": "March 8, 2026",
        "location": "Dall'ara Stadium",
        "stadium": "Renato Dall'Ara",
        "price_range": {"min": 32, "max": 140},
        "available_tickets": 10000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Cagliari vs Como",
        "image": "https://images.unsplash.com/photo-1629217855633-79a6925d6c47",
        "categories": ["CAGLIARI", "COMO 1907", "FOOTBALL", "SERIE A"],
        "date": "March 8, 2026",
        "location": "Sardegna Arena",
        "stadium": "Unipol Domus",
        "price_range": {"min": 25, "max": 110},
        "available_tickets": 8500,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Atalanta vs Udinese",
        "image": "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
        "categories": ["ATALANTA", "FOOTBALL", "SERIE A", "UDINESE"],
        "date": "March 8, 2026",
        "location": "Gewiss Stadium",
        "stadium": "Gewiss Stadium",
        "price_range": {"min": 38, "max": 170},
        "available_tickets": 11500,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "SSC Napoli – Torino FC",
        "image": "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
        "categories": ["FOOTBALL", "SERIE A", "SSC NAPOLI", "TORINO FC"],
        "date": "March 8, 2026",
        "location": "Diego Armando Maradona Stadium",
        "stadium": "Stadio Diego Armando Maradona",
        "price_range": {"min": 42, "max": 220},
        "available_tickets": 16000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Udinese vs Juventus FC",
        "image": "https://images.pexels.com/photos/9739469/pexels-photo-9739469.jpeg",
        "categories": ["FOOTBALL", "JUVENTUS FC", "SERIE A", "UDINESE"],
        "date": "March 15, 2026",
        "location": "Stadio Friuli",
        "stadium": "Dacia Arena",
        "price_range": {"min": 45, "max": 240},
        "available_tickets": 10000,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Como – Roma",
        "image": "https://images.pexels.com/photos/3452544/pexels-photo-3452544.jpeg",
        "categories": ["AS ROMA", "COMO 1907", "FOOTBALL", "SERIE A"],
        "date": "March 15, 2026",
        "location": "Giuseppe Sinigaglia",
        "stadium": "Stadio Giuseppe Sinigaglia",
        "price_range": {"min": 35, "max": 180},
        "available_tickets": 7800,
        "featured": True,
        "league": "SERIE A",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Sample categories data
categories_data = [
    {"name": "AC Milan", "label": "Tickets", "slug": "ac-milan", "event_count": 5},
    {"name": "Roma", "label": "Tickets", "slug": "roma", "event_count": 8},
    {"name": "FC Barcelona", "label": "Tickets", "slug": "fc-barcelona", "event_count": 3},
    {"name": "Manchester United", "label": "Tickets", "slug": "manchester-united", "event_count": 6},
    {"name": "Inter FC", "label": "Tickets", "slug": "inter-fc", "event_count": 10},
    {"name": "Napoli", "label": "Tickets", "slug": "napoli", "event_count": 7},
    {"name": "Atletico de Madrid", "label": "Tickets", "slug": "atletico-madrid", "event_count": 4},
    {"name": "Manchester City", "label": "Tickets", "slug": "manchester-city", "event_count": 5},
    {"name": "Chelsea FC", "label": "Tickets", "slug": "chelsea-fc", "event_count": 6},
    {"name": "Juventus", "label": "Tickets", "slug": "juventus", "event_count": 9},
    {"name": "Real Madrid", "label": "Tickets", "slug": "real-madrid", "event_count": 8},
    {"name": "Liverpool FC", "label": "Tickets", "slug": "liverpool-fc", "event_count": 7},
    {"name": "Arsenal", "label": "Tickets", "slug": "arsenal", "event_count": 6}
]

async def seed_database():
    print("🌱 Starting database seeding...")
    
    try:
        # Clear existing data
        print("🗑️  Clearing existing data...")
        await db.events.delete_many({})
        await db.categories.delete_many({})
        
        # Insert events
        print(f"📝 Inserting {len(events_data)} events...")
        result = await db.events.insert_many(events_data)
        print(f"✅ Inserted {len(result.inserted_ids)} events")
        
        # Insert categories with created_at
        for cat in categories_data:
            cat['created_at'] = datetime.utcnow()
        
        print(f"📝 Inserting {len(categories_data)} categories...")
        result = await db.categories.insert_many(categories_data)
        print(f"✅ Inserted {len(result.inserted_ids)} categories")
        
        print("🎉 Database seeding completed successfully!")
        
        # Print summary
        event_count = await db.events.count_documents({})
        category_count = await db.categories.count_documents({})
        print(f"\n📊 Database Summary:")
        print(f"   - Total Events: {event_count}")
        print(f"   - Total Categories: {category_count}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())

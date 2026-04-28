"""
Migration script: 
1. Rimuove tutti i prezzi da tutti gli eventi
2. Applica le 7 categorie standard (senza prezzo)
3. Normalizza sort_date a stringa ISO
4. Rimuove eventi del passato (data < oggi)
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

# 7 settori standard richiesti dall'utente
STANDARD_SECTORS = [
    {"name": "Cat 1 - Lower Central", "available": True, "notes": ""},
    {"name": "Cat 1 - Middle Central", "available": True, "notes": ""},
    {"name": "Cat 1 - Normal", "available": True, "notes": ""},
    {"name": "Cat 2 - Long Upper", "available": True, "notes": ""},
    {"name": "Cat 2 - Short Lower", "available": True, "notes": ""},
    {"name": "Cat 3 - Short Side Middle", "available": True, "notes": ""},
    {"name": "Cat 4 - Short Upper", "available": True, "notes": ""},
]


async def run():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("=" * 70)
    print("MIGRAZIONE EVENTI: Rimozione prezzi + Standardizzazione settori")
    print("=" * 70)

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_str = today.strftime("%Y-%m-%d")

    # 1. Cancella eventi passati
    # Pulisce sia datetime che string sort_date
    deleted_dt = await db.events.delete_many({
        "sort_date": {"$type": "date", "$lt": today}
    })
    print(f"\nCancellati eventi passati (datetime): {deleted_dt.deleted_count}")

    deleted_str = await db.events.delete_many({
        "sort_date": {"$type": "string", "$lt": today_str}
    })
    print(f"Cancellati eventi passati (string):   {deleted_str.deleted_count}")

    # 2. Aggiorna tutti gli eventi rimanenti
    cursor = db.events.find({})
    updated = 0
    async for ev in cursor:
        update_payload = {}

        # Normalizza sort_date a stringa ISO
        sd = ev.get("sort_date")
        if isinstance(sd, datetime):
            update_payload["sort_date"] = sd.strftime("%Y-%m-%dT%H:%M:%S")

        # Sostituisci ticket_categories con i 7 settori standard (senza prezzo)
        update_payload["ticket_categories"] = STANDARD_SECTORS.copy()

        # Rimuovi price_range
        unset_payload = {"price_range": ""}

        await db.events.update_one(
            {"_id": ev["_id"]},
            {"$set": update_payload, "$unset": unset_payload}
        )
        updated += 1

    print(f"\nAggiornati eventi: {updated}")

    # 3. Stats finali
    total = await db.events.count_documents({})
    upcoming = await db.events.count_documents({
        "$or": [
            {"sort_date": {"$gte": today_str}},
            {"sort_date": {"$gte": today}},
        ]
    })
    print(f"\nDB Stats finale: total={total}, upcoming={upcoming}")

    # Mostra una giornata di Serie A per verifica
    sample = await db.events.find_one({"league": "SERIE A"})
    if sample:
        print(f"\nSample Serie A event:")
        print(f"  title: {sample.get('title')}")
        print(f"  sort_date: {sample.get('sort_date')}")
        print(f"  ticket_categories[0]: {sample.get('ticket_categories', [{}])[0]}")

    client.close()


if __name__ == "__main__":
    asyncio.run(run())

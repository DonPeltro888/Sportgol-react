"""
Bulk fix logo per tutti i team con logo errato (Arsenal bug TheSportsDB) o mancante.
Usage:
  python -m scripts.bulk_fix_logos                # dry-run, lista team affected
  python -m scripts.bulk_fix_logos execute        # esegue (Gemini Vision + Perplexity + cache)
"""
import asyncio
import os
import sys
sys.path.insert(0, "/app/backend")
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_database")

from database import db
from services import seo_health_fix


# URL noto bug TheSportsDB (ritorna sempre Arsenal)
ARSENAL_BUG_URL = "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png"
CONCURRENCY = 4


async def get_targets():
    targets = []
    async for t in db.teams.find(
        {"$or": [
            {"logo_url": ARSENAL_BUG_URL},
            {"logo_url": {"$exists": False}},
            {"logo_url": ""},
            {"logo_url": None},
        ]},
        {"_id": 0, "slug": 1, "name": 1, "logo_url": 1}
    ):
        if t.get("slug"):
            targets.append(t)
    return targets


async def fix_one_with_sem(sem, slug, name, idx, total):
    async with sem:
        try:
            r = await seo_health_fix.fix_team(slug, mode="balanced")
            applied = r.get("applied")
            actions = r.get("actions") or []
            print(f"[{idx}/{total}] {slug:30s} {name:30s} applied={applied} {'; '.join(actions)[:120]}")
            return r
        except Exception as e:
            print(f"[{idx}/{total}] {slug:30s} ERROR: {str(e)[:200]}")
            return {"slug": slug, "ok": False, "error": str(e)}


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry-run"
    targets = await get_targets()
    print(f"Target teams: {len(targets)}")
    if mode != "execute":
        for t in targets[:30]:
            print(f"  - {t.get('slug'):30s} {t.get('name'):30s} logo={'Arsenal-bug' if t.get('logo_url')==ARSENAL_BUG_URL else 'missing'}")
        if len(targets) > 30:
            print(f"  ... +{len(targets)-30} more")
        print("\nTo execute: python -m scripts.bulk_fix_logos execute")
        return

    print(f"\n=== EXECUTING bulk fix logos ({len(targets)} teams, concurrency={CONCURRENCY}) ===\n")
    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [
        fix_one_with_sem(sem, t["slug"], t.get("name", ""), i + 1, len(targets))
        for i, t in enumerate(targets)
    ]
    results = await asyncio.gather(*tasks)
    fixed = sum(1 for r in results if r.get("applied"))
    errors = sum(1 for r in results if r.get("ok") is False)
    print(f"\n=== DONE: {fixed} fixed, {errors} errors, {len(results) - fixed - errors} no-op ===")


if __name__ == "__main__":
    asyncio.run(main())

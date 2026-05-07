"""
League Validator — verifica composizione lega da fonti autoritative
e marca squadre orfane come archive.

Usage:
  python -m scripts.validate_leagues dry-run [--league=serie-a]
  python -m scripts.validate_leagues execute --confirm [--league=serie-a]

Strategia:
  1. Fetch composizione canonica da OpenFootball (gratis, ufficiale)
     fallback Perplexity (se Perplexity attivo) — ma in P0 solo OpenFootball
  2. Per ogni squadra DB con league_slug==X:
     - se NON è nella lista canonica → flag archive: True, league_slug_archive=X, league_slug=null
     - se È nella lista canonica → ok
  3. Reporting: orfane, missing, in-range
"""
import asyncio
import sys
import os
import re
from typing import Dict, List, Set, Tuple
import httpx

sys.path.insert(0, "/app/backend")
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_database")

from motor.motor_asyncio import AsyncIOMotorClient
from services.team_normalize import normalize_team  # noqa: E402

# Mapping league_slug → OpenFootball file path (current season)
SEASON = "2025-26"
OPENFOOTBALL_LEAGUES = {
    "serie-a": f"{SEASON}/it.1.json",
    "serie-b": f"{SEASON}/it.2.json",
    "premier-league": f"{SEASON}/en.1.json",
    "championship": f"{SEASON}/en.2.json",
    "la-liga": f"{SEASON}/es.1.json",
    "bundesliga": f"{SEASON}/de.1.json",
    "ligue-1": f"{SEASON}/fr.1.json",
    "primeira-liga": f"{SEASON}/pt.1.json",
    "eredivisie": f"{SEASON}/nl.1.json",
    "champions-league": f"{SEASON}/uefa.cl.json",
    "europa-league": f"{SEASON}/uefa.el.json",
    "europa-conference-league": f"{SEASON}/uefa.ecl.json",
    "conference-league": f"{SEASON}/uefa.ecl.json",
}


async def fetch_openfootball_teams(league_slug: str) -> List[str]:
    """Wrapper retrocompatibile — usa il runtime validator (OpenFootball + Perplexity fallback)."""
    from services.league_validator import get_canonical_teams  # noqa
    norm_set = await get_canonical_teams(league_slug)
    # Restituisce direttamente i nomi normalizzati (lo script li ri-normalizza ma è idempotente)
    return list(norm_set)


async def validate_league(db, league_slug: str, dry_run: bool = True) -> Dict:
    canonical_names = await fetch_openfootball_teams(league_slug)
    if not canonical_names:
        return {"error": f"Canonical source: league {league_slug} not available", "league": league_slug}

    canonical_norm: Set[str] = {normalize_team(n) for n in canonical_names}
    canonical_norm.discard("")

    db_teams: List[Dict] = []
    async for d in db.teams.find({"league_slug": league_slug}, {"_id": 1, "name": 1, "slug": 1, "logo_url": 1}):
        db_teams.append(d)

    in_db_norm: Set[str] = {normalize_team(t["name"]) for t in db_teams}
    in_db_norm.discard("")

    orphans = [t for t in db_teams if normalize_team(t["name"]) not in canonical_norm]
    in_canon = [t for t in db_teams if normalize_team(t["name"]) in canonical_norm]
    missing = [c for c in canonical_names if normalize_team(c) not in in_db_norm]

    print(f"\n=== Validation: {league_slug} ({SEASON}) ===")
    print(f"DB teams in this league: {len(db_teams)}")
    print(f"Canonical (OpenFootball): {len(canonical_names)}")
    print(f"  ✓ In canonical: {len(in_canon)}")
    print(f"  ✗ Orphan (to archive): {len(orphans)}")
    for o in orphans:
        print(f"     - {o['name']} (slug={o.get('slug','-')})")
    print(f"  + Missing (in canon but not in DB): {len(missing)}")
    for m in missing:
        print(f"     - {m}")

    if not dry_run and orphans:
        ids = [o["_id"] for o in orphans]
        res = await db.teams.update_many(
            {"_id": {"$in": ids}},
            {"$set": {"league_slug_archive": league_slug, "league_slug": None, "season_archive": "before-2025-26"}},
        )
        print(f"  ✓ Archived {res.modified_count} orphan teams")

    return {
        "league": league_slug,
        "db_count": len(db_teams),
        "canonical_count": len(canonical_names),
        "orphans": [o["name"] for o in orphans],
        "missing": missing,
        "in_canonical": len(in_canon),
    }


async def main():
    mode = "dry-run"
    target_league = "serie-a"
    confirm = "--confirm" in sys.argv
    for a in sys.argv[1:]:
        if a == "execute":
            mode = "execute"
        elif a.startswith("--league="):
            target_league = a.split("=", 1)[1]
    dry_run = not (mode == "execute" and confirm)

    cl = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = cl[os.environ["DB_NAME"]]

    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print(f"League: {target_league}")
    print("=" * 60)

    if target_league == "all":
        for lg in OPENFOOTBALL_LEAGUES:
            await validate_league(db, lg, dry_run)
    else:
        await validate_league(db, target_league, dry_run)

    if dry_run:
        print(f"\nTo execute: python /app/backend/scripts/validate_leagues.py execute --confirm --league={target_league}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Deduplicazione events + teams + leagues con merge intelligente.

Strategia (come da scelte utente):
1a) Aggressivo: matching su (home_norm, away_norm, yyyy-mm-dd) per events,
    name_norm per teams/leagues
2a) Tieni il record più "ricco" (con stadium != TBA, location != TBA)
3a) Copia campi mancanti dal record duplicato prima di cancellarlo
5a) Priorità fonti: apifootball > football_data > matchesio > openfootball > thesportsdb

Utilizzo:
  python -m scripts.dedup_entities dry-run         # mostra cosa farebbe
  python -m scripts.dedup_entities execute        # esegue (richiede --confirm)
"""
import asyncio
import sys
from collections import defaultdict
from typing import Dict, List, Any, Tuple

# Path setup so this works as `python -m scripts.dedup_entities`
sys.path.insert(0, "/app/backend")

from motor.motor_asyncio import AsyncIOMotorClient
import os
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_database")

from services.team_normalize import normalize_team, normalize_league, event_dedup_key  # noqa: E402

SOURCE_PRIORITY = {
    "apifootball": 5,
    "football_data": 4,
    "matchesio": 3,
    "openfootball": 2,
    "thesportsdb": 1,
    None: 0,
    "": 0,
}

EVENT_PLACEHOLDER_VALUES = {"TBA", "tba", "T.B.A.", "Stadio", "TBD", "", None}


def is_placeholder(value) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s in EVENT_PLACEHOLDER_VALUES or s.lower() == "tba"


def event_richness_score(doc: Dict[str, Any]) -> int:
    """Quanti campi pieni (non TBA) ha un evento. Pesa stadium/location di più."""
    score = 0
    if not is_placeholder(doc.get("stadium")):
        score += 5
    if not is_placeholder(doc.get("location")):
        score += 4
    if not is_placeholder(doc.get("city")):
        score += 4
    if doc.get("home_team_logo") or doc.get("home_logo"):
        score += 1
    if doc.get("away_team_logo") or doc.get("away_logo"):
        score += 1
    if doc.get("price_min") or doc.get("minimum_price"):
        score += 2
    if doc.get("description"):
        score += 1
    if doc.get("ticket_url"):
        score += 2
    # SEO già scritto = preserva
    if doc.get("seo_title") or doc.get("seo_intro"):
        score += 100
    # Source priority
    score += SOURCE_PRIORITY.get(doc.get("source"), 0)
    return score


def merge_record(winner: Dict[str, Any], loser: Dict[str, Any]) -> Dict[str, Any]:
    """Aggiunge campi mancanti dal loser al winner. Ritorna patch dict da applicare."""
    patch: Dict[str, Any] = {}
    enrichable_fields = [
        "stadium", "location", "city", "country", "home_team_logo", "away_team_logo",
        "home_logo", "away_logo", "price_min", "minimum_price", "description",
        "ticket_url", "image_url", "league_logo", "competition", "league",
        "home_team_canonical", "away_team_canonical", "match_id_external",
    ]
    for f in enrichable_fields:
        if is_placeholder(winner.get(f)) and not is_placeholder(loser.get(f)):
            patch[f] = loser[f]
    return patch


# ─── Events ─────────────────────────────────────────────────────────────────

async def dedup_events(db, dry_run: bool = True) -> Dict[str, int]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    cursor = db.events.find({}, {})
    total = 0
    async for doc in cursor:
        total += 1
        key = event_dedup_key(doc.get("home_team"), doc.get("away_team"), doc.get("sort_date") or doc.get("date"))
        if not key:
            continue
        groups[key].append(doc)

    duplicates_groups = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"\n=== EVENTS: {total} totali, {len(duplicates_groups)} gruppi con duplicati ===")

    to_delete: List[Any] = []
    patches: List[Tuple[Any, Dict]] = []
    examples_shown = 0

    for key, docs in duplicates_groups.items():
        # Sort: richest first
        docs_sorted = sorted(docs, key=event_richness_score, reverse=True)
        winner = docs_sorted[0]
        losers = docs_sorted[1:]

        # Build merged patch from all losers
        merged_patch: Dict[str, Any] = {}
        for loser in losers:
            mp = merge_record({**winner, **merged_patch}, loser)
            merged_patch.update(mp)

        if examples_shown < 8:
            print(f"\n  [{key}]")
            for d in docs_sorted:
                marker = "  KEEP" if d["_id"] == winner["_id"] else "  DEL "
                print(f"  {marker} {d.get('home_team')} vs {d.get('away_team')} | {d.get('stadium','-')} | {d.get('location','-')} | source={d.get('source','-')} score={event_richness_score(d)}")
            if merged_patch:
                print(f"  PATCH winner with: {merged_patch}")
            examples_shown += 1

        if merged_patch:
            patches.append((winner["_id"], merged_patch))
        for l in losers:
            to_delete.append(l["_id"])

    print(f"\n=== EVENTS: would delete {len(to_delete)} duplicates, patch {len(patches)} winners ===")
    if not dry_run:
        for wid, patch in patches:
            await db.events.update_one({"_id": wid}, {"$set": patch})
        if to_delete:
            res = await db.events.delete_many({"_id": {"$in": to_delete}})
            print(f"  ✓ DELETED {res.deleted_count}, PATCHED {len(patches)}")
    return {"total": total, "duplicates": len(to_delete), "patched": len(patches)}


# ─── Teams ──────────────────────────────────────────────────────────────────

async def dedup_teams(db, dry_run: bool = True) -> Dict[str, int]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    total = 0
    async for doc in db.teams.find({}, {}):
        total += 1
        norm = normalize_team(doc.get("name"))
        if not norm:
            continue
        groups[norm].append(doc)

    dupes = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"\n=== TEAMS: {total} totali, {len(dupes)} gruppi con duplicati ===")

    to_delete: List[Any] = []
    patches: List[Tuple[Any, Dict]] = []
    rename_events: List[Tuple[str, str]] = []  # (old_name, new_name) per fixare events.home_team/away_team

    for norm, docs in dupes.items():
        # Score: with logo (CRITICAL) > with league_slug > prefer canonical name
        def score(d):
            s = 0
            # Logo è dato critico — molto pesante
            if d.get("logo_url"): s += 20
            if d.get("league_slug"): s += 5
            if d.get("seo_title") or d.get("seo_intro"): s += 100
            slug = d.get("slug", "") or ""
            name = (d.get("name") or "").lower().strip()
            norm_name = normalize_team(d.get("name"))
            # Penalizza nomi con numeri (es. "1. Fc Heidenheim", "Stade Brestois 29")
            if any(c.isdigit() for c in slug):
                s -= 5
            if any(c.isdigit() for c in name):
                s -= 3
            # Penalizza nomi con accenti (preferiamo ascii-clean)
            if any(ord(c) > 127 for c in name):
                s -= 1
            # Bonus se il nome è già la versione canonical normalizzata (esatto)
            if name == norm_name:
                s += 4
            # Penalizza prefisso/suffisso superflui
            tokens = name.split()
            useless_prefixes = {"ac", "fc", "sc", "asd", "us", "ss", "as", "ud", "rc", "rcd", "cf", "ca", "fk", "bk", "sk", "sv", "vfl", "vfb", "tsg", "afc", "ogc"}
            if tokens and tokens[0] in useless_prefixes:
                s -= 1.5
            if tokens and tokens[-1] in useless_prefixes:
                s -= 1.5
            s -= len(slug) * 0.05
            return s

        docs_sorted = sorted(docs, key=score, reverse=True)
        winner = docs_sorted[0]
        losers = docs_sorted[1:]

        merged_patch: Dict[str, Any] = {}
        for loser in losers:
            for f in ["logo_url", "league_slug", "stadium", "city", "country", "name_alt"]:
                if not (winner.get(f) or merged_patch.get(f)) and loser.get(f):
                    merged_patch[f] = loser[f]
            # Track names for events fixing
            if loser.get("name") and loser.get("name") != winner.get("name"):
                rename_events.append((loser["name"], winner["name"]))

        print(f"  [{norm}]")
        for d in docs_sorted:
            mark = "KEEP" if d["_id"] == winner["_id"] else "DEL "
            print(f"    {mark} {d.get('name'):30s} slug={d.get('slug','-'):20s} logo={'Y' if d.get('logo_url') else 'N'}")
        if merged_patch:
            patches.append((winner["_id"], merged_patch))
        for l in losers:
            to_delete.append(l["_id"])

    print(f"\n=== TEAMS: would delete {len(to_delete)}, patch {len(patches)}, rename in events: {len(rename_events)} ===")
    if not dry_run:
        for wid, patch in patches:
            await db.teams.update_one({"_id": wid}, {"$set": patch})
        if to_delete:
            res = await db.teams.delete_many({"_id": {"$in": to_delete}})
            print(f"  ✓ DELETED {res.deleted_count}, PATCHED {len(patches)}")
        # Rename events.home_team/away_team
        renamed_h = renamed_a = 0
        for old, new in rename_events:
            r1 = await db.events.update_many({"home_team": old}, {"$set": {"home_team": new}})
            r2 = await db.events.update_many({"away_team": old}, {"$set": {"away_team": new}})
            renamed_h += r1.modified_count
            renamed_a += r2.modified_count
        print(f"  ✓ RENAMED in events: {renamed_h} home_team, {renamed_a} away_team")
    return {"total": total, "duplicates": len(to_delete), "renamed_in_events": len(rename_events)}


# ─── Leagues ────────────────────────────────────────────────────────────────

async def dedup_leagues(db, dry_run: bool = True) -> Dict[str, int]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    total = 0
    async for doc in db.leagues.find({}, {}):
        total += 1
        norm = normalize_league(doc.get("name"))
        if not norm:
            continue
        groups[norm].append(doc)

    dupes = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"\n=== LEAGUES: {total} totali, {len(dupes)} gruppi con duplicati ===")

    to_delete: List[Any] = []
    rename_events: List[Tuple[str, str]] = []

    for norm, docs in dupes.items():
        def score(d):
            s = 0
            if d.get("logo_url"): s += 5
            if d.get("country"): s += 2
            if d.get("seo_title") or d.get("seo_intro"): s += 100
            s -= len(d.get("slug", "")) * 0.1
            return s

        docs_sorted = sorted(docs, key=score, reverse=True)
        winner = docs_sorted[0]
        losers = docs_sorted[1:]

        print(f"  [{norm}]")
        for d in docs_sorted:
            mark = "KEEP" if d["_id"] == winner["_id"] else "DEL "
            print(f"    {mark} {d.get('name'):35s} slug={d.get('slug','-')}")

        for l in losers:
            to_delete.append(l["_id"])
            if l.get("name") and l.get("name") != winner.get("name"):
                rename_events.append((l["name"], winner["name"]))

    print(f"\n=== LEAGUES: would delete {len(to_delete)} ===")
    if not dry_run:
        if to_delete:
            res = await db.leagues.delete_many({"_id": {"$in": to_delete}})
            print(f"  ✓ DELETED {res.deleted_count}")
        renamed = 0
        for old, new in rename_events:
            r = await db.events.update_many({"league": old}, {"$set": {"league": new}})
            renamed += r.modified_count
        print(f"  ✓ RENAMED league field in events: {renamed}")
    return {"total": total, "duplicates": len(to_delete)}


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry-run"
    confirm = "--confirm" in sys.argv
    dry_run = not (mode == "execute" and confirm)

    cl = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = cl[os.environ["DB_NAME"]]

    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'EXECUTE (will modify DB)'}")
    print("=" * 60)

    res_e = await dedup_events(db, dry_run)
    res_t = await dedup_teams(db, dry_run)
    res_l = await dedup_leagues(db, dry_run)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"  events:  {res_e}")
    print(f"  teams:   {res_t}")
    print(f"  leagues: {res_l}")
    if dry_run:
        print("\nTo execute: python /app/backend/scripts/dedup_entities.py execute --confirm")


if __name__ == "__main__":
    asyncio.run(main())
